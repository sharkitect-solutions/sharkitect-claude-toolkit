# Dark Pattern Regulations by Jurisdiction

Load when the user's marketing targets EU, UK, California, or FTC-regulated markets, when reviewing psychological tactics for compliance, when the user asks "is this legal?", or when recommending urgency/scarcity/default tactics that may cross regulatory lines. Do NOT load for general psychology principle selection or when the user is not concerned about compliance.

## What Counts as a Dark Pattern

Dark patterns are interface designs that trick users into actions they didn't intend. The term was coined by Harry Brignull (2010) and has since been codified into law across multiple jurisdictions.

### Dark Pattern Taxonomy (Regulatory Definitions)

| Pattern Type | Description | Common Marketing Examples | Jurisdictions That Explicitly Ban It |
|---|---|---|---|
| **Confirmshaming** | Guilt-tripping users who decline | "No, I hate saving money" decline text | EU DSA (Article 25, Recital 67), India DPDP Act 2023 |
| **Forced continuity** | Auto-renewing without clear notice, making cancellation difficult | Trial converts to paid with no reminder email, cancellation requires phone call during business hours | FTC Negative Option Rule (2024), California ARL, EU Consumer Rights Directive |
| **Hidden costs** | Revealing fees late in the checkout process | "Service fee" appearing only at payment step, mandatory "processing fee" added after price commitment | FTC (drip pricing enforcement), EU Consumer Rights Directive, UK Consumer Protection Act |
| **Misdirection** | Using visual hierarchy to steer toward the more profitable option | "Accept all cookies" as large green button, "Manage preferences" as tiny gray text | EU DSA, GDPR (CNIL: 150M euro fine against Google, 2022), EDPB Cookie Banner Taskforce |
| **Nagging** | Repeated interruptions to pressure action | Popup reappearing after dismissal, daily "upgrade" notifications, modal on every page visit | EU DSA, India DPDP Act |
| **Obstruction** | Making unwanted actions deliberately difficult | 1-click signup but 12-step cancellation, "contact us to cancel" with no self-service option | FTC Click-to-Cancel Rule (2024), California ARL, EU Consumer Rights Directive |
| **Trick questions** | Confusing language that reverses expected meaning | "Uncheck to not unsubscribe from non-marketing emails" (double/triple negative) | EU DSA, UK Consumer Protection from Unfair Trading Regulations |
| **Bait and switch** | Advertising one thing, delivering another | "Free" tool that requires payment for any useful feature, "50% off" that only applies to first month | FTC Act Section 5, state consumer protection laws, EU Unfair Commercial Practices Directive |
| **Roach motel** | Easy to get into, hard to get out | Easy signup, hidden cancellation, loyalty programs with no clear redemption path | FTC Click-to-Cancel Rule (2024), GDPR right to withdraw consent, California ARL |

## Jurisdiction-Specific Rules

### European Union: Digital Services Act (DSA) -- Effective Feb 2024

| DSA Provision | What It Prohibits | Marketing Impact | Penalty |
|---|---|---|---|
| Article 25(1) | Designing interfaces that "distort or impair" users' ability to make free and informed decisions | Guilt-trip decline text, misdirecting visual hierarchy for cookie consent, nagging popups | Up to 6% of global annual turnover for Very Large Online Platforms (VLOPs). Smaller platforms: member state enforcement |
| Article 25(2) | Giving "disproportionate prominence" to one choice over another | "Accept all" large and green vs "Reject" small and gray on consent banners | Same as above |
| Article 25(3) | Making service cancellation "significantly more difficult" than subscribing | If signup is 2 clicks, cancellation must be comparably easy. No mandatory phone calls, no multi-page "are you sure?" flows | Same as above |
| Recital 67 | Explicitly names dark patterns: "confirmshaming", "making certain choices more difficult", "nagging", "making the procedure for cancelling a service significantly longer" | Direct regulatory definition of the patterns marketers must avoid | Interpretive guidance for Articles 25 |

### United States: FTC Enforcement

| FTC Action | What It Targets | Key Precedent | Marketing Impact |
|---|---|---|---|
| **Click-to-Cancel Rule (2024)** | Cancellation must be as easy as signup. If you can subscribe online, you must be able to cancel online | FTC v. Amazon (Prime cancellation), FTC v. ABCmouse | No "call to cancel." No mandatory retention offers before cancellation is processed. No hiding the cancel button |
| **Negative Option Rule (amended 2024)** | Free trials that auto-convert must: (1) clearly disclose terms before billing info collection, (2) obtain express informed consent, (3) send reminder before first charge | FTC v. Vonage, FTC v. Publishers Clearing House | Pre-trial disclosure must be "clear and conspicuous" -- not in fine print, not behind a hyperlink. Reminder email required before first charge |
| **FTC Act Section 5** | Prohibits "unfair or deceptive acts or practices" | FTC v. Wyndham (privacy), FTC v. Epic Games ($520M for dark patterns in Fortnite) | Broad authority. Any marketing practice that a "reasonable consumer" would find deceptive is potentially actionable |
| **Drip Pricing Enforcement (2024-2025)** | All-in pricing: mandatory fees must be included in advertised price | FTC proposed rule on junk fees (hotel resort fees, event ticket fees) | SaaS: "Starting at $49/mo" is fine if $49 is the actual price. "$49/mo + $10 platform fee" in checkout is drip pricing |

