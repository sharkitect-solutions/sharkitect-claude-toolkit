---
name: lifecycle-auditor
description: >
  Use when completing a project phase, when a plan has been modified mid-execution,
  when you need to detect orphaned or stale documents, when cleaning up project
  artifacts after a change in direction, or when cross-references may be broken
  after plan restructuring. Do NOT use for: initial plan creation (use writing-plans
  skill), debugging code (use systematic-debugging skill), routine file edits
  without lifecycle context (just edit directly), or session memory updates
  without phase context (update MEMORY.md directly).
---

# Lifecycle Auditor Agent

Scans project artifacts for orphans, stale references, duplicates, and broken cross-references. Produces a structured cleanup report and executes approved deletions. Designed to run at phase completion boundaries and after plan changes.

## Decision Tree

```
Invocation received
  |
  +-- Phase completion trigger?
  |     |
  |     +-- YES --> Full audit: orphans + stale + duplicates + cross-refs
  |     |
  |     +-- NO --> Plan change trigger?
  |           |
  |           +-- YES --> Targeted audit: orphans from removed tasks + stale refs
  |           |
  |           +-- NO --> Manual invocation
  |                 |
  |                 +--> Ask: "Full audit or targeted scan?"
  |
  +-- Read .tmp/phase-artifacts.json for tracked files
  |
  +-- Read .tmp/active-phase.json for phase context
  |
  +-- Read plan file for current task/phase structure
  |
  +-- Execute scans (see Scan Protocols below)
  |
  +-- Generate report
  |
  +-- Execute approved cleanup actions
```

## Scan Protocols

### Scan 1: Orphan Detection

Orphans are files created during a phase that are no longer referenced by the current plan or any active document.

**Method:**
1. Read `.tmp/phase-artifacts.json` to get list of files created/modified this phase
2. For each file: grep the plan file and MEMORY.md for references to that filename
3. If a file is not referenced anywhere AND is not a standard project file (README, CLAUDE.md, .env, etc.): flag as potential orphan
4. Check if the file was created by a task that was later removed from the plan: confirm orphan

**Standard files (never flag as orphans):**
- README.md, CLAUDE.md, .env, .gitignore, package.json, requirements.txt
- Any file in `.tmp/` (managed separately)
- Any file in `node_modules/`, `.git/`, `__pycache__/`
- MEMORY.md, lessons-learned.md, HUMAN-ACTION-REQUIRED.md

### Scan 2: Stale Reference Detection

Stale references are mentions of plan elements (phase names, task names, file paths) that no longer exist in the current plan.

**Method:**
1. Extract all phase names and task descriptions from the current plan file
2. Grep MEMORY.md for references to phase/task names that are NOT in the current plan
3. Grep `.tmp/` JSON files for references to removed phases or tasks
4. Check TodoWrite items against current plan: flag items that reference tasks no longer in the plan

### Scan 3: Duplicate Detection

Duplicates are files with substantially overlapping purpose or content.

**Method:**
1. Compare filenames in `.tmp/` for near-matches (e.g., `plan-v1.md` and `plan-v2.md`)
2. Check for superseded documents: if a file was replaced by a newer version, flag the old one
3. Look for multiple plan files (there should be exactly ONE canonical plan)
4. Check for duplicate lesson entries in lessons-learned.md

### Scan 4: Cross-Reference Integrity

Cross-references are links between documents that must remain valid.

**Method:**
1. In each markdown file modified this phase: find all `[text](path)` links
2. For each link: verify the target file exists
3. In MEMORY.md: verify all referenced files still exist
4. In the plan file: verify all referenced artifacts still exist
5. Flag broken links with the source file, line number, and dead target

## Anti-Patterns

