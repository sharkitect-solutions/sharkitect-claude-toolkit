"""Tests for _dispatchers/_signal_extract.py shared signal extraction.

TDD-first: these tests are written BEFORE _signal_extract.py exists. They
define the contract for the shared helper that runs ONCE per dispatcher
invocation and produces the `signals` dict consumed by every sub-rule.

Contract (extract):
  extract(payload: dict) -> dict
    - Pure function over payload. No I/O. Never raises.
    - Always returns a dict with the canonical keys (defaults applied for
      missing fields). Sub-rules read pre-computed signals instead of
      re-parsing tool_input themselves.

Contract (load_skill_log_today):
  load_skill_log_today(*, log_dir=None) -> list[str]
    - Reads ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json (override via
      log_dir kwarg for tests).
    - Returns lowercased skill names. Empty list on missing/malformed.
    - Never raises.

Canonical signal keys produced by extract():
  tool_name, tool_input, hook_event_name, session_id, transcript_path,
  file_path, file_path_lower, content_body, content_head, command,
  old_string, new_string, is_excluded_path

Source: Phase 2 architecture spec
docs/superpowers/specs/2026-05-15-phase-2-architecture-spec.md Part A.3.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

import pytest

# Make the hooks/ dir importable for the _dispatchers package
HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


# ---------------------------------------------------------------------------
# extract() contract
# ---------------------------------------------------------------------------

def test_extract_returns_all_canonical_keys_on_empty_payload():
    """Even an empty payload must yield the canonical signal shape so sub-rules
    can read signals['file_path'] without KeyError defenses."""
    from _dispatchers import _signal_extract as sx
    out = sx.extract({})
    expected_keys = {
        "tool_name", "tool_input", "hook_event_name", "session_id",
        "transcript_path", "file_path", "file_path_lower", "content_body",
        "content_head", "command", "old_string", "new_string",
        "is_excluded_path",
    }
    assert expected_keys.issubset(out.keys())
    assert out["tool_name"] == ""
    assert out["tool_input"] == {}
    assert out["file_path"] == ""
    assert out["content_body"] == ""
    assert out["is_excluded_path"] is False


def test_extract_never_raises_on_none_payload():
    """payload=None must yield defaults, not crash. Dispatcher fail-OPEN
    semantics: signals always exist."""
    from _dispatchers import _signal_extract as sx
    out = sx.extract(None)
    assert isinstance(out, dict)
    assert out["tool_name"] == ""
    assert out["tool_input"] == {}


def test_extract_pulls_tool_name_and_hook_event_and_session():
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "session_id": "sess-abc",
        "transcript_path": "/tmp/transcript.jsonl",
    })
    assert out["tool_name"] == "Write"
    assert out["hook_event_name"] == "PreToolUse"
    assert out["session_id"] == "sess-abc"
    assert out["transcript_path"] == "/tmp/transcript.jsonl"


def test_extract_parses_tool_input_as_dict():
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Write",
        "tool_input": {"file_path": "/x.py", "content": "print(1)"},
    })
    assert out["tool_input"] == {"file_path": "/x.py", "content": "print(1)"}
    assert out["file_path"] == "/x.py"
    assert out["content_body"] == "print(1)"


def test_extract_parses_tool_input_when_string():
    """methodology-nudge.py defensively json.loads tool_input when it arrives
    as a string. Carry the same defense forward."""
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Write",
        "tool_input": json.dumps({"file_path": "/y.md", "content": "hi"}),
    })
    assert out["file_path"] == "/y.md"
    assert out["content_body"] == "hi"


def test_extract_defaults_tool_input_when_malformed_string():
    """If tool_input is a string but not valid JSON, default to {}."""
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Write",
        "tool_input": "{this is not json",
    })
    assert out["tool_input"] == {}
    assert out["file_path"] == ""


def test_extract_defaults_tool_input_when_none():
    from _dispatchers import _signal_extract as sx
    out = sx.extract({"tool_name": "Write", "tool_input": None})
    assert out["tool_input"] == {}


def test_extract_file_path_normalized_to_forward_slashes():
    """Windows-style backslash paths normalize to forward slashes so a single
    regex pattern matches across both platforms."""
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Edit",
        "tool_input": {"file_path": r"C:\Users\X\.claude\hooks\foo.py"},
    })
    assert out["file_path"] == "C:/Users/X/.claude/hooks/foo.py"


def test_extract_file_path_lower_provided_for_case_insensitive_matching():
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Edit",
        "tool_input": {"file_path": "/Workspace/Plan.MD"},
    })
    assert out["file_path"] == "/Workspace/Plan.MD"
    assert out["file_path_lower"] == "/workspace/plan.md"


def test_extract_content_body_falls_back_to_new_string_for_edit():
    """For Edit tool: tool_input has new_string but no content key. Mirror
    methodology-nudge.py line 508: `content or new_string`."""
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "/z.py",
            "old_string": "foo",
            "new_string": "bar baz quux",
        },
    })
    assert out["content_body"] == "bar baz quux"
    assert out["old_string"] == "foo"
    assert out["new_string"] == "bar baz quux"


def test_extract_content_body_prefers_content_over_new_string_when_both_present():
    """Edge case mirroring source-of-truth: `content or new_string` means
    content wins when truthy."""
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Write",
        "tool_input": {
            "file_path": "/q.py",
            "content": "WIN",
            "new_string": "LOSE",
        },
    })
    assert out["content_body"] == "WIN"


def test_extract_content_head_capped_at_2000_chars():
    """content_head is the regex-prep slice; long files must not blow up
    every sub-rule's regex scan."""
    from _dispatchers import _signal_extract as sx
    long_content = "a" * 5000
    out = sx.extract({
        "tool_name": "Write",
        "tool_input": {"file_path": "/big.txt", "content": long_content},
    })
    assert len(out["content_head"]) == 2000
    assert out["content_head"] == "a" * 2000
    # Full body still preserved for sub-rules that need it
    assert len(out["content_body"]) == 5000


