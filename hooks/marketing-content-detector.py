"""
marketing-content-detector.py - PreToolUse BLOCKING hook for marketing/funnel content

Hardens the marketing-content nudge from methodology-nudge.py into a BLOCKING
gate. Detects marketing/positioning/funnel keywords being written to disk and
DENIES the Write/Edit until the marketing-strategy-pmm skill has been invoked
this session OR the user provides an explicit bypass phrase.

Source: wr-2026-04-18 (workforce-hq filed 3 BUG/PROCESS work requests after
agent rationalized past 2 explicit nudges in the same session). Memory rule:
"Documentation without runtime detection is insufficient -- if a rule keeps
getting violated, add detection, don't reinforce the rule."

Coexists with methodology-nudge.py marketing detection (advisory). Both can
fire on the same call; this BLOCKING one wins because it returns
permissionDecision: deny.

DETECTION
  - tool_name in ("Write", "Edit") with meaningful content
  - file content (Write.content OR Edit.new_string) matches keyword regex
    (lead magnet / funnel / positioning / GTM / ICP / value prop /
    messaging framework / customer journey / conversion path)
  - Keywords are word-boundary aware to suppress false positives in code
  - Quoted-content guard: keyword inside a string literal of a code file
    (.py/.js/.ts/.go/.rb) is treated as a non-trigger (variable name, comment)

BYPASS (any of these allows the operation)
  1. marketing-strategy-pmm has been invoked at least once today
     (read from ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json)
  2. Recent user message in transcript (read from transcript_path on stdin
     input) contains one of: "skip pmm", "bypass marketing", "no positioning",
     "internal doc only", "not marketing"
  3. Hook is removed from settings.json

GRACEFUL DEGRADATION
  - If skill-invocation log is missing/unreadable: ALLOW (don't deadlock).
  - If transcript_path is missing/unreadable: only the skill-log bypass works.
  - Any unhandled exception: exit 0 (allow).

DESIGN TRADE-OFF (intentional false-negative bias)
  False positives DEADLOCK the agent (require user to type bypass phrase).
  False negatives are recoverable (the agent just writes; the user notices).
  When in doubt, this hook ALLOWS the operation. Conservative detection,
  permissive bypass.

Pure stdlib. ASCII-only output. Input/output: JSON via stdin/stdout.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"
REQUIRED_SKILL = "marketing-strategy-pmm"

# Bypass phrases scanned in the most-recent user message (case-insensitive).
BYPASS_PHRASES = (
    "skip pmm",
    "bypass marketing",
    "bypass pmm",
    "no positioning",
    "internal doc only",
    "not marketing",
    "skip marketing-strategy-pmm",
)

# Marketing keyword patterns -- word-boundary aware. Each entry is a regex.
# Conservative: requires multi-word terms or strong-signal acronyms in caps
# context (ICP/GTM are noisy single tokens, so we require word boundaries
# AND prefer the spelled-out form to suppress code-variable false positives).
MARKETING_PATTERNS = [
    re.compile(r"\blead\s+magnet\b", re.I),
    re.compile(r"\bfunnel\b", re.I),
    re.compile(r"\bpositioning\b", re.I),
    re.compile(r"\bGTM\b"),  # case-sensitive: GTM not gtm (avoids "the gtm script")
    re.compile(r"\bgo[\s-]to[\s-]market\b", re.I),
    re.compile(r"\bICP\b"),  # case-sensitive
    re.compile(r"\bideal\s+customer\s+profile\b", re.I),
    re.compile(r"\bvalue\s+prop(?:osition)?\b", re.I),
    re.compile(r"\bmessaging\s+framework\b", re.I),
    re.compile(r"\bcustomer\s+journey\b", re.I),
    re.compile(r"\bconversion\s+path\b", re.I),
]

# Code-file extensions where keyword-in-string-literal should be ignored.
CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".rs", ".java", ".c", ".cpp", ".h"}

# Quote-stripping regex for code files (very rough, just to suppress obvious
# false positives like a string literal containing "funnel"). We strip:
#   "..." and '...' and `...` (one-line literals only)
QUOTED_LITERAL_RE = re.compile(r"""(?:\"[^\"\n]*\"|\'[^\'\n]*\'|`[^`\n]*`)""")

