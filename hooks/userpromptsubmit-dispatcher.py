#!/usr/bin/env python
"""
userpromptsubmit-dispatcher.py - Build 6 v1

Single UserPromptSubmit hook entry point that loads enabled sub-rules from
config, runs each against the user's prompt + session context, aggregates
advisory nudges into additionalContext.

Spec: 3.- Skill Management Hub/docs/superpowers/specs/2026-05-18-build-6-userpromptsubmit-dispatcher-design.md

Architecture: mirror methodology-dispatcher's sub-rule contract pattern; new
dispatcher shell for UserPromptSubmit event format.
"""
import importlib
import json
import os
import re
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Make _subrules importable
HOOKS_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOKS_DIR))

DEFAULT_CONFIG_PATH = Path.home() / ".claude" / "config" / "userpromptsubmit-dispatcher.json"
DEFAULT_FIRE_LOG_PATH = Path.home() / ".claude" / ".tmp" / "hook-fire-log.jsonl"
DEFAULT_BYPASS_LOG_PATH = Path(tempfile.gettempdir()) / "claude_bypass_log.jsonl"


def load_config() -> dict:
    """Load dispatcher config from env override OR default path."""
    cfg_path = Path(os.environ.get("USERPROMPTSUBMIT_DISPATCHER_CONFIG", str(DEFAULT_CONFIG_PATH)))
    if not cfg_path.exists():
        return {"enabled_subrules": [], "log_dir": None}
    return json.loads(cfg_path.read_text())


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _log_fire(record: dict):
    log_path = Path(os.environ.get("HOOK_FIRE_LOG_PATH", str(DEFAULT_FIRE_LOG_PATH)))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _log_bypass(record: dict):
    log_path = Path(os.environ.get("BYPASS_LOG_PATH", str(DEFAULT_BYPASS_LOG_PATH)))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _detect_bypass_phrases(prompt: str, enabled_subrules: list) -> list:
    """Find all 'skip <slug>' phrases in prompt. Each sub-rule decides what matches."""
    return re.findall(r"\bskip\s+[a-z][a-z0-9\-]*", prompt.lower())


def _import_subrule(subrule_id: str):
    """Import a sub-rule by 'namespace.rule_name' dotted path."""
    full = f"_subrules.{subrule_id}"
    return importlib.import_module(full)


def run_dispatcher(prompt: str, recent_tool_calls: list = None) -> dict:
    """
    Main dispatcher entry. Returns dict with 'additionalContext' key (str).

    Called by both the actual hook entry (read stdin) AND tests (pass args directly).
    """
    recent_tool_calls = recent_tool_calls or []
    cfg = load_config()
    enabled = cfg.get("enabled_subrules", [])
    bypass_phrases = _detect_bypass_phrases(prompt, enabled)

    context = {
        "recent_tool_calls": recent_tool_calls,
        "active_plans": [],  # populated by hook entry from plans-registry; tests pass []
        "session_brief": None,
        "workspace": os.environ.get("CLAUDE_WORKSPACE", "skill-management-hub"),
        "bypass_phrases_in_prompt": bypass_phrases,
    }

    nudges = []
    fired_count = 0
    bypassed_count = 0

    for subrule_id in enabled:
        try:
            mod = _import_subrule(subrule_id)
        except Exception as e:
            _log_fire({
                "ts": _now_iso(),
                "hook": "userpromptsubmit-dispatcher",
                "event": "UserPromptSubmit",
                "subrule": subrule_id,
                "outcome": "import_error",
                "error": str(e),
            })
            continue

        try:
            result = mod.check(prompt, context)
        except Exception as e:
            _log_fire({
                "ts": _now_iso(),
                "hook": "userpromptsubmit-dispatcher",
                "event": "UserPromptSubmit",
                "subrule": subrule_id,
                "outcome": "subrule_exception",
                "error": str(e),
                "traceback": traceback.format_exc(),
            })
            continue  # failure isolation

        if result is None:
            continue

        # Bypass check: prompt contains the rule's exact bypass_keyword
        if result.bypass_keyword in prompt.lower():
            bypass_slug = result.bypass_keyword.replace("skip ", "")
            _log_bypass({
                "ts": _now_iso(),
                "gate": bypass_slug,
                "category": "A",
                "justification": "explicit user direction in prompt",
                "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
            })
            bypassed_count += 1
            continue

        if result.mode == "advisory":
            nudges.append(f"[{result.rule_name}] {result.message} (Bypass: '{result.bypass_keyword}' in your message.)")
            fired_count += 1

    _log_fire({
        "ts": _now_iso(),
        "hook": "userpromptsubmit-dispatcher",
        "event": "UserPromptSubmit",
        "fired_count": fired_count,
        "bypassed_count": bypassed_count,
        "enabled_count": len(enabled),
    })

    if nudges:
        return {"additionalContext": "\n\n".join(nudges)}
    return {"additionalContext": ""}


def main():
    """Hook entry point: read JSON from stdin, emit hook response on stdout."""
    try:
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        # No input or malformed - silently exit (don't break Claude)
        print(json.dumps({}))
        sys.exit(0)

    prompt = hook_input.get("prompt", "") or hook_input.get("user_message", "")
    # Recent tool calls would be passed from hook context if available; for now empty
    result = run_dispatcher(prompt=prompt, recent_tool_calls=[])
    print(json.dumps(result))


if __name__ == "__main__":
    main()
