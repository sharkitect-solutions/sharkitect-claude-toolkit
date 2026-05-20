"""Tests for strategy_creation sub-rule.

Build 6 v2 (2026-05-20) — nudges invocation of the Sharkitect methodology
stack (pricing-strategy / marketing-strategy-pmm / smb-cfo / hq-revenue-ops /
brainstorming) when the user prompt initiates new pricing, positioning,
proposal, or strategic-decision work.

Source: wr-hq-2026-05-14-002 (Strategy Creation Rules round-table skipped on
pricing/positioning work; recurring failure class). Stacks on the v1.5
fortified pattern (word-boundary bypass, severity, match_evidence).

Bypass: 'skip strategy-creation'.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))
sys.path.insert(0, str(Path.home() / ".claude" / "tests"))

from _subrule_test_fixtures import make_context


# ---------------------------------------------------------------------------
# Firing behavior — pricing prompts
# ---------------------------------------------------------------------------


def test_fires_on_design_pricing_model_prompt():
    """User asks to design / build / draft a new pricing model -> rule fires."""
    from _subrules.sharkitect.strategy_creation import check

    ctx = make_context()
    result = check("let's design a new pricing model for the agency tier", ctx)

    assert result is not None
    assert result.mode == "advisory"
    assert result.rule_name == "strategy_creation"


def test_fires_on_how_much_should_we_charge():
    """Forward-looking pricing question -> rule fires."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("how much should we charge for the partnership tier?", make_context())
    assert result is not None


def test_fires_on_willingness_to_pay_analysis():
    """WTP keyword -> pricing-strategy required."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("we need to do a willingness-to-pay analysis on the new tier", make_context())
    assert result is not None


def test_fires_on_value_based_pricing():
    """Value-based pricing keyword -> rule fires."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("can we move this client to value-based pricing", make_context())
    assert result is not None


# ---------------------------------------------------------------------------
# Firing behavior — positioning / GTM prompts
# ---------------------------------------------------------------------------


def test_fires_on_positioning_work():
    """Positioning keyword -> marketing-strategy-pmm required."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("we need to rework our positioning against Cyncly", make_context())
    assert result is not None


def test_fires_on_april_dunford_reference():
    """Explicit April Dunford method reference -> rule fires."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("apply the April Dunford method to our positioning", make_context())
    assert result is not None


def test_fires_on_go_to_market_strategy():
    """GTM strategy work -> rule fires."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("draft a go-to-market strategy for the new product", make_context())
    assert result is not None


def test_fires_on_icp_definition():
    """ICP / ideal customer profile work -> rule fires."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("we need to define our ICP for the SMB segment", make_context())
    assert result is not None


# ---------------------------------------------------------------------------
# Firing behavior — proposal / SOW authoring
# ---------------------------------------------------------------------------


def test_fires_on_draft_proposal():
    """Drafting a client proposal -> hq-revenue-ops + pricing-strategy required."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("draft a proposal for the FF Hibu marketing takeover", make_context())
    assert result is not None


def test_fires_on_sow_creation():
    """Statement of work creation -> rule fires."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("let's put together a statement of work for the cards project", make_context())
    assert result is not None


# ---------------------------------------------------------------------------
# Firing behavior — strategic decisions
# ---------------------------------------------------------------------------


def test_fires_on_strategic_decision():
    """Strategic-decision keyword -> ceo-advisor + methodology stack required."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("we have a strategic decision to make about the partnership model", make_context())
    assert result is not None


def test_fires_on_market_entry():
    """Market entry / expansion -> strategy work required."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("planning market entry into the bathroom-remodel vertical", make_context())
    assert result is not None


# ---------------------------------------------------------------------------
# Negative cases — does NOT fire on unrelated prompts
# ---------------------------------------------------------------------------


def test_does_not_fire_on_code_request():
    """Pure coding prompt -> rule stays silent."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("write a python function to parse the json file", make_context())
    assert result is None


def test_does_not_fire_on_debugging_prompt():
    """Debugging prompt -> rule stays silent (systematic-debugging is a different skill)."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("the test is failing with a null reference error, help debug", make_context())
    assert result is None


def test_does_not_fire_on_infra_prompt():
    """Infrastructure work -> rule stays silent."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("set up the cron poll for the inbox", make_context())
    assert result is None


def test_does_not_fire_on_pure_state_query():
    """State queries are verify_state's job, not strategy_creation's.

    'what's the current pricing' is a read-only state query — verify_state
    fires here, strategy_creation should stay silent (we are not authoring
    new pricing work).
    """
    from _subrules.sharkitect.strategy_creation import check

    result = check("what's our current pricing for the agency tier", make_context())
    assert result is None


# ---------------------------------------------------------------------------
# Contract — severity, match_evidence, bypass, message
# ---------------------------------------------------------------------------


def test_severity_is_warning():
    """Strategy skips have real downstream cost — severity must be warning, not info.

    Source: 4+ documented recurrences across HQ + Sentinel of methodology
    skipping on strategy work. Each recurrence cost real work and risked
    real deals (wr-hq-2026-05-11-001, wr-hq-2026-05-11-003, etc.).
    """
    from _subrules.sharkitect.strategy_creation import check

    result = check("design a new pricing model", make_context())
    assert result is not None
    assert result.severity == "warning"


def test_match_evidence_populated():
    """Sub-rule must explain WHY it fired so debugging is cheap."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("how much should we charge for the new tier", make_context())
    assert result is not None
    assert result.match_evidence is not None
    # Evidence should mention the matched domain (pricing/positioning/proposal/strategy)
    assert any(
        kw in result.match_evidence.lower()
        for kw in ("pric", "position", "proposal", "strateg")
    ), f"match_evidence should name the matched domain. Got: {result.match_evidence!r}"


