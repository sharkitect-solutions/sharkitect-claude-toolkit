# Phase 6A: Supabase Scrub — Sentinel Audit Report
**Date:** 2026-04-15
**Auditor:** Sentinel workspace
**Status:** COMPLETE

---

## Database Inventory (24 tables)

| Table | Rows | Owner | Audit Status |
|-------|------|-------|-------------|
| `memories` | 713 (462 active, 251 inactive) | Sentinel | CLEAN |
| `system_health` | 12 | Sentinel | CLEAN |
| `activity_stream` | 215 | Sentinel | FIXED |
| `doc_lifecycle` | 94 | Sentinel | CLEAN |
| `dream_log` | 5 | Sentinel | CLEAN |
| `briefs` | 1 | HQ/Sentinel | DECISION MADE |
| `projects` | 14 | All workspaces | FIXED |
| `tasks` | 102 (was 103) | All workspaces | FIXED |
| `lessons_learned` | 0 | Skill Hub | EXPECTED (6B populates) |
| `work_requests` | 1 | Skill Hub | FLAGGED |
| `error_fixes` | 3 | HQ | NOTED |
| `sessions` | 5 | — | NOT AUDITED (low priority) |
| `kb_docs` | 69 | — | NOT AUDITED (low priority) |
| `logs` | 163 | — | NOT AUDITED (low priority) |
| `audit_log` | 99 | Sentinel | CLEAN |
| `voice_samples` | 34 | HQ | NOT AUDITED |
| `repo_findings` | 4 | Sentinel | CLEAN |
| `clients` | 1 | HQ | NOT AUDITED |
| `documents` | 0 | — | EMPTY (Phase 7) |
| `document_relationships` | 0 | — | EMPTY (Phase 7) |
| `user_preferences` | 0 | — | EMPTY (Phase 7) |
| `system_specs` | 0 | — | EMPTY (Phase 7) |
| `sync_conflicts` | 0 | — | EMPTY (Phase 7) |
| `automation_registry` | 0 | — | EMPTY (Phase 7) |

---

## Findings & Fixes

### 1. NON-CANONICAL WORKSPACE NAMES (FIXED)

**Problem:** Multiple tables used `hq` instead of `workforce-hq`, `autonomous-operations` instead of `sentinel`, and `global` for cross-workspace items.

**Fixes applied:**
- `projects.workspace`: 12 rows `hq` → `workforce-hq`
- `tasks.assigned_workspace`: 77 rows `hq` → `workforce-hq`
- `activity_stream.workspace`: 9 rows `autonomous-operations` → `sentinel`

**Intentional exceptions (NOT fixed):**
- `projects.workspace = 'global'`: 1 record (Foundation Reset) — genuinely cross-workspace
- `tasks.workspace = 'global'`: 11 records (Foundation Reset tasks) — genuinely cross-workspace
- `memories.workspace = 'shared'`: 7 records — **FIXED (2026-04-15):** migrated to `global`. `shared` was redundant with `global`, violating KISS principle.

**Recommendation for 6D:** Add a CHECK constraint or trigger to prevent non-canonical workspace names from being inserted. **DONE (2026-04-15):** CHECK constraints added on projects, tasks, activity_stream, doc_lifecycle. Allowed values: `workforce-hq`, `skill-management-hub`, `sentinel`, `global`.

### 2. ORPHANED TASK DELETED

**Problem:** 1 task referenced project `Briefing System Rebuild` which doesn't exist in the `projects` table.
- Task: "Stage 3.6 verification test task" (status: completed, orphaned)
- **Fix:** Deleted. It was a completed test task with no ongoing value.

### 3. MEMORIES TABLE — HEALTHY

- **713 total** (462 active, 251 inactive)
- **No stale memories** (all active memories accessed within 90 days)
- **No duplicate keys** among active memories
- **Workspace distribution:** workforce-hq dominates (584), skill-management-hub (95), sentinel (27), global (7, migrated from 'shared')
- **15 categories** in use: decision (134), rule (114), lesson (129), fact (35), preference (17), task (20), workflow (5), and 8 minor categories
- **No non-canonical workspace names** in this table

