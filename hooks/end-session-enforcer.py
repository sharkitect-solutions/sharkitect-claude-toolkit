"""
end-session-enforcer.py - PreToolUse BLOCKING hook for formal invocation
of the end-session skill when the user triggers an end-session signal.

RENAMED 2026-05-12 (S45) from session-checkpoint-enforcer.py. The previous
filename was a legacy artifact from before the skill split: what is now
called `end-session` was originally called `session-checkpoint`. After the
rename, this hook (which enforces end-session) carried the old filename,
producing chronic confusion in deny messages and bypass vocabulary. The
rename + bypass cleanup happened in S45 mid-session per user direction:
"the simple session checkpoint should not have 'mid' afterward... there
is still confusion about that, so we need to make sure it is cleaned up."

Source: wr-2026-04-23-006 (skill-management-hub). User flagged twice in a
24h window (2026-04-22 evening, 2026-04-23 morning) that the AI ran the
9-step checkpoint protocol INLINE (sequence of Bash + Write calls) instead
of invoking the end-session skill via the Skill tool. Inline execution
bypasses the formal audit gate, provides no visible confirmation to the
user, and breaks pattern consistency across sessions. User quote
2026-04-23: "This is a big gap that's been happening. It's very
inconsistent. It was working perfectly fine, and now, all of a sudden,
you guys have gotten slack on it."

Memory rule: "If a rule keeps getting violated, add detection, don't
reinforce the rule." Documentation alone proved insufficient; runtime
enforcement mirrors brainstorming-enforcer and hook-development-enforcer.

DETECTION
  - One of the most-recent 10 user messages contains an end-session
    signal (word-boundary matches on transcript text after stripping
    system-injected blocks). Signals:
        "end session", "end the session", "wrap up",
        "stop for the day", "that's it for today" / "thats it for today",
        "close out" / "close the session",
        "save session", "wrapping up", "done for today",
        "/end-session"
  - AND NO end-session skill invocation has been logged with a
    timestamp greater than that signal's transcript timestamp.

  Note: bare "checkpoint" and "/session-checkpoint" no longer trigger
  (they belong to the mid-session quick-save skill now).

BLOCKS (on PreToolUse)
  Bash, Write, Edit, TodoWrite. These are the tools the AI typically
  uses to execute the 9 checkpoint steps inline (git commit, file
  writes, progress tracking). Skill tool is deliberately NOT blocked
  so the AI can invoke end-session. Read/Grep/Glob not blocked
  (information-gathering is safe and needed to investigate state).

DOES NOT TRIGGER ON
  - Non-matched tools (Read, Grep, Glob, Skill, MCP tools, etc.)
  - Meta paths for Write/Edit: /.work-requests/, /.lifecycle-reviews/,
    /.routed-tasks/, /.claude/projects/*/memory/ (gap reports and
    auto-memory about end-of-session behavior must not deadlock)
  - Bash commands that are themselves the checkpoint completion
    (git commit, supabase-sync, etc.) still block -- the AI is
    expected to invoke the skill and let the skill drive the steps

BYPASS (any of these allows the operation)
  1. end-session skill invoked AFTER the most-recent end-session
     signal's timestamp (normal happy path).
  2. Fallback when timestamps are unparseable: ANY end-session
     invocation logged for today (graceful degradation, not strict).
  3. Recent user message contains one of:
        "skip end-session", "skip end session", "no end-session",
        "save progress quickly"
     The first three are the explicit standdown phrases for this
     gate. "save progress quickly" signals the user wants the
     mid-session session-checkpoint skill instead, NOT the full
     end-session ceremony, so this gate stands down.
  4. Current Write/Edit/TodoWrite content contains one of the same
     bypass phrases (for filing gap reports and documentation about
     this enforcer without deadlock -- mirrors the same pattern in
     brainstorming-enforcer and hook-development-enforcer).

  CLEANED 2026-05-12 (S45): removed legacy bypass phrases that referenced
  the old (now-renamed) skill name and confused the deny-message:
    - "skip session-checkpoint" (referenced the OTHER skill's name)
    - "skip checkpoint"          (ambiguous after rename)
    - "no session-checkpoint"    (same)
    - "no checkpoint"            (same)
    - "--mid"                    (legacy `session-checkpoint --mid` mode
                                  no longer exists post-rename)

GRACEFUL DEGRADATION
  - Missing skill log file -> ALLOW (no deadlock on missing tracker)
  - Missing transcript_path -> ALLOW (cannot detect signals without it)
  - Malformed timestamps on signal or log entry -> fall back to
    "invoked at all today" signal (bypass 2 above)
  - Any unhandled exception -> exit 0 (allow)

DESIGN TRADE-OFF (intentional false-negative bias)
  The hook's job is to catch the specific pattern "user signals end of
  session -> AI starts running git/write steps inline." It is NOT to
  police all checkpoint-adjacent activity. False positives deadlock the
  agent; false negatives just skip a single nudge. When in doubt, allow.

Tests: tests/test_end_session_enforcer.py in Skill Management Hub.

Pure stdlib. ASCII-only. Input/output: JSON via stdin/stdout.

# skip end-session -- self-modifying hook file, structural exemption.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"
# Post-rename 2026-05-11: `end-session` is the full 9-step end-of-session
# skill (renamed from session-checkpoint). `session-checkpoint` is now the
# mid-session quick-save skill (git + Supabase only). Invoking the
# mid-session skill does NOT satisfy this end-session gate.
SKILL_NAME = "end-session"

BYPASS_PHRASES = (
    "skip end-session",
    "skip end session",
    "no end-session",
    "save progress quickly",
)

# Silencer phrases (S50 fix, 2026-05-13). User saying any of these in a
# transcript message AFTER an end-session signal suppresses the gate until
# a fresh signal arrives (timestamp comparison handles re-arming). Designed
# from user direction "have a permanent line that says 'Still working on a
# project' or something. It would silence that until I actually say it again."
# The transcript IS the state -- no state file needed. # skip end-session
SILENCER_PHRASES = (
    "still working",
    "still going",
    "not ending",
    "not done yet",
    "ignore that",
)

# End-session signal patterns. Post-rename: bare "checkpoint" and
# "/session-checkpoint" no longer trigger (they belong to the mid-session
# skill now). "/end-session" added as the explicit invocation trigger.
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

# Descriptive-context markers (S50 fix, 2026-05-13). If a trigger pattern
# matches but is preceded by one of these markers within ~60 chars, treat
# as a descriptive reference (simile / past event / discussion / example /
# definition) rather than an imperative request. Source incident: user's
# architectural-discussion message "sort of like we did with the session
# checkpoint and end session may risk breaking something" repeatedly
# triggered the gate even though the user was describing past behavior,
# not requesting an end. # skip end-session
DESCRIPTIVE_MARKERS = re.compile(
    r"\b(?:"
    # Similes
    r"(?:sort|kind|just)\s+of\s+like|just\s+like"
    # Hypothetical / as-if
    r"|as\s+(?:if|though)"
    # Past-event references
    r"|remember(?:ed)?(?:\s+(?:when|how))?"
    r"|earlier|yesterday|previously|the\s+other\s+day"
    r"|we\s+(?:did|had|used\s+to)|that\s+happened"
    # Meta-discussion
    r"|talking\s+about|talked\s+about|discussing|discussion\s+of"
    r"|mention(?:ed|ing)?|referenc(?:ed|ing)?|discussed"
    # Examples
    r"|for\s+example|such\s+as|e\.g\.|i\.e\."
    # Names / definitions
    r"|called|named"
    r"|concept\s+of|idea\s+of|definition\s+of|the\s+term|the\s+phrase"
    # Past breakage
    r"|broke\s+(?:the|because|when)"
    r")\b",
    re.I,
)
# How many chars of context BEFORE a trigger match to scan for descriptive
# markers. 60 chars covers most natural-language simile and past-ref
# constructions without bleeding into the previous sentence's content.
DESCRIPTIVE_LOOKBEHIND = 60

# Meta paths: structurally exempt for Write/Edit (gap reports + memory).
META_PATH_MARKERS = (
    "/.work-requests/",
    "/.lifecycle-reviews/",
    "/.routed-tasks/",
    "/.claude/projects/",
    "/memory/feedback_",
)

# Skill content injection prefix. When the AI invokes `Skill end-session`,
# the harness loads the skill's SKILL.md content and injects it as a
# user-type text message starting with "Base directory for this skill:".
# That injection contains "End Session" (the skill heading) and
# "end-session" (the skill folder name), so the unfiltered signal scan
# would treat the injection itself as a fresh user signal -- landing
# milliseconds AFTER the invocation timestamp and creating an
# unbreakable feedback loop where each Skill invocation generates a
# fresh signal that the invocation cannot satisfy.
#
# Fixed 2026-05-12 (paired with the parse_iso_timestamp UTC normalization
# in the same session). Discovered when HQ refiled wr-hq-2026-05-12-003
# after the timezone fix shipped: the timezone math worked, but the
# signal-loop bug surfaced once the math stopped masking it.
#
# skip end-session
SKILL_INJECTION_PREFIX = "Base directory for this skill:"

# System-injected blocks stripped BEFORE signal matching, to avoid
# false positives where hook-injected reminders or system prompts
# contain "checkpoint" or "end session" as incidental keywords.
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

# How many recent user TEXT messages to scan for the signal. S50 fix
# (2026-05-13): tightened from 10 to 1 per user direction "it should also
# maybe just look at the previous message not ALL RECENT MESSAGES".
# Only counts user records with non-empty extracted text -- tool-result
# records (type=user, content=tool_result blocks) are skipped without
# depleting the budget, so the scan reliably reaches the user's most
# recent actual prompt. # skip end-session
TRANSCRIPT_USER_LOOKBACK = 1

# Matched tool names (PreToolUse fires on ALL tools; we filter in code
# rather than relying on settings.json matcher regex, so one code change
# propagates without settings edits).
BLOCKED_TOOLS = frozenset({"Bash", "Write", "Edit", "TodoWrite"})


def strip_system_blocks(text):
    """Remove system-injected tag blocks so their text is not scanned as user
    intent. Handles unclosed/nested tags gracefully (non-greedy match).
    """
    if not text:
        return ""
    try:
        return SYSTEM_BLOCK_RE.sub("", text)
    except Exception:
        return text


def parse_iso_timestamp(s):
    """Parse ISO-8601 timestamp. Return tz-aware UTC datetime, or None.

    FIXED 2026-05-12: handle the two-source timezone mismatch correctly.
      - Transcript user messages: UTC with 'Z' suffix
        (e.g., 2026-05-12T19:36:20.374Z)
      - skill-invocation-tracker.py: naive local time via
        datetime.now().isoformat() (e.g., 2026-05-12T15:37:00.123)

    The prior implementation stripped tz and compared as naive, which
    silently treated UTC-19:36 and local-15:37 as if both were in the
    same timezone -- producing inv_ts < signal_ts for every invocation
    made after the signal in any UTC-offset locale. End-session was
    permanently blocked outside UTC. Fix: normalize both to tz-aware
    UTC. Naive timestamps are assumed to be local time (Python's
    .astimezone() on a naive datetime treats it as local), aware
    timestamps are converted to UTC. Comparisons then compare real
    moments in time, not wall-clock strings.

    # skip end-session
    """
    if not s or not isinstance(s, str):
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        # Both branches yield tz-aware UTC. astimezone() on a naive
        # datetime treats it as local time before conversion.
        dt = dt.astimezone(timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def load_skill_log_records():
    """Return list of today's skill invocation records, or []."""
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
    """True if end-session skill was invoked after signal_ts.

    If signal_ts is None (signal detected but no parseable timestamp),
    fall back to "any invocation of end-session today" -- this
    biases toward allow (graceful degradation) rather than deadlock.
    """
    records = load_skill_log_records()
    if not records:
        return False
    for rec in records:
        skill = str(rec.get("skill", "")).lower()
        # Accept exact match OR namespaced (plugin:end-session)
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
    """Extract plain text from a transcript user message's content field.
    content may be a string or a list of content blocks.

    Skill-content-injection text blocks are EXCLUDED. When the AI invokes
    a Skill, the harness loads the skill's SKILL.md and injects it as a
    user-type text block beginning with "Base directory for this skill:".
    Without exclusion, invoking `Skill end-session` would itself create a
    fresh "end session" signal in the transcript (because the skill name
    appears in the injected markdown header), which arrives milliseconds
    after the invocation timestamp -- producing an unbreakable feedback
    loop. # skip end-session
    """
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
    """Yield (record, clean_text) for recent USER TEXT messages, newest first.

    Records with empty extracted text (i.e. tool-result-only user records)
    are SKIPPED without consuming a slot in the limit. This lets callers
    scan the user's actual recent prompt(s) even when many tool-result
    records sit between the AI's current tool call and the user's text.

    S50 fix (2026-05-13): factored out of find_most_recent_end_session so
    find_most_recent_silencer can share the same iteration semantics.
    # skip end-session
    """
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
            # tool-result-only or system-only record; skip without counting
            continue
        text_msgs_seen += 1
        yield (rec, clean)


