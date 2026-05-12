---
name: session-checkpoint
description: "Use when user wants a mid-session quick save -- 'checkpoint', 'save progress', 'back up before risky changes', '/session-checkpoint', or before compacting context. Does git commit + push + Supabase brain sync. That's it -- no audit, no lessons capture, no .tmp/ audit, no self-kill. Get back to work fast. Do NOT use for: end-of-session wrap-up (use end-session for the full 9-step audit + cleanup), skill syncing (use sync-skills.py), document freshness reviews (use document-lifecycle), resource gap detection (use resource-auditor)."
---

# Session Checkpoint (Mid-Session Quick Save)

Fast, minimal, non-disruptive mid-session save. Commits and pushes current work to git, syncs brain memories to Supabase, returns control. No audit. No lessons capture. No `.tmp/` sweep. No self-kill.

**Renamed/split on 2026-05-11.** This skill is now MID-ONLY. The full end-of-session protocol moved to a separate `end-session` skill. The old `--mid` flag is gone -- mid-session IS the only mode now.

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Save progress" / "checkpoint" / "back up before risky changes" / "/session-checkpoint" | YES | -- |
| "End session" / "wrap up" / "done for today" / "/end-session" | NO | end-session (full 9-step + self-kill) |
| "Sync skills to GitHub repo" | NO | sync-skills.py --sync --push |
| "Check if docs are still accurate" | NO | document-lifecycle |
| "Did I use all available resources?" | NO | resource-auditor |
| "Push memories to Supabase only" | PARTIAL (also commits git) | supabase-sync.py push (Supabase only) |

## Steps

1. **Stage and commit** any unstaged + staged changes:
   ```bash
   git add <changed files> && git commit -m "<short description of what was done>"
   ```
   If nothing to commit, skip silently -- no empty commits.

2. **Push** to remote:
   ```bash
   git push
   ```
   If no remote configured or push fails: WARN, do not block. Local commit still preserves state.

3. **Sync brain memories to Supabase** (if `supabase-sync.py` available in workspace):
   ```bash
   python tools/supabase-sync.py push
   ```
   If script missing or Supabase credentials absent: WARN, do not block.

4. **Report** to the user in one line:
   - Commit hash (short)
   - Push status (pushed / local-only / no remote)
   - Supabase status (synced / skipped / error)

## What This Skill Does NOT Do

| Step | Why omitted |
|---|---|
| Resource audit | Mid-session is not a wrap-up; nothing to audit yet |
| MEMORY.md update | User is still working; updates happen continuously, not at every save |
| Lessons capture | Lessons get captured at end-session, not at every mid-save |
| Plan status update | Done during the work, not as a save step |
| Pending items | Not closing the session |
| `.tmp/` audit | Disposable scratch isn't worth auditing mid-session |
| Self-kill | Session continues -- no process to kill |
| Session brief | Brief is the end-of-session deliverable |

If the user means end-of-session, route to `end-session` instead. Symptoms that indicate end-of-session (not mid):
- "wrap up", "done for today", "stop for the day", "close out", "save session", "end session"
- The session-checkpoint-enforcer hook will block other tools until `end-session` is invoked when these phrases are detected

## Failure Modes

| Symptom | Fix |
|---|---|
| `git commit` fails with pre-commit hook error | Fix the underlying issue (the hook is doing its job), re-stage, re-commit. Do NOT use `--no-verify`. |
| `git push` rejected (non-fast-forward) | Pull/rebase first if appropriate, then re-push. Do NOT force-push without explicit user approval. |
| `supabase-sync.py push` fails with network error | WARN and continue. Commit is already durable in git; Supabase will pick up next time. |
| No `tools/supabase-sync.py` in this workspace | SKIP step 3 silently, WARN once. |

## When To Use vs `/end-session`

- **`/session-checkpoint`** (this skill): "save my work, I'll keep going."
- **`/end-session`**: "I'm done for the day -- audit, capture, sync, push, kill orphan processes, terminate this session cleanly."

If you're not sure which one the user wants, ask. Default to NOT auto-routing -- mid vs end is not interchangeable.
