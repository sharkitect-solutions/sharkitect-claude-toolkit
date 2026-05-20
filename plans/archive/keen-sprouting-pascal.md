# Plan: Activate Document Lifecycle — Detection + Autonomous Review

## Context

The Document Lifecycle Management system was built in April 2026 with all components (skill, agent, hooks, Supabase table, freshness auditor). However, the **proactive layer** was never activated — no SessionStart hook, no scheduled checks, no autonomous review pipeline. Documents will silently go stale once review dates pass (earliest: May 6, 2026).

This plan activates everything in two phases:
- **Phase 1:** Detection & alerting (SessionStart hook + daily scheduled check)
- **Phase 2:** Autonomous review pipeline (dispatch → workspace review → draft → notify)

---

## Phase 1: Detection & Alerting

### 1A. SessionStart Hook Script

**New file:** `~/.claude/hooks/session-start-lifecycle.py` (~120 lines)

Self-contained Python script (stdlib only) that fires on every session start/resume:
1. Loads `.env` from CWD, falls back to Sentinel path (`4.- Sentinel/.env`)
2. Queries Supabase `doc_lifecycle` (all active docs)
3. Recomputes escalation states (current/due/deferred/overdue/critical)
4. PATCHes state changes back to Supabase
5. Filters docs for current workspace → writes `.tmp/doc-lifecycle-cache.json`
6. Also checks `.lifecycle-reviews/inbox/` for pending review requests (Phase 2)
7. If any non-current docs OR pending reviews exist, prints `additionalContext` warning
8. Non-blocking: wraps everything in try/except, exits 0 on any failure
9. urllib timeout: 10s

**Reuses:** `compute_escalation()` logic from `freshness-auditor.py`, workspace detection from `supabase-sync.py`

### 1B. Register SessionStart Hook

**Edit:** `~/.claude/settings.json` — add to `hooks` object:

```json
"SessionStart": [
  {
    "matcher": "startup|resume",
    "hooks": [
      {
        "type": "command",
        "command": "python \"C:/Users/Sharkitect Digital/.claude/hooks/session-start-lifecycle.py\"",
        "timeout": 15000
      }
    ]
  }
]
```

### 1C. Daily Scheduled Check

**New file:** `~/.claude/hooks/daily-freshness-check.bat` (3 lines)

```bat
@echo off
cd /d "C:\Users\Sharkitect Digital\Documents\Claude Code Workspaces\4.- Sentinel"
python tools\freshness-auditor.py check --alert
python tools\dispatch-lifecycle-reviews.py dispatch
```

Note: Line 4 is Phase 2's dispatcher — runs after freshness check completes.

**Register:** `schtasks /create /tn "Claude-DocLifecycle-DailyCheck" /tr "..." /sc daily /st 08:00 /f`

---

## Phase 2: Autonomous Review Pipeline

### Architecture

```
SENTINEL (daily 8AM or ralph-scheduler 2:15AM)
  freshness-auditor.py check → escalates states in Supabase
  dispatch-lifecycle-reviews.py dispatch → writes review requests per workspace
  │
  ├→ HQ/.lifecycle-reviews/inbox/review-request.json
  ├→ Skill Hub/.lifecycle-reviews/inbox/review-request.json
  ├→ Sentinel/.lifecycle-reviews/inbox/review-request.json
  └→ AIOS Builder/.lifecycle-reviews/inbox/review-request.json

Each workspace (on session start or ralph-loop):
  lifecycle-review-watcher.py --context → detects pending reviews
  │
  AI processes using document-lifecycle skill + lifecycle-review-processing.md
  │
  ├→ No changes needed: push-lifecycle to Supabase (mark reviewed)
  └→ Changes needed: draft in .lifecycle-reviews/drafts/
      │
      └→ Telegram: "2 drafts ready in HQ. Review at .lifecycle-reviews/drafts/"
  │
  Move request from inbox/ → processed/
```

### 2A. Dispatcher Tool

**New file:** `4.- Sentinel/tools/dispatch-lifecycle-reviews.py` (~180 lines)

Queries Supabase for all non-current docs, groups by workspace, writes review request JSONs.

**Workspace-to-path mapping** (from `supabase-sync.py` `detect_workspace()`):
```python
WORKSPACE_PATHS = {
    "workforce-hq": Path.home() / "Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ",
    "skill-management-hub": Path.home() / "Documents/Claude Code Workspaces/3.- Skill Management Hub",
    "sentinel": Path.home() / "Documents/Claude Code Workspaces/4.- Sentinel",
    "master-aios-builder": Path.home() / "Documents/Claude Code Workspaces/2.- Master AIOS Builder",
}
```

