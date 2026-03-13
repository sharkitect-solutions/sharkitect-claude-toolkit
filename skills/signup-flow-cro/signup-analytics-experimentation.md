# Signup Analytics & Experimentation

Load when setting up signup flow measurement, planning A/B tests on registration forms, or interpreting signup conversion data.

## Field-Level Tracking Implementation

Most analytics tools track page-level events. Signup optimization requires field-level granularity.

### What to Track Per Field

| Event | When to Fire | Data to Capture | Why It Matters |
|---|---|---|---|
| Field focus | User clicks/tabs into field | Field name, timestamp, device type | Measures form start rate and field engagement sequence |
| Field blur (without value) | User leaves field empty | Field name, time spent focused, previous field | Identifies intimidating or confusing fields |
| Field completed | User enters valid value and moves on | Field name, time to complete, input method (typed/autofilled/pasted) | Autofilled fields that still show high abandon = label/UX problem |
| Field error shown | Validation triggers | Field name, error type, value length | High error rates = unclear requirements or wrong input type |
| Field error resolved | User fixes validation error | Field name, time to resolve, attempts | Slow resolution = confusing error message |
| Form submitted | Submit button clicked | All field completion flags, total time, error count | Completion rate denominator |
| Form abandoned | Tab close/navigate away without submit | Last field interacted with, fields completed, time on form | Identifies the specific abandonment field |

### Abandonment Detection

