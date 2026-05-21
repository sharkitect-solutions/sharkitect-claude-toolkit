"""
quality-gate.py - PostToolUse hook for quality-gate plugin

Validates structural quality of skill SKILL.md and agent .md files
after Write/Edit operations. Lightweight linter, not a content reviewer.

Input: JSON on stdin with tool_name and tool_input.file_path
Output: Validation warnings on stdout (injected into conversation context)
Exit: Always 0 (non-blocking -- file already written, we just warn)

Usage as hook: Called automatically on PostToolUse Write|Edit events
Usage manual: python quality-gate.py --file <path>
"""

import json
import os
import re
import sys


# ---------------------------------------------------------------------------
# Path detection
# ---------------------------------------------------------------------------

def normalize_path(path):
    """Normalize path separators for cross-platform comparison."""
    return path.replace("\\", "/")


def is_skill_file(file_path):
    """Check if file_path is a skill SKILL.md file in ~/.claude/skills/."""
    norm = normalize_path(file_path).lower()
    return "/.claude/skills/" in norm and norm.endswith("/skill.md")


def is_agent_file(file_path):
    """Check if file_path is an agent .md file in ~/.claude/agents/."""
    norm = normalize_path(file_path).lower()
    return "/.claude/agents/" in norm and norm.endswith(".md")


