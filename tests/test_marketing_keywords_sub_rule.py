"""Characterization tests for _dispatchers/content_governance/marketing_keywords.py.

PINs the behavior of the original marketing-content-detector.py so the
Build #2A lift preserves it bit-for-bit. The source hook is a HARD DENY
gate (returns permissionDecision: deny) when marketing/funnel/positioning
keywords appear in file content AND the marketing-strategy-pmm skill has
not been invoked AND no bypass phrase fired.

Sub-rule contract per Phase 2 spec:
    evaluate(payload: dict) -> dict | None
      None                                    -> no contribution
      {"advisory": "<text>"}                  -> advisory (unused here)
      {"decision": "deny", "reason": "<text>"} -> hard gate

Source: ~/.claude/hooks/marketing-content-detector.py (440 LOC)
Source incidents:
  wr-2026-04-18 (HQ filed BUG after 2 nudges rationalized away in one session)
  wr-2026-04-22-001 (structural exemptions for meta paths + coordination JSON)
  wr-hq-2026-04-27-001/003 (natural-language imperative bypass + lookback window)
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

import pytest

HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


@pytest.fixture
def isolated_tmp_dir(tmp_path, monkeypatch):
    """Redirect HOME so ~/.claude/.tmp/ resolves under tmp_path.

    Creates the canonical .claude/.tmp/ subtree at tmp_path/.claude/.tmp/
    and points HOME (and USERPROFILE for Windows) to tmp_path. Both
    Path.home() and os.path.expanduser('~') resolve to the fake root.
    Returns the .claude/.tmp/ path for direct file writes (skill log etc.)."""
    fake_tmp = tmp_path / ".claude" / ".tmp"
    fake_tmp.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    return fake_tmp


def _write_skill_log(tmp_dir, skills):
    """Plant today's skill-invocation log. skills is a list of skill names."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_dir / f"skill-invocations-{today}.json"
    log_file.write_text(json.dumps({
        "invocations": [{"skill": s} for s in skills],
    }), encoding="utf-8")


def _write_transcript(tmp_path, user_messages):
    """Write a JSONL transcript with the given user messages.
    Returns the path string."""
    path = tmp_path / "transcript.jsonl"
    lines = []
    for msg in user_messages:
        lines.append(json.dumps({"type": "user", "message": {"content": msg}}))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# Tool-name filtering
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("wrong_tool", ["Read", "Bash", "TodoWrite", "Glob", "Grep"])
def test_no_contribution_on_wrong_tool(wrong_tool):
    from _dispatchers.content_governance import marketing_keywords as mk
    payload = {
        "tool_name": wrong_tool,
        "tool_input": {"file_path": "x.md", "content": "Our GTM strategy"},
    }
    assert mk.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Detection: marketing keywords trigger DENY (when no bypass / skill log)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("content", [
    "Our lead magnet is a free PDF",
    "The funnel converts at 3%",
    "Brand positioning matters",
    "GTM playbook needed",  # case-sensitive GTM
    "go-to-market strategy",
    "ICP definition",         # case-sensitive ICP
    "ideal customer profile work",
    "Our value prop is clear",
    "value proposition matters",
    "Our messaging framework",
    "Customer journey mapping",
    "Conversion path optimization",
])
def test_deny_on_marketing_keyword_no_bypass(isolated_tmp_dir, tmp_path, content):
    """When content has a marketing keyword and NO bypass, deny."""
    from _dispatchers.content_governance import marketing_keywords as mk
    # No skill log, no transcript bypass -> should deny
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "doc.md", "content": content},
        "transcript_path": str(tmp_path / "no_such_transcript.jsonl"),
    }
    result = mk.evaluate(payload)
    assert result is not None
    assert result.get("decision") == "deny"
    assert "marketing-strategy-pmm" in result.get("reason", "").lower()


