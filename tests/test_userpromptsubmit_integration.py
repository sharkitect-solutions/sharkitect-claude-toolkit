"""End-to-end integration tests for userpromptsubmit-dispatcher (stdin/stdout).

CRITICAL: tests assert the Claude Code UserPromptSubmit harness contract,
which requires nudges to be wrapped in:
    {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "..."}}
Bare {"additionalContext": "..."} is silently dropped by the harness.
"""
import json
import subprocess
from pathlib import Path

HOOK_PATH = Path.home() / ".claude" / "hooks" / "userpromptsubmit-dispatcher.py"


def test_dispatcher_emits_harness_contract_envelope():
    """Stdout MUST use hookSpecificOutput.{hookEventName,additionalContext} per Claude Code contract."""
    input_json = json.dumps({"prompt": "is the migration done?"})
    result = subprocess.run(
        ["python", str(HOOK_PATH)],
        input=input_json,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    # Harness contract: nested under hookSpecificOutput
    assert "hookSpecificOutput" in output, f"Missing hookSpecificOutput envelope. Got: {output}"
    hso = output["hookSpecificOutput"]
    assert hso.get("hookEventName") == "UserPromptSubmit", f"Wrong hookEventName: {hso}"
    assert "additionalContext" in hso, f"Missing additionalContext under hookSpecificOutput: {hso}"
    assert hso["additionalContext"], "additionalContext should be non-empty for state query"
    assert "verify" in hso["additionalContext"].lower()


def test_dispatcher_stdin_stdout_state_query_fires_nudge():
    """Pipe a state-query prompt via stdin, expect a nudge in stdout."""
    input_json = json.dumps({"prompt": "is the migration done?"})
    result = subprocess.run(
        ["python", str(HOOK_PATH)],
        input=input_json,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    nudge = output.get("hookSpecificOutput", {}).get("additionalContext", "")
    assert nudge, f"Expected non-empty nudge; got {output}"
    assert "verify" in nudge.lower()


def test_dispatcher_stdin_stdout_non_state_silent():
    """Non-state prompt -> no nudge (empty additionalContext or no envelope)."""
    input_json = json.dumps({"prompt": "write me a quicksort in python"})
    result = subprocess.run(
        ["python", str(HOOK_PATH)],
        input=input_json,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    nudge = output.get("hookSpecificOutput", {}).get("additionalContext", "")
    assert nudge == ""


def test_dispatcher_accepts_user_prompt_field_name():
    """Real harness uses field 'user_prompt' on some Claude Code versions."""
    # Note: methodology-dispatcher and cron-context-enforcer accept both 'prompt' and 'user_prompt'
    input_json = json.dumps({"user_prompt": "is the migration done?"})
    result = subprocess.run(
        ["python", str(HOOK_PATH)],
        input=input_json,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    nudge = output.get("hookSpecificOutput", {}).get("additionalContext", "")
    assert "verify" in nudge.lower(), f"Expected nudge when prompt is in user_prompt field; got {output}"


def test_dispatcher_handles_malformed_stdin():
    """Bad JSON on stdin -> graceful exit, empty output."""
    result = subprocess.run(
        ["python", str(HOOK_PATH)],
        input="this is not json",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "{}"


def test_dispatcher_handles_empty_stdin():
    """No stdin -> graceful exit."""
    result = subprocess.run(
        ["python", str(HOOK_PATH)],
        input="",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
