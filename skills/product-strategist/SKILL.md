---
name: product-strategist
description: "Use when making product strategy decisions -- prioritization, OKR design, roadmap planning, product-market fit assessment, or build-vs-buy evaluation. Use when diagnosing product health (retention curves, engagement ratios, revenue metrics). Use when translating company vision into team-level execution. Use when a product leader asks 'what should we build next?' or 'how do we know if we have PMF?' NEVER for project management or sprint planning -- that is execution, not strategy. NEVER for marketing positioning or go-to-market -- use marketing skills instead."
---

# Product Strategist

Think like a product leader who has shipped at scale, not a framework librarian. Most product strategy failures are not missing frameworks -- they are applying the wrong framework at the wrong stage, or confusing activity with outcomes.

Before any product strategy decision, ask:
- **What stage is the product?** (pre-PMF, scaling, mature, declining?)
- **What is the actual decision?** (what to build, how to measure, how to prioritize, or how to organize?)
- **What evidence exists?** (gut feeling, qualitative signal, quantitative data, or market research?)
- **What is the cost of being wrong?** (reversible experiment vs. irreversible bet?)

These four questions prevent the most common strategy mistake: applying a scaling playbook to a pre-PMF product, or applying a discovery playbook when you should be executing.

## Product Decision Routing

```
What kind of product decision?
|
+-- "Do we have product-market fit?"
|   -> Go to: Product-Market Fit Assessment
|   Signal: Founders/execs keep asking this question
|   Trap: PMF is not binary. You can have PMF in one segment and not another.
|
+-- "What should we build next?"
|   -> Go to: Prioritization Decision Tree
|   Signal: Backlog has 50+ ideas and no clear winner
|   Trap: The answer is almost never "the thing the loudest customer asked for"
|
+-- "How do we set goals for this quarter?"
|   -> Go to: OKR Design
|   Signal: Planning cycle starting, leadership wants alignment
|   Trap: OKRs that are task lists in disguise ("Ship feature X")
|
+-- "Is our product healthy?"
|   -> Go to: Product Health Signals
|   Signal: Metrics dashboard exists but nobody knows what "good" looks like
|   Trap: Vanity metrics (total signups, page views) hiding real problems
|
+-- "Should we build this ourselves or buy/partner?"
|   -> Go to: Build vs Buy vs Partner
|   Signal: Engineering wants to build; business wants to buy
|   Trap: Underestimating integration cost of "buy"
|
+-- "Our strategy keeps changing"
|   -> Go to: The Strategy Stack
|   Signal: Vision changes quarterly, roadmap changes weekly
|   Trap: Confusing strategy pivots with lack of strategy
```

## Product-Market Fit Assessment

PMF is not a feeling. Measure it.

**Sean Ellis Test:** Survey users: "How would you feel if you could no longer use this product?" If 40%+ say "very disappointed," you likely have PMF in that segment. Below 40% means you are still searching.

**Why NPS alone is misleading:** NPS measures satisfaction, not dependency. A product can have NPS of 70 among a biased sample of power users while 80% of signups churn in week one. NPS tells you existing users are happy -- it does not tell you the market needs your product.

**Quantitative PMF signals (all must be present, not just one):**

| Signal | Healthy Threshold | Why This Matters |
|--------|-------------------|------------------|
| Organic acquisition | >40% of new users | Paid acquisition masks lack of pull. If you turn off ads and growth stops, you have marketing-market fit, not product-market fit. |
| Cohort retention curve | Flattens (not just slows) | A curve that keeps declining means users try it and leave. Flattening means a core group stays permanently. |
| DAU/MAU ratio | >0.2 for non-seasonal products | Below 0.2 means users signed up but don't come back. Your product is not a habit. |
| Time-to-value | Decreasing over time | If it takes longer for new users to get value, your product is getting more complex, not better. |
| Usage expands over time | Users adopt more features | Deepening usage signals genuine need, not curiosity. |

**The PMF trap:** PMF is segment-specific. You can have strong PMF with 500-person companies and zero PMF with enterprises. Always specify: "PMF for [segment] solving [problem]." Claiming general PMF is almost always wrong.

