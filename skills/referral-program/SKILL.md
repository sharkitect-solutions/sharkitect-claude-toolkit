---
name: referral-program
description: "Use when designing referral programs, affiliate programs, or word-of-mouth growth loops. Also use when the user mentions referral incentive structure, viral coefficient modeling, affiliate commission design, referral fraud prevention, or ambassador programs. NEVER use for email nurture sequences (email-sequence), psychological persuasion principles (marketing-psychology), pricing model design (pricing-strategy), or launch execution planning (launch-strategy)."
version: "2.0"
optimized: true
optimized_date: "2026-03-12"
---

# Referral & Affiliate Programs

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Program type decision, incentive structure, viral coefficient, referral timing, fraud prevention, anti-patterns | Always (auto-loaded) |
| fraud-prevention-playbook.md | Sophisticated fraud patterns (referral rings, coupon hijacking, attribution gaming), device fingerprinting approaches, payout delay strategies, verification tier selection, fraud cost modeling | When designing fraud prevention for a referral program, investigating suspicious referral patterns, or choosing verification strictness level |
| platform-selection-guide.md | Platform comparison (ReferralCandy, GrowSurf, Viral Loops, PartnerStack, Rewardful, custom build), Stripe integration patterns, attribution window gotchas, migration considerations, build-vs-buy decision framework | When choosing a referral/affiliate platform, evaluating build-vs-buy for referral tracking, or migrating between referral tools |
| referral-analytics-optimization.md | K-factor decomposition methodology, cohort analysis for referred vs organic customers, A/B test framework for incentives (minimum sample sizes, test duration), industry benchmarks by vertical, program health scorecard | When measuring referral program performance, designing referral A/B tests, or diagnosing why a referral program is underperforming |

Do NOT load companion files for basic program type decisions, incentive sizing, or anti-pattern reference -- SKILL.md covers these fully.

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| Referral program architecture and incentive design | YES | -- |
| Affiliate program commission structure | YES | -- |
| Viral coefficient modeling and K-factor analysis | YES | -- |
| Referral timing and trigger moment selection | YES | -- |
| Referral fraud detection and prevention | YES | -- |
| Email nurture sequences for referral campaigns | NO | email-sequence |
| Psychological persuasion principles (reciprocity, social proof) | NO | marketing-psychology |
| Pricing model design and monetization strategy | NO | pricing-strategy |
| Product launch execution and channel strategy | NO | launch-strategy |
| Analytics tracking implementation (UTM, events) | NO | analytics-tracking |
| Landing page conversion optimization | NO | page-cro |
| A/B test statistical design | NO | ab-test-setup |

## Program Type Decision

Answer these questions in order. First match determines program type.

| Signal | Program Type | Why |
|---|---|---|
| Product naturally involves others (collaboration, sharing) | Customer referral | Network effects create organic sharing. Referral program amplifies existing behavior |
| Need to reach audiences you don't have access to | Affiliate | Affiliates bring their own audience. You're buying distribution, not amplifying existing word-of-mouth |
| High-ticket product (>$500 ACV) with long sales cycles | Affiliate | Justifies commission economics. Customer referrals work poorly for products friends don't personally use |
| Product has strong NPS (>50) and natural word-of-mouth | Customer referral | High NPS = customers already recommend you. Program adds incentive to existing behavior |
| Low NPS (<30) but need growth | Fix the product first | Referral programs amplify satisfaction. If customers aren't happy, paying them to refer creates resentment and low-quality referrals |
| Want both customer sharing AND partner distribution | Hybrid (separate programs) | Run a simple customer referral (small rewards) AND a structured affiliate (commissions). Never combine into one program -- incentives and management differ completely |

**The Referral Program Paradox**: Products that need referral programs most (low organic sharing) benefit least. If customers don't naturally talk about your product, a referral program won't fix that -- it creates mercenary referrers who game the system. Fix product-market fit first.

## Incentive Structure Decision

| Decision | Default | Override When |
|---|---|---|
| Single-sided vs double-sided | Double-sided (both parties rewarded). Friendbuy data: 35% higher conversion than single-sided | Single-sided for enterprise (referred party gets a demo, not a discount) or when referred party already has strong motivation |
| Cash vs product credit | Product credit. Lower cost to you + drives engagement. Cash attracts fraudsters and mercenary referrers | Cash for marketplaces where product credit doesn't apply, or when product credit value is ambiguous |
| Immediate vs delayed reward | Delayed (after referred user activates/purchases). Reduces fraud by 60-80% | Immediate only for very low-value rewards (<$5) where fraud cost is negligible |
| Flat vs tiered rewards | Flat for launch (simplicity). Tiered after 90 days if you want to increase referrer engagement | Tiered from day 1 only if you have a large existing user base (>10K) and can afford the complexity |
| Reward amount | 10-20% of first-year revenue per referred customer. Never exceed 30% of gross margin on that customer | Higher for land-and-expand models where first-year revenue underrepresents LTV. Lower for high-volume/low-margin businesses |

