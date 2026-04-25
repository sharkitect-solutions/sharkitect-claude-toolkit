"""
close-inbox-item.py -- Atomic inbox item closure helper for ALL workspaces

The single canonical mechanism for closing any inbox item (work request, routed
task, lifecycle review). Used by every workspace instead of ad-hoc python
json.dump + file move, which historically caused status-field drift (file moved
to processed/ but status stayed at "pending"/"in_progress"/"deferred").

Filed by: Sentinel wr-2026-04-19-002 (cross-workspace audit found 13+ records
with status-field drift across 3 workspaces). Root cause: no atomic
move-and-update mechanism existed. This script is the fix.

What it does (in order):
  1. Reads the inbox JSON file
  2. Validates: file is in an inbox/ directory, not already in processed/
  3. Sets top-level status to one of: processed | completed | resolved | rejected
  4. Writes/merges resolution object with required fields
  5. Appends an entry to status_history[]
  6. Moves the file from inbox/ to processed/ (atomic os.replace)
  7. Optionally updates Supabase cross_workspace_requests row

Usage (CLI):
    python ~/.claude/scripts/close-inbox-item.py \
        --file ".work-requests/inbox/2026-04-19_x.json" \
        --status processed \
        --resolved-by "skill-management-hub" \
        --what-was-done "Built X, deployed Y, verified Z" \
        --fix-type "hook" \
        [--artifacts-created "path1,path2"] \
        [--artifacts-modified "path1,path2"] \
        [--verified true] \
        [--no-supabase]

Usage (Python):
    from close_inbox_item import close_item
    close_item(
        file_path=".work-requests/inbox/foo.json",
        status="processed",
        resolved_by="skill-management-hub",
        what_was_done="...",
        fix_type="task",
    )

Allowed status values:
  - processed: Standard closure for completed work request / routed task
  - completed: Same semantic as processed (some workspaces prefer this term)
  - resolved:  Issue resolved, fix applied
  - rejected:  Reviewed and declined (with reason)

PROHIBITED: leaving status at pending | in_progress | deferred | new |
            awaiting_decision when moving to processed/

Dependencies: Python stdlib only.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


VALID_CLOSE_STATUSES = {"processed", "completed", "resolved", "rejected",
                         "superseded", "duplicate"}
# Statuses that REQUIRE a cross-reference to another inbox item_id.
# See universal-protocols.md "Superseded vs Duplicate" section.
CROSS_REF_REQUIRED = {
    "superseded": "superseded_by",  # id of the newer request that absorbed this
    "duplicate":  "duplicate_of",   # id of the surviving request
}
PROHIBITED_AT_CLOSE = {
    "pending",
    "in_progress",
    "deferred",
    "new",
    "blocked",
    "awaiting_decision",
}

# ---- Completion Notification Protocol (wr-2026-04-25-002) -------------------
# Canonical workspace -> .routed-tasks/inbox/ path. Resolution order:
#   1. ~/.claude/config/<workspace>-path.txt (explicit override)
#   2. Known Documents/Claude Code Workspaces/ paths
# Skill Hub does NOT have a .routed-tasks/inbox/. All inbound to Skill Hub
# goes through .work-requests/inbox/. We expose that path under the
# skill-management-hub key so notifications addressed to Skill Hub still
# land somewhere visible to its inbox processor.
_WS_FALLBACK_DIR = Path.home() / "Documents" / "Claude Code Workspaces"
_WORKSPACE_DIR_FALLBACK = {
    "workforce-hq": _WS_FALLBACK_DIR / "1.- SHARKITECT DIGITAL WORKFORCE HQ",
    "skill-management-hub": _WS_FALLBACK_DIR / "3.- Skill Management Hub",
    "sentinel": _WS_FALLBACK_DIR / "4.- Sentinel",
}

# kind values that MUST NOT generate a follow-up notification on close
# (would cause infinite ping-pong).
_NOTIFICATION_KINDS = {"completion_notification", "fyi"}


def _resolve_workspace_dir(canonical_name):
    """Return Path to a workspace's root directory, or None if unknown."""
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
    """Return Path to a workspace's notification destination dir.

    For HQ and Sentinel: <workspace>/.routed-tasks/inbox/
    For Skill Hub: <workspace>/.work-requests/inbox/ (no .routed-tasks/)

    Returns None if unresolvable. The caller must handle that case.
    """
    name = str(canonical_name or "").strip().lower()
    workspace_dir = _resolve_workspace_dir(name)
    if not workspace_dir:
        return None
    if name == "skill-management-hub":
        target = workspace_dir / ".work-requests" / "inbox"
    else:
        target = workspace_dir / ".routed-tasks" / "inbox"
    return target if target.is_dir() else None


