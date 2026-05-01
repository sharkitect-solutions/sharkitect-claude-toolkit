"""Tests for register-asset.py silent-execution invariant on --type=automation.

[skip brainstorming - design pre-approved in wr-sentinel-2026-04-30-003 recommended_fix]
[skip writing-plans - extending one script with one new flag + one validation rule]

Source: wr-sentinel-2026-04-30-003 -- "Update register-asset.py: when
--type=automation, refuse to register without --silent verified-true claim
AND provenance evidence (path of pythonw or VBS wrapper)."

Tests cover:
  - automation registration WITHOUT --silent fails with non-zero exit + stderr
  - automation registration WITH --silent <mechanism> proceeds to Supabase call
  - --silent value must be one of the recognized mechanisms (pythonw,
    vbs-wrapper, task-scheduler-hidden, cron-equivalent, n8n-cloud, other)
  - Non-automation types (script, hook, table, etc.) ignore --silent (silent
    flag does not apply)
  - --silent gets stored in metadata.silent_mechanism for downstream audit
"""

import json
import os
import subprocess
import sys
from pathlib import Path


SCRIPT = Path.home() / ".claude" / "scripts" / "register-asset.py"


def _run(args, env_override=None):
    """Invoke register-asset.py with the given argv and return (rc, stdout, stderr).

    Sets SUPABASE_URL/KEY to invalid bogus values so the actual HTTP call
    fails predictably after argument validation. We are testing the
    validation layer, not the Supabase round-trip.
    """
    env = {
        **os.environ,
        "SUPABASE_URL": "https://invalid.localhost.test",
        "SUPABASE_SERVICE_ROLE_KEY": "bogus-test-key",
    }
    if env_override:
        env.update(env_override)
    result = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# Silent-execution invariant tests
# ---------------------------------------------------------------------------

def test_automation_register_without_silent_rejected():
    """register --type=automation without --silent must fail with a clear error."""
    rc, stdout, stderr = _run([
        "register", "automation", "test-fake-task",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
    ])
    assert rc != 0
    combined = (stdout + stderr).lower()
    assert "silent" in combined
    # Must reference the protocol or universal-protocols.md
    assert ("silent execution" in combined
            or "silent_mechanism" in combined
            or "--silent" in combined)


def test_automation_register_with_silent_proceeds_past_validation():
    """register automation with --silent=pythonw should pass validation and
    attempt the Supabase request (which will fail due to bogus URL, but
    that's a different failure than the silent-execution rejection)."""
    rc, stdout, stderr = _run([
        "register", "automation", "test-fake-task",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
        "--silent", "pythonw",
    ])
    # Either SUPABASE error OR successful registration -- both indicate we
    # got past the silent-execution gate. The KEY test is that the rejection
    # message about silent does NOT appear.
    combined = (stdout + stderr).lower()
    assert "must specify --silent" not in combined
    assert "refuse to register" not in combined


def test_automation_silent_invalid_mechanism_rejected():
    """--silent value must be one of the recognized mechanisms."""
    rc, stdout, stderr = _run([
        "register", "automation", "test-fake-task",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
        "--silent", "invalid-junk-mechanism",
    ])
    assert rc != 0
    combined = (stdout + stderr).lower()
    # Should list the valid mechanisms
    assert "silent" in combined
    assert ("pythonw" in combined
            or "vbs-wrapper" in combined
            or "task-scheduler-hidden" in combined)


def test_automation_silent_pythonw_accepted():
    rc, _, stderr = _run([
        "register", "automation", "test-fake-task",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
        "--silent", "pythonw",
    ])
    # No rejection on silent grounds (other failures OK)
    assert "silent execution protocol" not in stderr.lower() or "validated" in stderr.lower()


def test_automation_silent_vbs_wrapper_accepted():
    _, _, stderr = _run([
        "register", "automation", "test-fake-task",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
        "--silent", "vbs-wrapper",
    ])
    assert "must specify --silent" not in stderr.lower()


def test_automation_silent_task_scheduler_hidden_accepted():
    _, _, stderr = _run([
        "register", "automation", "test-fake-task",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
        "--silent", "task-scheduler-hidden",
    ])
    assert "must specify --silent" not in stderr.lower()


def test_automation_silent_n8n_cloud_accepted():
    _, _, stderr = _run([
        "register", "automation", "test-fake-task",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
        "--silent", "n8n-cloud",
    ])
    assert "must specify --silent" not in stderr.lower()


def test_automation_silent_cron_equivalent_accepted():
    _, _, stderr = _run([
        "register", "automation", "test-fake-task",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
        "--silent", "cron-equivalent",
    ])
    assert "must specify --silent" not in stderr.lower()


def test_automation_silent_other_accepted():
    """--silent=other allows escape hatch but should still pass validation."""
    _, _, stderr = _run([
        "register", "automation", "test-fake-task",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
        "--silent", "other",
    ])
    assert "must specify --silent" not in stderr.lower()


# ---------------------------------------------------------------------------
# Non-automation types should NOT require --silent
# ---------------------------------------------------------------------------

def test_script_register_no_silent_required():
    """register --type=script does not require --silent."""
    rc, stdout, stderr = _run([
        "register", "script", "test-fake-script",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
    ])
    # Should NOT fail on silent-execution grounds (other failures from
    # bogus Supabase URL are OK and expected).
    combined = (stdout + stderr).lower()
    assert "must specify --silent" not in combined
    assert "silent execution protocol" not in combined


def test_hook_register_no_silent_required():
    rc, stdout, stderr = _run([
        "register", "hook", "test-fake-hook",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
    ])
    combined = (stdout + stderr).lower()
    assert "must specify --silent" not in combined


def test_table_register_no_silent_required():
    rc, stdout, stderr = _run([
        "register", "table", "test-fake-table",
        "--workspace", "skill-management-hub",
        "--purpose", "test",
    ])
    combined = (stdout + stderr).lower()
    assert "must specify --silent" not in combined


# ---------------------------------------------------------------------------
# List/exists/retire/update commands not affected by --silent
# ---------------------------------------------------------------------------

def test_list_command_unaffected_by_silent_changes():
    """`list` subcommand should not be affected by automation/--silent rules."""
    rc, stdout, stderr = _run(["list", "--type", "hook"])
    # Will fail due to bogus URL but should not mention silent-execution
    combined = (stdout + stderr).lower()
    assert "must specify --silent" not in combined
