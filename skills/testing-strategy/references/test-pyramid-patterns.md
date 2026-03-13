# Test Pyramid Patterns

## Shape Analysis with Ratio Guidelines

The pyramid shape is a resource allocation decision. Each shape optimizes for a different risk profile. Choosing wrong wastes engineering effort on the wrong layer.

### Classic Pyramid (70/20/10)

**Ratio:** 70% unit, 20% integration, 10% E2E.

**Optimizes for:** Codebases where most complexity lives in business logic within a single process. The majority of defects are logic errors catchable in isolation.

**Best fit:** Monolithic applications, libraries, SDKs, CLI tools, calculation engines, compilers, parsers.

**Cost profile:** Lowest total test execution time. Highest test count but fastest aggregate run. Unit tests cost ~$0.01 each to execute in CI (measured as compute-seconds). Integration tests cost ~$0.10. E2E tests cost ~$1.00 or more when including browser/device overhead.

**Failure mode:** If the application is primarily an integration layer (thin business logic, heavy I/O), you end up with thousands of unit tests that verify trivial code while integration bugs slip through.

### Testing Trophy (5/25/40/30)

**Ratio:** 5% static analysis, 25% unit, 40% integration, 30% E2E.

**Optimizes for:** Applications where the integration between components is the primary source of bugs. Most defects occur at boundaries: API calls, database queries, state management, component composition.

**Best fit:** SPAs with API backends, full-stack web applications, CRUD services, middleware-heavy systems.

**Why 40% integration:** Kent C. Dodds' research showed that integration tests provide the highest confidence-per-dollar for web applications. They exercise real component interaction without the brittleness of full E2E. A component rendering test that fires a click and verifies state change through multiple layers catches more real bugs than isolated unit tests of each layer.

**Failure mode:** Without discipline, the "integration" layer bloats to include slow, flaky tests that should be E2E or fast tests that should be unit. Define layer boundaries explicitly.

### Diamond Model (20/60/20)

**Ratio:** 20% unit, 60% integration, 20% E2E.

**Optimizes for:** Distributed systems where service boundaries are the dominant risk. Individual services have thin logic but complex interactions.

**Best fit:** Microservices architectures, event-driven systems, API gateway compositions, multi-service workflows.

**Why heavy integration:** In microservices, a single feature spans 3-7 services. Unit testing each service's internal logic gives false confidence -- the real bugs are in contract mismatches, serialization differences, eventual consistency race conditions, and retry/timeout interactions. Contract tests and service integration tests catch these.

**Contract testing emphasis:** Consumer-driven contracts are the backbone of the diamond. Each consuming service declares what it expects. The producing service runs these contracts as tests. When a producer changes its API, consumer contracts fail before deployment. This prevents "works on my service" integration bugs.

**Failure mode:** Without centralized contract management, contract tests drift. Teams write integration tests against mocked services that don't reflect reality.

### Honeycomb Model (10/70/20)

**Ratio:** 10% unit, 70% integration, 20% E2E.

**Optimizes for:** Infrastructure and platform systems where almost all behavior depends on external system interaction.

**Best fit:** Terraform/Pulumi modules, Kubernetes operators, CI/CD pipeline tools, database drivers, cloud SDK wrappers, monitoring/alerting systems.

**Why minimal unit tests:** Infrastructure code has minimal pure logic. A Terraform module's value is that it correctly calls AWS APIs and configures resources -- mocking the AWS API defeats the purpose. Integration tests against real (or emulated) cloud services are the only meaningful validation.

**Failure mode:** Integration tests against real cloud services are slow and expensive. Requires careful use of cloud emulators (LocalStack, MinIO) and test account isolation.

---

## Layer Boundary Definitions

Clear boundaries prevent "layer creep" where integration tests disguised as unit tests (or vice versa) blur the pyramid shape.

### Unit Layer Boundary

A test is a **unit test** if and only if:
- It runs in-process (no network, no file system, no database)
- It completes in <50ms
- It can run in any order, in parallel, without setup/teardown beyond object construction
- It tests a single behavior (one logical assertion per test, though multiple physical assertions are fine)

If a test requires a running database, HTTP server, or message queue -- even in-memory versions -- it is an integration test, not a unit test. Mislabeling slow "unit" tests inflates the unit count and hides feedback loop problems.

### Integration Layer Boundary

A test is an **integration test** if:
- It exercises 2+ real components collaborating (e.g., handler + middleware + database)
- It may use real infrastructure (test containers, in-memory databases, local HTTP servers)
- It completes in <2s (tests consistently >2s should be audited)
- It does NOT require a full deployed environment or browser

### E2E Layer Boundary

A test is an **E2E test** if:
- It exercises the system from an external user's perspective (browser, API client, CLI invocation)
- It runs against a deployed (or locally composed) environment with all services running
- It validates complete user journeys, not individual API endpoints

---

## Migration Strategy: Ice Cream Cone to Pyramid

### Phase 1: Stop the Bleeding (Week 1-2)
Freeze new E2E test creation. Every new test must justify its layer. Default new tests to integration unless E2E is required for the specific behavior.

### Phase 2: Identify Pushdown Candidates (Week 2-3)
Audit existing E2E tests. For each, ask: "Is this testing a user journey that requires the full stack, or is it testing business logic that happens to be triggered through the UI?" Business logic tests are pushdown candidates.

### Phase 3: Write Lower-Layer Replacements (Week 3-8)
For each pushdown candidate, write the equivalent unit or integration test first. Verify it catches the same defect class. Then delete the E2E version. Never delete an E2E test without a lower-layer replacement confirmed working.

### Phase 4: Establish Ratios (Ongoing)
Track test count and execution time by layer weekly. Set targets based on your chosen shape. Make ratio drift visible in team dashboards.

**Expected timeline:** 6-12 weeks for a 500-test suite. The cone does not flip overnight. Rushing creates coverage gaps.

---

## Cost-Per-Test Analysis

| Metric | Unit | Integration | E2E |
|--------|------|-------------|-----|
| Write time | 5-15 min | 15-45 min | 30-120 min |
| Execution time | 1-50ms | 100ms-2s | 5-60s |
| Maintenance (annual) | Low | Medium | High |
| CI compute cost | ~$0.001 | ~$0.01-0.10 | ~$0.50-5.00 |
| Flakiness risk | Near zero | Low | Medium-High |
| Defect localization | Exact line | Component boundary | "Somewhere in the stack" |
| Confidence per test | Low (isolated) | Medium (realistic) | High (user-level) |
| Confidence per dollar | High | Highest | Lowest |

The "confidence per dollar" row is why the trophy and diamond models exist. A single integration test that exercises a real API call through real middleware to a real database provides more production-representative confidence than 20 unit tests mocking every boundary. But it costs 10-100x more to run. The optimal allocation depends on where your bugs actually occur.

**Measure, don't assume:** Track where production bugs originate by layer. If 80% of production bugs are integration failures, a classic pyramid with 70% unit tests is misallocated regardless of what textbooks recommend.
