# Spend Estimation and Budget Inference

Load when the user wants to estimate competitor ad budgets, model spend from available signals, understand seasonal ad spending patterns, or detect multi-platform budget overlap. Do NOT load for basic ad extraction or messaging analysis (use SKILL.md or competitive-intelligence-frameworks.md).

## Impression-Based Spend Modeling

When spend data isn't directly available (everything except Facebook EU), estimate from observable signals.

### The CPM-Based Estimate

| Step | Method | Precision |
|---|---|---|
| 1. Estimate impressions | Ad libraries don't show impressions. Use social engagement as a proxy: if the boosted post is visible on the page, engagement (likes/comments/shares) * 100-500 = rough impression estimate. | Very low precision (order of magnitude only) |
| 2. Apply industry CPM | LinkedIn B2B: $30-$80 CPM. Facebook B2B: $15-$35 CPM. Facebook B2C: $8-$20 CPM. Google Display: $5-$15 CPM. Google Search: $20-$80 CPC (not CPM). TikTok: $10-$25 CPM. | Medium precision for range estimation |
| 3. Calculate | Estimated impressions * CPM / 1000 = Estimated spend per ad | Order-of-magnitude estimate |

**Reality check**: This method produces estimates with 2-5x error bars. Present as ranges ("$5K-$25K/month"), never as precise numbers. The value is relative comparison between competitors, not absolute spend figures.

### The Volume-Duration Method (More Reliable)

| Step | Method |
|---|---|
| 1. Count active ads | Total active ads across all platforms for the competitor |
| 2. Estimate minimum daily spend per ad | Platform minimums: Facebook $1/day, LinkedIn $10/day, Google $10/day. Real B2B campaigns rarely run below $25-50/day per ad. |
| 3. Calculate range | Low estimate: active_ads * $25/day * 30. High estimate: active_ads * $200/day * 30. |
| 4. Adjust for company stage | Seed: closer to low estimate. Series B+: closer to high estimate. Public company: potentially above high estimate. |

**Example**: Competitor has 15 active Facebook ads and 8 active LinkedIn ads.
- Low: 23 ads * $25/day * 30 = $17,250/month
- High: 23 ads * $200/day * 30 = $138,000/month
- If they're Series B SaaS: estimate $40K-$80K/month (middle of range, adjusted for stage)

### Facebook EU Spend Range Interpretation

| Reported Range | Midpoint | If Running 30 Days | If Running 7 Days |
|---|---|---|---|
| <$100 | $50 | $1.67/day (test or low priority) | $7.14/day (small test) |
| $100-$499 | $300 | $10/day (small campaign) | $43/day (moderate for short burst) |
| $500-$999 | $750 | $25/day (moderate) | $107/day (significant for short burst) |
| $1,000-$4,999 | $3,000 | $100/day (meaningful investment) | $429/day (aggressive push) |
| $5,000-$9,999 | $7,500 | $250/day (large campaign) | $1,071/day (major launch spend) |
| $10,000-$49,999 | $30,000 | $1,000/day (enterprise level) | $4,286/day (blitz campaign) |
| $50,000-$99,999 | $75,000 | $2,500/day (major brand investment) | $10,714/day (launch-level spend) |
| $100,000+ | $150,000+ | $5,000+/day (top-tier advertiser) | N/A (this range implies sustained investment) |

**The "per ad" trap**: These ranges are PER AD, not per campaign or per account. A competitor with 20 ads each showing "$1K-$5K" could have a total Facebook EU spend of $20K-$100K. Sum the midpoints across all ads for total estimated platform spend.

## Seasonal Adjustment

Ad spending is NOT uniform throughout the year. Adjust estimates for seasonality.

### B2B SaaS Seasonal Patterns

