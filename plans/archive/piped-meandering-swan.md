# Sharkitect Digital — Unified AI Workforce

## Context

**Vision:** Build a fully autonomous, agentic AI workforce that operates 10x more efficient than a human team. Two interfaces, one brain — the more it's used, the more it evolves, optimizes, and improves. Sharkitect Digital becomes one of the first 1-person companies operating as an enterprise generating $1M+ in annual revenue consistently.

**Two platforms, one workforce:**
- **Desktop (Claude Code):** Full 16-agent workforce with file access, code execution, deep reasoning
- **Mobile (Telegram via n8n):** Same 16 agents mirrored as n8n workflows, same memory, same chain of command

Both read from and write to the SAME Supabase shared brain. Work done on desktop is visible on mobile and vice versa. The company itself is proof of the product.

**What we're replacing:**
- Airtable memory (300-800ms) → Supabase (<50ms)
- Python polling bot (3-15s responses) → n8n webhook (instant receipt, 1-2s response)
- Single-agent Alex bot → Full hierarchical workforce on both platforms
- Keyword-based memory retrieval → Semantic search via pgvector
- Local JSON state → Shared cloud state across platforms

---

## Research Findings (Completed)

### Memory Platform: Supabase replaces Airtable

12 platforms compared. Supabase scored 40/45 — highest overall.

| Metric | Airtable (current) | Supabase (recommended) |
|--------|-------------------|----------------------|
| Read latency | 300-800ms | **Sub-50ms** |
| Write latency | 300-800ms | **Sub-20ms** |
| Rate limit | 5 req/sec | No hard limit |
| Semantic search | None | **pgvector (HNSW)** |
| Real-time sync | Polling only | **WebSocket push** |
| Multi-tenant (for product) | Separate bases | **Row Level Security** |
| n8n native node | Yes | **Yes** |
| Human editing UI | Best-in-class | Functional (3/5) |
| Free tier | 1,000 records | **500MB database** |
| Production cost | ~$20/user/mo | **$25/mo total** |

**CEO UI:** Supabase Table Editor first. If painful, Retool admin panel (half-day build). Chris interacts with memories 90% through the bot.

**Eliminated:** Pinecone/Weaviate/Qdrant (pgvector sufficient), Redis (add as cache if needed), Firebase (no semantic search), Notion (500-2000ms API), MongoDB Atlas (Supabase edges on real-time + cost), Neon/PlanetScale/Turso (PostgreSQL without extras).

### n8n Telegram Architecture: Hybrid wins

| | Pure n8n | Pure Python (current) | **Hybrid (recommended)** |
|--|---------|----------------------|------------------------|
| Message receipt | Webhook (instant) | Polling (100-500ms) | **Webhook (instant)** |
| Response time | 1.5-2.5s | 3-15s | **1.2-1.8s** |
| Tool flexibility | Limited | Full | **Full** |
| n8n visual editor | Yes | No | **Yes (all routing)** |

**Hard constraint:** n8n AI Agent node: Extended Thinking + Tool Use are INCOMPATIBLE.

---

## Video Research Synthesis (9 Nate Herk Videos)

### Universal Patterns (confirmed across 4+ videos)

1. **Agent-as-a-Tool via "Call n8n Workflow"** — Sub-agents are separate workflows called via tool nodes. Orchestrator never executes domain work.
2. **Execute Workflow Trigger** — Required entry point for all sub-agent workflows. Set to "accept all data."
3. **Tool descriptions ARE routing logic** — AI reads tool descriptions and infers when to use each sub-agent. No complex routing code needed.
4. **Orchestrator = Router Only** — "You are an orchestrator. Your ONLY job is to delegate." Validates Marcus's NN#1 design.
5. **One workflow does one thing** — Modular, testable, independently deployable. Each workflow has a single responsibility.

### Key Techniques to Adopt

| Technique | Source | Application |
|-----------|--------|-------------|
| Layered Prompting | Video 9 | High-level routing in Marcus ONLY. Detailed domain instructions in each sub-agent. Saves 40-60% tokens at orchestrator level. |
| Think Tool | Video 9 | Reusable reasoning sub-workflow. Forces agent to plan before delegating. For Alex, Marcus, and all C-Suite. |
| `$fromAI()` Dynamic Parameters | Video 7 | `{{ $fromAI("paramName", "description") }}` — AI fills values at runtime. |
| Discrete Variable Passing | Video 9 | Sub-workflows receive specific variables, NOT full conversation context. Keeps sub-agents stateless and fast. |
| Fire-and-Forget | Video 6 | For long-running ops, sub-workflow runs independently and sends result directly to Telegram. Prevents timeout. |
| Comprehensive Logging | Video 9 | Every operation: timestamp, workflow, input, output, token counts, model, errors. Both success AND error paths. |
| Multi-Vendor Model Strategy | Video 7 | Cheap model for routing/classification, capable model for generation. |
| Sub-Agent Error Handling | Videos 3, 9 | "Continue using error output" on Call n8n Workflow nodes. Dual-branch: success + error both feed to logging. |
| Contact Lookup Before Action | Videos 3, 7 | System prompt directive: always resolve identity before sending/sharing. |
| Persistent Asset Database | Video 6 | Track created assets for reuse before generating new ones. |

