"""content_pitching.py - Content-governance dispatcher sub-rule.

Source: ~/.claude/hooks/content-pitching-detector.py (263 LOC). Lift
preserves 1:1 behavior: HQ-workspace-only advisory nudge when recent
assistant messages show client-facing-content pitching patterns AND no
content-enforcer skill was invoked AND the session hasn't already been
nudged.

Detection (preserved):
  Two-part combo signal on the last 5 assistant messages:
    (a) content keyword present (tagline / headline / slogan /
        copy candidate / copy option / brand voice / brand color /
        brand palette / value prop)
    (b) option-enumeration pattern: 2+ Option/Candidate/Variant/Slogan/
        Tagline/Pitch/Version labels OR 3+ plain numbered list items
  BOTH must be present in the same assistant message.

Workspace scope: only fires when cwd contains the HQ_MARKER substring.

Suppression:
  - hq-content-enforcer OR content-enforcer in today's skill log
  - state file shows nudged=True for today (one-fire-per-session)
  - assistant message wraps the pattern inside a <system-reminder>-class
    block (system blocks stripped before scan)

Severity: ADVISORY (returns {"advisory": "<text>"}).

Source incident: wr-2026-04-19 (HQ pitched 4 tagline candidates + brand
palette without invoking hq-content-enforcer).
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Add hooks/ for _dispatchers package
_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events  # type: ignore
    from _dispatchers import _signal_extract  # type: ignore
except Exception:
    _feedback_events = None
    _signal_extract = None


HQ_MARKER = "SHARKITECT DIGITAL WORKFORCE HQ"
PREFERRED_SKILL = "hq-content-enforcer"
FALLBACK_SKILL = "content-enforcer"

ASSISTANT_LOOKBACK = 5

# System-block stripping (preserved verbatim from source lines 70-86)
_SYSTEM_BLOCK_TAGS = (
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
_SYSTEM_BLOCK_RE = re.compile(
    r"<(?:" + "|".join(_SYSTEM_BLOCK_TAGS) + r")\b[^>]*>.*?</(?:"
    + "|".join(_SYSTEM_BLOCK_TAGS) + r")\s*>",
    re.S | re.I,
)

# Content keyword signal (preserved from source lines 89-96)
_CONTENT_KEYWORDS_RE = re.compile(
    r"\b(?:"
    r"tagline|headline|slogan|value\s+prop(?:osition)?|"
    r"brand\s+voice|brand\s+color[s]?|brand\s+palette|"
    r"copy\s+candidate[s]?|copy\s+option[s]?"
    r")\b",
    re.I,
)

_OPTION_LABEL_RE = re.compile(
    r"^\s*(?:Option|Candidate|Variant|Slogan|Tagline|Pitch|Version)\s*[A-Z0-9]+\s*[:.\)]",
    re.M,
)
_NUMBERED_LIST_RE = re.compile(r"^\s*\d+\.\s+\S", re.M)


_ADVISORY_TEXT = (
    "CONTENT PITCHING DETECTED: recent assistant message shows client-facing "
    "content candidates (tagline / headline / slogan / copy / brand palette) "
    "without prior invocation of `hq-content-enforcer`. HQ CLAUDE.md "
    "mandates content-enforcer FIRST for anything clients, prospects, or "
    "public will see -- it loads brand voice, tone rules, and banned-term "
    "list before pitching. Invoke `Skill hq-content-enforcer` before "
    "finalizing candidates. Source: wr-2026-04-19 content-enforcer-skipped. "
    "See docs/hook-classification-policy.md (ADVISORY tier -- nudge, not block)."
)


def _is_hq_workspace():
    """True when cwd contains the HQ_MARKER substring (preserved from source)."""
    try:
        return HQ_MARKER in str(Path.cwd())
    except Exception:
        return False


def _strip_system_blocks(text):
    if not text:
        return ""
    try:
        return _SYSTEM_BLOCK_RE.sub("", text)
    except Exception:
        return text


def _load_skill_log():
    """Return list of lowercased skill names invoked today (None on missing).
    Note: source returns None on missing log so caller can distinguish
    'no log' from 'log exists but skill not invoked'. Preserve that contract."""
    if _signal_extract is not None:
        try:
            # _signal_extract.load_skill_log_today returns [] on missing.
            # Convert to None when no log file exists today to match source.
            today = datetime.now().strftime("%Y-%m-%d")
            log_path = Path.home() / ".claude" / ".tmp" / f"skill-invocations-{today}.json"
            if not log_path.exists():
                return None
            return _signal_extract.load_skill_log_today()
        except Exception:
            return None
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = Path.home() / ".claude" / ".tmp" / f"skill-invocations-{today}.json"
        if not log_path.exists():
            return None
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None


def _skill_invoked(name, log):
    target = name.lower()
    return any(
        e == target or e.endswith(":" + target) or e.startswith(target + ":")
        for e in (log or [])
    )


def _read_recent_assistant_messages(transcript_path):
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


def _has_pitching_pattern(messages):
    for raw in messages:
        txt = _strip_system_blocks(raw)
        if not txt or not _CONTENT_KEYWORDS_RE.search(txt):
            continue
        labeled = len(_OPTION_LABEL_RE.findall(txt))
        numbered = len(_NUMBERED_LIST_RE.findall(txt))
        if labeled >= 2 or numbered >= 3:
            return True
    return False


def _state_file():
    return Path.home() / ".claude" / ".tmp" / "content-pitching-detector-state.json"


def _load_state():
    sf = _state_file()
    today = datetime.now().strftime("%Y-%m-%d")
    if not sf.exists():
        return {"date": today, "nudged": False}
    try:
        s = json.loads(sf.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "nudged": False}
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "nudged": False}


def _save_state(state):
    sf = _state_file()
    try:
        sf.parent.mkdir(parents=True, exist_ok=True)
        sf.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def evaluate(payload):
    """Sub-rule entry point. Returns:
      None                       -> no contribution
      {"advisory": "<text>"}     -> advisory nudge
    Never raises."""
    try:
        if not isinstance(payload, dict):
            return None

        # Extract signals
        if _signal_extract is not None:
            signals = _signal_extract.extract(payload)
            tool_name = signals["tool_name"]
            transcript_path = signals["transcript_path"]
        else:
            tool_name = str(payload.get("tool_name", "") or "")
            transcript_path = str(payload.get("transcript_path", "") or "")

        # Tool filter
        if tool_name not in ("Edit", "Write", "TodoWrite"):
            return None

        # Workspace scope
        if not _is_hq_workspace():
            return None

        # State debounce
        state = _load_state()
        if state.get("nudged"):
            return None

        # Skill log bypass
        log = _load_skill_log()
        if log is not None:
            if _skill_invoked(PREFERRED_SKILL, log) or _skill_invoked(FALLBACK_SKILL, log):
                return None

        # Pitching pattern detection
        msgs = _read_recent_assistant_messages(transcript_path)
        if not _has_pitching_pattern(msgs):
            return None

        # Fire + persist state
        state["nudged"] = True
        _save_state(state)

        if _feedback_events is not None:
            try:
                _feedback_events.record(
                    cluster="content_governance",
                    sub_rule="content_pitching",
                    decision="advisory",
                    trigger="pitching_pattern_in_assistant_messages",
                    payload=payload,
                    tags={"workspace": "workforce-hq", "tool_name": tool_name},
                )
            except Exception:
                pass

        return {"advisory": _ADVISORY_TEXT}
    except Exception:
        return None
