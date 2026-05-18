"""Characterization tests for _dispatchers/content_governance/content_pitching.py.

PINs the behavior of the original content-pitching-detector.py so the
Build #2A lift preserves it bit-for-bit. The source hook is an ADVISORY
nudge fired when recent assistant messages show client-facing-content
pitching patterns AND no content-enforcer skill was invoked AND the
session hasn't already been nudged.

Sub-rule contract per Phase 2 spec:
    evaluate(payload: dict) -> dict | None

Source: ~/.claude/hooks/content-pitching-detector.py (263 LOC)
Source incident: wr-2026-04-19 (workforce-hq, UNUSED) -- HQ pitched 4
tagline candidates + FF brand palette without invoking hq-content-enforcer.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

import pytest

HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


@pytest.fixture
def isolated_home(tmp_path, monkeypatch):
    """Redirect HOME so state file + skill log resolve under tmp_path."""
    fake_tmp = tmp_path / ".claude" / ".tmp"
    fake_tmp.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    return fake_tmp


@pytest.fixture
def hq_cwd(tmp_path, monkeypatch):
    """Set cwd to a path that contains the HQ_MARKER 'SHARKITECT DIGITAL
    WORKFORCE HQ'. content-pitching-detector uses str(Path.cwd()) match."""
    hq = tmp_path / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
    hq.mkdir()
    monkeypatch.chdir(hq)
    return hq


def _write_transcript_with_assistant(tmp_path, assistant_messages):
    """Write a JSONL transcript with the given assistant messages. Returns path."""
    path = tmp_path / "transcript.jsonl"
    lines = []
    for msg in assistant_messages:
        lines.append(json.dumps({
            "type": "assistant",
            "message": {"content": msg},
        }))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def _write_skill_log(tmp_dir, skills):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_dir / f"skill-invocations-{today}.json"
    log_file.write_text(json.dumps({
        "invocations": [{"skill": s} for s in skills],
    }), encoding="utf-8")


