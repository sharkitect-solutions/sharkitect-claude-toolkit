# Paywall Pricing Experiments Guide

Load when designing A/B tests for paywalls or analyzing paywall experiment results.

## Experiment Design Fundamentals

### What to Test (Ranked by Typical Impact)

| Element | Expected Lift Range | Sample Size Needed | Risk Level |
|---------|-------------------|-------------------|------------|
| Trigger timing (when paywall appears) | 20-50% | Large (5K+ impressions per variant) | Low -- easily reversible |
| Price point changes | 10-30% on revenue (not just conversion) | Very large (10K+) | Medium -- pricing expectations sticky |
| Plan structure (2 vs 3 plans, feature bundling) | 15-25% | Large (5K+) | Medium -- changes user expectations |
| Copy/messaging on paywall | 5-15% | Medium (2K+) | Low |
| Visual design/layout | 3-10% | Medium (2K+) | Low |
| CTA button text | 2-8% | Small (1K+) | Low |
| Dismiss button style/position | 1-5% (but affects trust metrics) | Medium (2K+) | Low |

### What NOT to A/B Test
- Compliance elements (subscription terms, close button, restore purchases) -- these are requirements, not variables
- Price increases on existing subscribers -- grandfathering is expected
- Loss framing vs gain framing for users with no stored data -- loss framing always loses here, no test needed
- Paywall vs no paywall -- the business decision to monetize is not an experiment

## Statistical Rigor for Paywall Tests

### Sample Size Estimation

For paywall conversion tests, baseline conversion rates are typically 3-15%. The required sample size per variant:

| Baseline Conversion | Minimum Detectable Effect | Required Sample (per variant) | At 80% Power, 95% Confidence |
|--------------------|--------------------------|------------------------------|-------------------------------|
| 3% | 20% relative (3% -> 3.6%) | ~25,000 | 4-6 weeks for most apps |
| 5% | 20% relative (5% -> 6%) | ~14,000 | 2-4 weeks |
| 10% | 15% relative (10% -> 11.5%) | ~10,000 | 1-3 weeks |
| 15% | 10% relative (15% -> 16.5%) | ~14,000 | 2-4 weeks |

### Common Statistical Mistakes in Paywall Tests

| Mistake | Why It Happens | Consequence | Fix |
|---------|---------------|-------------|-----|
| Peeking at results daily | Excitement about early trends | False positives -- effects that disappear with more data | Set sample size target upfront, check only at milestones |
| Using conversion rate as sole metric | Conversion is easiest to measure | Higher conversion to monthly plan can REDUCE revenue vs lower conversion to annual | Use RPPI (Revenue Per Paywall Impression) as primary metric |
| Running test during promotional period | Wanted fast results during high-traffic event | Results don't generalize to normal periods | Run during representative traffic period, exclude anomalous days |
| Not segmenting by trigger type | Treating all paywall views as equivalent | Feature gate users and trial expiry users convert at very different rates -- averaging masks effects | Segment results by trigger type. An effect that works for trial users may hurt feature gate users |
| Ignoring 30-day retention | Measuring conversion at point of purchase only | "Regret purchases" inflate conversion but destroy LTV | Track 30-day retention by variant. Reject variants where retention drops >5pp |
| Testing too many variants | Wanting to test 4+ versions simultaneously | Dilutes sample per variant, extends test duration, increases multiple comparison risk | Maximum 3 variants (control + 2 treatments). Use sequential testing for more ideas |

## Experiment Templates

### Template 1: Trigger Timing Test

**Hypothesis**: Showing the paywall 2-3 seconds after blocked action (with transition animation) converts better than immediate display.

| Variant | Timing | Animation |
|---------|--------|-----------|
| Control | Immediate (<100ms) | None |
| Treatment A | 2 second delay | Fade-in |
| Treatment B | 3 second delay | Slide-up |

**Primary metric**: RPPI
**Secondary metrics**: Dismiss rate, time-to-decision, 30-day retention
**Segment by**: Trigger type (feature gate vs limit reached)
**Run for**: Minimum 14 days, 5K impressions per variant

### Template 2: Price Anchoring Test

