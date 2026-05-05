"""Tests for _dispatchers/_feedback_events.py shared event-logging interface.

TDD-first: these tests are written before _feedback_events.py exists.
They define the contract:

  record(cluster, sub_rule, decision, trigger, payload, *, stream_path=None)
    - Appends one JSONL record to the feedback events stream.
    - Never raises (silent failure on I/O errors).
    - Filters sensitive fields from payload before recording.

Stream location:
  Default: <tempdir>/feedback_events.jsonl
  Override: stream_path argument (used by tests for isolation)

Tests verify:
  1. record() writes a structured JSONL line on success
  2. record() with all-empty fields still produces a valid record
  3. record() never raises on permission/disk errors
  4. record() filters sensitive payload fields (file_content, command bodies)
  5. Multiple records append (not overwrite)
  6. Stream is JSONL-parseable (one valid JSON object per line)
"""
from __future__ import annotations

import json
import os
import sys

import pytest

# Make the hooks/ dir importable for the _dispatchers package
HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


def test_record_writes_jsonl_line(tmp_path):
    from _dispatchers import _feedback_events as fe
    stream = tmp_path / "events.jsonl"
    fe.record(
        cluster="methodology",
        sub_rule="brainstorming",
        decision="advisory",
        trigger="3+ options in user message",
        payload={"tool_name": "Write", "tool_input": {"file_path": "/x"}},
        stream_path=str(stream),
    )
    lines = stream.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["cluster"] == "methodology"
    assert rec["sub_rule"] == "brainstorming"
    assert rec["decision"] == "advisory"
    assert rec["trigger"] == "3+ options in user message"
    assert "ts" in rec  # timestamp added by record()


def test_record_appends_not_overwrites(tmp_path):
    from _dispatchers import _feedback_events as fe
    stream = tmp_path / "events.jsonl"
    fe.record(cluster="m", sub_rule="r1", decision="advisory",
              trigger="t1", payload={}, stream_path=str(stream))
    fe.record(cluster="m", sub_rule="r2", decision="hard_deny",
              trigger="t2", payload={}, stream_path=str(stream))
    lines = stream.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["sub_rule"] == "r1"
    assert json.loads(lines[1])["sub_rule"] == "r2"


def test_record_never_raises_on_unwritable_path(tmp_path):
    """The hook MUST NEVER break the user's tool call due to logging issues."""
    from _dispatchers import _feedback_events as fe
    # Path under a directory that doesn't exist — record() should silently fail
    bad = tmp_path / "nonexistent_dir" / "subdir" / "events.jsonl"
    # Should NOT raise
    fe.record(cluster="m", sub_rule="r", decision="advisory",
              trigger="t", payload={}, stream_path=str(bad))


def test_record_filters_sensitive_payload_fields(tmp_path):
    """Tool content (file content, Bash command body) should NOT be recorded
    verbatim — only metadata (paths, tool name, decision)."""
    from _dispatchers import _feedback_events as fe
    stream = tmp_path / "events.jsonl"
    sensitive_payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "/x.py",
            "content": "API_KEY=sk-secret-12345\nPASSWORD=pw",  # MUST NOT appear
        },
    }
    fe.record(cluster="m", sub_rule="r", decision="advisory",
              trigger="t", payload=sensitive_payload, stream_path=str(stream))
    raw = stream.read_text(encoding="utf-8")
    assert "sk-secret-12345" not in raw
    assert "PASSWORD" not in raw
    rec = json.loads(raw.splitlines()[0])
    # Metadata IS allowed in the recorded payload
    assert rec.get("payload", {}).get("tool_name") == "Write"
    assert rec.get("payload", {}).get("file_path") == "/x.py"


def test_record_filters_bash_command_body(tmp_path):
    """Bash command bodies often contain secrets (env vars, tokens) — filter them."""
    from _dispatchers import _feedback_events as fe
    stream = tmp_path / "events.jsonl"
    sensitive = {
        "tool_name": "Bash",
        "tool_input": {
            "command": "curl -H 'Authorization: Bearer sk-very-secret' https://api.example.com",
        },
    }
    fe.record(cluster="m", sub_rule="r", decision="hard_deny",
              trigger="t", payload=sensitive, stream_path=str(stream))
    raw = stream.read_text(encoding="utf-8")
    assert "sk-very-secret" not in raw
    assert "Bearer" not in raw


def test_record_includes_session_metadata(tmp_path):
    from _dispatchers import _feedback_events as fe
    stream = tmp_path / "events.jsonl"
    fe.record(
        cluster="content_governance",
        sub_rule="marketing_keywords",
        decision="hard_deny",
        trigger="GTM keyword",
        payload={"session_id": "test-session-123", "tool_name": "Write",
                 "tool_input": {"file_path": "/y.md"}},
        stream_path=str(stream),
    )
    rec = json.loads(stream.read_text(encoding="utf-8").splitlines()[0])
    assert rec["payload"].get("session_id") == "test-session-123"


def test_record_with_empty_fields(tmp_path):
    """Edge case: all-empty fields still produce a valid JSONL line (no crash)."""
    from _dispatchers import _feedback_events as fe
    stream = tmp_path / "events.jsonl"
    fe.record(cluster="", sub_rule="", decision="", trigger="",
              payload={}, stream_path=str(stream))
    lines = stream.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert "ts" in rec


def test_record_with_invalid_decision_falls_back_safely(tmp_path):
    """Invalid decision values are recorded as-is (caller responsibility) but don't crash."""
    from _dispatchers import _feedback_events as fe
    stream = tmp_path / "events.jsonl"
    fe.record(cluster="m", sub_rule="r", decision="WAT_INVALID",
              trigger="t", payload={}, stream_path=str(stream))
    rec = json.loads(stream.read_text(encoding="utf-8").splitlines()[0])
    assert rec["decision"] == "WAT_INVALID"