@pytest.mark.parametrize("benign_content", [
    "Just a regular doc with no marketing terms",
    "Function definition: def foo():",
    "Step 1: do this. Step 2: do that.",
    "",  # empty content
])
def test_no_contribution_on_benign_content(isolated_tmp_dir, benign_content):
    from _dispatchers.content_governance import marketing_keywords as mk
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "doc.md", "content": benign_content},
    }
    assert mk.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Case sensitivity: GTM / ICP must be uppercase to fire (avoid noise)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("noisy_lowercase", [
    "the gtm script is fine",      # lowercase gtm — must NOT fire
    "the icp value is set",        # lowercase icp — must NOT fire
])
def test_no_contribution_on_lowercase_gtm_icp(isolated_tmp_dir, noisy_lowercase):
    from _dispatchers.content_governance import marketing_keywords as mk
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "code.md", "content": noisy_lowercase},
    }
    # These should not deny because case-sensitive GTM/ICP are required
    assert mk.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Bypass 1: skill log shows marketing-strategy-pmm was invoked today
# ---------------------------------------------------------------------------

def test_bypass_when_marketing_strategy_pmm_invoked(isolated_tmp_dir, tmp_path):
    from _dispatchers.content_governance import marketing_keywords as mk
    _write_skill_log(isolated_tmp_dir, ["marketing-strategy-pmm"])
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "positioning.md", "content": "Our positioning is X"},
        "transcript_path": str(tmp_path / "no_transcript.jsonl"),
    }
    assert mk.evaluate(payload) is None


def test_bypass_when_pmm_invoked_namespaced(isolated_tmp_dir, tmp_path):
    """Plugin-namespaced skill names should also satisfy the skill-log bypass."""
    from _dispatchers.content_governance import marketing_keywords as mk
    _write_skill_log(isolated_tmp_dir, ["someplugin:marketing-strategy-pmm"])
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "positioning.md", "content": "Our positioning is X"},
        "transcript_path": str(tmp_path / "no_transcript.jsonl"),
    }
    assert mk.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Bypass 2: explicit bypass phrase in recent user message
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bypass_phrase", [
    "skip pmm",
    "bypass marketing",
    "bypass pmm",
    "no positioning",
    "internal doc only",
    "not marketing",
    "skip marketing-strategy-pmm",
    "go ahead and edit",
    "go ahead and update",
    "go ahead and modify",
    "go ahead and broaden",
    "execute this",
    "do it",
    "proceed with the edit",
    "make the change",
    "yes do that",
    "yes proceed",
    "i am driving this",
    "i'm driving this",
])
def test_bypass_phrase_in_recent_user_message(isolated_tmp_dir, tmp_path, bypass_phrase):
    from _dispatchers.content_governance import marketing_keywords as mk
    transcript = _write_transcript(tmp_path, [f"OK {bypass_phrase}"])
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "positioning.md", "content": "Our positioning is X"},
        "transcript_path": transcript,
    }
    assert mk.evaluate(payload) is None, \
        f"expected bypass for phrase: {bypass_phrase}"


# ---------------------------------------------------------------------------
# Bypass 3: structural exemption — meta paths
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("meta_path", [
    "/some/workspace/.work-requests/inbox/wr.json",
    "/some/workspace/.lifecycle-reviews/inbox/review.md",
    "/some/workspace/.routed-tasks/inbox/task.json",
])
def test_bypass_meta_path(isolated_tmp_dir, meta_path):
    from _dispatchers.content_governance import marketing_keywords as mk
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": meta_path, "content": "Our funnel is broken"},
    }
    assert mk.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Bypass 4: coordination JSON content (routed-task / work-request schema)
# ---------------------------------------------------------------------------

def test_bypass_routed_task_json(isolated_tmp_dir):
    from _dispatchers.content_governance import marketing_keywords as mk
    rt = json.dumps({
        "task_id": "rt-test",
        "routed_from": "hq",
        "routed_to": "skillhub",
        "context": "Discussion about our funnel strategy",
    })
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/some/inbox/rt.json", "content": rt},
    }
    assert mk.evaluate(payload) is None


