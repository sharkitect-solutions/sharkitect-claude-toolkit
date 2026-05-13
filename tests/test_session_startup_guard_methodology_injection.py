"""Tests for session-startup-guard.py injection of using-sharkitect-methodology meta-skill.

Source: Cluster A plan Task 2, docs/superpowers/specs/2026-05-12-methodology-gate-cluster-a-design.md
NOTE: Plan referenced ~/.claude/scripts/ — actual path is ~/.claude/hooks/.
"""
import importlib.util
import sys
from pathlib import Path

import pytest


GUARD_PATH = Path.home() / ".claude" / "hooks" / "session-startup-guard.py"
SKILL_MD = Path.home() / ".claude" / "skills" / "using-sharkitect-methodology" / "SKILL.md"


def _load_guard():
    """Load session-startup-guard.py as a module from its file path."""
    spec = importlib.util.spec_from_file_location("session_startup_guard", GUARD_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_startup_guard"] = module
    spec.loader.exec_module(module)
    return module


def test_guard_module_loads():
    """Sanity: the script imports as a module without side effects."""
    module = _load_guard()
    assert module is not None


def test_inject_method_exists():
    """The injection method must exist."""
    module = _load_guard()
    assert hasattr(module, "_inject_sharkitect_methodology_meta_skill"), \
        "session-startup-guard.py must define _inject_sharkitect_methodology_meta_skill"


def test_skill_path_constant_exists():
    """The module exposes the SKILL.md path constant for testability."""
    module = _load_guard()
    assert hasattr(module, "SHARKITECT_METHODOLOGY_SKILL_PATH"), \
        "module must expose SHARKITECT_METHODOLOGY_SKILL_PATH constant"


def test_injection_returns_skill_content_wrapped_in_extremely_important():
    """The injection method returns the SKILL.md content wrapped in <EXTREMELY_IMPORTANT>."""
    module = _load_guard()
    result = module._inject_sharkitect_methodology_meta_skill()
    assert result is not None, "injection returned None despite SKILL.md existing"
    assert "<EXTREMELY_IMPORTANT>" in result, "injection must wrap content in EXTREMELY_IMPORTANT"
    assert "using-sharkitect-methodology" in result, "injected content must reference the meta-skill name"
    assert "1%" in result, "anti-rationalization clause must survive injection"


def test_injection_handles_missing_skill_file_gracefully(monkeypatch, tmp_path):
    """If SKILL.md is missing, return None — never raise."""
    fake_skill_path = tmp_path / "nonexistent" / "SKILL.md"
    module = _load_guard()
    monkeypatch.setattr(module, "SHARKITECT_METHODOLOGY_SKILL_PATH", fake_skill_path)
    try:
        result = module._inject_sharkitect_methodology_meta_skill()
        assert result is None or result == "", \
            f"missing skill file should return None or empty, got: {type(result).__name__}"
    except Exception as e:
        pytest.fail(f"injection method raised on missing skill file: {e}")
