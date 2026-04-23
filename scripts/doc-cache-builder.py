"""
doc-cache-builder.py -- Build doc-lifecycle-cache.json from local workspace files

Scans the current workspace for business/operational documents (.md, .html, .txt)
and builds a cache file that drift-detection-hook.py uses to detect when edits
may affect related documents.

This is the Supabase-independent fallback. If session-start-lifecycle.py populates
the cache from Supabase, that takes priority (it has richer metadata). This script
ensures the cache EXISTS even when:
  - Documents aren't registered in Supabase yet
  - Supabase is unreachable
  - New workspace hasn't been set up with lifecycle tracking

Usage:
    python ~/.claude/scripts/doc-cache-builder.py              # Scan CWD
    python ~/.claude/scripts/doc-cache-builder.py --path /some/workspace
    python ~/.claude/scripts/doc-cache-builder.py --merge       # Merge with existing cache (don't overwrite Supabase entries)

Output: .tmp/doc-lifecycle-cache.json in the target workspace

Dependencies: Python stdlib only.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# Directories to skip when scanning
SKIP_DIRS = {
    ".git", ".tmp", ".claude", "node_modules", "__pycache__",
    ".work-requests", ".gap-reports", ".lifecycle-reviews", "tools", ".venv", "venv",
    "_archive",
}

# File extensions to scan
SCAN_EXTENSIONS = {".md", ".html", ".txt"}

# Files to always skip (infrastructure, not business docs)
SKIP_FILES = {
    "claude.md", "memory.md", "readme.md", "changelog.md",
    "license.md", "contributing.md", ".gitignore",
}

# Category detection patterns (order matters -- first match wins)
CATEGORY_PATTERNS = [
    ("pricing", re.compile(r"pricing|price|rate|cost|fee|package|tier", re.I)),
    ("strategy", re.compile(r"strategy|vision|mission|roadmap|okr|goal|executive.summary", re.I)),
    ("brand", re.compile(r"brand|voice|tone|style.guide|identity|logo", re.I)),
    ("client", re.compile(r"client|customer|account|project|deliverable|sow|proposal", re.I)),
    ("operations", re.compile(r"sop|workflow|process|operations|onboard|checklist|playbook", re.I)),
    ("technical", re.compile(r"api|config|schema|deploy|infra|architecture|technical", re.I)),
]


def detect_category(file_path, content_sample=""):
    """Detect document category from path and content."""
    text = file_path.replace("\\", "/").replace("-", " ").replace("_", " ") + " " + content_sample
    for category, pattern in CATEGORY_PATTERNS:
        if pattern.search(text):
            return category
    return "operations"  # Default


def extract_key_terms(file_path, content=""):
    """Extract meaningful terms for drift-detection matching."""
    terms = set()

    # From file path
    path_str = file_path.replace("\\", "/")
    parts = path_str.split("/")
    for part in parts:
        cleaned = (
            part.replace("-", " ").replace("_", " ")
            .replace(".md", "").replace(".html", "").replace(".txt", "")
            .lower()
        )
        for word in cleaned.split():
            if len(word) > 2 and word not in {"the", "and", "for", "from", "with", "this", "that"}:
                terms.add(word)

    # From content (first 1000 chars -- headers and key phrases)
    if content:
        # Extract markdown headers
        headers = re.findall(r"^#+\s+(.+)$", content[:2000], re.MULTILINE)
        for header in headers:
            for word in header.lower().split():
                cleaned = word.strip(".,;:!?\"'()[]{}#*-_")
                if len(cleaned) > 3:
                    terms.add(cleaned)

        # Extract bold terms (often key concepts)
        bold = re.findall(r"\*\*([^*]+)\*\*", content[:2000])
        for phrase in bold:
            for word in phrase.lower().split():
                cleaned = word.strip(".,;:!?\"'()[]{}#*-_")
                if len(cleaned) > 3:
                    terms.add(cleaned)

    return sorted(terms)[:20]  # Cap at 20 terms


def scan_workspace(workspace_path):
    """Scan workspace for business documents and build cache entries."""
    workspace = Path(workspace_path)
    entries = []

    for root, dirs, files in os.walk(workspace):
        # Prune skip directories
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS]

        root_path = Path(root)

        for fname in files:
            # Check extension
            ext = Path(fname).suffix.lower()
            if ext not in SCAN_EXTENSIONS:
                continue

            # Skip infrastructure files
            if fname.lower() in SKIP_FILES:
                continue

            file_path = root_path / fname
            rel_path = str(file_path.relative_to(workspace)).replace("\\", "/")

            # Read content sample for term extraction
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")[:3000]
            except OSError:
                content = ""

            # Skip very small files (likely stubs)
            if len(content.strip()) < 50:
                continue

            category = detect_category(rel_path, content[:500])
            key_terms = extract_key_terms(rel_path, content)

            # Get last modified time
            try:
                mtime = os.path.getmtime(file_path)
                last_modified = __import__("datetime").datetime.fromtimestamp(
                    mtime, tz=__import__("datetime").timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
            except OSError:
                last_modified = None

            entries.append({
                "doc_path": rel_path,
                "category": category,
                "key_terms": key_terms,
                "next_review": None,  # Not tracked locally -- Supabase handles scheduling
                "escalation_state": "current",
                "last_reviewed": None,
                "last_modified": last_modified,
                "deferred_at": None,
                "source": "local-scan",  # Distinguishes from Supabase-sourced entries
            })

    return entries


def merge_with_existing(new_entries, existing_path):
    """Merge new local-scan entries with existing cache (preserve Supabase entries)."""
    if not existing_path.exists():
        return new_entries

    try:
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return new_entries

    # Keep all Supabase-sourced entries (they have richer metadata)
    supabase_entries = [e for e in existing if e.get("source") != "local-scan"]
    supabase_paths = {e["doc_path"] for e in supabase_entries}

    # Add local-scan entries only for docs NOT already tracked by Supabase
    merged = list(supabase_entries)
    for entry in new_entries:
        if entry["doc_path"] not in supabase_paths:
            merged.append(entry)

    return merged


def main():
    parser = argparse.ArgumentParser(description="Build doc-lifecycle-cache.json from local files")
    parser.add_argument("--path", default=os.getcwd(), help="Workspace path to scan")
    parser.add_argument("--merge", action="store_true",
                        help="Merge with existing cache (preserve Supabase entries)")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    workspace = Path(args.path)
    if not workspace.is_dir():
        print(f"ERROR: {workspace} is not a directory", file=sys.stderr)
        return 1

    # Scan
    entries = scan_workspace(workspace)

    # Output path
    tmp_dir = workspace / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    cache_path = tmp_dir / "doc-lifecycle-cache.json"

    # Merge or overwrite
    if args.merge:
        entries = merge_with_existing(entries, cache_path)

    # Write
    cache_path.write_text(json.dumps(entries, indent=2, ensure_ascii=True), encoding="utf-8")

    if not args.quiet:
        print(f"Doc cache built: {cache_path}")
        print(f"  Documents found: {len(entries)}")
        categories = {}
        for e in entries:
            cat = e.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items()):
            print(f"    {cat}: {count}")
        sources = {}
        for e in entries:
            src = e.get("source", "unknown")
            sources[src] = sources.get(src, 0) + 1
        if len(sources) > 1:
            print(f"  Sources: {sources}")

    return 0


if __name__ == "__main__":
    sys.exit(main())