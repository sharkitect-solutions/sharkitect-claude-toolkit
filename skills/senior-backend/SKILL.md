---
name: senior-backend
description: "When designing backend system architecture, choosing between API styles, or making database scaling decisions. When reviewing backend code for production readiness, performance bottlenecks, or architectural anti-patterns. Also when planning authentication architecture or error handling strategy across service boundaries. For code quality patterns use clean-code instead. For database-specific queries use database instead. For security reviews use security-best-practices instead. For containerization use docker-expert instead. For NestJS-specific work use nestjs-expert instead. For debugging errors use error-resolver instead."
---

# Senior Backend

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| SKILL.md | Architecture decision matrix, API style selection, database gotchas, scalability patterns, auth architecture, performance debugging, error handling | Always (auto-loaded) |
| production-incident-patterns.md | Cascade failure anatomy (4 stages), retry amplification math, thundering herd scenarios (5), split-brain detection/recovery, incident severity classification, postmortem anti-patterns (5), on-call best practices | When debugging production issues, designing incident response, building runbooks, or analyzing system failures |
| api-versioning-and-evolution.md | Versioning strategy decision matrix (5), breaking vs non-breaking change classification (8 types), deprecation lifecycle (4 phases with RFC 8594 headers), consumer-driven contract testing (Pact workflow), API lifecycle anti-patterns (5) | When designing API versioning, managing breaking changes, planning deprecation, or setting up contract testing |
| observability-and-monitoring.md | Three pillars (what each actually solves), structured logging rules (5 with cost economics), OpenTelemetry distributed tracing (sampling by environment), SLO/SLI/SLA framework with error budget policy, alerting strategy (multi-window burn rate), four golden signals | When designing logging, implementing tracing, defining SLOs, or building monitoring dashboards |

## Scope Boundary

| If the user wants... | Use instead |
|----------------------|-------------|
| Code readability, naming, SOLID principles | clean-code |
| SQL query writing, schema design, specific DB engine tuning | database |
| OWASP vulnerabilities, dependency scanning, threat modeling | security-best-practices |
| Dockerfile optimization, compose orchestration, image layering | docker-expert |
| NestJS modules, providers, guards, interceptors | nestjs-expert |
| Stack traces, runtime errors, debugging sessions | error-resolver |
| System-wide architecture across multiple services | senior-architect |
| Backend system architecture, API style selection, scaling strategy | THIS skill |

## Architecture Decision Matrix

First-match signal table. Stop at the first row where all signals match.

| Team size | Deploy frequency | Data coupling | Regulatory | Architecture |
|-----------|-----------------|---------------|------------|-------------|
| 1-5 devs | any | any | any | Modular monolith |
| 5-15 devs | daily+ | loose between domains | none special | Modular monolith with extract-ready boundaries |
| 5-15 devs | daily+ | loose between domains | PCI/HIPAA isolation needed | Microservices for regulated domain only |
| 15-40 devs | multiple daily | domain-aligned teams own data | any | Microservices along team boundaries |
| 40+ devs | continuous | each team owns its data store | any | Microservices with platform team |
| any | any | tight cross-domain joins | any | Monolith (microservices will become distributed monolith) |

**When microservices HURT (non-obvious):**
- Shared database between services = distributed monolith with network latency added. Worse than monolith in every dimension
- Under 5 engineers = operational overhead (service mesh, distributed tracing, log correlation) exceeds any organizational benefit
- Synchronous call chains deeper than 3 services = latency multiplication + cascade failure risk. Refactor to async or merge services
- "We need microservices for scalability" -- horizontal scaling of a monolith (multiple instances behind load balancer) handles 95% of scale needs. Microservices solve ORGANIZATIONAL scaling, not computational scaling
- Data consistency requirements across services mean distributed transactions (Saga pattern), which are 10x harder to debug than database transactions

## API Style Decision Matrix

First-match. Choose the first row that fits.

| Signal | Choose | NOT this (common mistake) |
|--------|--------|--------------------------|
| Browser clients + server clients + mobile, public API | REST with OpenAPI spec | GraphQL (client diversity makes schema evolution painful) |
| Single frontend team, rapidly changing UI data needs | GraphQL | REST (avoids over/under-fetching churn) |
| Internal service-to-service, high throughput, schema-strict | gRPC with protobuf | REST (serialization overhead matters at scale) |
| TypeScript monorepo, frontend + backend same team | tRPC | REST (type-safe without code generation) |
| Public API with paying customers | REST | tRPC (couples to TypeScript ecosystem) |
| Multi-language microservices needing contracts | gRPC | GraphQL (schema stitching across languages is fragile) |

**When GraphQL becomes a liability:**
- N+1 resolver problem at scale requires DataLoader everywhere -- easy to forget, hard to detect until production
- Authorization per-field is genuinely hard. Row-level + field-level + nested object permissions = custom middleware that duplicates your entire auth model
- HTTP caching effectively impossible (POST-only, dynamic shapes). CDN/proxy caching requires persisted queries + GET conversion
- Query complexity attacks: without depth/complexity limiting, a single query can join 8 levels deep and bring down your database

