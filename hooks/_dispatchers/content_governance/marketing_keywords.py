"""marketing_keywords.py - Content-governance dispatcher sub-rule.

Source: ~/.claude/hooks/marketing-content-detector.py (440 LOC). Lift
preserves 1:1 behavior: HARD DENY on marketing/funnel/positioning keywords
in file content when marketing-strategy-pmm has not been invoked AND no
bypass phrase fired.

Detection (preserved):
  - tool_name in {Write, Edit} with non-empty content
  - content matches a marketing keyword regex (word-boundary aware;
    case-sensitive GTM/ICP; case-insensitive for spelled forms)
  - code files (.py/.js/.ts/...): strip string literals BEFORE scan
  - markdown files (.md/.markdown/...): strip fenced code + inline
    backticks BEFORE scan

Structural exemptions (any one bypasses):
  - file_path under /.work-requests/, /.lifecycle-reviews/, /.routed-tasks/
  - content parses as routed-task JSON (task_id + routed_from + routed_to)
  - content parses as work-request JSON (id + request_type + source_workspace)
  - content is a JSON object with doc_type: internal_coordination
  - markdown frontmatter declares doc_type: internal_coordination

Bypasses (any one passes through):
  - skill log shows marketing-strategy-pmm invoked today
  - intent_detection.is_user_driven() returns True (natural-language
    imperatives + literal bypass phrases + session intent flags)
  - legacy: explicit bypass phrase in recent user message (15-message
    lookback window)

Severity: HARD GATE (returns {"decision": "deny", "reason": ...}).

Source incidents:
  - wr-2026-04-18 (HQ filed BUG after 2 advisory nudges were rationalized
    away in one session -- "Documentation without runtime detection is
    insufficient")
  - wr-2026-04-22-001 (structural exemptions for meta paths +
    coordination JSON + doc_type frontmatter escape hatch)
  - wr-hq-2026-04-27-001/003 (natural-language imperative bypass
    vocabulary + lookback window expansion from 3 -> 15)

Design trade-off (preserved): false POSITIVES deadlock the agent (require
user to type bypass phrase); false NEGATIVES are recoverable. When in
doubt, ALLOW. Conservative detection, permissive bypass.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# Add hooks/ dir for _dispatchers package imports
_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

try:
    from _dispatchers import _feedback_events  # type: ignore
    from _dispatchers import _signal_extract  # type: ignore
except Exception:
    _feedback_events = None
    _signal_extract = None

# Add scripts/_lib for intent_detection (graceful if missing)
_SCRIPTS_LIB = os.path.expanduser("~/.claude/scripts/_lib")
if _SCRIPTS_LIB not in sys.path:
    sys.path.insert(0, _SCRIPTS_LIB)
try:
    import intent_detection  # type: ignore
except Exception:
    intent_detection = None  # graceful


REQUIRED_SKILL = "marketing-strategy-pmm"

# Bypass phrases (preserved verbatim from source line 72-101).
BYPASS_PHRASES = (
    "skip pmm",
    "bypass marketing",
    "bypass pmm",
    "no positioning",
    "internal doc only",
    "not marketing",
    "skip marketing-strategy-pmm",
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

# Marketing keyword patterns (preserved verbatim from source line 107-119).
MARKETING_PATTERNS = [
    re.compile(r"\blead\s+magnet\b", re.I),
    re.compile(r"\bfunnel\b", re.I),
    re.compile(r"\bpositioning\b", re.I),
    re.compile(r"\bGTM\b"),  # case-sensitive
    re.compile(r"\bgo[\s-]to[\s-]market\b", re.I),
    re.compile(r"\bICP\b"),  # case-sensitive
    re.compile(r"\bideal\s+customer\s+profile\b", re.I),
    re.compile(r"\bvalue\s+prop(?:osition)?\b", re.I),
    re.compile(r"\bmessaging\s+framework\b", re.I),
    re.compile(r"\bcustomer\s+journey\b", re.I),
    re.compile(r"\bconversion\s+path\b", re.I),
]

CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".rs",
             ".java", ".c", ".cpp", ".h"}
MD_EXTS = {".md", ".markdown", ".mdown", ".mkdn"}

META_PATH_MARKERS = (
    "/.work-requests/",
    "/.lifecycle-reviews/",
    "/.routed-tasks/",
)

ROUTED_TASK_SCHEMA_KEYS = {"task_id", "routed_from", "routed_to"}
WORK_REQUEST_SCHEMA_KEYS = {"id", "request_type", "source_workspace"}

MD_FENCED_CODE_RE = re.compile(r"```[\s\S]*?```")
MD_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DOC_TYPE_RE = re.compile(r"^\s*doc_type\s*:\s*(\S+)", re.MULTILINE)

QUOTED_LITERAL_RE = re.compile(r"""(?:\"[^\"\n]*\"|\'[^\'\n]*\'|`[^`\n]*`)""")

TRANSCRIPT_USER_LOOKBACK = 15

_SCAN_LIMIT = 8000  # cap content length for keyword scan


def _is_meta_path(file_path):
    if not file_path:
        return False
    norm = file_path.replace("\\", "/").lower()
    return any(marker in norm for marker in META_PATH_MARKERS)


def _is_coordination_json(content):
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


def _has_internal_coordination_doctype(content):
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


def _strip_md_code(text):
    text = MD_FENCED_CODE_RE.sub("", text)
    text = MD_INLINE_CODE_RE.sub("", text)
    return text


def _strip_quoted_literals(text):
    return QUOTED_LITERAL_RE.sub("", text)


