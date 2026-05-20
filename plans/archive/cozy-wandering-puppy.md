# Plan: Unified Work Request System

## Context

Skill Hub receives inbound work through two overlapping systems: `.gap-reports/` (capability gaps) and `.routed-tasks/` (generic cross-workspace routing). This causes duplicate reports, unclear boundaries, and confusion. Consolidating to a single inbound channel with expanded work types preserves the proven workflow while eliminating overlap.

**Full design spec:** `docs/superpowers/specs/2026-04-14-unified-work-request-system-design.md`

## Summary of Changes

- Rename `.gap-reports/` to `.work-requests/` (inbox/, processed/, outbox/)
- Rename `deferred/` to `outbox/` (routed-elsewhere items + audit trails)
- Expand `gap-reporter.py` to `work-request.py` with 6 types: MISSING, UNUSED, FALLBACK, TASK, BUG, ENHANCE
- Rename `gap-watcher.py` to `request-watcher.py`
- Rename `gap-processing.md` to `work-request-processing.md`
- Kill `.routed-tasks/` from Skill Hub entirely
- Update 44 files across all workspaces (see spec Tiers 1-5)
- HQ/Sentinel keep `.routed-tasks/` (still receive from Skill Hub)
- `.lifecycle-reviews/` stays separate everywhere

## Implementation Phases

### Phase 1: Core Infrastructure (Skill Hub)
1. Rename directories: `.gap-reports/` to `.work-requests/`, `deferred/` to `outbox/`
2. Move `.routed-tasks/outbox/*.md` to `.work-requests/outbox/`
3. Move `.routed-tasks/inbox/*.json` to `.work-requests/inbox/`
4. Archive `.routed-tasks/processed/` then delete `.routed-tasks/`
5. Create `~/.claude/scripts/work-request.py` (copy gap-reporter.py, expand types, update paths)
6. Create `tools/request-watcher.py` (copy gap-watcher.py, update paths)
7. Create `workflows/work-request-processing.md` (copy gap-processing.md, expand classification)
8. Test: run work-request.py, verify inbox, run request-watcher.py

### Phase 2: Global Infrastructure
9. Update `~/.claude/hooks/session-startup-guard.py` (inbox path + labels + CronCreate prompt)
10. Update `~/.claude/rules/universal-protocols.md` (rename protocol, update examples/paths)
11. Update `~/.claude/skills/resource-auditor/SKILL.md` (gap-reporter reference)
12. Update `~/.claude/skills/session-checkpoint/references/full-checkout-protocol.md`
13. Update `~/.claude/skills/deep-interview/SKILL.md` (if gap-reporter referenced)
14. Update `~/.claude/scripts/doc-cache-builder.py` (if .gap-reports referenced)

### Phase 3: Skill Hub Docs + Workflows
15. Update `CLAUDE.md` (all gap-reports/gap-reporter/gap-watcher/gap-processing references)
16. Update `docs/specs/` files (6 spec files, rename spec-gap-pipeline and spec-gap-reporter)
17. Update `workflows/` files (autonomous-loop, cron-schedule, marketplace-evaluation, annealing-protocol, project-setup, lifecycle-review-processing)
18. Update/delete decommissioned tools (gap-inbox-alert.py, sched-gap-alert.bat)
19. Update `tools/bootstrap.py`
20. Delete old scripts: `~/.claude/scripts/gap-reporter.py`, `tools/gap-watcher.py`, `workflows/gap-processing.md`

### Phase 4: Other Workspaces
21. Update Sentinel `CLAUDE.md` (2 references)
22. Update Sentinel `tools/gap-inbox-monitor.py` and `tools/brief-generator.py`
23. Update Sentinel `docs/specs/` (evening-report, morning-report, dream-consolidation)
24. Update Sentinel `workflows/cron-schedule.md`
25. Update HQ `workflows/cron-schedule.md` and `workflows/lifecycle-review-processing.md`

### Phase 5: Memory + Cleanup
26. Update Skill Hub `MEMORY.md` (infrastructure section)
27. Update Sentinel `MEMORY.md`
28. Update memory topic files (feedback_idle_process_everything, feedback_mid_session_triage, feedback_audit_gap_filing, phase5c_infrastructure_fixes)
29. Delete old files after verifying new ones work

### Phase 6: Verification
30. Run work-request.py test (new report lands in inbox)
31. Run request-watcher.py test (finds report)
32. Startup guard test (new chat detects inbox)
33. Outbound routing test (route to Sentinel)
34. Cross-workspace test (Sentinel sends to Skill Hub)
35. Reference scan: grep for old names across all workspaces (zero hits = done)
36. Process one real work request end-to-end

## Critical Files

- `~/.claude/scripts/gap-reporter.py` --> `~/.claude/scripts/work-request.py`
- `tools/gap-watcher.py` --> `tools/request-watcher.py`
- `workflows/gap-processing.md` --> `workflows/work-request-processing.md`
- `~/.claude/hooks/session-startup-guard.py`
- `~/.claude/rules/universal-protocols.md`
- `CLAUDE.md` (Skill Hub)
- Sentinel `CLAUDE.md`, `tools/gap-inbox-monitor.py`, `tools/brief-generator.py`

## Risks + Mitigations

| Risk | Mitigation |
|------|-----------|
| Stale reference breaks a workspace | Exhaustive file list in spec (44 files). Reference scan in Phase 6. |
| CronCreate prompt outdated | Update in startup guard AND recreate during this session. |
| Other workspaces call old gap-reporter.py | Delete old script only AFTER updating all callers. |
| Historical processed files have old schema fields | Don't modify them. They're historical records. New files use expanded schema. |
