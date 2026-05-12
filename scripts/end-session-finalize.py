"""
end-session-finalize.py - Final cleanup step of the `end-session` skill.

Runs ONCE at the very end of the 9-step end-session protocol:

  1. Reports the count of running claude.exe processes (diagnostic only)
  2. Schedules a DETACHED self-kill with a configurable delay (default 3s)
     so the terminal renders the final confirmation message BEFORE the kill fires
  3. Writes a kill-log entry for verifiability across sessions

The detached killer outlives the current claude.exe. When it fires, this session
terminates cleanly. Other claude.exe processes are LEFT ALONE — orphan cleanup
is the responsibility of `kill-orphan-claude-processes.py` (4h age threshold +
double-PID safety check) which runs hourly via Claude-Orphan-Cleanup-Hourly.

Source: 2026-05-11 (S41) rename of session-checkpoint -> end-session. Replaces
the broken SessionEnd-hook approach (S39/S40) where `/clear` in antigravity
process-replaces before hooks fire. Invoking THIS script from the skill the
USER explicitly runs (/end-session) removes that timing dependency.

Bug fix 2026-05-11 (post-S40): originally also killed every non-self claude.exe
under the assumption they were orphans. With multiple workspaces open
concurrently, this destroyed the user's active sessions. Orphan-kill removed
entirely; self-kill ONLY. See test_end_session_finalize_self_only.py.

Bug fix 2026-05-11 (S43): the detached killer used `cmd /c "timeout /t N
/nobreak >nul && taskkill /F /PID <pid>"`. Windows `timeout` requires a
console handle; with DETACHED_PROCESS | CREATE_NO_WINDOW | stdin=DEVNULL
there is no console, so `timeout` exits non-zero immediately, `&&`
short-circuits, and `taskkill` never runs. The log entry — written before
the spawn returns — falsely reads "scheduled". Production observed twice
(PIDs 26156 + 8348). Fix: replaced cmd-string with a pure-Python detached
killer (`time.sleep` + `subprocess.run(['taskkill', ...])`). Empirically
verified via test_schedule_self_kill_actually_terminates_victim_pid.

Pure stdlib. Windows-targeted (uses taskkill + DETACHED_PROCESS). On non-Windows
the self-kill is a no-op with a warning (other platforms don't have the same
leak pattern in antigravity).

USAGE:
  python ~/.claude/scripts/end-session-finalize.py             # default 3s self-kill delay
  python ~/.claude/scripts/end-session-finalize.py --delay 10  # 10s grace period
  python ~/.claude/scripts/end-session-finalize.py --no-self-kill  # report state only, do not kill
  python ~/.claude/scripts/end-session-finalize.py --dry-run   # report what would happen, do not kill
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


KILL_LOG = Path.home() / ".claude" / ".tmp" / "session-end-kill-log.jsonl"
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000


def list_claude_processes():
    """Return list of (pid, mem_kb) for all running claude.exe processes."""
    if platform.system() != "Windows":
        return []
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq claude.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=10,
            creationflags=CREATE_NO_WINDOW,
        )
        procs = []
        for line in result.stdout.strip().splitlines():
            parts = [p.strip('"') for p in line.split('","')]
            if len(parts) >= 5 and parts[0].lower().startswith("claude"):
                try:
                    pid = int(parts[1])
                    mem = parts[4].replace(",", "").replace(" K", "").strip()
                    procs.append((pid, mem))
                except (ValueError, IndexError):
                    pass
        return procs
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        return []


def get_self_claude_pid():
    """Find the claude.exe PID that is the parent (or grand-parent) of this script.
    Returns int PID or None if not found.
    """
    if platform.system() != "Windows":
        return None
    # Python script's parent is bash/cmd; bash's parent is claude.exe
    # Walk up the process tree via wmic
    try:
        my_pid = os.getpid()
        # Get parent PID chain
        current = my_pid
        for _ in range(5):  # max 5 levels up
            result = subprocess.run(
                ["wmic", "process", "where", f"ProcessId={current}",
                 "get", "ParentProcessId,Name", "/FORMAT:CSV"],
                capture_output=True, text=True, timeout=5,
                creationflags=CREATE_NO_WINDOW,
            )
            lines = [l for l in result.stdout.strip().splitlines() if l and "," in l]
            if len(lines) < 2:
                return None
            # Parse: Node,Name,ParentProcessId
            parts = lines[1].split(",")
            if len(parts) < 3:
                return None
            name = parts[1].strip().lower()
            try:
                parent = int(parts[2].strip())
            except ValueError:
                return None
            if name == "claude.exe":
                return current
            current = parent
            if current == 0:
                return None
        return None
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        return None


def write_log(entry):
    """Append one JSON line to the kill log."""
    KILL_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(KILL_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as e:
        print(f"WARN: could not write kill log: {e}", file=sys.stderr)


def schedule_self_kill(self_pid, delay, dry_run=False):
    """Spawn detached taskkill with delay. Returns subprocess.Popen or None."""
    if self_pid is None:
        print("WARN: could not determine self claude.exe PID; skipping self-kill",
              file=sys.stderr)
        return None
    if dry_run:
        print(f"  [dry-run] would schedule detached self-kill of PID {self_pid} "
              f"after {delay}s delay")
        write_log({
            "timestamp": datetime.now().isoformat(),
            "session_pid": self_pid,
            "action": "detached_taskkill_scheduled_dryrun",
            "delay_seconds": delay,
            "reason": "end-session-finalize",
        })
        return None

    if platform.system() != "Windows":
        print("WARN: self-kill only implemented on Windows; skipping", file=sys.stderr)
        return None

    # Detached pure-Python killer that sleeps then taskkills the claude.exe PID.
    # Why not `cmd /c "timeout /t N /nobreak >nul && taskkill ..."` —
    #   Windows `timeout` requires a console handle. With DETACHED_PROCESS |
    #   CREATE_NO_WINDOW | stdin=DEVNULL there is no console, so `timeout`
    #   exits non-zero immediately, `&&` short-circuits, taskkill never runs.
    #   `time.sleep` + `subprocess.run` have no console dependency. See S43
    #   bug-fix block in module docstring.
    killer_code = (
        f"import time, subprocess; "
        f"time.sleep({delay}); "
        f"subprocess.run(['taskkill', '/F', '/PID', '{self_pid}'])"
    )
    try:
        proc = subprocess.Popen(
            [sys.executable, "-c", killer_code],
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
            close_fds=True,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        write_log({
            "timestamp": datetime.now().isoformat(),
            "session_pid": self_pid,
            "action": "detached_taskkill_scheduled",
            "delay_seconds": delay,
            "killer_pid": proc.pid,
            "reason": "end-session-finalize",
        })
        return proc
    except (OSError, FileNotFoundError) as e:
        print(f"WARN: failed to schedule self-kill: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="End-session finalize: orphan kill + detached self-kill")
    parser.add_argument("--delay", type=int, default=3,
                        help="Seconds to wait before self-kill fires (default 3)")
    parser.add_argument("--no-self-kill", action="store_true",
                        help="Kill orphans but do NOT schedule self-kill (keep current session alive)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would happen without actually killing anything")
    args = parser.parse_args()

    print("End-session finalize starting...")
    self_pid = get_self_claude_pid()
    if self_pid:
        print(f"  current session claude.exe PID: {self_pid}")
    else:
        print("  current session claude.exe PID: UNKNOWN (will not self-kill)")

    procs = list_claude_processes()
    print(f"  total claude.exe processes running: {len(procs)}")
    if len(procs) > 1:
        print(f"  NOTE: {len(procs) - 1} other claude.exe process(es) detected.")
        print(f"        These are NOT killed by end-session. Orphan cleanup is")
        print(f"        owned by Claude-Orphan-Cleanup-Hourly (4h age threshold).")

    if args.no_self_kill:
        print("  self-kill SKIPPED (--no-self-kill)")
        return 0

    if self_pid is None:
        print("  self-kill SKIPPED (could not determine self PID)")
        return 0

    proc = schedule_self_kill(self_pid, args.delay, dry_run=args.dry_run)
    if proc:
        print(f"  detached self-kill scheduled: PID {self_pid} will be killed in {args.delay}s")
        print(f"  (detached killer PID: {proc.pid})")
    elif args.dry_run:
        pass  # already reported
    else:
        print("  WARN: self-kill could not be scheduled")

    return 0


if __name__ == "__main__":
    sys.exit(main())
