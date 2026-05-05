"""process_violation.py - Methodology dispatcher sub-rule.

Source: process-violation-detector.py (UserPromptSubmit advisory nudge
when the user signals process-violation language).

Behavior preserved 1:1 from source:
  Trigger patterns (case-insensitive in the user prompt):
    - "we are skipping steps" / "we're skipping steps"
    - "we are jumping the gun" / "we're jumping the gun"
    - "this goes against our foundations" / "against the foundations"
    - "violates [our/the] X principle/protocol/foundation/rule"
    - "how are we already X when we are still Y" (structural-mismatch)

  Per-pattern debounce: each pattern key is recorded once per session;
  subsequent prompts hitting the SAME pattern do not re-nudge, but a NEW
  pattern still nudges.

Bypasses (any one passes through):
  1. Skill log: systematic-debugging OR superpowers:systematic-debugging
     invoked today
  2. Phrase "skip systematic-debugging" present in the same prompt
  3. (no transcript / intent_detection layer here -- prompt IS the user
     speaking; intent_detection's transcript-based check would be
     redundant or self-referential)

Severity: ADVISORY (returns {"advisory": "<text>"})

Different payload shape: reads `prompt` or `user_prompt` field (matcher
is UserPromptSubmit, not PreToolUse).

Source incident: wr-hq-2026-05-01-001 (HQ filed after 14h FF
Hibu-replacement session where Chris pushed back on a diagnostic-vs-
prescription violation and systematic-debugging was skipped).
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events
except Exception:
    _feedback_events = None


TMP_DIR = Path.home() / ".claude" / ".tmp"
STATE_FILE = TMP_DIR / "process-violation-detector-state.json"

SYSTEMATIC_DEBUGGING_SKILL = "systematic-debugging"
SUPERPOWERS_SYSTEMATIC_DEBUGGING_SKILL = "superpowers:systematic-debugging"

BYPASS_PHRASE = "skip systematic-debugging"

TRIGGER_PATTERNS = [
    (
        re.compile(r"\bwe(?:'re|\s+are)\s+skipping\s+steps\b", re.IGNORECASE),
        "skipping-steps",
    ),
    (
        re.compile(r"\bwe(?:'re|\s+are)\s+jumping\s+the\s+gun\b", re.IGNORECASE),
        "jumping-gun",
    ),
    (
        re.compile(r"\bagainst\s+(?:our|the|my)\s+foundations?\b", re.IGNORECASE),
        "against-foundations",
    ),
    (
        re.compile(
            r"\bviolat(?:es|ed|ing)\s+(?:our|the|my|a|an|this)?\s*[\w\s\-]{0,40}?"
            r"(?:principle|protocol|foundation|discipline|methodology|rule|standard)\b",
            re.IGNORECASE,
        ),
        "violates-principle",
    ),
    (
        re.compile(
            r"\bhow\s+are\s+we\s+already\s+\w+.{0,80}?when\s+we(?:'re|\s+are)\s+still\s+\w+",
            re.IGNORECASE | re.DOTALL,
        ),
        "already-still-mismatch",
    ),
]


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
        return {"date": today, "nudged": []}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "nudged": []}
        if "nudged" not in s:
            s["nudged"] = []
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "nudged": []}


def _save_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def _build_advisory(matched_keys):
    matched_summary = ", ".join(matched_keys)
    return (
        "PROCESS VIOLATION LANGUAGE detected in user prompt "
        f"(pattern{'s' if len(matched_keys) > 1 else ''}: {matched_summary}).\n\n"
        "The user is signaling that the current trajectory has SKIPPED a "
        "process step, JUMPED ahead of a diagnosis, or VIOLATED a stated "
        "discipline. This is the canonical moment to STOP and invoke "
        "`superpowers:systematic-debugging` BEFORE generating any diagnosis "
        "or remediation plan.\n\n"
        "Run `Skill superpowers:systematic-debugging` BEFORE producing the "
        "next response. The skill enforces: gather evidence first, "
        "enumerate hypotheses with explicit falsification tests, test "
        "cheapest first, document what was ruled out. Without it, the "
        "reset response anchors on the first plausible-sounding cause -- "
        "which often happens to be right (today's outcome) but the audit "
        "trail is thin and the pattern is not reproducible for next time.\n\n"
        "Universal Protocols Investigation Protocol (NON-NEGOTIABLE): "
        "'When investigating bugs, unexpected behavior, system failures, "
        "recurring issues, or any situation requiring a hypothesis-test "
        "cycle -- INVOKE superpowers:systematic-debugging BEFORE generating "
        "hypotheses.' Source: wr-hq-2026-05-01-001 (FF Hibu-replacement "
        "session, 14h, diagnostic-vs-prescription violation flagged by user).\n\n"
        "Bypass: include 'skip systematic-debugging' in your next user "
        "message if the skill genuinely does not apply (e.g., user wants a "
        "stylistic rewrite, not a process-debugging response)."
    )


def evaluate(payload):
    """Evaluate process_violation sub-rule.

    Returns:
      None                       -> sub-rule did not trigger
      {"advisory": "<text>"}     -> ADVISORY soft nudge
    """
    prompt = str(payload.get("prompt") or payload.get("user_prompt") or "")
    if not prompt.strip():
        return None

    # Bypass phrase short-circuit
    if BYPASS_PHRASE in prompt.lower():
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="process_violation",
                decision="pass_through", trigger="bypass_phrase_in_prompt",
                payload=payload,
            )
        return None

    # Skill-already-invoked short-circuit
    log = _load_skill_log()
    if (_skill_invoked(SYSTEMATIC_DEBUGGING_SKILL, log)
            or _skill_invoked(SUPERPOWERS_SYSTEMATIC_DEBUGGING_SKILL, log)):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="process_violation",
                decision="pass_through", trigger="skill_log_bypass",
                payload=payload,
            )
        return None

    # Match patterns; honor per-pattern debounce
    state = _load_state()
    matched_keys = []
    for pattern, key_suffix in TRIGGER_PATTERNS:
        if pattern.search(prompt):
            full_key = f"process-violation:{key_suffix}"
            if full_key not in state.get("nudged", []):
                matched_keys.append(key_suffix)
                state.setdefault("nudged", []).append(full_key)

    if not matched_keys:
        return None

    _save_state(state)

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="process_violation",
            decision="advisory", trigger=f"patterns:{','.join(matched_keys)}",
            payload=payload,
        )
    return {"advisory": _build_advisory(matched_keys)}
