"""
hq-content-skill-stack-enforcer.py - PreToolUse BLOCKING hook (3 rules)

Consolidated hook that enforces the HQ content skill/agent stack BEFORE
Write/Edit on classified content lands on disk. Closes 3 work requests in
one consolidated mechanism (Option B from Resume Instructions, 2026-04-25).

REFACTORED 2026-04-27 (wr-hq-2026-04-27-003 design portion + 006 Tier 2):
  - Bypass detection delegated to shared ~/.claude/scripts/_lib/intent_detection.py
  - Recognizes natural-language imperatives ("update X", "go ahead and Y",
    "do it", "let's broaden Z") via the shared helper -- no need to learn
    private bypass keywords during user-driven cascade work.
  - Literal bypass keywords still respected via bypass_phrases arg (legacy compat).
  - Rule 2 SOW/proposal/contract gating now SECTION-AWARE: 4-skill stack
    fires only when the diff/content overlaps Sections 4 (scope), 10
    (limitation of liability), 13 (material breach), or 14 (jurisdiction).
    Cosmetic edits (typo fixes, header tweaks) elsewhere in a SOW pass through.

RULES (each independent, can fire individually)
================================================
Rule 1 - K3 client deliverable -> brand-reviewer Agent dispatch
  Trigger:   path matches knowledge-base/clients/*/* AND content has
             frontmatter `classification: K3` OR path under
             knowledge-base/clients/<name>/deliverables/
  Required:  Agent tool invocation this session with subagent_type
             matching `brand-reviewer` (case-insensitive substring)
  Source:    wr-2026-04-23 (HQ) brand-reviewer-agent-not-dispatched-on-bilingual-client-deliverable
  Skill ref: skills/hq-brand-review "Paired Agent" section -- skill is
             quick-check; K3 client-facing deliverables require Agent dispatch

Rule 2 - SOW / proposal / contract -> 4-skill stack
  Trigger:   filename matches `(sow|proposal|contract|statement-of-work)`
             OR path under `templates/(sow|proposals|contracts)/`
  Required:  ALL FOUR skills invoked this session (any order):
               - copywriting
               - writing-clearly-and-concisely
               - contract-legal
               - hq-brand-review
  Source:    wr-2026-04-23 (HQ) copywriting-and-concise-skills-skipped-on-sow-template
  Reason:    Routing guide mandates the 4-skill stack for legal-clause
             content (Section 13/14 material breach, jurisdiction, etc.)

Rule 3 - Bilingual -es.md -> independent Spanish brand-review
  Trigger:   filename ends in `-es.md` AND path under knowledge-base/clients/
  Required:  hq-brand-review skill invoked this session AFTER the
             corresponding English source file's most-recent Write/Edit
             (heuristic: same-session invocation suffices)
  Source:    wr-2026-04-23 (HQ) spanish-brand-review-skipped-on-dangeles-rewrite
  Reason:    hq-brand-review skill's edge-case guidance: bilingual content
             scored INDEPENDENTLY per language (Spanish norms slightly more
             formal, watch for direct translations of banned terms)

INPUTS
  PreToolUse hook on Write|Edit. Reads tool_name, tool_input.file_path,
  tool_input.content / new_string, transcript_path.

JOURNAL SOURCE
  Reads <tempdir>/claude_tool_usage_journal.jsonl (written by
  log-tool-invocation.py PostToolUse hook on Skill+Agent).
  Records have shape:
    {"tool": "Skill", "skill": "<name>", "timestamp": "<ISO>"}
    {"tool": "Agent", "subagent_type": "<name>", "timestamp": "<ISO>"}

BYPASS (any one allows the operation)
  1. Recent user message contains: "skip content-stack", "skip stack-enforcer",
     "skip k3-brand-agent", "skip sow-stack", "skip bilingual-brand"
  2. Hook removed from settings.json

GRACEFUL DEGRADATION
  - Missing journal -> ALLOW (no deadlock)
  - Missing transcript_path -> only journal-based bypass works
  - Path/content fields missing -> ALLOW (likely TodoWrite or unrelated)
  - Any unhandled exception -> exit 0 (allow)

DESIGN
  - Hook only fires for HQ workspace files (path contains
    `1.- SHARKITECT DIGITAL WORKFORCE HQ` -- canonical filesystem name).
    Other workspaces are unaffected.
  - Each rule blocks INDEPENDENTLY -- if all 3 trigger and ANY required skill
    is missing, the strictest rule's reason is reported.
  - Multiple rules can fire on one file. Reasons are concatenated.

Pure stdlib. ASCII-only output. Input/output via JSON on stdin/stdout.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile

# Make _lib helper importable (pure stdlib, no install needed)
_LIB_DIR = os.path.expanduser("~/.claude/scripts/_lib")
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)
try:
    import intent_detection  # type: ignore
except Exception:
    intent_detection = None  # graceful: legacy code path will run if helper missing


JOURNAL_PATH = os.path.join(tempfile.gettempdir(), "claude_tool_usage_journal.jsonl")
# Lookback for user messages in transcript when checking for bypass phrases.
# Raised from 3 to 15 (2026-04-27, wr-hq-2026-04-27-001) AND combined with a
# tool-result filter -- prior bug: tool_result messages count as user-type in
# the transcript schema, so after 3 successful Edits the bypass expired and
# the gate re-fired. Now we filter tool-results AND keep a generous window
# so user-driven cascade work doesn't require re-issuing bypass per edit batch.
TRANSCRIPT_USER_LOOKBACK = 15

HQ_WORKSPACE_MARKER = "1.- SHARKITECT DIGITAL WORKFORCE HQ"

# ---- Rule 1: K3 client deliverable ----
K3_PATH_RE = re.compile(
    r"[/\\]knowledge-base[/\\]clients[/\\]",
    re.I,
)
K3_FRONTMATTER_RE = re.compile(
    r"^---.*?\bclassification\s*:\s*K3\b.*?---",
    re.I | re.S,
)
BRAND_REVIEWER_AGENT_RE = re.compile(r"brand-reviewer", re.I)

# ---- Rule 2: SOW / proposal / contract ----
SOW_FILENAME_RE = re.compile(
    r"(sow|proposal|contract|statement[-_]of[-_]work|master[-_]services[-_]agreement|msa)",
    re.I,
)
SOW_PATH_RE = re.compile(
    r"[/\\]templates[/\\](?:sow|proposals?|contracts?)[/\\]",
    re.I,
)
SOW_REQUIRED_SKILLS = (
    "copywriting",
    "writing-clearly-and-concisely",
    "contract-legal",
    "hq-brand-review",
)

# Section-aware diff parsing (added 2026-04-27, wr-hq-2026-04-27-003 deferred
# scope). 4-skill stack should fire ONLY when the diff overlaps the legal-clause
# sections that triggered the original wr-2026-04-23 incident:
#   - Section 4: Scope / Deliverables (ambiguity = scope creep risk)
#   - Section 10: Limitation of Liability
#   - Section 13: Material Breach
#   - Section 14: Jurisdiction / Governing Law
# Cosmetic edits to other sections (typo fixes, header style, etc.) bypass
# the 4-skill requirement -- they don't carry legal risk.
#
# Detection patterns -- match Markdown heading styles commonly used in HQ
# SOW templates:
#   "## 4. Scope of Work"
#   "## Section 13 — Material Breach"
#   "### 14. Governing Law"
#   "## 10. Limitation of Liability"
SOW_LEGAL_SECTIONS = (4, 10, 13, 14)
SOW_SECTION_HEADING_RE = re.compile(
    r"(?:^|\n)#{1,6}\s+(?:section\s+)?(?:no\.?\s*)?(\d{1,2})(?:\.|:|\s+|\b)",
    re.IGNORECASE,
)
# Keyword fallback -- if a diff contains words indicating legal-clause content
# even without a numbered section heading, gate fires.
SOW_LEGAL_KEYWORD_RE = re.compile(
    r"\b(?:material\s+breach|limitation\s+of\s+liability|governing\s+law|"
    r"jurisdiction|venue|indemnif(?:y|ication)|hold\s+harmless|"
    r"force\s+majeure|warrant(?:y|ies)\s+disclaimer|exclusive\s+remedy|"
    r"consequential\s+damages|liquidated\s+damages|scope\s+of\s+work)\b",
    re.IGNORECASE,
)

# ---- Rule 3: Bilingual -es.md ----
BILINGUAL_FILENAME_RE = re.compile(r"-es\.md$", re.I)
BILINGUAL_REQUIRED_SKILL = "hq-brand-review"

# ---- Bypass ----
BYPASS_PHRASES = (
    # Original literal-keyword bypasses (keep these for backwards compat)
    "skip content-stack",
    "skip stack-enforcer",
    "skip k3-brand-agent",
    "skip sow-stack",
    "skip bilingual-brand",
    "skip hq-content-stack",
    # Natural-language imperative bypasses (added 2026-04-27, wr-hq-2026-04-27-001
    # + wr-hq-2026-04-27-003). User explicitly stated: "If we are working and I
    # tell you to do it, that should bypass this hook anyway." These phrases
    # signal explicit user direction. The gate stays for AI-autonomous edits
    # (no recent imperative) but lets user-driven work flow without ritual
    # bypass keywords. Match against full lowercase user message.
    "go ahead and edit",
    "go ahead and update",
    "go ahead and modify",
    "go ahead and change",
    "go ahead and broaden",
    "go ahead and proceed",
    "go ahead and execute",
    "execute this",
    "do it",
    "proceed with the edit",
    "make the edit",
    "make the change",
    "yes do that",
    "yes proceed",
    "i am driving this",
    "i'm driving this",
)


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def load_journal():
    """Return list of journal records (Skill/Agent invocations this session)."""
    if not os.path.exists(JOURNAL_PATH):
        return []
    try:
        with open(JOURNAL_PATH, "r", encoding="utf-8") as fh:
            records = []
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            return records
    except OSError:
        return []


def skill_was_invoked(records, name):
    """True if a Skill invocation in journal matches `name` (case-insensitive,
    accepts plugin-namespaced form like `superpowers:writing-plans`)."""
    target = name.lower()
    for rec in records:
        if rec.get("tool") != "Skill":
            continue
        skill = str(rec.get("skill", "")).lower()
        if skill == target or skill.endswith(":" + target) or skill.startswith(target + ":"):
            return True
    return False


def agent_was_dispatched(records, pattern_re):
    """True if an Agent invocation's subagent_type matches the regex."""
    for rec in records:
        if rec.get("tool") != "Agent":
            continue
        subagent = str(rec.get("subagent_type", ""))
        if pattern_re.search(subagent):
            return True
    return False


