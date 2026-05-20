#!/usr/bin/env python
"""
userpromptsubmit-dispatcher.py - Build 6 v2.1

Single UserPromptSubmit hook entry point that loads enabled sub-rules from
config, runs each against the user's prompt + session context, aggregates
advisory nudges into additionalContext.

Spec: 3.- Skill Management Hub/docs/superpowers/specs/2026-05-18-build-6-userpromptsubmit-dispatcher-design.md

Architecture: mirror methodology-dispatcher's sub-rule contract pattern; new
dispatcher shell for UserPromptSubmit event format.

History:
    v1   (2026-05-19) - initial ship; verify_state sub-rule + harness contract
    v1.5 (2026-05-19) - architect fortifications: word-boundary bypass regex
                        (defect #1), recent_tool_calls removed (defect #2),
                        SubRuleResult severity+match_evidence (defect #3)
    v2   (2026-05-20) - strategy_creation sub-rule shipped
    v2.1 (2026-05-20) - SHOULD-before-v3 fortifications: active_plans populated
                        from plans-registry, session_brief from .tmp/, per-rule
                        timeout via ThreadPoolExecutor (cross-platform).
                        Unblocks v3 plan_resume sub-rule.
"""
import importlib
import json
import os
import re
import sys
import tempfile
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FutureTimeout
from datetime import datetime, timezone
from pathlib import Path

# Make _subrules importable
HOOKS_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOKS_DIR))

DEFAULT_CONFIG_PATH = Path.home() / ".claude" / "config" / "userpromptsubmit-dispatcher.json"
DEFAULT_FIRE_LOG_PATH = Path.home() / ".claude" / ".tmp" / "hook-fire-log.jsonl"
DEFAULT_BYPASS_LOG_PATH = Path(tempfile.gettempdir()) / "claude_bypass_log.jsonl"
DEFAULT_PLANS_REGISTRY_PATH = Path.home() / ".claude" / "docs" / "plans-registry.md"
DEFAULT_SESSION_BRIEF_DIR = Path.home() / ".claude" / ".tmp"
DEFAULT_SUBRULE_TIMEOUT_SECONDS = 0.5  # 500ms; sub-rules should be regex+file reads


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
    """Import a sub-rule by 'namespace.rule_name' dotted path. Always reload
    so test-time-generated sub-rule files (or per-test rewrites) are picked
    up on each dispatcher run."""
    full = f"_subrules.{subrule_id}"
    if full in sys.modules:
        # Reload so test sub-rules don't get cached across tests
        return importlib.reload(sys.modules[full])
    return importlib.import_module(full)


