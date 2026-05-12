"""Tests for end-session-finalize.py: self-kill ONLY, never kill other claude.exe.

Bug source: 2026-05-11 (post-S40). end-session-finalize.kill_orphans() iterated
every claude.exe on the system and killed every PID != self_pid, with NO age
threshold and NO active-vs-orphan classification. With multiple workspaces open
concurrently (HQ + Sentinel + another Skill Hub instance), the user's active
sessions were killed mid-work. Kill log proof:
  21:36:23 self=25624 killed 17324 (242MB)
  21:36:24 killed 12968 (688MB)   ← active workspace
  21:36:24 killed 16064 (243MB)
  21:36:25 killed 4680  (572MB)   ← active workspace

Fix: remove kill_orphans() entirely. The dedicated kill-orphan-claude-processes.py
exists with proper safeguards (4h age threshold + double-PID check) and is
already scheduled via Claude-Orphan-Cleanup-Hourly. end-session-finalize ends
THIS session only; orphan cleanup is a separate concern with separate tooling.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


SCRIPT_PATH = Path(os.path.expanduser("~/.claude/scripts/end-session-finalize.py"))


def _load_script():
    spec = importlib.util.spec_from_file_location("end_session_finalize", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------
# Core invariant: main() must NEVER taskkill a PID other than self
# ----------------------------------------------------------------------------

def test_main_does_not_kill_non_self_pids():
    """REGRESSION: end-session-finalize must not kill any claude.exe PID
    except self. Multiple active workspace sessions look identical to orphans
    via tasklist; it is not this script's job to distinguish them.
    Orphan cleanup is owned by Claude-Orphan-Cleanup-Hourly with proper
    safeguards (4h age threshold + double-PID check).
    """
    mod = _load_script()

    self_pid = 25624
    other_pids = [(17324, "241980"), (12968, "688368"), (16064, "242616"), (4680, "572196")]
    all_procs = [(self_pid, "200000")] + other_pids

    with patch.object(mod, "list_claude_processes", return_value=all_procs), \
         patch.object(mod, "get_self_claude_pid", return_value=self_pid), \
         patch.object(mod, "schedule_self_kill", return_value=None), \
         patch.object(mod.subprocess, "run") as mock_run, \
         patch.object(sys, "argv", ["end-session-finalize.py", "--no-self-kill"]):
        mod.main()

    # Inspect every subprocess.run call. None may be a taskkill against a non-self PID.
    forbidden_kills = []
    for call in mock_run.call_args_list:
        args = call.args[0] if call.args else call.kwargs.get("args", [])
        if not args or "taskkill" not in str(args[0]).lower():
            continue
        # taskkill /F /PID <pid> or taskkill /PID <pid> /F
        for i, tok in enumerate(args):
            if str(tok).upper() == "/PID" and i + 1 < len(args):
                try:
                    pid = int(args[i + 1])
                except (ValueError, TypeError):
                    continue
                if pid != self_pid:
                    forbidden_kills.append(pid)

    assert not forbidden_kills, (
        f"end-session-finalize killed non-self PIDs: {forbidden_kills}. "
        f"This destroys active workspace sessions. Orphan cleanup belongs in "
        f"Claude-Orphan-Cleanup-Hourly, not end-session-finalize."
    )


def test_kill_orphans_function_removed():
    """The kill_orphans() function should not exist on the module after the fix.
    Keeping the function around invites accidental re-wiring. If orphan cleanup
    is ever needed from this script, route to kill-orphan-claude-processes.py
    explicitly with --execute.
    """
    mod = _load_script()
    assert not hasattr(mod, "kill_orphans"), (
        "kill_orphans() must be removed. Orphan cleanup is owned by "
        "kill-orphan-claude-processes.py (4h threshold + dry-run default)."
    )


def test_self_kill_still_works():
    """Self-kill must still fire. Removing orphan-kill must not regress the
    primary purpose of end-session-finalize: terminating THIS session cleanly.
    """
    mod = _load_script()
    self_pid = 99999

    with patch.object(mod, "list_claude_processes", return_value=[(self_pid, "100000")]), \
         patch.object(mod, "get_self_claude_pid", return_value=self_pid), \
         patch.object(mod, "schedule_self_kill") as mock_self_kill, \
         patch.object(sys, "argv", ["end-session-finalize.py"]):
        mod.main()

    mock_self_kill.assert_called_once()
    # First positional arg to schedule_self_kill is self_pid
    called_pid = mock_self_kill.call_args.args[0]
    assert called_pid == self_pid


def test_no_self_kill_flag_still_skips():
    """--no-self-kill must continue to skip the self-kill (test harness usage)."""
    mod = _load_script()
    self_pid = 99999

    with patch.object(mod, "list_claude_processes", return_value=[(self_pid, "100000")]), \
         patch.object(mod, "get_self_claude_pid", return_value=self_pid), \
         patch.object(mod, "schedule_self_kill") as mock_self_kill, \
         patch.object(sys, "argv", ["end-session-finalize.py", "--no-self-kill"]):
        mod.main()

    mock_self_kill.assert_not_called()
