# Test Data Strategies

## Factory Pattern Implementation

Factories eliminate brittle fixture files, reduce test setup boilerplate by 60-80%, and make test intent visible by showing only the fields that matter for each test.

### Core Principles (Language-Agnostic)

**1. Sensible Defaults:** Every factory produces a valid entity with zero arguments. Defaults represent the "happy path" entity.

**2. Targeted Overrides:** Tests override only the fields relevant to the behavior under test. If testing deactivation, override only `active: false`. This makes test intent explicit.

**3. Sequences for Uniqueness:** Auto-increment counters or UUIDs for unique constraints. Email: `user-{n}@test.com`. Never hardcode unique values -- parallel execution will collide.

**4. Traits for Common Variants:** Named presets for frequently needed states. `UserFactory.build(trait: "admin")` sets role, permissions, and admin-specific fields. Traits are composable: `build(traits: ["admin", "inactive"])`.

**5. Associations via Composition:** An OrderFactory calls CustomerFactory and ProductFactory internally. The caller can override associated objects but doesn't have to build them manually.

### Builder Pattern for Complex Objects

When entities have 10+ fields with complex interdependencies, builders add clarity: `TestOrderBuilder.new().with_customer(premium: true).with_line_items(3).with_discount(percent: 15).build()`. Use when the combination of fields matters and simple overrides don't convey intent.

### Anti-Patterns in Factory Design

**God Factory:** A single factory that produces every entity type. Grows into an unmaintainable monolith. Fix: one factory per domain entity, composed through associations.

**Fixture Masquerading as Factory:** A factory that reads from a YAML/JSON file instead of generating data. Inherits all the brittleness of fixtures. Fix: factories generate data programmatically.

**Over-Specification:** Factories that set 30 fields when the entity only requires 5. Every unnecessary field is a maintenance burden and potential test coupling. Fix: set only required fields and fields needed for valid state. Let database defaults handle the rest.

---

## Fixture Management

### When Fixtures Are Appropriate

Factories replace fixtures for dynamic data. But fixtures remain correct for:

- **Reference data** that is static and shared: country codes, currency definitions, tax rate tables, permission role definitions
- **Seed data** for development and staging environments: sample users, demo products, test tenants
- **Large datasets** for performance testing: generating 100K rows via factory is too slow; load from a fixture file
- **Snapshot testing baselines**: expected JSON responses, expected HTML output

### Fixture Lifecycle

**Shared fixtures** (loaded once per suite): Reference data, configuration, lookup tables. Immutable during tests. If a test needs to modify reference data, it must create its own copy.

**Per-test fixtures** (loaded and destroyed per test): State that tests mutate. Each test gets a fresh copy. Never rely on fixture state from a previous test.

**Warning:** Shared mutable fixtures are the #1 cause of "passes alone, fails in suite" bugs. If you see this pattern, the first investigation step is checking for shared mutable state.

---

## Database Strategies for Testing

### Strategy Comparison

| Strategy | Speed | Isolation | Realism | Best For |
|----------|-------|-----------|---------|----------|
| Transaction rollback | Fastest | High | High | Most tests (default choice) |
| Truncate + reseed | Fast | High | High | Tests that commit transactions |
| In-memory DB (SQLite) | Fast | High | Low | Simple queries only |
| Test containers | Medium | Highest | Highest | Schema/engine-specific behavior |
| Dedicated test DB | Slow | Medium | High | Shared integration environments |
| Database-per-test | Slowest | Highest | Highest | Multi-tenant, DDL testing |

### Transaction Rollback (Default Strategy)

Wrap each test in a transaction; roll back after completion. Returns to pre-test state in milliseconds. **Limitation:** Cannot test code that commits transactions or uses separate connections (async workers). Fall back to truncate + reseed.

### Test Containers

Disposable database instances in Docker. Use when testing engine-specific features (Postgres JSONB, MySQL full-text, MongoDB aggregation), migrations, or schema changes. Start containers once per CI run, not per test. Use database templates (`CREATE DATABASE ... TEMPLATE`) to clone migrated databases in milliseconds.

