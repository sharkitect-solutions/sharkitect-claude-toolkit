# Skill Directory Template

## Standard Layout

```
my-skill-name/
  SKILL.md                    # Required — core skill with frontmatter
  references/                 # Optional — deep-dive content
    topic-a.md                #   Detailed reference loaded on demand
    topic-b.md                #   Another reference topic
  scripts/                    # Optional — reusable code
    utility.py                #   Production-ready script
    utility.ts                #   TypeScript variant if needed
  examples/                   # Optional — complete working demos
    full-example.py           #   Runnable implementation
```

## Frontmatter Template

```yaml
---
name: my-skill-name
description: >
  Use when [primary triggering condition]. Use when a user says "[trigger phrase 1]",
  "[trigger phrase 2]", or "[trigger phrase 3]". Use when [edge case that should still
  trigger — describe the risk]. Use when [technology-specific trigger with named
  providers or tools]. Use when [indirect indicator that this skill is relevant].
  This skill applies to [scope assertion] — including [commonly-skipped cases].
---
```

## SKILL.md Body Template

```markdown
# My Skill Name

## Why This Skill Exists

[2-3 sentences explaining the problem this skill solves. Name Claude's default failure
mode explicitly. State why the default behavior is wrong.]

## The Core Failure Pattern

[Describe what Claude does WITHOUT this skill. Be specific — name the exact sequence
of bad decisions Claude makes. This section confronts Claude with its own behavior.]

## Rationalization Table

[Pre-empt Claude's excuses for skipping the skill's rules.]

| Rationalization | When It Appears | Why It Is Wrong |
|---|---|---|
| "[Excuse 1]" | [Context when this excuse surfaces] | [Concrete counterargument] |
| "[Excuse 2]" | [Context] | [Counterargument] |
| "[Excuse 3]" | [Context] | [Counterargument] |
| "[Excuse 4]" | [Context] | [Counterargument] |

## Non-Negotiable Rules

### 1. [Rule Name]

[Imperative statement of the rule.] [1-2 sentences explaining WHY.]

### 2. [Rule Name]

[Imperative statement.] [Why.]

### 3. [Rule Name]

[Imperative statement.] [Why.]

[Continue for 3-5 rules. More than 5 rules should be split — some belong in references.]

## Red Flags Checklist

[Specific patterns indicating the skill is being violated.]

- [ ] [Specific bad pattern 1]
- [ ] [Specific bad pattern 2]
- [ ] [Specific bad pattern 3]
- [ ] [Specific bad pattern 4]
- [ ] [Specific bad pattern 5]

## [Domain-Specific Section]

[Key patterns, code examples, decision tables, or guidance specific to this skill's
domain. Keep it focused — details go in references.]

See `references/topic-a.md` for [what it contains].
See `references/topic-b.md` for [what it contains].

## File Index

| File | Purpose |
|---|---|
| `references/topic-a.md` | [What this file contains and when to use it] |
| `references/topic-b.md` | [What this file contains and when to use it] |
| `scripts/utility.py` | [What this script does] |
| `examples/full-example.py` | [What this example demonstrates] |
```

## Checklist for New Skills

Use this checklist when creating any new skill:

### Structure (Stage 1)
- [ ] Directory created with skill name in kebab-case
- [ ] SKILL.md created with valid YAML frontmatter
- [ ] `name` field matches directory name
- [ ] `description` contains ONLY "Use when..." triggering conditions
- [ ] `description` does NOT summarize content or list features
- [ ] `description` is 100-200 words
- [ ] Planned which content goes in body vs references

### Content (Stage 2)
- [ ] 3 pressure scenarios created and run as baseline tests
- [ ] Rationalizations captured from baseline tests
- [ ] Rationalization table has 4+ entries with "When It Appears" column
- [ ] Non-negotiable rules written in imperative voice with "why"
- [ ] Red flags checklist has 5+ specific items
- [ ] Code examples show both wrong and right patterns (if coding skill)
- [ ] SKILL.md body is 1,500-2,000 words
- [ ] No hedging language ("might", "could", "consider")
- [ ] Detail pushed to references, not duplicated in body

### Testing (Stage 3)
- [ ] 10+ should-trigger test cases created
- [ ] 5+ should-NOT-trigger test cases created
- [ ] 3+ pressure test cases created
- [ ] Subagent evaluations run (with-skill vs baseline)
- [ ] All pressure tests pass (skill resists)
- [ ] Trigger precision > 90%
- [ ] Trigger recall > 90%
- [ ] Description optimized based on test results

### Polish
- [ ] File index table complete and accurate
- [ ] Zero content duplication between body and references
- [ ] All referenced files exist
- [ ] Scripts are runnable
- [ ] Examples are complete and self-contained
