# Plan: Pricing Structure Restructure — Per-Service Tiers + Partnership Fee

## Context

The current pricing structure uses global partnership tiers (Core $2,500, Growth $4,000, Performance $5,500+, Enterprise $7,000+) that bundle different services together. This creates confusion:
- A client with VDR + SLW-Complex pays Growth ($4,000) + SLW adjustment ($1,200-2,500) = $5,200-6,500, which is more than Performance tier for only 2 systems
- "Core = $2,500 for 1 system" doesn't account for the fact that VDR, RLR, and SLW have very different costs and value
- SLW complexity adjustments on top of tiers create a layered pricing model that's hard to explain

Chris's direction: Each service gets its own internal tier structure (Entry/Mid/Full) with its own setup and monthly pricing. The $500 partnership fee is a flat add-on. No global tiers. Services are priced independently and stacked.

## Previous Work (Completed This Session)

- SLW Pricing Calculator (`knowledge-base/revenue/slw-pricing-calculator.md`) — DONE, committed
- SLW Complexity Scorecard — DONE
- $2,500 universal floor — DONE, updated in pricing-structure.md
- Market analysis — DONE, rates validated as mid-range premium

## Approved Design Decisions

- **Setup discount only** for multi-service clients (Partnership Progression: 25%/40% off setup). No monthly discount for multiple services.
- **$500 partnership fee** is flat, charged once per client. Founding Partners lock at $500 forever. Future clients pay higher as company scales.
- **SLW pricing** stays as-is (calculator-driven, hours x rate). VDR and RLR need per-service tier pricing built.

---

## Deliverables

### 1. Restructure `pricing-structure.md`

**Remove:**
- Global partnership tiers table (Core/Growth/Performance/Enterprise)
- SLW Complexity Adjustments section (replaced by SLW Calculator)

**Replace with:**

**A) Partnership Fee section:**
- $500/mo flat partnership fee, first project only
- Covers: platform cost absorption, quarterly check-ups, strategic consultation, proactive optimization, priority support, system evolution
- Founding Partner lock: $500 forever for first 5 clients
- Future rate: increases as company scales (reviewed after 5+ clients and case studies)

**B) Per-Service Pricing — VDR:**

Using service-definitions.md Entry/Mid/Full configurations as the feature tiers:

| Config | Setup Fee | Monthly Fee | Key Features |
|--------|----------|-------------|--------------|
| Entry | $3,500 | $600/mo | After-hours, 200 min, 1 routing dest, basic capture |
| Mid | $4,500 | $900/mo | After-hours + overflow, 500 min, 3 routing, CRM, booking link |
| Full | $6,000 | $1,250/mo | 24/7, unlimited min, unlimited routing, calendar sync, escalation |

*Setup fee rationale: Entry ~28 hrs x $125, Mid ~30 hrs x $150, Full ~35 hrs x $170. Build timelines 1-4 weeks per service-definitions.*
*Monthly fee rationale: blended monthly hours x rate + platform costs. Entry ~2 hrs, Mid ~3 hrs, Full ~4 hrs.*
*Overage: $0.05/min above included monthly ceiling.*

**Scaling up within VDR (and RLR — same rule applies to all pre-built services):**
- Monthly fee changes to the new tier's rate immediately (client pays the difference)
- **Upgrade setup fee** = difference between current and new tier setup fees (covers the incremental build: adding CRM, more channels, etc.)
- **New client going directly into Mid or Full:** Pays the full tier setup fee
- **No upgrade setup fee** if scaling up doesn't require new build work (just config changes)
- **$2,500 minimum floor** still applies to any setup fee (new or upgrade)

**C) Per-Service Pricing — RLR:**

| Config | Setup Fee | Monthly Fee | Key Features |
|--------|----------|-------------|--------------|
| Entry | $4,000 | $700/mo | 75 leads/mo, 1 channel, 3-touch, 7-day sequence |
| Mid | $5,500 | $1,000/mo | 200 leads/mo, SMS+Email, 6-touch, CRM, 14-day |
| Full | $7,000 | $1,400/mo | 500 leads/mo, omnichannel, 10-touch, attribution, 30-day |

*RLR is more expensive than VDR due to copywriting, multi-touch coordination, and testing complexity (documented in service-definitions.md).*
*Overage: $1.50/lead above included monthly ceiling.*

**D) Per-Service Pricing — SLW:**
- Defer to SLW Pricing Calculator (`slw-pricing-calculator.md`)
- **The calculator produces CLIENT-FACING prices** — not internal cost tracking
- Scorecard determines tier → hours x rate = setup fee (what you charge the client)
- Monthly = blended hours x tier rate (what you charge the client)
- Universal floor: $2,500 setup / $250 monthly maintenance
- No fixed tier table — every SLW is custom-calculated
- Internal pricing back sheet provides line-item breakdown if client asks "how'd you get to this number?"

