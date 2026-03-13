# AutoGPT Platform Architecture Gotchas

## Infrastructure Dependencies

AutoGPT Platform requires 5 services minimum. Each has failure modes that aren't in the documentation.

| Service | Role | Common Failure | Detection | Fix |
|---|---|---|---|---|
| **PostgreSQL** | Graph storage, execution history, user data | Connection pool exhaustion under concurrent executions | `FATAL: too many connections for role` in executor logs | Prisma default is 5 connections per executor. With 3 executors = 15 connections. Set `connection_limit` in Prisma schema. Use PgBouncer for >5 executors |
| **Redis** | Execution state cache, pub/sub for real-time updates | Memory growth from orphaned execution states | Redis `INFO memory` shows growing `used_memory`. `DBSIZE` keeps increasing | Set `maxmemory-policy volatile-lru`. Execution keys should have TTL but many don't by default. Manual cleanup: scan and delete `exec:*` keys older than 7 days |
| **RabbitMQ** | Graph execution queue, node execution dispatch | Queue depth grows when executors are slower than submissions | RabbitMQ management UI (port 15672) shows queue depth increasing. Consumer count dropping | Scale executors: `docker compose up -d --scale executor=N`. If queues are backlogged >1000 messages, check executor health first |
| **Supabase** | Authentication, user management | Auth token expiry causes silent failures. Users appear logged in but API calls fail | 401 errors in network tab despite valid session. Executor logs show auth failures | Supabase JWT expires every 3600s by default. Frontend must refresh tokens proactively. Set `SUPABASE_JWT_EXPIRY` to 7200 for buffer |
| **Frontend (Next.js)** | Visual builder, agent management | Build failures after AutoGPT updates (dependency changes) | `Module not found` or `Cannot resolve` errors during build | Clear `.next/` and `node_modules/`, rebuild. AutoGPT updates frequently change Next.js config |

---

## Prisma and Database Gotchas

AutoGPT Platform uses Prisma ORM. These issues are specific to AutoGPT's schema and usage patterns.

| Gotcha | What Happens | Impact | Solution |
|---|---|---|---|
| **Migration ordering** | AutoGPT adds migrations in each release. If you have custom migrations, they interleave and conflict | `prisma migrate deploy` fails with "migration not found" or "already applied" | Never add custom migrations to AutoGPT's migration directory. Use a separate schema/database for custom tables |
| **Execution table bloat** | `AgentGraphExecution` and `AgentNodeExecution` tables grow unbounded. Every execution creates rows in both | Query performance degrades after ~100K executions. Dashboard becomes slow | Add retention policy: delete executions older than 30 days. Create index on `(userId, createdAt DESC)` if not present |
| **Connection storms** | When executor restarts, all Prisma connections re-initialize simultaneously | Postgres sees spike in connection attempts. Can hit `max_connections` limit | Set `pool_timeout` in Prisma connection string. Use PgBouncer in transaction mode as connection multiplexer |
| **JSON column queries** | Block configurations stored as JSONB. Querying specific config values is slow | Filtering agents by specific block configurations requires full table scan | Extract frequently-queried config values into indexed columns. Or use Postgres GIN indexes on JSONB |

---

## Executor Scaling Patterns

The executor is the bottleneck component. Scaling it wrong causes more problems than it solves.

| Scaling Approach | When to Use | Gotcha |
|---|---|---|
| **Vertical (bigger machine)** | <100 executions/day, simple graphs | Single point of failure. Executor crash = all queued work stops |
| **Horizontal (more executors)** | >100 executions/day or SLA requirements | Each executor opens its own DB connection pool. 10 executors x 5 connections = 50 DB connections. Plan accordingly |
| **Kubernetes HPA** | Dynamic load, usage spikes | HPA scaling on CPU misses the real bottleneck (queue depth). Scale on RabbitMQ queue length instead: `rabbitmq_queue_messages` metric |
| **Dedicated executors per graph** | High-priority agents that can't be queued behind others | Requires separate RabbitMQ queues per priority level. Not built-in. Custom routing needed |

### Executor Resource Sizing

| Workload | CPU Request | Memory Request | Memory Limit | Notes |
|---|---|---|---|---|
| Light (simple graphs, <50 exec/day) | 500m | 512Mi | 2Gi | Default Docker compose settings work |
| Medium (complex graphs, 50-500 exec/day) | 1000m | 1Gi | 4Gi | Monitor for OOMKilled. LLM response parsing can spike memory |
| Heavy (many concurrent, >500 exec/day) | 2000m | 2Gi | 8Gi | Consider dedicated executor pools for different graph types |

