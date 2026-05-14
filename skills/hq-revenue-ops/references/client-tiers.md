# Sharkitect Digital — Client & Service Tiering (Pointer Doc)

**Status:** active | **Last rebuilt:** 2026-05-13 | **Reason:** Drift correction per `wr-hq-2026-05-13-001` — prior version encoded a fabricated 4-tier ($5K+/$2-5K/$500-2K/<$500) client price-band model and pricing guardrails that do not exist in current v3.0 architecture.

**Authority:** This file is a POINTER. Canonical tiering content lives in the HQ knowledge-base K1 SoTs cited below. Per the No-Duplicate-Content Rule (universal-protocols.md), skill references summarize and cite — they do not encode standalone canonical content. When K1 SoTs evolve, this pointer follows automatically because the canonical decisions are NOT duplicated here.

---

## What "tiering" actually means at Sharkitect Digital

There is **no single client tier model**. Three distinct tiering systems run in parallel; each answers a different question. Reach for the right one based on the task.

### 1. Client Journey Tier (T0–T4) — "where is the client in the lifecycle?"

**K1 SoT:** `1.- SHARKITECT DIGITAL WORKFORCE HQ/knowledge-base/strategy/client-journey-tier-framework.md` v1.0

Tracks relationship state from cold visitor to advocate. Drives feature assignment (what experience this client gets) and which playbooks fire on tier transition.

| Tier | State | Key Feature Class |
|---|---|---|
| **T0 Anonymous Visitor** | No contact info | Public website, GBP, ads, lead magnets |
| **T1 Lead** | Contact info submitted, no meeting | Generic branded card, nurture sequence, basic HubSpot record |
| **T2 Prospect** | Meeting scheduled | Pre-meeting prep profile, post-meeting card upgrade, proposal generation |
| **T3 Active Client** | Signed partnership | Fully custom card, monthly KPI reports, client Notion workspace, direct Slack |
| **T4 Advocate** | Producing referrals / case studies | Case study placement, referral partnership, co-marketing |

Use for: feature assignment decisions, transition playbook triggers, "what does this client get?" questions.

---

### 2. Wrapper Choice — "which partnership offering did the client pick?"

**K1 SoT:** `knowledge-base/revenue/pricing-structure.md` v3.2 §2 ("The Two Wrapper Options")

Every active client picks ONE wrapper. Both share the same Project Line behavior below the wrapper; only the wrapper-layer mechanics differ.

| Wrapper | Founding Partner Rate | Standard Rate | Advisory Layer |
|---|---|---|---|
| **Standard AI Transformation Partnership** | $1,500/mo (first 5 clients, 24-mo lock) | $2,500/mo (placeholder, pending pricing sub-step) | Chris (human) — W1 Strategic Advisory (3hr/mo retainer), W2 Monthly KPI Report, W3 Capacity Recommendation Ritual, W4 Transparency Rituals |
| **AIOS** | $2,500/mo Founding / $5,000/mo Standard (locked, inherits from aios-pricing.md v1.5) | — | AIOS agent (continuously running version-locked product line) — same advisory scope, autonomously delivered |

**Mutual exclusivity:** A client cannot be in both wrappers. Pick one. AIOS subscriber + custom build = AIOS wrapper + Project line. Standard Partnership + custom build = Standard wrapper + Project line.

Use for: deal evaluation routing, advisory-layer scope definition, wrapper-vs-project line cost separation on invoices.

---

### 3. Per-Service Capacity Tier (T1/T2/T3 within each service) — "how much volume does this client need?"

**K1 SoT:** `knowledge-base/revenue/pricing-structure.md` v3.2 §7 (per-service scope breakdowns)

Each capacity-tiered service (VDR, RLR, PPM, CPS) has T1/T2/T3 bands that differ in **volume only**, never feature gating. SLW is scope-built and has no capacity tier.

| Service | Type | Capacity Axis |
|---|---|---|
| **VDR** — VoiceDesk AI Receptionist | Capacity-Tiered | Coverage band (after-hours → 24/7) |
| **RLR** — RapidLead Response | Capacity-Tiered | Total email sends/mo |
| **SLW** — SystemLink Workflow Sync | Scope-Built (no tier) | N/A — flat monthly per scope |
| **PPM** — PresencePulse Marketing Engine | Capacity-Tiered | Three independent axes (PPM-unique tier + internal RLR-component tier + internal CPS-component tier) |
| **CPS** — ContentPulse Social Engine | Capacity-Tiered, ADD-ON ONLY | Platforms × posts/week. Requires ≥1 core service live 90+ days. |

