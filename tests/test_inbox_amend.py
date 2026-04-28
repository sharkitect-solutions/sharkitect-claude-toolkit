"""Tests for inbox-amend.py: source-side inbox item amendment CLI.

Verifies all 13 amendment modes plus invariants:
- source identity matches item's source_workspace
- status guard (only amendable in new/pending/deferred)
- append-only source_amendments[] history
- atomic write via tempfile + os.replace
- auto-close on supersede/duplicate/withdraw via close-inbox-item.py call
- idempotency: same amendment_id replayed = no-op
- forward-compat schema slots reserved
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path.home() / ".claude" / "scripts" / "inbox-amend.py"


def _wr_fixture(tmp_path: Path, source: str = "workforce-hq", status: str = "pending") -> Path:
    """Create a minimal valid WR JSON in a tempdir simulating an inbox."""
    wr = {
        "id": "wr-hq-2026-04-28-001",
        "id_format_version": 2,
        "source_workspace": source,
        "request_type": "ENHANCE",
        "task_description": "test fixture",
        "severity": "warning",
        "priority": "medium",
        "status": status,
        "components": ["foo.py"],
        "source_amendments": []
    }
    p = tmp_path / "wr-hq-2026-04-28-001.json"
    p.write_text(json.dumps(wr, indent=2), encoding="utf-8")
    return p


def _rt_fixture(tmp_path: Path, source: str = "workforce-hq", target: str = "skill-management-hub", status: str = "pending") -> Path:
    """Create a minimal valid routed-task JSON for generic-amendment tests."""
    rt = {
        "id": "rt-2026-04-28-test",
        "id_format_version": 2,
        "routed_from": source,
        "routed_to": target,
        "source_workspace": source,
        "task_summary": "test fixture",
        "status": status,
        "source_amendments": []
    }
    p = tmp_path / "rt-2026-04-28-test.json"
    p.write_text(json.dumps(rt, indent=2), encoding="utf-8")
    return p


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8"
    )


# ----- Sanity tests -----

def test_help_exits_zero():
    """Sanity: --help works and exits 0."""
    r = _run(["--help"])
    assert r.returncode == 0
    out = (r.stdout + r.stderr).lower()
    assert "amend" in out


# ----- Mode 1: add-context -----

def test_add_context_appends_amendment(tmp_path: Path):
    """add-context appends an amendment event without mutating original fields."""
    f = _wr_fixture(tmp_path)
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "discovered additional context",
        "--note", "this is the new context"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert len(data["source_amendments"]) == 1
    a = data["source_amendments"][0]
    assert a["amendment_type"] == "add_context"
    assert a["actor"] == "workforce-hq"
    assert a["actor_type"] == "workspace"
    assert a["reason"] == "discovered additional context"
    assert a["notes"] == "this is the new context"
    # Forward-compat slots reserved (nullable)
    assert "condition" in a
    assert "template_id" in a
    assert "expires_at" in a
    assert "parent_etag" in a
    assert "triggers" in a
    # Original fields untouched
    assert data["task_description"] == "test fixture"
    assert data["severity"] == "warning"


# ----- Source identity validation -----

def test_source_mismatch_rejected(tmp_path: Path):
    """If --from workspace doesn't match source_workspace, reject."""
    f = _wr_fixture(tmp_path, source="workforce-hq")
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "sentinel",
        "--reason", "should be rejected",
        "--note", "should not write"
    ])
    assert r.returncode != 0
    assert "source" in r.stderr.lower()
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["source_amendments"] == []


def test_source_match_via_routed_from(tmp_path: Path):
    """For routed-tasks, source identity comes from routed_from field."""
    f = _rt_fixture(tmp_path, source="workforce-hq")
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "amend my routed task",
        "--note", "additional context"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"


# ----- Status guard -----

