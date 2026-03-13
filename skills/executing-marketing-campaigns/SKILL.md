---
name: executing-marketing-campaigns
description: >
  Use when planning, structuring, or optimizing a marketing campaign --
  including channel selection, budget allocation, measurement setup, or
  diagnosing why a running campaign is underperforming.
  Also activate when the user asks about go-to-market execution, campaign
  calendars, or multi-channel coordination.
  NEVER for brand identity/voice work (use brand skills), pure copywriting
  without campaign context (use copywriting skills), or ad creative review.
---

# Executing Marketing Campaigns

## Campaign Type Decision Tree

Before doing anything, classify the request. The campaign type determines
every downstream decision -- framework, channel mix, timeline, and metrics.

```
What outcome does the user need?

  Generate pipeline / leads        --> DEMAND GEN       (references/campaign-frameworks.md #demand-gen)
  Launch a product or feature      --> LAUNCH           (references/campaign-frameworks.md #launch)
  Reduce churn / increase LTV      --> RETENTION        (references/campaign-frameworks.md #retention)
  Build brand awareness / category --> AWARENESS         (references/campaign-frameworks.md #awareness)
  Re-engage lapsed users           --> WIN-BACK         (references/campaign-frameworks.md #win-back)
  Test a new channel or message    --> EXPERIMENT       (references/campaign-frameworks.md #experiment)
  Multiple / unclear               --> Ask. Do NOT guess. Wrong type = wasted budget.
```

After classifying, pull the matching framework from the reference file. Each
framework includes timeline, channel mix, budget split, success metrics, and
kill criteria. Do not improvise these -- use the framework.

## Expert Rules (What Generic Advice Gets Wrong)

These are the practitioner insights that separate campaigns that work from
campaigns that "looked good on paper."

### 1. Measurement-First Principle
Set up tracking, attribution, and reporting BEFORE writing a single line of
copy. If you cannot measure the outcome before launch, do not launch. This
is the single highest-leverage rule in campaign execution.
- See references/measurement-frameworks.md for attribution setup.

### 2. Channel Selection > Creative Quality
The right message in the wrong channel produces zero results. The mediocre
message in the right channel still generates pipeline. Always validate
channel-audience fit before investing in creative polish.
- Channel selection guide: references/channel-playbooks.md

### 3. The 70/20/10 Budget Rule
- 70% to proven channels (known positive ROI from past data)
- 20% to testing (channels with signal but unproven at scale)
- 10% to experimental (new channels, no data yet)
Deviation requires explicit justification with data.

### 4. Pre-Launch Validation Kills "Launch and Hope"
Most campaigns fail because of no pre-launch validation, not bad execution.
Before full launch, always run:
- Message testing (3-5 variants, small audience, 48-72 hours)
- Landing page smoke test (paid traffic to measure conversion before scale)
- Internal dry run (full sequence walkthrough to catch broken links, wrong
  UTMs, missing tracking pixels)

### 5. Diminishing Returns Curve
Every channel has a saturation point. Signs you have hit it:
- CPA rising 20%+ week-over-week with no audience expansion
- Frequency > 3x per user per week on paid social
- Email list engagement dropping below 15% open rate
When you see these: stop scaling that channel. Diversify.

### 6. Cadence > Perfection
One consistent campaign per month outperforms one "perfect" campaign per
quarter. The compounding effect of regular audience touchpoints beats
sporadic brilliance every time. Build a campaign calendar, not a magnum opus.

## Anti-Pattern Decision Table

