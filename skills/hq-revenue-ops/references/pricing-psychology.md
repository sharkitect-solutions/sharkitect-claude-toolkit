# Pricing Psychology for Sharkitect Service Proposals

**Status:** active | **Last rebuilt:** 2026-05-13 | **Reason:** Drift correction per `wr-hq-2026-05-13-001` — prior version contained fabricated service names ("Virtual Delivery Room", "Revenue Lifecycle Revenue", "Sharkitect Live Web", "Client Platform Services") that do not match the v3.0 architecture. Universal behavioral-economics principles unchanged; all Sharkitect-specific examples replaced with real services and v3.2-aligned mechanics.

**Authority pattern:** Universal behavioral-economics principles are timeless cross-domain — restated here. Sharkitect-specific application examples reference the K1 SoTs cited inline; no canonical pricing decisions are duplicated. When `pricing-structure.md` evolves, the examples remain structurally correct because they cite real services and real mechanics rather than encoding specific dollar amounts.

---

## 1. Anchoring Effect (Tversky & Kahneman, 1974)

The first number a prospect sees becomes their reference point for all subsequent evaluation. Higher anchors shift perceived value upward even when the prospect knows the anchor is arbitrary.

**Application to proposals**: Always present the highest-tier option first. Capacity-tier proposals open with T3 (highest volume), step down to T2, then T1. The middle tier reads as the obvious value rather than as a stretch.

### Sharkitect-specific anchor sequences (services per `pricing-structure.md` v3.2 §7)

| Service | Capacity Type | Anchor Sequence (high → low) |
|---|---|---|
| **VDR** (VoiceDesk AI Receptionist) | Coverage band | T3 (24/7/365 full coverage) → T2 (after-hours + weekends + business-hours overflow) → T1 (after-hours + weekends only) |
| **RLR** (RapidLead Response) | Sends/mo band | T3 (high volume) → T2 (mid volume) → T1 (low volume) |
| **PPM** (PresencePulse Marketing Engine) | SAP footprint × blog cadence × backlinks | T3 (statewide/multi-region, ~75 SAPs) → T2 (regional, ~30 SAPs) → T1 (local single-market, ~10 SAPs) |
| **CPS** (ContentPulse Social Engine) | Platforms × posts/week | T3 (4-5 platforms, 5 posts/wk each) → T2 (2-3 platforms, 3-5 posts/wk each) → T1 (single platform, 3-5 posts/wk) |
| **SLW** (SystemLink Workflow Sync) | Scope-built (no tier) | Anchor on Complexity tier per `slw-pricing-calculator.md` v1.0 (Complex → Medium → Standard) |

### Wrapper-level anchor

When the prospect's first exposure is the wrapper conversation, the anchor sequence is **AIOS Standard rate → AIOS Founding rate → Standard Partnership Standard rate → Standard Partnership Founding rate**. The Founding Partner Rate frames as preserved value, not a deal-of-the-day discount. Terminology rules: ALWAYS "Founding Partner Rate" / NEVER "grandfathered" or "legacy pricing" (per `pricing-structure.md` v3.2 §11).

**Rule**: The anchor option must be a real, deliverable package. Fake anchors destroy trust when discovered. Every tier above must actually exist as a sellable offering.

---

## 2. Loss Aversion (Kahneman & Tversky, 1979)

Losses are felt roughly 2x more intensely than equivalent gains. A $500 discount feels less motivating than the prospect of losing $500 in value they already expect.

**Application to discounting**: Never frame discounts as "save money." Frame the full price as including value that would be lost without it.

- ❌ "We can take $500 off the monthly."
- ✅ "The full package includes the W3 capacity-recommendation ritual and weekly status updates. Removing those saves $X but means you lose the monthly 'pay us less' optimization muscle."

### Sharkitect-specific loss-aversion framing

