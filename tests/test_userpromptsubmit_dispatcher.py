"""Tests for userpromptsubmit-dispatcher.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))
sys.path.insert(0, str(Path.home() / ".claude" / "tests"))

import pytest
from _subrule_test_fixtures import write_dispatcher_config


@pytest.fixture
def dispatcher_module():
    """Import the dispatcher fresh per test (it reads config at import-time)."""
    if "userpromptsubmit_dispatcher" in sys.modules:
        del sys.modules["userpromptsubmit_dispatcher"]
    # The hook file uses dashes; import by path
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "userpromptsubmit_dispatcher",
        Path.home() / ".claude" / "hooks" / "userpromptsubmit-dispatcher.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dispatcher_loads_config(dispatcher_module, tmp_path, monkeypatch):
    """Dispatcher reads ~/.claude/config/userpromptsubmit-dispatcher.json."""
    cfg_path = write_dispatcher_config(tmp_path, enabled_subrules=["sharkitect.verify_state"])
    monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

    cfg = dispatcher_module.load_config()
    assert cfg["enabled_subrules"] == ["sharkitect.verify_state"]


def test_dispatcher_returns_no_context_when_no_rule_fires(dispatcher_module, tmp_path, monkeypatch):
    """Prompt that doesn't trigger any sub-rule -> empty additionalContext."""
    cfg_path = write_dispatcher_config(tmp_path)
    monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

    result = dispatcher_module.run_dispatcher(
        prompt="write a python function to reverse a string",
        recent_tool_calls=[],
    )

    assert result.get("additionalContext", "") == ""


def test_dispatcher_emits_nudge_when_rule_fires(dispatcher_module, tmp_path, monkeypatch):
    """State-query prompt + no recent verify -> dispatcher emits verify_state nudge."""
    cfg_path = write_dispatcher_config(tmp_path)
    monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

    result = dispatcher_module.run_dispatcher(
        prompt="is the migration done?",
        recent_tool_calls=[],
    )

    ctx = result.get("additionalContext", "")
    assert "verify_state" in ctx or "verify" in ctx.lower()
    assert "skip verify-state" in ctx  # bypass discovery


def test_dispatcher_honors_bypass_phrase(dispatcher_module, tmp_path, monkeypatch):
    """Prompt containing 'skip verify-state' -> rule skipped, no nudge."""
    cfg_path = write_dispatcher_config(tmp_path)
    monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

    result = dispatcher_module.run_dispatcher(
        prompt="is the migration done? skip verify-state",
        recent_tool_calls=[],
    )

    assert result.get("additionalContext", "") == ""


def test_dispatcher_isolates_subrule_failures(dispatcher_module, tmp_path, monkeypatch, capsys):
    """A buggy sub-rule that raises does NOT crash the dispatcher."""
    # Create a buggy sub-rule
    buggy_dir = Path.home() / ".claude" / "hooks" / "_subrules" / "sharkitect"
    buggy_file = buggy_dir / "_test_buggy.py"
    buggy_file.write_text("def check(prompt, ctx): raise RuntimeError('boom')\n")
    try:
        cfg_path = write_dispatcher_config(tmp_path, enabled_subrules=[
            "sharkitect._test_buggy",
            "sharkitect.verify_state",
        ])
        monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

        # Should NOT raise, and verify_state should still fire
        result = dispatcher_module.run_dispatcher(
            prompt="is X done?",
            recent_tool_calls=[],
        )
        assert "verify" in result.get("additionalContext", "").lower()
    finally:
        buggy_file.unlink(missing_ok=True)


def test_dispatcher_logs_fires_to_telemetry(dispatcher_module, tmp_path, monkeypatch):
    """Every dispatcher invocation appends to hook-fire-log.jsonl."""
    cfg_path = write_dispatcher_config(tmp_path)
    monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))
    log_path = tmp_path / "hook-fire-log.jsonl"
    monkeypatch.setenv("HOOK_FIRE_LOG_PATH", str(log_path))

    dispatcher_module.run_dispatcher(
        prompt="is the build done?",
        recent_tool_calls=[],
    )

    assert log_path.exists()
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) >= 1
    record = json.loads(lines[-1])
    assert record["hook"] == "userpromptsubmit-dispatcher"
    assert record["event"] == "UserPromptSubmit"


def test_dispatcher_logs_bypasses_to_bypass_log(dispatcher_module, tmp_path, monkeypatch):
    """A bypass triggers a record in claude_bypass_log.jsonl."""
    cfg_path = write_dispatcher_config(tmp_path)
    monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))
    bypass_log = tmp_path / "claude_bypass_log.jsonl"
    monkeypatch.setenv("BYPASS_LOG_PATH", str(bypass_log))

    dispatcher_module.run_dispatcher(
        prompt="is X done? skip verify-state",
        recent_tool_calls=[],
    )

    assert bypass_log.exists()
    record = json.loads(bypass_log.read_text().strip().splitlines()[-1])
    assert record["gate"] == "verify-state"
    assert record["category"] == "A"


def test_dispatcher_multiple_subrules_aggregate(dispatcher_module, tmp_path, monkeypatch):
    """If multiple sub-rules fire, their nudges concatenate in additionalContext."""
    # Create a second test sub-rule that always fires
    test_dir = Path.home() / ".claude" / "hooks" / "_subrules" / "sharkitect"
    extra = test_dir / "_test_always_fire.py"
    extra.write_text(
        "from _subrules.sharkitect._contract import SubRuleResult\n"
        "def check(prompt, ctx):\n"
        "    return SubRuleResult(mode='advisory', message='ALWAYS-FIRES', "
        "rule_name='_test_always_fire', bypass_keyword='skip always')\n"
    )
    try:
        cfg_path = write_dispatcher_config(tmp_path, enabled_subrules=[
            "sharkitect.verify_state",
            "sharkitect._test_always_fire",
        ])
        monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

        result = dispatcher_module.run_dispatcher(
            prompt="is X done?",
            recent_tool_calls=[],
        )
        ctx = result.get("additionalContext", "")
        assert "verify" in ctx.lower()
        assert "ALWAYS-FIRES" in ctx
    finally:
        extra.unlink(missing_ok=True)
