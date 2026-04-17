"""
supabase-status-nudge.py - PostToolUse hook for Supabase task status enforcement

Detects when Write/Edit touches plan files (in ~/.claude/plans/ or workspace plans/)
and the content contains completion markers (COMPLETE, VERIFIED, FIXED, DONE).
When detected, nudges the AI to update Supabase task/project status.

Also fires when MEMORY.md is edited with phase completion language.

Debounced: only nudges once per session per file to avoid noise during
multi-edit plan updates.

Non-blocking: injects additional context, does not deny the operation.
Works in ALL workspaces.

Input: JSON on stdin with tool_name, tool_input, tool_result
Output: JSON on stdout with hookSpecificOutput.additionalContext (if nudge needed)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


# Debounce tracker -- one nudge per file per session
NUDGE_TRACKER = os.path.join(
    os.environ.get("TEMP", "/tmp"), "claude_supabase_nudge_session.json"
)

# Completion markers that suggest a task/phase was just finished
COMPLETION_MARKERS = [
    "-- COMPLETE",
    "-- VERIFIED",
    "-- FIXED",
    "-- DONE",
    "COMPLETE (",       # COMPLETE (2026-04-15)
    "VERIFIED (",
    "FIXED (",
    "status: completed",
    "FULLY COMPLETE",
]

# Paths that trigger the nudge
PLAN_DIRS = [
    str(Path.home() / ".claude" / "plans").replace("\\", "/").lower(),
]

# Filenames that trigger the nudge regardless of directory
WATCHED_FILENAMES = [
    "memory.md",
    "plans-registry.md",
]


def get_file_path(hook_input):
    """Extract the file path from the hook input."""
    tool_input = hook_input.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            return None
    return tool_input.get("file_path", None)


def get_new_content(hook_input):
    """Extract the new content being written from the hook input."""
    tool_input = hook_input.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            return ""
    # Write tool uses "content", Edit tool uses "new_string"
    return tool_input.get("content", "") or tool_input.get("new_string", "")


def is_plan_file(file_path):
    """Check if the file is a plan file or watched filename."""
    if not file_path:
        return False
    normalized = file_path.replace("\\", "/").lower()
    # Check if in a plans directory
    for plan_dir in PLAN_DIRS:
        if plan_dir in normalized:
            return True
    # Check watched filenames
    basename = os.path.basename(normalized)
    return basename in WATCHED_FILENAMES


def has_completion_marker(content):
    """Check if the content contains completion markers."""
    if not content:
        return False
    upper = content.upper()
    for marker in COMPLETION_MARKERS:
        if marker.upper() in upper:
            return True
    return False


def already_nudged(file_path):
    """Check if we already nudged for this file this session."""
    try:
        if os.path.exists(NUDGE_TRACKER):
            with open(NUDGE_TRACKER, "r") as f:
                data = json.load(f)
            return file_path.lower() in [p.lower() for p in data.get("nudged_files", [])]
    except (json.JSONDecodeError, OSError):
        pass
    return False


def record_nudge(file_path):
    """Record that we nudged for this file."""
    data = {"nudged_files": [], "session_start": datetime.now().isoformat()}
    try:
        if os.path.exists(NUDGE_TRACKER):
            with open(NUDGE_TRACKER, "r") as f:
                data = json.load(f)
    except (json.JSONDecodeError, OSError):
        pass

    if "nudged_files" not in data:
        data["nudged_files"] = []
    data["nudged_files"].append(file_path)
    data["last_nudge"] = datetime.now().isoformat()

    try:
        with open(NUDGE_TRACKER, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def main():
    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw)
    except (json.JSONDecodeError, IOError):
        print(json.dumps({}))
        return

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        print(json.dumps({}))
        return

    file_path = get_file_path(hook_input)
    if not file_path or not is_plan_file(file_path):
        print(json.dumps({}))
        return

    new_content = get_new_content(hook_input)
    if not has_completion_marker(new_content):
        print(json.dumps({}))
        return

    if already_nudged(file_path):
        print(json.dumps({}))
        return

    # Fire the nudge
    record_nudge(file_path)

    basename = os.path.basename(file_path)
    nudge_msg = (
        f"SUPABASE STATUS UPDATE NEEDED: You just wrote completion markers "
        f"to '{basename}'. If a task or phase was completed, update Supabase "
        f"NOW (before continuing other work):\n"
        f"  python ~/.claude/scripts/update-project-status.py task "
        f'"<task>" completed --project "<project>"\n'
        f"  python ~/.claude/scripts/update-project-status.py project "
        f'"<name>" <status> --phase "<phase>" --notes "<notes>"\n'
        f"Also update: plans-registry.md, MEMORY.md resume instructions, "
        f"and any cross-references. Supabase is the source of truth -- "
        f"if Supabase doesn't know, it didn't happen."
    )

    result = {
        "hookSpecificOutput": {
            "additionalContext": nudge_msg
        }
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
