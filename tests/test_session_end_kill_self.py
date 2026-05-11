"""Tests for session-end-cleanup.py kill-self extension.

Plan: 3.- Skill Management Hub/docs/superpowers/plans/2026-05-11-post-hard-stop-system-reassessment.md
     (Task 1.6 stopgap — claude.exe leaks on session-end empirically confirmed S38->S39).

Source: SessionEnd reason taxonomy from https://code.claude.com/docs/en/hooks
  - clear: ANTIGRAVITY-SPECIFIC — process-replacement (KILL).
           See module docstring of session-end-cleanup.py. On bare CLI this
           would be wrong; on antigravity (the env Sharkitect runs in)
           "clear conversation" spawns a new claude.exe, the old one leaks.
  - resume: --resume / --continue (session continues — DO NOT kill)
  - bypass_permissions_disabled: mode change (defensive skip)
  - logout: user logged out (KILL)
  - prompt_input_exit: Ctrl+C / exit (KILL)
  - other: anything else incl. normal wrap / tab close / window close (KILL)
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock


HOOK_PATH = Path(os.path.expanduser("~/.claude/hooks/session-end-cleanup.py"))


def _load_hook():
    spec = importlib.util.spec_from_file_location("session_end_cleanup", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------
# should_kill_for_reason — pure decision function
# ----------------------------------------------------------------------------

def test_kill_on_clear():
    """ANTIGRAVITY-SPECIFIC: `clear` reason fires when antigravity spawns
    a replacement claude.exe for the new chat. Old process must die.
    Empirical proof at S40, 2026-05-11. See module docstring."""
    hook = _load_hook()
    assert hook.should_kill_for_reason("clear") is True


def test_skip_kill_on_resume():
    """`--resume`/`--continue` transitions session — never kill."""
    hook = _load_hook()
    assert hook.should_kill_for_reason("resume") is False


def test_skip_kill_on_bypass_permissions_disabled():
    """Permissions-mode change — defensive skip."""
    hook = _load_hook()
    assert hook.should_kill_for_reason("bypass_permissions_disabled") is False


def test_kill_on_logout():
    """User logged out — claude.exe should die."""
    hook = _load_hook()
    assert hook.should_kill_for_reason("logout") is True


def test_kill_on_prompt_input_exit():
    """User typed exit / Ctrl+C — claude.exe should die."""
    hook = _load_hook()
    assert hook.should_kill_for_reason("prompt_input_exit") is True


def test_kill_on_other():
    """Normal wrap / tab close / window close — all map to 'other' per empirical data."""
    hook = _load_hook()
    assert hook.should_kill_for_reason("other") is True


def test_skip_kill_on_none_reason():
    """Defensive: if reason field missing, skip kill (better to leak than kill mid-session)."""
    hook = _load_hook()
    assert hook.should_kill_for_reason(None) is False


def test_skip_kill_on_unknown_reason():
    """Defensive: unknown future reason values default to skip."""
    hook = _load_hook()
    assert hook.should_kill_for_reason("future_unknown_value") is False


# ----------------------------------------------------------------------------
# schedule_self_kill — detached taskkill spawn
# ----------------------------------------------------------------------------

def test_schedule_self_kill_returns_false_for_none_pid():
    """No PID -> no kill scheduled."""
    hook = _load_hook()
    assert hook.schedule_self_kill(None) is False


def test_schedule_self_kill_returns_false_for_invalid_pid():
    """Non-int PID -> no kill scheduled."""
    hook = _load_hook()
    assert hook.schedule_self_kill("not-an-int") is False
    assert hook.schedule_self_kill(0) is False
    assert hook.schedule_self_kill(-1) is False


def test_schedule_self_kill_spawns_taskkill_with_pid():
    """Valid PID -> spawn taskkill subprocess with that PID."""
    hook = _load_hook()
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        result = hook.schedule_self_kill(12440)
        assert result is True
        assert mock_popen.called
        args = mock_popen.call_args
        # First positional arg = command list
        cmd = args[0][0]
        assert "taskkill" in cmd[0].lower() or cmd[0].lower().endswith("taskkill")
        assert "/PID" in cmd
        assert "12440" in cmd
        assert "/F" in cmd


def test_schedule_self_kill_uses_create_no_window_flag():
    """Must use CREATE_NO_WINDOW to avoid console flash (Silent Execution Protocol)."""
    if sys.platform != "win32":
        return  # Windows-only constant
    hook = _load_hook()
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        hook.schedule_self_kill(12440)
        kwargs = mock_popen.call_args[1]
        flags = kwargs.get("creationflags", 0)
        # CREATE_NO_WINDOW = 0x08000000
        assert flags & 0x08000000, f"missing CREATE_NO_WINDOW (got flags={hex(flags)})"


def test_schedule_self_kill_detaches_from_parent():
    """Subprocess must detach so kill survives parent claude.exe death."""
    if sys.platform != "win32":
        return
    hook = _load_hook()
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        hook.schedule_self_kill(12440)
        kwargs = mock_popen.call_args[1]
        flags = kwargs.get("creationflags", 0)
        # DETACHED_PROCESS = 0x00000008 OR CREATE_NEW_PROCESS_GROUP = 0x00000200
        # Either one suffices to detach from parent
        DETACHED = 0x00000008
        NEW_PG = 0x00000200
        assert (flags & DETACHED) or (flags & NEW_PG), \
            f"missing DETACHED_PROCESS or CREATE_NEW_PROCESS_GROUP (got flags={hex(flags)})"


def test_schedule_self_kill_swallows_exceptions():
    """Best-effort: subprocess errors must not crash the hook."""
    hook = _load_hook()
    with patch("subprocess.Popen", side_effect=OSError("simulated")):
        result = hook.schedule_self_kill(12440)
        # Returns False on failure rather than raising
        assert result is False


# ----------------------------------------------------------------------------
# Integration: main() respects reason filter
# ----------------------------------------------------------------------------

def test_main_calls_schedule_kill_on_other_reason(tmp_path, monkeypatch):
    """End-to-end: reason='other' triggers kill scheduling."""
    hook = _load_hook()
    # Redirect log files to tmp to avoid polluting real logs
    monkeypatch.setattr(hook, "LOG_FILE", tmp_path / "session-end-log.jsonl")
    monkeypatch.setattr(hook, "KILL_LOG_FILE", tmp_path / "session-end-kill-log.jsonl")
    monkeypatch.setattr(hook, "CRON_MARKER_DIR", tmp_path / "cron-fires")
    with patch.object(hook, "schedule_self_kill", return_value=True) as mock_kill, \
         patch.object(hook, "find_parent_claude_pid", return_value=12440), \
         patch("json.load", return_value={"reason": "other", "hook_event_name": "SessionEnd"}):
        hook.main()
    mock_kill.assert_called_once_with(12440)


def test_main_kills_on_clear_reason(tmp_path, monkeypatch):
    """End-to-end: reason='clear' triggers kill under antigravity (S40 fix).
    On bare CLI this would be wrong; under antigravity the old process is
    already being replaced. See module docstring."""
    hook = _load_hook()
    monkeypatch.setattr(hook, "LOG_FILE", tmp_path / "session-end-log.jsonl")
    monkeypatch.setattr(hook, "KILL_LOG_FILE", tmp_path / "session-end-kill-log.jsonl")
    monkeypatch.setattr(hook, "CRON_MARKER_DIR", tmp_path / "cron-fires")
    with patch.object(hook, "schedule_self_kill", return_value=True) as mock_kill, \
         patch.object(hook, "find_parent_claude_pid", return_value=12440), \
         patch("json.load", return_value={"reason": "clear", "hook_event_name": "SessionEnd"}):
        hook.main()
    mock_kill.assert_called_once_with(12440)


def test_main_skips_kill_when_no_pid_found(tmp_path, monkeypatch):
    """End-to-end: if find_parent_claude_pid returns None, no kill attempted."""
    hook = _load_hook()
    monkeypatch.setattr(hook, "LOG_FILE", tmp_path / "session-end-log.jsonl")
    monkeypatch.setattr(hook, "KILL_LOG_FILE", tmp_path / "session-end-kill-log.jsonl")
    monkeypatch.setattr(hook, "CRON_MARKER_DIR", tmp_path / "cron-fires")
    with patch.object(hook, "schedule_self_kill") as mock_kill, \
         patch.object(hook, "find_parent_claude_pid", return_value=None), \
         patch("json.load", return_value={"reason": "other", "hook_event_name": "SessionEnd"}):
        hook.main()
    mock_kill.assert_not_called()