**Review request JSON schema:**
```json
{
    "request_id": "lr-20260407-workforce-hq-pricing-strategy-md",
    "dispatched_at": "2026-04-07T08:00:00Z",
    "workspace": "workforce-hq",
    "workspace_root": "C:/Users/.../1.- SHARKITECT DIGITAL WORKFORCE HQ",
    "doc_path": "knowledge-base/pricing-strategy.md",
    "category": "pricing",
    "escalation_state": "overdue",
    "days_overdue": 12,
    "reason": "Pricing doc — wrong pricing means revenue loss or client confusion",
    "what_to_check": [
        "Verify all package prices are current",
        "Check if any new services added since last review",
        "Confirm discount policies still apply"
    ],
    "last_reviewed": "2026-03-26T04:09:07+00:00",
    "review_cycle_days": 60
}
```

**Commands:**
- `dispatch` — write review requests to each workspace's inbox
- `status` — show what would be dispatched (dry run)

**Key behaviors:**
- Creates `.lifecycle-reviews/inbox/` dirs automatically via `os.makedirs(exist_ok=True)`
- Idempotent: skips if same workspace+doc_path already in inbox
- `what_to_check` generated from category using `CATEGORY_RISKS` plus category-specific prompts
- Sends single Telegram summary after dispatching: "Lifecycle Reviews Dispatched: [HQ] 3, [Skill Hub] 2"
- Filename: `{workspace}-{doc_path_slug}-{timestamp}.json`

### 2B. Lifecycle Review Watcher

**New file:** `3.- Skill Management Hub/tools/lifecycle-review-watcher.py` (~150 lines)

Mirrors `gap-watcher.py` exactly but for `.lifecycle-reviews/inbox/`. Single shared copy, called from any workspace via absolute path.

**Commands:**
- bare — human-readable status
- `--context` — processing instructions for AI (ralph-loop / session start)
- `--json` — machine-readable output
- `--workspace-root <path>` — override workspace root (defaults to CWD)

**`--context` output** (the critical piece — tells AI what to do):
```
AUTONOMOUS LIFECYCLE REVIEW TRIGGERED
==================================================
N review request(s) in .lifecycle-reviews/inbox/

Steps:
1. For each review (priority: critical > overdue > due):
   a. Read the document at {doc_path} FULLY
   b. Compare against current workspace state
   c. If NO changes needed: run supabase-sync.py push-lifecycle to mark reviewed
   d. If changes needed: write draft to .lifecycle-reviews/drafts/{slug}.md
   e. Move request from inbox/ to processed/
2. After all reviews: send Telegram notification via Sentinel's telegram-send.py
3. Do NOT modify actual documents -- drafts only

PENDING REVIEWS:
  [OVERDUE] pricing-strategy.md (12d overdue, pricing)
    Check: Verify all package prices are current
```

**Exit codes:** 0 = empty inbox, 1 = reviews found

### 2C. Review Processing Workflow

**New file:** `3.- Skill Management Hub/workflows/lifecycle-review-processing.md`

The autonomous review procedure. Key difference from `gap-processing.md`: this is **semi-autonomous** — creates drafts, does NOT auto-modify documents.

**Procedure per review request:**
1. Read the document fully
2. Pull workspace context (recent activity, brain memories if available)
3. Compare each section's claims against current state
4. Decision:
   - **Accurate:** Skip draft. Run `supabase-sync.py push-lifecycle <doc_path> last_reviewed=now escalation_state=current last_review_outcome=confirmed`
   - **Changes needed:** Write draft to `.lifecycle-reviews/drafts/{slug}.md`
5. Move request from `inbox/` to `processed/` (add resolution fields)
6. After all reviews: Telegram via `python "4.- Sentinel/tools/telegram-send.py" "message"`

**Draft file format:**
```markdown
# Review Draft: pricing-strategy.md

**Reviewed:** 2026-04-07T07:15:00Z  |  **Status:** CHANGES NEEDED
**Escalation:** overdue (12 days)  |  **Category:** pricing

## Findings

### Package Pricing
- **Doc states:** "Starter package: $500/month"
- **Current reality:** Recent Acme Corp proposal quoted $650/month
- **Recommendation:** Update to $650/month

### Discount Policy
- **Status:** Still accurate

## Proposed Changes
[Updated content or diff-style patches]
```

### 2D. Ralph-Scheduler Integration

**Edit:** `4.- Sentinel/tools/ralph-scheduler.py` — add entry after `freshness-audit`:

