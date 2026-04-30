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
from datetime import datetime, timedelta, timezone
from pathlib import Path


# All valid request types
VALID_TYPES = ["MISSING", "UNUSED", "FALLBACK", "TASK", "BUG", "ENHANCE"]

# Capability gap types (original gap-reporter types)
GAP_TYPES = {"MISSING", "UNUSED", "FALLBACK"}

# Operational types (new)
OPERATIONAL_TYPES = {"TASK", "BUG", "ENHANCE"}

# Five canonical Supabase item_type values (post 2026-04-30 widen migration).
# work_request:           originator filing capability gap or task to Skill Hub.
# routed_task:            cross-workspace task dispatch to a target workspace.
# completion_notification: anti-ping-pong ack of cross-workspace completion.
# fyi:                    fire-and-forget informational filing (no ack).
# lifecycle_review:       OUT OF SCOPE for this script -- separate dispatch path.
# Source: wr-sentinel-2026-04-30-009.
ITEM_TYPES_SUPPORTED = {
    "work_request",
    "routed_task",
    "completion_notification",
    "fyi",
}
DEFAULT_ITEM_TYPE = "work_request"

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


def _resolve_target_inbox(item_type, target_workspace):
    """Return Path to the target inbox for a given item_type + target_workspace.

    Routing rules (wr-sentinel-2026-04-30-009):
      - work_request: ALWAYS routes to Skill Hub's .work-requests/inbox/.
        target_workspace is ignored (work requests are by-definition addressed
        to the Skill Hub for triage + build).
      - routed_task | completion_notification | fyi: routes to the target
        workspace's .routed-tasks/inbox/ EXCEPT for skill-management-hub
        which has no .routed-tasks/ -- inbound to Skill Hub goes through
        .work-requests/inbox/ per protocol.

    Returns Path or None if the destination cannot be resolved (workspace
    directory missing or unknown workspace name). Caller must handle None.
    """
    item_type = (item_type or "").strip().lower()
    if item_type not in ITEM_TYPES_SUPPORTED:
        return None

    if item_type == "work_request":
        hub = get_skill_hub_path()
        if hub is None:
            return None
        target = hub / ".work-requests" / "inbox"
        return target

    target_ws = (target_workspace or "").strip().lower()
    if not target_ws:
        return None

    workspace_dir = None
    cfg = Path.home() / ".claude" / "config" / f"{target_ws}-path.txt"
    if cfg.exists():
        try:
            p = Path(cfg.read_text(encoding="utf-8").strip())
            if p.is_dir():
                workspace_dir = p
        except OSError:
            pass
    if workspace_dir is None:
        p = _WORKSPACE_DIR_FALLBACK.get(target_ws)
        if p and p.is_dir():
            workspace_dir = p
    if workspace_dir is None:
        return None
    if target_ws == "skill-management-hub":
        return workspace_dir / ".work-requests" / "inbox"
    return workspace_dir / ".routed-tasks" / "inbox"


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


# ---- Quality gates (wr-2026-04-25-001 Phase 1 Task 1.2) --------------------
# Two gates added to reduce inbox noise + force concrete impact articulation.
# Both bypassable via --skip-dedup / --skip-impact-floor for tests.

# Block-listed generic impact phrases. Case-insensitive substring match.
# Source: plan spec Step 3 example block list. Extend conservatively.
_IMPACT_BLOCK_LIST = (
    "could be useful",
    "might be nice",
    "general improvement",
    "would be nice",
    "nice to have",
)

# Minimum chars for --impact text after stripping whitespace.
_IMPACT_MIN_CHARS = 30

# Dedup window: same source_workspace + same task_description filed within
# this many days = duplicate (counter increment, no new file).
_DEDUP_WINDOW_DAYS = 7


def _check_impact_floor(impact_text):
    """Return human-readable violation message or None if --impact passes the floor.

    Rejection rules:
      - Missing or empty after strip
      - < _IMPACT_MIN_CHARS chars after strip
      - Contains any block-listed phrase (case-insensitive substring match)

    Returns:
        str (violation message) or None (passes).
    """
    if not impact_text:
        return (
            "--impact is required and must articulate concrete impact "
            "(would have shortened fix by X / would have raised confidence "
            "from low to high). Empty/missing rejected."
        )
    stripped = impact_text.strip()
    if len(stripped) < _IMPACT_MIN_CHARS:
        return (
            f"--impact must articulate concrete impact "
            f"(would have shortened fix by X / would have raised confidence "
            f"from low to high). Got {len(stripped)} chars; need >= "
            f"{_IMPACT_MIN_CHARS}."
        )
    lower = stripped.lower()
    for phrase in _IMPACT_BLOCK_LIST:
        if phrase in lower:
            return (
                f"--impact contains block-listed generic phrase '{phrase}'. "
                f"Articulate concrete impact instead "
                f"(would have shortened fix by X / would have raised "
                f"confidence from low to high)."
            )
    return None


