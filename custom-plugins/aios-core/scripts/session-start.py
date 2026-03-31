"""
session-start.py - SessionStart hook for aios-core
Detects current workspace and outputs workspace-specific context.
Checks for post-compact recovery file and alerts if available.

Detection priority:
  1. CLAUDE.md PROJECT_PURPOSE field (explicit, portable)
  2. Path-based fallback (legacy, works without CLAUDE.md)
  3. Generic default

Exit codes: 0 = success, 2 = blocking error
Target: sub-50ms execution
"""

import os
import re
import sys


# ---------------------------------------------------------------------------
# Workspace detection
# ---------------------------------------------------------------------------

def detect_from_claude_md(cwd):
    """Primary detection: read PROJECT_PURPOSE from CLAUDE.md."""
    claude_md = os.path.join(cwd, "CLAUDE.md")
    if not os.path.isfile(claude_md):
        return None

    try:
        with open(claude_md, "r", encoding="utf-8") as f:
            content = f.read(4096)  # Only need the top of the file
    except (OSError, UnicodeDecodeError):
        return None

    # Match PROJECT_PURPOSE line (supports bold markdown and plain)
    match = re.search(
        r"\*{0,2}PROJECT_PURPOSE:?\*{0,2}\s*(.+)",
        content,
        re.IGNORECASE,
    )
    if not match:
        return None

    purpose = match.group(1).strip()
    purpose_lower = purpose.lower()

    # Map purpose keywords to workspace types
    if "skill management" in purpose_lower or "toolkit" in purpose_lower:
        return "skill-management-hub"
    if "workforce" in purpose_lower or "business operations" in purpose_lower or "hq" in purpose_lower:
        return "workforce-hq"
    if "client" in purpose_lower:
        return "client-project"

    # PURPOSE exists but doesn't match known types -- return it as-is
    # so the context block can display the actual purpose
    return ("custom", purpose)


def detect_from_path(cwd):
    """Fallback detection: infer workspace type from directory path."""
    cwd_lower = cwd.lower().replace("\\", "/")

    if "skill-management-hub" in cwd_lower or "skill management hub" in cwd_lower:
        return "skill-management-hub"
    if "workforce" in cwd_lower or "workspace-hq" in cwd_lower or "workspace hq" in cwd_lower:
        return "workforce-hq"
    if "client" in cwd_lower:
        return "client-project"
    return None


def detect_workspace(cwd):
    """Detect workspace type using layered strategy."""
    # 1. Primary: CLAUDE.md PROJECT_PURPOSE
    result = detect_from_claude_md(cwd)
    if result is not None:
        return result

    # 2. Fallback: path-based matching
    result = detect_from_path(cwd)
    if result is not None:
        return result

    # 3. Default: unknown
    return "unknown"


# ---------------------------------------------------------------------------
# Context generation
# ---------------------------------------------------------------------------

def get_workspace_context(workspace, cwd):
    """Return workspace-specific context lines."""
    # Handle custom workspace (tuple from CLAUDE.md detection)
    if isinstance(workspace, tuple) and workspace[0] == "custom":
        purpose = workspace[1]
        return [
            "[aios-core] Workspace: %s" % os.path.basename(cwd),
            "Project purpose: %s" % purpose,
            "Read MEMORY.md for project context and resume instructions.",
        ]

    contexts = {
        "skill-management-hub": [
            "[aios-core] Workspace: Skill Management Hub",
            "Tools: sync-skills.py, sync-agents.py, audit-plugins.py, plugin-scaffold.py",
            "Workflows: plugin-build.md, plugin-audit.md, skill-sync.md",
            "Read MEMORY.md for current phase and resume instructions.",
        ],
        "workforce-hq": [
            "[aios-core] Workspace: WORKFORCE HQ",
            "Context: Sharkitect Digital business operations and AI workforce management.",
            "Read MEMORY.md for active projects, client work, and priorities.",
        ],
        "client-project": [
            "[aios-core] Workspace: Client Project",
            "Read MEMORY.md and CLAUDE.md for project-specific context.",
        ],
    }

    default = [
        "[aios-core] Workspace: %s" % os.path.basename(cwd),
        "Read MEMORY.md for project context.",
    ]

    return contexts.get(workspace, default)


# ---------------------------------------------------------------------------
# Recovery check
# ---------------------------------------------------------------------------

def check_compact_recovery(cwd):
    """Check if a post-compact recovery file exists from a previous compaction."""
    recovery_path = os.path.join(cwd, ".tmp", "compact-context.md")
    if os.path.isfile(recovery_path):
        try:
            stat = os.stat(recovery_path)
            size_kb = stat.st_size / 1024
            return (
                "[aios-core] Post-compact recovery available: "
                ".tmp/compact-context.md (%.1f KB) -- "
                "read it to restore session context from before compaction."
                % size_kb
            )
        except OSError:
            pass
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    cwd = os.getcwd()
    workspace = detect_workspace(cwd)
    lines = get_workspace_context(workspace, cwd)

    recovery = check_compact_recovery(cwd)
    if recovery:
        lines.append(recovery)

    # stdout gets injected into session context
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