### California

| Law | What It Requires | Marketing Impact |
|---|---|---|
| **California Auto-Renewal Law (ARL)** | Clear disclosure of auto-renewal terms, easy cancellation, acknowledgment of consent | "I agree to auto-renewal at $X/period" must be presented clearly. Cancel button must be accessible without contacting support |
| **CCPA/CPRA** | "Do Not Sell or Share" link must be prominent. Financial incentives for data sharing must be disclosed | Discount-for-email popups are "financial incentives" under CCPA. Must disclose value of consumer data and allow withdrawal |
| **California Privacy Rights Act (CPRA)** | Global Privacy Control (GPC) browser signal must be honored as opt-out | Do NOT show "consent to tracking" popups to users sending GPC signal. Browser has already communicated their choice |

### United Kingdom

| Law | What It Requires | Marketing Impact |
|---|---|---|
| **Consumer Protection from Unfair Trading Regulations 2008** | Prohibits misleading actions, misleading omissions, and aggressive commercial practices | False urgency ("Only 2 left" when untrue), omitting material information (hidden fees), high-pressure sales tactics |
| **UK GDPR + PECR** | Cookie consent requirements similar to EU. ICO enforces | Cookie banners must offer genuine choice. "Accept all" default with hidden reject is non-compliant |
| **Digital Markets, Competition and Consumers Act 2024** | New powers for CMA to directly enforce against dark patterns, fake reviews, subscription traps | CMA can impose fines up to 10% of global turnover for fake reviews, drip pricing, and subscription traps |

## Compliance Checklist for Psychological Marketing Tactics

| Tactic | Compliance Check | Risk Level |
|---|---|---|
| **Countdown timer** | Is the deadline real? Does it reset on refresh? A resetting timer is deceptive in ALL jurisdictions | HIGH if fabricated. FTC Act Section 5, EU Unfair Commercial Practices Directive |
| **"Only X left" badge** | Is the number accurate and updated in real time? Does it apply to digital products? | HIGH if false. Moderate if true but applied to digital (misleading) |
| **Guilt-trip decline text** | Does the decline option use neutral language ("No thanks")? | HIGH in EU (DSA explicitly bans confirmshaming). Moderate in US (FTC has not specifically targeted this yet, but brand risk is high) |
| **Pre-checked add-ons** | Is the add-on genuinely beneficial? Is it visible before purchase? | HIGH. FTC Negative Option Rule, EU consumer rights prohibit pre-checked boxes for paid add-ons |
| **Auto-renewal** | Is renewal disclosed before billing info? Is cancellation easy? Is a reminder sent? | MEDIUM-HIGH. California ARL, FTC Click-to-Cancel, EU Consumer Rights Directive all have specific requirements |
| **Loss framing** | Is the stated loss real and verifiable? Or speculative? | LOW if truthful ("Your discount expires Friday" when it genuinely does). HIGH if fabricated or grossly exaggerated |
| **Social proof numbers** | Are user counts, review scores, and testimonials accurate and current? | MEDIUM. FTC endorsement guidelines require that testimonials reflect typical experience. Atypical results must be disclosed |
| **Default plan selection** | Does the default serve the user's likely needs? Or is it the most expensive option? | MEDIUM. EU DSA + FTC unfairness doctrine. Pre-selecting the most expensive option without stated reason is risky |
| **Free trial design** | Is the transition to paid clearly disclosed? Can users cancel before being charged? | HIGH. FTC Negative Option Rule is specifically designed for this. Violations result in monetary penalties + mandated refunds |
| **Price anchoring** | Is the "was" price a real historical price? Was it actually sold at that price for a reasonable period? | MEDIUM-HIGH. FTC and state AGs (notably California, New York) have sued retailers for fictitious "was" prices. Must have been offered at anchor price for a meaningful period |

## Safe Patterns: Compliant Alternatives

| Instead of This | Do This | Why It's Compliant |
|---|---|---|
| Countdown timer that resets | Real deadline with specific date: "Sale ends March 15 at midnight EST" | Truthful time constraint, doesn't reset, verifiable |
| "Only 3 left!!!" on digital | "Limited to first 100 enrollees for live Q&A access" | Genuine scarcity tied to a real constraint (instructor capacity) |
| "No, I don't care about my health" | "No thanks" or "Maybe later" | Neutral decline language, no guilt, DSA compliant |
| Pre-checked premium add-on | Unchecked add-on with clear benefit: "Add priority support ($9/mo) -- average response time: 2 hours vs 24 hours" | Informed choice with quantified benefit, not pre-selected |
| Hidden auto-renewal | Clear disclosure: "Renews at $X/year on [date]. Cancel anytime at [direct link]" | Full transparency, easy cancellation, ARL/FTC compliant |
| "$49/mo + platform fee" at checkout | "$59/mo" (all-inclusive) on the pricing page | All-in pricing eliminates drip pricing risk |
| Crossed-out fictitious price | Show competitor pricing or category average: "Category average: $99/mo. Our price: $49/mo" | Truthful comparison rather than fabricated anchor |
