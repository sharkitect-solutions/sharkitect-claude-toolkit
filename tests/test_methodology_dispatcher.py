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
        from _dispatchers.methodology import brainstorming
        monkeypatch.setattr(brainstorming, "TMP_DIR", tmp_path / ".tmp")
        transcript = _write_transcript(tmp_path, "let's brainstorm some name options")
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(tmp_path / "newfile.md"), "content": "x" * 250},
            "transcript_path": transcript,
            "session_id": "test-sig-a",
        })
        assert result is not None
        assert result.get("decision") == "deny"
        assert "brainstorming" in result.get("reason", "").lower()

    def test_signal_b_new_plan_file_write_triggers_deny(self, tmp_path, monkeypatch):
        """Signal B: Write to a new plans/*.md path."""
        from _dispatchers.methodology import brainstorming
        monkeypatch.setattr(brainstorming, "TMP_DIR", tmp_path / ".tmp")
        plan_path = tmp_path / "plans" / "new-feature.md"
        plan_path.parent.mkdir(parents=True)
        # File does NOT exist yet - this is a NEW plan write
        transcript = _write_transcript(tmp_path, "ok lets work on this")
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

    def test_signal_c_candidate_pitching_in_content_triggers_deny(self, tmp_path, monkeypatch):
        """Signal C: tool content has BOTH a domain keyword AND ideation header."""
        from _dispatchers.methodology import brainstorming
        monkeypatch.setattr(brainstorming, "TMP_DIR", tmp_path / ".tmp")
        transcript = _write_transcript(tmp_path, "ok proceed")
        content = (
            "# Brand suggestions\n\n"
            "Tagline options:\n"
            "1. Option A\n"
            "2. Option B\n"
            "3. Option C\n"
        )
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
    def test_write_to_plan_path_with_substantial_content_triggers(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import writing_plans
        monkeypatch.setattr(writing_plans, "TMP_DIR", tmp_path / ".tmp")
        plan_path = tmp_path / "plans" / "new.md"
        plan_path.parent.mkdir(parents=True)
        transcript = _write_transcript(tmp_path, "ok")
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

    def test_edit_with_structural_keyword_triggers(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import writing_plans
        monkeypatch.setattr(writing_plans, "TMP_DIR", tmp_path / ".tmp")
        plan_path = tmp_path / "plans" / "x.md"
        plan_path.parent.mkdir(parents=True)
        plan_path.write_text("# Plan\n", encoding="utf-8")
        transcript = _write_transcript(tmp_path, "ok")
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


# ---------------------------------------------------------------------------
# Sub-rule: claude_api
# Source: claude-api-skill-nudge.py (Advisory soft nudge)
# Preservation:
#   - 4 content signals: Anthropic SDK import, SDK call, cache_control,
#     thinking/beta.tools
#   - Bypass: skill log (claude-api), transcript phrase, intent_detection
#   - Exemptions: other-provider imports, other-provider filenames,
#     documentation paths
#   - Debounce: once per session (state file)
#   - ADVISORY: returns {"advisory": "..."} (no deny)
#   - Triggers on Write AND Edit
# ---------------------------------------------------------------------------

class TestClaudeApiSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        """Ensure the sub-rule's state file is isolated per test."""
        from _dispatchers.methodology import claude_api
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(claude_api, "TMP_DIR", state_dir)
        monkeypatch.setattr(
            claude_api, "STATE_FILE", state_dir / "claude-api-skill-nudge-state.json"
        )

    def test_anthropic_import_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "agent.py"),
                "content": "from anthropic import Anthropic\nclient = Anthropic()\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result
        assert "claude-api" in result["advisory"].lower()

    def test_messages_create_call_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "client.py"),
                "content": 'resp = client.messages.create(model="claude-sonnet-4", messages=[])\n',
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result

    def test_cache_control_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "cache.py"),
                "content": 'cache_control={"type": "ephemeral"}\n',
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result

    def test_thinking_beta_tools_triggers_advisory(self, tmp_path, monkeypatch):
        """Beta features signal: thinking={...} / beta.tools.* / computer_use / extended_thinking.

        Regex was previously `\\b(?:thinking\\s*=\\s*\\{|beta\\.tools\\.|...)\\b` --
        trailing \\b after \\{ or \\. could never match typical non-word follow-ups
        like '{"type":...' or 'tools.run(...)'. wr-skillhub-2026-05-05-001 fixed by
        dropping leading + trailing global \\b and pinning word-boundaries only on
        the branches ending in word chars (computer_use\\b, extended_thinking\\b).
        This test now uses the literal thinking={...} pattern that previously dead-fired.
        """
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "thinking.py"),
                "content": (
                    "from anthropic import Anthropic\n"
                    "client = Anthropic()\n"
                    "response = client.messages.create(\n"
                    '    model="claude-sonnet-4-5",\n'
                    '    thinking={"type":"enabled","budget_tokens":10000},\n'
                    "    messages=[{\"role\":\"user\",\"content\":\"hi\"}],\n"
                    ")\n"
                ),
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result

    def test_other_provider_import_exempt(self, tmp_path, monkeypatch):
        """OpenAI / Cohere / Mistral / Gemini imports skip nudge."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "agent.py"),
                "content": (
                    "from openai import OpenAI\n"
                    "from anthropic import Anthropic\n"  # both present
                    "client.messages.create(model='claude-sonnet-4', messages=[])\n"
                ),
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_other_provider_filename_exempt(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "agent-openai.py"),
                "content": "client.messages.create(model='claude-sonnet-4', messages=[])\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_documentation_path_exempt(self, tmp_path, monkeypatch):
        """Docs / .md files / plans / memory paths are exempt -- they may discuss API without being API code."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "docs" / "anthropic-notes.md"),
                "content": "from anthropic import Anthropic\nclient.messages.create(...)\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_skill_log(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        _write_skill_log(tmp_path, "claude-api")
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "agent.py"),
                "content": "from anthropic import Anthropic\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_transcript_phrase(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "agent.py"),
                "content": "from anthropic import Anthropic\n",
            },
            "transcript_path": _write_transcript(tmp_path, "skip claude-api-nudge"),
        })
        assert result is None

    def test_debounce_once_per_session(self, tmp_path, monkeypatch):
        """After firing once, subsequent triggers in the same session pass through."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        # First call: should fire
        first = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "agent1.py"),
                "content": "from anthropic import Anthropic\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert first is not None
        # Second call: should be debounced
        second = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "agent2.py"),
                "content": "from anthropic import Anthropic\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert second is None

    def test_non_write_edit_tool_exempt(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "echo from anthropic import Anthropic"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import claude_api
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "agent.py"),
                "content": "from anthropic import Anthropic\n",
            },
            "transcript_path": _write_transcript(
                tmp_path, "go ahead and write the agent.py we discussed"
            ),
        })
        assert result is None


# ---------------------------------------------------------------------------
# Sub-rule: multistep_plan
# Source: multistep-plan-nudge.py (Advisory soft nudge on TodoWrite >= 5)
# Preservation:
#   - Threshold: 5+ todos
#   - Bypass: skill log (writing-plans / superpowers:writing-plans),
#     transcript phrase, intent_detection
#   - Debounce: once per session
#   - ADVISORY: returns {"advisory": "..."}
#   - Triggers ONLY on TodoWrite tool
# ---------------------------------------------------------------------------

class TestMultistepPlanSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import multistep_plan
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(multistep_plan, "TMP_DIR", state_dir)
        monkeypatch.setattr(
            multistep_plan, "STATE_FILE", state_dir / "multistep-plan-nudge-state.json"
        )

    def test_5plus_todos_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multistep_plan
        todos = [{"content": f"task {i}", "status": "pending", "activeForm": f"doing {i}"} for i in range(5)]
        result = multistep_plan.evaluate({
            "tool_name": "TodoWrite",
            "tool_input": {"todos": todos},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result
        assert "writing-plans" in result["advisory"].lower()

    def test_under_threshold_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multistep_plan
        todos = [{"content": f"task {i}", "status": "pending", "activeForm": f"doing {i}"} for i in range(3)]
        result = multistep_plan.evaluate({
            "tool_name": "TodoWrite",
            "tool_input": {"todos": todos},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_skill_log_writing_plans(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        _write_skill_log(tmp_path, "writing-plans")
        from _dispatchers.methodology import multistep_plan
        todos = [{"content": f"task {i}", "status": "pending", "activeForm": f"doing {i}"} for i in range(7)]
        result = multistep_plan.evaluate({
            "tool_name": "TodoWrite",
            "tool_input": {"todos": todos},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_skill_log_superpowers_writing_plans(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        _write_skill_log(tmp_path, "superpowers:writing-plans")
        from _dispatchers.methodology import multistep_plan
        todos = [{"content": f"task {i}", "status": "pending", "activeForm": f"doing {i}"} for i in range(7)]
        result = multistep_plan.evaluate({
            "tool_name": "TodoWrite",
            "tool_input": {"todos": todos},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_transcript_phrase_todos_only(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multistep_plan
        todos = [{"content": f"t{i}", "status": "pending", "activeForm": f"d{i}"} for i in range(7)]
        result = multistep_plan.evaluate({
            "tool_name": "TodoWrite",
            "tool_input": {"todos": todos},
            "transcript_path": _write_transcript(tmp_path, "todos only please"),
        })
        assert result is None

    def test_bypass_via_transcript_phrase_skip_multistep_plan(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multistep_plan
        todos = [{"content": f"t{i}", "status": "pending", "activeForm": f"d{i}"} for i in range(7)]
        result = multistep_plan.evaluate({
            "tool_name": "TodoWrite",
            "tool_input": {"todos": todos},
            "transcript_path": _write_transcript(tmp_path, "skip multistep-plan, just track"),
        })
        assert result is None

    def test_debounce_once_per_session(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multistep_plan
        todos = [{"content": f"t{i}", "status": "pending", "activeForm": f"d{i}"} for i in range(6)]
        first = multistep_plan.evaluate({
            "tool_name": "TodoWrite",
            "tool_input": {"todos": todos},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert first is not None
        second = multistep_plan.evaluate({
            "tool_name": "TodoWrite",
            "tool_input": {"todos": todos},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert second is None

    def test_non_todowrite_tool_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multistep_plan
        result = multistep_plan.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_path / "x.py"),
                "content": "x" * 250,
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multistep_plan
        todos = [{"content": f"t{i}", "status": "pending", "activeForm": f"d{i}"} for i in range(8)]
        result = multistep_plan.evaluate({
            "tool_name": "TodoWrite",
            "tool_input": {"todos": todos},
            "transcript_path": _write_transcript(
                tmp_path, "go ahead and execute the multi-step task we agreed on"
            ),
        })
        assert result is None


# ---------------------------------------------------------------------------
# Sub-rule: supabase_ddl
# Source: supabase-ddl-skill-nudge.py (HARD GATE on Supabase MCP DDL)
# Preservation:
#   - Trigger: mcp__*supabase* tool with apply_migration/execute_sql operation
#     + DDL detected in SQL (ALTER TABLE / CREATE INDEX / COMMENT ON / etc.)
#   - Bypass: skill log (supabase-postgres-best-practices OR supabase),
#     transcript phrase, intent_detection
#   - HARD GATE: returns {"decision": "deny", "reason": ...}
#   - DDL detection strips SQL comments to avoid false positives
# ---------------------------------------------------------------------------

class TestSupabaseDdlSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import supabase_ddl
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(supabase_ddl, "TMP_DIR", state_dir)

    def test_alter_table_via_apply_migration_triggers_deny(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__apply_migration",
            "tool_input": {"query": "ALTER TABLE projects ADD COLUMN closure_reason text;"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert result.get("decision") == "deny"
        assert "supabase-postgres-best-practices" in result.get("reason", "").lower()

    def test_create_table_via_execute_sql_triggers_deny(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__supabase__execute_sql",
            "tool_input": {"query": "CREATE TABLE foo (id uuid primary key);"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert result.get("decision") == "deny"

    def test_create_index_triggers_deny(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__apply_migration",
            "tool_input": {"query": "CREATE INDEX idx_foo ON bar USING gin (data);"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert result.get("decision") == "deny"

    def test_comment_on_triggers_deny(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__execute_sql",
            "tool_input": {"query": "COMMENT ON COLUMN tasks.priority IS 'urgency';"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert result.get("decision") == "deny"

    def test_select_does_not_trigger(self, tmp_path, monkeypatch):
        """DML (SELECT/INSERT/UPDATE/DELETE) is not DDL."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__execute_sql",
            "tool_input": {"query": "SELECT * FROM projects WHERE status = 'active';"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_non_supabase_mcp_tool_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__github_mcp__create_branch",
            "tool_input": {"query": "CREATE TABLE x (id int);"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_supabase_non_sql_op_does_not_trigger(self, tmp_path, monkeypatch):
        """list_tables / get_logs / etc. are not apply_migration/execute_sql."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__list_tables",
            "tool_input": {"schemas": ["public"]},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_skill_log_postgres_best_practices(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        _write_skill_log(tmp_path, "supabase-postgres-best-practices")
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__apply_migration",
            "tool_input": {"query": "ALTER TABLE projects ADD COLUMN x text;"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_skill_log_supabase(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        _write_skill_log(tmp_path, "supabase")
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__apply_migration",
            "tool_input": {"query": "ALTER TABLE projects ADD COLUMN x text;"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_transcript_phrase(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__apply_migration",
            "tool_input": {"query": "ALTER TABLE projects ADD COLUMN x text;"},
            "transcript_path": _write_transcript(tmp_path, "skip ddl-nudge"),
        })
        assert result is None

    def test_ddl_in_sql_comment_does_not_trigger_false_positive(self, tmp_path, monkeypatch):
        """SQL comments containing DDL keywords should NOT trigger."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__execute_sql",
            "tool_input": {
                "query": "-- We previously did CREATE TABLE x; here\nSELECT count(*) FROM x;"
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import supabase_ddl
        result = supabase_ddl.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__apply_migration",
            "tool_input": {"query": "ALTER TABLE projects ADD COLUMN x text;"},
            "transcript_path": _write_transcript(
                tmp_path, "go ahead and apply the migration we discussed adding the closure_reason column"
            ),
        })
        assert result is None


# ---------------------------------------------------------------------------
# Sub-rule: deep_interview
# Source: deep-interview-gate.py (Advisory on Skill invocations of
# planning/design skills when /deep-interview hasn't run)
# Preservation:
#   - Trigger: tool_name == "Skill" AND skill_name in PLANNING_SKILLS
#   - Bypass: INTERVIEW_STATE file exists (deep-interview already ran)
#   - Debounce: SKIP_TRACKER file (once nudged this session, don't nag again)
#   - ADVISORY: returns {"advisory": "..."}
# ---------------------------------------------------------------------------

class TestDeepInterviewSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import deep_interview
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(
            deep_interview, "INTERVIEW_STATE",
            str(state_dir / "deep-interview-state.json"),
        )
        monkeypatch.setattr(
            deep_interview, "SKIP_TRACKER",
            str(state_dir / "claude_deep_interview_skip.json"),
        )

    def test_planning_skill_brainstorming_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import deep_interview
        result = deep_interview.evaluate({
            "tool_name": "Skill",
            "tool_input": {"skill": "brainstorming"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result
        assert "deep-interview" in result["advisory"].lower()

    def test_planning_skill_superpowers_writing_plans_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import deep_interview
        result = deep_interview.evaluate({
            "tool_name": "Skill",
            "tool_input": {"skill": "superpowers:writing-plans"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result

    def test_non_planning_skill_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import deep_interview
        result = deep_interview.evaluate({
            "tool_name": "Skill",
            "tool_input": {"skill": "claude-api"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_non_skill_tool_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import deep_interview
        result = deep_interview.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(tmp_path / "x.md"), "content": "x" * 250},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_when_deep_interview_state_exists(self, tmp_path, monkeypatch):
        """If /deep-interview already ran, no reminder."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import deep_interview
        # Create the state file
        with open(deep_interview.INTERVIEW_STATE, "w", encoding="utf-8") as f:
            f.write('{"ran": true}')
        result = deep_interview.evaluate({
            "tool_name": "Skill",
            "tool_input": {"skill": "brainstorming"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_debounce_via_skip_tracker(self, tmp_path, monkeypatch):
        """First call nudges; second call within session is debounced."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import deep_interview
        first = deep_interview.evaluate({
            "tool_name": "Skill",
            "tool_input": {"skill": "brainstorming"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert first is not None
        second = deep_interview.evaluate({
            "tool_name": "Skill",
            "tool_input": {"skill": "writing-plans"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert second is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import deep_interview
        result = deep_interview.evaluate({
            "tool_name": "Skill",
            "tool_input": {"skill": "brainstorming"},
            "transcript_path": _write_transcript(
                tmp_path,
                "go ahead and invoke brainstorming for the design we discussed",
            ),
        })
        assert result is None


# ---------------------------------------------------------------------------
# Sub-rule: process_violation
# Source: process-violation-detector.py (UserPromptSubmit advisory nudge
# when user signals process violation language)
# Preservation:
#   - 5 patterns: skipping-steps, jumping-gun, against-foundations,
#     violates-principle, already-still-mismatch
#   - Bypass: skill log (systematic-debugging / superpowers:systematic-debugging)
#   - Bypass: phrase "skip systematic-debugging" in prompt
#   - Per-pattern debounce: each key nudges once per session
#   - ADVISORY: returns {"advisory": "..."}
#   - Different payload shape: reads `prompt` or `user_prompt` field
# ---------------------------------------------------------------------------

class TestProcessViolationSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import process_violation
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(process_violation, "TMP_DIR", state_dir)
        monkeypatch.setattr(
            process_violation, "STATE_FILE",
            state_dir / "process-violation-detector-state.json",
        )

    def test_skipping_steps_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "prompt": "Wait -- we're skipping steps here. Let's slow down.",
        })
        assert result is not None
        assert "advisory" in result
        assert "systematic-debugging" in result["advisory"].lower()

    def test_jumping_gun_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "prompt": "I think we are jumping the gun on this.",
        })
        assert result is not None
        assert "advisory" in result

    def test_against_foundations_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "prompt": "This goes against our foundations of structured debugging.",
        })
        assert result is not None
        assert "advisory" in result

    def test_violates_principle_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "prompt": "This violates our diagnostic-before-prescription principle.",
        })
        assert result is not None
        assert "advisory" in result

    def test_already_still_mismatch_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "prompt": "How are we already prescribing a fix when we are still diagnosing the issue?",
        })
        assert result is not None
        assert "advisory" in result

    def test_no_violation_language_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "prompt": "Please add a new column to the projects table.",
        })
        assert result is None

    def test_bypass_phrase_in_prompt(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "prompt": "We're skipping steps but skip systematic-debugging here -- it's a stylistic rewrite.",
        })
        assert result is None

    def test_bypass_via_skill_log(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        _write_skill_log(tmp_path, "systematic-debugging")
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "prompt": "We're skipping steps here.",
        })
        assert result is None

    def test_bypass_via_skill_log_superpowers(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        _write_skill_log(tmp_path, "superpowers:systematic-debugging")
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "prompt": "We're skipping steps here.",
        })
        assert result is None

    def test_per_pattern_debounce(self, tmp_path, monkeypatch):
        """Same pattern in second prompt is debounced; new pattern still nudges."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        # First prompt: skipping-steps triggers
        first = process_violation.evaluate({"prompt": "We're skipping steps here."})
        assert first is not None
        # Second prompt: same pattern -- debounced
        second = process_violation.evaluate({"prompt": "We are skipping steps still."})
        assert second is None
        # Third prompt: different pattern -- still nudges
        third = process_violation.evaluate({"prompt": "We are jumping the gun on this."})
        assert third is not None

    def test_user_prompt_field_alias(self, tmp_path, monkeypatch):
        """Forward-compat: accept user_prompt as well as prompt."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({
            "user_prompt": "We are skipping steps here.",
        })
        assert result is not None

    def test_empty_prompt_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import process_violation
        result = process_violation.evaluate({"prompt": ""})
        assert result is None


