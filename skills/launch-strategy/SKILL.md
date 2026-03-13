---
name: launch-strategy
description: "Use when planning a product launch, feature announcement, go-to-market release, or phased rollout. Also use when the user mentions Product Hunt, early access, beta launch, waitlist, launch momentum, or release strategy. NEVER use for ongoing marketing campaigns (use marketing-strategy-pmm), creating launch assets or copy (use copywriting or content-creator), or post-launch analytics and attribution."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Launch Strategy

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Launch phases, channel strategy, timing decisions, Product Hunt tactical, post-launch momentum, anti-patterns | Always (auto-loaded) |
| launch-psychology-adoption.md | Switching cost taxonomy (5 types with quantified 9x threshold), Rogers' Diffusion tactical implications per segment, Chasm crossing and Bowling Alley strategy, loss aversion in free trials (reverse trial model), social proof cascade thresholds, network effect activation, commitment escalation ladder | When designing trial/freemium strategy, planning adoption curve progression, understanding why users aren't converting despite good product, or deciding between trial models |
| earned-media-pr-mechanics.md | Pitch anatomy (what journalists actually open), embargo structure (hard/soft/exclusive), editorial calendar timing by publication type, press kit optimization (usage rates per asset), warm introduction economics (3-8% cold vs 40-60% warm), earned media measurement (AVE is dead, what replaces it) | When planning PR outreach for a launch, preparing press materials, deciding whether to hire a PR firm, or measuring media coverage impact |
| launch-analytics-dark-funnel.md | Dark funnel attribution (60-70% of launch traffic is untrackable), "how did you hear about us?" survey implementation, K-factor calculation and benchmarks, launch spike decay analysis (5 patterns), cohort analysis by acquisition phase, real-time launch dashboard (what to watch vs ignore), conversion window by product type, attribution pitfalls | When setting up launch measurement, analyzing post-launch data, diagnosing why launch traffic didn't convert, or building a launch dashboard |

Do NOT load companion files for basic phase planning, simple Product Hunt launch, or standard channel selection -- SKILL.md covers these fully.

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| Phased product launch planning (alpha through public) | YES | -- |
| Channel strategy (owned/rented/borrowed) | YES | -- |
| Launch timing and sequencing decisions | YES | -- |
| Product Hunt, BetaList, HN launch tactics | YES | -- |
| Post-launch momentum and follow-up | YES | -- |
| Launch psychology and adoption dynamics | YES (via companion) | -- |
| PR/media outreach and embargo management | YES (via companion) | -- |
| Launch analytics and dark funnel attribution | YES (via companion) | -- |
| Ongoing marketing campaigns (non-launch) | NO | marketing-strategy-pmm |
| Writing launch copy, emails, or landing pages | NO | copywriting, email-composer, content-creator |
| Post-launch conversion rate optimization | NO | page-cro, signup-flow-cro |
| Pricing strategy and packaging | NO | pricing-strategy |
| Post-launch analytics and dashboards | NO | analytics-tracking |

## Launch Analysis Procedure

1. **Assess launch readiness**: Does the core use case work reliably? Is there an owned channel to capture signups? Is someone available for launch-day support?
2. **Classify launch scale**: Major (new product), Medium (new feature), or Minor (bug fix/tweak) -- determines effort level and channel mix.
3. **Map the channel strategy**: Select owned channels first, then rented for amplification, then borrowed for credibility.
4. **Design the phase progression**: Which phase is the product currently in? What signals indicate readiness for the next phase?
5. **Plan measurement**: Set up attribution (UTMs + "how did you hear" survey) before driving any traffic.

## Channel Strategy (ORB Framework)

Every launch distributes effort across three channel types. Rented and borrowed channels drive discovery; owned channels capture and retain the audience.

| Channel Type | Examples | Role in Launch | Risk |
|---|---|---|---|
| Owned | Email list, blog, podcast, branded community (Slack/Discord), product itself | Long-term compounding value; no algorithm dependency; direct relationship | Slow to build; requires consistent investment before launch |
| Rented | Twitter/X, LinkedIn, Reddit, YouTube, app stores | Fast visibility to existing audiences; viral potential | Algorithm changes, pay-to-play escalation, no data portability |
| Borrowed | Guest posts, podcast interviews, influencer partnerships, co-marketing, conference talks | Instant credibility; shortcut to established audiences | One-shot exposure; must convert to owned or it evaporates |

**Channel selection rule**: Pick 1-2 owned channels first (based on where your audience consumes content), then 1-2 rented channels for amplification, then pursue borrowed opportunities that convert to owned signups.

## Five-Phase Launch Framework

