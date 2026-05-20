---
status: ACTIVE (Phase A + C complete; B shipped concurrent with A; D + E pending HQ collaboration + user decision)
created: 2026-05-18
last_updated: 2026-05-19
last_updated_by: chris+claude
type: arc-plan
owner: sentinel
phases: A, B, C, D, E
phase_plans:
  - phase_a: ~/.claude/plans/2026-05-18-priority-inference-phase-a.md
classification: arc-plan (multi-subsystem; individual phase plans use strict writing-plans task/step structure)
trigger_source: User pushback message 2026-05-18 S57 on Weekly Review v0.2 smoke output — "no yes agents... report has to earn its place"
trigger_ref: session_2026_05_17_phase2_task2_1_locked.md (S56-B continuation, S57 redesign discussion)
related_spec: 4.- Sentinel/docs/specs/spec-weekly-sentinel-review.md (v1.1 APPROVED 2026-05-19)
related_plan: 4.- Sentinel/docs/plans/2026-05-05-sentinel-reports-restructure.md (parent — Phase 2 Task 2.4 closed 2026-05-19; project rolled to 16/16)
phase_c_shipped_commits: ["fa60ec1 (Weekly Review v1.1)", "abf4a17 (Report Optimization Methodology codification)"]
---

# Cross-Workspace Priority Inference + Weekly Review v1.0 (ARC PLAN)

**This is an ARC document.** Covers 5 phases (A-E) spanning Sentinel + HQ + each workspace.
Per writing-plans scope-check rule (multi-subsystem plans → break into per-phase plans),
each phase has (or will have) its own detailed task-level plan when execution begins.

**Status anchor:** Phase A in flight (S57, autonomous). Phase A detail plan: see frontmatter `phase_a`.

**Owner:** Sentinel (inference + storage); HQ (goal definitions); each workspace (reader)
**Source:** User direction 2026-05-18 — "the system should already know based on context, it should be smart enough to identify priorities... AI infers, user corrects only if wrong"

## Why this exists

Two problems the operation faces:

1. **No formal priority hierarchy across projects.** Many projects exist; `project.priority` is set per-project somewhat arbitrarily; no clear "these 3-5 are THE strategic focus right now, everything else is support." User correctly identified: without this, the Weekly Sentinel Review can't detect drift because there's no anchor to drift from.

2. **Manual priority tagging would create friction the user explicitly rejects.** "The system should already know" — AI has enough signal to infer priorities from conversation context, activity patterns, goal alignment, cross-workspace involvement, etc.

The solution: AI inference + 30-60 second user validation per week + persisted overrides.

## End state

- A computed, ranked, tiered priority list maintained by Sentinel, available to all workspaces
- Five tiers: T1 Strategic Focus / T2 Defensive Critical / T3 Core Operations / T4 Maintenance / T5 Exploratory
- Cross-workspace projects automatically get precedence (signal-driven, not manual)
- Weekly Review v1.0 (3 sections + 1 conditional) anchored on the inference
- User corrections persisted with TTL; AI learns over time

## Phase A — Sentinel-side inference engine + storage (autonomous, this session)

| Task | Deliverable | Owner |
|---|---|---|
| A.1 | Pause Task 2.4 signoff (Reports Restructure) — blocked on priority system | Sentinel ✅ |
| A.2 | Write this plan + register in plans-registry | Sentinel ✅ |
| A.3 | File routed-task to HQ: priority_focus proposal + goal-tagging UX | Sentinel |
| A.4 | Design `priority_overrides` Supabase table schema (draft migration) | Sentinel |
| A.5 | TDD `compute_priority_tiers()` function (pure logic) — signal stack defined in plan | Sentinel |
| A.6 | Wire `compute_priority_tiers()` to live Supabase data | Sentinel |
| A.7 | Smoke-test inference output against today's real data; review tier assignments | Sentinel |
| A.8 | Commit + push Phase A; update Sentinel schema index | Sentinel |

### Signal stack for inference (Phase A.5)

`compute_priority_tiers(projects, goals, activity, voice_samples, overrides) -> List[TierAssignment]`

