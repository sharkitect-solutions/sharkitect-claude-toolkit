"""
supabase-status-nudge.py - PostToolUse hook for Supabase task status enforcement

Two responsibilities:

1. COMPLETION nudge (passive, original): when Edit/Write touches a plan file
   and content contains completion markers (COMPLETE/VERIFIED/FIXED/DONE),
   inject a context reminder to update Supabase task/project status. Debounced
   per-file per-session.

2. IN-PROGRESS active write (added 2026-05-07, wr-sentinel-2026-05-07-002):
   when Edit/Write flips a task line from `- [ ] X` to `- [!] X` (the
   in_progress marker convention from session-startup-guard.py:241), look up
   the task in Supabase via ilike fuzzy match. If exactly one pending match,
   PATCH status='in_progress' and log to activity_stream. If zero or multiple
   matches, fall back to advisory nudge. Per-task per-session debounce
   separate from completion debounce. Fail-safe: any Supabase error (no
   creds, network down, etc.) silently falls back to passive nudge.

Source incident: 1 of 299 tasks in_progress system-wide -- agents NEVER
flip tasks to in_progress. The middle of the lifecycle is invisible.
Passive nudge alone has empirically failed; this layer adds active write.

Non-blocking: injects additional context, never denies the operation.
Works in ALL workspaces.

Input: JSON on stdin with tool_name, tool_input, tool_result
Output: JSON on stdout with hookSpecificOutput.additionalContext (if nudge needed)
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Debounce trackers -- two separate files so completion nudges do not block
# in-progress writes (or vice versa) within the same session.
NUDGE_TRACKER = os.path.join(
    os.environ.get("TEMP", "/tmp"), "claude_supabase_nudge_session.json"
)
IN_PROGRESS_TRACKER = os.path.join(
    os.environ.get("TEMP", "/tmp"), "claude_supabase_in_progress_session.json"
)

# Completion markers that suggest a task/phase was just finished
COMPLETION_MARKERS = [
    "-- COMPLETE",
    "-- VERIFIED",
    "-- FIXED",
    "-- DONE",
    "COMPLETE (",       # COMPLETE (2026-04-15)
    "VERIFIED (",
    "FIXED (",
    "status: completed",
    "FULLY COMPLETE",
]

# Paths that trigger nudges
PLAN_DIRS = [
    str(Path.home() / ".claude" / "plans").replace("\\", "/").lower(),
]

# Filenames that trigger nudges regardless of directory
WATCHED_FILENAMES = [
    "memory.md",
    "plans-registry.md",
]

# Markdown checkbox in_progress marker: `- [!] task text` or `* [!] task text`,
# possibly indented. Matches per-line via re.MULTILINE.
IN_PROGRESS_LINE_RE = re.compile(
    r"^\s*[-*]\s+\[!\]\s+(.+?)\s*$",
    re.MULTILINE,
)

# Workspace detection from file path (for activity_stream attribution).
# Maps lowercase substring -> canonical workspace name. activity_stream
# CHECK constraint accepts {workforce-hq, skill-management-hub, sentinel,
# global}.
_WORKSPACE_PATH_MAP = [
    ("/1.- sharkitect digital workforce hq/", "workforce-hq"),
    ("/3.- skill management hub/", "skill-management-hub"),
    ("/4.- sentinel/", "sentinel"),
]


# ---------------------------------------------------------------------------
# Tool input extraction
# ---------------------------------------------------------------------------

def get_file_path(hook_input):
    """Extract the file path from the hook input."""
    tool_input = hook_input.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            return None
    return tool_input.get("file_path", None)


def get_new_content(hook_input):
    """Extract the new content being written from the hook input."""
    tool_input = hook_input.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            return ""
    # Write tool uses "content", Edit tool uses "new_string"
    return tool_input.get("content", "") or tool_input.get("new_string", "")


def get_old_content(hook_input):
    """Extract the OLD content being replaced (Edit only). Empty string for
    Write."""
    tool_input = hook_input.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            return ""
    return tool_input.get("old_string", "") or ""


# ---------------------------------------------------------------------------
# Path / marker detection
# ---------------------------------------------------------------------------

def is_plan_file(file_path):
    """Check if the file is a plan file or watched filename."""
    if not file_path:
        return False
    normalized = file_path.replace("\\", "/").lower()
    for plan_dir in PLAN_DIRS:
        if plan_dir in normalized:
            return True
    basename = os.path.basename(normalized)
    return basename in WATCHED_FILENAMES


def has_completion_marker(content):
    """Check if the content contains completion markers."""
    if not content:
        return False
    upper = content.upper()
    for marker in COMPLETION_MARKERS:
        if marker.upper() in upper:
            return True
    return False


def extract_in_progress_lines(content):
    """Extract task texts from `- [!] task text` lines. Returns list of
    stripped task texts (may include duplicates; dedupe at caller)."""
    if not content:
        return []
    return [m.strip() for m in IN_PROGRESS_LINE_RE.findall(content)]


def extract_newly_flipped_tasks(new_content, old_content):
    """Return list of task texts that have `[!]` marker in new_content but
    not in old_content. For Write tool calls, old_content='' so this returns
    every `[!]` line (per-task debounce protects against re-firing).

    Dedup-preserving order: if a task appears multiple times in new_content,
    it appears once in the result.
    """
    new_tasks = extract_in_progress_lines(new_content)
    old_tasks = set(extract_in_progress_lines(old_content or ""))
    seen = set()
    flipped = []
    for t in new_tasks:
        if t in old_tasks:
            continue
        if t in seen:
            continue
        seen.add(t)
        flipped.append(t)
    return flipped


def detect_workspace_from_path(file_path):
    """Map an edited file path to a canonical workspace name. Falls back to
    'global' for files under ~/.claude/ or unknown paths (matches the
    activity_stream CHECK constraint vocabulary)."""
    if not file_path:
        return "global"
    norm = file_path.replace("\\", "/").lower()
    for substr, ws in _WORKSPACE_PATH_MAP:
        if substr in norm:
            return ws
    return "global"


# ---------------------------------------------------------------------------
# Debounce trackers
# ---------------------------------------------------------------------------

def already_nudged(file_path):
    """Check if we already issued a COMPLETION nudge for this file."""
    try:
        if os.path.exists(NUDGE_TRACKER):
            with open(NUDGE_TRACKER, "r") as f:
                data = json.load(f)
            return file_path.lower() in [p.lower() for p in data.get("nudged_files", [])]
    except (json.JSONDecodeError, OSError):
        pass
    return False


def record_nudge(file_path):
    """Record that we issued a COMPLETION nudge for this file."""
    data = {"nudged_files": [], "session_start": datetime.now().isoformat()}
    try:
        if os.path.exists(NUDGE_TRACKER):
            with open(NUDGE_TRACKER, "r") as f:
                data = json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    if "nudged_files" not in data:
        data["nudged_files"] = []
    data["nudged_files"].append(file_path)
    data["last_nudge"] = datetime.now().isoformat()
    try:
        with open(NUDGE_TRACKER, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def already_in_progress_attempted(task_text):
    """Check if we already attempted an IN-PROGRESS write for this task text
    in this session."""
    try:
        if os.path.exists(IN_PROGRESS_TRACKER):
            with open(IN_PROGRESS_TRACKER, "r") as f:
                data = json.load(f)
            return task_text.strip().lower() in [
                t.lower() for t in data.get("attempted_tasks", [])
            ]
    except (json.JSONDecodeError, OSError):
        pass
    return False


def record_in_progress_attempt(task_text):
    """Record that we attempted an IN-PROGRESS write for this task text
    (regardless of outcome). Prevents re-attempt on subsequent edits in
    the same session."""
    data = {"attempted_tasks": [], "session_start": datetime.now().isoformat()}
    try:
        if os.path.exists(IN_PROGRESS_TRACKER):
            with open(IN_PROGRESS_TRACKER, "r") as f:
                data = json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    if "attempted_tasks" not in data:
        data["attempted_tasks"] = []
    data["attempted_tasks"].append(task_text.strip())
    data["last_attempt"] = datetime.now().isoformat()
    try:
        with open(IN_PROGRESS_TRACKER, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Supabase helpers (fail-safe: any failure returns None / empty without
# raising; caller falls back to passive nudge.)
# ---------------------------------------------------------------------------

def _parse_env_file(path):
    """Best-effort .env parser (no external deps)."""
    out = {}
    try:
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k:
            out[k] = v
    return out


def _detect_workspace_prefix_from_cwd():
    """Returns SKILLHUB|HQ|SENTINEL|None based on CWD (mirrors
    update-project-status.py logic)."""
    cwd = str(Path.cwd()).lower()
    if "skill management hub" in cwd:
        return "SKILLHUB"
    if "sharkitect digital workforce hq" in cwd:
        return "HQ"
    if "sentinel" in cwd:
        return "SENTINEL"
    return None


def get_supabase_creds():
    """Returns (base_url, api_key) or (None, None) on failure. Walks env
    sources the same way update-project-status.py does."""
    # First check live env (fast path -- works inside subprocess with env set)
    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    api_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if base_url and api_key:
        return base_url, api_key

    # Layer 1: walk up CWD looking for .env (5 levels)
    search = Path.cwd()
    for _ in range(5):
        env_file = search / ".env"
        if env_file.exists():
            local = _parse_env_file(env_file)
            base_url = base_url or local.get("SUPABASE_URL", "").rstrip("/")
            api_key = api_key or local.get("SUPABASE_SERVICE_ROLE_KEY", "")
            if base_url and api_key:
                return base_url, api_key
        search = search.parent

    # Layer 2: ~/.claude/.env (with workspace prefix resolution)
    global_env = _parse_env_file(Path.home() / ".claude" / ".env")
    if not global_env:
        return None, None
    prefix = _detect_workspace_prefix_from_cwd()
    if prefix:
        base_url = (
            base_url
            or global_env.get(f"{prefix}_SUPABASE_URL", "").rstrip("/")
        )
        api_key = api_key or global_env.get(
            f"{prefix}_SUPABASE_SERVICE_ROLE_KEY", ""
        )
    if not base_url:
        base_url = global_env.get("SUPABASE_URL", "").rstrip("/")
    if not api_key:
        api_key = global_env.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if base_url and api_key:
        return base_url, api_key
    return None, None


def _headers(api_key, prefer=None):
    h = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _http_get(base_url, api_key, path, timeout=8):
    """GET helper. Returns parsed JSON list or [] on failure."""
    url = f"{base_url}/rest/v1/{path}"
    try:
        req = urllib.request.Request(url, headers=_headers(api_key))
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            json.JSONDecodeError, OSError):
        return []


def _http_patch(base_url, api_key, path, data, timeout=8):
    """PATCH helper. Returns parsed JSON dict or None on failure."""
    url = f"{base_url}/rest/v1/{path}"
    try:
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            url, data=body,
            headers=_headers(api_key, prefer="return=representation"),
            method="PATCH",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result[0] if isinstance(result, list) and result else result
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            json.JSONDecodeError, OSError):
        return None


def _http_post(base_url, api_key, path, data, timeout=8):
    """POST helper. Returns True on 2xx, False on failure."""
    url = f"{base_url}/rest/v1/{path}"
    try:
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            url, data=body,
            headers=_headers(api_key, prefer="return=representation"),
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            json.JSONDecodeError, OSError):
        return False


def find_pending_task_match(base_url, api_key, task_text):
    """ilike fuzzy-match against tasks.task WHERE status=pending. Returns
    (count, [task_dicts]). Caller decides what to do based on count."""
    if not task_text:
        return 0, []
    # URL-encode the task text so commas, dots, parens, etc. don't break
    # PostgREST's reserved-char rules. ilike pattern is *...* (substring).
    quoted = urllib.parse.quote(task_text, safe="")
    query = (
        "tasks?status=eq.pending"
        f"&task=ilike.*{quoted}*"
        "&select=id,task,project,assigned_workspace"
        "&limit=10"
    )
    results = _http_get(base_url, api_key, query)
    if not isinstance(results, list):
        return 0, []
    return len(results), results


def flip_task_to_in_progress(base_url, api_key, task_id, workspace):
    """PATCH tasks set status=in_progress. Returns the updated task dict
    (truthy) on success, None on failure."""
    return _http_patch(
        base_url, api_key, f"tasks?id=eq.{task_id}",
        {
            "status": "in_progress",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_updated_by": workspace,
        },
    )


def log_in_progress_event(base_url, api_key, task, workspace, file_path):
    """POST activity_stream event_type=task_auto_in_progress. Best-effort."""
    payload = {
        "workspace": workspace,
        "platform": "supabase-status-nudge.py",
        "event_type": "task_auto_in_progress",
        "content": (
            f"Auto-flipped task to in_progress from plan-file marker: "
            f"'{(task.get('task') or '')[:120]}'"
        ),
        "metadata": {
            "task_id": task.get("id"),
            "task_text": task.get("task"),
            "project": task.get("project"),
            "file_path": file_path,
            "trigger": "in_progress_marker_detected",
        },
        "actor": workspace,
    }
    return _http_post(base_url, api_key, "activity_stream", payload)


# ---------------------------------------------------------------------------
# Output composition
# ---------------------------------------------------------------------------

def build_completion_nudge_message(file_basename):
    return (
        f"SUPABASE STATUS UPDATE NEEDED: You just wrote completion markers "
        f"to '{file_basename}'. If a task or phase was completed, update "
        f"Supabase NOW (before continuing other work):\n"
        f"  python ~/.claude/scripts/update-project-status.py task "
        f'"<task>" completed --project "<project>"\n'
        f"  python ~/.claude/scripts/update-project-status.py project "
        f'"<name>" <status> --phase "<phase>" --notes "<notes>"\n'
        f"Also update: plans-registry.md, MEMORY.md resume instructions, "
        f"and any cross-references. Supabase is the source of truth -- "
        f"if Supabase doesn't know, it didn't happen."
    )


def build_in_progress_success_message(task, file_basename):
    task_text = task.get("task", "") or ""
    project = task.get("project", "") or "unknown"
    return (
        f"SUPABASE: Auto-flipped task to in_progress.\n"
        f"  task: {task_text[:120]}\n"
        f"  project: {project}\n"
        f"  trigger: `[!]` marker in '{file_basename}'\n"
        f"  Logged to activity_stream as task_auto_in_progress."
    )


def build_in_progress_ambiguous_message(task_text, count, file_basename):
    """Message when 0 or multiple pending matches found -- AI must update
    explicitly."""
    if count == 0:
        return (
            f"SUPABASE: Detected `[!]` in_progress marker for task "
            f"'{task_text[:80]}' in '{file_basename}', but no matching "
            f"pending task found in Supabase. If this is a real task, "
            f"add it now:\n"
            f'  python ~/.claude/scripts/update-project-status.py add-task '
            f'"<task>" --project "<project>" --workspace "<workspace>"\n'
            f"Then flip to in_progress:\n"
            f'  python ~/.claude/scripts/update-project-status.py task '
            f'"<task>" in_progress --project "<project>"'
        )
    # count >= 2
    return (
        f"SUPABASE: Detected `[!]` in_progress marker for task "
        f"'{task_text[:80]}' in '{file_basename}', but {count} pending "
        f"tasks match -- ambiguous. Resolve manually:\n"
        f'  python ~/.claude/scripts/update-project-status.py task '
        f'"<exact task text>" in_progress --project "<project>"'
    )


def build_unavailable_message(task_texts, file_basename):
    """Supabase creds not available or query failed -- fall back to advisory
    nudge listing the detected in-progress markers."""
    sample = ", ".join(f"'{t[:60]}'" for t in task_texts[:3])
    if len(task_texts) > 3:
        sample += f" (+{len(task_texts) - 3} more)"
    return (
        f"SUPABASE: Detected `[!]` in_progress markers in '{file_basename}' "
        f"({sample}) but could not auto-update Supabase (creds unavailable "
        f"or network error). Update manually:\n"
        f'  python ~/.claude/scripts/update-project-status.py task '
        f'"<task>" in_progress --project "<project>"'
    )


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------

def process_in_progress_markers(hook_input, file_path):
    """Returns the in-progress nudge message (str) or None. Encapsulates the
    new active-write behavior."""
    new_content = get_new_content(hook_input)
    old_content = get_old_content(hook_input)
    flipped = extract_newly_flipped_tasks(new_content, old_content)
    if not flipped:
        return None

    # Filter out tasks already attempted this session
    pending_tasks = [t for t in flipped if not already_in_progress_attempted(t)]
    if not pending_tasks:
        return None

    creds = get_supabase_creds()
    if not creds[0] or not creds[1]:
        # Mark all attempted so we don't retry every edit, then fall back.
        for t in pending_tasks:
            record_in_progress_attempt(t)
        return build_unavailable_message(pending_tasks, os.path.basename(file_path))

    base_url, api_key = creds
    workspace = detect_workspace_from_path(file_path)

    messages = []
    for task_text in pending_tasks:
        # Mark BEFORE the lookup so failures don't cause infinite retries
        record_in_progress_attempt(task_text)
        count, matches = find_pending_task_match(base_url, api_key, task_text)
        if count == 1:
            task = matches[0]
            patched = flip_task_to_in_progress(
                base_url, api_key, task["id"], workspace
            )
            if patched:
                log_in_progress_event(
                    base_url, api_key, task, workspace, file_path
                )
                messages.append(build_in_progress_success_message(
                    task, os.path.basename(file_path)
                ))
            else:
                # Patch failed -- fall back to ambiguous-style nudge
                messages.append(build_in_progress_ambiguous_message(
                    task_text, count, os.path.basename(file_path)
                ))
        else:
            messages.append(build_in_progress_ambiguous_message(
                task_text, count, os.path.basename(file_path)
            ))

    if not messages:
        return None
    return "\n\n".join(messages)


def main():
    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw)
    except (json.JSONDecodeError, IOError):
        print(json.dumps({}))
        return

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        print(json.dumps({}))
        return

    file_path = get_file_path(hook_input)
    if not file_path or not is_plan_file(file_path):
        print(json.dumps({}))
        return

    new_content = get_new_content(hook_input)

    messages = []

    # Layer 1: in-progress active write (new, wr-sentinel-2026-05-07-002)
    in_progress_msg = process_in_progress_markers(hook_input, file_path)
    if in_progress_msg:
        messages.append(in_progress_msg)

    # Layer 2: completion nudge (original, passive)
    if has_completion_marker(new_content) and not already_nudged(file_path):
        record_nudge(file_path)
        messages.append(build_completion_nudge_message(
            os.path.basename(file_path)
        ))

    if not messages:
        print(json.dumps({}))
        return

    result = {
        "hookSpecificOutput": {
            "additionalContext": "\n\n---\n\n".join(messages)
        }
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
