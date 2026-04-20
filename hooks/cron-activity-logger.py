"""
cron-activity-logger.py - PostToolUse hook logging cron-fired activity

Filed by: HQ wr-2026-04-19_workforce-hq_cron-fired-work-invisible-to-user-session
Companion to cron-activity-surfacer.py (UserPromptSubmit hook that surfaces
the log to the user on their next interactive message).

What it does:
  Detects when the current Claude turn started from a cron fire (recognized
  by the per-session cron marker file written by cron-context-enforcer.py).

  When in cron context, logs every "interesting" tool call to
  ~/.claude/.tmp/cron-activity-log.jsonl. Interesting = anything the user
  would want to know about:
    - File moves (especially inbox -> processed)
    - File writes/edits to .work-requests/, .routed-tasks/, .lifecycle-reviews/
    - File writes to MEMORY.md or CLAUDE.md
    - Bash commands containing 'git commit', 'git push', 'mv ', 'rm '
    - Supabase write operations (mcp__claude_ai_Supabase__execute_sql with
      INSERT/UPDATE/DELETE)
    - close-inbox-item.py invocations

  When NOT in cron context, this hook does nothing (zero overhead).

Each log entry has: timestamp, tool_name, summary (one-line), session_pid,
cron_fire_count.

Input: JSON on stdin with tool_name, tool_input, tool_response (optional).
Output: nothing (fire-and-forget); never blocks.

Pure Python stdlib.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


CRON_MARKER_DIR = Path.home() / ".claude" / ".tmp" / "cron-fires"
LOG_FILE = Path.home() / ".claude" / ".tmp" / "cron-activity-log.jsonl"


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def find_parent_claude_pid():
    """Walk parents to find claude.exe ancestor PID. Returns int or None."""
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


def get_cron_state(session_pid):
    """Return cron marker state dict or None if no marker (i.e. not in cron context)."""
    if not session_pid:
        return None
    marker = CRON_MARKER_DIR / f"session-{session_pid}.json"
    if not marker.exists():
        return None
    try:
        return json.loads(marker.read_text(encoding="utf-8"))
    except Exception:
        return None


def is_interesting(tool_name, tool_input):
    """
    Decide whether this tool call is worth logging.
    Returns (interesting: bool, summary: str).
    """
    if not tool_name:
        return False, ""

    if tool_name == "Bash":
        cmd = (tool_input or {}).get("command", "") if isinstance(tool_input, dict) else ""
        cmd_low = cmd.lower()
        triggers = ["git commit", "git push", "mv ", " rm ", "rm -",
                    "close-inbox-item.py", "taskkill"]
        for t in triggers:
            if t in cmd_low:
                short = (cmd[:120] + "...") if len(cmd) > 120 else cmd
                return True, f"Bash: {short}"
        return False, ""

    if tool_name in ("Write", "Edit"):
        path = (tool_input or {}).get("file_path", "") if isinstance(tool_input, dict) else ""
        if not path:
            return False, ""
        path_low = path.lower().replace("\\", "/")
        watch = [
            ".work-requests/inbox", ".work-requests/processed", ".work-requests/outbox",
            ".routed-tasks/inbox", ".routed-tasks/processed", ".routed-tasks/outbox",
            ".lifecycle-reviews/inbox", ".lifecycle-reviews/processed",
            "memory.md", "claude.md", ".env",
        ]
        for w in watch:
            if w in path_low:
                action = "Wrote" if tool_name == "Write" else "Edited"
                return True, f"{action}: {path}"
        return False, ""

    low = ""
    try:
        if isinstance(tool_input, dict):
            low = json.dumps(tool_input, default=str).lower()[:1000]
        else:
            low = str(tool_input or "").lower()[:1000]
    except Exception:
        low = ""

    if "supabase" in tool_name.lower():
        if any(kw in low for kw in ["insert ", "update ", "delete ", "patch", "post "]):
            return True, f"Supabase write via {tool_name}"
        return False, ""

    if tool_name in ("mcp__github-mcp__merge_pull_request",
                     "mcp__github-mcp__create_pull_request",
                     "mcp__github-mcp__push_files",
                     "mcp__github-mcp__create_or_update_file"):
        return True, f"GitHub write: {tool_name}"

    return False, ""


def append_log(entry):
    """Append a JSON line to the activity log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass  # Never break the user's session because of logging


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    session_pid = find_parent_claude_pid()
    cron_state = get_cron_state(session_pid)
    if not cron_state:
        return 0  # Not in cron context -> no logging

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    interesting, summary = is_interesting(tool_name, tool_input)
    if not interesting:
        return 0

    entry = {
        "timestamp": now_iso(),
        "session_pid": session_pid,
        "cron_fire_count": cron_state.get("fire_count"),
        "first_fire_at": cron_state.get("first_fire_at"),
        "tool_name": tool_name,
        "summary": summary,
    }
    append_log(entry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
