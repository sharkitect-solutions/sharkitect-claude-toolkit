"""
multistep-plan-nudge.py - PreToolUse soft nudge on TodoWrite for multistep work

Fires when TodoWrite is invoked with 5+ todos AND no prior writing-plans
skill invocation in this session AND the work appears to be multi-step
implementation (not just a checklist of small tasks).

Source: wr-2026-04-25 (HQ) process-writing-plans-skipped-multistep-autofix.
The autofix-completion scope was decomposed into 5+ todos via TodoWrite
without first invoking writing-plans -- so the work was tracked but lacked
explicit dependencies, autonomous-vs-blocked classification, and per-task
verification steps. Result: next session lacked a reviewable artifact and
re-derived the structure from conversation history.

WHEN IT FIRES
  TodoWrite tool invoked AND
  todos count >= 5 AND
  none of these skills invoked this session: writing-plans,
    superpowers:writing-plans

WHEN IT DOESN'T FIRE
  - Fewer than 5 todos (small checklist; TodoWrite is sufficient)
  - writing-plans / superpowers:writing-plans already invoked this session
  - Bypass phrase in recent user message
  - Already nudged in this session (debounced)

BYPASS (any one)
  1. Recent user message contains: "skip multistep-plan", "skip plan-nudge",
     "todos only", "no plan needed"
  2. writing-plans / superpowers:writing-plans already invoked
  3. Hook removed from settings.json

DESIGN -- soft nudge, not block
  TodoWrite is the right tool for many cases (single-conversation work,
  short batches). The nudge surfaces the option to capture the work as a
  plan for cross-session reviewability without forcing it. Block would
  generate friction for routine multistep work that doesn't need a formal
  plan.

  See universal-protocols.md Pre-Task Checklist for the TodoWrite-vs-
  writing-plans threshold:
    TodoWrite alone: single-conversation execution under 1 hour
    writing-plans:   multi-step work spanning > 1 hour OR cross-session
                     continuation OR work others will audit

Pure stdlib. ASCII-only output. Input/output via JSON on stdin/stdout.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path


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


def emit(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    }))


def load_skill_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError):
        return []


def skill_invoked(skill_name, log):
    target = skill_name.lower()
    for entry in log:
        if entry == target or entry.endswith(":" + target) or entry.startswith(target + ":"):
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
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def read_recent_user_messages(transcript_path):
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    try:
        with open(transcript_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return []
    msgs = []
    for raw in reversed(lines):
        if len(msgs) >= TRANSCRIPT_USER_LOOKBACK:
            break
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if rec.get("type") == "user":
            content = rec.get("message", {}).get("content", "")
            if isinstance(content, list):
                content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
            msgs.append(str(content).lower())
    return msgs


def has_bypass_phrase(msgs):
    for m in msgs:
        for phrase in BYPASS_PHRASES:
            if phrase in m:
                return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    if data.get("tool_name") != "TodoWrite":
        return 0

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    todos = tool_input.get("todos", [])
    if not isinstance(todos, list) or len(todos) < THRESHOLD_TODOS:
        return 0

    state = load_state()
    if state.get("nudged"):
        return 0  # already nudged this session

    log = load_skill_log()
    if skill_invoked(PREFERRED_SKILL, log) or skill_invoked(FALLBACK_SKILL, log):
        return 0  # plan skill already engaged

    transcript_path = data.get("transcript_path") or ""
    recent_msgs = read_recent_user_messages(transcript_path)
    if has_bypass_phrase(recent_msgs):
        return 0

    state["nudged"] = True
    save_state(state)

    # Compose the soft nudge
    todo_count = len(todos)
    msg = (
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
        "session continuity, the {todo_count}-item TodoWrite is fine -- "
        'continue. (To suppress this nudge for the rest of the session, '
        'include "todos only" or "skip multistep-plan" in your next user '
        "message.)\n\n"
        "Source: wr-2026-04-25 (HQ) process-writing-plans-skipped-multistep-autofix. "
        "Threshold: 5+ todos. Nudges once per session."
    )
    emit(msg)
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
