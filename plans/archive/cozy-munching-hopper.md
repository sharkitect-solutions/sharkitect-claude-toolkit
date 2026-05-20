# Phase 8.4: Business Operations Gap Analysis

## Context

Phases 1-8.3 built and optimized the toolkit (128 skills, 48 agents, 3 plugins) — but all optimization was done in isolation from the actual business operations. The Workforce HQ runs 16 specialized agents across 4 service lines, with 17 active n8n workflows, a Supabase shared brain, and 16+ MCP integrations. No one has systematically checked whether the toolkit actually covers what these agents and services need day-to-day.

Additionally, the Workforce HQ has documented 10+ operational issues (credential blockers, schema mismatches, destructive testing accidents, stale data, etc.) that may have been preventable with better tooling. The user wants this analysis to also identify where skills, agents, or plugins could act as guardrails against recurring problems.

### Architectural Shift (Active — being built in Workforce HQ)

The workforce is evolving to a **three-interface architecture** with a unified brain:

| Interface | Who | Direction | Purpose |
|-----------|-----|-----------|---------|
| **Claude Code / VS Code** | Marcus (gatekeeper) | Two-way | Primary work interface. Claude takes on agent roles as needed. Marcus orchestrates. |
| **Telegram Bot 1: "Sharkitect HQ"** | System | **One-way (outbound only)** | Receives automated reports: morning briefs, midday check-ins, evening briefs, audit reports, weekly/monthly. No user interaction. |
| **Telegram Bot 2: "Alex"** | Alex (EA) | Two-way | Mobile executive assistant. Triggers n8n orchestration, checks email/calendar, accesses full team. Used when away from desk. |

**Key changes from current state:**
- Alex is NO LONGER "The Gateway" for desk work — becomes mobile EA only
- Marcus is the true gatekeeper when at desk (via Claude Code)
- Current single Telegram bot is broken — needs splitting into two bots with distinct purposes
- **Unified brain:** Supabase (structured data) + Pinecone (long-term memory/embeddings) + Notion (documents)
- Memory must carry seamlessly across Claude Code sessions, n8n workflows, and Telegram interactions

**Impact on gap analysis:** This architecture introduces new platform requirements (Pinecone, second Telegram bot), changes agent role boundaries (Alex/Marcus), and creates a unified memory requirement that spans all three interfaces.

**Goal:** Map the full business operation against the toolkit, find gaps, and produce a prioritized build/buy queue for Phase 8.5.

## Inputs

### Workforce Structure (16 agents, 4 service lines)

| Agent | Title | Dept | Workers |
|-------|-------|------|---------|
| Alex | Executive Assistant | Mobile EA (Telegram) | — |
| Marcus | Chief of Staff | Gatekeeper (Claude Code) | — |
| Atlas | COO | Operations | — |
| Sterling | CFO | Finance | — |
| Vera | CBCO | Brand | — |
| Cleo | CMO | Marketing | Scout |
| Orion | CAITO | Technology | Node, Vantage, Echo, Quill |
| Felix | CRCO | Revenue | — |
| Sage | CKO | Knowledge | — |
| Axiom | CSAO | Strategy (Advisory) | — |
| Lex | CLO | Legal (Advisory) | — |
| Node | n8n Workflow Engineer | Tech (Worker) | — |
| Vantage | Workflow Intelligence Architect | Tech (Worker) | — |
| Echo | Reverse Engineering & Intelligence | Tech (Worker) | — |
| Quill | Prompt Engineer | Tech (Worker) | — |
| Scout | Lead Gen Pipeline | Marketing (Worker) | — |

**4 Service Lines:** VDR (Voice Digital Receptionist), RLR (Rapid Lead Response), SLW (SystemLink Workflows), CPS (Content & Social Publishing)

### Toolkit Inventory (from Skill Management Hub)
- 128 skills (all passing B-gate 96+/120)
- 48 sub-agents (all passing B-gate)
- 3 custom plugins (aios-core, quality-gate, auto-sync)
- 16+ MCP servers configured

### Operational History Sources
- Workforce HQ MEMORY.md: 10 codified process improvements (operational issues → fixes)
- Session history: 40+ sessions of build/debug/deploy history
- Supabase sharkitect-workforce: 292 memories, 51 KB docs across 16 agents
- Pending items list: 11 items (2 urgent, 5 active, 4 deferred)

## Analysis Methodology — 7 Sweeps

### Sweep 1: Supabase Health Audit
**Purpose:** Verify the shared brain is healthy, current, and capturing data correctly.

**Checks:**
1. Query Supabase via MCP — count memories per agent (all 16 should have data)
2. Check freshness — when was each agent's most recent memory written?
3. Check category distribution — are all categories (preference, rule, workflow, client, contact) populated?
4. Check KB doc coverage — are all 51 KB docs current with filesystem?
5. Check embedding quality — are embeddings present for all memories?
6. Compare Supabase memories vs MEMORY.md files — is there drift?

