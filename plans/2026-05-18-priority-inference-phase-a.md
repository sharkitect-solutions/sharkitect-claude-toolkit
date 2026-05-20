---
status: ACTIVE
created: 2026-05-18
last_updated: 2026-05-18
type: phase-plan
owner: sentinel
parent_arc: ~/.claude/plans/2026-05-18-cross-workspace-priority-inference.md
trigger_ref: User S57 pushback message 2026-05-18 on Weekly Review v0.2 smoke
---

# Phase A — Priority Inference Engine + Storage (Sentinel-side)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Author intends to execute INLINE in S57.

**Goal:** Build the Sentinel-side priority inference engine (signal-weighted tier assignment) + corrections storage table, so the Weekly Review v1.0 can anchor on a real strategic priority list instead of accidental signal.

**Architecture:** Pure-function `compute_priority_tiers()` (TDD-testable) consumes Supabase queries + override snapshot, emits ranked tier assignments (T1-T5). New `priority_overrides` table persists user corrections with 30d TTL. Sentinel owns inference + storage; all workspaces read via brain queries.

**Tech Stack:** Python 3.12 + stdlib (urllib REST) — mirrors existing `tools/ops-brain.py` pattern. Supabase Postgres + RLS. Migration via Supabase MCP.

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `tools/priority-inference.py` | CREATE | `compute_priority_tiers()` + signal scoring + Supabase brain queries |
| `tests/test_priority_inference.py` | CREATE | Pure-function unit tests (scoring, tier assignment, override merge) |
| Supabase migration `add_priority_overrides_2026_05_18` | CREATE | New table `public.priority_overrides` (Sentinel-owned, RLS) |
| `docs/supabase-schema-index.md` | MODIFY | Add row for `priority_overrides` |
| `~/.claude/plans/2026-05-18-cross-workspace-priority-inference.md` | UPDATE | Mark Phase A complete |
| Skill Hub `.work-requests/inbox/` | CREATE | Routed task to HQ for goal-tagging proposal |

---

## Task A.3: File routed-task to HQ — priority_focus + goal-tagging proposal

**Files:**
- Create: `1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/inbox/rt-sentinel-2026-05-18-priority-focus-goal-tagging.json`

- [ ] **Step 1: Compose routed-task via work-request.py (auto-generates v2 schema)**

Use `work-request.py --item-type routed_task --target-workspace workforce-hq` so HQ inbox is correctly populated. Type=ENHANCE, severity=warning.

- [ ] **Step 2: Verify file landed in HQ inbox**

Run: `ls -la "1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/inbox/" | grep priority-focus`
Expected: file present with v2 schema fields.

## Task A.4: Design + apply `priority_overrides` migration

**Files:**
- Create: Supabase migration `add_priority_overrides_2026_05_18`
- Modify: `docs/supabase-schema-index.md` (add new table row)

- [ ] **Step 1: Apply migration via Supabase MCP**

```sql
CREATE TABLE public.priority_overrides (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  tier text NOT NULL CHECK (tier IN ('T1', 'T2', 'T3', 'T4', 'T5')),
  reason text NOT NULL,
  set_by text NOT NULL,
  set_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL DEFAULT (now() + interval '30 days'),
  active boolean NOT NULL DEFAULT true,
  notes text,
  tenant_id uuid REFERENCES public.tenants(id) DEFAULT '00000000-0000-0000-0000-000000000001'::uuid
);
ALTER TABLE public.priority_overrides ENABLE ROW LEVEL SECURITY;
CREATE POLICY priority_overrides_service_all ON public.priority_overrides FOR ALL USING (true) WITH CHECK (true);
CREATE INDEX priority_overrides_project_active ON public.priority_overrides(project_id) WHERE active = true;
CREATE INDEX priority_overrides_expires_at ON public.priority_overrides(expires_at) WHERE active = true;
COMMENT ON TABLE public.priority_overrides IS 'User corrections to AI-inferred project priority tiers. 30d TTL. Sentinel-owned writes; all workspaces read.';
```

