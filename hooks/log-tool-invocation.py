"""
log-tool-invocation.py - PostToolUse hook on Skill + Agent matchers.

Appends one JSONL line to <tempdir>/claude_tool_usage_journal.jsonl per
Skill or Agent tool invocation. Resource-auditor (Step 3.5 PROCESS check)
reads this exact path via tempfile.gettempdir() and uses it to determine
which skills/agents the session used.

File was not being written until this hook was deployed (see
wr-2026-04-21-011, filed by Sentinel 2026-04-22). Without it the auditor's
PROCESS check silently reports zero invocations regardless of actual use,
defeating the feedback loop that catches methodology-skill skips.

JSONL format (one object per line):
  {"tool": "Skill", "skill": "<name>", "timestamp": "<ISO>"}
  {"tool": "Agent", "subagent_type": "<name>", "timestamp": "<ISO>"}

Behavior:
- Append-only (never overwrites)
- Fails silently on any write error (never blocks tool execution)
- Non-blocking: always exits 0
- Pure stdlib

Input: JSON on stdin with keys tool_name and tool_input.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime


JOURNAL_PATH = os.path.join(tempfile.gettempdir(), "claude_tool_usage_journal.jsonl")


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Skill", "Agent"):
        return 0

    tool_input = data.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    record = {"tool": tool_name, "timestamp": datetime.now().isoformat()}
    if tool_name == "Skill":
        skill = tool_input.get("skill") or tool_input.get("name") or ""
        if not skill:
            return 0
        record["skill"] = skill
    else:
        subagent = tool_input.get("subagent_type") or ""
        if not subagent:
            return 0
        record["subagent_type"] = subagent

    try:
        with open(JOURNAL_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
