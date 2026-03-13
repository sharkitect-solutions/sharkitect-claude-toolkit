# GTM Playbooks Reference

## Launch Tier Classification

Before planning ANY launch, classify its tier. This determines timeline, budget, and cross-functional involvement.

### Tier 1: Major Launch (8-week timeline)
**Trigger:** New product, platform expansion, new market entry, major rebrand
**Cross-functional:** Product + Marketing + Sales + CS + Engineering
**Budget:** $50k-$100k (Series A scale)

**Phase 1: Foundation (Weeks 1-4)**
- [ ] Launch kickoff with all stakeholders -- define goals, roles, timeline
- [ ] Positioning and messaging finalized (see positioning-frameworks.md)
- [ ] ICP and target segments confirmed
- [ ] Competitive battlecards updated
- [ ] Success metrics defined: pipeline $, MQLs, win rate, adoption rate
- [ ] Kill criteria defined: what signals would cause pivot or pause

**Phase 2: Build (Weeks 3-6)**
- [ ] Sales enablement: deck, demo script, objection handling, battlecards
- [ ] Marketing assets: landing pages, email sequences, blog posts, video
- [ ] Paid campaign setup: LinkedIn + Google (targeting, creative, bidding)
- [ ] Press/analyst outreach: briefing docs, embargoed access
- [ ] Beta customers: 5-10 early access users for testimonials
- [ ] Internal training: sales team certified on new positioning

**Phase 3: Launch (Weeks 7-8)**
- [ ] Day 1: Press release, email blast, social campaign, paid ads live
- [ ] Day 1: Sales outbound blitz (top 100 target accounts)
- [ ] Day 1-3: Monitor conversion funnels hourly, fix leaks
- [ ] Day 3-5: Webinar or live demo event
- [ ] Week 2: First optimization pass (pause underperforming channels)
- [ ] Week 2: Post-launch customer interviews (5-10)

**Phase 4: Optimize (Weeks 8-12)**
- [ ] Week 3-4: Scale winning channels (+20% weekly budget increase)
- [ ] Win/loss analysis on first competitive deals
- [ ] Messaging refinement based on sales and customer feedback
- [ ] Post-launch report: metrics vs goals, learnings, next actions

### Tier 2: Standard Launch (4-week timeline)
**Trigger:** Significant feature, new integration, pricing change
**Cross-functional:** Product + Marketing + Sales
**Budget:** $10k-$25k

**Week 1:** Messaging, assets list, sales enablement brief
**Week 2:** Build assets (blog post, email, landing page update, sales one-pager)
**Week 3:** Internal rollout (sales training, CS briefing)
**Week 4:** External launch (email, blog, social, in-app notification)

### Tier 3: Minor Launch (1-week timeline)
**Trigger:** Small feature, UX improvement, bug fix, optimization
**Cross-functional:** Product + Marketing only
**Budget:** <$5k

**Day 1-2:** Changelog entry, in-app notification copy
**Day 3-4:** Publish to existing customers
**Day 5:** Monitor adoption, update docs

## GTM Motion Selection Detail

### PLG (Product-Led Growth) Execution

**When to use:** ACV <$5k, end-user buyer, low switching cost, product can demonstrate value in <5 minutes

**Required infrastructure:**
- Free trial or freemium tier (time-limited trial converts better than freemium for B2B)
- Self-serve onboarding (no human touch to first value moment)
- In-product upgrade prompts (usage-based triggers, not time-based)
- Product analytics (activation metrics, feature adoption, expansion signals)

**PLG metrics stack:**
| Metric | Target | Why it matters |
|---|---|---|
| Time to first value | <5 minutes | Users who don't activate in session 1 rarely return |
| Activation rate | >25% | % of signups who reach "aha moment" |
| Free-to-paid conversion | >5% (trial), >2% (freemium) | Revenue efficiency of self-serve funnel |
| Expansion revenue | >120% net dollar retention | PLG economics depend on land-and-expand |
| Viral coefficient | >0.5 | Each user should generate 0.5+ additional signups |

**PLG failure signals:**
- Activation rate <10%: Product doesn't deliver value fast enough for self-serve
- Free-to-paid <2%: Either free tier is too generous or paid tier isn't compelling
- High signup volume + low activation: Marketing is attracting wrong audience (ICP problem)

### Sales-Led Execution

**When to use:** ACV >$50k, economic buyer (VP+), multi-stakeholder decision, long evaluation

**Required infrastructure:**
- SDR/AE team (or outsourced sales partner for initial market entry)
- CRM with deal stages, forecasting, activity tracking
- Sales enablement library mapped to deal stages
- Demo environment with customer-relevant data

**Sales-led metrics stack:**
| Metric | Target | Why it matters |
|---|---|---|
| Sales cycle length | <90 days (mid-market), <180 days (enterprise) | Longer cycles burn cash and forecast accuracy |
| Win rate | >25% (competitive), >40% (uncontested) | Below this, economics don't work |
| Pipeline coverage | 3-4x quota | Less than 3x = consistent quota miss |
| AE productivity | >$500k ARR/AE/year | Below this, hire more AEs only after fixing win rate |
| CAC payback | <18 months | Longer payback requires more capital |

