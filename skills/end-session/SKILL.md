---
name: end-session
description: "Use when user says 'end session', 'wrap up', 'stop for the day', 'done for today', 'close out', 'save session', 'wrapping up', or invokes /end-session. Runs the full 9-step end-of-session protocol: resource audit, MEMORY.md update, lessons capture, plan status, pending items, workspace checklist, .tmp/ audit, git commit+push, Supabase brain sync, session brief, summary. Final step schedules a detached self-kill of the current session ONLY (3s delay) so the window closes cleanly. Other claude.exe processes (active workspaces) are NOT touched -- orphan cleanup is handled separately by Claude-Orphan-Cleanup-Hourly with proper age safeguards. Do NOT use for: mid-session quick saves (use session-checkpoint), skill syncing (use sync-skills.py), brain memory queries (use supabase-sync.py pull), document freshness reviews (use document-lifecycle), resource gap detection (use resource-auditor)."
---

# End Session

Final-step end-of-session protocol. Captures lessons, updates memory, creates backups, syncs state across computers, then detaches a self-kill of the CURRENT session only so the session ends cleanly with no leaked claude.exe. Other workspace sessions are NOT touched -- orphan cleanup is owned by `kill-orphan-claude-processes.py` (4h age threshold + double-PID safety check) running hourly via Claude-Orphan-Cleanup-Hourly Task Scheduler.

