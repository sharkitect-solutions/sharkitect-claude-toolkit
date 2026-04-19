"""
writing-plans-enforcer.py - PreToolUse BLOCKING hook for multi-section plan docs

DENIES Write/Edit calls that create or expand plan documents without first
invoking the writing-plans skill (or superpowers:writing-plans, the
preferred form). Catches the case where a multi-thread plan is drafted
freehand and skips the quality checklist (risk register, rollback plan,
measurable per-thread completion criteria, review cadence).

Source: wr-2026-04-18 (workforce-hq -- 200+ line plan with 7 threads written
without the skill, missing risk register and rollback). Memory rule: "If a
rule keeps getting violated, add detection, don't reinforce the rule."

DETECTION
  Path matches one of:
    **/plan.md
    **/plans/*.md
    **/projects/*/plan*.md
  AND content signals a real plan body:
    - For Write: any non-trivial content (>= 200 chars; small Writes treated
      as scaffolds, allowed)
    - For Edit: new_string adds 50+ lines OR contains plan structural keywords
      ('## Phase', '## Thread', '## Milestone', 'Success criteria',
      'Risk register', 'Dependencies:')

DOES NOT TRIGGER ON
  - Read/Bash/Glob/Grep/TodoWrite (no plan content involved)
  - Edit with new_string under 50 lines AND no plan-structural keywords
    (treated as a status update, allowed)
  - Tiny Write (< 200 chars) -- treated as scaffold/placeholder, allowed

BYPASS (any of these allows the operation)
  1. writing-plans OR superpowers:writing-plans invoked today
     (read from ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json)
  2. Recent user message in transcript contains:
       "skip writing-plans", "skip plan-skill", "status update only"
  3. Hook removed from settings.json

GRACEFUL DEGRADATION
  - Missing skill log -> ALLOW (no deadlock).
  - Missing transcript_path -> only the skill-log bypass works.
  - Any unhandled exception -> exit 0 (allow).

DESIGN TRADE-OFF (intentional false-negative bias)
  Borderline edits (e.g., adding a status table to plan.md) ALLOW. We use
  the 50-line / structural-keyword threshold to catch the "drafting a real
  plan body" case while letting routine edits through.

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
PREFERRED_SKILL = "superpowers:writing-plans"
FALLBACK_SKILL = "writing-plans"

BYPASS_PHRASES = (
    "skip writing-plans",
    "skip plan-skill",
    "skip writing plans",
    "status update only",
    "skip writing-plans-enforcer",
)

PLAN_PATH_RE = re.compile(
    r"(?:"
    r"[/\\]plan\.md$"
    r"|[/\\]plans?[/\\][^/\\]+\.md$"
    r"|[/\\]projects[/\\][^/\\]+[/\\]plan[^/\\]*\.md$"
    r")",
    re.I,
)

# Plan-structural keywords. Hitting any of these in new content is a strong
# signal that a real plan body is being written (vs. a status edit).
PLAN_STRUCTURAL_RES = [
    re.compile(r"##\s+Phase\b", re.I),
    re.compile(r"##\s+Thread\b", re.I),
    re.compile(r"##\s+Milestone\b", re.I),
    re.compile(r"\bSuccess\s+criteria\b", re.I),
    re.compile(r"\bRisk\s+register\b", re.I),
    re.compile(r"\bDependencies\s*:", re.I),
]

# Write content threshold (chars) below which we treat it as scaffolding.
WRITE_MIN_CHARS = 200
# Edit new_string threshold (lines) above which we consider it a real expand.
EDIT_MIN_LINES = 50

TRANSCRIPT_USER_LOOKBACK = 3


def load_skill_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return []


def skill_invoked(name, log):
    target = name.lower()
    return any(
        e == target or e.endswith(":" + target) or e.startswith(target + ":")
        for e in log
    )


def read_recent_user_messages(transcript_path):
    if not transcript_path:
        return []
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return []
        msgs = []
        try:
            with p.open("r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except (json.JSONDecodeError, ValueError):
                        continue
                    if rec.get("type") != "user":
                        continue
                    msg = rec.get("message") or {}
                    content = msg.get("content")
                    if isinstance(content, str):
                        msgs.append(content)
                    elif isinstance(content, list):
                        for blk in content:
                            if isinstance(blk, dict) and blk.get("type") == "text":
                                msgs.append(blk.get("text", ""))
        except (OSError, UnicodeDecodeError):
            return []
        return msgs[-TRANSCRIPT_USER_LOOKBACK:]
    except Exception:
        return []


def has_bypass_phrase(messages):
    for txt in messages:
        low = txt.lower()
        if any(phrase in low for phrase in BYPASS_PHRASES):
            return True
    return False


def has_plan_structural_keyword(text):
    if not text:
        return False
    snippet = text[:8000]
    for pat in PLAN_STRUCTURAL_RES:
        if pat.search(snippet):
            return True
    return False


def is_real_plan_write(tool_name, content):
    """Decide whether the Write/Edit is a real plan body (worth blocking on)
    vs. a small status update / scaffold (allow).
    """
    if tool_name == "Write":
        if not content:
            return False
        if len(content) < WRITE_MIN_CHARS:
            return False  # scaffold/placeholder -- allow
        return True

    if tool_name == "Edit":
        if not content:
            return False
        line_count = content.count("\n") + 1
        if line_count >= EDIT_MIN_LINES:
            return True
        if has_plan_structural_keyword(content):
            return True
        return False

    return False


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
    if tool_name not in ("Write", "Edit"):
        return 0

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")
    if not file_path or not PLAN_PATH_RE.search(file_path):
        return 0  # not a plan-file path

    if tool_name == "Write":
        content = str(tool_input.get("content", "") or "")
    else:
        content = str(tool_input.get("new_string", "") or "")

    if not is_real_plan_write(tool_name, content):
        return 0  # too small / status update -- allow

    # ---- Bypass ----------------------------------------------------------
    log = load_skill_log()
    if skill_invoked(PREFERRED_SKILL, log) or skill_invoked(FALLBACK_SKILL, log):
        return 0

    transcript_path = data.get("transcript_path") or ""
    recent_msgs = read_recent_user_messages(transcript_path)
    if has_bypass_phrase(recent_msgs):
        return 0

    # ---- Block -----------------------------------------------------------
    deny(
        "BLOCKING: Writing a multi-section plan document (" + os.path.basename(file_path) + "). "
        "The writing-plans skill MUST be invoked before drafting -- it enforces "
        "risk register, rollback plan, measurable per-thread done criteria, "
        "and review cadence. Run `Skill superpowers:writing-plans` (preferred) "
        "or `Skill writing-plans`. To bypass for incremental status updates, "
        "include \"status update only\" in your message and retry. "
        "Source: wr-2026-04-18. See docs/hook-classification-policy.md."
    )
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
