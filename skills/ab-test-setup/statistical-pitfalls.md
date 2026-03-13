# Statistical Pitfalls in A/B Testing

## Sample Ratio Mismatch (SRM) Deep Dive

SRM is the most common and most under-diagnosed test validity problem. If your assignment ratio doesn't match your observation ratio, ALL test results are suspect.

### Detection Method

| Step | How | Threshold |
|---|---|---|
| 1. Expected ratio | Your configured split (e.g., 50/50 = 0.5 expected per variant) | N/A |
| 2. Observed ratio | Actual visitors per variant at analysis time | N/A |
| 3. Chi-squared test | Compare expected vs observed counts | p < 0.01 = SRM present. Conservative threshold because SRM consequences are severe |
| 4. If SRM detected | DO NOT analyze results. Debug assignment first | No threshold -- results are invalid |

### Common SRM Causes and Fixes

| Cause | How to Detect | Fix |
|---|---|---|
| **Bot traffic** | Bots may not execute JavaScript (client-side assignment), skewing toward server-side variant | Filter bots before analysis. Compare assignment counts to analytics counts |
| **Redirect latency** | Split URL tests: one URL loads slower, users bail before tracking fires | Ensure tracking fires BEFORE redirect. Use server-side assignment instead |
| **Browser extensions / ad blockers** | Block A/B testing scripts entirely. Users fall to control (or disappear) | Use server-side testing for important experiments. Check if blocking rate differs by variant |
| **CDN caching** | Edge cache serves stale variant. New users get cached version instead of fresh assignment | Set no-cache headers on assignment endpoint. Verify CDN config with multiple test requests |
| **Sticky assignment failure** | Cookie-based assignment + cookie deletion = user re-randomized. If variants have different bounce rates, surviving population skews | Use user-ID assignment. Log assignment at point of randomization, not at page view |
| **Variant-specific errors** | JavaScript error in variant B crashes page for 5% of users. They never fire the tracking event | Monitor JavaScript errors per variant. QA all variants before launch, including edge cases |

### SRM Investigation Checklist

1. Check total visitors per variant (raw assignment counts, not analytics)
2. Compare assignment timestamp distribution (should be uniform across time)
3. Check device/browser distribution per variant (should be identical)
4. Check geographic distribution per variant
5. Check for duplicate user IDs in assignment logs
6. Verify assignment logic in code (hash function, randomization seed)

---

## Multiple Comparisons Problem

### The Math

| Metrics Tested | P(at least one false positive) at alpha=0.05 | P(at least one false positive) at alpha=0.01 |
|---|---|---|
| 1 | 5.0% | 1.0% |
| 2 | 9.8% | 2.0% |
| 5 | 22.6% | 4.9% |
| 10 | 40.1% | 9.6% |
| 20 | 64.2% | 18.2% |

### Correction Methods

| Method | How It Works | When to Use | Trade-off |
|---|---|---|---|
| **Pre-commit to 1 primary** | Only one metric determines the test outcome. Others are exploratory | DEFAULT. Most A/B tests should have exactly one primary metric | No statistical adjustment needed. Secondary metrics are for learning, not decisions |
| **Bonferroni correction** | Divide alpha by number of tests. 5 metrics at 0.05 -> each tested at 0.01 | When you truly need multiple primary metrics (rare) | Very conservative. High false negative rate. A true 5% lift may not pass |
| **Holm-Bonferroni** | Step-down version: order p-values, apply progressively less strict thresholds | Preferred over Bonferroni when multiple comparisons are unavoidable | Less conservative than Bonferroni, still controls family-wise error rate |
| **False Discovery Rate (FDR/BH)** | Controls the expected proportion of false discoveries, not the probability of any | Large-scale testing (100+ variants, feature flags across many metrics) | More permissive. Accepts some false positives in exchange for higher power |

**Practical rule**: If you have 1 primary metric and 3-5 secondary metrics, don't correct -- just be explicit that secondaries are hypothesis-generating, not conclusive. Only correct when you have multiple metrics that EACH independently drive a decision.

---

## Bayesian vs Frequentist A/B Testing

### Practical Differences (Not Theoretical)

| Aspect | Frequentist | Bayesian |
|---|---|---|
| **Question answered** | "What's the probability of seeing this data if there's no real difference?" (p-value) | "What's the probability that B is better than A, given the data?" (posterior) |
| **Peeking** | FORBIDDEN without correction. Each peek inflates error rate | SAFE. Bayesian analysis is valid at any sample size. But small samples = wide posterior = useless answer |
| **Sample size** | Must pre-commit. Test invalid if you stop early | No fixed requirement. But stopping at small N gives wide credible intervals with no decision value |
| **Result interpretation** | "Variant B's conversion rate is 12.3% +/- 0.8% (95% CI). p=0.03. Significant at alpha=0.05" | "94% probability that B is better than A. Expected lift: 12.3% with 95% credible interval [3.1%, 22.8%]" |
| **When to use** | Team has statistical discipline. Can pre-commit to sample size. Single decision point | Team will peek. Want probability of being better. Continuous monitoring. Business wants "% chance of winning" |

