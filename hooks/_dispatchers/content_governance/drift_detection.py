"""drift_detection.py - Content-governance dispatcher sub-rule.

Source: ~/.claude/hooks/drift-detection-hook.py (662 LOC). Lift preserves
1:1 behavior of the five fire paths in source priority order:

  0. Companion prose-density check (paths matching
     */.claude/skills/*/references/*.md) -- runs BEFORE skip filter
  1. Governance nudge (3+ KB edits without governance skill invoked)
  2. Layer 1: relationship-map advisory (source_of_truth /
     downstream_edit / cluster_member / kb_structural)
  3. Layer 2: Supabase cross-workspace cache advisory
  4. Layer 3: keyword fallback (term overlap with stoplist filtered)

First applicable path returns an advisory; later paths are skipped within
a single evaluate() call.

Workspace-relative paths (.tmp/doc-lifecycle-cache.json,
.claude/drift-detection/document-relationship-map.json) are resolved
LAZILY at call time via os.getcwd() instead of at module-load time --
this corrects the source's brittle module-load-time path binding while
preserving every fire path's behavior.

Severity: ADVISORY (returns {"advisory": "<text>"}).

Source incidents:
  - wr-hq-2026-04-28-004 (governance nudge -- KB edits without governance
    skill produced correct edits but no audit trail)
  - wr-hq-2026-04-29-005 (keyword-overlap stoplist for generic structural
    terms like 'plan', 'projects', 'knowledge', 'base')
"""
from __future__ import annotations

import fnmatch
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events  # type: ignore
    from _dispatchers import _signal_extract  # type: ignore
except Exception:
    _feedback_events = None
    _signal_extract = None


# Governance-nudge tunables (preserved from source lines 44-47)
_GOVERNANCE_THRESHOLD = 3
_GOVERNANCE_SKILLS = ("hq-knowledge-governance", "lifecycle-auditor")

# Path to the H4 hybrid validator (preserved from source line 503).
# Resolved lazily at call time -- matches the workspace-path lazy pattern
# below and fixes the source's module-load-time binding so the validator
# can be relocated via $HOME under tests without re-importing the module.
def _pointer_validator_path():
    return Path.home() / ".claude" / "scripts" / "skill_judge_pointer_validator.py"

# Stoplist (preserved verbatim from source lines 250-277)
_KEYWORD_STOPLIST = frozenset({
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
    "this", "that", "these", "those", "have", "with", "from", "more",
    "some", "after", "before", "will", "been", "they", "them", "their",
    "your", "yours", "what", "when", "where", "which", "while", "would",
    "could", "should", "into", "onto", "upon", "than", "then", "thus",
    "such", "only", "also", "even", "very", "much", "many", "most",
    "each", "every", "other", "another", "again", "still", "ever",
    "just", "back", "next", "over", "down", "about", "between",
    "without", "within", "during", "since", "until", "through",
    "across", "above", "below", "around",
    "make", "made", "take", "took", "give", "gave", "find", "found",
    "show", "shown", "come", "came", "good", "best", "well", "true",
    "false", "real", "same", "like", "need", "want", "work", "works",
    "working", "working", "used", "uses", "using", "done", "doing",
    "added", "fixed", "based", "called", "complete", "completed",
})


def _workspace_cache_path():
    """Lazy: <cwd>/.tmp/doc-lifecycle-cache.json"""
    return os.path.join(os.getcwd(), ".tmp", "doc-lifecycle-cache.json")


def _workspace_rel_map_canonical():
    return os.path.join(os.getcwd(), ".claude", "drift-detection",
                        "document-relationship-map.json")


def _workspace_rel_map_legacy():
    return os.path.join(os.getcwd(), ".tmp",
                        "document-relationship-map.json")


def _supabase_cache_path():
    return str(Path.home() / ".claude" / ".tmp" / "doc-relationships.json")


def _governance_state_file():
    return Path.home() / ".claude" / ".tmp" / "drift-detection-governance-state.json"


def _resolve_relationship_map_path():
    if os.path.isfile(_workspace_rel_map_canonical()):
        return _workspace_rel_map_canonical()
    if os.path.isfile(_workspace_rel_map_legacy()):
        return _workspace_rel_map_legacy()
    return _workspace_rel_map_canonical()