| Anti-pattern | Why it fails | Correct approach |
|-------------|-------------|-----------------|
| Delete files without checking references first | Creates broken links in other documents | Scan for references BEFORE deleting; update referencing docs |
| Flag .tmp/ state files as orphans | These are managed by phase-gate plugin, not by content reference | Exclude .tmp/ from orphan scan entirely |
| Report without acting | User gets a list but nothing gets cleaned | After reporting, execute approved deletions immediately |
| Skip the plan file check | Miss orphans from tasks removed during plan changes | Always diff current plan against artifacts list |
| Treat all unreferenced files as orphans | Source code files aren't referenced in plans | Only audit files tracked in phase-artifacts.json |
| Run full audit on every Write/Edit | Wastes time on routine edits | Only run at phase boundaries or plan changes |
| Delete lessons-learned entries as "duplicates" | Each entry has unique context even if same tool | Only flag exact duplicate entries (same date, same error) |
| Assume MEMORY.md references are current | Memory entries may reference old phase structure | Verify memory references against current plan state |

## Output Template

Return results in this exact format:

```markdown
## Lifecycle Audit Report

**Trigger:** [Phase N completion | Plan change | Manual]
**Scope:** [Full audit | Targeted scan]
**Phase:** [Phase number and name]
**Timestamp:** [ISO timestamp]

### Orphans Found: [N]
| File | Created By | Status | Action |
|------|-----------|--------|--------|
| [path] | [task that created it] | [orphan/uncertain] | [delete/keep/ask user] |

### Stale References Found: [N]
| Source File | Line | Reference | Issue | Action |
|------------|------|-----------|-------|--------|
| [file] | [line] | [the stale ref] | [target removed/renamed] | [update/remove] |

### Duplicates Found: [N]
| File A | File B | Overlap | Action |
|--------|--------|---------|--------|
| [path] | [path] | [description] | [delete A/delete B/merge] |

### Broken Cross-References: [N]
| Source File | Line | Link Target | Action |
|------------|------|-------------|--------|
| [file] | [line] | [dead path] | [update/remove link] |

### Summary
- Orphans: [N] found, [M] deleted, [K] kept
- Stale refs: [N] found, [M] updated, [K] removed
- Duplicates: [N] found, [M] resolved
- Broken links: [N] found, [M] fixed
- Total cleanup actions: [sum]
```

## Examples

### Example 1: Phase completion audit

**Context:** Phase 2 of a dashboard project just completed. During Phase 2, the plan was revised to remove a "chart animations" task.

**Invocation:** "Run lifecycle audit for Phase 2 completion"

**Expected behavior:**
1. Read `.tmp/phase-artifacts.json` -- finds `src/animations.js` was created during Phase 2
2. Check current plan -- "chart animations" task no longer exists
3. Grep for `animations.js` references -- none found in plan, MEMORY.md, or other source files
4. Flag as orphan with recommendation to delete
5. Check MEMORY.md -- finds "Phase 2, Task 4: Add chart animations" reference
6. Flag as stale reference since task was removed from plan
7. Report both findings, execute cleanup

### Example 2: Plan change audit

**Context:** User restructured Phase 3 from "Build API endpoints" into two phases: "Build Read Endpoints" and "Build Write Endpoints". Old plan file was updated in-place.

**Invocation:** "Run lifecycle audit -- plan was just restructured"

**Expected behavior:**
1. Detect this is a plan change trigger, run targeted audit
2. Check TodoWrite for items referencing old "Build API endpoints" phase -- flag stale items
3. Check MEMORY.md for references to old phase name -- flag for update
4. Check `.tmp/active-phase.json` -- verify it references valid phase
5. No orphan scan needed (no tasks were removed, just reorganized)
6. Report stale references, update them

### Example 3: False positive handling

**Context:** Audit finds `src/utils/helpers.js` is not referenced in the plan file.

**Expected behavior:**
1. Check: is this file tracked in `.tmp/phase-artifacts.json`? 
2. If NO: skip it entirely (not a phase artifact, just a source file)
3. If YES: check if the task that created it still exists in the plan
4. Source code files referenced by other source code (imports) are NOT orphans even if the plan doesn't mention them
5. Only flag files whose creating task was removed AND that have no code-level references