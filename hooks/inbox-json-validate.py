"""
inbox-json-validate.py - PreToolUse BLOCKING hook for inbox JSON correctness

Validates JSON syntax BEFORE Write/Edit lands a malformed file in any
inbox / processed / outbox directory. Blocks the operation if the JSON
parser rejects the content.

DETECTION
  Tool: Write or Edit
  Path matches one of these segments (forward or back slash):
    .routed-tasks/inbox/      .routed-tasks/processed/      .routed-tasks/outbox/
    .work-requests/inbox/     .work-requests/processed/     .work-requests/outbox/
    .lifecycle-reviews/inbox/ .lifecycle-reviews/processed/ .lifecycle-reviews/outbox/
  AND filename ends in .json

VALIDATION
  Write: parse the full content with json.loads
  Edit:  parse the new_string field with json.loads (only if it looks like
         a complete JSON document; partial fragments allow through with
         a warning instead of a block, since Edit may patch a single field)

WHY THIS EXISTS
  Source: wr-2026-04-25-005 (Sentinel, CRITICAL). HQ-emitted routed-task
  rt-2026-04-25-watcher-watcher-blueprint contained literal Windows
  backslashes in notify_inbox_path. Single-backslash sequences in JSON
  string values are rejected by json.load with 'Invalid escape' error.
  Cascading impact: close-inbox-item.py couldn't read the file, audit
  scripts skipped/errored on it, Completion Notification Protocol
  couldn't route the auto-notification.

  Hand-emitted JSON via the Write tool bypasses the round-trip safety
  json.dumps() provides. This hook adds the safety net.

BYPASS
  1. Recent user message contains: "skip json-validate", "skip inbox-validate"
  2. File doesn't match the inbox path pattern (most files pass through)
  3. Hook removed from settings.json

GRACEFUL DEGRADATION
  - Edit on a partial JSON fragment (new_string is not a full document)
    -> warn but ALLOW (avoid blocking partial edits like {"status": "x"})
  - Any unhandled exception -> exit 0 (allow)

Pure stdlib. ASCII-only output.
"""

from __future__ import annotations

import json
import os
import re
import sys


INBOX_PATH_RE = re.compile(
    r"[/\\]\.(?:routed-tasks|work-requests|lifecycle-reviews)[/\\](?:inbox|processed|outbox)[/\\]",
    re.I,
)

# WR id schema (wr-2026-04-25-007). v2 is workspace-prefixed.
# v1 (legacy) is unprefixed; preserved for backward compat.
ID_RE_V2 = re.compile(r"^(wr|rt)-(hq|skillhub|sentinel)-\d{4}-\d{2}-\d{2}-(\d{3}|[a-z0-9-]+)$")
ID_RE_V1 = re.compile(r"^(wr|rt)-\d{4}-\d{2}-\d{2}-(\d{3}|[a-z0-9-]+)$")

BYPASS_PHRASES = (
    "skip json-validate",
    "skip inbox-validate",
    "skip inbox-json-validate",
    "skip wr-id-schema",  # bypass id-schema check only
)
TRANSCRIPT_USER_LOOKBACK = 3


def validate_wr_id_schema(parsed_json):
    """Return (ok: bool, reason: str). Enforces id presence + format.

    v2 (id_format_version >= 2): id MUST match ID_RE_V2 (workspace-prefixed).
    v1 (default): id is optional but if present must match v1 or v2 pattern.

    Source: wr-2026-04-25-007. Defense-in-depth complement to:
      - work-request.py (creation gate; emits v2 only)
      - close-inbox-item.py (closure gate; refuses v2 close without id)
    """
    try:
        fmt = int(parsed_json.get("id_format_version", 1) or 1)
    except (TypeError, ValueError):
        fmt = 1
    wr_id = parsed_json.get("id")
    if fmt >= 2:
        if not wr_id:
            return False, (
                f"id_format_version={fmt} requires explicit 'id' field "
                "(workspace-prefixed). Filename-derivation is forbidden."
            )
        if not ID_RE_V2.match(str(wr_id)):
            return False, (
                f"id '{wr_id}' does not match v2 pattern "
                "wr-<hq|skillhub|sentinel>-YYYY-MM-DD-NNN"
            )
        return True, "ok (v2)"
    # v1 legacy: id is optional but if present must match v1 or v2 pattern
    if wr_id and not (ID_RE_V1.match(str(wr_id)) or ID_RE_V2.match(str(wr_id))):
        return False, (
            f"id '{wr_id}' does not match v1 pattern wr-YYYY-MM-DD-NNN "
            "or v2 pattern wr-<workspace>-YYYY-MM-DD-NNN"
        )
    return True, "ok (v1 legacy)"


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def emit(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    }))


