---
name: agents-crewai
description: "Use when building multi-agent systems with CrewAI framework. Use when choosing between CrewAI Crews (autonomous) vs Flows (event-driven). Use when designing agent roles/goals/backstories for CrewAI. Use when debugging CrewAI crew failures (infinite loops, agents ignoring context, token cost explosion). Use when configuring CrewAI with different LLM providers (OpenAI, Anthropic, local). NEVER for general agent architecture decisions (use ai-agents-architect). NEVER for non-CrewAI frameworks like LangGraph or AutoGen."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# CrewAI Multi-Agent Orchestration

Think like someone who has built 20 crews and learned that the biggest failures aren't code bugs — they're crew DESIGN bugs. Wrong agent count, vague roles, wrong process type. The code compiles fine, the crew runs, but the output is mediocre because the architecture is wrong.

## When CrewAI Is (and Isn't) the Right Choice

```
Do you need multiple LLM-powered agents collaborating?
│
├─ NO → Don't use CrewAI
│  ├─ Single agent task → Use direct LLM calls or a simple agent loop
│  └─ Pipeline (no agent autonomy) → Use a script or workflow tool
│
└─ YES → Is the collaboration pattern simple or complex?
   │
   ├─ Simple (linear pipeline, A→B→C)
   │  └─ CrewAI Crews with Process.sequential
   │     (Simplest multi-agent setup. Start here.)
   │
   ├─ Complex (conditional routing, parallel branches, cycles)
   │  └─ CrewAI Flows (event-driven, state management)
   │     OR consider LangGraph if you need cycle-heavy graphs
   │
   └─ Conversational (agents debate/discuss until consensus)
      └─ AutoGen is better suited for conversation-style multi-agent
```

### CrewAI vs LangGraph vs AutoGen — Expert Take

| Factor | CrewAI Wins | LangGraph Wins | AutoGen Wins |
|--------|------------|----------------|-------------|
| Setup speed | Simple role-based agents, runs in 10 min | Requires graph thinking, longer setup | Easy chat setup, but patterns are limited |
| Process control | Sequential/hierarchical built-in | Full graph control with cycles | Conversation-based, less structured |
| Production readiness | Good — memory, caching, enterprise | Good — checkpointing, streaming | Improving, but less mature |
| Debugging | Moderate — verbose mode helps | Better — step-through graph nodes | Hard — conversation traces are long |
| When to pick | Most multi-agent tasks (default choice) | Complex stateful workflows with branches | Multi-agent debate/discussion |

**Default to CrewAI** for multi-agent orchestration unless you need LangGraph's graph cycles or AutoGen's conversational patterns.

## Crew Design — Where Most Teams Fail

### The "Too Many Cooks" Problem

Every additional agent adds:
- ~2000-5000 tokens for role/goal/backstory context
- Another LLM call per task cycle
- Communication overhead (context passing between agents)
- Debugging complexity (which agent went wrong?)

| Agent Count | Cost Multiplier | Quality Impact |
|-------------|----------------|----------------|
| 2 agents | ~2x single agent | Usually improves — specialization helps |
| 3-4 agents | ~3-5x | Sweet spot for most tasks |
| 5-7 agents | ~6-10x | Diminishing returns, coordination overhead |
| 8+ agents | ~12-20x | Actively hurts quality — agents duplicate work or contradict each other |

**Rule of thumb:** If you can't explain why each agent needs to be separate (different tools? different expertise? different output format?), merge them.

### Role/Goal/Backstory Quality

These three fields determine 80% of agent output quality. Bad roles produce generic output regardless of task quality.

```python
# BAD: Generic, gives agent no direction
Agent(
    role="Assistant",
    goal="Help with the task",
    backstory="You are helpful."
)

# GOOD: Specific expertise, clear direction
Agent(
    role="Financial Data Analyst",
    goal="Identify anomalies and trends in quarterly revenue data that would affect investor communications",
    backstory="You've spent 10 years at a Big 4 firm analyzing Fortune 500 financials. You know that small discrepancies in revenue recognition can signal major issues."
)
```

**The backstory test:** Does the backstory give the agent PERSPECTIVE that changes its output? "You are helpful" adds nothing. "10 years at Big 4 analyzing Fortune 500 financials" shapes how the agent interprets data, what it flags as important, and what language it uses.

### Sequential vs Hierarchical Decision

```
Process.sequential — Tasks run in defined order
│ Agent A does Task 1 → Agent B does Task 2 → Agent C does Task 3
│
│ Use when:
│ - Task order is clear and fixed
│ - Each task's output feeds the next
│ - You want predictable execution
│ - DEFAULT CHOICE for most crews
│
Process.hierarchical — Manager agent delegates dynamically
│ Manager decides → assigns tasks → reviews results
│
│ Use when:
│ - Task order depends on intermediate results
│ - Agents may need to collaborate or re-do work
│ - CAUTION: Manager adds cost + latency + another failure point
```

