# Competitive Moat Analysis

Load when evaluating whether a feature creates lasting competitive advantage, assessing defensibility of product opportunities, or deciding build vs buy vs partner for strategic features.

## Moat Types and Durability

| Moat Type | How It Works | Durability | Example |
|-----------|-------------|------------|---------|
| **Network effects** | Product gets more valuable as more users join | Very high (winner-take-most) | Slack (more teams = more integrations), Figma (more designers = more shared files) |
| **Switching costs** | Leaving is painful because of invested data, workflows, or integrations | High (grows with usage) | Salesforce (years of CRM data + custom automations), QuickBooks (financial history + tax filing) |
| **Data moats** | Proprietary data that improves the product and can't be replicated | High (but requires continuous collection) | Waze (crowdsourced traffic), Clearbit (firmographic enrichment data) |
| **Economies of scale** | Unit economics improve with volume, making it hard for smaller competitors to compete on price | Medium (until disruptive tech resets the cost curve) | AWS (infrastructure), Stripe (payment processing volume) |
| **Brand/trust** | Users choose you because they TRUST you, not because you're objectively better | Medium (fragile, one scandal away from erosion) | 1Password (security trust), Basecamp (opinionated brand loyalty) |
| **Regulatory/compliance** | Certifications, licenses, or compliance requirements create barriers to entry | Medium-high (durable but available to well-funded entrants) | Healthcare (HIPAA), Finance (SOC2/PCI), Government (FedRAMP) |

**Moat decay**: Every moat decays. Network effects erode when users multi-home (using both Slack and Teams). Switching costs erode when competitors build import tools. Data moats erode when the data becomes commoditized. The question is not "do we have a moat?" but "how fast is it decaying and are we deepening it faster?"

## Defensibility Scoring

For each feature opportunity, score defensibility across 4 dimensions.

| Dimension | Score 1 (Weak) | Score 3 (Moderate) | Score 5 (Strong) |
|-----------|---------------|-------------------|-----------------|
| **Time to copy** | Competitor replicates in < 1 month | 3-6 months to replicate | 12+ months to replicate (requires data, infrastructure, or expertise they lack) |
| **Data advantage** | Feature works the same with zero user data | Performance improves with more data, but competitors can start fresh | Feature is ONLY possible with proprietary data collected over months/years |
| **Integration depth** | Standalone feature, no dependencies | Connects to 2-3 other features or data sources | Deeply woven into user workflows, removing it would break their process |
| **Network contribution** | Single-user value only | Better with team adoption | Creates value for users OUTSIDE the product (shared artifacts, public profiles, marketplace) |

**Scoring interpretation**:
- 16-20: Strong moat candidate. Invest heavily.
- 10-15: Moderate defensibility. Build, but expect competition. Speed to market matters.
- 4-9: Weak moat. Feature is table stakes or easily copied. Don't over-invest; build fast or don't build.

## Feature Moat Patterns

Patterns that reliably create defensible advantages.

| Pattern | Mechanism | Implementation Requirement |
|---------|-----------|---------------------------|
| **User-generated content lock-in** | Users invest effort creating content (templates, automations, reports) that only works in your product | Content creation must be easy enough to generate volume, complex enough to resist export |
| **Integration hub** | Becoming the center of the user's tool ecosystem via deep integrations | Each integration adds switching cost. Target integrations users can't live without (email, CRM, payment). |
| **Collaborative graph** | Product value increases with team size -- inviting teammates strengthens lock-in | Collaboration must be genuinely valuable, not just a feature checkbox. If users only collaborate because you force it, it's not a moat. |
| **Learned preferences** | Product adapts to user behavior over time, creating personalization competitors start without | Requires data collection + ML pipeline. Cold-start problem means new competitor offers worse experience for months. |
| **Marketplace/platform** | Third-party developers build on your platform, creating ecosystem value you don't maintain | Requires critical mass of both supply (developers) and demand (users). Two-sided marketplace cold-start is extremely hard. |

**Anti-moat patterns** (things that feel defensible but aren't):
- "First mover advantage" -- Being first matters only if you also build switching costs. Without them, a better-funded competitor overtakes you.
- "Patent protection" -- Software patents are expensive to enforce and rarely prevent determined competitors. They're defensive (lawsuit deterrent), not offensive (market advantage).
- "Secret sauce algorithm" -- Unless the algorithm requires proprietary data to function, it can be reverse-engineered or independently developed. Algorithms are ideas; execution and data are moats.

## Build vs Buy vs Partner Decision

| Signal | Build | Buy/Acquire | Partner/Integrate |
|--------|-------|-------------|-------------------|
| Core to your value proposition | YES -- own it completely | Only if acquiring saves 12+ months | Never outsource your core |
| Adjacent to core, enhances value | If team has expertise and it's < 3 month build | If a startup does it well and acquisition is affordable | If a mature product exists and API is stable |
| Commodity (auth, payments, email) | Almost never | Never (waste of capital) | YES -- use Stripe, Auth0, SendGrid, etc. |
| Strategic experiment (testing new market) | Minimum viable build (2-4 weeks) | Never (too early to commit) | If partner can white-label or API-enable quickly |
| Regulated/compliance-heavy | Only if you have compliance expertise | Acquire for the certifications as much as the product | If partner is already certified and you can leverage their compliance |

**The build trap**: Engineers prefer building. Building feels productive. But building commodity features (auth, billing, email) is engineering time that doesn't differentiate your product. Every week spent rebuilding Stripe is a week not spent on your actual moat.

**The integration trap**: Over-reliance on partners creates dependencies. If your core workflow depends on a partner's API, they can raise prices, change terms, or deprecate features. Mitigate: ensure you can switch partners within 2-4 weeks, or build an abstraction layer.

## Timing Analysis

When you enter a market matters as much as what you build.

| Timing Signal | Implication | Strategy |
|---------------|-------------|----------|
| No competitors exist yet | Either you've found a gap or there's no market | Validate demand BEFORE building. If demand exists, move fast -- first mover with switching costs wins. |
| 1-2 competitors, early stage | Market is validated but not crowded | Differentiate on a specific segment or workflow. Don't build a "better" clone. |
| 5+ competitors, established market | Market is mature. Competing on features is a losing game. | Find an underserved niche within the market. Or reframe the problem entirely (Figma vs Adobe: same market, different paradigm). |
| Incumbent is dominant (>60% market share) | Head-to-head competition requires 10x resources | Attack from a different angle: different price point, different audience, different platform, different business model. |

**Platform shift timing**: The highest-leverage moment to enter a market is during a platform shift (mobile, cloud, AI). During shifts, incumbents' advantages (distribution, data, brand) partially reset. Figma won against Sketch during the cloud shift. New AI-native tools are winning now during the AI shift.
