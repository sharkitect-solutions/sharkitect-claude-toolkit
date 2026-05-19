#!/usr/bin/env python
"""
airtable-create-field-guard.py

PreToolUse structured guard: fires ONLY on the specific MCP tool call
`mcp__claude_ai_Airtable__create_field` when field type is one of the
documented limitations (formula, rollup, lookup) per ~/.claude/rules/api-limitations.md.

Replaces the retired mcp-limitation-guard.py, whose generic-keyword-on-Bash-command
matcher false-positive'd on benign commands whose data text happened to contain
words like 'rollup' or 'formula' (e.g., Slack message bodies, commit messages,
doc edits about the rollup/formula concepts).

Architecture: matches tool_name + structured tool_input fields, not command
string regex. Mirrors the methodology-dispatcher sub-rule contract pattern
(structured input → structured decision → additionalContext injection).

Source: wr-skillhub-2026-05-19-002 (BUG, Option B selected by user 2026-05-18 S58).
Aligned with: universal-protocols.md Hook Introduction Rule (narrow matcher,
advisory default, no kitchen-sink); methodology-dispatcher.py reference pattern.

Input: PreToolUse JSON on stdin with tool_name + tool_input.
Output: JSON on stdout. When firing, emits additionalContext via
hookSpecificOutput per Claude Code PreToolUse contract.
"""
import json
import sys

TARGET_TOOL = "mcp__claude_ai_Airtable__create_field"

# Documented Airtable limitations per ~/.claude/rules/api-limitations.md
# These types cannot be created via the Airtable API/MCP regardless of plan tier.
LIMITED_FIELD_TYPES = {"formula", "rollup", "lookup"}

# tool_input keys that MCP variants may use for field type
FIELD_TYPE_KEYS = ("type", "fieldType", "field_type")


def _extract_field_type(tool_input):
    """Pull the field type from any of the documented keys; case-fold for match."""
    if not isinstance(tool_input, dict):
        return None
    for key in FIELD_TYPE_KEYS:
        val = tool_input.get(key)
        if isinstance(val, str) and val:
            return val.lower()
    return None


def _build_nudge_message(field_type):
    """Build the api-limitation context message."""
    return (
        f"KNOWN AIRTABLE API LIMITATION: Cannot create field of type '{field_type}' "
        f"via the Airtable API or MCP. Documented in ~/.claude/rules/api-limitations.md. "
        f"Manual workaround: provide the user with Airtable UI steps (Field menu → "
        f"Customize field type → select '{field_type}' → configure source field / "
        f"formula expression / linked record). Do not attempt the API call — it will fail."
    )


def main():
    # Read stdin
    try:
        data = json.load(sys.stdin)
    except Exception:
        # Malformed input → silent empty response (don't crash)
        print(json.dumps({}))
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name != TARGET_TOOL:
        # Not our concern — stay silent
        print(json.dumps({}))
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    field_type = _extract_field_type(tool_input)
    if field_type is None:
        # No type provided — let the underlying MCP handle validation
        print(json.dumps({}))
        sys.exit(0)

    if field_type not in LIMITED_FIELD_TYPES:
        # Allowed field type — silent pass
        print(json.dumps({}))
        sys.exit(0)

    # Match: emit advisory additionalContext (does NOT block — AI may still
    # proceed with manual instructions per the api-limitations protocol)
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": _build_nudge_message(field_type),
        }
    }
    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
