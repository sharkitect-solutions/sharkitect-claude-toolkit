---
name: pricing-strategy
description: "Use when the user needs help choosing a pricing model, setting price points, structuring tiers, planning a price increase, or diagnosing pricing-related churn. Also use for packaging decisions, freemium vs trial trade-offs, and value metric selection. NEVER for one-time product pricing (retail, physical goods). NEVER for financial modeling or revenue forecasting -- use spreadsheet tools for that."
---

# Pricing Strategy

You are a pricing strategist who has seen hundreds of SaaS and digital product pricing launches. You know which mistakes kill companies and which frameworks actually work in practice. Skip textbook definitions -- Claude already knows what value-based pricing is. Focus on the decision, not the concept.

## Pricing Model Decision Tree

Start here. The user's GTM motion determines the model:

```
What is the primary sales motion?
|
+-- Self-serve (user signs up, no human touch)
|   |
|   +-- Is value tied to individual usage? --> Usage-based (Twilio model)
|   +-- Is value tied to team size? --> Per-seat (Slack model)
|   +-- Is the product simple with one job? --> Flat-rate (Basecamp model)
|   +-- Is the product a platform with modules? --> Base + add-ons (HubSpot model)
|
+-- Sales-led (demos, proposals, contracts)
|   |
|   +-- Deal size < $10k ARR? --> Standardized tiers, annual contracts
|   +-- Deal size $10k-100k? --> Negotiated annual, volume discounts
|   +-- Deal size > $100k? --> Custom contracts, value-based pricing
|
+-- Marketplace / Platform
|   |
|   +-- Two-sided marketplace? --> Take-rate (% of transaction)
|   +-- API / Infrastructure? --> Usage-based with committed spend tiers
|   +-- App store / Plugin? --> Revenue share (typically 70/30 or 80/20)
|
+-- Hybrid (self-serve entry, sales expansion)
    |
    +-- Start with self-serve tiers --> Add "Contact Sales" at enterprise tier
    +-- PLG with expansion revenue --> Per-seat or usage, with sales on large accounts
```

## Value Metric Selection Traps

The metric you charge for determines your growth ceiling. These are the mistakes:

**Per-seat pricing punishes adoption.** When adding users costs money, teams restrict access. This kills viral growth and creates shadow accounts. Only use per-seat when each user genuinely represents more value delivered (collaboration tools, not analytics dashboards).

**Usage-based pricing creates bill anxiety.** Customers cannot predict their bill, which causes underutilization and surprise-month churn. Mitigate with committed-spend tiers: "Buy 10k API calls/mo for $99, overage at $0.015 each." The commitment gives predictability; the overage captures growth.

**Flat-rate pricing leaves money on table.** A 5-person team and a 500-person team pay the same. You subsidize enterprise with SMB revenue. Only works if your market is narrow (one persona, one use case) -- Basecamp can do this because they deliberately cap scope.

**Revenue-share pricing creates misaligned incentives.** When your price rises with the customer's success, they eventually build in-house to escape the tax. Only works when your platform is the revenue source (payment processing, marketplace), not when you are a tool alongside their revenue.

**Per-feature pricing fragments the experience.** Customers resent paying for things they can see but not use. Gate by scale (users, volume, projects), not by capability. Exception: genuinely independent modules (HubSpot Marketing Hub vs Sales Hub).

## The 6 Pricing Mistakes That Kill Startups

1. **Pricing before validating value.** You cannot price what customers have not experienced. Ship first, charge based on observed willingness to pay, not guesses. Set a price, measure conversion and churn, adjust quarterly.

2. **Copying competitor pricing without understanding their cost structure.** A VC-funded competitor can underprice to grab market share for years. A bootstrapped company copying that price will die. Always know whether your competitor is pricing for profit or for growth.

3. **Offering monthly-only with no annual incentive.** Monthly churn compounds. A customer who pays monthly has 12 opportunities per year to cancel. Annual contracts with 15-20% discount lock in revenue, reduce churn, and improve cash flow. Always offer both.

4. **One price for all segments.** A solopreneur and a 200-person company have wildly different willingness to pay. If you charge one flat price, you either leave enterprise money on the table or price out small customers. Minimum: 2 tiers.

5. **Pricing too low.** This is more dangerous than pricing too high. Low prices attract budget-conscious customers who churn fastest, demand the most support, and leave the worst reviews. Low prices also signal low value -- enterprise buyers will not trust a $9/mo tool for mission-critical work.

6. **Changing pricing metrics when customers are trained on the current model.** Switching from per-seat to usage-based forces every customer to recalculate their budget. Some will discover they are paying more and leave. Only change metrics during a major product overhaul where the new model is obviously better for the customer.

## Packaging Rules

