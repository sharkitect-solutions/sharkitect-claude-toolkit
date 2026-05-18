"""Characterization tests for _dispatchers/content_governance/content_enforcer.py.

These tests PIN the behavior of the original content-enforcer-hook.py so the
Build #2A lift preserves it bit-for-bit. Source hook signature: HQ-workspace-
only PreToolUse on Write/Edit; advisory nudge when file_path looks like
client-facing content (path segment OR filename pattern + content extension);
non-blocking; no transcript scan; no skill log check; no state file.

Sub-rule contract per Phase 2 spec:
    evaluate(payload: dict) -> dict | None
      None                                    -> no contribution
      {"advisory": "<text>"}                  -> advisory (additionalContext)
      {"decision": "deny", "reason": "<text>"} -> hard gate (unused here)

Source: ~/.claude/hooks/content-enforcer-hook.py (191 LOC)
"""
from __future__ import annotations

import os
import sys

import pytest

# Make the _dispatchers package importable
HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


# Stand-in HQ workspace path used by tests that need to look like HQ cwd.
# The source hook does: "workforce" in cwd and "hq" in cwd (lowercased).
_HQ_CWD = r"C:\Users\me\Documents\Claude Code Workspaces\1.- SHARKITECT DIGITAL WORKFORCE HQ"
_NON_HQ_CWD = r"C:\Users\me\Documents\Claude Code Workspaces\3.- Skill Management Hub"


@pytest.fixture(autouse=True)
def _restore_cwd():
    """Each test mutates cwd via monkeypatch; restore after."""
    yield


# ---------------------------------------------------------------------------
# Workspace scoping — only HQ fires; non-HQ no-ops
# ---------------------------------------------------------------------------

def test_no_contribution_outside_hq_workspace(monkeypatch, tmp_path):
    from _dispatchers.content_governance import content_enforcer as ce
    # Non-HQ cwd: even with a content-like path the rule must no-op
    monkeypatch.chdir(tmp_path)  # tmp_path won't contain "workforce" or "hq"
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": "deliverables/landing/hero.md"},
    }
    assert ce.evaluate(payload) is None


def test_advisory_in_hq_workspace_on_content_path(monkeypatch, tmp_path):
    """When cwd is the HQ workspace AND the file_path looks like client content,
    emit an advisory naming hq-content-enforcer."""
    from _dispatchers.content_governance import content_enforcer as ce
    hq = tmp_path / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
    hq.mkdir()
    monkeypatch.chdir(hq)
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": "deliverables/landing/hero.md"},
    }
    result = ce.evaluate(payload)
    assert result is not None
    assert "advisory" in result
    assert "hq-content-enforcer" in result["advisory"].lower()


# ---------------------------------------------------------------------------
# Tool-name filtering — only Write / Edit fire
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("wrong_tool", ["Read", "Bash", "TodoWrite", "Glob", "Grep"])
def test_no_contribution_on_wrong_tool(monkeypatch, tmp_path, wrong_tool):
    from _dispatchers.content_governance import content_enforcer as ce
    hq = tmp_path / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
    hq.mkdir()
    monkeypatch.chdir(hq)
    payload = {
        "tool_name": wrong_tool,
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": "deliverables/landing/hero.md"},
    }
    assert ce.evaluate(payload) is None


@pytest.mark.parametrize("tool", ["Write", "Edit"])
def test_advisory_on_both_write_and_edit(monkeypatch, tmp_path, tool):
    from _dispatchers.content_governance import content_enforcer as ce
    hq = tmp_path / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
    hq.mkdir()
    monkeypatch.chdir(hq)
    payload = {
        "tool_name": tool,
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": "marketing/campaigns/q3-launch-email.md"},
    }
    assert ce.evaluate(payload) is not None


# ---------------------------------------------------------------------------
# Content-detection: extension + (path segment OR filename pattern)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("content_path", [
    "deliverables/landing-page.md",      # path segment: deliverables
    "content/blog/post.md",              # path segment: content
    "marketing/email.html",              # path segment: marketing
    "campaigns/q3.txt",                  # path segment: campaigns
    "outreach/cold-email.md",            # path segment: outreach
    "copy/hero-headline.md",             # path segment: copy
    "website/landing-page.html",         # path segment: website
    "src/landing-page.md",               # filename pattern: landing
    "src/sales-email.md",                # filename pattern: email
    "src/proposal-q3.md",                # filename pattern: proposal
    "src/hero-copy.md",                  # filename pattern: hero / copy
    "src/blog-post.md",                  # filename pattern: blog / post
    "src/case-study-acme.md",            # filename pattern: case-study
    "src/case_study_acme.md",            # filename pattern: case_study
    "src/newsletter-april.md",           # filename pattern: newsletter
    "src/announcement.md",               # filename pattern: announcement
    "src/cta-button.md",                 # filename pattern: cta
    "src/headline.md",                   # filename pattern: headline
    "src/tagline.md",                    # filename pattern: tagline
    "src/ad-creative.md",                # filename pattern: ad
    "src/brochure.md",                   # filename pattern: brochure
    "src/flyer.md",                      # filename pattern: flyer
    "src/sow-acme.md",                   # filename pattern: sow
    "src/social-post.md",                # filename pattern: social / post
    "src/pitch-deck.md",                 # filename pattern: pitch
    "src/script-onboarding.md",          # filename pattern: script
])
def test_advisory_fires_on_content_signals(monkeypatch, tmp_path, content_path):
    from _dispatchers.content_governance import content_enforcer as ce
    hq = tmp_path / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
    hq.mkdir()
    monkeypatch.chdir(hq)
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": content_path},
    }
    assert ce.evaluate(payload) is not None, \
        f"expected advisory for content-like path: {content_path}"


