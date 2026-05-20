# Autonomous Systems -- Human-Readable Index

> **Status:** SUPERSEDED AS SOURCE OF TRUTH -- live registry is the Supabase `assets` table. This doc remains as a human-readable narrative index. For queryable / programmatic access, use `register-asset.py list` or query `assets` directly.
>
> **Live registry:** Supabase table `assets` -- owner: Sentinel (schema gatekeeper). As of 2026-04-22: 358 rows across 7 asset types (automation, hook, plugin, report, script, table, workflow).
> **Register an asset:** `python ~/.claude/scripts/register-asset.py register <type> <name> --workspace <ws> --purpose <...> --location <...>`
> **List assets:** `python ~/.claude/scripts/register-asset.py list [--type TYPE] [--workspace WS] [--active-only]`
> **Check drift:** `python <Skill Hub>/tools/audit-autonomous-systems.py`
>
> **Old snapshot date:** 2026-04-15 (pre-registry era). This doc is no longer maintained as source of truth; treat as narrative context. For current state, query the registry.
> **Per-system specs:** Each system has an authoritative spec in its owning workspace's `docs/specs/` directory. Specs describe DESIGN; registry rows describe CURRENT STATE.
> **Spec Template:** `3.- Skill Management Hub/docs/specs/SPEC-TEMPLATE.md`

## Ownership Map

| System | Owner Workspace | Spec |
|--------|----------------|------|
| CEO Daily Briefs (n8n) | HQ | `HQ/docs/specs/spec-ceo-briefs.md` |
| Work Request Pipeline (watcher + processing) | Skill Hub | `Skill Hub/docs/specs/spec-work-request-pipeline.md` |
| ~~Gap Inbox Alert~~ | Skill Hub | DECOMMISSIONED — folded into Sentinel evening report. Archive: `Skill Hub/docs/specs/archive/spec-gap-inbox-alert.md` |
| Error Auto-Fix Bridge | HQ | `HQ/docs/specs/spec-error-autofix.md` |
| Document Lifecycle Dispatch | Sentinel | `Sentinel/docs/specs/spec-doc-lifecycle.md` |
| Sentinel Morning Report | Sentinel | `Sentinel/docs/specs/spec-morning-report.md` |
| Sentinel Evening Report | Sentinel | `Sentinel/docs/specs/spec-evening-report.md` |
| Sentinel Dream Consolidation | Sentinel | `Sentinel/docs/specs/spec-dream-consolidation.md` |
| Sentinel Repo Monitor | Sentinel | `Sentinel/docs/specs/spec-repo-monitor.md` |
| Orphan Claude Process Cleanup | Sentinel | (no spec yet; added 2026-04-21, see section 5d) |
| Session Startup Guard | Global (~/.claude/hooks/) | `Skill Hub/docs/specs/spec-session-startup-guard.md` |
| n8n Watcher's Watcher | Sentinel | `Sentinel/docs/specs/spec-watchers-watcher.md` |
| n8n Internal Error Handler | HQ | `HQ/docs/specs/spec-error-handler.md` |
| Work Request Reporter | Global (~/.claude/scripts/) | `Skill Hub/docs/specs/spec-work-request-reporter.md` |
| Sync Skills | Skill Hub | `Skill Hub/docs/specs/spec-sync-skills.md` |
| Manifest Refresh | Skill Hub | `Skill Hub/docs/specs/spec-manifest-refresh.md` |

---

## 1. CEO Daily Briefs (n8n Cloud)

**What it is:** A three-tier cascade system delivering CEO daily briefings via Telegram at three scheduled times.

**Primary Workflow ID:** `VLj4WK3uQSpGpuAZ` (n8n cloud — fires at 6:00 AM, 12:00 PM, 9:00 PM CT)
**Secondary Workflow ID:** `xwgKEG6vfJsx43UR` (n8n cloud — fires at 6:15 AM, 12:15 PM, 9:15 PM CT if Primary missed)
**Tertiary:** Windows Task Scheduler (fires at 6:30 AM, 12:30 PM, 9:30 PM CT if both n8n workflows missed)
**Runs on:** n8n cloud (sharkitect-solutions.app.n8n.cloud) + local Task Scheduler fallback.
**Authoritative spec:** `HQ/docs/specs/spec-ceo-briefs.md` (v2.0, three-tier cascade)

**How it works:**
- A Cron trigger node fires at each scheduled time
- The workflow has 14 nodes that aggregate data from connected sources (calendar, tasks, etc.)
- It formats the data into a structured briefing
- Delivers the final brief via Telegram message to your chat

