# Dimension Scoring Examples

Extended examples for each evaluation dimension. Load when you need calibration examples or are unsure how to score a specific dimension.

---

## D1: Knowledge Delta Examples

### High D1 (15-17): Expert-only content

```markdown
# From hook-development skill (D1=16)
## Hook Lifecycle (6 non-obvious behaviors)
| Phase | What Actually Happens | Gotcha |
|---|---|---|
| Pre-tool | Hook runs BEFORE tool execution | stdout becomes user-visible feedback |
| Matcher evaluation | Glob patterns on tool name + input fields | `*.ts` in path field, not just tool name |
| Exit code semantics | 0=allow, 2=block with message, other=error | Exit code 1 is NOT "block" -- it's "error" |
```

Why D1=16: Claude Code hook lifecycle internals are not in any training data. This is tool-specific, practitioner-discovered knowledge.

### Medium D1 (11-12): Mixed expert and standard

```markdown
# From senior-backend skill (D1=12)
## Database Gotchas
| Gotcha | Why It Matters |
|---|---|
| PgBouncer transaction mode breaks prepared statements | Prisma uses prepared statements by default |
| Prisma connection formula: connections = num_physical_cpus * 2 + 1 | NOT the Node.js worker count |
```

Why D1=12: Backend architecture is extensively blogged, but PgBouncer/Prisma interaction specifics are practitioner-discovered.

### Low D1 (4-8): Training data saturated

```markdown
# From git-commit-helper skill (D1=4)
## Conventional Commits
| Type | When to Use |
|---|---|
| feat | New feature |
| fix | Bug fix |
| refactor | Code restructuring |
```

Why D1=4: Conventional Commits specification is thoroughly documented, widely blogged, and fully in Claude's training data.

---

## D2: Mindset + Procedures Examples

### High D2 (12-14): Expert thinking + domain procedures

```markdown
# Good: Thinking framework + novel procedure
Before designing a popup trigger, ask:
- What user behavior PROVES they've received value? (not just scrolled)
- What's the maximum acceptable interruption cost at this moment?
- Can the same goal be achieved with a less intrusive element?

## IntersectionObserver Trigger Implementation
1. Create observer with rootMargin="-20%" (not 0 -- prevents edge-of-viewport fires)
2. Set threshold array: [0.25, 0.5, 0.75] for scroll velocity detection
3. Disconnect after first trigger to prevent re-fires
```

### Low D2 (3-5): Generic procedures only

```markdown
# Bad: Standard steps Claude already knows
Step 1: Read the user's requirements
Step 2: Plan the implementation
Step 3: Write the code
Step 4: Test the output
Step 5: Review and refine
```

---

## D3: Anti-Pattern Quality Examples

### High D3 (13-15): Named, specific, with "why it fails"

```markdown
| Anti-Pattern | What Happens | Why It Fails |
|---|---|---|
| **The Autopilot** | Run all integrations without asking consent | May expose personal repos. Raw data misses meetings, planning, research |
| **The Status Novel** | Generate 25+ bullet update | Teams tune out after 90 seconds. Long updates are skimmed, not read |
| **The Ticker Tape** | "Reviewed PR #456" with no context | Ticket numbers mean nothing without titles. Forces listeners to look things up |
```

Why high D3: Named patterns ("The Autopilot"), specific triggers ("Run all integrations"), quantified consequences ("90 seconds"), and actionable fixes.

### Low D3 (4-7): Vague, unnamed warnings

```markdown
## Things to Avoid
- Don't make mistakes in the implementation
- Be careful with edge cases
- Avoid overcomplicating the solution
- Consider performance implications
```

Why low D3: No names, no specifics, no "why." Claude can't pattern-match against these vague warnings.

---

## D4: Specification Compliance Examples

### High D4 (14-15): Perfect description + Scope Boundary

Description with trigger conditions + exclusions:
```yaml
description: >
  Use when user says 'daily', 'standup', 'scrum update', 'status update'.
  Do NOT use for: meeting-insights-analyzer (transcription analysis),
  internal-comms (announcements), professional-communication (messages).
```

Body includes Scope Boundary:
```markdown
## Scope Boundary
| Request | This Skill | Use Instead |
|---|---|---|
| "Prepare my daily standup" | YES | - |
| "Summarize this meeting recording" | NO | meeting-insights-analyzer |
```

### Low D4 (6-8): Weak description, no boundaries

```yaml
description: "A skill for helping with meetings and updates"
```

No Scope Boundary table. Description is vague, lacks trigger keywords, no exclusions.

---

## D5: Progressive Disclosure Examples

### High D5 (14-15): File Index with full triggers

```markdown
## File Index
| File | Load When | Do NOT Load |
|---|---|---|
| `integration-troubleshooting.md` | Any integration fails, gh/jira errors, script failures | Simple manual-only standup |
| `standup-effectiveness.md` | User asks about format, async standups, length calibration | Standard standup with no format questions |
| `digest-script-reference.md` | Claude Code history used, digest errors, JSONL questions | No Claude Code integration |
```

### Low D5 (2-3): No companions

A single SKILL.md file with everything inline. No references directory, no File Index, no loading triggers.

### Medium D5 (7-9): Companions without proper triggers

```markdown
## References
- platform-guide.md - for platform-specific information
- troubleshooting.md - for debugging issues
- examples.md - for code examples
```

Companions exist but listing is basic -- no "Load When" scenarios, no "Do NOT Load" guidance.

---

## D6: Freedom Calibration Examples

### Correct calibration

| Skill Type | Freedom Level | Why |
|---|---|---|
| frontend-design (creative) | High -- "Commit to a BOLD direction" | Multiple valid approaches, differentiation is the value |
| docx (file format) | Low -- "MUST use exact script" | One wrong byte corrupts the file |
| code-review (judgment) | Medium -- "Priority: security > logic > perf > style" | Principles exist but judgment required |

### Mismatched calibration (low D6)

- Creative skill with rigid step-by-step procedures (over-constrained)
- File format skill with "use your judgment" guidance (under-constrained)

---

## D7: Pattern Recognition Examples

### D7=9-10: Masterful pattern application

Skill clearly follows one of the five patterns (Mindset, Navigation, Philosophy, Process, Tool) with appropriate length and structure.

### D7=7-8: Clear pattern with minor deviations

Most well-optimized skills land here. They follow a recognizable pattern but may mix elements (e.g., Tool pattern with some Mindset elements).

### D7=4-6: Partial pattern, significant deviations

Chaotic structure that doesn't clearly map to any established pattern.

---

## D8: Practical Usability Examples

### High D8 (14-15): Decision trees + fallbacks + edge cases

```markdown
| Page Type | Primary Issue | First Action |
|---|---|---|
| Long-form content, low scroll depth | Content frontloading | Move key CTA above first screenful |
| Product page, high bounce | Value proposition clarity | Test hero headline against 3 alternatives |
| Checkout, high abandonment at step 3 | Payment friction | Add guest checkout + reduce form fields |

### If Primary Action Fails
| Condition | Fallback |
|---|---|
| CTA move doesn't improve scroll | Test progressive disclosure format |
| Headline test inconclusive after 2 weeks | Sample size insufficient -- extend or increase traffic |
```

### Low D8 (5-7): Vague guidance without decision support

```markdown
Optimize your page for conversions by testing different elements.
Consider the user journey and make appropriate changes.
Monitor results and iterate based on data.
```

No decision trees, no fallbacks, no edge cases. Claude must figure out what to actually do.
