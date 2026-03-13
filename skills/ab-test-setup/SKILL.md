---
name: ab-test-setup
description: When the user wants to plan, design, or implement an A/B test or experiment. Also use when the user mentions "A/B test," "split test," "experiment," "test this change," "variant copy," "multivariate test," or "hypothesis." For tracking implementation, see analytics-tracking. For CRO strategy and test ideas, see page-cro. For statistical methods beyond experimentation, see statistical-analysis.
---

# A/B Test Setup

## File Index

| File | What It Contains | Load When |
|---|---|---|
| `SKILL.md` | Test design decisions, hypothesis framework, analysis methodology, anti-patterns | Always loaded (you are here) |
| `statistical-pitfalls.md` | SRM detection, multiple comparisons, Bayesian vs frequentist, sequential testing, when calculators lie | User asks about statistics, significance, sample size issues, or test results seem wrong |
| `platform-implementation.md` | Tool comparison (PostHog/Optimizely/VWO/LaunchDarkly/Statsig/Eppo), client-side vs server-side gotchas, CDN interference, feature flag migration | User asks about implementation, tool selection, or debugging test setup |
| `test-velocity-management.md` | Prioritization frameworks (ICE/PIE gotchas), test backlog management, velocity benchmarks, when NOT to test, rollout procedures | User asks about test prioritization, program management, or scaling experimentation |

**Do NOT load** companion files unless the user's question specifically requires that depth. Most test design questions are answerable from this file alone.

## Scope Boundary

| Topic | This Skill | Not This Skill (Use Instead) |
|---|---|---|
| Designing experiments | YES | |
| Hypothesis formulation | YES | |
| Sample size decisions | YES | |
| Test analysis methodology | YES | |
| Statistical significance | YES | statistical-analysis (for general stats) |
| Bayesian A/B testing | YES | statistical-analysis (for Bayesian theory) |
| CRO test ideas | | page-cro, signup-flow-cro, popup-cro |
| Event tracking setup | | analytics-tracking |
| Multivariate copy testing | | copywriting |
| Feature flag management (non-experiment) | | Use engineering judgment |
| Pricing experiments | Hypothesis + measurement | pricing-strategy (for pricing decisions) |

---

## Test Type Decision

Pick the first match:

| Signal | Test Type | Why |
|---|---|---|
| Major page redesign or new flow | **Split URL test** | Different URLs avoid client-side modification complexity. Cleaner implementation for structural changes |
| Multiple simultaneous element changes + >50K weekly visitors | **Multivariate (MVT)** | Tests interaction effects between changes. Requires 4-10x traffic of simple A/B. Most teams overestimate their traffic for MVT |
| Testing a new feature rollout | **Feature flag with measurement** | Not every rollout needs full A/B infrastructure. Binary on/off with pre/post comparison is sufficient when effect size is large (>30%) |
| Comparing 3+ creative approaches | **A/B/n** | Multiple variants, single change dimension. Requires Bonferroni or Holm correction for multiple comparisons (most tools don't do this automatically) |
| Single change hypothesis | **A/B (50/50 split)** | Default. Simple, fast to reach significance, easiest to analyze correctly |

**The MVT trap**: Teams run MVT because it feels more "scientific." Reality: a 2x2 MVT with 4 cells needs ~4x the traffic of a simple A/B per cell. A site with 10K weekly visitors running a 2x2 MVT needs 16+ weeks vs 4 weeks for simple A/B. Run sequential A/Bs instead.

---

## Hypothesis Quality Ladder

| Level | Example | Problem |
|---|---|---|
| 1 (Weak) | "Let's test a new button color" | No reasoning, no prediction, no measurement criteria |
| 2 (Directional) | "A green button will increase clicks" | Has prediction but no reasoning or quantification |
| 3 (Reasoned) | "Because heatmaps show users miss the CTA, a higher-contrast button will increase clicks" | Has reasoning + prediction but no quantification |
| 4 (Quantified) | "Because heatmaps show 60% of users never scroll to the CTA, moving it above the fold will increase click-through rate by 15%+ for new visitors" | Has observation + specific change + quantified prediction + audience + metric |
| 5 (Falsifiable) | Level 4 + "We'll measure over 14 days with 5K visitors per variant. If CTR increase is <10%, we'll reject the hypothesis" | Adds pre-committed sample size, duration, and rejection criteria |

**Always aim for Level 4+.** Level 1-2 hypotheses produce tests that can't fail -- every result gets interpreted as "interesting," which means you learn nothing.

### Hypothesis Template

```
OBSERVE: [specific data point or user behavior]
BELIEVE: [specific change] will cause [metric] to [increase/decrease] by [X%]
FOR: [audience segment]
MEASURE: [primary metric] over [duration] with [sample size] per variant
REJECT IF: [metric change] < [minimum threshold]
```

---

## Sample Size Reality Check

The standard formula (Evan Miller calculator, etc.) assumes conditions that rarely hold:

| Assumption | Reality | Impact |
|---|---|---|
| Fixed sample size, single analysis | Most teams peek at results | Inflates false positive rate from 5% to 20-30%. Use sequential testing or commit to NO peeking |
| Single primary metric | Teams track 5-10 metrics | Multiple comparisons: 5 metrics at 95% confidence = 23% chance of at least one false positive. Apply Bonferroni correction or pre-commit to ONE primary metric |
| Equal variance across segments | Mobile/desktop, new/returning have different baselines | Segment-level effects can be real but opposite in direction (Simpson's paradox). Pre-stratify or analyze segments independently |
| Stable baseline during test | Seasonality, promotions, PR events shift baselines | Run tests for full business cycles (minimum 1 week, ideally 2). Don't start tests on Black Friday |
| No interference between variants | Users may switch devices, share URLs, use multiple accounts | Cookie-based assignment leaks. Use user-ID assignment when possible. Accept ~5% contamination as unavoidable |

### Sample Ratio Mismatch (SRM)

The most under-checked test validity issue. If your 50/50 split shows 51.2%/48.8% actual distribution, your test may be broken.

| Split Deviation | With 10K Users | Assessment |
|---|---|---|
| <0.5% | 50.2/49.8 | Normal random variation |
| 0.5-1.5% | 50.5/49.5 to 51.5/48.5 | Check SRM (chi-squared test, p<0.01 = problem) |
| >1.5% | 51.5/48.5+ | Almost certainly SRM. DO NOT trust results. Debug assignment logic |

**Common SRM causes**: bot traffic hitting one variant more, redirects dropping users, ad blockers blocking test JavaScript, CDN caching serving stale variant, broken assignment logic.

---

## Analysis Decision Framework

| Scenario | Action | Common Mistake |
|---|---|---|
| Reached sample size, p<0.05, meaningful effect | **Ship the winner** | Waiting for "more data" after reaching pre-committed sample size. You committed to a methodology -- honor it |
| Reached sample size, p<0.05, tiny effect (1-2%) | **Consider implementation cost** | A 1.5% conversion lift on 10K monthly visitors = 150 more conversions. Worth it if implementation is a CSS change. Not worth it if it's a 2-week refactor |
| Reached sample size, p>0.05 | **Keep control, document learning** | Calling it "inconclusive" and re-running. If you reached your pre-committed sample size and didn't detect an effect, the effect is likely smaller than your MDE. That IS a result |
| Haven't reached sample size, variant looks like it's winning | **Keep running** | Peeking + stopping = false positive inflation. The apparent winner at 40% of sample size reverts ~30% of the time |
| Haven't reached sample size, variant looks harmful | **Check guardrail metrics** | If guardrails are significantly negative (p<0.01), stop the test. This is the ONE exception to "don't stop early" |
| Conflicting segment results | **Report the overall result, note segments** | Cherry-picking the segment where the variant won. Post-hoc segments are hypotheses for the NEXT test, not conclusions |

### The Peeking Problem (Quantified)

| When You Peek and Stop | Actual False Positive Rate (vs stated 5%) |
|---|---|
| After 25% of sample | ~26% |
| After 50% of sample | ~16% |
| After 75% of sample | ~10% |
| At pre-committed sample size only | ~5% (as intended) |

**If you MUST peek**: Use sequential testing (SPRT, always-valid p-values, or mSPRT). These methods control error rates across multiple looks but require 20-30% more sample size.

---

## When NOT to Test

| Situation | Why Skip A/B Testing | Do Instead |
|---|---|---|
| <1K weekly visitors to test page | Will take months to reach significance for any reasonable MDE | Make the change, compare pre/post with caution. Or test on a higher-traffic page first |
| Fixing an obvious bug | You don't A/B test whether to fix broken things | Fix it. Monitor for regression |
| Legal/compliance requirement | No choice in implementation | Implement. Measure impact but don't delay for a test |
| Already 95%+ confident in direction | The "test everything" dogma wastes resources | Ship it. Save testing capacity for genuine uncertainty |
| Effect is binary (works/doesn't) | No spectrum of outcomes to measure | Feature flag with monitoring, not A/B test |

---

## Anti-Patterns

### The Peek-and-Ship
**What happens**: Check results daily, stop test when variant is ahead, declare victory.
**Why it fails**: At 50% of target sample size, apparent winners revert 30% of the time. You're making decisions on noise.
**The rationalization**: "We could see the trend clearly"

### The Frankentest
**What happens**: Change 5 things at once in the variant. "New headline, new image, new CTA, new layout, new social proof."
**Why it fails**: When it wins (or loses), you don't know which change caused it. Zero learning, pure gambling.
**The rationalization**: "We wanted a bold test"

### The Metric Fisher
**What happens**: Test doesn't hit significance on primary metric. Analyst searches secondary metrics until finding one that's significant.
**Why it fails**: With 20 metrics, you'll find ~1 significant result by chance alone. This IS the multiple comparisons problem.
**The rationalization**: "We found an interesting insight"

### The Perpetual Tester
**What happens**: Test runs for 3+ months because "we want more data." Traffic allocation never freed up.
**Why it fails**: External factors accumulate over long tests (seasonality, product changes, audience shifts). Results become meaningless.
**The rationalization**: "We want to be really sure"

### The Segment Slicer
**What happens**: Overall result is flat. Team slices by every available dimension until finding a segment where the variant wins. Ships variant for that segment.
**Why it fails**: Post-hoc segments are hypotheses, not conclusions. With 10 segments, you'll find 1-2 "winners" by chance.
**The rationalization**: "It works for mobile users from California on Tuesdays"

### The Underpowered Optimist
**What happens**: Test designed to detect 20% lift with 80% power. Actual effect is 3%. Test runs to completion, variant shows +3% (p=0.4). Team calls it "directionally positive" and ships.
**Why it fails**: A non-significant result is NOT evidence of a small positive effect. It's evidence that the effect (if any) is smaller than your MDE.
**The rationalization**: "The data suggests a trend"

### Rationalizations That Signal Bad Testing

1. "Let's just run it and see what happens" (no hypothesis)
2. "We don't have enough traffic for proper testing, but let's try" (underpowered by design)
3. "The variant is clearly winning, we can stop early" (peeking)
4. "It's not significant overall but it works for [segment]" (fishing)
5. "We should test this because everyone else does" (cargo cult)

### Red Flags

1. Test has no pre-committed sample size or duration
2. Primary metric changes mid-test
3. Multiple variants added after test starts
4. Test runs more than 2x the planned duration
5. Results reported without confidence intervals
6. "Significant" result based on fewer than 500 conversions
7. SRM check never performed

### NEVER

1. Never stop a test early because the variant is winning (unless guardrails are violated)
2. Never change variant implementation during a live test
3. Never report secondary metric significance without multiple comparison correction
4. Never run a test you couldn't act on regardless of outcome
5. Never use A/B test results from one audience to justify changes for a different audience