def _find_dedup_match(inbox_dir, source_workspace, task_description, today_iso):
    """Scan inbox + processed for a same-source same-task entry filed within
    the dedup window.

    Returns:
        (Path, dict) of the matching JSON file + its parsed data, or
        (None, None) if no match.

    Match criteria (ALL must hold):
      - Same source_workspace
      - Same task_description (case-insensitive exact match after strip)
      - Filed within _DEDUP_WINDOW_DAYS of today
    """
    if not source_workspace or not task_description:
        return None, None
    target_task = task_description.strip().lower()
    if not target_task:
        return None, None
    today_dt = datetime.strptime(today_iso, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    window_start = today_dt - timedelta(days=_DEDUP_WINDOW_DAYS)
    siblings = [inbox_dir]
    processed = inbox_dir.parent / "processed"
    if processed.exists():
        siblings.append(processed)
    for d in siblings:
        for f in d.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                continue
            if data.get("source_workspace") != source_workspace:
                continue
            existing_task = (data.get("task_description") or "").strip().lower()
            if existing_task != target_task:
                continue
            ts = data.get("timestamp")
            if not ts:
                continue
            try:
                # Tolerate both 'Z' and explicit offset
                ts_clean = ts.replace("Z", "+00:00")
                filed_dt = datetime.fromisoformat(ts_clean)
                if filed_dt.tzinfo is None:
                    filed_dt = filed_dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if window_start <= filed_dt <= today_dt + timedelta(days=1):
                return f, data
    return None, None


def _increment_dedup_count(filepath, data):
    """Increment dedup_count on an existing WR JSON file in-place.

    Returns the new counter value. Best-effort: I/O failures swallow.
    """
    current = int(data.get("dedup_count") or 0)
    new_value = current + 1
    data["dedup_count"] = new_value
    data["dedup_last_seen"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        filepath.write_text(
            json.dumps(data, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
    except OSError:
        pass
    return new_value


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

    # Resolve item_type (defaults to work_request for back-compat).
    # Source: wr-sentinel-2026-04-30-009. Adds 4 supported item_types matching
    # the post-2026-04-30 widened Supabase CHECK constraint.
    item_type = (getattr(args, "item_type", None) or DEFAULT_ITEM_TYPE).strip().lower()
    target_workspace = (getattr(args, "target_workspace", None) or "").strip().lower()

    report = {
        "id": None,  # Set after inbox path known
        "id_format_version": 2,
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "item_type": item_type,
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

    # Routed-task / completion-notification / fyi semantics.
    # Source: wr-sentinel-2026-04-30-009.
    if item_type == "routed_task":
        # Cross-workspace dispatch: source -> target. Mirror the
        # source/target into routed_from/routed_to so the receiver can
        # identify both ends without reparsing item_type.
        report["routed_from"] = args.workspace
        if target_workspace:
            report["routed_to"] = target_workspace
    elif item_type == "completion_notification":
        # Anti-ping-pong: notification items must NEVER request a
        # follow-up notification on close.
        report["kind"] = "completion_notification"
        report["routed_from"] = args.workspace
        if target_workspace:
            report["routed_to"] = target_workspace
    elif item_type == "fyi":
        # Fire-and-forget: by definition no acknowledgement expected.
        report["kind"] = "fyi"
        report["routed_from"] = args.workspace
        if target_workspace:
            report["routed_to"] = target_workspace

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
    # only if the caller passed --no-notify-on-completion OR the item_type is
    # itself a notification/fyi (anti-ping-pong: closing a notification must
    # not generate another notification).
    forces_notify_off = item_type in {"completion_notification", "fyi"}
    if not getattr(args, "no_notify_on_completion", False) and not forces_notify_off:
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
    # Routing target for the assigned_to column.
    # Source: wr-sentinel-2026-04-30-009.
    #   work_request           -> always Skill Hub (capability hub triages all)
    #   routed_task / fyi      -> the target workspace named in routed_to
    #   completion_notification -> the target workspace named in routed_to
    # If routed_to is missing for a non-work_request item, we fall back to
    # explicit assigned_to (legacy callers) or Skill Hub (last resort).
    if item_type == "work_request":
        assigned = "skill-management-hub"
    else:
        assigned = (
            report.get("routed_to")
            or report.get("assigned_to")
            or "skill-management-hub"
        )

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
    # Quality gate flags (wr-2026-04-25-001 Phase 1 Task 1.2). Default behavior
    # enforces both gates; opt-out flags exist for test harnesses.
    parser.add_argument("--skip-dedup", action="store_true",
                        help="Skip the 7-day same-source same-task dedup window. "
                             "For tests that intentionally file repeats.")
    parser.add_argument("--skip-impact-floor", action="store_true",
                        help="Skip the --impact severity floor (>=30 chars + no "
                             "block-listed generic phrases). For tests.")
    # ONE filing tool consolidation (wr-sentinel-2026-04-30-009).
    # --item-type lets a single script file work_requests, routed_tasks,
    # completion_notifications, and fyi messages. --target-workspace names
    # the destination for non-work_request items.
    parser.add_argument("--item-type",
                        choices=sorted(ITEM_TYPES_SUPPORTED),
                        default=DEFAULT_ITEM_TYPE,
                        help="Item type recorded on the cross_workspace_requests "
                             "row. Defaults to 'work_request' (preserves all "
                             "pre-2026-04-30 callers). Use 'routed_task' for "
                             "cross-workspace task dispatch, "
                             "'completion_notification' for ack of completed "
                             "cross-workspace work, or 'fyi' for fire-and-forget "
                             "informational filings. lifecycle_review uses a "
                             "separate dispatch path -- not in this flag.")
    parser.add_argument("--target-workspace",
                        help="Destination workspace for non-work_request items. "
                             "Required when --item-type is routed_task, "
                             "completion_notification, or fyi. Ignored for "
                             "work_request (always routes to Skill Hub).")

    args = parser.parse_args()

    # Severity floor on --impact (wr-2026-04-25-001 INFRA 9).
    # Skipped in JSON mode (caller takes responsibility) and when --skip-impact-floor.
    if not args.skip_impact_floor and not args.json:
        floor_violation = _check_impact_floor(args.impact)
        if floor_violation:
            print(f"ERROR: severity floor: {floor_violation}", file=sys.stderr)
            return 1

    # Normalize workspace name to canonical kebab-case
    if args.workspace:
        args.workspace = validate_workspace_name(args.workspace)

    # Find target inbox.
    # --output-dir overrides for tests (creation goes wherever the test asks).
    # Otherwise: route by --item-type via _resolve_target_inbox. Default
    # work_request still lands in Skill Hub's .work-requests/inbox/.
    # Source: wr-sentinel-2026-04-30-009.
    if args.output_dir:
        inbox = Path(args.output_dir)
        inbox.mkdir(parents=True, exist_ok=True)
        # processed/ sibling for counter scanning to work
        (inbox.parent / "processed").mkdir(exist_ok=True)
    else:
        item_type_for_routing = (args.item_type or DEFAULT_ITEM_TYPE).strip().lower()
        if item_type_for_routing != "work_request" and not args.target_workspace:
            print(
                f"ERROR: --target-workspace is required when --item-type is "
                f"{item_type_for_routing!r} (item_type != work_request must "
                f"name a destination workspace).",
                file=sys.stderr,
            )
            return 1
        target_inbox = _resolve_target_inbox(
            item_type_for_routing,
            args.target_workspace,
        )
        if target_inbox is None:
            print(
                f"ERROR: Cannot resolve target inbox for item_type="
                f"{item_type_for_routing!r}, target_workspace="
                f"{args.target_workspace!r}. "
                f"Check ~/.claude/config/<workspace>-path.txt.",
                file=sys.stderr,
            )
            return 1
        inbox = target_inbox
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox.parent / "processed").mkdir(exist_ok=True)

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

    # 7-day same-source same-task dedup window (wr-2026-04-25-001 INFRA 9).
    # Skipped via --skip-dedup (tests). When a duplicate is found, increment
    # dedup_count on the EXISTING file in-place and exit successfully -- do NOT
    # write a new file. Prevents inbox noise from repeated automatic filings of
    # the same gap (e.g. flaky cron, retried error class).
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not args.skip_dedup:
        existing_path, existing_data = _find_dedup_match(
            inbox,
            report.get("source_workspace"),
            report.get("task_description"),
            today_iso,
        )
        if existing_path is not None and existing_data is not None:
            new_count = _increment_dedup_count(existing_path, existing_data)
            print(
                f"Duplicate of {existing_data.get('id', 'unknown')} "
                f"(filed within {_DEDUP_WINDOW_DAYS} days, same source + task). "
                f"dedup_count incremented to {new_count}. No new file written."
            )
            return 0

    # Assign ID and filename, with retry loop to handle race conditions.
    # v2 (wr-2026-04-25-007): id is workspace-prefixed; counter is workspace-scoped.
    # Cross-workspace collision is impossible by construction.
    today = today_iso
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
    # item_type passed from --item-type so routed_task / completion_notification
    # / fyi rows are recorded under the correct CHECK value (post-2026-04-30
    # widen migration). Source: wr-sentinel-2026-04-30-009.
    if not args.no_supabase:
        log_to_supabase(
            report,
            item_type=report.get("item_type", DEFAULT_ITEM_TYPE),
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
