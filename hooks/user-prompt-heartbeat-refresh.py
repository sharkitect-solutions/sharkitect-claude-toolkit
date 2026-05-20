"""user-prompt-heartbeat-refresh.py -- UserPromptSubmit hook

Refreshes this Claude session's heartbeat file on every user prompt submission.
The heartbeat file is the THIRD protection signal in the orphan-claude-process
classifier (alongside VS Code ancestor walk and active-sessions registry); a
session whose heartbeat is fresh is protected from kill regardless of age.

Source: spec-orphan-cleanup-heartbeat.md v1.0 (2026-05-20).
Trigger incident: 2026-05-19 S62 kill of 13 live work sessions when the existing
two-signal classifier failed (VS Code parent died, registry pruned).

What this hook does:
  - Finds this Claude session's claude.exe PID
  - Reads or initializes ~/.claude/.tmp/session-heartbeats/<pid>.json
  - Updates `last_refresh` to now, increments `refresh_count`
  - Writes atomically via tmp+replace (concurrent classifier never sees partial)

Terminology: "heartbeat" in this hook always means SESSION heartbeat
(per-claude.exe-PID liveness signal), never the COMPONENT heartbeat used by
public.system_health for scheduled-job liveness tracking.

Graceful: any failure is silent. UserPromptSubmit hooks that fail must not
block the prompt.

Pure stdlib. Windows-only semantics (wmic). ASCII output.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


HEARTBEAT_DIR = Path.home() / ".claude" / ".tmp" / "session-heartbeats"
REGISTRY_PATH = Path.home() / ".claude" / ".tmp" / "active-sessions.json"

MAX_ANCESTOR_HOPS = 12

CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0


def _wmic_get_name_and_ppid(pid):
    """(name_lower, ppid) or (None, None). Graceful on any failure."""
    try:
        out = subprocess.check_output(
            ["wmic", "process", "where", f"ProcessId={pid}",
             "get", "Name,ParentProcessId", "/format:csv"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
            creationflags=CREATE_NO_WINDOW,
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


def find_claude_exe_pid_fast():
    """Fast path: read claude.exe PID from active-sessions.json registry.

    This hook fires on EVERY UserPromptSubmit; wmic ancestor walks cost ~100-300ms
    cumulative which adds visible latency to each prompt. The SessionStart hook
    (session-start-register-pid.py) already wrote our PID + cwd to the registry,
    so we match on cwd to find OUR session's claude.exe pid without wmic.

    Returns PID or None. None defers to the wmic fallback.
    """
    if not REGISTRY_PATH.exists():
        return None
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None
    sessions = data.get("sessions", []) if isinstance(data, dict) else []
    cwd = os.path.realpath(os.getcwd())
    for entry in sessions:
        if not isinstance(entry, dict):
            continue
        entry_cwd = entry.get("cwd")
        if entry_cwd and os.path.realpath(entry_cwd) == cwd:
            pid = entry.get("pid")
            if isinstance(pid, int) and pid > 0:
                return pid
    return None


def find_claude_exe_pid():
    """Find this session's claude.exe PID. Registry first (fast), wmic fallback."""
    fast = find_claude_exe_pid_fast()
    if fast is not None:
        return fast
    # Fallback: walk up the process tree via wmic (slow; only used when registry
    # is unavailable or the cwd doesn't match any registered session)
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


def refresh_heartbeat():
    """Refresh (or create) the heartbeat file for this session's claude.exe PID.

    Reads existing data if present, bumps refresh_count, writes atomically.
    If the file is missing or corrupt, initializes a new heartbeat with
    refresh_count=1 and first_seen=now (per spec section 5.3 fail-safe).
    """
    claude_pid = find_claude_exe_pid()
    if not claude_pid:
        return  # silent

    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    path = HEARTBEAT_DIR / f"{claude_pid}.json"
    now_iso = datetime.now(timezone.utc).isoformat()

    existing = None
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(existing, dict):
                existing = None
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            existing = None

    if existing is None:
        data = {
            "pid": claude_pid,
            "workspace": _canonical_workspace_name(os.getcwd()),
            "vscode_ppid": None,
            "vscode_ppname": None,
            "first_seen": now_iso,
            "last_refresh": now_iso,
            "refresh_count": 1,
        }
    else:
        try:
            count = int(existing.get("refresh_count", 0)) + 1
        except (ValueError, TypeError):
            count = 1
        existing["last_refresh"] = now_iso
        existing["refresh_count"] = count
        # Preserve first_seen if present, otherwise set it
        if "first_seen" not in existing:
            existing["first_seen"] = now_iso
        # Ensure pid field reflects the actual pid
        existing["pid"] = claude_pid
        data = existing

    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # Windows: if the classifier briefly holds the file handle while we try to
    # rename, replace() raises PermissionError. Short retry handles the collision
    # without losing atomicity — the rename itself is still atomic when it lands.
    import time as _time
    for attempt in range(5):
        try:
            tmp.replace(path)
            break
        except PermissionError:
            if attempt == 4:
                # Give up silently — next prompt will refresh again
                try:
                    tmp.unlink()
                except OSError:
                    pass
                return
            _time.sleep(0.005)


def _canonical_workspace_name(cwd):
    """Best-effort workspace identifier; mirrors session-start-register-pid logic."""
    import re
    base = os.path.basename(cwd.rstrip("/\\"))
    m = re.match(r"^\d+\.-\s*(.+)$", base)
    if m:
        name = m.group(1).strip().lower()
        return re.sub(r"\s+", "-", name)
    return base


def main():
    try:
        # Drain stdin (UserPromptSubmit hooks receive prompt payload; we don't need it)
        try:
            sys.stdin.read()
        except (OSError, ValueError):
            pass
        refresh_heartbeat()
    except Exception:
        # Never block the prompt. Silent failure.
        pass
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