def find_most_recent_end_session(transcript_path):
    """Scan transcript in reverse for an end-session signal.

    Returns (signal_ts, signal_found):
      signal_ts: datetime of the user message containing the signal, or None
        if the message had no parseable timestamp.
      signal_found: True if any of the last TRANSCRIPT_USER_LOOKBACK user
        TEXT messages contained an IMPERATIVE end-session match (descriptive
        references like similes / past references / meta-discussion do not
        count -- see _is_descriptive_reference).
    """
    for rec, clean in _iter_recent_user_text_messages(transcript_path, TRANSCRIPT_USER_LOOKBACK):
        if contains_end_session_signal(clean):
            ts = parse_iso_timestamp(rec.get("timestamp"))
            return (ts, True)
    return (None, False)


def find_most_recent_silencer(transcript_path):
    """Scan transcript in reverse for a silencer phrase ("still working",
    "not ending", etc.).

    Returns (silencer_ts, silencer_found). Mirror of find_most_recent_end_session.

    Silencer semantics (S50, 2026-05-13): if the user says a silencer phrase
    AFTER an end-session signal, the gate stands down -- the user has
    explicitly stated they are continuing the session. A fresh end-session
    signal AFTER the silencer re-arms the gate (timestamp comparison in
    main()). Scans a slightly wider window than end-session detection so a
    one-message-ago silencer still applies when the current most-recent user
    message contains an unrelated follow-up. # skip end-session
    """
    # Wider lookback than signal detection: silencer needs to persist across
    # one or two intervening turns, otherwise the silence is lost the moment
    # the user asks a follow-up question.
    for rec, clean in _iter_recent_user_text_messages(transcript_path, 3):
        low = clean.lower()
        if any(phrase in low for phrase in SILENCER_PHRASES):
            ts = parse_iso_timestamp(rec.get("timestamp"))
            return (ts, True)
    return (None, False)


