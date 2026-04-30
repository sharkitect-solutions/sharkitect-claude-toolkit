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
  6. Investigation pattern: 4+ status/health/state-query Bash or MCP calls
     in the same session WITHOUT systematic-debugging invocation
     -> nudge superpowers:systematic-debugging
     Source: wr-2026-04-23 (HQ) systematic-debugging-skipped-on-ceo-brief-investigation

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

# Investigation-pattern detection (wr-2026-04-23 HQ)
# When a session strings together 4+ status / health / state-query calls
# (Bash or MCP) WITHOUT having invoked systematic-debugging, that's the
# signature of ad-hoc investigation skipping the methodology skill.
# Threshold = 4 (not 3) to give a small grace window for routine monitoring
# (one CronCreate fire + one user-initiated check + one follow-up read is
# normal; 4+ in sequence is investigation).
SYSTEMATIC_DEBUGGING_SKILL = "systematic-debugging"
SUPERPOWERS_SYSTEMATIC_DEBUGGING_SKILL = "superpowers:systematic-debugging"
INVESTIGATION_THRESHOLD = 4

# Hypothesis-enumeration content detection (wr-hq-2026-04-28-003).
# When the assistant writes or edits a file whose content enumerates
# hypotheses ("Hypothesis 1:", "Possibility A:", "Hypotheses:" + numbered
# list), that's the signature of ad-hoc bug investigation skipping the
# systematic-debugging methodology. Fires BEFORE the first state-query
# accumulation that the existing INVESTIGATION_THRESHOLD trigger waits for.
# Source: wr-hq-2026-04-28-003 (HQ) -- iOS Save Contact stale-logo
# investigation generated hypotheses without invoking systematic-debugging.
#
# Pattern requires the literal word "Hypothesis"/"Possibility"/"Hypotheses"/
# "Possibilities" followed by an enumeration token (digit, letter, colon)
# to avoid false-positives on casual prose like "my hypothesis is...".
HYPOTHESIS_ENUM_RE = re.compile(
    r"\b(?:hypothes(?:is|es)|possibilit(?:y|ies)|root[\s-]cause[\s-]candidate[s]?)"
    r"\s*[#:]?\s*[1A-Za](?:[\.\):]|\s)",
    re.I,
)

# Verification-tool testing-strategy nudge (wr-sentinel-2026-04-27-020).
# When a new tools/, scripts/, or hooks/ file with a verification-pattern
# name is CREATED via Write AND testing-strategy hasn't been invoked,
# advisory nudge fires once per file. Source: Sentinel built
# tools/wr-id-consistency-check.py (297 lines) without invoking
# testing-strategy; tool fired correctly on real data once but lacked
# formal acceptance suite that would catch future regressions.
# Pattern excludes test_ prefix files (those ARE the tests; circular).
# Hosted in methodology-nudge.py instead of multistep-plan-nudge.py
# (the WR's primary recommendation) because multistep-plan-nudge.py is
# registered only on TodoWrite -- adding Edit|Write matcher requires a
# settings.json edit that's denied. methodology-nudge.py already runs on
# Edit|Write with the same skill-log + state-debouncing infrastructure.
VERIFICATION_TOOL_PATH_RE = re.compile(
    # Word STEMS, not full words. "validate" is NOT a substring of "validator"
    # (validator has 'ator' suffix, validate has 'ate'). Stems catch all
    # inflections: validat[e/or/ion/es/ed/ing], verif[y/ier/ies/ied/ication],
    # audit[/or/s/ed/ing], consistenc[y/ies], inspect[/or/ion/s].
    # 'checker' / 'tester' kept as full words since their stems ('check' /
    # 'test') over-match (test_ prefix matches test files which ARE the tests,
    # not tools needing tests; checker is more specific than 'check').
    r"(?:^|[/\\])(?:tools|scripts|hooks)[/\\]"
    r"[^/\\]*"
    r"(?:validat|verif|audit|consistenc|inspect|checker|tester)"
    r"[^/\\]*"
    r"\.(?:py|sh|js|ts)$",
    re.I,
)
TESTING_STRATEGY_SKILLS = (
    "testing-strategy",
    "test-driven-development",
    "superpowers:test-driven-development",
    "testing-patterns",
    "senior-qa",
)

