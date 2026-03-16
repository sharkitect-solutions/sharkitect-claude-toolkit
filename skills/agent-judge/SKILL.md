---
name: agent-judge
description: >
  Use when evaluating, auditing, scoring, or reviewing Claude Code native agents
  (.md files in ~/.claude/agents/) for quality. Use when comparing agents, running
  agent quality audits, benchmarking agent effectiveness, or deciding which agents
  need optimization. Use when a user says "score this agent", "evaluate this agent",
  "audit my agents", "how good is this agent", "rate this agent". Do NOT use for:
  skill-judge (evaluating SKILL.md files), ultimate-agent-creator (creating new
  agents), agent-development (structural guidance for plugin agents),
  agent-evaluation (runtime performance testing).
---

# Agent Judge

Evaluate Claude Code native agents against an 8-dimension rubric derived from 38+ agent evaluations and the proven skills pipeline (100+ skill evaluations).

---

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/agent-common-failures.md` | First evaluation of session, unfamiliar with the 4 agent failure patterns, need quick reference | Already evaluated 2+ agents this session (patterns memorized) |
| `references/agent-scoring-calibration.md` | Unsure about D1 for a domain, need D5/D7 calibration data, verifying thresholds, checking for scoring errors | Confident in calibration from recent evaluations |
| `references/agent-dimension-examples.md` | Need concrete high/low examples for a specific dimension, calibrating for unfamiliar agent type | Already calibrated from recent similar evaluations |

---

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Score/evaluate this agent" | YES | - |
| "Audit all my agents for quality" | YES | - |
| "Compare these two agents" | YES | - |
| "Which agents need optimization?" | YES | - |
| "Score this skill (SKILL.md)" | NO | skill-judge |
| "Create a new agent" | NO | ultimate-agent-creator |
| "Help me build a plugin agent" | NO | agent-development |
| "Test this agent's runtime performance" | NO | agent-evaluation |

---

## Core Philosophy

### The Agent Value Formula

> **Good Agent = Expert System Prompt + Precision Triggering + Right-Sized Tools**

An agent's value comes from three sources:
1. **Knowledge delta** -- expert content Claude doesn't have from training
2. **Triggering precision** -- description fires for right tasks, never for wrong ones
3. **Scoping discipline** -- minimum tools, appropriate model, structured output

### Agent vs Skill

| Concept | Format | Triggering | Body Function |
|---------|--------|------------|---------------|
| **Skill** | Directory with SKILL.md + references | Description + skill-specific loading | Expert knowledge, loaded on demand |
| **Agent** | Single `.md` file (+ optional references/) | Description read for EVERY message | System prompt shaping subagent behavior |

Critical difference: Claude reads ALL 38 agent descriptions on every message to decide which to invoke. Bad description = great agent that never fires. Every description costs orchestrator tokens.

### Three Knowledge Types (Same as Skills)

| Type | Definition | Treatment |
|------|------------|-----------|
| **Expert** | Claude genuinely doesn't know this | Must keep -- this is the agent's value |
| **Activation** | Claude knows but may not apply | Keep if brief -- serves as behavioral trigger |
| **Redundant** | Claude definitely knows this | Delete -- wastes context tokens in subagent |

Good agent body: >60% Expert, <25% Activation, <15% Redundant. Body sweet spot: 150-350 lines.

---

## Evaluation Dimensions (120 points total)

### D1: Knowledge Delta (20 points) -- THE CORE DIMENSION

Does the agent body add genuine expert knowledge Claude doesn't have?

| Score | Criteria |
|-------|----------|
| 0-5 | Explains basics Claude knows (generic best practices, standard procedures, tutorial content) |
| 6-10 | Mixed: some expert knowledge diluted by obvious content (bullet-list syndrome) |
| 11-15 | Mostly expert knowledge with minimal redundancy |
| 16-20 | Pure knowledge delta -- every section earns its context tokens |

**Red flags** (instant <=5): "What is X" sections, generic advice ("write clean code", "follow best practices"), standard library usage, content available in top-10 Google results.

**Green flags** (high delta): Decision trees for non-obvious choices, trade-offs only practitioners know, named failure modes with non-obvious consequences, domain-specific thinking frameworks, cross-domain insights (behavioral economics in CRO, kernel internals in DevOps).

**Evaluation**: Mark each body section [E]xpert, [A]ctivation, or [R]edundant. Calculate ratio.

---

### D2: Mindset & Procedures (15 points)

Does the agent transfer expert **thinking patterns** and **domain-specific procedures**?

| Score | Criteria |
|-------|----------|
| 0-3 | Only generic procedures or bullet lists of obvious steps |
| 4-7 | Has some domain procedures but relies on bullet-list format |
| 8-11 | Decision trees and branching logic, not just bullet lists |
| 12-15 | Expert-level: decision trees + domain workflows + "before X, assess Y" frameworks |

**Bullet-list test**: If the body is >40% bullet lists, D2 caps at 7. Decision trees, rationalization tables, and conditional logic score higher than any bullet list.

---

### D3: Anti-Pattern Quality (15 points)

Does the agent have effective NEVER lists with specific, named patterns?

| Score | Criteria |
|-------|----------|
| 0-3 | No anti-patterns or only generic warnings ("avoid errors", "be careful") |
| 4-7 | Some anti-patterns but unnamed or missing the WHY |
| 8-11 | 3-5 named anti-patterns with reasoning |
| 12-15 | 5-8+ named anti-patterns with WHY + consequences. Things only experience teaches. |

**The test**: Would a practitioner say "I learned this the hard way"? Named patterns with what-happens-if-violated and fix columns score highest.

**Agent-specific anti-patterns to look for**: Over-triggering, under-triggering, over-permissioned tools, generic output, scope creep, missing edge cases.

---

### D4: Spec Compliance (15 points)

Does the agent follow structural requirements?

| Score | Criteria |
|-------|----------|
| 0-5 | Missing or invalid frontmatter |
| 6-8 | Has frontmatter but description is vague, missing trigger conditions |
| 9-11 | Valid frontmatter, trigger conditions present, but weak exclusions |
| 12-13 | Valid frontmatter, trigger conditions + exclusions, tools declared |
| 14-15 | Perfect: triggers + exclusions in description, tools + model in frontmatter, Scope Boundary table or equivalent in body |

**Required frontmatter fields**: `name`, `description`, `tools` (list). Optional but scored: `model`.

**Description rules**: Must contain trigger conditions ("Use when..."), example phrasings users would say, and exclusions ("Do NOT use for: [agent] ([purpose])"). Description must NEVER summarize the agent's workflow or content.

---

### D5: Description & Triggering (15 points) -- HIGHEST-LEVERAGE DIMENSION

Does the description enable precise, reliable triggering?

| Score | Criteria |
|-------|----------|
| 0-3 | No `<example>` blocks. Description is a single sentence or vague summary. |
| 4-6 | 1 example, or examples without `<commentary>`, or same phrasing repeated. |
| 7-9 | 2 examples with varied phrasings and commentary, reactive triggers only. |
| 10-12 | 3 examples covering reactive + proactive, varied contexts. |
| 13-15 | 3-4 examples, reactive + proactive + edge case, negative boundary ("Do NOT use for..."), `<commentary>` on every example explaining WHY. |

**Why D5 matters most for agents**: Claude reads ALL descriptions on every message. A 337-line expert body behind a 1-sentence description is invisible. Description quality determines whether the agent exists in practice.

**Phrasing variety test**: Do examples use different words for the same intent? "review my code" / "check these changes" / "look over this PR" = good variety. Same words 3 times = no variety.

---

### D6: Freedom Calibration (15 points)

Is specificity appropriate for the task's fragility?

| Score | Criteria |
|-------|----------|
| 0-5 | Severely mismatched (rigid scripts for creative tasks, vague for fragile operations) |
| 6-10 | Partially appropriate |
| 11-13 | Good calibration for most scenarios |
| 14-15 | Perfect freedom calibration throughout |

| Agent Type | Should Have | Why |
|-----------|-------------|-----|
| Creative (content writing, design review) | High freedom -- principles, not scripts | Multiple valid approaches |
| Analysis (code review, security audit) | Medium freedom -- criteria + judgment | Clear standards but context varies |
| Execution (deployment, file ops, build) | Low freedom -- exact procedures, no deviation | Mistakes are expensive/irreversible |
| Coordination (multi-agent, project mgmt) | Medium-high freedom -- frameworks, not micromanagement | Must adapt to varied contexts |

---

### D7: Tool & Model Scoping (10 points) -- AGENT-UNIQUE DIMENSION

Are tools least-privilege and model appropriate?

| Score | Criteria |
|-------|----------|
| 0-3 | Tools omitted or wildly over-permissioned (Bash + Write for a read-only review agent) |
| 4-6 | Tools present but too broad, or model not specified |
| 7-8 | Appropriately scoped tools, model reasonable |
| 9-10 | Minimum necessary tools, model matches complexity, body-tool alignment verified |

**Tool scoping guide**:

| Agent Purpose | Appropriate Tools |
|--------------|-------------------|
| Read-only analysis (review, audit) | Read, Glob, Grep |
| Code generation/modification | + Write, Edit, Bash |
| Research/web-aware | + WebSearch, WebFetch |
| Delegation/coordination | + Task |

**Body-tool alignment check**: If body says "search the codebase", agent needs Glob + Grep. If body says "delegate to specialists", agent needs Task. Misalignment = -2 points.

**Model guide**: haiku = simple/fast, sonnet = most agents, opus = complex reasoning. Omit = inherit from parent (acceptable default).

---

### D8: Practical Usability (15 points)

Can the orchestrator actually use this agent's output effectively?

| Score | Criteria |
|-------|----------|
| 0-5 | No output format, no edge cases, agent returns unstructured text |
| 6-10 | Some structure but inconsistent, missing edge cases |
| 11-13 | Clear output format template, common cases covered |
| 14-15 | Structured output format, edge cases, confidence levels, actionable recommendations |

**Critical for agents**: Agents return a single message to the orchestrator. Without a structured output format, the orchestrator can't parse or route the response. Every agent should define what its return message looks like.

**Check for**: Output format template (headings, sections), edge case handling ("If [unusual input], then [specific response]"), confidence indicators, actionable next steps.

---

## Grade Scale

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 108-120 | Excellent -- production expert agent |
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

- **NEVER** give high scores because the agent "looks professional" or is well-formatted -- format wraps content, doesn't create value
- **NEVER** ignore token waste -- every redundant paragraph in the body wastes subagent context
- **NEVER** let length impress you -- a 150-line agent can outperform a 500-line agent
- **NEVER** skip mentally testing decision trees -- do they lead to correct choices?
- **NEVER** forgive explaining basics with "but it provides helpful context"
- **NEVER** assume bullet lists equal expert content -- they almost never do
- **NEVER** undervalue the description field -- poor description = invisible agent
- **NEVER** skip arithmetic verification -- confirm D1+D2+D3+D4+D5+D6+D7+D8 = Total
- **NEVER** score D5 high without checking for phrasing variety across examples
- **NEVER** ignore tool-body misalignment -- if body references capabilities the tools don't support, that's a defect

---

## Rationalizations That Inflate Agent Scores

| Rationalization | When It Appears | Why It's Wrong |
|---|---|---|
| "It's long and thorough, so it must be good" | Agent body is 400+ lines | Length often means redundancy or code-heavy bloat. Score content quality, not volume |
| "It has nice formatting and tables" | Well-structured layout | Tables can wrap redundant content. Check what's IN the tables |
| "The description is detailed" | Long description | Long doesn't mean precise. Does it have examples, varied phrasings, commentary, exclusions? |
| "It has all the tools it needs" | Tools list is extensive | Having all tools is different from having only needed tools. Check for over-permission |
| "The agent covers a lot of ground" | Broad scope | Broad scope often means shallow coverage. Does it go deep on its core purpose? |
| "It has some anti-patterns listed" | A few NEVER items | Count them. Are they named? Do they have WHY? Generic warnings don't count |
| "It's better than not having an agent" | Low-quality agent exists | A bad agent wastes tokens and may produce worse output than no agent. Sometimes deletion is optimal |

---

## Evaluation Protocol

### Step 1: Knowledge Delta Scan

Read the full agent `.md` file. Mark each body section [E]xpert, [A]ctivation, or [R]edundant. Calculate E:A:R ratio. If references exist at `~/.claude/agents/references/<name>/`, read those too.

### Step 2: Structure Analysis

Check: frontmatter validity (name, description, tools, model), body line count, `<example>` block count + quality, bullet-list ratio, output format presence, anti-pattern count.

### Step 3: Score Each Dimension

For each of 8 dimensions: find specific evidence (quote relevant lines or sections), assign score with one-line justification.

### Step 4: Calculate Total & Verify Arithmetic

```
Total = D1 + D2 + D3 + D4 + D5 + D6 + D7 + D8 (Max = 120)
```

**MANDATORY verification**: Add in pairs -- (D1+D2) + (D3+D4) + (D5+D6) + (D7+D8) = Total. Arithmetic errors are the most common evaluation failure.

### Step 5: Generate Report

Include: Total/120 with grade, dimension table with individual scores and one-line notes, E:A:R ratio, failure pattern classification (A/B/C/D), top 3-5 weaknesses with specific improvement guidance.

---

## The Meta-Question

> **"Would a practitioner who builds and optimizes agents say: 'Yes, this agent changes how the subagent performs -- it doesn't just restate what Claude already does'?"**

If yes -- the agent has genuine value. If no -- it's a token-expensive wrapper around default behavior.
