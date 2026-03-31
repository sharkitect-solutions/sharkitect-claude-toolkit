"""
check-line-count.py - PreToolUse hook for MEMORY.md and CLAUDE.md line limits

Blocks Edit/Write operations on MEMORY.md (>=150 lines) and CLAUDE.md (>=250 lines)
BEFORE the edit happens. Prevents file bloat that degrades system effectiveness.

Input: JSON on stdin with tool_name and tool_input.file_path
Output: Deny message on stderr (exit 2) or silent pass (exit 0)
"""

import json
import sys


LIMITS = {
    "MEMORY.md": 150,
    "CLAUDE.md": 250,
}


def normalize_path(path):
    return path.replace("\\", "/")


def count_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return 0


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

    limit = LIMITS.get(basename)
    if limit is None:
        sys.exit(0)

    line_count = count_lines(file_path)

    if line_count >= limit:
        msg = (
            f"BLOCKED: {basename} is {line_count} lines (limit: {limit}). "
            f"Move content to topic files or Supabase before adding more."
        )
        print(msg, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
