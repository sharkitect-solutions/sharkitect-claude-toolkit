"""End-to-end integration tests for userpromptsubmit-dispatcher (stdin/stdout)."""
import json
import subprocess
from pathlib import Path

HOOK_PATH = Path.home() / ".claude" / "hooks" / "userpromptsubmit-dispatcher.py"


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
    assert "additionalContext" in output
    assert output["additionalContext"]  # non-empty
    assert "verify" in output["additionalContext"].lower()


def test_dispatcher_stdin_stdout_non_state_silent():
    """Non-state prompt -> empty additionalContext."""
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
    assert output.get("additionalContext", "") == ""


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
