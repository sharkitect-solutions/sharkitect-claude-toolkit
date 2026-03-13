# Migration Patterns

## Zero-Downtime Migration Cookbook

### Add a Nullable Column

**Risk:** LOW -- single step, no expand-contract.

```sql
ALTER TABLE users ADD COLUMN middle_name TEXT;
```

Brief ACCESS EXCLUSIVE lock (milliseconds in Postgres 11+ -- no table rewrite for NULL defaults). In Postgres <11, adding a column with a non-null DEFAULT rewrites the entire table.

### Add a Column with NOT NULL Constraint

**Risk:** HIGH -- requires expand-contract.

**Expand:** Add nullable. **Backfill:** Batch UPDATE (see below). **Constrain:**
```sql
ALTER TABLE orders ADD CONSTRAINT orders_region_nn CHECK (region IS NOT NULL) NOT VALID;
ALTER TABLE orders VALIDATE CONSTRAINT orders_region_nn;
-- VALIDATE only needs SHARE UPDATE EXCLUSIVE lock (reads not blocked)
```
**Contract:** `ALTER TABLE orders ALTER COLUMN region SET NOT NULL;` (Postgres recognizes the CHECK and skips full scan), then drop the CHECK.

### Rename a Column

**Risk:** HIGH -- old code references old name. Requires 3-4 deployments over 1-2 weeks.

1. **Expand:** Add new column, deploy dual-write code
2. **Backfill:** Copy old to new in batches
3. **Switch readers:** Deploy code reading from new column
4. **Switch writers:** Deploy code writing only to new column
5. **Contract:** `ALTER TABLE users DROP COLUMN old_name;`

### Change a Column Type

**Risk:** VERY HIGH -- implicit cast may fail or lose precision.

Never: `ALTER TABLE t ALTER COLUMN c TYPE new_type;` (rewrites table, holds ACCESS EXCLUSIVE lock).

Instead: add new column with target type, dual-write, backfill with explicit cast (handle conversion errors per-row), switch readers, switch writers, drop old column.

### Drop a Column

**Risk:** MEDIUM -- running code may still reference it.

1. Deploy code that no longer references the column (fix `SELECT *` to explicit column lists first)
2. Wait one full deployment cycle
3. `ALTER TABLE t DROP COLUMN legacy_field;`

### Add an Index

**Risk:** LOW with CONCURRENTLY.

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer ON orders(customer_id);
```

Monitor: `SELECT * FROM pg_stat_progress_create_index;` (Postgres 12+). If CONCURRENTLY fails midway, it leaves an INVALID index -- drop it and retry.

## Data Backfill for Large Tables (10M+ Rows)

### Batched UPDATE

```sql
UPDATE target_table SET new_col = computed_value
WHERE id IN (
  SELECT id FROM target_table
  WHERE new_col IS NULL
  ORDER BY id LIMIT 5000
  FOR UPDATE SKIP LOCKED
);
-- Run in loop with 100ms sleep between batches
```

- `SKIP LOCKED` prevents deadlocks with concurrent transactions
- `ORDER BY id` enables predictable progress monitoring
- 5,000 row batches keep WAL and lock overhead manageable
- If replication lag exceeds 5 seconds, increase the inter-batch pause

### Progress Tracking (100M+ rows)

```sql
CREATE TABLE backfill_progress (
  table_name TEXT PRIMARY KEY,
  last_processed_id BIGINT,
  rows_processed BIGINT DEFAULT 0,
  started_at TIMESTAMPTZ DEFAULT NOW()
);
```

Resume from `last_processed_id` on crash/restart. Enables ETA calculation.

### Shadow Table Strategy

For transformations too complex for in-place UPDATE: create new table with target schema, backfill in batches via INSERT INTO...SELECT, set up trigger on old table to dual-write, swap tables via rename in a transaction, drop old table. This is what `pg_repack` and `gh-ost` automate.

## Migration Safety Checklist

### Pre-Migration

- [ ] Tested on production-size data copy (not dev fixtures)
- [ ] Lock duration estimated (`SET lock_timeout = '5s'` to fail fast)
- [ ] Rollback script written and tested
- [ ] Replication lag monitoring active
- [ ] Backfill ETA calculated (row_count / batch_size * interval)

### Rollback Rules

- **Expand phase:** DROP the new column/table/index. No data loss.
- **Backfill phase:** Stop script, drop new column. Old data untouched.
- **Contract phase:** Old structure is gone. Requires backup restore or reverse migration.
- **Cardinal rule:** Never combine expand and contract in one deployment.

### Lock Timeout Pattern

```sql
SET lock_timeout = '5s';
ALTER TABLE large_table ADD COLUMN new_col TEXT;
```

If lock cannot be acquired in 5 seconds, the statement fails instead of blocking all queries. Retry during low-traffic windows. Investigate blockers:

```sql
SELECT pid, now() - xact_start AS duration, query
FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;
```