def _is_descriptive_reference(text, match_pos):
    """Return True if a trigger match at match_pos is preceded by a
    descriptive marker (simile, past reference, discussion, example,
    definition) WITHIN THE CURRENT SENTENCE.

    The lookbehind window is bounded both by DESCRIPTIVE_LOOKBEHIND chars
    AND by the most-recent sentence-end punctuation (. ! ? newline). This
    prevents an earlier sentence's "discussed"/"like we"/etc. from poisoning
    an imperative match in a later sentence -- e.g. "we discussed end session
    protocols. now let's end the session" must still trigger on the second
    clause despite "discussed" in the first.

    Treating descriptive matches as non-imperative prevents false positives
    where the user discusses end-session concepts without requesting an end.
    # skip end-session
    """
    if not text or match_pos <= 0:
        return False
    start = max(0, match_pos - DESCRIPTIVE_LOOKBEHIND)
    window = text[start:match_pos]
    # Restrict to the current sentence: split on sentence-end punctuation
    # followed by whitespace, then keep the trailing fragment (the sentence
    # the match lives in). Also splits on bare newlines as paragraph breaks.
    parts = re.split(r"(?:[.!?]+\s+|\n+)", window)
    current_sentence = parts[-1] if parts else window
    return bool(DESCRIPTIVE_MARKERS.search(current_sentence))


