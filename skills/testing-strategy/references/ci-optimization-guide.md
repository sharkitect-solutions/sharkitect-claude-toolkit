# CI Test Optimization Guide

## Test Parallelization Architectures

### File-Level Splitting (Simplest)

Distribute test files evenly across N workers. Zero configuration, works with any runner. **Weakness:** imbalanced when file sizes vary -- pipeline time equals slowest worker. Good enough for suites <500 tests.

### Time-Based Splitting (Recommended Default)

Record execution time per test file, distribute using bin-packing to equalize worker time. Reduces wall-clock time 30-50% versus naive splitting. CircleCI has native `circleci tests split --split-by=timings`. GitHub Actions requires custom script. Fall back to file-level splitting when timing data is unavailable.

### Container-Level Splitting (Advanced)

N Docker containers, each with own database and process space. Use when tests have heavy infrastructure dependencies. Each container incurs setup time (pulling images, migrations), so diminishing returns beyond 5-8 containers as setup time dominates.

---

## Selective Test Execution

### Git Diff-Based Selection

Analyze changed files in the PR, map to affected test files, run only those tests.

**Mapping approaches:**
1. **Convention-based:** `src/billing/calculator.py` maps to `tests/billing/test_calculator.py`. Simple, works for 1:1 relationships. Misses cross-module dependencies.
2. **Import graph analysis:** Parse import statements to build a dependency graph. Changed file X is imported by files A, B, C which have tests in test_A, test_B, test_C. Run those tests. More accurate but requires tooling.
3. **Build system integration:** Nx, Bazel, and Turborepo maintain dependency graphs as part of their build model. `nx affected --target=test` runs exactly the affected tests. Most accurate and maintained automatically.

**Safety net:** Always run the full suite on merges to the main branch. Selective execution on PRs catches most issues; the full suite on merge catches dependency graph misses.

**Measured impact:** For mature monorepos, selective execution reduces PR test time by 60-90%. A 25-minute full suite drops to 2-5 minutes for typical PRs that touch 3-10 files.

### Changed-Code Coverage Analysis

After running affected tests, measure whether the changed lines are actually covered by the tests that ran. If changed lines have zero coverage, flag the PR for missing tests. This catches the case where the dependency graph doesn't connect a change to any test.

---

## Caching Strategies

### Dependency Cache

Cache `node_modules/`, `.venv/`, `~/.m2/` between runs, keyed on lockfile hash. Saves 1-5 minutes per run. First optimization to implement -- highest ROI, lowest risk.

### Build Cache

Cache compiled artifacts between runs. Docker: `--cache-from` with registry image reuses unchanged layers (saves 2-10min). TypeScript: cache `.tsbuildinfo` and `node_modules/.cache/` (saves 30-90s).

### Test Result Cache

Cache results keyed on source file hashes -- skip re-execution when files unchanged. **Warning:** only safe for deterministic tests. Nx/Bazel implement this natively, reducing incremental test time to near-zero for unchanged packages.

---

## Fail-Fast Ordering

Run the tests most likely to fail first. When they fail, abort early and report within 1-2 minutes instead of waiting for the full suite.

### Ordering Priority

1. **Tests touching changed files** (highest signal): If `billing.py` changed, run `test_billing.py` first. The changed code is most likely to contain the defect.
2. **Recently failed tests**: Tests that failed in the last 5 CI runs have a higher probability of failing again (regression, flaky, or area under active development).
3. **Fast tests before slow tests**: Among equally-likely-to-fail tests, run the fast ones first. A 10ms unit test failing in minute 1 is more useful than a 30s E2E test failing in minute 5.
4. **New tests** (no history): Tests written in this PR are unproven. Run them early to catch authoring mistakes.

Split CI into "fast feedback" (changed-file tests + recently failed, blocks on failure) and "full validation" (everything else). Most runners support this: pytest `--first-failed`, Jest `--changedSince` + `--bail`.

---

## Test Time Budgets

### Setting Budgets

| Stage | Wall Clock Budget | Rationale |
|-------|------------------|-----------|
| Lint + type check | 2 min | Static analysis on cached builds |
| Unit tests | 5 min | Fast feedback on logic correctness |
| Integration tests | 10 min | Service boundary validation |
| E2E tests (critical paths) | 15 min | User journey confidence |
| Full pipeline | 25 min | Maximum acceptable PR feedback time |