**Output:** Supabase health report with issues flagged.

### Sweep 2: Agent-to-Toolkit Mapping (16 agents)
**Purpose:** For each workforce agent, check if the toolkit provides adequate skills/agents/plugins for their defined responsibilities.

For each of the 16 agents, read their SKILLS.md and cross-reference against the toolkit:
- Are all skills listed in their SKILLS.md actually installed and optimized?
- Are the sub-agents they rely on in the toolkit?
- Are there responsibilities in their ROLE.md/OPERATIONS.md that have NO toolkit support?
- Are there toolkit capabilities that would benefit them but aren't in their SKILLS.md?

**Key files per agent:**
- `agents/{name}/ROLE.md` — responsibilities and authority
- `agents/{name}/SKILLS.md` — mapped skills, sub-agents, MCPs
- `agents/{name}/OPERATIONS.md` — SOPs and decision trees

**Output:** 16-row table: Agent | Current Skills | Missing Skills | Recommended Additions

### Sweep 3: Service Line Coverage
**Purpose:** For each service line, check end-to-end toolkit coverage.

| Service | Key Capabilities Needed | Check |
|---------|------------------------|-------|
| VDR | Voice AI, telephony, call routing, transcription, NLP | voice-agents, voice-ai-development, transcribe, twilio-communications |
| RLR | Lead capture, instant response, email/SMS, CRM integration | cold-email, email-composer, lead-research-assistant, outreach-specialist |
| SLW | Workflow automation, API integration, data sync, monitoring | n8n-*, api-patterns, database, supabase-postgres-best-practices |
| CPS | Content creation, social scheduling, brand compliance, SEO | content-creator, social-content, seo-optimizer, copywriting |

**Output:** 4-row table: Service | Coverage % | Gaps | Recommendations

### Sweep 4: Historical Issue Prevention Analysis
**Purpose:** Could any of the 10 codified operational issues have been prevented with a toolkit addition?

| # | Issue | Date | Could a skill/agent/plugin prevent this? |
|---|-------|------|------------------------------------------|
| 1 | Domain routing failure | 2026-03-03 | Routing validation skill? |
| 2 | Unverified brand review (3 false flags) | 2026-03-05 | Verification workflow/skill? |
| 3 | Credential blocker at end of build | 2026-03-05 | Pre-build checklist plugin? |
| 4 | Stale data from incoming/ file | 2026-03-10 | Data validation skill? |
| 5 | Plan file lost (.claude/plans/ ephemeral) | 2026-03-15 | Already codified as rule |
| 6 | Alex workflow deleted during testing | 2026-03-16 | Destructive ops guard? |
| 7 | Old bot artifacts persisted 2+ weeks | 2026-03-17 | Cleanup automation? |
| 8 | Supabase wrong column names | 2026-03-17 | Schema validation skill? |
| 9 | n8n "values" key caused 16/17 failures | 2026-03-17 | Already have n8n-validation-expert |
| 10 | n8n expression bracket ambiguity | 2026-03-22 | Already have n8n-expression-syntax |

**Output:** Issue prevention matrix with BUILD/ALREADY_COVERED/RULE_SUFFICIENT classification

### Sweep 5: Pending Work Gap Check
**Purpose:** For each pending item, identify toolkit components needed.

| # | Pending Item | Status | Toolkit Needs |
|---|-------------|--------|---------------|
| 1 | AIOS Vision Definition | URGENT | ai-agents-architect, agent-development, agent-memory-systems |
| 2 | TMC Data Analyst MVP | Active | data-privacy-compliance (HIPAA), statistical-analysis, xlsx |
| 3 | Fix ERA | Active | email-systems, systematic-debugging |
| 4 | ERA as Client Offering | Waiting | sales-enablement, pricing-strategy, sow-generator |
| 5 | Google Business Profile | Active | seo-optimizer, programmatic-seo |
| 6 | Voice AI Production | Active | voice-agents, voice-ai-development, transcribe, retellai-pack |
| 7 | Educational Presentations | Active | pptx, content-creator, launch-strategy |
| 8 | SystemLink: Check Dist | PAUSED | database, supabase-postgres-best-practices, api-patterns |

**Output:** Pending items with toolkit coverage assessment and gaps

### Sweep 6: Platform Integration Assessment
**Purpose:** Check MCP/CLI/API coverage for all platforms in use.

