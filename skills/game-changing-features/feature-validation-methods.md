# Feature Validation Methods

Load when testing a feature hypothesis before full investment, designing a validation experiment, choosing between validation approaches, or assessing evidence quality for product decisions.

## Validation Method Selection

First-match. Choose the method that fits your constraints.

| Constraint | Method | What It Proves | Time | Cost |
|-----------|--------|---------------|------|------|
| Need demand signal before any code | Fake door test | Users WANT this (click intent) | 1-3 days | Near zero |
| Need behavioral data, product exists | Painted door test | Users DISCOVER and ATTEMPT this (in-product intent) | 1-2 weeks | Low (UI changes only) |
| Need to test the value proposition, not the implementation | Wizard of Oz | Users GET VALUE from the outcome (regardless of how it's produced) | 2-4 weeks | Medium (manual labor) |
| Need to test willingness to pay | Pre-order / waitlist | Users will PAY for this (not just "interested") | 1-2 weeks | Low |
| Need to test the full experience | Concierge MVP | The full workflow works and delivers value (manual, unscaled) | 4-8 weeks | Medium-high (manual labor at scale) |
| Need to test at scale with real code | Beta / feature flag | The feature works at scale and metrics move | 4-12 weeks | High (real development) |

## Fake Door Test

Present a feature that doesn't exist yet. Measure how many users try to use it.

| Element | Implementation |
|---------|---------------|
| Placement | Button, menu item, or card in the product UI where the feature would naturally live |
| Interaction | User clicks -> sees "Coming soon! Join the waitlist" or "We're building this -- what would you use it for?" |
| Measurement | Click-through rate on the fake door. Compare to other feature CTAs for baseline. |
| Sample size | Minimum 1,000 users exposed. CTR below 2% = weak signal. CTR above 5% = strong signal. |
| Duration | 1-2 weeks. Remove after collecting sufficient data. |

**Fake door ethics**: Always be transparent. "Coming soon" is honest. "Click here to use Feature X" that leads to a 404 is deceptive and erodes trust. The user should feel they discovered an upcoming feature, not that they were tricked.

**Fake door failure modes**:
- Placement bias: putting the fake door in a high-traffic area inflates CTR. Place it where the feature would ACTUALLY live.
- Curiosity clicks: users click to explore, not because they want the feature. Add a follow-up question ("What would you use this for?") to separate curiosity from intent.
- Channel contamination: if you announce the feature externally (blog, email), fake door CTR reflects marketing reach, not product demand.

## Painted Door Test

Like a fake door, but INSIDE the product workflow at the moment of need.

| Element | Implementation |
|---------|---------------|
| Trigger | User reaches a point where the new feature would solve their current problem |
| Presentation | "Try [Feature X] to solve this?" with a CTA button |
| Measurement | % of users who click at the moment of need (intent-to-use rate) |
| Advantage over fake door | Measures demand IN CONTEXT, not exploratory curiosity |

**Painted door example**: User is in the export flow, struggling with formatting. A banner appears: "Auto-format your export? [Try it]". Click rate at this moment measures demand for auto-formatting among users who actually need it -- far more reliable than a menu item CTR.

## Wizard of Oz

Users believe they're using a real feature. Behind the scenes, a human performs the work manually.

| Element | Implementation |
|---------|---------------|
| Frontend | Real UI that looks and feels like the feature is automated |
| Backend | Human operators perform the task manually (or semi-manually with tools) |
| Measurement | Task success rate, user satisfaction, willingness to pay, time-to-value |
| Best for | AI features, recommendation engines, curation, personalization -- anything where the OUTPUT matters more than the mechanism |

**Wizard of Oz traps**:
- Latency expectation mismatch: if the "AI feature" takes 3 seconds in WoZ (because a human is fast) but would take 30 seconds when automated, you're testing the wrong experience. Match expected production latency.
- Quality ceiling: human operators may produce BETTER results than the automated version will. Validate that 80% quality (realistic for automation) still satisfies users.
- Scale limit: WoZ can handle 10-50 users. If you need 500+ users for statistical significance, WoZ is too slow. Use it for qualitative validation, not quantitative.

## Pre-Order and Waitlist Validation

The strongest demand signal: users commit money or email before the feature exists.

| Method | What It Proves | Implementation |
|--------|---------------|----------------|
| Waitlist with email | Interest (weak signal -- email costs nothing) | Landing page with value proposition + email capture. Track: signup rate, email open rate when you follow up. |
| Waitlist with commitment action | Stronger interest | Require more than email: fill out a survey, describe their use case, schedule a demo. Friction filters casual interest. |
| Pre-order with payment | Willingness to pay (strong signal) | Accept payment for the feature before it exists. Refund if you don't build it. This is the gold standard for B2C. |
| Letter of intent (B2B) | Enterprise demand | Non-binding agreement that the company will purchase if the feature is built to spec. Common in B2B SaaS. |

**The waitlist inflation problem**: 10,000 waitlist signups sounds impressive. But: what % will actually activate when the feature launches? Industry benchmarks: 10-30% of waitlist signups try the feature. 3-10% become active users. Size your expectations accordingly.

## Evidence Quality Tiers

Not all validation evidence is equal. Classify your evidence before making decisions.

| Tier | Evidence Type | Reliability | Decision Scope |
|------|-------------|-------------|----------------|
| **Tier 1: Behavioral** | Users DID the thing (analytics, purchase data, usage logs) | Highest | Can justify major investment (6+ month build) |
| **Tier 2: Experimental** | Users did the thing in a controlled test (A/B test, prototype test, beta) | High | Can justify medium investment (1-3 month build) |
| **Tier 3: Stated preference** | Users SAID they would do the thing (interviews, surveys, feature votes) | Medium | Can justify lightweight validation (fake door, WoZ) |
| **Tier 4: Proxy** | Similar users did the thing in a different product (competitor data, market research) | Low | Can justify exploration (research spike, concept testing) |
| **Tier 5: Opinion** | Stakeholders believe the thing should be built (founder intuition, board input) | Lowest | Can justify a conversation, not a commitment |

**Evidence escalation rule**: Never commit resources at a higher level than your evidence supports. Tier 5 evidence (opinion) gets a 1-week research spike, not a 3-month build. To justify a 3-month build, you need Tier 2-3 evidence minimum.

## Validation Sequencing

Run validations in order of cost and commitment. Stop when evidence is sufficient or insufficient.

| Phase | Method | Cost | Go/No-Go Signal |
|-------|--------|------|-----------------|
| 1. Desk research | Competitor analysis, market reports, support ticket mining | 1-2 days, $0 | Is anyone else solving this? Is there demand signal in our own data? |
| 2. Qualitative | 5-10 user interviews, focusing on the problem (not the solution) | 1-2 weeks, $0-500 | Do users recognize and care about this problem? |
| 3. Lightweight quantitative | Fake door test, painted door test, or survey | 1-2 weeks, $0-1000 | Do users ACT on the opportunity when presented? (>5% CTR) |
| 4. Solution validation | Wizard of Oz, prototype test, concierge MVP | 2-8 weeks, $1K-10K | Does the solution actually deliver value? Would users pay? |
| 5. Scale validation | Beta launch, feature flag rollout to 10% of users | 4-12 weeks, $10K-100K+ | Do metrics move at scale? Does the feature sustain engagement past novelty? |

**The skip trap**: Teams skip phases 1-3 and jump straight to building (phase 5) because "we already know users want this." This is the #1 cause of features that ship and nobody uses. The 2 weeks spent on phases 1-3 save 12 weeks of building the wrong thing.

## Kill Criteria

Define kill criteria BEFORE starting validation. Without pre-committed kill criteria, teams rationalize weak results.

| Validation Phase | Kill If |
|-----------------|---------|
| Desk research | No competitor or adjacent solution exists AND no support tickets mention the problem |
| User interviews | Fewer than 3 of 10 interviewees describe the problem unprompted |
| Fake door / painted door | CTR < 2% after 1,000+ exposures |
| Wizard of Oz | User satisfaction < 7/10 OR willingness to pay < 30% of target price point |
| Beta | Feature adoption < 20% of eligible users after 4 weeks OR retention impact not statistically significant |

**The "almost" trap**: "CTR was 1.8%, which is ALMOST 2%." Almost doesn't count. Kill criteria exist to prevent motivated reasoning. If the result is borderline, the hypothesis is weak -- which is itself useful information. Move on.
