"""
skill-sync-nudge.py - PostToolUse hook for skill/agent sync enforcement

Detects when Write/Edit targets files in ~/.claude/skills/ or ~/.claude/agents/.
When detected:
  1. Drops a .sync-needed flag in Skill Hub's .tmp/ directory
  2. Nudges the AI to run sync-skills.py before session end

Debounced: only nudges once per session to avoid noise during multi-file
skill builds. The flag file accumulates all modified paths.

Non-blocking: injects additional context, does not deny the operation.
Works in ALL workspaces -- skills can technically be written from anywhere.

Input: JSON on stdin with tool_name, tool_input, tool_result
Output: JSON on stdout with hookSpecificOutput.additionalContext (if nudge needed)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


# Where the sync flag lives (Skill Hub .tmp/)
SKILL_HUB_TMP = (
    Path.home()
    / "Documents"
    / "Claude Code Workspaces"
    / "3.- Skill Management Hub"
    / ".tmp"
)
SYNC_FLAG = SKILL_HUB_TMP / ".sync-needed"
NUDGE_TRACKER = os.path.join(
    os.environ.get("TEMP", "/tmp"), "claude_sync_nudge_session.json"
)

# Paths that trigger the sync flag
WATCHED_PREFIXES = [
    str(Path.home() / ".claude" / "skills").replace("\\", "/").lower(),
    str(Path.home() / ".claude" / "agents").replace("\\", "/").lower(),
]


def get_file_path(hook_input):
    """Extract the file path from the hook input."""
    tool_input = hook_input.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            return None
    return tool_input.get("file_path", "")


def is_watched_path(file_path):
    """Check if the file path is under a watched directory."""
    normalized = file_path.replace("\\", "/").lower()
    return any(normalized.startswith(prefix) for prefix in WATCHED_PREFIXES)


def update_sync_flag(file_path):
    """Add the modified file to the sync-needed flag."""
    SKILL_HUB_TMP.mkdir(parents=True, exist_ok=True)

    flag_data = {"created": datetime.now().isoformat(), "files": []}
    if SYNC_FLAG.exists():
        try:
            flag_data = json.loads(SYNC_FLAG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    normalized = file_path.replace("\\", "/")
    if normalized not in flag_data.get("files", []):
        flag_data.setdefault("files", []).append(normalized)
        flag_data["last_modified"] = datetime.now().isoformat()

    SYNC_FLAG.write_text(json.dumps(flag_data, indent=2), encoding="utf-8")


def should_nudge():
    """Check if we've already nudged this session (debounce)."""
    try:
        if os.path.exists(NUDGE_TRACKER):
            data = json.loads(Path(NUDGE_TRACKER).read_text(encoding="utf-8"))
            # Same session = same date + already nudged
            if data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                return not data.get("nudged", False)
        return True
    except (json.JSONDecodeError, OSError):
        return True


def mark_nudged():
    """Record that we've nudged this session."""
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "nudged": True,
        "nudged_at": datetime.now().isoformat(),
    }
    try:
        Path(NUDGE_TRACKER).write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )
    except OSError:
        pass


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        return

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return

    file_path = get_file_path(hook_input)
    if not file_path or not is_watched_path(file_path):
        return

    # File is under ~/.claude/skills/ or ~/.claude/agents/ -- flag it
    update_sync_flag(file_path)

    # Debounce: only nudge once per session
    if not should_nudge():
        return

    mark_nudged()

    # Determine what was modified
    if "/skills/" in file_path.replace("\\", "/").lower():
        artifact_type = "skill"
    else:
        artifact_type = "agent"

    output = {
        "hookSpecificOutput": {
            "additionalContext": (
                f"SYNC REMINDER: A {artifact_type} file was modified in ~/.claude/. "
                "Before this session ends, run: "
                "python tools/sync-skills.py --sync --push "
                "(from Skill Hub workspace) to back up to the toolkit repo "
                "and refresh manifests across all workspaces. "
                "The .sync-needed flag has been set in Skill Hub's .tmp/ directory."
            ),
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
