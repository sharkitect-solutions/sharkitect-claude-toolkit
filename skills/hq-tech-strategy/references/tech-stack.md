# Sharkitect Technology Stack

## Core Infrastructure

| Component | Technology | Tier | Purpose | Status |
|-----------|-----------|------|---------|--------|
| **AI Agent** | Claude Code (Opus 4.6) | Tier 2 | Primary AI workforce | Active |
| **Database** | Supabase (PostgreSQL + pgvector) | Tier 2 | Memory, KB, operational data | Active |
| **Automation** | n8n (self-hosted) | Tier 1 | Workflow automation, scheduled tasks | Active |
| **Version Control** | GitHub | Tier 1 | Code, skills, agents, configs | Active |
| **Task Scheduling** | Windows Task Scheduler | Tier 1 | Daily briefs, audits, syncs | Active |
| **Communication** | Telegram (bot API) | Tier 1 | Morning briefs, alerts | Active |
| **Email** | SMTP (Python scripts) | Tier 2 | Client communications | Active |
| **Calendar** | Google Calendar (MCP + GWS CLI) | Tier 1 | Scheduling, availability | Active |
| **CRM** | HubSpot (MCP) | Tier 2 | Contact management, pipeline | Active |
| **Documents** | pandoc + python-docx/pptx | Tier 1 | Document generation | Active |
| **Web Scraping** | Firecrawl (MCP + CLI) | Tier 0 | Research, competitive intel | Active |
| **Design** | Canva (MCP) | Tier 0 | Marketing assets | Available |
| **Lead Enrichment** | Clay (MCP) | Tier 2 | Lead data enrichment | Available |
| **Vectors** | Supabase pgvector (1536 dims) | Tier 2 | Semantic search, embeddings | Active |
| **Project Management** | Notion (MCP) | Tier 1 | Documentation, wikis | Active |

## Platform Decisions (Active)

### Why Supabase for Everything
- **Decision date**: 2026-03-27
- **Rationale**: One system for relational + vector + auth. $25/mo Pro plan covers current needs. Handles up to 50M vectors with pgvectorscale.
- **Exit cost**: Moderate — standard PostgreSQL underneath, data is portable.
- **Expansion trigger**: 5M+ vectors OR sub-50ms query requirement → evaluate Pinecone alongside.
- **Reference**: `memory-architecture.md` in HQ knowledge base.

### Why n8n Over Zapier/Make
- **Decision date**: 2026-02 (initial setup)
- **Rationale**: Self-hosted = no per-execution costs at scale. Full code access. Native Supabase + API support.
- **Exit cost**: High — 17 workflows would need migration. But self-hosted means no vendor dependency.
- **Current state**: 17 workflows (3 fully built, 14 skeleton). ~35% complete.

### Why Claude Code Over Multi-Agent Frameworks
- **Decision date**: 2026-03-27 (restructure)
- **Rationale**: Claude Code IS the agent. Task tool provides real subprocess agents. Skills provide specialized behavior. No CrewAI/LangGraph overhead needed.
- **The mistake**: Building 16 agent folders that pretended to be separate agents when it's actually one agent with many skills.

## Stack Rules

1. **SMTP-first for email**: Never use third-party email services when direct SMTP works.
2. **Supabase-first for data**: All structured data goes to Supabase. No spreadsheets, no local databases, no competing data stores.
3. **Python stdlib-first for scripts**: No pip dependencies unless absolutely necessary. Every custom tool uses stdlib only.
4. **MCP > CLI > API**: Prefer MCP connections (native tool integration) over CLI subprocess calls over raw HTTP API calls.
5. **No new databases**: Supabase handles relational + vector + auth. Adding another database requires explicit justification.