# TDD pattern detection (wr-skillhub-2026-04-29-001).
# When the assistant builds 2+ distinct deliverable files AND touches at least
# one test file in the same session WITHOUT prior superpowers:test-driven-
# development invocation, nudge before the second deliverable edit lands.
# The signal: multi-file build + tests in the mix = scope where TDD applies,
# but the methodology skill wasn't invoked. Catches the failure mode "I added
# tests after the fact, which is not the same as following TDD."
#
# Detection logic (PreToolUse on Write/Edit):
#   - Classify file_path as test, deliverable, or other (config/docs/data)
#   - Maintain dedup'd lists in state: tdd_deliverables_touched + tdd_tests_touched
#   - When BOTH thresholds cross (deliv>=2 AND tests>=1) AND TDD not invoked,
#     emit nudge and mark already_nudged so it fires once per session.
#
# False-positive guards:
#   - Test patterns checked FIRST (so test_*.py is never counted as deliverable)
#   - Excluded paths (is_excluded_path) bypass the entire block (.tmp, .git,
#     /processed/, /inbox/, /outbox/ etc. -- already-applied at handler entry)
#   - Deliverable extensions limited to code files (.py/.js/.ts/.go/etc.);
#     .md/.json/.yaml/.txt do not count, so doc/config edits don't trigger.
TEST_FILE_RE = re.compile(
    r"(?:^|[/\\])"
    r"(?:test_[^/\\]+\.(?:py|js|ts)$"
    r"|[^/\\]+_test\.(?:py|js|ts|go)$"
    r"|[^/\\]+\.test\.(?:js|ts|jsx|tsx)$"
    r"|[^/\\]+\.spec\.(?:js|ts|jsx|tsx)$"
    r"|tests?[/\\][^/\\]+\.(?:py|js|ts)$"
    r"|__tests__[/\\][^/\\]+)",
    re.I,
)
DELIVERABLE_EXT_RE = re.compile(
    r"\.(?:py|js|ts|jsx|tsx|go|rs|java|rb|ex|exs|kt|swift|c|cpp|h|hpp|sh|bash)$",
    re.I,
)
TDD_SKILLS = (
    "test-driven-development",
    "superpowers:test-driven-development",
)
TDD_DELIVERABLE_THRESHOLD = 2

# MCP tool-name patterns that indicate "I'm checking state"
INVESTIGATION_MCP_TOOL_RES = [
    re.compile(r"n8n.*get_execution|n8n.*list_executions|n8n.*get_workflow|n8n.*health_check", re.I),
    re.compile(r"supabase.*execute_sql|supabase.*get_logs|supabase.*get_advisors|supabase.*list_(?:projects|tables|migrations)", re.I),
    re.compile(r"github.*get_(?:commit|workflow|run)|github.*list_(?:commits|runs|jobs)", re.I),
    re.compile(r"sentry.*(?:list_issues|get_issue|search_events|seer)", re.I),
]

# Bash command patterns that indicate state querying
INVESTIGATION_BASH_RES = [
    # Generic process / port / log probes
    re.compile(r"\b(?:ps\s+aux|ps\s+-ef|tasklist|netstat|ss\s+-l|lsof)\b", re.I),
    re.compile(r"\bcurl[^\n|]*?(?:health|status|/api/|/v\d/)", re.I),
    # Cron / Task Scheduler / Schtasks state queries
    re.compile(r"\bschtasks\s+/query\b|\bcrontab\s+-l\b|\bcrontab\s+-e\b", re.I),
    # Direct Supabase / Postgres SELECTs via psql / python
    re.compile(r"psql.*-c.*(?:SELECT|select)\s", re.I),
    # python -c with select / status
    re.compile(r"python\s+-c\s+[\"'][^\"']*?(?:SELECT|select|status|health|active)\b", re.I),
    # Heartbeat / status JSON lookups
    re.compile(r"\b(?:cat|head|tail)\s+[^\n]*\.tmp[^\n]*?(?:heartbeat|status|state|health)", re.I),
    # n8n API / Supabase API direct curls
    re.compile(r"\bcurl[^\n|]*?(?:n8n|supabase|sentry)", re.I),
]


