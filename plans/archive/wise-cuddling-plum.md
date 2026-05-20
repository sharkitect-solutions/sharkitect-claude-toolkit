# Plan: Sharkitect Digital Unified AI Brain

## Context

Sharkitect Digital operates across multiple platforms (Claude Code, n8n, Telegram) and multiple project workspaces (Skill Management Hub, Workforce HQ, future client projects). Today each workspace is an island — decisions, lessons, preferences, and context are trapped in local files. The goal is a **unified cognitive layer** where every agent, every platform, every workspace operates as one workforce with shared memory, shared context, and the ability to learn, evolve, and eventually operate autonomously.

### Current State
- Supabase exists with 7 tables (522 memories, 2,650 kb_docs, 76 tasks, 11 projects, 162 logs, 3 sessions, 99 audit entries)
- Only HQ syncs to Supabase; Skill Management Hub writes ZERO
- 16 legacy agent memories (175 entries) from deprecated multi-agent model
- KB docs (2,650) never verified as actually useful
- No cross-platform memory (Claude Code ↔ n8n ↔ Telegram disconnected)
- No voice/identity learning across sessions
- No conflict resolution, freshness scoring, or decision authority framework

### Design Decisions Made (see memory/decision_*.md files for full details)
- **Option C architecture**: Supabase as brain + local cache layer. Pinecone/Graphiti as future upgrade path.
- **Operations Center**: New dedicated workspace for auditing, briefs, monitoring, repo scanning, memory hygiene
- **Client isolation**: Each client gets own Supabase instance; Sharkitect brain stores pointers only
- **Ecosystem**: Supabase (AI brain), Notion (human-readable docs), Airtable (operations/KPIs), HubSpot (CRM)
- **File retention tags**: Retention markers on files that survive project completion, with review dates
- **Voice profiles**: Layered system (global → audience → client-specific) with approved/rejected samples
- **Repo monitoring**: Ops Center watches upstream repos, Skill Hub acts on findings proactively
- **6 autonomy gaps**: Decision authority, conflict resolution, watcher's watcher, cross-agent work requests, freshness scoring, feedback metrics

---

## Architecture Overview

### Three-Tier Memory Model

| Tier | Purpose | Storage | Write Freq | Read Freq |
|------|---------|---------|-----------|----------|
| **Working Memory** | Current session context, active phase | Local MEMORY.md + .tmp/ + Auto Dream | Every session | Every session start |
| **Shared Brain** | Cross-project decisions, lessons, voice, activity | Supabase (pgvector + structured tables) | Session end sync | Session start pull |
| **Deep Archive** | Raw activity stream, full audit trail | Supabase (append-only tables) | Continuous append | On-demand search |

### Five Memory Layers (stored in Supabase)

| Layer | What It Stores | Example |
|-------|---------------|---------|
| **Identity** | Voice, preferences, communication style, behavioral rules | "Chris prefers direct, no-BS communication" |
| **Knowledge** | Business SOPs, client info, tool stack, pricing | "Client X uses Airtable + n8n, 12 employees" |
| **Experience** | Decisions, failures, lessons, patterns | "Telegram bot wasted 3 days — scrapped, don't revisit" |
| **Working Memory** | Active tasks, phases, priorities, blockers | "SystemLink Phase 2 active, TMC pending" |
| **Activity Stream** | What happened, when, where, by whom | "2026-04-01 14:30 — n8n Alex handled email from Juan" |

### Workspace Ecosystem

| Workspace | Role | Brain Access |
|-----------|------|-------------|
| **Skill Management Hub** | Build, optimize, evaluate skills/agents/plugins. Proactive self-improvement. | Read findings + cross-project context, write evaluations |
| **Workforce HQ** | Client deliverables, workflows, SOPs, daily project work | Read/write own work context |
| **Operations Center** (NEW) | Audit, brief, monitor, repo scan, memory hygiene, client ops | Read ALL, write findings/briefs/health |
| **Client project folders** | Project-specific work | Read/write own context |

### Platform Integration

