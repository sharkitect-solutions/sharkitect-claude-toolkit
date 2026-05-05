"""claude_api.py - Methodology dispatcher sub-rule.

Source: claude-api-skill-nudge.py (PreToolUse soft nudge for Anthropic SDK /
prompt-caching code).

Behavior preserved 1:1 from source:
  Content signals (any one fires):
    - Anthropic SDK import (from anthropic import / import anthropic /
      @anthropic-ai/sdk / AnthropicError)
    - Anthropic SDK call (anthropic.Anthropic( / messages.create( /
      beta.messages. / model="claude-*)
    - Prompt caching (cache_control / "type":"ephemeral" / extended-cache /
      cache_creation_input_tokens / cache_read_input_tokens)
    - Anthropic beta features (thinking={ / beta.tools. / computer_use /
      extended_thinking)

Exemptions:
  - Other-provider imports (openai, cohere, mistralai, google-generativeai,
    @google/generative-ai) -- mixed/other-provider code skips
  - Other-provider filenames (foo-openai.py, *-gemini.py, etc.)
  - Documentation paths (.md files, /docs/, /memory/, /plans/, /workflows/,
    /knowledge-base/, /specs/) -- they may discuss API without being API code

Bypasses (any one passes through):
  1. Skill log: claude-api invoked today
  2. Transcript bypass phrase: "skip claude-api-nudge", "skip api-skill-nudge",
     "no claude-api skill", "skip claude-api skill"
  3. Intent detection: user-driven mode via shared intent_detection.py
     (NEW layer added during consolidation)

Debounce: once per session (state file at ~/.claude/.tmp/<state-file>).

Severity: ADVISORY (returns {"advisory": "<text>"})

Source incident: wr-2026-04-25 (HQ) unused-claude-api-skill-for-prompt-caching.
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
STATE_FILE = TMP_DIR / "claude-api-skill-nudge-state.json"
SKILL_NAME = "claude-api"

# ---- Detection regexes (preserved 1:1 from source) ----
ANTHROPIC_IMPORT_RE = re.compile(
    r"\b(?:from\s+anthropic\s+import|import\s+anthropic\b|@anthropic-ai/sdk|AnthropicError\b)",
    re.I,
)
ANTHROPIC_SDK_CALL_RE = re.compile(
    r"\b(?:"
    r"anthropic\.Anthropic\s*\(|"
    r"messages\.create\s*\(|"
    r"beta\.messages\.|"
    r"model\s*=\s*[\"']claude-|"
    r"model\s*:\s*[\"']claude-|"
    r"\"model\"\s*:\s*\"claude-"
    r")",
    re.I,
)
CACHE_CONTROL_RE = re.compile(
    r"\b(?:cache_control|\"type\"\s*:\s*\"ephemeral\"|extended-cache|cache_creation_input_tokens|cache_read_input_tokens)\b",
    re.I,
)
THINKING_TOOLS_RE = re.compile(
    r"\b(?:thinking\s*=\s*\{|beta\.tools\.|computer_use|extended_thinking)\b",
    re.I,
)

# Other-provider imports -- if we see these we skip nudge
OTHER_PROVIDER_IMPORT_RE = re.compile(
    r"\b(?:"
    r"from\s+openai\s+import|import\s+openai\b|"
    r"from\s+cohere\s+import|import\s+cohere\b|"
    r"from\s+mistralai|"
    r"from\s+google\.generativeai|google-generativeai|"
    r"@google/generative-ai"
    r")",
    re.I,
)
OTHER_PROVIDER_FILENAME_RE = re.compile(
    r"(?:openai|gemini|cohere|mistral|llama)(?:[-_.]|$)",
    re.I,
)

# Documentation paths -- nudge would be noise on docs about Claude API
DOC_PATH_RE = re.compile(
    r"(?:[/\\](?:docs?|documentation|memory|MEMORY|plans?|workflows?|notes?|knowledge-base|specs?)[/\\]"
    r"|\.md$)",
    re.I,
)

BYPASS_PHRASES = (
    "skip claude-api-nudge",
    "skip api-skill-nudge",
    "no claude-api skill",
    "skip claude-api skill",
)
TRANSCRIPT_USER_LOOKBACK = 3


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
        low = txt.lower()
        if any(phrase in low for phrase in BYPASS_PHRASES):
            return True
    return False


def _detect_anthropic_signals(content):
    signals = []
    if ANTHROPIC_IMPORT_RE.search(content):
        signals.append("Anthropic SDK import")
    if ANTHROPIC_SDK_CALL_RE.search(content):
        signals.append("Anthropic SDK call (messages.create / Anthropic() / model=claude-*)")
    if CACHE_CONTROL_RE.search(content):
        signals.append("Prompt caching (cache_control / ephemeral / cache token fields)")
    if THINKING_TOOLS_RE.search(content):
        signals.append("Anthropic beta features (thinking, beta.tools, computer_use)")
    return signals


def _is_other_provider(file_path, content):
    if OTHER_PROVIDER_IMPORT_RE.search(content):
        return True
    base = os.path.basename(file_path).lower()
    if OTHER_PROVIDER_FILENAME_RE.search(base):
        return True
    return False


def _load_state():
    today = datetime.now().strftime("%Y-%m-%d")
    if not STATE_FILE.exists():
        return {"date": today, "nudged": False}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "nudged": False}
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "nudged": False}


def _save_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def evaluate(payload):
    """Evaluate claude_api sub-rule.

    Returns:
      None                       -> sub-rule did not trigger
      {"advisory": "<text>"}     -> ADVISORY soft nudge
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

    # Documentation paths exempt
    if DOC_PATH_RE.search(file_path):
        return None

    if tool_name == "Write":
        content = str(tool_input.get("content", "") or "")
    else:
        content = str(tool_input.get("new_string", "") or "")

    # Other-provider exemption
    if _is_other_provider(file_path, content):
        return None

    signals = _detect_anthropic_signals(content)
    if not signals:
        return None

    # Bypass: skill log
    log = _load_skill_log()
    if _skill_invoked(SKILL_NAME, log):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="claude_api",
                decision="pass_through", trigger="skill_log_bypass",
                payload=payload,
            )
        return None

    # Bypass: transcript phrase
    transcript_path = payload.get("transcript_path") or ""
    recent_msgs = _read_recent_user_messages(transcript_path)
    if _has_bypass_phrase(recent_msgs):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="claude_api",
                decision="pass_through", trigger="transcript_bypass_phrase",
                payload=payload,
            )
        return None

    # Bypass: intent_detection user-driven mode (NEW LAYER)
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=file_path,
                bypass_phrases=BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="claude_api",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    # Debounce: nudge once per session
    state = _load_state()
    if state.get("nudged"):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="claude_api",
                decision="pass_through", trigger="debounced_already_nudged",
                payload=payload,
            )
        return None
    state["nudged"] = True
    _save_state(state)

    advisory_text = (
        f"ANTHROPIC SDK / Claude API code detected in {os.path.basename(file_path)}.\n"
        f"  Signals: {'; '.join(signals)}\n\n"
        "BEFORE writing, invoke `Skill claude-api`. The skill encodes:\n"
        "  - Prompt caching: cache_control TTL (5min ephemeral vs 1hr extended), "
        "multi-breakpoint cache layouts (system + tools + few-shot), how cache "
        "hits compound across iterative-runner cascades\n"
        "  - Per-call cost-savings math at current Sonnet/Opus pricing\n"
        "  - Model migration (4.5 -> 4.6 -> 4.7), retired-model replacements\n"
        "  - Tool use, batch API, thinking, files, citations, memory\n"
        "  - When to use messages.create vs beta endpoints; correct extra_headers\n\n"
        "Apps built with this skill SHOULD include prompt caching by default.\n\n"
        'To suppress for the rest of the session, include "skip claude-api-nudge" '
        "in your next user message.\n\n"
        "Source: wr-2026-04-25 (HQ) unused-claude-api-skill-for-prompt-caching."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="claude_api",
            decision="advisory", trigger=f"signals:{len(signals)}",
            payload=payload,
        )
    return {"advisory": advisory_text}
