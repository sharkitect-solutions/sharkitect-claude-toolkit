"""multi_file_build.py - Methodology dispatcher sub-rule.

Source: NEW (wr-sentinel-2026-05-04-009 first half).

Trigger: PreToolUse on Write|Edit. Track distinct file-type categories
written across the session in a state file. When the count of DISTINCT
categories crosses 5 (THRESHOLD) without superpowers:writing-plans /
writing-plans skill invoked, advisory nudge.

File-type categories tracked:
  - spec:   any path containing /specs/ (e.g. docs/superpowers/specs/*.md)
  - tool:   .py under /tools/ or /scripts/ (any depth)
  - bat:    .bat anywhere
  - vbs:    .vbs anywhere
  - doc:    .md under /docs/ (excluding /specs/) -- documentation files

Bypass:
  - Skill log (writing-plans / superpowers:writing-plans)
  - Transcript bypass phrase
  - intent_detection user-driven mode (NEW LAYER)

Debounce: nudge once per session (state.nudged flag).

Severity: ADVISORY (returns {"advisory": "<text>"})

Source incident: Sentinel session 2026-05-04 Goal Monitor build -- 7 files
across spec/tool/wrappers/registration/routed-task without writing-plans
skill invocation. Existing resource-audit-hook nudges fired 3x without
escalating to skill invocation; layer was too generic.

Per Hook Introduction Rule: advisory by default, not hard-deny.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_SCRIPTS_LIB = os.path.expanduser("~/.claude/scripts/_lib")
if _SCRIPTS_LIB not in sys.path:
    sys.path.insert(0, _SCRIPTS_LIB)
try:
    from intent_detection import is_user_driven  # type: ignore
except Exception:
    is_user_driven = None

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events
except Exception:
    _feedback_events = None


TMP_DIR = Path.home() / ".claude" / ".tmp"
STATE_FILE = TMP_DIR / "multi-file-build-state.json"
PREFERRED_SKILL = "superpowers:writing-plans"
FALLBACK_SKILL = "writing-plans"

THRESHOLD = 5  # distinct file-type categories before nudging

BYPASS_PHRASES = (
    "skip multi-file-build",
    "skip writing-plans",
    "skip plan-skill",
    "skip writing plans",
    "status update only",
)
TRANSCRIPT_USER_LOOKBACK = 3

# ---- Classification regexes ----
SPEC_PATH_RE = re.compile(r"[/\\]specs?[/\\]", re.I)
TOOL_PATH_RE = re.compile(r"[/\\](?:tools?|scripts?)[/\\][^/\\]*\.py$", re.I)
BAT_PATH_RE = re.compile(r"\.bat$", re.I)
VBS_PATH_RE = re.compile(r"\.vbs$", re.I)
DOC_PATH_RE = re.compile(r"[/\\]docs?[/\\].*\.md$", re.I)


def _classify(file_path):
    """Classify file_path into one of the tracked categories or None.

    Order matters: spec is checked before doc so /docs/.../specs/foo.md
    classifies as 'spec' (the more specific signal).
    """
    if not file_path:
        return None
    if SPEC_PATH_RE.search(file_path):
        return "spec"
    if TOOL_PATH_RE.search(file_path):
        return "tool"
    if BAT_PATH_RE.search(file_path):
        return "bat"
    if VBS_PATH_RE.search(file_path):
        return "vbs"
    if DOC_PATH_RE.search(file_path):
        return "doc"
    return None


def _load_skill_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return []


def _skill_invoked(name, log):
    target = name.lower()
    return any(
        e == target or e.endswith(":" + target) or e.startswith(target + ":")
        for e in log
    )


def _read_recent_user_messages(transcript_path):
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
                if rec.get("type") != "user":
                    continue
                msg = rec.get("message") or {}
                content = msg.get("content")
                if isinstance(content, str):
                    msgs.append(content)
                elif isinstance(content, list):
                    for blk in content:
                        if isinstance(blk, dict) and blk.get("type") == "text":
                            msgs.append(blk.get("text", ""))
        return msgs[-TRANSCRIPT_USER_LOOKBACK:]
    except Exception:
        return []


def _has_bypass_phrase(messages):
    for txt in messages:
        low = txt.lower()
        if any(phrase in low for phrase in BYPASS_PHRASES):
            return True
    return False


def _load_state():
    today = datetime.now().strftime("%Y-%m-%d")
    if not STATE_FILE.exists():
        return {"date": today, "categories": [], "nudged": False}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "categories": [], "nudged": False}
        # categories stored as list (sets aren't JSON-native)
        if not isinstance(s.get("categories"), list):
            s["categories"] = []
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "categories": [], "nudged": False}


def _save_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def evaluate(payload):
    """Evaluate multi_file_build sub-rule.

    Returns:
      None                       -> sub-rule did not trigger
      {"advisory": "<text>"}     -> ADVISORY soft nudge
    """
    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return None

    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")
    category = _classify(file_path)
    if category is None:
        return None

    # Update tracker FIRST so suppressed nudges still capture the breadth signal
    state = _load_state()
    if category not in state["categories"]:
        state["categories"].append(category)
    _save_state(state)

    # Below threshold: no further work
    if len(state["categories"]) < THRESHOLD:
        return None

    # Bypass: skill log
    log = _load_skill_log()
    if _skill_invoked(PREFERRED_SKILL, log) or _skill_invoked(FALLBACK_SKILL, log):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="multi_file_build",
                decision="pass_through", trigger="skill_log_bypass",
                payload=payload,
            )
        return None

    # Bypass: transcript phrase
    transcript_path = payload.get("transcript_path") or ""
    recent_msgs = _read_recent_user_messages(transcript_path)
    if _has_bypass_phrase(recent_msgs):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="multi_file_build",
                decision="pass_through", trigger="transcript_bypass_phrase",
                payload=payload,
            )
        return None

    # Bypass: intent_detection user-driven mode (NEW LAYER)
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=file_path,
                bypass_phrases=BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="multi_file_build",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    # Debounce: nudge once per session
    if state.get("nudged"):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="multi_file_build",
                decision="pass_through", trigger="debounced_already_nudged",
                payload=payload,
            )
        return None
    state["nudged"] = True
    _save_state(state)

    cats = ", ".join(sorted(state["categories"]))
    advisory_text = (
        f"MULTI-FILE BUILD DETECTED: {len(state['categories'])} distinct file-type "
        f"categories written this session ({cats}) without `superpowers:writing-plans`.\n\n"
        "Multi-file builds are exactly what writing-plans exists to scaffold. "
        "Without a plan, files drift out of sync and steps get forgotten. "
        "Invoke `Skill superpowers:writing-plans` (preferred) or `Skill writing-plans` "
        "before the next write to capture: phase ordering, per-file deliverables, "
        "rollback plan, and measurable done criteria.\n\n"
        'To suppress for the rest of the session, include "skip multi-file-build" '
        "or \"status update only\" in your next user message.\n\n"
        "Source: wr-sentinel-2026-05-04-009 (Goal Monitor build pattern)."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="multi_file_build",
            decision="advisory",
            trigger=f"distinct_categories:{len(state['categories'])}",
            payload=payload,
        )
    return {"advisory": advisory_text}
