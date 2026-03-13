# API Versioning and Evolution

Load when designing API versioning strategy, managing breaking changes, planning API deprecation, or setting up contract testing between services.

## Versioning Strategy Decision

First-match. Stop at the first row where the signal applies.

| Signal | Strategy | Trade-off |
|--------|----------|-----------|
| Public API with paying customers (Stripe, Twilio model) | URL path versioning (`/v1/`, `/v2/`) | Explicit and impossible to miss. But maintaining multiple live versions is expensive. |
| Internal APIs between teams, contract-driven | Header versioning (`Accept: application/vnd.api+json;version=2`) | Clean URLs, version negotiation possible. But invisible in browser/logs without tooling. |
| API evolving rapidly, pre-product-market-fit | No versioning, additive changes only | Maximum velocity. But requires discipline to never break existing fields. |
| GraphQL API | Schema evolution (deprecate fields, add new ones) | Built-in deprecation mechanism. But clients must actively update queries. |
| gRPC services | Protobuf field numbering (add fields, never reuse numbers) | Wire-compatible by design. But removing fields requires careful communication. |

**The version proliferation trap**: Supporting v1, v2, v3, v4 simultaneously means maintaining 4 codebases. Set a policy: maximum 2 live versions. When v3 launches, v1 sunsets. Communicate sunset 6 months before enforcement.

## Breaking vs Non-Breaking Changes

| Change Type | Breaking? | Safe Strategy |
|------------|-----------|---------------|
| Add new optional field to response | No | Add freely. Clients should ignore unknown fields (Postel's Law). |
| Add new required field to request | YES | Make it optional with a default value. Enforce as required in next major version. |
| Remove a response field | YES | Deprecate first (mark in docs, add `Sunset` header). Remove in next major version after deprecation period. |
| Change field type (string -> integer) | YES | Add new field with new name and correct type. Deprecate old field. |
| Change URL path | YES | Keep old path as redirect (301) for 6+ months. Monitor old path traffic to zero. |
| Change error response format | YES (often missed) | Version error format alongside API version. Clients parse errors too. |
| Add new enum value | Depends | Breaking for clients with exhaustive switch/match statements. Document that enum sets may grow. |
| Change pagination default (20 -> 50) | Borderline | If clients rely on exact page sizes, it breaks. Always let clients specify page size. |

**The "additive only" illusion**: Teams believe additive changes are always safe. But adding a field that changes the semantic meaning of an existing field IS breaking. Example: adding `currency` field to a response that previously assumed USD -- clients that don't read `currency` will misinterpret amounts.

## Deprecation Lifecycle

| Phase | Duration | Actions |
|-------|----------|---------|
| 1. Announce | Day 0 | Add `Deprecation` header to responses. Update API docs with sunset date. Email API consumers. |
| 2. Warning period | 3-6 months (public) / 1-3 months (internal) | Log all calls to deprecated endpoints. Send monthly usage reports to consumers. Provide migration guide. |
| 3. Sunset enforcement | After warning period | Return 410 Gone for deprecated endpoints. Include migration URL in error response body. |
| 4. Removal | 1 month after sunset | Remove code. But keep URL routing to return helpful 410 error (not 404). |

**Deprecation headers (RFC 8594)**:
```
Deprecation: Sat, 01 Sep 2026 00:00:00 GMT
Sunset: Sat, 01 Dec 2026 00:00:00 GMT
Link: <https://api.example.com/docs/migration-v3>; rel="successor-version"
```

**The 1% consumer problem**: 99% of API consumers migrate. The last 1% never will -- they have abandoned integrations, unmaintained code, or zombie services. Set a sunset date and enforce it. Holding the 99% hostage for the 1% is a losing strategy.

## Consumer-Driven Contract Testing

| Concept | Implementation | Why It Matters |
|---------|---------------|----------------|
| Consumer defines contract | Consumer team writes a test specifying what fields/types they need from the provider | Provider knows exactly which changes would break which consumers |
| Provider verifies contracts | Provider CI runs all consumer contracts against their API | Breaking changes caught before merge, not after deploy |
| Contract broker | Central registry (Pact Broker, PactFlow) stores all contracts | Visibility into all consumer-provider relationships. "Who uses this field?" becomes answerable. |
| Can-I-Deploy check | CI/CD gate that checks if current provider version satisfies all consumer contracts | Deploy confidence: if contracts pass, no consumer will break |

**Pact workflow**:
1. Consumer writes Pact test -> generates contract JSON
2. Contract published to Pact Broker
3. Provider CI downloads consumer contracts -> verifies against real API
4. `can-i-deploy` check before provider deployment
5. If any consumer contract fails -> provider build fails

**When contract testing is overkill**: Single team owning both consumer and provider. Under 5 API consumers. APIs that change less than quarterly. The overhead of contract infrastructure exceeds the risk of breakage.

## API Lifecycle Anti-Patterns

| Anti-Pattern | Consequence | Alternative |
|-------------|-------------|-------------|
| Versioning by date (`/2025-01-15/`) | Consumers can't tell which version has which features. Sorting is confusing. | Use semantic versioning (`/v1/`, `/v2/`) with changelog. |
| "Eternal beta" (never v1) | No commitment to stability. Consumers can't rely on any contract. | Ship v1 when you have 3+ consumers depending on the API. Beta is for exploration, not avoidance. |
| Breaking changes in PATCH version | Violates semver expectations. Consumers stop trusting version numbers. | PATCH = bug fixes only. MINOR = additive. MAJOR = breaking. |
| No changelog | Consumers discover changes by their code breaking | Maintain a CHANGELOG.md or API changelog endpoint. Every release, every change, every migration note. |
| Internal APIs treated as unversioned | "We control both sides" until another team starts consuming the API | Treat any API consumed by more than one team as a versioned contract. |
