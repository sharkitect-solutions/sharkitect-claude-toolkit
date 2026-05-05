"""iterative_work.py - Methodology dispatcher sub-rule.

Source: iterative-work-nudge.py (PostToolUse advisory after 2+ consecutive
Bash errors without ralph-loop active).

Behavior preserved 1:1 from source:
  - Tracks consecutive Bash errors via state file (TRACKER_FILE)
  - Skill tool invocation matching "ralph" sets ralph_active=True and
    resets the counter
  - Bash with error pattern in tool_result -> increment counter
  - Bash without errors -> reset counter
  - Threshold: 2 consecutive errors with ralph_active=False -> ADVISORY
  - Non-Bash, non-Skill tools are ignored (no state change)

NEW LAYER: intent_detection user-driven mode -- if the user has explicitly
asked for manual iteration (e.g., "just keep retrying these tests"),
the advisory is suppressed even if 2+ errors occur.

Severity: ADVISORY (returns {"advisory": "<text>"})

Source incident: universal iterative work protocol -- without ralph-loop,
the AI typically stops after each failure instead of iterating until fixed.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

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


TRACKER_FILE = os.path.join(tempfile.gettempdir(), "claude_iterative_work_tracker.json")

ERROR_PATTERNS = [
    "error:",
    "Error:",
    "ERROR",
    "Traceback (most recent call last)",
    "SyntaxError",
    "TypeError",
    "NameError",
    "ImportError",
    "ModuleNotFoundError",
    "FileNotFoundError",
    "KeyError",
    "ValueError",
    "AttributeError",
    "FAIL",
    "FAILED",
    "Exit code",
    "command not found",
    "No such file or directory",
    "Permission denied",
    "Connection refused",
    "timeout",
    "status: error",
    "Build failed",
    "Compilation error",
    "npm ERR!",
    "assertion failed",
]

THRESHOLD = 2

BYPASS_PHRASES = (
    "skip ralph-loop",
    "skip iterative-work",
    "no ralph-loop",
    "no iterative-work nudge",
)
TRANSCRIPT_USER_LOOKBACK = 3


def _load_tracker():
    try:
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"consecutive_errors": 0, "ralph_active": False, "nudges": 0}


def _save_tracker(data):
    try:
        os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
        with open(TRACKER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        pass


def _has_error(result_text):
    if not result_text:
        return False
    lower = result_text.lower()
    for pattern in ERROR_PATTERNS:
        if pattern.lower() in lower:
            return True
    return False


def evaluate(payload):
    """Evaluate iterative_work sub-rule.

    Returns:
      None                       -> sub-rule did not trigger
      {"advisory": "<text>"}     -> ADVISORY soft nudge
    """
    tool_name = payload.get("tool_name", "")

    # Skill tool invoking ralph-* -> mark ralph_active, reset counter, no nudge
    if tool_name == "Skill":
        tool_input = payload.get("tool_input", {}) or {}
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except (json.JSONDecodeError, TypeError, ValueError):
                tool_input = {}
        skill = str(tool_input.get("skill", "") or "").lower()
        if "ralph" in skill:
            tracker = _load_tracker()
            tracker["ralph_active"] = True
            tracker["consecutive_errors"] = 0
            _save_tracker(tracker)
        return None

    # Only Bash from here on
    if tool_name != "Bash":
        return None

    tracker = _load_tracker()

    # If ralph-loop is already active, no nudge needed
    if tracker.get("ralph_active"):
        return None

    tool_result = payload.get("tool_result", "")
    result_str = str(tool_result) if tool_result else ""

    if _has_error(result_str):
        tracker["consecutive_errors"] = tracker.get("consecutive_errors", 0) + 1
    else:
        tracker["consecutive_errors"] = 0
        _save_tracker(tracker)
        return None

    _save_tracker(tracker)

    if tracker["consecutive_errors"] < THRESHOLD:
        return None

    # NEW LAYER: intent_detection user-driven mode bypass
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
                        cluster="methodology", sub_rule="iterative_work",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    tracker["nudges"] = tracker.get("nudges", 0) + 1
    _save_tracker(tracker)

    advisory_text = (
        f"ITERATIVE WORK DETECTED: {tracker['consecutive_errors']} "
        "consecutive Bash errors without ralph-loop active. Per universal "
        "protocol: invoke /ralph-loop NOW to handle build-test-fix cycles "
        "autonomously. Do not make another attempt without it. "
        "The user expects the system to iterate until fixed, "
        "not stop after each failure."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="iterative_work",
            decision="advisory",
            trigger=f"consecutive_errors:{tracker['consecutive_errors']}",
            payload=payload,
        )
    return {"advisory": advisory_text}
