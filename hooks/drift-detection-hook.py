"""
drift-detection-hook.py - PreToolUse hook for document drift detection

Three-layer detection:
  Layer 1 (Relationship map):  Local JSON of source-of-truth docs (legacy,
    workspace-local, hand-curated).
  Layer 2 (Supabase relationship cache):  Cross-workspace document_relationships
    table contents, sync'd to ~/.claude/.tmp/doc-relationships.json by
    tools/populate-document-relationships.py. Surfaces docs that reference
    the file being edited (i.e., dependents that need re-checking).
  Layer 3 (Keyword fallback):  For files not covered by 1 or 2, fall back
    to the original keyword-overlap approach using doc-lifecycle-cache.

Non-blocking: injects additional context only.
Works in ALL workspaces.

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with hookSpecificOutput.additionalContext (if drift signal)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


CACHE_PATH = os.path.join(os.getcwd(), ".tmp", "doc-lifecycle-cache.json")
# Config file -- canonical location is workspace .claude/drift-detection/; .tmp/ is a
# migration-era fallback only. Per ~/.claude/rules/universal-protocols.md .tmp/ Hygiene
# Protocol: config files tools depend on MUST NOT live in .tmp/.
RELATIONSHIP_MAP_PATH_CANONICAL = os.path.join(os.getcwd(), ".claude", "drift-detection", "document-relationship-map.json")
RELATIONSHIP_MAP_PATH_LEGACY = os.path.join(os.getcwd(), ".tmp", "document-relationship-map.json")
SUPABASE_CACHE_PATH = str(Path.home() / ".claude" / ".tmp" / "doc-relationships.json")
WORKSPACES_ROOT = Path.home() / "Documents" / "Claude Code Workspaces"

# Governance-skill nudge tracking (wr-hq-2026-04-28-004).
# When 3+ KB edits accumulate in a session WITHOUT hq-knowledge-governance OR
# lifecycle-auditor having been invoked, that's the signature of an unstructured
# stale-doc audit -- the failure mode the WR identifies. Source: HQ session
# 2026-04-28 manually audited KB without invoking either skill, lost the audit
# trail. Threshold = 3 (single KB edit = focused work, 2 = possibly related,
# 3+ = pattern that benefits from governance methodology + persistent audit log).
GOVERNANCE_STATE_FILE = Path.home() / ".claude" / ".tmp" / "drift-detection-governance-state.json"
GOVERNANCE_THRESHOLD = 3
GOVERNANCE_SKILLS = ("hq-knowledge-governance", "lifecycle-auditor")
SKILL_LOG_DIR = Path.home() / ".claude" / ".tmp"


def resolve_relationship_map_path():
    """Return the first existing relationship-map path, preferring the canonical location.

    Canonical: <workspace>/.claude/drift-detection/document-relationship-map.json
    Legacy (transition): <workspace>/.tmp/document-relationship-map.json
    """
    if os.path.isfile(RELATIONSHIP_MAP_PATH_CANONICAL):
        return RELATIONSHIP_MAP_PATH_CANONICAL
    if os.path.isfile(RELATIONSHIP_MAP_PATH_LEGACY):
        return RELATIONSHIP_MAP_PATH_LEGACY
    # Neither exists; return the canonical path (load_json will return None gracefully)
    return RELATIONSHIP_MAP_PATH_CANONICAL


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


def find_doc_id_by_path(supabase_cache, file_path):
    """Match the edited file_path to a doc_id in the Supabase cache.
    Tries multiple normalizations: workspace-relative, full relative, basename."""
    if not supabase_cache:
        return None
    docs = supabase_cache.get("docs", {})
    norm_edited = file_path.replace("\\", "/").lower()

    # Try to extract the workspace-relative portion (strip everything before
    # 'Claude Code Workspaces/')
    marker = "claude code workspaces/"
    idx = norm_edited.find(marker)
    workspace_relative = None
    if idx >= 0:
        workspace_relative = norm_edited[idx + len(marker):]

    for doc_id, info in docs.items():
        doc_fp = (info.get("file_path") or "").replace("\\", "/").lower()
        if not doc_fp:
            continue
        # Exact match (workspace-relative form)
        if workspace_relative and doc_fp == workspace_relative:
            return doc_id
        # Endswith match (handles different absolute prefixes)
        if norm_edited.endswith("/" + doc_fp):
            return doc_id
        if norm_edited == doc_fp:
            return doc_id
    return None


def check_supabase_cache(supabase_cache, file_path):
    """Find docs that REFERENCE the file being edited.
    Returns dict {sources: [list of {file_path, filename, workspace}]} or None."""
    if not supabase_cache:
        return None

    target_id = find_doc_id_by_path(supabase_cache, file_path)
    if not target_id:
        return None

    docs = supabase_cache.get("docs", {})
    edges = supabase_cache.get("edges", [])

    # Edges where the edited doc is the TARGET = docs that reference it
    sources = []
    for edge in edges:
        if edge.get("target_id") == target_id:
            src_id = edge.get("source_id")
            src_info = docs.get(src_id, {})
            if src_info:
                sources.append({
                    "file_path": src_info.get("file_path"),
                    "filename": src_info.get("filename"),
                    "workspace": src_info.get("workspace"),
                    "type": edge.get("type", "references"),
                })
    if not sources:
        return None
    return {"sources": sources}


def format_supabase_reminder(result):
    """Format the Supabase-cache result into a human-readable reminder."""
    sources = result["sources"]
    count = len(sources)
    sample = sources[:8]
    sample_lines = []
    for s in sample:
        ws = s.get("workspace") or "?"
        fp = s.get("file_path") or s.get("filename") or "?"
        sample_lines.append(f"  - [{ws}] {fp}")
    more = ""
    if count > 8:
        more = f"\n  ... and {count - 8} more dependents."
    return (
        "DRIFT DETECTION (Supabase cross-reference graph)\n"
        f"This document is referenced by {count} other tracked document(s). "
        "Changes here may invalidate them. After this edit, review:\n"
        + "\n".join(sample_lines)
        + more
        + "\n(Re-run tools/populate-document-relationships.py to refresh the graph.)"
    )


# Generic structural / English-stopword terms that must NEVER produce a
# keyword-overlap match. Without this filter, every doc with "plan.md" in
# its name gets matched against any other doc with "plan" in its key_terms.
# Source: wr-hq-2026-04-29-005 -- editing
# projects/sharkitect/credential-registry/plan.md surfaced 5 unrelated KB
# project plans because of the generic 'plan' / 'projects' / 'knowledge'
# / 'base' overlap.
KEYWORD_STOPLIST = frozenset({
    # File / directory structure
    "plan", "plans", "spec", "specs", "readme", "memory", "claude",
    "agents", "agent", "tools", "tool", "scripts", "script", "hooks",
    "hook", "docs", "doc", "audits", "audit", "archive", "archives",
    "tmp", "temp", "tests", "test", "workflows", "workflow",
    "knowledge", "base", "projects", "project", "src", "lib", "config",
    "configs", "settings", "settings", "data", "templates", "template",
    "registry", "registries", "section", "sections", "phase", "phases",
    "step", "steps", "note", "notes", "report", "reports", "review",
    "reviews", "main", "index",
    # Generic prose stopwords / connectives that pass length>3
    "this", "that", "these", "those", "have", "with", "from", "more",
    "some", "after", "before", "will", "been", "they", "them", "their",
    "your", "yours", "what", "when", "where", "which", "while", "would",
    "could", "should", "into", "onto", "upon", "than", "then", "thus",
    "such", "only", "also", "even", "very", "much", "many", "most",
    "each", "every", "other", "another", "again", "still", "ever",
    "just", "back", "next", "over", "down", "about", "between",
    "without", "within", "during", "since", "until", "through",
    "across", "above", "below", "around",
    # Generic verbs (4+ chars) that match too widely
    "make", "made", "take", "took", "give", "gave", "find", "found",
    "show", "shown", "come", "came", "good", "best", "well", "true",
    "false", "real", "same", "like", "need", "want", "work", "works",
    "working", "working", "used", "uses", "using", "done", "doing",
    "added", "fixed", "based", "called", "complete", "completed",
})


def _extract_terms_from_path(file_path):
    """Extract candidate keyword terms from file_path with stoplist filter."""
    if not file_path:
        return set()
    terms = set()
    parts = file_path.replace("\\", "/").replace("-", " ").replace("_", " ").split("/")
    for p in parts:
        cleaned = p.replace(".md", "").replace(".html", "").replace(".txt", "").lower()
        if not cleaned or len(cleaned) <= 3:
            continue
        if cleaned in KEYWORD_STOPLIST:
            continue
        terms.add(cleaned)
    return terms


def _extract_terms_from_content(content):
    """Extract candidate keyword terms from content with stoplist filter.

    Tightened from len>3 (no stoplist) to len>3 + stoplist filter to
    prevent generic words like 'this' / 'plan' / 'phase' from causing
    spurious matches against unrelated cache docs (wr-hq-2026-04-29-005).
    """
    if not content:
        return set()
    terms = set()
    words = content[:500].lower().split()
    for w in words:
        cleaned = w.strip(".,;:!?\"'()[]{}#*-_")
        if not cleaned or len(cleaned) <= 3:
            continue
        if cleaned in KEYWORD_STOPLIST:
            continue
        terms.add(cleaned)
    return terms


def keyword_fallback(cache, tool_input):
    """Keyword-overlap fallback with topic-keyword tightening.

    Generic structural terms (plan, projects, knowledge, base, ...) and
    English-stopword-like generics (this, with, will, ...) are filtered
    out of both file-path and content extraction, so over-matches on
    generic vocabulary stop dragging in unrelated docs. Domain terms
    (proper nouns like BREVO, technical terms like vault, credential)
    pass through and produce real matches.

    Source: wr-hq-2026-04-29-005.
    """
    if not cache:
        return []

    terms = _extract_terms_from_path(tool_input.get("file_path", ""))
    terms |= _extract_terms_from_content(
        tool_input.get("content", "") or tool_input.get("new_string", "")
    )

    if not terms:
        return []

    matches = []
    for doc in cache:
        doc_terms = set(t.lower() for t in doc.get("key_terms", []))
        # Apply stoplist to cache terms too -- stoplist words in a doc's
        # key_terms list cannot count toward overlap.
        doc_terms -= KEYWORD_STOPLIST
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


def load_governance_state():
    """Return per-session KB-edit tracking state."""
    today = datetime.now().strftime("%Y-%m-%d")
    if not GOVERNANCE_STATE_FILE.exists():
        return {"date": today, "kb_edits": [], "nudged": False}
    try:
        s = json.loads(GOVERNANCE_STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "kb_edits": [], "nudged": False}
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "kb_edits": [], "nudged": False}


def save_governance_state(state):
    GOVERNANCE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        GOVERNANCE_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def governance_skill_invoked():
    """Return True if hq-knowledge-governance or lifecycle-auditor was
    invoked today (per skill-invocation-tracker log)."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = SKILL_LOG_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return False
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        invocations = data.get("invocations", [])
        for rec in invocations:
            name = str(rec.get("skill", "")).lower()
            for target in GOVERNANCE_SKILLS:
                if name == target or name.endswith(":" + target) or name.startswith(target + ":"):
                    return True
    except (json.JSONDecodeError, OSError):
        pass
    return False


