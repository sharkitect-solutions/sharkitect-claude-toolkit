"""
iterative-work-nudge.py - PostToolUse hook for ralph-loop enforcement

Detects when iterative work patterns occur (Bash errors, test failures,
build failures) and nudges the AI to invoke /ralph-loop if it isn't
already active.

Tracks: consecutive Bash errors without ralph-loop activation.
After 2 consecutive errors, injects a reminder.

Non-blocking: injects additional context, does not deny the operation.
Works in ALL workspaces -- iterative work protocol is universal.

Input: JSON on stdin with tool_name and tool_result
Output: JSON on stdout with hookSpecificOutput.additionalContext (if needed)
"""

import json
import os
import sys
import tempfile


TRACKER_FILE = os.path.join(tempfile.gettempdir(), "claude_iterative_work_tracker.json")

# Patterns that indicate errors/failures in Bash output
ERROR_PATTERNS = [
    "error:",
    "Error:",
    "ERROR",
    "Traceback (most recent call last)",
    "SyntaxError",
    "TypeError",
    "NameError",
    "ImportError",
    "ModuleNotFoundError",
    "FileNotFoundError",
    "KeyError",
    "ValueError",
    "AttributeError",
    "FAIL",
    "FAILED",
    "Exit code",
    "command not found",
    "No such file or directory",
    "Permission denied",
    "Connection refused",
    "timeout",
    "status: error",
    "Build failed",
    "Compilation error",
    "npm ERR!",
    "assertion failed",
]

# Patterns that indicate ralph-loop is already active
RALPH_ACTIVE_PATTERNS = [
    "ralph",
    "Ralph Loop",
    "ralph-loop",
]


def load_tracker():
    """Load the iterative work tracker."""
    try:
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"consecutive_errors": 0, "ralph_active": False, "nudges": 0}


def save_tracker(data):
    """Save the tracker state."""
    try:
        with open(TRACKER_FILE, "w") as f:
            json.dump(data, f)
    except OSError:
        pass


def has_error(result_text):
    """Check if Bash output contains error patterns."""
    if not result_text:
        return False
    lower = result_text.lower()
    for pattern in ERROR_PATTERNS:
        if pattern.lower() in lower:
            return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    tool_result = data.get("tool_result", "")

    # If Skill tool invoked ralph-loop, mark it active
    if tool_name == "Skill":
        skill = tool_input.get("skill", "")
        if "ralph" in skill.lower():
            tracker = load_tracker()
            tracker["ralph_active"] = True
            tracker["consecutive_errors"] = 0
            save_tracker(tracker)
            return 0

    # Only track Bash errors
    if tool_name != "Bash":
        return 0

    tracker = load_tracker()

    # If ralph-loop is already active, no nudge needed
    if tracker["ralph_active"]:
        return 0

    # Check if this Bash output has errors
    result_str = str(tool_result) if tool_result else ""
    if has_error(result_str):
        tracker["consecutive_errors"] = tracker.get("consecutive_errors", 0) + 1
    else:
        # Success resets the counter
        tracker["consecutive_errors"] = 0
        save_tracker(tracker)
        return 0

    save_tracker(tracker)

    # Nudge after 2 consecutive errors
    if tracker["consecutive_errors"] >= 2:
        tracker["nudges"] = tracker.get("nudges", 0) + 1
        save_tracker(tracker)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    "ITERATIVE WORK DETECTED: %d consecutive Bash errors "
                    "without ralph-loop active. Per universal protocol: "
                    "invoke /ralph-loop NOW to handle build-test-fix cycles "
                    "autonomously. Do not make another attempt without it. "
                    "The user expects the system to iterate until fixed, "
                    "not stop after each failure."
                    % tracker["consecutive_errors"]
                ),
            }
        }
        print(json.dumps(output))

    return 0


if __name__ == "__main__":
    sys.exit(main())
