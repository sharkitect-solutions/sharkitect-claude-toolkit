#!/usr/bin/env python3
"""
Ultimate Skill Creator — Skill Initializer

Scaffolds a new skill directory using the ultimate-skill-creator's prescribed
structure: trigger-only description, failure-confrontation body, rationalization
table, red flags checklist, and file index.

Usage:
    python init_skill.py <skill-name> [--path <path>] [--minimal]

Examples:
    python init_skill.py api-rate-limiter
    python init_skill.py api-rate-limiter --path ~/.claude/skills
    python init_skill.py api-rate-limiter --path ./skills --minimal
"""

import sys
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Templates — these match the structure prescribed in examples/skill-directory-template.md
# ---------------------------------------------------------------------------

SKILL_TEMPLATE = '''---
name: {skill_name}
description: >
  Use when [primary triggering condition — describe the situation, not the skill].
  Use when a user says "[trigger phrase 1]", "[trigger phrase 2]", or "[trigger phrase 3]".
  Use when [edge case that should still trigger — describe the risk of skipping].
  Use when [technology-specific trigger with named providers or tools].
  Use when [indirect indicator that this skill is relevant].
  This skill applies to [scope assertion] — including [commonly-skipped cases].
---

# {skill_title}

## Why This Skill Exists

[TODO: 2-3 sentences explaining the problem this skill solves. Name Claude's default
failure mode explicitly. State why the default behavior is wrong.]

## The Core Failure Pattern

[TODO: Describe what Claude does WITHOUT this skill. Be specific — name the exact
sequence of bad decisions Claude makes. This section confronts Claude with its own
behavior so it recognizes the pattern in real time.]

## Rationalization Table

[TODO: Run 3 pressure scenarios WITHOUT the skill loaded. Record Claude's exact
rationalizations verbatim. Each rationalization becomes a row in this table.]

| Rationalization | When It Appears | Why It Is Wrong |
|---|---|---|
| "[Excuse 1 — use Claude's exact words]" | [Context when this excuse surfaces] | [Concrete counterargument with numbers or specifics] |
| "[Excuse 2]" | [Context] | [Counterargument] |
| "[Excuse 3]" | [Context] | [Counterargument] |
| "[Excuse 4]" | [Context] | [Counterargument] |

## Non-Negotiable Rules

### 1. [Rule Name]

[Imperative statement of the rule.] [1-2 sentences explaining WHY — rules without
reasons get ignored under pressure.]

### 2. [Rule Name]

[Imperative statement.] [Why.]

### 3. [Rule Name]

[Imperative statement.] [Why.]

[TODO: 3-5 rules. More than 5 should be split — excess detail belongs in references.]

## Red Flags Checklist

Before declaring output complete, verify none of these are present:

- [ ] [Specific bad pattern 1 — concrete enough to pattern-match against code/output]
- [ ] [Specific bad pattern 2]
- [ ] [Specific bad pattern 3]
- [ ] [Specific bad pattern 4]
- [ ] [Specific bad pattern 5]

[TODO: 5-10 items, ordered from most common to least common.]

## [Domain-Specific Section]

[TODO: Key patterns, code examples, decision tables, or guidance specific to this
skill's domain. Keep focused — implementation details go in references.]

[TODO: For coding skills, show WRONG and RIGHT patterns side by side.]

See `references/[topic].md` for [what it contains].

## File Index

| File | Purpose |
|---|---|
| `references/[topic].md` | [What this file contains and when to use it] |
'''

REFERENCE_TEMPLATE = '''# {topic_title}

[TODO: Deep-dive content for this topic. This file is loaded on demand when Claude
needs specific details beyond what the SKILL.md body provides.]

## Overview

[What this reference covers and when to consult it.]

## [Section 1]

[Detailed content. This can be longer than what belongs in the body — references
have a soft limit of 3,000 words but can go up to 5,000 if needed.]

## [Section 2]

[More detailed content.]
'''