### Incentive Sizing Formula

```
Max Referral Reward = (Customer LTV x Gross Margin) - Target CAC
Recommended Reward = Max Referral Reward x 0.3 to 0.5 (split between both sides)
```

| Business Model | Typical Referrer Reward | Typical Referred Reward | Notes |
|---|---|---|---|
| B2C SaaS ($20-50/month) | 1 month free or $20-50 credit | 1 month free or 20% off first 3 months | Product credit preferred. Keeps both users engaged |
| B2B SaaS ($200-2000/month) | $100-500 credit or 1-3 months free | Extended trial or first month free | Referred reward should reduce purchase friction, not just save money |
| E-commerce (AOV $50-200) | $10-25 store credit | $10-15 off first order or free shipping | Store credit drives repeat purchase. Don't do % discount (feels small on low AOV) |
| Marketplace | $10-25 credit | $10-20 credit for first transaction | Both sides need credit because marketplace requires both supply and demand |
| Enterprise ($10K+ ACV) | Custom (gift cards, exclusive access) | None (they get a demo) | Enterprise referrals are relationship-based, not incentive-driven. Reward is a thank-you, not a motivator |

## Viral Coefficient Reality Check

**K-factor formula**: K = (invitations per user) x (conversion rate per invitation)

| K Value | What It Means | How Common | Reality |
|---|---|---|---|
| K > 1.0 | True viral growth (each user brings >1 new user) | Extremely rare (<1% of programs) | Only happens in products with inherent network effects (messaging apps, collaboration tools). If someone promises K>1 for a non-network product, they're lying |
| K = 0.3-0.7 | Good amplification. Referrals supplement paid acquisition | Top 10% of programs | This is the realistic target. Each 10 customers bring 3-7 new customers. Meaningful CAC reduction |
| K = 0.1-0.3 | Modest contribution. Referrals are a channel, not a growth engine | Median outcome | Most referral programs land here. Still valuable if referral CAC < paid CAC |
| K < 0.1 | Program isn't working | Bottom 50% | Diagnose: low sharing rate (trigger/friction problem) or low conversion (landing page/incentive problem) |

**Benchmarks that actually matter**:
- Referral rate (% of customers who refer at least once): Good = 10-15%, Great = 15-25%, Exceptional = 25%+
- Referred customer LTV premium: Referred customers have 16-25% higher LTV and 18-37% lower churn (source: Wharton study, Schmitt et al. 2011). This is due to trust transfer + selection bias (people refer friends similar to themselves)
- Time to first referral: Median is 14-30 days after activation. If most referrals happen in first 7 days, you're capturing the "new toy" effect only

## Referral Timing Decision

When you ask matters more than what you offer. Referral prompts at wrong moments get ignored or create negative sentiment.

| Trigger Moment | Effectiveness | Why | Implementation |
|---|---|---|---|
| Right after first value moment ("aha") | HIGH | Customer just experienced value. Enthusiasm is peak. Social proof of value is fresh | Detect product milestone completion. Show referral prompt inline, not as modal popup |
| After positive NPS/CSAT response | VERY HIGH (3x baseline) | Customer just told you they're happy. Asking them to act on that sentiment works. NPS 9-10 respondents refer at 3-5x rate of 7-8 respondents | Trigger referral prompt immediately after NPS submission for scores 9-10 only |
| After support ticket resolution (positive) | HIGH | Gratitude + relief. Customer feels the team cares | Only for tickets resolved within SLA with positive feedback. Never after escalations |
| Random in-app prompt | LOW | No emotional context. Feels like spam. "Why are you asking me this right now?" | Avoid. If you must, limit to 1x per 30 days |
| In email drip sequence | MEDIUM | Scalable, but easy to ignore. Works better as a reminder than a first ask | Day 14 after activation. Include a specific reason ("You've created 5 projects -- your friends would love this") |
| At upgrade/renewal | MEDIUM-HIGH | Customer just committed to the product. Buying signals = sharing willingness | Best as a thank-you page element after payment confirmation, not as an upsell |

## Affiliate Commission Decisions

