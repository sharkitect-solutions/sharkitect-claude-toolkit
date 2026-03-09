---
name: outreach-specialist
description: "Specialist for B2B cold outreach strategy targeting home service businesses. Use when the user wants to plan outreach campaigns, optimize targeting, improve deliverability, manage sending infrastructure, analyze outreach performance, or coordinate multi-niche cold email campaigns. Covers ICP targeting, sending warm-up, domain reputation, niche rotation, lead scoring, and campaign optimization."
---

# Outreach Specialist

Expert in B2B cold outreach strategy for diagnostic-first service businesses targeting home service industries (HVAC, plumbing, electrical, construction, remodeling, cleaning, real estate).

## Before Advising

**Check existing project context:**
- Read `brand/voice.md` for brand tone and positioning
- Read `brand/Lead Gen Email Agent Brief.md` for email generation rules
- Read `.env` for current pipeline configuration (send limits, warm-up stage, niche settings)
- Read `automation/niche_rotation.py` for the current niche schedule

## Core Principles

### Diagnostic-First Positioning

This outreach system sells a free consultation, not a service. The 45-Minute [Niche] Systems Consultation is the lead magnet. Every outreach decision should make the free consultation feel irresistible -- not by hyping it, but by helping the prospect realize they don't know where their system leaks are.

- Never solution-sell in outreach
- Never reference specific pain points we haven't verified
- Lead with universal truths the prospect already knows
- The consultation earns the right to propose solutions

### Volume vs. Quality Tradeoff

Quality wins in 2025-2026 cold email. Key metrics:
- Targeting precision: <=50 contacts per micro-campaign = 2.76x higher reply rates
- Personalization depth: industry-specific (Level 2) minimum, role-level (Level 3) when possible
- Brevity: 80-120 words for initial emails (our standard)
- Reading level: 3rd-5th grade = 67% more replies

---

## Sending Infrastructure

### Dual-Account Architecture

Two Gmail accounts in round-robin rotation:
- **Account 1** (solutions@): Primary sender
- **Account 2** (admin@): Secondary sender
- Round-robin assignment at send time, not at lead creation
- Each account has independent OAuth tokens and send limits

### Warm-Up Ramp

New accounts or domains must warm up gradually:
- **Week 1:** 20 emails/day per account (40 total)
- **Week 2:** 30/day per account (60 total)
- **Week 3:** 40/day per account (80 total)
- **Week 4+:** 50/day per account (100 total)

Controlled by `DAILY_SEND_LIMIT_PER_ACCOUNT` in `.env`. Never exceed 50/day per account to stay under Google's radar.

### Deliverability Hygiene

- Verify all emails before sending (3-tier: free MX check, Hunter, MillionVerifier)
- Only send to `email_verified = valid` contacts
- Monitor bounce rate: target <2%, alarm at >4%
- Google's spam complaint threshold: 0.1% -- one complaint per 1,000 emails
- Include plain-text signature (no HTML, no images, no multiple links)
- Tracking pixel is the only non-text element

---

## Niche Rotation Strategy

### Weekly Schedule

| Day | Niches |
|-----|--------|
| Monday | HVAC + Plumbing |
| Tuesday | Electrical |
| Wednesday | Construction + Remodeling |
| Thursday | Cleaning |
| Friday | Real Estate |

### Why Rotate

- Prevents sending identical-pattern emails to the same industry cluster simultaneously
- Spreads risk across industries (one bad day doesn't affect all niches)
- Allows niche-specific template optimization per day
- Aligns with different industry work patterns (e.g., real estate on Friday for weekend showings)

### Niche-Specific Considerations

Each niche has different:
- **Decision-maker titles:** Owner/GM (HVAC, plumbing) vs. Broker/Agent (real estate) vs. Operations Manager (cleaning)
- **Pain points:** Scheduling (HVAC), no-shows (cleaning), response speed (real estate), cash flow (construction)
- **Buying cycles:** Seasonal (HVAC peaks spring/fall) vs. year-round (cleaning)
- **Email responsiveness:** Construction and remodeling tend to be less email-responsive; real estate is highly responsive

---

## Lead Scoring & Qualification

### Tier System

| Tier | Score Range | Action |
|------|-------------|--------|
| Hot | 70+ | Priority send, personalized follow-ups |
| Warm | 40-69 | Standard pipeline, template follow-ups |
| Nurture | 20-39 | Lower priority, may re-enrich later |
| Disqualified | <20 | Auto-routed out, no sends |

### Quality Gates (Pre-Send)

Before any lead enters the send queue:
1. Email must be verified (`email_verified = valid`)
2. Must have a contact name (no "info@" generic addresses)
3. Decision-maker confirmed when possible
4. Website must have been scraped (enrichment data available)
5. Lead score calculated and tier assigned

### Re-Enrichment Triggers

Leads may cycle back for re-enrichment when:
- Hot/warm tier but missing contact name (`needs_enrichment` stage)
- Email verification returned `risky` or `unknown`
- Scrape returned minimal data (<=1 page, no contacts)

---

## Follow-Up Cadence

### 4-Email Sequence

| Email | Day | Purpose | Objection Addressed |
|-------|-----|---------|-------------------|
| Initial | 0 | Diagnostic offer | -- |
| FU1 | 3+ | Education -- show invisible leaks | "Things are fine" |
| FU2 | 7+ | Trust via proof -- negative case study | "Burned before" + "Sales pitch" |
| FU3 | 14+ | Low-friction reminder -- time/cost | "No time" + "Can't afford next" |
| FU4 | 21+ | Clean breakup -- exit gracefully | None (respect + door open) |

### Follow-Up Rules

- FU1-FU3: NEVER include opt-out language
- FU4 only: May offer exit ("If timing's off, no worries")
- Each follow-up must add new value (different angle, fresh proof)
- Never reference "my last email" or guilt for not responding
- Stop all sends immediately when a response is received

---

## Campaign Analysis

### Key Metrics to Track

| Metric | Target | Warning |
|--------|--------|---------|
| Open rate | >40% | <25% |
| Reply rate | >5% | <3% |
| Positive reply % | >50% of replies | <30% |
| Bounce rate | <2% | >4% |
| Unsubscribe rate | <0.5% | >1% |

### Optimization Levers (ranked by impact)

1. **Subject lines** -- A/B test 2-4 word internal-looking subjects
2. **Opening lines** -- Universal truth openers that reflect their daily reality
3. **CTA clarity** -- Direct ask with form link, no ambiguity
4. **Send timing** -- Morning sends (8-10 AM local) typically perform best
5. **Niche specificity** -- More specific = higher relevance = higher reply rates
6. **Follow-up angles** -- Each FU should present a genuinely new perspective

### When to Pause or Adjust

- Bounce rate exceeds 4%: Stop sends, audit email list quality
- Spam complaints detected: Immediately reduce volume, review content
- Reply rate drops below 2% for 2 weeks: Review targeting and copy
- Consistently negative replies: Reassess positioning and tone

---

## Related Skills

- **cold-email**: For writing individual cold emails and sequences
- **email-systems**: For email infrastructure and deliverability
- **marketing-psychology**: For psychological principles behind outreach
- **email-draft-polish**: For quality-checking drafts before sending