| Platform | Current Integration | Coverage | Gap? |
|----------|-------------------|----------|------|
| n8n | MCP (n8n-mcp) + API | HIGH | — |
| Supabase | MCP + REST API + Python SDK | HIGH | — |
| Google Workspace | CLI (gws) + MCP (Gmail, Calendar) | MEDIUM | Drive? Sheets? |
| HubSpot | MCP | MEDIUM | Limited ops? |
| Telegram (Bot 1: Sharkitect HQ) | Python SDK (python-telegram-bot) | MEDIUM | One-way reporting bot. No MCP. |
| Telegram (Bot 2: Alex) | Python SDK (python-telegram-bot) | LOW | Two-way EA bot. Needs n8n orchestration triggers. |
| Pinecone | **NEW — not yet integrated** | NONE | Long-term memory/embeddings for unified brain |
| Airtable | MCP (airtable-mcp-server) | HIGH | — |
| Slack | MCP | HIGH | — |
| Notion | MCP (2 servers) | HIGH | — |
| QuickBooks Online | REST API (manual) | LOW | No MCP, no skill |
| Monday.com | TBD | LOW | No integration |
| Twilio | Python SDK | MEDIUM | twilio-communications skill exists |
| GitHub | MCP + CLI (gh) | HIGH | — |
| Canva | MCP | MEDIUM | — |
| Clay | MCP | MEDIUM | — |
| Figma | MCP | HIGH | — |
| Jotform | MCP | MEDIUM | — |
| Cal.com | TBD | LOW | No integration noted |
| Firecrawl | MCP | HIGH | — |

**Output:** Platform coverage matrix with integration quality scores

### Sweep 7: Unused Toolkit Capabilities
**Purpose:** Identify skills/agents in the toolkit that NO workforce agent currently leverages.

Cross-reference the 128 skills and 48 agents against all 16 workforce agents' SKILLS.md files. Flag any toolkit components that aren't mapped to any agent — these are either:
- Overlooked capabilities that should be assigned
- Future-facing tools not yet needed
- Redundant with other capabilities

**Output:** Unused components list with ASSIGN/FUTURE/REMOVE recommendation

## Implementation Steps

### Step 1: Supabase Health Audit
1. Load Supabase MCP tools
2. Query memories table — count by agent_id, check timestamps
3. Query kb_docs table — compare against filesystem
4. Check for stale/missing data
5. Document findings

### Step 2: Agent Mapping (batch — 4 agents per sweep)
1. **Batch A:** Alex, Marcus, Atlas, Sterling — read SKILLS.md, cross-reference toolkit
2. **Batch B:** Vera, Cleo, Orion, Felix — read SKILLS.md, cross-reference toolkit
3. **Batch C:** Sage, Axiom, Lex, Node — read SKILLS.md, cross-reference toolkit
4. **Batch D:** Vantage, Echo, Quill, Scout — read SKILLS.md, cross-reference toolkit

### Step 3: Service Line + Historical + Pending Analysis
- Run Sweeps 3-5 together (they share context)
- Cross-reference findings with Supabase memories for additional context

### Step 4: Platform + Unused Toolkit Analysis
- Run Sweeps 6-7 together
- Identify integration gaps and orphaned capabilities

### Step 5: Gap Synthesis & Recommendations
Consolidate all 7 sweeps into a single prioritized gap report:

| Gap | Source (Sweep) | Severity | Recommendation | Action |
|-----|---------------|----------|----------------|--------|
| ... | ... | CRITICAL/HIGH/MEDIUM/LOW | BUILD/BUY/ASSIGN/SKIP | ... |

### Step 6: Write Results
- Save to `.tmp/audit-data/phase-8.4-gap-analysis.json`
- Update MEMORY.md with Phase 8.4 results
- Present executive summary to user for approval before Phase 8.5

## Key Files

### Read (Workforce HQ)
- `agents/{all 16}/ROLE.md` — responsibilities
- `agents/{all 16}/SKILLS.md` — toolkit mapping
- `agents/{all 16}/OPERATIONS.md` — SOPs and processes
- `knowledge-base/` — operational docs
- `tools/supabase_memory.py` — Supabase client code

### Read (Skill Management Hub)
- `.tmp/audit-data/` — previous gap analysis results
- `MEMORY.md` — toolkit inventory summary

### Query (MCP)
- Supabase MCP — memories table, kb_docs table

### Write (Skill Management Hub)
- `.tmp/audit-data/phase-8.4-gap-analysis.json` — full results
- `MEMORY.md` — updated with Phase 8.4 findings

## Expected Output

A prioritized gap report answering:
1. Which workforce agents lack toolkit support for their responsibilities?
2. Which service lines have incomplete coverage?
3. Which historical issues could have been prevented?
4. Which pending items need new toolkit components?
5. Which platform integrations are missing or weak?
6. Which toolkit capabilities are going unused?
7. Is the Supabase shared brain healthy and current?

This feeds directly into Phase 8.5 (Build) where we create the recommended skills/agents/plugins.

## Verification
1. All 16 agents analyzed (no agent skipped)
2. All 4 service lines covered
3. All 10+ historical issues reviewed
4. All 11 pending items checked
5. All 20+ platform integrations assessed (including Pinecone + split Telegram bots)
6. Supabase queried and health verified
7. Architectural shift (Marcus gatekeeper, Alex mobile EA, unified brain) reflected in gap findings
8. Gap report saved to `.tmp/audit-data/`
