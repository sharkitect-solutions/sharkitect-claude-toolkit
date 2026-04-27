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

# Make _lib helper importable (pure stdlib, no install needed)
_LIB_DIR = os.path.expanduser("~/.claude/scripts/_lib")
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)
try:
    import intent_detection  # type: ignore
except Exception:
    intent_detection = None  # graceful: legacy code path will run if helper missing


TMP_DIR = Path.home() / ".claude" / ".tmp"
REQUIRED_SKILL = "marketing-strategy-pmm"

# Bypass phrases scanned in the most-recent user message (case-insensitive).
BYPASS_PHRASES = (
    # Original literal-keyword bypasses
    "skip pmm",
    "bypass marketing",
    "bypass pmm",
    "no positioning",
    "internal doc only",
    "not marketing",
    "skip marketing-strategy-pmm",
    # Natural-language imperative bypasses (added 2026-04-27, wr-hq-2026-04-27-001
    # + wr-hq-2026-04-27-003). Mirror of hq-content-skill-stack-enforcer expanded
    # vocab. User explicitly stated: "If we are working and I tell you to do it,
    # that should bypass this hook anyway."
    "go ahead and edit",
    "go ahead and update",
    "go ahead and modify",
    "go ahead and change",
    "go ahead and broaden",
    "go ahead and proceed",
    "go ahead and execute",
    "execute this",
    "do it",
    "proceed with the edit",
    "make the edit",
    "make the change",
    "yes do that",
    "yes proceed",
    "i am driving this",
    "i'm driving this",
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

# Markdown-like extensions where code fences and inline backticks are
# stripped before the keyword scan. Referential mentions inside
# ```...``` or `...` are treated as non-triggering. Source: wr-2026-04-22-001.
MD_EXTS = {".md", ".markdown", ".mdown", ".mkdn"}

# Structural exemption: file paths under these meta-directories hold
# cross-workspace coordination docs that legitimately reference the
# vocabulary the hook detects. Source: wr-2026-04-22-001.
META_PATH_MARKERS = (
    "/.work-requests/",
    "/.lifecycle-reviews/",
    "/.routed-tasks/",
)

# Coordination-JSON schema detection. If a Write payload parses as JSON
# with these field sets at the top level, it is a cross-workspace
# coordination record, not authored prose. Source: wr-2026-04-22-001.
ROUTED_TASK_SCHEMA_KEYS = {"task_id", "routed_from", "routed_to"}
WORK_REQUEST_SCHEMA_KEYS = {"id", "request_type", "source_workspace"}

# Fenced code blocks and inline backticks, for referential stripping
# in markdown content before the keyword scan.
MD_FENCED_CODE_RE = re.compile(r"```[\s\S]*?```")
MD_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

# YAML frontmatter detection for the doc_type escape hatch.
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DOC_TYPE_RE = re.compile(r"^\s*doc_type\s*:\s*(\S+)", re.MULTILINE)

# Quote-stripping regex for code files (very rough, just to suppress obvious
# false positives like a string literal containing "funnel"). We strip:
#   "..." and '...' and `...` (one-line literals only)
QUOTED_LITERAL_RE = re.compile(r"""(?:\"[^\"\n]*\"|\'[^\'\n]*\'|`[^`\n]*`)""")

# Look-back window: number of recent transcript user messages to scan
# for bypass phrases. Raised from 3 to 15 (2026-04-27, wr-hq-2026-04-27-001
# parity fix -- the lookback window expansion was applied to
# hq-content-skill-stack-enforcer.py but missed here, so this hook still
# expired the bypass after 3 successful tool calls. Source: wr-hq-003
# refactor scope, deferred reason quotes "TRANSCRIPT_USER_LOOKBACK 3 -> 15
# AND tool-result filter applied to BOTH hooks" -- this completes that fix).
TRANSCRIPT_USER_LOOKBACK = 15


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


def is_meta_path(file_path):
    """True if file_path lives under a cross-workspace coordination directory.
    Paths under /.work-requests/, /.lifecycle-reviews/, or /.routed-tasks/
    are structurally exempt. Source: wr-2026-04-22-001.
    """
    if not file_path:
        return False
    norm = file_path.replace("\\", "/").lower()
    return any(marker in norm for marker in META_PATH_MARKERS)


def is_coordination_json(content):
    """True if content parses as a JSON object that is a cross-workspace
    coordination record: routed task, work request, or explicit
    doc_type: internal_coordination marker. Source: wr-2026-04-22-001.
    """
    if not content:
        return False
    try:
        stripped = content.strip()
        if not stripped.startswith("{"):
            return False
        data = json.loads(stripped)
    except (json.JSONDecodeError, ValueError, OSError):
        return False
    if not isinstance(data, dict):
        return False
    keys = set(data.keys())
    if ROUTED_TASK_SCHEMA_KEYS.issubset(keys):
        return True
    if WORK_REQUEST_SCHEMA_KEYS.issubset(keys):
        return True
    dt = data.get("doc_type")
    if isinstance(dt, str) and dt.strip().strip("\"'").lower().replace("-", "_") == "internal_coordination":
        return True
    return False


def has_internal_coordination_doctype(content):
    """True if markdown YAML frontmatter declares doc_type: internal_coordination.
    Opt-in escape hatch for coordination docs that live outside meta paths.
    Source: wr-2026-04-22-001.
    """
    if not content:
        return False
    m = FRONTMATTER_RE.match(content)
    if not m:
        return False
    dm = DOC_TYPE_RE.search(m.group(1))
    if not dm:
        return False
    value = dm.group(1).strip().strip("\"'").lower().replace("-", "_")
    return value == "internal_coordination"


def strip_md_code(text):
    """Strip fenced code blocks and inline-backtick runs from markdown.
    Referential mentions of detector vocabulary inside code formatting are
    treated as non-triggering. Source: wr-2026-04-22-001.
    """
    text = MD_FENCED_CODE_RE.sub("", text)
    text = MD_INLINE_CODE_RE.sub("", text)
    return text


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
    elif ext in MD_EXTS:
        snippet = strip_md_code(snippet)
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

    # ---- Structural exemptions (wr-2026-04-22-001) ----------------------
    # 1. File paths under cross-workspace coordination directories.
    if is_meta_path(file_path):
        return 0

    # 2. Content that is a coordination-record JSON object.
    if is_coordination_json(content):
        return 0

    # 3. Markdown with a doc_type: internal_coordination declaration.
    if has_internal_coordination_doctype(content):
        return 0

    match = find_marketing_match(content, file_path)
    if not match:
        return 0  # no trigger

    # ---- Bypass checks ---------------------------------------------------
    # Bypass 1: skill already invoked today
    log = load_skill_log()
    if skill_invoked(REQUIRED_SKILL, log):
        return 0

    # Bypass 2: user-driven mode detected via shared helper.
    # Two-layer detection (2026-04-27 refactor, wr-hq-003):
    # - Primary: ~/.claude/scripts/_lib/intent_detection.py recognizes
    #   natural-language imperatives ("update X", "go ahead and Y", "do it"),
    #   session intent flags ("i'm driving this"), AND the literal bypass
    #   phrases below.
    # - Fallback: legacy scan_transcript_for_bypass kept for resilience if
    #   the helper is missing/broken.
    transcript_path = data.get("transcript_path") or ""
    if intent_detection is not None:
        try:
            if intent_detection.is_user_driven(
                transcript_path,
                file_path=file_path,
                bypass_phrases=BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                return 0
        except Exception:
            pass  # fall through to legacy scan
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
