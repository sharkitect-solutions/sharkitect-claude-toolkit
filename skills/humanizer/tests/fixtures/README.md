# Humanizer Benchmark Fixtures

Accuracy benchmark for the `humanizer` skill. Each fixture is an AI-generated paragraph paired with a canonical humanized version. The set serves three purposes:

1. **Drift detection** -- a quarterly skill-judge rerun + manual review of fixture outputs catches regressions when humanizer is edited.
2. **Calibration** -- new contributors can see the target quality of "humanized" output before they start editing the skill.
3. **Test-vector reference** -- if humanizer ships with a future runner, these are the test inputs.

## Format

Each fixture is a Markdown file with YAML frontmatter:

```yaml
---
id: 001-significance-inflation
ai_tells_present:
  - significance-inflation
  - rule-of-three
  - vague-attributions
category: encyclopedic
source_prompt: "Write a paragraph introducing the historical significance of the printing press."
notes: |
  Demonstrates the most common LLM failure mode: puffing up importance via
  abstract significance claims and unsourced "experts argue" framing.
---

## Input (AI-generated, raw)

<the AI text>

## Expected (Humanized, canonical)

<the humanized rewrite>

## Rationale

<2-4 bullets explaining what changed and why>
```

## Fixture index

| # | File | AI tells covered | Difficulty |
|---|------|------------------|------------|
| 1 | `001-significance-inflation.md` | significance-inflation, rule-of-three, vague-attributions | easy |
| 2 | `002-promotional-language.md` | promotional-language, copula-avoidance, em-dash-overuse | easy |
| 3 | `003-superficial-ing-analyses.md` | superficial-ing, abstract-tapestry-vocabulary, false-ranges | medium |
| 4 | `004-vague-attributions.md` | vague-attributions, knowledge-cutoff-hedging, subjectless-fragments | medium |
| 5 | `005-rule-of-three.md` | rule-of-three, elegant-variation, negative-parallelisms | easy |
| 6 | `006-em-dash-overuse.md` | em-dash-overuse, signposting, generic-conclusion | medium |
| 7 | `007-ai-vocabulary.md` | ai-vocabulary, fragmented-headers, inline-header-vertical-lists | medium |
| 8 | `008-composite-multiple-tells.md` | 8+ tells in one paragraph (real-world LLM essay opener) | hard |

## Tell-name reference

The `ai_tells_present` list uses kebab-case slugs that map to humanizer's catalog sections (1-29):

| Slug | Skill section |
|------|---------------|
| significance-inflation | §1 Undue Emphasis on Significance, Legacy, and Broader Trends |
| notability-emphasis | §2 Undue Emphasis on Notability and Media Coverage |
| superficial-ing | §3 Superficial Analyses with -ing Endings |
| promotional-language | §4 Promotional and Advertisement-like Language |
| vague-attributions | §5 Vague Attributions and Weasel Words |
| challenges-prospects | §6 Outline-like "Challenges and Future Prospects" Sections |
| ai-vocabulary | §7 Overused "AI Vocabulary" Words |
| copula-avoidance | §8 Avoidance of "is"/"are" |
| negative-parallelisms | §9 Negative Parallelisms and Tailing Negations |
| rule-of-three | §10 Rule of Three Overuse |
| elegant-variation | §11 Elegant Variation (Synonym Cycling) |
| false-ranges | §12 False Ranges |
| subjectless-fragments | §13 Passive Voice and Subjectless Fragments |
| em-dash-overuse | §14 Em Dash Overuse |
| boldface-overuse | §15 Overuse of Boldface |
| inline-header-vertical-lists | §16 Inline-Header Vertical Lists |
| abstract-tapestry-vocabulary | §17 Abstract "Tapestry" Vocabulary |
| knowledge-cutoff-hedging | §18 Knowledge-Cutoff Hedging |
| chatbot-artifacts | §19 Chatbot Artifacts |
| signposting | §20 Signposting and Announcements |
| generic-conclusion | §21 Generic Future-Looking Conclusions |
| filler-phrases | §22 Persuasive Framing Filler |
| fragmented-headers | §29 Fragmented Headers |

(Full mapping in humanizer SKILL.md sections 1-29.)

## Cadence

- **Quarterly:** rerun skill-judge on humanizer; spot-check 2-3 fixtures by manually applying the skill and diffing against expected.
- **On edit:** any structural change to humanizer SKILL.md should re-validate at least the 2 hard-difficulty fixtures (currently #8) for behavioral regressions.
- **On addition:** when a new AI-tell category is added to the skill catalog, add a fixture demonstrating it (or update an existing composite fixture).

## Source

Filed via `wr-skillhub-2026-05-06-003` item 6 (humanizer 8-point upgrade). Initial fixture set built S30 (2026-05-07). Target growth: 12-20 fixtures over time as new tell categories surface.
