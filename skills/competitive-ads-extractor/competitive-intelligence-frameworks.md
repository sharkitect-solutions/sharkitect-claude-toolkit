# Competitive Intelligence Frameworks

Load when the user needs structured frameworks for analyzing competitor ad strategy beyond basic extraction, when comparing messaging positioning across 3+ competitors, when calculating share of voice, or when assessing creative testing velocity. Do NOT load for basic ad extraction workflow (use SKILL.md).

## Share of Voice Estimation

Ad libraries don't expose impression or spend data (except Facebook EU). Estimate relative ad volume using proxy signals.

### Volume-Based SOV (Free Method)

| Step | Method |
|---|---|
| 1. Count active ads per competitor | Search each competitor in the ad library. Count total active ads. Normalize by company size (a 10,000-person company naturally runs more ads than a 50-person startup). |
| 2. Segment by platform | Count per platform: Facebook, LinkedIn, Google, TikTok. Platform mix reveals channel strategy. |
| 3. Segment by format | Count per format: image, video, carousel, text. Format mix reveals creative investment level. |
| 4. Calculate relative share | Company A: 45 ads / Total across all competitors: 180 ads = 25% volume SOV. |
| 5. Weight by longevity | Ads running 30+ days carry more weight than ads running 3 days (longer run = likely performing). Weight: 30+ days = 3x, 7-30 days = 2x, <7 days = 1x. |

**SOV limitation**: Volume SOV is a proxy, not a measurement. A company with 10 high-budget ads may outspend a company with 100 low-budget ads. Without spend data, volume is the best available signal.

### Spend-Based SOV (Facebook EU Only)

When analyzing EU-targeted Facebook ads, use exposed spend ranges:

| Step | Method |
|---|---|
| 1. Export spend ranges | For each competitor's ads, record the spend range (e.g., "$1K-$5K") |
| 2. Use range midpoint | Convert "$1K-$5K" to $3K midpoint. This introduces error but is the best available precision. |
| 3. Sum midpoints per competitor | Total estimated spend per competitor |
| 4. Calculate SOV | Company A total / All competitors total = Spend-based SOV % |

**Caveat for user**: Spend ranges are LIFETIME per ad, not daily. An ad showing "$5K-$10K" that ran for 100 days had a very different daily spend than one that ran for 5 days. Always normalize by run duration.

## Messaging Positioning Analysis

### Message Map Construction

For each competitor, build a message map from their ad portfolio:

| Layer | What to Extract | How to Identify |
|---|---|---|
| **Primary claim** | The single biggest promise repeated across most ads | The headline or first sentence that appears in >50% of their ads |
| **Supporting proof** | Evidence types used (numbers, logos, testimonials, awards) | What follows the primary claim -- data points, social proof, authority signals |
| **Objection handling** | Preemptive answers to buyer hesitation | "No credit card required," "Cancel anytime," "Works with your existing tools" -- friction reducers |
| **Emotional trigger** | The feeling the ad tries to create | Fear (risk of inaction), aspiration (vision of success), frustration (current pain), belonging (join 10K+ companies) |
| **Audience signal** | Who this specific ad targets | Job titles in copy, industry references, company size mentions, use case specificity |

### Positioning Quadrant

Plot competitors on two axes to identify positioning gaps:

```
                    Outcome-focused messaging
                           |
    Premium positioning  --+--  Value positioning
                           |
                    Feature-focused messaging
```

| Quadrant | Characteristics | Typical Brands |
|---|---|---|
| Premium + Outcome | "Transform your business" + high price signals | Enterprise SaaS, consulting platforms |
| Premium + Feature | "Most powerful platform" + technical superiority | Developer tools, infrastructure products |
| Value + Outcome | "Grow faster for less" + ROI focused | SMB tools, PLG products |
| Value + Feature | "Everything you need" + feature lists | Commodity tools, comparison-page brands |

**The crowded quadrant trap**: If 4 of 5 competitors cluster in Value + Feature, that quadrant is table stakes messaging. Moving to an adjacent quadrant (especially Premium + Outcome if no one occupies it) creates differentiation. The white space is the opportunity.

### Messaging Differentiation Score

Rate each competitor's messaging uniqueness:

