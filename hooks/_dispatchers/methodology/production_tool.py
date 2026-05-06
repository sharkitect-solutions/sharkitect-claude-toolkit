"""production_tool.py - Methodology dispatcher sub-rule.

Source: NEW (wr-sentinel-2026-05-04-009 second half).

Trigger: PreToolUse on Write|Edit. When a Python file under /tools/ or /scripts/
contains production-impact patterns (urllib.request import, literal PATCH http
verb, or execute_sql call) AND no matching test file exists, emit advisory
nudging testing-strategy / test-driven-development skill.

Detection signals (any one fires, content checked):
  - urllib.request import (e.g. `import urllib.request`, `from urllib.request import`)
  - HTTP PATCH verb (e.g. `PATCH /` strings, `method='PATCH'`, `request.patch(`)
  - Supabase execute_sql call (matches our infra: `execute_sql(`,
    `mcp__claude_ai_Supabase__execute_sql`, `apply_migration` -- DDL-mutating)

Test-file check:
  Looks for tests/test_<basename>.py relative to the file's project root.
  Project root is heuristic: walks up from file_path looking for tests/
  sibling directory. If not found, also checks ~/.claude/tests/ for
  global script tests.

Bypass:
  - Skill log (testing-strategy / test-driven-development /
    superpowers:test-driven-development / superpowers:testing-strategy)
  - Transcript bypass phrase
  - intent_detection user-driven mode (NEW LAYER)

Debounce: per-file once per session (state file tracks nudged paths).

Severity: ADVISORY (returns {"advisory": "<text>"})

Per Hook Introduction Rule: advisory by default, not hard-deny.

Source incident: Sentinel session 2026-05-04 Goal Monitor build -- shipped
tools/goal-monitor.py with subprocess + Supabase PATCH calls without tests.
Pattern: production-data-modifying tools shipped with no test coverage.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
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
STATE_FILE = TMP_DIR / "production-tool-state.json"

PREFERRED_SKILLS = (
    "superpowers:test-driven-development",
    "superpowers:testing-strategy",
    "test-driven-development",
    "testing-strategy",
)

BYPASS_PHRASES = (
    "skip production-tool",
    "skip testing-strategy",
    "skip tdd",
    "no tests for this",
    "manual test only",
)
TRANSCRIPT_USER_LOOKBACK = 3

# ---- Detection regexes ----
TOOLS_PATH_RE = re.compile(r"[/\\](?:tools?|scripts?)[/\\][^/\\]+\.py$", re.I)

URLLIB_REQUEST_RE = re.compile(
    r"\b(?:from\s+urllib\.request\s+import|import\s+urllib\.request|urllib\.request\.)",
    re.I,
)
HTTP_PATCH_RE = re.compile(
    r"(?:"
    r"['\"]PATCH['\"]"  # method='PATCH' or "PATCH"
    r"|method\s*=\s*['\"]PATCH['\"]"
    r"|requests?\.patch\s*\("
    r"|httpx?\.patch\s*\("
    r"|\.patch\s*\(\s*url"
    r")",
)
EXECUTE_SQL_RE = re.compile(
    r"(?:"
    r"\bexecute_sql\s*\("
    r"|mcp__claude_ai_Supabase__execute_sql"
    r"|\bapply_migration\s*\("
    r"|mcp__claude_ai_Supabase__apply_migration"
    r")",
)


def _has_production_signals(content):
    if not content:
        return []
    signals = []
    if URLLIB_REQUEST_RE.search(content):
        signals.append("urllib.request (raw HTTP -- production network call)")
    if HTTP_PATCH_RE.search(content):
        signals.append("HTTP PATCH (mutation against external service)")
    if EXECUTE_SQL_RE.search(content):
        signals.append("Supabase execute_sql / apply_migration (DDL or row mutation)")
    return signals


def _matching_test_exists(file_path):
    """Heuristic: find tests/test_<basename>.py near the tool file.

    Walks up from the tool file looking for a tests/ sibling directory and
    checks for tests/test_<basename>.py. Also checks ~/.claude/tests/ as
    a global fallback for ~/.claude/scripts tools.
    """
    try:
        p = Path(file_path)
        basename = p.stem  # without .py
        test_filename = f"test_{basename}.py"

        # Walk up looking for tests/ sibling
        cur = p.parent
        max_depth = 6
        for _ in range(max_depth):
            sibling = cur.parent / "tests"
            if sibling.is_dir() and (sibling / test_filename).is_file():
                return True
            # Also check tests/ at the same level (some layouts put tests inside tools dir)
            same_level = cur / "tests"
            if same_level.is_dir() and (same_level / test_filename).is_file():
                return True
            if cur.parent == cur:  # filesystem root
                break
            cur = cur.parent

        # Fallback: ~/.claude/tests/
        global_tests = Path.home() / ".claude" / "tests" / test_filename
        if global_tests.is_file():
            return True

        return False
    except Exception:
        return True  # graceful degradation: don't nudge on errors


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


def _any_preferred_invoked(log):
    return any(_skill_invoked(s, log) for s in PREFERRED_SKILLS)


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


def _load_state():
    today = datetime.now().strftime("%Y-%m-%d")
    if not STATE_FILE.exists():
        return {"date": today, "nudged_files": []}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "nudged_files": []}
        if not isinstance(s.get("nudged_files"), list):
            s["nudged_files"] = []
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "nudged_files": []}


def _save_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def evaluate(payload):
    """Evaluate production_tool sub-rule.

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
    if not file_path or not TOOLS_PATH_RE.search(file_path):
        return None

    if tool_name == "Write":
        content = str(tool_input.get("content", "") or "")
    else:
        content = str(tool_input.get("new_string", "") or "")

    signals = _has_production_signals(content)
    if not signals:
        return None

    # Test-file check: if a matching test exists, no nudge
    if _matching_test_exists(file_path):
        return None

    # Bypass: skill log
    log = _load_skill_log()
    if _any_preferred_invoked(log):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="production_tool",
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
                cluster="methodology", sub_rule="production_tool",
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
                        cluster="methodology", sub_rule="production_tool",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    # Per-file debounce
    state = _load_state()
    if file_path in state.get("nudged_files", []):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="production_tool",
                decision="pass_through", trigger="debounced_already_nudged",
                payload=payload,
            )
        return None
    state["nudged_files"].append(file_path)
    _save_state(state)

    advisory_text = (
        f"PRODUCTION TOOL WITHOUT TESTS: {os.path.basename(file_path)}\n"
        f"  Signals: {'; '.join(signals)}\n"
        f"  Test file expected at: tests/test_{Path(file_path).stem}.py (not found)\n\n"
        "This tool touches production data or external services. Shipping without "
        "tests means future refactors silently break behavior. Invoke "
        "`Skill superpowers:test-driven-development` (preferred) or "
        "`Skill superpowers:testing-strategy` to scaffold the test file before "
        "the tool ships. At minimum: smoke test on dry-run flag, error-path "
        "coverage on the production-mutating call, and a fixture for the "
        "external service.\n\n"
        'To suppress for this file, include "skip production-tool" or '
        '"manual test only" in your next user message.\n\n'
        "Source: wr-sentinel-2026-05-04-009 (Goal Monitor pattern)."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="production_tool",
            decision="advisory",
            trigger=f"signals:{len(signals)}",
            payload=payload,
        )
    return {"advisory": advisory_text}
