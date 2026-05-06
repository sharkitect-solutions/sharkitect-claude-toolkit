"""methodology-dispatcher.py - Top-level entry for the methodology hook cluster.

skip hook-development -- this dispatcher is the orchestration layer for 13
already-shipped sub-rules under _dispatchers/methodology/, built per the locked
consolidation spec. The sub-rules themselves encode the PreToolUse/PostToolUse/
graceful-degradation patterns the hook-development skill teaches; this
dispatcher merely routes and merges their outputs.

Reads JSON from stdin per the Claude Code hook protocol, routes the payload
to applicable methodology sub-rules under _dispatchers/methodology/, and
emits the merged hookSpecificOutput.

Routing (see docs/superpowers/specs/2026-05-05-hook-dispatcher-consolidation-spec.md):

  PreToolUse  -> brainstorming, writing_plans, claude_api, multistep_plan,
                 supabase_ddl, deep_interview, plan_file_read,
                 multi_file_build, production_tool, creation_gate
  PostToolUse -> iterative_work, mcp_auth_error
  UserPromptSubmit -> process_violation

Each sub-rule's evaluate() returns one of:
  None                                  -> no contribution
  {"advisory": "<text>"}                -> ADVISORY (additionalContext)
  {"decision": "deny", "reason": "..."} -> HARD GATE (permissionDecision deny)

Result merging:
  - First HARD GATE wins; subsequent sub-rules are not called.
  - All ADVISORY contributions are concatenated with "---" separators.
  - No contributions -> no stdout output.

Pattern preserved:
  - Each sub-rule is responsible for its own tool_name filtering, bypass
    checks, and intent_detection layer. The dispatcher does NOT pre-filter
    by tool_name; it calls every sub-rule for the event class and lets each
    decide.
  - Sub-rule exceptions are caught -> graceful degradation (no nudge rather
    than crash).

Settings.json wiring (deferred to Phase 2 -- requires user authorization):
  Three matcher entries call this dispatcher with different event filters.
  Until then, source hooks remain wired and this dispatcher is dormant
  except via direct unit-test invocation.

Source: docs/superpowers/specs/2026-05-05-hook-dispatcher-consolidation-spec.md
"""
from __future__ import annotations

import json
import os
import sys

# Ensure _dispatchers package is importable
_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)


def _safe_import(modname):
    """Import a sub-rule module, return None on failure (graceful degradation)."""
    try:
        return __import__(
            "_dispatchers.methodology." + modname,
            fromlist=[modname],
        )
    except Exception:
        return None


_brainstorming = _safe_import("brainstorming")
_writing_plans = _safe_import("writing_plans")
_claude_api = _safe_import("claude_api")
_multistep_plan = _safe_import("multistep_plan")
_supabase_ddl = _safe_import("supabase_ddl")
_deep_interview = _safe_import("deep_interview")
_process_violation = _safe_import("process_violation")
_iterative_work = _safe_import("iterative_work")
_mcp_auth_error = _safe_import("mcp_auth_error")
_plan_file_read = _safe_import("plan_file_read")
_multi_file_build = _safe_import("multi_file_build")
_production_tool = _safe_import("production_tool")
_creation_gate = _safe_import("creation_gate")


# Order matters for advisory concatenation; HARD GATE sub-rules go first so
# their deny short-circuits before lower-severity advisories run.
PRE_TOOL_USE_SUBRULES = [
    _brainstorming,        # HARD GATE
    _writing_plans,        # HARD GATE
    _supabase_ddl,         # HARD GATE
    _creation_gate,        # HARD GATE (Tier 1) + Advisory (Tier 2)
    _claude_api,           # Advisory
    _multistep_plan,       # Advisory
    _deep_interview,       # Advisory
    _plan_file_read,       # Advisory
    _multi_file_build,     # Advisory
    _production_tool,      # Advisory
]
POST_TOOL_USE_SUBRULES = [
    _iterative_work,       # Advisory
    _mcp_auth_error,       # Advisory
]
USER_PROMPT_SUBMIT_SUBRULES = [
    _process_violation,    # Advisory
]

EVENT_TO_SUBRULES = {
    "PreToolUse": PRE_TOOL_USE_SUBRULES,
    "PostToolUse": POST_TOOL_USE_SUBRULES,
    "UserPromptSubmit": USER_PROMPT_SUBMIT_SUBRULES,
}


def dispatch(payload):
    """Route payload to applicable sub-rules. Returns merged hook output dict or None.

    Args:
      payload: dict with at least:
        - hook_event_name: "PreToolUse" | "PostToolUse" | "UserPromptSubmit"
        - tool_name: str (for PreToolUse / PostToolUse)
        - tool_input: dict
        - transcript_path: str | None
        - other event-specific fields

    Returns:
      None -> no contribution from any sub-rule
      dict -> {"hookSpecificOutput": {...}}
    """
    event = payload.get("hook_event_name", "")
    sub_rules = EVENT_TO_SUBRULES.get(event, [])

    advisories = []
    for sub in sub_rules:
        if sub is None:  # import failed; skip
            continue
        try:
            result = sub.evaluate(payload)
        except Exception:
            continue  # graceful degradation
        if result is None:
            continue
        # HARD GATE short-circuits
        if isinstance(result, dict) and result.get("decision") == "deny":
            return {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "deny",
                    "permissionDecisionReason": result.get("reason", ""),
                }
            }
        if isinstance(result, dict) and "advisory" in result:
            advisories.append(str(result["advisory"]))

    if not advisories:
        return None

    merged = "\n\n---\n\n".join(advisories)
    return {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": merged,
        }
    }


def main():
    """Stdin/stdout entry per Claude Code hook protocol."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0

    result = dispatch(payload)
    if result is not None:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
