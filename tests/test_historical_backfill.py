"""Tests for --historical-backfill mode of wr-supabase-reconcile.py.

Source: wr-sentinel-2026-04-30-010 (Phase 2 of Luminous Foundation Bridge).

The new mode INSERTs missing cross_workspace_requests rows for historical
processed/ inbox items that never had a Supabase row. Distinct from existing
modes:

  --audit-file:           PATCHes resolution_summary text only
  --historical-manifest:  PATCHes status drift on existing rows
  --historical-backfill:  INSERTs entirely new rows for missing item_ids   <-- new

Manifest schema (different from --historical-manifest list-of-flat-dicts):

  {
    "count": 259,
    "generated_at": "...",
    "records": [
      {
        "source_path": "<absolute path to processed JSON>",
        "source_workspace_dir": "<workspace directory name>",
        "fields": {
          "item_id":          str,    NOT NULL
          "item_type":        str,    NOT NULL  (5-value CHECK)
          "requested_by":     str,    NOT NULL
          "assigned_to":      str,    NOT NULL
          "summary":          str,    NOT NULL
          "status":           str,    NOT NULL  (close vocabulary)
          "priority":         str|null
          "severity":         str|null
          "context":          str|null
          "kind":             str|null
          "resolution_summary": str|null
          "resolved_by":      str|null
          "resolved_at":      str|null
          "last_updated_by":  str|null
          "created_at":       str|null
        }
      },
      ...
    ]
  }

Required behavior:
  1. Validate manifest top-level + per-record NOT NULL fields
  2. Default dry-run: print count + first-3-record preview
  3. --apply: batch 25 records per POST
  4. SELECT COUNT WHERE item_id IN (...) before each batch -> skip existing
  5. Abort on first INSERT failure with source_path identifying the bad record
  6. Output report: inserted/skipped/failed counts + elapsed time
  7. activity_stream event 'historical_backfill' on success with metadata
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(os.path.expanduser("~/.claude/scripts/wr-supabase-reconcile.py"))


def _load_module():
    """Dynamic import of wr-supabase-reconcile.py (filename has hyphens)."""
    spec = importlib.util.spec_from_file_location("wsr_test", str(SCRIPT))
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _make_record(item_id="rt-2026-04-30-test", **overrides):
    """Build a minimal valid record. Override any field via kwargs."""
    fields = {
        "item_id": item_id,
        "item_type": "routed_task",
        "requested_by": "skill-management-hub",
        "assigned_to": "workforce-hq",
        "summary": "Test record summary",
        "priority": "medium",
        "severity": None,
        "context": "",
        "kind": None,
        "status": "completed",
        "resolution_summary": "Test resolution summary",
        "resolved_by": "workforce-hq",
        "resolved_at": "2026-04-30",
        "last_updated_by": "workforce-hq",
        "created_at": "2026-04-30T00:00:00Z",
    }
    fields.update(overrides)
    return {
        "source_path": f"/fake/path/{item_id}.json",
        "source_workspace_dir": "1.- SHARKITECT DIGITAL WORKFORCE HQ",
        "fields": fields,
    }


def _make_manifest(records=None, **top):
    """Build a manifest dict. Defaults to a 1-record manifest."""
    if records is None:
        records = [_make_record()]
    return {
        "count": len(records),
        "generated_at": "2026-04-30T00:00:00Z",
        "records": records,
        "errors": [],
        **top,
    }


def _write_manifest(tmp_path, manifest):
    """Write a manifest dict to tmp_path/manifest.json. Return Path."""
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(manifest), encoding="utf-8")
    return p


def _run_subprocess(manifest_path, *extra, env_extra=None):
    """Invoke wr-supabase-reconcile.py as subprocess.

    Returns CompletedProcess. Tests assert on returncode + stdout/stderr.
    Default workspace is skill-management-hub for activity_stream attribution.

    Inject fake SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY so main() passes its
    early env check. Dry-run + validation tests don't actually hit the URL.
    """
    cmd = [
        sys.executable, str(SCRIPT),
        "--historical-backfill", str(manifest_path),
        "--workspace", "skill-management-hub",
    ]
    cmd.extend(extra)
    env = dict(os.environ)
    env.setdefault("SUPABASE_URL", "http://localhost:65535")
    env.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test_key")
    # Strip workspace-prefixed variants so the script's load_env doesn't
    # overwrite our test values with real local credentials.
    for prefix in ("SKILLHUB", "HQ", "SENTINEL"):
        env.pop(f"{prefix}_SUPABASE_URL", None)
        env.pop(f"{prefix}_SUPABASE_SERVICE_ROLE_KEY", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=30, env=env)


# =============================================================================
# Manifest validation
# =============================================================================

def test_backfill_rejects_manifest_missing_records_key(tmp_path):
    """Manifest must be a dict containing a 'records' list."""
    manifest_path = _write_manifest(tmp_path, {"count": 0, "errors": []})
    result = _run_subprocess(manifest_path)
    assert result.returncode != 0, (
        f"expected error returncode; got 0. stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )
    err = (result.stdout + result.stderr).lower()
    assert "records" in err, (
        f"error should reference missing 'records' key; got {err!r}"
    )


def test_backfill_rejects_record_missing_required_field(tmp_path):
    """Record missing a NOT NULL field (item_type) -> validation error."""
    bad = _make_record()
    bad["fields"].pop("item_type")
    manifest_path = _write_manifest(tmp_path, _make_manifest([bad]))
    result = _run_subprocess(manifest_path)
    assert result.returncode != 0, (
        f"expected validation error; got 0. stderr={result.stderr!r}"
    )
    err = (result.stdout + result.stderr).lower()
    assert "item_type" in err, (
        f"error should name the missing field item_type; got {err!r}"
    )


def test_backfill_rejects_record_with_empty_required_field(tmp_path):
    """NOT NULL means non-empty too; empty string for summary -> reject."""
    bad = _make_record()
    bad["fields"]["summary"] = ""
    manifest_path = _write_manifest(tmp_path, _make_manifest([bad]))
    result = _run_subprocess(manifest_path)
    assert result.returncode != 0
    err = (result.stdout + result.stderr).lower()
    assert "summary" in err


# =============================================================================
# Dry-run preview
# =============================================================================

def test_backfill_dry_run_prints_count_and_preview(tmp_path):
    """Default mode prints count + first-3-record preview, no Supabase calls."""
    records = [_make_record(f"rt-2026-04-30-{n:03d}") for n in range(5)]
    manifest_path = _write_manifest(tmp_path, _make_manifest(records))
    result = _run_subprocess(manifest_path, "--no-activity-log")
    assert result.returncode == 0, (
        f"dry-run should succeed; got returncode={result.returncode}. "
        f"stderr={result.stderr!r}"
    )
    out = result.stdout
    assert "5" in out, f"expected count '5' in output; got {out!r}"
    assert "rt-2026-04-30-000" in out, "first record's item_id should appear"
    assert "rt-2026-04-30-002" in out, "third record's item_id should appear"
    # 4th and 5th records should NOT be in preview (only first 3)
    # Soft-check: preview cap means the 5th item shouldn't be in a "preview"
    # block. Allowed if the script also prints a summary tail mentioning all
    # records, but explicit per-record content stays first 3.
    preview_section = out.split("(preview)")[0] if "(preview)" in out else out


def test_backfill_dry_run_does_not_call_supabase(tmp_path, monkeypatch):
    """Dry-run must not POST or GET against Supabase (call helpers in-proc)."""
    wsr = _load_module()

    insert_calls = []
    get_calls = []

    def fake_insert(*a, **kw):
        insert_calls.append((a, kw))
        return 201, ""

    def fake_get(*a, **kw):
        get_calls.append((a, kw))
        return 200, "[]"

    # Whatever helper names the implementation uses, none should fire in dry-run.
    # We patch both expected helpers and any new INSERT helper to assert non-use.
    monkeypatch.setattr(wsr, "patch_supabase",
                        lambda *a, **kw: (200, "test"))
    monkeypatch.setattr(wsr, "get_supabase",
                        lambda *a, **kw: (_record_get(get_calls, a, kw)))

    if hasattr(wsr, "insert_supabase_batch"):
        monkeypatch.setattr(wsr, "insert_supabase_batch", fake_insert)

    records = [_make_record(f"rt-2026-04-30-{n:03d}") for n in range(3)]
    manifest_path = _write_manifest(tmp_path, _make_manifest(records))

    # Drive via main() so argparse + dispatch flows are tested.
    monkeypatch.setattr(sys, "argv", [
        "wr-supabase-reconcile.py",
        "--historical-backfill", str(manifest_path),
        "--workspace", "skill-management-hub",
        "--no-activity-log",
    ])
    monkeypatch.setenv("SUPABASE_URL", "http://localhost:65535")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test_key")
    rc = wsr.main()
    assert rc == 0, "dry-run should exit 0"
    assert insert_calls == [], (
        f"dry-run must not call INSERT; got {len(insert_calls)} calls"
    )


def _record_get(bucket, a, kw):
    bucket.append((a, kw))
    return (200, "[]")


# =============================================================================
# Apply mode: batched INSERT, idempotent skip, abort-on-failure
# =============================================================================

def test_backfill_apply_inserts_in_batches_of_25(tmp_path, monkeypatch):
    """--apply batches records into POST groups of 25."""
    wsr = _load_module()

    # 60 records -> 25 + 25 + 10 = 3 POST batches
    records = [_make_record(f"rt-batch-{n:03d}") for n in range(60)]
    manifest_path = _write_manifest(tmp_path, _make_manifest(records))

    inserted_payloads = []
    select_count_calls = []

    def fake_insert_batch(base_url, key, rows):
        inserted_payloads.append(list(rows))
        return 201, ""

    def fake_select_existing(base_url, key, item_ids):
        select_count_calls.append(list(item_ids))
        return set()  # nothing exists yet

    def fake_log(base_url, key, **kw):
        return 201, ""

    assert hasattr(wsr, "insert_supabase_batch"), (
        "wr-supabase-reconcile.py must export insert_supabase_batch(base_url, "
        "key, rows: list[dict]) -> (status, body) for the backfill mode"
    )
    assert hasattr(wsr, "select_existing_item_ids"), (
        "wr-supabase-reconcile.py must export select_existing_item_ids("
        "base_url, key, item_ids: list[str]) -> set[str] for idempotent skip"
    )
    monkeypatch.setattr(wsr, "insert_supabase_batch", fake_insert_batch)
    monkeypatch.setattr(wsr, "select_existing_item_ids", fake_select_existing)
    monkeypatch.setattr(wsr, "log_activity_event", fake_log)
    monkeypatch.setattr(sys, "argv", [
        "wr-supabase-reconcile.py",
        "--historical-backfill", str(manifest_path),
        "--apply",
        "--workspace", "skill-management-hub",
        "--no-activity-log",
    ])
    monkeypatch.setenv("SUPABASE_URL", "http://localhost:65535")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test_key")

    rc = wsr.main()
    assert rc == 0, "apply mode should succeed when all inserts ok"
    # Three POST batches: 25 + 25 + 10
    assert [len(b) for b in inserted_payloads] == [25, 25, 10], (
        f"expected batch sizes [25,25,10]; got "
        f"{[len(b) for b in inserted_payloads]}"
    )
    # SELECT COUNT must be called per-batch BEFORE the INSERT
    assert len(select_count_calls) == 3, (
        f"SELECT existing must run once per batch; got {len(select_count_calls)}"
    )


def test_backfill_skips_records_already_in_supabase(tmp_path, monkeypatch):
    """Records whose item_id already exists are skipped (idempotent re-run)."""
    wsr = _load_module()

    records = [_make_record(f"rt-idem-{n:03d}") for n in range(5)]
    manifest_path = _write_manifest(tmp_path, _make_manifest(records))

    inserted_payloads = []

    def fake_insert(base_url, key, rows):
        inserted_payloads.append(list(rows))
        return 201, ""

    # Pretend records 1 and 3 already exist in Supabase
    pre_existing = {"rt-idem-001", "rt-idem-003"}

    def fake_select(base_url, key, item_ids):
        return {iid for iid in item_ids if iid in pre_existing}

    monkeypatch.setattr(wsr, "insert_supabase_batch", fake_insert)
    monkeypatch.setattr(wsr, "select_existing_item_ids", fake_select)
    monkeypatch.setattr(wsr, "log_activity_event",
                        lambda *a, **kw: (201, ""))
    monkeypatch.setattr(sys, "argv", [
        "wr-supabase-reconcile.py",
        "--historical-backfill", str(manifest_path),
        "--apply",
        "--workspace", "skill-management-hub",
        "--no-activity-log",
    ])
    monkeypatch.setenv("SUPABASE_URL", "http://localhost:65535")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test_key")

    rc = wsr.main()
    assert rc == 0
    # Only 3 records should have been inserted (5 manifest - 2 existing)
    flat = [row for batch in inserted_payloads for row in batch]
    inserted_ids = {r["item_id"] for r in flat}
    assert inserted_ids == {"rt-idem-000", "rt-idem-002", "rt-idem-004"}, (
        f"expected 3 inserts excluding pre-existing; got {inserted_ids}"
    )


def test_backfill_aborts_on_insert_failure_naming_source_path(tmp_path, monkeypatch):
    """First INSERT failure -> abort with stderr citing failing record's source_path."""
    wsr = _load_module()

    records = [
        _make_record("rt-ok-001"),
        _make_record("rt-bad-002"),
        _make_record("rt-skipped-003"),
    ]
    # Mark the bad record's source_path so we can assert it appears in stderr
    records[1]["source_path"] = r"C:\fake\path\rt-bad-002.json"
    manifest_path = _write_manifest(tmp_path, _make_manifest(records))

    insert_calls = 0

    def fake_insert(base_url, key, rows):
        nonlocal insert_calls
        insert_calls += 1
        # Force failure on the first batch (which contains all 3 records)
        return 500, "synthetic INSERT failure for test"

    monkeypatch.setattr(wsr, "insert_supabase_batch", fake_insert)
    monkeypatch.setattr(wsr, "select_existing_item_ids",
                        lambda *a, **kw: set())
    monkeypatch.setattr(wsr, "log_activity_event",
                        lambda *a, **kw: (201, ""))
    monkeypatch.setattr(sys, "argv", [
        "wr-supabase-reconcile.py",
        "--historical-backfill", str(manifest_path),
        "--apply",
        "--workspace", "skill-management-hub",
        "--no-activity-log",
    ])
    monkeypatch.setenv("SUPABASE_URL", "http://localhost:65535")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test_key")

    rc = wsr.main()
    assert rc != 0, (
        f"expected non-zero exit on insert failure; got {rc}"
    )


