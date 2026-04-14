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

| # | Workspace | Scope | Owns | Does NOT Do |
|---|-----------|-------|------|-------------|
| 1 | **Workforce HQ** | Client work, business operations, revenue | Client deliverables, proposals, SOPs, invoicing, CRM, client projects, CEO daily briefs (n8n), fallback briefs (Task Scheduler), error-autofix bridge | Skills/hooks/agents, brain monitoring |
| 2 | **Skill Management Hub** | Capability infrastructure | Skills, hooks, agents, plugins, gap detection + alerting + processing, sync to GitHub toolkit repo | Client work, brain monitoring |
| 3 | **Sentinel** | Oversight, intelligence, monitoring | Brain health monitoring, dream consolidation, system intelligence reports, Supabase brain queries, document freshness auditing, morning system report, repo monitor, Watcher's Watcher (n8n) | Client work, skill creation, business automation |

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
- [ ] Check MEMORY.md -- review prior learnings, patterns, and preferences that apply to this task.
- [ ] Check workflows/ -- is there an existing SOP for this type of work? Follow it.
- [ ] Plan before executing -- identify what needs to be done, in what order, and present the plan before starting.
- [ ] If the task is ambiguous, ask ONE clarifying question before proceeding.

> Workspace CLAUDE.md may define additional workspace-specific pre-task items. Run those too.

## Post-Task Checklist (after ANY work)

Run this checklist after completing any task. No task is "done" until post-task passes.

- [ ] Verify all outputs are saved, correct, and complete.
- [ ] Check cross-references -- if Document A was updated and Document B references it, update B.
- [ ] Update MEMORY.md with session learnings (decisions, patterns, preferences discovered).
- [ ] If new patterns or processes were discovered, record them.
- [ ] Confirm nothing is left in an inconsistent or half-finished state.
- [ ] If a plan was created, completed, or abandoned: update `~/.claude/docs/plans-registry.md` (see Plan Lifecycle Protocol).
- [ ] Run `/session-checkpoint` before closing the session.

> Workspace CLAUDE.md may define additional workspace-specific post-task items. Run those too.

## Session Lifecycle

### Session Start
1. Read MEMORY.md -- check pending items, patterns, preferences.
2. Sync from global lessons: Read `~/.claude/lessons-learned.md`. Check Preferences, Process Decisions, and Architecture Direction sections for entries not yet reflected in this workspace's memory. Pull relevant new entries into workspace MEMORY.md or topic files. This ensures learnings from other workspaces propagate here.
3. `git pull` if remote exists (cross-computer sync).
4. Refresh document cache: `python ~/.claude/scripts/doc-cache-builder.py --path "$(pwd)" --merge --quiet`
5. Resume from where last session left off.

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

**Idle Mode** (user appears away -- no recent messages, no active task, session sitting idle):
- **Process autonomously.** Do not wait for user response.
- Follow the same processing rules as session start (full autonomous processing).
- When the user returns, show a brief summary of what was processed while they were away.

### How to Determine Mode
Use conversation context -- no external timer needed:
- If you have an active todo list with in-progress items: **Active Mode**
- If the user sent a message in the last few exchanges and you're working on it: **Active Mode**
- If the session is idle (last exchange was your output, no pending user request): **Idle Mode**
- If the CronCreate prompt fires and there's no active work context: **Idle Mode**

### Briefing Format (Active Mode)
```
Inbox check (2:15 PM): 1 routed task from Sentinel -- lifecycle review verification.
  Priority: medium | Est. fix: ~10 min
  Recommendation: DEFER. Operational validation, not blocking active work.
  Will process at next session start.
```

```
Inbox check (2:15 PM): 1 work request -- plugin cache wiped, 3 plugins missing.
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
python tools/supabase-sync.py write-voice rejected <content_type> <audience> "<rejected content>" --reason "<user's exact words>"
python tools/supabase-sync.py write-voice approved <content_type> <audience> "<corrected content>" --reason "<what user wanted instead>"
```
Content types: email, proposal, slack, documentation, social, internal, code, comment
Audiences: client, prospect, internal, partner

**2. Activity stream event** (tracks correction frequency for trend analysis):
```bash
python tools/supabase-sync.py write-activity correction "<what was corrected and why>"
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

## Extension Rule

Workspace CLAUDE.md files define ONLY workspace-specific additions to these protocols. They should NOT duplicate items listed above, but if they do, this rule is authoritative.

If a workspace CLAUDE.md explicitly contradicts this rule (e.g., "do NOT run resource-auditor in this workspace"), the workspace CLAUDE.md wins for that workspace. This is the local override principle -- universal protocols are the baseline, workspace instructions can override for their specific context.