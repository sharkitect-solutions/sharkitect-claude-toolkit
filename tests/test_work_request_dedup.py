"""Tests for work-request.py dedup window + severity floor.

Source: wr-2026-04-25-001 (CRITICAL, HQ) Phase 1 Task 1.2 in
~/.claude/plans/n8n-toolkit-audit-and-cadence-engine.md

Two gates added to the work-request.py write path:
  1. Severity floor on --impact: reject if < 30 chars OR contains a
     block-listed generic phrase ("could be useful", "might be nice", etc).
  2. 7-day dedup window: same source_workspace + same task_description filed
     within 7 days = duplicate. Increment dedup_count on the existing file
     and exit 0; do NOT write a new file.

Test cases per plan spec:
  1. Same gap from same workspace within 7 days -> counter increments, no new file.
  2. Same gap from same workspace > 7 days -> new file written.
  3. Same gap from different workspace -> new file (cross-workspace duplicates
     are independent signals).
  4. Vague --impact ("would be nice") -> rejected.
  5. Concrete --impact ("would have shortened fix by 30 minutes") -> accepted.

Bypass flags:
  --skip-dedup -- bypasses the dedup gate. Used by other test files that
                  intentionally write multiple WRs.
  --skip-impact-floor -- bypasses the impact floor. Used by other test files
                         that pass placeholder --impact "test".
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WR_SCRIPT = Path(os.path.expanduser("~/.claude/scripts/work-request.py"))

# A long, concrete impact string that passes the floor by default.
GOOD_IMPACT = (
    "Would have shortened fix by 30 minutes and raised confidence from low "
    "to high; affected the daily CEO brief generation."
)


def _run_wr(workspace: str, output_dir: Path, **kw):
    """Run work-request.py with sensible defaults; kw overrides any field.

    Defaults DO NOT bypass the new gates -- callers opt in to bypass via
    skip_dedup=True / skip_impact_floor=True. This makes the gates
    explicit in tests that exercise them.
    """
    cmd = [
        sys.executable, str(WR_SCRIPT),
        "--type", kw.get("type", "TASK"),
        "--severity", kw.get("severity", "info"),
        "--workspace", workspace,
        "--workspace-path", str(output_dir),
        "--task", kw.get("task", "Default test task description for dedup tests"),
        "--category", kw.get("category", "operations"),
        "--needed", kw.get("needed", "Default needed text for dedup tests"),
        "--gap", kw.get("gap", "Default gap text for dedup tests"),
        "--impact", kw.get("impact", GOOD_IMPACT),
        "--fix-type", kw.get("fix_type", "task"),
        "--fix-desc", kw.get("fix_desc", "Default fix description"),
        "--no-supabase",
        "--output-dir", str(output_dir),
    ]
    if kw.get("skip_dedup"):
        cmd.append("--skip-dedup")
    if kw.get("skip_impact_floor"):
        cmd.append("--skip-impact-floor")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


# ----------------------------------------------------------------------------
# Severity floor tests
# ----------------------------------------------------------------------------

def test_impact_floor_rejects_short_text(tmp_path):
    """--impact 'too short' (8 chars) -> rejected."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    r = _run_wr("skill-management-hub", inbox, impact="too short")
    assert r.returncode == 1, f"Expected rejection. stdout={r.stdout} stderr={r.stderr}"
    assert "severity floor" in r.stderr.lower()
    assert len(list(inbox.glob("*.json"))) == 0, "No file should be written on floor violation"


def test_impact_floor_rejects_block_listed_phrase(tmp_path):
    """--impact contains 'would be nice' -> rejected even if length OK."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    r = _run_wr(
        "skill-management-hub",
        inbox,
        impact="It would be nice to have this feature for our daily workflow.",
    )
    assert r.returncode == 1, f"Expected rejection. stdout={r.stdout} stderr={r.stderr}"
    assert "block-listed" in r.stderr.lower() or "block_listed" in r.stderr.lower()


def test_impact_floor_rejects_could_be_useful(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    r = _run_wr(
        "skill-management-hub",
        inbox,
        impact="This could be useful for the team in the future when scaling up.",
    )
    assert r.returncode == 1
    assert "block-listed" in r.stderr.lower()


def test_impact_floor_rejects_general_improvement(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    r = _run_wr(
        "skill-management-hub",
        inbox,
        impact="general improvement to the work-request pipeline overall.",
    )
    assert r.returncode == 1
    assert "block-listed" in r.stderr.lower()


def test_impact_floor_accepts_concrete_text(tmp_path):
    """Long concrete --impact passes."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    r = _run_wr(
        "skill-management-hub",
        inbox,
        impact=GOOD_IMPACT,
    )
    assert r.returncode == 0, f"Expected accept. stdout={r.stdout} stderr={r.stderr}"
    files = list(inbox.glob("*.json"))
    assert len(files) == 1


