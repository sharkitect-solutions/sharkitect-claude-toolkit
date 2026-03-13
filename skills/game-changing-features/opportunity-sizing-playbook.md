# Opportunity Sizing Playbook

Load when quantifying the potential impact of a feature opportunity, building a business case for investment, or comparing multiple feature candidates by expected value.

## Why Sizing Matters

Unsized opportunities default to "gut feel" ranking, which is systematically biased toward the loudest advocate's pet feature. Sizing forces specificity: "This feature could increase activation by 8-15%" is debatable. "This feature could not increase activation" is falsifiable.

## TAM Expansion Sizing

When a feature opens the product to a NEW user segment.

| Step | Method | Example |
|------|--------|---------|
| 1. Define the new segment | Who can't use the product today that could with this feature? | "Non-English speakers" / "Mobile-only users" / "Teams > 50 people" |
| 2. Size the segment | Total potential users in this segment (industry reports, census data, competitor user counts) | "42M Spanish-speaking internet users in the US" |
| 3. Apply adoption funnel | Awareness (5-15%) -> Trial (20-40%) -> Activation (30-60%) -> Paid conversion (2-10%) | 42M * 10% * 30% * 45% * 5% = 28,350 paid users |
| 4. Revenue per user | ARPU * retention period | $20/mo * 14 months avg = $280 LTV |
| 5. Expected revenue | Segment paid users * LTV | 28,350 * $280 = $7.9M |

**TAM sizing traps**:
- Top-down TAM ("The market is $50B, we'll capture 1%") is fantasy. Bottom-up (individual user adoption funnel) is grounded.
- Competitor user counts as proxy: if Competitor X has 500K users in a segment you don't serve, that's a more reliable signal than TAM reports.
- TAM != demand. A large segment doesn't mean they WANT your product. Validate demand signal before sizing revenue.

## Conversion Funnel Impact Sizing

When a feature improves an existing funnel step.

| Metric | How to Size | Ceiling Check |
|--------|-------------|---------------|
| Signup -> Activation rate | Current rate * expected lift % * confidence discount | Industry benchmark caps your ceiling (if industry avg is 40% and you're at 35%, max realistic improvement is ~40%, not 70%) |
| Activation -> Paid conversion | Same formula. Weight by plan value (don't count $0 plans). | Conversion is harder to move than activation. Use 50% confidence discount for untested hypotheses. |
| Free -> Paid upgrade rate | Current rate * expected lift. Size by delta revenue. | Upgrade rate improvements compound monthly. A 2% lift in monthly upgrade rate = 24% more upgrades/year. |

**The "multiply the funnel" mistake**: "If we improve every step by 10%, overall conversion improves by 10%." Wrong. Improvements multiply: 1.1 * 1.1 * 1.1 = 1.33 = 33% overall improvement. This cuts both ways -- small degradations also compound.

## Retention Impact Sizing

When a feature reduces churn.

| Step | Method |
|------|--------|
| 1. Identify churn segment | Which users churn, and why? (Churn reason from exit surveys, support tickets, usage patterns) |
| 2. Size the addressable churn | What % of monthly churners cite this reason? (e.g., "30% churn because of missing collaboration features") |
| 3. Estimate retention lift | Conservative: 25% of addressable churn retained. Moderate: 50%. Aggressive: 75%. |
| 4. Calculate revenue impact | Monthly churn revenue * addressable % * retention estimate * 12 months |

**Retention sizing example**:
- Monthly churn: 500 users * $25 ARPU = $12,500/month lost
- Addressable (30% cite collaboration): $3,750/month
- Conservative retention (25%): $937.50/month saved = $11,250/year
- Moderate retention (50%): $1,875/month saved = $22,500/year

**Retention reality check**: Churn reasons in exit surveys are unreliable. Users give the easiest answer, not the real one. Cross-reference with behavioral data: did churned users actually TRY collaboration features? If they never engaged with the area, "missing collaboration" is not the real reason.

## Build Cost Estimation

| Component | Sizing Method | Common Miss |
|-----------|-------------|-------------|
| Engineering time | Story points or t-shirt sizes from tech lead. Convert to weeks. Multiply by 1.5 (optimism bias). | Integration testing, documentation, monitoring, on-call overhead post-launch |
| Opportunity cost | What ELSE could the team build in this time? Size the foregone feature too. | The real cost of Feature A is Feature A + not-Feature-B |
| Ongoing maintenance | 20-30% of build cost per year for most features | "Ship and forget" is a myth. Every feature is a maintenance commitment. |
| Support cost | New features generate support tickets. Estimate 5-15% of users will need help. | If 10K users adopt the feature and 10% need help, that's 1,000 support tickets. At $15/ticket = $15K. |

**ROI calculation**: `(Annual revenue impact - Annual maintenance cost) / Total build cost`
- ROI > 3x in year 1: Strong investment
- ROI 1-3x in year 1: Moderate, depends on strategic value
- ROI < 1x in year 1: Needs multi-year compounding or strategic justification

## Confidence-Weighted Sizing

Not all estimates deserve equal weight. Adjust for evidence quality.

| Evidence Level | Confidence Multiplier | Example |
|---------------|----------------------|---------|
| Validated prototype with real user data | 0.8x (high confidence, slight discount for scale uncertainty) | "We ran a 2-week beta with 500 users. Activation improved 12%." |
| Behavioral data (analytics showing the gap) | 0.5x | "60% of users attempt X and fail. Removing the failure should convert some." |
| User interviews (qualitative, 10+ interviews) | 0.3x | "8 of 12 interviewees said they would use this feature." |
| User requests (feature request votes) | 0.2x | "200 users voted for this on our feedback board." |
| Team intuition (no external validation) | 0.1x | "We think this would be valuable." |

**Expected value formula**: `Sized impact * Confidence multiplier = Weighted expected value`

Example: Feature A sizes at $500K annual impact, based on behavioral data (0.5x) = $250K weighted expected value. Feature B sizes at $200K, based on validated prototype (0.8x) = $160K. Feature A is still larger, but the gap narrows when accounting for evidence quality.

## Comparison Framework

When comparing 3+ opportunities, use a standardized scorecard.

| Dimension | Feature A | Feature B | Feature C |
|-----------|-----------|-----------|-----------|
| Sized annual impact | $X | $Y | $Z |
| Evidence quality multiplier | 0.Nx | 0.Nx | 0.Nx |
| Weighted expected value | $X' | $Y' | $Z' |
| Build cost (eng-weeks) | N | N | N |
| Weighted ROI (WEV / build cost) | ratio | ratio | ratio |
| Time to impact (weeks from start to measurable result) | N | N | N |
| Reversibility (can we roll back?) | Yes/Partial/No | | |
| Compounds? (gets more valuable over time?) | Yes/No | | |

**Decision rule**: Rank by Weighted ROI, then break ties with time-to-impact (faster wins), then reversibility (reversible wins). Compounding features get a tiebreaker bonus.
