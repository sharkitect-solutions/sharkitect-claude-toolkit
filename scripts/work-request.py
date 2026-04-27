"""
work-request.py -- Universal work request script for ALL workspaces

Any workspace agent can call this script to send a work request to the
Skill Management Hub's unified inbox. Covers capability gaps (MISSING,
UNUSED, FALLBACK), operational tasks (TASK), bug fixes (BUG), and
enhancements (ENHANCE).

Replaces the former gap-reporter.py with an expanded type system.

Usage:
    python ~/.claude/scripts/work-request.py \
        --type MISSING \
        --severity warning \
        --workspace "workforce-hq" \
        --workspace-path "C:/Users/.../1.- SHARKITECT DIGITAL WORKFORCE HQ" \
        --task "Updating product pricing documents" \
        --category operations \
        --needed "Cross-document update detection when business documents change" \
        --gap "drift-detection-hook exists but doc-lifecycle-cache.json is empty" \
        --impact "Related documents not flagged for update when source doc changes" \
        --fix-type hook \
        --fix-desc "Populate doc-lifecycle-cache.json so drift-detection fires" \
        --fix-components "script: doc-cache-builder.py"

    Or from Python (for agents calling programmatically):
        import subprocess, sys
        subprocess.run([sys.executable, work_request_path, "--json", json_string])

Dependencies: Python stdlib only. No external packages.
"""

import argparse
import json
import os
import sys
import urllib.error  # noqa: used in log_to_supabase
import urllib.request  # noqa: used in log_to_supabase
from datetime import datetime, timezone
from pathlib import Path


# All valid request types
VALID_TYPES = ["MISSING", "UNUSED", "FALLBACK", "TASK", "BUG", "ENHANCE"]

# Capability gap types (original gap-reporter types)
GAP_TYPES = {"MISSING", "UNUSED", "FALLBACK"}

# Operational types (new)
OPERATIONAL_TYPES = {"TASK", "BUG", "ENHANCE"}

# Workspace canonical name -> short prefix used in v2 id format.
# Source: wr-2026-04-25-007 (workspace-prefixed id schema). The short prefix
# scopes the NNN counter per workspace per date, eliminating the cross-workspace
# collision bug. v2 id format: wr-<short>-YYYY-MM-DD-NNN.
WORKSPACE_SHORT_MAP = {
    "workforce-hq": "hq",
    "skill-management-hub": "skillhub",
    "sentinel": "sentinel",
}


