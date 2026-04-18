"""
mcp-auth-error-guard.py - PostToolUse hook for repeated MCP auth/permission errors

Tracks per-session-per-MCP-server count of permission/auth/unauthorized errors
in MCP tool responses. After N consecutive failures on the SAME MCP server,
injects a system reminder that nudges the AI to:
  (a) verify the credential and target identifiers it is passing match .env
  (b) invoke `superpowers:systematic-debugging` BEFORE further provider
      speculation

Why: Sessions tend to spiral into provider-side hypotheses (OAuth revocation,
integration downgrade, API rollout) when MCP returns "permission denied"
repeatedly. The cheapest highest-prior cause -- wrong input -- is usually
skipped entirely. This hook catches the pattern at turn 2 and forces a
hypothesis loop instead of unstructured speculation.

State: per-session counter at ~/.claude/.tmp/mcp-auth-failures.json
  { "<server>": {"count": N, "last_error": "...", "last_seen": "<ISO>"} }
Counter resets to 0 for a server when ANY successful call to that server
is observed.

Threshold: 2 consecutive failures triggers the nudge. Configurable via
the THRESHOLD constant.

Non-blocking: injects additional context, never denies the operation.
Pure stdlib. ASCII-only output (Windows cp1252 console rule).

Input: JSON on stdin with tool_name, tool_input, tool_response (or tool_result)
Output: JSON on stdout with hookSpecificOutput.additionalContext (if nudge)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"
STATE_FILE = TMP_DIR / "mcp-auth-failures.json"

THRESHOLD = 2  # consecutive failures before we nudge

# Patterns that indicate an auth/permission failure in the MCP response
# Case-insensitive substring matches.
AUTH_ERROR_PATTERNS = [
    "permission denied",
    "unauthorized",
    "auth failed",
    "authentication failed",
    "invalid token",
    "invalid api key",
    "invalid credentials",
    "access denied",
    "forbidden",
    "not authorized",
    "401",
    "403",
    "insufficient permissions",
    "insufficient scope",
    "missing scope",
    "invalid grant",
    "token expired",
    "token revoked",
]


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state):
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def extract_server(tool_name):
    """Parse mcp__<server>__<tool> -> '<server>'. Returns None for non-MCP."""
    if not tool_name.startswith("mcp__"):
        return None
    parts = tool_name.split("__")
    if len(parts) < 3:
        return None
    return parts[1]


def response_text(hook_input):
    """Concatenate response/result fields into one searchable string."""
    chunks = []
    for key in ("tool_response", "tool_result", "response", "result"):
        val = hook_input.get(key)
        if val is None:
            continue
        if isinstance(val, str):
            chunks.append(val)
        else:
            try:
                chunks.append(json.dumps(val))
            except (TypeError, ValueError):
                chunks.append(str(val))
    # Some harnesses also surface error fields explicitly
    err = hook_input.get("error")
    if err:
        if isinstance(err, str):
            chunks.append(err)
        else:
            try:
                chunks.append(json.dumps(err))
            except (TypeError, ValueError):
                chunks.append(str(err))
    return "\n".join(chunks)


def is_auth_error(text):
    if not text:
        return False
    lower = text.lower()
    for pat in AUTH_ERROR_PATTERNS:
        if pat in lower:
            return True
    return False


def detect_error_signal(hook_input):
    """Return (is_error_call, is_auth_error_match, extracted_error_snippet)."""
    text = response_text(hook_input)

    # Some harnesses set is_error / status fields
    is_error_flag = bool(hook_input.get("is_error")) or bool(
        hook_input.get("error")
    )
    # Status code style fields
    status = hook_input.get("status") or hook_input.get("status_code")
    status_is_err = False
    if isinstance(status, (int, str)):
        try:
            code = int(str(status))
            status_is_err = code >= 400
        except ValueError:
            status_is_err = False

    auth_match = is_auth_error(text)

    snippet = ""
    if auth_match:
        # Find first matching pattern's surrounding context for the reminder
        lower = text.lower()
        for pat in AUTH_ERROR_PATTERNS:
            idx = lower.find(pat)
            if idx >= 0:
                start = max(0, idx - 60)
                end = min(len(text), idx + len(pat) + 60)
                snippet = text[start:end].replace("\n", " ").strip()
                break

    return (is_error_flag or status_is_err or auth_match, auth_match, snippet)


def emit(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": text,
        }
    }))


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = hook_input.get("tool_name", "")
    server = extract_server(tool_name)
    if not server:
        return 0

    is_error, is_auth, snippet = detect_error_signal(hook_input)

    state = load_state()
    server_state = state.get(server, {"count": 0})

    if is_auth:
        server_state["count"] = int(server_state.get("count", 0)) + 1
        server_state["last_error"] = snippet[:240]
        server_state["last_seen"] = datetime.now().isoformat()
        state[server] = server_state
        save_state(state)

        if server_state["count"] >= THRESHOLD:
            n = server_state["count"]
            msg = (
                f"REPEATED MCP AUTH FAILURE on {server} ({n} consecutive). "
                "Before speculating about provider-side issues (OAuth revocation, "
                "API rollout, integration downgrade, scope changes), VERIFY the "
                "credential and target identifier values you are passing match "
                "what your .env / config expects. Common root causes: wrong "
                "project_id, wrong workspace_id, wrong account_id, stale token "
                "from copy-paste, env-var typo, region/instance mismatch.\n\n"
                "Required next step: invoke `superpowers:systematic-debugging` "
                "skill BEFORE further investigation. Cheapest highest-prior "
                "hypothesis is YOUR INPUT, not the provider. Look up your own "
                "credential audit / inventory docs (workforce-hq/.tmp/"
                "credential-audit-workforce-hq.md, .env, etc.) to confirm the "
                "exact values before continuing.\n\n"
                f"Last error excerpt: {snippet[:200]}"
            )
            emit(msg)
        return 0

    # Non-auth-error response: if the call appears successful for this server,
    # reset its counter. We treat "no error signal at all" as success.
    if not is_error:
        if server in state and int(state[server].get("count", 0)) > 0:
            state[server] = {"count": 0, "reset_at": datetime.now().isoformat()}
            save_state(state)
    # If is_error but not auth-related, leave counter unchanged (different
    # failure mode -- not what this hook tracks).

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
