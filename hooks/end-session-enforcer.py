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

# Meta paths: structurally exempt for Write/Edit (gap reports + memory).
META_PATH_MARKERS = (
    "/.work-requests/",
    "/.lifecycle-reviews/",
    "/.routed-tasks/",
    "/.claude/projects/",
    "/memory/feedback_",
)

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

# How many recent user messages to scan for the signal.
TRANSCRIPT_USER_LOOKBACK = 10

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
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "text":
                parts.append(str(blk.get("text", "")))
        return "\n".join(parts)
    return ""


def find_most_recent_end_session(transcript_path):
    """Scan transcript in reverse. Return (signal_ts, signal_found).

    signal_ts: datetime of the user message containing the signal,
      or None if the message had no parseable timestamp.
    signal_found: True if any of the last N user messages matched.
    """
    if not transcript_path:
        return (None, False)
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return (None, False)
        with p.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return (None, False)

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
        clean = strip_system_blocks(text)
        if contains_end_session_signal(clean):
            ts = parse_iso_timestamp(rec.get("timestamp"))
            return (ts, True)
    return (None, False)


def contains_end_session_signal(text):
    if not text:
        return False
    return any(pat.search(text) for pat in END_SESSION_PATTERNS)


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
    if not content:
        return False
    low = content.lower()
    return any(phrase in low for phrase in BYPASS_PHRASES)


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
