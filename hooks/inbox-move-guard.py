"""
inbox-move-guard.py - PreToolUse hook enforcing inbox move discipline

Fires on Bash, Write, and Edit tool calls. Four enforcement layers:

1. IMMOVABLE STATUS BLOCK: If source file has status "deferred" or "blocked",
   STOP the move entirely. Deferred items stay in inbox until processed when idle.
   Blocked items stay in inbox until their Supabase dependency completes.

2. ATTRIBUTION REQUIREMENT: For ALL inbox-to-processed moves, the source file
   MUST contain a resolution object with these required fields:
     - resolved_by: which workspace performed the work
     - what_was_done: description of actual work (not "acknowledged")
     - move_reason: "completed" | "superseded" | "duplicate"
   If any field is missing, warn the AI to add attribution before moving.

3. ACKNOWLEDGE/DEFER REJECTION: If resolution.what_was_done starts with
   "Acknowledged" or "Deferred", reject -- that's not real work.

4. WRITE/EDIT INTERCEPTION: If Write or Edit targets a processed/ directory,
   cross-check the matching inbox/ for a corresponding file. Block if:
   - A deferred or blocked item exists in inbox with the same or similar filename
   - The write would bypass the Bash mv guard by creating directly in processed/

Works globally across all workspaces and all inbox types:
  .work-requests/inbox/, .routed-tasks/inbox/, .lifecycle-reviews/inbox/

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with hookSpecificOutput.additionalContext (if violation)

Pure Python stdlib -- no external dependencies.
"""

import json
import os
import re
import sys


INBOX_DIRS = [
    ".work-requests/inbox",
    ".routed-tasks/inbox",
    ".lifecycle-reviews/inbox",
]

PROCESSED_PATTERNS = [
    "processed/",
    "processed\\",
]

VALID_MOVE_REASONS = ["completed", "superseded", "duplicate"]

FAKE_RESOLUTION_PREFIXES = [
    "acknowledged",
    "deferred",
    "noted",
    "registered",
    "logged",
    "recorded",
    "future",
    "tabled",
]


def read_json_file(filepath):
    """Read and parse a JSON file. Returns dict or None."""
    try:
        candidates = [filepath]
        if not os.path.isabs(filepath):
            cwd = os.getcwd()
            candidates.append(os.path.join(cwd, filepath))

        for candidate in candidates:
            if os.path.isfile(candidate):
                with open(candidate, "r", encoding="utf-8") as f:
                    return json.load(f)
    except (json.JSONDecodeError, OSError, TypeError):
        pass
    return None


def check_immovable(data):
    """Check if file has deferred or blocked status (cannot move to processed).
    Returns (is_immovable, reason) tuple."""
    if not data:
        return False, None
    status = str(data.get("status", "")).lower()
    if status == "blocked":
        blocked_desc = data.get("blocked_by_description", "unknown dependency")
        return True, "blocked (waiting on: %s)" % blocked_desc
    if status == "deferred":
        return True, "deferred"
    deferred_until = data.get("deferred_until", "")
    if deferred_until:
        return True, "deferred (deferred_until field set)"
    if data.get("blocked_by"):
        return True, "blocked (blocked_by field set)"
    res = data.get("resolution", {})
    if isinstance(res, dict):
        done = str(res.get("what_was_done", "")).lower()
        if done.startswith("deferred"):
            return True, "deferred (resolution says deferred)"
    return False, None


def check_attribution(data):
    """Check if file has proper attribution for moving to processed.
    Returns (is_valid, missing_fields, rejection_reason)."""
    if not data:
        return False, ["file unreadable"], None

    res = data.get("resolution")
    if not res or not isinstance(res, dict):
        return False, ["resolution object entirely missing"], None

    missing = []
    if not res.get("resolved_by"):
        missing.append("resolved_by (which workspace did the work)")
    if not res.get("what_was_done"):
        missing.append("what_was_done (description of actual work)")

    # Check for fake resolutions
    what_done = str(res.get("what_was_done", "")).lower().strip()
    for prefix in FAKE_RESOLUTION_PREFIXES:
        if what_done.startswith(prefix):
            return False, [], (
                "resolution.what_was_done starts with '%s' -- "
                "that is NOT real work. A resolution must describe "
                "ACTUAL COMPLETED WORK, not acknowledgment or deferral. "
                "If the work isn't done, the item stays in inbox." % prefix
            )

    # Check move_reason
    move_reason = str(res.get("move_reason", "")).lower().strip()
    if not move_reason:
        missing.append("move_reason (must be one of: %s)" % ", ".join(VALID_MOVE_REASONS))
    elif move_reason not in VALID_MOVE_REASONS:
        missing.append(
            "move_reason is '%s' but must be one of: %s"
            % (move_reason, ", ".join(VALID_MOVE_REASONS))
        )

    return len(missing) == 0, missing, None