EVALS_TEMPLATE = '''{
  "skill": "{skill_name}",
  "version": "1.0",
  "test_cases": [
    {
      "id": 1,
      "query": "[TODO: should-trigger prompt]",
      "category": "should_trigger",
      "expected": {
        "must_contain": ["[expected pattern 1]", "[expected pattern 2]"],
        "must_not_contain": ["[bad pattern 1]"],
        "behavior": "[description of expected behavior]"
      },
      "last_result": null,
      "last_score": null
    },
    {
      "id": 2,
      "query": "[TODO: should-NOT-trigger prompt]",
      "category": "should_not_trigger",
      "expected": {
        "must_contain": [],
        "must_not_contain": [],
        "behavior": "Skill should NOT activate for this query"
      },
      "last_result": null,
      "last_score": null
    },
    {
      "id": 3,
      "query": "[TODO: pressure prompt combining 3+ pressure types]",
      "category": "pressure",
      "expected": {
        "must_contain": ["[correct behavior despite pressure]"],
        "must_not_contain": ["[shortcut compliance]"],
        "behavior": "[description of expected resistance]"
      },
      "last_result": null,
      "last_score": null
    }
  ]
}
'''


def title_case(name: str) -> str:
    """Convert kebab-case to Title Case."""
    return " ".join(word.capitalize() for word in name.split("-"))


def validate_name(name: str) -> tuple[bool, str]:
    """Validate skill name follows kebab-case rules."""
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        return False, (
            f"Name '{name}' must be kebab-case: lowercase letters, digits, "
            "and single hyphens between words. No leading/trailing/consecutive hyphens."
        )
    if len(name) > 60:
        return False, f"Name '{name}' exceeds 60 characters."
    return True, ""


def init_skill(skill_name: str, base_path: str, minimal: bool = False) -> Path | None:
    """
    Initialize a new skill directory with the ultimate-skill-creator's structure.

    Args:
        skill_name: kebab-case skill name
        base_path: parent directory where skill folder will be created
        minimal: if True, skip optional directories (references/, examples/)

    Returns:
        Path to created skill directory, or None on error.
    """
    valid, err = validate_name(skill_name)
    if not valid:
        print(f"ERROR: {err}")
        return None

    skill_dir = Path(base_path).resolve() / skill_name

    if skill_dir.exists():
        print(f"ERROR: Directory already exists: {skill_dir}")
        return None

    skill_title = title_case(skill_name)

    # Create directory tree
    try:
        skill_dir.mkdir(parents=True)
        print(f"  Created {skill_dir}/")

        # SKILL.md — always created
        (skill_dir / "SKILL.md").write_text(
            SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title),
            encoding="utf-8",
        )
        print("  Created SKILL.md")

        # references/ — unless --minimal
        if not minimal:
            refs_dir = skill_dir / "references"
            refs_dir.mkdir()
            (refs_dir / "topic-a.md").write_text(
                REFERENCE_TEMPLATE.format(topic_title=f"{skill_title} — Topic A"),
                encoding="utf-8",
            )
            print("  Created references/topic-a.md")

        # evals.json — always created (testing is non-negotiable)
        (skill_dir / "evals.json").write_text(
            EVALS_TEMPLATE.format(skill_name=skill_name),
            encoding="utf-8",
        )
        print("  Created evals.json")

    except OSError as e:
        print(f"ERROR: {e}")
        return None

    # Next steps
    print(f"\nSkill '{skill_name}' initialized at {skill_dir}")
    print()
    print("Next steps (follow the three-stage workflow):")
    print()
    print("  Stage 1 — Structure & Planning")
    print("    1. Write the description with 'Use when...' trigger conditions ONLY")
    print("    2. Plan which content goes in body vs references")
    print()
    print("  Stage 2 — TDD Content Creation")
    print("    3. Run 3 pressure scenarios WITHOUT the skill (RED phase)")
    print("    4. Build rationalization table from captured failures")
    print("    5. Write non-negotiable rules with 'why' explanations (GREEN phase)")
    print("    6. Audit for loopholes and tighten rules (REFACTOR phase)")
    print()
    print("  Stage 3 — Eval, Benchmark & Polish")
    print("    7. Fill in evals.json with 10-20 test cases")
    print("    8. Run: python run_evals.py generate <skill-path>")
    print("    9. Grade results and iterate until passing")
    print()
    print("Validate anytime: python quick_validate.py <skill-path>")

    return skill_dir


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    skill_name = args[0]
    base_path = "."
    minimal = False

    i = 1
    while i < len(args):
        if args[i] == "--path" and i + 1 < len(args):
            base_path = args[i + 1]
            i += 2
        elif args[i] == "--minimal":
            minimal = True
            i += 1
        else:
            print(f"Unknown argument: {args[i]}")
            sys.exit(1)

    print(f"Initializing skill: {skill_name}")
    print(f"Location: {Path(base_path).resolve() / skill_name}")
    print()

    result = init_skill(skill_name, base_path, minimal)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