| Criterion | Score 1 (Generic) | Score 3 (Moderate) | Score 5 (Distinctive) |
|---|---|---|---|
| Primary claim | Indistinguishable from competitors ("All-in-one platform") | Category-specific but shared with 1-2 others ("AI-powered analytics") | Unique claim no competitor makes ("The only platform that X") |
| Proof type | Generic stats ("trusted by thousands") | Specific but common (named logos, dollar amounts) | Unique proof (proprietary data, audited results, category-defining benchmark) |
| Audience specificity | "For businesses" (everyone) | Industry or role-specific ("for marketing teams") | Hyper-specific ("for DTC brands doing $1-10M/year switching from Klaviyo") |
| Tone | Corporate neutral | Category-appropriate but undistinctive | Recognizable brand voice (could identify the brand with the logo hidden) |

**Score interpretation**: 16-20 = highly differentiated (rare). 10-15 = moderately differentiated. 4-9 = undifferentiated commodity messaging -- competing on distribution, not positioning.

## Creative Testing Velocity Analysis

How aggressively a competitor tests new creative indicates their growth maturity and budget confidence.

### Velocity Measurement

| Metric | How to Measure | What It Signals |
|---|---|---|
| New ads per month | Count ads with "First seen" dates in the last 30 days | Higher = active testing program. Lower = set-and-forget approach. |
| Creative lifespan | Average days between "First seen" and "Last seen" (or current date if active) | Short lifespan (7-14 days) = rapid testing with frequent kills. Long lifespan (60+ days) = either performing well or not being managed. |
| Format diversity | Count of unique formats (image, video, carousel) in last 90 days | Testing across formats suggests dedicated creative team or agency. |
| Message variation count | Number of distinct primary claims across active ads | 1-2 claims = confident in messaging. 5+ claims = still searching for product-market fit or testing aggressively. |
| Seasonal patterns | Ad volume spikes around specific dates or events | Reveals planning cadence (quarterly launches, event-driven, always-on). |

### Velocity Benchmarks by Stage

| Company Stage | Expected New Ads/Month | Typical Lifespan | Interpretation |
|---|---|---|---|
| Early startup (seed/A) | 2-5 | 30-90 days | Testing sparingly, budget-constrained. Each ad runs longer. |
| Growth stage (B/C) | 10-30 | 14-30 days | Active testing program. Dedicated paid team or agency. |
| Mature/enterprise | 30-100+ | 7-21 days | High-velocity testing with rapid iteration. Large creative team. |
| "Dark horse" (few but long-running) | 3-5 | 90+ days | Found what works and is scaling it. Most efficient -- or most neglected. |

### Creative Fatigue Detection

| Signal | Interpretation |
|---|---|
| Same ad running 90+ days with no new variants | Either performing exceptionally (rare) or abandoned (common). Check if ANY new ads have appeared -- if none, the ad program may be inactive. |
| Burst of 10+ new ads followed by silence | Campaign launch followed by budget exhaustion or team pivot. Check if any from the burst survived (survivors = winners). |
| Gradual increase in video ads replacing static | Platform algorithms favor video engagement. Competitor is adapting to platform signals. |
| Multiple variations of the same headline with different images | A/B testing creative (image) while holding copy constant. Indicates data-driven creative process. |
| Identical ad text across Facebook, LinkedIn, Google | No platform-specific adaptation. Likely a small team copy-pasting without channel strategy. Vulnerability: platform-optimized competitors will outperform. |

## Competitive Intelligence Report Template

Structure the final deliverable for maximum actionability:

| Section | Content | Length |
|---|---|---|
| Executive summary | 3-5 bullet findings. Lead with the biggest opportunity. | 5-7 sentences max |
| Competitor profiles | Per-competitor: message map, volume, format mix, velocity, positioning | 1 page per competitor |
| Comparison matrix | All competitors side-by-side on key dimensions | 1 table |
| Share of voice | Volume-based (all platforms) + spend-based (EU Facebook if applicable) | 1 table + 1 chart description |
| Positioning quadrant | Visual positioning map with competitor placement | 1 diagram description |
| White space analysis | Gaps in messaging, format, audience, or platform coverage | 3-5 specific opportunities |
| Recommendations | Testable hypotheses: "Based on [observation], test [specific ad] targeting [audience] because [reasoning]" | 3-5 numbered items |
