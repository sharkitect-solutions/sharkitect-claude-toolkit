# Test Velocity and Program Management

## When NOT to A/B Test

Testing everything is as wrong as testing nothing. Testing capacity is finite.

| Situation | Why Skip Testing | What to Do Instead |
|---|---|---|
| **Obvious bugs or broken UX** | You don't experiment on whether to fix broken things. Every day the bug exists costs conversions | Fix immediately. Compare pre/post metrics with interrupted time series analysis if you want to measure impact |
| **<500 weekly conversions on test page** | At 5% baseline and 10% MDE, you need ~30K visitors per variant. At 500 conversions/week, that's 12+ weeks per test | Make the change. Monitor for 2 weeks. Use pre/post comparison with caution. Or test on a higher-traffic page |
| **Compliance or legal requirement** | GDPR cookie banner, accessibility fix, Terms of Service update. No choice in implementation | Implement. Measure impact retroactively if needed |
| **Infrastructure or performance changes** | CDN migration, database optimization, caching improvements. Affect all users equally | Benchmark before/after. A/B testing infrastructure changes introduces operational risk |
| **The change is easily reversible and low-risk** | Color of a non-primary element, copy in a tooltip, spacing adjustment | Ship it. If metrics move negatively, revert. Save test capacity for high-impact changes |
| **You've already tested this** | Same hypothesis tested 6 months ago, nothing changed since | Review previous results. Only retest if traffic composition has significantly changed |

---

## Test Prioritization Framework

### ICE Scoring (and Its Failures)

ICE = Impact x Confidence x Ease (each scored 1-10, multiply for priority score)

| ICE Component | What Teams Get Wrong | Better Approach |
|---|---|---|
| **Impact** | Scored intuitively ("this feels high impact"). No connection to actual traffic or conversion data | Impact = (traffic to test page) x (realistic MDE) x (revenue per conversion). Calculate, don't estimate |
| **Confidence** | "I'm 8/10 confident this will work." Personal confidence ≠ evidence | Confidence should reflect DATA: do you have heatmaps, user research, competitor evidence, or past test results? Score 1-3 (gut), 4-6 (qualitative data), 7-10 (quantitative evidence) |
| **Ease** | Underestimated 80% of the time. "Easy" means "I haven't thought about edge cases yet" | Ease = implementation time + QA time + monitoring time. Get engineering estimate before scoring |

### Better Prioritization: Expected Value

```
Expected Value = P(variant wins) x Expected Revenue Impact x Test Duration Factor

Where:
- P(variant wins) = your honest estimate (historically, 20-30% of tests produce significant winners)
- Expected Revenue Impact = traffic x MDE x revenue per conversion x 12 months
- Test Duration Factor = 1 / (weeks to reach significance). Faster tests get priority because capacity is finite
```

### Prioritization by Test Type

| Priority | Test Type | Why Prioritize | Typical Impact |
|---|---|---|---|
| 1 | **High-traffic page, high-revenue action** | Maximum expected value. Homepage CTA, pricing page, checkout flow | 5-15% lift = significant revenue |
| 2 | **Known UX problem with data** | Heatmaps/recordings show the problem. High confidence in diagnosis | 10-30% lift when fixing confirmed problems |
| 3 | **Cross-selling / upsell touchpoints** | Revenue per user increase without traffic increase | 3-8% lift on ARPU, compounds across all users |
| 4 | **New feature rollout measurement** | Low incremental cost (feature already built). Validates product decisions | Binary: feature works or doesn't. Justifies engineering investment |
| 5 | **Copy/messaging variations** | Fast to implement, moderate impact | 2-10% lift. Low effort, moderate reward |
| 6 | **Design/layout changes** | Slower to implement, uncertain impact direction | 0-15% lift. Higher variance |

---

## Test Velocity Benchmarks

| Organization Maturity | Tests per Month | What Enables This |
|---|---|---|
| **Beginner** (1 person part-time) | 1-2 | One testing tool, marketing tests only, manual analysis |
| **Developing** (dedicated owner) | 3-5 | Established process, engineering support for server-side tests, basic analysis pipeline |
| **Mature** (experimentation team) | 10-20 | Dedicated experimentation platform, server-side infrastructure, automated analysis, review board |
| **Advanced** (experimentation culture) | 20-50+ | Feature flags on everything, all product changes are experiments, automated metric monitoring, ML-powered prioritization |

### Velocity Constraints (What Actually Limits You)

