"""
update-project-status.py -- Update Supabase project/task status

Called during session-checkpoint and during active work to sync project and
task statuses with Supabase. The AI provides what changed; this script pushes.

Usage:
    python update-project-status.py project <name> <status> [--phase <phase>] [--notes <notes>]
    python update-project-status.py task <task-text> <status> [--project <project>] [--notes <notes>]
    python update-project-status.py add-task <task-text> --project <project> --workspace <ws> [--priority <p>] [--depends-on <id1,id2>]
    python update-project-status.py add-dependency <task-text> --depends-on <blocker-task-text>
    python update-project-status.py check-blockers --workspace <workspace>
    python update-project-status.py my-tasks --workspace <workspace>
    python update-project-status.py recalc-carried-days
    python update-project-status.py list-projects [--status <status>]
    python update-project-status.py list-tasks [--project <project>] [--status <status>]
    python update-project-status.py rollup [--project <name>]
    python update-project-status.py table <project-name> [--days <30-45>]

Statuses:
    Projects: active, paused, complete, blocked, pending, tabled
    Tasks:    pending, in_progress, completed, blocked, deferred, tabled

Automatic cascades:
    - Project set to 'paused': all non-completed tasks drop to low priority
    - Project set to 'tabled': all non-completed tasks set to tabled + review_date, priority=low
    - Task set to 'completed': if last task for project, auto-complete project
    - recalc-carried-days: sets carried_days = days since created_at for all active tasks (excludes tabled)

Dependencies: Python stdlib only (urllib, json, os)
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_env():
    """Load .env searching up from CWD, then from script location."""
    def _try_load(start):
        search = start
        for _ in range(5):
            env_file = search / ".env"
            if env_file.exists():
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
                return True
            search = search.parent
        return False

    if _try_load(Path.cwd()):
        return
    _try_load(Path(__file__).resolve().parent.parent)


def get_config():
    load_env()
    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    api_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not base_url or not api_key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        sys.exit(1)
    return base_url, api_key


# ---------------------------------------------------------------------------
# Workspace detection (for last_updated_by audit trail)
# ---------------------------------------------------------------------------

_WORKSPACE_MAP = {
    "1.- sharkitect digital workforce hq": "workforce-hq",
    "3.- skill management hub": "skill-management-hub",
    "4.- sentinel": "sentinel",
}


def _detect_workspace():
    """Detect current workspace from CWD path. Returns canonical name."""
    cwd = Path.cwd().resolve()
    for part in cwd.parts:
        key = part.lower()
        if key in _WORKSPACE_MAP:
            return _WORKSPACE_MAP[key]
    return "unknown"


_CURRENT_WORKSPACE = _detect_workspace()


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _headers(api_key, prefer=None):
    h = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _get(base_url, api_key, path):
    url = f"{base_url}/rest/v1/{path}"
    req = urllib.request.Request(url, headers=_headers(api_key))
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"ERROR GET {path}: {e}")
        return []


def _patch(base_url, api_key, path, data):
    url = f"{base_url}/rest/v1/{path}"
    # Auto-inject audit trail on every write
    data.setdefault("last_updated_by", _CURRENT_WORKSPACE)
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers=_headers(api_key, prefer="return=representation"),
        method="PATCH"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result[0] if isinstance(result, list) and result else result
    except Exception as e:
        print(f"ERROR PATCH {path}: {e}")
        return None


def _post(base_url, api_key, path, data):
    url = f"{base_url}/rest/v1/{path}"
    # Auto-inject audit trail on every write
    data.setdefault("last_updated_by", _CURRENT_WORKSPACE)
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers=_headers(api_key, prefer="return=representation"),
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result[0] if isinstance(result, list) and result else result
    except Exception as e:
        print(f"ERROR POST {path}: {e}")
        return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _cascade_priority_on_pause(base_url, api_key, project_name):
    """When a project is paused, drop all its non-completed tasks to low priority."""
    encoded = urllib.parse.quote(project_name)
    tasks = _get(
        base_url, api_key,
        f"tasks?project=ilike.{encoded}&status=not.in.(completed,deferred)&select=id,task,priority"
    )
    if not tasks:
        print("  No active tasks to deprioritize.")
        return

    updated = 0
    for task in tasks:
        if task.get("priority") == "low":
            continue
        result = _patch(base_url, api_key, f"tasks?id=eq.{task['id']}", {
            "priority": "low",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        if result:
            updated += 1
    print(f"  CASCADE: {updated} task(s) dropped to low priority (project paused).")


def _cascade_table_project(base_url, api_key, project_name, review_date=None):
    """When a project is tabled, set all non-completed tasks to tabled + review_date."""
    encoded = urllib.parse.quote(project_name)
    tasks = _get(
        base_url, api_key,
        f"tasks?project=ilike.{encoded}&status=not.in.(completed)&select=id,task,status"
    )
    if not tasks:
        print("  No active tasks to table.")
        return

    update_data = {
        "status": "tabled",
        "priority": "low",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if review_date:
        update_data["review_date"] = review_date

    updated = 0
    for task in tasks:
        result = _patch(base_url, api_key, f"tasks?id=eq.{task['id']}", update_data)
        if result:
            updated += 1
    print(f"  CASCADE: {updated} task(s) set to tabled (review: {review_date or 'not set'}).")


def update_project(base_url, api_key, name, status, phase=None, notes=None, review_date=None):
    """Update a project's status by name."""
    valid = ["active", "paused", "complete", "blocked", "pending", "tabled"]
    if status not in valid:
        print(f"ERROR: Invalid project status '{status}'. Valid: {', '.join(valid)}")
        return False

    # Find project by name (case-insensitive via ilike)
    encoded_name = urllib.parse.quote(name)
    projects = _get(base_url, api_key, f"projects?name=ilike.{encoded_name}&select=id,name,status,current_phase")

    if not projects:
        # Try partial match
        projects = _get(base_url, api_key, f"projects?name=ilike.*{encoded_name}*&select=id,name,status,current_phase")

    if not projects:
        print(f"ERROR: No project found matching '{name}'")
        return False

    if len(projects) > 1:
        print(f"WARNING: Multiple projects match '{name}':")
        for p in projects:
            print(f"  - {p['name']} (status: {p['status']})")
        print("Using first match.")

    project = projects[0]
    old_status = project.get("status", "unknown")

    data = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if phase:
        data["current_phase"] = phase
    if notes:
        data["phase_description"] = notes
    if status == "complete":
        data["health"] = "on_track"
    if review_date:
        data["review_date"] = review_date

    result = _patch(base_url, api_key, f"projects?id=eq.{project['id']}", data)
    if result:
        print(f"UPDATED: {project['name']}: {old_status} -> {status}")
        if phase:
            print(f"  Phase: {phase}")

        # Auto-cascade: when project is paused, drop all its active tasks to low priority
        if status == "paused":
            _cascade_priority_on_pause(base_url, api_key, project['name'])

        # Auto-cascade: when project is tabled, set all tasks to tabled + review_date
        if status == "tabled":
            _cascade_table_project(base_url, api_key, project['name'], review_date)

        return True
    return False


