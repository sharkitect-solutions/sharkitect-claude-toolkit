# Cash Flow Models for SMBs

## 13-Week Cash Flow Forecast

The 13-week forecast is the primary cash management tool. Rolling basis -- each week, drop the oldest week and add week 13 for perpetual 3-month visibility.

### Template Structure
```
Week:                    W1      W2      W3   ...  W13     Total
BEGINNING CASH           XX
OPERATING INFLOWS
  Customer collections   XX      XX      XX        XX
  Other receipts         XX      XX      XX        XX
TOTAL INFLOWS            XX      XX      XX        XX
OPERATING OUTFLOWS
  Payroll                XX      XX      XX        XX
  Rent/lease             XX      XX      XX        XX
  Vendor payments        XX      XX      XX        XX
  SaaS/subscriptions     XX      XX      XX        XX
  Marketing spend        XX      XX      XX        XX
  Other operating        XX      XX      XX        XX
TOTAL OUTFLOWS           XX      XX      XX        XX
NET OPERATING FLOW       XX      XX      XX        XX
NON-OPERATING
  Loan payments          XX      XX      XX        XX
  Tax payments           XX      XX      XX        XX
  Capital expenditures   XX      XX      XX        XX
  Owner distributions    XX      XX      XX        XX
NET CASH FLOW            XX      XX      XX        XX
ENDING CASH              XX      XX      XX        XX
MINIMUM CASH TARGET      XX      XX      XX        XX
SURPLUS / (SHORTFALL)    XX      XX      XX        XX
```

### Population Rules
- **Customer collections:** Base on AR aging + historical payment patterns, not invoiced revenue. A $50K invoice from a net-60 customer appears when payment is expected.
- **Payroll:** Fixed and predictable. Use exact payroll dates (biweekly or semi-monthly).
- **Vendor payments:** Use actual due dates from AP aging, not when the expense was incurred.
- **Tax payments:** Enter quarterly estimated payments on exact due dates.
- **Minimum cash target:** Set at 4-6 weeks of operating expenses. Below this threshold requires immediate action.

---

## Direct vs Indirect Cash Flow Method

| Aspect | Direct Method | Indirect Method |
|--------|--------------|-----------------|
| Starting point | Actual cash receipts/payments | Net income |
| Best for | Weekly/monthly operational forecasting | GAAP reporting, investor presentations |
| Data source | Bank transactions, AR/AP | Income statement + balance sheet changes |
| SMB recommendation | Use for 13-week forecast | Use for monthly/quarterly reporting |

### Indirect Method Structure
```
Net Income
+ Depreciation & Amortization (non-cash)
- Increase in AR (cash tied up in uncollected revenue)
+ Increase in AP (cash conserved by paying later)
- Increase in Inventory (cash invested in unsold goods)
+ Increase in Deferred Revenue (cash received before earning)
= Cash from Operations
- Capital Expenditures + Asset Sales = Cash from Investing
+ Debt Proceeds - Debt Repayments - Distributions + Equity Raises = Cash from Financing
Net Change in Cash = Operations + Investing + Financing
```

---

## Cash Flow Waterfall Patterns

**Healthy:** Operating (+) > Investing (-) + Financing (-). Business funds itself.
**Growth:** Operating (+), Investing (-), Financing (+). Raising capital to accelerate proven ROI investments.
**Warning:** Operating (-), Financing (+). Relies on external funding to survive.
**Danger:** Operating (-), Investing (-), Financing (-). Burning reserves with no inflow. Immediate intervention.

---

## Runway Calculation

### Basic Formula
```
Runway (months) = Current Cash Balance / Average Monthly Net Burn
Net Burn = Total Monthly Expenses - Total Monthly Revenue
```

### Refined Formula (Accounts for Burn Acceleration)
```
Runway = (-b + sqrt(b^2 + 2*a*C)) / a
Where: C = current cash, b = current monthly net burn, a = monthly burn increase
```
If burn rate is stable (a=0), simplifies to basic formula. When burn increases $5K/month, the difference is material.

### Scenario Modeling
Model worst/base/best cases monthly: vary revenue growth (0% / trend / 1.5x), expense growth (+10% / budget / -5%), collection speed (+15 / current / -5 days DSO), and churn (+50% / current / -25%). **Decision rule:** Plan on base case. Set emergency triggers on worst case. If worst-case runway drops below 6 months, activate cost reduction regardless of trajectory.

---

## Cash Conversion Cycle

```
CCC = DIO + DSO - DPO
DIO = (Avg Inventory / COGS) * 365;  DSO = (Avg AR / Revenue) * 365;  DPO = (Avg AP / COGS) * 365
```

**Levers:** Reduce DSO (tighten terms, 2/10 net 30 discounts, automate collections). Reduce DIO (better forecasting, JIT ordering). Increase DPO (longer supplier terms, pay on due date not before). **Benchmarks:** SaaS DSO <45 days. Services <35 days. E-commerce CCC <30 days.

---

## Working Capital Management

```
Working Capital Ratio = Current Assets / Current Liabilities    [Target: 1.5-2.0]
```
**Below 1.0:** Liquidity crisis. **1.0-1.2:** Tight, one surprise creates shortfall. **1.5-2.0:** Healthy. **Above 3.0:** Possibly underdeployed capital.

### Cash Reserve Benchmarks

| Business Stage | Minimum Reserve | Recommended |
|---------------|----------------|-------------|
| Pre-revenue startup | 12+ months burn | 18+ months |
| Early revenue (<$1M ARR) | 6 months OPEX | 9 months |
| Growth ($1-5M ARR) | 4 months OPEX | 6 months |
| Established ($5-20M ARR) | 3 months OPEX | 4 months |
| Profitable + stable | 2 months OPEX | 3 months |

---

## Cash Flow vs P&L Divergence

When net income is positive but cash flow is negative, investigate:

| Cause | P&L Effect | Cash Effect | Fix |
|-------|-----------|-------------|-----|
| AR growing faster than revenue | Revenue recognized | Cash not collected | Tighten collections |
| Inventory buildup | No impact until sold | Cash spent on purchase | Better forecasting |
| Prepaid expenses | Amortized over time | Full outlay upfront | Negotiate monthly billing |
| Debt principal payments | Not on P&L | Real cash outflow | Include in cash forecast |
| Capital expenditures | Depreciated over years | Full outlay at purchase | Plan CAPEX separately |
| Deferred revenue decrease | Revenue from prior cash | No new inflow | Monitor net new bookings |

**Rule:** Never manage from the P&L alone. A profitable company can and does run out of cash. The 13-week forecast is the early warning system.
