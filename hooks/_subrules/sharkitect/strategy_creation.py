"""strategy_creation sub-rule - detects forward-looking strategy work
(pricing / positioning / proposal / strategic decision) and nudges the
Sharkitect methodology stack before the AI commits to an artifact.

Stacks on the v1.5 fortified Build 6 pattern. Severity=warning because
strategy skips have a documented recurrence cost (4+ incidents in HQ +
Sentinel; see wr-hq-2026-05-11-001, wr-hq-2026-05-11-003, wr-hq-2026-05-14-002).

Bypass: 'skip strategy-creation' (word-boundary match) in the user's prompt.

Domain coverage:
    - Pricing decisions: new pricing model, tiering, WTP, value-based, price points
    - Positioning / GTM: April Dunford method, ICP, competitive positioning, market category
    - Proposal / SOW authoring: client proposals, statements of work
    - Strategic decisions: market entry, business-model pivot, strategic direction

Pairs with the CEO Advisor Mandatory Invocation rule (universal-protocols.md,
2026-05-17 S55) -- the nudge message names both the methodology stack AND
ceo-advisor so the operator gets the full pre-decision lens.

History:
    v2.0 (2026-05-20) - initial implementation per Build 6 spec §7 sub-rule
      roadmap. Patterns scoped to forward-looking authoring verbs ("design",
      "draft", "create") to keep state-query prompts under verify_state's
      domain. Severity=warning reflects the recurrence-prone failure class.
"""
import re

from _subrules.sharkitect._contract import SubRuleResult


# Each pattern carries a domain label so match_evidence + downstream
# telemetry can attribute the fire to a specific category. Patterns use
# word-boundary anchors to contain false positives (e.g., 'pric' inside
# 'apricot' must not match).
STRATEGY_CREATION_PATTERNS = [
    # ---- Pricing ----
    # Forward-looking pricing authoring: design / draft / set / build / propose +
    # pricing-related noun. Past-tense queries fall to verify_state.
    (r"\b(new|set|design|create|build|draft|update|change|propose|model|rework|redesign)\s+(?:\S+\s+){0,4}(pric(?:e|es|ing)?\b|tier(?:s|ing)?\b|rate\s+card\b|pricing\s+model\b|pricing\s+structure\b|pricing\s+strategy\b)", "pricing"),
    # Direct pricing questions ("how much should we charge")
    (r"\bhow\s+(?:much\s+)?(?:should|do)\s+we\s+(?:charge|price|bill)\b", "pricing"),
    # Methodology-named keywords (WTP, value-based, anchoring, elasticity)
    (r"\b(willingness[\s\-]to[\s\-]pay|wtp\s+(?:analysis|anchor|target)|value[\s\-]based\s+pricing|price\s+anchor|price\s+elasticity)\b", "pricing"),
    # Price-action verbs
    (r"\b(price\s+(?:increase|decrease|change|cut|raise|drop)|monthly\s+fee|setup\s+fee|retainer\s+fee)\b", "pricing"),

    # ---- Positioning / GTM ----
    # April Dunford method (explicit signal)
    (r"\b(april\s+dunford|dunford\s+(?:method|positioning|frame))\b", "positioning"),
    # Positioning verbs and nouns
    (r"\b(position(?:ing)?|reposition(?:ing)?)\s+(?:against|as|for|vs\.?|versus|around|relative\s+to)\b", "positioning"),
    (r"\b(competitive\s+(?:positioning|frame|differentiation|advantage)|positioning\s+(?:frame|statement|brief|paper|document))\b", "positioning"),
    # GTM
    (r"\b(go[\s\-]to[\s\-]market|gtm\s+(?:strategy|plan|motion|approach|brief))\b", "positioning"),
    # ICP / segmentation
    (r"\b(icp|ideal\s+customer\s+profile|target\s+(?:market|segment|persona)|customer\s+persona)\b", "positioning"),
    # Market category
    (r"\b(market\s+(?:category|categorization|repositioning)|category\s+design)\b", "positioning"),

    # ---- Proposal / SOW authoring ----
    (r"\b(draft|write|create|build|put\s+together|author|prepare)\s+(?:\S+\s+){0,4}(proposal|sow|statement\s+of\s+work|engagement\s+letter)\b", "proposal"),
    (r"\b(client\s+proposal|sales\s+proposal|proposal\s+(?:for|to)\s+\w+)\b", "proposal"),

    # ---- Strategic decisions ----
    (r"\b(strategic\s+(?:decision|direction|frame|brief|choice|pivot|realignment))\b", "strategy"),
    (r"\bwe\s+have\s+a\s+strategic\s+decision\b", "strategy"),
    (r"\b(market\s+(?:entry|exit|expansion)|business\s+model\s+(?:change|pivot|shift)|product\s+pivot)\b", "strategy"),
]


def _matched_strategy_pattern(prompt: str):
    """Return (pattern, match_obj, domain) for first matching pattern, else None."""
    p = prompt.lower()
    for pattern, domain in STRATEGY_CREATION_PATTERNS:
        m = re.search(pattern, p)
        if m:
            return pattern, m, domain
    return None


# Nudge text — names the methodology stack so operator knows what to invoke.
# Per the using-sharkitect-methodology skill: pricing-strategy +
# marketing-strategy-pmm + smb-cfo + hq-revenue-ops + brainstorming, plus
# ceo-advisor per the CEO Advisor Mandatory Invocation rule.
_NUDGE_MESSAGE = (
    "Strategy/pricing/positioning/proposal work detected. Before authoring "
    "the artifact, invoke the Sharkitect methodology stack: "
    "(1) ceo-advisor (per the CEO Advisor Mandatory Invocation rule -- "
    "strategy work is always company-affecting), "
    "(2) pricing-strategy (WTP anchor + tier logic if pricing in scope), "
    "(3) marketing-strategy-pmm (April Dunford positioning frame if "
    "positioning in scope), "
    "(4) smb-cfo (revenue / margin / cash-flow impact), "
    "(5) hq-revenue-ops (deal-shape and tier classification if HQ work), "
    "(6) superpowers:brainstorming (enumerate 2+ alternatives before "
    "committing). The using-sharkitect-methodology skill catalogs which "
    "applies. Documentation has failed 4+ times across HQ + Sentinel "
    "(wr-hq-2026-05-11-001, wr-hq-2026-05-11-003, wr-hq-2026-05-14-002) -- "
    "this is the runtime enforcement layer."
)


def check(prompt: str, context: dict):
    """Fire on forward-looking strategy/pricing/positioning/proposal prompts.

    Returns SubRuleResult(advisory, severity=warning) when the prompt
    matches a strategy-creation pattern; returns None otherwise.

    State-query prompts ("what's our current pricing") fall to verify_state's
    domain and intentionally do not fire here. Past-tense references
    ("we already designed the pricing") are tolerated as false negatives in
    v2; v3 may add tense detection.
    """
    matched = _matched_strategy_pattern(prompt)
    if matched is None:
        return None

    pattern, m, domain = matched
    matched_phrase = m.group(0)
    evidence = (
        f"matched {domain} pattern {pattern!r} on phrase {matched_phrase!r} "
        f"at offset {m.start()}"
    )

    return SubRuleResult(
        mode="advisory",
        message=_NUDGE_MESSAGE,
        rule_name="strategy_creation",
        bypass_keyword="skip strategy-creation",
        severity="warning",
        match_evidence=evidence,
        cost_class="heuristic",
    )
