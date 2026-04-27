#!/usr/bin/env python3
"""wr-supabase-reconcile.py -- Fix 2026-04-25 batch-close drift in cross_workspace_requests.

Reads Sentinel pre-audit JSON (output of rt-2026-04-27-sentinel-wr-id-pre-audit).
For each entry, PATCHes the correct row's resolution_summary to match the
local processed/*.json content. Logs a reconciliation event to activity_stream
on success.

Source: wr-2026-04-25-007 Task 6/8.
Spec: 3.- Skill Management Hub/docs/superpowers/specs/2026-04-27-wr-id-schema-workspace-prefixed-design.md
Plan: ~/.claude/plans/2026-04-27-wr-id-schema-workspace-prefixed.md
Audit input: ~/.claude/.tmp/sentinel-wr-id-pre-audit-results.json (produced
by Sentinel pre-audit, Task 7).

Usage:
    python wr-supabase-reconcile.py --audit-file <path>           # dry-run
    python wr-supabase-reconcile.py --audit-file <path> --apply
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
    base_url: str, key: str, event_type: str, content: str, metadata: dict
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
    """
    endpoint = f"{base_url}/rest/v1/activity_stream"
    body = {
        "workspace": "skill-management-hub",
        "platform": "wr-supabase-reconcile.py",
        "event_type": event_type,
        "content": content,
        "metadata": metadata,
        "actor": "skill-management-hub",
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audit-file", required=True,
                    help="Sentinel pre-audit JSON (e.g. "
                         "~/.claude/.tmp/sentinel-wr-id-pre-audit-results.json)")
    ap.add_argument("--apply", action="store_true",
                    help="Apply changes. Default is dry-run.")
    ap.add_argument("--no-activity-log", action="store_true",
                    help="Skip activity_stream logging on success.")
    args = ap.parse_args()

    audit_path = Path(args.audit_file).expanduser()
    if not audit_path.exists():
        print(f"ERROR: audit file not found: {audit_path}", file=sys.stderr)
        return 2

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if not isinstance(audit, list):
        print("ERROR: audit file must be a JSON list", file=sys.stderr)
        return 2

    load_env()
    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    api_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not base_url or not api_key:
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing from .env",
              file=sys.stderr)
        return 2

    print(f"Reading {len(audit)} drift entries from {audit_path.name}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
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
            "last_updated_by": "skill-management-hub",
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
                )
        else:
            print(f"  FAIL {target}: HTTP {status} {body[:200]}")
            failed += 1

    mode_label = "Applied" if args.apply else "Dry-run"
    print(f"\n{mode_label}: {fixed}/{len(audit)} OK, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