def _slugify_for_filename(text, max_len=60):
    """Deterministic slug for notification filenames. ASCII-only, hyphenated."""
    import re
    if not text:
        return "unknown"
    s = str(text).strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if not s:
        return "unknown"
    return s[:max_len].rstrip("-") or "unknown"


def _detect_workspace_prefix(hint_path=None):
    """Infer workspace prefix from CWD or a hint path. Returns '' if unknown.
    Duplicated from <Skill Hub>/tools/load-env.py because ~/.claude/scripts/
    cannot reliably import from a specific workspace.
    """
    candidates = []
    if hint_path is not None:
        candidates.append(str(hint_path))
    candidates.append(os.getcwd())
    for raw in candidates:
        s = raw.replace("\\", "/").lower()
        if "skill management hub" in s or "/3.-" in s:
            return "SKILLHUB"
        if ("workforce" in s and "hq" in s) or "/1.-" in s:
            return "HQ"
        if "sentinel" in s or "/4.-" in s:
            return "SENTINEL"
    return ""


def _parse_env_file(path):
    """Minimal .env parser. Strips surrounding quotes. Skips blanks/comments."""
    out = {}
    if not path.exists():
        return out
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if val and val[0] not in ('"', "'"):
            hash_idx = val.find(" #")
            if hash_idx >= 0:
                val = val[:hash_idx].strip()
        val = val.strip('"').strip("'")
        if key:
            out[key] = val
    return out


def _load_env_value(key, hint_path=None):
    """Look up a credential using load-env.py resolution order:
        1. Workspace-local .env: KEY
        2. Global ~/.claude/.env: <PREFIX>_KEY
        3. Global ~/.claude/.env: KEY (unprefixed)
    Returns value or None.
    """
    local = _parse_env_file(Path.cwd() / ".env")
    if key in local and local[key]:
        return local[key]
    global_env = _parse_env_file(Path.home() / ".claude" / ".env")
    prefix = _detect_workspace_prefix(hint_path)
    if prefix:
        prefixed = f"{prefix}_{key}"
        if prefixed in global_env and global_env[prefixed]:
            return global_env[prefixed]
    if key in global_env and global_env[key]:
        return global_env[key]
    return None


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def find_processed_dir(inbox_path: Path) -> Path:
    """Given an inbox file path, return the matching processed/ directory."""
    parent = inbox_path.parent  # e.g. .work-requests/inbox
    if parent.name != "inbox":
        raise ValueError(
            f"File is not inside an inbox/ directory: {inbox_path}\n"
            f"Parent dir name is '{parent.name}', expected 'inbox'."
        )
    processed = parent.parent / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    return processed