**Hypothesis**: Showing annual price with monthly equivalent ("$99/year -- just $8.25/month") outperforms showing monthly price with annual savings ("$12/month -- save 31% annually").

| Variant | Primary Display | Secondary Display |
|---------|----------------|-------------------|
| Control | $12/month | "Save 31% with annual" |
| Treatment | $99/year ($8.25/mo) | "Most popular" badge |

**Primary metric**: Annual plan selection rate, RPPI
**Secondary**: Total conversion rate (any plan)
**Caution**: This test changes perceived price reference point. Run for full 21 days minimum to capture both impulse and deliberate converter peaks.

### Template 3: Social Proof Placement

**Hypothesis**: Showing peer-specific social proof ("Teams your size use Pro for X") outperforms generic social proof ("Join 50,000+ teams").

| Variant | Social Proof Type | Placement |
|---------|------------------|-----------|
| Control | "Join 50,000+ teams on Pro" | Below feature comparison |
| Treatment A | "Teams with [N] members use Pro for [top feature]" | Above CTA button |
| Treatment B | "[Company in similar industry] upgraded last week" | Below pricing, above CTA |

**Primary metric**: RPPI
**Caution**: Treatment B requires dynamic data. If personalization data is wrong (wrong industry, wrong company size), it performs WORSE than generic. Only test if data quality is >90% accurate.

## Cohort Analysis for Upgrade Quality

### Building an Upgrade Quality Dashboard

Track these metrics for every paywall variant, segmented by week of upgrade:

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| 7-day activation (used paid feature) | >80% | 60-80% | <60% -- users aren't using what they paid for |
| 30-day retention | >85% | 70-85% | <70% -- regret purchases |
| 60-day retention | >75% | 60-75% | <60% -- value not sustained |
| Support tickets within 7 days | <5% of upgraders | 5-10% | >10% -- confusion or mismatched expectations |
| Voluntary churn reason: "too expensive" | <20% of churners | 20-40% | >40% -- price-value mismatch |
| Voluntary churn reason: "didn't use enough" | <15% of churners | 15-30% | >30% -- premature upgrade, not enough activation |

### Identifying Regret Purchases

A paywall variant creates regret purchases when:
1. Conversion rate is >15% (unusually high for the trigger type)
2. AND 30-day retention is <70%
3. AND support tickets within 7 days exceed 10% of upgraders

Root causes of regret purchases:
- False urgency ("offer expires in 10 minutes" when it doesn't)
- Feature promises that don't match reality
- Accidental purchases (CTA too close to dismiss, confusing button labels)
- Price confusion (per-seat pricing not clearly communicated)

### Revenue Attribution by Paywall Variant

| Metric | Formula | What It Tells You |
|--------|---------|-------------------|
| RPPI | Revenue from upgrades / Total paywall impressions | Revenue efficiency per impression |
| Revenue per user (RPU) | Total revenue / Total active users (free + paid) | Overall monetization health |
| Upgrade LTV | Average revenue per upgrader over 12 months | Long-term value of the conversion |
| Paywall ROI | (Revenue from variant - Revenue from control) / Engineering cost to implement | Whether the optimization was worth building |

## Sequential Testing Protocol

When you have more ideas than bandwidth to test simultaneously:

1. **Start with highest-impact, lowest-risk** -- trigger timing and copy tests before price changes
2. **Lock winners before testing next** -- implement winning variant as new control before starting next test
3. **Wait 2 weeks between tests** -- user behavior needs time to stabilize after each change (novelty effect)
4. **Document every test** -- hypothesis, variants, sample size, duration, result, decision. Future teams will thank you
5. **Retest winners after 90 days** -- user base composition changes. A winner in Q1 may not win in Q3

## Metric Hierarchy

When metrics conflict (and they will), resolve in this order:

1. **30-day retention of upgraders** -- a variant that hurts retention is rejected regardless of conversion lift
2. **RPPI** -- revenue per impression captures both conversion rate and plan selection quality
3. **Conversion rate** -- useful for diagnostics but NOT the decision metric
4. **Time-to-decision** -- faster decisions correlate with higher satisfaction (less friction)
5. **Dismiss rate** -- high dismiss rate without conversion is a signal, not a failure (user saw and decided)
