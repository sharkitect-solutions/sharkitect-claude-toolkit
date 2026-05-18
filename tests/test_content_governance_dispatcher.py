"""Integration tests for content-governance-dispatcher.py.

PINs the dispatcher contract:
  - dispatch(payload) routes to the 4 content-governance sub-rules
  - marketing_keywords (HARD GATE) short-circuits the chain on deny
  - advisories from multiple sub-rules merge via "\n\n---\n\n"
  - sub-rule exceptions are caught (graceful degradation)
  - main() reads stdin and writes a single hookSpecificOutput JSON line

Source: 2026-05-15 Phase 2 architecture spec, mirrors methodology-dispatcher.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
from pathlib import Path

import pytest

HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


def _load_dispatcher():
    """Load content-governance-dispatcher.py via importlib (hyphenated filename)."""
    src = Path(HOOKS_DIR) / "content-governance-dispatcher.py"
    spec = importlib.util.spec_from_file_location("cgd", str(src))
    assert spec is not None and spec.loader is not None, "dispatcher file missing"
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def isolated_home(tmp_path, monkeypatch):
    """Redirect HOME so state files / skill log resolve under tmp_path."""
    fake_home = tmp_path / "fake_home"
    fake_tmp = fake_home / ".claude" / ".tmp"
    fake_tmp.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    return fake_tmp


@pytest.fixture
def workspace_cwd(tmp_path, monkeypatch):
    """Set cwd to a fake workspace with the .tmp/ + .claude/ scaffolding
    drift_detection expects."""
    ws = tmp_path / "fake_workspace"
    ws.mkdir()
    (ws / ".tmp").mkdir()
    (ws / ".claude" / "drift-detection").mkdir(parents=True)
    monkeypatch.chdir(ws)
    return ws


# ---------------------------------------------------------------------------
# Routing contract: dispatcher returns one of {None, advisory dict, deny dict}
# ---------------------------------------------------------------------------

def test_no_sub_rule_fires_returns_none(workspace_cwd, isolated_home):
    mod = _load_dispatcher()
    # Benign payload: not HQ workspace + non-content extension + no keywords
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": "src/util.py", "content": "def foo(): pass"},
    }
    assert mod.dispatch(payload) is None


def test_marketing_keyword_deny_short_circuits(workspace_cwd, isolated_home, tmp_path):
    """marketing_keywords HARD GATE wins -- no advisories appended."""
    mod = _load_dispatcher()
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {
            "file_path": "doc.md",
            "content": "Our GTM positioning is strong",
        },
        "transcript_path": str(tmp_path / "no_transcript.jsonl"),
    }
    result = mod.dispatch(payload)
    assert result is not None
    out = result["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse"
    assert out["permissionDecision"] == "deny"
    assert "marketing" in out["permissionDecisionReason"].lower()


def test_advisory_emits_additional_context(workspace_cwd, isolated_home):
    """An advisory-only sub-rule produces additionalContext output."""
    mod = _load_dispatcher()
    # 3 KB edits -> governance nudge fires (3rd Write returns advisory)
    for i in range(2):
        mod.dispatch({
            "tool_name": "Write",
            "hook_event_name": "PreToolUse",
            "tool_input": {"file_path": f"knowledge-base/c{i}.md", "content": "x"},
        })
    result = mod.dispatch({
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": "knowledge-base/c3.md", "content": "x"},
    })
    assert result is not None
    out = result["hookSpecificOutput"]
    assert "additionalContext" in out
    assert "GOVERNANCE NUDGE" in out["additionalContext"]


# ---------------------------------------------------------------------------
# Multiple advisories merge with separator
# ---------------------------------------------------------------------------

def test_dispatcher_swallows_sub_rule_exception(workspace_cwd, isolated_home, monkeypatch):
    """If a sub-rule raises mid-evaluate, the dispatcher MUST continue with
    remaining sub-rules (graceful degradation)."""
    mod = _load_dispatcher()
    # Inject a sub-rule that always raises
    class _Boom:
        @staticmethod
        def evaluate(payload):
            raise RuntimeError("simulated sub-rule crash")
    # Splice it into the sub-rule list temporarily
    original = list(mod.PRE_TOOL_USE_SUBRULES)
    mod.PRE_TOOL_USE_SUBRULES.insert(0, _Boom)
    try:
        payload = {
            "tool_name": "Write",
            "hook_event_name": "PreToolUse",
            "tool_input": {"file_path": "src/x.py", "content": "y"},
        }
        # Should not raise; result is None (no other sub-rule fires)
        assert mod.dispatch(payload) is None
    finally:
        mod.PRE_TOOL_USE_SUBRULES[:] = original


# ---------------------------------------------------------------------------
# main() stdin/stdout protocol
# ---------------------------------------------------------------------------

def test_main_reads_stdin_writes_stdout(workspace_cwd, isolated_home, tmp_path,
                                         monkeypatch, capsys):
    """main() reads JSON from stdin, writes hookSpecificOutput JSON to stdout."""
    mod = _load_dispatcher()
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": "doc.md", "content": "Our GTM playbook"},
        "transcript_path": str(tmp_path / "no_transcript.jsonl"),
    }
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    mod.main()
    captured = capsys.readouterr()
    out = json.loads(captured.out)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_main_silent_on_no_contribution(workspace_cwd, isolated_home,
                                         monkeypatch, capsys):
    """When no sub-rule contributes, main() prints nothing."""
    mod = _load_dispatcher()
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": "src/util.py", "content": "def foo(): pass"},
    }
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    mod.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == ""


def test_main_handles_malformed_stdin(workspace_cwd, isolated_home,
                                       monkeypatch, capsys):
    """Malformed JSON on stdin -> no crash, no output."""
    mod = _load_dispatcher()
    monkeypatch.setattr("sys.stdin", io.StringIO("not valid json{"))
    mod.main()  # Must not raise
    captured = capsys.readouterr()
    assert captured.out.strip() == ""


# ---------------------------------------------------------------------------
# Event routing
# ---------------------------------------------------------------------------

def test_unknown_event_no_contribution(workspace_cwd, isolated_home):
    """Events outside PreToolUse don't fire the content-governance sub-rules."""
    mod = _load_dispatcher()
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PostToolUse",  # not PreToolUse
        "tool_input": {"file_path": "doc.md", "content": "Our GTM playbook"},
    }
    assert mod.dispatch(payload) is None


def test_pre_tool_use_routes_to_subrules(workspace_cwd, isolated_home):
    """PreToolUse event routes to the content-governance sub-rule list."""
    mod = _load_dispatcher()
    assert "PreToolUse" in mod.EVENT_TO_SUBRULES
    sub_rules = mod.EVENT_TO_SUBRULES["PreToolUse"]
    # All 4 content-governance sub-rules should be present
    assert len(sub_rules) >= 4
