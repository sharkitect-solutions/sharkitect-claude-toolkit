# Session Checkpoint Failure Modes

Five named anti-patterns that erode the checkpoint system. Each includes detection signals, quantified consequences, and recovery procedures.

---

## The Five Failure Modes

| Anti-Pattern | Core Error | Detection Signal | Consequence |
|---|---|---|---|
| **The Phantom Checkpoint** | Running checkpoint but skipping verification | Summary shows all PASS but you didn't actually check each step | False confidence. MEMORY.md stale, lessons lost, gaps undetected. Next session starts blind. |
| **The Perpetual Postponer** | "I'll checkpoint at the end" then forgetting | Session exceeds 30+ tool calls with no mid-session save | If context compacts or session crashes, all progress since last checkpoint is lost. Recovery requires re-reading diffs. |
| **The Selective Saver** | Committing code but skipping memory/lessons/plans | Git shows commit but MEMORY.md timestamp is from 3 sessions ago | Code is backed up but context is lost. Next session has code it doesn't understand. The "what" is saved but the "why" is gone. |
| **The Summary Skipper** | Completing steps 1-8 but skipping the summary report | No pass/fail output generated | User doesn't know what succeeded. Failures are hidden. No accountability trail. |
| **The Quick-Mode Abuser** | Always using --mid instead of full checkout | Full checkout hasn't run in 3+ sessions despite significant work | Memory drifts. Lessons accumulate uncaptured. Resource gaps go undetected. System stops learning. |

---

## Failure Mode Interaction Matrix

Failure modes compound. One leads to another:

```
Perpetual Postponer --> session crashes --> Selective Saver (recovers code only)
                                              |
                                              v
Quick-Mode Abuser <-- "full mode takes too long" rationalization
       |
       v
Phantom Checkpoint <-- "I'll just run through it fast"
       |
       v
Summary Skipper <-- "I already know it passed"
```

**The death spiral:** Postponing leads to rushing, rushing leads to skipping, skipping leads to blindness, blindness leads to more postponing because "nothing seems broken."

---

## Rationalization Table

| What You Tell Yourself | Surface Logic | Why It Fails | What To Do Instead |
|---|---|---|---|
| "Nothing important happened this session" | Low-activity sessions don't need checkpoints | Even reading and deciding NOT to change something is a decision worth recording. Non-action decisions prevent future re-investigation. | Run full checkout. If truly nothing happened, it completes in 30 seconds. |
| "I'll remember where I left off" | Short-term memory feels reliable | You won't. Context compression, session gaps, and attention shifts guarantee you'll lose thread. The whole point of MEMORY.md is that you CAN'T remember. | Write resume instructions now while context is fresh. 60 seconds now saves 10 minutes next session. |
| "The code commit is enough" | Git preserves all file changes | Git preserves WHAT changed. It doesn't preserve WHY you made that choice, what alternatives you rejected, what patterns you noticed, or what the user's preferences are. | Code + context = complete checkpoint. Code alone = half a checkpoint. |
| "Quick mode is fine for this session" | Mid-session checkpoint covers the basics | Quick mode only does git + Supabase. It skips resource audit, memory update, lessons capture, plan status, and workspace checklist. After 3 quick-only sessions, you're 15+ checks behind. | If the session produced deliverables or decisions, use full mode. Reserve --mid for literal save-and-continue moments. |
| "I'll do a thorough checkpoint next session" | Defer now, compensate later | Next session has its own work. Deferred checkpoints never get retroactively thorough. The context needed to write accurate resume instructions exists NOW, not later. | Do it now. The protocol takes 1-3 minutes. The recovery cost of skipping is 10-30 minutes next session. |

---

## Recovery Procedures

### When You Realize a Checkpoint Was Phantom

1. Stop current work
2. Read the last checkpoint's summary output (if it exists)
3. For each PASS claim, verify it's actually true:
   - MEMORY.md: check last-modified timestamp
   - Git: `git log -1` -- does the commit exist?
   - Supabase: check brain sync timestamp in `.tmp/last-checkpoint.json`
4. Re-run any steps that were falsely marked PASS

### When Multiple Sessions Were Quick-Mode Only

1. Run full checkout now, even if mid-session
2. Check MEMORY.md -- is it current? Update with accumulated learnings
3. Check `~/.claude/lessons-learned.md` -- any resolved errors from recent sessions not captured?
4. Check active plan -- does it reflect actual state?
5. Consider this a "debt payment" session -- the system fell behind

### When Session Crashed Without Checkpoint

1. Check `.tmp/last-checkpoint.json` for most recent save point
2. Run `git log -5` to see what was committed
3. Run `git diff` to see uncommitted changes
4. Reconstruct session context from:
   - Git diff (what changed)
   - `.tmp/compact-context.md` (if compaction happened)
   - `.tmp/session-errors.json` (if errors were tracked)
5. Create a recovery checkpoint: `git add . && git commit -m "recovery after crash" && git push`
6. Update MEMORY.md with whatever context you can reconstruct

---

## The Checkpoint Quality Test

After completing a full checkout, ask yourself:

> "If I lost all conversation context right now and started a fresh session, could I resume effectively using only MEMORY.md, the plan file, and git history?"

- **YES** = checkpoint is complete
- **NO** = something was skipped. What would you need that isn't recorded?

This is the definitive test. Everything else is process -- this is the outcome that matters.