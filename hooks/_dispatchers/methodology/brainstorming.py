"""brainstorming.py - Methodology dispatcher sub-rule.

Source: brainstorming-enforcer.py (HARD GATE on new plan file writes /
ideation context / candidate-pitching content without superpowers:brainstorming
invoked).

Behavior preserved 1:1 from source:
  Signal A: recent user message contains ideation keywords (brainstorm,
            plan out, ideas for, what if we, naming, roadmap, etc.)
  Signal B: Write to a NEW plan file (plans/*.md, plan.md, projects/X/plan*.md
            where the file does not yet exist)
  Signal C: tool content contains BOTH a domain keyword (tagline, slogan,
            brand name, campaign name, etc.) AND an ideation header
            ("Tagline options", "Naming candidates", "Here are 5 names")

Bypasses (any one passes through):
  1. Skill log: brainstorming OR superpowers:brainstorming invoked today
  2. Transcript bypass phrase: "skip brainstorming", "no brainstorm",
     "skip ideation"
  3. Content bypass phrase: same phrases inside the Write content (lets
     gap reports / lessons-learned mention prior ideation without deadlock)
  4. Intent detection: user-driven mode via shared intent_detection.py
     (NEW layer added during consolidation)

Exemptions:
  - Meta paths (/.work-requests/, /.lifecycle-reviews/, /.routed-tasks/,
    /.claude/projects/*/memory/, /memory/feedback_*) - structurally exempt
  - Existing config docs (CLAUDE.md, MEMORY.md, README.md, AGENTS.md,
    GEMINI.md) - rewrites are realignment, not feature ideation

Severity: HARD GATE (returns {"decision": "deny", "reason": ...})

Source incident: wr-2026-04-18, wr-2026-04-20-001, wr-2026-04-21-010,
wr-hq-2026-04-29-005.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Add scripts/_lib to path for intent_detection
_SCRIPTS_LIB = os.path.expanduser("~/.claude/scripts/_lib")
if _SCRIPTS_LIB not in sys.path:
    sys.path.insert(0, _SCRIPTS_LIB)
try:
    from intent_detection import is_user_driven  # type: ignore
except Exception:
    is_user_driven = None  # graceful degradation

# Add hooks/ to path for _dispatchers package
_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events
except Exception:
    _feedback_events = None  # graceful degradation


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

# Ideation keywords (Signal A)
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
    re.compile(r"\bname\s+(?:it|options?|candidates?|for\s+(?:the|this|our))\b", re.I),
    re.compile(r"\bnaming\s+(?:exercise|options?|candidates?|round|ideas?|conventions?)\b", re.I),
    re.compile(r"\bwhat\s+(?:should|could)\s+we\s+(?:call|name)\b", re.I),
    re.compile(r"\bsuggest\s+(?:a\s+|some\s+|\d+\s+|(?:a\s+)?few\s+)?name[s]?\b", re.I),
]

# Plan-file path patterns (Signal B)
PLAN_PATH_RE = re.compile(
    r"(?:"
    r"[/\\]plan\.md$"
    r"|[/\\]plans?[/\\][^/\\]+\.md$"
    r"|[/\\]projects[/\\][^/\\]+[/\\]plan[^/\\]*\.md$"
    r")",
    re.I,
)

# Meta paths (structural exemption)
META_PATH_MARKERS = (
    "/.work-requests/",
    "/.lifecycle-reviews/",
    "/.routed-tasks/",
    "/.claude/projects/",
    "/.claude/memory/",
    "/memory/feedback_",
)

# Domain keywords (Signal C part 1)
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

# Ideation headers (Signal C part 2)
IDEATION_HEADER_RE = re.compile(
    r"\b(?:tagline|slogan|name|naming|campaign|headline)s?\s+"
    r"(?:option|candidate|idea|choice|suggestion)s?\b"
    r"|\bhere\s+are\s+(?:\d+|a\s+few|some)\s+"
    r"(?:tagline|slogan|name|naming|campaign|headline)",
    re.I,
)

TRANSCRIPT_USER_LOOKBACK = 3

# Config-doc basenames exempt from Signals A and C when they already exist
CONFIG_DOC_BASENAMES = (
    "claude.md",
    "memory.md",
    "readme.md",
    "agents.md",
    "gemini.md",
)

# System-injected blocks to strip BEFORE keyword matching
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


def _strip_system_blocks(text):
    if not text:
        return ""
    try:
        return SYSTEM_BLOCK_RE.sub("", text)
    except Exception:
        return text


def _load_skill_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return []


def _skill_invoked(name, log):
    target = name.lower()
    return any(
        e == target or e.endswith(":" + target) or e.startswith(target + ":")
        for e in log
    )


def _read_recent_user_messages(transcript_path):
    if not transcript_path:
        return []
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return []
        msgs = []
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
        return msgs[-TRANSCRIPT_USER_LOOKBACK:]
    except Exception:
        return []


def _has_bypass_phrase(messages):
    for txt in messages:
        clean = _strip_system_blocks(txt)
        low = clean.lower()
        if any(phrase in low for phrase in BYPASS_PHRASES):
            return True
    return False


def _has_ideation_keyword(messages):
    for txt in messages:
        clean = _strip_system_blocks(txt)
        for pat in IDEATION_KEYWORDS:
            if pat.search(clean):
                return True
    return False


def _is_new_plan_write(file_path, tool_name):
    if tool_name != "Write" or not file_path:
        return False
    if not PLAN_PATH_RE.search(file_path):
        return False
    try:
        if os.path.isfile(file_path):
            return False
    except OSError:
        return False
    return True


def _is_existing_config_doc(file_path):
    if not file_path:
        return False
    basename = os.path.basename(file_path).lower()
    if basename not in CONFIG_DOC_BASENAMES:
        return False
    try:
        return os.path.isfile(file_path)
    except OSError:
        return False


def _is_meta_path(file_path):
    if not file_path:
        return False
    norm = file_path.replace("\\", "/").lower()
    return any(marker in norm for marker in META_PATH_MARKERS)


def _has_ideation_content_pattern(text):
    if not text or len(text) < 20:
        return False
    if not DOMAIN_KEYWORDS_RE.search(text):
        return False
    if not IDEATION_HEADER_RE.search(text):
        return False
    return True


def _has_bypass_in_content(content):
    if not content:
        return False
    low = content.lower()
    return any(phrase in low for phrase in BYPASS_PHRASES)


def evaluate(payload):
    """Evaluate brainstorming sub-rule.

    Returns:
      None                                  -> sub-rule did not trigger
      {"decision": "deny", "reason": "..."} -> HARD GATE
    """
    tool_name = payload.get("tool_name", "")
    if tool_name != "Write":
        return None  # only Write -- edits are maintenance

    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")

    # Meta path exemption
    if _is_meta_path(file_path):
        return None

    # Detection
    transcript_path = payload.get("transcript_path") or ""
    recent_msgs = _read_recent_user_messages(transcript_path)
    content = str(tool_input.get("content", "") or "")
    config_doc_rewrite = _is_existing_config_doc(file_path)

    signal_a = _has_ideation_keyword(recent_msgs) and not config_doc_rewrite
    signal_b = _is_new_plan_write(file_path, tool_name)
    signal_c = _has_ideation_content_pattern(content) and not config_doc_rewrite

    if not (signal_a or signal_b or signal_c):
        return None

    # Bypass: skill log
    log = _load_skill_log()
    if _skill_invoked(PREFERRED_SKILL, log) or _skill_invoked(FALLBACK_SKILL, log):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="brainstorming",
                decision="pass_through", trigger="skill_log_bypass",
                payload=payload,
            )
        return None

    # Bypass: transcript phrase
    if _has_bypass_phrase(recent_msgs):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="brainstorming",
                decision="pass_through", trigger="transcript_bypass_phrase",
                payload=payload,
            )
        return None

    # Bypass: content phrase
    if _has_bypass_in_content(content):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="brainstorming",
                decision="pass_through", trigger="content_bypass_phrase",
                payload=payload,
            )
        return None

    # Bypass: intent_detection user-driven mode (NEW LAYER)
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=file_path,
                bypass_phrases=BYPASS_PHRASES, lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="brainstorming",
                        decision="pass_through", trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    # Hard gate fires
    trigger_label = []
    if signal_a:
        trigger_label.append("user message with ideation keyword")
    if signal_b:
        trigger_label.append("new plan file: " + os.path.basename(file_path))
    if signal_c:
        trigger_label.append("candidate-pitching pattern in tool content")
    label = " + ".join(trigger_label) if trigger_label else "ideation context"

    reason = (
        f"BLOCKING: Feature ideation or planning context detected ({label}). "
        "The brainstorming skill MUST be invoked before drafting plans or "
        "creating new features. The skill applies divergent-thinking patterns "
        "that catch alternatives the default flow misses. Run "
        "`Skill superpowers:brainstorming` (preferred) or `Skill brainstorming`. "
        'To bypass: include "skip brainstorming" in your message OR in the '
        "tool content itself. Gap reports, lifecycle reviews, and routed "
        "tasks under /.work-requests/ /.lifecycle-reviews/ /.routed-tasks/ "
        "and auto-memory files under /.claude/projects/*/memory/ are "
        "structurally exempt. TodoWrite is no longer inspected. "
        "Source: wr-2026-04-18, wr-2026-04-20-001, wr-2026-04-21-010, "
        "wr-hq-2026-04-29-005. See docs/hook-classification-policy.md."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="brainstorming",
            decision="hard_deny", trigger=label, payload=payload,
        )
    return {"decision": "deny", "reason": reason}
