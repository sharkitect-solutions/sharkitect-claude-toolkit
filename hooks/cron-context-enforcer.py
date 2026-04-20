"""
cron-context-enforcer.py - UserPromptSubmit hook enforcing cron-fire mode rules

Filed by:
  - HQ wr-2026-04-19_workforce-hq_cron-idle-detection-violates-first-fire-rule
    (CRITICAL): cron-fired session classified self as IDLE on first fire and
    autonomously processed inbox items without triage briefing.

What it does:
  Detects cron-fired prompts (recognized by the "MID-SESSION INBOX POLL"
  signature from universal-protocols.md cron template).

  On detection, injects additionalContext to:
    1. ENFORCE FIRST FIRE = ACTIVE: For the first cron fire in this Claude
       process's lifetime, force triage-only mode regardless of inferred
       user state (cron has no clock, no user activity is reliably
       detectable on first fire).
    2. ORPHAN AWARENESS: If the parent claude.exe process is older than 4h,
       this session may be an orphan -- inject a reminder that the user
       likely cannot see this output, so default to triage-mode and log
       all activity to .tmp/cron-activity-log.jsonl for surfacing later.
    3. RESPECT BLOCKED/IMMOVABLE: re-state the inbox-move-guard rule.

  Tracks fires per-session via a marker file keyed on the parent claude.exe PID.
  First fire creates the marker; subsequent fires see it.

Input: JSON on stdin with prompt, session_id, etc.
Output: JSON on stdout with hookSpecificOutput.additionalContext (if cron context).

Non-blocking: this hook never denies a prompt, only injects context.
Pure Python stdlib.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


CRON_MARKER_DIR = Path.home() / ".claude" / ".tmp" / "cron-fires"
ORPHAN_AGE_HOURS = 4.0

# The signature phrase that uniquely identifies a cron-fired inbox-poll prompt
# (from universal-protocols.md and per-workspace CLAUDE.md cron template).
CRON_SIGNATURES = [
    "MID-SESSION INBOX POLL",
    "Mid-Session Inbox Polling Protocol",
    "Step 1: Determine session mode",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def is_cron_prompt(prompt_text: str) -> bool:
    if not prompt_text:
        return False
    t = prompt_text.strip()
    return any(sig in t for sig in CRON_SIGNATURES)


def find_parent_claude_pid():
    """
    Walk up parents from this hook's PID to find claude.exe ancestor.
    Returns PID or None.
    """
    try:
        my_pid = os.getpid()
        for _ in range(10):
            out = subprocess.check_output(
                ["wmic", "process", "where", f"ProcessId={my_pid}",
                 "get", "Name,ParentProcessId", "/format:csv"],
                stderr=subprocess.DEVNULL, text=True, timeout=5,
            )
            name = parent = None
            for line in out.splitlines():
                line = line.strip()
                if not line or line.startswith("Node") or "Name" in line:
                    continue
                parts = line.split(",")
                if len(parts) >= 3:
                    name = parts[1].strip().lower()
                    try:
                        parent = int(parts[2].strip())
                    except (ValueError, TypeError):
                        parent = None
            if name == "claude.exe":
                return my_pid
            if not parent or parent == my_pid:
                return None
            my_pid = parent
        return None
    except Exception:
        return None


def get_process_age_hours(pid: int):
    """Return age in hours of given PID's process, or None on failure."""
    try:
        out = subprocess.check_output(
            ["wmic", "process", "where", f"ProcessId={pid}",
             "get", "CreationDate", "/format:csv"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        )
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("Node") or "CreationDate" in line:
                continue
            parts = line.split(",")
            if len(parts) >= 2:
                created_raw = parts[1].strip()
                m = re.match(r"^(\d{14})\.\d+([+-]\d+)$", created_raw)
                if m:
                    ts_part, tz_part = m.groups()
                    naive = datetime.strptime(ts_part, "%Y%m%d%H%M%S")
                    tz = timezone(timedelta(minutes=int(tz_part)))
                    created = naive.replace(tzinfo=tz)
                    age = datetime.now(timezone.utc) - created
                    return age.total_seconds() / 3600
    except Exception:
        pass
    return None


def record_fire(session_pid):
    """
    Marker file per-session tracking cron fires.
    Returns (is_first_fire, fire_count).
    """
    CRON_MARKER_DIR.mkdir(parents=True, exist_ok=True)
    marker = CRON_MARKER_DIR / f"session-{session_pid or 'unknown'}.json"
    is_first = not marker.exists()
    if is_first:
        data = {
            "session_pid": session_pid,
            "first_fire_at": now_iso(),
            "last_fire_at": now_iso(),
            "fire_count": 1,
        }
    else:
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            data["fire_count"] = int(data.get("fire_count", 0)) + 1
            data["last_fire_at"] = now_iso()
        except Exception:
            data = {
                "session_pid": session_pid,
                "first_fire_at": now_iso(),
                "last_fire_at": now_iso(),
                "fire_count": 1,
            }
            is_first = True
    marker.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return is_first, data["fire_count"]


def build_context(is_first_fire, fire_count, age_hours, session_pid):
    """Build the additionalContext message based on detected conditions."""
    blocks = []

    if is_first_fire:
        blocks.append(
            "**CRON FIRST-FIRE DETECTED (PID " + str(session_pid or "?") + ").**\n"
            "Per Mid-Session Inbox Polling Protocol: the FIRST cron fire of any "
            "session DEFAULTS TO ACTIVE MODE -- triage-only, no autonomous "
            "processing, regardless of any other signal you might infer.\n"
            "  - Check inboxes (.work-requests/, .lifecycle-reviews/, .routed-tasks/)\n"
            "  - Classify each item by priority + estimated time-to-fix\n"
            "  - Present a brief intelligent summary with handle-now-vs-defer recommendations\n"
            "  - DO NOT process. Wait for the user to direct you."
        )
    else:
        blocks.append(
            f"**CRON RE-FIRE (#{fire_count} this session, PID {session_pid or '?'}).**\n"
            "Apply Mid-Session Inbox Polling Protocol mode-detection:\n"
            "  - ACTIVE if user sent ANY message between previous cron and now -> triage only.\n"
            "  - IDLE only if NO user message between previous cron and now (long-running "
            "background tasks do NOT count as user activity)."
        )

    if age_hours is not None and age_hours >= ORPHAN_AGE_HOURS:
        blocks.append(
            f"**WARNING: This claude.exe process is {age_hours:.1f}h old (suspect orphan).**\n"
            "If you are firing autonomously, the user almost certainly CANNOT see "
            "your output. Default to triage-only mode and log every action you "
            "take to ~/.claude/.tmp/cron-activity-log.jsonl so it can be surfaced "
            "to the user when they return. Do NOT process inbox items in this state "
            "unless they are critical AND blocking other work."
        )

    blocks.append(
        "**Inbox discipline:** items with status 'blocked' or 'deferred' MUST stay "
        "in inbox/. Use ~/.claude/scripts/close-inbox-item.py to close items -- "
        "it atomically writes resolution + status + history + moves the file."
    )

    return "\n\n".join(blocks)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # No input -> nothing to do
        return 0

    # UserPromptSubmit field name varies by client; check both
    prompt = (payload.get("prompt") or payload.get("user_prompt") or "")
    if not is_cron_prompt(prompt):
        return 0

    session_pid = find_parent_claude_pid()
    age_hours = get_process_age_hours(session_pid) if session_pid else None
    is_first, fire_count = record_fire(session_pid)
    context = build_context(is_first, fire_count, age_hours, session_pid)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    json.dump(output, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
