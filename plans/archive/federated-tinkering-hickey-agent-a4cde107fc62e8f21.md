# Plan: Update HQ README.md to Reference Sentinel

## Objective
Update the Workforce HQ README.md file with two specific edits to reference the Sentinel workspace for automation instead of Windows Task Scheduler batch files.

## Edits Required

### Edit 1: Delete `run_audit.py` Row from Tools Table
- **File**: `C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/README.md`
- **Location**: Line 43 in the Tools table
- **Content to remove**: `| `run_audit.py` | Run Supabase sync and governance audits |`
- **Context**: This tool is being deprecated in favor of Sentinel workspace automation

### Edit 2: Replace "Scheduled Automation" Section
- **File**: Same as Edit 1
- **Location**: Lines 52-63 (entire section)
- **Old section**: The "Scheduled Automation" section describing Windows Task Scheduler batch files (audit_morning.bat, audit_midday.bat, etc.)
- **New section** (replacement text):
```markdown
## Scheduled Automation

Monitoring, briefs, and audits are handled by [Sentinel](../4.- Sentinel/) (workspace 4). HQ sessions generate intelligent CEO briefs (morning/midday/evening) via ralph-loop. See architecture spec for full design.
```

## Execution Steps

1. **Edit 1**: Use Edit tool to delete the `run_audit.py` row from the Tools table
   - Target: Line 43
   - Match the exact row text to ensure precision

2. **Edit 2**: Use Edit tool to replace the "Scheduled Automation" section
   - Replace lines 52-63 with the new text referencing Sentinel
   - Preserve surrounding sections (Tools table before, New Machine Setup section after)

3. **Git Commit**: After both edits complete, run:
   ```bash
   git commit -m "docs: update README.md to reference Sentinel for automation"
   ```

## Constraints
- **Do NOT change anything else** in the README.md file
- Only these 2 edits are permitted
- The file structure and all other content must remain exactly as is

## File Verification
- File exists and was successfully read in previous session
- Both sections (Tools table with `run_audit.py` row, and Scheduled Automation section) were verified present
- File is ready for editing

## Status
Ready to execute once plan mode is deactivated.