**Renamed from `session-checkpoint` on 2026-05-11.** The mid-session quick-save logic moved to a separate `session-checkpoint` skill. This skill is end-of-session only — when it runs, the session is wrapping up for good.

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/full-checkout-protocol.md` | Running end-of-session checkpoint, need the complete 9-step audit checklist with verification commands and edge cases | Mid-session quick save (use the session-checkpoint skill instead) |
| `references/failure-modes.md` | Catching yourself skipping steps, rationalizing "I'll do it next session," or when checkpoint produces warnings you want to dismiss; also load during post-checkpoint self-audit | Checkpoint completed cleanly with all steps passing |

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "End session" / "wrap up" / "done for today" / "/end-session" | YES | -- |
| "Save progress before compacting" | NO | session-checkpoint (mid-session quick save) |
| "Quick git push mid-session" | NO | session-checkpoint |
| "Back up before risky changes" | NO | session-checkpoint |
| "Sync skills to GitHub repo" | NO | sync-skills.py --sync --push |
| "Check if docs are still accurate" | NO | document-lifecycle |
| "Did I use all available resources?" | NO | resource-auditor |
| "Push memories to Supabase" | NO | supabase-sync.py push |
| "Revert to previous state" | NO | supabase-sync.py revert |

## When to Use

Triggered by explicit end-of-session signals:
- "end session" / "end the session" / "wrap up" / "wrapping up"
- "stop for the day" / "done for today" / "that's it for today"
- "close out" / "close the session" / "save session"
- `/end-session` slash command (or `Skill end-session`)

If the user wants a MID-session quick save (not ending), route to the `session-checkpoint` skill instead -- it does git + Supabase push only.

## Step Overview

Load `references/full-checkout-protocol.md` for detailed commands, verification, and edge cases per step.

| # | Step | Check | If Missing |
|---|------|-------|------------|
| 1 | Resource audit | Was resource-auditor invoked this session? | Run it now if significant work was done |
| 2 | MEMORY.md | Updated with session learnings? | Update with decisions, patterns, outcomes |
| 3 | Lessons learned | Errors, preferences, process decisions, or architecture learnings? | Write to ~/.claude/lessons-learned.md |
| 4 | Plan status | Active plan reflects current state? | Update plan with completed/remaining items |
| 5 | Pending items | Anything incomplete documented? | Add resume instructions to MEMORY.md |
| 6 | Workspace checklist | CLAUDE.md post-task items completed? | Execute remaining items |
| 6.5 | `.tmp/` audit | `.tmp/` contents classified (keep/promote/delete)? | Run the audit (see below) |
| 7 | Git checkpoint | `git add . && git commit && git push` | Commits + pushes all changes |
| 8 | Supabase sync | Brain state pushed? | `python tools/supabase-sync.py push` |
| 8.5 | Session brief | Summary written to Supabase + git? | Generate and push (see below) |
| 9 | Summary | Pass/fail per step | Report what failed and why |
| 10 | **Finalize** | Schedule detached self-kill of CURRENT session only | `python ~/.claude/scripts/end-session-finalize.py` |

## Step 10: Finalize (self-kill only)

After Step 9 prints the summary, run the finalize script as the absolute final action:

```bash
python ~/.claude/scripts/end-session-finalize.py
```

What it does:
1. Detects the current session's claude.exe PID via process-tree walk
2. Reports the count of OTHER claude.exe processes (informational only — does NOT touch them)
3. Schedules a DETACHED self-kill of the current claude.exe with a 3-second delay
4. Writes one JSONL entry per action to `~/.claude/.tmp/session-end-kill-log.jsonl`
5. Returns control immediately -- the AI prints "Session ending in 3s..." and exits

The detached killer outlives the current claude.exe. When it fires (~3s later), THIS session terminates cleanly. **Other claude.exe processes (active workspaces) are left alone.** Orphan cleanup is owned by `kill-orphan-claude-processes.py` running hourly via Claude-Orphan-Cleanup-Hourly Task Scheduler — it has the proper safeguards (4h age threshold + double-PID check + dry-run default) that distinguish leaked orphans from active workspace sessions.

**Why not orphan-kill here:** With multiple workspaces open concurrently (HQ + Sentinel + another Skill Hub), every active session has its own claude.exe PID and looks identical to a leaked orphan via tasklist. End-session has no signal to tell them apart. The 4h-age threshold in the dedicated orphan-cleanup tool is the correct boundary. (Source: bug fix 2026-05-11 post-S40 — earlier version killed all 4 active workspace sessions during /end-session.)

You do NOT need to `/clear` afterward — the kill closes the window.

Flags:
- `--delay 10`: longer grace window (useful if you want time to read the summary)
- `--no-self-kill`: report state only, do not kill (testing the script itself)
- `--dry-run`: report what would happen, don't kill anything

If the finalize script fails or doesn't find a self PID, the session stays open and the user can close manually. No data loss -- all 9 prior steps already committed + pushed durably.

### Graceful Degradation Rules

Not every workspace has every component. Handle missing infrastructure:

| Missing Component | Behavior | Steps Affected |
|---|---|---|
| No CLAUDE.md in workspace | SKIP Step 6 silently | Workspace checklist |
| No git repo initialized | Supabase-only checkpoint (no git commit/push) | Steps 7-8 |
| No git remote configured | Local commit only, WARN about no off-machine backup | Step 7 |
| No Supabase credentials | Git-only checkpoint, WARN about no brain sync | Step 8 |
| No active plan file | SKIP Step 4, not a failure | Plan status |
| Multiple plan files | Use most recently modified (check file timestamps) | Plan status |
| No session-errors.json | PASS Step 3 (error-tracker hook not yet installed) | Lessons capture |
| Resource-auditor not installed | WARN once, don't block | Step 1 |

### Resume Instruction Quality Gate (Step 5)

Resume instructions are only useful if they pass this test: **Can a cold-start session act on them immediately?**

**Minimum required fields:**
1. **What** was completed (specific deliverables, not "worked on X")
2. **Where** to resume (file path, function name, or step number)
3. **Why** it's incomplete (blocked, deferred, time, dependency)
4. **Next action** with enough specificity to start without re-reading context

**Bad:** "Continue with Phase 2"
**Good:** "Phase 2A ready to build. Create error-tracker-hook.py as PostToolUse on Bash. Pattern: scan output for tracebacks/non-zero exit, write to .tmp/session-errors.json. Register in settings.json next to resource-audit-hook."

### Critical Decision: Resource Audit (Step 1)

```
WAS SIGNIFICANT WORK DONE THIS SESSION?
  |
  +--> YES --> Was resource-auditor invoked?
  |              |
  |              YES --> Check its output. Any gaps found?
  |              |         |
  |              |         YES --> Were gap reports written?
  |              |         |        |
  |              |         |        YES --> PASS
  |              |         |        NO --> Write them now
  |              |         |
  |              |         NO --> PASS (clean audit)
  |              |
  |              NO --> Run resource-auditor now before closing
  |
  +--> NO --> SKIP (no significant work = nothing to audit)