| Period | Spend Modifier | Why |
|---|---|---|
| January | 0.7x (low) | Budget resets, Q1 planning, slow start. Many companies don't ramp spending until late Jan. |
| February-March | 1.0x (baseline) | Steady state. Q1 campaigns in full swing. |
| April-May | 1.1x (slightly elevated) | Pre-Q2-end push, conference season spending, event-driven campaigns. |
| June | 0.8x (dip) | Q2 close, teams focused on hitting pipeline targets, less experimentation. |
| July-August | 0.7x (summer low) | Decision-maker vacations. Reduced engagement rates make spending less efficient. Some companies pause. |
| September-October | 1.3x (elevated) | Q4 budget capture begins. "Use it or lose it" mentality. Conference season peaks. |
| November | 1.5x (peak for B2B) | Black Friday/Cyber Monday for B2C spills into B2B deals. End-of-year budget push. |
| December | 0.5x (lowest) | Holiday slowdown. Offices closed. Spending deferred to January. |

### B2C Seasonal Patterns

| Period | Spend Modifier | Why |
|---|---|---|
| Q1 (Jan-Mar) | 0.8x | Post-holiday hangover. Consumer spending reduced. CPMs drop (opportunity for efficient spend). |
| Q2 (Apr-Jun) | 1.0x | Baseline. Moderate and steady. |
| Q3 (Jul-Sep) | 1.1x | Back-to-school, early fall campaigns, holiday pre-planning begins. |
| Q4 (Oct-Dec) | 1.8-2.5x | Holiday shopping. CPMs spike 40-80%. Black Friday/Cyber Monday alone can equal Q1-Q2 combined spend for some brands. |

**Seasonal comparison trap**: If you analyze a competitor's ads in November and compare to your own ads in July, you're comparing peak spend to summer low. Always normalize for seasonality when making cross-time comparisons.

## Multi-Platform Budget Distribution Inference

If a competitor runs ads across multiple platforms, estimate how they split budget:

### Distribution Signals

| Signal | Likely Distribution |
|---|---|
| 80%+ of ads on one platform | Concentrated strategy. 60-80% of budget likely on that platform. |
| Even split across 3+ platforms | Diversified. Likely allocating 25-35% per platform with the rest in experiments. |
| Predominantly video ads | Higher budget skew to Facebook/Instagram/TikTok/YouTube (video-native platforms). Less on Google Search/LinkedIn. |
| Heavy LinkedIn presence with B2B product | LinkedIn likely takes 30-50% of budget (premium CPMs but precise B2B targeting). |
| Google Search + branded terms visible | 5-15% of budget allocated to brand protection (defensive spend, not growth). |
| New platform entries (e.g., first TikTok ads appear) | Testing phase: 5-10% of budget. If ads persist 60+ days, budget likely increasing. |

### Budget Inference from Hiring

| Hiring Signal | Budget Implication |
|---|---|
| "Paid Media Manager" job posting | Budget likely $50K+/month (below this, agencies handle it). The role justifies the salary only at this scale. |
| "Director of Growth" or "VP Growth" | Budget likely $200K+/month. Leadership hire implies significant existing or planned spend. |
| "Performance Marketing Analyst" | Budget likely $100K+/month. Analyst role means enough data volume to warrant dedicated analysis. |
| "Creative Strategist" or "Motion Designer" for ads | Investing in in-house creative production. Budget shift from static to video. Expect higher creative velocity. |
| Agency listed as partner (visible in case studies or LinkedIn) | Agency management typically starts at $10K+/month retainer. Total spend likely 5-10x the agency fee. |

## Confidence Calibration

Always communicate estimate confidence to the user:

| Estimation Method | Confidence Level | Error Range | Use Case |
|---|---|---|---|
| Facebook EU spend ranges (direct data) | High | +/- 30% (due to range bucketing) | Actual competitive spend analysis |
| Volume-duration method | Medium | +/- 2-3x | Relative comparison between competitors |
| CPM-based impression modeling | Low | +/- 5-10x | Order-of-magnitude sense only |
| Hiring signal inference | Directional only | Cannot quantify | Understanding whether they're investing or not |
| Seasonal-adjusted models | Medium (if base estimate is medium+) | Adds +/- 20% to base error | Comparing across time periods |

**The honesty rule**: If the user asks "How much is Competitor X spending on ads?" and the only data available is volume-based, say: "Based on their active ad volume, I estimate $30K-$120K/month, but this is a 2-3x error range. For more precise estimates, we would need Facebook EU spend data (if they target EU) or third-party intelligence tools like Pathmatics or SpyFu." Never present a range as precise when it isn't.
