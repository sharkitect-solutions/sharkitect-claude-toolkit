"""
intent_detection.py - Shared user-driven-mode detection for gating hooks.

Closes wr-hq-2026-04-27-003 design portion. Provides a single tested helper
that gating hooks call to distinguish:

  - AI-autonomous initiation: AI is independently deciding to take an action.
    Full gate applies. Hook should fire.
  - User-driven work: user has explicitly directed the AI. Gate is pure
    friction. Hook should pass through.

Origin
======
Source incident: 2026-04-27 session. Chris filed wr-hq-2026-04-27-001/003/004
/005/006 in 24 hours after hooks blocked routine cascade work he had
explicitly authorized. Quote: "If we are working and I tell you to do it,
that should bypass this hook anyway. ... I should be working on something
else and come back, and you'd be done." Friction quantified at ~30 min/day
during cascade sessions.

Design philosophy
=================
- HARD GATES STAY HARD for AI-autonomous initiation. The hooks were created
  in response to real incidents (e.g., Section 13/14 SOW legal language
  shipped without proper review). Removing gates would re-introduce that
  risk.
- BYPASSING IS DETECTION-BASED, not vocabulary-based. The legacy approach
  required the user to learn private bypass keywords ("skip pmm", "skip
  sow-stack"). This module recognizes natural-language imperatives so the
  user can just talk normally.
- CONSERVATIVE BIAS. False positive (incorrectly classifying as user-driven
  when AI is autonomous) is the dangerous direction -- gates would let
  unauthorized work through. False negative (incorrectly classifying as
  AI-autonomous when user is driving) is just friction -- user can re-issue
  with a stronger imperative or use literal bypass.
- LIBRARY-LIKE CONTRACT. No I/O side effects. No print statements. No mutation
  of caller state. Pure functions returning structured dicts. Test-friendly.

Public API
==========

detect_user_driven_mode(
    transcript_path: str | None,
    *,
    file_path: str | None = None,
    bypass_phrases: tuple[str, ...] = (),
    lookback: int = 15,
) -> dict

  Returns: {
    "is_user_driven": bool,
    "match_type": "literal_bypass" | "session_intent" | "imperative_aligned"
                  | "imperative_general" | None,
    "matched_phrase": str | None,
    "matched_message_index": int | None,  # 0 = most recent
    "evidence": str,  # human-readable explanation for hook output
  }

Detection tiers (priority order; first match wins)
==================================================

Tier 1: Literal bypass phrase
  Caller passes a tuple of literal bypass strings. Substring match in any
  recent user message. Backwards-compatible with existing hooks.

Tier 2: Session-level intent flag
  User said "i am driving this", "i'm driving this", "user-driven session",
  "i drive this", "i'm steering this", or similar within the lookback window.
  Recognized universally. Lasts the session.

Tier 3a: Imperative aligned to file
  User issued an imperative verb directive AND mentioned the file/path being
  edited (or its basename without extension, or a recognizable shortform).
  High-confidence user-driven signal.

Tier 3b: Imperative general
  User issued an imperative verb directive but no file alignment. Medium-
  confidence user-driven signal. Still passes the gate -- the imperative is
  the authorization.

Tier 4: Default
  No match. is_user_driven = False. Hook should fire fully.

read_recent_user_messages(transcript_path, lookback=15) -> list[str]

  Helper for reading the transcript. Filters tool-result echo records (the
  schema marks them type='user' but they're just system tool output, not
  real user prose). Returns up to `lookback` lowercased real user messages,
  most recent first.

Implementation notes
====================
- Pure stdlib (json, os, re, typing).
- All errors return safe default (is_user_driven=False).
- Tested via tests/test_intent_detection.py.
"""
from __future__ import annotations

import json
import os
import re
from typing import Optional, Sequence

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_LOOKBACK = 15

# Imperative verbs recognized in user messages. Matched against word boundaries.
# Ordered roughly by editing -> generation -> execution categories. Add
# carefully -- broad verbs ("do", "make") are intentionally listed so direct
# directives ("do it", "make it work") are caught.
IMPERATIVE_VERBS = (
    # Editing / refining
    "update", "modify", "change", "edit", "rewrite", "refactor", "fix",
    "polish", "tweak", "adjust", "tighten", "broaden", "narrow", "expand",
    "trim", "shorten", "lengthen", "rephrase", "reword", "restructure",
    "reorganize",
    # Adding / removing
    "add", "insert", "append", "prepend", "include", "remove", "delete",
    "drop", "strip", "exclude",
    # Creating
    "create", "build", "make", "generate", "draft", "write", "compose",
    "produce",
    # Operating
    "run", "execute", "deploy", "publish", "ship", "release", "merge",
    "rebase", "push", "pull", "sync", "cascade", "propagate", "apply",
    # Routing
    "route", "send", "post", "file", "open", "close", "process", "handle",
    "implement",
    # Direct
    "do", "proceed", "continue", "go",
)

# Imperative patterns. Each one captures a recent user message that the user
# almost certainly means as an authorization. Patterns are case-insensitive.
# Word boundaries used to avoid matching "update" inside "duplicated" etc.
_VERB_GROUP = "(?:" + "|".join(re.escape(v) for v in IMPERATIVE_VERBS) + ")"

