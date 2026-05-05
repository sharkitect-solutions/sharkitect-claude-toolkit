"""supabase_ddl.py - Methodology dispatcher sub-rule.

Source: supabase-ddl-skill-nudge.py (HARD GATE on Supabase MCP DDL calls
without supabase-postgres-best-practices skill engaged).

Behavior preserved 1:1 from source:
  Trigger: tool_name starts with "mcp__" AND contains "supabase" AND
           operation is apply_migration or execute_sql AND DDL detected
           in extracted SQL string. SQL comments are stripped before
           DDL detection to avoid false positives from commentary.

DDL keywords detected: ALTER TABLE, CREATE TABLE (incl. OR REPLACE),
CREATE [UNIQUE] INDEX, DROP TABLE/INDEX, COMMENT ON,
CREATE/ALTER/DROP POLICY, CREATE [OR REPLACE] FUNCTION, DROP FUNCTION,
CREATE [OR REPLACE] TRIGGER, DROP TRIGGER, CREATE [MATERIALIZED] VIEW,
ALTER [OR REPLACE] VIEW, CREATE/DROP SCHEMA, CREATE/DROP TYPE,
CREATE/ALTER/DROP SEQUENCE, CREATE/DROP EXTENSION.

SQL extraction: tries query / sql / statement / migration / migration_sql
keys; recurses into params if nested.

Bypasses (any one passes through):
  1. Skill log: supabase-postgres-best-practices OR supabase invoked today
  2. Transcript bypass phrase: "skip ddl-nudge", "skip ddl-skill-check",
     "skip supabase-ddl", "skip supabase-ddl-nudge"
  3. Intent detection: user-driven mode via shared intent_detection.py
     (NEW layer added during consolidation)

Severity: HARD GATE (returns {"decision": "deny", "reason": ...})

Source incident: wr-2026-04-25 (Sentinel) - non-blocking nudge silently
produced ineffective additionalContext while AI proceeded with DDL anyway.
Upgraded from soft-nudge to hard-block. Past incident 2026-04-17:
ALTER TABLE + GIN index on JSONB + COMMENT ON COLUMN applied without skill.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_SCRIPTS_LIB = os.path.expanduser("~/.claude/scripts/_lib")
if _SCRIPTS_LIB not in sys.path:
    sys.path.insert(0, _SCRIPTS_LIB)
try:
    from intent_detection import is_user_driven  # type: ignore
except Exception:
    is_user_driven = None

_HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
try:
    from _dispatchers import _feedback_events
except Exception:
    _feedback_events = None


TMP_DIR = Path.home() / ".claude" / ".tmp"

SKILL_NAME = "supabase-postgres-best-practices"
SECONDARY_SKILL = "supabase"

SUPABASE_TOOL_RE = re.compile(r"supabase", re.I)
SUPABASE_SQL_OPS = ("apply_migration", "execute_sql")

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

BYPASS_PHRASES = (
    "skip ddl-nudge",
    "skip ddl-skill-check",
    "skip supabase-ddl",
    "skip supabase-ddl-nudge",
)
TRANSCRIPT_USER_LOOKBACK = 3


def _load_skill_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return []


def _skill_invoked(name, log):
    target = name.lower()
    return any(
        e == target or e.endswith(":" + target) or e.startswith(target + ":")
        for e in log
    )


def _read_recent_user_messages(transcript_path):
    if not transcript_path:
        return []
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return []
        msgs = []
        with p.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if rec.get("type") != "user":
                    continue
                msg = rec.get("message") or {}
                content = msg.get("content")
                if isinstance(content, str):
                    msgs.append(content)
                elif isinstance(content, list):
                    for blk in content:
                        if isinstance(blk, dict) and blk.get("type") == "text":
                            msgs.append(blk.get("text", ""))
        return msgs[-TRANSCRIPT_USER_LOOKBACK:]
    except Exception:
        return []


def _has_bypass_phrase(messages):
    for txt in messages:
        low = txt.lower()
        if any(phrase in low for phrase in BYPASS_PHRASES):
            return True
    return False


def _extract_sql(tool_input):
    if not isinstance(tool_input, dict):
        return ""
    for key in ("query", "sql", "statement", "migration", "migration_sql"):
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            return val
    inner = tool_input.get("params")
    if isinstance(inner, dict):
        return _extract_sql(inner)
    return ""


def _is_ddl(sql):
    if not sql:
        return False
    clean = SQL_COMMENT_LINE_RE.sub("", sql)
    clean = SQL_COMMENT_BLOCK_RE.sub("", clean)
    return bool(DDL_RE.search(clean))


def evaluate(payload):
    """Evaluate supabase_ddl sub-rule.

    Returns:
      None                                  -> sub-rule did not trigger
      {"decision": "deny", "reason": "..."} -> HARD GATE
    """
    tool_name = payload.get("tool_name", "")
    if not tool_name.startswith("mcp__"):
        return None
    if not SUPABASE_TOOL_RE.search(tool_name):
        return None

    tool_lower = tool_name.lower()
    if not any(op in tool_lower for op in SUPABASE_SQL_OPS):
        return None

    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            tool_input = {}

    sql = _extract_sql(tool_input)
    if not _is_ddl(sql):
        return None

    # Bypass: skill log
    log = _load_skill_log()
    if _skill_invoked(SKILL_NAME, log) or _skill_invoked(SECONDARY_SKILL, log):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="supabase_ddl",
                decision="pass_through", trigger="skill_log_bypass",
                payload=payload,
            )
        return None

    # Bypass: transcript phrase
    transcript_path = payload.get("transcript_path") or ""
    recent_msgs = _read_recent_user_messages(transcript_path)
    if _has_bypass_phrase(recent_msgs):
        if _feedback_events:
            _feedback_events.record(
                cluster="methodology", sub_rule="supabase_ddl",
                decision="pass_through", trigger="transcript_bypass_phrase",
                payload=payload,
            )
        return None

    # Bypass: intent_detection user-driven mode (NEW LAYER)
    if is_user_driven is not None:
        try:
            if is_user_driven(
                transcript_path, file_path=None,
                bypass_phrases=BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                if _feedback_events:
                    _feedback_events.record(
                        cluster="methodology", sub_rule="supabase_ddl",
                        decision="pass_through",
                        trigger="intent_detection_user_driven",
                        payload=payload,
                    )
                return None
        except Exception:
            pass

    op_kind = "apply_migration" if "apply_migration" in tool_lower else "execute_sql"
    reason = (
        f"BLOCKING: DDL detected in Supabase MCP call ({op_kind} via {tool_name}).\n\n"
        f"The `{SKILL_NAME}` skill MUST be invoked before applying DDL. It covers:\n"
        "  - RLS-after-DDL gotchas (rows become invisible without policies)\n"
        "  - Index type selection (B-tree vs GIN vs GiST for JSONB / arrays / FTS)\n"
        "  - apply_migration vs execute_sql trade-off (Phantom Migration anti-pattern:\n"
        "    execute_sql DDL bypasses the migrations table)\n"
        "  - Constraint design, function search_path hardening, lock-window analysis\n"
        "  - Rollback strategies and constraint-rename safety\n\n"
        f"Run `Skill {SKILL_NAME}` (or `Skill {SECONDARY_SKILL}` for security-only checks),\n"
        "then re-issue the migration call.\n\n"
        'To bypass for an emergency or verified-safe migration, include the phrase\n'
        '"skip ddl-nudge" in your next user message and retry.\n\n'
        "Source: wr-2026-04-25 (Sentinel). Past incident (2026-04-17): ALTER TABLE +\n"
        "GIN index on JSONB + COMMENT ON COLUMN applied without skill. Hook upgraded\n"
        "from soft-nudge to hard-block after Sentinel reported the soft-nudge was\n"
        "ineffective. See docs/mandatory-skill-invocations.md."
    )

    if _feedback_events:
        _feedback_events.record(
            cluster="methodology", sub_rule="supabase_ddl",
            decision="hard_deny", trigger=f"ddl_op:{op_kind}",
            payload=payload,
        )
    return {"decision": "deny", "reason": reason}
