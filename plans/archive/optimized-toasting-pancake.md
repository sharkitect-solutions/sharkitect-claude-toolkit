# Plan: Make Sentinel Monitoring Reliable + Clean Up Legacy Components

## Context

The n8n Watcher sends "SENTINEL ALERT" for failed components. 4 ghost entries (n8n-morning-brief, n8n-evening-brief, n8n-dream-trigger, n8n-alex) already deleted. 3 real tools remain failed because they only run inside an ephemeral Claude Code session.

**Goal:** Make `nightly-dream`, `sentinel-brief`, and `sentinel-repo-monitor` run reliably regardless of session state. Add auto-sync to repo-monitor. Upgrade dream-consolidation with AI reasoning. Clean up all stale references.

---

## Tool-by-Tool Approach

### Tool 1: `brief-generator.py` (System Health Report) — Task Scheduler

Pure data formatting. No AI needed. Pulls Supabase data, formats, sends Telegram.
**Schedule:** Daily 5:45 AM CT via Windows Task Scheduler.

### Tool 2: `repo-monitor.py` (GitHub Fork Tracker) — Task Scheduler + Auto-Sync

Pure API calls. No AI needed. Enhancement: auto-sync forks when behind.
**Schedule:** Weekly Sunday 8 PM CT via Windows Task Scheduler.

### Tool 3: `dream-consolidation.py` (Brain Maintenance) — Claude CLI (Unified)

All-in-one Claude CLI job. One `.bat`, one scheduled task, one report.

**How it works:**
A single `claude -p` call (using `--model sonnet`) that orchestrates everything:

1. **Deterministic phases (Python via Bash tool):** Claude runs `python tools/dream-consolidation.py run-stage1` which executes:
   - Phase 1 (Orient): Count events by workspace/type
   - Phase 2 (Duplicates): Vector similarity merge via Supabase RPC
   - Phase 4 (Freshness): Flag stale memories via timestamp math
   - Writes results to `.tmp/dream-stage1-results.json`

