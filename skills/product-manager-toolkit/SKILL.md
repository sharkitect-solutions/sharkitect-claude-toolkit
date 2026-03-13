---
name: product-manager-toolkit
description: >
  Use when the user needs feature prioritization (RICE scoring, backlog ranking, capacity planning),
  customer interview analysis (transcript parsing, insight extraction, cross-interview synthesis),
  PRD writing or review, or product discovery frameworks (opportunity mapping, hypothesis testing).
  NEVER use for marketing strategy or go-to-market campaigns (use marketing-strategy-pmm).
  NEVER use for project execution, sprint planning, or delivery tracking (use executing-plans).
  NEVER use for standalone user research methodology beyond interview transcript analysis.
version: 2.0
optimized: true
optimized_date: 2026-03-11
---

# Product Manager Toolkit

## File Index

| File | Purpose | When to use |
|------|---------|-------------|
| `scripts/rice_prioritizer.py` | RICE scoring, portfolio analysis, roadmap generation | Feature prioritization with CSV input, capacity planning |
| `scripts/customer_interview_analyzer.py` | NLP-based transcript analysis: pain points, JTBD, sentiment, themes | Single interview analysis or multi-interview aggregation |
| `references/prd_templates.md` | 4 PRD formats: Standard (11-section), One-Page, Agile Epic, Feature Brief | Any requirements documentation task |

## Scope Boundary

| This skill handles | Defer to |
|--------------------|----------|
| Feature prioritization (RICE, scoring, ranking) | -- |
| Customer interview transcript analysis | -- |
| PRD writing, review, and structure | -- |
| Product discovery frameworks | -- |
| Marketing strategy, GTM campaigns, positioning | marketing-strategy-pmm |
| Project execution, sprint management, delivery | executing-plans |
| Writing plans and roadmap documents | writing-plans |
| User research design (survey creation, study planning) | Out of scope (no skill) |

## Prioritization Trap Detection

RICE and similar frameworks produce systematically wrong answers in predictable situations. Detect and correct these before presenting results.

### When RICE Gives Wrong Answers

| Trap | Why RICE fails | Correction |
|------|---------------|------------|
| Infrastructure/platform work | Reach = 0 direct users, so score = 0. But every feature depends on it. | Score Reach as "all users of features this unblocks" with a time-decay factor. Or exempt from RICE entirely and allocate a fixed % (15-25%) of capacity. |
| Technical debt reduction | No visible user impact, so Impact = minimal. But velocity degrades without it. | Track "developer hours lost per quarter" as a proxy Reach metric. If velocity dropped >15% quarter-over-quarter, escalate debt items above RICE ranking. |
| Defensive features (security, compliance) | Low reach, low impact -- until a breach or audit failure. | Apply a "catastrophic multiplier": if the downside of NOT doing it is existential (data breach, regulatory fine, SOC2 failure), it bypasses RICE. |
| Overconfident Confidence scores | Teams rate Confidence: High on features they like, regardless of evidence. | Require evidence tiers: High = quantitative data from 50+ users; Medium = qualitative from 10+ interviews; Low = team opinion only. |
| Effort anchoring | Effort estimates cluster around "M" because teams avoid extremes. | Force calibration: pick the single easiest item (XS anchor) and hardest (XL anchor) first, then score everything relative to those anchors. |
| Reach inflation for B2B | "All enterprise customers" = 50 accounts, not 50,000 users. Score looks tiny. | Use revenue-weighted reach: Reach = number of accounts x average contract value. Normalize across the portfolio. |
| Feature cannibalization | Two features score high individually but compete for the same users. | Run overlap analysis: if >60% of Feature A's reach overlaps Feature B's, only count the incremental reach for the lower-scored one. |

### Confidence Calibration Table

