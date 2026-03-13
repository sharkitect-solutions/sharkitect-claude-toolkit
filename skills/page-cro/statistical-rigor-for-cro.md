# Statistical Rigor for CRO Testing

Load when the user wants to run an A/B test, asks "is this result significant?", mentions sample size, discusses test duration, reports test results, or wants to compare conversion rates between variants. Also load when the user has been running tests without a framework and needs to formalize their approach. Do NOT load for qualitative page diagnosis or copy recommendations that don't involve testing.

## Sample Size: The Math Most CRO Practitioners Skip

### Minimum Sample Size Formula

For a two-variant test at 95% confidence and 80% power:

```
n = (Z_alpha/2 + Z_beta)^2 * (p1*(1-p1) + p2*(1-p2)) / (p2 - p1)^2
```

Where:
- Z_alpha/2 = 1.96 (for 95% confidence)
- Z_beta = 0.84 (for 80% power)
- p1 = baseline conversion rate
- p2 = minimum detectable effect (MDE) -- the smallest improvement worth detecting

### Quick Reference Table

| Baseline Conversion Rate | MDE (Relative) | Required Sample Per Variant | Total (2 variants) |
|---|---|---|---|
| 1% | 20% (1.0% -> 1.2%) | 130,000 | 260,000 |
| 2% | 15% (2.0% -> 2.3%) | 48,000 | 96,000 |
| 3% | 10% (3.0% -> 3.3%) | 39,000 | 78,000 |
| 5% | 10% (5.0% -> 5.5%) | 22,700 | 45,400 |
| 10% | 10% (10% -> 11%) | 10,500 | 21,000 |
| 10% | 5% (10% -> 10.5%) | 42,000 | 84,000 |
| 20% | 10% (20% -> 22%) | 4,400 | 8,800 |

**The uncomfortable truth**: Most marketing pages converting at 2-3% need 50,000-100,000 visitors PER VARIANT to detect a 10-15% relative improvement. At 1,000 visitors/day, that's 50-100 days per test. Sites running "quick A/B tests" on low-traffic pages are reading noise, not signal.

### Minimum Detectable Effect Selection

| Test Type | Realistic MDE | Why |
|---|---|---|
| Button color, CTA text tweak | 1-3% relative | These changes have tiny real effects. You need enormous samples to detect them. Often not worth testing. |
| Headline rewrite | 5-15% relative | Meaningful messaging change. Detectable with moderate traffic. |
| Complete page redesign | 10-30% relative | Large enough effect that moderate samples work. But confounded -- you won't know WHICH change mattered. |
| New offer / value prop | 15-50% relative | Structural changes produce large effects. Can detect with smaller samples. Worth testing first. |

**Rule**: Start testing the biggest changes first. They require the smallest samples and have the highest expected value. Micro-optimizations (button color, font size) should only be tested on pages with >50,000 monthly visitors.

## When to Call a Test

### The Four-Rule Framework

| Rule | Description | Violation Consequence |
|---|---|---|
| **Pre-commit sample size** | Calculate required sample BEFORE launching. Do not peek. | Peeking inflates false positive rate from 5% to 20-30% (Optimizely 2014 research). Every peek is a separate hypothesis test. |
| **Minimum duration: 2 full business cycles** | Run for at least 2 complete weeks (14 days) regardless of sample size | Day-of-week effects are real: B2B pages convert 30-50% higher Tuesday-Thursday vs weekends. A test that reaches sample size in 5 days captures an unrepresentative mix. |
| **Do not stop early on "significance"** | If your tool shows p<0.05 after 3 days but you planned for 14, keep running | Early significance is often a fluctuation. The probability that an "early winner" reverts to null increases the earlier you stop. |
| **Stop immediately on harm** | If variant is significantly WORSE (p<0.01) with large effect, stop early | Protecting users from a clearly worse experience outweighs statistical purity. Use a one-sided test threshold. |

### The Peeking Problem (Quantified)

| Number of Peeks During Test | Actual False Positive Rate (Nominal 5%) |
|---|---|
| 0 (wait for pre-committed sample) | 5% (as designed) |
| 1 (midpoint check) | 8% |
| 2 (check every third) | 11% |
| 5 (check daily on 5-day test) | 17% |
| 10 (check twice daily) | 22% |
| Continuous monitoring | Up to 30% |

**Solution**: Use sequential testing methods (Bayesian or SPRT) if you MUST monitor continuously. These methods adjust for repeated looks. Google Optimize used sequential testing; Optimizely offers it as "Stats Engine." VWO's SmartStats is Bayesian.

