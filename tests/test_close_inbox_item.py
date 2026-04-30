"""Additions for plan Phase C: withdrawn status, deprecation, annotate mode."""

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path.home() / ".claude" / "scripts" / "close-inbox-item.py"


def _make_inbox_item(tmp_path, item_id="wr-skillhub-2026-04-28-test", status="pending"):
    """Create a minimal valid inbox item JSON in an inbox/ directory under tmp_path."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    item_path = inbox / f"{item_id}.json"
    item = {
        "id": item_id,
        "id_format_version": 2,
        "source_workspace": "skill-management-hub",
        "routed_from": "skill-management-hub",
        "routed_to": "skill-management-hub",
        "status": status,
        "task_summary": "Test fixture for close-inbox-item.py phase C tests",
        "notify_on_completion": False,
    }
    item_path.write_text(json.dumps(item, indent=2), encoding="utf-8")
    return item_path


def _run_close(item_path, *extra_args):
    """Invoke close-inbox-item.py as a subprocess and return CompletedProcess."""
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--file", str(item_path),
        "--resolved-by", "skill-management-hub",
        "--what-was-done", "Test close in phase C suite -- verified by pytest fixture",
        "--no-supabase",
    ]
    cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True)


def test_status_withdrawn_accepted(tmp_path):
    """--status withdrawn is a valid close status; file moves to processed/."""
    item_path = _make_inbox_item(tmp_path)
    result = _run_close(
        item_path,
        "--status", "withdrawn",
        "--no-notify", "--no-notify-reason", "test-only",
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    # Item should have moved to processed/
    processed = tmp_path / "processed" / item_path.name
    assert processed.exists(), "item not moved to processed/"
    assert not item_path.exists(), "source file should have been moved out of inbox/"
    closed = json.loads(processed.read_text(encoding="utf-8"))
    assert closed["status"] == "withdrawn"


def test_processed_auto_converts_to_completed(tmp_path):
    """--status processed prints DEPRECATION warning + writes status='completed'."""
    item_path = _make_inbox_item(tmp_path)
    result = _run_close(
        item_path,
        "--status", "processed",
        "--no-notify", "--no-notify-reason", "test-only",
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    assert "DEPRECATION" in result.stderr
    assert "auto-converted to 'completed'" in result.stderr
    processed = tmp_path / "processed" / item_path.name
    assert not item_path.exists(), "source file should have been moved out of inbox/"
    closed = json.loads(processed.read_text(encoding="utf-8"))
    assert closed["status"] == "completed", f"expected 'completed', got {closed['status']!r}"


def test_resolved_auto_converts_to_completed(tmp_path):
    """--status resolved prints DEPRECATION warning + writes status='completed'."""
    item_path = _make_inbox_item(tmp_path)
    result = _run_close(
        item_path,
        "--status", "resolved",
        "--no-notify", "--no-notify-reason", "test-only",
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    assert "DEPRECATION" in result.stderr
    processed = tmp_path / "processed" / item_path.name
    assert not item_path.exists(), "source file should have been moved out of inbox/"
    closed = json.loads(processed.read_text(encoding="utf-8"))
    assert closed["status"] == "completed"


def test_annotate_appends_without_closing(tmp_path):
    """--annotate appends a status_history entry, leaves file in inbox/, status unchanged."""
    item_path = _make_inbox_item(tmp_path, status="in_progress")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--file", str(item_path),
            "--resolved-by", "skill-management-hub",
            "--what-was-done", "Halfway through schema migration -- 3 of 7 tables done",
            "--annotate",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    # File should NOT have moved
    assert item_path.exists(), "annotate must leave file in inbox/"
    processed_path = tmp_path / "processed" / item_path.name
    assert not processed_path.exists(), "annotate must not move file to processed/"
    # Status unchanged
    item = json.loads(item_path.read_text(encoding="utf-8"))
    assert item["status"] == "in_progress"
    # status_history has one entry
    assert "status_history" in item
    assert len(item["status_history"]) == 1
    note = item["status_history"][0]
    assert note["kind"] == "annotation"
    assert note["actor"] == "skill-management-hub"
    assert note["status"] == "in_progress"
    assert "Halfway through schema migration" in note["note"]


def test_annotate_rejects_non_inbox_file(tmp_path):
    """--annotate must refuse to mutate files that aren't in an inbox/ dir."""
    item_path = _make_inbox_item(tmp_path, status="in_progress")
    # Simulate a file that's already in processed/ -- mv it
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    target = processed_dir / item_path.name
    item_path.rename(target)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--file", str(target),
            "--resolved-by", "skill-management-hub",
            "--what-was-done", "Should be rejected because not in inbox/",
            "--annotate",
            "--no-supabase",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, f"expected non-zero, got 0 (stdout={result.stdout!r})"
    assert "inbox/" in result.stderr or "inbox" in result.stderr.lower()
    # File body should be untouched
    data = json.loads(target.read_text(encoding="utf-8"))
    assert "status_history" not in data or len(data.get("status_history", [])) == 0


