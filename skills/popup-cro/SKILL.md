---
name: popup-cro
description: "Use when optimizing popups, modals, overlays, slide-ins, exit intent popups, announcement banners, lead capture popups, popup timing/trigger strategy, popup frequency rules, or overlay conversion rate. NEVER for optimizing form fields inside a popup (use form-cro). NEVER for page-level conversion optimization beyond the popup (use page-cro). NEVER for A/B test statistical design or sample sizing (use ab-test-setup). NEVER for post-conversion email sequences (use email-sequence)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# Popup CRO

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Popup type decision matrix, trigger timing, Google compliance, frequency logic, popup vs inline decision, copy anti-patterns | Always (auto-loaded) |
| browser-api-mechanics.md | Exit intent cross-browser reality (mouseout Safari limitation), IntersectionObserver for scroll triggers, requestIdleCallback for non-blocking display, Page Visibility API, popup CLS prevention, animation performance | Load when implementing popup triggers in code, debugging why a popup doesn't fire on certain browsers/devices, or optimizing popup display performance. Do NOT load for popup copy, design, or A/B testing strategy. |
| legal-compliance-specifics.md | Google intrusive interstitial exact penalty rules, EU ePrivacy/GDPR/DSA requirements for popups, CCPA/CPRA opt-out and financial incentive rules, CASL email capture requirements, compliance decision matrix by jurisdiction | Load when the user's site targets EU/UK/California/Canadian audiences, when implementing cookie consent, or when organic traffic dropped after adding popups. Do NOT load for trigger timing or copy optimization unrelated to compliance. |
| advanced-trigger-engineering.md | Scroll velocity detection with thresholds, cursor trajectory prediction, engagement scoring model (point-based trigger system), session-aware frequency capping (storage architecture, cross-tab coordination), idle detection for re-engagement | Load when implementing custom triggers beyond basic scroll/time/exit, building engagement scoring systems, implementing session-aware frequency capping, or debugging trigger conflicts. Do NOT load for basic popup setup or legal compliance. |

## Scope Boundary

| Topic | This Skill | Other Skill |
|---|---|---|
| Popup trigger timing, format, frequency | YES | - |
| Modal/overlay design decisions | YES | - |
| Exit intent strategy | YES | - |
| Slide-in / bottom bar / sticky bar offers | YES | - |
| Google interstitial penalty avoidance | YES | - |
| Popup vs inline placement decision | YES | - |
| Form field count/layout inside a popup | NO | form-cro |
| Page-level layout, hero, above-the-fold | NO | page-cro |
| Signup flow multi-step optimization | NO | signup-flow-cro |
| A/B test design, sample size, significance | NO | ab-test-setup |
| Post-conversion drip/nurture emails | NO | email-sequence |
| Onboarding flows after signup | NO | onboarding-cro |

---

## Popup Type Decision Matrix

First-match by primary goal:

| Goal | Format | Trigger | Why This Combination |
|---|---|---|---|
| Email capture | Center modal | 50% scroll OR 45s delay | Entry popups convert 2-3% but generate 60% of popup complaints. Scroll/time proves engagement first -- same conversion, fewer complaints |
| Lead magnet delivery | Click-triggered modal | User clicks CTA | Self-selected intent = 10-25% conversion vs 2-5% for interruption popups. The user already wants the content |
| Exit save (e-commerce) | Exit intent modal | Cursor leaves viewport | Must offer something DIFFERENT than any entry popup. If entry was 10% off, exit should be free shipping or bundle deal |
| Discount/promo (first purchase) | Bottom bar or slide-in | 30s delay or 2nd page | Center modals for discounts feel desperate. Bottom bars feel like a courtesy ("btw, there's a code") |
| Announcement (feature, sale, event) | Top sticky bar | Immediate, always visible | Does not interrupt. Stays available. Dismissable. No conversion penalty because it's not blocking anything |
| Feedback/survey | Bottom-right slide-in | Engagement threshold (3+ pages or 2+ min) | Must earn the right to ask. Surveying bounced visitors wastes their time and your data |
| Webinar/event registration | Full-width banner below header | Page load, time-limited | Banner format signals urgency without modal interruption. Remove after event date -- stale banners erode trust |

### Multi-Popup Priority Queue

When a site has multiple popup types, conflicts WILL occur. Rules:

1. Never show 2 popups in one session. Period. Use a priority queue.
2. Priority order: exit-intent > behavior-triggered > scroll/time > page-load
3. If visitor qualifies for multiple popups, show the highest-intent one only
4. Suppress ALL popups for visitors who already converted (check cookie/localStorage + server-side)
5. Cart abandonment popup supersedes all others -- active purchase intent trumps list building