**What it reports:** A structured CEO daily brief -- priorities, calendar, key metrics, and action items for the relevant part of your day (morning/midday/evening).

**Status:** ACTIVE and running.

---

## 2. Gap Inbox Alert (Windows Task Scheduler)

**Task Name:** `AutonomousOps\GapInboxAlert` (scripts migrated to Skill Hub 2026-04-09)
**Runs on:** Local machine via Windows Task Scheduler
**Schedule:** Every 30 minutes (when machine is on)
**Owner:** Skill Hub
**Last Run:** 2026-04-09 05:46 AM (exit code 0 -- success)

**How it works:**
1. Task Scheduler calls `tools/sched-gap-alert.bat`
2. The .bat file runs `tools/gap-inbox-alert.py` with the full Python 3.12 path
3. The Python script checks `C:\Users\Sharkitect Digital\Documents\Claude Code Workspaces\3.- Skill Management Hub\.gap-reports\inbox\` for `.json` files
4. If files exist, it builds an alert message with severity levels and gap descriptions (up to 5 shown)
5. Sends a Telegram message via bot (using `TELEGRAM_HQ_BOT_TOKEN` and `TELEGRAM_MY_USER_ID` from `.env`)
6. If inbox is empty, it silently logs "no alert needed" and exits
7. Output logged to `.tmp/gap-alert.log`

**What it reports:** Telegram alerts when any workspace reports a gap (missing skill, broken hook, dead infrastructure). Message includes severity, workspace source, and gap description. Tells you to open a Skill Hub session to process them.

**Status:** ACTIVE. Ready state. Running on schedule.

---

## 3. Error Auto-Fix Bridge (cloudflared + FastAPI)

**Location:** `1.- SHARKITECT DIGITAL WORKFORCE HQ\tools\error-autofix\`
**Runs on:** Local machine as a persistent process
**Components:** cloudflared tunnel + FastAPI (uvicorn) on port 8765

**How it works:**
1. A cloudflared tunnel exposes a local FastAPI server to the internet
2. n8n's error handler workflows (see #7 below) POST error payloads to this tunnel when a workflow fails
3. The FastAPI server receives the `ErrorPayload` (execution_id, workflow_id, workflow_name, failed_node, error_message, error_type, etc.)
4. A `SafetyController` applies rate limiting, deduplication via error hashing, and concurrency control (semaphore)
5. If safety checks pass, it spawns Claude Code CLI (Sonnet) with a constructed prompt containing the error context
6. Claude analyzes the error and attempts a fix
7. Results are logged to Supabase and Airtable
8. A history deque (last 20 fixes) is maintained for the health endpoint

**What it reports:** Fix results -- whether Claude successfully diagnosed and fixed the error, or if it escalated. Logs to Supabase + Airtable for tracking.

**Status:** RUNNING (requires machine on and processes active).

---

## 4. Document Lifecycle Dispatch (Windows Task Scheduler)

**Task Name:** `Claude-DocLifecycle-DailyCheck`
**Runs on:** Local machine via Windows Task Scheduler
**Schedule:** Daily at 8:00 AM
**Last Run:** 2026-04-08 08:00 AM (exit code 0 -- success)

**How it works:**
1. Task Scheduler calls `daily-freshness-check.vbs` (VBScript wrapper, runs silently)
2. VBS calls `daily-freshness-check.bat`
3. The .bat changes directory to the Sentinel workspace and runs two Python scripts:
   - `tools/freshness-auditor.py check --alert` -- scans tracked documents for staleness based on review cadences
   - `tools/dispatch-lifecycle-reviews.py dispatch` -- creates review tickets (.json) in `.lifecycle-reviews/inbox/` for documents due for review

**What it reports:** Detects stale documents across all workspaces and dispatches review requests into the lifecycle inbox. These are picked up by the Session Startup Guard (#6) or during Skill Hub sessions.

**Status:** ACTIVE. Ready state. Running daily.

---

## 5. Sentinel Tasks (Windows Task Scheduler -- 3 tasks)

### 5a. Morning System Report

**Task Name:** `Sentinel\MorningReport`
**Schedule:** Daily at 5:45 AM
**Last Run:** 2026-04-09 05:45 AM (exit code 0)

**How it works:** Runs `sched-system-report.bat` which calls `scheduled-runner.py system-report` with `brief-generator.py morning`. Pure deterministic Python -- pulls data from Supabase (automation health, system status), formats it, sends a morning system health report via Telegram.

**What it reports:** Morning briefing on system health -- which automations are running, which failed overnight, any anomalies detected.

### 5b. Dream Consolidation

**Task Name:** `Sentinel\DreamConsolidation`
**Schedule:** Daily at 3:00 AM
**Last Run:** 2026-04-09 03:00 AM (exit code 0)

**How it works:** Runs `sched-dream.bat` which calls `scheduled-runner.py dream-consolidation` with `run-dream-cli.py`. Two-stage process:
- **Stage 1 (deterministic):** Python collects all the day's session learnings, gap reports, decisions, and memory updates across all workspaces
- **Stage 2 (AI):** Spawns Claude CLI (Sonnet) to synthesize collected data into consolidated insights, patterns, and recommendations

**What it reports:** A nightly "dream" -- synthesized intelligence about what happened across all workspaces that day, patterns emerging, and suggestions for system improvement.

### 5c. Repo Monitor

**Task Name:** `Sentinel\RepoMonitor`
**Schedule:** Weekly, Sunday at 8:00 PM
**Last Run:** Never (first scheduled run: 2026-04-12)

**How it works:** Runs `sched-repo-monitor.bat` which calls `scheduled-runner.py repo-monitor` with `repo-monitor.py scan`. Checks all GitHub forked repositories for upstream changes. If a fork is behind, it auto-syncs.

**What it reports:** Which repos are up-to-date, which were behind and synced, any sync failures.

### 5d. Orphan Claude Process Cleanup

**Task Name:** `Claude-Orphan-Cleanup-Hourly`
**Schedule:** Hourly at minute :47
**Created:** 2026-04-21 (ownership assigned to Sentinel via routed task)
**Last Run:** (pending first fire)

**How it works:** Runs `run-orphan-cleanup.bat` which calls `kill-orphan-claude-processes.py --execute --force --quiet --threshold-hours 4`. The script detects claude.exe processes older than 4 hours (safe threshold well above normal session durations), excludes the current session PID, and uses `taskkill /F` to terminate. Kills the parent process first, which cascades and takes down any child claude.exe processes spawned by CronCreate fires that never cleaned up.

**Why this exists:** CronCreate fires spawn new claude.exe processes to check inboxes. When those sessions exit cleanly, the process goes away. When they crash, get orphaned by Claude Code's lifecycle, or lose their session somehow, they linger indefinitely. By the end of a day of cron polling across 3 workspaces, 10+ orphans can accumulate, consuming 500MB-2GB of memory. The initial trigger was 11 orphans holding ~1.2GB on 2026-04-21.

**Safety:** `--force` is safe in Task Scheduler context because there is no active session to protect when the task runs. `--threshold-hours 4` prevents killing legitimately-long interactive sessions. `--quiet` suppresses output (taskscheduler has nowhere to display it). Script logs every kill to `~/.claude/.tmp/orphan-kill-log.jsonl` for audit.

**Wrapper:** `C:\Users\Sharkitect Digital\.claude\scripts\run-orphan-cleanup.bat` (matches pattern of other Sentinel Task Scheduler .bat wrappers).

**Status:** ACTIVE/Ready.

---

## 6. Session Startup Guard (Claude Code Hook)

**Location:** `~/.claude/hooks/session-startup-guard.py`
**Runs on:** Automatically on every Claude Code session start (registered in `settings.json`)
**Timeout:** 15 seconds

**How it works:**
1. Fires on every `SessionStart` event in any workspace
2. Implements a **3-state heartbeat** system:
   - **No heartbeat file** --> FULL STARTUP (run everything)
   - **Heartbeat exists, same day** --> VERIFY ONLY (quick health check)
   - **Heartbeat exists, old date** --> FULL STARTUP (new day)
3. Checks 4 systems:
   - **Work Requests** -- scans `.work-requests/inbox/` for pending `.json` reports (Skill Hub only)
   - **Lifecycle Inbox** -- scans `.lifecycle-reviews/inbox/` for pending review requests
   - **Skills Manifest** -- checks `.tmp/skills-manifest.json` freshness (stale if >24h)
   - **Cron Polling** -- checks if CronCreate jobs are configured
4. Outputs structured instructions as `additionalContext` for the AI to follow
5. Writes heartbeat file to `.tmp/session-heartbeat.json`

**What it reports:** A status table shown at session start with 6 steps (Heartbeat, Gap Inbox, Lifecycle Inbox, Manifest, Cron Polling, Final Status). If any inboxes have pending items, it instructs the AI to process them autonomously before showing results.

**Status:** WORKING. Non-blocking (always exits 0, never prevents session start).

---

## 7. n8n Support Workflows (n8n Cloud)

### 7a. Watcher's Watcher

**Workflow ID:** `N84M4ormvCzjlzTT`
**Runs on:** n8n cloud

**What it does:** Monitors the CEO Daily Brief workflow (#1) and other critical n8n workflows. If a scheduled workflow fails to execute or errors out, this workflow detects the gap and sends an alert. It's the failsafe that watches the watchers.

### 7b. Internal Error Handler

**Workflow ID:** `3AVNR5ZAfuelDz5d`
**Runs on:** n8n cloud

**What it does:** Catches errors from any n8n workflow that has error handling configured. When a workflow fails, this handler:
- Captures the error payload (execution ID, workflow name, failed node, error message)
- Routes it to the Error Auto-Fix Bridge (#3) via the cloudflared tunnel
- If the bridge is unreachable, falls back to a Telegram notification

**Status:** Both ACTIVE on n8n cloud.

---

## 8. Work Request Reporter (Global Script)

**Location:** `~/.claude/scripts/work-request.py`
**Runs on:** Called by any workspace's AI agent when it detects an issue needing Skill Hub action

**How it works:**
1. Any workspace agent calls this script with parameters (type, severity, workspace, description, fix recommendation)
2. The script writes a `.json` file into the Skill Management Hub's `.work-requests/inbox/`
3. The Session Startup Guard (#6) detects it on the next session start
4. CronCreate hourly poll detects it mid-session

**What it reports:** It doesn't report to you directly -- it's the intake mechanism that feeds systems #6 and CronCreate. Each request includes: type (MISSING/UNUSED/FALLBACK/TASK/BUG/ENHANCE), severity, source workspace, what was needed, what's missing, impact, and recommended fix.

**Status:** WORKING. Stdlib-only Python, no external dependencies. Replaced former gap-reporter.py (2026-04-14).

---

## System Interaction Map

```
n8n Cloud (24/7)
  |-- CEO Daily Briefs --> Telegram (you)
  |-- Watcher's Watcher --> monitors CEO Briefs
  +-- Internal Error Handler --> Error Auto-Fix Bridge (local)
                                    +-- Claude CLI fix --> Supabase + Airtable

