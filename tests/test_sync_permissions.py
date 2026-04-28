"""Tests for sync-permissions.py: read templates, write 4 settings.json with backup."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path.home() / ".claude" / "scripts" / "sync-permissions.py"


def _templates_fixture(tmp_path: Path) -> Path:
    t = {
        "schema_version": 1,
        "global_settings_path": str(tmp_path / "global-settings.json"),
        "global_permissions": {
            "allow_additions": ["Edit(~/.claude/rules/**)", "Edit(~/.claude/CLAUDE.md)"],
            "deny_additions": ["Edit(~/.claude/settings.json)"]
        },
        "workspaces": {
            "test-ws": {
                "settings_path": str(tmp_path / "test-ws-settings.json"),
                "deny_global_skill_hub_owned": ["Edit(~/.claude/rules/**)"],
                "deny_other_workspace_internals": [],
                "deny_inbox_direct_edit": [],
                "deny_other_workspace_human_action": []
            }
        }
    }
    p = tmp_path / "templates.json"
    p.write_text(json.dumps(t, indent=2), encoding="utf-8")
    return p


def _settings_fixture(path: Path, allow: list, deny: list) -> None:
    path.write_text(json.dumps({
        "permissions": {"allow": allow, "deny": deny}
    }, indent=2), encoding="utf-8")


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT)] + args,
                          capture_output=True, text=True, encoding="utf-8")


def test_dry_run_shows_diff_no_changes(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings, ["Bash(git status:*)"], [])

    r = _run(["--templates", str(templates), "--dry-run"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert "DRY RUN" in r.stdout or "dry run" in r.stdout.lower()
    assert "Edit(~/.claude/rules/**)" in r.stdout
    # File NOT modified
    data = json.loads(global_settings.read_text())
    assert data["permissions"]["allow"] == ["Bash(git status:*)"]


def test_execute_merges_additions_preserving_existing(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings,
                      ["Bash(git status:*)", "Bash(git push:*)"],
                      ["Bash(git push --force*)"])

    r = _run(["--templates", str(templates), "--execute"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(global_settings.read_text())
    assert "Bash(git status:*)" in data["permissions"]["allow"]
    assert "Bash(git push:*)" in data["permissions"]["allow"]
    assert "Bash(git push --force*)" in data["permissions"]["deny"]
    assert "Edit(~/.claude/rules/**)" in data["permissions"]["allow"]
    assert "Edit(~/.claude/settings.json)" in data["permissions"]["deny"]


def test_execute_creates_backup_before_write(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings, ["Bash(git status:*)"], [])

    r = _run(["--templates", str(templates), "--execute"])
    assert r.returncode == 0
    backups = list(global_settings.parent.glob("global-settings.json.bak.*"))
    assert len(backups) >= 1
    assert "Bash(git status:*)" in json.loads(backups[0].read_text())["permissions"]["allow"]


def test_idempotent_second_run_no_change(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings, ["Bash(git status:*)"], [])

    _run(["--templates", str(templates), "--execute"])
    after_first = global_settings.read_text()

    r = _run(["--templates", str(templates), "--execute"])
    assert r.returncode == 0
    assert global_settings.read_text() == after_first


def test_workspace_settings_creates_if_missing(tmp_path: Path):
    templates = _templates_fixture(tmp_path)
    global_settings = tmp_path / "global-settings.json"
    _settings_fixture(global_settings, [], [])
    workspace_settings = tmp_path / "test-ws-settings.json"
    assert not workspace_settings.exists()

    r = _run(["--templates", str(templates), "--execute"])
    assert r.returncode == 0
    assert workspace_settings.exists()
    data = json.loads(workspace_settings.read_text())
    assert "Edit(~/.claude/rules/**)" in data["permissions"]["deny"]


def test_invalid_json_in_templates_aborts(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json {", encoding="utf-8")
    r = _run(["--templates", str(bad), "--execute"])
    assert r.returncode != 0
