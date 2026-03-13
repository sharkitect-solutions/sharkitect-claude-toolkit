# Query Planner Internals

Deep reference for interpreting EXPLAIN output, understanding cost calculations, and diagnosing why Postgres chose a specific execution plan. Load this file when analyzing EXPLAIN ANALYZE output or tuning planner behavior.

---

## Join Algorithm Selection

Postgres chooses between three join algorithms based on row estimates, available indexes, and work_mem.

| Algorithm | Chosen When | Memory Usage | Best For |
|-----------|-------------|-------------|----------|
| Nested Loop | Inner side < ~1000 rows OR inner has index | Minimal (O(1)) | Small inner tables, index lookups |
| Hash Join | No useful index, inner fits in work_mem | O(inner rows) | Medium-large equi-joins |
| Merge Join | Both sides pre-sorted or have matching indexes | O(1) streaming | Large pre-sorted datasets |

**Row Count Thresholds (approximate, varies with work_mem):**
- Inner < 100 rows: Nested Loop almost always wins
- Inner 100-10,000 rows with index: Nested Loop with Index Scan
- Inner 100-10,000 rows without index: Hash Join
- Inner > 10,000 rows, both sides sorted: Merge Join
- Inner > 10,000 rows, unsorted: Hash Join (if fits in work_mem)

**When Hash Join Spills to Disk:**
```
Hash Join (actual time=2500.00..4800.00)
  -> Hash (actual time=1200.00..1200.00)
       Buckets: 65536  Batches: 8  Memory Usage: 32833kB
```
`Batches: 8` means the hash table spilled to disk in 8 batches. Fix by increasing `work_mem` for the session:
```sql
SET work_mem = '256MB';  -- session-level, not global
```

---

## EXPLAIN ANALYZE Output Interpretation

**Critical Fields to Read:**

```
Index Scan using orders_customer_idx on orders
  (cost=0.42..8.44 rows=1 width=85)
  (actual time=0.025..0.028 rows=1 loops=1)
  Buffers: shared hit=4
```

| Field | Meaning | Action When Suspicious |
|-------|---------|----------------------|
| cost=startup..total | Planner's estimated cost (arbitrary units) | Compare startup vs total -- large gap means expensive initialization |
| rows=N (estimated) | Planner's row count guess from pg_statistic | If actual rows >> estimated rows, run ANALYZE |
| actual time=start..end | Real wall-clock time in milliseconds | The definitive performance metric |
| rows=N (actual) | Real row count returned | Compare to estimated -- mismatch signals stale stats |
| loops=N | How many times this node executed | Total cost = per-loop cost * loops |
| Buffers: shared hit=N | Pages found in shared_buffers cache | High hit ratio = good caching |
| Buffers: shared read=N | Pages read from disk | High read count = cold cache or working set exceeds RAM |

**Estimate Accuracy Check:**
When estimated rows differ from actual rows by more than 10x, the planner is making decisions based on wrong statistics.

```sql
-- Bad: planner estimated 1 row, got 50,000
Index Scan (cost=0.42..8.44 rows=1) (actual rows=50000 loops=1)

-- Fix: update statistics
ANALYZE table_name;

-- If ANALYZE doesn't help, check for correlated columns:
CREATE STATISTICS orders_customer_status ON customer_id, status FROM orders;
ANALYZE orders;
```

---

## Statistics and pg_stats

Postgres stores column-level statistics that drive all planner decisions.

**Key Columns in pg_stats:**
```sql
SELECT attname, n_distinct, most_common_vals, most_common_freqs,
       correlation, null_frac
FROM pg_stats
WHERE tablename = 'orders' AND attname = 'status';
```

| Stat | What It Tells You |
|------|------------------|
| n_distinct | Number of unique values (-1 = all unique, -0.5 = 50% unique) |
| most_common_vals | Most frequent values and their frequencies |
| correlation | Physical row order vs logical order (1.0 = perfectly correlated, enables Index Only Scan) |
| null_frac | Fraction of NULL values (affects IS NULL / IS NOT NULL estimates) |

**default_statistics_target:**
Default is 100 (samples 30,000 rows). For columns with skewed distributions, increase it:
```sql
ALTER TABLE orders ALTER COLUMN status SET STATISTICS 500;
ANALYZE orders;
```
Higher values give the planner better estimates but make ANALYZE slower.

---

## Cost Tuning for Supabase Infrastructure

Supabase runs on SSD-backed cloud infrastructure. The default `random_page_cost = 4.0` assumes spinning disks and overestimates random I/O cost, causing the planner to prefer sequential scans when index scans would be faster.

**Recommended Adjustments:**
```sql
-- For Supabase (SSD storage):
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();

-- NOTE: On Supabase managed plans, you may not have ALTER SYSTEM access.
-- Instead, adjust per-session or per-transaction:
SET random_page_cost = 1.1;
```

**effective_cache_size Impact:**
This tells the planner how much of the dataset is likely in OS page cache + shared_buffers. Setting it too low makes the planner avoid index scans (it assumes random reads will hit disk). Supabase sets this per plan tier:
- Free tier: ~1GB
- Pro tier: ~4-8GB
- Team tier: ~8-16GB

If you see the planner choosing Seq Scan when the table fits in memory, effective_cache_size may be too low.

---

## Subquery vs JOIN Planner Behavior

The planner handles subqueries differently depending on their structure:

**Correlated Subqueries** -- re-executed per outer row (expensive):
```sql
-- Planner CANNOT flatten this -- runs once per outer row
SELECT * FROM orders o
WHERE total > (SELECT AVG(total) FROM orders WHERE customer_id = o.customer_id);
```

**Uncorrelated Subqueries** -- executed once, result cached:
```sql
-- Planner executes inner query once, caches scalar result
SELECT * FROM orders WHERE total > (SELECT AVG(total) FROM orders);
```

**Semi-Joins (EXISTS)** -- planner can short-circuit:
```sql
-- EXISTS stops scanning after first match (efficient)
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- IN with subquery may or may not be converted to semi-join
SELECT * FROM customers WHERE id IN (SELECT customer_id FROM orders);
-- Planner usually converts to semi-join, but verify with EXPLAIN
```

**CTE Optimization Fence (Postgres 11 and earlier):**
Before Postgres 12, CTEs were always materialized (optimization fence). Supabase runs Postgres 15+, so CTEs are inlined by default unless they are referenced multiple times or explicitly materialized.
```sql
-- Postgres 15+ (Supabase): planner inlines this CTE
WITH recent_orders AS (
  SELECT * FROM orders WHERE created_at > now() - interval '30 days'
)
SELECT * FROM recent_orders WHERE status = 'pending';

-- Force materialization if you need stability:
WITH recent_orders AS MATERIALIZED (...)
```
