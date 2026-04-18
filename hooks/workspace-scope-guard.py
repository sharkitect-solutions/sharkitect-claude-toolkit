"""
workspace-scope-guard.py - PreToolUse hook for workspace scope enforcement

Detects when Claude is creating files that belong in a different workspace
based on the current working directory and the file being written.

Non-blocking: injects a warning with the correct workspace to use.
Works globally across all workspaces.

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with hookSpecificOutput.additionalContext (if violation detected)

Scope violations detected:
- Writing skills/hooks/agents/plugins from non-Skill-Hub workspace
- Writing client deliverables from non-HQ workspace
- Writing monitoring/audit tools from non-Sentinel workspace
- Writing to another workspace's directory from current workspace

Protocol-sanctioned cross-workspace writes (NOT blocked):
- Universal-protocols Blocker-Cleared Notification Protocol:
  Append-only Edit on another workspace's .work-requests/inbox/*.json that
  extends the `blocker_cleared_notes` array.
- Cross-Workspace Routed Tasks Protocol:
  Write of a NEW file to another workspace's .routed-tasks/inbox/ (already
  covered by ALWAYS_ALLOWED). Also: Write of a NEW file to another
  workspace's .work-requests/inbox/ (parallel pattern -- new files in
  another workspace's inbox are coordination, not scope violation).
"""

import json
import os
import sys


# Workspace identification by CWD keywords
def detect_workspace(cwd):
    """Identify which workspace we're in based on CWD."""
    cwd_lower = cwd.replace("\\", "/").lower()
    if "skill management hub" in cwd_lower or "3.-" in cwd_lower:
        return "skill-hub"
    if "workforce" in cwd_lower and "hq" in cwd_lower or "1.-" in cwd_lower:
        return "hq"
    if "sentinel" in cwd_lower or "4.-" in cwd_lower:
        return "sentinel"
    return "unknown"


# Workspace directory paths (normalized, lowercase)
WORKSPACE_PATHS = {
    "skill-hub": "skill management hub",
    "hq": "sharkitect digital workforce hq",
    "sentinel": "sentinel",
}

# What each workspace is NOT allowed to create
# Maps: current_workspace -> [(path_pattern, violation_description, correct_workspace)]
SCOPE_VIOLATIONS = {
    "hq": [
        ("/.claude/skills/", "Creating skills belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/hooks/", "Creating hooks belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/agents/", "Creating agents belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/plugins/", "Creating plugins belongs in Skill Management Hub", "Skill Management Hub"),
        ("/4.- sentinel/", "Writing Sentinel files from HQ", "Sentinel"),
        ("/3.- skill management hub/", "Writing Skill Hub files from HQ", "Skill Management Hub"),
    ],
    "sentinel": [
        ("/.claude/skills/", "Creating skills belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/hooks/", "Creating hooks belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/agents/", "Creating agents belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/plugins/", "Creating plugins belongs in Skill Management Hub", "Skill Management Hub"),
        ("/1.- sharkitect digital workforce hq/", "Writing HQ files from Sentinel", "Workforce HQ"),
        ("/3.- skill management hub/", "Writing Skill Hub files from Sentinel", "Skill Management Hub"),
    ],
    "skill-hub": [
        ("/1.- sharkitect digital workforce hq/", "Writing HQ files from Skill Hub", "Workforce HQ"),
        ("/4.- sentinel/", "Writing Sentinel files from Skill Hub", "Sentinel"),
    ],
}

# Paths that are always allowed regardless of workspace (global shared infra)
ALWAYS_ALLOWED = [
    "/.claude/rules/",
    "/.claude/lessons-learned.md",
    "/.claude/docs/plans-registry.md",
    "/.claude/docs/autonomous-systems-inventory.md",
    "/.claude/scripts/",
    ".gap-reports/",
    ".routed-tasks/",
    ".lifecycle-reviews/",
    "memory/",
    "memory.md",
    ".tmp/",
]