**When gRPC is wrong:**
- Browser clients need grpc-web proxy (Envoy), adding infrastructure complexity for simple CRUD
- Debugging requires protobuf-aware tools. curl/Postman don't work natively. Developer experience suffers during integration
- Streaming is powerful but connection management in serverless (Lambda, Cloud Functions) is problematic -- connections drop on cold start

## Database Architecture Gotchas

**Connection pooling (the #1 production surprise):**
- PgBouncer transaction mode: prepared statements break (use `statement_cache_size=0` in Prisma). Session mode works but limits concurrency to pool size
- Prisma default connection limit = `num_cpus * 2 + 1`. In serverless with 50 concurrent functions, that is 50 separate pools = 550 connections against a database with max_connections=100. Solution: external pooler (PgBouncer/PgCat) or Prisma Accelerate
- Serverless cold start connection storms: 100 functions wake simultaneously, each opens a pool. Use connection pooler with queuing, not direct database connections
- Supabase/Neon pooler modes: transaction mode for most queries, session mode ONLY when using prepared statements, LISTEN/NOTIFY, or advisory locks

**Query optimization beyond EXPLAIN:**
- Covering indexes: include all SELECT columns in the index to avoid heap fetches. `CREATE INDEX idx ON orders(user_id) INCLUDE (status, total)` -- 10-50x faster for narrow queries
- Partial indexes: `CREATE INDEX idx ON orders(created_at) WHERE status = 'pending'` -- index is 1% the size when 99% of orders are completed
- Materialized view refresh: `REFRESH MATERIALIZED VIEW CONCURRENTLY` requires a unique index but avoids table lock. Schedule during low-traffic windows, not on every request
- JSONB vs normalized: JSONB wins for write-heavy schemas with variable structure (event logs, form submissions). Normalized wins when you query individual fields across rows (reporting, filtering, joining). GIN indexes on JSONB are large and slow to update

## Scalability Patterns

**Read replica decisions:**
- Replication lag tolerance determines what can use replicas. Financial balances, inventory counts = primary only. User profiles, product catalogs = replicas fine
- "Read after write" problem: user updates profile, next page load hits replica, sees old data. Solutions: route to primary for N seconds after write, or use session-sticky routing

**Caching layers (in order of preference):**
1. CDN/edge cache -- for static + semi-static responses. Cache-Control headers, stale-while-revalidate
2. Application-level cache (Redis) -- for computed results, session data, rate limiting. Set TTL aggressively (minutes, not hours)
3. In-process cache (LRU map) -- for hot config, feature flags. Invalidation is per-instance (inconsistency risk in multi-instance deploys)
- Cache invalidation that works: event-driven invalidation via pub/sub (Redis PUBLISH or message queue), NOT time-based TTL alone. TTL is the safety net, not the strategy

**Message queue selection:**
- Kafka: ordered, durable, replayable. High operational overhead (ZooKeeper/KRaft, partition management, consumer group rebalancing). Use when you need event sourcing, audit trails, or stream processing
- RabbitMQ: flexible routing, simple operations, message-level acknowledgment. Use for task queues, request/reply patterns, priority queues
- SQS: zero operations, scales automatically, at-least-once delivery. Use when you want a queue without operating infrastructure
- "Exactly-once" is a myth in distributed systems. Design for at-least-once + idempotency keys on the consumer side

## Authentication Architecture

**JWT vs sessions (the real trade-offs):**
- JWT revocation problem: once issued, a JWT is valid until expiry. "Log out all devices" requires a blocklist (which is just a session store with extra steps). Short expiry (15 min) + refresh tokens mitigates but doesn't solve
- JWT size: a JWT with 5 roles, 10 permissions, and org context is 2-4KB. This travels with EVERY request. Sessions store a 32-byte ID client-side
- Refresh token rotation: issue a new refresh token with each access token refresh. If a refresh token is used twice, revoke the entire family (token theft detection)
- Use JWTs for: service-to-service auth where token verification without a network call matters. Use sessions for: user-facing applications where revocation and size matter

**OAuth2/OIDC gotchas:**
- PKCE is mandatory for SPAs and mobile (not optional). Authorization code without PKCE in a public client = authorization code interception attack
- Token storage in browsers: httpOnly cookie (preferred, immune to XSS) vs memory (lost on refresh) vs localStorage (XSS vulnerable). Never localStorage for access tokens
- Silent refresh (iframe-based) broke when browsers shipped third-party cookie blocking (Safari ITP, Chrome). Migration path: use refresh token rotation with httpOnly cookies instead

## Performance Debugging Patterns

**N+1 detection in ORMs:**
- Symptom: API endpoint sends 1 query for parent + N queries for children. 50 items = 51 queries, 500ms+ response time
- Prisma: use `include` (eager load) not property access (lazy load). Enable query logging (`log: ['query']`) and count queries per request in middleware
- TypeORM/Sequelize: `relations` option on find, or explicit `createQueryBuilder` with `leftJoinAndSelect`
- Detection: middleware that counts queries per request. Alert when count exceeds threshold (e.g., >10 queries for a single endpoint)

**Connection pool exhaustion:**
- Symptom: requests hang for exactly the pool timeout duration, then fail. CPU is low, memory is fine
- Cause: long-running transactions holding connections, unreturned connections from error paths, or pool size < concurrent request count
- Fix: set `statement_timeout` at the database level, wrap all queries in try/finally that returns connections, monitor `pg_stat_activity` for idle-in-transaction

**Node.js memory leaks (the usual suspects):**
- Event listener accumulation: `emitter.on()` in a request handler without `removeListener`. MaxListenersExceededWarning is your early signal
- Closure captures: closures in long-lived callbacks that capture large objects (request bodies, database result sets). The closure keeps the entire scope alive
- Buffer pool: reading large files into Buffer without streaming. 100 concurrent uploads of 10MB each = 1GB memory spike

## Error Handling Architecture

**Across service boundaries:**
- Use RFC 7807 Problem Details format: `{ type, title, status, detail, instance }`. Every service speaks the same error language
- Map internal errors to appropriate HTTP status at the boundary. Internal "UserNotFound" = 404, "InsufficientFunds" = 422, never expose internal error types to callers
- Include correlation ID in every error response. Propagate via `X-Request-ID` header across services for distributed tracing

**Circuit breaker implementation:**
- Open threshold: 5 failures in 30 seconds (not percentage-based -- low traffic makes percentages meaningless)
- Half-open: after 30 seconds, allow 1 probe request. If it succeeds, close. If it fails, reopen for another 30 seconds
- Fallback strategies: cached response (stale data > no data), degraded response (partial features), queue for retry (eventual consistency)

**Retry patterns:**
- Exponential backoff with jitter: `delay = min(base * 2^attempt + random(0, base), max_delay)`. Without jitter, retries from multiple clients synchronize and cause thundering herd
- Idempotency keys: client generates UUID, sends with request. Server stores key + response. Duplicate key = return stored response without re-executing. Essential for payment APIs, order creation, any state-changing operation

## Rationalization

| Content choice | Reasoning |
|---------------|-----------|
| Architecture decision matrix with team-size signals | Claude defaults to "it depends" -- first-match table forces concrete recommendations based on the actual signals that matter |
| When microservices HURT section | Training data skews toward microservices advocacy. The distributed monolith anti-pattern, synchronous call chain multiplication, and organizational-vs-computational scaling distinction are practitioner knowledge |
| Connection pooling gotchas with specific numbers | PgBouncer mode interactions, Prisma connection formula, serverless connection storms are production surprises not well-covered in documentation |
| Exactly-once semantics myth + idempotency keys | Distributed systems literature says this but most tutorials present message queues as reliable-by-default. Idempotency key pattern is the practical solution |
| JWT revocation problem framed as "session store with extra steps" | Most JWT tutorials present them as superior to sessions. The revocation problem and size trade-off are the actual decision factors |
| N+1 detection as middleware query counting | ORM documentation shows eager loading syntax but not how to detect the problem systematically in existing codebases |

## Red Flags

1. STOP if recommending microservices for a team under 5 engineers -- recommend modular monolith with clear module boundaries instead
2. STOP if suggesting direct database connections from serverless functions -- recommend an external connection pooler (PgBouncer, PgCat, or managed pooler)
3. STOP if storing JWTs in localStorage -- recommend httpOnly cookies or in-memory storage with refresh token rotation
4. STOP if designing synchronous call chains across 3+ services -- recommend async communication via message queue or merge services
5. STOP if implementing "exactly-once" delivery semantics -- design for at-least-once with idempotency keys instead
6. STOP if suggesting GraphQL for a public API with diverse clients -- recommend REST with OpenAPI spec for client diversity
7. STOP if using time-based TTL as the primary cache invalidation strategy -- recommend event-driven invalidation with TTL as safety net
8. STOP if the architecture discussion ignores data coupling -- ask about cross-domain data dependencies before recommending any architecture

## NEVER

1. NEVER recommend a shared database between microservices -- this creates a distributed monolith that is strictly worse than a regular monolith
2. NEVER skip connection pool configuration in production -- default pool settings cause connection exhaustion under real load
3. NEVER use OAuth2 authorization code flow without PKCE in public clients (SPAs, mobile) -- this enables authorization code interception attacks
4. NEVER implement retry logic without exponential backoff and jitter -- synchronized retries cause thundering herd and cascade failures
5. NEVER expose internal error types or stack traces across service boundaries -- use RFC 7807 Problem Details with mapped status codes