def get_skill_hub_path():
    """Read Skill Hub path from config. Returns Path or None."""
    config = Path.home() / ".claude" / "config" / "skill-hub-path.txt"
    if config.exists():
        return Path(config.read_text(encoding="utf-8").strip())
    # Fallback: search common locations
    candidates = [
        Path.home() / "Documents" / "Claude Code Workspaces" / "3.- Skill Management Hub",
        Path.home() / "Documents" / "Claude Code Workspaces" / "Skill Management Hub",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


# ---- Completion Notification Protocol (wr-2026-04-25-002) -------------------
# Resolves a workspace's .routed-tasks/inbox/ path so outgoing WRs can
# auto-inject notify_inbox_path. Mirrors the resolver in close-inbox-item.py.
_WS_FALLBACK_DIR = Path.home() / "Documents" / "Claude Code Workspaces"
_WORKSPACE_DIR_FALLBACK = {
    "workforce-hq": _WS_FALLBACK_DIR / "1.- SHARKITECT DIGITAL WORKFORCE HQ",
    "skill-management-hub": _WS_FALLBACK_DIR / "3.- Skill Management Hub",
    "sentinel": _WS_FALLBACK_DIR / "4.- Sentinel",
}


def _resolve_routed_inbox(canonical_name):
    """Return absolute path string to <workspace>/.routed-tasks/inbox/.

    Skill Hub has no .routed-tasks/inbox/ -- notifications meant for it
    will land in .work-requests/inbox/ via close-inbox-item.py's symmetrical
    resolver. For requester-side injection, we still record the workspace's
    .routed-tasks/inbox/ as the canonical 'where to notify me' anchor for HQ
    and Sentinel; for Skill Hub itself, we record .work-requests/inbox/.
    Returns "" if unresolvable.
    """
    if not canonical_name:
        return ""
    name = str(canonical_name).strip().lower()
    cfg = Path.home() / ".claude" / "config" / f"{name}-path.txt"
    workspace_dir = None
    if cfg.exists():
        try:
            p = Path(cfg.read_text(encoding="utf-8").strip())
            if p.is_dir():
                workspace_dir = p
        except OSError:
            pass
    if workspace_dir is None:
        p = _WORKSPACE_DIR_FALLBACK.get(name)
        if p and p.is_dir():
            workspace_dir = p
    if workspace_dir is None:
        return ""
    if name == "skill-management-hub":
        target = workspace_dir / ".work-requests" / "inbox"
    else:
        target = workspace_dir / ".routed-tasks" / "inbox"
    return str(target) if target.is_dir() else ""


def _build_notification_filename_hint(item_id, target_workspace):
    """Build the canonical notification filename a completer should use."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not item_id:
        item_id = "request"
    # The completer will substitute its own canonical name as <completer>; we
    # use a placeholder the completer will replace if it uses the script
    # default. close-inbox-item.py honors the hint verbatim if provided, so
    # we encode the slug from the request id.
    slug = slugify(str(item_id))[:60]
    return f"rt-{today}-{slug}-completed-by-<completer-workspace>.json"


def _used_counters_for_workspace_date(inbox_dir, today, workspace_short, workspace_canonical):
    """Return set of NNNs already used today for the given workspace prefix.

    v2 (workspace-prefixed): scans for ids matching `wr-<workspace>-YYYY-MM-DD-NNN`.
    v1 legacy fallback: also catches `wr-YYYY-MM-DD-NNN` ids whose JSON has
    matching `source_workspace`. JSON `id` field is authoritative; filename is
    grep convenience only.

    Source: wr-2026-04-25-007. Replaces _used_counters_for_date which scanned
    ALL workspaces' counters together, causing two workspaces filing on the
    same date to pick identical NNNs.
    """
    import re
    used = set()
    siblings = [inbox_dir]
    processed = inbox_dir.parent / "processed"
    if processed.exists():
        siblings.append(processed)
    id_re_v2 = re.compile(rf"^wr-{re.escape(workspace_short)}-{re.escape(today)}-(\d{{3}})$")
    id_re_v1 = re.compile(rf"^wr-{re.escape(today)}-(\d{{3}})$")
    for d in siblings:
        for f in d.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                continue
            wr_id = str(data.get("id", ""))
            m = id_re_v2.match(wr_id)
            if m:
                used.add(int(m.group(1)))
                continue
            # v1 legacy: only count if JSON's source_workspace matches this caller
            m1 = id_re_v1.match(wr_id)
            if m1 and data.get("source_workspace") == workspace_canonical:
                used.add(int(m1.group(1)))
    return used


def get_next_id(inbox_dir, workspace_short, workspace_canonical):
    """Generate next sequential workspace-scoped request ID for today.

    v2 format: wr-<workspace_short>-YYYY-MM-DD-NNN
    NNN counter is per-workspace per-date. Cross-workspace collision is now
    impossible by construction (different workspaces have different prefixes).
    Backward compat: v1 legacy ids in inbox/processed still consume counter
    slots so the next NNN doesn't accidentally reuse one.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    used = _used_counters_for_workspace_date(inbox_dir, today, workspace_short, workspace_canonical)
    next_n = (max(used) + 1) if used else 1
    return f"wr-{workspace_short}-{today}-{next_n:03d}"


def slugify(text):
    """Convert text to filename-safe slug.

    Strips all Windows-illegal characters: : \\ / * ? \" < > |
    Also normalizes spaces, dots, and underscores to hyphens.
    """
    result = text.lower()
    # Replace Windows-illegal characters and common separators with hyphens
    for ch in [':', '\\', '/', '*', '?', '"', '<', '>', '|', ' ', '.', '_']:
        result = result.replace(ch, '-')
    # Collapse multiple hyphens
    while '--' in result:
        result = result.replace('--', '-')
    return result[:40].strip('-')


def build_report(args):
    """Build a work request JSON from arguments."""
    now = datetime.now(timezone.utc)
    request_type = args.type.upper()

    # Workspace short prefix resolution (v2 schema).
    # Source: wr-2026-04-25-007. Unknown workspace -> hard error to prevent
    # silent fallback to v1 format.
    workspace_short = WORKSPACE_SHORT_MAP.get(args.workspace)
    if workspace_short is None:
        print(
            f"ERROR: unknown workspace '{args.workspace}'. "
            f"Cannot derive v2 id prefix. "
            f"Valid workspaces: {sorted(WORKSPACE_SHORT_MAP.keys())}",
            file=sys.stderr,
        )
        sys.exit(2)

    report = {
        "id": None,  # Set after inbox path known
        "id_format_version": 2,
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "request_type": request_type,
        "source_workspace": args.workspace,
        "source_workspace_path": args.workspace_path.replace("\\", "/"),
        "task_description": args.task,
        "work_category": args.category,
        "what_was_needed": args.needed,
        "severity": args.severity.lower(),
        "status": "new",
        "edit_count_at_audit": args.edit_count or 0,
        "nudges_delivered": (args.edit_count or 0) // 5,
        "nudges_acted_on": 0,
        "recommended_fix": {
            "type": args.fix_type,
            "description": args.fix_desc,
            "components": [c.strip() for c in args.fix_components.split(",")]
            if args.fix_components else [],
        },
    }

    # Type-specific fields for capability gaps
    if request_type == "MISSING":
        report["capability_gap"] = args.gap or args.needed
        if args.fallback_used:
            report["resources_used_as_fallback"] = [
                {"type": "generic", "name": args.fallback_used, "note": "Used as fallback"}
            ]
    elif request_type == "UNUSED":
        report["resources_missed"] = [
            {"type": "unknown", "name": args.gap or args.needed, "severity": args.severity}
        ]
        report["resources_available"] = []
        report["resources_used"] = []
    elif request_type == "FALLBACK":
        report["what_would_be_better"] = args.gap or args.needed
        report["resources_used_as_fallback"] = [
            {"type": "generic", "name": args.fallback_used or "general knowledge",
             "note": "Used as fallback"}
        ]

    # Type-specific fields for operational types
    if request_type in OPERATIONAL_TYPES:
        report["description"] = args.gap or args.needed
        if args.target_file:
            report["target_file"] = args.target_file

    report["impact_assessment"] = args.impact or "Impact not specified."

    # Blocked-by fields (if this item depends on another completing first)
    blocked_by = getattr(args, "blocked_by", None)
    if blocked_by:
        report["status"] = "blocked"
        report["blocked_by"] = blocked_by
        report["blocked_by_type"] = getattr(args, "blocked_by_type", None) or "task"
        report["blocked_by_description"] = (
            getattr(args, "blocked_by_desc", None) or "Blocked by Supabase record"
        )
        report["blocker_cleared_notes"] = []

    # Completion Notification Protocol fields (wr-2026-04-25-002).
    # Auto-inject so the completer (Skill Hub, when this WR is closed) writes
    # a notification routed-task back to this workspace's inbox. Suppressed
    # only if the caller passed --no-notify-on-completion.
    if not getattr(args, "no_notify_on_completion", False):
        report["notify_on_completion"] = True
        notify_path = _resolve_routed_inbox(args.workspace)
        if notify_path:
            report["notify_inbox_path"] = notify_path
        # Filename hint helps the completer use a deterministic name when
        # writing the notification file. The id is set later in main(); the
        # completer's close script falls back to its own slug if id is unset.
        # We leave notification_filename_hint to be filled after id assignment.
    else:
        report["notify_on_completion"] = False

    return report


def _detect_workspace_prefix():
    """Infer workspace prefix from CWD. Returns '' if unknown."""
    s = os.getcwd().replace("\\", "/").lower()
    if "skill management hub" in s or "/3.-" in s:
        return "SKILLHUB"
    if ("workforce" in s and "hq" in s) or "/1.-" in s:
        return "HQ"
    if "sentinel" in s or "/4.-" in s:
        return "SENTINEL"
    return ""


def load_env():
    """Load .env from local workspace + global ~/.claude/.env with
    workspace-prefix fallback (e.g. SKILLHUB_SUPABASE_URL -> SUPABASE_URL).

    Returns dict of key=value pairs. Local .env wins over global.
    """
    result = {}

    def _parse(env_file):
        if not env_file.exists():
            return {}
        out = {}
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k:
                out[k] = v
        return out

    # Layer 1: workspace-local .env (walk up from CWD, then script location)
    def _try_load(start):
        search = start
        for _ in range(5):
            env_file = search / ".env"
            if env_file.exists():
                for k, v in _parse(env_file).items():
                    result.setdefault(k, v)
                return True
            search = search.parent
        return False

    if not _try_load(Path.cwd()):
        _try_load(Path(__file__).resolve().parent)

    # Layer 2: global ~/.claude/.env with workspace prefix resolution
    global_env = _parse(Path.home() / ".claude" / ".env")
    if global_env:
        prefix = _detect_workspace_prefix()
        if prefix:
            plen = len(prefix) + 1
            for k, v in global_env.items():
                if k.startswith(f"{prefix}_"):
                    result.setdefault(k[plen:], v)
                    result.setdefault(k, v)
        for k, v in global_env.items():
            if not any(k.startswith(f"{p}_") for p in ("SKILLHUB", "HQ", "SENTINEL")):
                result.setdefault(k, v)

    return result


def log_to_supabase(report, item_type="work_request"):
    """Log a cross-workspace request to Supabase cross_workspace_requests table.

    Best-effort: if Supabase is unreachable or credentials missing, log a
    warning but don't fail the overall request creation. The filesystem
    JSON is the primary record; Supabase is the audit backup.
    """
    env = load_env()
    base_url = env.get("SUPABASE_URL", "").rstrip("/")
    api_key = env.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not base_url or not api_key:
        print("  WARNING: Supabase credentials not found. Skipping audit log.", file=sys.stderr)
        return False

    source_ws = report.get("source_workspace", "unknown")
    # Work requests always go TO skill-management-hub
    # Routed tasks go to whatever assigned_to says
    assigned = report.get("assigned_to", "skill-management-hub")

    row = {
        "item_id": report.get("id", "unknown"),
        "item_type": item_type,
        "summary": report.get("what_was_needed", report.get("description", "No summary")),
        "requested_by": source_ws,
        "assigned_to": assigned,
        "status": "pending",
        "priority": report.get("priority", "medium"),
        "severity": report.get("severity", "info"),
        "context": report.get("task_description", ""),
        "last_updated_by": source_ws,
    }

    url = f"{base_url}/rest/v1/cross_workspace_requests"
    data = json.dumps(row).encode("utf-8")
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        urllib.request.urlopen(req, timeout=10)
        print("  Supabase: logged to cross_workspace_requests")
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"  WARNING: Supabase log failed: {e}", file=sys.stderr)
        return False


