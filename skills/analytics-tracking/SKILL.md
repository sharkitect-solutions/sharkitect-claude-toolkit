---
name: analytics-tracking
description: "Use when implementing analytics tracking, building measurement plans, configuring GA4 or GTM, designing event taxonomies, setting up conversion tracking, or auditing existing tracking implementations. Also use when choosing between analytics platforms, debugging tracking issues, designing UTM strategies, or implementing consent-compliant measurement. NEVER use for A/B test design and statistical analysis (ab-test-setup), CRO experiment recommendations (page-cro, form-cro), SEO performance analysis (seo-optimizer), or marketing attribution modeling (marketing-demand-acquisition)."
version: "2.0"
optimized: true
optimized_date: "2026-03-12"
---

# Analytics Tracking

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Platform selection, measurement planning, event naming, GA4 gotchas, GTM architecture, UTM strategy, consent decisions, anti-patterns | Always (auto-loaded) |
| ga4-bigquery-reference.md | BigQuery export configuration, event data schema (nested/repeated fields), essential query patterns (session reconstruction, attribution), cost optimization, common BigQuery + GA4 mistakes | When configuring BigQuery export, writing queries against GA4 data, debugging BigQuery results that don't match GA4 UI, or optimizing query costs |
| consent-mode-implementation.md | Consent Mode v2 signal types, CMP integration patterns (OneTrust, Cookiebot, Didomi), implementation sequence, behavioral modeling accuracy thresholds, testing consent states, regional requirements | When implementing consent management, debugging consent-related tracking gaps, choosing a CMP, or evaluating modeling accuracy for low-consent-rate sites |
| gtm-debugging-advanced.md | Debugging decision tree (symptom -> cause -> fix), data layer debugging, GTM server-side architecture and cost analysis, server-side gotchas, browser-specific tracking issues (Safari ITP, Firefox ETP, Brave) | When debugging complex tracking issues, evaluating server-side GTM, or troubleshooting browser-specific tracking failures |

Do NOT load companion files for basic GA4 event setup, simple UTM tagging, or standard GTM tag configuration -- SKILL.md covers these decisions fully.

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| Measurement plan design and event taxonomy | YES | -- |
| GA4 configuration and custom dimensions | YES | -- |
| GTM container architecture and tag management | YES | -- |
| Event naming conventions and data layer design | YES | -- |
| UTM strategy and campaign tracking | YES | -- |
| Conversion tracking setup | YES | -- |
| Consent mode and privacy-compliant tracking | YES | -- |
| Tracking debugging and validation | YES | -- |
| A/B test experiment design | NO | ab-test-setup |
| CRO recommendations from analytics data | NO | page-cro, form-cro |
| SEO ranking and organic traffic analysis | NO | seo-optimizer |
| Marketing attribution and channel ROI | NO | marketing-demand-acquisition |
| Data warehouse and ETL pipeline design | NO | data engineering |

## Analytics Platform Selection

| Signal | Best Fit | Why | Gotcha |
|---|---|---|---|
| Need free, integrated with Google Ads | GA4 | Native Google Ads integration, free up to 10M events/month | GA4 samples data above ~500K rows in Explore reports. BigQuery export is the only way to get unsampled data -- requires GCP project and ~$5-50/month depending on volume |
| Need user-level behavioral analytics (SaaS) | Mixpanel or Amplitude | Event-based models with user journey analysis, cohort retention, funnels | Both charge by tracked users (MTUs). Mixpanel free tier: 20M events. Amplitude: 10M events. At scale ($1K+/month), evaluate PostHog (self-hosted option) |
| Need session recordings + analytics combined | Heap, PostHog, or FullStory | Auto-capture reduces implementation work. Session replay for qualitative analysis | Auto-capture creates massive event volume. Heap retroactive analysis only works for auto-captured events -- custom events still need implementation. PostHog self-hosted requires DevOps capacity |
| Need customer data platform (CDP) + analytics | Segment + analytics tool | Segment routes events to multiple destinations from one implementation | Segment pricing jumps dramatically at scale (free: 1K MTUs, Team: $120/month for 10K). Consider RudderStack (open-source alternative) or Jitsu for cost-sensitive projects |
| Enterprise with strict data residency requirements | Matomo (self-hosted) or Piwik PRO | Full data ownership, GDPR-compliant by default, no cookie consent needed for basic analytics (EU DPA rulings) | Self-hosted Matomo requires server maintenance. Cloud Matomo starts at ~$19/month. Feature gap vs GA4/Mixpanel in advanced analysis |

**Default recommendation**: GA4 + GTM for most projects. Add Mixpanel/Amplitude only when you need user-level behavioral analysis that GA4 Explore reports can't provide.

