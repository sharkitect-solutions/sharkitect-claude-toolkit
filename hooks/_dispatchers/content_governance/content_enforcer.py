"""content_enforcer.py - Content-governance dispatcher sub-rule.

Source: ~/.claude/hooks/content-enforcer-hook.py (191 LOC). Lift preserves
1:1 behavior: HQ-workspace-only advisory nudge when the file_path looks
like client-facing content. Non-blocking. No transcript scan; no skill
log check; no state file.

Detection (preserved from source):
  Signal A: tool_name in {Write, Edit}
  Signal B: cwd is the HQ workspace (cwd lowercased contains both
            'workforce' and 'hq')
  Signal C: file_path is NOT under an excluded path (tools/, .tmp/,
            .work-requests/, etc.)
  Signal D: file_path basename has a content extension
            (.md / .html / .txt / .mdx / .htm / .docx)
  Signal E: file_path contains a content path segment
            (deliverables / content / website / marketing / campaigns /
            outreach / copy) OR a content filename pattern (landing /
            email / proposal / hero / cta / blog / case-study / etc.)

When all five hold, emit the advisory naming hq-content-enforcer.

Severity: ADVISORY (returns {"advisory": "<text>"} per sub-rule contract).

Source incidents:
  - wr-hq-2026-04-29-005 (HQ session nudged on _archive/env-backups/README.md
    which is internal infrastructure, not client content -- drove the
    EXCLUDE_PATHS additions for _archive/, docs/audits/, docs/specs/,
    .work-requests/, .lifecycle-reviews/, .routed-tasks/,
    HUMAN-ACTION-REQUIRED.md, tests/, knowledge-base/_internal/).
"""
from __future__ import annotations

import os
import sys

# Add hooks/ dir for _dispatchers package imports
_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

try:
    from _dispatchers import _feedback_events  # type: ignore
    from _dispatchers import _signal_extract  # type: ignore
except Exception:
    _feedback_events = None
    _signal_extract = None


# Content-indicating path segments (preserved verbatim from source line 20-28)
CONTENT_PATH_SEGMENTS = [
    "deliverables",
    "content",
    "website",
    "marketing",
    "campaigns",
    "outreach",
    "copy",
]

# Content-indicating filename patterns (preserved from source line 30-55)
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

# Content extensions (preserved from source line 58)
CONTENT_EXTENSIONS = {".md", ".html", ".txt", ".mdx", ".htm", ".docx"}

# Path exclusions (preserved verbatim from source line 67-94; wr-hq-2026-04-29-005)
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
    "_archive/",
    "/archive/",
    "docs/audits/",
    "docs/specs/",
    ".work-requests/",
    ".lifecycle-reviews/",
    ".routed-tasks/",
    "HUMAN-ACTION-REQUIRED.md",
    "tests/",
    "knowledge-base/_internal/",
]


def _is_hq_workspace():
    """True when current working directory is the HQ workspace.
    Match source line 97-100: cwd lowercased contains both 'workforce' AND 'hq'."""
    try:
        cwd = os.getcwd().replace("\\", "/").lower()
    except OSError:
        return False
    return "workforce" in cwd and "hq" in cwd


def _is_excluded(file_path_lower):
    """True if file_path matches any EXCLUDE_PATHS pattern. Match against
    the lowercased normalized path (signal_extract.file_path_lower)."""
    if not file_path_lower:
        return False
    for excl in EXCLUDE_PATHS:
        if excl.lower() in file_path_lower:
            return True
    return False


def _is_content_file(file_path_lower):
    """True if the file looks like client-facing content. Match preserves
    source line 117-138 logic: extension MUST be in CONTENT_EXTENSIONS,
    then path segment OR filename pattern matches."""
    if not file_path_lower:
        return False
    basename = os.path.basename(file_path_lower)
    _, ext = os.path.splitext(basename)
    if ext not in CONTENT_EXTENSIONS:
        return False
    for segment in CONTENT_PATH_SEGMENTS:
        if segment in file_path_lower:
            return True
    for pattern in CONTENT_FILENAME_PATTERNS:
        if pattern in basename:
            return True
    return False


_ADVISORY_TEXT = (
    "CONTENT CREATION DETECTED in HQ workspace. "
    "Have you invoked the hq-content-enforcer skill? "
    "If not, STOP and invoke it before proceeding. "
    "Brand voice compliance and skill-optimized content "
    "are mandatory for all client-facing deliverables."
)


def evaluate(payload):
    """Sub-rule entry point. Returns:
      None                       -> no contribution
      {"advisory": "<text>"}     -> advisory nudge
    Never raises (graceful degradation; dispatcher catches anyway)."""
    try:
        if not isinstance(payload, dict):
            return None

        # Extract canonical signals (shared helper or fallback to raw lookup)
        if _signal_extract is not None:
            signals = _signal_extract.extract(payload)
            tool_name = signals["tool_name"]
            file_path_lower = signals["file_path_lower"]
        else:
            tool_name = str(payload.get("tool_name", "") or "")
            tool_input = payload.get("tool_input") or {}
            if not isinstance(tool_input, dict):
                tool_input = {}
            file_path_lower = str(tool_input.get("file_path", "") or "").replace("\\", "/").lower()

        # Tool filter: only Write/Edit
        if tool_name not in ("Write", "Edit"):
            return None

        # Workspace filter: HQ only
        if not _is_hq_workspace():
            return None

        # File path required
        if not file_path_lower:
            return None

        # Exclusion filter
        if _is_excluded(file_path_lower):
            return None

        # Content detection
        if not _is_content_file(file_path_lower):
            return None

        # All signals fire -> advisory
        if _feedback_events is not None:
            try:
                _feedback_events.record(
                    cluster="content_governance",
                    sub_rule="content_enforcer",
                    decision="advisory",
                    trigger="hq_content_path_detected",
                    payload=payload,
                    tags={
                        "tool_name": tool_name,
                        "workspace": "workforce-hq",
                    },
                )
            except Exception:
                pass

        return {"advisory": _ADVISORY_TEXT}
    except Exception:
        return None