# ---------------------------------------------------------------------------
# Tool filter
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("wrong_tool", ["Read", "Bash", "Glob", "Grep"])
def test_no_contribution_on_wrong_tool(isolated_home, hq_cwd, tmp_path, wrong_tool):
    from _dispatchers.content_governance import content_pitching as cp
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Here are 5 tagline options:\n1. Foo\n2. Bar\n3. Baz\n4. Qux\n5. Quux\n"
    ])
    payload = {
        "tool_name": wrong_tool,
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is None


@pytest.mark.parametrize("right_tool", ["Edit", "Write", "TodoWrite"])
def test_fires_on_each_supported_tool(isolated_home, hq_cwd, tmp_path, right_tool):
    from _dispatchers.content_governance import content_pitching as cp
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Here are 5 tagline options:\n1. Foo\n2. Bar\n3. Baz\n4. Qux\n5. Quux\n"
    ])
    payload = {
        "tool_name": right_tool,
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    result = cp.evaluate(payload)
    assert result is not None
    assert "advisory" in result


# ---------------------------------------------------------------------------
# HQ-workspace scoping
# ---------------------------------------------------------------------------

def test_no_contribution_outside_hq_workspace(isolated_home, tmp_path, monkeypatch):
    from _dispatchers.content_governance import content_pitching as cp
    non_hq = tmp_path / "3.- Skill Management Hub"
    non_hq.mkdir()
    monkeypatch.chdir(non_hq)
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Here are 5 tagline options:\n1. A\n2. B\n3. C\n4. D\n5. E\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Pitching pattern: keyword + (2+ Option/Candidate labels OR 3+ numbered)
# ---------------------------------------------------------------------------

def test_fires_on_keyword_plus_3_numbered_list_items(isolated_home, hq_cwd, tmp_path):
    """tagline keyword + 3 plain numbered items -> advisory."""
    from _dispatchers.content_governance import content_pitching as cp
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Here are 3 tagline candidates for you:\n"
        "1. First\n"
        "2. Second\n"
        "3. Third\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is not None


def test_fires_on_keyword_plus_2_option_labels(isolated_home, hq_cwd, tmp_path):
    """tagline keyword + 2 'Option X:' labels -> advisory."""
    from _dispatchers.content_governance import content_pitching as cp
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Tagline options:\n"
        "Option A: First idea\n"
        "Option B: Second idea\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is not None


@pytest.mark.parametrize("keyword_message", [
    "Slogan options:\nOption 1: A\nOption 2: B\n",
    "Headline candidates:\nCandidate A: X\nCandidate B: Y\n",
    "Here are brand color options:\n1. Red\n2. Blue\n3. Green\n",
    "Brand palette ideas:\n1. Warm\n2. Cool\n3. Neutral\n",
    "Value prop variants:\nVariant 1: a\nVariant 2: b\n",
    "Brand voice ideas:\n1. Direct\n2. Friendly\n3. Witty\n",
    "Copy candidate set:\n1. v1\n2. v2\n3. v3\n",
    "Copy option set:\nPitch 1: X\nPitch 2: Y\n",
])
def test_fires_on_various_content_keywords(isolated_home, hq_cwd, tmp_path, keyword_message):
    from _dispatchers.content_governance import content_pitching as cp
    transcript = _write_transcript_with_assistant(tmp_path, [keyword_message])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is not None


def test_no_contribution_on_keyword_without_enumeration(isolated_home, hq_cwd, tmp_path):
    """tagline keyword but NO 2+ labels and NO 3+ numbered -> no fire."""
    from _dispatchers.content_governance import content_pitching as cp
    transcript = _write_transcript_with_assistant(tmp_path, [
        "The tagline should be punchy. Let me think about it.\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is None


def test_no_contribution_on_enumeration_without_keyword(isolated_home, hq_cwd, tmp_path):
    """3 numbered items but NO content keyword -> no fire."""
    from _dispatchers.content_governance import content_pitching as cp
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Steps:\n1. Build it\n2. Test it\n3. Ship it\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Skill log bypass
# ---------------------------------------------------------------------------

def test_bypass_when_hq_content_enforcer_invoked(isolated_home, hq_cwd, tmp_path):
    from _dispatchers.content_governance import content_pitching as cp
    _write_skill_log(isolated_home, ["hq-content-enforcer"])
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Tagline options:\n1. A\n2. B\n3. C\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is None


def test_bypass_when_fallback_content_enforcer_invoked(isolated_home, hq_cwd, tmp_path):
    from _dispatchers.content_governance import content_pitching as cp
    _write_skill_log(isolated_home, ["content-enforcer"])
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Tagline options:\n1. A\n2. B\n3. C\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is None


# ---------------------------------------------------------------------------
# State debounce — already nudged this session -> no-op
# ---------------------------------------------------------------------------

def test_already_nudged_state_prevents_re_fire(isolated_home, hq_cwd, tmp_path):
    """If state shows nudged=True for today, do not fire again."""
    from _dispatchers.content_governance import content_pitching as cp
    today = datetime.now().strftime("%Y-%m-%d")
    state_file = isolated_home / "content-pitching-detector-state.json"
    state_file.write_text(json.dumps({"date": today, "nudged": True}),
                          encoding="utf-8")
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Tagline options:\n1. A\n2. B\n3. C\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is None


def test_stale_state_from_yesterday_does_not_suppress(isolated_home, hq_cwd, tmp_path):
    """State file with yesterday's date is treated as cleared."""
    from _dispatchers.content_governance import content_pitching as cp
    state_file = isolated_home / "content-pitching-detector-state.json"
    state_file.write_text(json.dumps({"date": "1999-01-01", "nudged": True}),
                          encoding="utf-8")
    transcript = _write_transcript_with_assistant(tmp_path, [
        "Tagline options:\n1. A\n2. B\n3. C\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is not None


# ---------------------------------------------------------------------------
# System-block stripping (source line 70-86)
# ---------------------------------------------------------------------------

def test_system_block_content_is_stripped_before_scan(isolated_home, hq_cwd, tmp_path):
    """Assistant message wrapping the pitching pattern inside a
    <system-reminder> block must NOT trigger (system blocks are stripped
    before keyword + enumeration scan)."""
    from _dispatchers.content_governance import content_pitching as cp
    transcript = _write_transcript_with_assistant(tmp_path, [
        "<system-reminder>\n"
        "Tagline options:\n1. A\n2. B\n3. C\n"
        "</system-reminder>\n"
    ])
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": transcript,
    }
    assert cp.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Defensive cases
# ---------------------------------------------------------------------------

def test_no_contribution_when_transcript_missing(isolated_home, hq_cwd):
    """No transcript_path field -> no-op (no messages to scan)."""
    from _dispatchers.content_governance import content_pitching as cp
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
    }
    assert cp.evaluate(payload) is None


def test_no_contribution_when_transcript_file_missing(isolated_home, hq_cwd, tmp_path):
    """transcript_path points to a non-existent file -> no-op."""
    from _dispatchers.content_governance import content_pitching as cp
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "x.md"},
        "transcript_path": str(tmp_path / "nonexistent.jsonl"),
    }
    assert cp.evaluate(payload) is None


def test_no_contribution_on_empty_payload(isolated_home, hq_cwd):
    from _dispatchers.content_governance import content_pitching as cp
    assert cp.evaluate({}) is None


def test_no_contribution_on_none_payload(isolated_home, hq_cwd):
    from _dispatchers.content_governance import content_pitching as cp
    assert cp.evaluate(None) is None
