"""TDD tests for the 3 SHOULD-before-v3 architect fortifications.

Build 6 v2.1 (2026-05-20) — ai-systems-architect SHOULD-do-before-v3 items:
  1. cost_class field on SubRuleResult (forward-compatibility for Layer 3
     `prompt`-hook migration per spec §4.4)
  2. Dispatcher populates active_plans + session_brief in context
     (prerequisite for v3 plan_resume sub-rule)
  3. Per-rule timeout (defensive — prevents one slow sub-rule from blocking
     prompt processing)

Each item ships with its own test class. All 3 must pass before v3
(plan_resume) lands.

Source: ai-systems-architect verdict 2026-05-19 (post v1.5 fortification).
"""
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))
sys.path.insert(0, str(Path.home() / ".claude" / "tests"))

from _subrule_test_fixtures import make_context, write_dispatcher_config


def _load_dispatcher():
    """Fresh import of the dispatcher (it reads config at call time, not import)."""
    name = "ups_dispatcher_test"
    if name in sys.modules:
        del sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name,
        Path.home() / ".claude" / "hooks" / "userpromptsubmit-dispatcher.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ctx_text(result):
    return result.get("hookSpecificOutput", {}).get("additionalContext", "")


# ===========================================================================
# Item 1 — cost_class field on SubRuleResult
# ===========================================================================


class TestCostClassField:
    """SubRuleResult carries cost_class so dispatcher (today) and runbook (v3+)
    can route by execution cost.
    """

    def test_subrule_result_accepts_cost_class_heuristic(self):
        from _subrules.sharkitect._contract import SubRuleResult
        r = SubRuleResult(
            mode="advisory",
            message="m",
            rule_name="r",
            bypass_keyword="skip r",
            cost_class="heuristic",
        )
        assert r.cost_class == "heuristic"

    def test_subrule_result_accepts_cost_class_audit(self):
        from _subrules.sharkitect._contract import SubRuleResult
        r = SubRuleResult(
            mode="advisory",
            message="m",
            rule_name="r",
            bypass_keyword="skip r",
            cost_class="audit",
        )
        assert r.cost_class == "audit"

    def test_subrule_result_accepts_cost_class_llm_judge(self):
        from _subrules.sharkitect._contract import SubRuleResult
        r = SubRuleResult(
            mode="advisory",
            message="m",
            rule_name="r",
            bypass_keyword="skip r",
            cost_class="llm_judge",
        )
        assert r.cost_class == "llm_judge"

    def test_subrule_result_cost_class_defaults_to_heuristic(self):
        """Default cost_class is heuristic (cheapest layer)."""
        from _subrules.sharkitect._contract import SubRuleResult
        r = SubRuleResult(
            mode="advisory",
            message="m",
            rule_name="r",
            bypass_keyword="skip r",
        )
        assert r.cost_class == "heuristic"

    def test_subrule_result_cost_class_invalid_raises(self):
        """Vocabulary is strict: heuristic | audit | llm_judge only."""
        from _subrules.sharkitect._contract import SubRuleResult
        with pytest.raises(ValueError):
            SubRuleResult(
                mode="advisory",
                message="m",
                rule_name="r",
                bypass_keyword="skip r",
                cost_class="cheap",  # invalid
            )

    def test_verify_state_populates_cost_class_heuristic(self):
        """verify_state is a regex check -> cost_class=heuristic."""
        from _subrules.sharkitect.verify_state import check
        result = check("is the migration done?", make_context())
        assert result is not None
        assert result.cost_class == "heuristic"

    def test_strategy_creation_populates_cost_class_heuristic(self):
        """strategy_creation is a regex check -> cost_class=heuristic."""
        from _subrules.sharkitect.strategy_creation import check
        result = check("design a new pricing model", make_context())
        assert result is not None
        assert result.cost_class == "heuristic"


# ===========================================================================
# Item 2 — Dispatcher populates active_plans + session_brief
# ===========================================================================


