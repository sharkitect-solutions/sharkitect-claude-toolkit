# Production Scaling

Reference for operating Supabase Postgres at scale. Covers connection math, read replicas, partitioning decisions, VACUUM tuning, and monitoring queries. Load this file when dealing with high traffic, connection exhaustion, or performance degradation under load.

---

## Connection Pooling Math

**Supavisor Pool Sizing Formula:**

```
Available connections = plan_max_connections - superuser_reserved(3) - replication_slots
Pool per app instance = min(available / num_instances, cpu_cores * 2 + 1)
```

| Supabase Plan | max_connections | Available After Reserved | Suggested Pool Size (4 instances) |
|---------------|----------------|------------------------|----------------------------------|
| Free | 60 | 57 | 14 per instance |
| Pro (small) | 200 | 197 | 49 per instance |
| Pro (medium) | 200 | 197 | 49 per instance |
| Team | 200 | 197 | 49 per instance |
| Enterprise | Custom (500-1000+) | Custom | Custom |

**Serverless Connection Pattern:**

Serverless functions (Edge Functions, Vercel, Netlify) create unpredictable connection spikes. Each cold start opens a new connection. Without pooling, 200 concurrent invocations = 200 connections = exhausted pool.

Mandatory configuration for serverless:
```
Connection string: postgresql://user:pass@db.project.supabase.co:6543/postgres
                                                                  ^^^^
                                                            Port 6543 = Supavisor
```

Set in the serverless function's database client:
```javascript
// Node.js example (Edge Function)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,  // must use port 6543
  max: 1,           // each function instance gets ONE connection
  idleTimeoutMillis: 10000,  // release quickly
  connectionTimeoutMillis: 5000,
});
```

**Diagnosing Connection Leaks:**
```sql
-- Current connections by state
SELECT state, count(*), max(now() - state_change) AS max_duration
FROM pg_stat_activity WHERE datname = current_database()
GROUP BY state ORDER BY count DESC;

-- Kill connections idle > 5 minutes (likely leaked)
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'idle' AND now() - state_change > interval '5 minutes';
```

---

## Read Replicas

Supabase Pro plans support read replicas. Add one when: read:write ratio > 10:1, analytics compete with OLTP, geographic latency matters, or primary CPU > 70% at peak.

**Replication Lag Monitoring:**
```sql
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;
-- Acceptable: < 1 second. If > 5 seconds: check WAL generation rate and replica I/O.
```

Route reads to replica, writes to primary. Reads requiring consistency (e.g., account balance after transfer) must go to primary.

---

## Table Partitioning Decision Criteria

| Factor | Partition | Don't Partition |
|--------|-----------|----------------|
| Row count | > 10M rows | < 1M rows |
| Query pattern | Always filters on partition key (date, tenant) | Random access across all data |
| Data lifecycle | Need to DROP old data quickly | Keep all data indefinitely |
| Write volume | > 10K inserts/minute concentrated in recent partition | Distributed writes across all data |
| Maintenance | VACUUM on 100M-row table takes hours | VACUUM completes in seconds |

**Partition Key Selection:**
- Time-series data: partition by `created_at` (range partitioning, monthly or weekly)
- Multi-tenant SaaS: partition by `tenant_id` (list partitioning if < 100 tenants, hash if more)
- Avoid: partitioning by high-cardinality columns (user_id with millions of users)

**Partition Maintenance Automation:**
```sql
-- Create a function to auto-create monthly partitions
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name text, start_date date)
RETURNS void AS $$
DECLARE
  partition_name text;
  end_date date;
BEGIN
  partition_name := table_name || '_' || to_char(start_date, 'YYYY_MM');
  end_date := start_date + interval '1 month';

  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
    partition_name, table_name, start_date, end_date
  );
END;
$$ LANGUAGE plpgsql;

-- Create partitions 3 months ahead
SELECT create_monthly_partition('events', date_trunc('month', now() + interval '1 month'));
SELECT create_monthly_partition('events', date_trunc('month', now() + interval '2 months'));
SELECT create_monthly_partition('events', date_trunc('month', now() + interval '3 months'));
```

---

## VACUUM and ANALYZE Tuning

Supabase manages autovacuum, but default settings suit moderate workloads. High-write tables need per-table tuning.

**Default Autovacuum Thresholds:**
```
autovacuum_vacuum_threshold = 50        -- minimum dead tuples to trigger
autovacuum_vacuum_scale_factor = 0.2    -- trigger at 20% dead tuples
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1   -- trigger at 10% changed tuples
```

**Per-Table Tuning for High-Write Tables:**
```sql
-- Events table: 50M rows, 100K inserts/hour
-- Default: vacuum triggers at 10M dead tuples (20% of 50M) -- too late
ALTER TABLE events SET (
  autovacuum_vacuum_scale_factor = 0.02,     -- trigger at 2% (1M dead tuples)
  autovacuum_vacuum_cost_delay = 2,          -- reduce sleep between vacuum pages
  autovacuum_vacuum_cost_limit = 1000        -- process more pages per cycle
);

-- Orders table: moderate writes, need fresh statistics for planner
ALTER TABLE orders SET (
  autovacuum_analyze_scale_factor = 0.01     -- re-analyze after 1% changes
);
```

**Transaction ID Wraparound Prevention:**

Postgres uses 32-bit transaction IDs. After ~2 billion transactions, it must perform an aggressive VACUUM (freezing) to prevent wraparound. This can cause a database-wide freeze.

Monitor proximity to wraparound:
```sql
SELECT relname,
       age(relfrozenxid) AS xid_age,
       pg_size_pretty(pg_total_relation_size(oid)) AS total_size
FROM pg_class
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC
LIMIT 10;

-- WARNING threshold: age > 500,000,000
-- CRITICAL threshold: age > 1,000,000,000
-- Postgres forces autovacuum at age > autovacuum_freeze_max_age (default 200M)
```

---

## Production Monitoring Queries

Run these on a 5-minute schedule or expose via Edge Function:

```sql
-- Connection utilization (alert > 80%)
SELECT count(*) AS conns, current_setting('max_connections')::int AS max,
       round(count(*)::numeric / current_setting('max_connections')::int * 100, 1) AS pct
FROM pg_stat_activity;

-- Long-running queries (alert > 30s)
SELECT pid, now() - query_start AS duration, left(query, 100)
FROM pg_stat_activity WHERE state != 'idle' AND now() - query_start > interval '30 seconds';

-- Cache hit ratio (target > 99% for OLTP)
SELECT sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0) AS ratio
FROM pg_statio_user_tables;
```