def update_supabase(item_id: str, status: str, resolution_summary: str,
                    resolved_by: str, hint_path: Path | None = None) -> tuple[bool, str]:
    """
    Update cross_workspace_requests row in Supabase.
    Returns (success, message). Best-effort -- don't fail close on Supabase error.
    Uses workspace-prefix-aware env lookup (handles migrated ~/.claude/.env).
    """
    url = _load_env_value("SUPABASE_URL", hint_path)
    key = _load_env_value("SUPABASE_SERVICE_ROLE_KEY", hint_path)
    if not url or not key:
        return False, "Supabase credentials not found (checked local .env + ~/.claude/.env with workspace prefix)"
    # Map our internal status terms to Supabase canonical vocabulary.
    # Per universal-protocols.md "Status Vocabulary Layers":
    #   processed | completed | resolved  -> Supabase 'completed'
    #   rejected                           -> Supabase 'rejected'
    #   superseded                         -> Supabase 'superseded'
    #   duplicate                          -> Supabase 'duplicate'
    if status in {"processed", "completed", "resolved"}:
        sb_status = "completed"
    elif status in {"superseded", "duplicate"}:
        sb_status = status
    else:
        sb_status = "rejected"
    payload = json.dumps({
        "status": sb_status,
        "resolution_summary": resolution_summary[:1000],
        "resolved_by": resolved_by,
        "resolved_at": now_iso(),
        "last_updated_by": resolved_by,
        "updated_at": now_iso(),
    }).encode("utf-8")
    endpoint = f"{url}/rest/v1/cross_workspace_requests?item_id=eq.{item_id}"
    req = urllib.request.Request(
        endpoint,
        data=payload,
        method="PATCH",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if 200 <= resp.status < 300:
                return True, f"Supabase row {item_id} updated"
            return False, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTPError {e.code}: {e.reason}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def maybe_write_notification(
    closing_data,
    closing_path: Path,
    status: str,
    resolved_by: str,
    what_was_done: str,
    verification_summary: str = "",
    what_originator_can_do_now=None,
    notify_source: bool | None = None,
    no_notify_reason: str = "",
) -> tuple[str | None, str]:
    """Auto-write completion notification routed-task to source workspace.

    Returns (notification_path, message). notification_path is None if skipped.

    Skip conditions (any one is sufficient, evaluated in order):
      0. Caller passed notify_source=False (must include no_notify_reason)
      1. Closing item kind is in _NOTIFICATION_KINDS (notification or fyi)
      2. Source item explicitly set notify_on_completion=false
      3. Source workspace cannot be identified
      4. Source workspace == closing workspace (self-filed)
      5. Destination inbox cannot be resolved (workspace path missing)
      6. Status is rejected/superseded/duplicate AND originator did not
         explicitly opt in to notifications on those (these are not
         "completed" -- the originator may not want a "your work is done"
         message). For these, only notify if notify_on_completion=true was
         explicit in the source. Defaults to skip.
    """
    # Caller-side opt-out
    if notify_source is False:
        if not (no_notify_reason or "").strip():
            return None, ("ERROR: --no-notify requires --no-notify-reason "
                          "to prevent silent suppression")
        return None, f"skip: caller opted out -- reason: {no_notify_reason}"

    kind = str(closing_data.get("kind", "")).lower()
    if kind in _NOTIFICATION_KINDS:
        return None, f"skip: closing item kind={kind!r} (anti-ping-pong)"

    source_explicit_notify = closing_data.get("notify_on_completion")
    if source_explicit_notify is False:
        return None, "skip: source set notify_on_completion=false"

    # Identify source workspace from any of the standard fields.
    source_ws = (
        closing_data.get("routed_from")
        or closing_data.get("source_workspace")
        or closing_data.get("workspace")
    )
    if not source_ws:
        return None, "skip: no source workspace field on closing item"
    source_ws = str(source_ws).strip().lower()
    closer = str(resolved_by).strip().lower()
    if source_ws == closer:
        return None, f"skip: self-filed item (source==closer={source_ws})"

    # For non-completed close states, default to skip unless source explicitly
    # opted in. The originator probably doesn't want a "completed by X"
    # message about a request that was rejected, superseded, or marked
    # duplicate -- those have their own audit-trail discipline (resolution
    # cross-references). Skip unless they set notify_on_completion=true
    # explicitly.
    if status in {"rejected", "superseded", "duplicate"} \
            and source_explicit_notify is not True:
        return None, (f"skip: status={status} and source did not opt in "
                      "with notify_on_completion=true")

    # Resolve destination inbox. Prefer the explicit notify_inbox_path if
    # provided AND it exists; fall back to canonical lookup.
    dest_inbox = None
    explicit_path = closing_data.get("notify_inbox_path")
    if explicit_path:
        try:
            p = Path(str(explicit_path))
            if p.is_dir():
                dest_inbox = p
        except OSError:
            pass
    if dest_inbox is None:
        dest_inbox = _resolve_notify_inbox(source_ws)
    if dest_inbox is None:
        return None, (f"skip: cannot resolve inbox for {source_ws} "
                      "(no config file, no fallback path matched)")

    # Build filename. Use the originator's hint if provided.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    item_id = (closing_data.get("id")
               or closing_data.get("request_id")
               or closing_data.get("task_id")
               or "unknown")
    hint = closing_data.get("notification_filename_hint")
    if hint:
        notif_filename = str(hint)
        if not notif_filename.endswith(".json"):
            notif_filename += ".json"
    else:
        slug = _slugify_for_filename(item_id, 60)
        notif_filename = f"rt-{today}-{slug}-completed-by-{closer}.json"

    notif_path = dest_inbox / notif_filename

    # Compose notification body
    notification = {
        "task_id": notif_filename[:-5] if notif_filename.endswith(".json") else notif_filename,
        "kind": "completion_notification",
        "routed_from": closer,
        "routed_to": source_ws,
        "routed_date": today,
        "priority": "low",
        "status": "pending",
        "completes_task_id": item_id,
        "completes_task_status": status,
        "what_was_done": what_was_done,
        "verification_summary": verification_summary or "",
        "what_originator_can_do_now": list(what_originator_can_do_now or []),
        "context": (
            f"Completion notification for {item_id} (originally filed by "
            f"{source_ws}, completed by {closer})."
        ),
        "fix_instructions": (
            "Acknowledge this notification by closing it via "
            "close-inbox-item.py with --status processed. Optionally take "
            "the downstream actions listed in what_originator_can_do_now "
            "before closing."
        ),
        "notify_on_completion": False,
        "source_protocol": "Completion Notification Protocol",
        "source_protocol_doc": "~/.claude/rules/universal-protocols.md",
    }

    # Atomic exclusive create (avoid clobbering an existing notification)
    try:
        fd = os.open(str(notif_path),
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return None, f"skip: notification already exists at {notif_path}"
    except OSError as e:
        return None, f"error: cannot create notification: {e}"
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(notification, indent=2))
    except OSError as e:
        return None, f"error: write failed: {e}"

    return str(notif_path), f"notification written to {source_ws}: {notif_path.name}"


