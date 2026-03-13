# Scoring Calibration Guide

## Calibration Data from 100+ Evaluations

This reference provides real-world scoring patterns to help calibrate evaluations. Use when scoring a skill to verify your scores align with established patterns.

---

## D1: Knowledge Delta Calibration

D1 is the most variable dimension because it depends on domain saturation -- how well Claude's training data already covers the topic.

### Domain Saturation Hierarchy

| D1 Range | Domain Type | Why | Example Skills |
|---|---|---|---|
| 15-17 | Proprietary/tool-specific, very recent technology | Near-zero coverage in training data | hook-development (16), telegram-bot-builder (16), canvas-design (16) |
| 13-14 | Specialized cross-domain, provider-specific internals | Partial coverage, but specific gotchas are novel | voice-ai-development (14), mcp-integration (14), paywall-upgrade-cro (14), email-systems (13) |
| 11-12 | Professional domains with extensive documentation | Well-documented but expert nuance exists | senior-backend (12), copy-editing (11), micro-saas-launcher (11) |
| 8-10 | Heavily blogged, saturated with best-practice content | NNGroup, Baymard, HubSpot, etc. extensively cover these | page-cro (9), form-cro (8), popup-cro (10) |
| 4-6 | Thoroughly in training data, standard practices | Conventional commits, basic patterns well-known | git-commit-helper (4) |

### D1 Scoring Guidance

| Before Scoring D1, Ask... | If Yes | If No |
|---|---|---|
| Could Claude generate this content from training data alone? | D1 penalty (redundant content) | D1 credit (genuine delta) |
| Would a domain expert say "I learned this the hard way"? | D1 credit | D1 penalty |
| Is the content available in top-10 Google results for the domain? | D1 penalty (saturated) | D1 credit (practitioner-only) |
| Does it include quantified thresholds, provider-specific gotchas, or named failure modes? | D1 credit | Likely redundant |

### D1 Ceiling Warning

Skills in domains with D1<=8 typically score 80-95 total regardless of optimization effort. The D1 ceiling caps the total score because:
- D1 is the largest dimension (20 points max)
- Low D1 means the skill adds less genuine value
- Other dimensions can partially compensate but not fully

---

## D5: Progressive Disclosure Calibration

D5 is the dimension most directly controlled by companion files.

### D5 by Companion Status

| Companion Configuration | Typical D5 | Notes |
|---|---|---|
| No companions, no File Index | 2-3/15 | Floor score. Single-file skills max out here |
| No companions but well-organized single file | 4-5/15 | Rare. Some judges give credit for self-contained structure |
| 1-2 companions with basic listing | 7-9/15 | Listing without "Load When" triggers caps at 9 |
| 3+ companions with Load When / Do NOT Load | 13-15/15 | The target configuration. Ceiling depends on trigger quality |
| 6+ companions with Load When / Do NOT Load | 14-15/15 | Diminishing returns above 5-6 companions |
| Skeleton companions (placeholder content) | 2-4/15 | WORSE than none. False progressive disclosure penalized |
| Binary asset companions (fonts, images) | 8-10/15 | Better than none, worse than document companions |

### D5 Scoring Guidance

| Element | D5 Impact |
|---|---|
| File Index present with 3 columns (File, Load When, Do NOT Load) | +3-4 points over basic listing |
| File Index placed early in SKILL.md (first content section) | +1-2 points over bottom placement |
| "Do NOT Load" column populated for each entry | +2-3 points over Load When only |
| Companion content is genuinely distinct from SKILL.md | +2-3 points over rehashed content |
| Loading triggers embedded in workflow steps (not just File Index) | +1-2 points |

---

## Common Scoring Errors

### Arithmetic Errors

The most frequent evaluation error. After scoring all 8 dimensions, ALWAYS verify:

```
D1 + D2 + D3 + D4 + D5 + D6 + D7 + D8 = Total
```

Common mistakes:
- Off-by-one in mental addition (especially when D7 max is 10, not 15)
- Transposing dimension scores
- Forgetting to include one dimension

**Verification method**: Add dimensions in pairs -- (D1+D2) + (D3+D4) + (D5+D6) + (D7+D8) = Total

### Score Inflation Patterns

| Inflation Pattern | What Happens | Correction |
|---|---|---|
| **Length bias** | Long skill gets high scores because "it's thorough" | Length often means redundancy. Score content quality, not volume |
| **Format bias** | Well-formatted tables and headers get inflated scores | Tables can wrap redundant content. Check what's IN the tables |
| **Comparison anchoring** | Skill seems good compared to a terrible baseline | Score against the rubric absolute values, not relative to other skills |
| **D1 generosity** | Giving D1=12 for "some expert content" when most is redundant | Use the E:A:R ratio. If <50% Expert content, D1 should be <=10 |
| **D3 credit for any NEVER list** | Any anti-pattern section gets D3=10+ | Check specificity. "Avoid errors" is not an anti-pattern |

### Score Deflation Patterns

| Deflation Pattern | What Happens | Correction |
|---|---|---|
| **Unfamiliarity penalty** | Evaluator doesn't know the domain, assumes content is basic | If you don't know whether content is expert-level, research the domain first |
| **Style rigidity** | Penalizing valid approaches that don't match expected format | Multiple valid skill patterns exist. Score effectiveness, not conformity |
| **D5 unfairness to single-file skills** | Single-file skills auto-scored D5=2-3 | If the skill genuinely doesn't need companions (< 50 lines, focused scope), D5 can be 5-7 for well-organized self-containment |

---

## Dimension Interaction Patterns

Some dimensions predictably correlate:

| Pattern | Why | Implication |
|---|---|---|
| High D1 often means high D3 | Expert knowledge includes knowing what NOT to do | If D1 is high but D3 is low, check if anti-patterns were overlooked |
| High D5 requires companion files | D5 measures progressive disclosure architecture | Without companions, D5 max is ~5/15 regardless of SKILL.md quality |
| D4 requires description quality | D4 heavily weights the description field | Skills with weak descriptions rarely score D4 > 10 |
| D7 clusters at 7-9 | Most well-structured skills follow recognizable patterns | D7=10 (perfect) is rare. D7=7-8 is typical for good skills |
| D8 correlates with decision matrices | Actionable content = high D8 | Skills without decision tables rarely score D8 > 11 |
| D6 depends on skill type | Creative skills need high freedom, tool skills need low | Mismatched freedom is the most common D6 error |

---

## Sub-Grade Interpretation

| Grade | Score | What It Means | Typical Characteristics |
|---|---|---|---|
| A | 108-120 | Production expert skill. Every dimension strong | D1>=15, companions with triggers, named anti-patterns, decision matrices throughout |
| A- | 104-107 | Very strong with 1-2 minor weaknesses | Usually D7=8 (slightly non-ideal pattern match) or D6=12 (freedom slightly off) |
| B+ | 100-103 | Strong, passes quality gate comfortably | Solid across all dimensions. May have D1=12-13 in moderately saturated domain |
| B | 96-99 | Good, passes quality gate | May lack companions (D5=5-7) compensated by strong content, or has companions but domain-saturated D1 |
| C+ | 90-95 | Near quality gate. 1-6 points from B | Usually fixable with targeted companion addition or content strengthening |
| C | 80-89 | Adequate. Clear improvement path | Typically missing companions (D5=2-3) or domain-saturated (D1<=10) |
| C- | 70-79 | Below average. Significant gaps | Multiple weak dimensions. Usually needs structural changes |
| D+ | 60-69 | Poor. Fundamental issues | Often template-heavy with low knowledge delta |
| F | <60 | Needs complete redesign | Multiple critical failures across dimensions |