def is_inbox_to_processed_move(command):
    """Detect mv commands that move from inbox/ to processed/."""
    if "mv " not in command and "move " not in command.lower() and "git mv" not in command.lower():
        return False, []

    has_inbox_source = False
    has_processed_dest = False
    source_files = []

    cmd_normalized = command.replace("\\", "/")

    for inbox in INBOX_DIRS:
        inbox_normalized = inbox.replace("\\", "/")
        if inbox_normalized in cmd_normalized:
            has_inbox_source = True
            pattern = re.escape(inbox_normalized) + r"/[^\s\"']+"
            matches = re.findall(pattern, cmd_normalized)
            source_files.extend(matches)

    for processed in PROCESSED_PATTERNS:
        if processed in cmd_normalized:
            has_processed_dest = True

    return has_inbox_source and has_processed_dest, source_files


def is_processed_dir_path(filepath):
    """Check if a file path targets a processed/ directory under an inbox type."""
    if not filepath:
        return False, None, None
    normalized = filepath.replace("\\", "/")
    for inbox_dir in INBOX_DIRS:
        # e.g. .work-requests/inbox -> .work-requests/processed
        base_dir = inbox_dir.replace("/inbox", "")
        processed_dir = base_dir + "/processed"
        if processed_dir in normalized:
            inbox_path = normalized.replace(processed_dir, base_dir + "/inbox")
            return True, inbox_path, processed_dir
    return False, None, None


def find_inbox_match(processed_path):
    """Given a path targeting processed/, find the corresponding inbox file.
    Checks both exact filename match and similar filenames."""
    normalized = processed_path.replace("\\", "/")
    filename = os.path.basename(normalized)

    for inbox_dir in INBOX_DIRS:
        base_dir = inbox_dir.replace("/inbox", "")
        processed_dir = base_dir + "/processed"
        if processed_dir in normalized:
            # Construct the inbox equivalent path
            inbox_equiv = normalized.replace(processed_dir, base_dir + "/inbox")
            # Check absolute path
            if os.path.isfile(inbox_equiv):
                return inbox_equiv
            # Also check CWD-relative
            cwd = os.getcwd()
            abs_inbox = os.path.join(cwd, inbox_equiv)
            if os.path.isfile(abs_inbox):
                return abs_inbox
            # Check inbox directory for any file with similar name
            inbox_abs = os.path.join(cwd, base_dir, "inbox")
            if os.path.isdir(inbox_abs):
                for f in os.listdir(inbox_abs):
                    if f == filename:
                        return os.path.join(inbox_abs, f)
    return None


