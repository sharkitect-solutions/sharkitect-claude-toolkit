# Plan: Autonomous Self-Healing Loop -- Complete the Gap Pipeline

## Previous Plan Status
Content Quality Enforcement + Universal Gap Detection (Phases 1-4): **ALL COMPLETE** (2026-04-05)

## Context

The gap detection infrastructure is BUILT but the autonomous loop is NOT CLOSED. Three critical pieces are missing:

1. **Session-end doesn't close the loop.** `session-end-check.py` checks for unsaved files but never verifies: Was resource-auditor invoked? Were lessons captured? Was MEMORY.md updated? The user keeps manually reminding Claude to do this.

2. **Lessons-learned is manual.** When Claude encounters error->retry->fix, the lesson should automatically be written to `~/.claude/lessons-learned.md` AND pushed to Supabase brain so all workspaces benefit instantly. Currently it only happens when someone remembers.

3. **No monitoring of the gap pipeline itself.** Sentinel has no visibility into whether gap reports are aging in the inbox, whether workspaces are running audits, or whether lessons are propagating. The pipeline is invisible.

4. **No checkpoint/backup before risky changes.** When modifying skills, hooks, or system files, there's no automatic GitHub push to create a restore point. The hookify disaster proved this -- changes were made, things broke, work was lost because there was no checkpoint to revert to.

5. **No cross-computer continuity.** HQ has a GitHub repo but Skill Hub and Sentinel don't have git initialized. No session-start pull to sync from where the user left off on another machine. No session-end push to ensure everything is backed up.

**The goal:** Every session automatically captures lessons, detects gaps, writes reports, propagates knowledge, and creates backup checkpoints. The system gets smarter with every session. If something breaks, revert to the last checkpoint, learn the lesson, try again. All state syncs across computers via GitHub + Supabase.

---

## Phase 0: Git + Checkpoint Infrastructure

### 0A: Initialize git repos for Skill Hub and Sentinel
**Currently:** Only HQ has a GitHub repo. Skill Hub has `sharkitect-claude-toolkit` as a subfolder (for skill sync) but the workspace itself isn't a repo. Sentinel has no git at all.

**Actions:**
1. `git init` in Skill Hub workspace root
2. Create GitHub repo `sharkitect-solutions/sharkitect-skill-hub`
3. Add remote, initial commit + push
4. `git init` in Sentinel workspace root
5. Create GitHub repo `sharkitect-solutions/sharkitect-sentinel`
6. Add remote, initial commit + push
7. Create `.gitignore` for each (exclude `.tmp/`, `.env`, `node_modules/`)

### 0B: `checkpoint.py` aios-core script
**Location:** `~/.claude/plugins/cache/local/aios-core/scripts/checkpoint.py`

**Purpose:** Smart checkpoint that creates a git commit + push when risky changes are about to happen.

**When it fires (called by session-checkpoint skill or directly):**
- Before modifying skills, hooks, plugins, or system config files
- Before any batch operation (multi-file changes)
- At session end (part of session-checkpoint)
- On user command ("let's checkpoint")

**What it does:**
1. Detect workspace (same detection as session-start.py)
2. Check if workspace has git initialized + remote configured
3. If yes: `git add -A && git commit -m "checkpoint: {description}" && git push`
4. If no remote: just local commit (still a restore point)
5. Push MEMORY.md + session state to Supabase via supabase-sync.py
6. Return checkpoint hash so it can be referenced for revert

**Revert capability:**
- `python checkpoint.py revert` -- reverts to last checkpoint commit
- `python checkpoint.py revert {hash}` -- reverts to specific checkpoint
- After revert, automatically records what failed as a lesson candidate

### 0C: Session-start git sync
**Enhancement to `session-start.py`:**
1. If workspace has git remote, run `git fetch origin` + check if behind
2. If behind: emit "[aios-core] Local repo is {N} commit(s) behind remote. Run `git pull` to sync."
3. Pull MEMORY.md state from Supabase to check if another session updated it
4. If Supabase MEMORY is newer than local, emit warning with diff summary

### 0D: Pre-modification checkpoint hook
**Location:** `~/.claude/hooks/pre-modify-checkpoint.py`
**Hook type:** PreToolUse on `Write|Edit`

**Logic:**
1. Check if the file being modified is a "system file" (skills, hooks, plugins, CLAUDE.md, settings.json, aios-core scripts)
2. If yes AND no checkpoint exists in last 30 minutes (check `.tmp/last-checkpoint.json`):
   - Inject additionalContext: "SYSTEM FILE MODIFICATION DETECTED. Creating checkpoint before proceeding."
   - Write `.tmp/checkpoint-needed.json` flag