```python
{
    "name": "lifecycle-dispatch",
    "command": ["python", "tools/dispatch-lifecycle-reviews.py", "dispatch"],
    "time_ct": "02:15",  # 15 min after freshness audit
    "description": "Dispatch lifecycle review requests to workspaces",
},
```

### 2E. Directory Setup (per workspace)

```
{workspace}/.lifecycle-reviews/
  inbox/       ← review request JSONs land here
  drafts/      ← AI-generated draft updates saved here
  processed/   ← completed requests moved here
```

Created automatically by `dispatch-lifecycle-reviews.py` on first dispatch.

### 2F. CLAUDE.md Updates (each workspace)

Add to each workspace's Session Start Protocol:

**Skill Hub** (after gap inbox check, step 4):
```
4b. **Check lifecycle reviews**: Run lifecycle-review-watcher.py --context
    If reviews pending: process using document-lifecycle skill + lifecycle-review-processing.md
    If empty: proceed normally
```

**Also update Skill Hub's ralph-loop instruction** to include:
```
Also check .lifecycle-reviews/inbox/ for lifecycle reviews. If any exist, run lifecycle-review-watcher.py --context, then follow lifecycle-review-processing.md.
```

**HQ, Sentinel, AIOS Builder** — add similar session start check, referencing watcher by absolute path.

---

## Files Summary

| File | Action | Where | Lines |
|------|--------|-------|-------|
| `~/.claude/hooks/session-start-lifecycle.py` | CREATE | Phase 1 | ~120 |
| `~/.claude/settings.json` | EDIT | Phase 1 | +10 |
| `~/.claude/hooks/daily-freshness-check.bat` | CREATE | Phase 1+2 | 4 |
| Windows Task Scheduler entry | CREATE | Phase 1 | CLI |
| `4.- Sentinel/tools/dispatch-lifecycle-reviews.py` | CREATE | Phase 2 | ~180 |
| `3.- Skill Hub/tools/lifecycle-review-watcher.py` | CREATE | Phase 2 | ~150 |
| `3.- Skill Hub/workflows/lifecycle-review-processing.md` | CREATE | Phase 2 | ~120 |
| `4.- Sentinel/tools/ralph-scheduler.py` | EDIT | Phase 2 | +6 |
| `3.- Skill Hub/CLAUDE.md` | EDIT | Phase 2 | +5 |
| Other workspace CLAUDE.md files | EDIT | Phase 2 | +3 each |

## Reference Files (read-only patterns)

| File | Reuse For |
|------|-----------|
| `4.- Sentinel/tools/freshness-auditor.py` | Supabase queries, CATEGORY_RISKS, escalation, Telegram |
| `3.- Skill Hub/tools/gap-watcher.py` | Watcher structure, --context output, ralph-loop integration |
| `3.- Skill Hub/workflows/gap-processing.md` | Workflow structure, autonomous processing pattern |
| `3.- Skill Hub/tools/notify-workspaces.py` | Workspace discovery, notification writing |
| `4.- Sentinel/tools/gap-inbox-monitor.py` | WORKSPACE_ROOTS mapping pattern |
| `3.- Skill Hub/tools/supabase-sync.py` | detect_workspace() names, push-lifecycle command |

## Implementation Order

1. **Phase 1A-1B:** SessionStart hook + settings.json edit
2. **Phase 2A:** `dispatch-lifecycle-reviews.py` (Sentinel) — test with `status` (dry run)
3. **Phase 2B:** `lifecycle-review-watcher.py` (Skill Hub) — test with manual inbox JSON
4. **Phase 2C:** `lifecycle-review-processing.md` workflow
5. **Phase 1C:** `daily-freshness-check.bat` + Task Scheduler (includes dispatch call)
6. **Phase 2D:** Ralph-scheduler entry
7. **Phase 2E-2F:** Directory creation + CLAUDE.md updates
8. **End-to-end test:** Manually set a doc's next_review to past date → run dispatch → open workspace → verify watcher fires → verify draft created

## Verification

1. **SessionStart hook:** New session → `.tmp/doc-lifecycle-cache.json` refreshed
2. **Dispatcher dry run:** `python dispatch-lifecycle-reviews.py status` → shows what would dispatch
3. **Dispatcher live:** Manually backdate a doc → run dispatch → check workspace inbox
4. **Watcher:** Place test JSON in inbox → run `--context` → verify output
5. **End-to-end:** Dispatch → open workspace → AI reviews → draft appears → Telegram sent
6. **Daily check:** Double-click .bat → verify check + dispatch both run
7. **Task Scheduler:** `schtasks /query /tn "Claude-DocLifecycle-DailyCheck"` → verify exists
