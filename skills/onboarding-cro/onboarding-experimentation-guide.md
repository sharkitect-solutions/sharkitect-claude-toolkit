# Onboarding Experimentation Guide

Load when running onboarding A/B tests, planning an optimization roadmap, or troubleshooting why onboarding experiments produce inconclusive results.

## Why Onboarding Experiments Are Different

Standard A/B testing assumptions break down in onboarding. Understanding why prevents wasted experiments.

| Standard Assumption | Why It Breaks in Onboarding | Consequence |
|---|---|---|
| Large sample size available | Only NEW users enter onboarding. Existing users never see it. | Tests run 5-20x slower than in-product tests. A site with 10K DAU but 200 daily signups needs months, not days. |
| Users are interchangeable | New user composition shifts with marketing spend, seasonal campaigns, PR mentions | Week 1 signups (organic) differ from Week 3 signups (paid campaign). Randomize by signup cohort, not time period. |
| Short feedback loop | Activation may take 3-7 days. Retention signal takes 14-30 days. | You cannot call a winner after 3 days. Minimum test duration = activation horizon + buffer. |
| Low stakes per variant | A bad onboarding variant permanently loses first-time users | Those users never return for the "good" variant. Run minimum viable tests, cap variant exposure if risky. |
| Metric moves quickly | Activation rate changes slowly because it is a % of a growing denominator | Use rate-based metrics, not absolute counts. Monitor daily rate, not cumulative. |

## Experiment Design for Onboarding

### Sample Size Calculation

Use the standard formula but adjust for onboarding-specific constraints:

| Parameter | Typical Value | Onboarding-Specific Adjustment |
|---|---|---|
| Baseline conversion (activation rate) | Varies (20-60%) | Use last 30 days of new user activation rate, NOT all-time average |
| Minimum detectable effect (MDE) | 5-10% relative lift | For onboarding, target 10%+ MDE. Small lifts are hard to detect at new-user volumes. |
| Statistical significance | 95% (p < 0.05) | Keep at 95%. Onboarding decisions are hard to reverse -- you want high confidence. |
| Power | 80% | Keep at 80%. |
| Daily new users | Your signup volume | This is the bottleneck. 100 signups/day = 2-3 month tests for 10% MDE. |

**Duration floor**: Never run an onboarding test for less than 2 full weeks, even if sample size is reached earlier. Day-of-week effects change signup composition (weekend vs weekday signups behave differently).

### Holdback Group Design

A holdback group proves that onboarding guidance itself adds value. Without it, you are optimizing within a range but don't know if the range is above zero.

| Design | How It Works | When to Use |
|---|---|---|
| No-onboarding holdback | 5-10% of users skip onboarding entirely and land in the raw product | Once, when establishing that onboarding has value at all. If holdback retains similarly, your onboarding is theater. |
| Minimal onboarding holdback | Show only a single welcome screen vs full onboarding flow | When testing whether multi-step onboarding justifies its complexity. |
| Feature holdback | Disable a specific onboarding feature (e.g., checklist) for 10% of users | When measuring the incremental value of a specific component. |

**Holdback ethics**: Holdback groups in onboarding directly impact real users' first experience. Cap holdback at 5-10% of new users. Never holdback on enterprise/high-value accounts. Run for the minimum duration needed for significance.

## Experiment Catalog by Onboarding Component

### First-Run Experience Experiments

| Experiment | Hypothesis | Primary Metric | Watch Metric |
|---|---|---|---|
| Wizard vs product-first | Guided setup increases activation for complex products | Activation rate | Time to activation (wizard may slow down fast users) |
| 3-step vs 5-step wizard | Fewer steps reduce drop-off without losing personalization | Wizard completion rate | Activation rate (fewer steps may mean less personalization) |
| Question order (role first vs goal first) | Leading with goal creates stronger motivation framing | Step 2 completion rate | Personalization quality (wrong question order may misclassify users) |
| Pre-populated demo vs blank slate | Demo data shows value faster for complex products | First-session feature usage | "Created own project" rate (demo data may reduce ownership) |

### Checklist Experiments

