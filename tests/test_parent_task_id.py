"""Tests for F3 -- parent_task_id field across close-inbox-item.py,
work-request.py, and inbox-json-validate.py.

Source: wr-skillhub-2026-05-08-001 (F3 of AIOS Coordination Fix Strategic Build).

Three surfaces under test:
  1. close-inbox-item.py: accepts --parent-task-id, persists on JSON top-level
     and inside resolution; rejects invalid UUID format.
  2. work-request.py: accepts --parent-task-id, persists in created WR JSON;
     rejects invalid UUID format.
  3. inbox-json-validate.py PreToolUse hook: validates parent_task_id is a
     valid UUID string when present; missing field still passes.
"""

import json
import subprocess
import sys
from pathlib import Path


CLOSE_SCRIPT = Path.home() / ".claude" / "scripts" / "close-inbox-item.py"
WR_SCRIPT = Path.home() / ".claude" / "scripts" / "work-request.py"
VALIDATE_HOOK = Path.home() / ".claude" / "hooks" / "inbox-json-validate.py"

VALID_UUID = "550e8400-e29b-41d4-a716-446655440000"
ANOTHER_UUID = "11111111-2222-3333-4444-555555555555"
INVALID_UUIDS = ["not-a-uuid", "xxxx", "550e8400-e29b-41d4-a716", "", "550e8400e29b41d4a716446655440000"]


# ---------------------------------------------------------------------------
# close-inbox-item.py fixtures
# ---------------------------------------------------------------------------

def _make_inbox_item(tmp_path, item_id="wr-skillhub-2026-05-08-test", status="pending", extras=None):
    """Create a minimal valid inbox item JSON."""
    inbox = tmp_path / "inbox"
    inbox.mkdir(exist_ok=True)
    item_path = inbox / f"{item_id}.json"
    item = {
        "id": item_id,
        "id_format_version": 2,
        "source_workspace": "skill-management-hub",
        "routed_from": "skill-management-hub",
        "routed_to": "skill-management-hub",
        "status": status,
        "task_summary": "Test fixture for parent_task_id F3 tests",
        "notify_on_completion": False,
    }
    if extras:
        item.update(extras)
    item_path.write_text(json.dumps(item, indent=2), encoding="utf-8")
    return item_path


def _run_close(item_path, *extra_args):
    cmd = [
        sys.executable,
        str(CLOSE_SCRIPT),
        "--file", str(item_path),
        "--resolved-by", "skill-management-hub",
        "--what-was-done", "Test close in F3 parent_task_id suite -- verified by pytest fixture",
        "--no-supabase",
        "--no-notify", "--no-notify-reason", "test-only",
    ]
    cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True)


# ---------------------------------------------------------------------------
# close-inbox-item.py TESTS
# ---------------------------------------------------------------------------

def test_close_accepts_parent_task_id_and_persists_top_level(tmp_path):
    """--parent-task-id <uuid> persists on closed JSON top-level."""
    item_path = _make_inbox_item(tmp_path)
    result = _run_close(item_path, "--parent-task-id", VALID_UUID)
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    processed = tmp_path / "processed" / item_path.name
    assert processed.exists()
    closed = json.loads(processed.read_text(encoding="utf-8"))
    assert closed.get("parent_task_id") == VALID_UUID, (
        f"expected parent_task_id at top level, got: {closed.get('parent_task_id')!r}"
    )


def test_close_persists_parent_task_id_inside_resolution(tmp_path):
    """When --parent-task-id is set, resolution.parent_task_id is also recorded
    so the audit trail in resolution carries the linkage."""
    item_path = _make_inbox_item(tmp_path)
    result = _run_close(item_path, "--parent-task-id", VALID_UUID)
    assert result.returncode == 0, f"stderr={result.stderr!r}"
    closed = json.loads((tmp_path / "processed" / item_path.name).read_text(encoding="utf-8"))
    resolution = closed.get("resolution", {})
    assert resolution.get("parent_task_id") == VALID_UUID, (
        f"expected resolution.parent_task_id, got: {resolution.get('parent_task_id')!r}"
    )


