---
name: project-lifecycle
description: >
  Use when starting a new project or feature that requires multi-phase planning,
  when completing a phase and needing structured cleanup, when a plan changes
  mid-execution and artifacts need updating, when something fails and the failure
  needs documenting to prevent repetition, or when ending a session with work
  in progress. Use when any project has more than 3 tasks or spans multiple sessions.
  Do NOT use for: single-file edits, trivial changes, or exploratory research
  without deliverables (use writing-plans for plan creation, executing-plans for
  plan execution mechanics, systematic-debugging for bug investigation).
---

# Project Lifecycle Orchestrator

Structured methodology for managing projects through phases with automated cleanup, persistent learning, and zero-drift session continuity. Prevents orphaned documents, stale references, duplicate tasks, and repeated failures.

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `SKILL.md` | Always -- core protocols | -- |
| `references/phase-completion-checklist.md` | Phase completes or pauses | During plan creation |
| `references/failure-documentation-template.md` | Something fails or errors | During normal execution |
| `references/plan-decomposition-guide.md` | New project starts, plan needs structuring | During phase execution |

## Scope Boundary

| This Skill | Use Instead |
|------------|-------------|
| Phase lifecycle management (start, execute, complete, pause) | `writing-plans` for initial plan drafting mechanics |
| Document cleanup and orphan prevention | `executing-plans` for step-by-step plan execution |
| Failure documentation and learning loops | `systematic-debugging` for root cause analysis |
| Session handoff and continuity | `dispatching-parallel-agents` for concurrent task execution |
| Plan change management | `subagent-driven-development` for agent-based implementation |

---

## Protocol 1: Plan Decomposition

### When to apply
At project start, or when requirements arrive that need multi-step implementation.

### Decision tree
```
Requirements received
  │
  ├─ Fewer than 4 tasks? → Skip this skill. Do inline.
  │
  ├─ 4-15 tasks? → Single plan, break into 2-4 phases
  │
  └─ 15+ tasks? → Break into phases of 5-8 tasks each
       │
       └─ Any task has >10 sub-items? → Promote to its own phase
```

### Rules
1. ONE canonical plan file. Never create a second plan file -- update the existing one.
2. Plan lives in `.claude/plans/` (Claude Code native) or project-specific location.
3. Each phase is numbered sequentially: Phase 1, Phase 2, Phase 3.
4. Each phase has a clear objective stated in one sentence.
5. Tasks within a phase are tracked via TodoWrite during execution.
6. Write `.tmp/active-phase.json` when a phase starts:
   ```json
   {"number": 1, "name": "Phase name", "started": "ISO-timestamp", "tasks_total": 5, "tasks_done": 0, "plan_file": "path/to/plan"}
   ```

### Anti-patterns (NEVER do these)

| Anti-pattern | Consequence | Do this instead |
|-------------|-------------|-----------------|
| Create a second plan file when the first needs updating | Orphaned plan file causes confusion in future sessions | Update the existing plan file in-place |
| Start Phase 2 without completing Phase 1 protocol | Orphans accumulate, memory gaps, GitHub falls behind | Always run Phase Completion Protocol between phases |
| Put 20+ tasks in a single phase | Context window overflow, lost tracking, no checkpoints | Split into phases of 5-8 tasks maximum |
| Track tasks in your head instead of TodoWrite | Tasks get lost on compact, no visibility for user | Always use TodoWrite for task tracking |
| Skip complexity assessment | Discover mid-phase that a task is actually 15 sub-tasks | Assess before starting: >10 sub-items = its own phase |
| Create .tmp files without tracking them | Orphans accumulate invisibly | phase-gate plugin tracks automatically, but name files clearly |

---

## Protocol 2: Phase Execution

### When to apply
During active work on a phase's tasks.

### Rules
1. Only ONE phase is active at a time. The active phase is in `.tmp/active-phase.json`.
2. Before starting any task, check `lessons-learned.md` (project) AND `~/.claude/lessons-learned.md` (global) for relevant prior failures. Grep for keywords related to the tools/APIs you are about to use.
3. Track each task via TodoWrite: mark `in_progress` before starting, `completed` immediately after finishing.
4. After each task completion: update `.tmp/active-phase.json` (increment `tasks_done`).
5. If a task fails: follow Protocol 5 (Failure Documentation) immediately. Do not defer.
6. If something requires human action that the AI cannot perform: add to `HUMAN-ACTION-REQUIRED.md` in project root.
7. After ALL tasks complete: run Protocol 3 (Phase Completion). No exceptions.

