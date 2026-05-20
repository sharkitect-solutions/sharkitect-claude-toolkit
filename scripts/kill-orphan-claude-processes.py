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
from datetime import datetime, timedelta, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
LOG_FILE = Path.home() / ".claude" / ".tmp" / "orphan-kill-log.jsonl"

# Operator-authorized kill flow (spec-orphan-cleanup-heartbeat.md v1.0, 2026-05-20).
# --report-only writes detection reports here without killing. --from-report
# reads a specific report and kills only PIDs still eligible at execute time.
REPORT_DIR = Path.home() / ".claude" / ".tmp" / "orphan-cleanup-reports"
REPORT_ARCHIVE_DIR = REPORT_DIR / "archive"
REPORT_STALE_DAYS = 14

# Suppress console window when spawned from pythonw.exe (GUI subsystem).
# Without this flag, every child process (wmic, taskkill) allocates a new
# console window = visible flash. Cross-platform safe (no-op on non-Windows).
# Source: wr-sentinel-2026-05-11-002 (CREATE_NO_WINDOW regression fix).
CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0


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


CASCADE_KILLED_MARKERS = (
    "no running instance",
    "not found",
    "process not running",
    "not running",
)


def kill_pid(pid: int) -> tuple[str, str]:
    """Force-kill a process by PID. Returns (status, message).

    status is one of:
      - 'killed':         taskkill succeeded (rc=0)
      - 'cascade_killed': PID already dead (Windows cascade-killed it via
                          process-tree / job-object semantics when its
                          parent/sibling claude.exe was taskkilled)
      - 'failed':         genuine failure (timeout, missing taskkill, other)

    Cascade-killed is NOT a failure: it's the normal Windows behavior where
    one taskkill /F on claude.exe brings down its child claude.exe processes
    via job-object membership. Logging these as 'failed' inflates the failure
    count and triggers false drift signals in Sentinel cross-workspace audits.
    Source: wr-sentinel-2026-05-17-001 (Sentinel analysis after S39 empirical
    verification: 1 success + 12 cascade-kills from a single taskkill).
    """
    try:
        result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/F"],
            capture_output=True, text=True, timeout=10,
            creationflags=CREATE_NO_WINDOW,
        )
        if result.returncode == 0:
            return "killed", result.stdout.strip()
        stderr_lower = (result.stderr or "").lower()
        if any(marker in stderr_lower for marker in CASCADE_KILLED_MARKERS):
            return "cascade_killed", result.stderr.strip()
        return "failed", result.stderr.strip() or f"exit {result.returncode}"
    except subprocess.TimeoutExpired:
        return "failed", "taskkill timed out after 10s"
    except FileNotFoundError:
        return "failed", "taskkill not found (Windows-only script)"
    except Exception as e:
        return "failed", f"{type(e).__name__}: {e}"


