"""
phase-gate Stop hook.

Fires when the user tries to end a session. Checks for:
1. Active phase not yet complete -> blocks ONCE with cleanup reminder
2. HUMAN-ACTION-REQUIRED.md with unchecked items -> non-blocking reminder
3. Otherwise -> allows stop

One-time gate: writes a tracking file so the second stop attempt passes through.
This prevents users from being locked out of ending their session.
"""

import json
import os


def get_cwd():
    return os.getcwd()


def get_active_phase(cwd):
    """Read .tmp/active-phase.json if it exists."""
    phase_file = os.path.join(cwd, ".tmp", "active-phase.json")
    if not os.path.isfile(phase_file):
        return None
    try:
        with open(phase_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def has_pending_human_actions(cwd):
    """Check if HUMAN-ACTION-REQUIRED.md exists and has unchecked items."""
    har_file = os.path.join(cwd, "HUMAN-ACTION-REQUIRED.md")
    if not os.path.isfile(har_file):
        return False
    try:
        with open(har_file, "r", encoding="utf-8") as f:
            content = f.read()
        return "- [ ]" in content
    except OSError:
        return False


def was_already_warned(cwd):
    """Check if we already warned once this session."""
    gate_file = os.path.join(cwd, ".tmp", ".phase-gate-stop-warned")
    return os.path.isfile(gate_file)


def set_warned(cwd):
    """Mark that we warned, so next stop attempt passes through."""
    gate_file = os.path.join(cwd, ".tmp", ".phase-gate-stop-warned")
    try:
        os.makedirs(os.path.dirname(gate_file), exist_ok=True)
        with open(gate_file, "w", encoding="utf-8") as f:
            f.write("warned")
    except OSError:
        pass


def clear_warned(cwd):
    """Remove the warning gate file (called when phase completes normally)."""
    gate_file = os.path.join(cwd, ".tmp", ".phase-gate-stop-warned")
    try:
        if os.path.isfile(gate_file):
            os.remove(gate_file)
    except OSError:
        pass


def main():
    cwd = get_cwd()
    messages = []
    should_block = False

    active_phase = get_active_phase(cwd)

    # Check 1: Active phase not complete
    if active_phase and active_phase.get("status") not in ("complete", "paused"):
        if not was_already_warned(cwd):
            phase_num = active_phase.get("number", "?")
            phase_name = active_phase.get("name", "unknown")
            tasks_done = active_phase.get("tasks_done", 0)
            tasks_total = active_phase.get("tasks_total", 0)

            messages.append(
                "[phase-gate] Phase %s (%s) is still in progress "
                "(%s/%s tasks done). Before ending this session:"
                % (phase_num, phase_name, tasks_done, tasks_total)
            )
            messages.append(
                "  1. Complete remaining tasks OR mark phase as paused"
            )
            messages.append(
                "  2. Run Phase Completion Protocol (or Phase Pause Protocol)"
            )
            messages.append(
                "  3. Update MEMORY.md with resume instructions"
            )
            messages.append(
                "  4. Commit + push to GitHub if uncommitted changes exist"
            )

            set_warned(cwd)
            should_block = True

    # Check 2: Pending human actions (non-blocking reminder)
    if has_pending_human_actions(cwd):
        messages.append(
            "[phase-gate] Reminder: HUMAN-ACTION-REQUIRED.md has "
            "unchecked items. Review before closing."
        )

    # Output
    if messages:
        for msg in messages:
            print(msg)

    # Block only on first warning for active phase
    if should_block:
        result = {"decision": "block", "reason": "Active phase requires cleanup before session end"}
        print(json.dumps(result))


if __name__ == "__main__":
    main()