"""Tests for using-sharkitect-methodology meta-skill content invariants.

Source: Cluster A plan Task 1, docs/superpowers/specs/2026-05-12-methodology-gate-cluster-a-design.md
"""
import re
from pathlib import Path

import pytest


SKILL_DIR = Path.home() / ".claude" / "skills" / "using-sharkitect-methodology"
SKILL_MD = SKILL_DIR / "SKILL.md"
SKILL_CATALOG_MD = SKILL_DIR / "references" / "skill-catalog.md"
STRATEGY_RULES_MD = SKILL_DIR / "references" / "strategy-creation-rules.md"


def test_skill_md_exists():
    assert SKILL_MD.is_file(), f"SKILL.md missing at {SKILL_MD}"


def test_skill_md_has_valid_frontmatter():
    content = SKILL_MD.read_text(encoding="utf-8")
    assert content.startswith("---\n"), "frontmatter must start at line 1"
    parts = content.split("---", 2)
    assert len(parts) >= 3, "frontmatter must have opening and closing ---"
    fm = parts[1]
    assert re.search(r"^name:\s*using-sharkitect-methodology\b", fm, re.M), \
        "name must be using-sharkitect-methodology"
    assert re.search(r"^description:.+", fm, re.M), "description required"


def test_skill_description_mentions_methodology_skills():
    content = SKILL_MD.read_text(encoding="utf-8")
    fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    assert fm_match, "frontmatter must be parseable"
    desc = fm_match.group(1)
    assert "methodology" in desc.lower(), "description must mention methodology"
    assert any(s in desc.lower() for s in ["pricing-strategy", "marketing-strategy-pmm", "smb-cfo"]), \
        "description must name at least one canonical Sharkitect methodology skill"


def test_skill_has_anti_rationalization_clause():
    content = SKILL_MD.read_text(encoding="utf-8")
    assert "EXTREMELY-IMPORTANT" in content or "extremely important" in content.lower(), \
        "anti-rationalization clause requires EXTREMELY-IMPORTANT block"
    assert "1%" in content, "1% chance rule required (matches using-superpowers pattern)"
    assert "not negotiable" in content.lower() or "you do not have a choice" in content.lower(), \
        "anti-rationalization assertion language required"


def test_skill_lists_canonical_sharkitect_methodology_skills():
    content = SKILL_MD.read_text(encoding="utf-8")
    required_skills = [
        "pricing-strategy",
        "marketing-strategy-pmm",
        "smb-cfo",
        "hq-revenue-ops",
        "executing-plans",
    ]
    for skill in required_skills:
        assert skill in content, f"meta-skill must catalog {skill}"


def test_references_skill_catalog_exists():
    assert SKILL_CATALOG_MD.is_file(), f"references/skill-catalog.md missing at {SKILL_CATALOG_MD}"


def test_references_strategy_creation_rules_exists():
    assert STRATEGY_RULES_MD.is_file(), f"references/strategy-creation-rules.md missing at {STRATEGY_RULES_MD}"


def test_skill_md_line_count_under_250():
    """Mirrors the FULL skill rule from MEMORY.md: companion file split keeps SKILL.md scannable."""
    content = SKILL_MD.read_text(encoding="utf-8")
    lines = content.split("\n")
    assert len(lines) < 250, f"SKILL.md should be < 250 lines (got {len(lines)}); use companion files for detail"
