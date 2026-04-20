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


VALID_CLOSE_STATUSES = {"processed", "completed", "resolved", "rejected"}
PROHIBITED_AT_CLOSE = {
    "pending",
    "in_progress",
    "deferred",
    "new",
    "blocked",
    "awaiting_decision",
}


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
                    resolved_by: str) -> tuple[bool, str]:
    """
    Update cross_workspace_requests row in Supabase.
    Returns (success, message). Best-effort -- don't fail close on Supabase error.
    """
    # Prefer global env, then workspace .env
    env_paths = [Path.home() / ".claude" / ".env", Path.cwd() / ".env"]
    url = key = None
    for env_path in env_paths:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("SUPABASE_URL="):
                    url = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
            if url and key:
                break
    if not url or not key:
        return False, "Supabase credentials not found in .env"
    # Map our internal status terms to Supabase canonical 'completed'
    sb_status = "completed" if status in {"processed", "completed", "resolved"} else "rejected"
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
    resolution = {
        **existing_resolution,
        "resolved_date": now,
        "resolved_by": resolved_by,
        "fix_type": fix_type,
        "what_was_done": what_was_done,
        "artifacts_created": list(artifacts_created or []),
        "artifacts_modified": list(artifacts_modified or []),
        "verified": bool(verified),
        "move_reason": "completed" if status != "rejected" else "superseded",
    }
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
            ok, sb_msg = update_supabase(
                item_id=item_id,
                status=status,
                resolution_summary=what_was_done[:500],
                resolved_by=resolved_by,
            )
        else:
            sb_msg = "no item_id/request_id/task_id found in JSON"

    return {
        "ok": True,
        "final_path": str(dst),
        "previous_status": prev_status,
        "new_status": status,
        "supabase": sb_msg,
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
    args = p.parse_args()

    extra = {}
    if args.user_action_required:
        extra["user_action_required"] = args.user_action_required

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
        )
    except (ValueError, FileNotFoundError, FileExistsError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {result['message']}")
    print(f"  Path: {result['final_path']}")
    print(f"  Supabase: {result['supabase']}")
    sys.exit(0)


if __name__ == "__main__":
    main()