# ---------------------------------------------------------------------------
# Sub-rule: iterative_work
# Source: iterative-work-nudge.py (PostToolUse advisory after 2+ consecutive
# Bash errors without ralph-loop active)
# Preservation:
#   - Tracks consecutive Bash errors via state file
#   - Skill invocation matching ralph-* sets ralph_active=True
#   - 2+ consecutive errors with ralph_active=False -> advisory
#   - Bash success resets the counter
#   - Non-Bash tools (other than Skill) are ignored
#   - ADVISORY: returns {"advisory": "..."}
# ---------------------------------------------------------------------------

class TestIterativeWorkSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import iterative_work
        state_file = tmp_path / ".tmp" / "claude_iterative_work_tracker.json"
        state_file.parent.mkdir(exist_ok=True)
        monkeypatch.setattr(iterative_work, "TRACKER_FILE", str(state_file))

    def test_first_bash_error_no_nudge_yet(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import iterative_work
        result = iterative_work.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "python broken.py"},
            "tool_result": "Traceback (most recent call last):\n  TypeError: ...",
        })
        assert result is None  # counter at 1; threshold is 2

    def test_two_consecutive_bash_errors_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import iterative_work
        # First error
        iterative_work.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "x"},
            "tool_result": "Error: something failed",
        })
        # Second error -> advisory
        result = iterative_work.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "y"},
            "tool_result": "FAIL: another error",
        })
        assert result is not None
        assert "advisory" in result
        assert "ralph-loop" in result["advisory"].lower()

    def test_bash_success_resets_counter(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import iterative_work
        # 1 error
        iterative_work.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "x"},
            "tool_result": "Error: failed",
        })
        # success -> counter reset
        iterative_work.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "echo ok"},
            "tool_result": "ok",
        })
        # 1 more error -> counter back to 1, no nudge
        result = iterative_work.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "x"},
            "tool_result": "Error: failed",
        })
        assert result is None

    def test_ralph_loop_skill_invocation_marks_active(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import iterative_work
        # 2 errors first
        iterative_work.evaluate({
            "tool_name": "Bash", "tool_input": {"command": "x"},
            "tool_result": "Error: a",
        })
        iterative_work.evaluate({
            "tool_name": "Bash", "tool_input": {"command": "y"},
            "tool_result": "Error: b",
        })
        # Now invoke ralph-loop
        iterative_work.evaluate({
            "tool_name": "Skill",
            "tool_input": {"skill": "ralph-loop:ralph-loop"},
            "tool_result": "started",
        })
        # Subsequent errors should not nudge -- ralph_active=True
        result1 = iterative_work.evaluate({
            "tool_name": "Bash", "tool_input": {"command": "z"},
            "tool_result": "Error: c",
        })
        result2 = iterative_work.evaluate({
            "tool_name": "Bash", "tool_input": {"command": "w"},
            "tool_result": "Error: d",
        })
        assert result1 is None
        assert result2 is None

    def test_non_bash_non_skill_tool_ignored(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import iterative_work
        result = iterative_work.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(tmp_path / "x.py"), "content": "x"},
            "tool_result": "ok",
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import iterative_work
        # 2 errors with user-driven transcript
        transcript = _write_transcript(
            tmp_path, "go ahead and just keep retrying these tests manually"
        )
        iterative_work.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "x"},
            "tool_result": "Error: failed",
            "transcript_path": transcript,
        })
        result = iterative_work.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "y"},
            "tool_result": "Error: failed",
            "transcript_path": transcript,
        })
        # User-driven imperative -> bypass
        assert result is None


