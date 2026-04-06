# Phase Completion Checklist

Execute this checklist in order when ALL tasks in a phase are complete. Every step is mandatory unless explicitly marked optional.

---

## Pre-check
- [ ] All tasks in this phase marked `completed` in TodoWrite
- [ ] `.tmp/active-phase.json` shows `tasks_done` equals `tasks_total`

## Step 1: AUDIT
- [ ] Read `.tmp/phase-artifacts.json` for list of files created/modified this phase
- [ ] For each artifact: is it still needed going forward? If not, delete it
- [ ] Scan `.tmp/` for files not in the artifacts list (potential orphans)
- [ ] Check for superseded documents (old versions replaced by new ones)
- [ ] Check for duplicate task entries or stale references
- [ ] Invoke `lifecycle-auditor` agent if available, or perform checks manually
- [ ] Document what was cleaned: "[X] files deleted, [Y] references updated"

## Step 2: MEMORY
- [ ] Update MEMORY.md: "Phase [N] complete: [one-line summary of what was accomplished]"
- [ ] Record key decisions made during this phase
- [ ] Update `lessons-learned.md` (project) with any failures or learnings
- [ ] If any learnings are cross-project: update `~/.claude/lessons-learned.md` (global)
- [ ] Update session history topic file if one exists

## Step 3: LOG (optional -- skip if no external DB configured)
- [ ] Check `.env` for `SUPABASE_URL` or `AIRTABLE_API_KEY`
- [ ] If configured: log phase completion with schema:
  - `phase_name`, `phase_number`, `status: complete`
  - `project`, `tasks_completed`, `duration`
  - `key_outcomes` (1-2 sentences), `timestamp`
- [ ] If not configured: skip entirely

## Step 4: SYNC
- [ ] Run `git status` to check for uncommitted changes
- [ ] If changes exist:
  - `git add` relevant files (not `.env` or credentials)
  - Commit: `"Complete Phase [N]: [phase name] - [summary]"`
  - `git push`
- [ ] If no changes: skip

## Step 5: CHECKPOINT
- [ ] Update `.tmp/active-phase.json`: set `"status": "complete"`
- [ ] Archive this phase's artifact list
- [ ] Clear TodoWrite items for this phase
- [ ] Inform user: "Phase [N] complete. All cleanup done. Safe to compact if needed."

---

## Phase Pause Checklist (stopping mid-phase)

Use when ending a session before the phase is fully complete.

- [ ] Update `.tmp/active-phase.json`: set `"status": "paused"`, confirm `tasks_done` is accurate
- [ ] Update MEMORY.md: "Paused at Phase [N], Task [M]. Resume: [specific instructions]"
- [ ] Update `lessons-learned.md` with any failures from this session
- [ ] Check `HUMAN-ACTION-REQUIRED.md` -- any new items to add?
- [ ] Commit + push to GitHub if uncommitted changes exist
- [ ] Inform user: "Phase [N] paused at Task [M]. Everything saved. Ready to resume next session."