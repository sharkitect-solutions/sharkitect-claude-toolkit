"""
claude-api-skill-nudge.py - PreToolUse soft nudge for Anthropic SDK / prompt-caching code

Fires before Write/Edit on files containing Anthropic SDK imports, Claude
API calls, or prompt-caching constructs (cache_control, system messages,
messages.create) when the `claude-api` skill has not been invoked this
session. Adds context (not block) -- mirrors the hq-content-enforcer
pattern (soft nudge to engage domain expertise before producing output).

Source: wr-2026-04-25 (HQ) unused-claude-api-skill-for-prompt-caching.
The Anthropic Sonnet/Opus pricing math + multi-breakpoint cache structures
+ TTL choices + cascade compounding are all in the claude-api skill. Code
that touches those areas without engaging the skill produces guess-quality
output (wrong TTL choice, missed cache breakpoints, inaccurate cost math).

DETECTION SIGNALS (any of these in file_path or content)
  Path signals:
    - filename or path contains 'anthropic', 'claude', 'prompt' (file or dir)
    - excluding files that import openai/cohere/etc (other-provider code)
  Content signals:
    - imports: 'from anthropic import', 'import anthropic',
      '@anthropic-ai/sdk', 'AnthropicError'
    - SDK calls: 'anthropic.Anthropic(', 'messages.create(', 'beta.messages.',
      'model="claude-', "model='claude-"
    - caching: 'cache_control', '"type": "ephemeral"', 'extended-cache'
    - thinking / agents: 'thinking={', 'beta.tools.', 'computer_use'

EXCLUSIONS (skip nudge)
  - File imports another provider SDK (openai, cohere, mistral, gemini SDK,
    google-generativeai) -- provider-neutral code or other-provider
  - Filename suggests other provider: '*-openai.py', '*-gemini.py'
  - Path under documentation paths (.md plans, internal notes)

BYPASS
  1. claude-api skill invoked today (skill log)
  2. Recent user message contains: "skip claude-api-nudge",
     "skip api-skill-nudge", "no claude-api skill"
  3. Hook removed from settings.json

NON-BLOCKING -- emits additionalContext, never denies. Auto Mode friendly.
Pure stdlib. ASCII-only output. Input/output via JSON on stdin/stdout.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"
STATE_FILE = TMP_DIR / "claude-api-skill-nudge-state.json"

SKILL_NAME = "claude-api"

# ---- Detection regexes ----
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
    r"(?:thinking\s*=\s*\{|beta\.tools\.|computer_use\b|extended_thinking\b)",
    re.I,
)
PATH_HINT_RE = re.compile(r"(?:[/\\_-]|^)(?:anthropic|claude|prompt[s]?)(?:[/\\_.-]|$)", re.I)

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

# ---- Bypass ----
BYPASS_PHRASES = (
    "skip claude-api-nudge",
    "skip api-skill-nudge",
    "no claude-api skill",
    "skip claude-api skill",
)
TRANSCRIPT_USER_LOOKBACK = 3


def emit(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    }))


def load_skill_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError):
        return []


def skill_invoked(skill_name, log):
    target = skill_name.lower()
    for entry in log:
        if entry == target or entry.endswith(":" + target) or entry.startswith(target + ":"):
            return True
    return False


def load_state():
    if not STATE_FILE.exists():
        return {"date": datetime.now().strftime("%Y-%m-%d"), "nudged": False}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != datetime.now().strftime("%Y-%m-%d"):
            return {"date": datetime.now().strftime("%Y-%m-%d"), "nudged": False}
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": datetime.now().strftime("%Y-%m-%d"), "nudged": False}


def save_state(state):
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def read_recent_user_messages(transcript_path):
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    try:
        with open(transcript_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return []
    msgs = []
    for raw in reversed(lines):
        if len(msgs) >= TRANSCRIPT_USER_LOOKBACK:
            break
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if rec.get("type") == "user":
            content = rec.get("message", {}).get("content", "")
            if isinstance(content, list):
                content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
            msgs.append(str(content).lower())
    return msgs


def has_bypass_phrase(msgs):
    for m in msgs:
        for phrase in BYPASS_PHRASES:
            if phrase in m:
                return True
    return False


def detect_anthropic_signals(file_path, content):
    """Return list of detected signal types, or empty if none."""
    signals = []

    # Note: PATH_HINT_RE is left as a future signal (filename containing
    # 'anthropic' / 'claude' / 'prompt'). Currently we only fire on content
    # signals to keep false-positive rate low.
    _ = file_path  # reserved for future path-based signal expansion

    # Content checks
    if ANTHROPIC_IMPORT_RE.search(content):
        signals.append("Anthropic SDK import")
    if ANTHROPIC_SDK_CALL_RE.search(content):
        signals.append("Anthropic SDK call (messages.create / Anthropic() / model=claude-*)")
    if CACHE_CONTROL_RE.search(content):
        signals.append("Prompt caching (cache_control / ephemeral / cache token fields)")
    if THINKING_TOOLS_RE.search(content):
        signals.append("Anthropic beta features (thinking, beta.tools, computer_use)")

    # Path-only hit (no content signals) -- weak by itself; require content to fire
    return signals


def is_other_provider(file_path, content):
    if OTHER_PROVIDER_IMPORT_RE.search(content):
        return True
    base = os.path.basename(file_path).lower()
    if OTHER_PROVIDER_FILENAME_RE.search(base):
        return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return 0

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")
    if not file_path:
        return 0

    # Skip documentation files -- they may discuss claude-api without being claude-api code
    if DOC_PATH_RE.search(file_path):
        return 0

    if tool_name == "Write":
        content = str(tool_input.get("content", "") or "")
    else:
        content = str(tool_input.get("new_string", "") or "")

    # Skip if the file is for another provider
    if is_other_provider(file_path, content):
        return 0

    signals = detect_anthropic_signals(file_path, content)
    if not signals:
        return 0

    # Bypass: skill already invoked this session
    log = load_skill_log()
    if skill_invoked(SKILL_NAME, log):
        return 0

    # Bypass: skip phrase in recent user message
    transcript_path = data.get("transcript_path") or ""
    recent_msgs = read_recent_user_messages(transcript_path)
    if has_bypass_phrase(recent_msgs):
        return 0

    # Debounce: nudge once per session
    state = load_state()
    if state.get("nudged"):
        return 0
    state["nudged"] = True
    save_state(state)

    msg = (
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
    emit(msg)
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
