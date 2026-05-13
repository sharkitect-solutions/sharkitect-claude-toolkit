---
name: using-sharkitect-methodology
description: Use when starting any conversation in a Sharkitect workspace OR before any task involving NEW pricing, positioning, proposal, strategy, plan-execution, or schema-design work — mandates invocation of Sharkitect-specific methodology skills (pricing-strategy, marketing-strategy-pmm, smb-cfo, hq-revenue-ops, executing-plans, brainstorming) under the same anti-rationalization discipline as using-superpowers. Documentation has failed 4 times across HQ + Sentinel; this is the reasoning-layer enforcement. Do NOT use for: workspace navigation guidance (use session-startup-guard), individual methodology skill execution (invoke the named skill directly), generic skill discovery (use using-superpowers for superpowers:* skills).
---

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `SKILL.md` (this file) | Every session start; auto-injected via SessionStart hook | Never — always in context |
| `references/skill-catalog.md` | Need full trigger-condition definitions for a specific Sharkitect methodology skill; uncertain whether a domain matches; verifying skill applicability for an edge-case task | First invocation of an obvious-match skill (pricing-strategy on pricing work — catalog adds nothing); routine work clearly under a known skill |
| `references/strategy-creation-rules.md` | About to draft a pricing model, positioning decision, proposal structure, or strategy spec; verifying the HQ-mandated methodology stack ordering; need anti-pattern reference for rationalization | Non-strategy work (debugging, infrastructure, audits without strategic decisions); already invoked the methodology stack this session |

---

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| Strategy / pricing / positioning work begins | YES | — |
| About to write a proposal / spec / design doc | YES | — |
| Executing a written plan task-by-task | YES (cross-ref) | superpowers:executing-plans (this skill catalogs it) |
| Schema design / system design with multiple approaches | YES (cross-ref) | superpowers:brainstorming (this skill catalogs it) |
| Workspace orientation / session-start status | NO | session-startup-guard |
| Generic superpowers skill discovery | NO | using-superpowers |
| Hook / skill / agent creation guidance | NO | hook-development / ultimate-skill-creator / ultimate-agent-creator |
| Knowledge base classification | NO | hq-knowledge-governance (this skill catalogs it as a target) |

---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a Sharkitect methodology skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SHARKITECT METHODOLOGY SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this. Documentation has failed at least 4 times across HQ + Sentinel — runtime enforcement is the closing layer.
</EXTREMELY-IMPORTANT>

## Pre-Decision Thinking Framework

Before drafting ANY pricing, positioning, proposal, or strategy artifact, run this 4-question check:

| # | Question | If "I don't know" or "I haven't" |
|---|---|---|
| 1 | What's the willingness-to-pay anchor for this offer / tier? | INVOKE pricing-strategy |
| 2 | What's the April Dunford positioning frame against the closest alternative? | INVOKE marketing-strategy-pmm |
| 3 | What's the revenue / margin / cash-flow impact of this change? | INVOKE smb-cfo |
| 4 | Have I enumerated 2+ alternatives before settling on this approach? | INVOKE superpowers:brainstorming |

Run all 4 questions BEFORE the first character of the artifact is written. If ANY answer is "I don't know" or "I haven't," the corresponding skill is required — no exceptions.

## Instruction Priority

1. **User's explicit instructions** (CLAUDE.md, workspace rules, direct requests) — highest priority
2. **Sharkitect methodology skills + superpowers skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If a workspace CLAUDE.md says "don't use pricing-strategy this time" and this skill says "always use pricing-strategy for pricing work," follow the user's instruction. The user is in control.

## Sharkitect Methodology Skills (Quick Reference)

Full trigger conditions in `references/skill-catalog.md`. By domain:

### Strategy / Pricing / Positioning
- **`pricing-strategy`** — auto-invoke for: new pricing model, new tier structure, willingness-to-pay analysis, value-based pricing decisions, price elasticity, monthly/setup fee decisions
- **`marketing-strategy-pmm`** — auto-invoke for: new positioning (April Dunford method), competitive positioning, ICP work, alternative framing, market category decisions
- **`smb-cfo`** — auto-invoke for: revenue forecast impact, margin analysis, deal economics, cash flow implications of pricing changes
- **`hq-revenue-ops`** — auto-invoke for: HQ-specific deal economics framework, Sharkitect-deal-shaping work

### Execution Methodology (cross-ref to using-superpowers)
- **`superpowers:brainstorming`** — auto-invoke before committing to any single approach when 2+ alternatives exist
- **`superpowers:writing-plans`** — auto-invoke when implementing multi-step / multi-file work
- **`superpowers:executing-plans`** — auto-invoke when executing a written plan task-by-task
- **`superpowers:systematic-debugging`** — auto-invoke when investigating bugs, unexpected behavior, recurring issues

