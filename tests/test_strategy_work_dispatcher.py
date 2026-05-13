"""Tests for strategy_work dispatcher sub-rule (Cluster A Layer 3).

Source: docs/superpowers/specs/2026-05-12-methodology-gate-cluster-a-design.md
Tier 1 (ask decision): NEW pricing/positioning/strategy spec writes without methodology
Tier 2 (advisory): broader design/proposal/audit writes without methodology
Bypasses: skip methodology-gate, intent_detection user-driven, meta-path exemptions
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


SUBRULE_PATH = Path.home() / ".claude" / "hooks" / "_dispatchers" / "methodology" / "strategy_work.py"


def _load_subrule():
    spec = importlib.util.spec_from_file_location("strategy_work", SUBRULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload(file_path, tool_name="Write", content="placeholder content", session_id="test-session"):
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": {"file_path": str(file_path), "content": content},
        "session_id": session_id,
        "transcript_path": None,
    }


# ---- Tier 1 (ask decision on NEW pricing/positioning/strategy spec writes) ----


def test_tier1_ask_on_new_marketing_takeover_proposal(tmp_path):
    """Write to NEW marketing-takeover proposal with no methodology invoked -> ask."""
    module = _load_subrule()
    target = tmp_path / "projects" / "clients" / "Acme" / "marketing-takeover" / "proposal.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    assert result is not None
    assert result.get("decision") == "ask"
    reason = result.get("reason", "").lower()
    assert "methodology" in reason or "pricing-strategy" in reason


def test_tier1_ask_on_new_pricing_structure(tmp_path):
    """Write to NEW knowledge-base/revenue/pricing-structure-v3.md with no methodology -> ask."""
    module = _load_subrule()
    target = tmp_path / "knowledge-base" / "revenue" / "pricing-structure-v3.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    assert result is not None
    assert result.get("decision") == "ask"


def test_tier1_ask_on_new_pricing_spec(tmp_path):
    """Write to NEW docs/superpowers/specs/2026-XX-XX-pricing-redesign-design.md with no methodology -> ask."""
    module = _load_subrule()
    target = tmp_path / "docs" / "superpowers" / "specs" / "2026-05-12-pricing-redesign-design.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    assert result is not None
    assert result.get("decision") == "ask"


def test_tier1_passes_when_methodology_skill_invoked(tmp_path):
    """Write to NEW pricing path WITH methodology skill in session -> returns None (pass)."""
    module = _load_subrule()
    target = tmp_path / "knowledge-base" / "revenue" / "pricing-structure-v3.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "_session_has_methodology_skill", return_value=True):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    assert result is None  # pass-through


def test_tier1_skips_when_file_already_exists(tmp_path):
    """Write to EXISTING pricing file: Tier 1 must NOT fire (Tier 1 is NEW files only)."""
    module = _load_subrule()
    target = tmp_path / "knowledge-base" / "revenue" / "pricing-structure-v2.md"
    target.parent.mkdir(parents=True)
    target.write_text("existing content")  # file exists -> Tier 1 must skip
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    # File exists: Tier 1 ask must NOT fire. Tier 2 advisory MAY fire (broad match).
    if result is not None:
        assert result.get("decision") != "ask", \
            f"Tier 1 incorrectly fired on existing file; got: {result}"


# ---- Tier 2 (advisory on broader design/proposal/audit) ----


def test_tier2_advisory_on_audit_file(tmp_path):
    """Write to projects/clients/Acme/audit-report-2026-Q3.md with no methodology -> advisory."""
    module = _load_subrule()
    target = tmp_path / "projects" / "clients" / "Acme" / "audit-report-2026-Q3.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    assert result is not None
    assert "advisory" in result
    assert "methodology" in result["advisory"].lower()
    # NOT a Tier 1 ask
    assert "decision" not in result


def test_tier2_advisory_on_design_file_outside_tier1(tmp_path):
    """Write to docs/some-design.md outside Tier 1 strict paths -> advisory only."""
    module = _load_subrule()
    target = tmp_path / "docs" / "some-design.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    assert result is not None
    assert "advisory" in result
    assert "decision" not in result  # not ask, just advisory


def test_edit_existing_pricing_file_returns_advisory_not_ask(tmp_path):
    """Edit (not Write) to existing pricing-structure.md with no methodology -> advisory."""
    module = _load_subrule()
    target = tmp_path / "knowledge-base" / "revenue" / "pricing-structure-v2.md"
    target.parent.mkdir(parents=True)
    target.write_text("existing content")
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            payload = _payload(target, tool_name="Edit")
            result = module.evaluate(payload)
    # Edit on existing file: NOT ask (Tier 1 requires Write + NEW), but Tier 2 advisory applies
    assert result is not None
    assert "advisory" in result
    assert "decision" not in result


# ---- Bypass + exemption cases ----


def test_bypass_phrase_in_content_returns_none(tmp_path):
    """tool_input.content contains 'skip methodology-gate' -> pass through."""
    module = _load_subrule()
    target = tmp_path / "knowledge-base" / "revenue" / "pricing-structure-v3.md"
    target.parent.mkdir(parents=True)
    payload = _payload(target, content="some content. skip methodology-gate. more content.")
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        # _has_bypass_phrase is NOT patched -- real implementation must detect the phrase
        result = module.evaluate(payload)
    assert result is None


def test_meta_path_exemption_work_requests(tmp_path):
    """Files under .work-requests/ are exempt from both tiers."""
    module = _load_subrule()
    target = tmp_path / ".work-requests" / "inbox" / "wr-something-pricing.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    assert result is None


def test_meta_path_exemption_tmp(tmp_path):
    """Files under .tmp/ are exempt."""
    module = _load_subrule()
    target = tmp_path / ".tmp" / "scratch-design.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    assert result is None


def test_meta_path_exemption_brain_dump(tmp_path):
    """Files under brain-dump/ are exempt (capture flow, not strategy work)."""
    module = _load_subrule()
    target = tmp_path / "brain-dump" / "2026-05-12-pricing-thoughts.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "_session_has_methodology_skill", return_value=False):
        with patch.object(module, "_has_bypass_phrase", return_value=False):
            result = module.evaluate(_payload(target))
    assert result is None


def test_intent_detection_user_driven_bypass(tmp_path):
    """intent_detection.is_user_driven returns True -> pass through."""
    module = _load_subrule()
    target = tmp_path / "knowledge-base" / "revenue" / "pricing-structure-v3.md"
    target.parent.mkdir(parents=True)
    with patch.object(module, "is_user_driven", return_value=True):
        with patch.object(module, "_session_has_methodology_skill", return_value=False):
            with patch.object(module, "_has_bypass_phrase", return_value=False):
                result = module.evaluate(_payload(target))
    assert result is None


def test_non_pretooluse_event_returns_none():
    """PostToolUse or other events return None unconditionally."""
    module = _load_subrule()
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "/knowledge-base/revenue/pricing-structure-v3.md", "content": ""},
        "session_id": "test-session",
    }
    result = module.evaluate(payload)
    assert result is None


def test_non_write_edit_tool_returns_none(tmp_path):
    """Bash / Read / other tools on PreToolUse return None."""
    module = _load_subrule()
    target = tmp_path / "knowledge-base" / "revenue" / "pricing-structure-v3.md"
    payload = _payload(target, tool_name="Read")
    result = module.evaluate(payload)
    assert result is None
