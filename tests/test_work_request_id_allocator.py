"""Tests for work-request.py ID allocator's Supabase-aware behavior.

Source: wr-skillhub-2026-05-04-003.

Bug class: routed-task JSON moves to ANOTHER workspace's inbox (e.g. Sentinel's),
leaving no local trace under Skill Hub's `.work-requests/inbox/` or `processed/`.
The Supabase row, however, persists under that item_id forever. The pre-fix
allocator counted local files only -- so an ID became "available" again the
moment its JSON moved to another workspace, causing UNIQUE constraint
collisions on the next Supabase POST.

Fix: allocator now scans BOTH local inbox/processed AND Supabase
`cross_workspace_requests` for the workspace+date prefix, picks max(used)+1
across the union. Supabase scan gracefully falls back to local-only on
network error / missing credentials.

Test harness: `WR_FAKE_SUPABASE_USED_NNNS` env var injects a fake "Supabase
returned these NNNs" set without requiring a real HTTP server. This is a
narrow, documented test-only hook in the script.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WR_SCRIPT = Path(os.path.expanduser("~/.claude/scripts/work-request.py"))


def _run_wr(workspace: str, output_dir: Path, *, env_overrides=None, no_supabase=True):
    """Run work-request.py in test mode with optional env overrides.

    Default no_supabase=True so the Supabase WRITE path is skipped (tests should
    not POST). Pass no_supabase=False to exercise the Supabase READ path -- in
    that case, set WR_FAKE_SUPABASE_USED_NNNS via env_overrides to inject a
    deterministic fake response.
    """
    cmd = [
        sys.executable, str(WR_SCRIPT),
        "--type", "TASK",
        "--severity", "info",
        "--workspace", workspace,
        "--workspace-path", str(output_dir),
        "--task", "test allocator",
        "--category", "operations",
        "--needed", "test",
        "--gap", "test",
        "--impact", "test impact for the severity floor minimum length req",
        "--fix-type", "task",
        "--fix-desc", "test",
        "--skip-dedup",
        "--skip-impact-floor",
        "--output-dir", str(output_dir),
    ]
    if no_supabase:
        cmd.append("--no-supabase")

    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _seed_processed(processed_dir: Path, item_id: str, ws_slug: str = "skill-management-hub"):
    """Drop a JSON in processed/ with a given v2 id (so local scan picks it up)."""
    today = _today()
    fname = f"{today}_{ws_slug}_seeded-{item_id.split('-')[-1]}.json"
    p = processed_dir / fname
    p.write_text(json.dumps({
        "id": item_id,
        "id_format_version": 2,
        "request_type": "TASK",
        "source_workspace": ws_slug,
        "status": "completed",
    }), encoding="utf-8")
    return p


# ----------------------------------------------------------------------------
# Test 1 (WR scenario a): inbox empty + Supabase has -001, -002 -> next is -003.
# ----------------------------------------------------------------------------

def test_supabase_scan_returns_next_after_max(tmp_path):
    """Scenario (a) from wr-skillhub-2026-05-04-003.

    Local inbox is empty. Supabase has rows under wr-skillhub-<today>-001 and
    -002 (because earlier WRs were filed and JSONs moved to other workspaces'
    inboxes -- a routed-task pattern). Allocator must return -003, not -001.
    """
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (tmp_path / "processed").mkdir()

    today = _today()
    r = _run_wr(
        "skill-management-hub",
        inbox,
        env_overrides={"WR_FAKE_SUPABASE_USED_NNNS": "1,2"},
        no_supabase=False,  # exercise the Supabase READ path
    )
    assert r.returncode == 0, f"WR failed: {r.stderr}\n{r.stdout}"
    files = list(inbox.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    expected = f"wr-skillhub-{today}-003"
    assert data["id"] == expected, (
        f"Expected {expected} (Supabase max=2, local empty -> next=3), got {data['id']}"
    )


# ----------------------------------------------------------------------------
# Test 2 (WR scenario b): inbox has -005 + Supabase has -003 -> next is -006.
# ----------------------------------------------------------------------------

def test_local_and_supabase_union_max(tmp_path):
    """Scenario (b) from wr-skillhub-2026-05-04-003.

    Local processed/ has a -005 JSON (v2 id). Supabase has -003. Union max=5.
    Allocator must return -006.
    """
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    processed = tmp_path / "processed"
    processed.mkdir()

    today = _today()
    _seed_processed(processed, f"wr-skillhub-{today}-005")

    r = _run_wr(
        "skill-management-hub",
        inbox,
        env_overrides={"WR_FAKE_SUPABASE_USED_NNNS": "3"},
        no_supabase=False,
    )
    assert r.returncode == 0, f"WR failed: {r.stderr}\n{r.stdout}"
    files = list(inbox.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    expected = f"wr-skillhub-{today}-006"
    assert data["id"] == expected, (
        f"Expected {expected} (max(local=5, supabase=3)+1=6), got {data['id']}"
    )


# ----------------------------------------------------------------------------
# Test 3: --no-supabase skips the Supabase scan (regression for existing tests).
# ----------------------------------------------------------------------------

def test_no_supabase_flag_skips_supabase_scan(tmp_path):
    """When --no-supabase is set, allocator MUST NOT consult Supabase.

    This preserves the existing test harness contract: tests that pass
    --no-supabase get pure local-only behavior. Even if WR_FAKE_SUPABASE_USED_NNNS
    is set, --no-supabase wins.
    """
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (tmp_path / "processed").mkdir()

    today = _today()
    r = _run_wr(
        "skill-management-hub",
        inbox,
        env_overrides={"WR_FAKE_SUPABASE_USED_NNNS": "1,2,3,4,5"},
        no_supabase=True,  # explicit skip
    )
    assert r.returncode == 0, f"WR failed: {r.stderr}\n{r.stdout}"
    files = list(inbox.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    expected = f"wr-skillhub-{today}-001"
    assert data["id"] == expected, (
        f"Expected {expected} (--no-supabase = local only, inbox empty -> 001), "
        f"got {data['id']}"
    )


# ----------------------------------------------------------------------------
# Test 4: Supabase unreachable -> graceful fallback to local-only scan.
# ----------------------------------------------------------------------------

def test_supabase_unreachable_falls_back_to_local(tmp_path):
    """When Supabase scan returns None (no creds, network error), allocator
    must still produce a valid id from local-only data. The bug-fix should NOT
    introduce a new failure mode where Supabase outage breaks WR filing.
    """
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    processed = tmp_path / "processed"
    processed.mkdir()

    today = _today()
    _seed_processed(processed, f"wr-skillhub-{today}-007")

    # No WR_FAKE env var, no SUPABASE_URL -> _fetch returns None, fall back.
    # Pre-emptively unset SUPABASE_* in env to be deterministic on dev machines.
    env_overrides = {}
    for k in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY",
              "SKILLHUB_SUPABASE_URL", "SKILLHUB_SUPABASE_SERVICE_ROLE_KEY"):
        env_overrides[k] = ""

    r = _run_wr(
        "skill-management-hub",
        inbox,
        env_overrides=env_overrides,
        no_supabase=False,  # don't skip the scan; we want it to attempt and fail
    )
    assert r.returncode == 0, f"WR failed: {r.stderr}\n{r.stdout}"
    files = list(inbox.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    expected = f"wr-skillhub-{today}-008"
    assert data["id"] == expected, (
        f"Expected {expected} (Supabase unreachable, local max=7 -> 8), "
        f"got {data['id']}"
    )


# ----------------------------------------------------------------------------
# Test 5: collision-retry log line surfaces when Supabase finds a counter
# the local scan missed (operator visibility per WR spec).
# ----------------------------------------------------------------------------

def test_collision_retry_log_visible(tmp_path):
    """When Supabase has counters not in local scan, a log line must surface
    so operators see the discrepancy. Spec: 'surface a clear log line on
    collision retry so operators see it.'

    We don't mandate exact wording -- assert on a stable substring.
    """
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (tmp_path / "processed").mkdir()

    r = _run_wr(
        "skill-management-hub",
        inbox,
        env_overrides={"WR_FAKE_SUPABASE_USED_NNNS": "1,2,7"},
        no_supabase=False,
    )
    assert r.returncode == 0, f"WR failed: {r.stderr}\n{r.stdout}"
    combined = (r.stdout + r.stderr).lower()
    assert "supabase" in combined, "Operator log line must mention Supabase"
    # The log line should reference at least one of the counters Supabase
    # uniquely contributed (1, 2, or 7 -- all of them, since local was empty).
    assert any(s in combined for s in ("1, 2, 7", "[1, 2, 7]", "001", "007")), (
        f"Operator log line should reference the discovered counters. "
        f"Got: {combined[-500:]}"
    )
