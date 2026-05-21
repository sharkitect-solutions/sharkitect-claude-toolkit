# quality-gate

> Quality Gate - Automated structural validation for skill and agent files on Write/Edit

## Overview

Lightweight structural linter for Claude Code skill and agent files. Fires automatically after every Write or Edit to `~/.claude/skills/` or `~/.claude/agents/`, validating that files follow the required structural patterns. Catches issues in real-time instead of waiting for a full skill-judge or agent-judge evaluation.

This is a **linter, not a reviewer** -- it checks structure (frontmatter, description triggers, line count, File Index), not content quality. Content quality requires the full skill-judge or agent-judge meta-skills.

## Components

- **Hooks**: 1 command hook on PostToolUse (Write|Edit)
- **Scripts**: 1 Python script (stdlib only, Windows-compatible)

## Hook Events

| Event | Type | Matcher | Purpose |
|-------|------|---------|---------|
| PostToolUse | command | `Write\|Edit` | Validate skill SKILL.md and agent .md files after write/edit |

## What It Validates

### Skill Files (SKILL.md)

| Check | What It Looks For |
|-------|------------------|
| Frontmatter | `---` delimited YAML frontmatter present |
| Name field | `name:` field in frontmatter |
| Description field | `description:` field in frontmatter |
| Trigger conditions | Description contains "Use when...", "Use for..." |
| Exclusions | Description contains "Do NOT use for: ..." |
| Line count | Not a stub (<20 lines) or oversized (>500 lines) |
| File Index | Present for skills >100 lines |
| Scope Boundary | Present for skills >50 lines |

### Agent Files (.md)

| Check | What It Looks For |
|-------|------------------|
| Frontmatter | `---` delimited YAML frontmatter present |
| Name field | `name:` field in frontmatter |
| Description field | `description:` field in frontmatter |
| Examples | `<example>` blocks in description |
| Exclusions | Description contains "Do NOT use for: ..." |
| Line count | Not a stub (<30 lines) |
| Anti-patterns | NEVER/anti-pattern section in body |
| Output template | Output template/format section in body |

## How It Works

1. PostToolUse hook fires after every Write or Edit operation
2. Script reads the file path from stdin (JSON hook input)
3. If the path is NOT a skill SKILL.md or agent .md file, exits silently (0ms overhead)
4. If it IS a skill/agent file, reads the file from disk and runs structural checks
5. Outputs warnings to stdout (injected into conversation context) if issues found
6. Always exits 0 (non-blocking -- file already written, we just warn)

## Manual Testing

```bash
# Test a specific skill file
python scripts/quality-gate.py --file ~/.claude/skills/my-skill/SKILL.md

# Test a specific agent file
python scripts/quality-gate.py --file ~/.claude/agents/my-agent.md
```

## Installation

```bash
# From local path:
/plugin install --path /path/to/quality-gate
```

## Configuration

No configuration required. The hook activates automatically on session start for all Write and Edit operations.

## Requirements

- Python 3.8+ on PATH (as `python`)
- No external Python dependencies (stdlib only)

## Compatibility

- Windows 10/11 (primary target)
- macOS / Linux (compatible)
- All paths use `${CLAUDE_PLUGIN_ROOT}` for portability

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
