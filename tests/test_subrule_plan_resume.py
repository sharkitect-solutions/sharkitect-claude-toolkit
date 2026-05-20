"""Tests for plan_resume sub-rule.

Build 6 v3 (2026-05-20) — nudges invocation of the
superpowers:executing-plans skill when the user signals "pick up where we
left off" / "continue" / "resume" AND there is at least one active plan in
the plans-registry. Prevents the multi-task plan drop class documented in
wr-sentinel-2026-05-18-002.

Pairs with v2.1 active_plans population (Build 6 v2.1) — without v2.1's
plans-registry read, this rule could not differentiate "resume work" from
"resume conversation."

Bypass: 'skip plan-resume'.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))
sys.path.insert(0, str(Path.home() / ".claude" / "tests"))

from _subrule_test_fixtures import make_context


# ---------------------------------------------------------------------------
# Firing behavior — resume signals with active plans
# ---------------------------------------------------------------------------


def test_fires_on_pick_up_where_we_left_off_with_active_plan():
    """Classic resume signal + active plan present -> fires."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/2026-05-18-build-6.md"])
    result = check("pick up where we left off", ctx)

    assert result is not None
    assert result.mode == "advisory"
    assert result.rule_name == "plan_resume"


def test_fires_on_lets_continue_with_active_plan():
    """'let's continue' signal -> fires when plans active."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/active.md"])
    result = check("let's continue", ctx)

    assert result is not None


def test_fires_on_continue_with_active_plan():
    """Bare 'continue' word-bounded -> fires."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("continue the build", ctx)

    assert result is not None


def test_fires_on_resume_with_active_plan():
    """'resume' word-bounded -> fires."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("resume the work from last session", ctx)

    assert result is not None


def test_fires_on_where_were_we_with_active_plan():
    """'where were we' signal -> fires."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("where were we on this", ctx)

    assert result is not None


def test_fires_on_back_to_it_with_active_plan():
    """'back to it' colloquial resume -> fires."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("alright back to it", ctx)

    assert result is not None


def test_fires_on_keep_going_with_active_plan():
    """'keep going' signal -> fires."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("keep going on the plan", ctx)

    assert result is not None


def test_fires_on_pick_back_up_with_active_plan():
    """'pick back up' variant -> fires."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("let's pick back up where we stopped", ctx)

    assert result is not None


# ---------------------------------------------------------------------------
# Non-firing behavior
# ---------------------------------------------------------------------------


def test_does_not_fire_when_no_active_plans():
    """Resume signal but no active plan -> silent. Avoids noise when nothing's in flight."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=[])
    result = check("pick up where we left off", ctx)

    assert result is None


def test_does_not_fire_on_non_resume_prompts():
    """Random non-resume prompt -> silent."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("write me a quicksort in python", ctx)

    assert result is None


def test_does_not_fire_on_state_query():
    """State query falls to verify_state's domain, not plan_resume."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("is the build done", ctx)

    assert result is None


def test_does_not_fire_on_strategy_creation_prompt():
    """New strategy work falls to strategy_creation, not plan_resume."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("let's design a new pricing model", ctx)

    assert result is None


def test_does_not_fire_on_simple_thank_you():
    """Conversational closers don't fire."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("thanks", ctx)

    assert result is None


# ---------------------------------------------------------------------------
# Required SubRuleResult fields
# ---------------------------------------------------------------------------


def test_severity_is_warning():
    """Multi-task plan drop is a documented recurrence class -> warning."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("pick up where we left off", ctx)

    assert result is not None
    assert result.severity == "warning"


def test_bypass_keyword_is_skip_plan_resume():
    """Bypass slug per Strict Bypass Vocabulary."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("pick up where we left off", ctx)

    assert result is not None
    assert result.bypass_keyword == "skip plan-resume"


def test_match_evidence_populated():
    """match_evidence describes which signal fired and the active plan count."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/a.md", "~/.claude/plans/b.md"])
    result = check("pick up where we left off", ctx)

    assert result is not None
    assert result.match_evidence is not None
    assert len(result.match_evidence) > 0


def test_cost_class_is_heuristic():
    """Pure regex + context dict read -> heuristic cost class."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("pick up where we left off", ctx)

    assert result is not None
    assert result.cost_class == "heuristic"


# ---------------------------------------------------------------------------
# Nudge content
# ---------------------------------------------------------------------------


def test_nudge_message_names_executing_plans_skill():
    """Nudge cites superpowers:executing-plans by name so AI knows what to invoke."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"])
    result = check("pick up where we left off", ctx)

    assert result is not None
    assert "executing-plans" in result.message.lower()


def test_nudge_message_mentions_active_plan_count():
    """Nudge surfaces how many active plans are in flight so AI doesn't have to look it up."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=[
        "~/.claude/plans/a.md",
        "~/.claude/plans/b.md",
        "~/.claude/plans/c.md",
    ])
    result = check("pick up where we left off", ctx)

    assert result is not None
    # The message should reference the plans (count or path mention)
    msg = result.message.lower()
    assert ("3" in msg) or ("active plan" in msg) or ("plans-registry" in msg)


# ---------------------------------------------------------------------------
# Context tolerance — defensive coding
# ---------------------------------------------------------------------------


def test_tolerates_missing_session_brief():
    """session_brief=None must not break the check."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(active_plans=["~/.claude/plans/x.md"], session_brief=None)
    result = check("pick up where we left off", ctx)

    assert result is not None


def test_tolerates_workspace_other_than_skill_hub():
    """Rule fires regardless of workspace (HQ + Sentinel run plans too)."""
    from _subrules.sharkitect.plan_resume import check

    ctx = make_context(
        active_plans=["~/.claude/plans/x.md"],
        workspace="workforce-hq",
    )
    result = check("pick up where we left off", ctx)

    assert result is not None
