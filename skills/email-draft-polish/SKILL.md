---
name: email-draft-polish
description: "Quality assurance for cold email drafts before sending. Use when reviewing generated emails, polishing draft copy, checking emails against brand guidelines, auditing email quality, or validating that emails meet all formatting and content rules. Also use when the user says 'review this email,' 'check this draft,' 'polish this email,' 'QA these emails,' or 'audit email quality.'"
---

# Email Draft Polish

Quality gate for cold email drafts. Review, critique, and improve email copy before it goes out, ensuring every email meets brand standards and maximizes reply probability.

## Before Reviewing

**Load the brand brief:**
Read `brand/Lead Gen Email Agent Brief.md` for the complete ruleset. This is the authoritative source. When in doubt, the brief wins.

**Load the niche template:**
Read the relevant `brand/templates/[niche].md` for niche-specific context (industry pain points, terminology, golden examples).

---

## Review Checklist

### 1. Structure Check

- [ ] **Word count**: 80-120 words for initial emails (body only, excluding signature)
- [ ] **Opener**: Starts with a universal truth or grounded daily reality -- NOT "I hope this finds you well," NOT a compliment, NOT a question
- [ ] **Two "Maybe it's..." scenarios**: Specific, plausible examples of system leaks relevant to the niche
- [ ] **Pattern interrupt**: One-line pivot ("The leak wasn't where they thought it was." or similar)
- [ ] **Diagnostic framing**: Names the 45-Minute [Niche] Systems Consultation with correct niche-specific name
- [ ] **CTA**: Direct ask with form link placeholder (`{{CTA}}`), no opt-out language (except FU4)
- [ ] **Signature**: 5-line block (Christopher Sharkey / Founder & Owner / Sharkitect Digital / Your AI Transformation Partner / www.sharkitectdigital.com)

### 2. Voice Check

Target voice equation: 40% Confident Expert + 25% Friendly Neighbor + 20% Straight Shooter + 15% Curious Diagnostician.

- [ ] Reads like a human wrote it (read aloud test)
- [ ] Conversational but professional -- contractions OK, slang not OK
- [ ] No marketing jargon ("leverage," "synergy," "best-in-class," "cutting-edge")
- [ ] No emojis
- [ ] No markdown formatting (no bold, no links, no bullet points in the email body)
- [ ] No exclamation marks (or at most one, used sparingly)
- [ ] Confident but not arrogant -- peer tone, not vendor tone

### 3. Content Guardrails

- [ ] **No solution-selling**: Does NOT describe what Sharkitect does, how AI works, or what the partnership includes
- [ ] **No assumed pain points**: "Maybe it's..." framing (speculative), never "You're losing money because..."
- [ ] **No case studies in first contact**: No "We helped Company X achieve Y" in the initial email
- [ ] **No specific company references**: Does not mention the prospect's website, reviews, or anything that signals scraping
- [ ] **No "AI" or "automation" language**: The email is from a person, not a technology pitch
- [ ] **Consultation is IN-PERSON**: Never references a "call," "phone consultation," or "virtual meeting" -- it's an in-person consultation
- [ ] **No opt-out in initial/FU1/FU2/FU3**: Only FU4 (breakup) may offer exit language

### 4. Follow-Up Specific Checks

**FU1 (Education):**
- [ ] Addresses objection #2 ("Things are fine") by showing invisible leaks
- [ ] Adds new value -- industry insight, stat, or educational angle
- [ ] Does NOT repeat the initial email's content

**FU2 (Trust/Proof):**
- [ ] Addresses objections #3 ("Burned before") and #4 ("Sales pitch")
- [ ] Uses negative proof (turned down revenue, told someone not to change) or honesty signal
- [ ] Builds trust without being salesy

**FU3 (Objection-Buster):**
- [ ] Addresses objections #1 ("No time") and #5 ("Can't afford next step")
- [ ] Acknowledges they're busy (empathy, not guilt)
- [ ] Restates low friction: "45 minutes. No pitch. No charge."
- [ ] Direct CTA, still no opt-out

**FU4 (Clean Breakup):**
- [ ] Short -- under 60 words
- [ ] "This is my last note" or similar
- [ ] May offer exit: "If timing's off, no worries"
- [ ] Restates offer ONE final time briefly
- [ ] No hard sell, no guilt, no "you're missing out"

### 5. Deliverability Check

- [ ] No HTML formatting
- [ ] No images or embedded content
- [ ] Single link only (the CTA form link)
- [ ] No spam trigger words ("free" in subject, "act now," "limited time," "guaranteed")
- [ ] Subject line: 2-6 words, lowercase, looks internal/personal
- [ ] No ALL CAPS words
- [ ] No excessive punctuation (!!!, ???, ...)

---

## Common Failures to Watch For

### AI-Generated Tell-Tales
These patterns immediately signal "AI wrote this" -- flag and rewrite:
- "I hope this email finds you well"
- "I came across your company and was impressed"
- "In today's competitive landscape"
- "I wanted to reach out because"
- "Allow me to introduce"
- Starting with a question ("Are you struggling with...?")
- Lists of three with parallel structure (feels templated)
- Ending with "Looking forward to hearing from you"

### Tone Drift
- **Too formal**: "I would like to propose an opportunity" -> sounds like a bank
- **Too casual**: "Hey! Quick question for ya" -> sounds like spam
- **Too salesy**: "We help companies like yours increase revenue by..." -> vendor pitch
- **Too vague**: "Many businesses face challenges" -> says nothing specific

### Structure Violations
- Missing the pattern interrupt line
- Only one "Maybe it's..." scenario (need two)
- CTA buried in the middle instead of near the end
- Signature missing a line or in wrong order
- Lead magnet named incorrectly (e.g., "free consultation" instead of "The 45-Minute HVAC Systems Consultation")

---

## Revision Process

When an email fails any check:

1. **Identify** which specific checks failed
2. **Explain** why it matters (deliverability risk? brand violation? reduced reply rate?)
3. **Rewrite** the failing section with a corrected version
4. **Re-check** the full email after revision to ensure fixes didn't introduce new issues

Present revisions as before/after pairs so the change is clear.

---

## Related Skills

- **cold-email**: For writing cold emails from scratch
- **copy-editing**: For general marketing copy editing
- **outreach-specialist**: For campaign-level outreach strategy
- **marketing-psychology**: For psychological principles behind effective copy
