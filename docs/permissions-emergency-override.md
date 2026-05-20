# Permissions Emergency Override

**Status:** Active (shipped 2026-04-28 as part of Permissions Overhaul)
**Source of truth:** `~/.claude/config/workspace-permissions-templates.json`
**Companion docs:** `permissions-architecture.md`, `inbox-amendment-protocol.md`

This is the escape hatch when the permissions system blocks legitimate cross-lane work that needs to ship NOW. Use sparingly. Always revert.

---

## When to Use

Use this procedure ONLY when ALL of the following are true:

1. The deny is genuinely blocking work that has to ship in the current session.
2. Filing a WR + waiting for Skill Hub to merge a templates change is not viable on this timeline.
3. The work is small, scoped, and one-off -- not a recurring need.
4. You will revert the override the moment the immediate task ships.

Examples of legitimate emergencies:
- HQ session needs to write a one-off file under `~/.claude/skills/<somewhere>` to fix a session-blocking error and the Skill Hub session can't be opened in time.
- Sentinel needs to read+modify a Skill Hub workspace file as a one-off cleanup during an audit, before opening Skill Hub to do it properly.

Examples that are NOT emergencies (file a WR instead):
- Recurring need to write to a path the deny covers -> the templates JSON is wrong; fix it via WR to Skill Hub, not local override.
- Convenience ("it would be faster to do this from here") -> route via inbox; the deny exists for a reason.
- Accidental scope creep into another workspace's territory -> stop and route the work properly.

---

## Procedure

The override file is `<workspace>/.claude/settings.local.json`. This file is git-ignored. It is loaded by Claude Code on top of the workspace's `settings.json` and the global `settings.json`. Its `permissions.allow` entries override matching `permissions.deny` entries above it.

### Step 1: Identify the blocking pattern

When Claude Code denies a tool call, the rejection includes the matching deny rule. Note the exact pattern -- you'll match it in the override.

Example: working from HQ, you try to Edit a file under `~/.claude/skills/`, and the deny rule `Edit(~/.claude/skills/**)` from HQ's workspace `settings.json` blocks it.

### Step 2: Add a temporary allow to settings.local.json

Edit `<workspace>/.claude/settings.local.json` (create if it doesn't exist):

```json
{
  "permissions": {
    "allow": [
      "Edit(~/.claude/skills/specific-skill-name/SKILL.md)"
    ]
  }
}
```

Make the override pattern as specific as possible. Avoid overriding the entire `Edit(~/.claude/skills/**)` deny -- target the single file or the smallest subdirectory that unblocks your work.

### Step 3: Do the work

Make the immediate change. Verify it works. Commit if appropriate.

### Step 4: REVERT THE OVERRIDE (NON-NEGOTIABLE)

Remove the entry from `settings.local.json` the moment the immediate task ships. If `settings.local.json` only contained the temporary entry, delete the entire `permissions.allow` array (or delete the file if you only had this one override).

```bash
# Option A: edit the JSON to remove the entry
# Option B: if it was the only override, delete the file
rm "<workspace>/.claude/settings.local.json"
```

**Why revert is mandatory:**
- `settings.local.json` is git-ignored. It drifts between machines. An override left in place on machine A but not machine B causes "works on my machine" bugs that are hard to diagnose.
- Local overrides defeat the system. The deny patterns exist because cross-workspace writes cause real incidents (one workspace updating another's records with stale context, breaking ownership, mis-attributing changes). Every persistent local override erodes that protection.
- The override is invisible to other workspaces and to Sentinel audits. Persistent overrides hide policy drift.

### Step 5 (Optional): If the deny pattern keeps biting legitimate work

If you find yourself using the same override repeatedly across sessions, the templates JSON itself needs revision. File a WR to Skill Hub:

```bash
python ~/.claude/scripts/work-request.py \
  --type ENHANCE \
  --severity warning \
  --workspace "<your workspace canonical name>" \
  --workspace-path "$(pwd)" \
  --task "Permissions templates: deny pattern X blocks legitimate use case Y" \
  --category infrastructure \
  --needed "Allow <specific path/pattern> for <workspace>" \
  --gap "Current deny <full pattern from templates> blocks <use case>" \
  --impact "Forced to use settings.local.json override repeatedly; drift risk" \
  --fix-type config \
  --fix-desc "Revise workspace-permissions-templates.json: remove or narrow the deny on <path> for <workspace>" \
  --fix-components "workspace-permissions-templates.json, sync-permissions.py"
```

Skill Hub revises the templates, runs `sync-permissions.py --execute`, and commits the change. Your local override becomes unnecessary -- delete it once the templates change ships.

---

## Important Reminders

- The global `~/.claude/settings.json` and global `~/.claude/settings.local.json` are themselves DENIED for editing by every workspace (per `global_permissions.deny_additions`). Do not attempt to override at the global level -- this is intentional. Workspace-level `settings.local.json` is the only emergency lever.
- The workspace `settings.json` files (e.g., `<HQ>/.claude/settings.json`) are also denied for direct editing. The templates JSON + `sync-permissions.py` is the authoritative path. `settings.local.json` (with the `.local` suffix) is the override file you may edit.
- If you find this procedure even slightly confusing in the moment, that's a signal it should not be used in the moment. Stop, route the work, and let Skill Hub handle the templates revision.

## See Also

- `~/.claude/docs/permissions-architecture.md` -- two-layer model, deny precedence, per-workspace deny lists, "Adding a new global path" walkthrough.
- `~/.claude/docs/inbox-amendment-protocol.md` -- amend filed inbox items via CLI when direct Edit is denied.
- `~/.claude/rules/universal-protocols.md` -- workspace ownership, cross-workspace coordination protocols.