## Measurement Plan Framework

Design tracking decisions-first, not tools-first. Every event must answer a question that leads to an action.

| Step | Question | Output | Common Failure |
|---|---|---|---|
| 1. Business questions | What decisions will this data inform? | 5-10 specific questions ("Which landing pages convert best?", "Where do users drop off in onboarding?") | Tracking "everything" with no specific questions -- creates data graveyards where nobody looks at 90% of events |
| 2. Key metrics | What numbers answer each question? | Metrics mapped to questions (conversion rate by landing page, onboarding completion rate by step) | Vanity metrics (pageviews, total signups) that don't inform decisions |
| 3. Required events | What user actions produce those metrics? | Event list with properties, each tied to a metric | Tracking events you'll never query. Every event should map to at least one metric |
| 4. Implementation plan | How will each event fire? | Technical spec: trigger mechanism, data layer structure, property sources | Implementing before documenting -- leads to inconsistent naming and missing properties discovered months later |
| 5. Validation protocol | How will you verify correctness? | Test cases per event: expected trigger, expected properties, edge cases | "It fires" is not validation. Verify properties have correct values, events fire exactly once per action, and edge cases (back button, page refresh) don't create duplicates |

## Event Naming Architecture

| Decision | Recommendation | Why | Exception |
|---|---|---|---|
| Naming format | `object_action` (e.g., `signup_completed`, `cart_item_added`) | Reads naturally, groups by object in alphabetical event lists, matches GA4 recommended events | If team already uses `action_object` consistently -- consistency beats convention. Cost of migration > benefit of "correct" format |
| Case convention | `snake_case` lowercase | GA4 treats `Signup` and `signup` as different events. Mixed case = duplicate events that split your data | Never. Even if a platform's UI shows Title Case, the underlying event name should be snake_case |
| Property naming | Match event convention (`snake_case`) | Consistency across events and properties. GA4 custom dimensions reference property names exactly | GA4 has 50 event-scoped and 25 user-scoped custom dimension slots. Plan property names carefully -- you can't rename without losing historical data |
| Namespace depth | 2-3 segments max (`category_object_action`) | Deeper namespaces (`checkout_payment_credit_card_submitted`) become unwieldy in queries and reports | Long namespaces acceptable for high-cardinality event types where filtering by prefix is the primary query pattern |

**GA4 naming constraints**: Event names max 40 chars, property names max 40 chars, property values max 100 chars. These are HARD limits that silently truncate -- no error, just lost data.

## GA4-Specific Gotchas

| Gotcha | Impact | Fix |
|---|---|---|
| Data sampling in Explore reports | Above ~500K rows, GA4 applies sampling that can skew metrics by 10-30%. Standard reports are unsampled but limited in dimensions | Export to BigQuery for unsampled analysis. Free BigQuery export available in all GA4 properties (even free tier). First 1TB/month of queries free |
| 14-month data retention default | Event-level data in Explore reports expires after 14 months. Aggregated data in standard reports persists. Users don't realize until they need year-over-year Explore analysis | Change to maximum retention (14 months is already max for free GA4). For longer retention, BigQuery export stores data indefinitely at your own storage cost |
| Conversion counting change (2024+) | GA4 now defaults to "once per session" for most conversions. Previously "once per event." Switching changes historical metrics | Decide counting method at setup. "Once per session" for lead gen (form_submitted). "Every event" for e-commerce (purchase). Document the choice -- it affects conversion rate calculations retroactively |
| Consent Mode v2 required (EU) | Google requires Consent Mode v2 for EU traffic as of March 2024. Without it, remarketing audiences and conversion data are incomplete | Implement `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization` consent signals. Google models unconsentented data but accuracy degrades below 70% consent rate |
| Thresholding hides small-number data | GA4 applies thresholding when Google Signals is enabled -- removing rows where user count is too low to prevent re-identification. Appears as missing data in reports | Disable Google Signals if you don't need cross-device tracking. Or use BigQuery export where thresholding doesn't apply |
| Custom dimension limits | 50 event-scoped, 25 user-scoped, 10 item-scoped custom dimensions. Once created, dimensions can be archived but the slot isn't freed for 48 hours | Plan custom dimensions carefully. Don't create dimensions for data you'll only query once. Use event parameters (which are unlimited) and query via BigQuery instead |
| Attribution model default changed | GA4 switched default from last-click to data-driven attribution in 2023. Historical data retroactively recalculated | Choose attribution model explicitly. Data-driven requires sufficient conversion volume (typically 300+/month). Below that threshold, it falls back to last-click silently |

## GTM Container Architecture

