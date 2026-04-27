"""Tests for workspace-prefixed WR id schema (wr-2026-04-25-007 fix).

Plan: ~/.claude/plans/2026-04-27-wr-id-schema-workspace-prefixed.md
Spec: 3.- Skill Management Hub/docs/superpowers/specs/2026-04-27-wr-id-schema-workspace-prefixed-design.md
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

WR_SCRIPT = Path(os.path.expanduser("~/.claude/scripts/work-request.py"))
CLOSE_SCRIPT = Path(os.path.expanduser("~/.claude/scripts/close-inbox-item.py"))
HOOK_PATH = Path(os.path.expanduser("~/.claude/hooks/inbox-json-validate.py"))

ID_RE_V2 = re.compile(r"^wr-(hq|skillhub|sentinel)-\d{4}-\d{2}-\d{2}-\d{3}$")


# ----------------------------------------------------------------------------
# Task 1: work-request.py — workspace-prefixed v2 id
# ----------------------------------------------------------------------------

def _run_wr(workspace: str, output_dir: Path, **kw):
    cmd = [
        sys.executable, str(WR_SCRIPT),
        "--type", kw.get("type", "TASK"),
        "--severity", kw.get("severity", "info"),
        "--workspace", workspace,
        "--workspace-path", str(output_dir),
        "--task", kw.get("task", "test"),
        "--category", kw.get("category", "operations"),
        "--needed", kw.get("needed", "test"),
        "--gap", kw.get("gap", "test"),
        "--impact", kw.get("impact", "test"),
        "--fix-type", kw.get("fix_type", "task"),
        "--fix-desc", kw.get("fix_desc", "test"),
        "--no-supabase",
        "--output-dir", str(output_dir),
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def test_workspace_prefixed_id_skillhub(tmp_path):
    out = tmp_path / "inbox"
    out.mkdir()
    r = _run_wr("skill-management-hub", out)
    assert r.returncode == 0, f"WR failed: {r.stderr}\n{r.stdout}"
    files = list(out.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    assert ID_RE_V2.match(data["id"]), f"Bad id: {data['id']}"
    assert data["id"].startswith("wr-skillhub-")
    assert data["id_format_version"] == 2


def test_workspace_prefixed_id_hq(tmp_path):
    out = tmp_path / "inbox"
    out.mkdir()
    r = _run_wr("workforce-hq", out)
    assert r.returncode == 0, r.stderr
    data = json.loads(list(out.glob("*.json"))[0].read_text(encoding="utf-8"))
    assert data["id"].startswith("wr-hq-")
    assert data["id_format_version"] == 2


def test_workspace_prefixed_id_sentinel(tmp_path):
    out = tmp_path / "inbox"
    out.mkdir()
    r = _run_wr("sentinel", out)
    assert r.returncode == 0, r.stderr
    data = json.loads(list(out.glob("*.json"))[0].read_text(encoding="utf-8"))
    assert data["id"].startswith("wr-sentinel-")


def test_unknown_workspace_rejected(tmp_path):
    out = tmp_path / "inbox"
    out.mkdir()
    r = _run_wr("unknown-ws", out)
    assert r.returncode != 0
    assert "workspace" in (r.stderr + r.stdout).lower()


def test_counter_increments_per_workspace_per_date(tmp_path):
    """Same workspace + same date = NNN increments. No cross-workspace bleed."""
    out = tmp_path / "inbox"
    out.mkdir()
    r1 = _run_wr("skill-management-hub", out)
    r2 = _run_wr("skill-management-hub", out)
    assert r1.returncode == 0 and r2.returncode == 0
    files = sorted(out.glob("*.json"))
    assert len(files) == 2
    ids = sorted(json.loads(f.read_text(encoding="utf-8"))["id"] for f in files)
    nnns = [int(i.rsplit("-", 1)[1]) for i in ids]
    assert nnns[1] == nnns[0] + 1, f"Expected sequential, got {nnns}"


def test_cross_workspace_filename_collision_does_not_block_allocation(tmp_path):
    """Regression for wr-skillhub-2026-04-27-002 / wr-hq-2026-04-27-002.

    Prior bug: filename collision check globbed across ALL workspace prefixes
    (`{today}_*-{id_suffix}.json`), so when Sentinel had filed a -001 today and
    Skill Hub tried to file its first WR for today, the script's get_next_id()
    correctly returned 001 under Skill Hub's namespace but the filename glob
    saw the Sentinel -001 file and treated it as a collision -- looping until
    "failed to allocate unique request id after 10 retries".

    Fix at work-request.py:586-591 narrows the glob to {today}_{ws_slug}_*-NNN.json.
    This test pre-seeds the processed/ dir with a Sentinel -001 file under
    today's date, then files a Skill Hub WR. The script must allocate -001
    (under skillhub namespace) cleanly -- proving the filename glob is now
    workspace-scoped.
    """
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    processed = tmp_path / "processed"
    processed.mkdir()

    # Pre-seed processed/ with a Sentinel -001 file from today.
    # Different workspace prefix; legacy v1 id format (NNN suffix is what
    # the old buggy glob would have matched).
    sentinel_seed = processed / f"{today}_sentinel_some-prior-task-001.json"
    sentinel_seed.write_text(json.dumps({
        "id": f"wr-{today}-001",
        "request_type": "TASK",
        "source_workspace": "sentinel",
        "status": "processed",
    }), encoding="utf-8")

    # Now file from skill-management-hub. Must allocate -001 (skillhub
    # namespace), not retry past it.
    r = _run_wr("skill-management-hub", inbox)
    assert r.returncode == 0, (
        f"WR file failed (cross-workspace collision regression): "
        f"stderr={r.stderr}\nstdout={r.stdout}"
    )

    files = list(inbox.glob("*.json"))
    assert len(files) == 1, f"Expected 1 file, got {len(files)}"
    data = json.loads(files[0].read_text(encoding="utf-8"))
    assert data["id"].startswith("wr-skillhub-"), f"Bad prefix: {data['id']}"
    nnn = int(data["id"].rsplit("-", 1)[1])
    assert nnn == 1, (
        f"Expected NNN=001 (skillhub namespace, ignoring sentinel prior), "
        f"got NNN={nnn:03d}. The workspace-scoped glob fix may have regressed."
    )


# ----------------------------------------------------------------------------
# Task 2: close-inbox-item.py — strict v2 id
# ----------------------------------------------------------------------------

def _make_item(tmp: Path, name: str, payload: dict):
    inbox = tmp / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    (tmp / "processed").mkdir(exist_ok=True)
    (tmp / "outbox").mkdir(exist_ok=True)
    p = inbox / name
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return p


def test_close_v2_uses_json_id_not_filename(tmp_path):
    """Filename slug deliberately mismatches id; JSON id MUST win."""
    p = _make_item(tmp_path, "weird-mismatch-slug.json", {
        "id": "wr-skillhub-2026-04-27-042",
        "id_format_version": 2,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
        "status": "new",
        "notify_on_completion": False,
    })
    r = subprocess.run(
        [sys.executable, str(CLOSE_SCRIPT),
         "--file", str(p), "--status", "processed",
         "--resolved-by", "skill-management-hub",
         "--what-was-done", "Test harness verification close.",
         "--no-supabase", "--no-notify", "--no-notify-reason", "test"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"close failed: {r.stderr}"
    moved = tmp_path / "processed" / "weird-mismatch-slug.json"
    assert moved.exists()
    d = json.loads(moved.read_text(encoding="utf-8"))
    assert d["id"] == "wr-skillhub-2026-04-27-042"


def test_close_v2_missing_id_refused(tmp_path):
    p = _make_item(tmp_path, "no-id.json", {
        "id_format_version": 2,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
        "status": "new",
    })
    r = subprocess.run(
        [sys.executable, str(CLOSE_SCRIPT),
         "--file", str(p), "--status", "processed",
         "--resolved-by", "skill-management-hub",
         "--what-was-done", "Should be refused on v2 missing id field.",
         "--no-supabase", "--no-notify", "--no-notify-reason", "test"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode != 0
    combined = (r.stderr + r.stdout).lower()
    assert "id" in combined


def test_close_legacy_v1_works(tmp_path):
    """v1 file (no id_format_version) with id field still closes for backward compat."""
    p = _make_item(tmp_path, "2026-04-22_skill-management-hub_legacy-005.json", {
        "id": "wr-2026-04-22-005",
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
        "status": "new",
        "notify_on_completion": False,
    })
    r = subprocess.run(
        [sys.executable, str(CLOSE_SCRIPT),
         "--file", str(p), "--status", "processed",
         "--resolved-by", "skill-management-hub",
         "--what-was-done", "Backward compat closure of legacy v1 record.",
         "--no-supabase", "--no-notify", "--no-notify-reason", "test"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"v1 close failed: {r.stderr}"


# ----------------------------------------------------------------------------
# Task 3: inbox-json-validate.py — write-time enforcement
# ----------------------------------------------------------------------------

def _run_hook(file_path: Path, content_dict: dict):
    stdin = json.dumps({
        "tool_name": "Write",
        "tool_input": {
            "file_path": str(file_path),
            "content": json.dumps(content_dict),
        },
    })
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=stdin, capture_output=True, text=True, timeout=10,
    )


def test_hook_blocks_v2_without_id(tmp_path):
    p = tmp_path / ".work-requests" / "inbox" / "no-id.json"
    p.parent.mkdir(parents=True)
    r = _run_hook(p, {
        "id_format_version": 2,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
    })
    assert r.returncode == 2, f"should block missing id: {r.stdout}\n{r.stderr}"


def test_hook_blocks_v2_invalid_format(tmp_path):
    p = tmp_path / ".work-requests" / "inbox" / "bad.json"
    p.parent.mkdir(parents=True)
    r = _run_hook(p, {
        "id": "wr-bogus-format",
        "id_format_version": 2,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
    })
    assert r.returncode == 2


def test_hook_allows_v2_valid(tmp_path):
    p = tmp_path / ".work-requests" / "inbox" / "good.json"
    p.parent.mkdir(parents=True)
    r = _run_hook(p, {
        "id": "wr-skillhub-2026-04-27-001",
        "id_format_version": 2,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
    })
    assert r.returncode == 0, f"should allow valid v2: {r.stderr}"


def test_hook_allows_legacy_v1(tmp_path):
    p = tmp_path / ".work-requests" / "inbox" / "legacy.json"
    p.parent.mkdir(parents=True)
    r = _run_hook(p, {
        "id": "wr-2026-04-22-005",
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
    })
    assert r.returncode == 0, f"v1 should pass: {r.stderr}"


# ----------------------------------------------------------------------------
# wr-2026-04-27-019: vague-guard exemption for completion_notification acks
# Per Completion Notification Protocol (universal-protocols.md, ack side):
# closures of kind=completion_notification with status in {processed,
# completed, resolved} may use 'Acknowledged...' phrasing (>=10 char minimum
# still applies). Filed by Sentinel after a 19-item batch ack was rejected.
# ----------------------------------------------------------------------------

def _make_close_target(tmp, name, payload):
    inbox = tmp / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    (tmp / "processed").mkdir(exist_ok=True)
    (tmp / "outbox").mkdir(exist_ok=True)
    p = inbox / name
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return p


def _run_close(file_path, what_was_done, **flags):
    cmd = [
        sys.executable, str(CLOSE_SCRIPT),
        "--file", str(file_path),
        "--status", flags.get("status", "processed"),
        "--resolved-by", flags.get("resolved_by", "skill-management-hub"),
        "--what-was-done", what_was_done,
        "--no-supabase",
        "--no-notify",
        "--no-notify-reason", "test",
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def test_ack_close_allows_acknowledged_phrasing(tmp_path):
    """kind=completion_notification + status=processed: 'Acknowledged...' OK."""
    p = _make_close_target(tmp_path, "rt-2026-04-27-completion-test.json", {
        "id": "rt-skillhub-2026-04-27-completion-test",
        "id_format_version": 2,
        "kind": "completion_notification",
        "routed_from": "sentinel",
        "routed_to": "skill-management-hub",
        "completes_task_id": "wr-foo-2026-04-27-001",
        "what_was_done": "Sentinel did the work.",
        "notify_on_completion": False,
    })
    r = _run_close(p, "Acknowledged completion notification for wr-foo-2026-04-27-001.")
    assert r.returncode == 0, f"ack-close with 'Acknowledged' should pass: {r.stderr}"
    assert (tmp_path / "processed" / "rt-2026-04-27-completion-test.json").exists()


def test_ack_close_still_enforces_min_length(tmp_path):
    """ack-close exemption does NOT bypass >=10 char minimum."""
    p = _make_close_target(tmp_path, "rt-2026-04-27-tooshort.json", {
        "id": "rt-skillhub-2026-04-27-tooshort",
        "id_format_version": 2,
        "kind": "completion_notification",
        "notify_on_completion": False,
    })
    r = _run_close(p, "ack")  # 3 chars
    assert r.returncode != 0, "ack-close still requires >=10 chars"


def test_non_ack_close_still_rejects_acknowledged(tmp_path):
    """Regular WR closure (no kind=completion_notification): guard still fires."""
    p = _make_close_target(tmp_path, "wr-skillhub-2026-04-27-099.json", {
        "id": "wr-skillhub-2026-04-27-099",
        "id_format_version": 2,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
        "notify_on_completion": False,
    })
    r = _run_close(p, "Acknowledged but did nothing real.")
    assert r.returncode != 0, "non-ack-close 'Acknowledged' should still be rejected"


def test_ack_close_rejected_status_does_not_exempt(tmp_path):
    """Exemption applies only to processed|completed|resolved -- not rejected."""
    p = _make_close_target(tmp_path, "rt-2026-04-27-rejected.json", {
        "id": "rt-skillhub-2026-04-27-rejected",
        "id_format_version": 2,
        "kind": "completion_notification",
        "notify_on_completion": False,
    })
    r = _run_close(
        p,
        "Acknowledged but rejecting on merits.",
        status="rejected",
    )
    assert r.returncode != 0, "rejected status should still trigger startswith guard"
