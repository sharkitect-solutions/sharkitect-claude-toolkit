---
name: onboarding-cro
description: "Use when optimizing post-signup user activation, first-run experience, time-to-value, onboarding checklist design, empty state optimization, or activation rate improvement. Also for stalled user re-engagement, onboarding email triggers, or feature discovery sequencing. NEVER for signup/registration form optimization (use signup-flow-cro), ongoing lifecycle email sequences beyond onboarding (use email-sequence), paywall or upgrade flow optimization (use paywall-upgrade-cro), general page conversion optimization (use page-cro)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# Onboarding CRO

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| SKILL.md | Activation framework, first-run strategy, checklist engineering, empty states, stalled user recovery, measurement, anti-patterns | Always (auto-loaded) |
| activation-analysis-playbook.md | Cohort analysis methodology (step-by-step with SQL), false activation traps (8 named), activation event evolution triggers, multi-product activation patterns, business model activation variations, activation debugging checklist | When defining or redefining the activation event, troubleshooting low activation rates, or validating activation metrics |
| mobile-onboarding-patterns.md | iOS vs Android differences (6 factors), push notification permission strategy (4 patterns with iOS one-shot trap), deep link onboarding resumption, small-screen progressive disclosure, app store pre-install onboarding, cross-platform consistency rules | When optimizing mobile app onboarding or cross-platform onboarding experiences |
| onboarding-experimentation-guide.md | Why onboarding experiments differ (5 broken assumptions), sample size for new-user tests, holdback group design, experiment catalog by component (first-run, checklist, email), measurement pitfalls (6 named), ICE prioritization for onboarding, when NOT to experiment | When running onboarding A/B tests, planning an optimization roadmap, or troubleshooting inconclusive results |

## Scope Boundary

| Area | This Skill | Not This Skill |
|------|-----------|----------------|
| Signup form fields, social auth, registration page | -- | signup-flow-cro |
| Post-signup activation, first-run, empty states, checklist | Yes | -- |
| Onboarding email triggers (day 1-14 stalled user) | Yes | -- |
| Ongoing lifecycle email sequences beyond onboarding | -- | email-sequence |
| Paywall, upgrade prompts, trial-to-paid conversion | -- | paywall-upgrade-cro |
| General landing page or pricing page conversion | -- | page-cro |
| In-app feature adoption after activation achieved | -- | product-led-growth / retention |
| A/B test statistical design and sample size | -- | ab-test-setup |

This skill starts AFTER signup completes and ends when the user reaches their activation event. Everything before signup is signup-flow-cro. Everything after activation is retention/lifecycle.

---

## Activation Definition Framework

The activation event is the single most important decision in onboarding. Everything else -- checklists, empty states, emails -- exists to drive users toward this one event.

**How to find it:** Cohort analysis of retained vs churned users. Identify the action that retained users completed in their first session that churned users did not. This is the activation event.

**Activation events by product type:**

| Product Type | Typical Activation Event | Why This Action |
|-------------|-------------------------|-----------------|
| B2B SaaS | Complete first workflow + invite teammate | Solo usage of team tools churns -- collaboration = stickiness |
| Marketplace | Complete first transaction | Browsing without transacting = window shopping |
| Dev tool | Successful first API call or integration | Docs reading without implementation = evaluation limbo |
| Content platform | Follow 5+ sources | Empty feed = no return trigger |
| Analytics | Install tracking + view first report | Uninstalled tracking = zero value delivered |
| Social app | Connect with 3+ existing contacts | Stranger network = no engagement pull |

**Critical rules:**
- Activation must be SINGULAR -- one measurable event, not a checklist of 10 things
- The event must correlate with 7-day retention at r > 0.5 or it is the wrong event
- If you cannot define activation from data, use "first time the user receives the core value" as a proxy and validate later
- Composite activations (A AND B) are acceptable only when both are required for value (e.g., analytics requires install AND view report -- one without the other is zero value)

---

## First-Run Strategy Decision

What happens in the first 30 seconds after signup determines whether users activate or abandon. First-match the user's product against these signals:

| Signal | Strategy | Implementation | Why |
|--------|----------|----------------|-----|
| Product needs personalization to show relevant content | Guided setup wizard (3-5 screens max) | Role/use-case selection, then customize dashboard | Generic first view = irrelevant value = bounce |
| Product is simple, core action is obvious | Product-first (drop into app immediately) | Single highlighted CTA on first screen | Fastest path to value -- no wizard friction |
| Product has cold start problem (empty = useless) | Pre-populated demo data | Sample project/data with "Try it" + "Start fresh" options | Shows value before user invests any effort |
| Product requires external integration to function | Single integration focus | One connector screen, skip everything else | One connection = one win. Multiple = decision paralysis |
| B2B with team features as core value | Invite flow first | "Who should join you?" immediately post-signup | Team products used solo churn at 3-5x higher rate |
| Product has multiple distinct use cases | Use-case selector (2-4 options max) | Each option leads to a tailored first-run path | Wrong first experience = "this isn't for me" |