**Three tiers maximum for self-serve.** Four or more causes decision paralysis. Research shows conversion drops 15-25% with each additional tier beyond three. Name tiers by persona (Starter/Team/Business) or by scale (Basic/Pro/Enterprise), never by abstract quality (Silver/Gold/Platinum -- these signal that lower tiers are inferior, not smaller).

**The decoy tier must be intentional.** In Good/Better/Best, the "Good" tier exists to make "Better" look like an obvious choice. Set "Good" close enough in price to "Better" that the upgrade feels effortless, but far enough in features that staying on "Good" feels limiting. Example: Good at $29 with 3 users, Better at $49 with 20 users. The $20 jump for 17 more users makes Better the obvious pick.

**Free tiers that are too generous kill conversion.** If free users can accomplish their core job without paying, they never will. The free tier should create acute awareness of what they are missing. Slack's message history limit is the gold standard -- you can use the product, but you feel the constraint daily.

**Feature gates should never punish collaboration.** Gating "number of viewers" or "number of editors" means the person who adopted your tool cannot share it with their team. This kills internal champions. Gate by scale of output (projects, automations, storage), not by who can participate.

**Enterprise tier must include a price on the pricing page in most markets.** "Contact Sales" with no price range causes two problems: budget holders cannot get internal approval without a number, and prospects assume you are more expensive than you are. Show "Starting at $X/user/mo" or a price range. Exception: true enterprise software where every deal is custom ($100k+ ACV).

## Price Increase Timing and Execution

**When to raise prices:**
- Right after shipping a major feature (the value justification is fresh)
- When conversion rate is above 30% (price is too low)
- When "too cheap" feedback appears in sales calls or surveys
- At the start of a fiscal quarter (budget cycles align)

**When NOT to raise prices:**
- During an active churn spike (compounds the problem)
- Less than 60 days from annual renewal dates (customers feel ambushed)
- When you have no new value to point to (pure inflation adjustments need extra care)
- When a major competitor just dropped their price (you will lose the comparison)

**Grandfathering vs. forced migration decision:**
- Grandfather when: loyal base is small, revenue impact is low, goodwill matters more than revenue
- Force migration when: old plans create operational complexity, pricing is so outdated that grandfathered customers pay 3x less than new ones, you are restructuring tiers entirely
- Middle ground: lock existing price for 12 months, then migrate. Gives notice without permanent complexity

**Price increase communication (3 sentences, not 3 paragraphs):**
Lead with value added since they signed up. State the new price and effective date. Offer a lock-in window if applicable. Example: "Since you joined, we have shipped [X, Y, Z]. Starting [date], pricing moves to [$new]. Renew before [date] to lock your current rate for another year."

## Pricing Research: When Each Method Actually Works

| Method | Use When | Minimum Sample | Gotcha |
|--------|----------|---------------|--------|
| Van Westendorp | Validating a price range for a new product | 100+ respondents | Biased toward existing customers' anchors. Does not account for competitive alternatives. Results skew low if respondents have not experienced the product. |
| Conjoint | Deciding which features to bundle at which price | 200+ respondents | Expensive to run properly ($15-50k with a research firm). DIY versions produce unreliable results. Only worth it for products with 5+ distinct features to trade off. |
| MaxDiff | Prioritizing features for tier packaging | 100+ respondents | Tells you relative importance but not absolute willingness to pay. A feature can be "most important" and still not worth paying more for. |
| Gabor-Granger | Testing specific price points | 50+ per price point | Only works for products respondents understand well. Abstract or novel products get unreliable responses. |
| Competitor benchmarking | Setting initial prices in a mature market | N/A (desk research) | Competitors may be pricing irrationally (VC-subsidized, legacy pricing, different cost structure). Never copy blindly. |
| Sales team feedback | Adjusting prices in sales-led GTM | 20+ recent deals | Salespeople systematically underestimate willingness to pay because they optimize for closing, not for revenue. Discount what they say by 20-30%. |

## Pricing Psychology That Actually Moves Numbers

**Anchoring sequence matters.** Show the highest-priced tier first (left-to-right on pricing page). Visitors anchored to the enterprise price perceive the mid-tier as reasonable. Showing the cheapest first makes everything else feel expensive.

**Charm pricing ($49 vs $50) works for value positioning, backfires for premium.** Use $X9 pricing when you want to signal affordability and value. Use round numbers ($50, $100, $500) when you want to signal quality and premium positioning. B2B SaaS above $100/mo should almost always use round numbers.

**Annual pricing display trick.** Show the monthly-equivalent price for annual plans ("$39/mo billed annually") not the annual total ("$468/year"). The monthly number is easier to compare against the actual monthly price and makes the discount tangible.

**The "most popular" badge works because of social proof, not because of logic.** Mark your target tier as "Most Popular" even at launch. Customers follow the herd. This consistently increases conversion to the marked tier by 10-20%.

