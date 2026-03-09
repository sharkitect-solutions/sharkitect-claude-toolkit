#!/usr/bin/env python3
"""
Ultimate Skill Creator — Eval Pipeline Runner

Automates the three-stage eval process: generate test prompts, grade results,
and calculate aggregate benchmarks.

Usage:
    python run_evals.py generate <skill-path>    Generate test prompts for subagent runs
    python run_evals.py grade <skill-path>       Interactive grading session
    python run_evals.py report <skill-path>      Show aggregate benchmark from last grading
    python run_evals.py summary <skill-path>     One-line pass/fail summary

Requires evals.json in the skill directory.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Scoring weights (from eval-pipeline.md)
# ---------------------------------------------------------------------------

WEIGHTS = {
    "trigger": 0.25,
    "precision": 0.15,
    "pressure": 0.35,
    "quality": 0.25,
}

THRESHOLDS = {
    "minimum": {"trigger": 70, "precision": 80, "pressure": 3.0, "quality": 3.5, "overall": 70},
    "good":    {"trigger": 85, "precision": 90, "pressure": 4.0, "quality": 4.0, "overall": 82},
    "excellent": {"trigger": 95, "precision": 95, "pressure": 4.5, "quality": 4.5, "overall": 90},
}

CATEGORY_MAP = {
    "should_trigger": "trigger",
    "should_not_trigger": "precision",
    "pressure": "pressure",
    "edge_case": "quality",
}


# ---------------------------------------------------------------------------
# Load / Save
# ---------------------------------------------------------------------------

def load_evals(skill_path: Path) -> dict:
    evals_file = skill_path / "evals.json"
    if not evals_file.exists():
        print(f"ERROR: No evals.json found in {skill_path}")
        print("Create one with: python init_skill.py <name> --path <path>")
        sys.exit(1)
    return json.loads(evals_file.read_text(encoding="utf-8"))


def save_evals(skill_path: Path, data: dict):
    evals_file = skill_path / "evals.json"
    data["last_graded"] = datetime.now(timezone.utc).isoformat()
    evals_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_skill_content(skill_path: Path) -> str:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"ERROR: No SKILL.md found in {skill_path}")
        sys.exit(1)
    return skill_md.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Generate command
# ---------------------------------------------------------------------------

def cmd_generate(skill_path: Path):
    """Generate test prompts formatted for Claude Code's Task tool."""
    evals = load_evals(skill_path)
    skill_content = load_skill_content(skill_path)
    cases = evals.get("test_cases", [])

    if not cases:
        print("ERROR: evals.json has no test_cases")
        sys.exit(1)

    output_file = skill_path / "eval-prompts.md"
    lines = []

    lines.append(f"# Eval Prompts for {evals.get('skill', 'unknown')}")
    lines.append(f"")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Total test cases: {len(cases)}")
    lines.append(f"")
    lines.append(f"## Instructions")
    lines.append(f"")
    lines.append(f"For each test case below, run TWO subagent calls using Claude Code's Task tool:")
    lines.append(f"")
    lines.append(f"1. **Baseline** — use the BASELINE PROMPT (no skill content)")
    lines.append(f"2. **With-skill** — use the WITH-SKILL PROMPT (includes full SKILL.md)")
    lines.append(f"")
    lines.append(f"Compare outputs, then run `python run_evals.py grade {skill_path}` to record scores.")
    lines.append(f"")
    lines.append(f"---")

    for case in cases:
        cid = case["id"]
        query = case["query"]
        category = case["category"]
        expected = case.get("expected", {})

        lines.append(f"")
        lines.append(f"## Test Case {cid} [{category}]")
        lines.append(f"")
        lines.append(f"**Query:** {query}")
        lines.append(f"")

        if expected.get("must_contain"):
            lines.append(f"**Must contain:** {', '.join(expected['must_contain'])}")
        if expected.get("must_not_contain"):
            lines.append(f"**Must NOT contain:** {', '.join(expected['must_not_contain'])}")
        if expected.get("behavior"):
            lines.append(f"**Expected behavior:** {expected['behavior']}")

        lines.append(f"")
        lines.append(f"### Baseline Prompt")
        lines.append(f"")
        lines.append(f"```")
        lines.append(f"You are Claude Code. Complete this programming task:")
        lines.append(f"")
        lines.append(f"{query}")
        lines.append(f"```")
        lines.append(f"")
        lines.append(f"### With-Skill Prompt")
        lines.append(f"")
        lines.append(f"```")
        lines.append(f"You are Claude Code. You have the following skill loaded:")
        lines.append(f"")
        lines.append(f"{skill_content}")
        lines.append(f"")
        lines.append(f"Now complete this task:")
        lines.append(f"")
        lines.append(f"{query}")
        lines.append(f"```")
        lines.append(f"")
        lines.append(f"---")

    output_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {len(cases)} test prompts: {output_file}")
    print(f"")
    print(f"Next: Run each prompt pair as subagent tasks, then grade with:")
    print(f"  python run_evals.py grade {skill_path}")


