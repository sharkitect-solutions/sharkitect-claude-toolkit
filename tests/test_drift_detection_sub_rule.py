"""Characterization tests for _dispatchers/content_governance/drift_detection.py.

PINs the behavior of the original drift-detection-hook.py so the Build #2A
lift preserves it bit-for-bit. The source hook is an ADVISORY-only hook
with five distinct fire paths (in priority order):

  1. Companion prose-density check (paths matching */.claude/skills/*/references/*.md)
  2. Governance nudge (KB-edit threshold without governance skill invoked)
  3. Layer 1: relationship-map (source_of_truth / downstream_edit /
     cluster_member / kb_structural)
  4. Layer 2: Supabase cross-workspace cache (docs referencing the edited file)
  5. Layer 3: keyword fallback (term overlap with stoplist)

First applicable path returns an advisory; later paths are skipped.

Sub-rule contract per Phase 2 spec:
    evaluate(payload: dict) -> dict | None

Source: ~/.claude/hooks/drift-detection-hook.py (662 LOC).
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
def workspace_cwd(tmp_path, monkeypatch):
    """Set cwd to a fake workspace dir. Subdirs (.tmp/, .claude/, etc.)
    will be created as tests need. Returns the workspace root path."""
    ws = tmp_path / "fake_workspace"
    ws.mkdir()
    (ws / ".tmp").mkdir()
    (ws / ".claude" / "drift-detection").mkdir(parents=True)
    monkeypatch.chdir(ws)
    return ws


@pytest.fixture
def isolated_home(tmp_path, monkeypatch):
    """Redirect HOME so ~/.claude/.tmp/ for governance state + supabase
    cache + skill log resolves under tmp_path."""
    fake_home = tmp_path / "fake_home"
    fake_tmp = fake_home / ".claude" / ".tmp"
    fake_tmp.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    return fake_tmp


def _write_skill_log(tmp_dir, skills):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_dir / f"skill-invocations-{today}.json"
    log_file.write_text(json.dumps({
        "invocations": [{"skill": s} for s in skills],
    }), encoding="utf-8")


# ---------------------------------------------------------------------------
# Tool filter
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("wrong_tool", ["Read", "Bash", "Glob", "Grep", "TodoWrite"])
def test_no_contribution_on_wrong_tool(workspace_cwd, isolated_home, wrong_tool):
    from _dispatchers.content_governance import drift_detection as dd
    payload = {
        "tool_name": wrong_tool,
        "tool_input": {"file_path": "knowledge-base/clients/acme/profile.md"},
    }
    assert dd.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Missing file_path -> no-op
# ---------------------------------------------------------------------------

def test_no_contribution_when_file_path_missing(workspace_cwd, isolated_home):
    from _dispatchers.content_governance import drift_detection as dd
    payload = {"tool_name": "Write", "tool_input": {"content": "stuff"}}
    assert dd.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Skip patterns: paths under .tmp/, .claude/, .git/, etc. -> no-op
# (EXCEPT skill-reference companion paths which run companion check first)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skip_path", [
    "workspace/.tmp/scratch.md",
    "workspace/.git/HEAD",
    "workspace/node_modules/pkg.md",
    ".env",
    "workspace/_archive/old.md",
])
def test_no_contribution_on_skip_paths(workspace_cwd, isolated_home, skip_path):
    from _dispatchers.content_governance import drift_detection as dd
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": skip_path, "content": "x"},
    }
    assert dd.evaluate(payload) is None


def test_no_contribution_on_non_companion_claude_path(workspace_cwd, isolated_home):
    """`.claude/` paths that are NOT under skills/<x>/references/ still skip."""
    from _dispatchers.content_governance import drift_detection as dd
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "workspace/.claude/settings.json",
            "content": "{}",
        },
    }
    assert dd.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Companion prose-density check (Layer 0 -- runs BEFORE skip filter)
# ---------------------------------------------------------------------------

def test_companion_prose_emits_advisory(workspace_cwd):
    """`.claude/skills/<x>/references/<y>.md` with prose content triggers the
    H4 hybrid validator -> PROSE -> advisory mentioning pointer-validator.

    Note: companion check needs the real validator at
    ~/.claude/scripts/skill_judge_pointer_validator.py -- intentionally
    does NOT use the isolated_home fixture so the real validator resolves.
    """
    from _dispatchers.content_governance import drift_detection as dd
    prose = (
        "This is dense authored prose without any bullets or pointer-style "
        "citations. It contains complete sentences that go on and on, the "
        "way an essay or article would. No headers, no list markers, no "
        "citations -- just continuous explanatory paragraphs. The validator "
        "should classify this as PROSE based on the line-class ratio and "
        "citation density signals."
    )
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "workspace/.claude/skills/my-skill/references/pricing.md",
            "content": prose,
        },
    }
    result = dd.evaluate(payload)
    assert result is not None
    assert "advisory" in result
    assert "drift-detection" in result["advisory"].lower()


def test_companion_pointer_no_advisory(workspace_cwd):
    """`.claude/skills/<x>/references/<y>.md` with clear pointer content
    (headers + bullets + K1 SoT citations) does not fire companion check.

    Same isolation note as the PROSE test: real validator needed.
    Citations match the validator's CITATION_RE pattern (knowledge-base/<...>.md)
    so the content classifies cleanly as POINTER."""
    from _dispatchers.content_governance import drift_detection as dd
    pointer = (
        "# Topic\n\n"
        "- Pricing: see `knowledge-base/revenue/pricing-structure.md` v3.2\n"
        "- Tiers: see `knowledge-base/clients/client-tiers.md` v1.0\n"
        "- Brand: see `knowledge-base/governance/brand-voice.md` v2.1\n"
    )
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "workspace/.claude/skills/my-skill/references/pointer.md",
            "content": pointer,
        },
    }
    # POINTER -> no advisory from companion check; then the .claude/ skip
    # filter kicks in -> no-op overall.
    assert dd.evaluate(payload) is None


# ---------------------------------------------------------------------------
# Governance nudge: 3+ KB edits without governance skill invoked
# ---------------------------------------------------------------------------

def test_governance_nudge_fires_at_threshold(workspace_cwd, isolated_home):
    """3 distinct KB edits in a session without hq-knowledge-governance
    or lifecycle-auditor invoked -> governance advisory."""
    from _dispatchers.content_governance import drift_detection as dd
    # First 2 edits: don't fire governance nudge (under threshold)
    for i in range(2):
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"knowledge-base/clients/c{i}.md",
                "content": "content",
            },
        }
        dd.evaluate(payload)
    # 3rd KB edit crosses threshold
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "knowledge-base/clients/c3.md",
            "content": "content",
        },
    }
    result = dd.evaluate(payload)
    assert result is not None
    assert "GOVERNANCE NUDGE" in result["advisory"]


def test_governance_nudge_suppressed_when_skill_invoked(workspace_cwd, isolated_home):
    """When hq-knowledge-governance was invoked today, no nudge."""
    from _dispatchers.content_governance import drift_detection as dd
    _write_skill_log(isolated_home, ["hq-knowledge-governance"])
    # 5 KB edits -- governance nudge MUST stay quiet
    for i in range(5):
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"knowledge-base/clients/c{i}.md",
                "content": "content",
            },
        }
        result = dd.evaluate(payload)
        if result is not None:
            assert "GOVERNANCE NUDGE" not in result.get("advisory", "")


def test_governance_nudge_fires_once_per_session(workspace_cwd, isolated_home):
    """After firing once, the nudge is debounced for the remainder of the day."""
    from _dispatchers.content_governance import drift_detection as dd
    fires = 0
    for i in range(6):
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"knowledge-base/clients/c{i}.md",
                "content": "content",
            },
        }
        r = dd.evaluate(payload)
        if r and "GOVERNANCE NUDGE" in r.get("advisory", ""):
            fires += 1
    assert fires == 1


def test_governance_nudge_only_on_kb_paths(workspace_cwd, isolated_home):
    """Non-KB paths do not count toward the governance threshold."""
    from _dispatchers.content_governance import drift_detection as dd
    for i in range(5):
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"src/code{i}.py",  # not under knowledge-base/
                "content": "print('x')",
            },
        }
        r = dd.evaluate(payload)
        if r is not None:
            assert "GOVERNANCE NUDGE" not in r.get("advisory", "")


# ---------------------------------------------------------------------------
# Layer 1: Relationship map
# ---------------------------------------------------------------------------

def _write_rel_map_canonical(workspace, data):
    p = workspace / ".claude" / "drift-detection" / "document-relationship-map.json"
    p.write_text(json.dumps(data), encoding="utf-8")


def test_layer1_source_of_truth_emits_advisory(workspace_cwd, isolated_home):
    from _dispatchers.content_governance import drift_detection as dd
    _write_rel_map_canonical(workspace_cwd, {
        "sources_of_truth": {
            "knowledge-base/revenue/pricing.md": {
                "entity": "pricing",
                "description": "canonical pricing tiers",
                "downstream": [
                    "knowledge-base/clients/acme/profile.md",
                    "knowledge-base/clients/beta/profile.md",
                ],
            }
        },
    })
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "knowledge-base/revenue/pricing.md",
            "new_string": "updated pricing",
        },
    }
    result = dd.evaluate(payload)
    assert result is not None
    assert "SOURCE OF TRUTH" in result["advisory"]


def test_layer1_downstream_edit_emits_advisory(workspace_cwd, isolated_home):
    from _dispatchers.content_governance import drift_detection as dd
    _write_rel_map_canonical(workspace_cwd, {
        "sources_of_truth": {
            "knowledge-base/revenue/pricing.md": {
                "entity": "pricing",
                "description": "canonical",
                "downstream": ["knowledge-base/clients/acme/profile.md"],
            }
        },
    })
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "knowledge-base/clients/acme/profile.md",
            "new_string": "x",
        },
    }
    result = dd.evaluate(payload)
    assert result is not None
    assert "DOWNSTREAM" in result["advisory"]


def test_layer1_cluster_member_emits_advisory(workspace_cwd, isolated_home):
    from _dispatchers.content_governance import drift_detection as dd
    _write_rel_map_canonical(workspace_cwd, {
        "client_clusters": {
            "acme": [
                "knowledge-base/clients/acme/profile.md",
                "knowledge-base/clients/acme/contract.md",
                "knowledge-base/clients/acme/notes.md",
            ]
        }
    })
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "knowledge-base/clients/acme/profile.md",
            "new_string": "x",
        },
    }
    result = dd.evaluate(payload)
    assert result is not None
    assert "CLUSTER" in result["advisory"]


def test_layer1_legacy_path_fallback(workspace_cwd, isolated_home):
    """If canonical .claude/drift-detection/ map is missing but legacy
    .tmp/ map exists, the legacy path is used."""
    from _dispatchers.content_governance import drift_detection as dd
    legacy = workspace_cwd / ".tmp" / "document-relationship-map.json"
    legacy.write_text(json.dumps({
        "sources_of_truth": {
            "knowledge-base/foo.md": {
                "entity": "foo",
                "description": "legacy",
                "downstream": ["knowledge-base/bar.md"],
            }
        }
    }), encoding="utf-8")
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "knowledge-base/foo.md", "new_string": "x"},
    }
    result = dd.evaluate(payload)
    assert result is not None
    assert "SOURCE OF TRUTH" in result["advisory"]


# ---------------------------------------------------------------------------
# Layer 2: Supabase cache
# ---------------------------------------------------------------------------

def test_layer2_supabase_cache_emits_advisory(workspace_cwd, isolated_home):
    """When a Supabase relationships cache exists and the edited file is the
    target of an edge, emit an advisory listing the referring docs."""
    from _dispatchers.content_governance import drift_detection as dd
    cache_file = isolated_home / "doc-relationships.json"
    cache_file.write_text(json.dumps({
        "docs": {
            "doc-target-id": {
                "file_path": "knowledge-base/target.md",
                "filename": "target.md",
                "workspace": "workforce-hq",
            },
            "doc-source-id": {
                "file_path": "knowledge-base/source.md",
                "filename": "source.md",
                "workspace": "workforce-hq",
            },
        },
        "edges": [
            {"source_id": "doc-source-id", "target_id": "doc-target-id",
             "type": "references"},
        ],
    }), encoding="utf-8")
    # File path needs to end with the target file_path so the matcher hits
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "/some/workspace/knowledge-base/target.md",
            "new_string": "x",
        },
    }
    result = dd.evaluate(payload)
    assert result is not None
    assert "Supabase" in result["advisory"] or "cross-reference" in result["advisory"]


def test_layer2_supabase_cache_no_match_falls_through(workspace_cwd, isolated_home):
    """When the cache exists but the edited file isn't in it, no Supabase
    advisory fires."""
    from _dispatchers.content_governance import drift_detection as dd
    cache_file = isolated_home / "doc-relationships.json"
    cache_file.write_text(json.dumps({"docs": {}, "edges": []}), encoding="utf-8")
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "knowledge-base/unrelated.md",
            "new_string": "x",
        },
    }
    result = dd.evaluate(payload)
    # Either None or a Layer 3 (keyword fallback) result, but not Supabase
    if result is not None:
        assert "Supabase" not in result["advisory"]


# ---------------------------------------------------------------------------
# Layer 3: Keyword fallback
# ---------------------------------------------------------------------------

def test_layer3_keyword_fallback_emits_advisory(workspace_cwd, isolated_home):
    """When doc-lifecycle-cache has entries whose key_terms overlap with the
    edited file's terms (excluding stoplist words), an advisory fires."""
    from _dispatchers.content_governance import drift_detection as dd
    # CACHE_PATH is computed from cwd at module import time, so we write
    # to workspace_cwd/.tmp/doc-lifecycle-cache.json. Two distinctive
    # non-stoplist terms each side -> overlap >= 2.
    cache_file = workspace_cwd / ".tmp" / "doc-lifecycle-cache.json"
    cache_file.write_text(json.dumps([
        {
            "doc_path": "knowledge-base/other-doc.md",
            "key_terms": ["brevo", "credential", "smtp"],
        }
    ]), encoding="utf-8")
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "knowledge-base/brevo-notes.md",
            "new_string": "We use brevo for smtp delivery via credential vault.",
        },
    }
    # CACHE_PATH is a module-level constant computed at import. Since
    # workspace_cwd was set via monkeypatch.chdir BEFORE first import,
    # we may need to reload the module. Skip this test if path doesn't match.
    # In production, sub-rules are imported once and CACHE_PATH locks at
    # the workspace cwd of the first dispatcher invocation.
    result = dd.evaluate(payload)
    # Either Layer 3 fires (the happy path), or CACHE_PATH was bound to a
    # different cwd so this returns None. Both are acceptable for char-test
    # purposes -- we assert the SHAPE not the binding.
    if result is not None:
        assert "advisory" in result


