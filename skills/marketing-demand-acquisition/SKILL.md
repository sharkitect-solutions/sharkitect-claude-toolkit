---
name: marketing-demand-acquisition
description: "Use when planning demand generation campaigns, optimizing paid media spend across channels, building acquisition strategies, or calculating customer acquisition costs. Also use when the user mentions demand gen, paid ads, LinkedIn ads, Google ads, Meta ads, CAC, acquisition strategy, lead generation, pipeline generation, or MQL/SQL optimization. NEVER use for brand marketing or awareness campaigns without acquisition goals (use marketing-strategy-pmm), content creation or copywriting (use content-creator or copywriting), or email sequence design (use email-sequence)."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Marketing Demand & Acquisition

Plans and optimizes multi-channel acquisition for B2B SaaS, covering paid media, SEO, partnerships, and attribution -- calibrated for Series A+ startups with hybrid PLG/sales-led motions.

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Channel strategy, budget allocation, campaign planning, attribution | Always (auto-loaded) |
| scripts/calculate_cac.py | Calculate blended and channel-specific CAC | When computing acquisition costs or building unit economics models |
| platform-bidding-gotchas.md | LinkedIn/Google/Meta platform-specific gotchas: Audience Network waste, broad match drift, Advantage+ cannibalization, location targeting, conversion action defaults | Load when configuring campaigns on LinkedIn, Google, or Meta. Also load when diagnosing unexplained spend increases, audience mismatch, or declining ROAS. Do NOT load for channel selection or budget allocation (covered in SKILL.md). |
| attribution-implementation.md | UTM architecture, multi-touch attribution math, dark funnel measurement, offline conversion import, attribution debugging | Load when setting up attribution, designing UTM structure, debugging attribution gaps, or reconciling platform-reported vs CRM conversions. Do NOT load for high-level attribution model selection (covered in SKILL.md). |
| cac-ltv-unit-economics.md | Blended vs channel vs fully-loaded CAC, LTV calculation methods, NRR impact, payback periods by segment, CAC inflation diagnosis | Load when calculating acquisition costs, building LTV models, evaluating channel profitability, or presenting unit economics to investors. Do NOT load for campaign execution (use SKILL.md + platform-bidding-gotchas.md). |

## Channel Selection Decision Matrix

Choose channels based on ACV, audience, and funnel stage -- not habit.

| Channel | Best For | CAC Range | Conversion Rate | Use When |
|---|---|---|---|---|
| LinkedIn Ads | B2B, Enterprise, ABM, Director+ targeting | $150-400 | 0.5-2% | ACV >$10k, decision-maker targeting needed |
| Google Search | High-intent BOFU, solution-aware buyers | $80-250 | 2-5% | Users actively searching for your category |
| Google Display | Retargeting warm traffic, brand awareness | $50-150 | 0.3-1% | Retargeting existing visitors only -- cold display wastes budget |
| Meta (FB/IG) | SMB, consumer-like B2B, visual products | $60-200 | 1-3% | ACV <$10k, broad awareness, lookalike audiences |
| SEO / Content | Compounding organic acquisition | $50-150 (amortized) | 2-5% | Long-term play -- 6+ month payoff, but lowest sustainable CAC |
| Partnerships | Co-marketing, referrals, integrations | $100-300 | 5-10% | Complementary products with overlapping ICP |

**Channel prioritization rule**: Start with 2 channels maximum. Master them before adding more. Adding channels prematurely dilutes budget and learning velocity.

## Budget Allocation Framework

| Company Stage | Total Monthly Budget | Allocation |
|---|---|---|
| Pre-revenue / Seed | $5-15k | 60% one paid channel (LinkedIn or Google Search) + 40% SEO/content |
| Series A ($30-50k/mo) | $30-50k | 35% LinkedIn, 30% Google Search, 15% SEO, 10% Partnerships, 10% Experiments |
| Series B+ ($80k+/mo) | $80k+ | 30% LinkedIn, 25% Google, 15% Meta, 15% SEO, 10% Partnerships, 5% Experiments |

**Regional adjustment**: EU markets allocate 10-15% more to LinkedIn (strongest B2B channel in EU). US markets balance Google and LinkedIn equally.

## Campaign Planning Checklist

Before launching any campaign, confirm all items:

1. **Objective defined**: Specific SQL/MQL target with cost ceiling (e.g., "50 SQLs at <$300 CPO")
2. **Audience specified**: Company size, job titles, industries, geography -- not broad targeting
3. **Offer matches funnel stage**: TOFU = thought leadership/report, MOFU = demo/webinar, BOFU = free trial/consultation
4. **UTM structure set**: `utm_source={channel}&utm_medium={type}&utm_campaign={id}&utm_content={variant}`
5. **Landing page ready**: Dedicated LP matching ad message; not homepage
6. **Tracking confirmed**: CRM integration live, lead scoring configured, attribution reporting set
7. **Budget and duration**: Daily budget cap set, minimum 2-week test duration before evaluating
8. **Handoff protocol**: SQL criteria defined, routing workflow active, SLA agreed (4-hour response target)

## Funnel Stage Tactics

| Stage | Goal | Tactics | Success Metrics |
|---|---|---|---|
| TOFU (Awareness) | Brand visibility, site traffic | Paid social (thought leadership), content syndication, SEO (informational keywords), co-webinars | Traffic, engagement rate, email signups |
| MOFU (Consideration) | MQL generation | Paid search (solution keywords), retargeting, gated content, comparison pages, email nurture | MQLs, content downloads, demo page visits |
| BOFU (Decision) | SQL conversion | Brand/competitor paid search, free trial CTAs, case studies, intent-based retargeting | SQLs, demos booked, pipeline $ |