---

## Trigger Timing Decision

The trigger decision has more impact on conversion than copy, design, or offer combined.

| Trigger | When to Use | Conversion Range | Critical Rule |
|---|---|---|---|
| Time-delay | General list building, returning visitors | 2-5% | Minimum 30s. Under 15s triggers hostile dismissal -- users mentally categorize the site as "spammy" and this perception persists across return visits |
| Scroll depth | Content pages, blogs, long-form | 3-6% | 40-60% for articles. On product pages, 25% scroll often means they've passed the fold -- adjust per page type |
| Exit intent | E-commerce, lead gen, SaaS trials | 3-10% | Desktop ONLY. The `mouseout` event fires when cursor moves toward browser chrome. On mobile, this event does not exist |
| Click-triggered | Lead magnets, gated content, demos | 10-25% | Highest conversion because user self-selects. Should be the DEFAULT for any downloadable content |
| Page count | Research/comparison behavior | 4-8% | 3+ pages indicates research intent. Message should match: "Still comparing?" not "Subscribe!" |
| Behavior-based | Cart abandonment, pricing revisit, repeated category browsing | 5-15% | Highest intent signals. Cart abandonment: show once per cart session, not per page. Pricing revisit: "Questions about plans?" with chat or demo CTA |

### Mobile Trigger Alternatives

Exit intent is impossible on mobile (no cursor). Alternatives ranked by reliability:

1. **Scroll-up velocity**: User scrolls up quickly = searching for navigation to leave. Threshold: 300px upward in <500ms
2. **Tab visibility change**: `document.visibilitychange` event fires when user switches tabs. Show popup on return ("Welcome back")
3. **Page idle timeout**: No interaction for 60s+ on a mobile page suggests distraction or intent to leave
4. **Back button intercept**: `popstate` event. Use SPARINGLY -- intercepting back-button is hostile on mobile and banned by some app stores

---

## Google Interstitial Compliance

Google's "intrusive interstitials" penalty (active since January 2017, expanded 2024) specifically targets mobile:

**Penalized (affects mobile ranking):**
- Full-screen popup on mobile before user interacts with content
- Modal that must be dismissed before content is readable
- Above-the-fold layout where popup pushes content below the fold