| Platform | Read From Brain | Write To Brain | Method |
|----------|----------------|---------------|--------|
| **Claude Code** (all workspaces) | Session start pull | Session end sync | aios-core hooks + sync module |
| **n8n** (Alex, client workflows) | Workflow step queries | Activity logging, task updates | Supabase REST API via HTTP Request nodes |
| **Telegram** (via Alex/n8n) | n8n reads on behalf | n8n writes on behalf | Through n8n workflows |

### External Tool Integration

| Tool | Role | Brain Relationship |
|------|------|-------------------|
| **Supabase** | AI Brain (source of truth) | IS the brain |
| **Notion** | Human-readable company docs, SOPs, client docs, archived references | Brain stores pointers to Notion pages |
| **Airtable** | Workflow logs, KPIs, client deliverable data, project tracking | Brain stores pointers to Airtable bases |
| **HubSpot** | CRM — contacts, deals, pipeline | Brain stores client_id cross-references |
| **GitHub** | Code repos, toolkit, fork monitoring | Ops Center monitors, brain tracks sync state |

---

## Supabase Schema Redesign

### Existing Tables (Keep + Modify)

**`memories`** — Add columns:
- `workspace` (text): which workspace wrote this (hq, skill-management-hub, ops-center, etc.)
- `source_file` (text): which local file originated this memory (for sync tracking)
- `freshness_verified_at` (timestamptz): when last confirmed as still true
- `decay_days` (int): how many days before flagged as needs_verification (30/90/180)
- `tags` (text[]): flexible tagging (voice, client:marcus, retention, etc.)

**`tasks`** — Add columns:
- `workspace` (text): originating workspace
- `locked_by` (text): which agent has exclusive checkout
- `locked_at` (timestamptz): when locked (auto-expire after timeout)
- `strategic_goal` (text): traces upward to project → company goal
- `rationale` (text): why this task exists

**`projects`** — Add columns:
- `workspace` (text): which workspace owns this project
- `client_id` (text): HubSpot cross-reference if client project
- `supabase_project_id` (text): client's own Supabase instance if AI OS client

**`logs`** — Keep as-is (already captures platform, agent_id, workflow info)

**`sessions`** — Keep as-is (minimal use currently, will grow with Alex)

**`audit_log`** — Add column:
- `workspace` (text): which workspace was audited

### New Tables

**`activity_stream`** (append-only, KAIROS pattern):
- id (uuid)
- timestamp (timestamptz)
- workspace (text)
- platform (text): claude-code, n8n, telegram, manual
- event_type (text): decision, correction, task_complete, sync, error, observation
- content (text): what happened
- actor (text): which agent/workflow
- metadata (jsonb): flexible additional context
- INDEX on (workspace, timestamp DESC)

