"""Tests for process-violation-detector.py UserPromptSubmit hook.

[skip brainstorming - design pre-approved in wr-hq-2026-05-01-001 recommended_fix]
[skip writing-plans - implementing single hook with companion test file]

Source: wr-hq-2026-05-01-001 -- methodology skill (systematic-debugging) was
skipped during a clear process-debugging moment. The methodology-nudge.py
hook fires on PreToolUse:Edit|Write|Bash and detects code-iteration patterns.
This new hook fires on UserPromptSubmit and detects PROCESS-violation language
in user messages, nudging superpowers:systematic-debugging BEFORE the AI
generates a diagnosis.

Detection patterns under test:
  - "we are skipping steps" / "we're skipping steps"
  - "this goes against our foundations" / "against the foundations"
  - "we are jumping the gun" / "we're jumping the gun"
  - "how are we already X when we are still Y"
  - "this violates [X principle/protocol/foundation]"
  - Case-insensitive matches

Suppression rules:
  - systematic-debugging or superpowers:systematic-debugging already invoked
    this session -> no nudge
  - Bypass phrase "skip systematic-debugging" in user message -> no nudge
  - Same pattern within same session -> debounced (one nudge per pattern key)
  - Empty / malformed stdin -> exit 0 silent
  - Normal user prompts (no pattern match) -> no nudge
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


HOOK = Path.home() / ".claude" / "hooks" / "process-violation-detector.py"


def _run_hook(stdin_obj, tmp_state_dir, skill_log_entries=None):
    """Run process-violation-detector.py with isolated state + skill log.

    HOME override means hook reads/writes state under tmp_state_dir/.claude/.tmp.
    Returns (stdout, stderr, returncode).
    """
    tmp_dir = tmp_state_dir / ".claude" / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    if skill_log_entries:
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = tmp_dir / f"skill-invocations-{today}.json"
        log_path.write_text(json.dumps({
            "invocations": [{"skill": s} for s in skill_log_entries]
        }), encoding="utf-8")

    env = {
        "HOME": str(tmp_state_dir),
        "USERPROFILE": str(tmp_state_dir),
        "PATH": __import__("os").environ.get("PATH", ""),
    }
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(stdin_obj),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout, result.stderr, result.returncode


def _parse_nudge(stdout):
    if not stdout.strip():
        return ""
    try:
        out = json.loads(stdout)
    except json.JSONDecodeError:
        return ""
    return out.get("hookSpecificOutput", {}).get("additionalContext", "") or ""


# ---------------------------------------------------------------------------
# Trigger-pattern tests
# ---------------------------------------------------------------------------

def test_trigger_skipping_steps(tmp_path):
    stdout, _, rc = _run_hook(
        {"prompt": "we are skipping steps here, what's going on?"},
        tmp_path,
    )
    assert rc == 0
    nudge = _parse_nudge(stdout)
    assert "systematic-debugging" in nudge.lower()


def test_trigger_skipping_steps_contraction(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "we're skipping steps in this analysis"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout).lower()


def test_trigger_jumping_the_gun(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "we are jumping the gun on this"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout).lower()


def test_trigger_jumping_the_gun_contraction(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "we're jumping the gun and trying to prescribe before a full diagnosis"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout).lower()


def test_trigger_against_foundations(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "this goes against our foundations as a company"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout).lower()


def test_trigger_violates_principle(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "this violates our diagnose-before-prescribe principle"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout).lower()


def test_trigger_violates_protocol(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "this violates the verify-before-acting protocol"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout).lower()


def test_trigger_already_X_still_Y(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "how are we already at phase 3 when we are still on phase 1?"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout).lower()


def test_trigger_already_X_still_Y_contraction(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "how are we already prescribing when we're still diagnosing?"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout).lower()


def test_case_insensitive_match(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "WE ARE JUMPING THE GUN HERE"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout).lower()


# ---------------------------------------------------------------------------
# Suppression tests
# ---------------------------------------------------------------------------

def test_no_nudge_when_skill_already_invoked(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "we are jumping the gun here"},
        tmp_path,
        skill_log_entries=["systematic-debugging"],
    )
    assert _parse_nudge(stdout) == ""


def test_no_nudge_when_namespaced_skill_invoked(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "we are jumping the gun here"},
        tmp_path,
        skill_log_entries=["superpowers:systematic-debugging"],
    )
    assert _parse_nudge(stdout) == ""


def test_no_nudge_with_bypass_phrase(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "we are jumping the gun -- skip systematic-debugging"},
        tmp_path,
    )
    assert _parse_nudge(stdout) == ""


def test_no_nudge_for_normal_prompt(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "please review this code and tell me what it does"},
        tmp_path,
    )
    assert _parse_nudge(stdout) == ""


def test_no_nudge_for_empty_prompt(tmp_path):
    stdout, _, _ = _run_hook({"prompt": ""}, tmp_path)
    assert _parse_nudge(stdout) == ""


def test_no_nudge_no_user_prompt_key(tmp_path):
    stdout, _, _ = _run_hook({"session_id": "abc"}, tmp_path)
    assert _parse_nudge(stdout) == ""


# ---------------------------------------------------------------------------
# Debouncing tests
# ---------------------------------------------------------------------------

def test_debounced_same_pattern_same_session(tmp_path):
    """Same pattern key fires only one nudge per session."""
    stdout1, _, _ = _run_hook(
        {"prompt": "we are jumping the gun"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout1).lower()

    stdout2, _, _ = _run_hook(
        {"prompt": "we are still jumping the gun on this"},
        tmp_path,
    )
    # Second invocation, same pattern key -> debounced
    assert _parse_nudge(stdout2) == ""


def test_different_patterns_each_fire_once(tmp_path):
    """Distinct patterns fire independently."""
    stdout1, _, _ = _run_hook(
        {"prompt": "we are jumping the gun"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout1).lower()

    stdout2, _, _ = _run_hook(
        {"prompt": "this violates our diagnostic principle"},
        tmp_path,
    )
    assert "systematic-debugging" in _parse_nudge(stdout2).lower()


# ---------------------------------------------------------------------------
# Robustness tests
# ---------------------------------------------------------------------------

def test_invalid_json_stdin_exits_silently(tmp_path):
    """Hook should exit 0 even on broken stdin -- never block user prompt."""
    env = {
        "HOME": str(tmp_path),
        "USERPROFILE": str(tmp_path),
        "PATH": __import__("os").environ.get("PATH", ""),
    }
    (tmp_path / ".claude" / ".tmp").mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not valid json {{{",
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0


def test_emits_userpromptsubmit_event_name(tmp_path):
    stdout, _, _ = _run_hook(
        {"prompt": "we are jumping the gun here"},
        tmp_path,
    )
    out = json.loads(stdout)
    assert out["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"


def test_nudge_recommends_systematic_debugging_skill(tmp_path):
    """Nudge text must explicitly recommend the skill, not just mention it."""
    stdout, _, _ = _run_hook(
        {"prompt": "we are jumping the gun"},
        tmp_path,
    )
    nudge = _parse_nudge(stdout).lower()
    # Must reference both the protocol/pattern AND the skill name
    assert "systematic-debugging" in nudge
    assert ("invoke" in nudge or "run" in nudge or "use" in nudge)


# ---------------------------------------------------------------------------
# False-positive guards
# ---------------------------------------------------------------------------

def test_no_false_positive_on_jumping_unrelated(tmp_path):
    """'jumping' alone shouldn't fire -- needs the full 'jumping the gun' phrase."""
    stdout, _, _ = _run_hook(
        {"prompt": "the cat is jumping over the wall"},
        tmp_path,
    )
    assert _parse_nudge(stdout) == ""


def test_no_false_positive_on_step_word(tmp_path):
    """'steps' alone shouldn't fire -- needs 'skipping steps' phrase."""
    stdout, _, _ = _run_hook(
        {"prompt": "what are the steps to install this?"},
        tmp_path,
    )
    assert _parse_nudge(stdout) == ""
