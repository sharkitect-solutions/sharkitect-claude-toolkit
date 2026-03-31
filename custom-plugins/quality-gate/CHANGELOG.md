# Changelog - quality-gate

## [1.0.0] - 2026-03-18

### Added
- PostToolUse command hook: fires on Write|Edit to validate skill and agent files
- Skill validation: frontmatter, name, description triggers/exclusions, line count, File Index, Scope Boundary
- Agent validation: frontmatter, name, description examples/exclusions, line count, anti-patterns, output template
- Manual test mode: `python quality-gate.py --file <path>`
- Full Windows compatibility (Python stdlib only, no bash dependencies)
- Non-blocking design: always exits 0, warnings go to stdout for context injection
