# auto-sync

> Auto-Sync - Automatic detection of skill/agent changes with sync prompting

## Overview

Tracks modifications to skill and agent files in real-time and prevents accidental session exit without syncing. When you write or edit files in `~/.claude/skills/` or `~/.claude/agents/`, the plugin silently records the changes. When Claude is about to stop, the plugin blocks the exit and reminds you to run sync first.

Complements aios-core (which does broader session lifecycle checks) by focusing specifically on real-time file change tracking with a blocking stop mechanism.

## Components

- **Hooks**: 2 command hooks across 2 events (PostToolUse, Stop)
- **Scripts**: 2 Python scripts (stdlib only, Windows-compatible)

## Hook Events

| Event | Type | Matcher | Purpose |
|-------|------|---------|---------|
| PostToolUse | command | `Write\|Edit` | Track writes/edits to skill SKILL.md and agent .md files |
| Stop | command | (all) | Block session exit if unsynced changes exist, prompt sync |

## How It Works

### PostToolUse Flow (track-changes.py)
1. Fires after every Write or Edit operation
2. Checks if the file path contains `/.claude/skills/` or `/.claude/agents/`
3. If not a skill/agent file, exits silently (0ms overhead)
4. If yes, appends entry to `.tmp/modified-this-session.json` (deduplicates by path)

### Stop Flow (sync-reminder.py)
1. Fires when Claude is about to stop responding
2. Reads `.tmp/modified-this-session.json`
3. If no entries (or file missing), exits silently (allows stop)
4. If entries exist:
   - Outputs blocking JSON: `{"decision": "block", "reason": "..."}`
   - Lists modified skills and agents by name
   - Suggests sync commands: `python tools/sync-skills.py --sync --push`
   - Clears the tracking file (so next stop attempt proceeds)
5. Claude sees the reminder and can help run sync
6. User can sync or say "skip sync" to exit without syncing

### Integration with aios-core
- auto-sync creates `.tmp/modified-this-session.json`
- aios-core's PreCompact hook reads it to preserve modified file list during compaction
- aios-core's SessionEnd hook independently checks git status as a second safety net

## Tracking File Format

`.tmp/modified-this-session.json`:
```json
[
  {
    "path": "C:/Users/.../.claude/skills/my-skill/SKILL.md",
    "type": "skill",
    "tool": "Write",
    "time": "2026-03-18T01:00:00Z"
  }
]
```

## Installation

```bash
# From local path:
/plugin install --path /path/to/auto-sync
```

## Configuration

No configuration required. Both hooks activate automatically on session start.

## Requirements

- Python 3.8+ on PATH (as `python`)
- No external Python dependencies (stdlib only)

## Compatibility

- Windows 10/11 (primary target)
- macOS / Linux (compatible)
- All paths use `${CLAUDE_PLUGIN_ROOT}` for portability

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
