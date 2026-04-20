"""
check-orphan-claude-processes.py -- Detect orphan claude.exe processes (Windows)

Filed by: HQ wr-2026-04-19_workforce-hq_orphan-claude-processes-hold-rogue-crons
Root cause: When a Claude session ends abnormally (window closed, crash, sleep),
claude.exe can survive in background. Any CronCreate job in that orphan's memory
keeps firing on schedule with no user attached, so mode-detection always reads
IDLE and processing happens autonomously without visibility.

What this does (READ-ONLY):
  - Lists all claude.exe processes via tasklist + wmic
  - Computes age of each (CreationDate -> minutes ago)
  - Marks any process older than --threshold-hours as a suspect orphan
  - Excludes the current process (and its parent) from suspect list
  - Outputs JSON or text report (or, when called from session-startup-guard,
    a one-line summary)

This script does NOT kill anything. Use kill-orphan-claude-processes.py for that
(separate script so detection and destruction are different actions).

Usage:
    python ~/.claude/scripts/check-orphan-claude-processes.py
    python ~/.claude/scripts/check-orphan-claude-processes.py --json
    python ~/.claude/scripts/check-orphan-claude-processes.py --threshold-hours 4
    python ~/.claude/scripts/check-orphan-claude-processes.py --summary

Dependencies: Python stdlib + Windows tasklist/wmic (Windows-only).
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone


def get_claude_processes():
    """
    Returns list of dicts: {pid, created_at (datetime), working_set_bytes}
    Uses wmic which is more reliable than tasklist for creation timestamp.
    """
    try:
        out = subprocess.check_output(
            ["wmic", "process", "where", "name='claude.exe'",
             "get", "ProcessId,CreationDate,WorkingSetSize", "/format:csv"],
            stderr=subprocess.DEVNULL, text=True, timeout=10,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return []

    procs = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("Node") or "CreationDate" in line:
            continue
        parts = line.split(",")
        if len(parts) < 4:
            continue
        # CSV order: Node,CreationDate,ProcessId,WorkingSetSize
        try:
            created_raw = parts[1].strip()
            pid = int(parts[2].strip())
            ws = int(parts[3].strip()) if parts[3].strip() else 0
        except (ValueError, IndexError):
            continue
        # Parse wmic timestamp: 20260419104551.641162-300
        m = re.match(r"^(\d{14})\.\d+([+-]\d+)$", created_raw)
        if not m:
            continue
        ts_part, tz_part = m.groups()
        try:
            naive = datetime.strptime(ts_part, "%Y%m%d%H%M%S")
            tz_minutes = int(tz_part)
            tz = timezone(timedelta(minutes=tz_minutes))
            created = naive.replace(tzinfo=tz)
        except ValueError:
            continue
        procs.append({
            "pid": pid,
            "created_at": created,
            "working_set_bytes": ws,
        })
    return procs


def classify_processes(procs, current_pid, threshold_hours):
    """
    Returns dict with keys: total, current, recent, orphan_suspects.
    orphan_suspects = list of {pid, age_hours, mb}, sorted oldest-first.
    """
    now = datetime.now(timezone.utc)
    orphan = []
    recent = []
    current_proc = None
    for p in procs:
        age = now - p["created_at"]
        info = {
            "pid": p["pid"],
            "age_hours": round(age.total_seconds() / 3600, 1),
            "mb": round(p["working_set_bytes"] / (1024 * 1024), 0),
            "created_at": p["created_at"].isoformat(),
        }
        if p["pid"] == current_pid:
            current_proc = info
            continue
        if age >= timedelta(hours=threshold_hours):
            orphan.append(info)
        else:
            recent.append(info)
    orphan.sort(key=lambda x: -x["age_hours"])
    return {
        "total": len(procs),
        "threshold_hours": threshold_hours,
        "current": current_proc,
        "recent": recent,
        "orphan_suspects": orphan,
    }


def find_session_pid():
    """
    Walk up parent processes from this script to find the claude.exe ancestor.
    Returns PID or None. Best-effort -- safety net is "don't kill what we can't id."
    """
    try:
        out = subprocess.check_output(
            ["wmic", "process", "where", f"ProcessId={os.getpid()}",
             "get", "ParentProcessId", "/format:csv"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        )
    except Exception:
        return None
    parent_pid = None
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("Node") or "ParentProcessId" in line:
            continue
        parts = line.split(",")
        if len(parts) >= 2:
            try:
                parent_pid = int(parts[1].strip())
            except ValueError:
                pass
    if not parent_pid:
        return None
    # Walk up until we find claude.exe or hit ancestor limit
    pid = parent_pid
    for _ in range(10):
        try:
            out = subprocess.check_output(
                ["wmic", "process", "where", f"ProcessId={pid}",
                 "get", "Name,ParentProcessId", "/format:csv"],
                stderr=subprocess.DEVNULL, text=True, timeout=5,
            )
        except Exception:
            return None
        name = None
        next_pid = None
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("Node") or "Name" in line:
                continue
            parts = line.split(",")
            if len(parts) >= 3:
                name = parts[1].strip().lower()
                try:
                    next_pid = int(parts[2].strip())
                except ValueError:
                    next_pid = None
        if name == "claude.exe":
            return pid
        if not next_pid or next_pid == pid:
            return None
        pid = next_pid
    return None


def main():
    desc = (__doc__ or "Check orphan Claude processes.").split("\n\n")[0]
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("--threshold-hours", type=float, default=4.0,
                   help="Process older than this is a suspect orphan (default: 4)")
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.add_argument("--summary", action="store_true",
                   help="One-line summary for session-startup-guard")
    args = p.parse_args()

    procs = get_claude_processes()
    current_pid = find_session_pid()
    report = classify_processes(procs, current_pid, args.threshold_hours)
    report["current_session_pid"] = current_pid

    if args.summary:
        n = len(report["orphan_suspects"])
        if n == 0:
            print(f"Orphan check: 0 (total {report['total']} claude.exe processes)")
        else:
            oldest = report["orphan_suspects"][0]
            print(f"Orphan check: {n} suspect (oldest {oldest['age_hours']}h "
                  f"PID {oldest['pid']}). Run "
                  f"`python ~/.claude/scripts/kill-orphan-claude-processes.py` to terminate.")
        return 0

    if args.json:
        print(json.dumps(report, indent=2, default=str))
        return 0

    # Plain text
    print(f"=== Claude Process Check ===")
    print(f"Total claude.exe processes: {report['total']}")
    print(f"Current session PID: {current_pid or '(unknown)'}")
    print(f"Threshold for orphan: {args.threshold_hours}h")
    print()
    if report["orphan_suspects"]:
        print(f"Suspect orphans ({len(report['orphan_suspects'])}):")
        for o in report["orphan_suspects"]:
            print(f"  PID {o['pid']}  age {o['age_hours']:>6}h  mem {o['mb']:>6.0f}MB  started {o['created_at']}")
    else:
        print("No suspect orphans detected.")
    if report["recent"]:
        print()
        print(f"Recent processes ({len(report['recent'])}):")
        for r in report["recent"]:
            print(f"  PID {r['pid']}  age {r['age_hours']:>6}h  mem {r['mb']:>6.0f}MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
