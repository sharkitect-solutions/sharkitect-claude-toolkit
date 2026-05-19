"""
verify_state sub-rule - detects AI-about-to-claim-state without recent verification.

Fires when:
- User prompt matches a state-query pattern ("is X done?", "what's the status?", etc.)
- AND no verification tool call (Read/Grep/Bash/Supabase MCP) in recent_tool_calls

Bypass: 'skip verify-state' in the user's prompt.
"""
import re

from _subrules.sharkitect._contract import SubRuleResult

STATE_QUERY_PATTERNS = [
    r"\bis\s+(?:\S+\s+){1,4}(done|complete|finished|landed|deployed|shipped|closed|merged|ready)\b",
    r"\bdid\s+(?:\S+\s+){1,4}(land|ship|deploy|complete|finish|close|merge|work)\b",
    r"\bhas\s+(?:\S+\s+){1,4}(been|landed|shipped|deployed|completed|finished|closed|merged)\b",
    r"\bwhat'?s\s+the\s+(status|state|progress)\b",
    r"\bwhere\s+(are\s+we|do\s+we\s+stand)\b",
    r"\b(status|state|progress)\s+of\s+\S+",
    r"\bdoes\s+(?:\S+\s+){1,4}(exist|work|run|fire)\b",
]

VERIFICATION_TOOLS = {
    "Read", "Grep", "Glob", "Bash",
}

VERIFICATION_TOOL_PREFIXES = (
    "mcp__claude_ai_Supabase__",  # Supabase MCP queries count
    "mcp__github-mcp__get_",       # GitHub read-only counts
    "mcp__github-mcp__list_",
    "mcp__github-mcp__search_",
)


def _is_state_query(prompt: str) -> bool:
    p = prompt.lower()
    for pattern in STATE_QUERY_PATTERNS:
        if re.search(pattern, p):
            return True
    return False


def _has_recent_verification(recent_tool_calls: list) -> bool:
    for call in recent_tool_calls:
        name = call.get("name", "")
        if name in VERIFICATION_TOOLS:
            return True
        if any(name.startswith(prefix) for prefix in VERIFICATION_TOOL_PREFIXES):
            return True
    return False


def check(prompt: str, context: dict):
    if not _is_state_query(prompt):
        return None
    recent = context.get("recent_tool_calls", [])
    if _has_recent_verification(recent):
        return None
    return SubRuleResult(
        mode="advisory",
        message=(
            "Before answering this state-query, verify by reading the actual "
            "source (Read / Grep / Bash / Supabase query). The 100% Verification "
            "Before Any Action protocol requires direct source reads, not "
            "inference from memory. Cite what you read."
        ),
        rule_name="verify_state",
        bypass_keyword="skip verify-state",
    )
