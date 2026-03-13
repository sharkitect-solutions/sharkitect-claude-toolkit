---
name: ai-agents-architect
description: "Use when deciding WHETHER to build an AI agent (vs pipeline/chain), choosing an agent architecture pattern (ReAct, Plan-Execute, routing, multi-agent), designing tool schemas for agents, or debugging agent failures (loops, hallucinated tool calls, degraded tool selection). Use when the question is about agent DESIGN, not implementation. NEVER for implementing specific agent frameworks (use agent-development, agents-crewai). NEVER for agent memory design (use agent-memory-systems). NEVER for agent evaluation (use agent-evaluation)."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# AI Agent Architecture

Think like an architect who has shipped agents to production and learned that most agent failures are architecture failures — the wrong pattern for the problem, too many tools, no escape hatches. The hardest decision is usually "should this be an agent at all?"

## The Agent Tax — Why Most Tasks Don't Need Agents

Every agent adds cost you must justify:

| Tax | What It Costs | Typical Impact |
|-----|--------------|----------------|
| Latency | Each reasoning step = 1-5s LLM call | 5-step task = 5-25s minimum |
| Token cost | Reasoning + tool descriptions + history per step | 3-10x vs single LLM call |
| Unpredictability | Non-deterministic paths through tools | Same input, different results |
| Debuggability | Multi-step traces hard to reproduce | 10x debugging time |
| Failure surface | Each step can fail, hallucinate, or loop | Compound failure rates |

```
Should this be an agent?
│
├─ Is the task STATIC (same steps every time)?
│  └─ YES → Use a deterministic pipeline. No agent needed.
│     (ETL, format conversion, template filling)
│
├─ Does it need CONDITIONAL logic but predictable branches?
│  └─ YES → Use a chain/router. Still no agent.
│     (Classify → route to handler, if/else workflows)
│
├─ Does it need to DISCOVER what to do based on results?
│  └─ YES → This is an agent use case.
│     (Research tasks, debugging, multi-step problem solving)
│
└─ Does it need to ADAPT its plan mid-execution?
   └─ YES → This is a strong agent use case.
      (Complex reasoning, open-ended exploration)
```

**The brutal truth:** 70% of "agent" projects in production are pipelines with an LLM call in the middle. They don't need ReAct loops, tool registries, or memory systems. They need a well-written prompt and a `json.loads()`.

## Architecture Pattern Selection

| Pattern | Best For | Avoid When | Typical Steps |
|---------|----------|------------|---------------|
| **ReAct** | Exploratory tasks, tool-heavy work | Deterministic sequences, >10 steps | 3-8 |
| **Plan-Execute** | Complex multi-step tasks with clear subgoals | Simple tasks, rapidly changing context | 5-20 |
| **Routing** | Classification → specialized handler | Tasks needing iteration or discovery | 1-2 |
| **Multi-Agent** | Distinct roles with different tool sets | When single agent with role-switching works | Varies |
| **OODA** | Real-time reactive systems, monitoring | Batch processing, one-shot tasks | Continuous |

### When ReAct Breaks Down

ReAct (Reason-Act-Observe) is the default pattern but has specific failure modes:

- **Long tasks (>8 steps):** Context window fills with observation history. The agent "forgets" early steps. Solution: summarize observations, don't accumulate raw output.
- **High-branching tasks:** Too many valid tool choices per step. The agent dithers or picks randomly. Solution: reduce available tools per step via dynamic tool filtering.
- **Precise multi-step sequences:** ReAct's flexibility becomes a liability when steps MUST happen in order. Solution: Plan-Execute with a fixed step list.

### When to Use Plan-Execute Over ReAct

```
Plan-Execute is better when:
- Task has >5 clear sub-steps
- Steps have dependencies (step 3 needs step 1's output)
- You want human review of the plan before execution
- Failure at step N shouldn't require restarting from step 1

ReAct is better when:
- You don't know how many steps are needed
- Each step's action depends on what you discover
- The task is exploratory (research, debugging)
- Speed matters more than predictability
```

## Tool Design — The Most Undervalued Skill

**Tool descriptions matter more than the system prompt.** The agent reads tool descriptions at every step to decide which tool to call. Bad descriptions = wrong tool selection = agent failure.

### What Makes a Good Tool Schema

```
BAD tool description:
  "search" - "Searches for things"

GOOD tool description:
  "search_knowledge_base" - "Search internal knowledge base for
   product documentation and support articles. Returns top 5 matching
   documents with relevance scores. Use for: customer questions about
   product features, troubleshooting steps, pricing info. Do NOT use
   for: general web search, competitor info, real-time data."
```

**The rules:**
1. **Name is a verb phrase** — `search_knowledge_base` not `kb` or `search`
2. **Description says WHEN to use it** — not just what it does
3. **Description says WHEN NOT to use it** — prevents mis-selection
4. **Parameters have examples** — the agent sees the schema, not your code
5. **Return format is documented** — agent must know what it gets back

### The Tool Count Problem

| Tools Available | Selection Accuracy | Impact |
|----------------|-------------------|--------|
| 1-5 | ~95% correct | Reliable |
| 6-15 | ~85% correct | Acceptable |
| 16-30 | ~65% correct | Frequent wrong tool |
| 30+ | ~40% correct | Agent is guessing |