IMPERATIVE_PATTERNS = (
    # Direct imperative at start of message: "update X", "fix Y", "broaden Z"
    re.compile(rf"^\s*(?:please\s+)?{_VERB_GROUP}\b", re.IGNORECASE),
    # "let's update X", "let's go" - common cascade authorization
    re.compile(rf"\blet'?s\s+{_VERB_GROUP}\b", re.IGNORECASE),
    # "go ahead and X", "now X", "now go and X"
    re.compile(rf"\b(?:go\s+ahead\s+and|now|then|next)\s+{_VERB_GROUP}\b", re.IGNORECASE),
    # "can you X", "could you X", "would you X"
    re.compile(rf"\b(?:can|could|would|will)\s+you\s+(?:please\s+)?{_VERB_GROUP}\b", re.IGNORECASE),
    # "i want you to X", "i need you to X"
    re.compile(rf"\bi\s+(?:want|need|expect|ask)\s+you\s+to\s+{_VERB_GROUP}\b", re.IGNORECASE),
    # Direct authorization: "do it", "execute this", "make it so", "ship it",
    # "go for it", "proceed with"
    re.compile(r"\b(?:do\s+it|execute\s+this|make\s+it\s+so|ship\s+it|"
               r"go\s+for\s+it|proceed\s+with|make\s+the\s+(?:edit|change|update|fix)|"
               r"yes\s+(?:do\s+that|proceed|go\s+ahead)|sounds\s+good\s+go|"
               r"sounds\s+good\s+(?:proceed|continue))\b", re.IGNORECASE),
    # Cascade-specific: "knock out X", "knock these out", "clean up X"
    re.compile(r"\bknock\s+(?:out|these|them|that)", re.IGNORECASE),
    re.compile(r"\bclean\s+up\b", re.IGNORECASE),
)

# Session-level intent flags. Recognized once anywhere in the lookback window
# and treats the rest of the session as user-driven.
SESSION_INTENT_PATTERNS = (
    re.compile(r"\bi'?m\s+driving\s+(?:this|the\s+session)", re.IGNORECASE),
    re.compile(r"\bi\s+am\s+driving\s+(?:this|the\s+session)", re.IGNORECASE),
    re.compile(r"\buser[-\s]driven\s+session", re.IGNORECASE),
    re.compile(r"\bi'?m\s+steering\s+this", re.IGNORECASE),
    re.compile(r"\bi\s+drive\s+this", re.IGNORECASE),
    # "let me drive" / "i'll drive"
    re.compile(r"\b(?:let\s+me|i'?ll)\s+drive\b", re.IGNORECASE),
)


# ---------------------------------------------------------------------------
# Transcript reading
# ---------------------------------------------------------------------------

def _is_tool_result_message(content) -> bool:
    """True if a transcript record's content is purely tool-result echoes,
    not real user prose. The transcript schema marks tool-result messages as
    type='user' but their content is a list with type='tool_result' items.

    Filtering these out (origin: wr-hq-2026-04-27-001 lookback bug) prevents
    the bypass window from expiring after several successful tool calls.
    """
    if not isinstance(content, list):
        return False
    has_tool_result = any(
        isinstance(p, dict) and p.get("type") == "tool_result"
        for p in content
    )
    has_text = any(
        isinstance(p, dict) and p.get("type") == "text" and (p.get("text") or "").strip()
        for p in content
    )
    return has_tool_result and not has_text


