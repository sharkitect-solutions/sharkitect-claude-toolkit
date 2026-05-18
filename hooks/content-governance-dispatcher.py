"""content-governance-dispatcher.py - Top-level entry for content-governance hook cluster.

skip hook-development -- this dispatcher mirrors the methodology-dispatcher
pattern already shipped under the locked Phase 2 architecture spec
(docs/superpowers/specs/2026-05-15-phase-2-architecture-spec.md Part A.3).
The sub-rules under _dispatchers/content_governance/ encode the
PreToolUse/Edit|Write patterns the hook-development skill teaches.

Reads JSON from stdin per the Claude Code hook protocol, routes the
payload to the 4 content-governance sub-rules under
_dispatchers/content_governance/, and emits the merged hookSpecificOutput.

Routing:
  PreToolUse -> marketing_keywords (HARD GATE),
                content_enforcer (Advisory),
                content_pitching (Advisory),
                drift_detection (Advisory)

Each sub-rule's evaluate() returns one of:
  None                                  -> no contribution
  {"advisory": "<text>"}                -> ADVISORY (additionalContext)
  {"decision": "deny", "reason": "..."} -> HARD GATE (permissionDecision deny)

Result merging:
  - First HARD GATE wins; subsequent sub-rules are not called.
  - All ADVISORY contributions are concatenated with "---" separators.
  - No contributions -> no stdout output.

Pattern preserved (matches methodology-dispatcher.py):
  - Each sub-rule is responsible for its own tool_name filtering, bypass
    checks, workspace scoping, and intent_detection. The dispatcher does
    NOT pre-filter; it calls every sub-rule for the event class and lets
    each decide.
  - Sub-rule exceptions are caught -> graceful degradation.

Settings.json wiring (deferred to Build #2 cutover):
  Once this dispatcher is registered on PreToolUse:Edit|Write, the
  matching source hooks (content-enforcer-hook.py,
  marketing-content-detector.py, content-pitching-detector.py,
  drift-detection-hook.py) must be un-registered IN THE SAME atomic
  edit per Phase 2 spec Risk R1 (never leave both firing).

Source: docs/superpowers/specs/2026-05-15-phase-2-architecture-spec.md
        docs/superpowers/specs/2026-05-05-hook-dispatcher-consolidation-spec.md
"""
from __future__ import annotations

import json
import os
import sys

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)


def _safe_import(modname):
    """Import a sub-rule module under _dispatchers.content_governance, return
    None on failure (graceful degradation -- broken sub-rule cannot break
    the dispatcher)."""
    try:
        return __import__(
            "_dispatchers.content_governance." + modname,
            fromlist=[modname],
        )
    except Exception:
        return None


_marketing_keywords = _safe_import("marketing_keywords")
_content_enforcer = _safe_import("content_enforcer")
_content_pitching = _safe_import("content_pitching")
_drift_detection = _safe_import("drift_detection")


# Order matters for advisory concatenation; HARD GATE sub-rules go first
# so their deny short-circuits before lower-severity advisories run.
PRE_TOOL_USE_SUBRULES = [
    _marketing_keywords,   # HARD GATE
    _content_enforcer,     # Advisory
    _content_pitching,     # Advisory
    _drift_detection,      # Advisory
]


EVENT_TO_SUBRULES = {
    "PreToolUse": PRE_TOOL_USE_SUBRULES,
}


def dispatch(payload):
    """Route payload to applicable sub-rules. Returns merged hook output dict or None.

    Args:
      payload: dict with at least:
        - hook_event_name: "PreToolUse"
        - tool_name: str
        - tool_input: dict
        - transcript_path: str | None
        - other event-specific fields

    Returns:
      None -> no contribution from any sub-rule
      dict -> {"hookSpecificOutput": {...}}

    Decision precedence: deny > advisory.
      - deny short-circuits the whole chain.
      - advisory-only fires when no deny present; multiple advisories
        merge with "\n\n---\n\n".
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
