#!/usr/bin/env python3
"""Restore ~/.claude/settings.json from a templated toolkit backup.

Companion to tools/sync-skills.py settings_sync(). The toolkit's
settings-backup.json holds {HOME}-templated paths (no hardcoded user dir,
no platform-specific separators). This script expands the template for the
running platform and writes the result to ~/.claude/settings.json.

Used during fresh-machine setup and disaster recovery. Safe to run repeatedly:
takes a timestamped backup of the existing live file before overwriting.

Usage:
    python ~/.claude/scripts/restore-settings.py            # use default toolkit path
    python ~/.claude/scripts/restore-settings.py --backup PATH/settings-backup.json
    python ~/.claude/scripts/restore-settings.py --dry-run  # preview, don't write
    python ~/.claude/scripts/restore-settings.py --target /tmp/test-settings.json
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import shutil
import sys
import time
from pathlib import Path


def _load_sync_module():
    """Locate and import tools/sync-skills.py for templatize/detemplatize helpers."""
    candidates = [
        Path.home() / "Documents" / "Claude Code Workspaces" / "3.- Skill Management Hub" / "tools" / "sync-skills.py",
        Path.cwd() / "tools" / "sync-skills.py",
        Path.home() / ".claude" / "tools" / "sync-skills.py",
    ]
    for p in candidates:
        if p.exists():
            spec = importlib.util.spec_from_file_location("sync_skills_runtime", p)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod, p
    raise FileNotFoundError(
        "Could not locate sync-skills.py. Searched:\n  " + "\n  ".join(str(c) for c in candidates)
    )


def _default_backup_path():
    """Default toolkit settings-backup.json (Skill Hub clone)."""
    return (
        Path.home() / "Documents" / "Claude Code Workspaces" / "3.- Skill Management Hub"
        / "sharkitect-claude-toolkit" / "settings-backup.json"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--backup", type=Path, default=None,
                        help="Path to templated settings-backup.json (default: toolkit clone in Skill Hub)")
    parser.add_argument("--target", type=Path, default=Path.home() / ".claude" / "settings.json",
                        help="Where to write the restored file (default: ~/.claude/settings.json)")
    parser.add_argument("--platform", default=sys.platform, choices=["win32", "linux", "darwin"],
                        help="Target platform (default: current sys.platform)")
    parser.add_argument("--home", default=str(Path.home()),
                        help="Target home directory to substitute for {HOME} (default: current Path.home())")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print restored content to stdout without writing")
    args = parser.parse_args(argv)

    sync_mod, sync_path = _load_sync_module()

    backup = args.backup or _default_backup_path()
    if not backup.exists():
        print(f"ERROR: backup file not found: {backup}", file=sys.stderr)
        return 2

    templated = backup.read_text(encoding="utf-8")
    if "{HOME}" not in templated:
        print(f"WARNING: {backup} does not contain {{HOME}} sentinel — using as-is.", file=sys.stderr)

    restored = sync_mod.detemplatize_settings(templated, args.home, target_platform=args.platform)
    try:
        json.loads(restored)
    except json.JSONDecodeError as e:
        print(f"ERROR: restored content is not valid JSON: {e}", file=sys.stderr)
        return 3

    if args.dry_run:
        print(restored)
        return 0

    target = args.target
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        ts = time.strftime("%Y%m%d-%H%M%S")
        backup_existing = target.with_suffix(target.suffix + f".pre-restore.{ts}")
        shutil.copy2(target, backup_existing)
        print(f"Backed up existing settings to: {backup_existing}")

    target.write_text(restored, encoding="utf-8")
    print(f"Restored {target}")
    print(f"  source:    {backup}")
    print(f"  helpers:   {sync_path}")
    print(f"  platform:  {args.platform}")
    print(f"  home:      {args.home}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
