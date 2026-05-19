"""Tests for airtable-create-field-guard hook (replaces mcp-limitation-guard)."""
import json
import subprocess
from pathlib import Path

HOOK_PATH = Path.home() / ".claude" / "hooks" / "airtable-create-field-guard.py"


def _run(stdin_payload):
    return subprocess.run(
        ["python", str(HOOK_PATH)],
        input=json.dumps(stdin_payload),
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_fires_on_formula_field_creation():
    """Airtable create_field with type=formula -> additionalContext injected."""
    result = _run({
        "tool_name": "mcp__claude_ai_Airtable__create_field",
        "tool_input": {"baseId": "appXYZ", "tableId": "tblABC", "name": "Total", "type": "formula"},
    })
    assert result.returncode == 0
    out = json.loads(result.stdout)
    ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") or out.get("additionalContext", "")
    assert "formula" in ctx.lower()
    assert "airtable" in ctx.lower() or "ui" in ctx.lower()


def test_fires_on_rollup_field_creation():
    """type=rollup -> nudge fires."""
    result = _run({
        "tool_name": "mcp__claude_ai_Airtable__create_field",
        "tool_input": {"baseId": "appXYZ", "tableId": "tblABC", "name": "Sum", "type": "rollup"},
    })
    assert result.returncode == 0
    out = json.loads(result.stdout)
    ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") or out.get("additionalContext", "")
    assert "rollup" in ctx.lower()


def test_fires_on_lookup_field_creation():
    """type=lookup -> nudge fires."""
    result = _run({
        "tool_name": "mcp__claude_ai_Airtable__create_field",
        "tool_input": {"baseId": "appXYZ", "tableId": "tblABC", "name": "Linked", "type": "lookup"},
    })
    assert result.returncode == 0
    out = json.loads(result.stdout)
    ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") or out.get("additionalContext", "")
    assert "lookup" in ctx.lower()


def test_silent_on_allowed_field_types():
    """type=singleLineText / number / etc. -> hook stays silent."""
    for allowed_type in ("singleLineText", "number", "checkbox", "email", "phoneNumber", "url"):
        result = _run({
            "tool_name": "mcp__claude_ai_Airtable__create_field",
            "tool_input": {"baseId": "appXYZ", "tableId": "tblABC", "name": "X", "type": allowed_type},
        })
        assert result.returncode == 0
        out = json.loads(result.stdout)
        ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") or out.get("additionalContext", "")
        assert ctx == "", f"Should be silent for type={allowed_type}, got: {ctx!r}"


def test_silent_on_non_airtable_tools():
    """Any tool_name not matching exact Airtable create_field -> silent."""
    for tn in (
        "Bash",
        "Write",
        "Edit",
        "mcp__claude_ai_Airtable__list_bases",
        "mcp__claude_ai_Airtable__update_field",  # update_field is allowed
        "mcp__claude_ai_Slack__slack_send_message",
        "mcp__claude_ai_Airtable__create_records_for_table",
    ):
        result = _run({"tool_name": tn, "tool_input": {"type": "formula"}})
        assert result.returncode == 0
        out = json.loads(result.stdout)
        ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") or out.get("additionalContext", "")
        assert ctx == "", f"Should be silent for tool={tn}, got: {ctx!r}"


def test_silent_when_field_type_missing():
    """No type key in tool_input -> graceful silent (don't crash)."""
    result = _run({
        "tool_name": "mcp__claude_ai_Airtable__create_field",
        "tool_input": {"baseId": "appXYZ", "tableId": "tblABC", "name": "X"},
    })
    assert result.returncode == 0
    out = json.loads(result.stdout)
    ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") or out.get("additionalContext", "")
    assert ctx == ""


def test_handles_fieldType_alt_key():
    """Some MCP variants use fieldType instead of type -> still detected."""
    result = _run({
        "tool_name": "mcp__claude_ai_Airtable__create_field",
        "tool_input": {"baseId": "appXYZ", "tableId": "tblABC", "name": "X", "fieldType": "formula"},
    })
    assert result.returncode == 0
    out = json.loads(result.stdout)
    ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") or out.get("additionalContext", "")
    assert "formula" in ctx.lower()


def test_case_insensitive_type_match():
    """type='Formula' or 'FORMULA' still matches."""
    for variant in ("Formula", "FORMULA", "formula", "Rollup", "LOOKUP"):
        result = _run({
            "tool_name": "mcp__claude_ai_Airtable__create_field",
            "tool_input": {"name": "X", "type": variant},
        })
        out = json.loads(result.stdout)
        ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") or out.get("additionalContext", "")
        assert ctx != "", f"Should fire for type={variant!r}"


def test_handles_malformed_stdin_gracefully():
    """Bad JSON on stdin -> graceful empty output (don't crash)."""
    result = subprocess.run(
        ["python", str(HOOK_PATH)],
        input="not json at all",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0


def test_does_not_match_bash_with_formula_keyword():
    """The OLD false-positive case: Bash command containing 'rollup' or 'formula' in DATA -> silent."""
    result = _run({
        "tool_name": "Bash",
        "tool_input": {"command": "echo 'my message mentions rollup and formula and policy'"},
    })
    assert result.returncode == 0
    out = json.loads(result.stdout)
    ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") or out.get("additionalContext", "")
    assert ctx == "", f"Bash with keyword in data must NOT fire (the whole point of the rewrite). Got: {ctx!r}"