def _load_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Companion prose-density check (Layer 0)
# ---------------------------------------------------------------------------

def _load_pointer_validator():
    spec = importlib.util.spec_from_file_location("sjpv", _pointer_validator_path())
    if spec is None or spec.loader is None:
        return None
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except Exception:
        return None
    return m


def _check_companion_prose_density(file_path, content):
    norm = file_path.replace("\\", "/")
    if not fnmatch.fnmatch(norm.lower(), "*/.claude/skills/*/references/*.md"):
        return None
    validator = _load_pointer_validator()
    if validator is None:
        return None
    try:
        v = validator.classify(content)
    except Exception:
        return None
    if v.classification == "PROSE":
        return (
            f"[drift-detection] companion `{file_path}` classifies as PROSE "
            f"(prose-ratio fail + citation-density fail). Skill ref companions must be POINTER per "
            f"SoT-Reference Discipline (universal-protocols.md). See "
            f"~/.claude/skills/skill-judge/references/pointer-validator.md."
        )
    if v.classification == "BORDERLINE":
        reasons = "; ".join(v.reasons) if v.reasons else "mixed line-class/citation-density signals"
        return (
            f"[drift-detection] companion `{file_path}` is BORDERLINE pointer-vs-prose. "
            f"Reasons: {reasons}. Consider tightening to clear POINTER form."
        )
    return None


# ---------------------------------------------------------------------------
# Layer 1: Relationship map
# ---------------------------------------------------------------------------

def _normalize_kb_path(file_path):
    normalized = file_path.replace("\\", "/")
    kb_idx = normalized.find("knowledge-base/")
    if kb_idx >= 0:
        return normalized[kb_idx:]
    return normalized


def _check_relationship_map(rel_map, edited_path):
    if not rel_map:
        return None
    edited_rel = _normalize_kb_path(edited_path)

    sources = rel_map.get("sources_of_truth", {})
    for source_path, source_info in sources.items():
        if edited_rel == source_path or edited_rel.endswith(source_path):
            return {
                "type": "source_of_truth",
                "entity": source_info.get("entity", "unknown"),
                "description": source_info.get("description", ""),
                "downstream": source_info.get("downstream", []),
            }

    upstream_sources = []
    for source_path, source_info in sources.items():
        downstream = source_info.get("downstream", [])
        for ds in downstream:
            if edited_rel == ds or edited_rel.endswith(ds):
                upstream_sources.append({
                    "source": source_path,
                    "entity": source_info.get("entity", "unknown"),
                })
                break
    if upstream_sources:
        return {"type": "downstream_edit", "upstream_sources": upstream_sources}

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
                        "siblings": siblings,
                    }
                break

    if "knowledge-base/" in edited_rel:
        structural = rel_map.get("structural_docs", {})
        always_check = structural.get("always_check_on_kb_change", [])
        if always_check and edited_rel not in always_check:
            return {"type": "kb_structural", "check": always_check}

    return None


def _format_rel_reminder(result):
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
            "DRIFT DETECTION -- SOURCE OF TRUTH EDIT\n"
            "You are editing a source-of-truth document for [%s]: %s\n"
            "This change may require updates to %d downstream documents:\n"
            "  - %s%s\n"
            "After completing this edit, CHECK each downstream document for consistency."
            % (entity, desc, count, sample_str, more)
        )
    if result["type"] == "downstream_edit":
        sources = result["upstream_sources"]
        source_lines = ["  - %s (entity: %s)" % (s["source"], s["entity"]) for s in sources]
        return (
            "DRIFT DETECTION -- DOWNSTREAM DOCUMENT EDIT\n"
            "This document depends on these source-of-truth documents:\n"
            "%s\n"
            "Verify your edit is consistent with the current state of the source(s) above."
            % "\n".join(source_lines)
        )
    if result["type"] == "cluster_member":
        cluster = result["cluster"]
        siblings = result["siblings"]
        sibling_str = "\n  - ".join(siblings[:5])
        return (
            "DRIFT DETECTION -- CLIENT CLUSTER EDIT\n"
            "This document is part of the [%s] cluster.\n"
            "Related documents that may need updating:\n"
            "  - %s\n"
            "Check sibling documents for consistency after this edit."
            % (cluster, sibling_str)
        )
    if result["type"] == "kb_structural":
        check_str = ", ".join(result["check"])
        return (
            "DRIFT DETECTION -- KB STRUCTURE CHANGE\n"
            "A knowledge-base document was modified. Verify structural docs are current: %s"
            % check_str
        )
    return None


