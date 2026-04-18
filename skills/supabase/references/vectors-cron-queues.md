# Supabase Vectors, Cron, and Queues

Expert-only knowledge for Supabase's three Postgres-extension-based products: `pgvector` (semantic search), `pg_cron` (scheduled SQL), `pgmq` (message queue). This file covers the index choices, tuning parameters, and integration patterns that determine whether these are production-ready or expensive footguns.

---

## pgvector: Index Choice and Tuning

### Enable the extension

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
  id bigserial PRIMARY KEY,
  content text,
  embedding vector(1536)  -- dimension MUST match your embedding model
);
```

### HNSW vs IVFFlat: The Index Decision

| Index | Build time | Query speed | Recall (accuracy) | Update cost | Use when |
|-------|-----------|-------------|-------------------|-------------|----------|
| **HNSW** | Slow (10x slower than IVFFlat) | Fast (logarithmic) | High by default | Higher | Production, frequent reads, infrequent writes |
| **IVFFlat** | Fast | Faster than seq scan, slower than HNSW | Lower, must tune `lists` | Lower | Large append-mostly tables, batch updates |
| **No index (sequential scan)** | None | O(N), unusable above ~10K rows | Perfect (exact) | None | Tables under 10K rows, prototyping |

**Default recommendation: HNSW.** Build time is the only downside, and it's a one-time cost.

### HNSW creation and tuning

```sql
-- Default parameters work for most cases
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);

-- Tuned for higher recall (slower build, more memory)
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```

| Parameter | Default | Effect of increasing |
|-----------|---------|---------------------|
| `m` | 16 | More connections per node = better recall, more memory, slower writes |
| `ef_construction` | 64 | Better recall during build, much slower build |
| `ef_search` (query-time) | 40 | Higher = better recall, slower queries — set per query: `SET hnsw.ef_search = 100;` |

**Distance operator MUST match index ops:**
| Distance | Operator | Index ops | When to use |
|----------|----------|-----------|-------------|
| Cosine | `<=>` | `vector_cosine_ops` | OpenAI embeddings (most common) |
| L2 / Euclidean | `<->` | `vector_l2_ops` | When magnitude matters |
| Inner product | `<#>` | `vector_ip_ops` | When embeddings are normalized AND you want speed |

If you create the index with `vector_cosine_ops` but query with `<->`, the index is NOT used — you get a sequential scan with no error.

### IVFFlat: only if you have specific reasons

```sql
-- Critical: lists ≈ rows / 1000 (rows up to 1M), or sqrt(rows) above that
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);  -- for ~100K rows
```

**The `lists` trap:** if you create IVFFlat on an empty table or with wrong `lists`, recall is terrible. IVFFlat must be built AFTER bulk-loading your data. Rebuilding requires `REINDEX`.

**Set `probes` per query for recall vs speed:**
```sql
SET ivfflat.probes = 10;  -- default 1, max = lists. Higher = better recall, slower.
```

### Query patterns

```sql
-- Top 5 nearest neighbors by cosine distance
SELECT id, content, 1 - (embedding <=> $query_embedding) AS similarity
FROM documents
ORDER BY embedding <=> $query_embedding
LIMIT 5;
```

**Note:** `<=>` returns DISTANCE (0 = identical, 2 = opposite). Convert to similarity score with `1 - distance` for cosine.

### The HNSW filtering pitfall

```sql
-- WRONG — pre-filter forces index OFF, sequential scan
SELECT * FROM documents
WHERE org_id = 123 AND embedding <=> $q < 0.3
ORDER BY embedding <=> $q LIMIT 10;
```

The combination of WHERE filter + ORDER BY + LIMIT often defeats the HNSW index. Postgres has to fetch many candidates, filter, then sort.

**Better pattern: partition by org_id** (separate HNSW index per partition):
```sql
CREATE TABLE documents (
  id bigserial,
  org_id int,
  embedding vector(1536),
  PRIMARY KEY (id, org_id)
) PARTITION BY LIST (org_id);

-- Then create HNSW index per partition
```

**Or use `iterativescan` (pgvector 0.8+):**
```sql
SET hnsw.iterative_scan = relaxed_order;  -- or strict_order
-- Postgres explores HNSW until it has enough rows matching the filter
```

### Embedding generation: always normalize when using inner product

OpenAI text-embedding-3-* embeddings are pre-normalized (norm = 1). If you use any other model, NORMALIZE before inserting:

```sql
-- Normalize on insert
INSERT INTO documents (embedding) VALUES (l2_normalize($vec));
```

