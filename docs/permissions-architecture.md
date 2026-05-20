# Permissions Architecture

**Status:** Active (shipped 2026-04-28, plan Phases A-D complete)
**Source of truth:** `~/.claude/config/workspace-permissions-templates.json`
**Sync tool:** `~/.claude/scripts/sync-permissions.py`
**Spec:** `<Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md`

This document is reference material. For status vocabulary and inbox protocols, see `~/.claude/rules/universal-protocols.md`. This file complements those rules; it does not replace them.

---

## Overview -- Two-Layer Model

Claude Code resolves permissions by checking two sources in order:

1. **Global** -- `~/.claude/settings.json` -- applies to every session, every workspace, on this machine.
2. **Workspace** -- `<workspace>/.claude/settings.json` -- applies only when the session is rooted in that workspace directory.

Both layers contribute to a combined `allow` and `deny` list. Claude Code resolution rules:

| Rule | Behavior |
|------|----------|
| **Deny precedence** | Any `deny` match (global OR workspace) wins, regardless of any matching `allow`. |
| **Specificity wins** | A more specific path pattern overrides a broader one in the same direction (e.g., `Edit(~/.claude/skills/**)` allow is overridden by `Edit(~/.claude/settings.json)` deny). |
| **Workspace deny adds, never subtracts** | A workspace cannot grant something the global denied. It can only ADD denies on top of global allows. |

In practice the architecture is:

```
Global settings.json
    permissions.allow:  WIDE -- skills/, agents/, hooks/, scripts/, rules/,
                                CLAUDE.md, all Workspaces/, git verbs,
                                helper scripts
    permissions.deny:   NARROW -- settings.json itself, plugin cache,
                                .env, workspace .claude/settings*.json

Workspace settings.json (HQ, Sentinel only -- Skill Hub has no global denies)
    permissions.deny:   Workspace-specific -- denies the OTHER workspaces'
                                internals, denies global Skill-Hub-owned
                                paths (rules/, hooks/, scripts/, ...)
```

Skill Hub is the curator workspace -- it has wide permissions on global infrastructure paths because it owns skills, hooks, scripts, rules. HQ and Sentinel are scoped: they can read globally, but can only WRITE to their own workspace directory plus the cross-workspace shared commons.

---

## Source of Truth

Canonical: **`~/.claude/config/workspace-permissions-templates.json`**

The four `settings.json` files (1 global + 3 workspace) are derived from this single template file. Hand-editing a `settings.json` is allowed for emergency overrides via `settings.local.json` (see `permissions-emergency-override.md`), but the templates JSON is what gets propagated and committed across machines via the toolkit repo.

The templates JSON has this top-level shape:

| Field | Type | Purpose |
|-------|------|---------|
| `schema_version` | int | Currently `1`. Bump on breaking changes. |
| `documented_at` | string | ISO date the template was last revised. |
| `documented_by` | string | Canonical workspace name that last revised it. |
| `source_plan` | string | Path to the originating plan file. |
| `source_spec` | string | Path to the originating spec. |
| `global_settings_path` | string | Where the global settings.json lives (`~/.claude/settings.json`). |
| `global_permissions.allow_additions[]` | list | Patterns to merge into global allow. |
| `global_permissions.deny_additions[]` | list | Patterns to merge into global deny. |
| `workspaces.<name>.settings_path` | string | Where this workspace's settings.json lives. |
| `workspaces.<name>.deny_global_skill_hub_owned[]` | list | Denies global infra paths (HQ + Sentinel only). |
| `workspaces.<name>.deny_other_workspace_internals[]` | list | Denies sibling workspaces' tools/, docs/, etc. |
| `workspaces.<name>.deny_inbox_direct_edit[]` | list | Forces inbox edits through CLI. |
| `workspaces.<name>.deny_other_workspace_human_action[]` | list | Denies cross-workspace HUMAN-ACTION-REQUIRED.md edits. |
| `shared_commons_left_writeable.paths[]` | list | Documentation only -- inventory of cross-workspace writeable paths. |
| `emergency_override_procedure` | string | Pointer to override doc. |

The four workspace deny categories are kept separate so each policy axis can be reasoned about and modified independently. Adding a new "Skill-Hub-owned global path" updates one list everywhere; adding a new sibling-workspace internal updates one list per affected workspace.

---

## Sync Mechanism

`~/.claude/scripts/sync-permissions.py` reads the templates and propagates to all 4 settings.json files.

### Modes