### Human Action Items format
```markdown
# Human Action Required

Items that require manual intervention. AI will remind you at session start.

- [ ] Delete deprecated Airtable tables: DEPRECATED_leads, DEPRECATED_contacts
- [ ] Rotate API key for n8n (expires 2026-04-15)
- [ ] Review and approve PR #47 before next phase can start
```

---

## Protocol 3: Phase Completion

### When to apply
When ALL tasks in the current phase are done. This is mandatory -- never skip it.

### Load companion: `references/phase-completion-checklist.md`

### Sequence (execute in order)

**Step 1 -- AUDIT**
Invoke the `lifecycle-auditor` agent (or perform manually if agent unavailable):
- Scan `.tmp/` for artifacts created during this phase (listed in `.tmp/phase-artifacts.json`)
- Check: is each artifact still needed going forward?
- Scan for superseded documents (old versions that were replaced)
- Scan for duplicate task entries or stale TodoWrite items
- DELETE confirmed orphans. UPDATE stale references. REPORT what was cleaned.

**Step 2 -- MEMORY**
- Update MEMORY.md: mark phase as complete, record key decisions made
- Update `lessons-learned.md` (project): any failures or learnings from this phase
- If any learnings are cross-project (API limitations, tool quirks): also update `~/.claude/lessons-learned.md` (global)
- Update session history topic file if one exists

**Step 3 -- LOG (optional)**
- If `SUPABASE_URL` exists in `.env`: log phase completion to Supabase
- If `AIRTABLE_API_KEY` exists in `.env`: log to Airtable
- Schema: `{phase_name, phase_number, status, project, tasks_completed, duration, key_outcomes, timestamp}`
- If no external DB configured: skip silently. This is never a blocker.

**Step 4 -- SYNC**
- Check `git status` for uncommitted changes
- If changes exist: `git add` relevant files, commit with message: `"Complete Phase N: [phase name] - [summary]"`, push to remote
- If no changes: skip

**Step 5 -- CHECKPOINT**
- Update `.tmp/active-phase.json`: mark as `"status": "complete"`
- Archive this phase's artifact list in `.tmp/phase-artifacts.json`
- Clear TodoWrite items for this phase
- Output: "Phase N complete. All cleanup done. Safe to compact if needed."

---

## Protocol 4: Plan Change

### When to apply
When the user modifies the plan, changes direction, removes tasks, or restructures phases mid-execution. The `phase-gate` plugin PostToolUse hook will remind you when it detects a plan file was modified.

### Sequence

**Step 1 -- DIFF**
Identify what changed:
- Tasks added? Tasks removed? Tasks reworded?
- Phases restructured?
- Entire approach changed?

**Step 2 -- CLEANUP**
- Tasks removed → check if those tasks created any artifacts. If yes, decide: keep or delete.
- Documents superseded → delete the old version NOW. Do not leave it.
- TodoWrite → clear old items that no longer exist in the plan. Create new items for new tasks.
- Check `.tmp/phase-artifacts.json` → remove entries for deleted artifacts.

**Step 3 -- CROSS-REFERENCE UPDATE**
- Find all documents that reference the changed plan elements (grep for task names, phase names)
- Update references to reflect the new plan
- Check MEMORY.md for stale references to the old plan structure

**Step 4 -- LOG THE CHANGE**
- Add to MEMORY.md: `"Phase X plan revised: [what changed] [why]"`
- If tasks were deleted: note what was abandoned and why (prevents rediscovery later)

### Anti-patterns

| Anti-pattern | Consequence | Do this instead |
|-------------|-------------|-----------------|
| Create a new plan file instead of updating | Two plans exist, confusion in future sessions | Update the existing plan in-place |
| Remove a task from the plan but leave its artifacts | Orphaned files confuse future sessions | Delete artifacts when removing their parent task |
| Update the plan but not TodoWrite | AI works from stale task list | Always sync TodoWrite with plan changes |
| Forget to update MEMORY.md about the change | Next session doesn't know the plan changed | Always note plan changes in memory |