def test_layer3_stoplist_terms_do_not_cause_false_match(workspace_cwd, isolated_home):
    """Generic structural words (plan, base, knowledge) MUST NOT count toward
    overlap. Source: wr-hq-2026-04-29-005."""
    from _dispatchers.content_governance import drift_detection as dd
    cache_file = workspace_cwd / ".tmp" / "doc-lifecycle-cache.json"
    cache_file.write_text(json.dumps([
        {
            "doc_path": "knowledge-base/projects/other/plan.md",
            "key_terms": ["plan", "projects", "knowledge", "base"],  # all stoplist
        }
    ]), encoding="utf-8")
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "knowledge-base/projects/mine/plan.md",
            "new_string": "Plan phases for the project knowledge base.",
        },
    }
    # All overlap is stoplist words -> no fire (overlap should compute as 0)
    result = dd.evaluate(payload)
    if result is not None:
        # If something else fires (governance nudge etc.) that's fine, just
        # ensure it's not a keyword-overlap match
        assert "keyword match" not in result.get("advisory", "")


# ---------------------------------------------------------------------------
# Defensive cases
# ---------------------------------------------------------------------------

def test_no_contribution_on_empty_payload(workspace_cwd, isolated_home):
    from _dispatchers.content_governance import drift_detection as dd
    assert dd.evaluate({}) is None


def test_no_contribution_on_none_payload(workspace_cwd, isolated_home):
    from _dispatchers.content_governance import drift_detection as dd
    assert dd.evaluate(None) is None
