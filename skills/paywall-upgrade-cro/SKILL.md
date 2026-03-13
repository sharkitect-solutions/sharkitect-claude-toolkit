---
name: paywall-upgrade-cro
description: When building or optimizing in-app paywalls, upgrade modals, feature gates, usage limit screens, or trial expiration flows. Also when diagnosing why upgrade conversion is low despite product engagement. For public pricing pages use page-cro instead. For non-upgrade popups use popup-cro instead. For form field optimization use form-cro instead. For onboarding-to-aha flows use onboarding-cro instead. For experiment infrastructure use ab-test-setup instead.
---

# Paywall and Upgrade Screen CRO

## Scope Boundary

| Scenario | This skill | Use instead |
|---|---|---|
| In-product upgrade modal after user hits feature gate | YES | -- |
| Trial expiration screen with usage summary | YES | -- |
| Usage limit reached, prompting tier change | YES | -- |
| Mobile app subscription paywall (iOS/Android) | YES | -- |
| Plan comparison shown inside authenticated product | YES | -- |
| Public pricing page on marketing site | NO | page-cro |
| Generic popup for email capture or announcement | NO | popup-cro |
| Optimizing form fields on checkout page | NO | form-cro |
| First-run onboarding driving to aha moment | NO | onboarding-cro |
| Signup form optimization for new account creation | NO | signup-flow-cro |
| Setting up A/B test infrastructure for experiments | NO | ab-test-setup |

Key distinction: this skill handles moments where the user is ALREADY inside the product and has experienced value. The conversion psychology differs fundamentally from cold-visitor pricing pages.

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Trigger diagnosis, upgrade psychology, pricing gotchas, measurement, anti-patterns | Always (auto-loaded) |
| platform-compliance.md | Apple App Store review criteria, StoreKit 2 vs 1, Google Play billing lifecycle, EU DSA requirements, regional compliance | When implementing mobile paywalls or preparing for app store submission |
| pricing-experiments.md | A/B test design for paywalls, sample size estimation, statistical mistakes, experiment templates, cohort analysis, RPPI attribution | When designing paywall experiments or analyzing test results |
| upgrade-copy-guide.md | CTA copy by trigger type, value proposition structure, social proof hierarchy, urgency calibration, dismiss button copy, localization gotchas | When writing paywall copy, CTAs, or value propositions |

## Paywall Optimization Procedure

Follow this sequence for every paywall optimization request. The order matters.

1. **Identify the trigger context**: Match the user's scenario to the Paywall Trigger Diagnosis table. If none of the 6 patterns match, ask what specific user action or threshold triggers the paywall -- do not guess. If the user has an existing paywall that converts poorly, skip to step 3 and diagnose the current implementation first.
2. **Confirm aha moment exists**: Before optimizing any paywall, verify the user has a defined activation moment. If they haven't identified one, pause paywall work and redirect to onboarding-cro -- no paywall optimization matters if users don't perceive value yet. If the user's product is mature and activation is well-established, skip this step.
3. **Audit against anti-patterns**: Check all 7 anti-patterns in the table below. If any are present, fix those BEFORE adding new optimization -- layering optimization on broken foundations amplifies the damage. If the user's current paywall has none of the anti-patterns and converts above the benchmark range for their trigger type, focus on incremental refinement rather than redesign.
4. **Select psychology mechanism**: Match the upgrade context to the appropriate mechanism (Endowed Progress, Loss Aversion, Decoy Pricing, Status Quo Bias). If the user already has a working mechanism with measured results, do not replace it -- only change if RPPI is below the benchmark range for their trigger type.
5. **Plan measurement**: Define the primary metric (RPPI preferred over raw conversion rate) and set benchmarks from the Measurement section. If the user lacks analytics infrastructure, help them set up basic event tracking before launching any paywall changes -- unmeasured optimization is guessing.

**Key mindset**: The highest-converting paywalls don't feel like paywalls. They feel like the natural next step in a workflow the user is already engaged in. If the upgrade prompt breaks flow rather than continuing it, the trigger timing is wrong regardless of copy or pricing quality.

