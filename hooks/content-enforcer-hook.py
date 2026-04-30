"""
content-enforcer-hook.py - PreToolUse hook for content creation detection

Detects when Claude is writing client-facing content in the HQ workspace
and injects a reminder to invoke the hq-content-enforcer skill first.

Non-blocking: injects additional context, does not deny the operation.
Only active in the WORKFORCE HQ workspace (detected by CWD).

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with hookSpecificOutput.additionalContext (if content detected)
"""

import json
import os
import sys


# Content-indicating path segments and filename patterns
CONTENT_PATH_SEGMENTS = [
    "deliverables",
    "content",
    "website",
    "marketing",
    "campaigns",
    "outreach",
    "copy",
]

CONTENT_FILENAME_PATTERNS = [
    "landing",
    "email",
    "proposal",
    "form",
    "copy",
    "page",
    "post",
    "blog",
    "article",
    "social",
    "pitch",
    "script",
    "case-study",
    "case_study",
    "newsletter",
    "announcement",
    "hero",
    "cta",
    "headline",
    "tagline",
    "ad",
    "brochure",
    "flyer",
    "sow",
]

# File extensions that could be content
CONTENT_EXTENSIONS = {".md", ".html", ".txt", ".mdx", ".htm", ".docx"}

# Paths to EXCLUDE (never trigger on these). Per HQ Content Creation Rules,
# the enforcer's scope is client-facing content (landing pages, website
# copy, emails, forms, proposals, presentations, social posts, blog posts,
# ad copy, case studies, sales scripts). Internal infrastructure paths are
# out of scope. Source: wr-hq-2026-04-29-005 -- HQ session nudged on
# Edit to _archive/env-backups/README.md (internal infra doc, not client
# content).
EXCLUDE_PATHS = [
    ".tmp/",
    ".claude/",
    "tools/",
    "workflows/",
    ".git/",
    "node_modules/",
    ".env",
    "package.json",
    "settings.json",
    "MEMORY.md",
    "CLAUDE.md",
    "DOCUMENT-MAP.md",
    "INDEX.md",
    # --- Internal-infrastructure path-excludes (wr-hq-2026-04-29-005) ---
    "_archive/",        # archived legacy content, not client-facing
    "/archive/",        # alternate archive convention; leading slash to
                        # avoid matching "archive" inside marketing-strategy
                        # filenames or section names
    "docs/audits/",     # audit reports, internal infra docs
    "docs/specs/",      # system specs, internal infra docs
    ".work-requests/",  # cross-workspace coordination meta
    ".lifecycle-reviews/",  # cross-workspace coordination meta
    ".routed-tasks/",   # cross-workspace coordination meta
    "HUMAN-ACTION-REQUIRED.md",  # operational stack queue, not client doc
    "tests/",           # test files
    "knowledge-base/_internal/",  # internal KB section if present
]


def is_hq_workspace():
    """Check if current working directory is the WORKFORCE HQ workspace."""
    cwd = os.getcwd().replace("\\", "/").lower()
    return "workforce" in cwd and "hq" in cwd


def normalize_path(path):
    """Normalize path separators."""
    return path.replace("\\", "/").lower()


def is_excluded(file_path):
    """Check if file path matches any exclusion pattern."""
    normalized = normalize_path(file_path)
    for excl in EXCLUDE_PATHS:
        if excl.lower() in normalized:
            return True
    return False


def is_content_file(file_path):
    """Determine if the file being written/edited looks like client-facing content."""
    normalized = normalize_path(file_path)
    basename = os.path.basename(normalized)
    _, ext = os.path.splitext(basename)

    # Must be a content-type extension
    if ext not in CONTENT_EXTENSIONS:
        return False

    # Check path segments
    for segment in CONTENT_PATH_SEGMENTS:
        if segment in normalized:
            return True

    # Check filename patterns
    name_lower = basename.lower()
    for pattern in CONTENT_FILENAME_PATTERNS:
        if pattern in name_lower:
            return True

    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only trigger on Write and Edit
    if tool_name not in ("Write", "Edit"):
        return 0

    # Only in HQ workspace
    if not is_hq_workspace():
        return 0

    # Get the file path from tool input
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0

    # Skip excluded paths
    if is_excluded(file_path):
        return 0

    # Check if this looks like content
    if not is_content_file(file_path):
        return 0

    # Inject reminder
    reminder = (
        "CONTENT CREATION DETECTED in HQ workspace. "
        "Have you invoked the hq-content-enforcer skill? "
        "If not, STOP and invoke it before proceeding. "
        "Brand voice compliance and skill-optimized content "
        "are mandatory for all client-facing deliverables."
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": reminder,
        }
    }

    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())