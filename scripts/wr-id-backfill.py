#!/usr/bin/env python3
"""wr-id-backfill.py -- Fill MISSING id field on legacy WR JSONs.

NEVER rewrites existing ids (v1 stays v1 forever). Only fills `id` when
absent. Idempotent. Defaults to --dry-run.

Why: pre-v2 work-request.py emitted JSON without a top-level `id` field.
close-inbox-item.py historically derived an id from the filename, which
collided with unrelated WR ids and produced wrong-row Supabase updates
(2026-04-25 batch close lost 11 records' resolution_summary text into
wrong rows). v2 schema requires explicit `id` field; this script
backfills missing ids on legacy files without touching existing ones.

Source: wr-2026-04-25-007 Task 5/8.
Spec: 3.- Skill Management Hub/docs/superpowers/specs/2026-04-27-wr-id-schema-workspace-prefixed-design.md
Plan: ~/.claude/plans/2026-04-27-wr-id-schema-workspace-prefixed.md

Usage:
    python wr-id-backfill.py                       # dry-run all 3 workspaces
    python wr-id-backfill.py --apply               # apply
    python wr-id-backfill.py --apply --workspace skill-management-hub
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WORKSPACE_SHORT = {
    "workforce-hq": "hq",
    "skill-management-hub": "skillhub",
    "sentinel": "sentinel",
}
WORKSPACE_DIRS = {
    "workforce-hq": "1.- SHARKITECT DIGITAL WORKFORCE HQ",
    "skill-management-hub": "3.- Skill Management Hub",
    "sentinel": "4.- Sentinel",
}

ID_RE_V2 = re.compile(r"^wr-(hq|skillhub|sentinel)-\d{4}-\d{2}-\d{2}-\d{3}$")
ID_RE_V1 = re.compile(r"^wr-\d{4}-\d{2}-\d{2}-\d{3}$")
# Pre-rename legacy: many 2026-04-08..2026-04-17 files used 'gap-' prefix
# before the gap->WR vocabulary unification. These are full Supabase records
# keyed by their gap-* id strings -- treat as valid legacy, never rewrite.
ID_RE_LEGACY_GAP = re.compile(r"^gap-\d{4}-\d{2}-\d{2}-\d{3}$")
# Matches: 2026-04-22_skill-management-hub_some-slug-words-001.json
FILENAME_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})_(?P<ws>[a-z\-]+)_.+-(?P<nnn>\d{3})\.json$"
)
WORKSPACES_BASE = Path(
    "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces"
)


def derive_id_from_filename(p: Path, source_workspace: str) -> str | None:
    """Derive a v2-style id from filename + source_workspace.

    Returns wr-<short>-YYYY-MM-DD-NNN, or None if filename pattern unmatched.
    """
    m = FILENAME_RE.match(p.name)
    if not m:
        return None
    date = m.group("date")
    nnn = m.group("nnn")
    short = WORKSPACE_SHORT.get(source_workspace)
    if not short:
        return None
    return f"wr-{short}-{date}-{nnn}"


def process_file(p: Path, apply_changes: bool) -> str | None:
    """Return a status string if any action/review needed; None if file is clean."""
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
        return f"  SKIP (unreadable): {p.name} -- {e}"

    # Out-of-scope: routed-task completion notifications (RT identifiers,
    # different schema). They use task_id not id and live by RT conventions.
    if p.name.startswith("rt-") or data.get("kind") == "completion_notification":
        return None

    wr_id = data.get("id")
    # Has any valid id? Leave it alone. v1, v2, and pre-rename gap-* all count.
    if wr_id and (
        ID_RE_V2.match(str(wr_id))
        or ID_RE_V1.match(str(wr_id))
        or ID_RE_LEGACY_GAP.match(str(wr_id))
    ):
        return None
    # Has a malformed id? Flag, don't overwrite.
    if wr_id:
        return f"  REVIEW (malformed id): {p.name} -- id={wr_id!r}"
    # No id: derive from filename
    derived = derive_id_from_filename(p, str(data.get("source_workspace", "")))
    if not derived:
        return (
            f"  REVIEW (cannot derive): {p.name} -- "
            f"source_workspace={data.get('source_workspace')!r}"
        )
    if not apply_changes:
        return f"  WOULD-FILL: {p.name} -> id={derived}"
    data["id"] = derived
    data["id_backfilled"] = True
    p.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return f"  FILLED: {p.name} -> id={derived}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="Apply changes. Default is dry-run.")
    ap.add_argument("--workspace", choices=sorted(WORKSPACE_DIRS.keys()),
                    help="Limit to one workspace. Default: all 3.")
    ap.add_argument("--base", type=Path, default=WORKSPACES_BASE,
                    help="Override workspaces base dir (testing).")
    args = ap.parse_args()

    targets = [args.workspace] if args.workspace else list(WORKSPACE_DIRS.keys())
    total_scanned = 0
    total_actions = 0

    for ws in targets:
        ws_dir = args.base / WORKSPACE_DIRS[ws]
        if not ws_dir.exists():
            print(f"=== {ws} (SKIPPED: workspace dir not found at {ws_dir}) ===")
            continue
        for sub in ("inbox", "processed", "outbox"):
            d = ws_dir / ".work-requests" / sub
            if not d.exists():
                continue
            print(f"=== {ws} / .work-requests/{sub} ===")
            for f in sorted(d.glob("*.json")):
                total_scanned += 1
                msg = process_file(f, args.apply)
                if msg:
                    print(msg)
                    total_actions += 1

    mode = "APPLIED" if args.apply else "DRY-RUN (use --apply to fill)"
    print(f"\nFiles scanned: {total_scanned}. Actions: {total_actions}. {mode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
