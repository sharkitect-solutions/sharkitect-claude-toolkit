# Plan Decomposition Guide

How to break projects into phases with complexity assessment and task sizing.

---

## Step 1: Assess Overall Scope

Count the total tasks needed to complete the project. Use this decision matrix:

| Total Tasks | Strategy |
|-------------|----------|
| 1-3 | No phases needed. Execute inline. Skip this skill. |
| 4-8 | Single phase or 2 small phases. Light structure. |
| 9-15 | 2-4 phases of 4-6 tasks each. Standard structure. |
| 16-30 | 4-6 phases of 5-7 tasks each. Full structure. |
| 30+ | Consider splitting into separate projects. Each "project" gets its own phase structure. |

---

## Step 2: Group Tasks into Phases

### Grouping principles

1. **Dependency order:** Tasks that must complete before others start go in earlier phases
2. **Domain cohesion:** Tasks that touch the same area (same files, same API, same system) go together
3. **Deliverable boundaries:** Each phase should produce a tangible, testable result
4. **Session fit:** A phase should be completable in 1-2 sessions (not 5+ sessions per phase)

### Phase sizing rules

| Rule | Threshold | Action |
|------|-----------|--------|
| Maximum tasks per phase | 8 | Split into two phases if more |
| Minimum tasks per phase | 2 | Merge with adjacent phase if fewer |
| Maximum sub-tasks per task | 10 | Promote task to its own phase |
| Maximum estimated duration | 2 sessions | Split if it would take longer |

---

## Step 3: Complexity Assessment

For each task, estimate complexity:

| Complexity | Indicators | Sub-task estimate |
|-----------|-----------|-------------------|
| **Simple** | Single file change, clear requirements, no external dependencies | 0-2 sub-tasks |
| **Moderate** | Multiple files, some decision-making, 1-2 external deps | 3-6 sub-tasks |
| **Complex** | Architectural decisions, multiple systems, unknown unknowns | 7-15 sub-tasks |
| **Epic** | Cross-project impact, multiple sessions, requires research | 15+ sub-tasks → becomes its own phase |

### Promotion rule
If a task's sub-task count exceeds 10, it's not a task -- it's a phase. Promote it:

```
Before: Phase 2, Task 3: "Build complete dashboard" (15 sub-tasks)

After:  Phase 2: Build Dashboard Layout (5 sub-tasks)
        Phase 3: Build Dashboard Data Integration (5 sub-tasks)
        Phase 4: Build Dashboard Interactivity (5 sub-tasks)
```

---

## Step 4: Write the Plan

### Plan file format

```markdown
# [Project Name] Implementation Plan

## Overview
[1-2 sentence summary of what this project achieves]

## Phase 1: [Phase Name]
**Objective:** [One sentence -- what is done when this phase completes?]
**Estimated tasks:** [N]

### Tasks
1. [Task description]
2. [Task description]
   - Sub-task a
   - Sub-task b
3. [Task description]

## Phase 2: [Phase Name]
**Objective:** [One sentence]
**Estimated tasks:** [N]
**Depends on:** Phase 1

### Tasks
1. ...

## Phase 3: ...
```

### Rules
- ONE plan file. Update in-place. Never create duplicates.
- Store in `.claude/plans/` (Claude Code native) or project-specific location
- Each phase has an objective that can be verified as "done" or "not done"
- Dependencies between phases are explicit

---

## Step 5: Initialize Phase Tracking

When starting a phase, create `.tmp/active-phase.json`:

```json
{
  "number": 1,
  "name": "Setup Foundation",
  "status": "active",
  "started": "2026-03-31T14:00:00Z",
  "tasks_total": 5,
  "tasks_done": 0,
  "plan_file": ".claude/plans/my-project.md"
}
```

This file is read by:
- `phase-gate` plugin hooks (to detect active phase)
- `aios-core` SessionStart (to remind you of active work)
- Phase Completion Protocol (to know what to checkpoint)

---

## Common Decomposition Patterns

### Pattern: Build → Integrate → Polish
```
Phase 1: Build core components independently
Phase 2: Integrate components together
Phase 3: Polish, test, document
```

### Pattern: Research → Prototype → Production
```
Phase 1: Research and spike (gather info, test assumptions)
Phase 2: Build prototype (working but rough)
Phase 3: Production-ize (error handling, edge cases, docs)
```

### Pattern: Data → Logic → Interface
```
Phase 1: Set up data layer (schema, migrations, seed)
Phase 2: Build business logic (APIs, processing)
Phase 3: Build interface (UI, CLI, whatever users touch)
```

### Pattern: Audit → Plan → Execute → Verify
```
Phase 1: Audit current state (what exists, what's broken)
Phase 2: Plan changes (design new structure)
Phase 3: Execute changes (implement)
Phase 4: Verify and clean up (test, document, sync)
```