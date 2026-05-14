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

Routes by v3.2 architecture mechanics. Branches lead to the K1 SoT decision; this skill does not encode the decision values.

```
NEW DEAL OR PRICING DECISION
  |
  +-- Wrapper choice clarified?
  |     Standard Partnership Wrapper  -->  continue (advisory layer = Chris)
  |     AIOS Wrapper                  -->  continue (advisory layer = AIOS agent;
  |                                          mechanics inherit aios-pricing.md v1.5)
  |     Mutual exclusivity: client picks ONE wrapper. See pricing-structure.md v3.2 § 2.
  |
  +-- Sub-threshold engagement (client below typical Partnership tier)?
  |     YES -->  Sharkitect Growth Essentials: $2,500 setup, $250/mo,
  |              Partnership Wrapper fee WAIVED, 12-month minimum, upgrade path at month 12+.
  |              See sharkitect-growth-essentials.md v1.1 + pricing-structure.md v3.2 § 13.
  |     NO  -->  continue with Wrapper + Project Lines.
  |
  +-- Project Lines required (per v3.2 § 7)?
  |     VDR (VoiceDesk AI Receptionist) -- Capacity-Tiered (coverage band)
  |     RLR (RapidLead Response)         -- Capacity-Tiered (email sends/mo)
  |     SLW (SystemLink Workflow Sync)   -- Scope-Built (Complexity Scorecard per slw-pricing-calculator.md v1.0)
  |     PPM (PresencePulse Marketing)    -- Capacity-Tiered (three independent axes)
  |     CPS (ContentPulse Social Engine) -- Capacity-Tiered, ADD-ON ONLY
  |       Gate: NEVER entry point; requires >= 1 core service live 90+ days
  |       (90-day waiver allowed for vendor transitions). See v3.2 § 15 Rule #1.
  |
  +-- Founding Partner Rate eligibility?
  |     First 5 signed clients only -->  $1,500/mo Standard wrapper, 24-month lock
  |                                       (anchor in v3.2; numbers refined in pricing sub-step).
  |     Client #6+                  -->  Standard non-FP rate (placeholder pending pricing sub-step).
  |     Terminology rule: ALWAYS "Founding Partner Rate" / "partnership evolution review".
  |                       NEVER "grandfathered" / "legacy pricing" / "price increase".
  |     See v3.2 § 11.
  |
  +-- Multi-system expansion sequence (Partnership Progression Pricing, setup only)?
  |     2nd system within 12 months of prior go-live  -->  25% off SETUP
  |     3rd+ system within 12 months of prior go-live -->  40% off SETUP
  |     $2,500 setup minimum floor enforced regardless of discount (v3.2 § 9 + § 15 Rule #12).
  |     NEVER applies to monthly recurring (v3.2 § 15 Rule #4). Frame as efficiency saving,
  |     NOT a discount.
  |
  +-- Annual commitment?
  |     15% off MONTHLY recurring -->  Wrapper + Scope-Built (flat-fee) project lines ONLY.
  |     Capacity-Tiered project lines have NO annual discount (capacity flex IS the value lever).
  |     See v3.2 § 10.
  |
  +-- Approval routing & payment-term thresholds
        Canonical decision rules live in financial-operations-guide.md (HQ knowledge-base/governance/)
        and sales-enablement-playbook.md (HQ knowledge-base/revenue/). This skill routes to
        those K1 SoTs rather than encoding the thresholds.
```

## Pricing Guardrails (Quick Reference -- v3.2-sourced)

Quick checks. Full details and authoritative values live in `pricing-structure.md` v3.2. This skill cites; it does not duplicate.

| Guardrail | Rule | K1 source |
|-----------|------|-----------|
| **Setup fee floor** | $2,500 minimum on every setup -- no setup drops below this regardless of discount or tier | v3.2 § 9 + § 15 Rule #12 |
| **Partnership Progression Pricing** | 0% on 1st system, 25% off SETUP on 2nd, 40% off SETUP on 3rd+ (efficiency saving, never framed as discount) | v3.2 § 9 |
| **Expansion window** | Progression discount applies only if next system added within 12 months of prior go-live | v3.2 § 9 |
| **Annual Commitment** | 15% off MONTHLY recurring -- Wrapper + Scope-Built lines ONLY (NOT capacity-tiered) | v3.2 § 10 |
| **Multi-service monthly discounts** | NONE -- only setup fees receive progression pricing | v3.2 § 15 Rule #4 |
| **CPS entry rule** | NEVER entry point; requires >= 1 core service live 90+ days (90-day waiver only for vendor transitions) | v3.2 § 15 Rule #1 |
| **Capacity tiers** | Volume only -- NEVER feature gating; every client at every tier gets standard inclusions | v3.2 § 15 Rule #3 |
| **Lead notification destinations** | Cap 2 per service (CRM / email / Slack); additional = a la carte | v3.2 § 15 Rule #13 |
| **Founding Partner eligibility** | First 5 signed clients only; 24-month lock; "Founding Partner Rate" terminology mandatory | v3.2 § 11 |
| **Implementation fees** | Never discounted -- only setup/build fees receive Partnership Progression Pricing | v3.2 § 9 |
| **Platform costs** | Absorbed into project monthly fee -- never passthrough line items | v3.2 § 15 Rule #9 |
| **Verbal pricing** | NEVER given -- always present in written proposal format (see Anti-Patterns below) | Sharkitect operations standard |

Margin floors, payment-term thresholds, and approval-authority brackets live in `knowledge-base/governance/financial-operations-guide.md`. Cite, don't encode.

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
3. **Lifecycle-Tier Mismatch**: Treating a Tier 1 Lead (no meeting yet) with Tier 3 Active Client attention (full custom card, dedicated Slack, monthly KPI reports) OR treating a Tier 3 Active Client with Tier 1 Lead service level (still on generic card). See `client-journey-tier-framework.md` v1.0 for the canonical lifecycle tiers (T0 Anonymous → T1 Lead → T2 Prospect → T3 Active Client → T4 Advocate). Over-servicing pre-qualified leads burns capacity; under-servicing active clients signals "we stopped caring." Service level must match lifecycle state, not deal size.
4. **Skipping Qualification**: Jumping to proposals without confirming budget, authority, need, and timeline. Unqualified proposals have a <10% close rate and waste 8+ hours each.
5. **Verbal Agreements**: "They said yes on the call" is not a closed deal. Nothing is real until it's signed and payment method is on file.
6. **Making It Up Next Phase**: Discounting Phase 1 assuming Phase 2 will be at full price. Recovery rate is only 30% — 7 out of 10 clients who got a discounted Phase 1 expect the same discount on Phase 2 or walk. A $1,000 Phase 1 discount turns into $3,000+ in lost margin across a 3-phase engagement.
7. **Revenue Concentration Blindness**: Letting one client exceed 25% of total revenue without a mitigation plan. If that client churns, expect 3+ months to recover the revenue gap. During recovery, cash flow strain forces you to accept below-margin deals, creating a downward spiral. Check revenue concentration monthly.
8. **Handshake Pricing**: Quoting prices verbally before running margin math against guardrails. 40% of verbal quotes end up below minimum margin because they skip the pricing validation step. Once a number is spoken, the client anchors to it, and walking it back damages trust. Always run the deal through the pricing guardrails table BEFORE any number leaves your mouth.
