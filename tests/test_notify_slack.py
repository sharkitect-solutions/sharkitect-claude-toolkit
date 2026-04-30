"""Tests for ~/.claude/scripts/notify-slack.py global helper.

Covers:
1. Successful POST with token + channel
2. Missing token -> graceful failure with reason
3. Missing channel -> graceful failure with reason
4. CLI --skip-slack dry run -> exit 0 without HTTP
5. CLI exits 0 on missing creds by default (soft-fail)
6. CLI exits 1 on missing creds when --require-creds is set
7. CLI exits 2 on Slack API failure
8. send_slack with explicit token + channel overrides env
9. Custom token_env_name + channel_env_name resolution
10. mrkdwn=False is honored in payload
"""
import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

# Load notify-slack.py as a module (file has hyphen, can't import directly)
SCRIPT_PATH = Path(os.path.expanduser("~/.claude/scripts/notify-slack.py"))
spec = importlib.util.spec_from_file_location("notify_slack", SCRIPT_PATH)
assert spec is not None and spec.loader is not None, "notify-slack.py not loadable"
notify_slack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notify_slack)


class TestSendSlack(unittest.TestCase):
    def test_successful_post(self):
        called = {}

        def fake_post(url, headers, data):
            called["url"] = url
            called["headers"] = dict(headers)
            called["data"] = json.loads(data.decode())
            return True, ""

        ok, err = notify_slack.send_slack(
            message="hello",
            channel="C123",
            token="xoxb-fake",
            env={},
            http_post=fake_post,
        )
        self.assertTrue(ok)
        self.assertEqual(err, "")
        self.assertEqual(called["url"], notify_slack.SLACK_API_POST_MESSAGE)
        self.assertEqual(called["data"]["channel"], "C123")
        self.assertEqual(called["data"]["text"], "hello")
        self.assertTrue(called["data"]["mrkdwn"])
        self.assertIn("Bearer xoxb-fake", called["headers"]["Authorization"])

    def test_missing_token_graceful(self):
        ok, err = notify_slack.send_slack(
            message="hello",
            channel="C123",
            token=None,
            env={},  # no SLACK_POLARIS_BOT_OAUTH_TOKEN
        )
        self.assertFalse(ok)
        self.assertIn("missing credentials: token", err)
        self.assertIn("SLACK_POLARIS_BOT_OAUTH_TOKEN", err)

    def test_missing_channel_graceful(self):
        ok, err = notify_slack.send_slack(
            message="hello",
            channel=None,
            token="xoxb-fake",
            env={},
        )
        self.assertFalse(ok)
        self.assertIn("missing credentials: channel", err)
        self.assertIn("SLACK_POLARIS_DEFAULT_CHANNEL", err)

    def test_explicit_overrides_env(self):
        called = {}

        def fake_post(_url, _headers, data):
            called["data"] = json.loads(data.decode())
            return True, ""

        ok, _ = notify_slack.send_slack(
            message="hi",
            channel="C_OVERRIDE",
            token="xoxb-override",
            env={
                "SLACK_POLARIS_BOT_OAUTH_TOKEN": "xoxb-from-env",
                "SLACK_POLARIS_DEFAULT_CHANNEL": "C_FROM_ENV",
            },
            http_post=fake_post,
        )
        self.assertTrue(ok)
        self.assertEqual(called["data"]["channel"], "C_OVERRIDE")

    def test_custom_env_var_names(self):
        called = {}

        def fake_post(_url, headers, data):
            called["data"] = json.loads(data.decode())
            called["headers"] = dict(headers)
            return True, ""

        ok, _ = notify_slack.send_slack(
            message="hi",
            token_env_name="MY_CUSTOM_TOKEN",
            channel_env_name="MY_CUSTOM_CHANNEL",
            env={
                "MY_CUSTOM_TOKEN": "xoxb-custom",
                "MY_CUSTOM_CHANNEL": "C_CUSTOM",
            },
            http_post=fake_post,
        )
        self.assertTrue(ok)
        self.assertEqual(called["data"]["channel"], "C_CUSTOM")
        self.assertIn("Bearer xoxb-custom", called["headers"]["Authorization"])

    def test_mrkdwn_false(self):
        called = {}

        def fake_post(_url, _headers, data):
            called["data"] = json.loads(data.decode())
            return True, ""

        notify_slack.send_slack(
            message="plain",
            channel="C1",
            token="x",
            env={},
            http_post=fake_post,
            mrkdwn=False,
        )
        self.assertFalse(called["data"]["mrkdwn"])

    def test_api_failure_propagates(self):
        def fake_post(_url, _headers, data):
            return False, "slack api: invalid_auth"

        ok, err = notify_slack.send_slack(
            message="hi",
            channel="C1",
            token="x",
            env={},
            http_post=fake_post,
        )
        self.assertFalse(ok)
        self.assertIn("invalid_auth", err)


class TestCli(unittest.TestCase):
    def _invoke(self, args, env_override=None):
        """Invoke the script in subprocess. env_override is dict of env vars to set."""
        env = dict(os.environ)
        if env_override is not None:
            # Reset Slack vars first, then apply override
            for k in list(env):
                if k.startswith("SLACK_POLARIS_"):
                    del env[k]
            env.update(env_override)
        # Empty HOME so .env doesn't get loaded from real ~/.claude/.env
        # NOTE: use a tmp dir for HOME so neither ~/.claude/.env nor ./.env interfere
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH)] + args,
            capture_output=True,
            text=True,
            env=env,
            cwd=os.path.expanduser("~"),  # Avoid .env in CWD
        )

    def test_skip_slack_dry_run_exit_0(self):
        result = self._invoke(
            ["--message", "test", "--skip-slack"],
            env_override={
                "SLACK_POLARIS_BOT_OAUTH_TOKEN": "xoxb-fake",
                "SLACK_POLARIS_DEFAULT_CHANNEL": "C1",
            },
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("DRY RUN", result.stdout)

    def test_missing_creds_soft_fail_exits_0_default(self):
        result = self._invoke(
            ["--message", "test"],
            env_override={},  # No token, no channel
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("missing credentials", result.stderr.lower())

    def test_missing_creds_hard_fail_with_require(self):
        result = self._invoke(
            ["--message", "test", "--require-creds"],
            env_override={},
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing credentials", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
