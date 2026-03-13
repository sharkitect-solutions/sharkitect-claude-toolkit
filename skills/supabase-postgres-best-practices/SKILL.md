---
name: supabase-postgres-best-practices
description: "Use when designing Supabase database schemas, writing Postgres queries in Supabase projects, configuring Row Level Security policies, optimizing query performance, setting up connection pooling, or troubleshooting Supabase database issues. Do NOT use for general backend architecture, frontend Supabase client usage unrelated to database, Supabase Auth configuration, or Supabase Storage/Realtime features."
---

# Supabase Postgres Best Practices

Expert-level Postgres optimization for Supabase projects. 28 rule files provide concrete SQL patterns. This entry point provides the strategic framework, decision models, and anti-patterns that determine WHEN and WHY to apply each rule.

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| SKILL.md | Always | -- |
| rules/query-*.md | Optimizing queries, fixing slow queries, indexing | Schema design, connection issues |
| rules/schema-*.md | Designing tables, migrations, data types | Query optimization, connection pooling |
| rules/conn-*.md | Connection errors, pooling config, timeouts | Schema design, query optimization |
| rules/security-*.md | Row Level Security policies, auth queries | Non-auth queries, schema design |
| rules/lock-*.md | Transaction locking, deadlocks, concurrency | Basic queries, simple CRUD |
| rules/data-*.md | Pagination, batch operations, N+1 queries | Schema design, connection pooling |
| rules/monitor-*.md | EXPLAIN analysis, pg_stat_statements, VACUUM | Basic queries, schema design |
| rules/advanced-*.md | Full-text search, JSONB indexing | Basic queries, simple CRUD |
| references/query-planner-internals.md | EXPLAIN analysis, cost tuning, join algorithms | Basic queries, schema design |
| references/production-scaling.md | High traffic, connection limits, replication | Development setup, basic queries |
| references/supabase-specific-patterns.md | Edge Functions + DB, realtime triggers, auth.uid() | Generic Postgres without Supabase |

## Scope Boundary

IN SCOPE: Supabase Postgres schema design, query optimization, RLS policies, connection pooling (Supavisor), indexing strategies, partitioning, zero-downtime migrations, performance tuning, monitoring, VACUUM management

OUT OF SCOPE: Supabase Auth UI flows (use supabase-auth), Supabase Storage bucket configuration, Supabase Realtime channel subscriptions (use supabase-realtime-optimizer), frontend JavaScript client patterns, general backend architecture (use senior-backend), ORM-specific configuration

---

## Query Planner Decision Framework

Postgres selects scan strategies based on cost estimates derived from table statistics. Understanding these choices prevents cargo-cult indexing.

**Scan Type Selection Logic:**

| Scan Type | Chosen When | Typical Cost Profile |
|-----------|-------------|---------------------|
| Sequential Scan | Selectivity > 5-10% of table, or table < 8KB | Low startup, linear growth with table size |
| Index Scan | Selectivity < 5%, index available, random I/O affordable | Higher startup, but sublinear growth |
| Bitmap Index Scan | Selectivity 1-15%, multiple conditions on different indexes | Medium startup, combines multiple indexes |
| Index Only Scan | All requested columns exist in index (covering index) | Lowest I/O when visibility map is current |

**Cost Model Coefficients (Supabase defaults):**
- `seq_page_cost = 1.0` -- baseline cost of sequential disk page read
- `random_page_cost = 4.0` -- random I/O is 4x more expensive (reduce to 1.1-1.5 on SSD-backed Supabase instances)
- `cpu_tuple_cost = 0.01` -- processing each row
- `cpu_index_tuple_cost = 0.005` -- processing each index entry
- `effective_cache_size` -- tells planner how much data is likely cached (Supabase sets this per plan tier)

**When the Planner Gets It Wrong:**

The planner relies on `pg_statistic` data updated by ANALYZE. Stale statistics cause bad plans. Diagnose with:
```sql
-- Check when statistics were last updated
SELECT schemaname, relname, last_analyze, last_autoanalyze,
       n_live_tup, n_dead_tup
FROM pg_stat_user_tables
WHERE n_live_tup > 10000
ORDER BY last_analyze NULLS FIRST;
```

Force a re-analyze on tables with stale stats before blaming the planner:
```sql
ANALYZE orders;  -- single table
ANALYZE;         -- entire database (expensive, use off-peak)
```

Never use `SET enable_seqscan = off` in production. It is a diagnostic tool only -- use it to confirm an index WOULD help, then fix the root cause (missing index, stale stats, or bad cost settings).

---

## RLS Performance Architecture

RLS adds per-row evaluation overhead. On a 1M-row table, a naive policy calls its expression 1M times per query. Three techniques control this cost.

**Technique 1: Subquery Wrapping for Function Caching**

Wrap `auth.uid()` and other volatile functions in a subquery so Postgres evaluates them once and caches the result:
```sql
-- WRONG: auth.uid() evaluated per row
CREATE POLICY bad ON orders USING (auth.uid() = user_id);

-- RIGHT: evaluated once, result reused
CREATE POLICY good ON orders USING ((SELECT auth.uid()) = user_id);
```

