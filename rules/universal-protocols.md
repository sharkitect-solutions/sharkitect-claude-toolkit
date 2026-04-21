# Universal Protocols -- Sharkitect Digital

> **Scope:** All Sharkitect Digital internal workspaces.
> **Skip when:** CLAUDE.md PROJECT_PURPOSE contains "Universal AI Operating System"
> or workspace type is "client-project".
> **Authority:** This rule is the single source of truth for universal protocols.
> Workspace CLAUDE.md files may contain older copies of these items -- this rule
> takes precedence. Workspace CLAUDE.md extends these protocols with
> workspace-specific additions only.

## Workspace Directory (NON-NEGOTIABLE)

Every workspace has a defined scope. Work MUST happen in the correct workspace. If the task you're about to do falls outside this workspace's scope, STOP and tell the user: "This belongs in [correct workspace]. Reason: [scope rule]."

| # | Workspace | Filesystem Path | Scope | Owns | Does NOT Do |
|---|-----------|----------------|-------|------|-------------|
| 1 | **SHARKITECT DIGITAL WORKFORCE HQ** | `1.- SHARKITECT DIGITAL WORKFORCE HQ` | Client work, business operations, revenue | Client deliverables, proposals, SOPs, invoicing, CRM, client projects, CEO daily briefs (n8n), fallback briefs (Task Scheduler), error-autofix bridge | Skills/hooks/agents, brain monitoring |
| 2 | **Skill Management Hub** | `3.- Skill Management Hub` | Capability infrastructure | Skills, hooks, agents, plugins, gap detection + alerting + processing, sync to GitHub toolkit repo | Client work, brain monitoring |
| 3 | **Sentinel** | `4.- Sentinel` | Oversight, intelligence, monitoring | Brain health monitoring, dream consolidation, system intelligence reports, Supabase brain queries, document freshness auditing, morning system report, repo monitor, Watcher's Watcher (n8n) | Client work, skill creation, business automation |

> **CRITICAL:** The filesystem path column above is the EXACT directory name under `Claude Code Workspaces/`. When writing files to another workspace, ALWAYS use this exact name. NEVER guess, abbreviate, or construct paths from the shorthand workspace name. If unsure, run `ls` on the workspaces directory first. NEVER create a new workspace directory -- if the path doesn't exist, STOP and ask the user.

### Canonical Naming Standard (NON-NEGOTIABLE)

Each workspace has exactly THREE identifiers. No aliases. No abbreviations. No alternatives.

| Workspace | Filesystem Path (for file ops) | Canonical Name (for Supabase, scripts, references) |
|-----------|-------------------------------|-----------------------------------------------------|
| SHARKITECT DIGITAL WORKFORCE HQ | `1.- SHARKITECT DIGITAL WORKFORCE HQ` | `workforce-hq` |
| Skill Management Hub | `3.- Skill Management Hub` | `skill-management-hub` |
| Sentinel | `4.- Sentinel` | `sentinel` |

**Rules:**
1. **Supabase writes, script arguments, JSON fields, and all programmatic references** use the Canonical Name column. Always. No exceptions.
2. **Filesystem operations** (writing files, reading paths) use the Filesystem Path column. Always. No exceptions.
3. **Human-readable text** (MEMORY.md, conversation, commit messages) uses the Workspace column.
4. **There are NO other valid names.** Not "Skill Hub", not "HQ", not abbreviations. If a script receives a non-canonical name, it must reject it -- not silently convert it. Silent conversion enables drift.
5. **Scripts enforce this.** Both `work-request.py` and `update-project-status.py` validate workspace names against the canonical list and exit with an error on mismatch.

**Why:** A previous incident created a duplicate workspace directory because the AI constructed a path from an abbreviated name instead of using the exact filesystem path. Aliases enable this class of error. One name per context, enforced programmatically.

### Automation Ownership
Each workspace owns the scheduled tasks and automations that support its purpose. See `~/.claude/docs/autonomous-systems-inventory.md` for the full ownership map.

### Routing Rules
- **Building a skill, hook, or agent?** --> Skill Hub
- **Building or fixing a business n8n workflow (briefs, error handler)?** --> Workforce HQ
- **Building or fixing a monitoring n8n workflow (watcher)?** --> Sentinel
- **Working on a client deliverable?** --> Workforce HQ
- **Monitoring system health or running audits?** --> Sentinel
- **Processing a work request (building the fix)?** --> Skill Hub
- **Setting up gap alerting or detection?** --> Skill Hub
- **Modifying a Task Scheduler job?** --> The workspace that owns the system it supports

### When You Detect Out-of-Scope Work
If you realize the current task belongs in another workspace:
1. STOP before creating files or making changes
2. Tell the user which workspace owns this work and why
3. Suggest: "Open [workspace name] and continue there"
4. If the user insists on continuing here, note it in MEMORY.md as a scope exception with the reason

---

## Pre-Task Checklist (before ANY work)

Run this checklist before starting any task. These items are non-negotiable.

- [ ] Read the request carefully. Confirm understanding before acting.
- [ ] Check your toolkit -- review all available skills, agents, tools, plugins, and MCPs. Identify which ones are relevant to this task. Use them.
- [ ] **Named-skill enforcement (NON-NEGOTIABLE):** If the task spec, routed-task `fix_instructions`, work request, or inbox JSON literally names a skill to invoke (phrases like "invoke X skill", "Relevant skill:", "See <skill>'s <companion>.md", "use the X skill"), you MUST invoke that skill via the `Skill` tool BEFORE starting implementation. Do NOT substitute inline spec reading or general knowledge. The whole point of curated skills is the reinforced, up-to-date patterns they encode. Silent skip degrades the system.
- [ ] Check MEMORY.md -- review prior learnings, patterns, and preferences that apply to this task.
- [ ] Check workflows/ -- is there an existing SOP for this type of work? Follow it.
- [ ] Plan before executing -- identify what needs to be done, in what order, and present the plan before starting.
- [ ] If the task is ambiguous, ask ONE clarifying question before proceeding.

> Workspace CLAUDE.md may define additional workspace-specific pre-task items. Run those too.

## Post-Task Checklist (after ANY work)

Run this checklist after completing any task. No task is "done" until post-task passes. Execute in this order -- Supabase first, then local, then push.

### 1. Verify Work
- [ ] Verify all outputs are saved, correct, and complete.
- [ ] Check cross-references -- if Document A was updated and Document B references it, update B.
- [ ] Confirm nothing is left in an inconsistent or half-finished state.

### 2. Update Supabase (SOURCE OF TRUTH -- do this FIRST, not last)
- [ ] If any task was completed: `python ~/.claude/scripts/update-project-status.py task "<task>" completed --project "<project>"`
- [ ] If a project phase advanced: `python ~/.claude/scripts/update-project-status.py project "<name>" <status> --phase "<phase>" --notes "<notes>"`
- [ ] If a project was completed, blocked, or unblocked: update project status immediately.
- [ ] If new tasks were discovered: `python ~/.claude/scripts/update-project-status.py add-task "<task>" --project "<project>" --workspace "<workspace>"`