def test_annotate_rejects_already_closed_status(tmp_path):
    """--annotate must refuse to mutate items whose status is a close-state."""
    item_path = _make_inbox_item(tmp_path, status="completed")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--file", str(item_path),
            "--resolved-by", "skill-management-hub",
            "--what-was-done", "Should be rejected because status is closed",
            "--annotate",
            "--no-supabase",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, f"expected non-zero, got 0 (stdout={result.stdout!r})"
    assert "close-state" in result.stderr or "closed" in result.stderr.lower()
    data = json.loads(item_path.read_text(encoding="utf-8"))
    # Body unchanged
    assert "status_history" not in data or len(data.get("status_history", [])) == 0


# --- Close-out verify scope (wr-sentinel-2026-04-29-005) --------------------
# cross_workspace_requests holds WR rows only. Routed tasks (rt-*) and
# lifecycle reviews (lifecycle-*) PATCH 0 rows then trip the verify with
# 'item_id not found'. The skip branch suppresses the noise without changing
# the verify behavior for real WRs.

def _load_module():
    """Dynamic import of the script (filename has hyphens)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("cii", str(SCRIPT))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _make_item(tmp_path, item_id, kind=None):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    p = inbox / f"{item_id}.json"
    body = {
        "id": item_id,
        "id_format_version": 2,
        "source_workspace": "skill-management-hub",
        "routed_from": "skill-management-hub",
        "routed_to": "skill-management-hub",
        "status": "pending",
        "notify_on_completion": False,
    }
    if kind:
        body["kind"] = kind
    p.write_text(json.dumps(body, indent=2), encoding="utf-8")
    return p


def test_close_out_verify_skipped_for_rt_prefix(tmp_path, monkeypatch):
    """rt-* items skip close-out verify -- table holds WRs only."""
    cii = _load_module()
    monkeypatch.setattr(cii, "update_supabase", lambda **kw: (True, "stubbed OK"))

    def must_not_run(**kw):
        raise AssertionError("_verify_supabase_close called for rt- item")
    monkeypatch.setattr(cii, "_verify_supabase_close", must_not_run)

    item_path = _make_item(tmp_path, "rt-test-2026-04-30", kind="completion_notification")
    result = cii.close_item(
        file_path=str(item_path),
        status="completed",
        resolved_by="skill-management-hub",
        what_was_done="Test ack of rt- completion notification -- verifying skip path",
        update_supabase_row=True,
    )
    assert result["ok"]
    assert "skipped" in result["supabase_verify"]
    assert "not a WR" in result["supabase_verify"]


def test_close_out_verify_skipped_for_lifecycle_prefix(tmp_path, monkeypatch):
    """lifecycle-* items also skip close-out verify."""
    cii = _load_module()
    monkeypatch.setattr(cii, "update_supabase", lambda **kw: (True, "stubbed OK"))

    def must_not_run(**kw):
        raise AssertionError("_verify_supabase_close called for lifecycle- item")
    monkeypatch.setattr(cii, "_verify_supabase_close", must_not_run)

    item_path = _make_item(tmp_path, "lifecycle-test-2026-04-30")
    result = cii.close_item(
        file_path=str(item_path),
        status="completed",
        resolved_by="skill-management-hub",
        what_was_done="Test close of lifecycle review -- verifying skip path",
        update_supabase_row=True,
    )
    assert result["ok"]
    assert "skipped" in result["supabase_verify"]


def test_close_out_verify_still_runs_for_wr_prefix(tmp_path, monkeypatch):
    """wr-* items DO run close-out verify (regression guard)."""
    cii = _load_module()
    monkeypatch.setattr(cii, "update_supabase", lambda **kw: (True, "stubbed OK"))

    captured = []

    def fake_verify(**kw):
        captured.append(kw["item_id"])
        return (True, "fake verify OK")
    monkeypatch.setattr(cii, "_verify_supabase_close", fake_verify)

    item_path = _make_item(tmp_path, "wr-skillhub-2026-04-30-test")
    result = cii.close_item(
        file_path=str(item_path),
        status="completed",
        resolved_by="skill-management-hub",
        what_was_done="Test close of wr- request -- verify still runs",
        update_supabase_row=True,
    )
    assert result["ok"]
    assert captured == ["wr-skillhub-2026-04-30-test"]
    assert "fake verify OK" in result["supabase_verify"]
