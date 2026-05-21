"""subagent_vs_inline sub-rule -- detects plan-execution moments and nudges
the Inline-Default / Subagent-Exception Discipline protocol's 4-condition gate.

skip brainstorming -- executing locked plan 2026-05-21-build-6-v5-inline-default-subagent-exception.md

Source: universal-protocols.md "Inline-Default / Subagent-Exception Discipline"
(added 2026-05-21 v5). Refines and supersedes lessons-learned.md 2026-05-19
S61 entry. Three refinements applied per wr-hq-2026-05-20-001.

Bypass: 'skip subagent-vs-inline' (word-boundary match) in the user's prompt.

History:
    v5.0 (2026-05-21) -- initial implementation per Build 6 spec Section 7
      sub-rule roadmap + v5 spec. Detection on USER's prompt at UserPromptSubmit.
      Severity=warning.
"""
import re

from _subrules.sharkitect._contract import SubRuleResult


SUBAGENT_VS_INLINE_PATTERNS = [
    # Direct execution verbs
    (r"\b(let'?s|let\s+us|i\s+(?:want|need)\s+to|we\s+(?:should|need\s+to))\s+(execute|run|implement|ship|tackle|kick\s+off|kick\s+it\s+off)\b", "execution_intent"),

    # Execute + plan/phase/task object
    (r"\b(execute|implement|run|start\s+work\s+on|kick\s+off|ship)\s+(?:the|this|that|our|some\s+|\S+\s+)*(plan|phase|task|tasks|build|step|steps)\b", "plan_execution"),

    # Phase start
    (r"\b(start|begin|kick\s+off|fire\s+up)\s+phase\s+\d+\b", "phase_start"),

    # Skill mentions
    (r"\bsuperpowers:(executing-plans|subagent-driven-development|dispatching-parallel-agents)\b", "skill_named"),
    (r"\binvoke\s+(?:\S+\s+){0,3}(executing-plans|subagent-driven-development|dispatching-parallel-agents)\b", "skill_invocation"),

    # Dispatch language (plural forms included -- "dispatch subagents")
    (r"\b(dispatch|spawn|fan\s+out|parallelize|distribute)\s+(?:\S+\s+){0,3}(subagents?|agents?|tasks?)\b", "dispatch_language"),

    # Tool language ("use the Agent tool" / "use the Task tool")
    (r"\buse\s+(?:the\s+)?(agent|task)\s+tool\b", "tool_language"),
]


def _first_matching_pattern(prompt: str, patterns):
    p = prompt.lower()
    for pattern, category in patterns:
        m = re.search(pattern, p)
        if m:
            return pattern, m, category
    return None


_NUDGE_MESSAGE = (
    "Plan-execution moment detected. The Inline-Default / Subagent-Exception "
    "Discipline (NON-NEGOTIABLE, universal-protocols.md) applies:\n"
    "  Default: INLINE execution via superpowers:executing-plans (the live "
    "controller drives every task).\n"
    "  Exception: superpowers:subagent-driven-development requires ALL FOUR "
    "conditions to pass:\n"
    "    (1) Self-contained in the plan -- code, test commands, expected "
    "output present inline.\n"
    "    (2) Zero prior-conversation context dependency -- nothing from "
    "earlier in this session is load-bearing.\n"
    "    (3) Repetitive or parallelizable -- same shape, different data, OR "
    "independent across tasks.\n"
    "    (4) Plan + workspace documentation are sufficient context -- no "
    "in-conversation discussion is load-bearing.\n"
    "  Any 1 condition fails -> inline. Ambiguous -> inline.\n"
    "  Do NOT frame inline as 'deviation from skill default' -- the upstream "
    "superpowers:writing-plans default is overridden by Sharkitect's system "
    "rule per universal-protocols.md Instruction Priority. Inline is the "
    "documented norm. Recurrence cost: S64 2026-05-20 framing-as-deviation "
    "incident."
)


def check(prompt: str, context: dict):
    """Fire on plan-execution prompts.

    Detection on USER's prompt at UserPromptSubmit time. active_plans context
    contributes to match_evidence (richer telemetry when plans are in flight)
    but does NOT gate firing -- ad-hoc execution prompts also benefit from the
    4-condition frame.
    """
    matched = _first_matching_pattern(prompt, SUBAGENT_VS_INLINE_PATTERNS)
    if matched is None:
        return None

    pattern, m, category = matched
    matched_phrase = m.group(0).strip()

    active_plans = context.get("active_plans") or []
    plan_context = (
        f"{len(active_plans)} active plan(s) in registry"
        if active_plans
        else "no active plans in registry (ad-hoc execution)"
    )
    evidence = (
        f"matched {category} pattern {pattern!r} on phrase "
        f"{matched_phrase!r} at offset {m.start()}; {plan_context}"
    )

    return SubRuleResult(
        mode="advisory",
        message=_NUDGE_MESSAGE,
        rule_name="subagent_vs_inline",
        bypass_keyword="skip subagent-vs-inline",
        severity="warning",
        match_evidence=evidence,
        cost_class="heuristic",
    )