**Expert insight:** Most teams default to hierarchical because it sounds more capable. In practice, sequential produces better results for 80% of use cases because the execution is predictable and debuggable. Use hierarchical only when you genuinely need dynamic task assignment.

### Crews vs Flows Decision

| Need | Use Crews | Use Flows |
|------|-----------|-----------|
| Linear agent pipeline | Yes | Overkill |
| Conditional branching | Awkward | Yes — `@router` decorator |
| Parallel execution paths | Limited | Yes — event-driven |
| State management across steps | Implicit (context passing) | Explicit (`BaseModel` state) |
| Simple multi-agent task | Yes | Overkill |
| Complex orchestration with retry/fallback | Limited | Yes |

**Start with Crews.** Graduate to Flows when you need conditional routing, parallel branches, or explicit state management. See `references/flows.md` for Flow patterns.

## Production Gotchas

| Gotcha | Symptom | Fix |
|--------|---------|-----|
| Token cost explosion | Bill 10-20x expected | Reduce agent count, use `max_iter`, use haiku/cheaper models for simple agents |
| Agent infinite loop | Task never completes | Set `max_iter=10` on agents (default 15 is often too high) |
| Context not passing | Agent B ignores Agent A's output | Explicitly set `context=[task_a]` on Task B |
| ChromaDB storage growth | Disk fills up with memory data | Set `CREWAI_STORAGE_DIR`, add cleanup schedule |
| Manager agent confusion | Hierarchical crew produces bad delegations | Switch to sequential, or improve manager LLM to opus-level |
| Backstory ignored | Agent output doesn't reflect expertise | Backstory too generic — make it specific with concrete experience |
| Tool errors swallowed | Agent fabricates tool results | Check `verbose=True` output, verify tools actually execute |

## File Index

| File | Purpose | When to Load |
|------|---------|-------------|
| SKILL.md | Design decisions, anti-patterns, when to use CrewAI | Always (auto-loaded) |
| references/flows.md | Flow patterns, state management, router examples | When implementing Flows (event-driven orchestration) |
| references/tools.md | Built-in tools list, custom tool creation, MCP integration | When adding tools to agents |
| references/troubleshooting.md | Debugging guides, common errors, solutions | When crew execution fails or produces bad output |

**Do NOT load** reference files when deciding whether to use CrewAI, choosing between Crews and Flows, or designing crew architecture. The SKILL.md body covers those decisions.

## Rationalization Table

| Rationalization | When It Appears | Why It's Wrong |
|----------------|-----------------|----------------|
| "Let's add another agent for that" | Expanding crew for a subtask | Every agent adds 2000-5000 tokens + an LLM call. Can this subtask be handled by an existing agent with an additional tool? |
| "Hierarchical is more sophisticated" | Choosing process type | Hierarchical adds a manager agent (cost + latency + failure point). Sequential is better for 80% of use cases. |
| "The backstory doesn't matter much" | Writing agent config | Backstory determines agent perspective and output quality. Generic backstories = generic output. |
| "We need Flows for everything" | Choosing orchestration pattern | Flows add complexity. Start with Crews for linear pipelines. Use Flows only when you need conditional routing or parallel branches. |
| "More tools = more capable agents" | Assigning tools | Agents with too many tools pick wrong ones. 3-5 focused tools per agent. |

## NEVER

- NEVER add agents without justifying why they can't be merged — each agent adds ~2000-5000 tokens + an LLM call; unjustified agents waste money and degrade quality
- NEVER use `Process.hierarchical` as the default — the manager agent adds cost, latency, and a failure point; use sequential unless you genuinely need dynamic task assignment
- NEVER write generic backstories ("You are helpful") — the backstory shapes agent perspective; generic = generic output regardless of task quality
- NEVER skip `context=[previous_task]` when tasks depend on each other — without explicit context passing, agents can't see previous outputs
- NEVER deploy without `max_iter` limits on agents — the default 15 iterations is often too high; agents loop until token budget exhaustion
- NEVER ignore token costs in multi-agent crews — a 5-agent sequential crew costs 5-10x a single agent; budget for this

## Red Flags

- [ ] Crew has 6+ agents for a task a 2-3 agent crew could handle — "too many cooks" problem
- [ ] Using hierarchical process for a linear pipeline — sequential is simpler and more reliable
- [ ] Agent backstories are all generic one-liners — output quality will be generic
- [ ] No `max_iter` set on any agents — risk of infinite loops and token waste
- [ ] Tasks don't use `context=[]` but depend on previous task output — broken data flow
- [ ] Using expensive model (GPT-4o/Opus) for every agent in a large crew — use cheaper models for simple agents
- [ ] No `verbose=True` during development — can't debug agent reasoning without it