**If none match clearly:** Default to product-first. Getting users into the product faster beats getting them into a wizard.

---

## Onboarding Checklist Engineering

A checklist is not "list some features." Every design choice affects completion rate.

**Sizing:** 3-5 items. Completion rate drops ~15% per item above 5 (Appcues 2023 benchmark data). Never exceed 5 unless the product genuinely requires it.

**Endowed progress effect:** Start the checklist at 20% complete (1 of 5 pre-checked, typically "Create account"). Users who see progress are 2x more likely to complete (Nunes & Dreze 2006). This is not a gimmick -- it is one of the most replicated findings in behavioral economics.

**Item ordering rules:**
1. First item completable in <60 seconds (quick win creates momentum)
2. Order remaining items by value delivered to user, NOT by setup complexity
3. If an item unlocks other items, place it earlier regardless of value rank
4. Final item should be the activation event itself

**Item copy formula:** `[Action verb] + [Object] + [Time estimate] -- [Benefit]`
- Good: "Connect Slack (1 min) -- Get notifications where your team works"
- Bad: "Set up integrations" (no time estimate, no benefit, vague action)

**Mandatory UX rules:**
- Dismiss option required -- trapped users churn faster than users who never saw the checklist
- Deep-link each item directly to the relevant screen (never make users navigate)
- Show completion state persistently (sidebar or top bar, not modal)
- On 100% completion: unlock a feature or show a meaningful metric, not confetti (celebration fatigue is real)

---

## Empty State Strategy

Every empty screen in the product is an onboarding surface. Most teams treat empty states as error pages. They should be treated as conversion opportunities.

**Required elements for every empty state:**
1. What this area does (1 sentence, benefit-oriented)
2. What it looks like with data (illustration, screenshot, or sample preview)
3. Primary CTA to create the first item
4. Secondary option: "Start from template" or "Import from [source]"

**Pre-populated vs truly empty decision:**

| Situation | Recommendation | Rationale |
|-----------|---------------|-----------|
| Complex product, activation requires seeing output | Pre-populate with demo data | Users need to see value before investing effort (+15-25% activation lift typical) |
| Simple product, creation IS the value | Truly empty with strong CTA | Demo data dilutes ownership feeling |
| Product with templates/presets | Offer template gallery | Compromise: user chooses content but skips blank-page paralysis |
| Data product (analytics, CRM) | Pre-populate with sample data + "Connect real data" CTA | Empty charts and tables communicate zero value |

**Empty state copy formula:** "[Area name] is where you'll [benefit]. [CTA to create first item]."
- Example: "Reports is where you'll track what matters. Create your first report."

---

## Stalled User Recovery

**Stalled user definition by segment:**

| Segment | Stalled Threshold | Why This Timing |
|---------|------------------|-----------------|
| B2C app | 24-48 hours post-signup | B2C intent decays rapidly -- if they didn't activate same day, momentum is lost |
| B2B SaaS (self-serve) | 3-7 days | B2B users often sign up during research, return later to evaluate |
| B2B SaaS (sales-assisted) | 7-14 days | Longer buying cycles, may need internal approval |
| Enterprise | 14-21 days | Implementation timelines, IT involvement, procurement |

**Email recovery sequence for stalled users:**

| Timing | Subject Angle | Content Focus | CTA |
|--------|--------------|---------------|-----|
| Day 1 | Value reminder | Restate the specific benefit they signed up for + single action to get started | "Pick up where you left off" |
| Day 3 | Address blocker | Anticipate the #1 reason users stall (too complex? missing integration? unclear value?) | "Here's the quickest way to [benefit]" |
| Day 7 | Offer help | Personal tone, offer live walkthrough or demo call | "Reply to this email" or "Book a 15-min call" |
| Day 14 | Last chance + social proof | Show what active users are achieving, imply what they're missing | "See what [N] teams built this week" |

**In-app recovery (returning stalled user):**
- Detect return visit after stall period
- Show "Welcome back" with simplified path: skip completed steps, highlight the ONE next step toward activation
- Never replay the full onboarding flow -- they already saw it and it didn't convert them

**High-value account escalation:** For accounts matching ICP or high-intent signals (company size, plan selected, referral source), trigger personal outreach from founder or CSM at day 3, not day 7. The 4-day difference in response time can be the difference between activation and churn.

---

## Onboarding Measurement Framework

| Metric | Good | Warning | Critical | Notes |
|--------|------|---------|----------|-------|
| Activation rate | >40% | 20-40% | <20% | % of signups completing activation event |
| Time to activation (B2C) | <1 day | 1-3 days | >3 days | Measured from signup timestamp |
| Time to activation (B2B) | <3 days | 3-7 days | >7 days | Longer is acceptable for enterprise |
| Onboarding completion | >60% | 30-60% | <30% | % completing all checklist items |
| Day 1 retention | >50% | 25-50% | <25% | Returned at least once on day after signup |
| Day 7 retention | >25% | 10-25% | <10% | Strongest early predictor of long-term retention |

