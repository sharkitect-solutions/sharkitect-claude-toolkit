"""Tests for ONE filing tool consolidation (wr-sentinel-2026-04-30-009).

Three changes are under test:

1. work-request.py: --item-type flag accepting work_request | routed_task |
   completion_notification | fyi, plus --target-workspace. Resolves the
   correct destination inbox per item_type + target (HQ/Sentinel ->
   .routed-tasks/inbox/, Skill Hub -> .work-requests/inbox/ -- Skill Hub
   has no .routed-tasks/ per protocol). Logs cross_workspace_requests row
   with item_type matching --item-type for ALL item_types.

2. close-inbox-item.py: UPSERT pattern -- if cross_workspace_requests row
   missing for the item_id, INSERT it from local JSON metadata before
   applying the close PATCH. Solves the "232-row drift" problem where
   PATCHing a non-existent row was a silent no-op.

3. close-inbox-item.py: substitute the literal <YYYY-MM-DD> token in
   notification_filename_hint with today's date. Reject unsubstituted
   placeholders after substitution (clear error referencing the
   filename_hint contract). Pre-validate item_type against the 5-value
   Supabase CHECK list (work_request | routed_task | lifecycle_review |
   completion_notification | fyi).

Source: WR wr-sentinel-2026-04-30-009 (Sentinel; Phase 1 of Luminous
Foundation Bridge). Schema CHECK widened from 3 to 5 values via
migration widen_cross_workspace_requests_item_type 2026-04-30.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WR_SCRIPT = Path(os.path.expanduser("~/.claude/scripts/work-request.py"))
CLOSE_SCRIPT = Path(os.path.expanduser("~/.claude/scripts/close-inbox-item.py"))

GOOD_IMPACT = (
    "Would have shortened fix by 30 minutes and raised confidence from "
    "low to high; affected the daily CEO brief generation."
)


def _load_close_module():
    """Dynamic import of close-inbox-item.py (filename has hyphens)."""
    spec = importlib.util.spec_from_file_location("cii_test", str(CLOSE_SCRIPT))
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _load_wr_module():
    """Dynamic import of work-request.py (filename has hyphens)."""
    spec = importlib.util.spec_from_file_location("wr_test", str(WR_SCRIPT))
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run_wr_subprocess(output_dir, **kw):
    """Invoke work-request.py via subprocess.

    Defaults pass impact + dedup gates; override via kw.
    --no-supabase is set so tests don't hit live Supabase.
    """
    cmd = [
        sys.executable, str(WR_SCRIPT),
        "--type", kw.get("type", "TASK"),
        "--severity", kw.get("severity", "info"),
        "--workspace", kw.get("workspace", "skill-management-hub"),
        "--workspace-path", str(output_dir),
        "--task", kw.get("task", "Filing-tool consolidation regression task"),
        "--category", kw.get("category", "operations"),
        "--needed", kw.get("needed", "test-needed"),
        "--gap", kw.get("gap", "test-gap"),
        "--impact", kw.get("impact", GOOD_IMPACT),
        "--fix-type", kw.get("fix_type", "task"),
        "--fix-desc", kw.get("fix_desc", "test-fix-desc"),
        "--no-supabase",
        "--output-dir", str(output_dir),
        "--skip-dedup",
    ]
    if "item_type" in kw:
        cmd.extend(["--item-type", kw["item_type"]])
    if "target_workspace" in kw:
        cmd.extend(["--target-workspace", kw["target_workspace"]])
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def _read_only_json_in(directory):
    """Return the parsed JSON of the single .json file in directory.

    Asserts there is exactly one. Used after _run_wr_subprocess.
    """
    files = sorted(Path(directory).glob("*.json"))
    assert len(files) == 1, (
        f"expected 1 JSON in {directory}, got {len(files)}: "
        f"{[f.name for f in files]}"
    )
    return files[0], json.loads(files[0].read_text(encoding="utf-8"))


# =============================================================================
# work-request.py: --item-type + --target-workspace tests
# =============================================================================

def test_default_item_type_is_work_request_back_compat(tmp_path):
    """Omitting --item-type defaults to work_request; existing behavior preserved.

    Regression guard: every WR filed before this change was a work_request
    by default. Adding the flag must not break any existing caller.
    """
    inbox = tmp_path / "inbox"
    result = _run_wr_subprocess(inbox)
    assert result.returncode == 0, (
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    _, data = _read_only_json_in(inbox)
    assert data.get("item_type") == "work_request", (
        "default --item-type must be 'work_request'; got "
        f"{data.get('item_type')!r}"
    )
    # Filename still uses workspace prefix for collision avoidance
    assert data["id"].startswith("wr-skillhub-"), data["id"]


def test_invalid_item_type_rejected(tmp_path):
    """--item-type with unknown value exits non-zero with clear error.

    Five valid values: work_request, routed_task, completion_notification,
    fyi, lifecycle_review (lifecycle is out of scope but the CHECK
    accepts it; argparse choices should reject the typo case).
    """
    inbox = tmp_path / "inbox"
    result = _run_wr_subprocess(inbox, item_type="bogus_value")
    assert result.returncode != 0
    err = (result.stderr + result.stdout).lower()
    assert "bogus_value" in err or "invalid choice" in err or "item-type" in err, (
        f"expected error to mention bogus_value or item-type; got "
        f"stderr={result.stderr!r}"
    )


def test_item_type_routed_task_writes_kind_and_routed_to(tmp_path):
    """--item-type routed_task records routed_to + item_type=routed_task.

    Routed-task semantic differs from work_request: routed_to identifies
    the target workspace; assigned_to in Supabase mirrors it.
    """
    inbox = tmp_path / "inbox"
    result = _run_wr_subprocess(
        inbox,
        item_type="routed_task",
        target_workspace="sentinel",
    )
    assert result.returncode == 0, (
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    _, data = _read_only_json_in(inbox)
    assert data.get("item_type") == "routed_task"
    assert data.get("routed_to") == "sentinel"
    # routed_from mirrors source_workspace for routed-tasks
    assert data.get("routed_from") == data.get("source_workspace") == "skill-management-hub"


def test_item_type_completion_notification_sets_kind(tmp_path):
    """--item-type completion_notification sets kind=completion_notification.

    Anti-ping-pong invariant: completion_notification items must have
    notify_on_completion=False so the close path doesn't generate a
    follow-up notification.
    """
    inbox = tmp_path / "inbox"
    result = _run_wr_subprocess(
        inbox,
        item_type="completion_notification",
        target_workspace="workforce-hq",
    )
    assert result.returncode == 0, (
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    _, data = _read_only_json_in(inbox)
    assert data.get("item_type") == "completion_notification"
    assert data.get("kind") == "completion_notification", (
        "completion_notification item_type must inject kind field"
    )
    assert data.get("notify_on_completion") is False, (
        "completion_notification must NOT request notification (anti-ping-pong)"
    )


def test_item_type_fyi_sets_kind_and_notify_off(tmp_path):
    """--item-type fyi sets kind=fyi and notify_on_completion=False.

    fyi is fire-and-forget by definition; no acknowledgement expected.
    """
    inbox = tmp_path / "inbox"
    result = _run_wr_subprocess(
        inbox,
        item_type="fyi",
        target_workspace="sentinel",
    )
    assert result.returncode == 0, (
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    _, data = _read_only_json_in(inbox)
    assert data.get("item_type") == "fyi"
    assert data.get("kind") == "fyi"
    assert data.get("notify_on_completion") is False


def test_inbox_resolver_routed_task_to_hq_uses_routed_tasks_dir(tmp_path):
    """Resolver function: HQ + routed_task -> <hq>/.routed-tasks/inbox/.

    Tests the path-resolution function directly (no subprocess).
    """
    wr = _load_wr_module()
    # Standalone resolver -- function name to be added by implementation
    assert hasattr(wr, "_resolve_target_inbox"), (
        "work-request.py must export _resolve_target_inbox(item_type, target_workspace)"
    )
    p = wr._resolve_target_inbox("routed_task", "workforce-hq")
    assert p is not None, "HQ routed_task should resolve to a path"
    p_str = str(p).replace("\\", "/").lower()
    assert "/.routed-tasks/inbox" in p_str, (
        f"HQ routed_task should target .routed-tasks/inbox; got {p_str}"
    )


def test_inbox_resolver_routed_task_to_skill_hub_uses_work_requests_dir(tmp_path):
    """Resolver function: Skill Hub + routed_task -> <skillhub>/.work-requests/inbox/.

    Skill Hub has no .routed-tasks/ -- inbound work goes through
    .work-requests/inbox/ per protocol.
    """
    wr = _load_wr_module()
    p = wr._resolve_target_inbox("routed_task", "skill-management-hub")
    assert p is not None, "Skill Hub routed_task should resolve to a path"
    p_str = str(p).replace("\\", "/").lower()
    assert "/.work-requests/inbox" in p_str, (
        f"Skill Hub routed_task should target .work-requests/inbox; got {p_str}"
    )


def test_routed_task_log_to_supabase_passes_routed_task_item_type(tmp_path, monkeypatch):
    """log_to_supabase receives item_type='routed_task' for routed-task filings.

    Regression guard: filing a routed-task must record item_type=routed_task
    on the cross_workspace_requests row. Today, all rows go in as
    item_type='work_request' regardless -- that's the bug this WR fixes.
    """
    wr = _load_wr_module()

    captured = []

    def fake_log(report, item_type="work_request"):
        captured.append({"report_id": report.get("id"), "item_type": item_type})
        return True

    monkeypatch.setattr(wr, "log_to_supabase", fake_log)

    # Build args that traverse main() with routed_task item_type
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (tmp_path / "processed").mkdir()
    argv = [
        "work-request.py",
        "--type", "TASK",
        "--severity", "info",
        "--workspace", "skill-management-hub",
        "--workspace-path", str(tmp_path),
        "--task", "Routed-task Supabase logging test",
        "--category", "operations",
        "--needed", "test-needed",
        "--gap", "test-gap",
        "--impact", GOOD_IMPACT,
        "--fix-desc", "test-fix-desc",
        "--output-dir", str(inbox),
        "--skip-dedup",
        "--item-type", "routed_task",
        "--target-workspace", "sentinel",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    rc = wr.main()
    assert rc == 0, "wr.main() should succeed with routed_task item_type"
    assert len(captured) == 1, (
        f"log_to_supabase should be called once; got {len(captured)} calls"
    )
    assert captured[0]["item_type"] == "routed_task", (
        "log_to_supabase must receive item_type='routed_task' for routed-task "
        f"filings; got {captured[0]['item_type']!r}"
    )


# =============================================================================
# close-inbox-item.py: UPSERT (insert when missing) tests
# =============================================================================

def _make_inbox_item(tmp_path, item_id, kind=None, source_ws="skill-management-hub"):
    """Create a minimal valid inbox item JSON in tmp_path/inbox/."""
    inbox = tmp_path / "inbox"
    inbox.mkdir(exist_ok=True)
    item_path = inbox / f"{item_id}.json"
    body = {
        "id": item_id,
        "id_format_version": 2,
        "source_workspace": source_ws,
        "routed_from": source_ws,
        "routed_to": source_ws,
        "status": "pending",
        "task_summary": f"Fixture for {item_id}",
        "what_was_needed": "test-needed",
        "task_description": "test task description",
        "severity": "info",
        "priority": "medium",
        "notify_on_completion": False,
    }
    if kind:
        body["kind"] = kind
    item_path.write_text(json.dumps(body, indent=2), encoding="utf-8")
    return item_path


def test_upsert_inserts_when_row_missing(tmp_path, monkeypatch):
    """update_supabase performs INSERT then PATCH when row missing.

    Today: PATCH-only path silently no-ops when row absent (the 232-row drift
    bug). Required behavior: GET first; if empty, POST a new row built from
    local JSON; then PATCH the close fields.
    """
    cii = _load_close_module()

    # Capture HTTP calls
    calls = []

    class FakeResponse:
        def __init__(self, status=200, body=b"[]"):
            self.status = status
            self._body = body
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return self._body

    def fake_urlopen(req, timeout=10):
        calls.append({
            "method": req.get_method(),
            "url": req.full_url,
            "body": (req.data or b"").decode("utf-8") if req.data else "",
        })
        # Simulate row missing: GET returns [], then POST + PATCH succeed
        if req.get_method() == "GET":
            return FakeResponse(200, b"[]")
        return FakeResponse(204, b"")

    monkeypatch.setattr(cii.urllib.request, "urlopen", fake_urlopen)
    def _fake_env(k, hint_path=None):
        if k == "SUPABASE_URL":
            return "http://localhost:65535"
        if k == "SUPABASE_SERVICE_ROLE_KEY":
            return "test_key"
        return None
    monkeypatch.setattr(cii, "_load_env_value", _fake_env)
    # Stop _verify_supabase_close from making its own GET (covered separately)
    monkeypatch.setattr(cii, "_verify_supabase_close",
                        lambda **kw: (True, "stubbed verify"))

    item_id = "wr-skillhub-2026-04-30-upsert-test"
    item_path = _make_inbox_item(tmp_path, item_id)
    result = cii.close_item(
        file_path=str(item_path),
        status="completed",
        resolved_by="skill-management-hub",
        what_was_done="Test close to exercise UPSERT INSERT path",
        update_supabase_row=True,
    )
    assert result["ok"]
    methods = [c["method"] for c in calls]
    # Required sequence: GET (existence check) -> POST (insert) -> PATCH (close)
    assert "GET" in methods, (
        f"UPSERT must GET first to check existence; got methods={methods}"
    )
    assert "POST" in methods, (
        f"UPSERT must POST to INSERT row when missing; got methods={methods}"
    )
    # Verify INSERT body contains required fields
    post_calls = [c for c in calls if c["method"] == "POST"]
    assert len(post_calls) >= 1, "expected at least one POST"
    post_body = json.loads(post_calls[0]["body"])
    assert post_body.get("item_id") == item_id
    assert post_body.get("item_type") == "work_request"
    assert post_body.get("requested_by") == "skill-management-hub"


def test_upsert_patches_only_when_row_exists(tmp_path, monkeypatch):
    """update_supabase skips INSERT when GET returns a row, PATCHes only.

    Backward-compat: existing PATCH path must remain when row is already
    present. The UPSERT only kicks in for missing rows.
    """
    cii = _load_close_module()
    calls = []

    class FakeResponse:
        def __init__(self, status=200, body=b"[]"):
            self.status = status
            self._body = body
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return self._body

    def fake_urlopen(req, timeout=10):
        calls.append({
            "method": req.get_method(),
            "url": req.full_url,
            "body": (req.data or b"").decode("utf-8") if req.data else "",
        })
        if req.get_method() == "GET":
            # Return an existing row
            row = [{"item_id": "wr-skillhub-2026-04-30-existing",
                    "status": "pending"}]
            return FakeResponse(200, json.dumps(row).encode("utf-8"))
        return FakeResponse(204, b"")

    monkeypatch.setattr(cii.urllib.request, "urlopen", fake_urlopen)
    def _fake_env(k, hint_path=None):
        if k == "SUPABASE_URL":
            return "http://localhost:65535"
        if k == "SUPABASE_SERVICE_ROLE_KEY":
            return "test_key"
        return None
    monkeypatch.setattr(cii, "_load_env_value", _fake_env)
    monkeypatch.setattr(cii, "_verify_supabase_close",
                        lambda **kw: (True, "stubbed verify"))

    item_path = _make_inbox_item(tmp_path, "wr-skillhub-2026-04-30-existing")
    result = cii.close_item(
        file_path=str(item_path),
        status="completed",
        resolved_by="skill-management-hub",
        what_was_done="Test close where Supabase row already exists",
        update_supabase_row=True,
    )
    assert result["ok"]
    methods = [c["method"] for c in calls]
    # POST must NOT happen when row already exists
    assert "POST" not in methods, (
        f"UPSERT must skip POST when row exists; got methods={methods}"
    )
    assert "PATCH" in methods, (
        f"UPSERT must still PATCH close fields when row exists; "
        f"got methods={methods}"
    )


# =============================================================================
# close-inbox-item.py: <YYYY-MM-DD> placeholder substitution tests
# =============================================================================

def test_yyyy_mm_dd_placeholder_substituted_to_today(tmp_path, monkeypatch):
    """Notification filename hint with <YYYY-MM-DD> gets today's date.

    Bug: literal <YYYY-MM-DD> currently lands in notification filenames.
    Fix: substitute before path construction.
    """
    cii = _load_close_module()

    # Build a closing item that triggers a notification (cross-workspace)
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    src_workspace_root = tmp_path / "fake-source"
    notify_dir = src_workspace_root / ".routed-tasks" / "inbox"
    notify_dir.mkdir(parents=True)

    item_id = "wr-sentinel-2026-04-30-placeholder-test"
    body = {
        "id": item_id,
        "id_format_version": 2,
        "source_workspace": "sentinel",
        "routed_from": "sentinel",
        "routed_to": "skill-management-hub",
        "status": "pending",
        "notify_on_completion": True,
        "notify_inbox_path": str(notify_dir),
        "notification_filename_hint":
            f"rt-<YYYY-MM-DD>-{item_id}-completed-by-<completer-workspace>.json",
        "task_summary": "Fixture",
        "task_description": "td",
        "what_was_needed": "n",
        "severity": "info",
        "priority": "medium",
    }
    item_path = inbox / f"{item_id}.json"
    item_path.write_text(json.dumps(body, indent=2), encoding="utf-8")

    monkeypatch.setattr(cii, "update_supabase",
                        lambda **kw: (True, "stubbed OK"))
    monkeypatch.setattr(cii, "_verify_supabase_close",
                        lambda **kw: (True, "stubbed verify"))

    result = cii.close_item(
        file_path=str(item_path),
        status="completed",
        resolved_by="skill-management-hub",
        what_was_done="Test placeholder substitution -- expecting YYYY-MM-DD replaced",
        update_supabase_row=True,
    )
    assert result["ok"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    notif_path = result.get("notification_path")
    assert notif_path, (
        f"notification should be written; got result={result}"
    )
    notif_name = Path(notif_path).name
    assert "<YYYY-MM-DD>" not in notif_name, (
        f"<YYYY-MM-DD> must be substituted; got filename={notif_name}"
    )
    assert today in notif_name, (
        f"today's date {today} must appear in filename; got {notif_name}"
    )


def test_unsubstituted_placeholder_rejected(tmp_path, monkeypatch):
    """Unknown <token> placeholder remaining after substitution -> error.

    Defensive: protects against typos in originator's filename_hint that
    would otherwise produce literal <unknown-thing> in filenames.
    """
    cii = _load_close_module()
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    src_workspace_root = tmp_path / "fake-source"
    notify_dir = src_workspace_root / ".routed-tasks" / "inbox"
    notify_dir.mkdir(parents=True)

    item_id = "wr-sentinel-2026-04-30-bad-placeholder"
    body = {
        "id": item_id,
        "id_format_version": 2,
        "source_workspace": "sentinel",
        "routed_from": "sentinel",
        "routed_to": "skill-management-hub",
        "status": "pending",
        "notify_on_completion": True,
        "notify_inbox_path": str(notify_dir),
        # <unknown-typo> won't match any known substitution token
        "notification_filename_hint":
            f"rt-<YYYY-MM-DD>-{item_id}-<unknown-typo>.json",
        "task_summary": "Fixture",
        "task_description": "td",
        "what_was_needed": "n",
        "severity": "info",
        "priority": "medium",
    }
    item_path = inbox / f"{item_id}.json"
    item_path.write_text(json.dumps(body, indent=2), encoding="utf-8")

    monkeypatch.setattr(cii, "update_supabase",
                        lambda **kw: (True, "stubbed OK"))
    monkeypatch.setattr(cii, "_verify_supabase_close",
                        lambda **kw: (True, "stubbed verify"))

    result = cii.close_item(
        file_path=str(item_path),
        status="completed",
        resolved_by="skill-management-hub",
        what_was_done="Test rejects unknown placeholder in filename hint",
        update_supabase_row=True,
    )
    # Close still succeeds (notification is best-effort) but notification
    # is skipped with an error message that names the placeholder contract.
    assert result["ok"]
    notif_msg = (result.get("notification_msg") or "").lower()
    assert (
        "placeholder" in notif_msg
        or "unsubstituted" in notif_msg
        or "filename_hint" in notif_msg
    ), (
        f"notification_msg should explain unsubstituted placeholder; "
        f"got {notif_msg!r}"
    )
    # No notification file should have been written
    assert result.get("notification_path") is None, (
        f"notification must not be written when hint has unknown placeholders; "
        f"got path={result.get('notification_path')}"
    )


# =============================================================================
# close-inbox-item.py: item_type validation
# =============================================================================

def test_item_type_validation_against_5_value_check_list(tmp_path, monkeypatch):
    """_derive_item_type returns one of 5 valid Supabase CHECK values.

    The 5 valid item_types per Sentinel migration
    widen_cross_workspace_requests_item_type 2026-04-30:
      work_request | routed_task | lifecycle_review | completion_notification | fyi

    Anything else is rejected at INSERT time by the CHECK; close-inbox-item
    must reject earlier with a clear error.
    """
    cii = _load_close_module()
    assert hasattr(cii, "_derive_item_type"), (
        "close-inbox-item.py must export _derive_item_type(data) for item_type "
        "validation before INSERT"
    )

    # Valid cases
    assert cii._derive_item_type({"id": "wr-skillhub-2026-04-30-001"}) == "work_request"
    assert cii._derive_item_type({"id": "rt-2026-04-30-some-slug"}) == "routed_task"
    assert cii._derive_item_type({"id": "lifecycle-2026-04-30-some-slug"}) == "lifecycle_review"
    assert cii._derive_item_type({"id": "rt-x", "kind": "completion_notification"}) == "completion_notification"
    assert cii._derive_item_type({"id": "rt-x", "kind": "fyi"}) == "fyi"

    # Unknown id prefix -> None (caller must reject)
    assert cii._derive_item_type({"id": "unknown-prefix-foo"}) is None
    assert cii._derive_item_type({}) is None


# =============================================================================
# Cross-workspace routing auto-promotion (wr-skillhub-2026-05-06-002)
# =============================================================================

def test_target_workspace_with_default_work_request_auto_promotes_to_routed_task(tmp_path):
    """When --target-workspace=NON_SKILLHUB is given without explicit --item-type,
    default work_request is auto-promoted to routed_task with stderr warning.

    Source: wr-skillhub-2026-05-06-002. Legacy bug: such filings silently
    routed to Skill Hub's local inbox. Fix: detect, auto-convert, warn.
    """
    inbox = tmp_path / "inbox"
    # Build cmd manually so we can pass --target-workspace WITHOUT item_type override
    cmd = [
        sys.executable, str(WR_SCRIPT),
        "--type", "TASK",
        "--severity", "info",
        "--workspace", "skill-management-hub",
        "--workspace-path", str(inbox),
        "--task", "Cross-workspace routing test",
        "--category", "operations",
        "--needed", "test-needed",
        "--gap", "test-gap",
        "--impact", GOOD_IMPACT,
        "--fix-type", "task",
        "--fix-desc", "test-fix-desc",
        "--no-supabase",
        "--output-dir", str(inbox),
        "--skip-dedup",
        "--target-workspace", "sentinel",
        # NO --item-type -> defaults to work_request -> should auto-promote
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, (
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    # Stderr warning fired
    assert "auto-promoting" in result.stderr.lower() or "auto-promote" in result.stderr.lower(), (
        f"expected auto-promote warning on stderr; got {result.stderr!r}"
    )
    assert "wr-skillhub-2026-05-06-002" in result.stderr
    # Resulting JSON has routed_task semantics
    _, data = _read_only_json_in(inbox)
    assert data.get("item_type") == "routed_task"
    assert data.get("routed_to") == "sentinel"
    assert data.get("routed_from") == "skill-management-hub"


def test_target_workspace_skill_management_hub_does_not_auto_promote(tmp_path):
    """target_workspace=skill-management-hub stays as work_request (default semantics).

    Skill Hub IS the work-request inbox, so addressing a WR to it is valid
    and should NOT auto-promote.
    """
    inbox = tmp_path / "inbox"
    cmd = [
        sys.executable, str(WR_SCRIPT),
        "--type", "TASK",
        "--severity", "info",
        "--workspace", "workforce-hq",
        "--workspace-path", str(inbox),
        "--task", "WR addressed to Skill Hub explicitly",
        "--category", "operations",
        "--needed", "test-needed",
        "--gap", "test-gap",
        "--impact", GOOD_IMPACT,
        "--fix-type", "task",
        "--fix-desc", "test-fix-desc",
        "--no-supabase",
        "--output-dir", str(inbox),
        "--skip-dedup",
        "--target-workspace", "skill-management-hub",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    # No auto-promote warning
    assert "auto-promot" not in result.stderr.lower(), result.stderr
    _, data = _read_only_json_in(inbox)
    assert data.get("item_type") == "work_request"


def test_target_workspace_same_as_source_does_not_auto_promote(tmp_path):
    """Self-targeted (target == source) stays as work_request.

    Edge case: a workspace filing a WR to itself for tracking purposes.
    Should NOT auto-promote (no real cross-workspace dispatch).
    """
    inbox = tmp_path / "inbox"
    cmd = [
        sys.executable, str(WR_SCRIPT),
        "--type", "TASK",
        "--severity", "info",
        "--workspace", "skill-management-hub",
        "--workspace-path", str(inbox),
        "--task", "Self-targeted WR",
        "--category", "operations",
        "--needed", "test-needed",
        "--gap", "test-gap",
        "--impact", GOOD_IMPACT,
        "--fix-type", "task",
        "--fix-desc", "test-fix-desc",
        "--no-supabase",
        "--output-dir", str(inbox),
        "--skip-dedup",
        "--target-workspace", "skill-management-hub",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert "auto-promot" not in result.stderr.lower(), result.stderr
    _, data = _read_only_json_in(inbox)
    assert data.get("item_type") == "work_request"


def test_explicit_routed_task_does_not_trigger_auto_promote_warning(tmp_path):
    """Caller explicitly passes --item-type=routed_task -- no warning.

    Auto-promote is for legacy callers who forgot the flag. Explicit caller
    sees no warning.
    """
    inbox = tmp_path / "inbox"
    result = _run_wr_subprocess(
        inbox,
        item_type="routed_task",
        target_workspace="sentinel",
    )
    assert result.returncode == 0
    assert "auto-promot" not in result.stderr.lower(), result.stderr
    _, data = _read_only_json_in(inbox)
    assert data.get("item_type") == "routed_task"
    assert data.get("routed_to") == "sentinel"