Without normalization, inner product (`<#>`) gives wrong results. Cosine (`<=>`) self-corrects but adds compute.

---

## pg_cron: Scheduled SQL

### Enable + first job

```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Run a query daily at 03:00 UTC
SELECT cron.schedule(
  'cleanup-stale-sessions',  -- job name (unique)
  '0 3 * * *',
  $$ DELETE FROM auth.sessions WHERE not_after < now() $$
);
```

### Critical timezone caveat

**pg_cron runs in UTC. Always.** A schedule of `0 9 * * *` fires at 09:00 UTC, which is varying local times:
- 04:00 EST (winter) / 05:00 EDT (summer)
- 18:00 JST
- 10:00 CET (winter) / 11:00 CEST (summer)

For "daily at 9am company time," pick a fixed UTC offset that approximates your business hours, OR have the cron call a function that computes the correct local time and conditionally executes.

### Updating an existing job

`cron.schedule(name, ...)` is **upsert-by-name only for the schedule** — it does NOT update the command. To change a job's SQL:

```sql
SELECT cron.unschedule('job-name');
SELECT cron.schedule('job-name', '0 3 * * *', $$ NEW SQL HERE $$);
```

### Calling Edge Functions from cron

```sql
CREATE EXTENSION IF NOT EXISTS pg_net;  -- for net.http_post

SELECT cron.schedule(
  'daily-report',
  '0 3 * * *',
  $$
    SELECT net.http_post(
      url := 'https://<project>.supabase.co/functions/v1/daily-report',
      headers := jsonb_build_object(
        'Authorization', 'Bearer ' || vault.read_secret('service_role'),
        'Content-Type', 'application/json'
      ),
      body := '{}'::jsonb
    );
  $$
);
```

**Why `vault.read_secret` and not hardcoded:** never inline service_role keys in cron job SQL — they end up in `cron.job` table queries and can leak via DB logs. Store in Vault, read at runtime.

### Inspecting jobs

```sql
SELECT * FROM cron.job;                    -- all scheduled jobs
SELECT * FROM cron.job_run_details         -- run history
  WHERE jobname = 'daily-report'
  ORDER BY start_time DESC LIMIT 20;
```

`job_run_details` keeps history but grows unbounded. Schedule a self-cleaning job:
```sql
SELECT cron.schedule('purge-cron-history', '0 4 * * *',
  $$ DELETE FROM cron.job_run_details WHERE end_time < now() - interval '30 days' $$
);
```

### Common failure modes

- Job appears in `cron.job` but never runs → pg_cron not enabled in `postgresql.conf` `shared_preload_libraries` (Supabase Cloud handles this; self-hosted requires manual config)
- `permission denied` on inserted records → cron jobs run as the role that called `cron.schedule` (usually `postgres`); to run as a different role: `SET ROLE` inside the job SQL
- Multiple instances of the same job firing → the job's SQL takes longer than the schedule interval. Use `pg_try_advisory_lock` inside the job to prevent overlap.

```sql
-- Prevent overlapping runs
SELECT cron.schedule('long-job', '*/5 * * * *', $$
  SELECT CASE WHEN pg_try_advisory_lock(12345)
    THEN do_work()
    ELSE NULL
  END;
  PERFORM pg_advisory_unlock(12345);
$$);
```

---

## pgmq: Message Queue in Postgres

### When to use pgmq vs alternatives

| Need | Use |
|------|-----|
| Simple background jobs, low volume (<1K/sec) | **pgmq** — no extra infra, transactional with your data |
| Cross-region pub/sub, fan-out | NOT pgmq → use Realtime Broadcast or external (NATS, Kafka) |
| Long-running workflows with retries | pgmq + Edge Function workers |
| Real-time client notifications | NOT pgmq → use Realtime |

### Enable + create queue

```sql
CREATE EXTENSION IF NOT EXISTS pgmq;

SELECT pgmq.create('email_outbox');  -- queue name
```

### Producer (transactional with your data)

```sql
BEGIN;
  INSERT INTO orders (customer_id, total) VALUES (123, 99.99);
  SELECT pgmq.send('email_outbox', '{"type":"order_confirmation","order_id":456}'::jsonb);
COMMIT;
```

**Critical advantage:** the queue write is in the SAME TRANSACTION as the order insert. If the order rolls back, the message is never sent. Compare to external queues (SQS, Redis) where you can commit the order then crash before queueing → silent message loss.

### Consumer pattern (worker)

