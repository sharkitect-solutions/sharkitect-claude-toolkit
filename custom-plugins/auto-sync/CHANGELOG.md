# Changelog - auto-sync

## [1.0.0] - 2026-03-18

### Added
- PostToolUse command hook: tracks Write/Edit to skill SKILL.md and agent .md files
- Stop command hook: blocks session exit with sync reminder if unsynced changes exist
- Session-scoped tracking file: `.tmp/modified-this-session.json` with deduplication
- Blocking stop mechanism with auto-clear (first stop blocks, second goes through)
- Integration with aios-core PreCompact hook for context preservation
- Full Windows compatibility (Python stdlib only, no bash dependencies)
