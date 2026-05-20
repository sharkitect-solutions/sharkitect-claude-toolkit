# Infrastructure Audit Report — Phases 1C + 1D + 1E

**Date:** 2026-04-09
**Auditor:** Sentinel
**Part of:** Foundation Reset master plan (wise-sprouting-canyon.md)

---

## Phase 1C: Windows Task Scheduler Audit

### Active Custom Tasks

| # | Task Name | Schedule | Action Path | Last Run | Result | .bat? | Paths Valid? | Owner | Status |
|---|-----------|----------|-------------|----------|--------|-------|-------------|-------|--------|
| 1 | `\Claude-DocLifecycle-DailyCheck` | Daily 8:00 AM | VBS → .bat → freshness-auditor.py + dispatch-lifecycle-reviews.py | 4/9 8:00 AM | 0 (OK) | YES | YES | Sentinel | HEALTHY |
| 2 | `\AutonomousOps\GapInboxAlert` | Every 30 min | sched-gap-alert.bat → gap-inbox-alert.py | 4/9 11:46 AM | 0 (OK) | YES | YES | Skill Hub | HEALTHY |
| 3 | `\Sentinel\DreamConsolidation` | Daily 3:00 AM | sched-dream.bat → run-dream-cli.py | 4/9 3:00 AM | 0 (OK) | YES | YES | Sentinel | HEALTHY |
| 4 | `\Sentinel\MorningReport` | Daily 5:45 AM | sched-system-report.bat → brief-generator.py | 4/9 5:45 AM | 0 (OK) | YES | YES | Sentinel | HEALTHY |
| 5 | `\Sentinel\RepoMonitor` | Weekly Sun 8 PM | sched-repo-monitor.bat → repo-monitor.py | Never | 267011 | YES | YES | Sentinel | WARNING (first run 4/12) |
| 6 | `\SharkitectHQ\FallbackMorningBrief` | Daily 6:15 AM | fallback-morning-brief.bat → fallback-brief-sender.py | 4/9 6:15 AM | -2147024894 | YES | YES | HQ | **BROKEN** (0x80070002) |
| 7 | `\SharkitectHQ\FallbackMiddayBrief` | Daily 12:15 PM | fallback-midday-brief.bat → fallback-brief-sender.py | 4/8 12:15 PM | 0 (OK) | YES | YES | HQ | HEALTHY (odd .tmp\..\ path) |
| 8 | `\SharkitectHQ\FallbackEveningBrief` | Daily 9:15 PM | fallback-evening-brief.bat → fallback-brief-sender.py | 4/8 9:15 PM | -2147024894 | YES | YES | HQ | **BROKEN** (0x80070002) |

### Dead/Orphaned Tasks (from dissolved workspaces)

| Task Name | Points To | Status | Action |
|-----------|-----------|--------|--------|
| `\Lead Gen - Daily Pipeline` | Dissolved "Agentic Lead Gen Agent" workspace | DISABLED, no files on disk | **DELETE** |
| `\SCOUTDailyPipeline` | Dissolved "SCOUT - Lead Gen Agent" workspace | DISABLED, no files on disk | **DELETE** |
| `\SCOUTPipeline` | Dissolved "SCOUT" workspace (duplicate) | DISABLED, no files on disk | **DELETE** |
| `\SCOUTWeekendSendOnly` | Dissolved "SCOUT" workspace | DISABLED, no files on disk | **DELETE** |

### Previously Deleted Tasks — Verification

All 10 tasks confirmed **DELETED** from Task Scheduler:
SharkitectMorningBrief, EveningBrief, WeeklyAudit, MidnightAudit, TriggerMorning, TriggerMidday, TriggerEvening, FallbackMorningBrief (root), FallbackMiddayBrief (root), FallbackEveningBrief (root).

### Summary

| Metric | Count |
|--------|-------|
| Total custom tasks | 12 |
| Healthy | 5 |
| Broken (error codes) | 2 |
| Not yet run | 1 |
| Dead/orphaned | 4 |
| Previously deleted confirmed gone | 10/10 |

### Action Items

