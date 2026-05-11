"""
rule-file-self-audit-gate.py - PostToolUse self-audit gate for rule-class files.

Fires after Edit/Write on rule-class files (universal-protocols.md,
lessons-learned.md, CLAUDE.md, MEMORY.md / topic files, settings.json files,
~/.claude/rules/**, ~/.claude/docs/plans-registry.md). Injects an honest
self-audit prompt with the per-file-class checklist + Strict Bypass Vocabulary
requirements.

The gate is corrective, not preventive: PostToolUse fires AFTER the write
succeeds. The injected context forces the AI to honestly answer whether
prerequisite checks were run BEFORE the edit. If "no": remediate (run missed
checks, fix contradictions, revise the edit) BEFORE proceeding.

Spec source:
  ~/.claude/rules/universal-protocols.md
    'Post-Action Self-Audit on Rule-Class Files' section
    'Strict Bypass Vocabulary for Runtime Audits' section
Plan source:
  3.- Skill Management Hub/docs/superpowers/plans/2026-05-11-post-hard-stop-system-reassessment.md
  Task 0.5 (Pre-Phase-1 Foundational Hook Build)

Module API (used by tests + main()):
  evaluate(payload: dict) -> EvalResult(additional_context: str | None, file_class: str | None)
  validate_bypass(justification: str) -> BypassResult(valid: bool, rejection_reason: str, category: str | None)

Loose-excuse catcher (validate_bypass): rejects bypass justifications that do
NOT explicitly name Category A/B/C/D AND do NOT include the literal skip phrase.
Logging deferred to Phase 2 per Task 0.5 scope.

Bypass keyword: "skip rule-self-audit" (single consolidated phrase, per
Strict Bypass Vocabulary "shared CONSOLIDATED bypass surface").

Pure stdlib. ASCII-only.
"""
from __future__ import annotations

import fnmatch
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace


CONFIG_PATH = Path.home() / ".claude" / "config" / "rule-file-checklists.json"


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"classes": [], "bypass_vocabulary": {}}


def _normalize_path(p: str) -> str:
    """Normalize path separators + lowercase for glob matching."""
    return p.replace("\\", "/").lower()


def _match_class(file_path: str, classes: list[dict]) -> dict | None:
    """Return the first matching file-class config, or None."""
    norm = _normalize_path(file_path)
    for cls in classes:
        for glob_pat in cls.get("globs", []):
            pat = _normalize_path(glob_pat)
            if fnmatch.fnmatch(norm, pat):
                return cls
    return None


# ---------------------------------------------------------------------------
# evaluate() - per-file-class checklist injection
# ---------------------------------------------------------------------------

def evaluate(payload: dict) -> SimpleNamespace:
    """Evaluate a PostToolUse payload and return injected context (or None).

    Returns SimpleNamespace with:
      .additional_context : str | None
      .file_class         : str | None
    """
    result = SimpleNamespace(additional_context=None, file_class=None)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        return result

    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            return result

    file_path = str(tool_input.get("file_path", "") or "")
    if not file_path:
        return result

    config = _load_config()
    cls = _match_class(file_path, config.get("classes", []))
    if cls is None:
        return result

    result.file_class = cls.get("file_class_name", "rule-class file")
    bv = config.get("bypass_vocabulary", {})
    result.additional_context = _build_audit_prompt(cls, bv, file_path)
    return result