**Technique 2: Permissive vs Restrictive Policy Composition**

Policies on the same table combine with OR (permissive, the default) or AND (restrictive). Misunderstanding this causes data leaks or unnecessary complexity.

- Multiple PERMISSIVE policies: row visible if ANY policy passes (OR)
- RESTRICTIVE policy: row visible only if it passes AND all permissive policies also pass
- Use RESTRICTIVE for mandatory constraints (e.g., `deleted_at IS NULL`), PERMISSIVE for access grants

```sql
-- Permissive: user sees own orders OR orders from their team
CREATE POLICY own_orders ON orders USING ((SELECT auth.uid()) = user_id);
CREATE POLICY team_orders ON orders USING ((SELECT is_team_member(team_id)));

-- Restrictive: BOTH permissive policies AND this must pass
CREATE POLICY not_deleted ON orders AS RESTRICTIVE USING (deleted_at IS NULL);
```

**Technique 3: Testing RLS Without Deploying**
```sql
-- Test as a specific user role locally
SET LOCAL role = 'authenticated';
SET LOCAL request.jwt.claims = '{"sub": "user-uuid-here"}';
SELECT * FROM orders;  -- shows only what this user would see
RESET role;
```

---

## Supavisor Connection Management

Supabase migrated from PgBouncer to Supavisor. The architectural differences matter for application design.

**Transaction Mode vs Session Mode Decision:**

| Use Transaction Mode (port 6543) When | Use Session Mode (port 5432) When |
|----------------------------------------|-----------------------------------|
| Serverless functions (Edge Functions, Vercel) | Need prepared statements with names |
| High concurrency, short-lived queries | Using LISTEN/NOTIFY |
| Standard CRUD operations | Temporary tables across queries |
| Most web application workloads | Long-running analytical queries |

**Prepared Statement Limitation in Transaction Mode:**

Transaction mode releases the connection back to the pool after each transaction. Named prepared statements are bound to a specific connection and will fail on the next request if a different connection is assigned.

Workarounds:
1. Use unnamed prepared statements (most ORMs default to this)
2. Wrap PREPARE + EXECUTE + DEALLOCATE in a single transaction
3. Switch to session mode for workloads that require named prepared statements

**Connection Limit Formula:**
```
Effective connections = (Supabase plan max_connections) - (reserved for superuser: 3) - (reserved for replication: varies)

Free tier:    60 - 3 = 57 effective
Pro tier:    200 - 3 = 197 effective
Team tier:   200 - 3 = 197 effective (but higher compute = more headroom)
Enterprise:  Custom
```

Pool size per application should be: `min(available_connections / number_of_app_instances, CPU_cores * 2 + 1)`

---

## Migration Strategy for Zero Downtime

Supabase migrations run against a live database. Unsafe migrations cause downtime.

**Safe Operations (no lock, no downtime):**
- `CREATE TABLE` -- new tables have no readers
- `ADD COLUMN` with no default and no NOT NULL -- metadata-only change
- `CREATE INDEX CONCURRENTLY` -- builds index without blocking writes
- `DROP INDEX CONCURRENTLY` -- removes index without blocking queries
- `ADD COLUMN ... DEFAULT x` (Postgres 11+) -- metadata-only, no table rewrite

**Unsafe Operations (require careful handling):**
- `ALTER COLUMN TYPE` -- full table rewrite, exclusive lock
- `ADD COLUMN ... NOT NULL` without default -- fails on existing rows
- `CREATE INDEX` (without CONCURRENTLY) -- blocks all writes
- `ALTER TABLE ... ADD CONSTRAINT ... NOT VALID` then `VALIDATE CONSTRAINT` -- split into two migrations

**Zero-Downtime Column Type Change Pattern:**
```sql
-- Step 1: Add new column
ALTER TABLE orders ADD COLUMN amount_v2 numeric(12,2);

-- Step 2: Backfill (in batches to avoid long locks)
UPDATE orders SET amount_v2 = amount::numeric(12,2)
WHERE id BETWEEN 1 AND 10000;
-- ... repeat for all batches

-- Step 3: Swap in application code (deploy reading from amount_v2)
-- Step 4: Drop old column after verification period
ALTER TABLE orders DROP COLUMN amount;
ALTER TABLE orders RENAME COLUMN amount_v2 TO amount;
```

**Supabase CLI Migration Workflow:**
```bash
supabase migration new add_orders_index
# Edit the generated SQL file
supabase db push          # Apply to remote
supabase db reset         # Reset local to match migrations
```

---

## Monitoring and Diagnostics

Supabase exposes standard Postgres monitoring views. These three queries surface 90% of performance issues.

**Top Slow Queries (requires pg_stat_statements extension):**
```sql
SELECT query, calls, mean_exec_time, total_exec_time,
       rows, shared_blks_hit, shared_blks_read
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

**Table Bloat Detection:**
```sql
SELECT schemaname, relname,
       n_live_tup, n_dead_tup,
       ROUND(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 1) AS dead_pct,
       last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY dead_pct DESC;
