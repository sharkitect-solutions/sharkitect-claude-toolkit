# Viral Loop Analytics for Generators

## K-Factor Measurement for Generators

Generators have a unique viral loop: the result IS the share content. This makes K-factor measurement different from standard viral products.

### Generator-Specific K-Factor Formula

```
K = Completion Rate x Share Rate x Shares per Sharer x Click-Through Rate x Completion Rate (new user)

Where:
- Completion Rate = % of visitors who complete the generator (land -> result)
- Share Rate = % of completers who share their result (any channel)
- Shares per Sharer = average number of shares per sharing user (usually 1.0-1.5 for generators)
- Click-Through Rate = % of share viewers who click through to the generator
- Completion Rate (new) = % of referred visitors who complete the generator themselves
```

| Component | Generator Benchmark | How to Measure |
|---|---|---|
| Completion Rate | 50-80% (depends on input count) | Google Analytics funnel: landing page -> result page. Or custom event tracking |
| Share Rate | 5-15% organic, 15-30% with good UX | Track share button clicks + `navigator.share()` calls. Estimate screenshot shares at 2-3x button shares |
| Shares per Sharer | 1.0-1.5 | Most generator users share once. Some share to multiple platforms. Track unique share events per user session |
| Click-Through Rate | 2-8% | UTM-tagged share links. Compare share volume (from button clicks) to referred visits (from UTM tracking) |
| New User Completion Rate | 40-65% (lower than organic because some visitors aren't the target audience) | Referred visitor funnel: landing -> result. Segment by referral source |

**Typical generator K-factors**: 0.1-0.3 (baseline), 0.3-0.7 (good), 0.7-1.0 (strong viral), >1.0 (exponential -- very rare, usually short-lived). BuzzFeed quizzes at peak achieved K > 2.0, but this was pre-algorithm-change Facebook. Modern realistic ceiling: K = 0.5-0.8 for well-optimized generators.

## Tracking Implementation

### Essential Events to Track

| Event | When to Fire | Properties to Capture | Why |
|---|---|---|---|
| `generator_start` | User enters first input or clicks "Start" | generator_id, source (organic/referred/ad), device_type | Measures entry rate. Compare to page views for start rate |
| `generator_progress` | Each question/step completed | step_number, total_steps, time_on_step | Identify which question causes most drop-offs |
| `generator_complete` | Result displayed | result_type, time_to_complete, input_count | Completion rate and result distribution |
| `share_click` | Share button clicked (any platform) | platform (twitter/facebook/copy/native), result_type | Which platforms and results drive sharing |
| `share_complete` | Share confirmed (not all platforms report this) | platform, result_type | Actual shares vs button clicks (many users click then cancel) |
| `referral_land` | Referred visitor arrives (UTM or referral param detected) | referrer_result, source_platform | Where referred traffic comes from |
| `referral_complete` | Referred visitor completes generator | referrer_result, new_result, source_platform | Full viral loop closure |

### UTM Strategy for Generator Shares

| Parameter | Value Pattern | Example |
|---|---|---|
| `utm_source` | Platform name | `twitter`, `facebook`, `whatsapp`, `copy-link` |
| `utm_medium` | Always "share" for organic shares | `share` |
| `utm_campaign` | Generator ID | `personality-quiz-v2` |
| `utm_content` | Result type | `midnight-architect` |

This lets you answer: "Which result type drives the most referred traffic?" and "Which platform has the highest share-to-visit conversion?"

## Cohort Analysis for Generators

### Daily Cohort Metrics

| Metric | What to Track | Healthy | Warning |
|---|---|---|---|
| **Daily completions** | Total generator completions per day | Stable or growing | Declining >10% week-over-week (content fatigue) |
| **Organic vs referred split** | % of completions from organic traffic vs shared links | 40-60% referred at peak viral | <20% referred = viral loop isn't working |
| **Result distribution shift** | Are certain results becoming more/less common over time? | Stable distribution | If one result trends upward, it may be because shared results attract similar people (selection bias) |
| **Share rate by day** | Does share rate decay over time? | First 7 days highest, then stabilizes | Sharp drop after day 3 = "novelty wear-off." Need to refresh content or add new features |
| **Viral generation** | Track how many "generations" of sharing occur. Gen 0 = organic, Gen 1 = shared by Gen 0, Gen 2 = shared by Gen 1 | Gen 2-3 visible | Gen 0 only = no viral loop. Users share but nobody shares the share |

### Result-Level Analytics

Not all results are equally viral. Measure per result type.

| Metric | Per-Result Insight | Action If Low |
|---|---|---|
| **Share rate per result** | Which results get shared most? | Low-share results may need better visual design, more flattering language, or more identity signal |
| **Click-through per result** | Which shared results drive the most clicks? | Low-CTR results may have boring share cards or OG images that reveal too much |
| **Viral coefficient per result** | Which results produce the highest K-factor end-to-end? | Focus design effort on high-K results. Consider making them slightly rarer (rarity increases share motivation) |
| **Sentiment per result** | Do certain results get positive or negative reactions? | Monitor comments on shared results. Negative reactions = users feel labeled negatively |

## A/B Testing Viral Features

### What to Test (Priority Order)

| Priority | Test | Expected Impact | Minimum Sample |
|---|---|---|---|
| 1 | **Share card design** (visual style, text size, reveal level) | 20-50% improvement in share-to-click rate | 500 shares per variant |
| 2 | **Share button placement** (above fold, below result, sticky) | 10-30% improvement in share rate | 1,000 completions per variant |
| 3 | **Pre-written share text** variations | 10-25% improvement in share rate | 1,000 completions per variant |
| 4 | **Result page layout** (result size, description length, CTA position) | 5-15% improvement in share rate | 2,000 completions per variant |
| 5 | **Input optimization** (fewer questions, different question types) | 10-30% improvement in completion rate | 500 starts per variant |

### Generator-Specific A/B Testing Gotchas

| Gotcha | What Goes Wrong | How to Avoid |
|---|---|---|
| **Network effects confound results** | Variant A goes viral, driving traffic to variant B through shared links that don't preserve the variant assignment | Use sticky variant assignment by user (cookie or fingerprint). Ensure shared links carry the variant through to new users |
| **Result distribution varies by variant** | If variant A changes questions, the result distribution changes. Comparing share rates across different result distributions is comparing apples to oranges | Measure share rate PER RESULT TYPE, not just overall. Or force the same result distribution in both variants |
| **Viral lag** | Changes to share card design affect clicks 24-48 hours later (social platform caching). Results look the same for days, then diverge | Wait at least 72 hours before checking results. Social platform image caches need time to refresh |
| **Screenshot shares unmeasurable** | A/B test shows no change in share BUTTON clicks, but actual sharing (via screenshot) may have changed | Use qualitative signals: monitor social mentions, track branded search, survey users on how they shared |

## Retention and Re-Engagement

Generators are typically one-time-use. Building return visits requires deliberate mechanics.

| Mechanic | How It Works | Expected Impact | Implementation Effort |
|---|---|---|---|
| **New quiz variants** | "You took the Career Quiz -- try our Personality Quiz!" | 20-40% of completers try a second quiz within 7 days | MEDIUM -- requires building new content |
| **Result evolution** | "Come back next week to see how your type evolves" | 5-15% weekly return rate | HIGH -- requires tracking and dynamic results |
| **Comparison feature** | "Compare your result with a friend" sends unique link | 10-20% of sharers send comparison links | LOW-MEDIUM -- comparison page + unique URL logic |
| **Collection/badge system** | "You've unlocked 3 of 8 personality types" | 8-15% try to collect multiple results | MEDIUM -- persistent user state needed |
| **Seasonal/themed updates** | "Holiday edition" or "2026 version" of popular generator | Reactivates 15-30% of past users | MEDIUM -- content refresh + email/notification |

## Dashboard Metrics (What to Check Daily)

| Metric | Where to Find | Action Trigger |
|---|---|---|
| Daily completions | Analytics events | <80% of 7-day average = investigate drop |
| Share rate | Share clicks / completions | <5% = share UX broken or result quality issue |
| Referred visits | UTM-tagged traffic | Declining while shares stable = OG image/share card issue |
| Completion rate | Result views / landing page views | <50% = input friction too high or landing page misaligned |
| Result distribution | Count by result type | Any result >40% = scoring algorithm needs rebalancing |
| Top sharing platform | Group shares by platform | Shift between platforms = update share card optimization priority |
