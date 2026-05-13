"""strategy_work.py - Methodology dispatcher sub-rule for strategy/pricing/positioning work.

Source: wr-hq-2026-05-11-001, wr-hq-2026-05-11-003, wr-hq-2026-05-12-001,
wr-sentinel-2026-05-12-004 (Cluster A -- 4 stacked methodology-skip recurrences)
+ wr-sentinel-2026-05-13 (using-sharkitect-methodology-skipped-at-session-start).

Spec: docs/superpowers/specs/2026-05-12-methodology-gate-cluster-a-design.md (Layer 3)

Two tiers:

Tier 1 -- ask decision (narrow hard-gate):
  - Tool: Write only (Edit is maintenance, not creation)
  - Path: matches NEW pricing/positioning/strategy spec file patterns
  - File does NOT exist on disk yet
  - No methodology skill invoked in current session
  - Returns {"decision": "ask", "reason": ...} -> permissionDecision: "ask"

Tier 2 -- advisory (broad nudge):
  - Tool: Write or Edit on broader design/proposal/audit/spec file patterns
  - No methodology skill invoked in current session
  - Returns {"advisory": ...}

Bypasses (apply to BOTH tiers):
  1. Bypass phrase 'skip methodology-gate' in tool content OR transcript
  2. Intent detection: user-driven mode
  3. Meta-path exemption (.work-requests/, .lifecycle-reviews/, .routed-tasks/,
     brain-dump/, .claude/projects/*/memory/, .tmp/)
  4. Test file exemption (test_*.py, *_test.py)
  5. Standing exemption: methodology skill (incl. using-sharkitect-methodology)
     invoked in current session via the tool-usage journal
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

_SCRIPTS_LIB = os.path.expanduser("~/.claude/scripts/_lib")
if _SCRIPTS_LIB not in sys.path:
    sys.path.insert(0, _SCRIPTS_LIB)
try:
    from intent_detection import is_user_driven  # type: ignore
except Exception:
    is_user_driven = None

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events  # type: ignore
except Exception:
    _feedback_events = None


METHODOLOGY_SKILLS = (
    "pricing-strategy",
    "marketing-strategy-pmm",
    "smb-cfo",
    "hq-revenue-ops",
    "superpowers:brainstorming",
    "brainstorming",
    "using-sharkitect-methodology",
)

BYPASS_PHRASES = ("skip methodology-gate",)

# Tier 1: Write to NEW file at any of these path patterns triggers ask.
TIER1_PATH_PATTERNS = [
    re.compile(r"[/\\]projects[/\\]clients[/\\][^/\\]+[/\\]marketing-takeover[/\\][^/\\]+\.md$", re.I),
    re.compile(r"[/\\]projects[/\\]clients[/\\][^/\\]+[/\\]proposal[^/\\]*\.md$", re.I),
    re.compile(r"[/\\]projects[/\\]clients[/\\][^/\\]+[/\\]pricing[^/\\]*\.md$", re.I),
    re.compile(r"[/\\]knowledge-base[/\\]revenue[/\\]pricing-structure[^/\\]*\.md$", re.I),
    re.compile(r"[/\\]knowledge-base[/\\]strategy[/\\][^/\\]+\.md$", re.I),
    re.compile(r"[/\\]docs[/\\]superpowers[/\\]specs[/\\][^/\\]*pricing[^/\\]*\.md$", re.I),
    re.compile(r"[/\\]docs[/\\]superpowers[/\\]specs[/\\][^/\\]*positioning[^/\\]*\.md$", re.I),
    re.compile(r"[/\\]deliverables[/\\]proposals[/\\][^/\\]+\.md$", re.I),
]

# Tier 2: broader advisory triggers (Write or Edit)
TIER2_PATH_PATTERNS = [
    re.compile(r"[/\\][^/\\]*proposal[^/\\]*\.md$", re.I),
    re.compile(r"[/\\][^/\\]*audit[^/\\]*\.md$", re.I),
    re.compile(r"[/\\][^/\\]*design[^/\\]*\.md$", re.I),
    re.compile(r"[/\\][^/\\]*spec[^/\\]*\.md$", re.I),
]

# Exemption path patterns (apply to BOTH tiers)
EXEMPT_PATH_PATTERNS = [
    re.compile(r"[/\\]\.work-requests[/\\]", re.I),
    re.compile(r"[/\\]\.lifecycle-reviews[/\\]", re.I),
    re.compile(r"[/\\]\.routed-tasks[/\\]", re.I),
    re.compile(r"[/\\]\.tmp[/\\]", re.I),
    re.compile(r"[/\\]brain-dump[/\\]", re.I),
    re.compile(r"[/\\]\.claude[/\\]projects[/\\][^/\\]+[/\\]memory[/\\]", re.I),
    re.compile(r"[/\\]test_[^/\\]+\.py$", re.I),
    re.compile(r"[/\\][^/\\]+_test\.py$", re.I),
]


def _is_exempt_path(file_path: str) -> bool:
    return any(p.search(file_path) for p in EXEMPT_PATH_PATTERNS)


def _matches_tier1(file_path: str) -> bool:
    return any(p.search(file_path) for p in TIER1_PATH_PATTERNS)


def _matches_tier2(file_path: str) -> bool:
    return any(p.search(file_path) for p in TIER2_PATH_PATTERNS)


def _has_bypass_phrase(payload: dict) -> bool:
    """Check for 'skip methodology-gate' in tool content OR transcript tail."""
    content = payload.get("tool_input", {}).get("content", "") or ""
    if any(phrase in content.lower() for phrase in BYPASS_PHRASES):
        return True
    transcript_path = payload.get("transcript_path")
    if transcript_path and os.path.isfile(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(0, size - 3000))
                tail = f.read()
            if any(phrase in tail.lower() for phrase in BYPASS_PHRASES):
                return True
        except (OSError, UnicodeDecodeError):
            pass
    return False


def _session_has_methodology_skill(payload: dict) -> bool:
    """Check tool-usage journal for any methodology skill invocation in current session."""
    journal_path = Path(tempfile.gettempdir()) / "claude_tool_usage_journal.jsonl"
    if not journal_path.is_file():
        return False
    session_id = payload.get("session_id", "")
    if not session_id:
        return False
    try:
        with open(journal_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if entry.get("session_id") != session_id:
                    continue
                tool_name = entry.get("tool_name", "")
                if tool_name in ("Skill", "skill"):
                    skill_name = entry.get("tool_input", {}).get("skill", "")
                    if any(m in skill_name for m in METHODOLOGY_SKILLS):
                        return True
    except (OSError, UnicodeDecodeError):
        pass
    return False


_ASK_REASON_TEMPLATE = (
    "Methodology gate: about to write NEW pricing/positioning/strategy spec file "
    "`{path}` without invoking pricing-strategy, marketing-strategy-pmm, "
    "smb-cfo, hq-revenue-ops, or superpowers:brainstorming. "
    "Per HQ Strategy Creation Rules and 4+ documented recurrences across HQ + "
    "Sentinel, methodology invocation is required for new pricing/positioning "
    "work. Allow this write, or cancel and invoke a methodology skill first? "
    "(Bypass: include 'skip methodology-gate' in your message OR invoke the "
    "using-sharkitect-methodology skill.)"
)

_ADVISORY_TEMPLATE = (
    "Methodology nudge: writing/editing `{path}` looks like methodology-relevant "
    "work (strategy/pricing/positioning/design/proposal/audit). Consider invoking "
    "pricing-strategy, marketing-strategy-pmm, smb-cfo, hq-revenue-ops, "
    "superpowers:brainstorming, or using-sharkitect-methodology before proceeding. "
    "Bypass: 'skip methodology-gate' in your message."
)


def evaluate(payload: dict):
    """Evaluate Tier 1 + Tier 2 patterns. Return ask, advisory, or None."""
    event = payload.get("hook_event_name", "")
    if event != "PreToolUse":
        return None
    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return None

    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return None

    # Exemptions (apply to both tiers)
    if _is_exempt_path(file_path):
        return None

    # Bypass phrase
    if _has_bypass_phrase(payload):
        return None

    # User-driven intent bypass
    if is_user_driven is not None:
        try:
            if is_user_driven(payload):
                return None
        except Exception:
            pass

    # Methodology skill already invoked in session -> pass
    if _session_has_methodology_skill(payload):
        return None

    # Tier 1: Write to NEW file matching strict patterns -> ask
    if tool_name == "Write" and _matches_tier1(file_path):
        if not Path(file_path).exists():
            return {
                "decision": "ask",
                "reason": _ASK_REASON_TEMPLATE.format(path=file_path),
            }

    # Tier 2: advisory on broader patterns OR Edit on Tier 1 paths
    if _matches_tier1(file_path) or _matches_tier2(file_path):
        return {"advisory": _ADVISORY_TEMPLATE.format(path=file_path)}

    return None
