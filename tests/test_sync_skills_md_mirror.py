"""Tests for sync-skills.py markdown-directory mirror functions.

Source: wr-sentinel-2026-05-20-001 (sync ~/.claude/plans/ + ~/.claude/docs/).

These tests are written BEFORE the implementation is re-added — RED phase first
per superpowers:test-driven-development. Initial run must fail with
AttributeError on the absent functions.

After GREEN: tests serve as regression protection for any future modifications
to the markdown-mirror behavior.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
from pathlib import Path


SYNC_SKILLS_PATH = Path(os.path.expanduser(
    "~/Documents/Claude Code Workspaces/3.- Skill Management Hub/tools/sync-skills.py"
))


def _load_sync_skills():
    """Load the sync-skills.py module via importlib (hyphen in filename)."""
    spec = importlib.util.spec_from_file_location("sync_skills", SYNC_SKILLS_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {SYNC_SKILLS_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ----------------------------------------------------------------------------
# get_plans_dir / get_docs_dir
# ----------------------------------------------------------------------------

def test_get_plans_dir_points_to_claude_plans():
    """get_plans_dir() returns ~/.claude/plans/ — session-load-bearing path."""
    mod = _load_sync_skills()
    result = mod.get_plans_dir()
    assert result == Path.home() / ".claude" / "plans"


def test_get_docs_dir_points_to_claude_docs():
    """get_docs_dir() returns ~/.claude/docs/ — plans-registry.md lives here."""
    mod = _load_sync_skills()
    result = mod.get_docs_dir()
    assert result == Path.home() / ".claude" / "docs"


def test_get_repo_plans_dir_creates_and_returns_toolkit_path(tmp_path, monkeypatch):
    """get_repo_plans_dir() finds and creates the toolkit plans/ dir."""
    mod = _load_sync_skills()
    # Real call should return the project's toolkit/plans/ dir
    result = mod.get_repo_plans_dir()
    assert result is not None
    assert result.exists()
    assert result.name == "plans"
    assert result.parent.name == "sharkitect-claude-toolkit"


def test_get_repo_docs_dir_creates_and_returns_toolkit_path():
    """get_repo_docs_dir() finds and creates the toolkit docs/ dir."""
    mod = _load_sync_skills()
    result = mod.get_repo_docs_dir()
    assert result is not None
    assert result.exists()
    assert result.name == "docs"
    assert result.parent.name == "sharkitect-claude-toolkit"


# ----------------------------------------------------------------------------
# compare_md_dir
# ----------------------------------------------------------------------------

def test_compare_md_dir_detects_new_files(tmp_path):
    """Files in live but not in repo go to diff['new']."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    _write(live / "new1.md", "content1")
    _write(live / "new2.md", "content2")
    repo.mkdir()
    mod = _load_sync_skills()
    diff = mod.compare_md_dir(live, repo)
    assert sorted(diff["new"]) == ["new1.md", "new2.md"]
    assert diff["modified"] == []
    assert diff["deleted"] == []
    assert diff["live_total"] == 2
    assert diff["repo_total"] == 0


def test_compare_md_dir_detects_modified_files_via_hash(tmp_path):
    """Same filename in both, different content (hash differs) -> diff['modified']."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    _write(live / "same.md", "live content (newer)")
    _write(repo / "same.md", "repo content (older)")
    mod = _load_sync_skills()
    diff = mod.compare_md_dir(live, repo)
    assert diff["new"] == []
    assert diff["modified"] == ["same.md"]
    assert diff["deleted"] == []


def test_compare_md_dir_unchanged_files_not_in_modified(tmp_path):
    """Identical content in both -> NOT in modified; counted in live_total/repo_total."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    same_content = "identical content"
    _write(live / "stable.md", same_content)
    _write(repo / "stable.md", same_content)
    mod = _load_sync_skills()
    diff = mod.compare_md_dir(live, repo)
    assert diff["new"] == []
    assert diff["modified"] == []
    assert diff["deleted"] == []
    assert "stable.md" in diff["unchanged"]


def test_compare_md_dir_detects_deleted_files(tmp_path):
    """File in repo but not in live goes to diff['deleted'] (mirror should remove it)."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    live.mkdir()
    _write(repo / "gone.md", "stale content")
    mod = _load_sync_skills()
    diff = mod.compare_md_dir(live, repo)
    assert diff["new"] == []
    assert diff["modified"] == []
    assert diff["deleted"] == ["gone.md"]


def test_compare_md_dir_recurses_into_subdirs(tmp_path):
    """Files at depth>1 (e.g. plans/archive/foo.md) are detected and use forward-slash keys."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    _write(live / "top.md", "top")
    _write(live / "archive" / "old.md", "archived")
    _write(live / "archive" / "deep" / "older.md", "very old")
    repo.mkdir()
    mod = _load_sync_skills()
    diff = mod.compare_md_dir(live, repo)
    # Keys use forward slashes regardless of OS
    assert sorted(diff["new"]) == [
        "archive/deep/older.md",
        "archive/old.md",
        "top.md",
    ]


