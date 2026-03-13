# CAC/LTV Unit Economics Deep Dive

Load when calculating customer acquisition costs, building LTV models, evaluating channel profitability, presenting unit economics to leadership or investors, or diagnosing why growth spending isn't translating to profitability.

## CAC: Beyond the Blended Number

### CAC Hierarchy (Always Calculate All Three)

| CAC Type | Formula | What It Tells You | Common Error |
|---|---|---|---|
| **Blended CAC** | Total S&M spend / New customers acquired | Overall acquisition efficiency. What investors ask for first. | Mixing organic and paid customers. A "blended CAC" of $200 might hide $50 organic CAC and $800 paid CAC. |
| **Channel CAC** | Channel spend / Customers from that channel | Which channels are efficient and which are burning money. | Attributing all customers to the last-touch channel. A customer who found you via SEO, was nurtured by email, and converted on a Google ad is not a "Google Ads customer." |
| **Fully-loaded CAC** | (Channel spend + allocated sales cost + tooling + headcount) / Customers from that channel | True cost including human labor. | Excluding sales team cost. If an SDR spends 50% of time on LinkedIn leads, 50% of their comp is LinkedIn's CAC. |

### Paid vs Organic CAC Split

| Metric | Formula | Why It Matters |
|---|---|---|
| Paid CAC | Paid channel spend / Paid-attributed customers | Marginal cost of acquiring one more customer through paid channels. This is your scaling lever. |
| Organic CAC | (Content team cost + SEO tools + community spend) / Organic-attributed customers | Cost of "free" acquisition. It's never free -- content and SEO require headcount and tooling. |
| Paid/Organic ratio | % of new customers from paid vs organic | If >70% from paid, you're vulnerable to CAC inflation. If >70% organic, you're likely under-investing in growth. Target: 40-60% paid for Series A-B stage. |

### CAC by Customer Segment

| Segment | Typical CAC Multiple vs Average | Why | Action |
|---|---|---|---|
| Self-serve (PLG) | 0.3-0.5x | Product-led, low/no sales touch | Protect this channel. Any friction increase (mandatory demo, gating features) inflates CAC dramatically. |
| SMB (sales-assisted) | 1.0-1.5x | Some sales involvement but short cycle | SDR qualification + fast AE close. Over-investing sales time here destroys unit economics. |
| Mid-market | 2.0-3.0x | Longer cycles, multiple stakeholders, RFPs | Acceptable if ACV is 5-10x SMB. If CAC/ACV ratio exceeds 0.5, sales process is too heavy for the deal size. |
| Enterprise | 3.0-8.0x | 6-18 month cycles, legal review, procurement | Only sustainable with ACV >$100k and multi-year contracts. Track pipeline velocity, not just CAC. |

**Segment CAC trap**: Blended CAC masks segment problems. A company with $300 blended CAC might have $100 PLG CAC (healthy) and $2,000 enterprise CAC with $5k ACV (catastrophic -- 40% of first-year revenue spent on acquisition). Always segment.

## LTV Modeling

### LTV Calculation Methods

| Method | Formula | Best For | Limitation |
|---|---|---|---|
| **Simple LTV** | ARPU * Average customer lifespan (months) | Early stage (<100 customers), quick estimation | Assumes flat ARPU and ignores expansion. Useful for napkin math only. |
| **Cohort LTV** | Sum of monthly revenue from a cohort over its lifetime | Companies with 12+ months of data | Requires complete cohort data. Early cohorts may not represent current product/pricing. |
| **Predictive LTV** | ARPU * Gross margin % / Monthly churn rate | Steady-state businesses with stable churn | Assumes constant churn rate, which rarely holds. Early months churn higher than later months. |
| **Expansion-adjusted LTV** | (ARPU + monthly expansion revenue) * Gross margin % / (Churn rate - Net revenue retention offset) | Companies with strong NRR (>110%) | Most accurate but requires granular expansion revenue data per cohort. |

### Net Revenue Retention (NRR) Impact on LTV

NRR is the most underappreciated variable in LTV calculation.

| NRR | What It Means | LTV Impact | Benchmark |
|---|---|---|---|
| 80% | Losing 20% of revenue from existing customers annually | LTV is capped. You're running on a treadmill. | Below average. Product-market fit issue or pricing problem. |
| 100% | Expansion exactly offsets churn | LTV = initial contract value * lifespan. No growth from existing base. | Acceptable for SMB-focused products. |
| 120% | Existing customers grow 20% annually net of churn | LTV compounds significantly. A $10k customer becomes $12k, $14.4k, $17.3k over 3 years. | Good for mid-market SaaS. |
| 140%+ | Expansion dramatically exceeds churn | LTV is 2-3x what simple calculations suggest. Land-and-expand model working. | Best-in-class (Snowflake, Twilio, Datadog). |

