"""_signal_extract.py - Shared signal extraction for hook dispatcher sub-rules.

Runs ONCE per dispatcher invocation. Extracts the signals every sub-rule
needs (file_path normalized, content body, content head pre-prepped for
regex, command body, is_excluded_path flag, skill log) so sub-rules can
read pre-computed values from a signals dict instead of re-parsing
tool_input themselves.

Contract:
    extract(payload: dict | None) -> dict
        - Pure function. No I/O. Never raises.
        - Always returns a dict with canonical keys populated (defaults
          applied for missing fields).

    load_skill_log_today(*, log_dir: str | None = None) -> list[str]
        - Reads <log_dir>/skill-invocations-YYYY-MM-DD.json.
        - Default log_dir: ~/.claude/.tmp/
        - Returns lowercased skill names. Empty list on missing/malformed.
        - Never raises.

Source: Phase 2 architecture spec
  docs/superpowers/specs/2026-05-15-phase-2-architecture-spec.md Part A.3.

Cost amortization context:
  methodology-nudge.py (1100 LOC, ~30 regex patterns) and the other
  PreToolUse:Edit|Write sub-rules each re-parse tool_input, re-extract
  file_path / content, and re-run is_excluded_path checks independently.
  Phase 2 dispatcher consolidation collapses this duplicate work into a
  single call to extract() at dispatcher entry. Each sub-rule reads
  signals[key] instead of running its own parse.

Design discipline:
    - Pure stdlib (json, os, datetime). No external dependencies.
    - Pure functions; no global state.
    - No I/O at import time.
    - Tests at tests/test_signal_extract.py (TDD-first; written before this
      module).
"""
from __future__ import annotations

import json
import os
from datetime import datetime


# Path segments that mark a file as out-of-scope for sub-rule analysis.
# Mirrors methodology-nudge.is_excluded_path() so consolidation preserves
# behavior. Match performed on the LOWERCASED forward-slash-normalized path.
_EXCLUDED_SEGMENTS = (
    "/.tmp/",
    "/.git/",
    "/node_modules/",
    "/__pycache__/",
    "/processed/",
    "/inbox/",
    "/outbox/",
    "/memory/",
    "memory.md",
    "claude.md",
)

# Content head slice — first N chars are what regex scanners actually need.
# Long files get truncated to bound regex cost across sub-rules. Matches the
# 2000-char window used by most methodology-nudge.py triggers.
_CONTENT_HEAD_BYTES = 2000


def _normalize_path(raw):
    """Convert backslashes to forward slashes. Empty/None -> ''."""
    if not raw:
        return ""
    return str(raw).replace("\\", "/")


def _coerce_tool_input(raw):
    """Return a dict regardless of what shape tool_input arrived in.

    - dict: returned as-is
    - JSON string: parsed; falls back to {} on JSONDecodeError
    - None / other: {}
    """
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


def _is_excluded(file_path_lower):
    """Check the lowercased normalized path against the canonical exclusion
    set. Empty path is NOT excluded (caller may still want to act on a
    payload without a file path)."""
    if not file_path_lower:
        return False
    for seg in _EXCLUDED_SEGMENTS:
        if seg in file_path_lower:
            return True
    return False


def extract(payload):
    """Extract shared signals from a hook payload.

    Args:
        payload: dict | None. The JSON payload Claude Code writes to the
            hook's stdin (already json.loaded by the dispatcher).

    Returns:
        dict with every key in _CANONICAL_KEYS populated. Defaults applied
        for missing fields so sub-rules can read signals[key] without
        KeyError defenses.

    Never raises. Bad input yields defaults rather than crashing — the
    dispatcher must fail-OPEN per Phase 2 spec A.6 R5.
    """
    if not isinstance(payload, dict):
        payload = {}

    tool_name = str(payload.get("tool_name", "") or "")
    hook_event_name = str(payload.get("hook_event_name", "") or "")
    session_id = str(payload.get("session_id", "") or "")
    transcript_path = str(payload.get("transcript_path", "") or "")

    tool_input = _coerce_tool_input(payload.get("tool_input"))

    file_path = _normalize_path(tool_input.get("file_path", ""))
    file_path_lower = file_path.lower()

    # content_body: Write tools carry `content`; Edit tools carry
    # `new_string` (plus `old_string`). Mirror methodology-nudge.py line
    # 508 -- `content or new_string` -- so content wins when both are
    # present (Write payload with both keys present, edge case).
    content_raw = tool_input.get("content", "") or ""
    new_string_raw = tool_input.get("new_string", "") or ""
    content_body = str(content_raw) if content_raw else str(new_string_raw)
    content_head = content_body[:_CONTENT_HEAD_BYTES]

    command = str(tool_input.get("command", "") or "")
    old_string = str(tool_input.get("old_string", "") or "")
    new_string = str(new_string_raw)

    return {
        "tool_name": tool_name,
        "tool_input": tool_input,
        "hook_event_name": hook_event_name,
        "session_id": session_id,
        "transcript_path": transcript_path,
        "file_path": file_path,
        "file_path_lower": file_path_lower,
        "content_body": content_body,
        "content_head": content_head,
        "command": command,
        "old_string": old_string,
        "new_string": new_string,
        "is_excluded_path": _is_excluded(file_path_lower),
    }


def load_skill_log_today(*, log_dir=None):
    """Read today's skill-invocation log. Returns lowercased skill names.

    Args:
        log_dir: override directory containing the log file. Default:
            ~/.claude/.tmp/. Tests use a tmp_path override for isolation.

    Returns:
        list[str] of lowercased skill names invoked today. Empty list on:
          - log_dir missing
          - log file missing for today
          - log file present but malformed (JSON or shape)
          - log file present but lacking 'invocations' key
        Per-record skip when a record lacks a 'skill' key.

    Never raises. Logging issues must not break the dispatcher.
    """
    try:
        base_dir = log_dir or os.path.join(
            os.path.expanduser("~"), ".claude", ".tmp"
        )
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(base_dir, f"skill-invocations-{today}.json")
        if not os.path.isfile(log_path):
            return []
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return []
        invocations = data.get("invocations")
        if not isinstance(invocations, list):
            return []
        out = []
        for rec in invocations:
            if not isinstance(rec, dict):
                continue
            skill = rec.get("skill")
            if not skill:
                continue
            out.append(str(skill).lower())
        return out
    except (OSError, json.JSONDecodeError, ValueError, UnicodeDecodeError):
        return []
    except Exception:
        return []
