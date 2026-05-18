"""Tests for _dispatchers/methodology/scope_discipline.py (Phase 2 Build #2B).

Strict 1:1 behavior preservation of workspace-scope-guard.py wrapped in
evaluate(payload). Returns:

  None                                  -> sub-rule did not trigger / pass-through
  {"advisory": "<text>"}                -> ADVISORY (additionalContext)

Source behavior preserved:
  Layer 1: Workspace-specific STRUCTURAL forbidden self-paths (e.g. Skill Hub
    writing to its own .routed-tasks/ -- the workspace does not own that
    directory structure).
  Layer 2: TARGET-side structural forbidden paths regardless of source
    workspace (e.g. anyone writing to Skill Hub's .routed-tasks/).
  Layer 3: ALWAYS_ALLOWED exemptions (.routed-tasks/, .lifecycle-reviews/,
    /.claude/rules/, /.claude/scripts/, memory/, .tmp/, etc.).
  Layer 4: Protocol-sanctioned cross-workspace writes (.work-requests/inbox/
    new file, blocker_cleared_notes append).
  Layer 5: Cross-workspace SCOPE_VIOLATIONS (HQ writing skills, Sentinel
    writing client deliverables, etc.).

Part C-4 anti-drift / fortification / bilateral additions are DEFERRED to
Build 6 per spec section C.4. This sub-rule is the pure source-lift.

Spec: docs/superpowers/specs/2026-05-15-phase-2-architecture-spec.md (Part A)
"""
from __future__ import annotations

import os
import sys

import pytest

# Make hooks/ importable for the _dispatchers package
HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


def _payload(tool_name, tool_input):
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
    }


# Canonical CWDs that match source workspace detection regex
SKILL_HUB_CWD = "C:/Users/User/Claude Code Workspaces/3.- Skill Management Hub"
HQ_CWD = "C:/Users/User/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ"
SENTINEL_CWD = "C:/Users/User/Claude Code Workspaces/4.- Sentinel"


# ---------------------------------------------------------------------------
# Layer 1: workspace-specific STRUCTURAL forbidden self-paths
# ---------------------------------------------------------------------------

class TestScopeDisciplineForbiddenSelfPaths:
    def test_skill_hub_writing_own_routed_tasks_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.chdir(SKILL_HUB_CWD if os.path.isdir(SKILL_HUB_CWD) else os.getcwd())
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: SKILL_HUB_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": SKILL_HUB_CWD + "/.routed-tasks/inbox/rt-x.json",
             "content": "{}"},
        ))
        assert result is not None
        assert "advisory" in result
        assert "Skill Hub has no .routed-tasks/" in result["advisory"] or "STRUCTURE VIOLATION" in result["advisory"]

    def test_hq_writing_own_work_requests_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": HQ_CWD + "/.work-requests/inbox/wr-x.json",
             "content": "{}"},
        ))
        assert result is not None
        assert "advisory" in result
        assert ".work-requests/" in result["advisory"]

    def test_sentinel_writing_own_work_requests_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: SENTINEL_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": SENTINEL_CWD + "/.work-requests/inbox/wr-x.json",
             "content": "{}"},
        ))
        assert result is not None
        assert "advisory" in result
        assert ".work-requests/" in result["advisory"]


# ---------------------------------------------------------------------------
# Layer 2: TARGET-side structural forbidden (regardless of source workspace)
# ---------------------------------------------------------------------------

class TestScopeDisciplineTargetForbidden:
    def test_writing_to_skill_hub_routed_tasks_from_anywhere_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        # Use the canonical path pattern source matches against
        target = "/3.- Skill Management Hub/.routed-tasks/inbox/rt-x.json"
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": target, "content": "{}"},
        ))
        assert result is not None
        assert "advisory" in result
        assert "TARGET WORKSPACE STRUCTURE VIOLATION" in result["advisory"]
        assert ".work-requests/inbox/" in result["advisory"]  # redirect mentioned

    def test_writing_to_hq_work_requests_from_anywhere_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: SKILL_HUB_CWD)
        target = "/1.- SHARKITECT DIGITAL WORKFORCE HQ/.work-requests/inbox/wr-x.json"
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": target, "content": "{}"},
        ))
        assert result is not None
        assert "TARGET WORKSPACE STRUCTURE VIOLATION" in result["advisory"]

    def test_writing_to_sentinel_work_requests_from_anywhere_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        target = "/4.- Sentinel/.work-requests/inbox/wr-x.json"
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": target, "content": "{}"},
        ))
        assert result is not None
        assert "TARGET WORKSPACE STRUCTURE VIOLATION" in result["advisory"]


# ---------------------------------------------------------------------------
# Layer 3: ALWAYS_ALLOWED exemptions
# ---------------------------------------------------------------------------