```

"Significant work" = any task that produced outputs, modified code, created scripts, changed configs, or built infrastructure. This includes internal tools, automation scripts, CLAUDE.md changes, n8n workflows, and system architecture — not just client-facing deliverables. Only SKIP for pure conversation (Q&A, discussion) or trivial edits (typo fixes, memory-only updates).

#### Step 1 Gate: Skill-Judge / Agent-Judge Nudges (wr-2026-04-22-015)

After the resource-audit decision, Step 1 ALSO fails if `quality-gate-hook.py`
nudged a skill-judge or agent-judge invocation that was never satisfied.

**Check:**
1. Read `~/.claude/.tmp/skill-judge-nudges-YYYY-MM-DD.json` (today's date). Each
   entry has `kind` (skill | agent | skill-companion), `target` (skill/agent name),
   `file`, and `timestamp`.
2. Read `~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json`. Extract the set of
   skills invoked today (lowercased).
3. For every nudge entry, verify that EITHER `skill-judge` (for kind=skill or
   skill-companion) OR `agent-judge` (for kind=agent) appears in the invocations
   list. If ANY nudge lacks a matching judge invocation -> Step 1 FAILS.

**On failure:**
- Print which targets are missing their judge invocation
- Do NOT proceed to Step 2 until resolved
- Two resolutions: (a) invoke the missing judge now and re-verify, or (b) if
  the nudge was a false positive (e.g., unrelated edit to a skill directory),
  note the reason in the final Step 9 summary report

**Graceful degradation:**
- Missing nudge tracker file -> PASS (nothing to verify; either nothing was
  nudged, or an older session pre-tracker ran)
- Missing skill-invocations file -> WARN but PASS (tracker not recording this
  session; treat as inconclusive)

**Why this exists:** The quality-gate-hook advisory was ignored in
wr-2026-04-22-014 (16-WR batch session modified 2 skill companions without
invoking skill-judge). Advisory alone is not enough; the close-time gate makes
the nudge non-optional without being intrusive mid-session.

### MEMORY.md Update (Step 2)

Not everything learned in a session belongs in memory. Use this classifier:

```
INFORMATION LEARNED THIS SESSION
  |
  +--> Is it derivable from code, git log, or existing docs?
  |      YES --> DON'T RECORD (it's already persisted elsewhere)
  |
  +--> Will it matter in 3+ sessions from now?
  |      NO --> DON'T RECORD (ephemeral -- use plan/todo instead)
  |
  +--> Was it surprising or non-obvious?
  |      YES --> RECORD AS PATTERN or DECISION
  |      NO --> Was it a user preference?
  |               YES --> RECORD AS PREFERENCE
  |               NO --> DON'T RECORD (obvious knowledge)
```

**High-value entries** (always persist):
- "We tried X but Y worked because Z" -- the *because* is the knowledge delta
- "User prefers A over B" -- prevents re-asking in future sessions
- Confirmed patterns (worked 2+ times in different contexts)
- Architecture decisions with rejected alternatives and reasoning

**Zero-value entries** (never persist):
- "Modified file X" -- git log has this
- "Task completed successfully" -- obvious from the deliverable existing
- Unverified hypotheses -- wait until confirmed

### Lessons Capture (Step 3)

Lessons are NOT just errors. Capture anything learned this session across ALL categories:

**3A. Resolved Errors** -- Check `.tmp/session-errors.json` for `resolved: true` AND `retry_count >= 2`.
Format: date, category (api-limitation/tool-usage/platform/approach), attempted, error, solution, tags.

**3B. Preferences Discovered** -- Did the user express a preference about communication channels, output formats, workflow choices, tool selections, or how they want things done?
Format: date, `preference:` prefix, context, apply-when, tags. Section: `## Preferences`

**3C. Process Decisions** -- Did we try an approach that didn't work and pivot? Did we validate that a process works well?
Format: date, `process:` prefix, context, why, tags. Section: `## Process Decisions`

**3D. Architecture Direction** -- Did the user state or confirm a standing principle about system design?
Format: date, `direction:` prefix, context, apply-when, design principles, tags. Section: `## Architecture Direction`

For each qualifying entry (any category):
1. Format per category template above
2. Append to the correct section in `~/.claude/lessons-learned.md`
3. Push to Supabase brain via supabase-sync.py sync

**PASS condition:** No session-errors.json AND no preferences/process/architecture learnings. But most sessions surface at least one -- reflect carefully before passing.

### Summary Output (Step 9)

```
SESSION CHECKPOINT COMPLETE
===========================
[PASS] Resource audit: clean / invoked / N/A
[PASS] MEMORY.md: updated with 3 new entries
[PASS] Lessons: 1 lesson captured (windows encoding fix)
[PASS] Plan: updated phase 2 status
[PASS] Pending: 2 items documented for next session
[PASS] Workspace checklist: all items complete
[PASS] .tmp/ audit: 4 items (3 kept, 1 promoted, 0 deleted)
[PASS] Git: committed abc1234, pushed to origin/main
[PASS] Supabase: brain sync complete
[PASS] Session brief: pushed
---
All 10 checks passed. Safe to close session.
```

Or with failures:

