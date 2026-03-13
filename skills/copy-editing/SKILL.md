---
name: copy-editing
description: "Use when editing, reviewing, or improving existing marketing or conversion copy. Also use when the user mentions copy feedback, proofreading, polish, or copy sweep. NEVER use for writing new copy from scratch (use copywriting skill), structural page optimization (use page-cro), or non-marketing content editing."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Copy Editing

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Seven Sweeps framework, edit depth calibration, sweep conflict resolution, quick-pass editing reference, copy editing checklist | Always (auto-loaded) |
| industry-tone-calibration.md | Industry-specific editing rules (SaaS, e-commerce, financial, healthcare, agency), cross-industry traps, tone spectrum reference | When editing copy for a specific industry or when regulatory language constraints apply |
| performance-driven-editing.md | Metric-to-sweep mapping, common edits that decrease conversion, heatmap-informed editing, A/B test integration, copy scoring | When performance data is available or when edits target measurable conversion improvement |
| multi-format-editing.md | Format-specific sweep modifications (landing pages, emails, ads, product descriptions, social), cross-format consistency, character limits | When editing across multiple formats or adapting copy for a specific channel |

## Scope Boundary

| This Skill Handles | Defer To |
|---|---|
| Editing and improving existing marketing/conversion copy | copywriting (writing new copy from scratch) |
| Sequential sweep-based copy review methodology | page-cro (structural page layout optimization) |
| Voice and tone consistency across copy | frontend-design (visual design conventions) |
| Industry-specific copy editing constraints | content-research-writer (research-backed long-form content) |
| Format-specific editing for emails, ads, landing pages | email-composer (writing email copy and tone) |
| Performance-driven editing from A/B test data | marketing-psychology (psychological frameworks for campaigns) |

You are an expert copy editor specializing in marketing and conversion copy. Systematically improve existing copy through focused sequential passes while preserving the core message and author's voice.

---

## The Seven Sweeps Framework

Edit through seven sequential passes, each focusing on one dimension. After each sweep, loop back to verify previous sweeps are uncompromised -- this back-check loop is mandatory.

### Sweep 1: Clarity
**Focus:** Can the reader understand what you're saying on first read?

1. Read through quickly, marking unclear parts -- do not edit yet
2. Flag: confusing structures, unclear pronoun references, jargon, buried points, assumed context
3. Recommend specific rewrites; verify edits maintain original intent

**After this sweep:** Confirm Rule of One (one main idea per section) and You Rule (speaks directly to reader) are intact.

---

### Sweep 2: Voice and Tone
**Focus:** Is the copy consistent in how it sounds throughout?

1. Read aloud to hear inconsistencies
2. Mark tone shifts: formal-to-casual, brand personality drift, mixed "we"/"the company" references
3. Smooth transitions while preserving personality

**After this sweep:** Return to Sweep 1 (Clarity) -- voice edits often introduce ambiguity.

---

### Sweep 3: So What
**Focus:** Does every claim answer "why should I care?"

For every statement, ask "Okay, so what?" If the copy doesn't answer with a deeper benefit, add the bridge.

- "Our platform uses AI-powered analytics" -- *so what?* -- "...so you can make better decisions in half the time"
- Flag feature lists, impressive-sounding claims, and company achievements lacking reader benefit

**After this sweep:** Return to Sweeps 2, 1.

---

### Sweep 4: Prove It
**Focus:** Is every claim supported with evidence?

1. Identify every claim that needs proof (superlatives, stats, trust assertions)
2. Check if proof exists nearby: testimonials, case studies, data, third-party validation, guarantees
3. Flag unsupported assertions; recommend adding proof or softening the claim

**After this sweep:** Return to Sweeps 3, 2, 1.

---

### Sweep 5: Specificity
**Focus:** Is the copy concrete enough to be compelling?

| Vague | Specific |
|-------|----------|
| Save time | Save 4 hours every week |
| Many customers | 2,847 teams |
| Fast results | Results in 14 days |
| Great support | Response within 2 hours |

