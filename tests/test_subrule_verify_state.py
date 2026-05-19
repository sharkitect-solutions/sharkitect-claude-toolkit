"""Tests for verify_state sub-rule.

v1.5 (2026-05-19) Build 6 fortification per ai-systems-architect verdict:
  - Option D: removed `recent_tool_calls` defensive logic. The 100% Verification
    Before Any Action protocol mandates per-action source verification, so
    firing on every state-query is the intended behavior, not a false-positive.
    The prior "does not fire when recent Read/Grep/Bash" tests have been
    DELETED — they asserted the dead-code defense behavior that conflicted
    with the protocol the rule enforces.
  - Defect #3: SubRuleResult now carries severity + match_evidence fields.
    verify_state populates severity="info" and match_evidence with the
    matched state-query pattern.
"""
import sys
from pathlib import Path

# Ensure _subrules importable
sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))
sys.path.insert(0, str(Path.home() / ".claude" / "tests"))

from _subrule_test_fixtures import make_context


# ---------------------------------------------------------------------------
# Firing behavior — per-action verification per protocol
# ---------------------------------------------------------------------------


def test_fires_on_state_query_prompt():
    """User asks 'is X done?' -> rule fires.

    Per the 100% Verification Before Any Action protocol, every state-query
    requires its own verification. The rule fires on every state-query
    regardless of prior session tool history.
    """
    from _subrules.sharkitect.verify_state import check

    ctx = make_context()
    prompt = "is the migration done yet?"

    result = check(prompt, ctx)

    assert result is not None
    assert result.mode == "advisory"
    assert result.rule_name == "verify_state"
    assert result.bypass_keyword == "skip verify-state"
    assert "verify" in result.message.lower() or "read" in result.message.lower()


def test_does_not_fire_on_non_state_prompts():
    """Prompt that isn't asking about state -> rule stays silent."""
    from _subrules.sharkitect.verify_state import check

    ctx = make_context()
    prompt = "write me a python function to reverse a string"

    result = check(prompt, ctx)

    assert result is None


def test_fires_on_various_state_query_patterns():
    """Multiple state-query phrasings all trigger."""
    from _subrules.sharkitect.verify_state import check

    state_prompts = [
        "what's the status of the deployment",
        "did the migration land",
        "where are we at on the feature",
        "is the build complete",
        "has the WR been closed",
    ]
    ctx = make_context()

    for prompt in state_prompts:
        result = check(prompt, ctx)
        assert result is not None, f"Should fire for: {prompt!r}"


def test_empty_context_still_works():
    """Empty context dict still triggers on state-query."""
    from _subrules.sharkitect.verify_state import check

    ctx = make_context()
    prompt = "what's the status"

    result = check(prompt, ctx)

    assert result is not None


# ---------------------------------------------------------------------------
# Option D — protocol-aligned: fire regardless of tool history
# ---------------------------------------------------------------------------


def test_fires_even_when_recent_verification_tools_present():
    """v1.5 Option D: rule fires on state-query even if recent_tool_calls
    contains Read/Grep/Bash. The 100% Verification protocol requires
    per-action verification; prior verification of a different topic does
    not satisfy the verification need for this state-query.

    Source: ai-systems-architect verdict 2026-05-19 defect #2; reconciled
    against the 100% Verification Before Any Action protocol which mandates
    per-action verification (not per-session). Path D selected over the
    architect's prescribed path A (wire the journal) because Path A would
    weaken the protocol the rule enforces.
    """
    from _subrules.sharkitect.verify_state import check

    # Context populated with Read/Grep/Bash — under the OLD dead-code defense,
    # this would suppress firing. Under Option D, the rule fires anyway.
    from _subrule_test_fixtures import make_tool_call
    ctx = make_context(recent_tool_calls=[
        make_tool_call("Read", "some/unrelated/file"),
        make_tool_call("Grep", "unrelated pattern"),
        make_tool_call("Bash", "ls -la"),
    ])
    prompt = "is the migration done?"

    result = check(prompt, ctx)

    assert result is not None, (
        "verify_state must fire per-action regardless of prior tool history "
        "(100% Verification protocol). Path D removed the dead-code defense."
    )


# ---------------------------------------------------------------------------
# Defect #3 — SubRuleResult carries severity + match_evidence
# ---------------------------------------------------------------------------


def test_subrule_result_accepts_severity_field():
    """SubRuleResult must accept a severity field with values info/warning/critical."""
    from _subrules.sharkitect._contract import SubRuleResult

    r = SubRuleResult(
        mode="advisory",
        message="m",
        rule_name="r",
        bypass_keyword="skip r",
        severity="info",
    )
    assert r.severity == "info"

    r2 = SubRuleResult(
        mode="advisory",
        message="m",
        rule_name="r",
        bypass_keyword="skip r",
        severity="warning",
    )
    assert r2.severity == "warning"


def test_subrule_result_severity_defaults_to_info():
    """When severity is not provided, defaults to 'info' (most permissive)."""
    from _subrules.sharkitect._contract import SubRuleResult

    r = SubRuleResult(
        mode="advisory",
        message="m",
        rule_name="r",
        bypass_keyword="skip r",
    )
    assert r.severity == "info"


def test_subrule_result_accepts_match_evidence_field():
    """SubRuleResult must accept a match_evidence string explaining why it fired."""
    from _subrules.sharkitect._contract import SubRuleResult

    r = SubRuleResult(
        mode="advisory",
        message="m",
        rule_name="r",
        bypass_keyword="skip r",
        match_evidence="matched pattern X at offset 12",
    )
    assert r.match_evidence == "matched pattern X at offset 12"


def test_subrule_result_match_evidence_defaults_to_none():
    """When match_evidence is not provided, defaults to None."""
    from _subrules.sharkitect._contract import SubRuleResult

    r = SubRuleResult(
        mode="advisory",
        message="m",
        rule_name="r",
        bypass_keyword="skip r",
    )
    assert r.match_evidence is None


def test_subrule_result_severity_invalid_value_raises():
    """SubRuleResult rejects severity values outside the {info, warning, critical} vocabulary."""
    from _subrules.sharkitect._contract import SubRuleResult
    import pytest

    with pytest.raises(ValueError):
        SubRuleResult(
            mode="advisory",
            message="m",
            rule_name="r",
            bypass_keyword="skip r",
            severity="medium",  # invalid — would conflict with priority vocabulary
        )


# ---------------------------------------------------------------------------
# verify_state populates the new fields
# ---------------------------------------------------------------------------


def test_verify_state_populates_severity_info():
    """verify_state nudges are informational (operator may choose to verify)."""
    from _subrules.sharkitect.verify_state import check

    result = check("is the migration done?", make_context())

    assert result is not None
    assert result.severity == "info"


def test_verify_state_populates_match_evidence():
    """verify_state explains WHY it fired by reporting which pattern matched."""
    from _subrules.sharkitect.verify_state import check

    result = check("is the migration done?", make_context())

    assert result is not None
    assert result.match_evidence is not None, (
        "verify_state should populate match_evidence so debugging 'why did "
        "this fire?' doesn't require re-running the rule logic mentally."
    )
    # Evidence should mention "pattern" and the matched phrase
    assert "pattern" in result.match_evidence.lower() or "match" in result.match_evidence.lower()
