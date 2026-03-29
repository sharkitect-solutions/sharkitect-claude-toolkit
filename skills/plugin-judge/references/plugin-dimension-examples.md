# Plugin Dimension Examples

Concrete high-score and low-score examples for each dimension. Use to calibrate evaluations and verify scoring consistency.

---

## D1: Package Structure

### High Score (13/15) — hookify

```
hookify/
  .claude-plugin/plugin.json    # Valid manifest with name, version, description
  hooks/hooks.json              # 4 events, wrapper format, valid JSON
  hooks/pretooluse.py           # Script for PreToolUse
  hooks/posttooluse.py          # Script for PostToolUse
  hooks/stop.py                 # Script for Stop
  hooks/userpromptsubmit.py     # Script for UserPromptSubmit
  skills/hookify/SKILL.md       # Embedded skill
  agents/hookify-agent.md       # Embedded agent
  README.md                     # Documentation present
  (no CHANGELOG -- prevents 15)
```

**Why 13**: Complete structure with manifest, hooks, skills, agents, README. Missing only CHANGELOG to reach 15.

### Low Score (2/15) — pyright-lsp

```
pyright-lsp/
  README.md                     # Only file present
```

**Why 2**: Single file. No manifest (no plugin.json or package.json). No components of any kind. The README exists, preventing a score of 0, but there's no plugin structure to evaluate.

### Score 0 — Empty directory

Plugin install path exists but contains zero files, or path doesn't exist at all. This happens with orphaned registry entries pointing to deleted directories.

---

## D2: Hook Quality

### High Score (12/15) — security-guidance

```json
{
  "description": "Security reminder hook...",
  "hooks": {
    "PreToolUse": [{
      "hooks": [{ "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/security_reminder_hook.py" }],
      "matcher": "Edit|Write|MultiEdit"
    }]
  }
}
```

**Why 12**: Targeted matcher (`Edit|Write|MultiEdit` -- only fires on write operations). Correct event (PreToolUse to check BEFORE changes). Command type appropriate for deterministic security check. Uses `${CLAUDE_PLUGIN_ROOT}` for portability. Single-purpose, focused hook.

### Medium Score (7/15) — prettier-markdown-hook

```json
{
  "hooks": [{
    "event": "Stop",
    "matcher": ".*",
    "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format-markdown.sh",
    "timeout": 30000
  }]
}
```

**Why 7**: Correct event (Stop -- format after work is done). `.*` matcher is appropriate for Stop events (semantically correct). Has timeout (good). BUT: uses Format B (list) instead of standard wrapper format, 30-second timeout is generous for a formatting operation, and no error handling specification (no `continueOnError` in standard format).

### Low Score (0/15) — components-only pack (no hooks)

retellai-pack, customerio-pack, etc. have zero hooks. For these archetype-based default is 5/15 (hooks aren't their purpose, don't penalize).

**Exception**: If a plugin's stated purpose implies it should have hooks (e.g., a "workflow automation" plugin with no hooks), score 2/15 -- the absence IS a deficiency.

---

## D3: Hook Architecture

### High Score (12/15) — hookify

Uses 4 events:
- **PreToolUse** (command) -- validate before tool runs
- **PostToolUse** (command) -- react to tool output
- **Stop** (command) -- handle completion
- **UserPromptSubmit** (command) -- process user input

**Why 12**: Each event serves a distinct purpose. All use command hooks (correct for deterministic user-configured behavior). No redundancy -- each hook handles a different phase of the interaction cycle. Clean separation of concerns. Missing UserPromptSubmit prompt hook for context-aware processing prevents 15.

