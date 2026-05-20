# Future Plan: Autonomous Cross-Workspace Coordination

> **Status:** FUTURE -- discuss after Phase 6 guardrails are in place
> **Created:** 2026-04-15
> **Context:** During Phase 6 planning, Chris asked whether workspaces could autonomously coordinate without human orchestration (switching between windows, telling each workspace to start). Two viable options were identified. Both use existing infrastructure -- no new tools needed.

## Problem Statement

Today, multi-workspace phases (like Foundation Reset Phases 5-6) require Chris to:
1. Open each workspace manually
2. Paste a prompt or give instructions
3. Wait for completion
4. Switch to the next workspace and repeat
5. Handle sync points ("workspace B can't start until A finishes")

This is human orchestration overhead that should be automated. The goal: Chris kicks off a multi-workspace phase once, and workspaces coordinate completion signals and handoffs autonomously.

## Option A: Routed Task Completion Signals + CronCreate Polling

**How it works:**
1. Each workspace gets a "phase task" (via routed task JSON or work request) describing what to do
2. Workspace completes its portion autonomously
3. On completion, workspace writes a completion signal JSON to the next workspace's `.routed-tasks/inbox/`
4. The receiving workspace's CronCreate (hourly poll) detects the signal
5. CronCreate determines if all prerequisites are met (e.g., "6A requires all 3 workspace validations complete")
6. If prerequisites met: proceeds autonomously. If not: waits for next poll.

**Completion signal format:**
```json
{
  "task_id": "phase6a-completion-skillhub",
  "task_summary": "Phase 6A data validation complete for Skill Hub",
  "routed_from": "skill-management-hub",
  "routed_to": "sentinel",
  "routed_date": "2026-04-16",
  "priority": "high",
  "context": "Skill Hub has completed its Phase 6A data validation. All tables validated, 2 stale records archived. Ready for 6A verification gate.",
  "what_source_already_did": "Validated projects, tasks, work_requests tables. Archived 2 orphaned task records.",
  "fix_instructions": "This is a completion signal, not a fix request. When ALL workspace completion signals are received, proceed with 6A verification gate.",
  "signal_type": "phase_completion",
  "phase": "6A",
  "workspace_status": "complete"
}
```

**Prerequisites tracking:** The receiving workspace (e.g., Sentinel for 6A gate) checks its `.routed-tasks/inbox/` for completion signals from all required workspaces. Only when all are present does it proceed.

**Pros:**
- Uses 100% existing infrastructure (routed tasks + CronCreate)
- No new tools or mechanisms needed
- Audit trail built in (JSON files document what happened)
- Works today

**Cons:**
- Up to 59 minutes latency between completion and detection (CronCreate polls hourly)
- Requires all workspace sessions to stay open (CronCreate dies on session close)
- No guaranteed ordering -- polling is best-effort
- If a session closes before CronCreate fires, the signal sits unprocessed until next session

**Best for:** Phases where hourly latency is acceptable. Overnight autonomous runs. Situations where Chris is away and workspaces operate independently.

---

## Option B: RemoteTrigger as Push Notification

**How it works:**
1. Same as Option A, but instead of waiting for CronCreate to poll, the completing workspace uses RemoteTrigger to immediately wake up the target workspace
2. RemoteTrigger sends a prompt to a specific workspace session, which processes it immediately

**How RemoteTrigger would work:**
1. Workspace A finishes its work
2. Workspace A writes the completion signal JSON to Workspace B's inbox (same as Option A)
3. Workspace A also fires a RemoteTrigger to Workspace B with a prompt like: "A completion signal has been delivered to your .routed-tasks/inbox/. Check it and proceed if all prerequisites are met."
4. Workspace B receives the trigger immediately and processes it

**Pros:**
- Near-instant notification (seconds, not up to 59 minutes)
- Still has audit trail (JSON files)
- More responsive coordination

**Cons:**
- RemoteTrigger was previously marked BROKEN for MCP-dependent tasks (cold-start race condition)
- Recent testing (2026-04-15) showed it works for cloud MCP -- needs more validation
- Requires target workspace to have an active session listening for triggers
- More complex setup -- two mechanisms (JSON + trigger) instead of one
- If RemoteTrigger fails, falls back to Option A behavior (CronCreate picks it up)

**Best for:** Time-sensitive coordination where hourly latency is too slow. Critical path handoffs.

---

## Hybrid Recommendation (when we build this)

Use Option A as the baseline with Option B as an accelerator:

1. **Always write the completion signal JSON** (Option A) -- this is the source of truth and audit trail
2. **Try RemoteTrigger as a push notification** (Option B) -- if it works, great, instant handoff
3. **CronCreate as the safety net** -- if RemoteTrigger fails or session isn't active, hourly poll catches it
4. **Prerequisite logic in the receiving workspace** -- regardless of how the signal arrived, the workspace checks "do I have all required completion signals?" before proceeding

This gives us: instant notification when possible, hourly fallback when not, and a reliable audit trail always.

## Infrastructure Gaps to Address First

Before building this, Phase 6 guardrails should be in place:
1. All workspaces must have `.routed-tasks/{inbox,processed,outbox}` directories (HQ was missing -- fixed 2026-04-15)
2. Startup guard Step 3.5 must reliably detect and process routed tasks
3. CronCreate prompt must include routed task processing (currently does for Skill Hub, verify for others)
4. A "completion signal" schema should be standardized (the `signal_type` field above)
5. RemoteTrigger reliability needs validation before depending on it

## When to Implement

After Phase 6 is complete and the foundation is clean. Implementing coordination on a dirty foundation means the coordination mechanism inherits the drift. Clean first, coordinate second.

Candidate implementation: Phase 7 (OPERATIONAL) or as a standalone project after Foundation Reset completes.