### Knowledge / Governance / Operations
- **`hq-knowledge-governance`** — K1-K5 classification, knowledge-base health audits
- **`hq-content-enforcer`** — writing, rewriting, editing, reviewing external-facing content
- **`hq-orchestrator`** — task touches multiple business domains
- **`hq-strategic-ops`** — diagnosing architectural debt across Sharkitect's business systems
- **`hq-operations`** — creating or auditing Sharkitect SOPs
- **`hq-tech-strategy`** — technology architecture decisions for Sharkitect
- **`hq-reverse-engineering`** — reverse engineering a competitor's product or system

### People
- **`hr-people-ops`** — hiring, role definitions, org-design work

## The Rule

**Invoke relevant Sharkitect methodology skills BEFORE any response or action.** Even a 1% chance a skill might apply means that you should invoke the skill to check. If an invoked skill turns out to be wrong for the situation, you don't need to use it.

## Anti-Patterns (Named — Reality Reframe — What It Costs)

| Rationalization | Reality | What It Costs |
|---|---|---|
| "I know what pricing-strategy would say" | You don't until you invoke it. Methodology output is non-derivable. | Generic market-anchored averaging instead of WTP-calibrated tier logic. Lost FF Hibu pricing rigor (wr-hq-2026-05-11-001). |
| "This pricing call is simple" | Simple pricing decisions are where the methodology delivers the most measurable benefit. | Naive tier-jump pricing that misses value-anchor; client renegotiates or churns. |
| "I'll add structure later if needed" | Later means never. Spec ships without WTP analysis; downstream phases inherit unanchored numbers. | Numbers get locked in proposals; reversing requires reopening client conversation. |
| "The user wants it fast" | Methodology is faster than 4 recurrences. Invoke. | Each recurrence costs 30-90 min of user-paused work + audit + WR + fix cycle. |
| "I already brainstormed this" | Brainstorming != pricing-strategy. Different skills, different outputs. WTP analysis is NOT a brainstorming output. | Confusing skill outputs leads to half-applied methodology that looks rigorous but isn't. |
| "The work is mostly done already" | The remaining decisions are where methodology matters most. Late-stage skipping shows up in the final spec. | Spec section 8 (contrarian-truth) gets brain-dumped instead of structured. |
| "It's just an audit, not new work" | Audits surface decisions that need methodology too. | Audit-driven decisions inherit the same rigor gap as the original creation. |

## Skill Priority

When multiple Sharkitect skills could apply:

1. **Strategy skills first** (pricing-strategy, marketing-strategy-pmm) — these inform every downstream decision
2. **Execution methodology second** (brainstorming, writing-plans) — these structure the work
3. **Domain execution last** (revenue-ops, content-enforcer) — these execute within the strategy

"New pricing model" → pricing-strategy first, then brainstorming, then marketing-strategy-pmm (positioning implications), then hq-revenue-ops (deal-shape applications).

## When NOT to Invoke (Important — prevents over-invocation)

- **Editing existing content** without strategic change (typo fixes, formatting, link updates) → no methodology skill needed
- **Reading / auditing** without producing a new decision artifact → use the audit's domain skill if it surfaces decisions; otherwise skip
- **Infrastructure work** unless it touches business strategy directly → use hook-development, supabase-postgres-best-practices, etc.
- **Inside the methodology gate itself** (this skill, strategy_work.py, session-startup-guard methodology injection) → bypass via `skip methodology-gate` (you can't gate the gate's own builds)
- **User explicitly overrides** for the session ("skip pricing-strategy for this task") → honor the user's instruction

## User Instructions Override

User instructions ALWAYS win. If a workspace CLAUDE.md says "skip pricing-strategy for this session" or the user directly says "don't use methodology skills here," follow the user's instruction. Document the override in MEMORY.md if it's a recurring pattern.

For one-off bypasses of the runtime gate, the bypass phrase is `skip methodology-gate` in the user message OR in tool content (per Strict Bypass Vocabulary protocol).

## Why This Skill Exists

Documentation has demonstrably failed at least 4 times across HQ + Sentinel:
- `wr-hq-2026-05-11-001` — methodology-skip 3rd recurrence on pricing work (FF Hibu marketing-takeover proposal)
- `wr-hq-2026-05-11-003` — pricing-strategy skill skipped 4th recurrence (pricing model redesign spec)
- `wr-hq-2026-05-12-001` — executing-plans skill not invoked during Sub-project A Phase 1
- `wr-sentinel-2026-05-12-004` — brainstorming skipped on schema design

Each recurrence cost real work and risked real deals. This meta-skill is the reasoning-layer enforcement that turns the documented methodology stack into actual invocation discipline.