def test_extract_content_head_shorter_than_2000_returns_full():
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Write",
        "tool_input": {"file_path": "/s.txt", "content": "short"},
    })
    assert out["content_head"] == "short"
    assert out["content_body"] == "short"


def test_extract_command_extracted_for_bash():
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la /tmp"},
    })
    assert out["command"] == "ls -la /tmp"
    # Bash has no file_path / content; those default
    assert out["file_path"] == ""
    assert out["content_body"] == ""


# ---------------------------------------------------------------------------
# is_excluded_path canonical exclusion set
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("excluded_path", [
    "/Users/me/repo/.tmp/scratch.json",
    "/Users/me/repo/.git/HEAD",
    "/Users/me/repo/node_modules/lib/index.js",
    "/Users/me/repo/__pycache__/foo.pyc",
    "/Users/me/repo/.work-requests/processed/wr-1.json",
    "/Users/me/repo/.routed-tasks/inbox/rt-1.json",
    "/Users/me/repo/.work-requests/outbox/audit.md",
    "/Users/me/repo/MEMORY.md",
    "/Users/me/repo/CLAUDE.md",
    "/Users/me/repo/memory/feedback_x.md",  # under /memory/ — also excluded per methodology-nudge precedent
    r"C:\Users\me\repo\.tmp\scratch.json",   # Windows backslash form
])
def test_extract_is_excluded_path_true_for_canonical_excludes(excluded_path):
    """The canonical exclusion set must match methodology-nudge.is_excluded_path
    so sub-rules continue to skip these paths uniformly."""
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Write",
        "tool_input": {"file_path": excluded_path, "content": "x"},
    })
    assert out["is_excluded_path"] is True, f"expected exclusion for {excluded_path}"


