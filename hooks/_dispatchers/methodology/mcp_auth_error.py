"""mcp_auth_error.py - Methodology dispatcher sub-rule.

Source: mcp-auth-error-guard.py (PostToolUse advisory after 2+ consecutive
MCP auth/permission errors per server).

Behavior preserved 1:1 from source:
  - Per-server counter (server extracted from mcp__<server>__<tool>)
  - Auth error patterns: permission denied, unauthorized, 401, 403,
    invalid token, invalid api key, invalid credentials, access denied,
    forbidden, not authorized, insufficient permissions / scope,
    missing scope, invalid grant, token expired, token revoked
  - Threshold: 2 consecutive failures -> ADVISORY
  - Success on the same server resets the counter
  - Non-auth errors leave the counter unchanged (different failure mode)
  - Non-MCP tools ignored

NEW LAYER: intent_detection user-driven mode -- if the user has
explicitly directed manual error gathering (e.g., "let it fail repeatedly
while I gather error samples"), the advisory is suppressed.

Severity: ADVISORY (returns {"advisory": "<text>"})

Source incident (2026-04-17): Sentinel session ran 10+ turns of
unstructured provider speculation when Supabase MCP rejected calls. Real
cause: wrong project_id. The cheapest highest-prior cause is YOUR INPUT.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

_SCRIPTS_LIB = os.path.expanduser("~/.claude/scripts/_lib")
if _SCRIPTS_LIB not in sys.path:
    sys.path.insert(0, _SCRIPTS_LIB)
try:
    from intent_detection import is_user_driven  # type: ignore
except Exception:
    is_user_driven = None

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events
except Exception:
    _feedback_events = None


TMP_DIR = Path.home() / ".claude" / ".tmp"
STATE_FILE = TMP_DIR / "mcp-auth-failures.json"

THRESHOLD = 2

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

BYPASS_PHRASES = (
    "skip mcp-auth-nudge",
    "skip auth-error-guard",
    "no auth-error nudge",
)
TRANSCRIPT_USER_LOOKBACK = 3


def _load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return {}


def _save_state(state):
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def _extract_server(tool_name):
    if not tool_name.startswith("mcp__"):
        return None
    parts = tool_name.split("__")
    if len(parts) < 3:
        return None
    return parts[1]


def _response_text(payload):
    chunks = []
    for key in ("tool_response", "tool_result", "response", "result"):
        val = payload.get(key)
        if val is None:
            continue
        if isinstance(val, str):
            chunks.append(val)
        else:
            try:
                chunks.append(json.dumps(val))
            except (TypeError, ValueError):
                chunks.append(str(val))
    err = payload.get("error")
    if err:
        if isinstance(err, str):
            chunks.append(err)
        else:
            try:
                chunks.append(json.dumps(err))
            except (TypeError, ValueError):
                chunks.append(str(err))
    return "\n".join(chunks)


def _is_auth_error(text):
    if not text:
        return False
    lower = text.lower()
    for pat in AUTH_ERROR_PATTERNS:
        if pat in lower:
            return True
    return False


def _detect_error_signal(payload):
    text = _response_text(payload)
    is_error_flag = bool(payload.get("is_error")) or bool(payload.get("error"))
    status = payload.get("status") or payload.get("status_code")
    status_is_err = False
    if isinstance(status, (int, str)):
        try:
            code = int(str(status))
            status_is_err = code >= 400
        except ValueError:
            status_is_err = False

    auth_match = _is_auth_error(text)

    snippet = ""
    if auth_match:
        lower = text.lower()
        for pat in AUTH_ERROR_PATTERNS:
            idx = lower.find(pat)
            if idx >= 0:
                start = max(0, idx - 60)
                end = min(len(text), idx + len(pat) + 60)
                snippet = text[start:end].replace("\n", " ").strip()
                break

    return (is_error_flag or status_is_err or auth_match, auth_match, snippet)


def evaluate(payload):
    """Evaluate mcp_auth_error sub-rule.

    Returns:
      None                       -> sub-rule did not trigger
      {"advisory": "<text>"}     -> ADVISORY soft nudge
    """
    tool_name = payload.get("tool_name", "")
    server = _extract_server(tool_name)
    if not server:
        return None

    is_error, is_auth, snippet = _detect_error_signal(payload)

    state = _load_state()
    server_state = state.get(server, {"count": 0})

    if is_auth:
        server_state["count"] = int(server_state.get("count", 0)) + 1
        server_state["last_error"] = snippet[:240]
        server_state["last_seen"] = datetime.now().isoformat()
        state[server] = server_state
        _save_state(state)

        if server_state["count"] < THRESHOLD:
            return None

        # NEW LAYER: intent_detection user-driven bypass
        transcript_path = payload.get("transcript_path") or ""
        if is_user_driven is not None:
            try:
                if is_user_driven(
                    transcript_path, file_path=None,
                    bypass_phrases=BYPASS_PHRASES,
                    lookback=TRANSCRIPT_USER_LOOKBACK,
                ):
                    if _feedback_events:
                        _feedback_events.record(
                            cluster="methodology", sub_rule="mcp_auth_error",
                            decision="pass_through",
                            trigger="intent_detection_user_driven",
                            payload=payload,
                        )
                    return None
            except Exception:
                pass

        n = server_state["count"]
        advisory_text = (
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

        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="mcp_auth_error",
                decision="advisory", trigger=f"server:{server}:n:{n}",
                payload=payload,
            )
        return {"advisory": advisory_text}

    # Non-auth-error response: if appears successful, reset counter
    if not is_error:
        if server in state and int(state[server].get("count", 0)) > 0:
            state[server] = {"count": 0, "reset_at": datetime.now().isoformat()}
            _save_state(state)

    # Non-auth error with is_error: leave counter unchanged
    return None
