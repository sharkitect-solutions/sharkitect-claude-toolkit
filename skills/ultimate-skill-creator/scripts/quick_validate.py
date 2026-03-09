#!/usr/bin/env python3
"""
Ultimate Skill Creator — Skill Validator

Validates a skill against the ultimate-skill-creator's quality standards:
  - Structural checks (frontmatter, required fields, naming)
  - CSO enforcement (trigger-only descriptions, no summaries)
  - Body quality checks (word count, required sections, hedging)
  - Completeness checks (file index, referenced files exist)

Usage:
    python quick_validate.py <skill-directory> [--strict] [--fix-hints]

Exit codes:
    0 = all checks pass
    1 = errors found (skill is broken)
    2 = warnings only (skill works but has quality issues)
"""

import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUMMARY_INDICATORS = [
    "implements", "provides", "covers", "offers", "delivers",
    "this skill", "this covers", "including", "such as",
    "three-stage", "multi-step", "with patterns for", "with support for",
]

HEDGING_WORDS = [
    r"\bmight\b", r"\bcould\b", r"\bperhaps\b", r"\bpossibly\b",
    r"\byou may want to\b", r"\bconsider\b", r"\byou should consider\b",
    r"\bit might be helpful\b", r"\byou could try\b",
]

REQUIRED_BODY_SECTIONS = {
    "rationalization": r"##\s.*[Rr]ationalization",
    "red_flags": r"##\s.*[Rr]ed\s*[Ff]lag",
    "file_index": r"##\s.*[Ff]ile\s*[Ii]ndex",
}

DESC_MIN_WORDS = 80
DESC_MAX_WORDS = 250
BODY_MIN_WORDS = 1200
BODY_TARGET_MAX = 2000
BODY_HARD_MAX = 2500


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def count_words(text: str) -> int:
    return len(text.split())


