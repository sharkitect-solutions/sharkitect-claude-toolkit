# aios-core

> AIOS Core - Session lifecycle management for the Sharkitect toolkit

## Overview

Foundation plugin for the Sharkitect AIOS toolkit. Manages session lifecycle events that no other plugin covers: workspace detection at session start, sync reminders at session end, and context preservation before compaction.

Complements Superpowers (which handles workflow activation) by adding operational automation for the toolkit maintenance cycle.

## Components

- **Hooks**: 3 command hooks across 3 lifecycle events
- **Scripts**: 3 Python scripts (stdlib only, Windows-compatible)

## Hook Events

| Event | Script | Purpose |
|-------|--------|---------|
| SessionStart | `session-start.py` | Detect workspace from cwd, output context reminders, check for post-compact recovery |
| SessionEnd | `session-end-check.py` | Check for modified skill/agent files, uncommitted changes, output sync reminders |
| PreCompact | `pre-compact-preserve.py` | Preserve git status, recent commits, modified files to `.tmp/compact-context.md` |

## How It Works

### SessionStart Flow
1. Reads current working directory
2. Identifies workspace (Skill Management Hub, WORKFORCE HQ, client project, or generic)
3. Outputs workspace-specific context reminders (tools, workflows, MEMORY.md pointer)
4. Checks for `.tmp/compact-context.md` from a previous compaction and alerts if recovery data is available

### SessionEnd Flow
1. Checks `~/.claude/skills/` and `~/.claude/agents/` for uncommitted git changes
2. Checks current workspace for uncommitted changes
3. Checks for auto-sync tracking file entries
4. Outputs non-blocking warnings to stderr if changes detected

### PreCompact Flow
1. Captures git status (uncommitted changes, diff stats)
2. Captures recent commit history (last 5)
3. Reads session tracking state from `.tmp/modified-this-session.json` if present
4. Writes everything to `.tmp/compact-context.md` for post-compact recovery
5. SessionStart hook detects this file on next cycle and alerts the model

## Installation

```bash
# From local path:
/plugin install --path /path/to/aios-core
```

## Configuration

No configuration required. All hooks activate automatically on their respective lifecycle events.

## Requirements

- Python 3.8+ on PATH (as `python`)
- Git on PATH (for change detection)
- No external Python dependencies (stdlib only)

## Compatibility

- Windows 10/11 (primary target)
- macOS / Linux (compatible)
- All paths use `${CLAUDE_PLUGIN_ROOT}` for portability

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
