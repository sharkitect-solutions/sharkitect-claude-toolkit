---
name: micro-saas-launcher
description: "Use when user is building a solo/small-team SaaS product targeting a niche market with <$50K MRR goal, needs help with go/no-go decisions, MVP scoping to weeks not months, initial pricing architecture, or launch channel selection for indie/bootstrapped products. NEVER for full application architecture (use app-builder), enterprise or funded launch campaigns (use launch-strategy), advanced pricing optimization or experimentation (use pricing-strategy), market positioning or competitive strategy (use product-strategist), landing page design or CRO (use page-cro)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# Micro-SaaS Launcher

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Idea validation, tech stack selection, pricing architecture, launch channels, traction metrics | Always (auto-loaded) |
| mvp-shipping-playbook.md | Feature scoping decisions, 2-week ship plan, build vs buy matrix, deployment options, technical debt budget | When scoping an MVP, deciding what to build first, or planning a ship cycle |
| retention-growth-playbook.md | Churn diagnosis, activation metrics, dunning recovery, growth levers, retention emails, pricing iteration | When product has launched and needs retention improvement or growth levers |
| financial-modeling-guide.md | Revenue projections, cost structure, breakeven calculation, pricing change impact, milestone planning, tax awareness | When projecting revenue, calculating unit economics, or planning financial milestones |

## Scope Boundary

| This Skill Handles | Defer To |
|---|---|
| Go/no-go decision for niche SaaS ideas | product-strategist (market positioning) |
| MVP scoping and 2-week ship plans | app-builder (full application architecture) |
| Initial pricing architecture (flat/tiered/usage) | pricing-strategy (price optimization, A/B tests) |
| Solo-founder launch channel selection | launch-strategy (enterprise/funded launches) |
| Early traction metrics (first 100 customers) | seo-optimizer (organic growth at scale) |
| Tech stack selection for bootstrapped products | senior-architect (system design at scale) |

## Idea-to-Revenue Decision Matrix

Evaluate in order. First STOP kills the idea. First PAUSE means gather more data.

| Signal | Check | GO | PAUSE | STOP |
|---|---|---|---|---|
| Pain frequency | How often does the pain occur? | Daily/weekly | Monthly | Yearly or less |
| Willingness to pay | Are people paying for alternatives? | 3+ competitors with paying users | Free tools exist, no paid | Nobody trying to solve this |
| Your distribution | Can you reach 100 prospects in 30 days? | Existing audience or community access | Cold outreach possible | No channel identified |
| Build scope | Can one person ship core in 2 weeks? | Yes, clear feature set | Maybe, needs scoping | Requires team or 3+ months |
| Revenue ceiling | Can 200 customers sustain you? | $10K+ MRR at target price | $3-10K MRR possible | Sub-$3K MRR ceiling |
| Churn structure | Will customers stay 12+ months? | Workflow dependency or data lock-in | Moderate switching cost | One-time use or easy to replace |

A viable micro-SaaS needs GO on pain frequency, willingness to pay, AND build scope. Everything else can be PAUSE.

### Ambiguous Signal Resolution

When the decision matrix gives mixed results, use these tiebreakers:

| Ambiguous Situation | What It Usually Means | Recommended Action |
|---|---|---|
| Pain is real but nobody pays for alternatives | Either the pain isn't severe enough, or you found a nascent market | Test: can you pre-sell to 5 prospects at target price before building? If yes, nascent market. If no, insufficient pain. |
| Existing competitors but all have terrible products | Either the market is hard to serve profitably, or incumbents are complacent | Check: are the bad products making money? If yes, opportunity. If they are also struggling, the market itself is the problem. |
| Strong demand signals but revenue ceiling looks low | Niche may be too small, OR you are underpricing | Recalculate at 2-3x your initial price. If ceiling still low at higher price, the niche is too small for solo sustainability. |
| Multiple product ideas pass the matrix equally | Analysis paralysis disguised as due diligence | Choose the one where YOU have the strongest distribution advantage. Product quality is a commodity; distribution is the moat. |
| B2C idea scores well but you have B2B experience | Your distribution network mismatches the product | Switch to B2B framing of the same problem. B2C micro-SaaS has 5-10x higher churn and 3-5x lower ARPU. Almost always worse for solo founders. |
| Technical co-founder wants to build, non-technical wants to sell | Healthy tension if channeled correctly | Non-technical founder does customer development for 2 weeks FIRST. Build only what those conversations validate. Prevents building in a vacuum. |

## Tech Stack Decision Matrix

Do NOT default to any stack. Match stack to product type.

| Product Type | Frontend | Backend/DB | Auth | Why This Stack |
|---|---|---|---|---|
| Content/SEO tool | Next.js (SSR) | Supabase Postgres | Supabase Auth | SEO needs server rendering |
| Chrome extension | Vanilla JS/React | Firebase | Firebase Auth | Extension APIs need lightweight |
| API/developer tool | Minimal dashboard | Express/Fastify + Postgres | API keys | Developers expect REST/CLI, not fancy UI |
| Automation/workflow | React SPA | Supabase or PlanetScale | Clerk | Heavy client interaction, less SEO |
| Slack/Discord bot | None (bot UI) | Node.js + Redis | OAuth per platform | Platform-native, no custom frontend |
| Email/newsletter tool | Next.js | Postgres + queue (BullMQ) | Magic links | Deliverability > UI complexity |