@pytest.mark.parametrize("normal_path", [
    "/Users/me/repo/src/main.py",
    "/Users/me/repo/docs/spec.md",
    "/Users/me/repo/tools/helper.py",
    "/Users/me/repo/.claude/skills/my-skill/SKILL.md",  # .claude/skills is content, not excluded
    "",  # empty path is not excluded
])
def test_extract_is_excluded_path_false_for_normal_paths(normal_path):
    from _dispatchers import _signal_extract as sx
    out = sx.extract({
        "tool_name": "Write",
        "tool_input": {"file_path": normal_path, "content": "x"},
    })
    assert out["is_excluded_path"] is False, f"unexpected exclusion for {normal_path}"


# ---------------------------------------------------------------------------
# load_skill_log_today() contract
# ---------------------------------------------------------------------------

def test_load_skill_log_today_returns_empty_when_dir_missing(tmp_path):
    """Missing log dir is the common bootstrap case. Empty list, no crash."""
    from _dispatchers import _signal_extract as sx
    out = sx.load_skill_log_today(log_dir=str(tmp_path / "does_not_exist"))
    assert out == []


def test_load_skill_log_today_returns_empty_when_file_missing(tmp_path):
    """Dir exists but today's log file does not. Empty list."""
    from _dispatchers import _signal_extract as sx
    out = sx.load_skill_log_today(log_dir=str(tmp_path))
    assert out == []


def test_load_skill_log_today_returns_lowercased_skill_names(tmp_path):
    """Skill names lowercased so callers can compare without re-lowering."""
    from _dispatchers import _signal_extract as sx
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / f"skill-invocations-{today}.json"
    log_file.write_text(json.dumps({
        "invocations": [
            {"skill": "SuperPowers:Brainstorming"},
            {"skill": "Writing-Plans"},
            {"skill": "supabase-postgres-best-practices"},
        ],
    }), encoding="utf-8")
    out = sx.load_skill_log_today(log_dir=str(tmp_path))
    assert "superpowers:brainstorming" in out
    assert "writing-plans" in out
    assert "supabase-postgres-best-practices" in out


def test_load_skill_log_today_returns_empty_on_malformed_json(tmp_path):
    """Malformed JSON must not crash the dispatcher."""
    from _dispatchers import _signal_extract as sx
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / f"skill-invocations-{today}.json"
    log_file.write_text("not valid json", encoding="utf-8")
    out = sx.load_skill_log_today(log_dir=str(tmp_path))
    assert out == []


def test_load_skill_log_today_handles_missing_invocations_key(tmp_path):
    """JSON parses but lacks 'invocations' key. Empty list, no crash."""
    from _dispatchers import _signal_extract as sx
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / f"skill-invocations-{today}.json"
    log_file.write_text(json.dumps({"other_key": "x"}), encoding="utf-8")
    out = sx.load_skill_log_today(log_dir=str(tmp_path))
    assert out == []


def test_load_skill_log_today_skips_entries_with_missing_skill_field(tmp_path):
    """Records lacking a 'skill' key are skipped, not crashed on."""
    from _dispatchers import _signal_extract as sx
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / f"skill-invocations-{today}.json"
    log_file.write_text(json.dumps({
        "invocations": [
            {"skill": "good-skill"},
            {"other_field": "no skill key"},
            {"skill": "another-good"},
        ],
    }), encoding="utf-8")
    out = sx.load_skill_log_today(log_dir=str(tmp_path))
    assert "good-skill" in out
    assert "another-good" in out


# ---------------------------------------------------------------------------
# Determinism / purity — same input yields same output
# ---------------------------------------------------------------------------

def test_extract_is_deterministic():
    """Same payload twice -> identical output dicts. Confirms no hidden state."""
    from _dispatchers import _signal_extract as sx
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/x.py", "content": "y"},
        "session_id": "s1",
    }
    a = sx.extract(payload)
    b = sx.extract(payload)
    assert a == b