**Observation:** The 251 inactive memories were properly deactivated by dream consolidation. No action needed.

### 4. SYSTEM_HEALTH TABLE — ALL 12 COMPONENTS VERIFIED

| Component | Status | Last Heartbeat | Assessment |
|-----------|--------|----------------|------------|
| sentinel-health-check | healthy | 2026-04-15 22:00 UTC | Current |
| work-request-pipeline | healthy | 2026-04-15 21:13 UTC | Current |
| skill-management-hub-sync | healthy | 2026-04-15 19:37 UTC | Current |
| workforce-hq-sync | healthy | 2026-04-15 17:45 UTC | Current |
| sentinel-sync | healthy | 2026-04-15 16:58 UTC | Current |
| sentinel-session | healthy | 2026-04-15 16:56 UTC | Current |
| n8n-watcher | healthy | 2026-04-15 14:00 UTC | Current |
| sentinel-brief | healthy | 2026-04-15 10:00 UTC | Current |
| freshness-auditor | healthy | 2026-04-15 09:00 UTC | Current |
| nightly-dream | healthy | 2026-04-15 08:03 UTC | Current |
| sentinel-evening | healthy | 2026-04-15 03:00 UTC | Current |
| sentinel-repo-monitor | healthy | 2026-04-13 01:00 UTC | OK (weekly cadence — next run Sunday) |

**All components exist and are actively heartbeating.** No decommissioned systems found. No stale heartbeats.

### 5. ACTIVITY_STREAM — EVENT TYPES REVIEWED

15 event types in use (215 total events):

| Event Type | Count | Assessment |
|------------|-------|------------|
| session_end | 74 | Standard |
| session_brief | 66 | Standard |
| correction | 29 | Standard |
| brief_generated | 15 | Standard |
| brief_sent | 12 | Standard |
| session_complete | 4 | Standard |
| voice_capture | 4 | Standard |
| phase_complete | 3 | Standard |
| dream_cycle_complete | 2 | Standard |
| work_request_created | 1 | Standard |
| sentinel-instantiation | 1 | Non-standard naming (hyphen) |
| dream_consolidation | 1 | Standard |
| phase4b-deployed | 1 | Non-standard naming (hyphen) |
| session-checkpoint | 1 | Non-standard naming (hyphen) |
| sentinel-session-close | 1 | Non-standard naming (hyphen) |

**Finding:** 4 event types use hyphens instead of underscores. Low-impact (only 4 events total), but recommend standardizing to underscores in future writes for consistency with documentation-standards.md.

### 6. DOC_LIFECYCLE — CLEAN

- 94 tracked documents (all `is_active = true`, all `escalation_state = 'current'`)
- Distribution: workforce-hq (77), skill-management-hub (14), sentinel (3)
- Sentinel's 3 tracked docs verified: `CLAUDE.md`, `workflows/project-setup.md`, `workflows/skills-evaluation.md`
- **Observation:** Only 3 sentinel docs tracked. Many sentinel docs (specs, workflows) are NOT in the lifecycle system. This is a 6E proactive finding.

### 7. DREAM_LOG — HEALTHY

- 5 entries, running since 2026-04-03
- Latest run: 2026-04-15 08:03 UTC (today) — 0 duplicates, 0 contradictions, 1 stale flagged, 1 voice rule synthesized, 3 patterns extracted
- Consistent nightly execution since Apr 12 (before that, gap from Apr 3-12)
- Dream consolidation is working as designed

### 8. BRIEFS TABLE — RECOMMENDATION

**Current state:** 1 record (morning brief from 2026-04-08).

**Recommendation: KEEP the table.** Rationale:
- `activity_stream` is an event log ("brief was generated at X"). It captures *that* a brief happened.
- `briefs` should store the *actual content* of each brief for historical reference and analysis.
- HQ owns the n8n workflow fix (routed task `rt-2026-04-15-briefs-table-not-populated`).
- Once HQ fixes the workflow to INSERT here, this becomes the historical brief archive.

### 9. PROJECTS — CROSS-WORKSPACE REVIEW