def test_close_preserves_existing_top_level_parent_task_id(tmp_path):
    """If the inbox JSON already had parent_task_id (set at filing time by
    work-request.py), close should preserve it AND not require the CLI flag
    to be re-passed. The CLI flag, when provided, overrides; absent, the
    existing value is used."""
    item_path = _make_inbox_item(tmp_path, extras={"parent_task_id": ANOTHER_UUID})
    result = _run_close(item_path)  # no --parent-task-id flag
    assert result.returncode == 0, f"stderr={result.stderr!r}"
    closed = json.loads((tmp_path / "processed" / item_path.name).read_text(encoding="utf-8"))
    assert closed.get("parent_task_id") == ANOTHER_UUID
    assert closed.get("resolution", {}).get("parent_task_id") == ANOTHER_UUID


def test_close_cli_flag_overrides_existing_parent_task_id(tmp_path):
    """If both the JSON and the CLI flag specify parent_task_id, CLI wins."""
    item_path = _make_inbox_item(tmp_path, extras={"parent_task_id": ANOTHER_UUID})
    result = _run_close(item_path, "--parent-task-id", VALID_UUID)
    assert result.returncode == 0
    closed = json.loads((tmp_path / "processed" / item_path.name).read_text(encoding="utf-8"))
    assert closed.get("parent_task_id") == VALID_UUID


def test_close_rejects_invalid_uuid(tmp_path):
    """--parent-task-id with non-UUID string causes non-zero exit + error."""
    for bad in INVALID_UUIDS:
        if not bad:
            continue  # argparse rejects empty separately
        item_path = _make_inbox_item(tmp_path, item_id=f"wr-skillhub-2026-05-08-test-{abs(hash(bad)) % 1000:03d}")
        result = _run_close(item_path, "--parent-task-id", bad)
        assert result.returncode != 0, (
            f"expected failure for invalid UUID {bad!r}, got returncode=0; "
            f"stderr={result.stderr!r}"
        )
        assert "uuid" in result.stderr.lower() or "parent_task_id" in result.stderr.lower(), (
            f"expected error mentioning UUID/parent_task_id, got stderr={result.stderr!r}"
        )
        # File should still be in inbox (close failed before move)
        assert item_path.exists(), "source should remain in inbox/ on validation failure"


def test_close_backward_compat_no_flag(tmp_path):
    """Closing without --parent-task-id still works (backward compat)."""
    item_path = _make_inbox_item(tmp_path)
    result = _run_close(item_path)
    assert result.returncode == 0, f"stderr={result.stderr!r}"
    closed = json.loads((tmp_path / "processed" / item_path.name).read_text(encoding="utf-8"))
    # parent_task_id absent or None -- both acceptable
    assert closed.get("parent_task_id") in (None, "") or "parent_task_id" not in closed


# ---------------------------------------------------------------------------
# work-request.py TESTS
# ---------------------------------------------------------------------------

def _run_wr(tmp_path, *extra_args):
    inbox = tmp_path / "wr-inbox"
    inbox.mkdir(exist_ok=True)
    cmd = [
        sys.executable,
        str(WR_SCRIPT),
        "--type", "TASK",
        "--severity", "warning",
        "--workspace", "skill-management-hub",
        "--workspace-path", str(tmp_path),
        "--task", "F3 parent_task_id test filing",
        "--category", "infrastructure",
        "--needed", "Test the --parent-task-id flag",
        "--gap", "no test coverage for parent_task_id field",
        "--impact", "Without this test, parent_task_id field could regress unnoticed in future edits to the script",
        "--fix-type", "test",
        "--fix-desc", "Test fixture for parent_task_id field validation in work-request.py",
        "--fix-components", "test_parent_task_id.py",
        "--no-supabase",
        "--output-dir", str(inbox),
        "--skip-dedup",
    ]
    cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True), inbox


def test_wr_accepts_parent_task_id_and_persists(tmp_path):
    """work-request.py --parent-task-id <uuid> persists on filed WR JSON."""
    result, inbox = _run_wr(tmp_path, "--parent-task-id", VALID_UUID)
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    files = list(inbox.glob("*.json"))
    assert len(files) == 1, f"expected 1 WR file, got {len(files)}: {files}"
    wr = json.loads(files[0].read_text(encoding="utf-8"))
    assert wr.get("parent_task_id") == VALID_UUID, (
        f"expected parent_task_id={VALID_UUID!r}, got {wr.get('parent_task_id')!r}"
    )