def update_task(base_url, api_key, task_text, status, project=None, notes=None):
    """Update a task's status by matching task text."""
    valid = ["pending", "in_progress", "completed", "blocked", "deferred", "tabled"]
    if status not in valid:
        print(f"ERROR: Invalid task status '{status}'. Valid: {', '.join(valid)}")
        return False

    # Build query
    encoded = urllib.parse.quote(task_text)
    query = f"tasks?task=ilike.*{encoded}*&select=id,task,status,project"
    if project:
        encoded_proj = urllib.parse.quote(project)
        query += f"&project=ilike.*{encoded_proj}*"
    query += "&limit=5"

    tasks = _get(base_url, api_key, query)

    if not tasks:
        print(f"ERROR: No task found matching '{task_text}'")
        return False

    if len(tasks) > 1:
        print(f"WARNING: Multiple tasks match '{task_text}':")
        for t in tasks:
            print(f"  - [{t.get('project', '?')}] {t['task'][:60]} (status: {t['status']})")
        print("Using first match.")

    task = tasks[0]
    old_status = task.get("status", "unknown")

    data = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if notes:
        data["notes"] = notes
    if status == "completed":
        data["completed_at"] = datetime.now(timezone.utc).isoformat()

    result = _patch(base_url, api_key, f"tasks?id=eq.{task['id']}", data)
    if result:
        print(f"UPDATED: [{task.get('project', '?')}] {task['task'][:60]}: {old_status} -> {status}")

        # Auto-complete project when last task finishes
        if status == "completed" and task.get("project"):
            _check_auto_complete_project(base_url, api_key, task["project"])

        # Check if anything in cross_workspace_requests is blocked by this task
        if status == "completed":
            _check_downstream_blockers(base_url, api_key, task["id"])

        return True
    return False


