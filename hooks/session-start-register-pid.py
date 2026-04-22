"""
session-start-register-pid.py -- SessionStart hook

Registers this Claude session's PID + VS Code ancestor PID in
~/.claude/.tmp/active-sessions.json so the orphan-kill script can
identify real sessions even when the age-based heuristic flags them.

Source: wr-2026-04-22-012 (orphan-kill killed 4 real sessions across
HQ / Sentinel / Skill Hub when the user left workspaces open overnight).

Design:
  PRIMARY defense is the VS Code ancestor check in
  check-orphan-claude-processes.py. This registry is the BACKUP --
  important for:
    - CLI-only sessions (parent is cmd.exe / bash.exe / pwsh.exe,
      not a VS Code variant)
    - Cases where the ancestor walk fails mid-call (race conditions)
    - Faster exclusion without walking the process tree each time

What this hook writes per session start:
  {
    "pid": <claude.exe PID>,
    "workspace": "<canonical workspace name or cwd basename>",
    "vscode_ppid": <PID of nearest VS Code ancestor, or null>,
    "vscode_ppname": "<name of that ancestor, or null>",
    "started_at": "<ISO timestamp>",
    "cwd": "<current working directory>"
  }

The registry is a list of these entries under a "sessions" key. This
hook also prunes stale entries (PID no longer alive) before appending.

Graceful: any failure is silent. Never block session start.
SessionStart hooks that fail print nothing and exit 0 to prevent
session-start from aborting.

Pure stdlib. Windows-only semantics (wmic). ASCII output.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REGISTRY_PATH = Path.home() / ".claude" / ".tmp" / "active-sessions.json"

VSCODE_VARIANT_NAMES = frozenset({
    "code.exe",
    "code - insiders.exe",
    "cursor.exe",
    "windsurf.exe",
    "code-oss.exe",
    "codium.exe",
    "trae.exe",
    "antigravity.exe",      # Anthropic Antigravity IDE -- see sibling script for
                            # the live-trace that revealed this gap.
})

MAX_ANCESTOR_HOPS = 12  # slightly more than check script: include claude.exe + VS Code renderer chain


def _wmic_get_name_and_ppid(pid):
    """(name_lower, ppid) or (None, None). Graceful on any failure."""
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


def find_claude_exe_pid():
    """Walk up from the hook's own Python PID to find the claude.exe ancestor.
    Returns PID or None.
    """
    pid = os.getpid()
    seen = set()
    for _ in range(MAX_ANCESTOR_HOPS):
        if pid in seen or pid is None or pid == 0:
            return None
        seen.add(pid)
        name, ppid = _wmic_get_name_and_ppid(pid)
        if name == "claude.exe":
            return pid
        if ppid is None or ppid == pid:
            return None
        pid = ppid
    return None


def find_vscode_ancestor(start_pid):
    """Walk up from start_pid looking for a VS Code variant ancestor.
    Returns (ancestor_pid, ancestor_name_lower) or (None, None).
    """
    pid = start_pid
    seen = set()
    for _ in range(MAX_ANCESTOR_HOPS):
        if pid in seen or pid is None or pid == 0:
            return None, None
        seen.add(pid)
        name, ppid = _wmic_get_name_and_ppid(pid)
        if name is None:
            return None, None
        if name in VSCODE_VARIANT_NAMES:
            return pid, name
        if ppid is None or ppid == pid:
            return None, None
        pid = ppid
    return None, None


def is_pid_alive(pid):
    """True if PID is currently running. Uses tasklist for speed."""
    if not pid:
        return False
    try:
        out = subprocess.check_output(
            ["tasklist", "/fi", f"pid eq {pid}", "/fo", "csv", "/nh"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        )
    except (subprocess.CalledProcessError, FileNotFoundError,
            subprocess.TimeoutExpired, OSError):
        return False
    # Tasklist prints "INFO: No tasks are running..." on stderr, stdout is empty
    # When found, stdout has a CSV line with the image name.
    return bool(out.strip() and str(pid) in out)


def canonical_workspace_name(cwd):
    """Best-effort workspace identifier. Uses the path basename + numeric prefix
    convention (e.g. '3.- Skill Management Hub' -> 'skill-management-hub').
    Falls back to the literal basename if the prefix pattern doesn't match.
    """
    base = os.path.basename(cwd.rstrip("/\\"))
    # Pattern: "<N>.- <Name>" -> slug
    m = re.match(r"^\d+\.-\s*(.+)$", base)
    if m:
        name = m.group(1).strip().lower()
        return re.sub(r"\s+", "-", name)
    return base


def load_registry():
    """Load registry dict, returns {"sessions": [...]} or empty shape."""
    if not REGISTRY_PATH.exists():
        return {"sessions": []}
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("sessions"), list):
            return {"sessions": []}
        return data
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return {"sessions": []}


def prune_dead_sessions(data):
    """Drop entries whose PID is no longer alive."""
    live = []
    for entry in data.get("sessions", []):
        if not isinstance(entry, dict):
            continue
        pid = entry.get("pid")
        if isinstance(pid, int) and is_pid_alive(pid):
            live.append(entry)
    data["sessions"] = live
    return data


def write_registry(data):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write: tmp + rename
    tmp = REGISTRY_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(REGISTRY_PATH)


def main():
    try:
        # Read hook stdin (we don't use it, but must drain to avoid pipe errors)
        try:
            sys.stdin.read()
        except (OSError, ValueError):
            pass

        claude_pid = find_claude_exe_pid()
        if not claude_pid:
            # Can't identify our own session -- nothing to register. Silent.
            return 0

        # Find VS Code ancestor (may be None for CLI sessions)
        vs_pid, vs_name = find_vscode_ancestor(claude_pid)

        cwd = os.getcwd()
        entry = {
            "pid": claude_pid,
            "workspace": canonical_workspace_name(cwd),
            "vscode_ppid": vs_pid,
            "vscode_ppname": vs_name,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "cwd": cwd,
        }

        data = load_registry()
        data = prune_dead_sessions(data)

        # Remove any prior entry with the same PID (session restart on same PID is rare,
        # but keeps the registry idempotent).
        data["sessions"] = [e for e in data["sessions"] if e.get("pid") != claude_pid]
        data["sessions"].append(entry)

        write_registry(data)
    except Exception:
        # Never block session start. Any failure is silent.
        pass
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
