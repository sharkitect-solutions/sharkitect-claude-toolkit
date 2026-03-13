---
name: autogpt-agents
description: >
  Use when the user wants to build autonomous AI agents using AutoGPT Platform,
  design visual workflow agents, or evaluate AutoGPT against other agent frameworks.
  Covers platform vs classic architecture decisions, block design, execution model
  tradeoffs, and production deployment. Do NOT use for: general agent architecture
  theory (use ai-agents-architect), LangChain agent patterns (use agents-llamaindex
  or langchain-agent), CrewAI multi-agent orchestration (use agents-crewai), or
  agent memory system design (use agent-memory-systems).
---

# AutoGPT Agent Platform

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `framework-comparison.md` | User is choosing between agent frameworks, evaluating AutoGPT vs alternatives, or asking "should I use AutoGPT or..." | User has already committed to AutoGPT and needs implementation help |
| `platform-architecture-gotchas.md` | User is deploying AutoGPT Platform, hitting infrastructure issues, or designing production agent systems | User is doing local development or prototyping |
| `block-development-patterns.md` | User is building custom blocks, extending AutoGPT functionality, or debugging block execution | User is only using built-in blocks via the visual builder |

## Scope Boundary

| Topic | This Skill | Other Skill |
|---|---|---|
| AutoGPT Platform setup and deployment | YES | - |
| AutoGPT block design and execution model | YES | - |
| AutoGPT vs other agent frameworks decision | YES | - |
| General autonomous agent architecture | Mention only | ai-agents-architect |
| LangChain agent chains and tools | NO | agents-llamaindex, langchain-agent |
| CrewAI role-based collaboration | NO | agents-crewai |
| Agent memory and context management | NO | agent-memory-systems |
| Agent evaluation and benchmarking | NO | agent-evaluation |
| MCP server integration for agents | NO | mcp-integration |
| Docker containerization general | NO | docker-expert |
| FastAPI backend patterns | NO | fastapi-pro |
| General workflow automation (n8n, Make) | NO | n8n-workflow-patterns, make-builder |

---

## Platform vs Classic Decision

AutoGPT has TWO distinct systems with different architectures, licenses, and use cases. Confusing them is the most common mistake.

| Signal | Use Platform | Use Classic (Forge) |
|---|---|---|
| Need visual drag-and-drop agent builder | YES -- React frontend with node-based editor | NO |
| Non-technical users will build agents | YES -- low-code visual builder | NO -- requires Python |
| Need persistent scheduled/webhook-triggered agents | YES -- built-in trigger system with queue-based execution | Possible but manual |
| Building custom agent logic with full code control | NO -- constrained to block system | YES -- full Python agent with Forge toolkit |
| Need to deploy to production at scale | Platform -- but read gotchas | Classic -- more deployment flexibility |
| Want to benchmark agent performance | Classic has agbenchmark with VCR cassettes | Platform has no built-in benchmark |
| License matters (commercial use) | **Polyform Shield** -- restrictive, review before commercial use | **MIT** -- permissive |

**The license trap**: Platform and Classic have DIFFERENT licenses. Platform uses Polyform Shield License 1.0.0, which restricts competitive use. Classic uses MIT. Many teams discover this after building on Platform. Check before committing.

---

## Agent Framework Selection

First-match decision -- use the FIRST row where your situation matches:

| Your Situation | Best Framework | Why NOT AutoGPT |
|---|---|---|
| Need a visual builder for non-developers | **AutoGPT Platform** | -- (AutoGPT IS the answer) |
| Building agents that call tools in a chain with full code control | **LangChain/LangGraph** | AutoGPT's block system constrains tool chaining patterns. LangChain gives direct control over agent loops |
| Multi-agent collaboration with role specialization | **CrewAI** | AutoGPT agents are solo graph executors. Multi-agent coordination requires custom orchestration on top |
| Simple hosted agent with file search, code interpreter | **OpenAI Assistants API** | Zero infrastructure. If your agent fits Assistants' constraints, don't build infrastructure |
| Microsoft ecosystem (Azure, M365, Dynamics) | **Semantic Kernel** | Native Azure integration. AutoGPT has no Microsoft-specific connectors |
| Production agent with custom logic, no visual builder needed | **LangGraph or custom** | AutoGPT Platform adds infrastructure overhead (Postgres+Redis+RabbitMQ+Supabase) for a visual builder you won't use |
| Prototyping quickly, may switch frameworks later | **LangChain** | Largest ecosystem, most examples, easiest to start and migrate away from |

---

## Execution Model

AutoGPT Platform executes agents as **directed acyclic graphs (DAGs)** through a queue-based system:

```
Trigger -> REST API -> Graph Validator -> RabbitMQ Queue -> Executor -> Node-by-Node Block Execution -> Output
```

### Execution Constraints That Bite

| Constraint | Impact | Workaround |
|---|---|---|
| **DAG only -- no cycles** | Cannot build agents that loop back to earlier steps (common in ReAct pattern) | Use nested agent blocks or external orchestration for iterative reasoning |
| **Queue-based execution** | Latency floor of 100-500ms per node even for trivial operations (RabbitMQ overhead) | Acceptable for batch/async agents. Fatal for real-time conversational agents |
| **Node isolation** | Each node executes independently. No shared memory between nodes in same execution | Pass all needed context through node connections. State bloats quickly |
| **Single-tenant executor** | Default executor processes one graph at a time per worker | Scale with `docker compose up -d --scale executor=N` but each executor needs its own resources |
| **No streaming** | Block outputs yield complete results, not token streams | Cannot build streaming chat interfaces natively. Need WebSocket workaround |

