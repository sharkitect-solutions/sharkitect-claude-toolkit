# CEO Daily Briefing System — Design & Implementation Plan
## STATUS: COMPLETE (2026-04-08). All 8 steps executed. E2E tested. Brief format approved.

## Context

The CEO briefing system has failed 3 times due to rushing into implementation without proper design:
1. **RemoteTrigger approach** — MCP race condition on cloud cold boot. Tools unavailable when session starts. PAUSED.
2. **Deterministic Python script** (`hq-brief-generator.py`) — No AI reasoning, no Gmail, no Calendar. Just Supabase data with if/else formatting. Useless output.
3. **Wrong prioritization** — All projects were "medium" priority, no queue_position sorting. Briefs showed random tasks.

This plan designs a reliable, AI-powered briefing system that works first time by leveraging proven infrastructure (ralph-loop, ralph-scheduler.py) and the HQ session's pre-connected MCPs.

---

## Architecture Decision: Trigger File Pattern

**Approach:** ralph-scheduler.py writes a trigger file when a brief is due. ralph-loop detects the file and the HQ Claude session generates the brief using AI + MCPs.

**Why this approach:**
- ralph-scheduler.py is proven — handles time windows, dedup, state management. Only change: what command it runs.
- ralph-loop is proven — runs every 5 min. Only add: file-existence check.
- MCPs are pre-connected in HQ session — Gmail, Calendar, Supabase all live. No cold-boot issues.
- Separation of concerns: scheduler handles timing, AI handles intelligence.

**Delivery cascade:**
- PRIMARY: HQ ralph-loop (AI + MCPs) at :00 each brief hour
- SECONDARY: Windows Task Scheduler (sends last saved brief) at :15
- PAUSED: RemoteTrigger (re-enable when MCP boot issue resolved)

---

## Schema Changes (Supabase Migration)

### New Tables

**`briefs`** — Brief history for evening-morning comparison and audit trail
```sql
CREATE TABLE IF NOT EXISTS briefs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000001',
    brief_type TEXT NOT NULL CHECK (brief_type IN ('morning', 'midday', 'evening')),
    content TEXT NOT NULL,
    focus_project TEXT,
    generated_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_briefs_type_date ON briefs (brief_type, generated_at DESC);
ALTER TABLE briefs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "briefs_all" ON briefs FOR ALL
    USING (tenant_id = '00000000-0000-0000-0000-000000000001'::uuid);
```

### Altered Tables

```sql
-- tasks: add due_date for "what's due today?" filtering
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date DATE;

-- projects: add target_date and health for on-track assessment
ALTER TABLE projects ADD COLUMN IF NOT EXISTS target_date DATE;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS health TEXT DEFAULT 'on_track';
```

### NOT Building (YAGNI)

- **daily_focus table** — The briefs table already stores what the focus was. Morning brief sets focus by queue_position. No separate table needed.
- **decisions table** — Adds write burden with no clear writer. Decisions are in session history and git commits. Skip for now.
- **feedback_metrics population** — Nice-to-have for trend analysis. Not needed for V1 briefs. Can add later.

---

## Implementation Steps

### Step 1: Supabase Migration -- COMPLETE (2026-04-08, Skill Hub session)
**What:** Run schema migration via Supabase MCP `apply_migration`
**Verify:** All 4 checks passed: briefs table exists, tasks.due_date, projects.target_date, projects.health.
**Migration name:** `ceo_briefing_system_v1`

### Step 2: Create `tools/write-brief-trigger.py` (NEW FILE)
**Location:** `1.- SHARKITECT DIGITAL WORKFORCE HQ/tools/write-brief-trigger.py`
**What:** Tiny stdlib-only Python script (~50 lines) that:
- Takes one argument: `morning`, `midday`, or `evening`
- Checks Supabase `activity_stream` for `brief_sent` in last 2h (deduplication)
- If not already sent: writes `.tmp/brief-trigger.json` with `{"type": "morning", "requested_at": "ISO timestamp"}`
- If already sent: prints skip message, exits cleanly
- Reads Supabase credentials from `.env`

### Step 3: Update `tools/ralph-scheduler.py` SCHEDULE
**Location:** `1.- SHARKITECT DIGITAL WORKFORCE HQ/tools/ralph-scheduler.py`
**What:** Change the 3 brief SCHEDULE entries to call `write-brief-trigger.py` instead of `hq-brief-generator.py`:
```python
{"name": "morning-brief", "command": ["python", "tools/write-brief-trigger.py", "morning"], "time_ct": "06:00", ...},
{"name": "midday-brief", "command": ["python", "tools/write-brief-trigger.py", "midday"], "time_ct": "12:00", ...},
{"name": "evening-brief", "command": ["python", "tools/write-brief-trigger.py", "evening"], "time_ct": "21:00", ...},
```
**Note:** Change times from :05 to :00. No more staggering — HQ is primary now, not fallback.

