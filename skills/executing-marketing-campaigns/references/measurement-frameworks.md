# Measurement Frameworks

Attribution models, metric hierarchies, reporting structures, and the
post-mortem framework. This file supports the measurement-first principle
from SKILL.md.

---

## Metric Hierarchy: Vanity vs Business

Not all metrics are equal. Optimize for business metrics. Use vanity metrics
only as diagnostics.

**Business Metrics (optimize for these):**
- Revenue attributed to campaign
- Marketing Qualified Leads (MQLs)
- Sales Qualified Leads (SQLs)
- Pipeline value generated
- Customer Acquisition Cost (CAC)
- Return on Ad Spend (ROAS)
- Net Revenue Retention (NRR) -- for retention campaigns

**Diagnostic Metrics (use to find problems, not to prove success):**
- Click-through rate (CTR)
- Landing page conversion rate
- Email open rate
- Cost per click (CPC)
- Bounce rate

**Vanity Metrics (never report as primary KPIs):**
- Impressions
- Reach
- Social media followers
- Page views without conversion context
- "Engagement" without a clear definition

**Rule:** If a campaign report leads with impressions or reach and does not
include a business metric, the reporting is broken. Fix it before the next
campaign.

---

## Attribution Models

Choose the model before launch. Changing attribution mid-campaign invalidates
comparison.

**Last Touch:**
- 100% credit to the final interaction before conversion
- Best for: Short sales cycles, single-channel campaigns
- Weakness: Ignores all awareness and nurture touchpoints

**First Touch:**
- 100% credit to the first interaction
- Best for: Understanding which channels drive awareness
- Weakness: Ignores everything that happened after initial contact

**Linear:**
- Equal credit to every touchpoint
- Best for: When you have no strong hypothesis about which stage matters most
- Weakness: Treats a random blog visit the same as a demo request

**Time Decay:**
- More credit to touchpoints closer to conversion
- Best for: Long sales cycles (B2B enterprise)
- Weakness: Undervalues early awareness touchpoints

**Position-Based (U-Shaped):**
- 40% first touch, 40% last touch, 20% distributed across middle
- Best for: Most B2B SaaS campaigns (balances awareness and conversion credit)
- This is the recommended default if you have no prior data.

**Data-Driven (algorithmic):**
- ML model assigns credit based on actual conversion paths
- Best for: Large datasets (1,000+ conversions/month)
- Weakness: Black box, requires significant data volume

**Practical Guidance:**
- < 100 conversions/month: use last touch or position-based (not enough data
  for anything fancier)
- 100-1,000 conversions/month: position-based or time decay
- > 1,000 conversions/month: data-driven if your platform supports it
- Always: compare at least two models to understand the spread

---

## UTM Parameter Standards

Consistent UTM usage is non-negotiable. Broken UTMs = broken attribution.

**Required Parameters:**
- `utm_source`: Platform or publisher (google, linkedin, newsletter)
- `utm_medium`: Marketing medium (cpc, email, social, organic)
- `utm_campaign`: Campaign name (product-launch-q1-2026)

**Optional but Recommended:**
- `utm_content`: Differentiates ad variants or links (cta-button, hero-image)
- `utm_term`: Keyword for paid search

**Naming Convention:**
- All lowercase, hyphens between words (no spaces, no underscores)
- Include date context in campaign name (q1-2026, mar-2026)
- Use a shared UTM builder spreadsheet so the whole team uses the same names
- Never change UTM conventions mid-campaign

---

## Reporting Templates

### Weekly Campaign Report (During Active Campaign)

```
Campaign: [Name]
Period: [Date Range]
Budget Spent: $X / $Y total (X% of budget)

Performance Summary:
  Impressions:    [N] (diagnostic only)
  Clicks:         [N] (CTR: X%)
  Conversions:    [N] (Conv Rate: X%)
  Cost/Conversion: $X (Target: $Y)
  Pipeline Value:  $X (if applicable)

Channel Breakdown:
  [Channel 1]: [spend] | [conversions] | [CPA]
  [Channel 2]: [spend] | [conversions] | [CPA]

Actions This Week:
  - [What was changed and why]
  - [What will be tested next week]

Kill Criteria Check:
  - CPA threshold: [current] vs [limit] --> [OK / WARNING / KILL]
  - Conversion rate: [current] vs [minimum] --> [OK / WARNING / KILL]
```

### Campaign Summary Report (Post-Campaign)

```
Campaign: [Name]
Duration: [Start] to [End]
Total Budget: $X spent of $Y allocated

Results vs Targets:
  Metric          | Target    | Actual    | Variance
  MQLs            | [N]       | [N]       | +/-X%
  SQLs            | [N]       | [N]       | +/-X%
  Pipeline Value  | $X        | $X        | +/-X%
  CAC             | $X        | $X        | +/-X%
  ROAS            | X:1       | X:1       | +/-X%

Channel Performance:
  Channel         | Spend     | Conv      | CPA       | Verdict
  [Channel 1]     | $X        | [N]       | $X        | Scale/Maintain/Cut
  [Channel 2]     | $X        | [N]       | $X        | Scale/Maintain/Cut

Key Learnings:
  1. [What worked and should be repeated]
  2. [What did not work and should be avoided]
  3. [What was inconclusive and needs more testing]

Recommendations for Next Campaign:
  - [Specific, actionable recommendations]
```

---

## Post-Mortem Framework

Run within 1 week of campaign end. This is mandatory -- campaigns without
post-mortems are wasted learning.

### Structure

**1. Performance Review (15 min)**
- Did we hit our targets? (refer to pre-defined success metrics)
- Which channels outperformed? Underperformed?
- Where did we over/under-spend relative to results?

**2. Timeline Review (10 min)**
- Did we launch on time?
- What caused delays? (approval bottlenecks, asset production, technical issues)
- Was the campaign duration right, or should it have been shorter/longer?

**3. What Worked (10 min)**
- Specific tactics, messages, or channels that exceeded expectations
- Why did they work? (audience insight, timing, creative quality, channel fit)
- Can these be systematized for future campaigns?

**4. What Did Not Work (10 min)**
- Specific failures with root cause analysis
- Was it a strategy problem (wrong audience, wrong channel) or execution problem
  (late launch, broken tracking, poor creative)?
- How do we prevent this specific failure next time?

**5. Surprises (5 min)**
- Anything unexpected -- positive or negative
- Data points that challenge existing assumptions

**6. Action Items (10 min)**
- Specific, assigned, time-bound actions for the next campaign
- Process improvements to implement immediately
- Tests to run based on this campaign's data

### Post-Mortem Rules
- No blame. Focus on systems and processes, not individuals.
- Data required. Every claim must be supported by a metric.
- Action-oriented. If a finding does not produce an action item, it is an
  observation, not a finding.
- Written record. Post-mortem notes go into a shared campaign archive.
  Verbal-only post-mortems are useless in 3 months.

---

## Campaign Health Quick-Check

Use this when someone says a campaign is "not working" and you need to
diagnose quickly.

```
Step 1: Are people seeing it?
  Check: Impressions, reach, email delivery rate
  If low --> Targeting, budget, or deliverability problem

Step 2: Are people engaging?
  Check: CTR, email click rate, video view rate
  If low --> Creative, messaging, or value prop problem

Step 3: Are people converting?
  Check: Landing page conversion rate, form completion rate
  If low --> Offer, page design, or friction problem

Step 4: Are conversions sticking?
  Check: Activation rate, 30-day retention, churn
  If low --> Expectation mismatch between campaign and product
```

Always diagnose top-down. Fixing conversion rate is pointless if nobody is
seeing the campaign in the first place.
