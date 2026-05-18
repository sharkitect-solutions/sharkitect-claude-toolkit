"""n8n_http.py - Methodology dispatcher sub-rule (Phase 2 Build #2B).

Source: n8n-httpRequest-guard.py (HARD GATE on n8n-nodes-base.httpRequest
without justification or allowlist match).

Behavior preserved 1:1 from source:
  Trigger 1 (Write/Edit): file path looks like n8n workflow JSON AND content
    contains n8n-nodes-base.httpRequest node AND not justified.
  Trigger 2 (n8n MCP create/update/deploy): tool_name starts with mcp__n8n
    or mcp__claude_ai_n8n AND operation is create/update/deploy AND
    httpRequest detected in JSON-serialized tool_input AND not justified.

Justification (any one passes through):
  1. Inline allow-http: <reason> comment in workflow content
  2. Every URL host found is on the allowlist (hosts or host_suffixes)

Allowlist source: ~/.claude/config/n8n-http-allowlist.json if present;
DEFAULT_ALLOWLIST otherwise. Malformed config falls back to defaults.

Severity: HARD GATE (returns {"decision": "deny", "reason": ...})

Source incident: wr-2026-04-17-008. Default n8n behavior was to use
httpRequest for every service even when native nodes existed. Hook moved
the choice from default-httpRequest to default-native-node-or-justify.

Spec: docs/superpowers/specs/2026-05-15-phase-2-architecture-spec.md (Part A)
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events
except Exception:
    _feedback_events = None


HTTP_NODE_RE = re.compile(r'"type"\s*:\s*"n8n-nodes-base\.httpRequest"', re.I)
ALLOW_COMMENT_RE = re.compile(r"allow[-_]http\s*:\s*([^\n\"'*/]+)", re.I)
URL_HOST_RE = re.compile(r'"url"\s*:\s*"https?://([^/"\\]+)', re.I)

CONFIG_PATH = Path.home() / ".claude" / "config" / "n8n-http-allowlist.json"

DEFAULT_ALLOWLIST = {
    "hosts": [
        "api.firecrawl.dev",
        "firecrawl.dev",
        "localhost",
        "127.0.0.1",
        "host.docker.internal",
    ],
    "host_suffixes": [
        ".sharkitectdigital.com",
        ".internal",
        ".local",
    ],
}


def load_allowlist():
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return {
                "hosts": [h.lower() for h in data.get("hosts", [])],
                "host_suffixes": [s.lower() for s in data.get("host_suffixes", [])],
            }
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "hosts": [h.lower() for h in DEFAULT_ALLOWLIST["hosts"]],
        "host_suffixes": [s.lower() for s in DEFAULT_ALLOWLIST["host_suffixes"]],
    }


def url_is_allowlisted(url_host, allowlist):
    h = url_host.lower()
    if h in allowlist["hosts"]:
        return True
    return any(h.endswith(suffix) for suffix in allowlist["host_suffixes"])


def justified(content):
    """True if content contains an allow-http: justification comment."""
    return bool(ALLOW_COMMENT_RE.search(content))


def find_violations(content, allowlist):
    """Return list of {host, justified} for each httpRequest node found.
    Empty list = no httpRequest nodes detected.
    """
    if not HTTP_NODE_RE.search(content):
        return []

    if justified(content):
        return [{"host": "<global allow-http comment>", "justified": True}]

    hosts = URL_HOST_RE.findall(content)
    if not hosts:
        return [{"host": "<unparseable url>", "justified": False}]

    violations = []
    for h in hosts:
        violations.append({"host": h, "justified": url_is_allowlisted(h, allowlist)})
    return violations


def is_n8n_workflow_path(file_path):
    if not file_path:
        return False
    p = file_path.replace("\\", "/").lower()
    return (
        p.endswith(".json")
        and ("n8n" in p or "/workflows/" in p or "workflow" in Path(p).name)
    )


def _deny_reason_write(unjustified):
    hosts = ", ".join(v["host"] for v in unjustified)
    return (
        f"BLOCKED: Adding n8n-nodes-base.httpRequest without justification.\n"
        f"Host(s): {hosts}\n\n"
        "Native n8n nodes exist for GitHub, HubSpot, Supabase, Brevo, Slack, "
        "Gmail, Google Sheets/Drive/Calendar, Notion, and many others. Use the "
        "native node for per-operation context, credential auto-wiring, and built-in "
        "error semantics.\n\n"
        "If HTTP is genuinely required (no native node exists for this service):\n"
        "  - Add an inline justification comment in the workflow:\n"
        "      \"notes\": \"allow-http: <service name has no native n8n node>\"\n"
        "  - OR add the host to ~/.claude/config/n8n-http-allowlist.json\n\n"
        "Source: wr-2026-04-17-008. See docs/mandatory-skill-invocations.md "
        "(n8n section)."
    )


def _deny_reason_mcp(tool_name, unjustified):
    hosts = ", ".join(v["host"] for v in unjustified)
    return (
        f"BLOCKED: n8n MCP {tool_name} adds n8n-nodes-base.httpRequest without "
        f"justification.\nHost(s): {hosts}\n\n"
        "Use the native n8n node for the target service. If no native node exists, "
        "add an inline allow-http: <reason> comment in the workflow OR add the host "
        "to ~/.claude/config/n8n-http-allowlist.json.\n\n"
        "Source: wr-2026-04-17-008."
    )


def evaluate(payload):
    """Evaluate n8n_http sub-rule.

    Returns:
      None                                  -> sub-rule did not trigger / pass-through
      {"decision": "deny", "reason": "..."} -> HARD GATE
    """
    tool_name = payload.get("tool_name", "")
    if not tool_name:
        return None

    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    allowlist = load_allowlist()

    # ---- Surface 1: Write/Edit on n8n workflow JSON ----------------------
    if tool_name in ("Write", "Edit"):
        file_path = str(tool_input.get("file_path", ""))
        content = str(tool_input.get("content", "") or tool_input.get("new_string", ""))

        if not is_n8n_workflow_path(file_path):
            return None
        if not content:
            return None

        violations = find_violations(content, allowlist)
        if not violations:
            return None

        unjustified = [v for v in violations if not v["justified"]]
        if not unjustified:
            return None

        if _feedback_events:
            try:
                _feedback_events.record(
                    cluster="methodology", sub_rule="n8n_http",
                    decision="hard_deny", trigger="write_edit_unjustified",
                    payload=payload,
                )
            except Exception:
                pass
        return {"decision": "deny", "reason": _deny_reason_write(unjustified)}

    # ---- Surface 2: n8n MCP create/update/deploy calls -------------------
    is_n8n_mcp = tool_name.startswith("mcp__n8n") or tool_name.startswith("mcp__claude_ai_n8n")
    if not is_n8n_mcp:
        return None

    tool_lower = tool_name.lower()
    is_create_or_update = any(k in tool_lower for k in ("create", "update", "deploy"))
    if not is_create_or_update:
        return None

    payload_text = json.dumps(tool_input)
    violations = find_violations(payload_text, allowlist)
    if not violations:
        return None
    unjustified = [v for v in violations if not v["justified"]]
    if not unjustified:
        return None

    if _feedback_events:
        try:
            _feedback_events.record(
                cluster="methodology", sub_rule="n8n_http",
                decision="hard_deny", trigger="mcp_create_update_unjustified",
                payload=payload,
            )
        except Exception:
            pass
    return {"decision": "deny", "reason": _deny_reason_mcp(tool_name, unjustified)}
