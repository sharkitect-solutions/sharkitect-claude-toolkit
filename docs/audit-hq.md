# Workspace Audit: Workforce HQ

**Audit Date:** 2026-04-09
**Auditor:** Claude Code (Phase 1A — Foundation Reset)
**Workspace Path:** `C:\Users\Sharkitect Digital\Documents\Claude Code Workspaces\1.- SHARKITECT DIGITAL WORKFORCE HQ`

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| **Workspace Name** | Sharkitect Digital Workforce HQ |
| **Workspace Number** | 1 |
| **Stated Purpose** | "Sharkitect Digital's operations center. One AI agent with specialized skills handles all company operations: strategy, finance, brand, marketing, technology, revenue/sales, knowledge management, and legal." |
| **Repo** | `sharkitect-solutions/sharkitect-workforce-hq` (private, GitHub) |

### Purpose Drift Assessment

**DRIFT DETECTED — MODERATE.** The stated purpose says "one AI agent with specialized skills" but significant artifacts still describe a 16-agent model:

1. `workflows/operating-rhythm.md` — References Alex, Marcus, Sage, Atlas, Sterling, Vera, Cleo, Orion, Felix, Axiom by name as active agents coordinating work. Describes Marcus as orchestrator, Alex checking rhythm calendar, Sage doing knowledge synthesis, etc.
2. `workflows/governance-enforcement.md` — `owner: marcus`, references Marcus, Sage, Atlas as "routine enforcers" and Axiom as escalation tier.
3. `workflows/learning-synthesis.md` — `owner: sage`, describes Sage harvesting "all 16 agent MEMORY.md files."
4. `workflows/performance-governance.md` — `owner: marcus`, describes three-level performance architecture across 16 agents.
5. `knowledge-base/governance/workforce-governance-framework.md` — Says "single source of truth for how governance is structured across all 16 agents."
6. `.tmp/workforce-workflow-ids.json` — Maps 16 agent names to n8n workflow IDs (these n8n workflows likely no longer exist or serve the original purpose).
7. Multiple KB docs have `owner:` frontmatter referencing agent names (atlas, sage, marcus, felix, lex, etc.).
8. `knowledge-base/clients/fantastic-floors/systemlink-estimate-sync/sop-monday-qbo-estimate-sync.md` — Version history references "Orion," "Node," "Sterling," "Vera," "Atlas" as contributors.

**The workspace's CLAUDE.md and README.md correctly describe the single-agent model.** The drift is in downstream documents that were never updated after the AIOS restructure (2026-03-27/28).

---

## 2. FILE INVENTORY

### workflows/ (9 files)

| File | Last Updated | Summary | Status |
|------|-------------|---------|--------|
| `ceo-brief-templates.md` | 2026-04-08+ | Templates for AI-generated CEO briefs (morning/midday/evening) | **ACTIVE** |
| `cron-schedule.md` | 2026-04-08+ | CronCreate job definitions for HQ session | **ACTIVE** (but see Section 8 for CronCreate concerns) |
| `operating-rhythm.md` | 2026-03-23 | Daily/weekly/monthly/quarterly cadence definitions | **STALE** — Entire document describes 16-agent orchestration (Alex→Marcus→agents). References "16 agent MEMORY.md files," agent-specific scans, Marcus synthesizing reports. None of this exists anymore. |
| `governance-enforcement.md` | 2026-03-03 | Governance enforcement framework | **STALE** — Owner: marcus. Describes Marcus, Sage, Atlas as enforcers, Axiom as escalation. Agent model is dead. |
| `learning-synthesis.md` | 2026-03-03 | Cross-agent learning synthesis | **STALE** — Owner: sage. Describes Sage harvesting 16 MEMORY.md files. Agent model is dead. |
| `performance-governance.md` | 2026-03-03 | Three-level performance measurement | **STALE** — Owner: marcus. Describes enterprise/department/agent KPI hierarchy across 16 agents. |
| `project-setup.md` | Unknown | WAT framework bootstrap procedure | **ACTIVE** (generic, still applicable) |
| `skills-evaluation.md` | Unknown | Dynamic skill discovery and matching | **ACTIVE** (generic, still applicable) |
| `hq-cleanup-audit.md` | Unknown | Cleanup/audit workflow | **ACTIVE** (generic procedure) |

