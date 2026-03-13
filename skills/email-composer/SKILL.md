---
name: Email Composer
description: "Use when composing a NEW email from scratch (any type: business, technical, customer, personal-professional). NEVER for editing/polishing existing drafts (email-draft-polish), multi-email sequences or drip campaigns (email-sequence), email infrastructure/deliverability/SPF/DKIM (email-systems), cold sales outreach (cold-email), internal company announcements/memos (internal-comms), general text editing (copy-editing), or non-email professional writing (professional-communication)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# Email Composer

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| SKILL.md | Tone calibration matrix, subject line engineering, structural anti-patterns (8), recipient psychology (4 types + cross-cultural), email failure checklist | Always (auto-loaded) |
| scenario-frameworks.md | Structural frameworks for 8 email scenarios: meeting request, follow-up (5 types), introduction (3 types), feedback request, status update, decline/say-no, decision request, apology, vendor negotiation | When composing an email for a specific scenario that needs structural guidance |
| difficult-emails-guide.md | Bad news delivery (3 severity levels + medium decision), negative feedback by email (when appropriate vs dangerous), escalation emails (pre-checklist + structure), declining without burning bridges, expectation management, conflict de-escalation (5-step + escalating vs de-escalating words), legal-sensitive communications | When the email involves sensitive, high-stakes, or emotionally charged content |
| email-timing-and-follow-up.md | Optimal send times (6 recipient types), follow-up timing and cadence (5 urgency levels), timezone management (5 scenarios), email vs other medium decision tree (8 message types), email chain management (6 situations), read receipt ethics, inbox management for recipients | When timing matters, planning follow-ups, or deciding whether email is the right medium |

## Scope Boundary

| Need | Use This Skill? | Use Instead |
|---|---|---|
| Compose a new email from scratch | YES | -- |
| Edit/polish an existing draft | NO | email-draft-polish |
| Multi-email sequences or drip campaigns | NO | email-sequence |
| Email infrastructure, deliverability, SPF/DKIM | NO | email-systems |
| Cold sales outreach to strangers | NO | cold-email |
| Internal memos, announcements, org comms | NO | internal-comms |
| General text editing (not email) | NO | copy-editing |
| Non-email professional writing | NO | professional-communication |

## Tone Calibration Matrix

Select tone parameters by crossing recipient relationship with purpose. Do NOT default to "professional" -- calibrate precisely.

| Recipient | Request | Update/FYI | Bad News | Escalation | Appreciation |
|---|---|---|---|---|---|
| C-suite | BLUF, 0 contractions, no exclamation, "Regards" | 3 sentences max, bullet data, "Best" | Lead with impact number, then cause, then fix, "Regards" | State risk in dollars/days, 1 clear ask, "Respectfully" | 1 sentence specific praise, tie to metric, "Best" |
| Direct manager | Light contractions OK, 1 exclamation max, "Thanks" | Bullet-heavy, include your interpretation, "Best" | Own it first sentence, corrective action second, "Thanks" | Frame as blocker to shared goal, propose options, "Thanks" | Genuine, specific, skip superlatives, "Thanks" |
| Peer/colleague | Contractions normal, casual sign-off, "Cheers"/"Thanks" | Conversational, skip preamble, "Thanks" | Direct but empathetic, offer help, "Thanks" | Name the impact on your work, no blame, "Thanks" | Informal, can use humor if relationship supports it, "Cheers" |
| Direct report | Warm but clear, contractions OK, "Thanks" | Add context on WHY, not just what, "Best" | Private, specific, forward-looking, "Thanks" | Be direct about gap, ask for their plan, "Thanks" | Public when possible, name specific behavior, "Great work" |
| External client | 0 contractions, 0 exclamations, "Kind regards" | Lead with value to THEM, "Best regards" | Acknowledge impact first, solution second, timeline third, "Sincerely" | Restate SLA/agreement, document facts, "Regards" | Tie to business outcome, "Best regards" |
| Vendor/partner | Direct, transactional, "Best" | Brief, action-oriented, "Thanks" | State terms, cite agreement, "Regards" | Quote contract clause, escalation path, "Regards" | Brief acknowledgment, "Thanks" |

**Sentence length**: C-suite/client = 12-18 words avg. Peers = 8-15 words. Technical audiences = whatever clarity requires.
**Emoji policy**: Never in first email to someone. Never to C-suite/clients. Peers only after they use emoji first.

## Subject Line Engineering

**Mobile preview truncates at 30 characters.** Front-load the essential word.

| Pattern | When to Use | Example |
|---|---|---|
| `[ACTION REQUIRED]` prefix | Recipient must do something by a date | `[ACTION REQUIRED] Approve budget by Fri` |
| `[FYI]` prefix | No action needed, awareness only | `[FYI] API latency spike resolved` |
| `[DECISION NEEDED]` prefix | Binary/ternary choice required | `[DECISION NEEDED] Vendor A or B for Q3` |
| Naked subject (no prefix) | Standard correspondence | `Database migration timeline update` |
| `Re:` chain continuation | Same thread, same topic | Keep existing subject |
| Break `Re:` chain when | Topic shifted, new decision needed, or chain > 5 deep | New subject referencing old thread |

**Internal vs external**: Internal subjects can use prefixes and abbreviations. External subjects to clients must read as complete, professional phrases -- no brackets, no abbreviations.

**Never**: Single-word subjects ("Update", "Question", "Hello"). Clickbait urgency when not urgent. ALL CAPS words.

## Structural Anti-Patterns

These patterns cause emails to fail (no response, wrong action, confusion). Detect and fix before output.