### Things to Avoid

1. **Passing full conversation history to sub-agents** — Bloats tokens, causes confusion. Pass discrete variables only.
2. **Domain instructions in orchestrator prompt** — Marcus gets high-level routing ONLY. Domain expertise stays in sub-agents.
3. **Agent Factory for production** (Video 8) — Good for scaffolding initial workflows, but workflow JSON is brittle. Use for initial generation, then refine manually.
4. **Window Buffer Memory for multi-agent** — Fine for single-agent. For multi-agent workforce, use Supabase sessions table (cross-platform, persistent, queryable).
5. **Skipping logging** — Every video that showed production systems had comprehensive logging. Non-negotiable for the backbone of a company.

---

## Architecture

### System Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    SUPABASE (Shared Brain)                     │
│                                                                │
│  memories    — per-agent partitioned (agent_id), pgvector      │
│  sessions    — conversation state per platform + agent         │
│  kb_docs     — knowledge base documents with embeddings        │
│  logs        — comprehensive operation logging                 │
│                                                                │
│  Row Level Security (future multi-tenant via tenant_id)        │
│  Real-time WebSocket subscriptions                             │
│  Sub-50ms reads, sub-20ms writes                               │
└───────────┬──────────────────────────┬────────────────────────┘
            │                          │
     ┌──────┴──────┐          ┌────────┴────────┐
     │   DESKTOP   │          │     MOBILE      │
     │ Claude Code │          │   Telegram/n8n  │
     │             │          │                 │
     │ 16 agents   │          │ 16 n8n workflows│
     │ (prompts +  │          │ (mirrored       │
     │  tools)     │          │  hierarchy)     │
     │             │          │                 │
     │ supabase-py │          │ Supabase nodes  │
     │ File access │          │ Webhook trigger │
     │ Code exec   │          │ Think Tool      │
     │ Deep reason │          │ Fast-paths      │
     └─────────────┘          └─────────────────┘
```

### Agent Hierarchy (n8n mirror of Claude Code workforce)

```
TELEGRAM WEBHOOK (instant)
  ↓
ALEX (n8n workflow — AI Agent + Think Tool)
  ├── Own tools: check_email, check_calendar, check_hubspot, check_drive
  ├── Handle directly: scheduling, routine comms, admin, info retrieval
  └── Escalate → MARCUS (Call n8n Workflow)

MARCUS (n8n workflow — AI Agent + Think Tool)
  ├── Orchestrator ONLY — routes, never executes domain work
  ├── System prompt: "Your ONLY job is to delegate to the correct agent"
  ├── Layered prompting: high-level routing descriptions only
  └── Routes to C-Suite (each a "Call n8n Workflow" tool):
      ├── ATLAS (COO) — operations, delivery
      ├── STERLING (CFO) — finance, financial governance
      ├── VERA (Brand) — brand identity, communications standards
      ├── CLEO (CMO) — marketing, growth
      ├── ORION (CTO) — technology, systems, builds
      ├── FELIX (Revenue) — revenue, sales, clients
      ├── SAGE (Knowledge) — knowledge management, documentation
      ├── AXIOM (Strategy) — strategic inflection points [advisor]
      └── LEX (Legal) — contracts, compliance, IP [advisor]

(Phase 2) Worker agents — connected to supervisors:
  ├── NODE, VANTAGE, ECHO, QUILL → ORION (Call n8n Workflow tools)
  └── SCOUT → CLEO (Call n8n Workflow tool)
```

### Think Tool (Reusable Reasoning Sub-Workflow)

Separate n8n workflow (built once, called by all agents that need it):
- **Input:** Current task/message + available tools list
- **Process:** Forces the agent to reason step-by-step before acting
- **Output:** Structured reasoning (which tool(s) to call, why, in what order)
- **Deployed to:** Alex (handle-vs-escalate), Marcus (multi-lane routing), ALL C-Suite (worker delegation as teams grow)

```
Execute Workflow Trigger
  → AI Agent (fast model — Haiku or Sonnet)
     System prompt: "Analyze this task. Which tool(s) should be called? In what order? Why?"
  → Return structured reasoning to caller
