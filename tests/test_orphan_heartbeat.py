"""Tests for orphan-cleanup heartbeat protection layer.

Spec: 4.- Sentinel/docs/specs/spec-orphan-cleanup-heartbeat.md (v1.0 APPROVED 2026-05-20)
WR:   2026-05-20_sentinel_session-heartbeat-as-third-pro-002 (severity=critical)

12 tests per spec section 9 test matrix.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

CHECK_PATH = Path(os.path.expanduser("~/.claude/scripts/check-orphan-claude-processes.py"))
KILL_PATH = Path(os.path.expanduser("~/.claude/scripts/kill-orphan-claude-processes.py"))
REFRESH_HOOK_PATH = Path(os.path.expanduser("~/.claude/hooks/user-prompt-heartbeat-refresh.py"))
REGISTER_HOOK_PATH = Path(os.path.expanduser("~/.claude/hooks/session-start-register-pid.py"))


def _load(path: Path, modname: str):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_proc(pid, age_hours):
    """Construct a process dict shaped like get_claude_processes() output."""
    now = datetime.now(timezone.utc)
    return {
        "pid": pid,
        "created_at": now - timedelta(hours=age_hours),
        "working_set_bytes": 100 * 1024 * 1024,
    }


# ----------------------------------------------------------------------------
# Group A: Classifier (tests 1-6)
# ----------------------------------------------------------------------------

def test_01_fresh_heartbeat_protects_any_age():
    """Fresh heartbeat alone protects regardless of age (spec test 1)."""
    check = _load(CHECK_PATH, "check_orphan")
    procs = [_make_proc(pid=12345, age_hours=100)]
    heartbeat = {
        12345: {
            "pid": 12345,
            "last_refresh": datetime.now(timezone.utc).isoformat(),
            "refresh_count": 50,
        }
    }
    report = check.classify_processes(
        procs, current_pid=None, threshold_hours=8.0,
        _ancestor_lookup=lambda pid: (None, None),
        _registry_reader=lambda: {},
        _heartbeat_reader=lambda pid: heartbeat.get(pid),
    )
    assert len(report["orphan_suspects"]) == 0
    assert len(report["protected"]) == 1
    assert "heartbeat" in report["protected"][0]["protection"].lower()


def test_02_stale_heartbeat_live_vscode_protects():
    """Stale heartbeat + live VS Code ancestor -> protected (spec test 2)."""
    check = _load(CHECK_PATH, "check_orphan")
    procs = [_make_proc(pid=12345, age_hours=14)]
    stale_ts = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()
    # Lookup returns (name_lower, ppid) for each pid as the walker climbs.
    # Tree: claude.exe (12345) -> code.exe (999) [VS Code variant found]
    tree = {12345: ("claude.exe", 999), 999: ("code.exe", 0)}
    report = check.classify_processes(
        procs, current_pid=None, threshold_hours=8.0,
        _ancestor_lookup=lambda pid: tree.get(pid, (None, None)),
        _registry_reader=lambda: {},
        _heartbeat_reader=lambda pid: {"pid": 12345, "last_refresh": stale_ts, "refresh_count": 5},
    )
    assert len(report["orphan_suspects"]) == 0
    assert len(report["protected"]) == 1


def test_03_stale_heartbeat_dead_vscode_registered_protects():
    """Stale heartbeat + dead VS Code + registered session -> protected (spec test 3)."""
    check = _load(CHECK_PATH, "check_orphan")
    procs = [_make_proc(pid=12345, age_hours=14)]
    stale_ts = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()
    report = check.classify_processes(
        procs, current_pid=None, threshold_hours=8.0,
        _ancestor_lookup=lambda pid: (None, None),
        _registry_reader=lambda: {12345: {"workspace": "test"}},
        _heartbeat_reader=lambda pid: {"pid": 12345, "last_refresh": stale_ts, "refresh_count": 5},
    )
    assert len(report["orphan_suspects"]) == 0
    assert len(report["protected"]) == 1


def test_04_true_orphan_all_signals_fail():
    """All three signals fail + age >= 8h -> orphan_suspect (spec test 4)."""
    check = _load(CHECK_PATH, "check_orphan")
    procs = [_make_proc(pid=12345, age_hours=14)]
    stale_ts = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()
    report = check.classify_processes(
        procs, current_pid=None, threshold_hours=8.0,
        _ancestor_lookup=lambda pid: (None, None),
        _registry_reader=lambda: {},
        _heartbeat_reader=lambda pid: {"pid": 12345, "last_refresh": stale_ts, "refresh_count": 5},
    )
    assert len(report["orphan_suspects"]) == 1
    assert report["orphan_suspects"][0]["pid"] == 12345


def test_05_age_below_threshold_is_recent():
    """Age < 8h with all signals failing -> recent (spec test 5)."""
    check = _load(CHECK_PATH, "check_orphan")
    procs = [_make_proc(pid=12345, age_hours=4)]
    report = check.classify_processes(
        procs, current_pid=None, threshold_hours=8.0,
        _ancestor_lookup=lambda pid: (None, None),
        _registry_reader=lambda: {},
        _heartbeat_reader=lambda pid: None,
    )
    assert len(report["orphan_suspects"]) == 0
    assert len(report["recent"]) == 1


def test_06_corrupt_heartbeat_treated_as_missing(tmp_path, monkeypatch):
    """Corrupt heartbeat JSON -> treated as missing, fail-safe (spec test 6)."""
    check = _load(CHECK_PATH, "check_orphan")
    hb_dir = tmp_path / "session-heartbeats"
    hb_dir.mkdir()
    (hb_dir / "12345.json").write_text("not json{}", encoding="utf-8")
    monkeypatch.setattr(check, "HEARTBEAT_DIR", hb_dir)
    result = check.read_session_heartbeat(12345)
    assert result is None


# ----------------------------------------------------------------------------
# Group B: Kill script modes (tests 7-8)
# ----------------------------------------------------------------------------

def test_07_report_only_writes_report_kills_nothing(tmp_path, monkeypatch):
    """--report-only writes report, kills nothing (spec test 7)."""
    kill = _load(KILL_PATH, "kill_orphan")
    monkeypatch.setattr(kill, "REPORT_DIR", tmp_path)
    fake_report = {
        "orphan_suspects": [{
            "pid": 12345, "age_hours": 14.2, "mb": 480,
            "created_at": "2026-05-20T13:35:00Z",
        }],
        "total": 1, "threshold_hours": 8.0, "current": None,
        "recent": [], "protected": [],
    }
    monkeypatch.setattr(kill, "_classify_for_kill",
                        lambda threshold_hours: (fake_report, 99999))
    killed_calls = []
    monkeypatch.setattr(kill, "kill_pid",
                        lambda pid: killed_calls.append(pid) or ("killed", "ok"))
    rc = kill.run_report_only(threshold_hours=8.0)
    assert rc == 0
    assert killed_calls == []
    reports = list(tmp_path.glob("report-*.json"))
    assert len(reports) == 1
    data = json.loads(reports[0].read_text(encoding="utf-8"))
    assert data["status"] == "pending_operator_review"
    assert len(data["candidates"]) == 1
    assert data["candidates"][0]["pid"] == 12345


def test_08_from_report_skips_recovered_heartbeat(tmp_path, monkeypatch):
    """--from-report skips PIDs whose heartbeat refreshed since report (spec test 8)."""
    kill = _load(KILL_PATH, "kill_orphan")
    monkeypatch.setattr(kill, "REPORT_DIR", tmp_path)
    report_path = tmp_path / "report-test.json"
    report_path.write_text(json.dumps({
        "report_id": "report-test",
        "generated_at": "2026-05-20T03:00:00Z",
        "threshold_hours": 8.0,
        "candidates": [{"pid": 12345, "age_hours": 14.0, "evidence": {}}],
        "status": "pending_operator_review",
    }), encoding="utf-8")
    # At execute time, classifier shows PID 12345 as protected (fresh heartbeat)
    protected_report = {
        "orphan_suspects": [],
        "protected": [{"pid": 12345, "age_hours": 14.0,
                       "protection": "heartbeat:fresh"}],
        "recent": [], "total": 1, "threshold_hours": 8.0, "current": None,
    }
    monkeypatch.setattr(kill, "_classify_for_kill",
                        lambda threshold_hours: (protected_report, 99999))
    killed_calls = []
    monkeypatch.setattr(kill, "kill_pid",
                        lambda pid: killed_calls.append(pid) or ("killed", "ok"))
    rc = kill.run_from_report(report_path, threshold_hours=8.0)
    assert rc == 0
    assert killed_calls == []
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["status"] == "executed"
    pid_entry = next(c for c in data["candidates"] if c["pid"] == 12345)
    assert pid_entry["result"] == "protection_recovered"


# ----------------------------------------------------------------------------
# Group C: Heartbeat hook (tests 9-11)
# ----------------------------------------------------------------------------

def test_09_refresh_hook_creates_heartbeat_when_missing(tmp_path, monkeypatch):
    """Refresh hook creates fresh heartbeat if file missing (spec test 9)."""
    assert REFRESH_HOOK_PATH.exists(), "user-prompt-heartbeat-refresh.py must exist"
    refresh = _load(REFRESH_HOOK_PATH, "refresh_hook")
    monkeypatch.setattr(refresh, "HEARTBEAT_DIR", tmp_path)
    monkeypatch.setattr(refresh, "find_claude_exe_pid", lambda: 12345)
    refresh.refresh_heartbeat()
    hb_file = tmp_path / "12345.json"
    assert hb_file.exists()
    data = json.loads(hb_file.read_text(encoding="utf-8"))
    assert data["pid"] == 12345
    assert data["refresh_count"] == 1
    assert "last_refresh" in data
    assert "first_seen" in data


def test_10_atomic_write_never_partial(tmp_path, monkeypatch):
    """Concurrent reader never observes partial-write file (spec test 10)."""
    refresh = _load(REFRESH_HOOK_PATH, "refresh_hook")
    monkeypatch.setattr(refresh, "HEARTBEAT_DIR", tmp_path)
    monkeypatch.setattr(refresh, "find_claude_exe_pid", lambda: 12345)
    refresh.refresh_heartbeat()
    hb_file = tmp_path / "12345.json"

    errors = []
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            try:
                content = hb_file.read_text(encoding="utf-8")
                if content:
                    json.loads(content)
            except json.JSONDecodeError:
                errors.append("partial JSON observed")
            except (FileNotFoundError, PermissionError):
                # File momentarily missing or briefly locked during rename is
                # acceptable on Windows; production read_session_heartbeat
                # treats this as a missing-heartbeat (fail-safe to other signals).
                pass
            time.sleep(0.0005)

    t = threading.Thread(target=reader)
    t.start()
    try:
        for _ in range(100):
            refresh.refresh_heartbeat()
    finally:
        stop.set()
        t.join(timeout=2)
    assert errors == [], f"observed partial writes: {errors}"


def test_11_cleanup_removes_dead_pid_heartbeats(tmp_path, monkeypatch):
    """prune_dead_heartbeats removes heartbeat files for dead PIDs (spec test 11)."""
    register = _load(REGISTER_HOOK_PATH, "register_hook")
    monkeypatch.setattr(register, "HEARTBEAT_DIR", tmp_path)
    (tmp_path / "1111.json").write_text("{}", encoding="utf-8")
    (tmp_path / "2222.json").write_text("{}", encoding="utf-8")
    (tmp_path / "3333.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(register, "is_pid_alive", lambda pid: pid == 2222)
    register.prune_dead_heartbeats()
    assert not (tmp_path / "1111.json").exists()
    assert (tmp_path / "2222.json").exists()
    assert not (tmp_path / "3333.json").exists()


# ----------------------------------------------------------------------------
# Group D: Report archive (test 12)
# ----------------------------------------------------------------------------

def test_12_archives_stale_unprocessed_reports(tmp_path, monkeypatch):
    """Reports 14+ days old with no current-eligible candidates auto-archive (spec test 12)."""
    kill = _load(KILL_PATH, "kill_orphan")
    monkeypatch.setattr(kill, "REPORT_DIR", tmp_path)
    archive_dir = tmp_path / "archive"
    monkeypatch.setattr(kill, "REPORT_ARCHIVE_DIR", archive_dir)
    old_report = tmp_path / "report-old.json"
    old_report.write_text(json.dumps({
        "report_id": "report-old",
        "generated_at": "2026-05-05T00:00:00Z",
        "candidates": [{"pid": 99999, "age_hours": 100}],
        "status": "pending_operator_review",
    }), encoding="utf-8")
    old_time = (datetime.now(timezone.utc) - timedelta(days=15)).timestamp()
    os.utime(old_report, (old_time, old_time))
    # Classifier sees no eligible candidates (PID 99999 not alive anymore)
    empty_report = {
        "orphan_suspects": [], "protected": [], "recent": [],
        "total": 0, "threshold_hours": 8.0, "current": None,
    }
    monkeypatch.setattr(kill, "_classify_for_kill",
                        lambda threshold_hours: (empty_report, 99999))
    kill.archive_stale_reports()
    assert not old_report.exists()
    assert (archive_dir / "report-old.json").exists()