- [ ] **Step 2: Verify via direct SQL**

Run via Supabase MCP: `SELECT table_name, column_count FROM information_schema.tables WHERE table_name = 'priority_overrides';`
Expected: 1 row, 10 columns.

- [ ] **Step 3: Update schema index**

Append a row to `docs/supabase-schema-index.md` in the table-of-contents AND a definition section per existing pattern. Set `Rows: 0`, `Status: active — new 2026-05-18 (Priority Inference Phase A)`.

## Task A.5: TDD `compute_priority_tiers()` pure function

**Files:**
- Create: `tools/priority-inference.py`
- Create: `tests/test_priority_inference.py`

- [ ] **Step 1: Write failing tests (RED)**

Tests cover: signal scoring math, tier assignment thresholds, T1 cap at 5, override-overrides-inference, T2 precedence over T1 when defensive criteria met.

```python
# tests/test_priority_inference.py
import importlib.util, unittest
from pathlib import Path
p = Path(__file__).parent.parent / "tools" / "priority-inference.py"
spec = importlib.util.spec_from_file_location("pi", p)
pi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pi)

class TestScoring(unittest.TestCase):
    def test_score_factors_combine(self):
        score = pi.score_project(
            goal_aligned=True, cross_workspace=True, active_days=5,
            blocker_count=2, days_to_deadline=20, voice_mentions=1,
            strategic_focus_flag=False
        )
        # 5 + 3 + 5*2 + 2*2 + 0 + 2 = 24
        self.assertGreaterEqual(score, 20)

    def test_deadline_proximity_only_counts_under_30d(self):
        with_deadline = pi.score_project(goal_aligned=False, cross_workspace=False,
            active_days=0, blocker_count=0, days_to_deadline=15, voice_mentions=0,
            strategic_focus_flag=False)
        no_deadline = pi.score_project(goal_aligned=False, cross_workspace=False,
            active_days=0, blocker_count=0, days_to_deadline=60, voice_mentions=0,
            strategic_focus_flag=False)
        self.assertGreater(with_deadline, no_deadline)

class TestTierAssignment(unittest.TestCase):
    def test_t1_assigned_to_top_3_by_score_min_8(self):
        projects = [
            {"id": "a", "score": 20, "deadline_days": None, "blocker_count": 0, "status": "active"},
            {"id": "b", "score": 15, "deadline_days": None, "blocker_count": 0, "status": "active"},
            {"id": "c", "score": 10, "deadline_days": None, "blocker_count": 0, "status": "active"},
            {"id": "d", "score": 3, "deadline_days": None, "blocker_count": 0, "status": "active"},
        ]
        tiers = pi.assign_tiers(projects, overrides=[])
        self.assertEqual(tiers["a"], "T1")
        self.assertEqual(tiers["b"], "T1")
        self.assertEqual(tiers["c"], "T1")
        self.assertEqual(tiers["d"], "T4")

    def test_t1_cap_at_5(self):
        projects = [{"id": f"p{i}", "score": 20 - i, "deadline_days": None, "blocker_count": 0, "status": "active"} for i in range(8)]
        tiers = pi.assign_tiers(projects, overrides=[])
        t1_count = sum(1 for v in tiers.values() if v == "T1")
        self.assertEqual(t1_count, 5)

    def test_t2_assigned_for_defensive_critical(self):
        projects = [{"id": "x", "score": 6, "deadline_days": 7, "blocker_count": 0, "status": "active"}]
        tiers = pi.assign_tiers(projects, overrides=[])
        self.assertEqual(tiers["x"], "T2")

    def test_t5_for_deferred_status(self):
        projects = [{"id": "z", "score": 12, "deadline_days": None, "blocker_count": 0, "status": "deferred"}]
        tiers = pi.assign_tiers(projects, overrides=[])
        self.assertEqual(tiers["z"], "T5")

    def test_override_supersedes_inference(self):
        projects = [{"id": "a", "score": 20, "deadline_days": None, "blocker_count": 0, "status": "active"}]
        overrides = [{"project_id": "a", "tier": "T5", "active": True}]
        tiers = pi.assign_tiers(projects, overrides=overrides)
        self.assertEqual(tiers["a"], "T5")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Verify RED (tests fail because module doesn't exist)**

Run: `cd "4.- Sentinel" && python -m unittest tests.test_priority_inference 2>&1 | tail -5`
Expected: FAIL with FileNotFoundError on tools/priority-inference.py.

- [ ] **Step 3: Write minimal `priority-inference.py` to GREEN**

Create `tools/priority-inference.py` with `score_project()` + `assign_tiers()` pure functions matching the test contracts. NO Supabase calls yet — those come in A.6.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_priority_inference -v 2>&1 | tail -15`
Expected: All tests PASS.

