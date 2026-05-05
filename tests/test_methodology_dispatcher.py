"""Tests for methodology-dispatcher.py sub-rules and dispatch logic.

Each sub-rule has its own test class. The dispatcher test class
(TestDispatcher, added with the entry point) verifies that the dispatcher
calls sub-rules in the right order and emits the correct merged output.

Sub-rule test conventions:
  - Use tmp_path for transcript / state / log fixtures (test isolation)
  - Patch _feedback_events to a no-op or per-test stream so production
    feedback_events.jsonl is not polluted
  - Each sub-rule test class verifies: trigger, bypass via skill log,
    bypass via transcript phrase, exemptions (meta path / config doc),
    no-op cases, and intent_detection user-driven bypass.

Files under test:
  ~/.claude/hooks/_dispatchers/methodology/<sub_rule>.py

Spec: docs/superpowers/specs/2026-05-05-hook-dispatcher-consolidation-spec.md
"""
from __future__ import annotations

import json
import os
import sys

import pytest

# Make hooks/ importable for the _dispatchers package
HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


# ---------------------------------------------------------------------------
# Test fixtures shared across sub-rule classes
# ---------------------------------------------------------------------------

def _write_transcript(tmp_path, *messages):
    """Helper: write a JSONL transcript with the given user messages."""
    path = tmp_path / "transcript.jsonl"
    lines = []
    for msg in messages:
        lines.append(json.dumps({
            "type": "user",
            "message": {"content": msg},
        }))
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return str(path)


def _write_skill_log(tmp_path, *skill_names):
    """Helper: write today's skill-invocation log with given skills."""
    from datetime import datetime
    log_dir = tmp_path / ".tmp"
    log_dir.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log = log_dir / f"skill-invocations-{today}.json"
    log.write_text(json.dumps({
        "invocations": [{"skill": n} for n in skill_names]
    }), encoding="utf-8")
    return str(log)


# ---------------------------------------------------------------------------
# Sub-rule: brainstorming
# Source: brainstorming-enforcer.py (HARD GATE)
# Preservation:
#   - 3 signals (A: ideation keywords in transcript user msgs,
#     B: new plan file write to plans/ path,
#     C: candidate-pitching pattern in tool content)
#   - Bypass: skill log, transcript bypass phrase, content bypass phrase,
#     intent_detection user-driven mode
#   - Exemptions: meta paths, existing config docs (CLAUDE.md / MEMORY.md / etc.)
#   - HARD GATE: returns {"decision": "deny", "reason": ...}
#   - Only Write tool, never Edit
# ---------------------------------------------------------------------------

