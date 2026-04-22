"""
verification-before-build-enforcer.py - PostToolUse hook on Write matcher.

Enforces the Verification-Before-Building Protocol at runtime (source:
wr-2026-04-22-006; protocol in universal-protocols.md).

Trigger: Write targets infrastructure paths where new assets commonly get
created:
  ~/.claude/scripts/*.py|*.bat|*.sh
  ~/.claude/hooks/*.py
  <any workspace>/tools/*.py
  <any workspace>/workflows/*.md

Check: look at <tempdir>/claude_preflight_invocations.jsonl (written by
tools/preflight-check.py when it runs). If NO entry exists within the last
90 minutes of wall-clock time, inject a non-blocking advisory nudge asking
whether preflight-check ran.

Advisory class (not blocking) because false positives on edits-of-existing-
infra would be annoying. Also debounced per-session per-path so the nudge
fires once.

If the rule keeps getting ignored (tracked in activity stream events),
consider upgrading to BLOCKING via a PreToolUse-deny follow-up WR.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path


MARKER_PATH = Path(tempfile.gettempdir()) / "claude_preflight_invocations.jsonl"
SESSION_TRACKER = Path(os.environ.get("TEMP", "/tmp")) / "claude_vbb_enforcer_session.json"
PREFLIGHT_WINDOW = timedelta(minutes=90)


# (path_substring, label) pairs. Match any substring.
WATCHED_SUBSTRINGS = (
    ("/.claude/hooks/", "hook"),
    ("/.claude/scripts/", "script"),
    ("/tools/", "workspace-tool"),
    ("/workflows/", "workflow-sop"),
)

# File-suffix filter -- only apply nudge to new-code files, not arbitrary docs.
CODE_SUFFIXES = (".py", ".bat", ".sh", ".ts", ".js")
DOC_SUFFIXES = (".md",)


def get_file_path(data):
    ti = data.get("tool_input", {}) or {}
    if isinstance(ti, str):
        try:
            ti = json.loads(ti)
        except (json.JSONDecodeError, TypeError):
            return ""
    return str(ti.get("file_path", "") or "")


def classify(file_path):
    """Return asset_label if file_path matches a watched pattern, else None."""
    norm = file_path.replace("\\", "/").lower()
    for substr, label in WATCHED_SUBSTRINGS:
        if substr not in norm:
            continue
        # Code files in hooks/scripts/tools
        if norm.endswith(CODE_SUFFIXES):
            return label
        # Workflow markdown files only for the workflows path
        if norm.endswith(DOC_SUFFIXES) and substr == "/workflows/":
            return label
    return None


def recent_preflight_ran():
    """True if preflight-check.py fired within PREFLIGHT_WINDOW."""
    if not MARKER_PATH.exists():
        return False
    cutoff = datetime.now() - PREFLIGHT_WINDOW
    try:
        with MARKER_PATH.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = rec.get("timestamp", "")
                try:
                    t = datetime.fromisoformat(ts)
                except (ValueError, TypeError):
                    continue
                if t >= cutoff:
                    return True
    except OSError:
        return False
    return False


def load_tracker():
    try:
        return json.loads(SESSION_TRACKER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"paths_nudged": []}


def save_tracker(tracker):
    try:
        SESSION_TRACKER.write_text(json.dumps(tracker), encoding="utf-8")
    except OSError:
        pass


def emit_advisory(asset_label, file_path):
    msg = (
        f"VERIFICATION-BEFORE-BUILD NUDGE: You just wrote a new {asset_label} at "
        f"{file_path}, and no preflight-check.py invocation was recorded in the "
        f"last 90 minutes. Per Verification-Before-Building Protocol "
        f"(universal-protocols.md), run the preflight BEFORE creating new "
        f"infrastructure to catch existing assets you might extend instead:\n"
        f"  python <Skill Hub>/tools/preflight-check.py \"<what you built>\"\n"
        f"If you already checked and decided to build new, note the reasoning "
        f"in the artifact or plan. Advisory only; not blocking. "
        f"Source: wr-2026-04-22-006."
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

    if data.get("tool_name") != "Write":
        return 0

    file_path = get_file_path(data)
    if not file_path:
        return 0

    asset_label = classify(file_path)
    if not asset_label:
        return 0

    if recent_preflight_ran():
        return 0

    tracker = load_tracker()
    key = file_path.replace("\\", "/").lower()
    if key in tracker.get("paths_nudged", []):
        return 0

    emit_advisory(asset_label, file_path)
    tracker.setdefault("paths_nudged", []).append(key)
    save_tracker(tracker)
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