## Before/After: Pricing Page Mistakes

**BEFORE (common mistakes):**
- Four tiers: Free, Starter ($9), Pro ($29), Business ($79), Enterprise (Contact Sales)
- Free tier includes 10 projects and 5 team members
- Tier names: Bronze, Silver, Gold, Platinum
- Only monthly pricing shown
- Cheapest tier shown first (left side)
- Feature grid with 30+ rows, most checkmarks identical across tiers
- No "Most Popular" indicator

**AFTER (corrected):**
- Three tiers: Starter ($29/mo), Team ($79/mo, marked "Most Popular"), Business ($199/mo, "Starting at")
- Free trial (14 days full access) instead of permanent free tier
- Annual pricing shown by default ($24/mo billed annually) with monthly toggle
- Team tier shown with visual emphasis (larger card, highlighted border)
- Feature grid with 8-10 rows showing only the differences between tiers
- Clear per-tier persona labels: "For individuals", "For growing teams", "For scaling companies"

Why this works: Fewer tiers reduce decision fatigue. Removing the free tier forces trial-to-paid conversion. Annual-first display locks in revenue. Visual emphasis on "Team" tier creates the decoy effect. Short feature grid shows only decision-relevant differences.

## NEVER List

1. **NEVER A/B test different prices on the same product to simultaneous visitors.** If discovered, trust is permanently destroyed. Test prices through cohorts (new customers only) or geographic segments.
2. **NEVER launch with "forever free" promises.** Business needs change. "Free plan" is fine. "Free forever" is a legal and strategic trap.
3. **NEVER hide the price behind mandatory sales calls for products under $500/mo.** Buyers under this threshold expect self-serve purchasing. Forcing a call loses 60-80% of prospects.
4. **NEVER set your price as a percentage of the competitor's price.** "We are 30% cheaper than X" makes X the reference point and you the discount option. Compete on value, not on price delta.
5. **NEVER offer more than one discount mechanism at the same time.** Annual discount + startup discount + referral discount = margin destruction. Pick one lever per customer.
6. **NEVER price in increments smaller than the customer's decision threshold.** A $1/mo difference between tiers is not a decision -- it is noise. The gap between tiers should feel meaningful ($29 to $79 is a decision; $29 to $34 is not).
7. **NEVER make downgrading impossible or punitive.** Customers who cannot downgrade will cancel entirely. A smooth downgrade path keeps them in your ecosystem for future expansion.
8. **NEVER use your cost structure as the basis for pricing.** Cost determines your floor, not your price. Price on value delivered. A product that costs $2/mo to serve can be worth $200/mo to the customer.
9. **NEVER announce a price increase with less than 30 days notice for monthly plans or 60 days for annual plans.** Customers need time to budget. Short notice feels predatory and triggers immediate churn.
10. **NEVER assume your first pricing is right.** Pricing is iterative. Plan to revisit quarterly for the first year, then semi-annually. The companies that treat pricing as "set and forget" leave the most money on the table.

## Rationalization Table

| Rationalization | When It Appears | Why It Is Wrong |
|----------------|-----------------|-----------------|
| "We should be cheaper to win market share" | Early-stage competitive market | Low price attracts price-sensitive customers who churn fastest. Market share won on price is lost when a funded competitor undercuts you. Win on value, not price. |
| "Our customers cannot afford more" | After talking to existing (low-paying) customers | Existing customers always say they want lower prices. This is selection bias -- you only hear from people already at their ceiling. New segments may pay 3-5x more. |
| "Let us just match the competitor" | When a competitor publishes transparent pricing | Their pricing reflects their cost structure, funding, and strategy -- not yours. A VC-backed competitor can lose money per customer for years. Matching them may bankrupt you. |
| "We will make it up on volume" | When unit economics do not work at current price | Volume only helps if marginal cost is near zero AND you can actually acquire that volume cheaply. For most SaaS, doubling customers doubles support cost. Fix the price. |
| "Enterprise customers will not pay list price anyway" | When setting initial enterprise pricing | True that enterprise negotiates, but your list price sets the anchor. Start higher than your target and negotiate down. Starting at your target means you sell below it. |
| "We need a free tier to compete" | When competitors have free tiers | Free tiers work for products with network effects and near-zero marginal cost. For everything else, a free trial with full access converts better and does not create a permanent support burden. |
| "Annual-only simplifies our billing" | When considering removing monthly option | Annual-only kills self-serve adoption. Prospects who cannot try monthly will not commit to 12 months. Monthly-with-annual-discount captures both cautious and committed buyers. |
| "We should charge per feature because we built a lot" | When the product has many features | Customers pay for outcomes, not feature counts. Per-feature pricing fragments the experience and creates resentment ("I can see it but I cannot use it"). Gate by scale, not by capability. |