### 3. Update Local Documents
- [ ] Update MEMORY.md with session learnings (decisions, patterns, preferences discovered).
- [ ] If a plan was created, completed, or abandoned: update `~/.claude/docs/plans-registry.md` (see Plan Lifecycle Protocol).
- [ ] If a plan file was worked on: update the plan's status header and individual task markers to match reality.
- [ ] If new patterns, errors, preferences, or process decisions were discovered: write to `~/.claude/lessons-learned.md` (see 7 categories).
- [ ] If new patterns or processes were discovered, record them in workspace MEMORY.md topic files.

### 4. Push Everything
- [ ] Git commit + push: `git add <changed files> && git commit -m "<description>" && git push`
- [ ] Run `/session-checkpoint` before closing the session (this runs the full 9-step audit as a safety net).

> Workspace CLAUDE.md may define additional workspace-specific post-task items. Run those too.
> **Key principle:** A task is not complete when the code works. A task is complete when Supabase says it's complete, local docs reflect it, and git has it pushed. All three or it didn't happen.

## Session Lifecycle

### Session Start
1. Read MEMORY.md -- check pending items, patterns, preferences.
2. Sync from global lessons: Read `~/.claude/lessons-learned.md`. Check Preferences, Process Decisions, and Architecture Direction sections for entries not yet reflected in this workspace's memory. Pull relevant new entries into workspace MEMORY.md or topic files. This ensures learnings from other workspaces propagate here.
3. `git pull` if remote exists (cross-computer sync).
4. Refresh document cache: `python ~/.claude/scripts/doc-cache-builder.py --path "$(pwd)" --merge --quiet`
5. **Supabase ownership audit (FULL_STARTUP only):** Verify that all known projects, plans, and tasks for THIS workspace are accurately represented in Supabase. Check statuses, priorities, blockers, and phase descriptions. If anything is missing, stale, or inaccurate -- fix it immediately. Plans count as projects (status `pending` until active). If it exists as a plan, it must exist as a Supabase project.
6. Resume from where last session left off.

### During Session (at stage completions / checkpoints)
1. Update MEMORY.md with decisions and progress.
2. Push state to Supabase (if configured for this workspace).
3. Git checkpoint (commit + push) at significant milestones.

### Session End
- Run `/session-checkpoint` -- this invokes the full 9-step end-of-session protocol:
  1. Resource audit verification
  2. MEMORY.md update
  3. Lessons learned capture
  4. Plan status update
  5. Pending items documentation
  6. Workspace-specific checklist (reads CLAUDE.md)
  7. Git checkpoint (commit + push)
  8. Supabase brain sync
  9. Summary report (pass/fail per step)
- The session-checkpoint skill handles everything. Do NOT skip it.
- Do NOT close a session without running `/session-checkpoint`.

## Memory Protocol

### Architecture
- **Project MEMORY.md** -- Auto-loaded every session. Hard limit: 200 lines (content beyond 200 is truncated and invisible). Keep as concise index. Move detailed content into separate topic files in the same directory and reference them from MEMORY.md.
- **Topic files** -- For detailed notes that don't fit in MEMORY.md's 200-line limit. Store in the same memory directory (e.g., `session-history.md`, `patterns.md`, `debugging-notes.md`). Reference from MEMORY.md.

### Session Memory Protocol
**Every session, without exception:**
1. **Start of session:** Read MEMORY.md. Then sync from `~/.claude/lessons-learned.md` -- pull any new Preferences, Process Decisions, or Architecture Direction entries into workspace memory if relevant and not already reflected.
2. **During session:** When a significant decision is made, a pattern is discovered, or a task outcome is known -- update memory immediately. Do not wait until the end.
3. **End of session:** Push new learnings (preferences, process decisions, architecture direction, errors) to `~/.claude/lessons-learned.md` via session-checkpoint Step 3. Update workspace MEMORY.md with session-specific decisions and progress.

### What to Record
- Decisions made and the reasoning behind them
- Patterns confirmed across 2+ interactions
- User preferences (communication style, decision patterns, approval triggers)
- Solutions to recurring problems
- Process improvements that proved effective
- Failures, root causes, and what was done instead

### What NOT to Record
- Temporary session context that won't matter next time
- Speculation or unverified conclusions
- Duplicate information already in project documentation
- Information that contradicts established project rules without user approval

### 200-Line Discipline
MEMORY.md WILL be truncated at 200 lines. Plan for this:
- Keep the most important information (active rules, key patterns, pending items) in the FIRST 150 lines
- Session history summaries go in a separate `session-history.md` file
- Detailed technical notes go in topic-specific files
- Regularly prune outdated entries

## Work Request Protocol (NON-NEGOTIABLE)

When you detect a missing capability, broken infrastructure, dead configuration, bug, or needed enhancement during ANY work -- report it immediately. Do NOT wait for a post-task audit.

### What Triggers a Work Request
- You need a skill, hook, or workflow that doesn't exist (type: MISSING)
- A hook or tool exists but isn't functioning (type: MISSING or BUG)
- You used general knowledge where a specialized skill would produce better output (type: FALLBACK)
- An existing resource exists but wasn't invoked when it should have been (type: UNUSED)
- An existing artifact has a bug that needs fixing (type: BUG)
- An existing system needs improvement (type: ENHANCE)
- An operational task needs Skill Hub to handle it (type: TASK)

### How to Report
Run the work request script from any workspace:
```bash
python ~/.claude/scripts/work-request.py \
  --type MISSING \
  --severity warning \
  --workspace "YOUR WORKSPACE NAME" \
  --workspace-path "$(pwd)" \
  --task "Brief description of what you were doing" \
  --category operations \
  --needed "What capability was needed" \
  --gap "What specifically is missing or broken" \
  --impact "How this affected the work" \
  --fix-type hook \
  --fix-desc "Description of recommended fix" \
  --fix-components "component1, component2"
```

