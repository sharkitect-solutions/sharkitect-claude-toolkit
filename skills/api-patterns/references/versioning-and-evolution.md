# API Versioning & Evolution

## Breaking Change Taxonomy

Not all changes break consumers equally. Classify changes to determine whether a version increment is required.

### Always Breaking (requires major version)

| # | Change | Why It Breaks |
|---|--------|---------------|
| 1 | Remove response field | Consumers parsing it crash or get null |
| 2 | Rename a field | Same as remove + add; old name stops working |
| 3 | Change field type | `19.99` to `"19.99"` breaks typed clients |
| 4 | Make optional field required in requests | Existing clients omitting it get 400 |
| 5 | Remove an endpoint | Clients calling it get 404 |
| 6 | Change URL structure | All client integrations break |
| 7 | Change HTTP method semantics | Idempotent PUT becoming non-idempotent breaks retries |
| 8 | Add auth to public endpoint | Previously working clients get 401 |
| 9 | Change error response structure | Client error-parsing logic breaks |
| 10 | Reduce rate limits | Clients at previous limits get 429s |
| 11 | Change pagination structure | Page navigation logic breaks |
| 12 | Remove or redefine enum values | Exhaustive client switches fail |

### Never Breaking (safe without version change)

Adding optional response fields, new endpoints, new optional query params, increasing rate limits, adding new enum values (caveat: document "expect new values" in contract), adding error codes for new conditions.

### Context-Dependent

Making a required request field optional (usually safe unless clients depend on server defaults). Changing default values (breaks clients relying on old defaults). Adding stricter validation (rejects previously accepted data). Performance changes (slower may trigger client timeouts).

---

## Versioning Strategy Selection

| Strategy | Example | Advantages | Disadvantages | When to Use |
|----------|---------|-----------|---------------|-------------|
| **URL Path** | `GET /v2/users/{id}` | Most discoverable; visible in logs and docs; easy load balancer routing; cacheable | Suggests entire API changes at once; proliferates route definitions; enables version-by-copy-paste | Public APIs, external consumers, teams without API gateway |
| **Header** | `API-Version: 2` | Clean URLs; version individual resources; supports content negotiation | Invisible in browser/logs; requires custom headers; harder manual testing | Internal APIs, SaaS platforms, sophisticated consumers |
| **Query Param** | `?api_version=2` | Easy to add to any URL | Mixes with business params; complicates caching; no standard convention | Rarely -- only as migration path for previously unversioned APIs |

---

## API Lifecycle Management

Every API endpoint moves through a defined lifecycle. Managing transitions explicitly prevents surprise breakage.

### Lifecycle Stages

**Experimental** -- Available under a feature flag, beta header, or `/beta/` prefix. No stability guarantees. May change or disappear without notice. Consumers accept the risk explicitly. Duration: 1-6 months.

**Stable** -- Production-ready. Covered by versioning guarantees. Breaking changes require a new major version. This is the default state for all production endpoints. Duration: indefinite (until deprecated).

**Deprecated** -- Still functional but scheduled for removal. Returns `Deprecation: true` header and `Sunset: <date>` header (RFC 8594). Documentation prominently marks deprecated status with migration guide. Duration: minimum 6 months for public APIs, 3 months for internal.

**Sunset** -- Endpoint removed. Returns 410 Gone with a body pointing to the replacement endpoint. After sunset, the URL should not be reused for a different purpose (consumers with stale caches would get unexpected responses).

### Sunset Header Implementation

```
HTTP/1.1 200 OK
Sunset: Sat, 01 Mar 2026 00:00:00 GMT
Deprecation: true
Link: </v3/users>; rel="successor-version"
```

The `Sunset` header gives consumers a machine-readable deadline. The `Link` header with `successor-version` relation points to the replacement. Monitoring consumers who still call deprecated endpoints: log and alert, then proactively reach out before the sunset date.

**Minimum sunset windows:** Public API: 12 months. Partner API: 6 months. Internal API: 3 months. These are minimums -- longer is better. Stripe maintains deprecated API versions for years.

---

## Contract Testing

Contract testing verifies that API producers and consumers agree on the interface, without requiring end-to-end integration tests.

### Consumer-Driven Contracts

The consumer defines what it needs from the producer (a subset of the full API). The producer runs the consumer's contract tests in CI. If the producer changes something the consumer depends on, the test fails before deployment.

**Key principle:** The consumer does not test the entire API -- only the fields and behaviors it actually uses. This means the producer can freely change parts no consumer depends on.

**Workflow:**
1. Consumer team writes contract: "I call `GET /users/{id}` and expect `{id, name, email}` in the response."
2. Contract is shared via a broker (Pact Broker, schema registry) or committed to a shared repository.
3. Producer CI runs all consumer contracts against the actual implementation.
4. If a contract fails, the producer knows which consumer would break and can negotiate the change.

### Schema Validation in CI

For teams not ready for full contract testing, validate OpenAPI schemas against actual responses:

1. **Generate OpenAPI from code** (not manually). Frameworks like NestJS/Swagger, FastAPI, and Spring OpenAPI generate specs from decorators/annotations. Manual specs drift.
2. **Record actual responses** during integration tests.
3. **Validate recorded responses against the OpenAPI schema.** Fail CI if any response contains fields not in the schema or is missing required fields.
4. **Diff the OpenAPI schema** on every PR. Flag additions (safe), modifications (review), and removals (breaking).

---

## Backward-Compatible Evolution Patterns

### Additive-Only Changes

The safest evolution strategy: only add, never remove or modify. New fields in responses, new optional parameters in requests, new endpoints, new enum values. Consumers ignoring unknown fields are never affected. This works until you need to fix a design mistake -- then you need versioning.

### Envelope Wrapping

When a response structure must change, wrap the old structure in a new envelope rather than modifying it:

**Before:** `{"users": [...]}`
**After:** `{"data": {"users": [...]}, "meta": {"total": 100, "page": 1}}`

Clients parsing `response.users` still work. New clients use `response.data.users` and gain metadata. The envelope pattern buys time for migration without a version bump -- but document a timeline for removing the old root-level structure.

### Feature Flags in APIs

Introduce new behavior behind a request header or query parameter: `X-Feature: new-pagination`. Consumers opt in by sending the header. Once adoption reaches a threshold (e.g., 80% of traffic uses the new feature), make it the default and sunset the old behavior.

**Governance:** Track which feature flags are active. Set expiration dates. Feature flags that live longer than 6 months become permanent technical debt -- either graduate them to default behavior or remove them.

### Expand-Contract Migration

For field renames or type changes that cannot be done additively:

1. **Expand:** Add the new field alongside the old field. Both contain the same data. Document the old field as deprecated.
2. **Migrate:** Give consumers time to switch to the new field. Monitor usage of both fields via API analytics.
3. **Contract:** Remove the old field in a new major version (or after the sunset window).

Duration: minimum one full sunset window between expand and contract phases.

---

## OpenAPI Schema Versioning

**Schema-first vs code-first:** Start schema-first for initial design (forces interface thinking before implementation). Switch to code-first generation after v1 ships (prevents drift). Validate generated schemas against the original design contract in CI. Frameworks like NestJS/Swagger, FastAPI, and Spring OpenAPI generate specs from annotations.

**Changelog discipline:** Maintain a machine-readable API changelog alongside the OpenAPI spec. Each entry: date, version, change type (added/modified/deprecated/removed), affected endpoints, migration notes. Consumers subscribe to the changelog and receive proactive notification of changes rather than discovering them when their code breaks.