class TestBrainstormingSubRule:
    """Preserve brainstorming-enforcer.py 1:1 as a sub-rule."""

    def test_signal_a_ideation_keyword_in_transcript_triggers_deny(self, tmp_path, monkeypatch):
        """Signal A: recent user message contains 'brainstorm' or other ideation keyword."""
        monkeypatch.setenv("TMP_DIR_OVERRIDE", str(tmp_path / ".tmp"))
        transcript = _write_transcript(tmp_path, "let's brainstorm some name options")
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(tmp_path / "newfile.md"), "content": "x" * 250},
            "transcript_path": transcript,
            "session_id": "test-sig-a",
        })
        assert result is not None
        assert result.get("decision") == "deny"
        assert "brainstorming" in result.get("reason", "").lower()

    def test_signal_b_new_plan_file_write_triggers_deny(self, tmp_path):
        """Signal B: Write to a new plans/*.md path."""
        plan_path = tmp_path / "plans" / "new-feature.md"
        plan_path.parent.mkdir(parents=True)
        # File does NOT exist yet - this is a NEW plan write
        transcript = _write_transcript(tmp_path, "ok lets work on this")
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(plan_path), "content": "x" * 250},
            "transcript_path": transcript,
            "session_id": "test-sig-b",
        })
        assert result is not None
        assert result.get("decision") == "deny"

    def test_existing_plan_file_overwrite_does_not_trigger(self, tmp_path):
        """Signal B suppression: existing plan files are NOT new creation."""
        plan_path = tmp_path / "plans" / "existing-plan.md"
        plan_path.parent.mkdir(parents=True)
        plan_path.write_text("# Existing plan", encoding="utf-8")
        transcript = _write_transcript(tmp_path, "update the plan status")
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(plan_path), "content": "x" * 250},
            "transcript_path": transcript,
            "session_id": "test-sig-b-overwrite",
        })
        # Existing plan overwrite is treated as update, not new ideation
        assert result is None or result.get("decision") != "deny"

    def test_signal_c_candidate_pitching_in_content_triggers_deny(self, tmp_path):
        """Signal C: tool content has BOTH a domain keyword AND ideation header."""
        transcript = _write_transcript(tmp_path, "ok proceed")
        content = (
            "# Brand suggestions\n\n"
            "Tagline options:\n"
            "1. Option A\n"
            "2. Option B\n"
            "3. Option C\n"
        )
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(tmp_path / "doc.md"), "content": content},
            "transcript_path": transcript,
            "session_id": "test-sig-c",
        })
        assert result is not None
        assert result.get("decision") == "deny"

    def test_bypass_via_skill_log(self, tmp_path, monkeypatch):
        """Bypass: brainstorming or superpowers:brainstorming invoked today."""
        monkeypatch.setenv("CLAUDE_TMP_DIR", str(tmp_path / ".tmp"))
        _write_skill_log(tmp_path, "superpowers:brainstorming")
        # Patch the brainstorming module's TMP_DIR to match
        from _dispatchers.methodology import brainstorming
        monkeypatch.setattr(brainstorming, "TMP_DIR", tmp_path / ".tmp")
        transcript = _write_transcript(tmp_path, "let's brainstorm naming")
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(tmp_path / "n.md"), "content": "x" * 250},
            "transcript_path": transcript,
            "session_id": "test-bypass-skill",
        })
        # Bypass means no deny -- either None or non-deny
        assert result is None or result.get("decision") != "deny"

    def test_bypass_via_transcript_phrase(self, tmp_path):
        """Bypass: 'skip brainstorming' phrase in recent user message."""
        transcript = _write_transcript(tmp_path, "skip brainstorming, just write the plan")
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(tmp_path / "plans" / "x.md"), "content": "x" * 250},
            "transcript_path": transcript,
            "session_id": "test-bypass-transcript",
        })
        # New plan file path with bypass phrase => no deny
        assert result is None or result.get("decision") != "deny"

    def test_bypass_via_content_phrase(self, tmp_path):
        """Bypass: 'skip brainstorming' phrase IN the content being written
        (allows filing gap reports about brainstorming without deadlock)."""
        transcript = _write_transcript(tmp_path, "lets brainstorm this")
        content = "# Gap report\n\nThe brainstorming-enforcer hook... skip brainstorming"
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(tmp_path / "report.md"), "content": content + "x" * 250},
            "transcript_path": transcript,
            "session_id": "test-bypass-content",
        })
        assert result is None or result.get("decision") != "deny"

    def test_meta_path_exemption(self, tmp_path):
        """Exemption: writes under /.work-requests/, /.routed-tasks/, etc.
        are structurally exempt (gap reports about ideation must be writable)."""
        meta_path = tmp_path / ".work-requests" / "inbox" / "wr-test.json"
        meta_path.parent.mkdir(parents=True)
        transcript = _write_transcript(tmp_path, "let's brainstorm options")
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(meta_path), "content": "x" * 250},
            "transcript_path": transcript,
            "session_id": "test-meta-exempt",
        })
        # Meta path exempt -- no deny even with ideation transcript
        assert result is None

    def test_existing_config_doc_exemption(self, tmp_path):
        """Exemption: rewrites of existing CLAUDE.md / MEMORY.md / README.md
        / AGENTS.md / GEMINI.md are structural realignment, not feature ideation."""
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# Project\n", encoding="utf-8")
        transcript = _write_transcript(tmp_path, "let's brainstorm refactoring")
        content = "# Project rewrite\n\nTagline options:\n1. A\n2. B\n3. C\n" + "x" * 250
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(claude_md), "content": content},
            "transcript_path": transcript,
            "session_id": "test-config-exempt",
        })
        assert result is None or result.get("decision") != "deny"

    def test_edit_does_not_trigger(self, tmp_path):
        """Only Write triggers brainstorming; Edit (maintenance) is exempt."""
        transcript = _write_transcript(tmp_path, "let's brainstorm names")
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(tmp_path / "plans" / "x.md"),
                "old_string": "a",
                "new_string": "b",
            },
            "transcript_path": transcript,
            "session_id": "test-edit-exempt",
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path):
        """NEW LAYER: user-driven imperative ('go ahead and...') passes
        through via shared intent_detection.py helper."""
        transcript = _write_transcript(
            tmp_path,
            "go ahead and write the new plan file we discussed"
        )
        from _dispatchers.methodology import brainstorming
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "plans" / "discussed-plan.md"),
                "content": "x" * 250,
            },
            "transcript_path": transcript,
            "session_id": "test-intent-bypass",
        })
        # User-driven imperative -> intent_detection returns is_user_driven=True
        # -> sub-rule passes through with no deny
        assert result is None or result.get("decision") != "deny"


