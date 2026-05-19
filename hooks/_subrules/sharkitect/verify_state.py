"""
verify_state sub-rule - detects AI-about-to-claim-state on state-query prompts.

Fires when the user's prompt matches a state-query pattern ("is X done?",
"what's the status?", "did Y land?", etc.). The 100% Verification Before
Any Action protocol mandates verifying directly-related facts against
source for EVERY action / recommendation / judgment call -- so the rule
fires on every state-query, regardless of prior session tool history.
Prior verification of a different topic does not satisfy verification need
for the current state-query.

Bypass: 'skip verify-state' (word-boundary match) in the user's prompt.

History:
    v1.5 (2026-05-19) - removed recent_tool_calls defensive check (was
      dead code; conflicted with 100% Verification protocol's per-action
      mandate). Added severity + match_evidence population per defect #3.
"""
import re

from _subrules.sharkitect._contract import SubRuleResult

STATE_QUERY_PATTERNS = [
    r"\bis\s+(?:\S+\s+){1,4}(done|complete|finished|landed|deployed|shipped|closed|merged|ready)\b",
    r"\bdid\s+(?:\S+\s+){1,4}(land|ship|deploy|complete|finish|close|merge|work)\b",
    r"\bhas\s+(?:\S+\s+){1,4}(been|landed|shipped|deployed|completed|finished|closed|merged)\b",
    r"\bwhat'?s\s+the\s+(status|state|progress)\b",
    r"\bwhere\s+(are\s+we|do\s+we\s+stand)\b",
    r"\b(status|state|progress)\s+of\s+\S+",
    r"\bdoes\s+(?:\S+\s+){1,4}(exist|work|run|fire)\b",
]


def _matched_state_query(prompt: str):
    """Return (pattern, match_object) for first matching state-query pattern, else None."""
    p = prompt.lower()
    for pattern in STATE_QUERY_PATTERNS:
        m = re.search(pattern, p)
        if m:
            return pattern, m
    return None


def check(prompt: str, context: dict):
    """Fire per-action on every state-query.

    The 100% Verification Before Any Action protocol (universal-protocols.md)
    mandates source-reads for every action / recommendation / judgment call.
    Each state-query is its own verification need; prior verification of a
    different topic does not satisfy this one.
    """
    matched = _matched_state_query(prompt)
    if matched is None:
        return None

    pattern, m = matched
    # Plain-language evidence so debugging "why did this fire?" doesn't
    # require re-running the rule logic mentally.
    matched_phrase = m.group(0)
    evidence = f"matched pattern {pattern!r} on phrase {matched_phrase!r} at offset {m.start()}"

    return SubRuleResult(
        mode="advisory",
        message=(
            "Before answering this state-query, verify by reading the actual "
            "source (Read / Grep / Bash / Supabase query). The 100% Verification "
            "Before Any Action protocol requires direct source reads, not "
            "inference from memory. Cite what you read."
        ),
        rule_name="verify_state",
        bypass_keyword="skip verify-state",
        severity="info",
        match_evidence=evidence,
    )
