---
name: ultimate-agent-creator
description: >
  Use when creating a new Claude Code native agent (.md file in ~/.claude/agents/),
  when building an agent from scratch or from a user request, when formalizing behavior
  into a reusable agent, or when the user says "create an agent", "build an agent",
  "make an agent for", "write an agent". Use when improving, refactoring, or
  rebuilding an existing agent that fails to trigger, produces generic output, or
  has over-permissioned tools. Use when optimizing an agent's description for better
  triggering, rewriting a bullet-list body into expert content, or scoping tools to
  least-privilege. Do NOT use for: agent-judge (evaluating/scoring existing agents),
  agent-development (plugin agent structural guidance), skill-judge (scoring SKILL.md
  files), ultimate-skill-creator (creating skills, not agents).
---

# Ultimate Agent Creator

## Why This Skill Exists

Agents fail for four predictable reasons -- all addressable during creation:

1. **They don't trigger.** The description doesn't match how users phrase requests, or it overlaps with another agent's description, so the orchestrator never invokes it.
2. **They produce generic output.** The body is bullet lists or generic advice that Claude already knows, adding zero knowledge delta. The subagent behaves identically with or without the agent loaded.
3. **They're over-permissioned.** Tools include Bash and Write for a read-only review agent, creating security risks and scope creep.
4. **They don't survive the single-message constraint.** Agents return one message to the orchestrator. Without a structured output format, the response is unparseable and inconsistent.

This skill addresses all four through a 4-layer creation process that builds agents from description outward.

