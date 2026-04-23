"""
voice-write.py -- Write voice samples and corrections to Supabase

Unified write path for the voice capture + correction tracking pipeline.
Called by AI agents in any workspace when they detect user corrections,
approved/rejected content, or voice feedback.

Usage:
    python ~/.claude/scripts/voice-write.py voice <status> <content_type> <audience> "<content>" --reason "<reason>" [--tone <tone>] [--client-id <id>] [--context "<ctx>"]
    python ~/.claude/scripts/voice-write.py correction "<description>" [--workspace <ws>]
    python ~/.claude/scripts/voice-write.py stats [--days 30]

Examples:
    # Log a rejected email draft with reason
    python ~/.claude/scripts/voice-write.py voice rejected email client "Hey there! Hope this finds you well..." --reason "Too generic, never use hope this finds you well"

    # Log an approved email draft
    python ~/.claude/scripts/voice-write.py voice approved email client "Marcus, dashboard updates are ready for review." --reason "Perfect tone for existing client" --tone casual

    # Log a user correction event
    python ~/.claude/scripts/voice-write.py correction "User corrected email tone: too formal for existing client. Wants casual." --workspace workforce-hq

    # Show capture stats
    python ~/.claude/scripts/voice-write.py stats --days 7

Dependencies: Python stdlib only (no external packages)
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ── Configuration ────────────────────────────────────────────────────

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

VALID_STATUSES = {"approved", "rejected"}
VALID_CONTENT_TYPES = {"email", "proposal", "slack", "documentation", "social", "internal", "code", "comment"}
VALID_AUDIENCES = {"client", "prospect", "internal", "partner"}
VALID_TONES = {"formal", "casual", "technical", "friendly", "professional-casual"}


# ── Environment ──────────────────────────────────────────────────────

def _detect_workspace_prefix():
    """Infer workspace prefix from CWD. Returns '' if unknown."""
    s = os.getcwd().replace("\\", "/").lower()
    if "skill management hub" in s or "/3.-" in s:
        return "SKILLHUB"
    if ("workforce" in s and "hq" in s) or "/1.-" in s:
        return "HQ"
    if "sentinel" in s or "/4.-" in s:
        return "SENTINEL"
    return ""


def _parse_env(path):
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k:
            out[k] = v
    return out


def _load_env():
    """Load credentials from local .env + global ~/.claude/.env with
    workspace-prefix fallback (e.g. SKILLHUB_SUPABASE_URL -> SUPABASE_URL).
    """
    loaded_any = False

    # Layer 1: workspace-local candidates (CWD, script-adjacent, all workspace dirs)
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    ws_root = Path.home() / "Documents" / "Claude Code Workspaces"
    if ws_root.is_dir():
        for d in ws_root.iterdir():
            if d.is_dir():
                candidates.append(d / ".env")
    for env_file in candidates:
        if env_file.exists():
            for k, v in _parse_env(env_file).items():
                os.environ.setdefault(k, v)
            loaded_any = True

    # Layer 2: global ~/.claude/.env with workspace prefix resolution
    global_env = _parse_env(Path.home() / ".claude" / ".env")
    if global_env:
        prefix = _detect_workspace_prefix()
        if prefix:
            plen = len(prefix) + 1
            for k, v in global_env.items():
                if k.startswith(f"{prefix}_"):
                    os.environ.setdefault(k[plen:], v)
                    os.environ.setdefault(k, v)
        for k, v in global_env.items():
            if not any(k.startswith(f"{p}_") for p in ("SKILLHUB", "HQ", "SENTINEL")):
                os.environ.setdefault(k, v)
        loaded_any = True

    return loaded_any


def _get_supabase():
    """Get Supabase URL and key from environment."""
    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    api_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not base_url or not api_key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set", file=sys.stderr)
        sys.exit(1)
    return base_url, api_key


# ── Supabase Writers ─────────────────────────────────────────────────

def _supabase_post(base_url, api_key, table, data):
    """POST to a Supabase table. Returns response data or None."""
    url = f"{base_url}/rest/v1/{table}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result[0] if isinstance(result, list) and result else result
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        print(f"ERROR: Supabase {table} write failed: HTTP {e.code} - {body_text}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Supabase {table} write failed: {e}", file=sys.stderr)
        return None


def _supabase_get(base_url, api_key, table, params=""):
    """GET from a Supabase table."""
    url = f"{base_url}/rest/v1/{table}?{params}" if params else f"{base_url}/rest/v1/{table}"
    req = urllib.request.Request(url, headers={
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Prefer": "count=exact",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            count_header = resp.headers.get("content-range", "")
            data = json.loads(resp.read().decode("utf-8"))
            total = count_header.split("/")[-1] if "/" in count_header else "?"
            return data, total
    except Exception as e:
        print(f"ERROR: Supabase {table} read failed: {e}", file=sys.stderr)
        return [], "?"


# ── Commands ─────────────────────────────────────────────────────────

def cmd_voice(args):
    """Write a voice sample to Supabase voice_samples table."""
    if len(args) < 4:
        print("Usage: voice-write.py voice <status> <content_type> <audience> \"<content>\" --reason \"<reason>\"")
        print(f"  status: {', '.join(sorted(VALID_STATUSES))}")
        print(f"  content_type: {', '.join(sorted(VALID_CONTENT_TYPES))}")
        print(f"  audience: {', '.join(sorted(VALID_AUDIENCES))}")
        return 1

    status = args[0]
    content_type = args[1]
    audience = args[2]
    content = args[3]

    # Validate
    if status not in VALID_STATUSES:
        print(f"ERROR: status must be one of: {', '.join(sorted(VALID_STATUSES))}", file=sys.stderr)
        return 1
    if content_type not in VALID_CONTENT_TYPES:
        print(f"ERROR: content_type must be one of: {', '.join(sorted(VALID_CONTENT_TYPES))}", file=sys.stderr)
        return 1
    if audience not in VALID_AUDIENCES:
        print(f"ERROR: audience must be one of: {', '.join(sorted(VALID_AUDIENCES))}", file=sys.stderr)
        return 1

    # Parse optional args
    reason = ""
    tone = ""
    client_id = None
    context = ""
    i = 4
    while i < len(args):
        if args[i] == "--reason" and i + 1 < len(args):
            reason = args[i + 1]
            i += 2
        elif args[i] == "--tone" and i + 1 < len(args):
            tone = args[i + 1]
            i += 2
        elif args[i] == "--client-id" and i + 1 < len(args):
            client_id = args[i + 1]
            i += 2
        elif args[i] == "--context" and i + 1 < len(args):
            context = args[i + 1]
            i += 2
        else:
            i += 1

    base_url, api_key = _get_supabase()

    data = {
        "content": content,
        "status": status,
        "content_type": content_type,
        "audience": audience,
        "tone": tone or None,
        "reason": reason or None,
        "context": context or None,
        "client_id": client_id,
        "tenant_id": DEFAULT_TENANT,
    }

    result = _supabase_post(base_url, api_key, "voice_samples", data)
    if result:
        sample_id = result.get("id", "?")
        print(f"Voice sample written: {status} {content_type}/{audience} (id: {sample_id})")
        return 0
    return 1


def cmd_correction(args):
    """Write a correction event to Supabase activity_stream."""
    if len(args) < 1:
        print("Usage: voice-write.py correction \"<description>\" [--workspace <ws>]")
        return 1

    description = args[0]
    workspace = "unknown"
    i = 1
    while i < len(args):
        if args[i] == "--workspace" and i + 1 < len(args):
            workspace = args[i + 1]
            i += 2
        else:
            i += 1

    base_url, api_key = _get_supabase()

    data = {
        "tenant_id": DEFAULT_TENANT,
        "workspace": workspace,
        "event_type": "correction",
        "content": description,
        "actor": "ai-agent",
        "metadata": json.dumps({
            "source": "voice-write.py",
            "capture_type": "real-time",
        }),
    }

    result = _supabase_post(base_url, api_key, "activity_stream", data)
    if result:
        print(f"Correction logged to activity_stream (workspace: {workspace})")
        return 0
    return 1


def cmd_stats(args):
    """Show voice sample and correction capture statistics."""
    days = 30
    i = 0
    while i < len(args):
        if args[i] == "--days" and i + 1 < len(args):
            days = int(args[i + 1])
            i += 2
        else:
            i += 1

    base_url, api_key = _get_supabase()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")

    # Voice samples
    samples, total_samples = _supabase_get(
        base_url, api_key, "voice_samples",
        f"created_at=gte.{since}&order=created_at.desc&limit=100"
    )

    # Corrections from activity_stream
    corrections, total_corrections = _supabase_get(
        base_url, api_key, "activity_stream",
        f"event_type=eq.correction&timestamp=gte.{since}&order=timestamp.desc&limit=100"
    )

    print(f"Voice & Correction Stats (last {days} days)")
    print("=" * 50)

    # Voice sample breakdown
    approved = sum(1 for s in samples if s.get("status") == "approved")
    rejected = sum(1 for s in samples if s.get("status") == "rejected")
    print(f"\nVoice Samples: {len(samples)} total ({total_samples} all-time)")
    print(f"  Approved: {approved}")
    print(f"  Rejected: {rejected}")

    # By content type
    by_type = {}
    for s in samples:
        ct = s.get("content_type", "unknown")
        by_type[ct] = by_type.get(ct, 0) + 1
    if by_type:
        print("  By type:", ", ".join(f"{k}={v}" for k, v in sorted(by_type.items())))

    # By audience
    by_audience = {}
    for s in samples:
        a = s.get("audience", "unknown")
        by_audience[a] = by_audience.get(a, 0) + 1
    if by_audience:
        print("  By audience:", ", ".join(f"{k}={v}" for k, v in sorted(by_audience.items())))

    # Corrections
    print(f"\nCorrections: {len(corrections)} total ({total_corrections} all-time)")
    by_ws = {}
    for c in corrections:
        ws = c.get("workspace", "unknown")
        by_ws[ws] = by_ws.get(ws, 0) + 1
    if by_ws:
        print("  By workspace:", ", ".join(f"{k}={v}" for k, v in sorted(by_ws.items())))

    # Synthesis readiness
    print(f"\nSynthesis Readiness:")
    groups = {}
    for s in samples:
        key = f"{s.get('content_type', '?')}/{s.get('audience', '?')}"
        groups[key] = groups.get(key, 0) + 1
    for key, count in sorted(groups.items()):
        ready = "READY" if count >= 3 else f"need {3 - count} more"
        print(f"  {key}: {count} samples ({ready})")

    if not groups:
        print("  No samples yet. Run voice profiling exercise in HQ to seed data.")

    return 0


# ── Main ─────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: voice-write.py <voice|correction|stats> [args...]")
        print("  voice      -- Write a voice sample (approved/rejected content)")
        print("  correction -- Log a user correction event")
        print("  stats      -- Show capture statistics")
        return 1

    _load_env()

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "voice":
        return cmd_voice(args)
    elif cmd == "correction":
        return cmd_correction(args)
    elif cmd == "stats":
        return cmd_stats(args)
    else:
        print(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())