| Anti-Pattern | Why It Fails | What To Do Instead |
|---|---|---|
| Launching without measurement in place | Cannot prove ROI, cannot optimize, budget gets cut next quarter | Set up tracking + attribution first (references/measurement-frameworks.md) |
| Spreading budget equally across all channels | Ignores channel-audience fit; subsidizes underperformers | Use 70/20/10 rule; allocate by proven performance data |
| Optimizing for clicks/impressions instead of pipeline | Vanity metrics look good in reports but do not generate revenue | Define business metric (MQLs, SQLs, revenue) as primary KPI from day one |
| Running campaigns without audience segmentation | Same message to everyone = resonates with no one | Segment by pain point, buying stage, or persona before writing copy |
| "Always be launching" -- too-frequent sends | Campaign fatigue tanks engagement rates across all channels | Cap email to 2-3/week max; paid social frequency < 3x/user/week |
| No kill criteria before launch | Failing campaigns run too long, burning budget on hope | Define kill threshold at launch (e.g., "if CPA > $X after 500 clicks, pause") |
| Copying competitor campaigns without context | Their audience, budget, and goals are different from yours | Analyze competitor strategy; adapt the principle, not the execution |
| Treating channels as independent silos | Ignores cross-channel amplification and attribution overlap | Map the customer journey across channels; use multi-touch attribution |
| Skipping the post-mortem | Same mistakes repeat; no institutional learning | Run a structured post-mortem within 1 week of campaign end (references/measurement-frameworks.md #post-mortem) |

## Rationalization Table

| The User Says | They Actually Need | Why |
|---|---|---|
| "We need a viral campaign" | Awareness campaign with realistic reach targets | Virality is an outcome, not a strategy. Build for consistent reach. |
| "Let's do everything -- email, social, paid, events" | Channel prioritization based on audience data | Spreading thin = mediocre everywhere. Pick 2-3 channels max to start. |
| "Our campaign isn't working" | Campaign health diagnostic (see below) | "Not working" has 4 distinct failure modes. Diagnose before prescribing. |
| "We need more leads" | Demand gen campaign with pipeline metrics | "More leads" often means "more qualified leads." Define MQL criteria first. |
| "Competitor X is doing Y, we should too" | Competitive analysis then adapted strategy | Copying tactics without understanding strategy wastes budget. |
| "We just need better creative" | Full-funnel diagnosis | Creative is rarely the bottleneck. Usually it is targeting or channel fit. |
| "Can we just boost this post?" | Paid social strategy with targeting and measurement | Boosting without targeting burns budget. Set up proper paid campaigns. |

## NEVER List

- NEVER launch a campaign without measurement and attribution configured first
- NEVER allocate budget without historical channel performance data or a test plan
- NEVER optimize toward vanity metrics (impressions, likes) as the primary KPI
- NEVER skip audience segmentation -- "everyone" is not a target audience
- NEVER run a campaign longer than 2 weeks past its kill criteria threshold
- NEVER copy a competitor's campaign without analyzing why it works for their audience
- NEVER send more than 3 marketing emails per week to the same segment
- NEVER present campaign results without comparing to pre-defined success metrics

## Campaign Health Diagnostic

When a user says a campaign is "not working," diagnose which stage is broken:

```
Funnel Stage     | Symptom                  | Root Cause Area        | Fix Direction
-----------------+--------------------------+------------------------+---------------------------
Awareness        | Low impressions/reach    | Channel or targeting   | Expand audience, test new
                 |                          |                        | channels, increase budget
Interest         | Low CTR (< 1% display,   | Creative or messaging  | Test new headlines, value
                 | < 2% email, < 3% search)|                        | props, or CTAs
Conversion       | Low conversion rate      | Offer or landing page  | Simplify page, strengthen
                 | (< 2% landing page)     |                        | offer, reduce form fields
Retention        | High churn post-convert  | Expectation mismatch   | Align campaign promise with
                 |                          |                        | actual product experience
```

Work top-down. An awareness problem makes everything downstream look broken.
Fix the highest stage first.

## Workflow: Campaign Build Sequence

After classifying campaign type and pulling the framework:

1. **Measurement setup** -- tracking, UTMs, attribution model, reporting dashboard
2. **Audience definition** -- segments, personas, exclusions
3. **Channel selection** -- pick 2-3 based on audience data + 70/20/10 budget rule
4. **Message development** -- per-channel messaging, value props, CTAs
5. **Pre-launch validation** -- message test, landing page smoke test, internal dry run
6. **Launch** -- staggered rollout, monitor first 48 hours closely
7. **Optimization** -- weekly review cadence, reallocate budget based on data
8. **Post-mortem** -- within 1 week of campaign end, structured review

Each step has detailed checklists in the reference files.

## References

- `references/campaign-frameworks.md` -- Campaign architecture by type (launch, demand gen, retention, awareness, win-back, experiment)
- `references/channel-playbooks.md` -- Per-channel execution checklists and optimization guides
- `references/measurement-frameworks.md` -- Attribution models, metric hierarchies, reporting templates, post-mortem framework
