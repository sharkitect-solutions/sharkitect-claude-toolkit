#!/usr/bin/env python3
"""
notify-slack.py -- Reusable global helper for posting messages to Slack
via the Polaris bot (or any Slack OAuth token). Parallel to
notify-human-action.py but for Slack instead of Telegram + .md file.

Built per wr-skillhub-2026-04-29-002. The audit_cadence_engine.py inline
send_slack_notification() proved the pattern; this script lifts it to a
global helper any workspace can call.

Usage as CLI:
    python ~/.claude/scripts/notify-slack.py \
        --message "Hello from a workspace" \
        --channel C0B0P7H0BL6 \
        --token-env SLACK_POLARIS_BOT_OAUTH_TOKEN

Usage as importable module:
    from importlib import util
    spec = util.spec_from_file_location("notify_slack",
        os.path.expanduser("~/.claude/scripts/notify-slack.py"))
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ok, err = mod.send_slack(message="Hi", channel="C123", env=os.environ)

Credential resolution order (first hit wins):
    1. CLI --token + --channel (explicit overrides)
    2. Process environment vars (e.g., set in shell before invocation)
    3. ~/.claude/.env (global)
    4. ./env (workspace fallback, current working directory)

Exit codes:
    0 = posted successfully OR --skip-slack (dry run)
    1 = missing credentials AND --require-creds was set
    2 = Slack API call failed
    3 = invalid CLI args

Stdlib only. No external dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Mapping, Optional, Tuple


SLACK_API_POST_MESSAGE = "https://slack.com/api/chat.postMessage"

DEFAULT_TOKEN_ENV = "SLACK_POLARIS_BOT_OAUTH_TOKEN"
DEFAULT_CHANNEL_ENV = "SLACK_POLARIS_DEFAULT_CHANNEL"


def load_env() -> dict:
    """Load env from process env, then ~/.claude/.env, then ./.env (workspace).

    Process env wins over .env files (so explicit shell overrides take effect).
    ~/.claude/.env wins over workspace .env (so workspace can selectively
    override, but global is the canonical source).
    """
    env = dict(os.environ)
    candidates = [
        Path.home() / ".claude" / ".env",
        Path.cwd() / ".env",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        try:
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Strip inline comments after the value (e.g. KEY=val # comment)
                if "#" in value:
                    value = value.split("#", 1)[0].strip()
                if key and key not in env:
                    env[key] = value
        except OSError:
            continue
    return env


def _http_post(url: str, headers: Mapping[str, str], data: bytes) -> Tuple[bool, str]:
    """POST to Slack chat.postMessage. Pulled out so tests can inject a stub."""
    try:
        req = urllib.request.Request(
            url, data=data, headers=dict(headers), method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            result = json.loads(body)
            if result.get("ok"):
                return True, ""
            return False, f"slack api: {result.get('error', 'unknown')}"
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        json.JSONDecodeError,
        OSError,
    ) as exc:
        return False, f"{type(exc).__name__}: {exc}"


def send_slack(
    message: str,
    channel: Optional[str] = None,
    token: Optional[str] = None,
    *,
    token_env_name: str = DEFAULT_TOKEN_ENV,
    channel_env_name: str = DEFAULT_CHANNEL_ENV,
    env: Optional[Mapping[str, str]] = None,
    http_post=None,
    mrkdwn: bool = True,
) -> Tuple[bool, str]:
    """Post a message to Slack via Polaris bot (or any OAuth token).

    Args:
        message: Text body. Pass mrkdwn=True for Slack markdown formatting.
        channel: Slack channel ID. If None, resolved from env[channel_env_name].
        token: Slack OAuth bot token. If None, resolved from env[token_env_name].
        token_env_name: Env var to read token from (default SLACK_POLARIS_BOT_OAUTH_TOKEN).
        channel_env_name: Env var to read default channel from.
        env: Env mapping. If None, calls load_env().
        http_post: Optional injected POSTer (for tests). Defaults to urllib.
        mrkdwn: Set Slack mrkdwn flag (default True).

    Returns:
        (ok, error_message). On success: (True, ""). On missing creds:
        (False, "missing credentials: ..."). On API failure: (False, "...").
    """
    if env is None:
        env = load_env()
    if not token:
        token = env.get(token_env_name)
    if not channel:
        channel = env.get(channel_env_name)

    if not token:
        return False, f"missing credentials: token (env {token_env_name})"
    if not channel:
        return False, f"missing credentials: channel (env {channel_env_name})"

    payload = {
        "channel": channel,
        "text": message,
        "mrkdwn": bool(mrkdwn),
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    poster = http_post or _http_post
    return poster(SLACK_API_POST_MESSAGE, headers, data)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Post a message to Slack via Polaris bot (or any OAuth token).",
    )
    parser.add_argument(
        "--message",
        required=True,
        help="Slack message body. Supports mrkdwn unless --no-mrkdwn.",
    )
    parser.add_argument(
        "--channel",
        default=None,
        help=f"Channel ID. If omitted, falls back to env[{DEFAULT_CHANNEL_ENV}].",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="OAuth token. If omitted, falls back to env var named by --token-env.",
    )
    parser.add_argument(
        "--token-env",
        default=DEFAULT_TOKEN_ENV,
        help=f"Env var to read OAuth token from (default {DEFAULT_TOKEN_ENV}).",
    )
    parser.add_argument(
        "--channel-env",
        default=DEFAULT_CHANNEL_ENV,
        help=f"Env var to read default channel from (default {DEFAULT_CHANNEL_ENV}).",
    )
    parser.add_argument(
        "--no-mrkdwn",
        action="store_true",
        help="Disable Slack mrkdwn formatting.",
    )
    parser.add_argument(
        "--skip-slack",
        action="store_true",
        help="Dry run: log the intended message + channel, do not call Slack.",
    )
    parser.add_argument(
        "--require-creds",
        action="store_true",
        help="Exit non-zero if credentials are missing (default: exit 0 with warning).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success/info output; only print on error.",
    )
    args = parser.parse_args(argv)

    env = load_env()

    if args.skip_slack:
        # Dry run -- still resolve channel/token for visibility, but do not POST.
        channel = args.channel or env.get(args.channel_env, "(unset)")
        token_present = bool(args.token or env.get(args.token_env))
        if not args.quiet:
            print(f"[notify-slack] DRY RUN -- channel={channel}, token_present={token_present}")
            print(f"[notify-slack] message preview ({len(args.message)} chars):")
            preview = args.message if len(args.message) <= 300 else args.message[:300] + "..."
            for line in preview.splitlines() or [preview]:
                print(f"  {line}")
        return 0

    ok, err = send_slack(
        message=args.message,
        channel=args.channel,
        token=args.token,
        token_env_name=args.token_env,
        channel_env_name=args.channel_env,
        env=env,
        mrkdwn=not args.no_mrkdwn,
    )

    if ok:
        if not args.quiet:
            channel_used = args.channel or env.get(args.channel_env, "")
            print(f"[notify-slack] OK -- posted to {channel_used}")
        return 0

    if "missing credentials" in err and not args.require_creds:
        # Soft-fail: warn but exit 0 so callers can keep running.
        print(f"[notify-slack] WARNING: {err}", file=sys.stderr)
        return 0

    print(f"[notify-slack] FAILED: {err}", file=sys.stderr)
    if "missing credentials" in err:
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
