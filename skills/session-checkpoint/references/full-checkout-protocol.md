# Full Checkout Protocol -- Detailed Steps

Complete reference for the 9-step end-of-session checkpoint. Each step includes exact commands, verification criteria, and edge case handling.

---

## Step 1: Resource Audit Verification

**Goal:** Confirm that resource-auditor was invoked if deliverables were produced.

**Detection heuristic -- "deliverables produced":**
- User-facing documents written (proposals, reports, guides, emails)
- Code files created or substantially modified for user's project
- Configurations deployed to production systems
- Content published or prepared for publication

**NOT deliverables** (skip audit): memory updates, plan edits, skill modifications, internal tooling changes.

**Commands:**
```bash
# Check if resource-auditor ran (look for its output)
ls .tmp/resource-audit-*.json 2>/dev/null

# If no audit file exists and deliverables were produced:
# Invoke resource-auditor skill now
```

**Edge cases:**
- Resource-auditor found gaps but user chose not to address them: PASS (gap reports were written, processing is Skill Hub's job)
- Session was entirely internal work (skill building, system config): SKIP
- Resource-auditor is not installed in this workspace: WARN and note in summary

---

## Step 2: MEMORY.md Update

**Goal:** Persist session learnings that future sessions need.

**Verification:**
```
Was MEMORY.md modified this session?
  |
  YES --> Were the modifications substantive?
  |         |
  |         YES --> PASS
  |         NO --> Review: did the session produce learnings not yet captured?
  |
  NO --> Did the session produce learnable information?
          |
          YES --> FAIL: update MEMORY.md now
          NO --> PASS (read-only or trivial session)
```

**What qualifies as "learnable information":**
- A decision was made between alternatives (record which and why)
- A pattern was confirmed (worked 2+ times in similar contexts)
- A user preference was discovered ("I prefer X over Y")
- A process was improved ("doing A before B prevents C")
- Something failed and the root cause was identified

**200-line discipline:** If MEMORY.md is approaching 200 lines, move detailed content to topic files. Keep MEMORY.md as a concise index with pointers.

**Update template:**
```markdown
- **[Topic]**: [What was learned]. [Why it matters for future sessions].
```

---

## Step 3: Lessons Learned Capture

**Goal:** Capture ALL reusable knowledge from this session -- not just errors.

Lessons-learned.md has 7 sections. Check each:

### 3A. Resolved Errors

**Source:** `.tmp/session-errors.json` (written by error-tracker-hook when available)

**Qualifying criteria:**
- `resolved: true` -- the error was eventually fixed
- `retry_count >= 2` -- it took multiple attempts (knowledge worth capturing)

**If error-tracker-hook is not yet installed:**
- Ask: "Were there any errors this session that took multiple attempts to fix?"
- If yes, manually format as a lesson entry

**Format:**
```markdown
### [YYYY-MM-DD] category: short description

**Attempted:** What was tried first
**Error:** What went wrong
**Solution:** What actually worked
**Tags:** comma, separated, keywords
```

**Categories:** api-limitation, tool-usage, platform, approach

### 3B. Preferences Discovered

**Reflect:** Did the user express a preference about communication channels, output formats, workflow choices, tool selections, or how they want things done?

**Format:**
```markdown
### [YYYY-MM-DD] preference: short description

**Context:** What the preference is about
**Apply when:** When to use this preference
**Tags:** comma, separated, keywords
```

**Section:** `## Preferences` in lessons-learned.md

### 3C. Process Decisions

**Reflect:** Did we try an approach that didn't work and pivot to something better? Did we validate that a certain process works well?

**Format:**
```markdown
### [YYYY-MM-DD] process: short description

**Context:** What was decided
**Apply when:** When to apply this decision
**Why:** The reasoning behind it
**Tags:** comma, separated, keywords
```

**Section:** `## Process Decisions` in lessons-learned.md

### 3D. Architecture Direction

**Reflect:** Did the user state or confirm a standing principle about how systems should be designed?

**Format:**
```markdown
### [YYYY-MM-DD] direction: short description

**Context:** The principle
**Apply when:** When this applies
**Design principles:** Bullet list of specific guidelines
**Tags:** comma, separated, keywords
```

**Section:** `## Architecture Direction` in lessons-learned.md

### After writing any lesson:
```bash
# Lessons are global -- push to brain so all workspaces benefit
python <aios-core>/scripts/checkpoint.py sync
```

**PASS condition:** No qualifying errors AND no preferences/process/architecture learnings. Most sessions surface at least one -- reflect carefully before passing.

---

## Step 4: Plan Status Update

**Goal:** Ensure active plan reflects reality.

**Check:**
```bash
# Find active plan
ls ~/.claude/plans/*.md 2>/dev/null
# Or check .tmp/active-phase.json
```

**If active plan exists:**
- Are completed items marked as complete?
- Does the "current state" section reflect what was actually accomplished?
- Are remaining items still accurate (nothing added/removed)?

**If no plan exists:** PASS (not all sessions use plans)

**Common failure:** Plan says "Phase 2: IN PROGRESS" but Phase 2 was actually completed this session. Update it.

---

## Step 5: Pending Items Documentation

**Goal:** Future-you (or another session) knows exactly where to resume.

**Write to MEMORY.md under "Resume Instructions":**
1. What was completed this session
2. What remains incomplete and why (blocked? deferred? ran out of time?)
3. Specific next step with enough context to start immediately
4. Any prerequisites or dependencies for the next step

**Bad resume instruction:** "Continue with Phase 2"
**Good resume instruction:** "Phase 2A (error-tracker-hook.py) ready to build. Pattern: PostToolUse on Bash, scans for error signatures, writes to .tmp/session-errors.json. Reference: checkpoint.py for similar hook registration in settings.json."

---

## Step 6: Workspace-Specific Checklist

**Goal:** Execute any post-task items defined in the workspace's CLAUDE.md.

**How to find them:**
```
Read CLAUDE.md -> Find "Post-Task Checklist" section -> Execute uncompleted items
```

**Common workspace-specific items:**
- Skill Hub: `python tools/sync-skills.py --sync --push` if skills were modified
- HQ: Run content-enforcer review if documents were created
- Sentinel: Update health status if system changes were made

**If CLAUDE.md has no post-task checklist:** SKIP

---

## Step 7: Git Checkpoint

**Goal:** Commit and push all changes for backup and cross-computer continuity.

**Command:**
```bash
python "<aios-core>/scripts/checkpoint.py" create "session end: <brief description>"
```

**What checkpoint.py does internally:**
1. `git add -A` (stages everything)
2. `git commit -m "checkpoint: <description>"`
3. `git push` (if remote configured)
4. Writes `.tmp/last-checkpoint.json` with commit hash and timestamp

**Edge cases:**
- No git repo initialized: WARN (checkpoint.py handles gracefully, still does brain sync)
- No remote configured: Local commit only, WARN about no off-machine backup
- Push fails (auth, network): Local commit preserved, WARN about manual push needed
- No changes to commit: PASS (checkpoint.py reports "no changes")

**Description format:** `"session end: <what was accomplished>"` -- e.g., `"session end: built session-checkpoint skill, enhanced session-end-check"`

---

## Step 8: Supabase Brain Sync

**Goal:** Push memory state to Supabase so other workspaces and computers see updates.

**This is handled by checkpoint.py** in Step 7 (it calls supabase-sync.py push internally).

**Verification:** checkpoint.py output includes "Brain sync complete" on success.

**If Supabase sync fails:**
- Check if `.env` has SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
- WARN but don't block -- git backup is the primary safety net

---

## Step 9: Summary Generation

**Goal:** Clear pass/fail report so you and the user know the session state.

**Status codes:**
- `[PASS]` -- Step completed successfully
- `[FAIL]` -- Step required action and it wasn't taken (fix before closing)
- `[WARN]` -- Step had issues but non-blocking
- `[SKIP]` -- Step not applicable to this session

**If any FAIL exists:** Do not close the session. Fix the failing step first, then re-run summary.

**If only WARN/SKIP:** Safe to close. Warnings are informational.

---

## Timing Expectations

| Step | Typical Duration | Notes |
|------|-----------------|-------|
| 1. Resource audit | 5-15s | Depends on whether audit needs to run |
| 2. MEMORY.md | 10-30s | Writing + verification |
| 3. Lessons | 5-20s | Only if qualifying errors exist |
| 4. Plan status | 5-10s | Quick read + update |
| 5. Pending items | 10-20s | Writing resume instructions |
| 6. Workspace checklist | 5-30s | Depends on items |
| 7. Git checkpoint | 5-15s | Commit + push |
| 8. Supabase sync | 2-5s | Handled by checkpoint.py |
| 9. Summary | 2-5s | Report generation |
| **Total** | **~1-3 min** | Most sessions under 2 minutes |