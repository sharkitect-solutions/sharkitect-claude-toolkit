---
name: hq-reverse-engineering
description: >
  Use when the user wants to reverse engineer a competitor's product or approach, analyze a YouTube video or tutorial
  to extract architectural insights, deconstruct an existing system to understand how it works, or gather structured
  competitive intelligence from vague or unstructured sources with confidence-level scoring.
  NEVER use for standard competitive market research with public data (use competitive-intelligence-analyst agent),
  general web research without reverse engineering intent (use search-specialist agent),
  or analyzing your own codebase (use code-reviewer or architect-reviewer agents).
version: 0.1.0
---

# HQ Reverse Engineering — System Deconstruction & Intelligence Extraction

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/analysis-framework.md` | Starting any reverse engineering analysis | Quick competitive lookups without structural analysis |
| `references/intelligence-template.md` | Producing a structured intelligence report | Informal analysis or quick answers |
| `references/downstream-routing.md` | Feeding intelligence into other workflows (blueprinting, building) | Standalone analysis with no build intent |

## Paired Agent

Launch `reverse-engineer` agent (Task tool, model: opus) for execution:
- Deep analysis of YouTube videos, tutorials, competitor demos
- Multi-source research combining web scraping, docs, and inference
- Structured intelligence reports with confidence scoring
- System architecture extraction from vague or incomplete information

Support agents (launched alongside or after):
- `search-specialist` — Broad web research to supplement findings
- `competitive-intelligence-analyst` — Market positioning context

Use this skill directly (without agent) for:
- Quick classification of input type (video, product, tutorial)
- Deciding whether reverse engineering is the right approach vs simpler research
- Reviewing and routing completed intelligence reports

## When to Reverse Engineer vs When to Research

```
USER WANTS COMPETITIVE INTELLIGENCE
  |
  +-- Is the information publicly documented (pricing, features, blog posts)?
  |     YES --> Use competitive-intelligence-analyst agent (standard research)
  |     NO  --> Continue
  |
  +-- Is the user providing VAGUE or UNSTRUCTURED input (video, demo, tutorial)?
  |     YES --> Use reverse-engineer agent (this skill)
  |     NO  --> Continue
  |
  +-- Does the user want to understand HOW something was built (architecture, patterns)?
  |     YES --> Use reverse-engineer agent (this skill)
  |     NO  --> Use search-specialist or competitive-intelligence-analyst
  |
  +-- Does the user want to REPLICATE or IMPROVE on a competitor's approach?
        YES --> Use reverse-engineer agent, then route output to blueprinting
        NO  --> Standard competitive intelligence is sufficient
```

## Input Types Accepted

| Input Type | How to Process | Confidence Baseline |
|-----------|---------------|---------------------|
| **YouTube video transcript** | Extract claims, identify architecture hints, separate fact from speculation | LOW (60%) — videos are curated, incomplete |
| **Product demo/walkthrough** | Map UI flows to backend architecture, identify integrations | MEDIUM (70%) — UI reveals patterns |
| **Tutorial/how-to** | Extract exact steps, identify tools/frameworks, assess completeness | HIGH (80%) — tutorials aim for accuracy |
| **Blog post/article** | Extract technical decisions, cross-reference with other sources | MEDIUM (70%) — depends on author's depth |
| **Competitor website** | Scrape via Firecrawl, analyze tech stack signals, map feature set | MEDIUM (70%) — public info is curated |
| **Code repository** | Direct analysis of architecture, dependencies, patterns | VERY HIGH (90%) — code doesn't lie |
| **User complaint/review** | Identify pain points, infer system limitations | LOW (55%) — subjective, often incomplete |

## Confidence Scoring System

Every finding MUST be tagged with a confidence level:

| Level | Score | Meaning | Basis |
|-------|-------|---------|-------|
| **CONFIRMED** | 90-100% | Verified through direct evidence | Code, official docs, multiple independent sources |
| **HIGH** | 75-89% | Strong evidence, minor inference | Tutorial with code samples, consistent patterns across sources |
| **MEDIUM** | 60-74% | Reasonable inference from partial evidence | Demo walkthrough, architecture hints, industry patterns |
| **LOW** | 40-59% | Educated guess based on limited evidence | Vague video claims, single source, heavy inference |
| **SPECULATIVE** | <40% | Hypothesis requiring validation | No direct evidence, based on patterns or analogies |

**Rule**: Never present SPECULATIVE findings as facts. Always label confidence explicitly.

## Anti-Patterns

1. **Confidence Inflation**: Treating a YouTube creator's claim as HIGH confidence without corroboration. One source = LOW unless it's code or official documentation.
2. **Architecture Assumption**: Assuming a competitor uses a specific technology based on UI alone. UI reveals patterns, not implementations.
3. **Ignoring Business Model**: Reverse engineering only the technology while missing the business model that makes it work. Technical architecture serves business goals.
4. **Analysis Paralysis**: Spending 10 hours reverse engineering when 2 hours would yield 80% of the insights. Diminishing returns apply heavily.
5. **Building Without Validating**: Taking reverse engineering output directly to implementation without validating key assumptions. Always flag LOW/SPECULATIVE items for validation before building.
6. **Survivorship Bias**: Only analyzing successful competitors skews architecture assumptions. Research shows ~40% of "best practices" attributed to winners are actually irrelevant to their success (they succeeded despite those choices, not because of them). Always include at least one failed or pivoted competitor in the analysis set to calibrate what actually matters vs what is incidental.
7. **Source Circularity**: Three articles citing the same original blog post is 1 source, not 3. Failing to trace citations back to their origin overestimates confidence by 20-30%. Before upgrading any finding from LOW to MEDIUM or MEDIUM to HIGH based on "multiple sources," verify the sources are genuinely independent — different authors, different data, different observation dates.
8. **Reverse Anchoring**: The first architecture interpretation frames all subsequent analysis, causing confirmation bias in ~65% of multi-source analyses. Mitigate by writing down at least 2 alternative hypotheses BEFORE deep inference begins (see ACH framework in analysis-framework.md). If you catch yourself dismissing contradictory evidence as "probably wrong," you are anchored.
