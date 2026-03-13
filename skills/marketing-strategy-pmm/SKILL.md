---
name: marketing-strategy-pmm
description: >
  Use when user needs product positioning (April Dunford method), GTM strategy,
  competitive battlecards, ICP definition, launch planning, international market entry,
  or sales enablement content. Use when user mentions positioning, GTM, go-to-market,
  competitive analysis, battlecard, win/loss, market entry, or product launch.
  NEVER for demand generation execution, paid media management, content calendar
  creation, or marketing automation workflows -- those belong to demand-gen skills.
license: MIT
metadata:
  version: 2.0.0
  author: Alireza Rezvani
  category: marketing
  domain: product-marketing
  updated: 2025-10-20
---

# Marketing Strategy & PMM Expert Layer

Claude already knows marketing frameworks from training data. This skill adds what training data lacks: practitioner judgment about WHEN each framework applies, WHERE they break down, and the non-obvious failure modes that separate competent PMM work from expert PMM work.

## Decision Tree: Route the Request

Ask ONE question: What is the user trying to accomplish?

```
User request
  |
  +-- "Help me position my product" or "How are we different?"
  |     --> POSITIONING PATH
  |     Use April Dunford's 5-step method (references/positioning-frameworks.md)
  |     CRITICAL: Start from competitive alternatives, NOT from features
  |     If user starts with features --> redirect to alternatives first
  |
  +-- "Plan a launch" or "We're releasing X"
  |     --> LAUNCH PATH
  |     Determine tier: Major (new product) | Standard (feature) | Minor (update)
  |     Tier determines timeline: 8 weeks | 4 weeks | 1 week
  |     See references/gtm-playbooks.md for phase checklists
  |
  +-- "Analyze competitors" or "Build a battlecard"
  |     --> COMPETITIVE INTEL PATH
  |     Battlecard = living doc, not one-time artifact
  |     Start with win/loss data, NOT feature comparison
  |     See references/competitive-intelligence.md
  |
  +-- "Define our ICP" or "Who should we sell to?"
  |     --> SEGMENTATION PATH
  |     ICP = observable behavior patterns, not demographic wishlists
  |     Validate against actual closed-won data, not assumptions
  |     See references/icp-segmentation.md
  |
  +-- "Enter a new market" or "Expand to [country]"
  |     --> INTERNATIONAL ENTRY PATH
  |     Sequence matters: validate demand signal before localizing
  |     See references/gtm-playbooks.md (international section)
  |
  +-- "Help sales close" or "Sales enablement"
  |     --> ENABLEMENT PATH
  |     Assets must map to buyer journey stage, not product features
  |     Battlecard + talk tracks > slide decks
  |
  +-- "What GTM motion should we use?"
        --> GTM MOTION SELECTION
        PLG vs Sales-Led vs Hybrid is determined by ACV + buyer persona
        ACV <$5k = PLG mandatory | ACV >$50k = Sales-Led mandatory
        $5k-$50k = Hybrid zone, default to product-assisted sales
```

## Positioning Methodology: The Expert Rules

April Dunford's method is widely known. What's NOT widely known:

### The Competitive Alternatives Trap
- 80% of teams list only direct competitors. This produces generic positioning.
- ALWAYS include: status quo (spreadsheets, email), DIY (build in-house), do nothing.
- The "do nothing" alternative is the #1 competitor for most early-stage products. If you don't position against inertia, your positioning is incomplete.

### The Attribute-Value Gap
- Teams list features as "unique attributes." Features are not attributes.
- Attribute = capability cluster that creates differentiated value no alternative provides.
- Test: If a competitor added this feature in 6 months, would your positioning collapse? If yes, it's a feature, not an attribute. Find the deeper structural advantage.