| Pattern | When | Structure | Gotcha |
|---|---|---|---|
| Single container, tag-organized | Small-medium sites, one team manages | Folders by tag type (GA4, Ads, Meta). One GA4 config tag, event tags grouped | Works until 100+ tags. Then performance degrades -- every page loads all tag configurations even if most don't fire |
| Single container, trigger-organized | Sites with complex trigger logic | Folders by page section or funnel stage. Tags grouped by where they fire | Better for debugging (find all tags that fire on checkout) but harder to audit all tags for one platform |
| Multi-container (primary + secondary) | Large sites, multiple teams | Primary: core analytics (GA4, consent). Secondary: marketing tags (ads pixels, chat widgets) | Container load order matters. Primary must load first for consent management. Secondary containers add 50-100ms latency each |
| Server-side GTM | Need first-party tracking, ad blocker bypass, or data processing before sending | Client container sends to server container (Cloud Run/App Engine). Server container routes to destinations | Requires GCP infrastructure ($50-500/month). Debugging is harder (two containers to inspect). But: first-party domain bypasses most ad blockers, and you control what data leaves your server |

**Container hygiene**: GTM containers accumulate dead tags over time. Audit quarterly: check for tags with zero fires in 30 days, triggers that reference deleted variables, and workspace conflicts from team members who left.

## UTM Architecture

| Rule | Why | Violation Impact |
|---|---|---|
| Lowercase everything (`google` not `Google`) | GA4 is case-sensitive. `Google`, `google`, and `GOOGLE` create 3 separate source entries | Fragmented source/medium reports. Channel groupings break because default rules expect lowercase |
| Standardize medium values to GA4 defaults | GA4 Default Channel Grouping uses specific medium values: `cpc`, `email`, `social`, `referral`, `organic`, `display` | Custom medium values (`paid-social`, `newsletter`, `sponsored`) fall into "(Other)" channel grouping. You must create custom channel groups to fix this |
| Never put PII in UTM parameters | UTMs appear in GA4 as event parameters. PII in UTMs = PII in analytics = GDPR/CCPA violation | Compliance risk. Also: UTMs are visible in browser address bar and server logs |
| Use utm_content for variant testing | Differentiate ad creative, CTA placement, or email version | Without it, you can't compare performance of different creatives within the same campaign |
| Document all UTMs in a shared registry | Prevent duplicate/conflicting campaigns. Enable consistent reporting | Without registry: 5 team members create 5 different utm_source values for the same platform. Data is fragmented permanently |

## Data Layer Anti-Patterns

| Name | Pattern | Why It Fails | Fix |
|---|---|---|---|
| The Event Hoarder | Tracking 200+ events "because we might need the data" | 90% of events are never queried. Noise drowns signal. Implementation and maintenance cost scales linearly. GA4 has 500 distinct event name limit | Start with 15-25 events tied to specific business questions. Add events only when someone asks a question the current data can't answer |
| The Vanity Dashboard | Tracking pageviews and total users as primary metrics | Pageviews don't inform decisions. "10K visits" tells you nothing about conversion, engagement, or revenue. Stakeholders feel informed but can't act | Replace with behavioral metrics: conversion rate by source, feature adoption rate, time-to-activation, revenue per user segment |
| The PII Leaker | Passing email, name, or phone number as event properties | Violates GDPR/CCPA. GA4 Terms of Service prohibit PII. Google can terminate your property. Data is irrecoverable once sent | Hash user identifiers before sending. Use user_id (opaque identifier) instead of email. Audit data layer pushes for accidental PII (form field values, URL parameters with email) |
| The Duplicate Trigger | Same event fires 2-3 times per action due to multiple GTM triggers or re-renders | Inflated event counts. Conversion numbers are wrong. Funnel analysis shows impossible completion rates (>100%) | Use event deduplication: transaction_id for purchases, form_id + timestamp for submissions. In GTM, use "once per page" trigger option or custom JavaScript variable to prevent re-fires |
| The Consent Ignorer | Firing all tags before consent, then retroactively applying consent | GDPR/ePrivacy violation (max fine: 4% global revenue). Even with consent mode, tags that fire pre-consent send a network request | GTM consent mode must be the FIRST thing configured. Default state: denied. Tags fire only after explicit consent signal. Use consent initialization triggers |
| The Silo Architect | GA4 for marketing, Mixpanel for product, Amplitude for data science -- no shared event taxonomy | Same user action has 3 different event names. Cross-team analysis impossible. "Conversion rate" means different things to different teams | Single event taxonomy documented in a tracking plan. Use Segment or GTM server-side to route one event definition to multiple destinations |

## Debugging Procedure