**Override rule**: If you already know a stack well, use it. Familiarity beats optimization at micro-SaaS scale. Only switch stacks when your current one physically cannot support the product type (e.g., SSR requirement).

## Solo Founder Failure Modes

| Failure Mode | Detection Signal | What Is Actually Happening | Intervention |
|---|---|---|---|
| Feature factory | Backlog grows faster than releases; no feature ties to revenue | Building feels productive but avoids the hard problem (distribution) | Freeze backlog. Ship nothing until 3 users request the same thing |
| Premature scaling | Optimizing infra, hiring, or automating before $5K MRR | Avoiding sales by solving engineering problems instead | Stay on single-server. Manual ops until unit economics prove out |
| Wrong market | High trial signups but <2% conversion to paid | The audience has the problem but not the budget or urgency | Reposition upmarket (B2B) or find the segment that churns least |
| Distribution blindness | Great product, zero organic growth after 60 days | Built product-first without a distribution thesis | Identify ONE channel. Spend 80% of non-coding time on it |
| Perfectionism loop | Redesigning UI, refactoring code, "not ready yet" after 4+ weeks | Fear of rejection disguised as quality standards | Ship today. Set a public deadline. First version should embarrass you slightly |
| Discount addiction | Lifetime deals, 50% coupons, free tiers doing all the work | Using price as substitute for product-market fit | Remove discounts for 30 days. If signups drop to zero, problem is value not price |
| Metrics theater | Tracking pageviews, Twitter followers, and waitlist size instead of paying customers and churn | Vanity metrics feel like progress but measure attention, not revenue | Dashboard should have exactly 3 numbers: MRR, paying customers, and monthly churn. Remove everything else. |
| Platform dependency | Building entirely on one platform's API (Twitter, Shopify, Notion) without diversification plan | Platform rule changes or API deprecation can kill your product overnight (Twitter API pricing 2023, Heroku free tier 2022) | Never build >80% of revenue on a single platform dependency. Have a migration plan documented before launch. |
| Support spiral | Founder spending 3+ hours/day on customer support at <$5K MRR | Under-invested in self-serve (docs, onboarding, in-app guidance). Each support ticket is a product bug. | Track top 5 support topics weekly. Turn each into a product fix or help doc. Reduce volume, don't hire support. |

## Pricing Architecture Decision

| Signal | Single Flat Price | Two Tiers (Free/Paid) | Three Tiers | Usage-Based |
|---|---|---|---|---|
| Value is uniform across users | Best fit | Overkill | Overkill | Wrong model |
| Need viral/freemium growth | Wrong model | Best fit | Acceptable | Wrong model |
| Clear feature differentiation exists | Too limiting | Acceptable | Best fit | Wrong model |
| Value scales with consumption (API, sends, seats) | Wrong model | Wrong model | Acceptable | Best fit |
| You have <50 customers | Best fit | Acceptable | Too complex | Too complex |

**Starting price formula**: Find what the manual alternative costs per month. Price at 20-30% of that. If no manual alternative exists, the pain might not be real.

**Micro-SaaS price anchors**: Simple tools $9-29/mo, Pro tools $29-99/mo, B2B tools $49-299/mo. Lifetime deals = 3-5x monthly (use sparingly -- they attract deal-seekers, not long-term customers).

## Launch Channel Selection

| Product Type | Primary Channel | Secondary Channel | Avoid |
|---|---|---|---|
| Developer tool | Hacker News, Reddit, GitHub | Dev Twitter, tech blogs | Facebook Ads, LinkedIn |
| SMB productivity | AppSumo, Product Hunt | Google Ads (high intent) | Organic social |
| Creator tool | Twitter/X, YouTube | Product Hunt, communities | Cold email |
| B2B niche vertical | Cold email to ICP list | LinkedIn outreach | Broad social media |
| Chrome extension | Chrome Web Store SEO | Reddit, niche forums | Paid ads (CAC too high) |
| Slack/Discord integration | App directory listing | Community where users gather | SEO (low search volume) |

**Channel commitment rule**: Pick ONE primary channel. Work it for 60 days before evaluating. Spreading across 3+ channels in the first 90 days guarantees mediocre results in all of them.

## Traction Metrics by Stage

| Stage | Timeframe | North Star | Healthy | Warning | Critical |
|---|---|---|---|---|---|
| Pre-launch | Before day 0 | Waitlist signups | 200+ signups | 50-200 signups | <50 signups |
| Launch week | Days 1-7 | Trial starts or signups | 50+ trials | 20-50 trials | <20 trials |
| First month | Days 1-30 | Paying customers | 20+ paying | 5-20 paying | <5 paying |
| Month 2-3 | Days 30-90 | Monthly churn rate | <5% monthly | 5-10% monthly | >10% monthly |
| Month 3-6 | Days 90-180 | MRR growth rate | 15%+ MoM | 5-15% MoM | <5% MoM |
| Month 6-12 | Days 180-365 | Net revenue retention | >100% NRR | 85-100% NRR | <85% NRR |

