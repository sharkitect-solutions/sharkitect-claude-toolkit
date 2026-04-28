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
