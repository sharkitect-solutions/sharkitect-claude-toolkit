"""
deep-interview-gate.py - PreToolUse hook for requirements clarification enforcement

Fires before the Skill tool is invoked. Checks if the skill being called is
brainstorming, writing-plans, or other planning/design skills. If deep-interview
has NOT run this session (no state file exists), injects a non-blocking reminder
to consider running /deep-interview first.

Does NOT block the skill invocation -- just makes the cost of skipping visible.
The user and AI can proceed if requirements are already clear.

Non-blocking: injects additional context via stdout.
Works in ALL workspaces -- requirements clarification is universal.

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with additionalContext (if reminder needed)
"""

import json
import os
import sys


# Skills that should be preceded by deep-interview when requirements are vague
PLANNING_SKILLS = [
    "brainstorming",
    "superpowers:brainstorming",
    "writing-plans",
    "superpowers:writing-plans",
    "app-builder",
    "senior-architect",
    "project-lifecycle",
]

# State file that deep-interview creates when it runs
INTERVIEW_STATE = os.path.join(os.getcwd(), ".tmp", "deep-interview-state.json")

# Session tracker -- once user explicitly skips, don't nag again this session
SKIP_TRACKER = os.path.join(
    os.environ.get("TEMP", os.environ.get("TMP", "/tmp")),
    "claude_deep_interview_skip.json"
)


def _interview_ran():
    """Check if deep-interview has run (state file exists with current data)."""
    return os.path.isfile(INTERVIEW_STATE)


def _already_skipped():
    """Check if user already acknowledged the skip this session."""
    if not os.path.isfile(SKIP_TRACKER):
        return False
    try:
        with open(SKIP_TRACKER, "r") as f:
            data = json.load(f)
        return data.get("skipped", False)
    except (json.JSONDecodeError, IOError):
        return False


def _mark_skipped():
    """Record that user was reminded and proceeded anyway."""
    try:
        os.makedirs(os.path.dirname(SKIP_TRACKER), exist_ok=True)
        with open(SKIP_TRACKER, "w") as f:
            json.dump({"skipped": True}, f)
    except IOError:
        pass


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only act on Skill tool calls
    if tool_name != "Skill":
        sys.exit(0)

    # Get which skill is being invoked
    skill_name = tool_input.get("skill", "")

    # Check if it's a planning/design skill
    is_planning_skill = False
    for ps in PLANNING_SKILLS:
        if skill_name == ps or skill_name.endswith(":" + ps):
            is_planning_skill = True
            break

    if not is_planning_skill:
        sys.exit(0)

    # If deep-interview already ran, no reminder needed
    if _interview_ran():
        sys.exit(0)

    # If user already skipped the reminder this session, don't nag
    if _already_skipped():
        sys.exit(0)

    # Mark that we've shown the reminder (won't nag again this session)
    _mark_skipped()

    # Inject the reminder
    reminder = {
        "hookSpecificOutput": {
            "additionalContext": (
                "REQUIREMENTS CHECK: /deep-interview has NOT run this session. "
                "You are about to invoke '" + skill_name + "' which is a planning/design skill. "
                "If the user's request is vague or underspecified (missing scope, constraints, "
                "success criteria, or edge cases), consider running /deep-interview first to "
                "clarify requirements. This prevents building the wrong thing. "
                "If requirements are already clear and specific, proceed -- this is a reminder, "
                "not a block."
            )
        }
    }
    print(json.dumps(reminder))


if __name__ == "__main__":
    main()
