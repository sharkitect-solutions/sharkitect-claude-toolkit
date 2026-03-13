---
name: outreach-specialist
description: "Use when planning cold outreach campaigns, optimizing email deliverability, building prospect targeting strategies, managing sending infrastructure, designing follow-up sequences, or analyzing outreach performance. Use when the user mentions cold email, outreach, prospecting, lead generation campaigns, email warm-up, deliverability, or reply rates. NEVER for warm introductions or referral-based outreach. NEVER for email marketing to opted-in lists. NEVER for content marketing or social selling. NEVER for transactional email systems."
---

# Outreach Specialist

Claude's default cold outreach advice is generic -- "personalize your emails" and "follow up persistently" -- which produces 1-3% reply rates and deliverability problems. This skill teaches deliverability-first infrastructure decisions, diagnostic positioning over solution-selling, and micro-campaign targeting that achieves 2-5x industry reply rates. The difference is architectural, not cosmetic.

## The Outreach Architecture Decision Tree

Route every outreach project through these four decisions before writing a single email.

### 1. What's the offer type?

| Offer Type | Outreach Style | Email Length | CTA Design |
|---|---|---|---|
| Free diagnostic / consultation | Problem-awareness → curiosity gap → low-friction ask | 60-100 words | Calendar link or reply-to-book |
| Demo / trial | Specific outcome claim → social proof → time-bounded ask | 80-120 words | Direct demo link with fallback reply |
| Direct product / service | Pain-agitate → solution hint → qualification question | 80-130 words | Reply with qualifying answer |
| Content / event invite | Value preview → exclusivity signal → single CTA | 50-80 words | Registration link, no reply needed |

**Key rule:** Diagnostic offers outsell direct pitches 3:1 in cold outreach because they lower commitment and reframe the seller as advisor. Default to diagnostic unless the user has a specific reason not to.

### 2. What's the market segment?

| Segment | Decision Maker | Avg Response Window | Personalization Minimum |
|---|---|---|---|
| SMB (<50 employees) | Owner / GM | 24-72 hours | Industry-specific (Level 2) |
| Mid-market (50-500) | VP / Director | 48-96 hours | Role-specific (Level 3) |
| Enterprise (500+) | Individual contributor champion | 1-2 weeks | Account-specific (Level 4) |

**Scaling rule:** As company size increases, personalization depth must increase and volume must decrease. A 500-email SMB campaign can work at Level 2 personalization. A 500-email enterprise campaign at Level 2 will get 0 replies.

### 3. What's the volume tier?

| Volume | Emails/Campaign | Infrastructure Needed | Personalization Depth |
|---|---|---|---|
| Micro | <50 | Single domain, single account | Level 3-4 (role/account) |
| Scaled | 100-500 | 2-3 sending accounts, dedicated domain | Level 2-3 (industry/role) |
| High-volume | 500+ | Domain rotation, IP warming, multiple accounts | Level 2 minimum + dynamic variables |

**Critical:** High-volume only works with established infrastructure (30+ days warmed). Never launch high-volume from new domains -- deliverability will collapse within 48 hours.

### 4. What's the infrastructure state?

| State | Daily Limit | What to Do First |
|---|---|---|
| Brand new domains | 0 (not ready) | Set up authentication, begin warm-up ramp. See references/infrastructure-setup.md |
| Warming (days 1-14) | 10-25/account | Small micro-campaigns only, monitor every metric daily |
| Warming (days 15-30) | 25-40/account | Begin scaled campaigns, watch bounce rate closely |
| Established (30+ days, clean history) | 40-60/account | Full campaign operations, monitor weekly |
| Damaged reputation | 0 (pause all sends) | Diagnose cause, pause 7-14 days, restart warm-up |

## Deliverability-First Rules

These are the decisions where mistakes cost weeks or months to recover from. Infrastructure before copy, always.

