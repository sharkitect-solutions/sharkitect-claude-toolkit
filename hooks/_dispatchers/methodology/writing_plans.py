"""writing_plans.py - Methodology dispatcher sub-rule.

Source: writing-plans-enforcer.py (HARD GATE on multi-section plan body
writes without superpowers:writing-plans invoked).

Behavior preserved 1:1 from source:
  - Path: **/plan.md, **/plans/*.md, **/projects/X/plan*.md
  - Content threshold:
      Write: >= 200 chars (smaller writes are scaffolds)
      Edit:  new_string >= 50 lines OR contains plan-structural keyword
             (## Phase / ## Thread / ## Milestone / Success criteria /
             Risk register / Dependencies:)
  - Bypass: skill log (writing-plans / superpowers:writing-plans),
    transcript phrase, intent_detection user-driven mode (NEW)
  - HARD GATE: returns {"decision": "deny", "reason": ...}
  - Triggers on Write AND Edit (unlike brainstorming, which is Write-only)

Source incident: wr-2026-04-18.
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
PREFERRED_SKILL = "superpowers:writing-plans"
FALLBACK_SKILL = "writing-plans"

BYPASS_PHRASES = (
    "skip writing-plans",
    "skip plan-skill",
    "skip writing plans",
    "status update only",
    "skip writing-plans-enforcer",
)

PLAN_PATH_RE = re.compile(
    r"(?:"
    r"[/\\]plan\.md$"
    r"|[/\\]plans?[/\\][^/\\]+\.md$"
    r"|[/\\]projects[/\\][^/\\]+[/\\]plan[^/\\]*\.md$"
    r")",
    re.I,
)

PLAN_STRUCTURAL_RES = [
    re.compile(r"##\s+Phase\b", re.I),
    re.compile(r"##\s+Thread\b", re.I),
    re.compile(r"##\s+Milestone\b", re.I),
    re.compile(r"\bSuccess\s+criteria\b", re.I),
    re.compile(r"\bRisk\s+register\b", re.I),
    re.compile(r"\bDependencies\s*:", re.I),
]

WRITE_MIN_CHARS = 200
EDIT_MIN_LINES = 50
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


def _has_plan_structural_keyword(text):
    if not text:
        return False
    snippet = text[:8000]
    for pat in PLAN_STRUCTURAL_RES:
        if pat.search(snippet):
            return True
    return False


def _is_real_plan_write(tool_name, content):
    if tool_name == "Write":
        if not content or len(content) < WRITE_MIN_CHARS:
            return False
        return True
    if tool_name == "Edit":
        if not content:
            return False
        line_count = content.count("\n") + 1
        if line_count >= EDIT_MIN_LINES:
            return True
        if _has_plan_structural_keyword(content):
            return True
        return False
    return False


def evaluate(payload):
    """Evaluate writing_plans sub-rule.

    Returns:
      None                                  -> sub-rule did not trigger
      {"decision": "deny", "reason": "..."} -> HARD GATE
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
    if not file_path or not PLAN_PATH_RE.search(file_path):
        return None

    if tool_name == "Write":
        content = str(tool_input.get("content", "") or "")
    else:
        content = str(tool_input.get("new_string", "") or "")

    if not _is_real_plan_write(tool_name, content):
        return None

    log = _load_skill_log()
    if _skill_invoked(PREFERRED_SKILL, log) or _skill_invoked(FALLBACK_SKILL, log):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="writing_plans",
                decision="pass_through", trigger="skill_log_bypass",
                payload=payload,
            )
        return None

    transcript_path = payload.get("transcript_path") or ""
    recent_msgs = _read_recent_user_messages(transcript_path)
    if _has_bypass_phrase(recent_msgs):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="writing_plans",
                decision="pass_through", trigger="transcript_bypass_phrase",
                payload=payload,
            )
        return None

    # NEW LAYER: intent_detection user-driven bypass
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=file_path,
                bypass_phrases=BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="writing_plans",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    reason = (
        "BLOCKING: Writing a multi-section plan document ("
        + os.path.basename(file_path) + "). The writing-plans skill MUST be "
        "invoked before drafting -- it enforces risk register, rollback plan, "
        "measurable per-thread done criteria, and review cadence. Run "
        "`Skill superpowers:writing-plans` (preferred) or `Skill writing-plans`. "
        'To bypass for incremental status updates, include "status update only" '
        "in your message and retry. Source: wr-2026-04-18. "
        "See docs/hook-classification-policy.md."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="writing_plans",
            decision="hard_deny",
            trigger=f"plan_write:{tool_name}:{os.path.basename(file_path)}",
            payload=payload,
        )
    return {"decision": "deny", "reason": reason}
