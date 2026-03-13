# Competitive Intelligence Reference

## Battlecard Template

Create one battlecard per competitor. Living document -- NOT a one-time artifact.

### Battlecard Structure

```
COMPETITOR: [Name]
Last updated: [Date]
Update owner: [PMM name]
Next review: [Date -- max 30 days out]

--- QUICK FACTS ---
Founded: [Year]
Funding: [Stage, total raised]
Headcount: [Approximate]
Revenue: [Estimate if available]
Key customers: [Logos]
Pricing: [Model and range]

--- POSITIONING ---
Their claim: [What they say on their homepage]
Market reality: [What customers and analysts actually say]
Category: [How they position themselves]
Recent messaging shifts: [Any changes in last 90 days]

--- STRENGTHS (verified, not assumed) ---
1. [Strength] -- Source: [win/loss interview, G2 review, product trial]
2. [Strength] -- Source: [specific evidence]
3. [Strength] -- Source: [specific evidence]

--- WEAKNESSES (verified, not assumed) ---
1. [Weakness] -- Source: [loss interview, churned customer, G2 review]
2. [Weakness] -- Source: [specific evidence]
3. [Weakness] -- Source: [specific evidence]

--- OUR DIFFERENTIATION ---
When we win against them: [Specific scenarios with data]
When we lose against them: [Specific scenarios with data]
Win rate: [X% in head-to-head deals, sample size N]

--- TALK TRACKS ---

Objection: "We're already using [Competitor]"
Response framework:
  1. Acknowledge (don't attack): "Makes sense, they're a solid product."
  2. Probe for pain: "What prompted you to take this call?"
  3. Position on pain: [Map their pain to our differentiation]
  4. Quantify: "Teams that switch typically see [metric improvement]"

Objection: "[Competitor] has more features"
Response framework:
  1. Agree and reframe: "They do have breadth. The question is depth."
  2. Focus on their use case: "Which 3 features are most critical?"
  3. Demo those 3: Show superiority on what matters to THIS buyer
  4. Cost of complexity: "More features = longer onboarding + more training"

Objection: "[Competitor] is cheaper"
Response framework:
  1. Validate: "Price matters. Let's make sure we're comparing accurately."
  2. Total cost: Include implementation, training, maintenance, integration costs
  3. Value delta: "The question isn't cost, it's ROI per dollar spent"
  4. Proof: "[Customer X] chose us at [higher price] because [outcome]"

--- RECENT MOVES ---
[Date]: [What they did -- launch, pricing change, acquisition, hire]
[Date]: [What they did]
[Date]: [What they did]
```

### Battlecard Quality Rules

| Rule | Why |
|---|---|
| Every strength/weakness must cite a source | Prevents assumption-based battlecards that mislead sales |
| Win rate must include sample size | "80% win rate" means nothing with N=5 |
| Talk tracks must be tested by sales before publishing | Untested talk tracks damage deals |
| Review cycle must be <30 days | Stale battlecards are worse than no battlecards |
| Weaknesses must include "when we lose" scenarios | Sales needs to know when to walk away, not just when to fight |

## Win/Loss Analysis Framework

### Interview Process

**Who to interview:**
- Closed-won customers (within 30 days of close)
- Closed-lost prospects (within 14 days of loss -- memory fades fast)
- Churned customers (within 7 days of churn notice)

**Interview count targets:**
| Company stage | Monthly interviews | Why this number |
|---|---|---|
| Pre-Series A | 3-5 | Small deal volume, every data point matters |
| Series A-B | 8-12 | Enough for pattern detection |
| Series C+ | 15-20 | Statistical significance on trends |

**Who conducts interviews:**
- NOT the account's AE (bias: they'll defend their performance)
- PMM or dedicated win/loss analyst
- Third-party research firm (most unbiased, most expensive)

### Interview Questions (Prioritized)

**Tier 1 (always ask):**
1. What was the business problem you were trying to solve?
2. What alternatives did you evaluate? (Probe: "Anyone else? Considered building internally?")
3. What was the deciding factor? (One thing, not a list)
4. What almost changed your mind? (Reveals hidden objections)
5. How would you describe us to a colleague in one sentence? (Tests positioning)

**Tier 2 (ask if time permits):**
6. How was the evaluation process? (Reveals sales process friction)
7. Who else was involved in the decision? (Maps buying committee)
8. What would you change about our product/process?
9. How did our pricing compare? (Not just "were we cheaper" but "did pricing model fit")
10. Would you recommend us? Why or why not?

### Analysis Framework

**After every 10 interviews, extract:**

