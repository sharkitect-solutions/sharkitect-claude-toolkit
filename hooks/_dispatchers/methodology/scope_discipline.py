"""scope_discipline.py - Methodology dispatcher sub-rule (Phase 2 Build #2B).

Source: workspace-scope-guard.py (advisory-only enforcement of workspace
scope rules: which workspace owns which path patterns).

Behavior preserved 1:1 from source:
  Layer 1: Workspace-specific STRUCTURAL forbidden self-paths
           (Skill Hub writing to its own .routed-tasks/, HQ/Sentinel writing
            to their own .work-requests/).
  Layer 2: TARGET-side structural forbidden paths regardless of source
           (anyone writing to Skill Hub's .routed-tasks/, etc.).
  Layer 3: ALWAYS_ALLOWED exemptions (.routed-tasks/, .lifecycle-reviews/,
           /.claude/rules/, /.claude/scripts/, memory/, .tmp/, etc.).
  Layer 4: Protocol-sanctioned cross-workspace writes (.work-requests/inbox/
           new file, blocker_cleared_notes append).
  Layer 5: Cross-workspace SCOPE_VIOLATIONS (creating skills/hooks/agents/
           plugins from non-Skill-Hub; writing other workspaces' dirs).

Layer order preserved: 1 -> 2 -> 3 -> 4 -> 5 (structural checks BEFORE
ALWAYS_ALLOWED so global exemptions don't bypass structural rules; sanctioned
writes evaluated AFTER allowed exemptions and BEFORE scope violations).

Severity: ADVISORY only (returns {"advisory": "..."}). Source never used
permissionDecision: deny -- workspace-scope-guard is a soft nudge.

NOT INCLUDED (deferred to Build 6 per Phase 2 spec C.4):
  - Part C-4 anti-drift detection (side-concern mid-task absorption)
  - Fortification-vs-Expansion 3Q test
  - Bilateral CEO scope justification prompt
  These additions require UserPromptSubmit infra and TodoWrite scope-change
  detection that ship in Build 6.

Source incidents preserved:
  - wr-2026-04-21-001: Skill Hub writing to own .routed-tasks/ (5 files drift)
  - Sentinel hallucination 2026-04-21: HQ/Sentinel inventing .work-requests/
  - 2026-04-29: Sentinel writing to Skill Hub's .routed-tasks/ from outside

Spec: docs/superpowers/specs/2026-05-15-phase-2-architecture-spec.md (Part A)
"""
from __future__ import annotations

import os
import sys

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events
except Exception:
    _feedback_events = None


def _get_cwd():
    """Cwd resolver, exposed for test monkeypatching."""
    return os.getcwd()


def detect_workspace(cwd):
    """Identify which workspace we're in based on CWD."""
    cwd_lower = cwd.replace("\\", "/").lower()
    if "skill management hub" in cwd_lower or "3.-" in cwd_lower:
        return "skill-hub"
    if "workforce" in cwd_lower and "hq" in cwd_lower or "1.-" in cwd_lower:
        return "hq"
    if "sentinel" in cwd_lower or "4.-" in cwd_lower:
        return "sentinel"
    return "unknown"


WORKSPACE_PATHS = {
    "skill-hub": "skill management hub",
    "hq": "sharkitect digital workforce hq",
    "sentinel": "sentinel",
}

SCOPE_VIOLATIONS = {
    "hq": [
        ("/.claude/skills/", "Creating skills belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/hooks/", "Creating hooks belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/agents/", "Creating agents belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/plugins/", "Creating plugins belongs in Skill Management Hub", "Skill Management Hub"),
        ("/4.- sentinel/", "Writing Sentinel files from HQ", "Sentinel"),
        ("/3.- skill management hub/", "Writing Skill Hub files from HQ", "Skill Management Hub"),
    ],
    "sentinel": [
        ("/.claude/skills/", "Creating skills belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/hooks/", "Creating hooks belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/agents/", "Creating agents belongs in Skill Management Hub", "Skill Management Hub"),
        ("/.claude/plugins/", "Creating plugins belongs in Skill Management Hub", "Skill Management Hub"),
        ("/1.- sharkitect digital workforce hq/", "Writing HQ files from Sentinel", "Workforce HQ"),
        ("/3.- skill management hub/", "Writing Skill Hub files from Sentinel", "Skill Management Hub"),
    ],
    "skill-hub": [
        ("/1.- sharkitect digital workforce hq/", "Writing HQ files from Skill Hub", "Workforce HQ"),
        ("/4.- sentinel/", "Writing Sentinel files from Skill Hub", "Sentinel"),
    ],
}