## Paywall Trigger Diagnosis

First-match decision table. Use the FIRST row where all signals match.

| Signal pattern | Trigger type | Urgency | Non-obvious timing |
|---|---|---|---|
| User clicked locked feature 3+ times in 7 days | Feature intent gate | High -- they want this specific thing | Show 2-3 seconds AFTER the blocked click, not during. Cognitive processing time means immediate interruption reads as punishment, not opportunity |
| Usage at 80-95% of limit, accelerating consumption rate | Graduated limit warning | Medium -- preview scarcity before hard wall | Show at 80% with soft banner, 95% with modal. Never surprise at 100% -- the "sudden wall" kills trust permanently |
| Trial day 10 of 14, user has created stored data | Loss-framed trial reminder | High -- created data = switching cost | Lead with THEIR data ("12 projects, 47 files") not your features. Data hostage anxiety converts, feature lists don't |
| Power user (top 20% engagement) on free tier for 30+ days | Habituated free user | Low -- wrong urgency backfires here | These users have rationalized "free is enough." Urgency fails. Instead: show what power users at their usage level DO with Pro (peer comparison) |
| User invited 2+ teammates to free workspace | Team expansion signal | Medium -- organizational budget unlocks | Frame as team capability, not individual upgrade. "Your team can..." shifts from personal expense to business tool |
| First session, no meaningful actions yet | DO NOT SHOW | None | Any paywall before aha moment has 60-80% dismiss rate AND poisons future paywall response for 30+ days (negative priming) |

### Why trigger timing is non-obvious

The Hook Model inversion (Nir Eyal): showing paywalls at PEAK engagement feels logical but interrupts the reward phase of the habit loop. The user is in flow state -- interruption creates resentment, not purchase intent. Optimal trigger is during the TRANSITION between sessions or between tasks (natural cognitive breaks), not during peak activity. Exception: hard usage limits where the block IS the natural break.

**Override rule**: If the user's product has a monetization model that doesn't match these patterns (usage-based billing, enterprise contracts, marketplace fees), adapt the trigger logic to their model rather than forcing a freemium/trial pattern match. The signals above assume freemium-to-paid or trial-to-paid models.

The 2-3 second delay rule: when a user clicks a locked feature, their brain needs processing time to shift from "doing the task" to "evaluating a purchase." Immediate paywall display (under 500ms) gets processed as an error state. A brief delay (2-3 seconds) with a subtle transition animation lets the cognitive shift happen naturally. RevenueCat A/B data shows 12-18% higher conversion with delayed presentation vs instant modal.

## Upgrade Psychology Mechanisms

### Endowed Progress Effect
Nunes & Dreze (2006): people given a 10-stamp card with 2 stamps pre-filled complete at higher rates than those given an 8-stamp card with none filled. Apply to upgrades: show users their "progress toward Pro" based on features they already use. "You're using 4 of 6 Pro features on your free plan -- unlock the remaining 2." This reframes the upgrade from "buying something new" to "completing something started." Effective lift: 15-25% over standard feature comparison.

### Loss Aversion Framing Calibration
Loss framing ("you'll lose X") works ONLY when the user has created irreplaceable value:
- Trial with stored data, created projects, team configurations -- loss framing converts 2-3x better than gain framing
- New user with no investment -- loss framing backfires. "You'll lose access" to things they barely used feels manipulative. Use gain framing instead
- Usage limit users -- hybrid works best. "Keep your 47 projects AND unlock unlimited" combines loss prevention with gain

### Decoy Pricing Architecture
Ariely's Economist study: a deliberately unattractive middle option pushes selection toward premium. The specific math that practitioners use:
- Decoy must be within 10-15% price of target plan but with 40-50% fewer features
- If Pro is $29/month and Basic is $9/month, a "Plus" at $24/month with only 2 features more than Basic makes Pro look like obvious value
- Decoy works on plan comparison screens but HURTS on single-plan paywalls (adding options to a focused paywall drops conversion 20-30%)
- Three-plan display optimal. Four or more plans trigger choice paralysis -- conversion drops 15% per additional plan beyond three