def contains_end_session_signal(text):
    """Return True if text contains an imperative end-session signal.

    Iterates every pattern match in the text. A match is considered
    imperative unless it is preceded by a descriptive marker within
    DESCRIPTIVE_LOOKBEHIND chars (simile / past reference / meta-discussion
    / example / definition). At least one non-descriptive match is
    required to trigger.

    S50 (2026-05-13): upgraded from any-substring-wins to
    descriptive-aware scanning. # skip end-session
    """
    if not text:
        return False
    for pat in END_SESSION_PATTERNS:
        for m in pat.finditer(text):
            if not _is_descriptive_reference(text, m.start()):
                return True
    return False


def recent_user_messages_contain_bypass(transcript_path):
    """True if any of the most-recent user messages contains a bypass
    phrase. Separate pass from signal detection because bypass may
    appear in the SAME user message as the end-session signal (user
    says 'wrap up' -- 'save progress quickly').
    """
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
    """Return the textual content being written, for bypass-in-content check."""
    if not isinstance(tool_input, dict):
        return ""
    if tool_name == "Write":
        content = tool_input.get("content", "")
        return content if isinstance(content, str) else ""
    if tool_name == "Edit":
        # Both old_string and new_string may describe why the edit exists
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
    """Return True if content contains either a BYPASS phrase or a SILENCER phrase.

    S51 fix (2026-05-13): silencer phrases ("still working", "still going",
    "not ending", etc.) now ALSO act as in-content bypasses, so the AI can
    use natural language instead of the awkward "skip end-session" keyword
    when continuing work past a false-positive trigger. Per user direction:
    "did you also include a silencer phrase for the AI? For example, you
    can just say 'still working' or 'still going', not 'ending' or something
    like that, so it silences it." # skip end-session
    """
    if not content:
        return False
    low = content.lower()
    if any(phrase in low for phrase in BYPASS_PHRASES):
        return True
    if any(phrase in low for phrase in SILENCER_PHRASES):
        return True
    return False