**1. Buried Lede** -- Action item appears in paragraph 3+.
Fix: First sentence = what you need. Second sentence = by when. Context follows.

**2. Essay Email** -- >150 words for a request that needs <40.
Fix: If the ask fits in 2 sentences, the email is 2 sentences + sign-off. Permission to be brief.

**3. Passive Ask** -- "It would be great if someone could look into this."
Fix: Name the person. Name the action. Name the date. "Alex, please review the PR by Thursday EOD."

**4. Premature Apology** -- "Sorry to bother you" / "I know you're busy" as openers.
Fix: Delete. These phrases signal low status and prime the reader to deprioritize. Just make the ask.

**5. Wall of Context** -- 5 paragraphs of background before revealing the ask.
Fix: BLUF (Bottom Line Up Front). Ask first, context second, detail in attachment if needed.

**6. Multi-Ask Sprawl** -- 3+ unrelated requests in one email.
Fix: One email = one ask. Completion rate drops ~50% per additional ask. Send separate emails or use numbered list with explicit "I need responses to all 3."

**7. Ambiguous Deadline** -- "When you get a chance" / "at your earliest convenience."
Fix: Specific date and time. "By Wednesday 3 PM ET" or "No rush -- next week is fine" (at least anchors expectation).

**8. Attachment Phantom** -- "See attached" but no attachment; or attachment not referenced in body.
Fix: Always verify attachment is present. Reference it by name: "See the attached Q4-forecast.xlsx for details."

## Recipient Psychology

### C-Suite
Structure: BLUF, then 3 bullets max, then "Happy to provide detail." Attach the detail doc -- never paste it inline. They scan, they don't read. Make scanning productive. Every sentence must either state the ask, quantify impact, or propose a decision.

### Engineers/Technical
Skip pleasantries. Lead with the technical context they need to evaluate the request. Include version numbers, error codes, links to logs. "Hi, hope you're well" wastes their time and yours. Bullet points > paragraphs. Code blocks welcome.

### Clients
First sentence acknowledges their world ("I know launch week is intense"). Quantify value to THEM, not to you. Every email ends with an explicit next step that includes a date: "I'll send the revised mockups by Thursday. If I don't hear back by Friday, I'll proceed with version B." Never leave next steps ambiguous.

### Vendors
Be transactional. State what you need, when, and the terms. Document agreements in email even if discussed on a call ("Per our call today, confirming: ..."). Friendly but not warm -- warmth gets exploited in negotiations.

### Cross-Cultural Calibration
| Culture | Directness | Formality | Preamble | "No" Style |
|---|---|---|---|---|
| US | Direct ask OK | Medium | Brief | "Unfortunately, we can't" |
| UK | Slightly indirect | Medium-high | Polite buffer | "I'm afraid that won't be possible" |
| Japan | Indirect, consensus-seeking | High | Seasonal greeting expected | Imply difficulty, never blunt refusal |
| Germany | Very direct, expected | High initially | Minimal | Direct "no" is professional, not rude |
| Latin America | Relationship-first | Medium | Personal warmth expected | Soft decline with alternative |

## Email Failure Mode Checklist

Before outputting any composed email, verify against these failure modes:

- [ ] **CTA exists**: Reader knows exactly what to do after reading
- [ ] **Single primary ask**: If multiple asks, they're numbered and reader is told to respond to all
- [ ] **Active voice**: "Please approve" not "Approval is needed"
- [ ] **Right medium**: If the email requires back-and-forth discussion, suggest a call instead
- [ ] **Deadline specified**: Concrete date/time, not "when convenient"
- [ ] **Correct audience**: No one is CC'd who shouldn't see this; no one missing who should
- [ ] **Scannability**: Key info in first 3 lines, bullets for lists, bold for critical items
- [ ] **No premature apology**: Opener doesn't undermine the ask

## Rationalization Table

| Temptation | Why It Fails | Do Instead |
|---|---|---|
| "I'll add context so they understand fully" | Reader skips long emails. Understanding != reading. | BLUF + "Details below if needed" with a visual break |
| "I should soften this with hedging language" | "Maybe we could possibly consider" = no one acts | State the ask directly. Politeness is in tone, not hedging. |
| "I'll CC the whole team for visibility" | Diffusion of responsibility. Everyone assumes someone else will act. | TO: the person who must act. CC: only those who must know. |
| "The formal template will look more professional" | Generic templates read as generic. | Match the relationship. Forced formality to a peer feels cold. |
| "I'll include all the background they might need" | Information overload kills action. | Include only what's needed to decide. Link or attach the rest. |
| "I should follow up same-day to show urgency" | Reads as impatient or aggressive. | Wait 2-3 business days. Then follow up with new value, not "just checking in." |

## Red Flags

1. Email exceeds 200 words for a simple request -- compress or split
2. No verb in the call-to-action -- "Thoughts?" is not a CTA; "Please confirm by Friday" is
3. Opening with apology or self-deprecation -- delete the throat-clearing
4. Using "ASAP" without a real deadline -- pick a date or admit it's not urgent
5. Passive voice hiding who must act -- find the actor, name them
6. Reply-all on a thread where your response only matters to the sender
7. Sending bad news or criticism over email when a call would be more humane
8. Writing the email at all when Slack/chat would get a faster response for a quick question

## NEVER

1. Never output template emails with `[bracketed placeholders]` -- ask for the missing information, then compose a complete email
2. Never use "I hope this email finds you well" -- it's filler that signals a mass email
3. Never compose an email longer than 300 words without explicitly asking if the user wants a shorter version
4. Never include emoji in emails to people the user hasn't previously emailed
5. Never default to formal tone -- calibrate to the actual recipient relationship using the Tone Calibration Matrix