**`voice_samples`**:
- id (uuid)
- content (text): the actual text
- status (text): approved / rejected
- content_type (text): email, proposal, slack, documentation, social
- audience (text): client, prospect, internal, partner
- client_id (text, nullable): specific client if client-specific voice
- tone (text): formal, casual, technical, friendly
- reason (text): why approved/rejected (Chris's words)
- context (text): situational context
- created_at (timestamptz)

**`work_requests`** (cross-agent handoffs):
- id (uuid)
- from_workspace (text)
- to_workspace (text)
- request (text): what's needed
- priority (text): low, medium, high, critical
- status (text): pending, accepted, in_progress, complete, declined
- rationale (text): why this was requested
- response (text, nullable): outcome or reason for decline
- created_at (timestamptz)
- updated_at (timestamptz)

**`retained_files`** (retention tag tracking):
- id (uuid)
- file_path (text)
- workspace (text)
- reason (text): why this file is retained
- originating_project (text)
- retained_by (text): which process decided
- retained_at (timestamptz)
- review_date (timestamptz): when to re-evaluate
- status (text): active, expired, released

**`system_health`** (watcher's watcher):
- id (uuid)
- component (text): ops-center, skill-hub-sync, hq-sync, nightly-dream, repo-monitor
- last_heartbeat (timestamptz)
- status (text): healthy, degraded, failed
- details (jsonb): last run stats
- INDEX on (component)

**`repo_findings`** (upstream monitoring):
- id (uuid)
- repo (text): which repo
- finding_type (text): new_component, update_available, fork_behind, breaking_change
- description (text)
- relevance_score (int): 1-10 for Sharkitect
- client_relevance (text[], nullable): which clients could benefit
- status (text): pending_evaluation, adopted, adapted, skipped
- evaluated_by (text, nullable): which workspace acted on it
- evaluation_notes (text, nullable)
- created_at (timestamptz)

### Tables to Clean Up

**`kb_docs`** (2,650 rows): Audit before migration.
- Query to find docs never retrieved (no search hits)
- Keep docs that ARE retrieved; archive or drop the rest
- Add `workspace` column for future multi-workspace docs

**`escalations`** (0 rows): Keep structure, will be used by Alex.

### Legacy Cleanup
- 16 old agent IDs (marcus, orion, node, cleo, etc.): Export descriptions to Notion, soft-delete from Supabase
- `claude-code-hq` (1 memory): Rename to proper workspace identifier

### New Indexes
- `memories`: (workspace, agent_id, category, active)
- `memories`: (workspace, tags) using GIN
- `activity_stream`: (workspace, timestamp DESC)
- `tasks`: (workspace, status, priority)
- `work_requests`: (to_workspace, status)
- `system_health`: (component)

### New RPC Functions
- `search_memories_cross_workspace`: Like existing `search_memories` but with optional workspace filter
- `get_session_context`: Returns combined working memory + relevant shared brain entries for a workspace at session start
- `check_freshness`: Returns memories past their decay threshold needing re-verification

---

## Sync Architecture

### Claude Code → Supabase (Session End Push)

**Module:** `supabase-sync.py` (shared across all workspaces, lives in toolkit repo)

On session end:
1. Hash local MEMORY.md + topic files
2. Compare against last sync hash
3. If changed: parse memory entries → upsert to Supabase `memories` table with workspace tag
4. Sync lessons-learned.md → Supabase `memories` (category: experience)
5. Sync active-phase.json → Supabase `projects`/`tasks` tables
6. Write activity_stream entry: "Session ended, X memories synced"
7. Store new hash

### Supabase → Claude Code (Session Start Pull)

**Module:** Enhanced `aios-core/session-start.py`

On session start:
1. Pull from Supabase `work_requests` where to_workspace = current workspace, status = pending
2. Pull from Supabase `repo_findings` where status = pending_evaluation (for Skill Hub)
3. Pull from Supabase `activity_stream` — last 24h of cross-workspace activity
4. Pull from Supabase `system_health` — any degraded/failed components
5. Pull from Supabase `memories` — any flagged as needs_verification relevant to this workspace
6. Check `retained_files` for any past review_date
7. Output summary to session context

### n8n → Supabase (Workflow Event Push)

Via HTTP Request nodes in n8n workflows:
- POST to `activity_stream` after significant workflow actions
- POST to `memories` for new learnings from Alex conversations
- PATCH `tasks` status when n8n workflows complete work
- POST to `work_requests` when Alex identifies something another workspace should handle

### Nightly Consolidation (Dream Cycle)

**Scheduled via n8n or Windows Task Scheduler, runs in Ops Center:**

1. **Orient**: Scan activity_stream from last 24h across all workspaces
2. **Gather Signal**: Identify contradictions, duplicates, corrections, recurring patterns
3. **Consolidate**: Merge duplicates, resolve contradictions (using conflict resolution protocol), update freshness timestamps
4. **Prune**: Flag stale memories past decay threshold, archive orphaned entries
5. **Synthesize**: Extract new rules/patterns from activity (e.g., "Chris corrected email tone 3x this week → update voice profile")
6. **Report**: Write consolidation summary to activity_stream

---

## Decision Authority Framework

| Level | Scope | Examples | Agent Behavior |
|-------|-------|---------|---------------|
| **Act + Log** | Low-risk, reversible, internal | Update memory, sync repos, run audits, reorganize files | Do it, write to activity_stream |
| **Act + Notify** | Medium-risk, reversible | Install skill, update hook, modify internal SOPs | Do it, notify Chris in next brief |
| **Draft + Hold** | Client-facing or financial | Emails, proposals, pricing quotes | Draft it, hold for Chris's approval |
| **Escalate** | High-risk or irreversible | Delete data, change pricing, client contracts, production deploys | Do NOT act, present to Chris with options |

---

## Conflict Resolution Protocol

When two memories or data points contradict:
1. Most recent timestamp wins (unless confidence differs)
2. `confirmed` beats `inferred` regardless of age
3. Direct correction from Chris beats any automated inference
4. When genuinely ambiguous → surface both to Chris with context, don't silently pick one
5. Log the conflict and resolution to activity_stream for future learning

---

## Behavioral Rules (Baked Into Brain)

Stored as category: `rule`, agent_id: `shared` — inherited by ALL agents on ALL platforms:
- Never be a yes-agent. Push back when something doesn't make sense.
- Reference past failures before repeating mistakes (check lessons-learned).
- Prioritize revenue-generating work over nice-to-haves.
- Be proactively honest, even if it's not what Chris wants to hear.
- Surface relevant context unprompted ("Remember, we tried this before...").
- Learn from corrections — immediately store voice/preference updates.
- When suggesting, always explain WHY with pros/cons.
- If blocked or uncertain, say so rather than guessing.

---

## Voice Profile System

Layered voice architecture:
```
Global voice (how Chris sounds in general)
  -> Audience voice (clients vs internal vs prospects)
     -> Client-specific voice (Marcus vs Juan vs new client)
```

Capture triggers:
- Direct corrections ("too salesy") → immediate write, category: voice
- Approved outputs → store as positive example with context
- Rejected outputs → store as anti-example with reason
- Pattern discovery → nightly consolidation synthesizes rules from samples

---

## Operations Center Scope

### Function 1: Internal Watchdog
- Audit each workspace for stale/orphan files
- Verify PLO hooks fire correctly
- Compare local vs git repos (flag drift)
- Compare local memory vs Supabase (flag sync gaps)
- Check retention tags and review dates

### Function 2: Intelligence Hub
- Morning/afternoon/evening briefs with priority analysis
- Cross-workspace status synthesis
- Overnight event analysis (reprioritize based on new info)
- Memory hygiene (recategorize, deduplicate, flag stale)

### Function 3: Client Ops Mirror
- Same audit/monitoring for client AI OS installations
- Client-specific configs, shared audit engine
- Feed gaps/findings to HQ for solution building

### Function 4: Repo Monitor
- Fork sync (detect behind upstream, auto-update or flag)
- New component evaluation (relevance scoring)
- Findings → Supabase → morning brief + Skill Hub session start

### Watcher's Watcher
- n8n workflow checks system_health table heartbeat
- Alerts via Telegram if any component flatlines
- Separate from Ops Center itself

---

## Feedback Metrics (Track Brain Effectiveness)

| Metric | What It Measures | Target Trend |
|--------|-----------------|-------------|
| Correction rate | How often Chris corrects agent output | Decreasing |
| First-draft acceptance | Outputs approved without changes | Increasing |
| Memory retrieval relevance | Surfaced context used vs ignored | Increasing |
| Time-to-resume | How long to pick up after a break | Decreasing toward zero |
| Gap detection accuracy | Ops Center true positives vs false alarms | Increasing |

Stored in Supabase. Ops Center includes trends in weekly brief.

---

## Legacy Cleanup (Migration Tasks)

1. Export 16 old agent descriptions to Notion (reference archive)
2. Soft-delete legacy agent memories in Supabase (set active=false)
3. Audit kb_docs (2,650 rows): identify never-retrieved docs, archive deadweight
4. Rename `claude-code-hq` agent_id to proper workspace identifier
5. Migrate HQ audit infrastructure to Operations Center workspace
6. Remove audit scripts from HQ once Ops Center is confirmed working

---

## Implementation Phases

### Phase 1: Foundation (Supabase Schema + Sync Module)
- Run DDL migrations: new columns on existing tables + new tables
- Build `supabase-sync.py` universal sync module
- Update aios-core session-start.py with Supabase pull
- Add session-end sync hook
- Enable Auto Dream on all workspaces
- **Verify:** Memory written in Skill Hub appears when HQ starts

### Phase 2: Operations Center Setup
- Create new workspace folder with CLAUDE.md
- Migrate audit scripts from HQ (cleaned up, rebuilt on new schema)
- Build morning/evening brief generators
- Set up repo monitoring (fork sync + upstream watch)
- Set up system_health heartbeat
- **Verify:** Morning brief includes cross-workspace status

### Phase 3: Brain Intelligence
- Implement nightly consolidation workflow (dream cycle)
- Build conflict resolution into memory queries
- Add freshness scoring and decay thresholds
- Implement voice profile capture hooks
- Build work_request system for cross-agent handoffs
- **Verify:** Corrections in one workspace propagate to all others

### Phase 4: Autonomy Framework
- Implement decision authority levels in agent behavioral rules
- Build feedback metrics tracking
- Set up watcher's watcher (n8n heartbeat monitor)
- Legacy cleanup (Notion export, kb_docs audit, agent migration)
- **Verify:** Agent correctly escalates high-risk decisions, acts on low-risk ones

### Phase 5: Client Extension
- Template the Operations Center audit engine for client deployments
- Build client isolation architecture (separate Supabase instances + pointers)
- Connect HubSpot cross-references
- Build client-specific voice profiles
- **Verify:** Client audit findings surface in Sharkitect morning brief

### Phase 6: Alex & n8n Integration
- Build Alex's n8n workflows with Supabase read/write
- Connect Telegram bot to brain (memory queries, task creation)
- Activity stream integration (n8n workflow events → Supabase)
- **Verify:** Tell Alex something via Telegram → Claude Code knows about it next session

---

## Critical Files

| File | Location | Role |
|------|----------|------|
| `supabase_memory.py` | HQ tools/ | Existing brain client (keep for HQ, extend with new schema) |
| `supabase-sync.py` | Toolkit repo (shared) | NEW — universal sync module for all workspaces |
| `session-start.py` | aios-core plugin | UPDATE — add Supabase pull |
| `session-end-sync.py` | aios-core plugin | NEW — add Supabase push |
| `dream-consolidation.py` | Ops Center tools/ | NEW — nightly memory consolidation |
| `repo-monitor.py` | Ops Center tools/ | NEW — fork sync + upstream watch |
| `brief-generator.py` | Ops Center tools/ | NEW — morning/evening brief synthesis |
| `health-heartbeat.py` | Ops Center tools/ | NEW — system health monitoring |

---

## Verification Plan

1. **Phase 1 test:** Create a memory in Skill Hub → end session → start HQ session → verify it appears
2. **Phase 2 test:** Run morning brief → verify it includes status from all workspaces
3. **Phase 3 test:** Correct an email tone in HQ → verify voice profile updates → verify Skill Hub sees it
4. **Phase 4 test:** Agent encounters a high-risk action → verify it escalates instead of acting
5. **Phase 5 test:** Client audit finds a gap → verify it appears in Sharkitect morning brief
6. **Full loop test:** Tell Alex via Telegram "remind me to check SystemLink tomorrow" → verify it appears in morning brief → verify Claude Code knows about it

---

## Reference Documents

- `memory/decision_ops_architecture.md` — Ops Center as separate workspace (revised from HQ)
- `memory/decision_ops_center_scope.md` — 3 functions + repo monitoring
- `memory/decision_retention_tags.md` — File retention tag system
- `memory/decision_voice_profile.md` — Voice profile with client-specific layers
- `memory/decision_repo_monitoring.md` — Upstream repo monitoring and proactive toolkit evolution
- `memory/decision_autonomy_gaps.md` — 6 missing pieces for autonomous operation
- `resources/video-insights/full-analysis.md` — 10 video analyses with pattern extraction