**Wrapper inclusions to frame as loss-on-removal** (Standard Partnership Wrapper per `pricing-structure.md` v3.2 §3):
- W1 Strategic Advisory (3hr/mo retainer of Chris's time) — "you lose direct strategic access to the architect"
- W2 Monthly KPI Report + check-in — "you stop seeing your cross-service KPIs consolidated"
- W3 Capacity Recommendation Ritual — "you lose the 'pay us less' optimization muscle that keeps you on the right tier each month"
- W4 Transparency Rituals — "you lose the quarterly business-health rollup and annual relationship review"

**Renewal / downgrade conversations**: Enumerate what the client LOSES on tier downgrade, not what they save. For an RLR T2 client considering T1, the loss-aversion frame is: "Dropping to T1 means your monthly send capacity falls from [T2 band] to [T1 band] — your follow-up sequence depth or your lead intake throughput has to give. Which one are you willing to lose?"

**Cancellation framing**: For an active VDR client, the loss is concrete — "your AI receptionist stops covering [their actual coverage band] and inbound calls during that window go unanswered or roll to voicemail." The framing references real coverage they've come to depend on.

---

## 3. Prospect Theory and Bundle Framing (Kahneman & Tversky, 1979)

People evaluate outcomes relative to a reference point, not in absolute terms. Gains show diminishing sensitivity (the jump from $0 to $100 feels bigger than $900 to $1,000).

**⚠️ IMPORTANT — Sharkitect-specific constraint**: There are **no monthly discounts for multiple services** per `pricing-structure.md` v3.2 §15 Rule #4. Bundle discounts apply to **setup fees only**, via Partnership Progression Pricing (25% off setup on 2nd system, 40% off setup on 3rd+) — §9. Do NOT frame proposals with fabricated monthly bundle savings; they violate the v3.2 architecture.

### Where prospect-theory framing legitimately applies at Sharkitect

**Partnership Progression Pricing** (§9): Frame as one consolidated efficiency saving across an expansion sequence, not as three separate per-service discounts.

- ❌ "$X off setup on RLR, $Y off setup on PPM, $Z off setup on CPS."
- ✅ "Your three-system expansion saves $[X+Y+Z] in setup efficiency because we're already in your infrastructure — that's one consolidated saving across the year."

**Annual Commitment Discount** (§10): The 15% annual benefit applies to Partnership Wrapper + Scope-Built (flat-fee) lines ONLY. Frame the savings as one annualized number for cognitive impact: "Annual commitment on your Standard Partnership Wrapper saves $[12 × rate × 0.15] — that crosses the annualized threshold that justifies the commitment math."

**Note**: Capacity-Tiered lines have NO annual discount because the **capacity flex IS the value lever** for those (§10). The two discount mechanisms operate on two distinct layers without stacking conflict.

---

## 4. Decoy Pricing (Asymmetric Dominance Effect)

When a third option is clearly worse than one target but comparable to another, people shift preference toward the target. The decoy makes the target look obviously superior.

**Application to Sharkitect proposals**: Three-option capacity-tier proposals naturally fit this pattern when constructed correctly. The capacity bands themselves create the asymmetric dominance.

### RLR example (volume axis = total email sends/mo per §7.2)

| Option | Position | What it is |
|---|---|---|
| **T1 — Low volume band** | Decoy | Standard inclusions + low send capacity. Honest entry point; rarely the right answer for a real revenue-response operation. |
| **T2 — Mid volume band** | Target | Same standard inclusions + comfortable send capacity for typical mid-funnel cadence. Best-fit for most real engagements. |
| **T3 — High volume band** | Anchor | Same standard inclusions + high send capacity. For aggressive multi-touch sequences and high inbound volume. |

The gap T1 → T2 is small in price but materially expands capacity headroom; the gap T2 → T3 is larger in price but adds capacity many clients won't immediately use. The middle tier reads as the obvious value.

### Wrapper-level decoy

The two wrapper options (Standard Partnership vs AIOS) are NOT a decoy structure — they target different buyers (human-advisory vs AI-advisory). Treat them as parallel offerings per §2, not as a hierarchy.

**Key**: Never construct fake decoys. Every option must be a real, deliverable package per its scope in `pricing-structure.md` v3.2 §7. Manufactured decoys destroy trust the moment a prospect compares notes with another buyer.

---

## 5. Endowment Effect (Thaler, 1980)

Once people possess something, they value it more than they did before owning it. Free trials convert not because of rational evaluation but because giving up what they already have triggers loss aversion.

**Application to upsells**: Once a client is in an active engagement, they psychologically "own" their current automation. Upsell conversations should never start with "here's what you could add." Start with "here's what your current setup is already doing for you" — then show the natural next step.

### Sharkitect-specific endowment sequences

**Within-service capacity upsell** (T1 → T2 → T3):
- Lead with the W2 Monthly KPI Report numbers: "Your VDR handled [X] calls last month at T1 (after-hours + weekends). Coverage stops at 5pm weekdays — the data shows [Y] missed calls during business hours rolling to voicemail. T2 catches those without you doing anything."
- Anchor to the W3 capacity-recommendation output already produced: "We're flagging this from your data, not pitching it."

**Cross-project expansion** (adding a second/third service line):
- Anchor to the wrapper they already pay for: "You're already paying for the Partnership Wrapper. Adding RLR doesn't change the wrapper — it adds a single Project Line."
- Anchor to Partnership Progression Pricing (§9): "Because we're already in your infrastructure, the 2nd system setup carries a 25% efficiency reduction. We're not negotiating; this is structural to how we work."

**Wrapper upgrade** (Standard Partnership → AIOS):
- The endowment is the existing advisory relationship. The pitch is augmentation, not replacement: "Your advisory layer continues; AIOS adds continuously-running coverage on top of the 3hr/mo retainer."

**Cancellation/downgrade pre-emption**: Run a value audit using the W2 Monthly KPI Report data and the W4 quarterly business-health summary. These artifacts are wrapper deliverables (§3); they exist whether or not the client is considering cancellation. The endowment effect anchors the client to those numbers — they're harder to walk away from than the cost line on the invoice.

---

## Pricing Psychology Checklist

Run through before finalizing any proposal:

- [ ] Highest-price option listed FIRST (anchoring)
- [ ] Service names accurate to `pricing-structure.md` v3.2 (VDR / RLR / SLW / PPM / CPS — never invented variations)
- [ ] Capacity-tier framing references the actual volume axis for the service (coverage / sends / SAPs / platforms × posts) per §7
- [ ] Discounts framed as preserved value, not saved money (loss aversion)
- [ ] No fabricated monthly bundle discounts — Sharkitect has none per §15 Rule #4
- [ ] Partnership Progression Pricing framed as efficiency saving across the expansion sequence, NOT per-service negotiation (§9)
- [ ] Annual Commitment 15% framed as annualized impact, applied ONLY to wrapper + scope-built lines (§10)
- [ ] Three-tier capacity proposal uses the service's real T1/T2/T3 bands as the decoy structure (§7)
- [ ] Upsell anchors to W2 / W3 / W4 deliverables already produced (endowment)
- [ ] $2,500 setup floor honored on every quote (§9 + §15 Rule #12)
- [ ] Founding Partner Rate terminology compliant — "Founding Partner Rate" / "partnership evolution review" only (§11)
- [ ] CPS entry rule honored — never the entry point; requires ≥1 core service live 90+ days (§15 Rule #1)
- [ ] Verbal pricing NEVER given — written proposal format only (anti-pattern: Handshake Pricing per SKILL.md)

---

## Version pinning

| K1 SoT | Pinned version |
|---|---|
| `pricing-structure.md` | v3.2 (2026-05-13) |
| `slw-pricing-calculator.md` | v1.0 |
| `client-journey-tier-framework.md` | v1.0 |
| `aios-pricing.md` | v1.5 |

When a pinned version bumps and the structural mechanics change (not just numbers), drift-detection should flag this file for review. Specific dollar amounts and band thresholds locking in the v3.x pricing sub-step do NOT require this file to be rewritten — the examples reference mechanics by name, not number.
