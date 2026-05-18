"""Tests for _dispatchers/methodology/end_session.py (Phase 2 Build #2B).

Strict 1:1 behavior preservation of end-session-enforcer.py wrapped in
evaluate(payload). Returns:

  None                                  -> sub-rule did not trigger / pass-through
  {"decision": "deny", "reason": "..."} -> HARD GATE

Source preserves:
  - End-session signal patterns (end session, wrap up, /end-session, etc.)
  - Descriptive marker exemption (simile / past reference / discussion)
  - Silencer phrases (still working, not ending, etc.)
  - Skill log timestamp comparison (invocation AFTER signal bypasses)
  - Bypass phrases in transcript and tool content
  - Meta-path exemptions (.work-requests/, .lifecycle-reviews/, .routed-tasks/,
    /memory/feedback_, /.claude/projects/)
  - BLOCKED_TOOLS filter (only Bash, Write, Edit, TodoWrite)

Spec: docs/superpowers/specs/2026-05-15-phase-2-architecture-spec.md (Part A)
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone, timedelta

import pytest

HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


def _payload(tool_name, tool_input, transcript_path=""):
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "transcript_path": transcript_path,
    }


def _write_jsonl_transcript(tmp_path, messages):
    """Write JSONL transcript. messages is a list of (role, content, ts) tuples.
    role: "user" | "assistant"
    content: str (text) or list[dict] (content blocks)
    ts: iso timestamp string, or None
    """
    path = tmp_path / "transcript.jsonl"
    lines = []
    for role, content, ts in messages:
        rec = {
            "type": role,
            "message": {"content": content},
        }
        if ts:
            rec["timestamp"] = ts
        lines.append(json.dumps(rec))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def _write_skill_log(tmp_path, *entries):
    """Write today's skill-invocation log.
    entries: list of (skill_name, timestamp_iso_or_None) tuples.
    """
    log_dir = tmp_path / ".tmp"
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log = log_dir / f"skill-invocations-{today}.json"
    invs = []
    for skill, ts in entries:
        rec = {"skill": skill}
        if ts:
            rec["timestamp"] = ts
        invs.append(rec)
    log.write_text(json.dumps({"invocations": invs}), encoding="utf-8")
    return log_dir


# ---------------------------------------------------------------------------
# Signal detection: imperative end-session patterns -> deny (no bypass)
# ---------------------------------------------------------------------------

class TestEndSessionSignalDetection:
    def test_signal_end_session_denies(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "let's end the session please", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "git status"}, transcript_path=transcript,
        ))
        assert result is not None
        assert result.get("decision") == "deny"
        assert "end-session" in result.get("reason", "").lower()

    def test_signal_wrap_up_denies(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "wrap up please", ts)])
        result = end_session.evaluate(_payload(
            "Write", {"file_path": "/x.md", "content": "y"}, transcript_path=transcript,
        ))
        assert result is not None
        assert result.get("decision") == "deny"

    def test_signal_slash_end_session_denies(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "/end-session", ts)])
        result = end_session.evaluate(_payload(
            "TodoWrite", {"todos": []}, transcript_path=transcript,
        ))
        assert result is not None
        assert result.get("decision") == "deny"

    def test_signal_stop_for_day_denies(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "let's stop for the day", ts)])
        result = end_session.evaluate(_payload(
            "Bash", {"command": "git push"}, transcript_path=transcript,
        ))
        assert result is not None
        assert result.get("decision") == "deny"

    def test_no_signal_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "please fix the bug", ts)])
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        assert result is None


# ---------------------------------------------------------------------------
# Descriptive marker exemption: similes/past-ref/discussion should not trigger
# ---------------------------------------------------------------------------

class TestEndSessionDescriptiveExemption:
    def test_simile_exempt(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "sort of like we did with end session protocols last week", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        assert result is None

    def test_meta_discussion_exempt(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "we discussed end session behavior earlier", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        assert result is None

    def test_imperative_after_descriptive_in_diff_sentence_denies(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "we discussed end session protocols. Now end the session.", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        assert result is not None
        assert result.get("decision") == "deny"


# ---------------------------------------------------------------------------
# Silencer phrases: silence the gate when said after signal
# ---------------------------------------------------------------------------

class TestEndSessionSilencer:
    def test_silencer_after_signal_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts_signal = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        ts_silencer = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [
                ("user", "wrap up please", ts_signal),
                ("user", "actually still working on this", ts_silencer),
            ],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        # Silencer is in the most-recent message; signal is older -> gate stands down
        # BUT signal detection uses TRANSCRIPT_USER_LOOKBACK=1 so only latest matters
        # Latest message has no signal -> pass anyway
        assert result is None

    def test_silencer_same_message_as_signal_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "wrap up but still working actually", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        # Both signal + silencer in same message; silencer wins on >= comparison
        assert result is None


# ---------------------------------------------------------------------------
# Bypass: skill log invocation AFTER signal
# ---------------------------------------------------------------------------

class TestEndSessionSkillLogBypass:
    def test_invocation_after_signal_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        signal_ts = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        # Skill invoked LATER -- naive local-time string (matches tracker format)
        inv_ts = datetime.now().isoformat()
        _write_skill_log(tmp_path, ("end-session", inv_ts))
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "end the session", signal_ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        assert result is None

    def test_namespaced_invocation_recognized(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        signal_ts = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        inv_ts = datetime.now().isoformat()
        _write_skill_log(tmp_path, ("plugin:end-session", inv_ts))
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "end the session", signal_ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        assert result is None

    def test_unparseable_signal_ts_falls_back_to_any_invocation(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        # No timestamp on the signal message
        _write_skill_log(tmp_path, ("end-session", datetime.now().isoformat()))
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "wrap up", None)],  # no timestamp
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        # Fallback: any end-session invocation today -> pass
        assert result is None

    def test_no_invocation_no_bypass_denies(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        signal_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        # Skill log exists with some OTHER skill -- not end-session
        _write_skill_log(tmp_path, ("brainstorming", datetime.now().isoformat()))
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "end the session", signal_ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        assert result is not None
        assert result.get("decision") == "deny"


# ---------------------------------------------------------------------------
# Bypass: phrase in transcript and content
# ---------------------------------------------------------------------------

class TestEndSessionBypassPhrases:
    def test_bypass_phrase_in_transcript_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "end the session but skip end-session", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "git commit"}, transcript_path=transcript,
        ))
        assert result is None

    def test_save_progress_quickly_in_transcript_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "wrap up -- save progress quickly", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "git push"}, transcript_path=transcript,
        ))
        assert result is None

    def test_bypass_in_write_content_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "end the session", ts)])
        result = end_session.evaluate(_payload(
            "Write",
            {"file_path": "/x.md", "content": "# skip end-session\nfoo"},
            transcript_path=transcript,
        ))
        assert result is None

    def test_bypass_in_edit_new_string_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "wrap up", ts)])
        result = end_session.evaluate(_payload(
            "Edit",
            {"file_path": "/x.md", "old_string": "a", "new_string": "skip end-session b"},
            transcript_path=transcript,
        ))
        assert result is None

    def test_bypass_in_todowrite_content_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "end the session", ts)])
        result = end_session.evaluate(_payload(
            "TodoWrite",
            {"todos": [{"content": "skip end-session task", "activeForm": "x", "status": "pending"}]},
            transcript_path=transcript,
        ))
        assert result is None

    def test_silencer_phrase_in_content_passes(self, tmp_path, monkeypatch):
        """S51: silencer phrases also act as in-content bypasses."""
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "end the session", ts)])
        result = end_session.evaluate(_payload(
            "Bash",
            {"command": "echo 'still working'", "description": "x"},
            transcript_path=transcript,
        ))
        assert result is None


# ---------------------------------------------------------------------------
# Meta-path exemptions
# ---------------------------------------------------------------------------

class TestEndSessionMetaPath:
    def test_work_requests_path_exempt(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "end the session", ts)])
        result = end_session.evaluate(_payload(
            "Write",
            {"file_path": "/workspace/.work-requests/inbox/wr-x.json", "content": "{}"},
            transcript_path=transcript,
        ))
        assert result is None

    def test_lifecycle_reviews_path_exempt(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "wrap up", ts)])
        result = end_session.evaluate(_payload(
            "Edit",
            {"file_path": "/workspace/.lifecycle-reviews/inbox/lr-x.json",
             "old_string": "a", "new_string": "b"},
            transcript_path=transcript,
        ))
        assert result is None

    def test_routed_tasks_path_exempt(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "end the session", ts)])
        result = end_session.evaluate(_payload(
            "Write",
            {"file_path": "/workspace/.routed-tasks/inbox/rt-x.json", "content": "{}"},
            transcript_path=transcript,
        ))
        assert result is None

    def test_memory_path_exempt(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "wrap up", ts)])
        result = end_session.evaluate(_payload(
            "Write",
            {"file_path": "/anywhere/memory/feedback_x.md", "content": "x"},
            transcript_path=transcript,
        ))
        assert result is None

    def test_bash_not_meta_path_exempt(self, tmp_path, monkeypatch):
        """Meta-path exemption only applies to Write/Edit, not Bash."""
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "end the session", ts)])
        result = end_session.evaluate(_payload(
            "Bash",
            {"command": "ls /workspace/.work-requests/"},
            transcript_path=transcript,
        ))
        # Bash with .work-requests/ in command does NOT get meta-path exempt
        # -> should deny
        assert result is not None
        assert result.get("decision") == "deny"


# ---------------------------------------------------------------------------
# Tool filter: only Bash/Write/Edit/TodoWrite trigger
# ---------------------------------------------------------------------------

class TestEndSessionToolFilter:
    def test_read_tool_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "end the session", ts)])
        result = end_session.evaluate(_payload(
            "Read", {"file_path": "/x.md"}, transcript_path=transcript,
        ))
        assert result is None

    def test_grep_tool_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "wrap up", ts)])
        result = end_session.evaluate(_payload(
            "Grep", {"pattern": "foo"}, transcript_path=transcript,
        ))
        assert result is None

    def test_glob_tool_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "end the session", ts)])
        result = end_session.evaluate(_payload(
            "Glob", {"pattern": "**/*.py"}, transcript_path=transcript,
        ))
        assert result is None

    def test_mcp_tool_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(tmp_path, [("user", "wrap up", ts)])
        result = end_session.evaluate(_payload(
            "mcp__supabase__execute_sql", {"query": "SELECT 1"}, transcript_path=transcript,
        ))
        assert result is None


# ---------------------------------------------------------------------------
# Pass-through: no transcript, malformed transcript, empty payload
# ---------------------------------------------------------------------------

class TestEndSessionPassThrough:
    def test_no_transcript_path_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path="",
        ))
        assert result is None

    def test_missing_transcript_file_passes(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=str(tmp_path / "missing.jsonl"),
        ))
        assert result is None

    def test_empty_payload_passes(self):
        from _dispatchers.methodology import end_session
        result = end_session.evaluate({})
        assert result is None

    def test_assistant_message_with_signal_does_not_trigger(self, tmp_path, monkeypatch):
        """Only USER messages count as signal sources."""
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("assistant", "I will end the session now", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        assert result is None

    def test_system_block_stripped_before_signal_match(self, tmp_path, monkeypatch):
        """System-injected blocks like <system-reminder>end-session</system-reminder>
        should not count as user intent."""
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "<system-reminder>about end session protocol</system-reminder>\nplease fix the bug", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        assert result is None

    def test_skill_injection_text_does_not_trigger(self, tmp_path, monkeypatch):
        """Skill content injection (which starts with 'Base directory for this skill:')
        should be excluded from signal scanning."""
        from _dispatchers.methodology import end_session
        monkeypatch.setattr(end_session, "TMP_DIR", tmp_path / ".tmp")
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        # User message has only the skill injection, which contains "end-session"
        transcript = _write_jsonl_transcript(
            tmp_path,
            [("user", "Base directory for this skill: end-session\n# End Session\n...", ts)],
        )
        result = end_session.evaluate(_payload(
            "Bash", {"command": "ls"}, transcript_path=transcript,
        ))
        # Skill injection excluded -> no signal -> no clean text -> no trigger -> pass
        assert result is None