**Enforcement:** Track stage times in CI dashboards. Set alerts when a stage exceeds 80% of its budget. Investigate before it hits 100%.

**Budget breach protocol:**
1. Identify the slowest tests in the breaching stage (most CI platforms report per-test timing)
2. Are they in the right layer? Slow "unit" tests are often integration tests in disguise. Reclassify.
3. Can they be parallelized further? Add workers if compute cost is acceptable.
4. Can selective execution skip them for this PR? Not all tests need to run on every change.
5. Are they flaky and retrying? Flaky retries inflate execution time. Fix the flake instead.

If unit tests take 15 minutes with 8 workers, the problem is architecture, not CI. Likely: tests doing I/O (reclassify), expensive setup (share at suite level), coupled modules (prevents selective execution), excessive test data (1000 records when 3 suffice). Fixing architecture gives 5-20x improvement; CI tricks give 2-3x.

---

## Flaky Test Quarantine and Management

### Detection

**Automatic detection:** Run each failing test 2-3 times. If it passes on retry, mark it as flaky (not failing). Track flake rate per test over time.

**Manual reporting:** Give developers a one-click "flag as flaky" option in CI reports. Low friction reporting catches flakes that automatic detection misses (e.g., tests that flake only under specific timing conditions).

### Quarantine Process

1. **Immediate:** Move flaky test to a non-blocking suite. It still runs, but failures don't block the PR. Record the quarantine date and the observed flake rate.
2. **Triage (within 48 hours):** Assign an owner. Root cause analysis: timing dependency, shared state, external service dependency, or resource contention.
3. **Fix or delete (within 1 sprint):** Fix the root cause and return to the blocking suite. If unfixable within a sprint, evaluate whether the test provides enough value to justify the maintenance cost. If not, delete it and document the coverage gap.
4. **Track metrics:** Quarantine count over time should be stable or declining. A rising quarantine count signals a systemic problem (test infrastructure, shared environments, or cultural tolerance of flakiness).

### Common Root Causes and Fixes

| Root Cause | Symptom | Fix |
|-----------|---------|-----|
| Timing dependency | Passes/fails based on system load | Use explicit waits with conditions, not sleep. Mock time-sensitive operations. |
| Shared state | Fails when run after specific other test | Isolate state per test (transaction rollback, temp directories) |
| Port conflicts | Fails in parallel, passes serial | Use dynamic port allocation (port 0), not hardcoded ports |
| External service | Fails when third-party API is slow/down | Mock external services in unit/integration. Separate E2E suite for external deps. |
| Resource exhaustion | Fails after N tests in a suite | Leak detection: unclosed connections, file handles, event listeners. Add cleanup in teardown. |
| Non-deterministic data | Fails on specific generated values | Seed random generators. Log generated values for reproduction. |

---

## Cost Optimization for Cloud CI

### Compute Cost Reduction

**Spot instances:** 60-90% cost savings for unit/integration tests. Add retry-on-preemption. **Right-size:** tests are CPU-bound, use compute-optimized instances (c-series). **Concurrency limits:** cap parallel workers per repo to prevent budget spikes.

### Time-Cost Trade-Off

| Approach | Time Savings | Cost Impact |
|----------|-------------|-------------|
| 2x parallelism | ~45% faster | ~80% more compute cost |
| 4x parallelism | ~70% faster | ~250% more compute cost |
| Selective execution | 60-90% faster | 60-90% less compute cost |
| Result caching | 50-95% faster | 50-95% less compute cost |
| Dependency caching | 10-30% faster | Net savings (less download) |

**Key insight:** Selective execution and caching save both time and money. Parallelism trades money for time. Optimize for selective execution first, then add parallelism for the tests that must run.

### Budget Monitoring

Track CI spend per repository, per branch, per test stage. Set alerts at 80% of monthly budget. Common causes of budget spikes:
- Flaky tests triggering excessive retries
- Abandoned branches with active CI schedules
- Test suite growth without parallelism or selective execution adjustment
- Missing dependency caches causing full reinstalls every run
