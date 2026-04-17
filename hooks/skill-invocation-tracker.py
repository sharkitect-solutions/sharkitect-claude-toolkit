"""
skill-invocation-tracker.py - PreToolUse hook on Skill matcher

Records every Skill tool invocation to a per-day session-state file at
~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json. Other hooks
(content-enforcement-gate, methodology-nudge, future enforcement gates) read
this log to determine whether the AI has invoked required skills before
proceeding with gated operations.

Tracked record:
  {
    "skill": "<skill-name-or-namespaced>",
    "args": "<short-snippet-or-empty>",
    "timestamp": "<ISO>",
    "cwd": "<working-directory>"
  }

Non-blocking: always exits 0. Pure stdlib.

Input: JSON on stdin
  { "tool_name": "Skill", "tool_input": {"skill": "...", "args": "..."} }
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path


LOG_DIR = Path.home() / ".claude" / ".tmp"


def log_path():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"skill-invocations-{today}.json"


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    if data.get("tool_name") != "Skill":
        return 0

    tool_input = data.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    skill = tool_input.get("skill") or tool_input.get("name") or ""
    if not skill:
        return 0

    args = tool_input.get("args") or ""
    if isinstance(args, str) and len(args) > 200:
        args = args[:200]

    record = {
        "skill": skill,
        "args": args,
        "timestamp": datetime.now().isoformat(),
        "cwd": os.getcwd(),
    }

    path = log_path()
    log = {"date": datetime.now().strftime("%Y-%m-%d"), "invocations": []}
    if path.exists():
        try:
            log = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    log.setdefault("invocations", []).append(record)
    log["last_updated"] = datetime.now().isoformat()

    try:
        path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
