"""Tests for sync-permissions.py: read templates, write 4 settings.json with backup."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


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
    backups = list(global_settings.parent.glob("global-settings.json.bak.*"))
    assert len(backups) == 1, f"expected exactly one backup after idempotent run, got {len(backups)}"


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


def test_templates_file_not_found_returns_2(tmp_path: Path):
    nonexistent = tmp_path / "does-not-exist.json"
    r = _run(["--templates", str(nonexistent), "--execute"])
    assert r.returncode == 2
    assert "Templates not found" in r.stderr or "not found" in r.stderr.lower()


def test_validate_templates_catches_missing_keys(tmp_path: Path):
    bad = tmp_path / "bad-templates.json"
    bad.write_text(json.dumps({
        "schema_version": 1,
        # missing global_settings_path AND global_permissions entirely
    }), encoding="utf-8")
    r = _run(["--templates", str(bad), "--execute"])
    assert r.returncode == 3, f"stderr: {r.stderr}"
    assert "Template validation failed" in r.stderr
    assert "global_settings_path" in r.stderr


def test_expand_path_translates_posix_drive_letter_on_windows():
    """Regression: Path('//c/Users/...').resolve() interprets as UNC on Windows.
    _expand_path must convert //c/Users/... to c:/Users/... before resolve.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("sync_permissions", str(SCRIPT))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if sys.platform == "win32":
        result = mod._expand_path("//c/Users/Sharkitect Digital/Documents/test")
        # On Windows, must be drive-letter form, not UNC
        assert str(result).startswith("C:") or str(result).startswith("c:"), \
            f"expected C:/ prefix, got {result}"
        assert "\\\\" not in str(result)[:2], f"path resolved as UNC: {result}"
    else:
        # On POSIX, leave as-is; //c/... is just a regular path
        result = mod._expand_path("//c/foo")
        assert str(result).endswith("/c/foo") or "c/foo" in str(result)