---

## Block Execution Edge Cases

| Edge Case | What Happens | How to Handle |
|---|---|---|
| **Block timeout** | Default timeout varies by block type. LLM blocks have longer timeouts than standard blocks | Set explicit `timeout_seconds` in block config. Default of 60s is too short for complex LLM calls with tool use |
| **Partial yield** | Block yields some outputs then throws exception | Previous yields are preserved in node execution record. Downstream nodes may or may not fire depending on which outputs were yielded |
| **Credential rotation** | API key is rotated in provider. Blocks using cached credentials fail | Credentials are loaded per-execution, not cached across executions. BUT if an execution is long-running, credentials loaded at start may expire mid-execution |
| **Concurrent block writes** | Two blocks in parallel try to update the same external resource | AutoGPT doesn't provide distributed locking. Blocks executing in parallel CAN race. Use idempotent operations or external locking |
| **Graph validation gaps** | Graph validator checks structure but NOT semantic validity. Invalid block configs pass validation | A graph can be "valid" but fail at runtime because block inputs don't match expected types. Test each block independently before composing graphs |

---

## Authentication and Multi-Tenancy

| Aspect | How It Works | Gotcha |
|---|---|---|
| **User isolation** | Graphs, credentials, and executions are scoped to user ID via Supabase auth | Executor runs with service-level access. A bug in block code could theoretically access another user's data. Review custom blocks for user-scoping |
| **Credential encryption** | Block credentials encrypted with `ENCRYPTION_KEY` env var | If `ENCRYPTION_KEY` changes, ALL stored credentials become unreadable. Back up the key. Rotate by re-encrypting, not by changing the key |
| **API authentication** | Bearer token from Supabase JWT | No API key-based auth for external integrations. Webhooks require separate authentication mechanism (X-Webhook-Signature) |
| **Rate limiting** | No built-in rate limiting on API or execution endpoints | A single user can flood the execution queue. Implement rate limiting at reverse proxy level (nginx, Cloudflare) |

---

## Monitoring and Observability

AutoGPT Platform has minimal built-in monitoring. You need to add it.

| What to Monitor | Why | How |
|---|---|---|
| **RabbitMQ queue depth** | Primary indicator of executor health. Growing queue = executors falling behind | RabbitMQ management API: `GET /api/queues`. Alert when depth >100 |
| **Execution duration by graph** | Identifies slow graphs and regression | Log execution start/end times. Calculate p50, p95, p99 per graph_id |
| **Block failure rate** | Which blocks fail most often. Guides block improvement priority | Query `AgentNodeExecution` for `executionStatus = 'FAILED'` grouped by block type |
| **Database connection count** | Prevents connection exhaustion | PostgreSQL: `SELECT count(*) FROM pg_stat_activity`. Alert when >80% of max_connections |
| **Redis memory usage** | Prevents OOM and data loss | Redis `INFO memory`. Alert when used_memory > 80% of maxmemory |
| **LLM API error rate** | External dependency health | Track 429 (rate limit), 500 (provider issue), timeout responses per block |

### Health Check Endpoint

AutoGPT Platform doesn't expose a proper health check. Build one:

```
GET /api/v1/health should check:
1. Database connection (SELECT 1)
2. Redis connection (PING)
3. RabbitMQ connection (queue declare)
4. Supabase auth (token validation)

Return 200 only if ALL pass. Any failure = 503.
```

Without this, load balancers and Kubernetes will route traffic to unhealthy instances.

---

## Common Production Issues

| Issue | Symptom | Root Cause | Fix |
|---|---|---|---|
| **Executions silently fail** | Graph shows "completed" but output is empty | Block yielded no outputs (empty result from LLM, API returned nothing). Platform doesn't distinguish "completed with output" from "completed with nothing" | Add explicit error handling in blocks. Check for empty responses and yield error output instead of nothing |
| **Dashboard slow after weeks** | Agent list and execution history pages take >5 seconds | No pagination on execution queries. Every execution ever is being loaded | Add LIMIT/OFFSET to execution queries. Implement retention policy |
| **WebSocket disconnects** | Real-time execution updates stop. UI shows stale state | WebSocket server has default connection limit. Supabase realtime has its own limits | Implement WebSocket reconnection on frontend. Monitor active connections. Scale WebSocket server |
| **Graph save loses changes** | Edit graph, save, reload, changes are gone | Concurrent save from another tab or auto-save conflict. No conflict resolution | Last-write-wins is the default. Add optimistic locking (version field) if multiple editors |
