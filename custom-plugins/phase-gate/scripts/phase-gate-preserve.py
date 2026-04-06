"""
phase-gate PreCompact hook.

Fires before context compaction. Preserves full phase state so the AI
can recover exactly where it was after compaction.

Writes to:
- .tmp/phase-state-backup.json (full state snapshot)
- .tmp/compact-context.md (human-readable append, complements aios-core)

Also clears the stop-warning gate file since compaction resets session state.
"""

import json
import os
from datetime import datetime, timezone


def get_cwd():
    return os.getcwd()


def read_json_file(path):
    """Safely read a JSON file, return None on failure."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def detect_plan_file(cwd):
    """Find the current plan file path."""
    # Check .claude/plans/ first
    plans_dir = os.path.join(cwd, ".claude", "plans")
    if os.path.isdir(plans_dir):
        for f in os.listdir(plans_dir):
            if f.endswith(".md"):
                return os.path.join(plans_dir, f)

    # Check active-phase.json for plan_file reference
    active = read_json_file(os.path.join(cwd, ".tmp", "active-phase.json"))
    if active and active.get("plan_file"):
        plan_path = active["plan_file"]
        if os.path.isfile(plan_path):
            return plan_path
        # Try relative to cwd
        rel_path = os.path.join(cwd, plan_path)
        if os.path.isfile(rel_path):
            return rel_path

    return None


def main():
    cwd = get_cwd()
    tmp_dir = os.path.join(cwd, ".tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    # Gather state
    active_phase = read_json_file(os.path.join(tmp_dir, "active-phase.json"))
    artifacts = read_json_file(os.path.join(tmp_dir, "phase-artifacts.json"))
    plan_file = detect_plan_file(cwd)

    state = {
        "preserved_at": timestamp,
        "active_phase": active_phase,
        "artifacts": artifacts,
        "plan_file": plan_file,
        "has_human_actions": os.path.isfile(
            os.path.join(cwd, "HUMAN-ACTION-REQUIRED.md")
        ),
        "has_lessons_learned": os.path.isfile(
            os.path.join(cwd, "lessons-learned.md")
        ),
    }

    # Write backup JSON
    backup_path = os.path.join(tmp_dir, "phase-state-backup.json")
    try:
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except OSError:
        pass

    # Append to compact-context.md (human-readable, complements aios-core)
    context_path = os.path.join(tmp_dir, "compact-context.md")
    lines = ["\n## Phase State (preserved by phase-gate)\n"]

    if active_phase:
        phase_num = active_phase.get("number", "?")
        phase_name = active_phase.get("name", "unknown")
        status = active_phase.get("status", "unknown")
        tasks_done = active_phase.get("tasks_done", 0)
        tasks_total = active_phase.get("tasks_total", 0)
        lines.append(
            "- Active: Phase %s (%s) - %s - %s/%s tasks done"
            % (phase_num, phase_name, status, tasks_done, tasks_total)
        )
    else:
        lines.append("- No active phase")

    if plan_file:
        lines.append("- Plan file: %s" % plan_file)

    if artifacts and artifacts.get("files"):
        count = len(artifacts["files"])
        lines.append("- Artifacts tracked this phase: %s files" % count)

    if state["has_human_actions"]:
        lines.append("- HUMAN-ACTION-REQUIRED.md exists -- review pending items")

    if state["has_lessons_learned"]:
        lines.append("- lessons-learned.md exists -- check before retrying failed approaches")

    lines.append("- Preserved at: %s" % timestamp)
    lines.append("")

    try:
        with open(context_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except OSError:
        pass

    # Clear the stop-warning gate (compaction resets session context)
    gate_file = os.path.join(tmp_dir, ".phase-gate-stop-warned")
    try:
        if os.path.isfile(gate_file):
            os.remove(gate_file)
    except OSError:
        pass

    # Output confirmation
    if active_phase:
        print(
            "[phase-gate] Phase state preserved to .tmp/phase-state-backup.json. "
            "Recovery available after compaction."
        )


if __name__ == "__main__":
    main()