# ---------------------------------------------------------------------------
# Layer 2: Supabase cache
# ---------------------------------------------------------------------------

def _find_doc_id_by_path(supabase_cache, file_path):
    if not supabase_cache:
        return None
    docs = supabase_cache.get("docs", {})
    norm_edited = file_path.replace("\\", "/").lower()
    marker = "claude code workspaces/"
    idx = norm_edited.find(marker)
    workspace_relative = None
    if idx >= 0:
        workspace_relative = norm_edited[idx + len(marker):]
    for doc_id, info in docs.items():
        doc_fp = (info.get("file_path") or "").replace("\\", "/").lower()
        if not doc_fp:
            continue
        if workspace_relative and doc_fp == workspace_relative:
            return doc_id
        if norm_edited.endswith("/" + doc_fp):
            return doc_id
        if norm_edited == doc_fp:
            return doc_id
    return None


def _check_supabase_cache(supabase_cache, file_path):
    if not supabase_cache:
        return None
    target_id = _find_doc_id_by_path(supabase_cache, file_path)
    if not target_id:
        return None
    docs = supabase_cache.get("docs", {})
    edges = supabase_cache.get("edges", [])
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


def _format_supabase_reminder(result):
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


# ---------------------------------------------------------------------------
# Layer 3: Keyword fallback
# ---------------------------------------------------------------------------

def _extract_terms_from_path(file_path):
    if not file_path:
        return set()
    terms = set()
    parts = file_path.replace("\\", "/").replace("-", " ").replace("_", " ").split("/")
    for p in parts:
        cleaned = p.replace(".md", "").replace(".html", "").replace(".txt", "").lower()
        if not cleaned or len(cleaned) <= 3:
            continue
        if cleaned in _KEYWORD_STOPLIST:
            continue
        terms.add(cleaned)
    return terms


def _extract_terms_from_content(content):
    if not content:
        return set()
    terms = set()
    words = content[:500].lower().split()
    for w in words:
        cleaned = w.strip(".,;:!?\"'()[]{}#*-_")
        if not cleaned or len(cleaned) <= 3:
            continue
        if cleaned in _KEYWORD_STOPLIST:
            continue
        terms.add(cleaned)
    return terms


def _keyword_fallback(cache, tool_input):
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
        doc_terms -= _KEYWORD_STOPLIST
        overlap = doc_terms & terms
        if len(overlap) >= 2:
            matches.append(doc["doc_path"])
    return matches[:5]


# ---------------------------------------------------------------------------
# Governance nudge
# ---------------------------------------------------------------------------

def _load_governance_state():
    sf = _governance_state_file()
    today = datetime.now().strftime("%Y-%m-%d")
    if not sf.exists():
        return {"date": today, "kb_edits": [], "nudged": False}
    try:
        s = json.loads(sf.read_text(encoding="utf-8"))
        if s.get("date") != today:
            return {"date": today, "kb_edits": [], "nudged": False}
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": today, "kb_edits": [], "nudged": False}


def _save_governance_state(state):
    sf = _governance_state_file()
    try:
        sf.parent.mkdir(parents=True, exist_ok=True)
        sf.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def _governance_skill_invoked():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = Path.home() / ".claude" / ".tmp" / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return False
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        invocations = data.get("invocations", [])
        for rec in invocations:
            name = str(rec.get("skill", "")).lower()
            for target in _GOVERNANCE_SKILLS:
                if name == target or name.endswith(":" + target) or name.startswith(target + ":"):
                    return True
    except (json.JSONDecodeError, OSError):
        pass
    return False


def _maybe_governance_nudge(file_path):
    if "knowledge-base/" not in file_path.replace("\\", "/").lower():
        return None
    state = _load_governance_state()
    if state.get("nudged"):
        if _governance_skill_invoked():
            state["kb_edits"] = []
            state["nudged"] = False
            _save_governance_state(state)
        return None
    edits = state.setdefault("kb_edits", [])
    norm = file_path.replace("\\", "/")
    if norm not in edits:
        edits.append(norm)
    _save_governance_state(state)
    if len(edits) < _GOVERNANCE_THRESHOLD:
        return None
    if _governance_skill_invoked():
        return None
    state["nudged"] = True
    _save_governance_state(state)
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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_SKIP_PATTERNS = [".tmp/", ".claude/", ".git/", "node_modules/", ".env",
                  "_archive/"]