def log_kill(entries: list):
    """Append kill records to log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def _classify_for_kill(threshold_hours):
    """Helper used by both the legacy interactive flow and the new report flows.

    Returns (classify_report, current_session_pid).
    Importable seam for tests; production path calls the real check module.
    """
    check_mod = load_check_module()
    procs = check_mod.get_claude_processes()
    current_pid = check_mod.find_session_pid()
    report = check_mod.classify_processes(procs, current_pid, threshold_hours)
    return report, current_pid


def run_report_only(threshold_hours):
    """Detect-only mode: classify, write a report file, kill nothing.

    Exits 0 regardless of how many candidates are found (detection != verdict).
    Spec-orphan-cleanup-heartbeat.md section 7.1.
    """
    classify_report, _current_pid = _classify_for_kill(threshold_hours)
    suspects = classify_report.get("orphan_suspects", [])

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    report_id = "report-" + now.strftime("%Y-%m-%d-%H-%M-%S")
    report_path = REPORT_DIR / f"{report_id}.json"
    report_doc = {
        "report_id": report_id,
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "generator": "kill-orphan-claude-processes.py --report-only",
        "threshold_hours": threshold_hours,
        "candidates": [
            {
                "pid": s["pid"],
                "age_hours": s["age_hours"],
                "working_set_mb": s.get("mb"),
                "created_at": s.get("created_at"),
                "evidence": {
                    "heartbeat": "missing_or_stale",
                    "vscode_ancestor": "not_found",
                    "registry_entry": "absent_or_dead_parent",
                    "current_session_match": False,
                },
            }
            for s in suspects
        ],
        "protected_count": len(classify_report.get("protected", [])),
        "recent_count": len(classify_report.get("recent", [])),
        "total_claude_processes": classify_report.get("total", 0),
        "status": "pending_operator_review",
    }
    # Atomic write
    tmp = report_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(report_doc, indent=2), encoding="utf-8")
    tmp.replace(report_path)
    return 0


def run_from_report(report_path, threshold_hours):
    """Operator-authorized kill flow: re-classify report's candidates at execute time
    and kill only PIDs still eligible. PIDs that recovered protection (e.g. fresh
    heartbeat written after report generation) are skipped and annotated.

    Spec-orphan-cleanup-heartbeat.md section 7.2.
    """
    try:
        report_doc = json.loads(report_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: cannot load report {report_path}: {e}", file=sys.stderr)
        return 1

    candidates = report_doc.get("candidates", [])
    if not candidates:
        report_doc["status"] = "executed"
        report_doc["executed_at"] = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        report_path.write_text(json.dumps(report_doc, indent=2), encoding="utf-8")
        return 0

    # Re-classify with current state
    classify_report, _current = _classify_for_kill(threshold_hours)
    eligible_pids = {s["pid"] for s in classify_report.get("orphan_suspects", [])}

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    log_entries = []
    for c in candidates:
        pid = c.get("pid")
        if pid not in eligible_pids:
            c["result"] = "protection_recovered"
            c["resolved_at"] = now_iso
            continue
        status, msg = kill_pid(pid)
        c["result"] = status
        c["message"] = msg
        c["resolved_at"] = now_iso
        log_entries.append({
            "timestamp": now_iso,
            "pid": pid,
            "age_hours": c.get("age_hours"),
            "result": status,
            "message": msg,
            "from_report": report_doc.get("report_id"),
        })

    if log_entries:
        log_kill(log_entries)
    report_doc["status"] = "executed"
    report_doc["executed_at"] = now_iso
    report_path.write_text(json.dumps(report_doc, indent=2), encoding="utf-8")
    return 0


def archive_stale_reports():
    """Move reports older than REPORT_STALE_DAYS with status=pending_operator_review
    AND no current-eligible candidates into REPORT_ARCHIVE_DIR.

    Spec-orphan-cleanup-heartbeat.md section 7.3 final paragraph.
    """
    if not REPORT_DIR.exists():
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=REPORT_STALE_DAYS)
    # Cache classifier output across all archive checks in this run.
    classify_cache = None
    for report_path in REPORT_DIR.glob("report-*.json"):
        try:
            mtime = datetime.fromtimestamp(report_path.stat().st_mtime, tz=timezone.utc)
            if mtime >= cutoff:
                continue
            doc = json.loads(report_path.read_text(encoding="utf-8"))
            if doc.get("status") != "pending_operator_review":
                continue
            if classify_cache is None:
                classify_report, _ = _classify_for_kill(doc.get("threshold_hours", 8.0))
                classify_cache = {s["pid"] for s in classify_report.get("orphan_suspects", [])}
            candidate_pids = {c.get("pid") for c in doc.get("candidates", [])}
            if candidate_pids & classify_cache:
                # Still actionable -- leave alone
                continue
            REPORT_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            report_path.replace(REPORT_ARCHIVE_DIR / report_path.name)
        except (OSError, json.JSONDecodeError):
            continue


def main():
    desc = (__doc__ or "Kill orphan Claude processes.").split("\n\n")[0]
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("--threshold-hours", type=float, default=8.0,
                   help="Kill processes older than this (default: 8h, "
                        "raised from 4h by spec-orphan-cleanup-heartbeat.md 2026-05-20)")
    p.add_argument("--execute", action="store_true",
                   help="Actually kill (default is dry-run, prints what WOULD be killed)")
    p.add_argument("--report-only", action="store_true",
                   help="Detection-only mode: classify, write a JSON report under "
                        f"{REPORT_DIR}, kill nothing. Recommended cron mode.")
    p.add_argument("--from-report", type=str, default=None, metavar="PATH",
                   help="Operator-authorized kill flow: re-classify candidates in "
                        "the named report and kill only PIDs still eligible.")
    p.add_argument("--show-report", type=str, default=None, metavar="PATH",
                   help="Print the contents of a report without killing or modifying.")
    p.add_argument("--force", action="store_true",
                   help="Allow killing even when current session PID can't be identified "
                        "(unsafe). Default refuses to kill if current PID is unknown.")
    p.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = p.parse_args()

    # New report-flow branches dispatch first; legacy interactive flow follows below.
    if args.report_only:
        archive_stale_reports()
        return run_report_only(args.threshold_hours)
    if args.show_report:
        path = Path(args.show_report)
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"ERROR: cannot read report {path}: {e}", file=sys.stderr)
            return 1
        print(json.dumps(doc, indent=2))
        return 0
    if args.from_report:
        path = Path(args.from_report)
        if not path.exists():
            print(f"ERROR: report not found: {path}", file=sys.stderr)
            return 1
        if not args.execute:
            print(f"REFUSING: --from-report requires --execute. (dry-run not supported "
                  f"on report-driven flow; the report itself IS the dry-run record.)",
                  file=sys.stderr)
            return 2
        return run_from_report(path, args.threshold_hours)

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
    killed = cascade_killed = failed = 0
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    status_markers = {"killed": "OK", "cascade_killed": "CASCADE", "failed": "FAIL"}
    for o in report["orphan_suspects"]:
        if o["pid"] == current_pid:
            print(f"  SKIP PID {o['pid']} (current session)")
            continue
        status, msg = kill_pid(o["pid"])
        marker = status_markers.get(status, "FAIL")
        print(f"  {marker} PID {o['pid']} (age {o['age_hours']}h): {msg}")
        log_entries.append({
            "timestamp": now_iso,
            "pid": o["pid"],
            "age_hours": o["age_hours"],
            "mb": o["mb"],
            "result": status,
            "message": msg,
        })
        if status == "killed":
            killed += 1
        elif status == "cascade_killed":
            cascade_killed += 1
        else:
            failed += 1

    log_kill(log_entries)
    print()
    print(f"Killed {killed}, Cascade-killed {cascade_killed}, Failed {failed}. Log: {LOG_FILE}")
    return 0 if failed == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