## Task A.6: Wire `compute_priority_tiers()` to live Supabase data

**Files:**
- Modify: `tools/priority-inference.py` (add `PriorityBrain` class + `compute_priority_tiers()` orchestrator)

- [ ] **Step 1: Add `PriorityBrain` class with Supabase REST methods**

Mirror `WeeklyReviewBrain` pattern from `weekly-review-generator.py`. Methods:
- `fetch_projects()` — all active/pending projects with full metadata
- `fetch_goals()` — active goals with project linkages
- `fetch_recent_activity(days)` — activity stream last N days
- `fetch_active_overrides()` — `priority_overrides` WHERE active=true AND expires_at > now()
- `fetch_blocker_counts()` — count of tasks/requests blocked by each project's outputs

- [ ] **Step 2: Add `compute_priority_tiers()` orchestrator**

Pulls all signals → calls `score_project()` per project → calls `assign_tiers()` with overrides → returns enriched tier list with reasoning.

- [ ] **Step 3: CLI entry point**

```python
if __name__ == "__main__":
    tiers = compute_priority_tiers()
    for t, items in sorted(group_by_tier(tiers).items()):
        print(f"\n=== {t} ===")
        for item in items:
            print(f"  - {item['name']} (score={item['score']}, reason={item['reason']})")
```

## Task A.7: Smoke-test inference against today's real data

- [ ] **Step 1: Run CLI**

Run: `PYTHONIOENCODING=utf-8 python tools/priority-inference.py 2>&1 | head -60`
Expected: Tier list of current Sentinel projects with scores + reasoning.

- [ ] **Step 2: Manual sanity check**

Verify: Reports Restructure (active, recent activity) should land T1 or T2. AIOS items (deferred) should land T5. Confirm cross-workspace projects get the boost.

## Task A.8: Commit + push Phase A

- [ ] **Step 1: Verify all tests still pass**

Run from Sentinel root: `python -m unittest tests.test_priority_inference tests.test_weekly_review_generator 2>&1 | tail -5`
Expected: All pass.

- [ ] **Step 2: Commit**

```bash
git add tools/priority-inference.py tests/test_priority_inference.py docs/supabase-schema-index.md
git commit -m "feat(priority-inference): Phase A - tier inference engine + priority_overrides schema (Sentinel)"
git push origin master
```

- [ ] **Step 3: Update tracking**

- Mark Phase A complete in arc plan + plans-registry row
- Add Supabase task for Phase A completion + create Phase A done activity_stream event
- Update MEMORY.md S57 session entry

## Self-Review Checklist

- [ ] Spec coverage: every task in arc plan Phase A → represented here? YES (A.3-A.8)
- [ ] No placeholders — every step has either exact code, exact command, or specific deliverable
- [ ] Type consistency — `score_project()` signature matches in test + implementation; `assign_tiers()` returns `Dict[str, str]` consistently
- [ ] Tests are real — assertions against actual behavior, not against mocks

## Approval gate (end of Phase A)

User reviews inference output (Task A.7 Step 2). Two valid responses:
- **GO:** authorize Phase B (schema deploy was just done) + Phase C (Weekly Review v1.0 rebuild)
- **CORRECT:** identify specific tier assignments that look wrong; persist as `priority_overrides` rows; re-run to validate