def read_file_safe(file_path):
    """Read file content, return None on failure."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def get_name(file_path, file_type):
    """Extract display name from file path."""
    if file_type == "Skill":
        return os.path.basename(os.path.dirname(file_path))
    return os.path.splitext(os.path.basename(file_path))[0]


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def extract_frontmatter(content):
    """Extract frontmatter and body from content.
    Returns (frontmatter_text, body_text) or (None, content).
    """
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if match:
        body = content[match.end():].lstrip("\n")
        return match.group(1), body
    return None, content


def has_field(frontmatter, field_name):
    """Check if a YAML field exists in frontmatter."""
    pattern = r"^" + re.escape(field_name) + r"\s*:"
    return bool(re.search(pattern, frontmatter, re.MULTILINE))


def extract_description(frontmatter):
    """Extract the full description text from YAML frontmatter.
    Handles single-line and multi-line (>, >-, |) YAML formats.
    """
    lines = frontmatter.split("\n")
    desc_parts = []
    in_desc = False

    for line in lines:
        stripped = line.strip()

        if not in_desc:
            if stripped.startswith("description:"):
                in_desc = True
                after = stripped[len("description:"):].strip()
                if after in (">", ">-", "|", "|-", ""):
                    continue
                desc_parts.append(after.strip("\"'"))
                continue
        else:
            if line.startswith("  ") or line.startswith("\t"):
                desc_parts.append(stripped)
            elif stripped == "":
                continue
            else:
                break

    return " ".join(desc_parts)


# ---------------------------------------------------------------------------
# Skill validation
# ---------------------------------------------------------------------------

def validate_skill(file_path, content):
    """Validate a skill SKILL.md file structurally. Returns list of warnings."""
    warnings = []
    lines = content.splitlines()
    line_count = len(lines)

    # 1. Frontmatter
    frontmatter, body = extract_frontmatter(content)
    if frontmatter is None:
        warnings.append(
            "MISSING FRONTMATTER: Skill must start with --- delimited YAML frontmatter"
        )
        return warnings

    # 2. Name field
    if not has_field(frontmatter, "name"):
        warnings.append("MISSING NAME: Frontmatter must have 'name:' field")

    # 3. Description field + quality checks
    if not has_field(frontmatter, "description"):
        warnings.append("MISSING DESCRIPTION: Frontmatter must have 'description:' field")
    else:
        desc = extract_description(frontmatter)
        if len(desc) < 20:
            warnings.append(
                "SHORT DESCRIPTION: Only %d chars (aim for 50+ with triggers and exclusions)"
                % len(desc)
            )
        else:
            # 4. Trigger conditions (CSO rule)
            if not re.search(
                r"use when|use for|use this|invoke when|invoke for",
                desc, re.IGNORECASE,
            ):
                warnings.append(
                    "NO TRIGGERS: Description needs trigger conditions "
                    "('Use when...', 'Use for...')"
                )
            # 5. Exclusions (CSO rule)
            if not re.search(
                r"do not use for|don't use for|do NOT use|use instead:",
                desc, re.IGNORECASE,
            ):
                warnings.append(
                    "NO EXCLUSIONS: Description needs exclusions "
                    "('Do NOT use for: [skill] ([purpose])')"
                )

    # 6. Line count
    if line_count < 20:
        warnings.append(
            "STUB: Only %d lines -- too short for meaningful skill content" % line_count
        )
    elif line_count > 500:
        warnings.append(
            "OVERSIZED: %d lines -- consider splitting with companion files" % line_count
        )

    # 7. File Index (for skills >100 lines)
    body_lower = body.lower()
    if line_count > 100 and "file index" not in body_lower:
        warnings.append(
            "NO FILE INDEX: Skills >100 lines need a File Index table "
            "(File, Load When, Do NOT Load)"
        )

    # 8. Scope Boundary (for substantial skills)
    if line_count > 50 and "scope boundary" not in body_lower:
        warnings.append(
            "NO SCOPE BOUNDARY: Consider adding a Scope Boundary table "
            "(This Skill / Use Instead)"
        )

    return warnings


# ---------------------------------------------------------------------------
# Agent validation
# ---------------------------------------------------------------------------

def validate_agent(file_path, content):
    """Validate an agent .md file structurally. Returns list of warnings."""
    warnings = []
    lines = content.splitlines()
    line_count = len(lines)

    # 1. Frontmatter
    frontmatter, body = extract_frontmatter(content)
    if frontmatter is None:
        warnings.append(
            "MISSING FRONTMATTER: Agent must start with --- delimited YAML frontmatter"
        )
        return warnings

    # 2. Name field
    if not has_field(frontmatter, "name"):
        warnings.append("MISSING NAME: Frontmatter must have 'name:' field")

    # 3. Description field + quality checks
    if not has_field(frontmatter, "description"):
        warnings.append("MISSING DESCRIPTION: Frontmatter must have 'description:' field")
    else:
        desc = extract_description(frontmatter)
        if len(desc) < 20:
            warnings.append(
                "SHORT DESCRIPTION: Only %d chars (aim for 100+ with examples and exclusions)"
                % len(desc)
            )
        else:
            # 4. Examples in description
            if "<example>" not in desc.lower():
                # Also check first 3000 chars of content (examples may be in frontmatter block)
                head = content[:3000].lower()
                if "<example>" not in head:
                    warnings.append(
                        "NO EXAMPLES: Agent description should contain "
                        "<example> blocks with commentary"
                    )
            # 5. Exclusions
            if not re.search(
                r"do not use for|don't use for|do NOT use",
                desc, re.IGNORECASE,
            ):
                warnings.append(
                    "NO EXCLUSIONS: Description needs exclusions "
                    "('Do NOT use for: ...')"
                )

    # 6. Line count
    if line_count < 30:
        warnings.append(
            "STUB: Only %d lines -- too short for meaningful agent content" % line_count
        )

    # 7. Anti-patterns section
    body_lower = body.lower()
    has_never = "never" in body_lower
    has_antipattern = re.search(r"anti.?pattern", body_lower)
    if not has_never and not has_antipattern:
        warnings.append(
            "NO ANTI-PATTERNS: Agent should have NEVER/anti-pattern section"
        )

    # 8. Output template
    if not re.search(
        r"output.?template|output.?format|response.?format|"
        r"structured.?output|return.?format|report.?format",
        body_lower,
    ):
        warnings.append(
            "NO OUTPUT TEMPLATE: Agent should have output template/format section"
        )

    return warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Manual test mode: python quality-gate.py --file <path>
    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Usage: python quality-gate.py --file <path>", file=sys.stderr)
            return 1
        file_path = os.path.abspath(sys.argv[2])
        content = read_file_safe(file_path)
        if content is None:
            print("Cannot read: %s" % file_path, file=sys.stderr)
            return 1
        if is_skill_file(file_path):
            warnings = validate_skill(file_path, content)
            file_type = "Skill"
        elif is_agent_file(file_path):
            warnings = validate_agent(file_path, content)
            file_type = "Agent"
        else:
            print("Not a skill or agent file: %s" % file_path, file=sys.stderr)
            return 1
        name = get_name(file_path, file_type)
        if warnings:
            print("[quality-gate] %s '%s' - %d issue(s):" % (file_type, name, len(warnings)))
            for w in warnings:
                print("  - %s" % w)
        else:
            print("[quality-gate] %s '%s' - PASS (0 issues)" % (file_type, name))
        return 0

    # Hook mode: read JSON from stdin
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        return 0

    # Determine file type and validate
    if is_skill_file(file_path):
        content = read_file_safe(file_path)
        if content is None:
            return 0
        warnings = validate_skill(file_path, content)
        file_type = "Skill"
    elif is_agent_file(file_path):
        content = read_file_safe(file_path)
        if content is None:
            return 0
        warnings = validate_agent(file_path, content)
        file_type = "Agent"
    else:
        return 0

    # Output warnings (stdout = injected into conversation context)
    if warnings:
        name = get_name(file_path, file_type)
        output = [
            "[quality-gate] %s '%s' - %d structural issue(s):"
            % (file_type, name, len(warnings))
        ]
        for w in warnings:
            output.append("  - %s" % w)
        print("\n".join(output))

    return 0


if __name__ == "__main__":
    sys.exit(main())