def _check_downstream_blockers(base_url, api_key, completed_task_id):
    """Check if any cross_workspace_requests are blocked by this completed task.
    Prints a reminder to notify the blocked workspace."""
    blocked_items = _get(
        base_url, api_key,
        f"cross_workspace_requests?blocked_by=eq.{completed_task_id}"
        f"&status=eq.blocked&select=id,summary,assigned_to"
    )
    if blocked_items:
        print(f"  BLOCKER CLEARED: {len(blocked_items)} downstream item(s) were blocked by this task:")
        for item in blocked_items:
            print(
                f"    - [{item.get('assigned_to', '?')}] "
                f"{str(item.get('summary', ''))[:60]}"
            )
        print(
            "  ACTION REQUIRED: Add blocker_cleared_notes to the blocked "
            "workspace's inbox item per Blocker-Cleared Notification Protocol."
        )


def _check_auto_complete_project(base_url, api_key, project_name):
    """If all tasks for a project are completed, auto-complete the project."""
    encoded = urllib.parse.quote(project_name)
    remaining = _get(
        base_url, api_key,
        f"tasks?project=ilike.{encoded}&status=neq.completed&select=id"
    )
    if not remaining:
        # All tasks done -- check if project is already complete
        projects = _get(
            base_url, api_key,
            f"projects?name=ilike.{encoded}&select=id,name,status"
        )
        if projects and projects[0].get("status") != "complete":
            result = _patch(base_url, api_key, f"projects?id=eq.{projects[0]['id']}", {
                "status": "complete",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "health": "on_track",
            })
            if result:
                print(f"  AUTO-COMPLETE: Project '{project_name}' -- all tasks done.")