## Prioritization Decision Tree

```
What is the product's maturity stage?
|
+-- Pre-PMF (searching for fit)
|   Method: ICE (Impact, Confidence, Ease)
|   Why: You lack data for anything more sophisticated.
|   RICE requires reliable reach estimates -- pre-PMF, you don't have them.
|   Focus: Run the fewest experiments that test the riskiest assumptions.
|
+-- Growth (PMF confirmed, scaling)
|   Method: Opportunity Scoring
|   How: For each job-to-be-done, measure:
|         - Importance (how much users care, 1-10)
|         - Satisfaction (how well current solution works, 1-10)
|         - Opportunity = Importance + (Importance - Satisfaction)
|   Why: High importance + low satisfaction = underserved opportunity.
|   Trap: Don't survey only power users -- they over-index on advanced features.
|
+-- Mature (optimizing, defending position)
|   Method: Cost of Delay
|   How: Estimate weekly revenue/retention impact of NOT building each feature.
|   Why: In mature products, the cost of inaction is often higher than the value of action.
|   Trap: Cost of delay is hard to estimate accurately. Use ranges, not point estimates.
|
+-- Any stage, backlog grooming
|   Method: RICE (Reach, Impact, Confidence, Effort)
|   Why: RICE is fine for ordering a backlog. It is NOT a strategy tool.
|   Trap: Teams use RICE scores as objective truth. They are estimates of estimates.
```

**The "strategy tax":** Some features don't serve current users at all. They exist for strategic positioning -- platform play, ecosystem lock-in, enterprise readiness, regulatory compliance. These features will always score low on RICE/ICE but may be essential. Maintain a separate "strategic bets" bucket (max 20% of capacity) that bypasses normal prioritization. If strategic bets exceed 20%, you are not prioritizing -- you are guessing.

## OKR Design

### The Outcome vs. Output Test

Before writing any Key Result, apply this test:

```
"Ship redesigned onboarding flow" -- Is this an outcome or an output?
OUTPUT. It describes work, not impact. What if you ship it and activation doesn't improve?

Rewrite: "Increase day-7 activation rate from 23% to 35%"
OUTCOME. Teams can now choose HOW to achieve it -- maybe redesigning onboarding,
maybe improving the first-run experience, maybe better targeting.
```

Every KR must pass the outcome test. If it describes shipping something, it is a task masquerading as a Key Result.

### OKR Anti-Pattern Table

| Anti-Pattern | Example | Why It Fails | Fix |
|-------------|---------|-------------|-----|
| Output KRs | "Ship feature X by March" | Measures activity, not impact. Feature ships, metric doesn't move, everyone claims success anyway. | Rewrite as outcome: "Increase [metric] from X to Y" |
| Too many OKRs | 5 objectives, 20 KRs | No focus. Teams context-switch constantly. Nothing moves meaningfully. | Max 3 objectives, 3-4 KRs each. If everything is a priority, nothing is. |
| Sandbagging | Team hits 100% every quarter | OKRs are supposed to be ambitious (70% hit = good). Hitting 100% means targets were set to guarantee success. | If a team hits 100% twice in a row, raise targets 30% next quarter. |
| Mechanical cascading | Company KR split equally across 4 teams | Creates alignment theater -- teams hit their fraction but nobody owns the outcome. One team's shortfall is invisible. | Each team should have their own outcome that CONTRIBUTES to the company KR, not a quota share of it. |
| Aspirational-only OKRs | "Become the leading platform for X" | No measurable KR. What does "leading" mean? By what measure? | Every objective needs at least one KR with a current number and a target number. |
| Shared OKRs nobody owns | "Cross-functional: improve user experience" | When everyone owns it, nobody owns it. Accountability diffuses. | Assign a single DRI (directly responsible individual) per objective. Others contribute. |

### Before/After: OKR Cascade

**BAD cascade (alignment theater):**
```
Company: "Grow ARR from $10M to $15M"
  -> Product: "Contribute $2M ARR" (arbitrary split)
     -> Team A: "Contribute $500K" (sub-split)
     -> Team B: "Contribute $500K" (sub-split)

Problem: Team A ships a pricing change (+$600K). Team B misses (-$200K).
Company hits $14.4M. "Close enough." Nobody investigates why Team B missed
because the aggregate looked fine.
```