**Flagged references:**
- `operating-rhythm.md` line 7: `owner: marcus`
- `operating-rhythm.md` line 24: "CronCreate with full AI reasoning" as primary brief generation (CronCreate is session-only)
- `operating-rhythm.md` line 39: "Alex checks the Operating Rhythm Calendar"
- `operating-rhythm.md` line 43: "Alex informs Marcus of due rhythm activities"
- `operating-rhythm.md` line 44: "Marcus executes the rhythm activities"
- `operating-rhythm.md` lines 123-156: Weekly cadence coordinated by Marcus with Sage, Atlas, Sterling
- `operating-rhythm.md` lines 162-305: Monthly/quarterly cadences with full 16-agent participation
- `operating-rhythm.md` line 110: "Felix's proposal" in task capture example
- `governance-enforcement.md` line 7: `owner: marcus`
- `learning-synthesis.md` line 7: `owner: sage`
- `performance-governance.md` line 7: `owner: marcus`

### tools/ (Top-level scripts — 15 files + error-autofix/)

| File | Summary | Status |
|------|---------|--------|
| `bootstrap.py` | WAT framework environment bootstrap | **ACTIVE** |
| `hq-brief-generator.py` | Fallback brief generator (Python, no MCP) | **ACTIVE** |
| `fallback-brief-sender.py` | Sends cached/generated brief if CronCreate missed | **ACTIVE** (but references RemoteTrigger — see below) |
| `fallback-morning-brief.bat` | Task Scheduler trigger for morning fallback | **ACTIVE** |
| `fallback-midday-brief.bat` | Task Scheduler trigger for midday fallback | **ACTIVE** |
| `fallback-evening-brief.bat` | Task Scheduler trigger for evening fallback | **ACTIVE** |
| `supabase-sync.py` | Shared Supabase sync script (push/pull/status) | **ACTIVE** |
| `supabase_memory.py` | Supabase brain read/write library | **ACTIVE** |
| `seed_supabase.py` | Seed Supabase with initial data | **ACTIVE** (utility) |
| `seed_plan_to_supabase.py` | Seed project plans to Supabase | **ACTIVE** (utility) |
| `sop_docx_builder.py` | Branded DOCX builder | **ACTIVE** |
| `create_check_dist_airtable_v2.py` | SystemLink Airtable table creator | **ACTIVE** (project-specific) |
| `create_check_dist_workflow_v3.py` | SystemLink n8n workflow creator | **ACTIVE** (project-specific) |
| `patch_workflow_sov_parsing.py` | Patch SOV parsing in n8n workflow | **ACTIVE** (project-specific) |
| `ff_report_data.py` | FF client report data extraction | **ACTIVE** (project-specific) |
| `generate_ff_report.py` | FF performance report generator (Python) | **ACTIVE** (project-specific) |
| `generate_ff_report_docx.js` | FF report DOCX generation (Node.js) | **ACTIVE** (project-specific) |
| `generate_ff_report_pptx.js` | FF report PPTX generation (Node.js) | **ACTIVE** (project-specific) |
| `read_docx.py` | DOCX reader utility | **ACTIVE** |
| `read_pptx.py` | PPTX reader utility | **ACTIVE** |

**Flagged references:**
- `fallback-brief-sender.py` line 52: Comment says "Check for brief_sent events from ANY source (HQ or RemoteTrigger)" — RemoteTrigger is broken/eliminated.

### tools/error-autofix/ (11 files + pycache)

