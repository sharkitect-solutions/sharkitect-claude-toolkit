"""
notification-write-verify.py - PostToolUse verifier for Completion Notification Protocol

Fires after Bash invocations of close-inbox-item.py. Verifies that for
cross-workspace closures requiring a notification (per the protocol's skip
rules), a corresponding notification routed-task actually landed in the source
workspace's inbox. If not, emits strong corrective context with the exact
remediation command.

This is belt-and-suspenders enforcement layered ON TOP of the close script's
built-in auto-notification. Catches cases the script can't:
  - Old/cached version of close-inbox-item.py without notification logic
  - --no-notify passed with a thin/insufficient reason
  - Script wrote notification but the file vanished (race / disk full)
  - Caller invoked close logic via a different code path (manual file move)

Source: wr-2026-04-25-002 (Sentinel). The auto-write in close-inbox-item.py
is the primary mechanism; this hook is the verification gate.

DETECTION

Fires only when:
  - tool_name == 'Bash'
  - tool_input.command matches 'close-inbox-item.py'
  - The command parsed --file argument resolves to an item now in processed/
    (i.e., the close actually completed)

For each detected close:
  1. Locate the closed item under processed/ (derive from --file by replacing
     'inbox' segment with 'processed')
  2. Read the closed item JSON
  3. Apply the protocol's skip rules (kind=completion_notification, fyi,
     notify_on_completion=false, self-filed, etc.)
  4. If notification IS expected, verify it exists in the source workspace's
     inbox by scanning for a file matching the convention:
        rt-<YYYY-MM-DD>-<slug>-completed-by-<closer>.json
     OR a file containing completes_task_id == <closed item's id>
  5. If missing, emit corrective additionalContext.

GRACEFUL DEGRADATION

  - Cannot parse --file -> exit 0 silent
  - Closed item not yet in processed/ -> exit 0 silent (close may have failed)
  - Source workspace unresolvable -> exit 0 silent (script also skipped)
  - Notification present -> exit 0 silent (happy path)

Pure stdlib. Non-blocking (PostToolUse cannot deny). Always exits 0.

Input:  stdin JSON {tool_name, tool_input, tool_result}
Output: stdout JSON systemMessage (only when notification missing)
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path


# Mirrored from close-inbox-item.py (kept in sync; identical resolution map)
_WS_FALLBACK_DIR = Path.home() / "Documents" / "Claude Code Workspaces"
_WORKSPACE_DIR_FALLBACK = {
    "workforce-hq": _WS_FALLBACK_DIR / "1.- SHARKITECT DIGITAL WORKFORCE HQ",
    "skill-management-hub": _WS_FALLBACK_DIR / "3.- Skill Management Hub",
    "sentinel": _WS_FALLBACK_DIR / "4.- Sentinel",
}
_NOTIFICATION_KINDS = {"completion_notification", "fyi"}


def _resolve_workspace_dir(canonical_name):
    if not canonical_name:
        return None
    name = str(canonical_name).strip().lower()
    cfg = Path.home() / ".claude" / "config" / f"{name}-path.txt"
    if cfg.exists():
        try:
            p = Path(cfg.read_text(encoding="utf-8").strip())
            if p.is_dir():
                return p
        except OSError:
            pass
    p = _WORKSPACE_DIR_FALLBACK.get(name)
    if p and p.is_dir():
        return p
    return None


def _resolve_notify_inbox(canonical_name):
    name = str(canonical_name or "").strip().lower()
    workspace_dir = _resolve_workspace_dir(name)
    if not workspace_dir:
        return None
    if name == "skill-management-hub":
        target = workspace_dir / ".work-requests" / "inbox"
    else:
        target = workspace_dir / ".routed-tasks" / "inbox"
    return target if target.is_dir() else None


def _parse_close_command_args(command):
    """Extract --file, --resolved-by, --status, --no-notify from a close-inbox-item
    invocation. Returns dict (may have missing keys).
    """
    out = {}
    try:
        # shlex on Windows must use posix=False to handle backslashes in paths.
        # But our Bash hook runs through Git Bash where posix=True is correct.
        # Try posix first; fall back to non-posix if shlex fails.
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError:
            tokens = shlex.split(command, posix=False)
    except Exception:
        return out
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("--file", "-f") and i + 1 < len(tokens):
            out["file"] = tokens[i + 1]
            i += 2
            continue
        if t == "--resolved-by" and i + 1 < len(tokens):
            out["resolved_by"] = tokens[i + 1].strip().lower()
            i += 2
            continue
        if t == "--status" and i + 1 < len(tokens):
            out["status"] = tokens[i + 1].strip().lower()
            i += 2
            continue
        if t == "--no-notify":
            out["no_notify"] = True
            i += 1
            continue
        if t.startswith("--file="):
            out["file"] = t.split("=", 1)[1]
            i += 1
            continue
        if t.startswith("--resolved-by="):
            out["resolved_by"] = t.split("=", 1)[1].strip().lower()
            i += 1
            continue
        if t.startswith("--status="):
            out["status"] = t.split("=", 1)[1].strip().lower()
            i += 1
            continue
        i += 1
    return out


def _find_processed_path(file_arg):
    """Given the --file value (originally pointed at inbox/), return the path
    in processed/ where it should now live. The close script does a move from
    .../inbox/<name>.json to .../processed/<name>.json.
    """
    try:
        src = Path(file_arg)
    except (TypeError, ValueError):
        return None
    # If the path is already in processed/, return as-is
    parts = list(src.parts)
    for i, part in enumerate(parts):
        if part == "inbox":
            parts[i] = "processed"
            return Path(*parts)
        if part == "processed":
            return src
    return None


def _should_notify(closed_data, status, resolved_by):
    """Apply protocol skip rules. Returns (should_notify, reason).

    Mirrors close-inbox-item.py's maybe_write_notification logic so the
    verifier and the writer agree on what "expected" means.
    """
    kind = str(closed_data.get("kind", "")).lower()
    if kind in _NOTIFICATION_KINDS:
        return False, f"kind={kind}"
    if closed_data.get("notify_on_completion") is False:
        return False, "source set notify_on_completion=false"

    source_ws = (
        closed_data.get("routed_from")
        or closed_data.get("source_workspace")
        or closed_data.get("workspace")
    )
    if not source_ws:
        return False, "no source workspace identifiable"
    source_ws = str(source_ws).strip().lower()
    if source_ws == str(resolved_by).strip().lower():
        return False, "self-filed"

    # Non-completed close states default to skip unless source explicitly opted in
    if status in {"rejected", "superseded", "duplicate"} \
            and closed_data.get("notify_on_completion") is not True:
        return False, f"status={status} and source did not opt in"

    return True, "expected"


def _scan_for_notification(source_inbox, closed_id, resolved_by, hint=None):
    """Look in source workspace's inbox for a matching notification file.

    Match strategy (any one wins):
      A. notification_filename_hint exists verbatim
      B. file with completes_task_id == closed_id and routed_from == resolved_by
      C. filename contains the closed_id slug AND 'completed-by-{resolved_by}'

    Returns the matched Path, or None.
    """
    try:
        inbox = Path(source_inbox)
        if not inbox.is_dir():
            return None
    except (TypeError, ValueError):
        return None

    if hint:
        hint_name = hint if hint.endswith(".json") else f"{hint}.json"
        candidate = inbox / hint_name
        if candidate.exists():
            return candidate

    closed_id_str = str(closed_id or "").lower()
    resolved_str = str(resolved_by or "").lower()

    try:
        files = list(inbox.glob("rt-*.json"))
    except OSError:
        return None

    for f in files:
        # Filename signal
        name_lower = f.name.lower()
        if (closed_id_str and closed_id_str in name_lower
                and f"completed-by-{resolved_str}" in name_lower):
            return f
        # Body signal
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        body_completes = str(data.get("completes_task_id", "")).lower()
        body_routed_from = str(data.get("routed_from", "")).lower()
        if body_completes == closed_id_str and body_routed_from == resolved_str:
            return f
    return None


def emit_correction(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": text,
        }
    }))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    if data.get("tool_name") != "Bash":
        return 0
    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}
    command = str(tool_input.get("command", ""))
    if "close-inbox-item.py" not in command:
        return 0

    parsed = _parse_close_command_args(command)
    file_arg = parsed.get("file")
    resolved_by = parsed.get("resolved_by")
    status = parsed.get("status", "processed")
    if not file_arg or not resolved_by:
        return 0

    # The script may have been invoked with --no-notify. In that case the
    # script itself would have rejected without --no-notify-reason; we trust
    # the script's validation and don't double-check here.
    if parsed.get("no_notify"):
        return 0

    processed_path = _find_processed_path(file_arg)
    if processed_path is None or not processed_path.exists():
        # Close didn't actually complete; nothing to verify
        return 0

    try:
        closed_data = json.loads(processed_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(closed_data, dict):
        return 0

    expected, reason = _should_notify(closed_data, status, resolved_by)
    if not expected:
        return 0

    # Notification IS expected. Verify it landed.
    source_ws = (
        closed_data.get("routed_from")
        or closed_data.get("source_workspace")
        or closed_data.get("workspace")
    )
    if not source_ws:
        return 0
    source_ws = str(source_ws).strip().lower()

    # Prefer explicit notify_inbox_path from the closed item if valid
    source_inbox = None
    explicit = closed_data.get("notify_inbox_path")
    if explicit:
        try:
            p = Path(str(explicit))
            if p.is_dir():
                source_inbox = p
        except OSError:
            pass
    if source_inbox is None:
        source_inbox = _resolve_notify_inbox(source_ws)
    if source_inbox is None:
        # We can't verify if we can't find the source's inbox. Don't false-alarm.
        return 0

    closed_id = (closed_data.get("id")
                 or closed_data.get("request_id")
                 or closed_data.get("task_id"))
    hint = closed_data.get("notification_filename_hint")
    found = _scan_for_notification(source_inbox, closed_id, resolved_by, hint)
    if found is not None:
        return 0  # All good

    # Missing. Emit corrective system message with exact remediation.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    re_for_slug = re.compile(r"[^a-z0-9]+")
    id_slug = re_for_slug.sub("-", str(closed_id or "request").lower()).strip("-")[:60]
    suggested_filename = (
        f"rt-{today}-{id_slug}-completed-by-{resolved_by}.json"
    )
    suggested_path = source_inbox / suggested_filename

    correction = (
        "COMPLETION NOTIFICATION MISSING. The Completion Notification Protocol "
        f"(universal-protocols.md) requires a notification routed-task be "
        f"written to {source_ws}'s inbox after closing a cross-workspace item. "
        f"Closed item: {closed_id}. Source workspace: {source_ws}. Closed by: "
        f"{resolved_by}. Status: {status}.\n\n"
        f"No matching notification file was found in {source_inbox}. The close "
        "script's auto-notification likely failed silently or this script is an "
        "older version without the auto-write feature.\n\n"
        f"REMEDIATE NOW by writing a notification routed-task to "
        f"{suggested_path} using the schema at "
        "~/.claude/docs/templates/completion-notification-rt-template.json. "
        "Required fields: task_id, kind=completion_notification, "
        f"routed_from={resolved_by}, routed_to={source_ws}, "
        f"completes_task_id={closed_id}, what_was_done (copy of --what-was-done), "
        "verification_summary, what_originator_can_do_now, "
        "fix_instructions (acknowledge by closing), notify_on_completion=false."
    )
    emit_correction(correction)
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never block on internal errors
        pass
    sys.exit(0)
