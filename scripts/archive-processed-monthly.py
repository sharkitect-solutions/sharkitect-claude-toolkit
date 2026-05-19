#!/usr/bin/env python
"""archive-processed-monthly.py -- GLOBAL folder-hygiene tool.

Move prior-month processed inbox items into structured monthly archive folders.
Designed to run from Windows Task Scheduler on a monthly cadence per workspace.

SOURCES (relative to each workspace root, skipped if missing):
  .routed-tasks/processed/*.json
  .lifecycle-reviews/processed/*.json
  .work-requests/processed/*.json

DESTINATION (relative to workspace root):
  _archive/processed-inbox/routed-tasks/YYYY-MM/
  _archive/processed-inbox/lifecycle-reviews/YYYY-MM/
  _archive/processed-inbox/work-requests/YYYY-MM/

Month bucket is derived from each file's mtime (when it was moved to processed/).
The current month is always skipped -- only completed months get archived. This
makes the live processed/ folder a rolling window of recent activity.

Usage:
    python ~/.claude/scripts/archive-processed-monthly.py --workspace-root PATH
                                                          [--dry-run] [--cutoff YYYY-MM]

Source: wr-sentinel-2026-05-19-004. Promoted from HQ-local
(1.- SHARKITECT DIGITAL WORKFORCE HQ/tools/archive-processed-monthly.py) to
global per operator directive 2026-05-19: "build that not only for you but
also for skilled management hub as well, so that it's a global thing that
every workspace has." Ships with AIOS.

Exit codes:
    0 -- clean run (zero or more files moved)
    1 -- fatal error (workspace root missing, --workspace-root not given, etc.)
"""
from __future__ import annotations
import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

SOURCES = [
    (".routed-tasks/processed", "routed-tasks"),
    (".lifecycle-reviews/processed", "lifecycle-reviews"),
    (".work-requests/processed", "work-requests"),
]
ARCHIVE_BASE = "_archive/processed-inbox"


def parse_args():
    p = argparse.ArgumentParser(description="Monthly archive of processed inbox items (global).")
    p.add_argument("--workspace-root", type=Path, required=True,
                   help="Absolute path to the workspace root to clean up.")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--cutoff", default=None,
                   help="YYYY-MM. Files with mtime in months strictly before this are archived. "
                        "Default = current month.")
    return p.parse_args()


def first_day_of_month(year: int, month: int) -> dt.datetime:
    return dt.datetime(year, month, 1, tzinfo=dt.timezone.utc)


def resolve_cutoff(cutoff_arg: str | None) -> dt.datetime:
    if cutoff_arg:
        try:
            year, month = map(int, cutoff_arg.split("-"))
        except ValueError:
            raise SystemExit(f"--cutoff must be YYYY-MM, got: {cutoff_arg}")
        return first_day_of_month(year, month)
    today = dt.datetime.now(dt.timezone.utc)
    return first_day_of_month(today.year, today.month)


def file_month_bucket(path: Path) -> str:
    mt = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc)
    return f"{mt.year:04d}-{mt.month:02d}"


def setup_dual_output(log_path: Path):
    """Tee stdout to a log file so pythonw.exe (silent, no console) runs leave a trail."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = open(log_path, "a", encoding="utf-8")

    real_stdout = sys.__stdout__  # may be None under pythonw.exe

    class Tee:
        def write(self, s):
            log_handle.write(s)
            log_handle.flush()
            if real_stdout is not None:
                try:
                    real_stdout.write(s)
                except Exception:
                    pass

        def flush(self):
            log_handle.flush()

    sys.stdout = Tee()
    sys.stderr = Tee()


def main() -> int:
    args = parse_args()
    root = args.workspace_root.resolve()

    if not root.exists():
        print(f"ERROR: workspace root does not exist: {root}", file=sys.stderr)
        return 1

    log_path = root / ".tmp" / "archive-processed-monthly.log"
    setup_dual_output(log_path)

    cutoff = resolve_cutoff(args.cutoff)
    print(f"\n=== Archive monthly run @ {dt.datetime.now(dt.timezone.utc).isoformat()} ===")
    print(f"Workspace: {root}")
    print(f"Cutoff: files with mtime < {cutoff.isoformat()} (i.e. before that month)")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("-" * 60)

    archive_base = root / ARCHIVE_BASE
    total_moved = 0
    total_skipped = 0

    for src_rel, dest_subname in SOURCES:
        src_dir = root / src_rel
        if not src_dir.exists():
            print(f"  [skip] source missing: {src_rel}")
            continue

        files = [p for p in src_dir.iterdir()
                 if p.is_file() and not p.name.startswith(".")]
        if not files:
            print(f"  [empty] {src_rel}")
            continue

        moved_here = 0
        skipped_here = 0
        for f in files:
            mt = dt.datetime.fromtimestamp(f.stat().st_mtime, tz=dt.timezone.utc)
            if mt >= cutoff:
                skipped_here += 1
                continue
            bucket = file_month_bucket(f)
            dest_dir = archive_base / dest_subname / bucket
            dest_path = dest_dir / f.name

            if args.dry_run:
                print(f"  [DRY] would move: {src_rel}/{f.name} -> {ARCHIVE_BASE}/{dest_subname}/{bucket}/")
            else:
                dest_dir.mkdir(parents=True, exist_ok=True)
                if dest_path.exists():
                    print(f"  [WARN] dest exists, skipping: {dest_path}")
                    skipped_here += 1
                    continue
                shutil.move(str(f), str(dest_path))
                print(f"  [MOVE] {src_rel}/{f.name} -> {dest_subname}/{bucket}/")

            moved_here += 1

        print(f"  {src_rel}: {moved_here} archived, {skipped_here} kept (current month or skipped)")
        total_moved += moved_here
        total_skipped += skipped_here

    print("-" * 60)
    print(f"TOTAL: {total_moved} archived, {total_skipped} kept in live folders")
    return 0


if __name__ == "__main__":
    sys.exit(main())
