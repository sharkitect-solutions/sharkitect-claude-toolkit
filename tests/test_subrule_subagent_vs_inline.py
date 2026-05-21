"""Tests for subagent_vs_inline sub-rule.

skip brainstorming -- executing locked plan 2026-05-21-build-6-v5-inline-default-subagent-exception.md

Spec: docs/superpowers/specs/2026-05-21-build-6-v5-inline-default-subagent-exception-design.md
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_subrule():
    src = Path.home() / ".claude" / "hooks" / "_subrules" / "sharkitect" / "subagent_vs_inline.py"
    assert src.exists(), f"sub-rule not found at {src}"
    hooks_dir = Path.home() / ".claude" / "hooks"
    if str(hooks_dir) not in sys.path:
        sys.path.insert(0, str(hooks_dir))
    spec = importlib.util.spec_from_file_location("subagent_vs_inline_mod", str(src))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _empty_context():
    return {"active_plans": [], "session_brief": None, "workspace": "skill-management-hub", "bypass_phrases_in_prompt": []}


def _context_with_plans(plans):
    return {"active_plans": list(plans), "session_brief": None, "workspace": "skill-management-hub", "bypass_phrases_in_prompt": []}


# ---- Fire-on-trigger ----

def test_let_execute_fires():
    mod = _load_subrule()
    r = mod.check("let's execute the plan", _empty_context())
    assert r is not None
    assert r.rule_name == "subagent_vs_inline"
    assert r.severity == "warning"
    assert r.bypass_keyword == "skip subagent-vs-inline"
    assert r.cost_class == "heuristic"


def test_implement_plan_fires():
    mod = _load_subrule()
    assert mod.check("implement the v4 plan", _empty_context()) is not None


def test_start_phase_fires():
    mod = _load_subrule()
    assert mod.check("start Phase 2", _empty_context()) is not None


def test_skill_named_executing_plans_fires():
    mod = _load_subrule()
    assert mod.check("let's run superpowers:executing-plans on this", _empty_context()) is not None


def test_skill_named_subagent_driven_fires():
    mod = _load_subrule()
    assert mod.check("should we use superpowers:subagent-driven-development?", _empty_context()) is not None


def test_invoke_executing_plans_fires():
    mod = _load_subrule()
    assert mod.check("invoke executing-plans for the Build 6 v4 plan", _empty_context()) is not None


def test_dispatch_subagents_fires():
    mod = _load_subrule()
    assert mod.check("let's dispatch subagents in parallel", _empty_context()) is not None


def test_agent_tool_fires():
    mod = _load_subrule()
    assert mod.check("use the Agent tool to run these audits", _empty_context()) is not None


# ---- No-fire ----

def test_state_query_no_fire():
    mod = _load_subrule()
    assert mod.check("is the plan done?", _empty_context()) is None


def test_planning_only_no_fire():
    mod = _load_subrule()
    assert mod.check("let's plan Phase 3", _empty_context()) is None


def test_resume_signal_no_fire():
    mod = _load_subrule()
    assert mod.check("pick up where we left off", _empty_context()) is None


def test_unrelated_execute_no_fire():
    mod = _load_subrule()
    # "execute the SQL query" -- execute verb but no plan/phase/task scope nor skill mention
    assert mod.check("execute the SQL query and show me the rows", _empty_context()) is None


def test_unrelated_run_no_fire():
    mod = _load_subrule()
    # "run the test suite" -- run verb but tied to "tests", not plan execution
    assert mod.check("run the test suite", _empty_context()) is None


# ---- Bypass ----

def test_bypass_keyword_correct():
    mod = _load_subrule()
    r = mod.check("let's execute the plan", _empty_context())
    assert r is not None
    assert r.bypass_keyword == "skip subagent-vs-inline"


# ---- Context ----

def test_active_plans_in_evidence():
    mod = _load_subrule()
    r = mod.check("execute plan", _context_with_plans(["foo.md", "bar.md"]))
    assert r is not None
    assert "2 active plan" in (r.match_evidence or "")


def test_no_active_plans_evidence_noted():
    mod = _load_subrule()
    r = mod.check("execute plan", _empty_context())
    assert r is not None
    assert "no active plans" in (r.match_evidence or "")


def test_missing_context_keys_no_crash():
    mod = _load_subrule()
    r = mod.check("execute the plan", {})
    assert r is not None  # defensive .get() -- no key required


# ---- Integration with v4 ----

def test_v4_and_v5_both_fire_on_mixed_prompt(tmp_path):
    """Confirm both sub-rules return non-None on a mixed planning + execution prompt."""
    # v5
    mod_v5 = _load_subrule()
    r5 = mod_v5.check("let's plan and execute Phase 3", _empty_context())
    assert r5 is not None, "v5 should fire on 'execute Phase 3'"

    # v4
    v4_path = Path.home() / ".claude" / "hooks" / "_subrules" / "sharkitect" / "bigger_picture_first.py"
    if not v4_path.exists():
        # v4 not yet shipped -- skip the v4 side of the integration test.
        # The v4 plan covers its own fire-on-trigger; cross-test runs in full
        # only after BOTH are deployed.
        return
    spec_v4 = importlib.util.spec_from_file_location("bigger_picture_first_mod", str(v4_path))
    assert spec_v4 is not None and spec_v4.loader is not None
    mod_v4 = importlib.util.module_from_spec(spec_v4)
    spec_v4.loader.exec_module(mod_v4)
    r4 = mod_v4.check("let's plan and execute Phase 3", _empty_context())
    assert r4 is not None, "v4 should fire on 'plan Phase 3'"