```

**Worth the ~200ms:** A wrong routing decision wastes FAR more time downstream than 200ms of upfront reasoning. Quality and accuracy over raw speed.

### Supabase Schema

```sql
-- Core memory table (per-agent partitioned)
CREATE TABLE memories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000001',
    agent_id TEXT NOT NULL DEFAULT 'shared',  -- 'alex', 'marcus', 'orion', 'shared', etc.
    key TEXT NOT NULL,
    category TEXT NOT NULL,           -- fact, preference, rule, decision, client, contact, workflow
    content TEXT NOT NULL,
    source TEXT DEFAULT 'conversation',
    confidence TEXT DEFAULT 'inferred',
    use_count INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true,
    embedding VECTOR(1536),           -- OpenAI text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    last_accessed TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(tenant_id, agent_id, key)
);

CREATE INDEX ON memories USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON memories (tenant_id, agent_id, category, active);
CREATE INDEX ON memories (tenant_id, agent_id, updated_at DESC);

-- Session state (per-platform, per-agent conversation context)
CREATE TABLE sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL,
    agent_id TEXT NOT NULL DEFAULT 'alex',
    platform TEXT NOT NULL,            -- 'desktop' or 'telegram'
    messages JSONB DEFAULT '[]',
    summary TEXT,
    pending_tasks JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Knowledge base documents
CREATE TABLE kb_docs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL,
    title TEXT NOT NULL,
    category TEXT,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Comprehensive operation logging (backbone reliability)