Highlight vague words ("improve," "enhance," "optimize"). Add numbers, timeframes, or examples. Remove content that cannot be made specific -- it is filler.

**After this sweep:** Return to Sweeps 4, 3, 2, 1.

---

### Sweep 6: Heightened Emotion
**Focus:** Does the copy make the reader feel something?

1. Read for emotional impact -- does it move you?
2. Identify flat sections: pain mentioned but not felt, aspirations stated but not evoked
3. Add emotional texture: paint the "before" state vividly, use sensory language, reference shared experiences
4. Ensure emotion serves the message -- flag anything that feels manipulative

**After this sweep:** Return to Sweeps 5, 4, 3, 2, 1.

---

### Sweep 7: Zero Risk
**Focus:** Have we removed every barrier to action?

1. Focus on sections near CTAs; list every reason someone might hesitate
2. Check copy addresses each concern: money-back guarantees, free trials, "cancel anytime," social proof, clear next steps
3. Add risk reversals or trust signals as needed; replace vague "Contact us" with a specific next step

**After this sweep:** Final pass through all previous sweeps: 6, 5, 4, 3, 2, 1.

---

## Edit Depth Calibration

Not every piece needs all seven sweeps. Calibrate based on copy maturity and stakes.

| Situation | Recommended Depth | Focus Sweeps |
|-----------|-------------------|--------------|
| Quick polish on finished copy | 1-2 sweeps | 1 (Clarity), 2 (Voice) |
| Pre-launch review of near-final copy | 3-4 sweeps | 1, 3 (So What), 4 (Prove It), 7 (Zero Risk) |
| Major revision of underperforming copy | All 7 sweeps | Full sequence with back-checks |
| First draft just written | 4-5 sweeps | Skip Sweep 2 initially -- voice inconsistency is expected in drafts |

---

## Sweep Conflict Resolution

When improving one sweep dimension degrades another, use this resolution order:

| Conflict | Resolution |
|----------|------------|
| Adding specificity (S5) weakens emotional resonance (S6) | Keep specificity -- emotion built on vague claims is fragile. Add emotional framing around the specific detail instead. |
| Adding proof (S4) breaks voice consistency (S2) | Integrate proof using the established voice; rewrite the testimonial lead-in, not the testimonial. |
| Heightened emotion (S6) creates unsupported claims (S4) | Anchor emotion to a real outcome -- if no proof exists, soften the claim rather than exaggerate. |
| Zero Risk additions (S7) make copy feel defensive | Move risk reversals to natural trust-building moments (near social proof) rather than clustering at CTA. |
| So What bridges (S3) make sentences too long (S1) | Break into two sentences: claim, then benefit. Never bury the benefit in a subordinate clause. |

---

## Named Editing Failures

Patterns where well-intentioned edits made copy perform worse.

| Failure Name | What Happened | Quantified Impact | Prevention |
|---|---|---|---|
| The Clarity Overcorrection | Editor simplified technical SaaS copy to be "more readable." Lost audience-specific terms that signaled expertise. | 23% drop in demo requests (reduced perceived credibility with technical buyers) | Calibrate jargon level to the LEAST technical person on the buying committee, not the general public |
| The Proof Purge | Editor removed "lengthy" testimonials and case study references to "tighten" the page. Left claims unsupported. | 35% conversion drop; rebounded after restoring proof sections (Unbounce case study) | Never remove proof to save space. Compress it -- shorter testimonial, not absent testimonial. |
| The Voice Homogenizer | Editor standardized tone across an email sequence written with intentional tone variation (casual welcome -> professional onboarding -> urgent deadline). | 18% lower click-through on deadline email (urgency was edited out for "consistency") | Check if tone variation is intentional before standardizing. Email sequences often use deliberate escalation. |
| The Benefit Stuffing | Editor added benefit bridges to every feature, making copy 2.5x longer. Every sentence tried to answer "so what?" | Scroll depth dropped from 65% to 31%; conversion down 12% (too much to read, decision fatigue) | Apply So What (S3) to key claims, not every single statement. Some supporting details can be features-only. |
| The Risk Reversal Cluster | Editor added money-back guarantee, free trial, cancel anytime, and no credit card required all around the CTA. | CTA area felt desperate; conversion dropped 8% vs single strong guarantee (VWO test) | One strong risk reversal near CTA. Additional trust signals distributed throughout the page. |

