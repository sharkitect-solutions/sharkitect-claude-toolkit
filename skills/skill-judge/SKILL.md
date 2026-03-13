---
name: skill-judge
description: "Use when evaluating, auditing, scoring, or reviewing Agent Skills (SKILL.md files) for quality. Use when comparing skills, running skill quality audits, benchmarking skill effectiveness, or deciding which skills need optimization. Use when a user says 'score this skill', 'evaluate this skill', 'audit my skills', 'how good is this skill'. Do NOT use for: ultimate-skill-creator (creating new skills), skill-creator (lightweight skill creation), superpowers:writing-skills (auto-triggered writing workflows)."
---

# Skill Judge

Evaluate Agent Skills against official specifications and patterns derived from 100+ evaluations across 110 skills.

---

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/common-failures.md` | First evaluation of session, unfamiliar with the 9 failure patterns, need quick reference checklist | Already evaluated 2+ skills this session (patterns memorized) |
| `references/scoring-calibration.md` | Unsure about D1 for a domain, need companion impact data for D5, verifying sub-grade thresholds, checking for scoring errors | Confident in calibration from recent evaluations |
| `references/dimension-examples.md` | Need concrete high/low examples for a specific dimension, calibrating for unfamiliar skill type | Already calibrated from recent similar evaluations |

---

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Score/evaluate this skill" | YES | - |
| "Audit all my skills for quality" | YES | - |
| "Compare these two skills" | YES | - |
| "Which skills need optimization?" | YES | - |
| "Create a new skill" | NO | ultimate-skill-creator |
| "Write/improve skill content" | NO | superpowers:writing-skills |
| "Review this code for quality" | NO | clean-code or code-reviewer agent |
| "Evaluate this agent's performance" | NO | agent-evaluation |

---

## Core Philosophy

### The Core Formula

> **Good Skill = Expert-only Knowledge - What Claude Already Knows**

A Skill's value is its **knowledge delta** -- the gap between what it provides and what the model already knows. When a Skill explains basics or standard library usage, it wastes context tokens -- a shared resource with system prompts, conversation history, and user requests.

### Three Types of Knowledge

| Type | Definition | Treatment |
|------|------------|-----------|
| **Expert** | Claude genuinely doesn't know this | Must keep -- this is the Skill's value |
| **Activation** | Claude knows but may not think of | Keep if brief -- serves as reminder |
| **Redundant** | Claude definitely knows this | Delete -- wastes tokens |

The art of Skill design: maximize Expert content, use Activation sparingly, eliminate Redundant ruthlessly. Good Skill: >70% Expert, <20% Activation, <10% Redundant.

### Tool vs Skill

| Concept | Essence | Function |
|---------|---------|----------|
| **Tool** | What model CAN do | Execute actions (bash, read, write, WebSearch) |
| **Skill** | What model KNOWS how to do | Guide decisions (expert patterns, anti-patterns, decision trees) |

`General Agent + Excellent Skill = Domain Expert Agent`

---

## Evaluation Dimensions (120 points total)

### D1: Knowledge Delta (20 points) -- THE CORE DIMENSION

Does the Skill add genuine expert knowledge Claude doesn't have?

| Score | Criteria |
|-------|----------|
| 0-5 | Explains basics Claude knows (tutorials, standard library usage, generic best practices) |
| 6-10 | Mixed: some expert knowledge diluted by obvious content |
| 11-15 | Mostly expert knowledge with minimal redundancy |
| 16-20 | Pure knowledge delta -- every paragraph earns its tokens |

**Red flags** (instant <=5): "What is X" sections, step-by-step standard tutorials, common library docs, generic advice ("write clean code").

**Green flags** (high delta): Decision trees for non-obvious choices, trade-offs only experts know, real-world edge cases, "NEVER do X because [non-obvious reason]", domain-specific thinking frameworks.

**Evaluation**: For each section ask "Does Claude already know this?" Mark as [E]xpert, [A]ctivation, or [R]edundant. Calculate ratio.

---

### D2: Mindset + Appropriate Procedures (15 points)

Does the Skill transfer expert **thinking patterns** AND **domain-specific procedures**?

| Score | Criteria |
|-------|----------|
| 0-3 | Only generic procedures Claude already knows |
| 4-7 | Has domain procedures but lacks thinking frameworks |
| 8-11 | Good balance: thinking patterns + domain-specific workflows |
| 12-15 | Expert-level: shapes thinking AND provides novel procedures |

**Valuable**: "Before [action], ask yourself..." thinking frameworks. Domain-specific workflows with non-obvious ordering or critical steps. **Redundant**: Generic steps (open, edit, save). Standard programming patterns.

---

### D3: Anti-Pattern Quality (15 points)

Does the Skill have effective NEVER lists with specific, named patterns?

| Score | Criteria |
|-------|----------|
| 0-3 | No anti-patterns mentioned |
| 4-7 | Generic warnings ("avoid errors", "be careful") |
| 8-11 | Specific NEVER list with some reasoning |
| 12-15 | Named anti-patterns with WHY -- things only experience teaches |

**The test**: Would an expert say "I learned this the hard way"? Named patterns ("The Autopilot", "The Status Novel") with what-happens, why-it-fails, and fix columns score highest.

---

### D4: Specification Compliance (15 points)

Does the Skill follow format requirements? **Special focus on description quality.**

| Score | Criteria |
|-------|----------|
| 0-5 | Missing frontmatter or invalid format |
| 6-10 | Has frontmatter but description is vague or incomplete |
| 11-13 | Valid frontmatter, trigger conditions present but weak exclusions or no Scope Boundary |
| 14-15 | Perfect: trigger conditions + exclusions in description, Scope Boundary table in body |

**Description must contain**: Trigger conditions ("Use when..."), specific phrases in quotes, searchable keywords, exclusions ("Do NOT use for: [skill] ([purpose])"). Description must NEVER summarize workflow or content -- this is the cardinal CSO rule.

**Why description is critical**: It's the ONLY thing Claude reads when deciding whether to load a skill. Poor description = invisible skill regardless of content quality.

---

### D5: Progressive Disclosure (15 points)

Does the Skill implement proper content layering?

| Score | Criteria |
|-------|----------|
| 0-5 | Everything in SKILL.md (>500 lines) or skeleton companions with no real content |
| 6-10 | Has companions but no explicit loading triggers |
| 11-13 | Good layering with File Index including Load When triggers |
| 14-15 | Perfect: File Index with Load When + Do NOT Load, triggers embedded in workflow |

**With companion files**: Check File Index -- 3 columns (File, Load When, Do NOT Load)? Placed early in SKILL.md? Real content in companions (not skeletons)?

**Simple Skills** (<100 lines, no companions): Score based on conciseness and self-containment. Max ~7/15 for well-organized single-file skills.

---

### D6: Freedom Calibration (15 points)

Is specificity appropriate for the task's fragility?

| Score | Criteria |
|-------|----------|
| 0-5 | Severely mismatched (rigid scripts for creative tasks, vague for fragile operations) |
| 6-10 | Partially appropriate |
| 11-13 | Good calibration for most scenarios |
| 14-15 | Perfect freedom calibration throughout |

| Task Type | Should Have | Why |
|-----------|-------------|-----|
| Creative/Design | High freedom (principles, not steps) | Multiple valid approaches |
| Code review/judgment | Medium freedom (priorities + judgment) | Principles exist but context varies |
| File format operations | Low freedom (exact scripts, no deviation) | One wrong byte corrupts file |

**The test**: "If Agent makes a mistake, what's the consequence?" High consequence = low freedom.

---

### D7: Pattern Recognition (10 points)

Does the Skill follow an established design pattern?

| Pattern | ~Lines | When to Use |
|---------|--------|-------------|
| **Mindset** | ~50 | Creative tasks requiring taste |
| **Navigation** | ~30 | Multiple distinct sub-scenarios |
| **Philosophy** | ~150 | Art/creation requiring originality |
| **Process** | ~200 | Complex multi-step projects |
| **Tool** | ~300 | Precise operations on formats |

| Score | Criteria |
|-------|----------|
| 0-3 | No recognizable pattern, chaotic structure |
| 4-6 | Partially follows a pattern |
| 7-8 | Clear pattern with minor deviations |
| 9-10 | Masterful application of appropriate pattern |

---

### D8: Practical Usability (15 points)

Can an Agent actually use this Skill effectively?

| Score | Criteria |
|-------|----------|
| 0-5 | Confusing, incomplete, contradictory guidance |
| 6-10 | Usable but with noticeable gaps |
| 11-13 | Clear guidance for common cases |
| 14-15 | Comprehensive: decision trees + fallbacks + edge cases |

**Check for**: Decision trees for multi-path scenarios, working code examples, error handling and fallbacks, edge case coverage, immediate actionability.

---

## Grade Scale

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 108-120 | Excellent -- production expert skill |
| A- | 104-107 | Very strong with minor polish needed |
| B+ | 100-103 | Strong, passes quality gate comfortably |
| B | 96-99 | Good, passes quality gate |
| C+ | 90-95 | Near quality gate, targeted fixes can reach B |
| C | 80-89 | Adequate, clear improvement path |
| C- | 70-79 | Below average, significant gaps |
| D+ | 60-69 | Poor, needs fundamental restructuring |
| F | <60 | Needs complete redesign |

---

## NEVER Do When Evaluating

- **NEVER** give high scores because it "looks professional" or is well-formatted
- **NEVER** ignore token waste -- every redundant paragraph deducts from D1
- **NEVER** let length impress you -- a 43-line Skill can outperform a 500-line Skill
- **NEVER** skip mentally testing decision trees -- do they lead to correct choices?
- **NEVER** forgive explaining basics with "but it provides helpful context"
- **NEVER** assume all procedures are valuable -- distinguish domain-specific from generic
- **NEVER** undervalue the description field -- poor description = skill never gets used
- **NEVER** put "when to use" info only in the body -- Agent only sees description before loading
- **NEVER** skip arithmetic verification -- confirm D1+D2+D3+D4+D5+D6+D7+D8 = Total

---

## Rationalizations That Inflate Scores

| Rationalization | When It Appears | Why It's Wrong |
|---|---|---|
| "It's long and thorough, so it must be good" | Skill is 500+ lines | Length often means redundancy. A 43-line mindset skill can outperform an 800-line dump |
| "It has nice formatting and tables" | Well-structured layout | Formatting wraps content, doesn't create knowledge delta. Score content, not presentation |
| "It covers all the basics well" | Clear fundamentals | Covering basics = covering what Claude already knows. Redundant, not valuable |
| "The procedures are detailed" | Step-by-step tutorials | Detailed GENERIC procedures waste tokens. Only domain-specific procedures have value |
| "It has code examples" | Multiple snippets | Code Claude could generate itself is redundant. Only non-obvious patterns add value |
| "The description is clear" | Readable description | Readability isn't the metric. Does it have triggers, WHEN scenarios, and exclusions? |
| "It's better than nothing" | Comparing to baseline | A bad skill wastes context and may teach wrong patterns. Sometimes no skill IS better |

---

## Evaluation Protocol

### Step 1: Knowledge Delta Scan

Read SKILL.md completely. Mark each section [E]xpert, [A]ctivation, or [R]edundant. Calculate E:A:R ratio.

### Step 2: Structure Analysis

Check: frontmatter validity, total lines, companion files and sizes, pattern identification, loading triggers presence.

### Step 3: Score Each Dimension

For each of 8 dimensions: find specific evidence (quote relevant lines), assign score with one-line justification.

### Step 4: Calculate Total & Verify Arithmetic

```
Total = D1 + D2 + D3 + D4 + D5 + D6 + D7 + D8 (Max = 120)
```

**MANDATORY verification**: Add in pairs -- (D1+D2) + (D3+D4) + (D5+D6) + (D7+D8) = Total. Arithmetic errors are the most common evaluation failure across 100+ evaluations.

### Step 5: Generate Report

Include: Total/120 with grade, dimension table with scores and notes, critical issues, top 3 improvements with specific guidance.

---

## The Meta-Question

> **"Would an expert in this domain say: 'Yes, this captures knowledge that took me years to learn'?"**

If yes -- the Skill has genuine value. If no -- it's compressing what Claude already knows.
