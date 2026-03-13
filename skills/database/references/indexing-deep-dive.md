# Indexing Deep Dive

## Index Type Selection Decision Tree

```
What operation does your query perform?

Equality only (WHERE col = value)?
  -> Hash index (Postgres 10+, but B-tree works too and supports range)

Equality + Range (WHERE col = X AND date > Y)?
  -> B-tree (composite: equality columns first, range columns second)

Full-text search (WHERE doc @@ to_tsquery('term'))?
  -> GIN on tsvector column

JSONB containment (WHERE data @> '{"key": "value"}')?
  -> GIN on JSONB column

Array operations (WHERE tags @> ARRAY['red'])?
  -> GIN on array column

Geometric/spatial (ST_DWithin, ST_Contains)?
  -> GiST (or SP-GiST for non-overlapping geometries)

Range type queries (WHERE range_col && '[2024-01-01, 2024-06-01)')?
  -> GiST on range column

Large table, naturally ordered (created_at on append-only log)?
  -> BRIN (tiny index, 1-5% of B-tree size, good for sequential correlation)

Nearest-neighbor search (ORDER BY col <-> point)?
  -> GiST with distance operator
```

## Composite Index Design Patterns

### The ERS Rule (Equality, Range, Sort)

For a query: `WHERE status = 'active' AND created_at > '2024-01-01' ORDER BY priority DESC`

Optimal index: `(status, created_at, priority)` -- equality first, range second, sort third.

**Why this order matters at the B-tree level:** B-tree nodes are sorted. Equality conditions narrow to exact leaf nodes. Range conditions scan a contiguous subset of those leaves. Sort columns within that subset are already in order, avoiding a separate Sort operation.

Reversing to `(created_at, status, priority)` forces scanning all created_at > '2024-01-01' entries across ALL statuses, then filtering -- far more pages read.

### Multi-Column Index Selectivity

When two equality columns are present, put the more selective column first ONLY IF both columns are always queried together. If sometimes you query on status alone, lead with status so the index serves that single-column query too.

**Rule:** A composite index on (A, B, C) serves queries on (A), (A, B), and (A, B, C) -- but NOT (B), (C), or (B, C). The leading column must always be present.

## Partial Index Recipes

### Soft-Delete Filter
```sql
CREATE INDEX idx_orders_active ON orders(customer_id, created_at)
  WHERE deleted_at IS NULL;
```
If 90% of rows have `deleted_at IS NULL`, this index is ~90% smaller than a full index and only includes rows your queries actually care about.

### Status Column Filter
```sql
CREATE INDEX idx_jobs_pending ON jobs(priority, created_at)
  WHERE status = 'pending';
```
Worker queues only query pending jobs. This index covers the hot path and ignores the 99% of historical completed/failed jobs.

### Boolean Flag Filter
```sql
CREATE INDEX idx_users_unverified ON users(email)
  WHERE email_verified = FALSE;
```
The verification reminder job queries only unverified users (typically <5% of the table). Full index waste: 95%.

### NULL Exclusion
```sql
CREATE INDEX idx_invoices_due ON invoices(due_date)
  WHERE due_date IS NOT NULL;
```
Skip rows with NULL due_date. B-tree indexes include NULLs by default -- excluding them reduces size when NULLs are common.

## Covering Index Patterns

A covering index includes all columns the query needs, eliminating the heap lookup entirely (Postgres reports this as "Index Only Scan").

```sql
-- Query: SELECT email, first_name FROM users WHERE email = 'x@y.com'
CREATE INDEX idx_users_email_covering ON users(email) INCLUDE (first_name);
```

**INCLUDE vs adding to the index key:** INCLUDE columns are stored in leaf pages but are NOT part of the B-tree sort order. They do not affect index traversal, only add data to leaf pages. Use INCLUDE for columns in SELECT but not in WHERE/ORDER BY.

**When covering indexes pay off:**
- High-frequency queries (>1000/minute) that currently do Index Scan + heap lookup
- The heap table is wide (many columns) but the query only needs 2-3
- The table has high dead-tuple churn (heap pages are bloated, avoiding them saves I/O)

**When they do not pay off:**
- The query already returns quickly (<1ms)
- The INCLUDE columns are large (TEXT, JSONB) and inflate the index significantly
- The table is small enough to fit in shared_buffers entirely

## Index Bloat Detection and Maintenance

### Detecting Bloat

```sql
-- Check estimated bloat (pgstattuple extension)
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
       idx_scan AS times_used
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

Indexes with `idx_scan = 0` over a 30-day period are candidates for removal. Confirm with application query logs before dropping.

### Bloat from UPDATE-heavy Workloads

Postgres MVCC creates dead index entries on every UPDATE (the old row version's index entry persists until vacuum). Tables with frequent updates on indexed columns accumulate index bloat. Symptoms: index is 2-5x larger than expected for the row count.

**Fix:** `REINDEX CONCURRENTLY idx_name` (Postgres 12+). This rebuilds the index without locking the table. Schedule during low-traffic periods despite being non-blocking -- it still consumes CPU and I/O.

### CREATE INDEX CONCURRENTLY

Standard `CREATE INDEX` acquires a SHARE lock on the table, blocking all writes until the index build completes. On a 100M row table, this can take minutes.

`CREATE INDEX CONCURRENTLY` builds the index in the background. It takes longer (two table scans instead of one) but does not block writes. Trade-off: if it fails midway, it leaves an invalid index that must be dropped manually.

**Always use CONCURRENTLY in production.** The only exception: new tables with no concurrent traffic.

## Index Size Estimation

**Rule of thumb for B-tree:** Index size (bytes) ~ row_count * (key_size + 8 bytes TID + 4 bytes per-tuple overhead). For a BIGINT (8 byte) key on 10M rows: 10M * 20 bytes ~ 200MB plus internal page overhead ~ 250MB.

**GIN indexes:** Typically 2-3x the size of the indexed column data. A 500MB JSONB column generates a ~1-1.5GB GIN index.

**BRIN indexes:** Fixed overhead per block range (default 128 pages). For a 10GB table: typically 1-5MB. Use when the column has high physical correlation with row storage order (e.g., auto-increment ID, insertion timestamp).
