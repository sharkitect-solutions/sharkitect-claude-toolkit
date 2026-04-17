"""
drift-detection-hook.py - PreToolUse hook for document drift detection

Two-layer detection:
  Layer 1 (Relationship map): If the file being edited is a source-of-truth
    document, surfaces ALL downstream documents that must be checked.
  Layer 2 (Keyword fallback): For files not in the relationship map, falls
    back to the original keyword-overlap approach using doc-lifecycle-cache.

Non-blocking: injects additional context only.
Works in ALL workspaces that have tracked documents.

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with hookSpecificOutput.additionalContext (if drift signal)
"""

import json
import os
import sys


CACHE_PATH = os.path.join(os.getcwd(), ".tmp", "doc-lifecycle-cache.json")
RELATIONSHIP_MAP_PATH = os.path.join(os.getcwd(), ".tmp", "document-relationship-map.json")


def load_json(path):
    """Load a JSON file. Returns parsed content or empty structure."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def normalize_path(file_path):
    """Normalize a file path to forward-slash, relative form for matching."""
    normalized = file_path.replace("\\", "/")
    # Strip leading drive and workspace path to get relative path
    # Look for knowledge-base/ as the anchor
    kb_idx = normalized.find("knowledge-base/")
    if kb_idx >= 0:
        return normalized[kb_idx:]
    return normalized


def check_relationship_map(rel_map, edited_path):
    """
    Check if the edited file is a source-of-truth document.
    Returns list of downstream docs that need checking, or None if not found.
    """
    if not rel_map:
        return None

    edited_rel = normalize_path(edited_path)

    # --- Check 1: Is this a source-of-truth document? ---
    sources = rel_map.get("sources_of_truth", {})
    for source_path, source_info in sources.items():
        if edited_rel == source_path or edited_rel.endswith(source_path):
            downstream = source_info.get("downstream", [])
            entity = source_info.get("entity", "unknown")
            desc = source_info.get("description", "")
            return {
                "type": "source_of_truth",
                "entity": entity,
                "description": desc,
                "downstream": downstream
            }

    # --- Check 2: Is this a downstream doc of any source? ---
    # If editing a downstream doc, warn about which source it depends on
    upstream_sources = []
    for source_path, source_info in sources.items():
        downstream = source_info.get("downstream", [])
        for ds in downstream:
            if edited_rel == ds or edited_rel.endswith(ds):
                upstream_sources.append({
                    "source": source_path,
                    "entity": source_info.get("entity", "unknown")
                })
                break

    if upstream_sources:
        return {
            "type": "downstream_edit",
            "upstream_sources": upstream_sources
        }

    # --- Check 3: Is this in a client cluster? ---
    clusters = rel_map.get("client_clusters", {})
    for cluster_name, cluster_docs in clusters.items():
        if cluster_name.startswith("_"):
            continue
        for doc_path in cluster_docs:
            if edited_rel == doc_path or edited_rel.endswith(doc_path):
                siblings = [d for d in cluster_docs if d != doc_path]
                if siblings:
                    return {
                        "type": "cluster_member",
                        "cluster": cluster_name,
                        "siblings": siblings
                    }
                break

    # --- Check 4: Is this a KB doc being added/removed? ---
    if "knowledge-base/" in edited_rel:
        structural = rel_map.get("structural_docs", {})
        always_check = structural.get("always_check_on_kb_change", [])
        if always_check and edited_rel not in always_check:
            return {
                "type": "kb_structural",
                "check": always_check
            }

    return None


def keyword_fallback(cache, tool_input):
    """Original keyword-overlap approach as fallback."""
    if not cache:
        return []

    terms = set()

    file_path = tool_input.get("file_path", "")
    if file_path:
        parts = file_path.replace("\\", "/").replace("-", " ").replace("_", " ").split("/")
        for p in parts:
            cleaned = p.replace(".md", "").replace(".html", "").replace(".txt", "").lower()
            if cleaned and len(cleaned) > 2:
                terms.add(cleaned)

    content = tool_input.get("content", "") or tool_input.get("new_string", "")
    if content:
        words = content[:500].lower().split()
        for w in words:
            cleaned = w.strip(".,;:!?\"'()[]{}#*-_")
            if len(cleaned) > 3:
                terms.add(cleaned)

    if not terms:
        return []

    matches = []
    for doc in cache:
        doc_terms = set(doc.get("key_terms", []))
        overlap = doc_terms & terms
        if len(overlap) >= 2:
            matches.append(doc["doc_path"])
    return matches[:5]


def format_reminder(result):
    """Format the relationship-map result into a human-readable reminder."""
    if result["type"] == "source_of_truth":
        entity = result["entity"]
        desc = result["description"]
        downstream = result["downstream"]
        count = len(downstream)
        sample = downstream[:5]
        sample_str = "\n  - ".join(sample)
        more = ""
        if count > 5:
            more = "\n  ... and %d more documents." % (count - 5)
        return (
            "DRIFT DETECTION — SOURCE OF TRUTH EDIT\n"
            "You are editing a source-of-truth document for [%s]: %s\n"
            "This change may require updates to %d downstream documents:\n"
            "  - %s%s\n"
            "After completing this edit, CHECK each downstream document for consistency."
            % (entity, desc, count, sample_str, more)
        )

    elif result["type"] == "downstream_edit":
        sources = result["upstream_sources"]
        source_lines = ["  - %s (entity: %s)" % (s["source"], s["entity"]) for s in sources]
        return (
            "DRIFT DETECTION — DOWNSTREAM DOCUMENT EDIT\n"
            "This document depends on these source-of-truth documents:\n"
            "%s\n"
            "Verify your edit is consistent with the current state of the source(s) above."
            % "\n".join(source_lines)
        )

    elif result["type"] == "cluster_member":
        cluster = result["cluster"]
        siblings = result["siblings"]
        sibling_str = "\n  - ".join(siblings[:5])
        return (
            "DRIFT DETECTION — CLIENT CLUSTER EDIT\n"
            "This document is part of the [%s] cluster.\n"
            "Related documents that may need updating:\n"
            "  - %s\n"
            "Check sibling documents for consistency after this edit."
            % (cluster, sibling_str)
        )

    elif result["type"] == "kb_structural":
        check = result["check"]
        check_str = ", ".join(check)
        return (
            "DRIFT DETECTION — KB STRUCTURE CHANGE\n"
            "A knowledge-base document was modified. Verify structural docs are current: %s"
            % check_str
        )

    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Write", "Edit"):
        return 0

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0

    normalized = file_path.replace("\\", "/").lower()
    skip_patterns = [".tmp/", ".claude/", ".git/", "node_modules/", ".env", "_archive/"]
    for pattern in skip_patterns:
        if pattern in normalized:
            return 0

    # --- Layer 1: Relationship map (precise, directional) ---
    rel_map = load_json(RELATIONSHIP_MAP_PATH)
    rel_result = check_relationship_map(rel_map, file_path)

    if rel_result:
        reminder = format_reminder(rel_result)
        if reminder:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": reminder,
                }
            }
            print(json.dumps(output))
            return 0

    # --- Layer 2: Keyword fallback (broad, less precise) ---
    cache = load_json(CACHE_PATH)
    if isinstance(cache, list):
        matches = keyword_fallback(cache, tool_input)
        if matches:
            doc_list = ", ".join(matches)
            reminder = (
                "DRIFT DETECTION (keyword match): The content you are writing may relate "
                "to tracked documents that could need updating. After completing this task, "
                "consider checking: %s" % doc_list
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