### Architecture Violation Example — Hypothetical Bad Plugin

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": ".*",
      "hooks": [{ "type": "prompt", "prompt": "Initialize the plugin state..." }]
    }]
  }
}
```

**Why this fails D3**: SessionStart is command-only. A prompt hook here silently fails -- the initialization never runs. The developer assumed SessionStart supports prompt hooks. Score: 3/15 (fundamental architectural mistake).

### Sequential Assumption Violation — Hypothetical

Plugin has two hooks on the same event expecting Hook A to run before Hook B:
```json
{
  "PreToolUse": [
    { "matcher": "Write", "hooks": [{ "type": "command", "command": "hook-a.sh" }] },
    { "matcher": "Write", "hooks": [{ "type": "command", "command": "hook-b.sh" }] }
  ]
}
```

**Why this is risky**: Hooks run in PARALLEL. Hook B may execute before Hook A. If Hook B depends on Hook A's output (e.g., a file Hook A creates), it will intermittently fail. Score: 5/15 max if sequential dependency exists.

---

## D4: Security & Portability

### High Score (13/15) — Plugin using ${CLAUDE_PLUGIN_ROOT}

```json
"command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/security_reminder_hook.py"
```

**Why high**: Uses the portable variable. Works on any machine regardless of install location. No hardcoded paths, no credential exposure.

### Critical Failure (2/15) — Hypothetical Hardcoded Path

```json
"command": "/Users/developer/Projects/my-plugin/hooks/check.sh"
```

**Why 2**: Hardcoded to developer's machine. Will fail on every other machine. If published to marketplace, every user gets "file not found". This is the #1 portability failure in plugin development.

### Shell Injection Risk (4/15) — Hypothetical Unsafe Script

```bash
#!/bin/bash
TOOL_NAME=$1
eval "python3 check_${TOOL_NAME}.py"  # DANGEROUS: unsanitized input in eval
```

**Why 4**: Tool name could contain shell metacharacters. `eval` with user-controlled input is a classic injection vector. Even in a trusted environment, this is bad practice that could cause unexpected behavior with tools named `foo;rm -rf /`.

---

## D5: Component Quality

### High Score (12/15) — superpowers

14 embedded skills covering brainstorming, TDD, debugging, code review, and more. Skills have proper frontmatter, descriptions with trigger conditions, and substantive content. The SessionStart hook auto-activates workflows.

**Why 12**: Skills individually have solid content. Descriptions are functional. The auto-activation through hooks elevates the component value. Doesn't reach 14 because some skills lack companion files for deeper content.

### Medium Score (7/15) — retellai-pack

30 embedded skills covering Retell AI topics from hello-world to production checklists. Each skill has frontmatter and ~50-100 lines of content.

**Why 7**: Large quantity, decent organization, domain-specific content. BUT: spot-checking reveals many skills explain basics Claude already knows (hello-world, install-auth patterns are generic). Knowledge delta is moderate, not high. Skills lack companion files. Descriptions are adequate but not precision-tuned.

### Low Score (3/15) — Hypothetical Stub Pack

```markdown
---
name: feature-x
description: "Feature X skill"
---
# Feature X
TODO: Add content
```

**Why 3**: Stub skills with no content. Description is useless for triggering. No knowledge delta. No procedures. The plugin is a skeleton pretending to be a toolkit.

---

## D6: Business Value

### High Score (14/15) — superpowers (for any user)

Automates brainstorming, TDD, debugging, and code review through SessionStart hook. Fires automatically without user intervention. Saves significant time per session by auto-triggering appropriate workflows.

**Why 14**: Universal value regardless of domain. Automates workflows every developer needs. The SessionStart hook means value is delivered passively -- you don't even have to remember to use it.

### Context-Dependent Score — retellai-pack

- **For VDR builder (Sharkitect Digital)**: 12/15. Retell AI is the VoiceDesk platform. These 30 skills directly support service delivery.
- **For data engineer**: 2/15. Retell AI is completely irrelevant to data pipelines.

**Why context matters**: Business value is always relative to the user's actual needs. A technically perfect plugin for a domain you don't work in has near-zero value.

### Zero Value (0/15) — Empty Shell

sow-generator, zapier-zap-builder, etc. have zero components. They provide no functionality at all. Theoretical future value doesn't count -- evaluate what EXISTS, not what might be built later.

---

## D7: Documentation

### Adequate Score (8/15) — Typical plugin with README

```markdown
# Plugin Name
Description of what the plugin does.

## Installation
/plugin install name@marketplace

## Usage
Brief usage notes.
```

**Why 8**: Has purpose, install instructions, and basic usage. Missing: hook event descriptions, configuration options, examples, CHANGELOG.

### High Score (12/15) — Hypothetical Well-Documented Plugin

```markdown
# Plugin Name
> Automated security checking for file write operations.

## Overview
Fires a PreToolUse hook on Edit/Write/MultiEdit to check for...

## Installation
/plugin install security-guidance@claude-plugins-official

## Hook Events
| Event | Matcher | What It Does |
|---|---|---|
| PreToolUse | Edit\|Write\|MultiEdit | Checks for security issues... |

## Configuration
Set `SECURITY_LEVEL=strict` in your project's .env...

## Examples
### Example 1: Catching SQL injection
...

## Changelog
### 1.0.0 - 2026-03-01
- Initial release
```

**Why 12**: Has every documentation element: purpose, install, hook descriptions, configuration, examples, changelog. Only missing troubleshooting section for 14+.

---

## D8: Reliability & Testing

### Good Reliability (10/15) — hookify scripts

```python
#!/usr/bin/env python3
import sys, json, os

def main():
    try:
        # Read hook configuration
        config_path = os.path.join(os.environ.get('CLAUDE_PLUGIN_ROOT', '.'), 'config.json')
        if not os.path.exists(config_path):
            return 0  # Graceful: no config = no action, don't block

        config = json.loads(open(config_path).read())
        # ... process hook logic ...
        return 0
    except Exception:
        return 0  # Graceful: errors don't block the session

sys.exit(main())
```

**Why 10**: Checks file existence before reading. Uses environment variable with fallback. Catches all exceptions. Returns 0 (success) on any error -- never blocks the session. Could improve: specific exception handling, logging, timeout protection.

### Poor Reliability (3/15) — Hypothetical Fragile Hook

```bash
#!/bin/bash
cat $HOOK_DATA | jq '.tool' | xargs python3 check.py
```

**Why 3**: No file existence check. No error handling. Unquoted variables. `jq` might not be installed. Pipeline will crash on empty input. `xargs` with untrusted input is risky. Any single failure crashes the entire hook chain.

---

## Cross-Dimension Relationships

Some dimension scores are correlated. Watch for these patterns:

| If D__ is low | Check D__ too | Why |
|---------------|---------------|-----|
| D1 (structure) low | D2, D3 likely low | Bad structure usually means bad hooks |
| D2 (hook quality) high | D4 should be checked | Good hooks can still have security issues |
| D5 (components) high | D6 should match | Good components should mean good business value |
| D7 (docs) low | D8 often low too | Poor documentation correlates with poor testing |
| D6 (value) = 0 | Overall grade should be F | A zero-value plugin shouldn't pass regardless of technical quality |
