# Pricing Psychology for Service Proposals

Cross-domain behavioral economics applied to Sharkitect Digital deal construction.

## 1. Anchoring Effect (Tversky & Kahneman, 1974)

The first number a prospect sees becomes their reference point for all subsequent evaluation. Higher anchors shift perceived value upward even when the prospect knows the anchor is arbitrary.

**Application to proposals**: Always present the highest-tier option first. When a prospect sees the $8,000/mo Enterprise package before the $2,500/mo Growth package, the Growth package feels like a bargain rather than a significant expense.

| Service Line | Anchor Sequence |
|-------------|----------------|
| VDR (Virtual Delivery Room) | Full AI ops suite ($7,500) -> Automation package ($4,000) -> Starter ($1,500) |
| RLR (Revenue Lifecycle Revenue) | Full-funnel automation ($6,000) -> Pipeline management ($3,000) -> Lead scoring only ($1,200) |
| SLW (Sharkitect Live Web) | Enterprise web platform ($5,500) -> Growth site ($2,800) -> Landing page pack ($900) |
| CPS (Client Platform Services) | Managed platform + AI ($8,000) -> Platform setup + support ($4,500) -> Setup only ($2,000) |

**Rule**: The anchor option must be a real, deliverable package. Fake anchors destroy trust when discovered.

## 2. Loss Aversion (Kahneman & Tversky, 1979)

Losses are felt roughly 2x more intensely than equivalent gains. A $500 discount feels less motivating than the prospect of losing $500 in value they already expect.

**Application to discounting**: Never frame discounts as "save $500." Instead, frame the full price as including value that would be lost without it.

- BAD: "We can take $500 off the monthly."
- GOOD: "The full package includes priority SLA and quarterly reviews. Removing those saves $500 but means issues wait 48 hours instead of 4."

**Application to renewals**: When a client considers downgrading, enumerate what they lose (specific features, SLA levels, dedicated contacts) rather than what the lower tier costs. The pain of losing their current setup outweighs the pleasure of saving money.

**Sharkitect-specific**: For VDR clients, frame cancellation as "your 47 automated workflows stop running and manual fallback takes 12+ hours/week." The loss of automation time hits harder than the monthly fee.

## 3. Prospect Theory and Bundle Framing (Kahneman & Tversky, 1979)

People evaluate outcomes relative to a reference point, not in absolute terms. Gains show diminishing sensitivity (the jump from $0 to $100 feels bigger than $900 to $1,000).

**Application to bundle framing**: Frame bundles as a single savings amount, not per-service discounts. The perceived value of one $600 savings is greater than three separate $200 savings because each individual saving falls on a flatter part of the value curve.

- BAD: "Save $200 on workflows, $200 on integrations, $200 on management."
- GOOD: "Bundle all three and save $600/mo (that's $7,200/year back in your pocket)."

**Application by service line**:
- VDR + RLR bundle: "Full revenue operations stack — saves $800/mo vs buying separately" (one big number)
- SLW + CPS bundle: "Complete digital presence package — saves $650/mo vs a la carte" (one big number)

**Rule**: Always annualize savings when the number is large enough. $600/mo becomes $7,200/year, which crosses a psychological threshold for SMB decision-makers.

## 4. Decoy Pricing (Asymmetric Dominance Effect)

When a third option is added that is clearly worse than one target but comparable to another, people shift preference toward the target option. The decoy exists to make the target look obviously superior.

**Application to proposal construction**: Structure three-option proposals so the middle option is the target and the lowest option is the decoy that makes the middle look like the obvious choice.

| Option | Price | Includes | Purpose |
|--------|-------|----------|---------|
| Starter (decoy) | $1,500/mo | Setup + 5 workflows, email support, no SLA | Makes Growth look like a steal |
| Growth (target) | $2,500/mo | Setup + 15 workflows, Slack support, 8-hr SLA, monthly reviews | Best value perception |
| Enterprise | $5,000/mo | Unlimited workflows, dedicated manager, 4-hr SLA, weekly reviews | Anchor |

**Key**: The gap between Starter and Growth is small in price ($1,000) but large in value (3x workflows, SLA, reviews). The gap between Growth and Enterprise is large in price ($2,500) but incremental in value. This steers most buyers to Growth.

**Sharkitect-specific**: For RLR deals, include a "lead scoring only" tier at $1,200 that lacks any automation. The $1,800 step up to full pipeline management ($3,000) looks small against the value of actual automation vs manual work.

## 5. Endowment Effect (Thaler, 1980)

Once people possess something, they value it more than they did before owning it. This is why free trials convert — not because people rationally evaluate value, but because giving up what they already have triggers loss aversion.

**Application to upsells**: Once a client is on a Tier 3 or Tier 2 plan, they psychologically "own" their current automations and workflows. Upsell conversations should never start with "here's what you could add." Start with "here's what your current setup is already doing for you" — then show the natural next step.

**Upsell sequence by tier**:
1. Tier 3 -> Tier 2: "Your 5 workflows saved you ~20 hours last month. Adding 10 more at Growth tier saves another 40 hours — triple the impact for only 67% more cost."
2. Tier 2 -> Tier 1: "Your pipeline automation closed 8 deals last quarter. Strategic tier adds AI scoring that identifies your top 20% of leads, so your team stops wasting time on the other 80%."
3. Tier 1 -> Tier 0: "Your systems run your operations now. Enterprise tier adds a dedicated architect who ensures zero downtime and proactive optimization — you stop managing tech entirely."

**Sharkitect-specific**: For CPS clients, run a "value audit" at month 3 showing exactly what the platform has done (tickets resolved, hours saved, uptime stats). The endowment effect anchors them to these numbers, making cancellation psychologically expensive.

## Pricing Psychology Checklist

Run through before finalizing any proposal:

- [ ] Highest-price option is listed FIRST (anchoring)
- [ ] Discounts are framed as lost value, not saved money (loss aversion)
- [ ] Bundle savings shown as one total number, annualized if >$400/mo (prospect theory)
- [ ] Three options with clear decoy making target obvious (asymmetric dominance)
- [ ] If upsell: current value enumerated BEFORE new value introduced (endowment effect)
- [ ] No discount exceeds 20% off list (guardrail — see SKILL.md)
- [ ] All options stay above minimum margin for their service lines (guardrail)
- [ ] Verbal pricing NEVER given — always present in written proposal format (anti-pattern: Handshake Pricing)
