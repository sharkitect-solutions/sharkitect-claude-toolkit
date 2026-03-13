---
name: agent-development
description: "Use when creating Claude Code plugin agents (.md files in agents/ directory), writing agent descriptions for reliable triggering, designing agent system prompts, choosing agent tool sets, selecting agent models (haiku/sonnet/opus), or debugging why an agent doesn't trigger or triggers incorrectly. Use when the question is about Claude Code PLUGIN agents specifically. NEVER for general AI agent architecture (use ai-agents-architect). NEVER for agent memory design (use agent-memory-systems). NEVER for agent evaluation (use agent-evaluation)."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Claude Code Plugin Agent Development

Think like someone who has built 50 plugin agents and learned that 80% of agent problems are description problems — the agent exists, the system prompt is good, but it never triggers because the description doesn't match how users actually phrase requests.

## Agent vs Command Decision

Before building, decide which you need:

```
Does the user explicitly invoke this?
│
├─ YES, with a slash command → Build a COMMAND
│  (User types /review, /test, /deploy)
│
└─ NO, Claude should decide when to use it → Build an AGENT
   │
   ├─ Should it trigger PROACTIVELY?
   │  (After code is written, after tests pass, etc.)
   │  └─ Agent with proactive examples in description
   │
   └─ Should it trigger REACTIVELY?
      (When user asks "review this", "check for bugs", etc.)
      └─ Agent with reactive examples in description
```

**Most common mistake:** Building an agent for something that should be a command. If the user will always explicitly ask for it with a known phrase, a command is simpler and more reliable.

## Description Engineering — The #1 Skill

The description determines whether your agent ever gets used. Claude sees ALL agent descriptions for every message and decides which to trigger. A perfect system prompt behind a bad description is invisible.

### The Precision-Recall Tradeoff

```
Too narrow ◄──────────────────────────────────► Too broad
"Use when user says 'review PR'"           "Use when user needs help with code"
- Misses "check my changes"                - Triggers on everything
- Misses "look over this PR"               - Conflicts with other agents
- Agent almost never fires                  - Agent fires when it shouldn't
```

**Sweet spot:** Specific trigger conditions + varied example phrasings.

### Description Anatomy That Works

```yaml
description: |
  Use this agent when [2-3 specific trigger conditions].
  [1 sentence on what it does, not how]. Examples:

  <example>
  Context: [Realistic scenario that LED to this request]
  user: "[Natural phrasing A]"
  assistant: "[Brief response showing agent use]"
  <commentary>[WHY this agent fits]</commentary>
  </example>

  <example>
  Context: [DIFFERENT scenario]
  user: "[Natural phrasing B — different words, same intent]"
  assistant: "[Response]"
  <commentary>[WHY — different reasoning than example 1]</commentary>
  </example>
```

### Example Quality Checklist

| Quality Factor | Bad | Good |
|---------------|-----|------|
| Phrasing variety | Same words in all examples | Different phrasings for same intent |
| Context specificity | "User needs help" | "User just implemented auth with JWT" |
| Commentary | "Triggers the agent" | "Auth code written, proactively check for security patterns" |
| Proactive coverage | Only reactive examples | Mix of reactive + proactive triggers |
| Negative boundaries | No exclusions | "Do NOT use for general code questions" |

### Proactive vs Reactive Triggering

**Reactive** (user asks): Easy to get right. Match user phrasing in examples.

**Proactive** (Claude decides): Hard to get right. Requires:
1. Context in examples showing WHAT just happened (not "user needs help")
2. Commentary explaining the REASONING for triggering
3. At least 2 proactive examples showing different trigger scenarios

**The proactive triggering trap:** If your proactive examples are too vague, the agent fires constantly and annoys users. Be specific about what conditions warrant proactive use.

## System Prompt Design

The body of the agent `.md` file IS the system prompt. What makes it effective:

### The Expert Pattern

Most agents need this: tell the agent what to THINK ABOUT, not just what to DO.

```markdown
You are [role] specializing in [domain].

Before starting, assess:
- What is the scope? (single file, module, entire project?)
- What matters most? (security, performance, correctness, style?)
- What context do I have? (CLAUDE.md conventions, recent changes?)

[Then provide process steps...]
```

### Common System Prompt Failures

| Failure | Symptom | Fix |
|---------|---------|-----|
| Too vague | Agent produces generic output | Add specific criteria, examples of good/bad output |
| Too rigid | Agent can't handle variations | Use principles ("prioritize security") not scripts ("check line 42") |
| No output format | Inconsistent results | Define exact section headings and content expectations |
| No scope control | Agent tries to do everything | Add "Focus on X. Do NOT attempt Y." |
| No edge cases | Agent crashes on unusual input | Add "If [unusual case], then [specific handling]" |

### Choosing a Pattern

