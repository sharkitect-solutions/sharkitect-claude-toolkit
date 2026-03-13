---
name: database
description: "Use when designing database schemas, optimizing queries, choosing between database engines, planning data models, implementing migrations, or troubleshooting database performance issues. Do NOT use for Supabase-specific patterns (use supabase-postgres-best-practices), application-level caching strategy, or ORM-specific configuration unrelated to database design."
---

# Database Design and Management

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| references/engine-comparison.md | Choosing or comparing database engines | Already decided on engine |
| references/indexing-deep-dive.md | Designing indexes, diagnosing slow queries, index maintenance | Simple single-column lookups |
| references/migration-patterns.md | Planning schema changes on live systems, zero-downtime deploys | Greenfield with no existing data |

## Scope Boundary

IN SCOPE: Schema design, normalization decisions, index strategy, query optimization, engine selection, migration planning, connection management, partition strategy, performance diagnostics, data modeling, backup planning, N+1 detection

OUT OF SCOPE: Supabase-specific RLS/Edge Functions (use supabase-postgres-best-practices), ORM configuration unrelated to database design, application-level caching architecture, frontend state management, infrastructure provisioning (Terraform/Pulumi), database-as-a-service platform operations

---

## Database Engine Selection Framework

Choose the engine based on workload characteristics, not popularity. See `references/engine-comparison.md` for the full decision matrix.

**Quick Decision Thresholds:**

| Criteria | SQLite | Postgres | MySQL | MongoDB | Redis | DynamoDB |
|----------|--------|----------|-------|---------|-------|----------|
| Concurrent writers | <100 | Thousands | Thousands | Thousands | Single-threaded* | Unlimited |
| Data size ceiling | <1TB | Petabytes | Petabytes | Petabytes | RAM-bound | Unlimited |
| Query complexity | Simple | Complex joins, CTEs, window functions | Moderate joins | Document lookups, aggregation pipeline | Key lookups, sorted sets | Single-table, key-condition |
| Consistency model | Serializable (WAL mode: concurrent reads) | Full ACID, MVCC | ACID per-engine (InnoDB) | Tunable (single-doc atomic) | Single-threaded atomic | Eventually consistent default, strong optional |
| Operational overhead | Zero (embedded) | Moderate | Moderate | Moderate-High | Low | Zero (managed) |

*Redis uses single-threaded command processing but handles thousands of concurrent connections via I/O multiplexing.

**Selection Rules:**
- Embedded/edge/mobile with no server: SQLite. Period.
- Relational data with complex queries, need correctness guarantees: Postgres.
- Read-heavy web apps with simple schemas, MySQL ecosystem tools needed: MySQL.
- Rapidly evolving schema, document-oriented data, no cross-document joins: MongoDB.
- Sub-millisecond key-value lookups, ephemeral data, pub/sub, rate limiting: Redis.
- Predictable latency at any scale, willing to model everything as single-table: DynamoDB.

When two engines seem equal, default to Postgres. Its extension ecosystem (PostGIS, pg_trgm, timescaledb, pgvector) covers more future requirements than any other engine.

---

## Schema Design Principles

### Normalization Decision Framework

Start at Third Normal Form (3NF). Denormalize only with measured evidence.

**Stay normalized when:** write-heavy workloads, data integrity is non-negotiable (financial/medical/legal), schema is still evolving, query patterns are diverse.

**Denormalize when:** a query joins 4+ tables at >50ms under load, the field is read 100x more than written, you have measured write amplification cost, and you will maintain the copy (triggers, CDC, or application logic).

Crossover: if a JOIN query executes fewer than 100 times/minute, denormalization rarely justifies the consistency maintenance cost.

### Composite Key Design

Order composite primary keys by selectivity (most selective column first) unless the access pattern demands otherwise. For time-series data, lead with the partition dimension (tenant_id, device_id) to enable efficient range scans within a partition.

### Enum Handling

| Approach | When to Use |
|----------|-------------|
| CHECK constraint | Fewer than 10 values, rarely change, no metadata needed |
| Lookup table (FK) | Values change over time, need display labels, i18n, sort order, or soft-disable |
| Application enum | Values are purely presentational and never queried by the database |

Never store enums as integers without a mapping table. "The Magic Number Trap" -- six months later nobody knows what status=7 means.

### JSON/JSONB Columns

**Use JSONB when:** schema varies per row (user preferences, plugin config, form submissions), you query specific keys with GIN indexes (`@>` containment), or data is consumed as a blob by the application.

**Do NOT use JSONB when:** you JOIN on nested fields regularly, the "flexible" schema is actually stable (avoiding a migration, not solving a real problem), or you need referential integrity on nested values.

### Temporal Data Patterns

**SCD Type 2:** Add `valid_from`, `valid_to` columns. Query `WHERE valid_to IS NULL` for current state. Best for dimension tables where history matters (pricing, customer segments).

**Event Sourcing:** Append-only event log, derive state via projection. Best for audit-critical domains (financial, compliance) needing point-in-time reconstruction. Higher read complexity -- adopt only when audit requirements justify it.

