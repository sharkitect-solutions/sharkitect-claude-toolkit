#!/usr/bin/env python3
"""wr-supabase-reconcile.py -- Reconcile cross_workspace_requests drift.

Two modes:

  (1) --audit-file <path>          Original mode (wr-2026-04-25-007).
      Fix resolution_summary text from a Sentinel pre-audit JSON.
      Entries: {"correct_item_id": ..., "correct_what_was_done": ...}.
      Touches resolution_summary + last_updated_by only.

  (2) --historical-manifest <path>  Added 2026-04-29 (wr-sentinel-2026-04-29-001).
      Reconcile full status drift for historical pre-protocol closes
      (2026-04-16 to 2026-04-18). Reads each entry's local processed file
      (resolution.what_was_done + resolution.resolved_date) and PATCHes
      status, resolution_summary, resolved_at, resolved_by, last_updated_by.
      Status normalization mirrors close-inbox-item.py: processed/resolved
      collapse to 'completed'; 'superseded' passes through with the
      superseded_by reference prefixed into resolution_summary (no
      dedicated column exists).

      Manifest schema (JSON list):
        [
          {
            "item_id": "wr-YYYY-MM-DD-NNN",
            "target_status": "completed" | "superseded",
            "processed_file": "filename.json",        // basename, looked up in
                                                      // <workspace>/.work-requests/processed/
                                                      // for Skill Hub or
                                                      // <workspace>/.routed-tasks/processed/
                                                      // for HQ/Sentinel
            "superseded_by": "wr-YYYY-MM-DD-NNN"      // optional, only when target_status='superseded'
          },
          ...
        ]

Logs each reconciliation to activity_stream as a drift_correction event.

Source: wr-2026-04-25-007 (original) + wr-sentinel-2026-04-29-001 (historical mode).
Spec: 3.- Skill Management Hub/docs/superpowers/specs/2026-04-27-wr-id-schema-workspace-prefixed-design.md
Plan: ~/.claude/plans/2026-04-27-wr-id-schema-workspace-prefixed.md

Usage:
    python wr-supabase-reconcile.py --audit-file <path>                 # dry-run
    python wr-supabase-reconcile.py --audit-file <path> --apply
    python wr-supabase-reconcile.py --historical-manifest <path>        # dry-run
    python wr-supabase-reconcile.py --historical-manifest <path> --apply
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

WORKSPACE_PREFIXES = ("SKILLHUB", "HQ", "SENTINEL")


def _parse_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
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


def _detect_workspace_prefix() -> str | None:
    cwd_str = str(Path.cwd()).lower()
    if "1.- sharkitect digital workforce hq" in cwd_str:
        return "HQ"
    if "3.- skill management hub" in cwd_str:
        return "SKILLHUB"
    if "4.- sentinel" in cwd_str:
        return "SENTINEL"
    return None


def load_env() -> None:
    """Mirror update-project-status.py loader: prefixed keys -> unprefixed,
    then unprefixed-universal -- so os.environ.get("SUPABASE_URL") works."""
    global_env = _parse_env(Path.home() / ".claude" / ".env")
    prefix = _detect_workspace_prefix()
    if prefix:
        plen = len(prefix) + 1
        for k, v in global_env.items():
            if k.startswith(f"{prefix}_"):
                os.environ.setdefault(k[plen:], v)
                os.environ.setdefault(k, v)
    for k, v in global_env.items():
        if not any(k.startswith(f"{p}_") for p in WORKSPACE_PREFIXES):
            os.environ.setdefault(k, v)


def _headers(key: str, prefer: str | None = None) -> dict[str, str]:
    h = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def patch_supabase(base_url: str, key: str, item_id: str, payload: dict) -> tuple[int, str]:
    endpoint = (
        f"{base_url}/rest/v1/cross_workspace_requests"
        f"?item_id=eq.{urllib_quote(item_id)}"
    )
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        method="PATCH",
        headers=_headers(key, prefer="return=representation"),
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as e:
        return 0, f"network error: {e}"


def get_supabase(base_url: str, key: str, item_id: str) -> tuple[int, str]:
    endpoint = (
        f"{base_url}/rest/v1/cross_workspace_requests"
        f"?item_id=eq.{urllib_quote(item_id)}&select=item_id,resolution_summary,last_updated_by"
    )
    req = urllib.request.Request(endpoint, headers=_headers(key))
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as e:
        return 0, f"network error: {e}"


def log_activity_event(
    base_url: str, key: str, event_type: str, content: str, metadata: dict,
    *, workspace: str = "skill-management-hub", actor: str = "skill-management-hub",
) -> tuple[int, str]:
    """Insert into activity_stream so the reconciliation is auditable.

    activity_stream schema (verified 2026-04-27):
      - workspace (text, NOT NULL, CHECK in {workforce-hq, skill-management-hub,
        sentinel, global})
      - platform (text, NOT NULL)
      - event_type (text, NOT NULL)
      - content (text, NOT NULL) -- human-readable summary
      - metadata (jsonb, nullable) -- structured payload
      - actor (text, nullable)

    workspace/actor accept caller override (added 2026-04-27, wr-sentinel-023)
    so the script can be run from any workspace and attribute the reconciliation
    correctly. Default preserves backward compat with prior Skill Hub-only usage.
    """
    endpoint = f"{base_url}/rest/v1/activity_stream"
    body = {
        "workspace": workspace,
        "platform": "wr-supabase-reconcile.py",
        "event_type": event_type,
        "content": content,
        "metadata": metadata,
        "actor": actor,
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=_headers(key, prefer="return=representation"),
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as e:
        return 0, f"network error: {e}"


def urllib_quote(s: str) -> str:
    """Minimal URL-quote for PostgREST eq filters."""
    import urllib.parse
    return urllib.parse.quote(s, safe="")


# --------------------------------------------------------------------------
# Historical-manifest mode helpers (added 2026-04-29, wr-sentinel-2026-04-29-001)
# --------------------------------------------------------------------------

# Status normalization mirrors close-inbox-item.py (~ line 116). Local close
# vocabulary collapses to Supabase vocabulary at write time.
LOCAL_TO_SUPABASE_STATUS = {
    "processed": "completed",
    "resolved":  "completed",
    "completed": "completed",
    "superseded": "superseded",
    "duplicate": "duplicate",
    "rejected":  "rejected",
    "withdrawn": "withdrawn",
}


def _find_processed_dir(workspace: str) -> Path:
    """Resolve workspace -> processed directory.

    Skill Hub uses .work-requests/processed/ (it owns the WR pipeline).
    HQ + Sentinel use .routed-tasks/processed/ for cross-workspace items.
    """
    workspaces_root = (
        Path.home()
        / "Documents"
        / "Claude Code Workspaces"
    )
    if workspace == "skill-management-hub":
        ws_dir = workspaces_root / "3.- Skill Management Hub"
        return ws_dir / ".work-requests" / "processed"
    if workspace == "workforce-hq":
        ws_dir = workspaces_root / "1.- SHARKITECT DIGITAL WORKFORCE HQ"
        return ws_dir / ".routed-tasks" / "processed"
    if workspace == "sentinel":
        ws_dir = workspaces_root / "4.- Sentinel"
        return ws_dir / ".routed-tasks" / "processed"
    raise ValueError(f"Unknown workspace: {workspace}")


def _normalize_resolved_at(raw: str | None) -> str | None:
    """Convert local resolved_date variants to ISO8601 timestamptz Supabase accepts.

    Accepts: '2026-04-17', '2026-04-18T02:28:26Z', '2026-04-18T02:28:26.475047Z'.
    Returns None if input is None or unparseable -- caller decides whether to
    abort or fall back to a synthetic timestamp.
    """
    if not raw:
        return None
    raw = raw.strip()
    # YYYY-MM-DD -> append T00:00:00Z
    if len(raw) == 10 and raw[4] == "-" and raw[7] == "-":
        return f"{raw}T00:00:00Z"
    # Already has time component -- assume timestamptz-compatible
    return raw


def _read_processed_file(processed_dir: Path, filename: str) -> dict:
    """Read a processed/*.json by basename. Returns parsed dict.

    Raises FileNotFoundError if the file is missing.
    """
    p = processed_dir / filename
    if not p.exists():
        raise FileNotFoundError(f"processed file not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _build_resolution_summary(
    raw_text: str,
    *,
    target_status: str,
    superseded_by: str | None,
) -> str:
    """Apply supersession prefix when applicable, then truncate to 500 chars.

    No superseded_by Supabase column exists, so the supersession reference
    must live inside resolution_summary text. If the raw resolution text
    already begins with the supersession reference, do not double-prefix.
    """
    body = raw_text or ""
    if target_status == "superseded" and superseded_by:
        # Skip prefix injection if the body already cites the same superseded_by id.
        already_cited = body.lower().lstrip().startswith(
            f"superseded by {superseded_by.lower()}"
        )
        if not already_cited:
            prefix = f"Superseded by {superseded_by}. "
            max_body = max(0, 500 - len(prefix))
            return (prefix + body[:max_body])[:500]
    return body[:500]


def _process_historical_entry(
    entry: dict,
    *,
    base_url: str,
    api_key: str,
    workspace: str,
    actor: str,
    apply: bool,
    no_activity_log: bool,
) -> tuple[bool, str]:
    """Process one manifest entry. Returns (ok, message).

    Validates entry shape, finds processed file based on entry's source workspace,
    reads resolution data, computes target Supabase payload, then either prints
    the would-PATCH preview (dry-run) or applies the PATCH (live).
    """
    item_id = entry.get("item_id")
    target_status = entry.get("target_status")
    processed_filename = entry.get("processed_file")
    superseded_by = entry.get("superseded_by")
    # Optional override: which workspace's processed/ directory to read from.
    # Defaults to skill-management-hub since that's where this WR's audit pointed.
    source_workspace = entry.get("source_workspace", "skill-management-hub")

    if not (item_id and target_status and processed_filename):
        return False, f"missing required field in entry: {entry!r}"

    sb_status = LOCAL_TO_SUPABASE_STATUS.get(target_status)
    if not sb_status:
        return False, (
            f"{item_id}: target_status={target_status!r} not in "
            f"{sorted(LOCAL_TO_SUPABASE_STATUS)}"
        )

    if target_status == "superseded" and not superseded_by:
        return False, f"{item_id}: target_status=superseded requires superseded_by"

    try:
        processed_dir = _find_processed_dir(source_workspace)
        local = _read_processed_file(processed_dir, processed_filename)
    except (FileNotFoundError, ValueError) as e:
        return False, f"{item_id}: {e}"

    resolution = local.get("resolution") or {}
    raw_text = resolution.get("what_was_done") or ""
    resolved_date = (
        resolution.get("resolved_date")
        or local.get("resolved_at")
        or local.get("timestamp")
    )

    if not raw_text:
        return False, f"{item_id}: local resolution.what_was_done is empty"

    resolution_summary = _build_resolution_summary(
        raw_text, target_status=target_status, superseded_by=superseded_by
    )
    resolved_at = _normalize_resolved_at(resolved_date)

    payload = {
        "status": sb_status,
        "resolution_summary": resolution_summary,
        "resolved_by": (resolution.get("resolved_by") or workspace),
        "last_updated_by": workspace,
    }
    if resolved_at:
        payload["resolved_at"] = resolved_at

    if not apply:
        preview_text = resolution_summary[:80].replace("\n", " ")
        msg = (
            f"WOULD-PATCH {item_id} -> status={sb_status}, "
            f"resolved_at={resolved_at}, resolution_summary={preview_text!r}..."
        )
        return True, msg

    # Pre-check: confirm the row exists and read current state
    status, body = get_supabase(base_url, api_key, item_id)
    if status != 200:
        return False, f"{item_id}: PRE-CHECK HTTP {status} {body[:200]}"

    # PATCH the row
    status, body = patch_supabase(base_url, api_key, item_id, payload)
    if status not in (200, 204):
        return False, f"{item_id}: PATCH HTTP {status} {body[:200]}"

    if not no_activity_log:
        log_activity_event(
            base_url, api_key,
            event_type="drift_correction",
            content=(
                f"Historical status_drift reconciled for {item_id}: "
                f"status -> {sb_status} (was pending), "
                "resolution_summary + resolved_at filled from local processed/. "
                "Drift caused by pre-protocol close path "
                "(2026-04-16 to 2026-04-18, before close-inbox-item.py)."
            ),
            metadata={
                "subject": "historical_status_drift_reconcile",
                "item_id": item_id,
                "target_status": sb_status,
                "superseded_by": superseded_by,
                "processed_file": processed_filename,
                "source_workspace": source_workspace,
                "trigger_wr": "wr-sentinel-2026-04-29-001",
                "audit": "4.- Sentinel/docs/audits/status-drift-audit-2026-04-29.md",
            },
            workspace=workspace,
            actor=actor,
        )
    return True, f"OK   {item_id} -> {sb_status}"


# --------------------------------------------------------------------------
# Main: branch on --audit-file (text mode) or --historical-manifest (status mode)
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-file",
                      help="Sentinel pre-audit JSON (text-only resolution_summary fix).")
    mode.add_argument("--historical-manifest",
                      help="Manifest JSON with item_id, target_status, "
                           "processed_file [, superseded_by, source_workspace] "
                           "for full status drift reconciliation.")
    ap.add_argument("--apply", action="store_true",
                    help="Apply changes. Default is dry-run.")
    ap.add_argument("--no-activity-log", action="store_true",
                    help="Skip activity_stream logging on success.")
    # Added 2026-04-27 (wr-sentinel-2026-04-27-023): workspace + actor flags
    # for accurate attribution when run from a workspace other than Skill Hub.
    # Defaults preserve backward compat. activity_stream.workspace CHECK
    # constraint accepts: workforce-hq | skill-management-hub | sentinel | global.
    ap.add_argument("--workspace",
                    default="skill-management-hub",
                    choices=["skill-management-hub", "workforce-hq", "sentinel", "global"],
                    help="Workspace for last_updated_by + activity_stream.workspace. "
                         "Default: skill-management-hub.")
    ap.add_argument("--actor",
                    default=None,
                    help="Actor for activity_stream.actor. Defaults to --workspace value.")
    args = ap.parse_args()
    actor = args.actor or args.workspace

    load_env()
    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    api_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not base_url or not api_key:
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing from .env",
              file=sys.stderr)
        return 2

    if args.historical_manifest:
        return _run_historical(args, base_url, api_key, actor)
    return _run_audit_file(args, base_url, api_key, actor)


def _run_audit_file(args, base_url: str, api_key: str, actor: str) -> int:
    audit_path = Path(args.audit_file).expanduser()
    if not audit_path.exists():
        print(f"ERROR: audit file not found: {audit_path}", file=sys.stderr)
        return 2

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if not isinstance(audit, list):
        print("ERROR: audit file must be a JSON list", file=sys.stderr)
        return 2

    print(f"Reading {len(audit)} drift entries from {audit_path.name}")
    print(f"Mode: AUDIT-FILE / {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Supabase: {base_url}\n")

    fixed = 0
    failed = 0
    for entry in audit:
        target = entry.get("correct_item_id")
        correct_text = entry.get("correct_what_was_done", "")
        if not target or not correct_text:
            print(f"  SKIP (missing fields): {entry!r}")
            continue

        if not args.apply:
            preview = correct_text[:80].replace("\n", " ")
            print(f"  WOULD-PATCH item_id={target}")
            print(f"    -> resolution_summary = {preview!r}...")
            fixed += 1
            continue

        # Verify current state before mutation
        status, body = get_supabase(base_url, api_key, target)
        if status != 200:
            print(f"  PRE-CHECK FAIL {target}: HTTP {status} {body[:200]}")
            failed += 1
            continue

        # PATCH the row
        # PostgREST limit: resolution_summary may have a CHECK constraint on
        # length. Truncate to 500 chars matching close-inbox-item.py convention.
        truncated = correct_text[:500]
        status, body = patch_supabase(base_url, api_key, target, {
            "resolution_summary": truncated,
            "last_updated_by": args.workspace,
        })
        if status in (200, 204):
            print(f"  OK   {target}")
            fixed += 1
            if not args.no_activity_log:
                log_activity_event(
                    base_url, api_key,
                    event_type="drift_correction",
                    content=(
                        f"Reconciled cross_workspace_requests.resolution_summary "
                        f"for {target}; restored from local processed/*.json. "
                        "Drift caused by 2026-04-25 batch close using "
                        "filename-derivation when JSON 'id' field was missing."
                    ),
                    metadata={
                        "subject": "wr_id_supabase_drift_reconcile",
                        "item_id": target,
                        "source_audit": "sentinel-wr-id-pre-audit-results.json",
                        "trigger_wr": "wr-2026-04-25-007",
                    },
                    workspace=args.workspace,
                    actor=actor,
                )
        else:
            print(f"  FAIL {target}: HTTP {status} {body[:200]}")
            failed += 1

    mode_label = "Applied" if args.apply else "Dry-run"
    print(f"\n{mode_label}: {fixed}/{len(audit)} OK, {failed} failed.")
    return 0 if failed == 0 else 1


def _run_historical(args, base_url: str, api_key: str, actor: str) -> int:
    manifest_path = Path(args.historical_manifest).expanduser()
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        print("ERROR: manifest must be a JSON list", file=sys.stderr)
        return 2

    print(f"Reading {len(manifest)} historical entries from {manifest_path.name}")
    print(f"Mode: HISTORICAL-MANIFEST / {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Supabase: {base_url}\n")

    ok_count = 0
    failed = 0
    for entry in manifest:
        ok, msg = _process_historical_entry(
            entry,
            base_url=base_url,
            api_key=api_key,
            workspace=args.workspace,
            actor=actor,
            apply=args.apply,
            no_activity_log=args.no_activity_log,
        )
        prefix = "  " if ok else "  FAIL "
        print(f"{prefix}{msg}")
        if ok:
            ok_count += 1
        else:
            failed += 1

    mode_label = "Applied" if args.apply else "Dry-run"
    print(f"\n{mode_label}: {ok_count}/{len(manifest)} OK, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
