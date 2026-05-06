"""creation_gate.py - Methodology dispatcher sub-rule.

Source: Unifies two existing source hooks per docs/superpowers/specs/
2026-05-05-hook-dispatcher-consolidation-spec.md (lines 24 + 31 + 39):
  - hook-development-enforcer.py (HARD GATE on new hook creation)
  - verification-before-build-enforcer.py (Advisory on new infra writes)

Behavior preserved 1:1 from sources, with two internal check tiers:

Tier 1 -- Hook-creation HARD GATE (from hook-development-enforcer):
  - Tool: Write only (Edit is maintenance, not creation)
  - Path: matches **/.claude/hooks/*.py (global ~/.claude/hooks/ or workspace
    .claude/hooks/) AND file does not yet exist
  - Bypass: hook-development / plugin-dev:hook-development skill invoked
    today, transcript bypass phrase, content bypass phrase, or intent_detection
    user-driven mode
  - Exemptions: meta paths (/.work-requests/, /.lifecycle-reviews/,
    /.routed-tasks/, /.claude/projects/*/memory/), test files
  - HARD GATE: returns {"decision": "deny", "reason": ...}

Tier 2 -- Verification-before-build ADVISORY (from verification-before-build-enforcer):
  - Tool: Write on any infrastructure path (~/.claude/hooks/, ~/.claude/scripts/,
    workspace tools/, workspace workflows/)
  - Check: <tempdir>/claude_preflight_invocations.jsonl for preflight-check.py
    invocation within last 90 minutes
  - If no recent preflight: advisory nudge
  - Per-path debounce: nudges once per session per file_path
  - ADVISORY: returns {"advisory": "..."}

The two tiers are evaluated in order. Tier 1 fires first; if it denies, Tier 2
is not reached. If Tier 1 passes (e.g. existing hook edit, or skill bypass),
Tier 2 may still nudge for missing preflight.

NOTE on architecture: the original verification-before-build-enforcer was a
PostToolUse hook. The consolidation spec moves it to PreToolUse, but the spec
also notes the severity is "Advisory->GATE" -- meaning a future upgrade from
advisory to hard-gate is planned. This module preserves ADVISORY semantics
1:1; the GATE upgrade requires explicit user sign-off and is not applied here.

NEW LAYER: intent_detection user-driven bypass applies to BOTH tiers.

Source incidents:
  - wr-2026-04-22-015 (hook-development-enforcer)
  - wr-2026-04-22-006 (verification-before-build-enforcer)
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta
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
    from _dispatchers import _feedback_events
except Exception:
    _feedback_events = None


TMP_DIR = Path.home() / ".claude" / ".tmp"
PREFERRED_HOOK_SKILL = "plugin-dev:hook-development"
FALLBACK_HOOK_SKILL = "hook-development"

# Tier 1 (hook gate) ---------------------------------------------------------

HOOK_BYPASS_PHRASES = (
    "skip hook-development",
    "skip hook development",
    "skip hook-dev",
    "no hook-development",
    "no hook development",
)
HOOK_PATH_RE = re.compile(r"[/\\]\.claude[/\\]hooks[/\\][^/\\]+\.py$", re.I)
HOOK_TEST_PATH_RE = re.compile(r"[/\\]tests?[/\\].*hook.*\.py$", re.I)
HOOK_META_PATH_MARKERS = (
    "/.work-requests/",
    "/.lifecycle-reviews/",
    "/.routed-tasks/",
    "/.claude/projects/",
    "/memory/feedback_",
)

# Tier 2 (preflight) ---------------------------------------------------------

PREFLIGHT_MARKER_PATH = Path(tempfile.gettempdir()) / "claude_preflight_invocations.jsonl"
PREFLIGHT_STATE_FILE = TMP_DIR / "creation-gate-preflight-state.json"
PREFLIGHT_WINDOW = timedelta(minutes=90)
PREFLIGHT_BYPASS_PHRASES = (
    "skip preflight",
    "skip preflight-check",
    "skip verification-before-build",
)
PREFLIGHT_WATCHED_SUBSTRINGS = (
    ("/.claude/hooks/", "hook"),
    ("/.claude/scripts/", "script"),
    ("/tools/", "workspace-tool"),
    ("/workflows/", "workflow-sop"),
)
PREFLIGHT_CODE_SUFFIXES = (".py", ".bat", ".sh", ".ts", ".js")
PREFLIGHT_DOC_SUFFIXES = (".md",)

TRANSCRIPT_USER_LOOKBACK = 5


# ---- Shared helpers --------------------------------------------------------

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
    for entry in log:
        if entry == target:
            return True
        if ":" in entry and entry.split(":", 1)[1] == target:
            return True
        if ":" in target and target.split(":", 1)[1] == entry:
            return True
    return False


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


def _has_phrase(messages, phrases):
    for txt in messages:
        low = txt.lower()
        if any(phrase in low for phrase in phrases):
            return True
    return False


def _has_phrase_in_content(content, phrases):
    if not content:
        return False
    low = content.lower()
    return any(phrase in low for phrase in phrases)


# ---- Tier 1: hook creation gate -------------------------------------------

def _is_meta_path(file_path):
    if not file_path:
        return False
    norm = file_path.replace("\\", "/").lower()
    return any(marker in norm for marker in HOOK_META_PATH_MARKERS)


def _is_new_hook_write(file_path, tool_name):
    if tool_name != "Write":
        return False
    if not file_path:
        return False
    if HOOK_TEST_PATH_RE.search(file_path):
        return False
    if not HOOK_PATH_RE.search(file_path):
        return False
    try:
        if os.path.isfile(file_path):
            return False
    except OSError:
        return False
    return True


def _evaluate_hook_gate(payload, file_path, tool_input, transcript_path):
    """Tier 1: HARD GATE on new hook creation without hook-development skill."""
    if _is_meta_path(file_path):
        return None
    if not _is_new_hook_write(file_path, payload.get("tool_name", "")):
        return None

    # Bypass: skill log
    log = _load_skill_log()
    if _skill_invoked(PREFERRED_HOOK_SKILL, log) or _skill_invoked(FALLBACK_HOOK_SKILL, log):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="creation_gate.hook",
                decision="pass_through", trigger="skill_log_bypass",
                payload=payload,
            )
        return None

    # Bypass: phrase in transcript
    recent_msgs = _read_recent_user_messages(transcript_path)
    if _has_phrase(recent_msgs, HOOK_BYPASS_PHRASES):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="creation_gate.hook",
                decision="pass_through", trigger="transcript_bypass_phrase",
                payload=payload,
            )
        return None

    # Bypass: phrase in current content (gap reports about hooks)
    content = str(tool_input.get("content", "") or "")
    if _has_phrase_in_content(content, HOOK_BYPASS_PHRASES):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="creation_gate.hook",
                decision="pass_through", trigger="content_bypass_phrase",
                payload=payload,
            )
        return None

    # Bypass: intent_detection user-driven mode (NEW LAYER)
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=file_path,
                bypass_phrases=HOOK_BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="creation_gate.hook",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    reason = (
        "BLOCKING: New hook file detected at " + os.path.basename(file_path) + ". "
        "The `hook-development` skill MUST be invoked before writing new hook "
        "code. It loads patterns for PreToolUse/PostToolUse design, matcher "
        "scoping, graceful degradation, and false-positive bias -- all of "
        "which typically require 2-3 iterations to get right without the "
        "skill. Run `Skill plugin-dev:hook-development` (preferred) or "
        "`Skill hook-development`. To bypass: include \"skip hook-development\" "
        "in your message OR the hook file's docstring. Existing hooks can be "
        "edited freely (this gate only fires on NEW files). Meta paths under "
        "/.work-requests/ /.lifecycle-reviews/ /.routed-tasks/ "
        "/.claude/projects/*/memory/ are structurally exempt. "
        "Source: wr-2026-04-22-015."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="creation_gate.hook",
            decision="hard_deny",
            trigger=f"new_hook:{os.path.basename(file_path)}",
            payload=payload,
        )
    return {"decision": "deny", "reason": reason}


# ---- Tier 2: verification-before-build advisory ---------------------------

def _classify_preflight_path(file_path):
    """Return asset_label if file_path matches a watched infra pattern."""
    if not file_path:
        return None
    norm = file_path.replace("\\", "/").lower()
    for substr, label in PREFLIGHT_WATCHED_SUBSTRINGS:
        if substr not in norm:
            continue
        if norm.endswith(PREFLIGHT_CODE_SUFFIXES):
            return label
        if norm.endswith(PREFLIGHT_DOC_SUFFIXES) and substr == "/workflows/":
            return label
    return None


def _recent_preflight_ran():
    """True if preflight-check.py invocation within PREFLIGHT_WINDOW."""
    if not PREFLIGHT_MARKER_PATH.exists():
        return False
    cutoff = datetime.now() - PREFLIGHT_WINDOW
    try:
        with PREFLIGHT_MARKER_PATH.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = rec.get("timestamp", "")
                try:
                    t = datetime.fromisoformat(ts)
                except (ValueError, TypeError):
                    continue
                if t >= cutoff:
                    return True
    except OSError:
        return False
    return False


def _load_preflight_state():
    today = datetime.now().strftime("%Y-%m-%d")
    if not PREFLIGHT_STATE_FILE.exists():
        return {"date": today, "paths_nudged": []}
    try:
        s = json.loads(PREFLIGHT_STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "paths_nudged": []}
        if not isinstance(s.get("paths_nudged"), list):
            s["paths_nudged"] = []
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "paths_nudged": []}


def _save_preflight_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        PREFLIGHT_STATE_FILE.write_text(
            json.dumps(state, indent=2), encoding="utf-8"
        )
    except OSError:
        pass


def _evaluate_preflight_advisory(payload, file_path, tool_input, transcript_path):
    """Tier 2: ADVISORY on new infra writes without recent preflight-check."""
    if payload.get("tool_name", "") != "Write":
        return None

    asset_label = _classify_preflight_path(file_path)
    if not asset_label:
        return None

    if _recent_preflight_ran():
        return None

    # Bypass: transcript phrase
    recent_msgs = _read_recent_user_messages(transcript_path)
    if _has_phrase(recent_msgs, PREFLIGHT_BYPASS_PHRASES):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="creation_gate.preflight",
                decision="pass_through", trigger="transcript_bypass_phrase",
                payload=payload,
            )
        return None

    # Bypass: intent_detection user-driven mode (NEW LAYER)
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=file_path,
                bypass_phrases=PREFLIGHT_BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="creation_gate.preflight",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    # Per-path debounce
    state = _load_preflight_state()
    key = file_path.replace("\\", "/").lower()
    if key in state.get("paths_nudged", []):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="creation_gate.preflight",
                decision="pass_through", trigger="debounced_already_nudged",
                payload=payload,
            )
        return None
    state["paths_nudged"].append(key)
    _save_preflight_state(state)

    advisory_text = (
        f"VERIFICATION-BEFORE-BUILD: New {asset_label} at {os.path.basename(file_path)} "
        "without a preflight-check.py invocation in the last 90 minutes.\n\n"
        "Per Verification-Before-Building Protocol (universal-protocols.md), "
        "run the preflight BEFORE creating new infrastructure to catch "
        "existing assets you might extend instead:\n"
        '  python <Skill Hub>/tools/preflight-check.py "<what you built>"\n\n'
        "If you already checked and decided to build new, note the reasoning "
        "in the artifact or the plan. To suppress for the rest of the session "
        "for this path, include \"skip preflight\" in your next user message.\n\n"
        "Source: wr-2026-04-22-006."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="creation_gate.preflight",
            decision="advisory", trigger=f"new_{asset_label}:{os.path.basename(file_path)}",
            payload=payload,
        )
    return {"advisory": advisory_text}


# ---- Public entry point ---------------------------------------------------

def evaluate(payload):
    """Evaluate creation_gate sub-rule.

    Returns:
      None                                         -> sub-rule did not trigger
      {"decision": "deny", "reason": "..."}        -> Tier 1 HARD GATE
      {"advisory": "<text>"}                       -> Tier 2 ADVISORY
    """
    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return None

    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")
    if not file_path:
        return None

    transcript_path = payload.get("transcript_path") or ""

    # Tier 1: hook-creation HARD GATE
    hook_result = _evaluate_hook_gate(payload, file_path, tool_input, transcript_path)
    if hook_result is not None:
        return hook_result

    # Tier 2: verification-before-build ADVISORY
    return _evaluate_preflight_advisory(payload, file_path, tool_input, transcript_path)