### In-Memory Database Caveats

SQLite-in-memory substituting for Postgres/MySQL is dangerous: missing JSON operators, window functions, CTEs; different type coercion and transaction isolation. Use only for standard SQL with no engine-specific features.

---

## State Isolation Techniques

**Process-level:** Each test process gets its own database, temp directory, and environment. Default in most parallel runners.

**Thread-level:** Each test gets a dedicated transaction, temp directory, and thread-local storage. Shared singletons (connection pools, caches) must be reset or scoped per test.

**Environment variables:** Set and restore in teardown, or use DI-injected configuration objects. Tests reading `process.env` directly without restoring contaminate subsequent tests.

---

## Production Data Anonymization

### When to Use Production Data

Production data is valuable for: reproducing production-only bugs, performance testing with realistic data distributions, validating migrations against real schemas.

Production data is dangerous when: it contains PII (names, emails, addresses, payment details), it contains credentials or secrets, compliance frameworks prohibit it (GDPR, HIPAA, SOC2).

### Anonymization Pipeline

1. **Identify sensitive fields:** PII columns, credential fields, API keys, free-text fields that may contain PII
2. **Choose anonymization strategy per field:**
   - **Fake replacement:** Replace names with faker-generated names, emails with test domains
   - **Hashing:** One-way hash identifiers to preserve uniqueness and referential integrity without reversibility
   - **Redaction:** Replace with fixed string ("[REDACTED]") for fields where value doesn't matter
   - **Bucketing:** Replace precise values with ranges (age 34 -> "30-40") for analytics data
3. **Preserve referential integrity:** The anonymized `user_id` in the orders table must match the anonymized `id` in the users table. Use deterministic hashing (same input always produces same output) for foreign key fields.
4. **Validate post-anonymization:** Run application code against anonymized data. If it crashes on unexpected values, the anonymization broke constraints. Fix the pipeline, don't fix the tests.
5. **Automate the pipeline:** Anonymization must be reproducible and auditable. A manual export-and-scrub process will eventually leak PII through human error.

### Never Do This

- Copy production databases directly to test environments without anonymization
- Use production API keys or credentials in test environments
- Anonymize "most" fields and leave some PII "because it's internal only"
- Store anonymized production data in version control (it's still derived from PII)

---

## Seed Data vs Generated Data

| Criterion | Seed Data (Fixtures) | Generated Data (Factories) |
|-----------|---------------------|---------------------------|
| Determinism | Identical every run | Varies (unless seeded RNG) |
| Readability | Explicit, visible in files | Defined in code, requires reading factory |
| Maintenance | Manual updates on schema change | Auto-adapts when factory updated |
| Coverage of edge cases | Only what's explicitly written | Random generation finds unexpected edges |
| Performance test suitability | Good (bulk load from file) | Poor (generation overhead) |
| Realistic data distribution | Only if carefully crafted | Statistically representative if factories mirror production distributions |

**Recommended approach:** Seed data for baseline state (reference tables, default configuration). Factories for entity data in tests. Property-based testing with constrained random generation for edge case discovery.

---

## Test Data for Distributed Systems

### Challenge: Cross-Service Data Consistency

In microservices, a "test user" may need records in the auth service, profile service, billing service, and permissions service. Creating test data requires coordinating across service boundaries.

### Strategies

**Shared test data service:** A dedicated microservice that creates consistent test entities across all services via their APIs. Tests call `testDataService.createUser(traits)` and get back IDs valid in all services. Expensive to build but eliminates per-test coordination.

**Event-driven setup:** Create the user in the auth service. Let event propagation create records in downstream services. Wait for eventual consistency before asserting. Slower but tests the real propagation path.

**Per-service isolation:** Each service's tests use only that service's database. Cross-service behavior is validated by contract tests, not by shared test data. Fastest and most isolated but misses integration bugs.

**Recommendation for SMB teams (3-20 engineers):** Start with per-service isolation plus contract tests. Add event-driven setup for critical cross-service flows (user creation, order processing). Build a shared test data service only if you have 5+ services with complex cross-service test scenarios.
