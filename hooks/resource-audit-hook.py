"""
resource-audit-hook.py - PostToolUse hook for resource audit reminders

Tracks two things:
1. Write/Edit operations on deliverable files (edit counter + nudges)
2. Skill/Agent invocations in a tool usage journal (for PROCESS gap detection)

Edit counter nudges every 5 edits to run the resource-auditor skill.
Counter does NOT reset on nudge -- only when the resource-auditor runs.

Tool usage journal logs every Skill and Agent call with tool_name and
key arguments. The resource-auditor reads this journal to detect PROCESS
gaps (e.g., brainstorming not invoked during planning sessions).

Non-blocking: injects additional context, does not deny the operation.
Works in ALL workspaces -- resource auditing is universal.

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with hookSpecificOutput.additionalContext (if threshold met)
"""

import json
import os
import sys
import tempfile


COUNTER_FILE = os.path.join(tempfile.gettempdir(), "claude_resource_audit_counter.txt")
JOURNAL_FILE = os.path.join(tempfile.gettempdir(), "claude_tool_usage_journal.jsonl")
NUDGE_INTERVAL = 5


def get_counter():
    """Read the current Write/Edit counter from temp file."""
    try:
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def set_counter(value):
    """Write the counter value to temp file."""
    with open(COUNTER_FILE, "w") as f:
        f.write(str(value))


def is_excluded_path(file_path):
    """Exclude paths that are infrastructure, not deliverables."""
    normalized = file_path.replace("\\", "/").lower()
    exclude_patterns = [
        "/.claude/",
        "/.git/",
        "/.tmp/",
        "/node_modules/",
        ".env",
        "memory.md",
        "claude.md",
    ]
    for pattern in exclude_patterns:
        if pattern in normalized:
            return True
    return False


def log_tool_usage(tool_name, tool_input):
    """Append a Skill or Agent invocation to the tool usage journal."""
    entry = {"tool": tool_name}
    if tool_name == "Skill":
        entry["skill"] = tool_input.get("skill", "")
        entry["args"] = tool_input.get("args", "")
    elif tool_name == "Agent":
        entry["description"] = tool_input.get("description", "")
        entry["subagent_type"] = tool_input.get("subagent_type", "")
    try:
        with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Log Skill and Agent invocations to the tool usage journal
    if tool_name in ("Skill", "Agent"):
        log_tool_usage(tool_name, tool_input)
        return 0

    # Only trigger edit counter on Write and Edit
    if tool_name not in ("Write", "Edit"):
        return 0

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0

    # Don't count infrastructure edits (hooks, skills, settings, memory)
    if is_excluded_path(file_path):
        return 0

    # Increment counter (never resets on nudge -- only when audit actually runs)
    count = get_counter() + 1
    set_counter(count)

    # Nudge at every multiple of NUDGE_INTERVAL (5, 10, 15, 20...)
    if count % NUDGE_INTERVAL == 0:
        nudge_number = count // NUDGE_INTERVAL
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    "RESOURCE AUDIT REMINDER: You have completed %d Write/Edit "
                    "operations on deliverable files (nudge #%d). "
                    "You SHOULD run the resource-auditor skill now to verify you "
                    "are using the right skills, tools, and resources for this task. "
                    "Four checks: UNUSED (had it, didn't use it), "
                    "MISSING (needed it, doesn't exist), "
                    "FALLBACK (used generic, specialized would be better), "
                    "PROCESS (methodology skill should have been invoked). "
                    "If you do not run the audit now, this counter will keep climbing "
                    "and the post-task audit will report how many nudges were ignored."
                    % (count, nudge_number)
                ),
            }
        }
        print(json.dumps(output))

    return 0


if __name__ == "__main__":
    sys.exit(main())