def is_meta_path(file_path):
    """Meta-path exemption for Write/Edit gap reports and auto-memory."""
    if not file_path:
        return False
    norm = file_path.replace("\\", "/").lower()
    return any(marker in norm for marker in META_PATH_MARKERS)


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name not in BLOCKED_TOOLS:
        return 0  # Skill, Read, Grep, Glob, MCP, etc. pass through

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    # Meta-path exemption for Write/Edit targets
    if tool_name in ("Write", "Edit"):
        file_path = str(tool_input.get("file_path", "") or "")
        if is_meta_path(file_path):
            return 0

    # ---- Detect ----------------------------------------------------------
    transcript_path = data.get("transcript_path") or ""
    signal_ts, signal_found = find_most_recent_end_session(transcript_path)
    if not signal_found:
        return 0  # no end-session in recent user messages

    # ---- Bypass: silencer phrase in recent transcript -------------------
    # S50 fix (2026-05-13): if the user said a silencer phrase ("still
    # working", "not ending", etc.) with timestamp >= the signal, the
    # gate stands down. Same-timestamp (signal + silencer in same message)
    # also resolves to silencer-wins.
    silencer_ts, silencer_found = find_most_recent_silencer(transcript_path)
    if silencer_found:
        if signal_ts is None or silencer_ts is None:
            return 0  # graceful: missing timestamp, bias toward allow
        if silencer_ts >= signal_ts:
            return 0

    # ---- Bypass: skill already invoked AFTER the signal ------------------
    if checkpoint_invoked_after(signal_ts):
        return 0

    # ---- Bypass: phrase in recent user messages --------------------------
    if recent_user_messages_contain_bypass(transcript_path):
        return 0

    # ---- Bypass: phrase in current tool content --------------------------
    content = extract_write_content(tool_name, tool_input)
    if has_bypass_in_content(content):
        return 0

    # ---- Block -----------------------------------------------------------
    deny(
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
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