**Temporal Tables (SQL:2011):** Postgres and MariaDB support system-versioned temporal tables natively. Use when available and you need automatic history without application logic.

---

## Indexing Strategy

See `references/indexing-deep-dive.md` for the complete decision tree, recipes, and maintenance procedures.

**Index Type Selection (Postgres-centric, principles apply broadly):**

| Index Type | Use When | Storage Overhead |
|------------|----------|-----------------|
| B-tree (default) | Equality, range, sorting, LIKE 'prefix%' | Moderate (20-30% of table) |
| Hash | Equality-only lookups, no range/sort needed | Smaller than B-tree |
| GIN | Full-text search, JSONB containment, array operations | 2-3x column size |
| GiST | Geometric/spatial, range types, nearest-neighbor | Moderate |
| BRIN | Large naturally-ordered tables (timestamps, auto-increment) | Tiny (1-5% of B-tree) |

**Composite Index Column Ordering Rule:**
Place columns in this order: Equality conditions first, then Range conditions, then Sort columns. This is the "ERS" rule. A composite index on (status, created_at, name) serves `WHERE status = 'active' AND created_at > '2024-01-01' ORDER BY name` optimally.

**Partial Indexes Save Space:**
```sql
CREATE INDEX idx_orders_pending ON orders(created_at)
  WHERE status = 'pending';
```
If only 5% of orders are pending, this index is 95% smaller than a full index. Use partial indexes on boolean flags, status columns, and soft-delete markers.

**Covering Indexes Eliminate Table Lookups:**
```sql
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (first_name, last_name);
```
Postgres returns results directly from the index (Index Only Scan) without visiting the heap. Measure with EXPLAIN ANALYZE -- look for "Index Only Scan" in the plan.

**Index Maintenance Overhead:**
Every index adds write amplification. Each INSERT updates every index on the table. Rule of thumb: more than 8 indexes on a write-heavy table is a smell. Profile before adding index number 6+.

---

## Query Optimization

### EXPLAIN ANALYZE Interpretation

Always run `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` in a transaction you roll back.

**Key signals:**
- **Seq Scan on large table:** Not always bad. If returning >5-10% of rows, Seq Scan is faster than Index Scan (avoids random I/O). Add index only when selectivity <5%.
- **Nested Loop with inner Seq Scan:** N+1 at database level. Fix with Hash Join (add index) or restructure query.
- **High `actual loops`:** Repeated subplan execution. Materialize subquery or convert to JOIN.
- **Buffers shared read >> shared hit:** Data from disk, not cache. Increase `shared_buffers` or reduce working set.

### N+1 Detection and Elimination

One query to fetch a list, then N queries for related data. Costs O(N) round trips.

**Detection:** If the same parameterized query executes >10 times within one request, you have N+1.

**Elimination:** Eager JOIN, batch loading (IN clause with collected IDs), LATERAL subquery, or DataLoader pattern (batch + cache at application layer).

### Pagination Strategies

| Method | Best For | Breaks When |
|--------|----------|-------------|
| OFFSET/LIMIT | Small datasets, random page access | >1000 offset (scans and discards rows) |
| Cursor (keyset) | Large datasets, sequential navigation | Need to jump to arbitrary page |
| Seek method | Time-series, sorted feeds | Multi-column sort with NULLs |

**Crossover:** Switch from OFFSET to cursor at ~10,000 rows or when users never jump to page 500. OFFSET degrades linearly -- page 1000 scans and discards 999 pages.

---

## Migration Architecture

See `references/migration-patterns.md` for the zero-downtime cookbook and rollback checklist.

### Zero-Downtime Migration Principles

**The Expand-Contract Pattern:**
1. **Expand:** Add the new column/table/index alongside the old one. Application writes to both.
2. **Migrate:** Backfill existing data from old to new.
3. **Contract:** Remove the old column/table/index after all readers have switched.

Never combine expand and contract in a single deployment. The gap between them should be at least one full deployment cycle.

**Dangerous Operations (require expand-contract):**
- Renaming a column (old code still references old name)
- Changing a column type (implicit cast may fail or lose precision)
- Adding NOT NULL constraint to existing column (must backfill first)
- Dropping a column (old code may still SELECT it)

**Safe Operations (single-step):**
- Adding a nullable column with no default
- Adding an index with `CREATE INDEX CONCURRENTLY` (Postgres)
- Adding a new table
- Adding a CHECK constraint as NOT VALID then validating separately

### Data Backfill for Large Tables

Never run `UPDATE large_table SET new_col = computed_value` on a table with 1M+ rows in a single transaction. It locks the table and bloats WAL.

**Batched backfill pattern:**
```sql
UPDATE target_table SET new_col = source_value
WHERE id IN (
  SELECT id FROM target_table
  WHERE new_col IS NULL
  LIMIT 5000
)
```
Run in a loop with 100ms sleep between batches. Monitor replication lag if running against a primary with replicas.

---

## Connection Management

### Pool Sizing Formula

The PostgreSQL wiki formula, validated by benchmarks: `connections = (core_count * 2) + effective_spindle_count`. For SSD-backed systems, effective spindle count is 1. A 4-core server: (4 * 2) + 1 = 9 connections.

