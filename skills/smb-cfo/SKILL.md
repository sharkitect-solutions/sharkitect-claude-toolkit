---
name: smb-cfo
description: "Use when analyzing P&L statements, building cash flow forecasts, calculating runway or break-even, creating budgets, running monthly close, categorizing expenses, modeling unit economics, or making financial decisions for small-to-medium businesses. Use when revenue is under $50M and the team lacks a full-time CFO. Do NOT use for investment banking models, personal finance, enterprise treasury management, or public company SEC reporting."
---

# SMB CFO -- Financial Operations for Small & Medium Businesses

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/monthly-close-checklist.md` | Running monthly close, reconciling accounts, building management reports | General P&L questions, forecasting, budgeting |
| `references/cash-flow-models.md` | Building cash flow forecasts, calculating runway, modeling scenarios, managing working capital | Expense categorization, unit economics, margin analysis |
| `references/financial-metrics-guide.md` | Evaluating margins, computing unit economics, benchmarking SaaS/service/e-commerce metrics | Monthly close procedures, cash flow forecasting |

## Scope Boundary

| In Scope | Out of Scope |
|----------|-------------|
| P&L analysis and margin improvement | Investment banking / M&A modeling |
| Cash flow forecasting (13-week, annual) | Personal finance and retirement planning |
| Budget creation and variance analysis | Public company SEC/SOX compliance |
| Runway and break-even calculations | Enterprise treasury and FX hedging |
| Expense categorization (OPEX/CAPEX) | Tax return preparation (refer to CPA) |
| Monthly close process | Audit procedures (refer to external auditor) |
| Unit economics (CAC, LTV, payback) | Insurance underwriting |
| Financial decision frameworks | Cryptocurrency/DeFi accounting |
| Tax planning basics and accruals | Multi-entity consolidation above 5 entities |
| SaaS, service, and e-commerce metrics | Actuarial analysis |

---

## Core Financial Framework

### P&L Structure for SMBs

Build every P&L with this five-tier waterfall. Skipping tiers hides where margin leaks.

```
Revenue (Gross Sales - Returns - Discounts)
- COGS / Cost of Revenue
= Gross Profit              [Target: 50-80% SaaS, 30-50% services, 20-40% e-commerce]
- OPEX (S&M + G&A + R&D)
= Operating Income (EBIT)   [Target: 10-25% for healthy SMBs]
- Interest + Other
= Pre-Tax Income - Tax Provision = Net Income  [Target: 5-15% at scale]
```

Classify every line item. Unclassified expenses create "The Missing Accrual" -- cash-basis thinking that distorts true profitability. Accrual accounting recognizes revenue when earned and expenses when incurred, regardless of cash movement.

### Budget Planning Template

Structure annual budgets top-down from revenue targets, then validate bottom-up from capacity.

**Top-Down:** Set revenue target from trailing growth. Apply target gross margin to derive COGS ceiling. Allocate OPEX: S&M (15-25%), G&A (8-15%), R&D (10-20%). Compute target net income.

**Bottom-Up Validation:** Count capacity (hours, units, seats), multiply by utilization and pricing, compare to top-down target. If gap exceeds 20%, hiring or pricing changes are required.

**Variance Analysis:** Compare actuals to budget monthly. Investigate any line item deviating >10%. Persistent 3-month variances require reforecast -- the original plan is no longer useful.

---

## Expense Categorization Taxonomy

### OPEX vs CAPEX

| Category | OPEX (Expensed Immediately) | CAPEX (Capitalized & Depreciated) |
|----------|----------------------------|-----------------------------------|
| Software | Monthly SaaS subscriptions | Custom-built software (>$5K, >1yr life) |
| Hardware | Repairs, maintenance | Servers, equipment (>$2,500 threshold) |
| Labor | Salaries, contractor fees | Development labor on capitalizable projects |
| Facilities | Rent, utilities, insurance | Leasehold improvements, buildouts |
| Marketing | Ad spend, agency fees, events | Brand assets with multi-year value (rare) |

**Why it matters:** Misclassifying CAPEX as OPEX understates assets. Misclassifying OPEX as CAPEX inflates assets and defers costs -- this is how accounting fraud starts at small companies.

### Fixed vs Variable Cost Map

**Fixed:** Rent, base salaries, insurance, loan payments, core SaaS tools.
**Variable:** COGS, payment processing, shipping, project contractors, platform fees.
**Semi-Variable:** Sales commissions, cloud hosting, support staff (step function), marketing.

High fixed costs amplify both gains and losses as revenue changes -- critical for break-even analysis.

---

## Runway and Break-Even Calculations

### Runway Formula

```
Basic Runway (months) = Cash Balance / Monthly Net Burn Rate
Net Burn Rate = Monthly Expenses - Monthly Revenue