def extract_frontmatter(content: str) -> tuple[str | None, str]:
    """Return (frontmatter_text, body_text). frontmatter_text is None if missing."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, content
    body_start = match.end()
    return match.group(1), content[body_start:]


def extract_field(frontmatter: str, field: str) -> str | None:
    """Extract a YAML field value, handling folded block scalars (>)."""
    # Try folded/literal block scalar first
    pattern = rf"^{field}:\s*[>|]\s*\n((?:[ \t]+.+\n?)+)"
    m = re.search(pattern, frontmatter, re.MULTILINE)
    if m:
        lines = m.group(1).split("\n")
        return " ".join(line.strip() for line in lines if line.strip())

    # Try inline value
    m = re.search(rf"^{field}:\s*(.+)", frontmatter, re.MULTILINE)
    if m:
        val = m.group(1).strip().strip("\"'")
        return val if val else None

    return None


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []
        self.fix_hints: list[str] = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def error(self, msg: str, hint: str = ""):
        self.errors.append(msg)
        if hint:
            self.fix_hints.append(f"  FIX: {hint}")

    def warn(self, msg: str, hint: str = ""):
        self.warnings.append(msg)
        if hint:
            self.fix_hints.append(f"  TIP: {hint}")

    def ok(self, msg: str):
        self.info.append(msg)


def validate_skill(skill_path: str | Path) -> tuple[bool, str, ValidationResult]:
    """
    Full validation of a skill directory.

    Returns:
        (passed, summary_message, detailed_result)
    """
    result = ValidationResult()
    skill_path = Path(skill_path).resolve()

    # ------------------------------------------------------------------
    # 1. Structure checks
    # ------------------------------------------------------------------

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        result.error("SKILL.md not found", "Create SKILL.md with YAML frontmatter")
        return False, "SKILL.md not found", result

    content = skill_md.read_text(encoding="utf-8")
    frontmatter_text, body = extract_frontmatter(content)

    if frontmatter_text is None:
        result.error("No YAML frontmatter (--- delimiters) found",
                      "Add ---\\nname: ...\\ndescription: >\\n  ...\\n--- at the top")
        return False, "No frontmatter", result

    result.ok("SKILL.md exists with frontmatter")

    # ------------------------------------------------------------------
    # 2. Name validation
    # ------------------------------------------------------------------

    name = extract_field(frontmatter_text, "name")
    if not name:
        result.error("Missing 'name' field in frontmatter")
    else:
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            result.error(f"Name '{name}' is not valid kebab-case",
                          "Use lowercase letters, digits, single hyphens: my-skill-name")
        elif name != skill_path.name:
            result.warn(f"Name '{name}' doesn't match directory '{skill_path.name}'",
                         f"Rename directory to '{name}' or update the name field")
        else:
            result.ok(f"Name '{name}' is valid kebab-case and matches directory")

    # ------------------------------------------------------------------
    # 3. Description / CSO validation
    # ------------------------------------------------------------------

    description = extract_field(frontmatter_text, "description")
    if not description:
        result.error("Missing 'description' field in frontmatter")
    else:
        desc_words = count_words(description)

        # Word count
        if desc_words < DESC_MIN_WORDS:
            result.warn(f"Description is {desc_words} words (target: {DESC_MIN_WORDS}-{DESC_MAX_WORDS})",
                         "Add more 'Use when...' trigger conditions")
        elif desc_words > DESC_MAX_WORDS:
            result.warn(f"Description is {desc_words} words (target: {DESC_MIN_WORDS}-{DESC_MAX_WORDS})",
                         "Trim to essential trigger conditions only")
        else:
            result.ok(f"Description word count: {desc_words} (within {DESC_MIN_WORDS}-{DESC_MAX_WORDS} target)")

        # CSO: Check for "Use when" pattern
        sentences = [s.strip() for s in re.split(r"(?<=[.!])\s+", description) if s.strip()]
        non_trigger = []
        for s in sentences:
            s_lower = s.lower()
            if not (s_lower.startswith("use when") or
                    s_lower.startswith("use for") or
                    s_lower.startswith("keywords:") or
                    s_lower.startswith("this skill applies")):
                non_trigger.append(s)

        if non_trigger:
            result.error(
                f"CSO violation: {len(non_trigger)} sentence(s) don't start with 'Use when'",
                "Every sentence must start with 'Use when...' — descriptions are trigger conditions ONLY"
            )
            for s in non_trigger[:3]:  # Show first 3
                result.errors.append(f"  Offending: \"{s[:80]}...\"" if len(s) > 80 else f"  Offending: \"{s}\"")

        # CSO: Check for summary indicators
        desc_lower = description.lower()
        found_summaries = [word for word in SUMMARY_INDICATORS if word in desc_lower]
        if found_summaries:
            result.warn(
                f"Description may contain summary language: {', '.join(found_summaries)}",
                "Remove workflow summaries. Only describe WHEN the skill should trigger, not WHAT it does."
            )

        if not non_trigger and not found_summaries:
            result.ok("Description follows CSO rules (trigger-only format)")

    # ------------------------------------------------------------------
    # 4. Body quality checks
    # ------------------------------------------------------------------

    body_words = count_words(body)

    if body_words < BODY_MIN_WORDS:
        result.warn(f"Body is {body_words} words (target: {BODY_MIN_WORDS}-{BODY_TARGET_MAX})",
                     "Add rationalization table, rules with 'why', and red flags checklist")
    elif body_words > BODY_HARD_MAX:
        result.error(f"Body is {body_words} words (hard limit: {BODY_HARD_MAX})",
                      "Move implementation details to references/ files")
    elif body_words > BODY_TARGET_MAX:
        result.warn(f"Body is {body_words} words (target max: {BODY_TARGET_MAX})",
                     "Consider moving some content to references/ files")
    else:
        result.ok(f"Body word count: {body_words} (within target)")

    # Required sections
    for section_name, pattern in REQUIRED_BODY_SECTIONS.items():
        if re.search(pattern, body):
            result.ok(f"Found required section: {section_name}")
        else:
            label = section_name.replace("_", " ").title()
            result.warn(f"Missing recommended section: {label}",
                         f"Add a '## {label}' section — see the skill template for format")

    # Hedging language — skip lines that are quoting bad patterns (red flags, examples)
    body_lines = body.split("\n")
    prose_lines = [
        line for line in body_lines
        if not line.strip().startswith("- [ ]")  # Red flags checklist items
        and not line.strip().startswith("|")       # Table rows (rationalization examples)
        and '("' not in line                       # Quoted examples
        and "WRONG" not in line                    # Wrong-pattern labels
    ]
    prose_body = "\n".join(prose_lines)

    hedging_found = []
    for pattern in HEDGING_WORDS:
        matches = re.findall(pattern, prose_body, re.IGNORECASE)
        hedging_found.extend(matches)
    if hedging_found:
        unique = list(set(h.lower() for h in hedging_found))
        result.warn(
            f"Hedging language found ({len(hedging_found)}x): {', '.join(unique[:5])}",
            "Replace with imperative voice: 'Do X' not 'You might consider X'"
        )
    else:
        result.ok("No hedging language detected")

    # Rationalization table row count
    table_rows = re.findall(r"^\|[^|]+\|[^|]+\|[^|]+\|$", body, re.MULTILINE)
    # Subtract header and separator rows
    data_rows = [r for r in table_rows if not re.match(r"^\|\s*-+", r) and
                 not re.match(r"^\|\s*Rationalization", r, re.IGNORECASE)]
    if data_rows:
        if len(data_rows) < 4:
            result.warn(f"Rationalization table has {len(data_rows)} rows (minimum: 4)",
                         "Add more rationalizations from pressure testing")
        else:
            result.ok(f"Rationalization table has {len(data_rows)} rows")

    # Red flags count
    red_flags = re.findall(r"^- \[ \]", body, re.MULTILINE)
    if red_flags:
        if len(red_flags) < 5:
            result.warn(f"Red flags checklist has {len(red_flags)} items (minimum: 5)",
                         "Add more specific, scannable red flag patterns")
        else:
            result.ok(f"Red flags checklist has {len(red_flags)} items")

    # ------------------------------------------------------------------
    # 5. File index / referenced files
    # ------------------------------------------------------------------

    # Check if file index references files that actually exist
    file_refs = re.findall(r"`((?:references|scripts|examples|assets)/[^\s`]+)`", body)
    missing_files = []
    for ref in file_refs:
        ref_path = skill_path / ref
        if not ref_path.exists():
            missing_files.append(ref)

    if missing_files:
        result.error(
            f"{len(missing_files)} referenced file(s) not found: {', '.join(missing_files)}",
            "Create the missing files or remove the references"
        )
    elif file_refs:
        result.ok(f"All {len(file_refs)} referenced files exist")

    # ------------------------------------------------------------------
    # 6. Evals check
    # ------------------------------------------------------------------

    evals_file = skill_path / "evals.json"
    if evals_file.exists():
        try:
            evals = json.loads(evals_file.read_text(encoding="utf-8"))
            cases = evals.get("test_cases", [])
            if len(cases) < 10:
                result.warn(f"evals.json has {len(cases)} test cases (minimum: 10)",
                             "Add more should-trigger, should-NOT-trigger, and pressure test cases")
            else:
                result.ok(f"evals.json has {len(cases)} test cases")
        except json.JSONDecodeError:
            result.error("evals.json contains invalid JSON")
    else:
        result.warn("No evals.json found",
                     "Create evals.json with test cases — testing is non-negotiable")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    if result.errors:
        summary = f"FAIL — {len(result.errors)} error(s), {len(result.warnings)} warning(s)"
    elif result.warnings:
        summary = f"PASS with {len(result.warnings)} warning(s)"
    else:
        summary = "PASS — all checks clean"

    return result.passed, summary, result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_report(result: ValidationResult, summary: str, show_hints: bool = False):
    """Print a formatted validation report."""
    print()

    if result.errors:
        print("ERRORS:")
        for e in result.errors:
            print(f"  x {e}")
        print()

    if result.warnings:
        print("WARNINGS:")
        for w in result.warnings:
            print(f"  ! {w}")
        print()

    if result.info:
        print("PASSED:")
        for i in result.info:
            print(f"  + {i}")
        print()

    if show_hints and result.fix_hints:
        print("HOW TO FIX:")
        for h in result.fix_hints:
            print(h)
        print()

    print(f"Result: {summary}")


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    skill_path = args[0]
    show_hints = "--fix-hints" in args or "--strict" in args
    strict = "--strict" in args

    print(f"Validating: {Path(skill_path).resolve()}")

    passed, summary, result = validate_skill(skill_path)

    # In strict mode, warnings are treated as errors
    if strict and result.warnings:
        passed = False
        summary = f"STRICT FAIL — {len(result.errors)} error(s), {len(result.warnings)} warning(s) (strict mode)"

    print_report(result, summary, show_hints)

    if not passed:
        sys.exit(1)
    elif result.warnings:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
