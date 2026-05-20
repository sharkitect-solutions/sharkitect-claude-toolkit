# Plan: Operational Foundation Lock — Sync, Briefs, and Procedures Audit

## Context

Chris identified a critical gap before Phase 1: **local memory (MEMORY.md, session-history, plan files) is the actual source of truth, but Supabase should be**. Changes made in Claude Code don't auto-push to Supabase, meaning the Telegram/n8n side sees stale data. Chris's vision: seamless cross-platform continuity — work in Claude Code, leave, continue on Telegram, come back, zero gaps.

Additionally, the current "daily brief" is a single 6 PM audit. Chris wants **morning + evening briefs** with distinct purposes, plus verification that all data is synced to Supabase before the day ends.

This plan addresses everything before Phase 1 begins:
1. Automatic Supabase sync (no manual re-seeding) — evening auto-push + scheduled every 2-3 hours + on-demand command
2. Morning brief (6 AM CT: plan the day) vs evening brief (9 PM CT: close the day)
3. Pending task tracking in briefs + synced to Supabase
4. Active project phase tracking in briefs
5. Supabase sync verification in evening brief
6. Expand seeder coverage: pending tasks, memory topic files, session history
7. Operational procedures audit (close all gaps)
8. Error resilience — scheduled tasks survive network/API failures (retry + fallback)
9. Error surfacing — broken checks become visible attention items (never invisible)
10. Session-start Supabase check — see what happened on other platforms since last Claude Code session
11. Structured error logging — foundation for Phase 2-3 autonomous error resolution (detect → log → future: auto-dispatch → troubleshoot → resolve or escalate)

---

## Step 1: Add Supabase Sync Check + Auto-Push

### File: `tools/audit/audit_checks.py` — 2 new functions

**`check_supabase_sync()`** — Detects if local files have changed since last sync:

```python
def check_supabase_sync() -> dict:
    """Compare local content hash against last-synced hash."""
    # 1. Parse MEMORY.md → rules, decisions, process fixes, env facts
    # 2. Parse 16 agent MEMORY.md files → agent memories
    # 3. Scan knowledge-base/*.md → KB docs
    # 4. Generate SHA256 hash of all concatenated content
    # 5. Compare against stored hash in .tmp/supabase-sync-hash.json
    # 6. Return: needs_sync (bool), local_hash, stored_hash,
    #    local_counts (rules, decisions, etc.), last_synced timestamp
```

How it works:
- Imports parsing functions directly from `tools/seed_supabase.py` (reuse existing logic)
- Generates a content hash from ALL parseable content (rules + decisions + process fixes + env + agent memories + KB doc paths + pending tasks + memory topic files)
- Compares against `.tmp/supabase-sync-hash.json` (stored after last successful sync)
- If hash differs → `needs_sync = True`

**`sync_to_supabase()`** — Executes the sync when needed:

```python
def sync_to_supabase() -> dict:
    """Re-run the seeder to push local changes to Supabase."""
    # 1. Import and call seed_memories() + seed_kb_docs() from seed_supabase.py
    # 2. Save new content hash to .tmp/supabase-sync-hash.json
    # 3. Return: stats (rules synced, decisions synced, etc.), elapsed time
```

How it works:
- Imports `seed_memories()`, `seed_kb_docs()`, `get_brain()`, `load_env()` from `tools/seed_supabase.py`
- Runs full re-seed (idempotent via upserts, ~$0.003 cost, ~30s duration)
- Updates `.tmp/supabase-sync-hash.json` with new hash + timestamp
- Returns detailed stats for the evening brief report

**Hash file** (`.tmp/supabase-sync-hash.json`):
```json
{
    "hash": "a1b2c3d4...",
    "last_synced": "2026-03-15T18:00:00",
    "stats": {"rules": 34, "decisions": 59, "agent_memories": 104, "kb_docs": 44}
}
```

### File: `tools/audit/config.py` — Add sync config

```python
SYNC_HASH_FILE = TMP_DIR / "supabase-sync-hash.json"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
```

---

## Step 1B: Expand Seeder Coverage

### File: `tools/seed_supabase.py` — 3 new parsers + expanded KB doc collection

