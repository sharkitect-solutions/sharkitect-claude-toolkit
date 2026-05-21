"""Regression test for session-startup-guard.py plugin restore filtering of
.orphaned_at marker files.

Source incident:
  S65 plugin poison cycle (2026-05-20). When CC auto-update wiped
  ~/.claude/plugins/cache/local/, the startup-guard restored plugins from the
  toolkit backup. If the toolkit was ever poisoned (CC having written
  .orphaned_at markers into a prior live tree, which then got mirrored into
  the toolkit by sync-skills.py), the restore re-introduced the markers and
  CC's plugin manager deleted the plugins again within minutes. 41-day silent
  cycle.

Fix:
  Sync-skills now refuses to mirror markers (Guard #2). This Guard #1 is the
  defense-in-depth layer: if the toolkit is EVER poisoned (manual error, an
  unrelated sync path, restoring from an older backup, third-party clone of
  the repo), the restore must still deliver a poison-free tree.

The startup-guard exposes a helper _restore_plugin_tree(src, dst) that does
shutil.copytree with ignore=ignore_patterns('.orphaned_at'). This test pins
that behavior so any future refactor (e.g., switching to a different copy
strategy) cannot silently regress.

Tests RED before the helper exists, GREEN after.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_guard_mod():
    src = Path.home() / ".claude" / "hooks" / "session-startup-guard.py"
    assert src.exists(), f"session-startup-guard.py not found at {src}"
    spec = importlib.util.spec_from_file_location("startup_guard_mod", str(src))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _marker_files(root: Path):
    if not root.exists():
        return []
    return list(root.rglob(".orphaned_at"))


def _build_poisoned_plugin(plugin: Path):
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / "hooks").mkdir()
    (plugin / "scripts").mkdir()
    (plugin / "manifest.json").write_text('{"v":1}', encoding="utf-8")
    (plugin / "hooks" / "ok.py").write_text("# ok\n", encoding="utf-8")
    (plugin / ".claude-plugin" / ".orphaned_at").write_text("2026-05-20", encoding="utf-8")
    (plugin / "hooks" / ".orphaned_at").write_text("2026-05-20", encoding="utf-8")
    (plugin / "scripts" / ".orphaned_at").write_text("2026-05-20", encoding="utf-8")


def test_restore_helper_strips_orphaned_at_markers(tmp_path):
    """The restore helper must drop every .orphaned_at marker from the copy."""
    mod = _load_guard_mod()
    assert hasattr(mod, "_restore_plugin_tree"), (
        "session-startup-guard.py must expose _restore_plugin_tree(src, dst) "
        "as the canonical plugin restore helper"
    )

    src = tmp_path / "toolkit" / "aios-core"
    dst = tmp_path / "live" / "aios-core"
    _build_poisoned_plugin(src)

    mod._restore_plugin_tree(src, dst)

    # Real content arrived
    assert (dst / "manifest.json").exists()
    assert (dst / "hooks" / "ok.py").exists()
    # Poison did not
    leftover = _marker_files(dst)
    assert leftover == [], f"restore leaked .orphaned_at markers: {leftover}"


def test_restore_helper_deep_marker_excluded(tmp_path):
    """Deep markers (any depth) must also be excluded."""
    mod = _load_guard_mod()
    src = tmp_path / "toolkit" / "phase-gate"
    dst = tmp_path / "live" / "phase-gate"
    (src / "deep" / "nested" / "path").mkdir(parents=True)
    (src / "deep" / "nested" / "path" / ".orphaned_at").write_text("x", encoding="utf-8")
    (src / "manifest.json").write_text('{}', encoding="utf-8")

    mod._restore_plugin_tree(src, dst)

    leftover = _marker_files(dst)
    assert leftover == [], f"deep marker leaked: {leftover}"


def test_restore_helper_clean_input_still_works(tmp_path):
    """A poison-free toolkit plugin must still be copied as before."""
    mod = _load_guard_mod()
    src = tmp_path / "toolkit" / "clean-plugin"
    dst = tmp_path / "live" / "clean-plugin"
    src.mkdir(parents=True)
    (src / "manifest.json").write_text('{"v":1}', encoding="utf-8")
    (src / "hooks").mkdir()
    (src / "hooks" / "h.py").write_text("# h\n", encoding="utf-8")

    mod._restore_plugin_tree(src, dst)

    assert (dst / "manifest.json").exists()
    assert (dst / "hooks" / "h.py").exists()


def test_check_plugin_integrity_uses_helper(monkeypatch, tmp_path):
    """End-to-end: when check_plugin_integrity restores a poisoned toolkit
    plugin, the resulting cache/local tree must be poison-free."""
    mod = _load_guard_mod()

    # Fake home so plugins/ and cache/local/ live under tmp_path
    fake_home = tmp_path / "home"
    plugins_dir = fake_home / ".claude" / "plugins"
    cache_local = plugins_dir / "cache" / "local"
    cache_local.mkdir(parents=True)
    installed = plugins_dir / "installed_plugins.json"
    installed.write_text(
        '{"plugins":{"aios-core@local":{}}}',
        encoding="utf-8",
    )

    # Fake toolkit backup under SKILL_HUB_ROOT/sharkitect-claude-toolkit/custom-plugins
    fake_toolkit = tmp_path / "skillhub" / "sharkitect-claude-toolkit" / "custom-plugins"
    _build_poisoned_plugin(fake_toolkit / "aios-core")

    monkeypatch.setattr(mod.Path, "home", classmethod(lambda _cls: fake_home))
    monkeypatch.setattr(mod, "SKILL_HUB_ROOT", tmp_path / "skillhub")

    status, restored, missing = mod.check_plugin_integrity()

    assert "aios-core" in restored, (status, restored, missing)
    restored_path = cache_local / "aios-core"
    assert restored_path.exists()
    assert (restored_path / "manifest.json").exists()
    leftover = _marker_files(restored_path)
    assert leftover == [], (
        f"check_plugin_integrity leaked markers from toolkit -> cache/local: {leftover}"
    )