CREATE TABLE logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000001',
    timestamp TIMESTAMPTZ DEFAULT now(),
    agent_id TEXT NOT NULL,            -- which agent ran this
    workflow_name TEXT,                 -- n8n workflow name
    workflow_id TEXT,                   -- n8n workflow ID
    platform TEXT NOT NULL,            -- 'desktop' or 'telegram'
    user_input TEXT,                    -- what triggered this
    agent_response TEXT,               -- what was returned
    tool_calls JSONB DEFAULT '[]',     -- tools invoked [{name, input, output}]
    tokens_prompt INTEGER DEFAULT 0,
    tokens_completion INTEGER DEFAULT 0,
    tokens_total INTEGER DEFAULT 0,
    model TEXT,                        -- claude-sonnet-4-6, claude-haiku-4-5, etc.
    duration_ms INTEGER,               -- total execution time
    success BOOLEAN DEFAULT true,
    error TEXT,                        -- error message if failed
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX ON logs (tenant_id, agent_id, timestamp DESC);
CREATE INDEX ON logs (tenant_id, success, timestamp DESC);
```

### Semantic Search (per-agent aware)

```sql
CREATE FUNCTION search_memories(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    p_tenant_id UUID DEFAULT '00000000-0000-0000-0000-000000000001',
    p_agent_id TEXT DEFAULT NULL  -- NULL = search all agents, specific = agent + shared
)
RETURNS TABLE (
    id UUID, key TEXT, category TEXT, content TEXT,
    confidence TEXT, use_count INT, similarity FLOAT, agent_id TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT m.id, m.key, m.category, m.content,
           m.confidence, m.use_count,
           1 - (m.embedding <=> query_embedding) AS similarity,
           m.agent_id
    FROM memories m
    WHERE m.tenant_id = p_tenant_id
      AND m.active = true
      AND (p_agent_id IS NULL
           OR m.agent_id = p_agent_id
           OR m.agent_id = 'shared')
      AND 1 - (m.embedding <=> query_embedding) > match_threshold
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

**Embedding pipeline:** OpenAI `text-embedding-3-small` before insert/query. ~$0.002 per 1,000 memories. Background async for writes.

---

## Implementation Plan — 4 Phases

### Phase 0: Supabase Foundation
**Everything depends on this. Must complete first.**

#### 0a. Set up Supabase project
- Create project on supabase.com
- Enable pgvector extension
- Create tables: `memories`, `sessions`, `kb_docs`, `logs`
- Create `search_memories` RPC function
- Set up Row Level Security policies (tenant_id-based)
- Generate API keys (anon key for n8n, service role key for Python)

#### 0b. Build Python memory client
**New file:** `tools/alex-telegram-bot/supabase_memory.py`

```python
class SupabaseMemory:
    """Unified memory client — reads/writes to Supabase shared brain.

    Replaces: ConversationMemory (local JSON) + MemorySync (Airtable)
    Adds: semantic search, per-agent partitioning, cross-platform sessions
    """

    def __init__(self, supabase_url, supabase_key, tenant_id=None, agent_id='shared'):
        self.client = create_client(supabase_url, supabase_key)
        self.tenant_id = tenant_id or DEFAULT_TENANT
        self.agent_id = agent_id

    # Memory CRUD (writes to this agent's partition)
    def store_memory(self, key, category, content, source) -> dict
    def get_memory(self, key) -> dict | None
    def deactivate_memory(self, key) -> bool

    # Semantic search (searches this agent's memories + shared)
    def get_relevant_memories(self, message: str, limit: int = 10) -> list[dict]

    # Session management
    def save_session(self, platform: str, messages: list, summary: str = "")
    def load_session(self, platform: str) -> dict

    # Conversation history
    def add_message(self, role: str, content: str)
    def get_messages_for_api(self) -> list[dict]

    # Logging
    def log_operation(self, **kwargs) -> None

    # Embedding helper
    def _embed(self, text: str) -> list[float]
```

#### 0c. Migrate Airtable data to Supabase
- Read all memories from Airtable via existing `memory_sync.py`
- Generate embeddings for each entry
- Insert into Supabase `memories` table (agent_id='shared' for existing data)
- Verify counts match
- Keep Airtable read-only for 1 week, then retire

#### 0d. Update Claude Code integration
- Update `brain.py` and `bot.py` to use `SupabaseMemory`
- Replace keyword matching with semantic search
- Replace local JSON with Supabase session reads/writes
- Add Supabase + OpenAI credentials to `.env`

**Files:**
| File | Change |
|------|--------|
| **NEW** `supabase_memory.py` | Unified memory client |
| `brain.py` | Import SupabaseMemory, semantic search for context |
| `bot.py` | Replace ConversationMemory with SupabaseMemory |
| `config.py` | Add supabase_url, supabase_key, openai_api_key |
| `.env` | Add SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY, OPENAI_API_KEY |

**Retired:** `memory.py` (kept as fallback), `memory_sync.py`, `data/memory.json`

---

### Phase 1: Core Workforce (Alex + Marcus + 9 C-Suite)
**11 agents in n8n. The command chain comes alive.**

#### Build Order

Build sequentially — each agent depends on the one before it in the chain:

1. **Think Tool** (reusable sub-workflow) — built once, used by all agents
2. **Shared utility workflows** — email check, calendar check, HubSpot lookup, Drive search
3. **Alex** (Telegram entry point) — webhook + AI Agent + Think Tool + utility tools + escalate_to_marcus
4. **Marcus** (orchestrator) — AI Agent + Think Tool + 9 C-Suite routing tools
5. **C-Suite agents** (9 workflows, can be scaffolded in parallel via Agent Factory):
   - Atlas, Sterling, Vera, Cleo, Orion, Felix, Sage, Axiom, Lex

#### 1a. Think Tool Sub-Workflow

```
[Execute Workflow Trigger] → [AI Agent (Haiku)]
   System prompt: "Analyze the task. List available tools. Determine which
   tool(s) to call, in what order, and why. Return structured reasoning."
   → [Return to caller]
```

Deployed to: Alex, Marcus, all 9 C-Suite. ~200ms per invocation. Worth it — wrong routing costs far more downstream.

#### 1b. Alex's n8n Workflow

Alex is the Telegram entry point AND has his own operational tools. Not just a passthrough.

```
[Telegram Trigger (webhook)] → [Code: debounce 0.5s]
  → [Code: fast-path regex check]
     ├── [match] → Direct tool call → [AI Agent: synthesize result] → [Telegram Send]
     └── [no match] → [AI Agent (Sonnet) + Think Tool + sub-tools]
                        → [Telegram Send (progressive edit)]
  → [Supabase: log operation]
```

**Alex's sub-tools (each a separate "one thing" workflow):**
| Tool Workflow | Purpose | Called via |
|--------------|---------|-----------|
| `check_email` | Gmail triage via gws CLI or direct API | Call n8n Workflow |
| `check_calendar` | Calendar agenda/conflicts | Call n8n Workflow |
| `check_hubspot` | Contact/deal/company lookup | Call n8n Workflow |
| `check_drive` | File search and retrieval | Call n8n Workflow |
| `escalate_to_marcus` | Route to full workforce | Call n8n Workflow |

**Alex's system prompt (layered — high-level only):**
- Identity: Elite Executive Assistant to Chris
- Authority: scheduling, routine comms, basic research, admin support, info retrieval
- Decision rule: If task is within authority → use own tools. If not → escalate to Marcus. Think Tool helps decide.
- NO domain knowledge in Alex's prompt — that lives in sub-agents

**Fast-paths (skip AI entirely, LOOSE matching):**
- "check email" / "inbox" / "any mail?" → direct `check_email` workflow
- "calendar" / "schedule" / "today" → direct `check_calendar` workflow
- "look up [name]" → direct `check_hubspot` workflow

**Message debounce:** 0.5s Code node. Chris sends 3 messages quickly → batched into one request.

**Progressive response:** Send "..." immediately → edit message every 500ms with accumulated text → show tool progress ("Checking inbox...").

#### 1c. Marcus's n8n Workflow

Orchestrator only. Routes to C-Suite, never executes domain work.

```
[Execute Workflow Trigger] → [AI Agent (Sonnet) + Think Tool + 9 C-Suite tools]
  → [Return result to Alex]
```

**Marcus's system prompt (layered — routing descriptions only):**
```
You are Marcus, Chief of Staff. Your ONLY job is to:
1. Analyze the incoming task
2. Identify which department(s) own this work
3. Route to the correct C-Suite agent(s)
4. If task spans multiple departments, route to ALL relevant agents
5. Synthesize results and return to Alex

You NEVER execute domain work yourself. You route, coordinate, and synthesize.
```

**Marcus's C-Suite tools (descriptions drive routing):**
| Tool | Description (what AI reads to decide routing) |
|------|----------------------------------------------|
| `route_to_atlas` | "Operations and delivery. Project management, SOP execution, workflow optimization." |
| `route_to_sterling` | "Finance and financial governance. Budget, pricing, invoicing, financial analysis." |
| `route_to_vera` | "Brand identity and communications standards. Tone, voice, brand compliance." |
| `route_to_cleo` | "Marketing and growth. Campaigns, content strategy, lead generation, CRO." |
| `route_to_orion` | "Technology, systems, and builds. n8n workflows, integrations, technical architecture." |
| `route_to_felix` | "Revenue, sales, and clients. Proposals, client relationships, deal management." |
| `route_to_sage` | "Knowledge management and documentation. KB integrity, cross-references, learning synthesis." |
| `route_to_axiom` | "Strategic inflection points. Org design, market positioning, enterprise alignment. Engage for strategic decisions only." |
| `route_to_lex` | "Contracts, compliance, IP, legal risk. Engage for legal matters only." |

**Multi-lane routing:** Think Tool helps Marcus identify ALL agents that a task touches. Per MULTI-LANE AUTO-ROUTING rule — Marcus convenes the team, solves, presents solution. Chris should never have to tell us which agents to pull in.

#### 1d. C-Suite Agent Workflows (9 agents)

Each follows the same pattern:

```
[Execute Workflow Trigger] → [AI Agent (Sonnet) + Think Tool + domain-specific tools]
  → [Supabase: read/write agent memory (agent_id = agent name)]
  → [Return result to Marcus]
```

**Per-agent specifics:**

| Agent | agent_id | Key Domain Tools | Memory Focus |
|-------|----------|-------------------|-------------|
| Atlas | `atlas` | Project tracker, SOP executor | Operational decisions, delivery status |
| Sterling | `sterling` | Financial calculator, invoice tools | Pricing decisions, budget tracking |
| Vera | `vera` | Brand guide checker, tone analyzer | Brand rules, voice preferences |
| Cleo | `cleo` | Campaign tools, analytics, CRO | Marketing insights, campaign performance |
| Orion | `orion` | n8n API, system monitor, build tools | Technical decisions, architecture patterns |
| Felix | `felix` | HubSpot CRM, proposal generator | Client relationships, deal status |
| Sage | `sage` | KB scanner, cross-ref validator | Documentation patterns, learning history |
| Axiom | `axiom` | Strategy frameworks, analysis tools | Strategic decisions, market insights |
| Lex | `lex` | Contract templates, compliance checker | Legal decisions, compliance status |

**System prompts loaded from agent knowledge base:** Each agent's ROLE.md + KNOWLEDGE.md content becomes the system prompt. Detailed domain instructions stay HERE, not in Marcus's prompt (layered prompting pattern).

**Agent Factory approach:** Use meta-agent (Claude Opus + Extended Thinking) to generate initial workflow JSON for each C-Suite agent. Then review and refine each one in Claude Code with Orion's team. Factory for scaffolding speed — manual refinement for production quality.

---

### Phase 2: Worker Agents
**5 workers connected to their C-Suite supervisors.**

| Worker | Supervisor | Role | Connected via |
|--------|-----------|------|---------------|
| Node | Orion | n8n workflow builder, integration specialist | Call n8n Workflow tool in Orion |
| Vantage | Orion | Architecture, blueprints, system design | Call n8n Workflow tool in Orion |
| Echo | Orion | Testing, QA, validation | Call n8n Workflow tool in Orion |
| Quill | Orion | Content generation, prompt engineering | Call n8n Workflow tool in Orion |
| Scout | Cleo | Lead research, outreach, prospecting | Call n8n Workflow tool in Cleo |

Each worker follows the same pattern as C-Suite agents:
```
[Execute Workflow Trigger] → [AI Agent (Sonnet) + domain tools]
  → [Supabase: read/write agent memory (agent_id = worker name)]
  → [Return result to supervisor]
```

**C-Suite supervisors updated:** Orion and Cleo get Think Tool + worker routing tools added to their workflows. Same pattern as Marcus routing to C-Suite.

**Performance optimizations (bundled with Phase 2):**
- Streaming responses in Alex's workflow (progressive Telegram message editing)
- Conversation history window: 20 → 12 messages (saves ~2,400 tokens/call)
- Parallel tool execution when Claude returns multiple tool_use blocks
- Direct Google API calls (replace gws subprocess for Gmail/Calendar — 100-400ms vs 500ms-2s)

---

### Phase 3: Autonomous Evolution
**The system optimizes itself. Ongoing, never "done."**

#### 3a. Autonomous Audit System (weekly)

New n8n workflow that runs every Sunday (aligned with existing weekly rhythm):

```
[Schedule Trigger (weekly)] → [AI Agent (Sonnet)]
  → Read all agent logs from past week (Supabase logs table)
  → Analyze: routing accuracy, response times, error rates, tool usage patterns
  → Identify: weaknesses, strengths, gaps, optimization opportunities
  → Generate: audit report with specific recommendations
  → Write: report to Supabase + Slack notification to #alex-escalations
  → If critical gap found: create Pending Task for Marcus
```

**Audit dimensions:**
- **Routing accuracy**: Did Marcus send tasks to the right agents?
- **Response quality**: Did agents handle tasks within their authority?
- **Performance**: Average response times per agent, token usage trends
- **Error patterns**: Recurring failures, common error types
- **Gap detection**: Tasks that fell through cracks, agents that couldn't complete work
- **Evolution metrics**: Week-over-week improvement trends

#### 3b. Gap-Filling Worker Agents

When the audit identifies a gap (e.g., "Orion's team needs a deployment specialist"):
1. Audit report flags the gap with evidence
2. Marcus reviews and approves new worker agent creation
3. Agent Factory scaffolds the workflow
4. Orion's team in Claude Code refines it
5. New worker integrated into supervisor's tool list
6. Next audit verifies the gap is closed

#### 3c. Escalation Auto-Fix (3-layer system)

```
Layer 1: Slack → #alex-escalations (immediate, ~1s)
Layer 2: n8n webhook → triggers Claude Code session (~2s)
Layer 3: Marcus → Agent → Fix → Post resolution (autonomous)
```

Chris's directive: "It should automatically cause the team to fix it."

#### 3d. Learning Synthesis

Monthly (aligned with existing learning synthesis cadence):
- Sage reads all 16 agent MEMORY.md files + Supabase agent memories
- Identifies cross-agent patterns and learnings
- Distributes relevant insights to affected agents
- Updates shared knowledge base

---

## Verification Plan

**Phase 0 (Supabase Foundation):**
1. Memory count in Supabase matches Airtable
2. `search_memories("pricing")` returns pricing-related memories (semantic, not keyword)
3. Both desktop and Telegram can read/write the same memories
4. Per-agent partitioning works: Alex's memories don't leak into Orion's queries
5. Logs table captures operations correctly

**Phase 1 (Core Workforce — 11 agents):**
1. Telegram message → webhook fires instantly (no polling delay)
2. "Check my email" → fast-path triggers, response in 1-2s
3. "Create a proposal for [client]" → Alex escalates → Marcus routes to Felix → Felix responds
4. Multi-lane task → Marcus routes to multiple agents, synthesizes
5. Think Tool reasoning is visible in logs
6. Each agent reads/writes to its own memory partition
7. Desktop and Telegram both see same memory state

**Phase 2 (Workers):**
1. "Build an n8n workflow for X" → Alex → Marcus → Orion → Node
2. Worker agents appear in supervisor's tool list
3. Orion and Cleo Think Tool routes to correct workers

**Phase 3 (Evolution):**
1. Weekly audit runs automatically, generates report
2. Report identifies real issues (not false positives)
3. Gap recommendations are actionable
4. Auto-fix escalation triggers within 2s of failure

---

## Decisions — LOCKED (Chris-approved)

1. **Supabase replaces Airtable** as the shared brain
2. **Per-agent memory partitioning** — each agent gets own `agent_id` in Supabase, all share same database
3. **Full workforce on BOTH platforms** — 16 agents mirrored in n8n, same chain of command as Claude Code
4. **Hierarchical routing** — Alex → Marcus → C-Suite → Workers (via "Call n8n Workflow" chains)
5. **Phase 1 = Alex + Marcus + 9 C-Suite** (11 agents). Phase 2 = 5 Workers. Phase 3 = Autonomous evolution.
6. **Think Tool for Alex + Marcus + ALL C-Suite** — quality/accuracy over raw latency
7. **Agent Factory for scaffolding** — generate initial workflows, refine in Claude Code
8. **Voice deferred** to Pending Item #7 — operational reliability first
9. **Comprehensive Supabase logging** — timestamp, agent, workflow, input, output, tokens, model, errors
10. **One workflow does one thing** — modular, testable, independently deployable
11. **Layered prompting** — high-level routing in Marcus, detailed domain in sub-agents
12. **Debounce window**: 0.5 seconds
13. **Fast-path confidence**: LOOSE — catch as many natural variations as possible
14. **Escalation**: `#alex-escalations` + 3-layer auto-fix
15. **Alex has own sub-tools** — not just a passthrough, handles scheduling/comms/admin with own workflows

## Decision — CEO Memory UI

**Supabase Table Editor first.** Clean break from Airtable. If painful → Retool admin panel (half-day build).

---

## Cost Projection

| Component | Monthly Cost |
|-----------|-------------|
| Supabase Free (MVP) | $0 |
| Supabase Pro (production) | $25 |
| OpenAI embeddings (10K memories/mo) | ~$0.02 |
| Claude API — increased usage (16 agents) | ~$50-100 (estimate) |
| n8n Cloud (already have) | included |
| **Total additional** | **$75-125/mo** |

vs. current: $20/mo Airtable + $20/mo API = $40/mo for a single-agent bot that takes 3-15s.

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| 16-agent token costs escalate | Medium | Layered prompting (40-60% savings), Haiku for Think Tool, fast-paths skip AI |
| Agent Factory produces broken workflows | Low | Factory for scaffolding only, manual refinement required |
| n8n workflow complexity at 20+ workflows | Medium | One workflow does one thing, comprehensive logging, weekly audit |
| Think Tool adds latency to every request | Low | ~200ms per invocation, prevents wrong routing (far costlier) |
| Supabase Table Editor too technical for Chris | Medium | Retool admin panel (half-day build) |
| Migration data loss | Low | Run Airtable + Supabase in parallel for 1 week |
| Embedding API adds latency to writes | Low | Async: write memory first, embed in background |
| Telegram edit rate limit (30/min) | Low | 500ms throttle between progressive edits |
| Agent routing loops (A calls B calls A) | Medium | Strict hierarchy enforcement, no upward delegation, logging detects loops |

---

## Execution Protocol — Batches & Context Control

### Rules
1. **Each Phase = New Chat Session.** Phase 0 in one chat, Phase 1 in another, etc. Keeps context window controlled.
2. **Each Phase is broken into Batches.** Batches are small enough to complete within one context window without compression issues.
3. **Memory Checkpoint after every Batch.** Before compressing or moving to the next batch, update ALL of the following:
   - Project `MEMORY.md` (session progress, decisions, status)
   - `memory/session-history.md` (detailed session log)
   - Plan file (mark completed batches, note any deviations)
   - Affected agent `MEMORY.md` files in `agents/<name>/`
   - Any KB files that were created or modified
4. **Compress between Batches.** After checkpoint, `/compact` to free context. Next batch picks up from memory.
5. **Crash Recovery.** If a session crashes or context is lost, memory files contain exactly where we are. Every batch's checkpoint is the recovery point.

---

### Phase 0 Batches: Supabase Foundation
**Chat Session 1**

| Batch | Work | Checkpoint |
|-------|------|------------|
| **0-A** | ~~Create Supabase project, enable pgvector, create all 4 tables + indexes + RPC function + RLS policies~~ | **COMPLETE 2026-03-15.** Project ref: dgnjfamhwfyogmgcpedb. 4 tables + 7 indexes + RPC + 16 RLS + 3 triggers. All verified via REST API. Schema at `.tmp/supabase-schema.sql`. Credentials in `.env`. MCP in `.mcp.json`. |
| **0-B** | ~~Build `supabase_memory.py` — full SupabaseMemory class with all methods~~ | **COMPLETE 2026-03-15.** 17 public methods, REST API via httpx, OpenAI embeddings, 21 tests passed. |
| **0-C** | ~~Migrate Airtable data → Supabase. Generate embeddings. Verify counts match~~ | **COMPLETE 2026-03-15.** 216 memories + 44 KB docs seeded with embeddings. Airtable migration skipped (Chris-approved) — seeded from files instead. |
| **0-D** | ~~Update `bot.py`, `config.py`, `supabase_sync.py` to use SupabaseMemory. Run verification tests~~ | **COMPLETE 2026-03-15.** 4 files modified (config.py, bot.py, memory_tool.py) + 1 new (supabase_sync.py). Airtable sync replaced with Supabase. Keyword matching replaced with pgvector semantic search. Interaction logging + session persistence added. 8/8 verification tests passed. **PHASE 0 COMPLETE.** |

---

### Phase 1 Batches: Core Workforce (11 agents)
**Chat Session 2** (batches 1-A through 1-C)
**Chat Session 3** (batches 1-D through 1-F)

| Batch | Work | Checkpoint |
|-------|------|------------|
| **1-A** | Build Think Tool sub-workflow in n8n | Record workflow ID, verify it accepts input and returns reasoning, update MEMORY.md |
| **1-B** | Build 4 shared utility workflows (check_email, check_calendar, check_hubspot, check_drive) | Record 4 workflow IDs, verify each returns data correctly, update MEMORY.md |
| **1-C** | Build Alex's n8n workflow — webhook + debounce + fast-paths + AI Agent + Think Tool + 5 sub-tools | Record workflow ID, verify Telegram webhook fires, test fast-path + AI path, update MEMORY.md + Alex MEMORY.md |
| **1-D** | Build Marcus's n8n workflow — AI Agent + Think Tool + 9 routing tool stubs (placeholder workflows) | Record workflow ID, verify routing logic works with stubs, update MEMORY.md + Marcus MEMORY.md |
| **1-E** | Build first 5 C-Suite agents (Atlas, Sterling, Vera, Cleo, Orion) — scaffold via Agent Factory, then refine | Record 5 workflow IDs, verify each receives routing from Marcus, update MEMORY.md + each agent's MEMORY.md |
| **1-F** | Build remaining 4 C-Suite agents (Felix, Sage, Axiom, Lex). Run full-chain verification tests | Record 4 workflow IDs, verify full chain: Telegram → Alex → Marcus → Agent → response. Mark Phase 1 COMPLETE. Full checkpoint. |

---

### Phase 2 Batches: Worker Agents
**Chat Session 4**

| Batch | Work | Checkpoint |
|-------|------|------------|
| **2-A** | Build Node + Vantage workers, connect to Orion. Update Orion's Think Tool routing | Record 2 workflow IDs, verify Orion delegates correctly, update MEMORY.md + Orion MEMORY.md |
| **2-B** | Build Echo + Quill workers, connect to Orion. Build Scout, connect to Cleo | Record 3 workflow IDs, verify all worker routing works, update MEMORY.md + Orion/Cleo MEMORY.md |
| **2-C** | Performance optimizations: streaming responses, conversation window tuning, parallel tool execution | Verify latency improvements, record benchmark numbers, update MEMORY.md |
| **2-D** | Direct Google API calls (replace gws subprocess). Full end-to-end regression test of all 16 agents | Verify no regressions, record final latency numbers. Mark Phase 2 COMPLETE. Full checkpoint. |

---

### Phase 3 Batches: Autonomous Evolution
**Chat Session 5**

| Batch | Work | Checkpoint |
|-------|------|------------|
| **3-A** | Build weekly autonomous audit workflow (Schedule Trigger → AI Agent → Supabase logs analysis → Slack report) | Record workflow ID, run manually to verify audit output quality, update MEMORY.md |
| **3-B** | Build escalation auto-fix (3-layer: Slack → n8n webhook → Marcus → Agent → Fix → Post resolution) | Verify auto-fix triggers correctly on simulated failure, update MEMORY.md |
| **3-C** | Build learning synthesis workflow (monthly Sage-driven harvest). Final system documentation | Verify synthesis runs, document entire system. Mark Phase 3 COMPLETE. Full checkpoint. |

---

### Memory Checkpoint Template

After every batch, write this to session-history.md:

```
### Batch [X-Y] — [Title]
- **Status:** COMPLETE / IN PROGRESS / BLOCKED
- **What was built:** [list]
- **Workflow IDs:** [list if applicable]
- **Files created/modified:** [list]
- **Decisions made:** [list]
- **Issues encountered:** [list]
- **Next batch:** [X-Z]
```

---

## Build Sequence Summary

```
CHAT 1 — Phase 0: Supabase Foundation
  ├── 0-A: Project + schema + RLS
  ├── 0-B: SupabaseMemory client
  ├── 0-C: Airtable → Supabase migration
  └── 0-D: Claude Code integration + verification

CHAT 2 — Phase 1 (first half): Think Tool + Alex + Marcus
  ├── 1-A: Think Tool sub-workflow
  ├── 1-B: 4 shared utility workflows
  └── 1-C: Alex's full n8n workflow

CHAT 3 — Phase 1 (second half): Marcus + 9 C-Suite
  ├── 1-D: Marcus orchestrator
  ├── 1-E: First 5 C-Suite agents
  └── 1-F: Last 4 C-Suite + full-chain verification

CHAT 4 — Phase 2: Workers + Performance
  ├── 2-A: Node + Vantage → Orion
  ├── 2-B: Echo + Quill → Orion, Scout → Cleo
  ├── 2-C: Performance optimizations
  └── 2-D: Direct Google API + regression test

CHAT 5 — Phase 3: Autonomous Evolution
  ├── 3-A: Weekly audit workflow
  ├── 3-B: Escalation auto-fix
  └── 3-C: Learning synthesis + final docs
```
