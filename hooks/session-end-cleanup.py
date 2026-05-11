"""
session-end-cleanup.py - SessionEnd / Stop hook for clean cron + marker cleanup
                        + claude.exe self-kill on true session termination

Filed by: HQ wr-2026-04-19_workforce-hq_orphan-claude-processes-hold-rogue-crons
Extended 2026-05-11 (S39) for claude.exe leak fix per Task 1.6 of
Post-Hard-Stop System Reassessment plan. Empirical: PID 12440 from S38
remained alive 3.1h after normal wrap — claude.exe is NOT reaped natively.

What it does:
  1. Removes the per-session cron-fire marker
     (~/.claude/.tmp/cron-fires/session-<pid>.json) so a future session
     reusing the same PID starts clean.
  2. Logs the session-end event to ~/.claude/.tmp/session-end-log.jsonl
     so we can correlate orphan timing with abnormal session ends.
  3. Does NOT call CronDelete (Claude Code already kills in-session crons
     on session end; only orphans -- crons in dead processes -- survive).
  4. Schedules a detached taskkill against the parent claude.exe PID when
     reason indicates true termination (logout / prompt_input_exit / other).
     Skips for `clear` (context wipe, session continues), `resume`, and
     `bypass_permissions_disabled`. Source: SessionEnd reason taxonomy at
     https://code.claude.com/docs/en/hooks.

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
KILL_LOG_FILE = Path.home() / ".claude" / ".tmp" / "session-end-kill-log.jsonl"

# SessionEnd reason values that indicate the session continues — DO NOT kill.
# Source: https://code.claude.com/docs/en/hooks
REASONS_SKIP_KILL = frozenset({"clear", "resume", "bypass_permissions_disabled"})

# Reasons that indicate true termination — DO kill if found.
REASONS_DO_KILL = frozenset({"logout", "prompt_input_exit", "other"})

# Windows subprocess creation flags (defined locally for cross-platform safety).
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200


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


def should_kill_for_reason(reason):
    """Decide whether the SessionEnd reason indicates true termination.

    Returns True only for reasons in REASONS_DO_KILL. None / unknown / skip-set
    values return False (defensive: prefer leak over killing mid-session).
    """
    if reason is None:
        return False
    if reason in REASONS_SKIP_KILL:
        return False
    return reason in REASONS_DO_KILL


def schedule_self_kill(pid):
    """Spawn a detached taskkill against the given claude.exe PID.

    Returns True if subprocess was spawned, False otherwise. Detached + windowless
    so the kill survives the current process death and does not flash a console.
    Best-effort: subprocess errors are swallowed and return False.
    """
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        flags = CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        subprocess.Popen(
            ["taskkill", "/PID", str(pid), "/F"],
            creationflags=flags,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        return True
    except Exception:
        return False


def log_kill_scheduled(pid, reason, event):
    """Best-effort log of kill scheduling for correlation with orphan-cleanup audits."""
    KILL_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": now_iso(),
        "event": event,
        "session_pid": pid,
        "reason": reason,
        "action": "detached_taskkill_scheduled",
    }
    try:
        with open(KILL_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    session_pid = find_parent_claude_pid()
    event = payload.get("hook_event_name", "Stop")
    reason = payload.get("reason")

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
        "reason": reason,
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass

    # Schedule self-kill on true termination reasons (claude.exe leaks on
    # session end natively — empirical S38->S39, 2026-05-11).
    if session_pid and should_kill_for_reason(reason):
        if schedule_self_kill(session_pid):
            log_kill_scheduled(session_pid, reason, event)

    return 0


if __name__ == "__main__":
    sys.exit(main())
