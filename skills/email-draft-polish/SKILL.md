---
name: email-draft-polish
description: "Use when reviewing a generated cold email draft, polishing email copy before sending, checking an email against brand guidelines, auditing email quality, or validating that an email meets formatting and content rules. Also triggered by: 'review this email,' 'check this draft,' 'polish this email,' 'QA these emails,' 'audit email quality.' NEVER for writing emails from scratch, general copywriting tasks, or non-cold-email correspondence."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Email Draft Polish

## File Index

| File | Purpose | Required |
|------|---------|----------|
| `brand/Lead Gen Email Agent Brief.md` | Complete ruleset -- authoritative source | YES -- load before reviewing |
| `brand/templates/[niche].md` | Niche-specific pain points, terminology, golden examples | YES -- load matching niche |

**If brand brief is missing:** Stop and ask the user to provide it. Do not proceed without it. Every rule in this skill is derived from that document -- QA without it is guesswork.

---

## Rationalization Table

These are the excuses Claude (or the user) might use to skip a thorough QA pass. None of them are valid.

| Rationalization | Why It Fails |
|----------------|-------------|
| "The email looks good enough" | "Good enough" sends the wrong impression to cold prospects. One AI tell-tale tanks deliverability and reply rates. |
| "This is just a follow-up, less scrutiny needed" | Follow-ups have their own specific structural requirements. FU2 and FU3 especially require trust signals that are easy to miss. |
| "The user already approved the template" | Approving a template structure is not approving a specific draft. Each draft requires its own pass. |
| "It's close enough to the brand voice" | "Close enough" accumulates. A slightly salesy tone plus a slightly formal opener plus one marketing buzzword = an email that reads as AI-generated. |
| "The checklist doesn't apply to this niche" | The checklist applies to all niches. Niche-specific items are additive, not replacements. |
| "The user said they just want light polish" | Light polish still requires flagging hard rule violations. Mention all failures; let the user decide what to fix. |
| "This email already performed well before" | Past performance on a different draft in a different niche with a different prospect is not a pass on this one. |

---

## NEVER

- **NEVER approve an email that contains AI tell-tales.** Phrases like "I hope this finds you well," "In today's competitive landscape," or "I wanted to reach out" are disqualifying -- rewrite, do not approve.
- **NEVER let "call" or "phone" slip through.** The consultation is in-person only. A single wrong word here breaks the entire offer framing.
- **NEVER skip the brand brief.** Every rule in this skill has additional context in the brief. Reviewing without it means missing niche-specific exceptions and requirements.
- **NEVER approve a draft with solution-selling language.** Describing what Sharkitect does, how AI works, or what the engagement includes violates the core premise of the email (diagnostic framing, not sales pitch).
- **NEVER assume the follow-up type.** Confirm whether the draft is initial, FU1, FU2, FU3, or FU4 before applying the checklist. Each type has different requirements.
- **NEVER skip the deliverability check.** A brilliant email that hits a spam filter has a 0% reply rate. Deliverability is not optional.
- **NEVER present a pass without checking every item.** Rushing the checklist produces false confidence and sends broken emails.

---

## Before Reviewing

**Step 1 -- Identify the email type:**
Confirm: initial, FU1, FU2, FU3, or FU4. This determines which sections of the checklist apply.

**Step 2 -- Load the brand brief:**
Read `brand/Lead Gen Email Agent Brief.md`. This is the authoritative source. When in doubt, the brief wins.

**Step 3 -- Load the niche template:**
Read `brand/templates/[niche].md` for niche-specific context (industry pain points, terminology, golden examples).

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

## Red Flags

Observable patterns that indicate this skill is being violated or the email has a serious problem.

- **AI tell-tale phrase detected** -- "I hope this," "I wanted to reach out," "In today's landscape," or any phrase that appears in the AI-Generated Tell-Tales list below. Hard stop.
- **Word "call" or "phone" appears in body** -- Consultation is in-person. Any reference to a call violates the offer framing.
- **Draft describes Sharkitect's services or AI** -- Solution-selling. The email should create curiosity, not pitch a product.
- **Opener is a question** -- Questions as openers are a documented AI pattern. They also put the reader on defense. Flag and rewrite.
- **Only one "Maybe it's..." scenario** -- The structure requires two. One scenario reads as thin and unconvincing.
- **Signature is incomplete or wrong order** -- Any deviation from the 5-line block breaks brand consistency.
- **Subject line is more than 6 words or contains caps** -- Deliverability risk and looks promotional rather than personal.
- **Opt-out language in initial, FU1, FU2, or FU3** -- Exit language belongs only in FU4. Including it earlier signals low confidence and reduces response urgency.
- **Word count outside 80-120 for initial emails** -- Under 80 reads as dismissive; over 120 loses attention. Both reduce reply probability.
- **Follow-up repeats initial email content** -- FU1 through FU4 must add new value. Repetition signals that you have nothing new to say.

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
