"""
session-start-lifecycle.py -- SessionStart hook for document lifecycle

Fires on every session start/resume. Performs three tasks:
1. Queries Supabase doc_lifecycle for all active docs, recomputes escalation states
2. Refreshes the local .tmp/doc-lifecycle-cache.json for drift-detection-hook.py
3. Checks .lifecycle-reviews/inbox/ for pending review requests
4. Outputs warnings to Claude if any docs are overdue or reviews are pending

Non-blocking: exits 0 on any failure. Never prevents session from starting.
Input: JSON on stdin (SessionStart hook format)
Output: JSON on stdout with additionalContext (if warnings exist)

Dependencies: Python stdlib only
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# .env loading
# ---------------------------------------------------------------------------

def _load_env():
    """Load .env from CWD or Sentinel workspace as fallback."""
    candidates = [
        Path.cwd() / ".env",
        Path.home() / "Documents" / "Claude Code Workspaces" / "4.- Sentinel" / ".env",
    ]
    for env_file in candidates:
        if env_file.exists():
            try:
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
                return
            except OSError:
                continue


# ---------------------------------------------------------------------------
# Workspace detection (matches supabase-sync.py detect_workspace)
# ---------------------------------------------------------------------------

def _detect_workspace():
    """Detect workspace ID from CWD path."""
    cwd = os.getcwd().lower().replace("\\", "/")
    if "skill-management" in cwd or "skill management" in cwd:
        return "skill-management-hub"
    if "workforce" in cwd or "workforce hq" in cwd or "sharkitect digital workforce" in cwd:
        return "workforce-hq"
    if "sentinel" in cwd:
        return "sentinel"
    return "unknown"


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def _supabase_get(path, params=None):
    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    api_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not base_url or not api_key:
        return None
    url = f"{base_url}/rest/v1/{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    req = urllib.request.Request(url, headers={
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _supabase_patch(path, data):
    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    api_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not base_url or not api_key:
        return False
    url = f"{base_url}/rest/v1/{path}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }, method="PATCH")
    with urllib.request.urlopen(req, timeout=10):
        return True


# ---------------------------------------------------------------------------
# Escalation logic (matches freshness-auditor.py)
# ---------------------------------------------------------------------------

def _compute_escalation(row):
    now = datetime.now(timezone.utc)
    next_review = row.get("next_review")
    deferred_at = row.get("deferred_at")
    if not next_review:
        return row.get("escalation_state", "current")
    try:
        nr = datetime.fromisoformat(next_review.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return row.get("escalation_state", "current")
    if now < nr:
        return "current"
    if not deferred_at:
        return "due"
    try:
        df = datetime.fromisoformat(deferred_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return "due"
    days_deferred = (now - df).days
    if days_deferred >= 7:
        return "critical"
    elif days_deferred >= 3:
        return "overdue"
    return "deferred"


CATEGORY_RISKS = {
    "strategy": "business direction -- stale info means wrong audience targeting",
    "client": "active project details -- outdated data leads to wrong deliverables",
    "operations": "how work gets done -- stale processes mean inconsistent execution",
    "pricing": "service costs -- wrong pricing means revenue loss",
    "brand": "brand voice/identity -- stale docs produce inconsistent messaging",
    "technical": "system behavior -- outdated configs cause tool failures",
}


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main():
    _load_env()
    workspace = _detect_workspace()
    warnings = []

    # --- 1. Query Supabase for all active docs ---
    all_docs = _supabase_get("doc_lifecycle", {
        "is_active": "eq.true",
        "select": "id,workspace,doc_path,category,next_review,escalation_state,"
                  "last_reviewed,deferred_at",
    })
    if all_docs is None:
        return 0  # Supabase unreachable -- silent exit

    # --- 2. Recompute escalation states, patch changes ---
    now = datetime.now(timezone.utc)
    non_current = []
    workspace_cache = []

    for doc in all_docs:
        correct_state = _compute_escalation(doc)
        current_state = doc.get("escalation_state", "current")

        if correct_state != current_state:
            try:
                _supabase_patch(
                    f"doc_lifecycle?id=eq.{doc['id']}",
                    {"escalation_state": correct_state,
                     "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                )
            except Exception:
                pass

        # Collect non-current docs for warnings
        if correct_state != "current":
            try:
                nr = datetime.fromisoformat(doc["next_review"].replace("Z", "+00:00"))
                days_over = (now - nr).days
            except (ValueError, AttributeError, KeyError):
                days_over = 0
            category = doc.get("category", "technical")
            non_current.append({
                "workspace": doc.get("workspace", "unknown"),
                "doc_path": doc.get("doc_path", "?"),
                "category": category,
                "state": correct_state,
                "days_overdue": days_over,
                "risk": CATEGORY_RISKS.get(category, "important information may be outdated"),
            })

        # Build cache for current workspace
        if doc.get("workspace") == workspace:
            # Generate key_terms from doc_path for drift-detection-hook
            doc_path = doc.get("doc_path", "")
            key_terms = [
                t for t in doc_path.replace("\\", "/").replace("-", " ")
                .replace("_", " ").replace(".md", "").replace(".html", "")
                .split("/") if t and len(t) > 2
            ]

            workspace_cache.append({
                "doc_path": doc_path,
                "category": doc.get("category", "technical"),
                "key_terms": key_terms,
                "next_review": doc.get("next_review"),
                "escalation_state": correct_state,
                "last_reviewed": doc.get("last_reviewed"),
                "deferred_at": doc.get("deferred_at"),
            })

    # --- 3. Write local cache ---
    tmp_dir = Path.cwd() / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    cache_path = tmp_dir / "doc-lifecycle-cache.json"
    cache_path.write_text(json.dumps(workspace_cache, indent=2), encoding="utf-8")

    # --- 3b. Fallback: if Supabase returned no docs for this workspace, run local scanner ---
    if not workspace_cache:
        doc_cache_builder = Path.home() / ".claude" / "scripts" / "doc-cache-builder.py"
        if doc_cache_builder.exists():
            import subprocess
            try:
                subprocess.run(
                    [sys.executable, str(doc_cache_builder),
                     "--path", str(Path.cwd()), "--merge", "--quiet"],
                    timeout=30, capture_output=True
                )
            except Exception:
                pass  # Non-blocking

    # --- 4. Check lifecycle review inbox ---
    inbox_dir = Path.cwd() / ".lifecycle-reviews" / "inbox"
    pending_reviews = []
    if inbox_dir.exists():
        for f in sorted(inbox_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                pending_reviews.append(data.get("doc_path", f.name))
            except (json.JSONDecodeError, OSError):
                pending_reviews.append(f.name)

    # --- 5. Build warning message ---
    if non_current:
        # Group by workspace
        by_ws = {}
        for item in non_current:
            ws = item["workspace"]
            if ws not in by_ws:
                by_ws[ws] = []
            by_ws[ws].append(item)

        parts = [f"DOCUMENT FRESHNESS ALERT: {len(non_current)} doc(s) need attention."]
        for ws, items in sorted(by_ws.items()):
            parts.append(f"  [{ws}] {len(items)} doc(s):")
            for item in items[:5]:
                parts.append(
                    f"    - {item['doc_path']} ({item['state']}, {item['days_overdue']}d overdue, "
                    f"{item['category']}): {item['risk']}"
                )

        parts.append("")
        parts.append("Consider invoking the lifecycle-auditor agent or document-lifecycle skill "
                      "to review overdue documents.")
        warnings.append("\n".join(parts))

    if pending_reviews:
        parts = [
            f"LIFECYCLE REVIEWS PENDING: {len(pending_reviews)} review request(s) "
            f"in .lifecycle-reviews/inbox/",
            "Run: python tools/lifecycle-review-watcher.py --context",
            "Then follow workflows/lifecycle-review-processing.md to process them.",
        ]
        warnings.append("\n".join(parts))

    # --- 6. Output ---
    if warnings:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n\n".join(warnings),
            }
        }
        print(json.dumps(output))

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # Non-blocking: never prevent session from starting
    sys.exit(0)
