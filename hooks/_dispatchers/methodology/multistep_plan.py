"""multistep_plan.py - Methodology dispatcher sub-rule.

Source: multistep-plan-nudge.py (PreToolUse:TodoWrite advisory soft nudge
when TodoWrite is invoked with 5+ todos and no writing-plans skill
invoked this session).

Behavior preserved 1:1 from source:
  Trigger: tool_name == "TodoWrite" AND len(todos) >= 5 AND no
           writing-plans / superpowers:writing-plans skill invoked today

Bypasses (any one passes through):
  1. Skill log: writing-plans or superpowers:writing-plans invoked today
  2. Transcript bypass phrase: "skip multistep-plan", "skip plan-nudge",
     "skip multistep-nudge", "todos only", "no plan needed"
  3. Intent detection: user-driven mode via shared intent_detection.py
     (NEW layer added during consolidation)

Debounce: once per session (state file at ~/.claude/.tmp/<state-file>).

Severity: ADVISORY (returns {"advisory": "<text>"})

Source incident: wr-2026-04-25 (HQ) process-writing-plans-skipped-multistep-autofix.
"""
from __future__ import annotations

import json
import os
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
STATE_FILE = TMP_DIR / "multistep-plan-nudge-state.json"

THRESHOLD_TODOS = 5
PREFERRED_SKILL = "superpowers:writing-plans"
FALLBACK_SKILL = "writing-plans"

BYPASS_PHRASES = (
    "skip multistep-plan",
    "skip plan-nudge",
    "skip multistep-nudge",
    "todos only",
    "no plan needed",
)

TRANSCRIPT_USER_LOOKBACK = 3


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
        return {"date": today, "nudged": False}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "nudged": False}
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "nudged": False}


def _save_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def evaluate(payload):
    """Evaluate multistep_plan sub-rule.

    Returns:
      None                       -> sub-rule did not trigger
      {"advisory": "<text>"}     -> ADVISORY soft nudge
    """
    if payload.get("tool_name") != "TodoWrite":
        return None

    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    todos = tool_input.get("todos", [])
    if not isinstance(todos, list) or len(todos) < THRESHOLD_TODOS:
        return None

    # Bypass: skill log
    log = _load_skill_log()
    if _skill_invoked(PREFERRED_SKILL, log) or _skill_invoked(FALLBACK_SKILL, log):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="multistep_plan",
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
                cluster="methodology", sub_rule="multistep_plan",
                decision="pass_through", trigger="transcript_bypass_phrase",
                payload=payload,
            )
        return None

    # Bypass: intent_detection user-driven mode (NEW LAYER)
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=None,
                bypass_phrases=BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="multistep_plan",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    # Debounce: nudge once per session
    state = _load_state()
    if state.get("nudged"):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="multistep_plan",
                decision="pass_through", trigger="debounced_already_nudged",
                payload=payload,
            )
        return None
    state["nudged"] = True
    _save_state(state)

    todo_count = len(todos)
    advisory_text = (
        f"MULTISTEP WORK detected ({todo_count} todos via TodoWrite, no "
        "writing-plans invocation this session).\n\n"
        "TodoWrite tracks an in-session checklist; it does NOT capture (a) "
        "decomposed scope into discrete tasks with explicit dependencies, "
        "(b) autonomous-doable vs blocked classification, (c) per-task "
        "verification steps, (d) risk register or rollback strategy.\n\n"
        "If this work spans >1 hour, or will continue across sessions, or "
        "anyone else will need to audit/resume it -- invoke "
        "`superpowers:writing-plans` (preferred) or `writing-plans` to "
        "produce a reviewable plan artifact alongside the todos.\n\n"
        f"If this is a quick within-session checklist that won't need cross-"
        f"session continuity, the {todo_count}-item TodoWrite is fine -- "
        'continue. (To suppress this nudge for the rest of the session, '
        'include "todos only" or "skip multistep-plan" in your next user '
        "message.)\n\n"
        "Source: wr-2026-04-25 (HQ) process-writing-plans-skipped-multistep-autofix. "
        "Threshold: 5+ todos. Nudges once per session."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="multistep_plan",
            decision="advisory", trigger=f"todos:{todo_count}",
            payload=payload,
        )
    return {"advisory": advisory_text}
