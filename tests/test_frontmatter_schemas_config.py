# ~/.claude/tests/test_frontmatter_schemas_config.py
"""Tests for ~/.claude/config/frontmatter-schemas.json structure + loader."""
import json
from pathlib import Path

import pytest

CONFIG_PATH = Path.home() / ".claude" / "config" / "frontmatter-schemas.json"

def _load():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

def test_config_file_exists():
    assert CONFIG_PATH.exists(), f"missing config file: {CONFIG_PATH}"

def test_config_has_classes_array():
    cfg = _load()
    assert "classes" in cfg and isinstance(cfg["classes"], list) and len(cfg["classes"]) >= 4

def test_each_class_has_required_keys():
    cfg = _load()
    required = {"file_class_name", "globs", "required_fields"}
    for cls in cfg["classes"]:
        missing = required - cls.keys()
        assert not missing, f"class {cls.get('file_class_name')} missing keys: {missing}"

def test_k1_sot_schema_has_versioning_fields():
    cfg = _load()
    k1 = next(c for c in cfg["classes"] if c["file_class_name"] == "k1-sot")
    must_have = {"document", "classification", "owner", "version", "status", "last_updated", "previous_versions"}
    assert must_have.issubset(set(k1["required_fields"]))

def test_skill_ref_companion_schema_pointer_aware():
    cfg = _load()
    sr = next(c for c in cfg["classes"] if c["file_class_name"] == "skill-ref-companion")
    assert {"status", "last_rebuilt", "reason"}.issubset(set(sr["required_fields"]))

def test_plan_file_schema():
    cfg = _load()
    pf = next(c for c in cfg["classes"] if c["file_class_name"] == "plan-file")
    assert {"status", "created", "last_updated"}.issubset(set(pf["required_fields"]))

def test_brain_dump_schema():
    cfg = _load()
    bd = next(c for c in cfg["classes"] if c["file_class_name"] == "brain-dump")
    assert {"date", "session_context", "status", "relates_to", "priority"}.issubset(set(bd["required_fields"]))

def test_status_enum_for_versioned_docs():
    cfg = _load()
    k1 = next(c for c in cfg["classes"] if c["file_class_name"] == "k1-sot")
    assert "status_enum" in k1
    assert set(k1["status_enum"]) == {"DRAFT", "APPROVED", "SUPERSEDED", "DEPRECATED"}

def test_superseded_requires_pointer():
    cfg = _load()
    k1 = next(c for c in cfg["classes"] if c["file_class_name"] == "k1-sot")
    cr = k1.get("conditional_required", {})
    assert cr.get("when_status_superseded") == ["superseded_by", "superseded_date", "superseded_reason"]