# ---------------------------------------------------------------------------
# Sub-rule: writing_plans
# Source: writing-plans-enforcer.py (HARD GATE)
# Preservation:
#   - Path: **/plan.md, **/plans/*.md, **/projects/X/plan*.md
#   - Content: Write >= 200 chars OR Edit with structural keyword OR 50+ lines
#   - Bypass: skill log (writing-plans / superpowers:writing-plans),
#     transcript phrase (skip writing-plans / status update only)
#   - HARD GATE: returns {"decision": "deny"}
#   - Triggers on Write AND Edit
# ---------------------------------------------------------------------------

class TestWritingPlansSubRule:
    def test_write_to_plan_path_with_substantial_content_triggers(self, tmp_path):
        plan_path = tmp_path / "plans" / "new.md"
        plan_path.parent.mkdir(parents=True)
        transcript = _write_transcript(tmp_path, "ok")
        from _dispatchers.methodology import writing_plans
        result = writing_plans.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(plan_path), "content": "x" * 250},
            "transcript_path": transcript,
        })
        assert result is not None
        assert result.get("decision") == "deny"
        assert "writing-plans" in result.get("reason", "").lower()

    def test_short_write_treated_as_scaffold(self, tmp_path):
        """Writes under 200 chars are scaffolds, allowed."""
        plan_path = tmp_path / "plans" / "scaffold.md"
        plan_path.parent.mkdir(parents=True)
        transcript = _write_transcript(tmp_path, "ok")
        from _dispatchers.methodology import writing_plans
        result = writing_plans.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(plan_path), "content": "# Title\nTBD"},
            "transcript_path": transcript,
        })
        assert result is None

    def test_non_plan_path_does_not_trigger(self, tmp_path):
        from _dispatchers.methodology import writing_plans
        result = writing_plans.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "src" / "thing.py"),
                "content": "x" * 250,
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_edit_with_structural_keyword_triggers(self, tmp_path):
        plan_path = tmp_path / "plans" / "x.md"
        plan_path.parent.mkdir(parents=True)
        plan_path.write_text("# Plan\n", encoding="utf-8")
        transcript = _write_transcript(tmp_path, "ok")
        from _dispatchers.methodology import writing_plans
        result = writing_plans.evaluate({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(plan_path),
                "old_string": "# Plan",
                "new_string": "# Plan\n## Phase 1\n## Phase 2\n## Phase 3\n",
            },
            "transcript_path": transcript,
        })
        assert result is not None
        assert result.get("decision") == "deny"

    def test_small_edit_status_update_does_not_trigger(self, tmp_path):
        """Edit under 50 lines without structural keywords is a status update."""
        plan_path = tmp_path / "plans" / "x.md"
        plan_path.parent.mkdir(parents=True)
        plan_path.write_text("# Plan\nstatus: pending\n", encoding="utf-8")
        from _dispatchers.methodology import writing_plans
        result = writing_plans.evaluate({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(plan_path),
                "old_string": "status: pending",
                "new_string": "status: complete",
            },
            "transcript_path": _write_transcript(tmp_path, "update status"),
        })
        assert result is None

    def test_bypass_via_skill_log(self, tmp_path, monkeypatch):
        _write_skill_log(tmp_path, "superpowers:writing-plans")
        from _dispatchers.methodology import writing_plans
        monkeypatch.setattr(writing_plans, "TMP_DIR", tmp_path / ".tmp")
        plan_path = tmp_path / "plans" / "x.md"
        plan_path.parent.mkdir(parents=True)
        result = writing_plans.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(plan_path), "content": "x" * 250},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_transcript_phrase(self, tmp_path):
        plan_path = tmp_path / "plans" / "x.md"
        plan_path.parent.mkdir(parents=True)
        transcript = _write_transcript(tmp_path, "status update only")
        from _dispatchers.methodology import writing_plans
        result = writing_plans.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(plan_path), "content": "x" * 250},
            "transcript_path": transcript,
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path):
        """User imperative ('go ahead and update the plan') -> bypass."""
        plan_path = tmp_path / "plans" / "discussed-plan.md"
        plan_path.parent.mkdir(parents=True)
        transcript = _write_transcript(
            tmp_path, "go ahead and write the discussed-plan file we agreed on"
        )
        from _dispatchers.methodology import writing_plans
        result = writing_plans.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(plan_path), "content": "x" * 250},
            "transcript_path": transcript,
        })
        assert result is None