**Step-level drop-off analysis:** Measure conversion between each onboarding step. The step with the largest absolute drop-off is your highest-leverage optimization target. Fix the biggest leak first -- do not optimize step 4 when 50% drop off at step 2.

**Segmented analysis is mandatory:** Aggregate activation rate hides segment-level problems. Always break down by: acquisition channel, device type, B2B company size, and use-case selected (if applicable). A 35% aggregate activation rate might be 60% from organic and 15% from paid -- the paid onboarding is broken, not the product.

---

## Onboarding Anti-Patterns

1. **Feature Tour Syndrome** -- 10-step product tour showing every feature on first login. Nobody reads past step 3. Fix: max 3 contextual tooltips, defer feature discovery to progressive disclosure over days 1-7.

2. **Premature Permission Asking** -- Requesting notification, location, or camera permissions before demonstrating any value. Users reflexively deny permissions when trust is zero. Fix: ask after the first value moment, explain the specific benefit ("We'll notify you when your report is ready").

3. **The Setup Wall** -- Requiring 5+ configuration steps before showing any product value. Each required step loses 10-20% of users. Fix: show value with minimal setup (smart defaults), complete remaining setup later via checklist.

4. **Email Verification Gate** -- Blocking all product access until email is verified. Verification emails have 50-70% open rates, so 30-50% of users never get in. Fix: allow limited access immediately, verify asynchronously, gate only sensitive actions behind verification.

5. **Checklist Theater** -- Checklist items that don't correlate with activation ("Complete your profile", "Read our blog", "Follow us on Twitter"). Fix: every checklist item must move the user closer to the activation event. If it doesn't contribute to activation, remove it.

6. **Configuration Overload** -- Asking 10+ preference questions before showing the product. Users came to use the product, not fill out a survey. Fix: ask 1-2 high-impact questions (role, primary use case), set smart defaults for everything else, refine later.

7. **Celebration Fatigue** -- Confetti and "Great job!" after every trivial action (created account, clicked a button, viewed a page). Devalues real milestones. Fix: celebrate only activation event and meaningful milestones. Silent acknowledgment (checkmark, brief animation) for routine steps.

8. **The Abandoned Dashboard** -- Sending users to an empty dashboard with no guidance after signup. Empty dashboards communicate "figure it out yourself." Fix: every post-signup screen must have a clear, visible next action. If the dashboard is empty, the dashboard IS the onboarding surface.

---

## Rationalization

| When you are tempted to... | Do this instead |
|---------------------------|-----------------|
| Add more checklist items to be "thorough" | Cut to 5 max. Every additional item reduces overall completion rate. Thoroughness kills activation. |
| Copy a competitor's onboarding flow | Analyze what THEIR activation event is. Your product likely has a different one. Borrowed flows optimize for borrowed metrics. |
| Skip activation definition and go straight to UI changes | Stop. Define the activation event first. Without it, you are optimizing navigation to an unknown destination. |
| Build a generic "product tour" as onboarding | Build a guided path to the activation event instead. Tours teach features. Onboarding delivers value. |
| Send the same onboarding emails to all users | Segment by action taken. A user who connected an integration needs different guidance than one who hasn't logged in since signup. |
| Add an NPS survey during onboarding | Wait until after activation. Surveying users who haven't received value yet measures first impressions, not product quality. |

---

## Red Flags

1. Activation event is undefined or defined as "signup" -- signup is not activation, it is the starting line
2. Onboarding checklist has 7+ items -- completion rate will be below 30%
3. Time to activation exceeds 7 days for a self-serve B2B product -- momentum is lost, re-engagement costs spike
4. Onboarding flow is identical for all user segments -- different roles/use-cases need different paths to value
5. No measurement of step-level drop-off -- you cannot optimize what you do not measure at each step
6. Stalled users receive no outreach for 14+ days -- by day 14 without contact, recovery rate drops below 5%
7. Empty states show only "No data yet" with no CTA -- every empty state without a next action is a dead end
8. Email verification blocks product access entirely -- 30-50% of users lost before they see any value

---

## NEVER

1. NEVER launch onboarding changes without defining the activation event first -- you need a target before you can aim
2. NEVER require more than 3 steps before showing the user any product value -- each required step loses 10-20% of users
3. NEVER treat onboarding as a one-time project -- activation rates shift with product changes, audience changes, and channel mix changes; measure continuously
4. NEVER assume your activation event is correct without validating against retention data -- intuition about what "matters" is wrong more often than right
5. NEVER gate the entire product behind onboarding completion -- users who skip steps but activate are more valuable than users who complete every step but never activate