| Decision | Guidance |
|---|---|
| Commission model | Recurring revenue product = recurring commission (10-25% for 12 months). One-time purchase = flat fee or % of sale (15-30%). Lead gen = flat fee per qualified action ($20-500 depending on value) |
| Cookie duration | Match your sales cycle. 30 days for SaaS (most signups happen within 14 days). 60-90 days for enterprise. 7 days for impulse purchases. Longer cookies attract more affiliates but increase attribution disputes |
| Attribution model | Last-click is standard and simplest. First-click rewards discovery (favors content creators). Multi-touch is fairest but complex and creates disputes. Start with last-click, add first-click bonus for top affiliates |
| Minimum payout threshold | $50-100 minimum. Below $50 attracts low-quality affiliates. Above $100 discourages new affiliates. Monthly payouts standard, Net-30 for trust/fraud buffer |
| Exclusivity | Never require exclusivity for standard affiliates. Offer higher commission for exclusive partnerships (dedicated review, no competitor promotion). Exclusive partners should get 1.5-2x standard rate |

## Anti-Patterns

| Anti-Pattern | What Happens | Why It Fails | Fix |
|---|---|---|---|
| **The Bribe Program** | Massive rewards ($100+ for low-ACV product) to force referrals | Attracts mercenary referrers and fraudsters. Referred customers have no genuine interest. CAC via referral exceeds paid CAC. Fraud rate 30-50% | Size rewards at 10-20% of first-year revenue. Quality referrals come from product satisfaction, not bribe size |
| **The Hidden Link** | Referral program exists but nobody knows about it. Buried in settings or footer | <2% of customers discover it. Program looks like it "doesn't work" but was never given a chance | Surface referral at trigger moments (post-value, post-NPS). In-product placement, not just a settings page link |
| **The Complicated Math** | "Earn 500 points per referral! 10,000 points = $5 gift card!" | Nobody calculates point-to-value conversion. Feels like a scam. Points systems add friction without adding value | State rewards in real terms: "$20 credit" or "1 month free." No points, no conversions, no ambiguity |
| **The Premature Ask** | Referral prompt during onboarding, before user has experienced any value | User hasn't validated the product yet. Asking for referrals before trust is established feels presumptuous. Damages brand perception | Wait until first value moment. Minimum: 7 days active usage AND at least one core feature milestone completed |
| **The Generic Ask** | "Refer a friend!" with no context, no personalization, no specific reason | Gives the referrer nothing to say. "I got this generic popup" isn't a compelling reason to share. Conversion rate <0.5% | Personalize: "You've saved 12 hours this month. Know someone who'd love that?" Give referrers a story, not just a link |
| **The Infinite Reward** | No cap on referral rewards. Top referrer earns $50K/year gaming the system | Creates professional referrers who aren't customers. Attracts organized fraud rings. Budget becomes unpredictable | Cap at reasonable level (e.g., $5K/year per referrer). Review accounts exceeding 20 referrals/month manually |

### Rationalizations That Signal Bad Decisions

| Rationalization | Reality |
|---|---|
| "We'll just launch it and see what happens" | Referral programs without fraud prevention, timing strategy, and measurement get gamed within 2 weeks |
| "Everyone will refer if we pay them enough" | Money doesn't create word-of-mouth. Product quality does. High rewards attract fraudsters, not advocates |
| "We don't need fraud prevention yet" | Fraud appears within days of launch. Retrofitting prevention is 5x harder than building it in |
| "Let's copy Dropbox's referral program" | Dropbox had inherent virality (shared folders) + product-market fit. The program amplified existing sharing behavior. Copying the mechanic without the product dynamics fails |
| "Affiliates will just find us" | Quality affiliates are recruited, not attracted. Passive affiliate program pages get 95% low-quality applicants (coupon sites, spam blogs) |

### Red Flags

| Red Flag | Diagnosis |
|---|---|
| Referral rate >50% within first week of launch | Fraud or internal gaming, not organic sharing |
| Referred users churn faster than organic | Referrals are incentive-driven, not value-driven. Wrong audience being referred |
| Single referrer responsible for >20% of referrals | Either a power user (good) or a fraud ring operator (bad). Investigate before rewarding |
| Referral conversion rate >40% | Suspiciously high. Check for self-referrals, same-household referrals, or fake accounts |
| CAC via referral exceeds paid channel CAC | Rewards are too high, fraud is eating margin, or referred users aren't converting to paid |
| 90%+ of referrals come from coupon/deal sites | Your referral link leaked. These aren't referrals, they're discount seekers who would have purchased anyway |
| Most referrals happen within minutes of signup | Users are self-referring with alternate emails before engaging with product |

### NEVER

- Never launch a referral program without fraud prevention rules
- Never ask for referrals before the user has experienced core product value
- Never set referral rewards higher than 30% of gross margin per referred customer
- Never combine customer referral and affiliate programs into a single program
- Never use points systems when you can state rewards in real currency/product terms
