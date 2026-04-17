"""
error-tracker-hook.py - PostToolUse hook for automatic error tracking

Scans Bash and MCP tool output for error signatures. Tracks errors in
.tmp/session-errors.json with retry counts. When an error is retried
and succeeds, marks it resolved.

For MCP tools: detects soft failures (API returns "not supported",
"UNSUPPORTED_FIELD_TYPE", etc.) and identifies permanent API limitations.
On first occurrence of an API limitation, suggests lesson capture
immediately (no retry threshold -- these never resolve by retrying).

Self-healing: On any error, greps ~/.claude/lessons-learned.md for
matching keywords. If a known solution exists, injects it as
additionalContext so Claude uses the fix instead of retrying blindly.

Non-blocking: injects additional context, does not deny operations.

Input: JSON on stdin with tool_name, tool_input, tool_result
Output: JSON on stdout with additionalContext (if applicable)
"""

import hashlib
import json
import os
import re
import sys
import time


# Error signature patterns for Bash output
ERROR_PATTERNS = [
    re.compile(r"Traceback \(most recent call last\)", re.IGNORECASE),
    re.compile(r"^Error:", re.MULTILINE),
    re.compile(r"^FAILED", re.MULTILINE),
    re.compile(r"^fatal:", re.MULTILINE),
    re.compile(r"command not found", re.IGNORECASE),
    re.compile(r"Permission denied", re.IGNORECASE),
    re.compile(r"ModuleNotFoundError:", re.IGNORECASE),
    re.compile(r"ImportError:", re.IGNORECASE),
    re.compile(r"FileNotFoundError:", re.IGNORECASE),
    re.compile(r"ConnectionRefusedError:", re.IGNORECASE),
    re.compile(r"exit code [1-9]", re.IGNORECASE),
    re.compile(r"non-zero exit", re.IGNORECASE),
]

# Patterns to IGNORE (common false positives in Bash output)
IGNORE_PATTERNS = [
    re.compile(r"error_handler", re.IGNORECASE),
    re.compile(r"error_message", re.IGNORECASE),
    re.compile(r"on_error", re.IGNORECASE),
    re.compile(r"ErrorBoundary", re.IGNORECASE),
    re.compile(r"raise.*Error\(", re.IGNORECASE),
    re.compile(r"except.*Error", re.IGNORECASE),
]

# MCP tool soft-failure patterns (API returns response but operation failed)
MCP_ERROR_PATTERNS = [
    re.compile(r"UNSUPPORTED", re.IGNORECASE),
    re.compile(r"not supported", re.IGNORECASE),
    re.compile(r"INVALID_REQUEST", re.IGNORECASE),
    re.compile(r"is not allowed", re.IGNORECASE),
    re.compile(r"FORBIDDEN", re.IGNORECASE),
    re.compile(r"AUTHENTICATION_REQUIRED", re.IGNORECASE),
    re.compile(r"CANNOT_CREATE", re.IGNORECASE),
    re.compile(r"UNSUPPORTED_FIELD_TYPE", re.IGNORECASE),
    re.compile(r"field type .* is not supported", re.IGNORECASE),
    re.compile(r'"error"\s*:', re.IGNORECASE),
    re.compile(r"NOT_FOUND", re.IGNORECASE),
    re.compile(r"INVALID_PERMISSIONS", re.IGNORECASE),
]

# Patterns that indicate a PERMANENT API limitation (vs transient error)
API_LIMITATION_PATTERNS = [
    re.compile(r"UNSUPPORTED", re.IGNORECASE),
    re.compile(r"not supported at this time", re.IGNORECASE),
    re.compile(r"is not supported", re.IGNORECASE),
    re.compile(r"UNSUPPORTED_FIELD_TYPE", re.IGNORECASE),
    re.compile(r"Creating .* fields is not supported", re.IGNORECASE),
    re.compile(r"deletion is not supported", re.IGNORECASE),
]


def _errors_file_path(cwd):
    """Path to session errors tracking file."""
    return os.path.join(cwd, ".tmp", "session-errors.json")


def _load_errors(cwd):
    """Load existing session errors."""
    path = _errors_file_path(cwd)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_errors(cwd, errors):
    """Save session errors to tracking file."""
    path = _errors_file_path(cwd)
    tmp_dir = os.path.dirname(path)
    os.makedirs(tmp_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2)


def _error_hash(identifier, error_summary):
    """Generate a stable hash for an error (same identifier + error = same hash)."""
    key = "%s::%s" % (identifier.strip()[:200], error_summary.strip()[:200])
    return hashlib.md5(key.encode("utf-8")).hexdigest()[:12]


def _extract_error_summary(output):
    """Extract the most relevant error line from output."""
    lines = output.strip().splitlines()
    # Check all error pattern lists for the most specific match
    all_patterns = ERROR_PATTERNS + MCP_ERROR_PATTERNS
    for line in reversed(lines):
        line_s = line.strip()
        if line_s and any(p.search(line_s) for p in all_patterns):
            if not any(ip.search(line_s) for ip in IGNORE_PATTERNS):
                return line_s[:200]
    # Fallback: last non-empty line
    for line in reversed(lines):
        if line.strip():
            return line.strip()[:200]
    return "unknown error"


