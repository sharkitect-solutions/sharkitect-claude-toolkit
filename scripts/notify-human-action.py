#!/usr/bin/env python3
"""
notify-human-action.py -- Append an entry to a workspace's HUMAN-ACTION-REQUIRED.md
file and send a Telegram HQ bot notification in one atomic call.

Implements the Human Action Required Protocol added to universal-protocols.md
per wr-2026-04-21-006. Any workspace closing work that requires a user-facing
action before dependent work can proceed MUST call this helper to surface the
ask actively; silent drift is prohibited.

Usage:
    python ~/.claude/scripts/notify-human-action.py \
        --workspace skill-management-hub \
        --action "Execute credential migration Step 1" \
        --execute-from skill-management-hub \
        --reference-id wr-2026-04-21-007 \
        --details "From Skill Hub: python tools/migrate-env-to-global.py --workspace skillhub --execute" \
        --expected-outcome "~/.claude/.env contains SKILLHUB_* prefixed keys"

Credentials (in ~/.claude/.env, then fall back to per-workspace .env):
    TELEGRAM_BOT_TOKEN   Bot token for @SharkitectHQBot
    TELEGRAM_CHAT_ID     Chat ID to message

If Telegram credentials are missing, the file entry is still written and
the script prints a warning. File update is mandatory; Telegram is advisory.

Non-blocking; always exits 0 unless CLI args are malformed. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_PATHS = {
    "workforce-hq": "1.- SHARKITECT DIGITAL WORKFORCE HQ",
    "skill-management-hub": "3.- Skill Management Hub",
    "sentinel": "4.- Sentinel",
}


def load_env():
    """Load env from ~/.claude/.env first, then per-workspace .env as fallback."""
    env = dict(os.environ)
    for candidate in [
        Path.home() / ".claude" / ".env",
        Path.cwd() / ".env",
    ]:
        if not candidate.exists():
            continue
        try:
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in env:
                    env[k] = v
        except OSError:
            continue
    return env


def workspace_root(workspace):
    if workspace not in WORKSPACE_PATHS:
        return None
    return Path.home() / "Documents" / "Claude Code Workspaces" / WORKSPACE_PATHS[workspace]


FILE_HEADER = """# HUMAN ACTION REQUIRED -- {workspace}

This file accumulates all user-facing actions that block work in this workspace.
Each entry is appended when a workspace closes work that requires a user step.
When the user completes the action, the entry is updated with `Status: done`
and a completion timestamp.

**Rules:**
- Append-only. Do not overwrite or delete entries.
- `Status: open` entries older than 24h trigger Sentinel morning-report flagging.
- When the user says done in the workspace: verify the precondition signal,
  set Status to done, fill Done timestamp, append resolution line, then run
  the blocked work.

Source: universal-protocols.md Human Action Required Protocol (wr-2026-04-21-006).

---

"""


def append_entry(file_path, workspace, action, execute_from, reference_id,
                 details, expected_outcome):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        file_path.write_text(FILE_HEADER.format(workspace=workspace), encoding="utf-8")

    now = datetime.now(timezone.utc)
    entry = (
        f"## {now.date().isoformat()} -- {action}\n\n"
        f"- **Requesting workspace:** {workspace}\n"
        f"- **Execute from:** {execute_from}\n"
        f"- **Reference ID:** {reference_id}\n"
        f"- **Action required:**\n"
        f"  {details}\n"
        f"- **Expected outcome:**\n"
        f"  {expected_outcome}\n"
        f"- **Status:** open\n"
        f"- **Filed:** {now.isoformat()}\n"
        f"- **Done:** (pending)\n\n"
        f"---\n\n"
    )
    with file_path.open("a", encoding="utf-8") as fh:
        fh.write(entry)


def send_telegram(token, chat_id, message):
    if not token or not chat_id:
        return False, "missing credentials"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            result = json.loads(body)
            if result.get("ok"):
                return True, ""
            return False, f"telegram api: {result.get('description', 'unknown')}"
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as exc:
        return False, f"{type(exc).__name__}: {exc}"


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").strip().split("\n")[0])
    p.add_argument("--workspace", required=True, choices=list(WORKSPACE_PATHS.keys()),
                   help="Canonical workspace name where the file is created")
    p.add_argument("--action", required=True, help="One-line action summary")
    p.add_argument("--execute-from", required=True,
                   help="Workspace the user should run the action from")
    p.add_argument("--reference-id", required=True,
                   help="WR / RT / task id that surfaced the action")
    p.add_argument("--details", required=True,
                   help="Multi-line step-by-step detail for the user")
    p.add_argument("--expected-outcome", required=True,
                   help="Success signal the workspace will verify on completion")
    p.add_argument("--skip-telegram", action="store_true",
                   help="Append file entry only; skip Telegram notification")
    args = p.parse_args()

    root = workspace_root(args.workspace)
    if not root:
        print(f"ERROR: Unknown workspace '{args.workspace}'", file=sys.stderr)
        return 2

    file_path = root / "HUMAN-ACTION-REQUIRED.md"
    append_entry(file_path, args.workspace, args.action, args.execute_from,
                 args.reference_id, args.details, args.expected_outcome)
    print(f"OK: appended entry to {file_path}")

    if args.skip_telegram:
        print("OK: skipped Telegram notification (--skip-telegram)")
        return 0

    env = load_env()
    token = env.get("TELEGRAM_BOT_TOKEN") or env.get("HQ_TELEGRAM_BOT_TOKEN")
    chat_id = env.get("TELEGRAM_CHAT_ID") or env.get("HQ_TELEGRAM_CHAT_ID")
    message = (
        "[HUMAN ACTION NEEDED]\n"
        f"Workspace: {args.workspace}\n"
        f"Action: {args.action}\n"
        f"Details: {args.workspace}/HUMAN-ACTION-REQUIRED.md"
    )
    ok, err = send_telegram(token, chat_id, message)
    if ok:
        print("OK: Telegram notification sent")
    else:
        print(f"WARN: Telegram notification failed ({err}); file entry still written")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
