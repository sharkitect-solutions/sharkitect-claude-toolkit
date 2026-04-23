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
VALID_ASSET_TYPES = {"table", "script", "automation", "hook", "report", "workflow", "plugin"}


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

    row = {
        "asset_type": args.asset_type,
        "name": args.name,
        "owner_workspace": ws,
        "purpose": args.purpose,
        "location": args.location,
        "metadata": parse_metadata(args.metadata),
        "active": not args.inactive,
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
    params = {"select": "asset_type,name,owner_workspace,purpose,location,active,updated_at", "order": "asset_type.asc,name.asc"}
    if args.type:
        params["asset_type"] = f"eq.{args.type}"
    if args.workspace:
        params["owner_workspace"] = f"eq.{args.workspace}"
    if args.active_only:
        params["active"] = "eq.true"
    rows = sb_request("GET", "assets", params=params) or []
    if not rows:
        print("(no assets found)")
        return 0
    print(f"{'TYPE':<12} {'WORKSPACE':<22} {'NAME':<40} {'ACTIVE':<7} LOCATION")
    print("-" * 120)
    for r in rows:
        print(f"{r['asset_type']:<12} {r['owner_workspace']:<22} {r['name'][:40]:<40} {str(r['active']):<7} {(r.get('location') or '')[:60]}")
    print(f"\n{len(rows)} asset(s)")
    return 0


def cmd_exists(args):
    validate_type(args.asset_type)
    params = {
        "asset_type": f"eq.{args.asset_type}",
        "name": f"eq.{urllib.parse.quote(args.name, safe='')}",
        "select": "id,active",
    }
    if args.workspace:
        params["owner_workspace"] = f"eq.{args.workspace}"
    rows = sb_request("GET", "assets", params=params) or []
    if rows:
        active = rows[0].get("active")
        print(f"FOUND (active={active}): {rows[0]['id']}")
        return 0
    print("NOT FOUND")
    sys.exit(2)


def cmd_retire(args):
    validate_type(args.asset_type)
    validate_workspace(args.workspace)
    params = {
        "asset_type": f"eq.{args.asset_type}",
        "name": f"eq.{urllib.parse.quote(args.name, safe='')}",
        "owner_workspace": f"eq.{args.workspace}",
    }
    body = {"active": False, "last_updated_by": detect_workspace() or args.workspace}
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
    if args.inactive:
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
    reg.add_argument("--inactive", action="store_true")

    lst = sub.add_parser("list", help="List assets (filters optional)")
    lst.add_argument("--type", dest="type")
    lst.add_argument("--workspace")
    lst.add_argument("--active-only", action="store_true")

    ex = sub.add_parser("exists", help="Check if an asset is registered (exit 0 found / 2 not found)")
    ex.add_argument("asset_type")
    ex.add_argument("name")
    ex.add_argument("--workspace")

    ret = sub.add_parser("retire", help="Soft-delete (set active=false)")
    ret.add_argument("asset_type")
    ret.add_argument("name")
    ret.add_argument("--workspace", required=True)

    upd = sub.add_parser("update", help="Update fields on an existing asset")
    upd.add_argument("asset_type")
    upd.add_argument("name")
    upd.add_argument("--workspace", required=True)
    upd.add_argument("--purpose")
    upd.add_argument("--location")
    upd.add_argument("--metadata")
    upd.add_argument("--inactive", action="store_true")

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
