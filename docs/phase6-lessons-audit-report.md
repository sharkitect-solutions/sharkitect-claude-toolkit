# Phase 6B: Lessons-Learned Audit Report
> **Created:** 2026-04-15
> **Auditor:** Sentinel workspace
> **Status:** COMPLETE — Skill Hub to execute fixes
> **File audited:** `~/.claude/lessons-learned.md` (1105 lines, 78 entries across 7 categories)

---

## Audit Summary

| Check | Count |
|-------|-------|
| Entries audited | 78 |
| PASS (verified accurate) | 55 |
| DELETE (obsolete/contradicted) | 3 |
| UPDATE (partially stale) | 7 |
| MERGE (same-class duplicates) | 10 (→ 4 merged entries) |
| MOVE (wrong category) | 3 |

---

## 1. ENTRIES TO DELETE (3)

### DELETE-1: `[2026-04-08] process: Trigger file pattern for scheduled AI tasks` (line ~665)
- **Reason:** Explicitly marked `[OBSOLETE]` in the entry itself. Superseded by the 3-tier scheduling architecture entry (line ~801). The entry even says "OBSOLETE (2026-04-09)."
- **Action:** Delete entirely. The corrected architecture entry (line ~801) already contains the valid information.

### DELETE-2: `[2026-04-08] process: Project/task status updates must be automated, not manual` (line ~672)
- **Reason:** Superseded by two newer, more complete entries:
  - `[2026-04-15] process: Supabase task updates must be enforced, not requested` (line ~549) — describes the 3-layer enforcement solution
  - `[2026-04-15] process: Task completion must update ALL tracking surfaces` (line ~1067) — describes the multi-surface update protocol
  - The 2026-04-08 entry says "Until the auto-status hook is built (gap-2026-04-08-001)" — that hook (`supabase-status-nudge.py`) now exists.
- **Action:** Delete. Fully superseded.

### DELETE-3: `[2026-04-09] process: Resource auditor must catch process gaps` (line ~1025)
- **Reason:** References `gap-2026-04-09-002` and describes a needed enhancement. The resource-audit-hook.py exists but the "fourth gap type: PROCESS" was never implemented. This is a feature request disguised as a lesson. Should be a Supabase task, not a lessons-learned entry.
- **Action:** Delete from lessons-learned. If the enhancement is still desired, add as a Supabase task under Skill Hub.

---

## 2. ENTRIES TO UPDATE (7)

### UPDATE-1: `[2026-04-12] tool-usage: Claude Code hooks "if" field` (line ~127)
- **Current:** Says "Our Claude Code is v2.1.71 -- NOT yet available."
- **Verified:** Claude Code is still v2.1.71 as of 2026-04-15. Entry is still correct.
- **Action:** No change needed yet. Recheck after next Claude Code upgrade.
- **Status:** PASS (still accurate)

### UPDATE-2: `[2026-04-09] approach: pre-modify-checkpoint.py hook references phantom checkpoint.py` (line ~320)
- **Current:** Says "The hook itself needs to be fixed or removed."
- **Verified:** `pre-modify-checkpoint.py` still exists at `~/.claude/hooks/`. It still references `checkpoint.py` which still doesn't exist.
- **Action:** Update entry to note the hook is STILL unfixed. Add recommendation: either rename to `checkpoint-reminder.py` (which also exists in hooks/ — possible duplicate?) or delete and consolidate with `checkpoint-reminder.py`.
- **Suggested text update:** Add line: "*Status (2026-04-15):* Hook still exists unfixed. `checkpoint-reminder.py` may serve the same purpose — consolidation recommended."

### UPDATE-3: `[2026-04-08] preference: CEO brief formatting — scannable, bold headers` (line ~475)
- **Current:** Says "Use Telegram MarkdownV2 with bold `*HEADERS*`"
- **Contradiction:** The Telegram formatting entry (line ~221) says "DON'T USE MarkdownV2... Use HTML instead."
- **Action:** Update line 478 to say "Use Telegram Markdown (`parse_mode: HTML` with `<b>` tags)" instead of "MarkdownV2 with bold `*HEADERS*`." The rest of the entry (structure, emojis, bullets) is correct.

### UPDATE-4: `[2026-04-14] process: NON-NEGOTIABLE — All documents must have created/updated metadata` (line ~738)
- **Current:** Says "Phase 8 of the master plan includes a full backfill pass."
- **Update needed:** Phase 8 hasn't started. This is still accurate as a forward reference. However, the entry references "documentation-standards.md" which was completed in Phase 5D. Add reference to the completed SOP.
- **Suggested addition:** "Full standard defined in `~/.claude/docs/documentation-standards.md` (completed Phase 5D)."

### UPDATE-5: `[2026-04-14] direction: Parent-child relational model is MANDATORY` (line ~943)
- **Current:** Says "Migration plan: Current Supabase projects/tasks schema will be restructured as part of Foundation Reset Phase 6/7."
- **Update needed:** We are NOW in Phase 6. The 6A audit confirmed projects/tasks use text-matching (no FK). This migration should be planned for Phase 7 or deferred. Update to reflect current phase context.
- **Suggested text:** Change "Phase 6/7" to "Phase 7 (schema rebuild phase)."