WORKSPACE_FORBIDDEN_PATHS = {
    "skill-hub": [
        (
            ".routed-tasks/",
            "Skill Hub has no .routed-tasks/ directory per universal-protocols.md -- "
            "its entire inbound channel is .work-requests/inbox/ and its outbound "
            "audit trail is .work-requests/outbox/.",
            ".work-requests/outbox/ (for outbound audit) or another workspace's .routed-tasks/inbox/ (for routing TO them)",
        ),
    ],
    "hq": [
        (
            ".work-requests/",
            "HQ has no .work-requests/ directory per universal-protocols.md -- "
            "that name is exclusive to Skill Hub. HQ's coordination folder is "
            ".routed-tasks/{inbox,processed,outbox}/.",
            ".routed-tasks/outbox/ (for outbound audit to any workspace) or Skill Hub's .work-requests/inbox/ (for filing work requests TO Skill Hub via work-request.py)",
        ),
    ],
    "sentinel": [
        (
            ".work-requests/",
            "Sentinel has no .work-requests/ directory per universal-protocols.md -- "
            "that name is exclusive to Skill Hub. Sentinel's coordination folder is "
            ".routed-tasks/{inbox,processed,outbox}/.",
            ".routed-tasks/outbox/ (for outbound audit to any workspace) or Skill Hub's .work-requests/inbox/ (for filing work requests TO Skill Hub via work-request.py)",
        ),
    ],
}

ALWAYS_ALLOWED = [
    "/.claude/rules/",
    "/.claude/lessons-learned.md",
    "/.claude/docs/plans-registry.md",
    "/.claude/docs/autonomous-systems-inventory.md",
    "/.claude/scripts/",
    ".gap-reports/",
    ".routed-tasks/",
    ".lifecycle-reviews/",
    "memory/",
    "memory.md",
    ".tmp/",
]


def normalize_path(path):
    return path.replace("\\", "/").lower()


def is_always_allowed(file_path):
    normalized = normalize_path(file_path)
    for allowed in ALWAYS_ALLOWED:
        if allowed.lower() in normalized:
            return True
    return False


def check_cross_workspace_write(file_path, current_workspace):
    normalized = normalize_path(file_path)
    violations = SCOPE_VIOLATIONS.get(current_workspace, [])
    for pattern, description, correct_ws in violations:
        if pattern.lower() in normalized:
            return description, correct_ws
    return None, None


def is_self_write(file_path_norm, cwd_norm, workspace_name):
    """True if file_path is inside the current workspace's own directory.

    Uses path-prefix matching (not substring) so that filenames containing
    workspace names -- e.g. `2026-04-21_sentinel-foo.json` routed TO Skill
    Hub -- don't false-positive as "inside Sentinel's dir."
    """
    if not cwd_norm:
        return False
    del workspace_name
    cwd_check = cwd_norm.rstrip("/")
    return file_path_norm == cwd_check or file_path_norm.startswith(cwd_check + "/")


def check_forbidden_self_path(file_path, current_workspace, cwd):
    forbidden = WORKSPACE_FORBIDDEN_PATHS.get(current_workspace, [])
    if not forbidden:
        return None, None

    file_norm = normalize_path(file_path)
    cwd_norm = normalize_path(cwd)

    if not is_self_write(file_norm, cwd_norm, current_workspace):
        return None, None

    for pattern, reason, redirect in forbidden:
        if pattern.lower() in file_norm:
            return reason, redirect
    return None, None