### Status Quo Bias Exploitation
For trial-to-paid conversions: frame the upgrade as MAINTAINING their current experience, not buying something new. "Continue with Pro" outperforms "Upgrade to Pro" by 8-12% in trial expiration contexts. The user's mental model is "I already have this" -- the CTA should reinforce that frame rather than breaking it.

## Mobile Paywall Architecture

### Apple Platform Constraints
- Anti-steering rules (updated 2024): apps CANNOT link to web checkout, mention that prices are lower on web, or use language encouraging out-of-app purchase. Violations result in app rejection, not just guideline warnings
- StoreKit 2 vs StoreKit 1: SK2 supports offer codes, subscription status API, and server-side receipt validation natively. SK1 requires manual receipt parsing. If targeting iOS 15+, use SK2 exclusively -- SK1 paywalls feel dated and lack native subscription management
- App Store review triggers for paywalls: full-screen paywalls shown before any free content = likely rejection. Paywalls that obscure the close button or use dark patterns = rejection. Paywalls that don't clearly show subscription terms (price, duration, renewal) = rejection. Apple specifically checks that "Restore Purchases" is accessible

### Google Play Billing Gotchas
Five proration modes for subscription upgrades/downgrades, each with different billing behavior:
1. IMMEDIATE_WITH_TIME_PRORATION -- prorates remaining time, no extra charge. Users expect this but it creates revenue recognition complexity
2. IMMEDIATE_AND_CHARGE_PRORATED_PRICE -- charges difference immediately. Cleanest for upgrades but can surprise users with unexpected charge
3. IMMEDIATE_WITHOUT_PRORATION -- charges full new price immediately, old subscription time lost. Feels unfair to users, avoid for upgrades
4. DEFERRED -- change takes effect at next billing cycle. Best for downgrades but users don't see immediate effect, causing "did it work?" confusion
5. IMMEDIATE_AND_CHARGE_FULL_PRICE -- charges full new price now, extends billing date. Only use for significantly higher tiers where time-value matters

Default to mode 1 for upgrades and mode 4 for downgrades unless business logic requires otherwise.

### Remote Paywall Configuration
RevenueCat, Superwall, and Adapty all enable server-side paywall changes without app updates. Key decision factors:
- RevenueCat: strongest analytics, largest install base, but paywall UI customization requires Superwall integration or custom code
- Superwall: best for rapid paywall A/B testing (no-code paywall builder), but less mature subscription management
- Adapty: strongest paywall builder with native A/B testing, but smaller ecosystem and fewer third-party integrations
- All three take 0% revenue share on their base plans (they charge flat monthly fees). The "free tier" of each supports enough for most indie apps

## Pricing Presentation Gotchas

### Toggle Default Position
Annual-first default increases annual plan selection by 15-22% (Profitwell data across 2,100+ SaaS companies). The anchoring effect means whichever price users see FIRST becomes their reference point. Monthly-first makes annual feel expensive ("that's $X more commitment"). Annual-first makes monthly feel wasteful ("I'd save $Y per year").

### Threshold Effects in SaaS Pricing
$29 vs $30 matters far less than $99 vs $100. Psychological thresholds in SaaS cluster at $10, $50, $100, $250, and $1000. Crossing a threshold boundary costs 15-30% conversion compared to staying just below. Within a threshold band ($31 vs $39), the effect is minimal (2-4%). Implication: price at $49 or $99, never $51 or $101.

### Per-Seat Pricing Display Failures
"Per user/month, billed annually" creates 4 common misunderstandings:
1. Users multiply by 12 and think that's the total (forgetting the per-user multiplier)
2. Users see "$10/user/month" and expect a $10 charge (not $10 x users x 12)
3. Annual billing with per-seat pricing hides the true commitment -- show the actual annual total prominently
4. Adding seats mid-cycle confuses users about prorated charges -- explain BEFORE they hit the payment screen

