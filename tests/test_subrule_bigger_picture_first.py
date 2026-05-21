"""Tests for bigger_picture_first sub-rule.

skip brainstorming -- executing locked plan 2026-05-21-build-6-v4-bigger-picture-first.md

Spec: docs/superpowers/specs/2026-05-21-build-6-v4-bigger-picture-first-design.md
"""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_subrule():
    src = Path.home() / ".claude" / "hooks" / "_subrules" / "sharkitect" / "bigger_picture_first.py"
    assert src.exists(), f"sub-rule not found at {src}"
    # The sub-rule imports from _subrules.sharkitect._contract -- make _subrules importable
    hooks_dir = Path.home() / ".claude" / "hooks"
    import sys
    if str(hooks_dir) not in sys.path:
        sys.path.insert(0, str(hooks_dir))
    spec = importlib.util.spec_from_file_location("bigger_picture_first_mod", str(src))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _empty_context():
    return {"active_plans": [], "session_brief": None, "workspace": "skill-management-hub", "bypass_phrases_in_prompt": []}


# ---- Fire-on-trigger cases ----

def test_explicit_planning_fires():
    mod = _load_subrule()
    r = mod.check("let's plan the Phase 2 architecture", _empty_context())
    assert r is not None
    assert r.rule_name == "bigger_picture_first"
    assert r.severity == "warning"
    assert r.bypass_keyword == "skip bigger-picture-first"
    assert r.cost_class == "heuristic"


def test_design_verb_fires():
    mod = _load_subrule()
    r = mod.check("let me design a new hook to catch this", _empty_context())
    assert r is not None


def test_spec_out_fires():
    mod = _load_subrule()
    r = mod.check("let's spec out the userpromptsubmit dispatcher v6", _empty_context())
    assert r is not None


def test_should_we_build_fires():
    mod = _load_subrule()
    r = mod.check("should we build a separate dispatcher for PostToolUse?", _empty_context())
    assert r is not None


def test_what_should_we_build_next_fires():
    mod = _load_subrule()
    r = mod.check("what should we build next on Build 6?", _empty_context())
    assert r is not None


def test_infrastructure_creation_fires():
    mod = _load_subrule()
    r = mod.check("create a new automation for orphan cleanup", _empty_context())
    assert r is not None


def test_architecture_decision_fires():
    mod = _load_subrule()
    r = mod.check("we need an architecture decision on the sub-rule contract", _empty_context())
    assert r is not None


def test_consolidation_fires():
    mod = _load_subrule()
    r = mod.check("let's consolidate the methodology hooks into the dispatcher", _empty_context())
    assert r is not None


def test_aios_productization_fires():
    mod = _load_subrule()
    r = mod.check("this needs to ship as an AIOS client capability", _empty_context())
    assert r is not None


def test_authoring_with_scope_marker_fires():
    mod = _load_subrule()
    r = mod.check("draft a plan for the next phase rollout", _empty_context())
    assert r is not None


# ---- No-fire (false-positive prevention) ----

def test_state_query_does_not_fire():
    mod = _load_subrule()
    # verify_state's domain -- must not be poached by v4
    assert mod.check("is the Phase 2 plan done?", _empty_context()) is None


def test_bare_plan_no_scope_no_fire():
    mod = _load_subrule()
    assert mod.check("let's plan dinner this weekend", _empty_context()) is None


def test_spec_recipe_no_fire():
    mod = _load_subrule()
    assert mod.check("spec out this recipe for me", _empty_context()) is None


def test_draft_email_no_fire():
    mod = _load_subrule()
    assert mod.check("draft an email to the client", _empty_context()) is None


def test_resume_signal_no_fire():
    mod = _load_subrule()
    # plan_resume's domain
    assert mod.check("let's continue where we left off", _empty_context()) is None


def test_strategy_pricing_no_fire():
    mod = _load_subrule()
    # strategy_creation's domain -- pricing tier work falls to that rule, not v4
    assert mod.check("design a new pricing tier", _empty_context()) is None


# ---- Bypass ----

def test_bypass_skip_phrase_skips():
    mod = _load_subrule()
    # Per dispatcher contract, bypass is enforced by the DISPATCHER after the
    # rule returns its result, not by the rule itself. The rule still returns
    # a SubRuleResult; the dispatcher suppresses emission.
    # This test confirms the rule's bypass_keyword string is correct so the
    # dispatcher can match it.
    r = mod.check("let's plan the next phase", _empty_context())
    assert r is not None
    assert r.bypass_keyword == "skip bigger-picture-first"


# ---- Context tolerance ----

def test_empty_active_plans_no_effect():
    mod = _load_subrule()
    r = mod.check("let's plan Phase 3 architecture", {"active_plans": [], "session_brief": None, "workspace": "skill-management-hub", "bypass_phrases_in_prompt": []})
    assert r is not None  # rule does not consult active_plans


def test_no_session_brief_no_effect():
    mod = _load_subrule()
    r = mod.check("let's plan Phase 3 architecture", {"active_plans": [], "session_brief": None, "workspace": "skill-management-hub", "bypass_phrases_in_prompt": []})
    assert r is not None


def test_missing_context_keys_no_crash():
    mod = _load_subrule()
    # Defensive .get() access -- empty dict must not crash
    r = mod.check("let's plan Phase 3 architecture", {})
    assert r is not None  # rule does not strictly require any context key