def _is_tool_result_message(content):
    """Return True if a transcript record's content is purely tool-result echoes
    (not real user prose). Tool-result records have type=='user' in the schema
    but their content is a list with at least one item where type=='tool_result'.
    Filtering these out (2026-04-27, wr-hq-2026-04-27-001) prevents the bypass
    window from expiring after 3 successful tool calls."""
    if not isinstance(content, list):
        return False
    has_tool_result = any(
        isinstance(p, dict) and p.get("type") == "tool_result"
        for p in content
    )
    has_text = any(
        isinstance(p, dict) and p.get("type") == "text" and p.get("text", "").strip()
        for p in content
    )
    # Pure tool-result echo (no accompanying user text) is filtered out.
    # If there's both tool_result AND user text in the same record, count it
    # as a real user message (rare edge case).
    return has_tool_result and not has_text


def read_recent_user_messages(transcript_path):
    if not transcript_path or not os.path.exists(transcript_path):
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
        if rec.get("type") != "user":
            continue
        content = rec.get("message", {}).get("content", "")
        # Filter out tool-result echoes -- they're not real user prose
        if _is_tool_result_message(content):
            continue
        if isinstance(content, list):
            content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
        text = str(content).lower().strip()
        if not text:
            continue
        msgs.append(text)
    return msgs