1. **DELETE** 4 orphaned tasks (Lead Gen, SCOUT x3) — point to dissolved workspaces
2. **INVESTIGATE** FallbackMorningBrief and FallbackEveningBrief — .bat/.py exist but runtime returns 0x80070002 (likely unquoted path or missing dependency; FallbackMidday succeeds using quoted path with `.tmp\..\` detour)
3. **FIX** FallbackMiddayBrief action path — remove `.tmp\..\` detour (fragile)
4. **VERIFY** RepoMonitor after first run (Sunday 4/12)

---

## Phase 1D: n8n Workflow Audit

### Instance Overview

| Metric | Count |
|--------|-------|
| Total workflows | 85 |
| Active | 7 |
| Inactive | 78 |
| Known (in inventory) | 3 |
| Unknown (not in inventory) | 82 |

### Known Workflows (in autonomous-systems-inventory.md)

| Name | ID | Active | Trigger | Last Exec | Status | Error WF? | Owner |
|------|-----|--------|---------|-----------|--------|-----------|-------|
| CEO Daily Briefs | xwgKEG6vfJsx43UR | YES | Cron (6AM/12PM/9PM) | 4/9 5:00 PM | Success | YES → Internal Error Handler | HQ |
| Watcher's Watcher | N84M4ormvCzjlzTT | YES | Cron (every 12h) | 4/9 2:00 PM | Success | YES → Internal Error Handler | Sentinel |
| Internal Error Handler | 3AVNR5ZAfuelDz5d | YES | Error Trigger | 4/8 3:45 AM | Success | N/A (IS the handler) | HQ |

### Active But Unknown Workflows

| Name | ID | Trigger | Error WF? | Owner |
|------|-----|---------|-----------|-------|
| [FF] Global Error Handler | oQDSXQdTyQgEFIyVMIwFx | Error Trigger | N/A (IS handler) | Client (FF) |
| [FF] CALCULATE v2 | JUTq8y5sn15J97Ph | Webhook | YES | Client (FF) |
| [FF] ESTIMATE v2 | CwjHNWh686qpF5g2 | Webhook | YES | Client (FF) |
| Speed-to-Lead Demo | e0lUI3Wdn9JdxEx2 | Webhook | **NO** | Demo |

### Inactive Workflow Categories (78 total)

| Category | Count | Description | Action |
|----------|-------|-------------|--------|
| WORKFORCE Agent Fleet | 16 | Dissolved 16-agent system (Alex, Marcus, Sage, etc.) | **ARCHIVE/DELETE** |
| [ALEX] Sub-Agent Suite | 9 | Prior Alex assistant architecture | **ARCHIVE/DELETE** |
| FF Testing/Archive | ~15 | Duplicate/versioned FF workflows | **ARCHIVE** |
| Other demos/tests | ~38 | Various inactive experiments | **REVIEW & ARCHIVE** |

### Credential Issues — CRITICAL

**This is the most severe finding across all audits.**

| Credential Type | Instances | Workflows Affected | Severity |
|----------------|-----------|-------------------|----------|
| Supabase service_role JWT | ~50+ | CEO Briefs (32), Watcher's Watcher (4), FF Error Handler (1), all 16 WORKFORCE agents (48), Atlas Clone (3) | **CRITICAL** |
| Telegram bot token | 4 | CEO Briefs (2), Watcher's Watcher (2) | **CRITICAL** |
| Slack bot token | 6+ | Email Response Scanner, Email Response Approval Listener | **CRITICAL** |
| Webhook secret | 1 | Internal Error Handler (`sharkitect-autofix-2026`) | **HIGH** |
| Anthropic API key | 1 | FF Global Error Handler | **CRITICAL** |

**Total: ~63+ critical hardcoded credential instances.**

All credentials should be migrated to n8n's credential store immediately. The Supabase service_role key is the highest priority — it's exposed in 20+ workflows and grants full database access.

### Error Handling Gaps

| Issue | Count | Details |
|-------|-------|---------|
| Active workflows without error handler | 1 | Speed-to-Lead Demo |
| Inactive workflows without error handler | ~75 | All WORKFORCE agents, most FF test copies, demos |
| Error handler referencing inactive handler | 2 | Email Response workflows → AIOS Error Handler (inactive) |

### Dead Infrastructure

| Item | Issue | Action |
|------|-------|--------|
| Internal Error Handler bridge URL | Uses ephemeral Cloudflare tunnel URL (dead) | **FIX** — update to current tunnel URL |
| AIOS Error Handler (u1LBkfbBCuJDEpep) | Inactive, but still referenced by 2 workflows | **DELETE** or activate |
| [ARCHIVED] CALCULATE v1 | Superseded by v2, webhook still registered | **ARCHIVE** properly |

### Action Items (Priority Order)

1. **CRITICAL: Rotate Supabase service_role key** after migrating all 50+ instances to n8n credential store
2. **CRITICAL: Move Telegram bot token** to n8n credentials (4 instances in 2 workflows)
3. **CRITICAL: Move Slack bot token** to n8n credentials (6+ instances in 2 workflows)
4. **CRITICAL: Move Anthropic API key** to n8n credentials (1 instance)
5. **HIGH: Fix Internal Error Handler bridge URL** (dead Cloudflare tunnel)
6. **HIGH: Add error workflow to Speed-to-Lead Demo** (active, no error handling)
7. **MEDIUM: Archive 60+ inactive workflows** (WORKFORCE fleet, ALEX suite, FF test copies)
8. **MEDIUM: Delete or activate AIOS Error Handler** (referenced but inactive)

---

## Phase 1E: Global Artifacts Audit

### 1. Rules (`~/.claude/rules/`) — 3 files

| File | Size | Governs | Status |
|------|------|---------|--------|
| `api-limitations.md` | 1.1 KB | API/MCP limitation workarounds | CLEAN |
| `context7.md` | 610 B | Context7 MCP usage enforcement | CLEAN |
| `universal-protocols.md` | 14.6 KB | Master cross-workspace protocols | CLEAN (1 LOW finding) |

**Findings:** No stale agent names, no contradictions between rules. Minor: `universal-protocols.md` indirectly references dissolved "master-aios-builder" via startup guard description (LOW).

### 2. Scripts (`~/.claude/scripts/`) — 2 files

| File | Purpose | Status |
|------|---------|--------|
| `doc-cache-builder.py` | Builds doc lifecycle cache for drift detection | CLEAN |
| `gap-reporter.py` | Universal gap reporting to Skill Hub inbox | CLEAN |

**Findings:** Both stdlib-only Python, valid paths, no stale references.

### 3. Hooks (`~/.claude/hooks/`) — 14 files

| File | Type | Purpose | Status |
|------|------|---------|--------|
| `check-line-count.py` | PreToolUse | MEMORY.md/CLAUDE.md line limit enforcement | CLEAN |
| `checkpoint-reminder.py` | PostToolUse | Reminds to update MEMORY.md after edits | CLEAN |
| `content-enforcer-hook.py` | PreToolUse | Content quality skill reminder (HQ) | CLEAN |
| `drift-detection-hook.py` | PreToolUse | Document drift detection on Write/Edit | CLEAN |
| `error-tracker-hook.py` | PostToolUse | Error tracking + known fix suggestions | CLEAN |
| `mcp-limitation-guard.py` | PreToolUse | Pre-checks MCP calls against known limitations | CLEAN |
| `pre-modify-checkpoint.py` | PreToolUse | Warns before modifying system files | CLEAN |
| `quality-gate-hook.py` | PostToolUse | Build-judge-optimize loop for skills/agents | CLEAN |
| `resource-audit-hook.py` | PostToolUse | Edit tracking + resource auditor nudges | CLEAN |
| `session-start-lifecycle.py` | SessionStart | Doc lifecycle data from Supabase | MEDIUM (refs dissolved workspace) |
| `session-startup-guard.py` | SessionStart | 3-state heartbeat, inbox checks | MEDIUM (refs dissolved workspace) |
| `daily-freshness-check.bat` | Task Scheduler | Freshness auditor + lifecycle dispatch | **HIGH** (bare `python`, misplaced) |
| `daily-freshness-check.vbs` | Task Scheduler | Silent VBS wrapper | MEDIUM (misplaced) |

**All 12 .py hooks are registered in `settings.json`.** No orphans, no missing registrations.

**Findings:**
- **HIGH:** `daily-freshness-check.bat` uses bare `python` instead of full path (per lessons-learned, Task Scheduler requires full path)
- **MEDIUM:** `.bat` and `.vbs` are Task Scheduler support files misplaced in hooks dir (should be in Sentinel `tools/`)
- **MEDIUM:** 2 hooks reference dissolved "master-aios-builder" workspace in detection logic

### 4. Plans (`~/.claude/plans/`) — 48 files, 778 KB

| Status | Count |
|--------|-------|
| Active (executing) | 1 (wise-sprouting-canyon.md — Foundation Reset) |
| Completed | ~35 |
| Historical/Reference | ~10 |
| Agent sub-plans | ~8 |

**Findings:**
- **HIGH:** 48 plan files / 778 KB never pruned. Only 1 is active. Directory needs archival.
- **MEDIUM:** Several completed plans reference dissolved agent hierarchy (16-agent model), Alex bot, etc.

### 5. Docs (`~/.claude/docs/`) — 2 files (+audit reports being added now)

| File | Purpose | Status |
|------|---------|--------|
| `autonomous-systems-inventory.md` | Authoritative system ownership map | CLEAN, current |
| `audit-sentinel.md` | Phase 1A self-audit | CLEAN, current |

### 6. Lessons-Learned (`~/.claude/lessons-learned.md`) — 501 lines, 44 KB

**Status:** Well-organized, 7 categories, dated entries with tags.

**Findings:**
- **MEDIUM:** Line 304 references deleted `ralph-scheduler.py` without noting deletion
- **LOW:** Line 363 title mentions dissolved "Autonomous Operations workspace" (body is correct)
- **LOW:** 501 lines / 44 KB approaching size where grep-based searching slows down

### 7. Cross-Workspace MEMORY.md Audit

| Workspace | Status | Critical Findings |
|-----------|--------|-------------------|
| **HQ** | STALE | **CRITICAL:** Claims deleted `ralph-scheduler.py` is part of active briefing system. **HIGH:** Lists 6 Task Scheduler tasks that may not exist. |
| **Skill Hub** | STALE | **HIGH:** Claims hooks `aios-core` and `phase-gate` are registered (not in settings.json). **MEDIUM:** Says CEO briefs "needs fixes" while HQ says "COMPLETE." |
| **Sentinel** | CLEAN | 7-line concise index, no stale claims. |

---

## Cross-Phase Findings Summary

### Severity Distribution

| Severity | 1C (Task Sched) | 1D (n8n) | 1E (Global) | Total |
|----------|-----------------|----------|-------------|-------|
| CRITICAL | 0 | 4 (credentials) | 1 (HQ MEMORY) | 5 |
| HIGH | 0 | 2 | 4 | 6 |
| MEDIUM | 2 | 2 | 8 | 12 |
| LOW | 1 | 1 | 8 | 10 |

### Themes

1. **Credential exposure is the #1 risk.** 63+ hardcoded credentials across n8n workflows, including the Supabase service_role key that grants full database access. This is a security emergency.

2. **Dissolved systems leave long tails.** The 16-agent WORKFORCE model was dissolved, but 16 n8n workflows, 4 Task Scheduler tasks, multiple MEMORY.md references, and plan files still reference it. Cleanup was incomplete.

3. **MEMORY.md drift is real.** HQ and Skill Hub MEMORY files make claims about systems that no longer exist or work differently than described. This actively misleads future sessions.

4. **n8n is 90% clutter.** Only 7 of 85 workflows are active. 78 inactive workflows (many with hardcoded credentials) add attack surface and confusion.

5. **Plans directory is a graveyard.** 47 of 48 plans are completed/historical. 778 KB of accumulated plan files that will never be referenced again.