---

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/agent-structure-spec.md` | Planning agent structure, writing frontmatter, choosing tools, selecting model | Body content already written, in optimization phase |
| `references/agent-optimization-patterns.md` | Rewriting bullet-list body to expert content, building anti-patterns, creating decision trees, compressing bloated agents | Creating a new agent from scratch (use structure-spec first) |
| `references/agent-native-mechanics.md` | Understanding triggering mechanics, context window impact, delegation chains, collaboration patterns, single-message return constraint | Already familiar with native agent mechanics |

---

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Create an agent for X" | YES | - |
| "Build a new agent that does Y" | YES | - |
| "Rewrite this agent's body" | YES | - |
| "Fix this agent -- it never triggers" | YES | - |
| "Optimize this agent's description" | YES | - |
| "Score/evaluate this agent's quality" | NO | agent-judge |
| "Audit all my agents for quality" | NO | agent-judge |
| "Help me build a plugin agent" | PARTIAL -- structure + description yes, plugin-specific no | agent-development |
| "Create a skill (not an agent)" | NO | ultimate-skill-creator |
| "Test this agent's runtime performance" | NO | agent-evaluation |

---

## The 4-Layer Creation Process

Every agent -- new or rebuilt -- follows these 4 layers in order. Each layer addresses one of the four failure modes.

### Layer 1: Description Engineering

**Failure addressed**: Agent doesn't trigger.

The description is the ONLY thing the orchestrator reads when deciding which agent to invoke. Claude reads ALL 38+ descriptions on every message. A perfect body behind a bad description is invisible.

**Step 1: Write trigger conditions.**
Start with "Use this agent when..." followed by 2-3 specific conditions.

**Step 2: Write 3 `<example>` blocks.**
Each example must have:
- `Context:` -- a realistic scenario (not "user needs help")
- `user:` -- a natural phrasing (varied words across examples)
- `assistant:` -- how the orchestrator responds (brief)
- `<commentary>` -- WHY this agent fits (not another)

**Quality requirements for examples:**
- Different phrasings for same intent ("review code" / "check changes" / "look over this PR")
- Mix of reactive (user asks) + proactive (context warrants) scenarios
- At least 1 edge case or boundary scenario

**Step 3: Write explicit exclusions.**
"Do NOT use for: [agent-name] ([reason]), [agent-name] ([reason])."
Cross-reference agents with overlapping domains. With 38+ agents, overlap is inevitable.

**Step 4: Verify word count.**
Target: 150-300 words. Enough for precision, short enough not to bloat orchestrator context.

See `references/agent-structure-spec.md` for frontmatter format and complete examples.

### Layer 2: Expert Body Rewrite

**Failure addressed**: Agent produces generic output.

The body IS the system prompt. It determines HOW the subagent thinks and acts. Bullet lists produce bullet-list thinking. Decision trees produce expert thinking.

**Diagnose before writing:**

```
What is the current body state?
├─ No body or <50 lines → Full build from expert knowledge
├─ 50-400 lines of bullet lists → Strip bullets, replace with decision trees
├─ 400+ lines of code blocks → Strip redundant code, add expert procedures
└─ 150-350 lines with decision trees → Targeted polish only
```

**Expert content types (use 3+ of these):**

| Content Type | What It Does | When to Use |
|---|---|---|
| Decision trees | Branches logic based on conditions | Always -- replaces bullet lists |
| Named anti-patterns | NEVER do X because [non-obvious reason] | Always -- 5-8 minimum |
| Rationalization tables | "When Claude says X, it's wrong because Y" | Discipline-enforcing agents |
| Output format templates | Structured response headings + content spec | Always -- solves single-message constraint |
| Edge case handlers | "If [unusual input], then [specific response]" | Complex or multi-path agents |
| Scope boundaries | "Focus on X. Do NOT attempt Y." | Agents prone to scope creep |

**Content audit -- mark each section:**
- **[E]xpert**: Teaches Claude something new -- KEEP
- **[A]ctivation**: Changes behavior Claude might skip -- KEEP if brief
- **[R]edundant**: Claude already knows this -- DELETE

**Target**: >60% Expert, <25% Activation, <15% Redundant. Body: 150-350 lines.

**Memory injection** (add to every active agent):
```markdown
## Session Context
Before starting work, read the project's MEMORY.md for current context and patterns.
After completing work, update MEMORY.md if you made significant decisions.
```
Read-only agents: only read MEMORY.md. Active agents: read AND update.

See `references/agent-optimization-patterns.md` for detailed rewrite strategies.

### Layer 3: Dynamic References (Conditional)

**Failure addressed**: Body can't contain enough expert content without bloating.

**Only apply if ALL of these are true:**
- Agent needs >350 lines of expert content to reach B gate quality
- Agent has the Read tool in its toolset
- Agent is NOT assigned to haiku model (too lightweight for reference loading)
- Body alone cannot achieve sufficient knowledge delta

**If applying:**
1. Create `~/.claude/agents/references/<agent-name>/` directory
2. Write 2-3 focused reference files (70-150 lines each):
   - `decision-tree.md` -- complex branching logic for multi-path scenarios
   - `anti-patterns.md` -- detailed failure cases with production examples
   - `checklists.md` -- domain-specific verification procedures
3. Add load instructions to the body:
   ```markdown
   ## Deep References (load on demand)
   - For complex [X] scenarios: Read `~/.claude/agents/references/<name>/decision-tree.md`
   - For known failure patterns: Read `~/.claude/agents/references/<name>/anti-patterns.md`
   Only load when the task requires that specific depth.
   ```

**If NOT applying**: Ensure body is dense enough (150-350 lines of expert content) to stand alone.

### Layer 4: Tool & Model Scoping

**Failure addressed**: Over-permissioned tools, wrong model.

**Tool scoping decision tree:**

```
What does the agent DO?
├─ Read-only analysis (review, audit, research)
│  → Tools: Read, Glob, Grep
│  → Add WebSearch, WebFetch ONLY if body references web research
│
├─ Code generation/modification (build, fix, debug)
│  → Tools: Read, Write, Edit, Bash, Glob, Grep
│
├─ Coordination/delegation (orchestrate other agents)
│  → Tools: Read, Glob, Grep, Task
│  → Add Write ONLY if it produces artifacts
│
└─ Full autonomy (rare -- only if genuinely needs everything)
   → Omit tools field (inherits all)
   → Document WHY in body