def maybe_governance_nudge(file_path):
    """Track KB edit and emit governance nudge if threshold reached.

    Returns reminder string if nudge should fire, None otherwise.
    Only counts edits to knowledge-base/ paths.
    """
    if "knowledge-base/" not in file_path.replace("\\", "/").lower():
        return None
    state = load_governance_state()
    if state.get("nudged"):
        # Already nudged this session -- if skill has since been invoked,
        # reset for next stretch
        if governance_skill_invoked():
            state["kb_edits"] = []
            state["nudged"] = False
            save_governance_state(state)
        return None

    edits = state.setdefault("kb_edits", [])
    norm = file_path.replace("\\", "/")
    if norm not in edits:
        edits.append(norm)
    save_governance_state(state)

    if len(edits) < GOVERNANCE_THRESHOLD:
        return None
    if governance_skill_invoked():
        return None

    state["nudged"] = True
    save_governance_state(state)
    sample = "\n  - ".join(os.path.basename(p) for p in edits[-5:])
    return (
        "GOVERNANCE NUDGE -- KB EDIT VOLUME\n"
        f"You have edited {len(edits)} knowledge-base documents this session "
        "without invoking `hq-knowledge-governance` or `lifecycle-auditor`. "
        "That's the signature of an ad-hoc stale-doc pass that produces correct "
        "edits but leaves no audit trail.\n\n"
        f"Recent KB edits:\n  - {sample}\n\n"
        "Invoke `hq-knowledge-governance` (HQ workspace) or "
        "`lifecycle-auditor` agent BEFORE the next KB edit so the rest of this "
        "pass produces: (a) consistent K-tier classification, (b) audit log "
        "with rationale per doc, (c) reusable rubric for stale vs current, "
        "(d) Supabase governance event entries. Future sessions can verify "
        "'has this doc been audited recently' from the persistent record. "
        "Source: wr-hq-2026-04-28-004."
    )


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

    # --- Governance-skill nudge (KB-edit threshold, wr-hq-2026-04-28-004) ---
    # Fires once per session at 3+ KB edits when no governance skill invoked.
    # Independent of the relationship-map / Supabase / keyword layers below
    # so a single edit can produce both a drift signal AND a governance nudge.
    governance_reminder = maybe_governance_nudge(file_path)
    if governance_reminder:
        # Emit the governance nudge first (separate output), then continue
        # to the relationship-map layers for any drift signal on this edit.
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": governance_reminder,
            }
        }))
        # Note: we still fall through to the layers below. Claude Code accepts
        # the FIRST hook output and ignores subsequent prints from the same
        # hook -- so we return here. The drift signal will fire on the next
        # KB edit instead.
        return 0

    # --- Layer 1: Relationship map (precise, directional, hand-curated) ---
    rel_map = load_json(resolve_relationship_map_path())
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

    # --- Layer 2: Supabase document_relationships cache (cross-workspace) ---
    supabase_cache = load_json(SUPABASE_CACHE_PATH)
    sb_result = check_supabase_cache(supabase_cache, file_path)
    if sb_result:
        reminder = format_supabase_reminder(sb_result)
        if reminder:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": reminder,
                }
            }
            print(json.dumps(output))
            return 0

    # --- Layer 3: Keyword fallback (broad, less precise) ---
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