| Flag | Behavior |
|------|----------|
| `--dry-run` | Prints what would change. Writes nothing. |
| `--execute` | Writes changes. Creates timestamped backup of any pre-existing settings.json. |

`--dry-run` and `--execute` are mutually exclusive and one is required.

### Behavior

1. **Loads + validates templates.** Calls `_validate_templates(...)`. On missing/malformed top-level keys exits rc=3 with a list of errors. Examples of validation failures: missing `global_settings_path`, missing `global_permissions`, `allow_additions` not a list, missing `workspaces.<name>.settings_path`.
2. **For the global file:** reads existing settings.json (or empty dict if absent), merges `allow_additions` into `permissions.allow` and `deny_additions` into `permissions.deny`, deduplicating against existing entries. Order is preserved -- existing entries first, additions appended. Refuses to merge if existing `permissions.allow` or `permissions.deny` is not a list (rc=1 with a clear error).
3. **For each workspace:** does the same with the four workspace deny categories concatenated into one deny list. Workspaces only contribute denies; allows are inherited from global.
4. **Atomic write:** `_atomic_write_json` writes to a tempfile in the same directory and `os.replace`s onto the destination. Tempfile is cleaned up on failure; original file untouched.
5. **Backup:** `_backup` copies the existing file (if any) to a timestamped sibling like `settings.json.bak.20260428-143022`. On collision (rerun within the same second) a counter suffix is appended (`.bak.<stamp>-1`, `.bak.<stamp>-2`).
6. **Idempotency:** rerunning with no template changes prints "No change: <path>" for each file and exits 0.

### `_expand_path` POSIX-to-Windows translation

Templates use POSIX-style paths like `//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/...` because that is the form Claude Code permission patterns match on Windows. But `Path.resolve()` on Windows interprets `//c/...` as a UNC network path (`\\c\...`), which fails for filesystem operations.

`_expand_path` (line 61 of `sync-permissions.py`) detects the `//<letter>/` POSIX form on `win32` and rewrites it to drive-letter form (`<letter>:/...`) before calling `Path(s).resolve()`. The original POSIX form is what gets written into the settings.json files (Claude Code expects that). The Windows form is only used for opening + writing the file.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success (or no changes needed). |
| 1 | Existing settings.json has malformed `permissions.allow` / `permissions.deny` (not a list). |
| 2 | Templates file not found. |
| 3 | Templates file failed `_validate_templates` (missing or malformed required keys). |
| 130 | Ctrl-C interrupt. |

---

## Per-Workspace Allow/Deny Inventory

Pulled from `~/.claude/config/workspace-permissions-templates.json` as of schema_version 1. Always re-check the templates file for the current truth.

### Global (everywhere)

**Allow additions** (relevant categories):

| Category | Patterns |
|----------|----------|
| Edit on global infra | `Edit(~/.claude/rules/**)`, `Edit(~/.claude/CLAUDE.md)`, `Edit(~/.claude/skills/**)`, `Edit(~/.claude/agents/**)`, `Edit(~/.claude/hooks/**)`, `Edit(~/.claude/scripts/**)`, `Edit(~/.claude/docs/**)`, `Edit(~/.claude/lessons-learned.md)`, `Edit(~/.claude/.tmp/**)`, `Edit(~/.claude/config/**)`, `Edit(~/.claude/tests/**)`, `Edit(~/.claude/plans/**)` |
| Edit on workspaces | `Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/**)` |
| Bash on helper scripts | `Bash(python ~/.claude/scripts/sync-permissions.py *)`, `Bash(python ~/.claude/scripts/inbox-amend.py *)` |
| Bash on git verbs | `Bash(git mv:*)`, `Bash(git rm:*)`, `Bash(git clone:*)`, `Bash(git ls-files:*)`, `Bash(git ls-tree:*)`, `Bash(git show-ref:*)`, `Bash(git submodule:*)`, `Bash(git worktree:*)`, `Bash(git reflog:*)`, `Bash(git cherry-pick:*)`, `Bash(git revert:*)`, `Bash(git blame:*)`, `Bash(git bisect:*)`, `Bash(git apply:*)`, `Bash(git format-patch:*)`, `Bash(git ls-remote:*)`, `Bash(git fsck:*)`, `Bash(git gc:*)`, `Bash(git prune:*)`, `Bash(git notes:*)` |

**Deny additions** (apply everywhere):

