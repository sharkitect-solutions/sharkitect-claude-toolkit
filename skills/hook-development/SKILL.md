---
name: hook-development
description: >
  Use when user asks to create a hook, add PreToolUse/PostToolUse/Stop/SubagentStop/SessionStart/SessionEnd/UserPromptSubmit/PreCompact/Notification hook,
  validate tool use, implement prompt-based hooks, use ${CLAUDE_PLUGIN_ROOT}, set up event-driven automation in Claude Code,
  block dangerous commands via hooks, build a Claude Code plugin with hooks, or configure hooks.json.
  NEVER use for general webhook/API endpoint development, GitHub Actions, CI/CD pipelines, or non-Claude-Code event systems.
version: 0.1.0
optimized: true
optimized_date: 2026-03-11
---

# Hook Development for Claude Code Plugins

## File Index

| File | Purpose | When to Load |
|------|---------|--------------|
| `examples/load-context.sh` | SessionStart context-loading script | Building SessionStart hooks or detecting project type |
| `examples/validate-bash.sh` | Bash command validation patterns | Building PreToolUse hooks for Bash tool |
| `examples/validate-write.sh` | File write validation patterns | Building PreToolUse hooks for Write/Edit tools |
| `references/advanced.md` | Multi-stage validation, cross-event workflows, caching, external integrations | Complex hook architectures, performance optimization, state sharing |
| `references/migration.md` | Converting command hooks to prompt hooks | Refactoring existing hooks or choosing between hook types |
| `references/patterns.md` | 10 proven hook patterns (security, test enforcement, context loading, MCP monitoring, etc.) | Starting a new hook -- find the closest pattern first |
| `scripts/hook-linter.sh` | Lint hook scripts for common issues | Before deploying any command hook script |
| `scripts/README.md` | Usage guide for all utility scripts | First time using the development tools |
| `scripts/test-hook.sh` | Test hooks with sample input | Before deploying hooks to Claude Code |
| `scripts/validate-hook-schema.sh` | Validate hooks.json structure | After editing any hooks.json configuration |

## Scope Boundary

This skill covers hooks within the Claude Code plugin system ONLY. Hooks are bash scripts or LLM prompts triggered by Claude Code events.

| In Scope | Out of Scope |
|----------|-------------|
| Plugin hooks.json configuration | General webhook/API development |
| Prompt-based and command hooks | GitHub Actions / CI pipelines |
| Hook event lifecycle | Server-side event systems |
| Matcher patterns for Claude tools | MCP server development (use mcp skill) |
| ${CLAUDE_PLUGIN_ROOT} usage | Claude Desktop configuration |

## Hook Type Decision

| Signal | Choose Prompt Hook | Choose Command Hook |
|--------|-------------------|-------------------|
| Needs context-aware reasoning | Yes | No |
| Catches intent, not just patterns | Yes | No |
| Needs to run in < 50ms | No | Yes |
| Purely deterministic check (file size, regex) | No | Yes |
| Integrates external CLI tool | No | Yes |
| Needs to set environment vars | No | Yes (SessionStart only) |
| Complex multi-criteria validation | Yes | No |

Prompt hooks support: PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit.
Command hooks support: ALL events (including SessionStart, SessionEnd, PreCompact, Notification).

## Configuration Format (CRITICAL -- Two Different JSON Structures)

Plugin hooks and settings hooks use DIFFERENT JSON structures. Confusing them is the most common hook bug.

**Plugin format** -- `hooks/hooks.json` in a plugin directory:
```json
{
  "description": "Optional description",
  "hooks": {
    "PreToolUse": [{ "matcher": "Write", "hooks": [{ "type": "prompt", "prompt": "..." }] }]
  }
}
```
The `"hooks"` wrapper key is REQUIRED. Events nest inside it.

**Settings format** -- `.claude/settings.json` or `.claude.json`:
```json
{
  "hooks": {
    "PreToolUse": [{ "matcher": "Write", "hooks": [{ "type": "prompt", "prompt": "..." }] }]
  }
}
```
Events go directly under `"hooks"` alongside other settings keys.

Both formats merge at runtime. Plugin hooks and settings hooks run in parallel.

## Event Selection Guide

| Event | Fires When | Best For | Output Controls |
|-------|-----------|----------|----------------|
| PreToolUse | Before tool executes | Approve/deny/modify tool calls | `permissionDecision`: allow, deny, ask; `updatedInput` |
| PostToolUse | After tool completes | Feedback, logging, quality checks | `systemMessage` to Claude |
| Stop | Main agent wants to stop | Completeness verification | `decision`: approve or block |
| SubagentStop | Subagent wants to stop | Subagent task validation | `decision`: approve or block |
| UserPromptSubmit | User submits prompt | Context injection, prompt validation | `systemMessage`, can block |
| SessionStart | Session begins | Load context, set env vars | `$CLAUDE_ENV_FILE` for persisting env |
| SessionEnd | Session ends | Cleanup, logging | Fire-and-forget |
| PreCompact | Before context compaction | Preserve critical information | `systemMessage` survives compaction |
| Notification | Claude sends notification | External integrations, logging | Fire-and-forget |

## Hook Lifecycle (Non-Obvious Behavior)