3. The session-checkpoint skill reads this flag and runs checkpoint.py

**Not a blocker** -- injects context so Claude runs checkpoint before proceeding with the risky edit.

---

## Phase 1: Session Checkpoint + Enhanced Session-End

### 1A: `session-checkpoint` skill
**Location:** `~/.claude/skills/session-checkpoint/SKILL.md`
**Purpose:** The COMPLETE end-of-session protocol. When user says "end session" or "let's wrap up," THIS is what runs. No manual reminders. No forgotten steps.

**Full checklist it executes:**
1. **Resource audit:** Check if resource-auditor was invoked. If not and work was done, run it now.
2. **MEMORY.md:** Check if updated this session. If not, update it with session learnings.
3. **Lessons learned:** Check `.tmp/session-errors.json` for resolved errors. Write lessons.
4. **Plans:** Check if active plan was updated to reflect current state. Update if needed.
5. **Pending items:** Document what's incomplete so next session knows where to resume.
6. **Supabase push:** Run `supabase-sync.py push` to sync MEMORY + brain state.
7. **Git checkpoint:** Run `checkpoint.py` to commit + push all changes to GitHub.
8. **Workspace-specific items:** Read CLAUDE.md post-task checklist, execute any remaining items.
9. **Produce summary:** Pass/fail per item. List what was pushed where. Note any failures.

**Two modes:**
- `/session-checkpoint` -- full end-of-session (runs everything above)
- `/session-checkpoint --mid` -- mid-session checkpoint (git commit + Supabase push only, no full audit)

**Files to create:** `~/.claude/skills/session-checkpoint/SKILL.md` (~250 lines, possibly 1 companion)
**Files to modify:** `session-start.py` -- add timestamp recording (~8 lines)
**Judge:** skill-judge, target A-

### 1B: Enhanced `session-end-check.py`
**Location:** `~/.claude/plugins/cache/local/aios-core/scripts/session-end-check.py`

Add 3 new checks to existing `main()`:
1. `check_resource_audit_ran()` -- warns if auditor never fired
2. `check_lessons_candidates()` -- flags resolved errors as lesson candidates
3. `check_session_checkpoint()` -- warns if checkpoint skill wasn't invoked

**Estimated change:** ~60 lines added to existing 127-line file

---

## Phase 2: Automatic Lessons-Learned Capture

### 2A: `error-tracker-hook.py`
**Location:** `~/.claude/hooks/error-tracker-hook.py`
**Hook type:** PostToolUse on `Bash`

**What it does:**
1. Scans Bash output for error signatures (non-zero exit, tracebacks, FAILED)
2. Writes to `.tmp/session-errors.json` with error hash, summary, retry count
3. When same error retried and succeeds, marks `resolved: true`
4. When `retry_count >= 2` and resolved, injects: "This was retried and fixed. Record as lesson."
5. **Self-healing:** On any error, greps `~/.claude/lessons-learned.md` for matching tags. If found, injects the known solution as additionalContext BEFORE Claude retries blindly.

**Files to create:** `~/.claude/hooks/error-tracker-hook.py` (~150 lines)
**Files to modify:** `~/.claude/settings.json` -- register PostToolUse on Bash

### 2B: `lesson-writer.py`
**Location:** `~/.claude/plugins/cache/local/aios-core/scripts/lesson-writer.py`

Called by session-end-check when resolved errors detected:
1. Reads `.tmp/session-errors.json` for entries with `resolved: true` + `retry_count >= 2`
2. Formats entry following existing lessons-learned.md template
3. Appends to `~/.claude/lessons-learned.md`
4. Pushes to Supabase brain via supabase-sync.py so all workspaces see it

**Files to create:** `lesson-writer.py` (~100 lines)
**Files to modify:** `session-end-check.py` -- call lesson-writer after detecting candidates

---

## Phase 2.5: MCP/API Limitation Detection & Prevention

### Context
The error-tracker (Phase 2) only catches Bash errors. MCP tool limitations (Airtable can't create rollup/formula fields, can't delete tables) fall through three cracks:
1. **Claude knows without trying** -- says "MCP doesn't support this" but no tool fires, no hook sees it, no lesson captured
2. **MCP tool returns soft failure** -- tool_result contains error JSON but error-tracker ignores non-Bash tools
3. **REST API fallback via Bash** -- already caught by error-tracker, but only after wasting a retry

### 2.5A: `~/.claude/rules/api-limitations.md` (global rule)
**Purpose:** Handles Scenario 1 -- when Claude knows a limitation but no tool fires.