### Cost Model Reality

| Cost Component | Local Dev | Production (Small) | Production (Scale) |
|---|---|---|---|
| Infrastructure (Postgres+Redis+RabbitMQ) | $0 (Docker) | $50-150/mo (managed services) | $200-800/mo |
| Supabase (auth) | Free tier | $25/mo | $25-200/mo |
| Executor compute | Local CPU | 1-2 vCPU, 2-4GB RAM per executor | 2-4 vCPU, 4-8GB RAM x N executors |
| LLM API calls | Per-node, per-execution | Track via cost_config in blocks | At 100 executions/day with 5 LLM nodes each: 500 API calls/day. Model choice matters |

**The hidden cost**: Every LLM block in the graph is a separate API call. A 10-node agent with 3 LLM blocks running 50 times/day = 150 API calls/day = $15-45/day with GPT-4o. Graph complexity directly multiplies LLM spend.

---

## Block Design Principles

Blocks are AutoGPT's unit of functionality. Design decisions here determine agent quality.

| Principle | Rule | Common Violation |
|---|---|---|
| **Single responsibility** | One block does one thing. Combine via graph, not via block internals | "Swiss army knife" blocks that do fetching + parsing + LLM call + formatting |
| **Yield early, yield often** | Use `yield "output_name", value` for each distinct output as soon as available | Collecting all results then yielding once at the end (breaks streaming and partial execution) |
| **Schema everything** | Input and output schemas (Pydantic) must be explicit. No `dict` or `Any` types | Loose schemas that accept anything -- blocks break silently when upstream changes |
| **Credential isolation** | Never hardcode API keys. Use `credentials_required` and `get_credentials()` | Storing keys in block config or environment variables directly |
| **Idempotent execution** | Blocks may re-execute on failure. Side effects must be safe to repeat | Blocks that create resources without checking for existing ones (duplicate records, double-sends) |
| **Cost awareness** | Set `cost_config` for any block making external API calls | Users have no visibility into which blocks drive costs without explicit tracking |

---

## Anti-Patterns

| Name | What Happens | Why It Fails |
|---|---|---|
| **Monolith Graph** | 30+ node agent with complex branching doing everything in one graph | Impossible to debug, test, or modify. Single failure cascades. Split into nested agent blocks |
| **Visual-Only Thinking** | Designing agents in the visual builder without considering execution model | Drag-and-drop hides queue latency, memory constraints, and DAG limitations. Design on paper first, then implement |
| **Platform for Chat** | Using AutoGPT Platform for real-time conversational agents | Queue-based execution adds 100-500ms per node. No native streaming. Use OpenAI Assistants or LangChain for chat |
| **License Blindspot** | Building commercial product on Platform without reading Polyform Shield | Polyform Shield restricts competitive use. Discovered post-launch = rewrite or legal exposure |
| **Fork-and-Forget** | Forking AutoGPT repo to customize, then never syncing upstream | AutoGPT ships breaking changes frequently (Prisma schema migrations, block API changes). Custom forks diverge quickly and become unmaintainable |
| **Infrastructure Overkill** | Deploying full Platform stack (Postgres+Redis+RabbitMQ+Supabase) for a simple agent | If you don't need the visual builder or multi-tenant execution, use LangChain/LangGraph with 90% less infrastructure |

---

## Rationalizations (What People Say to Justify Bad Agent Decisions)

1. "AutoGPT will figure it out autonomously" -- AutoGPT executes predetermined graphs, not open-ended autonomous reasoning. The "autonomous" in the name is aspirational branding, not architecture
2. "We'll add more nodes to handle edge cases" -- Graph complexity grows quadratically. 10 nodes = manageable. 30 nodes = debugging nightmare. Refactor before expanding
3. "The visual builder means anyone can build agents" -- Visual builder requires understanding DAGs, block types, data flow, and execution model. It's low-code, not no-knowledge
4. "We'll use Classic for now and migrate to Platform later" -- Different architectures, different APIs, different execution models. There is no migration path. Pick one
5. "AutoGPT is the most popular agent framework" -- GitHub stars != production readiness. Evaluate on your specific requirements, not popularity

## Red Flags

1. Agent graph has more than 15 nodes without nested agent blocks
2. Using Platform for use case that doesn't need visual builder
3. No cost tracking on LLM blocks in production agents
4. Building on Platform without reviewing Polyform Shield license
5. Real-time chat use case with queue-based execution architecture
6. Forked repo with no upstream sync strategy
7. Executor running with default resource limits in production (OOMKilled incoming)

## NEVERs

1. NEVER deploy Platform to production without managed database -- Docker volumes lose data
2. NEVER skip Prisma migrations after pulling upstream changes -- schema drift corrupts data
3. NEVER hardcode credentials in blocks or environment files committed to git
4. NEVER assume block execution order beyond explicit graph edges -- parallel nodes execute in any order
5. NEVER use AutoGPT Platform for latency-sensitive applications (<500ms response requirement)
