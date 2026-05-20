---
name: AIOS Coordination Fix — Strategic Build
status: active
priority: critical
owner: sentinel
owner_workspace: cross-workspace
keywords: [aios, coordination, dependencies, blocker-surfacing, register-plan, parent-task-id, drift-detection, discipline-hooks, q3-architectural-decision]
created_at: 2026-05-08
last_updated_by: sentinel
---

# AIOS Coordination Fix — Strategic Build (Master Plan)

> save progress quickly — locked in 2026-05-08 end of session, queued for execution next session.

## Why this exists

User reported 2026-05-08: "no notifications anywhere", "everything pending", "nothing blocked", "AIOS plan unclear". Sentinel audit (`docs/audits/aios-coordination-audit-2026-05-08.md`) confirmed:

- 310 total tasks across all projects; only 11 (3.5%) have `depends_on` populated
- Zero tasks currently `status='blocked'`
- Held AIOS architectural package invisible — no task carries it as blocker
- Parent-task progress doesn't roll up from sub-scope work
- `register-plan.py` doesn't auto-create tasks with deps; manual two-step

The Supabase data model has the right fields. The discipline doesn't populate them. This plan fixes the system that makes architectural decisions observable BEFORE the next architectural decision (Q3) is made.

## Strategic ordering principle

User direction (verbatim, 2026-05-08): *"Fix the issue first. Backfill everything that needs to be backfilled. Rename project A. Make sure everything on those things is done first. For the iOS architect decision, everything needs to be done prior to that, because that is dependent on everything else. Once we name everything, link everything up, backfill everything, and connect everything, they will have a straight picture of what needs to happen before that, what needs to happen before the next step."*

Architectural decisions made in unobservable systems are bad decisions. Build the observability and coordination infrastructure FIRST. Then decide Q3 with the full chain visible.

## The 9-step build order

### Phase 1 — Build the coordination capability

**1. F3 — Add `parent_task_id` field to RT/WR/lifecycle schemas + tooling** [SCRIPT-SIDE SHIPPED 2026-05-08 S34; schema migration awaiting Sentinel]
- Owner: Skill Hub
- Deliverable: schema migration adds `parent_task_id uuid` to `cross_workspace_requests` (and any other inbox-related tables). Updates `close-inbox-item.py` and `work-request.py` to accept and persist the field.
- Why first: F1 and F8 BOTH require this field. Building F1 without F3 means retrofitting later.
- Filed via: `wr-skillhub-2026-05-08-005`
- **Status (2026-05-08 S34):** Script-side three-gate enforcement SHIPPED via TDD (12 tests GREEN, 78/78 related no regressions). work-request.py + close-inbox-item.py + inbox-json-validate.py all accept `--parent-task-id` with UUID validation. Spec at `3.- Skill Management Hub/docs/superpowers/specs/2026-05-08-parent-task-id-field-design.md`. universal-protocols.md schema contract updated (with user authorization). Schema migration RT routed to Sentinel: `4.- Sentinel/.routed-tasks/inbox/rt-skillhub-2026-05-08-f3-parent-task-id-schema-migration.json`. PENDING: (a) Sentinel ALTER TABLE + index + COMMENT, (b) Skill Hub flips 1-block uncomment in close-inbox-item.py update_supabase to enable Supabase write, (c) parent-task progress rollup (auto-append to tasks.notes on close). When all 3 land + verified, parent WR `wr-skillhub-2026-05-08-001` closes.

**2. F1 — Auto-generate tasks + dependencies from plan files**
- Owner: Sentinel
- Deliverable: `register-plan.py` upgraded to parse plan markdown for phase markers, owner declarations, and trigger conditions; creates matching `tasks` rows with `assigned_workspace`, `phase`, `depends_on`, `parent_task_id` (when applicable), `notes`. Idempotent.
- Why second: depends on F3.

### Phase 2 — Apply to existing data

**3. F4 — Backfill: re-run `register-plan` against every multi-phase plan; encode all dependency chains; mark Phase 1 (AIOS Build) blocked-by-Q3-package**
- Owner: Sentinel
- Why third: depends on F1's idempotent re-run capability.

**4. F5 — Rename Project A: "AI Operating System (AIOS)" → "AIOS — Contrarian Truth Cascade (Marketing)"**
- Owner: HQ
- Why fourth: parallel-safe with #3. Filed via: `rt-sentinel-2026-05-08-rename-project-a-marketing-cascade`

### Phase 3 — Visibility + enforcement layer

**5. F2 — Surface held cross-workspace blockers at session start** (Skill Hub) — depends on F4 + F5

**6. F6 — Sentinel audit drift class: phase tasks without dependencies** (Sentinel) — parallel-safe with #5

**7. F7 — Stale held-item escalation** (Sentinel) — depends on F2 (#5)

**8. F8 — Discipline hooks: nag when status updates / parent linkage skipped** (Skill Hub) — parallel-safe with #5/#6/#7; depends on F3 + F1

### Phase 4 — Decide with full blueprint

**9. Q3 — AIOS architectural decision: separate `sharkitect-aios-central-hub` project vs reuse `sharkitect-brain`**
- Owner: User (with `superpowers:brainstorming` support)
- Why ninth: by this point, dashboard shows full Phase 1 → 10 chain with owners, deps, blocked status. Decision made with complete context.

## Parallel-safe paths

- **#3 + #4** in parallel (HQ rename independent of Sentinel backfill)
- **#5 + #6 + #8** in parallel (different owners; surface, detect, enforce)
- **#7** depends on #5

## Acceptance criteria

**Phase 1:**
- [ ] `parent_task_id` column exists on `cross_workspace_requests`; `close-inbox-item.py` + `work-request.py` accept the field
- [ ] `register-plan.py` parses phase structure and creates tasks with `depends_on` chain
- [ ] Idempotency test: re-running on existing plan does not duplicate or clobber

**Phase 2:**
- [ ] AIOS Build project shows full dependency chain Phase 1 → 10
- [ ] AIOS Build Phase 1 is `status='blocked'` with `blocked_by` referencing the held AIOS sentinel package
- [ ] Project A renamed
- [ ] Other multi-phase plans backfilled (or explicitly exempt)

**Phase 3:**
- [ ] Session startup surfaces held cross-workspace blockers (Step 3.6)
- [ ] Morning report shows `phase_task_missing_dependency` drift count
- [ ] Stale held items >3d surface in brief; >7d trigger user notification
- [ ] Discipline hooks fire when sub-scope work closes without parent linkage

**Phase 4:**
- [ ] Q3 decision recorded
- [ ] AIOS Build Phase 1 unblocked or retargeted
- [ ] Held AIOS sentinel package closed

## Cross-workspace deliveries queued

| ID | Type | To | Subject |
|----|------|-----|---------|
| `wr-skillhub-2026-05-08-005` | Work Request | Skill Hub | F3 — parent_task_id schema + tooling |
| `rt-sentinel-2026-05-08-rename-project-a-marketing-cascade` | Routed Task | HQ | F5 — rename Project A |
| (queued for after F1) | WR | Skill Hub | F2 — held-blocker surfacing |
| (queued for after F1) | WR | Skill Hub | F8 — discipline hooks |

## Resume instructions

Next session: open against item #1. F3 WR is in Skill Hub's `.work-requests/inbox/`; F5 RT is in HQ's `.routed-tasks/inbox/`. Both picked up at those workspaces' session-start.

Sentinel-side work (#2 F1, #3 F4, #6 F6, #7 F7) tracked as Supabase tasks under this project. Sentinel resumes by querying tasks under this project ordered by `depends_on`.
