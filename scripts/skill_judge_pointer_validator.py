"""
H4 hybrid pointer-vs-prose validator.

H1 (line-class ratio): classify each non-empty line as header / list-item /
citation / prose. If prose-line ratio of non-header lines exceeds threshold,
fail H1.

H2 (cross-reference density): require >=1 K1 citation per N non-header lines.

H3 escalation: when H1 + H2 disagree OR when result is borderline, the caller
(skill-judge) should escalate to an AI-judge pass with K1 SoT loaded for
side-by-side comparison.

Pure stdlib. ASCII-only.
"""
import re
from dataclasses import dataclass, field
from typing import Dict, List

# Tunable thresholds
PROSE_RATIO_THRESHOLD = 0.40         # prose lines / non-header lines, fail if >= this
MIN_CITATIONS_PER_LINES = 30         # require >=1 citation per N non-header lines

CITATION_RE = re.compile(r"`?(?:[A-Za-z0-9_./\\-]*knowledge-base/[A-Za-z0-9_./\\-]+\.md)`?")
HEADER_RE = re.compile(r"^#{1,6}\s+\S")
LIST_RE = re.compile(r"^\s*([-*+]|\d+\.)\s+\S")
TABLE_RE = re.compile(r"^\s*\|")


@dataclass
class Verdict:
    classification: str  # POINTER | BORDERLINE | PROSE
    passes_h1: bool
    passes_h2: bool
    escalation_recommended: bool
    line_class_counts: Dict = field(default_factory=dict)
    citation_count: int = 0
    reasons: List = field(default_factory=list)


def _classify_line(line: str) -> str:
    s = line.strip()
    if not s:
        return "blank"
    if HEADER_RE.match(line):
        return "header"
    if LIST_RE.match(line):
        return "list"
    if TABLE_RE.match(line):
        return "table"
    if CITATION_RE.search(line) and len(s) < 200:
        return "citation"
    return "prose"


def classify(text: str) -> Verdict:
    counts = {"header": 0, "list": 0, "citation": 0, "table": 0, "prose": 0, "blank": 0}
    for line in text.splitlines():
        counts[_classify_line(line)] += 1
    non_header = sum(v for k, v in counts.items() if k not in {"header", "blank"})
    prose_ratio = (counts["prose"] / non_header) if non_header else 0.0
    citation_count = len(CITATION_RE.findall(text))
    passes_h1 = prose_ratio < PROSE_RATIO_THRESHOLD
    passes_h2 = non_header == 0 or citation_count >= max(1, non_header // MIN_CITATIONS_PER_LINES)
    reasons = []
    if not passes_h1:
        reasons.append(f"H1 FAIL: prose_ratio={prose_ratio:.2f} >= {PROSE_RATIO_THRESHOLD}")
    if not passes_h2:
        reasons.append(f"H2 FAIL: only {citation_count} citation(s) across {non_header} non-header lines")
    if passes_h1 and passes_h2:
        cls = "POINTER"
        esc = False
    elif passes_h1 != passes_h2:
        cls = "BORDERLINE"
        esc = True
    else:
        cls = "PROSE"
        esc = False
    return Verdict(
        classification=cls,
        passes_h1=passes_h1,
        passes_h2=passes_h2,
        escalation_recommended=esc,
        line_class_counts=counts,
        citation_count=citation_count,
        reasons=reasons,
    )
