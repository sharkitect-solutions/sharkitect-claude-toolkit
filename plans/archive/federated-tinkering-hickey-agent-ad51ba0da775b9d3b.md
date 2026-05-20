# Task 3: Update HQ CLAUDE.md - Plan

## Objective
Update the CLAUDE.md file at `C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/CLAUDE.md` with 5 precise edits to replace "Task Scheduler" references with "Sentinel (workspace 4)".

## Target File
- Path: C:\Users\Sharkitect Digital\Documents\Claude Code Workspaces\1.- SHARKITECT DIGITAL WORKFORCE HQ\CLAUDE.md
- Current state: 238 lines, confirmed read in previous context window
- Status: Awaiting edits (plan mode was active, now ready to execute)

## Required Edits

### Edit 1: Line 24 (Architecture Overview section)
- Current: `  Task Scheduler: Python scripts on schedule (briefs, syncs, audits, monitoring)`
- Replace with: `  Sentinel: 8 tools on schedule (briefs, syncs, audits, monitoring) — workspace 4`

### Edit 2: Line 35 (Decision logic section)
- Current: `The one question that decides where work lives:** "Does this need to run when no Claude Code session is open?" YES → n8n or Task Scheduler. NO → Claude Code.`
- Replace with: `The one question that decides where work lives:** "Does this need to run when no Claude Code session is open?" YES → n8n or Sentinel. NO → Claude Code.`

### Edit 3: Line 218 (File Structure section description)
- Current: `| `tools/audit/` | Briefing pipeline, audit checks, report formatter |`
- Replace with: `| `tools/audit/` | [ARCHIVED — see Sentinel workspace 4 for current audit tools] |`

### Edit 4: Line 229 (Environment Reference section - Task Scheduler line)
- Current: `- **Task Scheduler** — 6 tasks: morning brief (5AM), midday pulse (12:15PM), evening brief (9PM), midnight audit (12AM), weekly report (Sun 9:30PM), Supabase sync (hourly).`
- Replace with: `- **Sentinel (workspace 4)** — 8 tools: morning brief, midday pulse, evening brief, midnight audit, weekly report, Supabase sync, dream cycle, work-request monitor. See `4.- Sentinel/docs/` for specs.`

### Edit 5: Line 230 (Environment Reference section - MCP servers line)
- Current: `- **MCP servers**: Supabase, Airtable, n8n, Gmail, Google Calendar, HubSpot, Jotform, Notion, Slack, Firecrawl, Memory, Canva, Clay, GitHub, Figma, Context7.`
- Replace with: `- **MCP servers**: Supabase, Airtable, n8n, Gmail, Google Calendar, HubSpot, Jotform, Notion, Slack, Firecrawl, Memory, Canva, Clay, GitHub, Figma, Context7, Telegram.`

## Execution Steps

1. ✓ File already read in previous context
2. Apply Edit 1 (line 24) using Edit tool
3. Apply Edit 2 (line 35) using Edit tool
4. Apply Edit 3 (line 218) using Edit tool
5. Apply Edit 4 (line 229) using Edit tool
6. Apply Edit 5 (line 230) using Edit tool
7. Create git commit with message: `docs: update CLAUDE.md to reference Sentinel instead of old audit system`
8. Verify: `git status` shows clean state

## Success Criteria
- All 5 edits applied successfully
- File saves without errors
- Git commit created with correct message
- No other files modified

## Blockers/Notes
- Plan mode was blocking execution in previous window
- File has been read and is ready for editing
- All edits are precise replacements (no hand-editing needed)
- Commit message is provided and final
