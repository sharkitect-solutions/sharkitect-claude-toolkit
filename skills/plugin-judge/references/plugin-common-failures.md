# Plugin Common Failure Patterns

7 named failure patterns identified from auditing 44+ plugins across 5 marketplaces. Each pattern describes the structural deficiency, how to detect it, and what it costs.

---

## Pattern 1: The Empty Shell

**What it is**: Plugin is installed and registered but contains zero functional components -- no hooks, no skills, no agents, no MCPs. Just a manifest and maybe a README.

**Detection**: `audit-plugins.py` reports `plugin_type: empty`. Total files <= 2. Zero skills, zero agents, zero hooks.

**Why it happens**: Plugin was scaffolded but never implemented. Or implementation files were deleted during an update. Or the plugin's functionality was moved elsewhere but the registry entry remains.

**What it costs**: Disk space. Registry bloat. Confusion during audits ("I have 44 plugins" when only 38 do anything). Orphaned cache versions accumulate.

**Score impact**: D1 auto-0 (no structure to evaluate), D2 auto-0, D3 auto-0, D5 auto-0, D6 auto-0, D8 auto-0. Maximum possible total: ~15-20/120 (only D4 and D7 can score if README exists).

**Examples found**: sow-generator, discovery-questionnaire, roi-calculator, zapier-zap-builder, typescript-lsp, pyright-lsp (6 of 44 = 14% empty rate).

---

## Pattern 2: The Hookless Pack

**What it is**: Plugin contains only skills or only agents with zero hooks. Functions identically to standalone skills/agents installed directly. The "plugin" wrapper adds no automation value.

**Detection**: `has_hooks_json: false` AND (`skill_count > 0` OR `agent_count > 0`). Plugin type is `skills_only` or `agents_only`.

**Why it happens**: Many plugin marketplaces package skills/agents as plugins for distribution convenience. The plugin format is used as a delivery mechanism, not as an automation platform.