### Step 4: Create `workflows/ceo-brief-templates.md` (NEW FILE)
**Location:** `1.- SHARKITECT DIGITAL WORKFORCE HQ/workflows/ceo-brief-templates.md`
**What:** The brief generation instructions and templates, kept OUTSIDE of CLAUDE.md to avoid bloating it. Contains:
- CEO Prioritization Framework
- MCP data gathering instructions (exact queries)
- Morning/Midday/Evening templates
- Telegram send instructions
- Dedup and logging instructions

This file is what the ralph-loop prompt tells Claude to `Read` when a trigger file is detected.

**Morning Brief Template — "Set me up to win today"**
```
MORNING BRIEF — {Day of Week}, {Month} {Day}, {Year}

FOCUS: {#1 project by queue_position, client work first} ({Client: XX} if applicable)
  Phase {N}/{total}: {phase name}
  [ ] {task 1} {[BLOCKED] if blocked}
  [ ] {task 2}
  ...
  ({X} tasks remaining{, Y blocked if any})

UP NEXT: {#2 project} — {1-line status}

CALENDAR
  {Time} — {Event} ({who/what context})
  (or: Clear day.)

EMAILS
  [HIGH] {sender} — {what they need}
  [MED] {sender} — {summary}
  (or: Inbox clear.)

{Only if non-healthy components:}
ALERTS
  [{status}] {component} — last heartbeat {Xh ago}

{Only if tasks with carried_days > 2:}
CARRY-FORWARD
  {task} [{X}d carry]

SUGGESTED FOCUS
{2-3 sentences: What to work on first and WHY. Reference blockers, deadlines, aging tasks. Strategic advisor voice.}
```

**Midday Brief Template — "Are we on track?"**
```
MIDDAY CHECK-IN — {Day of Week}, {Month} {Day}, {Year}

FOCUS CHECK: {#1 project} — {On track / Behind / Blocked} — {1 line why}

WINS
  [x] {tasks completed since morning}
  (or: No tasks completed yet.)

BLOCKERS
  {New issues since morning, or: None.}

AFTERNOON
  {Remaining calendar events, or: Clear afternoon.}

SUGGESTIONS
{1-2 sentences: What to prioritize for afternoon based on morning progress.}
```

**Evening Brief Template — "How did today actually go?"**
```
EVENING WRAP-UP — {Day of Week}, {Month} {Day}, {Year}

ASSESSMENT: {Strong / Partial / Miss} — {1 sentence summary}

DONE
  [x] {completed tasks today}
  (or: No tasks completed today.)

NOT DONE
  [ ] {incomplete tasks} — {why, if discernible}

TOMORROW
  Calendar: {tomorrow's events, or: Clear day.}
  Priority: {#1 project + top task to tackle}

{Only if flags exist:}
FLAGS
  [STALE] {task} — carried {X}d
  [SYSTEM] {component} — {status}
  [BLOCKED] {project} — {reason}
```

### Step 5: Update HQ CLAUDE.md ralph-loop prompt
**Location:** `1.- SHARKITECT DIGITAL WORKFORCE HQ/CLAUDE.md`
**What:** Replace the current ralph-loop one-liner with:
```
/ralph-loop 5m First run: python tools/ralph-scheduler.py run — then check if .tmp/brief-trigger.json exists. If it exists: read it, then read workflows/ceo-brief-templates.md and follow the instructions exactly to generate and send the brief. After sending, delete the trigger file. If no trigger file exists, stay quiet.
```
This keeps the CLAUDE.md compact. All the intelligence (templates, queries, format) lives in the workflow file.

### Step 6: Update `tools/fallback-brief-sender.py`
**Location:** `1.- SHARKITECT DIGITAL WORKFORCE HQ/tools/fallback-brief-sender.py`
**What:** 
- Add `midday` to valid types (currently only morning/evening)
- Create `tools/fallback-midday-brief.bat` for Windows Task Scheduler
- Register Windows scheduled task: `SharkitectHQ\FallbackMiddayBrief` at 12:15 PM daily