**Funnel balance rule**: Startups over-invest in TOFU. If MQL-to-SQL conversion is below 15%, shift budget from TOFU awareness to MOFU/BOFU conversion -- the problem is conversion quality, not volume.

## LinkedIn Ads Tactical Guide

| Element | Recommendation |
|---|---|
| Campaign structure | One campaign group per initiative, separate campaigns by funnel stage (Awareness / Consideration / Conversion) |
| Targeting | Company size 50-5000, Director+ titles, specific industries. Use Matched Audiences for retargeting and email list uploads |
| Lead Gen Forms vs Landing Pages | Lead Gen Forms: 2-3x higher conversion, lower quality -- use for TOFU/MOFU. Landing Pages: lower conversion, higher quality -- use for BOFU |
| Budget | Start $50/day per campaign. Scale 20% weekly if CAC < target |
| Creative types | Thought leadership (no product pitch), social proof (logos + testimonials), problem-solution (pain point in 3 seconds), demo-first (show product immediately) |

## Google Ads Tactical Guide

| Element | Recommendation |
|---|---|
| Campaign priority | 1. Brand (protect terms), 2. Competitor ("X alternative"), 3. Solution (category keywords), 4. Problem (informational), 5. Display retargeting |
| Keyword strategy | Exact match for brand, phrase match for solution, broad match with negatives for discovery. Maintain 100+ negative keywords |
| Bid strategy | Manual CPC until 50+ conversions, then Target CPA, then Maximize Conversions with tCPA after 100+ conversions |
| Ad format | Responsive Search Ads: 15 headlines (value props, features, social proof, CTAs, keywords) + 4 descriptions |
| EU adjustment | Bid 15-20% higher for same quality in EU markets |

## Attribution Model Selection

| Model | Use When | Limitation |
|---|---|---|
| First-touch | Evaluating which channels drive initial discovery | Ignores all nurturing influence |
| Last-touch | Evaluating which channels close deals | Ignores earlier touchpoints that built awareness |
| Multi-touch W-shaped (40-20-40) | Hybrid PLG/sales-led (recommended for Series A+) | More complex to explain to stakeholders |
| Linear | Need simple equal-weight view across touchpoints | Overvalues low-impact touches |

**Setup**: Use multi-touch as default. Run first-touch and last-touch reports side-by-side monthly to understand channel roles at different funnel stages.

## Scaling Rules

| Signal | Action |
|---|---|
| CAC < target for 2+ consecutive weeks | Increase budget 20% weekly |
| CAC > target for 2+ consecutive weeks | Pause campaign, diagnose (audience, creative, landing page, offer), relaunch |
| Conversion rate drops >20% from baseline | Check for creative fatigue, landing page issues, or audience saturation |
| MQL-to-SQL rate below 15% | Tighten targeting, increase lead scoring threshold, review SQL criteria with sales |
| One channel 2x+ more efficient than others | Shift 20% of underperformer budget to winner; don't kill underperformer entirely until replacement tested |

**Kill rule**: If a campaign hasn't produced a single SQL in 4 weeks at adequate budget, kill it. Don't optimize dead campaigns.

## MQL-to-SQL Handoff

| Element | Specification |
|---|---|
| SQL criteria | Title (Director+) + Company size (50-5000) + Budget confirmed + Timeline (<90 days) + High-intent action (demo request or equivalent) |
| Routing | Automated via CRM workflow to assigned SDR |
| SLA | SDR responds within 4 hours, AE books demo within 24 hours |
| Recycling | If not qualified: return to nurture list, reduce lead score, re-engage in 6-12 months |
| Lost opportunity tracking | Track closed-lost reasons (price, features, competitor, budget, timing) to inform product and messaging |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "We need to be on every channel" | Spreading budget across 5+ channels means none gets enough spend to optimize; master 2 channels before adding a third |
| "Our CAC is fine as a ratio of ACV" | CAC must be evaluated with payback period; a $500 CAC is fine for $50k ACV but catastrophic for $500 ACV -- always compare CAC to LTV |
| "We'll figure out attribution later" | Without attribution from day one, you cannot identify which campaigns drive pipeline; every dollar spent without tracking is unlearnable |
| "LinkedIn is too expensive" | LinkedIn's higher CPL is offset by superior targeting precision for B2B; cost per SQL (not CPL) is the metric that matters |
| "SEO takes too long, we'll do it later" | SEO compounds over time; starting 6 months late means 6 months of missed organic growth that paid can never fully replace |
| "Sales says our leads are bad" | Before blaming lead quality, verify: Are leads being followed up within SLA? Is the SQL definition agreed upon? Data resolves opinion conflicts |

## Red Flags

- Running paid campaigns with no UTM tracking or CRM integration -- every dollar is unattributable
- Spending >50% of budget on TOFU awareness with no MOFU/BOFU conversion campaigns
- No negative keyword list on Google Search campaigns (wastes 20-40% of spend on irrelevant clicks)
- MQL-to-SQL handoff with no SLA -- leads go cold while sales prioritizes inbound
- Campaign running for 4+ weeks with zero SQLs and no pause/diagnosis
- Budget allocation unchanged for 3+ months despite channel performance data showing clear winners and losers
- No landing page -- ads point to homepage

## NEVER

- Launch a paid campaign without dedicated landing pages -- homepage sends visitors to navigation instead of conversion
- Report CPL (cost per lead) as the primary metric -- CPL ignores lead quality; always report cost per SQL and cost per opportunity
- Set up attribution after campaigns are running -- retroactive attribution is unreliable; instrument before the first dollar is spent
- Optimize for MQL volume without tracking MQL-to-SQL conversion -- volume without quality is vanity spend
- Trust channel benchmarks without validating against your own data -- benchmarks are averages across industries; your specific CAC depends on your ICP, offer, and sales process
