"""
brainstorming-enforcer.py - PreToolUse BLOCKING hook for feature ideation work

DENIES TodoWrite or Write calls that look like the AI is jumping into feature
ideation / planning without first invoking the brainstorming skill (or
superpowers:brainstorming, the preferred form).

Source: wr-2026-04-18 (workforce-hq -- agent skipped brainstorming during a
7-thread feature roadmap session, defaulting to "organize + give feedback"
instead of divergent thinking). Memory rule: "If a rule keeps getting
violated, add detection, don't reinforce the rule."

DETECTION (either signal triggers)
  A. Recent user message in transcript contains feature-ideation keywords:
       brainstorm, plan out, think through, ideas for, what if we,
       should we build, lets plan / let's plan, feature ideas, roadmap
  B. Write target path looks like a NEW plan file:
       **/plan.md OR **/plans/*.md OR **/projects/*/plan*.md
     AND the write is to a path that does not yet exist (genuine new plan)

DOES NOT TRIGGER ON
  - Edit (only Write/TodoWrite -- edits are usually status updates)
  - Read/Bash/Glob/Grep (no creative content involved)
  - Existing-file Writes that are pure overwrites of small files
    (we treat these as updates, not new plans)

BYPASS (any of these allows the operation)
  1. Skill already invoked today (brainstorming OR superpowers:brainstorming)
     read from ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json
  2. Recent user message contains: "skip brainstorming", "no brainstorm",
     "skip ideation", "skip brainstorm"
  3. Hook removed from settings.json

GRACEFUL DEGRADATION
  - Missing skill log -> ALLOW (no deadlock).
  - Missing transcript_path -> only the keyword-in-content can trigger
    (Signal A becomes inert), and only the skill-log bypass works.
  - Any unhandled exception -> exit 0 (allow).

DESIGN TRADE-OFF (intentional false-negative bias)
  Borderline cases (e.g., a status-update edit on plan.md) ALLOW. We use
  Write-only + path-shape signals to keep status updates moving freely.
  False positives deadlock the agent; false negatives just skip a nudge.

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
PREFERRED_SKILL = "superpowers:brainstorming"
FALLBACK_SKILL = "brainstorming"

BYPASS_PHRASES = (
    "skip brainstorming",
    "skip brainstorm",
    "no brainstorm",
    "no brainstorming",
    "skip ideation",
)

# Ideation keywords scanned in the most-recent user messages.
IDEATION_KEYWORDS = [
    re.compile(r"\bbrainstorm\b", re.I),
    re.compile(r"\bplan\s+out\b", re.I),
    re.compile(r"\bthink\s+through\b", re.I),
    re.compile(r"\bideas\s+for\b", re.I),
    re.compile(r"\bwhat\s+if\s+we\b", re.I),
    re.compile(r"\bshould\s+we\s+build\b", re.I),
    re.compile(r"\b(?:lets|let'?s)\s+plan\b", re.I),
    re.compile(r"\bfeature\s+ideas?\b", re.I),
    re.compile(r"\broadmap\b", re.I),
]

# Plan-file path patterns. Forward and back slashes both supported.
PLAN_PATH_RE = re.compile(
    r"(?:"
    r"[/\\]plan\.md$"
    r"|[/\\]plans?[/\\][^/\\]+\.md$"
    r"|[/\\]projects[/\\][^/\\]+[/\\]plan[^/\\]*\.md$"
    r")",
    re.I,
)

# Look-back window for transcript user messages.
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
    """Return up to TRANSCRIPT_USER_LOOKBACK most-recent user message texts.
    Graceful: any failure -> [].
    """
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


def has_ideation_keyword(messages):
    for txt in messages:
        for pat in IDEATION_KEYWORDS:
            if pat.search(txt):
                return True
    return False


def is_new_plan_write(file_path, tool_name):
    """True if the Write target looks like creating a NEW plan file.
    Conservative: requires both the path to match AND the file to not yet
    exist (so we don't block status-update overwrites of existing plans).
    """
    if tool_name != "Write":
        return False
    if not file_path:
        return False
    if not PLAN_PATH_RE.search(file_path):
        return False
    # Borderline: if file already exists, treat as update -> allow.
    # This intentionally biases toward false-negative (allow) to avoid
    # deadlocking on routine plan edits.
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
    if tool_name not in ("TodoWrite", "Write"):
        return 0

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")

    # ---- Detect ----------------------------------------------------------
    transcript_path = data.get("transcript_path") or ""
    recent_msgs = read_recent_user_messages(transcript_path)

    signal_a = has_ideation_keyword(recent_msgs)
    signal_b = is_new_plan_write(file_path, tool_name)

    if not (signal_a or signal_b):
        return 0  # no trigger

    # ---- Bypass ----------------------------------------------------------
    log = load_skill_log()
    if skill_invoked(PREFERRED_SKILL, log) or skill_invoked(FALLBACK_SKILL, log):
        return 0

    # User-override phrase (in any of the recent messages)
    if has_bypass_phrase(recent_msgs):
        return 0

    # ---- Block -----------------------------------------------------------
    trigger_label = []
    if signal_a:
        trigger_label.append("user message with ideation keyword")
    if signal_b:
        trigger_label.append("new plan file: " + os.path.basename(file_path))
    label = " + ".join(trigger_label) if trigger_label else "ideation context"

    deny(
        "BLOCKING: Feature ideation or planning context detected (" + label + "). "
        "The brainstorming skill MUST be invoked before drafting plans or "
        "creating new features. The skill applies divergent-thinking patterns "
        "that catch alternatives the default flow misses. Run "
        "`Skill superpowers:brainstorming` (preferred) or `Skill brainstorming`. "
        "To bypass for status updates or pure execution, include "
        "\"skip brainstorming\" in your message and retry. "
        "Source: wr-2026-04-18. See docs/hook-classification-policy.md."
    )
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