def close_item(
    file_path,
    status: str,
    resolved_by: str,
    what_was_done: str,
    fix_type: str = "task",
    artifacts_created=None,
    artifacts_modified=None,
    verified: bool = True,
    update_supabase_row: bool = True,
    extra_resolution=None,
    superseded_by: str = "",
    duplicate_of: str = "",
    notify_source: bool | None = None,
    no_notify_reason: str = "",
    verification_summary: str = "",
    what_originator_can_do_now=None,
) -> dict:
    """
    Atomically close an inbox item.

    Returns dict with: ok (bool), final_path (str), supabase (str), message (str).
    Raises ValueError on validation failure (status, resolution content, etc).
    """
    src = Path(file_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"Inbox file not found: {src}")
    if status not in VALID_CLOSE_STATUSES:
        raise ValueError(
            f"Invalid close status '{status}'. "
            f"Must be one of: {sorted(VALID_CLOSE_STATUSES)}"
        )
    # Enforce cross-reference requirement for superseded / duplicate closures
    # per universal-protocols.md "Superseded vs Duplicate" rule. These
    # statuses exist specifically to preserve the audit trail linking this
    # closed request to the one that absorbed or surviving-duplicated it.
    if status == "superseded" and not (superseded_by or "").strip():
        raise ValueError(
            "status=superseded requires --superseded-by <item_id> naming the "
            "newer request that absorbed this work (e.g. wr-2026-04-23-005). "
            "Without this, the audit trail is broken and the close is "
            "indistinguishable from a drift-correction."
        )
    if status == "duplicate" and not (duplicate_of or "").strip():
        raise ValueError(
            "status=duplicate requires --duplicate-of <item_id> naming the "
            "surviving request (usually older or better-scoped). Without "
            "this, the close is indistinguishable from rejected-on-merits."
        )
    if not what_was_done or len(what_was_done.strip()) < 10:
        raise ValueError(
            "what_was_done must describe ACTUAL work completed (>=10 chars). "
            "Vague phrases like 'acknowledged', 'deferred', 'logged' are NOT valid."
        )
    lower = what_was_done.strip().lower()
    if lower.startswith(("acknowledged", "deferred", "logged", "noted")):
        raise ValueError(
            f"what_was_done starts with '{lower.split()[0]}' which is not real work. "
            "Closing with this would create a fake-completion record. "
            "Either describe the actual work or leave the item in inbox."
        )

    processed_dir = find_processed_dir(src)
    dst = processed_dir / src.name
    if dst.exists():
        raise FileExistsError(f"Already exists in processed/: {dst}")

    # Read, mutate, write
    data = json.loads(src.read_text(encoding="utf-8"))
    now = now_iso()
    prev_status = data.get("status", "unknown")

    # 1. Set top-level status
    data["status"] = status
    data["processed_date"] = now

    # 2. Build/merge resolution object
    existing_resolution = data.get("resolution", {})
    # move_reason field records the SEMANTIC reason we're closing, not the
    # raw status. Mapping:
    #   processed / completed / resolved -> "completed"
    #   rejected                         -> "rejected"
    #   superseded                       -> "superseded"
    #   duplicate                        -> "duplicate"
    move_reason_map = {
        "processed": "completed",
        "completed": "completed",
        "resolved": "completed",
        "rejected": "rejected",
        "superseded": "superseded",
        "duplicate": "duplicate",
    }
    resolution = {
        **existing_resolution,
        "resolved_date": now,
        "resolved_by": resolved_by,
        "fix_type": fix_type,
        "what_was_done": what_was_done,
        "artifacts_created": list(artifacts_created or []),
        "artifacts_modified": list(artifacts_modified or []),
        "verified": bool(verified),
        "move_reason": move_reason_map.get(status, status),
    }
    # Attach cross-reference for superseded / duplicate per the rule
    if status == "superseded" and superseded_by:
        resolution["superseded_by"] = superseded_by.strip()
    if status == "duplicate" and duplicate_of:
        resolution["duplicate_of"] = duplicate_of.strip()
    if extra_resolution:
        resolution.update(extra_resolution)
    data["resolution"] = resolution

    # 3. Append status history entry
    history = data.get("status_history", [])
    history.append({
        "timestamp": now,
        "from_status": prev_status,
        "to_status": status,
        "actor": resolved_by,
        "trigger": "close-inbox-item.py",
    })
    data["status_history"] = history

    # Write to a tmp file in same dir, then atomic rename to dst
    tmp = src.with_suffix(src.suffix + ".closing")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, dst)
    src.unlink()

    # 4. Best-effort Supabase update
    sb_msg = "skipped"
    if update_supabase_row:
        item_id = data.get("id") or data.get("request_id") or data.get("task_id")
        if item_id:
            _ok, sb_msg = update_supabase(
                item_id=item_id,
                status=status,
                resolution_summary=what_was_done[:500],
                resolved_by=resolved_by,
                hint_path=src,
            )
        else:
            sb_msg = "no item_id/request_id/task_id found in JSON"

    # 5. Completion Notification Protocol -- auto-write notification routed-task
    # to the source workspace's inbox unless the close is exempt (self-filed,
    # source set notify_on_completion=false, kind=completion_notification, or
    # caller passed notify_source=False with a reason).
    notify_path, notify_msg = maybe_write_notification(
        closing_data=data,
        closing_path=src,
        status=status,
        resolved_by=resolved_by,
        what_was_done=what_was_done,
        verification_summary=verification_summary,
        what_originator_can_do_now=what_originator_can_do_now,
        notify_source=notify_source,
        no_notify_reason=no_notify_reason,
    )

    return {
        "ok": True,
        "final_path": str(dst),
        "previous_status": prev_status,
        "new_status": status,
        "supabase": sb_msg,
        "notification_path": notify_path,
        "notification_msg": notify_msg,
        "message": f"Closed {src.name}: {prev_status} -> {status}",
    }


