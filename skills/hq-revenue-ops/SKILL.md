---
name: hq-revenue-ops
description: >
  Use when evaluating Sharkitect Digital deal economics, applying client tiering rules, validating
  pricing against margin targets, managing pipeline governance, or coordinating deal approval workflows.
  Covers deal scoring, pricing validation, client tier classification, and revenue-related escalation.
  NEVER use for general financial modeling or P&L analysis (use financial-analyst agent),
  market-level pricing research (use competitive-intelligence-analyst agent),
  or sales outreach and prospecting (use sales-researcher agent).
version: 0.1.0
---

# HQ Revenue Operations — Deal Governance & Client Tiering

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/client-tiers.md` | Every deal evaluation, pricing decision, or client classification task | General financial analysis unrelated to specific deals |
| `references/pricing-psychology.md` | Building proposals, structuring pricing options, planning upsells, or framing discounts | Quick tier lookups, pipeline stage checks, or deal approval routing |

## Paired Agents

Launch these agents (Task tool) for execution:
- `sales-researcher` — Lead qualification, prospect research, outreach strategy
- `customer-success-manager` — Client health scoring, retention strategy, upsell identification
- `financial-analyst` — P&L analysis, cash flow, unit economics (when deal-level analysis needs financial context)

The `smb-cfo` skill provides the financial modeling layer. This skill provides the deal governance layer. They complement but don't overlap — smb-cfo answers "can we afford this?" while hq-revenue-ops answers "should we do this deal?"

Use this skill directly (without agent) for:
- Quick client tier classification
- Deal approval routing (who needs to sign off)
- Pricing guardrail checks

## Scope Boundary

| Request | This Skill | Use Instead |
|---------|-----------|-------------|
| "Evaluate this deal" | YES | - |
| "Check client tier" | YES | - |
| "Validate pricing against guardrails" | YES | - |
| "Route deal for approval" | YES | - |
| "Build a pricing model" | NO | smb-cfo skill |
| "Research competitor pricing" | NO | competitive-intelligence-analyst agent |
| "Write a proposal document" | NO | copywriting skill |
| "Forecast revenue for next quarter" | NO | financial-analyst agent |
| "Create a discount strategy" | NO | pricing-strategy skill |
| "Run a sales outreach campaign" | NO | sales-researcher agent |

## Deal Evaluation Decision Tree

```
NEW DEAL OR PRICING DECISION
  |
  +-- What's the monthly recurring value?
  |   |
  |   |-- Under $500/mo → Tier 3 (Standard). Auto-approve if within guardrails.
  |   |-- $500-$2,000/mo → Tier 2 (Growth). Requires margin check.
  |   |-- $2,000-$5,000/mo → Tier 1 (Strategic). Requires full deal review.
  |   |-- Over $5,000/mo → Tier 0 (Enterprise). CEO approval required.
  |
  +-- Does it involve custom development?
  |     YES --> Add 30% margin buffer to base pricing
  |     NO  --> Standard service pricing applies
  |
  +-- Is the client requesting payment terms beyond Net 30?
  |     YES --> Requires financial-analyst assessment of cash flow impact
  |     NO  --> Standard terms apply
  |
  +-- Is this a multi-service bundle?
        YES --> Apply bundle discount rules from client-tiers.md
        NO  --> Single service pricing
```

## Pricing Guardrails (Quick Reference)

Full details in companion file. Quick checks:

| Guardrail | Rule | Violation Action |
|-----------|------|-----------------|
| **Minimum margin** | Never below 40% gross margin | Block deal, escalate |
| **Discount cap** | Max 20% off list price | CEO approval for anything higher |
| **Free work** | No free work beyond initial consultation | No exceptions |
| **Scope creep** | Every change order documented and priced | Stop work if unpaid scope grows |
| **Payment terms** | Net 30 standard, Net 45 max for Tier 0/1 | No Net 60+ without CEO approval |

## Pipeline Governance

| Stage | Required Before Moving Forward |
|-------|-------------------------------|
| **Lead** | Contact info + source identified |
| **Qualified** | Budget confirmed + decision-maker identified + timeline established |
| **Proposal** | Scope document + pricing validated against guardrails |
| **Negotiation** | All terms documented + approval chain completed for tier |
| **Closed Won** | Signed contract + payment method on file |
| **Closed Lost** | Loss reason documented + competitive intel captured |

## Anti-Patterns

1. **Undercutting for Volume**: Dropping below 40% margin to win deals destroys the business model. One bad deal at 20% margin requires three good deals at 50% to recover.
2. **Scope Ambiguity**: "We'll figure it out as we go" in proposals leads to scope creep. Every deliverable must be listed. What's NOT included matters as much as what IS.
3. **Tier Mismatch**: Treating a Tier 3 client with Tier 1 attention (or vice versa). Service level must match tier. Over-servicing Tier 3 clients is the #1 profitability killer.
4. **Skipping Qualification**: Jumping to proposals without confirming budget, authority, need, and timeline. Unqualified proposals have a <10% close rate and waste 8+ hours each.
5. **Verbal Agreements**: "They said yes on the call" is not a closed deal. Nothing is real until it's signed and payment method is on file.
6. **Making It Up Next Phase**: Discounting Phase 1 assuming Phase 2 will be at full price. Recovery rate is only 30% — 7 out of 10 clients who got a discounted Phase 1 expect the same discount on Phase 2 or walk. A $1,000 Phase 1 discount turns into $3,000+ in lost margin across a 3-phase engagement.
7. **Revenue Concentration Blindness**: Letting one client exceed 25% of total revenue without a mitigation plan. If that client churns, expect 3+ months to recover the revenue gap. During recovery, cash flow strain forces you to accept below-margin deals, creating a downward spiral. Check revenue concentration monthly.
8. **Handshake Pricing**: Quoting prices verbally before running margin math against guardrails. 40% of verbal quotes end up below minimum margin because they skip the pricing validation step. Once a number is spoken, the client anchors to it, and walking it back damages trust. Always run the deal through the pricing guardrails table BEFORE any number leaves your mouth.
