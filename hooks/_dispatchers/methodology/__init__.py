"""Methodology dispatcher sub-rules.

Pattern: AI is doing work-type X; the process skill that encodes HOW to do
X correctly is Y; nudge or gate Y before / during / after the work.

Each sub-rule module exports:

    def evaluate(payload: dict) -> dict | None:
        '''
        payload = {
            "tool_name": str,
            "tool_input": dict,
            "transcript_path": str | None,
            "session_id": str | None,
            "matcher": str,
            "hook_event_name": str,  # PreToolUse | PostToolUse | UserPromptSubmit
        }

        Returns:
          None                                  -> no contribution
          {"advisory": "<text>"}                -> contribute advisory text
          {"decision": "deny", "reason": "..."} -> hard block (HARD GATE only)
        '''
"""