| Confidence level | Required evidence | Typical accuracy |
|-----------------|-------------------|-----------------|
| High (100%) | A/B test data, 50+ user quantitative validation, or existing usage analytics | 80-90% of projected impact realized |
| Medium (80%) | 10+ qualitative interviews, competitor benchmarks, or analogous feature data | 50-70% of projected impact realized |
| Low (50%) | Team intuition, stakeholder request, or <5 data points | 20-40% of projected impact realized |

## PRD Quality Checklist

What separates a PRD that gets built from one that gets shelved:

### PRDs That Get Built (5 signals)
1. **Problem is quantified**: "Users spend 3.2 hours/week on manual data entry" not "Users find data entry frustrating"
2. **Success metric has a number and a date**: "Reduce churn from 8% to 5% within 90 days of launch" not "Improve retention"
3. **Out-of-scope is specific**: Names exact features/requests being deferred and explains why
4. **Engineering reviewed feasibility BEFORE the PRD was finalized**: Contains a "Technical Feasibility" section written or co-authored by an engineer
5. **Has a kill criteria**: "If adoption is below 10% after 30 days, we sunset and reallocate resources"

### PRDs That Get Shelved (5 anti-patterns)
1. Problem statement is a restatement of the solution ("Users need a dashboard" -- that is a solution, not a problem)
2. No clear owner or RACI -- everyone is "consulted," nobody is "accountable"
3. Success metrics are lagging indicators only (revenue, NPS) with no leading indicators (activation rate, feature adoption in week 1)
4. Timeline has no dependencies mapped -- treats the feature as if it exists in isolation
5. Written after the solution was already decided -- reverse-engineered justification, not genuine discovery

### PRD Template Selection

| Situation | Template | From `references/prd_templates.md` |
|-----------|----------|-------------------------------------|
| Major feature, 6+ weeks, cross-functional | Standard PRD (11-section) | Section 1 |
| Small feature, 2-4 weeks, single team | One-Page PRD | Section 3 |
| Sprint-based delivery, agile team | Agile Epic Template | Section 2 |
| Exploration phase, pre-commitment | Feature Brief | Section 4 |

## Interview Analysis: Expert Pitfalls

The `scripts/customer_interview_analyzer.py` extracts signals, but the PM must catch these systematic biases before acting on the output.

### Bias Detection Guide

| Bias | How to detect in transcript | What to do |
|------|---------------------------|------------|
| Confirmation bias | Interviewer follows up enthusiastically on answers that match their hypothesis, drops threads that don't | Re-read dropped threads. Count disconfirming evidence separately. If ratio of confirming:disconfirming > 5:1, suspect bias. |
| Leading questions | "Don't you think X would be helpful?" or "Would you say X is a problem?" | Flag any question containing "don't you," "would you say," or "wouldn't it be." Discount answers to leading questions. |
| Courtesy bias | Interviewee says everything is "great" or "sounds good" with no specifics | Look for behavioral evidence: "When did you last actually do X?" If they can't give a specific instance, discount the positive. |
| Survivorship bias | Only interviewed current users; didn't talk to churned users or non-adopters | Note if sample = current users only. Their pain points differ from why people leave or never sign up. |
| Recency bias | Interviewee anchors on last week's experience, not the pattern over months | Ask "Is this typical or was last week unusual?" Weight recurring patterns over one-time events. |
| Small sample extrapolation | PM treats 3 interviews as representative of 10,000 users | Minimum viable sample: 5 interviews for theme emergence, 12+ for pattern confidence, 20+ for segmentation. Below 5, label all findings as "hypotheses." |

### Cross-Interview Synthesis Procedure
1. Run analyzer on each transcript individually
2. Use `aggregate_interviews()` function to merge findings
3. Only promote a pain point to "validated" if it appears in 3+ independent interviews
4. Rank validated pain points by: (frequency across interviews) x (average severity)
5. Check for contradictions: if Interview A says "X is critical" and Interview B says "X doesn't matter," investigate the segment difference before averaging

## Stakeholder Alignment Failure Modes

When a PM thinks they have buy-in but actually don't:

