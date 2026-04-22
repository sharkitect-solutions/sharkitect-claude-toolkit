"""
hook-development-enforcer.py - PreToolUse BLOCKING hook for new-hook creation

DENIES Write calls that create a NEW hook file under .claude/hooks/ (global or
workspace) when the `hook-development` skill (or its `plugin-dev:hook-development`
form) has NOT been invoked this session.

Source: wr-2026-04-22-015 (skill-management-hub). Three new hooks built in a
session (log-tool-invocation.py, asset-registration-nudge.py,
verification-before-build-enforcer.py) without invoking hook-development. The
existing advisory in methodology-nudge.py was too easy to skip. This hook
hardens the check to BLOCK-tier enforcement, mirroring brainstorming-enforcer.

Memory rule: "If a rule keeps getting violated, add detection, don't reinforce
the rule." Advisory -> blocking escalation when advisory proves insufficient.

DETECTION (Signal B only -- kept narrow to minimize false positives)
  - Tool name is Write (not Edit -- edits are maintenance of existing hooks)
  - file_path matches .claude/hooks/*.py (global ~/.claude/hooks/ or workspace
    .claude/hooks/)
  - File does NOT yet exist (genuine new hook creation)

DOES NOT TRIGGER ON
  - Edit to existing hooks (maintenance, not new creation)
  - Write to hook TEMPLATE paths under skills/, plugins/, or docs/
  - Write to test files (tests/test_*.py next to hook dir)
  - Non-hook paths
  - Meta paths: /.work-requests/, /.lifecycle-reviews/, /.routed-tasks/,
    /.claude/projects/*/memory/ (gap reports + auto-memory about hook dev)

BYPASS
  1. Skill already invoked today: `hook-development` OR `plugin-dev:hook-development`
     (read from ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json)
  2. Recent user message contains: "skip hook-development", "no hook-development",
     "skip hook-dev"
  3. Current Write content contains one of the same bypass phrases (for filing
     gap reports ABOUT hook development without deadlock)

GRACEFUL DEGRADATION
  - Missing skill log -> ALLOW (no deadlock on missing tracker)
  - Missing transcript_path -> only content-bypass works
  - Any unhandled exception -> exit 0 (allow)

Pure stdlib. ASCII-only. Input/output: JSON via stdin/stdout.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"
PREFERRED_SKILL = "plugin-dev:hook-development"
FALLBACK_SKILL = "hook-development"

BYPASS_PHRASES = (
    "skip hook-development",
    "skip hook development",
    "skip hook-dev",
    "no hook-development",
    "no hook development",
)

# Hook path: global ~/.claude/hooks/*.py or workspace .claude/hooks/*.py
HOOK_PATH_RE = re.compile(r"[/\\]\.claude[/\\]hooks[/\\][^/\\]+\.py$", re.I)

# Meta paths exempt from blocking (gap reports + auto-memory may mention hooks)
META_PATH_MARKERS = (
    "/.work-requests/",
    "/.lifecycle-reviews/",
    "/.routed-tasks/",
    "/.claude/projects/",  # auto-memory
    "/memory/feedback_",
)

# Test files next to a hook dir are not hooks themselves
TEST_PATH_RE = re.compile(r"[/\\]tests?[/\\].*hook.*\.py$", re.I)


def load_skill_log():
    """Return list of skill names invoked today (lowercased)."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError):
        return []


def skill_invoked(skill_name, log):
    """Check if skill was invoked. Handles namespaced (plugin:skill) form."""
    target = skill_name.lower()
    for entry in log:
        if entry == target:
            return True
        # Match suffix: plugin-dev:hook-development matches hook-development
        if ":" in entry and entry.split(":", 1)[1] == target:
            return True
        if ":" in target and target.split(":", 1)[1] == entry:
            return True
    return False


def read_recent_user_messages(transcript_path, limit=5):
    """Read the last N user messages from the transcript JSONL."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return []
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    msgs = []
    for raw in reversed(lines):
        if len(msgs) >= limit:
            break
        try:
            rec = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue
        if rec.get("type") == "user":
            content = rec.get("message", {}).get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    str(c.get("text", "")) for c in content if isinstance(c, dict)
                )
            if isinstance(content, str) and content:
                msgs.append(content)
    return msgs


def has_bypass_phrase(msgs):
    for msg in msgs:
        low = msg.lower()
        if any(phrase in low for phrase in BYPASS_PHRASES):
            return True
    return False


def has_bypass_in_content(content):
    if not content:
        return False
    low = content.lower()
    return any(phrase in low for phrase in BYPASS_PHRASES)


def is_meta_path(file_path):
    if not file_path:
        return False
    norm = file_path.replace("\\", "/").lower()
    return any(marker in norm for marker in META_PATH_MARKERS)


def is_new_hook_write(file_path, tool_name):
    """True if this is a Write to a brand-new .claude/hooks/*.py file."""
    if tool_name != "Write":
        return False
    if not file_path:
        return False
    if TEST_PATH_RE.search(file_path):
        return False
    if not HOOK_PATH_RE.search(file_path):
        return False
    # Bias toward allow if file already exists (that's maintenance, not new creation)
    try:
        if os.path.isfile(file_path):
            return False
    except OSError:
        return False
    return True


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name != "Write":
        return 0

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")

    # Early exit: meta paths are structurally exempt (prevent recursion traps)
    if is_meta_path(file_path):
        return 0

    # Detect new-hook creation
    if not is_new_hook_write(file_path, tool_name):
        return 0

    # Bypass: skill already invoked
    log = load_skill_log()
    if skill_invoked(PREFERRED_SKILL, log) or skill_invoked(FALLBACK_SKILL, log):
        return 0

    # Bypass: phrase in recent user message
    transcript_path = data.get("transcript_path") or ""
    recent_msgs = read_recent_user_messages(transcript_path)
    if has_bypass_phrase(recent_msgs):
        return 0

    # Bypass: phrase in current tool content (for gap reports about hooks)
    content = str(tool_input.get("content", "") or "")
    if has_bypass_in_content(content):
        return 0

    # Block
    deny(
        "BLOCKING: New hook file detected at " + os.path.basename(file_path) + ". "
        "The `hook-development` skill MUST be invoked before writing new hook "
        "code. It loads patterns for PreToolUse/PostToolUse design, matcher "
        "scoping, graceful degradation, and false-positive bias -- all of "
        "which typically require 2-3 iterations to get right without the "
        "skill. Run `Skill plugin-dev:hook-development` (preferred) or "
        "`Skill hook-development`. To bypass: include \"skip hook-development\" "
        "in your message OR the hook file's docstring. Existing hooks can be "
        "edited freely (this hook only fires on NEW files). Meta paths under "
        "/.work-requests/ /.lifecycle-reviews/ /.routed-tasks/ "
        "/.claude/projects/*/memory/ are structurally exempt. "
        "Source: wr-2026-04-22-015."
    )
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
