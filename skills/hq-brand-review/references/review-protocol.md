# Brand Review Protocol -- 6-Step Execution Guide

Load this file every time the brand-reviewer agent runs a full review. This defines the exact scoring methodology, thresholds, and edge-case handling for Sharkitect Digital brand compliance.

## Step 1: Voice Attribute Measurement

Score each attribute on 1-10 against the brand guide targets.

| Attribute | Target | 1-3 (Failing) | 4-6 (Weak) | 7-9 (On-Brand) | 10 (Overcorrected) |
|-----------|--------|----------------|-------------|-----------------|---------------------|
| **Confident** | 7-9 | Multiple hedge words per paragraph; passive voice dominant | Occasional hedging; some declarative statements | Active voice, present tense, concrete specifics | Arrogant; dismisses reader concerns; no caveats even when warranted |
| **Direct** | 7-9 | Buried leads; context before point; avg sentence >25 words | Mixed structure; some paragraphs lead with point | First sentence = point; 12-18 word avg; 2-4 sentence paragraphs | Telegraphic; missing necessary context; reads as curt |
| **Expert** | 6-8 | No specifics; vague claims; unexplained jargon | Some metrics but relies on superlatives | Precise terms, cited outcomes, honest constraints | Inaccessible; assumes deep technical knowledge audience lacks |
| **Approachable** | 6-8 | Corporate formality; no contractions; "Dear valued client" | Inconsistent tone; formal headers with casual body | "You" focused; natural contractions; dry humor where appropriate | Forced casualness; slang; undermines credibility |
| **Action-Oriented** | 7-9 | No next steps; theoretical conclusions; passive recommendations | Vague CTAs; "consider doing X" without specifics | Clear next step; specific dates; named ownership | Every sentence demands action; exhausting to read |

**Scoring rule:** Measure attribute presence across the FULL document. A single strong paragraph does not compensate for 5 weak ones. Weight the opening and closing 20% higher -- readers remember beginnings and endings.

## Step 2: Banned Term & Pattern Scan

Run these checks against the full content:

**Absolute ban patterns (any match = violation):**
```
\b(synerg(y|ize|istic))\b
\b(best[- ]in[- ]class)\b
\b(paradigm\s+shift)\b
\bplease do not hesitate\b
\bat the end of the day\b
\bit goes without saying\b
\bthink outside the box\b
\b(low[- ]hanging fruit)\b
\bleverage\b ← only when used as verb (check: "leverage our" / "to leverage")
```

**Contextual ban patterns (flag for review):**
```
\b(AI[- ]powered)\b ← allowed in technical docs only
\bscalable\b ← allowed with specific metrics ("scales to 10K")
\brobust\b ← almost never appropriate outside technical architecture
\bseamless\b ← never appropriate (nothing is seamless)
\brevolutionary\b ← never appropriate (let results speak)
```

**AI-generated content markers (flag as probable AI drift):**
```
\b(furthermore|moreover|in addition)\b ← filler transitions
\bthat's a great question\b
\bI hope this helps\b
\b(might|could|potentially)\b ← count occurrences; >3 per 500 words = flag
```

**Scoring:** 0 violations = full marks. Each absolute ban = -2 points from Voice Alignment. Each contextual ban without justification = -1 point. Each AI marker cluster (3+ in 500 words) = -1 point.

## Step 3: Tone Consistency Analysis

Check formality and energy scores against channel targets from the brand guide:

| Channel | Formality Target | Energy Target |
|---------|-----------------|---------------|
| Client proposals | 6/10 | 5/10 |
| Client emails | 4/10 | 5/10 |
| Blog posts | 5/10 | 6/10 |
| Social media | 3/10 | 7/10 |
| Landing pages | 5/10 | 7/10 |
| Internal docs | 3/10 | 4/10 |

**Measurement method:**
- Formality: Count formal markers (passive voice, no contractions, complex sentence structure, third-person) vs informal markers (contractions, "you/your", short sentences, conversational transitions). Ratio maps to 1-10.
- Energy: Count energy markers (imperatives, exclamation marks, short punchy sentences, power verbs) vs low-energy markers (hedges, long qualifications, passive constructions). Ratio maps to 1-10.
- Consistency: Measure variance across sections. Standard deviation >2 points within a single piece = tone inconsistency flag.