Most applications over-provision connections. A pool of 20-30 connections handles thousands of concurrent application threads via queuing. PgBouncer or application-level pooling prevents the "500 connections from 50 application instances" problem.

### Transaction Isolation Levels

| Level | Use Case | Anomalies Prevented |
|-------|----------|-------------------|
| READ COMMITTED (default) | General OLTP, most web apps | Dirty reads |
| REPEATABLE READ | Reports that must see consistent snapshot | Dirty reads, non-repeatable reads |
| SERIALIZABLE | Financial transactions, inventory, double-booking prevention | All anomalies (may abort on conflict) |

Default to READ COMMITTED. Use SERIALIZABLE only for operations where a race condition means monetary loss or data corruption. Serializable transactions may abort and must be retried -- your application code must handle `SQLSTATE 40001`.

### Connection Lifecycle Best Practices

- Acquire connections as late as possible, release as early as possible
- Never hold a connection during external HTTP calls or user input waits
- Set `idle_in_transaction_session_timeout` to kill forgotten transactions (e.g., 30 seconds)
- Set `statement_timeout` to prevent runaway queries (e.g., 30 seconds for web requests, higher for batch jobs)

---

## Named Anti-Patterns

### "The God Table"
One table with 50+ columns covering unrelated domains. Symptoms: most columns NULL, schema changes touch unrelated features, row size exceeds 8KB triggering TOAST. Fix: decompose into focused tables joined by FK.

### "The Stringly Typed"
Structured data stored as delimited strings: `tags = "red,blue,green"`. Cannot query efficiently, no integrity, parsing bugs. Fix: proper columns, array types, or junction tables.

### "The Index Carpet"
Indexing every column. Each index adds write overhead (page splits, WAL, vacuum). 15 indexes = 15x write amplification on inserts. Fix: index only WHERE/JOIN/ORDER BY columns from actual queries. Monitor `pg_stat_user_indexes` for unused indexes.

### "The Soft Delete Swamp"
`is_deleted BOOLEAN DEFAULT FALSE` on every table. Every query needs `WHERE is_deleted = FALSE` (developers forget). Cascading soft-deletes are never consistent. Fix: hard deletes + audit log table, or SCD Type 2 if recovery needed.

### "The UUID Everywhere"
UUID v4 PKs when auto-increment suffices. 16 bytes vs 4-8, random B-tree page splits destroy locality, 2-4x index bloat. Fix: BIGSERIAL for internal PKs, UUID as external-facing identifier in separate column. If UUID PKs required, use UUIDv7 (time-sorted) for locality.

### "The Premature Optimization"
Materialized views, denormalized columns, and caching before measuring actual performance. A "slow" 50ms query gets a cache, creating consistency problems for nothing. Fix: EXPLAIN ANALYZE first, optimize the measured bottleneck.

---

## Rationalization Table

| Temptation | Why It Feels Right | What Actually Happens | Do This Instead |
|------------|-------------------|----------------------|-----------------|
| "Let's use MongoDB because our schema might change" | Schema flexibility sounds productive | You move complexity from schema management to application-level validation; data inconsistencies emerge within months | Start with Postgres + JSONB columns for the genuinely flexible parts; keep the stable parts in typed columns |
| "We need UUIDs for security -- auto-increment IDs are guessable" | Sequential IDs reveal record count and creation order | UUID v4 PKs fragment indexes, increase storage 2-4x, slow range queries. Sequential IDs in URLs are a presentation concern, not a database concern | Use BIGSERIAL PKs internally; add a UUID column for external APIs; never expose internal PKs in URLs |
| "Add an index on every foreign key" | ORMs and guides recommend it | Foreign keys used only for INSERT/DELETE constraint checks (never in WHERE clauses) get indexes that consume space and slow writes for zero read benefit | Index FKs only if you query or JOIN on that column. Check `pg_stat_user_indexes` for scans = 0 |
| "Denormalize now to avoid slow JOINs later" | JOINs have a bad reputation from the ORM era | You add write amplification and consistency bugs for a JOIN that takes 2ms. Denormalization is a measured response, not a preventive measure | Benchmark the normalized query first. Denormalize only when you have measured evidence of unacceptable latency under production load |

---

## Red Flags

- **Query returning >1000 rows to the application for filtering in code** -- the database should filter, not the app. Push predicates down.
- **No indexes on columns used in WHERE clauses of queries running >100 times per minute** -- measure with pg_stat_statements or equivalent, then add targeted indexes.
- **Connection count approaching max_connections** -- you need connection pooling (PgBouncer), not a higher max_connections setting. Each connection costs ~10MB of RAM.
- **Tables with >50 columns** -- likely a God Table. Decompose before it becomes load-bearing.
- **Migrations that combine DDL and large DML in one transaction** -- the DDL acquires locks, the DML holds them for the duration. Split into separate deployments.
- **No backup testing** -- backups that have never been restored are not backups. Test restore quarterly at minimum.
- **OFFSET pagination beyond page 100** -- performance is degrading linearly. Switch to cursor-based pagination.
