# ~/.claude/tests/test_stale_pointer_nudge.py
"""Tests for stale-pointer-nudge.py PostToolUse Read advisory."""
import importlib.util
import sys
from pathlib import Path

HOOK_PATH = Path.home() / ".claude" / "hooks" / "stale-pointer-nudge.py"


def _load():
    spec = importlib.util.spec_from_file_location("spn", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_hook_file_exists():
    assert HOOK_PATH.exists()


def test_no_nudge_on_non_skill_ref_read(tmp_path):
    spn = _load()
    payload = {"tool_name": "Read", "tool_input": {"file_path": str(tmp_path / "random.md")}}
    r = spn.evaluate(payload)
    assert r.additional_context is None


def test_nudge_on_skill_ref_companion_with_superseded_pointer(tmp_path, monkeypatch):
    spn = _load()
    # Build fake skill-ref pointing to a fake K1 SoT with status: superseded
    k1 = tmp_path / "knowledge-base" / "revenue" / "old.md"
    k1.parent.mkdir(parents=True)
    k1.write_text("---\nstatus: SUPERSEDED\nsuperseded_by: knowledge-base/revenue/new.md\n---\n", encoding="utf-8")
    ref = tmp_path / ".claude" / "skills" / "demo" / "references" / "x.md"
    ref.parent.mkdir(parents=True)
    ref.write_text(f"Cites `{k1}` v1.0\n", encoding="utf-8")
    payload = {"tool_name": "Read", "tool_input": {"file_path": str(ref)}}
    r = spn.evaluate(payload, k1_search_root=tmp_path)
    assert r.additional_context is not None
    assert "superseded" in r.additional_context.lower()
    assert "new.md" in r.additional_context.lower()


def test_nudge_on_missing_k1_path(tmp_path):
    spn = _load()
    ref = tmp_path / ".claude" / "skills" / "demo" / "references" / "x.md"
    ref.parent.mkdir(parents=True)
    ref.write_text("Cites `knowledge-base/revenue/does-not-exist.md` v9.9\n", encoding="utf-8")
    payload = {"tool_name": "Read", "tool_input": {"file_path": str(ref)}}
    r = spn.evaluate(payload, k1_search_root=tmp_path)
    assert r.additional_context is not None
    assert "missing" in r.additional_context.lower() or "not found" in r.additional_context.lower()


def test_no_nudge_on_active_k1(tmp_path):
    spn = _load()
    k1 = tmp_path / "knowledge-base" / "revenue" / "active.md"
    k1.parent.mkdir(parents=True)
    k1.write_text("---\nstatus: APPROVED\nversion: 1.0\n---\n", encoding="utf-8")
    ref = tmp_path / ".claude" / "skills" / "demo" / "references" / "x.md"
    ref.parent.mkdir(parents=True)
    ref.write_text(f"Cites `{k1}` v1.0\n", encoding="utf-8")
    payload = {"tool_name": "Read", "tool_input": {"file_path": str(ref)}}
    r = spn.evaluate(payload, k1_search_root=tmp_path)
    assert r.additional_context is None


def test_bypass_skip_stale_pointer(tmp_path):
    spn = _load()
    ref = tmp_path / ".claude" / "skills" / "demo" / "references" / "x.md"
    ref.parent.mkdir(parents=True)
    ref.write_text("skip stale-pointer\nCites `knowledge-base/revenue/missing.md`\n", encoding="utf-8")
    payload = {"tool_name": "Read", "tool_input": {"file_path": str(ref)}}
    r = spn.evaluate(payload, k1_search_root=tmp_path)
    assert r.additional_context is None