## Bayesian vs Frequentist: Decision Guide

| Factor | Frequentist (p-values) | Bayesian (probability to be best) |
|---|---|---|
| Answer it gives | "If there's no difference, would we see this result?" (p-value) | "What's the probability variant B is better than A?" (direct answer) |
| Requires fixed sample? | YES -- sample size must be committed before starting | NO -- can check anytime without inflation |
| Handles peeking? | NO -- peeking inflates false positive rate | YES -- probability updates continuously and correctly |
| Prior knowledge | Not used | Can incorporate prior test results (informative prior) |
| Easy to misinterpret? | Very. "p<0.05" does NOT mean "95% chance B is better" | Less so. "92% probability B is better" means what it says |
| Best for | High-stakes decisions, regulatory contexts, academic publishing | Ongoing optimization, low-traffic sites, business decisions |
| Tool support | Google Analytics Experiments (deprecated), basic A/B tools | VWO SmartStats, Optimizely Stats Engine, Dynamic Yield |

**Recommendation for CRO practitioners**: Use Bayesian methods. The direct probability statement ("87% chance this variant wins") is what business stakeholders actually need. Frequentist p-values answer a question nobody asked.

## Multiple Comparison Problem

Testing multiple variants or multiple metrics simultaneously inflates false positives.

| Scenario | Variants | Metrics | Effective Tests | False Positive Risk (at nominal 5%) |
|---|---|---|---|---|
| Simple A/B, one metric | 2 | 1 | 1 | 5% |
| A/B, 3 metrics (CVR, bounce, time) | 2 | 3 | 3 | 14% |
| A/B/C, one metric | 3 | 1 | 2 | 10% |
| A/B/C/D, 3 metrics | 4 | 3 | 9 | 37% |

### Corrections

| Method | When to Use | How |
|---|---|---|
| **Bonferroni** | Conservative, few comparisons | Divide alpha by number of tests: 5%/3 = 1.67% per test. Simple but overly conservative |
| **Holm-Bonferroni** | Moderate, still simple | Step-down procedure: order p-values, apply increasingly lenient thresholds. Less conservative than Bonferroni |
| **Designate primary metric** | Most CRO tests | Pre-commit ONE primary metric for the go/no-go decision. Observe secondary metrics but do not use them for significance claims |
| **Hierarchical testing** | Revenue + conversion rate | Test primary metric first. Only test secondary metric if primary is significant. Controls family-wise error |

**The practical rule**: One test, one primary metric, two variants. This is the only configuration where standard statistical tools give reliable answers without corrections. Every deviation adds complexity. If you must test multiple variants, use a tool that handles multiplicity natively (Optimizely, VWO).

## Revenue vs Conversion Rate: Which Metric to Optimize

| Metric | When to Use as Primary | Trap |
|---|---|---|
| Conversion rate | Lead gen, email signup, free trial | A variant that converts 20% more users but attracts lower-quality leads may reduce revenue. Track downstream metrics |
| Revenue per visitor | E-commerce, direct purchase | Averages hide distribution. A variant where 1 whale purchase inflates RPV is not a real winner. Check median AND mean |
| Revenue per session | SaaS with upsells | Better than RPV when sessions vary in length. But attribution becomes complex with multi-session journeys |

**Always track BOTH conversion rate and revenue, even if only one is primary.** A test that lifts conversion rate 15% but drops average order value 20% is a net loss. This happens more often than expected -- discount-based variants and low-friction CTAs both tend to increase volume while decreasing quality.

## Test Duration Calendar Effects

| Effect | Impact on CRO Tests | Mitigation |
|---|---|---|
| **Day of week** | B2B: Tuesday-Thursday convert 30-50% higher. E-commerce: Friday-Sunday higher | Run minimum 2 full weeks. Start tests on Monday |
| **Pay cycle** | Consumer purchase behavior spikes around 1st and 15th of month | Run minimum 1 full month for purchase tests, or start mid-cycle |
| **Seasonality** | Q4 holiday traffic behaves differently from Q1 | Never extrapolate Q4 test results to Q1. Re-test after seasonal shift |
| **Novelty effect** | New designs get attention from returning visitors simply because they're new | First-week results often overestimate lift. Wait for novelty to wear off (typically 7-10 days for sites with repeat visitors) |
| **Marketing campaigns** | A viral post, PR mention, or ad spike changes traffic composition mid-test | Segment results by traffic source. Or pause test during abnormal traffic events |
