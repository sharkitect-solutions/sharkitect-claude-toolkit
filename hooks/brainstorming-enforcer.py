"""
brainstorming-enforcer.py - PreToolUse BLOCKING hook for feature ideation work

DENIES TodoWrite or Write calls that look like the AI is jumping into feature
ideation / planning without first invoking the brainstorming skill (or
superpowers:brainstorming, the preferred form).

Source: wr-2026-04-18 (workforce-hq -- agent skipped brainstorming during a
7-thread feature roadmap session, defaulting to "organize + give feedback"
instead of divergent thinking). Extended by wr-2026-04-20-001 (HQ Paramount
tagline pitch) to catch candidate-pitching in assistant tool output and to
fix the recursion trap that blocked filing gap reports about the hook itself.
Memory rule: "If a rule keeps getting violated, add detection, don't
reinforce the rule."

DETECTION (any signal triggers)
  A. Recent user message in transcript contains feature-ideation keywords:
       brainstorm, plan out, think through, ideas for, what if we,
       should we build, lets plan / let's plan, feature ideas, roadmap,
       naming patterns (name options, naming candidates, etc.)
  B. Write target path looks like a NEW plan file:
       **/plan.md OR **/plans/*.md OR **/projects/*/plan*.md
     AND the write is to a path that does not yet exist (genuine new plan)
  C. Tool content (Write content / TodoWrite todos) contains an
     explicit candidate-pitching pattern: BOTH a domain keyword (tagline,
     slogan, brand name, product name, campaign name, naming, rebrand)
     AND an ideation header ("Tagline options", "Naming candidates",
     "Here are 5 campaign names", etc.). Requiring the header (not just
     a nearby numbered list) honors the hook's false-negative bias:
     decision records and style guides that happen to list things
     without pitching them as candidates are allowed. Added by
     wr-2026-04-20-001 after the Paramount tagline incident.

DOES NOT TRIGGER ON
  - Edit (only Write/TodoWrite -- edits are usually status updates)
  - Read/Bash/Glob/Grep (no creative content involved)
  - Existing-file Writes that are pure overwrites of small files
    (we treat these as updates, not new plans)
  - Writes to meta paths: /.work-requests/, /.lifecycle-reviews/,
    /.routed-tasks/. These hold gap reports and cross-workspace
    coordination docs that describe ideation workflows; blocking them
    creates a recursion trap (wr-2026-04-20-001).

BYPASS (any of these allows the operation)
  1. Skill already invoked today (brainstorming OR superpowers:brainstorming)
     read from ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json
  2. Recent user message contains: "skip brainstorming", "no brainstorm",
     "skip ideation", "skip brainstorm"
  3. The current Write content OR a TodoWrite todo contains one of the
     same bypass phrases (lets the assistant file legitimate
     reports/documentation about prior ideation without deadlock).
     Added by wr-2026-04-20-001.
  4. Hook removed from settings.json

GRACEFUL DEGRADATION
  - Missing skill log -> ALLOW (no deadlock).
  - Missing transcript_path -> only the keyword-in-content can trigger
    (Signal A becomes inert), and only the skill-log bypass works.
  - Any unhandled exception -> exit 0 (allow).

DESIGN TRADE-OFF (intentional false-negative bias)
  Borderline cases (e.g., a status-update edit on plan.md) ALLOW. We use
  Write-only + path-shape signals to keep status updates moving freely.
  False positives deadlock the agent; false negatives just skip a nudge.

Tests: tests/test_brainstorming_enforcer.py in Skill Management Hub.

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
    # Naming-work triggers -- wr-2026-04-19 brainstorming-skipped-naming (HQ):
    # multi-round name options (5+ for CardOps) without brainstorming skill.
    # Naming = divergent thinking, matches the skill's expected-input matrix.
    re.compile(r"\bname\s+(?:it|options?|candidates?|for\s+(?:the|this|our))\b", re.I),
    re.compile(r"\bnaming\s+(?:exercise|options?|candidates?|round|ideas?|conventions?)\b", re.I),
    re.compile(r"\bwhat\s+(?:should|could)\s+we\s+(?:call|name)\b", re.I),
    re.compile(r"\bsuggest\s+(?:a\s+|some\s+|\d+\s+|(?:a\s+)?few\s+)?name[s]?\b", re.I),
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

# Meta paths: structurally exempt. Gap reports, lifecycle reviews, and
# cross-workspace routed tasks describe ideation workflows by nature;
# blocking Writes to these paths makes it impossible to file bugs about
# the ideation system itself. Source: wr-2026-04-20-001.
#
# Auto-memory paths (~/.claude/projects/*/memory/) added 2026-04-22 per
# wr-2026-04-21-010: memory files are fact capture (feedback memories,
# user preferences, session notes), never feature ideation. Exempting
# them eliminates the false positive where a feedback_*.md write gets
# blocked because the session happened to discuss features earlier.
META_PATH_MARKERS = (
    "/.work-requests/",
    "/.lifecycle-reviews/",
    "/.routed-tasks/",
    "/.claude/projects/",  # auto-memory and per-project state
    "/.claude/memory/",    # workspace memory topic files
    "/memory/feedback_",   # explicit feedback file naming convention
)

# Domain keywords scoped to branding/naming/campaign work where divergent
# thinking is most commonly substituted for candidate-pitching. Kept
# narrow to prevent false positives on generic numbered lists
# (feature lists, steps, TODOs).
DOMAIN_KEYWORDS_RE = re.compile(
    r"\b(?:"
    r"taglines?|slogans?|"
    r"brand\s+names?|product\s+names?|company\s+names?|"
    r"campaign\s+names?|project\s+names?|"
    r"naming(?:\s+(?:exercise|round|convention))?s?|"
    r"rebrand(?:ing)?|"
    r"headline\s+options?"
    r")\b",
    re.I,
)

# Explicit ideation headers such as "Tagline options", "Name candidates",
# "Here are 5 campaign names".
IDEATION_HEADER_RE = re.compile(
    r"\b(?:tagline|slogan|name|naming|campaign|headline)s?\s+"
    r"(?:option|candidate|idea|choice|suggestion)s?\b"
    r"|\bhere\s+are\s+(?:\d+|a\s+few|some)\s+"
    r"(?:tagline|slogan|name|naming|campaign|headline)",
    re.I,
)

# Note: a numbered-list signal was considered (domain keyword + adjacent
# 2-5 short items) but rejected for this iteration. It false-positives on
# style guides ("Tagline conventions: 1. short, 2. active voice") and
# decision records ("Product name: X. Reasons: 1. ..."). If a
# header-less candidate pitch slips through in the wild, file a follow-up
# WR and reconsider with a commit-language exclusion.

# Look-back window for transcript user messages.
TRANSCRIPT_USER_LOOKBACK = 3

# Config-doc basenames that are exempt from Signals A and C when the file
# already exists. These files are operational config / structural docs;
# rewriting them is realignment, not new feature ideation. Source:
# wr-hq-2026-04-29-005 -- HQ session blocked on CLAUDE.md realignment to
# the Skill Hub/Sentinel template (Signal C fired on 'Tagline options'
# substring inside the doc body, despite the rewrite being structural).
# Match is case-insensitive on basename. Existence check is required so
# brand-new file creation can still trigger if other signals fire (rare
# case but worth flagging when it happens).
CONFIG_DOC_BASENAMES = (
    "claude.md",
    "memory.md",
    "readme.md",
    "agents.md",
    "gemini.md",
)

# System-injected blocks to strip BEFORE keyword matching. Fixes a false
# positive where hook-injected system reminders (e.g., RESOURCE AUDIT
# REMINDER) contained words like "alternatives", "plans", "options" and
# got matched as user ideation keywords. Source: wr-2026-04-19
# brainstorming-hook-false-positive (HQ).
SYSTEM_BLOCK_TAGS = (
    "system-reminder",
    "user-prompt-submit-hook",
    "command-message",
    "command-name",
    "command-args",
    "command-stdout",
    "command-stderr",
    "ide_selection",
    "local-command-stdout",
    "local-command-stderr",
)
SYSTEM_BLOCK_RE = re.compile(
    r"<(?:" + "|".join(SYSTEM_BLOCK_TAGS) + r")\b[^>]*>.*?</(?:"
    + "|".join(SYSTEM_BLOCK_TAGS) + r")\s*>",
    re.S | re.I,
)


def strip_system_blocks(text):
    """Remove system-injected tag blocks so their text is not scanned as user
    intent. Handles unclosed/nested tags gracefully (non-greedy match).
    """
    if not text:
        return ""
    try:
        return SYSTEM_BLOCK_RE.sub("", text)
    except Exception:
        return text


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
        clean = strip_system_blocks(txt)
        low = clean.lower()
        if any(phrase in low for phrase in BYPASS_PHRASES):
            return True
    return False


def has_ideation_keyword(messages):
    for txt in messages:
        clean = strip_system_blocks(txt)
        for pat in IDEATION_KEYWORDS:
            if pat.search(clean):
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


def is_existing_config_doc(file_path):
    """True if Write target is an existing config/structural doc (CLAUDE.md,
    MEMORY.md, README.md, AGENTS.md, GEMINI.md). Exempt from Signals A and C
    because rewriting these is structural realignment, not feature ideation.

    Source: wr-hq-2026-04-29-005. Existence required so brand-new creates
    still trigger when ideation patterns are present.
    """
    if not file_path:
        return False
    basename = os.path.basename(file_path).lower()
    if basename not in CONFIG_DOC_BASENAMES:
        return False
    try:
        return os.path.isfile(file_path)
    except OSError:
        return False


def is_meta_path(file_path):
    """True if Write target is a work-request / lifecycle / routed-task
    path. These paths hold meta-documentation that describes ideation
    workflows by nature; blocking Writes to them creates a recursion trap
    where the system cannot file bugs about itself (wr-2026-04-20-001).
    """
    if not file_path:
        return False
    norm = file_path.replace("\\", "/").lower()
    return any(marker in norm for marker in META_PATH_MARKERS)


def extract_write_content(tool_name, tool_input):
    """Return the textual content being written by this tool call.
    For Write: the content field. For TodoWrite: concatenated todo
    content + activeForm fields. Returns "" for anything else.
    """
    if not isinstance(tool_input, dict):
        return ""
    if tool_name == "Write":
        content = tool_input.get("content", "")
        return content if isinstance(content, str) else ""
    if tool_name == "TodoWrite":
        todos = tool_input.get("todos", [])
        if not isinstance(todos, list):
            return ""
        parts = []
        for t in todos:
            if isinstance(t, dict):
                parts.append(str(t.get("content", "")))
                parts.append(str(t.get("activeForm", "")))
        return "\n".join(parts)
    return ""


def has_ideation_content_pattern(text):
    """Signal C: tool output contains an explicit candidate-pitching
    pattern. Requires BOTH a domain keyword AND an ideation header.
    Requiring the header (not just a nearby numbered list) honors the
    hook's false-negative bias and avoids triggering on decision
    records, style guides, or templates that mention naming topics.
    """
    if not text or len(text) < 20:
        return False
    if not DOMAIN_KEYWORDS_RE.search(text):
        return False
    if not IDEATION_HEADER_RE.search(text):
        return False
    return True


def has_bypass_in_content(content):
    """True if the current Write/TodoWrite content itself contains a
    bypass phrase. Lets the assistant file legitimate reports or
    documentation about prior ideation without deadlock
    (wr-2026-04-20-001: gap reports were blocked by this very hook).
    """
    if not content:
        return False
    low = content.lower()
    return any(phrase in low for phrase in BYPASS_PHRASES)


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
    # Only Write is inspected now. TodoWrite was removed 2026-04-22 per
    # wr-2026-04-21-010: TodoWrite is session-state tracking, never an
    # ideation surface, and blocking it cost 1-2 turns per false positive
    # when sessions touched ideation keywords earlier.
    if tool_name != "Write":
        return 0

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")

    # ---- Early exit: meta paths are structurally exempt -----------------
    # Gap reports, lifecycle reviews, routed tasks, and auto-memory files
    # are meta-docs ABOUT workflows or fact-capture files, not ideation
    # surfaces. Blocking them creates recursion traps (filing bugs about
    # ideation = blocked; capturing user feedback about ideation = blocked).
    # Source: wr-2026-04-20-001, wr-2026-04-21-010.
    if is_meta_path(file_path):
        return 0

    # ---- Detect ----------------------------------------------------------
    transcript_path = data.get("transcript_path") or ""
    recent_msgs = read_recent_user_messages(transcript_path)
    content = extract_write_content(tool_name, tool_input)

    # Existing config-doc exemption (wr-hq-2026-04-29-005): rewrites of
    # CLAUDE.md / MEMORY.md / README.md / AGENTS.md / GEMINI.md are
    # structural realignment, not feature ideation. Suppress Signals A
    # and C; Signal B (new-plan-file path) is orthogonal and these
    # basenames don't match the plan path regex anyway.
    config_doc_rewrite = is_existing_config_doc(file_path)

    signal_a = has_ideation_keyword(recent_msgs) and not config_doc_rewrite
    signal_b = is_new_plan_write(file_path, tool_name)
    signal_c = has_ideation_content_pattern(content) and not config_doc_rewrite

    if not (signal_a or signal_b or signal_c):
        return 0  # no trigger

    # ---- Bypass ----------------------------------------------------------
    log = load_skill_log()
    if skill_invoked(PREFERRED_SKILL, log) or skill_invoked(FALLBACK_SKILL, log):
        return 0

    # User-override phrase (in any of the recent messages)
    if has_bypass_phrase(recent_msgs):
        return 0

    # Also honor a bypass phrase embedded in the current tool content
    # (wr-2026-04-20-001 -- gap reports need to describe prior ideation).
    if has_bypass_in_content(content):
        return 0

    # ---- Block -----------------------------------------------------------
    trigger_label = []
    if signal_a:
        trigger_label.append("user message with ideation keyword")
    if signal_b:
        trigger_label.append("new plan file: " + os.path.basename(file_path))
    if signal_c:
        trigger_label.append("candidate-pitching pattern in tool content")
    label = " + ".join(trigger_label) if trigger_label else "ideation context"

    deny(
        "BLOCKING: Feature ideation or planning context detected (" + label + "). "
        "The brainstorming skill MUST be invoked before drafting plans or "
        "creating new features. The skill applies divergent-thinking patterns "
        "that catch alternatives the default flow misses. Run "
        "`Skill superpowers:brainstorming` (preferred) or `Skill brainstorming`. "
        "To bypass: include \"skip brainstorming\" in your message OR in the "
        "tool content itself. Gap reports, lifecycle reviews, and routed "
        "tasks under /.work-requests/ /.lifecycle-reviews/ /.routed-tasks/ "
        "and auto-memory files under /.claude/projects/*/memory/ are "
        "structurally exempt. TodoWrite is no longer inspected. "
        "Source: wr-2026-04-18, wr-2026-04-20-001, wr-2026-04-21-010. "
        "See docs/hook-classification-policy.md."
    )
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
