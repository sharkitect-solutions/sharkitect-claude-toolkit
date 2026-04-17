"""
quality-gate-hook.py - PostToolUse hook for skill/agent quality enforcement

Detects when a skill (SKILL.md) or agent (.md in agents/) is created or
modified, and injects a mandatory reminder to run the appropriate judge
(skill-judge or agent-judge) before considering the work complete.

Non-blocking: injects additional context, does not deny the operation.
Works in ALL workspaces -- quality gates are universal.

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with hookSpecificOutput.additionalContext (if skill/agent detected)
"""

import json
import os
import sys


def normalize_path(path):
    return path.replace("\\", "/").lower()


def is_skill_file(file_path):
    """Check if the file is a skill SKILL.md."""
    normalized = normalize_path(file_path)
    return normalized.endswith("/skill.md") and "/skills/" in normalized


def is_agent_file(file_path):
    """Check if the file is an agent .md in the agents directory."""
    normalized = normalize_path(file_path)
    if not normalized.endswith(".md"):
        return False
    # Agent files live in ~/.claude/agents/ or similar agent directories
    return "/agents/" in normalized and "/.claude/" in normalized


def is_skill_companion(file_path):
    """Check if the file is a skill companion (references/ under a skill dir)."""
    normalized = normalize_path(file_path)
    return "/skills/" in normalized and "/references/" in normalized


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

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0

    reminder = None

    if is_skill_file(file_path):
        # Extract skill name from path
        normalized = normalize_path(file_path)
        parts = normalized.split("/skills/")
        skill_name = parts[-1].split("/")[0] if len(parts) > 1 else "unknown"
        reminder = (
            "SKILL CREATED/MODIFIED: %s. "
            "MANDATORY: Run skill-judge on this skill before considering it complete. "
            "Invoke: skill-judge %s "
            "Quality gate: B (96/120) minimum. "
            "If score < 96: optimize and re-judge until it passes. "
            "This is the annealing loop -- build, judge, optimize, re-judge."
            % (skill_name, file_path.rsplit("/SKILL.md", 1)[0].rsplit("\\SKILL.md", 1)[0])
        )
    elif is_agent_file(file_path):
        agent_name = os.path.basename(file_path).replace(".md", "")
        reminder = (
            "AGENT CREATED/MODIFIED: %s. "
            "MANDATORY: Run agent-judge on this agent before considering it complete. "
            "Quality gate: B (96/120) minimum. "
            "If score < 96: optimize and re-judge until it passes."
            % agent_name
        )
    elif is_skill_companion(file_path):
        # Companion file modified -- remind about the parent skill
        normalized = normalize_path(file_path)
        parts = normalized.split("/skills/")
        skill_name = parts[-1].split("/")[0] if len(parts) > 1 else "unknown"
        reminder = (
            "SKILL COMPANION MODIFIED for skill: %s. "
            "If this is a significant content change, re-run skill-judge "
            "to verify the skill still passes quality gate (B / 96+)."
            % skill_name
        )

    if reminder:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": reminder,
            }
        }
        print(json.dumps(output))

    return 0


if __name__ == "__main__":
    sys.exit(main())