1. **Authentication is non-negotiable.** SPF + DKIM + DMARC must all pass before sending a single cold email. Missing any one cuts inbox placement by 30-50%. See references/infrastructure-setup.md for configuration.
2. **Warm-up cannot be skipped or rushed.** The 30-day ramp exists because mailbox providers build sender reputation over time. Shortcuts trigger spam filters that take longer to clear than the warm-up itself.
3. **50 emails/day/account is the ceiling for Google Workspace.** At 51+, Google's rate limiting activates unpredictably. Microsoft 365 allows ~80/day but flags patterns faster.
4. **Bounce rate above 4% is an emergency.** Stop all sends immediately. Audit the list. Every bounce degrades domain reputation and the damage compounds -- a 6% bounce day can take 2 weeks to recover from.
5. **Spam complaint threshold is 0.1%.** One complaint per 1,000 emails. Above this, inbox placement drops across ALL campaigns on that domain, not just the offending one.
6. **Plain text outperforms HTML in cold email.** No images, no HTML formatting, no multiple links. One link maximum. Tracking pixels are acceptable but reduce deliverability by ~5%.
7. **Never send cold email from your primary business domain.** Use a dedicated outreach domain (e.g., company-reach.com instead of company.com). If the outreach domain gets burned, your business email is unaffected.

## Targeting Precision Framework

Why micro-campaigns beat blast campaigns: a 50-contact campaign with Level 3 personalization produces 2.76x the reply rate of a 500-contact campaign with Level 1 personalization. The math always favors precision.

### Personalization Depth Levels

| Level | What's Personalized | Time per Email | Expected Reply Lift |
|---|---|---|---|
| Level 1: Spray | Name + company only | 0 (automated) | Baseline (2-3%) |
| Level 2: Industry | Industry-specific pain points, seasonal context | 30 sec | 1.5-2x baseline |
| Level 3: Role | Role-specific language, title-aware framing, company-size context | 1-2 min | 2.5-3.5x baseline |
| Level 4: Account | Company-specific research, recent news/events, mutual connections | 5-10 min | 4-6x baseline |

**Decision rule:** Spend personalization time where deal size justifies it. $500 ACV = Level 2 max. $5K ACV = Level 3. $50K+ ACV = Level 4.

### ICP-to-Campaign Flow

1. Define ICP: industry + company size + role + geography + qualifying signal
2. Build niche list: one industry-role combination per micro-campaign (never mix)
3. Score leads: verified email + decision-maker confirmed + enrichment data available
4. Disqualify ruthlessly: no generic emails (info@, contact@), no unverifiable addresses, no companies outside ICP
5. Cap campaign size: 25-50 for micro, 100-200 for scaled, split into batches for high-volume

## Email Copy Architecture

These are structural rules, not templates. Templates are in references/campaign-templates.md.

**The 4 rules that separate 3% reply-rate emails from 15% reply-rate emails:**

1. **60-120 words maximum.** Every word above 120 reduces reply probability. Cold emails are not the place to educate -- they earn the right to a conversation.
2. **3rd-5th grade reading level.** Short sentences. Common words. No jargon unless the recipient uses that exact jargon daily. Tools: Hemingway App or readability-score.com.
3. **One CTA, stated once.** "Would a 15-minute call this week make sense?" not "Book a demo OR reply OR visit our site OR download our whitepaper." Multiple CTAs produce zero action.
4. **Subject lines that look internal.** 2-4 words that could be an internal memo subject: "quick question", "scheduling idea", "[first name] - timing". Never salesy subjects ("Exclusive offer!", "Don't miss out!").

**Follow-up architecture:** See references/campaign-templates.md for full sequence frameworks. The key principle: each follow-up must introduce a genuinely new angle (proof, data, different pain point). Never reference the previous email ("Just following up on my last email...").

## Anti-Pattern Decision Table

| Anti-Pattern | Why It Fails | What To Do Instead |
|---|---|---|
| Sending 200+ emails from a 1-week-old domain | Triggers spam filters immediately, domain may be permanently flagged | Follow 30-day warm-up ramp, start at 10-20/day |
| "Just checking in" follow-ups | Adds zero value, trained as spam signal by filters and humans | Each follow-up introduces new proof, angle, or value |
| HTML-heavy emails with images and buttons | Cold email filters penalize formatting complexity; looks like marketing blast | Plain text, one link max, conversational tone |
| Mixing industries in one campaign | Prevents meaningful A/B testing; generic copy underperforms niche copy | One industry-role combination per micro-campaign |
| Buying pre-built email lists | 20-40% invalid rate typical; destroys bounce rate and domain reputation | Build lists from verified sources, validate every address before send |
| Solution-selling in the first email | Prospect hasn't confirmed the problem exists; feels presumptuous | Lead with problem awareness, offer diagnosis |
| Sending same email copy for 30+ days | Mailbox providers detect repeated content patterns and flag as spam | Rotate copy every 2 weeks, maintain 3-4 active variants |
| Skipping email verification | Even "good" lists have 5-15% invalid addresses that cause bounces | 3-tier verification: MX check, API verification, catch-all detection |
| Including unsubscribe link in cold email | Signals bulk sending to spam filters; cold email is not marketing email | Use breakup email as natural exit; honor opt-out replies immediately |
| Personalizing with obviously scraped data | "I saw your LinkedIn post from 2019..." feels surveillance, not relevance | Use timely signals: recent hires, funding, seasonal patterns |