# ---------------------------------------------------------------------------
# Sub-rule: mcp_auth_error
# Source: mcp-auth-error-guard.py (PostToolUse advisory on 2+ consecutive
# MCP auth/permission errors per server)
# Preservation:
#   - Per-server counter (extracted from mcp__<server>__<tool>)
#   - Auth error patterns (permission denied, unauthorized, 401, 403, etc.)
#   - Threshold: 2 consecutive failures -> advisory
#   - Success on same server resets counter
#   - Non-auth errors leave counter unchanged
#   - Non-MCP tools ignored
#   - ADVISORY: returns {"advisory": "..."}
# ---------------------------------------------------------------------------

class TestMcpAuthErrorSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import mcp_auth_error
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(mcp_auth_error, "TMP_DIR", state_dir)
        monkeypatch.setattr(
            mcp_auth_error, "STATE_FILE",
            state_dir / "mcp-auth-failures.json",
        )

    def test_first_auth_failure_no_nudge_yet(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import mcp_auth_error
        result = mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__list_tables",
            "tool_input": {},
            "tool_response": "permission denied for project",
        })
        assert result is None  # count=1, threshold=2

    def test_two_consecutive_auth_failures_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import mcp_auth_error
        mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__list_tables",
            "tool_input": {},
            "tool_response": "permission denied",
        })
        result = mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__execute_sql",
            "tool_input": {"query": "SELECT 1"},
            "tool_response": "401 Unauthorized",
        })
        assert result is not None
        assert "advisory" in result
        assert "mcp auth failure" in result["advisory"].lower()
        assert "claude_ai_Supabase" in result["advisory"]

    def test_non_mcp_tool_ignored(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import mcp_auth_error
        result = mcp_auth_error.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "x"},
            "tool_response": "permission denied",
        })
        assert result is None

    def test_success_resets_counter(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import mcp_auth_error
        # 1 auth failure
        mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__list_tables",
            "tool_input": {},
            "tool_response": "permission denied",
        })
        # success on same server resets
        mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__list_tables",
            "tool_input": {},
            "tool_response": '[{"name":"projects"}]',
        })
        # Next failure is count=1 again, no nudge
        result = mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__execute_sql",
            "tool_input": {"query": "x"},
            "tool_response": "401 Unauthorized",
        })
        assert result is None

    def test_non_auth_error_does_not_increment(self, tmp_path, monkeypatch):
        """A non-auth error (e.g., timeout, schema error) should not trigger this hook."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import mcp_auth_error
        # 1 auth failure
        mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__list_tables",
            "tool_input": {},
            "tool_response": "permission denied",
        })
        # Non-auth error
        result = mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__execute_sql",
            "tool_input": {"query": "x"},
            "tool_response": "syntax error at end of input",
        })
        # No nudge (counter stayed at 1)
        assert result is None

    def test_different_servers_have_independent_counters(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import mcp_auth_error
        # Server A: 1 failure
        mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__list_tables",
            "tool_input": {},
            "tool_response": "permission denied",
        })
        # Server B: 1 failure
        result_b = mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Slack__slack_send_message",
            "tool_input": {},
            "tool_response": "401 Unauthorized",
        })
        # Server B is independent, count=1, no nudge
        assert result_b is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import mcp_auth_error
        transcript = _write_transcript(
            tmp_path,
            "go ahead and let it fail repeatedly while I gather error samples",
        )
        mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__list_tables",
            "tool_input": {},
            "tool_response": "permission denied",
            "transcript_path": transcript,
        })
        result = mcp_auth_error.evaluate({
            "tool_name": "mcp__claude_ai_Supabase__execute_sql",
            "tool_input": {"query": "x"},
            "tool_response": "401 Unauthorized",
            "transcript_path": transcript,
        })
        # user-driven -> bypass
        assert result is None


# ---------------------------------------------------------------------------
# Sub-rule: plan_file_read (NEW from wr-sentinel-2026-04-30-008)
# Trigger: PreToolUse:Read on plan-file paths whose first ~30 lines declare
# 'REQUIRED SUB-SKILL' or 'superpowers:executing-plans'
# Preservation:
#   - Bypass: skill log (executing-plans / superpowers:executing-plans)
#   - Bypass: transcript phrase
#   - Once-per-session-per-file debounce
#   - ADVISORY: returns {"advisory": "..."}
# ---------------------------------------------------------------------------

class TestPlanFileReadSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import plan_file_read
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(plan_file_read, "TMP_DIR", state_dir)
        monkeypatch.setattr(
            plan_file_read, "STATE_FILE",
            state_dir / "plan-file-read-state.json",
        )

    def _make_plan_file(self, tmp_path, content, subdir="docs/plans"):
        plan_dir = tmp_path / subdir
        plan_dir.mkdir(parents=True, exist_ok=True)
        plan_path = plan_dir / "test-plan.md"
        plan_path.write_text(content, encoding="utf-8")
        return plan_path

    def test_plan_file_with_required_sub_skill_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import plan_file_read
        plan_path = self._make_plan_file(
            tmp_path,
            "# Plan\n\nREQUIRED SUB-SKILL: Use superpowers:executing-plans to implement.\n",
        )
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result
        assert "executing-plans" in result["advisory"].lower()

    def test_plan_file_with_executing_plans_phrase_triggers(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import plan_file_read
        plan_path = self._make_plan_file(
            tmp_path,
            "# My Plan\n\nWe will use superpowers:executing-plans for phase-by-phase implementation.\n",
        )
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result

    def test_global_claude_plans_path_triggers(self, tmp_path, monkeypatch):
        """~/.claude/plans/*.md style path."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import plan_file_read
        plan_path = self._make_plan_file(
            tmp_path,
            "REQUIRED SUB-SKILL: superpowers:executing-plans\n",
            subdir=".claude/plans",
        )
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None

    def test_non_plan_file_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import plan_file_read
        random_md = tmp_path / "notes.md"
        random_md.write_text(
            "# Random\nREQUIRED SUB-SKILL: superpowers:executing-plans\n",
            encoding="utf-8",
        )
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(random_md)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_plan_file_without_required_phrases_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import plan_file_read
        plan_path = self._make_plan_file(
            tmp_path,
            "# Plan\n\nThis is a regular plan with no skill requirement.\n",
        )
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_required_phrase_only_in_lines_after_30_does_not_trigger(self, tmp_path, monkeypatch):
        """First-30-lines window: phrases past line 30 don't fire."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import plan_file_read
        body = "# Plan\n" + ("filler line\n" * 35) + "REQUIRED SUB-SKILL: executing-plans\n"
        plan_path = self._make_plan_file(tmp_path, body)
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_skill_log_executing_plans(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        _write_skill_log(tmp_path, "executing-plans")
        from _dispatchers.methodology import plan_file_read
        plan_path = self._make_plan_file(
            tmp_path, "REQUIRED SUB-SKILL: superpowers:executing-plans\n"
        )
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_skill_log_superpowers_executing_plans(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        _write_skill_log(tmp_path, "superpowers:executing-plans")
        from _dispatchers.methodology import plan_file_read
        plan_path = self._make_plan_file(
            tmp_path, "REQUIRED SUB-SKILL: superpowers:executing-plans\n"
        )
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_debounce_per_file(self, tmp_path, monkeypatch):
        """Same plan file re-read in same session: nudges only once."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import plan_file_read
        plan_path = self._make_plan_file(
            tmp_path, "REQUIRED SUB-SKILL: superpowers:executing-plans\n"
        )
        first = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert first is not None
        second = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert second is None

    def test_non_read_tool_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import plan_file_read
        plan_path = self._make_plan_file(
            tmp_path, "REQUIRED SUB-SKILL: superpowers:executing-plans\n"
        )
        result = plan_file_read.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(plan_path), "content": "x" * 250},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import plan_file_read
        plan_path = self._make_plan_file(
            tmp_path, "REQUIRED SUB-SKILL: superpowers:executing-plans\n"
        )
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_path)},
            "transcript_path": _write_transcript(
                tmp_path,
                f"go ahead and read {plan_path.name} so we can review the structure",
            ),
        })
        assert result is None


# ---------------------------------------------------------------------------
# Sub-rule: multi_file_build (NEW from wr-sentinel-2026-05-04-009 first half)
# Trigger: PreToolUse:Edit|Write. Tracks distinct file-type categories
# (spec, tool, bat, vbs, doc) written across the session. Crosses 5 ->
# advisory nudge to invoke superpowers:writing-plans.
# Preservation: bypass via skill log (writing-plans /
# superpowers:writing-plans), transcript phrase, intent_detection.
# Severity: ADVISORY.
# ---------------------------------------------------------------------------

class TestMultiFileBuildSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import multi_file_build
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(multi_file_build, "TMP_DIR", state_dir)
        monkeypatch.setattr(
            multi_file_build, "STATE_FILE",
            state_dir / "multi-file-build-state.json",
        )

    def _write(self, file_path, transcript_path, content="content"):
        return {
            "tool_name": "Write",
            "tool_input": {"file_path": str(file_path), "content": content},
            "transcript_path": transcript_path,
        }

    def test_below_threshold_does_not_trigger(self, tmp_path, monkeypatch):
        """4 distinct categories -- under threshold of 5."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(tmp_path, "ok")
        paths = [
            tmp_path / "docs" / "specs" / "x.md",
            tmp_path / "tools" / "y.py",
            tmp_path / "scripts" / "z.bat",
            tmp_path / "scripts" / "w.vbs",
        ]
        last_result = None
        for p in paths:
            p.parent.mkdir(parents=True, exist_ok=True)
            last_result = multi_file_build.evaluate(self._write(p, transcript))
        assert last_result is None

    def test_5_distinct_file_types_triggers_advisory(self, tmp_path, monkeypatch):
        """spec + tool + bat + vbs + doc = 5 categories -> advisory."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(tmp_path, "ok")
        paths = [
            tmp_path / "docs" / "specs" / "x.md",
            tmp_path / "tools" / "y.py",
            tmp_path / "scripts" / "z.bat",
            tmp_path / "scripts" / "w.vbs",
            tmp_path / "docs" / "guide.md",
        ]
        last_result = None
        for p in paths:
            p.parent.mkdir(parents=True, exist_ok=True)
            last_result = multi_file_build.evaluate(self._write(p, transcript))
        assert last_result is not None
        assert "advisory" in last_result
        assert "writing-plans" in last_result["advisory"].lower()

    def test_5_writes_same_category_does_not_trigger(self, tmp_path, monkeypatch):
        """5 .py files all under tools/ = 1 category, no nudge."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(tmp_path, "ok")
        last_result = None
        for i in range(5):
            p = tmp_path / "tools" / f"f{i}.py"
            p.parent.mkdir(parents=True, exist_ok=True)
            last_result = multi_file_build.evaluate(self._write(p, transcript))
        assert last_result is None

    def test_classification_spec_path(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import multi_file_build
        assert multi_file_build._classify("/x/docs/superpowers/specs/foo.md") == "spec"
        assert multi_file_build._classify("/y/specs/bar.md") == "spec"

    def test_classification_tool_path(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import multi_file_build
        assert multi_file_build._classify("/repo/tools/foo.py") == "tool"
        assert multi_file_build._classify("/repo/scripts/bar.py") == "tool"

    def test_classification_bat_and_vbs(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import multi_file_build
        assert multi_file_build._classify("/x/silent.bat") == "bat"
        assert multi_file_build._classify("/x/runner.vbs") == "vbs"

    def test_classification_doc_path(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import multi_file_build
        assert multi_file_build._classify("/repo/docs/guide.md") == "doc"

    def test_classification_unrecognized_returns_none(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import multi_file_build
        assert multi_file_build._classify("/repo/src/main.go") is None
        assert multi_file_build._classify("/repo/random.txt") is None
        assert multi_file_build._classify("") is None

    def test_bypass_via_skill_log_writing_plans(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        # Place skill log in TMP_DIR (state_dir) per dispatcher convention
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = tmp_path / ".tmp" / f"skill-invocations-{today}.json"
        log_path.write_text(
            json.dumps({"invocations": [{"skill": "writing-plans"}]}),
            encoding="utf-8",
        )
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(tmp_path, "ok")
        paths = [
            tmp_path / "docs" / "specs" / "x.md",
            tmp_path / "tools" / "y.py",
            tmp_path / "scripts" / "z.bat",
            tmp_path / "scripts" / "w.vbs",
            tmp_path / "docs" / "guide.md",
        ]
        last_result = None
        for p in paths:
            p.parent.mkdir(parents=True, exist_ok=True)
            last_result = multi_file_build.evaluate(self._write(p, transcript))
        assert last_result is None

    def test_bypass_via_skill_log_superpowers_writing_plans(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = tmp_path / ".tmp" / f"skill-invocations-{today}.json"
        log_path.write_text(
            json.dumps({"invocations": [{"skill": "superpowers:writing-plans"}]}),
            encoding="utf-8",
        )
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(tmp_path, "ok")
        paths = [
            tmp_path / "docs" / "specs" / "x.md",
            tmp_path / "tools" / "y.py",
            tmp_path / "scripts" / "z.bat",
            tmp_path / "scripts" / "w.vbs",
            tmp_path / "docs" / "guide.md",
        ]
        last_result = None
        for p in paths:
            p.parent.mkdir(parents=True, exist_ok=True)
            last_result = multi_file_build.evaluate(self._write(p, transcript))
        assert last_result is None

    def test_bypass_via_transcript_phrase(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(tmp_path, "skip multi-file-build")
        paths = [
            tmp_path / "docs" / "specs" / "x.md",
            tmp_path / "tools" / "y.py",
            tmp_path / "scripts" / "z.bat",
            tmp_path / "scripts" / "w.vbs",
            tmp_path / "docs" / "guide.md",
        ]
        last_result = None
        for p in paths:
            p.parent.mkdir(parents=True, exist_ok=True)
            last_result = multi_file_build.evaluate(self._write(p, transcript))
        assert last_result is None

    def test_debounce_once_per_session(self, tmp_path, monkeypatch):
        """First crossing nudges; subsequent writes do not re-nudge."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(tmp_path, "ok")
        paths = [
            tmp_path / "docs" / "specs" / "x.md",
            tmp_path / "tools" / "y.py",
            tmp_path / "scripts" / "z.bat",
            tmp_path / "scripts" / "w.vbs",
            tmp_path / "docs" / "guide.md",
        ]
        first_nudge = None
        for p in paths:
            p.parent.mkdir(parents=True, exist_ok=True)
            r = multi_file_build.evaluate(self._write(p, transcript))
            if r is not None:
                first_nudge = r
        assert first_nudge is not None
        # Add a 6th distinct category-equivalent write (another doc); should be debounced
        extra = tmp_path / "docs" / "another.md"
        result2 = multi_file_build.evaluate(self._write(extra, transcript))
        assert result2 is None

    def test_non_write_edit_tool_ignored(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(tmp_path, "ok")
        result = multi_file_build.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
            "transcript_path": transcript,
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(
            tmp_path,
            "go ahead and create all the files we agreed on for this build",
        )
        paths = [
            tmp_path / "docs" / "specs" / "x.md",
            tmp_path / "tools" / "y.py",
            tmp_path / "scripts" / "z.bat",
            tmp_path / "scripts" / "w.vbs",
            tmp_path / "docs" / "guide.md",
        ]
        last_result = None
        for p in paths:
            p.parent.mkdir(parents=True, exist_ok=True)
            last_result = multi_file_build.evaluate(self._write(p, transcript))
        assert last_result is None

    def test_edit_tool_also_counts(self, tmp_path, monkeypatch):
        """Edit tool counts toward threshold same as Write."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import multi_file_build
        transcript = _write_transcript(tmp_path, "ok")
        # 4 Writes + 1 Edit on a different category
        paths_writes = [
            tmp_path / "docs" / "specs" / "x.md",
            tmp_path / "tools" / "y.py",
            tmp_path / "scripts" / "z.bat",
            tmp_path / "scripts" / "w.vbs",
        ]
        for p in paths_writes:
            p.parent.mkdir(parents=True, exist_ok=True)
            multi_file_build.evaluate(self._write(p, transcript))
        # 5th: Edit on a doc -- should push to threshold and nudge
        edit_path = tmp_path / "docs" / "guide.md"
        edit_path.parent.mkdir(parents=True, exist_ok=True)
        result = multi_file_build.evaluate({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(edit_path),
                "old_string": "x", "new_string": "y",
            },
            "transcript_path": transcript,
        })
        assert result is not None
        assert "advisory" in result


# ---------------------------------------------------------------------------
# Sub-rule: production_tool (NEW from wr-sentinel-2026-05-04-009 second half)
# Trigger: PreToolUse:Edit|Write on Python files under /tools/ or /scripts/
# whose content shows production-impact patterns (urllib.request import,
# HTTP PATCH verb, or Supabase execute_sql / apply_migration call) AND no
# matching test_<basename>.py file exists. Advisory pointing to
# testing-strategy / test-driven-development skill.
# ---------------------------------------------------------------------------

class TestProductionToolSubRule:
    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import production_tool
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(production_tool, "TMP_DIR", state_dir)
        monkeypatch.setattr(
            production_tool, "STATE_FILE",
            state_dir / "production-tool-state.json",
        )

    def _make_tool(self, tmp_path, name="ship_data.py", content="import sys\n"):
        tool_dir = tmp_path / "tools"
        tool_dir.mkdir(parents=True, exist_ok=True)
        tool_path = tool_dir / name
        tool_path.write_text(content, encoding="utf-8")
        return tool_path

    def _make_test(self, tmp_path, basename):
        test_dir = tmp_path / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_path = test_dir / f"test_{basename}.py"
        test_path.write_text("def test_x(): pass\n", encoding="utf-8")
        return test_path

    def test_urllib_request_no_test_triggers(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path)
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "import urllib.request\nurllib.request.urlopen('http://x')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result
        assert "test" in result["advisory"].lower()

    def test_http_patch_no_test_triggers(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path, name="patcher.py")
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "import requests\nrequests.patch(url, json={'a':1})\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "PATCH" in result["advisory"]

    def test_method_eq_patch_string_triggers(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path, name="updater.py")
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "method='PATCH'\nmake_req(url, method=method)\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None

    def test_execute_sql_no_test_triggers(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path, name="db_writer.py")
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "from db import execute_sql\nexecute_sql('UPDATE users SET x=1')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "execute_sql" in result["advisory"] or "SQL" in result["advisory"]

    def test_existing_test_file_does_not_trigger(self, tmp_path, monkeypatch):
        """tests/test_<basename>.py exists -> no nudge."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path, name="db_writer.py")
        self._make_test(tmp_path, "db_writer")
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "from db import execute_sql\nexecute_sql('UPDATE x')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_non_python_file_does_not_trigger(self, tmp_path, monkeypatch):
        """JS file under tools/ -- pattern is Python-specific."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool_dir = tmp_path / "tools"
        tool_dir.mkdir(parents=True, exist_ok=True)
        js_tool = tool_dir / "ship.js"
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(js_tool),
                "content": "fetch(url, {method:'PATCH'})",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_non_tools_path_does_not_trigger(self, tmp_path, monkeypatch):
        """Python file outside /tools/ or /scripts/ -- not a tool."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        random_dir = tmp_path / "src"
        random_dir.mkdir(parents=True, exist_ok=True)
        py_file = random_dir / "main.py"
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(py_file),
                "content": "import urllib.request\nurllib.request.urlopen('http://x')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_python_without_dangerous_patterns_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path)
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "import os\nimport json\nprint('hello')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_skill_log_test_driven_development(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = tmp_path / ".tmp" / f"skill-invocations-{today}.json"
        log_path.write_text(
            json.dumps({"invocations": [{"skill": "test-driven-development"}]}),
            encoding="utf-8",
        )
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path)
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "import urllib.request\nurllib.request.urlopen('http://x')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_skill_log_superpowers_test_driven_development(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = tmp_path / ".tmp" / f"skill-invocations-{today}.json"
        log_path.write_text(
            json.dumps({"invocations": [{"skill": "superpowers:test-driven-development"}]}),
            encoding="utf-8",
        )
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path)
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "import urllib.request\nurllib.request.urlopen('http://x')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_transcript_phrase(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path)
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "import urllib.request\nurllib.request.urlopen('http://x')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "skip production-tool"),
        })
        assert result is None

    def test_debounce_per_file(self, tmp_path, monkeypatch):
        """Same tool re-edited in same session: nudges only once."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path)
        first = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "import urllib.request\nurllib.request.urlopen('http://x')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert first is not None
        second = production_tool.evaluate({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(tool),
                "old_string": "x",
                "new_string": "import urllib.request\nurllib.request.urlopen('http://y')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert second is None

    def test_non_write_edit_tool_ignored(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        result = production_tool.evaluate({
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import production_tool
        tool = self._make_tool(tmp_path)
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool),
                "content": "import urllib.request\nurllib.request.urlopen('http://x')\n",
            },
            "transcript_path": _write_transcript(
                tmp_path,
                f"go ahead and ship {tool.name} we will write tests after",
            ),
        })
        assert result is None


# ---------------------------------------------------------------------------
# Sub-rule: creation_gate (NEW unifies hook + verification-before-build)
# Source absorption:
#   Tier 1 - hook-development-enforcer.py: HARD GATE on new ~/.claude/hooks/*.py
#   Tier 2 - verification-before-build-enforcer.py: ADVISORY on infra writes
#            without recent preflight-check.py
# Spec: docs/superpowers/specs/2026-05-05-hook-dispatcher-consolidation-spec.md
# ---------------------------------------------------------------------------

class TestCreationGateSubRuleHookTier:
    """Tier 1: hook-creation HARD GATE."""

    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import creation_gate
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(creation_gate, "TMP_DIR", state_dir)
        monkeypatch.setattr(
            creation_gate, "PREFLIGHT_STATE_FILE",
            state_dir / "creation-gate-preflight-state.json",
        )
        # Use isolated preflight marker so absent file = no recent preflight
        marker = tmp_path / "preflight_invocations.jsonl"
        monkeypatch.setattr(creation_gate, "PREFLIGHT_MARKER_PATH", marker)

    def test_new_hook_write_without_skill_blocks(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        # Use a path that contains .claude/hooks/ but does NOT yet exist
        hook_path = tmp_path / ".claude" / "hooks" / "new_hook.py"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        # Do NOT create the file -- new-hook detection requires non-existence
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(hook_path),
                "content": "# new hook code\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "decision" in result
        assert result["decision"] == "deny"
        assert "hook-development" in result["reason"]

    def test_existing_hook_edit_does_not_trigger(self, tmp_path, monkeypatch):
        """Hook tier only fires on Write to NEW files; edits / Write-overwrites pass."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        hook_path = tmp_path / ".claude" / "hooks" / "existing_hook.py"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text("# existing\n", encoding="utf-8")
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(hook_path),
                "content": "# updated\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        # Hook tier passes (file exists). May still emit Tier 2 advisory; that's fine.
        # Confirm if a result, it's NOT a hook-tier deny.
        if result is not None and "decision" in result:
            assert "deny" not in str(result).lower() or "hook-development" not in str(result)

    def test_edit_tool_on_new_hook_does_not_trigger(self, tmp_path, monkeypatch):
        """Hook tier is Write-only; Edit tool ignored."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        hook_path = tmp_path / ".claude" / "hooks" / "x.py"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(hook_path),
                "old_string": "x", "new_string": "y",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        # Should not be a hook-tier deny
        if result is not None:
            assert result.get("decision") != "deny"

    def test_meta_path_exempt(self, tmp_path, monkeypatch):
        """Files under /.work-requests/ etc. are structurally exempt."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        meta_path = tmp_path / ".work-requests" / ".claude" / "hooks" / "draft.py"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(meta_path),
                "content": "# meta\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        # Should NOT deny (meta path exempt). May not advise either.
        if result is not None:
            assert result.get("decision") != "deny"

    def test_test_file_path_exempt(self, tmp_path, monkeypatch):
        """Files matching tests/.../hook*.py are not 'hook' files."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        test_path = tmp_path / "tests" / "test_hook_things.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(test_path),
                "content": "def test_x(): pass\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        # No hook-tier deny
        if result is not None:
            assert result.get("decision") != "deny"

    def test_bypass_via_skill_log_hook_development(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = tmp_path / ".tmp" / f"skill-invocations-{today}.json"
        log_path.write_text(
            json.dumps({"invocations": [{"skill": "hook-development"}]}),
            encoding="utf-8",
        )
        from _dispatchers.methodology import creation_gate
        hook_path = tmp_path / ".claude" / "hooks" / "new_hook.py"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(hook_path),
                "content": "# new hook\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        # Hook tier bypassed; may emit Tier 2 preflight advisory but not a deny
        if result is not None:
            assert result.get("decision") != "deny"

    def test_bypass_via_skill_log_plugin_dev_namespace(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = tmp_path / ".tmp" / f"skill-invocations-{today}.json"
        log_path.write_text(
            json.dumps({"invocations": [{"skill": "plugin-dev:hook-development"}]}),
            encoding="utf-8",
        )
        from _dispatchers.methodology import creation_gate
        hook_path = tmp_path / ".claude" / "hooks" / "new_hook.py"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(hook_path),
                "content": "# new hook\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        if result is not None:
            assert result.get("decision") != "deny"

    def test_bypass_via_transcript_phrase(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        hook_path = tmp_path / ".claude" / "hooks" / "new_hook.py"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(hook_path),
                "content": "# new hook\n",
            },
            "transcript_path": _write_transcript(tmp_path, "skip hook-development"),
        })
        if result is not None:
            assert result.get("decision") != "deny"

    def test_bypass_via_content_phrase(self, tmp_path, monkeypatch):
        """Phrase in the file content (for filing gap reports about hooks)."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        hook_path = tmp_path / ".claude" / "hooks" / "new_hook.py"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(hook_path),
                "content": "# skip hook-development -- this is a gap report\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        if result is not None:
            assert result.get("decision") != "deny"

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER: user-driven imperative bypass on hook tier."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        hook_path = tmp_path / ".claude" / "hooks" / "new_hook.py"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(hook_path),
                "content": "# new hook\n",
            },
            "transcript_path": _write_transcript(
                tmp_path,
                f"go ahead and create {hook_path.name} we already discussed it",
            ),
        })
        if result is not None:
            assert result.get("decision") != "deny"

    def test_non_hook_path_does_not_trigger_hook_tier(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        random_path = tmp_path / "src" / "main.py"
        random_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(random_path),
                "content": "# regular code\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        # No hook-tier deny
        if result is not None:
            assert result.get("decision") != "deny"


class TestCreationGateSubRulePreflightTier:
    """Tier 2: verification-before-build ADVISORY."""

    def _isolate_state(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import creation_gate
        state_dir = tmp_path / ".tmp"
        state_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(creation_gate, "TMP_DIR", state_dir)
        monkeypatch.setattr(
            creation_gate, "PREFLIGHT_STATE_FILE",
            state_dir / "creation-gate-preflight-state.json",
        )
        marker = tmp_path / "preflight_invocations.jsonl"
        monkeypatch.setattr(creation_gate, "PREFLIGHT_MARKER_PATH", marker)
        return marker

    def test_new_script_without_recent_preflight_triggers_advisory(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        # An ~/.claude/scripts/-shaped path (no real fs creation needed)
        script_path = tmp_path / ".claude" / "scripts" / "new_tool.py"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(script_path),
                "content": "import sys\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result
        assert "preflight" in result["advisory"].lower()

    def test_workspace_tool_path_triggers(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        tool_path = tmp_path / "tools" / "ship.py"
        tool_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool_path),
                "content": "import sys\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result

    def test_workflow_md_path_triggers(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        wf_path = tmp_path / "workflows" / "new-sop.md"
        wf_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(wf_path),
                "content": "# SOP\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result

    def test_recent_preflight_suppresses_advisory(self, tmp_path, monkeypatch):
        marker = self._isolate_state(tmp_path, monkeypatch)
        # Write a recent preflight invocation into the marker file
        from datetime import datetime
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            json.dumps({"timestamp": datetime.now().isoformat()}) + "\n",
            encoding="utf-8",
        )
        from _dispatchers.methodology import creation_gate
        tool_path = tmp_path / "tools" / "ship.py"
        tool_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool_path),
                "content": "import sys\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_old_preflight_does_not_suppress(self, tmp_path, monkeypatch):
        """Preflight older than 90 minutes does not suppress."""
        marker = self._isolate_state(tmp_path, monkeypatch)
        from datetime import datetime, timedelta
        marker.parent.mkdir(parents=True, exist_ok=True)
        old_ts = (datetime.now() - timedelta(hours=2)).isoformat()
        marker.write_text(
            json.dumps({"timestamp": old_ts}) + "\n",
            encoding="utf-8",
        )
        from _dispatchers.methodology import creation_gate
        tool_path = tmp_path / "tools" / "ship.py"
        tool_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool_path),
                "content": "import sys\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is not None
        assert "advisory" in result

    def test_per_path_debounce(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        tool_path = tmp_path / "tools" / "ship.py"
        tool_path.parent.mkdir(parents=True, exist_ok=True)
        first = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool_path),
                "content": "import sys\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert first is not None
        second = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool_path),
                "content": "import sys\nimport os\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert second is None

    def test_non_infra_path_does_not_trigger(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        random_path = tmp_path / "src" / "main.py"
        random_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(random_path),
                "content": "import sys\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        assert result is None

    def test_bypass_via_transcript_phrase(self, tmp_path, monkeypatch):
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        tool_path = tmp_path / "tools" / "ship.py"
        tool_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool_path),
                "content": "import sys\n",
            },
            "transcript_path": _write_transcript(tmp_path, "skip preflight"),
        })
        assert result is None

    def test_intent_detection_user_driven_bypass(self, tmp_path, monkeypatch):
        """NEW LAYER on preflight tier."""
        self._isolate_state(tmp_path, monkeypatch)
        from _dispatchers.methodology import creation_gate
        tool_path = tmp_path / "tools" / "ship.py"
        tool_path.parent.mkdir(parents=True, exist_ok=True)
        result = creation_gate.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tool_path),
                "content": "import sys\n",
            },
            "transcript_path": _write_transcript(
                tmp_path,
                f"go ahead and create {tool_path.name} I already checked existing tools",
            ),
        })
        assert result is None


# ---------------------------------------------------------------------------
# TestDispatcher: top-level methodology-dispatcher.py orchestration
# Verifies routing, HARD GATE short-circuit, advisory concatenation,
# graceful degradation, and event-class filtering.
# ---------------------------------------------------------------------------

class TestDispatcher:
    """Tests for methodology-dispatcher.py top-level entry."""

    def _import_dispatcher(self):
        """Import methodology-dispatcher.py as a module despite the dash in filename."""
        import importlib.util
        path = os.path.expanduser("~/.claude/hooks/methodology-dispatcher.py")
        spec = importlib.util.spec_from_file_location("methodology_dispatcher", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_unknown_event_returns_none(self, tmp_path):
        d = self._import_dispatcher()
        assert d.dispatch({"hook_event_name": "UnknownEvent"}) is None

    def test_no_subrule_contributions_returns_none(self, tmp_path):
        """Bash command with no triggers -> no advisories -> None."""
        d = self._import_dispatcher()
        result = d.dispatch({
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "echo hi"},
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        # No applicable sub-rule fires for Bash on PreToolUse (sub-rules
        # filter internally; brainstorming wants Write, etc.)
        assert result is None

    def test_hard_gate_short_circuits(self, tmp_path, monkeypatch):
        """First sub-rule that returns deny short-circuits the rest."""
        d = self._import_dispatcher()

        # Stub two sub-rules: first returns deny, second would assert called
        called = {"second": False}

        class StubFirst:
            @staticmethod
            def evaluate(payload):
                return {"decision": "deny", "reason": "stub deny reason"}

        class StubSecond:
            @staticmethod
            def evaluate(payload):
                called["second"] = True
                return {"advisory": "should not appear"}

        monkeypatch.setattr(d, "PRE_TOOL_USE_SUBRULES", [StubFirst, StubSecond])
        monkeypatch.setattr(
            d, "EVENT_TO_SUBRULES",
            {"PreToolUse": [StubFirst, StubSecond]},
        )

        result = d.dispatch({
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "/x", "content": "y"},
        })
        assert result is not None
        ho = result["hookSpecificOutput"]
        assert ho["hookEventName"] == "PreToolUse"
        assert ho["permissionDecision"] == "deny"
        assert "stub deny reason" in ho["permissionDecisionReason"]
        # Second sub-rule must NOT have been called (short-circuit)
        assert called["second"] is False

    def test_multiple_advisories_concatenate(self, tmp_path, monkeypatch):
        d = self._import_dispatcher()

        class StubA:
            @staticmethod
            def evaluate(payload):
                return {"advisory": "first advisory text"}

        class StubB:
            @staticmethod
            def evaluate(payload):
                return None

        class StubC:
            @staticmethod
            def evaluate(payload):
                return {"advisory": "third advisory text"}

        monkeypatch.setattr(
            d, "EVENT_TO_SUBRULES",
            {"PreToolUse": [StubA, StubB, StubC]},
        )

        result = d.dispatch({
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "/x", "content": "y"},
        })
        assert result is not None
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "first advisory text" in ctx
        assert "third advisory text" in ctx
        assert "---" in ctx  # separator

    def test_subrule_exception_does_not_crash(self, tmp_path, monkeypatch):
        d = self._import_dispatcher()

        class StubBoom:
            @staticmethod
            def evaluate(payload):
                raise RuntimeError("kaboom")

        class StubGood:
            @staticmethod
            def evaluate(payload):
                return {"advisory": "good advisory"}

        monkeypatch.setattr(
            d, "EVENT_TO_SUBRULES",
            {"PreToolUse": [StubBoom, StubGood]},
        )

        result = d.dispatch({
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "/x", "content": "y"},
        })
        # Boom is suppressed; Good still runs
        assert result is not None
        assert "good advisory" in result["hookSpecificOutput"]["additionalContext"]

    def test_post_tool_use_routes_to_correct_subrules(self, tmp_path, monkeypatch):
        d = self._import_dispatcher()

        called = []

        class StubPost:
            @staticmethod
            def evaluate(payload):
                called.append("post")
                return None

        class StubPre:
            @staticmethod
            def evaluate(payload):
                called.append("pre")
                return None

        monkeypatch.setattr(
            d, "EVENT_TO_SUBRULES",
            {"PreToolUse": [StubPre], "PostToolUse": [StubPost]},
        )

        d.dispatch({
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
            "tool_response": "",
        })
        assert called == ["post"]

    def test_user_prompt_submit_routes(self, tmp_path, monkeypatch):
        d = self._import_dispatcher()

        called = []

        class StubUPS:
            @staticmethod
            def evaluate(payload):
                called.append("ups")
                return None

        monkeypatch.setattr(
            d, "EVENT_TO_SUBRULES",
            {"UserPromptSubmit": [StubUPS]},
        )

        d.dispatch({
            "hook_event_name": "UserPromptSubmit",
            "user_prompt": "test",
        })
        assert called == ["ups"]

    def test_failed_import_subrule_skipped(self, tmp_path, monkeypatch):
        """If a sub-rule failed to import (None in the list), it's skipped."""
        d = self._import_dispatcher()

        class StubGood:
            @staticmethod
            def evaluate(payload):
                return {"advisory": "good"}

        monkeypatch.setattr(
            d, "EVENT_TO_SUBRULES",
            {"PreToolUse": [None, StubGood, None]},
        )

        result = d.dispatch({
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "/x", "content": "y"},
        })
        assert result is not None
        assert "good" in result["hookSpecificOutput"]["additionalContext"]

    def test_real_subrules_loaded_for_pre_tool_use(self, tmp_path):
        """Sanity: actual PRE_TOOL_USE_SUBRULES list is populated post-import."""
        d = self._import_dispatcher()
        # All 10 PreToolUse sub-rules should have imported successfully.
        # Filter Nones (none expected, but graceful).
        loaded = [s for s in d.PRE_TOOL_USE_SUBRULES if s is not None]
        assert len(loaded) == 10

    def test_real_dispatcher_does_not_crash_on_pre_tool_use_write(self, tmp_path):
        """End-to-end smoke: dispatcher accepts a real PreToolUse:Write payload
        and returns either None or a valid hookSpecificOutput dict without
        crashing. Specific sub-rule outcomes depend on each sub-rule's internal
        bypass and threshold logic; this test just verifies the dispatcher
        plumbing works against the live sub-rule chain."""
        d = self._import_dispatcher()
        plan_path = tmp_path / "src" / "main.py"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        result = d.dispatch({
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(plan_path),
                "content": "import os\nprint('hello')\n",
            },
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        # Either None (no sub-rule fired) or valid output structure
        if result is not None:
            assert "hookSpecificOutput" in result
            ho = result["hookSpecificOutput"]
            assert "hookEventName" in ho
            assert "permissionDecision" in ho or "additionalContext" in ho

    def test_real_dispatcher_post_tool_use_smoke(self, tmp_path):
        """End-to-end smoke for PostToolUse routing."""
        d = self._import_dispatcher()
        result = d.dispatch({
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "echo hi"},
            "tool_response": "hi",
            "transcript_path": _write_transcript(tmp_path, "ok"),
        })
        # Smoke: doesn't crash; result is None or valid
        if result is not None:
            assert "hookSpecificOutput" in result