| File | Summary | Status |
|------|---------|--------|
| `server.py` | FastAPI bridge server (webhook → Claude Code CLI) | **ACTIVE** |
| `claude_runner.py` | Spawns Claude Code CLI for auto-fix | **ACTIVE** |
| `config.py` | Pydantic settings from .env | **ACTIVE** |
| `prompt_template.py` | Prompt template for error diagnosis | **ACTIVE** |
| `safety.py` | Dedup, rate limit, circuit breaker | **ACTIVE** |
| `start.bat` | Start bridge server (visible window) | **ACTIVE** |
| `start.sh` | Start bridge server (Unix) | **ACTIVE** |
| `start_hidden.pyw` | Start bridge server hidden (Windows login) | **ACTIVE** |
| `start_tunnel.pyw` | Start cloudflared tunnel (Windows login) | **ACTIVE** |
| `requirements.txt` | Python dependencies | **ACTIVE** |
| `bridge.log` | Runtime log | **ACTIVE** (runtime artifact) |
| `tunnel.log` | Tunnel runtime log | **ACTIVE** (runtime artifact) |
| `tunnel_url.txt` | Current tunnel URL | **ACTIVE** (runtime artifact) |
| `__init__.py` | Package init | **ACTIVE** |

### tools/hooks/ (4 files)

| File | Summary | Status |
|------|---------|--------|
| `agent-folder-blocker.py` | Blocks creation of new agent folders | **ACTIVE** |
| `check_claude_md_line_count.sh` | Warns if CLAUDE.md exceeds line limit | **ACTIVE** |
| `check_memory_line_count.sh` | Warns if MEMORY.md exceeds line limit | **ACTIVE** |
| `file-age-warning.py` | Warns about old/stale files | **ACTIVE** |

### knowledge-base/ (Organized by subdirectory)

#### knowledge-base/strategy/ (7 files)

| File | Summary | Status |
|------|---------|--------|
| `business-plan.md` | Company business plan | **ACTIVE** |
| `executive-summary.md` | Executive summary | **ACTIVE** |
| `icp.md` | Ideal Customer Profile | **ACTIVE** |
| `messaging-framework.md` | Messaging framework | **ACTIVE** |
| `partnership-model-strategy.md` | Partnership model | **ACTIVE** |
| `positioning.md` | Market positioning | **ACTIVE** |
| `strategic-blueprint.md` | Strategic blueprint | **ACTIVE** |

#### knowledge-base/governance/ (4 files + .gitkeep)

| File | Summary | Status |
|------|---------|--------|
| `brand-identity-guide.md` | Brand voice & identity (SOT) | **ACTIVE** |
| `financial-operations-guide.md` | Financial operations | **ACTIVE** |
| `tool-stack-reference.md` | Tool stack reference | **ACTIVE** |
| `workforce-governance-framework.md` | Governance framework | **STALE** — References "all 16 agents," agent-level governance, department-level enforcement. |

#### knowledge-base/operations/ (2 files + .gitkeep)

| File | Summary | Status |
|------|---------|--------|
| `partnership-operations-manual.md` | Partnership ops manual | **ACTIVE** |
| `partnership-renewal-exit-framework.md` | Renewal/exit framework | **ACTIVE** |

#### knowledge-base/revenue/ (12 files + .gitkeep)

All **ACTIVE**. Core business documents (pricing, sales, proposals, discovery, etc.).

#### knowledge-base/sops/ (11 files + .gitkeep)

All **ACTIVE** except:
- `sow-template-slw.md` — frontmatter `owner: atlas, lex` (agent names)
- `discovery-signoff-template-slw.md` — frontmatter `owner: felix, atlas` (agent names)

#### knowledge-base/projects/ (12 project folders)