def evaluate(payload):
    """Sub-rule entry point. Returns:
      None                       -> no contribution
      {"advisory": "<text>"}     -> first matching advisory wins
    Never raises."""
    try:
        if not isinstance(payload, dict):
            return None

        if _signal_extract is not None:
            signals = _signal_extract.extract(payload)
            tool_name = signals["tool_name"]
            file_path = signals["file_path"]
            content = signals["content_body"]
            tool_input = signals["tool_input"]
        else:
            tool_name = str(payload.get("tool_name", "") or "")
            tool_input = payload.get("tool_input") or {}
            if not isinstance(tool_input, dict):
                tool_input = {}
            file_path = str(tool_input.get("file_path", "") or "").replace("\\", "/")
            content = str(tool_input.get("content", "") or tool_input.get("new_string", "") or "")

        if tool_name not in ("Write", "Edit"):
            return None
        if not file_path:
            return None

        # Layer 0: companion prose-density (BEFORE skip filter)
        companion_finding = _check_companion_prose_density(file_path, content)
        if companion_finding:
            if _feedback_events is not None:
                try:
                    _feedback_events.record(
                        cluster="content_governance",
                        sub_rule="drift_detection",
                        decision="advisory",
                        trigger="companion_prose_density",
                        payload=payload,
                    )
                except Exception:
                    pass
            return {"advisory": companion_finding}

        # Skip filter (after companion check)
        normalized = file_path.lower()
        for pattern in _SKIP_PATTERNS:
            if pattern in normalized:
                return None

        # Layer 1a: governance nudge (returns immediately on fire)
        governance_reminder = _maybe_governance_nudge(file_path)
        if governance_reminder:
            if _feedback_events is not None:
                try:
                    _feedback_events.record(
                        cluster="content_governance",
                        sub_rule="drift_detection",
                        decision="advisory",
                        trigger="governance_nudge",
                        payload=payload,
                    )
                except Exception:
                    pass
            return {"advisory": governance_reminder}

        # Layer 1: relationship map
        rel_map = _load_json(_resolve_relationship_map_path())
        rel_result = _check_relationship_map(rel_map, file_path)
        if rel_result:
            reminder = _format_rel_reminder(rel_result)
            if reminder:
                if _feedback_events is not None:
                    try:
                        _feedback_events.record(
                            cluster="content_governance",
                            sub_rule="drift_detection",
                            decision="advisory",
                            trigger=f"relationship_map_{rel_result['type']}",
                            payload=payload,
                        )
                    except Exception:
                        pass
                return {"advisory": reminder}

        # Layer 2: Supabase cache
        supabase_cache = _load_json(_supabase_cache_path())
        sb_result = _check_supabase_cache(supabase_cache, file_path)
        if sb_result:
            reminder = _format_supabase_reminder(sb_result)
            if reminder:
                if _feedback_events is not None:
                    try:
                        _feedback_events.record(
                            cluster="content_governance",
                            sub_rule="drift_detection",
                            decision="advisory",
                            trigger="supabase_cache_match",
                            payload=payload,
                        )
                    except Exception:
                        pass
                return {"advisory": reminder}

        # Layer 3: keyword fallback
        cache = _load_json(_workspace_cache_path())
        if isinstance(cache, list):
            matches = _keyword_fallback(cache, tool_input)
            if matches:
                doc_list = ", ".join(matches)
                reminder = (
                    "DRIFT DETECTION (keyword match): The content you are writing may relate "
                    "to tracked documents that could need updating. After completing this task, "
                    "consider checking: %s" % doc_list
                )
                if _feedback_events is not None:
                    try:
                        _feedback_events.record(
                            cluster="content_governance",
                            sub_rule="drift_detection",
                            decision="advisory",
                            trigger="keyword_fallback",
                            payload=payload,
                        )
                    except Exception:
                        pass
                return {"advisory": reminder}

        return None
    except Exception:
        return None