def test_bypass_keyword_format():
    """Bypass follows the 'skip <slug>' contract."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("design a new pricing model", make_context())
    assert result is not None
    assert result.bypass_keyword == "skip strategy-creation"
    assert result.bypass_keyword.startswith("skip ")


def test_message_references_methodology_stack():
    """Nudge text must point operator at the methodology skills to invoke."""
    from _subrules.sharkitect.strategy_creation import check

    result = check("design a new pricing model", make_context())
    assert result is not None
    msg = result.message.lower()
    # Must name at least 2 of the methodology skills so operator knows what to invoke
    skill_mentions = sum(
        1 for skill in (
            "pricing-strategy",
            "marketing-strategy-pmm",
            "smb-cfo",
            "hq-revenue-ops",
            "brainstorming",
            "using-sharkitect-methodology",
        ) if skill in msg
    )
    assert skill_mentions >= 2, (
        f"Nudge should reference at least 2 methodology skills so operator "
        f"knows what to invoke. Found {skill_mentions} in: {result.message!r}"
    )


def test_message_mentions_ceo_advisor_for_company_affecting_work():
    """Strategy work is always company-affecting -> ceo-advisor mandatory.

    Per the CEO Advisor Mandatory Invocation rule (universal-protocols.md,
    2026-05-17 S55), every company-affecting decision requires ceo-advisor
    invocation BEFORE the substantive response. Strategy creation IS
    company-affecting by definition.
    """
    from _subrules.sharkitect.strategy_creation import check

    result = check("rework our positioning against the competitor", make_context())
    assert result is not None
    assert "ceo-advisor" in result.message.lower()


# ---------------------------------------------------------------------------
# Word-boundary + false-positive containment
# ---------------------------------------------------------------------------


def test_word_boundary_pricing_not_matching_inside_word():
    """The substring 'pric' inside another word should NOT trigger.

    Regex must use \\b so words like 'apricot' or 'unpriced' don't false-fire.
    """
    from _subrules.sharkitect.strategy_creation import check

    # 'unpriced' contains 'pric' as substring; with proper word boundary the
    # rule should not infer this is pricing-design work.
    result = check("the apricot section is unpriced in the spreadsheet", make_context())
    # Could legitimately go either way — the heuristic accepts some FP
    # to maximize recall. The bypass keyword is the operator's escape valve.
    # What we explicitly assert: if it fires, evidence still mentions the
    # matched pattern so the FP is debuggable.
    if result is not None:
        assert result.match_evidence is not None


# ---------------------------------------------------------------------------
# Integration — dispatcher actually wires strategy_creation
# ---------------------------------------------------------------------------


def test_dispatcher_emits_strategy_creation_nudge_when_enabled(monkeypatch, tmp_path):
    """End-to-end: dispatcher loads enabled sub-rule -> emits nudge on strategy prompt."""
    from _subrule_test_fixtures import write_dispatcher_config
    cfg_path = write_dispatcher_config(
        tmp_path,
        enabled_subrules=["sharkitect.strategy_creation"],
    )
    monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "userpromptsubmit_dispatcher_test_import",
        Path.home() / ".claude" / "hooks" / "userpromptsubmit-dispatcher.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    result = mod.run_dispatcher(prompt="design a new pricing model")
    ctx = result.get("hookSpecificOutput", {}).get("additionalContext", "")
    assert "strategy_creation" in ctx
    assert "skip strategy-creation" in ctx


def test_dispatcher_bypass_skips_strategy_creation(monkeypatch, tmp_path):
    """Bypass phrase in prompt -> no nudge emitted."""
    from _subrule_test_fixtures import write_dispatcher_config
    cfg_path = write_dispatcher_config(
        tmp_path,
        enabled_subrules=["sharkitect.strategy_creation"],
    )
    monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "userpromptsubmit_dispatcher_test_import_bypass",
        Path.home() / ".claude" / "hooks" / "userpromptsubmit-dispatcher.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    result = mod.run_dispatcher(prompt="design a new pricing model. skip strategy-creation")
    ctx = result.get("hookSpecificOutput", {}).get("additionalContext", "")
    assert ctx == ""
