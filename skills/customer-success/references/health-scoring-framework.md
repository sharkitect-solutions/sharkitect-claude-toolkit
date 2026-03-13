# Health Scoring Framework - Deep Reference

## Dimension Metrics Specification

### Product Usage Metrics (Weight: 30%)

| Metric | Green Threshold | Yellow Threshold | Red Threshold | Data Source |
|---|---|---|---|---|
| DAU/MAU ratio | >25% | 10-25% | <10% | Product analytics |
| Feature adoption depth | >60% of tier features used | 30-60% | <30% | Feature tracking |
| Login frequency trend (30d) | Stable or increasing | 5-20% decline | >20% decline | Auth logs |
| Time-in-app (weekly avg) | >80% of cohort median | 50-80% of cohort | <50% of cohort | Session analytics |
| Core workflow completion rate | >70% sessions complete workflow | 40-70% | <40% | Funnel analytics |

Calculate the dimension score by averaging the metric scores. Each metric maps to its threshold band: Green = 80-100, Yellow = 50-79, Red = 0-49. Use the midpoint of the band for metrics that fall clearly within a range.

### Support Health Metrics (Weight: 15%)

| Metric | Green Threshold | Yellow Threshold | Red Threshold |
|---|---|---|---|
| Ticket volume trend (30d) | Flat or declining | 10-30% increase | >30% increase |
| CSAT on resolved tickets | >4.2/5.0 | 3.5-4.2 | <3.5 |
| Escalation rate | <5% of tickets | 5-15% | >15% |
| Repeat issue rate | <10% | 10-25% | >25% |
| Time to resolution satisfaction | <24 hours | 24-72 hours | >72 hours |

Rising ticket volume alone is not Red. Context matters: a customer onboarding complex features will generate more tickets. Check the ticket sentiment trend alongside volume.

### Financial Health Metrics (Weight: 20%)

| Metric | Green Threshold | Yellow Threshold | Red Threshold |
|---|---|---|---|
| Payment timeliness | Within terms | 1-15 days late | >15 days late |
| Contract value trend | Stable or growing | Flat (no expansion in 18mo) | Downgrade or discount request |
| Expansion history | Expanded in last 12 months | No expansion but stable | Contracted or multiple discounts |
| Discount dependency | 0-10% discount | 10-25% discount | >25% discount |
| Invoice dispute rate | 0 disputes/year | 1 dispute/year | 2+ disputes/year |

Discount dependency is the silent killer. Track the cumulative discount percentage across renewals. Accounts with >25% discount are 4x more likely to churn than full-price accounts because the perceived value never matched the original price.

### Relationship Health Metrics (Weight: 25%)

| Metric | Green Threshold | Yellow Threshold | Red Threshold |
|---|---|---|---|
| Exec sponsor engagement | Monthly+ touchpoint | Quarterly touchpoint | No touchpoint in 6+ months |
| Champion status | Identified, active, responsive | Identified but passive | No champion identified |
| Multi-threading depth | 3+ departments engaged | 2 departments | Single contact only |
| NPS score (most recent) | 9-10 (Promoter) | 7-8 (Passive) | 0-6 (Detractor) |
| Meeting attendance rate | >80% of scheduled | 50-80% | <50% |

Multi-threading depth is the most controllable metric and the highest-leverage intervention. A single-threaded $100K account has the same risk profile as a multi-threaded $30K account. Invest in relationship breadth proportional to ACV.

### Onboarding Health Metrics (Weight: 10%, decays post-Day 180)

| Metric | Green Threshold | Yellow Threshold | Red Threshold |
|---|---|---|---|
| Time-to-first-value | <50% of benchmark | 50-100% of benchmark | >100% of benchmark |
| Milestone completion | >80% on schedule | 50-80% on schedule | <50% on schedule |
| Training adoption | >90% invited attended | 60-90% attended | <60% attended |
| Implementation satisfaction | >4.0/5.0 | 3.0-4.0 | <3.0 |

After Day 180, reduce this dimension's weight by 2 percentage points per quarter until it reaches 0%. Redistribute the freed weight equally to Product Usage and Relationship Health.

## Weighted Composite Calculation

```
composite = (usage_score * 0.30) + (support_score * 0.15) +
            (financial_score * 0.20) + (relationship_score * 0.25) +
            (onboarding_score * onboarding_weight)
```

Apply floor override: `if min(all_dimensions) < 40: composite = min(composite, 59)`

## Score Decay for Missing Data

When a metric has no data update for 30+ days:
1. Mark the metric as "stale" in dashboards (visual indicator)
2. After 30 days: subtract 5 points from that dimension per month of staleness
3. After 90 days of no data: force dimension to Yellow (max 65) regardless of last known value
4. After 180 days of no data: force dimension to Red (max 35)

Rationale: a customer generating no telemetry is either disengaged or churning silently. Both warrant investigation.

## Industry Benchmarks (SaaS B2B)

| Metric | Top Quartile | Median | Bottom Quartile |
|---|---|---|---|
| DAU/MAU ratio | >30% | 15-20% | <10% |
| Logo retention (annual) | >95% | 88-92% | <85% |
| Net revenue retention | >120% | 100-110% | <95% |
| Time-to-first-value | <14 days | 30-45 days | >60 days |
| NPS | >50 | 20-35 | <10 |
| Support CSAT | >4.5 | 4.0-4.3 | <3.8 |

Use these benchmarks to calibrate your Green/Yellow/Red thresholds. If your customer base systematically differs from B2B SaaS norms (e.g., long implementation cycles in enterprise healthcare), adjust thresholds using your own cohort percentiles rather than industry averages.

## Automation Rules by Threshold

| Trigger | Automated Action |
|---|---|
| Any dimension enters Red | Create alert in CS tool, notify assigned CSM and CS Director |
| Composite drops below 60 | Auto-schedule intervention call within 48 hours |
| Usage declines >20% for 14+ days | Send automated re-engagement email sequence |
| Champion marked departed | Flag account for immediate multi-threading review |
| Payment >15 days overdue | Notify CS + Finance jointly, pause expansion conversations |
| NPS detractor response received | Create SEV-3 escalation ticket automatically |
| All dimensions Green for 90+ days | Flag for expansion play and advocacy program invitation |