| Folder | Summary | Status |
|--------|---------|--------|
| `aios-vision-definition/` | AIOS product definition (5 files) | **ACTIVE** |
| `briefing-system-rebuild/` | Briefing system plan | **ACTIVE** (complete) |
| `educational-meetings/` | Educational meetings plan | **ACTIVE** (pending) |
| `email-response-automation/` | ERA project (5 files) | **ACTIVE** (tabled) |
| `era-client-offering/` | ERA client offering plan | **STALE** — Duplicate/superseded by `email-response-automation/`? |
| `fix-era/` | Fix ERA plan | **STALE** — Separate from `era-client-offering/` and `email-response-automation/`? Three ERA folders. |
| `google-business-profile/` | GBP update plan | **ACTIVE** (pending) |
| `operational-foundation/` | Operational foundation plan | **UNKNOWN** — May be superseded by Foundation Reset |
| `telegram-ai-bot/` | Telegram bot research | **ACTIVE** (tabled) |
| `tmc-data-analyst/` | TMC data analyst plan | **ACTIVE** (tabled) |
| `unified-ai-workforce/` | Unified workforce plan | **ACTIVE** (tabled) |
| `voice-ai/` | Voice AI plan | **ACTIVE** (tabled) |

#### knowledge-base/clients/fantastic-floors/ (2 project folders)

| Folder | Summary | Status |
|--------|---------|--------|
| `systemlink-check-distribution/` | Check dist project (12 files + 6 deliverables) | **ACTIVE** |
| `systemlink-estimate-sync/` | Estimate sync project (1 SOP + 3 deliverables) | **ACTIVE** (but SOP references agent names in version history) |

### resources/ (3 image files + .gitkeep)

All **ACTIVE** (logo images).

### _archive/ (Agent folders + legacy files)

| Contents | Status |
|----------|--------|
| 12+ agent folders (alex, atlas, axiom, cleo, echo, felix, lex, marcus, node, etc.) | **ARCHIVED** — Correctly moved here. Reference only. |
| `skill_proposer.py` | **ARCHIVED** — References all agent names. |
| `Sharkitect AI Workforce Master Reference v5.md` | **ARCHIVED** — Full 16-agent architecture doc. |

### .tmp/ (21 files — all disposable/regenerated)

Notable items:
- `workforce-workflow-ids.json` — Maps 16 agent names to n8n workflow IDs. **STALE** if those n8n workflows no longer exist.
- `skills-manifest.json` — Current skills manifest. **ACTIVE**.
- `session-heartbeat.json` — Session heartbeat. **ACTIVE**.
- `ff-extraction/` — FF project data extraction files. **ACTIVE** (SystemLink project).

### DELETED FILES (in git working tree, not yet committed)

Per `git status`, these files have been deleted but not committed:
- `tools/ralph-scheduler.py` — Was the scheduler that wrote brief triggers. Superseded by Task Scheduler.
- `tools/register-triggers.py` — Registered Task Scheduler triggers. One-time use, done.
- `tools/register-trigger-tasks.bat` — Batch wrapper for above.
- `tools/write-brief-trigger.py` — Wrote trigger files. Superseded.
- `tools/trigger-morning-brief.bat` — Old trigger approach. Superseded by fallback-*.bat.
- `tools/trigger-midday-brief.bat` — Same.
- `tools/trigger-evening-brief.bat` — Same.
- `.tmp/last-evening-brief.txt` — Transient, may have been consumed.
- `.tmp/last-morning-brief.txt` — Same.

**These deletions should be committed.**

---

## 3. AUTONOMOUS SYSTEMS