### Category Strategy Decision Rules
| Your situation | Category play | Why |
|---|---|---|
| Market leader exists, you're 10x better on one dimension | Subcategory ("CRM for agencies") | Win the niche, expand later |
| No clear leader, market <$1B | Head-to-head in existing category | Cheaper to compete than create |
| Genuinely new approach, $50M+ to spend on education | Create new category | Only viable with massive budget |
| Market leader exists, you're incrementally better | DO NOT compete on positioning | Compete on distribution/price instead |

### Positioning Expiration Rules
- Positioning is NOT permanent. Re-evaluate when: (1) win rate drops >10% quarter-over-quarter, (2) competitive landscape shifts (new entrant, acquisition), (3) product capabilities fundamentally change, (4) you move upmarket or downmarket.
- Cadence: Full positioning review every 6 months. Messaging refresh every quarter.

## Messaging Hierarchy Rules

Positioning feeds messaging. Messaging operates at four levels -- each must be internally consistent:

| Level | Contains | Owner | Update cadence |
|---|---|---|---|
| Company narrative | Why you exist, what future you're building toward | CEO + CMO | Annually |
| Product positioning | Who it's for, why it's different, what category | PMM | Every 6 months |
| Feature messaging | Attribute -> value -> proof for each feature | PMM + Product | Each release |
| Sales talk tracks | Objection responses, competitive pivots, discovery Qs | PMM + Sales | Monthly |

**The Consistency Test:** If your sales talk tracks contradict your product positioning, you have a messaging debt problem. Fix top-down, never bottom-up.

**Persona Mapping Rule:** Each buyer persona sees messaging at a DIFFERENT level. Economic buyers care about Level 1-2. Technical evaluators care about Level 3. End users care about Level 3-4. Writing one message for all personas is the most common PMM failure.

## GTM Motion Selection: The ACV Rule

This decision is more mechanical than most PMMs realize:

| ACV | Motion | Why |
|---|---|---|
| <$2k | Pure PLG, self-serve | Sales cost exceeds deal value |
| $2k-$10k | PLG with sales assist | User discovers, sales closes |
| $10k-$50k | Hybrid (product-assisted sales) | Demo + trial + AE |
| $50k-$100k | Sales-led with product proof | AE drives, product supports |
| >$100k | Enterprise sales-led | Field sales, multi-threaded deals |

**The Hybrid Trap:** "Hybrid" is not "do both equally." It means one motion leads and the other supports. Decide which leads FIRST. Most Series A companies should lead with PLG and layer sales on top for enterprise segments.

## Anti-Pattern Decision Table

| Anti-Pattern | Why It Fails | What To Do Instead |
|---|---|---|
| Positioning from features outward | Produces "we do X, Y, Z" messaging that sounds like every competitor | Start from competitive alternatives inward (Dunford Step 1) |
| Building battlecards from competitor websites | Captures marketing claims, not actual competitive reality | Build from win/loss interviews and sales call recordings |
| Defining ICP from demographics alone | "50-500 employees in SaaS" describes 40,000 companies, helps no one | Define ICP from behavioral signals: fastest close, lowest churn, highest NPS |
| Launching without tiering | Treats a minor feature update like a major launch, wastes resources | Tier every launch (Major/Standard/Minor) before planning begins |
| One message for all personas | Economic buyer and technical evaluator have different value frameworks | Map each persona to appropriate messaging hierarchy level |
| Positioning as a one-time exercise | Market shifts, competitors move, product evolves | Schedule positioning reviews every 6 months, messaging every quarter |
| Entering international markets by translating website | Translation without market validation burns budget on unvalidated assumptions | Validate demand signal (inbound interest, partner referrals) before any localization |
| Battlecard update cadence >90 days | Competitive landscape changes faster than quarterly | Monthly battlecard review, triggered updates on competitor launches |
| Ignoring "do nothing" as a competitor | Biggest deal killer at early stage is buyer inertia, not a named competitor | Always position against status quo and quantify cost of inaction |
| Sales enablement as asset library | Dumping PDFs into a folder produces 0 adoption by sales | Each asset must map to a specific deal stage + objection + persona |