| Experiment | Hypothesis | Primary Metric | Watch Metric |
|---|---|---|---|
| 3 items vs 5 items | Fewer items increase completion rate | Checklist completion rate | Activation rate (fewer items may skip critical steps) |
| Endowed progress (1/5 pre-checked) vs fresh (0/5) | Pre-checked step creates momentum per Nunes & Dreze 2006 | Checklist completion rate | User satisfaction (some users find pre-checking dishonest) |
| Fixed order vs user-chosen order | Autonomy increases engagement for power users | Per-item completion rates | Activation rate (wrong order may miss dependencies) |
| Persistent sidebar vs dismissible modal | Persistent reminder drives completion | Checklist completion rate | Feature usage depth (sidebar may crowd product UI) |

### Email Sequence Experiments

| Experiment | Hypothesis | Primary Metric | Watch Metric |
|---|---|---|---|
| 4-email sequence vs 2-email sequence | More touchpoints recover more stalled users | Reactivation rate | Unsubscribe rate (too many emails drives opt-out) |
| Value-focused vs help-focused day 3 email | Restating value is more motivating than offering help for self-serve products | Email click-through -> activation | Reply rate (help-focused generates more replies, which may convert via conversation) |
| Personal sender vs brand sender | Personal name ("Sarah from Acme") increases open rate | Email open rate | Trust (fake personalization can backfire if user replies and gets a bot) |
| Send time (morning vs afternoon) | Afternoon emails catch users when they have work bandwidth | Open rate | Activation rate (opened doesn't mean acted on) |

## Measurement Pitfalls

| Pitfall | What Goes Wrong | Prevention |
|---|---|---|
| Peeking at results early | Seeing a positive trend, stopping the test, declaring a winner. But the trend reverses with more data. | Pre-register test duration and sample size. Do not check results before the pre-registered end date. |
| Simpson's Paradox | Variant B wins overall but loses in every segment. Caused by unequal segment distribution across variants. | Always check segment-level results. If variant B only wins because it got more organic users, it didn't win. |
| Novelty effect | New onboarding variant is "interesting," driving short-term engagement that fades. | Run tests for 4+ weeks. Compare week 1 lift vs week 4 lift. If declining, it is novelty, not improvement. |
| Survivor bias | Measuring activation rate only among users who completed step 1. Users who dropped at step 1 are invisible. | Measure from signup (intent-to-treat), not from onboarding start. Include all randomized users in the denominator. |
| Metric gaming | Optimizing checklist completion by making items trivially easy (auto-completing steps). | Checklist completion is not the goal. Activation rate and retention are. Easy checklists produce "completed but not activated" users. |
| Interaction effects | Testing wizard step count AND email sequence simultaneously. Can't tell which caused the lift. | One major test per onboarding stage at a time. Use a testing roadmap that sequences experiments. |

## Experiment Prioritization

Use ICE scoring adapted for onboarding constraints:

| Factor | Score 1-10 | Onboarding-Specific Guidance |
|---|---|---|
| **I**mpact | Expected lift on activation rate | Experiments targeting the highest-drop-off step score highest. |
| **C**onfidence | How sure are you this will work? | Data-backed hypotheses (from drop-off analysis) > opinion-based. Prior test results in similar products increase confidence. |
| **E**ase | How fast can you implement and get results? | Factor in test duration (new-user volume). A high-impact test that takes 4 months to reach significance may not be "easy." |

**Roadmap rule**: Prioritize experiments that target the single biggest drop-off point in the onboarding funnel. Fix the biggest leak before experimenting on smaller ones. A 5% improvement at a 60% drop-off step is worth more than a 20% improvement at a 5% drop-off step.

## When NOT to Experiment

| Situation | Do Instead |
|---|---|
| Activation event is undefined | Define it first (see activation-analysis-playbook.md). Experimenting without knowing what success looks like is waste. |
| <50 daily signups | You don't have enough volume for statistical significance in a reasonable timeframe. Use qualitative methods: user interviews, session recordings, usability testing. |
| Onboarding has obvious bugs or UX failures | Fix the bugs. You don't need an A/B test to know that a broken form field should be fixed. Experimentation is for optimization, not bug detection. |
| The product itself doesn't deliver value | Onboarding optimization cannot compensate for a product that doesn't solve a real problem. If users who complete onboarding still churn, the problem is the product. |