### UPDATE-6: `[2026-04-09] platform: Claude Code plugin auto-update wipes local plugin cache` (line ~1032)
- **Current:** References gap-2026-04-09-003 and says a prevention hook is needed.
- **Verified:** `~/.claude/plugins/cache/local/` exists with 4 plugins (aios-core, auto-sync, phase-gate, quality-gate). The prevention hook was never built.
- **Action:** Update to note plugins are currently present, but the protection hook still hasn't been built. Risk remains.

### UPDATE-7: `[2026-04-05] platform: Plugin hooks using python3 fail on Windows` (line ~296)
- **Current:** References "hookify" and "ralph-loop" plugins specifically.
- **Verified:** Both plugins still exist. Windows App Execution Aliases fix is still relevant.
- **Action:** Add note that this applies to ALL plugins, not just hookify/ralph-loop. Any plugin with `python3` in hooks.json will fail.

---

## 3. ENTRIES TO MERGE (10 → 4 merged entries)

### MERGE-1: schtasks/Git Bash path mangling (3 entries → 1)
- `[2026-04-09] platform: schtasks via git bash requires cmd.exe wrapper` (line ~184)
- `[2026-04-08] platform: schtasks in Git Bash needs MSYS_NO_PATHCONV=1` (line ~207)
- `[2026-04-09] platform: Task Scheduler /tr paths with spaces MUST be quoted` (line ~214)

**Proposed merged entry:**
```
### [2026-04-09] platform: Windows Task Scheduler from Git Bash — complete reference

**Problem:** schtasks commands from Git Bash fail in multiple ways due to MSYS path conversion and Windows quoting rules.

**Solutions (use ALL together):**
1. Prefix with `MSYS_NO_PATHCONV=1` to prevent `/flag` → `C:/Program Files/Git/flag` mangling
2. Always quote `/tr` paths containing spaces: `/tr "\"C:\path with spaces\script.bat\""`
3. Use full python.exe path in .bat files: `"C:\Users\...\Python312\python.exe"`
4. Skip `/rl HIGHEST /ru "username"` flags to avoid "Access denied" (tasks run fine without elevation)
5. After creating a task, run `schtasks /run /tn "TaskName"` to verify it works (267011 = "never ran yet," not a failure)

**Tags:** windows, task-scheduler, schtasks, git-bash, msys, path-mangling, quoting, MSYS_NO_PATHCONV
```

### MERGE-2: n8n HTTP Request / Code node limitations (2 entries → 1)
- `[2026-04-10] tool-usage: n8n Code node sandbox does NOT have fetch or $http` (line ~247)
- `[2026-04-10] tool-usage: Testing n8n schedule-triggered workflows via API` (line ~254)

**Proposed merged entry:**
```
### [2026-04-10] tool-usage: n8n execution constraints — Code node sandbox + schedule trigger testing

**Code node sandbox:** `fetch()` and `$http` are not available. Use `$helpers.httpRequest({...})` with `await`. If $helpers also fails, replace with HTTP Request nodes chained via Merge nodes (append mode).

**Testing schedule-triggered workflows:** n8n public API doesn't support executing schedule-triggered workflows. Add a temporary Webhook node, connect to first processing node, activate, trigger via curl, verify, then remove webhook.

**Tags:** n8n, code-node, sandbox, fetch, http, testing, webhook, schedule-trigger
```

### MERGE-3: Verify-before-acting pattern (3 entries → 1)
- `[2026-04-09] approach: NEVER reference a tool, script, or file without verifying it exists` (line ~822)
- `[2026-04-09] approach: Read lessons-learned.md BEFORE proposing solutions` (line ~843)
- `[2026-04-08] approach: ALWAYS verify tool capabilities before building on them` (line ~853)

**Proposed merged entry:**
```
### [2026-04-09] approach: VERIFY before acting — tools, files, capabilities, and lessons

Three distinct verification failures, all with the same root cause: acting on assumptions instead of checking.

**Rule (3 checks before ANY action):**
1. **Verify existence:** Before running a script or referencing a file, `ls` or `find` it. If it doesn't exist, check what DOES exist that serves the same purpose.
2. **Verify capabilities:** Before building on a tool, read its source code. "Loop" doesn't mean "scheduler." Test in isolation first.
3. **Verify history:** Before proposing a solution, grep lessons-learned.md for the tool/approach. If there's a documented failure, acknowledge it.

**Incidents:**
- checkpoint.py: phantom reference in skill, never existed, supabase-sync.py was the real tool
- ralph-loop: assumed it was a scheduler from its name, built 9 automations that never worked
- RemoteTrigger: proposed for CEO briefs despite documented MCP cold-start failure

**Tags:** verification, assumptions, phantom-references, tools, trust, pre-planning
```

### MERGE-4: Cross-workspace workspace path verification (2 entries → 1)
- `[2026-04-14, REPEATED 2026-04-15] approach: ALWAYS verify workspace filesystem paths` (line ~273)
- The `direction: Cross-workspace shared state must be ONE global file` (line ~814)

