"""
supabase-ddl-skill-nudge.py - PreToolUse BLOCKING hook for Supabase DDL skill enforcement

Fires before Supabase MCP migration / SQL execution calls. If the SQL contains
DDL keywords (ALTER TABLE, CREATE TABLE, CREATE INDEX, DROP, COMMENT ON,
CREATE/ALTER POLICY, CREATE FUNCTION, CREATE TRIGGER) AND the
`supabase-postgres-best-practices` skill has NOT been invoked this session,
DENY the call with guidance to invoke the skill first.

Why: Sessions write DDL (ALTER TABLE, GIN index on JSONB, COMMENT ON COLUMN)
without consulting the canonical skill that covers RLS-after-DDL gotchas,
index-type selection, and the apply_migration vs execute_sql trade-off
(the Phantom Migration anti-pattern).

Source: wr-2026-04-25 (Sentinel) -- non-blocking nudge silently produced
ineffective additionalContext while AI proceeded with DDL anyway. Upgraded
to blocking deny.

Reads ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json (written by
skill-invocation-tracker.py) to suppress the block if the skill is already
loaded this session.

BYPASS (any of these allows the operation)
  1. supabase-postgres-best-practices OR supabase invoked today
     (read from ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json)
  2. Recent user message in transcript contains:
       "skip ddl-nudge", "skip supabase-ddl", "skip ddl-skill-check"
  3. Hook removed from settings.json

Pure stdlib. ASCII-only output (Windows cp1252 console rule).

Input: JSON on stdin with tool_name and tool_input
Output: JSON on stdout with hookSpecificOutput.additionalContext (if nudge)
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"
STATE_FILE = TMP_DIR / "supabase-ddl-nudge-state.json"

SKILL_NAME = "supabase-postgres-best-practices"
SECONDARY_SKILL = "supabase"  # security checklist

# Tool names this hook fires on (case-insensitive substring match against
# tool_name to handle both `mcp__claude_ai_Supabase__*` and
# `mcp__supabase__*` shapes).
SUPABASE_TOOL_RE = re.compile(r"supabase", re.I)
SUPABASE_SQL_OPS = ("apply_migration", "execute_sql")

# DDL detection. Strip SQL comments first to avoid false positives from
# "CREATE TABLE..." mentioned in commentary lines.
DDL_RE = re.compile(
    r"\b("
    r"ALTER\s+TABLE|"
    r"CREATE\s+(?:OR\s+REPLACE\s+)?TABLE|"
    r"CREATE\s+(?:UNIQUE\s+)?INDEX|"
    r"DROP\s+TABLE|"
    r"DROP\s+INDEX|"
    r"COMMENT\s+ON|"
    r"CREATE\s+POLICY|"
    r"ALTER\s+POLICY|"
    r"DROP\s+POLICY|"
    r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION|"
    r"DROP\s+FUNCTION|"
    r"CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER|"
    r"DROP\s+TRIGGER|"
    r"CREATE\s+(?:OR\s+REPLACE\s+)?VIEW|"
    r"CREATE\s+(?:MATERIALIZED\s+)?VIEW|"
    r"ALTER\s+(?:OR\s+REPLACE\s+)?VIEW|"
    r"CREATE\s+SCHEMA|"
    r"DROP\s+SCHEMA|"
    r"CREATE\s+TYPE|"
    r"DROP\s+TYPE|"
    r"CREATE\s+SEQUENCE|"
    r"ALTER\s+SEQUENCE|"
    r"DROP\s+SEQUENCE|"
    r"CREATE\s+EXTENSION|"
    r"DROP\s+EXTENSION"
    r")\b",
    re.I,
)
SQL_COMMENT_LINE_RE = re.compile(r"--[^\n]*", re.M)
SQL_COMMENT_BLOCK_RE = re.compile(r"/\*.*?\*/", re.S)


def load_skill_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError):
        return []


def skill_invoked(skill_name, log):
    target = skill_name.lower()
    for entry in log:
        if entry == target or entry.endswith(":" + target) or entry.startswith(target + ":"):
            return True
    return False


def load_state():
    if not STATE_FILE.exists():
        return {"date": datetime.now().strftime("%Y-%m-%d"), "nudged": []}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if s.get("date") != datetime.now().strftime("%Y-%m-%d"):
            return {"date": datetime.now().strftime("%Y-%m-%d"), "nudged": []}
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": datetime.now().strftime("%Y-%m-%d"), "nudged": []}


def save_state(state):
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def already_nudged(state, key):
    return key in state.get("nudged", [])


def mark_nudged(state, key):
    state.setdefault("nudged", []).append(key)


def extract_sql(tool_input):
    """Pull the SQL string from any of the common parameter shapes."""
    if not isinstance(tool_input, dict):
        return ""
    for key in ("query", "sql", "statement", "migration", "migration_sql"):
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            return val
    # Some shapes nest: {"params": {"query": "..."}}
    inner = tool_input.get("params")
    if isinstance(inner, dict):
        return extract_sql(inner)
    return ""


def is_ddl(sql):
    if not sql:
        return False
    clean = SQL_COMMENT_LINE_RE.sub("", sql)
    clean = SQL_COMMENT_BLOCK_RE.sub("", clean)
    return bool(DDL_RE.search(clean))


def emit(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    }))


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


BYPASS_PHRASES = (
    "skip ddl-nudge",
    "skip ddl-skill-check",
    "skip supabase-ddl",
    "skip supabase-ddl-nudge",
)

TRANSCRIPT_USER_LOOKBACK = 3


def read_recent_user_messages(transcript_path):
    if not transcript_path:
        return []
    try:
        with open(transcript_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return []
    msgs = []
    for raw in reversed(lines):
        if len(msgs) >= TRANSCRIPT_USER_LOOKBACK:
            break
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if rec.get("type") == "user":
            content = rec.get("message", {}).get("content", "")
            if isinstance(content, list):
                content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
            msgs.append(str(content).lower())
    return msgs


def has_bypass_phrase(msgs):
    for m in msgs:
        for phrase in BYPASS_PHRASES:
            if phrase in m:
                return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = data.get("tool_name", "")
    if not tool_name.startswith("mcp__"):
        return 0
    if not SUPABASE_TOOL_RE.search(tool_name):
        return 0

    # Only fire on apply_migration / execute_sql endpoints
    tool_lower = tool_name.lower()
    if not any(op in tool_lower for op in SUPABASE_SQL_OPS):
        return 0

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    sql = extract_sql(tool_input)
    if not is_ddl(sql):
        return 0

    log = load_skill_log()

    # Bypass 1: skill invoked today (either primary or secondary)
    if skill_invoked(SKILL_NAME, log) or skill_invoked(SECONDARY_SKILL, log):
        return 0

    # Bypass 2: explicit bypass phrase in recent user message
    transcript_path = data.get("transcript_path") or ""
    recent_msgs = read_recent_user_messages(transcript_path)
    if has_bypass_phrase(recent_msgs):
        return 0

    # ---- Block ---------------------------------------------------------
    op_kind = "apply_migration" if "apply_migration" in tool_lower else "execute_sql"
    reason_lines = [
        f"BLOCKING: DDL detected in Supabase MCP call ({op_kind} via {tool_name}).",
        "",
        f"The `{SKILL_NAME}` skill MUST be invoked before applying DDL. It covers:",
        "  - RLS-after-DDL gotchas (rows become invisible without policies)",
        "  - Index type selection (B-tree vs GIN vs GiST for JSONB / arrays / FTS)",
        "  - apply_migration vs execute_sql trade-off (Phantom Migration anti-pattern:",
        "    execute_sql DDL bypasses the migrations table)",
        "  - Constraint design, function search_path hardening, lock-window analysis",
        "  - Rollback strategies and constraint-rename safety",
        "",
        f"Run `Skill {SKILL_NAME}` (or `Skill {SECONDARY_SKILL}` for security-only checks),",
        "then re-issue the migration call.",
        "",
        'To bypass for an emergency or verified-safe migration, include the phrase',
        '"skip ddl-nudge" in your next user message and retry.',
        "",
        "Source: wr-2026-04-25 (Sentinel). Past incident (2026-04-17): ALTER TABLE +",
        "GIN index on JSONB + COMMENT ON COLUMN applied without skill. Hook upgraded",
        "from soft-nudge to hard-block after Sentinel reported the soft-nudge was",
        "ineffective. See docs/mandatory-skill-invocations.md.",
    ]

    deny("\n".join(reason_lines))
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