14 projects total:
- **Active (3):** Foundation Reset (global), SystemLink (workforce-hq), Emmanuel FF Admin Database (workforce-hq)
- **Complete (2):** Founder-Grade Briefing System, Update GBP — both >7 days old but <90 days, no archival needed yet
- **Paused (3):** Voice AI, Alex Personal Assistant, Unified AI Workforce — all tabled/low priority, correct
- **Pending (3):** Educational Meetings, Social Media Optimization, YouTube+Repo Intelligence Pipeline
- **Tabled (3):** Email Response Automation, TMC Data Analyst MVP, AI Operating System

**Status accuracy:** Foundation Reset shows "Phase 6: Clean and Guard" — correct for today's work.

### 10. TASKS — CROSS-WORKSPACE REVIEW

102 tasks (after deleting 1 orphan):
- workforce-hq: 81 total (62 completed, 5 pending, 2 blocked, 2 deferred, 10 tabled)
- skill-management-hub: 14 total (9 completed, 5 pending)
- sentinel: 7 total (2 completed, 4 pending, 1 tabled)

**No tasks completed >90 days ago** (system is young enough that nothing has aged out).

### 11. WORK_REQUESTS TABLE — FLAGGED

1 record: "Build client onboarding email sequence using voice profile" (from skill-management-hub → workforce-hq, status: deferred, created 2026-04-03).

**Issue:** This is 12 days old and deferred with no response. Skill Hub should validate whether this is still relevant or should be archived. Not Sentinel's data to fix, but flagged for Skill Hub.

### 12. ERROR_FIXES TABLE — NOTED

3 records (HQ validates):
- 2 from "Watcher's Watcher" (1 solved, 1 blocked) — April 8
- 1 from "CEO Daily Briefs" (blocked) — April 13

The blocked CEO Brief error may relate to the briefs table gap. HQ to verify.

### 13. EMPTY PHASE 7 TABLES — EXPECTED

6 tables are empty and awaiting Phase 7 population:
`documents`, `document_relationships`, `user_preferences`, `system_specs`, `sync_conflicts`, `automation_registry`

These are correctly empty — schemas exist, population happens in Phase 7.

---

## Verification Query Results

### Projects by Workspace and Status
```
global          | active   | 1
skill-mgmt-hub  | pending  | 1
workforce-hq    | active   | 2
workforce-hq    | complete | 2
workforce-hq    | paused   | 3
workforce-hq    | pending  | 2
workforce-hq    | tabled   | 3
```

### Tasks by Assigned Workspace and Status
```
sentinel            | completed | 2
sentinel            | pending   | 4
sentinel            | tabled    | 1
skill-mgmt-hub      | completed | 9
skill-mgmt-hub      | pending   | 5
workforce-hq        | blocked   | 2
workforce-hq        | completed | 62
workforce-hq        | deferred  | 2
workforce-hq        | pending   | 5
workforce-hq        | tabled    | 10
```

---

## Summary of Actions Taken

| Action | Count | Details |
|--------|-------|---------|
| Workspace names fixed | 98 rows | 12 projects + 77 tasks + 9 activity_stream events |
| Orphaned tasks deleted | 1 | "Stage 3.6 verification test task" |
| Tables audited | 17 | All owned tables + cross-workspace audit |
| Issues flagged for other workspaces | 3 | work_requests staleness (Skill Hub), error_fixes blocked (HQ), briefs population (HQ) |

---

## Proactive Findings (6E Preview)

1. **Sentinel doc_lifecycle gap:** Only 3 sentinel documents tracked in doc_lifecycle. Sentinel has 6+ spec docs, multiple workflow files, and tool scripts that should be tracked for freshness. Recommend registering all sentinel specs and key workflows.

2. **Event type naming inconsistency:** 4 activity_stream event types use hyphens instead of underscores. Recommend a guardrail (6D) that normalizes event_type to underscore format on write.

3. **No CHECK constraint on workspace columns:** Any string can be written to workspace fields. A CHECK or enum constraint would prevent future non-canonical names. Recommend implementing in 6D.
