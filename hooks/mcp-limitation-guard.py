"""
mcp-limitation-guard.py - PreToolUse hook for known API limitation prevention

Fires before MCP tool calls and Bash commands. Checks if the operation
being attempted matches a known API limitation in lessons-learned.md.
If so, injects a warning with the known workaround BEFORE Claude wastes
a tool call that will fail.

Non-blocking: injects additional context, does not deny the operation.
Performance: only reads the API Limitations section of lessons-learned.md.
Early-exits if no keyword overlap detected.

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with additionalContext (if limitation matched)
"""

import json
import os
import re
import sys


def _load_api_limitations():
    """Load and parse API Limitations section from lessons-learned.md."""
    lessons_path = os.path.join(
        os.path.expanduser("~"), ".claude", "lessons-learned.md"
    )
    if not os.path.isfile(lessons_path):
        return []

    try:
        with open(lessons_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    # Extract the API Limitations section
    api_section_match = re.search(
        r"## API Limitations\s*\n(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    if not api_section_match:
        return []

    api_section = api_section_match.group(1)

    # Parse individual entries (each starts with ###)
    entries = []
    sections = re.split(r"(?=^### )", api_section, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract tags
        tags_match = re.search(r"\*\*Tags:\*\*\s*(.+)", section)
        tags = set()
        if tags_match:
            for tag in tags_match.group(1).split(","):
                tag = tag.strip().lower()
                if tag:
                    tags.add(tag)

        # Extract tool name if present
        tool_match = re.search(r"\*\*Tool:\*\*\s*(.+)", section)
        tool_name = ""
        if tool_match:
            tool_name = tool_match.group(1).strip().lower()

        # Extract operation if present
        op_match = re.search(r"\*\*Operation:\*\*\s*(.+)", section)
        operation = ""
        if op_match:
            operation = op_match.group(1).strip().lower()

        # Extract solution
        solution_match = re.search(
            r"\*\*Solution:\*\*\s*(.+?)(?:\n\*\*|\Z)",
            section,
            re.DOTALL,
        )
        solution = ""
        if solution_match:
            solution = solution_match.group(1).strip()

        # Extract manual steps if present
        steps_match = re.search(
            r"\*\*Manual-Steps:\*\*\s*(.+?)(?:\n\*\*|\Z)",
            section,
            re.DOTALL,
        )
        manual_steps = ""
        if steps_match:
            manual_steps = steps_match.group(1).strip()

        # Also add words from the heading as keywords
        heading_match = re.match(r"### .+?\]\s*\S+:\s*(.+)", section)
        if heading_match:
            for word in re.findall(r"[a-zA-Z_]{4,}", heading_match.group(1)):
                tags.add(word.lower())

        if tags or tool_name:
            entries.append({
                "tags": tags,
                "tool": tool_name,
                "operation": operation,
                "solution": solution,
                "manual_steps": manual_steps,
                "raw": section[:300],
            })

    return entries


def _extract_signal_keywords(tool_name, tool_input):
    """Extract keywords from the tool call that could match limitation tags."""
    keywords = set()

    # Parse MCP tool name components (e.g., mcp__claude_ai_Airtable__create_field)
    if tool_name.startswith("mcp__"):
        parts = tool_name.split("__")
        for part in parts:
            # Split camelCase and snake_case
            for word in re.findall(r"[a-zA-Z]{4,}", part):
                keywords.add(word.lower())

    # For Bash: extract keywords from command
    if isinstance(tool_input, dict):
        command = tool_input.get("command", "")
        if command:
            for word in re.findall(r"[a-zA-Z_]{4,}", command):
                keywords.add(word.lower())

        # Check specific MCP input fields that indicate operation type
        for key in ("type", "field_type", "fieldType", "operation"):
            val = tool_input.get(key, "")
            if isinstance(val, str) and val:
                keywords.add(val.lower())
                # Also add component words
                for word in re.findall(r"[a-zA-Z]{4,}", val):
                    keywords.add(word.lower())

        # Check for delete-type operations in any field
        input_str = json.dumps(tool_input).lower()
        if "delete" in input_str:
            keywords.add("delete")
        if "rollup" in input_str:
            keywords.add("rollup")
        if "formula" in input_str:
            keywords.add("formula")
        if "lookup" in input_str:
            keywords.add("lookup")

    return keywords


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    tool_name = data.get("tool_name", "")

    # Only check MCP tools and Bash
    if not (tool_name.startswith("mcp__") or tool_name == "Bash"):
        return 0

    tool_input = data.get("tool_input", {})

    # Extract signal keywords from this tool call
    keywords = _extract_signal_keywords(tool_name, tool_input)
    if not keywords:
        return 0

    # Load known API limitations
    limitations = _load_api_limitations()
    if not limitations:
        return 0

    # Match against known limitations (require 2+ tag overlaps)
    best_match = None
    best_score = 0

    for entry in limitations:
        # Score: count how many of the entry's tags appear in our keywords
        score = len(entry["tags"] & keywords)

        # Bonus: if the tool name matches the entry's tool field
        if entry["tool"] and entry["tool"] in tool_name.lower():
            score += 2

        # Bonus: if the operation field matches
        if entry["operation"]:
            op_words = set(re.findall(r"[a-zA-Z]{4,}", entry["operation"]))
            score += len(op_words & keywords)

        if score >= 2 and score > best_score:
            best_score = score
            best_match = entry

    if not best_match:
        return 0

    # Sanity checks to prevent false positives.
    # Applied to BOTH Bash and MCP calls. The Tool-field check was originally
    # Bash-only; extended to MCP 2026-04-23 (wr-2026-04-22-020) after a
    # HubSpot MCP call got matched against Airtable limitation entries via
    # the generic verb "create".
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        unquoted = re.sub(r'"[^"]*"', "", command)
        unquoted = re.sub(r"'[^']*'", "", unquoted).lower()

        # Check 1 (Bash-only): at least one matched tag must appear in the
        # UNQUOTED portion. If all overlap came from quoted strings (like
        # --needed "hubspot api"), it's prose, not a real API call.
        matched_tags = best_match["tags"] & keywords
        if matched_tags and not any(t in unquoted for t in matched_tags):
            return 0

        # Check 2 (Bash service-identifier): the limitation's Tool field
        # must appear as a standalone word in the unquoted command.
        # Prevents `nslookup` triggering Airtable "lookup field" limitations.
        if best_match.get("tool"):
            tool_tokens = re.findall(r"[a-zA-Z]{4,}", best_match["tool"].lower())
            if tool_tokens:
                found = False
                for token in tool_tokens:
                    if re.search(r"\b" + re.escape(token) + r"\b", unquoted):
                        found = True
                        break
                if not found:
                    return 0

    elif tool_name.startswith("mcp__"):
        # Check 2 (MCP service-identifier): if the limitation entry has a
        # Tool field, that service name must appear as a case-insensitive
        # component of the MCP tool path. Prevents Airtable limitations
        # matching HubSpot/Supabase/Notion/etc. MCP calls just because the
        # verbs (create, update, delete) overlap. Source: wr-2026-04-22-020.
        if best_match.get("tool"):
            tool_tokens = re.findall(r"[a-zA-Z]{4,}", best_match["tool"].lower())
            if tool_tokens:
                tool_name_lower = tool_name.lower()
                found = False
                for token in tool_tokens:
                    # mcp__ names are double-underscore separated. Treat each
                    # token as a component match: 'airtable' in 'airtable' yes,
                    # 'airtable' in 'hubspot' no.
                    if token in tool_name_lower:
                        found = True
                        break
                if not found:
                    return 0

    # Build the warning message
    parts = [
        "KNOWN API LIMITATION: This operation matches a documented limitation."
    ]

    if best_match["solution"]:
        parts.append("Solution: %s" % best_match["solution"][:300])

    if best_match["manual_steps"]:
        parts.append("Manual steps for user: %s" % best_match["manual_steps"][:500])

    parts.append(
        "Do NOT attempt this operation via API/MCP -- it will fail. "
        "Instead, provide the user with manual instructions."
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "\n".join(parts),
        }
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())