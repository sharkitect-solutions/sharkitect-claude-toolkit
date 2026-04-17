"""
check-line-count.py - PreToolUse hook for MEMORY.md and CLAUDE.md line limits

Two-tier, mode-aware protection:
  MEMORY.md: Hard block at 150 lines. No exceptions.
  CLAUDE.md: Mode-dependent limits.
    - Bootstrap mode (setup templates): soft warn 1500, hard block 2500
    - Runtime mode (daily operation): soft warn 150, hard block 250

Content-aware: Write checks new content, Edit calculates net change.
Shrinking edits ALWAYS allowed on over-limit files.

Input: JSON on stdin with tool_name and tool_input
Output: Warning on stdout (soft) or deny on stderr + exit 2 (hard)
"""

import json
import sys


MEMORY_HARD_LIMIT = 150

CLAUDE_LIMITS = {
    "bootstrap": {"soft": 1500, "hard": 2500},
    "runtime":   {"soft": 150,  "hard": 250},
}

BOOTSTRAP_MARKERS = [
    "bootstrap mode",
    "section 7: bootstrap tool",
    "/instantiate",
    "instantiation blueprint",
]


def normalize_path(path):
    return path.replace("\\", "/")


def count_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return 0


def count_content_lines(content):
    if not content:
        return 0
    return content.count("\n") + (1 if not content.endswith("\n") else 0)


def detect_claude_mode(file_path, new_content=None):
    """Detect if CLAUDE.md is in Bootstrap or Runtime mode.
    Checks new_content first (for Write), falls back to existing file."""
    text = ""
    if new_content:
        text = new_content[:5000].lower()
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read(5000).lower()
        except (OSError, UnicodeDecodeError):
            pass

    for marker in BOOTSTRAP_MARKERS:
        if marker in text:
            return "bootstrap"
    return "runtime"


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    norm = normalize_path(file_path)
    basename = norm.rsplit("/", 1)[-1] if "/" in norm else norm

    if basename not in ("MEMORY.md", "CLAUDE.md"):
        sys.exit(0)

    current_lines = count_lines(file_path)
    new_content = tool_input.get("content", "") if tool_name == "Write" else None

    # Calculate projected line count
    if tool_name == "Write":
        projected = count_content_lines(new_content)
    elif tool_name == "Edit":
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        net_change = new_string.count("\n") - old_string.count("\n")
        projected = current_lines + net_change
        if net_change <= 0:
            sys.exit(0)  # Shrinking edits always allowed
    else:
        sys.exit(0)

    # --- MEMORY.md: simple hard block ---
    if basename == "MEMORY.md":
        if projected >= MEMORY_HARD_LIMIT:
            print(
                f"BLOCKED: {basename} would be {projected} lines "
                f"(limit: {MEMORY_HARD_LIMIT}). "
                f"Move content to topic files or Supabase.",
                file=sys.stderr,
            )
            sys.exit(2)
        sys.exit(0)

    # --- CLAUDE.md: mode-dependent ---
    mode = detect_claude_mode(file_path, new_content)
    limits = CLAUDE_LIMITS[mode]

    if projected >= limits["hard"]:
        print(
            f"BLOCKED: CLAUDE.md ({mode} mode) would be {projected} lines "
            f"(hard limit: {limits['hard']}). "
            f"{'Externalize content to /references/ or /context/.' if mode == 'bootstrap' else 'Compress to runtime mode or externalize content.'}",
            file=sys.stderr,
        )
        sys.exit(2)

    if projected >= limits["soft"]:
        print(
            f"WARNING: CLAUDE.md ({mode} mode) will be {projected} lines "
            f"(soft limit: {limits['soft']}, hard limit: {limits['hard']}). "
            f"{'Bootstrap templates can be large, but consider externalizing if possible.' if mode == 'bootstrap' else 'Runtime CLAUDE.md should be 87-150 lines per AIOS spec. Consider compressing.'}"
        )
        sys.exit(0)  # Warn but allow

    sys.exit(0)


if __name__ == "__main__":
    main()