```

**Model selection:**

| Complexity | Model | Examples |
|---|---|---|
| Simple classification, formatting | haiku | Basic categorization, template filling |
| Most analysis and generation | sonnet (or omit to inherit) | Code review, research, content creation |
| Complex multi-step reasoning | opus | Architecture decisions, multi-agent coordination |

**Body-tool alignment check (mandatory):**
Read every instruction in the body. For each action verb (search, read, write, run, delegate, fetch), verify the corresponding tool is in the tools list. Misalignment means the agent will fail at runtime.

See `references/agent-structure-spec.md` for complete tool/model reference.

---

## Critical Rules

### The Description-First Rule

Write the description BEFORE the body. If the description doesn't work, the body is irrelevant. Test the description mentally: "If a user said [X], would the orchestrator pick this agent over the 37 others?"

### The Anti-Bullet Rule

Bodies with >40% bullet lists produce generic output. Decision trees, tables, and conditional logic are mandatory. If you catch yourself writing a bullet list, convert it:

| Bullet List (BAD) | Decision Tree (GOOD) |
|---|---|
| "- Check for security issues" | "IF handling user input → validate + sanitize. IF handling auth → check token expiry + rotation. IF neither → skip security review for this component." |
| "- Follow best practices" | "WHICH best practice? → Check body section for domain-specific practices. IF not covered → flag as gap in agent body." |

### The Exclusion Rule

Every agent MUST have explicit exclusions in the description. With 38+ agents, overlap is guaranteed. An agent without exclusions will compete with siblings for the same triggers.

### The Output Format Rule

Every agent MUST define its output format in the body. Agents return a single message. Without structure, the orchestrator gets unparseable prose. Minimum format:

```markdown
## Output Format
### Summary (2-3 sentences)
### Findings/Results (structured list with severity/priority)
### Recommendations (actionable next steps)
### Confidence Level (HIGH/MEDIUM/LOW with reasoning)
```

---

## NEVER

- NEVER create an agent without 3+ `<example>` blocks -- triggering will be unreliable across phrasings
- NEVER write a body that's >40% bullet lists -- it will produce generic output indistinguishable from no agent
- NEVER give an agent tools it doesn't need -- over-permission creates security risks and scope creep
- NEVER skip exclusions in the description -- with 38+ agents, overlap WILL cause mis-routing
- NEVER omit an output format template -- agents return one message; unstructured responses are unparseable
- NEVER write examples with the same phrasing repeated -- users express the same intent differently
- NEVER put triggering information only in the body -- the orchestrator reads descriptions, not bodies, when routing
- NEVER create a thin agent (<80 lines) expecting to "fill it in later" -- thin agents score F and get forgotten

---

## Red Flags Checklist

Before declaring any agent complete, verify:

- [ ] Description has 3+ `<example>` blocks with varied phrasings
- [ ] Description has explicit exclusions ("Do NOT use for...")
- [ ] Body is 150-350 lines (not thin, not bloated)
- [ ] Body has <40% bullet lists
- [ ] Body has 5-8+ named anti-patterns with WHY
- [ ] Body has structured output format template
- [ ] Tools are minimum necessary (read-only agents don't have Write/Bash)
- [ ] Model is specified and appropriate (or omitted to inherit)
- [ ] Body-tool alignment verified (every action verb has a corresponding tool)
- [ ] No [R]edundant content (Claude already knows this)
- [ ] Memory injection present if agent makes decisions worth tracking
- [ ] Edge cases handled ("If [unusual input], then...")

## Completion Checklist

An agent is done when ALL pass:

- [ ] Description triggers on 90%+ of relevant queries (mental test: 5 phrasings)
- [ ] Description does NOT trigger on neighboring agents' tasks (exclusions verify)
- [ ] Body is 150-350 lines of >60% Expert content
- [ ] Has 5-8 named anti-patterns with WHY + consequences
- [ ] Has structured output format with headings + content spec
- [ ] Tools are least-privilege (no unnecessary permissions)
- [ ] Model matches task complexity
- [ ] Body-tool alignment verified
- [ ] All examples have `<commentary>` explaining WHY this agent
- [ ] Would pass B gate (96+/120) on agent-judge rubric
