"""
content-pitching-detector.py - PreToolUse ADVISORY hook for client-facing content pitches

Detects when the assistant has recently been pitching client-facing content
(tagline candidates, headlines, slogans, copy options, brand palette) WITHOUT
first invoking the content-enforcer skill. Emits a soft additionalContext
nudge on the next tool call so the AI can course-correct.

Why ADVISORY (not BLOCKING) per docs/hook-classification-policy.md:
  - Tagline/copy pitches are exploratory -- multiple candidates are the norm,
    blocking each would deadlock creative flow.
  - Pattern-based detection on assistant prose has medium-precision (numbered
    lists + keyword combo); false positives are more likely than BLOCKING
    hooks should allow.
  - Skipping the nudge is recoverable within the session.
  - Suffix `-detector.py` per policy naming convention for ADVISORY hooks.

Source: wr-2026-04-19 (workforce-hq, UNUSED) -- HQ pitched 4 tagline candidates
+ FF brand palette without invoking hq-content-enforcer. CLAUDE.md mandates
content-enforcer FIRST for anything clients, prospects, or public will see.

DETECTION
  Two-part combo signal on recent assistant messages (last 5) in transcript:
    (a) keyword present: tagline / headline / slogan / copy candidate /
        copy option / brand voice / brand color / brand palette / value prop
    (b) option-enumeration pattern: 2+ lines matching Option/Candidate/
        Variant/Slogan/Tagline/Pitch/Version labels, OR 3+ plain numbered
        list items.
  BOTH must be present in the same assistant message. Either alone is
  insufficient (numbered lists are common; "tagline" appears in discussion).

WORKSPACE SCOPE
  Only fires when cwd is the Workforce HQ workspace (client-facing content
  lives there). Other workspaces no-op.

SUPPRESSION
  - hq-content-enforcer OR content-enforcer invoked today (skill log check)
  - Already nudged this session (state debounce)

GRACEFUL DEGRADATION
  - Missing transcript -> no-op.
  - Missing skill log -> no-op (err toward no-nudge since ADVISORY
    false-positives erode trust).
  - Any exception -> exit 0 (allow).

Pure stdlib. ASCII-only. PreToolUse on Edit|Write|TodoWrite.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"
STATE_FILE = TMP_DIR / "content-pitching-detector-state.json"

HQ_MARKER = "SHARKITECT DIGITAL WORKFORCE HQ"

PREFERRED_SKILL = "hq-content-enforcer"
FALLBACK_SKILL = "content-enforcer"

ASSISTANT_LOOKBACK = 5

# Strip system-injected blocks BEFORE scanning. Fixes the class of bug from
# wr-2026-04-19 brainstorming-hook-false-positive.
SYSTEM_BLOCK_TAGS = (
    "system-reminder",
    "user-prompt-submit-hook",
    "command-message",
    "command-name",
    "command-args",
    "command-stdout",
    "command-stderr",
    "ide_selection",
    "local-command-stdout",
    "local-command-stderr",
)
SYSTEM_BLOCK_RE = re.compile(
    r"<(?:" + "|".join(SYSTEM_BLOCK_TAGS) + r")\b[^>]*>.*?</(?:"
    + "|".join(SYSTEM_BLOCK_TAGS) + r")\s*>",
    re.S | re.I,
)

# Keyword signal -- content types that require content-enforcer review.
CONTENT_KEYWORDS_RE = re.compile(
    r"\b(?:"
    r"tagline|headline|slogan|value\s+prop(?:osition)?|"
    r"brand\s+voice|brand\s+color[s]?|brand\s+palette|"
    r"copy\s+candidate[s]?|copy\s+option[s]?"
    r")\b",
    re.I,
)

# Option-enumeration signal -- must find 2+ matches in same message.
OPTION_LABEL_RE = re.compile(
    r"^\s*(?:Option|Candidate|Variant|Slogan|Tagline|Pitch|Version)\s*[A-Z0-9]+\s*[:.\)]",
    re.M,
)
NUMBERED_LIST_RE = re.compile(r"^\s*\d+\.\s+\S", re.M)


def is_hq_workspace():
    try:
        return HQ_MARKER in str(Path.cwd())
    except Exception:
        return False


def strip_system_blocks(text):
    if not text:
        return ""
    try:
        return SYSTEM_BLOCK_RE.sub("", text)
    except Exception:
        return text


def load_skill_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return None
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None


def skill_invoked(name, log):
    target = name.lower()
    return any(
        e == target or e.endswith(":" + target) or e.startswith(target + ":")
        for e in (log or [])
    )


def read_recent_assistant_messages(transcript_path):
    if not transcript_path:
        return []
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return []
        msgs = []
        with p.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if rec.get("type") != "assistant":
                    continue
                msg = rec.get("message") or {}
                content = msg.get("content")
                if isinstance(content, str):
                    msgs.append(content)
                elif isinstance(content, list):
                    for blk in content:
                        if isinstance(blk, dict) and blk.get("type") == "text":
                            msgs.append(blk.get("text", ""))
        return msgs[-ASSISTANT_LOOKBACK:]
    except Exception:
        return []


def has_pitching_pattern(messages):
    for raw in messages:
        txt = strip_system_blocks(raw)
        if not txt or not CONTENT_KEYWORDS_RE.search(txt):
            continue
        labeled = len(OPTION_LABEL_RE.findall(txt))
        numbered = len(NUMBERED_LIST_RE.findall(txt))
        if labeled >= 2 or numbered >= 3:
            return True
    return False


def load_state():
    if not STATE_FILE.exists():
        return {"date": datetime.now().strftime("%Y-%m-%d"), "nudged": False}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != datetime.now().strftime("%Y-%m-%d"):
            return {"date": datetime.now().strftime("%Y-%m-%d"), "nudged": False}
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": datetime.now().strftime("%Y-%m-%d"), "nudged": False}


def save_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def emit(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    }))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "TodoWrite"):
        return 0

    if not is_hq_workspace():
        return 0

    state = load_state()
    if state.get("nudged"):
        return 0

    log = load_skill_log()
    if log is not None:
        if skill_invoked(PREFERRED_SKILL, log) or skill_invoked(FALLBACK_SKILL, log):
            return 0

    transcript_path = data.get("transcript_path") or ""
    msgs = read_recent_assistant_messages(transcript_path)
    if not has_pitching_pattern(msgs):
        return 0

    state["nudged"] = True
    save_state(state)

    emit(
        "CONTENT PITCHING DETECTED: recent assistant message shows client-facing "
        "content candidates (tagline / headline / slogan / copy / brand palette) "
        "without prior invocation of `hq-content-enforcer`. HQ CLAUDE.md "
        "mandates content-enforcer FIRST for anything clients, prospects, or "
        "public will see -- it loads brand voice, tone rules, and banned-term "
        "list before pitching. Invoke `Skill hq-content-enforcer` before "
        "finalizing candidates. Source: wr-2026-04-19 content-enforcer-skipped. "
        "See docs/hook-classification-policy.md (ADVISORY tier -- nudge, not block)."
    )
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