The current seeder misses several important content areas. Adding:

**`parse_pending_tasks(text)`** — Parses `## Pending — Master List` into individual memory entries:
- Each task becomes a memory with category `task`
- Key: `task_{number}_{name_slug}`
- Content includes status marker (`[x]`/`[~]`/`[ ]`), task name, and detail
- Enables Telegram bot to answer "what's pending?" via semantic search

**`parse_rhythm_calendar(text)`** — Parses `## Operating Rhythm Calendar` table:
- Each cadence row becomes a memory with category `workflow`
- Key: `rhythm_{cadence}`
- Content: cadence name, last completed, next due, status

**Expand `seed_memories()` call** to include these two new parsers alongside existing ones.

**Expand `collect_kb_docs()`** (or add `collect_memory_topic_files()`):
- Scan `~/.claude/projects/.../memory/*.md` (excluding MEMORY.md itself)
- Currently 5 files NOT synced: `session-history.md`, `voice-ai-requirements.md`, `ff-report-generation.md`, `reference_hubspot_mcp_app.md`, `feedback_plan_mode_exit.md`
- Each stored as a KB doc with category `memory_topic`
- Session history stored as single doc (may be large — truncate to last 20 sessions if needed)

This closes the cross-platform gap: EVERYTHING in local memory becomes searchable in Supabase.

---

## Step 2: Add Pending Tasks Check

### File: `tools/audit/audit_checks.py` — New function

**`check_pending_tasks()`** — Parses the Pending Master List from MEMORY.md:

```python
def check_pending_tasks() -> dict:
    """Parse Pending Master List from project MEMORY.md."""
    # Returns:
    # {
    #     "status": "OK",
    #     "total": 11,
    #     "active": [{"id": 2, "name": "UNIFIED AI WORKFORCE", "detail": "Phase 0 COMPLETE..."}],
    #     "completed": [{"id": 3, "name": "FIX RLR MVP"}],
    #     "blocked": [{"id": 5, "name": "FIX ERA"}],
    #     "pending": [{"id": 1, "name": "AIOS READDRESS"}, ...],
    # }
```

How it works:
- Reads `PROJECT_MEMORY_FILE`
- Finds `## Pending — Master List` section
- Parses numbered items with `[x]`, `[~]`, `[ ]` markers
- Categorizes: `[x]` = completed, `[~]` = active/in-progress, `[ ]` = pending
- Extracts task name (bold text) and status detail

