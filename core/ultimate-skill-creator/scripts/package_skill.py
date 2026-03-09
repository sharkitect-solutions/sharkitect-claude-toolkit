#!/usr/bin/env python3
"""
Ultimate Skill Creator — Skill Packager

Validates a skill, then packages it into a distributable zip file.
Runs full CSO validation before packaging — broken skills don't ship.

Usage:
    python package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python package_skill.py ~/.claude/skills/my-skill
    python package_skill.py ~/.claude/skills/my-skill ./dist
"""

import sys
import zipfile
from pathlib import Path

# Import validation from sibling module
sys.path.insert(0, str(Path(__file__).parent))
from quick_validate import validate_skill


EXCLUDE_PATTERNS = {
    "__pycache__", ".pyc", ".pyo", ".DS_Store", "Thumbs.db",
    "eval-prompts.md",  # Generated output, not part of the skill
}


def should_exclude(path: Path) -> bool:
    return any(part in EXCLUDE_PATTERNS or part.startswith(".") for part in path.parts)


def package_skill(skill_path: str | Path, output_dir: str | Path | None = None) -> Path | None:
    """
    Package a skill folder into a zip file after validation.

    Returns:
        Path to created zip file, or None on error.
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"ERROR: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"ERROR: Not a directory: {skill_path}")
        return None

    if not (skill_path / "SKILL.md").exists():
        print(f"ERROR: SKILL.md not found in {skill_path}")
        return None

    # Run full validation
    print("Validating skill...")
    passed, summary, result = validate_skill(skill_path)

    if not passed:
        print(f"Validation FAILED: {summary}")
        print("Fix errors before packaging.")
        if result.errors:
            for e in result.errors:
                print(f"  x {e}")
        return None

    if result.warnings:
        print(f"Validation passed with warnings: {summary}")
        for w in result.warnings:
            print(f"  ! {w}")
        print()
    else:
        print(f"Validation: {summary}")
        print()

    # Build zip
    skill_name = skill_path.name
    if output_dir:
        out = Path(output_dir).resolve()
        out.mkdir(parents=True, exist_ok=True)
    else:
        out = Path.cwd()

    zip_path = out / f"{skill_name}.zip"

    try:
        file_count = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fp in sorted(skill_path.rglob("*")):
                if fp.is_file() and not should_exclude(fp.relative_to(skill_path)):
                    arcname = fp.relative_to(skill_path.parent)
                    zf.write(fp, arcname)
                    print(f"  + {arcname}")
                    file_count += 1

        print(f"\nPackaged {file_count} files: {zip_path}")
        return zip_path

    except OSError as e:
        print(f"ERROR creating zip: {e}")
        return None


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    skill_path = args[0]
    output_dir = args[1] if len(args) > 1 else None

    print(f"Packaging: {Path(skill_path).resolve()}")
    if output_dir:
        print(f"Output: {Path(output_dir).resolve()}")
    print()

    result = package_skill(skill_path, output_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