**GOOD cascade (real alignment):**
```
Company: "Grow ARR from $10M to $15M"
  -> Product: "Increase net revenue retention from 95% to 110%"
     (product's highest-leverage contribution to ARR growth)
     -> Team A: "Reduce churn in mid-market segment from 8% to 4%"
        (owns the biggest retention gap)
     -> Team B: "Increase expansion revenue per account from $2K to $3.5K"
        (owns the growth within existing accounts)

Each team has a distinct outcome. Each outcome directly contributes to
product's NRR goal. NRR directly contributes to company ARR.
No arbitrary splitting. Clear ownership. Failure is visible and attributable.
```

## Product Health Signals

### Death Signals (act immediately if you see these)

| Signal | Threshold | What It Means |
|--------|-----------|---------------|
| DAU/MAU ratio | < 0.2 (non-seasonal) | Users signed up but do not return. Product is not a habit. |
| Feature adoption | < 5% of users use > 50% of features | You built for edge cases. Most of your product is dead weight. |
| Net Revenue Retention | < 80% | You lose more revenue from churn/contraction than you gain from expansion. Growth requires ever-increasing acquisition to stand still. |
| Support tickets per user | Increasing quarter over quarter | Product is getting harder to use as you add complexity. |
| Time-to-value | Increasing quarter over quarter | New users take longer to get value. Onboarding debt is compounding. |
| Cohort retention curve | Never flattens | Every cohort eventually leaves. No core user base forming. |

### Vanity Metrics (look good, mean nothing)

- **Total registered users:** Only matters if they are active. 1M signups with 20K MAU is a leaky bucket.
- **Page views / sessions:** Activity is not value. Users rage-clicking through confusing UX generate lots of page views.
- **Feature count:** More features often means more confusion. Measure feature adoption rate, not feature count.
- **Gross revenue without cohort breakdown:** Revenue can grow while unit economics deteriorate. Always look at revenue per cohort.

## The Strategy Stack

Vision, strategy, roadmap, and sprint are four distinct layers. Each has its own change frequency:

```
Layer         | Timeframe  | Change Frequency    | Owner
--------------+------------+---------------------+---------------
Vision        | 3-5 years  | Rarely (major pivot)| CEO/Founder
Strategy      | Annual     | Yearly review       | Product Leader
Roadmap       | Quarterly  | Quarterly planning  | Product Team
Sprint/Cycle  | 1-2 weeks  | Every cycle         | Engineering
```

**The diagnostic:** If your vision changes quarterly, you don't have strategy -- you have panic. If your roadmap never changes, you are not learning from the market -- you are executing a plan made with outdated information. If your sprint scope changes daily, you have a prioritization problem, not a strategy problem.

**Strategy must answer exactly three questions:**
1. Who is our target customer? (not "everyone")
2. What is our unique value? (not "better UX")
3. How do we win? (not "by building great product")

If your strategy document doesn't answer these with specifics, it is a vision statement pretending to be a strategy.

## Build vs Buy vs Partner

```
Is this capability a core differentiator?
|
+-- YES: Build it.
|   Your competitive advantage depends on controlling this.
|   Example: Stripe built their own payment processing core.
|
+-- NO: Is it a commodity?
    |
    +-- YES: Buy it.
    |   Don't waste engineering on solved problems.
    |   Example: Authentication (use Auth0/Clerk), email (use SendGrid).
    |   Trap: "It's not exactly what we need" is almost never a valid reason
    |   to build. Customization cost < integration cost in 90%+ of cases.
    |
    +-- NO: Is it strategic but not core?
        |
        +-- YES: Partner.
        |   You need the capability but building it would distract from core.
        |   Example: Payment processing for a SaaS (partner with Stripe).
        |
        +-- NO: Do you actually need it at all?
            Probably not. Cut it.
```