def test_bypass_work_request_json(isolated_tmp_dir):
    from _dispatchers.content_governance import marketing_keywords as mk
    wr = json.dumps({
        "id": "wr-test-001",
        "request_type": "TASK",
        "source_workspace": "hq",
        "context": "Need to update our positioning",
    })
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/some/wr.json", "content": wr},
    }
    assert mk.evaluate(payload) is None


def test_bypass_doctype_internal_coordination(isolated_tmp_dir):
    """Markdown with frontmatter doc_type: internal_coordination is an
    explicit escape hatch (wr-2026-04-22-001)."""
    from _dispatchers.content_governance import marketing_keywords as mk
    content = (
        "---\n"
        "doc_type: internal_coordination\n"
        "---\n"
        "Internal note about our GTM playbook.\n"
    )
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/some/doc.md", "content": content},
    }
    assert mk.evaluate(payload) is None


# ---------------------------------------------------------------------------
# False-positive suppression: code-file string literal containing keyword
# ---------------------------------------------------------------------------

def test_code_file_string_literal_keyword_does_not_fire(isolated_tmp_dir):
    """A Python file with a string literal containing 'funnel' must NOT deny."""
    from _dispatchers.content_governance import marketing_keywords as mk
    code = 'name = "funnel"\nprint(name)\n'
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "config.py", "content": code},
    }
    assert mk.evaluate(payload) is None


def test_markdown_inline_backtick_keyword_does_not_fire(isolated_tmp_dir):
    """Markdown with `funnel` in inline backticks must NOT deny (referential
    mention, not authored marketing copy)."""
    from _dispatchers.content_governance import marketing_keywords as mk
    md = "The word `funnel` appears in code samples but this doc is technical.\n"
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "tech-doc.md", "content": md},
    }
    assert mk.evaluate(payload) is None


def test_markdown_fenced_code_keyword_does_not_fire(isolated_tmp_dir):
    """Markdown with a fenced code block containing the keyword must NOT deny."""
    from _dispatchers.content_governance import marketing_keywords as mk
    md = "Example:\n\n```python\n# our funnel logic\ndef foo(): pass\n```\n"
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "tech-doc.md", "content": md},
    }
    assert mk.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Edit support: scans new_string instead of content
# ---------------------------------------------------------------------------

def test_deny_on_edit_new_string_keyword(isolated_tmp_dir, tmp_path):
    from _dispatchers.content_governance import marketing_keywords as mk
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "doc.md",
            "old_string": "Old content",
            "new_string": "Our GTM strategy will pivot",
        },
        "transcript_path": str(tmp_path / "no_transcript.jsonl"),
    }
    result = mk.evaluate(payload)
    assert result is not None
    assert result.get("decision") == "deny"


def test_no_contribution_on_empty_new_string(isolated_tmp_dir):
    """Edit with empty new_string must no-op (no content to scan)."""
    from _dispatchers.content_governance import marketing_keywords as mk
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "doc.md", "old_string": "x", "new_string": ""},
    }
    assert mk.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Defensive: malformed payloads
# ---------------------------------------------------------------------------

def test_no_contribution_on_empty_payload(isolated_tmp_dir):
    from _dispatchers.content_governance import marketing_keywords as mk
    assert mk.evaluate({}) is None


def test_no_contribution_on_none_payload(isolated_tmp_dir):
    from _dispatchers.content_governance import marketing_keywords as mk
    assert mk.evaluate(None) is None


def test_no_contribution_on_string_tool_input(isolated_tmp_dir):
    """tool_input arriving as a string (rare but possible) must parse + survive."""
    from _dispatchers.content_governance import marketing_keywords as mk
    payload = {
        "tool_name": "Write",
        "tool_input": json.dumps({"file_path": "/x.md", "content": "Our GTM strategy"}),
        "transcript_path": "/no/such/transcript",
    }
    # With JSON-parsed tool_input + GTM in content + no bypass -> deny
    result = mk.evaluate(payload)
    assert result is not None
    assert result.get("decision") == "deny"