Each project scored by weighted signals:

| Signal | Weight | Source |
|---|---|---|
| Goal-alignment (project ladders to active goal) | +5 | `public.goals` rows referencing project |
| Cross-workspace involvement | +3 | project metadata + activity across workspaces |
| Recent activity (last 14d weighted) | +2 per active day | `public.activity_stream`, `public.tasks.updated_at` |
| Blocker count (projects this one blocks) | +2 per blocked downstream | `tasks.blocked_by` + `cross_workspace_requests.blocked_by` |
| Deadline proximity (<30 days) | +3 | `projects.deadline` (if present) |
| Recent user mentions in voice samples | +2 | `voice_samples` last 14d |
| Explicit `is_strategic_focus` (HQ-set, when available) | +5 | future HQ field |
| User override (current period) | overrides all | `priority_overrides` table |

Tier assignment (after scoring):
- Top 3-5 by score, with score ≥ 8 → **T1 Strategic Focus**
- Score ≥ 6 AND deadline <14 days OR active blocker → **T2 Defensive Critical**
- Score ≥ 4 AND active status → **T3 Core Operations**
- Score 1-3 OR maintenance-typed → **T4 Maintenance**
- Score 0 OR status in (deferred, paused, tabled) → **T5 Exploratory / Parked**

Cap T1 at 5 by design (per ceo-advisor: strategy is saying NO). Excess T1-eligible projects spill to T2.

### priority_overrides schema (Phase A.4 draft)

```sql
CREATE TABLE public.priority_overrides (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  tier text NOT NULL CHECK (tier IN ('T1', 'T2', 'T3', 'T4', 'T5')),
  reason text NOT NULL,                    -- short explanation user gave when overriding
  set_by text NOT NULL,                    -- 'user' | workspace canonical name
  set_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL DEFAULT (now() + interval '30 days'),
  active boolean NOT NULL DEFAULT true,
  notes text,
  tenant_id uuid REFERENCES public.tenants(id) DEFAULT '00000000-0000-0000-0000-000000000001'
);
CREATE INDEX priority_overrides_project_active ON public.priority_overrides(project_id) WHERE active = true;
CREATE INDEX priority_overrides_expires_at ON public.priority_overrides(expires_at) WHERE active = true;
```

RLS: enabled, service-role full access (per Sentinel-owned-tables pattern). Migration name: `add_priority_overrides_2026_05_18`.

## Phase B — Schema deployment (autonomous after Phase A review)

| Task | Deliverable |
|---|---|
| B.1 | Apply `add_priority_overrides_2026_05_18` migration |
| B.2 | Add `priority_overrides` row to `docs/supabase-schema-index.md` |
| B.3 | Verify RLS + indexes + insert/read smoke test |

## Phase C — Weekly Review v1.0+v1.1 (SHIPPED 2026-05-19)

**Status:** ✅ COMPLETE. v1.0 shipped 2026-05-18 (3 sections + 1 conditional anchored on priority-inference). v1.1 shipped 2026-05-19 (executive-grade humanization pass: plain-English workspace names, word-bounded truncation, demoted refs, narrative grouping, stakes-bearing recommendation, warmer Section D header). User signed off Task 2.4 on 2026-05-19. Parent project (Reports Restructure) rolled to 16/16 complete via cascade trigger. Commits: `fa60ec1` (v1.1) + `abf4a17` (Report Optimization Methodology codification).

**Methodology codified:** The v1.0→v1.1 process is now the standard for any future report optimization. Local SOP at `4.- Sentinel/workflows/report-optimization-methodology.md`. Skill Hub WR `wr-sentinel-2026-05-19-003` filed to package as global auto-invocable skill. HQ FYI routed for CEO Daily Briefs application.

---

### Original task list (historical):



Replace v0.2 6-section structure with the lean v1.0:

| Section | Spec | Notes |
|---|---|---|
| **A. Where the week's work went** | Show inferred T1-T2 ranking + capacity allocation; flag drift when T1 work stalled OR T4+ work consumed >50% of capacity | Forces strategic visibility |
| **B. Decisions waiting on you** | Item-level list with workspace tag + specific decision phrasing + days-waiting | Forces visibility into decision debt |
| **C. One thing to do this week** | Synthesized from A+B with explicit narrative bridge ("→ this is your B-1 item from above") | Forces a single action |
| **(D conditional). System judgment alert** | Only renders when an autonomous decision needs REVIEW or REVERSE; suppressed otherwise | No "everything is fine" noise |

DROPPED: Stale Truth Audit (Sentinel acts on docs autonomously, doesn't surface), Trust Statement ("everything is fine" trap).

Word budget: <250 words (down from 400). Reads in 30 seconds.

| Task | Deliverable |
|---|---|
| C.1 | Delete v0.2 sections being dropped from `weekly-review-generator.py` |
| C.2 | Rebuild Section A as inferred-tier presentation reading `compute_priority_tiers()` output |
| C.3 | Strengthen Section B (decision queue) — workspace tags + specific phrasing |
| C.4 | Strengthen Section C — explicit narrative bridge to Section B |
| C.5 | Make Section D conditional — suppress all-ACCEPT weeks |
| C.6 | Update tests (some current tests cover dropped sections — adjust) |
| C.7 | Smoke test v1.0 against real data |
| C.8 | User review + Task 2.4 signoff |

## Phase D — HQ goal-tagging build (cross-workspace, gated on HQ acceptance)

HQ owns. Sentinel filed routed-task in Phase A.3.

- D.1: HQ confirms goal definitions in `public.goals`
- D.2: HQ adds `is_strategic_focus boolean` field to projects (optional; Phase A signals work without it)
- D.3: Sentinel re-runs inference with HQ-enriched signal; precision should improve

## Phase E — Legacy report retirement

Per original Reports Restructure Phase 5 (unchanged). After Phase C user signoff on v1.0:
- E.1: Retire Morning System Report
- E.2: Retire Evening System Report
- E.3: Retire standalone Repo Monitor
- E.4: Update workflows + automation registry

## Approval gates (NON-NEGOTIABLE)

1. **End of Phase A:** user reviews inference output against today's real projects; corrects tier assignments; confirms 5-tier model still feels right OR requests adjustment to 3-tier.
2. **End of Phase C:** user reviews v1.0 smoke output; signs off on Task 2.4.
3. **End of Phase E:** user reviews retired-report list; confirms no monitoring gap.

## What this is NOT

- Not a quick fix. Realistic timeline: 2-3 focused sessions. Phase A is autonomous-executable today; Phases B-E need either user review or HQ collaboration.
- Not perfect. The signal stack is v1; it WILL miss some priority assignments. The override mechanism is the safety net.
- Not a replacement for HQ's CEO Daily Briefs or other reports. This is the strategic weekly forcing function, not operational status.

## Cross-references

- Spec: `4.- Sentinel/docs/specs/spec-weekly-sentinel-review.md` (v0.2; will bump to v1.0 in Phase C)
- Parent plan: `4.- Sentinel/docs/plans/2026-05-05-sentinel-reports-restructure.md` Phase 2
- Source pushback: User message 2026-05-18 on v0.2 smoke output ("not yes agents... report has to earn its place")

## Source rule alignment

- **CEO Advisor Mandatory Invocation Protocol** (universal-protocols.md): this build is company-affecting; ceo-advisor invoked multiple times in S57 session before locking design
- **Pushback Protocol**: scope shaped by honest pushback on user's "zero-touch inference" idea (proposed AI infers + user 60s validates)
- **Anti-Drift Scope Discipline**: this conversation expanded organically from "ship v0.2" → "redesign sections" → "should report exist" → "no, fix the underlying priority gap first" — user-driven scope refinement, not drift
- **Supabase Ownership Protocol**: priority_overrides table = Sentinel-owned (computed) + HQ-owned goal tagging (strategic) — clean lane separation
- **Hook Introduction Rule**: no new hooks proposed; reusing existing TDD discipline + Sentinel brain pattern
