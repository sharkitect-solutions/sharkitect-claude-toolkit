"""
asset-registration-nudge.py - PostToolUse hook for Operational Asset Registry.

Detects when Write targets create new files under infrastructure paths:
  ~/.claude/scripts/*.py
  ~/.claude/scripts/*.bat
  ~/.claude/scripts/*.sh
  ~/.claude/hooks/*.py

When a NEW file is detected (not a re-edit), drops a sync-style flag at
Skill Hub .tmp/.asset-registration-needed listing the asset + suggested
type, and injects a one-shot nudge into the tool result asking the AI to
run register-asset.py.

Debounced per-path (flag accumulates, each path logged once). Also
debounced per-session to cap nudge noise.

Source: wr-2026-04-22-004. Today's Operational Asset Registry audit found
13 live hooks + automations that were never registered because nobody
remembered to run register-asset.py at creation time. Manual discipline
fails; hook-nudge pattern (proven by skill-sync-nudge) closes the gap.

Non-blocking: injects additionalContext, never denies. Pure stdlib.

Input: JSON on stdin with tool_name, tool_input, tool_response.
Output: JSON on stdout with hookSpecificOutput.additionalContext (if new).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path


SKILL_HUB_TMP = (
    Path.home()
    / "Documents"
    / "Claude Code Workspaces"
    / "3.- Skill Management Hub"
    / ".tmp"
)
FLAG_PATH = SKILL_HUB_TMP / ".asset-registration-needed"
SESSION_TRACKER = Path(os.environ.get("TEMP", "/tmp")) / "claude_asset_nudge_session.json"

# (prefix, asset_type) pairs. First match wins.
WATCHED = [
    (str(Path.home() / ".claude" / "hooks").replace("\\", "/").lower(), "hook"),
    (str(Path.home() / ".claude" / "scripts").replace("\\", "/").lower(), "script"),
]

VALID_SUFFIXES = (".py", ".bat", ".sh")


def get_file_path(data):
    ti = data.get("tool_input", {}) or {}
    if isinstance(ti, str):
        try:
            ti = json.loads(ti)
        except (json.JSONDecodeError, TypeError):
            return ""
    return str(ti.get("file_path", "") or "")


def classify(file_path):
    """Return (asset_type, relative_name) if path is watched, else (None, None)."""
    if not file_path.lower().endswith(VALID_SUFFIXES):
        return None, None
    norm = file_path.replace("\\", "/").lower()
    for prefix, atype in WATCHED:
        if norm.startswith(prefix + "/"):
            return atype, Path(file_path).stem
    return None, None


def is_new_file(data):
    """Heuristic: a Write is 'new' if response does not indicate overwrite.

    We cannot cheaply verify pre-existence. Registration is idempotent, so
    default to True; only suppress when the response explicitly indicates
    the file already existed before this Write.
    """
    resp = data.get("tool_response") or data.get("tool_result") or {}
    if isinstance(resp, dict):
        # Claude's Write tool result often contains 'created' or similar.
        txt = json.dumps(resp).lower()
        if "already exists" in txt or "overwrote" in txt:
            return False
    # If we cannot tell, default to True -- register-asset.py is safe to
    # re-run on an existing asset (it no-ops).
    return True


def load_session_tracker():
    try:
        return json.loads(SESSION_TRACKER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"paths_nudged": [], "session_start": datetime.now().isoformat()}


def save_session_tracker(tracker):
    try:
        SESSION_TRACKER.write_text(json.dumps(tracker), encoding="utf-8")
    except OSError:
        pass


def update_flag(asset_type, file_path, name):
    SKILL_HUB_TMP.mkdir(parents=True, exist_ok=True)
    flag = {"created": datetime.now().isoformat(), "assets": []}
    if FLAG_PATH.exists():
        try:
            flag = json.loads(FLAG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    norm = file_path.replace("\\", "/")
    entry = {"type": asset_type, "path": norm, "name": name}
    if entry not in flag.setdefault("assets", []):
        flag["assets"].append(entry)
        flag["last_modified"] = datetime.now().isoformat()
    try:
        FLAG_PATH.write_text(json.dumps(flag, indent=2), encoding="utf-8")
    except OSError:
        pass


def emit_context(asset_type, file_path, name):
    msg = (
        f"ASSET REGISTRATION NUDGE: New {asset_type} created at {file_path}. "
        f"Per the Operational Asset Registry protocol (universal-protocols.md), "
        f"register this asset NOW before moving on. Command:\n"
        f"  python ~/.claude/scripts/register-asset.py \\\n"
        f"    --type {asset_type} \\\n"
        f"    --name \"{name}\" \\\n"
        f"    --workspace skill-management-hub \\\n"
        f"    --purpose \"<one line -- what it does>\" \\\n"
        f"    --platform {'local-python' if file_path.endswith('.py') else 'local-batch'}\n"
        f"Skipping registration accumulates drift; the morning + evening "
        f"drift audits will surface this as missing_from_registry. "
        f"Source: wr-2026-04-22-004. "
        f"Flagged at .tmp/.asset-registration-needed."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }))


def main():
    try:
        data = json.load(sys.stdin)
    except (OSError, json.JSONDecodeError):
        return 0

    if data.get("tool_name") not in ("Write",):
        return 0

    file_path = get_file_path(data)
    if not file_path:
        return 0

    asset_type, name = classify(file_path)
    if not asset_type:
        return 0

    if not is_new_file(data):
        return 0

    # Per-session debounce to prevent re-nudging the same path repeatedly.
    tracker = load_session_tracker()
    key = file_path.replace("\\", "/").lower()
    if key in tracker.get("paths_nudged", []):
        return 0

    update_flag(asset_type, file_path, name)
    emit_context(asset_type, file_path, name)
    tracker.setdefault("paths_nudged", []).append(key)
    save_session_tracker(tracker)
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