2. **AI reasoning phases (Sonnet's own intelligence):** Claude reads the Stage 1 results + queries Supabase for raw data, then:
   - Phase 3 (Conflicts): Reads both memory contents, determines true contradiction vs complementary
   - Phase 5 (Voice): Synthesizes natural-language voice guide from approved/rejected samples
   - Phase 6 (Patterns): Identifies meaningful patterns beyond threshold math
   - Phase 7 (Report): Writes insightful consolidation report with actionable recommendations

3. **Delivery:** Claude runs `python tools/telegram-send.py` to send the final report
4. **Heartbeat:** Claude runs a Python snippet to update `nightly-dream` in Supabase `system_health`

**Cost:** Sonnet once daily at 3 AM, small context (memory data + activity stream). Minimal.

**Schedule:** Daily 3:00 AM CT via Windows Task Scheduler → `.bat` → `claude -p --model sonnet`

**Fallback:** If Claude CLI fails (API down, no internet), the Watcher flags `nightly-dream` as stale after 36h. Next morning's system brief includes the failure. No data loss — brain cleanup just waits a day.

---

## Implementation Steps

### Step 1: Create `scheduled-runner.py` (unified wrapper)

**File:** `4.- Sentinel/tools/scheduled-runner.py`

Wraps any target script/command with:
1. Reads `.tmp/ralph-schedule.json` — skips if task already ran within its cadence window
2. Runs the target command via subprocess
3. On success: updates state file + writes heartbeat to Supabase `system_health`
4. Logs to `.tmp/scheduled-runner.log`

Heartbeat mapping:

| Task Name | Heartbeat Component | Cadence Window |
|-----------|-------------------|----------------|
| `system-report` | `sentinel-brief` | 20 hours |
| `repo-monitor` | `sentinel-repo-monitor` | 6 days |
| `dream-consolidation` | `nightly-dream` | 20 hours |

Key: `brief-generator.py` and `repo-monitor.py` do NOT write their own heartbeats today. This wrapper handles it for them. `dream-consolidation.py` already writes its own, but the wrapper serves as backup.

### Step 2: Add auto-sync to `repo-monitor.py`

**File:** `4.- Sentinel/tools/repo-monitor.py`

Add `auto_sync_fork(owner_repo)` function:
- POST to `https://api.github.com/repos/{owner_repo}/merge-upstream` with `{"branch": "main"}`
- Uses existing `GITHUB_PAT_KEY` from `.env`
- On success: finding becomes `fork_synced` (informational, no human action needed)
- On failure (merge conflict): finding stays `fork_behind_conflict` (needs human attention)

Modify `scan_all()`: after `check_fork_behind` detects a stale fork, call `auto_sync_fork`.

### Step 3: Add `run-stage1` command to `dream-consolidation.py`

**File:** `4.- Sentinel/tools/dream-consolidation.py`

Add a `run-stage1` subcommand that runs only Phases 1, 2, 4 (Orient, Duplicates, Freshness). Writes results to `.tmp/dream-stage1-results.json`. The existing `run` command continues to work for manual/session use.

### Step 4: Create dream consolidation prompt

**File:** `4.- Sentinel/tools/dream-consolidation-prompt.md`

The prompt Claude CLI receives. Structured instructions for:
1. Run `python tools/dream-consolidation.py run-stage1 --alert` (deterministic phases)
2. Read `.tmp/dream-stage1-results.json`
3. Query Supabase for conflict details, voice samples, recent activity
4. Perform AI analysis (conflicts, voice synthesis, patterns, insights)
5. Format final report
6. Send via `python tools/telegram-send.py`
7. Update `nightly-dream` heartbeat in Supabase

### Step 5: Create `.bat` wrappers

**Files in `4.- Sentinel/tools/`:**

| File | What It Runs |
|------|-------------|
| `sched-system-report.bat` | `scheduled-runner.py system-report "python tools/brief-generator.py morning"` |
| `sched-repo-monitor.bat` | `scheduled-runner.py repo-monitor "python tools/repo-monitor.py scan"` |
| `sched-dream.bat` | `scheduled-runner.py dream-consolidation "claude -p \"$(cat tools/dream-consolidation-prompt.md)\" --model sonnet --allowedTools \"Bash(python *)\" \"Read\" \"Write\""` |

Each `.bat`: `cd /d` to Sentinel workspace, run command, append to `.tmp/sched-*.log`.

### Step 6: Register Windows Scheduled Tasks

| Task Name | Schedule | Time (CT) |
|-----------|----------|-----------|
| `Sentinel-MorningReport` | Daily | 5:45 AM |
| `Sentinel-DreamConsolidation` | Daily | 3:00 AM |
| `Sentinel-RepoMonitor` | Weekly Sunday | 8:00 PM |

User runs `schtasks /create` commands from elevated Command Prompt.

### Step 7: Add threshold to health-monitor.py

**File:** `4.- Sentinel/tools/health-monitor.py`

Add to THRESHOLDS:
```python
"sentinel-repo-monitor": {"degraded_hours": 192, "failed_hours": 336},  # weekly: ~8d / ~14d
```

### Step 8: Update docs

- `4.- Sentinel/docs/watcher-workflow-spec.md` — remove deleted components (n8n-morning-brief, n8n-evening-brief, n8n-dream-trigger, n8n-alex), update Components Watched table
- `4.- Sentinel/docs/n8n-brain-integration-guide.md` — clean up legacy "may still exist" note, update component table
- `4.- Sentinel/CLAUDE.md` — note that dream/brief/repo now run via Task Scheduler

### Step 9: Update MEMORY.md

- Record: 4 ghost entries deleted, 3 tools made reliable via Task Scheduler
- Record: dream-consolidation upgraded with AI (Sonnet via CLI)
- Record: repo-monitor now auto-syncs forks
- Update component counts

---

## Files Summary

| Action | File | What |
|--------|------|------|
| CREATE | `4.- Sentinel/tools/scheduled-runner.py` | Unified wrapper: dedup + heartbeat + logging |
| CREATE | `4.- Sentinel/tools/dream-consolidation-prompt.md` | AI prompt for full dream cycle |
| CREATE | `4.- Sentinel/tools/sched-system-report.bat` | Task Scheduler → brief-generator |
| CREATE | `4.- Sentinel/tools/sched-repo-monitor.bat` | Task Scheduler → repo-monitor |
| CREATE | `4.- Sentinel/tools/sched-dream.bat` | Task Scheduler → claude CLI dream |
| MODIFY | `4.- Sentinel/tools/repo-monitor.py` | Add auto_sync_fork() |
| MODIFY | `4.- Sentinel/tools/dream-consolidation.py` | Add run-stage1 command |
| MODIFY | `4.- Sentinel/tools/health-monitor.py` | Add repo-monitor threshold |
| MODIFY | `4.- Sentinel/docs/watcher-workflow-spec.md` | Remove deleted, update table |
| MODIFY | `4.- Sentinel/docs/n8n-brain-integration-guide.md` | Clean legacy refs |
| MODIFY | `4.- Sentinel/CLAUDE.md` | Note Task Scheduler migration |
| MODIFY | MEMORY.md | Record all changes |

**NOT modified:** `ralph-scheduler.py` — keep all tasks in schedule. If session is open, ralph-loop handles them. Shared state file prevents duplicates.

---

## Verification

1. `dream-consolidation.py run-stage1 --dry-run` — runs only phases 1, 2, 4, writes `.tmp/dream-stage1-results.json`
2. `repo-monitor.py scan --dry-run` — shows auto-sync logic without executing
3. Each `.bat` runs manually — output appears in `.tmp/sched-*.log`
4. `scheduled-runner.py` twice in a row — second run skips ("already ran within window")
5. `health-monitor.py list` — all 3 show healthy after first successful runs
6. `claude -p "..." --model sonnet` — test the dream CLI trigger manually
7. Next Watcher cycle — no more SENTINEL ALERT for these components