**NOT penalized (safe):**
- Cookie consent and age verification (legal obligation exemption)
- Login dialogs for paywalled content
- Banners using "reasonable amount of screen space" (Google's language -- interpreted as <15% viewport)
- ANY popup triggered AFTER first user interaction (scroll, click, 30s+ delay)

**The workaround every CRO tool uses:** Delay popup until after first scroll or click event. This satisfies Google's "before user interaction" criterion while still capturing most visitors. Time-based delay of 30s+ also appears to satisfy the policy based on observed ranking behavior, though Google has not explicitly confirmed a time threshold.

---

## Popup Frequency Logic

Frequency mismanagement is the #1 source of popup complaints and the easiest fix in CRO.

| Visitor State | Frequency Rule | Implementation |
|---|---|---|
| First-time visitor | Max 1 popup per session | `sessionStorage` flag, cleared on tab close |
| Dismissed popup | 7-14 day cooldown before showing again | `localStorage` with timestamp. 7 days for high-value offers, 14 days for newsletters |
| Submitted/converted | Suppress ALL capture popups permanently | Server-side flag tied to email/account. localStorage alone fails on device switch or clear |
| Multiple popup types exist | Priority queue: show only the highest-priority one per session | Central popup manager that checks queue before firing any popup |
| Cart abandonment | Once per cart, not per page | Flag tied to cart ID. Reset only when cart contents change or cart is emptied |
| Returning subscriber | Show ONLY announcement bars, never capture popups | Check subscription status server-side. Showing "Subscribe!" to subscribers is insulting |

### The localStorage Problem

localStorage-only frequency tracking has three failure modes:
1. **Private/incognito browsing**: localStorage is session-scoped, user sees popup every incognito session
2. **Multiple devices**: User who subscribed on desktop sees capture popup on mobile
3. **Cache clearing**: Power users who clear cookies/storage see popups repeatedly

Solution: Dual tracking. localStorage for immediate suppression + server-side check against email/account database for converted users. For non-converted visitors, localStorage is sufficient -- the worst case is showing a popup again after 30 days to someone who dismissed it.

---

## Popup vs. Inline Decision

Not every conversion point should be a popup. Popups interrupt -- sometimes that's good (jolting passive readers), sometimes it's destructive (blocking active buyers).

| Page Context | Popup? | Instead Use | Why |
|---|---|---|---|
| High-intent page (pricing, demo, trial) | NO | Inline form or CTA on-page | Visitor is already converting. A popup interrupts the flow they chose. Inline form conversion is 15-30% on pricing pages -- popups can't beat that AND they add friction |
| Blog / content page | YES (scroll-triggered) | - | Readers need a nudge. Without interruption, blog-to-subscriber rate is typically <0.5% |
| Product listing / category page | Bottom bar or slide-in ONLY | - | Center modals block product browsing. Users came to shop, not subscribe. A quiet bottom bar captures without blocking |
| Checkout flow | NEVER | - | Any interruption during checkout = cart abandonment. Even a "helpful" popup ("Add gift wrapping?") increases drop-off by 3-8% |
| Landing page with single CTA | NO | - | The entire page IS the conversion mechanism. A popup competes with the page's own CTA and splits attention |
| Homepage | Depends on homepage role | Bottom bar for e-commerce, scroll-triggered modal for content sites | Homepages with high bounce (50%+) benefit from a delayed popup. Homepages with low bounce (engaged visitors) don't need interruption |

---

## Popup Copy Anti-Patterns

Named patterns practitioners encounter repeatedly:

| Anti-Pattern | Example | Why It Fails | Fix |
|---|---|---|---|
| **Guilt Trip Close** | "No, I hate saving money" | Manipulative. Classified as dark pattern under EU Digital Services Act. Users screenshot and share on social media | Neutral decline: "No thanks" or "Maybe later" |
| **Value Vacuum** | "Subscribe to our newsletter" | Zero benefit stated. Newsletter is a delivery mechanism, not a value proposition | State the benefit: "Get weekly pricing alerts for products you've browsed" |
| **Urgency Theater** | "Only 2 left!" on digital products | Fake scarcity destroys trust when users can verify. Even on physical products, "only X left" is now assumed fake | Use real deadlines: "Sale ends March 15" with actual date |
| **Wall of Text** | 3+ sentences in popup body | Users don't read popups, they scan. Eye-tracking shows <2 seconds before dismiss decision | Max: headline (6-8 words) + one supporting line + CTA |
| **Double Interrupt** | Popup fires while cookie consent banner is visible | User is already processing one overlay. Two simultaneous overlays feel hostile | Queue popups behind consent banner. Fire popup only after consent banner is dismissed or accepted |
| **Bait-and-Switch Offer** | "Get 20% off!" but the code only works on select items or orders over $100 | First impression of the brand is deception. Refund/chargeback rates spike | Honor the offer as presented. If conditions exist, state them IN the popup |
| **Infinite Loop Dismiss** | Clicking X reveals a "Are you sure?" confirmation popup | Users feel trapped. Mobile users may force-close the browser tab entirely | One X click = gone. No confirmation. Respect the dismiss |

---

## Rationalization Safeguards

| Request | Real Answer |
|---|---|
| "Show the popup on page load for maximum impressions" | Page-load popups have the highest dismiss rate (85%+) and trigger Google's mobile penalty. Delay to first interaction for same conversion at 60% fewer complaints |
| "Let's add a popup to the checkout flow" | Any interruption during checkout increases abandonment by 3-8%. The checkout flow should have ZERO popups. Use post-purchase thank-you page instead |
| "We need popups on every page" | Popup fatigue is cumulative across sessions. Sites with popups on every page see 40% higher bounce rates. Limit to 2-3 page types max |
| "The exit intent popup should be full-screen on mobile" | Exit intent doesn't work on mobile (no cursor event). Full-screen mobile popups trigger Google's ranking penalty. Use bottom sheet at 50% viewport max |
| "Show the same popup again if they dismissed it" | Showing a dismissed popup again in the same session is the single most reported UX complaint in popup tools (OptinMonster, Sumo, Privy support data). 7-day minimum cooldown |
| "We should use a countdown timer to create urgency" | Real deadlines work. Fake timers that reset on page refresh are detected by users within 2 visits and destroy trust permanently. Only use if the deadline is real |

## Red Flags

1. Popup fires before any user interaction on mobile (Google penalty risk)
2. No frequency capping -- same popup shown every visit or every page
3. Multiple popups can fire in the same session with no priority queue
4. Converted/subscribed users still see capture popups
5. Exit intent strategy deployed on mobile without alternative trigger
6. Full-screen modal on mobile blocking content access
7. Guilt-trip decline text or confirmation popup after dismiss
8. Popup appears during active checkout or payment flow

## NEVER

1. Never show a popup during checkout, payment, or form submission flows
2. Never show the same popup twice in a single session regardless of page navigation
3. Never use exit intent as-is on mobile -- it does not exist as a browser event
4. Never display a full-screen interstitial on mobile before user interaction
5. Never show capture popups to users who have already converted/subscribed