**NRR formula**: (Starting MRR + Expansion - Contraction - Churn) / Starting MRR. Measure monthly, report as annualized.

## CAC Payback Period

### Calculation

```
Payback period (months) = CAC / (ARPU * Gross margin %)
```

### Payback Period Benchmarks

| Payback Period | Assessment | Implication |
|---|---|---|
| <6 months | Excellent. Invest aggressively. | Cash-efficient growth. Can fund acquisition from operating cash flow. |
| 6-12 months | Good. Standard for healthy SaaS. | Sustainable with adequate cash reserves. Default target for Series A-B. |
| 12-18 months | Concerning. Monitor closely. | Requires significant cash runway or external funding to sustain growth. Investigate which segments are dragging. |
| 18-24 months | Problematic. Fix before scaling. | Either CAC is too high (acquisition problem) or ARPU is too low (pricing/packaging problem). Do not scale spend until payback improves. |
| >24 months | Red flag. Stop scaling immediately. | Unit economics are broken. Every new customer is a 2-year cash drain. Fix fundamentals: pricing, ICP targeting, sales efficiency, or product-market fit. |

### Payback by Channel (The Real Decision)

| Channel | Monthly Spend | New Customers | Channel CAC | ARPU | Gross Margin | Payback (months) | Verdict |
|---|---|---|---|---|---|---|---|
| Google Search | $30k | 40 | $750 | $200 | 80% | 4.7 | Scale aggressively |
| LinkedIn | $25k | 15 | $1,667 | $500 | 80% | 4.2 | Scale -- high CAC but high ARPU offsets |
| Meta | $20k | 25 | $800 | $100 | 80% | 10.0 | Reduce -- low ARPU makes payback too long |
| SEO (amortized) | $10k | 30 | $333 | $150 | 80% | 2.8 | Protect and invest -- best unit economics |

**The ARPU-weighted trap**: LinkedIn's $1,667 CAC looks terrible next to Google's $750. But LinkedIn attracts $500 ARPU customers (4.2 month payback) while Google attracts $200 ARPU (4.7 months). CAC without ARPU context leads to wrong decisions. Always evaluate CAC in context of the segment it acquires.

## CAC Inflation Diagnosis

When CAC rises, diagnose before reacting.

| Signal | Likely Cause | Fix |
|---|---|---|
| CPM rising, CTR stable | Market competition increasing (more advertisers in your space) | Differentiate creative (competitors converge on similar messaging), try new ad formats, test emerging channels |
| CPM stable, CTR declining | Creative fatigue or audience saturation | Refresh creatives, expand audience, rotate messaging angles |
| CTR stable, conversion rate declining | Landing page or offer problem | A/B test landing page, review offer-to-audience match, check page load speed |
| Conversion rate stable, SQL rate declining | Lead quality degrading -- platform optimization drifting to cheaper clicks | Tighten targeting, implement offline conversion import, review keyword match types |
| All metrics stable, CAC still rising | Channel saturation -- diminishing returns at current spend level | This channel has hit its efficient frontier. Do not increase budget. Add a new channel instead. |

## Investor-Ready Unit Economics Template

| Metric | Current | 6 Months Ago | Target | Status |
|---|---|---|---|---|
| Blended CAC | $ | $ | $ | Improving / Declining / Stable |
| Paid CAC | $ | $ | $ | |
| Organic CAC | $ | $ | $ | |
| LTV (expansion-adjusted) | $ | $ | $ | |
| LTV:CAC ratio | x | x | >3x | |
| CAC payback (months) | N | N | <12 | |
| Paid/organic customer mix | %/% | %/% | 40-60/60-40 | |
| NRR | % | % | >110% | |

**LTV:CAC ratio benchmarks**:
- <1x: Losing money on every customer. Fix immediately.
- 1-3x: Unprofitable or marginally profitable growth. Acceptable only if NRR >120% (LTV will compound).
- 3-5x: Healthy. Standard target for venture-backed SaaS.
- >5x: Either under-investing in growth (leaving money on the table) or ARPU is about to compress. Investigate both.
