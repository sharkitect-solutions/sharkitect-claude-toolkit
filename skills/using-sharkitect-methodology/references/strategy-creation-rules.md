# Strategy Creation Rules — Reference Excerpt

> Source: `1.- SHARKITECT DIGITAL WORKFORCE HQ/CLAUDE.md` Strategy Creation Rules section.
> Kept in sync via sync-skills.py. Excerpt for parity inside the meta-skill folder.

## Pre-Strategy-Work Methodology Stack

When undertaking NEW strategic work (new pricing model, new positioning, new offer structure, new proposal architecture), invoke skills in this order BEFORE drafting:

1. **`pricing-strategy`** — for pricing/tier work (willingness-to-pay, value-based)
2. **`marketing-strategy-pmm`** — for positioning work (April Dunford method)
3. **`superpowers:brainstorming`** — for divergent enumeration before committing to single approach
4. **`smb-cfo`** — for revenue forecast / margin implications
5. **`hq-revenue-ops`** — for HQ-specific deal economics framework
6. **`superpowers:writing-plans`** — for multi-phase migration / implementation structure
7. **`writing-clearly-and-concisely`** — for spec / proposal authoring

## Trigger Conditions

These triggers activate the stack:
- New pricing model / new tier structure
- New positioning (vs Hibu, Cyncly, Thryv, Scorpion, etc.)
- New proposal architecture (multi-document, multi-phase, tiered pricing)
- New offer structure
- Significant revision to existing pricing-structure.md (v2.0 → v3.0 class change)
- Marketing-takeover proposals
- Competitive market anchoring decisions

## Anti-Patterns

These thoughts MEAN you are skipping methodology and need to STOP:

- "I've done pricing before, I know what to do."
- "The user wants a fast answer."
- "Methodology is overkill for this."
- "I'll add structure later."
- "Generic market-anchored averaging is enough."

When you catch yourself with any of these, INVOKE THE SKILL FIRST. The methodology IS the structure that prevents pricing errors that lose deals.

## Why This Reference Exists

The HQ Strategy Creation Rules section was created after wr-hq-2026-05-09-007 + wr-hq-2026-05-09-008 (2nd recurrence of methodology-skip). Despite this rule being in HQ's CLAUDE.md, the 3rd (wr-hq-2026-05-11-001) and 4th (wr-hq-2026-05-11-003) recurrences happened. Documentation alone failed; Cluster A (this meta-skill + SessionStart injection + strategy_work dispatcher sub-rule) is the runtime + reasoning-layer closing fix.

## Sync Discipline

This file is a snapshot of HQ's Strategy Creation Rules. When HQ updates its CLAUDE.md Strategy Creation Rules:
1. HQ commits the change
2. sync-skills.py (run from Skill Hub) detects the drift via the cross-document integrity check
3. This file is updated in the next Skill Hub session to maintain parity