def check_target_workspace_forbidden(file_path):
    """Check if the WRITE TARGET path lands inside a directory the target
    workspace structurally does not own, regardless of source workspace.
    """
    file_norm = normalize_path(file_path)

    if "/3.- skill management hub/.routed-tasks/" in file_norm:
        return (
            "TARGET WORKSPACE STRUCTURE VIOLATION. Skill Hub has NO "
            ".routed-tasks/ directory per universal-protocols.md. Inbound "
            "coordination to Skill Hub goes through .work-requests/inbox/ "
            "via `python ~/.claude/scripts/work-request.py`. Writing to "
            "Skill Hub's .routed-tasks/ creates silent drift -- the file "
            "lands in a directory Skill Hub never reads, so the request "
            "never reaches Skill Hub's processing pipeline.",
            "Skill Hub's .work-requests/inbox/ via "
            "`python ~/.claude/scripts/work-request.py --type <TYPE> "
            "--severity <SEVERITY> --workspace <SOURCE_WORKSPACE> "
            "--workspace-path \"$(pwd)\" --task \"<DESC>\" ...`",
        )

    if "/1.- sharkitect digital workforce hq/.work-requests/" in file_norm:
        return (
            "TARGET WORKSPACE STRUCTURE VIOLATION. HQ has NO "
            ".work-requests/ directory per universal-protocols.md. "
            ".work-requests/ is exclusive to Skill Hub. HQ's coordination "
            "channel is .routed-tasks/{inbox,processed,outbox}/.",
            "HQ's .routed-tasks/inbox/ (for routing TO HQ) or your own "
            ".routed-tasks/outbox/ (for outbound audit trail)",
        )

    if "/4.- sentinel/.work-requests/" in file_norm:
        return (
            "TARGET WORKSPACE STRUCTURE VIOLATION. Sentinel has NO "
            ".work-requests/ directory per universal-protocols.md. "
            ".work-requests/ is exclusive to Skill Hub. Sentinel's "
            "coordination channel is .routed-tasks/{inbox,processed,outbox}/.",
            "Sentinel's .routed-tasks/inbox/ (for routing TO Sentinel) "
            "or your own .routed-tasks/outbox/ (for outbound audit trail)",
        )
    return None, None


def is_protocol_sanctioned_write(tool_name, tool_input):
    """Detect protocol-sanctioned cross-workspace writes that should pass."""
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return False
    normalized = normalize_path(file_path)

    if tool_name == "Write" and "/.work-requests/inbox/" in normalized:
        return True

    if tool_name == "Edit" and "/.work-requests/inbox/" in normalized and normalized.endswith(".json"):
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        if (
            "blocker_cleared_notes" in old_string
            and "blocker_cleared_notes" in new_string
            and len(new_string) > len(old_string) + 20
        ):
            return True
    return False


def evaluate(payload):
    """Evaluate scope_discipline sub-rule.

    Returns:
      None                                  -> sub-rule did not trigger / pass-through
      {"advisory": "<text>"}                -> ADVISORY
    """
    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return None

    tool_input = payload.get("tool_input", {}) or {}
    if not isinstance(tool_input, dict):
        return None

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return None

    cwd = _get_cwd()
    current_workspace = detect_workspace(cwd)

    # Layer 1: Self-write to structurally forbidden path
    if current_workspace != "unknown":
        forbidden_reason, redirect = check_forbidden_self_path(
            file_path, current_workspace, cwd,
        )
        if forbidden_reason is not None and redirect is not None:
            advisory = (
                "WORKSPACE STRUCTURE VIOLATION. "
                + forbidden_reason
                + " Redirect to: " + redirect + ". "
                "If the user explicitly overrides, note the exception in MEMORY.md."
            )
            if _feedback_events:
                try:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="scope_discipline",
                        decision="advisory", trigger="forbidden_self_path",
                        payload=payload,
                    )
                except Exception:
                    pass
            return {"advisory": advisory}

    # Layer 2: Target-side structural forbidden (regardless of source)
    target_forbidden_reason, target_redirect = check_target_workspace_forbidden(file_path)
    if target_forbidden_reason is not None and target_redirect is not None:
        advisory = (
            target_forbidden_reason
            + " Redirect to: " + target_redirect + ". "
            "If the user explicitly overrides, note the exception in MEMORY.md."
        )
        if _feedback_events:
            try:
                _feedback_events.record(
                    cluster="methodology", sub_rule="scope_discipline",
                    decision="advisory", trigger="target_forbidden",
                    payload=payload,
                )
            except Exception:
                pass
        return {"advisory": advisory}

    # Layer 3: Always-allowed exemptions
    if is_always_allowed(file_path):
        return None

    # Layer 4: Protocol-sanctioned cross-workspace writes
    if is_protocol_sanctioned_write(tool_name, tool_input):
        return None

    if current_workspace == "unknown":
        return None

    # Layer 5: Cross-workspace scope violations
    violation, correct_ws = check_cross_workspace_write(file_path, current_workspace)
    if violation is None:
        return None

    advisory = (
        "WORKSPACE SCOPE VIOLATION DETECTED. "
        "{violation}. "
        "This work belongs in {correct_ws}. "
        "STOP and tell the user: 'This belongs in {correct_ws}. "
        "Open that workspace and continue there.' "
        "If the user explicitly overrides, note the exception in MEMORY.md."
    ).format(violation=violation, correct_ws=correct_ws)

    if _feedback_events:
        try:
            _feedback_events.record(
                cluster="methodology", sub_rule="scope_discipline",
                decision="advisory", trigger="cross_workspace_violation",
                payload=payload,
            )
        except Exception:
            pass
    return {"advisory": advisory}
