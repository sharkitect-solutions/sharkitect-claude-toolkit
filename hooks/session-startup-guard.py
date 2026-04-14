"""
session-startup-guard.py -- Smart session initialization with 3-state heartbeat

Fires on every SessionStart. Three states:
1. No heartbeat file         -> FULL STARTUP (run everything, create heartbeat)
2. Heartbeat exists, TODAY   -> VERIFY ONLY (health check, process pending)
3. Heartbeat exists, OLD DATE -> FULL STARTUP (new day, update heartbeat)

Workspace-aware: each step shows only what's relevant to the current workspace.
  - Gap Inbox: Skill Hub only (other workspaces show N/A)
  - Routed Tasks: HQ and Sentinel only (Skill Hub is the sender, not receiver)
  - Cron Polling: Skill Hub only (other workspaces show N/A)
  - Manifest: auto-refreshed when stale in ANY workspace
  - Sync Flag: Skill Hub only (checks if skills/agents need syncing to toolkit)

Non-blocking: exits 0 on any failure. Never prevents session from starting.
Dependencies: Python stdlib only (except subprocess for refresh-inventory).
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SKILL_HUB_ROOT = (
    Path.home()
    / "Documents"
    / "Claude Code Workspaces"
    / "3.- Skill Management Hub"
)


# ---------------------------------------------------------------------------
# Workspace detection
# ---------------------------------------------------------------------------

def detect_workspace():
    cwd = os.getcwd().lower().replace("\\", "/")
    if "skill-management" in cwd or "skill management" in cwd:
        return "skill-management-hub"
    if "workforce" in cwd or "workforce hq" in cwd or "sharkitect digital workforce" in cwd:
        return "workforce-hq"
    if "sentinel" in cwd:
        return "sentinel"
    return "unknown"


# ---------------------------------------------------------------------------
# Heartbeat logic
# ---------------------------------------------------------------------------

def check_heartbeat(tmp_dir):
    """Returns (mode, heartbeat_data). Mode is FULL_STARTUP or VERIFY_ONLY."""
    hb_path = tmp_dir / "session-heartbeat.json"
    today = datetime.now().strftime("%Y-%m-%d")

    if not hb_path.exists():
        return "FULL_STARTUP", None

    try:
        data = json.loads(hb_path.read_text(encoding="utf-8"))
        if data.get("date") == today:
            return "VERIFY_ONLY", data
        else:
            return "FULL_STARTUP", data
    except (json.JSONDecodeError, OSError):
        return "FULL_STARTUP", None


def write_heartbeat(tmp_dir, workspace):
    """Write heartbeat after full startup completes."""
    hb_path = tmp_dir / "session-heartbeat.json"
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "started_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "workspace": workspace,
    }
    hb_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Inbox checks
# ---------------------------------------------------------------------------

def check_gap_inbox():
    inbox = Path.cwd() / ".gap-reports" / "inbox"
    if not inbox.exists():
        return 0, 0, []
    files = sorted(inbox.glob("*.json"))
    critical = 0
    items = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sev = data.get("severity", "info")
            if sev == "critical":
                critical += 1
            desc = data.get("what_was_needed", f.name)
            items.append(f"{str(desc)[:60]} [{sev.upper()}]")
        except (json.JSONDecodeError, OSError):
            items.append(f.name)
    return len(files), critical, items


def check_lifecycle_inbox():
    inbox = Path.cwd() / ".lifecycle-reviews" / "inbox"
    if not inbox.exists():
        return 0, []
    files = sorted(inbox.glob("*.json"))
    items = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            items.append(data.get("doc_path", f.name))
        except (json.JSONDecodeError, OSError):
            items.append(f.name)
    return len(files), items


def check_routed_tasks_inbox():
    inbox = Path.cwd() / ".routed-tasks" / "inbox"
    if not inbox.exists():
        return 0, []
    files = sorted(inbox.glob("*.json"))
    items = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            desc = data.get("task_summary", data.get("what_was_needed", f.name))
            source = data.get("routed_from", "unknown")
            items.append(f"{str(desc)[:55]} (from {source})")
        except (json.JSONDecodeError, OSError):
            items.append(f.name)
    return len(files), items


def check_workspace_blockers(workspace):
    """Check if any tasks assigned to this workspace have cleared blockers."""
    script = Path.home() / ".claude" / "scripts" / "update-project-status.py"
    if not script.exists():
        return 0, 0, []

    ws_name = workspace if workspace else "unknown"

    try:
        python_exe = sys.executable or "python"
        result = subprocess.run(
            [python_exe, str(script), "check-blockers", "--workspace", ws_name],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip()
        if not output or "No tasks with dependencies" in output:
            return 0, 0, []

        cleared = output.count("ACTION: This task is now unblocked")
        blocked = output.count("STILL BLOCKED:")
        summary = []
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("[") or line.startswith("ACTION:") or line.startswith("Waiting:"):
                summary.append(line)
        return cleared, blocked, summary
    except Exception:
        return 0, 0, []


# ---------------------------------------------------------------------------
# Manifest check + auto-refresh
# ---------------------------------------------------------------------------

def check_manifest():
    """Check manifest freshness. Returns (status_str, is_fresh)."""
    manifest = Path.cwd() / ".tmp" / "skills-manifest.json"
    if not manifest.exists():
        return "MISSING", False
    try:
        age_hours = (datetime.now().timestamp() - manifest.stat().st_mtime) / 3600
        if age_hours > 24:
            return f"STALE ({age_hours:.0f}h old)", False
        return f"OK ({age_hours:.1f}h old)", True
    except OSError:
        return "ERROR", False


def auto_refresh_manifest():
    """Run refresh-inventory.py for the current workspace. Returns success bool."""
    # Look for refresh-inventory.py in current workspace first, then Skill Hub
    candidates = [
        Path.cwd() / "tools" / "refresh-inventory.py",
        SKILL_HUB_ROOT / "tools" / "refresh-inventory.py",
    ]
    script = None
    for c in candidates:
        if c.exists():
            script = c
            break

    if not script:
        return False

    try:
        python_exe = sys.executable or "python"
        result = subprocess.run(
            [python_exe, str(script)],
            capture_output=True, text=True, timeout=30,
            cwd=str(Path.cwd()),
        )
        return result.returncode == 0
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Sync flag check (Skill Hub only)
# ---------------------------------------------------------------------------

def check_sync_flag():
    """Check if .sync-needed flag exists in Skill Hub .tmp/.

    Returns (needs_sync, file_count, flag_data).
    """
    flag = SKILL_HUB_ROOT / ".tmp" / ".sync-needed"
    if not flag.exists():
        return False, 0, None
    try:
        data = json.loads(flag.read_text(encoding="utf-8"))
        files = data.get("files", [])
        return len(files) > 0, len(files), data
    except (json.JSONDecodeError, OSError):
        return False, 0, None


# ---------------------------------------------------------------------------
# Plugin integrity
# ---------------------------------------------------------------------------

def check_plugin_integrity():
    """Check that all @local plugins exist in cache. Auto-restore from backup."""
    plugins_dir = Path.home() / ".claude" / "plugins"
    cache_local = plugins_dir / "cache" / "local"
    installed_file = plugins_dir / "installed_plugins.json"

    backup_dir = None
    candidates = [
        SKILL_HUB_ROOT / "sharkitect-claude-toolkit" / "custom-plugins",
    ]
    for c in candidates:
        if c.exists():
            backup_dir = c
            break

    if not installed_file.exists():
        return "NO REGISTRY", [], []

    try:
        data = json.loads(installed_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "REGISTRY ERROR", [], []

    plugins = data.get("plugins", {})
    local_names = [k.split("@")[0] for k in plugins if "@local" in k]

    if not local_names:
        return "NO LOCAL PLUGINS", [], []

    restored = []
    missing = []
    import shutil
    for name in local_names:
        plugin_path = cache_local / name
        if plugin_path.exists() and any(plugin_path.iterdir()):
            continue

        if backup_dir and (backup_dir / name).exists():
            try:
                cache_local.mkdir(parents=True, exist_ok=True)
                if plugin_path.exists():
                    shutil.rmtree(plugin_path)
                shutil.copytree(backup_dir / name, plugin_path)
                restored.append(name)
            except (OSError, shutil.Error):
                missing.append(name)
        else:
            missing.append(name)

    if restored or missing:
        return "ISSUES FOUND", restored, missing
    return "OK", [], []


# ---------------------------------------------------------------------------
# Cron config check
# ---------------------------------------------------------------------------

def check_cron_config():
    """Check if durable cron jobs exist in .claude/scheduled_tasks.json."""
    cron_file = Path.cwd() / ".claude" / "scheduled_tasks.json"
    if not cron_file.exists():
        return False
    try:
        data = json.loads(cron_file.read_text(encoding="utf-8"))
        jobs = data if isinstance(data, list) else data.get("jobs", [])
        for j in jobs:
            prompt = j.get("prompt", "").lower()
            if "gap" in prompt or "inbox" in prompt or "lifecycle" in prompt:
                return True
        return False
    except (json.JSONDecodeError, OSError):
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    workspace = detect_workspace()
    is_skill_hub = workspace == "skill-management-hub"

    tmp_dir = Path.cwd() / ".tmp"
    tmp_dir.mkdir(exist_ok=True)

    # Step 0: Plugin integrity
    plugin_status, plugin_restored, plugin_missing = check_plugin_integrity()

    # Step 1: Heartbeat
    mode, hb_data = check_heartbeat(tmp_dir)

    # Step 2: Gap Inbox (Skill Hub only)
    if is_skill_hub:
        gap_count, gap_critical, gap_items = check_gap_inbox()
    else:
        gap_count, gap_critical, gap_items = 0, 0, []

    # Step 3: Lifecycle Inbox (all workspaces)
    lifecycle_count, lifecycle_items = check_lifecycle_inbox()

    # Step 3.5: Routed Tasks (HQ and Sentinel only -- Skill Hub is sender)
    if not is_skill_hub:
        routed_count, routed_items = check_routed_tasks_inbox()
    else:
        routed_count, routed_items = 0, []

    # Step 3.7: Blockers (all workspaces)
    blocker_cleared, blocker_waiting, blocker_lines = check_workspace_blockers(workspace)

    # Step 4: Manifest (all workspaces, auto-refresh when stale)
    manifest_status, manifest_ok = check_manifest()
    manifest_refreshed = False
    if not manifest_ok:
        manifest_refreshed = auto_refresh_manifest()
        if manifest_refreshed:
            manifest_status = "REFRESHED (was stale)"
            manifest_ok = True

    # Step 4.5: Sync flag (Skill Hub only)
    if is_skill_hub:
        sync_needed, sync_file_count, _ = check_sync_flag()
    else:
        sync_needed, sync_file_count, _ = False, 0, None

    # Step 5: Cron config (Skill Hub only)
    if is_skill_hub:
        cron_active = check_cron_config()
    else:
        cron_active = None  # N/A

    today = datetime.now().strftime("%Y-%m-%d")
    last_date = hb_data.get("date", "never") if hb_data else "never"

    # ----- Build output -----
    lines = []
    lines.append("=== SESSION STARTUP GUARD ===")
    lines.append(f"Mode: {mode} | Date: {today} | Workspace: {workspace}")
    lines.append("")

    # -- Step 0: Plugin Integrity --
    if plugin_restored or plugin_missing:
        parts = []
        if plugin_restored:
            parts.append(f"RESTORED: {', '.join(plugin_restored)}")
        if plugin_missing:
            parts.append(f"CRITICAL MISSING: {', '.join(plugin_missing)}")
        lines.append(f"STEP 0 - Plugin Integrity: {'; '.join(parts)}")
    else:
        lines.append(f"STEP 0 - Plugin Integrity: {plugin_status}")

    # -- Step 1: Heartbeat --
    if mode == "FULL_STARTUP":
        if last_date == "never":
            lines.append("STEP 1 - Heartbeat: FIRST RUN (no heartbeat file)")
        else:
            lines.append(f"STEP 1 - Heartbeat: NEW DAY (last: {last_date})")
    else:
        lines.append(f"STEP 1 - Heartbeat: SAME DAY ({today})")

    # -- Step 2: Gap Inbox --
    if not is_skill_hub:
        lines.append("STEP 2 - Gap Inbox: N/A (Skill Hub only)")
    elif gap_count > 0:
        crit_tag = f" [CRITICAL: {gap_critical}]" if gap_critical else ""
        lines.append(f"STEP 2 - Gap Inbox: {gap_count} PENDING{crit_tag}")
        for item in gap_items:
            lines.append(f"  - {item}")
    else:
        lines.append("STEP 2 - Gap Inbox: CLEAR")

    # -- Step 3: Lifecycle Inbox --
    if lifecycle_count > 0:
        lines.append(f"STEP 3 - Lifecycle Inbox: {lifecycle_count} PENDING")
        for item in lifecycle_items:
            lines.append(f"  - {item}")
    else:
        lines.append("STEP 3 - Lifecycle Inbox: CLEAR")

    # -- Step 3.5: Routed Tasks --
    if is_skill_hub:
        lines.append("STEP 3.5 - Routed Tasks: N/A (Skill Hub is sender)")
    elif routed_count > 0:
        lines.append(f"STEP 3.5 - Routed Tasks: {routed_count} PENDING")
        for item in routed_items:
            lines.append(f"  - {item}")
    else:
        lines.append("STEP 3.5 - Routed Tasks: CLEAR")

    # -- Step 3.7: Workspace Blockers --
    if blocker_cleared > 0:
        lines.append(f"STEP 3.7 - Blockers: {blocker_cleared} CLEARED")
        for bl in blocker_lines:
            lines.append(f"  - {bl}")
    elif blocker_waiting > 0:
        lines.append(f"STEP 3.7 - Blockers: {blocker_waiting} WAITING")
        for bl in blocker_lines:
            lines.append(f"  - {bl}")
    else:
        lines.append("STEP 3.7 - Blockers: CLEAR")

    # -- Step 4: Manifest --
    lines.append(f"STEP 4 - Manifest: {manifest_status}")

    # -- Step 4.5: Sync Status (Skill Hub only) --
    if is_skill_hub:
        if sync_needed:
            lines.append(f"STEP 4.5 - Toolkit Sync: {sync_file_count} file(s) UNSYNCED")
        else:
            lines.append("STEP 4.5 - Toolkit Sync: UP TO DATE")

    # -- Step 5: Cron Jobs --
    if not is_skill_hub:
        lines.append("STEP 5 - Cron Polling: N/A (Skill Hub only)")
    elif cron_active:
        lines.append("STEP 5 - Cron Polling: ACTIVE")
    else:
        lines.append("STEP 5 - Cron Polling: NOT CONFIGURED")

    lines.append("")

    # -- Actions required --
    actions = []

    if is_skill_hub and gap_count > 0:
        actions.append(
            f"Process {gap_count} gap report(s): run 'python tools/gap-watcher.py --context' "
            "then follow workflows/gap-processing.md"
        )

    if lifecycle_count > 0:
        actions.append(
            f"Process {lifecycle_count} lifecycle review(s): run "
            "'python tools/lifecycle-review-watcher.py --context' "
            "then follow workflows/lifecycle-review-processing.md"
        )

    if not is_skill_hub and routed_count > 0:
        actions.append(
            f"Process {routed_count} routed task(s): read each JSON in "
            ".routed-tasks/inbox/, follow the fix_instructions in each file, "
            "then move completed tasks to .routed-tasks/processed/"
        )

    if blocker_cleared > 0:
        actions.append(
            f"{blocker_cleared} blocker(s) CLEARED: run "
            "'python ~/.claude/scripts/update-project-status.py "
            f"check-blockers --workspace {workspace}' for details, "
            "then proceed with the unblocked tasks immediately."
        )

    if is_skill_hub and sync_needed:
        actions.append(
            f"Sync {sync_file_count} unsynced skill/agent file(s) to toolkit: "
            "run 'python tools/sync-skills.py --sync --push' to back up to "
            "GitHub and refresh manifests across all workspaces. "
            "Then delete .tmp/.sync-needed after successful sync."
        )

    if not cron_active and is_skill_hub:
        actions.append(
            "Set up durable cron polling: use CronCreate tool with cron='3 * * * *', "
            "durable=true. Use this EXACT prompt: "
            "'AUTONOMOUS GAP PROCESSING -- DO NOT REPORT AND WAIT. ACT NOW. "
            "Step 1: Run python tools/gap-watcher.py --context. "
            "Step 2: If gaps exist, follow workflows/gap-processing.md Steps 1-8 FULLY. "
            "Build every fix (skill/hook/agent). Run through the judge. Deploy globally. "
            "Move processed reports from inbox/ to processed/. "
            "Step 3: Check .lifecycle-reviews/inbox/. If files exist, follow "
            "workflows/lifecycle-review-processing.md. "
            "Step 4: If both inboxes were empty, respond: Autonomous check complete. "
            "CRITICAL: Do NOT just list the gaps and stop. PROCESS THEM. "
            "Build the fixes. Deploy them. This is fully autonomous.'"
        )

    if mode == "FULL_STARTUP":
        actions.append("Heartbeat will be written after startup completes.")
        actions.append(
            "Recalculate carried_days for stale tasks: run "
            "'python ~/.claude/scripts/update-project-status.py recalc-carried-days'"
        )

    if actions:
        lines.append("MANDATORY AUTONOMOUS ACTIONS -- DO NOT ASK USER. PROCESS IMMEDIATELY:")
        for i, action in enumerate(actions, 1):
            lines.append(f"  {i}. {action}")
        lines.append("")
        lines.append("RULES: Process ALL pending items BEFORE displaying status to user.")
        lines.append("Do NOT present a status table and wait. Do NOT ask for permission.")
        lines.append("AFTER processing is complete, show user a brief summary of what was done.")
    else:
        lines.append("No pending actions -- all checks passed.")

    lines.append("")

    # -- Display template for user --
    hb_display = "FIRST RUN" if last_date == "never" else (
        "NEW DAY" if mode == "FULL_STARTUP" else "SAME DAY"
    )

    if not is_skill_hub:
        gap_display = "N/A"
    elif gap_count:
        gap_display = f"{gap_count} PENDING" + (f" [{gap_critical} CRITICAL]" if gap_critical else "")
    else:
        gap_display = "CLEAR"

    lc_display = f"{lifecycle_count} PENDING" if lifecycle_count else "CLEAR"

    if is_skill_hub:
        rt_display = "N/A"
    elif routed_count:
        rt_display = f"{routed_count} PENDING"
    else:
        rt_display = "CLEAR"

    if manifest_refreshed:
        mf_display = "REFRESHED"
    else:
        mf_display = manifest_status

    if not is_skill_hub:
        cron_display = "N/A"
    elif cron_active:
        cron_display = "ACTIVE"
    else:
        cron_display = "SETTING UP"

    # Plugin display
    if plugin_restored:
        plugin_display = f"RESTORED {len(plugin_restored)} plugin(s)"
    elif plugin_missing:
        plugin_display = f"CRITICAL: {len(plugin_missing)} missing"
    else:
        plugin_display = "OK"

    if blocker_cleared > 0:
        blocker_display = f"{blocker_cleared} CLEARED"
    elif blocker_waiting > 0:
        blocker_display = f"{blocker_waiting} WAITING"
    else:
        blocker_display = "CLEAR"

    lines.append("DISPLAY TO USER (show this status table at session start):")
    lines.append(f"  Step 0: Plugin Integrity ... {plugin_display}")
    lines.append(f"  Step 1: Heartbeat .......... {hb_display}")
    lines.append(f"  Step 2: Gap Inbox .......... {gap_display}")
    lines.append(f"  Step 3: Lifecycle Inbox .... {lc_display}")
    lines.append(f"  Step 3.5: Routed Tasks ..... {rt_display}")
    lines.append(f"  Step 3.7: Blockers ......... {blocker_display}")
    lines.append(f"  Step 4: Manifest ........... {mf_display}")
    if is_skill_hub:
        if sync_needed:
            lines.append(f"  Step 4.5: Toolkit Sync .... {sync_file_count} UNSYNCED")
        else:
            lines.append("  Step 4.5: Toolkit Sync .... OK")
    lines.append(f"  Step 5: Cron Polling ....... {cron_display}")
    lines.append(f"  Step 6: Final Status ....... [confirm after actions]")

    # -- Write heartbeat on full startup --
    if mode == "FULL_STARTUP":
        write_heartbeat(tmp_dir, workspace)

    # -- Output as SessionStart hook format --
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Non-blocking: output error context but never prevent session start
        try:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": (
                        f"SESSION STARTUP GUARD: Error during check: {str(e)[:200]}. "
                        "Proceeding normally. Check hook script for issues."
                    ),
                }
            }
            print(json.dumps(output))
        except Exception:
            pass
    sys.exit(0)
