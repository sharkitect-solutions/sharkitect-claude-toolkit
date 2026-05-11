"""Tests for rule-file-self-audit-gate.py (Task 0.5 of Post-Hard-Stop System Reassessment).

Plan: 3.- Skill Management Hub/docs/superpowers/plans/2026-05-11-post-hard-stop-system-reassessment.md
Spec source: ~/.claude/rules/universal-protocols.md "Post-Action Self-Audit on Rule-Class Files"
             + "Strict Bypass Vocabulary for Runtime Audits"
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


HOOK_PATH = Path(os.path.expanduser("~/.claude/hooks/rule-file-self-audit-gate.py"))


def _load_hook():
    spec = importlib.util.spec_from_file_location("rule_file_self_audit_gate", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_hook_subprocess(payload: dict) -> tuple[int, str, str]:
    """Run hook as subprocess like real PostToolUse would. Returns (exit, stdout, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=10,
    )
    return proc.returncode, proc.stdout, proc.stderr


# ----------------------------------------------------------------------------
# evaluate() — per-file-class checklist injection
# ----------------------------------------------------------------------------

def test_fires_on_universal_protocols_edit_with_checklist():
    """Editing universal-protocols.md surfaces the contradiction-check checklist."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/home/user/.claude/rules/universal-protocols.md"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is not None
    ctx = result.additional_context.lower()
    assert "contradiction" in ctx
    assert "did you" in ctx
    assert "grep" in ctx


def test_fires_on_lessons_learned_edit():
    """Editing lessons-learned.md surfaces the lessons checklist."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/home/user/.claude/lessons-learned.md"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is not None
    ctx = result.additional_context.lower()
    assert "categor" in ctx  # "categories" or "category"
    assert "contradict" in ctx


def test_fires_on_workspace_claude_md_edit():
    """Editing a workspace CLAUDE.md surfaces the cross-workspace consistency checklist."""
    hook = _load_hook()
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/CLAUDE.md"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is not None
    ctx = result.additional_context.lower()
    assert "universal-protocols" in ctx or "sibling" in ctx


def test_fires_on_workspace_memory_md_edit():
    """Editing workspace MEMORY.md surfaces the 200-line cap checklist."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "C:/Users/Sharkitect Digital/.claude/projects/foo/memory/MEMORY.md"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is not None
    ctx = result.additional_context.lower()
    assert "200" in ctx or "line cap" in ctx


def test_fires_on_memory_topic_file_edit():
    """Editing a memory/ topic file surfaces sibling-overlap checklist."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "C:/Users/Sharkitect Digital/.claude/projects/foo/memory/feedback_something.md"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is not None
    ctx = result.additional_context.lower()
    assert "sibling" in ctx or "overlap" in ctx


def test_fires_on_settings_json_edit():
    """Editing settings.json surfaces the allow/deny intersection checklist."""
    hook = _load_hook()
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/home/user/.claude/settings.json"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is not None
    ctx = result.additional_context.lower()
    assert "allow" in ctx and "deny" in ctx
    assert "backup" in ctx


def test_fires_on_workspace_settings_local_edit():
    """Editing a workspace .claude/settings.local.json surfaces settings checklist."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "C:/path/workspace/.claude/settings.local.json"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is not None
    ctx = result.additional_context.lower()
    assert "allow" in ctx and "deny" in ctx


def test_fires_on_plans_registry_edit():
    """Editing plans-registry.md surfaces classification + duplicate checklist."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/home/user/.claude/docs/plans-registry.md"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is not None
    ctx = result.additional_context.lower()
    assert "active" in ctx or "completed" in ctx or "duplicate" in ctx


def test_fires_on_rules_subdir_file():
    """Editing any file under ~/.claude/rules/ surfaces a checklist."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/home/user/.claude/rules/context7.md"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is not None


def test_no_fire_on_non_rule_file():
    """Editing a normal source file does NOT fire."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/home/user/project/src/foo.py"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is None


def test_no_fire_on_non_edit_tool():
    """Reading a rule file does NOT fire (only Edit/Write trigger)."""
    hook = _load_hook()
    payload = {
        "tool_name": "Read",
        "tool_input": {"file_path": "/home/user/.claude/rules/universal-protocols.md"},
    }
    result = hook.evaluate(payload)
    assert result.additional_context is None


