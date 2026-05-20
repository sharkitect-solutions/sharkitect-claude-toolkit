"""plan_resume sub-rule - detects "pick up where we left off" / "continue" /
"resume" prompts AND active plans in flight, then nudges invocation of the
superpowers:executing-plans skill.

Stacks on the v2.1 active_plans population: without `context["active_plans"]`
being filled by the dispatcher, this rule could not distinguish "resume the
work" from "resume the conversation." Empty active_plans -> silent
(intentional: nothing to resume against).

Severity = warning. Multi-task plan drop is a documented recurrence class
(wr-sentinel-2026-05-18-002 + repeated PROCESS-skill skip incidents). The
cost of an unprompted plan re-entry is concrete: tasks executed out of
order, methodology skipped between steps, plan state diverging from
Supabase.

Bypass: 'skip plan-resume' (word-boundary match).

History:
    v3.0 (2026-05-20) - initial implementation per Build 6 spec sub-rule
      roadmap (line 278). Patterns scoped to explicit resume signals; the
      active_plans non-empty guard prevents noise when no plan is in flight.
      Per the spec note about /goal command overlap: shipping the sub-rule
      first; migration to /goal-based semantics deferred to AIOS Phase 5.
"""
import re

from _subrules.sharkitect._contract import SubRuleResult


# Each pattern captures an explicit resume signal. Word-boundary anchors
# prevent false positives (e.g., 'resume' inside 'presumed', 'continue'
# inside 'continuous'). Phrases are intentionally narrow — the rule fires
# only when the user is signaling intent to resume work, not when the word
# appears incidentally in unrelated prose.
PLAN_RESUME_PATTERNS = [
    # Classic resume signals
    r"\bpick\s+(?:up|back\s+up)\s+(?:where\s+(?:we|i)\s+(?:left|stopped|paused))?",
    r"\b(?:let'?s|let\s+us)\s+(?:continue|resume|keep\s+going|pick\s+(?:up|back\s+up))\b",
    r"\b(?:where\s+(?:were|are)\s+we|where\s+(?:did|do)\s+we\s+(?:leave\s+off|stop|pause))\b",
    r"\bback\s+to\s+it\b",
    r"\bkeep\s+going\b",
    r"\bcontinue\s+(?:the|on|with|from|where)\b",
    r"\bresume\s+(?:the|on|with|from|where)\b",
    r"\bpick\s+back\s+up\b",
    # Lone-word variants — anchored to start of prompt OR after sentence
    # boundary so they don't match "continue" embedded in unrelated prose.
    r"^\s*(?:continue|resume)\b",
    r"[\.\?!]\s*(?:continue|resume)\b",
]


def _matched_resume_signal(prompt: str):
    """Return (pattern, match_obj) for first matching pattern, else None."""
    p = prompt.lower()
    for pattern in PLAN_RESUME_PATTERNS:
        m = re.search(pattern, p)
        if m:
            return pattern, m
    return None


def _format_active_plans_summary(active_plans: list) -> str:
    """One-line summary of active plans for the nudge message.

    Keeps the nudge actionable — the AI sees the plan paths and can pick the
    right one without re-reading plans-registry.md.
    """
    if not active_plans:
        return "no active plans"
    if len(active_plans) == 1:
        return f"1 active plan: {active_plans[0]}"
    if len(active_plans) <= 3:
        return f"{len(active_plans)} active plans: " + ", ".join(active_plans)
    # Truncate long lists to avoid bloating additionalContext
    head = ", ".join(active_plans[:3])
    return f"{len(active_plans)} active plans (showing first 3): {head}, ..."


def check(prompt: str, context: dict):
    """Fire on resume-signal prompts when at least one active plan exists.

    Returns SubRuleResult(advisory, severity=warning) when both conditions
    hold; returns None otherwise.

    Design note: this rule cannot detect "executing-plans skill already
    invoked this session" because recent_tool_calls was removed in v1.5
    (per 100% Verification protocol — per-action verification, not
    per-session caching). The trade-off: the rule may nudge re-invocation,
    which is cheap (the skill is a fast read). False-positive cost is low.
    """
    active_plans = context.get("active_plans") or []
    if not active_plans:
        # No plans in flight -> resume signal is conversational, not work-related.
        # Keep silent to avoid noise.
        return None

    matched = _matched_resume_signal(prompt)
    if matched is None:
        return None

    pattern, m = matched
    matched_phrase = m.group(0).strip()
    evidence = (
        f"resume signal {matched_phrase!r} at offset {m.start()}; "
        f"{len(active_plans)} active plan(s) in registry"
    )

    plans_summary = _format_active_plans_summary(active_plans)

    message = (
        f"Resume signal detected with {plans_summary}. Before continuing, "
        f"invoke superpowers:executing-plans -- the skill enforces "
        f"task-by-task discipline (one task in_progress at a time, "
        f"verifications before claiming completion, finishing-a-development-"
        f"branch on done). Multi-task plan drop is a documented recurrence "
        f"class (wr-sentinel-2026-05-18-002 + repeated PROCESS-skill skip "
        f"incidents); this is the runtime enforcement layer."
    )

    return SubRuleResult(
        mode="advisory",
        message=message,
        rule_name="plan_resume",
        bypass_keyword="skip plan-resume",
        severity="warning",
        match_evidence=evidence,
        cost_class="heuristic",
    )
