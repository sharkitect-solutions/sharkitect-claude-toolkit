"""
session-end-check.py - SessionEnd hook for aios-core
Detects unsaved skill/agent changes and uncommitted git changes.
Outputs reminders to stderr (non-blocking warnings).

Exit codes: 0 = success (always), warnings go to stderr
Target: sub-50ms execution
"""

import os
import subprocess
import sys
from pathlib import Path


def check_skill_agent_modifications():
    """Check if skill/agent files were modified recently (proxy: git status)."""
    claude_home = Path.home() / ".claude"
    skills_dir = claude_home / "skills"
    agents_dir = claude_home / "agents"
    modified = []

    for check_dir, label in [(skills_dir, "skills"), (agents_dir, "agents")]:
        if not check_dir.exists():
            continue
        try:
            result = subprocess.run(
                ["git", "-C", str(check_dir), "status", "--porcelain"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                count = len(result.stdout.strip().splitlines())
                modified.append("%d modified %s file(s)" % (count, label))
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

    return modified


def check_workspace_uncommitted():
    """Check for uncommitted changes in current workspace."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            count = len(result.stdout.strip().splitlines())
            return "%d uncommitted change(s) in workspace" % count
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def check_session_tracking():
    """Check if auto-sync tracking file has entries."""
    tracking_file = os.path.join(os.getcwd(), ".tmp", "modified-this-session.json")
    if os.path.isfile(tracking_file):
        try:
            size = os.path.getsize(tracking_file)
            if size > 10:  # More than empty JSON
                return "Session tracking file has entries -- run sync before closing."
        except OSError:
            pass
    return None


def main():
    warnings = []

    modifications = check_skill_agent_modifications()
    if modifications:
        warnings.append("[aios-core] Unsaved changes detected: " + ", ".join(modifications))
        warnings.append("[aios-core] Run: python tools/sync-skills.py --sync --push")
        warnings.append("[aios-core] Run: python tools/sync-agents.py --sync --push")

    uncommitted = check_workspace_uncommitted()
    if uncommitted:
        warnings.append("[aios-core] " + uncommitted)

    tracking = check_session_tracking()
    if tracking:
        warnings.append("[aios-core] " + tracking)

    if warnings:
        # Output to stderr as non-blocking warnings
        print("\n".join(warnings), file=sys.stderr)
    else:
        print("[aios-core] Session clean -- no unsaved changes detected.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