def test_wr_rejects_invalid_uuid(tmp_path):
    """work-request.py rejects --parent-task-id values that aren't valid UUIDs."""
    for bad in ["not-a-uuid", "xxxx", "550e8400-e29b"]:
        result, inbox = _run_wr(tmp_path, "--parent-task-id", bad)
        assert result.returncode != 0, (
            f"expected failure for invalid UUID {bad!r}, got returncode=0; "
            f"stderr={result.stderr!r}"
        )
        assert "uuid" in result.stderr.lower() or "parent_task_id" in result.stderr.lower(), (
            f"expected error mentioning UUID/parent_task_id, got stderr={result.stderr!r}"
        )


def test_wr_backward_compat_no_flag(tmp_path):
    """Filing without --parent-task-id still works (backward compat)."""
    result, inbox = _run_wr(tmp_path)
    assert result.returncode == 0, f"stderr={result.stderr!r}"
    files = list(inbox.glob("*.json"))
    assert len(files) == 1
    wr = json.loads(files[0].read_text(encoding="utf-8"))
    # parent_task_id absent
    assert "parent_task_id" not in wr or wr["parent_task_id"] in (None, "")


# ---------------------------------------------------------------------------
# inbox-json-validate.py TESTS
# ---------------------------------------------------------------------------

def _run_validator(file_path, content):
    """Invoke the hook with a Write tool_input shaped event."""
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(file_path), "content": content},
        "transcript_path": "",
    }
    result = subprocess.run(
        [sys.executable, str(VALIDATE_HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    return result


def _inbox_path_in(tmp_path):
    """Build a path that matches the hook's INBOX_PATH_RE pattern."""
    p = tmp_path / ".work-requests" / "inbox" / "wr-skillhub-2026-05-08-validate.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def test_validator_accepts_valid_uuid_parent_task_id(tmp_path):
    """parent_task_id with valid UUID format passes validation."""
    target = _inbox_path_in(tmp_path)
    payload_json = json.dumps({
        "id": "wr-skillhub-2026-05-08-001",
        "id_format_version": 2,
        "source_workspace": "skill-management-hub",
        "status": "new",
        "parent_task_id": VALID_UUID,
    })
    result = _run_validator(target, payload_json)
    assert result.returncode == 0
    # Should not emit a deny decision
    if result.stdout.strip():
        out = json.loads(result.stdout)
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision", "")
        assert decision != "deny", f"unexpected deny: {result.stdout!r}"


def test_validator_rejects_invalid_uuid_parent_task_id(tmp_path):
    """parent_task_id with invalid UUID format triggers deny."""
    target = _inbox_path_in(tmp_path)
    payload_json = json.dumps({
        "id": "wr-skillhub-2026-05-08-001",
        "id_format_version": 2,
        "source_workspace": "skill-management-hub",
        "status": "new",
        "parent_task_id": "not-a-valid-uuid-string",
    })
    result = _run_validator(target, payload_json)
    # Hook emits deny decision via stdout JSON
    assert result.stdout.strip(), f"expected stdout deny output, got empty; stderr={result.stderr!r}"
    out = json.loads(result.stdout)
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision", "")
    assert decision == "deny", f"expected deny, got {decision!r}; full output: {result.stdout!r}"
    reason = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    assert "uuid" in reason.lower() or "parent_task_id" in reason.lower(), (
        f"expected reason to mention UUID/parent_task_id, got {reason!r}"
    )


def test_validator_omitted_parent_task_id_passes(tmp_path):
    """Missing parent_task_id is fine -- field is optional."""
    target = _inbox_path_in(tmp_path)
    payload_json = json.dumps({
        "id": "wr-skillhub-2026-05-08-001",
        "id_format_version": 2,
        "source_workspace": "skill-management-hub",
        "status": "new",
    })
    result = _run_validator(target, payload_json)
    assert result.returncode == 0
    if result.stdout.strip():
        out = json.loads(result.stdout)
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision", "")
        assert decision != "deny"