def _detect_error(output, tool_category="bash"):
    """Check if tool output contains error signatures. Returns summary or None."""
    if not output or len(output) < 5:
        return None

    patterns = ERROR_PATTERNS if tool_category == "bash" else MCP_ERROR_PATTERNS

    matched = False
    for pattern in patterns:
        m = pattern.search(output)
        if m:
            if tool_category == "bash":
                match_text = m.group(0)
                if any(ip.search(match_text) for ip in IGNORE_PATTERNS):
                    continue
            matched = True
            break

    if not matched:
        return None

    return _extract_error_summary(output)


def _is_api_limitation(error_summary):
    """Check if an error looks like a permanent API limitation (vs transient)."""
    return any(p.search(error_summary) for p in API_LIMITATION_PATTERNS)


def _search_lessons(error_summary):
    """Search ~/.claude/lessons-learned.md for a known solution matching the error."""
    lessons_path = os.path.join(
        os.path.expanduser("~"), ".claude", "lessons-learned.md"
    )
    if not os.path.isfile(lessons_path):
        return None

    try:
        with open(lessons_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return None

    # Extract keywords from error summary (words 4+ chars, lowercased)
    keywords = set()
    for word in re.findall(r"[a-zA-Z_]{4,}", error_summary):
        keywords.add(word.lower())

    if not keywords:
        return None

    # Split lessons into sections (each starts with ###)
    sections = re.split(r"(?=^### )", content, flags=re.MULTILINE)

    best_match = None
    best_score = 0

    for section in sections:
        if not section.strip():
            continue
        section_lower = section.lower()
        score = sum(1 for kw in keywords if kw in section_lower)
        if score >= 2 and score > best_score:
            best_score = score
            best_match = section.strip()

    if best_match and best_score >= 2:
        solution_match = re.search(
            r"\*\*Solution:\*\*\s*(.+?)(?:\n\*\*|\Z)",
            best_match,
            re.DOTALL,
        )
        if solution_match:
            solution = solution_match.group(1).strip()
            return "KNOWN SOLUTION (from lessons-learned.md): %s" % solution[:500]

    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    tool_name = data.get("tool_name", "")

    # Categorize tool type
    if tool_name == "Bash":
        tool_category = "bash"
    elif tool_name.startswith("mcp__"):
        tool_category = "mcp"
    else:
        return 0  # Only track Bash and MCP tools

    tool_input = data.get("tool_input", {})
    tool_result = data.get("tool_result", "")

    # For Bash: use command as identifier; for MCP: use tool_name
    if tool_category == "bash":
        identifier = tool_input.get("command", "")
        if not identifier:
            return 0
    else:
        identifier = tool_name

    if not tool_result:
        return 0

    # Convert tool_result to string if needed
    if isinstance(tool_result, dict):
        tool_result = json.dumps(tool_result)

    cwd = os.getcwd()
    errors = _load_errors(cwd)

    # Check if this output contains an error
    error_summary = _detect_error(tool_result, tool_category)

    if error_summary:
        # Error detected -- track it
        eh = _error_hash(identifier, error_summary)
        is_limitation = _is_api_limitation(error_summary)

        # Check if we've seen this error before
        existing = None
        for entry in errors:
            if entry.get("hash") == eh:
                existing = entry
                break

        if existing:
            existing["retry_count"] = existing.get("retry_count", 1) + 1
            existing["last_seen"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            )
        else:
            errors.append({
                "hash": eh,
                "command": identifier[:200],
                "tool_category": tool_category,
                "error_summary": error_summary,
                "is_api_limitation": is_limitation,
                "retry_count": 1,
                "resolved": False,
                "first_seen": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                ),
                "last_seen": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                ),
            })

        _save_errors(cwd, errors)

        # Self-healing: search lessons for known solution
        known_fix = _search_lessons(error_summary)
        if known_fix:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        "ERROR DETECTED: %s\n\n%s\n\n"
                        "Apply this known fix instead of retrying blindly."
                        % (error_summary[:100], known_fix)
                    ),
                }
            }
            print(json.dumps(output))
            return 0

        # For API limitations: suggest lesson capture on FIRST occurrence
        # (these never resolve by retrying -- capture immediately)
        if is_limitation:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        "API LIMITATION DETECTED: %s\n"
                        "Tool: %s\n\n"
                        "This is a PERMANENT platform limitation, not a transient "
                        "error. Do NOT retry -- it will never work.\n\n"
                        "1. Provide manual step-by-step instructions for the user.\n"
                        "2. Ask: 'Should I add this to lessons-learned.md so future "
                        "sessions automatically know about this limitation?'"
                        % (error_summary[:150], identifier[:100])
                    ),
                }
            }
            print(json.dumps(output))
            return 0

        # No known fix, not a limitation -- just track silently
        return 0

    else:
        # No error in output -- check if a previously tracked error was resolved
        if identifier and errors:
            for entry in errors:
                if (
                    not entry.get("resolved")
                    and entry.get("command", "")[:100] == identifier[:100]
                ):
                    entry["resolved"] = True
                    entry["resolved_at"] = time.strftime(
                        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                    )
                    _save_errors(cwd, errors)

                    if entry.get("retry_count", 0) >= 2:
                        output = {
                            "hookSpecificOutput": {
                                "hookEventName": "PostToolUse",
                                "additionalContext": (
                                    "ERROR RESOLVED after %d retries: '%s'. "
                                    "This fix should be recorded as a lesson in "
                                    "~/.claude/lessons-learned.md so all workspaces "
                                    "benefit. Capture it at session-checkpoint."
                                    % (
                                        entry["retry_count"],
                                        entry["error_summary"][:80],
                                    )
                                ),
                            }
                        }
                        print(json.dumps(output))
                    return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())