| Step | Tool | What to Check | Common Finding |
|---|---|---|---|
| 1. Verify tag fires | GTM Preview mode | Tag fires on correct trigger. Variables resolve to expected values | Trigger condition too broad (fires on every page) or too narrow (CSS selector changed after deploy) |
| 2. Verify data layer | Browser console: `dataLayer` | Event object contains expected properties with correct values and types | Property value is `undefined` because data layer push happens before DOM element exists. Fix: use DOM Ready trigger instead of Page View |
| 3. Verify GA4 receives | GA4 DebugView (Realtime > debug_mode=true) | Event appears with correct name and parameters | Event name exceeds 40 chars (silently truncated). Or: parameter name has spaces (replaced with underscores, breaking custom dimension mapping) |
| 4. Verify reports populate | GA4 Explore (24-48 hour delay) | Custom dimensions show expected values. No unexpected (not set) values | Custom dimension not created in GA4 Admin, or parameter name in tag doesn't match dimension's "event parameter" field exactly |
| 5. Verify cross-device | GA4 User Explorer | Same user_id appears across devices/sessions | user_id not set on all platforms. Or: user_id set before login (anonymous sessions create separate user records that never merge) |

## Consent Implementation Decision

| Scenario | Implementation | Key Requirement |
|---|---|---|
| EU/EEA visitors | Consent Mode v2 with CMP (OneTrust, Cookiebot, or similar) | Must collect explicit opt-in BEFORE firing analytics/ad tags. Default state: `denied` for all consent types. Google requires `ad_user_data` and `ad_personalization` signals |
| US visitors (no state law applies) | Optional but recommended: basic cookie banner | California (CCPA), Colorado, Connecticut, Virginia, Utah all have different requirements. Safest: implement opt-out for all US visitors |
| B2B SaaS (no cookies, server-side only) | May not need consent for basic analytics | If using first-party server-side tracking without cookies, many EU DPAs have ruled consent is not required. But: any Google or Meta tag requires consent regardless |
| Global visitors, mixed regulation | Geo-targeted consent: full CMP for EU, opt-out for US, notice-only for others | CMP must detect user location (via IP) and apply correct consent flow. Test with VPN from different regions |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "We'll figure out what to track after launch" | Post-launch tracking retrofitting means missing data for the most critical period (launch). Event taxonomy designed under pressure is inconsistent and hard to fix without losing historical continuity |
| "Just track everything and filter later" | GA4 has 500 event name limit and 50 custom dimension slots. "Everything" hits limits fast. Plus: more events = more bugs, more maintenance, and more noise in every report |
| "We don't need a tracking plan, the developer knows what to track" | Developers implement what they understand -- page loads and button clicks. Business context (which clicks matter, what conversion means, what segments are important) requires product/marketing input. The result is technically correct tracking that doesn't answer business questions |
| "GA4 enhanced measurement handles everything" | Enhanced measurement captures 7 basic events (page_view, scroll, outbound_click, site_search, video_engagement, file_download, form_interaction). These cover <20% of typical measurement needs. Custom events are where actionable insights live |
| "We'll add UTMs when we scale" | Retroactive UTM implementation means all historical campaign data is unattributed. Source/medium reports show "(direct) / (none)" for everything before UTMs were added. That data is permanently lost |

## Red Flags

- No tracking plan document -- events are added ad-hoc by whoever needs data, resulting in inconsistent naming and duplicate events
- Event names with spaces or mixed case -- GA4 treats these as separate events, fragmenting data permanently
- GA4 property with Google Signals enabled but no cross-device use case -- thresholding hides data for no benefit
- UTM parameters with PII (email addresses, names) -- compliance violation that persists in analytics data indefinitely
- GTM container with 100+ tags and no folder organization -- unmaintainable, impossible to audit which tags fire where
- No consent management for EU visitors -- legal risk and incomplete data (Google rejects conversion data without Consent Mode v2)
- Custom dimensions created for one-time analysis -- wastes scarce slots (50 event-scoped maximum) that can't be recovered for 48 hours after archiving
- user_id set to email address instead of opaque identifier -- PII in analytics that violates GA4 Terms of Service

## NEVER

- Fire analytics tags before consent signal in EU/EEA -- this is a GDPR violation regardless of whether you later apply consent retroactively
- Use mixed case or spaces in event names -- GA4 treats them as separate events and there is no way to merge them after the fact
- Pass PII (email, name, phone, IP) as event properties to GA4 -- violates Terms of Service and GDPR. Google can terminate the property
- Create custom dimensions without checking remaining slot count -- GA4's 50/25/10 limits are hard caps with no upgrade path
- Implement tracking without a documented measurement plan -- ad-hoc tracking creates data debt that compounds with every new event and becomes impossible to untangle
