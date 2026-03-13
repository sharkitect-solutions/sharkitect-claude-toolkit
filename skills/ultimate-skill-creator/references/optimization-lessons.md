# Optimization Lessons from 100+ Skill Evaluations

## Domain Saturation Hierarchy

The single biggest factor in a skill's D1 (Knowledge Delta) score is how well Claude's training data already covers the domain. This is NOT controllable -- it's an inherent property of the domain.

### D1 Scores by Domain Type (from real evaluations)

| D1 Range | Domain Characteristics | Examples |
|---|---|---|
| 15-17/20 | Proprietary systems, tool-specific internals, very recent technology | Claude Code hooks (16), Telegram API gotchas (16), canvas art-direction (16), programmatic visual design (16) |
| 13-14/20 | Specialized but documented, cross-domain intersections | Voice AI provider specifics (14), MCP protocol (14), mobile billing compliance (14), email deliverability (13) |
| 11-12/20 | Well-documented professional domains | Backend architecture (12), copy editing (11), deslop/AI patterns (12), micro-SaaS (11) |
| 8-10/20 | Heavily blogged, well-covered by training data | CRO/conversion optimization (8-10), page optimization (9), form design (8) |
| 4-6/20 | Thoroughly in training data, standard practices | Git conventional commits (4), basic coding patterns (5) |

### Implications for Skill Creators

| If Your Domain D1 Is... | Strategy | Expected Score Range |
|---|---|---|
| 15+ | Focus on decision frameworks and anti-patterns. Pure content drives score | 100-110+ |
| 12-14 | Add cross-domain expertise that blogs don't cover (platform-specific gotchas, API internals) | 96-105 |
| 9-11 | Companion files critical. Research citations and quantified data create delta | 90-100 |
| 4-8 | D1 is the binding constraint. Even perfect structure can't overcome domain saturation | 80-95 (may not reach B gate) |

**Key insight**: Skills in D1<=8 domains may never reach 96+ (B gate) regardless of optimization effort. The ceiling is the domain, not the skill.

---

## Named Anti-Pattern Design

Skills with named anti-patterns consistently score 2-3 points higher on D3 than skills with generic warnings.

### The Naming Format

```markdown
| Anti-Pattern | What Happens | Why It Fails | Fix |
|---|---|---|---|
| **The Autopilot** | Run tools without asking, dump raw data | Users may have personal repos visible. Raw data misses context | Always ask consent. Always interview. Tools supplement, never replace |
```

### Why Naming Works

| Factor | Named Pattern | Generic Warning |
|---|---|---|
| **Memorability** | "The Autopilot" sticks in context | "Don't run tools without asking" is forgotten |
| **Pattern matching** | Claude recognizes "I'm doing The Autopilot" mid-task | Claude can't match against vague warnings |
| **Conversation reference** | "You're falling into The Status Novel" is actionable | "Your update is too long" lacks framework |
| **Self-check** | Named patterns are scannable as a checklist | Generic warnings blur together |

### Naming Conventions

| Convention | Example | When to Use |
|---|---|---|
| **The [Noun]** | The Autopilot, The Dump, The Skeleton | Most common. Names the pattern as a character |
| **The [Adj] [Noun]** | The Premature Generate, The Single-Repo Assumption | When noun alone is ambiguous |
| **[Domain] [Pattern]** | Status Theater, Blocker Burial | When the pattern is domain-specific |

Target: 6-8 named anti-patterns per skill. Each must have "What Happens," "Why It Fails," and "Fix" columns.

---

## Decision Matrix Design

Decision matrices are the highest-D8 pattern. They provide immediate actionability by mapping inputs to outputs.

### The First-Match Pattern

```markdown
| Signal | Decision | Rationale |
|---|---|---|
| Team < 5 engineers | Monolith | Communication overhead exceeds service boundary value |
| Deploy frequency < weekly | Monolith | Microservices add complexity without deployment flexibility benefit |
| Data coupling > 60% | Monolith | Shared database defeats the purpose of service boundaries |
| All above clear | Microservices | Team size, deploy cadence, and data boundaries all support it |
```

Rules for first-match design:
- Order rows from most common to least common scenario
- First matching row is the answer -- stop evaluating
- Last row is the default/fallback
- Include quantified thresholds where possible ("< 5 engineers" not "small team")

### Decision Matrix Quality Markers

| Good Matrix | Bad Matrix |
|---|---|
| Quantified thresholds (< 5, > 60%) | Vague qualifiers ("small", "high", "many") |
| Mutually exclusive rows | Overlapping conditions that match multiple rows |
| Clear action per row | Actions that still require judgment ("consider X") |
| First-match ordering | Random ordering requiring full table scan |
| 5-8 rows | 15+ rows (too many to be useful as a quick reference) |

---

## Compression Techniques

Skills often start verbose. The optimization cycle compresses ruthlessly.

### What to Delete

| Content Type | Delete? | Rationale |
|---|---|---|
| "What is X" explanations | YES | Claude already knows. Zero knowledge delta |
| Step-by-step tutorials for standard operations | YES | Generic procedures Claude can generate |
| Example conversations/dialogues | YES | Take 50-100 lines, provide minimal guidance value |
| Output templates (pre-formatted examples) | YES | Output format should be generated dynamically |
| ASCII art diagrams | YES | Consume tokens, rarely add decision value |
| Hedging language ("you might want to", "consider") | YES | Replace with imperatives |
| Feature lists of what the skill covers | YES | This belongs in description, not body |

### What to Keep

| Content Type | Keep? | Rationale |
|---|---|---|
| Decision matrices and tables | YES | Highest-value content format |
| Named anti-patterns with "why it fails" | YES | D3 core content |
| Rationalization tables | YES | Pressure defense mechanism |
| Scope Boundary tables | YES | D4 compliance |
| Red flags / NEVER lists | YES | Self-check mechanisms |
| Quantified claims with sources | YES | Knowledge delta (D1) |
| File Index with loading triggers | YES | D5 progressive disclosure |

### Compression Ratios from Real Optimizations

| Starting Size | Target Size | Typical Ratio | Example |
|---|---|---|---|
| 400-600 lines | 150-200 lines | 55-65% reduction | marketing-demand-acquisition: 986->165 (83%) |
| 200-400 lines | 120-180 lines | 40-55% reduction | daily-meeting-update: 409->160 (61%) |
| 50-100 lines | 130-180 lines | Expansion | deslop: 24->155 (expanded -- too sparse originally) |

The ideal SKILL.md body is 130-200 lines. Below 100 usually means insufficient expert content. Above 300 usually means content should move to companions.

---

## File Index Placement

Through A/B testing across optimization batches:

| Placement | D5 Score Impact | Why |
|---|---|---|
| After frontmatter + intro (lines 15-30) | 13-15/15 | Claude encounters it early, loads companions when needed |
| Middle of SKILL.md (lines 60-80) | 10-12/15 | Sometimes missed during sequential reading |
| Bottom of SKILL.md (last section) | 8-10/15 | Often skimmed or missed entirely |

**Rule**: File Index should be the FIRST content section after the skill's opening paragraph or CSO description block.