class TestContextPopulation:
    """Dispatcher reads active_plans from plans-registry + session_brief from
    .tmp/session-brief-YYYY-MM-DD.md, passes both via context to sub-rules.
    Sub-rules (notably v3 plan_resume) consume them.
    """

    def test_active_plans_populated_from_registry(self, tmp_path, monkeypatch):
        """Active Plans section of plans-registry.md is parsed into context.active_plans."""
        registry = tmp_path / "plans-registry.md"
        registry.write_text(
            "# Plans Registry\n\n"
            "## Active Plans\n\n"
            "| Path | Status | Workspaces |\n"
            "|---|---|---|\n"
            "| `~/.claude/plans/feature-X.md` | active | skill-management-hub |\n"
            "| `~/.claude/plans/feature-Y.md` | pending | workforce-hq |\n"
            "\n## Completed Plans\n\n"
            "| Path | Outcome |\n"
            "|---|---|\n"
            "| `~/.claude/plans/done.md` | shipped |\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("PLANS_REGISTRY_PATH", str(registry))

        # Use a sub-rule that captures the context it received
        sentinel_file = (
            Path.home()
            / ".claude" / "hooks" / "_subrules" / "sharkitect"
            / "_test_capture_ctx.py"
        )
        sentinel_file.write_text(
            "from _subrules.sharkitect._contract import SubRuleResult\n"
            "captured_ctx = {}\n"
            "def check(prompt, ctx):\n"
            "    captured_ctx.clear(); captured_ctx.update(ctx)\n"
            "    return SubRuleResult(mode='advisory', message='ok', "
            "rule_name='_test_capture_ctx', bypass_keyword='skip cap')\n",
            encoding="utf-8",
        )
        try:
            cfg = write_dispatcher_config(
                tmp_path, enabled_subrules=["sharkitect._test_capture_ctx"]
            )
            monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg))

            mod = _load_dispatcher()
            mod.run_dispatcher(prompt="anything")

            # Re-import captured_ctx after run
            from _subrules.sharkitect import _test_capture_ctx
            importlib_reload = importlib.import_module
            cap = _test_capture_ctx.captured_ctx
            assert any("feature-X.md" in p for p in cap.get("active_plans", [])), (
                f"expected feature-X.md in active_plans, got {cap.get('active_plans')!r}"
            )
            # Completed Plans must NOT leak into active_plans
            assert not any("done.md" in p for p in cap.get("active_plans", []))
        finally:
            sentinel_file.unlink(missing_ok=True)

    def test_active_plans_tolerates_missing_registry(self, tmp_path, monkeypatch):
        """If plans-registry.md doesn't exist, active_plans is [] (not crash)."""
        monkeypatch.setenv("PLANS_REGISTRY_PATH", str(tmp_path / "nonexistent.md"))
        cfg = write_dispatcher_config(tmp_path, enabled_subrules=[])
        monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg))

        mod = _load_dispatcher()
        # Should not raise
        result = mod.run_dispatcher(prompt="anything")
        assert _ctx_text(result) == ""

    def test_session_brief_populated_from_file(self, tmp_path, monkeypatch):
        """Today's session brief in .tmp/session-brief-YYYY-MM-DD.md is read into context."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        brief_dir = tmp_path / ".tmp"
        brief_dir.mkdir()
        brief_path = brief_dir / f"session-brief-{today}.md"
        brief_path.write_text(
            "# Session brief\n\nLast session shipped Build 6 v1.5.",
            encoding="utf-8",
        )
        monkeypatch.setenv("SESSION_BRIEF_DIR", str(brief_dir))

        sentinel_file = (
            Path.home()
            / ".claude" / "hooks" / "_subrules" / "sharkitect"
            / "_test_capture_brief.py"
        )
        sentinel_file.write_text(
            "from _subrules.sharkitect._contract import SubRuleResult\n"
            "captured_brief = {'val': None}\n"
            "def check(prompt, ctx):\n"
            "    captured_brief['val'] = ctx.get('session_brief')\n"
            "    return SubRuleResult(mode='advisory', message='ok', "
            "rule_name='_test_capture_brief', bypass_keyword='skip cap')\n",
            encoding="utf-8",
        )
        try:
            cfg = write_dispatcher_config(
                tmp_path, enabled_subrules=["sharkitect._test_capture_brief"]
            )
            monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg))

            mod = _load_dispatcher()
            mod.run_dispatcher(prompt="anything")

            from _subrules.sharkitect import _test_capture_brief
            assert _test_capture_brief.captured_brief["val"] is not None
            assert "Build 6 v1.5" in _test_capture_brief.captured_brief["val"]
        finally:
            sentinel_file.unlink(missing_ok=True)

    def test_session_brief_tolerates_missing_file(self, tmp_path, monkeypatch):
        """If today's brief doesn't exist, session_brief is None (not crash)."""
        monkeypatch.setenv("SESSION_BRIEF_DIR", str(tmp_path / "nonexistent"))
        cfg = write_dispatcher_config(tmp_path, enabled_subrules=[])
        monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg))

        mod = _load_dispatcher()
        result = mod.run_dispatcher(prompt="anything")
        assert _ctx_text(result) == ""


# ===========================================================================
# Item 3 — Per-rule timeout
# ===========================================================================


class TestPerRuleTimeout:
    """A slow / hanging sub-rule MUST NOT block prompt processing. Dispatcher
    enforces a per-rule timeout; expired rules are logged + skipped; other
    rules continue.
    """

    def test_slow_subrule_times_out(self, tmp_path, monkeypatch):
        """A sub-rule that sleeps past the timeout is killed; dispatcher continues."""
        slow_file = (
            Path.home()
            / ".claude" / "hooks" / "_subrules" / "sharkitect"
            / "_test_slow.py"
        )
        slow_file.write_text(
            "import time\n"
            "from _subrules.sharkitect._contract import SubRuleResult\n"
            "def check(prompt, ctx):\n"
            "    time.sleep(2.0)\n"
            "    return SubRuleResult(mode='advisory', message='SHOULD_NOT_APPEAR', "
            "rule_name='_test_slow', bypass_keyword='skip slow')\n",
            encoding="utf-8",
        )
        try:
            cfg_path = tmp_path / "userpromptsubmit-dispatcher.json"
            cfg_path.write_text(json.dumps({
                "enabled_subrules": ["sharkitect._test_slow"],
                "log_dir": None,
                "subrule_timeout_seconds": 0.2,  # 200ms
            }))
            monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

            mod = _load_dispatcher()

            t0 = time.time()
            result = mod.run_dispatcher(prompt="anything")
            elapsed = time.time() - t0

            # The slow rule's message must NOT appear (timed out)
            assert "SHOULD_NOT_APPEAR" not in _ctx_text(result)
            # Dispatcher must return in well under the sub-rule's full sleep
            assert elapsed < 1.5, f"dispatcher took {elapsed:.2f}s; timeout did not fire"
        finally:
            slow_file.unlink(missing_ok=True)

    def test_timeout_does_not_block_other_subrules(self, tmp_path, monkeypatch):
        """Other sub-rules continue running after one times out."""
        slow_file = (
            Path.home()
            / ".claude" / "hooks" / "_subrules" / "sharkitect"
            / "_test_slow2.py"
        )
        slow_file.write_text(
            "import time\n"
            "from _subrules.sharkitect._contract import SubRuleResult\n"
            "def check(prompt, ctx):\n"
            "    time.sleep(2.0)\n"
            "    return None\n",
            encoding="utf-8",
        )
        try:
            cfg_path = tmp_path / "userpromptsubmit-dispatcher.json"
            cfg_path.write_text(json.dumps({
                "enabled_subrules": [
                    "sharkitect._test_slow2",
                    "sharkitect.verify_state",
                ],
                "log_dir": None,
                "subrule_timeout_seconds": 0.2,
            }))
            monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

            mod = _load_dispatcher()
            result = mod.run_dispatcher(prompt="is the migration done?")
            # verify_state should STILL fire even though _test_slow2 timed out
            assert "verify" in _ctx_text(result).lower()
        finally:
            slow_file.unlink(missing_ok=True)

    def test_timeout_is_logged_to_fire_log(self, tmp_path, monkeypatch):
        """Timeout events land in hook-fire-log.jsonl with outcome='timeout'."""
        slow_file = (
            Path.home()
            / ".claude" / "hooks" / "_subrules" / "sharkitect"
            / "_test_slow3.py"
        )
        slow_file.write_text(
            "import time\n"
            "from _subrules.sharkitect._contract import SubRuleResult\n"
            "def check(prompt, ctx):\n"
            "    time.sleep(2.0)\n"
            "    return None\n",
            encoding="utf-8",
        )
        try:
            cfg_path = tmp_path / "userpromptsubmit-dispatcher.json"
            cfg_path.write_text(json.dumps({
                "enabled_subrules": ["sharkitect._test_slow3"],
                "log_dir": None,
                "subrule_timeout_seconds": 0.15,
            }))
            monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))
            log_path = tmp_path / "hook-fire-log.jsonl"
            monkeypatch.setenv("HOOK_FIRE_LOG_PATH", str(log_path))

            mod = _load_dispatcher()
            mod.run_dispatcher(prompt="anything")

            assert log_path.exists()
            records = [json.loads(line) for line in log_path.read_text().splitlines()]
            timeout_records = [r for r in records if r.get("outcome") == "timeout"]
            assert len(timeout_records) >= 1, (
                f"expected a timeout outcome record; got records: {records!r}"
            )
            assert timeout_records[0]["subrule"] == "sharkitect._test_slow3"
        finally:
            slow_file.unlink(missing_ok=True)

    def test_timeout_default_is_500ms_when_unconfigured(self, tmp_path, monkeypatch):
        """When config omits subrule_timeout_seconds, default is 0.5s."""
        cfg_path = tmp_path / "userpromptsubmit-dispatcher.json"
        cfg_path.write_text(json.dumps({
            "enabled_subrules": [],
            "log_dir": None,
            # subrule_timeout_seconds intentionally omitted
        }))
        monkeypatch.setenv("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(cfg_path))

        mod = _load_dispatcher()
        # Expose default via module constant so tests can assert
        assert mod.DEFAULT_SUBRULE_TIMEOUT_SECONDS == 0.5


# Need importlib at runtime (used inside one test above)
import importlib  # noqa: E402