| Agent Purpose | Pattern | Key Elements |
|--------------|---------|--------------|
| Analyze/review code | Analysis | Severity tiers, file:line references, actionable recommendations |
| Generate code/tests | Generation | Convention matching, quality standards, completeness checks |
| Validate/check rules | Validation | Pass/fail criteria, violation details, fix suggestions |
| Coordinate multi-step | Orchestration | Phase tracking, progress reporting, failure handling |

Load `references/system-prompt-design.md` for full pattern templates when implementing.

## Tool Scoping Strategy

```
What does the agent need to DO?
│
├─ Read-only analysis → ["Read", "Grep", "Glob"]
│  (Code review, security scan, documentation check)
│
├─ Code generation → ["Read", "Write", "Grep", "Glob"]
│  (Test generation, docs generation, code scaffolding)
│
├─ System interaction → ["Read", "Write", "Bash", "Grep", "Glob"]
│  (Build verification, deployment, test execution)
│
└─ Full autonomy → omit tools field (gets all tools)
   (Only for orchestration agents that need everything)
```

**Principle of least privilege:** Start with minimum tools. Add more only when the agent demonstrably needs them. An agent with Bash access that doesn't need it is a risk.

## Model Selection

| Model | Cost | Best For | Avoid For |
|-------|------|----------|-----------|
| `haiku` | Lowest | Simple classification, formatting, quick checks | Complex reasoning, nuanced analysis |
| `sonnet` | Medium | Most agents — good balance of speed and quality | When you need maximum reasoning depth |
| `opus` | Highest | Complex multi-step reasoning, architecture decisions | Simple tasks (waste of money) |
| `inherit` | Parent's | Default — matches caller's model | When you specifically need different capability |

**Default to `inherit`** unless you have a reason. Common reasons to override:
- Haiku for high-volume agents (runs on every commit, every file save)
- Opus for agents making critical decisions (security review, architecture)

## File Index

| File | Purpose | When to Load |
|------|---------|-------------|
| SKILL.md | Decision frameworks, description engineering, anti-patterns | Always (auto-loaded) |
| references/system-prompt-design.md | System prompt pattern templates (analysis, generation, validation, orchestration) | When writing a system prompt for a specific agent type |
| references/triggering-examples.md | Example block format guide and template library | When writing agent description examples |
| references/agent-creation-system-prompt.md | The exact prompt used by Claude Code for AI-assisted generation | When using AI-assisted agent creation |
| examples/agent-creation-prompt.md | Complete agent generation template | When creating agents via prompt |
| examples/complete-agent-examples.md | Full working agent examples | When you need a reference implementation |

**Do NOT load** reference files when making decisions about whether to build an agent, choosing between agent and command, or debugging triggering issues. The SKILL.md body covers those decisions.

## Rationalization Table

| Rationalization | When It Appears | Why It's Wrong |
|----------------|-----------------|----------------|
| "The description just needs to say what it does" | Writing agent description | Description must say WHEN to trigger with varied example phrasings. "What it does" doesn't help Claude decide when to use it. |
| "One example is enough" | Writing description examples | Different phrasings catch different user patterns. 2-4 examples with varied wording dramatically improve trigger reliability. |
| "Give it all tools so it can handle anything" | Choosing agent tools | More tools = more ways for the agent to do something unexpected. Least privilege prevents unintended side effects. |
| "I'll just use opus for everything" | Choosing model | Opus costs 10-15x more than haiku. Most agents work fine on inherit/sonnet. Use opus only for complex reasoning tasks. |
| "The system prompt can be short, the agent will figure it out" | Writing system prompt | Agents without output format specs produce inconsistent results. Without edge case handling, they crash on unusual input. |

## NEVER

- NEVER write a description without at least 2 example blocks with varied phrasings — a single example teaches Claude only one way to trigger; users will phrase requests differently
- NEVER build an agent when a command serves the same purpose — if the user always explicitly invokes it, a command is more reliable and simpler
- NEVER give agents tools they don't need — an agent with Bash access that only reads code is a security risk waiting to happen
- NEVER write examples with vague context ("User needs help") — vague context produces vague triggering; be specific about what scenario warrants this agent
- NEVER skip the proactive triggering examples if the agent should fire automatically — without proactive examples in the description, Claude won't know to trigger the agent after relevant work
- NEVER assume the system prompt alone makes the agent work — the description determines IF the agent loads; the system prompt determines HOW it behaves after loading

## Red Flags

- [ ] Agent description has no `<example>` blocks — triggering will be unreliable
- [ ] All examples use the same user phrasing — misses how users actually talk
- [ ] Agent has Bash/Write tools but only does read-only analysis — over-permissioned
- [ ] No proactive examples but agent should fire automatically — it won't
- [ ] System prompt says "be helpful" without specific process or output format — generic output
- [ ] Agent description overlaps significantly with another agent — triggering conflicts
- [ ] Using opus model for an agent that runs frequently on simple tasks — cost waste