**The build trap:** Engineering teams default to building because integration feels risky and building feels productive. But every custom-built commodity feature is a maintenance burden forever. Multiply the build estimate by 3x for ongoing maintenance over 3 years. If buy-and-integrate is cheaper than that total, buy.

## Feature Cutting Framework

Features should be cut when they drag the product down. But never cut on a single metric.

**Cut criteria (need 2+ to justify cutting):**
- Usage below 5% AND declining trend (not just low -- declining)
- Support cost disproportionate to usage (feature generates 30% of tickets but 3% of usage)
- Blocks platform evolution (legacy feature prevents migration/modernization)
- Negative impact on new user experience (feature confuses onboarding without helping activation)

**Before cutting, check:**
- Is this feature used by high-value customers even if few in number? (revenue-weighted usage, not user-count-weighted)
- Is this feature contractually required for any enterprise deals?
- Can the feature be simplified rather than removed?

## Rationalization Table

| Rationalization | When It Appears | Why It Is Wrong |
|----------------|-----------------|-----------------|
| "Let's just use RICE scores to decide" | Prioritization meetings | RICE is backlog grooming, not strategy. It cannot express strategic bets, platform plays, or opportunity cost. Teams game RICE by inflating Reach estimates. |
| "We need to build it ourselves because buy won't be exactly right" | Build vs buy discussions | Customization cost is almost always less than building + maintaining from scratch. The 20% gap in functionality rarely matters; the 300% cost difference always does. |
| "Our NPS is high so we have PMF" | Board meetings, investor updates | NPS measures satisfaction of current users. If your sample is biased toward power users, NPS says nothing about the broader market. High NPS + high churn = no PMF. |
| "We should cascade OKRs down to every team equally" | Quarterly planning | Mechanical cascading creates alignment theater. Each team needs their own outcome that contributes to the company goal, not an arbitrary fraction of a shared metric. |
| "Let's add this feature -- three customers asked for it" | Feature request review | Three vocal customers are not a market signal. Check: what percentage of your TAM has this need? Are these customers representative or outliers? Loudest != most important. |
| "We'll figure out the metric later, let's ship first" | Sprint planning, hack weeks | If you cannot define what success looks like before building, you cannot tell whether you succeeded. You will ship, declare victory, and move on without learning. |
| "Our strategy is to build the best product" | Strategy offsites | This is a goal, not a strategy. Strategy requires tradeoffs -- who you serve (and who you don't), what you build (and what you won't), how you win (specifically). "Best product" is the absence of strategy. |
| "We can always pivot later" | Early-stage product decisions | Some decisions are hard to reverse: architecture choices, pricing model, target market reputation. Evaluate reversibility before treating a strategic bet as an experiment. |

## NEVER

- NEVER set OKRs where every Key Result is a deliverable ("ship X", "launch Y") -- these are task lists, not objectives; teams will ship and declare success even when the actual outcome doesn't improve
- NEVER use a single metric to assess product health -- DAU alone, NPS alone, revenue alone all hide critical problems; product health is a dashboard, not a number
- NEVER prioritize based solely on customer requests -- customers describe symptoms, not solutions; three customers asking for feature X may actually need a better version of feature Y
- NEVER change product vision more than once per year absent a genuine market shift -- frequent vision changes signal panic, not agility; teams cannot execute against a moving target
- NEVER treat RICE scores as objective truth -- every input is an estimate; two features scored 45 and 47 are effectively tied; false precision creates false confidence
- NEVER skip defining success criteria before building -- if you cannot state what metric moves and by how much, you cannot learn whether the work mattered
- NEVER build commodity capabilities in-house because "the off-the-shelf solution isn't perfect" -- the 20% gap in fit costs far less than 100% of building and maintaining it yourself
- NEVER launch a major feature without a kill/success metric and a review date -- features without exit criteria live forever, accumulating maintenance cost and UX complexity
- NEVER use "we're data-driven" as a reason to delay decisions when data won't arrive for months -- sometimes the cost of waiting exceeds the cost of being wrong; estimate reversibility and act accordingly
- NEVER cascade OKRs by splitting a parent metric equally across child teams -- this creates shared accountability where nobody is truly responsible; each team needs a distinct owned outcome
