"""end_session.py - Methodology dispatcher sub-rule (Phase 2 Build #2B).

Source: end-session-enforcer.py (HARD GATE: when user signals end-of-session
in recent transcript AND end-session skill not invoked AFTER the signal,
block Bash/Write/Edit/TodoWrite to force formal Skill invocation).

Behavior preserved 1:1 from source (700 LOC). Includes:
  - End-session signal patterns (end session, wrap up, /end-session, etc.)
  - Descriptive marker exemption (simile / past reference / discussion)
  - Silencer phrases (still working, not ending, etc.)
  - Skill log timestamp comparison (invocation AFTER signal bypasses)
  - Bypass phrases in transcript and tool content
  - Meta-path exemptions for Write/Edit
  - BLOCKED_TOOLS filter (only Bash, Write, Edit, TodoWrite)
  - System-block stripping (system-reminder, user-prompt-submit-hook, etc.)
  - Skill content injection exemption (Base directory for this skill: prefix)
  - Timezone-aware ISO parsing (mixed UTC/local timestamps in skill log)
  - TRANSCRIPT_USER_LOOKBACK=1 (S50 fix)

Severity: HARD GATE (returns {"decision": "deny", "reason": ...})

Source: wr-2026-04-23-006 + S50 + S51 + S43 history -- the source is the
end-session-enforcer.py at ~/.claude/hooks/. Spec: docs/superpowers/specs/
2026-05-15-phase-2-architecture-spec.md (Part A).

# skip end-session -- self-referential meta-module, structural exemption.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events
except Exception:
    _feedback_events = None


TMP_DIR = Path.home() / ".claude" / ".tmp"
SKILL_NAME = "end-session"

BYPASS_PHRASES = (
    "skip end-session",
    "skip end session",
    "no end-session",
    "save progress quickly",
)

SILENCER_PHRASES = (
    "still working",
    "still going",
    "not ending",
    "not done yet",
    "ignore that",
)

END_SESSION_PATTERNS = [
    re.compile(r"\bend\s+(?:the\s+)?session\b", re.I),
    re.compile(r"\bwrap(?:ping)?\s+up\b", re.I),
    re.compile(r"\bstop\s+for\s+the\s+day\b", re.I),
    re.compile(r"\bthat'?s\s+it\s+for\s+today\b", re.I),
    re.compile(r"\bdone\s+for\s+(?:today|the\s+day)\b", re.I),
    re.compile(r"\bclose\s+(?:out|the\s+session)\b", re.I),
    re.compile(r"\bsave\s+session\b", re.I),
    re.compile(r"/end-session\b", re.I),
]

DESCRIPTIVE_MARKERS = re.compile(
    r"\b(?:"
    r"(?:sort|kind|just)\s+of\s+like|just\s+like"
    r"|as\s+(?:if|though)"
    r"|remember(?:ed)?(?:\s+(?:when|how))?"
    r"|earlier|yesterday|previously|the\s+other\s+day"
    r"|we\s+(?:did|had|used\s+to)|that\s+happened"
    r"|talking\s+about|talked\s+about|discussing|discussion\s+of"
    r"|mention(?:ed|ing)?|referenc(?:ed|ing)?|discussed"
    r"|for\s+example|such\s+as|e\.g\.|i\.e\."
    r"|called|named"
    r"|concept\s+of|idea\s+of|definition\s+of|the\s+term|the\s+phrase"
    r"|broke\s+(?:the|because|when)"
    r")\b",
    re.I,
)
DESCRIPTIVE_LOOKBEHIND = 60

META_PATH_MARKERS = (
    "/.work-requests/",
    "/.lifecycle-reviews/",
    "/.routed-tasks/",
    "/.claude/projects/",
    "/memory/feedback_",
)

SKILL_INJECTION_PREFIX = "Base directory for this skill:"

SYSTEM_BLOCK_TAGS = (
    "system-reminder",
    "user-prompt-submit-hook",
    "command-message",
    "command-name",
    "command-args",
    "command-stdout",
    "command-stderr",
    "ide_selection",
    "ide_opened_file",
    "local-command-stdout",
    "local-command-stderr",
)
SYSTEM_BLOCK_RE = re.compile(
    r"<(?:" + "|".join(SYSTEM_BLOCK_TAGS) + r")\b[^>]*>.*?</(?:"
    + "|".join(SYSTEM_BLOCK_TAGS) + r")\s*>",
    re.S | re.I,
)

TRANSCRIPT_USER_LOOKBACK = 1

BLOCKED_TOOLS = frozenset({"Bash", "Write", "Edit", "TodoWrite"})


def strip_system_blocks(text):
    if not text:
        return ""
    try:
        return SYSTEM_BLOCK_RE.sub("", text)
    except Exception:
        return text


def parse_iso_timestamp(s):
    """Parse ISO-8601 timestamp. Return tz-aware UTC datetime, or None."""
    if not s or not isinstance(s, str):
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        dt = dt.astimezone(timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def load_skill_log_records():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        invs = data.get("invocations", [])
        return invs if isinstance(invs, list) else []
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return []


def checkpoint_invoked_after(signal_ts):
    records = load_skill_log_records()
    if not records:
        return False
    for rec in records:
        skill = str(rec.get("skill", "")).lower()
        bare = skill.split(":")[-1] if ":" in skill else skill
        if bare != SKILL_NAME:
            continue
        if signal_ts is None:
            return True  # graceful fallback
        inv_ts = parse_iso_timestamp(rec.get("timestamp"))
        if inv_ts is None:
            continue
        if inv_ts > signal_ts:
            return True
    return False


def extract_text_from_content(content):
    if isinstance(content, str):
        if content.lstrip().startswith(SKILL_INJECTION_PREFIX):
            return ""
        return content
    if isinstance(content, list):
        parts = []
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "text":
                text = str(blk.get("text", ""))
                if text.lstrip().startswith(SKILL_INJECTION_PREFIX):
                    continue
                parts.append(text)
        return "\n".join(parts)
    return ""


def _iter_recent_user_text_messages(transcript_path, limit):
    if not transcript_path:
        return
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return
        with p.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return

    text_msgs_seen = 0
    for line in reversed(lines):
        if text_msgs_seen >= limit:
            return
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if rec.get("type") != "user":
            continue
        msg = rec.get("message") or {}
        text = extract_text_from_content(msg.get("content"))
        clean = strip_system_blocks(text)
        if not clean.strip():
            continue
        text_msgs_seen += 1
        yield (rec, clean)


def find_most_recent_end_session(transcript_path):
    for rec, clean in _iter_recent_user_text_messages(transcript_path, TRANSCRIPT_USER_LOOKBACK):
        if contains_end_session_signal(clean):
            ts = parse_iso_timestamp(rec.get("timestamp"))
            return (ts, True)
    return (None, False)


def find_most_recent_silencer(transcript_path):
    for rec, clean in _iter_recent_user_text_messages(transcript_path, 3):
        low = clean.lower()
        if any(phrase in low for phrase in SILENCER_PHRASES):
            ts = parse_iso_timestamp(rec.get("timestamp"))
            return (ts, True)
    return (None, False)


def _is_descriptive_reference(text, match_pos):
    if not text or match_pos <= 0:
        return False
    start = max(0, match_pos - DESCRIPTIVE_LOOKBEHIND)
    window = text[start:match_pos]
    parts = re.split(r"(?:[.!?]+\s+|\n+)", window)
    current_sentence = parts[-1] if parts else window
    return bool(DESCRIPTIVE_MARKERS.search(current_sentence))


def contains_end_session_signal(text):
    if not text:
        return False
    for pat in END_SESSION_PATTERNS:
        for m in pat.finditer(text):
            if not _is_descriptive_reference(text, m.start()):
                return True
    return False


def recent_user_messages_contain_bypass(transcript_path):
    if not transcript_path:
        return False
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return False
        with p.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return False

    user_msgs_seen = 0
    for line in reversed(lines):
        if user_msgs_seen >= TRANSCRIPT_USER_LOOKBACK:
            break
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if rec.get("type") != "user":
            continue
        user_msgs_seen += 1
        msg = rec.get("message") or {}
        text = extract_text_from_content(msg.get("content"))
        clean = strip_system_blocks(text).lower()
        if any(phrase in clean for phrase in BYPASS_PHRASES):
            return True
    return False


def extract_write_content(tool_name, tool_input):
    if not isinstance(tool_input, dict):
        return ""
    if tool_name == "Write":
        content = tool_input.get("content", "")
        return content if isinstance(content, str) else ""
    if tool_name == "Edit":
        parts = []
        for key in ("new_string", "old_string"):
            v = tool_input.get(key, "")
            if isinstance(v, str):
                parts.append(v)
        return "\n".join(parts)
    if tool_name == "TodoWrite":
        todos = tool_input.get("todos", [])
        if not isinstance(todos, list):
            return ""
        parts = []
        for t in todos:
            if isinstance(t, dict):
                parts.append(str(t.get("content", "")))
                parts.append(str(t.get("activeForm", "")))
        return "\n".join(parts)
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        desc = tool_input.get("description", "")
        return (cmd if isinstance(cmd, str) else "") + "\n" + (desc if isinstance(desc, str) else "")
    return ""


def has_bypass_in_content(content):
    if not content:
        return False
    low = content.lower()
    if any(phrase in low for phrase in BYPASS_PHRASES):
        return True
    if any(phrase in low for phrase in SILENCER_PHRASES):
        return True
    return False


def is_meta_path(file_path):
    if not file_path:
        return False
    norm = file_path.replace("\\", "/").lower()
    return any(marker in norm for marker in META_PATH_MARKERS)


def _deny_reason():
    return (
        "BLOCKING: End-session signal detected in recent user messages "
        "but the end-session skill has not been formally invoked "
        "via the Skill tool. Inline execution of the 9 checkpoint steps "
        "(git commit, supabase-sync, file writes, etc.) is NOT an "
        "acceptable substitute: it bypasses the formal audit gate, "
        "provides no visible confirmation to the user, and breaks "
        "pattern consistency across sessions. "
        "Run: `Skill end-session` (or use /end-session). "
        "Bypass phrases (include in your next response or tool content): "
        "'skip end-session', 'skip end session', 'no end-session', "
        "'save progress quickly' (the last signals you want the "
        "mid-session session-checkpoint skill instead, not full end-session). "
        "Meta paths under /.work-requests/ /.lifecycle-reviews/ "
        "/.routed-tasks/ /.claude/projects/*/memory/ are structurally "
        "exempt. Source: wr-2026-04-23-006."
    )


def evaluate(payload):
    """Evaluate end_session sub-rule.

    Returns:
      None                                  -> sub-rule did not trigger / pass-through
      {"decision": "deny", "reason": "..."} -> HARD GATE
    """
    tool_name = payload.get("tool_name", "")
    if tool_name not in BLOCKED_TOOLS:
        return None

    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    # Meta-path exemption for Write/Edit targets
    if tool_name in ("Write", "Edit"):
        file_path = str(tool_input.get("file_path", "") or "")
        if is_meta_path(file_path):
            return None

    transcript_path = payload.get("transcript_path") or ""
    signal_ts, signal_found = find_most_recent_end_session(transcript_path)
    if not signal_found:
        return None

    # Silencer bypass: silencer with ts >= signal stands down
    silencer_ts, silencer_found = find_most_recent_silencer(transcript_path)
    if silencer_found:
        if signal_ts is None or silencer_ts is None:
            return None  # graceful: missing timestamp, bias toward allow
        if silencer_ts >= signal_ts:
            return None

    # Skill log bypass: end-session invoked AFTER the signal
    if checkpoint_invoked_after(signal_ts):
        return None

    # Bypass phrase in recent transcript
    if recent_user_messages_contain_bypass(transcript_path):
        return None

    # Bypass phrase in current tool content
    content = extract_write_content(tool_name, tool_input)
    if has_bypass_in_content(content):
        return None

    # Block
    if _feedback_events:
        try:
            _feedback_events.record(
                cluster="methodology", sub_rule="end_session",
                decision="hard_deny", trigger="end_session_signal_no_bypass",
                payload=payload,
            )
        except Exception:
            pass
    return {"decision": "deny", "reason": _deny_reason()}
