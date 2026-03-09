# Skill Structure Guide

## Directory Layout

Every skill lives in its own directory under `~/.claude/skills/` (standalone) or within
a plugin's `skills/` directory. The standard layout:

```
skill-name/
  SKILL.md              # Required. Core skill file with frontmatter + body.
  references/           # Optional. Deep-dive content loaded on demand.
    topic-a.md
    topic-b.md
  scripts/              # Optional. Reusable code the skill teaches.
    utility.py
    utility.ts
  examples/             # Optional. Complete working implementations.
    full-example.py
  assets/               # Optional. Images, diagrams, data files.
    diagram.png
```

## Frontmatter Format

Every SKILL.md starts with YAML frontmatter between `---` delimiters:

```yaml
---
name: skill-name-in-kebab-case
description: >
  Use when [triggering condition]. Use when [another condition]. Use when a user
  says "[quoted trigger phrase]" or "[another phrase]". Keywords: term1, term2.
---
```

### Name Rules

- Use kebab-case (lowercase with hyphens)
- Be specific: `api-rate-limit-handler` not `api-helper`
- Match the directory name exactly

### Description Rules

The description determines whether the skill triggers. It is the single most important
factor in skill effectiveness — a skill that never loads is a skill that doesn't exist.

**One rule:** every sentence starts with "Use when..." and describes WHEN to load the
skill, never WHAT the skill contains. Target: 100-200 words.

See `writing-rules.md` for the complete CSO (Claude Search Optimization) framework,
including good vs bad examples, the pushiness rule, and description red flags.

## Size Targets

| Component | Target Size | Hard Limit | Rationale |
|---|---|---|---|
| Description | 100-200 words | 300 words | Loaded for EVERY query — keep lean |
| SKILL.md body | 1,500-2,000 words | 2,500 words | Loaded when triggered — balance depth vs context cost |
| Reference file | 1,000-3,000 words | 5,000 words | Loaded on demand — can be more detailed |
| Script file | As needed | No limit | Code should be complete and runnable |
| Example file | As needed | No limit | Should demonstrate real-world usage |

### Why These Targets Matter

Claude's context window is shared across the entire conversation. Every word in a skill
consumes context that could be used for the user's actual task. The progressive disclosure
system exists to minimize this cost:

1. **Metadata** (~100 words) — loaded for EVERY query to decide if the skill is relevant.
   Must be ultra-lean.
2. **Body** (1,500-2,000 words) — loaded ONLY when the skill triggers. Contains the
   essential rules and patterns Claude needs to change its behavior.
3. **Resources** (unlimited) — loaded ONLY when Claude needs specific details. Contains
   implementation specifics, provider docs, deep dives.

## File Organization Principles

### What goes in the body vs references

**In the body (SKILL.md):**
- Non-negotiable rules (the "must" statements)
- Rationalization table (pressure defense)
- Red flags checklist (self-check)
- Key patterns with brief code examples
- Pointers to references for detail

**In references:**
- Full implementations (complete code)
- Provider-specific details
- Algorithm deep dives
- Historical context / "why" essays
- Edge case catalogs

**Rule of thumb:** If removing it from the body would make a rule unclear, keep it.
If it's supporting detail that enriches understanding but isn't required for compliance,
move it to a reference.

### Zero Duplication Rule

Never repeat content between the body and references. The body should POINT to references,
not summarize them. If Claude reads a summary in the body, it may skip the reference
entirely — defeating the purpose of having the reference.

**Bad:**
```
## Circuit Breaker Pattern
A circuit breaker has three states: closed, open, and half-open. [500 words of detail]
For more details, see `references/patterns.md`.
```

**Good:**
```
## When to Use Circuit Breakers
Use a circuit breaker when an API returns 500/503 consistently for 30+ seconds.
See `references/patterns.md` for the full implementation pattern.
```

## File Index Table

Every SKILL.md that includes bundled resources MUST have a file index table at the bottom.
This tells Claude (and human readers) exactly what each file contains and when to use it.

```markdown
## File Index

| File | Purpose |
|---|---|
| `references/patterns.md` | Advanced patterns: circuit breaker, token bucket, adaptive limiting |
| `references/providers.md` | Provider-specific rate limits for OpenAI, Stripe, GitHub, AWS |
| `scripts/retry.py` | Production-ready retry decorator with backoff and jitter |
| `examples/client.py` | Complete API client demonstrating all patterns together |
```

## Frontmatter Validation Checklist

Before finalizing any skill, verify:

- [ ] `name` field matches the directory name exactly
- [ ] `name` uses kebab-case with no spaces or underscores
- [ ] `description` starts with "Use when..."
- [ ] `description` contains no workflow summary
- [ ] `description` contains no feature list
- [ ] `description` is 100-200 words
- [ ] YAML frontmatter parses without errors (test with a YAML linter if unsure)
- [ ] The `>` folded block scalar is used for multi-line descriptions

## Common Structure Mistakes

**Flat file dump.** Putting everything in SKILL.md with no references. Results in a
3,000+ word body that consumes excessive context every time it triggers.

**Over-structured.** Creating 10 reference files for a skill that only needs 2.
Each file has overhead (Claude must decide whether to open it). Keep the number small.

**Scripts without context.** Including a script but never mentioning it in the body.
Claude won't know to use it. Always reference scripts from the body with a clear
explanation of when and why to use them.

**Examples that don't run.** If you include an example, it must be complete and
self-contained. Partial examples that require external setup confuse more than they help.

**Missing frontmatter.** The YAML frontmatter is required. Without it, the skill system
can't index or trigger the skill. No frontmatter = invisible skill.