```
SESSION CHECKPOINT COMPLETE
===========================
[PASS] Resource audit: clean
[FAIL] MEMORY.md: NOT updated -- session had 2 significant decisions
[PASS] Lessons: no qualifying errors
[WARN] Plan: no active plan found
[PASS] Pending: documented
[SKIP] Workspace checklist: no post-task items in CLAUDE.md
[PASS] Git: committed def5678, pushed
[PASS] Supabase: synced
---
6 passed, 1 failed, 1 warning. Fix MEMORY.md before closing.
```

### .tmp/ Audit (Step 6.5)

Enforces the `.tmp/ Hygiene Protocol` from `~/.claude/rules/universal-protocols.md`. Runs at every full-mode checkpoint, before git commit. Skip only in `--mid` (quick) mode.

**Inputs:**
- Current workspace `.tmp/` directory contents
- Size of each file + brief purpose inference (filename, extension)

**Procedure:**

1. **List** current `.tmp/` contents with size, newest first:
   ```bash
   ls -lhS .tmp/ 2>/dev/null || echo "(no .tmp/ folder)"
   ```

2. **Classify** each item (present the table to the user):

   | File | Size | Classification | Reason |
   |------|------|----------------|--------|
   | `doc-lifecycle-cache.json` | 45KB | **keep** | regenerated by `doc-cache-builder.py` on demand |
   | `skills-manifest.json` | 120KB | **keep** | regenerated by `refresh-inventory.py` |
   | `credential-audit-hq.md` | 14KB | **promote** | valuable artifact -> move to `docs/audits/` |
   | `test-output-2026-04-10.log` | 3MB | **delete** | stale test scratch, last task closed |
   | `document-relationship-map.json` | 15KB | **promote** | config file -> move to `.claude/drift-detection/` |

3. **User classification pause:** If anything is ambiguous, ask the user (one batched question). Do not guess for files >100KB or files with business-sounding names (audit, schema, export, template).

4. **Promote** valuable files to their correct home BEFORE any delete:
   - Config files tools read -> `<workspace>/.claude/<component>/`
   - Audits, schema exports, specs -> `docs/`
   - Reusable scripts -> `tools/`
   - Client deliverables -> `resources/<client>/` or wherever that workspace stores them

5. **Delete** remaining scratch (anything classified "delete"). Use `rm` with explicit paths, not wildcards on `.tmp/`.

6. **Verify:** post-audit `.tmp/` should contain only tool-regenerated caches. Typical size <1MB.

**Pass condition:** Audit completed AND `.tmp/` post-state is classified-clean (either promoted or deleted, nothing lingering).

**Skip conditions:**
- `.tmp/` does not exist -> PASS (nothing to audit)
- `.tmp/` is empty -> PASS
- `--mid` mode -> SKIP (this step belongs in full-mode only)

**Examples of what to catch:**
- `credential-audit-*.md` -> promote to `docs/audits/` (HQ 2026-04-21 incident)
- `supabase-schema-*.sql` -> promote to `docs/schema/`
- `n8n-code-*.js` -> promote to `tools/n8n-exports/`
- `template-builder-*.py` -> promote to `tools/`
- `document-relationship-map.json` -> promote to `.claude/drift-detection/` (see drift-detection-hook.py migration)
- `session-errors-*.json` -> keep (tool-regenerated)
- `doc-relationships.json` -> keep (Supabase cache, regenerated)

**Source:** HQ 2026-04-21 `.tmp/` audit found 7MB/54 items including valuable credentials audit, Supabase exports, and reusable scripts sitting in a folder named "disposable." wr-2026-04-21-002 filed; `.tmp/ Hygiene Protocol` added to universal-protocols; this step enforces it at session close.

### Session Brief (Step 8.5)

After Supabase sync, generate and push a session brief so other sessions (especially Sentinel's morning report) can see what happened.

**Generate:** Write a 2-4 sentence summary covering:
- What was accomplished (specific deliverables, not "worked on things")
- Key decisions made
- What remains for next session

**Push:** `python <supabase-sync-path> write-session-brief "<summary>"`

This writes to both Supabase (`activity_stream` with `event_type: session_brief`) and a local file (`.tmp/session-brief-YYYY-MM-DD.md`) for git.

**If supabase-sync.py doesn't have `write-session-brief` command** (older deployment): SKIP this step, WARN in summary.

## Script Locations

These are the tools this skill orchestrates:

| Script | Location | Purpose |
|--------|----------|---------|
| `supabase-sync.py` | `tools/supabase-sync.py` in each workspace | Brain memory operations (push, pull, write-session-brief, status) |
| `session-end-check.py` | `~/.claude/plugins/cache/local/aios-core/scripts/` | SessionEnd hook (runs automatically) |