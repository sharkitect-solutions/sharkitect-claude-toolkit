"""Tests for audit-hook-fires.py (CLI for empirical hook fire aggregation).

skip brainstorming -- spec is wr-skillhub-2026-05-15-001 recommended_fix;
user-authorized via the 2026-05-17 pending-items briefing (Category A
explicit user direction per Strict Bypass Vocabulary).

skip TDD -- characterization tests after spec-driven build; not strict
red-green-refactor. Acknowledged suboptimal; documented honestly.

Source: wr-skillhub-2026-05-15-001 (Skill Hub).
Companion to ~/.claude/hooks/log-hook-fire.py.

Test pyramid (per testing-strategy, project type=CLI tool):
  - Heavy unit layer: parse_iso, matcher_to_regex (trickiest function),
    enumerate_hooks (settings parsing), event_is_visible_in_tool_call_log.
  - Integration layer: end-to-end audit() against synthetic log + settings
    fixtures, plus CLI subprocess invocation to catch wiring breaks.

Patching:
  - module-level LOG_FILE and SETTINGS_FILE constants are monkey-patched
    so tests are hermetic and never touch the real home dir.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPT_PATH = Path(os.path.expanduser("~/.claude/scripts/audit-hook-fires.py"))


def _load_module():
    """Load audit-hook-fires.py as a module (its filename has a hyphen)."""
    spec = importlib.util.spec_from_file_location("audit_hook_fires", SCRIPT_PATH)
    assert spec and spec.loader, f"Could not load spec for {SCRIPT_PATH}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def m():
    return _load_module()


# ----------------------------------------------------------------------------
# Unit: parse_iso
# ----------------------------------------------------------------------------

def test_parse_iso_valid_with_z_suffix(m):
    dt = m.parse_iso("2026-05-17T12:00:00Z")
    assert dt is not None
    assert dt.tzinfo is not None
    assert dt.year == 2026 and dt.month == 5 and dt.day == 17


def test_parse_iso_valid_with_offset(m):
    dt = m.parse_iso("2026-05-17T12:00:00+00:00")
    assert dt is not None
    assert dt.year == 2026


def test_parse_iso_invalid_returns_none(m):
    assert m.parse_iso("not-a-date") is None
    assert m.parse_iso("") is None
    assert m.parse_iso(None) is None
    assert m.parse_iso(12345) is None


# ----------------------------------------------------------------------------
# Unit: matcher_to_regex
# ----------------------------------------------------------------------------

def test_matcher_wildcard_matches_everything(m):
    r = m.matcher_to_regex("*")
    assert r.match("Edit")
    assert r.match("Write")
    assert r.match("mcp__claude_ai_Supabase__execute_sql")


def test_matcher_empty_treated_as_wildcard(m):
    r = m.matcher_to_regex("")
    assert r.match("Edit")


def test_matcher_pipe_alternatives(m):
    r = m.matcher_to_regex("Edit|Write")
    assert r.match("Edit")
    assert r.match("Write")
    assert not r.match("Bash")
    assert not r.match("Read")


def test_matcher_mcp_prefix(m):
    r = m.matcher_to_regex("mcp__")
    assert r.match("mcp__claude_ai_Supabase__execute_sql")
    assert r.match("mcp__github-mcp__create_pull_request")
    assert not r.match("Edit")
    assert not r.match("Bash")


def test_matcher_regex_with_dot_star(m):
    r = m.matcher_to_regex("mcp__.*")
    assert r.match("mcp__anything")
    assert not r.match("Edit")


def test_matcher_pipe_with_regex_alternative(m):
    """Real-world: 'Edit|Write|TodoWrite|Bash|Skill|Read|mcp__.*'"""
    r = m.matcher_to_regex("Edit|Write|TodoWrite|Bash|Skill|Read|mcp__.*")
    assert r.match("Edit")
    assert r.match("TodoWrite")
    assert r.match("mcp__claude_ai_Supabase__execute_sql")
    assert not r.match("Glob")
    assert not r.match("Grep")


def test_matcher_bash_mcp_combined(m):
    """Real-world: 'Bash|mcp__'"""
    r = m.matcher_to_regex("Bash|mcp__")
    assert r.match("Bash")
    assert r.match("mcp__github_create")
    assert not r.match("Edit")


def test_matcher_malformed_regex_matches_nothing(m):
    """Bad regex should match NOTHING (safer than matching everything)."""
    r = m.matcher_to_regex("[unclosed-bracket")
    assert not r.match("Edit")
    assert not r.match("anything")


# ----------------------------------------------------------------------------
# Unit: event_is_visible_in_tool_call_log
# ----------------------------------------------------------------------------

def test_event_visibility(m):
    assert m.event_is_visible_in_tool_call_log("PreToolUse")
    assert m.event_is_visible_in_tool_call_log("PostToolUse")
    assert not m.event_is_visible_in_tool_call_log("SessionStart")
    assert not m.event_is_visible_in_tool_call_log("SessionEnd")
    assert not m.event_is_visible_in_tool_call_log("UserPromptSubmit")
    assert not m.event_is_visible_in_tool_call_log("Stop")
    assert not m.event_is_visible_in_tool_call_log("PreCompact")


# ----------------------------------------------------------------------------
# Unit: enumerate_hooks (settings.json parsing)
# ----------------------------------------------------------------------------

def test_enumerate_hooks_empty_settings(m):
    assert list(m.enumerate_hooks({})) == []
    assert list(m.enumerate_hooks({"hooks": {}})) == []
    assert list(m.enumerate_hooks(None)) == []


def test_enumerate_hooks_realistic_shape(m):
    settings = {
        "hooks": {
            "PreToolUse": [
                {"matcher": "Edit|Write", "hooks": [
                    {"type": "command", "command": 'python "/path/to/foo.py"'},
                    {"type": "command", "command": 'python "/path/to/bar.py"'},
                ]},
            ],
            "PostToolUse": [
                {"matcher": "*", "hooks": [
                    {"type": "command", "command": 'python "/path/to/baz.py"'},
                ]},
            ],
        }
    }
    out = list(m.enumerate_hooks(settings))
    assert len(out) == 3
    events = [e for e, _, _ in out]
    paths = [p for _, _, p in out]
    assert events.count("PreToolUse") == 2
    assert events.count("PostToolUse") == 1
    assert all(p.endswith(".py") for p in paths)


def test_enumerate_hooks_default_matcher_when_missing(m):
    settings = {"hooks": {"PreToolUse": [
        {"hooks": [{"type": "command", "command": 'python "/p/h.py"'}]},
    ]}}
    out = list(m.enumerate_hooks(settings))
    assert len(out) == 1
    _, matcher, _ = out[0]
    assert matcher == "*"


def test_enumerate_hooks_skips_unparseable_commands(m):
    settings = {"hooks": {"PreToolUse": [
        {"matcher": "*", "hooks": [
            {"type": "command", "command": "echo hello no path"},
            {"type": "command", "command": 'python "/p/real.py"'},
        ]},
    ]}}
    out = list(m.enumerate_hooks(settings))
    assert len(out) == 1
    assert out[0][2] == "/p/real.py"


def test_enumerate_hooks_skips_non_list_entries(m):
    settings = {"hooks": {"PreToolUse": "not-a-list"}}
    out = list(m.enumerate_hooks(settings))
    assert out == []


# ----------------------------------------------------------------------------
# Integration: audit() against synthetic log + settings
# ----------------------------------------------------------------------------

def _write_log(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _write_settings(path, settings):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings), encoding="utf-8")


@pytest.fixture
def patched_paths(m, tmp_path, monkeypatch):
    log_file = tmp_path / "hook-fire-log.jsonl"
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(m, "LOG_FILE", log_file)
    monkeypatch.setattr(m, "SETTINGS_FILE", settings_file)
    return log_file, settings_file


def test_audit_empty_log_returns_zero_counts(m, patched_paths):
    _, settings_file = patched_paths
    _write_settings(settings_file, {
        "hooks": {"PreToolUse": [
            {"matcher": "Edit|Write", "hooks": [
                {"command": 'python "/p/foo.py"'},
            ]},
        ]}
    })
    summary, meta = m.audit(window_days=90)
    assert meta["total_tool_calls_in_window"] == 0
    assert meta["log_exists"] is False
    assert len(summary) == 1
    assert summary[0]["inferred_fires"] == 0


def test_audit_counts_matching_tool_calls(m, patched_paths):
    log_file, settings_file = patched_paths
    now = datetime.now(timezone.utc)
    iso = now.isoformat().replace("+00:00", "Z")
    _write_log(log_file, [
        {"timestamp": iso, "tool_name": "Edit"},
        {"timestamp": iso, "tool_name": "Write"},
        {"timestamp": iso, "tool_name": "Bash"},
    ])
    _write_settings(settings_file, {
        "hooks": {
            "PreToolUse": [
                {"matcher": "Edit|Write", "hooks": [
                    {"command": 'python "/p/edit_write_hook.py"'},
                ]},
                {"matcher": "Bash", "hooks": [
                    {"command": 'python "/p/bash_hook.py"'},
                ]},
            ],
            "PostToolUse": [
                {"matcher": "*", "hooks": [
                    {"command": 'python "/p/star_hook.py"'},
                ]},
            ],
            "SessionStart": [
                {"matcher": "*", "hooks": [
                    {"command": 'python "/p/session_hook.py"'},
                ]},
            ],
        }
    })
    summary, meta = m.audit(window_days=90)
    assert meta["total_tool_calls_in_window"] == 3
    by_path = {s["hook_path"]: s for s in summary}
    assert by_path["/p/edit_write_hook.py"]["inferred_fires"] == 2
    assert by_path["/p/bash_hook.py"]["inferred_fires"] == 1
    assert by_path["/p/star_hook.py"]["inferred_fires"] == 3
    session = by_path["/p/session_hook.py"]
    assert session["inferred_fires"] is None
    assert "not-visible" in session["inference_kind"]


def test_audit_window_filters_old_entries(m, patched_paths):
    log_file, settings_file = patched_paths
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=120)
    recent = now - timedelta(days=10)
    _write_log(log_file, [
        {"timestamp": old.isoformat().replace("+00:00", "Z"), "tool_name": "Edit"},
        {"timestamp": recent.isoformat().replace("+00:00", "Z"), "tool_name": "Edit"},
    ])
    _write_settings(settings_file, {
        "hooks": {"PreToolUse": [
            {"matcher": "Edit", "hooks": [{"command": 'python "/p/h.py"'}]},
        ]}
    })
    summary, meta = m.audit(window_days=30)
    assert meta["total_tool_calls_in_window"] == 1
    assert summary[0]["inferred_fires"] == 1

    summary, meta = m.audit(window_days=200)
    assert meta["total_tool_calls_in_window"] == 2
    assert summary[0]["inferred_fires"] == 2


def test_audit_skips_malformed_log_lines(m, patched_paths):
    log_file, settings_file = patched_paths
    log_file.parent.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("not-json\n")
        f.write("\n")
        f.write(json.dumps({"timestamp": "bad-ts", "tool_name": "Edit"}) + "\n")
        f.write(json.dumps({"timestamp": now_iso, "tool_name": "Edit"}) + "\n")
    _write_settings(settings_file, {"hooks": {"PreToolUse": [
        {"matcher": "Edit", "hooks": [{"command": 'python "/p/h.py"'}]},
    ]}})
    summary, meta = m.audit(window_days=90)
    assert meta["total_tool_calls_in_window"] == 1
    assert summary[0]["inferred_fires"] == 1


def test_audit_zero_fire_candidate_identification(m, patched_paths):
    """Core use case: hook registered but log shows zero matching calls."""
    log_file, settings_file = patched_paths
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _write_log(log_file, [
        {"timestamp": now_iso, "tool_name": "Edit"},
        {"timestamp": now_iso, "tool_name": "Write"},
    ])
    _write_settings(settings_file, {"hooks": {"PreToolUse": [
        {"matcher": "Edit|Write", "hooks": [{"command": 'python "/p/active.py"'}]},
        {"matcher": "TodoWrite", "hooks": [{"command": 'python "/p/dead.py"'}]},
    ]}})
    summary, _ = m.audit(window_days=90)
    by_path = {s["hook_path"]: s["inferred_fires"] for s in summary}
    assert by_path["/p/active.py"] == 2
    assert by_path["/p/dead.py"] == 0


# ----------------------------------------------------------------------------
# Integration: CLI subprocess (catches wiring breaks)
# ----------------------------------------------------------------------------

def test_cli_json_output_is_valid_json():
    """End-to-end: --json emits valid JSON with expected top-level shape."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--window-days", "90", "--json"],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    parsed = json.loads(result.stdout)
    assert "meta" in parsed
    assert "hooks" in parsed
    assert isinstance(parsed["hooks"], list)
    assert "window_days" in parsed["meta"]


def test_cli_table_output_runs_cleanly():
    """End-to-end: default table output runs and emits expected header."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--window-days", "90"],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "HOOK FIRE AUDIT" in result.stdout
    assert "EVENT" in result.stdout
    assert "MATCHER" in result.stdout
