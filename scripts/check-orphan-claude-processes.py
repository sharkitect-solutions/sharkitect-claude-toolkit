"""
check-orphan-claude-processes.py -- Detect orphan claude.exe processes (Windows)

Filed by: HQ wr-2026-04-19_workforce-hq_orphan-claude-processes-hold-rogue-crons
Root cause: When a Claude session ends abnormally (window closed, crash, sleep),
claude.exe can survive in background. Any CronCreate job in that orphan's memory
keeps firing on schedule with no user attached, so mode-detection always reads
IDLE and processing happens autonomously without visibility.

Multi-signal detection added 2026-04-22 (wr-2026-04-22-012):
  Age-only detection killed 4 real active sessions across HQ/Sentinel/SkillHub
  when user kept multiple workspaces open overnight. True orphans are now
  distinguished from idle-but-real sessions using three signals:

    1. PRIMARY  -- VS Code ancestor check: real sessions have a live
                   Code.exe / Cursor.exe / Windsurf.exe / Code-Insiders ancestor
                   in the process tree. Orphans' VS Code parent is gone.

    2. BACKUP   -- active-sessions registry: the session-start-register-pid.py
                   SessionStart hook writes the session's PID + vscode_ppid to
                   ~/.claude/.tmp/active-sessions.json. Kill script reads this
                   and protects any registered PID whose vscode_ppid is alive.

    3. TERTIARY -- transcript-mtime is NOT used as a protection signal, because
                   CronCreate fires write to the transcript in both orphans and
                   real idle sessions (user pointed this out during design).

A claude.exe process is classified as TRUE ORPHAN only if ALL of:
  - age >= threshold_hours
  - not the current session PID
  - no live VS Code variant ancestor in its process tree
  - not in the active-sessions registry (or registered entry's vscode_ppid
    is no longer alive)

What this does (READ-ONLY):
  - Lists all claude.exe processes via tasklist + wmic
  - Computes age of each (CreationDate -> minutes ago)
  - Applies the multi-signal classifier described above
  - Outputs JSON or text report (or, when called from session-startup-guard,
    a one-line summary)

This script does NOT kill anything. Use kill-orphan-claude-processes.py for that
(separate script so detection and destruction are different actions).

Usage:
    python ~/.claude/scripts/check-orphan-claude-processes.py
    python ~/.claude/scripts/check-orphan-claude-processes.py --json
    python ~/.claude/scripts/check-orphan-claude-processes.py --threshold-hours 4
    python ~/.claude/scripts/check-orphan-claude-processes.py --summary
    python ~/.claude/scripts/check-orphan-claude-processes.py --show-protected

Dependencies: Python stdlib + Windows tasklist/wmic (Windows-only).
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


# VS Code variants that host Claude Code. A live parent of one of these names
# is a strong signal that claude.exe is a real session, not an orphan.
VSCODE_VARIANT_NAMES = frozenset({
    "code.exe",
    "code - insiders.exe",
    "cursor.exe",
    "windsurf.exe",
    "code-oss.exe",
    "codium.exe",
    "trae.exe",
    "antigravity.exe",      # Anthropic Antigravity IDE -- added 2026-04-22 after
                            # live-trace showed claude.exe's real parent chain
                            # terminates at Antigravity.exe (not Code.exe).
                            # Without this entry the ancestor-walk misses it
                            # and real sessions get misclassified as orphans.
})

# Maximum hops to walk up the process tree looking for a VS Code ancestor.
# Bounds pathological cycles and reparenting loops.
VSCODE_ANCESTOR_MAX_HOPS = 8

# Active-sessions registry path
REGISTRY_PATH = Path.home() / ".claude" / ".tmp" / "active-sessions.json"


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


def _wmic_get_name_and_ppid(pid):
    """Return (name_lower, ppid) for a PID, or (None, None) if not found.
    Pure stdlib wrapper around wmic.
    """
    try:
        out = subprocess.check_output(
            ["wmic", "process", "where", f"ProcessId={pid}",
             "get", "Name,ParentProcessId", "/format:csv"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        )
    except (subprocess.CalledProcessError, FileNotFoundError,
            subprocess.TimeoutExpired, OSError):
        return None, None
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("Node") or "Name" in line:
            continue
        parts = line.split(",")
        if len(parts) >= 3:
            name = parts[1].strip().lower() if parts[1].strip() else None
            try:
                ppid = int(parts[2].strip()) if parts[2].strip() else None
            except ValueError:
                ppid = None
            return name, ppid
    return None, None


def find_vscode_ancestor(start_pid, max_hops=VSCODE_ANCESTOR_MAX_HOPS, _lookup=None):
    """Walk up from start_pid looking for a live VS Code variant ancestor.

    Returns (ancestor_pid, ancestor_name_lower) if found, else (None, None).

    - Bounded by max_hops to prevent cycles / pathological trees.
    - If a PID lookup fails (process exited between our calls), we stop and
      return (None, None) conservatively.
    - _lookup is an injection point for testing (a callable taking pid,
      returning (name, ppid)). Defaults to the real wmic call.
    """
    lookup = _lookup or _wmic_get_name_and_ppid
    pid = start_pid
    seen = set()
    for _ in range(max_hops):
        if pid in seen or pid is None or pid == 0:
            return None, None
        seen.add(pid)
        name, ppid = lookup(pid)
        if name is None:
            return None, None  # process gone or lookup failed -- not protected
        if name in VSCODE_VARIANT_NAMES:
            return pid, name
        if ppid is None or ppid == pid:
            return None, None
        pid = ppid
    return None, None


def read_active_sessions_registry(_lookup=None):
    """Read ~/.claude/.tmp/active-sessions.json and return dict pid -> entry
    for entries whose vscode_ppid is still alive (if recorded).

    If the registry file is missing or malformed, returns {} (graceful).
    _lookup injection for testing.
    """
    if not REGISTRY_PATH.exists():
        return {}
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return {}
    sessions = data.get("sessions", [])
    if not isinstance(sessions, list):
        return {}
    lookup = _lookup or _wmic_get_name_and_ppid
    alive = {}
    for entry in sessions:
        if not isinstance(entry, dict):
            continue
        pid = entry.get("pid")
        if not isinstance(pid, int):
            continue
        vscode_ppid = entry.get("vscode_ppid")
        if isinstance(vscode_ppid, int) and vscode_ppid > 0:
            name, _ = lookup(vscode_ppid)
            if name in VSCODE_VARIANT_NAMES:
                alive[pid] = entry
                continue
        # No verifiable vscode_ppid -- do NOT treat as protected. The registry
        # is backup; without a live VS Code parent we fall back to the primary
        # ancestor-walk check (which will also fail for a true orphan).
    return alive


def classify_processes(procs, current_pid, threshold_hours,
                       _ancestor_lookup=None, _registry_reader=None):
    """
    Multi-signal orphan classifier (wr-2026-04-22-012).

    For each claude.exe process:
      - If age < threshold_hours  -> recent
      - If pid == current_pid      -> current
      - Else check protection signals in order:
          (1) live VS Code ancestor in process tree  -> protected
          (2) listed in active-sessions registry w/
              live vscode_ppid                        -> protected
      - Otherwise                                    -> orphan_suspects (TRUE orphan)

    Returns dict: total, threshold_hours, current, recent, protected, orphan_suspects.
    Lists sorted oldest-first by age_hours (descending).

    Injection points _ancestor_lookup and _registry_reader let tests simulate
    arbitrary process trees and registry states.
    """
    now = datetime.now(timezone.utc)
    orphan = []
    protected = []
    recent = []
    current_proc = None
    registry = (_registry_reader or read_active_sessions_registry)()
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
        if age < timedelta(hours=threshold_hours):
            recent.append(info)
            continue
        # Old enough to be a suspect -- apply protection signals
        vs_pid, vs_name = find_vscode_ancestor(p["pid"], _lookup=_ancestor_lookup)
        if vs_pid:
            info["protection"] = f"vscode_ancestor:{vs_name}(PID {vs_pid})"
            protected.append(info)
            continue
        if p["pid"] in registry:
            ws = registry[p["pid"]].get("workspace", "?")
            info["protection"] = f"registered_session:{ws}"
            protected.append(info)
            continue
        orphan.append(info)
    orphan.sort(key=lambda x: -x["age_hours"])
    protected.sort(key=lambda x: -x["age_hours"])
    return {
        "total": len(procs),
        "threshold_hours": threshold_hours,
        "current": current_proc,
        "recent": recent,
        "protected": protected,
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
    p.add_argument("--show-protected", action="store_true",
                   help="Also list old-but-protected processes (real sessions with "
                        "live VS Code ancestor or registered active-sessions entry)")
    args = p.parse_args()

    procs = get_claude_processes()
    current_pid = find_session_pid()
    report = classify_processes(procs, current_pid, args.threshold_hours)
    report["current_session_pid"] = current_pid

    if args.summary:
        n = len(report["orphan_suspects"])
        n_protected = len(report.get("protected", []))
        if n == 0:
            extra = f", {n_protected} protected" if n_protected else ""
            print(f"Orphan check: 0 (total {report['total']} claude.exe processes{extra})")
        else:
            oldest = report["orphan_suspects"][0]
            extra = f", {n_protected} protected" if n_protected else ""
            print(f"Orphan check: {n} suspect (oldest {oldest['age_hours']}h "
                  f"PID {oldest['pid']}{extra}). Run "
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
        print(f"True orphans ({len(report['orphan_suspects'])}):")
        for o in report["orphan_suspects"]:
            print(f"  PID {o['pid']}  age {o['age_hours']:>6}h  mem {o['mb']:>6.0f}MB  started {o['created_at']}")
    else:
        print("No true orphans detected.")
    if report.get("protected") and args.show_protected:
        print()
        print(f"Old-but-protected real sessions ({len(report['protected'])}):")
        for p_info in report["protected"]:
            prot = p_info.get("protection", "?")
            print(f"  PID {p_info['pid']}  age {p_info['age_hours']:>6}h  mem {p_info['mb']:>6.0f}MB  [{prot}]")
    elif report.get("protected"):
        print()
        print(f"({len(report['protected'])} old-but-protected real session(s) hidden; pass --show-protected)")
    if report["recent"]:
        print()
        print(f"Recent processes ({len(report['recent'])}):")
        for r in report["recent"]:
            print(f"  PID {r['pid']}  age {r['age_hours']:>6}h  mem {r['mb']:>6.0f}MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
