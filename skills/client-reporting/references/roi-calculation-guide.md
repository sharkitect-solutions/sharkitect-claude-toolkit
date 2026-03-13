# ROI Calculation Guide for Client Reporting

## ROI Calculation Methodologies

### Simple ROI
```
ROI = (Gain from Investment - Cost of Investment) / Cost of Investment * 100
```
Use for: Single-period projects with clear start and end. Client-friendly, easy to explain. Weakness: ignores timing of returns and risk.

### Time-Adjusted ROI
```
Annualized ROI = ((1 + ROI)^(1/years)) - 1
```
Use for: Comparing engagements of different durations. A 6-month project returning 40% is not equivalent to a 2-year project returning 40%. Annualizing normalizes the comparison.

### Risk-Adjusted ROI
```
Risk-Adjusted ROI = Expected ROI * Probability of Achievement
```
Use for: Forward-looking projections. When presenting projected ROI, discount by confidence level. An 80% likely ROI of 200% should be presented as 160% risk-adjusted. This prevents over-promising and builds credibility when actuals land near projections.

### Payback Period
```
Payback Period = Total Investment / Monthly Net Benefit
```
Use for: Cash-conscious SMB clients. "You will recoup this investment in 4.2 months" is more compelling than "ROI is 187%" for a business owner watching cash flow.

---

## Value Quantification Frameworks

### Time Savings Quantification
```
Annual Value = Hours Saved per Week * 52 * Blended Hourly Rate of Affected Roles
```

Blended hourly rate calculation: Sum (each role's annual compensation / 2,080 hours * number of people in that role) / total people affected. Include benefits and overhead -- use a 1.3x multiplier on base salary for SMBs. A $75K employee costs approximately $97.5K fully loaded, or $46.88/hour.

Do not use the highest-paid person's rate unless they are the primary beneficiary. Auditors will challenge inflated rates immediately.

### Error Reduction Quantification
```
Annual Value = (Old Error Rate - New Error Rate) * Volume * Average Cost per Error
```

Average cost per error must include: direct rework hours, customer impact (refunds, credits, churn), management investigation time, and downstream process disruption. For SMBs, a single order processing error typically costs $50-$200 when all downstream effects are included. A data entry error in financial systems costs $100-$500 to identify and correct.

### Revenue Impact Quantification
```
Annual Value = New Monthly Revenue Attributable * 12
         or = Revenue Increase % * Prior Baseline Revenue * Attribution %
```

Always state the attribution percentage explicitly. "The redesigned checkout flow contributed to a 23% revenue increase. We attribute 60% of this gain to the redesign based on A/B test data, with the remaining 40% attributable to the concurrent promotional campaign." Partial attribution with explanation is infinitely more credible than 100% attribution without.

### Cost Avoidance Quantification
```
Annual Value = Probability of Event * Cost of Event
```

Cost avoidance is real but harder to defend than cost savings. Frame it as risk reduction: "The security audit identified 3 critical vulnerabilities. Based on industry breach data, the expected annual loss from similar vulnerabilities for businesses your size is $180K-$420K. Remediation reduces this exposure by approximately 85%."

Never present cost avoidance as guaranteed savings. The distinction matters to finance teams: cost savings hit the P&L, cost avoidance is probabilistic.

---

## Baseline Establishment Techniques

### Pre-Engagement Baseline

Capture baselines before work begins, not after. Retroactive baselines invite dispute.

**Mandatory baseline data points:**
1. Current metric values (with date range and source system)
2. Historical trend (3-6 months minimum to establish trajectory)
3. Seasonal or cyclical patterns that might explain future changes
4. Other planned initiatives that could affect the same metrics

### Control Period Method

When possible, maintain a control period: measure the metric for 2-4 weeks after engagement starts but before changes are deployed. This isolates natural variance from intervention impact. If the metric was already improving at 5% monthly before your changes, you cannot claim the full 12% improvement post-change.

### Benchmark Comparison

When pre-engagement baselines are unavailable, use industry benchmarks as proxy. Cite the benchmark source explicitly. "Industry average checkout abandonment for e-commerce SMBs is 69.8% (Baymard Institute, 2025). Your current rate of 54.2% outperforms the benchmark by 22%."

---

## Presenting ROI to Different Audiences

### C-Suite / Business Owner
- Lead with business impact in dollars or percentage
- One page maximum, no methodology details
- Compare ROI to alternative uses of the same investment
- Frame as: "For every $1 invested, you received $X.XX in return"

### Team Lead / Department Manager
- Lead with operational improvements (time saved, errors reduced, throughput increased)
- Include methodology summary (2-3 sentences)
- Show before/after with their team's specific metrics
- Frame as: "Your team gained X hours per week, equivalent to Y% capacity increase"

### Procurement / Finance
- Lead with total cost vs total benefit over the engagement period
- Include full methodology with assumptions listed
- Show payback period and annualized ROI
- Provide the raw data for independent verification
- Frame as: "Total investment of $X returned $Y over Z months, payback achieved in month W"

---

## Common ROI Pitfalls

| Pitfall | Why It Happens | How to Avoid |
|---------|---------------|--------------|
| Cherry-picking the peak metric | Natural variance means some periods look exceptional | Use rolling averages (4-week or monthly) instead of single best data point |
| Ignoring the counterfactual | The metric might have improved without intervention | Establish trend baseline; only claim improvement above existing trajectory |
| Double-counting across workstreams | Multiple teams claim the same revenue gain | Define attribution model upfront; sum of all attribution must not exceed 100% |
| Projecting short-term gains forever | A 3-month pilot result is not an annual guarantee | State projection assumptions and confidence intervals; cap projections at observed data period * 2 |
| Comparing gross benefit to net cost | Omitting the client's internal costs (training, adoption, process change) | Include all costs on both sides; total cost of ownership vs total benefit realized |
| Using vanity metrics as proxy for ROI | Pageviews, followers, impressions are not business outcomes | Convert all metrics to business impact: revenue, cost reduction, time saved, risk reduced |
