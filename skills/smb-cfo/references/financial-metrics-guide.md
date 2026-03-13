# Financial Metrics Guide for SMBs

## Margin Analysis

| Metric | Formula | SaaS | Services | E-commerce |
|--------|---------|------|----------|------------|
| Gross Margin | (Revenue - COGS) / Revenue | 70-85% | 50-70% | 25-45% |
| Operating Margin | Operating Income / Revenue | 15-25% | 10-20% | 5-15% |
| Net Margin | Net Income / Revenue | 10-20% | 8-15% | 3-10% |

**Interpretation:** Gross margin below industry median signals pricing weakness or COGS bloat -- investigate before growth spending. Operating margin declining while gross margin holds means OPEX growing faster than revenue. Net margin negative 6+ months requires restructuring or capital.

---

## SaaS-Specific Metrics

```
MRR = Sum of all active monthly subscription values
ARR = MRR * 12
Net New MRR = New MRR + Expansion MRR - Churned MRR - Contraction MRR
Logo Churn Rate = Customers Lost / Starting Customers
NRR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR
Quick Ratio = (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)
Rule of 40 = Revenue Growth Rate (%) + Profit Margin (%)
```

**Benchmarks:**
- Logo churn: <2% monthly for SMB-serving SaaS, <1% for enterprise
- NRR: >100% means expansion > churn. Best-in-class: 110-130%. Below 90% is a serious problem.
- Quick Ratio: Above 4.0 is healthy. Below 1.0 means the business is shrinking.
- Rule of 40: Above 40 is healthy. Below 20 signals both growth and profitability problems.

---

## Service Business Metrics

```
Utilization Rate = Billable Hours / Available Hours          [Target: 65-80%]
Effective Bill Rate = Total Revenue / Total Billable Hours
Realization Rate = Revenue Collected / (Billable Hrs * Std Rate)  [Target: >85%]
Revenue per Employee = Total Revenue / FTE Count             [$150-250K services, $200-400K consulting]
Project Margin = (Project Revenue - Direct Costs) / Revenue  [Kill below 30% unless strategic]
```

Below 65% utilization indicates overcapacity. Above 80% risks burnout. Realization below 85% signals excessive discounting or scope creep. Track project margin in real time, not after delivery.

---

## E-commerce Metrics

```
AOV = Total Revenue / Number of Orders
Contribution Margin per Order = AOV - COGS - Shipping - Processing - Returns
ROAS = Revenue from Ads / Ad Spend
Break-even ROAS = 1 / Contribution Margin %
Inventory Turnover = COGS / Average Inventory                [Target: 4-8x annually]
Days Inventory Outstanding = 365 / Inventory Turnover
```

**Example:** 35% contribution margin means break-even ROAS = 1/0.35 = 2.86x. Any ROAS below 2.86 loses money on first-order basis.

---

## Unit Economics (Cross-Industry)

### Customer Acquisition Cost
```
CAC = Total Sales & Marketing Spend / New Customers Acquired
```
Segment by channel. Blended CAC of $50 hides organic at $10 and paid at $120. Scaling paid without knowing channel CAC triggers "The Growth-at-All-Costs Fallacy."

### Lifetime Value
```
Simple LTV = ARPU * Gross Margin % * (1 / Monthly Churn Rate)
Discounted LTV = Sum of (Monthly Gross Profit * Discount Factor) over lifetime
```
Use simple LTV for internal benchmarking. Use discounted LTV (10-15% annual discount rate) for investment decisions. Undiscounted LTV overstates present value.

### LTV:CAC Benchmarks

| Ratio | Meaning | Action |
|-------|---------|--------|
| Below 1:1 | Losing money per customer | Stop acquisition. Fix product/pricing/retention. |
| 1:1 to 2:1 | Marginal, no room for error | Improve retention or reduce CAC before scaling. |
| 3:1 | Healthy baseline | Scale channels with proven 3:1+ ratios. |
| 5:1+ | Strong economics | Increase spend on channels maintaining this ratio. |
| Above 10:1 | Under-investing in growth | Test higher spend; leaving growth on the table. |

### CAC Payback Period
```
Payback (months) = CAC / (Monthly ARPU * Gross Margin %)
```
**Target:** Under 12 months for SMBs. Under 18 for enterprise SaaS with high NRR. Above 24 is dangerous -- funding acquisition 2 years before returns.

---

## Efficiency Ratios

```
Burn Multiple = Net Burn / Net New ARR
```
Below 1.5x excellent. 1.5-2.5x good. Above 3x inefficient. Above 5x unsustainable.

```
Revenue per Employee = Annual Revenue / Average FTE Count
```
$100-200K early-stage. $200-400K growth. $400K+ efficient at scale. Declining while hiring means team scaling faster than output.

---

## Financial Health Scorecard

Assess quarterly. 7+ green = strong. 3+ red = immediate attention. Any red for 3+ months warrants dedicated plan.

| Metric | Red | Yellow | Green |
|--------|-----|--------|-------|
| Gross Margin | <30% | 30-50% | >50% |
| Operating Margin | <0% | 0-10% | >10% |
| Runway (months) | <6 | 6-12 | >12 |
| LTV:CAC | <2:1 | 2-3:1 | >3:1 |
| CAC Payback | >18mo | 12-18mo | <12mo |
| NRR (SaaS) | <90% | 90-100% | >100% |
| Working Capital Ratio | <1.0 | 1.0-1.5 | >1.5 |
| Revenue Growth YoY | <0% | 0-20% | >20% |
| Customer Concentration | >25% single | 15-25% | <15% |
| DSO (days) | >60 | 45-60 | <45 |