def read_recent_user_messages(transcript_path):
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    try:
        with open(transcript_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return []
    msgs = []
    for raw in reversed(lines):
        if len(msgs) >= TRANSCRIPT_USER_LOOKBACK:
            break
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if rec.get("type") == "user":
            content = rec.get("message", {}).get("content", "")
            if isinstance(content, list):
                content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
            msgs.append(str(content).lower())
    return msgs


def has_bypass_phrase(msgs):
    for m in msgs:
        for phrase in BYPASS_PHRASES:
            if phrase in m:
                return True
    return False


def looks_like_full_json_doc(s):
    """Heuristic: does this string look like it should parse as a complete
    JSON document?  Used to decide whether Edit's new_string should be
    validated as a full doc or treated as a partial fragment.
    """
    s = s.strip()
    if len(s) < 2:
        return False
    return (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]"))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return 0

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")
    if not file_path or not file_path.lower().endswith(".json"):
        return 0
    if not INBOX_PATH_RE.search(file_path):
        return 0

    transcript_path = data.get("transcript_path") or ""
    recent_msgs = read_recent_user_messages(transcript_path)
    if has_bypass_phrase(recent_msgs):
        return 0

    if tool_name == "Write":
        content = str(tool_input.get("content", "") or "")
        if not content.strip():
            return 0  # empty file -- let Write through, JSON parser will fail later if it's loaded
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            base = os.path.basename(file_path)
            reason = (
                f"BLOCKING: Write to inbox file `{base}` would create malformed "
                f"JSON.\n\n"
                f"Parser error: {e.msg} at line {e.lineno} column {e.colno} "
                f"(char {e.pos}).\n\n"
                "Common cause: literal Windows backslashes in path strings "
                'inside JSON (e.g. \"C:\\Users\\...\" emits as `C:\\Users\\...` '
                "after Write -- single backslash sequence is invalid JSON). "
                "Fix: use forward slashes in paths (`C:/Users/...`) OR "
                "construct the JSON via `json.dumps(payload, indent=2)` in "
                "a Python helper instead of hand-emitting via Write.\n\n"
                "To bypass for emergency manual repair, include 'skip "
                "json-validate' in your next user message.\n\n"
                "Source: wr-2026-04-25-005 (Sentinel, CRITICAL). HQ's routed-"
                "task writer emitted literal Windows backslashes that broke "
                "downstream close-inbox-item.py + auto-notification routing."
            )
            deny(reason)
            return 0

        # JSON parsed cleanly. Validate WR id schema (wr-2026-04-25-007).
        # Only applies when the parsed payload is a dict (lifecycle reviews,
        # WRs, RTs are all dict-shaped). Lists or other shapes pass through.
        if isinstance(parsed, dict):
            ok, reason = validate_wr_id_schema(parsed)
            if not ok:
                base = os.path.basename(file_path)
                deny(
                    f"BLOCKING: Write to inbox file `{base}` violates WR id "
                    f"schema. {reason}\n\n"
                    "Source: wr-2026-04-25-007 (workspace-prefixed id schema). "
                    "v2 ids eliminate cross-workspace NNN collisions and the "
                    "filename-derivation drift that caused 11 wrong-row "
                    "Supabase updates in the 2026-04-25 batch close.\n\n"
                    "To bypass for emergency manual repair, include 'skip "
                    "wr-id-schema' in your next user message."
                )
                sys.exit(2)
        return 0

    if tool_name == "Edit":
        new_string = str(tool_input.get("new_string", "") or "")
        # Only validate if new_string looks like a full JSON document; partial
        # fragments (e.g. patching a single field value) are allowed.
        if not looks_like_full_json_doc(new_string):
            return 0
        try:
            json.loads(new_string)
            return 0
        except json.JSONDecodeError as e:
            base = os.path.basename(file_path)
            # Soft warning rather than block, since Edit on a fragment is harder
            # to validate cleanly. The Write hook above is the primary safety net.
            emit(
                f"WARNING: Edit to inbox file `{base}` produces what looks like "
                f"a JSON document body but it does not parse: {e.msg} at line "
                f"{e.lineno} column {e.colno}. Verify before saving (the file "
                "may be loaded by close-inbox-item.py / audit scripts which will "
                "fail). Source: wr-2026-04-25-005."
            )
            return 0

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