# Look-back window: number of recent transcript user messages to scan
# for bypass phrases.
TRANSCRIPT_USER_LOOKBACK = 3


def load_skill_log():
    """Return list of skill names invoked today (lowercased).

    Graceful: missing/unreadable file -> empty list (allows operation
    in absence of evidence -- no deadlock).
    """
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
    """Match plain or namespaced skill names (plugin:name or name:variant)."""
    target = name.lower()
    return any(
        e == target or e.endswith(":" + target) or e.startswith(target + ":")
        for e in log
    )


def scan_transcript_for_bypass(transcript_path):
    """Read recent user messages from JSONL transcript; return True if any
    contain a bypass phrase. Graceful: any failure returns False.
    """
    if not transcript_path:
        return False
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return False
        # Read the file and collect the last N user messages
        user_msgs = []
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
                        user_msgs.append(content)
                    elif isinstance(content, list):
                        for blk in content:
                            if isinstance(blk, dict) and blk.get("type") == "text":
                                user_msgs.append(blk.get("text", ""))
        except (OSError, UnicodeDecodeError):
            return False

        # Check the last N messages
        for txt in user_msgs[-TRANSCRIPT_USER_LOOKBACK:]:
            low = txt.lower()
            if any(phrase in low for phrase in BYPASS_PHRASES):
                return True
    except Exception:
        return False
    return False


def strip_quoted_literals(text):
    """For code files: remove single/double/backtick quoted strings on a line.
    This eliminates the most common false-positive pattern: keyword embedded
    in a code variable's string literal. Imperfect (won't catch multiline
    strings) but cheap and effective for the noisy false-positive case.
    """
    return QUOTED_LITERAL_RE.sub("", text)


def find_marketing_match(content, file_path):
    """Scan content for any MARKETING_PATTERNS match. Returns the first
    match string or None. Applies code-file quote stripping when applicable.
    """
    if not content:
        return None
    snippet = content[:8000]  # cap scan length to keep hook fast
    ext = os.path.splitext((file_path or "").lower())[1]
    if ext in CODE_EXTS:
        snippet = strip_quoted_literals(snippet)
    for pat in MARKETING_PATTERNS:
        m = pat.search(snippet)
        if m:
            return m.group(0)
    return None


def deny(reason):
    """Emit a PreToolUse deny decision. Modern Claude Code pattern --
    permissionDecision: deny in hookSpecificOutput. Verified against
    content-enforcement-gate.py and n8n-httpRequest-guard.py which use
    the same pattern in the codebase.
    """
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
        return 0  # only Write/Edit

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")
    if tool_name == "Write":
        content = str(tool_input.get("content", "") or "")
    else:
        content = str(tool_input.get("new_string", "") or "")

    if not content:
        return 0  # nothing to scan

    match = find_marketing_match(content, file_path)
    if not match:
        return 0  # no trigger

    # ---- Bypass checks ---------------------------------------------------
    # Bypass 1: skill already invoked today
    log = load_skill_log()
    if skill_invoked(REQUIRED_SKILL, log):
        return 0

    # Bypass 2: user provided an override phrase recently
    transcript_path = data.get("transcript_path") or ""
    if scan_transcript_for_bypass(transcript_path):
        return 0

    # ---- Block ----------------------------------------------------------
    base = os.path.basename(file_path) if file_path else "(unknown file)"
    deny(
        "BLOCKING: Marketing/funnel content detected in " + base + " "
        "(matched: '" + match + "'). The marketing-strategy-pmm skill MUST "
        "be invoked before writing positioning, GTM, ICP, value prop, or "
        "funnel content. The skill encodes April Dunford-style positioning "
        "frameworks. To bypass for genuinely non-marketing content, include "
        "\"skip pmm\" or \"internal doc only\" in your next message and retry. "
        "Source: wr-2026-04-18 (HQ filed BUG after 2 nudges were rationalized "
        "away in one session). See docs/hook-classification-policy.md."
    )
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never deadlock the agent on a hook bug.
        pass
    sys.exit(0)
