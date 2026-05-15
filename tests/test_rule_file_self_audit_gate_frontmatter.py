# ~/.claude/tests/test_rule_file_self_audit_gate_frontmatter.py
"""Tests for frontmatter-completeness check integrated into rule-file-self-audit-gate.py."""
import sys
from pathlib import Path

HOOK_DIR = Path.home() / ".claude" / "hooks"
sys.path.insert(0, str(HOOK_DIR))
import importlib.util
spec = importlib.util.spec_from_file_location("rfsg", HOOK_DIR / "rule-file-self-audit-gate.py")
rfsg = importlib.util.module_from_spec(spec); spec.loader.exec_module(rfsg)


def _payload(path: str, content: str = "") -> dict:
    return {"tool_name": "Write", "tool_input": {"file_path": path, "content": content}}


def test_k1_sot_missing_frontmatter_surfaces_checklist(tmp_path):
    fake = tmp_path / "knowledge-base" / "revenue" / "pricing-structure.md"
    fake.parent.mkdir(parents=True)
    fake.write_text("# No frontmatter here\n\nbody only.\n", encoding="utf-8")
    result = rfsg.evaluate(_payload(str(fake), fake.read_text(encoding="utf-8")))
    assert result.additional_context is not None
    # The "missing required frontmatter field" string is ONLY emitted by _frontmatter_findings()
    # - not present in any checklist text. This assertion fails if the helper is not wired.
    assert "missing required frontmatter field" in result.additional_context.lower()
    # And specifically name at least one concrete required field that's missing
    assert ("document" in result.additional_context.lower()
            or "classification" in result.additional_context.lower()
            or "approved_by" in result.additional_context.lower())

def test_k1_sot_with_complete_frontmatter_no_completeness_flag(tmp_path):
    fake = tmp_path / "knowledge-base" / "revenue" / "x.md"
    fake.parent.mkdir(parents=True)
    fm = (
        "---\ndocument: x\nclassification: K1\nowner: hq\n"
        "approved_by: chris\napproved_date: 2026-05-15\n"
        "version: 1.0\nstatus: APPROVED\nlast_updated: 2026-05-15\n"
        "last_updated_by: chris\nprevious_versions: initial\n---\n\nbody\n"
    )
    fake.write_text(fm, encoding="utf-8")
    result = rfsg.evaluate(_payload(str(fake), fake.read_text(encoding="utf-8")))
    if result.additional_context:
        assert "missing required frontmatter field" not in result.additional_context.lower()

def test_superseded_without_pointer_flagged(tmp_path):
    fake = tmp_path / "knowledge-base" / "revenue" / "y.md"
    fake.parent.mkdir(parents=True)
    fm = (
        "---\ndocument: y\nclassification: K1\nowner: hq\n"
        "approved_by: chris\napproved_date: 2026-05-15\n"
        "version: 2.0\nstatus: SUPERSEDED\nlast_updated: 2026-05-15\n"
        "last_updated_by: chris\nprevious_versions: v1\n---\n\nbody\n"
    )
    fake.write_text(fm, encoding="utf-8")
    result = rfsg.evaluate(_payload(str(fake), fake.read_text(encoding="utf-8")))
    assert result.additional_context is not None
    # "status=SUPERSEDED requires field" is ONLY emitted by _frontmatter_findings()
    # - fails if the helper or its conditional_required branch is not wired
    assert "status=superseded requires field" in result.additional_context.lower()
    assert "superseded_by" in result.additional_context.lower()

def test_skill_ref_companion_class_matches(tmp_path):
    fake = tmp_path / ".claude" / "skills" / "demo" / "references" / "x.md"
    fake.parent.mkdir(parents=True)
    fake.write_text("# pointer\n", encoding="utf-8")
    result = rfsg.evaluate(_payload(str(fake), fake.read_text(encoding="utf-8")))
    assert result.additional_context is not None
    assert "skill-ref-companion" in result.additional_context.lower() or "skill ref" in result.additional_context.lower()

def test_brain_dump_class_matches(tmp_path):
    fake = tmp_path / "brain-dump" / "2026-05-15-test.md"
    fake.parent.mkdir(parents=True)
    fake.write_text("body only\n", encoding="utf-8")
    result = rfsg.evaluate(_payload(str(fake), fake.read_text(encoding="utf-8")))
    assert result.additional_context is not None
    assert "brain-dump" in result.additional_context.lower() or "brain dump" in result.additional_context.lower()

def test_bypass_skip_rule_self_audit_short_circuits(tmp_path):
    fake = tmp_path / "knowledge-base" / "x.md"
    fake.parent.mkdir(parents=True)
    fake.write_text("body\n", encoding="utf-8")
    payload = _payload(str(fake), "skip rule-self-audit\nbody")
    result = rfsg.evaluate(payload)
    # When bypass fires, evaluate() returns additional_context=None -- strict assertion
    assert result.additional_context is None
