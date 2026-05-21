"""bigger_picture_first sub-rule -- detects forward-looking planning,
architecture, or build prompts and nudges the Bigger-Picture-First Discipline
protocol's 5-question test.

skip brainstorming -- executing locked plan 2026-05-21-build-6-v4-bigger-picture-first.md

Source: universal-protocols.md "Bigger-Picture-First Discipline" (added
2026-05-18 in S58). Recurrence class: 3 instances in 7 sessions (S37, S58,
S65). Per the documented "Documentation without runtime detection eventually
fails" lesson, this sub-rule is the runtime enforcement layer.

Bypass: 'skip bigger-picture-first' (word-boundary match) in the user's prompt.

History:
    v4.0 (2026-05-21) -- initial implementation per Build 6 spec Section 7
      sub-rule roadmap. Detection on USER's prompt at UserPromptSubmit;
      AI-output detection (Layer 3 prompt-hook) deferred to Phase 3 migration.
"""
import re

from _subrules.sharkitect._contract import SubRuleResult


# Patterns paired with category labels. Word-boundary anchors prevent
# embedded-substring false positives. Lower-cased matching applied in
# _first_matching_pattern() to avoid per-pattern .lower() boilerplate.
BIGGER_PICTURE_PATTERNS = [
    # ---- Explicit planning / authoring intent ----
    # Scope-marker check applied in check() -- prevents 'let's plan dinner'.
    (r"\b(let'?s|let\s+us|let\s+me|i'?ll|i\s+(?:want|need)\s+to|we\s+(?:should|need\s+to))\s+(plan|design|spec(?:\s+out)?|architect|build|refactor|restructure|reorganize|consolidate)\b", "planning_intent"),

    # Authoring intent -- anchored to start-of-prompt or sentence boundary
    # (prevents noun-form 'is the plan done?' false positives), AND
    # scope-marker check applied in check() (prevents 'draft an email').
    (r"(?:^|[\.\?!]\s+)(plan|spec|draft)\s+(?:out\s+)?(?:a|the|this|that|our|some)?\s*\S+", "authoring_intent"),

    # ---- Decision questions ----
    (r"\bshould\s+we\s+(build|design|plan|refactor|restructure|reorganize|consolidate|architect|spec|invest|adopt|migrate|pivot)\b", "decision_question"),

    (r"\bwhat\s+should\s+we\s+(build|do|work\s+on|tackle)\s+(?:next|first)\b", "roadmap_question"),

    # ---- Infrastructure creation ----
    (r"\b(?:build|create|add|introduce|spin\s+up)\s+(?:a\s+)?(?:new\s+)?(hook|script|automation|plugin|table|workflow|skill|agent|protocol|sub-?rule|dispatcher|service|api|endpoint|module|integration)\b", "infrastructure_creation"),

    # ---- Architecture decisions ----
    (r"\b(architecture|architectural)\s+(decision|choice|direction|change|shift)\b", "architecture_decision"),

    (r"\b(consolidate|deprecate|migrate|sunset|retire|kill|kill\s+off)\s+(?:\S+\s+){0,4}(hook|script|automation|plugin|table|skill|agent|protocol|service|api|module|integration|system|workflow)\b", "consolidation"),

    # ---- AIOS client work ----
    (r"\b(aios|client\s+aios)\s+(?:client\s+)?(?:feature|capability|product|module|surface|deployment)\b", "aios_productization"),
]


# Scope-marker words used for authoring_intent secondary filter. Within +/- 50
# chars of "plan/spec/draft" -- prevents "plan dinner" / "spec out the recipe"
# / "draft an email" from firing.
SCOPE_MARKERS = (
    r"feature", r"system", r"roadmap", r"phase", r"build", r"release",
    r"architecture", r"infrastructure", r"hook", r"script", r"plugin",
    r"protocol", r"workflow", r"deployment", r"migration", r"refactor",
    r"product", r"capability", r"sub-?rule", r"dispatcher",
)


def _first_matching_pattern(prompt: str, patterns):
    """Return (pattern, match_obj, category) for first matching pattern, else None."""
    p = prompt.lower()
    for pattern, category in patterns:
        m = re.search(pattern, p)
        if m:
            return pattern, m, category
    return None


def _has_scope_marker_nearby(prompt: str, match_obj) -> bool:
    """Return True if a scope-marker word appears within +/- 50 chars of the
    bare 'plan/spec/draft' match. Used to filter authoring_intent false
    positives ('plan dinner', 'draft an email')."""
    start = max(0, match_obj.start() - 50)
    end = min(len(prompt), match_obj.end() + 50)
    window = prompt[start:end].lower()
    return any(re.search(rf"\b{marker}\b", window) for marker in SCOPE_MARKERS)


_NUDGE_MESSAGE = (
    "Planning / architecture / build prompt detected. The Bigger-Picture-First "
    "Discipline protocol (NON-NEGOTIABLE, universal-protocols.md added 2026-05-18) "
    "requires the work pass 5 checks IN THIS ORDER before producing a plan or "
    "spec:\n"
    "  1. Long-term vision frame -- name the destination + cite the strategic "
    "frame document.\n"
    "  2. Walk-back from destination to today -- name the 2-3 intermediate "
    "milestones.\n"
    "  3. Alignment test for this step -- on the path or off to the side?\n"
    "  4. Scope-widening check -- adjacent in-flight work to consolidate with?\n"
    "  5. Execute with vision visible -- include 'Long-term vision served' as a "
    "first-class section in the plan / spec.\n"
    "Pair with the using-sharkitect-methodology skill (catalog of which "
    "methodology applies per task type) and superpowers:brainstorming (enumerate "
    "alternatives before committing). Recurrence class -- 3 instances in 7 "
    "sessions (S37, S58, S65); runtime detection is now the enforcement layer."
)


def check(prompt: str, context: dict):
    """Fire on forward-looking planning / architecture / build prompts.

    Detection on USER's prompt at UserPromptSubmit time. The rule does NOT
    consult active_plans / session_brief -- those are reserved for future v2
    enhancements (e.g., suppress nudge when today's brief already documents
    the long-term vision).
    """
    matched = _first_matching_pattern(prompt, BIGGER_PICTURE_PATTERNS)
    if matched is None:
        return None

    pattern, m, category = matched

    # Secondary filter for planning_intent + authoring_intent -- both require
    # a scope marker nearby. Without this, 'let's plan dinner' / 'draft an
    # email' / 'spec out this recipe' would fire.
    if category in ("planning_intent", "authoring_intent"):
        if not _has_scope_marker_nearby(prompt, m):
            return None

    matched_phrase = m.group(0)
    evidence = (
        f"matched {category} pattern {pattern!r} on phrase "
        f"{matched_phrase!r} at offset {m.start()}"
    )

    return SubRuleResult(
        mode="advisory",
        message=_NUDGE_MESSAGE,
        rule_name="bigger_picture_first",
        bypass_keyword="skip bigger-picture-first",
        severity="warning",
        match_evidence=evidence,
        cost_class="heuristic",
    )
