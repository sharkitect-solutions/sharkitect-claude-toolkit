# Plan: Simplify Cross-Workspace Communication Channels

## Status: NOT STARTED — Planning deferred to next session

## Context

Currently there are two separate channels for cross-workspace communication:
1. `.gap-reports/inbox/` — gap detection writes here (resource-auditor, gap-reporter.py)
2. `.routed-tasks/inbox/` — workspaces route tasks to each other here

This creates confusion because:
- The same issue can arrive as BOTH a gap report AND a routed task (voice capture pipeline arrived as both)
- AI has to decide which channel to use when sending work
- Two inboxes means two processing flows, two sets of rules, two things to check
- More options = more room for AI to make mistakes

## User's Direction

Simplify to ONE channel: routed tasks. Everything flows through `.routed-tasks/`. Gap detection machinery (resource-auditor, gap-reporter.py) stays but writes routed tasks instead of gap reports. One inbox, one format, one processing flow.

Key routing logic stays the same:
- Universal items (skills, hooks, agents, protocols) → Skill Hub handles
- Workspace-specific items → route to the owning workspace via outbox

## What Needs Planning (Next Session)

1. **Gap detection output change**: gap-reporter.py writes to `.routed-tasks/inbox/` instead of `.gap-reports/inbox/`. What fields carry over? What's the unified JSON schema?
2. **Gap-watcher.py**: Does it still exist? Or does the routed task processing flow absorb its role?
3. **Startup guard**: Currently checks both inboxes separately. Simplify to one check.
4. **CronCreate prompts**: Remove gap-specific steps, unify to routed task processing only.
5. **Deferred folder**: Clarify purpose — only for re-routing to the correct workspace. NOT for "do later."
6. **Migration**: What happens to existing gap reports in processed/ and deferred/? Archive or leave as historical?
7. **Resource-auditor hook**: Currently writes gap reports. Update to write routed tasks.
8. **All 3 workspace CLAUDE.md files**: Update inbox references.
9. **universal-protocols.md**: Merge gap detection protocol into routed tasks protocol.
10. **Lifecycle reviews**: Are these a third channel that should also consolidate? Or do they stay separate?

## Files That Will Be Affected

- `~/.claude/scripts/gap-reporter.py` — output format change
- `~/.claude/hooks/session-startup-guard.py` — inbox check simplification
- `~/.claude/rules/universal-protocols.md` — protocol merge
- `tools/gap-watcher.py` — possibly retire or merge
- `workflows/gap-processing.md` — merge into routed task processing
- `workflows/cron-schedule.md` (all 3 workspaces) — prompt updates
- `CLAUDE.md` (all 3 workspaces) — inbox references
- Resource-auditor skill — gap report output format

## Decision: NOT ready to execute. Needs full brainstorming session.
