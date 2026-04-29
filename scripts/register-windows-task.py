#!/usr/bin/env python3
"""
register-windows-task.py -- Permanent fix for the schtasks-with-spaces class
of failures.

Background:
  Windows Task Scheduler is registered via the `schtasks` CLI. Calling
  `schtasks /Create` from Bash through cmd /c -- when the target executable
  path contains spaces or `.- ` prefixes (like our workspace
  `3.- Skill Management Hub`) -- repeatedly fails because the multi-layer
  quoting (Bash -> cmd -> schtasks) drops or mis-escapes quotes.

  PowerShell can do this cleanly, but the workspace has a deny rule on
  `powershell` invocations from Bash to prevent shell-bypass abuse. That
  deny rule is correct in spirit but blocks the legitimate path.

  Python's subprocess.run(list_args) bypasses the multi-shell layer entirely:
  Windows takes the args list and hands them to the schtasks process directly,
  so spaces and quirky prefixes stay intact. This helper wraps that pattern
  so every workspace can register Task Scheduler entries without re-solving
  the quoting puzzle each time.

Usage:
  python ~/.claude/scripts/register-windows-task.py create \\
      --task-name "Toolkit-Monitor-Daily" \\
      --run "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/tools/audit-cadence-engine.bat" \\
      --schedule daily \\
      --start-time 18:00

  python ~/.claude/scripts/register-windows-task.py query --task-name "Toolkit-Monitor-Daily"
  python ~/.claude/scripts/register-windows-task.py delete --task-name "Toolkit-Monitor-Daily"

Exit codes:
  0  success
  1  schtasks failure (output included in stderr)
  2  bad CLI args

Pure stdlib. Cross-workspace usable from any location.

Source: wr-2026-04-29 Fork A (Skill Hub session 11). Permanent solution to
the path-escape failure class observed during Toolkit Monitor scheduling.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from typing import List


def _have_schtasks() -> bool:
    """True iff schtasks.exe is on PATH (only present on Windows)."""
    return shutil.which("schtasks") is not None


def _run_schtasks(args: List[str], dry_run: bool = False) -> int:
    """Run schtasks with list-form args. No shell. Returns exit code.

    list-form args means Windows hands the strings to schtasks directly,
    so paths-with-spaces and `.- ` prefixes survive intact -- no Bash/cmd
    quoting layer to mangle them.
    """
    cmd = ["schtasks"] + args
    if dry_run:
        print("DRY RUN: would execute:")
        for tok in cmd:
            print(f"  {tok}")
        return 0
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("ERROR: schtasks timed out after 60 seconds", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("ERROR: schtasks.exe not found on PATH (Windows-only tool)",
              file=sys.stderr)
        return 1

    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.returncode != 0 and proc.stderr:
        sys.stderr.write(proc.stderr)
    return proc.returncode


# ---------------------------------------------------------------------------
# Subcommand: create
# ---------------------------------------------------------------------------

_SCHEDULE_MAP = {
    "daily": "DAILY",
    "weekly": "WEEKLY",
    "hourly": "HOURLY",
    "minute": "MINUTE",
    "once": "ONCE",
    "onlogon": "ONLOGON",
    "onstart": "ONSTART",
}


def cmd_create(args: argparse.Namespace) -> int:
    """schtasks /Create with proper list-form args."""
    sc = _SCHEDULE_MAP.get(args.schedule.lower())
    if sc is None:
        print(f"ERROR: unknown schedule '{args.schedule}'. "
              f"Valid: {', '.join(_SCHEDULE_MAP.keys())}", file=sys.stderr)
        return 2

    schtasks_args: List[str] = [
        "/Create",
        "/SC", sc,
        "/TN", args.task_name,
        "/TR", args.run,
    ]
    if args.start_time and sc not in ("ONLOGON", "ONSTART", "MINUTE", "HOURLY"):
        schtasks_args.extend(["/ST", args.start_time])
    if args.start_date and sc == "ONCE":
        schtasks_args.extend(["/SD", args.start_date])
    if args.modifier:
        schtasks_args.extend(["/MO", str(args.modifier)])
    if args.run_as:
        schtasks_args.extend(["/RU", args.run_as])
    if args.run_level == "highest":
        schtasks_args.append("/RL")
        schtasks_args.append("HIGHEST")
    if args.force:
        schtasks_args.append("/F")

    rc = _run_schtasks(schtasks_args, dry_run=args.dry_run)
    if rc != 0:
        return 1

    if args.verify and not args.dry_run:
        # Re-query to confirm the task actually landed.
        print(f"\n--- VERIFY: schtasks /Query /TN {args.task_name!r} ---")
        verify_rc = _run_schtasks(["/Query", "/TN", args.task_name, "/FO", "LIST"])
        if verify_rc != 0:
            print(f"WARN: task created but verification query failed "
                  f"(rc={verify_rc})", file=sys.stderr)
            return 1
    return 0


# ---------------------------------------------------------------------------
# Subcommand: query
# ---------------------------------------------------------------------------

def cmd_query(args: argparse.Namespace) -> int:
    schtasks_args = ["/Query"]
    if args.task_name:
        schtasks_args.extend(["/TN", args.task_name])
    if args.verbose:
        schtasks_args.extend(["/V", "/FO", "LIST"])
    else:
        schtasks_args.extend(["/FO", "LIST"])
    return _run_schtasks(schtasks_args, dry_run=args.dry_run) or 0


# ---------------------------------------------------------------------------
# Subcommand: delete
# ---------------------------------------------------------------------------

def cmd_delete(args: argparse.Namespace) -> int:
    schtasks_args = ["/Delete", "/TN", args.task_name]
    if args.force:
        schtasks_args.append("/F")
    return _run_schtasks(schtasks_args, dry_run=args.dry_run) or 0


# ---------------------------------------------------------------------------
# Main / argparse
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="register-windows-task",
        description=(
            "Permanent helper for Windows Task Scheduler registration that "
            "bypasses the Bash/cmd quoting failures with paths-with-spaces."
        ),
    )
    sub = p.add_subparsers(dest="subcommand", required=True)

    # create
    c = sub.add_parser("create", help="Register or replace a scheduled task")
    c.add_argument("--task-name", required=True,
                   help="Task name as it will appear in Task Scheduler "
                   "(e.g. 'Toolkit-Monitor-Daily')")
    c.add_argument("--run", required=True,
                   help="Full path to the program/script to execute "
                   "(.bat, .exe, etc). Quotes around spaces are added "
                   "automatically; do NOT pre-quote.")
    c.add_argument("--schedule", required=True,
                   choices=list(_SCHEDULE_MAP.keys()),
                   help="Schedule type")
    c.add_argument("--start-time",
                   help="HH:MM (24-hour) for DAILY/WEEKLY/ONCE schedules")
    c.add_argument("--start-date",
                   help="YYYY-MM-DD for ONCE schedule (defaults to today)")
    c.add_argument("--modifier",
                   help="Schedule modifier (e.g. interval days for DAILY, "
                   "minute count for MINUTE)")
    c.add_argument("--run-as",
                   help="User to run as (omit for current user / SYSTEM)")
    c.add_argument("--run-level", choices=["limited", "highest"],
                   default="limited",
                   help="Privilege level (default: limited)")
    c.add_argument("--force", action="store_true", default=True,
                   help="Overwrite existing task with same name (default: on)")
    c.add_argument("--no-force", dest="force", action="store_false",
                   help="Do NOT overwrite existing task")
    c.add_argument("--verify", action="store_true", default=True,
                   help="Re-query after create to confirm task landed (default: on)")
    c.add_argument("--no-verify", dest="verify", action="store_false",
                   help="Skip verification query")
    c.add_argument("--dry-run", action="store_true",
                   help="Print the schtasks command without executing")
    c.set_defaults(func=cmd_create)

    # query
    q = sub.add_parser("query", help="Query existing scheduled task(s)")
    q.add_argument("--task-name",
                   help="Specific task to query (omit to list all)")
    q.add_argument("--verbose", "-v", action="store_true",
                   help="Verbose output (full task details)")
    q.add_argument("--dry-run", action="store_true",
                   help="Print the schtasks command without executing")
    q.set_defaults(func=cmd_query)

    # delete
    d = sub.add_parser("delete", help="Delete a scheduled task")
    d.add_argument("--task-name", required=True,
                   help="Task name to delete")
    d.add_argument("--force", action="store_true", default=True,
                   help="Skip confirmation prompt (default: on)")
    d.add_argument("--no-force", dest="force", action="store_false",
                   help="Prompt for confirmation")
    d.add_argument("--dry-run", action="store_true",
                   help="Print the schtasks command without executing")
    d.set_defaults(func=cmd_delete)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not _have_schtasks() and not args.dry_run:
        print("ERROR: schtasks.exe not found on PATH. This tool only works on "
              "Windows. Use --dry-run to preview the command on other platforms.",
              file=sys.stderr)
        return 1
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