def read_recent_user_messages(
    transcript_path: Optional[str],
    lookback: int = DEFAULT_LOOKBACK,
) -> list:
    """Return up to `lookback` most-recent real user messages, most recent
    first, all lowercased. Tool-result echoes filtered out.

    Returns [] if the transcript is missing or unreadable.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    try:
        with open(transcript_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return []

    out = []
    for raw in reversed(lines):
        if len(out) >= lookback:
            break
        try:
            rec = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue
        if rec.get("type") != "user":
            continue
        content = rec.get("message", {}).get("content", "")
        if _is_tool_result_message(content):
            continue
        if isinstance(content, list):
            content = " ".join(
                (p.get("text") or "") for p in content if isinstance(p, dict)
            )
        text = str(content).lower().strip()
        if not text:
            continue
        out.append(text)
    return out


# ---------------------------------------------------------------------------
# Core detection
# ---------------------------------------------------------------------------

def _file_aliases(file_path: Optional[str]) -> list:
    """Generate likely aliases for a file path that a user might mention.

    For "C:/path/to/icp.md" this returns ["icp.md", "icp"].
    For "knowledge-base/strategy/icp.md" returns ["icp.md", "icp"].
    Returns [] if file_path is None.
    """
    if not file_path:
        return []
    base = os.path.basename(file_path)
    aliases = [base.lower()]
    stem = os.path.splitext(base)[0]
    if stem and stem.lower() != base.lower():
        aliases.append(stem.lower())
    # Strip language suffixes like "-es" so "icp.md" matches "icp-es.md"
    if "-" in stem:
        head = stem.split("-")[0]
        if head and head.lower() not in aliases:
            aliases.append(head.lower())
    return aliases


def _has_session_intent(messages: Sequence[str]) -> Optional[tuple]:
    """Search lookback window for a session-level intent flag.

    Returns (matched_phrase, message_index) if found, else None.
    """
    for idx, msg in enumerate(messages):
        for pat in SESSION_INTENT_PATTERNS:
            m = pat.search(msg)
            if m:
                return (m.group(0), idx)
    return None


def _has_literal_bypass(
    messages: Sequence[str],
    bypass_phrases: Sequence[str],
) -> Optional[tuple]:
    """Substring-match any of the caller's literal bypass phrases against
    recent user messages.

    Returns (matched_phrase, message_index) if found, else None.
    """
    if not bypass_phrases:
        return None
    for idx, msg in enumerate(messages):
        for phrase in bypass_phrases:
            if phrase and phrase.lower() in msg:
                return (phrase, idx)
    return None


def _has_imperative(
    messages: Sequence[str],
    file_aliases: Sequence[str],
) -> Optional[tuple]:
    """Search lookback window for an imperative directive.

    Returns (match_type, matched_phrase, message_index) where match_type is
    "imperative_aligned" if the same message references one of file_aliases,
    or "imperative_general" otherwise. Returns None if no imperative.

    Most-recent message has priority. Within a single message, alignment
    is checked.
    """
    for idx, msg in enumerate(messages):
        for pat in IMPERATIVE_PATTERNS:
            m = pat.search(msg)
            if not m:
                continue
            # Found imperative. Check alignment.
            aligned = False
            if file_aliases:
                for alias in file_aliases:
                    if alias and alias in msg:
                        aligned = True
                        break
            match_type = "imperative_aligned" if aligned else "imperative_general"
            return (match_type, m.group(0), idx)
    return None


def detect_user_driven_mode(
    transcript_path: Optional[str],
    *,
    file_path: Optional[str] = None,
    bypass_phrases: Sequence[str] = (),
    lookback: int = DEFAULT_LOOKBACK,
) -> dict:
    """Classify the current Edit/Write call as AI-autonomous or user-driven.

    Args:
      transcript_path: path to current session transcript (from hook stdin)
      file_path: optional file being edited; enables alignment scoring
      bypass_phrases: caller-specific literal bypass strings (backwards
        compat with each hook's existing bypass vocabulary)
      lookback: how many recent user messages to scan (default 15)

    Returns: dict with keys:
      is_user_driven: bool
      match_type: str | None
      matched_phrase: str | None
      matched_message_index: int | None  (0 = most recent)
      evidence: str  (one-line human-readable explanation)

    On any error, returns the safe default (is_user_driven=False).
    """
    default = {
        "is_user_driven": False,
        "match_type": None,
        "matched_phrase": None,
        "matched_message_index": None,
        "evidence": "no user-driven signal found in lookback window",
    }
    try:
        messages = read_recent_user_messages(transcript_path, lookback=lookback)
        if not messages:
            return default

        # Tier 1: literal bypass (caller's vocabulary)
        hit = _has_literal_bypass(messages, bypass_phrases)
        if hit:
            phrase, idx = hit
            return {
                "is_user_driven": True,
                "match_type": "literal_bypass",
                "matched_phrase": phrase,
                "matched_message_index": idx,
                "evidence": f"literal bypass phrase '{phrase}' found in user message #{idx}",
            }

        # Tier 2: session-level intent flag
        hit = _has_session_intent(messages)
        if hit:
            phrase, idx = hit
            return {
                "is_user_driven": True,
                "match_type": "session_intent",
                "matched_phrase": phrase,
                "matched_message_index": idx,
                "evidence": f"session intent flag '{phrase}' found in user message #{idx}",
            }

        # Tier 3: imperative directive (aligned > general)
        aliases = _file_aliases(file_path)
        hit = _has_imperative(messages, aliases)
        if hit:
            match_type, phrase, idx = hit
            evidence = (
                f"{match_type} directive '{phrase}' in user message #{idx}"
                + (f" (file alias matched)" if match_type == "imperative_aligned" else "")
            )
            return {
                "is_user_driven": True,
                "match_type": match_type,
                "matched_phrase": phrase,
                "matched_message_index": idx,
                "evidence": evidence,
            }

        # Tier 4: default
        return default

    except Exception:
        # Safe-fail: anything wrong -> AI-autonomous (gate fires, no bypass).
        return default


# ---------------------------------------------------------------------------
# Convenience wrappers used by hook short-circuits
# ---------------------------------------------------------------------------

def is_user_driven(
    transcript_path: Optional[str],
    *,
    file_path: Optional[str] = None,
    bypass_phrases: Sequence[str] = (),
    lookback: int = DEFAULT_LOOKBACK,
) -> bool:
    """Boolean wrapper. Returns True if the current Edit/Write should bypass
    the gate due to user direction. Calls `detect_user_driven_mode` and
    returns its `is_user_driven` field.
    """
    return detect_user_driven_mode(
        transcript_path,
        file_path=file_path,
        bypass_phrases=bypass_phrases,
        lookback=lookback,
    )["is_user_driven"]