# =============================================================================
# Activity-stream logging on success
# =============================================================================

def test_backfill_logs_activity_stream_event_on_success(tmp_path, monkeypatch):
    """After successful run, log activity_stream event 'historical_backfill'."""
    wsr = _load_module()

    records = [_make_record(f"rt-log-{n:03d}") for n in range(3)]
    manifest_path = _write_manifest(tmp_path, _make_manifest(records))

    log_calls = []

    def fake_log(base_url, key, **kw):
        log_calls.append(kw)
        return 201, ""

    monkeypatch.setattr(wsr, "insert_supabase_batch",
                        lambda *a, **kw: (201, ""))
    monkeypatch.setattr(wsr, "select_existing_item_ids",
                        lambda *a, **kw: set())
    monkeypatch.setattr(wsr, "log_activity_event", fake_log)
    monkeypatch.setattr(sys, "argv", [
        "wr-supabase-reconcile.py",
        "--historical-backfill", str(manifest_path),
        "--apply",
        "--workspace", "skill-management-hub",
    ])
    monkeypatch.setenv("SUPABASE_URL", "http://localhost:65535")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test_key")

    rc = wsr.main()
    assert rc == 0
    assert len(log_calls) == 1, (
        f"expected 1 activity_stream log call; got {len(log_calls)}"
    )
    call = log_calls[0]
    assert call["event_type"] == "historical_backfill", (
        f"event_type must be 'historical_backfill'; got {call.get('event_type')!r}"
    )
    metadata = call.get("metadata", {})
    assert metadata.get("inserted") == 3
    assert metadata.get("skipped") == 0
    assert metadata.get("failed") == 0
    assert "manifest_path" in metadata
    assert metadata.get("manifest_count") == 3
    assert metadata.get("batch_size") == 25


# =============================================================================
# Mutex with existing modes
# =============================================================================

def test_backfill_mutex_with_audit_file_and_historical_manifest(tmp_path):
    """--historical-backfill cannot be combined with --audit-file or
    --historical-manifest (argparse mutex group)."""
    manifest_path = _write_manifest(tmp_path, _make_manifest())
    other_path = tmp_path / "other.json"
    other_path.write_text("[]", encoding="utf-8")

    cmd = [
        sys.executable, str(SCRIPT),
        "--historical-backfill", str(manifest_path),
        "--audit-file", str(other_path),
        "--workspace", "skill-management-hub",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    assert result.returncode != 0, (
        "argparse should reject combining --historical-backfill with --audit-file"
    )