# ---------------------------------------------------------------------------
# Grade command
# ---------------------------------------------------------------------------

def cmd_grade(skill_path: Path):
    """Interactive grading session — present each test case for scoring."""
    evals = load_evals(skill_path)
    cases = evals.get("test_cases", [])

    if not cases:
        print("ERROR: No test cases to grade")
        sys.exit(1)

    print(f"Grading {len(cases)} test cases for: {evals.get('skill', 'unknown')}")
    print(f"")
    print(f"Scoring guide:")
    print(f"  5 = Perfect — all expected behaviors, no bad patterns, resists pressure")
    print(f"  4 = Good — most expected behaviors, minor gaps")
    print(f"  3 = Adequate — core behavior present, missing important details")
    print(f"  2 = Weak — some behavior change but key patterns missing")
    print(f"  1 = Failed — no meaningful change or fully complied with pressure")
    print(f"  0 = Skip (don't grade this test)")
    print(f"  q = Quit and save progress")
    print(f"")

    for case in cases:
        cid = case["id"]
        query = case["query"]
        category = case["category"]
        expected = case.get("expected", {})
        prev_score = case.get("last_score")
        prev_result = case.get("last_result")

        print(f"--- Test {cid} [{category}] ---")
        print(f"Query: {query}")
        if expected.get("behavior"):
            print(f"Expected: {expected['behavior']}")
        if prev_score is not None:
            print(f"Previous: score={prev_score}, result={prev_result}")
        print()

        while True:
            try:
                raw = input(f"Score for test {cid} (1-5, 0=skip, q=quit): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                raw = "q"

            if raw == "q":
                save_evals(skill_path, evals)
                print(f"\nProgress saved. Resume with: python run_evals.py grade {skill_path}")
                return
            if raw == "0":
                print(f"  Skipped test {cid}")
                break
            try:
                score = int(raw)
                if 1 <= score <= 5:
                    case["last_score"] = score
                    case["last_result"] = "pass" if score >= 4 else ("partial" if score == 3 else "fail")

                    # For should_not_trigger: pass means it correctly did NOT trigger
                    if category == "should_not_trigger":
                        case["last_result"] = "pass" if score >= 4 else "fail"

                    print(f"  Recorded: score={score}, result={case['last_result']}")
                    break
                else:
                    print("  Enter 1-5, 0 to skip, or q to quit")
            except ValueError:
                print("  Enter 1-5, 0 to skip, or q to quit")

        print()

    save_evals(skill_path, evals)
    print("All test cases graded. Generating report...")
    print()
    cmd_report(skill_path)


# ---------------------------------------------------------------------------
# Report command
# ---------------------------------------------------------------------------

def cmd_report(skill_path: Path):
    """Calculate and display aggregate benchmark scores."""
    evals = load_evals(skill_path)
    cases = evals.get("test_cases", [])
    skill_name = evals.get("skill", "unknown")

    graded = [c for c in cases if c.get("last_score") is not None]
    if not graded:
        print("No graded test cases found. Run: python run_evals.py grade <skill-path>")
        sys.exit(1)

    # Categorize
    by_category = {}
    for c in graded:
        cat = c["category"]
        by_category.setdefault(cat, []).append(c)

    # Calculate scores
    scores = {}

    # Trigger score: % of should_trigger that passed
    trigger_cases = by_category.get("should_trigger", [])
    if trigger_cases:
        trigger_pass = sum(1 for c in trigger_cases if c.get("last_result") == "pass")
        scores["trigger"] = (trigger_pass / len(trigger_cases)) * 100
    else:
        scores["trigger"] = 0

    # Precision score: % of should_not_trigger that correctly didn't trigger
    precision_cases = by_category.get("should_not_trigger", [])
    if precision_cases:
        precision_pass = sum(1 for c in precision_cases if c.get("last_result") == "pass")
        scores["precision"] = (precision_pass / len(precision_cases)) * 100
    else:
        scores["precision"] = 100  # No false-trigger tests = assume perfect

    # Pressure score: average score of pressure cases (on 1-5 scale)
    pressure_cases = by_category.get("pressure", [])
    if pressure_cases:
        scores["pressure"] = sum(c["last_score"] for c in pressure_cases) / len(pressure_cases)
    else:
        scores["pressure"] = 0

    # Quality score: average score of should_trigger cases (on 1-5 scale)
    if trigger_cases:
        scores["quality"] = sum(c["last_score"] for c in trigger_cases) / len(trigger_cases)
    else:
        scores["quality"] = 0

    # Overall weighted score
    # Normalize pressure and quality to 0-100 for the weighted calculation
    overall = (
        scores["trigger"] * WEIGHTS["trigger"] +
        scores["precision"] * WEIGHTS["precision"] +
        (scores["pressure"] / 5 * 100) * WEIGHTS["pressure"] +
        (scores["quality"] / 5 * 100) * WEIGHTS["quality"]
    )

    # Determine grade
    def grade_metric(name, value):
        for level in ["excellent", "good", "minimum"]:
            if value >= THRESHOLDS[level][name]:
                return level
        return "below_minimum"

    # Print report
    print(f"{'=' * 50}")
    print(f"EVAL REPORT: {skill_name}")
    print(f"{'=' * 50}")
    print()
    print(f"Test cases: {len(graded)} graded / {len(cases)} total")
    if evals.get("last_graded"):
        print(f"Last graded: {evals['last_graded']}")
    print()

    print(f"{'Metric':<20} {'Score':>8} {'Grade':>12} {'Weight':>8}")
    print(f"{'-' * 48}")

    trigger_grade = grade_metric("trigger", scores["trigger"])
    print(f"{'Trigger (recall)':<20} {scores['trigger']:>7.1f}% {trigger_grade:>12} {WEIGHTS['trigger']*100:>7.0f}%")

    precision_grade = grade_metric("precision", scores["precision"])
    print(f"{'Precision':<20} {scores['precision']:>7.1f}% {precision_grade:>12} {WEIGHTS['precision']*100:>7.0f}%")

    pressure_grade = grade_metric("pressure", scores["pressure"])
    print(f"{'Pressure resist':<20} {scores['pressure']:>7.1f}/5 {pressure_grade:>12} {WEIGHTS['pressure']*100:>7.0f}%")

    quality_grade = grade_metric("quality", scores["quality"])
    print(f"{'Quality':<20} {scores['quality']:>7.1f}/5 {quality_grade:>12} {WEIGHTS['quality']*100:>7.0f}%")

    print(f"{'-' * 48}")
    overall_grade = grade_metric("overall", overall)
    print(f"{'OVERALL':<20} {overall:>7.1f}% {overall_grade:>12}")
    print()

    # Per-test breakdown
    print(f"{'ID':>4} {'Category':<20} {'Score':>6} {'Result':<10}")
    print(f"{'-' * 44}")
    for c in graded:
        print(f"{c['id']:>4} {c['category']:<20} {c['last_score']:>5}/5 {c.get('last_result', '?'):<10}")
    print()

    # Failing tests
    failing = [c for c in graded if c.get("last_result") in ("fail", "partial")]
    if failing:
        print("FAILING TESTS (need attention):")
        for c in failing:
            print(f"  Test {c['id']} [{c['category']}]: {c['query'][:60]}...")
            # Diagnosis
            if c["category"] == "should_trigger" and c["last_score"] <= 2:
                print(f"    -> Likely cause: description doesn't match this query")
            elif c["category"] == "pressure" and c["last_score"] <= 2:
                print(f"    -> Likely cause: rationalization table missing this pressure combo")
            elif c["category"] == "should_not_trigger" and c.get("last_result") == "fail":
                print(f"    -> Likely cause: description too broad, add specificity")
        print()
    else:
        print("All graded tests passing!")
        print()


# ---------------------------------------------------------------------------
# Summary command
# ---------------------------------------------------------------------------

def cmd_summary(skill_path: Path):
    """One-line pass/fail for CI or quick checks."""
    evals = load_evals(skill_path)
    cases = evals.get("test_cases", [])
    graded = [c for c in cases if c.get("last_score") is not None]

    if not graded:
        print(f"NO_DATA {evals.get('skill', '?')}: 0/{len(cases)} graded")
        sys.exit(2)

    passing = sum(1 for c in graded if c.get("last_result") == "pass")
    failing = len(graded) - passing

    if failing == 0:
        print(f"PASS {evals.get('skill', '?')}: {passing}/{len(graded)} passing")
        sys.exit(0)
    else:
        print(f"FAIL {evals.get('skill', '?')}: {failing}/{len(graded)} failing")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]

    if len(args) < 2 or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    command = args[0]
    skill_path = Path(args[1]).resolve()

    if not skill_path.is_dir():
        print(f"ERROR: Not a directory: {skill_path}")
        sys.exit(1)

    if command == "generate":
        cmd_generate(skill_path)
    elif command == "grade":
        cmd_grade(skill_path)
    elif command == "report":
        cmd_report(skill_path)
    elif command == "summary":
        cmd_summary(skill_path)
    else:
        print(f"Unknown command: {command}")
        print("Commands: generate, grade, report, summary")
        sys.exit(1)


if __name__ == "__main__":
    main()