### Step 7: Project Data Cleanup (with Chris)
**What:** Review all projects in Supabase and clean up the data so briefs only surface what matters.
1. **Set target_date** on real priorities (SystemLink, AIOS) — gives briefs the ability to say "on track" or "behind"
2. **Table or archive low-priority ideas** — projects like "Voice AI", "ERA as Client Offering", "Update GBP" that are ideas, not active work. Set `status: 'tabled'` or `category: 'idea'` so briefs skip them. The brief query already filters `WHERE status IN ('active','pending','blocked')` — tabled projects won't appear.
3. **Set health** on active projects — `on_track`, `at_risk`, `blocked`, `off_track`
4. **Add due_date** to tasks that actually have deadlines. Leave others NULL — the brief will only surface due items if the field is populated.
5. **Clean orphan tasks** — tasks tied to tabled/completed projects that are still showing as pending.
6. **Verify queue_position** order matches Chris's current strategic priorities.

**This step is interactive** — HQ session walks through each project with Chris for 5 minutes.

### Step 8: End-to-End Test
1. Manually create trigger: write `{"type":"morning","requested_at":"2026-04-09T11:00:00Z"}` to `.tmp/brief-trigger.json`
2. Let ralph-loop detect it (or manually trigger the ralph-loop prompt)
3. Verify:
   - [ ] Telegram received a properly formatted CEO brief
   - [ ] Brief shows FOCUS = SystemLink (Client: FF), UP NEXT = AIOS
   - [ ] Gmail emails included (actionable only)
   - [ ] Calendar events included
   - [ ] System alerts shown if any non-healthy
   - [ ] `activity_stream` has `brief_sent` row
   - [ ] `.tmp/last-morning-brief.txt` exists with brief content
   - [ ] `briefs` table has a row with the brief content
   - [ ] `.tmp/brief-trigger.json` is deleted
   - [ ] Fallback at :15 detects `brief_sent` and skips

---

## CEO Prioritization Framework (embedded in ceo-brief-templates.md)

```
PRIORITY ORDER (non-negotiable):
1. queue_position is the authoritative rank. Lower number = higher priority.
2. Client projects (client_id IS NOT NULL) always outrank internal projects at the same priority level.
3. Priority levels: critical > high > medium > low
4. The FOCUS project = lowest queue_position among active projects, client work first.
5. The UP NEXT project = second by same logic.
6. Other projects ONLY appear in FLAGS if blocked or carrying tasks 3+ days.
7. NEVER show a low-priority project above a higher one just because it has a "critical" task.

DATA QUERY (single join, ordered correctly):
SELECT p.name, p.priority, p.queue_position, p.client_id, p.current_phase,
       p.phase_number, p.total_phases, p.blocker, p.target_date, p.health,
       t.task, t.priority as task_priority, t.status as task_status,
       t.carried_days, t.due_date
FROM projects p
LEFT JOIN tasks t ON t.project = p.name AND t.status != 'completed'
WHERE p.status IN ('active','pending','blocked')
ORDER BY p.queue_position ASC,
         CASE t.priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2
              WHEN 'medium' THEN 3 ELSE 4 END,
         t.created_at ASC
```

---

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| ralph-loop doesn't detect trigger file | Test explicitly. The prompt is clear: "check if .tmp/brief-trigger.json exists" |
| MCP call fails mid-brief | Templates instruct: "If any MCP call fails, note UNAVAILABLE in that section, continue with remaining data" |
| Trigger file persists (ralph-loop crashes) | write-brief-trigger.py adds staleness: if file > 30min old, delete without generating |
| Duplicate briefs | 3-layer dedup: (1) ralph-scheduler state file, (2) write-brief-trigger.py checks activity_stream, (3) ralph-loop checks before sending |
| Brief exceeds 4000 chars (Telegram limit) | Templates designed to be concise. Prompt says "Keep under 4000 chars" explicitly |
| hq-brief-generator.py orphaned | Keep as fallback reference. fallback-brief-sender.py can call it if no .tmp/last-{type}-brief.txt exists |

---

## Files Modified/Created Summary

| File | Action | Workspace |
|------|--------|-----------|
| `tools/write-brief-trigger.py` | CREATE | HQ |
| `workflows/ceo-brief-templates.md` | CREATE | HQ |
| `tools/ralph-scheduler.py` | EDIT (SCHEDULE entries only) | HQ |
| `CLAUDE.md` | EDIT (ralph-loop prompt) | HQ |
| `tools/fallback-brief-sender.py` | EDIT (add midday) | HQ |
| `tools/fallback-midday-brief.bat` | CREATE | HQ |
| Supabase migration | RUN (briefs table, alter tasks/projects) | Cloud |
| `tools/hq-brief-generator.py` | KEEP (fallback reference) | HQ |

---

## What This Does NOT Cover (Future)

- RemoteTrigger re-enablement (blocked on platform MCP boot fix)
- decisions table (no clear writer yet)
- feedback_metrics population (trend analysis, not V1)
- Escalations wiring (needs n8n error workflows first)
- Brief scoring / day_score tracking (evening assessment is text-based for now)
