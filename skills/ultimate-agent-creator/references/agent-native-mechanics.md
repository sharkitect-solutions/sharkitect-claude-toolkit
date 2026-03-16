# Agent Native Mechanics

How Claude Code native agents actually work at the system level. Understanding these mechanics prevents common design mistakes.

---

## Triggering Pipeline

### How the Orchestrator Routes to Agents

```
User message arrives
│
├─ Orchestrator reads ALL agent descriptions (38+ descriptions)
│  └─ Each description costs tokens in the orchestrator's context
│
├─ Orchestrator decides: use an agent, or handle directly?
│  ├─ If agent match found → Invoke that agent
│  │  └─ Agent receives: system prompt (body) + user message + tools
│  └─ If no match → Orchestrator handles directly
│
├─ Agent executes (multiple tool calls possible)
│  └─ Agent has NO memory of prior invocations
│
└─ Agent returns SINGLE message to orchestrator
   └─ Orchestrator uses this response to answer the user
```

### Implications for Description Design

| Mechanic | Implication | Design Rule |
|---|---|---|
| ALL descriptions read every time | Every word costs orchestrator tokens | Keep descriptions <300 words |
| Orchestrator chooses ONE agent | Overlapping descriptions cause confusion | Add exclusions to prevent mis-routing |
| Decision is binary (use or don't) | Near-miss descriptions lead to inconsistent triggering | Include varied phrasings to cover edge cases |
| Description is the ONLY input | Body content never influences routing decision | All trigger info MUST be in description |

---

## Context Window Mechanics

### Token Budget for Agents

```
Agent Context Window
├─ System prompt (agent body): 150-350 lines typical
├─ User message forwarded from orchestrator
├─ Tool call results (file reads, search results, etc.)
├─ Dynamic references (if loaded via Read tool)
└─ Agent's own reasoning and response
```

**Key constraint**: Body + tool results + references must leave room for the agent to think and respond. A 500-line body consumes ~25% of context before the agent does any work.

### Why 150-350 Lines is the Sweet Spot

| Body Size | Context Usage | Working Space | Verdict |
|---|---|---|---|
| <50 lines | ~2% | 98% available | Too thin -- agent lacks guidance |
| 150-200 lines | ~8-10% | 90% available | Good for focused agents |
| 200-350 lines | ~12-18% | 82-88% available | Good for complex agents |
| 350-500 lines | ~18-25% | 75-82% available | Pushing limits |
| >500 lines | >25% | <75% available | Leaves too little room for tool results |

### Dynamic References and Context

When an agent loads a reference file via Read tool:
- The file content enters the context window
- Good: agent has expert knowledge for the specific case
- Risk: large references can crowd out working space
- Rule: references should be 70-150 lines each, loaded selectively

---

## Single-Message Return Constraint

### The Constraint

Agents return exactly ONE message to the orchestrator. They cannot:
- Ask follow-up questions to the user
- Return partial results and continue later
- Stream incremental output
- Maintain state between invocations

### Design Implications

| Constraint | Design Response |
|---|---|
| One message only | Structured output format is mandatory -- make the message count |
| No follow-ups | Agent must handle ambiguity within the single invocation |
| No partial results | Include confidence levels so orchestrator knows if results are complete |
| No memory | Each invocation starts fresh -- read MEMORY.md for context |

### Output Format is Non-Negotiable

Without a structured output format:
- The orchestrator gets unstructured prose
- Inconsistent response structure across invocations
- Orchestrator can't reliably extract key findings
- User gets different response shapes for similar queries

Minimum viable output format:
```markdown
### Summary
### Findings/Results (with severity/priority)
### Recommendations
### Confidence Level
```

---

## Tool Execution Model

### How Agents Use Tools

```
Agent starts with: body (system prompt) + message + tools list
│
├─ Agent can make MULTIPLE tool calls during execution
│  ├─ Read files (Read, Glob, Grep)
│  ├─ Modify files (Write, Edit)
│  ├─ Execute commands (Bash)
│  ├─ Search web (WebSearch, WebFetch)
│  └─ Delegate to other agents (Task)
│
├─ Each tool call adds results to context window
│
└─ After all tool calls, agent formulates final response
```

### Tool Risk Levels

| Risk | Tools | Implication |
|---|---|---|
| Read-only (safe) | Read, Glob, Grep | Cannot modify anything. Safe for all agents |
| Write (moderate) | Write, Edit | Can create/modify files. Give to code generation agents only |
| Execute (high) | Bash | Can run any command. Give to build/test/deploy agents only |
| Network (moderate) | WebSearch, WebFetch | Can access external resources. Give to research agents only |
| Delegation (moderate) | Task | Can invoke other agents. Give to coordination agents only |

### Least Privilege Decision Tree

```
For each tool in the proposed list:
│
├─ Does the body explicitly instruct the agent to use this capability?
│  ├─ YES → Keep the tool
│  └─ NO → Remove the tool
│
├─ Would removing this tool prevent the agent from completing its core task?
│  ├─ YES → Keep the tool
│  └─ NO → Remove the tool
│
└─ Is this tool's risk level appropriate for the agent's purpose?
   ├─ Read-only agent with Bash → REMOVE Bash
   ├─ Research agent with Write → REMOVE Write
   └─ Analysis agent with Task → REMOVE Task (unless it delegates)
```

---

## Agent Collaboration Patterns

### Delegation Chain

```
Orchestrator → Agent A (coordinator)
                 ├─ Agent A uses Task tool → Agent B
                 ├─ Agent A uses Task tool → Agent C
                 └─ Agent A synthesizes results → returns to Orchestrator
```

**Design rules for delegation chains:**
- Coordinator agent needs Task tool
- Coordinated agents do NOT need Task tool (they're leaf nodes)
- Coordinator's output format must reference what it expects from delegates
- Each agent in the chain must have compatible output formats

### n8n Cluster Example

```
n8n-workflow-architect (coordinator)
├─ Delegates to: api-integration-researcher (for unknown APIs)
├─ Hands off to: n8n-workflow-builder (for implementation)
└─ n8n-workflow-builder delegates to: n8n-workflow-debugger (for errors)
```

**Cluster design rules:**
- Optimize the coordinator first (it delegates to others)
- Ensure output formats are composable across the cluster
- Cross-reference in descriptions ("works with n8n-workflow-builder for...")
- De-conflict descriptions within the cluster

### Parallel Fan-Out

```
Orchestrator → Coordination Agent
                 ├─ Task(Agent B) → runs in parallel
                 ├─ Task(Agent C) → runs in parallel
                 └─ Task(Agent D) → runs in parallel
                 Coordination Agent waits for all, synthesizes
```

### Sequential Pipeline

```
Orchestrator → Agent A (produces output)
Orchestrator → Agent B (uses Agent A's output as input)
Orchestrator → Agent C (uses Agent B's output as input)
```

---

## Memory and State

### The Stateless Problem

Each agent invocation starts with zero memory of prior invocations. This means:
- Same question asked twice gets independently generated answers
- Decisions made in previous invocations are invisible
- Project context must be re-established every time

### Memory Injection Solution

Add to agent body:
```markdown
## Session Context
Before starting work, read the project's MEMORY.md for current context and patterns.
After completing work, update MEMORY.md if you made significant decisions.
```

| Agent Type | Memory Access |
|---|---|
| Read-only (review, analysis) | Read MEMORY.md only |
| Active (coding, building, debugging) | Read AND update MEMORY.md |
| Coordination (orchestrating others) | Read MEMORY.md, delegates handle updates |

### What to Store in MEMORY.md

- Architectural decisions and their reasoning
- Known patterns and conventions in the codebase
- Previous findings that should inform future work
- User preferences discovered during interaction
- Active constraints or requirements

### What NOT to Store

- Temporary task details (specific file being reviewed)
- Generic knowledge (standard practices)
- Information already in CLAUDE.md or project docs
