# HQ Old Audit System Cleanup

## Context

We deleted 6 stale Windows scheduled tasks (DepsUpdate, SupabaseSync, and 4 broken duplicates in SharkitectDigital\ folder) plus their directly-associated files (audit_sync.bat, audit_midday.bat, update-deps.bat, update-deps.py). But the OLD HQ audit system that powered those tasks is still present — 120KB+ of Python code, 4 more .bat files, log files, and 24 documents with stale references. Sentinel (workspace 4) replaces this entire system. This plan cleans up everything so HQ doesn't reference things that no longer exist.

4 remaining disabled Windows tasks (MorningBrief, EveningBrief, WeeklyAudit, MidnightAudit) are being kept for rebuild later — they'll be rewired to Sentinel tools in a separate task.

---

## Phase 1: Fix Dependency Before Deleting

**Why:** `tools/seed_plan_to_supabase.py` (line 74-76) imports from `audit.config`. If we delete tools/audit/ without fixing this, that script breaks.

**File:** `C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/tools/seed_plan_to_supabase.py`

**Action:** Replace lines 74-76:
```python
# OLD:
sys.path.insert(0, str(Path(__file__).parent / "audit"))
from audit.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

# NEW (read from .env directly, same pattern as other HQ tools):
# Load env vars - audit.config module has been removed; read .env directly
def _load_env():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

_load_env()
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
```

Verify `os` and `Path` are already imported at top of file.

---

## Phase 2: Delete Dead Code

All files in the old audit system. Git history preserves everything if ever needed.

**Delete files (7):**
1. `tools/audit_morning.bat`
2. `tools/audit_evening.bat`
3. `tools/audit_weekly.bat`
4. `tools/audit_midnight.bat`
5. `tools/run_audit.py`
6. `tools/run_audit_silent.py`
7. `tools/register_tasks.py`

**Delete directories (2):**
8. `tools/audit/` (entire directory including __pycache__)
9. `tools/logs/` (7 stale log files)

---

## Phase 3: Update Active Documents

### 3a. CLAUDE.md
File: `HQ/CLAUDE.md`

| Line | Current | New |
|------|---------|-----|
| 24 | `Task Scheduler: Python scripts on schedule (briefs, syncs, audits, monitoring)` | `Sentinel (workspace 4): monitoring, briefs, dream consolidation, health checks (scheduled automation)` |
| 31 | `All folders + n8n + Task Scheduler read/write same database` | `All folders + n8n + Sentinel read/write same database` |
| 35 | `YES → n8n or Task Scheduler. NO → Claude Code.` | `YES → n8n or Sentinel scheduled tasks. NO → Claude Code.` |
| 218 | `\| tools/audit/ \| Briefing pipeline, audit checks, report formatter \|` | DELETE this row |
| 230 | `**Task Scheduler** — 6 tasks: morning brief (5AM)...` | `**Sentinel** (workspace 4) — handles monitoring, briefs, and audits. Scheduled tasks being rebuilt to use Sentinel tools.` |

### 3b. README.md
File: `HQ/README.md`

- **Lines 52-63** (Scheduled Automation section): Replace entire section with:
  ```
  ## Scheduled Automation
  
  Monitoring, briefs, and audits are handled by [Sentinel](../4.- Sentinel/) (workspace 4).
  Legacy scheduled tasks are disabled and being rebuilt to use Sentinel tools.
  ```
- **Tools table** (~line 43-44): Remove `run_audit.py` row if present

### 3c. workflows/operating-rhythm.md
File: `HQ/workflows/operating-rhythm.md`

- **Lines 22-36** (Automated Briefs section): Replace task table + batch file list with Sentinel reference
- **Lines 353-370** (Audit Scripts Reference section): Delete entirely — references files being deleted

---

## Phase 4: Verify

1. Run: `python tools/seed_plan_to_supabase.py --help` (or similar) to confirm it still imports cleanly
2. Check `tools/` directory contains only non-audit tools (bootstrap.py, supabase-sync.py, supabase_memory.py, hooks/, sop_docx_builder.py, etc.)
3. Grep HQ for `audit_sync|audit_midday|run_audit_silent|register_tasks` — should return zero active-doc hits
4. Confirm archive/KB docs NOT touched (historical record preserved)

---

## What NOT to Touch

- `_archive/` — all historical agent memories and old bot data. Leave as-is.
- `knowledge-base/projects/*/plan.md` — historical project plans. Leave as-is.
- The 4 remaining disabled Windows scheduled tasks — rebuilt in separate task.
- `supabase-sync.py`, `supabase_memory.py` — independent tools, no audit imports.

---

## Verification

- `seed_plan_to_supabase.py` runs without import error
- No broken references in CLAUDE.md, README.md, operating-rhythm.md
- `tools/` directory is clean (no audit remnants)
- HQ agent can start a session without errors from stale references