**Reality check**: Most micro-SaaS products take 6-12 months to reach $1K MRR. If you hit $1K MRR in month 1-2, you likely have strong product-market fit. If you are at $0 MRR after 90 days with active effort, pivot the positioning or the product.

## Recommendation Confidence

Not all guidance above carries equal certainty. Override when your context demands it.

| Area | Confidence | Override When |
|---|---|---|
| 2-week build constraint | HIGH | Almost never. Scope creep kills more micro-SaaS than any other factor. Exception: regulated industries (HIPAA, SOC 2) requiring compliance features before launch. |
| GO/PAUSE/STOP validation | MEDIUM | You have proprietary distribution (audience >5K, partnership pipeline, or marketplace access) that changes the acquisition math fundamentally |
| Tech stack recommendations | LOW | You have 2+ years in another stack. Familiarity beats optimization at this scale. Only switch when your stack physically cannot support the product type. |
| Pricing starting points | MEDIUM | You have direct evidence: pre-sales at a specific price, competitor pricing analysis, or willingness-to-pay interviews with 10+ prospects |
| Channel selection | LOW | Channel effectiveness varies wildly by niche. These are defaults for common product types. Test your actual niche for 30-60 days before trusting or abandoning a channel. |
| Traction benchmarks | MEDIUM | Thresholds assume $20-40 ARPU. B2B at $99/mo needs 5-10x fewer customers to hit the same MRR. Adjust proportionally. |
| Failure mode detection | HIGH | These patterns have consistent outcomes across thousands of indie founders. If you recognize the signal, act immediately. |

## Quick Diagnosis

When something isn't working, match the observable signal to a likely cause:

| You're Seeing | Probably Means | Do This First |
|---|---|---|
| High traffic, zero signups | Value prop mismatch with traffic source | Rewrite headline to match the search intent or ad copy that brought visitors |
| Signups but zero activation | Onboarding friction or unclear first step | Email 5 stuck users: "What were you hoping to do when you signed up?" |
| Active free users, no upgrades | Free tier too generous OR paid value unclear | Restrict free tier for 2 weeks, measure impact on upgrades and churn |
| Paying users, high monthly churn | Problem is one-time (not recurring) or better alternative found | Interview 5 churned users. Ask what they switched to and why. |
| Feature requests from free users only | You have fans, not customers | Ignore until a paying user requests the same thing |
| One channel works, others flat | Normal. This IS the plan working. | 3x investment in the working channel. Cut the rest. |
| MRR flat for 60+ days | Acquisition saturated OR churn eating new growth | Diagnose: is new customer count dropping, or is churn rate rising? Fix the binding constraint. |
| Competitor ships your exact feature | Common. Not fatal at micro-SaaS scale. | Your advantage is speed + customer intimacy. Ship 2 improvements this week. |

## Rationalization Table

| If You Catch Yourself Thinking... | The Real Issue Is... |
|---|---|
| "I just need one more feature before launching" | You are afraid of market rejection and using building as avoidance |
| "My product is for everyone" | You have not identified a specific buyer and will market to nobody |
| "I will figure out distribution after the product is good" | Distribution is harder than building -- starting late means failing late |
| "Competitors mean the market is saturated" | You have not found your differentiation angle -- competitors validate demand |
| "I need to raise money to compete" | Micro-SaaS wins on focus and speed, not capital -- if you need funding, it is not micro-SaaS |
| "I will offer a free tier to get users" | Free users are not validation -- only paying customers prove value |

## Red Flags -- Stop and Verify

1. Building for 4+ weeks with zero external feedback from potential paying users
2. Cannot describe the target customer in one sentence with job title and pain point
3. Chosen tech stack requires learning a new framework AND a new language simultaneously
4. Pricing below $9/month for a B2B tool (signals you do not believe in the value)
5. Launch plan depends on "going viral" or a single Product Hunt launch for all traction
6. Adding a feature because a free user requested it (free users optimize for free, not for value)
7. MRR has been flat for 60+ days and you are adding features instead of changing distribution
8. You have 3+ pricing tiers before reaching 50 paying customers

## NEVER

1. NEVER recommend a specific tech stack without asking about the founder's existing skills and the product type first
2. NEVER suggest "build an audience first" as a launch strategy -- that takes years and is a separate business
3. NEVER treat a Product Hunt launch as a growth strategy -- it is a one-day event, not a channel
4. NEVER advise building a marketplace or two-sided platform as a micro-SaaS -- marketplace dynamics require scale that contradicts micro-SaaS constraints
5. NEVER skip the pricing conversation until after launch -- price validates willingness to pay, which is the entire thesis
