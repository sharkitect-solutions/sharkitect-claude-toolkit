"""
track-changes.py - PostToolUse hook for auto-sync plugin

Tracks Write/Edit operations to skill SKILL.md and agent .md files.
Maintains a session-scoped list at .tmp/modified-this-session.json
that the sync-reminder Stop hook and aios-core PreCompact hook consume.

Input: JSON on stdin with tool_name and tool_input.file_path
Output: None (silent tracking)
Exit: Always 0 (non-blocking)
"""

import json
import os
import sys
from datetime import datetime, timezone


def normalize_path(path):
    """Normalize path separators for cross-platform comparison."""
    return path.replace("\\", "/")


def is_skill_or_agent_file(file_path):
    """Check if file_path is a skill SKILL.md or agent .md file."""
    norm = normalize_path(file_path).lower()
    if "/.claude/skills/" in norm and norm.endswith("/skill.md"):
        return "skill"
    if "/.claude/agents/" in norm and norm.endswith(".md"):
        return "agent"
    return None


def load_tracking_file(tracking_path):
    """Load the tracking file. Returns list of entries."""
    if not os.path.isfile(tracking_path):
        return []
    try:
        with open(tracking_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_tracking_file(tracking_path, entries):
    """Save entries to the tracking file."""
    os.makedirs(os.path.dirname(tracking_path), exist_ok=True)
    try:
        with open(tracking_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except OSError:
        pass


def main():
    # Read hook input from stdin
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        return 0

    # Check if this is a skill/agent file
    file_type = is_skill_or_agent_file(file_path)
    if file_type is None:
        return 0

    # Determine tracking file location (relative to cwd)
    cwd = os.getcwd()
    tracking_path = os.path.join(cwd, ".tmp", "modified-this-session.json")

    # Load existing entries
    entries = load_tracking_file(tracking_path)

    # Check for duplicates (same path already tracked)
    norm_path = normalize_path(file_path)
    existing_paths = {normalize_path(e.get("path", "")) for e in entries if isinstance(e, dict)}
    if norm_path in existing_paths:
        # Already tracked, update timestamp
        for e in entries:
            if isinstance(e, dict) and normalize_path(e.get("path", "")) == norm_path:
                e["tool"] = tool_name
                e["time"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                e["type"] = file_type
                break
    else:
        # New entry
        entries.append({
            "path": file_path,
            "type": file_type,
            "tool": tool_name,
            "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    # Save updated tracking file
    save_tracking_file(tracking_path, entries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