1. **Loaded at session start ONLY.** Editing hooks.json or hook scripts mid-session has zero effect. Must restart Claude Code.
2. **All matching hooks run in parallel.** Multiple hooks in the same matcher array execute simultaneously. They cannot see each other's output. Design for independence.
3. **Plugin + settings hooks merge.** A plugin's PreToolUse hooks and the user's settings PreToolUse hooks ALL run in parallel together.
4. **Invalid JSON = silent failure.** Bad hooks.json prevents ALL hooks from loading. Always validate with `scripts/validate-hook-schema.sh`.
5. **Use `/hooks` command** to inspect which hooks are loaded in the current session.
6. **Use `claude --debug`** to see hook registration, execution logs, input/output JSON, and timing.

## Exit Code Semantics

| Exit Code | Meaning | Behavior |
|-----------|---------|----------|
| 0 | Success | stdout shown in transcript |
| 2 | Blocking error | stderr fed back to Claude as context |
| Other | Non-blocking error | Logged but does not block |

For PreToolUse: exit 2 with `permissionDecision: "deny"` blocks the tool call.
For Stop: exit 2 with `decision: "block"` prevents the agent from stopping.

## Hook Input (stdin JSON)

All hooks receive JSON via stdin. Common fields:
- `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`

Event-specific fields:
- PreToolUse/PostToolUse: `tool_name`, `tool_input`, `tool_result` (PostToolUse only)
- UserPromptSubmit: `user_prompt`
- Stop/SubagentStop: `reason`

In prompt hooks, access via: `$TOOL_INPUT`, `$TOOL_RESULT`, `$USER_PROMPT`.
In command hooks, parse with: `input=$(cat)` then `jq -r '.tool_name'`.

## Matcher Patterns

```
"Write"              -- exact tool name
"Write|Edit"         -- multiple tools (pipe-separated)
"*"                  -- all tools (wildcard)
"mcp__.*"            -- regex: all MCP tools
"mcp__asana__.*"     -- regex: specific MCP server's tools
"mcp__.*__delete.*"  -- regex: all MCP delete operations
```
Matchers are case-sensitive. Regex uses standard patterns (no delimiters).

## Environment Variables (Command Hooks)

| Variable | Available In | Purpose |
|----------|-------------|---------|
| `$CLAUDE_PROJECT_DIR` | All events | Project root path |
| `$CLAUDE_PLUGIN_ROOT` | All events | Plugin directory (use for portable paths) |
| `$CLAUDE_ENV_FILE` | SessionStart ONLY | Append `export KEY=val` to persist env vars |
| `$CLAUDE_CODE_REMOTE` | All events | Set if running in remote context |

ALWAYS use `${CLAUDE_PLUGIN_ROOT}` in hooks.json commands. Never hardcode paths.

## Bash Hook Script Template

```bash
#!/bin/bash
set -euo pipefail
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
# ... validation logic ...
# Approve: exit 0
# Block: echo '{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"reason"}' >&2 && exit 2
exit 0
```

See `examples/` for complete working scripts. Run `scripts/hook-linter.sh` before deploying.

## Implementation Workflow

1. Identify which event to hook (use Event Selection Guide above)
2. Choose prompt vs command hook (use Hook Type Decision table above)
3. Check `references/patterns.md` for a matching pattern
4. Write hook config in `hooks/hooks.json` (use correct format -- plugin wrapper)
5. For command hooks: write script, lint with `scripts/hook-linter.sh`, test with `scripts/test-hook.sh`
6. Validate config: `scripts/validate-hook-schema.sh hooks/hooks.json`
7. Test in Claude Code: `claude --debug`
8. Iterate -- remember to restart session after each hooks.json change

## Rationalization Table

| Concept | Why It Earns Space |
|---------|--------------------|
| Two JSON configuration formats | Most common hook bug -- plugin wrapper vs settings direct structure |
| Hook lifecycle (load-once, parallel execution) | Non-obvious runtime behavior that causes debugging confusion |
| Exit code semantics (0 vs 2 vs other) | Determines whether hooks block operations or just log |
| Event selection guide with output controls | Each event has unique output capabilities that affect what hooks can do |
| Matcher regex patterns for MCP tools | MCP tool naming convention is not documented elsewhere |
| File Index with load conditions | 10 companion files need clear routing to avoid information overload |

## Red Flags

1. **Editing hooks mid-session and expecting changes** -- hooks only load at session start
2. **Using settings JSON format in plugin hooks.json** -- missing the `"hooks"` wrapper key
3. **Assuming hook execution order** -- all matching hooks run in parallel, non-deterministic
4. **Hardcoding absolute paths** -- use `${CLAUDE_PLUGIN_ROOT}` for portability
5. **Using prompt hooks for SessionStart/SessionEnd/PreCompact/Notification** -- these events only support command hooks
6. **Forgetting `set -euo pipefail`** in bash hook scripts -- silent failures on errors
7. **Writing to stdout when intending to block** -- blocking output must go to stderr with exit 2
8. **Not quoting bash variables** -- injection vulnerability (`"$var"` not `$var`)

## NEVER

1. NEVER assume hooks execute in a specific order -- they run in parallel
2. NEVER modify hooks.json and expect current session to pick up changes
3. NEVER hardcode file paths in hooks.json commands -- always use ${CLAUDE_PLUGIN_ROOT}
4. NEVER use prompt hooks for SessionStart, SessionEnd, PreCompact, or Notification events
5. NEVER output blocking errors to stdout -- use stderr (>&2) with exit code 2