**What it costs**: No automation overhead (hooks don't fire). But the plugin wrapper adds indirection -- skills are installed at the plugin cache path rather than `~/.claude/skills/`. This can cause version confusion and makes manual inspection harder.

**Score impact**: D2 caps at 5/15 (no hooks to evaluate), D3 caps at 5/15 (no hook architecture). These plugins compete on D5 (component quality) and D6 (business value).

**Not inherently bad**: A components-only pack with excellent skills (retellai-pack: 30 skills) can still score well if the skills themselves are high quality. The failure is when the plugin format adds no value AND the components are weak.

---

## Pattern 3: The Overbroad Matcher

**What it is**: Hook uses `.*` wildcard on PreToolUse or PostToolUse, causing it to fire on EVERY tool invocation rather than the specific tools it was designed for.

**Detection**: In hooks.json, look for `"matcher": ".*"` on PreToolUse or PostToolUse events. (Note: `.*` is APPROPRIATE for Stop, SessionStart, UserPromptSubmit where matching all events is semantically correct.)

**Why it happens**: Developer didn't realize matchers are regex patterns that should target specific tools. Or used `.*` during development and forgot to narrow it.

**What it costs**: Performance -- hook fires on every Read, Write, Edit, Bash, Glob, Grep call. For command hooks, this adds latency to every tool use. For prompt hooks, this injects prompt text into every tool decision. Can cause unexpected behavioral changes across unrelated workflows.

**Score impact**: D2 -3 to -5 (imprecise matcher), D3 -2 (wrong scope), D8 -2 (false positive triggers). A single overbroad matcher can drop a plugin from B to C+.

**Fix**: Replace `.*` with specific tool names: `"matcher": "Edit|Write"` or `"matcher": "Bash"`.

---

## Pattern 4: The Hardcoded Path

**What it is**: Hook commands or scripts contain absolute user paths (`/Users/john/`, `C:\Users\john\`) instead of using `${CLAUDE_PLUGIN_ROOT}` for portability.

**Detection**: Search all hook commands and scripts for path patterns containing `/Users/`, `/home/`, `C:\Users\`, or `C:/Users/`. The audit tool flags this as `HARDCODED_PATH`.

**Why it happens**: Developer tested locally, used absolute paths, forgot to switch to the portable variable. Or copied code from a non-plugin context where absolute paths were fine.

**What it costs**: Plugin breaks on ANY other machine. If shared via marketplace, every user gets "file not found" errors. The plugin is permanently locked to the author's machine.

**Score impact**: D4 caps at 5/15 (critical portability failure). If the plugin has multiple hardcoded paths, D4 drops to 0-3.

**Fix**: Replace all absolute paths with `${CLAUDE_PLUGIN_ROOT}/relative/path`. This variable resolves to the plugin's actual install location at runtime.

---

## Pattern 5: The Format Mismatch

**What it is**: Plugin's hooks.json uses an incorrect or inconsistent format. Two valid formats exist and plugins sometimes mix them or use neither:

**Format A** (standard plugin wrapper):
```json
{
  "description": "...",
  "hooks": {
    "EventName": [{ "matcher": "...", "hooks": [{ "type": "command", "command": "..." }] }]
  }
}
```

**Format B** (list format):
```json
{
  "hooks": [
    { "event": "Stop", "matcher": ".*", "command": "..." }
  ]
}
```

**Detection**: The audit tool reports `has_wrapper_key: false` or `HOOKS_FLAT_FORMAT`. Invalid JSON is caught as `INVALID_HOOKS_JSON`.

**Why it happens**: Claude Code has evolved its hook format. Older plugins may use Format B. Some plugins were generated from templates that used a different format than what the runtime expects.

**What it costs**: If the runtime doesn't recognize the format, hooks silently don't fire. The plugin appears installed but does nothing. Debugging this is extremely frustrating because there are no error messages.

**Score impact**: D1 -3 (structural issue), D2 -5 (hooks may not work), D8 -3 (reliability failure).

---

## Pattern 6: The Command-Only Violation

**What it is**: Plugin uses a prompt hook on an event that only supports command hooks (SessionStart, SessionEnd, PreCompact, Notification).

**Detection**: In hooks.json, check for `"type": "prompt"` under SessionStart, SessionEnd, PreCompact, or Notification events.

**Why it happens**: Developer didn't know about the command-only restriction. Or assumed all events support both hook types.

**What it costs**: The hook silently fails or causes undefined behavior. On SessionStart this means the plugin's initialization logic never runs. On SessionEnd it means cleanup logic never executes.

**Score impact**: D3 -5 (architectural violation), D8 -3 (reliability failure). This is a hard rule violation, not a style preference.

---

## Pattern 7: The Orphan Accumulator

**What it is**: Plugin has many orphaned cached versions (marked with `.orphaned_at`) from previous installs/updates. While not a functional issue, it indicates version management problems and wastes disk space.

**Detection**: `orphaned_versions > 3` in the audit data. The audit tool counts `.orphaned_at` markers across all cached versions.

**Why it happens**: Plugin is frequently updated (new commits pushed), and old versions aren't cleaned up. Or the plugin was installed/uninstalled multiple times.

**What it costs**: Disk space (can be significant for large plugins like superpowers with 126 files per version). Confusion when manually inspecting the cache. No functional impact.

**Score impact**: D1 -1 (minor structural issue). Not a significant deduction unless the orphan count is extreme (>10).

---

## Quick Reference Checklist

Before scoring, verify these 7 patterns are not present:

| # | Pattern | Quick Check | Severity |
|---|---------|-------------|----------|
| 1 | Empty Shell | `plugin_type == "empty"`? | CRITICAL |
| 2 | Hookless Pack | Has skills but no hooks? (Score D2/D3 appropriately) | INFORMATIONAL |
| 3 | Overbroad Matcher | `"matcher": ".*"` on PreToolUse/PostToolUse? | HIGH |
| 4 | Hardcoded Path | `/Users/` or `C:\Users\` in commands/scripts? | CRITICAL |
| 5 | Format Mismatch | hooks.json valid and in expected format? | HIGH |
| 6 | Command-Only Violation | Prompt hooks on SessionStart/End/PreCompact/Notification? | HIGH |
| 7 | Orphan Accumulator | `orphaned_versions > 3`? | LOW |
