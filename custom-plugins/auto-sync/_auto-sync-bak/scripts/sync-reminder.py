"""
sync-reminder.py - Stop hook for auto-sync plugin

Checks if skill/agent files were modified this session (via tracking file
written by track-changes.py). If modified files exist, blocks the stop
and injects a sync reminder. Clears the tracking file after firing
so the next stop attempt proceeds normally.

Input: JSON on stdin with session_id
Output: JSON with decision "block" and reason (if files need syncing)
Exit: Always 0
"""

import json
import os
import sys


def load_tracking_file(tracking_path):
    """Load the tracking file. Returns list of entries or empty list."""
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


def format_file_list(entries):
    """Format entries into a readable list."""
    lines = []
    skills = []
    agents = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        path = e.get("path", "unknown")
        ftype = e.get("type", "unknown")
        if ftype == "skill":
            # Extract skill name from path
            parts = path.replace("\\", "/").split("/")
            try:
                idx = parts.index("skills")
                name = parts[idx + 1] if idx + 1 < len(parts) else "unknown"
            except ValueError:
                name = "unknown"
            skills.append(name)
        elif ftype == "agent":
            name = os.path.splitext(os.path.basename(path))[0]
            agents.append(name)

    if skills:
        lines.append("Skills modified: %s" % ", ".join(sorted(set(skills))))
    if agents:
        lines.append("Agents modified: %s" % ", ".join(sorted(set(agents))))
    return lines


def main():
    # Read hook input
    try:
        raw = sys.stdin.read()
        # Stop hook input contains session_id and possibly other fields
    except Exception:
        return 0

    cwd = os.getcwd()
    tracking_path = os.path.join(cwd, ".tmp", "modified-this-session.json")

    entries = load_tracking_file(tracking_path)

    if not entries:
        # No modified files, allow stop
        return 0

    # Build the sync reminder
    file_list = format_file_list(entries)
    count = len(entries)

    reason_parts = [
        "[auto-sync] %d skill/agent file(s) were modified this session but may not be synced:" % count,
    ]
    for line in file_list:
        reason_parts.append("  %s" % line)
    reason_parts.append("")
    reason_parts.append("Please run sync before ending the session:")
    reason_parts.append("  python tools/sync-skills.py --sync --push")
    reason_parts.append("  python tools/sync-agents.py --sync --push")
    reason_parts.append("")
    reason_parts.append("If you want to skip sync, say 'skip sync' and I will stop.")

    reason = "\n".join(reason_parts)

    # Clear the tracking file so the next stop attempt goes through
    # (whether the user syncs or says "skip sync")
    try:
        os.remove(tracking_path)
    except OSError:
        pass

    # Output blocking JSON
    output = {
        "decision": "block",
        "reason": reason,
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
