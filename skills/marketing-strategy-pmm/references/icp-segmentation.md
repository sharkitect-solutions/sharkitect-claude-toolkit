# ICP & Segmentation Reference

## ICP Definition Methodology

### The Behavioral ICP (vs Demographic ICP)

Most teams define ICP as demographics: "50-500 employee SaaS companies in the US." This describes 40,000+ companies and helps no one make decisions.

**Expert ICP definition starts from behavior, not demographics.**

### Step 1: Analyze Your Best Customers

Pull these data points for every customer from the last 12 months:

| Data point | Source | Why it matters |
|---|---|---|
| Time to close (days) | CRM | Fast closers = strong product-market fit |
| Net revenue retention | Billing system | High NRR = sticky product |
| NPS score | Survey tool | Promoters = referenceable |
| Support ticket volume | Help desk | Low tickets = good fit |
| Feature adoption breadth | Product analytics | High adoption = deep engagement |
| Expansion revenue | Billing system | Expansion = growing value perception |
| Churn risk score | CS tool or manual | Low risk = durable fit |

### Step 2: Identify the Intersection

Your ICP is the customer segment that scores high on 3+ of these dimensions simultaneously:
- Top 25% fastest sales cycle
- Top 25% highest NPS
- Top 25% lowest churn / highest NRR
- Top 25% highest feature adoption

**The intersection is your ICP.** Not the union -- the intersection.

### Step 3: Discover What They Have in Common

Once you have 15-30 customers in the intersection, look for shared traits:

**Observable traits (use for targeting):**
- Industry vertical or sub-vertical
- Company size range (employees or revenue)
- Technology stack (what tools they already use)
- Growth stage (funding round, growth rate)
- Org structure (do they have a [specific role]?)
- Buying trigger (what event caused them to look for a solution?)

**Behavioral traits (use for qualification):**
- Problem severity: Is this a "hair on fire" problem or a "nice to have"?
- Solution maturity: Have they tried to solve this before? How?
- Decision speed: Can they make purchase decisions in <90 days?
- Budget authority: Does the contact have budget, or do they need approval?
- Champion potential: Will they advocate internally?

### Step 4: Write the ICP Statement

**Format:**
```
Our ideal customer is a [company type] that:
- Is experiencing [specific buying trigger]
- Currently handles this with [status quo solution]
- Has [observable trait] that makes our approach uniquely valuable
- Typically decides within [timeframe] and invests [$range]

We know this because these customers:
- Close [X%] faster than our average
- Retain at [Y%] NRR
- Score [Z] NPS
- Based on analysis of [N] customers
```

### ICP Validation Checklist

Before committing resources to an ICP:

- [ ] Based on actual customer data, not assumptions (minimum N=15)
- [ ] Sales cycle for this segment is faster than company average
- [ ] Churn rate for this segment is lower than company average
- [ ] NPS for this segment is higher than company average
- [ ] Addressable market contains >100 companies (not too narrow)
- [ ] Can be targeted through identifiable channels (not invisible)
- [ ] Sales team can articulate the ICP in one sentence
- [ ] Marketing can build a targetable audience matching this ICP

### ICP Scoring System (for CRM)

Assign every lead/account a fit score:

| Score | Label | Criteria | Action |
|---|---|---|---|
| A | Perfect fit | Matches 5+ ICP traits, buying trigger present | Fast-track: <4 hour response, AE assigned |
| B | Good fit | Matches 3-4 ICP traits | Standard: <24 hour response, qualify further |
| C | Partial fit | Matches 1-2 ICP traits | Nurture: Marketing automation, monitor for signals |
| D | Poor fit | Matches 0 traits or anti-ICP | Disqualify: Don't waste sales time |