### Currency Localization Mistakes
Three failures practitioners see repeatedly:
1. Direct conversion without psychological rounding -- $29.99 becomes EUR 27.43, which feels arbitrary. Round to EUR 27.99 or EUR 29.99
2. Wrong currency symbol placement -- USD uses prefix ($29), EUR varies by country (29 EUR in Germany, EUR 29 in Ireland), JPY uses prefix with no decimals
3. Tax display mismatch -- US/Canada show prices excluding tax, EU/UK/Australia require tax-inclusive display. Showing US-style prices to EU users violates consumer protection law and creates sticker shock at checkout

## Upgrade Flow Measurement

### Benchmarks by Trigger Type
Paywall-to-upgrade conversion rates (industry medians from RevenueCat, Baremetrics, ProfitWell aggregated data):
- Feature gate click: 3-8% (low because many clicks are exploratory, not high-intent)
- Usage limit reached: 8-15% (higher because the user has proven need through volume)
- Trial expiration (with data created): 15-25% (highest because loss aversion is active)
- Soft upgrade prompt (time-based): 0.5-2% (lowest -- no urgency, no blocked action)
- Team expansion trigger: 10-20% (organizational budget reframes personal cost)

### Time-to-Upgrade Distribution
Upgrade timing follows a bimodal distribution, not a normal curve. Peak 1: within 48 hours of first paywall view (impulse converters). Peak 2: 14-21 days later (deliberate evaluators). The gap between peaks is a dead zone where almost nobody converts. Implication: median time-to-upgrade is far more useful than mean. A mean of 10 days hides the reality that users convert in 2 days or 18 days, rarely 10.

### Upgrade Quality Scoring
Conversion rate alone is misleading. A paywall that converts 20% but those users churn at 40% within 30 days is worse than one that converts 10% with 5% churn. Track 30-day retention of upgraded users by paywall variant. If a variant shows conversion above 15% but 30-day retention below 70%, the paywall is creating "regret purchases" -- likely through false urgency or misleading feature promises.

### North Star Metric
Revenue Per Paywall Impression (RPPI) = total revenue from upgrades / total paywall impressions. This single metric captures conversion rate, plan selection (which tier), AND billing frequency (monthly vs annual) in one number. A paywall that converts fewer users but into annual plans can have higher RPPI than one with higher conversion to monthly. Typical RPPI ranges: $0.02-0.08 for freemium SaaS, $0.15-0.50 for mobile apps with hard paywalls.

## Anti-Patterns

| Name | Pattern | Why it fails | Quantified impact |
|---|---|---|---|
| The Premature Ask | Paywall before aha moment | 60-80% dismiss rate, negative priming poisons future paywall response for 30+ days | Users shown premature paywalls convert 40% less on subsequent paywalls vs users who saw no early paywall |
| The Hostage Screen | Blocking critical workflow with no escape route | Drives support tickets and app store complaints, not upgrades | 1-star reviews mentioning "paywall" or "forced upgrade" increase 3-5x |
| The Feature Fog | 20+ features in comparison table | Cognitive overload causes decision paralysis -- users defer instead of choosing | Reducing features shown from 15+ to 5-7 most relevant increases conversion 18-25% |
| The Silent Paywall | Lock icon with no explanation of WHY this feature is paid | Feels arbitrary and punitive, user thinks it should be free | Adding a single sentence explaining the value ("used by teams processing 1000+ items/month") lifts conversion 10-15% |
| The Guilt Trip Close | Manipulative dismiss text ("No, I don't want to grow my business") | EU Digital Services Act compliance risk, brand damage, social media backlash potential | Short-term 2-3% lift, but NPS drops 8-12 points and support complaints increase |
| The Frequency Nag | Same paywall shown 3+ times per session | Conversion drops 40% after 3rd impression in same session, annoyance compounds | Cap at 2 per session with 24-hour cooldown after dismiss. Escalating urgency across sessions (not within) |
| The Bait Downgrade | Making free tier progressively worse to force upgrades | Accelerates churn instead of conversion -- users leave rather than pay when they feel manipulated | Free-tier degradation correlates with 2-3x increase in churn vs stable free tier with clear upgrade path |

## Pre-Launch Paywall Checklist

Verify before shipping any paywall to production:

| Check | Why | Fail = |
|---|---|---|
| Close/dismiss button visible and accessible | Apple/Google reject hidden or delayed close buttons | App store rejection |
| Subscription terms shown (price, duration, renewal) | Legal requirement on iOS, Google Play, and EU markets | App rejection or legal violation |
| "Restore Purchases" accessible on iOS | Apple specifically checks during review | App rejection |
| Paywall frequency capped at 2 per session | Conversion drops 40% after 3rd impression | Annoyance-driven churn |
| Loss framing only for users with stored data | Loss framing without investment backfires | Lower conversion than no paywall |
| RPPI tracking implemented before launch | Cannot optimize what you cannot measure | Flying blind on ROI |
| Platform-specific billing tested end-to-end | StoreKit 2 / Google Play Billing edge cases | Failed payments, refund storms |
| Dismiss text is neutral ("Not now" or "Maybe later") | Guilt-trip text violates EU DSA and damages NPS | Legal risk and brand damage |

## Rationalization

1. Why trigger timing research over generic "show after aha moment" | Claude's training data has the surface-level advice everywhere. The 2-3 second delay rule, Hook Model inversion, and bimodal distribution are practitioner knowledge from A/B testing platforms, not CRO blog posts
2. Why specific proration modes for Google Play | Five different billing behaviors that each create different user experiences -- getting this wrong causes refund requests and bad reviews. No CRO article covers this; it's billing API documentation cross-referenced with UX impact
3. Why Apple anti-steering rules in a CRO skill | Paywall optimization for iOS is constrained by App Store policy that changes frequently. Practitioners learn this through rejection, not through CRO training. Missing these constraints means optimized paywalls that get rejected
4. Why RPPI over conversion rate | Every CRO resource teaches "optimize conversion rate" but practitioners who manage subscription revenue know that conversion rate alone is misleading. RPPI captures the actual business outcome
5. Why named anti-patterns with quantified impact | Generic "don't use dark patterns" advice is in every CRO guide. Naming specific patterns with measured consequences (NPS drop from guilt trips, conversion decay from frequency nagging) gives actionable thresholds
6. Why decoy pricing math specifics | Ariely's work is widely cited but the specific implementation rules (10-15% price gap, 40-50% feature gap, three-plan maximum) come from practitioner testing, not from the original research

## Red Flags

1. STOP if recommending a paywall before the user has defined their product's aha moment -- help them identify it first using onboarding-cro
2. STOP if showing more than 7 features in a comparison table -- compress to the 3-5 features that matter most for the user's segment
3. STOP if using loss framing for users who haven't created stored data -- switch to gain framing, loss framing without investment backfires
4. STOP if suggesting the same paywall for iOS and Android without addressing platform-specific billing constraints -- each platform has different rules
5. STOP if optimizing conversion rate without mentioning 30-day retention of upgraders -- high conversion with high churn means the paywall is creating regret purchases
6. STOP if recommending paywall frequency above 2 per session -- conversion drops 40% after the 3rd impression, suggest cross-session escalation instead
7. STOP if designing a plan comparison with 4+ tiers -- choice paralysis drops conversion 15% per additional plan beyond three
8. STOP if using per-seat pricing display without showing the calculated annual total -- 4 common misunderstandings mean users will be surprised at checkout

## NEVER

1. NEVER show a paywall during active user flow (mid-task, mid-creation) -- the interruption cost exceeds any conversion gain and creates lasting negative association with upgrade prompts
2. NEVER use manipulative dismiss button text ("No, I prefer less revenue") -- EU DSA compliance risk, measurable NPS damage, and the 2-3% short-term lift is not worth the brand erosion
3. NEVER recommend iOS paywalls that link to web checkout or mention web pricing -- App Store rejection is near-certain and risks account-level review escalation
4. NEVER optimize paywall conversion rate in isolation without tracking upgrade quality (30-day retention) -- a paywall that converts regret-purchasers destroys LTV
5. NEVER suggest degrading the free tier to force upgrades -- this accelerates churn 2-3x faster than it drives conversion and poisons word-of-mouth