Browser `beforeunload` is unreliable (doesn't fire on mobile tab close, blocked by some browsers). Use multiple signals:

| Detection Method | Reliability | Coverage |
|---|---|---|
| `visibilitychange` to `hidden` | High | Tab switch, minimize, mobile home button |
| `pagehide` event | High | Navigation away, tab close (mobile-friendly) |
| `beforeunload` event | Medium | Desktop tab close (unreliable on mobile) |
| Heartbeat (send ping every 30s, detect when it stops) | High | Covers all cases but requires server-side timeout logic |
| Last field interaction + no submit within 2 minutes | Medium | Works without browser events but has false positives for slow typists |

**Recommended**: Use `visibilitychange` as primary trigger, `pagehide` as fallback, heartbeat for server-side validation. Fire abandonment event with last-interacted field and completion state.

## Funnel Math for Signup Optimization

### Conversion Rate Decomposition

Don't track a single "signup conversion rate." Decompose it:

```
Page visitors
  -> Form viewers (scrolled to form): Page engagement rate
  -> Form starters (focused first field): Form start rate
  -> Form completers (submitted): Form completion rate
  -> Account created (no server error): Submit success rate
  -> Activated (completed key action): Activation rate
```

Each stage has different optimization levers:

| Stage Drop | Likely Cause | Optimization Target |
|---|---|---|
| Low page engagement | Value prop unclear, page too long, form below fold | Page layout, headline, CTA visibility |
| Low form start | Too many visible fields, no trust signals, commitment anxiety | Field count, trust badges, "takes 30 seconds" copy |
| Low form completion | Specific field causing abandonment, error frustration, mobile issues | Field-level analysis, error handling, keyboard optimization |
| Low submit success | Server errors, duplicate email handling, rate limiting | Error handling, graceful degradation, clear error messages |
| Low activation | Onboarding friction, unclear next step, email verification wall | Post-signup flow (defer to onboarding-cro) |

### Cohort-Based Analysis

Single conversion rates hide trend changes. Track signup cohorts weekly:

| Cohort Week | Visitors | Started Form | Completed | Completion Rate | Activation Rate (7-day) |
|---|---|---|---|---|---|
| Week 1 | 1,000 | 450 | 270 | 60.0% | 45% |
| Week 2 (changed CTA) | 1,100 | 520 | 330 | 63.5% | 47% |
| Week 3 (added field) | 950 | 430 | 215 | 50.0% | 48% |

Week 3 shows: adding the field improved activation (+1%) but killed completion rate (-13.5%). Net effect depends on absolute numbers. Calculate revenue impact, not just rates.

## A/B Testing Signup Flows: Statistical Pitfalls

### Sample Size Requirements

Signup flow changes affect small conversion differences. Small differences need large samples.

| Baseline Rate | Minimum Detectable Effect | Sample Size Per Variant | At 10K visitors/month |
|---|---|---|---|
| 50% completion | 5% relative (50% -> 52.5%) | 6,000 | 5-6 weeks per test |
| 50% completion | 10% relative (50% -> 55%) | 1,600 | 2 weeks per test |
| 10% trial-to-paid | 10% relative (10% -> 11%) | 14,000 | 14 weeks per test |
| 10% trial-to-paid | 20% relative (10% -> 12%) | 3,600 | 4 weeks per test |

**Reality check**: Most startups cannot run signup A/B tests with statistical validity. At <5K visitors/month, use before/after comparisons with cohort analysis instead of formal A/B tests.

### Common Testing Mistakes in Signup Flows

| Mistake | Why It Happens | Consequence | Fix |
|---|---|---|---|
| Testing too many variants | "Let's test 4 different forms" | Sample dilution, no variant reaches significance | Maximum 2 variants (control + one change) |
| Measuring wrong metric | Optimizing form completion rate without tracking activation | More signups but worse quality users | Always track downstream metric (7-day activation, trial-to-paid) |
| Stopping test early on positive | "We're winning, ship it!" after 3 days | False positive rate 30%+ with early stopping | Pre-commit to sample size. Use sequential testing if you must peek. |
| Not segmenting mobile/desktop | Overall result is flat but mobile improved 20% and desktop dropped 15% | Missing a real improvement hidden by device mix | Run analysis by device. Consider device-specific experiences. |
| Testing during traffic spike | Launch on Product Hunt, test during the spike | PH traffic is fundamentally different from steady-state | Exclude non-organic traffic spikes from test analysis |
| Ignoring novelty effect | New design shows 15% lift in week 1, normalizes to 3% by week 4 | Shipped based on inflated early results | Run tests for minimum 2 full weeks. Compare week 1 vs week 2+ results. |

### Sequential Testing for Low-Traffic Sites

When you can't wait for full sample sizes, use sequential testing with spending functions:

| Week | Cumulative Sample | Alpha Spent | Significance Threshold |
|---|---|---|---|
| 1 | 500 | 0.001 | p < 0.001 (only stop if massive effect) |
| 2 | 1,000 | 0.005 | p < 0.005 |
| 3 | 1,500 | 0.015 | p < 0.015 |
| 4 (final) | 2,000 | 0.050 | p < 0.050 (standard threshold) |

This lets you stop early for big wins while protecting against false positives. Use O'Brien-Fleming spending function (most conservative at early looks).

## Interpreting Signup Data

### Signals That Look Bad but Are Fine

| Signal | Why It Seems Bad | Why It's Actually OK |
|---|---|---|
| Low form start rate (20%) on pricing page | Most visitors aren't starting signup | High-intent visitors self-select. The 20% who start are qualified. Low start rate from pricing page is normal. |
| Mobile completion rate 15% lower than desktop | Mobile is underperforming | If mobile traffic is mostly discovery (blog, social), intent is lower. Compare mobile-from-ads vs desktop-from-ads for fair comparison. |
| Completion rate dropped after removing a field | "Fewer fields should mean higher completion" | Removed field may have been a commitment device. Some fields increase perceived value (use-case question makes product feel personalized). |
| Social auth adoption only 15% | "Nobody uses social auth" | 15% is actually solid. Social auth users typically have 2x higher activation rates. The 15% overperforms on downstream metrics. |

### Signals That Look Good but Are Dangerous

| Signal | Why It Seems Good | Why It's Actually Bad |
|---|---|---|
| 90%+ form completion rate | "Our form converts great!" | If activation rate is <20%, you're making it too easy to sign up for uncommitted users. Some friction is intentional filtering. |
| High signup volume from a specific channel | "This channel is crushing it" | Check activation rate by channel. Some channels (AppSumo, PH) drive high signups but 5-10% activation. CAC per activated user may be worse. |
| A/B test shows 20% completion lift | "Ship it immediately" | If the winning variant removed a qualification field, you may get more signups but worse user quality. Track 30-day retention by variant before declaring winner. |

## Privacy & Compliance for Signup Analytics

| Requirement | Applies When | Implementation |
|---|---|---|
| Cookie consent before tracking | EU visitors (GDPR), California (CCPA) | Essential signup analytics (form errors, completion) can be classified as strictly necessary. Field-level behavioral tracking requires consent. |
| Data minimization | Always | Don't log actual field values in analytics events. Track field name, timing, and completion status only. Never log passwords or sensitive data in analytics. |
| Right to deletion | GDPR, CCPA | Analytics events linked to user ID must be deletable. Use anonymized session IDs for pre-signup analytics, link to user ID only after account creation. |
| Transparency | GDPR Article 13 | Disclose field-level tracking in privacy policy if capturing keystroke timing, mouse movement, or similar behavioral data. |
