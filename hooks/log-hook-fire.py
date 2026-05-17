"""
log-hook-fire.py - PostToolUse * matcher: telemetry log of every tool call.

Filed by: wr-skillhub-2026-05-15-001 (Skill Hub). Enables empirical
zero-fire hook retirement audits per the Hook Introduction Rule sunset
clause (universal-protocols.md).

What it logs:
  One JSON line per tool call to ~/.claude/.tmp/hook-fire-log.jsonl with
  fields: {timestamp, tool_name, file_path, session_id, hook_event}.

Limitation (documented honestly):
  A PostToolUse hook only sees its own fire and the tool call context. It
  CANNOT observe other hooks' executions. The companion CLI
  (~/.claude/scripts/audit-hook-fires.py) infers per-hook fire counts by
  joining tool calls to the matcher rules in settings.json. This is an
  approximation: hooks that early-exit, deny, or have internal guards still
  count as "fired" because the script DID execute. For budget/retirement
  decisions ("did this hook do anything in 90 days?") the inferred count
  is the right signal.

Behavior:
  - Never blocks (always exits 0).
  - Never raises (best-effort logging).
  - Cheap: append-only file write; no subprocess, no network.
  - Skips silently on empty/malformed input.

Pure Python stdlib.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path.home() / ".claude" / ".tmp" / "hook-fire-log.jsonl"


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def extract_file_path(tool_input):
    """Pull a file_path-ish field if present. Best-effort; None if absent."""
    if not isinstance(tool_input, dict):
        return None
    for key in ("file_path", "path", "filename", "notebook_path"):
        v = tool_input.get(key)
        if v and isinstance(v, str):
            return v
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = payload.get("tool_name") or ""
    if not tool_name:
        return 0

    entry = {
        "timestamp": now_iso(),
        "tool_name": tool_name,
        "file_path": extract_file_path(payload.get("tool_input")),
        "session_id": payload.get("session_id"),
        "hook_event": payload.get("hook_event_name") or "PostToolUse",
    }

    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        # Never break the user's session because of logging.
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