**E) Per-Service Pricing — CPS (Add-On, unchanged):**
- $2,500 setup / $750/mo (3 platforms)
- +$500/mo per additional platform (max 5)
- Still requires 90 days post core system go-live

**F) Client Monthly Total:**
```
Total Monthly = $500 partnership (first project only, already charged) 
              + sum of individual service monthly fees
```

Example: Client with VDR-Mid + RLR-Entry + SLW-Medium
= $500 + $900 + $700 + ~$495 = $2,595/mo

**G) Standalone SaaS Pricing — update to match per-service model:**
- Monthly rates already per-service (keep as-is, already aligned)
- Setup fees: standard per-service setup + 25% premium (keep)
- No partnership fee (standalone doesn't include partnership)

### 2. Update `service-definitions.md`
- Remove references to global partnership tiers
- Add note that each service has its own pricing tiers in `pricing-structure.md`

### 3. Update cross-referencing documents
- `partnership-agreement-template.md` — update fee structure references
- `sales-enablement-playbook.md` — update how pricing is presented
- `client-onboarding-framework.md` — update pricing step
- `proposal-template-slw.md` — verify alignment
- `DOCUMENT-MAP.md` and `INDEX.md` — update pricing descriptions

### 4. Update `slw-pricing-calculator.md`
- Remove the $500 partnership base from the monthly formula (it's now in the global partnership fee section)
- First project monthly = blended hours x tier rate (floor $250)
- Additional projects = same formula
- No distinction between first/additional projects in the calculator — partnership fee is handled separately

---

## Resolved Decisions

**1. VDR/RLR pricing:** Using estimates as v1.0. Mark as "pending calibration after 3+ builds." Chris will refine after real build data.

**2. Standalone SaaS monthly rates:** Will adjust upward so standalone rates are always higher than partnership rates for equivalent configurations. Standalone = no partnership services, so it should cost more per-service.

**3. Tier naming:** Using Entry/Mid/Full (from service-definitions.md). Clean break from old global tier names.

**4. Two upgrade models — pre-built vs custom:**

**Pre-built services (VDR, RLR, CPS) — standard SaaS upgrade model:**
- Upgrade setup fee = difference between current tier and new tier setup fees
- Upgrade monthly = difference between current tier and new tier monthly fees
- If upgrade doesn't require new build work (just feature unlocks/config), no upgrade setup fee — only monthly changes
- Example: RLR Entry ($4,000 setup, $700/mo) → Mid ($5,500 setup, $1,000/mo) = $1,500 upgrade setup + $300/mo increase

**Custom service (SLW) — calculator-driven, no fixed upgrade pricing:**
- Every add-on, expansion, or modification is scoped and priced via the SLW Pricing Calculator
- Adding invoice tracking to an existing Check Distribution build = run calculator for the incremental scope
- **Re-score the INCREMENTAL work** through the Complexity Scorecard to determine its tier and rate
  - If the add-on is a simple data flow (scores Standard at $125/hr), price at Standard rate — even if the original build was Complex
  - If the add-on requires restructuring existing complex workflows (scores Complex at $215/hr), price at Complex rate
  - The original build's tier is already priced and paid for; the add-on stands on its own for scoring
- Monthly may increase based on recalculated blended hours for the expanded system
- There are no "tiers" to upgrade between — it's always scope-driven
- $2,500 setup floor still applies to each new SLW scope addition

**5. SLW Calculator is CLIENT-FACING pricing:** The calculator produces the actual numbers charged to the client, not just internal cost tracking. The pricing back sheet is the internal breakdown available if client asks.

---

## Verification

- [ ] Calculate FF's actual pricing through the new model and verify it matches what was charged
- [ ] Verify a hypothetical 2-service client's total makes sense (not too high, not too low)
- [ ] Verify standalone rates are higher than partnership rates for equivalent configurations
- [ ] Verify all cross-referenced documents are consistent
- [ ] Verify the $2,500 setup floor still applies across all services
- [ ] Verify Partnership Progression discounts still work (25%/40% off setup, $2,500 post-discount floor)

---

## Files to Modify

| File | Action |
|------|--------|
| `knowledge-base/revenue/pricing-structure.md` | Major restructure — remove global tiers, add per-service pricing |
| `knowledge-base/revenue/slw-pricing-calculator.md` | Remove $500 partnership from monthly formula |
| `knowledge-base/revenue/service-definitions.md` | Remove global tier references |
| `knowledge-base/DOCUMENT-MAP.md` | Update pricing-structure description |
| `knowledge-base/INDEX.md` | Update pricing entries |
| Other cross-referenced docs | Verify alignment (may need minor updates) |