### Hybrid Execution

**When to use:** ACV $5k-$50k, or serving multiple segments (SMB + Enterprise)

**Architecture:**
```
SMB segment ($2k-$10k ACV)
  --> PLG motion leads
  --> Sales assists on upgrade opportunities
  --> Self-serve onboarding, sales closes expansion

Mid-market segment ($10k-$50k ACV)
  --> Product-assisted sales leads
  --> Free trial used as evaluation tool (not acquisition)
  --> AE manages from demo request onward

Enterprise segment ($50k+ ACV)
  --> Sales-led motion
  --> Product demo as proof, not self-serve
  --> Multi-threaded deal management
```

**The handoff problem:** Hybrid fails when the PLG-to-sales handoff is unclear. Define explicit signals:
- Product Qualified Lead (PQL): User hits usage threshold + fits ICP
- Sales Qualified Lead (SQL): PQL + confirmed budget + timeline
- Trigger: When PQL score crosses threshold, auto-assign to AE in CRM

## International Market Entry

### Demand Signal Validation (Before ANY Localization)

**Do NOT enter a market based on TAM alone.** Validate demand signals first:

| Signal | Strength | Action |
|---|---|---|
| Inbound leads from target market (>10/month) | Strong | Proceed to localization |
| Partner or reseller expressing interest | Moderate | Explore partnership, test with their network |
| Customer requests for local support/language | Moderate | Survey depth of demand (10+ customers requesting) |
| Large TAM but zero inbound | Weak | Do NOT invest in localization. Run targeted ads first to test |
| Competitor recently entered this market | Informational | Validates market exists, but doesn't validate YOUR demand |

### Market Entry Playbook (per market)

**Phase 1: Validate (4-8 weeks, <$5k)**
- Run targeted LinkedIn/Google ads in local language
- Create one localized landing page (not full website)
- Measure: CPC, conversion rate, lead quality vs home market
- Decision gate: If cost-per-lead is <2x home market, proceed

**Phase 2: Test (8-12 weeks, $10-20k)**
- Localize core website pages (homepage, product, pricing)
- Local currency pricing with market-appropriate packaging
- Hire local SDR or engage local sales partner
- First 10 customers: interview for positioning validation
- Decision gate: If close rate is >50% of home market, scale

**Phase 3: Scale (ongoing)**
- Full product localization (UI, support docs, in-app)
- Local support during business hours
- Local case studies and testimonials
- Legal compliance (GDPR for EU, PIPEDA for Canada, etc.)
- Local partnerships and co-marketing

### Localization Checklist (goes beyond translation)

**Essential (before accepting local revenue):**
- [ ] Local currency pricing displayed
- [ ] Local payment methods accepted (SEPA for EU, etc.)
- [ ] Data residency compliance (where is customer data stored?)
- [ ] Local terms of service and privacy policy
- [ ] Tax compliance (VAT for EU, GST for Canada, etc.)

**Important (before scaling past 10 customers):**
- [ ] Website in local language (core pages minimum)
- [ ] Product UI in local language (if non-English market)
- [ ] Local business hours support (even if remote)
- [ ] Local phone number and address (builds trust)
- [ ] Local case studies (one is enough to start)

**Nice to have (for mature market presence):**
- [ ] Local office or co-working presence
- [ ] Local marketing events (meetups, conferences)
- [ ] Local content marketing (blog, social media)
- [ ] Local partnerships (resellers, integrators, consultants)

## Launch Metrics Framework

### Leading Indicators (track daily during launch week)
| Metric | What it tells you | Action if off-track |
|---|---|---|
| Landing page conversion rate | Is messaging resonating? | A/B test headline, rewrite value prop |
| Demo request volume | Is demand being generated? | Increase ad spend or improve targeting |
| Free trial signups | Is the offer compelling? | Check pricing page, simplify signup flow |
| Email open rate | Is the announcement reaching people? | Test subject lines, check deliverability |
| Sales response time | Are leads being followed up? | Enforce SLA (<4 hours for inbound) |

### Lagging Indicators (track weekly post-launch)
| Metric | What it tells you | Healthy benchmark |
|---|---|---|
| MQL to SQL conversion | Are leads qualified? | >20% |
| SQL to closed-won | Is sales able to close? | >25% |
| Pipeline generated ($) | Is the launch creating revenue opportunity? | 3:1 vs launch spend |
| Customer adoption rate | Are existing users engaging? | >40% within 90 days |
| Win rate vs pre-launch | Did positioning improve competitiveness? | Increase >5% |

### Kill Criteria (when to pivot or pause)
- Landing page conversion <1% after 1 week of traffic: Positioning is wrong, not execution
- Zero SQLs after 2 weeks: Target audience is wrong or product-market fit is absent
- Win rate DECREASES post-launch: New messaging is worse than old messaging, revert
- CAC >3x target after 4 weeks: Channel mix is wrong, reallocate budget