Refined Runway (accounts for burn acceleration):
  Runway = Cash / (Current Burn + (Monthly Burn Increase * Months / 2))
```

**Why the refined formula matters:** "The Runway Delusion" occurs when founders use the basic formula while burn rate is increasing monthly due to hiring or scaling spend. A company with $600K cash and $50K monthly burn calculates 12 months of runway. But if burn increases $5K/month from new hires, actual runway is closer to 9.5 months. The basic formula overstates by 26%.

**Thresholds:** >18 months = invest in growth. 12-18 = plan next raise or profitability. 6-12 = caution, cut discretionary. <6 = crisis, reduce burn immediately.

### Break-Even Analysis

```
Break-Even Units = Fixed Costs / (Price per Unit - Variable Cost per Unit)
Break-Even Revenue = Fixed Costs / Contribution Margin Ratio
Contribution Margin Ratio = (Revenue - Variable Costs) / Revenue
```

For service businesses, replace "units" with billable hours:
```
Break-Even Hours = Fixed Costs / (Bill Rate - Variable Cost per Hour)
```

Run break-even analysis before every major fixed cost increase (new hire, office lease, annual contract). If the increase pushes break-even beyond 80% of current capacity, the decision carries significant risk.

---

## Unit Economics

### Core Metrics

```
CAC (Customer Acquisition Cost) = Total Sales & Marketing Spend / New Customers Acquired
LTV (Lifetime Value) = ARPU * Gross Margin % * Average Customer Lifespan (months)
LTV:CAC Ratio                    [Target: >3:1 for healthy business, >5:1 before scaling aggressively]
CAC Payback Period = CAC / (Monthly ARPU * Gross Margin %)    [Target: <12 months]
```

**Why LTV:CAC below 3:1 is dangerous:** Each customer costs nearly as much to acquire as they generate in gross profit. Growth spending at this ratio burns cash faster than it builds value -- this is "The Growth-at-All-Costs Fallacy" in action. Fix unit economics before scaling spend.

**Why payback period matters more than LTV:CAC for cash-constrained SMBs:** LTV:CAC can look healthy at 4:1, but if payback takes 18 months and you have 10 months of runway, you run out of cash before recouping acquisition costs.

### Blended vs Cohort Analysis

Never rely solely on blended averages. "The Vanity Revenue Trap" hides when recent cohorts perform worse than early ones. Segment unit economics by:
- Acquisition channel (organic vs paid vs referral)
- Customer segment (SMB vs mid-market)
- Time cohort (Q1 vs Q2 vs Q3 customers)
- Geography (if applicable)

If the latest cohort's LTV:CAC is below 2:1 while blended shows 4:1, the business is degrading and blended metrics are masking it.

---

## Financial Decision Framework

### When to Hire
All must be true: (1) utilization >85% for 3+ months, (2) lost revenue from constraints exceeds fully-loaded hire cost, (3) runway remains >12 months after adding position, (4) role has measurable revenue/ops impact within 90 days. Budget fully-loaded cost (salary + taxes + benefits + equipment + overhead) for every headcount decision.

### When to Invest in Growth
All must be true: (1) LTV:CAC >3:1 and payback <12 months on target channel, (2) gross margin >50%, (3) runway remains >15 months post-investment, (4) ROI measurable within one quarter.

### When to Cut Costs
Cut when ANY is true: runway <9 months, gross margin <40% for 2 months, burn >110% budget for 3 months, or a segment shows negative contribution margin. **Priority order:** discretionary marketing > unused software > contractor hours > open headcount > existing headcount (last resort -- rehiring costs 50-200% of annual salary).

---

## Tax Planning Basics

**Quarterly estimates:** SMBs owing $1,000+ federal tax must pay quarterly (Apr 15, Jun 15, Sep 15, Jan 15). Missing payments triggers penalties.

**Accrual timing:** When profitable, accelerate deductible expenses (prepay contracts, buy equipment before Dec 31). Defer revenue when legally permissible (milestone billing, delivery-based recognition).

**Section 179:** Equipment and software under IRS thresholds can be fully expensed in purchase year rather than depreciated. **R&D Credit:** Software development labor often qualifies; SMBs under $5M revenue can apply against payroll taxes -- valuable even pre-profit.

**Entity structure:** S-Corp vs LLC vs C-Corp affects pass-through taxation and self-employment tax. Review annually with CPA when revenue exceeds $100K.

Defer tax return preparation and compliance filing to a licensed CPA. This skill covers planning, not compliance.

---

## Named Anti-Patterns

### The Vanity Revenue Trap
Topline revenue growth masking that COGS and CAC grow faster. Revenue doubles but losses triple. **Detect:** Compare revenue growth rate to gross profit growth rate; check unit economics by cohort. **Fix:** Freeze growth spend. Rebuild unit economics. Resume only when LTV:CAC >3:1 on the most recent cohort.

### The Runway Delusion
Using basic runway formula while burn rate increases monthly. Overestimates remaining time by 20-40%. **Detect:** Plot monthly burn for 6 months; upward trend means basic formula is wrong. **Fix:** Use refined runway formula. Recalculate after every new recurring expense commitment.

### The Missing Accrual
Cash-basis thinking in an accrual-basis system. Revenue recognized before delivery, expenses missed because bills have not arrived. **Detect:** Persistent divergence between cash flow and net income. **Fix:** Monthly close with accrual checklist. Accrue all known liabilities even without invoices.

### The Contractor Mirage
Classifying full-time-equivalent workers as contractors. True cost is 25-35% higher (taxes, benefits, overhead) plus misclassification legal risk. **Detect:** Any contractor at 30+ hours/week for 3+ months. **Fix:** Budget fully-loaded costs for all labor regardless of classification.

### The Growth-at-All-Costs Fallacy
Aggressive acquisition spend before proving unit economics. Assumes scale fixes margins -- it almost never does. **Detect:** Payback >15 months, LTV:CAC <2:1 on paid, rising CAC quarter-over-quarter. **Fix:** Cap growth spend at survivable levels. Prove economics at small scale first.

---

## Rationalization Table

| Temptation | Why It Fails | Do This Instead |
|------------|-------------|-----------------|
| "We'll grow into profitability" | Growth amplifies losses when unit economics are broken. Doubling customers at negative contribution margin doubles the loss. | Fix unit economics first. Prove LTV:CAC > 3:1 at current scale before spending to grow. |
| "Revenue is up, we're fine" | Revenue is vanity. A business can grow revenue 100% and still die if margins compress or cash conversion slows. | Track gross margin trend and cash flow alongside revenue. All three must move together. |
| "We can't afford to do monthly close" | Skipping close means flying blind. Errors compound monthly. By the time you discover the problem, it's a crisis. | Implement a 5-day close cycle. The time investment is 8-12 hours/month. The cost of not knowing is bankruptcy. |
| "Contractors are cheaper than employees" | Only on paper. Missing employer taxes, benefits, equipment, and misclassification risk makes the comparison misleading. | Calculate fully-loaded cost for both options. Include legal risk premium for contractor misclassification. |
| "We'll worry about taxes at year-end" | Year-end tax planning is damage control. Quarterly planning is strategy. Missed estimated payments incur penalties. | Set quarterly tax review cadence. Accrue tax liability monthly. Make estimated payments on schedule. |
| "Our blended metrics look great" | Blended averages hide cohort degradation. If your newest customers are less profitable, the trend line is your future. | Segment all metrics by cohort, channel, and customer type. React to the trend, not the average. |

---

## Red Flags Checklist

Monitor these indicators continuously. Any single flag warrants investigation. Two or more flags simultaneously demand immediate executive attention.

- [ ] **Cash below 6 months runway** -- Survival risk. Activate cost reduction plan immediately.
- [ ] **Gross margin declining 3+ consecutive months** -- Pricing, COGS, or product mix problem. Diagnose before it reaches operating income.
- [ ] **AR aging > 60 days growing** -- Customers are paying slower. Tighten collection process or risk cash crunch even with strong revenue.
- [ ] **Burn rate exceeding budget by >15% for 2+ months** -- Spending is out of control. Freeze discretionary spend and audit every new commitment.
- [ ] **LTV:CAC below 2:1 on newest cohort** -- Acquisition economics are deteriorating. Pause scaling spend on underperforming channels.
- [ ] **Revenue growing but cash declining** -- Classic accrual vs cash disconnect. Investigate working capital: AR growing, AP shrinking, or inventory building.
- [ ] **Single customer > 25% of revenue** -- Concentration risk. Losing that customer could be fatal. Diversify aggressively.
- [ ] **Monthly close taking > 10 business days** -- Financial visibility is too slow. Errors and surprises accumulate. Streamline the close process.
- [ ] **Payroll exceeding 60% of revenue** -- Overweight on labor relative to output. Review utilization, pricing, and headcount plan.
- [ ] **Quarterly tax estimates not being paid** -- IRS penalties accrue. Signals broader financial discipline breakdown.