**These should NOT be merged** — they address different concerns (filesystem paths vs data file location). Both PASS.

---

## 4. ENTRIES TO MOVE (wrong category) (3)

### MOVE-1: `[2026-04-08] platform: Hidden background processes on Windows` (line ~289)
- **Currently in:** Approach section (between lines 270-302)
- **Should be in:** Platform section
- **Reason:** This is a platform-specific Windows issue, not an approach/methodology lesson.

### MOVE-2: `[2026-04-08] tool-usage: Telegram MarkdownV2 requires escaping` (line ~221)
- **Currently in:** Platform section (after platform entries end at line 213)
- **Should be in:** Tool Usage section
- **Reason:** It's about Telegram API behavior, not OS/platform issues. (It appears to already be in the right location on re-check — it's between Platform and Approach sections. The section header "---" before Approach is at line 269.)
- **CORRECTION:** Actually checking line numbers more carefully — this entry IS in the right zone (after the Platform section separator at line 199). However, there's no clear section header for it. It lives between "Platform" entries and "Approach" entries without being clearly in either. **Action:** Move explicitly under Tool Usage header.

### MOVE-3: `[2026-04-09] tool-usage: Task Scheduler 267011` (line ~864)
- **Currently in:** Process Decisions section
- **Should be in:** Tool Usage section (or merged into MERGE-1 above)
- **Reason:** This is a tool behavior fact, not a process decision.

---

## 5. CATEGORY DISTRIBUTION (current)

| Category | Count | Assessment |
|----------|-------|-----------|
| API Limitations | 7 | Clean — all Airtable/Gmail/Google Drive. Well-documented. |
| Tool Usage | 13 | Slightly scattered — 2 entries misplaced in other sections |
| Platform | 7 | Clean. One entry (background processes) should move from Approach. |
| Approach | 8 | Clean after merges. |
| Preferences | 19 | Largest section. All verified accurate. |
| Process Decisions | 20 | 3 entries should be deleted, 1 moved out. |
| Architecture Direction | 12 | Clean. Well-structured. |

---

## 6. TAG CONSISTENCY CHECK

| Issue | Examples | Fix |
|-------|----------|-----|
| Case inconsistency | None found | PASS |
| Abbreviation variants | `n8n` used consistently | PASS |
| Duplicate tags | `supabase` vs `Supabase` | None found — all lowercase | PASS |
| Missing tags | Some entries lack tags entirely | All entries have tags | PASS |

**Tag standardization: CLEAN.** No inconsistencies found.

---

## 7. PATTERN SYNTHESIS

### Pattern A: "Verify before acting" (3 entries → MERGE-3 above)
Already captured as a merge. The synthesis: **one verification rule with 3 checks** instead of 3 separate stories.

### Pattern B: "Supabase updates must be immediate and enforced" (3 entries)
- Line ~549: Supabase task updates must be enforced
- Line ~672: Project/task status updates must be automated (DELETE-2, superseded)
- Line ~1067: Task completion must update ALL tracking surfaces

**After DELETE-2, the remaining 2 entries are complementary** (one about enforcement mechanism, one about scope of update). No further merge needed.

### Pattern C: "n8n workflow building rules" (5+ entries)
Multiple entries about n8n best practices: native nodes > HTTP Request, JSON.stringify for dynamic data, model dropdown values, Merge nodes for parallel branches, test via webhook. These are different enough to remain separate — they address distinct failure modes. No merge needed.

---

## 8. PROACTIVE FINDINGS (6E preview from 6B)

1. **pre-modify-checkpoint.py is a live ticking bomb.** It fires on every Write/Edit and references `checkpoint.py` which doesn't exist. This generates noise on every file operation. Either fix it to reference a real tool, or delete it. A `checkpoint-reminder.py` hook also exists — possible overlap. Recommend consolidation.

2. **Lessons-learned.md at 1105 lines is getting unwieldy.** 78 entries in a flat file. Once populated to Supabase `lessons_learned` table (Phase 6B output), consider whether the flat file should be archived and Supabase becomes the primary query surface. The flat file is useful for `grep` in pre-task checks, but Supabase enables filtered queries by category/tag/workspace.

3. **No automated test that lessons-learned entries reference valid paths/tools.** A simple script could grep all file paths and command references in the file and verify they exist. Would catch phantom references before they mislead a session.

---

## Execution Instructions for Skill Hub

1. **DELETE** the 3 entries listed in Section 1
2. **UPDATE** the 7 entries listed in Section 2 with the suggested changes
3. **MERGE** the 10 entries into 4 as specified in Section 3 (delete originals, add merged versions)
4. **MOVE** the 3 entries to their correct categories as noted in Section 4
5. **After cleanup:** Populate the Supabase `lessons_learned` table with all remaining entries
6. **Verify:** Run a final count — should be approximately 67 entries (78 - 3 deleted - 6 merged away - 2 from DELETE supersession = ~67)

---

*Report generated by Sentinel workspace as part of Foundation Reset Phase 6B.*
*Skill Hub executes the fixes. Sentinel verifies after completion.*