| What | Pattern |
|------|---------|
| Global settings file | `Edit(~/.claude/settings.json)` |
| Global local override | `Edit(~/.claude/settings.local.json)` |
| Workspace settings files | `Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/**/.claude/settings.json)`, `...settings.local.json` |
| Plugin cache | `Edit(~/.claude/plugins/**)` |
| Secrets | `Edit(~/.claude/.env)`, `Edit(//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/**/.env)` |

### Skill Hub (`skill-management-hub`)

Skill Hub is the curator workspace. **No global Skill-Hub-owned denies** -- it owns skills/, hooks/, scripts/, rules/, etc. and has full Edit access to all of them via the global allow.

| Deny category | Targets |
|---------------|---------|
| `deny_global_skill_hub_owned` | (empty list) |
| `deny_other_workspace_internals` | HQ: `_archive/**`, `assets/**`, `docs/**`, `knowledge-base/**`, `resources/**`, `tools/**`, `workflows/**`, `.claude/**`, `CLAUDE.md`, `MEMORY.md`. Sentinel: `docs/**`, `supabase/**`, `tools/**`, `workflows/**`, `.claude/**`, `CLAUDE.md`, `MEMORY.md` |
| `deny_inbox_direct_edit` | HQ + Sentinel `.routed-tasks/inbox/**`, `.routed-tasks/processed/**`, `.lifecycle-reviews/inbox/**`, `.lifecycle-reviews/processed/**` |
| `deny_other_workspace_human_action` | `<HQ>/HUMAN-ACTION-REQUIRED.md`, `<Sentinel>/HUMAN-ACTION-REQUIRED.md` |

**What Skill Hub CAN do:** edit anything under `~/.claude/` except settings files and plugins. Edit any file in its own workspace. File new inbox items into HQ/Sentinel via `Bash` subprocess (e.g., `notify-human-action.py`, `work-request.py`). Amend its own filed inbox items via `inbox-amend.py`.

**What Skill Hub CANNOT do:** directly Edit any HQ or Sentinel internal file (forces work-request.py / routed-task flow). Directly Edit cross-workspace inbox items (forces inbox-amend.py).

### Workforce HQ (`workforce-hq`)

| Deny category | Targets |
|---------------|---------|
| `deny_global_skill_hub_owned` | `~/.claude/rules/**`, `~/.claude/skills/**`, `~/.claude/agents/**`, `~/.claude/hooks/**`, `~/.claude/scripts/**`, `~/.claude/CLAUDE.md`, `~/.claude/docs/**`, `~/.claude/config/**`, `~/.claude/tests/**`, `~/.claude/plans/**` |
| `deny_other_workspace_internals` | Skill Hub: `docs/**`, `knowledge-base/**`, `resources/**`, `sharkitect-claude-toolkit/**`, `skill-comparison-test/**`, `tests/**`, `tools/**`, `workflows/**`, `.claude/**`, `CLAUDE.md`, `MEMORY.md`. Sentinel: `docs/**`, `supabase/**`, `tools/**`, `workflows/**`, `.claude/**`, `CLAUDE.md`, `MEMORY.md` |
| `deny_inbox_direct_edit` | Skill Hub `.work-requests/inbox/**` + `processed/**`, `.lifecycle-reviews/inbox/**` + `processed/**`. Sentinel `.routed-tasks/inbox/**` + `processed/**`, `.lifecycle-reviews/inbox/**` + `processed/**` |
| `deny_other_workspace_human_action` | `<Skill Hub>/HUMAN-ACTION-REQUIRED.md`, `<Sentinel>/HUMAN-ACTION-REQUIRED.md` |

