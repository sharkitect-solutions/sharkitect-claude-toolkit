# ~/.claude/tests/test_drift_detection_companion_extension.py
"""Tests for drift-detection-hook.py companion prose-density extension."""
import importlib.util
import sys
from pathlib import Path

HOOK = Path.home() / ".claude" / "hooks" / "drift-detection-hook.py"


def _load():
    spec = importlib.util.spec_from_file_location("ddh", HOOK)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_function_exists():
    m = _load()
    assert hasattr(m, "check_companion_prose_density")


def test_pointer_companion_returns_none():
    m = _load()
    text = "# Title\n\n- bullet citing `knowledge-base/x.md`\n"
    assert m.check_companion_prose_density("/x/.claude/skills/demo/references/x.md", text) is None


def test_prose_companion_returns_finding():
    m = _load()
    text = "# T\n\n" + "\n".join([f"Long prose line {i}." for i in range(50)])
    finding = m.check_companion_prose_density("/x/.claude/skills/demo/references/x.md", text)
    assert finding is not None
    assert "prose" in finding.lower()


def test_non_companion_path_returns_none():
    m = _load()
    text = "# T\n\n" + "\n".join([f"Long prose line {i}." for i in range(50)])
    assert m.check_companion_prose_density("/x/random.md", text) is None
