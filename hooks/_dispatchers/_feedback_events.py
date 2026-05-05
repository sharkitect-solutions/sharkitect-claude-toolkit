"""_feedback_events.py - Shared event-logging interface for hook dispatcher sub-rules.

Records one structured JSONL line per sub-rule decision (gate / nudge /
pass-through). The stream becomes the input data for AIOS Feedback Loop
Type 5 (System Learning) per
`docs/superpowers/specs/2026-05-03-aios-feedback-loop-spec-v1.0.md`.

Contract:
    record(cluster, sub_rule, decision, trigger, payload, *, stream_path=None)

Behavior:
    - Append-only JSONL line on success.
    - Failures are silent (a logging failure must NEVER break the hook
      that called it). Hooks rely on this contract for graceful degradation.
    - Sensitive fields are stripped from payload before recording.
      Tool content (file content, Bash command bodies) often contains
      secrets/tokens; only metadata (paths, tool name, session id, matcher)
      is preserved.

Stream location:
    Default: <tempdir>/feedback_events.jsonl
    Override: pass stream_path argument (used by tests for isolation)

Downstream:
    Sentinel runs a nightly job mirroring this file to the Supabase
    feedback_events table for trend analysis. dream-consolidation reads
    it for pattern detection.

Design discipline:
    - Pure stdlib (json, os, tempfile, datetime). No external dependencies.
    - Pure functions; no global state.
    - No I/O at import time.
    - Tests at tests/test_feedback_events.py (TDD-first; written before this
      module).
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone


_DEFAULT_STREAM = os.path.join(tempfile.gettempdir(), "feedback_events.jsonl")

# Top-level payload keys safe to record (metadata only -- no content / secrets).
_SAFE_PAYLOAD_KEYS = (
    "tool_name",
    "session_id",
    "matcher",
    "hook_event_name",
    "workspace",
)


def _filter_payload(payload):
    """Strip sensitive fields from payload before recording.

    Keeps:
      - Top-level metadata: tool_name, session_id, matcher, hook_event_name,
        workspace
      - tool_input.file_path (promoted to top-level for easier querying)

    Strips:
      - tool_input.content (file content -- may contain secrets)
      - tool_input.new_string (Edit body -- may contain secrets)
      - tool_input.old_string (Edit anchor -- conservative: strip; the
        file path alone is enough for trend analysis)
      - tool_input.command (Bash body -- frequently contains tokens)
      - Any other unrecognized fields (default-deny)

    Returns:
      dict with only the safe subset, or empty dict if input is not a dict
      or the dict has no safe fields.
    """
    if not isinstance(payload, dict):
        return {}

    out = {}
    for k in _SAFE_PAYLOAD_KEYS:
        if k in payload:
            out[k] = payload[k]

    ti = payload.get("tool_input")
    if isinstance(ti, dict):
        fp = ti.get("file_path")
        if fp:
            out["file_path"] = fp

    return out


def record(cluster, sub_rule, decision, trigger, payload, *, stream_path=None):
    """Append one record to the feedback events stream.

    Args:
        cluster: 'methodology' | 'content_governance' | 'post_action' (or
            any string -- caller's responsibility to use the canonical set)
        sub_rule: name of the sub-rule (e.g., 'brainstorming')
        decision: 'pass_through' | 'advisory' | 'hard_deny' (or any string)
        trigger: short human-readable description of what fired
        payload: dict with tool_name, tool_input, session_id, etc.
            (filtered before recording)
        stream_path: override the default stream location. Used by tests
            for isolation; production code uses the default.

    Returns:
        None.

    Never raises. Any exception during serialization or I/O is silently
    swallowed -- the hook layer must not break user tool calls due to
    logging issues.
    """
    try:
        path = stream_path or _DEFAULT_STREAM
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "cluster": str(cluster),
            "sub_rule": str(sub_rule),
            "decision": str(decision),
            "trigger": str(trigger),
            "payload": _filter_payload(payload),
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        # Silent: never break the calling hook.
        pass
