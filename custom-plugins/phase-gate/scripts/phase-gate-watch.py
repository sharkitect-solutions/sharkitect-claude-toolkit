"""
phase-gate PostToolUse (Write|Edit) hook.

Fires on every Write/Edit and makes smart decisions:
1. Plan file modified -> remind AI to run Plan Change Protocol
2. lessons-learned.md modified -> remind about global copy
3. Active phase exists -> track file in phase-artifacts.json
4. Otherwise -> silent pass-through

Reads tool_input from stdin JSON to detect file_path.
Must complete in <50ms for responsiveness.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_cwd():
    return os.getcwd()


def get_home():
    return str(Path.home())


def read_stdin():
    """Read hook input from stdin."""
    try:
        data = json.load(sys.stdin)
        return data
    except (json.JSONDecodeError, EOFError):
        return {}


def get_file_path(hook_input):
    """Extract the file path that was just written/edited."""
    tool_input = hook_input.get("tool_input", {})
    return tool_input.get("file_path", "")


def is_plan_file(file_path):
    """Detect if the modified file is a plan file."""
    normalized = file_path.replace("\\", "/").lower()

    # Explicit plan directories
    if "/.claude/plans/" in normalized:
        return True
    if "/.claude\\plans\\" in file_path.lower():
        return True

    # Files with "plan" in the name inside common locations
    basename = os.path.basename(normalized)
    if "plan" in basename and basename.endswith(".md"):
        return True

    return False


def is_lessons_learned(file_path):
    """Detect if the modified file is a lessons-learned file."""
    basename = os.path.basename(file_path).lower()
    return basename == "lessons-learned.md"


def is_global_lessons(file_path):
    """Check if this is the GLOBAL lessons-learned (not project-local)."""
    home = get_home().replace("\\", "/").lower()
    normalized = file_path.replace("\\", "/").lower()
    global_path = home + "/.claude/lessons-learned.md"
    return normalized == global_path


def get_active_phase(cwd):
    """Read .tmp/active-phase.json if it exists."""
    phase_file = os.path.join(cwd, ".tmp", "active-phase.json")
    if not os.path.isfile(phase_file):
        return None
    try:
        with open(phase_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def track_artifact(cwd, file_path):
    """Add file to .tmp/phase-artifacts.json for orphan auditing later."""
    artifacts_file = os.path.join(cwd, ".tmp", "phase-artifacts.json")
    artifacts = {"files": [], "last_updated": ""}

    if os.path.isfile(artifacts_file):
        try:
            with open(artifacts_file, "r", encoding="utf-8") as f:
                artifacts = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    # Normalize path for comparison
    normalized = os.path.normpath(file_path)
    if normalized not in artifacts.get("files", []):
        artifacts.setdefault("files", []).append(normalized)

    artifacts["last_updated"] = datetime.now(timezone.utc).isoformat()

    try:
        os.makedirs(os.path.dirname(artifacts_file), exist_ok=True)
        with open(artifacts_file, "w", encoding="utf-8") as f:
            json.dump(artifacts, f, indent=2)
    except OSError:
        pass


def main():
    hook_input = read_stdin()
    file_path = get_file_path(hook_input)

    if not file_path:
        return

    cwd = get_cwd()
    messages = []

    # Decision 1: Plan file modified
    if is_plan_file(file_path):
        messages.append(
            "[phase-gate] Plan file modified: %s. "
            "Run Plan Change Protocol: check for orphaned artifacts, "
            "update cross-references, sync TodoWrite with new plan state."
            % os.path.basename(file_path)
        )

    # Decision 2: Lessons-learned modified (project-local only)
    elif is_lessons_learned(file_path) and not is_global_lessons(file_path):
        global_ll = os.path.join(get_home(), ".claude", "lessons-learned.md")
        if os.path.isfile(global_ll):
            messages.append(
                "[phase-gate] Project lessons-learned.md updated. "
                "If this failure applies to ANY project using this tool/API, "
                "also add it to ~/.claude/lessons-learned.md (global)."
            )

    # Decision 3: Track artifact if phase is active
    active_phase = get_active_phase(cwd)
    if active_phase and active_phase.get("status") != "complete":
        track_artifact(cwd, file_path)

    # Output messages (empty = silent pass-through)
    if messages:
        for msg in messages:
            print(msg)


if __name__ == "__main__":
    main()