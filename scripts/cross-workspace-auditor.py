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



def check_plan_registry_drift(supabase_url: str, supabase_key: str) -> list:
    """Drift class: plan_registry_drift.

    Parses ~/.claude/docs/plans-registry.md Active Plans table. For each row,
    looks up matching Supabase project by name. Flags mismatches:
      - Registry says Active but Supabase project.status NOT IN ('active','pending')
      - Registry says Active but no Supabase project found at all

    Returns list of dicts: {plan_name, registry_status, supabase_status, owner_workspace}.
    """
    import re
    findings = []
    registry_path = Path.home() / ".claude" / "docs" / "plans-registry.md"
    if not registry_path.exists():
        return [{"error": f"registry not found: {registry_path}"}]
    content = registry_path.read_text(encoding="utf-8")
    # Parse Active Plans section
    active_match = re.search(
        r"## Active Plans(.*?)(?:## Completed Plans|## Tabled|$)",
        content, re.DOTALL,
    )
    if not active_match:
        return findings
    active_section = active_match.group(1)
    # Each row starts with "| [<plan_name>](path) | ..."
    plan_rows = re.findall(r"^\|\s*\[([^\]]+)\]", active_section, re.MULTILINE)
    if not plan_rows:
        return findings
    # Query Supabase projects
    try:
        url = f"{supabase_url}/rest/v1/projects?select=name,status,workspace"
        req = urllib.request.Request(
            url,
            headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            projects = json.loads(resp.read())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        return [{"error": str(e)}]
    if not isinstance(projects, list):
        return findings
    sb_names = {p["name"]: p for p in projects if "name" in p}
    for plan_name in plan_rows:
        slug = plan_name.lower().replace(" ", "-")
        match = sb_names.get(plan_name) or next(
            (p for n, p in sb_names.items() if slug in n.lower()),
            None,
        )
        if not match:
            findings.append({
                "plan_name": plan_name,
                "registry_status": "Active",
                "supabase_status": "MISSING",
                "owner_workspace": "unknown",
            })
        elif match["status"] not in ("active", "pending"):
            findings.append({
                "plan_name": plan_name,
                "registry_status": "Active",
                "supabase_status": match["status"],
                "owner_workspace": match.get("workspace", "unknown"),
            })
    return findings




def check_coordination_drift(supabase_url: str, supabase_key: str) -> list:
    """Drift class: coordination_drift.

    Routed-tasks in cross_workspace_requests with status IN open vocab AND
    created_at > 7 days ago. Returns list of {item_id, assigned_to,
    requested_by, status, days_open, updated_at}.

    Schema (verified 2026-05-12):
      - column is updated_at (NOT last_updated_at)
      - target workspace is assigned_to (NOT routed_to)
      - source workspace is requested_by (NOT source_workspace)
    """
    findings = []
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    try:
        url = (
            f"{supabase_url}/rest/v1/cross_workspace_requests?"
            f"select=item_id,assigned_to,requested_by,status,created_at,updated_at"
            f"&status=in.(pending,in_progress,deferred,blocked)"
            f"&created_at=lt.{urllib.parse.quote(cutoff)}"
        )
        req = urllib.request.Request(
            url,
            headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            rows = json.loads(resp.read())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        return [{"error": str(e)}]
    if not isinstance(rows, list):
        return findings
    now = datetime.now(timezone.utc)
    for r in rows:
        try:
            created = datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
            days_open = (now - created).days
        except (KeyError, ValueError, AttributeError):
            days_open = -1
        findings.append({
            "item_id": r.get("item_id"),
            "workspace": r.get("assigned_to") or "unknown",  # for routing logic in Task 8
            "assigned_to": r.get("assigned_to") or "unknown",
            "requested_by": r.get("requested_by") or "unknown",
            "status": r.get("status"),
            "days_open": days_open,
            "updated_at": r.get("updated_at"),
        })
    return findings


def check_memory_claim_drift(supabase_url: str, supabase_key: str) -> list:
    """Drift class: memory_claim_drift.

    Subset of session_supabase_delta but inverted: workspace MEMORY.md
    (the index file) claims something is COMPLETE/SHIPPED/DONE but
    Supabase has NO matching completed task in the last 7 days.

    Threshold: claim_count > completed_7d + 3 (per plan tuning note).
    First-run severity should be info; tune via empirical observation.

    Returns: [{workspace, claim_count, supabase_completed_7d, delta, evidence_file}]
    """
    import re
    findings = []
    workspaces = [
        ("workforce-hq", "1.- SHARKITECT DIGITAL WORKFORCE HQ"),
        ("skill-management-hub", "3.- Skill Management Hub"),
        ("sentinel", "4.- Sentinel"),
    ]
    claim_re = re.compile(r"(COMPLETE|SHIPPED|DONE|FULLY OPERATIONAL)\b", re.IGNORECASE)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    for canonical, path_name in workspaces:
        memory_dir = WORKSPACES_PARENT / "Documents" / "Claude Code Workspaces" / path_name / "memory"
        if not memory_dir.exists():
            continue
        memory_md = memory_dir / "MEMORY.md"
        if not memory_md.exists():
            continue
        try:
            content_text = memory_md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        # Count Supabase completed tasks in last 7d
        try:
            url = (
                f"{supabase_url}/rest/v1/tasks?select=id"
                f"&assigned_workspace=eq.{canonical}"
                f"&status=eq.completed"
                f"&updated_at=gt.{urllib.parse.quote(cutoff)}"
            )
            req = urllib.request.Request(
                url,
                headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                completed_7d = len(json.loads(resp.read()))
        except (urllib.error.URLError, json.JSONDecodeError):
            completed_7d = -1
        # Count claim lines
        claim_lines = [m.group(0) for line in content_text.splitlines() for m in claim_re.finditer(line)]
        if len(claim_lines) > completed_7d + 3 and completed_7d >= 0:
            findings.append({
                "workspace": canonical,
                "claim_count": len(claim_lines),
                "supabase_completed_7d": completed_7d,
                "delta": len(claim_lines) - completed_7d,
                "evidence_file": str(memory_md.relative_to(WORKSPACES_PARENT)),
            })
    return findings




def normalize_skill_hub_drift(findings: dict) -> None:
    """Normalize Skill Hub's nested asset_registry.drift.* into top-level keys.

    Skill Hub returns:
      asset_registry.drift.rollup.drift_rows -> [{project_name, workspace, ...}]
      asset_registry.drift.stale_visibility_items.items -> [{type, workspace, action_summary,
        hours_overdue, reference_id}] mixed brain_dump + human_action
      asset_registry.drift.task_scheduler / hooks / croncreate / n8n -> lists of asset rows

    Sentinel auditor uses flat top-level keys for routing logic (Tasks 7 + 8).
    Mutates `findings` in place.
    """
    ar = findings.get("asset_registry", {})
    if not isinstance(ar, dict) or not ar:
        return
    drift = ar.get("drift", {})
    if not isinstance(drift, dict) or not drift:
        return
    rollup_block = drift.get("rollup", {})
    if isinstance(rollup_block, dict):
        findings.setdefault("rollup_drift", rollup_block.get("drift_rows", []) or [])
    svi = drift.get("stale_visibility_items", {})
    if isinstance(svi, dict):
        items = svi.get("items", []) or []
        findings.setdefault("overdue_hars", [i for i in items if i.get("type") == "human_action"])
        findings.setdefault("stale_brain_dumps", [i for i in items if i.get("type") == "brain_dump"])
    asset_reg_drift = []
    for asset_class in ("task_scheduler", "hooks", "croncreate", "n8n"):
        block = drift.get(asset_class)
        if isinstance(block, list):
            for item in block:
                if isinstance(item, dict):
                    item_copy = dict(item)
                    item_copy.setdefault("asset_class", asset_class)
                    asset_reg_drift.append(item_copy)
    findings.setdefault("asset_registry_drift", asset_reg_drift)


def act_tier_a_autofix(findings: dict, supabase_url: str, supabase_key: str, dry_run: bool = False) -> list:
    """Tier A -- Sentinel fixes mechanical drift autonomously.

    Drift classes handled:
      - rollup_drift: trigger trg_recompute_project_task_counts via PATCH-touch on a task
      - plan_registry_drift: queue registry rewrite (full markdown-table parse deferred to v2)

    Each successful action returns: {action_taken, audit_class, target_workspace, evidence}.
    Failures return action_taken in {recompute_failed, registry_correction_queued}.
    """
    actions = []
    # --- 1. Rollup drift autofix ---
    for finding in findings.get("rollup_drift", []) or []:
        if not isinstance(finding, dict):
            continue
        project_name = finding.get("project_name")
        target_workspace = finding.get("workspace") or "unknown"
        if not project_name:
            continue
        if dry_run:
            actions.append({
                "action_taken": "would_recompute_rollup",
                "audit_class": "rollup_drift",
                "target_workspace": target_workspace,
                "evidence": finding,
                "dry_run": True,
            })
            continue
        # Look up project_id by name, then touch one of its tasks to fire the recompute trigger
        try:
            proj_url = (
                f"{supabase_url}/rest/v1/projects?"
                f"select=id&name=eq.{urllib.parse.quote(project_name)}&limit=1"
            )
            req = urllib.request.Request(
                proj_url,
                headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                proj_rows = json.loads(resp.read())
            if not proj_rows:
                actions.append({
                    "action_taken": "recompute_failed",
                    "audit_class": "rollup_drift",
                    "target_workspace": target_workspace,
                    "evidence": finding,
                    "error": f"project name not found: {project_name}",
                })
                continue
            project_id = proj_rows[0]["id"]
            # Touch any task in the project (no semantic change; trigger fires on UPDATE)
            task_url = f"{supabase_url}/rest/v1/tasks?project_id=eq.{project_id}&limit=1"
            req = urllib.request.Request(
                task_url,
                headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                task_rows = json.loads(resp.read())
            if not task_rows:
                # No tasks -- recompute can't be triggered via task touch. Skip.
                actions.append({
                    "action_taken": "recompute_skipped_no_tasks",
                    "audit_class": "rollup_drift",
                    "target_workspace": target_workspace,
                    "evidence": finding,
                    "note": "project has no tasks; rollup will be 0/0 after manual recompute",
                })
                continue
            task_id = task_rows[0]["id"]
            patch_url = f"{supabase_url}/rest/v1/tasks?id=eq.{task_id}"
            patch_body = json.dumps({
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).encode("utf-8")
            patch_req = urllib.request.Request(
                patch_url,
                data=patch_body,
                headers={
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                method="PATCH",
            )
            urllib.request.urlopen(patch_req, timeout=15)
            actions.append({
                "action_taken": "recomputed_rollup_via_trigger",
                "audit_class": "rollup_drift",
                "target_workspace": target_workspace,
                "evidence": finding,
            })
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            actions.append({
                "action_taken": "recompute_failed",
                "audit_class": "rollup_drift",
                "target_workspace": target_workspace,
                "evidence": finding,
                "error": str(e),
            })

    # --- 2. Plan-registry drift autofix ---
    # Concrete rewrite is deferred to Topic 2 v2 (full markdown-table parse + atomic write).
    # v1 flags the surgical edit needed and surfaces it in the drift_fixed_notification.
    for finding in findings.get("plan_registry_drift", []) or []:
        if not isinstance(finding, dict):
            continue
        plan_name = finding.get("plan_name")
        sb_status = finding.get("supabase_status")
        target_workspace = finding.get("owner_workspace") or "unknown"
        if dry_run:
            actions.append({
                "action_taken": "would_correct_registry",
                "audit_class": "plan_registry_drift",
                "target_workspace": target_workspace,
                "evidence": finding,
                "dry_run": True,
            })
        else:
            actions.append({
                "action_taken": "registry_correction_queued",
                "audit_class": "plan_registry_drift",
                "target_workspace": target_workspace,
                "evidence": finding,
                "note": (
                    f"Manual rewrite needed: registry says Active, "
                    f"Supabase says '{sb_status}' for plan '{plan_name}'"
                ),
            })

    return actions


def send_har_slack(findings: dict, dry_run: bool = False) -> list:
    """Tier C -- Send Slack notification to user for each overdue HAR.

    Reads from findings["overdue_hars"] (populated by normalize_skill_hub_drift).
    Uses workspace tools/slack-send.py with --har-json. Subprocess invocation
    is captured to surface returncode + stdout in findings JSON for debugging.

    Returns: [{action_taken, har_reference_id, workspace, hours_overdue, returncode}]
    """
    actions = []
    har_list = findings.get("overdue_hars", []) or []
    if not har_list:
        return actions
    sentinel_root = (
        WORKSPACES_PARENT / "Documents" / "Claude Code Workspaces" / "4.- Sentinel"
    )
    slack_send_path = sentinel_root / "tools" / "slack-send.py"
    for har in har_list:
        if not isinstance(har, dict):
            continue
        ref_id = har.get("reference_id", "(no ref)")
        workspace = har.get("workspace", "unknown")
        hours = har.get("hours_overdue") or 0
        if dry_run:
            actions.append({
                "action_taken": "would_send_har_slack",
                "har_reference_id": ref_id,
                "workspace": workspace,
                "hours_overdue": hours,
                "dry_run": True,
            })
            continue
        if not slack_send_path.exists():
            actions.append({
                "action_taken": "har_slack_failed",
                "har_reference_id": ref_id,
                "workspace": workspace,
                "error": f"slack-send.py not found at {slack_send_path}",
            })
            continue
        # Write HAR to temp JSON, invoke slack-send.py --har-json
        import tempfile
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
                json.dump(har, tf)
                tf_path = tf.name
            try:
                result = subprocess.run(
                    ["python", str(slack_send_path), "--har-json", tf_path],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(sentinel_root),  # so workspace .env is read for SLACK_SENTINEL_AUDIT_REPORTS_CHANNEL
                )
                actions.append({
                    "action_taken": "sent_har_slack" if result.returncode == 0 else "har_slack_failed",
                    "har_reference_id": ref_id,
                    "workspace": workspace,
                    "hours_overdue": hours,
                    "returncode": result.returncode,
                    "stdout": result.stdout.strip()[:200],
                    "stderr": result.stderr.strip()[:200] if result.returncode != 0 else "",
                })
            finally:
                Path(tf_path).unlink(missing_ok=True)
        except (subprocess.TimeoutExpired, OSError) as e:
            actions.append({
                "action_taken": "har_slack_failed",
                "har_reference_id": ref_id,
                "workspace": workspace,
                "error": str(e),
            })
    return actions




WORKSPACE_INBOXES = {
    "workforce-hq": (
        WORKSPACES_PARENT / "Documents" / "Claude Code Workspaces"
        / "1.- SHARKITECT DIGITAL WORKFORCE HQ" / ".routed-tasks" / "inbox"
    ),
    "skill-management-hub": (
        WORKSPACES_PARENT / "Documents" / "Claude Code Workspaces"
        / "3.- Skill Management Hub" / ".work-requests" / "inbox"
    ),
    "sentinel": (
        WORKSPACES_PARENT / "Documents" / "Claude Code Workspaces"
        / "4.- Sentinel" / ".routed-tasks" / "inbox"
    ),
}

# Tier B drift classes -- routed as audit_finding (requires workspace judgment)
TIER_B_CLASSES = {
    "asset_registry_drift",
    "session_supabase_delta",
    "coordination_drift",
    "memory_claim_drift",
    "stale_brain_dumps",
    "wr_id_consistency",
}

# Tier A drift classes -- Sentinel autofixed in Task 7; route drift_fixed_notification
TIER_A_CLASSES = {
    "rollup_drift",
    "plan_registry_drift",
}

# Successful Tier A action types (used to filter actions worth notifying about)
TIER_A_SUCCESS_ACTIONS = {
    "recomputed_rollup_via_trigger",
    "registry_corrected",
}


def route_tier_a_notifications(tier_a_actions: list, dry_run: bool = False) -> list:
    """Tier A -- After Sentinel autofixes drift, route drift_fixed_notification
    to the owning workspace so they ack at next session start.

    Returns list of {target, path, audit_class, action_count}.
    Skips actions that didn't succeed or are targeted at sentinel itself.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sentinel_inbox = WORKSPACE_INBOXES["sentinel"]
    routed = []
    grouped = {}
    for action in tier_a_actions or []:
        if not isinstance(action, dict):
            continue
        if action.get("dry_run"):
            continue
        if action.get("action_taken") not in TIER_A_SUCCESS_ACTIONS:
            continue
        target = action.get("target_workspace")
        audit_class = action.get("audit_class")
        if not target or target == "sentinel" or target == "unknown" or not audit_class:
            continue
        grouped.setdefault((target, audit_class), []).append(action)

    lesson_hints = {
        "rollup_drift": (
            "When tasks change status, ensure update-project-status.py is used "
            "(it touches updated_at and fires the recompute trigger). Direct Supabase "
            "writes that bypass the script can leave projects.total_tasks/completed_tasks stale."
        ),
        "plan_registry_drift": (
            "When a plan's Supabase project status changes (paused/blocked/complete), "
            "update ~/.claude/docs/plans-registry.md in the same change. Supabase is SoT; "
            "the registry is the human-readable mirror."
        ),
    }

    for (target, audit_class), actions in grouped.items():
        slug = audit_class.replace("_", "-")[:40]
        task_id = f"rt-sentinel-{today}-drift-fixed-{slug}-{target[:8]}"
        inbox = WORKSPACE_INBOXES.get(target)
        if not inbox or not inbox.exists():
            continue
        path = inbox / f"{task_id}.json"
        body = {
            "id": task_id,
            "id_format_version": 2,
            "source_workspace": "sentinel",
            "routed_to": target,
            "routed_date": today,
            "priority": "low",
            "severity": "info",
            "status": "pending",
            "kind": "drift_fixed_notification",
            "task_summary": (
                f"Sentinel autofixed {len(actions)} {audit_class} drift item(s) "
                f"affecting your workspace"
            ),
            "what_was_drifted": f"{audit_class}: see evidence array",
            "what_sentinel_did": [a.get("action_taken") for a in actions],
            "lesson_learned": lesson_hints.get(
                audit_class,
                "See evidence; consider updating session-end checklist to prevent recurrence.",
            ),
            "evidence": [a.get("evidence") for a in actions],
            "fix_instructions": (
                "Acknowledge by closing this RT with --status processed. "
                "Optionally update your session-end checklist or feedback memory "
                "using lesson_learned hint."
            ),
            "notify_on_completion": False,  # Tier A is fire-and-forget; ack closure is enough
        }
        entry = {
            "target": target,
            "path": str(path),
            "audit_class": audit_class,
            "action_count": len(actions),
        }
        if dry_run:
            entry["dry_run"] = True
        else:
            path.write_text(json.dumps(body, indent=2), encoding="utf-8")
        routed.append(entry)
    return routed


def route_tier_b_findings(findings: dict, dry_run: bool = False) -> list:
    """Tier B -- Route audit_finding tasks for drift classes that need workspace judgment.

    Routed-task schema includes audit_finding:true so Skill Hub's hard-stop hook
    can detect and gate AI-autonomous tool calls in receiving workspaces.

    Returns list of {target, path, audit_class, finding_count}.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sentinel_inbox = WORKSPACE_INBOXES["sentinel"]
    routed = []
    grouped = {}

    for audit_class, items in findings.items():
        if audit_class not in TIER_B_CLASSES:
            continue
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            target = (
                item.get("workspace")
                or item.get("assigned_to")
                or item.get("owner_workspace")
            )
            if not target or target == "sentinel" or target == "unknown":
                continue
            grouped.setdefault((target, audit_class), []).append(item)

    for (target, audit_class), items in grouped.items():
        slug = audit_class.replace("_", "-")[:40]
        task_id = f"rt-sentinel-{today}-audit-{slug}-{target[:8]}"
        inbox = WORKSPACE_INBOXES.get(target)
        if not inbox or not inbox.exists():
            continue
        path = inbox / f"{task_id}.json"
        body = {
            "id": task_id,
            "id_format_version": 2,
            "source_workspace": "sentinel",
            "routed_to": target,
            "routed_date": today,
            "priority": "high",
            "severity": "warning",
            "status": "pending",
            "kind": "audit_finding",
            "audit_finding": True,
            "audit_class": audit_class,
            "audit_finding_severity": "warning",
            "task_summary": (
                f"Audit finding: {len(items)} {audit_class} item(s) detected in {target}"
            ),
            "context": (
                f"Cross-workspace-auditor run {today} found drift in {audit_class}. "
                f"See evidence array for specifics."
            ),
            "fix_instructions": (
                "Review each item in evidence array. For each, either: "
                "(a) take corrective action (update Supabase, close inbox item, etc.) "
                "and close this RT, or (b) reject with --status rejected if the finding is invalid."
            ),
            "evidence": items,
            "notify_on_completion": True,
            "notify_inbox_path": str(sentinel_inbox),
            "notification_filename_hint": f"rt-{target[:8]}-{today}-{slug}-completed.json",
        }
        entry = {
            "target": target,
            "path": str(path),
            "audit_class": audit_class,
            "finding_count": len(items),
        }
        if dry_run:
            entry["dry_run"] = True
        else:
            path.write_text(json.dumps(body, indent=2), encoding="utf-8")
        routed.append(entry)
    return routed




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

    if not args.source or args.source == "plan_registry_drift":
        if sb_url and sb_key:
            findings["plan_registry_drift"] = check_plan_registry_drift(sb_url, sb_key)
        else:
            findings["plan_registry_drift"] = {"error": "no Supabase credentials"}

    if not args.source or args.source == "coordination_drift":
        if sb_url and sb_key:
            findings["coordination_drift"] = check_coordination_drift(sb_url, sb_key)
        else:
            findings["coordination_drift"] = {"error": "no Supabase credentials"}

    if not args.source or args.source == "memory_claim_drift":
        if sb_url and sb_key:
            findings["memory_claim_drift"] = check_memory_claim_drift(sb_url, sb_key)
        else:
            findings["memory_claim_drift"] = {"error": "no Supabase credentials"}

    # Normalize Skill Hub drift into top-level keys for Tier A/B/C consumers
    normalize_skill_hub_drift(findings)

    if not args.source or args.source == "tier_a":
        if sb_url and sb_key:
            findings["tier_a_actions"] = act_tier_a_autofix(
                findings, sb_url, sb_key, dry_run=args.dry_run
            )
        else:
            findings["tier_a_actions"] = {"error": "no Supabase credentials"}

    if not args.source or args.source == "tier_c":
        findings["tier_c_har_notifications"] = send_har_slack(
            findings, dry_run=args.dry_run
        )

    if not args.source or args.source in ("tier_a_routes", "routes"):
        findings["tier_a_drift_fixed_routes"] = route_tier_a_notifications(
            findings.get("tier_a_actions", []) if isinstance(findings.get("tier_a_actions"), list) else [],
            dry_run=args.dry_run,
        )

    if not args.source or args.source in ("tier_b_routes", "routes"):
        findings["tier_b_audit_finding_routes"] = route_tier_b_findings(
            findings, dry_run=args.dry_run
        )

    # Auditor pipeline complete; Tasks 9-13 add tests + scheduling + verification., plan_registry_drift, coordination_drift,
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
