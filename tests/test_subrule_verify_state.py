"""Tests for verify_state sub-rule."""
import sys
from pathlib import Path

# Ensure _subrules importable
sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))
sys.path.insert(0, str(Path.home() / ".claude" / "tests"))

from _subrule_test_fixtures import make_context, make_tool_call


def test_fires_when_state_claim_without_recent_verify():
    """User asks 'is X done?' with no recent Read/Grep/Bash -> rule fires."""
    from _subrules.sharkitect.verify_state import check

    ctx = make_context(recent_tool_calls=[
        make_tool_call("Edit"),
        make_tool_call("Write"),
        make_tool_call("TodoWrite"),
    ])
    prompt = "is the migration done yet?"

    result = check(prompt, ctx)

    assert result is not None
    assert result.mode == "advisory"
    assert result.rule_name == "verify_state"
    assert result.bypass_keyword == "skip verify-state"
    assert "verify" in result.message.lower() or "read" in result.message.lower()


def test_does_not_fire_when_recent_read_present():
    """Recent Read/Grep/Bash satisfies verification -> rule stays silent."""
    from _subrules.sharkitect.verify_state import check

    ctx = make_context(recent_tool_calls=[
        make_tool_call("Edit"),
        make_tool_call("Read", "path/to/relevant/file"),
        make_tool_call("TodoWrite"),
    ])
    prompt = "is the migration done?"

    result = check(prompt, ctx)

    assert result is None


def test_does_not_fire_on_non_state_prompts():
    """Prompt that isn't asking about state -> rule stays silent."""
    from _subrules.sharkitect.verify_state import check

    ctx = make_context(recent_tool_calls=[])
    prompt = "write me a python function to reverse a string"

    result = check(prompt, ctx)

    assert result is None


def test_fires_on_various_state_query_patterns():
    """Multiple state-query phrasings all trigger."""
    from _subrules.sharkitect.verify_state import check

    state_prompts = [
        "what's the status of the deployment",
        "did the migration land",
        "where are we at on the feature",
        "is the build complete",
        "has the WR been closed",
    ]
    ctx = make_context(recent_tool_calls=[])

    for prompt in state_prompts:
        result = check(prompt, ctx)
        assert result is not None, f"Should fire for: {prompt!r}"


def test_grep_satisfies_verification():
    """Recent Grep call counts as verification."""
    from _subrules.sharkitect.verify_state import check

    ctx = make_context(recent_tool_calls=[
        make_tool_call("Grep", "search pattern"),
    ])
    prompt = "is X done?"

    result = check(prompt, ctx)

    assert result is None


def test_bash_satisfies_verification():
    """Recent Bash call counts as verification."""
    from _subrules.sharkitect.verify_state import check

    ctx = make_context(recent_tool_calls=[
        make_tool_call("Bash", "ls -la"),
    ])
    prompt = "is X done?"

    result = check(prompt, ctx)

    assert result is None


def test_supabase_mcp_call_satisfies_verification():
    """Recent Supabase MCP call counts as verification."""
    from _subrules.sharkitect.verify_state import check

    ctx = make_context(recent_tool_calls=[
        make_tool_call("mcp__claude_ai_Supabase__execute_sql", "SELECT ..."),
    ])
    prompt = "is X complete in supabase?"

    result = check(prompt, ctx)

    assert result is None


def test_empty_context_still_works():
    """No tool calls at all + state prompt -> fires."""
    from _subrules.sharkitect.verify_state import check

    ctx = make_context()
    prompt = "what's the status"

    result = check(prompt, ctx)

    assert result is not None
