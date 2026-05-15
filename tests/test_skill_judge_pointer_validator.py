# ~/.claude/tests/test_skill_judge_pointer_validator.py
"""H4 hybrid pointer-vs-prose validator tests."""
import importlib.util
from pathlib import Path

MOD = Path.home() / ".claude" / "scripts" / "skill_judge_pointer_validator.py"


def _load():
    spec = importlib.util.spec_from_file_location("sjpv", MOD)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_module_exists():
    assert MOD.exists()


def test_classify_pure_pointer_passes_h1():
    m = _load()
    pointer = (
        "# Title (Pointer Doc)\n\n## Section\n\n"
        "**K1 SoT:** `knowledge-base/x.md` v1.0\n\n"
        "- Bullet 1 citing `knowledge-base/x.md` v1.0\n"
        "- Bullet 2 citing `knowledge-base/x.md` v1.0\n"
    )
    verdict = m.classify(pointer)
    assert verdict.passes_h1 is True
    assert verdict.passes_h2 is True
    assert verdict.classification == "POINTER"


def test_classify_canonical_prose_fails_h1():
    m = _load()
    prose = (
        "# Title\n\n"
        + "\n".join([f"This is canonical prose line {i} encoding policy details." for i in range(40)])
    )
    v = m.classify(prose)
    assert v.passes_h1 is False
    assert v.classification in {"PROSE", "BORDERLINE"}


def test_classify_low_citation_density_fails_h2():
    m = _load()
    text = (
        "# Title\n\n"
        + "\n".join([f"- bullet {i} without citation" for i in range(40)])
    )
    v = m.classify(text)
    assert v.passes_h1 is True   # bullets pass line-class
    assert v.passes_h2 is False  # no citations
    assert v.classification == "BORDERLINE"  # needs H3 escalation


def test_borderline_flags_for_h3_escalation():
    m = _load()
    text = (
        "# Title\n\n"
        + "\n".join([f"- bullet {i} citing `knowledge-base/x.md` v1.0" for i in range(15)])
        + "\n"
        + "\n".join([f"Some explanatory prose line {i}." for i in range(10)])
    )
    v = m.classify(text)
    # Mixed: should land BORDERLINE asking for H3 escalation
    assert v.classification in {"POINTER", "BORDERLINE"}
    if v.classification == "BORDERLINE":
        assert v.escalation_recommended is True


def test_threshold_constants_documented():
    m = _load()
    assert hasattr(m, "PROSE_RATIO_THRESHOLD")
    assert hasattr(m, "MIN_CITATIONS_PER_LINES")
    assert isinstance(m.PROSE_RATIO_THRESHOLD, float)
    assert 0.0 < m.PROSE_RATIO_THRESHOLD < 1.0


def test_status_field_in_verdict():
    m = _load()
    v = m.classify("# Title\n\n- citation `knowledge-base/x.md`\n")
    assert v.classification in {"POINTER", "BORDERLINE", "PROSE"}
    assert hasattr(v, "line_class_counts")
    assert hasattr(v, "citation_count")