| Constraint | Impact | How to Unblock |
|---|---|---|
| **Traffic** | Can only run 1-2 tests at a time on the same page | Test on different pages simultaneously. Or use smaller MDE (accept detecting only large effects) |
| **Engineering bandwidth** | Server-side tests compete with product roadmap | Build reusable test infrastructure (component-level flags, config-driven variants). First test takes 2 weeks, subsequent tests take 2 days |
| **Analysis bandwidth** | Results pile up, nobody analyzes them | Automate standard analysis. Pre-built dashboards. Only escalate surprising results for deep analysis |
| **Idea quality** | Running out of good test ideas | Systematic idea generation: heatmap review, user testing sessions, competitor analysis, customer support ticket mining |
| **Organizational buy-in** | Stakeholders override test results or skip testing | Build a test results repository. Track cumulative revenue impact. Show the cost of decisions made WITHOUT testing |

---

## Running Multiple Simultaneous Tests

### Interaction Effects

| Scenario | Risk | Mitigation |
|---|---|---|
| **Tests on different pages** | LOW. Checkout test and homepage test don't interact | Run freely in parallel. Check that traffic allocation doesn't starve either test |
| **Tests on same page, different elements** | MEDIUM. Headline test + CTA test might interact (certain headlines pair better with certain CTAs) | Accept the interaction risk (usually small). Or run MVT if you suspect strong interaction. Document which tests were concurrent |
| **Tests on same element** | HIGH. Two tests modifying the same button/section will conflict | Never run overlapping tests on the same element. Queue them sequentially |
| **Tests on sequential funnel steps** | MEDIUM. Landing page test affects who reaches checkout. Checkout test results depend on landing page variant | Analyze checkout test results segmented by landing page variant. Be aware of composition effects |

### Traffic Allocation Across Tests

| Total Weekly Visitors | Max Concurrent 50/50 Tests (same page) | Why |
|---|---|---|
| 1K-5K | 1 | Not enough traffic to split further. Each variant needs sufficient sample |
| 5K-20K | 1-2 | Can run 2 non-overlapping tests if on different pages |
| 20K-100K | 2-4 | Sufficient traffic for multiple tests. Watch for interaction effects |
| 100K+ | 5-10+ | Can run multiple tests including MVT. Use mutual exclusion layers for overlapping elements |

### Mutual Exclusion (Layered Testing)

For high-traffic sites running many concurrent tests:

| Layer | What It Contains | How Assignment Works |
|---|---|---|
| Layer 1: Navigation | Header tests, menu tests, search tests | Users randomized independently for this layer |
| Layer 2: Content | Headline tests, image tests, copy tests | Users randomized independently (different seed) |
| Layer 3: CTA | Button tests, form tests, pricing tests | Users randomized independently |

Each layer is independent. A user might be in variant A for Layer 1, variant B for Layer 2, and control for Layer 3. This prevents tests from blocking each other while maintaining statistical independence within each layer.

---

## Test Rollout Procedure

After a test produces a winner:

| Step | Action | Common Mistake |
|---|---|---|
| 1. **Document results** | Record hypothesis, metrics, confidence, effect size, segments | Skipping documentation. 6 months later, nobody remembers why the page looks this way |
| 2. **Implementation review** | The variant in the test may be a quick hack (DOM manipulation). Production implementation may differ | Assuming test variant = production code. Client-side test modifications need proper engineering implementation |
| 3. **Ramp to 100%** | Keep the winning variant in the testing tool. Ramp from 50% to 75% to 100% over 3-5 days | Immediately removing the test and hard-coding the change. Ramp catches issues the test didn't (edge cases, scale effects) |
| 4. **Permanent implementation** | Replace test code with permanent production code | Leaving the test running indefinitely ("it works, don't touch it"). Test code has runtime cost and dependency on the testing tool |
| 5. **Post-implementation monitor** | Watch metrics for 2 weeks after permanent implementation | Declaring victory and moving on. Novelty effects fade. Seasonal factors may change the result |
| 6. **Archive test** | Move to completed tests repository with full documentation | Deleting test data. You'll want it when someone asks "didn't we test this before?" |

---

## Building an Experimentation Culture

| Maturity Stage | Characteristics | Next Step |
|---|---|---|
| **Ad hoc** | Tests happen occasionally. No process. Results lost | Establish a test request form and results repository. One person owns experimentation |
| **Reactive** | Tests happen when someone has an idea. Basic process exists | Implement systematic prioritization (ICE/expected value). Monthly test planning meetings |
| **Proactive** | Regular test cadence. Prioritized backlog. Results reviewed | Build automated analysis pipeline. Empower product teams to run their own tests |
| **Systematic** | Every major change is tested. Feature flags standard. Automated analysis | Invest in advanced methods (sequential testing, multi-armed bandits, Bayesian). Experiment on experimentation (meta-optimization) |
| **Cultural** | Experimentation is default. "Ship it without testing" requires justification, not "test it" | Continuous optimization. ML-powered test generation. Automated personalization |