def main():
    p = argparse.ArgumentParser(
        description="Atomically close an inbox item (work request / routed task / lifecycle review).",
        epilog="See module docstring for full protocol description.",
    )
    p.add_argument("--file", required=True, help="Path to inbox JSON file to close")
    p.add_argument("--status", default="processed",
                   choices=sorted(VALID_CLOSE_STATUSES),
                   help="New status (default: processed)")
    p.add_argument("--resolved-by", required=True,
                   help="Workspace canonical name (e.g. skill-management-hub)")
    p.add_argument("--what-was-done", required=True,
                   help="Description of actual work completed (>=10 chars, NOT 'acknowledged')")
    p.add_argument("--fix-type", default="task",
                   help="Fix category: task, hook, skill, agent, bug, protocol, etc.")
    p.add_argument("--artifacts-created", default="",
                   help="Comma-separated paths created")
    p.add_argument("--artifacts-modified", default="",
                   help="Comma-separated paths modified")
    p.add_argument("--verified", default="true",
                   help="true|false -- whether resolution was verified")
    p.add_argument("--no-supabase", action="store_true",
                   help="Skip Supabase row update")
    p.add_argument("--user-action-required", default="",
                   help="If set, included in resolution as user_action_required field")
    p.add_argument("--superseded-by", default="",
                   help="Required when --status=superseded. Item id of the newer "
                        "request that absorbed this work (e.g. wr-2026-04-23-005).")
    p.add_argument("--duplicate-of", default="",
                   help="Required when --status=duplicate. Item id of the "
                        "surviving request (usually older or better-scoped).")
    # Completion Notification Protocol args (wr-2026-04-25-002).
    p.add_argument("--no-notify", action="store_true",
                   help="Suppress the auto-completion-notification routed-task "
                        "that would otherwise be written to the source "
                        "workspace's inbox. Requires --no-notify-reason. "
                        "Reserved for: closing a kind=completion_notification "
                        "item, self-filed items, or test runs.")
    p.add_argument("--no-notify-reason", default="",
                   help="Required with --no-notify. Plain-text justification "
                        "for skipping the notification. Recorded for audit.")
    p.add_argument("--verification-summary", default="",
                   help="One- or two-line summary of how the work was "
                        "verified. Included in the completion-notification.")
    p.add_argument("--what-originator-can-do-now", default="",
                   help="Pipe-separated list of next actions the originator "
                        "can take now that this work is done (e.g. 'flip "
                        "AUTOFIX_V2_MODE=on|update project status to verified').")
    args = p.parse_args()

    extra = {}
    if args.user_action_required:
        extra["user_action_required"] = args.user_action_required

    # Resolve notify_source from CLI flags. None = auto (notify if eligible).
    notify_source_arg = False if args.no_notify else None
    if args.no_notify and not args.no_notify_reason.strip():
        print("ERROR: --no-notify requires --no-notify-reason '<text>' to "
              "prevent silent notification suppression.", file=sys.stderr)
        sys.exit(1)
    next_actions = [s.strip() for s in args.what_originator_can_do_now.split("|")
                    if s.strip()]

    try:
        result = close_item(
            file_path=args.file,
            status=args.status,
            resolved_by=args.resolved_by,
            what_was_done=args.what_was_done,
            fix_type=args.fix_type,
            artifacts_created=[s.strip() for s in args.artifacts_created.split(",") if s.strip()],
            artifacts_modified=[s.strip() for s in args.artifacts_modified.split(",") if s.strip()],
            verified=args.verified.lower() == "true",
            update_supabase_row=not args.no_supabase,
            extra_resolution=extra or None,
            superseded_by=args.superseded_by,
            duplicate_of=args.duplicate_of,
            notify_source=notify_source_arg,
            no_notify_reason=args.no_notify_reason,
            verification_summary=args.verification_summary,
            what_originator_can_do_now=next_actions,
        )
    except (ValueError, FileNotFoundError, FileExistsError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {result['message']}")
    print(f"  Path: {result['final_path']}")
    print(f"  Supabase: {result['supabase']}")
    print(f"  Notification: {result['notification_msg']}")
    if result.get("notification_path"):
        print(f"    -> {result['notification_path']}")
    sys.exit(0)


if __name__ == "__main__":
    main()
