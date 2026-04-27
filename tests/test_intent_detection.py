"""Tests for intent_detection.py shared user-driven-mode helper.

Module: ~/.claude/scripts/_lib/intent_detection.py
Filed via: wr-hq-2026-04-27-003 (deferred design portion)

Test architecture: classic pyramid -- this is a library, all unit tests, no
external dependencies. Pure-function design makes mocking unnecessary.

Coverage targets:
  - read_recent_user_messages: transcript parsing edge cases
  - _is_tool_result_message: tool-result filter
  - _file_aliases: filename alias generation
  - _has_session_intent: session intent detection
  - _has_literal_bypass: literal bypass match
  - _has_imperative: imperative directive + alignment
  - detect_user_driven_mode: top-level orchestration + tier priority
  - is_user_driven: boolean wrapper
  - Error/edge cases: missing transcript, malformed JSON, empty messages
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

# Make the helper importable
LIB_DIR = Path(os.path.expanduser("~/.claude/scripts/_lib"))
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

import intent_detection as id_mod  # type: ignore  # noqa: E402  (added to sys.path at runtime)


# ---------------------------------------------------------------------------
# Helpers for building synthetic transcripts
# ---------------------------------------------------------------------------

def _user_msg(text: str) -> str:
    """Build a transcript line for a real user message."""
    return json.dumps({
        "type": "user",
        "message": {"content": text},
    }) + "\n"


def _user_msg_list(text: str) -> str:
    """Build a transcript line where content is a list with text part."""
    return json.dumps({
        "type": "user",
        "message": {"content": [{"type": "text", "text": text}]},
    }) + "\n"


def _tool_result_msg(tool_use_id: str = "x", out: str = "ok") -> str:
    """Build a transcript line that's a tool-result echo (type=user but
    content is purely tool_result -- should be filtered)."""
    return json.dumps({
        "type": "user",
        "message": {"content": [{
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": out,
        }]},
    }) + "\n"


def _assistant_msg(text: str) -> str:
    return json.dumps({
        "type": "assistant",
        "message": {"content": text},
    }) + "\n"


def _write_transcript(*lines) -> str:
    """Write a transcript to a temp file and return path."""
    fh = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8")
    fh.writelines(lines)
    fh.close()
    return fh.name


# ---------------------------------------------------------------------------
# read_recent_user_messages
# ---------------------------------------------------------------------------

def test_read_recent_user_messages_returns_most_recent_first():
    path = _write_transcript(
        _user_msg("first message"),
        _user_msg("second message"),
        _user_msg("third message"),
    )
    msgs = id_mod.read_recent_user_messages(path, lookback=3)
    assert msgs[0] == "third message"
    assert msgs[1] == "second message"
    assert msgs[2] == "first message"
    os.unlink(path)


def test_read_recent_user_messages_respects_lookback():
    path = _write_transcript(
        *[_user_msg(f"msg {i}") for i in range(20)],
    )
    msgs = id_mod.read_recent_user_messages(path, lookback=5)
    assert len(msgs) == 5
    os.unlink(path)


def test_read_recent_user_messages_filters_tool_results():
    path = _write_transcript(
        _user_msg("real message 1"),
        _tool_result_msg(),
        _tool_result_msg(),
        _tool_result_msg(),
        _user_msg("real message 2"),
    )
    msgs = id_mod.read_recent_user_messages(path, lookback=10)
    # Only 2 real user messages should appear
    assert len(msgs) == 2
    assert msgs[0] == "real message 2"
    assert msgs[1] == "real message 1"
    os.unlink(path)


def test_read_recent_user_messages_handles_list_content():
    path = _write_transcript(
        _user_msg_list("text in list form"),
    )
    msgs = id_mod.read_recent_user_messages(path)
    assert msgs == ["text in list form"]
    os.unlink(path)


def test_read_recent_user_messages_skips_assistant():
    path = _write_transcript(
        _user_msg("user one"),
        _assistant_msg("assistant reply"),
        _user_msg("user two"),
    )
    msgs = id_mod.read_recent_user_messages(path)
    assert msgs == ["user two", "user one"]
    os.unlink(path)


def test_read_recent_user_messages_handles_malformed_json():
    """Malformed lines should be skipped silently, not abort."""
    fh = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8")
    fh.write(_user_msg("good message"))
    fh.write("THIS IS NOT JSON\n")
    fh.write(_user_msg("another good message"))
    fh.close()
    msgs = id_mod.read_recent_user_messages(fh.name)
    assert "good message" in msgs
    assert "another good message" in msgs
    os.unlink(fh.name)


def test_read_recent_user_messages_missing_path_returns_empty():
    assert id_mod.read_recent_user_messages(None) == []
    assert id_mod.read_recent_user_messages("") == []
    assert id_mod.read_recent_user_messages("/nonexistent/path/transcript.jsonl") == []


def test_read_recent_user_messages_filters_empty_strings():
    path = _write_transcript(
        _user_msg(""),
        _user_msg("real"),
        _user_msg("   "),
    )
    msgs = id_mod.read_recent_user_messages(path)
    assert msgs == ["real"]
    os.unlink(path)


def test_read_recent_user_messages_lowercases():
    path = _write_transcript(_user_msg("UPPERCASE MESSAGE"))
    msgs = id_mod.read_recent_user_messages(path)
    assert msgs == ["uppercase message"]
    os.unlink(path)


# ---------------------------------------------------------------------------
# _is_tool_result_message
# ---------------------------------------------------------------------------

def test_is_tool_result_message_pure_tool_result():
    assert id_mod._is_tool_result_message([
        {"type": "tool_result", "tool_use_id": "x", "content": "ok"}
    ]) is True


def test_is_tool_result_message_mixed_with_text_is_real():
    """If a record has both tool_result AND user text, treat as real user msg."""
    assert id_mod._is_tool_result_message([
        {"type": "tool_result", "tool_use_id": "x", "content": "ok"},
        {"type": "text", "text": "user wrote this too"},
    ]) is False


def test_is_tool_result_message_text_only():
    assert id_mod._is_tool_result_message([
        {"type": "text", "text": "just user prose"},
    ]) is False


def test_is_tool_result_message_string_content():
    """String content (not a list) is real user prose."""
    assert id_mod._is_tool_result_message("plain text") is False


def test_is_tool_result_message_empty_list():
    assert id_mod._is_tool_result_message([]) is False


# ---------------------------------------------------------------------------
# _file_aliases
# ---------------------------------------------------------------------------

def test_file_aliases_basic():
    aliases = id_mod._file_aliases("C:/path/to/icp.md")
    assert "icp.md" in aliases
    assert "icp" in aliases


def test_file_aliases_with_lang_suffix():
    """A file like icp-es.md should also alias to 'icp' so a user mentioning
    'broaden the icp' triggers alignment."""
    aliases = id_mod._file_aliases("knowledge-base/clients/dangeles/icp-es.md")
    assert "icp-es.md" in aliases
    assert "icp-es" in aliases
    assert "icp" in aliases  # head of hyphenated stem


def test_file_aliases_none_returns_empty():
    assert id_mod._file_aliases(None) == []
    assert id_mod._file_aliases("") == []


def test_file_aliases_lowercases():
    aliases = id_mod._file_aliases("/path/ICP.MD")
    assert "icp.md" in aliases
    assert "icp" in aliases


# ---------------------------------------------------------------------------
# _has_session_intent
# ---------------------------------------------------------------------------

def test_session_intent_im_driving_this():
    msgs = ["i'm driving this session, just go"]
    hit = id_mod._has_session_intent(msgs)
    assert hit is not None
    assert hit[1] == 0


def test_session_intent_i_am_driving():
    msgs = ["other text", "i am driving the session for the next hour"]
    hit = id_mod._has_session_intent(msgs)
    assert hit is not None
    assert hit[1] == 1


def test_session_intent_let_me_drive():
    msgs = ["let me drive this one"]
    hit = id_mod._has_session_intent(msgs)
    assert hit is not None


def test_session_intent_user_driven_session():
    msgs = ["this is a user-driven session"]
    hit = id_mod._has_session_intent(msgs)
    assert hit is not None


def test_session_intent_no_match():
    msgs = ["what time is it", "build the thing"]
    assert id_mod._has_session_intent(msgs) is None


# ---------------------------------------------------------------------------
# _has_literal_bypass
# ---------------------------------------------------------------------------

def test_literal_bypass_substring_match():
    msgs = ["please skip pmm and continue"]
    hit = id_mod._has_literal_bypass(msgs, ("skip pmm", "skip sow-stack"))
    assert hit is not None
    assert hit[0] == "skip pmm"


def test_literal_bypass_no_phrases_returns_none():
    msgs = ["any message"]
    assert id_mod._has_literal_bypass(msgs, ()) is None


def test_literal_bypass_no_match():
    msgs = ["totally unrelated text"]
    hit = id_mod._has_literal_bypass(msgs, ("skip pmm",))
    assert hit is None


def test_literal_bypass_case_insensitive():
    """Caller's bypass phrases are matched case-insensitively against
    already-lowercased messages."""
    msgs = ["please skip pmm and continue"]
    # Phrase passed in already lowercase; messages already lowercased by reader
    hit = id_mod._has_literal_bypass(msgs, ("SKIP PMM",))
    assert hit is not None


# ---------------------------------------------------------------------------
# _has_imperative
# ---------------------------------------------------------------------------

def test_imperative_at_start_of_message():
    msgs = ["update the icp file"]
    hit = id_mod._has_imperative(msgs, [])
    assert hit is not None
    assert hit[0] == "imperative_general"


def test_imperative_aligned_with_file():
    msgs = ["update icp.md please"]
    hit = id_mod._has_imperative(msgs, ["icp.md", "icp"])
    assert hit is not None
    assert hit[0] == "imperative_aligned"


def test_imperative_lets_construction():
    msgs = ["let's update the docs"]
    hit = id_mod._has_imperative(msgs, [])
    assert hit is not None


def test_imperative_go_ahead_and():
    msgs = ["go ahead and broaden the description"]
    hit = id_mod._has_imperative(msgs, [])
    assert hit is not None


def test_imperative_can_you():
    msgs = ["can you update the file"]
    hit = id_mod._has_imperative(msgs, [])
    assert hit is not None


def test_imperative_do_it():
    msgs = ["do it"]
    hit = id_mod._has_imperative(msgs, [])
    assert hit is not None


def test_imperative_knock_out():
    msgs = ["lets continue to knock out what is holding up"]
    hit = id_mod._has_imperative(msgs, [])
    assert hit is not None


def test_imperative_no_directive():
    msgs = ["just a question, what do you think"]
    assert id_mod._has_imperative(msgs, []) is None


def test_imperative_avoids_substring_false_positive():
    """Verb 'update' should not match inside 'duplicated' (word boundary)."""
    msgs = ["this is duplicated content"]
    assert id_mod._has_imperative(msgs, []) is None


# ---------------------------------------------------------------------------
# detect_user_driven_mode -- tier priority
# ---------------------------------------------------------------------------

def test_detect_returns_safe_default_when_no_transcript():
    result = id_mod.detect_user_driven_mode(None)
    assert result["is_user_driven"] is False
    assert result["match_type"] is None


def test_detect_literal_bypass_wins_over_imperative():
    """Tier 1 (literal bypass) outranks Tier 3 (imperative)."""
    path = _write_transcript(
        _user_msg("update the icp file -- skip pmm"),
    )
    result = id_mod.detect_user_driven_mode(path, bypass_phrases=("skip pmm",))
    assert result["is_user_driven"] is True
    assert result["match_type"] == "literal_bypass"
    os.unlink(path)


def test_detect_session_intent_wins_over_imperative():
    """Tier 2 (session intent) outranks Tier 3 (imperative) when both present."""
    path = _write_transcript(
        _user_msg("i'm driving this session, update everything"),
    )
    result = id_mod.detect_user_driven_mode(path)
    assert result["is_user_driven"] is True
    # Literal bypass not configured, session intent fires
    assert result["match_type"] == "session_intent"
    os.unlink(path)


def test_detect_imperative_aligned_with_file():
    path = _write_transcript(
        _user_msg("update icp.md broaden the section on pricing"),
    )
    result = id_mod.detect_user_driven_mode(
        path,
        file_path="C:/work/icp.md",
    )
    assert result["is_user_driven"] is True
    assert result["match_type"] == "imperative_aligned"
    os.unlink(path)


def test_detect_imperative_general_no_alignment():
    path = _write_transcript(
        _user_msg("update the system"),
    )
    result = id_mod.detect_user_driven_mode(
        path,
        file_path="C:/work/unrelated.md",
    )
    assert result["is_user_driven"] is True
    assert result["match_type"] == "imperative_general"
    os.unlink(path)


def test_detect_default_when_only_questions():
    path = _write_transcript(
        _user_msg("what do you think about this"),
        _user_msg("how does that work"),
    )
    result = id_mod.detect_user_driven_mode(path)
    assert result["is_user_driven"] is False
    os.unlink(path)


def test_detect_handles_tool_result_decay_correctly():
    """REGRESSION: wr-hq-2026-04-27-001 lookback bug. After issuing imperative
    and several tool calls produce tool-result echoes, imperative should still
    be visible in the lookback window."""
    path = _write_transcript(
        _user_msg("update the file please"),       # real imperative
        _tool_result_msg(),                         # tool ran
        _tool_result_msg(),                         # tool ran
        _tool_result_msg(),                         # tool ran
        _tool_result_msg(),                         # tool ran
    )
    result = id_mod.detect_user_driven_mode(path, lookback=15)
    # Old buggy behavior: lookback=3 + tool_results counted = imperative
    # falls outside window. New behavior: tool-results filtered, imperative
    # found.
    assert result["is_user_driven"] is True
    assert result["match_type"] in ("imperative_general", "imperative_aligned")
    os.unlink(path)


def test_detect_evidence_field_populated():
    path = _write_transcript(_user_msg("update everything"))
    result = id_mod.detect_user_driven_mode(path)
    assert isinstance(result["evidence"], str)
    assert result["evidence"]
    os.unlink(path)


# ---------------------------------------------------------------------------
# is_user_driven (boolean wrapper)
# ---------------------------------------------------------------------------

def test_is_user_driven_true():
    path = _write_transcript(_user_msg("update everything"))
    assert id_mod.is_user_driven(path) is True
    os.unlink(path)


def test_is_user_driven_false():
    path = _write_transcript(_user_msg("just a question"))
    assert id_mod.is_user_driven(path) is False
    os.unlink(path)


def test_is_user_driven_no_transcript():
    assert id_mod.is_user_driven(None) is False


# ---------------------------------------------------------------------------
# Error resilience
# ---------------------------------------------------------------------------

def test_detect_returns_safe_default_on_unreadable_path():
    """Pointing at a directory or unreadable path must not crash."""
    result = id_mod.detect_user_driven_mode("/this/does/not/exist.jsonl")
    assert result["is_user_driven"] is False


def test_detect_handles_completely_empty_transcript():
    path = _write_transcript()
    result = id_mod.detect_user_driven_mode(path)
    assert result["is_user_driven"] is False
    os.unlink(path)
