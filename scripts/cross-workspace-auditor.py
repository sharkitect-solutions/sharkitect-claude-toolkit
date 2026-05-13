"""
cross-workspace-auditor.py -- Sentinel-owned daily aggregator that consumes
existing drift classes from Skill Hub's audit-autonomous-systems.py, adds 4 new
Sentinel-owned drift sources, acts autonomously within Sentinel scope, and
routes audit_finding tasks to other workspaces.

Spec: 4.- Sentinel/docs/specs/spec-cross-workspace-auditor.md
Topic: rt-skillhub-2026-05-10-topic2-cross-workspace-audit-with-suggest-authority

Three-tier action model (per 2026-05-12 user direction):
  Tier A -- Sentinel autofixes mechanical drift + routes drift_fixed_notification
  Tier B -- Sentinel routes audit_finding for judgment-required classes
  Tier C -- Sentinel sends Slack notification to user for overdue HARs

Usage:
    python cross-workspace-auditor.py                    # full run
    python cross-workspace-auditor.py --dry-run          # log findings, no routing
    python cross-workspace-auditor.py --json             # machine-readable output
    python cross-workspace-auditor.py --source <name>    # one drift source only

Pure stdlib (+ .env parsing). ASCII-only.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKSPACES_PARENT = Path(__file__).resolve().parent.parent.parent
SKILL_HUB_AUDIT = (
    WORKSPACES_PARENT / "Documents" / "Claude Code Workspaces"
    / "3.- Skill Management Hub" / "tools" / "audit-autonomous-systems.py"
)


def load_env(env_path: Path) -> dict:
    """Parse a .env file into a dict. Skip blank lines and # comments.

    Strips inline comments after the value (e.g. KEY=val # comment) -- mirrors
    notify-slack.py and slack-send.py behavior. Required because workspace .env
    files annotate channel IDs and other identifiers with trailing comments.
    """
    if not env_path.exists():
        return {}
    out = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if "#" in v:
            v = v.split("#", 1)[0].strip()
        out[k.strip()] = v
    return out


def consume_asset_registry_drift() -> dict:
    """Run Skill Hub's audit-autonomous-systems.py --json and return findings.

    Returns the full JSON output from Skill Hub's auditor. On failure, returns
    {"error": "..."} so the rest of the auditor can continue.
    """
    if not SKILL_HUB_AUDIT.exists():
        return {"error": f"Skill Hub auditor not found at {SKILL_HUB_AUDIT}"}
    try:
        result = subprocess.run(
            ["python", str(SKILL_HUB_AUDIT), "--json"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return {
                "error": f"Skill Hub auditor exit={result.returncode}",
                "stderr": result.stderr[:500],
            }
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"error": str(e)}


def resolve_supabase_env() -> dict:
    """Load .env from global ~/.claude/.env then Sentinel workspace .env (override).

    Supabase keys live in workspace .env not global; explicit Sentinel-workspace path
    is used because the auditor runs from ~/.claude/scripts/ where Path.cwd() is
    unreliable (cron / Task Scheduler launch from arbitrary cwd).
    """
    sentinel_env = (
        WORKSPACES_PARENT / "Documents" / "Claude Code Workspaces"
        / "4.- Sentinel" / ".env"
    )
    return {
        **load_env(Path.home() / ".claude" / ".env"),
        **load_env(sentinel_env),
    }


def get_supabase_creds(env: dict) -> tuple:
    """Return (url, key) tuple. Tries SERVICE_ROLE_KEY first, falls back to SERVICE_KEY/ANON_KEY."""
    url = env.get("SUPABASE_URL", "")
    key = (
        env.get("SUPABASE_SERVICE_ROLE_KEY", "")
        or env.get("SUPABASE_SERVICE_KEY", "")
        or env.get("SUPABASE_ANON_KEY", "")
    )
    return url, key


def check_session_supabase_delta(supabase_url: str, supabase_key: str) -> list:
    """Drift class: session_supabase_delta.

    For each workspace, scan the most recent session-log topic file and look
    for claims like '- COMPLETE: <task>' or 'shipped <task>' or 'DONE: <task>'.
    Match against Supabase tasks WHERE status IN ('pending','in_progress','blocked').
    Flag any matched task as drift: memory says complete, Supabase says open.

    Returns list of dicts: {workspace, task_text_claim, supabase_task_id,
    supabase_status, evidence_file}.
    """
    import re
    findings = []
    workspaces = [
        ("workforce-hq", "1.- SHARKITECT DIGITAL WORKFORCE HQ"),
        ("skill-management-hub", "3.- Skill Management Hub"),
        ("sentinel", "4.- Sentinel"),
    ]
    claim_patterns = [
        r"^\s*-\s*\*\*COMPLETE\*\*[:\s]",
        r"^\s*-\s*\[x\]\s",
        r"shipped\s+(?:in\s+commit\s+)?[a-f0-9]{7}",
        r"DONE:\s+",
    ]
    pattern_re = re.compile("|".join(claim_patterns), re.IGNORECASE | re.MULTILINE)
    for canonical, path_name in workspaces:
        memory_dir = WORKSPACES_PARENT / "Documents" / "Claude Code Workspaces" / path_name
        memory_files = list(memory_dir.rglob("memory/session_*.md")) if memory_dir.exists() else []
        if not memory_files:
            continue
        # Most recent 3 session files (mtime-sorted)
        recent = sorted(memory_files, key=lambda p: p.stat().st_mtime, reverse=True)[:3]
        # Fetch open tasks for this workspace
        try:
            url = (
                f"{supabase_url}/rest/v1/tasks?"
                f"select=id,task,status&assigned_workspace=eq.{canonical}"
                f"&status=in.(pending,in_progress,blocked)"
            )
            req = urllib.request.Request(
                url,
                headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                open_tasks = json.loads(resp.read())
        except (urllib.error.URLError, json.JSONDecodeError):
            continue
        if not isinstance(open_tasks, list):
            continue
        for memory_file in recent:
            try:
                content_text = memory_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in pattern_re.finditer(content_text):
                line_start = content_text.rfind(chr(10), 0, m.start()) + 1
                line_end = content_text.find(chr(10), m.end())
                line = content_text[line_start:line_end if line_end > 0 else len(content_text)]
                line_lower = line.lower()
                for task in open_tasks:
                    task_text = task.get("task") or ""
                    task_keywords = task_text.lower().split()[:4]
                    if len(task_keywords) >= 2 and all(kw in line_lower for kw in task_keywords[:2]):
                        findings.append({
                            "workspace": canonical,
                            "task_text_claim": line.strip()[:200],
                            "supabase_task_id": task.get("id"),
                            "supabase_task_text": task_text[:200],
                            "supabase_status": task.get("status"),
                            "evidence_file": str(memory_file.relative_to(WORKSPACES_PARENT)),
                        })
    return findings



def main():
    ap = argparse.ArgumentParser(description="Sentinel cross-workspace auditor")
    ap.add_argument("--dry-run", action="store_true", help="log findings, do not route or write Supabase")
    ap.add_argument("--json", action="store_true", help="machine-readable JSON output to stdout")
    ap.add_argument("--source", help="run only one drift source (e.g. asset_registry, coordination_drift)")
    args = ap.parse_args()

    findings: dict = {}

    if not args.source or args.source == "asset_registry":
        findings["asset_registry"] = consume_asset_registry_drift()

    env = resolve_supabase_env()
    sb_url, sb_key = get_supabase_creds(env)

    if not args.source or args.source == "session_supabase_delta":
        if sb_url and sb_key:
            findings["session_supabase_delta"] = check_session_supabase_delta(sb_url, sb_key)
        else:
            findings["session_supabase_delta"] = {"error": "no Supabase credentials"}

    # Tasks 4-8 add: plan_registry_drift, plan_registry_drift, coordination_drift,
    # memory_claim_drift, tier_a_actions, tier_a_drift_fixed_routes,
    # tier_b_audit_finding_routes, tier_c_har_notifications.

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        ar = findings.get("asset_registry", {})
        if "error" in ar:
            print(f"Asset-registry: ERROR {ar['error']}", file=sys.stderr)
        else:
            drift = ar.get("drift", {}) if isinstance(ar, dict) else {}
            total = sum(len(v) if isinstance(v, list) else 0 for v in drift.values())
            print(f"Asset-registry drift: {total} items across {len(drift)} classes")


if __name__ == "__main__":
    main()
