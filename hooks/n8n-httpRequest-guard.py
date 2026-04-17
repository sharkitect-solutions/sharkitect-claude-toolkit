"""
n8n-httpRequest-guard.py - PreToolUse HARD BLOCK on n8n-nodes-base.httpRequest

Blocks Write/Edit/n8n-mcp create+update calls that add the
n8n-nodes-base.httpRequest node UNLESS:

  1. The content includes a justification comment matching:
       "// allow-http: <reason>"  OR  "/* allow-http: <reason> */"
       (also accepted in workflow description / node notes)
  2. The HTTP target service is on the allowlist (configurable at
     ~/.claude/config/n8n-http-allowlist.json -- defaults inline below)

Allowlist defaults: services without native n8n nodes that legitimately
require HTTP (Firecrawl, internal corporate APIs, custom webhooks).

Hard block via permissionDecision: "deny" with a clear reason. AI must add
justification or rebuild with the native node.

Trigger surfaces:
  - Write/Edit on *.json files containing the n8n-nodes-base.httpRequest type
  - mcp__n8n__create_workflow_*, mcp__n8n__update_workflow_*,
    mcp__n8n-mcp__n8n_create_workflow, mcp__n8n-mcp__n8n_update_*

Pure Python stdlib.

Input: JSON on stdin
Output: JSON on stdout with permissionDecision (block) or empty (allow)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


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
    "notes": "Hosts/suffixes that legitimately require HTTP because no native n8n node exists.",
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
    A node is justified if (a) inline allow-http comment OR (b) URL host on allowlist.
    Returns empty list if no httpRequest nodes detected."""
    if not HTTP_NODE_RE.search(content):
        return []

    if justified(content):
        return [{"host": "<global allow-http comment>", "justified": True}]

    hosts = URL_HOST_RE.findall(content)
    if not hosts:
        # Has httpRequest node but no URL parseable -- treat as unjustified
        return [{"host": "<unparseable url>", "justified": False}]

    violations = []
    for h in hosts:
        violations.append({"host": h, "justified": url_is_allowlisted(h, allowlist)})
    return violations


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def is_n8n_workflow_path(file_path):
    if not file_path:
        return False
    p = file_path.replace("\\", "/").lower()
    return (
        p.endswith(".json")
        and ("n8n" in p or "/workflows/" in p or "workflow" in Path(p).name)
    )


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    allowlist = load_allowlist()

    # ---- Surface 1: Write/Edit on n8n workflow JSON ----------------------
    if tool_name in ("Write", "Edit"):
        file_path = str(tool_input.get("file_path", ""))
        content = str(tool_input.get("content", "") or tool_input.get("new_string", ""))

        if not is_n8n_workflow_path(file_path):
            return 0
        if not content:
            return 0

        violations = find_violations(content, allowlist)
        if not violations:
            return 0

        unjustified = [v for v in violations if not v["justified"]]
        if not unjustified:
            return 0

        hosts = ", ".join(v["host"] for v in unjustified)
        deny(
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
        return 0

    # ---- Surface 2: n8n MCP create/update calls --------------------------
    is_n8n_mcp = tool_name.startswith("mcp__n8n") or tool_name.startswith("mcp__claude_ai_n8n")
    is_create_or_update = any(k in tool_name.lower() for k in ("create", "update", "deploy"))
    if is_n8n_mcp and is_create_or_update:
        # Concatenate any string fields in tool_input that might carry workflow JSON
        payload = json.dumps(tool_input)
        violations = find_violations(payload, allowlist)
        if not violations:
            return 0
        unjustified = [v for v in violations if not v["justified"]]
        if not unjustified:
            return 0
        hosts = ", ".join(v["host"] for v in unjustified)
        deny(
            f"BLOCKED: n8n MCP {tool_name} adds n8n-nodes-base.httpRequest without "
            f"justification.\nHost(s): {hosts}\n\n"
            "Use the native n8n node for the target service. If no native node exists, "
            "add an inline allow-http: <reason> comment in the workflow OR add the host "
            "to ~/.claude/config/n8n-http-allowlist.json.\n\n"
            "Source: wr-2026-04-17-008."
        )
        return 0

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
