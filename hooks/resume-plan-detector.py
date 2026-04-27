"""
resume-plan-detector.py -- Nudge superpowers:executing-plans when a structured
                            resume plan exists in the workspace's auto-memory.

Fires on SessionStart. Detects ~/.claude/projects/<workspace-id>/memory/resume_*.md
files. If the file has plan-like structure (carry-over tables, decision rules,
"what to check" sections), outputs a soft nudge to invoke
superpowers:executing-plans before proceeding.

Source: wr-hq-2026-04-27-004 (HQ filed). Pattern observed during 2026-04-27
ICP-cascade session: HQ followed resume_next_session.md task-by-task using
TodoWrite + manual sequencing rather than the executing-plans methodology.
The plan went smoothly because the discipline was internalized, but other
plans without that internal discipline would silently fail. The named-skill
enforcement protocol exists specifically to prevent this.

Non-blocking: exits 0 always. Only emits a nudge when:
  1. resume_*.md file exists in workspace auto-memory
  2. File has plan-like structural markers (numbered carry-overs, decision rules,
     status tables, or explicit "REQUIRED SUB-SKILL" / "executing-plans" text)
  3. Once-per-session debounce via .tmp/.resume-plan-nudge-<plan-hash>

Dependencies: Python stdlib only.
"""

import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path


# Plan-like structural signals. Need 2+ of these to trigger the nudge.
# This is intentionally loose -- false positives nudge gently, false
# negatives leave the user without the discipline reinforcement.
PLAN_PATTERNS = [
    # Explicit named-skill marker -- highest signal
    re.compile(r"REQUIRED SUB-SKILL", re.IGNORECASE),
    re.compile(r"superpowers:executing-plans|executing-plans skill", re.IGNORECASE),
    # Numbered carry-overs / phases / steps
    re.compile(r"^\s*##?\s*(carry-?overs?|phases?|steps?|tasks?)\b", re.IGNORECASE | re.MULTILINE),
    # Decision rules -- very characteristic of structured plans
    re.compile(r"\bdecision rule\b", re.IGNORECASE),
    # "What to check" -- another characteristic plan section
    re.compile(r"\bwhat to check\b", re.IGNORECASE),
    # Status tables (carry-over / done / pending grids)
    re.compile(r"\|\s*(status|carry-over|task|step|phase)\s*\|", re.IGNORECASE),
    # Structured status tracking
    re.compile(r"^\s*##?\s*(All\s+\d+|next session priority|pick up first)", re.IGNORECASE | re.MULTILINE),
]


def _sanitize_cwd_for_project_dir(cwd_str):
    """Mirror Claude Code's project-dir sanitization for the current cwd.

    Algorithm (verified empirically 2026-04-27):
      1. Replace each non-alphanumeric character with '-' (preserves case
         on alphanumerics, including consecutive non-alpha runs becoming
         multi-dash sequences).
      2. Lowercase ONLY the leading drive-letter character (Windows
         drive letters render lowercase in the project dir name).

    Examples:
      C:\\Users\\Sharkitect Digital\\Documents\\Claude Code Workspaces\\1.- SHARKITECT DIGITAL WORKFORCE HQ
      -> c--Users-Sharkitect-Digital-Documents-Claude-Code-Workspaces-1---SHARKITECT-DIGITAL-WORKFORCE-HQ
    """
    s = re.sub(r"[^a-zA-Z0-9]", "-", cwd_str)
    if s and s[0].isalpha():
        s = s[0].lower() + s[1:]
    return s


def detect_workspace_id():
    """Map cwd to the ~/.claude/projects/<sanitized>/ directory."""
    projects_root = Path.home() / ".claude" / "projects"
    if not projects_root.exists():
        return None
    sanitized = _sanitize_cwd_for_project_dir(str(Path.cwd()))
    candidate = projects_root / sanitized
    if candidate.exists() and candidate.is_dir():
        return candidate
    # Fallback: case-insensitive match in case the algorithm differs slightly
    # (e.g., trailing slash variants, OS quirks).
    target_lower = sanitized.lower()
    for child in projects_root.iterdir():
        if child.is_dir() and child.name.lower() == target_lower:
            return child
    return None


def find_resume_plans(memory_dir):
    """Scan memory_dir for resume_*.md files. Returns list of paths."""
    if not memory_dir or not memory_dir.exists():
        return []
    return sorted(memory_dir.glob("resume_*.md"))


def looks_like_structured_plan(content):
    """Return True if content has 2+ plan-like structural markers."""
    matches = sum(1 for pat in PLAN_PATTERNS if pat.search(content))
    return matches >= 2


def session_already_nudged(plan_hash, tmp_dir):
    """Check debounce file. Returns True if we've already nudged for this plan in this session."""
    marker = tmp_dir / f".resume-plan-nudge-{plan_hash}"
    return marker.exists()


def mark_session_nudged(plan_hash, tmp_dir):
    """Drop debounce marker so we don't nudge twice for the same plan."""
    marker = tmp_dir / f".resume-plan-nudge-{plan_hash}"
    try:
        marker.write_text(datetime.now().isoformat(), encoding="utf-8")
    except OSError:
        pass


def main():
    # Find workspace's auto-memory directory.
    workspace_dir = detect_workspace_id()
    if workspace_dir is None:
        sys.exit(0)

    memory_dir = workspace_dir / "memory"
    plans = find_resume_plans(memory_dir)
    if not plans:
        sys.exit(0)

    # Find the most recently modified plan that has plan-like structure.
    # We only surface ONE -- the most relevant -- not all of them.
    # Sort by mtime desc; pick first that matches.
    plans_sorted = sorted(plans, key=lambda p: p.stat().st_mtime, reverse=True)
    selected = None
    for plan in plans_sorted:
        try:
            content = plan.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if looks_like_structured_plan(content):
            selected = plan
            break

    if selected is None:
        sys.exit(0)

    # Debounce per-session per-plan.
    tmp_dir = Path.cwd() / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    plan_hash = hashlib.sha1(str(selected).encode("utf-8")).hexdigest()[:12]
    if session_already_nudged(plan_hash, tmp_dir):
        sys.exit(0)
    mark_session_nudged(plan_hash, tmp_dir)

    # Emit the nudge. Soft, non-blocking. Output goes into the AI's startup context.
    rel_path = selected.relative_to(Path.home() / ".claude")
    print("=== RESUME PLAN DETECTED ===")
    print(f"A structured carry-over plan exists at ~/.claude/{rel_path}")
    print("")
    print("Before starting work, invoke superpowers:executing-plans to follow it")
    print("with discipline. This ensures verification-before-completion at each")
    print("step, audit trail of plan-step transitions, and structured execution")
    print("rather than ad-hoc TodoWrite + manual sequencing.")
    print("")
    print("(Source: wr-hq-2026-04-27-004. To bypass for ad-hoc work, just")
    print("acknowledge and continue -- this is a soft nudge, not a gate.)")

    sys.exit(0)


if __name__ == "__main__":
    main()
