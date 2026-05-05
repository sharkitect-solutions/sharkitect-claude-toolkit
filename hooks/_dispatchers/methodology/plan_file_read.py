"""plan_file_read.py - Methodology dispatcher sub-rule.

Source: NEW (wr-sentinel-2026-04-30-008). PreToolUse:Read advisory when
the agent reads a plan file that explicitly cites
`superpowers:executing-plans` as a REQUIRED SUB-SKILL.

Trigger:
  - tool_name == "Read"
  - file_path matches plan-file pattern:
      */docs/plans/*.md
      */.claude/plans/*.md
  - file's first 30 lines contain 'REQUIRED SUB-SKILL' OR
    'superpowers:executing-plans'

Bypasses (any one passes through):
  1. Skill log: executing-plans OR superpowers:executing-plans invoked
  2. Transcript bypass phrase
  3. Intent detection: user-driven mode (NEW layer)
  4. Per-file debounce: same plan-file path nudges only once per session

Severity: ADVISORY (returns {"advisory": "<text>"})

Source incident: Sentinel session 2026-04-30 read the Luminous Foundation
Bridge plan, started executing Phase 1, completed all 7 sub-steps but
never invoked superpowers:executing-plans. Plan-aware verification was
bypassed.
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
STATE_FILE = TMP_DIR / "plan-file-read-state.json"

PREFERRED_SKILL = "superpowers:executing-plans"
FALLBACK_SKILL = "executing-plans"

PLAN_PATH_RE = re.compile(
    r"(?:"
    r"[/\\]docs[/\\]plans[/\\][^/\\]+\.md$"
    r"|[/\\]\.claude[/\\]plans[/\\][^/\\]+\.md$"
    r")",
    re.I,
)

REQUIRED_SUB_SKILL_RE = re.compile(r"\bREQUIRED\s+SUB-SKILL\b", re.I)
EXECUTING_PLANS_REF_RE = re.compile(r"\bsuperpowers:executing-plans\b", re.I)

FIRST_LINES_WINDOW = 30

BYPASS_PHRASES = (
    "skip plan-file-read",
    "skip executing-plans",
    "skip plan-skill-nudge",
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


def _load_state():
    today = datetime.now().strftime("%Y-%m-%d")
    if not STATE_FILE.exists():
        return {"date": today, "nudged_files": []}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "nudged_files": []}
        if "nudged_files" not in s:
            s["nudged_files"] = []
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "nudged_files": []}


def _save_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def _read_plan_head(file_path, n_lines=FIRST_LINES_WINDOW):
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            head = []
            for i, line in enumerate(f):
                if i >= n_lines:
                    break
                head.append(line)
            return "".join(head)
    except (OSError, UnicodeDecodeError):
        return ""


def evaluate(payload):
    """Evaluate plan_file_read sub-rule.

    Returns:
      None                       -> sub-rule did not trigger
      {"advisory": "<text>"}     -> ADVISORY soft nudge
    """
    if payload.get("tool_name") != "Read":
        return None

    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")
    if not file_path or not PLAN_PATH_RE.search(file_path):
        return None

    head = _read_plan_head(file_path)
    if not head:
        return None

    if not (REQUIRED_SUB_SKILL_RE.search(head) or EXECUTING_PLANS_REF_RE.search(head)):
        return None

    # Bypass: skill log
    log = _load_skill_log()
    if _skill_invoked(PREFERRED_SKILL, log) or _skill_invoked(FALLBACK_SKILL, log):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="plan_file_read",
                decision="pass_through", trigger="skill_log_bypass",
                payload=payload,
            )
        return None

    # Bypass: intent_detection user-driven mode (NEW LAYER)
    transcript_path = payload.get("transcript_path") or ""
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=file_path,
                bypass_phrases=BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="plan_file_read",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    # Per-file debounce
    state = _load_state()
    norm_path = os.path.normcase(os.path.abspath(file_path))
    if norm_path in state.get("nudged_files", []):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="plan_file_read",
                decision="pass_through", trigger="debounced_per_file",
                payload=payload,
            )
        return None
    state.setdefault("nudged_files", []).append(norm_path)
    _save_state(state)

    advisory_text = (
        f"PLAN EXECUTION DETECTED. The plan file {os.path.basename(file_path)} "
        f"declares `{PREFERRED_SKILL}` as REQUIRED SUB-SKILL "
        "(or references it directly in the first lines). Invoke "
        f"`Skill {PREFERRED_SKILL}` (preferred) or `Skill {FALLBACK_SKILL}` "
        "before executing phase-by-phase work. The skill enforces phase "
        "exit-criteria gating, structured task progress tracking, and the "
        "skill's self-review checklist -- all of which are bypassed if you "
        "execute the plan inline.\n\n"
        'To suppress for this session, include "skip plan-file-read" or '
        '"skip executing-plans" in your next user message.\n\n'
        "Source: wr-sentinel-2026-04-30-008. Past incident: Sentinel session "
        "2026-04-30 read the Luminous Foundation Bridge plan, executed Phase "
        "1 inline, completed all 7 sub-steps without invoking the skill -- "
        "plan-aware verification (phase exit gating, structured progress) "
        "was bypassed."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="plan_file_read",
            decision="advisory", trigger=f"plan_path:{os.path.basename(file_path)}",
            payload=payload,
        )
    return {"advisory": advisory_text}