def has_bypass_phrase(msgs):
    for m in msgs:
        for phrase in BYPASS_PHRASES:
            if phrase in m:
                return True
    return False


def is_k3_client_deliverable(file_path, content):
    """Rule 1 trigger detection."""
    if not K3_PATH_RE.search(file_path):
        return False
    if K3_FRONTMATTER_RE.search(content):
        return True
    # If path goes under deliverables/ subdir, treat as K3 even without frontmatter
    if re.search(r"[/\\]deliverables[/\\]", file_path, re.I):
        return True
    return False


def is_sow_content(file_path):
    """Rule 2 trigger detection (file-path level)."""
    base = os.path.basename(file_path)
    if SOW_FILENAME_RE.search(base):
        return True
    if SOW_PATH_RE.search(file_path):
        return True
    return False


def diff_touches_legal_sections(content):
    """Section-aware Rule 2 trigger.

    Returns True if the content/diff being written overlaps any of the
    legal-clause sections (4/10/13/14) OR mentions legal-clause keywords
    that imply legal content regardless of numbering.

    Returns False if the diff is purely cosmetic / non-legal (e.g., typo
    fix in Section 6, header restyle, table formatting).

    Behavior on missing/empty content: True (fail-safe -- if we can't tell
    what's being written, default to gating).
    """
    if not content:
        return True
    # Direct keyword match -- if the diff mentions any legal-clause concept,
    # gate fires.
    if SOW_LEGAL_KEYWORD_RE.search(content):
        return True
    # Section-heading match -- if the diff contains a numbered heading
    # matching a tracked legal section, gate fires.
    for match in SOW_SECTION_HEADING_RE.finditer(content):
        try:
            section_num = int(match.group(1))
        except (TypeError, ValueError):
            continue
        if section_num in SOW_LEGAL_SECTIONS:
            return True
    return False