A rules file with `alwaysApply: true` injected into every session's context. Instructs Claude to:
1. Check `~/.claude/lessons-learned.md` under "API Limitations" for workarounds
2. Provide manual steps instead of saying "not supported" and stopping
3. If no workaround exists, suggest capturing it: "Should I add this to lessons-learned.md?"

Seed with known limitations:
- Airtable: cannot create formula, rollup, or lookup fields via API/MCP
- Airtable: cannot delete tables via API
- Airtable: cannot delete fields/columns via API

**~30 lines. Zero risk, immediate value.**

### 2.5B: Expand `error-tracker-hook.py` for MCP tools
**Purpose:** Handles Scenario 2 -- MCP tool returns but with an error/limitation.

**Changes to existing file:**
1. Remove `if tool_name != "Bash": return 0` guard
2. Add tool categorization: `bash` / `mcp` / `other` (exit on `other`)
3. Add `MCP_ERROR_PATTERNS` list for soft failures:
   - `UNSUPPORTED`, `not supported`, `INVALID_REQUEST`, `FORBIDDEN`
   - `UNSUPPORTED_FIELD_TYPE`, `is not allowed`, `"error"`
4. Branch `_detect_error()` by tool category (Bash patterns vs MCP patterns)
5. For API-limitation-class errors: suggest lesson capture on FIRST occurrence (don't wait for 2 retries -- API limits never resolve by retrying)
6. Use `tool_name` instead of `command` for MCP error hashing

### 2.5C: `~/.claude/hooks/mcp-limitation-guard.py` (PreToolUse)
**Purpose:** PREVENT known-limited operations before Claude wastes a tool call.

**Logic:**
1. Fires on PreToolUse for MCP tools and Bash
2. Extracts signal keywords from tool_name + tool_input (e.g., "Airtable", "create_field", field type "rollup")
3. Scans `~/.claude/lessons-learned.md` "API Limitations" section for matching tags
4. If match found: inject "KNOWN API LIMITATION: [solution]. Do NOT attempt. Provide manual instructions instead."

**Performance:** Only reads the API Limitations section (~1KB). Early-exits if no keyword overlap. Fast enough for every tool call.

### 2.5D: Register hooks + seed lessons
1. Add PreToolUse matcher `mcp__|Bash` for `mcp-limitation-guard.py`
2. Add PostToolUse matcher `mcp__` for `error-tracker-hook.py`
3. Add structured Airtable limitation entries to `lessons-learned.md`:
   - `**Tool:**` and `**Operation:**` fields for precise hook matching
   - `**Manual-Steps:**` field for user instructions

### Files to create:
- `~/.claude/rules/api-limitations.md` (~30 lines)
- `~/.claude/hooks/mcp-limitation-guard.py` (~120 lines)

### Files to modify:
- `~/.claude/hooks/error-tracker-hook.py` -- expand to MCP tools (~40 lines changed)
- `~/.claude/settings.json` -- register new hooks
- `~/.claude/lessons-learned.md` -- seed with structured Airtable limitations

---

## Phase 3: Sentinel Gap Pipeline Monitor

### 3A: `gap-inbox-monitor.py`
**Location:** `4.- Sentinel/tools/gap-inbox-monitor.py`
**Usage:** `python tools/gap-inbox-monitor.py check [--alert]` / `status`

**Checks:**
1. **Inbox aging:** Reports older than 48h = stale, 7d = critical
2. **Processing velocity:** inbox count vs processed count
3. **Workspace coverage:** Which workspaces haven't run resource-auditor recently
4. **Lessons freshness:** lessons-learned.md not updated in 14+ days = stale

Registers `gap-pipeline` component in system_health table.

**Files to create:** `gap-inbox-monitor.py` (~200 lines)

### 3B: Brief generator update
**Location:** `4.- Sentinel/tools/brief-generator.py`

Add "GAP PIPELINE" section to morning/evening briefs showing inbox count, oldest report age, processing velocity, workspace audit coverage.

**Files to modify:** `brief-generator.py` (~40 lines added)

---

## Phase 4: Workspace Wiring + Supabase Sync Fix + Clients Table

### User-Reported Issues (discovered 2026-04-05)

**Issue 1: Supabase sync not firing during sessions.**
Investigation found:
- `session-start.py` HAS `pull_brain_context()` wired (line 485) -- pulls from Supabase. WORKING.
- `session-end-check.py` HAS `push_brain_sync()` wired (line 218) -- pushes to Supabase. WORKING but SILENT FAILURES.
- `checkpoint.py` HAS `_push_brain_sync()` in `cmd_create()` (line 191) and `cmd_sync()` (line 322). WORKING but SILENT FAILURES.
- **Root cause:** The code IS wired. The issue is that push failures are silently swallowed (try/except catches and discards errors). User sees no feedback, thinks sync isn't happening. May also be that supabase-sync.py itself is erroring (bad path, missing env var, timeout) and the silent catch hides it.

**Issue 2: New `clients` table created but not propagated.**
HQ did:
- Created `clients` table in Supabase
- Updated HQ CLAUDE.md line 227 to list `clients` in the tables list + describe its purpose
- .env already has SUPABASE keys (no new env vars needed for the table itself)

HQ did NOT:
- Update Sentinel's ops-brain.py to know about the clients table
- Update Sentinel's n8n-brain-integration-guide.md with clients table API spec
- Update supabase-sync.py with any clients-related commands
- Add clients table to any other workspace's awareness

### 4A: Fix Supabase sync visibility

**Problem:** All three aios-core scripts silently return when supabase-sync.py isn't found.

**Fix in `session-end-check.py` `push_brain_sync()`:**
- Line 84-85: change `if not sync_script: return` to print warning:
  `[aios-core] WARNING: supabase-sync.py not found. Brain sync skipped.`
- Line 96-97: already prints timeout, but improve error message

**Fix in `checkpoint.py` `_push_brain_sync()`:**
- Same pattern -- add warning when script not found
- Lines 88-95 already have some error handling but it's buried

**Fix in `session-start.py` `pull_brain_context()`:**
- Same pattern -- add warning when script not found

**Estimated change:** ~5 lines each file.

### 4B: Fix supabase-sync.py reachability (ROOT CAUSE)

**This is THE bug.** `push_brain_sync()` in session-end-check.py tries two paths:
1. `aios-core/scripts/supabase-sync.py` -- **DOES NOT EXIST** (confirmed via glob)
2. `cwd/tools/supabase-sync.py` -- only works if cwd is Sentinel workspace

For HQ, Skill Hub, or any non-Sentinel workspace: NEITHER path resolves. The function silently returns at line 84-85 (`if not sync_script: return`). Same pattern in checkpoint.py.

supabase-sync.py only exists at: `4.- Sentinel/tools/supabase-sync.py`

**Fix:** Copy supabase-sync.py to `~/.claude/plugins/cache/local/aios-core/scripts/supabase-sync.py`
- This is the first candidate path checked by ALL aios-core scripts
- aios-core should be self-contained -- it shouldn't depend on a specific workspace being open
- Keep Sentinel's copy as the "development" version; aios-core copy is the "deployed" version
- Add `.env` loading to supabase-sync.py if not already present (it needs SUPABASE_URL etc.)

**Also fix:** The silent `if not sync_script: return` -- change to print a warning so the user knows sync was skipped.

### 4C: HQ CLAUDE.md update
Add to post-task checklist: `- [ ] Run /session-checkpoint before closing`

### 4D: Sentinel CLAUDE.md update
- Populate ACTIVE_SKILLS (replace placeholder)
- Add resource-auditor + session-checkpoint to post-task checklist
- Add gap-inbox-monitor to regular health check duties

### 4E: Skill Hub CLAUDE.md update
Add resource-auditor + session-checkpoint to post-task checklist

### 4F: Clients table propagation

**Sentinel updates needed:**
1. `ops-brain.py` -- add `get_clients()` method to query clients table, add to `get_full_summary()`
2. `brief-generator.py` -- add CLIENTS section to morning brief (active clients count, payment terms due soon)
3. `docs/n8n-brain-integration-guide.md` -- add clients table API spec (schema, endpoints, example queries)

**supabase-sync.py update:**
- Add `write-client` / `list-clients` subcommands if needed for cross-workspace access

**Other workspaces:** No .env changes needed (same Supabase project). They access clients via Supabase MCP or REST API directly. The key is that CLAUDE.md in each workspace should mention the table exists.

### 4G: Lessons propagation (cross-workspace sync)
Enhance `session-start.py` `check_global_lessons()`:
1. Query Supabase for lessons newer than latest local entry
2. Append new lessons to local `~/.claude/lessons-learned.md`
3. Emit: "[aios-core] {N} new lesson(s) synced from other workspaces"

Add `pull-lessons` subcommand to supabase-sync.py (~50 lines)

---

## Implementation Sequence

| Phase | Deliverables | Status |
|-------|-------------|--------|
| 0 | Git init + checkpoint.py + pre-modify hook + session-start git sync | COMPLETE |
| 1 | session-checkpoint skill (110/120 A) + enhanced session-end | COMPLETE |
| 2 | error-tracker hook + lesson-writer + self-healing retry | COMPLETE |
| 2.5 | MCP limitation guard + error-tracker MCP expansion + api-limitations rule | COMPLETE |
| 3 | gap-inbox-monitor + brief update | COMPLETE |
| 4 | Workspace wiring + lessons propagation + Supabase sync fix + clients table | COMPLETE |

**Phase 0 comes first** because once git + checkpoints are working, every subsequent phase has a safety net. If Phase 1 breaks something, we revert to the Phase 0 checkpoint.

## Verification

### Checkpoint Test (after Phase 0)
1. Make a change to a skill file
2. **Expected:** pre-modify-checkpoint hook fires, checkpoint.py creates git commit + push
3. Intentionally break something
4. Run `python checkpoint.py revert` -- workspace restored to pre-change state
5. Verify the broken change is gone and system works

### Cross-Computer Test (after Phase 0)
1. Push from this computer
2. On another machine (or simulate): start session in same workspace
3. **Expected:** session-start detects local repo is behind, prompts to pull

### Full Loop Test (after Phase 4)
1. Open HQ workspace, do a task WITHOUT using relevant skills
2. **Expected:** resource-audit-hook fires, resource-auditor detects UNUSED gap, writes report to Skill Hub inbox
3. Run `/session-checkpoint` -- should flag gaps, update memory, push Supabase + GitHub
4. Close session -- session-end pushes lessons + brain sync + final checkpoint
5. Open Skill Hub -- session-start surfaces the gap report as priority
6. Process the gap following gap-processing.md workflow
7. Open Sentinel -- run gap-inbox-monitor, verify pipeline health
8. Open a DIFFERENT workspace -- session-start pulls new lessons from Supabase

### Self-Healing Test (after Phase 2)
1. Run a command that fails (known error with a lesson)
2. **Expected:** error-tracker detects error, greps lessons-learned, injects known solution
3. Run a command that fails twice then succeeds
4. **Expected:** lesson auto-written at session end, pushed to Supabase, available to all workspaces next session

---

## Critical Files

**To create:**
- `~/.claude/plugins/cache/local/aios-core/scripts/checkpoint.py` (~200 lines)
- `~/.claude/hooks/pre-modify-checkpoint.py` (~80 lines)
- `~/.claude/skills/session-checkpoint/SKILL.md` (~250 lines)
- `~/.claude/hooks/error-tracker-hook.py` (~150 lines)
- `~/.claude/plugins/cache/local/aios-core/scripts/lesson-writer.py` (~100 lines)
- `4.- Sentinel/tools/gap-inbox-monitor.py` (~200 lines)
- `.gitignore` for Skill Hub and Sentinel workspaces

**To modify:**
- `~/.claude/plugins/cache/local/aios-core/scripts/session-start.py` -- timestamp + git sync + lessons pull
- `~/.claude/plugins/cache/local/aios-core/scripts/session-end-check.py` -- 3 new checks + lesson-writer call
- `~/.claude/hooks/resource-audit-hook.py` -- write last-audit timestamp
- `~/.claude/settings.json` -- register error-tracker hook + pre-modify-checkpoint hook
- `4.- Sentinel/tools/brief-generator.py` -- gap pipeline section
- `4.- Sentinel/tools/supabase-sync.py` -- pull-lessons subcommand
- HQ CLAUDE.md -- post-task checklist
- Sentinel CLAUDE.md -- ACTIVE_SKILLS + post-task checklist
- Skill Hub CLAUDE.md -- post-task checklist
- `~/.claude/lessons-learned.md` -- add hookify/python3 lesson from this session

**GitHub repos to create:**
- `sharkitect-solutions/sharkitect-skill-hub` (for Skill Hub workspace)
- `sharkitect-solutions/sharkitect-sentinel` (for Sentinel workspace)

**Existing repos:**
- `sharkitect-solutions/sharkitect-workforce-hq` (HQ -- already has remote)
- `sharkitect-solutions/sharkitect-claude-toolkit` (skills/agents backup -- synced via sync-skills.py)

## Design Principles

1. `python` (not python3) for all hooks/scripts -- Windows compatibility
2. All Python tools: stdlib only, no external dependencies
3. Skills go through annealing loop (skill-judge, target max score)
4. Hooks fire deterministically, not advisory
5. Cross-workspace knowledge sharing via Supabase brain + lessons-learned.md
6. Compact between phases (user preference)