**Capacity reassessed monthly** via the W3 wrapper ritual ("pay us less / pay us more" recommendations based on usage).

Use for: capacity recommendation decisions, invoice line construction, per-service usage analysis, upsell/downsell conversations.

---

## Special Pricing Surfaces

### Founding Partner Rate (Early Client Rate Lock)

**K1 SoT:** `knowledge-base/revenue/pricing-structure.md` v3.2 §11

| Element | Detail |
|---|---|
| Eligibility | First 5 signed clients only |
| Rate Lock Duration | 24 months from go-live |
| Partnership Fee Lock | $1,500/mo (Standard wrapper) — anchor verified in pricing sub-step |
| Month 18 Notification | Partnership evolution review — 6 months advance notice |
| Month 24 Transition | Rate moves to current published pricing |

**Terminology rules:** ALWAYS say "Founding Partner Rate" / "partnership evolution review". NEVER say "grandfathering" / "legacy pricing" / "price increase".

### Sharkitect Growth Essentials (Sub-Threshold Offer)

**K1 SoT:** `knowledge-base/revenue/sharkitect-growth-essentials.md` v1.1 + `pricing-structure.md` v3.2 §13

| Element | Detail |
|---|---|
| Setup fee | $2,500 one-time |
| Monthly fee | $250/mo |
| Partnership wrapper fee | WAIVED |
| Term | 12-month minimum |
| Upgrade path | Graduates to full Partnership at month 12+ (transition rate decision pending pricing sub-step) |

---

## Pricing Guardrails (Quick Reference Only — Canonical in K1)

**K1 SoT:** `pricing-structure.md` v3.2 §9, §15, plus `slw-pricing-calculator.md` v1.0 (SLW Complexity Scorecard)

| Guardrail | Rule | Source |
|---|---|---|
| Setup fee minimum floor | $2,500 — no setup drops below this regardless of discount or tier | v3.2 §9 + §15 Rule #12 |
| Partnership Progression Pricing | 0% on 1st system, 25% off setup on 2nd, 40% off setup on 3rd+ (efficiency saving, NOT a discount) | v3.2 §9 |
| 12-Month Expansion Window | Progression discount only if next system added within 12 months of prior go-live | v3.2 §9 |
| Annual Commitment Discount | 15% off monthly recurring — applies to Wrapper + Scope-Built lines ONLY (NOT capacity-tiered lines) | v3.2 §10 |
| Capacity tiers volume-only | NEVER feature gating across tiers; every client at every tier gets standard inclusions | v3.2 §15 Rule #3 |
| No monthly multi-service discounts | Only setup fees receive Progression Pricing; monthly rates are sum-of-projects | v3.2 §15 Rule #4 |
| CPS entry rule | NEVER an entry point; requires ≥1 core service live 90+ days (90-day waiver only for vendor transitions) | v3.2 §15 Rule #1 |
| Lead notification destination cap | Max 2 per service (CRM / email / Slack); additional = à la carte | v3.2 §15 Rule #13 |
| Implementation fees never discounted | Only setup/build fees receive Progression Pricing | v3.2 §9 |

**Capacity-tier dollar amounts and band thresholds:** DEFERRED to pricing sub-step (Phase 3 in progress, 2026-05-13). When pricing locks land in v3.x, this pointer reads automatically because no numbers are duplicated here.

---

## Deal Approval Routing (Pointer)

**K1 SoT:** `knowledge-base/revenue/sales-enablement-playbook.md` and `knowledge-base/governance/financial-operations-guide.md`.

Specific approval thresholds, payment terms, and escalation paths live in those K1 SoTs. This skill's role is to ROUTE to the correct K1 ruleset, not to encode the rules.

---

## What this file is NOT

- NOT a substitute for `pricing-structure.md`. Read v3.2 for the canonical architecture.
- NOT a discount strategy. That's the `pricing-strategy` skill.
- NOT a margin or P&L model. That's the `smb-cfo` skill.
- NOT a sales playbook. That's `sales-enablement-playbook.md` v1.0 in HQ knowledge-base.

## Version pinning

| K1 SoT | Pinned version |
|---|---|
| `pricing-structure.md` | v3.2 (2026-05-13) |
| `client-journey-tier-framework.md` | v1.0 (2026-04-18) |
| `aios-pricing.md` | v1.5 |
| `aios-beta-program.md` | v1.0 |
| `sharkitect-growth-essentials.md` | v1.1 |
| `slw-pricing-calculator.md` | v1.0 |

When a pinned version bumps, drift-detection should flag this pointer for review. The pointer itself doesn't need rewriting unless the K1 SoT's STRUCTURE (not just numbers) changes.