def check_write_edit_to_processed(tool_name, tool_input):
    """Check if a Write or Edit tool call targets a processed/ directory.
    Returns (is_violation, message) tuple."""
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return False, None

    is_processed, _inbox_equiv, _processed_dir = is_processed_dir_path(file_path)
    if not is_processed:
        return False, None

    # This Write/Edit targets a processed/ directory -- potential bypass
    inbox_file = find_inbox_match(file_path)

    if inbox_file:
        # Found a corresponding inbox file -- check if deferred
        file_data = read_json_file(inbox_file)
        is_immovable, immovable_reason = check_immovable(file_data)
        if is_immovable:
            return True, (
                "STOP -- WRITE/EDIT BYPASS OF INBOX GUARD DETECTED. "
                "You are using %s to write directly to '%s' (a processed/ directory). "
                "A corresponding file exists in inbox/ at '%s' with status: %s. "
                "This is the SAME violation as moving an immovable item to processed/ -- "
                "it just bypasses the Bash mv guard. "
                "The item STAYS IN THE INBOX until the work is DONE and VERIFIED. "
                "DO NOT create files in processed/ to circumvent the move guard."
                % (tool_name, os.path.basename(file_path), os.path.basename(inbox_file),
                   immovable_reason)
            )

        # Inbox file exists but not deferred -- still check attribution
        if file_data:
            is_valid, missing, rejection = check_attribution(file_data)
            if rejection:
                return True, (
                    "STOP -- WRITE/EDIT BYPASS WITH FAKE RESOLUTION. "
                    "You are using %s to write to processed/ directory. "
                    "The inbox file '%s' has a fake resolution. %s "
                    "Fix the resolution in the inbox file first, then use 'mv' to move properly."
                    % (tool_name, os.path.basename(inbox_file), rejection)
                )
            if not is_valid:
                return True, (
                    "STOP -- WRITE/EDIT BYPASS WITHOUT ATTRIBUTION. "
                    "You are using %s to write directly to '%s'. "
                    "The inbox file '%s' is missing attribution: %s. "
                    "Add resolution to the inbox file first, then use 'mv' to move properly."
                    % (tool_name, os.path.basename(file_path),
                       os.path.basename(inbox_file), "; ".join(missing))
                )

    # No inbox match but still writing to processed/ -- warn about bypass pattern
    # Check if the content being written contains deferred indicators
    content = tool_input.get("content", "") or tool_input.get("new_string", "")
    if content:
        try:
            content_data = json.loads(content)
            is_immovable, immovable_reason = check_immovable(content_data)
            if is_immovable:
                return True, (
                    "STOP -- WRITING IMMOVABLE CONTENT TO PROCESSED/. "
                    "You are using %s to write to '%s' and the content itself "
                    "has status: %s. Items with this status belong in inbox/, not processed/. "
                    "Write to the inbox/ directory instead."
                    % (tool_name, os.path.basename(file_path), immovable_reason)
                )
        except (json.JSONDecodeError, TypeError):
            pass

    # Generic warning for any direct write to processed/
    return True, (
        "WARNING -- DIRECT WRITE TO PROCESSED/ DETECTED. "
        "You are using %s to write directly to '%s' in a processed/ directory. "
        "The standard workflow is: complete work -> add resolution to inbox file -> "
        "mv from inbox/ to processed/. Direct writes bypass the move guard. "
        "If this is intentional (e.g., adding resolution notes to an already-moved file), "
        "proceed with caution. Otherwise, use the standard inbox -> processed flow."
        % (tool_name, os.path.basename(file_path))
    )


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Layer 4: Write/Edit/MCP interception for processed/ directories
    if tool_name in ("Write", "Edit"):
        is_violation, message = check_write_edit_to_processed(tool_name, tool_input)
        if is_violation and message:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": message,
                }
            }
            print(json.dumps(output))
            return 0

    # MCP tools that create/update files (e.g., github push_files, create_or_update_file)
    if tool_name.startswith("mcp__"):
        # Check common MCP file-write parameters for processed/ paths
        for key in ("path", "file_path", "filePath", "content"):
            val = tool_input.get(key, "")
            if isinstance(val, str) and any(p in val.replace("\\", "/") for p in PROCESSED_PATTERNS):
                is_processed, _, _ = is_processed_dir_path(val)
                if is_processed:
                    inbox_file = find_inbox_match(val)
                    if inbox_file:
                        file_data = read_json_file(inbox_file)
                        is_immovable, immovable_reason = check_immovable(file_data)
                        if is_immovable:
                            output = {
                                "hookSpecificOutput": {
                                    "hookEventName": "PreToolUse",
                                    "additionalContext": (
                                        "STOP -- MCP BYPASS OF INBOX GUARD DETECTED. "
                                        "MCP tool '%s' targets a processed/ directory "
                                        "while an immovable item (%s) exists in inbox/. "
                                        "The item STAYS IN THE INBOX until the work is DONE."
                                        % (tool_name, immovable_reason)
                                    ),
                                }
                            }
                            print(json.dumps(output))
                            return 0

    # Original Bash mv/move/git-mv detection
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        is_move, source_files = is_inbox_to_processed_move(command)

        if is_move:
            for src in source_files:
                file_data = read_json_file(src)

                # Layer 1: Immovable status block (deferred or blocked)
                is_immovable, immovable_reason = check_immovable(file_data)
                if is_immovable:
                    status_label = "BLOCKED" if "blocked" in (immovable_reason or "") else "DEFERRED"
                    output = {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "additionalContext": (
                                "STOP -- %s ITEM MOVE BLOCKED. "
                                "File '%s' has status: %s. "
                                "This violates the inbox protocol (NON-NEGOTIABLE). "
                                "A task in processed/ is INVISIBLE to all future sessions. "
                                "Moving it there is equivalent to DELETING it. "
                                "DO NOT PROCEED. The item STAYS IN THE INBOX until the actual "
                                "work described in the request is DONE and VERIFIED."
                                % (status_label, os.path.basename(src), immovable_reason)
                            ),
                        }
                    }
                    print(json.dumps(output))
                    return 0

                # Layer 2: Attribution check
                is_valid, missing, rejection = check_attribution(file_data)

                if rejection:
                    output = {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "additionalContext": (
                                "STOP -- FAKE RESOLUTION DETECTED in '%s'. %s "
                                "DO NOT PROCEED with this move."
                                % (os.path.basename(src), rejection)
                            ),
                        }
                    }
                    print(json.dumps(output))
                    return 0

                if not is_valid:
                    output = {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "additionalContext": (
                                "STOP -- MISSING ATTRIBUTION for '%s'. "
                                "Before moving ANY item from inbox/ to processed/, the file "
                                "MUST contain a resolution object with ALL of these fields: "
                                "resolved_by, what_was_done, move_reason. "
                                "Missing: %s. "
                                "Add these fields to the JSON file FIRST, then retry the move. "
                                "This is required for audit trail -- we must know WHO moved it and WHY."
                                % (os.path.basename(src), "; ".join(missing))
                            ),
                        }
                    }
                    print(json.dumps(output))
                    return 0

            # All files passed -- still remind to double-check
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        "INBOX MOVE CHECK: You are moving item(s) from inbox/ to processed/. "
                        "Before proceeding, confirm: Is the actual work DONE and VERIFIED? "
                        "If the item is deferred, waiting on another phase, or not yet complete "
                        "-- it MUST stay in inbox/. Only 'done' is 'processed.'"
                    ),
                }
            }
            print(json.dumps(output))
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