| System | How It Runs | Schedule | Working? | Spec Doc |
|--------|-------------|----------|----------|----------|
| **CEO Morning Brief** | CronCreate (session-only) + Task Scheduler fallback | 5:57 AM CT (CronCreate) / 6:15 AM CT (fallback) | **PARTIALLY** — CronCreate only works when session is open. Fallback ran today (exit code 2147942402 = user not logged in at that time). | `workflows/ceo-brief-templates.md` + `workflows/cron-schedule.md` |
| **CEO Midday Brief** | CronCreate (session-only) + Task Scheduler fallback | 12:03 PM CT (CronCreate) / 12:15 PM CT (fallback) | **YES** — Fallback ran today, exit code 0. | Same as above |
| **CEO Evening Brief** | CronCreate (session-only) + Task Scheduler fallback | 8:57 PM CT (CronCreate) / 9:15 PM CT (fallback) | **PARTIALLY** — Last run 4/8 exit code 2147942402. | Same as above |
| **Error Auto-Fix Bridge** | Python FastAPI server, auto-starts on Windows login via `start_hidden.pyw` | Always-on (when machine is on) | **YES** — E2E tested 2026-04-08 | `MEMORY.md` project section (no standalone spec doc) |
| **Cloudflared Tunnel** | Python script, auto-starts on Windows login via `start_tunnel.pyw` | Always-on (when machine is on) | **YES** — Tested with error auto-fix | **NONE** (documented in MEMORY.md only) |
| **Supabase Sync** | `supabase-sync.py` — manual/session-based | On demand (session start/end) | **YES** | **NONE** (code is self-documenting but no spec) |
| **Lifecycle Review Polling** | CronCreate (session-only) | Every 7 minutes (when session open) | **UNKNOWN** — Only runs during active sessions. No fallback. | `workflows/cron-schedule.md` |
| **Drift Detection** | Hook fires on Write/Edit events | Event-driven (during session) | **UNKNOWN** — Depends on `doc-lifecycle-cache.json` being current | **NONE** (described in CLAUDE.md universal protocols) |

### Systems Described in Docs But NOT Actually Running

| System | Described In | Reality |
|--------|-------------|---------|
| **Weekly workforce scan** | `workflows/operating-rhythm.md` lines 120-158 | **DOES NOT EXIST** — Requires Marcus, Sage, Atlas, Sterling agents |
| **Monthly workforce review** | `workflows/operating-rhythm.md` lines 162-245 | **DOES NOT EXIST** — Requires all 7 C-Suite agents |
| **Quarterly strategic assessment** | `workflows/operating-rhythm.md` lines 249-305 | **DOES NOT EXIST** — Requires Axiom, Sage, Atlas agents |
| **Hourly Supabase sync** | `workflows/operating-rhythm.md` line 112-114 | **DOES NOT EXIST** — operating-rhythm.md says "every hour" but no Task Scheduler job exists for this. MEMORY.md lists "SupabaseSync hourly" in Task Scheduler section but PowerShell query returned no such task. |
| **Governance enforcement** | `workflows/governance-enforcement.md` | **DOES NOT EXIST** — Requires Marcus, Sage, Atlas as enforcers |
| **Learning synthesis** | `workflows/learning-synthesis.md` | **DOES NOT EXIST** — Requires Sage harvesting 16 MEMORY.md files |
| **Performance governance** | `workflows/performance-governance.md` | **DOES NOT EXIST** — Requires 16-agent KPI hierarchy |

---

## 4. SUPABASE USAGE

### Tables This Workspace READS From

| Table | Script(s) | Purpose |
|-------|-----------|---------|
| `memories` | `supabase-sync.py`, `supabase_memory.py` | Pull workspace memories, search, stale detection |
| `projects` | `hq-brief-generator.py` | Brief generation — active projects |
| `tasks` | `hq-brief-generator.py` | Brief generation — active and completed tasks |
| `briefs` | `hq-brief-generator.py`, `fallback-brief-sender.py` | Dedup check — has a brief already been sent? |
| `activity_stream` | `supabase-sync.py` | Cross-workspace activity awareness |

### Tables This Workspace WRITES To

| Table | Script(s) | Purpose |
|-------|-----------|---------|
| `memories` | `supabase-sync.py`, `supabase_memory.py` | Upsert memories from MEMORY.md + topic files |
| `activity_stream` | `supabase-sync.py`, `hq-brief-generator.py` | Log session events, brief_sent events |
| `briefs` | `hq-brief-generator.py` | Log sent briefs |
| `error_fixes` | `tools/error-autofix/server.py` | Log auto-fix attempts and results |
| `projects` | `seed_plan_to_supabase.py` | Seed/update project records |
| `tasks` | `seed_plan_to_supabase.py` | Seed/update task records |

### Workspace Name String