def _find_marketing_match(content, file_path):
    if not content:
        return None
    snippet = content[:_SCAN_LIMIT]
    ext = os.path.splitext((file_path or "").lower())[1]
    if ext in CODE_EXTS:
        snippet = _strip_quoted_literals(snippet)
    elif ext in MD_EXTS:
        snippet = _strip_md_code(snippet)
    for pat in MARKETING_PATTERNS:
        m = pat.search(snippet)
        if m:
            return m.group(0)
    return None


def _load_skill_log_today():
    """Load today's skill invocations. Returns list of lowercased names.
    Uses shared helper from Build #1; falls back to legacy on missing helper."""
    if _signal_extract is not None:
        try:
            return _signal_extract.load_skill_log_today()
        except Exception:
            pass
    # Fallback: read directly (preserve graceful failure semantics)
    try:
        from datetime import datetime as _dt
        today = _dt.now().strftime("%Y-%m-%d")
        log_path = Path.home() / ".claude" / ".tmp" / f"skill-invocations-{today}.json"
        if not log_path.exists():
            return []
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


def _scan_transcript_for_bypass(transcript_path):
    """Legacy fallback when intent_detection helper is missing."""
    if not transcript_path:
        return False
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return False
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
        for txt in user_msgs[-TRANSCRIPT_USER_LOOKBACK:]:
            low = txt.lower()
            if any(phrase in low for phrase in BYPASS_PHRASES):
                return True
    except Exception:
        return False
    return False


def _deny_reason(file_path, match):
    base = os.path.basename(file_path) if file_path else "(unknown file)"
    return (
        "BLOCKING: Marketing/funnel content detected in " + base + " "
        "(matched: '" + match + "'). The marketing-strategy-pmm skill MUST "
        "be invoked before writing positioning, GTM, ICP, value prop, or "
        "funnel content. The skill encodes April Dunford-style positioning "
        "frameworks. To bypass for genuinely non-marketing content, include "
        "\"skip pmm\" or \"internal doc only\" in your next message and retry. "
        "Source: wr-2026-04-18 (HQ filed BUG after 2 nudges were rationalized "
        "away in one session). See docs/hook-classification-policy.md."
    )


def evaluate(payload):
    """Sub-rule entry point. Returns:
      None                                    -> no contribution
      {"decision": "deny", "reason": "..."}   -> hard gate
    Never raises (graceful degradation)."""
    try:
        if not isinstance(payload, dict):
            return None

        # Extract canonical signals
        if _signal_extract is not None:
            signals = _signal_extract.extract(payload)
            tool_name = signals["tool_name"]
            file_path = signals["file_path"]
            content = signals["content_body"]
            transcript_path = signals["transcript_path"]
        else:
            tool_name = str(payload.get("tool_name", "") or "")
            tool_input = payload.get("tool_input") or {}
            if isinstance(tool_input, str):
                try:
                    tool_input = json.loads(tool_input)
                except (json.JSONDecodeError, TypeError, ValueError):
                    tool_input = {}
            if not isinstance(tool_input, dict):
                tool_input = {}
            file_path = str(tool_input.get("file_path", "") or "")
            if tool_name == "Write":
                content = str(tool_input.get("content", "") or "")
            else:
                content = str(tool_input.get("new_string", "") or "")
            transcript_path = str(payload.get("transcript_path", "") or "")

        # Tool filter
        if tool_name not in ("Write", "Edit"):
            return None

        # No content -> nothing to scan
        if not content:
            return None

        # ---- Structural exemptions ----------------------------------------
        if _is_meta_path(file_path):
            return None
        if _is_coordination_json(content):
            return None
        if _has_internal_coordination_doctype(content):
            return None

        # Marketing keyword scan
        match = _find_marketing_match(content, file_path)
        if not match:
            return None

        # ---- Bypass: skill log -------------------------------------------
        log = _load_skill_log_today()
        if _skill_invoked(REQUIRED_SKILL, log):
            if _feedback_events is not None:
                try:
                    _feedback_events.record(
                        cluster="content_governance",
                        sub_rule="marketing_keywords",
                        decision="pass_through_bypass",
                        trigger="skill_log_match",
                        payload=payload,
                        tags={"matched_keyword": match, "bypass": "skill_log"},
                    )
                except Exception:
                    pass
            return None

        # ---- Bypass: user-driven intent / transcript phrase --------------
        if intent_detection is not None:
            try:
                if intent_detection.is_user_driven(
                    transcript_path,
                    file_path=file_path,
                    bypass_phrases=BYPASS_PHRASES,
                    lookback=TRANSCRIPT_USER_LOOKBACK,
                ):
                    if _feedback_events is not None:
                        try:
                            _feedback_events.record(
                                cluster="content_governance",
                                sub_rule="marketing_keywords",
                                decision="pass_through_bypass",
                                trigger="user_driven_intent",
                                payload=payload,
                                tags={"matched_keyword": match,
                                      "bypass": "intent_detection"},
                            )
                        except Exception:
                            pass
                    return None
            except Exception:
                pass
        if _scan_transcript_for_bypass(transcript_path):
            if _feedback_events is not None:
                try:
                    _feedback_events.record(
                        cluster="content_governance",
                        sub_rule="marketing_keywords",
                        decision="pass_through_bypass",
                        trigger="transcript_bypass_phrase",
                        payload=payload,
                        tags={"matched_keyword": match,
                              "bypass": "transcript_legacy"},
                    )
                except Exception:
                    pass
            return None

        # ---- DENY --------------------------------------------------------
        if _feedback_events is not None:
            try:
                _feedback_events.record(
                    cluster="content_governance",
                    sub_rule="marketing_keywords",
                    decision="hard_deny",
                    trigger="marketing_keyword_no_bypass",
                    payload=payload,
                    tags={"matched_keyword": match, "tool_name": tool_name},
                )
            except Exception:
                pass
        return {"decision": "deny", "reason": _deny_reason(file_path, match)}
    except Exception:
        return None