### Bayesian Gotchas

| Gotcha | What Goes Wrong | How to Avoid |
|---|---|---|
| **Prior sensitivity** | Informative prior + small sample = prior dominates. Your "belief" overwhelms the data | Use weakly informative priors (e.g., Beta(1,1) = uniform) unless you have strong historical data. Always report prior sensitivity analysis |
| **"Probability of winning" isn't magnitude** | 99% probability B is better, but the expected lift is 0.1%. Statistically confident, practically meaningless | Always report expected effect size AND probability. Decision = probability * magnitude |
| **Loss function ignored** | Bayesian framework supports decision theory (expected loss), but most tools only show "probability of winning" | Define your loss function: what's the cost of choosing the wrong variant? Factor in implementation cost |
| **Stopping too early** | Bayesian says you CAN peek, but at n=50, your 95% credible interval might be [-5%, +25%]. Technically valid, practically useless | Set a minimum sample size for practical precision, even in Bayesian framework. "Valid at any N" != "useful at any N" |

---

## Sequential Testing

For teams that NEED to monitor results continuously (can't commit to fixed sample size and single analysis).

### Methods

| Method | How It Works | Overhead vs Fixed-Sample | Best For |
|---|---|---|---|
| **SPRT (Sequential Probability Ratio Test)** | Pre-define two hypotheses (H0: no effect, H1: minimum effect). At each observation, calculate likelihood ratio. Stop when ratio crosses upper or lower boundary | 20-30% more observations on average vs fixed-sample for same power | Binary outcomes (convert/don't). Real-time stopping |
| **Always-valid p-values (mSPRT)** | Modified SPRT that produces p-values valid at any stopping time. Can compute confidence intervals at any point | 30-40% more observations. Wider confidence intervals at early looks | When you want frequentist guarantees with continuous monitoring |
| **Group sequential** | Pre-planned interim analyses (e.g., at 25%, 50%, 75%, 100% of max sample). Alpha spending function allocates error across looks | 5-15% more observations. Simpler than continuous monitoring | Structured review cadence (weekly check-ins) |

### Sequential Testing Gotchas

| Gotcha | Impact | Mitigation |
|---|---|---|
| **Higher sample size requirement** | Sequential methods need 20-40% more data than fixed-sample to achieve same power | Factor this into your timeline. If you barely have enough traffic for fixed-sample, sequential makes it worse |
| **Wider confidence intervals** | The price of continuous monitoring is wider intervals at each look | Accept this trade-off. You're paying for flexibility with precision |
| **Implementation complexity** | Most A/B testing tools don't natively support proper sequential methods. PostHog and Eppo do. Optimizely and VWO do not (as of 2025) | If your tool doesn't support it, don't DIY. Use fixed-sample with group sequential (planned check-ins) |
| **Mixing methods** | Starting with sequential, then switching to fixed-sample analysis (or vice versa) invalidates both | Choose one method before the test starts. Commit to it |

---

## When Sample Size Calculators Lie

Standard calculators (Evan Miller, Optimizely) assume conditions that may not hold:

| Assumption | When It Breaks | What Happens | What to Do |
|---|---|---|---|
| **IID observations** | Users visit multiple times. Each visit is NOT independent | Effective sample size is smaller than visitor count. Test appears to have more power than it does | Use unique users, not sessions, as your unit. If 30% of users visit 3+ times, your effective N is ~70% of visitor count |
| **Fixed baseline** | Conversion rate varies by day of week, season, marketing campaigns | Variance is higher than calculator assumes. Need more data to detect same effect | Run for full weeks (not partial). Add 20-30% to calculated sample size for high-variance metrics |
| **Normal approximation** | Very low conversion rates (<1%) or very small samples (<100/variant) | Normal approximation to binomial breaks down. P-values are unreliable | Use exact tests (Fisher's exact) for small samples. For low rates, use Poisson approximation or simply collect more data |
| **No novelty/primacy effects** | New design is exciting/confusing initially, then effect fades | Early results show large effect that shrinks over time. Stopping at significance captures the inflated effect | Always run for at least 2 full business cycles. Compare week 1 vs week 2 effect sizes |
| **Consistent traffic quality** | Paid campaign starts mid-test, bringing different audience | Traffic mix shifts, changing baseline rate and segment composition | Lock traffic sources before test starts. Or stratify analysis by traffic source |