**Consistent:** `"workforce-hq"` everywhere checked:
- `hq-brief-generator.py` line 559: `"workspace": "workforce-hq"`
- `supabase-sync.py` line 131: `return "workforce-hq"` (from CLAUDE.md detection)
- `supabase-sync.py` line 142: `return "workforce-hq"` (from path detection)
- `supabase-sync.py` line 790: `workforce-hq` in help text

**No inconsistencies found** (no `"hq"` or `"workforce"` alone used as workspace identifier).

### Known Issues

- **No evidence of workspace creating its own tables.** All table references match the documented Supabase schema.
- `supabase_memory.py` line 76 references `agent_id` column for "per-agent isolation" — this is a leftover from the 16-agent model. The code still works (it just uses a single agent_id), but the concept is stale.

---

## 5. TASK SCHEDULER JOBS

| Task Name | Schedule | .bat Path | Last Run | Exit Code | Status |
|-----------|----------|-----------|----------|-----------|--------|
| `FallbackMorningBrief` | Daily 6:15 AM | `tools\fallback-morning-brief.bat` | 2026-04-09 6:15 AM | 2147942402 | **PARTIAL** — Code means "user not logged in." Works when machine is awake. |
| `FallbackMiddayBrief` | Daily 12:15 PM | `tools\fallback-midday-brief.bat` (via `.tmp\..\tools\` path) | 2026-04-09 12:15 PM | 0 | **WORKING** |
| `FallbackEveningBrief` | Daily 9:15 PM | `tools\fallback-evening-brief.bat` | 2026-04-08 9:15 PM | 2147942402 | **PARTIAL** — Same "not logged in" issue. |

### Missing/Expected Jobs

| Expected Job | Status |
|-------------|--------|
| `SupabaseSync` (hourly) | **MISSING** — MEMORY.md claims this exists but PowerShell query returned no matching task. Either it was never created, or it was deleted and MEMORY.md not updated. |
| `TriggerMorningBrief` (6:00 AM) | **MISSING/DELETED** — MEMORY.md lists this but git status shows `trigger-morning-brief.bat` was deleted. May have been cleaned up and MEMORY.md not updated. |
| `TriggerMiddayBrief` (12:00 PM) | **MISSING/DELETED** — Same. |
| `TriggerEveningBrief` (9:00 PM) | **MISSING/DELETED** — Same. |

### Inconsistency

MEMORY.md "Task Scheduler" section lists 6 active tasks + "9 legacy disabled." PowerShell only found 3 active tasks. Either the trigger tasks were deleted, or they exist under different names, or the disabled tasks were fully removed. MEMORY.md is out of date.

### Path Inconsistency

`FallbackMiddayBrief` uses a different path format (`".tmp\..\tools\fallback-midday-brief.bat"` with quotes and relative path) compared to the other two (direct absolute paths without quotes). This works but is inconsistent.

---

## 6. n8n WORKFLOWS

### Workflow IDs in `.tmp/workforce-workflow-ids.json`

| Name | Workflow ID | What It Represents |
|------|------------|-------------------|
| `think` | `fvutg0RoW3YKuT3V` | Unknown — "think" workflow |
| `alex` | `jksDsTpZS2bcGuIV` | Alex assistant |
| `marcus` | `YaZMRjAV2Qo6U8rY` | Marcus orchestrator |
| `atlas` | `F6eqZi4PfSp8qMnv` | Atlas operations |
| `sterling` | `7bBURxrc8HhUaJ3Y` | Sterling finance |
| `vera` | `peSNCgTCYlPwbRXY` | Vera brand |
| `cleo` | `7TZzIEpCB4tPqrK9` | Cleo marketing |
| `orion` | `9fMcUv5ebqcJeVST` | Orion technology |
| `felix` | `YmYV1ZvhGrp458cO` | Felix revenue |
| `sage` | `kqY4DYpfwNULXPtN` | Sage knowledge |
| `axiom` | `cHgvL67lSOc8e9tA` | Axiom strategy |
| `lex` | `ws5t3ILBQRs8SQ08` | Lex legal |
| `node` | `wPpWO79SU0SuzDsv` | Node n8n engineer |
| `vantage` | `eMuVowW2sXBSD9lh` | Vantage analytics |
| `echo` | `miq14bQat21KiNcC` | Echo execution |
| `quill` | `lSp1vbC2RIq2uKMh` | Quill content |
| `scout` | `bmW6S0EZu4rzVB43` | Scout lead gen |

**STATUS: LIKELY ALL STALE.** These are from the 16-agent n8n architecture. CLAUDE.md says n8n has "17 workflows (all active)" but the only ones confirmed still relevant are:
- **Alex** (`jksDsTpZS2bcGuIV`) — Personal assistant (if still running)
- **Internal Error Handler** (`3AVNR5ZAfuelDz5d`) — Referenced in MEMORY.md for error auto-fix
- **Check Distribution v3** (`bt54zeRz9SIOmSqf`) — SystemLink project
- **Delete Unassigned** (`DHgxqssKWspsoh7x`) — SystemLink project

The other 13+ agent workflows were likely never updated after the restructure. **This file should be verified against actual n8n instance state.**

---

## 7. CROSS-WORKSPACE AWARENESS

### Known Workspaces

| # | Workspace | Believed Responsibility |
|---|-----------|------------------------|
| 1 | **Workforce HQ** (this) | Client work, business operations, revenue, CEO briefs, error auto-fix |
| 2 | **Skill Management Hub** | Skills, hooks, agents, plugins, gap detection/alerting/processing |
| 3 | *(Unknown/not referenced)* | — |
| 4 | **Sentinel** | Monitoring, briefs, dream consolidation, system intelligence, health checks |

### What Other Workspaces Know About HQ

- **Skill Hub** receives gap reports from HQ via `~/.claude/scripts/gap-reporter.py` → `.gap-reports/inbox/`
- **Sentinel** is referenced as handling "system health report" (5:45 AM CT) in `operating-rhythm.md`
- All workspaces share `supabase-sync.py` (it's described as "shared across ALL Sharkitect workspaces")

### Routing Rules Followed

Per CLAUDE.md and universal protocols:
- Building a skill/hook/agent → Skill Hub
- Building/fixing a business n8n workflow → HQ
- Building/fixing a monitoring n8n workflow → Sentinel
- Client deliverables → HQ
- Monitoring/audits → Sentinel
- Gap reports (detection) → Skill Hub processes them
- Modifying Task Scheduler → Workspace that owns the system

### Gaps in Awareness

- **Workspace 3** is never mentioned. The numbering goes 1, 2, 4. Either workspace 3 was dissolved/merged or it exists and HQ doesn't know about it.
- **"Autonomous Operations" (workspace 5)** was dissolved per universal protocols. No remaining references found in non-archive files (clean).
- MEMORY.md says "Sentinel (workspace 4)" but CLAUDE.md architecture section doesn't assign a number to Sentinel — it just says "Sentinel."

---

## 8. GAPS AND CONTRADICTIONS

### Critical Issues

1. **4 workflow files describe a dead architecture.** `operating-rhythm.md`, `governance-enforcement.md`, `learning-synthesis.md`, and `performance-governance.md` all describe a 16-agent orchestration model that was replaced in March 2026. They are not just stale — they are actively misleading. Any session that reads these will try to coordinate non-existent agents.

2. **MEMORY.md Task Scheduler section is wrong.** Claims 6 active tasks (SupabaseSync + 3 Trigger + 3 Fallback) + "9 legacy disabled." Reality: only 3 Fallback tasks exist. The Trigger tasks were deleted (along with their .bat files). SupabaseSync doesn't exist. The "9 legacy disabled" tasks may have been fully removed.

3. **CronCreate is documented as "PRIMARY" everywhere but is session-only.** `cron-schedule.md`, `CLAUDE.md`, and `README.md` all describe CronCreate as the primary scheduling mechanism with Task Scheduler as "FALLBACK." In reality, CronCreate only runs when a Claude Code session is open. If no session is open (which is the common case for 6 AM and 9 PM briefs), CronCreate doesn't fire and the "fallback" becomes the only path. The "primary/fallback" framing is inverted from reality.

4. **`operating-rhythm.md` and `ceo-brief-templates.md` describe the same system differently.** `operating-rhythm.md` has a detailed spec for brief content (sections, sources, formulas) from the old agent era. `ceo-brief-templates.md` has the current spec used by CronCreate. They conflict on section names, data sources, and formats. Two specs, one system.

5. **No standalone spec for the Error Auto-Fix system.** It's documented only in MEMORY.md. If MEMORY.md gets pruned or the entry ages out, the system's architecture, safety controls, and IDs are lost.

6. **Three ERA project folders.** `email-response-automation/` (5 files), `era-client-offering/` (1 file), and `fix-era/` (1 file). Unclear which is authoritative. All three are "tabled" so no immediate harm, but a cleanup candidate.

### Moderate Issues

7. **`workforce-governance-framework.md` says "all 16 agents"** but was last updated 2026-04-05 — after the restructure. This means it was touched post-restructure but its content wasn't updated.

8. **6 KB documents have agent names in frontmatter** (`owner: marcus`, `owner: sage`, `owner: atlas, lex`, `owner: felix, atlas`). These owner fields are meaningless in the single-agent model.

9. **`fallback-brief-sender.py` references RemoteTrigger** on line 52 in a comment. RemoteTrigger is documented as broken/eliminated. The code still works (it's just a comment checking for brief_sent events from "any source"), but the comment is misleading.

10. **`.tmp/workforce-workflow-ids.json` maps 16 agent names to n8n workflow IDs.** These IDs may point to workflows that no longer exist or were repurposed. This file is consumed by tools that may try to reference these workflows.

11. **CLAUDE.md says "17 workflows (all active)"** but only 4 workflows are confirmed relevant to current operations. The number 17 likely includes the 16 agent workflows plus one more. This needs verification against actual n8n instance.

12. **`FallbackMiddayBrief` Task Scheduler action uses a different path format** than the other two fallback tasks. It works but is inconsistent and fragile.

13. **`supabase_memory.py` references `agent_id` column** for "per-agent isolation." This is a conceptual leftover from the 16-agent model. The code works fine with a single agent, but the design intent described in the docstring is obsolete.

### Minor Issues

14. **Uncommitted deletions.** 7+ deleted files in git working tree haven't been committed. These should be committed to keep git clean.

15. **`_archive/skill_proposer.py`** references all agent names. This is correctly in `_archive/` so it's fine, but confirms archive is the right place for it.

16. **FF SOP version history** (`sop-monday-qbo-estimate-sync.md`) names agents as contributors. This is historical and arguably correct (those agents did "write" those versions), but it's confusing in a single-agent world.

17. **No `.lifecycle-reviews/` directory** found in workspace root. The CronCreate job for lifecycle review polling checks this directory every 7 minutes but it may not exist. (Could be created on demand.)

18. **README.md references `../4.- Sentinel/`** as a relative path. This assumes a specific directory layout that may not hold on all machines.

---

## Summary Scorecard

| Area | Health | Key Issue |
|------|--------|-----------|
| **Identity** | YELLOW | CLAUDE.md is correct; 4 workflows + 1 KB doc still describe 16-agent model |
| **Active Tools** | GREEN | All tools functional and current |
| **Brief System** | YELLOW | Works but CronCreate "primary" framing is misleading; fallbacks do the real work |
| **Error Auto-Fix** | GREEN | Working, tested, no issues |
| **Supabase Usage** | GREEN | Consistent workspace naming, correct table usage |
| **Task Scheduler** | RED | MEMORY.md claims 6 active + 9 disabled; reality is 3 active, rest gone |
| **n8n Workflows** | RED | 16 agent workflow IDs cached; unknown how many still exist in n8n |
| **Cross-Workspace** | YELLOW | Routing rules clear but workspace 3 is a mystery |
| **Doc Currency** | RED | 4 workflows + governance framework describe dead architecture |
| **Naming** | YELLOW | Agent names in 6+ document frontmatter fields |
