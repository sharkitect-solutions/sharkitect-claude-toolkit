"""Tests for end-session-enforcer.py hook.

Goals (S50 fix, 2026-05-13):
1. Descriptive-context false-positives DO NOT trigger (simile, past ref, discussion,
   examples, quoted/named references).
2. Imperative/standalone end-session signals STILL trigger (slash command,
   "let's end the session", "wrap up now", bare "end session").
3. Silencer mechanism: user saying "still working" / "not ending" AFTER an
   end-session phrase suppresses the gate. Fresh end-session signal AFTER
   silencer re-arms the gate.
4. No new false negatives: existing detection cases still pass.

Source incident: 2026-05-13 S50 — user's architectural-discussion message
"sort of like we did with the session checkpoint and end session may risk
breaking something" triggered the gate on every subsequent Bash/Write,
forcing repeated "skip end-session" bypass keywords in AI output that the
user found noisy. Detection was pure substring; no imperative-form check,
no negative-context gates, no silencer.

# skip end-session — test file structurally referencing the gate vocabulary
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


HOOK_PATH = Path.home() / ".claude" / "hooks" / "end-session-enforcer.py"


def _load():
    spec = importlib.util.spec_from_file_location("end_session_enforcer", HOOK_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_transcript(tmp_path, messages):
    """Build a JSONL transcript file. `messages` is a list of dicts:
       {"type": "user"|"assistant", "timestamp": iso, "text": str}.
    Returns the transcript path as a string.
    """
    transcript = tmp_path / "transcript.jsonl"
    lines = []
    for m in messages:
        rec = {
            "type": m["type"],
            "timestamp": m["timestamp"],
            "message": {"content": m["text"]},
        }
        lines.append(json.dumps(rec))
    transcript.write_text("\n".join(lines), encoding="utf-8")
    return str(transcript)


# ---------------------------------------------------------------------------
# Descriptive-context false-positive tests (the S50 bug class)
# ---------------------------------------------------------------------------


def test_descriptive_simile_does_not_trigger(tmp_path):
    """User's S50 message: 'sort of like we did with end session...' — descriptive simile."""
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "sort of like we did with the session checkpoint and end session we may risk breaking something",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert not found, "descriptive simile 'sort of like we did with end session' must NOT trigger"


