# Plan: Autonomous Repo Findings Evaluation via Work Request Routing

## Context

The repo monitor (`tools/repo-monitor.py`) scans weekly for upstream changes in forked/watched repos and writes findings to Supabase `repo_findings` with `status: pending_evaluation`. Currently, these findings sit there until someone manually evaluates them during a session. A manual workflow (`workflows/repo-findings-evaluation.md`) was just created, but the user wants this to be **autonomous** — findings should be routed to Skill Hub as work requests so they can be evaluated and acted on without human intervention.

**The problem:** Findings accumulate silently. The morning report shows them, but nobody processes them. Between sessions, nothing happens.

**The goal:** After every repo monitor scan, automatically route each pending finding to Skill Hub as a work request. Skill Hub evaluates the finding (sync fork / investigate / dismiss) and updates Supabase with the resolution.

## Design Decisions

### Why route to Skill Hub (not process in Sentinel)?

- Sentinel is **read-only oversight** — it monitors and reports, it doesn't build or fix things
- Evaluating a finding may require action: syncing a fork, investigating breaking changes, updating dependencies — that's Skill Hub's domain
- Work request routing is the established cross-workspace communication pattern
- Skill Hub already processes work requests autonomously during idle sessions

### What triggers the routing?

After `repo-monitor.py scan` completes and writes findings to Supabase, a new post-scan step routes each `pending_evaluation` finding as a work request to Skill Hub.

### Work request structure for repo findings

Each finding becomes a TASK-type work request with enough context for Skill Hub to evaluate autonomously:
- **type:** TASK
- **category:** operations
- **needed:** Evaluate repo finding and take action (sync/investigate/dismiss)
- **gap:** The finding description + repo + finding_type + relevance_score
- **fix_type:** workflow
- **fix_desc:** Instructions for Skill Hub: check the upstream change, decide action, update Supabase `repo_findings` row with status + evaluation_notes

## Implementation Plan

### Step 1: Add `route_findings_to_skill_hub()` function to `repo-monitor.py`

**File:** `tools/repo-monitor.py`

After `scan_all()` writes findings to Supabase, call a new function that:
1. Queries Supabase for all `pending_evaluation` findings (not just the ones from this scan — catch any backlog too)
2. For each finding, calls `work-request.py` with:
   - `--type TASK`
   - `--severity` mapped from relevance_score (≥8 = critical, ≥5 = warning, <5 = info)
   - `--workspace sentinel`
   - `--workspace-path` (Sentinel workspace path)
   - `--task "Repo monitor: evaluate upstream finding"`
   - `--category operations`
   - `--needed "Evaluate repo finding: {repo} — {finding_type}"`
   - `--gap "{description} (relevance: {score}/10)"`
   - `--impact "Pending findings accumulate without evaluation; upstream changes may be missed"`
   - `--fix-type workflow`
   - `--fix-desc "Check upstream change for {repo}. Finding type: {finding_type}. If fork_behind: sync via GitHub merge-upstream API. If new_release: check changelog for relevant changes. If breaking_change: investigate before syncing. Update Supabase repo_findings row {id} with status (evaluated/dismissed/action_sync/action_investigate) and evaluation_notes."`
   - `--fix-components "supabase: repo_findings table, github: {repo}"`
3. After routing, update the finding's status in Supabase from `pending_evaluation` to `routed_to_skill_hub` so it doesn't get re-routed on the next scan

**Key detail:** The work request `--fix-desc` must contain the Supabase finding ID so Skill Hub knows exactly which row to update when it resolves the request.

### Step 2: Wire routing into `scan_all()` flow

**File:** `tools/repo-monitor.py`

At the end of `scan_all()`, after all findings are written to Supabase, call `route_findings_to_skill_hub()`. Skip routing in `--dry-run` mode.

### Step 3: Update `repo_findings` status values

**No schema change needed.** The `status` column is a text field. We add a new convention:
- `pending_evaluation` — written by repo-monitor scan (existing)
- `routed_to_skill_hub` — routed as work request, awaiting Skill Hub processing (new)
- `evaluated` / `dismissed` / `action_sync` / `action_investigate` — resolved by Skill Hub (existing from manual workflow)

### Step 4: Update the manual workflow doc

**File:** `workflows/repo-findings-evaluation.md`

Update to reflect that evaluation is now autonomous via work request routing. Keep the manual steps as a fallback reference (in case Skill Hub is backed up or someone wants to evaluate directly).

### Step 5: Update evening/morning report display

**File:** `tools/brief-generator.py`

The morning report already shows pending findings. Update the query or display to distinguish `pending_evaluation` (not yet routed — problem) from `routed_to_skill_hub` (routed, awaiting processing — expected). Only flag `pending_evaluation` as needing attention.

**File:** `tools/ops-brain.py`

Check `get_repo_findings()` — currently queries `status=eq.pending_evaluation`. May need to also show `routed_to_skill_hub` findings or add a separate count.

## Files to Modify

| File | Change |
|------|--------|
| `tools/repo-monitor.py` | Add `route_findings_to_skill_hub()`, call it from `scan_all()` |
| `workflows/repo-findings-evaluation.md` | Update to document autonomous routing + keep manual fallback |
| `tools/brief-generator.py` | Distinguish routed vs unrouted findings in morning report |
| `tools/ops-brain.py` | Update `get_repo_findings()` to handle new status value |

## Existing Functions to Reuse

- `~/.claude/scripts/work-request.py` — The established routing mechanism. Call via subprocess with CLI args. No need to build custom routing.
- `repo-monitor.py:_supabase_post()` — Already handles Supabase writes. Need a PATCH variant for status updates.
- `brief-generator.py:get_routed_tasks()` — Pattern for reading cross-workspace inbox data.

## Verification

1. Run `python tools/repo-monitor.py scan --dry-run` — confirm findings are detected but NOT routed (dry-run guard)
2. Run `python tools/repo-monitor.py scan` on a repo with a known pending finding — confirm work request appears in Skill Hub's `.work-requests/inbox/`
3. Verify Supabase `repo_findings` row status changed from `pending_evaluation` to `routed_to_skill_hub`
4. Check morning report (`python tools/brief-generator.py morning --no-send`) — confirm routed findings display correctly
5. Verify no duplicate work requests on re-scan (status check prevents re-routing)