def test_compare_md_dir_excludes_non_markdown_files(tmp_path):
    """Only .md files are mirrored; .py / .json / .txt are excluded."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    _write(live / "keep.md", "yes")
    _write(live / "script.py", "no")
    _write(live / "data.json", "no")
    _write(live / "notes.txt", "no")
    repo.mkdir()
    mod = _load_sync_skills()
    diff = mod.compare_md_dir(live, repo)
    assert diff["new"] == ["keep.md"]


def test_compare_md_dir_excludes_dot_directories(tmp_path):
    """Files under .git/ / .hidden/ / __pycache__/ are excluded."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    _write(live / "visible.md", "yes")
    _write(live / ".git" / "objects" / "abc.md", "no")
    _write(live / ".hidden" / "secret.md", "no")
    _write(live / "__pycache__" / "compiled.md", "no")
    repo.mkdir()
    mod = _load_sync_skills()
    diff = mod.compare_md_dir(live, repo)
    assert diff["new"] == ["visible.md"]


def test_compare_md_dir_empty_live_dir(tmp_path):
    """Empty live dir + populated repo = everything goes to 'deleted'."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    live.mkdir()
    _write(repo / "a.md", "a")
    _write(repo / "b.md", "b")
    mod = _load_sync_skills()
    diff = mod.compare_md_dir(live, repo)
    assert diff["new"] == []
    assert sorted(diff["deleted"]) == ["a.md", "b.md"]


def test_compare_md_dir_missing_repo_dir(tmp_path):
    """Live dir exists but repo doesn't yet — all live files are 'new'."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"  # NOT created
    _write(live / "first.md", "first sync")
    mod = _load_sync_skills()
    diff = mod.compare_md_dir(live, repo)
    assert diff["new"] == ["first.md"]
    assert diff["repo_total"] == 0


# ----------------------------------------------------------------------------
# sync_md_dir
# ----------------------------------------------------------------------------

def test_sync_md_dir_copies_new_files(tmp_path):
    """diff['new'] entries get copied live -> repo; actions list shows ADDED."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    _write(live / "new.md", "new content")
    repo.mkdir()
    diff = {"new": ["new.md"], "modified": [], "deleted": []}
    mod = _load_sync_skills()
    actions = mod.sync_md_dir(live, repo, diff, "plans")
    assert (repo / "new.md").exists()
    assert (repo / "new.md").read_text(encoding="utf-8") == "new content"
    assert any("ADDED" in a and "plans/new.md" in a for a in actions)


def test_sync_md_dir_overwrites_modified_files(tmp_path):
    """diff['modified'] entries get overwritten with live content; actions show UPDATED."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    _write(live / "same.md", "NEW CONTENT")
    _write(repo / "same.md", "old content")
    diff = {"new": [], "modified": ["same.md"], "deleted": []}
    mod = _load_sync_skills()
    actions = mod.sync_md_dir(live, repo, diff, "docs")
    assert (repo / "same.md").read_text(encoding="utf-8") == "NEW CONTENT"
    assert any("UPDATED" in a and "docs/same.md" in a for a in actions)


def test_sync_md_dir_removes_deleted_files(tmp_path):
    """diff['deleted'] entries get unlinked from repo; actions show REMOVED."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    live.mkdir()
    _write(repo / "stale.md", "should be removed")
    diff = {"new": [], "modified": [], "deleted": ["stale.md"]}
    mod = _load_sync_skills()
    actions = mod.sync_md_dir(live, repo, diff, "plans")
    assert not (repo / "stale.md").exists()
    assert any("REMOVED" in a and "plans/stale.md" in a for a in actions)


def test_sync_md_dir_preserves_subdir_structure(tmp_path):
    """Nested paths (e.g. plans/archive/foo.md) get copied with parent dirs created."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    _write(live / "archive" / "deep" / "old.md", "archived content")
    repo.mkdir()
    diff = {"new": ["archive/deep/old.md"], "modified": [], "deleted": []}
    mod = _load_sync_skills()
    actions = mod.sync_md_dir(live, repo, diff, "plans")
    dst = repo / "archive" / "deep" / "old.md"
    assert dst.exists()
    assert dst.read_text(encoding="utf-8") == "archived content"


def test_sync_md_dir_cleans_empty_parents_on_delete(tmp_path):
    """When a deleted file leaves its parent dir empty, the parent is removed too.
    Mirrors sync_scripts cleanup behavior."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    live.mkdir()
    _write(repo / "archive" / "old" / "stale.md", "stale")
    diff = {"new": [], "modified": [], "deleted": ["archive/old/stale.md"]}
    mod = _load_sync_skills()
    mod.sync_md_dir(live, repo, diff, "plans")
    assert not (repo / "archive" / "old" / "stale.md").exists()
    # Empty parent should be cleaned up
    assert not (repo / "archive" / "old").exists()
    # But repo root itself stays
    assert repo.exists()


def test_sync_md_dir_label_appears_in_action_log(tmp_path):
    """The `label` arg (e.g. 'plans' or 'docs') appears in the action strings."""
    live = tmp_path / "live"
    repo = tmp_path / "repo"
    _write(live / "x.md", "x")
    repo.mkdir()
    diff = {"new": ["x.md"], "modified": [], "deleted": []}
    mod = _load_sync_skills()
    actions = mod.sync_md_dir(live, repo, diff, "MYLABEL")
    assert any("MYLABEL/x.md" in a for a in actions)
