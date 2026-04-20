"""
cron-activity-surfacer.py - UserPromptSubmit hook surfacing cron activity

Filed by: HQ wr-2026-04-19_workforce-hq_cron-fired-work-invisible-to-user-session
Companion to cron-activity-logger.py (PostToolUse hook that writes the log).

What it does:
  On EVERY user-submitted prompt (real interactive prompt, NOT a cron-fired
  prompt), checks ~/.claude/.tmp/cron-activity-log.jsonl for entries that
  haven't been surfaced yet.

  If unread entries exist, injects additionalContext into the user's message
  summarizing what cron-fired sessions did since the last interactive turn.

  Tracks "what's been surfaced" via a cursor file
  ~/.claude/.tmp/cron-activity-surfaced-at.json that records the last-shown
  timestamp. Only entries newer than that timestamp are surfaced.

  Skips itself when the prompt IS a cron prompt (so cron fires don't
  surface their own activity to themselves).

Input: JSON on stdin with prompt/user_prompt.
Output: JSON on stdout with hookSpecificOutput.additionalContext.

Pure Python stdlib. Never blocks.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


LOG_FILE = Path.home() / ".claude" / ".tmp" / "cron-activity-log.jsonl"
CURSOR_FILE = Path.home() / ".claude" / ".tmp" / "cron-activity-surfaced-at.json"
MAX_ENTRIES_TO_SHOW = 25


CRON_SIGNATURES = [
    "MID-SESSION INBOX POLL",
    "Mid-Session Inbox Polling Protocol",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def is_cron_prompt(prompt_text):
    if not prompt_text:
        return False
    return any(sig in prompt_text for sig in CRON_SIGNATURES)


def get_cursor():
    if not CURSOR_FILE.exists():
        return None
    try:
        return json.loads(CURSOR_FILE.read_text(encoding="utf-8")).get("last_surfaced_at")
    except Exception:
        return None


def set_cursor(ts):
    CURSOR_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        CURSOR_FILE.write_text(json.dumps({"last_surfaced_at": ts}), encoding="utf-8")
    except Exception:
        pass


def read_unread_entries(cursor):
    """Read JSONL log, return entries with timestamp > cursor."""
    if not LOG_FILE.exists():
        return []
    entries = []
    try:
        with open(LOG_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                ts = e.get("timestamp", "")
                if not ts:
                    continue
                if cursor is None or ts > cursor:
                    entries.append(e)
    except Exception:
        return []
    return entries


def format_summary(entries):
    """Build a human-friendly summary block."""
    if not entries:
        return ""
    # Group by session_pid + cron_fire_count to show fire boundaries
    groups = {}
    for e in entries:
        key = (e.get("session_pid"), e.get("cron_fire_count"))
        groups.setdefault(key, []).append(e)

    lines = [
        f"**AUTONOMOUS CRON ACTIVITY SINCE YOUR LAST MESSAGE ({len(entries)} action(s))**",
        "",
        "While you were away, cron-fired Claude sessions performed these actions:",
    ]
    shown = 0
    for (pid, fire), items in sorted(groups.items(), key=lambda x: (x[0][0] or 0, x[0][1] or 0)):
        first_ts = items[0].get("timestamp", "")
        lines.append("")
        lines.append(f"- **Session PID {pid}, cron fire #{fire}** (first action {first_ts}):")
        for e in items:
            if shown >= MAX_ENTRIES_TO_SHOW:
                lines.append(f"  - ... ({len(entries) - shown} more, see ~/.claude/.tmp/cron-activity-log.jsonl)")
                break
            lines.append(f"  - {e.get('timestamp', '')[:19]}Z  {e.get('summary', '')}")
            shown += 1
        if shown >= MAX_ENTRIES_TO_SHOW:
            break
    lines.extend([
        "",
        "If any of this was unexpected or shouldn't have happened autonomously, "
        "say so and we'll investigate which session/cron did it. The full log "
        "is at `~/.claude/.tmp/cron-activity-log.jsonl`.",
    ])
    return "\n".join(lines)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    prompt = (payload.get("prompt") or payload.get("user_prompt") or "")
    if is_cron_prompt(prompt):
        return 0  # Don't surface to a cron-fired prompt itself

    cursor = get_cursor()
    entries = read_unread_entries(cursor)
    if not entries:
        return 0

    summary = format_summary(entries)
    # Advance cursor to newest entry
    newest_ts = max(e.get("timestamp", "") for e in entries)
    set_cursor(newest_ts)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": summary,
        }
    }
    json.dump(output, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