| Phase | Goal | Key Actions | Success Signal |
|---|---|---|---|
| 1. Internal | Validate core functionality | Recruit 5-15 friendly testers one-on-one; collect usability feedback; fix critical gaps | Testers can complete the core use case without hand-holding |
| 2. Alpha | First external validation | Landing page with email capture; announce existence; invite testers individually; MVP in production | Growing waitlist; first unsolicited signups |
| 3. Beta | Build buzz with broader feedback | Work through early access list; tease problem/solution publicly; recruit influencers to test | Word-of-mouth referrals; engagement on teasers |
| 4. Early Access | Validate at scale | Leak product details (screenshots, GIFs, demos); gather quantitative usage data; run product/market fit survey; throttle invites in batches (5-10% at a time) or invite all under "early access" framing | Retention metrics stabilize; PMF survey > 40% "very disappointed" |
| 5. Full Launch | Maximum visibility and conversion | Open self-serve signups; start charging; announce across all channels; Product Hunt / BetaList / HN; in-app popups, blog post, social, email blast | Sustained signup velocity beyond launch day spike |

## Launch Scale Decision Matrix

Not every update deserves the same effort. Match marketing intensity to the update's impact.

| Update Type | Examples | Marketing Effort | Channels |
|---|---|---|---|
| Major (new product, product overhaul) | New product launch, major pivot, platform expansion | Full campaign: blog + email + social + in-app + PR + marketplace listings | All ORB channels |
| Medium (new feature, integration) | New integration, significant UI redesign, pricing change | Targeted: email to relevant segments + in-app banner + social post | Owned + 1 rented |
| Minor (bug fix, tweak) | Performance improvement, small UX fix, minor feature | Changelog + release notes | Owned only (changelog) |

**Stagger releases**: Ship features separately over weeks rather than bundling them. Each announcement sustains momentum and signals active development.

## Product Hunt Tactical Guide

Product Hunt works best for B2C SaaS and developer tools targeting early adopters. Skip it if your audience is enterprise-only.

| Phase | Critical Actions |
|---|---|
| Pre-launch (2-4 weeks) | Build relationships with PH community members; optimize listing (compelling tagline, polished visuals, short demo video < 2 min); study top launches in your category; engage in communities providing value before pitching |
| Launch day | Treat as all-day event; respond to every comment in real time; spark discussions (ask questions back); direct all traffic to owned signup (not just PH upvotes); coordinate existing audience to engage |
| Post-launch | Follow up with every commenter; convert PH traffic to email signups; publish post-launch content (learnings, metrics, behind-the-scenes); use PH badge as social proof |

**Timing**: Launch Tuesday-Thursday. Avoid holidays and major tech events. Post at 12:01 AM PT for maximum runway.

## Launch Timing Decision Table

| Factor | Launch Now | Wait |
|---|---|---|
| Core use case works reliably | Yes | -- |
| No clear core use case yet | -- | Yes -- ship when one path works end-to-end |
| Competitor launching soon | Yes -- capture mindshare first | -- |
| Critical security/data issue unresolved | -- | Yes -- trust is unrecoverable once lost |
| Waitlist > 500 people with no product access | Yes -- you're losing momentum | -- |
| No owned channel established yet | -- | Yes -- build email capture first or launch traffic evaporates |
| Team bandwidth for launch-day support | Yes | If no one can respond to users on launch day, wait |

## Post-Launch Momentum

The launch announcement is the beginning, not the end. Compound momentum with:

1. **Onboarding email sequence** (triggered on signup) -- introduce key features over 5-7 days
2. **Roundup inclusion** -- add announcement to your next newsletter/weekly update for people who missed it
3. **Comparison pages** -- publish "vs competitor" pages while launch attention is high
4. **Interactive demo** -- create a no-code walkthrough (Navattic, Storylane) so visitors can try before signing up
5. **Continuous signal** -- even minor changelog updates remind customers the product is actively evolving, building retention and word-of-mouth

## Launch Anti-Patterns

