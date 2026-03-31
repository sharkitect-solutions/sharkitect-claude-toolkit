# Changelog - aios-core

## [1.0.0] - 2026-03-18

### Added
- SessionStart hook: workspace detection from cwd, context injection, post-compact recovery detection
- SessionEnd hook: skill/agent modification detection, uncommitted change warnings, sync reminders
- PreCompact hook: context preservation to .tmp/compact-context.md (git status, recent commits, session state)
- 3 Python scripts: session-start.py, session-end-check.py, pre-compact-preserve.py
- Full Windows compatibility (Python stdlib only, no bash dependencies)
