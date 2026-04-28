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