| Name | Anti-Pattern | Why It Fails | Fix |
|---|---|---|---|
| The Big Bang Bet | Skip all phases, go straight to public launch | Single-moment launches have one shot; no feedback loop, no momentum build-up, no course correction. If the product has issues, they're exposed publicly | Always run at least internal + beta phases before public launch |
| The PH Obsession | Treat Product Hunt rank as THE launch metric | PH is one rented channel with a 24-hour window; 80% of PH traffic bounces without converting. Rank doesn't correlate with long-term success | Track conversion to owned channel (email signups, trials started). PH is amplification, not strategy |
| The Ghost Launch | Launch with no owned channel to capture signups | Rented and borrowed channel traffic evaporates within 48 hours. Without email capture, every visitor who doesn't sign up immediately is gone permanently | Build email capture mechanism before driving any traffic. Waitlist page minimum |
| The Perfectionist Trap | Wait for "feature completeness" before launching | There is no "ready" -- launching early with one strong use case beats launching late with ten mediocre ones. Early users validate what to build next | Launch when core use case works reliably. Everything else is iteration |
| The Feature Dump | Bundle 5+ features into one announcement | Overwhelms users, wastes potential for multiple momentum moments, makes it impossible to attribute which feature drove interest | Stagger releases: ship features separately over weeks. Each announcement sustains momentum |
| The Silent Ship | Launch a minor update with zero communication | Every update is a signal that the product is alive. Silence between major launches causes user churn and kills word-of-mouth | Every update gets a changelog entry at minimum. Larger updates get email + social |
| The Lone Channel | Rely entirely on one borrowed channel (one influencer, one podcast) | If that single channel falls through, the launch has no backup. One channel also means one audience segment, limiting reach | Always have 2+ channels active. Owned channel as foundation, 1-2 rented/borrowed for amplification |
| The Empty Room | Drive traffic before the product can handle it (no onboarding, broken core flow) | First impressions are permanent. Users who hit a broken experience on launch day will never return, and they'll tell others | Validate the full signup-to-core-use-case flow with beta users before opening to public traffic |

## Recommendation Confidence

| Area | Confidence | Override When |
|---|---|---|
| Phased launch approach (alpha -> beta -> public) | HIGH | True emergency launches (security product responding to a major vulnerability, competitor about to capture your market). Even then, compress phases rather than skip them |
| Owned channel before paid amplification | HIGH | Only if you have an existing large audience on a rented channel (100K+ followers) AND the product has viral mechanics that compensate for no email capture |
| Product Hunt for B2C/developer tools | MEDIUM | Skip PH for enterprise-only products, niche B2B verticals where the audience isn't on PH, or products that can't be demonstrated in screenshots/short video |
| Five-phase progression model | MEDIUM | Open-source projects often skip alpha/beta and go straight to public repo + Show HN. The community IS the beta. Also skip phases for products with strong network effects that need immediate scale |
| Staggering feature releases | HIGH | Only bundle when features are deeply interdependent and make no sense individually. Even then, announce the bundle but highlight one feature per day |
| Launch timing (Tuesday-Thursday) | LOW | Depends heavily on audience. Developer tools may do better on weekends (side project time). Enterprise products should avoid Fridays. Test with your specific audience |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "We'll just launch when the product is ready" | There is no "ready" -- phased launches (alpha, beta, early access) generate feedback that makes the product better before the big push |
| "Product Hunt will handle our launch marketing" | PH is one rented channel with a 24-hour window; without owned channels to capture traffic, PH visitors bounce and never return |
| "Our product is so good it will market itself" | Even exceptional products need distribution; virality requires seeding through borrowed and rented channels before it compounds |
| "We should wait until we have more features" | Launching early with one strong use case beats launching late with ten mediocre ones; early users validate what to build next |
| "Let's do a big-bang launch instead of phases" | Single-moment launches have one shot; phased launches build momentum, collect feedback, and create multiple press opportunities |
| "Minor updates don't need marketing" | Every update is a signal that the product is alive; changelog updates retain existing users and generate word-of-mouth |

## Red Flags

- No email capture mechanism before driving traffic -- 60-80% of launch visitors will never return if not captured on first visit
- Skipping internal/alpha phases and going straight to public launch -- unvalidated products face public criticism that permanently damages reputation and SEO
- Bundling 5+ features into one announcement -- wastes 4 momentum opportunities and overwhelms users trying to understand the product
- No one available for launch-day support -- unanswered questions in the first 4 hours set the tone for all coverage and reviews
- Single channel dependency (one influencer, one podcast appearance) -- if that channel underperforms, there's no backup plan
- No attribution setup before launch -- without UTMs + "how did you hear" survey, you can't optimize mid-launch or learn for next time
- No post-launch follow-up sequence -- the launch day spike decays to baseline within 48-72 hours without sustained momentum actions
- Announcing a public launch date before core use case is reliable in production -- creates deadline pressure that forces shipping broken features

## NEVER

- Launch on a dedicated IP without completing the warm-up schedule if email is a primary channel -- deliverability failure kills launch reach
- Skip building an email capture mechanism before driving traffic -- visitors who leave without signing up are gone permanently
- Announce a launch date publicly before the core use case works reliably in production
- Send a single launch email to your entire list without segmentation -- engagement rates determine future deliverability
- Treat Product Hunt rank as the primary success metric -- conversion to owned channel signups is what matters
