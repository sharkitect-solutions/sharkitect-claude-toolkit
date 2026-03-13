# Companion File Design Guide

## Why Companions Exist

Skills use a three-layer loading architecture:
1. **Metadata** (~100 tokens) -- always loaded for matching
2. **SKILL.md body** (target <300 lines) -- loaded when triggered
3. **Companion files** (unlimited) -- loaded on demand

Companion files are the third layer. They hold expert content that would bloat the main SKILL.md but is essential for specific scenarios. The loading trigger in SKILL.md tells Claude WHEN to load each companion and WHEN NOT to.

---

## Impact Quantification

From 30+ before/after measurements during skill optimization:

| Companion Status | D5 Score (avg) | Total Score Impact |
|---|---|---|
| No companions, no File Index | 2-3/15 | Baseline |
| 1-2 companions, basic listing | 7-9/15 | +5 to +7 points |
| 3+ companions with Load When/Do NOT Load triggers | 13-15/15 | +10 to +12 points |
| Skeleton companions (placeholder content) | 2-4/15 | WORSE than none |

The skeleton trap: senior-backend had 6 companion files that were auto-generated skeletons with placeholder content ("Scenario 1/2/3"). These scored WORSE than having no companions because judges penalize false progressive disclosure.

---

## Companion File Sizing

| Guideline | Target | Rationale |
|---|---|---|
| Lines per file | 70-150 | Under 70 lacks depth for a standalone reference. Over 150 becomes a mini-SKILL.md |
| Files per skill | 3-5 | Under 3 doesn't justify the File Index overhead. Over 5 fragments knowledge too much |
| Total companion content | 250-600 lines | Combined companion content should be 2-4x the SKILL.md body |

---

## Content Types That Work

| Type | Description | Why It Works | Example |
|---|---|---|---|
| **Decision reference** | Deep-dive into one decision point from SKILL.md | Provides nuance SKILL.md can't fit | "platform-implementation.md" for A/B testing tool selection |
| **Troubleshooting catalog** | Error conditions, failure modes, recovery steps | Loaded only when things break | "integration-troubleshooting.md" for standup skill |
| **Domain deep-dive** | Expert knowledge in a sub-domain | Keeps SKILL.md focused on decisions, companion on details | "statistical-pitfalls.md" for experiment analysis |
| **Research/evidence base** | Citations, quantified findings, study references | Adds credibility without bloating main file | "standup-effectiveness.md" with Stray et al. citations |
| **Technical reference** | API schemas, format specs, encoding rules | Loaded when debugging or building | "digest-script-reference.md" for JSONL parsing |

### Content Types That Fail

| Type | Why It Fails | Fix |
|---|---|---|
| **Rehashed SKILL.md** | Duplicates body content. Judges penalize. | Companion must cover NEW ground |
| **Skeleton/placeholder** | Empty structure with "TODO" or generic headings | Write real content or don't create the file |
| **Tutorial content** | "What is X" explanations Claude already knows | Focus on expert knowledge: gotchas, edge cases, decision factors |
| **Output templates** | Pre-formatted example outputs | Templates belong in examples/ or should be generated dynamically |
| **Exhaustive catalogs** | 500+ line lists of every possible scenario | Stay under 150 lines. If more needed, split into multiple companions |

---

## File Index Design

The File Index in SKILL.md is what makes companions discoverable. Without it, Claude doesn't know companions exist.

### The Load When / Do NOT Load Format

```markdown
## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `platform-implementation.md` | User needs specific tool setup, platform comparison, or debugging platform-specific issues | General experiment design with no platform questions |
| `statistical-pitfalls.md` | Sample size calculations, significance questions, when to stop a test, multiple comparison concerns | Simple A/B test with clear winner and large sample |
| `test-velocity-management.md` | User has testing backlog, wants to increase throughput, or needs to prioritize experiments | Single one-off test with no velocity concerns |
```

### Why Three Columns

| Column | Purpose | Without It |
|---|---|---|
| **File** | Identifies the companion | Claude can't find it |
| **Load When** | Tells Claude the trigger conditions | Claude loads companions randomly or never |
| **Do NOT Load** | Tells Claude when to SKIP | Claude over-loads, wasting context on irrelevant content |

The "Do NOT Load" column is the critical innovation. Without it, Claude defaults to loading everything "just in case," which wastes context and dilutes the main SKILL.md's guidance.

### File Index Placement

Put the File Index near the TOP of SKILL.md (after frontmatter + intro, before main content sections). Claude reads sequentially -- a File Index at the bottom may be missed or skimmed.

---

## Companion Content Writing Rules

| Rule | Rationale |
|---|---|
| Every companion must add knowledge not in SKILL.md | Zero duplication. Companion enriches, never repeats |
| Use tables as primary format | Tables are scannable, unambiguous, space-efficient |
| Include failure modes and edge cases | Expert knowledge = what goes wrong, not just what to do |
| Name anti-patterns with "The X" format | Named patterns are memorable and referenceable (D3 boost) |
| Quantify claims where possible | "32% increase" > "significant improvement" |
| Keep paragraphs to 2-3 sentences | Companions are reference material, not essays |
| Use horizontal rules between major sections | Improves scannability in long companions |
| Include a section header hierarchy | H2 for major sections, H3 for subsections. No H1 (reserved for title) |

---

## Companion Strategy by Skill Type

| Skill Type | Companion Focus | Example Files |
|---|---|---|
| **Tool skills** (docx, pdf, xlsx) | Format specifications, library comparisons, error catalogs | `ooxml-internals.md`, `library-selection.md` |
| **Process skills** (mcp-builder) | Phase-specific deep dives, checklist expansions | `config-debugging.md`, `auth-patterns.md` |
| **CRO/marketing skills** | Platform-specific gotchas, research citations, compliance | `browser-api-mechanics.md`, `legal-compliance.md` |
| **Creative skills** (frontend-design) | Reference catalogs (fonts, colors), art-historical context | `typography-reference.md`, `color-systems.md` |
| **Meta skills** (skill-judge, skill-creator) | Calibration data, extended examples, methodology deep-dives | `scoring-calibration.md`, `dimension-examples.md` |
