# Agent Structure Specification

## File Format

Agents are single Markdown files at `~/.claude/agents/<agent-name>.md` with YAML frontmatter.

```yaml
---
name: agent-name
description: >
  Use this agent when [trigger condition 1], [trigger condition 2],
  or [trigger condition 3]. Specifically:

  <example>
  Context: [Realistic scenario]
  user: "[Natural phrasing A]"
  assistant: "[Brief response showing agent invocation]"
  <commentary>[WHY this agent, not another]</commentary>
  </example>

  <example>
  Context: [DIFFERENT scenario]
  user: "[Natural phrasing B -- different words, same intent]"
  assistant: "[Response]"
  <commentary>[WHY -- different reasoning than example 1]</commentary>
  </example>

  <example>
  Context: [Edge case or proactive scenario]
  user: "[Natural phrasing C]"
  assistant: "[Response]"
  <commentary>[WHY -- covers edge case or proactive trigger]</commentary>
  </example>

  Do NOT use for: [agent-name] ([reason]), [agent-name] ([reason]).
tools: Read, Glob, Grep
model: sonnet
---

[Body content -- the system prompt]
```

---

## Frontmatter Fields

| Field | Required | Format | Notes |
|---|---|---|---|
| `name` | YES | lowercase, hyphens, <=64 chars | Must match filename stem |
| `description` | YES | String or block scalar (>) | Trigger conditions + examples + exclusions |
| `tools` | YES | Comma-separated list | Minimum necessary tools |
| `model` | RECOMMENDED | haiku, sonnet, opus, or omit | Omit = inherit from parent |

### Tools Reference

| Tool | Purpose | Give To |
|---|---|---|
| Read | Read files from filesystem | Almost all agents |
| Write | Create/overwrite files | Code generation, content creation agents |
| Edit | Modify existing files (diff-based) | Code modification agents |
| Bash | Execute shell commands | Build/test/deploy agents |
| Glob | Find files by pattern | Analysis, search agents |
| Grep | Search file contents | Analysis, search agents |
| WebSearch | Search the internet | Research agents |
| WebFetch | Fetch URL content | Research, integration agents |
| Task | Delegate to other agents | Coordination agents |
| TodoWrite | Track task progress | Multi-step workflow agents |
| NotebookEdit | Edit Jupyter notebooks | Data science agents |

### Model Selection Guide

```
How complex is the agent's reasoning?
├─ Simple pattern matching, formatting, categorization
│  → haiku (cheapest, fastest)
│
├─ Most analysis, code review, content generation
│  → sonnet (balanced) or omit (inherit parent's model)
│
├─ Multi-step architectural reasoning, cross-domain synthesis
│  → opus (most capable, most expensive)
│
└─ Unsure?
   → Omit the field (inherit from parent)
   → Override later if needed
```

---

## Description Engineering

### The CSO Rule (Claude Search Optimization)

The description is the ONLY thing the orchestrator reads when routing. Rules:

1. **Start with trigger conditions**: "Use this agent when..."
2. **Include varied example phrasings**: Different words for same intent
3. **Include explicit exclusions**: "Do NOT use for: [agent] ([reason])"
4. **NEVER summarize workflow or content** -- the orchestrator treats summaries as sufficient and skips loading
5. **NEVER use "implements", "provides", "covers"** -- these are workflow summary words

### Example Quality Rubric

| Quality | Bad | Good |
|---|---|---|
| Context | "User needs help" | "User just implemented JWT auth and wants security review" |
| Phrasing | Same words 3x | "review code" / "check changes" / "look over this PR" |
| Commentary | "Triggers the agent" | "Auth code written, proactively check for OWASP patterns" |
| Scenarios | All reactive | Mix: reactive + proactive + edge case |
| Exclusions | None | "Do NOT use for general code questions (use fullstack-developer)" |

### Description Word Count Targets

| Agent Type | Target | Rationale |
|---|---|---|
| Focused single-purpose | 150-200 words | Tight trigger space, few overlaps |
| Multi-purpose with overlaps | 200-300 words | More examples needed to differentiate |
| Cluster member (e.g., n8n) | 200-250 words | Cross-references to sibling agents |

---

## Body Architecture

### Minimum Viable Body (150 lines)

```markdown
# [Agent Role Title]

[1-2 sentence expert persona statement]

## [Primary Decision Framework]
[Decision tree or table -- NOT bullet list]

## [Domain-Specific Procedures]
[Expert workflows, conditional logic]

## Anti-Patterns
### [Named Pattern 1]
**What**: [Description]
**Why it fails**: [Non-obvious consequence]
**Fix**: [Actionable correction]

[Repeat for 5-8 patterns]

## Output Format
### Summary (2-3 sentences)
### Findings (numbered, with severity)
### Recommendations (prioritized actions)
### Confidence Level (HIGH/MEDIUM/LOW with reasoning)

## Edge Cases
- If [unusual input]: [specific handling]
- If [scope boundary hit]: [escalation path]
- If [ambiguous request]: [clarification protocol]
```

### Body Line Count Targets

| Body Size | Assessment | Action |
|---|---|---|
| < 50 lines | Critically thin (Pattern B) | Full rebuild needed |
| 50-80 lines | Below minimum viable | Needs substantial content addition |
| 80-150 lines | Lean but potentially sufficient | Ensure every line is Expert content |
| 150-350 lines | Sweet spot | Ideal range for most agents |
| 350-500 lines | Getting bloated | Consider extracting to Layer 3 references |
| > 500 lines | Over-bloated (Pattern C risk) | Must compress or extract references |

---

## Dynamic References (Layer 3)

### Directory Structure

```
~/.claude/agents/references/<agent-name>/
├── decision-tree.md       # Complex branching logic (70-150 lines)
├── anti-patterns.md        # Detailed failure cases (70-150 lines)
└── checklists.md           # Domain-specific verifications (70-150 lines)
```

### Load Instructions in Body

```markdown
## Deep References (load on demand)
- For complex [X] scenarios: Read `~/.claude/agents/references/<name>/decision-tree.md`
- For known failure patterns: Read `~/.claude/agents/references/<name>/anti-patterns.md`
Only load when the task requires that specific depth.
```

### When to Use References

| Condition | Use References? |
|---|---|
| Body alone can reach B gate (96+/120) | NO -- keep it simple |
| Body would exceed 400 lines with needed content | YES -- extract detailed content |
| Agent handles 3+ distinct complex scenarios | YES -- one reference per scenario |
| Agent is haiku model | NO -- haiku struggles with reference loading |
| Agent doesn't have Read tool | NO -- can't load references without Read |

---

## De-confliction Checklist

Before finalizing any agent, verify against overlapping agents:

1. **Search descriptions**: Read descriptions of agents in the same domain
2. **Check for trigger overlap**: Would the same user query trigger both agents?
3. **Add exclusions**: "Do NOT use for: [overlapping-agent] ([what it handles])"
4. **Add to sibling agents**: Update their descriptions with reciprocal exclusions
5. **Test mentally**: "If user says X, which agent fires?" -- should have one clear answer

### Common Overlap Pairs

| Agent A | Agent B | De-confliction |
|---|---|---|
| code-reviewer | architect-reviewer | code-reviewer = line-by-line quality. architect-reviewer = structural patterns |
| debugger | code-reviewer | debugger = finding/fixing bugs. code-reviewer = reviewing for quality |
| frontend-developer | fullstack-developer | frontend = frontend-only. fullstack = spans all layers |
| project-manager | scrum-master | PM = planning/tracking. SM = team facilitation/ceremonies |
| mcp-expert | mcp-server-architect | expert = integration/config. architect = building new servers |
