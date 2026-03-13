---
name: testing-strategy
description: "Use when designing test architecture, choosing what to test, building test pyramids, planning E2E test strategy, managing test data, optimizing CI test pipelines, or establishing testing standards for a project. Do NOT use for writing individual unit tests, debugging test failures, or test framework API reference."
---

# Testing Strategy & QA Architecture

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/test-pyramid-patterns.md` | Designing test layer ratios, choosing pyramid shape, migrating from ice cream cone, analyzing cost-per-test by layer | Writing specific tests, CI optimization, test data questions |
| `references/test-data-strategies.md` | Building factory patterns, managing fixtures, designing database strategies for tests, handling state isolation, anonymizing production data | Pyramid design, CI pipeline optimization, flaky test remediation |
| `references/ci-optimization-guide.md` | Reducing CI test execution time, parallelizing test suites, implementing selective test execution, managing flaky tests in CI, setting test time budgets | Pyramid design, test data management, choosing what to test |

## Scope Boundary

| In Scope | Out of Scope |
|----------|-------------|
| Test pyramid and layer architecture | Writing individual test cases |
| What-to-test decision frameworks | Framework API reference (Jest, Pytest, etc.) |
| E2E strategy and critical path mapping | Debugging specific test failures |
| Test data management architecture | Database administration |
| CI test pipeline optimization | CI/CD pipeline setup from scratch |
| Testing standards for engineering teams | Code review process (use code-review skill) |
| Contract testing between services | API design (use api-patterns skill) |
| Visual regression testing strategy | Frontend component development |
| Test metrics and reporting | Project management or sprint planning |
| Flaky test remediation architecture | Individual flaky test root cause debugging |

---

## Test Pyramid Architecture

The test pyramid is a resource allocation model, not a dogma. The shape you choose determines where you spend engineering time and where you get confidence.

### Layer Responsibilities

**Unit tests** validate isolated logic: pure functions, business rules, state transitions, data transformations. Answer: "Does this piece work correctly in isolation?" Target: <5ms per test.

**Integration tests** validate collaboration: API endpoints with real middleware, database queries against real schemas, service-to-service contracts. Answer: "Do these pieces work correctly together?" Target: <500ms per test.

**E2E tests** validate user outcomes: complete user journeys through the real system, multi-step workflows, cross-service transactions. Answer: "Can the user accomplish their goal?" Target: <30s per test.

**Static analysis** (linting, type checking, dead code detection) catches defects at zero runtime cost. It is the foundation beneath every pyramid shape.

### Choosing the Right Shape

**Classic Pyramid** (70/20/10) -- Default for monolithic applications, libraries, and CLI tools. Heavy unit layer because most logic lives in a single codebase where isolation is cheap.

**Testing Trophy** (5/25/40/30 static/unit/integration/E2E) -- For applications where integration points are the primary risk. SPAs with API backends, CRUD-heavy services, middleware-dependent systems. Kent C. Dodds formalized this: test behavior at the integration layer where user confidence is highest per dollar spent.

**Diamond Model** (20/60/20) -- For microservices architectures where contract compliance between services matters more than internal unit logic. Heavy integration layer validates that service boundaries hold.

**Honeycomb Model** (10/70/20) -- For infrastructure, platform, and DevOps systems where integration with external dependencies (cloud APIs, OS primitives, network) is the dominant risk. Internal logic is often thin.

The wrong shape wastes engineering time. An ice cream cone (heavy E2E, light unit) for a math library is absurd. A classic pyramid for a thin API gateway that delegates everything is equally wasteful.

---

## What-to-Test Decision Framework

### Risk-Based Prioritization

Every test costs engineering time to write, maintain, and execute. Prioritize by risk:

```
Test Priority = Failure Probability x Business Impact x Detection Difficulty
```

**Always test (high priority):**
- Payment and billing logic (high impact, hard to detect silently)
- Authentication and authorization boundaries (security + compliance)
- Data transformations that cross system boundaries (serialization, API contracts)
- Business rules with branching logic (state machines, pricing engines, eligibility checks)
- Anything that failed before (regression anchors)

**Test strategically (medium priority):**
- CRUD operations (test the edge cases: concurrent writes, partial updates, cascade deletes)
- UI interactions on critical paths (checkout, onboarding, core workflows)
- Third-party API integrations (contract tests, not full integration tests)
- Configuration and feature flag logic

**Skip or minimize (low priority):**
- Framework glue code (routing declarations, ORM model definitions, DI container config)
- One-to-one wrapper functions that add no logic
- CSS styling (except critical-path visual regression)
- Generated code (test the generator, not the output)
- Simple getters/setters with no logic

### The Test-This-Not-That Decision Tree

1. Does it contain business logic or branching? YES -> test it. NO -> continue.
2. Does it transform data between boundaries? YES -> test the transformation. NO -> continue.
3. Has it caused a bug before? YES -> regression test. NO -> continue.
4. Would failure be silently catastrophic? YES -> test it. NO -> continue.
5. Is it pure framework plumbing? YES -> skip. NO -> write a test.

---

## Testing Layer Design

### Unit Tests: Isolation Boundaries

**What to isolate:** External services, databases, file systems, network calls, system clocks, random number generators -- anything non-deterministic that makes tests slow, flaky, or order-dependent.

**Test doubles hierarchy** (use the weakest double that proves the behavior):

| Double | What It Does | Use When |
|--------|-------------|----------|
| **Dummy** | Placeholder, never called | Satisfying a required parameter |
| **Stub** | Returns pre-configured values | Controlling indirect inputs |
| **Spy** | Records calls for later assertion | Verifying interactions without replacing behavior |
| **Mock** | Pre-programmed expectations | Verifying specific call sequences matter |
| **Fake** | Working implementation (simplified) | Real dependency is too slow/complex (in-memory DB, fake SMTP) |

If you mock more than 2 dependencies in a single test, the test is testing wiring, not behavior. Refactor to reduce coupling, or promote to integration level. Design for testability: inject dependencies through constructors or parameters. Code that instantiates its own dependencies is untestable without monkey-patching.

### Integration Tests: Service Boundary Validation

**Contract tests** verify that service interfaces match expectations on both sides. Consumer-driven contracts let downstream services specify what they need; producers verify compliance. The principle is tool-agnostic: test the agreement, not the implementation.

**Database integration tests:** Use real database engines, not mocks. In-memory alternatives (SQLite for Postgres) miss engine-specific behavior (JSON operators, window functions, transaction isolation). Test containers provide disposable, real-engine instances.

**API integration tests:** Test the full request/response cycle through middleware, serialization, validation, and error handling. Mock only external downstream services, never your own middleware stack.

### E2E Tests: Critical Path Strategy

**Identify critical paths first.** Cover the 5-15 user journeys representing 80% of business value: sign up, core workflow, payment, account management, and top feature flows.

**Page Object Model (POM):** Encapsulate UI interaction details behind named methods. `checkoutPage.completePayment(card)` survives UI redesigns; `driver.findElement(By.css('#pay-btn')).click()` does not. POMs reduce E2E maintenance cost by 40-60%.

**Flaky test management:** A flaky test is worse than no test -- it trains the team to ignore failures. Quarantine immediately, fix within one sprint, delete if unfixable.

**Visual regression testing:** Screenshot diffing catches CSS regressions that functional tests miss. Use perceptual diff algorithms (not pixel-exact), run on 2-3 viewport sizes, 1 browser.

---

## Test Data Management

### Factory Patterns

Factories generate test objects with sensible defaults and targeted overrides. They replace fixture files that become stale and brittle as schemas evolve.

**Principles:**
- Each factory produces a single valid entity with all required fields populated
- Override only the fields relevant to the specific test case
- Use sequences for unique constraints (email, username) to avoid collision
- Compose factories: an Order factory calls LineItem and Customer factories
- Never share mutable factory output between tests -- create fresh per test

### Fixture vs Factory Decision

| Criterion | Use Fixtures | Use Factories |
|-----------|-------------|---------------|
| Schema changes frequently | No | Yes |
| Tests need unique data per run | No | Yes |
| Complex object relationships | No | Yes |
| Reference data (countries, currencies) | Yes | No |
| Seed data for development DB | Yes | No |
| Large datasets for performance testing | Yes (file-based) | No (too slow to generate) |

### State Isolation

Every test must start from a known state and leave no residue. Isolation failures cause the most frustrating debugging sessions in testing -- "it passes alone but fails in the suite."

**Strategies by speed:**
1. **Transaction rollback** (fastest): Wrap each test in a transaction, roll back after. Works for single-database tests. Fails when testing transaction logic itself.
2. **Truncate and reseed** (fast): Clear tables between tests, insert baseline data. Works for multi-table scenarios. Slower than rollback.
3. **Database-per-test** (slowest, most isolated): Spin up a fresh database instance. Use only when schema DDL is under test or isolation is paramount (multi-tenant testing).

---

## CI Test Optimization

### Test Time Budgets

Set hard time limits per CI stage. When exceeded, the suite is failing even if all tests pass.

| Stage | Budget | What Happens When Exceeded |
|-------|--------|---------------------------|
| Static analysis + lint | 2 min | Add incremental analysis, cache results |
| Unit tests | 5 min | Parallelize, remove slow tests to integration |
| Integration tests | 10 min | Test containers caching, selective execution |
| E2E tests | 15 min | Reduce critical paths, parallelize browsers |
| Full pipeline | 25 min | Mandatory architectural review of test strategy |

**Why 25 minutes total:** Beyond 25 minutes, developers context-switch away from the PR. Review research shows that feedback loops >10 minutes reduce fix quality. At 30+ minutes, developers batch multiple changes per push, making failures harder to diagnose.

### Parallelization Strategies

**File-level splitting** (simplest): Distribute test files across N workers. Works when test files are roughly equal duration. Produces worker imbalance when file sizes vary.

**Time-based splitting** (recommended): Record test execution times, distribute files to workers to equalize total time per worker. Rebalances automatically as tests are added or removed. Most CI platforms support this natively (CircleCI test splitting, GitHub Actions matrix).

**Selective execution** (advanced): Analyze which source files changed, map to dependent test files via import graph, run only affected tests. Reduces execution by 60-90% on incremental changes. Requires maintaining a dependency map -- build tools like Nx, Bazel, or Turborepo compute this automatically. Fall back to full suite on dependency map changes or configuration changes.

### Fail-Fast Ordering

Run tests most likely to fail first: (1) tests touching changed files, (2) tests that failed in the last N runs, (3) fast tests before slow tests. A failure detected in minute 1 saves 24 minutes of pipeline time versus discovering it at minute 25.

---

## Testing Anti-Patterns

### The Ice Cream Cone
60%+ E2E, few unit tests. Teams start from the user perspective but never invest in lower layers. E2E tests are 10-50x slower and 5-10x more brittle. **Detect:** E2E >40% of test count or execution time. **Fix:** Push logic tests down. Keep E2E only for integration-dependent journeys.

### The Assertion-Free Test
Tests that execute code but verify nothing meaningful (`expect(result).toBeTruthy()` on a function that always returns an object). Pure cost, zero signal. **Detect:** Tautological assertions or zero assertions. **Fix:** Every test asserts a specific, falsifiable behavior.

### The Flaky Suite Tolerance
5-15% intermittent failures. Team re-runs CI until green. Destroys trust -- real failures get ignored. **Detect:** Flake rate. Healthy <1%, dangerous >3%, catastrophic >10%. **Fix:** Quarantine to non-blocking suite. Fix or delete within one sprint.

### The Mock Overload
Tests mock 3+ dependencies, assert mocks were called correctly. Tests your mocking setup, not behavior. **Detect:** >2 doubles per test; tests break on refactor without behavior change. **Fix:** Reduce coupling. Prefer fakes. Promote to integration tests.

### The Slow Feedback Loop
Suite takes 10+ minutes. Developers skip tests locally, batch changes. **Detect:** If developers say "I'll let CI run it," the loop is broken. **Fix:** Separate fast tests (<5s locally) from slow tests. Fast tests before every commit.

### The Coverage Theater
90%+ line coverage but tests written to hit lines, not verify behaviors. **Detect:** High coverage, low defect detection. **Fix:** Mutation testing instead. Target mutation score >70% on business logic.

---

## Test Architecture by Project Type

| Project Type | Pyramid Shape | Primary Risk Layer | Testing Emphasis |
|-------------|--------------|-------------------|-----------------|
| REST/GraphQL API | Trophy | Integration | Request/response contracts, middleware, auth, error handling |
| SPA (React, Vue, etc.) | Trophy | Integration | Component interaction, state management, API integration |
| Mobile App (RN, Flutter) | Diamond | Integration + E2E | Platform-specific behavior, device matrix, offline mode |
| CLI Tool | Classic Pyramid | Unit | Argument parsing, output formatting, error codes, file system ops |
| Data Pipeline (ETL) | Diamond | Integration | Schema validation, transformation correctness, idempotency, failure recovery |
| Microservices | Diamond | Integration | Contract testing, eventual consistency, circuit breakers, retry behavior |
| Library / SDK | Classic Pyramid | Unit | API surface coverage, backward compatibility, edge cases, documentation examples as tests |
| E-commerce Platform | Trophy | Integration + E2E | Checkout flow, payment processing, inventory consistency, pricing rules |
| Real-time System | Honeycomb | Integration | Latency bounds, message ordering, reconnection, backpressure handling |

---

## Rationalization Table

| Shortcut | Why It Seems OK | Why It Fails | Do This Instead |
|----------|----------------|-------------|-----------------|
| "We'll add tests later" | Shipping fast feels productive | Test debt compounds exponentially. Code written without tests is designed without testability. Retrofitting costs 3-5x more than writing tests alongside code. | Write tests for business logic as you write the code. Skip tests only for throwaway prototypes with a defined expiration date. |
| "E2E tests cover everything" | User-level tests feel comprehensive | E2E tests are combinatorially incomplete. 3 features with 4 states each = 64 combinations. E2E might cover 5. Unit tests cover all 64 in milliseconds. | Use E2E for critical paths only (5-15 journeys). Push combinatorial testing to unit and integration layers. |
| "Mocking makes tests fast" | Mocked tests run in milliseconds | Mocked tests test assumptions, not reality. When the real dependency changes behavior, mocked tests still pass. You discover the break in production. | Use the weakest test double needed. Prefer fakes over mocks. Run integration tests with real dependencies in CI. |
| "We need 90% coverage" | High numbers feel safe | Coverage rewards testing easy code and ignoring hard code. The 10% uncovered is usually the 10% most likely to break (error paths, race conditions, edge cases). | Target coverage by risk tier: 90%+ on business logic, 70%+ on integration glue, 50%+ on UI, ignore generated code. |
| "Our tests pass, so the code works" | Green CI feels safe | Tests only prove what they assert. A passing suite with weak assertions proves nothing. A passing suite that does not cover the changed code proves nothing about the change. | Review test quality alongside code. Require meaningful assertions. Run mutation testing periodically to verify test strength. |

---

## Red Flags Checklist

Stop and reassess the testing approach when any of these appear:

- [ ] **E2E test suite takes >20 minutes** -- Feedback loop is broken. Developers are skipping tests or batching changes. Audit test distribution across layers.
- [ ] **Flaky test rate >3%** -- Suite trust is degrading. Quarantine immediately. Fix flaky tests before writing new ones.
- [ ] **Test failures are routinely re-run without investigation** -- The team has normalized test unreliability. This is a culture problem, not a technical one.
- [ ] **New features ship without tests and "we'll add them later"** -- Test debt is accumulating. It will not be paid later. Establish test requirements in the definition of done.
- [ ] **Integration or E2E tests assert implementation details** -- Tests break on every refactor. They test structure, not behavior. Rewrite to assert outcomes.
- [ ] **Test suite has >50% mocked dependencies** -- Tests are disconnected from reality. Refactor toward fakes and real dependencies.
- [ ] **Coverage is >85% but bugs still reach production regularly** -- Coverage is measuring the wrong thing. Introduce mutation testing to measure test effectiveness.
- [ ] **No test runs locally in <2 minutes** -- Developers cannot iterate. Separate fast and slow test suites immediately.
- [ ] **Test data is shared between tests via global state** -- Order-dependent failures are inevitable. Isolate test data per test.
- [ ] **Nobody on the team can explain the test architecture** -- Tests are ad hoc, not strategic. Document the testing pyramid shape, layer responsibilities, and conventions.

---

## Testing Metrics That Matter

**Defect Escape Rate:** Bugs found in production / total bugs found. Target: <10%. High escape rate means tests cover the wrong things.

**Mean Time to Detect (MTTD):** Time from bug introduction to test failure. Target: <1 hour unit/integration, <4 hours E2E.

**Test Execution Time Trend:** Plot weekly. Should be flat or declining. Rising trend = architecture not scaling.

**Flaky Test Percentage:** Target: <1%. Track weekly. Rising trend requires immediate quarantine.

**Coverage by Risk Tier:** Business logic 90%+, integration glue 70%+, UI 50%+, generated code 0%. Blended numbers are meaningless.

**Mutation Testing Score:** Code mutations caught by tests. Target: >70% on business logic. More meaningful than line coverage.

**Test Maintenance Ratio:** Fix/update time / new test time. Healthy: <0.3. Above 0.5 = too coupled to implementation. Above 1.0 = restructure.