def _read_active_plans() -> list:
    """Parse plans-registry.md and return a list of active-plan file paths.

    Tolerates missing file, missing 'Active Plans' section, and malformed
    table rows. v2.1 SHOULD-before-v3 fortification: prerequisite for v3
    plan_resume sub-rule (which needs to know which plans are in flight).
    """
    registry_path = Path(os.environ.get("PLANS_REGISTRY_PATH", str(DEFAULT_PLANS_REGISTRY_PATH)))
    if not registry_path.exists():
        return []
    try:
        content = registry_path.read_text(encoding="utf-8")
    except Exception:
        return []

    # Slice to the Active Plans section only (stop at the next H2)
    active_section_match = re.search(
        r"##\s+Active Plans\s*\n(.*?)(?=\n##\s+|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if not active_section_match:
        return []
    section = active_section_match.group(1)

    # Extract anything that looks like a path inside backticks OR a bare
    # path token in the first table column. Markdown table rows look like:
    #   | `~/.claude/plans/foo.md` | active | ws |
    paths = []
    for m in re.finditer(r"`([^`]+\.md)`", section):
        paths.append(m.group(1))
    return paths


def _read_session_brief() -> str | None:
    """Return today's session brief content if it exists, else None.

    Today's brief lives at `.tmp/session-brief-YYYY-MM-DD.md` (per
    end-session protocol). v2.1 fortification: dispatcher exposes the
    brief to sub-rules so plan_resume + future rules have session context.
    """
    brief_dir = Path(os.environ.get("SESSION_BRIEF_DIR", str(DEFAULT_SESSION_BRIEF_DIR)))
    if not brief_dir.exists():
        return None
    today = datetime.now().strftime("%Y-%m-%d")
    brief_path = brief_dir / f"session-brief-{today}.md"
    if not brief_path.exists():
        return None
    try:
        return brief_path.read_text(encoding="utf-8")
    except Exception:
        return None


def _run_subrule_with_timeout(mod, prompt: str, context: dict, timeout_seconds: float):
    """Run sub-rule check() with a wall-clock timeout.

    Uses ThreadPoolExecutor for cross-platform support (signal.SIGALRM is
    POSIX-only; Windows needs threading). A timed-out sub-rule's thread
    keeps running but is detached -- safe because sub-rule checks are I/O
    + regex, not CPU-bound loops.

    Returns either the SubRuleResult / None from check(), or the sentinel
    string "TIMEOUT" so the dispatcher can log + skip without retrying.
    Raises any exception the sub-rule raised (for the existing failure-
    isolation try/except to catch).
    """
    # NOT using `with` because ThreadPoolExecutor.__exit__ blocks on running
    # futures; the whole point of the timeout is to return immediately even
    # when the sub-rule thread is still running. shutdown(wait=False,
    # cancel_futures=True) detaches without waiting (Python 3.9+).
    ex = ThreadPoolExecutor(max_workers=1)
    try:
        future = ex.submit(mod.check, prompt, context)
        try:
            return future.result(timeout=timeout_seconds)
        except _FutureTimeout:
            return "TIMEOUT"
    finally:
        ex.shutdown(wait=False, cancel_futures=True)


def run_dispatcher(prompt: str) -> dict:
    """
    Main dispatcher entry. Returns harness envelope dict with hookSpecificOutput.

    Called by both the actual hook entry (read stdin) AND tests.

    v2.1 (2026-05-20): active_plans populated from plans-registry, session_brief
    populated from .tmp/session-brief-YYYY-MM-DD.md, per-rule timeout enforced
    via ThreadPoolExecutor (cross-platform).

    v1.5 (2026-05-19): recent_tool_calls parameter removed per Option D
    (100% Verification protocol mandates per-action verification; the
    defensive logic that consumed this field has been retired).
    """
    cfg = load_config()
    enabled = cfg.get("enabled_subrules", [])
    timeout_seconds = float(cfg.get("subrule_timeout_seconds", DEFAULT_SUBRULE_TIMEOUT_SECONDS))
    bypass_phrases = _detect_bypass_phrases(prompt, enabled)

    context = {
        "active_plans": _read_active_plans(),
        "session_brief": _read_session_brief(),
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
            result = _run_subrule_with_timeout(mod, prompt, context, timeout_seconds)
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

        if result == "TIMEOUT":
            _log_fire({
                "ts": _now_iso(),
                "hook": "userpromptsubmit-dispatcher",
                "event": "UserPromptSubmit",
                "subrule": subrule_id,
                "outcome": "timeout",
                "timeout_seconds": timeout_seconds,
            })
            continue  # treat as no-fire; other sub-rules still run

        if result is None:
            continue

        # Bypass check: rule's bypass_keyword must appear with word boundaries
        # in the prompt. Uses _detect_bypass_phrases output which already runs
        # the regex `\bskip\s+[a-z][a-z0-9\-]*` -- guarantees the match is not
        # embedded inside a larger word (defect #1 fix, ai-systems-architect
        # verdict 2026-05-19). Substring fallback retired.
        if result.bypass_keyword in bypass_phrases:
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

    # Harness contract: Claude Code UserPromptSubmit expects nudges nested under
    # hookSpecificOutput.{hookEventName,additionalContext}. Bare top-level
    # additionalContext is silently dropped. Mirror methodology-dispatcher /
    # cron-context-enforcer output shape.
    inner = {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "\n\n".join(nudges) if nudges else "",
    }
    return {"hookSpecificOutput": inner}


def main():
    """Hook entry point: read JSON from stdin, emit hook response on stdout."""
    try:
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        # No input or malformed - silently exit (don't break Claude)
        print(json.dumps({}))
        sys.exit(0)

    # Accept both 'prompt' and 'user_prompt' field names (harness uses both
    # across Claude Code versions; methodology-dispatcher + cron-context-enforcer
    # both fall back the same way).
    prompt = hook_input.get("prompt") or hook_input.get("user_prompt") or ""
    result = run_dispatcher(prompt=prompt)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