---

## Protocol 5: Failure Documentation

### When to apply
When any operation fails, errors out, or produces unexpected results. Apply IMMEDIATELY -- do not defer to end of phase.

### Load companion: `references/failure-documentation-template.md`

### Sequence

**Step 1 -- Document in project `lessons-learned.md`**
```markdown
## [YYYY-MM-DD] [Category]: [Short title]
**Attempted:** What was tried (specific command, API call, approach)
**Error:** What happened (error message, unexpected behavior)
**Solution:** What worked instead (the fix or workaround)
**Tags:** [category tags for grep matching]
```

Categories: `api-limitation`, `tool-usage`, `approach`, `configuration`, `dependency`, `permissions`, `rate-limit`, `timeout`

**Step 2 -- Assess cross-project relevance**
Is this failure specific to THIS project, or would it apply to any project using this tool/API?
- Project-specific (e.g., "our webhook URL was wrong") → project file only
- Cross-project (e.g., "Airtable API can't delete tables") → ALSO add to `~/.claude/lessons-learned.md`

**Step 3 -- Human action needed?**
If the failure reveals something the AI cannot fix (e.g., manual UI deletion, credential rotation):
- Add to `HUMAN-ACTION-REQUIRED.md` with clear instructions
- Continue working with available workarounds

---

## Protocol 6: Session Handoff

### When to apply
At session end -- whether closing, compacting, or pausing. The `phase-gate` Stop hook will remind you if a phase is in progress.

### Sequence

1. **Plan file** is up-to-date with current state (completed tasks marked, remaining tasks clear)
2. **MEMORY.md** has resume instructions: `"Next session: Phase N, Task M. [context needed to continue]"`
3. **`lessons-learned.md`** is current with any failures from this session
4. **`HUMAN-ACTION-REQUIRED.md`** exists if there are pending manual items
5. **`.tmp/active-phase.json`** reflects current state:
   - If phase is done: status "complete"
   - If pausing mid-phase: status "paused", tasks_done reflects progress
6. **GitHub** is synced (commit + push if uncommitted changes exist)
7. **TodoWrite** reflects actual task state

### Pausing vs completing

| Scenario | Action |
|----------|--------|
| All tasks in phase done | Run full Phase Completion Protocol (Protocol 3) |
| Stopping mid-phase by choice | Mark as "paused", update memory with resume point, push to GitHub |
| Compacting (context limit) | aios-core PreCompact preserves state; phase-gate PreCompact saves phase state |

---

## Protocol 7: Session Start (Resumption)

### When to apply
At the start of every session. The `aios-core` SessionStart hook provides automated reminders, but the AI should also actively check.

### Sequence

1. Read MEMORY.md for resume instructions and current project state
2. Check `.tmp/active-phase.json`: is a phase in progress or paused?
3. Check `HUMAN-ACTION-REQUIRED.md`: any pending items for the user?
4. Check `lessons-learned.md` (project) for relevant prior failures
5. Check `~/.claude/lessons-learned.md` (global) for cross-project learnings
6. Check `.tmp/phase-state-backup.json`: was there a compaction? Recover state if needed.
7. Brief the user: "Resuming Phase N, Task M. [key context]. Any changes before we continue?"

---

## State Files Reference

| File | Location | Scope | Created by | Read by |
|------|----------|-------|-----------|---------|
| `active-phase.json` | `.tmp/` | Session | This skill | phase-gate hooks, aios-core |
| `phase-artifacts.json` | `.tmp/` | Session | phase-gate hook | lifecycle-auditor agent |
| `phase-state-backup.json` | `.tmp/` | Survives compact | phase-gate PreCompact | This skill (Protocol 7) |
| `lessons-learned.md` | Project root | Persistent | This skill (Protocol 5) | This skill (Protocol 2, 7) |
| `lessons-learned.md` | `~/.claude/` | Global persistent | This skill (Protocol 5) | This skill (Protocol 2, 7) |
| `HUMAN-ACTION-REQUIRED.md` | Project root | Persistent | This skill (Protocol 2, 5) | aios-core, this skill |