# Path filter: documentation / internal notes / plans / operational artifacts.
# When a file path matches this, marketing keyword content matches are SKIPPED
# because the file is documentation ABOUT marketing, not a marketing deliverable.
# Prevents false positives on internal planning docs that reference positioning,
# funnel, GTM, etc. as concepts rather than producing positioning output.
DOCUMENTATION_PATH_RE = re.compile(
    r"(?:"
    r"[/\\]docs?[/\\]"
    r"|[/\\]knowledge-base[/\\]"
    r"|[/\\]memory[/\\]"
    r"|[/\\]workflows?[/\\]"
    r"|[/\\]\.routed-tasks[/\\]"
    r"|[/\\]\.work-requests[/\\]"
    r"|[/\\]\.lifecycle-reviews[/\\]"
    r"|[/\\]projects[/\\]"
    r"|[/\\]plans?[/\\]"
    r"|[/\\]notes?[/\\]"
    r"|[/\\]rules[/\\]"
    r"|[/\\]lessons[/\\]"
    r"|[/\\]README\.md$"
    r"|[/\\]MEMORY\.md$"
    r"|[/\\]CLAUDE\.md$"
    r"|[/\\]plan\.md$"
    r"|[/\\]roadmap\.md$"
    r"|[/\\]lessons-learned\.md$"
    r")",
    re.I,
)

# Path signal: actual marketing deliverables where marketing-strategy-pmm DOES apply.
# Used to require the nudge even if content keywords are weak.
MARKETING_DELIVERABLE_PATH_RE = re.compile(
    r"(?:"
    r"[/\\]ads?[/\\]"
    r"|[/\\]landing(?:-page)?[/\\]"
    r"|[/\\]sales-?scripts?[/\\]"
    r"|[/\\]pitch(?:-deck)?[/\\]"
    r"|[/\\]email-?campaigns?[/\\]"
    r"|[/\\]positioning[/\\]"
    r"|[/\\]gtm[/\\]"
    r"|[/\\]one-pagers?[/\\]"
    r"|[/\\]sales-collateral[/\\]"
    r")",
    re.I,
)

# Plan file trigger: single-file plan / roadmap writes should nudge writing-plans.
# Complements the existing "3+ Writes" multi-file trigger. Fires on these patterns:
#   plan.md / roadmap.md at any depth
#   plans/<something>.md
#   roadmap/<something>.md
#   **/projects/<name>/plan.md
PLAN_FILE_RE = re.compile(
    r"(?:"
    r"[/\\](?:plan|roadmap)\.md$"
    r"|[/\\]plans?[/\\][^/\\]+\.md$"
    r"|[/\\]roadmaps?[/\\][^/\\]+\.md$"
    r"|[/\\]projects[/\\][^/\\]+[/\\]plan\.md$"
    r")",
    re.I,
)

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


