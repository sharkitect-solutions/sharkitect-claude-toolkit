# Permissions Overhaul + Inbox Amendment System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Claude Code Auto-Mode's implicit self-modification gate with an explicit two-layer permissions architecture (global allowlist + workspace-scoped denies), ship a generic inbox-item amendment CLI tool covering 13 modes across WR/routed-task/lifecycle-review, consolidate the close-state vocabulary to 5 distinct values (deprecating `processed`/`resolved` to `completed`), and add `withdrawn` as a source-controlled close state.

**Architecture:** Templates source-of-truth at `~/.claude/config/workspace-permissions-templates.json`. `sync-permissions.py` propagates atomically to 4 settings.json files (1 global + 3 workspace) with timestamped backup, idempotent. `inbox-amend.py` (NEW) routes all source-side modifications through validated CLI with source-identity check, status guard, append-only history, and auto-close on supersede/duplicate/withdraw via `close-inbox-item.py`. Direct AI Edit on cross-workspace inbox files is denied; new-file creation via Bash-launched scripts remains allowed (subprocess writes bypass the AI's Edit/Write tool gate). Spec approved 2026-04-28 at `<Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md`.

**Tech Stack:** Python 3.12 stdlib only (json, pathlib, shutil, argparse, datetime, hashlib, subprocess, sys, os, tempfile, uuid). pytest (already used in `~/.claude/tests/`). Claude Code permissions syntax: `Edit(<pattern>)`, forward-slash POSIX paths on Windows (`/c/...`), `~/` expands, `**` recursive glob, deny precedence wins.

---

## Execution Status

- **Session 1 (2026-04-28): Phases 0+A+B COMPLETE.** All 6 tasks (Phase 0 + A1/A2/A3 + B1/B2) shipped. inbox-amend.py at 24/24 tests passing. Toolkit commits 45196ab → c490c20 pushed. Parser bug discovered + fixed in B2: subparser dest renamed `mode` → `command` to avoid bulk-amend `--mode` flag collision (note for retrospective).
- **Session 2 (2026-04-28): Phases C+D COMPLETE.** All 5 tasks (C1/C2/C3 + D1/D2) shipped + 2 review fix-up passes applied. close-inbox-item.py: withdrawn status, --annotate mode, processed/resolved deprecation, inbox/ guard, close-state guard, source-removal test invariants. sync-permissions.py: TDD-shipped, _validate_templates, type guards, backup collision avoidance, ValueError-not-SystemExit, +2 tests for rc=2 and validator coverage. Test totals: 38/38 across B+C+D (24+6+8). Toolkit commits 143955e → bec7ec6 pushed.
- **Session 4 (2026-04-29 cron PID 39392 fresh chat in Skill Hub): F1 PASS — hard gate validator confirms Phase 1 allow rule operative in fresh sessions.** F1 ran end-to-end (bash create marker → Edit tool append "Phase 1 verified" → bash rm cleanup) with zero permission prompts and zero bypass keywords. Confirms `Edit(~/.claude/rules/**)` in global settings.json overrides the runtime self-modification gate that denied edits in Session 3. Plan + MEMORY updated; F2-F8 ready-to-paste prompts written to `<Skill Hub>/.tmp/F2-F8-fresh-chat-prompts.md`. **REMAINING:** F2-F6 (HQ fresh chat) + F7 (Sentinel fresh chat) + F8 (any chat).
- **Session 5 (2026-04-29 HQ fresh chat): F2 PASS, F3 PASS, F6 PARTIAL PASS, F8-HQ-side partial PASS; F4 + F5 BLOCKED-FINDING (defense-in-depth working stronger than plan expected). Phase F COMPLETE.** F2: Write to `~/.claude/rules/.smoke-test-2026-04-28-2.md` correctly DENIED with "File is in a directory that is denied by your permission settings." F3: Edit append + revert on `~/.claude/lessons-learned.md` both succeeded; methodology-nudge fired advisory on 2nd Edit (correctly non-blocking). F4: bash heredoc to Sentinel `.routed-tasks/inbox/` DENIED by additional shell-bypass guard ("circumventing the Edit deny rule covering that path") — MORE secure than plan premise that "bash CREATE bypasses Edit deny." F5: bash pre-place DENIED by separate scope-creep guard ("Creating a fake test routed-task with misrepresented source_workspace in another workspace's inbox is scope creep") — F5 cannot run from HQ without alternative pre-placement method. F6: steps 1-3 PASS (`wr-hq-2026-04-29-002` filed, `amend-2026-04-29-e639e4f4` applied with source_amendments[0] populated, withdraw cleanly closed new→withdrawn + Supabase row updated); step 4 CORRECTLY SKIPPED per self-filed-item anti-ping-pong rule (same workspace files+closes WR; "skip: self-filed item (source==closer=workforce-hq)"). F8 HQ-side: no orphan smoke artifacts beyond the Phase F task itself. **Policy decisions adopted (HQ recommendation option a):** (1) F4/F5 — defense-in-depth working as designed; bash bypass blocked is MORE secure, no carve-out (carve-outs erode the deny scaffolding); (2) F6 step 4 — anti-ping-pong skip is design-correct for self-filed scenarios; F6 expectation about cross-workspace notification only applies when source ≠ closer.
- **Session 3 (2026-04-28): Phases E + G + H1-H3 + H7-H9 COMPLETE in-session; H4 + H5 + H6 + Phase F DEFERRED to fresh chat.** E1 dry-run validated; E2 executed with **Windows POSIX path bug discovered + fixed inline** in `sync-permissions.py` `_expand_path` (`//c/...` resolved as UNC on Windows; translation to `c:/...` added; regression test `test_expand_path_translates_posix_drive_letter_on_windows` added; 9/9 sync tests pass; total 39/39 across B+C+D+E1-regression). All 4 settings.json now valid (60 allow + 17 deny global; HQ 38, SH 27, Sentinel 41 deny). E3: Skill Hub `.claude/settings.json` committed (36dadbc); commit-settings routed-tasks filed to HQ + Sentinel. G1: rt-sentinel-2026-04-28-add-withdrawn-enum filed. H1-H3: 3 architecture docs at `~/.claude/docs/` (permissions-architecture 320L, inbox-amendment-protocol 458L, permissions-emergency-override 110L; via SDD subagent; all sections + all 13 modes verified; no placeholders). H7: plans-registry updated; Supabase project b66c5528-65fc-457f-a6e1-29ccdeb6353b created; 8 phase tasks (A-E,G marked completed). H8: lessons-learned.md gained quality-over-speed preference + Windows POSIX path lesson + runtime self-modification gate architecture direction; Skill Hub MEMORY.md resume entry updated. H9: toolkit final commit 0f0ff78 pushed. **Toolkit commits this session: bb18078 (sync-permissions.py Windows POSIX fix + regression test + settings-backup snapshot), 0f0ff78 (lessons-learned).** Skill Hub workspace commit: 36dadbc. **DEFERRED — runtime self-modification gate denied edits to `~/.claude/rules/` despite the `Edit(~/.claude/rules/**)` allow rule landing in settings.json (exactly the open risk in plan Risks table; gate operates above settings.json layer):** H4 paste cron rules from HUMAN-ACTION-REQUIRED.md staging, H5 close wr-hq-2026-04-27-007 (must follow H4), H6 mark 2 HUMAN-ACTION entries done, Phase F 8 smoke tests in NEW chats (F1 in SH = hard gate). **Resume in fresh chat in Skill Hub:** if Edit `~/.claude/rules/` still denied, fallback `defaultMode: "acceptEdits"` in global settings.json OR ask user to paste manually → complete H4-H6 → run F1-F8 across SH+HQ → final toolkit commit if anything changes.

---

## Pre-Plan Context (read first if zero context)

**Spec:** `<Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md` -- read this BEFORE starting. Plan implements that design.

**Why:** Claude Code runtime updated to a stricter Auto-Mode gate. Workspace autonomy contract ("revertible-in-5-min == autonomous") is workspace-level and doesn't override the runtime. Custom hooks accumulated to 42 (target 30); 17 fire on every Edit/Write. Cross-workspace inbox coordination has no source/target authority enforcement.

**Out of scope (deferred to follow-on plans):**
- Hook consolidation 42→28 (separate plan)
- Toolkit-wide governance + evolution loop (Phase 3 vision)
- Sentinel-side `withdrawn` enum migration (routed-task filed in Phase G of this plan; Sentinel executes separately)
- Routed-task and lifecycle-review handler wiring beyond what comes free from the generic design (Phase 1.5)

**User-locked decisions (do not re-litigate):**
- Generic from day 1 (covers WR, routed-task, lifecycle-review)
- Withdrawn (not Cancelled) as new close state name
- Bulk amend included
- Continue-on-failure semantics for bulk-amend
- Notify with explicit reason on withdraw
- 3-session execution split (Phases A+B / C+D / E+F+G+H)
- Quality > speed; right the first time

---

## File Structure

### New files (created in this plan)

| Path | Responsibility |
|------|---------------|
| `~/.claude/config/workspace-permissions-templates.json` | Source of truth: allow/deny rules per scope |
| `~/.claude/scripts/sync-permissions.py` | Reads templates, writes 4 settings.json with backup |
| `~/.claude/scripts/inbox-amend.py` | Generic source-side amendment CLI |
| `~/.claude/tests/test_sync_permissions.py` | pytest suite for sync-permissions |
| `~/.claude/tests/test_inbox_amend.py` | pytest suite for inbox-amend |
| `~/.claude/docs/permissions-architecture.md` | Reference: two-layer model |
| `~/.claude/docs/inbox-amendment-protocol.md` | Reference: amendment modes + schema + state machine |
| `~/.claude/docs/permissions-emergency-override.md` | Procedure when system blocks legitimate work |
| `<Skill Hub>/.claude/settings.json` | NEW workspace settings (currently missing) |
| `<Sentinel>/.claude/settings.json` | NEW workspace settings (currently missing) |

### Modified files

| Path | Change |
|------|--------|
| `~/.claude/settings.json` | Add Edit/Write allow + deny entries; preserve existing 25 Bash allow / 10 Bash deny |
| `<HQ workspace>/.claude/settings.json` | Add `permissions.deny` block (currently has `hooks` only) |
| `~/.claude/scripts/close-inbox-item.py` | Add `withdrawn` status, `--annotate` mode, deprecate `processed`/`resolved` with auto-conversion |
| `~/.claude/tests/test_close_inbox_item.py` | Add tests for the above |
| `~/.claude/rules/universal-protocols.md` | Update Status Vocabulary Layers section + paste cron-user-review-flag rule (closes wr-hq-007) |
| `~/.claude/lessons-learned.md` | Append: quality-over-speed preference + design rationale |
| `~/.claude/docs/plans-registry.md` | Add active plan entry |
| `<Skill Hub>/HUMAN-ACTION-REQUIRED.md` | Mark items #2 (Tier 1) and #3 (cron rule) as done |

### Workspace path constants (used throughout plan)

```
GLOBAL_DIR     = ~/.claude
HQ_DIR         = //c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ
SKILLHUB_DIR   = //c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub
SENTINEL_DIR   = //c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel
TOOLKIT_DIR    = $SKILLHUB_DIR/sharkitect-claude-toolkit
```

When commands below show `$SKILLHUB_DIR` etc., substitute the literal path.

---

## Phase 0 — HQ work request triage (~5-10 min, before Phase A) **[COMPLETE 2026-04-28 — all 5 deferred to enforcement-hook batch]**

Five WRs landed from HQ on 2026-04-28 while the plan was being designed. Triage them BEFORE Phase A so we know if anything blocks Phase 1 work or needs urgent attention. None are CRITICAL based on filename, but verify.

### Task 0.1: Read all 5 incoming HQ WRs

**Files:**
- Read: `<Skill Hub>/.work-requests/inbox/2026-04-28_workforce-hq_*.json` (5 files)

- [ ] **Step 1: Read the inbox context**

```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/request-watcher.py --context 2>&1 | head -80
```

Expected: lists all WRs in inbox; identify the 5 from HQ with 2026-04-28 timestamps:
- `hq-content-enforcer-skill-shou-002`
- `hq-knowledge-governance-skill-004`
- `methodology-+-specialist-skill-001`
- `n8n-workflow-debugger-agent-(s-005`
- `superpowers-systematic-debuggi-003`

- [ ] **Step 2: Classify each by severity + actionability**

For each of the 5 WRs, read the JSON and record:
- severity (info/warning/high/critical)
- request_type (MISSING/UNUSED/FALLBACK/TASK/BUG/ENHANCE)
- whether it blocks Phase 1 work
- estimated fix complexity

Use the table:

| WR | Severity | Type | Blocks Phase 1? | Fix complexity | Recommendation |
|----|----------|------|-----------------|----------------|----------------|
| ... fill in | | | | | |

### Task 0.2: Decide handle now vs defer

- [ ] **Step 1: For each WR, decide:**
  - **CRITICAL or blocks Phase 1**: handle inline before Phase A
  - **HIGH actionable + small fix**: handle inline before Phase A if total time < 30 min
  - **All others**: defer with `inbox-amend.py` (... but inbox-amend.py doesn't exist yet -- it's built in Phase B; for Phase 0, defer manually by editing the JSON's `status` to `deferred` with explicit reason in `status_history`)

- [ ] **Step 2: Document decisions**

Record decisions in this plan file as inline notes (or append to lessons-learned.md). Format:
```
- wr-xxxx: <decision>. Reason: <why>.
```

### Task 0.3: Proceed to Phase A or escalate

- [ ] **Step 1: Branch on findings**
  - If all 5 deferred or handled: proceed to Phase A1.
  - If any critical and handled: proceed to Phase A1 with note in plan.
  - If any blocks Phase 1 work in unforeseen way: HALT, file follow-on plan, do not start Phase A.

---

## Phase A — Foundation (~30 min) **[COMPLETE 2026-04-28]**

### Task A1: Backup all settings.json files

**Files:**
- Read: `~/.claude/settings.json`
- Read: `$HQ_DIR/.claude/settings.json`
- Create: `~/.claude/.tmp/settings-backups-2026-04-28/<source-name>.json.bak`

- [ ] **Step 1: Confirm pre-state of all 4 settings.json files**

Run:
```bash
echo "=== Global ==="; ls -la ~/.claude/settings.json
for ws in "1.- SHARKITECT DIGITAL WORKFORCE HQ" "3.- Skill Management Hub" "4.- Sentinel"; do
  base="c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/$ws"
  echo "=== $ws ==="
  ls -la "$base/.claude/settings.json" 2>&1
done
```

Expected: global EXISTS; HQ EXISTS; Skill Hub MISSING ("No such file"); Sentinel MISSING. If existence differs, halt and recheck plan.

- [ ] **Step 2: Create backup directory and copy existing files**

Run:
```bash
mkdir -p ~/.claude/.tmp/settings-backups-2026-04-28
cp ~/.claude/settings.json ~/.claude/.tmp/settings-backups-2026-04-28/global-settings.json.bak
cp "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.claude/settings.json" ~/.claude/.tmp/settings-backups-2026-04-28/hq-settings.json.bak
ls -la ~/.claude/.tmp/settings-backups-2026-04-28/
```

Expected: 2 .bak files (Skill Hub + Sentinel don't exist yet, nothing to back up).

- [ ] **Step 3: Commit safety backup to toolkit for cross-machine recovery**

Run:
```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/sharkitect-claude-toolkit"
mkdir -p safety-backups/2026-04-28
cp ~/.claude/.tmp/settings-backups-2026-04-28/*.bak safety-backups/2026-04-28/
git add safety-backups/2026-04-28/
git commit -m "Pre-paste safety backup: settings.json snapshot 2026-04-28 (plan Phase A1)"
git push
```

Expected: backup committed to remote; recoverable from any machine.

---

### Task A2: Define permissions templates source-of-truth

**Files:**
- Create: `~/.claude/config/workspace-permissions-templates.json`

- [ ] **Step 1: Create the templates file**

Write `~/.claude/config/workspace-permissions-templates.json`:

```json
{
  "schema_version": 1,
  "documented_at": "2026-04-28",
  "documented_by": "skill-management-hub",
  "source_plan": "~/.claude/plans/2026-04-28-permissions-and-inbox-amendment-system.md",
  "source_spec": "<Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md",

  "global_settings_path": "~/.claude/settings.json",
  "global_permissions": {
    "allow_additions": [
      "Edit(~/.claude/rules/**)",
      "Edit(~/.claude/CLAUDE.md)",
      "Edit(~/.claude/skills/**)",
      "Edit(~/.claude/agents/**)",
      "Edit(~/.claude/hooks/**)",
      "Edit(~/.claude/scripts/**)",
      "Edit(~/.claude/docs/**)",
      "Edit(~/.claude/lessons-learned.md)",
      "Edit(~/.claude/.tmp/**)",
      "Edit(~/.claude/config/**)",
      "Edit(~/.claude/tests/**)",
      "Edit(~/.claude/plans/**)",
      "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/**)",
      "Bash(python ~/.claude/scripts/sync-permissions.py *)",
      "Bash(python ~/.claude/scripts/inbox-amend.py *)",
      "Bash(git mv:*)",
      "Bash(git rm:*)",
      "Bash(git clone:*)",
      "Bash(git ls-files:*)",
      "Bash(git ls-tree:*)",
      "Bash(git show-ref:*)",
      "Bash(git submodule:*)",
      "Bash(git worktree:*)",
      "Bash(git reflog:*)",
      "Bash(git cherry-pick:*)",
      "Bash(git revert:*)",
      "Bash(git blame:*)",
      "Bash(git bisect:*)",
      "Bash(git apply:*)",
      "Bash(git format-patch:*)",
      "Bash(git ls-remote:*)",
      "Bash(git fsck:*)",
      "Bash(git gc:*)",
      "Bash(git prune:*)",
      "Bash(git notes:*)"
    ],
    "deny_additions": [
      "Edit(~/.claude/settings.json)",
      "Edit(~/.claude/settings.local.json)",
      "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/**/.claude/settings.json)",
      "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/**/.claude/settings.local.json)",
      "Edit(~/.claude/plugins/**)",
      "Edit(~/.claude/.env)",
      "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/**/.env)"
    ]
  },

  "workspaces": {
    "skill-management-hub": {
      "settings_path": "//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.claude/settings.json",
      "deny_global_skill_hub_owned": [],
      "deny_other_workspace_internals": [
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/_archive/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/assets/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/docs/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/knowledge-base/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/resources/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/tools/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/workflows/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.claude/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/CLAUDE.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/MEMORY.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/docs/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/supabase/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/tools/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/workflows/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.claude/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/CLAUDE.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/MEMORY.md)"
      ],
      "deny_inbox_direct_edit": [
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/processed/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.lifecycle-reviews/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.lifecycle-reviews/processed/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.routed-tasks/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.routed-tasks/processed/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.lifecycle-reviews/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.lifecycle-reviews/processed/**)"
      ],
      "deny_other_workspace_human_action": [
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/HUMAN-ACTION-REQUIRED.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/HUMAN-ACTION-REQUIRED.md)"
      ]
    },
    "workforce-hq": {
      "settings_path": "//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.claude/settings.json",
      "deny_global_skill_hub_owned": [
        "Edit(~/.claude/rules/**)",
        "Edit(~/.claude/skills/**)",
        "Edit(~/.claude/agents/**)",
        "Edit(~/.claude/hooks/**)",
        "Edit(~/.claude/scripts/**)",
        "Edit(~/.claude/CLAUDE.md)",
        "Edit(~/.claude/docs/**)",
        "Edit(~/.claude/config/**)",
        "Edit(~/.claude/tests/**)",
        "Edit(~/.claude/plans/**)"
      ],
      "deny_other_workspace_internals": [
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/docs/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/knowledge-base/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/resources/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/sharkitect-claude-toolkit/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/skill-comparison-test/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/tests/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/tools/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/workflows/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.claude/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/CLAUDE.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/MEMORY.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/docs/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/supabase/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/tools/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/workflows/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.claude/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/CLAUDE.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/MEMORY.md)"
      ],
      "deny_inbox_direct_edit": [
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/processed/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.lifecycle-reviews/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.lifecycle-reviews/processed/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.routed-tasks/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.routed-tasks/processed/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.lifecycle-reviews/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.lifecycle-reviews/processed/**)"
      ],
      "deny_other_workspace_human_action": [
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/HUMAN-ACTION-REQUIRED.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/HUMAN-ACTION-REQUIRED.md)"
      ]
    },
    "sentinel": {
      "settings_path": "//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.claude/settings.json",
      "deny_global_skill_hub_owned": [
        "Edit(~/.claude/rules/**)",
        "Edit(~/.claude/skills/**)",
        "Edit(~/.claude/agents/**)",
        "Edit(~/.claude/hooks/**)",
        "Edit(~/.claude/scripts/**)",
        "Edit(~/.claude/CLAUDE.md)",
        "Edit(~/.claude/docs/**)",
        "Edit(~/.claude/config/**)",
        "Edit(~/.claude/tests/**)",
        "Edit(~/.claude/plans/**)"
      ],
      "deny_other_workspace_internals": [
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/_archive/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/assets/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/docs/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/knowledge-base/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/resources/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/tools/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/workflows/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.claude/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/CLAUDE.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/MEMORY.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/docs/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/knowledge-base/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/resources/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/sharkitect-claude-toolkit/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/skill-comparison-test/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/tests/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/tools/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/workflows/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.claude/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/CLAUDE.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/MEMORY.md)"
      ],
      "deny_inbox_direct_edit": [
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/processed/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.lifecycle-reviews/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.lifecycle-reviews/processed/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/processed/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.lifecycle-reviews/inbox/**)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.lifecycle-reviews/processed/**)"
      ],
      "deny_other_workspace_human_action": [
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/HUMAN-ACTION-REQUIRED.md)",
        "Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/HUMAN-ACTION-REQUIRED.md)"
      ]
    }
  },

  "shared_commons_left_writeable": {
    "description": "Paths every workspace can write. Covered by global allow on workspaces dir; NOT included in any workspace's deny lists. All cross-workspace coordination flows through these.",
    "paths": [
      "<other workspace>/.routed-tasks/inbox/<filename>.json (NEW file creation via Bash/Python -- subprocess writes bypass Edit deny)",
      "<other workspace>/.lifecycle-reviews/inbox/<filename>.json (same)",
      "<Skill Hub>/.work-requests/inbox/<filename>.json (via work-request.py)",
      "<own workspace>/HUMAN-ACTION-REQUIRED.md (own-workspace direct Edit)",
      "<other workspace>/HUMAN-ACTION-REQUIRED.md (cross-workspace via notify-human-action.py Bash subprocess)",
      "~/.claude/lessons-learned.md (all session-end appends, direct Edit allowed)",
      "~/.claude/docs/plans-registry.md (all plan lifecycle updates, direct Edit allowed)",
      "~/.claude/.tmp/ (caches, manifests, logs)"
    ]
  },

  "emergency_override_procedure": "See ~/.claude/docs/permissions-emergency-override.md"
}
```

- [ ] **Step 2: Validate JSON syntax**

Run:
```bash
python -c "import json; d = json.load(open('/c/Users/Sharkitect Digital/.claude/config/workspace-permissions-templates.json')); print('Valid JSON,', len(d['workspaces']), 'workspaces,', len(d['global_permissions']['allow_additions']), 'global allow,', len(d['global_permissions']['deny_additions']), 'global deny')"
```

Expected: `Valid JSON, 3 workspaces, 15 global allow, 7 global deny`

- [ ] **Step 3: Sync to toolkit + commit**

Run:
```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py --sync
cd sharkitect-claude-toolkit
git add config/workspace-permissions-templates.json
git commit -m "Add workspace-permissions-templates.json source-of-truth (Phase 1 plan A2)"
git push
```

Expected: file mirrored to `toolkit/config/`, committed, pushed.

---

### Task A3: Lock in close-state vocabulary in universal-protocols.md

**Files:**
- Modify: `~/.claude/rules/universal-protocols.md` (Status Vocabulary Layers section)

- [ ] **Step 1: Locate the Status Vocabulary Layers section**

Run:
```bash
grep -n "Status Vocabulary Layers" ~/.claude/rules/universal-protocols.md
```

Expected: one match around line 290.

- [ ] **Step 2: Update the close-inbox-item.py output row**

Find the row beginning `| **close-inbox-item.py output** |` and replace with:

```
| **close-inbox-item.py output** | Close-only: `completed | rejected | superseded | duplicate | withdrawn`. Legacy `processed | resolved` accepted but auto-converted to `completed` with deprecation warning. Rejects all open-state values at close. | All workspaces closing inbox items |
```

- [ ] **Step 3: Update the local JSON inbox files row**

Find the row beginning `| **Local JSON inbox files**` and replace with:

```
| **Local JSON inbox files** (`.work-requests/inbox/*.json`, `.routed-tasks/inbox/*.json`, etc.) | Open states: `new`, `pending`, `in_progress`, `deferred`, `blocked`. Close states: `completed`, `rejected`, `superseded`, `duplicate`, `withdrawn`. (Legacy historical files may show `processed | resolved` -- read-only history, not used for new closes.) | AI agents writing inbox JSON directly |
```

- [ ] **Step 4: Update the Supabase row**

Find the row beginning `| **Supabase` and replace with:

```
| **Supabase `cross_workspace_requests.inbox_items_status_check`** | `pending | in_progress | deferred | blocked | completed | superseded | duplicate | rejected | withdrawn`. (Does NOT accept `new` or `processed`. `withdrawn` requires Sentinel migration -- routed task filed in plan Phase G.) | Supabase inserts/updates from any workspace |
```

- [ ] **Step 5: Verify all 3 edits landed**

Run:
```bash
grep "withdrawn" ~/.claude/rules/universal-protocols.md | head -10
```

Expected: at least 3 matches (one per row).

- [ ] **Step 6: Sync + commit**

Run:
```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py --sync
cd sharkitect-claude-toolkit
git add rules/universal-protocols.md
git commit -m "Status Vocabulary Layers: consolidate to 5-state close vocab + add withdrawn (plan A3)"
git push
```

Expected: rule synced to toolkit + pushed.

---

## Phase B — Build inbox-amend.py (TDD, ~2.5 hours) **[COMPLETE 2026-04-28 — 24/24 tests pass]**

### Task B1: Write failing tests for inbox-amend.py

**Files:**
- Create: `~/.claude/tests/test_inbox_amend.py`

- [ ] **Step 1: Write the test scaffold with all 13 mode tests**

Write `~/.claude/tests/test_inbox_amend.py`:

```python
"""Tests for inbox-amend.py: source-side inbox item amendment CLI.

Verifies all 13 amendment modes plus invariants:
- source identity matches item's source_workspace
- status guard (only amendable in new/pending/deferred)
- append-only source_amendments[] history
- atomic write via tempfile + os.replace
- auto-close on supersede/duplicate/withdraw via close-inbox-item.py call
- idempotency: same amendment_id replayed = no-op
- forward-compat schema slots reserved
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path.home() / ".claude" / "scripts" / "inbox-amend.py"


def _wr_fixture(tmp_path: Path, source: str = "workforce-hq", status: str = "pending") -> Path:
    """Create a minimal valid WR JSON in a tempdir simulating an inbox."""
    wr = {
        "id": "wr-hq-2026-04-28-001",
        "id_format_version": 2,
        "source_workspace": source,
        "request_type": "ENHANCE",
        "task_description": "test fixture",
        "severity": "warning",
        "priority": "medium",
        "status": status,
        "components": ["foo.py"],
        "source_amendments": []
    }
    p = tmp_path / "wr-hq-2026-04-28-001.json"
    p.write_text(json.dumps(wr, indent=2), encoding="utf-8")
    return p


def _rt_fixture(tmp_path: Path, source: str = "workforce-hq", target: str = "skill-management-hub", status: str = "pending") -> Path:
    """Create a minimal valid routed-task JSON for generic-amendment tests."""
    rt = {
        "id": "rt-2026-04-28-test",
        "id_format_version": 2,
        "routed_from": source,
        "routed_to": target,
        "source_workspace": source,
        "task_summary": "test fixture",
        "status": status,
        "source_amendments": []
    }
    p = tmp_path / "rt-2026-04-28-test.json"
    p.write_text(json.dumps(rt, indent=2), encoding="utf-8")
    return p


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8"
    )


# ----- Sanity tests -----

def test_help_exits_zero():
    """Sanity: --help works and exits 0."""
    r = _run(["--help"])
    assert r.returncode == 0
    out = (r.stdout + r.stderr).lower()
    assert "amend" in out


# ----- Mode 1: add-context -----

def test_add_context_appends_amendment(tmp_path: Path):
    """add-context appends an amendment event without mutating original fields."""
    f = _wr_fixture(tmp_path)
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "discovered additional context",
        "--note", "this is the new context"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert len(data["source_amendments"]) == 1
    a = data["source_amendments"][0]
    assert a["amendment_type"] == "add_context"
    assert a["actor"] == "workforce-hq"
    assert a["actor_type"] == "workspace"
    assert a["reason"] == "discovered additional context"
    assert a["notes"] == "this is the new context"
    # Forward-compat slots reserved (nullable)
    assert "condition" in a
    assert "template_id" in a
    assert "expires_at" in a
    assert "parent_etag" in a
    assert "triggers" in a
    # Original fields untouched
    assert data["task_description"] == "test fixture"
    assert data["severity"] == "warning"


# ----- Source identity validation -----

def test_source_mismatch_rejected(tmp_path: Path):
    """If --from workspace doesn't match source_workspace, reject."""
    f = _wr_fixture(tmp_path, source="workforce-hq")
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "sentinel",
        "--reason", "should be rejected",
        "--note", "should not write"
    ])
    assert r.returncode != 0
    assert "source" in r.stderr.lower()
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["source_amendments"] == []


def test_source_match_via_routed_from(tmp_path: Path):
    """For routed-tasks, source identity comes from routed_from field."""
    f = _rt_fixture(tmp_path, source="workforce-hq")
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "amend my routed task",
        "--note", "additional context"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"


# ----- Status guard -----

def test_in_progress_status_rejects_amendment(tmp_path: Path):
    """status=in_progress means target started; source amendments locked."""
    f = _wr_fixture(tmp_path, status="in_progress")
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "too late to amend",
        "--note", "should not write"
    ])
    assert r.returncode != 0
    err = r.stderr.lower()
    assert "in_progress" in err or "locked" in err


def test_completed_status_rejects_amendment(tmp_path: Path):
    """closed items can't be amended."""
    f = _wr_fixture(tmp_path, status="completed")
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "too late",
        "--note", "should not write"
    ])
    assert r.returncode != 0


# ----- Mode 2: severity-update -----

def test_severity_update_records_from_to(tmp_path: Path):
    """severity-update logs from/to and updates top-level field."""
    f = _wr_fixture(tmp_path)
    r = _run([
        "severity-update",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "blocking revenue work now",
        "--new-severity", "critical"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    a = data["source_amendments"][0]
    assert a["amendment_type"] == "severity_update"
    assert a["fields_changed"]["severity"] == {"from": "warning", "to": "critical"}
    assert data["severity"] == "critical"


# ----- Mode 3: priority-update -----

def test_priority_update_records_from_to(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "priority-update",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "blocked by Q2 deadline shift",
        "--new-priority", "high"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    a = data["source_amendments"][0]
    assert a["amendment_type"] == "priority_update"
    assert a["fields_changed"]["priority"] == {"from": "medium", "to": "high"}
    assert data["priority"] == "high"


# ----- Mode 4 + 5: component-add / component-remove -----

def test_component_add_appends(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "component-add",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "discovered these are also relevant",
        "--components", "bar.py,baz.py"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["components"] == ["foo.py", "bar.py", "baz.py"]
    assert data["source_amendments"][0]["amendment_type"] == "component_add"


def test_component_remove_drops(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "component-remove",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "foo.py turned out to be unrelated",
        "--components", "foo.py"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["components"] == []


# ----- Mode 6: add-evidence -----

def test_add_evidence_appends_to_evidence_array(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "add-evidence",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "found the error log",
        "--evidence-type", "log",
        "--evidence-ref", "/tmp/error.log",
        "--note", "stack trace at line 42"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert len(data["evidence"]) == 1
    assert data["evidence"][0]["type"] == "log"
    assert data["evidence"][0]["ref"] == "/tmp/error.log"


# ----- Mode 7: link-related -----

def test_link_related_appends_cross_reference(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "link-related",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "this depends on completing the other WR",
        "--link-type", "depends_on",
        "--link-id", "wr-hq-2026-04-25-001"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["related_items"][0] == {"type": "depends_on", "id": "wr-hq-2026-04-25-001"}


# ----- Mode 8: reclassify -----

def test_reclassify_updates_request_type(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "reclassify",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "investigation showed this is a bug not enhancement",
        "--new-type", "BUG"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["request_type"] == "BUG"


# ----- Mode 9: supersede -----

def test_supersede_requires_supersedes_id(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "supersede",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "filed broader scope as new WR"
    ])
    assert r.returncode != 0
    assert "supersedes" in r.stderr.lower()


def test_supersede_records_reference(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "supersede",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "filed broader scope at wr-hq-2026-04-29-001",
        "--supersedes", "wr-hq-2026-04-29-001",
        "--close-script-stub", str(tmp_path / "close-args.json")
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    a = data["source_amendments"][0]
    assert a["supersedes"] == "wr-hq-2026-04-29-001"
    # Auto-close was invoked
    args = json.loads((tmp_path / "close-args.json").read_text())
    assert "--status" in args["argv"]
    assert "superseded" in args["argv"]


# ----- Mode 10: duplicate -----

def test_duplicate_records_reference(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "duplicate",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "found existing wr that covers this",
        "--duplicate-of", "wr-hq-2026-04-26-005",
        "--close-script-stub", str(tmp_path / "close-args.json")
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["source_amendments"][0]["duplicate_of"] == "wr-hq-2026-04-26-005"


# ----- Mode 11: withdraw -----

def test_withdraw_closes_with_withdrawn_status(tmp_path: Path):
    """withdraw mode auto-calls close-inbox-item.py with --status withdrawn."""
    f = _wr_fixture(tmp_path)
    capture = tmp_path / "close-args.json"
    r = _run([
        "withdraw",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "filed in error -- shouldn't have been created",
        "--close-script-stub", str(capture)
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    args = json.loads(capture.read_text(encoding="utf-8"))
    assert "--status" in args["argv"]
    assert "withdrawn" in args["argv"]
    # Notification reason is included in the auto-close
    idx = args["argv"].index("--what-was-done")
    assert "filed in error" in args["argv"][idx + 1].lower() or "shouldn't" in args["argv"][idx + 1].lower()


# ----- Mode 12: reroute -----

def test_reroute_moves_file_and_updates_routed_to(tmp_path: Path):
    """reroute moves the JSON to new target's inbox and updates routed_to."""
    src_inbox = tmp_path / "src-ws" / ".routed-tasks" / "inbox"
    new_target_inbox = tmp_path / "new-target-ws" / ".routed-tasks" / "inbox"
    src_inbox.mkdir(parents=True); new_target_inbox.mkdir(parents=True)

    rt = {
        "id": "rt-2026-04-28-test",
        "id_format_version": 2,
        "routed_from": "workforce-hq",
        "routed_to": "skill-management-hub",
        "source_workspace": "workforce-hq",
        "task_summary": "test reroute",
        "status": "pending",
        "source_amendments": []
    }
    src_file = src_inbox / "rt-2026-04-28-test.json"
    src_file.write_text(json.dumps(rt, indent=2), encoding="utf-8")

    r = _run([
        "reroute",
        "--file", str(src_file),
        "--from", "workforce-hq",
        "--reason", "wrong target -- should have gone to sentinel",
        "--new-target", "sentinel",
        "--new-target-inbox-dir", str(new_target_inbox)
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert not src_file.exists()
    moved = new_target_inbox / "rt-2026-04-28-test.json"
    assert moved.exists()
    data = json.loads(moved.read_text(encoding="utf-8"))
    assert data["routed_to"] == "sentinel"
    assert any(a["amendment_type"] == "reroute" for a in data["source_amendments"])
    assert data["routed_to_history"][-1]["from"] == "skill-management-hub"
    assert data["routed_to_history"][-1]["to"] == "sentinel"


def test_reroute_aborts_on_collision(tmp_path: Path):
    """If destination filename already exists, reroute aborts (no overwrite)."""
    src_inbox = tmp_path / "src" / ".routed-tasks" / "inbox"
    dst_inbox = tmp_path / "dst" / ".routed-tasks" / "inbox"
    src_inbox.mkdir(parents=True); dst_inbox.mkdir(parents=True)

    rt = {"id": "rt-test", "id_format_version": 2, "routed_from": "workforce-hq",
          "routed_to": "skill-management-hub", "source_workspace": "workforce-hq",
          "status": "pending", "source_amendments": []}
    src = src_inbox / "rt-test.json"
    src.write_text(json.dumps(rt), encoding="utf-8")
    # Pre-place a colliding file at destination
    (dst_inbox / "rt-test.json").write_text("{}", encoding="utf-8")

    r = _run([
        "reroute",
        "--file", str(src),
        "--from", "workforce-hq",
        "--reason", "collision should abort",
        "--new-target", "sentinel",
        "--new-target-inbox-dir", str(dst_inbox)
    ])
    assert r.returncode != 0
    assert "collision" in r.stderr.lower() or "exists" in r.stderr.lower()
    # Source file untouched
    assert src.exists()


# ----- Mode 13: retract-amendment -----

def test_retract_amendment_marks_original(tmp_path: Path):
    """retract appends new event referencing retracted amendment_id; original flagged."""
    f = _wr_fixture(tmp_path)
    r1 = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "first amendment",
        "--note", "to be retracted",
        "--amendment-id", "amend-test-001"
    ])
    assert r1.returncode == 0

    r2 = _run([
        "retract-amendment",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "made in error -- retracting",
        "--retracts-amendment", "amend-test-001"
    ])
    assert r2.returncode == 0
    data = json.loads(f.read_text(encoding="utf-8"))
    assert len(data["source_amendments"]) == 2
    retract_event = data["source_amendments"][1]
    assert retract_event["amendment_type"] == "retract_amendment"
    assert retract_event["retracts_amendment"] == "amend-test-001"
    # Original flagged retracted
    orig = data["source_amendments"][0]
    assert orig["retracted"] is True
    assert orig["retracted_at"] is not None
    assert orig["retracted_by_amendment_id"] is not None


# ----- bulk-amend -----

def test_bulk_amend_applies_to_all(tmp_path: Path):
    """bulk-amend mode applies same amendment to multiple files."""
    f1 = _wr_fixture(tmp_path)
    data = json.loads(f1.read_text(encoding="utf-8"))
    data["id"] = "wr-hq-2026-04-28-002"
    f2 = tmp_path / "wr-hq-2026-04-28-002.json"
    f2.write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run([
        "bulk-amend",
        "--files", f"{f1},{f2}",
        "--from", "workforce-hq",
        "--reason", "blocked by external dep",
        "--mode", "add-context",
        "--note", "shared context across all WRs"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    for fp in [f1, f2]:
        d = json.loads(fp.read_text(encoding="utf-8"))
        assert len(d["source_amendments"]) == 1
        assert d["source_amendments"][0]["notes"] == "shared context across all WRs"


def test_bulk_amend_continue_on_failure(tmp_path: Path):
    """bulk-amend continues past failures, returns nonzero if any failed."""
    f1 = _wr_fixture(tmp_path, status="pending")
    data = json.loads(f1.read_text(encoding="utf-8"))
    data["id"] = "wr-hq-2026-04-28-002"
    data["status"] = "in_progress"  # this one will fail status guard
    f2 = tmp_path / "wr-hq-2026-04-28-002.json"
    f2.write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run([
        "bulk-amend",
        "--files", f"{f1},{f2}",
        "--from", "workforce-hq",
        "--reason", "test partial failure",
        "--mode", "add-context",
        "--note", "should land on f1, fail on f2"
    ])
    assert r.returncode != 0  # nonzero because at least one failed
    # f1 succeeded
    d1 = json.loads(f1.read_text(encoding="utf-8"))
    assert len(d1["source_amendments"]) == 1
    # f2 untouched (status guard rejected)
    d2 = json.loads(f2.read_text(encoding="utf-8"))
    assert len(d2["source_amendments"]) == 0


# ----- Idempotency -----

def test_idempotent_same_amendment_id(tmp_path: Path):
    """Applying same amendment_id twice is a no-op."""
    f = _wr_fixture(tmp_path)
    r1 = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "first apply",
        "--note", "the note",
        "--amendment-id", "amend-test-001"
    ])
    assert r1.returncode == 0
    r2 = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "second apply (should no-op)",
        "--note", "different note",
        "--amendment-id", "amend-test-001"
    ])
    assert r2.returncode == 0
    data = json.loads(f.read_text(encoding="utf-8"))
    assert len(data["source_amendments"]) == 1


# ----- Validation: short reason -----

def test_short_reason_rejected(tmp_path: Path):
    """Reason must be >= 10 chars."""
    f = _wr_fixture(tmp_path)
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "too short",  # 9 chars
        "--note", "should fail"
    ])
    assert r.returncode != 0
```

- [ ] **Step 2: Run tests, verify all fail (script doesn't exist yet)**

Run:
```bash
python -m pytest ~/.claude/tests/test_inbox_amend.py -v 2>&1 | tail -30
```

Expected: ALL tests fail with FileNotFoundError or similar (`inbox-amend.py` doesn't exist).

- [ ] **Step 3: Sync + commit failing tests**

Run:
```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py --sync
cd sharkitect-claude-toolkit
git add tests/test_inbox_amend.py
git commit -m "Add failing tests for inbox-amend.py (TDD: tests first, plan B1)"
git push
```

Expected: tests committed.

---

### Task B2: Implement inbox-amend.py

**Files:**
- Create: `~/.claude/scripts/inbox-amend.py`

- [ ] **Step 1: Write the script**

Write `~/.claude/scripts/inbox-amend.py`:

```python
#!/usr/bin/env python
"""inbox-amend.py -- Generic source-side inbox item amendment CLI.

Applies to work-request, routed-task, and lifecycle-review JSON files
in inbox/ directories. Source workspace amends own filed items via this
CLI; direct Edit on cross-workspace inbox files is denied by the
permissions system. The CLI enforces source identity, status guard
(locked once target sets in_progress or any close state), and
append-only history in the source_amendments[] array.

Modes (13 total):
  add-context, severity-update, priority-update, component-add,
  component-remove, add-evidence, link-related, reclassify, supersede,
  duplicate, withdraw, reroute, retract-amendment, bulk-amend.

Schema (each amendment is appended to source_amendments[]):
  See spec at <Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md.

Pure stdlib. Atomic write via tempfile + os.replace.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path


CANONICAL_WORKSPACES = ("workforce-hq", "skill-management-hub", "sentinel")
AMENDABLE_STATUSES = {"new", "pending", "deferred"}
CLOSE_INBOX_SCRIPT = Path.home() / ".claude" / "scripts" / "close-inbox-item.py"
AUTO_CLOSE_MAP = {
    "supersede": "superseded",
    "duplicate": "duplicate",
    "withdraw": "withdrawn"
}


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _gen_amendment_id() -> str:
    today = dt.date.today().isoformat()
    return f"amend-{today}-{uuid.uuid4().hex[:8]}"


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _atomic_write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=p.name + ".", suffix=".tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, p)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _validate_source(item: dict, claimed_from: str) -> tuple[bool, str]:
    if claimed_from not in CANONICAL_WORKSPACES:
        return False, f"--from must be one of {CANONICAL_WORKSPACES}; got {claimed_from!r}"
    actual = item.get("source_workspace") or item.get("routed_from")
    if not actual:
        return False, "Item has neither source_workspace nor routed_from -- cannot validate identity"
    if actual != claimed_from:
        return False, (
            f"Source mismatch: --from={claimed_from!r} but item.source_workspace={actual!r}. "
            "Only the originating workspace may amend its own filed items. "
            "Cross-workspace coordination uses routed-tasks instead."
        )
    return True, ""


def _validate_status_guard(item: dict) -> tuple[bool, str]:
    s = item.get("status", "new")
    if s in AMENDABLE_STATUSES:
        return True, ""
    return False, (
        f"Item status={s!r} is locked -- source amendments only allowed in "
        f"{sorted(AMENDABLE_STATUSES)}. Once target sets in_progress or "
        "closes, source must coordinate via routed-task."
    )


def _is_idempotent_replay(item: dict, amendment_id: str) -> bool:
    return any(
        a.get("amendment_id") == amendment_id
        for a in item.get("source_amendments", [])
    )


def _build_event(args, mode: str, fields_changed: dict | None = None,
                 structured_data: dict | None = None) -> dict:
    """Build amendment event with full forward-compat schema."""
    return {
        "amendment_id": args.amendment_id or _gen_amendment_id(),
        "timestamp": _now_iso(),
        "actor": args.from_,
        "actor_type": "workspace",
        "amendment_type": mode,
        "reason": args.reason,
        "fields_changed": fields_changed or {},
        "structured_data": structured_data or {},
        "notes": getattr(args, "note", None) or "",
        "supersedes": getattr(args, "supersedes", None),
        "duplicate_of": getattr(args, "duplicate_of", None),
        "retracts_amendment": getattr(args, "retracts_amendment", None),
        "retracted": False,
        "retracted_at": None,
        "retracted_by_amendment_id": None,
        # Forward-compat slots
        "condition": None,
        "template_id": None,
        "expires_at": None,
        "parent_etag": None,
        "triggers": []
    }


def _apply_event(item: dict, event: dict, top_level_updates: dict | None = None) -> None:
    item.setdefault("source_amendments", []).append(event)
    if top_level_updates:
        for k, v in top_level_updates.items():
            item[k] = v


def _maybe_auto_close(args, item: dict, event: dict, mode: str) -> None:
    """Call close-inbox-item.py for supersede/duplicate/withdraw."""
    close_status = AUTO_CLOSE_MAP.get(mode)
    if not close_status:
        return
    ref_arg = []
    if mode == "supersede":
        ref_arg = ["--superseded-by", args.supersedes]
    elif mode == "duplicate":
        ref_arg = ["--duplicate-of", args.duplicate_of]

    what_was_done = f"Source amendment ({mode}): {args.reason}"
    argv = [
        sys.executable, str(CLOSE_INBOX_SCRIPT),
        "--file", str(args.file),
        "--status", close_status,
        "--resolved-by", args.from_,
        "--what-was-done", what_was_done,
    ] + ref_arg

    if getattr(args, "close_script_stub", None):
        Path(args.close_script_stub).write_text(
            json.dumps({"argv": argv}), encoding="utf-8"
        )
        return
    subprocess.run(argv, check=True)


# ===== Mode handlers =====

def cmd_add_context(args, item: dict) -> dict:
    event = _build_event(args, "add_context")
    _apply_event(item, event)
    return event


def cmd_severity_update(args, item: dict) -> dict:
    old = item.get("severity")
    event = _build_event(args, "severity_update",
                         fields_changed={"severity": {"from": old, "to": args.new_severity}})
    _apply_event(item, event, top_level_updates={"severity": args.new_severity})
    return event


def cmd_priority_update(args, item: dict) -> dict:
    old = item.get("priority")
    event = _build_event(args, "priority_update",
                         fields_changed={"priority": {"from": old, "to": args.new_priority}})
    _apply_event(item, event, top_level_updates={"priority": args.new_priority})
    return event


def cmd_component_add(args, item: dict) -> dict:
    components = list(item.get("components", []))
    incoming = [c.strip() for c in args.components.split(",") if c.strip()]
    new = [c for c in incoming if c not in components]
    components.extend(new)
    event = _build_event(args, "component_add",
                         fields_changed={"components": {"from": item.get("components", []), "to": components}},
                         structured_data={"components_added": new})
    _apply_event(item, event, top_level_updates={"components": components})
    return event


def cmd_component_remove(args, item: dict) -> dict:
    to_remove = {c.strip() for c in args.components.split(",") if c.strip()}
    components = [c for c in item.get("components", []) if c not in to_remove]
    event = _build_event(args, "component_remove",
                         fields_changed={"components": {"from": item.get("components", []), "to": components}},
                         structured_data={"components_removed": list(to_remove)})
    _apply_event(item, event, top_level_updates={"components": components})
    return event


def cmd_add_evidence(args, item: dict) -> dict:
    entry = {"type": args.evidence_type, "ref": args.evidence_ref, "note": args.note or ""}
    event = _build_event(args, "add_evidence", structured_data={"evidence": [entry]})
    item.setdefault("evidence", []).append(entry)
    _apply_event(item, event)
    return event


def cmd_link_related(args, item: dict) -> dict:
    link = {"type": args.link_type, "id": args.link_id}
    event = _build_event(args, "link_related", structured_data={"related_items": [link]})
    item.setdefault("related_items", []).append(link)
    _apply_event(item, event)
    return event


def cmd_reclassify(args, item: dict) -> dict:
    old = item.get("request_type")
    event = _build_event(args, "reclassify",
                         fields_changed={"request_type": {"from": old, "to": args.new_type}})
    _apply_event(item, event, top_level_updates={"request_type": args.new_type})
    return event


def cmd_supersede(args, item: dict) -> dict:
    if not args.supersedes:
        raise SystemExit("supersede mode requires --supersedes <new-id>")
    event = _build_event(args, "supersede")
    _apply_event(item, event)
    return event


def cmd_duplicate(args, item: dict) -> dict:
    if not args.duplicate_of:
        raise SystemExit("duplicate mode requires --duplicate-of <surviving-id>")
    event = _build_event(args, "duplicate")
    _apply_event(item, event)
    return event


def cmd_withdraw(args, item: dict) -> dict:
    event = _build_event(args, "withdraw")
    _apply_event(item, event)
    return event


def cmd_reroute(args, item: dict) -> dict:
    new_target = args.new_target
    new_target_dir = Path(args.new_target_inbox_dir).resolve()
    if not new_target_dir.exists():
        raise SystemExit(f"new-target-inbox-dir does not exist: {new_target_dir}")

    # Collision check: abort if destination filename already taken
    new_path = new_target_dir / Path(args.file).name
    if new_path.exists():
        raise SystemExit(
            f"Reroute collision: destination already exists at {new_path}. "
            "Aborting to prevent overwrite. Rename source or choose different "
            "destination."
        )

    old_target = item.get("routed_to")
    history = list(item.get("routed_to_history", []))
    history.append({
        "from": old_target,
        "to": new_target,
        "timestamp": _now_iso(),
        "reason": args.reason
    })
    event = _build_event(args, "reroute",
                         fields_changed={"routed_to": {"from": old_target, "to": new_target}})
    item["routed_to"] = new_target
    item["routed_to_history"] = history
    _apply_event(item, event)
    # Move file
    _atomic_write_json(new_path, item)
    Path(args.file).unlink()
    args.file = new_path
    return event


def cmd_retract_amendment(args, item: dict) -> dict:
    if not args.retracts_amendment:
        raise SystemExit("retract-amendment mode requires --retracts-amendment <amendment-id>")
    found = False
    new_id = args.amendment_id or _gen_amendment_id()
    for a in item.get("source_amendments", []):
        if a.get("amendment_id") == args.retracts_amendment:
            a["retracted"] = True
            a["retracted_at"] = _now_iso()
            a["retracted_by_amendment_id"] = new_id
            found = True
            break
    if not found:
        raise SystemExit(
            f"No amendment with id {args.retracts_amendment!r} found in source_amendments[]"
        )
    args.amendment_id = new_id
    event = _build_event(args, "retract_amendment")
    _apply_event(item, event)
    return event


def cmd_bulk_amend(args) -> int:
    """Apply same amendment across multiple files via subordinate process calls."""
    files = [Path(f.strip()) for f in args.files.split(",") if f.strip()]
    if not files:
        raise SystemExit("bulk-amend requires --files <comma-separated paths>")
    failures = []
    for f in files:
        sub_argv = [
            sys.executable, str(Path(__file__).resolve()),
            args.mode,
            "--file", str(f),
            "--from", args.from_,
            "--reason", args.reason
        ]
        if args.note:
            sub_argv += ["--note", args.note]
        proc = subprocess.run(sub_argv, capture_output=True, text=True)
        if proc.returncode != 0:
            failures.append((f, proc.returncode, proc.stderr))
    if failures:
        print(f"BULK-AMEND PARTIAL FAILURE: {len(failures)} of {len(files)} file(s) failed:",
              file=sys.stderr)
        for f, code, err in failures:
            print(f"  {f}: rc={code} stderr={err.strip()[:200]}", file=sys.stderr)
        return 1
    print(f"BULK-AMEND OK: {len(files)} files updated")
    return 0


# ===== Argparse =====

def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--from", dest="from_", required=True, choices=CANONICAL_WORKSPACES)
    p.add_argument("--reason", required=True, help=">= 10 char human-readable explanation")
    p.add_argument("--note", default=None)
    p.add_argument("--amendment-id", default=None)
    p.add_argument("--close-script-stub", default=None, help=argparse.SUPPRESS)


def main() -> int:
    parser = argparse.ArgumentParser(prog="inbox-amend.py")
    sub = parser.add_subparsers(dest="mode", required=True)

    p = sub.add_parser("add-context"); _add_common_args(p)

    p = sub.add_parser("severity-update"); _add_common_args(p)
    p.add_argument("--new-severity", required=True, choices=("info", "warning", "high", "critical"))

    p = sub.add_parser("priority-update"); _add_common_args(p)
    p.add_argument("--new-priority", required=True, choices=("low", "medium", "high", "critical"))

    p = sub.add_parser("component-add"); _add_common_args(p)
    p.add_argument("--components", required=True)

    p = sub.add_parser("component-remove"); _add_common_args(p)
    p.add_argument("--components", required=True)

    p = sub.add_parser("add-evidence"); _add_common_args(p)
    p.add_argument("--evidence-type", required=True, choices=("log", "screenshot", "trace", "url", "file"))
    p.add_argument("--evidence-ref", required=True)

    p = sub.add_parser("link-related"); _add_common_args(p)
    p.add_argument("--link-type", required=True, choices=("blocks", "blocked_by", "related", "depends_on"))
    p.add_argument("--link-id", required=True)

    p = sub.add_parser("reclassify"); _add_common_args(p)
    p.add_argument("--new-type", required=True,
                   choices=("MISSING", "UNUSED", "FALLBACK", "TASK", "BUG", "ENHANCE"))

    p = sub.add_parser("supersede"); _add_common_args(p)
    p.add_argument("--supersedes", required=True)

    p = sub.add_parser("duplicate"); _add_common_args(p)
    p.add_argument("--duplicate-of", required=True)

    p = sub.add_parser("withdraw"); _add_common_args(p)

    p = sub.add_parser("reroute"); _add_common_args(p)
    p.add_argument("--new-target", required=True, choices=CANONICAL_WORKSPACES)
    p.add_argument("--new-target-inbox-dir", required=True)

    p = sub.add_parser("retract-amendment"); _add_common_args(p)
    p.add_argument("--retracts-amendment", required=True)

    p = sub.add_parser("bulk-amend")
    p.add_argument("--files", required=True)
    p.add_argument("--from", dest="from_", required=True, choices=CANONICAL_WORKSPACES)
    p.add_argument("--reason", required=True)
    p.add_argument("--mode", required=True)
    p.add_argument("--note", default=None)

    args = parser.parse_args()

    if args.mode == "bulk-amend":
        return cmd_bulk_amend(args)

    if len(args.reason) < 10:
        print(f"--reason must be >= 10 chars (got {len(args.reason)})", file=sys.stderr)
        return 2

    item = _read_json(args.file)

    ok, err = _validate_source(item, args.from_)
    if not ok:
        print(err, file=sys.stderr)
        return 3

    ok, err = _validate_status_guard(item)
    if not ok:
        print(err, file=sys.stderr)
        return 4

    if not args.amendment_id:
        args.amendment_id = _gen_amendment_id()

    if _is_idempotent_replay(item, args.amendment_id):
        print(f"Idempotent replay: amendment_id {args.amendment_id} already present, no-op",
              file=sys.stderr)
        return 0

    handler = {
        "add-context": cmd_add_context,
        "severity-update": cmd_severity_update,
        "priority-update": cmd_priority_update,
        "component-add": cmd_component_add,
        "component-remove": cmd_component_remove,
        "add-evidence": cmd_add_evidence,
        "link-related": cmd_link_related,
        "reclassify": cmd_reclassify,
        "supersede": cmd_supersede,
        "duplicate": cmd_duplicate,
        "withdraw": cmd_withdraw,
        "reroute": cmd_reroute,
        "retract-amendment": cmd_retract_amendment,
    }[args.mode]

    event = handler(args, item)

    # For non-reroute modes, write the file. (reroute already wrote during move.)
    if args.mode != "reroute":
        _atomic_write_json(args.file, item)

    auto_close_key = {"supersede": "supersede", "duplicate": "duplicate", "withdraw": "withdraw"}.get(args.mode)
    if auto_close_key:
        _maybe_auto_close(args, item, event, auto_close_key)

    print(f"OK: {args.mode} amendment {event['amendment_id']} applied to {args.file}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
```

- [ ] **Step 2: Run all inbox-amend tests, verify pass**

Run:
```bash
python -m pytest ~/.claude/tests/test_inbox_amend.py -v 2>&1 | tail -50
```

Expected: ALL 25+ tests PASS. If any fail, fix in inbox-amend.py until green. Do not commit until all pass.

- [ ] **Step 3: Sync + commit**

Run:
```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py --sync
cd sharkitect-claude-toolkit
git add scripts/inbox-amend.py tests/test_inbox_amend.py
git commit -m "Implement inbox-amend.py + 25 tests passing (plan B2)"
git push
```

---

## Phase C — Extend close-inbox-item.py (~1 hour)

### Task C1: Add `withdrawn` status + auto-deprecate processed/resolved

**Files:**
- Modify: `~/.claude/scripts/close-inbox-item.py`

- [ ] **Step 1: Locate status choices in argparse**

Run:
```bash
grep -n "choices=\[\"completed\"\|choices=(\"completed\"" ~/.claude/scripts/close-inbox-item.py | head -5
```

Note line number.

- [ ] **Step 2: Add `withdrawn` to choices**

Find the line with `"choices=\[\"completed\", \"duplicate\"...`. Replace the array to add `"withdrawn"`:

OLD:
```python
choices=["completed", "duplicate", "processed", "rejected", "resolved", "superseded"]
```

NEW:
```python
choices=["completed", "duplicate", "processed", "rejected", "resolved", "superseded", "withdrawn"]
```

- [ ] **Step 3: Add deprecation warning + auto-conversion for processed/resolved**

After argparse parses (find `args = parser.parse_args()`), insert:

```python
if args.status in ("processed", "resolved"):
    print(
        f"DEPRECATION: --status {args.status!r} auto-converted to 'completed'. "
        "Per the 2026-04-28 close-state vocabulary consolidation, only "
        "'completed' is used for target-controlled close-as-done. See "
        "~/.claude/rules/universal-protocols.md Status Vocabulary Layers.",
        file=sys.stderr
    )
    args.status = "completed"
```

- [ ] **Step 4: Update Supabase status normalization**

Find the line near 116 with `sb_status = 'completed' if status in {'processed', 'completed', 'resolved'}`. Replace with:

```python
if status in ('processed', 'completed', 'resolved'):
    sb_status = 'completed'
elif status == 'withdrawn':
    sb_status = 'withdrawn'  # NOTE: requires Sentinel migration on cross_workspace_requests CHECK constraint (plan Phase G)
elif status == 'superseded':
    sb_status = 'superseded'
elif status == 'duplicate':
    sb_status = 'duplicate'
else:
    sb_status = 'rejected'
```

---

### Task C2: Add `--annotate` mode

**Files:**
- Modify: `~/.claude/scripts/close-inbox-item.py`

- [ ] **Step 1: Add --annotate flag to argparse**

Find the argparse parser. Add:

```python
parser.add_argument("--annotate", action="store_true",
                    help="Append a status_history entry without closing the item. "
                         "Status stays unchanged; file stays in inbox/. Used by "
                         "target workspace to track in-flight progress.")
```

- [ ] **Step 2: Add annotate branch early in main**

After argparse parses + the deprecation check, before main close logic:

```python
if args.annotate:
    import datetime as _dt
    from pathlib import Path as _Path
    item_path = _Path(args.file)
    item = json.loads(item_path.read_text(encoding="utf-8"))
    note_entry = {
        "status": item.get("status", "pending"),
        "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "actor": args.resolved_by,
        "note": args.what_was_done,
        "kind": "annotation"
    }
    item.setdefault("status_history", []).append(note_entry)
    # Atomic write
    import tempfile as _tempfile, os as _os
    fd, tmp = _tempfile.mkstemp(prefix=item_path.name + ".", suffix=".tmp", dir=item_path.parent)
    try:
        with _os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)
        _os.replace(tmp, item_path)
    except Exception:
        if _os.path.exists(tmp):
            _os.unlink(tmp)
        raise
    print(f"OK: annotated {item_path.name} (status={item.get('status')}, kind=annotation)")
    return 0
```

---

### Task C3: Tests for C1 + C2

**Files:**
- Modify (or create): `~/.claude/tests/test_close_inbox_item.py`

- [ ] **Step 1: Check if test file exists**

Run:
```bash
ls ~/.claude/tests/test_close_inbox_item.py 2>&1
```

If exists, append the new tests. If not, create the file.

- [ ] **Step 2: Add tests for withdrawn + deprecation + annotate**

Append (or create file with) these tests:

```python
"""Additions for plan Phase C: withdrawn status, deprecation, annotate mode."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

CLOSE_SCRIPT = Path.home() / ".claude" / "scripts" / "close-inbox-item.py"


def _make_inbox_item(tmp_path: Path, source: str = "workforce-hq", status: str = "pending") -> Path:
    """Create a minimal inbox WR JSON for closure tests."""
    inbox = tmp_path / "inbox"
    inbox.mkdir(exist_ok=True)
    processed = tmp_path / "processed"
    processed.mkdir(exist_ok=True)
    wr = {
        "id": "wr-test-001",
        "id_format_version": 2,
        "source_workspace": source,
        "request_type": "ENHANCE",
        "task_description": "test fixture",
        "severity": "warning",
        "status": status,
        "notify_on_completion": False
    }
    p = inbox / "wr-test-001.json"
    p.write_text(json.dumps(wr, indent=2), encoding="utf-8")
    return p


def _run_close(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLOSE_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8"
    )


def test_status_withdrawn_accepted(tmp_path: Path):
    f = _make_inbox_item(tmp_path)
    r = _run_close([
        "--file", str(f),
        "--status", "withdrawn",
        "--resolved-by", "workforce-hq",
        "--what-was-done", "Source withdrew this WR after realizing it was filed in error",
        "--no-supabase",
        "--no-notify",
        "--no-notify-reason", "test-only"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    moved = tmp_path / "processed" / "wr-test-001.json"
    assert moved.exists()
    data = json.loads(moved.read_text())
    assert data["status"] == "withdrawn"


def test_processed_auto_converts_to_completed(tmp_path: Path):
    f = _make_inbox_item(tmp_path)
    r = _run_close([
        "--file", str(f),
        "--status", "processed",
        "--resolved-by", "skill-management-hub",
        "--what-was-done", "Work completed successfully via processed status",
        "--no-supabase",
        "--no-notify",
        "--no-notify-reason", "test-only"
    ])
    assert r.returncode == 0
    assert "DEPRECATION" in r.stderr
    moved = tmp_path / "processed" / "wr-test-001.json"
    data = json.loads(moved.read_text())
    assert data["status"] == "completed"


def test_resolved_auto_converts_to_completed(tmp_path: Path):
    f = _make_inbox_item(tmp_path)
    r = _run_close([
        "--file", str(f),
        "--status", "resolved",
        "--resolved-by", "skill-management-hub",
        "--what-was-done", "Issue is no longer active",
        "--no-supabase",
        "--no-notify",
        "--no-notify-reason", "test-only"
    ])
    assert r.returncode == 0
    assert "DEPRECATION" in r.stderr
    moved = tmp_path / "processed" / "wr-test-001.json"
    data = json.loads(moved.read_text())
    assert data["status"] == "completed"


def test_annotate_appends_without_closing(tmp_path: Path):
    f = _make_inbox_item(tmp_path, status="deferred")
    r = _run_close([
        "--file", str(f),
        "--resolved-by", "skill-management-hub",
        "--what-was-done", "Reviewed; deferring to focused session because X",
        "--annotate",
        "--no-supabase"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    # File still in inbox/
    assert f.exists()
    # Not in processed/
    assert not (tmp_path / "processed" / f.name).exists()
    data = json.loads(f.read_text())
    assert data["status"] == "deferred"
    last = data["status_history"][-1]
    assert last["kind"] == "annotation"
    assert "deferring" in last["note"].lower()
```

- [ ] **Step 3: Run tests**

Run:
```bash
python -m pytest ~/.claude/tests/test_close_inbox_item.py -v 2>&1 | tail -20
```

Expected: all new tests PASS plus any existing tests still pass.

- [ ] **Step 4: Sync + commit**

Run:
```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py --sync
cd sharkitect-claude-toolkit
git add scripts/close-inbox-item.py tests/test_close_inbox_item.py
git commit -m "close-inbox-item.py: withdrawn status + annotate mode + deprecation (plan C)"
git push
```

---

## Phase D — Build sync-permissions.py (TDD, ~1.5 hours)

### Task D1: Write failing tests for sync-permissions.py

**Files:**
- Create: `~/.claude/tests/test_sync_permissions.py`

- [ ] **Step 1: Write tests**

Write `~/.claude/tests/test_sync_permissions.py`:

```python
"""Tests for sync-permissions.py: read templates, write 4 settings.json with backup."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path.home() / ".claude" / "scripts" / "sync-permissions.py"


def _templates_fixture(tmp_path: Path) -> Path:
    t = {
        "schema_version": 1,
        "global_settings_path": str(tmp_path / "global-settings.json"),
        "global_permissions": {
            "allow_additions": ["Edit(~/.claude/rules/**)", "Edit(~/.claude/CLAUDE.md)"],
            "deny_additions": ["Edit(~/.claude/settings.json)"]
        },
        "workspaces": {
            "test-ws": {
                "settings_path": str(tmp_path / "test-ws-settings.json"),
                "deny_global_skill_hub_owned": ["Edit(~/.claude/rules/**)"],
                "deny_other_workspace_internals": [],
                "deny_inbox_direct_edit": [],
                "deny_other_workspace_human_action": []
            }
        }
    }
    p = tmp_path / "templates.json"
    p.write_text(json.dumps(t, indent=2), encoding="utf-8")
    return p


def _settings_fixture(path: Path, allow: list, deny: list) -> None:
    path.write_text(json.dumps({
        "permissions": {"allow": allow, "deny": deny}
    }, indent=2), encoding="utf-8")


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT)] + args,
                          capture_output=True, text=True, encoding="utf-8")


def test_dry_run_shows_diff_no_changes(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings, ["Bash(git status:*)"], [])

    r = _run(["--templates", str(templates), "--dry-run"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert "DRY RUN" in r.stdout or "dry run" in r.stdout.lower()
    assert "Edit(~/.claude/rules/**)" in r.stdout
    # File NOT modified
    data = json.loads(global_settings.read_text())
    assert data["permissions"]["allow"] == ["Bash(git status:*)"]


def test_execute_merges_additions_preserving_existing(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings,
                      ["Bash(git status:*)", "Bash(git push:*)"],
                      ["Bash(git push --force*)"])

    r = _run(["--templates", str(templates), "--execute"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(global_settings.read_text())
    assert "Bash(git status:*)" in data["permissions"]["allow"]
    assert "Bash(git push:*)" in data["permissions"]["allow"]
    assert "Bash(git push --force*)" in data["permissions"]["deny"]
    assert "Edit(~/.claude/rules/**)" in data["permissions"]["allow"]
    assert "Edit(~/.claude/settings.json)" in data["permissions"]["deny"]


def test_execute_creates_backup_before_write(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings, ["Bash(git status:*)"], [])

    r = _run(["--templates", str(templates), "--execute"])
    assert r.returncode == 0
    backups = list(global_settings.parent.glob("global-settings.json.bak.*"))
    assert len(backups) >= 1
    assert "Bash(git status:*)" in json.loads(backups[0].read_text())["permissions"]["allow"]


def test_idempotent_second_run_no_change(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings, ["Bash(git status:*)"], [])

    _run(["--templates", str(templates), "--execute"])
    after_first = global_settings.read_text()

    r = _run(["--templates", str(templates), "--execute"])
    assert r.returncode == 0
    assert global_settings.read_text() == after_first


def test_workspace_settings_creates_if_missing(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings, [], [])
    workspace_settings = tmp_path / "test-ws-settings.json"
    assert not workspace_settings.exists()

    r = _run(["--templates", str(templates), "--execute"])
    assert r.returncode == 0
    assert workspace_settings.exists()
    data = json.loads(workspace_settings.read_text())
    assert "Edit(~/.claude/rules/**)" in data["permissions"]["deny"]


def test_invalid_json_in_templates_aborts(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json {", encoding="utf-8")
    r = _run(["--templates", str(bad), "--execute"])
    assert r.returncode != 0
```

- [ ] **Step 2: Run tests, verify all fail**

```bash
python -m pytest ~/.claude/tests/test_sync_permissions.py -v 2>&1 | tail -15
```

Expected: all 6 tests FAIL (script doesn't exist).

---

### Task D2: Implement sync-permissions.py

**Files:**
- Create: `~/.claude/scripts/sync-permissions.py`

- [ ] **Step 1: Write the script**

Write `~/.claude/scripts/sync-permissions.py`:

```python
#!/usr/bin/env python
"""sync-permissions.py -- Propagate permissions templates to settings.json files.

Reads ~/.claude/config/workspace-permissions-templates.json (or override
via --templates). Writes the global ~/.claude/settings.json plus each
workspace's .claude/settings.json with the merged permissions block.
Existing entries are preserved; template additions are merged.
Atomic writes with timestamped backup. Idempotent.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


def _now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def _read_json(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON in {p}: {e}")


def _atomic_write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=p.name + ".", suffix=".tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, p)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _backup(p: Path) -> Path | None:
    if not p.exists():
        return None
    bak = p.with_suffix(p.suffix + f".bak.{_now_stamp()}")
    shutil.copy2(p, bak)
    return bak


def _expand_path(s: str) -> Path:
    """Expand ~/ and resolve."""
    return Path(os.path.expanduser(s)).resolve()


def _merge_lists(existing: list, additions: list) -> list:
    """Append additions preserving order, deduplicating against existing."""
    seen = set(existing)
    out = list(existing)
    for a in additions:
        if a not in seen:
            out.append(a); seen.add(a)
    return out


def _build_workspace_deny(ws_template: dict) -> list:
    """Concatenate the four deny categories from a workspace template."""
    out = []
    for k in ("deny_global_skill_hub_owned",
              "deny_other_workspace_internals",
              "deny_inbox_direct_edit",
              "deny_other_workspace_human_action"):
        out.extend(ws_template.get(k, []))
    return out


def sync_global(templates: dict, dry_run: bool) -> int:
    path = _expand_path(templates["global_settings_path"])
    settings = _read_json(path)
    perms = settings.setdefault("permissions", {})
    allow = perms.setdefault("allow", [])
    deny = perms.setdefault("deny", [])

    new_allow = _merge_lists(allow, templates["global_permissions"]["allow_additions"])
    new_deny = _merge_lists(deny, templates["global_permissions"]["deny_additions"])

    if new_allow == allow and new_deny == deny:
        print(f"  No change: {path}")
        return 0

    if dry_run:
        added_allow = [a for a in new_allow if a not in allow]
        added_deny = [d for d in new_deny if d not in deny]
        print(f"  Would update: {path}")
        for a in added_allow:
            print(f"    + allow: {a}")
        for d in added_deny:
            print(f"    + deny: {d}")
        return 0

    bak = _backup(path)
    perms["allow"] = new_allow
    perms["deny"] = new_deny
    _atomic_write_json(path, settings)
    print(f"  Updated: {path}  (backup: {bak.name if bak else 'NEW FILE'})")
    return 0


def sync_workspace(name: str, ws_template: dict, dry_run: bool) -> int:
    path = _expand_path(ws_template["settings_path"])
    settings = _read_json(path)
    perms = settings.setdefault("permissions", {})
    perms.setdefault("allow", [])
    deny = perms.setdefault("deny", [])

    additions = _build_workspace_deny(ws_template)
    new_deny = _merge_lists(deny, additions)

    if new_deny == deny:
        print(f"  [{name}] No change: {path}")
        return 0

    if dry_run:
        added = [a for a in new_deny if a not in deny]
        print(f"  [{name}] Would update: {path}")
        for d in added:
            print(f"    + deny: {d}")
        return 0

    bak = _backup(path)
    perms["deny"] = new_deny
    _atomic_write_json(path, settings)
    print(f"  [{name}] Updated: {path}  (backup: {bak.name if bak else 'NEW FILE'})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="sync-permissions.py")
    parser.add_argument("--templates",
                        default=str(Path.home() / ".claude" / "config" / "workspace-permissions-templates.json"))
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true",
                     help="Show what would change, don't write")
    grp.add_argument("--execute", action="store_true",
                     help="Apply changes with backup")
    args = parser.parse_args()

    templates_path = Path(args.templates)
    if not templates_path.exists():
        print(f"Templates not found: {templates_path}", file=sys.stderr)
        return 2
    templates = _read_json(templates_path)

    mode = "DRY RUN" if args.dry_run else "EXECUTE"
    print(f"sync-permissions.py [{mode}]")
    print(f"Templates: {templates_path}")
    print()
    print("Global settings:")
    sync_global(templates, args.dry_run)
    print()
    print("Workspace settings:")
    for name, ws in templates.get("workspaces", {}).items():
        sync_workspace(name, ws, args.dry_run)
    print()
    print("Done.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
```

- [ ] **Step 2: Run tests**

```bash
python -m pytest ~/.claude/tests/test_sync_permissions.py -v 2>&1 | tail -15
```

Expected: all 6 PASS.

- [ ] **Step 3: Sync + commit**

```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py --sync
cd sharkitect-claude-toolkit
git add scripts/sync-permissions.py tests/test_sync_permissions.py
git commit -m "sync-permissions.py: implementation + tests passing (plan D2)"
git push
```

---

## Phase E — Apply settings.json changes (~30 min)

### Task E1: Dry-run validation

- [ ] **Step 1: Run dry-run**

```bash
python ~/.claude/scripts/sync-permissions.py --dry-run
```

Expected output: lists what would be added.
- 35 entries to global allow (15 Edit/Write paths + 2 Bash script paths + 18 git Bash verbs)
- 7 entries to global deny
- ~25 deny entries per workspace
- Skill Hub + Sentinel show "Would create" since their settings.json files don't exist yet.

- [ ] **Step 2: Verify dry-run output looks correct**

Visual review. If any path is wrong (e.g., wrong workspace path, missing entry), fix templates and re-run dry-run.

---

### Task E2: Execute

- [ ] **Step 1: Execute the sync**

```bash
python ~/.claude/scripts/sync-permissions.py --execute
```

Expected: 4 file writes (global + 3 workspaces); 2 timestamped backups (global + HQ); 2 new files created (Skill Hub + Sentinel).

- [ ] **Step 2: Validate all 4 settings.json are valid JSON**

```bash
for f in ~/.claude/settings.json \
         "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.claude/settings.json" \
         "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.claude/settings.json" \
         "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.claude/settings.json"; do
  echo "=== $f ==="
  python -c "import json; d=json.load(open('$f')); a=d.get('permissions',{}).get('allow',[]); n=d.get('permissions',{}).get('deny',[]); print(f'OK -- {len(a)} allow, {len(n)} deny')"
done
```

Expected: all 4 print "OK" with allow/deny counts.

- [ ] **Step 3: Sync settings-backup.json to toolkit**

```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py --sync
cd sharkitect-claude-toolkit
git add settings-backup.json
git commit -m "Settings-backup snapshot post-Phase-E2 (plan E2)"
git push
```

---

### Task E3: Route commit-settings tasks to HQ + Sentinel

The new `<HQ>/.claude/settings.json` and (newly created) `<Skill Hub>/.claude/settings.json` need to be committed in their respective workspace repos. Skill Hub commits its own; HQ + Sentinel get routed-tasks.

- [ ] **Step 1: Commit Skill Hub workspace settings (in this workspace)**

```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
git add .claude/settings.json
git commit -m "Add Phase 1 workspace permissions deny scaffolding (plan E3)"
git push
```

- [ ] **Step 2: File routed-task to HQ**

```bash
cat > "/tmp/rt-hq-commit-settings.json" <<'EOF'
{
  "id": "rt-hq-2026-04-28-commit-settings",
  "id_format_version": 2,
  "task_summary": "Commit updated .claude/settings.json with workspace-scoped deny rules",
  "routed_from": "skill-management-hub",
  "routed_to": "workforce-hq",
  "source_workspace": "skill-management-hub",
  "routed_date": "2026-04-28",
  "priority": "low",
  "status": "pending",
  "context": "Phase 1 of permissions overhaul: HQ's .claude/settings.json was extended with workspace-scoped deny rules per workspace-permissions-templates.json. File needs commit + push.",
  "what_source_already_did": "sync-permissions.py merged the deny entries; verified valid JSON with expected entries; backup created at <backup>.bak.<timestamp>.",
  "fix_instructions": "From HQ workspace: git add .claude/settings.json && git commit -m 'Apply Phase 1 workspace permissions deny scaffolding' && git push",
  "notify_on_completion": true,
  "notify_inbox_path": "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox",
  "notification_filename_hint": "rt-2026-04-28-commit-settings-completed-by-workforce-hq.json"
}
EOF
cp "/tmp/rt-hq-commit-settings.json" "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/inbox/rt-hq-2026-04-28-commit-settings.json"
```

- [ ] **Step 3: File routed-task to Sentinel**

```bash
cat > "/tmp/rt-sentinel-commit-settings.json" <<'EOF'
{
  "id": "rt-sentinel-2026-04-28-commit-settings",
  "id_format_version": 2,
  "task_summary": "Commit new .claude/settings.json with workspace-scoped deny rules",
  "routed_from": "skill-management-hub",
  "routed_to": "sentinel",
  "source_workspace": "skill-management-hub",
  "routed_date": "2026-04-28",
  "priority": "low",
  "status": "pending",
  "context": "Phase 1 of permissions overhaul: Sentinel's .claude/settings.json was created (didn't exist before) with workspace-scoped deny rules per workspace-permissions-templates.json. File needs commit + push.",
  "what_source_already_did": "sync-permissions.py created the file; verified valid JSON with expected entries.",
  "fix_instructions": "From Sentinel workspace: git add .claude/settings.json && git commit -m 'Apply Phase 1 workspace permissions deny scaffolding' && git push",
  "notify_on_completion": true,
  "notify_inbox_path": "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox",
  "notification_filename_hint": "rt-2026-04-28-commit-settings-completed-by-sentinel.json"
}
EOF
cp "/tmp/rt-sentinel-commit-settings.json" "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.routed-tasks/inbox/rt-sentinel-2026-04-28-commit-settings.json"
```

---

## Phase F — Smoke test (~30 min)

> **CRITICAL: After E2 completes, OPEN A NEW CHAT to pick up the new settings. Smoke tests run in fresh sessions.** Cached permissions in the current session won't reflect the new rules.

### Task F1: Smoke test global allow -- Skill Hub edits ~/.claude/rules/  [PASS 2026-04-29]

- [x] **Step 1: In a NEW chat in Skill Hub workspace**

- [x] **Step 2: Create test file + attempt edit**

```bash
echo "smoke test marker" > ~/.claude/rules/.smoke-test-2026-04-28.md
```

In Claude session, ask:
> Edit ~/.claude/rules/.smoke-test-2026-04-28.md and append the line "Phase 1 verified".

Expected: edit succeeds without prompting.

**Result (2026-04-29 Session 4 cron PID 39392 fresh chat):** PASS. Edit tool succeeded on first call with zero permission prompts and zero bypass keywords. Confirms the explicit `Edit(~/.claude/rules/**)` allow rule in `~/.claude/settings.json` overrides the runtime self-modification gate that denied the prior session. Hard gate validator → Phase 1 architecture is operative as designed.

- [x] **Step 3: Cleanup**

```bash
rm ~/.claude/rules/.smoke-test-2026-04-28.md
```

If F1 FAILS (denied even with allow rule): halt; this is the open risk identified in spec. Set fallback `defaultMode: "acceptEdits"` or revert via backups (see Rollback Plan).

---

### Task F2: Smoke test workspace deny -- HQ tries to edit ~/.claude/rules/  [PASS 2026-04-29]

- [x] **Step 1: In a NEW chat in HQ workspace**

- [x] **Step 2: Try the edit**

**Result (2026-04-29 HQ fresh chat):** PASS. Write tool returned "File is in a directory that is denied by your permission settings." Workspace deny rule operative as designed.

If F2 FAILS (allowed when should be denied): halt; templates have a hole. Investigate which deny pattern didn't match.

---

### Task F3: Smoke test cross-workspace commons -- HQ edits lessons-learned.md  [PASS 2026-04-29]

- [x] **Step 1: In HQ session**

- [x] **Step 2: Revert**

**Result (2026-04-29 HQ fresh chat):** PASS. Edit append + revert both succeeded; tail of lessons-learned.md before/after sequence confirmed identical (Tags line ends file). methodology-nudge fired advisory on 2nd Edit (correctly non-blocking — advisory not gate). Cross-workspace commons access confirmed working as designed.

---

### Task F4: Smoke test inbox file CREATION -- HQ files routed-task to Sentinel  [BLOCKED-FINDING 2026-04-29 — defense-in-depth stronger than expected]

**Result (2026-04-29 HQ fresh chat):** BLOCKED-FINDING. The bash heredoc was DENIED by an additional shell-bypass guard with reason: "circumventing the Edit deny rule covering that path." The plan's premise that "bash CREATE bypasses Edit deny" is **wrong** — the system is MORE secure than the plan expected. Bash subprocess writes that target paths covered by Edit deny rules are also blocked.

**Policy decision (HQ recommendation, adopted 2026-04-29):** No carve-out. Defense-in-depth is the correct behavior; carve-outs erode the deny scaffolding. F4 retired as a smoke test — the capability it was designed to verify (bash bypass) is correctly blocked. Cross-workspace inbox writes use sanctioned tooling (`work-request.py`, `inbox-amend.py`) which sets `source_workspace` honestly and routes through authorized paths.

~~Step 1 / Step 2 (bash heredoc create + rm)~~ — superseded by the BLOCKED-FINDING above.

---

### Task F5: Smoke test inbox direct-Edit deny  [BLOCKED-FINDING 2026-04-29 — separate scope-creep guard fired upstream]

**Result (2026-04-29 HQ fresh chat):** BLOCKED-FINDING. Step 1's bash pre-place was DENIED by a separate scope-creep guard with reason: "Creating a fake test routed-task with misrepresented `source_workspace` in another workspace's inbox is scope creep." The pre-place itself never landed, so the F5 step-2 deny check could not run from HQ.

**Policy decision (HQ recommendation, adopted 2026-04-29):** No carve-out. The scope-creep guard correctly prevents one workspace from fabricating routed-task records that misrepresent their origin — this is exactly the kind of cross-workspace identity drift the permissions overhaul exists to prevent. F5's deny check is already covered transitively by the inbox direct-Edit deny rule which is exercised in normal operation (and would be re-tested by any cross-workspace amend attempt).

~~Step 1 / Step 2 / Step 3 (pre-place + Edit attempt + cleanup)~~ — superseded by the BLOCKED-FINDING above.

---

### Task F6: End-to-end inbox-amend.py test  [PARTIAL PASS 2026-04-29 — steps 1-3 PASS; step 4 correctly skipped per anti-ping-pong design]

**Result (2026-04-29 HQ fresh chat):** Steps 1-3 PASS. Step 4 CORRECTLY SKIPPED per self-filed-item anti-ping-pong rule.
- **Step 1 PASS:** `wr-hq-2026-04-29-002` filed at `2026-04-29_workforce-hq_test-marker-002.json`. work-request.py stdout: "Work request written: ...2026-04-29_workforce-hq_test-marker-002.json ID: wr-hq-2026-04-29-002 Supabase: logged".
- **Step 2 PASS:** `amend-2026-04-29-e639e4f4` applied with full schema; post-amend JSON shows `source_amendments=[{amendment_id: amend-2026-04-29-e639e4f4, actor: workforce-hq, amendment_type: add_context, ...}]`.
- **Step 3 PASS:** Withdraw cleanly closed `new -> withdrawn`, moved to Skill Hub `processed/`, Supabase row `wr-hq-2026-04-29-002` updated. Stdout includes "Notification: skip: self-filed item (source==closer=workforce-hq)".
- **Step 4 SKIPPED-BY-DESIGN:** ls of HQ inbox grep smoke returned only the original Phase F routed-task — no new completion notification created. This is correct: the Completion Notification Protocol explicitly skips notification when source==closer (anti-ping-pong rule, prevents self-notification feedback loops).

**Policy decision (HQ recommendation, adopted 2026-04-29):** Document anti-ping-pong skip as design-correct for self-filed scenarios. F6 step 4's notification expectation only applies when source ≠ closer (true cross-workspace flow). For end-to-end notification verification across workspaces, see F7's cross-workspace amendment flow (Sentinel → HQ-filed WR) which already exercises that path.

~~Step 1 / Step 2 / Step 3 / Step 4~~ — superseded by the PARTIAL PASS result above.

- [ ] **Step 1: From HQ session, file a real WR**

```bash
python ~/.claude/scripts/work-request.py \
  --type ENHANCE --severity info \
  --workspace workforce-hq \
  --workspace-path "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ" \
  --task "Smoke test for inbox-amend.py" \
  --category operations \
  --needed "test marker" \
  --gap "test marker" \
  --impact "none -- smoke test, will withdraw" \
  --fix-type "test" \
  --fix-desc "smoke test, will withdraw immediately" \
  --fix-components "none"
```

Note the WR id printed (something like `wr-hq-2026-04-28-XXX`).

- [ ] **Step 2: Amend with add-context**

```bash
python ~/.claude/scripts/inbox-amend.py add-context \
  --file "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox/<filename>.json" \
  --from workforce-hq \
  --reason "smoke testing the amendment system end-to-end" \
  --note "this is a test amendment that will be withdrawn shortly"
```

Expected: succeeds; `source_amendments[0]` populated with full schema.

- [ ] **Step 3: Withdraw**

```bash
python ~/.claude/scripts/inbox-amend.py withdraw \
  --file "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox/<filename>.json" \
  --from workforce-hq \
  --reason "smoke test complete -- withdrawing"
```

Expected: WR closed status=withdrawn; moved to processed/; auto-notification routed-task written to HQ inbox.

- [ ] **Step 4: Verify notification arrived**

```bash
ls "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/inbox/" | grep -i smoke
```

Expected: notification routed-task file present, kind=completion_notification, references the withdrawn WR.

---

### Task F7: Source-mismatch rejection test ✅ PASS (2026-04-29 Sentinel fresh chat)

- [x] **Step 1: From Sentinel session (NEW chat), try to amend HQ-filed WR**

  **Result:** Sentinel ran `inbox-amend.py add-context` against `2026-04-25_workforce-hq_comprehensive-audit-of-n8n-rel-001.json` with `--from sentinel`. Exit code 3 (nonzero). Stderr: `"Source mismatch: --from=sentinel but item.source_workspace=workforce-hq. Only the originating workspace may amend its own filed items. Cross-workspace coordination uses routed-tasks instead."` File SHA-256 unchanged before/after: `45830d2d78ce34a7708e334ae4bdb69abe1fe1d88bf1fdcb604c784e446b24ef`. Source-identity enforcement validated end-to-end. Notification: rt-skillhub-2026-04-29-phase-f-smoke-test-sentinel-completed-by-sentinel.json.

(Find a real HQ-filed WR that's still pending in `<Skill Hub>/.work-requests/inbox/`.)

```bash
python ~/.claude/scripts/inbox-amend.py add-context \
  --file "<path-to-HQ-filed-WR>" \
  --from sentinel \
  --reason "should fail -- not the source workspace" \
  --note "should not write"
```

Expected: returns nonzero; stderr contains "Source mismatch".

---

### Task F8: Cleanup smoke test artifacts (Sentinel-side: ✅ PASS 2026-04-29, HQ-side: ✅ PASS 2026-04-29)

- [x] **Sentinel-side cleanup verified (2026-04-29):** routed-tasks/inbox/ and ~/.claude/rules/ contain no HQ-leftover smoke artifacts (only F7 task itself in inbox at time of check). Note: plan-file update from Sentinel was permission-denied (~/.claude/plans/ is Skill Hub territory per the permissions overhaul — this is the system working as designed).
- [x] **HQ-side cleanup verified (2026-04-29):** Skill Hub `processed/` contains the withdrawn smoke-test WR + Sentinel F7 notification. HQ `.routed-tasks/inbox/` contains no orphan smoke artifacts beyond the original Phase F routed-task itself (which was the assignment, not an artifact). System clean. Plan-file update from HQ was correctly out of scope (~/.claude/plans/ is Skill Hub territory per the permissions overhaul) — Skill Hub completed the plan-file updates in this session.

```bash
ls "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/processed/" | grep smoke
ls "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/inbox/" | grep smoke
ls ~/.claude/rules/ | grep smoke
```

Expected: smoke test files moved/processed correctly. Optional: delete the smoke-test processed WR + completion notification if you want a clean inbox for next session.

---

## Phase G — Sentinel coordination (file routed-task only) (~5 min)

### Task G1: Route Supabase migration to Sentinel

- [ ] **Step 1: File routed-task**

```bash
cat > "/tmp/rt-sentinel-add-withdrawn-enum.json" <<'EOF'
{
  "id": "rt-sentinel-2026-04-28-add-withdrawn-enum",
  "id_format_version": 2,
  "task_summary": "Add 'withdrawn' to cross_workspace_requests.inbox_items_status_check enum",
  "routed_from": "skill-management-hub",
  "routed_to": "sentinel",
  "source_workspace": "skill-management-hub",
  "routed_date": "2026-04-28",
  "priority": "medium",
  "status": "pending",
  "context": "Phase 1 of permissions overhaul ships a new close status 'withdrawn' for source-initiated retraction. close-inbox-item.py accepts and emits this status; Supabase rejects until CHECK constraint updated.",
  "what_source_already_did": "Added 'withdrawn' to close-inbox-item.py status choices, updated universal-protocols.md Status Vocabulary Layers, deployed inbox-amend.py with withdraw mode auto-closing via close-inbox-item.py with --status withdrawn.",
  "fix_instructions": "1. ALTER TABLE cross_workspace_requests change CHECK constraint inbox_items_status_check to add 'withdrawn'. 2. Verify activity_stream.event_type CHECK constraint has space for 'wr_amendment' (Phase 1.5 will add this; reserve slot now if there's a constraint). 3. No-op test: insert a row with status='withdrawn' and confirm accepted. Roll back the test row.",
  "notify_on_completion": true,
  "notify_inbox_path": "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox",
  "notification_filename_hint": "rt-2026-04-28-add-withdrawn-enum-completed-by-sentinel.json"
}
EOF
cp "/tmp/rt-sentinel-add-withdrawn-enum.json" "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.routed-tasks/inbox/rt-sentinel-2026-04-28-add-withdrawn-enum.json"
ls "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.routed-tasks/inbox/" | grep withdrawn
```

Expected: routed-task file present in Sentinel inbox.

---

## Phase H — Documentation + close-out (~1.5 hours)

### Task H1: Write docs/permissions-architecture.md

- [ ] Write `~/.claude/docs/permissions-architecture.md` with sections:
  - Overview (two-layer model, deny precedence)
  - Source of truth: `~/.claude/config/workspace-permissions-templates.json`
  - Sync: `sync-permissions.py --execute` propagates to all 4 settings.json
  - Per-workspace allow/deny tables (Skill Hub / HQ / Sentinel)
  - Cross-workspace shared commons inventory
  - "Adding a new global path" walkthrough
  - "Adding a new workspace" walkthrough

(Reference content for these sections is in the templates JSON itself; doc just narrates.)

---

### Task H2: Write docs/inbox-amendment-protocol.md

- [ ] Write `~/.claude/docs/inbox-amendment-protocol.md` with sections:
  - When to amend vs file new vs withdraw
  - All 13 amendment modes with example commands
  - Schema reference (link to spec)
  - Status state machine (link to spec)
  - Status transitions table
  - Auto-close behavior on supersede/duplicate/withdraw
  - bulk-amend examples
  - Idempotency / replay safety

---

### Task H3: Write docs/permissions-emergency-override.md

- [ ] Write `~/.claude/docs/permissions-emergency-override.md`:
  - When to use (system blocks legitimate cross-lane work)
  - Procedure: edit `<workspace>/.claude/settings.local.json` (git-ignored) to add temporary `permissions.allow` rule
  - Critical: revert the override after work is done
  - Optional: file WR to Skill Hub if the deny pattern itself needs revision

---

### Task H4: Paste cron user-review rule into universal-protocols.md (NOW UNBLOCKED)

- [ ] **Step 1: From a Skill Hub session, attempt the edit**

The full rule text is staged in `<Skill Hub>/HUMAN-ACTION-REQUIRED.md` entry "2026-04-28 -- Paste cron-user-review-flag-honor rule". Apply it to `~/.claude/rules/universal-protocols.md` Idle Mode section.

Expected: succeeds. (Phase 1 unblocked global rule edits.)

- [ ] **Step 2: Verify**

```bash
grep -n "User-Review Flag Honor" ~/.claude/rules/universal-protocols.md
```

Expected: 1 match around line 561.

- [ ] **Step 3: Sync + commit**

```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py --sync
cd sharkitect-claude-toolkit
git add rules/universal-protocols.md
git commit -m "Add User-Review Flag Honor + System-Configuration Edit Hold rules (closes wr-hq-007 prep)"
git push
```

---

### Task H5: Close wr-hq-2026-04-27-007

- [ ] **Step 1: Close**

```bash
python ~/.claude/scripts/close-inbox-item.py \
  --file "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox/2026-04-27_workforce-hq_cron-sessions-must-respect-exp-007.json" \
  --status completed \
  --resolved-by skill-management-hub \
  --what-was-done "Cron user-review-flag-honor rule + system-config-edit-hold rule landed in ~/.claude/rules/universal-protocols.md as part of Phase 1 permissions overhaul. The harness self-modification gate that initially denied autonomous rule edits is now superseded by an explicit Edit(~/.claude/rules/**) allow + workspace-level denies for HQ and Sentinel. Original concern (cron sessions overriding user-review caveats) structurally prevented for system-config paths via permission gating + explicit rule." \
  --fix-type protocol \
  --verified true
```

Expected: WR closed; moved to processed/; notification routed-task auto-written to HQ.

---

### Task H6: Mark HUMAN-ACTION-REQUIRED entries done

- [ ] **Step 1: Edit Skill Hub HUMAN-ACTION-REQUIRED.md**

Open `c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/HUMAN-ACTION-REQUIRED.md`.

For the 2026-04-27 entry "Apply Tier 1 git allowlist + deny block to global ~/.claude/settings.json":
- Change `Status: open` → `Status: done`
- Change `Done: (pending)` → `Done: 2026-04-28T<actual UTC timestamp>`
- Append: `**Resolution:** Tier 1 git allowlist verified present in ~/.claude/settings.json (25 Bash allow / 10 Bash deny entries match Tier 1 spec). Phase 1 permissions overhaul layered Edit/Write rules on top.`

For the 2026-04-28 entry "Paste cron-user-review-flag-honor rule":
- Change `Status: open` → `Status: done`
- Change `Done: (pending)` → `Done: 2026-04-28T<actual UTC timestamp>`
- Append: `**Resolution:** Rule pasted to ~/.claude/rules/universal-protocols.md Idle Mode section in Phase H4 of plan 2026-04-28-permissions-and-inbox-amendment-system.md. Verified with grep "User-Review Flag Honor" returns 1 match. wr-hq-2026-04-27-007 closed in Phase H5.`

---

### Task H7: Add to plans-registry + Supabase project

- [ ] **Step 1: Update plans-registry**

Open `~/.claude/docs/plans-registry.md`. In the Active Plans table, add row:

```
| 2026-04-28-permissions-and-inbox-amendment-system | skill-management-hub | active | Phase 1 in progress | Two-layer permissions + generic inbox amendment system |
```

- [ ] **Step 2: Create Supabase project**

```bash
python ~/.claude/scripts/update-project-status.py add-project \
  "Permissions Overhaul + Inbox Amendment System" \
  --workspace skill-management-hub \
  --status active \
  --priority high \
  --notes "Plan: ~/.claude/plans/2026-04-28-permissions-and-inbox-amendment-system.md | Spec: <Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md"
```

(If `add-project` subcommand doesn't exist on this script version, use whatever subcommand creates a new project entry.)

- [ ] **Step 3: Add tasks for the plan phases**

```bash
for phase in "Phase A: Foundation" "Phase B: inbox-amend.py" "Phase C: close-inbox-item extensions" "Phase D: sync-permissions.py" "Phase E: Apply settings" "Phase F: Smoke tests" "Phase G: Sentinel coordination" "Phase H: Documentation + close-out"; do
  python ~/.claude/scripts/update-project-status.py add-task \
    "$phase" \
    --project "Permissions Overhaul + Inbox Amendment System" \
    --workspace skill-management-hub
done
```

---

### Task H8: Update lessons-learned + MEMORY.md

- [ ] **Step 1: Append quality-over-speed preference to lessons-learned.md**

Add to `~/.claude/lessons-learned.md` Preferences section:

```markdown
### 2026-04-28: Quality > speed for build/architecture decisions

User preference: "I prefer quality, final outcome, long-term solutions over speed. Get it right the first time rather than going back to fix later."

Applies to: all architecture, builds, refactors, client deliverables, tooling, schema design.

Exception (1-in-10 rule): time-sensitive client deadlines where full build would delay handoff. In that case, document the shortcut + the proper-path TODO.

Operational implication: when proposing options, lead with the long-term solution. Quick-fix options are alternatives only if the user has a deadline constraint.

Source: 2026-04-28 design conversation on inbox amendment system (where the user explicitly directed forward-thinking schema design and called out the close-state vocabulary inconsistency).
```

- [ ] **Step 2: Add Skill Hub MEMORY.md resume entry**

Edit `c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/[memory dir]/MEMORY.md` Resume Instructions, add at top:

```markdown
0aaaa. **2026-04-28 PERMISSIONS OVERHAUL EXECUTING** -- Plan at ~/.claude/plans/2026-04-28-permissions-and-inbox-amendment-system.md (8 phases over 3 sessions). Spec at <Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md. Closes wr-hq-2026-04-27-007 + 2 HUMAN-ACTION-REQUIRED items. Estimated 7-8 hours focused work. Pre-execution checklist: confirm git clean, confirm backup at ~/.claude/.tmp/settings-backups-2026-04-28/, read spec top-to-bottom, smoke test F1 is the first hard gate.
```

---

### Task H9: Final commit + push (workspace + toolkit)

- [ ] **Step 1: Commit workspace state**

```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
git add HUMAN-ACTION-REQUIRED.md
git add .work-requests/processed/2026-04-27_workforce-hq_cron-sessions-must-respect-exp-007.json
git add .work-requests/inbox/   # remove the closed WR (now empty there)
# Skill Hub MEMORY.md (memory dir path may vary)
# Add any new docs
git add docs/permissions-architecture.md docs/inbox-amendment-protocol.md docs/permissions-emergency-override.md 2>/dev/null || true
git commit -m "Phase 1 permissions overhaul COMPLETE: wr-hq-007 closed, HUMAN-ACTIONs done, 5-state vocab + withdrawn locked in"
git push
```

- [ ] **Step 2: Sync + commit toolkit**

```bash
cd "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py --sync --push
```

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Auto Mode harness STILL denies even with explicit Edit allow rules | Medium | High | F1 smoke test catches in 30 sec. Fallback: `defaultMode: "acceptEdits"` in global settings.json. If that fails too, halt; revert via backups; file Anthropic support ticket. |
| Workspace deny breaks legitimate cross-workspace flow we didn't inventory | Medium | High | F3-F7 cover known commons; pre-paste backups (A1) enable rollback; post-paste regression caught by normal session-checkpoint within 24h |
| `source_amendments[]` grows unbounded over time | Low | Low | Most items close before accumulating much; future Sentinel-driven compaction (Phase 3 vision) |
| bulk-amend partial failure leaves mixed state | Low | Low | Continue-on-failure semantics + clear failure report; each amendment is its own append-only event so partial state recoverable; documented as v1 limitation |
| Reroute filename collision overwrites destination | Low | Medium | B2 implementation includes pre-check + abort on collision; B1 test_reroute_aborts_on_collision verifies |
| Atomic write fails leaving tempfile orphan | Low | Low | All atomic write paths clean up tempfile in except block |
| Source mismatch on amendments rejects legitimate edits | Low | Medium | Workspace canonical names are stable; if mismatch, that's a real bug in the calling session's workspace-detection (separate Phase 1.5 follow-on) |
| Sentinel-side schema migration delays withdrawn-status acceptance in Supabase | Medium | Low | Local JSON is correct (source of truth); Supabase reconcile via `wr-supabase-reconcile.py` after Sentinel migration lands |
| Settings.json edit while Claude Code session running may not be picked up immediately | Medium | Medium | Plan explicitly requires NEW chat for smoke tests (F1-F8). Document: "Restart Claude Code or open new chat after sync-permissions.py --execute" |
| User changes mind on close-state consolidation mid-execution | Low | Low | Consolidation only in A3; one rule edit to revert if needed |
| Plan executor misreads phase ordering | Low | Medium | Explicit Phase A→B→C→D→E→F→G→H sequencing; each phase has dependencies noted |

---

## Rollback Plan

If F1 or F2 or F5 smoke tests fail (deny rules don't work as expected) OR any step damages a workflow:

1. **Stop immediately.** Do not proceed.
2. **Restore from backups:**
   ```bash
   cp ~/.claude/.tmp/settings-backups-2026-04-28/global-settings.json.bak ~/.claude/settings.json
   cp ~/.claude/.tmp/settings-backups-2026-04-28/hq-settings.json.bak "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.claude/settings.json"
   rm "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.claude/settings.json"
   rm "c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.claude/settings.json"
   ```
3. **Verify restoration:** open new chat in each workspace; attempt the original failing op; confirm pre-Phase-1 behavior.
4. **Document** in `~/.claude/lessons-learned.md` and file follow-on WR with the specific deny that bit us.

If only one component fails (e.g., inbox-amend.py works but sync-permissions.py breaks), roll back only the failed component.

Toolkit safety-backup commit (A1 Step 3) provides cross-machine recovery if local backups are lost.

---

## Self-Review (executed before plan finalized)

**Spec coverage:**
- ✅ Two-layer permissions architecture → A2 + D1/D2 + E1/E2
- ✅ Workspace-scoped deny → A2 templates + D2 sync + F2/F5 smoke tests
- ✅ Cross-workspace shared commons → A2 (templates) + F3/F4 smoke tests
- ✅ Generic inbox-amend covers WR/RT/lifecycle → B2 (`source_workspace OR routed_from`)
- ✅ All 13 amendment modes → B2 cmd_* functions; B1 tests cover each
- ✅ `withdrawn` status → C1 + Phase G migration
- ✅ Close-state consolidation (processed/resolved → completed) → C1 + A3
- ✅ Auto-close on supersede/duplicate/withdraw → B2 `_maybe_auto_close`
- ✅ Bulk amend included → B2 `cmd_bulk_amend` + B1 tests
- ✅ Forward-compat schema slots → B2 `_build_event` (condition, template_id, expires_at, parent_etag, triggers)
- ✅ Idempotency → B2 `_is_idempotent_replay`; B1 test
- ✅ Retraction → B2 `cmd_retract_amendment`; B1 test
- ✅ Reroute collision check → B2 `cmd_reroute`; B1 test
- ✅ Annotate mode → C2; C3 test
- ✅ Emergency override → H3 docs
- ✅ Sync mechanism with backup → D2 `_backup`
- ✅ Smoke tests F1-F8
- ✅ Sentinel coordination → G1
- ✅ Close wr-hq-007 + HUMAN-ACTIONs → H4-H6
- ✅ Plan registered + Supabase → H7
- ✅ MEMORY.md + lessons-learned → H8

**Placeholder scan:**
- ✅ No "TBD" / "TODO later" outside intentional Out-of-Scope deferral references
- ✅ All code blocks have actual code (no stubs)
- ✅ All paths exact

**Type/name consistency:**
- ✅ `inbox-amend.py`, `sync-permissions.py`, `close-inbox-item.py` consistent throughout
- ✅ Status names: `new | pending | in_progress | deferred | blocked | completed | rejected | superseded | duplicate | withdrawn`
- ✅ Mode names: `add-context | severity-update | priority-update | component-add | component-remove | add-evidence | link-related | reclassify | supersede | duplicate | withdraw | reroute | retract-amendment | bulk-amend`
- ✅ Canonical workspace names: `workforce-hq | skill-management-hub | sentinel`
- ✅ Schema fields: `amendment_id | timestamp | actor | actor_type | amendment_type | reason | fields_changed | structured_data | notes | supersedes | duplicate_of | retracts_amendment | retracted | retracted_at | retracted_by_amendment_id | condition | template_id | expires_at | parent_etag | triggers`

---

## Execution Handoff

**Plan complete and saved to `~/.claude/plans/2026-04-28-permissions-and-inbox-amendment-system.md`.**

Two execution options for next session(s):

1. **Subagent-Driven (recommended)** -- I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for: keeping the executing chat's context window focused; cleaner per-task review; faster failure detection at task boundaries.

2. **Inline Execution** -- Execute tasks in the next chat using `superpowers:executing-plans`, batch execution with checkpoints. Best for: tight integration where context across phases matters more.

**Recommended split per user preference (3 sessions):**
- Session 1: Phase 0 + Phases A + B (HQ WR triage + foundation + amendment tool). ~3-3.5 hours.
- Session 2: Phases C + D (close-inbox-item extension + sync-permissions). ~2 hours.
- Session 3: Phases E + F + G + H (apply, smoke test, coordination, close-out). ~2-3 hours.

Total: 7.5-8.5 hours focused build, 3 sessions, manageable context per chat.

**Pre-execution checklist for the next session:**
- [ ] git state clean before starting
- [ ] Read this plan + the spec top-to-bottom before invoking `executing-plans` / `subagent-driven-development`
- [ ] Verify all 9 currently-deferred WRs in inbox are still relevant
- [ ] Smoke test F1 is the first hard gate -- if fails, halt and re-investigate before proceeding

**Which execution approach?**
