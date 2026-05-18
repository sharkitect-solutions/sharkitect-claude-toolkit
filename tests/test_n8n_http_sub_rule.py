"""Tests for _dispatchers/methodology/n8n_http.py (Phase 2 Build #2B).

Strict 1:1 behavior preservation of n8n-httpRequest-guard.py wrapped in
evaluate(payload) for the methodology dispatcher. Returns:

  None                                  -> sub-rule did not trigger / passed through
  {"decision": "deny", "reason": "..."} -> HARD GATE

Source behavior preserved:
  Trigger 1 (Write/Edit): file path looks like n8n workflow JSON AND content
    contains n8n-nodes-base.httpRequest node AND not justified by either
    inline allow-http: comment OR allowlisted URL host/suffix.
  Trigger 2 (n8n MCP): tool_name starts with mcp__n8n or mcp__claude_ai_n8n
    AND operation is create/update/deploy AND httpRequest node detected in
    JSON-serialized tool_input AND not justified.

Spec: docs/superpowers/specs/2026-05-15-phase-2-architecture-spec.md (Part A)
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


def _payload(tool_name, tool_input, hook_event_name="PreToolUse"):
    return {
        "hook_event_name": hook_event_name,
        "tool_name": tool_name,
        "tool_input": tool_input,
    }


HTTP_NODE_JSON = (
    '{\n'
    '  "nodes": [\n'
    '    {\n'
    '      "name": "HTTP Request",\n'
    '      "type": "n8n-nodes-base.httpRequest",\n'
    '      "parameters": {\n'
    '        "url": "https://api.example-unknown.com/foo"\n'
    '      }\n'
    '    }\n'
    '  ]\n'
    '}\n'
)

HTTP_NODE_JSON_ALLOWLISTED = (
    '{\n'
    '  "nodes": [\n'
    '    {\n'
    '      "name": "Firecrawl Scrape",\n'
    '      "type": "n8n-nodes-base.httpRequest",\n'
    '      "parameters": {\n'
    '        "url": "https://api.firecrawl.dev/scrape"\n'
    '      }\n'
    '    }\n'
    '  ]\n'
    '}\n'
)

HTTP_NODE_JSON_WITH_JUSTIFICATION = (
    '{\n'
    '  "nodes": [\n'
    '    {\n'
    '      "name": "Custom API",\n'
    '      "notes": "allow-http: legacy webhook, no native node exists",\n'
    '      "type": "n8n-nodes-base.httpRequest",\n'
    '      "parameters": {\n'
    '        "url": "https://api.example-unknown.com/foo"\n'
    '      }\n'
    '    }\n'
    '  ]\n'
    '}\n'
)

HTTP_NODE_JSON_SUFFIX = (
    '{\n'
    '  "nodes": [\n'
    '    {\n'
    '      "type": "n8n-nodes-base.httpRequest",\n'
    '      "parameters": {\n'
    '        "url": "https://prod.sharkitectdigital.com/internal-api"\n'
    '      }\n'
    '    }\n'
    '  ]\n'
    '}\n'
)

HTTP_NODE_NO_URL = (
    '{\n'
    '  "nodes": [\n'
    '    {\n'
    '      "type": "n8n-nodes-base.httpRequest"\n'
    '    }\n'
    '  ]\n'
    '}\n'
)

NON_HTTP_NODE_JSON = (
    '{\n'
    '  "nodes": [\n'
    '    {\n'
    '      "type": "n8n-nodes-base.slack",\n'
    '      "parameters": {}\n'
    '    }\n'
    '  ]\n'
    '}\n'
)


# ---------------------------------------------------------------------------
# Surface 1: Write/Edit on n8n workflow JSON
# ---------------------------------------------------------------------------

class TestN8nHttpWriteEdit:
    def test_write_httpRequest_no_justification_denies(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": HTTP_NODE_JSON},
        ))
        assert result is not None
        assert result.get("decision") == "deny"
        assert "httpRequest" in result.get("reason", "")
        assert "api.example-unknown.com" in result.get("reason", "")

    def test_write_httpRequest_allow_http_comment_passes(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": HTTP_NODE_JSON_WITH_JUSTIFICATION},
        ))
        assert result is None

    def test_write_httpRequest_allowlisted_host_passes(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": HTTP_NODE_JSON_ALLOWLISTED},
        ))
        assert result is None

    def test_write_httpRequest_allowlisted_suffix_passes(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "n8n" / "wf.json"),
             "content": HTTP_NODE_JSON_SUFFIX},
        ))
        assert result is None

    def test_write_httpRequest_no_url_denies_unparseable(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": HTTP_NODE_NO_URL},
        ))
        assert result is not None
        assert result.get("decision") == "deny"
        assert "unparseable" in result.get("reason", "").lower() or "url" in result.get("reason", "").lower()

    def test_write_non_http_node_passes(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": NON_HTTP_NODE_JSON},
        ))
        assert result is None

    def test_write_non_workflow_path_passes(self):
        """Path doesn't look like an n8n workflow JSON -> sub-rule pass-through.
        Even if content contains httpRequest, non-workflow paths are not in scope.

        Uses a literal path string to avoid pytest tmp_path containing the
        substring "n8n" from the test function name (which would false-trigger
        the n8n keyword check that source preserves verbatim).
        """
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": "/home/user/docs/config.json",
             "content": HTTP_NODE_JSON},
        ))
        assert result is None

    def test_write_empty_content_passes(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": ""},
        ))
        assert result is None

    def test_edit_uses_new_string_for_content(self, tmp_path):
        """Edit tool: source extracts content via new_string fallback."""
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Edit",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "old_string": "stub",
             "new_string": HTTP_NODE_JSON},
        ))
        assert result is not None
        assert result.get("decision") == "deny"

    def test_path_n8n_keyword_detection(self, tmp_path):
        """Paths containing 'n8n' keyword count as n8n workflow paths."""
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "src" / "my-n8n-export.json"),
             "content": HTTP_NODE_JSON},
        ))
        assert result is not None
        assert result.get("decision") == "deny"

    def test_workflow_keyword_in_filename(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "exports" / "my-workflow.json"),
             "content": HTTP_NODE_JSON},
        ))
        assert result is not None
        assert result.get("decision") == "deny"


# ---------------------------------------------------------------------------
# Surface 2: n8n MCP create/update/deploy calls
# ---------------------------------------------------------------------------

class TestN8nHttpMcpCalls:
    """MCP n8n trigger surface. Source serializes tool_input via json.dumps
    and runs regex on the result; nested-dict tool_input shapes are detected,
    while a string-valued JSON param has its inner quotes escaped and bypasses
    detection. Tests preserve source behavior on the nested-dict shape (the
    realistic MCP n8n call shape).
    """

    def test_mcp_n8n_create_with_http_denies(self):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "mcp__n8n-mcp__n8n_create_workflow",
            {"name": "test", "nodes": [{
                "type": "n8n-nodes-base.httpRequest",
                "parameters": {"url": "https://random.example.com/x"},
            }]},
        ))
        assert result is not None
        assert result.get("decision") == "deny"

    def test_mcp_n8n_update_with_allowlist_passes(self):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "mcp__claude_ai_n8n__update_workflow",
            {"id": "abc", "nodes": [{
                "type": "n8n-nodes-base.httpRequest",
                "parameters": {"url": "https://api.firecrawl.dev/scrape"},
            }]},
        ))
        assert result is None

    def test_mcp_n8n_get_workflow_passes(self):
        """Read-only MCP n8n calls are not in scope (no create/update/deploy)."""
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "mcp__n8n-mcp__n8n_get_workflow",
            {"id": "abc"},
        ))
        assert result is None

    def test_non_n8n_mcp_passes(self):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "mcp__supabase__execute_sql",
            {"query": "SELECT 1"},
        ))
        assert result is None

    def test_mcp_n8n_create_with_justification_passes(self):
        """Inline notes containing allow-http: comment passes (justification)."""
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "mcp__n8n__create_workflow_from_code",
            {"nodes": [{
                "type": "n8n-nodes-base.httpRequest",
                "notes": "allow-http: legacy webhook, no native node",
                "parameters": {"url": "https://random.example.com/x"},
            }]},
        ))
        assert result is None

    def test_mcp_n8n_deploy_with_http_denies(self):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "mcp__n8n-mcp__n8n_deploy_template",
            {"template": {"nodes": [{
                "type": "n8n-nodes-base.httpRequest",
                "parameters": {"url": "https://random.example.com/x"},
            }]}},
        ))
        assert result is not None
        assert result.get("decision") == "deny"


# ---------------------------------------------------------------------------
# Pass-through cases
# ---------------------------------------------------------------------------

class TestN8nHttpPassThrough:
    def test_unrelated_tool_passes(self):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload("Read", {"file_path": "/foo.json"}))
        assert result is None

    def test_bash_tool_passes(self):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload("Bash", {"command": "ls"}))
        assert result is None

    def test_grep_tool_passes(self):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload("Grep", {"pattern": "httpRequest"}))
        assert result is None

    def test_empty_payload_passes(self):
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate({})
        assert result is None

    def test_tool_input_as_string_decoded(self):
        """When tool_input arrives as JSON string, sub-rule decodes it."""
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "mcp__n8n-mcp__n8n_create_workflow",
            json.dumps({"nodes": [{
                "type": "n8n-nodes-base.httpRequest",
                "parameters": {"url": "https://random.example.com/x"},
            }]}),
        ))
        assert result is not None
        assert result.get("decision") == "deny"

    def test_malformed_tool_input_string_passes(self):
        """Unparseable JSON in tool_input does not crash."""
        from _dispatchers.methodology import n8n_http
        result = n8n_http.evaluate(_payload(
            "mcp__n8n-mcp__n8n_create_workflow",
            "not-json-{{{",
        ))
        # Sub-rule should not crash; either pass-through or deny gracefully.
        # Source behavior: tool_input becomes {} on parse fail -> no httpRequest -> pass
        assert result is None


# ---------------------------------------------------------------------------
# Config / allowlist
# ---------------------------------------------------------------------------

class TestN8nHttpAllowlistConfig:
    def test_custom_config_overrides_defaults(self, tmp_path, monkeypatch):
        """When config file present, it replaces defaults."""
        from _dispatchers.methodology import n8n_http
        config_dir = tmp_path / ".claude" / "config"
        config_dir.mkdir(parents=True)
        config = config_dir / "n8n-http-allowlist.json"
        config.write_text(json.dumps({
            "hosts": ["custom.example.io"],
            "host_suffixes": [],
        }), encoding="utf-8")

        # Patch CONFIG_PATH to point at our test fixture
        monkeypatch.setattr(n8n_http, "CONFIG_PATH", config)

        # firecrawl.dev no longer allowlisted (defaults overridden)
        custom_blocked = HTTP_NODE_JSON_ALLOWLISTED.replace(
            "api.firecrawl.dev", "api.firecrawl.dev"  # firecrawl no longer in custom list
        )
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": custom_blocked},
        ))
        assert result is not None
        assert result.get("decision") == "deny"

        # custom.example.io IS allowed
        custom_url = HTTP_NODE_JSON_ALLOWLISTED.replace(
            "api.firecrawl.dev", "custom.example.io",
        )
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": custom_url},
        ))
        assert result is None

    def test_missing_config_falls_back_to_defaults(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import n8n_http
        nonexistent = tmp_path / "no" / "config.json"
        monkeypatch.setattr(n8n_http, "CONFIG_PATH", nonexistent)

        # Defaults should still allow firecrawl.dev
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": HTTP_NODE_JSON_ALLOWLISTED},
        ))
        assert result is None

    def test_malformed_config_falls_back_to_defaults(self, tmp_path, monkeypatch):
        from _dispatchers.methodology import n8n_http
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        bad_config = config_dir / "bad.json"
        bad_config.write_text("{not-json", encoding="utf-8")
        monkeypatch.setattr(n8n_http, "CONFIG_PATH", bad_config)

        # Defaults still allow firecrawl.dev
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": HTTP_NODE_JSON_ALLOWLISTED},
        ))
        assert result is None


# ---------------------------------------------------------------------------
# Mixed URL hosts: deny if ANY is unjustified
# ---------------------------------------------------------------------------

class TestN8nHttpMixedHosts:
    def test_one_unjustified_among_multiple_denies(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        mixed = (
            '{\n'
            '  "nodes": [\n'
            '    {"type": "n8n-nodes-base.httpRequest",\n'
            '     "parameters": {"url": "https://api.firecrawl.dev/x"}},\n'
            '    {"type": "n8n-nodes-base.httpRequest",\n'
            '     "parameters": {"url": "https://random.example.com/y"}}\n'
            '  ]\n'
            '}\n'
        )
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": mixed},
        ))
        assert result is not None
        assert result.get("decision") == "deny"
        # random.example.com should be in the reason
        assert "random.example.com" in result.get("reason", "")

    def test_all_allowlisted_passes(self, tmp_path):
        from _dispatchers.methodology import n8n_http
        all_ok = (
            '{\n'
            '  "nodes": [\n'
            '    {"type": "n8n-nodes-base.httpRequest",\n'
            '     "parameters": {"url": "https://api.firecrawl.dev/x"}},\n'
            '    {"type": "n8n-nodes-base.httpRequest",\n'
            '     "parameters": {"url": "https://prod.internal/y"}}\n'
            '  ]\n'
            '}\n'
        )
        result = n8n_http.evaluate(_payload(
            "Write",
            {"file_path": str(tmp_path / "workflows" / "wf.json"),
             "content": all_ok},
        ))
        assert result is None
