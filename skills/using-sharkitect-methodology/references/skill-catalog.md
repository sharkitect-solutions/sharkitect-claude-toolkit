# Sharkitect Methodology Skills — Full Catalog with Trigger Conditions

> Companion reference for the `using-sharkitect-methodology` meta-skill.
> Each entry: skill name, when to auto-invoke, what it produces.
> Source: Cluster A spec, docs/superpowers/specs/2026-05-12-methodology-gate-cluster-a-design.md

## Strategy / Pricing / Positioning

### pricing-strategy
**Auto-invoke when:** task involves a new pricing model, new tier structure, willingness-to-pay analysis, value-based pricing rationale, price elasticity considerations, monthly/setup fee decisions, capacity-flex mechanics, or any modification to `knowledge-base/revenue/pricing-structure*.md`.

**What it produces:** structured WTP analysis, value-based pricing rationale, tier-positioning logic, elasticity-aware decision frames.

**Recurrence-history note:** skipped 4 times across HQ. wr-hq-2026-05-11-001 + wr-hq-2026-05-11-003 closed via Cluster A meta-skill + runtime ask-gate.

### marketing-strategy-pmm
**Auto-invoke when:** task involves new product positioning, April Dunford-style category definition, competitive alternative framing, ICP refinement, market-category decisions, or premium-tier positioning decisions.

**What it produces:** April Dunford-style positioning statement, alternative framing analysis, ICP-aligned messaging structure.

### smb-cfo
**Auto-invoke when:** task involves revenue forecast impact, margin analysis, deal economics, cash flow implications of pricing changes, or any quantitative-CFO-perspective input on a strategy decision.

**What it produces:** revenue forecast deltas, margin analysis, cash flow modeling.

### hq-revenue-ops
**Auto-invoke when:** task involves HQ-specific deal economics framework, Sharkitect-deal-shaping work, or applying Sharkitect's specific revenue-ops methodology to a deal.

**What it produces:** HQ-framework-applied deal economics, Sharkitect-specific pricing constraints.

## Execution Methodology (cross-reference to using-superpowers)

### superpowers:brainstorming
**Auto-invoke when:** committing to any approach where 2+ alternatives exist, before writing a design spec, before architectural decisions.

**Recurrence-history note:** skipped on schema design (wr-sentinel-2026-05-12-004). Closed via Cluster A meta-skill cross-reference.

### superpowers:writing-plans
**Auto-invoke when:** about to implement multi-step / multi-file work, after brainstorming produces a design spec.

### superpowers:executing-plans
**Auto-invoke when:** executing a written plan file with checkbox tasks.

**Recurrence-history note:** skipped during Sub-project A Phase 1 (wr-hq-2026-05-12-001). Closed via Cluster A meta-skill catalog entry.

### superpowers:systematic-debugging
**Auto-invoke when:** investigating bugs, test failures, unexpected behavior, recurring incidents.

## Knowledge / Governance / Operations

### hq-knowledge-governance
**Auto-invoke when:** auditing knowledge base health, classifying documents K1-K5, detecting orphaned or conflicting documents.

### hq-content-enforcer
**Auto-invoke when:** writing, rewriting, editing, or reviewing external-facing content (client-facing, prospect-facing, social, web).

### hq-orchestrator
**Auto-invoke when:** task touches multiple business domains (revenue + operations, knowledge + revenue, etc.).

### hq-strategic-ops
**Auto-invoke when:** diagnosing architectural debt across Sharkitect's business systems.

### hq-operations
**Auto-invoke when:** creating or auditing Sharkitect SOPs.

### hq-tech-strategy
**Auto-invoke when:** making technology architecture decisions for Sharkitect.

### hq-reverse-engineering
**Auto-invoke when:** reverse engineering a competitor's product or system.

## People

### hr-people-ops
**Auto-invoke when:** writing job descriptions, designing hiring pipelines, defining roles, org-design work.

---

## How This Catalog Is Maintained

When a new Sharkitect methodology skill is created:
1. Add an entry here with trigger conditions + output description
2. Add a cross-reference to the appropriate domain section in `SKILL.md`
3. Re-run `skill-judge` on `using-sharkitect-methodology` to verify the catalog addition doesn't break the description-token coverage

When a skill is renamed or retired:
1. Update the entry here (or remove)
2. Update the `SKILL.md` quick-reference table
3. Update `METHODOLOGY_SKILLS` tuple in `~/.claude/hooks/_dispatchers/methodology/strategy_work.py` if the skill is in the runtime gate's allow-list