**Used in:**
- Morning brief: Shows active + pending tasks (what's on the plate today)
- Evening brief: Shows what changed since morning (any completions, new blockers)

---

## Step 3: Add Active Project Phase Check

### File: `tools/audit/audit_checks.py` — New function

**`check_active_projects()`** — Scans plan files for current phase/batch status:

```python
def check_active_projects() -> dict:
    """Scan knowledge-base/projects/*/plan.md for active project phases."""
    # Returns:
    # {
    #     "status": "OK",
    #     "projects": [
    #         {
    #             "name": "Unified AI Workforce",
    #             "plan_file": "knowledge-base/projects/unified-ai-workforce/plan.md",
    #             "current_phase": "Phase 1: Alex + Marcus + C-Suite in n8n",
    #             "status": "NEXT",
    #             "next_batch": "1-A: Build Think Tool sub-workflow",
    #         }
    #     ]
    # }
```

How it works:
- Scans `knowledge-base/projects/*/plan.md`
- For each plan file, parses phase headers and batch tables
- Identifies current phase (first non-COMPLETE phase)
- Identifies next batch (first non-COMPLETE batch in current phase)
- Returns structured summary

**Used in:**
- Morning brief: "Active project: Unified AI Workforce — Phase 1, next: Batch 1-A"
- Evening brief: Same, with any phase/batch updates noted

---

## Step 4: Add Today's Session Activity Check

### File: `tools/audit/audit_checks.py` — New function

**`check_today_activity()`** — Queries Supabase logs for today's activity:

```python
def check_today_activity() -> dict:
    """Query Supabase logs for today's interactions."""
    # Uses httpx to query: GET /rest/v1/logs?timestamp=gte.{today}T00:00:00
    # Returns:
    # {
    #     "status": "OK",
    #     "interaction_count": 12,
    #     "workflows_run": ["daily_audit", "seed_supabase"],
    #     "errors": 0,
    #     "platforms": {"telegram": 8, "claude_code": 3, "task_scheduler": 1},
    # }
```

How it works:
- Raw httpx GET to Supabase REST API (same pattern as `log_to_supabase()` in run_audit.py)
- Filters logs table by `timestamp >= today 00:00:00`
- Aggregates: total interactions, unique workflows, error count, platform breakdown
- Graceful skip if Supabase unreachable

**Used in:**
- Evening brief only: "Today's activity: 12 interactions across 2 platforms, 0 errors"

---

## Step 5: Split Daily Brief into Morning + Evening

### File: `tools/audit/daily_audit.py` — Add `run_morning_brief()` and `run_evening_brief()`

**Morning Brief** (`run_morning_brief()`):
```
Checks run:
  1. check_calendar()            → TODAY's events
  2. check_email()               → Unread summary
  3. check_pending_tasks()       → Active/pending tasks
  4. check_active_projects()     → Current project phase
  5. check_overnight_activity()  → Telegram interactions since last evening brief (CONDITIONAL: only shown if > 0)
```

**`check_overnight_activity()`** — Queries Supabase logs for interactions between last evening brief and now:
- Similar to `check_today_activity()` but filtered: `timestamp > last_evening_brief AND timestamp < now`
- Returns count + brief summary (workflow names, platforms)
- If zero interactions → returns `{"status": "QUIET"}` → section omitted from brief

**Evening Brief** (`run_evening_brief()`):
```
Checks run:
  1. check_calendar()          → TOMORROW's events (re-run with tomorrow filter)
  2. check_today_activity()    → What happened today (from Supabase logs)
  3. check_pending_tasks()     → Updated task status
  4. check_active_projects()   → Current phase (any updates?)
  5. check_department_capacity() → System health
  6. check_initiative_registry()
  7. check_governance_log()
  8. check_rhythm_calendar()
  9. check_incoming_files()
  10. check_tmp_files()
  11. check_supabase_sync()    → Sync status
  12. sync_to_supabase()       → Auto-push if needed
  13. Attention items          → Merged from all checks
```

**Calendar logic change for evening:**
- Morning brief: `check_calendar()` as-is (shows today + tomorrow)
- Evening brief: Modify to show TOMORROW only (today is over)
- Add optional `tomorrow_only=True` parameter to `check_calendar()`

**Backwards compatibility:**
- `run_daily_audit()` still exists, calls `run_evening_brief()` (alias)

---

## Step 6: Update Report Formatter

### File: `tools/audit/report_formatter.py` — Add `format_morning()`, update `format_daily()` → `format_evening()`

**Morning Brief Format:**
```
<b>☀️ MORNING BRIEF — 2026-03-16</b>

<b>TODAY'S CALENDAR</b>
  3 events
  • 10:00 AM — Meeting with FF (Google Meet)
  • 2:00 PM — Strategy session
  • 4:00 PM — Follow-up call

<b>EMAIL</b>
  Unread: 8 (2 important)
  • John @ Fantastic Floors — "Re: PayLink timeline" [!]
  • Twilio Support — "Monthly usage report"

<b>OVERNIGHT</b>                          ← Only shown if > 0 interactions
  2 Telegram interactions since 9 PM
  • Memory query: "pricing for CPS"
  • Calendar check: tomorrow's schedule

<b>ACTIVE TASKS</b>
  [~] Unified AI Workforce — Phase 0 COMPLETE, Phase 1 NEXT
  [ ] AIOS Readdress — Follow up on team assessment
  [ ] TMC Data Analyst MVP — Needs planning

<b>ACTIVE PROJECT</b>
  Unified AI Workforce — Phase 1, Next: Batch 1-A (Think Tool sub-workflow)
```

**Evening Brief Format:**
```
<b>EVENING BRIEF — 2026-03-16</b>
Status: ALL_CLEAR

<b>TOMORROW'S CALENDAR</b>
  1 event
  • 9:00 AM — Weekly standup

<b>TODAY'S ACTIVITY</b>
  12 interactions | Platforms: Telegram (8), Claude Code (3), Scheduler (1)
  Errors: 0

<b>TASKS</b>
  Active: 1 | Pending: 8 | Completed: 2 | Blocked: 1
  Blocked: FIX ERA

<b>ACTIVE PROJECT</b>
  Unified AI Workforce — Phase 1, Next: Batch 1-A

<b>SYSTEM HEALTH</b>
  <b>Capacity</b>: Elevated: Technology | Idle: Strategy, Legal, Knowledge
  <b>Initiatives</b>: 8 tracked, 4 active, 1 blocked
  <b>Governance</b>: EMPTY
  <b>Rhythm</b>: All cadences on track
  <b>Files</b>: Incoming: 0 | Tmp: 6 (2 stale)

<b>SUPABASE SYNC</b>
  Status: SYNCED
  Last sync: 2026-03-16 21:00 | Records: 280+ (230+ memories + 49 KB docs)
  -- OR --
  Status: SYNCED (auto-pushed 3 new rules, 2 updated decisions)

<b>ATTENTION (2 items)</b>
  • Blocked initiative: ERA
  • Governance Log is EMPTY
```

**Weekly Format:** Keep as-is (already includes Sage/Atlas/Sterling/Marcus). Add skills inventory to weekly only (remove from daily — too noisy for daily use).

---

## Step 7: Update Entry Point

### File: `tools/run_audit.py` — Support morning/evening/weekly/sync

```python
# Usage:
#   python run_audit.py morning              (morning brief → Telegram)
#   python run_audit.py evening              (evening brief → Telegram)
#   python run_audit.py weekly               (weekly report → Telegram)
#   python run_audit.py sync                 (on-demand Supabase sync, no brief, no Telegram)
#   python run_audit.py morning --no-telegram (local test)
#   python run_audit.py daily                (alias for evening, backwards compat)
```

Changes:
- Add `morning` mode → calls `run_morning_brief()` + `format_morning()`
- Rename `daily` handling → calls `run_evening_brief()` + `format_evening()`
- Add `sync` mode → calls `check_supabase_sync()` + `sync_to_supabase()` only (no brief, no Telegram, prints stats to console). ~30 seconds. Use before switching from Claude Code to Telegram.
- Keep `daily` as alias for `evening` (backwards compatibility)
- `weekly` stays the same

---

## Step 8: Update Windows Task Scheduler

Four scheduled tasks:
1. **SharkitectMorningBrief** — 6:00 AM CT daily → `python tools/run_audit.py morning`
2. **SharkitectEveningBrief** — 9:00 PM CT daily → `python tools/run_audit.py evening`
3. **SharkitectSupabaseSync** — Every 3 hours (9 AM, 12 PM, 3 PM, 6 PM) → `python tools/run_audit.py sync` (silent background sync, no Telegram, no brief — just ensures Supabase stays current throughout the day)
4. **SharkitectWeeklyAudit** — Sunday 9:00 PM CT → `python tools/run_audit.py weekly` (unchanged)

Delete or rename existing `SharkitectDailyAudit` (replaced by evening).

On-demand sync also available: `python tools/run_audit.py sync` — run manually before switching to Telegram for immediate sync.

---

## Step 9: Codify Operational Procedures

### Update MEMORY.md — New Active Rules:

1. **SUPABASE AUTO-SYNC** — Three-tier sync strategy: (a) Scheduled every 3 hours via Task Scheduler (silent, no Telegram), (b) Evening brief at 9 PM verifies + auto-pushes + confirms via Telegram, (c) On-demand `python tools/run_audit.py sync` before switching platforms. Manual fallback: `python tools/seed_supabase.py`.

2. **MORNING/EVENING BRIEF SPLIT** — Two briefs per day via Telegram. Morning (6 AM CT): calendar today, email, active tasks, project phase, overnight activity (if any). Evening (9 PM CT): calendar tomorrow, today's activity, task status, system health, Supabase sync verification. Weekly stays Sunday 9 PM.

3. **SYNC VERIFICATION MANDATORY** — Every evening brief verifies Supabase has all current local data. Auto-pushes if not. Chris should NEVER find stale data on Telegram that was updated in Claude Code. Scheduled syncs every 3 hours provide continuous coverage.

4. **FULL SUPABASE COVERAGE** — Everything in local files is synced to Supabase: active rules, decisions, process improvements, environment facts, agent memories, KB docs, pending tasks, operating rhythm calendar, memory topic files (voice AI reqs, FF report learnings, session history, etc.). If it exists locally, it exists in Supabase.

5. **ERROR RESILIENCE MANDATORY** — All scheduled tasks (briefs, syncs, audits) must survive network/API failures without crashing. Telegram sends retry 2x with 3s backoff. On final failure: save to `.tmp/unsent-brief-*.txt` + SMTP fallback. Individual check errors don't kill the whole audit — they surface as attention items.

6. **STRUCTURED ERROR LOGGING** — Every detected error is logged to Supabase `logs` table with `workflow_name: "error_event"`, severity, resolution_status, and a resolution_log array. This is the foundation for Phase 2 autonomous error resolution (Marcus auto-dispatches agents to troubleshoot, agents log each attempt, resolve or escalate to Chris).

7. **SESSION-START CROSS-PLATFORM CHECK** — At Claude Code session start (alongside Operating Rhythm Calendar check), query Supabase for recent interactions on other platforms (Telegram, Task Scheduler). Closes the "what happened while I was away?" gap.

### Update `workflows/operating-rhythm.md`:

Add Morning/Evening Brief section under Daily Cadence:
- Morning brief = lightweight (calendar + tasks + email + overnight activity if any)
- Evening brief = comprehensive (system health + sync + accomplishments)
- Both are automated via Task Scheduler (no manual trigger needed)
- Background sync runs every 3 hours (no notification, just keeps Supabase current)
- On-demand sync available before platform switching
- Operating Rhythm Calendar check still happens at first Claude Code session (separate from Telegram briefs)

---

## Step 10: Error Resilience for Scheduled Tasks

### File: `tools/audit/telegram_sender.py` — Add error handling + retry

**Problem:** Currently NO try/except around `httpx.post()` — a network error crashes the entire scheduled task, and the report is permanently lost. No retry logic exists.

**Fix:**
- Wrap all `httpx.post()` calls in try/except with 2 retries (3-second backoff)
- On final failure: save report text to `.tmp/unsent-brief-{timestamp}.txt` as fallback
- Return structured error dict (not crash) so the caller can handle it
- Add SMTP fallback: if Telegram fails after retries, send report via email to Chris (using existing SMTP credentials in .env)

```python
def send_report(text: str, retries: int = 2) -> list:
    """Send report to Telegram with retry + SMTP fallback."""
    # 1. Try Telegram (up to 3 attempts with 3s backoff)
    # 2. If all Telegram attempts fail:
    #    a. Save to .tmp/unsent-brief-{timestamp}.txt
    #    b. Try SMTP fallback to Chris's email
    #    c. Return error dict with failure details
    # 3. On success: return list of response dicts as before
```

### File: `tools/audit/daily_audit.py` — Wrap each check in try/except

**Problem:** An uncaught exception in ANY check kills the entire audit. If `check_calendar()` crashes, nothing after it runs.

**Fix:**
- Wrap each check call in individual try/except
- On exception: set that check's result to `{"status": "ERROR", "error": str(e)}`
- Audit continues running remaining checks
- Errors become attention items (see Step 11)

---

## Step 11: Audit Error Surfacing

### File: `tools/audit/daily_audit.py` + `tools/audit/weekly_audit.py` — Surface errors as attention items

**Problem:** If a check returns `status: "ERROR"` or `"SKIPPED"`, it's invisible — never surfaces in the brief, Chris never knows.

**Fix:** After all checks run, scan all results for non-OK statuses:

```python
# After all checks complete:
for check_name, result in all_check_results.items():
    if isinstance(result, dict) and result.get("status") in ("ERROR", "SKIPPED"):
        error_detail = result.get("error", "unknown")
        results["attention_items"].append(
            f"⚠️ {check_name} {result['status']}: {error_detail}"
        )
```

Applies to both morning and evening briefs. Any check that errors or is skipped becomes a visible attention item in the Telegram report.

---

## Step 12: Session-Start Supabase Check

### File: `tools/audit/audit_checks.py` — New function

**`check_recent_interactions(since_hours=24)`** — Queries Supabase logs for recent platform interactions:

```python
def check_recent_interactions(since_hours: int = 24) -> dict:
    """Query Supabase logs for interactions since N hours ago."""
    # Uses httpx GET to /rest/v1/logs?timestamp=gte.{cutoff}
    # Returns:
    # {
    #     "status": "OK",
    #     "count": 5,
    #     "platforms": {"telegram": 4, "task_scheduler": 1},
    #     "summary": ["Memory query: pricing", "Calendar check", ...],
    #     "errors": [{"workflow": "morning_audit", "error": "calendar API timeout"}],
    # }
```

**Purpose:** When a new Claude Code session starts, the Operating Rhythm check can call this to see what happened on other platforms since last session. Closes the "what did I miss while away?" gap.

**Integration with Operating Rhythm:** Add to `workflows/operating-rhythm.md` under session-start protocol:
- After checking Operating Rhythm Calendar, also call `check_recent_interactions()`
- If interactions found: brief summary to Chris ("Since your last session: 4 Telegram interactions, 1 scheduled audit. 0 errors.")
- If errors found: flag immediately ("1 error detected in morning brief — calendar API timeout")

---

## Step 13: Structured Error Logging to Supabase (Foundation for Autonomous Resolution)

### File: `tools/audit/audit_checks.py` — New function

**`log_error_event(source, error_type, detail, severity="medium")`** — Logs structured errors to Supabase:

```python
def log_error_event(source: str, error_type: str, detail: str, severity: str = "medium") -> dict:
    """Log a structured error to Supabase for tracking and future autonomous resolution."""
    # Writes to logs table:
    # {
    #     "agent_id": "marcus",
    #     "workflow_name": "error_event",
    #     "platform": source,           # "morning_brief", "evening_brief", "sync", etc.
    #     "success": false,
    #     "agent_response": json.dumps({
    #         "error_type": error_type,  # "api_timeout", "auth_failure", "parse_error", etc.
    #         "detail": detail,          # Human-readable description
    #         "severity": severity,      # "low", "medium", "high", "critical"
    #         "resolution_status": "unresolved",
    #         "requires_human": null,    # Phase 2 fills this: true/false
    #         "resolution_log": [],      # Phase 2 fills: [{agent, action, result, timestamp}]
    #     }),
    #     "metadata": {"error_type": error_type, "severity": severity},
    # }
```

**How it integrates with the brief error surfacing (Step 11):**
- When Step 11 detects an ERROR/SKIPPED check, it also calls `log_error_event()` to record it
- The error is now: (a) in the brief (Chris sees it), (b) in Supabase (agents can query it later)

**Why this matters for Phase 2-3 (Autonomous Error Resolution):**

This creates the **structured error record** that the autonomous resolution system will hook into. The schema is designed for it:

- `resolution_status`: `"unresolved"` → `"investigating"` → `"resolved"` or `"blocked_human"`
- `requires_human`: `null` (not yet triaged) → `true` (needs Chris) or `false` (agents can fix)
- `resolution_log`: Array of troubleshooting steps taken — what was tried, what worked, what didn't

**Phase 2-3 will add** (NOT in this plan — requires n8n agent orchestration):
1. **Error dispatch workflow** — n8n watches for new `error_event` logs → routes to Marcus → Marcus assigns agent
2. **Agent troubleshooting loop** — Agent tries fixes, appends to `resolution_log`, updates `resolution_status`
3. **Immediate notification** — When resolved: Telegram notification ("System fixed"). When blocked: Telegram with steps Chris needs to take
4. **Learning capture** — After resolution, agent updates MEMORY.md with root cause + fix for future prevention
5. **Self-healing** — If same error recurs, agent checks memory for previous fix and applies automatically

The full autonomous error resolution flow Chris described:
```
Error detected → Log to Supabase (this plan)
  → Marcus auto-dispatched (Phase 2)
  → Agent troubleshoots autonomously (Phase 2)
  → Each attempt logged to resolution_log (Phase 2)
  → Resolved? → Immediate Telegram notification (Phase 2)
  → Blocked on Chris? → Immediate Telegram with steps (Phase 2)
  → Chris acts → Team re-tests → Loop until fixed (Phase 2)
  → Agent updates MEMORY.md with solution (Phase 2)
  → Future: auto-apply known fix if same error recurs (Phase 3)
```

This plan lays the detection + logging foundation. Phase 2 adds the autonomous muscles.

---

## Files Modified

| File | Change |
|------|--------|
| `tools/audit/config.py` | Add SYNC_HASH_FILE, OPENAI_API_KEY, PROJECT_MEMORY_DIR |
| `tools/audit/audit_checks.py` | Add 9 new functions: `check_supabase_sync()`, `sync_to_supabase()`, `check_pending_tasks()`, `check_active_projects()`, `check_today_activity()`, `check_overnight_activity()`, `check_recent_interactions()`, `log_error_event()` + per-check error handling |
| `tools/audit/daily_audit.py` | Add `run_morning_brief()` + `run_evening_brief()`, keep `run_daily_audit()` as alias, wrap each check in try/except, surface ERROR/SKIPPED as attention items |
| `tools/audit/weekly_audit.py` | Same error surfacing: wrap checks in try/except, surface ERROR/SKIPPED |
| `tools/audit/report_formatter.py` | Add `format_morning()` + `format_evening()`, keep `format_daily()` as alias |
| `tools/audit/telegram_sender.py` | Add retry logic (2 retries, 3s backoff) + save-to-file fallback + SMTP fallback |
| `tools/run_audit.py` | Add `morning`, `evening`, `sync` modes; rename `daily` to `evening` (with alias) |
| `tools/seed_supabase.py` | Add `parse_pending_tasks()`, `parse_rhythm_calendar()`, expand `collect_kb_docs()` to include memory topic files |
| `workflows/operating-rhythm.md` | Add Morning/Evening Brief section, sync strategy documentation, session-start Supabase check |

No new files created. 9 files modified.

---

## Verification

1. `python tools/run_audit.py morning --no-telegram` — Verify morning format (calendar today + email + tasks + project + overnight if any)
2. `python tools/run_audit.py evening --no-telegram` — Verify evening format (calendar tomorrow + activity + tasks + system health + sync)
3. `python tools/run_audit.py sync` — Verify on-demand sync works (no Telegram, just console output with stats)
4. `python tools/run_audit.py morning` — Verify Telegram HTML renders correctly
5. `python tools/run_audit.py evening` — Verify Telegram HTML + Supabase sync runs
6. Verify `.tmp/supabase-sync-hash.json` created after first sync/evening run
7. Modify MEMORY.md manually, run `sync` — verify hash mismatch detected and auto-pushes
8. `python tools/run_audit.py daily --no-telegram` — Verify backwards compatibility (runs evening)
9. `python tools/run_audit.py weekly --no-telegram` — Verify weekly still works (skills moved from daily to weekly)
10. Verify expanded seeder coverage: run `python tools/seed_supabase.py --dry-run` — confirm pending tasks, rhythm calendar, and memory topic files are counted
11. Query Supabase for pending tasks: `GET /rest/v1/memories?key=like.task_*` — verify all pending items synced
12. Query Supabase for memory topic files: `GET /rest/v1/kb_docs?category=eq.memory_topic` — verify 5 files synced
13. Verify Windows Task Scheduler: 4 tasks (MorningBrief 6 AM, EveningBrief 9 PM, SupabaseSync every 3 hours, WeeklyAudit Sunday 9 PM)
14. **Error resilience:** Disconnect network temporarily, run `python tools/run_audit.py morning --no-telegram` — verify audit completes (checks show ERROR, not crash), verify `.tmp/unsent-brief-*.txt` fallback works
15. **Error surfacing:** Intentionally break one check (e.g., bad Supabase URL), run morning brief — verify ERROR appears as attention item in the output
16. **Error logging:** After test #15, query Supabase `logs` table for `workflow_name=error_event` — verify structured error record created with `resolution_status: "unresolved"`
17. **Session-start check:** Call `check_recent_interactions(since_hours=24)` directly — verify it returns recent log entries from other platforms
