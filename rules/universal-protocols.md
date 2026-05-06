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
- [ ] **Preflight check before building new infrastructure (NON-NEGOTIABLE):** If the task involves creating a new automation, hook, script, report, workflow, Supabase table, or plugin, run `python <Skill Hub>/tools/preflight-check.py "<description>"` BEFORE designing or writing code. Review matches. Extend existing assets rather than duplicating. See the Verification-Before-Building Protocol below.
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

### Superseded vs Duplicate (NON-NEGOTIABLE)

Two additional close states for records that SHOULD NOT count as real rejections. Both are valid Supabase `cross_workspace_requests` close statuses (see Status Vocabulary Layers below). Use them when the decision rule in the previous subsection lands on "valid from origin" BUT the work is no longer live because newer work has absorbed or matched it.

| Close state | Use when | Example | Timeline it feeds |
|-------------|----------|---------|-------------------|
| **superseded** | A LATER filing renders THIS one obsolete. The earlier work was legitimate; it just got absorbed into or outdated by newer work. | wr-001 proposes approach X; wr-002 supersedes X with approach Y after new context. wr-001 closes as `superseded` with a `superseded_by` reference to wr-002. | Request-trend timeline (legitimate requests that got absorbed). NOT rejection. |
| **duplicate** | Another workspace independently filed the SAME thing. Whichever is older (or better-scoped) wins; the other closes as duplicate. | Sentinel files wr-X for a gap; HQ files wr-Y for the same gap two days later. Close the newer/weaker one as `duplicate`. | Filer-quality timeline as noise (both workspaces caught the same signal twice). NOT rejection. |

