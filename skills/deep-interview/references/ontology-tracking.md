# Ontology Tracking: Entity Convergence Method

Track the key entities (nouns) a user names across interview rounds. When entities
stabilize, the user's mental model is solid. When they keep shifting, the scope is
still fuzzy and feature-level questions will compound confusion.

## What to Track

After each user answer, extract the **core entities** they named or implied:

- **Systems**: "database", "API", "webhook", "queue"
- **Objects**: "task", "user", "order", "document", "report"
- **Actors**: "admin", "customer", "team member", "bot"
- **Containers**: "workspace", "project", "folder", "channel"

Record each entity with a short type label (core, supporting, external).

## Detecting Instability

**Rename detection:** Same concept, different names across rounds.

| Round | User Said | Likely Same Entity? |
|---|---|---|
| 1 | "workflow" | - |
| 2 | "pipeline" | Yes -- same concept, different name |
| 3 | "automation" | Yes -- third name for the same thing |

**Signal:** If the core entity has 3+ names across 3 rounds, the user hasn't
crystallized what this thing IS. Stop asking about what it DOES and ask what it IS.

**Split detection:** One entity becomes two.

| Round | User Said | What Happened |
|---|---|---|
| 1 | "tasks" | Single entity |
| 3 | "tasks" and "subtasks" | Split into parent/child |
| 5 | "tasks", "subtasks", and "milestones" | Three related entities |

**Signal:** Splits are healthy IF the user chose them deliberately. Ask: "You've
separated [X] into [Y] and [Z]. Is that intentional, or should these stay as one thing?"

**Merge detection:** Two entities become one.

| Round | User Said | What Happened |
|---|---|---|
| 2 | "alerts" and "notifications" | Two entities |
| 4 | "notifications" (encompassing both) | Merged |

**Signal:** Merges simplify scope. Confirm: "So alerts and notifications are the same
system now? Or are they still different under the hood?"

## Stability Scoring

After each round, compare the current entity list to the previous round:

- **Stable entity:** Same name, same type, present in both rounds
- **Renamed entity:** Different name but same type + similar context (counts as stable)
- **New entity:** Not present in any form in the previous round
- **Removed entity:** Present before, absent now

```
stability_ratio = (stable + renamed) / total_current_entities
```

| Stability | Meaning | Action |
|---|---|---|
| 100% | All entities same as last round | Ready to proceed -- model is solid |
| 75-99% | Minor additions, no removals or renames | Probably ready -- confirm the new ones |
| 50-74% | Significant changes | Core concept may be shifting -- probe scope |
| <50% | More entities changed than stayed | Mental model is unstable -- ask "what IS this?" |

## When to Trigger Ontology Questions

Trigger an ontology-style question (instead of the next dimension-targeting question) when:

1. **Stability < 75% for 2 consecutive rounds.** The user keeps changing what the
   things are. Feature questions are premature.
2. **Core entity renamed 3+ times.** The user can't settle on what to call the
   central concept. This is a naming problem that masks a scope problem.
3. **Entity count growing every round without stabilization.** The user keeps
   adding things. Ask: "Which of these is the ONE core thing, and which are
   supporting details?"

## Ontology Questions

These target the IS, not the DOES:

- "You've called this [X], [Y], and [Z] across our conversation. What IS it at its core?"
- "Looking at everything we've discussed, which entity is the CENTER -- the one
  everything else orbits? And which are supporting?"
- "If you had to draw a box around the ONE thing this project creates/manages/processes,
  what goes inside the box and what stays outside?"
- "I'm seeing [N] distinct entities. For v1, which ones are essential and which could
  be added later?"

## Reporting in the Brief

When the requirements brief is produced (Phase 4), include an entity summary:

```markdown
### Key Entities
| Entity | Type | Stable Since | Notes |
|---|---|---|---|
| Task | Core | Round 1 | Central object -- CRUD + status transitions |
| User | Supporting | Round 1 | Maps to existing auth system |
| Tag | Supporting | Round 3 | Added for filtering, optional for v1 |
| Workflow | Core | Round 4 | Was "pipeline" in R2, "automation" in R3, settled as "workflow" |
```

The "Stable Since" column shows when each entity stopped changing -- later rounds
mean the concept took longer to crystallize, which is worth noting as a risk area.