def test_past_reference_does_not_trigger(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "remember when we did the end session sweep yesterday — that broke things",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert not found, "'remember when we did end session' is a past reference, not a request"


def test_discussion_meta_reference_does_not_trigger(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "we're talking about end session protocols and how they should work",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert not found, "'talking about end session' is a meta-discussion, not a request"


def test_example_context_does_not_trigger(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "for example end session triggers cause problems",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert not found, "'for example end session' is an example reference, not a request"


def test_term_definition_reference_does_not_trigger(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "what does the term end session actually mean here",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert not found, "'the term end session' is a definition reference, not a request"


def test_wrap_up_as_past_event_does_not_trigger(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "earlier we did the wrap up sweep and it broke",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert not found, "'earlier we did the wrap up' is a past reference"


# ---------------------------------------------------------------------------
# True-positive tests (must keep firing)
# ---------------------------------------------------------------------------


def test_slash_command_end_session_triggers(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "/end-session",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert found, "/end-session slash command must always trigger"


def test_lets_end_the_session_triggers(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "let's end the session for today",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert found, "imperative 'let's end the session' must trigger"


def test_wrap_up_now_triggers(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "wrap up now please, I have to go",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert found, "'wrap up now' must trigger"


def test_standalone_end_session_triggers(tmp_path):
    """Bare standalone 'end session' message — no surrounding context — should trigger."""
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "end session",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert found, "standalone 'end session' message must trigger"


def test_ready_to_end_session_triggers(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "I'm ready to end the session for today",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert found, "'ready to end the session' must trigger"


def test_done_for_today_triggers(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "I'm done for today, stop here",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert found, "'done for today' must trigger"


def test_thats_it_for_today_triggers(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "that's it for today, save and close",
    }])
    _, found = module.find_most_recent_end_session(transcript)
    assert found, "'that's it for today' must trigger"


# ---------------------------------------------------------------------------
# Silencer mechanism tests (new in S50 fix)
# ---------------------------------------------------------------------------


def test_silencer_after_signal_cross_turn_auto_silences(tmp_path):
    """User says 'end session' at 12:00, then 'still working' at 12:30.

    With lookback=1, find_most_recent_end_session only scans the most-recent
    user text message ('still working') and sees no signal -- the older
    signal is naturally stale. Silencer is still independently detected
    (wider scan window) for downstream comparison, but the immediate
    semantics are: cross-turn silencer works for free via lookback=1.
    """
    module = _load()
    transcript = _write_transcript(tmp_path, [
        {"type": "user", "timestamp": "2026-05-13T12:00:00Z", "text": "end session"},
        {"type": "user", "timestamp": "2026-05-13T12:30:00Z", "text": "actually still working on the project"},
    ])
    silencer_ts, silencer_found = module.find_most_recent_silencer(transcript)
    _, signal_found = module.find_most_recent_end_session(transcript)
    assert silencer_found, "'still working' must be detected by silencer scan"
    assert silencer_ts is not None
    assert not signal_found, (
        "lookback=1: older signal isn't scanned when a newer user text "
        "message replaces it; gate auto-silences cross-turn"
    )


def test_silencer_in_same_message_overrides_signal(tmp_path):
    """User says BOTH 'end session' AND 'still working' in the same message.
    Both are detected with equal timestamps; silencer wins by >= comparison
    in main(). This is the only case where the silencer mechanism (vs the
    cross-turn auto-silence from lookback=1) actually matters.
    """
    module = _load()
    transcript = _write_transcript(tmp_path, [{
        "type": "user",
        "timestamp": "2026-05-13T12:00:00Z",
        "text": "we were going to end session but still working actually",
    }])
    signal_ts, signal_found = module.find_most_recent_end_session(transcript)
    silencer_ts, silencer_found = module.find_most_recent_silencer(transcript)
    assert signal_found, "imperative signal is detected"
    assert silencer_found, "silencer phrase in same message is detected"
    assert signal_ts is not None and silencer_ts is not None
    assert silencer_ts >= signal_ts, (
        "same-message: silencer_ts == signal_ts; main() uses >= so silencer wins"
    )


def test_signal_after_silencer_rearms(tmp_path):
    """User says 'still working' at 12:00, then 'end session now' at 12:30 — fresh signal wins."""
    module = _load()
    transcript = _write_transcript(tmp_path, [
        {"type": "user", "timestamp": "2026-05-13T12:00:00Z", "text": "still working on this"},
        {"type": "user", "timestamp": "2026-05-13T12:30:00Z", "text": "end session now please"},
    ])
    silencer_ts, _ = module.find_most_recent_silencer(transcript)
    signal_ts, signal_found = module.find_most_recent_end_session(transcript)
    assert signal_found
    assert silencer_ts is not None and signal_ts is not None
    assert signal_ts > silencer_ts, "fresh signal AFTER silencer must re-arm the gate"


def test_silencer_phrase_not_ending(tmp_path):
    """'not ending' is a valid silencer phrase."""
    module = _load()
    transcript = _write_transcript(tmp_path, [
        {"type": "user", "timestamp": "2026-05-13T12:00:00Z", "text": "wrap up"},
        {"type": "user", "timestamp": "2026-05-13T12:30:00Z", "text": "no, not ending yet"},
    ])
    _, found = module.find_most_recent_silencer(transcript)
    assert found, "'not ending' must be detected as silencer"


def test_silencer_phrase_still_going(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [
        {"type": "user", "timestamp": "2026-05-13T12:00:00Z", "text": "end session"},
        {"type": "user", "timestamp": "2026-05-13T12:30:00Z", "text": "still going, keep working"},
    ])
    _, found = module.find_most_recent_silencer(transcript)
    assert found


def test_no_silencer_when_absent(tmp_path):
    module = _load()
    transcript = _write_transcript(tmp_path, [
        {"type": "user", "timestamp": "2026-05-13T12:00:00Z", "text": "let's work on something"},
    ])
    _, found = module.find_most_recent_silencer(transcript)
    assert not found


# ---------------------------------------------------------------------------
# Direct unit tests of helper functions
# ---------------------------------------------------------------------------


def test_is_descriptive_reference_detects_simile():
    module = _load()
    text = "sort of like we did with end session things broke"
    # Find the position of "end session" in the text
    pos = text.find("end session")
    assert pos > 0
    assert module._is_descriptive_reference(text, pos), \
        "preceded by 'sort of like we did' should be classified as descriptive"


def test_is_descriptive_reference_imperative_is_not_descriptive():
    module = _load()
    text = "end session now please"
    # Match position is at 0
    assert not module._is_descriptive_reference(text, 0), \
        "imperative at start of message is not descriptive"


def test_is_descriptive_reference_short_text_handled():
    module = _load()
    assert not module._is_descriptive_reference("", 0)
    assert not module._is_descriptive_reference("end session", 0)


def test_contains_end_session_signal_skips_descriptive(tmp_path):
    """contains_end_session_signal returns False when only descriptive matches present."""
    module = _load()
    text = "remember when we did the end session sweep"
    assert not module.contains_end_session_signal(text)


def test_contains_end_session_signal_finds_imperative_after_descriptive():
    """If text has both a descriptive AND an imperative match, imperative wins."""
    module = _load()
    text = "we discussed end session protocols. now let's end the session"
    assert module.contains_end_session_signal(text), \
        "second clause is imperative and should trigger"


# ---------------------------------------------------------------------------
# AI-side silencer-in-tool-content tests (S51 fix — user direction:
# "did you also include a silencer phrase for the AI?")
# ---------------------------------------------------------------------------


def test_ai_silencer_still_working_in_tool_content_bypasses():
    """When AI includes 'still working' in tool_input content, has_bypass_in_content
    accepts it -- natural-language alternative to the awkward 'skip end-session'."""
    module = _load()
    assert module.has_bypass_in_content("doing the next step. still working on this.")


def test_ai_silencer_still_going_in_tool_content_bypasses():
    module = _load()
    assert module.has_bypass_in_content("still going with phase 2 cleanup")


def test_ai_silencer_not_ending_in_tool_content_bypasses():
    module = _load()
    assert module.has_bypass_in_content("not ending yet, more cleanup to do")


def test_neutral_tool_content_does_not_bypass():
    """Tool content without any bypass/silencer phrase does NOT bypass."""
    module = _load()
    assert not module.has_bypass_in_content("regular tool content without any keywords")
    assert not module.has_bypass_in_content("git status; ls; echo hello")


def test_legacy_bypass_phrases_still_work_in_tool_content():
    """The existing 'skip end-session' family must still work for back-compat."""
    module = _load()
    assert module.has_bypass_in_content("skip end-session — fixing the hook itself")
    assert module.has_bypass_in_content("save progress quickly")


# ---------------------------------------------------------------------------
# Lookback tightening tests (S50 fix — user direction "look at the previous
# message not ALL RECENT MESSAGES")
# ---------------------------------------------------------------------------


def test_old_signal_does_not_trigger_after_newer_replacing_message(tmp_path):
    """User said 'end session' message 1 ago, then 'continue working' message 0 ago.
    With lookback=1 (most-recent user text message only), only newer message is
    scanned. Newer has no signal -> no trigger. Older signal is stale."""
    module = _load()
    transcript = _write_transcript(tmp_path, [
        {"type": "user", "timestamp": "2026-05-13T11:00:00Z", "text": "end session"},
        {"type": "user", "timestamp": "2026-05-13T12:00:00Z", "text": "actually let's keep working on this"},
    ])
    _, found = module.find_most_recent_end_session(transcript)
    assert not found, "older end-session signal must NOT trigger when a newer user message replaces it"


def test_old_signal_does_not_trigger_2_messages_back(tmp_path):
    """Three user messages: signal 2 ago, neutral 1 ago, neutral 0 ago.
    Lookback=1 means only the most recent counts. No trigger."""
    module = _load()
    transcript = _write_transcript(tmp_path, [
        {"type": "user", "timestamp": "2026-05-13T11:00:00Z", "text": "end session"},
        {"type": "user", "timestamp": "2026-05-13T11:30:00Z", "text": "wait actually one more thing"},
        {"type": "user", "timestamp": "2026-05-13T12:00:00Z", "text": "let's continue with phase 2"},
    ])
    _, found = module.find_most_recent_end_session(transcript)
    assert not found, "signal from 2+ messages ago must NOT trigger"


def test_tool_result_records_do_not_count_against_lookback(tmp_path):
    """Tool-result records (type=user, content=tool_result) between user texts
    shouldn't deplete the lookback budget. Lookback counts user TEXT messages."""
    module = _load()
    transcript = tmp_path / "transcript.jsonl"
    lines = [
        json.dumps({
            "type": "user", "timestamp": "2026-05-13T11:00:00Z",
            "message": {"content": "end session please"},
        }),
        # 3 tool_result-only records, should be skipped without counting:
        json.dumps({
            "type": "user", "timestamp": "2026-05-13T11:00:05Z",
            "message": {"content": [{"type": "tool_result", "content": "result1"}]},
        }),
        json.dumps({
            "type": "user", "timestamp": "2026-05-13T11:00:10Z",
            "message": {"content": [{"type": "tool_result", "content": "result2"}]},
        }),
        json.dumps({
            "type": "user", "timestamp": "2026-05-13T11:00:15Z",
            "message": {"content": [{"type": "tool_result", "content": "result3"}]},
        }),
    ]
    transcript.write_text("\n".join(lines), encoding="utf-8")
    _, found = module.find_most_recent_end_session(str(transcript))
    assert found, "tool_result records should be skipped; the user text 'end session please' must still be found"


def test_signal_in_most_recent_text_message_triggers_even_after_tool_results(tmp_path):
    """User text with signal is the most recent NON-tool-result user record.
    Tool result records after it shouldn't displace it."""
    module = _load()
    transcript = tmp_path / "transcript.jsonl"
    lines = [
        # Earlier neutral message:
        json.dumps({
            "type": "user", "timestamp": "2026-05-13T11:00:00Z",
            "message": {"content": "build the thing"},
        }),
        # Newer end-session text:
        json.dumps({
            "type": "user", "timestamp": "2026-05-13T11:30:00Z",
            "message": {"content": "end session"},
        }),
        # Tool results AFTER the signal (would happen if AI invokes tools post-signal):
        json.dumps({
            "type": "user", "timestamp": "2026-05-13T11:30:05Z",
            "message": {"content": [{"type": "tool_result", "content": "intermediate"}]},
        }),
    ]
    transcript.write_text("\n".join(lines), encoding="utf-8")
    _, found = module.find_most_recent_end_session(str(transcript))
    assert found, "most-recent text user message has signal; tool_results don't displace it"