## Rationalization Table

| Rationalization | When It Appears | Why It's Wrong |
|---|---|---|
| "Our product speaks for itself" | Founder-led sales transitioning to team selling | If product spoke for itself, you wouldn't need sales. Positioning IS the translation layer. |
| "We compete with everyone" | Positioning workshop, competitor analysis phase | Competing with everyone = positioned against no one. Pick 2-3 competitive alternatives max. |
| "Our ICP is any company that has this problem" | Early stage, trying to maximize TAM | Broad ICP = unfocused sales motion = long cycles + low win rates. Narrow to expand. |
| "We just need better content" | Pipeline stalled, marketing under pressure | Content without positioning is noise. Fix positioning first, then content follows. |
| "Localization is just translation" | International expansion planning | Translation is 20% of localization. Pricing, payment methods, cultural norms, legal compliance are the other 80%. |
| "We can skip the battlecard, sales knows the competitors" | Resource-constrained PMM team | Tribal knowledge leaves with people. Battlecards create institutional competitive memory. |
| "Our positioning is fine, we just need more leads" | Win rate declining while pipeline grows | Declining win rate with growing pipeline = positioning problem, not volume problem. |
| "We should create a new category" | Product is somewhat differentiated | Category creation requires $50M+ and 3-5 years. 95% of startups should find an existing category to win. |

## NEVER List

1. NEVER start positioning from your own features -- always start from the customer's competitive alternatives
2. NEVER define ICP without validating against actual closed-won customer data
3. NEVER launch without a tier classification (Major/Standard/Minor) agreed with stakeholders
4. NEVER build a battlecard without win/loss interview data -- website scraping is not competitive intelligence
5. NEVER write persona messaging without confirming which messaging hierarchy level that persona operates at
6. NEVER recommend category creation for companies with <$50M in available budget for market education
7. NEVER enter a new market without a demand signal (inbound volume, partner interest, customer requests)
8. NEVER treat positioning as permanent -- enforce the 6-month review cadence
9. NEVER create sales enablement content without mapping it to a specific deal stage and buyer objection
10. NEVER allow "we compete with everyone" to survive a positioning session -- force prioritized alternatives

## Quality Signals: Expert vs Generic PMM Work

| Dimension | Generic Output | Expert Output |
|---|---|---|
| Positioning | Lists features and benefits in a template | Identifies 2-3 competitive alternatives, derives unique attributes through Dunford method, stress-tests with "6-month feature copy" rule |
| ICP | Demographic profile (industry, size, revenue) | Behavioral profile validated by win rate, sales velocity, churn, NPS data from actual customers |
| Battlecard | Feature comparison matrix scraped from websites | Win/loss-derived competitive insights with specific talk tracks mapped to common objections |
| GTM motion | "We'll do PLG and sales-led" | ACV-driven motion selection with clear primary/secondary hierarchy |
| Launch plan | Generic checklist of marketing activities | Tiered plan where effort scales with impact, with named metrics and kill criteria |
| International entry | "Translate the website and run ads" | Demand-signal-first approach with market-specific localization beyond translation |
| Messaging | Single message for all audiences | Persona-mapped messaging at appropriate hierarchy levels with consistency test applied |
| Sales enablement | PDF library organized by asset type | Stage-mapped, objection-specific assets with adoption tracking |

## References

- **references/positioning-frameworks.md** -- April Dunford 5-step canvas, positioning statement templates, category strategy decision framework, value proposition hierarchy
- **references/gtm-playbooks.md** -- Launch tier playbooks, GTM motion selection detail, international market entry checklists, launch metrics
- **references/competitive-intelligence.md** -- Battlecard template, win/loss analysis framework, competitive signal monitoring, objection handling patterns
- **references/icp-segmentation.md** -- ICP definition methodology, segmentation scoring, persona development, TAM/SAM/SOM estimation