**What HQ CAN do:** edit anything in its own workspace. File new WRs into Skill Hub via `work-request.py`. File new routed-tasks into Sentinel via Bash file creation. Amend its own filed inbox items via `inbox-amend.py`. Append entries to its own HUMAN-ACTION-REQUIRED.md (and other workspaces' via `notify-human-action.py`).

**What HQ CANNOT do:** Edit any global infra path (skills, hooks, rules, scripts, config, docs, agents). If HQ needs a hook fix, it files a WR. Edit Skill Hub or Sentinel internals. Edit cross-workspace inbox files directly.

### Sentinel (`sentinel`)

| Deny category | Targets |
|---------------|---------|
| `deny_global_skill_hub_owned` | Same as HQ -- `~/.claude/rules/**`, `~/.claude/skills/**`, `~/.claude/agents/**`, `~/.claude/hooks/**`, `~/.claude/scripts/**`, `~/.claude/CLAUDE.md`, `~/.claude/docs/**`, `~/.claude/config/**`, `~/.claude/tests/**`, `~/.claude/plans/**` |
| `deny_other_workspace_internals` | HQ: same as Skill Hub's deny on HQ. Skill Hub: same as HQ's deny on Skill Hub. |
| `deny_inbox_direct_edit` | HQ `.routed-tasks/inbox/**` + `processed/**`, `.lifecycle-reviews/inbox/**` + `processed/**`. Skill Hub `.work-requests/inbox/**` + `processed/**`, `.lifecycle-reviews/inbox/**` + `processed/**` |
| `deny_other_workspace_human_action` | `<HQ>/HUMAN-ACTION-REQUIRED.md`, `<Skill Hub>/HUMAN-ACTION-REQUIRED.md` |

**What Sentinel CAN do:** edit anything in its own workspace (including Supabase schema files under `supabase/`). File new routed-tasks into HQ or Skill Hub. File new WRs to Skill Hub via `work-request.py`. Amend its own filed inbox items via `inbox-amend.py`. Append entries to its own HUMAN-ACTION-REQUIRED.md.

**What Sentinel CANNOT do:** Edit global infra. Edit HQ or Skill Hub internals. Edit cross-workspace inbox files directly.

---

## Cross-Workspace Shared Commons Inventory

Paths every workspace can write because they are NOT in any workspace's deny list. All cross-workspace coordination flows through these. Documented in `shared_commons_left_writeable.paths` in the templates JSON.

| Path | Access Pattern | Workspace That Writes |
|------|----------------|----------------------|
| `~/.claude/lessons-learned.md` | Direct Edit allowed | All workspaces (session-end appends) |
| `~/.claude/docs/plans-registry.md` | Direct Edit allowed | All workspaces (plan lifecycle updates) |
| `~/.claude/.tmp/**` | Direct Edit allowed | All workspaces (caches, manifests, logs) |
| `<other workspace>/.routed-tasks/inbox/<filename>.json` | NEW file via Bash/Python or AI Write tool | All workspaces filing routed-tasks |
| `<other workspace>/.lifecycle-reviews/inbox/<filename>.json` | Same | All workspaces filing lifecycle reviews |
| `<Skill Hub>/.work-requests/inbox/<filename>.json` | Via `work-request.py` Bash subprocess | HQ + Sentinel filing WRs |
| `<own workspace>/HUMAN-ACTION-REQUIRED.md` | Direct Edit allowed | Own workspace |
| `<other workspace>/HUMAN-ACTION-REQUIRED.md` | Via `notify-human-action.py` Bash subprocess | All workspaces (cross-workspace appends) |

**Important nuance: deny-on-existing vs allow-on-create.** The `deny_inbox_direct_edit` lists block direct Edit on existing files in those inbox dirs. But CREATING a new file in the same directory via Bash subprocess (or AI Write tool) is permitted by the global `Edit(//c/.../Workspaces/**)` allow. The deny applies to existing files; the global allow applies to file creation. This is what makes the file-new + amend-via-CLI architecture possible.

---

## Walkthrough: Adding a New Global Path

Use this walkthrough when you discover a new global infrastructure path that should be writeable from Skill Hub but denied to HQ + Sentinel (e.g., a new directory under `~/.claude/` like `~/.claude/templates/`).

```bash
# 1. Edit the templates file
# Add to global_permissions.allow_additions[] in
# ~/.claude/config/workspace-permissions-templates.json:
#   "Edit(~/.claude/templates/**)"

# Add to BOTH workforce-hq and sentinel deny_global_skill_hub_owned[]:
#   "Edit(~/.claude/templates/**)"

# Skill Hub gets nothing added -- empty deny_global_skill_hub_owned by design.

# 2. Dry-run to confirm the diff
python ~/.claude/scripts/sync-permissions.py --dry-run

# Expect: "+ allow: Edit(~/.claude/templates/**)" under Global,
#         "+ deny: Edit(~/.claude/templates/**)" under workforce-hq AND sentinel,
#         "No change: ..." for Skill Hub.

# 3. Execute (creates timestamped backups of any pre-existing settings.json)
python ~/.claude/scripts/sync-permissions.py --execute

# 4. Verify the four settings files updated
ls ~/.claude/settings.json.bak.*           # backup created
ls "<HQ>/.claude/settings.json.bak.*"      # backup created
ls "<Sentinel>/.claude/settings.json.bak.*" # backup created
# Skill Hub may not get a backup if no prior file existed.

# 5. Commit the templates JSON to the toolkit repo
cd "<Skill Hub>/sharkitect-claude-toolkit"
git add config/workspace-permissions-templates.json
git commit -m "Add ~/.claude/templates/** to permissions templates"
git push
```

---

## Walkthrough: Adding a New Workspace

Use this when a fourth workspace gets added to the operation.

```bash
# 1. Edit ~/.claude/config/workspace-permissions-templates.json
# Add a new key under "workspaces":
#   "new-workspace-canonical-name": {
#     "settings_path": "//c/Users/.../<new workspace dir>/.claude/settings.json",
#     "deny_global_skill_hub_owned": [
#       (copy from workforce-hq -- same denies on global infra)
#     ],
#     "deny_other_workspace_internals": [
#       (deny HQ + Skill Hub + Sentinel internals -- mirror existing patterns)
#     ],
#     "deny_inbox_direct_edit": [
#       (deny HQ + Skill Hub + Sentinel inbox dirs -- same pattern)
#     ],
#     "deny_other_workspace_human_action": [
#       (deny HQ + Skill Hub + Sentinel HUMAN-ACTION-REQUIRED.md)
#     ]
#   }

# Also: ADD the new workspace to the OTHER three workspaces'
# deny_other_workspace_internals + deny_inbox_direct_edit +
# deny_other_workspace_human_action lists (so they cannot edit IT either).

# 2. Update CANONICAL_WORKSPACES tuple in:
#   ~/.claude/scripts/inbox-amend.py  (line ~34)
#   Plus any other script enforcing the canonical list. Search:
#     grep -rn "CANONICAL_WORKSPACES" ~/.claude/scripts/
#     grep -rn "WORKSPACE_SHORT_MAP" ~/.claude/scripts/

# 3. Dry-run + execute
python ~/.claude/scripts/sync-permissions.py --dry-run
python ~/.claude/scripts/sync-permissions.py --execute

# 4. Create the new workspace's inbox structure
mkdir -p "<new workspace>/.routed-tasks/inbox" \
         "<new workspace>/.routed-tasks/processed" \
         "<new workspace>/.routed-tasks/outbox" \
         "<new workspace>/.lifecycle-reviews/inbox" \
         "<new workspace>/.lifecycle-reviews/processed" \
         "<new workspace>/.claude"

# 5. Add the new workspace to the universal-protocols.md canonical
# naming table. Update CLAUDE.md PROJECT_PURPOSE references.

# 6. Commit templates + script changes to toolkit
cd "<Skill Hub>/sharkitect-claude-toolkit"
git add config/workspace-permissions-templates.json scripts/inbox-amend.py
git commit -m "Add <new workspace> to permissions templates + amend CLI"
git push

# 7. Route a startup task to the new workspace via its routed-tasks/inbox
# so it picks up the change at next session start.
```

---

## Limitations + Open Items (v1)

| Limitation | Status | Notes |
|------------|--------|-------|
| `withdrawn` not yet in Supabase `cross_workspace_requests.inbox_items_status_check` enum | Filed to Sentinel via plan Phase G | `close-inbox-item.py` will write `withdrawn` to Supabase; constraint will reject until migration ships. Until then, expect Supabase POST failures on withdraw closes. |
| Settings.json hand-edits drift from templates | Mitigated by `--dry-run` showing diffs | If you hand-edited a settings.json, the next `--execute` will re-add removed allows / re-add removed denies. To remove a permission permanently, edit the templates JSON, NOT the settings.json. |
| Settings.local.json overrides are git-ignored | Documented in `permissions-emergency-override.md` | Local overrides drift between machines. Use only for emergency, revert promptly, file a WR if the deny pattern itself needs revision. |
| Templates JSON does not enforce structure beyond `_validate_templates` | Acceptable for v1 | Validator checks top-level keys + list types. Does NOT validate that paths exist on disk or that pattern strings are syntactically valid Claude Code permission patterns. |

---

## See Also

- `~/.claude/docs/inbox-amendment-protocol.md` -- how to amend inbox items now that direct Edit is denied.
- `~/.claude/docs/permissions-emergency-override.md` -- the emergency escape hatch.
- `~/.claude/rules/universal-protocols.md` -- Status Vocabulary Layers, Rejected vs Drift-Correction, Superseded vs Duplicate, Blocked vs Deferred. Authoritative for inbox semantics.
- `<Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md` -- design rationale and the "why."
