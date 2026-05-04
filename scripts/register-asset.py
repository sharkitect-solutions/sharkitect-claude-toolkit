"""
register-asset.py -- Universal helper for the Operational Asset Registry

Any workspace can use this to register, update, query, or retire assets in the
Supabase `assets` table. Upserts by (asset_type, name, owner_workspace).

Asset types:
  table       - Supabase table
  script      - Python/shell script or CLI tool
  automation  - Scheduled job (n8n, Task Scheduler, CronCreate)
  hook        - Claude Code hook (SessionStart, PostToolUse, etc.)
  report      - Scheduled brief or report output
  workflow    - Markdown SOP
  plugin      - Claude Code plugin
  document    - KB markdown / blueprint / persistent reference doc that
                doesn't fit workflow/SOP shape (n8n workflow blueprints,
                technical-reference docs, audit reports, etc.)
  blueprint   - Synonym for document, accepted for clarity when registering
                workflow blueprints / architecture diagrams as standalone
                reference assets.

Usage:
    register-asset.py register <type> <name> [options]
    register-asset.py list [--type TYPE] [--workspace WS] [--active-only]
    register-asset.py exists <type> <name> [--workspace WS]
    register-asset.py retire <type> <name> --workspace WS
    register-asset.py update <type> <name> --workspace WS [options]

Options for register/update:
    --workspace WS          Owner workspace (canonical name; required)
    --purpose TEXT          One-line description
    --location PATH         Filesystem path, URL, or identifier
    --metadata JSON         JSON blob of type-specific fields
    --inactive              Mark as inactive on register (soft-delete init)

Exit: 0 on success, 1 on error, 2 on "already exists" for register without --force.

Dependencies: Python stdlib only (urllib, json, argparse)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CANONICAL_WORKSPACES = {"workforce-hq", "skill-management-hub", "sentinel", "global"}
VALID_ASSET_TYPES = {"table", "script", "automation", "hook", "report", "workflow", "plugin", "document", "blueprint"}

# Asset lifecycle status (Sentinel migration 2026-05-04, Phase 1 of Option B).
# Source: wr-sentinel-2026-05-04-006. The legacy `active` boolean is being
# consolidated into a single `status` column with richer state. Phase 2 of the
# migration will DROP COLUMN active; this script writes BOTH during the
# transition to remain compatible with consumers that still read `active`.
VALID_ASSET_STATUSES = {"active", "paused", "deactivated", "deprecated"}
NON_ACTIVE_STATUSES = {"paused", "deactivated", "deprecated"}

# Silent Execution Protocol (universal-protocols.md, NON-NEGOTIABLE).
# Source: wr-sentinel-2026-04-30-003. Every registered automation must declare
# its silent-execution mechanism so visible-window tasks cannot enter the
# registry undetected. The audit-autonomous-systems.py 'visible_window_automation'
# drift class verifies live runtime against the declared mechanism.
VALID_SILENT_MECHANISMS = {
    "pythonw",                # pythonw.exe instead of python.exe
    "vbs-wrapper",            # WshShell.Run windowStyle=0 wrapper
    "task-scheduler-hidden",  # /RL HIGHEST + hidden-task XML attribute
    "cron-equivalent",        # POSIX cron / launchd / systemd timer (always silent)
    "n8n-cloud",              # n8n cloud workflows (run in cloud, no local window)
    "other",                  # explicit escape hatch; must be justified in --purpose
}


def _detect_workspace_prefix():
    """Infer workspace prefix from CWD. Returns '' if unknown.
    Mirrors <Skill Hub>/tools/load-env.py. Duplicated because ~/.claude/scripts/
    cannot reliably import from a specific workspace.
    """
    s = os.getcwd().replace("\\", "/").lower()
    if "skill management hub" in s or "/3.-" in s:
        return "SKILLHUB"
    if ("workforce" in s and "hq" in s) or "/1.-" in s:
        return "HQ"
    if "sentinel" in s or "/4.-" in s:
        return "SENTINEL"
    return ""


def _parse_env(path):
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k:
            out[k] = v
    return out


def load_env():
    """Load credentials from local .env + global ~/.claude/.env with
    workspace-prefix fallback (e.g. SKILLHUB_SUPABASE_URL -> SUPABASE_URL).
    """
    # Layer 1: walk up from CWD for workspace-local .env
    here = Path.cwd()
    for _ in range(5):
        env = here / ".env"
        if env.exists():
            for k, v in _parse_env(env).items():
                os.environ.setdefault(k, v)
            break
        if here.parent == here:
            break
        here = here.parent

    # Layer 2: global ~/.claude/.env with workspace prefix resolution
    global_env = _parse_env(Path.home() / ".claude" / ".env")
    if not global_env:
        return
    prefix = _detect_workspace_prefix()
    if prefix:
        plen = len(prefix) + 1
        for k, v in global_env.items():
            if k.startswith(f"{prefix}_"):
                os.environ.setdefault(k[plen:], v)
                os.environ.setdefault(k, v)
    for k, v in global_env.items():
        if not any(k.startswith(f"{p}_") for p in ("SKILLHUB", "HQ", "SENTINEL")):
            os.environ.setdefault(k, v)


def sb_config():
    load_env()
    return (
        os.environ.get("SUPABASE_URL", "").rstrip("/"),
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""),
    )


def sb_headers(prefer=None):
    _, key = sb_config()
    h = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def sb_request(method, path, params=None, body=None, prefer=None):
    base, key = sb_config()
    if not base or not key:
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set in .env", file=sys.stderr)
        sys.exit(1)
    qs = f"?{urllib.parse.urlencode(params, safe='.,()*%')}" if params else ""
    url = f"{base}/rest/v1/{path}{qs}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=sb_headers(prefer))
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR {method} {path}: HTTP {e.code} -- {body}", file=sys.stderr)
        return None
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"ERROR {method} {path}: {e}", file=sys.stderr)
        return None


def detect_workspace():
    """Best-effort workspace detection from CWD."""
    cwd = str(Path.cwd()).lower().replace("\\", "/")
    if "skill management" in cwd or "skill-management" in cwd:
        return "skill-management-hub"
    if "workforce" in cwd:
        return "workforce-hq"
    if "sentinel" in cwd:
        return "sentinel"
    return None


def validate_workspace(ws):
    if ws not in CANONICAL_WORKSPACES:
        print(f"ERROR: workspace must be one of {sorted(CANONICAL_WORKSPACES)}, got '{ws}'", file=sys.stderr)
        sys.exit(1)


def validate_type(t):
    if t not in VALID_ASSET_TYPES:
        print(f"ERROR: asset_type must be one of {sorted(VALID_ASSET_TYPES)}, got '{t}'", file=sys.stderr)
        sys.exit(1)


def parse_metadata(raw):
    if not raw:
        return {}
    try:
        v = json.loads(raw)
        if not isinstance(v, dict):
            raise ValueError("metadata must be a JSON object")
        return v
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: invalid --metadata JSON: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_register(args):
    validate_type(args.asset_type)
    ws = args.workspace or detect_workspace()
    if not ws:
        print("ERROR: --workspace required (could not auto-detect)", file=sys.stderr)
        sys.exit(1)
    validate_workspace(ws)

    metadata = parse_metadata(args.metadata)

    # Silent Execution Protocol enforcement (NON-NEGOTIABLE for automation type).
    # Source: wr-sentinel-2026-04-30-003. Automations must declare their silent
    # mechanism at registration time so visible-window tasks are caught.
    silent = getattr(args, "silent", None)
    if args.asset_type == "automation":
        if not silent:
            print(
                "ERROR: --silent is required when registering an automation.\n"
                "Silent Execution Protocol (universal-protocols.md, NON-NEGOTIABLE):\n"
                "  every automation must declare its silent-execution mechanism.\n"
                "  Valid values: " + ", ".join(sorted(VALID_SILENT_MECHANISMS)) + "\n"
                "Example: --silent pythonw   (Python entry point via pythonw.exe)\n"
                "         --silent vbs-wrapper   (WshShell.Run windowStyle=0)\n"
                "         --silent task-scheduler-hidden   (XML hidden-task attribute)\n"
                "         --silent cron-equivalent   (POSIX cron/launchd/systemd)\n"
                "         --silent n8n-cloud   (cloud-hosted, no local window)\n"
                "         --silent other   (escape hatch; justify in --purpose)",
                file=sys.stderr,
            )
            sys.exit(1)
        if silent not in VALID_SILENT_MECHANISMS:
            print(
                f"ERROR: invalid --silent value '{silent}'. Must be one of: "
                + ", ".join(sorted(VALID_SILENT_MECHANISMS))
                + " (Silent Execution Protocol, universal-protocols.md).",
                file=sys.stderr,
            )
            sys.exit(1)
        # Stamp the declared mechanism into metadata for downstream audit
        metadata["silent_mechanism"] = silent
    elif silent:
        # --silent on non-automation types is harmless but worth noting
        print(
            f"NOTE: --silent ignored on asset_type={args.asset_type} (only "
            "applies to automation). Stored in metadata for reference.",
            file=sys.stderr,
        )
        metadata["silent_mechanism"] = silent

    # Resolve status (per wr-sentinel-2026-05-04-006). --status is the new
    # canonical input. --inactive is preserved for back-compat and maps to
    # status=deactivated.
    status = getattr(args, "status", None) or "active"
    if args.inactive and status == "active":
        status = "deactivated"
    if status not in VALID_ASSET_STATUSES:
        print(
            f"ERROR: invalid --status '{status}'. Must be one of: "
            + ", ".join(sorted(VALID_ASSET_STATUSES)),
            file=sys.stderr,
        )
        sys.exit(1)
    status_reason = getattr(args, "status_reason", None)
    if status in NON_ACTIVE_STATUSES and not status_reason:
        print(
            f"ERROR: --status-reason is required when --status={status}.\n"
            "Non-active states must carry a one-line reason for audit + drift surfacing.",
            file=sys.stderr,
        )
        sys.exit(1)

    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    row = {
        "asset_type": args.asset_type,
        "name": args.name,
        "owner_workspace": ws,
        "purpose": args.purpose,
        "location": args.location,
        "metadata": metadata,
        "status": status,
        "status_reason": status_reason,
        "status_changed_at": now_iso,
        # Back-compat boolean (Phase 2 will DROP COLUMN active)
        "active": status == "active",
        "last_updated_by": detect_workspace() or ws,
    }
    # Upsert on the unique key
    result = sb_request(
        "POST", "assets",
        params={"on_conflict": "asset_type,name,owner_workspace"},
        body=row,
        prefer="resolution=merge-duplicates,return=representation",
    )
    if result is None:
        sys.exit(1)
    print(f"OK: registered {args.asset_type}/{args.name} ({ws})")
    return 0


def cmd_list(args):
    params = {
        "select": "asset_type,name,owner_workspace,purpose,location,status,status_reason,active,updated_at",
        "order": "asset_type.asc,name.asc",
    }
    if args.type:
        params["asset_type"] = f"eq.{args.type}"
    if args.workspace:
        params["owner_workspace"] = f"eq.{args.workspace}"
    if args.active_only:
        # Prefer status column (canonical post-migration); fall back implicit
        # by also including back-compat active=true for transitional rows.
        params["status"] = "eq.active"
    rows = sb_request("GET", "assets", params=params) or []
    if not rows:
        print("(no assets found)")
        return 0
    print(f"{'TYPE':<12} {'WORKSPACE':<22} {'NAME':<40} {'STATUS':<13} LOCATION")
    print("-" * 120)
    for r in rows:
        # Read status preferentially; fall back to active boolean for rows
        # that haven't been migrated yet (defensive).
        status_val = r.get("status") or ("active" if r.get("active") else "deactivated")
        print(
            f"{r['asset_type']:<12} {r['owner_workspace']:<22} "
            f"{r['name'][:40]:<40} {status_val:<13} {(r.get('location') or '')[:60]}"
        )
    print(f"\n{len(rows)} asset(s)")
    return 0


def cmd_exists(args):
    validate_type(args.asset_type)
    params = {
        "asset_type": f"eq.{args.asset_type}",
        "name": f"eq.{urllib.parse.quote(args.name, safe='')}",
        "select": "id,status,active",
    }
    if args.workspace:
        params["owner_workspace"] = f"eq.{args.workspace}"
    rows = sb_request("GET", "assets", params=params) or []
    if rows:
        status_val = rows[0].get("status") or ("active" if rows[0].get("active") else "deactivated")
        print(f"FOUND (status={status_val}): {rows[0]['id']}")
        return 0
    print("NOT FOUND")
    sys.exit(2)


def cmd_retire(args):
    """Retire = set status=deactivated. --reason is required (audit trail)."""
    validate_type(args.asset_type)
    validate_workspace(args.workspace)
    if not getattr(args, "reason", None):
        print(
            "ERROR: --reason is required when retiring an asset.\n"
            "Retire sets status=deactivated; the reason is persisted to "
            "status_reason for audit and drift surfacing.",
            file=sys.stderr,
        )
        sys.exit(1)
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    params = {
        "asset_type": f"eq.{args.asset_type}",
        "name": f"eq.{urllib.parse.quote(args.name, safe='')}",
        "owner_workspace": f"eq.{args.workspace}",
    }
    body = {
        "status": "deactivated",
        "status_reason": args.reason,
        "status_changed_at": now_iso,
        "active": False,  # back-compat
        "last_updated_by": detect_workspace() or args.workspace,
    }
    result = sb_request("PATCH", "assets", params=params, body=body, prefer="return=representation")
    if result is None:
        sys.exit(1)
    if not result:
        print(f"ERROR: no row matches {args.asset_type}/{args.name}/{args.workspace}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: retired {args.asset_type}/{args.name} ({args.workspace})")
    return 0


def cmd_update(args):
    validate_type(args.asset_type)
    validate_workspace(args.workspace)
    params = {
        "asset_type": f"eq.{args.asset_type}",
        "name": f"eq.{urllib.parse.quote(args.name, safe='')}",
        "owner_workspace": f"eq.{args.workspace}",
    }
    patch = {"last_updated_by": detect_workspace() or args.workspace}
    if args.purpose is not None:
        patch["purpose"] = args.purpose
    if args.location is not None:
        patch["location"] = args.location
    if args.metadata is not None:
        patch["metadata"] = parse_metadata(args.metadata)

    # Status update path (preferred). --status takes precedence over --inactive.
    new_status = getattr(args, "status", None)
    new_reason = getattr(args, "status_reason", None)
    if new_status:
        if new_status not in VALID_ASSET_STATUSES:
            print(
                f"ERROR: invalid --status '{new_status}'. Must be one of: "
                + ", ".join(sorted(VALID_ASSET_STATUSES)),
                file=sys.stderr,
            )
            sys.exit(1)
        if new_status in NON_ACTIVE_STATUSES and not new_reason:
            print(
                f"ERROR: --status-reason is required when transitioning to {new_status}.",
                file=sys.stderr,
            )
            sys.exit(1)
        from datetime import datetime, timezone
        patch["status"] = new_status
        patch["status_reason"] = new_reason
        patch["status_changed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        patch["active"] = new_status == "active"
    elif args.inactive:
        # Legacy path: --inactive maps to status=deactivated (requires reason)
        if not new_reason:
            print(
                "ERROR: --status-reason is required when using --inactive (maps to status=deactivated).",
                file=sys.stderr,
            )
            sys.exit(1)
        from datetime import datetime, timezone
        patch["status"] = "deactivated"
        patch["status_reason"] = new_reason
        patch["status_changed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        patch["active"] = False

    result = sb_request("PATCH", "assets", params=params, body=patch, prefer="return=representation")
    if result is None:
        sys.exit(1)
    if not result:
        print(f"ERROR: no row matches {args.asset_type}/{args.name}/{args.workspace}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: updated {args.asset_type}/{args.name} ({args.workspace})")
    return 0


def build_parser():
    p = argparse.ArgumentParser(description="Operational Asset Registry helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    reg = sub.add_parser("register", help="Register or upsert an asset")
    reg.add_argument("asset_type")
    reg.add_argument("name")
    reg.add_argument("--workspace")
    reg.add_argument("--purpose")
    reg.add_argument("--location")
    reg.add_argument("--metadata")
    reg.add_argument(
        "--status",
        choices=sorted(VALID_ASSET_STATUSES),
        default=None,
        help="Asset lifecycle status (default: active). One of: "
             + ", ".join(sorted(VALID_ASSET_STATUSES))
             + ". Required: --status-reason when status != active.",
    )
    reg.add_argument(
        "--status-reason",
        dest="status_reason",
        help="Required when --status is paused/deactivated/deprecated. "
             "Persisted to status_reason for audit + drift surfacing.",
    )
    reg.add_argument(
        "--inactive",
        action="store_true",
        help="DEPRECATED: maps to --status=deactivated. Use --status instead.",
    )
    reg.add_argument(
        "--silent",
        help=(
            "Silent-execution mechanism (REQUIRED for asset_type=automation). "
            "Valid: pythonw | vbs-wrapper | task-scheduler-hidden | "
            "cron-equivalent | n8n-cloud | other. Source: Silent Execution "
            "Protocol, universal-protocols.md (NON-NEGOTIABLE)."
        ),
    )

    lst = sub.add_parser("list", help="List assets (filters optional)")
    lst.add_argument("--type", dest="type")
    lst.add_argument("--workspace")
    lst.add_argument("--active-only", action="store_true")

    ex = sub.add_parser("exists", help="Check if an asset is registered (exit 0 found / 2 not found)")
    ex.add_argument("asset_type")
    ex.add_argument("name")
    ex.add_argument("--workspace")

    ret = sub.add_parser("retire", help="Retire (set status=deactivated). --reason required.")
    ret.add_argument("asset_type")
    ret.add_argument("name")
    ret.add_argument("--workspace", required=True)
    ret.add_argument(
        "--reason",
        required=True,
        help="REQUIRED: one-line audit trail for retirement (persisted to status_reason).",
    )

    upd = sub.add_parser("update", help="Update fields on an existing asset")
    upd.add_argument("asset_type")
    upd.add_argument("name")
    upd.add_argument("--workspace", required=True)
    upd.add_argument("--purpose")
    upd.add_argument("--location")
    upd.add_argument("--metadata")
    upd.add_argument(
        "--status",
        choices=sorted(VALID_ASSET_STATUSES),
        default=None,
        help="Transition asset to a new lifecycle status. Required: --status-reason for non-active states.",
    )
    upd.add_argument(
        "--status-reason",
        dest="status_reason",
        help="Required when --status or --inactive transitions to a non-active state.",
    )
    upd.add_argument(
        "--inactive",
        action="store_true",
        help="DEPRECATED: use --status=deactivated --status-reason '<text>' instead.",
    )

    return p


def main():
    args = build_parser().parse_args()
    return {
        "register": cmd_register,
        "list": cmd_list,
        "exists": cmd_exists,
        "retire": cmd_retire,
        "update": cmd_update,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