## Rationalization Table

| Rationalization | When It Appears | Why It's Wrong |
|---|---|---|
| "We need more volume to see results" | Low reply rates after 2-3 weeks | Volume amplifies bad targeting. Fix targeting/copy first, then scale. |
| "Our emails are too short, we need to explain more" | Prospects not engaging | Length is not the problem. Relevance and positioning are. Longer cold emails perform worse. |
| "Let's add more links so they have options" | Low click-through rate | Multiple CTAs create decision paralysis. One clear ask outperforms every time. |
| "We should warm up faster, we're losing time" | Impatience during ramp period | Rushing warm-up risks the domain permanently. A 2-week shortcut can cost 2-month recovery. |
| "The list is fine, our copy must be bad" | High bounce rate (>4%) | List quality causes bounces, not copy. Verify the data before rewriting anything. |
| "Let's send from our main domain to look legitimate" | Low open rates from outreach domain | Burning your main domain destroys ALL business email. The outreach domain exists to absorb risk. |
| "We should follow up more aggressively" | No replies after sequence completes | Aggressive follow-up triggers spam complaints. Test new angles, not more frequency. |
| "Personalization takes too long at scale" | Scaling pressure | Then reduce volume to match personalization capacity. Unpersonalized scale produces negative ROI. |

## NEVER List

1. **NEVER send cold email without SPF + DKIM + DMARC all passing.** No exceptions, no "we'll set it up later."
2. **NEVER exceed 50 emails/day per Google Workspace account or 80 per Microsoft 365 account.**
3. **NEVER launch campaigns from a domain less than 14 days into warm-up.** Micro-campaigns only during warm-up.
4. **NEVER send to unverified email addresses.** Every address must pass verification before entering the send queue.
5. **NEVER include more than one external link in a cold email.** Each additional link increases spam score.
6. **NEVER reference previous emails in follow-ups** ("per my last email", "just circling back"). Each email stands alone.
7. **NEVER use the prospect's first name more than once in an email.** Repeated name insertion is an obvious automation tell.
8. **NEVER send identical copy to more than 50 recipients.** Mailbox providers detect duplicate content and flag it.
9. **NEVER continue sending when bounce rate exceeds 4%.** Stop immediately, audit, fix, then resume.
10. **NEVER pitch a solution before diagnosing the problem.** The first email earns a conversation, not a sale.

## Performance Diagnostic Framework

When campaign metrics are below benchmarks (see references/outreach-benchmarks.md), diagnose in this exact order. Each layer must be healthy before the next matters.

```
Layer 1: DELIVERABILITY (are emails reaching inboxes?)
  Check: inbox placement rate, bounce rate, spam folder rate
  Fix: authentication, warm-up status, sending volume, list quality
  |
Layer 2: TARGETING (are the right people receiving emails?)
  Check: ICP match rate, title accuracy, company fit
  Fix: list source, enrichment quality, qualification criteria
  |
Layer 3: COPY (is the message compelling?)
  Check: open rate (subject line), reply rate (body + CTA)
  Fix: subject line testing, body length, CTA clarity, reading level
  |
Layer 4: TIMING (is the send time optimal?)
  Check: open rate by day/time, industry work patterns
  Fix: send window adjustment, timezone targeting, seasonal factors
```

**Critical rule:** If Layer 1 is broken, do NOT touch Layers 2-4. Rewriting copy when emails land in spam is wasted effort. Fix infrastructure first, measure again, then move up the stack.
