"""
methodology-nudge.py - PreToolUse soft nudge for domain skill invocation

Detects domain-relevant work patterns and nudges the AI to invoke the
appropriate domain skill BEFORE producing output. Soft nudge (additionalContext),
not a hard block -- respects Auto Mode while surfacing skills that are being
silently skipped.

Patterns detected:
  1. CRO surfaces (form/landing/signup/paywall/popup/onboarding file paths)
     -> nudge form-cro / page-cro / signup-flow-cro / paywall-upgrade-cro /
        popup-cro / onboarding-cro
  2. Hook modifications (~/.claude/hooks/* paths)
     -> nudge hook-development
  3. n8n workflow design (workflow JSON, n8n-mcp tool calls, n8n.json files)
     -> nudge n8n-workflow-patterns + n8n-mcp-tools-expert
  4. Repeat-edit on same file within session (edited 2+ times)
     -> nudge systematic-debugging
  5. Multi-file Write on deliverable files (3+ Writes)
     -> nudge writing-plans

Reads ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json (written by
skill-invocation-tracker hook) to suppress nudges for skills already invoked
this session.

Per-session state at ~/.claude/.tmp/methodology-nudge-state.json tracks edits
per file and total writes to avoid noise.

Non-blocking. Pure stdlib.

Input: JSON on stdin with tool_name + tool_input
Output: JSON on stdout with hookSpecificOutput.additionalContext (if nudge)
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"
STATE_FILE = TMP_DIR / "methodology-nudge-state.json"

# CRO trigger: filename pattern -> required skill
CRO_PATTERNS = [
    (re.compile(r"(?:^|[/\\_-])form[s]?(?:[/\\_.-]|$)", re.I), "form-cro", "form (lead capture, contact, signup form)"),
    (re.compile(r"(?:^|[/\\_-])(?:landing|landing-page|lp)(?:[/\\_.-]|$)", re.I), "page-cro", "landing page"),
    (re.compile(r"(?:^|[/\\_-])(?:signup|register|registration|signin|login)(?:[/\\_.-]|$)", re.I), "signup-flow-cro", "signup / registration flow"),
    (re.compile(r"(?:^|[/\\_-])(?:paywall|upgrade|pricing|billing)(?:[/\\_.-]|$)", re.I), "paywall-upgrade-cro", "paywall / upgrade / pricing surface"),
    (re.compile(r"(?:^|[/\\_-])(?:popup|modal|overlay|exit-intent)(?:[/\\_.-]|$)", re.I), "popup-cro", "popup / modal / overlay"),
    (re.compile(r"(?:^|[/\\_-])(?:onboarding|first-run|activation|welcome)(?:[/\\_.-]|$)", re.I), "onboarding-cro", "onboarding / first-run / activation"),
    (re.compile(r"(?:^|[/\\_-])(?:checkout|cart)(?:[/\\_.-]|$)", re.I), "form-cro", "checkout / cart"),
]

# Hook path trigger
HOOK_PATH_RE = re.compile(r"[/\\]\.claude[/\\]hooks[/\\]", re.I)

# n8n triggers (file paths and content)
N8N_PATH_RE = re.compile(r"(?:[/\\]n8n[/\\]|[._-]n8n\.json$|[/\\]workflows[/\\]n8n[/\\])", re.I)
N8N_CONTENT_RE = re.compile(r"n8n-nodes-base\.|n8n-nodes-langchain\.|\"nodes\"\s*:\s*\[", re.I)
N8N_SKILLS = ("n8n-workflow-patterns", "n8n-mcp-tools-expert", "n8n-node-configuration")

# Supabase schema-work triggers
# Match any tool whose name contains 'supabase' (case-insensitive) AND is a
# schema-altering operation: apply_migration, execute_sql with CREATE/ALTER/DROP,
# create_branch, merge_branch, reset_branch, deploy_edge_function (function = schema-adjacent).
SUPABASE_TOOL_RE = re.compile(r"supabase", re.I)
SUPABASE_SCHEMA_OP_RE = re.compile(
    r"(?:apply_migration|create_branch|merge_branch|reset_branch|rebase_branch|deploy_edge_function)$",
    re.I,
)
SUPABASE_SCHEMA_SQL_RE = re.compile(
    r"\b(?:CREATE|ALTER|DROP)\s+(?:OR\s+REPLACE\s+)?(?:TABLE|INDEX|VIEW|MATERIALIZED\s+VIEW|TYPE|TRIGGER|FUNCTION|POLICY|SCHEMA|EXTENSION|SEQUENCE|DOMAIN|ROLE)\b",
    re.I,
)
# Strip SQL comments before scanning (-- single-line, /* */ block) to avoid
# false positives from "CREATE TABLE..." mentioned in commentary
SQL_COMMENT_LINE_RE = re.compile(r"--[^\n]*", re.M)
SQL_COMMENT_BLOCK_RE = re.compile(r"/\*.*?\*/", re.S)
SUPABASE_SKILL = "supabase-postgres-best-practices"

# Marketing keywords for content scanning (Bash/Write/Edit content)
MARKETING_KEYWORDS_RE = re.compile(
    r"\b(lead\s*magnet|funnel|qualif(?:y|ication)|positioning|"
    r"go[\s-]to[\s-]market|GTM|ICP|differentiation|pricing\s*tier|"
    r"ad\s*creative|launch\s*strategy)\b",
    re.I,
)
MARKETING_SKILL = "marketing-strategy-pmm"

# Routed-task named-skill detection
# Matches: "invoke supabase skill", "use the skill-creator skill", "call `hook-development` skill"
ROUTED_INVOKE_SKILL_RE = re.compile(
    r"(?:invoke|use|call|consult)\s+(?:the\s+)?[`'\"]?([a-zA-Z][a-zA-Z0-9_:-]{2,})[`'\"]?\s+skill\b",
    re.I,
)
# Matches: "Relevant skill: supabase", "Relevant skills: foo, bar" (first token)
ROUTED_RELEVANT_SKILL_RE = re.compile(
    r"[Rr]elevant\s+skill[s]?:\s*[`'\"]?([a-zA-Z][a-zA-Z0-9_:-]{2,})[`'\"]?",
    re.I,
)
# Words that show up in the capture group but aren't real skill names
ROUTED_SKILL_STOPWORDS = {
    "a", "an", "the", "this", "that", "any", "some", "specific", "appropriate",
    "invoke", "use", "call", "consult", "relevant", "correct", "right", "proper",
    "our", "your", "their", "its", "my", "his", "her",
}


def scan_routed_task_named_skills():
    """Scan {cwd}/.routed-tasks/inbox/*.json for fix_instructions that name a skill.

    Returns list of dicts: [{"task_id": str, "skill": str, "file": str}, ...]
    Deduped per (task_id, skill) pair. Silent on any parse/IO error.
    """
    try:
        inbox = Path(os.getcwd()) / ".routed-tasks" / "inbox"
    except OSError:
        return []
    if not inbox.is_dir():
        return []

    results = []
    seen = set()
    try:
        files = list(inbox.glob("*.json"))
    except OSError:
        return []

    for jf in files:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue

        # Only consider items still actionable
        status = str(data.get("status", "")).lower()
        if status in ("processed", "completed", "done", "resolved"):
            continue

        instructions = str(data.get("fix_instructions", "") or "")
        if not instructions:
            continue

        task_id = str(data.get("task_id") or jf.stem)
        for rx in (ROUTED_INVOKE_SKILL_RE, ROUTED_RELEVANT_SKILL_RE):
            for match in rx.finditer(instructions):
                name = match.group(1).strip().lower()
                if not name or name in ROUTED_SKILL_STOPWORDS:
                    continue
                # Skip tokens that look like prose artefacts (too short, digits only)
                if len(name) < 3 or name.isdigit():
                    continue
                key = (task_id, name)
                if key in seen:
                    continue
                seen.add(key)
                results.append({"task_id": task_id, "skill": name, "file": jf.name})

    return results


def load_skill_log():
    """Return list of skill names invoked today (lowercased)."""
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
    """Check if skill was invoked. Match handles namespaced (plugin:skill) form."""
    target = skill_name.lower()
    for entry in log:
        if entry == target or entry.endswith(":" + target) or entry.startswith(target + ":"):
            return True
    return False


def load_state():
    if not STATE_FILE.exists():
        return {"date": datetime.now().strftime("%Y-%m-%d"), "edits": {}, "writes": [], "nudged": []}
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        # Reset if a new day
        if s.get("date") != datetime.now().strftime("%Y-%m-%d"):
            return {"date": datetime.now().strftime("%Y-%m-%d"), "edits": {}, "writes": [], "nudged": []}
        return s
    except (json.JSONDecodeError, OSError):
        return {"date": datetime.now().strftime("%Y-%m-%d"), "edits": {}, "writes": [], "nudged": []}


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


def emit(text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}}))


def is_excluded_path(path):
    p = path.replace("\\", "/").lower()
    return any(seg in p for seg in (
        "/.tmp/", "/node_modules/", "/.git/", "/__pycache__/",
        "memory.md", "claude.md", "/processed/", "/inbox/", "/outbox/",
    ))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    state = load_state()
    log = load_skill_log()
    nudges = []

    file_path = str(tool_input.get("file_path", ""))
    content = str(tool_input.get("content", "") or tool_input.get("new_string", "") or "")

    # ---- Triggers on Write/Edit -------------------------------------------
    if tool_name in ("Write", "Edit") and file_path and not is_excluded_path(file_path):
        # Track edits per file for repeat-edit detection
        if tool_name == "Edit":
            edits = state.setdefault("edits", {})
            edits[file_path] = edits.get(file_path, 0) + 1
            if edits[file_path] >= 2 and not skill_invoked("systematic-debugging", log):
                key = f"systematic-debugging:{file_path}"
                if not already_nudged(state, key):
                    nudges.append(
                        f"REPEAT EDIT detected on {os.path.basename(file_path)} "
                        f"({edits[file_path]} edits this session). Invoke "
                        "`systematic-debugging` skill before continuing -- two "
                        "edits to the same file in one task usually means a "
                        "missing failure-mode in the design. Run the hypothesis "
                        "loop instead of patching iteratively."
                    )
                    mark_nudged(state, key)

        # Track writes for multi-file plan detection
        if tool_name == "Write":
            writes = state.setdefault("writes", [])
            if file_path not in writes:
                writes.append(file_path)
            if len(writes) == 3 and not skill_invoked("writing-plans", log) and not skill_invoked("superpowers:writing-plans", log):
                key = "writing-plans:multi-file"
                if not already_nudged(state, key):
                    nudges.append(
                        "MULTI-FILE BUILD detected (3+ Write operations this "
                        "session). Consider invoking `writing-plans` to capture "
                        "the build sequence as an audit trail. Skipped if Auto "
                        "Mode + simple builds; required for cross-file architecture."
                    )
                    mark_nudged(state, key)

        # CRO surface detection
        for pattern, skill, surface in CRO_PATTERNS:
            if pattern.search(file_path) and not skill_invoked(skill, log):
                ext_ok = any(file_path.lower().endswith(ext) for ext in (
                    ".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".md", ".mdx"
                ))
                if not ext_ok:
                    continue
                key = f"{skill}:{file_path}"
                if not already_nudged(state, key):
                    nudges.append(
                        f"CRO SURFACE DETECTED: {os.path.basename(file_path)} looks like a "
                        f"{surface}. Invoke `{skill}` skill BEFORE writing the markup. "
                        "CRO skills load field-ordering, conversion copy, error states, and "
                        "mobile patterns specific to this surface. Generic builds convert lower. "
                        "See docs/mandatory-skill-invocations.md."
                    )
                    mark_nudged(state, key)

        # Hook path detection
        if HOOK_PATH_RE.search(file_path) and not skill_invoked("hook-development", log):
            key = f"hook-development:{file_path}"
            if not already_nudged(state, key):
                nudges.append(
                    f"HOOK MODIFICATION DETECTED: {os.path.basename(file_path)} is under "
                    "~/.claude/hooks/. Invoke `hook-development` skill BEFORE editing. "
                    "Without it, hook fixes typically need 2-3 false-positive iterations."
                )
                mark_nudged(state, key)

        # n8n workflow detection
        if N8N_PATH_RE.search(file_path) or N8N_CONTENT_RE.search(content[:2000]):
            missing_n8n = [s for s in N8N_SKILLS if not skill_invoked(s, log)]
            if missing_n8n:
                key = f"n8n:{file_path or 'content'}"
                if not already_nudged(state, key):
                    skills_list = ", ".join(f"`{s}`" for s in missing_n8n)
                    nudges.append(
                        "n8n WORKFLOW WORK DETECTED. Invoke "
                        f"{skills_list} BEFORE designing or editing nodes. "
                        "Without these, sessions default to httpRequest for services "
                        "with native nodes (GitHub, HubSpot, Supabase, Brevo). "
                        "n8n-httpRequest-guard.py blocks unjustified httpRequest at write time."
                    )
                    mark_nudged(state, key)

        # Marketing content keyword detection (in file content)
        if content and MARKETING_KEYWORDS_RE.search(content[:2000]) and not skill_invoked(MARKETING_SKILL, log):
            key = f"marketing:{file_path}"
            if not already_nudged(state, key):
                nudges.append(
                    "MARKETING / FUNNEL CONTENT detected (keywords like lead magnet, "
                    "funnel, positioning, GTM, ICP). Invoke `marketing-strategy-pmm` "
                    "to apply April Dunford-style positioning + qualification frame "
                    "instead of freestyling. See docs/mandatory-skill-invocations.md."
                )
                mark_nudged(state, key)

    # ---- Triggers on routed-task fix_instructions naming a skill ----------
    # Fires when any tool is invoked while a pending routed task in this
    # workspace's .routed-tasks/inbox/ has a fix_instructions field that
    # names a skill ("invoke X skill", "Relevant skill: X") AND that skill
    # has not yet been invoked this session. Nudges once per (task_id, skill)
    # pair per session. Soft nudge only.
    #
    # Safety: validates the extracted skill name exists under ~/.claude/skills/
    # or any plugin skill dir before nudging, to suppress regex false positives.
    try:
        routed_named = scan_routed_task_named_skills()
    except Exception:
        routed_named = []

    if routed_named:
        skills_root = Path.home() / ".claude" / "skills"
        plugins_root = Path.home() / ".claude" / "plugins"
        for entry in routed_named:
            name = entry["skill"]
            task_id = entry["task_id"]

            # Skip if already invoked (handles namespaced forms like plugin:name)
            if skill_invoked(name, log):
                continue

            # Plausibility gate: skill directory must exist somewhere, OR the
            # name must match an invoked skill's namespaced form. Suppresses
            # regex over-matching on prose.
            name_installed = False
            if (skills_root / name).is_dir():
                name_installed = True
            elif plugins_root.is_dir():
                # Check any plugin skill dir ending with this name
                try:
                    for plugin_skill in plugins_root.rglob(f"skills/{name}"):
                        if plugin_skill.is_dir():
                            name_installed = True
                            break
                except OSError:
                    pass
            if not name_installed:
                continue

            key = f"routed-task-skill:{task_id}:{name}"
            if already_nudged(state, key):
                continue
            nudges.append(
                f"ROUTED-TASK NAMED SKILL: inbox task `{task_id}` names "
                f"`{name}` skill in its fix_instructions, but it has not been "
                "invoked this session. Per universal-protocols.md Pre-Task "
                "Checklist, invoke the named skill BEFORE starting "
                "implementation. Task authors name skills precisely because "
                "the reasoning, patterns, and edge-cases encoded there are "
                "load-bearing for the work -- general knowledge bypasses "
                "them."
            )
            mark_nudged(state, key)

    # ---- Triggers on Supabase MCP schema-work calls -----------------------
    if SUPABASE_TOOL_RE.search(tool_name) and not skill_invoked(SUPABASE_SKILL, log):
        is_schema_op = bool(SUPABASE_SCHEMA_OP_RE.search(tool_name))
        is_schema_sql = False
        # execute_sql: scan the SQL for CREATE/ALTER/DROP (after stripping comments)
        if "execute_sql" in tool_name.lower():
            sql = str(tool_input.get("query") or tool_input.get("sql") or "")
            if sql:
                clean = SQL_COMMENT_LINE_RE.sub("", sql)
                clean = SQL_COMMENT_BLOCK_RE.sub("", clean)
                is_schema_sql = bool(SUPABASE_SCHEMA_SQL_RE.search(clean))
        if is_schema_op or is_schema_sql:
            key = f"supabase:{tool_name}"
            if not already_nudged(state, key):
                op_kind = "apply_migration / branch op" if is_schema_op else "execute_sql with CREATE/ALTER/DROP"
                nudges.append(
                    f"SUPABASE SCHEMA WORK detected ({op_kind} via {tool_name}). "
                    f"Invoke `{SUPABASE_SKILL}` BEFORE proceeding -- the canonical source "
                    "for Supabase schema decisions (constraints, RLS, indexes, triggers, naming, "
                    "tenant_id discipline). See docs/mandatory-skill-invocations.md."
                )
                mark_nudged(state, key)

    # ---- Triggers on n8n MCP calls ----------------------------------------
    if tool_name.startswith("mcp__n8n") or tool_name.startswith("mcp__claude_ai_n8n"):
        if "create" in tool_name.lower() or "update" in tool_name.lower() or "deploy" in tool_name.lower():
            missing_n8n = [s for s in N8N_SKILLS if not skill_invoked(s, log)]
            if missing_n8n:
                key = f"n8n:mcp:{tool_name}"
                if not already_nudged(state, key):
                    skills_list = ", ".join(f"`{s}`" for s in missing_n8n)
                    nudges.append(
                        f"n8n MCP CREATE/UPDATE on {tool_name}. Invoke "
                        f"{skills_list} BEFORE this call. "
                        "Skills load native-node patterns, validation strategy, and "
                        "common gotchas. Without them, you build and re-build."
                    )
                    mark_nudged(state, key)

    # ---- Bash command pattern triggers ------------------------------------
    if tool_name == "Bash":
        cmd = str(tool_input.get("command", ""))
        if MARKETING_KEYWORDS_RE.search(cmd) and not skill_invoked(MARKETING_SKILL, log):
            key = f"marketing:bash"
            if not already_nudged(state, key):
                nudges.append(
                    "MARKETING / FUNNEL command detected. Invoke "
                    "`marketing-strategy-pmm` first if you are about to make "
                    "positioning, qualification, or lead-source decisions."
                )
                mark_nudged(state, key)

    save_state(state)

    if nudges:
        emit("\n\n".join(nudges))

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