**Scoring:** Each dimension (formality, energy) within +/-1 of target = full marks. Each dimension off by 2 = -1. Off by 3+ = -2. Inconsistency flag = additional -1.

## Step 4: Audience Calibration Check

Verify content matches the intended audience sophistication level:

| Audience | Reading Level | Jargon Tolerance | Example Density |
|----------|--------------|-------------------|-----------------|
| Business owner (non-technical) | Grade 8-10 | Low -- explain all terms on first use | High -- concrete before abstract |
| Technical decision-maker | Grade 12-14 | Medium -- industry terms OK, proprietary terms explained | Medium -- architecture diagrams welcome |
| End user / employee | Grade 6-8 | None -- plain language only | Very high -- step-by-step with screenshots |
| Partner / vendor | Grade 10-12 | High -- shared professional vocabulary | Low -- focus on specs and SLAs |

**Measurement:** Identify the intended audience from context (channel, subject, recipient). Check reading level using Flesch-Kincaid or equivalent heuristic. Flag jargon that exceeds audience tolerance. Score 1-10 based on alignment.

## Step 5: Brand Drift Scoring

Calculate the Brand Fidelity Score:

```
voice_alignment  = avg(confident, direct, expert, approachable, action_oriented)  [1-10]
tone_consistency = avg(formality_alignment, energy_alignment, consistency_score)   [1-10]
audience_fit     = audience_calibration_score                                       [1-10]

raw_score = voice_alignment + tone_consistency + audience_fit   [3-30]

violation_penalty:
  - Each absolute banned term:      -2
  - Each unjustified contextual ban: -1
  - Each AI marker cluster:          -1
  - Tone inconsistency flag:         -1

brand_fidelity_score = raw_score - violation_penalty   [clamp to 0-30]
```

## Step 6: Determination

Map the Brand Fidelity Score to a determination:

| Determination | Score Range | Action | Report Format |
|--------------|-------------|--------|---------------|
| **Brand-Clear** | 25-30 | Publish as-is. Optional minor notes (max 2). | One-paragraph summary. List minor notes if any. |
| **Aligned with Notes** | 18-24 | Publish after listed changes. Max 3 specific fixes. | Summary + numbered fix list with exact locations. |
| **Revision Required** | 10-17 | Return to author with detailed change list. | Full breakdown by step. Annotated excerpts. Rewrite guidance. |
| **Escalation Required** | 0-9 | Fundamental voice mismatch. Needs full rewrite with brand guide open. | Full report + recommendation to rewrite from scratch with brand guide loaded. |

## Edge Cases

**Bilingual content (English + Spanish):**
- Score each language section independently. The brand voice applies in both languages.
- Spanish content gets +1 formality tolerance (Spanish business norms are slightly more formal).
- Banned terms: check English list for English sections; for Spanish sections, flag direct translations of banned terms (e.g., "sinergia", "de vanguardia").

**Heavily technical content (API docs, architecture specs):**
- Shift Expert target from 6-8 to 8-10. Technical accuracy outweighs approachability here.
- Relax Approachable target to 4-6. Technical readers expect precision over warmth.
- "AI-powered" and "scalable" contextual bans are lifted when accompanied by specifications.
- Audience calibration: assume Technical decision-maker unless stated otherwise.

**Intentionally informal content (internal Slack, team celebrations, casual social):**
- If the content creator explicitly flags "intentionally casual" or the channel is internal:
  - Relax all voice attribute targets by -2 points (e.g., Confident target becomes 5-7).
  - Skip banned term scan for contextual bans (absolute bans still apply).
  - Adjust determination thresholds: Brand-Clear becomes 20-30, Aligned with Notes becomes 14-19.
- Document the relaxation in the review report so it is traceable.

**Multi-author content (proposals with sections from different writers):**
- Score each section independently, then score overall consistency.
- Flag sections where voice attributes differ by >3 points from the document average.
- Tone consistency check is especially critical -- readers notice jarring shifts between sections.
