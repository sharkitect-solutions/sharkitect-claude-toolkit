"""
process-violation-detector.py - UserPromptSubmit advisory nudge for
process-violation language.

Sibling to methodology-nudge.py. Where methodology-nudge fires on
PreToolUse:Edit|Write|Bash and detects code-iteration / investigation
patterns, this hook fires on UserPromptSubmit and detects PROCESS-violation
language in the user's prompt -- the signature of a moment where the AI
needs to stop, invoke superpowers:systematic-debugging, and run a structured
hypothesis-test cycle BEFORE generating a diagnosis.

Trigger patterns (case-insensitive, in user prompt text):
  - "we are skipping steps" / "we're skipping steps"
  - "we are jumping the gun" / "we're jumping the gun"
  - "this goes against our foundations" / "against the foundations"
  - "how are we already X when we are still Y" / "...we're still..."
  - "this violates" + (principle | protocol | foundation | rule)
    -- but only when paired with a process discipline word

Suppression:
  - systematic-debugging (or superpowers:systematic-debugging) already
    invoked this session -> no nudge
  - Bypass phrase "skip systematic-debugging" in same prompt -> no nudge
  - Same pattern key already nudged this session -> no nudge (debounced)

Output: advisory `additionalContext` via UserPromptSubmit hookSpecificOutput.
Non-blocking. Pure stdlib. Exit 0 always.

Source: wr-hq-2026-05-01-001 (HQ filed after 14h FF Hibu-replacement session
where Chris pushed back on a diagnostic-vs-prescription violation and
systematic-debugging was skipped during the reset analysis).

Hook budget note: this hook adds +1 to UserPromptSubmit matcher (currently
2 hooks: cron-context-enforcer, cron-activity-surfacer). When wr-002 router
consolidation ships, this logic is intended to absorb into
methodology-router.py as a UserPromptSubmit sub-route (alongside the
PostToolUse code-iteration sub-route from methodology-nudge.py).
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"
STATE_FILE = TMP_DIR / "process-violation-detector-state.json"

SYSTEMATIC_DEBUGGING_SKILL = "systematic-debugging"
SUPERPOWERS_SYSTEMATIC_DEBUGGING_SKILL = "superpowers:systematic-debugging"

# Bypass phrase: when present in the same user prompt, hook stays silent.
BYPASS_PHRASE = "skip systematic-debugging"

# ---- Trigger patterns ------------------------------------------------------
# Each pattern has: (compiled regex, key suffix used in debounce state)
# Patterns are case-insensitive. Word boundaries used where needed to avoid
# substring false positives.

TRIGGER_PATTERNS = [
    # "we are skipping steps" / "we're skipping steps"
    (
        re.compile(r"\bwe(?:'re|\s+are)\s+skipping\s+steps\b", re.IGNORECASE),
        "skipping-steps",
    ),
    # "we are jumping the gun" / "we're jumping the gun"
    (
        re.compile(r"\bwe(?:'re|\s+are)\s+jumping\s+the\s+gun\b", re.IGNORECASE),
        "jumping-gun",
    ),
    # "this goes against our foundations" / "against the foundations"
    (
        re.compile(r"\bagainst\s+(?:our|the|my)\s+foundations?\b", re.IGNORECASE),
        "against-foundations",
    ),
    # "this violates [our/the] X principle/protocol/foundation/rule"
    # Pairing 'violates' with a process-discipline noun keeps the trigger
    # specific. Bare 'violates' would over-match (syntax violations, etc.).
    (
        re.compile(
            r"\bviolat(?:es|ed|ing)\s+(?:our|the|my|a|an|this)?\s*[\w\s\-]{0,40}?"
            r"(?:principle|protocol|foundation|discipline|methodology|rule|standard)\b",
            re.IGNORECASE,
        ),
        "violates-principle",
    ),
    # "how are we already X when we are still Y" / "...we're still..."
    # Catches the structural-mismatch question Chris asked during the FF
    # session: "how are we already prescribing when we're still diagnosing?"
    (
        re.compile(
            r"\bhow\s+are\s+we\s+already\s+\w+.{0,80}?when\s+we(?:'re|\s+are)\s+still\s+\w+",
            re.IGNORECASE | re.DOTALL,
        ),
        "already-still-mismatch",
    ),
]


def load_skill_log():
    """Return list of skill names invoked today (lowercased)."""
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
    """Match handles namespaced (plugin:skill) form."""
    target = skill_name.lower()
    for entry in log:
        if entry == target or entry.endswith(":" + target) or entry.startswith(target + ":"):
            return True
    return False


def load_state():
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


def save_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def already_nudged(state, key):
    return key in state.get("nudged", [])


def mark_nudged(state, key):
    state.setdefault("nudged", []).append(key)


def emit(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": text,
        }
    }))


def build_nudge_text(matched_keys):
    """Return the advisory nudge text shown to the AI."""
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


def main():
    # Read stdin; on any error, exit 0 silently (never block prompts).
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0

    if not isinstance(data, dict):
        return 0

    # UserPromptSubmit payload field is conventionally `prompt`; some sources
    # use `user_prompt`. Accept either for forward-compat.
    prompt = str(data.get("prompt") or data.get("user_prompt") or "")
    if not prompt.strip():
        return 0

    # Bypass phrase short-circuit
    if BYPASS_PHRASE in prompt.lower():
        return 0

    # Skill-already-invoked short-circuit
    log = load_skill_log()
    if (skill_invoked(SYSTEMATIC_DEBUGGING_SKILL, log)
            or skill_invoked(SUPERPOWERS_SYSTEMATIC_DEBUGGING_SKILL, log)):
        return 0

    # Match patterns
    state = load_state()
    matched_keys = []
    for pattern, key_suffix in TRIGGER_PATTERNS:
        if pattern.search(prompt):
            key = f"process-violation:{key_suffix}"
            if not already_nudged(state, key):
                matched_keys.append(key_suffix)
                mark_nudged(state, key)

    if matched_keys:
        emit(build_nudge_text(matched_keys))
        save_state(state)

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Safe-fail: never block a user prompt due to hook bug.
        pass
    sys.exit(0)