**Anti-ICP traits (auto-disqualify):**
- Company size below minimum viable (can't afford the product)
- Industry with regulatory barriers you can't serve
- Technology stack fundamentally incompatible
- Buying process >12 months (capital-draining sales cycle)
- No budget authority in the buying committee you can reach

## Segmentation Criteria and Scoring

### Segmentation Dimensions

**Dimension 1: Company Size (determines ACV and motion)**
| Segment | Size | Typical ACV | GTM motion |
|---|---|---|---|
| VSB (Very Small Business) | 1-10 employees | <$500/yr | Self-serve only (or don't serve) |
| SMB | 11-200 employees | $500-$5k/yr | PLG with optional sales assist |
| Mid-Market | 201-2,000 employees | $5k-$50k/yr | Hybrid (product + sales) |
| Enterprise | 2,001-10,000 employees | $50k-$250k/yr | Sales-led |
| Strategic | 10,000+ employees | $250k+/yr | Named account, field sales |

**Dimension 2: Vertical (determines messaging and packaging)**
- Horizontal play: Same product, different messaging per vertical
- Vertical play: Modified product/features per industry
- Decision: Start horizontal unless >40% of revenue comes from one vertical

**Dimension 3: Geography (determines localization investment)**
- See gtm-playbooks.md for international entry framework
- Key rule: Only localize after demand signal is validated

**Dimension 4: Use Case (determines product packaging)**
- Each distinct use case may justify its own landing page, onboarding flow, and pricing tier
- Identify: What are the 2-3 primary jobs-to-be-done your customers hire your product for?

### Segment Prioritization Matrix

Score each segment on these dimensions (1-5 scale):

| Criterion | Weight | How to score |
|---|---|---|
| TAM (total addressable market) | 20% | Revenue potential in this segment |
| Win rate (historical) | 25% | % of opportunities won in this segment |
| Sales velocity (historical) | 20% | Speed of close vs company average |
| Retention (historical) | 20% | NRR and churn for this segment |
| Strategic value | 15% | Brand logos, reference-ability, expansion potential |

**Weighted score = (TAM x 0.2) + (Win rate x 0.25) + (Velocity x 0.2) + (Retention x 0.2) + (Strategic x 0.15)**

Top-scoring segment = primary focus (50%+ of resources).
Second segment = secondary (25-30% of resources).
All others = deprioritize until primary and secondary are saturated.

## Persona Development Framework

### Persona Construction Rules

1. **Maximum 3-4 personas.** More than 4 means you haven't prioritized.
2. **Each persona must map to a buying role**, not a demographic.
3. **Personas are validated by sales, not invented by marketing.**

### Buying Committee Roles

| Role | Definition | What they care about | Messaging level |
|---|---|---|---|
| Economic buyer | Signs the contract, owns budget | ROI, risk mitigation, business outcomes | Company narrative + Product positioning |
| Technical evaluator | Assesses product fitness | Architecture, security, integration, performance | Feature messaging + technical proof |
| Champion/User | Will use the product daily | Ease of use, workflow fit, daily efficiency | Feature messaging + UX proof |
| Blocker | Can veto but can't approve | Risk, compliance, change management | Risk mitigation + proof points |

### Persona Document Template

```
PERSONA: [Role title]
Buying role: [Economic buyer / Technical evaluator / Champion / Blocker]

CONTEXT:
- Reports to: [Title]
- Team size: [Range]
- Key responsibility: [One sentence]
- Measured on: [Their KPIs]

BUYING TRIGGER:
- What event makes them start looking? [Be specific]
- What has to go wrong for this to become urgent?

EVALUATION CRITERIA (ranked):
1. [Most important factor]
2. [Second most important]
3. [Third most important]

OBJECTIONS (from win/loss data):
1. [Most common objection]
2. [Second most common]

PREFERRED CONTENT:
- Format: [Video / whitepaper / case study / demo / technical docs]
- Channel: [Where they discover solutions -- LinkedIn, peer recommendation, analyst report, Google]
- Decision involvement: [Early research / Shortlist evaluation / Final approval]

MESSAGING DO:
- Lead with [their top evaluation criteria]
- Prove with [evidence type they trust]

MESSAGING DON'T:
- Don't lead with [irrelevant criteria for this role]
- Don't use [tone/language that alienates this persona]
```

## TAM/SAM/SOM Estimation

### Definitions and Calculation

**TAM (Total Addressable Market):** Everyone who could theoretically buy your product.
- Calculation: [# of companies in target segments] x [average ACV]
- Source: Industry reports (Gartner, IDC), government data (Census Bureau, Eurostat), databases (LinkedIn Sales Navigator, ZoomInfo)

**SAM (Serviceable Addressable Market):** TAM filtered by what you can actually serve today.
- Filters: Geography you operate in, languages you support, segments you serve, compliance you hold
- Calculation: TAM x [% of TAM that matches your current capabilities]

**SOM (Serviceable Obtainable Market):** SAM filtered by realistic market share.
- Factors: Current market share, growth rate, competitive intensity, sales capacity
- Calculation: SAM x [realistic market share % based on competitive position]
- Rule of thumb: First-year SOM is typically 1-5% of SAM for startups

### Common TAM Estimation Errors

| Error | Why it's wrong | Correct approach |
|---|---|---|
| Using total industry revenue as TAM | Includes spending on things you don't replace | Only count spending your product actually displaces |
| Top-down only (analyst report number) | Misses segment boundaries | Cross-validate with bottom-up: count of target companies x ACV |
| Ignoring willingness to pay | Just because a market exists doesn't mean they'll pay you | Validate with pricing research or early sales data |
| Static TAM | Markets grow and shrink | Re-estimate annually, note growth assumptions |
| Conflating TAM with opportunity | TAM = theoretical max; opportunity = what you can win | Always present SOM alongside TAM for realistic planning |

### Bottom-Up TAM Calculation Template

```
Step 1: Define target segments
  Segment A: [Description]
  Segment B: [Description]

Step 2: Count addressable companies per segment
  Segment A: [N] companies (source: [LinkedIn/ZoomInfo/Census])
  Segment B: [N] companies (source: [LinkedIn/ZoomInfo/Census])

Step 3: Apply ACV per segment
  Segment A: [N] x [$ACV] = $[TAM-A]
  Segment B: [N] x [$ACV] = $[TAM-B]

Step 4: Sum for total TAM
  TAM = $[TAM-A] + $[TAM-B] = $[Total]

Step 5: Apply SAM filters
  Geographic filter: [X%] of TAM operates in markets we serve
  Capability filter: [Y%] of TAM matches our product capabilities
  SAM = TAM x [X%] x [Y%] = $[SAM]

Step 6: Estimate SOM
  Current market share: [Z%]
  Realistic 12-month capture: [W%] of SAM
  SOM = SAM x [W%] = $[SOM]
```