def test_in_progress_status_rejects_amendment(tmp_path: Path):
    """status=in_progress means target started; source amendments locked."""
    f = _wr_fixture(tmp_path, status="in_progress")
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "too late to amend",
        "--note", "should not write"
    ])
    assert r.returncode != 0
    err = r.stderr.lower()
    assert "in_progress" in err or "locked" in err


def test_completed_status_rejects_amendment(tmp_path: Path):
    """closed items can't be amended."""
    f = _wr_fixture(tmp_path, status="completed")
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "too late",
        "--note", "should not write"
    ])
    assert r.returncode != 0


# ----- Mode 2: severity-update -----

def test_severity_update_records_from_to(tmp_path: Path):
    """severity-update logs from/to and updates top-level field."""
    f = _wr_fixture(tmp_path)
    r = _run([
        "severity-update",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "blocking revenue work now",
        "--new-severity", "critical"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    a = data["source_amendments"][0]
    assert a["amendment_type"] == "severity_update"
    assert a["fields_changed"]["severity"] == {"from": "warning", "to": "critical"}
    assert data["severity"] == "critical"


# ----- Mode 3: priority-update -----

def test_priority_update_records_from_to(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "priority-update",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "blocked by Q2 deadline shift",
        "--new-priority", "high"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    a = data["source_amendments"][0]
    assert a["amendment_type"] == "priority_update"
    assert a["fields_changed"]["priority"] == {"from": "medium", "to": "high"}
    assert data["priority"] == "high"


# ----- Mode 4 + 5: component-add / component-remove -----

def test_component_add_appends(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "component-add",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "discovered these are also relevant",
        "--components", "bar.py,baz.py"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["components"] == ["foo.py", "bar.py", "baz.py"]
    assert data["source_amendments"][0]["amendment_type"] == "component_add"


def test_component_remove_drops(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "component-remove",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "foo.py turned out to be unrelated",
        "--components", "foo.py"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["components"] == []


# ----- Mode 6: add-evidence -----

def test_add_evidence_appends_to_evidence_array(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "add-evidence",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "found the error log",
        "--evidence-type", "log",
        "--evidence-ref", "/tmp/error.log",
        "--note", "stack trace at line 42"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert len(data["evidence"]) == 1
    assert data["evidence"][0]["type"] == "log"
    assert data["evidence"][0]["ref"] == "/tmp/error.log"


# ----- Mode 7: link-related -----

def test_link_related_appends_cross_reference(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "link-related",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "this depends on completing the other WR",
        "--link-type", "depends_on",
        "--link-id", "wr-hq-2026-04-25-001"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["related_items"][0] == {"type": "depends_on", "id": "wr-hq-2026-04-25-001"}


# ----- Mode 8: reclassify -----

def test_reclassify_updates_request_type(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "reclassify",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "investigation showed this is a bug not enhancement",
        "--new-type", "BUG"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["request_type"] == "BUG"


# ----- Mode 9: supersede -----

def test_supersede_requires_supersedes_id(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "supersede",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "filed broader scope as new WR"
    ])
    assert r.returncode != 0
    assert "supersedes" in r.stderr.lower()


def test_supersede_records_reference(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "supersede",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "filed broader scope at wr-hq-2026-04-29-001",
        "--supersedes", "wr-hq-2026-04-29-001",
        "--close-script-stub", str(tmp_path / "close-args.json")
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    a = data["source_amendments"][0]
    assert a["supersedes"] == "wr-hq-2026-04-29-001"
    # Auto-close was invoked
    args = json.loads((tmp_path / "close-args.json").read_text())
    assert "--status" in args["argv"]
    assert "superseded" in args["argv"]


# ----- Mode 10: duplicate -----

def test_duplicate_records_reference(tmp_path: Path):
    f = _wr_fixture(tmp_path)
    r = _run([
        "duplicate",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "found existing wr that covers this",
        "--duplicate-of", "wr-hq-2026-04-26-005",
        "--close-script-stub", str(tmp_path / "close-args.json")
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["source_amendments"][0]["duplicate_of"] == "wr-hq-2026-04-26-005"


# ----- Mode 11: withdraw -----

def test_withdraw_closes_with_withdrawn_status(tmp_path: Path):
    """withdraw mode auto-calls close-inbox-item.py with --status withdrawn."""
    f = _wr_fixture(tmp_path)
    capture = tmp_path / "close-args.json"
    r = _run([
        "withdraw",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "filed in error -- shouldn't have been created",
        "--close-script-stub", str(capture)
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    args = json.loads(capture.read_text(encoding="utf-8"))
    assert "--status" in args["argv"]
    assert "withdrawn" in args["argv"]
    # Notification reason is included in the auto-close
    idx = args["argv"].index("--what-was-done")
    assert "filed in error" in args["argv"][idx + 1].lower() or "shouldn't" in args["argv"][idx + 1].lower()


# ----- Mode 12: reroute -----

def test_reroute_moves_file_and_updates_routed_to(tmp_path: Path):
    """reroute moves the JSON to new target's inbox and updates routed_to."""
    src_inbox = tmp_path / "src-ws" / ".routed-tasks" / "inbox"
    new_target_inbox = tmp_path / "new-target-ws" / ".routed-tasks" / "inbox"
    src_inbox.mkdir(parents=True); new_target_inbox.mkdir(parents=True)

    rt = {
        "id": "rt-2026-04-28-test",
        "id_format_version": 2,
        "routed_from": "workforce-hq",
        "routed_to": "skill-management-hub",
        "source_workspace": "workforce-hq",
        "task_summary": "test reroute",
        "status": "pending",
        "source_amendments": []
    }
    src_file = src_inbox / "rt-2026-04-28-test.json"
    src_file.write_text(json.dumps(rt, indent=2), encoding="utf-8")

    r = _run([
        "reroute",
        "--file", str(src_file),
        "--from", "workforce-hq",
        "--reason", "wrong target -- should have gone to sentinel",
        "--new-target", "sentinel",
        "--new-target-inbox-dir", str(new_target_inbox)
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert not src_file.exists()
    moved = new_target_inbox / "rt-2026-04-28-test.json"
    assert moved.exists()
    data = json.loads(moved.read_text(encoding="utf-8"))
    assert data["routed_to"] == "sentinel"
    assert any(a["amendment_type"] == "reroute" for a in data["source_amendments"])
    assert data["routed_to_history"][-1]["from"] == "skill-management-hub"
    assert data["routed_to_history"][-1]["to"] == "sentinel"


def test_reroute_aborts_on_collision(tmp_path: Path):
    """If destination filename already exists, reroute aborts (no overwrite)."""
    src_inbox = tmp_path / "src" / ".routed-tasks" / "inbox"
    dst_inbox = tmp_path / "dst" / ".routed-tasks" / "inbox"
    src_inbox.mkdir(parents=True); dst_inbox.mkdir(parents=True)

    rt = {"id": "rt-test", "id_format_version": 2, "routed_from": "workforce-hq",
          "routed_to": "skill-management-hub", "source_workspace": "workforce-hq",
          "status": "pending", "source_amendments": []}
    src = src_inbox / "rt-test.json"
    src.write_text(json.dumps(rt), encoding="utf-8")
    # Pre-place a colliding file at destination
    (dst_inbox / "rt-test.json").write_text("{}", encoding="utf-8")

    r = _run([
        "reroute",
        "--file", str(src),
        "--from", "workforce-hq",
        "--reason", "collision should abort",
        "--new-target", "sentinel",
        "--new-target-inbox-dir", str(dst_inbox)
    ])
    assert r.returncode != 0
    assert "collision" in r.stderr.lower() or "exists" in r.stderr.lower()
    # Source file untouched
    assert src.exists()


# ----- Mode 13: retract-amendment -----

def test_retract_amendment_marks_original(tmp_path: Path):
    """retract appends new event referencing retracted amendment_id; original flagged."""
    f = _wr_fixture(tmp_path)
    r1 = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "first amendment",
        "--note", "to be retracted",
        "--amendment-id", "amend-test-001"
    ])
    assert r1.returncode == 0

    r2 = _run([
        "retract-amendment",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "made in error -- retracting",
        "--retracts-amendment", "amend-test-001"
    ])
    assert r2.returncode == 0
    data = json.loads(f.read_text(encoding="utf-8"))
    assert len(data["source_amendments"]) == 2
    retract_event = data["source_amendments"][1]
    assert retract_event["amendment_type"] == "retract_amendment"
    assert retract_event["retracts_amendment"] == "amend-test-001"
    # Original flagged retracted
    orig = data["source_amendments"][0]
    assert orig["retracted"] is True
    assert orig["retracted_at"] is not None
    assert orig["retracted_by_amendment_id"] is not None


# ----- bulk-amend -----

def test_bulk_amend_applies_to_all(tmp_path: Path):
    """bulk-amend mode applies same amendment to multiple files."""
    f1 = _wr_fixture(tmp_path)
    data = json.loads(f1.read_text(encoding="utf-8"))
    data["id"] = "wr-hq-2026-04-28-002"
    f2 = tmp_path / "wr-hq-2026-04-28-002.json"
    f2.write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run([
        "bulk-amend",
        "--files", f"{f1},{f2}",
        "--from", "workforce-hq",
        "--reason", "blocked by external dep",
        "--mode", "add-context",
        "--note", "shared context across all WRs"
    ])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    for fp in [f1, f2]:
        d = json.loads(fp.read_text(encoding="utf-8"))
        assert len(d["source_amendments"]) == 1
        assert d["source_amendments"][0]["notes"] == "shared context across all WRs"


def test_bulk_amend_continue_on_failure(tmp_path: Path):
    """bulk-amend continues past failures, returns nonzero if any failed."""
    f1 = _wr_fixture(tmp_path, status="pending")
    data = json.loads(f1.read_text(encoding="utf-8"))
    data["id"] = "wr-hq-2026-04-28-002"
    data["status"] = "in_progress"  # this one will fail status guard
    f2 = tmp_path / "wr-hq-2026-04-28-002.json"
    f2.write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run([
        "bulk-amend",
        "--files", f"{f1},{f2}",
        "--from", "workforce-hq",
        "--reason", "test partial failure",
        "--mode", "add-context",
        "--note", "should land on f1, fail on f2"
    ])
    assert r.returncode != 0  # nonzero because at least one failed
    # f1 succeeded
    d1 = json.loads(f1.read_text(encoding="utf-8"))
    assert len(d1["source_amendments"]) == 1
    # f2 untouched (status guard rejected)
    d2 = json.loads(f2.read_text(encoding="utf-8"))
    assert len(d2["source_amendments"]) == 0


# ----- Idempotency -----

def test_idempotent_same_amendment_id(tmp_path: Path):
    """Applying same amendment_id twice is a no-op."""
    f = _wr_fixture(tmp_path)
    r1 = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "first apply",
        "--note", "the note",
        "--amendment-id", "amend-test-001"
    ])
    assert r1.returncode == 0
    r2 = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "second apply (should no-op)",
        "--note", "different note",
        "--amendment-id", "amend-test-001"
    ])
    assert r2.returncode == 0
    data = json.loads(f.read_text(encoding="utf-8"))
    assert len(data["source_amendments"]) == 1


# ----- Validation: short reason -----

def test_short_reason_rejected(tmp_path: Path):
    """Reason must be >= 10 chars."""
    f = _wr_fixture(tmp_path)
    r = _run([
        "add-context",
        "--file", str(f),
        "--from", "workforce-hq",
        "--reason", "too short",  # 9 chars
        "--note", "should fail"
    ])
    assert r.returncode != 0