def is_bilingual_spanish_client_file(file_path):
    """Rule 3 trigger detection."""
    if not K3_PATH_RE.search(file_path):
        return False
    return bool(BILINGUAL_FILENAME_RE.search(file_path))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return 0

    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    file_path = str(tool_input.get("file_path", "") or "")
    if not file_path:
        return 0

    # Only enforce on HQ workspace files
    if HQ_WORKSPACE_MARKER not in file_path:
        return 0

    if tool_name == "Write":
        content = str(tool_input.get("content", "") or "")
    else:
        content = str(tool_input.get("new_string", "") or "")

    # ---- Bypass check ----
    # Two-layer detection (2026-04-27 refactor, wr-hq-003):
    # 1. Shared intent_detection helper -- recognizes natural-language
    #    imperatives, session intent flags, AND the literal bypass phrases.
    # 2. Legacy in-file detection -- preserved as a fallback so this hook
    #    works even if the helper is missing/broken.
    transcript_path = data.get("transcript_path") or ""
    if intent_detection is not None:
        try:
            if intent_detection.is_user_driven(
                transcript_path,
                file_path=file_path,
                bypass_phrases=BYPASS_PHRASES,
                lookback=TRANSCRIPT_USER_LOOKBACK,
            ):
                return 0
        except Exception:
            pass  # fall through to legacy check
    # Legacy fallback (literal bypass phrase only)
    recent_msgs = read_recent_user_messages(transcript_path)
    if has_bypass_phrase(recent_msgs):
        return 0

    journal = load_journal()

    # ---- Evaluate each rule ----
    violations = []

    # Rule 1: K3 client deliverable -> brand-reviewer Agent dispatch
    if is_k3_client_deliverable(file_path, content):
        if not agent_was_dispatched(journal, BRAND_REVIEWER_AGENT_RE):
            violations.append(
                "Rule 1 (K3 client deliverable): brand-reviewer Agent NOT "
                "dispatched this session.\n"
                "  Required: Agent tool invocation with subagent_type "
                "containing 'brand-reviewer' BEFORE writing K3 client content.\n"
                "  Why: hq-brand-review skill quick-check is insufficient for "
                "K3 client-facing deliverables. Per skill's 'Paired Agent' "
                "section, K3 + AI-generated + multi-document consistency "
                "requires Agent dispatch (full 6-step protocol)."
            )

    # Rule 2: SOW / proposal / contract -> 4-skill stack
    # Section-aware gating: only fire when the diff overlaps a legal-clause
    # section (4/10/13/14) or contains legal-clause keywords. Cosmetic edits
    # to non-legal sections pass through (added 2026-04-27, wr-hq-003).
    if is_sow_content(file_path) and diff_touches_legal_sections(content):
        missing_skills = [s for s in SOW_REQUIRED_SKILLS if not skill_was_invoked(journal, s)]
        if missing_skills:
            violations.append(
                "Rule 2 (SOW / proposal / contract -- legal-clause content): "
                "missing skill(s) from the required 4-skill stack.\n"
                f"  Missing: {', '.join(missing_skills)}\n"
                f"  Required (all four): {', '.join(SOW_REQUIRED_SKILLS)}\n"
                "  Why: Legal-clause content (material breach, jurisdiction, "
                "limitation of liability, force majeure) requires the full "
                "4-skill stack. Source: wr-2026-04-23 (Section 13/14 rewrite "
                "shipped without copywriting + writing-clearly-and-concisely).\n"
                "  Section-aware mode: this gate fires ONLY when the diff "
                "overlaps Sections 4 (scope), 10 (liability), 13 (breach), "
                "14 (jurisdiction), or contains legal-clause keywords. "
                "Cosmetic edits to other sections of a SOW pass through."
            )

    # Rule 3: Bilingual -es.md -> Spanish brand-review
    if is_bilingual_spanish_client_file(file_path):
        if not skill_was_invoked(journal, BILINGUAL_REQUIRED_SKILL):
            violations.append(
                "Rule 3 (Bilingual Spanish client file): hq-brand-review "
                "NOT invoked this session.\n"
                "  Required: hq-brand-review skill invocation BEFORE writing "
                "Spanish translation. Spanish must be scored INDEPENDENTLY -- "
                "Spanish business communication norms are slightly more "
                "formal (+1 formality target), and direct translations of "
                "banned terms ('sinergia', 'de vanguardia', 'al final del "
                "dia') must be caught.\n"
                "  Why: Source wr-2026-04-23 (D'Angeles rewrite shipped "
                "without independent Spanish brand-review)."
            )

    if not violations:
        return 0

    reason = (
        "BLOCKING: HQ content skill stack violation(s) detected.\n\n"
        + "\n\n".join(violations)
        + "\n\n"
        f"File: {file_path}\n\n"
        "To proceed: invoke the missing skills/agents via the Skill or "
        "Agent tool, then retry this Write/Edit.\n"
        "To bypass for verified-safe routine edits, include one of these "
        'phrases in your next user message: "skip content-stack", '
        '"skip stack-enforcer", or rule-specific bypass '
        '("skip k3-brand-agent", "skip sow-stack", "skip bilingual-brand"), '
        "and retry.\n\n"
        "Source: wr-2026-04-23 (HQ x3) consolidated into Option B per "
        "Resume Instructions 2026-04-25."
    )

    deny(reason)
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