Task Scheduler (when PC on)
  |-- Gap Inbox Alert (30 min) --> Telegram (you)
  |-- Doc Lifecycle (daily 8AM) --> .lifecycle-reviews/inbox/
  |-- Sentinel Morning Report (5:45 AM) --> Telegram (you)
  |-- Dream Consolidation (3:00 AM) --> Supabase brain
  +-- Repo Monitor (Sun 8 PM) --> GitHub sync

Session Hook (every Claude session)
  +-- Startup Guard --> reads inboxes --> instructs AI to process

Cross-Workspace Script
  +-- Gap Reporter --> writes to Skill Hub inbox --> feeds #2 and #6
```

---

## Deleted Systems (Phase 1 Cleanup, 2026-04-09)

7 stale Task Scheduler tasks were removed:
- `SharkitectMorningBrief`, `EveningBrief`, `WeeklyAudit`, `MidnightAudit`, `TriggerMorning`, `TriggerMidday`, `TriggerEvening`
- Reason: From earlier approaches that no longer functioned.

3 RemoteTrigger configs were disabled:
- Reason: MCP cold-start failure (MCP tools aren't registered when RemoteTrigger fires at session init).

3 Fallback Brief tasks (`FallbackMorningBrief`, `FallbackMiddayBrief`, `FallbackEveningBrief`):
- Created as backup for CEO briefs but no longer present in Task Scheduler. n8n cloud workflow is the primary delivery mechanism.

---

## Known Risks and Caveats

1. **Error Auto-Fix Bridge (#3)** requires the local machine to be running with both cloudflared and the FastAPI server active. If the machine sleeps or reboots, it stops working until manually restarted.
2. **All Task Scheduler jobs (#2, #4, #5)** only run when the PC is on and the user is logged in ("Interactive only" mode). They do NOT run during sleep/shutdown.
3. **RepoMonitor (#5c)** has never successfully executed yet. First run scheduled for 2026-04-12.
4. **Dream Consolidation (#5b)** Stage 2 requires Claude CLI to be available -- if the CLI auth token expires or the CLI is unavailable, Stage 2 will fail (Stage 1 still runs).
5. **RemoteTrigger is broken** for any MCP-dependent task due to cold-start race condition. Do not use.
6. **CronCreate jobs** die on session close. They are recreated each session by the Startup Guard but only exist during active Claude Code sessions.