1. **Win themes** (ranked by frequency):
   - Theme A: mentioned in X/10 wins
   - Theme B: mentioned in Y/10 wins
   - Pattern: What do winning deals have in common?

2. **Loss themes** (ranked by frequency):
   - Theme A: mentioned in X/10 losses
   - Theme B: mentioned in Y/10 losses
   - Pattern: What do lost deals have in common?

3. **Competitive shifts:**
   - Which competitors are appearing more/less often?
   - Any new entrants mentioned for the first time?
   - Have competitor talk tracks or pricing changed?

4. **Positioning validation:**
   - Is our positioning reflected in how customers describe us?
   - If customer description != our positioning, we have a messaging gap

5. **Product gaps (actionable for product team):**
   - Feature X mentioned as deal-breaker in N deals
   - Priority: [critical if N>3 in a single quarter]

### Win/Loss Reporting Cadence

| Report | Audience | Frequency | Content |
|---|---|---|---|
| Win/loss summary | PMM, Sales leadership | Monthly | Top themes, win rate trends, action items |
| Competitive trend report | Product, Executive team | Quarterly | Competitor movements, market shifts, positioning recs |
| Battlecard updates | Sales team | As-needed, max monthly | Updated talk tracks, new objection responses |
| Product gap brief | Product management | Quarterly | Feature requests from lost deals, ranked by revenue impact |

## Competitive Signal Monitoring

### What to Monitor

| Signal | Source | Cadence | What it reveals |
|---|---|---|---|
| Website messaging changes | Competitor website (use change tracking tool) | Weekly | Positioning shifts, new features, target market changes |
| Pricing changes | Pricing page, sales outreach, customer reports | Monthly | Go-to-market strategy shifts |
| Job postings | LinkedIn, competitor careers page | Monthly | Product roadmap hints (hiring ML engineers = AI features coming) |
| Funding announcements | Crunchbase, press releases | As-they-happen | Budget for growth, potential price wars |
| Product launches | Blog, Product Hunt, press | As-they-happen | Feature parity threats, positioning attacks |
| Key hires/departures | LinkedIn | Monthly | Strategic shifts, leadership instability |
| Customer reviews (new) | G2, Capterra, TrustRadius | Bi-weekly | Real user sentiment, emerging complaints |
| Patent filings | Google Patents, USPTO | Quarterly | Long-term product direction |

### Competitive Response Decision Framework

When a competitor makes a move, use this framework:

```
Competitor action
  |
  +-- Does it affect our win rate? (check last 30 days of deal data)
  |     |
  |     +-- YES, win rate dropped >5% --> URGENT: Update battlecards within 48 hours
  |     +-- NO, win rate stable --> MONITOR: Note it, update battlecard at next cycle
  |
  +-- Does it affect our positioning? (does it undermine our claimed differentiation?)
  |     |
  |     +-- YES, they now match our key attribute --> CRITICAL: Re-run positioning exercise
  |     +-- NO, our differentiation holds --> INFORM: Brief sales team, no strategy change
  |
  +-- Does it affect our pricing? (did they undercut or restructure?)
        |
        +-- YES, material price difference --> EVALUATE: Run pricing analysis (not knee-jerk reaction)
        +-- NO, pricing stable --> IGNORE: Don't chase competitor pricing changes
```

## Objection Handling Pattern Library

### Structure for Every Objection Response

```
1. ACKNOWLEDGE (never dismiss)
   "That's a fair concern..." or "I hear that a lot..."

2. REFRAME (shift the evaluation criteria)
   "The real question is..." or "What we've found is..."

3. EVIDENCE (prove it, don't claim it)
   Customer quote, metric, case study, or demo

4. ADVANCE (move to next step)
   "Would it be helpful to..." or "Can I show you..."
```

### Common Objection Patterns by Type

**Price objections:**
- Always respond with total cost of ownership, not sticker price
- Include: implementation time, training cost, ongoing maintenance, integration cost
- Tool: ROI calculator with customer-specific inputs

**Feature gap objections:**
- Acknowledge the gap honestly. Never promise roadmap delivery dates.
- Reframe: "Of the features you need, which 3 are deal-breakers vs nice-to-haves?"
- If gap is real and critical: qualify out gracefully (better than winning a churning customer)

**Incumbent objections ("already using X"):**
- Never attack the incumbent directly
- Probe for why they're talking to you (something is broken)
- Position on the delta: what SPECIFICALLY would change if they switched
- Quantify switching cost vs switching benefit (must be 3:1 or better)

**Timing objections ("not now"):**
- Distinguish between real timing (budget cycle, reorg) and objection masking
- If real timing: agree on specific follow-up date, send relevant content in interim
- If mask: probe deeper -- "What would need to change for this to become a priority?"