def recalc_carried_days(base_url, api_key):
    """Recalculate carried_days for ALL non-completed tasks.

    Sets carried_days = days since created_at for every task that is not
    completed. This includes paused and deferred tasks so we can track
    how long items have been sitting (for stale review triggers).
    Called at session start (FULL_STARTUP).

    CEO briefs should filter which statuses to show in CARRY-FORWARD
    at query time, not here. We track everything; briefs display selectively.

    Stale review threshold: tasks paused or deferred for 30+ days get
    flagged in output so the session can surface them for review.
    """
    STALE_REVIEW_DAYS = 30

    # Get ALL non-completed tasks (active, in_progress, blocked, paused, deferred)
    tasks = _get(
        base_url, api_key,
        "tasks?status=neq.completed&select=id,task,status,created_at,carried_days,project"
    )
    if not tasks:
        print("CARRIED DAYS: No non-completed tasks to update.")
        return

    today = datetime.now(timezone.utc).date()
    updated = 0
    stale_review = []
    for task in tasks:
        created_str = task.get("created_at", "")
        if not created_str:
            continue
        # Parse ISO date (handle both datetime and date-only formats)
        try:
            created_date = datetime.fromisoformat(created_str.replace("Z", "+00:00")).date()
        except (ValueError, AttributeError):
            continue

        days = (today - created_date).days
        if days < 0:
            days = 0
        old_days = task.get("carried_days", 0) or 0

        if days != old_days:
            result = _patch(base_url, api_key, f"tasks?id=eq.{task['id']}", {
                "carried_days": days,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            if result:
                updated += 1

        # Flag paused/deferred tasks that exceed stale review threshold
        if task.get("status") in ("paused", "deferred") and days >= STALE_REVIEW_DAYS:
            stale_review.append(task)

    print(f"CARRIED DAYS: {updated} task(s) updated out of {len(tasks)} non-completed tasks.")

    if stale_review:
        print(f"STALE REVIEW: {len(stale_review)} paused/deferred task(s) exceed {STALE_REVIEW_DAYS} days:")
        for t in stale_review:
            days = (today - datetime.fromisoformat(
                t["created_at"].replace("Z", "+00:00")
            ).date()).days
            print(f"  [{t.get('status')}] [{t.get('project', '?')}] "
                  f"{t.get('task', '?')[:50]} -- {days} days")
        print("  ACTION: Review each -- reactivate, keep (reset counter), or delete.")


def list_projects(base_url, api_key, status_filter=None):
    """List projects, optionally filtered by status."""
    query = "projects?select=name,status,current_phase,priority,workspace&order=queue_position.asc.nullslast"
    if status_filter:
        query += f"&status=eq.{status_filter}"

    projects = _get(base_url, api_key, query)
    if not projects:
        print("No projects found.")
        return

    print(f"{'Name':<35} {'Status':<10} {'Phase':<25} {'Priority':<8}")
    print("-" * 80)
    for p in projects:
        print(f"{p.get('name','?'):<35} {p.get('status','?'):<10} {str(p.get('current_phase','')):<25} {p.get('priority','?'):<8}")


def list_tasks(base_url, api_key, project_filter=None, status_filter=None):
    """List tasks, optionally filtered."""
    query = "tasks?select=task,status,project,priority&order=created_at.desc&limit=30"
    if project_filter:
        encoded = urllib.parse.quote(project_filter)
        query += f"&project=ilike.*{encoded}*"
    if status_filter:
        query += f"&status=eq.{status_filter}"

    tasks = _get(base_url, api_key, query)
    if not tasks:
        print("No tasks found.")
        return

    print(f"{'Project':<20} {'Task':<40} {'Status':<12} {'Priority':<8}")
    print("-" * 82)
    for t in tasks:
        print(f"{str(t.get('project','?')):<20} {str(t.get('task','?'))[:39]:<40} {t.get('status','?'):<12} {t.get('priority','?'):<8}")


# ---------------------------------------------------------------------------
# Cross-workspace task tracking commands
# ---------------------------------------------------------------------------

def _resolve_project_id(base_url, api_key, project_name):
    """Resolve a project name to its UUID. Returns (id, matched_name) or (None, None)."""
    encoded = urllib.parse.quote(project_name)
    # Exact match first
    projects = _get(base_url, api_key,
                    f"projects?name=ilike.{encoded}&select=id,name")
    if projects:
        return projects[0]["id"], projects[0]["name"]
    # Partial match
    projects = _get(base_url, api_key,
                    f"projects?name=ilike.*{encoded}*&select=id,name")
    if projects:
        return projects[0]["id"], projects[0]["name"]
    return None, None


def _validate_workspace(workspace):
    """Validate workspace is a canonical name. Exits on invalid."""
    CANONICAL = {"workforce-hq", "skill-management-hub", "sentinel", "global"}
    if workspace and workspace.lower() not in CANONICAL:
        print(
            f"ERROR: '{workspace}' is not a canonical workspace name. "
            f"Valid: {', '.join(sorted(CANONICAL))}. "
            f"No aliases or abbreviations.",
            file=sys.stderr,
        )
        sys.exit(1)
    return workspace.lower() if workspace else workspace


def add_task(base_url, api_key, task_text, project, workspace, priority="medium",
             depends_on=None):
    """Create a new task in Supabase."""
    workspace = _validate_workspace(workspace)
    # Resolve project name to project_id FK
    project_id, matched_name = _resolve_project_id(base_url, api_key, project)
    if project_id:
        project = matched_name  # Use canonical name from projects table

    data = {
        "task": task_text,
        "project": project,
        "project_id": project_id,
        "assigned_workspace": workspace,
        "priority": priority,
        "status": "pending",
        "source": "claude_code",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "carried_days": 0,
        "depends_on": depends_on or [],
    }
    result = _post(base_url, api_key, "tasks", data)
    if result:
        task_id = result.get("id", "?")
        print(f"CREATED: [{project}] {task_text[:60]}")
        print(f"  ID: {task_id}")
        print(f"  Workspace: {workspace} | Priority: {priority}")
        if project_id:
            print(f"  Project FK: {project_id[:8]}...")
        else:
            print(f"  WARNING: No project match found for '{project}' -- project_id is NULL")
        if depends_on:
            print(f"  Depends on: {len(depends_on)} task(s)")
        return True
    return False


VALID_PROJECT_CATEGORIES = {"formal", "idea", "tabled"}
VALID_PROJECT_STATUSES = {"active", "pending", "paused", "blocked", "tabled", "complete", "completed"}


def add_project(base_url, api_key, name, workspace, status="pending",
                priority="medium", phase=None, phase_description=None,
                category="formal", total_phases=None, target_date=None,
                idempotent=False):
    """
    Create a new project in Supabase.
    Filed by: Sentinel wr-2026-04-19-003 (script lacked add-project subcommand;
    forced direct Supabase MCP INSERT with check-constraint round-trips).

    Validates category against allowed set BEFORE submitting to avoid the
    operational->formal round-trip Sentinel hit. Validates workspace against
    canonical names. Returns the created (or matched, if --idempotent) project
    UUID for downstream add-task --depends-on chaining.
    """
    workspace = _validate_workspace(workspace)
    if category not in VALID_PROJECT_CATEGORIES:
        print(f"ERROR: Invalid category '{category}'. "
              f"Must be one of: {sorted(VALID_PROJECT_CATEGORIES)}")
        return False
    if status not in VALID_PROJECT_STATUSES:
        print(f"ERROR: Invalid status '{status}'. "
              f"Must be one of: {sorted(VALID_PROJECT_STATUSES)}")
        return False

    # Idempotent check: does a project with this name already exist?
    encoded = urllib.parse.quote(name)
    existing = _get(base_url, api_key,
                    f"projects?name=ilike.{encoded}&select=id,name,status&limit=1")
    if existing:
        if idempotent:
            row = existing[0]
            print(f"EXISTS (idempotent): [{row['name']}] status={row['status']}")
            print(f"  ID: {row['id']}")
            return True
        print(f"ERROR: Project '{name}' already exists "
              f"(id={existing[0]['id']}). Use --idempotent to no-op on duplicates.")
        return False

    now = datetime.now(timezone.utc).isoformat()
    data = {
        "name": name,
        "status": status,
        "priority": priority,
        "category": category,
        "workspace": workspace,
        "last_updated_by": workspace,
        "created_at": now,
        "updated_at": now,
    }
    if phase:
        data["current_phase"] = phase
    if phase_description:
        data["phase_description"] = phase_description
    if total_phases is not None:
        data["total_phases"] = int(total_phases)
    if target_date:
        data["target_date"] = target_date

    result = _post(base_url, api_key, "projects", data)
    if result:
        proj_id = result.get("id", "?")
        print(f"CREATED PROJECT: [{name}]")
        print(f"  ID: {proj_id}")
        print(f"  Workspace: {workspace} | Status: {status} | "
              f"Priority: {priority} | Category: {category}")
        if phase:
            print(f"  Phase: {phase}{f' -- {phase_description}' if phase_description else ''}")
        return True
    return False


def add_dependency(base_url, api_key, task_text, blocker_text):
    """Add a dependency: task_text depends on blocker_text completing first."""
    # Find the dependent task
    encoded = urllib.parse.quote(task_text)
    tasks = _get(base_url, api_key,
                 f"tasks?task=ilike.*{encoded}*&select=id,task,depends_on&limit=5")
    if not tasks:
        print(f"ERROR: No task found matching '{task_text}'")
        return False
    task = tasks[0]

    # Find the blocker task
    encoded_b = urllib.parse.quote(blocker_text)
    blockers = _get(base_url, api_key,
                    f"tasks?task=ilike.*{encoded_b}*&select=id,task&limit=5")
    if not blockers:
        print(f"ERROR: No blocker task found matching '{blocker_text}'")
        return False
    blocker = blockers[0]

    # Append blocker ID to depends_on
    current_deps = task.get("depends_on") or []
    blocker_id = blocker["id"]
    if blocker_id in current_deps:
        print(f"SKIP: '{task['task'][:40]}' already depends on '{blocker['task'][:40]}'")
        return True

    current_deps.append(blocker_id)
    result = _patch(base_url, api_key, f"tasks?id=eq.{task['id']}", {
        "depends_on": current_deps,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    if result:
        print(f"DEPENDENCY ADDED:")
        print(f"  '{task['task'][:50]}' now depends on")
        print(f"  '{blocker['task'][:50]}' (ID: {blocker_id[:8]}...)")
        return True
    return False


def check_blockers(base_url, api_key, workspace):
    """Check if any tasks for this workspace have cleared blockers."""
    workspace = _validate_workspace(workspace)
    # Get tasks with dependencies that are pending or blocked
    encoded_ws = urllib.parse.quote(workspace)
    tasks = _get(
        base_url, api_key,
        f"tasks?assigned_workspace=eq.{encoded_ws}"
        f"&status=in.(pending,blocked)"
        f"&select=id,task,project,depends_on,status"
    )

    # Filter to tasks that actually have dependencies
    dep_tasks = [t for t in tasks if t.get("depends_on") and len(t["depends_on"]) > 0]

    if not dep_tasks:
        print(f"No tasks with dependencies for workspace '{workspace}'.")
        return

    # Collect all dependency IDs we need to check
    all_dep_ids = set()
    for t in dep_tasks:
        for dep_id in t["depends_on"]:
            all_dep_ids.add(dep_id)

    # Batch-fetch all dependency tasks
    dep_statuses = {}
    for dep_id in all_dep_ids:
        results = _get(base_url, api_key,
                       f"tasks?id=eq.{dep_id}&select=id,task,status,assigned_workspace")
        if results:
            dep_statuses[dep_id] = results[0]

    cleared = []
    still_blocked = []

    for t in dep_tasks:
        deps = t["depends_on"]
        completed_deps = []
        pending_deps = []

        for dep_id in deps:
            dep = dep_statuses.get(dep_id)
            if dep and dep.get("status") == "completed":
                completed_deps.append(dep)
            else:
                pending_deps.append(dep or {"id": dep_id, "task": "unknown", "status": "?"})

        if not pending_deps:
            cleared.append({"task": t, "completed_deps": completed_deps})
        else:
            still_blocked.append({"task": t, "pending_deps": pending_deps,
                                  "completed_deps": completed_deps})

    if cleared:
        print("BLOCKERS CLEARED:")
        for item in cleared:
            t = item["task"]
            print(f"  [{t.get('project', '?')}] {t['task'][:65]}")
            for d in item["completed_deps"]:
                ws = d.get("assigned_workspace", "?")
                print(f"    Completed: {d['task'][:50]} ({ws})")
            print(f"    ACTION: This task is now unblocked. You can proceed.")
            print()

    if still_blocked:
        print("STILL BLOCKED:")
        for item in still_blocked:
            t = item["task"]
            done = len(item["completed_deps"])
            total = done + len(item["pending_deps"])
            print(f"  [{t.get('project', '?')}] {t['task'][:65]}")
            print(f"    Progress: {done}/{total} dependencies completed")
            for d in item["pending_deps"]:
                ws = d.get("assigned_workspace", "?")
                print(f"    Waiting: {d.get('task', '?')[:50]} ({ws}) [{d.get('status', '?')}]")
            print()

    if not cleared and not still_blocked:
        print(f"No blocked tasks with dependencies for '{workspace}'.")


def my_tasks(base_url, api_key, workspace):
    """Show all tasks assigned to a workspace, grouped by project."""
    workspace = _validate_workspace(workspace)
    encoded_ws = urllib.parse.quote(workspace)
    tasks = _get(
        base_url, api_key,
        f"tasks?assigned_workspace=eq.{encoded_ws}"
        f"&select=task,project,status,priority,depends_on,carried_days"
        f"&order=project.asc,status.asc,priority.asc"
    )

    if not tasks:
        print(f"No tasks assigned to workspace '{workspace}'.")
        return

    # Group by project
    projects = {}
    for t in tasks:
        proj = t.get("project") or "(no project)"
        if proj not in projects:
            projects[proj] = []
        projects[proj].append(t)

    # Get project info for status display
    proj_info = {}
    for proj_name in projects:
        if proj_name == "(no project)":
            continue
        encoded = urllib.parse.quote(proj_name)
        info = _get(base_url, api_key,
                    f"projects?name=ilike.{encoded}&select=name,status,current_phase")
        if info:
            proj_info[proj_name] = info[0]

    print(f"=== TASKS FOR {workspace} ===")
    print()

    counts = {"pending": 0, "in_progress": 0, "completed": 0, "blocked": 0, "deferred": 0}

    for proj_name, proj_tasks in projects.items():
        info = proj_info.get(proj_name, {})
        proj_status = info.get("status", "?")
        phase = info.get("current_phase", "")
        phase_str = f", {phase}" if phase else ""
        print(f"{proj_name} ({proj_status}{phase_str})")

        for t in proj_tasks:
            status = t.get("status", "?")
            counts[status] = counts.get(status, 0) + 1
            # Distinct markers per status so downstream parsers (e.g.,
            # session-startup-guard.py STALE detection) can filter precisely.
            # `[ ]` is PENDING only; tabled/deferred/blocked/in_progress have
            # their own markers. Fixes wr-2026-04-19 startup-guard stale
            # detection including tabled tasks (HQ filed 70% false-positive rate).
            marker = {
                "completed": "x",
                "blocked": "!",
                "in_progress": ">",
                "tabled": "T",
                "deferred": "D",
            }.get(status, " ")
            deps = t.get("depends_on") or []
            dep_tag = f" (BLOCKED: {len(deps)} deps)" if deps and status != "completed" else ""
            carry = t.get("carried_days", 0) or 0
            carry_tag = f" [{carry}d carry]" if carry > 2 else ""
            print(f"  [{marker}] {t.get('task', '?')[:65]}{dep_tag}{carry_tag}")

        print()

    parts = []
    for s in ["pending", "in_progress", "completed", "blocked", "deferred"]:
        if counts.get(s, 0) > 0:
            parts.append(f"{counts[s]} {s}")
    print(f"=== {', '.join(parts)} ===")


def rollup(base_url, api_key, project_filter=None):
    """Show project progress rollup from project_progress view."""
    query = "project_progress?order=total_tasks.desc"
    if project_filter:
        encoded = urllib.parse.quote(project_filter)
        query += f"&project_name=ilike.*{encoded}*"

    rows = _get(base_url, api_key, query)
    if not rows:
        print("No project progress data found.")
        return

    print(f"{'Project':<40} {'Status':<10} {'Done':<8} {'Total':<7} {'%':<5} {'Blocked':<8}")
    print("-" * 80)
    for r in rows:
        total = r.get("total_tasks", 0)
        done = r.get("completed_tasks", 0)
        pct = r.get("pct_complete", 0)
        blocked = r.get("blocked_tasks", 0)
        name = r.get("project_name", "?")[:39]
        status = r.get("project_status", "?")
        print(f"{name:<40} {status:<10} {done:<8} {total:<7} {pct:<5} {blocked:<8}")

    # Summary
    total_all = sum(r.get("total_tasks", 0) for r in rows)
    done_all = sum(r.get("completed_tasks", 0) for r in rows)
    pct_all = round(100 * done_all / total_all) if total_all > 0 else 0
    print("-" * 80)
    print(f"{'TOTAL':<40} {'':10} {done_all:<8} {total_all:<7} {pct_all:<5}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    base_url, api_key = get_config()

    if cmd == "project" and len(sys.argv) >= 4:
        name = sys.argv[2]
        status = sys.argv[3]
        phase = None
        notes = None
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--phase" and i + 1 < len(sys.argv):
                phase = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--notes" and i + 1 < len(sys.argv):
                notes = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        success = update_project(base_url, api_key, name, status, phase, notes)
        sys.exit(0 if success else 1)

    elif cmd == "task" and len(sys.argv) >= 4:
        task_text = sys.argv[2]
        status = sys.argv[3]
        project = None
        notes = None
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--project" and i + 1 < len(sys.argv):
                project = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--notes" and i + 1 < len(sys.argv):
                notes = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        success = update_task(base_url, api_key, task_text, status, project, notes)
        sys.exit(0 if success else 1)

    elif cmd == "add-task" and len(sys.argv) >= 3:
        task_text = sys.argv[2]
        project = None
        workspace = None
        priority = "medium"
        dep_ids = []
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--project" and i + 1 < len(sys.argv):
                project = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--workspace" and i + 1 < len(sys.argv):
                workspace = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                priority = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--depends-on" and i + 1 < len(sys.argv):
                dep_ids = [x.strip() for x in sys.argv[i + 1].split(",") if x.strip()]
                i += 2
            else:
                i += 1
        if not project or not workspace:
            print("ERROR: --project and --workspace are required for add-task")
            sys.exit(1)
        success = add_task(base_url, api_key, task_text, project, workspace,
                           priority, dep_ids or None)
        sys.exit(0 if success else 1)

    elif cmd == "add-project" and len(sys.argv) >= 3:
        name = sys.argv[2]
        workspace = None
        status = "pending"
        priority = "medium"
        phase = None
        phase_description = None
        category = "formal"
        total_phases = None
        target_date = None
        idempotent = False
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--workspace" and i + 1 < len(sys.argv):
                workspace = sys.argv[i + 1]; i += 2
            elif sys.argv[i] == "--status" and i + 1 < len(sys.argv):
                status = sys.argv[i + 1]; i += 2
            elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                priority = sys.argv[i + 1]; i += 2
            elif sys.argv[i] == "--phase" and i + 1 < len(sys.argv):
                phase = sys.argv[i + 1]; i += 2
            elif sys.argv[i] == "--phase-description" and i + 1 < len(sys.argv):
                phase_description = sys.argv[i + 1]; i += 2
            elif sys.argv[i] == "--category" and i + 1 < len(sys.argv):
                category = sys.argv[i + 1]; i += 2
            elif sys.argv[i] == "--total-phases" and i + 1 < len(sys.argv):
                total_phases = sys.argv[i + 1]; i += 2
            elif sys.argv[i] == "--target-date" and i + 1 < len(sys.argv):
                target_date = sys.argv[i + 1]; i += 2
            elif sys.argv[i] == "--idempotent":
                idempotent = True; i += 1
            else:
                i += 1
        if not workspace:
            print("ERROR: --workspace is required for add-project")
            sys.exit(1)
        success = add_project(base_url, api_key, name, workspace,
                              status=status, priority=priority,
                              phase=phase, phase_description=phase_description,
                              category=category, total_phases=total_phases,
                              target_date=target_date, idempotent=idempotent)
        sys.exit(0 if success else 1)

    elif cmd == "add-dependency" and len(sys.argv) >= 3:
        task_text = sys.argv[2]
        blocker_text = None
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--depends-on" and i + 1 < len(sys.argv):
                blocker_text = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        if not blocker_text:
            print("ERROR: --depends-on is required for add-dependency")
            sys.exit(1)
        success = add_dependency(base_url, api_key, task_text, blocker_text)
        sys.exit(0 if success else 1)

    elif cmd == "check-blockers":
        workspace = None
        if "--workspace" in sys.argv:
            idx = sys.argv.index("--workspace")
            if idx + 1 < len(sys.argv):
                workspace = sys.argv[idx + 1]
        if not workspace:
            print("ERROR: --workspace is required for check-blockers")
            sys.exit(1)
        check_blockers(base_url, api_key, workspace)

    elif cmd == "my-tasks":
        workspace = None
        if "--workspace" in sys.argv:
            idx = sys.argv.index("--workspace")
            if idx + 1 < len(sys.argv):
                workspace = sys.argv[idx + 1]
        if not workspace:
            print("ERROR: --workspace is required for my-tasks")
            sys.exit(1)
        my_tasks(base_url, api_key, workspace)

    elif cmd == "recalc-carried-days":
        recalc_carried_days(base_url, api_key)

    elif cmd == "list-projects":
        status_filter = None
        if "--status" in sys.argv:
            idx = sys.argv.index("--status")
            if idx + 1 < len(sys.argv):
                status_filter = sys.argv[idx + 1]
        list_projects(base_url, api_key, status_filter)

    elif cmd == "list-tasks":
        project_filter = None
        status_filter = None
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--project" and i + 1 < len(sys.argv):
                project_filter = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--status" and i + 1 < len(sys.argv):
                status_filter = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        list_tasks(base_url, api_key, project_filter, status_filter)

    elif cmd == "rollup":
        project_filter = None
        if "--project" in sys.argv:
            idx = sys.argv.index("--project")
            if idx + 1 < len(sys.argv):
                project_filter = sys.argv[idx + 1]
        rollup(base_url, api_key, project_filter)

    elif cmd == "table" and len(sys.argv) >= 3:
        project_name = sys.argv[2]
        days = 30  # default review period
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--days" and i + 1 < len(sys.argv):
                days = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        from datetime import timedelta
        review_date = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")
        success = update_project(base_url, api_key, project_name, "tabled", review_date=review_date)
        if success:
            print(f"  Review date: {review_date} ({days} days from now)")
        sys.exit(0 if success else 1)

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