```

Tables with dead_pct > 20% need attention. Supabase runs autovacuum, but heavy write workloads can outpace it. Adjust per-table: `ALTER TABLE orders SET (autovacuum_vacuum_scale_factor = 0.05)`.

**Index Usage Efficiency:**
```sql
SELECT relname, indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;
```
Indexes with zero scans are dead weight -- they slow writes and consume storage. Drop them.

---

## Named Anti-Patterns

### "The RLS Bypass"
Using `service_role` key in client-side code, which bypasses all Row Level Security. The service_role key is a server-only secret. Exposing it in a browser or mobile app gives every user full database access. Use the `anon` key for client-side and enforce RLS. Service_role belongs in server-side Edge Functions or backend APIs only.

### "The N+1 Policy"
Creating a separate RLS policy for each table that performs the same permission check (e.g., each policy queries `team_members` independently). Instead, create a single `security definer` helper function that caches the check, and reference it from all policies. This reduces redundant subqueries from N to 1.

### "The Connection Hog"
Opening persistent database connections from serverless functions (Edge Functions, Vercel serverless, AWS Lambda). Each cold start creates a new connection that never closes. At scale, this exhausts `max_connections` within minutes. Always use Supavisor transaction mode (port 6543) from serverless environments, and set aggressive idle timeouts.

### "The Naked Migration"
Running `ALTER TABLE` or `CREATE INDEX` (without CONCURRENTLY) on production tables during business hours. These acquire exclusive locks that block all reads and writes until complete. On a 10M-row table, a non-concurrent index build can lock the table for minutes. Always use `CREATE INDEX CONCURRENTLY` and schedule schema-altering migrations during low-traffic windows.

### "The Function Trap"
Creating `security definer` functions without `SET search_path = ''`. Security definer functions execute with the privileges of the function owner (typically the superuser). Without an explicit search_path, an attacker can manipulate the search path to call malicious functions. Always set `search_path = ''` and fully qualify all table references inside security definer functions.

### "The Index Carpet"
Adding an index on every column "just in case." Each index costs write performance (every INSERT/UPDATE/DELETE must update all indexes) and storage. A table with 15 indexes will have 3-5x slower writes than one with 3 targeted indexes. Use `pg_stat_user_indexes` to identify which indexes are actually scanned, and drop the rest.

---

## Rationalization Table

| Shortcut Temptation | Why It Fails | What to Do Instead |
|---------------------|-------------|-------------------|
| "Skip RLS, we validate in the app layer" | Application bugs, API bypass, direct DB access all leak data. RLS is the last line of defense. | Enable RLS on every table with user data. Use service_role only server-side. |
| "Just add more indexes to make it faster" | Each index slows writes and consumes RAM. Unused indexes degrade overall performance. | Run EXPLAIN ANALYZE first. Add indexes only for proven slow query patterns. Audit with pg_stat_user_indexes. |
| "Use session mode pooling for everything" | Session mode holds connections open, exhausting the pool under concurrent load. Serverless functions never release. | Default to transaction mode. Use session mode only when prepared statements or LISTEN/NOTIFY require it. |
| "Run ALTER TABLE directly, it's a small change" | Even metadata-only changes acquire locks. Non-concurrent index builds block the entire table. Column type changes rewrite every row. | Use zero-downtime migration patterns. CREATE INDEX CONCURRENTLY. Batch backfills for type changes. |
| "Disable autovacuum, it's using too many resources" | Dead tuples accumulate, causing table bloat, slower sequential scans, and eventually transaction ID wraparound (database shutdown). | Tune autovacuum per-table instead of disabling it. Lower scale_factor for high-write tables. |

---

## Red Flags

Stop and reassess the approach if ANY of these conditions exist:

1. **RLS disabled on user-facing tables** -- every table exposed through the Supabase API MUST have RLS enabled. No exceptions for "internal" tables that might be accessed through views or functions.
2. **service_role key present in client-side code** -- check environment variables, bundled JS, mobile app configs. This is a critical security vulnerability.
3. **Sequential scans on tables with > 50,000 rows** -- run EXPLAIN ANALYZE. If the planner chooses Seq Scan on a large table with a WHERE clause, an index is missing or statistics are stale.
4. **Connection count approaching plan limits** -- query `SELECT count(*) FROM pg_stat_activity`. If this exceeds 80% of plan max_connections, connection pooling is misconfigured or leaking.
5. **Dead tuple ratio > 20% on any table** -- autovacuum is falling behind. Tune autovacuum_vacuum_scale_factor or investigate write patterns.
6. **Migrations without CONCURRENTLY on production** -- any CREATE INDEX or DROP INDEX without CONCURRENTLY will lock tables. Review all migration files before applying.
7. **RLS policies using bare function calls without subquery wrapping** -- `auth.uid() = user_id` instead of `(SELECT auth.uid()) = user_id` causes per-row function evaluation. Performance degrades linearly with table size.