**Solutions when you have many tools:**
- **Dynamic tool filtering:** Only show tools relevant to the current step
- **Tool categories:** Group tools, let agent pick category first, then specific tool
- **Specialized sub-agents:** Each sub-agent gets 3-5 tools for its domain

## Multi-Agent Decision Framework

```
Do you need multiple agents?
│
├─ Do different parts need DIFFERENT tool sets?
│  ├─ YES and tools would conflict → Multi-agent
│  └─ YES but tools are compatible → Single agent, more tools (if <15)
│
├─ Do different parts need DIFFERENT system prompts?
│  ├─ YES, fundamentally different personas → Multi-agent
│  └─ YES, minor tone shifts → Single agent with role-switching
│
├─ Do parts need to run in PARALLEL?
│  ├─ YES → Multi-agent (parallel execution)
│  └─ NO → Likely single agent
│
└─ Is the task DECOMPOSABLE into independent subtasks?
   ├─ YES, clean boundaries → Multi-agent with orchestrator
   └─ NO, tightly coupled → Single agent
```

### Multi-Agent Communication Patterns

| Pattern | How It Works | Failure Mode |
|---------|-------------|-------------|
| **Orchestrator** | Central agent delegates to specialists | Orchestrator becomes bottleneck; misunderstands specialist output |
| **Pipeline** | Agent A's output feeds Agent B | No feedback loop; error in A propagates silently |
| **Debate** | Multiple agents critique each other | Converges to consensus mush; tokens explode |
| **Hierarchical** | Manager agents supervise worker agents | Over-engineering; each layer adds latency + cost |

**Default to orchestrator pattern.** It's the simplest to debug, easiest to extend, and has the clearest failure modes. Only use other patterns when orchestrator demonstrably fails.

## Agent Failure Modes (What Production Teaches You)

| Failure | Symptom | Root Cause | Fix |
|---------|---------|------------|-----|
| **Infinite loop** | Agent repeats same action | No loop detection, bad stop condition | Max iterations + action deduplication |
| **Hallucinated tool call** | Agent fabricates tool output without calling it | Tool description unclear, or model confused | Verify tool was actually called in traces |
| **Tool selection drift** | Agent picks wrong tool increasingly | Context window filling with irrelevant history | Summarize history, filter tools per step |
| **Plan abandonment** | Agent ignores its own plan mid-execution | New observation contradicts plan, no replan logic | Explicit replan trigger when observations diverge |
| **Graceless failure** | Agent errors out with no useful output | No fallback, no partial result handling | Return partial results + clear error context |
| **Silent wrong answer** | Agent confidently returns incorrect result | No verification step, no self-check | Add verification tool, structured self-critique |

### The Escape Hatch Pattern

Every agent MUST have a way to gracefully give up:

```
After N failed attempts at the same sub-task:
1. Return what you HAVE accomplished (partial results)
2. Explain what you COULDN'T do and why
3. Suggest what a human should do next
4. Do NOT retry the same failing action
```

Without escape hatches, agents loop until they hit token limits, waste money, and return nothing useful.

## Rationalization Table

| Rationalization | When It Appears | Why It's Wrong |
|----------------|-----------------|----------------|
| "Let's build an agent for this" | Starting any LLM task | Most tasks are pipelines. Ask "does this need to discover what to do?" first. |
| "More tools = more capable" | Designing agent tool set | More tools = worse selection accuracy. 5-10 focused tools beat 30 unfocused ones. |
| "We need multiple agents" | Complex task decomposition | Single agent with role-switching handles most cases. Multi-agent adds communication overhead. |
| "ReAct handles everything" | Choosing architecture | ReAct breaks on long tasks, precise sequences, and high-branching decisions. Match pattern to task. |
| "The agent will figure it out" | Skipping tool description quality | Tool descriptions are the agent's primary decision input. Vague descriptions = random tool selection. |

## NEVER

- NEVER build an agent when a deterministic pipeline handles the task — agents add latency, cost, and unpredictability that must be justified by genuinely dynamic reasoning
- NEVER give an agent >15 tools without dynamic filtering — selection accuracy drops below useful threshold at ~16+ tools
- NEVER skip the escape hatch — agents without graceful failure will loop until token limits, wasting cost and returning nothing
- NEVER put "when to use this tool" only in the system prompt — the agent reads tool descriptions at every step; the system prompt fades from attention in long contexts
- NEVER assume multi-agent is better than single-agent — each agent boundary is a communication failure point; default to single agent until it demonstrably can't handle the task
- NEVER deploy an agent without loop detection — max iterations + action deduplication are non-negotiable production requirements

## Red Flags

- [ ] Building an agent for a task that follows the same steps every time — this is a pipeline
- [ ] Agent has 20+ tools with no filtering strategy — tool selection will be unreliable
- [ ] No max iteration limit on the agent loop — will run until token budget exhaustion
- [ ] Tool descriptions say what the tool does but not when to use it — agent can't make good selection decisions
- [ ] Multi-agent system where agents rarely communicate — probably should be independent pipelines
- [ ] No partial result return on failure — agent either succeeds completely or returns nothing
- [ ] Agent tested only on happy-path inputs — adversarial and edge-case inputs will reveal architecture gaps