**Neither is the same as:**
- **rejected** -- declined on merits (valid but won't be done)
- **drift_correction** -- filed in error (should never have existed)

Both `superseded` and `duplicate` describe requests that were legitimate AND got completed elsewhere or absorbed -- no actual rejection signal.

**Required resolution metadata:**
- **superseded:** `resolution.superseded_by` = `item_id` of the newer request that absorbed this work. `resolution.resolved_by` = the closing workspace. `resolution.what_was_done` = short reason ("absorbed into wr-XXX after broader scoping discovered in [context]").
- **duplicate:** `resolution.duplicate_of` = `item_id` of the surviving request. `resolution.resolved_by` = the closing workspace. `resolution.what_was_done` = short reason ("duplicate of wr-YYY; [this workspace] filed same gap 2 days later, [other workspace's] filing is better scoped / older").

**Enforcement:** `close-inbox-item.py` accepts `--status superseded` and `--status duplicate` via the Supabase vocabulary. The script's status normalization (line ~116) collapses the three semantic close variants (`processed | completed | resolved`) into Supabase `completed`, but `superseded` and `duplicate` pass through as their own Supabase values -- so use the exact status flag to preserve the signal.

**Why this matters:** Without these states, workspaces face a false choice: `rejected` (inflates decline rate; hides real rejection signal) or `drift_correction` (requires delete + activity_stream event, inappropriate for legitimate absorbed work). The three close states are distinct metrics and must stay separated in the request-trend and filer-quality timelines.

**Source:** Sentinel wr-2026-04-22-018 (closed 2026-04-22). Sentinel flagged that three close states existed in Supabase without documented triggers; documented the disambiguation via Skill Hub (rule-file edits are Skill Hub territory per wr-2026-04-21-005 precedent).

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

### Status Vocabulary Layers (NON-NEGOTIABLE)

Three distinct status vocabularies exist, one per layer. Mixing them produces CHECK-constraint rejections and silent data loss. Source: wr-2026-04-21-008.

| Layer | Accepted values | Who uses it |
|-------|-----------------|-------------|
| **Local JSON inbox files** (`.work-requests/inbox/*.json`, `.routed-tasks/inbox/*.json`, etc.) | Open states: `new`, `pending`, `in_progress`, `deferred`, `blocked`. Close states: `completed`, `rejected`, `superseded`, `duplicate`, `withdrawn`. (Legacy historical files may show `processed | resolved` -- read-only history, not used for new closes.) | AI agents writing inbox JSON directly |
| **close-inbox-item.py output** | Close-only: `completed | rejected | superseded | duplicate | withdrawn`. Legacy `processed | resolved` accepted but auto-converted to `completed` with deprecation warning. Rejects all open-state values at close. | All workspaces closing inbox items |
| **Supabase `cross_workspace_requests.inbox_items_status_check`** | `pending | in_progress | deferred | blocked | completed | superseded | duplicate | rejected | withdrawn`. (Does NOT accept `new` or `processed`. `withdrawn` requires Sentinel migration -- routed task filed in plan Phase G.) | Supabase inserts/updates from any workspace |
| **Supabase `projects.status` CHECK** | `active | pending | paused | blocked | tabled | complete | rejected | withdrawn`. (Sentinel migration 2026-05-04 widened the CHECK to add `rejected` + `withdrawn` per wr-sentinel-2026-05-04-002. Schema also gained `closure_reason text` column for audit on the new states.) | `update-project-status.py project <name> <status>` and direct Supabase writes |
| **Supabase `tasks.status` CHECK** | `pending | in_progress | completed | blocked | deferred | tabled | rejected | withdrawn`. (Same migration. Note: rejected + withdrawn tasks DROP OFF the project's `total_tasks` rollup -- see Status Cascade and Rollup section below.) | `update-project-status.py task <text> <status>` and direct Supabase writes |
| **Supabase `goals.status` CHECK** | `active | at-risk | paused | achieved | missed | superseded | withdrawn`. Goals track outcomes (target_value + deadline) not work streams; progress is rolled up via `current_value` snapshots, not task counts. Source: wr-sentinel-2026-05-04-008; goals shipped 2026-05-04. | HQ rollup script + direct Supabase writes from any workspace that owns goals |

**close-inbox-item.py normalization (line ~116):**
```python
sb_status = 'completed' if status in {'processed', 'completed', 'resolved'} else 'rejected'
```
So the three semantic close variants collapse to `completed` in Supabase; only explicit `rejected` stays `rejected`.

**Rules for direct Supabase writes (bypassing close-inbox-item.py):**
1. Use Supabase vocabulary, NOT local JSON vocabulary. `new` -> use `pending`. `processed` -> use `completed`.
2. Do NOT insert `blocked` until the accompanying schema migration ships (see Part A below). Filed 2026-04-21-008 Part A to Sentinel: add `blocked` to the CHECK constraint. Until that lands, local JSON may hold status=`blocked` but Supabase rows should stay at `pending` with `blocked_by` metadata until the blocker clears.
3. `superseded` and `duplicate` are Supabase-only close states for records that should not count as real rejections. Use when a later filing supersedes earlier work or duplicates it.

**Status-vocabulary drift prevention:**
- Whenever you need to directly INSERT or UPDATE a row in `cross_workspace_requests`, reference this table first.
- If a CHECK rejection occurs, re-read this subsection rather than guessing at the right value.

### WR/RT/Lifecycle JSON Schema Contract (NON-NEGOTIABLE)

All work-request, routed-task, and lifecycle-review JSON files written into any inbox directory MUST conform to the schema below. The JSON `id` field is the SINGLE authoritative identifier; the filename is grep convenience only and MUST NOT be used to derive identity.

**Source:** wr-2026-04-25-007 (Skill Hub). Two collision bugs in the legacy v1 (`wr-YYYY-MM-DD-NNN`) format motivated the v2 schema:
1. **Creation-side collision:** Two workspaces filing on the same date both pick `wr-YYYY-MM-DD-005`. The Supabase POST then collides on `item_id` UNIQUE constraint.
2. **Close-side collision:** When a JSON had no top-level `id` field, `close-inbox-item.py` derived a Supabase row identifier from the filename, which collided with unrelated WR ids. Result (2026-04-25 batch close): 11 WRs' `resolution_summary` text written into wrong Supabase rows.

#### v2 schema (REQUIRED for all new files)

| Field | Type | Required | Format |
|-------|------|----------|--------|
| `id` | string | YES | WR: `wr-<workspace>-YYYY-MM-DD-NNN`. RT: `rt-<workspace>-YYYY-MM-DD-<slug>`. Lifecycle: `lifecycle-<workspace>-YYYY-MM-DD-<slug>`. |
| `id_format_version` | integer | YES | `2` |
| `source_workspace` | string | YES (WR) | Canonical name: `workforce-hq` / `skill-management-hub` / `sentinel` |
| `status` | string | YES | One of the 9 values per Status Vocabulary Layers (above) |

#### Workspace short-prefix map (canonical → short, used in `id`)

| Canonical | Short prefix |
|-----------|---------|
| `workforce-hq` | `hq` |
| `skill-management-hub` | `skillhub` |
| `sentinel` | `sentinel` |

#### Three-gate enforcement (defense-in-depth)

| Layer | File | When it fires | Failure mode |
|-------|------|---------------|--------------|
| **Creation** | `~/.claude/scripts/work-request.py` | Source workspace files a WR | Refuses to emit if workspace canonical name not in WORKSPACE_SHORT_MAP |
| **Write-time** | `~/.claude/hooks/inbox-json-validate.py` (PreToolUse Write) | Any agent edits inbox JSON | Denies Write if `id_format_version >= 2` AND id missing/malformed; v1 legacy without id passes |
| **Closure** | `~/.claude/scripts/close-inbox-item.py` | Closing item to processed/ | Refuses close if v2 file missing `id` field; v1 legacy fallback to `request_id`/`task_id` preserved for completion-notification routed-tasks |

#### Backward compatibility

Legacy v1 ids (`wr-YYYY-MM-DD-NNN` without prefix, no `id_format_version` field) remain readable everywhere. They are NOT auto-rewritten -- the backfill script (`~/.claude/scripts/wr-id-backfill.py`) only fills MISSING `id` fields on legacy auto-tool JSONs that never had one. It does NOT promote existing v1 ids to v2. This is deliberate: every v1 id already has a matching `cross_workspace_requests` row keyed by that v1 string. Rewriting locally to v2 without simultaneously rewriting Supabase keys would create the very drift this protocol is fixing.

Result: Supabase holds a permanent mix of v1 and v2 `item_id` strings. Both are valid query keys. ALL new WRs are v2; legacy v1 records are read-only history.

#### Bypass

To skip the write-time hook for emergency manual repair, include `skip wr-id-schema` in your next user message (or `skip json-validate` to skip both JSON-syntax + id-schema gates).

#### References

- Spec: `3.- Skill Management Hub/docs/superpowers/specs/2026-04-27-wr-id-schema-workspace-prefixed-design.md`
- Plan: `~/.claude/plans/2026-04-27-wr-id-schema-workspace-prefixed.md`
- Trigger WR: `wr-2026-04-25-007` (Skill Hub) -- close-side filename-fallback collision discovered during 2026-04-25 batch close of 11 WRs.
- Tests: `~/.claude/tests/test_wr_id_schema.py` (12 cases covering all 3 gates)

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

## In-Session Close-Out Workflow Contract (NON-NEGOTIABLE)

Every workspace closes inbox items (work requests, routed tasks, lifecycle reviews) using a 5-step contract. The contract is enforced by `~/.claude/scripts/close-inbox-item.py` -- the canonical close path. Direct `mv` from inbox/ to processed/ + manual JSON edit is PROHIBITED (it caused the historical drift class reconciled by wr-sentinel-2026-04-29-001).

### The 5 steps

| Step | Name | Enforcement | Bypass |
|------|------|-------------|--------|
| 1 | **Backup-verify** | Refuse close if any path in `--artifacts-created` / `--artifacts-modified` has uncommitted git changes in the workspace repo | `--skip-backup-check --skip-backup-reason '<text >= 10 chars>'` (logged in `resolution.backup_check_skip_reason`) |
| 2 | **Move** | inbox/ -> processed/ via atomic `os.replace` | none -- always runs |
| 3 | **Acknowledge** | Auto-write completion-notification routed-task to source workspace's inbox per Completion Notification Protocol | `--no-notify --no-notify-reason '<text>'` (anti-ping-pong, self-filed, kind=completion_notification) |
| 4 | **Supabase update** | PATCH `cross_workspace_requests.status` + `resolution_summary` + `resolved_at` + `resolved_by` + `last_updated_by` | `--no-supabase` (testing only) |
| 5 | **Close-out verify** | Re-read the row; assert `status` is in close vocabulary AND `resolution_summary` is non-empty | none -- always runs when Supabase update succeeded; soft-fail (warns to stderr without undoing the close) |

Steps 2/3/4 were already enforced by close-inbox-item.py before 2026-04-29. Steps 1 and 5 were added as part of the close-out contract to prevent the drift class observed in the 2026-04-29 status-drift audit.

### Why each step exists

- **Step 1 (backup-verify):** A close that moves the inbox file but leaves the work itself uncommitted means the resolution describes work that exists only in the working tree. If that machine dies, restarts, or the directory is wiped, the work is gone but the inbox says "completed." The gate forces backup before move.
- **Step 2 (move):** Existing -- the close-inbox-item.py atomic rename (write tmp, replace, unlink).
- **Step 3 (acknowledge):** Without active push back to the originator, completion is invisible to the requester. Existing -- enforced by Completion Notification Protocol.
- **Step 4 (Supabase update):** Existing -- writes the close vocabulary and resolution_summary to the canonical brain row.
- **Step 5 (close-out verify):** PATCH return code can be misleading (200 with empty body, racing writes, schema constraint quirks). Re-reading the row makes the post-condition observable. If verify fails, the inbox file already moved and the PATCH already returned success -- so this is a soft-fail warning, not a rollback. The point is to know about drift in real time instead of discovering it during a quarterly audit.

### Backup-verify scope (current v1)

The gate currently checks the workspace where the inbox file lives (most workspace artifacts live there). For artifacts under `~/.claude/` (skills, hooks, scripts, agents, rules, config), `~/.claude/` itself is not a git repo on standard installs -- the toolkit repo at `<Skill Hub>/sharkitect-claude-toolkit/` mirrors those paths via `sync-skills.py`. v1 of the gate does NOT check the toolkit mirror, so an artifact under `~/.claude/` that isn't yet synced to the toolkit will pass the gate even if not durably backed up. Discipline: run `python <Skill Hub>/tools/sync-skills.py --sync --push` BEFORE closing any inbox item whose artifacts include `~/.claude/` paths. v2 of the gate (future WR) will mirror-check the toolkit repo so this discipline is enforced rather than asked.

### Close-out verify scope (current v1)

v1 verifies the cross_workspace_requests row only -- status reached close vocabulary AND resolution_summary populated. v2 will additionally check related Supabase rows (tasks, projects, assets) whose foreign-key references touch the closed item_id, per Sentinel's recommendation in wr-sentinel-2026-04-29-002. v2 needs a schema-link discovery pass first (which fields on which tables reference cross_workspace_requests.item_id?) and is filed as a follow-up.

### Trigger and source

- **Trigger:** wr-sentinel-2026-04-29-002 (after Sentinel's status-drift audit on 2026-04-29 found 12 phantom rows whose local close happened pre-protocol -- between 2026-04-16 and 2026-04-18, before close-inbox-item.py existed). User explicitly requested the contract: "verify backup of the work itself, move it, acknowledge, update Supabase, close-out verify."
- **Audit document:** `4.- Sentinel/docs/audits/status-drift-audit-2026-04-29.md`
- **Reconcile WR:** wr-sentinel-2026-04-29-001 (12 historical rows fixed via `wr-supabase-reconcile.py --historical-manifest`).

### Enforcement summary

- Step 1 hard-blocks at close time unless explicitly bypassed with reason.
- Steps 2/3/4 were already hard-enforced.
- Step 5 logs to stderr on failure but does not undo the close (the close has already happened by the time verify runs; the verify makes drift observable).
- All steps run in order from a single CLI invocation -- callers do not orchestrate them.
- Direct `mv inbox/X processed/X` + manual JSON edit is PROHIBITED. The inbox-move-guard hook also blocks this at runtime; this contract documents WHY.

## Completion Notification Protocol (NON-NEGOTIABLE)

Applies UNIFORMLY to routed-tasks AND work-requests. Closes the inbox-driven coordination loop so completed cross-workspace work is never invisible to the originator.

### Why this exists

The Cross-Workspace Routed Tasks Protocol and Work Request Protocol cover SENDING and CLOSING. They do NOT cover NOTIFYING the originator of completion. Without active notification, completed work moves silently from `inbox/` to `processed/` in the receiver workspace, and the originator never finds out. Result: tasks "complete" but the system behaves as if they're still pending. The user becomes the messenger between workspaces, defeating the autonomy model.

The Blocker-Cleared Notification Protocol (below) covers a narrow case -- the originator already had a blocked inbox item waiting on this work. That covers maybe 10% of cross-workspace flows. The Completion Notification Protocol covers the other 90%: routed tasks and work-requests that the originator filed and then mentally moved on from.

Source: wr-2026-04-25-002 (Sentinel). Filed during AutoFix v2 schema migration when Sentinel completed verified work and the user observed HQ would never know unless explicitly notified mid-session.

### Two-sided contract

#### Requester side (NON-NEGOTIABLE)

Every routed-task JSON written into another workspace's `.routed-tasks/inbox/` AND every work-request JSON written into Skill Hub's `.work-requests/inbox/` MUST include:

```json
{
  "notify_on_completion": true,
  "notify_inbox_path": "<absolute path to requester's .routed-tasks/inbox/>",
  "notification_filename_hint": "rt-<YYYY-MM-DD>-<original-task-slug>-completed-by-<completer-workspace>.json"
}
```

`notify_on_completion: false` is permitted ONLY for fire-and-forget informational notifications that explicitly do not need acknowledgement (`kind: completion_notification` or `kind: fyi`). All work requests, all task assignments, all bug reports, all enhancement requests must be `true`.

`work-request.py` and routed-task tooling auto-inject these fields when present. If you hand-write a routed-task JSON (without tooling), you MUST include them yourself.

#### Completer side (NON-NEGOTIABLE)

When closing an inbox item via `close-inbox-item.py` whose `routed_from` (or `source_workspace` for work-requests) is a DIFFERENT workspace than the closing workspace AND whose `notify_on_completion` is `true` (or is missing -- defaults to `true` for safety), the closer MUST write a notification routed-task into the originator's `.routed-tasks/inbox/`.

The script does this automatically: `close-inbox-item.py` defaults to `--notify-source` ON for cross-workspace closures and emits the notification using the canonical schema. Manual `--no-notify` is permitted only with `--no-notify-reason "<text>"` and is reserved for: (a) closing a `kind: completion_notification` (would cause infinite ping-pong), (b) self-filed items where the completer == originator.

The notification has these required fields:

```json
{
  "task_id": "<derived from notification_filename_hint>",
  "kind": "completion_notification",
  "routed_from": "<this workspace>",
  "routed_to": "<originator workspace>",
  "completes_task_id": "<original task id>",
  "what_was_done": "<copy of --what-was-done>",
  "verification_summary": "<key proof points>",
  "what_originator_can_do_now": ["..."],
  "fix_instructions": "Acknowledge this notification by closing it via close-inbox-item.py with --status processed.",
  "notify_on_completion": false
}
```

The notification is itself a routed-task and itself follows the protocol -- but with `notify_on_completion: false` to avoid infinite ping-pong.

#### Ack side (NON-NEGOTIABLE)

When a workspace finds a `kind: completion_notification` item in its own `.routed-tasks/inbox/`, it MUST close it via `close-inbox-item.py` with `--status processed` within the next session start or idle poll. This is short, low-effort acknowledgement work -- the originator confirms it received and processed the news, optionally takes downstream action (e.g. flip a feature flag, update a project status), and closes. The completer can then trust that its notification landed.

Notifications carry the closing workspace's `verification_summary` and `what_originator_can_do_now` array, so the originator usually has everything it needs to act without re-reading the original task.

### Filename convention

`rt-<YYYY-MM-DD>-<original-task-slug-truncated>-completed-by-<completer-workspace>.json` -- placed in originator's `.routed-tasks/inbox/`. The slug is the human-readable portion of the original `task_id` / `id` / `request_id`, max 60 chars. If the originator provided `notification_filename_hint`, use that verbatim.

### Tooling enforcement

1. **`~/.claude/scripts/close-inbox-item.py`** has a `--notify-source` flag (default ON when `routed_from` / `source_workspace` ≠ current workspace AND `notify_on_completion` ≠ `false`). When ON, the script auto-writes the notification routed-task using a deterministic template populated from the closing item's metadata plus the `--what-was-done` value, the `--verification-summary`, and the `--what-originator-can-do-now` arguments. Set `--no-notify` (with `--no-notify-reason "<text>"`) only when the closing item is a `kind: completion_notification` or self-filed.

2. **`~/.claude/scripts/work-request.py`** auto-injects `notify_on_completion: true` and `notify_inbox_path` on every WR it writes. The script knows the source workspace; deriving the `.routed-tasks/inbox/` path is mechanical via the workspace canonical-name → path map.

3. **`~/.claude/hooks/notification-write-verify.py`** is a PostToolUse hook that fires after `close-inbox-item.py` invocations on cross-workspace items. It verifies a corresponding notification file landed in the source workspace's inbox. If not, it emits strong corrective context with the exact CLI to run to remediate. Soft failure mode -- the close itself already happened; the hook ensures the notification follow-through is not forgotten.

4. **Template:** `~/.claude/docs/templates/completion-notification-rt-template.json` is the canonical notification schema. The close script and any hand-written notifications populate from this template.

### Memory propagation

Every workspace's `MEMORY.md` references this protocol so it gets reinforced at session start. Each workspace's memory directory contains a `feedback_completion_notification_protocol.md` topic file capturing the failure mode (silent completion) identified by the user during AutoFix v2 schema migration on 2026-04-25, and the rule going forward: completion is an active push, not a passive pull.

### Exemptions

- **Self-filed items** (`routed_from == routed_to` or `source_workspace == closing workspace`): no notification needed.
- **Items where `notify_on_completion: false` was explicitly set by the originator:** no notification.
- **`kind: completion_notification` items themselves:** the ack closure does NOT generate a follow-up notification (would cause infinite ping-pong).
- **`kind: fyi` items:** by definition fire-and-forget, no acknowledgement expected.
- **Lifecycle reviews:** they have their own dispatch / close cycle; the dispatcher knows when work is done.

### Concrete example (the originating incident)

`rt-2026-04-24-autofix-v2-schema-complete` (HQ → Sentinel) was completed and verified by Sentinel on 2026-04-25. Without this protocol, HQ would have had no way to know. With this protocol:
1. HQ's outgoing routed-task included `notify_on_completion: true` + `notify_inbox_path` (HQ's `.routed-tasks/inbox/`).
2. Sentinel ran `close-inbox-item.py --notify-source` (default ON), which auto-wrote `rt-2026-04-25-autofix-v2-schema-complete-completed-by-sentinel.json` into HQ's inbox.
3. HQ's session-startup-guard surfaces the notification at next session start.
4. HQ acknowledges by closing the notification with `--status processed`, optionally flipping `AUTOFIX_V2_MODE=on` as the downstream action.
5. Loop closed. Both sides know the work is done.

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
- **User-Review Flag Honor (NON-NEGOTIABLE).** Idle Mode MUST NOT auto-apply items whose `fix_instructions`, `resolution.what_was_done`, completion-notification body, or any free-text field carries an explicit user-review marker. Triggering markers (case-insensitive substring match): "warrants user review", "warrants explicit user review", "requires user decision", "requires user approval", "requires user review", "explicit user approval", "needs user decision", "user must decide", "user must approve", "presenting for review", "for user review", "requires_user_review: true", or any text indicating the originator wants the user to choose between options before action is taken. Items also carry an explicit `requires_user_review: true` JSON field as a structured guard. **Behavior on match:** Idle Mode leaves the item in inbox, appends a `cron_held_for_user_review` array entry to its JSON with timestamp + matched marker text + cron session id, and skips processing. The item surfaces in the next ACTIVE-mode triage briefing where the user decides. Cross-system rule: this applies whether the marker appears on a work request, routed task, lifecycle review, or completion notification linked to one of those. **Why:** 2026-04-27 incident -- cron-fired session PID 59368 auto-applied option (a) of a cascade-mirror exemption decision because Skill Hub's completion notification framed it as a recommendation; the explicit "warrants explicit user review" caveat in the same notification was overridden by Tier 1 Proactive Autonomy. Today's outcome happened to align with user intent, but the next will not always. Source: wr-hq-2026-04-27-007.
- **System-Configuration Edit Hold (NON-NEGOTIABLE).** Even when no user-review marker is present, Idle Mode MUST NOT auto-apply changes to `~/.claude/CLAUDE.md`, any workspace `CLAUDE.md`, `~/.claude/settings.json`, any workspace `.claude/settings*.json`, or any file under `~/.claude/rules/`. Such items become triage-only by default and surface to the user. **Why:** these files affect every future session in every workspace; misapplied changes compound silently and are expensive to detect post-hoc. The Tier 1 Proactive Autonomy clause does not extend to system-wide configuration. Today's enforcement is via the runtime self-modification gate (which denied this very edit autonomously); the rule formalizes the principle so future cron sessions know to triage rather than retry under proactive-autonomy framing.
- When the user returns, show a brief summary of what was processed while they were away AND what was held for user review.

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

## Brain Dump Capture Protocol (NON-NEGOTIABLE)

When the user drops information, ideas, questions, or strategic topics that are off-topic-but-relevant during in-flight work, the AI MUST capture them WITHOUT derailing the current session. This is the universal pattern for every workspace, not just one. Pattern proven 2026-05-06 (Skill Hub S28); user direction (verbatim): *"this is perfect, exactly what it's meant to be... I want this to be a global protocol."*

### Trigger signals (any one fires capture)

- **Explicit:** "brain dump this," "side note," "off topic but," "this reminds me," "while I'm thinking about it," "park this for later," "different topic but"
- **Slash command (when built):** `/brain-dump <text>`
- **Detected drift mid-task:** user message that introduces 2+ new strategic topics while a focused task is in progress (heuristic: ≥3 distinct subject changes vs. the active todo)
- **AI judgment:** if the user's message is going to derail the current task AND contains forward-looking ideas worth preserving, capture without being told

### What the AI MUST do

| Step | Action |
|---|---|
| 1 | **Acknowledge briefly** -- one sentence, plain language, confirming you heard the dump and you're parking it |
| 2 | **Capture preliminary thoughts AT DUMP TIME** -- frozen snapshot of your initial reactions per topic. These don't have to be deep; they exist so the eventual conversation has a starting point that isn't blank. The user explicitly wants these preserved: *"document all of that so we don't forget what your original thoughts are."* |
| 3 | **Park to `<workspace>/brain-dump/YYYY-MM-DD-<short-slug>.md`** with frontmatter (date, session_context, status=new, relates_to, priority, ai_preliminary_thoughts) and body sections (raw dump, preliminary thoughts per topic, triage decision placeholder, action taken placeholder) |
| 4 | **Answer ONLY the tactical questions** in the dump that are blocking immediate progress (yes/no, do-now/defer, single-step decisions) |
| 5 | **Continue the in-flight task** as if the strategic items don't exist for the current session -- they're parked, not pending |

### What the AI MUST NOT do

- Write a full deep response to strategic questions
- Start implementing anything from the dump
- Spawn TodoWrite items for parked topics (those go in the brain-dump file, not the active todo list)
- Open a plan file or run brainstorming/writing-plans for parked topics
- Mention the dump in the in-flight task's deliverable
- Ask permission to capture -- capture is automatic, the user has already authorized this protocol

### Folder structure (every workspace)

```
<workspace-root>/
  brain-dump/
    README.md              # protocol explanation + frontmatter template
    YYYY-MM-DD-<slug>.md   # one file per dump (date-sortable)
```

The `README.md` template ships once from Skill Hub at workspace instantiation; from there each workspace owns its own brain-dump folder. Folder is git-tracked (it's not scratch -- these are forward-looking commitments).

### Frontmatter template

```yaml
---
date: YYYY-MM-DD
session_context: <what was being worked on when the dump happened>
status: new | triaged | absorbed | new-project-pending | follow-up | dropped
relates_to: <project name(s) if applicable>
priority: low | medium | high | critical
ai_preliminary_thoughts: <captured at dump time so they're not lost>
---
```

### Sweep cadence (when triaged + acted on)

- **Session start (preferred)** -- before new task work begins, AI checks `brain-dump/` for items with `status: new` and surfaces them in the startup status table. User decides per-item: discuss now, defer to specific session, drop. Items that get discussed/acted on move to `status: triaged`.
- **Session end** -- session-checkpoint sweeps and confirms each entry has either been acted on or has a clear next-touch decision recorded.
- **On demand** -- user types "sweep brain dumps" / "triage brain dumps" any time.
- **Sentinel weekly review (when built)** -- entries older than 14 days flagged as stale; routed for forced-decision.

### Triage decision categories

When sweeping, each entry resolves to one of:

| Decision | Action |
|---|---|
| **Absorb-into-current-project** | Update related Supabase project / WR / plan; mark entry `status: absorbed` |
| **New project** | File new Supabase project (`status: pending`); add to `~/.claude/docs/plans-registry.md`; mark entry `status: new-project-pending` |
| **Follow-up question** | Park as discussion item for next relevant session; mark entry `status: follow-up` with `next_touch` date |
| **Drop** | On review, decided not worth pursuing; mark entry `status: dropped` with one-line reason. Stays in folder as historical record |

### Implementation tiers

This protocol ships in three tiers, in order:

1. **v0 (NOW, manual)** -- folder + MD files + AI-side discipline per the rules above. No tooling required. ALREADY LIVE in Skill Hub from S28; pattern proven.
2. **v1 (next build)** -- workspace-startup-guard auto-creates `brain-dump/` folder + README.md if missing. Surfaces `status: new` count at session start. Routes to a follow-up WR when implemented.
3. **v2 (future)** -- in-session detection hook (PreToolUse on user prompts catches the trigger phrases listed above) AND `/brain-dump` slash command for explicit invocation. Both write to the same folder structure.

### Why this exists

The user demonstrated the failure mode: while focused on one task, ideas come up that pertain to other workspaces or future projects. Without a capture mechanism, those ideas are lost when the session ends. With the prior model (dump-then-AI-goes-deep), the current task derails because the AI tries to address everything at once. This protocol resolves the dilemma: capture preserves the idea, the discipline of "tactical answer + park strategic" preserves the current task's focus.

### Pattern verification (incident record)

- **2026-05-06 (Skill Hub S28):** User dropped 5 strategic topics + AIOS executive summary mid-session during dispatcher consolidation work. AI captured all 5 to `brain-dump/2026-05-06-aios-dogfood-and-brain-dump-workflow.md` with preliminary thoughts per topic, answered only the 2 tactical questions (end session yes; build hook now no), and did not derail. User confirmed: "this is perfect, exactly what it's meant to be... worked perfectly fine." Promoted to universal protocol the same session.

## Human Action Required Protocol (NON-NEGOTIABLE)

When any workspace closes work that requires a user-facing action before dependent work can proceed, it MUST surface that ask actively. Silent drift is prohibited.

**Source:** wr-2026-04-21-006 (concrete incident: credential migration waited 3 days silently because next_user_action was buried in a closed record's resolution field, invisible to the user).

### Trigger

Any time a workspace closes a WR, routed task, lifecycle review, or Supabase task where the user must perform an action (execute migration, rotate API key, click UI button, update device config, approve deletion) before dependent work can proceed.

### File location

`<workspace-root>/HUMAN-ACTION-REQUIRED.md` -- one file per workspace, append-only, persists across sessions. If the file does not exist, create it with a standard header. If it exists, append a new entry.

### Entry format

Chronological entries. Each entry has these fields:

```markdown
## {ISO-DATE} -- {SHORT-ACTION-SUMMARY}

- **Requesting workspace:** {source workspace}
- **Execute from:** {workspace the user should run this from}
- **Reference ID:** {WR / RT / task id}
- **Action required:**
  {what the user must do, step by step}
- **Expected outcome:**
  {what happens when the user completes it -- success signal to look for}
- **Status:** open
- **Filed:** {ISO timestamp}
- **Done:** (pending -- to be filled on completion)
```

### Notification

When filing an entry, notify the user via Telegram HQ bot synchronously with the file write. Message format:

```
[HUMAN ACTION NEEDED]
Workspace: {name}
Action: {short summary}
Details: {workspace}/HUMAN-ACTION-REQUIRED.md
```

Use `~/.claude/scripts/notify-human-action.py` (see helper below) to append entry + send Telegram in one atomic call.

### Completion flow

When the user signals done in the relevant workspace:
1. Verify the precondition signal (e.g. for credential migration: `~/.claude/.env` exists with expected keys).
2. Update the entry's `Status:` to `done` and fill the `Done:` timestamp.
3. Append a short resolution line describing what was verified.
4. Execute the downstream work that was blocked.
5. (Optional) Notify completing via Telegram if the blocked work produces output the user should see.

### Append-only rule

Later user actions append NEW entries. Never overwrite or delete prior entries -- they are the historical record used by the trend surfacing pass.

### Trend surfacing

Sentinel's morning report scans all workspaces' `HUMAN-ACTION-REQUIRED.md` files and:
- Lists entries with `Status: open` older than 24 hours.
- Flags patterns (same action class repeating across workspaces = automation candidate).

### Enforcement hook (planned, optional)

A PostToolUse close-guard hook (`~/.claude/hooks/human-action-close-guard.py`) should warn when a WR/RT closes with a `next_user_action` field but no matching open entry in the filer workspace's `HUMAN-ACTION-REQUIRED.md`. Not yet built; file a follow-up WR if the current discipline drifts.

### Helper script

`~/.claude/scripts/notify-human-action.py`:
```
python ~/.claude/scripts/notify-human-action.py \
  --workspace <canonical-workspace> \
  --action "<short summary>" \
  --execute-from <workspace-to-run-from> \
  --reference-id <wr-or-rt-id> \
  --details "<multi-line details>" \
  --expected-outcome "<what success looks like>"
```

Appends entry to the workspace's HUMAN-ACTION-REQUIRED.md (creating it with header if missing) and sends Telegram HQ bot notification. Telegram credentials loaded from `~/.claude/.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`).

## Verify Before Acting Protocol (NON-NEGOTIABLE)

Before running ANY script, tool, or command referenced in a skill, workflow, MEMORY.md, or doc:

1. **Verify it exists on disk.** Run `ls` or `find` on the path. If the file doesn't exist, STOP.
2. **Check what DOES exist.** Look in `tools/`, `scripts/`, and the workspace directory for alternatives that serve the same purpose.
3. **Never report "blocked" or "missing" without checking alternatives.** The tool you need may exist under a different name or path.
4. **Never claim a system is broken because a skill told you to run something that doesn't exist.** The skill is wrong, not the system.

**Why this exists:** During Foundation Reset Phase 3, a skill referenced `checkpoint.py` -- a script that was planned but never built. The session followed the instruction blindly, reported "blocked by missing plugin," and failed to recognize that `supabase-sync.py` (the actual working tool) was right there in `tools/`. This happened during a cleanup session, eroding trust in the system's ability to self-correct. Phantom references in skills and docs must be caught at execution time, not trusted blindly.

## Verify Before Filing Protocol (NON-NEGOTIABLE)

Before filing ANY work request, routed task, or lifecycle review whose premise is "system X does not do Y":

1. **Read the script that ships X.** `grep` for the function or behavior Y. If it exists, the premise is wrong — do not file.
2. **Distinguish "no diff" from "no participation".** Sync-tool output messages like "no changes detected" / "everything in sync" / "nothing to do" describe state-against-last-run, not whether the file is in the sync set. Hash both copies (live + backup) before claiming a file isn't synced.
3. **Tool output ≠ tool intent.** If the only evidence for the premise is a single line of CLI output, you are inferring the missing behavior. Read source before filing.
4. **2-minute verification rule.** Every WR/RT premise must survive 2 minutes of grep + hash + ls. If you have not done that, you are not ready to file.

**Why this exists:** 2026-05-04, wr-skillhub-2026-05-04-002 was filed claiming sync-skills.py does not mirror ~/.claude/settings.json to the toolkit repo. Source inspection showed `sync_settings()` had been mirroring it the whole time. Author had observed `sync-skills.py --sync --push` print "Everything is in sync. No changes detected" and concluded the file wasn't in the sync set, when in fact the file was already in sync from the prior run that same session (the voice-capture-hook registration two minutes earlier). Drift-corrected via activity_stream event 8d45c0f6-32f3-4197-a1cb-128302812aad. Real residual concern (cross-platform path templating) was a separable narrower issue and got fixed inline. The class of error the rule prevents: confusing run-summary output with feature absence, then filing infrastructure WRs that re-do work the codebase already does.

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

## Verification-Before-Building Protocol (NON-NEGOTIABLE)

Before planning, suggesting, or building ANY new automation, hook, script, report, workflow, Supabase table, or plugin -- you MUST query the Operational Asset Registry first. Transparency about what exists is the whole point of the registry; building without checking defeats its purpose.

**When this protocol fires (the trigger list):**
- About to write a new file under `~/.claude/scripts/`, `~/.claude/hooks/`, workspace `tools/`, or workspace `workflows/`
- About to register a new Windows Task Scheduler job, n8n workflow, or CronCreate durable job
- About to request a new Supabase table from Sentinel
- About to create a new Claude Code plugin, skill, or agent
- About to propose an architecture that implies new infrastructure
- About to suggest "we should build X" in conversation

**When this protocol does NOT fire:**
- Bug fixes to an existing registered asset (fix the thing, don't re-verify)
- Config edits, doc updates, comment changes
- Work explicitly scoped to an existing plan that already cited a preflight check

**The check (the preflight step):**
```bash
# Free-text query across all 358+ registered assets:
python <Skill Hub>/tools/preflight-check.py "description of what you plan to build"

# Or restrict to a specific asset type:
python <Skill Hub>/tools/preflight-check.py --type hook "logging tool usage"
python <Skill Hub>/tools/preflight-check.py --type automation "daily digest"
python <Skill Hub>/tools/preflight-check.py --type table "track something"
```

**What the output requires you to do:**
- **Strong match found (score >= 5):** Review it. Default assumption: extend or reuse the existing asset. If you still need to build new, write down why in the plan/conversation so the decision is auditable.
- **Partial match (score 2-4):** Inspect the candidate. Is your planned build a new companion / new parameter / new mode of the existing asset? If yes, extend. If no, proceed and note the distinction.
- **No match (score 0 / empty):** Proceed with build. You have an explicit green light -- write it, and register the new asset at creation time per the Operational Asset Registry Protocol.

**What you may NOT do:**
- Skip the preflight check because "I know what's out there" -- memory drifts, registry is the truth.
- Run the check and ignore the matches because "mine is different" -- if it's different, write down why BEFORE building.
- Treat the protocol as optional for "small" work -- the marketing-content-detector was "a small nudge" and became a major enforcement mechanism. Scope creep is real; register at creation, check before creation.

**Why this rule exists (incident record):**
- 2026-04-22: User asked "do we have a database of all scheduled tasks and autonomous systems?" The registry (`assets` table) already existed with 345 rows, but 13 live hooks + automations were not registered because builders didn't check the registry before creating. Worse: the builders didn't even know the registry existed. Drift accumulated silently.
- Earlier incidents: cross_workspace_requests vs work_requests table duplication (the original motivation for the registry); multiple Task Scheduler jobs for the same purpose with slightly different names accumulating across workspaces.
- Pattern: every time we build without verifying, we either duplicate or break composition. The preflight is cheap (1 second); the cleanup is expensive (entire session).

**Enforcement:**
- **Documentation:** this protocol + the pre-task checklist item below. Necessary but not sufficient (past lesson: "Documentation without runtime detection is insufficient -- if a rule keeps getting violated, add detection, don't reinforce the rule").
- **Runtime nudge (pending):** `verification-before-build-enforcer.py` PostToolUse hook, filed as wr-2026-04-22-006. Will fire on new-file creation under infrastructure paths and nudge preflight-check before the asset takes shape. Until that hook is deployed, discipline is manual.

## Hook Introduction Rule (NON-NEGOTIABLE)

Hooks accumulate without governance until the cumulative friction becomes hostile to flow. Each hook in isolation is reasonable; the layer becomes problematic. To prevent recurrence, every new hook must clear an explicit budget exchange before being added.

**Source incident (2026-04-27):** User filed FOUR hook-friction WRs in one session (wr-hq-2026-04-27-001/003/004/005) after global hook count reached 42 with 17 firing on every Edit/Write. Quote: "We're going backwards instead of forward... I'm fighting this like crazy and you guys can't do anything now because of all these restrictions." Cumulative friction quantified at 30+ min/day during cascade work. The pattern: every past incident produced a new hook; none were ever retired. Hook count grew monotonically while incident class coverage saturated. Filed as wr-hq-2026-04-27-006 (Tier 3).

### Hook budget

| Constraint | Target | Current (2026-04-27) |
|---|---|---|
| Total global hooks in `~/.claude/hooks/` | ≤ 30 | 42 |
| Hooks on any single matcher (e.g., `PreToolUse:Edit\|Write`) | ≤ 6 | 17 (PreToolUse:Edit\|Write) |
| Hooks fully blocking (vs. advisory nudge) per matcher | ≤ 3 | (pending audit) |

When the budget is exceeded, a new hook may be added ONLY in a one-in-one-out trade with retirement of an existing hook in the same matcher and category. Above-budget proposals must include the retirement target and a justification for why the new hook earns the slot.

### Pre-introduction checklist (NON-NEGOTIABLE for new hooks)

Before creating any new file under `~/.claude/hooks/`:

1. **Run the preflight check** (Verification-Before-Building Protocol). Does an existing hook already cover this? If yes, extend it instead of creating a new one.
2. **Identify the past incident** that justifies the hook. Hooks without a documented incident are speculative complexity. Required: WR id, date, and one-line description of what the hook prevents.
3. **Choose the gate severity correctly.**
   - **Hard block (deny)**: only when silent failure is catastrophic AND undetectable post-hoc. Most hooks should NOT be hard blocks.
   - **Advisory nudge (additionalContext)**: default for new hooks. Cheaper psychologically; lets the AI proceed with awareness rather than fight a wall.
   - **Telemetry-only**: log the event, never gate. Best when measurement is the primary value.
4. **Wire user-driven-mode detection** if the hook gates Edit/Write. Hooks that gate writing MUST consult `~/.claude/scripts/_lib/intent_detection.py` so explicit user direction bypasses the gate. AI-autonomous initiation still triggers the gate. Source: wr-hq-2026-04-27-003 design.
5. **One-in-one-out budget swap** if total hooks ≥ 30 OR matcher hooks ≥ 6. Identify which existing hook the new one replaces, retire it in the same change, document the trade in the registration metadata.
6. **Sunset clause: 90-day zero-fire review.** If the hook fires zero times in 90 days, it is auto-flagged for retirement review. If 180 days zero-fire, retire by default. Implementation: log every hook fire to `<tempdir>/hook-fire-log.jsonl` (PostToolUse `*` matcher, single low-overhead hook), Sentinel surfaces zero-fire hooks in monthly cleanup report.

### Anti-patterns this rule prevents

| Anti-pattern | What it looks like | Why it fails |
|---|---|---|
| **"Each hook is fine in isolation."** | Each new hook is reasonable, well-scoped, low-cost individually. | Cumulative cost is N hooks × K Edits = quadratic friction. The bottleneck is total fires, not per-hook quality. |
| **"Add a hook to fix every incident."** | Every WR closes by adding a new gate. | The hook layer becomes a graveyard of past incidents. Coverage saturates, friction grows. |
| **"Block first, allow exceptions later."** | New hooks default to hard-deny mode. | Forces the user to learn private bypass vocabulary. Each new bypass keyword is documentation debt. |
| **"It only fires when relevant."** | Pattern-based triggers feel narrow. | Patterns over-match. The user is forced to bypass repeatedly during legitimate cascade work. |

### Audit cadence

- **At creation** (this rule): preflight + budget check + sunset clause.
- **Monthly**: Sentinel zero-fire report — hooks that didn't fire in 30 days flagged.
- **Quarterly**: full hook audit — re-categorize every hook KEEP/CONSOLIDATE/DEMOTE/RETIRE. The 2026-04-27 audit at `<Skill Hub>/docs/audits/hook-inventory-audit-2026-04-27.md` is the template.

### Enforcement

- **Documentation:** this rule + the pre-task checklist `hook-development-enforcer.py` already denies new hook creation under `~/.claude/hooks/` without skill invocation.
- **Runtime telemetry (planned):** zero-fire audit (described above). Not yet implemented; file follow-up WR if hook proliferation recurs after this rule is documented.

The autonomy goal is: user delegates → AI executes → user returns to completed work. Every hook that fires during user-driven cascade work is a gate that the user has to manually open. The Hook Introduction Rule treats the hook layer as a finite governance budget, not an open inbox.

## Operational Asset Registry (NON-NEGOTIABLE)

Every scheduled task, automation, hook, script, report, workflow, plugin, and Supabase table MUST be registered in the Supabase `assets` table. The registry is the single queryable source of truth for "what exists, what it runs, what it does, what its purpose is, who owns it."

**Registry table:** `assets` (Supabase). Owner: Sentinel (schema gatekeeper).
**Registration helper:** `~/.claude/scripts/register-asset.py` -- callable from any workspace, writes only the caller's own rows.
**Drift auditor:** `<Skill Hub>/tools/audit-autonomous-systems.py` -- compares registry against live Task Scheduler + n8n Cloud + `~/.claude/settings.json` hooks + CronCreate durable state. Run any time you want to verify the registry is accurate.

**When to register (at CREATION TIME, not post-hoc):**
- Any new `*.py` / `*.bat` / `*.sh` under `~/.claude/scripts/` or workspace `tools/` --> register as `script`.
- Any new hook under `~/.claude/hooks/` or `.claude/hooks/` --> register as `hook`.
- Any new Windows Task Scheduler job, n8n workflow, or CronCreate durable job --> register as `automation`.
- Any new Supabase table --> register as `table` (AND coordinate with Sentinel per Supabase schema ownership protocol).
- Any new brief, report, dashboard, or periodic output --> register as `report`.
- Any new SOP markdown in `workflows/` --> register as `workflow`.
- Any new Claude Code plugin --> register as `plugin`.

**When to query the registry (BEFORE building new):**
- Before writing a new automation: `python ~/.claude/scripts/register-asset.py list --type automation` -- does one already exist that does what you need?
- Before writing a new hook: same with `--type hook`.
- Before asking Sentinel to create a new Supabase table: same with `--type table`. Existing table may already fit.

**Drift tolerance: zero.** Any asset present in runtime but missing from registry is a bug. Any asset in registry but missing from runtime is either orphaned config or a rename that wasn't reflected -- either way, fix it. Sentinel runs the drift audit at morning + evening report generation and surfaces drift to the user.

**Hook enforcement (pending):** An `asset-registration-nudge.py` hook is planned (wr-2026-04-22-004) that will detect new files in `~/.claude/scripts/` and `~/.claude/hooks/` at write time and nudge registration. Until deployed, registration discipline is manual -- every session that builds infrastructure MUST register what it built before closing.

**Past incident (2026-04-22):** User asked "I thought we had a database to log all our scheduled tasks and autonomous systems." Reality: the Supabase table existed with 345 assets, but 13 live hooks + automations weren't registered. Including `Claude-Orphan-Cleanup-Hourly` -- the very system that killed 4 real claude.exe sessions the same morning, which would have been easier to triage if registered. Drift audit caught all 13 and closed the gap. Lesson: registration at creation is the only sustainable discipline.

## Scheduling Tool Rules (NON-NEGOTIABLE)

Before using ANY tool for scheduling or automation, verify what it actually does. Never assume from the name.

**Ownership:** Each workspace owns the scheduled tasks and automations that support its systems. The Supabase `assets` table is the authoritative ownership map (query by `owner_workspace`). The static doc at `~/.claude/docs/autonomous-systems-inventory.md` is a human-readable snapshot pointing at the registry; it is NOT the source of truth. Modify automations from the workspace that owns them.

**Tool hierarchy (verified 2026-04-09):**
- **n8n cloud** = PRIMARY for 24/7 tasks that don't need local filesystem (CEO briefs, cloud monitoring). Runs at sharkitect-solutions.app.n8n.cloud regardless of machine state.
- **Windows Task Scheduler** = PERSISTENT LOCAL for tasks needing local filesystem when computer is on (gap alerting, brief fallbacks, freshness audits). Use full python.exe path in .bat files.
- **CronCreate** = IN-SESSION ONLY for AI-powered inbox polling (all workspaces). Triage-only when user is active, autonomous processing when idle. Dies on session close. 7-day auto-expire. Recreated each session via startup guard. See Mid-Session Inbox Polling Protocol.
- **RemoteTrigger** = BROKEN for MCP-dependent tasks. MCP cold-start race condition (tools not registered at session init). Do NOT use for anything requiring Supabase, Gmail, Calendar MCPs. Documented in lessons-learned.md.
- **ralph-loop** = Task iteration loop ONLY. Keeps AI working on one task by intercepting Stop event. Has NO timer, NO interval, NO cron. Use for: iterative code improvement, plan execution overnight. NEVER for polling or scheduling.
- **session-startup-guard.py** = SessionStart hook. 3-state heartbeat. Checks inboxes and cron status. Creates CronCreate jobs if missing.

Each workspace has a `workflows/cron-schedule.md` listing its specific CronCreate jobs.

## Silent Execution Protocol (NON-NEGOTIABLE)

Every scheduled task or automation must run silently with no visible window. A console flash mid-work interrupts user focus and (per direct user report) causes accidental keystroke errors that corrupt other work. Silent autonomy is a core principle of the system; visible-window automations violate that principle.

**Source:** wr-sentinel-2026-04-30-003. User direction (verbatim, 2026-04-29): *"sometimes a pop-up window can cause me to mess something up."*

### Required mechanisms

| Platform | Silent mechanism | Example |
|---|---|---|
| Python entry point (Windows) | `pythonw.exe` instead of `python.exe` | `pythonw.exe "C:\scripts\foo.py"` |
| .bat orchestration | VBS wrapper with `WshShell.Run windowStyle=0` | `wscript.exe "C:\scripts\silent-runner.vbs"` |
| Direct VBScript | `cscript.exe //B` (batch mode, no UI) | `cscript.exe //B "C:\scripts\runner.vbs"` |
| Task Scheduler creation | `schtasks /create /RL HIGHEST /F` plus the hidden-task XML attribute when applicable | XML `<Hidden>true</Hidden>` |
| PowerShell entry point | `-WindowStyle Hidden` flag (or wrap in VBS) | `powershell.exe -WindowStyle Hidden -File foo.ps1` |
| Cron / launchd / systemd | Always silent (no terminal allocation) | system default |
| n8n cloud workflows | Cloud-hosted, no local window | n8n.io scheduling |

**Prohibited:** bare `python.exe`, bare `cmd.exe /c`, bare `.bat` / `.cmd` file references, PowerShell without `-WindowStyle Hidden`. These all flash a console window when the task fires.

### Creation-time invariant (REQUIRED)

`register-asset.py register automation <name> --workspace <ws>` REQUIRES `--silent <mechanism>` where mechanism is one of: `pythonw | vbs-wrapper | task-scheduler-hidden | cron-equivalent | n8n-cloud | other`. Registration without `--silent` is rejected. The mechanism is stored in `metadata.silent_mechanism` for downstream audit.

`other` is an explicit escape hatch for legitimate edge cases (e.g., an interactive task the user actually wants to see). Justify in `--purpose` text.

### Audit invariant (REQUIRED)

`audit-autonomous-systems.py` includes a `visible_window_automation` drift class. Any live Task Scheduler entry whose action invokes `python.exe`, `cmd.exe`, bare `.bat`, or visible PowerShell is surfaced in the morning + evening drift reports as a Silent Execution Protocol violation requiring retrofit.

The drift class is computed from the schtasks `/v` "Task To Run" column. Empty / unknown commands are not flagged (avoid false positives) but the absence of a registered silent mechanism IS surfaced via the existing `missing_from_registry` channel.

### Retrofit responsibility

Each workspace owns the retrofit of its own visible-window automations (per Supabase Ownership Protocol). Skill Hub owns the protocol + audit infrastructure; HQ + Sentinel each retrofit their own Task Scheduler entries when the audit surfaces violations.

When retrofitting:
1. Identify the visible task via `audit-autonomous-systems.py` output
2. Pick the appropriate silent mechanism from the table above
3. Update the .bat / Python entry point or wrap in VBS (whichever applies)
4. Re-create the Task Scheduler entry pointing at the silent mechanism
5. Update the registry: `register-asset.py update automation <name> --workspace <ws> --metadata '{"silent_mechanism":"<mechanism>"}'`
6. Verify via the audit drift report on next run

### Why this matters

Silent autonomy is a load-bearing principle: the user delegates tasks expecting them to complete invisibly while focused on revenue work. Every console flash is a context switch the user did not consent to. Cumulative cost across 8+ scheduled tasks firing daily is real (and the user reports concrete accidental-keystroke incidents). The protocol pushes the cost back where it belongs — to the workspace that built the automation, at registration time.

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

### Status Cascade and Rollup (NON-NEGOTIABLE)

Status flows BOTH directions: forward (project status -> child task status) and reverse (task progress -> parent project counts -> auto-complete/auto-reopen). Both halves are enforced by Supabase triggers (DB-side) AND mirrored in `update-project-status.py` (script-side defense-in-depth). Either path must produce the same result.

**Source:** `wr-sentinel-2026-04-30-002` (forward cascade rule + trigger) + `wr-sentinel-2026-04-30-006` (reverse rollup migration + trigger). Migration name: `add_project_task_rollup_2026_04_30`. Triggers: `trg_recompute_project_task_counts` (rollup), `projects_status_cascade_to_tasks` (cascade -- applied by Sentinel after this rule was codified).

#### Forward cascade rule (project -> tasks)

When a project's `status` transitions to a non-active value, every non-final child task (status NOT IN `completed`, `cancelled`) is updated according to this canonical rule:

| Project transitions to | Apply to non-final child tasks |
|---|---|
| `paused`              | `tasks.status = paused` |
| `tabled`              | `tasks.status = tabled`, `tasks.priority = low`, `tasks.review_date` set |
| `blocked`             | `tasks.status = blocked`, `tasks.priority = low` |
| `complete`            | `tasks.status = completed` (review and reopen if a task wasn't actually done) |
| `active` or `pending` | **no automatic forward cascade** -- child task state preserved |

**Reverse cascade (project resumed from paused/tabled/blocked back to active/pending):** child tasks do NOT auto-restore prior state. They are set to `tasks.priority = low` with `tasks.notes` annotation `auto-resumed YYYY-MM-DD; review and re-prioritize`. The owner re-prioritizes manually after review.

#### Reverse rollup rule (tasks -> project counts)

`public.projects` carries two trigger-maintained columns:
- `total_tasks integer NOT NULL DEFAULT 0`
- `completed_tasks integer NOT NULL DEFAULT 0`

The trigger `trg_recompute_project_task_counts` fires AFTER INSERT/UPDATE/DELETE on `public.tasks` and recomputes both counts on the affected project(s). Behavior:
- `total_tasks` counts ONLY non-rejected-non-withdrawn tasks. Specifically: `total_tasks = COUNT(*) FILTER (WHERE status NOT IN ('rejected','withdrawn'))`. Rationale: rejected and withdrawn tasks are dropped from the project plan -- they no longer count toward what the project needs to ship. A project with 5 tasks where 2 are withdrawn shows `total_tasks=3`; complete the remaining 3 and the project auto-completes correctly. If a withdrawn task is replaced with a new task, total goes back up to 4. Source: user direction 2026-05-04 during Phase 5.1 dashboard work; trigger source verified at `recompute_project_task_counts`. Filed via wr-sentinel-2026-05-04-003.
- If `total_tasks > 0 AND completed_tasks = total_tasks` AND project is not already `complete`, the trigger sets `projects.status = complete` automatically.
- If a previously-complete project sees a non-final task arrive, the trigger reopens it to `active`.

#### Forward cascade trigger deployment status

The forward cascade rule above is documented but the matching DB trigger `projects_status_cascade_to_tasks` is **DOCUMENTED BUT NOT YET DEPLOYED** in the database (verified 2026-05-04 by Sentinel). It will land in Luminous Foundation Bridge Phase 6 (Vocabulary harmonization + cascade rules + pause_reason fields). Until then:
- Manual cascade applies: when an agent updates a project status to `paused | tabled | blocked | complete`, it must explicitly invoke `update-project-status.py project ...`, which performs script-side cascade.
- Direct Supabase writes that change `projects.status` will NOT trigger child-task cascade until Phase 6 ships.
- `rejected` and `withdrawn` are explicitly NOT cascaded by either the future trigger or current script; their semantics are "drops off the plan," not "applied to children." Source: wr-sentinel-2026-05-04-002.

#### Why both halves exist

- The DB triggers are AUTHORITATIVE -- direct Supabase MCP writes still cascade and roll up correctly because the trigger runs at the DB layer.
- The script-side cascade in `update-project-status.py` is defense-in-depth + caller feedback. When you run `task <text> completed`, the script reads back the parent project's `total_tasks/completed_tasks` and prints `parent project X is now N/M complete; auto-completed` (or similar), so the caller sees the rollup result without a separate query.
- Drift between trigger output and SELECT COUNT(*) is BUG signal -- run `update-project-status.py status-rollup-check` to detect, and surface in Sentinel's morning report via the `rollup_drift` drift class in `audit-autonomous-systems.py`.

#### Verification (pre-trust check)

Before relying on either cascade, verify both halves are live:

```sql
-- Confirm rollup columns exist
SELECT column_name FROM information_schema.columns
WHERE table_name = 'projects' AND column_name IN ('total_tasks','completed_tasks');

-- Confirm both triggers exist
SELECT tgname FROM pg_trigger
WHERE tgname IN ('trg_recompute_project_task_counts','projects_status_cascade_to_tasks');
```

If either is missing, file a routed task to Sentinel (schema owner) -- do NOT bypass with manual workarounds.

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

## Workspace Data Quality Audit Cadence (NON-NEGOTIABLE)

Every workspace runs the 8-check Workspace Data Quality Audit weekly against its OWN Supabase projects + tasks rows. This is a recurring duty, not an ad-hoc task. Drift in Supabase data (stale notes, outdated blockers, uncascaded statuses) propagates silently into the dashboard, morning briefs, and CEO views -- the cadence catches it before it compounds.

**Source:** `wr-sentinel-2026-04-30-005`. User direction (verbatim, 2026-04-29): *"I don't want to deal with this anymore."* The cadence is the enforcement.

### The audit

Each workspace runs the canonical checklist at `<Sentinel>/docs/audits/workspace-data-quality-audit-checklist.md`. Sentinel maintains the checklist; each workspace executes it against its own data.

The 8 checks (mechanical, SQL-driven):

1. **Linkage integrity** -- FK orphans (tasks with `project` text set but `project_id` NULL)
2. **Rollup count sanity** -- `projects.total_tasks` / `completed_tasks` vs actual SELECT COUNT(*) FROM tasks
3. **Forward cascade compliance** -- non-final tasks under paused/tabled/blocked/complete projects must mirror project status per the Status Cascade rule above
4. **Blocker freshness** -- every blocked or paused project must have a current `blocker` text; every blocked task must have current `notes`
5. **Notes coverage** -- every open task under a non-active project must have notes explaining where the work stands
6. **Stale `updated_at`** -- non-final rows that haven't been touched in 14+ days
7. **Phase / progress freshness** -- active multi-phase projects must have current_phase, phase_number, total_phases, phase_description
8. **Priority sanity** -- non-active projects shouldn't have critical or high priority tasks

### Cadence

| Cadence tier | Workspace | Frequency | Deadline window |
|---|---|---|---|
| First pass | All three | One-time | 2026-05-06 |
| Recurring | All three | Weekly | Within 7 days of prior audit |

### Output format and follow-through

1. Each workspace writes its audit report to `<workspace>/docs/audits/data-quality-audit-YYYY-MM-DD.md` using the format in the canonical checklist (counts inspected per check, issues found, fixes applied, issues deferred + reason, new tasks generated, open cross-workspace coordination).
2. When the audit completes, the workspace files a `kind: completion_notification` routed-task to Sentinel's `.routed-tasks/inbox/` with the audit report path. This closes the loop and gives Sentinel verification material.
3. Sentinel verifies and closes the routed task per the Completion Notification Protocol.

### Enforcement

- Each workspace is registered in the Operational Asset Registry as a `workflow` asset named `workspace-data-quality-audit-<workspace-canonical-name>` with `audit_cadence='warm'` (weekly).
- `audit-autonomous-systems.py` drift class `overdue_data_quality_audit` scans each workspace's `docs/audits/` and flags workspaces whose latest `data-quality-audit-YYYY-MM-DD.md` is older than 7 days. Sentinel surfaces this drift class in the morning report.
- Sentinel's monthly hook-fire and asset-cadence audits include this duty's active state.

### Update mechanics during the audit

- Always go through `update-project-status.py` (or the canonical brain-update path), not direct Supabase writes. The script bumps `updated_at` and writes `last_updated_by`. Direct writes are how Check 2 drift gets introduced.
- **Notes format:** short, one-line, action-oriented. Bad: "still working on it." Good: "blocked on Juan finalizing expense cuts post 4/22 pullback; resume when client confirms budget."

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
- Every entity type (projects, tasks, plans, goals, system health, lessons learned, etc.)
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
5. **Use only allowed statuses** — projects: `active/pending/paused/blocked/tabled/complete/rejected/withdrawn`. Tasks: `pending/in_progress/completed/blocked/deferred/tabled/rejected/withdrawn`. Goals: `active/at-risk/paused/achieved/missed/superseded/withdrawn`.

### Entity catalog (canonical reference)

| Entity | Supabase table | Local file pattern | Allowed statuses | Required metadata fields |
|--------|----------------|--------------------|--------------------|--------------------------|
| **Project** | `public.projects` | plan files in `~/.claude/plans/` indexed by `~/.claude/docs/plans-registry.md` | `active`, `pending`, `paused`, `blocked`, `tabled`, `complete`, `rejected`, `withdrawn` | `name`, `workspace`, `status`, `priority`, `created_at`, `last_updated_by` |
| **Task** | `public.tasks` | inline in plan files; tracked via `update-project-status.py` | `pending`, `in_progress`, `completed`, `blocked`, `deferred`, `tabled`, `rejected`, `withdrawn` | `text`, `project` (FK), `assigned_workspace`, `status`, `priority`, `created_at` |
| **Goal** | `public.goals` | workspace `knowledge-base/strategy/*.md` until rolled into the table | `active`, `at-risk`, `paused`, `achieved`, `missed`, `superseded`, `withdrawn` | `name`, `target_metric`, `target_value`, `unit`, `deadline`, `workspace`, `status`, `current_value` (rollup) |
| **Plan** | rows in `public.projects` (status = `pending` until active) | `~/.claude/plans/<slug>.md` indexed by `~/.claude/docs/plans-registry.md` | mirrors Project statuses | path, status, workspaces involved, phase markers |
| **System health component** | `public.system_health` (Sentinel-owned) | `4.- Sentinel/health/*.md` | `healthy`, `degraded`, `unhealthy`, `unknown` | `component`, `status`, `last_check`, `owner_workspace` |
| **Lessons learned** | none (file-only) | `~/.claude/lessons-learned.md` (7 categories) | n/a (append-only log) | category, date, workspace, what_happened, lesson |
| **Inbox item** | `public.cross_workspace_requests` | `<workspace>/.work-requests/inbox/`, `.routed-tasks/inbox/`, `.lifecycle-reviews/inbox/` | open: `new`, `pending`, `in_progress`, `deferred`, `blocked`. close: `completed`, `rejected`, `superseded`, `duplicate`, `withdrawn` | `id` (v2 schema), `id_format_version`, `source_workspace`, `status`, `notify_on_completion` |
| **Asset** | `public.assets` (registry) | source files in `~/.claude/scripts/`, `hooks/`, workspace `tools/`, etc. | `active`, `deprecated`, `retired` | `name`, `type`, `owner_workspace`, `purpose`, `audit_cadence`, `silent_mechanism` (automations) |

**Source of the goals row:** wr-sentinel-2026-05-04-008. `public.goals` shipped 2026-05-04 (HQ rt closed by Sentinel). HQ owns the rollup script that snapshots trajectory + updates `current_value`.

### Goals vs Projects (decision rule, NON-NEGOTIABLE)

**Goals are outcomes; projects are work.** If it has a `target_value` + `deadline` + you measure progress against the target, it is a goal. If it is a stream of work that produces deliverables, it is a project.

Project-shaped goals create the drift class observed when HQ filed its Revenue Target as a project (later deleted, project_id `d345b55b`): the task rollup saw "0 tasks completed → project never advances," while the actual revenue progressed independently of any tasks. Goals must live in `public.goals` so progress is tracked as `current_value` toward `target_value`, not as `total_tasks` / `completed_tasks` rollup.

**Decision aid:**
- "Hit $20K MRR by Q3" → goal (target_metric=`MRR`, target_value=`20000`, unit=`USD/month`, deadline=`2026-09-30`)
- "Build CEO daily brief workflow" → project (work stream with discrete deliverable)
- "Reduce p99 API latency below 200ms" → goal
- "Migrate database to Supabase" → project
- "Achieve 95%+ test pass rate on closed PRs" → goal
- "Fix 13 historical error_fixes via autofix v2" → project (the goal is "v2 reaches confidence threshold X" — the migration is the project)

If you find yourself filing a project whose only "completion" is hitting a metric, stop and refile as a goal.

Sentinel audits compliance with these standards across all workspaces.

## Modifying ~/.claude/settings.json (NON-NEGOTIABLE)

The Edit tool is PERMANENTLY DENIED on `~/.claude/settings.json` by a deny rule listed inside settings.json itself -- chicken-and-egg by design: settings.json contains the deny list that blocks editing it. Do NOT waste time attempting Edit, PowerShell, cmd workarounds, or any other path-escape variants. They will all fail. The ONLY supported path is documented below.

### The ONLY way to modify settings.json

Bash + Python `open(..., 'w')` via subprocess. This is a different code path than the Edit tool and is not blocked by the deny rule. Use this pattern, no other.

### Required preconditions (every time)

1. **Explicit user approval for the specific change.** A general "approved this work" is NOT enough -- settings.json governs every future session in every workspace, so each modification requires per-action authorization. If you don't have explicit approval, STOP and ask, presenting the exact diff.
2. **Show the diff before applying** so the user can verify intent matches.

### Required execution sequence (every time)

1. **Backup:** `shutil.copy2(src, src_parent / f'settings.json.bak.<YYYYMMDD-slug>')`
2. **Read:** `json.load(f)`
3. **Mutate the dict surgically** (e.g., remove specific entries from `s['permissions']['deny']` by string match; append the new entries). Do NOT rewrite the whole file from scratch -- you will lose unrelated keys you didn't read.
4. **Write back:** `json.dump(s, f, indent=2)` then `f.write('\n')`
5. **Verify post-write:** re-read with `json.load`, confirm structure is valid AND the diff matches intent.
6. **Empirical test:** actually attempt the operation the change was supposed to enable (e.g., if you removed `Edit(~/.claude/.env)` from deny, immediately try Editing `~/.claude/.env`). If the test fails, RESTORE from backup before doing anything else.

### What does NOT work -- do not attempt

| Approach | Why it fails |
|---|---|
| Edit tool on settings.json | Hard-denied by `Edit(~/.claude/settings.json)` rule |
| `cmd //c "..."` with `\\` quoting | Bash MSYS path conversion mangles quotes; even when it doesn't, the underlying Edit deny still applies if the tool routes through Edit |
| PowerShell via Bash | Separate deny rule; user has not authorized PowerShell as a bypass |
| `sed -i` in-place edit | No backup, no JSON validation, fragile against quote variations |
| Hand-written full-file rewrite | Lossy -- drops keys the script didn't know about |

### Source incident

2026-04-29 (Skill Hub session 11): Fork A required `~/.claude/settings.json` modification to remove a contradictory `.env` deny rule. Edit tool blocked twice (first by safety system citing "self-modification of permission config", then by the explicit `Edit(~/.claude/settings.json)` deny). Bash + Python `open(..., 'w')` succeeded on first try with full backup + verify + empirical-test sequence. User instruction (verbatim): "I do want to make sure that this is documented as the only way to bypass this chicken-and-egg problem... so that we don't have this issue in the future, and we don't even try anything else except for what we know works."

---

## Settings.json Permission Discipline (NON-NEGOTIABLE)

Applies to BOTH `~/.claude/settings.json` (global) AND every `<workspace>/.claude/settings.json` (workspace-local). The HOW is documented above; this rule is about WHAT the permission lists must hold.

### The core rule

**Deny wins on conflict.** When the same exact path string appears in both `permissions.allow` and `permissions.deny`, the engine refuses the operation. The allow line becomes dead code AND its intended grant is silently broken. There is no scenario where keeping a duplicate allow + deny for the same path is correct — one of them must go.

### When retrofitting permissions (the common failure mode)

Every permission refactor MUST follow this sequence:

1. **Audit existing denies first.** Before adding any new allow, grep the deny list for the path being added. If it's there, remove it in the same change.
2. **Remove conflicting denies, never just append allows.** "Append allow" + "leave matching deny in place" = the allow does nothing.
3. **Verify by counting.** Before and after the change, log `len(allow)` and `len(deny)` AND `len(allow & deny)`. The intersection must be 0 after the change. If not, the change is broken — restore from backup.
4. **Empirical test one path.** Pick one path that the change was supposed to unblock and actually attempt the previously-denied operation (Edit a file, Write a file). If it still gets denied, the change didn't take effect — investigate before declaring done.

### Orphan denies (the second failure mode)

Even with no allow conflict, a deny rule that has no current justification is a silent block. When ownership of a path changes, when a workspace's role expands, or when a permissions refactor goes through, denies left over from prior intent quietly break legitimate work. A deny entry must answer: "what is this protecting?" If the answer is "I don't remember" or "an old constraint that no longer applies" — remove it.

Symptom of an orphan deny: a workspace tries to do something the universal protocols say it CAN do, gets blocked, and on inspection finds a deny rule that no rule-doc justifies.

### Documented offender pattern

| Path | Offender workspaces | Status as of 2026-04-30 | Why it's wrong |
|------|---------------------|--------------------------|----------------|
| `*/.routed-tasks/{inbox,processed}/**` + `*/.lifecycle-reviews/{inbox,processed}/**` (cross-workspace) | Skill Hub (fixed 2026-04-30 by wr-007), HQ (fixed earlier) | Sentinel: check status | Allow + deny duplicate on same path. Cross-workspace inbox writes silently broken. |
| `Edit(*/HUMAN-ACTION-REQUIRED.md)` | Skill Hub (fixed), HQ + Sentinel: check | Skill Hub fixed 2026-04-30 | Orphan deny. Blocked the standard `notify-human-action.py` helper. |
| `Edit(~/.claude/plans/**)` | HQ AND Sentinel | OPEN — routed for fix 2026-04-30 | Orphan deny. Locks workspace out of the GLOBAL plans dir even though every workspace is supposed to be able to file global plans (Plan Lifecycle Protocol). Skill Hub correctly has no rule (falls back to global allow). |

### Source incident

2026-04-30 (Skill Hub session 13): Sentinel filed wr-sentinel-2026-04-30-007 after discovering that Phase 1 permissions overhaul (commit a5ae246, 2026-04-28) had added cross-workspace inbox ALLOW rules but NOT removed the matching DENY rules. Cross-workspace inbox writes were silently broken for ~24 hours. While applying the wr-007 diff to Skill Hub, broader audit found a separate-but-structurally-identical orphan deny on `Edit(~/.claude/plans/**)` in HQ AND Sentinel — locking both out of writing global plan files even though the Plan Lifecycle Protocol expects all workspaces to write there. Two follow-up routed tasks filed to HQ + Sentinel for them to remove their own deny entries (each workspace owns its own settings.json per ownership rule). User direction (verbatim): "If we're updating the allowed list, it makes sense that they shouldn't be in the denied list as well. Make sure whatever is allowed is off the denied list."

### Enforcement

- **At edit time:** the procedure in "Modifying ~/.claude/settings.json" above includes verify-by-counting (step 5). Extend that step to assert `len(allow ∩ deny) == 0` before declaring success.
- **Periodic audit:** Sentinel's `audit-autonomous-systems.py` should grow a `permission_conflict` drift class that scans every `settings.json` for allow ∩ deny intersection AND for known-orphan deny patterns, surfacing them in the morning report. (Filed as a follow-up if not already in `wr-sentinel-2026-04-30-005` cadence scope.)

---

## Modifying .env files (NON-NEGOTIABLE)

The Edit and Write tools are DENIED on `.env` files (workspace .env files AND `~/.claude/.env`). This is intentional — `.env` files contain credentials, and the deny rule prevents accidental token leaks via blob-style write tools that could echo content back into transcripts. Do NOT waste time attempting Edit, Write, or alternate path-escape variants. They will all fail.

The same Bash + Python `open(..., 'w')` / `open(..., 'a')` pattern that unblocks `~/.claude/settings.json` editing also unblocks `.env` editing. This is a different code path than the Edit/Write tools and is not blocked by the deny rule.

### When this applies

- Adding a new credential to `~/.claude/.env` or any workspace `.env`
- Promoting a workspace-local credential to global `.env`
- Removing a deprecated credential
- Restructuring or annotating an `.env` file
- Migrating an `.env` file's section comments

### The ONLY supported path

#### Reading existing `.env` content (for safe append / structured edit)

```python
import os
env_path = os.path.expanduser('~/.claude/.env')          # or workspace path
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()
```

NOTE: do NOT print existing `.env` content to stdout via `cat`, `head`, `grep`, etc. — those expose credentials in the transcript. Read into Python; act on the variable; never echo. (A guard hook will block credential-dumping reads on global `.env` regardless.)

#### Append-only (idempotent — safest pattern)

```python
import os, re
env_path = os.path.expanduser('~/.claude/.env')
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Idempotent guard: do NOT re-add if a marker key from the new section
# is already present
if 'NEW_CREDENTIAL_MARKER_KEY' in content:
    print('already present -- no change')
else:
    section = '''
# --- new section comment ---
NEW_CREDENTIAL_KEY_1=value1
NEW_CREDENTIAL_KEY_2=value2
'''
    if not content.endswith('\n'):
        section = '\n' + section
    with open(env_path, 'a', encoding='utf-8') as f:
        f.write(section)

# Verify by counting (no stdout dump)
with open(env_path, 'r', encoding='utf-8') as f:
    new_content = f.read()
keys = re.findall(r'^NEW_CREDENTIAL_\w+=', new_content, re.MULTILINE)
print(f'Total NEW_CREDENTIAL_* keys after append: {len(keys)}')
```

#### Full rewrite (workspace `.env` only — never `~/.claude/.env`)

Workspace `.env` files can be fully rewritten when restructuring. ALWAYS snapshot to `archive/env-YYYY-MM-DD-<context>.txt` first via `shutil.copy2` so the prior state is recoverable.

```python
import shutil, os
src = '.env'
dst = 'archive/env-2026-04-29-archived.txt'
os.makedirs('archive', exist_ok=True)
shutil.copy2(src, dst)         # snapshot before rewrite

content = '''# Header comment
KEY1=value1
KEY2=value2
'''
with open('.env', 'w', encoding='utf-8') as f:
    f.write(content)
```

`~/.claude/.env` should NEVER be fully rewritten by AI — too many keys live there from too many cleanups. Always append-only. If the global `.env` legitimately needs surgical key removal, do a structured edit:

```python
import os
env_path = os.path.expanduser('~/.claude/.env')
with open(env_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
# Surgically drop ONLY the lines matching the deprecated key
new_lines = [ln for ln in lines if not ln.startswith('DEPRECATED_KEY=')]
with open(env_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
```

### Required sequence (every time)

1. **Authorization:** explicit user approval for the specific change. A general "approved this work" is NOT enough — `.env` mutations affect every future session that reads the credential. Each modification requires per-action authorization.
2. **Snapshot:** for full rewrites, `shutil.copy2(src, archive_path)` first. For append-only on `~/.claude/.env`, the idempotent guard substitutes for a snapshot (the new section is the diff).
3. **Idempotent guard:** before appending, check if a marker key from the new section is already present. Skip if so. This makes re-runs safe.
4. **Write:** `open(path, 'a' or 'w', encoding='utf-8')`.
5. **Verify post-write:** re-read with `open(...).read()`, run `re.findall` on the expected keys, print COUNTS only — never the values.
6. **Empirical test (if applicable):** if a script depends on the new credential, run a one-shot smoke test that confirms the credential is now readable. Use the workspace's `tools/load-env.py KEY` if available.

### What does NOT work — do not attempt

| Approach | Why it fails |
|---|---|
| Edit tool on `.env` | Hard-denied by `Edit(.env)` deny rule |
| Write tool on `.env` | Same deny |
| `cat`, `head`, or `grep` on `~/.claude/.env` to inspect existing content | Bash hook blocks credential dump; even if it didn't, exposes secrets in transcript |
| `cmd //c "..."` rewrites | Bash MSYS path conversion mangles quotes |
| `sed -i` in-place edit | No snapshot, no idempotent guard, fragile against quote variations |
| Hand-written full-file rewrite of `~/.claude/.env` | Lossy — drops keys from prior cleanups the AI didn't see |

### Precedence

The same global `Edit/Write(.env)` deny that blocks Edit/Write also blocks the corresponding Bash sub-tools that try to wrap them. Bash + Python `open(...)` is the documented path. If a future safety mechanism blocks Python `open()` on `.env`, file a WR — do NOT chain workarounds.

### Source incident

2026-04-29 (Skill Hub session 12): user asked the AI to clean up Skill Hub's workspace `.env` and promote Polaris credentials to `~/.claude/.env` (global). Write tool denied on `.env`. Bash + Python `open(..., 'w')` and `open(..., 'a')` succeeded on first try with archive snapshot + idempotent guard + count-only verification. User instruction (verbatim): "I need you to document what you did so other workspaces know how to do it, because that has been an issue we've had."

The pattern parallels the `~/.claude/settings.json` modification path documented in the section above. Both files are gated by the same family of permission rules; both unblock through the same Bash + Python `open()` mechanism. Documenting them as a single class so workspaces don't re-discover the workaround twice.

---

## Naming Conventions (NON-NEGOTIABLE)

Every user-facing artifact MUST have a name a non-technical reader can understand within 5 seconds. Engineery, metaphor-based, or self-referential names are prohibited at the user-facing surface.

### The 5-second test
Read the name aloud. If someone unfamiliar with the system can't guess what it does, the name fails.

### Required pattern
Names should answer:
- WHO/WHAT does it serve? (CEO, toolkit, sales, audits, n8n)
- WHAT does it do? (brief, monitor, scan, sync, alert, tracker)
- WHEN/HOW OFTEN? (morning, daily, end-of-day) -- only when timing matters

### Good
- "CEO morning brief" / "CEO midday check-in" / "CEO end-of-day brief"
- "Toolkit Monitor"
- "n8n Workflow Error Handler"
- "Cards Landing Visit Tracker"
- "Inbox Auto-Processor"

### Bad
- "Audit Cadence Engine" -- audit of what? what cadence?
- "Watchers Watcher" -- meta-cute, unclear
- "Methodology Nudge" -- nudge what?
- "Resource Auditor" -- too generic
- "Dream Consolidation" -- metaphor over function

### Where it applies (rename if violating)
- Task Scheduler entries (visible in Windows UI)
- Slack channels and bot display names
- Cron job descriptions
- Notification message headers (e.g., the `*[...]*` prefix in Slack/Telegram posts)
- Asset registry display names
- Skill / agent description fields (the picker text)
- Plan / workflow file titles in indexes
- Email subject lines

### Where it does NOT apply (internal naming is fine)
- Python module filenames (`audit_cadence_engine.py` is OK as snake_case)
- Function names, variable names, internal class names
- Git branch names
- Database table/column names (Sentinel-controlled)

### Retroactive renames
- **At creation time:** name it correctly from day 1.
- **During preflight:** if you encounter an ambiguous name on an asset you're already touching, propose a rename in the same change.
- **Don't refactor purely for renaming.** Bundle renames with substantive work; refactor cost is real.

### Source incident
2026-04-29 (Skill Hub session 11): user pushed back on "Audit Cadence Engine" -- the name failed the 5-second test, and user reported not knowing what the asset did despite multiple sessions of work on it. Renamed to "Toolkit Monitor." User cited multiple existing offenders across HQ + Sentinel they couldn't decode without context.

---

## Extension Rule

Workspace CLAUDE.md files define ONLY workspace-specific additions to these protocols. They should NOT duplicate items listed above, but if they do, this rule is authoritative.

If a workspace CLAUDE.md explicitly contradicts this rule (e.g., "do NOT run resource-auditor in this workspace"), the workspace CLAUDE.md wins for that workspace. This is the local override principle -- universal protocols are the baseline, workspace instructions can override for their specific context.