def test_emits_strict_bypass_vocabulary_requirement():
    """The injected context must reference Category A/B/C/D bypass vocabulary."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/home/user/.claude/rules/universal-protocols.md"},
    }
    result = hook.evaluate(payload)
    ctx = result.additional_context.lower()
    # Strict Bypass Vocabulary requires specific category match
    assert "category" in ctx
    # Should mention at least one of A/B/C/D or the strict bypass vocabulary
    assert any(c in result.additional_context for c in ["A", "B", "C", "D"])


def test_emits_honest_answer_prompt():
    """The injected context must include an explicit honest-answer prompt."""
    hook = _load_hook()
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/home/user/.claude/rules/universal-protocols.md"},
    }
    result = hook.evaluate(payload)
    ctx = result.additional_context.lower()
    # Honest answer prompt: "did you complete each item BEFORE this edit?"
    assert "before" in ctx
    assert "honest" in ctx or "did you" in ctx


# ----------------------------------------------------------------------------
# validate_bypass() — loose-excuse catcher
# ----------------------------------------------------------------------------

def test_rejects_loose_excuse_bypass():
    """Bypass without Category A/B/C/D justification is rejected."""
    hook = _load_hook()
    result = hook.validate_bypass("I already verified this earlier")
    assert result.valid is False
    assert "category" in result.rejection_reason.lower()


def test_rejects_just_this_once():
    """'Just this once' is categorically invalid."""
    hook = _load_hook()
    result = hook.validate_bypass("Just this once, the edit is trivial")
    assert result.valid is False
    assert "category" in result.rejection_reason.lower()


def test_rejects_small_edit_rationalization():
    """'This is a small edit' is AI self-justification — invalid."""
    hook = _load_hook()
    result = hook.validate_bypass("This is a small edit, doesn't need the check")
    assert result.valid is False


def test_rejects_we_already_did_this():
    """'We already ran this scan earlier' is excuse, not bypass."""
    hook = _load_hook()
    result = hook.validate_bypass("We already ran this scan earlier in the session")
    assert result.valid is False


def test_rejects_user_implied():
    """'The user implied' is invalid — implied != explicit."""
    hook = _load_hook()
    result = hook.validate_bypass("The user implied we should skip")
    assert result.valid is False


def test_accepts_category_a_explicit_user_direction():
    """Category A: explicit user direction with skip phrase is valid."""
    hook = _load_hook()
    result = hook.validate_bypass(
        "Category A: user said 'skip rule-self-audit' in current session"
    )
    assert result.valid is True


def test_accepts_category_b_emergency_repair():
    """Category B: emergency manual repair is valid."""
    hook = _load_hook()
    result = hook.validate_bypass(
        "Category B: Emergency manual repair to fix brain row missing after drift correction"
    )
    assert result.valid is True


def test_accepts_category_c_self_referential_meta_edit():
    """Category C: editing the gate's own infrastructure is valid."""
    hook = _load_hook()
    result = hook.validate_bypass(
        "Category C: Self-referential meta-edit — editing rule-file-self-audit-gate.py itself"
    )
    assert result.valid is True


def test_accepts_category_d_standing_exemption():
    """Category D: documented standing exemption is valid."""
    hook = _load_hook()
    result = hook.validate_bypass(
        "Category D: Standing exemption — completion-notification routed-tasks per documented protocol"
    )
    assert result.valid is True


def test_empty_justification_rejected():
    """Empty bypass justification is rejected."""
    hook = _load_hook()
    result = hook.validate_bypass("")
    assert result.valid is False


def test_validate_bypass_returns_namespace_with_required_fields():
    """validate_bypass result must expose .valid and .rejection_reason."""
    hook = _load_hook()
    result = hook.validate_bypass("anything")
    assert hasattr(result, "valid")
    assert hasattr(result, "rejection_reason")


# ----------------------------------------------------------------------------
# Subprocess (real PostToolUse) integration
# ----------------------------------------------------------------------------

def test_subprocess_emits_additional_context_on_universal_protocols_edit():
    """Run the hook as a real subprocess. stdout must contain additionalContext JSON."""
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/home/user/.claude/rules/universal-protocols.md"},
    }
    exit_code, stdout, stderr = _run_hook_subprocess(payload)
    assert exit_code == 0
    assert stdout.strip(), f"Expected stdout, got empty. stderr: {stderr}"
    out = json.loads(stdout)
    assert "hookSpecificOutput" in out
    hso = out["hookSpecificOutput"]
    assert hso.get("hookEventName") == "PostToolUse"
    assert "additionalContext" in hso
    ctx = hso["additionalContext"].lower()
    assert "contradiction" in ctx
    assert "grep" in ctx


def test_subprocess_silent_on_normal_file():
    """Subprocess is silent (no stdout) for non-rule files."""
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/home/user/project/src/foo.py"},
    }
    exit_code, stdout, _stderr = _run_hook_subprocess(payload)
    assert exit_code == 0
    assert not stdout.strip()


def test_subprocess_silent_on_invalid_input():
    """Subprocess does not crash on malformed input (exit 0, silent)."""
    proc = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input="not json at all",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 0
