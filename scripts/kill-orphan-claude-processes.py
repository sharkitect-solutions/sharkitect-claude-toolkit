"""
kill-orphan-claude-processes.py -- Terminate orphan claude.exe processes (Windows)

Filed by: HQ wr-2026-04-19_workforce-hq_orphan-claude-processes-hold-rogue-crons
Companion to check-orphan-claude-processes.py. Detection and destruction are
deliberately split so killing is always an explicit action.

What it does:
  - Calls check-orphan-claude-processes.py to identify suspect orphans
  - Excludes the current session's claude.exe ancestor (multiple safety checks)
  - Requires --execute to actually kill (default is DRY-RUN)
  - Uses taskkill /PID /F (force terminate) -- orphan crons are non-graceful by
    nature, so graceful shutdown isn't possible
  - Logs every kill to ~/.claude/.tmp/orphan-kill-log.jsonl

Safety:
  - Default is dry-run; nothing is killed unless --execute is passed
  - Refuses to kill the current session's PID
  - Refuses to run if it can't identify the current session PID (unless
    --force is also passed)
  - Threshold defaults to 4 hours; can be raised with --threshold-hours

Usage:
    python ~/.claude/scripts/kill-orphan-claude-processes.py
    python ~/.claude/scripts/kill-orphan-claude-processes.py --execute
    python ~/.claude/scripts/kill-orphan-claude-processes.py --execute --threshold-hours 1

Dependencies: Python stdlib + Windows taskkill (Windows-only).
"""

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
LOG_FILE = Path.home() / ".claude" / ".tmp" / "orphan-kill-log.jsonl"


def load_check_module():
    """Import check-orphan-claude-processes.py as a module."""
    check_path = SCRIPT_DIR / "check-orphan-claude-processes.py"
    if not check_path.exists():
        raise FileNotFoundError(f"Companion script not found: {check_path}")
    spec = importlib.util.spec_from_file_location("check_orphan", check_path)
    if not spec or not spec.loader:
        raise ImportError("Could not load check-orphan-claude-processes.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def kill_pid(pid: int) -> tuple[bool, str]:
    """Force-kill a process by PID. Returns (success, message)."""
    try:
        result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/F"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip() or f"exit {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "taskkill timed out after 10s"
    except FileNotFoundError:
        return False, "taskkill not found (Windows-only script)"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def log_kill(entries: list):
    """Append kill records to log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def main():
    desc = (__doc__ or "Kill orphan Claude processes.").split("\n\n")[0]
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("--threshold-hours", type=float, default=4.0,
                   help="Kill processes older than this (default: 4h)")
    p.add_argument("--execute", action="store_true",
                   help="Actually kill (default is dry-run, prints what WOULD be killed)")
    p.add_argument("--force", action="store_true",
                   help="Allow killing even when current session PID can't be identified "
                        "(unsafe). Default refuses to kill if current PID is unknown.")
    p.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = p.parse_args()

    try:
        check_mod = load_check_module()
    except (FileNotFoundError, ImportError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    procs = check_mod.get_claude_processes()
    current_pid = check_mod.find_session_pid()
    report = check_mod.classify_processes(procs, current_pid, args.threshold_hours)

    if not report["orphan_suspects"]:
        if not args.quiet:
            print(f"No orphan claude.exe processes (>={args.threshold_hours}h) detected.")
        return 0

    if not current_pid and not args.force:
        print(f"REFUSING to kill: cannot identify current session PID.", file=sys.stderr)
        print(f"  This is a safety check to prevent killing the active Claude session.", file=sys.stderr)
        print(f"  Use --force to override (DANGEROUS).", file=sys.stderr)
        return 2

    n = len(report["orphan_suspects"])
    print(f"Suspect orphans: {n} (threshold {args.threshold_hours}h, current PID {current_pid or '?'})")
    for o in report["orphan_suspects"]:
        print(f"  PID {o['pid']}  age {o['age_hours']:>6}h  mem {o['mb']:>6.0f}MB")

    if not args.execute:
        print()
        print(f"DRY-RUN: would kill {n} processes. Re-run with --execute to actually terminate.")
        return 0

    print()
    print(f"Executing taskkill on {n} processes...")
    log_entries = []
    killed = failed = 0
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    for o in report["orphan_suspects"]:
        if o["pid"] == current_pid:
            print(f"  SKIP PID {o['pid']} (current session)")
            continue
        ok, msg = kill_pid(o["pid"])
        marker = "OK" if ok else "FAIL"
        print(f"  {marker} PID {o['pid']} (age {o['age_hours']}h): {msg}")
        log_entries.append({
            "timestamp": now_iso,
            "pid": o["pid"],
            "age_hours": o["age_hours"],
            "mb": o["mb"],
            "result": "killed" if ok else "failed",
            "message": msg,
        })
        if ok:
            killed += 1
        else:
            failed += 1

    log_kill(log_entries)
    print()
    print(f"Killed {killed}, Failed {failed}. Log: {LOG_FILE}")
    return 0 if failed == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
