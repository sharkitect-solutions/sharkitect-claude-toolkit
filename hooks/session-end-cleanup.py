"""
session-end-cleanup.py - SessionEnd / Stop hook for clean cron + marker cleanup

Filed by: HQ wr-2026-04-19_workforce-hq_orphan-claude-processes-hold-rogue-crons
Layer 3 of the orphan prevention design (DETECTION + CLEANUP + PREVENTION).
This is the PREVENTION layer.

What it does:
  1. Removes the per-session cron-fire marker
     (~/.claude/.tmp/cron-fires/session-<pid>.json) so a future session
     reusing the same PID starts clean.
  2. Logs the session-end event to ~/.claude/.tmp/session-end-log.jsonl
     so we can correlate orphan timing with abnormal session ends.
  3. Does NOT call CronDelete (Claude Code already kills in-session crons
     on session end; only orphans -- crons in dead processes -- survive).

Fire-and-forget. Never blocks. Best-effort cleanup.

Input: JSON on stdin with session_id, hook_event_name, etc.
Output: nothing.

Pure Python stdlib.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


CRON_MARKER_DIR = Path.home() / ".claude" / ".tmp" / "cron-fires"
LOG_FILE = Path.home() / ".claude" / ".tmp" / "session-end-log.jsonl"


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def find_parent_claude_pid():
    """Walk parents to find claude.exe ancestor PID."""
    try:
        my_pid = os.getpid()
        for _ in range(10):
            out = subprocess.check_output(
                ["wmic", "process", "where", f"ProcessId={my_pid}",
                 "get", "Name,ParentProcessId", "/format:csv"],
                stderr=subprocess.DEVNULL, text=True, timeout=3,
            )
            name = parent = None
            for line in out.splitlines():
                line = line.strip()
                if not line or line.startswith("Node") or "Name" in line:
                    continue
                parts = line.split(",")
                if len(parts) >= 3:
                    name = parts[1].strip().lower()
                    try:
                        parent = int(parts[2].strip())
                    except (ValueError, TypeError):
                        parent = None
            if name == "claude.exe":
                return my_pid
            if not parent or parent == my_pid:
                return None
            my_pid = parent
    except Exception:
        return None
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    session_pid = find_parent_claude_pid()
    event = payload.get("hook_event_name", "Stop")

    # Cleanup cron marker
    marker_removed = False
    if session_pid:
        marker = CRON_MARKER_DIR / f"session-{session_pid}.json"
        if marker.exists():
            try:
                marker.unlink()
                marker_removed = True
            except Exception:
                pass

    # Log event
    entry = {
        "timestamp": now_iso(),
        "event": event,
        "session_pid": session_pid,
        "session_id": payload.get("session_id"),
        "marker_removed": marker_removed,
        "reason": payload.get("reason"),
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
