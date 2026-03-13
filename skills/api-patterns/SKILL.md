---
name: api-patterns
description: "Use when designing REST APIs, choosing between API styles (REST/GraphQL/gRPC/tRPC), implementing authentication patterns, designing rate limiting, versioning APIs, or reviewing API architecture. Do NOT use for Stripe-specific API integration (use stripe-best-practices), MCP protocol design (use mcp-integration), or frontend data fetching patterns unrelated to API design."
---

# API Patterns & Architecture

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/authentication-deep-dive.md` | Designing auth for APIs, choosing between OAuth2 flows, JWT validation, API key management, webhook signing, mTLS setup | Rate limiting, versioning, general REST design |
| `references/rate-limiting-patterns.md` | Implementing rate limiting, choosing algorithms (token bucket, sliding window), distributed throttling with Redis, cost-based limiting | Auth patterns, versioning, API style selection |
| `references/versioning-and-evolution.md` | Planning API versioning strategy, managing breaking changes, contract testing, API lifecycle (experimental to sunset), backward-compatible evolution | Auth patterns, rate limiting, initial API design |
| `scripts/api_validator.py` | Validating an existing codebase for API best practices, checking OpenAPI specs | Design-phase decisions, auth or rate limiting questions |

## Scope Boundary

| In Scope | Out of Scope |
|----------|-------------|
| API style selection (REST, GraphQL, gRPC, tRPC) | Stripe-specific integration (use stripe-best-practices) |
| REST resource modeling and URL design | MCP protocol design (use mcp-integration) |
| Authentication and authorization architecture | Frontend data fetching (React Query, SWR) |
| Rate limiting design and algorithms | Infrastructure load balancing |
| API versioning and lifecycle management | Database schema design (use database skill) |
| Error response design and status codes | Monitoring and observability setup |
| Pagination, filtering, and sorting patterns | DevOps deployment pipelines |
| Contract testing strategy | Writing individual test cases (use testing-strategy) |
| OpenAPI specification design | Backend framework tutorials (use framework-specific skill) |

---

## API Style Selection Framework

Choosing the wrong API style is an architectural mistake that compounds for years. The decision depends on four measurable factors, not team preference.

### Decision Matrix

| Factor | REST | GraphQL | gRPC | tRPC |
|--------|------|---------|------|------|
| Team size <5 devs | Preferred | Overkill | Only if perf-critical | Preferred (TS monorepo) |
| Team size >20 devs | Good | Preferred (federation) | Service mesh | Not suitable |
| Single client (web) | Fine | Unnecessary | Unnecessary | Ideal |
| Multiple clients (mobile+web+3P) | OK | Preferred | Internal only | Not suitable |
| Public API for external devs | Preferred | Possible | Unusual | Not possible |
| Latency <50ms P99 required | Possible | Too much overhead | Preferred | Possible (local) |
| Nested/relational data shapes | N+1 risk | Preferred | Repeated calls | Possible |
| Flat CRUD resources | Preferred | Overkill | Overkill | Good |
| Binary/streaming data | Poor | Poor | Preferred | Poor |
| Real-time subscriptions | WebSocket add-on | Built-in | Bidirectional streaming | WebSocket add-on |

**When to combine styles:** Large systems often use REST for public APIs, gRPC for inter-service communication, and GraphQL as a BFF (Backend for Frontend) aggregation layer. This is not inconsistency -- it is matching the style to the boundary.

### The tRPC Constraint

tRPC eliminates the serialization boundary between client and server by sharing TypeScript types directly. This delivers extraordinary developer experience -- but only when both ends are TypeScript and deployed from the same repository. The moment you need a non-TypeScript consumer, a mobile client, or a public API, tRPC becomes a liability. Evaluate tRPC as a monorepo accelerator, not as a general API strategy.

### GraphQL Federation Threshold

GraphQL becomes cost-effective when three or more frontend teams consume overlapping backend data. Below that, the schema governance overhead (federation composition, schema registry, breaking change detection) exceeds the benefit of flexible queries. A single team consuming a single API is faster with REST or tRPC.

---

## REST API Design Architecture

### Resource Modeling

Resources are nouns. URLs identify resources, HTTP methods define operations. This principle is correct 90% of the time -- the other 10% is where experts differ from beginners.

**When to break the nouns-only rule:** Actions that do not map to CRUD on a single resource. `POST /payments/{id}/refund` is clearer than `POST /refunds` with a payment_id body field, because the refund is an action on a payment, not an independent resource. Similarly, `POST /reports/generate` is legitimate when report generation is a long-running process, not a simple read. The test: if the "action" creates or modifies a resource, model it as a resource. If it triggers a process, an RPC-style sub-path is appropriate.

**URL nesting depth:** Maximum 3 levels: `/users/{id}/orders/{id}/items`. Deeper nesting signals incorrect resource boundaries. If you reach `/users/{id}/orders/{id}/items/{id}/reviews`, the review is its own top-level resource with a query filter: `GET /reviews?item_id={id}`.

### HTTP Method Semantics

| Method | Semantics | Idempotent | Safe | Body |
|--------|-----------|-----------|------|------|
| GET | Read resource(s) | Yes | Yes | No |
| POST | Create resource or trigger action | No | No | Yes |
| PUT | Full replacement of resource | Yes | No | Yes |
| PATCH | Partial update | Yes* | No | Yes |
| DELETE | Remove resource | Yes | No | Optional |

*PATCH idempotency depends on the patch format. JSON Merge Patch (RFC 7396) is idempotent -- applying the same patch twice yields the same result. JSON Patch (RFC 6902) is not -- "add to array" appends on each application. This distinction matters for retry safety. If your API accepts retries (and it should for network reliability), prefer merge patch or document the idempotency guarantee explicitly.

**PUT vs PATCH in practice:** PUT requires the client to send the complete resource representation. Omitted fields are set to defaults or null. This makes PUT dangerous for resources with many fields -- clients must track the full schema. PATCH only transmits changed fields, but implementing PATCH correctly requires handling null vs absent (intent to clear vs intent to leave unchanged). Most teams implement "PATCH" but call it PUT, creating subtle bugs. Choose one, implement it correctly, document the contract.

### Status Code Selection

**2xx success:** 200 (read/update with body), 201 (create -- include Location header), 204 (success, no body -- DELETE, PUT/PATCH when echo is unnecessary).

**3xx redirect:** 301 (permanent -- cacheable), 302/307 (temporary -- 307 preserves method, 302 may not), 304 (not modified -- ETag/If-None-Match validation).

**4xx client error:** 400 (malformed request), 401 (not authenticated -- "who are you?"), 403 (not authorized -- "you cannot do this"), 404 (not found OR deliberately hiding 403 for security), 409 (conflict -- concurrent modification, duplicate key), 422 (semantically invalid -- parsed but business rules reject it), 429 (rate limited).

**5xx server error:** 500 (unhandled error -- always log, never expose internals), 502 (upstream dependency failed), 503 (overloaded -- include Retry-After header), 504 (upstream timeout).

**The 400 vs 422 distinction:** 400 means the request cannot be parsed (malformed JSON, wrong content type). 422 means the request is syntactically valid but semantically wrong (email format invalid, quantity negative). This distinction helps clients differentiate between serialization bugs and validation errors.

---

## Error Design & Response Patterns

### RFC 7807 Problem Details

Use a consistent error envelope. RFC 7807 (Problem Details for HTTP APIs) provides a standard:

```
{
  "type": "https://api.example.com/errors/insufficient-funds",
  "title": "Insufficient Funds",
  "status": 422,
  "detail": "Account balance is $10.00, but transfer requires $25.00.",
  "instance": "/transfers/abc-123",
  "balance": 1000,
  "required": 2500
}
```

The `type` URI should resolve to human-readable documentation. The `detail` field provides instance-specific context. Extension fields (`balance`, `required`) carry machine-readable data for client-side handling. Internal error codes (e.g., `ERR_INSUFFICIENT_FUNDS`) are useful for client error mapping but do not replace HTTP status codes -- they supplement them.

### Pagination Patterns

**Offset pagination** (`?page=3&per_page=20`): Simple to implement, allows jumping to arbitrary pages. Breaks at scale -- `OFFSET 100000` forces the database to scan and discard 100K rows. Crossover point: offset degrades noticeably at ~10K total records on most databases.

**Cursor pagination** (`?after=abc123&limit=20`): Uses an opaque cursor (typically base64-encoded primary key or sort value). Consistent performance regardless of dataset size. Cannot jump to arbitrary pages. Preferred for infinite scroll, feeds, and large datasets.

**Keyset pagination** (`?created_after=2025-01-01T00:00:00Z&limit=20`): Cursor pagination with transparent, human-readable cursors based on sort columns. Requires a deterministic sort order (add tie-breaker column if primary sort is not unique). Most efficient for time-series and sorted data.

### Filtering and Sorting

Use query parameters: `GET /orders?status=shipped&sort=-created_at&fields=id,total`. Prefix sort fields with `-` for descending. The `fields` parameter enables sparse fieldsets -- clients request only needed columns, reducing payload size and database load.

For complex filtering, avoid deeply nested query parameter schemas. If filter complexity exceeds 3 conditions, consider a `POST /orders/search` endpoint with a JSON body. This is not RESTful purism -- it is practical. Encoding complex filters in query strings produces unreadable URLs, caching nightmares, and URL length limit violations.

---

## Authentication & Authorization Patterns

Authentication answers "who are you?" Authorization answers "what can you do?" Conflating them is the root cause of most API security failures.

### Auth Method Selection

| Method | Authenticates | Best For | Not For |
|--------|-------------|----------|---------|
| **API Keys** | Application | Server-to-server, rate limit tracking, public API metering | User-level permissions, browser clients, mobile apps |
| **OAuth2** | User (delegated) | Third-party access, user consent flows, multi-tenant SaaS | Simple server-to-server, internal tools |
| **JWT** | Session | Stateless authentication, microservice propagation | Long-lived tokens, sensitive claims storage |
| **mTLS** | Service | Service mesh, zero-trust networks, certificate-based identity | Public APIs, browser clients, mobile apps |

**The critical distinction:** API keys identify the calling application. OAuth2 tokens identify the user who granted permission. A request can carry both -- the API key identifies which application is calling, and the OAuth2 token identifies which user authorized it. Stripe uses this dual model: API key for the merchant's server, connected account tokens for user-delegated actions.

### Token Lifecycle Principles

Access tokens should be short-lived (15 minutes) because they cannot be individually revoked without a blocklist check on every request. Refresh tokens should be long-lived (7-30 days) but rotated on every use -- issuing a new refresh token and invalidating the old one. If a rotated-out refresh token is replayed, it signals theft: revoke the entire token family. See `references/authentication-deep-dive.md` for OAuth2 flow selection, JWT validation checklist, HMAC webhook signing, and mTLS architecture.

---

## Rate Limiting Architecture

Rate limiting protects APIs from abuse, ensures fair usage, and prevents cascade failures during traffic spikes.

### Algorithm Selection

**Token bucket** for most APIs -- allows bursts up to bucket capacity while enforcing average rate. **Sliding window counter** for smooth enforcement without boundary spikes (weighted combination of current and previous fixed windows, O(1) memory). **Fixed window** only for internal services where boundary spikes (2x burst at window edges) are tolerable.

### Distributed Rate Limiting

In multi-instance deployments, rate limiting requires a shared counter store (Redis is the standard). The core challenge is atomicity: two requests hitting different instances must not both read "under limit" and both proceed. Use Lua scripts or Redis MULTI/EXEC for atomic check-and-increment. Accept that distributed rate limiting is best-effort during partitions -- a client may get 2x the limit briefly, which is acceptable for most systems. See `references/rate-limiting-patterns.md` for Redis Lua scripts, cost-based limiting (endpoint weight scoring), tiered limits by auth level, and retry strategies.

---

## Named Anti-Patterns

### The God Endpoint
One route handles everything via query parameters: `GET /api?action=getUser&id=5` or `POST /api` with an action field in the body. Violates resource modeling, defeats HTTP caching, makes documentation impossible, and hides the API surface from security audits. **Detect:** single route handling 5+ distinct operations. **Fix:** decompose into resource-specific endpoints.

### The Chatty API
N+1 client calls because resources are too granular. Client fetches `/users/1`, then `/users/1/profile`, then `/users/1/preferences`, then `/users/1/avatar`. Four round trips for one screen. **Detect:** client makes 3+ sequential calls to render a single view. **Fix:** composite endpoints (`GET /users/1?include=profile,preferences`), BFF aggregation layer, or evaluate GraphQL if the pattern is pervasive.

### The Phantom Version
Version appears in the URL (`/v2/users`) but behavior is identical to v1. Teams increment versions prophylactically or copy-paste routes without changing logic. Increases maintenance surface with zero benefit. **Detect:** diff between version handlers shows no behavioral difference. **Fix:** version only when a breaking change actually exists.

### Auth Theater
Token is validated (signature checked, expiry verified) but scopes and permissions are not enforced. Any authenticated user can access any resource. The authentication layer creates a false sense of security while authorization is missing entirely. **Detect:** endpoints check `isAuthenticated()` but never check `hasPermission()`. **Fix:** implement RBAC or ABAC and enforce at every endpoint.

### Schema Drift
The actual API response diverges from the documented schema. Optional fields appear or disappear. Types change between string and number. Nested objects gain undocumented properties. Consumers build on undocumented behavior, then break when it changes. **Detect:** compare OpenAPI spec against actual responses (contract testing). **Fix:** generate OpenAPI from code (not manually) and run contract tests in CI.

### The Breaking "Fix"
Changing error codes, response field names, or response shapes in a "patch" release. The team considers it a bug fix; consumers experience it as a breaking change. **Detect:** any response structure change in a non-major version. **Fix:** classify all response shape changes as breaking. Use the versioning-and-evolution reference for the full breaking change taxonomy.

---

## Rationalization Table

| Shortcut | Why It Seems OK | Why It Fails | Do This Instead |
|----------|----------------|-------------|-----------------|
| "REST for everything" | REST is the default standard | gRPC handles inter-service 5-10x faster; GraphQL eliminates N+1 for complex UIs; tRPC removes serialization in TS monorepos. Using REST everywhere means suboptimal performance or overfetching where alternatives excel. | Evaluate per boundary. Public API = REST. Internal high-throughput = gRPC. Multi-client flexible queries = GraphQL. TS monorepo = tRPC. |
| "We don't need versioning yet" | No breaking changes planned | The first breaking change is always unplanned. Without a versioning strategy, any response change risks breaking consumers. Retrofitting versioning after launch requires coordinating all existing clients. | Establish versioning strategy before first consumer. URL-path versioning is simplest to start. |
| "API keys are fine for auth" | Simple to implement | API keys authenticate the application, not the user. They cannot represent delegated permissions, expire gracefully, or be scoped per-operation. Leaked API keys grant full access with no revocation granularity. | API keys for server-to-server and rate limit identification. OAuth2 for user-delegated access. JWT for stateless session tokens. |
| "Just return 500 for all errors" | Simpler error handling | Clients cannot distinguish between retry-safe failures (503, 429) and permanent failures (400, 404). Every error triggers the same retry logic, amplifying load during outages. Status codes exist to convey failure semantics. | Map internal errors to appropriate HTTP status codes. Use RFC 7807 for error bodies. |
| "Pagination isn't needed for small datasets" | Only 50 records today | Datasets grow. An unpaginated endpoint becomes a performance bomb when records hit 10K+. Adding pagination later requires a breaking API change (response moves from array to object with metadata). | Always paginate list endpoints from day one. Default limit of 20-50 with cursor-based pagination. |

---

## Red Flags Checklist

Stop and reassess the API design when any of these conditions appear:

- [ ] **Single endpoint handles 5+ distinct operations** -- God Endpoint anti-pattern. Decompose into resource-specific routes immediately.
- [ ] **Client makes 3+ sequential API calls to render one view** -- Chatty API. Add composite endpoints, a BFF layer, or evaluate GraphQL.
- [ ] **No authentication on endpoints that modify data** -- Security gap. Every write endpoint needs auth. No exceptions.
- [ ] **API returns 200 for error conditions** -- Broken HTTP semantics. Clients and proxies interpret 200 as success. Use appropriate 4xx/5xx codes.
- [ ] **Response schema differs from OpenAPI documentation** -- Schema Drift. Implement contract testing in CI to catch divergence automatically.
- [ ] **No rate limiting on public-facing endpoints** -- Abuse vector. Implement rate limiting before launch, not after the first incident.
- [ ] **Error responses expose stack traces or internal paths** -- Information disclosure. Return RFC 7807 Problem Details externally; log full details internally.
- [ ] **Breaking changes deployed without version increment** -- Consumer trust destruction. Classify changes using the breaking change taxonomy and version accordingly.
- [ ] **JWT tokens have no expiration or expiration >24 hours** -- Compromised tokens remain valid indefinitely. Access tokens: 15 minutes. Refresh tokens: 7-30 days with rotation.
- [ ] **All list endpoints return unbounded results** -- Memory bombs on large datasets. Add pagination with sensible defaults and maximum page sizes.
