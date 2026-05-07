"""
voice_loader.py -- Unified voice sample loader for content-producing skills.

Pulls the user's most recent N approved voice samples from Supabase
voice_samples table. Designed to be consumed by any content-producing skill:
humanizer, copywriting, email-composer, copy-editing, hq-content-enforcer.

The goal is autonomous voice fidelity: when AI drafts client-facing content,
it should pull recent approved samples to anchor tone, rhythm, word choice,
greetings, and closings -- not generic "opinionated" voice from training data.

Usage from a skill (Python):

    from _lib.voice_loader import (
        load_voice_samples,
        format_for_prompt,
        should_auto_load,
    )

    if should_auto_load("email", "client"):
        samples = load_voice_samples(content_type="email", audience="client", n=5)
        prompt_context = format_for_prompt(samples)
        # inject prompt_context into AI prompt before drafting

Usage from the command line (smoke test):

    python ~/.claude/scripts/_lib/voice_loader.py email client
    python ~/.claude/scripts/_lib/voice_loader.py email prospect --n 3 --json

Schema (Supabase voice_samples):
  - id (uuid, auto)
  - content (text)                  -- the actual sample text
  - status (text)                   -- approved | rejected
  - content_type (text)             -- email | proposal | slack | documentation
                                       | social | internal | code | comment
  - audience (text)                 -- client | prospect | internal | partner
  - tone (text, nullable)           -- formal | casual | technical | friendly
                                       | professional-casual
  - reason (text, nullable)         -- why approved/rejected
  - context (text, nullable)        -- situational notes
  - client_id (uuid, nullable)
  - tenant_id (uuid)
  - created_at (timestamptz, auto)

Source WR: wr-skillhub-2026-05-06-003 item 3 (humanizer 8-point upgrade).
Continuous Voice & Preference Learning Protocol (universal-protocols.md).

Stdlib only -- no external dependencies.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


# --- Configuration ---------------------------------------------------

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
DEFAULT_LIMIT = 5
MAX_LIMIT = 50
TIMEOUT_SECONDS = 8

VALID_CONTENT_TYPES = {
    "email", "proposal", "slack", "documentation",
    "social", "internal", "code", "comment",
}
VALID_AUDIENCES = {"client", "prospect", "internal", "partner"}
VALID_STATUSES = {"approved", "rejected"}

# Auto-load policy: ON for client-facing combos, OFF for internal-only or code.
# Per WR wr-skillhub-2026-05-06-003 item 3: "default to ON for client-facing
# tasks (emails, proposals, social, blog, marketing, client-deliverables) and
# OFF for internal docs."
INTERNAL_ONLY_CONTENT_TYPES = {"internal", "code", "comment"}


# --- Environment loading (mirrors voice-write.py) --------------------

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


def _parse_env_file(path):
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
    """Merge local .env and global ~/.claude/.env. Local overrides global."""
    env = {}
    global_env = Path.home() / ".claude" / ".env"
    env.update(_parse_env_file(global_env))
    local_env = Path(".env")
    if local_env.exists():
        env.update(_parse_env_file(local_env))
    return env


def _get_supabase_creds():
    """Return (base_url, api_key) tuple. Workspace-prefix fallback supported.

    Tries SUPABASE_URL / SUPABASE_KEY first, then <PREFIX>_SUPABASE_URL /
    <PREFIX>_SUPABASE_KEY (e.g. SKILLHUB_SUPABASE_URL).

    Returns (None, None) if credentials are missing -- callers should
    degrade gracefully rather than raise.
    """
    env = {**os.environ, **_load_env()}
    prefix = _detect_workspace_prefix()

    base_url = env.get("SUPABASE_URL")
    api_key = (env.get("SUPABASE_SERVICE_ROLE_KEY")
               or env.get("SUPABASE_ANON_KEY")
               or env.get("SUPABASE_KEY"))

    if not base_url and prefix:
        base_url = env.get(f"{prefix}_SUPABASE_URL")
    if not api_key and prefix:
        api_key = (env.get(f"{prefix}_SUPABASE_SERVICE_ROLE_KEY")
                   or env.get(f"{prefix}_SUPABASE_ANON_KEY")
                   or env.get(f"{prefix}_SUPABASE_KEY"))

    if not base_url or not api_key:
        return None, None
    return base_url.rstrip("/"), api_key


# --- Public API ------------------------------------------------------

def should_auto_load(content_type, audience):
    """Decide whether voice samples should auto-load for this content + audience.

    Returns True for client-facing tasks where voice fidelity matters
    (emails, proposals, social, blog drafts, marketing copy to clients).
    Returns False for internal-only content (SOPs, code comments, runbooks)
    where Sharkitect brand standards or technical precision dominate.

    Per WR wr-skillhub-2026-05-06-003 item 3 user direction:
      "default to ON for client-facing tasks (emails, proposals, social,
       blog, marketing, client-deliverables) and OFF for internal docs"
    """
    if content_type not in VALID_CONTENT_TYPES:
        return False
    if audience not in VALID_AUDIENCES:
        return False
    if content_type in INTERNAL_ONLY_CONTENT_TYPES:
        return False
    if audience == "internal":
        return False
    return True


def load_voice_samples(
    content_type=None,
    audience=None,
    n=DEFAULT_LIMIT,
    status="approved",
    tenant_id=DEFAULT_TENANT,
):
    """Pull the most recent N voice samples matching the given filters.

    Args:
        content_type: filter by content type (email, proposal, etc.) or None
        audience: filter by audience (client, prospect, etc.) or None
        n: number of samples to return (1-50, default 5)
        status: filter by status (default 'approved')
        tenant_id: tenant uuid (default the system tenant)

    Returns:
        list of dicts with keys: content, tone, reason, context, created_at,
        content_type, audience. Returns empty list on credential miss or API
        failure -- callers should fall back to no-voice-anchor mode rather
        than raising.

    Behavior:
        - Filters: status=eq.<status>, tenant_id=eq.<tenant_id>, plus optional
          content_type and audience filters.
        - Order: created_at desc.
        - Limit: clamped to [1, MAX_LIMIT].
    """
    n = max(1, min(int(n), MAX_LIMIT))

    if status not in VALID_STATUSES:
        return []
    if content_type is not None and content_type not in VALID_CONTENT_TYPES:
        return []
    if audience is not None and audience not in VALID_AUDIENCES:
        return []

    base_url, api_key = _get_supabase_creds()
    if not base_url or not api_key:
        return []

    params = {
        "status": f"eq.{status}",
        "tenant_id": f"eq.{tenant_id}",
        "select": "content,tone,reason,context,created_at,content_type,audience",
        "order": "created_at.desc",
        "limit": str(n),
    }
    if content_type:
        params["content_type"] = f"eq.{content_type}"
    if audience:
        params["audience"] = f"eq.{audience}"

    qs = urllib.parse.urlencode(params)
    url = f"{base_url}/rest/v1/voice_samples?{qs}"

    req = urllib.request.Request(url, method="GET")
    req.add_header("apikey", api_key)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            if isinstance(data, list):
                return data
            return []
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return []


def format_for_prompt(samples, max_chars_per_sample=600):
    """Format a list of voice samples as a prompt-ready context block.

    Truncates each sample's content to max_chars_per_sample for token economy.
    Includes tone and reason metadata where available.

    Returns a string block ready to inject before the drafting prompt, or an
    empty string if samples is empty.
    """
    if not samples:
        return ""

    lines = ["VOICE SAMPLES (recent approved drafts -- match this voice, do not deviate):", ""]
    for i, s in enumerate(samples, 1):
        content = (s.get("content") or "").strip()
        if len(content) > max_chars_per_sample:
            content = content[:max_chars_per_sample].rstrip() + "..."
        meta_parts = []
        ct = s.get("content_type")
        aud = s.get("audience")
        tone = s.get("tone")
        reason = s.get("reason")
        if ct and aud:
            meta_parts.append(f"{ct} -> {aud}")
        if tone:
            meta_parts.append(f"tone={tone}")
        if reason:
            meta_parts.append(f"reason: {reason}")
        meta = " | ".join(meta_parts) if meta_parts else ""

        lines.append(f"--- Sample {i}{(' (' + meta + ')') if meta else ''} ---")
        lines.append(content)
        lines.append("")

    lines.append(
        "GUIDANCE: match the rhythm, sentence length, word choice, and "
        "transitions of these samples. Do NOT default to generic 'opinionated' "
        "voice or assistant-style flourishes."
    )
    return "\n".join(lines)


def voice_anchor(content_type, audience, n=DEFAULT_LIMIT, force=False):
    """One-call convenience helper: returns the formatted prompt block or ''.

    If should_auto_load(content_type, audience) is False AND force is False,
    returns '' (no voice anchor for internal-only content).

    Otherwise pulls samples and formats them for prompt injection.
    """
    if not force and not should_auto_load(content_type, audience):
        return ""
    samples = load_voice_samples(
        content_type=content_type,
        audience=audience,
        n=n,
    )
    return format_for_prompt(samples)


# --- CLI smoke test --------------------------------------------------

def _cli_main(argv):
    """Smoke-test from the command line.

    Usage:
        python voice_loader.py <content_type> <audience> [--n N] [--json] [--force]

    Examples:
        python voice_loader.py email client
        python voice_loader.py email prospect --n 3
        python voice_loader.py internal internal --force --n 2
        python voice_loader.py email client --json
    """
    if len(argv) < 3:
        print((_cli_main.__doc__ or "").strip(), file=sys.stderr)
        return 1

    content_type = argv[1]
    audience = argv[2]
    n = DEFAULT_LIMIT
    as_json = False
    force = False
    i = 3
    while i < len(argv):
        if argv[i] == "--n" and i + 1 < len(argv):
            try:
                n = int(argv[i + 1])
            except ValueError:
                print(f"--n requires an integer, got: {argv[i + 1]}", file=sys.stderr)
                return 1
            i += 2
        elif argv[i] == "--json":
            as_json = True
            i += 1
        elif argv[i] == "--force":
            force = True
            i += 1
        else:
            i += 1

    auto = should_auto_load(content_type, audience)
    print(f"# voice_loader smoke test", file=sys.stderr)
    print(f"# content_type={content_type} audience={audience} n={n}", file=sys.stderr)
    print(f"# should_auto_load={auto} force={force}", file=sys.stderr)

    if not auto and not force:
        print(f"# auto-load OFF for this content+audience combo", file=sys.stderr)
        print(f"# (override with --force)", file=sys.stderr)
        return 0

    samples = load_voice_samples(content_type=content_type, audience=audience, n=n)
    print(f"# loaded {len(samples)} sample(s)", file=sys.stderr)

    if as_json:
        print(json.dumps(samples, indent=2, default=str))
    else:
        block = format_for_prompt(samples)
        print(block if block else "(no samples found)")

    return 0


if __name__ == "__main__":
    sys.exit(_cli_main(sys.argv))