def _is_iterative_patching(new_old_string, prior_fingerprints):
    """Return True if this edit is re-patching text from a prior edit.

    Heuristic (per wr-skillhub-2026-04-27-004): an edit is "iterative
    patching" if its old_string contains a substantial substring of any
    PRIOR edit's new_string. That's the signature of "I just wrote this,
    now I'm editing it again" -- the failure mode the systematic-debugging
    skill is supposed to interrupt.

    Pure-additive edits (new function appended), signature changes that
    touch a caller, and unrelated edits to different regions of the same
    file all produce non-overlapping old_string/new_string pairs and
    correctly do NOT trigger the nudge.

    Threshold: 30 characters of overlap. Below that, false-positive risk
    rises (common boilerplate like 'def foo(' or '    return ' would match
    spuriously). Above 30 chars, the match is meaningful: substantial,
    distinctive text shared with a prior new_string.
    """
    if not new_old_string or len(new_old_string) < 30:
        return False
    # Scan every contiguous 30-char window of the current old_string against
    # every prior new_string. If any window appears in any prior new_string,
    # we're touching text we just wrote.
    SCAN_WINDOW = 30
    for fp in prior_fingerprints:
        prior_new = (fp.get("new") if isinstance(fp, dict) else "") or ""
        if len(prior_new) < SCAN_WINDOW:
            continue
        # Sliding window: efficient for short strings, bounded by truncation
        # at 200 chars per fingerprint.
        for i in range(0, len(new_old_string) - SCAN_WINDOW + 1):
            window = new_old_string[i:i + SCAN_WINDOW]
            if window in prior_new:
                return True
    return False


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
        # Track edits per file for repeat-edit detection.
        # Fingerprint-based overlap heuristic distinguishes iterative patching
        # (same lines, re-edited) from paired refinements (signature + caller,
        # unrelated edits to same file). Only iterative patching warrants the
        # systematic-debugging nudge. Source: wr-skillhub-2026-04-27-004.
        if tool_name == "Edit":
            old_string = str(tool_input.get("old_string", "") or "")
            new_string = str(tool_input.get("new_string", "") or "")

            # Backward-compat: edits[file_path] used to be an int. Migrate
            # transparently so prior-session state doesn't crash the hook.
            edits = state.setdefault("edits", {})
            entry = edits.get(file_path)
            if isinstance(entry, int):
                entry = {"count": entry, "fingerprints": []}
            elif not isinstance(entry, dict):
                entry = {"count": 0, "fingerprints": []}
            entry["count"] = entry.get("count", 0) + 1
            fingerprints = entry.setdefault("fingerprints", [])

            # Detect overlap with prior edits BEFORE recording the new fingerprint
            iterative = _is_iterative_patching(old_string, fingerprints)

            # Record this edit's fingerprint (truncate to keep state small)
            if old_string or new_string:
                fingerprints.append({
                    "old": old_string[:200],
                    "new": new_string[:200],
                })
                # Cap history at 6 entries to bound state size
                if len(fingerprints) > 6:
                    del fingerprints[: len(fingerprints) - 6]
            edits[file_path] = entry

            # Nudge ONLY when (a) 2+ edits AND (b) iterative pattern detected
            # AND (c) systematic-debugging hasn't been invoked yet.
            # Bare 2-edit threshold caused false positives on additive changes
            # (new function appended, signature + caller, separate concerns).
            if (entry["count"] >= 2
                    and iterative
                    and not skill_invoked("systematic-debugging", log)
                    and not skill_invoked("superpowers:systematic-debugging", log)):
                key = f"systematic-debugging:{file_path}"
                if not already_nudged(state, key):
                    nudges.append(
                        f"REPEAT EDIT detected on {os.path.basename(file_path)} "
                        f"({entry['count']} edits this session, RE-PATCHING prior "
                        "change). Invoke `systematic-debugging` skill -- you're "
                        "editing text you just wrote, which usually means the "
                        "first attempt missed a failure mode. Run the hypothesis "
                        "loop instead of patching iteratively."
                    )
                    mark_nudged(state, key)

        # Verification-tool creation -> testing-strategy nudge.
        # Fires ONLY on Write (file creation). Edits to existing tools
        # don't re-trigger. Source: wr-sentinel-2026-04-27-020.
        if (tool_name == "Write"
                and VERIFICATION_TOOL_PATH_RE.search(file_path)
                and not any(skill_invoked(s, log) for s in TESTING_STRATEGY_SKILLS)):
            key = f"testing-strategy:verification-tool:{file_path}"
            if not already_nudged(state, key):
                nudges.append(
                    f"VERIFICATION TOOL CREATED: {os.path.basename(file_path)} "
                    "is a new verification / audit / check tool that other "
                    "systems will trust. Invoke `testing-strategy` (or "
                    "`superpowers:test-driven-development` / `testing-patterns` "
                    "/ `senior-qa`) and write fixture-based tests BEFORE other "
                    "workspaces start consuming its output.\n\n"
                    "Without acceptance tests, future regressions (schema "
                    "field rename, status vocabulary shift, edge-case input) "
                    "won't be caught until a real downstream report fails. "
                    "The cost of writing the test suite now is hours; the "
                    "cost of debugging a silent verification regression later "
                    "is days.\n\n"
                    "Source: wr-sentinel-2026-04-27-020. Precedent: "
                    "~/.claude/tests/test_wr_id_schema.py (12 cases) shipped "
                    "alongside the wr-id-schema-v2 enforcement infrastructure."
                )
                mark_nudged(state, key)

        # TDD pattern detection (wr-skillhub-2026-04-29-001).
        # Multi-file deliverable + test-file edits in same session WITHOUT
        # superpowers:test-driven-development = TDD applies but methodology
        # was skipped. Fire once per session on the threshold-crossing edit.
        # Test classification runs FIRST so test_*.py is never miscounted as
        # a deliverable.
        is_test_file = bool(TEST_FILE_RE.search(file_path))
        is_deliverable = (
            (not is_test_file)
            and bool(DELIVERABLE_EXT_RE.search(file_path))
        )
        if is_test_file:
            tdd_tests = state.setdefault("tdd_tests_touched", [])
            if file_path not in tdd_tests:
                tdd_tests.append(file_path)
        if is_deliverable:
            tdd_deliv = state.setdefault("tdd_deliverables_touched", [])
            if file_path not in tdd_deliv:
                tdd_deliv.append(file_path)

        deliv_count = len(state.get("tdd_deliverables_touched", []))
        test_count = len(state.get("tdd_tests_touched", []))
        if (deliv_count >= TDD_DELIVERABLE_THRESHOLD
                and test_count >= 1
                and not any(skill_invoked(s, log) for s in TDD_SKILLS)):
            key = "tdd:multi-file-with-tests"
            if not already_nudged(state, key):
                nudges.append(
                    f"TDD PATTERN detected: {deliv_count} deliverable file(s) "
                    f"+ {test_count} test file(s) touched this session "
                    "WITHOUT `superpowers:test-driven-development` invocation. "
                    "Multi-file build + tests in the mix is the scope where "
                    "TDD applies.\n\n"
                    "Run `Skill superpowers:test-driven-development` BEFORE "
                    "the next deliverable edit. Adding tests after the fact "
                    "is NOT the same as following TDD methodology -- the "
                    "skill enforces red-green-refactor cadence (write the "
                    "failing test FIRST, then minimum code to pass, then "
                    "refactor) which catches missing edge cases that "
                    "'tests written alongside' typically miss.\n\n"
                    "If TDD doesn't apply (refactor with no behavior change, "
                    "config edits, doc-only work, hot-fix to running prod), "
                    "invoke the skill anyway and let it self-exempt -- silent "
                    "skip on methodology nudges is a trust failure even when "
                    "the rationalization is correct. Source: "
                    "wr-skillhub-2026-04-29-001."
                )
                mark_nudged(state, key)

        # Hypothesis-enumeration content detection (wr-hq-2026-04-28-003).
        # Fires when the content being written/edited enumerates hypotheses
        # AND systematic-debugging hasn't been invoked yet. Earlier signal
        # than the state-query-based INVESTIGATION_THRESHOLD trigger.
        if (content
                and HYPOTHESIS_ENUM_RE.search(content[:3000])
                and not skill_invoked(SYSTEMATIC_DEBUGGING_SKILL, log)
                and not skill_invoked(SUPERPOWERS_SYSTEMATIC_DEBUGGING_SKILL, log)):
            key = "systematic-debugging:hypothesis-enum"
            if not already_nudged(state, key):
                nudges.append(
                    "HYPOTHESIS ENUMERATION detected in content being written "
                    f"({os.path.basename(file_path)}). The assistant is "
                    "generating hypotheses ad-hoc without invoking "
                    "`superpowers:systematic-debugging` -- the methodology "
                    "skill explicitly designed for hypothesis-test cycles.\n\n"
                    "Run `Skill superpowers:systematic-debugging` BEFORE "
                    "committing the hypothesis list. The skill enforces: "
                    "gather evidence first, enumerate hypotheses with "
                    "explicit falsification tests, test cheapest first, "
                    "document what was ruled out. Without it, investigations "
                    "anchor on the first plausible-sounding cause and miss "
                    "systemic issues.\n\n"
                    "Universal Protocols Investigation Protocol "
                    "(NON-NEGOTIABLE): 'When investigating bugs, unexpected "
                    "behavior, system failures, recurring issues, or any "
                    "situation requiring a hypothesis-test cycle -- INVOKE "
                    "superpowers:systematic-debugging BEFORE generating "
                    "hypotheses.' Source: wr-hq-2026-04-28-003 (iOS Save "
                    "Contact stale-logo investigation)."
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

        # Marketing content keyword detection (in file content).
        # Path-aware precision: skip if path is documentation/plan/notes (file
        # is ABOUT marketing concepts, not a marketing deliverable). Elevate
        # to REQUIRED language if path is a known marketing deliverable.
        is_doc_path = bool(DOCUMENTATION_PATH_RE.search(file_path))
        is_marketing_deliverable = bool(MARKETING_DELIVERABLE_PATH_RE.search(file_path))
        keyword_hit = content and MARKETING_KEYWORDS_RE.search(content[:2000])

        if keyword_hit and not is_doc_path and not skill_invoked(MARKETING_SKILL, log):
            key = f"marketing:{file_path}"
            if not already_nudged(state, key):
                tier = "REQUIRED" if is_marketing_deliverable else "RECOMMENDED"
                extra = (
                    " Do NOT rationalize applicability -- invoke the skill and let it "
                    "self-exempt if the content is out of scope. Per user memory "
                    "feedback_never_skip_protocols.md, silent skip on nudges is a "
                    "trust failure even when the rationalization is correct."
                    if tier == "REQUIRED"
                    else ""
                )
                nudges.append(
                    f"{tier}: MARKETING / FUNNEL CONTENT detected (keywords like lead "
                    "magnet, funnel, positioning, GTM, ICP). Invoke "
                    "`marketing-strategy-pmm` to apply April Dunford-style positioning "
                    "+ qualification frame instead of freestyling. See "
                    f"docs/mandatory-skill-invocations.md.{extra}"
                )
                mark_nudged(state, key)

        # Plan file trigger: single-file writes to plan.md / roadmap.md / plans/*.md
        # complement the existing 3+ writes -> writing-plans trigger. Catches the
        # case where a multi-thread plan is drafted in one single large file.
        if PLAN_FILE_RE.search(file_path) \
                and not skill_invoked("writing-plans", log) \
                and not skill_invoked("superpowers:writing-plans", log):
            key = f"writing-plans:plan-file:{file_path}"
            if not already_nudged(state, key):
                nudges.append(
                    "RECOMMENDED: PLAN FILE WRITE detected "
                    f"({os.path.basename(file_path)}). Invoke `writing-plans` BEFORE "
                    "drafting so the plan hits the quality checklist (risk register, "
                    "rollback, measurable completion signals per thread, review "
                    "cadence). 'I know what a plan looks like' is the rationalization "
                    "superpowers explicitly flags as a red flag. Invoke the skill and "
                    "let it self-exempt for trivial or status-update-only plan edits."
                )
                mark_nudged(state, key)

        # Executing-plans trigger: when a plan file is being edited AND the plan
        # explicitly names executing-plans as a required sub-skill, nudge
        # `superpowers:executing-plans` BEFORE iterating on the plan steps.
        # Source: wr-skillhub-2026-04-27-003. Pattern observed 2026-04-27 PM:
        # the wr-id-schema plan header line 5 said "REQUIRED SUB-SKILL: Use
        # superpowers:executing-plans" and the AI followed task-by-task with
        # TodoWrite + manual sequencing instead of formally invoking the skill.
        # The plan went smoothly only because the discipline was internalized.
        if PLAN_FILE_RE.search(file_path) \
                and not skill_invoked("executing-plans", log) \
                and not skill_invoked("superpowers:executing-plans", log):
            try:
                plan_path = Path(file_path)
                if plan_path.exists():
                    head = plan_path.read_text(encoding="utf-8", errors="replace").splitlines()[:25]
                    head_text = "\n".join(head)
                    if re.search(r"REQUIRED\s+SUB-SKILL", head_text, re.IGNORECASE) \
                            and re.search(r"executing-plans", head_text, re.IGNORECASE):
                        key = f"executing-plans:{file_path}"
                        if not already_nudged(state, key):
                            nudges.append(
                                f"PLAN REQUIRES executing-plans: {os.path.basename(file_path)} "
                                "header explicitly names superpowers:executing-plans as a "
                                "REQUIRED SUB-SKILL. Invoke it BEFORE iterating on the plan "
                                "tasks. The named-skill enforcement protocol exists to ensure "
                                "verification-before-completion at each step rather than "
                                "ad-hoc TodoWrite + manual sequencing."
                            )
                            mark_nudged(state, key)
            except (OSError, UnicodeDecodeError):
                pass

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

        # Batch-WR-processing trigger (wr-2026-04-22-017).
        #
        # Processing 3+ work requests in one session is a batch operation
        # that benefits from a structured plan. Without one, the session
        # drifts between WRs and loses track of cross-WR dependencies
        # (e.g., "WR-A modifies the script that WR-B also touches").
        #
        # Detection: count Bash invocations of close-inbox-item.py that
        # target a path under /.work-requests/inbox/ (i.e., closing a WR,
        # not a routed task or lifecycle review). We don't block; once
        # 3 closures have happened in a session without writing-plans
        # having been invoked, emit a single advisory nudge. Debounced
        # via the existing already_nudged state machine.
        #
        # 3 is the threshold per the WR: 1 = direct work, 2 = possibly
        # related, 3+ = batch deserving structure.
        if "close-inbox-item.py" in cmd and "/.work-requests/inbox/" in cmd.replace("\\", "/").lower():
            wr_count = state.setdefault("wr_closures", 0)
            state["wr_closures"] = wr_count + 1
            if (state["wr_closures"] >= 3
                    and not skill_invoked("writing-plans", log)
                    and not skill_invoked("superpowers:writing-plans", log)):
                key = "writing-plans:wr-batch"
                if not already_nudged(state, key):
                    nudges.append(
                        f"BATCH WR PROCESSING detected "
                        f"({state['wr_closures']}+ work requests closed this "
                        "session). Consider invoking `writing-plans` (or "
                        "`superpowers:writing-plans`) to capture the batch as "
                        "a structured plan -- tracks cross-WR dependencies, "
                        "risks, and completion signals. Single WR = direct "
                        "work; 2 WRs = possibly related; 3+ = batch that "
                        "benefits from structure. TodoWrite is NOT a "
                        "substitute for a plan on 3+ interrelated WRs. "
                        "Source: wr-2026-04-22-017."
                    )
                    mark_nudged(state, key)

    # ---- Investigation-pattern trigger (Bash + MCP, wr-2026-04-23 HQ) ----
    # Count investigative state-query calls. If 4+ accumulate in this session
    # WITHOUT systematic-debugging being invoked, nudge once.
    is_investigative = False
    if tool_name == "Bash":
        cmd_text = str(tool_input.get("command", ""))
        for rx in INVESTIGATION_BASH_RES:
            if rx.search(cmd_text):
                is_investigative = True
                break
    elif tool_name.startswith("mcp__"):
        for rx in INVESTIGATION_MCP_TOOL_RES:
            if rx.search(tool_name):
                is_investigative = True
                break

    if is_investigative:
        # If systematic-debugging was already invoked, reset the counter
        # (the methodology is in play; no further nudge needed)
        if (skill_invoked(SYSTEMATIC_DEBUGGING_SKILL, log)
                or skill_invoked(SUPERPOWERS_SYSTEMATIC_DEBUGGING_SKILL, log)):
            state["investigation_count"] = 0
        else:
            inv_count = state.get("investigation_count", 0) + 1
            state["investigation_count"] = inv_count
            if inv_count >= INVESTIGATION_THRESHOLD:
                key = "systematic-debugging:investigation"
                if not already_nudged(state, key):
                    nudges.append(
                        f"INVESTIGATION PATTERN detected ({inv_count}+ status / "
                        "health / state-query calls this session without "
                        "`superpowers:systematic-debugging`). Sequential "
                        "read-investigation calls usually mean a hypothesis is "
                        "being formed ad-hoc instead of via the methodology.\n\n"
                        "Run `Skill superpowers:systematic-debugging` BEFORE the "
                        "next read. The skill enforces: gather evidence first, "
                        "enumerate hypotheses, test cheapest first, document "
                        "falsifications. Without it, sessions anchor on the "
                        "first plausible-sounding cause and miss systemic issues.\n\n"
                        "Triggers like 'this is weird', 'I didn't expect', 'it "
                        "worked yesterday' are the classic signature -- so are "
                        "stale-data investigations and chained MCP/Bash status "
                        "queries. Source: wr-2026-04-23 (HQ) "
                        "systematic-debugging-skipped-on-ceo-brief-investigation."
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