| Failure mode | Warning sign | Prevention |
|-------------|-------------|------------|
| Silent disagreement | Stakeholder says "looks good" in meeting but never references the decision afterward | Ask explicitly: "What concerns do you have?" Silence is not agreement. Follow up async within 24h. |
| Scope creep as sabotage | Engineering lead keeps adding "must-have" requirements after sign-off | Lock scope with a signed-off doc. Any addition after lock requires a trade-off: "What do we cut to add this?" |
| Executive override | VP casually mentions a "small change" that invalidates the PRD | Treat any post-approval executive input as a formal change request. Assess impact on timeline and present trade-offs. |
| Different success definitions | PM measures adoption, engineering measures performance, sales measures pipeline | Align on ONE north star metric + 2-3 supporting metrics BEFORE kickoff. Document in PRD. |
| HIPPO override of data | Highest-Paid Person's Opinion overrides interview data or analytics | Present data first, opinion second. Frame as "the data suggests X -- do we have additional context that changes this?" |

## Metric Selection Traps

### Vanity vs. Actionable Metrics

| Vanity metric (avoid as primary) | Actionable alternative | Why |
|----------------------------------|----------------------|-----|
| Total registered users | Monthly active users (MAU) | Registrations include abandoned accounts |
| Page views | Time-to-value (first meaningful action) | Views don't indicate value delivery |
| App downloads | Day-7 retention rate | Downloads without retention = waste |
| "NPS score" in isolation | NPS segmented by cohort + follow-up action rate | Aggregate NPS hides segment problems |
| Feature usage count | Feature adoption rate (% of eligible users) | Raw count is meaningless without a denominator |

### Goodhart's Law in Product
"When a measure becomes a target, it ceases to be a good measure." Watch for:
- Team gaming activation metrics by lowering the bar (count "viewed dashboard" as "activated")
- Retention numbers improving because you made it harder to cancel, not because value increased
- Engagement metrics rising due to notification spam, not genuine interest
- Revenue per user increasing because low-value users churned (survivorship in metrics)

**Antidote**: Always pair a primary metric with a "health check" counter-metric. If conversion rate goes up, check that absolute conversions also increased (not just smaller denominator). If engagement rises, check that unsubscribe/mute rates haven't spiked.

## Rationalization Table

| Dimension | What this skill adds beyond Claude's base knowledge |
|-----------|-----------------------------------------------------|
| RICE trap detection | 7 specific scenarios where RICE produces systematically wrong rankings, with correction procedures |
| PRD quality signals | Concrete 5-signal checklist separating PRDs that ship from ones that stall, based on organizational behavior patterns |
| Interview bias catalog | 6 named biases with detection heuristics and minimum sample sizes for valid findings |
| Stakeholder failure modes | 5 alignment failures with early warning signs -- organizational dynamics Claude can't derive from PM textbooks |
| Metric traps | Vanity-vs-actionable mapping plus Goodhart's Law detection patterns specific to product contexts |
| Companion tooling | 3 scripts/references for deterministic execution of prioritization, analysis, and documentation |

## Red Flags

1. Presenting RICE scores for infrastructure work without applying the unblocking-reach correction
2. Treating 3 customer interviews as statistically significant for product decisions
3. Writing a PRD after the solution was already decided and engineering started
4. Using "total registered users" or "page views" as a primary success metric for a feature
5. Accepting Confidence: High on RICE scoring without requiring quantitative evidence
6. Finalizing a PRD without an explicit out-of-scope section and kill criteria
7. Skipping the cross-interview contradiction check when synthesizing multiple transcripts
8. Letting a stakeholder's "looks good" in a meeting count as formal alignment

## NEVER

1. NEVER present RICE rankings without checking for the 7 known trap conditions first
2. NEVER write a PRD problem statement that is actually a disguised solution statement
3. NEVER label interview findings as "validated" with fewer than 3 independent corroborating interviews
4. NEVER use a single metric without a counter-metric health check (Goodhart's Law protection)
5. NEVER skip the stakeholder alignment verification step -- silence is not agreement