def validate_workspace_name(name):
    """Validate workspace name is one of the exact canonical names.

    There are exactly 4 valid values. No aliases, no normalization,
    no silent conversion. If the name doesn't match, it's an error.
    This prevents drift from alternative names.

    Canonical names (source of truth):
      workforce-hq
      skill-management-hub
      sentinel
      global
    """
    CANONICAL_NAMES = {"workforce-hq", "skill-management-hub", "sentinel", "global"}

    if not name:
        return name

    cleaned = name.strip().lower()

    if cleaned in CANONICAL_NAMES:
        return cleaned

    # Not canonical -- reject with helpful error
    print(
        f"ERROR: '{name}' is not a canonical workspace name. "
        f"Valid names: {', '.join(sorted(CANONICAL_NAMES))}. "
        f"Do NOT use alternatives, abbreviations, or filesystem directory names. "
        f"Use the exact canonical name.",
        file=sys.stderr,
    )
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Send a work request to the Skill Management Hub inbox"
    )

    # JSON mode (for programmatic callers)
    parser.add_argument("--json", help="Full work request as JSON string (overrides all other args)")

    # Individual field mode (for CLI callers)
    parser.add_argument("--type", choices=VALID_TYPES,
                        help="Request type: MISSING, UNUSED, FALLBACK (capability gaps) "
                             "or TASK, BUG, ENHANCE (operational)")
    parser.add_argument("--severity", choices=["critical", "warning", "info"],
                        default="warning", help="Request severity")
    parser.add_argument("--workspace", help="Source workspace name")
    parser.add_argument("--workspace-path", help="Source workspace absolute path")
    parser.add_argument("--task", help="Task description when issue was detected")
    parser.add_argument("--category", help="Work category (content, code, operations, etc.)")
    parser.add_argument("--needed", help="What capability or fix is needed")
    parser.add_argument("--gap", help="Specific gap/issue description")
    parser.add_argument("--impact", help="How this affects work quality or output")
    parser.add_argument("--fix-type", default="skill",
                        help="Fix type: skill, hook, agent, plugin, protocol, tool, workflow")
    parser.add_argument("--fix-desc", help="Description of recommended fix")
    parser.add_argument("--fix-components", help="Comma-separated component list")
    parser.add_argument("--fallback-used", help="What generic resource was used as fallback")
    parser.add_argument("--target-file", help="Target file for BUG/ENHANCE types")
    parser.add_argument("--edit-count", type=int, default=0,
                        help="Edit counter value at time of report")
    parser.add_argument("--blocked-by", help="Supabase UUID of blocking record")
    parser.add_argument("--blocked-by-type",
                        choices=["task", "project", "cross_workspace_request"],
                        help="Type of blocking record")
    parser.add_argument("--blocked-by-desc",
                        help="Human-readable description of what this is blocked by")
    # Completion Notification Protocol (wr-2026-04-25-002).
    parser.add_argument("--no-notify-on-completion", action="store_true",
                        help="Set notify_on_completion=false on the outgoing WR. "
                             "Reserved for fire-and-forget informational filings "
                             "(kind=fyi). Default behavior is to inject "
                             "notify_on_completion=true and notify_inbox_path so "
                             "the completer auto-writes a notification back.")
    # Test-harness flags (wr-2026-04-25-007). Allow unit tests to exercise
    # creation without writing to the real Skill Hub inbox or hitting Supabase.
    parser.add_argument("--no-supabase", action="store_true",
                        help="Skip the Supabase audit log POST. For tests.")
    parser.add_argument("--output-dir",
                        help="Override target inbox directory (default: Skill Hub "
                             ".work-requests/inbox/). For tests.")

    args = parser.parse_args()

    # Normalize workspace name to canonical kebab-case
    if args.workspace:
        args.workspace = validate_workspace_name(args.workspace)

    # Find target inbox.
    # --output-dir overrides for tests (creation goes wherever the test asks).
    # Otherwise: Skill Hub's .work-requests/inbox/ (the canonical destination).
    if args.output_dir:
        inbox = Path(args.output_dir)
        inbox.mkdir(parents=True, exist_ok=True)
        # processed/ sibling for counter scanning to work
        (inbox.parent / "processed").mkdir(exist_ok=True)
    else:
        hub_path = get_skill_hub_path()
        if not hub_path:
            print("ERROR: Cannot find Skill Management Hub path.", file=sys.stderr)
            print("Check ~/.claude/config/skill-hub-path.txt", file=sys.stderr)
            return 1

        inbox = hub_path / ".work-requests" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)

    # Build or parse report
    if args.json:
        try:
            report = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
            return 1
        # Normalize workspace name in JSON mode too
        if "source_workspace" in report:
            report["source_workspace"] = validate_workspace_name(
                report["source_workspace"]
            )
        # Ensure request_type field exists (backward compat with old gap_type)
        if "request_type" not in report and "gap_type" in report:
            report["request_type"] = report["gap_type"]
    else:
        if not all([args.type, args.workspace, args.task, args.needed]):
            print("ERROR: --type, --workspace, --task, and --needed are required.",
                  file=sys.stderr)
            print("Or use --json to pass a complete report.", file=sys.stderr)
            return 1
        if not args.workspace_path:
            args.workspace_path = os.getcwd()
        report = build_report(args)

    # Assign ID and filename, with retry loop to handle race conditions.
    # v2 (wr-2026-04-25-007): id is workspace-prefixed; counter is workspace-scoped.
    # Cross-workspace collision is impossible by construction.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    source_ws = report.get("source_workspace", "unknown")
    workspace_short = WORKSPACE_SHORT_MAP.get(source_ws)
    if workspace_short is None:
        print(
            f"ERROR: unknown workspace '{source_ws}'. "
            f"Cannot derive v2 id prefix. "
            f"Valid workspaces: {sorted(WORKSPACE_SHORT_MAP.keys())}",
            file=sys.stderr,
        )
        return 1
    ws_slug = slugify(source_ws)
    desc_slug = slugify(report.get("what_was_needed", report.get("description", "request"))[:30])
    filepath = None
    for _ in range(10):
        report["id"] = get_next_id(inbox, workspace_short, source_ws)
        id_suffix = report["id"].split("-")[-1]
        filename = f"{today}_{ws_slug}_{desc_slug}-{id_suffix}.json"
        candidate = inbox / filename
        # If a file with this name OR this id-suffix exists in inbox/processed
        # for THIS WORKSPACE, retry. (Cross-workspace -NNN.json filename
        # overlap is harmless — distinct ws_slug prefixes; matching them
        # caused infinite-retry when Sentinel had a -001.json the same
        # date Skill Hub tried to file its own. Discovered while filing the
        # tests-sync gap WR mid-2026-04-27.)
        existing_suffix = list(inbox.glob(f"{today}_{ws_slug}_*-{id_suffix}.json"))
        processed_dir = inbox.parent / "processed"
        if processed_dir.exists():
            existing_suffix += list(
                processed_dir.glob(f"{today}_{ws_slug}_*-{id_suffix}.json")
            )
        if existing_suffix or candidate.exists():
            continue  # collision -- retry with higher counter
        # Attempt exclusive create (fail if another process wrote in the meantime)
        content = json.dumps(report, indent=2, ensure_ascii=True)
        try:
            fd = os.open(str(candidate), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            continue  # raced -- retry
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        filepath = candidate
        break
    if filepath is None:
        print("ERROR: failed to allocate unique request id after 10 retries", file=sys.stderr)
        return 1

    # Backfill notification_filename_hint now that id is final.
    # build_report() couldn't do this because id wasn't allocated yet. We
    # update both the in-memory report dict and the on-disk JSON.
    if report.get("notify_on_completion") is True \
            and "notification_filename_hint" not in report:
        hint = _build_notification_filename_hint(
            report["id"], "<completer-workspace>"
        )
        report["notification_filename_hint"] = hint
        try:
            filepath.write_text(
                json.dumps(report, indent=2, ensure_ascii=True),
                encoding="utf-8",
            )
        except OSError:
            # Non-fatal: WR is already on disk without the hint, completer
            # will still derive a sensible filename. Worst case: filename
            # convention varies but the notification still lands.
            pass

    # Validate write succeeded (Windows can silently truncate on illegal chars)
    if not filepath.exists() or filepath.stat().st_size == 0:
        print(f"ERROR: File write failed or produced 0-byte file: {filepath}", file=sys.stderr)
        print("Check filename for Windows-illegal characters.", file=sys.stderr)
        return 1

    req_type = report.get("request_type", report.get("gap_type", "unknown"))
    print(f"Work request written: {filepath}")
    print(f"  ID: {report['id']}")
    print(f"  Type: {req_type}")
    print(f"  Severity: {report.get('severity')}")
    print(f"  From: {report.get('source_workspace')}")

    # Log to Supabase cross_workspace_requests (best-effort audit trail).
    # --no-supabase skips this for tests.
    if not args.no_supabase:
        log_to_supabase(report, item_type="work_request")

    return 0


if __name__ == "__main__":
    sys.exit(main())
