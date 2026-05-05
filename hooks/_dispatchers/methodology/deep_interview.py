"""deep_interview.py - Methodology dispatcher sub-rule.

Source: deep-interview-gate.py (PreToolUse:Skill advisory soft nudge when
a planning/design skill is invoked without /deep-interview having run).

Behavior preserved 1:1 from source:
  Trigger: tool_name == "Skill" AND tool_input.skill in PLANNING_SKILLS
  PLANNING_SKILLS: brainstorming, superpowers:brainstorming, writing-plans,
  superpowers:writing-plans, app-builder, senior-architect, project-lifecycle

Bypasses (any one passes through):
  1. INTERVIEW_STATE file exists (deep-interview already ran in cwd)
  2. SKIP_TRACKER file exists (already nudged this session, debounced)
  3. Intent detection: user-driven mode via shared intent_detection.py
     (NEW layer added during consolidation)

Debounce: SKIP_TRACKER is set on first nudge so subsequent planning-skill
invocations in the same session don't re-nag.

Severity: ADVISORY (returns {"advisory": "<text>"})

Source incident: requirements clarification is universal -- planning skills
without clear requirements produce wrong-thing builds.
"""
from __future__ import annotations

import json
import os
import sys

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


PLANNING_SKILLS = [
    "brainstorming",
    "superpowers:brainstorming",
    "writing-plans",
    "superpowers:writing-plans",
    "app-builder",
    "senior-architect",
    "project-lifecycle",
]

INTERVIEW_STATE = os.path.join(os.getcwd(), ".tmp", "deep-interview-state.json")
SKIP_TRACKER = os.path.join(
    os.environ.get("TEMP", os.environ.get("TMP", "/tmp")),
    "claude_deep_interview_skip.json",
)

BYPASS_PHRASES = (
    "skip deep-interview",
    "skip interview-gate",
    "no deep-interview needed",
)
TRANSCRIPT_USER_LOOKBACK = 3


def _interview_ran():
    return os.path.isfile(INTERVIEW_STATE)


def _already_skipped():
    if not os.path.isfile(SKIP_TRACKER):
        return False
    try:
        with open(SKIP_TRACKER, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("skipped", False)
    except (json.JSONDecodeError, OSError):
        return False


def _mark_skipped():
    try:
        os.makedirs(os.path.dirname(SKIP_TRACKER), exist_ok=True)
        with open(SKIP_TRACKER, "w", encoding="utf-8") as f:
            json.dump({"skipped": True}, f)
    except OSError:
        pass


def evaluate(payload):
    """Evaluate deep_interview sub-rule.

    Returns:
      None                       -> sub-rule did not trigger
      {"advisory": "<text>"}     -> ADVISORY soft nudge
    """
    if payload.get("tool_name") != "Skill":
        return None

    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    skill_name = str(tool_input.get("skill", "") or "")

    is_planning = False
    for ps in PLANNING_SKILLS:
        if skill_name == ps or skill_name.endswith(":" + ps):
            is_planning = True
            break
    if not is_planning:
        return None

    # Bypass: deep-interview already ran
    if _interview_ran():
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="deep_interview",
                decision="pass_through", trigger="interview_state_exists",
                payload=payload,
            )
        return None

    # Debounce: already skipped this session
    if _already_skipped():
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="deep_interview",
                decision="pass_through", trigger="skip_tracker_set",
                payload=payload,
            )
        return None

    # Bypass: intent_detection user-driven mode (NEW LAYER)
    transcript_path = payload.get("transcript_path") or ""
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=None,
                bypass_phrases=BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="deep_interview",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    # Mark skipped so subsequent planning-skill invocations in this session
    # don't re-nag
    _mark_skipped()

    advisory_text = (
        "REQUIREMENTS CHECK: /deep-interview has NOT run this session. "
        f"You are about to invoke '{skill_name}' which is a planning/design skill. "
        "If the user's request is vague or underspecified (missing scope, constraints, "
        "success criteria, or edge cases), consider running /deep-interview first to "
        "clarify requirements. This prevents building the wrong thing. "
        "If requirements are already clear and specific, proceed -- this is a reminder, "
        "not a block."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="deep_interview",
            decision="advisory", trigger=f"planning_skill:{skill_name}",
            payload=payload,
        )
    return {"advisory": advisory_text}