```sql
-- Read up to 5 messages, hide them for 30s (visibility timeout)
SELECT * FROM pgmq.read('email_outbox', vt => 30, qty => 5);
-- returns msg_id, read_ct, enqueued_at, message
```

After processing each message:
```sql
SELECT pgmq.delete('email_outbox', $msg_id);  -- success
-- OR
SELECT pgmq.archive('email_outbox', $msg_id);  -- keep for inspection in <queue>_archive table
```

If you don't `delete` or `archive` within `vt` seconds, the message becomes visible again → automatic retry.

### Edge Function worker pattern

```ts
// edge-function: process-email-queue (called by cron every minute)
Deno.serve(async () => {
  const { data: messages } = await supabase.rpc('pgmq_read', {
    queue_name: 'email_outbox', vt: 60, qty: 10
  })

  for (const msg of messages ?? []) {
    try {
      await sendEmail(msg.message)
      await supabase.rpc('pgmq_delete', { queue_name: 'email_outbox', msg_id: msg.msg_id })
    } catch (err) {
      // Don't delete — message becomes visible again after vt expires for retry
      if (msg.read_ct >= 5) {
        // Move to dead-letter after 5 retries
        await supabase.rpc('pgmq_archive', { queue_name: 'email_outbox', msg_id: msg.msg_id })
      }
    }
  }

  return new Response('ok')
})
```

### Schedule the worker

```sql
SELECT cron.schedule('process-email-queue', '* * * * *',
  $$ SELECT net.http_post(url := 'https://<project>.supabase.co/functions/v1/process-email-queue', ...) $$);
```

### Pgmq monitoring

```sql
-- Queue depth (number of messages waiting)
SELECT * FROM pgmq.metrics('email_outbox');
-- returns: queue_length, newest_msg_age_sec, oldest_msg_age_sec, total_messages, scrape_time

-- Watch for queue depth growing (worker can't keep up)
-- Alert when oldest_msg_age_sec > 5 minutes
```

### Archive table maintenance

`pgmq.archive()` moves to `<queue_name>_archive` table — grows forever. Schedule cleanup:
```sql
SELECT cron.schedule('purge-email-archive', '0 5 * * *',
  $$ DELETE FROM pgmq.q_email_outbox_archive WHERE archived_at < now() - interval '30 days' $$);
```

### Common pgmq gotchas

- **Visibility timeout too short** → worker still processing when message becomes visible again, processed twice. Set `vt` to 2-3x your worst-case processing time.
- **Forgetting to archive failed messages** → poison messages retry forever, blocking the queue. Implement read_ct check.
- **Long transactions holding queue locks** → pgmq.read uses `SELECT FOR UPDATE SKIP LOCKED`. A long-running transaction holding many locks can starve other workers.
- **Mixing transactional and non-transactional consumers** → if one worker uses BEGIN/pgmq.read/process/COMMIT and another uses autocommit pgmq.read + external work, retry semantics get inconsistent.

---

## Other Useful Extensions Quick Reference

| Extension | Purpose | Notable gotcha |
|-----------|---------|---------------|
| `pg_graphql` | Auto-generate GraphQL API from schema | Auto-exposes everything in `public` — review carefully |
| `pg_net` | HTTP requests from SQL | Async — returns request_id, response in `net._http_response` table |
| `vault` | Encrypted secret storage | Read-only after creation; rotate by creating new + deleting old |
| `pg_jsonschema` | JSON Schema validation in CHECK constraints | Slower than native CHECK, use sparingly |
| `pgsodium` | DEPRECATED — use Vault | Migration path documented in Supabase docs |
| `pg_stat_statements` | Query performance stats | Always enable for production tuning |

Enable via Dashboard → Database → Extensions, or `CREATE EXTENSION` directly.

---

## When This Skill Has Failed in the Past

- HNSW index with mismatched ops/operator → silent sequential scan, slow queries
- IVFFlat created on empty table → terrible recall, requires REINDEX
- Filter + HNSW + ORDER BY → index defeated, slow. Fix: partition or `iterative_scan`
- Cron job time interpreted as local → daily report runs at 4am EST instead of 9am
- Inlined service_role in cron SQL → key visible in cron.job table, leaks via logs
- pgmq message processed twice → vt too short relative to processing time
- pgmq archive table never purged → table grows unbounded, eventually fills disk
- pgmq `read_ct` not checked → poison messages retry forever
- Embedding model dimension mismatch → vector(1536) but using a 768-dim model → all queries fail with dimension error
