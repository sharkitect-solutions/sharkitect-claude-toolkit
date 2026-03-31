"""
checkpoint-reminder.py - PostToolUse hook for checkpoint reminders

Tracks Edit/Write calls. After 3+ edits without touching MEMORY.md,
reminds the agent to checkpoint progress. Resets counter when MEMORY.md
is edited.

Input: JSON on stdin with tool_name and tool_input.file_path
Output: Reminder message on stdout (non-blocking, exit 0 always)
State: Counter persisted in ~/.claude/.tmp/.checkpoint-counter
"""

import json
import os
import sys


COUNTER_FILE = os.path.join(os.path.expanduser("~"), ".claude", ".tmp", ".checkpoint-counter")
THRESHOLD = 3


def normalize_path(path):
    return path.replace("\\", "/")


def read_counter():
    try:
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def write_counter(count):
    try:
        os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)
        with open(COUNTER_FILE, "w") as f:
            f.write(str(count))
    except OSError:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    norm = normalize_path(file_path)
    basename = norm.rsplit("/", 1)[-1] if "/" in norm else norm

    if basename == "MEMORY.md":
        write_counter(0)
        sys.exit(0)

    counter = read_counter() + 1

    if counter >= THRESHOLD:
        print(
            "Checkpoint reminder: You have made "
            f"{counter} edits since last MEMORY.md update. "
            "Consider updating MEMORY.md with progress before continuing."
        )
        write_counter(0)
    else:
        write_counter(counter)

    sys.exit(0)


if __name__ == "__main__":
    main()