@pytest.mark.parametrize("normal_path", [
    "src/utils/helpers.py",               # wrong extension (.py is not content)
    "tools/build.js",                     # wrong extension
    "docs/architecture.md",               # .md but no content segment / filename pattern
    "tests/test_foo.md",                  # tests/ is excluded
    "package.json",                       # excluded
    "MEMORY.md",                          # excluded
    "CLAUDE.md",                          # excluded
])
def test_no_contribution_on_non_content_paths(monkeypatch, tmp_path, normal_path):
    from _dispatchers.content_governance import content_enforcer as ce
    hq = tmp_path / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
    hq.mkdir()
    monkeypatch.chdir(hq)
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": normal_path},
    }
    assert ce.evaluate(payload) is None, \
        f"unexpected advisory for non-content path: {normal_path}"


# ---------------------------------------------------------------------------
# Exclusion paths — never fire on these even if filename pattern matches
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("excluded", [
    ".tmp/landing.md",                   # excluded: .tmp/
    ".claude/skills/landing-cro/SKILL.md",  # excluded: .claude/
    "tools/landing-builder.md",          # excluded: tools/
    "workflows/landing-page-sop.md",     # excluded: workflows/
    ".git/COMMIT_EDITMSG",               # excluded: .git/
    "node_modules/some-pkg/email.md",    # excluded: node_modules/
    "_archive/2023-landing.md",          # excluded: _archive/
    "src/_archive/landing-2023.md",      # excluded: _archive/ (anywhere)
    "knowledge-base/_internal/landing.md",  # excluded: knowledge-base/_internal/
    "docs/audits/landing-audit.md",      # excluded: docs/audits/
    "docs/specs/landing-spec.md",        # excluded: docs/specs/
    ".work-requests/inbox/landing.md",   # excluded: .work-requests/
    ".lifecycle-reviews/inbox/landing.md",  # excluded: .lifecycle-reviews/
    ".routed-tasks/inbox/landing.md",    # excluded: .routed-tasks/
    "HUMAN-ACTION-REQUIRED.md",          # excluded: HUMAN-ACTION-REQUIRED.md
    "tests/test_landing.md",             # excluded: tests/
])
def test_no_contribution_on_excluded_paths(monkeypatch, tmp_path, excluded):
    from _dispatchers.content_governance import content_enforcer as ce
    hq = tmp_path / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
    hq.mkdir()
    monkeypatch.chdir(hq)
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": excluded},
    }
    assert ce.evaluate(payload) is None, \
        f"unexpected advisory for excluded path: {excluded}"


# ---------------------------------------------------------------------------
# Edge cases — empty / missing / malformed inputs
# ---------------------------------------------------------------------------

def test_no_contribution_on_missing_file_path(monkeypatch, tmp_path):
    from _dispatchers.content_governance import content_enforcer as ce
    hq = tmp_path / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
    hq.mkdir()
    monkeypatch.chdir(hq)
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {},  # no file_path
    }
    assert ce.evaluate(payload) is None


def test_no_contribution_on_empty_payload(monkeypatch, tmp_path):
    """evaluate must NEVER raise; missing fields -> no contribution."""
    from _dispatchers.content_governance import content_enforcer as ce
    monkeypatch.chdir(tmp_path)
    assert ce.evaluate({}) is None


def test_no_contribution_on_none_payload(monkeypatch, tmp_path):
    """Defensive: payload=None still safe."""
    from _dispatchers.content_governance import content_enforcer as ce
    monkeypatch.chdir(tmp_path)
    # Sub-rules should never receive None per dispatcher contract, but be defensive
    assert ce.evaluate(None) is None


# ---------------------------------------------------------------------------
# Behavior preservation — extension matters even with content path segment
# ---------------------------------------------------------------------------

def test_no_contribution_when_extension_not_content_type(monkeypatch, tmp_path):
    """marketing/foo.py should NOT fire — extension is .py not in
    {.md, .html, .txt, .mdx, .htm, .docx}. Source hook line 124."""
    from _dispatchers.content_governance import content_enforcer as ce
    hq = tmp_path / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
    hq.mkdir()
    monkeypatch.chdir(hq)
    payload = {
        "tool_name": "Write",
        "hook_event_name": "PreToolUse",
        "tool_input": {"file_path": "marketing/automation/script.py"},
    }
    assert ce.evaluate(payload) is None