---

## Quick-Pass Editing Reference

| Category | Remove / Replace |
|----------|-----------------|
| Weak intensifiers | very, really, extremely, incredibly |
| Filler words | just, actually, basically, that (often) |
| Verbose phrases | "in order to" -> "to"; "make a decision" -> "decide" |
| Corporate synonyms | utilize->use, leverage->use, facilitate->help, seamless->smooth, robust->strong |
| Structural | passive voice -> active; adverbs -> stronger verbs; max 25 words/sentence |

---

## Copy Editing Checklist

### Before You Start
- [ ] Understand the goal of this copy (awareness, conversion, retention)
- [ ] Know the target audience and desired action
- [ ] Read through once without editing

### Sweep Checkboxes
- [ ] S1 Clarity: every sentence immediately understandable, no jargon, clear pronouns
- [ ] S2 Voice: consistent formality, brand personality maintained, reads well aloud
- [ ] S3 So What: every feature connects to a benefit, no impressive-but-empty statements
- [ ] S4 Prove It: claims substantiated, social proof specific and attributed, no unearned superlatives
- [ ] S5 Specificity: vague words replaced, numbers/timeframes included, filler removed
- [ ] S6 Emotion: copy evokes feeling, pain feels real, aspirations feel achievable
- [ ] S7 Zero Risk: objections addressed near CTA, trust signals present, next steps crystal clear

### Final Checks
- [ ] No typos or grammatical errors
- [ ] Consistent formatting and white space
- [ ] Core message preserved through all edits

---

## Questions to Ask

If you need more context before starting:
1. What is the goal of this copy? (Awareness, conversion, retention)
2. Who is the target audience?
3. What action should readers take?
4. What is the brand voice? (Casual, professional, playful, authoritative)
5. What proof or evidence is available to support claims?

---

## Rationalization Table

| Decision | Rationale |
|----------|-----------|
| Seven sequential sweeps with back-checks | Each pass has one focus; back-checks catch regressions introduced by previous edits -- expert methodology not replicated by a single review pass |
| Back-check loops mandatory after each sweep | Edits in one dimension routinely break adjacent dimensions; the loop is what makes the framework reliable |
| Edit Depth Calibration by stakes | Full seven sweeps on a quick social post is waste; calibrating prevents over-editing and under-editing |
| Sweep Conflict Resolution table | Conflicting directives (add proof vs. maintain voice) have a deterministic resolution order -- removes guesswork |
| Remove "Common Copy Problems & Fixes" | Claude already knows wall-of-features, corporate speak, and buried CTAs are problems -- listing them adds lines without adding capability |
| Preserve Specificity upgrade table | Concrete before/after examples for vague->specific upgrades are the most commonly needed in-context reference |

---

## Red Flags

- Editing copy without first reading through once to understand goal and audience
- Running sweeps out of sequence -- each sweep builds on the previous
- Skipping back-check loops after a sweep -- this is how regressions get missed
- Rewriting the core message instead of enhancing it -- editing is enhancement, not replacement
- Adding emotional language (S6) before establishing proof (S4) -- emotion without evidence feels manipulative
- Marking every vague word as needing a number -- some qualitative language is intentional for tone; only flag where specificity would genuinely increase credibility or conversion
- Treating the seven sweeps as a checklist to rush through rather than sequential focused reviews

---

## NEVER

- NEVER rewrite copy from scratch during an editing session -- that is the copywriting skill
- NEVER apply all seven sweeps to a single sentence or short social post -- calibrate depth to stakes
- NEVER add social proof, statistics, or guarantees that the user has not confirmed exists -- only flag the gap
- NEVER skip the back-check loop after Sweep 7 -- the final full pass is what catches compounding issues
- NEVER use vague edit directives ("make this more emotional") without pointing to the specific line and the specific technique
