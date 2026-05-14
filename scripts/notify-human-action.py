#!/usr/bin/env python3
"""
notify-human-action.py -- Append an entry to a workspace's HUMAN-ACTION-REQUIRED.md
file and send a Slack (Polaris bot) notification in one atomic call.

Implements the Human Action Required Protocol in ~/.claude/rules/universal-protocols.md
(originally per wr-2026-04-21-006; channel migrated to Slack per
wr-sentinel-2026-05-13-002, 2026-05-13). Any workspace closing work that requires
a user-facing action before dependent work can proceed MUST call this helper to
surface the ask actively; silent drift is prohibited.

Channel decision (2026-05-13): Slack is the canonical outbound alert channel.
Telegram is repurposed for two-way mobile bridge only and is NOT used here.

Usage:
    python ~/.claude/scripts/notify-human-action.py \
        --workspace skill-management-hub \
        --action "Execute credential migration Step 1" \
        --execute-from skill-management-hub \
        --reference-id wr-2026-04-21-007 \
        --details "From Skill Hub: python tools/migrate-env-to-global.py --workspace skillhub --execute" \
        --expected-outcome "~/.claude/.env contains SKILLHUB_* prefixed keys"

Credentials (loaded from ~/.claude/.env, then per-workspace .env):
    SLACK_POLARIS_BOT_OAUTH_TOKEN  OAuth token for the Polaris bot

Per-workspace dedicated channels (set 2026-05-13):
    SKILL_MANAGMENT_HUB_ALERTS     C0B0P7H0BL6   (skill-management-hub)
    HQ_ALERTS                      C0B0MT7ANTF   (workforce-hq)
    SENTINEL_ALERTS                C0B0P86BU3Y   (sentinel)

Channel resolution order (per Human Action Required Protocol + 2026-05-13 channel routing):
    1. CLI --channel (explicit override)
    2. Workspace's dedicated channel env var (based on --workspace flag)

If Slack credentials are missing, the file entry is still written and the
script prints a warning. File update is mandatory; Slack is advisory.

Non-blocking; always exits 0 unless CLI args are malformed. Pure stdlib.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from importlib import util
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
                if "#" in v:
                    v = v.split("#", 1)[0].strip()
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
Channel: Slack (Polaris bot) per wr-sentinel-2026-05-13-002, 2026-05-13.

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


def _load_notify_slack():
    """Import notify-slack.py as a module (it uses a hyphenated filename)."""
    slack_path = Path.home() / ".claude" / "scripts" / "notify-slack.py"
    if not slack_path.exists():
        return None
    spec = util.spec_from_file_location("notify_slack", str(slack_path))
    if spec is None or spec.loader is None:
        return None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


WORKSPACE_CHANNEL_ENV = {
    "skill-management-hub": "SKILL_MANAGMENT_HUB_ALERTS",
    "workforce-hq":          "HQ_ALERTS",
    "sentinel":              "SENTINEL_ALERTS",
}


def send_slack_notification(env, workspace, channel_override, message):
    """Post the HAR alert via Polaris bot to the workspace's dedicated channel.

    Per 2026-05-13 channel routing: each workspace has its own dedicated channel.
    HAR notifications route to the workspace whose HAR file was just appended,
    so the user sees the alert in the channel for that workspace.
    """
    mod = _load_notify_slack()
    if mod is None:
        return False, "notify-slack.py not available"
    token = env.get("SLACK_POLARIS_BOT_OAUTH_TOKEN")
    channel = channel_override
    if not channel:
        channel_env_name = WORKSPACE_CHANNEL_ENV.get(workspace)
        if channel_env_name:
            channel = env.get(channel_env_name)
    if not token:
        return False, "missing credentials: SLACK_POLARIS_BOT_OAUTH_TOKEN"
    if not channel:
        env_name = WORKSPACE_CHANNEL_ENV.get(workspace, "(unmapped workspace)")
        return False, f"missing credentials: channel (env {env_name} for workspace '{workspace}')"
    return mod.send_slack(message=message, channel=channel, token=token, env=env)


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
    p.add_argument("--channel", default=None,
                   help="Slack channel ID override (else env-resolved)")
    p.add_argument("--skip-slack", action="store_true",
                   help="Append file entry only; skip Slack notification")
    p.add_argument("--skip-telegram", action="store_true",
                   help="DEPRECATED alias for --skip-slack (Telegram channel removed 2026-05-13).")
    args = p.parse_args()

    root = workspace_root(args.workspace)
    if not root:
        print(f"ERROR: Unknown workspace '{args.workspace}'", file=sys.stderr)
        return 2

    file_path = root / "HUMAN-ACTION-REQUIRED.md"
    append_entry(file_path, args.workspace, args.action, args.execute_from,
                 args.reference_id, args.details, args.expected_outcome)
    print(f"OK: appended entry to {file_path}")

    if args.skip_slack or args.skip_telegram:
        if args.skip_telegram and not args.skip_slack:
            print("NOTE: --skip-telegram is deprecated; honoring as --skip-slack "
                  "(channel migrated 2026-05-13 per wr-sentinel-2026-05-13-002)")
        print("OK: skipped Slack notification")
        return 0

    env = load_env()
    message = (
        "[HUMAN ACTION NEEDED]\n"
        f"Workspace: {args.workspace}\n"
        f"Action: {args.action}\n"
        f"Reference: {args.reference_id}\n"
        f"Details: {args.workspace}/HUMAN-ACTION-REQUIRED.md"
    )
    ok, err = send_slack_notification(env, args.workspace, args.channel, message)
    if ok:
        print("OK: Slack notification sent")
    else:
        print(f"WARN: Slack notification failed ({err}); file entry still written")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