def normalize_path(path):
    """Normalize path for comparison."""
    return path.replace("\\", "/").lower()


def is_always_allowed(file_path):
    """Check if file is in a globally-allowed path."""
    normalized = normalize_path(file_path)
    for allowed in ALWAYS_ALLOWED:
        if allowed.lower() in normalized:
            return True
    return False


def check_cross_workspace_write(file_path, current_workspace):
    """Check if writing to another workspace's directory."""
    normalized = normalize_path(file_path)

    violations = SCOPE_VIOLATIONS.get(current_workspace, [])
    for pattern, description, correct_ws in violations:
        if pattern.lower() in normalized:
            return description, correct_ws

    return None, None


def is_protocol_sanctioned_write(tool_name, tool_input):
    """
    Detect protocol-sanctioned cross-workspace writes that should NOT be blocked.

    Two patterns are sanctioned by universal-protocols.md:

    1. Write a NEW file to another workspace's .work-requests/inbox/
       (parallel to .routed-tasks/inbox/ pattern -- coordination, not violation).
       Detected via tool_name == "Write" AND path matches the inbox pattern.
       NOTE: ALWAYS_ALLOWED already covers .routed-tasks/inbox/ via prefix match.

    2. Append-only Edit on another workspace's .work-requests/inbox/*.json
       that extends the `blocker_cleared_notes` array (Blocker-Cleared
       Notification Protocol).

       Heuristic detection (deliberately conservative):
       - tool_name == "Edit"
       - file_path matches "*/.work-requests/inbox/*.json"
       - both old_string and new_string contain "blocker_cleared_notes"
       - new_string is meaningfully longer than old_string (suggests append,
         not modify-in-place or delete)

       Known false-positive risk: an Edit that REPLACES an existing
       blocker_cleared_notes entry with a longer one (e.g., editing a typo
       in a previously-signed note) would also be allowed. This is acceptable
       because (a) such edits are rare, (b) protocol violations of this kind
       are easily auditable from git history, and (c) a non-blocking warning
       is preferable to blocking legitimate signing work.
    """
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return False
    normalized = normalize_path(file_path)

    # Pattern 1: Write to ANY .work-requests/inbox/ in another workspace
    if tool_name == "Write" and "/.work-requests/inbox/" in normalized:
        return True

    # Pattern 2: Edit appending to blocker_cleared_notes
    if tool_name == "Edit" and "/.work-requests/inbox/" in normalized and normalized.endswith(".json"):
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        # Both sides reference the array name AND the new content extends it
        if (
            "blocker_cleared_notes" in old_string
            and "blocker_cleared_notes" in new_string
            and len(new_string) > len(old_string) + 20
        ):
            return True

    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only trigger on Write and Edit
    if tool_name not in ("Write", "Edit"):
        return 0

    # Get file path
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0

    # Skip always-allowed paths (covers .routed-tasks/, .lifecycle-reviews/, etc.)
    if is_always_allowed(file_path):
        return 0

    # Skip protocol-sanctioned cross-workspace writes
    # (blocker_cleared_notes appends, new work request drops)
    if is_protocol_sanctioned_write(tool_name, tool_input):
        return 0

    # Detect current workspace
    cwd = os.getcwd()
    current_workspace = detect_workspace(cwd)

    if current_workspace == "unknown":
        return 0

    # Check for violations
    violation, correct_ws = check_cross_workspace_write(file_path, current_workspace)

    if violation is None:
        return 0

    warning = (
        "WORKSPACE SCOPE VIOLATION DETECTED. "
        "{violation}. "
        "This work belongs in {correct_ws}. "
        "STOP and tell the user: 'This belongs in {correct_ws}. "
        "Open that workspace and continue there.' "
        "If the user explicitly overrides, note the exception in MEMORY.md."
    ).format(violation=violation, correct_ws=correct_ws)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": warning,
        }
    }

    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