Request types: `MISSING` (nothing exists), `UNUSED` (exists but wasn't used), `FALLBACK` (used generic instead of specialized), `TASK` (operational work), `BUG` (fix needed), `ENHANCE` (improvement needed).

### Where Requests Go
All work requests land in the Skill Management Hub's `.work-requests/inbox/`. The Skill Hub processes them autonomously -- builds fixes, deploys globally, and notifies all workspaces. Items that belong to another workspace get routed via `.routed-tasks/` to the owning workspace.

### Do NOT Fix Gaps Locally
Workspaces do not build global artifacts. If you detect an issue, REPORT it via `work-request.py`. The Skill Hub handles triage, building, quality gating, and deployment. Local fixes bypass the quality gate and won't be available to other workspaces.

## Cross-Workspace Routed Tasks Protocol (NON-NEGOTIABLE)

When a workspace discovers an issue that belongs to another workspace, it routes a task.

**Sending TO Skill Hub:** Use `work-request.py` (see Work Request Protocol above). Do NOT write to `.routed-tasks/` -- Skill Hub has no `.routed-tasks/` directory. All inbound work goes through `.work-requests/inbox/`.

**Sending TO HQ or Sentinel:** Use `.routed-tasks/` as described below.

**Skill Hub sending OUT:** Skill Hub routes work to other workspaces by writing to their `.routed-tasks/inbox/` and keeping audit trails in its own `.work-requests/outbox/`.

### Directory Structure (HQ and Sentinel)
```
.routed-tasks/
  inbox/       # Incoming tasks from other workspaces (JSON, machine-readable)
  processed/   # Completed tasks with resolution notes
  outbox/      # Human-readable reports of tasks THIS workspace sent (audit trail)
```

### Routing Flow
1. **Source workspace** writes a human-readable `.md` file in its own `.routed-tasks/outbox/` describing the finding, what it already did, and what the target workspace needs to do
2. **Source workspace** writes a `.json` file to the **target workspace's** `.routed-tasks/inbox/` with structured fields the AI can parse and act on
3. **Target workspace** processes the JSON at session start (startup guard Step 3.5) or CronCreate poll
4. **Target workspace** moves completed JSON to `.routed-tasks/processed/` with a `resolution` object appended

### File Naming Convention
- **Outbox (.md):** `{target}-{short-slug}.md` (e.g., `skillhub-gap-pipeline-stale-heartbeat.md`)
- **Inbox/Processed (.json):** `rt-{date}-{short-slug}.json` (e.g., `rt-2026-04-14-gap-pipeline-stale-heartbeat.json`)
- The `task_id` inside the JSON matches the filename (without `.json`)
- Slugs should be descriptive enough to understand at a glance without opening the file

### Required JSON Fields
```json
{
  "task_id": "rt-2026-04-14-short-slug",
  "task_summary": "One-line human-readable description",
  "routed_from": "source-workspace-name",
  "routed_to": "target-workspace-name",
  "routed_date": "2026-04-14",
  "priority": "low|medium|high|critical",
  "context": "What was found and why it matters",
  "what_source_already_did": "What the source workspace fixed on its side",
  "fix_instructions": "What the target workspace needs to do",
  "lessons_learned": "Optional: reusable pattern for workspace memory"
}
```

When resolved, append a `resolution` object:
```json
{
  "resolution": {
    "resolved_date": "2026-04-14",
    "resolved_by": "target-workspace-name",
    "what_was_done": "Description of the fix",
    "files_changed": ["path/to/file.py"],
    "verified": true
  }
}
```

### Processing Rules
- **Session start**: startup guard detects pending items -> process immediately BEFORE responding to user
- **Mid-session CronCreate** (all workspaces): hourly triage poll -- see Mid-Session Inbox Polling Protocol below
- **Manual**: if you notice items during work, process immediately
- "Process" means: do the work, verify, move to processed. Not "list them and ask the user."
- **DEFERRED ≠ PROCESSED (NON-NEGOTIABLE):** If a task cannot be completed right now, it STAYS IN THE INBOX. Do NOT move it to `processed/`. A task in `processed/` is a task no session will ever pick up again. Only move to `processed/` when the actual work described in `fix_instructions` is DONE and VERIFIED.
- **USE close-inbox-item.py (NON-NEGOTIABLE):** Every workspace closes inbox items via `python ~/.claude/scripts/close-inbox-item.py --file <path> --status processed --resolved-by <workspace> --what-was-done "<description>"`. This script atomically (a) sets the top-level `status` field to one of `processed | completed | resolved | rejected`, (b) writes/merges the `resolution` object with required fields, (c) appends a `status_history` entry, (d) moves the file to `processed/`, and (e) best-effort updates the matching Supabase `cross_workspace_requests` row. Do NOT use ad-hoc `python json.dump` + file move -- this caused 13+ records of status-field drift across 3 workspaces (Sentinel wr-2026-04-19-002 audit). Allowed close statuses: `processed | completed | resolved | rejected`. PROHIBITED at close: `pending | in_progress | deferred | new | blocked | awaiting_decision`. The script rejects vague `what_was_done` like "acknowledged" or "deferred" to prevent fake-completion records.

### Rejected vs Drift-Correction (NON-NEGOTIABLE)

Two distinct closure paths for inbox items that will NOT be worked on. Choose correctly -- the metrics depend on it.

| Path | Use When | How to Close | Timeline it lives in |
|------|----------|--------------|----------------------|
| **Closed as rejected** | Request is VALID but declined on merits (wrong priority, duplicate of existing work, out of scope, won't-fix, author stands by the request) | `close-inbox-item.py --file <path> --status rejected --resolved-by <workspace> --what-was-done "<reason for rejection>"` | Request-trend timeline (legitimate requests that got declined) |
| **Deleted + drift_correction** | Request was INVALID FROM ORIGIN (misfiled, wrong pattern, author mistake, filed off a single transient error, wrong directory, author withdraws on review) | Delete the JSON file, delete the matching Supabase `cross_workspace_requests` row, then insert an `activity_stream` row with `event_type='drift_correction'` citing the filed request id and reason | Filer-quality timeline (signal that filing process needs tightening) |

**Why both paths exist:** Both close the work, but they measure different things. "Rejected" lives in the request-trend timeline -- it tells us which kinds of valid requests we're declining and why (and is therefore visible in briefs and dashboards). "Drift-correction" lives in the filer-quality timeline -- it tells us which workspaces or hooks are producing noise. Mixing them inflates the rejection rate and hides the filer-drift signal. Both metrics matter; they must stay separate.

**Decision rule:** Ask "would this request have been correctly filed if the author had the information they have now?" If YES, it's a real request the author still stands behind -> reject on merits. If NO (the request should never have been created -- author withdraws, pattern was wrong, triggered by a transient fluke), it's drift -> delete + drift_correction.

**Source incident:** 2026-04-21 Sentinel filed wr-2026-04-21-002 (bash PATH error off a single transient failure without retrying) and wr-2026-04-21-003 (wrong directory pattern). Both were invalid from origin -- the author (Sentinel) reviewed and withdrew both. If closed with `--status rejected`, rejection-rate metrics would have shown "2 declined requests" -- false signal, hiding the real lesson (filer drift). Chris authorized delete + drift_correction event (logged as `b51dca5f-754a-450b-a1f5-ca205900a944`).

**Enforcement:** `close-inbox-item.py` accepts `--status rejected` directly. Drift-correction requires a manual delete (JSON + Supabase row) plus an `activity_stream` INSERT with `event_type='drift_correction'`. Sentinel owns the schema/CHECK constraint for `event_type`.

### Blocked vs Deferred (NON-NEGOTIABLE)

Two distinct inbox states with different behaviors. Do NOT confuse them.

| Status | Meaning | `blocked_by` required? | Auto-process when idle? |
|--------|---------|----------------------|------------------------|
| **deferred** | "Not now, busy with other work" | No | **YES** -- pick up immediately when idle |
| **blocked** | "Cannot proceed until dependency completes" | **YES** (Supabase UUID) | **YES**, but ONLY after Supabase confirms blocker is completed |

**Deferred:** Item CAN be done, just not right now. When the session goes idle (no active user work), deferred items are processed autonomously. No user instruction needed. "Deferred" means "when we're free" -- idle IS free.

**Blocked:** Item CANNOT be done until a specific dependency completes. The `blocked_by` field must contain the Supabase UUID of the blocking record (task, project, or cross_workspace_request). The `blocked_by_type` field indicates the table (`task`, `project`, or `cross_workspace_request`). The `blocked_by_description` field provides a human-readable explanation. At startup and during idle polls, check Supabase for the blocker's status. If completed -> unblock and process. If still pending -> leave blocked.

**JSON fields for blocked items:**
```json
{
  "status": "blocked",
  "blocked_by": "<supabase-uuid-of-blocking-record>",
  "blocked_by_type": "task|project|cross_workspace_request",
  "blocked_by_description": "Human-readable: what this is waiting on",
  "blocker_cleared_notes": []
}
```

**Neither deferred NOR blocked can move to processed/.** Both stay in inbox until the work is actually done. The inbox-move-guard enforces this.

### Inbox-Driven Coordination (NON-NEGOTIABLE)

ALL cross-workspace task dispatch goes through inboxes. Never copy-paste prompts between workspaces.

**The rule:** When workspace A needs workspace B to do something, A writes a task to B's inbox (work request or routed task). A does NOT generate a "paste this prompt into workspace B" instruction. The user should never have to copy anything between workspaces.

**Urgency encoding:**
- `severity: critical` + `"immediate": true` in the JSON = Must be done NOW, blocks current work
- `severity: high` = Should be done this session, blocks a phase or project
- `severity: medium` / `low` = Can be deferred, process when time is right

**How it works:**
1. Source workspace writes the task to the target's inbox with full context and urgency level
2. User opens target workspace and says "run your inbox tasks" -- or the idle CronCreate poll picks it up automatically
3. If the user says "defer that," the request stays in the inbox. Add a `"deferred_until"` field with reason. It gets processed when the time is right.
4. No copy-paste. No "here's a prompt for workspace X." The inbox IS the coordination mechanism.

**Why:** Copy-pasting prompts is manual, error-prone, and defeats the autonomy model. The inbox system provides: context that travels with the request, automatic pickup via CronCreate when idle, an audit trail (processed/ with resolution), and urgency that the target workspace can act on without asking.

## Mid-Session Inbox Polling Protocol (NON-NEGOTIABLE)

CronCreate fires hourly in ALL workspaces to check inboxes. Behavior depends on session state.

### Two Modes

**Active Mode** (user is engaged -- recent messages, active task in progress):
- **Triage only.** Check inboxes, classify each item by priority and time-to-fix.
- Present a brief intelligent summary (not just "3 items pending" -- explain WHAT they are, WHY they matter, and whether they can wait).
- **Recommendation required.** For each item, state: "Recommend: handle now" or "Recommend: defer to next session."
- Include reasoning: "This blocks X" or "This is operational validation, not urgent."
- User decides. If user says defer, move on. If user says handle, process it.
- **Critical items**: always recommend handling immediately, but still let user decide.
- **Deferred items**: Do NOT mention in triage briefing (they auto-process when idle). EXCEPTION: If a deferred item is critical OR is blocking another task/workspace, include it in triage with recommendation to handle now.
- **Blocked items**: Check each item's `blocked_by` UUID against Supabase. If a blocker has cleared, mention it: "Blocker cleared for [item]. Recommend: handle now." If still blocked, do not mention.

**Idle Mode** (user appears away -- no recent messages, no active task, session sitting idle):
- **Process autonomously.** Full processing, not triage. Do not wait for user response.
- **Processing order (dependency-aware priority):**
  1. Items blocking other items go FIRST (unblock downstream work)
  2. Within that: critical -> high -> medium -> low (see Priority Escalation Protocol)
  3. Same priority, no dependencies: FIFO (oldest first)
- **Deferred items:** Process them. "Deferred" means "when we're free" -- idle IS free. No special treatment -- they're just regular items that were delayed.
- **Blocked items:** Check each item's `blocked_by` UUID against Supabase.
  - If blocker status = completed -> mark item as unblocked (status -> "pending"), process it
  - If blocker still pending/in_progress -> leave blocked, skip
  - If `blocker_cleared_notes` exist, run the Blocker-Cleared Verification (see protocol below)
- When the user returns, show a brief summary of what was processed while they were away.

### How to Determine Mode

**Primary signal: cron-to-cron user activity.** Scan conversation history backward for the previous CronCreate poll firing (recognizable by the standard "MID-SESSION INBOX POLL. Follow the Mid-Session Inbox Polling Protocol..." prompt). Then look at what happened between that prior cron and now:

- **IDLE if:** No user message exists between the previous cron fire and this one. Long-running tasks in the background (tests, deploys, agent dispatches, builds) do NOT count as user activity -- a card-funnel test mid-flight while the user is away is still IDLE.
- **ACTIVE if:** User sent at least one message between the previous cron fire and now.
- **First cron fire of session: ALWAYS ACTIVE, TRIAGE-ONLY (NON-NEGOTIABLE).** The first cron fire of any session must default to ACTIVE mode. NO autonomous processing on first fire, regardless of any other signal you might infer. Triage only -- present brief intelligent summary with handle-now-vs-defer recommendations, then wait. The cron has no clock and no reliable user-activity signal at first fire. Past incident (2026-04-19): cron-fired session classified itself as IDLE on first fire and processed 2 routed tasks autonomously while user was actively watching, breaking the user-visibility principle. Hook `cron-context-enforcer.py` enforces this at runtime by injecting an ACTIVE-mode reminder when it detects the first fire.
- **Orphan process awareness (NON-NEGOTIABLE).** If `cron-context-enforcer.py` flags the parent claude.exe process as 4+ hours old, it is likely an orphan from a prior session that closed abnormally. Orphans NEVER have user activity to detect. Default to triage-only mode and log every action to `.tmp/cron-activity-log.jsonl`. Do NOT process inbox items in suspect-orphan state unless they are critical AND blocking other work.

**Secondary signals (use only when cron-to-cron signal is ambiguous):**
- An unanswered question YOU asked the user that's still pending in the most recent assistant turn -> treat as ACTIVE (user is reading/composing).
- The user said "end session" / "wrap up" / "go away for X" / similar disengagement signal -> IDLE on the next poll.

**Do NOT use these signals (they are unreliable):**
- "Active todos with in_progress items" -- todos can sit in_progress while the user is away. Mode reflects USER state, not task state.
- "Last exchange was my output" -- normal during multi-step work where the user is reading. This alone does not mean idle.

### Anti-Hallucination Rules (NON-NEGOTIABLE)

**You have no clock.** No tool gives you wall-clock time, and you cannot measure minutes since the user's last message. Therefore:

- **NEVER** claim a specific elapsed time ("no activity for 45 minutes", "Chris has been away ~20 min", "since 2:15 PM"). These are hallucinations -- you have no source for them.
- **NEVER** prefix briefings or summaries with a clock time you fabricated. If you reference timing, use ONLY relative qualitative terms: "recent", "this session", "earlier", "since last poll", "since you ended the previous task".
- If you genuinely need a real timestamp (e.g., for a Supabase write), call a script that returns one (`date`, `python -c "import datetime; print(datetime.datetime.now())"`). Never invent the value yourself.

### Briefing Format (Active Mode)
```
Inbox check: 1 routed task from Sentinel -- lifecycle review verification.
  Priority: medium | Est. fix: ~10 min
  Recommendation: DEFER. Operational validation, not blocking active work.
  Will process at next session start.
```

```
Inbox check: 1 work request -- plugin cache wiped, 3 plugins missing.
  Priority: critical | Est. fix: ~5 min
  Recommendation: HANDLE NOW. Plugin loss compounds if we build skills
  this session without noticing they're gone.
```

### What Each Workspace Checks
| Workspace | Work Requests | Lifecycle Inbox | Routed Tasks Inbox |
|-----------|---------------|-----------------|-------------------|
| Skill Hub | YES | YES | N/A (no .routed-tasks/) |
| Workforce HQ | N/A (sends via work-request.py) | YES | YES |
| Sentinel | N/A (sends via work-request.py) | YES | YES |

### CronCreate Setup (all workspaces)
Each workspace creates a CronCreate durable job at session start if not already configured.
The startup guard (Step 5) detects missing cron and instructs creation. The prompt varies per workspace -- see workspace CLAUDE.md for the exact prompt.

## Priority Escalation Protocol (NON-NEGOTIABLE)

When an item blocks another item, its effective priority automatically escalates. This applies to inbox items, Supabase tasks, and Supabase projects.

### Rules
1. Find the HIGHEST priority among ALL items this one blocks (walk the full cascade chain)
2. Set the blocker's effective priority to ONE LEVEL ABOVE that highest
3. Ceiling: `critical` (cannot exceed)
4. Tiebreaker: at same effective priority, items with documented dependencies (blockers) take precedence over regular items

### Priority ladder
`low` -> `medium` -> `high` -> `critical` (max)

### Example
Item A (`low`) blocks Item B (`medium`) which blocks Item C (`high`).
- Highest cascaded dependency = `high`
- One level above `high` = `critical`
- Item A's effective priority = `critical`
- If another regular `critical` item exists in the queue, Item A goes first (blocker precedence)

### Computation
Escalation is computed at triage time, not stored. The original `priority` field stays unchanged in the record. The effective priority is calculated by checking what depends on this item. This keeps records clean while ensuring blockers are processed in the right order.

### Where this applies
- **Inbox items** (work requests, routed tasks, lifecycle reviews) -- during triage and idle processing
- **Supabase tasks** (via `update-project-status.py check-blockers`) -- during session-start blocker checks
- **Supabase projects** -- if project X blocks project Y, project X gets escalated

## Blocker-Cleared Notification Protocol (NON-NEGOTIABLE)

When a workspace completes work that another workspace's inbox item is blocked on:

### Completing workspace responsibilities
1. Update Supabase (mark task/project/request as completed)
2. Find the blocked item in the waiting workspace's inbox
3. Open the EXISTING JSON file and add a note to the `blocker_cleared_notes` array:
   ```json
   {
     "timestamp": "<ISO timestamp>",
     "signed_by": "<completing workspace canonical name>",
     "note": "Blocker cleared: <description of what was completed>",
     "supabase_record_id": "<UUID of the completed record>"
   }
   ```
4. Do NOT change the item's `status` from `blocked` -- the owning workspace verifies and changes it

### Receiving workspace responsibilities (at next startup/idle poll)
1. Read the `blocker_cleared_notes` in the inbox item
2. **VERIFY against Supabase:** Query the `blocked_by` UUID, confirm status = `completed`
3. **If MATCH** (note says cleared AND Supabase confirms):
   - Change item status from `blocked` to `pending` (unblocked)
   - Process it (if idle) or include in triage (if active) with "Blocker cleared" note
4. **If MISMATCH** (note says cleared BUT Supabase still shows pending/in_progress):
   - Do NOT process the item
   - Send a work request to the signing workspace: "Mismatch detected: blocker_cleared_notes says [X] but Supabase record [UUID] shows status [Y]. Please investigate and correct."
   - Document the discrepancy in the inbox item's `blocker_cleared_notes`
   - The signing workspace investigates root cause, fixes the gap, and files a work request to whoever owns the broken update process
   - Both workspaces document findings in local memory and Supabase

### Why this exists
Trust-but-verify prevents cascading errors from stale Supabase data. If a workspace says "done" but Supabase disagrees, something is broken in the update pipeline. Catching it immediately prevents downstream workspaces from acting on false information.

## Cross-Document Integrity Protocol

When you update any business document, check whether related documents need updating too.

### How It Works
1. `doc-cache-builder.py` runs at session start and builds `.tmp/doc-lifecycle-cache.json`
2. `drift-detection-hook.py` fires on every Write/Edit and checks if the content relates to tracked documents
3. If drift is detected, you get a reminder to check related documents

### Your Responsibility
- When you add/change a product, service, pricing, team member, or process: think about what OTHER documents reference this information
- If drift-detection reminds you about related documents: check them and update if needed
- If drift-detection is NOT firing (empty cache, no reminders): that itself is an issue -- report it via work-request.py

### Session Start: Cache Refresh
Every session start should refresh the document cache:
```bash
python ~/.claude/scripts/doc-cache-builder.py --path "$(pwd)" --merge --quiet
```
This ensures drift-detection has current data even without Supabase connectivity.

## Pushback Protocol (NON-NEGOTIABLE)

Never be a yes-agent. Before agreeing with any user design decision, ask: "Am I agreeing because this is right, or because the user suggested it?"

- If an approach has trade-offs the user hasn't considered, name them BEFORE agreeing
- If there's a simpler or more reliable way, say so even if the user is excited about their idea
- If the approach won't work technically, say so directly with the reason and an alternative
- If the user is over-engineering, call it out. Complexity is a cost.
- Frame pushback constructively: explain WHY it won't work and offer the alternative
- Trust requires honesty, not compliance. Agreement must mean "this is actually the right call."

## Proactive Autonomy Protocol (NON-NEGOTIABLE)

Every workspace must think, suggest, and act -- not wait for instructions. The goal is a fully autonomous, agentic system where workspaces actively help the company grow and improve.

### Three Tiers of Proactive Action

| Confidence | Action | Example |
|-----------|--------|---------|
| **100% -- clearly needed** | Build it, then report what you did and why. Don't ask permission. | "I noticed the sync script doesn't handle network timeouts. I added retry logic and deployed it." |
| **High confidence -- strong suggestion** | Pitch it with reasoning. Explain why it matters and what it fixes. | "The CEO brief query doesn't filter tabled projects. This causes noise. Recommend adding a filter -- want me to build it?" |
| **Lower confidence -- idea worth exploring** | Flag it as something to consider. Don't block on it. | "I noticed our error tracking doesn't cover n8n webhook failures. Worth investigating when we have capacity." |

### What "Proactive" Means in Practice

- **During any task:** If you see something broken, suboptimal, or missing while doing other work -- don't ignore it. Either fix it (100% confidence), pitch it, or file a work request.
- **During audits and reviews:** Don't just check boxes. Ask "what else could go wrong here?" and "what would make this better?"
- **During builds:** Don't just build what was asked. Ask "what's the next thing that will break or be needed?" and either build it or flag it.
- **Cross-workspace awareness:** If you discover something that affects another workspace, route it immediately via work request or routed task. Don't assume someone else will notice.

### What This Is NOT

- Not an excuse to over-engineer or add unnecessary complexity. Pushback Protocol still applies.
- Not permission to ignore the user's priorities. User instructions always take precedence.
- Not a license to build speculative features. Proactive means solving real problems you can see, not hypothetical ones.

### Why This Exists

The system must operate autonomously while the owner focuses on revenue generation and family. Every hour the owner spends debugging infrastructure or pointing out obvious improvements is an hour not spent closing deals. The workspaces must carry the operational load -- thinking, identifying, fixing, and improving without being asked.

## Correction Capture Protocol (NON-NEGOTIABLE)

When the user corrects you -- tone, style, approach, factual error, preference -- capture it immediately. Do NOT wait for session-checkpoint. Corrections are the highest-value learning signal.

### What Triggers Capture
- **Direct corrections:** "No, not like that" / "Too formal" / "More direct" / "That's wrong"
- **Positive confirmations of non-obvious choices:** "Perfect" / "Yes, exactly like that" / "Keep doing that"
- **Style/voice feedback:** "I wouldn't say it like that" / "More like how I'd actually say it"
- **Behavioral corrections:** "Don't do X" / "Stop doing Y" / "Always do Z"

### What To Capture
For each correction, run TWO commands:

**1. Voice sample** (captures the content for voice profile learning):
```bash
python ~/.claude/scripts/voice-write.py voice rejected <content_type> <audience> "<rejected content>" --reason "<user's exact words>"
python ~/.claude/scripts/voice-write.py voice approved <content_type> <audience> "<corrected content>" --reason "<what user wanted instead>"
```
Content types: email, proposal, slack, documentation, social, internal, code, comment
Audiences: client, prospect, internal, partner

**2. Activity stream event** (tracks correction frequency for trend analysis):
```bash
python ~/.claude/scripts/voice-write.py correction "<what was corrected and why>" --workspace "<current-workspace>"
```

### When NOT To Capture
- Factual questions ("What does this function do?") -- not corrections
- Task instructions ("Add a button here") -- not corrections
- Bug reports ("This is broken") -- tracked by error-tracker, not this

### Why This Exists
Dream consolidation synthesizes voice samples nightly into distilled rules. Without input data, the voice phase finds 0 samples. Every uncaptured correction is a lost learning signal. The correction rate metric (trending down = system is learning) requires real-time capture to be meaningful.

## Verify Before Acting Protocol (NON-NEGOTIABLE)

Before running ANY script, tool, or command referenced in a skill, workflow, MEMORY.md, or doc:

1. **Verify it exists on disk.** Run `ls` or `find` on the path. If the file doesn't exist, STOP.
2. **Check what DOES exist.** Look in `tools/`, `scripts/`, and the workspace directory for alternatives that serve the same purpose.
3. **Never report "blocked" or "missing" without checking alternatives.** The tool you need may exist under a different name or path.
4. **Never claim a system is broken because a skill told you to run something that doesn't exist.** The skill is wrong, not the system.

**Why this exists:** During Foundation Reset Phase 3, a skill referenced `checkpoint.py` -- a script that was planned but never built. The session followed the instruction blindly, reported "blocked by missing plugin," and failed to recognize that `supabase-sync.py` (the actual working tool) was right there in `tools/`. This happened during a cleanup session, eroding trust in the system's ability to self-correct. Phantom references in skills and docs must be caught at execution time, not trusted blindly.

## Investigation Protocol (NON-NEGOTIABLE)

When investigating bugs, unexpected behavior, system failures, recurring issues, or any situation requiring a hypothesis-test cycle -- INVOKE `superpowers:systematic-debugging` BEFORE generating hypotheses.

The skill enforces structured root-cause analysis: gather evidence first, enumerate hypotheses, test cheapest first, document falsifications. Without it, ad-hoc debugging tends to anchor on the first plausible-sounding cause and miss systemic issues.

**Triggers:**
- Unexpected file states (items moving without action, stale data, missing artifacts)
- Tool/script failures or unexpected output
- "This is weird" / "I can't figure out why" / "It worked yesterday"
- Recurring pattern of the same symptom across sessions
- Any time you start a sentence with "I think the problem is..."

**Past incident (2026-04-19, HQ):** Investigation of cron-fired autonomous inbox processing succeeded in finding root cause, but skipped systematic-debugging skill. Pattern at-risk: ad-hoc debugging without methodology might miss systemic issues that the formal skill would surface. Filed as wr-2026-04-19_workforce-hq_systematic-debugging-skipped-during-cron-investigation.

The `methodology-nudge.py` global hook enforces this at runtime by detecting 2+ edits to the same file (a typical patch-iteratively-instead-of-investigate signal) and nudging the skill.

## MCP Auth Errors -- Check Inputs FIRST (NON-NEGOTIABLE)

When ANY MCP tool returns "permission denied", "unauthorized", "auth failed", "invalid token", or similar credential errors, the FIRST hypothesis to check is YOUR INPUT, not the provider. Before speculating about OAuth revocation, integration downgrade, API rollouts, or scope changes:

1. Verify the credential value (look up in .env, compare to what you passed)
2. Verify the target identifier (project_id, workspace_id, account_id) matches what your .env / docs say
3. Look up your own audit/inventory docs (workforce-hq/.tmp/credential-audit-workforce-hq.md, etc.)
4. THEN, if input is verified correct, escalate to provider hypotheses

The cheapest, highest-prior cause is "wrong input." Provider-side regressions are rare. If the cron-fired `mcp-auth-error-guard.py` hook injects a reminder, treat it as authoritative -- invoke `superpowers:systematic-debugging` immediately.

Past incident (2026-04-17): Sentinel session ran 10+ turns of unstructured provider speculation when Supabase MCP rejected calls. Real cause: wrong project_id (passed wkbpstfbilfhhcabqfdj, actual was dgnjfamhwfyogmgcpedb). User had to interrupt with "are you confused?" The mcp-auth-error-guard.py hook now enforces this.

## Scheduling Tool Rules (NON-NEGOTIABLE)

Before using ANY tool for scheduling or automation, verify what it actually does. Never assume from the name.

**Ownership:** Each workspace owns the scheduled tasks and automations that support its systems. See `~/.claude/docs/autonomous-systems-inventory.md` for the full ownership map. Modify automations from the workspace that owns them.

**Tool hierarchy (verified 2026-04-09):**
- **n8n cloud** = PRIMARY for 24/7 tasks that don't need local filesystem (CEO briefs, cloud monitoring). Runs at sharkitect-solutions.app.n8n.cloud regardless of machine state.
- **Windows Task Scheduler** = PERSISTENT LOCAL for tasks needing local filesystem when computer is on (gap alerting, brief fallbacks, freshness audits). Use full python.exe path in .bat files.
- **CronCreate** = IN-SESSION ONLY for AI-powered inbox polling (all workspaces). Triage-only when user is active, autonomous processing when idle. Dies on session close. 7-day auto-expire. Recreated each session via startup guard. See Mid-Session Inbox Polling Protocol.
- **RemoteTrigger** = BROKEN for MCP-dependent tasks. MCP cold-start race condition (tools not registered at session init). Do NOT use for anything requiring Supabase, Gmail, Calendar MCPs. Documented in lessons-learned.md.
- **ralph-loop** = Task iteration loop ONLY. Keeps AI working on one task by intercepting Stop event. Has NO timer, NO interval, NO cron. Use for: iterative code improvement, plan execution overnight. NEVER for polling or scheduling.
- **session-startup-guard.py** = SessionStart hook. 3-state heartbeat. Checks inboxes and cron status. Creates CronCreate jobs if missing.

Each workspace has a `workflows/cron-schedule.md` listing its specific CronCreate jobs.

## Iterative Work Protocol (NON-NEGOTIABLE)

When work requires build-test-fix cycles, invoke `/ralph-loop` BEFORE starting the first attempt. Do NOT make one attempt, report the result, and wait for the user to say "try again."

### What triggers ralph-loop:
- **Building a new tool or script** -- run it, check output, fix errors, re-run until it works
- **Fixing a bug or broken system** -- apply fix, test, verify, iterate if still broken
- **n8n workflow fixes** -- apply change, test execution, check result, iterate
- **Skill/agent creation or optimization** -- build, judge, fix issues, re-judge until gate passes
- **Any task where "did it work?" requires testing** -- don't guess, test and iterate

### What does NOT need ralph-loop:
- Pure research, reading, or analysis (no test step)
- Simple file edits where correctness is obvious (updating a config value, fixing a typo)
- Tasks the user explicitly says they want to review before iteration

### The rule:
1. Recognize that the task is iterative (has a test/verify step)
2. Invoke `/ralph-loop` at the start
3. Build -> Test -> Check result -> Fix if broken -> Repeat
4. Report to user only when it's DONE and working, or when you're genuinely stuck after multiple attempts

**Why this exists:** The user should not have to sit through attempt -> fail -> "try again" -> fail -> "try again" cycles. The system handles iteration autonomously. The goal is 98% of work arriving at the user already fixed and verified.

## Supabase Status Sync Protocol (NON-NEGOTIABLE)

Supabase is the source of truth for project and task status. Local plan files, MEMORY.md, and todo lists are working copies. If Supabase is stale, other workstations and CEO briefs see outdated information.

### When to update Supabase immediately (do NOT wait for session-checkpoint):
- **Plan phase completed** -- update project status/phase AND mark related tasks as `completed`
- **Task finished** -- update task status to `completed` immediately after verifying the work
- **Project paused/blocked/unblocked** -- update project status immediately when the decision is made
- **New task discovered** -- add it to Supabase when identified, not at session end
- **New tasks from a plan** -- when a plan creates tasks for this workspace, add them to Supabase immediately

### How to update:
```bash
# Update project status + phase
python ~/.claude/scripts/update-project-status.py project "<name>" <status> --phase "<phase>" --notes "<notes>"

# Update task status
python ~/.claude/scripts/update-project-status.py task "<task-text>" <status> --project "<project>"

# Create a new task (with workspace assignment)
python ~/.claude/scripts/update-project-status.py add-task "<task-text>" --project "<project>" --workspace "<workspace>" [--priority high] [--depends-on "<id1,id2>"]

# Add dependency: task A depends on task B completing first
python ~/.claude/scripts/update-project-status.py add-dependency "<task-text>" --depends-on "<blocker-task-text>"

# Check if your blockers have cleared
python ~/.claude/scripts/update-project-status.py check-blockers --workspace "<workspace>"

# See all tasks assigned to your workspace
python ~/.claude/scripts/update-project-status.py my-tasks --workspace "<workspace>"
```

### Automatic cascades (handled by the script):
- **Project set to `paused`** -- all non-completed tasks automatically drop to `low` priority
- **Last task completed** -- project auto-completes when all its tasks are done

### Cross-Workspace Task Tracking (NON-NEGOTIABLE)

Every task in Supabase MUST have an `assigned_workspace`. This is how workspaces know what belongs to them and how CEO briefs show progress across the full operation.

**Rules:**
1. **Single-workspace projects:** Tasks inherit the project's workspace. Set `assigned_workspace` when creating tasks.
2. **Global projects (multi-workspace):** Each task is assigned to the workspace responsible for completing it. Example: Foundation Reset Phase 5A = `workforce-hq`, Phase 5B = `skill-management-hub`, Phase 5C = `sentinel`.
3. **Dependencies:** When a task can't start until another workspace finishes something, use `add-dependency` to encode it in Supabase. Never rely on verbal coordination through the user.
4. **Session start blocker check:** Every workspace runs `check-blockers --workspace <name>` at session start (automated by session-startup-guard). If blockers have cleared, proceed with the unblocked work immediately without waiting for user instruction.
5. **Visibility:** Any workspace can run `my-tasks --workspace <other>` to see another workspace's queue. This is how workspaces discover each other's progress autonomously.

### Carried days recalculation (runs at session start):
On FULL_STARTUP (first session of a new day), the session-startup-guard triggers:
```bash
python ~/.claude/scripts/update-project-status.py recalc-carried-days
```
This sets `carried_days = (today - created_at)` for ALL non-completed tasks -- including paused and deferred. We track everything; CEO briefs filter which statuses to display at query time.

**Stale review**: Tasks paused or deferred for 30+ days are flagged in the script output. When flagged, review each one: reactivate, keep deferred/paused (which resets the counter next time the status is explicitly set), or delete from the task list. This prevents stale projects and ideas from sitting indefinitely.

### Session-checkpoint Step 8B is the BACKUP, not the primary sync:
Step 8B catches anything missed during the session. But the goal is: by the time session-checkpoint runs, Supabase should already be current. Step 8B should find nothing to update.

**Why this exists:** Sessions completed work but never updated Supabase. CEO briefs showed zero completions. Work done in one workspace was invisible to others. Supabase must stay current as the cross-machine source of truth.

### Supabase Ownership Protocol (NON-NEGOTIABLE)

Each workspace owns its own Supabase records -- ALL tables, not just projects and tasks. This includes documents, health components, brain memories, kb_docs, and any future tables. No workspace creates, modifies, or deletes another workspace's records in ANY Supabase table unless the user explicitly authorizes it.

**Rules:**
1. **Only the owning workspace writes its own records.** If Skill Hub discovers that HQ needs a project, document, or any Supabase entry, it routes a task to HQ's inbox describing what's needed. HQ creates it. Skill Hub does NOT insert HQ rows into any Supabase table.
2. **Only the owning workspace updates its own records.** If Sentinel notices that an HQ project is stale or a document is outdated, it routes a finding to HQ. Sentinel does NOT update HQ's records.
3. **Read is global, write is local.** Any workspace can query any other workspace's records for visibility (briefs, audits, blocker checks). But writes are local -- you only touch your own rows. The ONLY exception is explicit user authorization ("go ahead and update HQ's project from here").
4. **No implicit exceptions.** Convenience is not authorization. "It would be faster to do it from here" is not a valid reason to write to another workspace's records. Route the task and let the owning workspace handle it.
4. **Plans = projects in Supabase.** Any planned initiative, even if not yet started, gets a Supabase project entry with status `pending`. This ensures full operational visibility. If a plan exists, a project must exist. CEO briefs can't report on what isn't in Supabase.
5. **Session-start Supabase audit.** Every workspace, on FULL_STARTUP, verifies that all its known projects, plans, and tasks are accurately represented in Supabase. If anything is missing, stale, or has wrong statuses/priorities/blockers -- fix it immediately. This is part of the session startup protocol.
6. **Scaffolding exception.** If a workspace creates a placeholder project for another workspace (e.g., during cross-workspace planning), it MUST flag this in the routed task as "scaffolded -- review and take ownership." The owning workspace reviews, adjusts, and confirms ownership at its next session.

**Why this exists:** When one workspace creates another's projects, it lacks full context -- wrong priorities, missing blockers, inaccurate descriptions. The workspace doing the work knows best. Ownership also ensures accountability: if a project is stale, exactly one workspace is responsible. Cross-workspace writes also risk conflicting updates. Read globally, write locally.

**What this enables:** HQ can pull from Supabase for morning/afternoon/evening briefs and accurately show:
- What each workspace is working on right now
- Upcoming projects and plans across the entire operation
- What was completed today
- What's blocked and by whom
- Full operational transparency without any workspace working in a silo

## Plan Lifecycle Protocol (NON-NEGOTIABLE)

Plans use random hash filenames (e.g., `wise-sprouting-canyon.md`). Without a registry, sessions waste time searching. A single global registry tracks ALL plans across ALL workspaces.

**Global registry:** `~/.claude/docs/plans-registry.md` -- ONE file, ONE source of truth. All workspaces read and write to this same file. No workspace-local copies.

### When a plan is CREATED:
1. Add a row to the Active Plans table in `~/.claude/docs/plans-registry.md` immediately (path, status, workspaces involved)
2. Reference it in the creating workspace's MEMORY.md Resume Instructions with the full path

### When a plan phase COMPLETES:
1. Update the Status and Phase columns in `~/.claude/docs/plans-registry.md`

### When a plan is FULLY COMPLETED:
1. Move the row from Active Plans to Completed Plans in the registry. Fill in Outcome and Lessons columns.
2. Archive the plan file to `plans/archive/` if it lives in `~/.claude/plans/`
3. Update MEMORY.md to reflect completion, not active status

### When a plan is ABANDONED:
1. Move to Completed Plans with status ABANDONED. Document why in Lessons column.
2. Follow Pivot Cleanup Protocol below for any artifacts it created
3. Add a lessons-learned.md entry for why it was abandoned

### Session-end responsibility:
Every workspace checks `~/.claude/docs/plans-registry.md` at session end and updates any plans it worked on during the session. This is part of the session-end protocol. Future: Supabase `documents` table will mirror this registry (Phase 4B of Foundation Reset).

**Why this exists:** Plans with hash filenames get lost. Sessions waste time searching the filesystem. Completed plans sit in registries misleading future sessions. Multiple workspace copies drift apart -- one global file eliminates that.

## Pivot Cleanup Protocol (NON-NEGOTIABLE)

When a build fails, an approach is abandoned, or a system is superseded by a new one:

1. **DELETE** all Windows Task Scheduler registrations created for the abandoned approach
2. **DELETE** all .bat files, Python scripts, and config files created for it
3. **DELETE** all RemoteTrigger configs created for it
4. **REMOVE** all CLAUDE.md references to it across affected workspaces
5. **UPDATE** MEMORY.md to remove false claims about it working
6. **UPDATE** workflow docs to remove references to the abandoned approach
7. **ADD** a lessons-learned.md entry documenting WHY it failed and what replaced it
8. **VERIFY** no remaining files, configs, or documentation reference the deleted artifacts

**Only exception:** The lessons-learned.md entry stays forever.

**Why this exists:** Multiple automation rebuilds left behind 7 dead Task Scheduler tasks, 3 broken RemoteTrigger configs, orphaned .bat files, and MEMORY.md entries claiming systems worked when they never ran. This accumulation misleads future sessions and erodes trust.

## .tmp/ Hygiene Protocol (NON-NEGOTIABLE)

`.tmp/` is a disposable folder. Only two kinds of files belong there: (a) files regenerated on demand by tools, and (b) genuine in-flight scratch for the current task. Anything else is a bug in file placement.

### What qualifies for .tmp/

| Category | Examples | Allowed? |
|----------|----------|----------|
| Tool-regenerated cache | `doc-lifecycle-cache.json`, `skills-manifest.json`, `capability-updates.json`, `last-sync.json` | YES -- re-created on demand, safe to delete |
| Active in-flight scratch | test output, intermediate audit data being used this session | YES -- must be pruned at task/session end |
| Config files tools depend on | `document-relationship-map.json`, any file a hook/script reads as config | **NO** -- move to workspace `.claude/<component>/` |
| Valuable artifacts | credential audits, Supabase schema exports, reusable scripts, n8n code exports | **NO** -- promote to `docs/`, `resources/`, or `tools/` |
| Delivered outputs | client deliverables, committed plans, published docs | **NO** -- these are not scratch |

Rule of thumb: if another tool/hook/script reads it, it is NOT scratch. If you would be upset if it disappeared, it is NOT scratch.

### Project-end prune rule

When a project, plan, or major task completes, audit `.tmp/` before closing:

1. List all `.tmp/` contents with size and purpose
2. Classify each: **keep** (active tool cache) | **promote** (valuable -> move to permanent home) | **delete** (true scratch)
3. Promote valuable files to their correct location BEFORE deleting anything
4. Delete remaining scratch
5. Verify: the post-audit `.tmp/` should be small (typically <1MB) and contain only regenerable caches

The `session-checkpoint` skill runs this audit as Step 6.5 -- do not skip it.

### Config-in-scratch is a bug

If a tool or hook reads its config from `.tmp/`, the tool is wrong, not the folder. Config files must live in `<workspace>/.claude/<component>/` (workspace-specific config) or `~/.claude/config/<component>/` (global config). Example migration: `drift-detection-hook.py` now reads `document-relationship-map.json` from `<workspace>/.claude/drift-detection/` (with `.tmp/` fallback only during the transition). Any other tool found reading config from `.tmp/` gets filed as a work request and migrated the same way.

### Source incident

2026-04-21 HQ session: `.tmp/` grew to 7MB with 54 items, including a credential audit, Supabase schema export, reusable template-builder scripts, and n8n code exports -- all sitting in a folder named "disposable." Also discovered `drift-detection-hook.py` was reading `document-relationship-map.json` from `.tmp/`, making a load-bearing config file vulnerable to accidental wipe. HQ filed wr-2026-04-21-002; Skill Hub owns the global rule and the hook fix.

### Enforcement

- **session-checkpoint Step 6.5:** `.tmp/` audit runs at every full-mode checkpoint, before git commit
- **drift-detection-hook.py:** reads `document-relationship-map.json` from `<workspace>/.claude/drift-detection/` first, falls back to `.tmp/` only during migration window
- **Gitignore posture:** `.tmp/` stays gitignored -- that is correct. The fix for "valuable file in .tmp/" is to move the file, not to track `.tmp/`.

## Documentation Standards (NON-NEGOTIABLE)

All workspaces follow the Documentation Standards SOP at `~/.claude/docs/documentation-standards.md`. This SOP defines:
- Every entity type (projects, tasks, plans, system health, lessons learned, etc.)
- Their allowed statuses (no inventing new ones)
- Required metadata fields
- Where each entity is stored (Supabase table + local file)
- How to create, update, and transition entities
- How to query for accurate, consistent data
- Canonical workspace names for Supabase fields

**Key rules from the SOP (summary — full details in the doc):**
1. **Supabase is the source of truth** — update Supabase FIRST, before local files
2. **Status updates are immediate** — not deferred to session end
3. **Use canonical workspace names** in all Supabase writes: `workforce-hq`, `skill-management-hub`, `sentinel`
4. **Every document needs metadata** — created date, updated date, owner. No exceptions.
5. **Use only allowed statuses** — projects: `active/pending/paused/blocked/tabled/complete`. Tasks: `pending/in_progress/completed/blocked/deferred/tabled`.

Sentinel audits compliance with these standards across all workspaces.

---

## Extension Rule

Workspace CLAUDE.md files define ONLY workspace-specific additions to these protocols. They should NOT duplicate items listed above, but if they do, this rule is authoritative.

If a workspace CLAUDE.md explicitly contradicts this rule (e.g., "do NOT run resource-auditor in this workspace"), the workspace CLAUDE.md wins for that workspace. This is the local override principle -- universal protocols are the baseline, workspace instructions can override for their specific context.