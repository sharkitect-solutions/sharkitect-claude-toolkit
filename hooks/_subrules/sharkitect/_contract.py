"""
Sub-Rule Contract for UserPromptSubmit Dispatcher

Every sub-rule under _subrules/<namespace>/<rule_name>.py exposes ONE function:

    def check(prompt: str, context: dict) -> SubRuleResult | None

The dispatcher loads enabled sub-rules from
~/.claude/config/userpromptsubmit-dispatcher.json, runs each check(), and
emits aggregated additionalContext nudges to Claude.

Context dict keys (provided by dispatcher):
    - active_plans: list[str] - plan file paths from plans-registry.md
      (populated by dispatcher in v3 prep; sub-rules may read but should
      tolerate empty list)
    - session_brief: str | None - recent session brief content if available
      (populated by dispatcher in v4 prep)
    - workspace: str - canonical workspace name (workforce-hq | skill-management-hub | sentinel)
    - bypass_phrases_in_prompt: list[str] - bypass phrases ('skip <slug>')
      detected in prompt via word-boundary regex

Bypass contract per Strict Bypass Vocabulary protocol:
    Each sub-rule declares bypass_keyword in the slug form 'skip <slug>'.
    Dispatcher checks bypass_phrases_in_prompt for this phrase BEFORE running
    the sub-rule (word-boundary match, not substring).
    Match = skip with Category A bypass logged to <tempdir>/claude_bypass_log.jsonl.

Mode semantics:
    'advisory' (v1 default) - nudge appears as additionalContext; Claude is free to proceed
    'hard_block' (RESERVED for v2; do not use in v1) - would block prompt submission

Severity vocabulary (NEW v1.5):
    'info'     (default) - informational; operator may act or skip
    'warning'  - quality/operational concern; should be addressed but not blocking
    'critical' - blocks work / data loss / production failure; rare for nudges
    Matches the log-level vocabulary used in cross_workspace_requests.severity.
    Dispatcher uses severity for aggregation order + length-budget truncation (v2+).

match_evidence (NEW v1.5):
    Optional short string explaining WHY the rule fired. When populated,
    debugging "why did this rule fire?" doesn't require re-running the rule
    logic mentally. Example: "matched pattern 'is X done' at offset 12".

Failure isolation:
    A sub-rule that raises an exception MUST NOT crash the dispatcher.
    Dispatcher catches, logs the error, continues to next sub-rule.

History:
    v1.5 (2026-05-19) - added severity + match_evidence per ai-systems-architect
      defect #3. Removed recent_tool_calls context key per defect #2 + Option D
      (100% Verification protocol mandates per-action, not per-session).
"""
from dataclasses import dataclass
from typing import Literal, Optional


@dataclass(frozen=True)
class SubRuleResult:
    """Returned by a sub-rule's check() when the rule wants to fire."""
    mode: Literal["advisory", "hard_block"]
    message: str
    rule_name: str
    bypass_keyword: str  # the exact 'skip <slug>' phrase that disables this rule
    severity: Literal["info", "warning", "critical"] = "info"
    match_evidence: Optional[str] = None

    def __post_init__(self):
        if self.mode == "hard_block":
            # v1 enforcement: hard_block reserved for v2 after empirical validation
            raise ValueError("hard_block mode reserved for v2; use advisory in v1")
        if not self.bypass_keyword.startswith("skip "):
            raise ValueError(f"bypass_keyword must start with 'skip ': got {self.bypass_keyword!r}")
        if self.severity not in ("info", "warning", "critical"):
            # Strict vocabulary -- aligns with cross_workspace_requests.severity
            # and prevents priority/severity conflation (low/medium/high are
            # priority values, not severity).
            raise ValueError(
                f"severity must be one of info|warning|critical (log-level "
                f"taxonomy): got {self.severity!r}"
            )