class TestScopeDisciplineAlwaysAllowed:
    def test_routed_tasks_in_other_workspace_passes(self, monkeypatch):
        """Writing to ANOTHER workspace's .routed-tasks/ (not Skill Hub's,
        which is structurally forbidden) is sanctioned coordination."""
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: SKILL_HUB_CWD)
        target = "/1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/inbox/rt-x.json"
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": target, "content": "{}"},
        ))
        assert result is None

    def test_lifecycle_reviews_anywhere_passes(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        target = "/4.- Sentinel/.lifecycle-reviews/inbox/lr-x.json"
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": target, "content": "{}"},
        ))
        assert result is None

    def test_claude_rules_passes(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Edit",
            {"file_path": "/home/user/.claude/rules/universal-protocols.md",
             "old_string": "a", "new_string": "b"},
        ))
        assert result is None

    def test_claude_scripts_passes(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": "/home/user/.claude/scripts/helper.py", "content": "x"},
        ))
        assert result is None

    def test_memory_passes(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Edit",
            {"file_path": "/some/workspace/memory/feedback_x.md",
             "old_string": "a", "new_string": "b"},
        ))
        assert result is None

    def test_tmp_passes(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": "/workspace/.tmp/cache.json", "content": "{}"},
        ))
        assert result is None


# ---------------------------------------------------------------------------
# Layer 4: protocol-sanctioned writes
# ---------------------------------------------------------------------------

class TestScopeDisciplineProtocolSanctioned:
    def test_write_to_other_workspace_work_requests_inbox_passes(self, monkeypatch):
        """New Write to .work-requests/inbox/ is sanctioned coordination."""
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": "/some/workspace/.work-requests/inbox/wr-x.json",
             "content": "{}"},
        ))
        assert result is None

    def test_edit_appending_blocker_cleared_notes_passes(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        old = '{"blocker_cleared_notes": []}'
        new = '{"blocker_cleared_notes": [{"timestamp": "2026-05-18T00:00:00Z", "note": "cleared by HQ"}]}'
        result = scope_discipline.evaluate(_payload(
            "Edit",
            {"file_path": "/some/workspace/.work-requests/inbox/wr-x.json",
             "old_string": old, "new_string": new},
        ))
        assert result is None


# ---------------------------------------------------------------------------
# Layer 5: cross-workspace SCOPE_VIOLATIONS (creates skill from HQ, etc.)
# ---------------------------------------------------------------------------

class TestScopeDisciplineCrossWorkspaceViolations:
    def test_hq_creating_skill_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": "/home/user/.claude/skills/new-skill/SKILL.md",
             "content": "x"},
        ))
        assert result is not None
        assert "SCOPE VIOLATION" in result["advisory"]
        assert "Skill Management Hub" in result["advisory"]

    def test_sentinel_creating_hook_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: SENTINEL_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": "/home/user/.claude/hooks/new-hook.py",
             "content": "x"},
        ))
        assert result is not None
        assert "SCOPE VIOLATION" in result["advisory"]

    def test_hq_writing_to_sentinel_dir_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": "/code/4.- Sentinel/docs/audit.md",
             "content": "x"},
        ))
        assert result is not None
        assert "SCOPE VIOLATION" in result["advisory"]
        assert "Sentinel" in result["advisory"]

    def test_skill_hub_writing_to_hq_dir_warns(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: SKILL_HUB_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": "/code/1.- SHARKITECT DIGITAL WORKFORCE HQ/deliverables/x.md",
             "content": "x"},
        ))
        assert result is not None
        assert "SCOPE VIOLATION" in result["advisory"]


# ---------------------------------------------------------------------------
# Pass-through: legitimate same-workspace writes, non-Write/Edit tools, etc.
# ---------------------------------------------------------------------------

class TestScopeDisciplinePassThrough:
    def test_read_tool_passes(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Read",
            {"file_path": "/anything.md"},
        ))
        assert result is None

    def test_bash_tool_passes(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Bash",
            {"command": "ls"},
        ))
        assert result is None

    def test_unknown_workspace_passes(self, monkeypatch):
        """Unknown workspace = no scope rules to enforce."""
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: "/random/dir")
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": "/random/dir/file.md", "content": "x"},
        ))
        assert result is None

    def test_legitimate_in_workspace_write_passes(self, monkeypatch):
        """Writing inside one's own workspace to a non-forbidden path = OK."""
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: SKILL_HUB_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": SKILL_HUB_CWD + "/docs/something.md", "content": "x"},
        ))
        assert result is None

    def test_empty_file_path_passes(self, monkeypatch):
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": "", "content": "x"},
        ))
        assert result is None

    def test_empty_payload_passes(self):
        from _dispatchers.methodology import scope_discipline
        result = scope_discipline.evaluate({})
        assert result is None


# ---------------------------------------------------------------------------
# Self-write detection: path-prefix not substring
# ---------------------------------------------------------------------------

class TestScopeDisciplineSelfWriteDetection:
    def test_filename_containing_workspace_keyword_not_false_positive(self, monkeypatch):
        """A filename like rt-sentinel-foo.json routed TO Skill Hub must NOT
        be classified as 'inside Sentinel's dir'.
        """
        from _dispatchers.methodology import scope_discipline
        monkeypatch.setattr(scope_discipline, "_get_cwd", lambda: HQ_CWD)
        # Writing TO HQ's own outbox a file named with the Sentinel prefix
        result = scope_discipline.evaluate(_payload(
            "Write",
            {"file_path": HQ_CWD + "/.routed-tasks/outbox/rt-sentinel-x.md",
             "content": "x"},
        ))
        # ALWAYS_ALLOWED covers .routed-tasks/ -> pass
        assert result is None
