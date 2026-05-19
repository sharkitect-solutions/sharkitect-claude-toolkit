"""
Sub-Rule Contract for UserPromptSubmit Dispatcher

Every sub-rule under _subrules/<namespace>/<rule_name>.py exposes ONE function:

    def check(prompt: str, context: dict) -> SubRuleResult | None

The dispatcher loads enabled sub-rules from
~/.claude/config/userpromptsubmit-dispatcher.json, runs each check(), and
emits aggregated additionalContext nudges to Claude.

Context dict keys (provided by dispatcher):
    - recent_tool_calls: list[dict] - last 20 tool calls (name, args_summary, ts)
    - active_plans: list[str] - plan file paths from plans-registry.md
    - session_brief: str | None - recent session brief content if available
    - workspace: str - canonical workspace name (workforce-hq | skill-management-hub | sentinel)
    - bypass_phrases_in_prompt: list[str] - bypass phrases (skip <slug>) detected in prompt

Bypass contract per Strict Bypass Vocabulary protocol:
    Each sub-rule declares bypass_keyword in the slug form 'skip <slug>'.
    Dispatcher checks the prompt for this phrase BEFORE running the sub-rule.
    Match = skip with Category A bypass logged to <tempdir>/claude_bypass_log.jsonl.

Mode semantics:
    'advisory' (v1 default) - nudge appears as additionalContext; Claude is free to proceed
    'hard_block' (RESERVED for v2; do not use in v1) - would block prompt submission

Failure isolation:
    A sub-rule that raises an exception MUST NOT crash the dispatcher.
    Dispatcher catches, logs the error, continues to next sub-rule.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class SubRuleResult:
    """Returned by a sub-rule's check() when the rule wants to fire."""
    mode: Literal["advisory", "hard_block"]
    message: str
    rule_name: str
    bypass_keyword: str  # the exact 'skip <slug>' phrase that disables this rule

    def __post_init__(self):
        if self.mode == "hard_block":
            # v1 enforcement: hard_block reserved for v2 after empirical validation
            raise ValueError("hard_block mode reserved for v2; use advisory in v1")
        if not self.bypass_keyword.startswith("skip "):
            raise ValueError(f"bypass_keyword must start with 'skip ': got {self.bypass_keyword!r}")
