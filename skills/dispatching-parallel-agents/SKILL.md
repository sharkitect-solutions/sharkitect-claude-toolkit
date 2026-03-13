---
name: dispatching-parallel-agents
description: "Use when facing 2+ independent tasks that can run concurrently without shared state. Use when multiple test files fail with different root causes. Use when independent subsystems need investigation simultaneously. Use when parallel code generation, research, or analysis would save time. NEVER when tasks share state, edit the same files, or have sequential dependencies."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Dispatching Parallel Agents

Think like someone who has dispatched 100 parallel agent batches and learned that the decision to parallelize matters more than the parallelization itself. Most failures come from dispatching tasks that AREN'T truly independent — agents edit the same files, need the same context, or produce conflicting changes.

## The Independence Test (Before Dispatching)

Every parallel dispatch must pass this test:

```
For each pair of tasks, ask:
│
├─ Do they touch the SAME files?
│  └─ YES → NOT independent. Merge into one agent or sequence them.
│
├─ Does Task B need Task A's OUTPUT?
│  └─ YES → NOT independent. Must run sequentially.
│
├─ Do they need the SAME shared resource?
│  (same database, same API with rate limits, same lock)
│  └─ YES → NOT independent. Will conflict.
│
└─ Can each agent solve its task with ONLY its own context?
   └─ NO → NOT independent. Agents will miss cross-cutting issues.
```

**If any pair fails this test, don't parallelize those tasks.** You can still parallelize the independent subset.

## When to Dispatch (Beyond Test Fixing)

| Scenario | Independent? | Why |
|----------|-------------|-----|
| 3 test files failing with different root causes | Yes | Each file tests different subsystem |
| Research on 4 unrelated topics | Yes | No shared context needed |
| Generating code for 3 unrelated features | Usually yes | Unless features share interfaces |
| Fixing bug A and refactoring module B | Only if B doesn't contain A | Check for file overlap |
| Reviewing 5 independent PRs | Yes | Each PR is self-contained |
| Investigating frontend + backend + database issues | Maybe | Check if they share the same root cause |

## Agent Prompt Engineering for Parallel Dispatch

Each agent prompt must be **self-contained** — the agent can't ask you or other agents for clarification mid-run.

### The SCCO Framework

Every parallel agent prompt needs:

| Element | What It Does | Bad Example | Good Example |
|---------|-------------|-------------|-------------|
| **S**cope | What files/area to focus on | "Fix the tests" | "Fix 3 failures in agent-tool-abort.test.ts" |
| **C**ontext | Error messages, relevant code paths | "There's a bug" | Paste exact error messages and test names |
| **C**onstraints | What NOT to touch | (nothing) | "Do NOT modify production code, only test files" |
| **O**utput | What to return | "Fix it" | "Return: root cause, changes made, tests passing" |

### Scope Sizing

| Scope Size | Agent Count | Works Well? |
|------------|-------------|-------------|
| 1 test file per agent | 3-5 agents | Best — focused, fast |
| 1 subsystem per agent | 2-4 agents | Good — clear boundaries |
| 1 feature per agent | 2-3 agents | Good if features are independent |
| Half the codebase per agent | 2 agents | Risky — too broad, agents get lost |

**Diminishing returns:** Beyond 5-6 parallel agents, the integration overhead (reviewing, merging, conflict checking) outweighs the time savings. Aim for 2-5 agents per dispatch.

## What Happens When Things Go Wrong

| Problem | How You'll Know | Fix |
|---------|----------------|-----|
| **Agents edit same file** | Merge conflicts when integrating | Should have been caught by independence test. Resolve manually. |
| **One agent fails** | Returns error or incomplete results | Don't let one failure block others. Review successful agents' work, re-dispatch failed task. |
| **Agents make contradictory fixes** | Tests pass individually but fail together | Run full suite after integration. Root cause was hidden dependency — investigate together. |
| **Agent scope too broad** | Agent takes too long, returns shallow results | Re-dispatch with narrower scope. Split into 2 focused agents. |
| **Agent makes systematic error** | Same wrong pattern in all changes | Spot-check before accepting. Add constraints to prevent the pattern. |

### The Integration Protocol

After all agents return:

1. **Read each summary** — understand what changed and why
2. **Check for file overlap** — did any agents touch the same files? If yes, merge carefully
3. **Apply changes one at a time** — don't blindly merge everything
4. **Run full test suite** — individual agent fixes may conflict
5. **Spot-check agent reasoning** — agents can confidently make wrong assumptions

## Rationalization Table

| Rationalization | When It Appears | Why It's Wrong |
|----------------|-----------------|----------------|
| "Let me dispatch an agent for each test" | Seeing many test failures | Failures may share a root cause. Investigate first — fixing one may fix 10 others. |
| "I'll dispatch 8 agents to go faster" | Lots of independent work | Beyond 5-6 agents, integration overhead exceeds time savings. Batch into 3-5 focused groups. |
| "They're probably independent" | Haven't verified independence | "Probably" means you haven't checked. Run the independence test. Conflicting agents waste more time than sequential work. |
| "The agent can figure out the scope" | Writing broad agent prompts | Broad scope = shallow results. Agents work best with narrow, specific tasks and all context included. |

## NEVER

- NEVER dispatch parallel agents that will edit the same files — merge conflicts waste more time than sequential execution saves
- NEVER skip the independence test because tasks "look" independent — hidden dependencies produce conflicting changes that are harder to debug than the original problem
- NEVER dispatch more than 5-6 agents at once — integration overhead (reviewing, merging, conflict-checking) grows quadratically; batch into smaller groups
- NEVER write agent prompts without pasting the actual error messages or context — agents can't ask for clarification mid-run; missing context = wrong fixes
- NEVER accept agent results without running the full test suite — individual fixes may pass in isolation but conflict when combined
- NEVER parallelize exploratory debugging — if you don't know what's broken yet, you can't create focused agent scopes; investigate first, parallelize second

## Red Flags

- [ ] Dispatching agents for failures you haven't investigated at all — may share a root cause that one fix would solve
- [ ] Agent prompt says "fix the tests" without listing specific test names and errors — scope too vague
- [ ] Multiple agents assigned to the same module or file — will conflict
- [ ] No constraints in agent prompts — agents may refactor unrelated code
- [ ] Accepting all agent results without running full test suite — hidden conflicts
- [ ] Dispatching 7+ agents simultaneously — integration overhead exceeds benefit