def _build_audit_prompt(cls: dict, bv: dict, file_path: str) -> str:
    """Build the additionalContext message: file class + checklist + honest-answer prompt + bypass vocab."""
    class_name = cls.get("file_class_name", "rule-class file")
    basename = os.path.basename(file_path)
    checklist_items = cls.get("checklist", [])

    lines = []
    lines.append(
        f"RULE-FILE SELF-AUDIT GATE fired after Edit/Write on `{basename}` "
        f"(file class: {class_name})."
    )
    lines.append("")
    lines.append(
        "Per the Post-Action Self-Audit on Rule-Class Files protocol "
        "(NON-NEGOTIABLE in universal-protocols.md), and per the "
        "Contradiction Check Before Rule / Doc Updates protocol it "
        "enforces, answer HONESTLY: did you complete each prerequisite "
        "check BEFORE this edit?"
    )
    lines.append("")
    lines.append("Pre-edit checklist for this file class:")
    for i, item in enumerate(checklist_items, 1):
        lines.append(f"  {i}. {item}")
    lines.append("")
    lines.append(
        "If your honest answer to ANY item is 'no': you MUST remediate "
        "BEFORE proceeding with other work. Steps: (a) run the missed "
        "checks now, (b) report what you found, (c) if findings warrant, "
        "revise THIS edit, (d) only then continue."
    )
    lines.append("")
    lines.append(
        "Documentation has repeatedly proven insufficient -- past sessions "
        "skipped just-added rules within the same session. This gate is the "
        "runtime backstop. Do not rationalize past it."
    )
    lines.append("")
    lines.append(
        "Bypass (Strict Bypass Vocabulary): valid ONLY if the user's CURRENT-"
        "session message contains the literal phrase `skip rule-self-audit` "
        "AND your bypass note cites one of:"
    )
    cats = bv.get("categories") or {
        "A": "Explicit user direction",
        "B": "Emergency manual repair",
        "C": "Self-referential meta-edit",
        "D": "Standing exemption documented in the gate's own definition",
    }
    for letter in ("A", "B", "C", "D"):
        desc = cats.get(letter, "")
        lines.append(f"  Category {letter} -- {desc}")
    lines.append("")
    lines.append(
        "Loose excuses are INVALID: 'I already verified', 'just this once', "
        "'this is a small edit', 'we already did this', 'the user implied'. "
        "If you cannot name a specific Category A/B/C/D with evidence, you "
        "are NOT bypassing -- you are skipping. Run the checklist."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# validate_bypass() - loose-excuse catcher
# ---------------------------------------------------------------------------

# Loose-excuse patterns (substrings, case-insensitive). If a justification
# contains ONLY these and no Category A/B/C/D anchor, reject as loose excuse.
LOOSE_EXCUSE_PATTERNS = (
    "i already verified",
    "already verified",
    "just this once",
    "small edit",
    "we already ran",
    "we already did",
    "ran this scan earlier",
    "user implied",
    "would be faster",
    "this case is different",
    "doesn't need the check",
    "does not need the check",
    "trivial",
)

# Category anchors -- a valid bypass MUST name one of these explicitly.
CATEGORY_ANCHORS = {
    "A": ("category a", "category-a", "(a)", "cat a", "cat. a"),
    "B": ("category b", "category-b", "(b)", "cat b", "cat. b"),
    "C": ("category c", "category-c", "(c)", "cat c", "cat. c"),
    "D": ("category d", "category-d", "(d)", "cat d", "cat. d"),
}


def _detect_category(text: str) -> str | None:
    """Return 'A'/'B'/'C'/'D' if the text explicitly names a category, else None."""
    low = text.lower()
    for letter, markers in CATEGORY_ANCHORS.items():
        for m in markers:
            if m in low:
                return letter
    return None


def _is_loose_excuse(text: str) -> bool:
    low = text.lower()
    return any(p in low for p in LOOSE_EXCUSE_PATTERNS)


def validate_bypass(justification: str) -> SimpleNamespace:
    """Validate a bypass justification against Strict Bypass Vocabulary.

    Returns SimpleNamespace with:
      .valid            : bool
      .rejection_reason : str  (empty if valid)
      .category         : str | None  ('A'|'B'|'C'|'D' if valid)
    """
    result = SimpleNamespace(valid=False, rejection_reason="", category=None)

    text = (justification or "").strip()
    if not text:
        result.rejection_reason = (
            "Empty bypass justification. Strict Bypass Vocabulary requires "
            "an explicit Category A/B/C/D with evidence."
        )
        return result

    category = _detect_category(text)
    if category is None:
        # Check whether it's a recognized loose excuse for a more pointed message
        if _is_loose_excuse(text):
            result.rejection_reason = (
                "Loose excuse rejected. The justification matches a known "
                "AI self-justification pattern (e.g. 'I already verified', "
                "'just this once', 'small edit'). Per Strict Bypass "
                "Vocabulary, bypasses MUST name a specific category "
                "(A: explicit user direction / B: emergency manual repair / "
                "C: self-referential meta-edit / D: documented standing "
                "exemption)."
            )
        else:
            result.rejection_reason = (
                "Bypass justification does not name a category. Per Strict "
                "Bypass Vocabulary, valid bypasses MUST explicitly name "
                "Category A (explicit user direction), B (emergency manual "
                "repair), C (self-referential meta-edit), or D (documented "
                "standing exemption). 'Just because' is not a category."
            )
        return result

    # Category named explicitly -- accept.
    result.valid = True
    result.category = category
    return result


# ---------------------------------------------------------------------------
# main() - PostToolUse stdin/stdout integration
# ---------------------------------------------------------------------------

def _emit(text: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": text,
        }
    }
    sys.stdout.write(json.dumps(payload))
    sys.stdout.write("\n")


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0

    if not isinstance(data, dict):
        return 0

    result = evaluate(data)
    if result.additional_context:
        _emit(result.additional_context)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except Exception:
        rc = 0
    sys.exit(rc)