def test_impact_floor_bypassed_with_flag(tmp_path):
    """--skip-impact-floor lets short --impact through."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    r = _run_wr(
        "skill-management-hub",
        inbox,
        impact="x",
        skip_impact_floor=True,
    )
    assert r.returncode == 0, f"Expected accept with bypass. stderr={r.stderr}"


# ----------------------------------------------------------------------------
# Dedup window tests
# ----------------------------------------------------------------------------

def test_dedup_increments_counter_within_7_days(tmp_path):
    """Same source + same task within 7 days -> counter increments, no new file."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox.parent / "processed").mkdir()

    # First filing: should write a file.
    r1 = _run_wr(
        "skill-management-hub",
        inbox,
        task="Specific dedup test task ABC",
    )
    assert r1.returncode == 0, f"First filing failed: {r1.stderr}"
    files_after_first = list(inbox.glob("*.json"))
    assert len(files_after_first) == 1
    first_id = json.loads(files_after_first[0].read_text(encoding="utf-8"))["id"]
    assert json.loads(files_after_first[0].read_text(encoding="utf-8")).get("dedup_count", 0) == 0

    # Second filing of the SAME thing: should dedup.
    r2 = _run_wr(
        "skill-management-hub",
        inbox,
        task="Specific dedup test task ABC",
    )
    assert r2.returncode == 0, f"Second filing failed: {r2.stderr}"
    assert "duplicate of" in r2.stdout.lower(), f"Expected dedup msg. stdout={r2.stdout}"
    assert first_id in r2.stdout, f"Dedup should reference {first_id}. stdout={r2.stdout}"

    # Confirm no new file was written.
    files_after_second = list(inbox.glob("*.json"))
    assert len(files_after_second) == 1, "Dedup must not write a new file"

    # Confirm the existing file's counter incremented.
    data = json.loads(files_after_second[0].read_text(encoding="utf-8"))
    assert data["dedup_count"] == 1, f"Expected dedup_count=1, got {data.get('dedup_count')}"

    # Third filing: counter to 2.
    r3 = _run_wr(
        "skill-management-hub",
        inbox,
        task="Specific dedup test task ABC",
    )
    assert r3.returncode == 0
    data3 = json.loads(files_after_second[0].read_text(encoding="utf-8"))
    assert data3["dedup_count"] == 2


def test_dedup_writes_new_file_after_window(tmp_path):
    """Same source + same task filed > 7 days ago -> NOT a dedup; write new file."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox.parent / "processed").mkdir()

    # Hand-craft an existing file with timestamp 10 days ago.
    old_ts = (datetime.now(timezone.utc) - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    existing = {
        "id": "wr-skillhub-2026-04-18-001",
        "id_format_version": 2,
        "timestamp": old_ts,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
        "task_description": "Outside window dedup test task",
        "what_was_needed": "test",
        "severity": "info",
        "status": "new",
    }
    (inbox / "old.json").write_text(json.dumps(existing, indent=2), encoding="utf-8")

    # New filing should NOT dedup (10 days > 7-day window).
    r = _run_wr(
        "skill-management-hub",
        inbox,
        task="Outside window dedup test task",
    )
    assert r.returncode == 0
    assert "duplicate of" not in r.stdout.lower(), (
        f"Filing > window should not dedup. stdout={r.stdout}"
    )
    files = list(inbox.glob("*.json"))
    assert len(files) == 2, f"Expected 2 files (old + new). Got: {[f.name for f in files]}"


def test_dedup_does_not_match_different_workspace(tmp_path):
    """Same task from a DIFFERENT workspace -> new file (independent signal)."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox.parent / "processed").mkdir()

    # Skill Hub files first.
    r1 = _run_wr(
        "skill-management-hub",
        inbox,
        task="Cross-workspace dedup test task XYZ",
    )
    assert r1.returncode == 0

    # Sentinel files the SAME task description -- should NOT dedup.
    r2 = _run_wr(
        "sentinel",
        inbox,
        task="Cross-workspace dedup test task XYZ",
    )
    assert r2.returncode == 0
    assert "duplicate of" not in r2.stdout.lower(), (
        f"Cross-workspace same-task should NOT dedup. stdout={r2.stdout}"
    )
    files = list(inbox.glob("*.json"))
    assert len(files) == 2


def test_dedup_bypassed_with_flag(tmp_path):
    """--skip-dedup writes a new file even when a duplicate exists."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox.parent / "processed").mkdir()

    r1 = _run_wr(
        "skill-management-hub",
        inbox,
        task="Bypass dedup test task",
    )
    assert r1.returncode == 0

    r2 = _run_wr(
        "skill-management-hub",
        inbox,
        task="Bypass dedup test task",
        skip_dedup=True,
    )
    assert r2.returncode == 0
    files = list(inbox.glob("*.json"))
    assert len(files) == 2, f"Expected 2 files with bypass. Got: {[f.name for f in files]}"


def test_dedup_finds_match_in_processed_dir(tmp_path):
    """Dedup scans processed/ too, not just inbox/."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    processed = inbox.parent / "processed"
    processed.mkdir()

    # Drop a recent processed WR with matching source + task.
    recent_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    existing = {
        "id": "wr-skillhub-2026-04-27-001",
        "id_format_version": 2,
        "timestamp": recent_ts,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
        "task_description": "Processed-dir dedup match task",
        "what_was_needed": "test",
        "severity": "info",
        "status": "completed",
    }
    (processed / "p.json").write_text(json.dumps(existing, indent=2), encoding="utf-8")

    # New filing should dedup against the processed file.
    r = _run_wr(
        "skill-management-hub",
        inbox,
        task="Processed-dir dedup match task",
    )
    assert r.returncode == 0
    assert "duplicate of" in r.stdout.lower(), (
        f"Should dedup against processed/ entry. stdout={r.stdout}"
    )
    # No new file in inbox; processed/ counter incremented.
    assert len(list(inbox.glob("*.json"))) == 0
    data = json.loads((processed / "p.json").read_text(encoding="utf-8"))
    assert data["dedup_count"] == 1
