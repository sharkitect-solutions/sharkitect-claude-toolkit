---
name: competitive-ads-extractor
description: "Use when extracting, analyzing, or comparing competitors' ads from ad libraries (Facebook Ad Library, LinkedIn Ad Library, Google Ads Transparency Center). Also use when the user wants to understand competitor messaging, creative patterns, or ad strategy. NEVER use for creating ads (use copywriting or social-content), running ad campaigns, or non-advertising competitive analysis."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Competitive Ads Extractor

Extracts and structures competitor ad data from public ad libraries, then applies a repeatable analysis framework to surface messaging patterns, creative approaches, and positioning gaps.

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Extraction workflow, platform overview, analysis framework, output structure | Always (auto-loaded) |
| platform-data-access-realities.md | Deep dive on what each platform API actually exposes vs what users expect: Facebook Ad Library API specifics, Google Ads Transparency gaps, LinkedIn active-only limitation, TikTok curation bias, platform-specific gotchas | Load when the user asks about specific data availability, encounters missing data, or wants programmatic API access. Also load when choosing which platforms to prioritize. Do NOT load for basic extraction (SKILL.md covers the overview). |
| competitive-intelligence-frameworks.md | Share of voice estimation (volume-based and spend-based), messaging positioning analysis (message maps, positioning quadrants, differentiation scoring), creative testing velocity measurement, report template | Load when analyzing 3+ competitors, calculating share of voice, assessing messaging positioning, or measuring creative testing velocity. Do NOT load for single-competitor basic extraction. |
| spend-estimation-methods.md | Impression-based spend modeling, volume-duration method, Facebook EU spend range interpretation, seasonal adjustment factors (B2B/B2C), multi-platform budget distribution inference, hiring signal budget inference, confidence calibration | Load when the user asks about competitor ad budgets, spend estimation, or wants to compare budgets across competitors. Do NOT load for messaging or creative analysis. |

## Extraction Workflow

1. **Identify targets** -- confirm company name(s), ad library platforms, and whether the scope is active-only or historical ads
2. **Access the library** -- navigate to the platform URL (see Platform-Specific Access below), search by brand name or page ID
3. **Filter and capture** -- apply date range, format (video/image/carousel), and country filters as needed; record ad copy, visuals, CTAs, run dates, and any available impression data
4. **Organize raw data** -- group ads by competitor, then tag each with primary theme, format, and audience signal (offer, pain point, demographic cue)
5. **Run analysis** -- apply the Analysis Framework below; identify patterns across the full set before drawing conclusions from individual ads

## Platform-Specific Access

| Platform | URL / Method | What's Available | Key Limitations |
|---|---|---|---|
| Facebook Ad Library | facebook.com/ads/library | Active + inactive ads, run dates, spend ranges (EU only), impressions (EU only), ad creative | No engagement metrics; US hides spend data |
| LinkedIn Ad Library | linkedin.com/ad-library | Active ads only, targeting category (job title, industry), ad format | Historical ads not retained; no spend data |
| Google Ads Transparency | adstransparency.google.com | Search, display, YouTube ads; verified advertiser status; run dates | Creative detail limited for display; no keyword data |
| TikTok Creative Center | ads.tiktok.com/business/creativecenter | Top-performing ads by industry, CTR/CVR benchmarks (aggregated), trending formats | Only shows curated "top" ads, not full brand libraries |

**Legal note:** All four platforms publish this data intentionally for transparency. Manually reading and recording ad content is legal in all jurisdictions. Automated scraping via bots may violate platform ToS and in some regions data protection law -- if the user wants to scrape programmatically, flag this risk before proceeding.

## Analysis Framework

| Dimension | What to Look For | Why It Matters |
|---|---|---|
| Pain point framing | Which problem is named in the hook? | Reveals which segment the ad targets and what fear/frustration is most activating |
| Value proposition type | Feature vs. outcome vs. social proof vs. price | Shows maturity of market positioning and where competitors anchor |
| CTA pattern | Verb choice, commitment level (free trial vs. buy now) | Signals funnel stage and conversion strategy |
| Creative format | Static, video length, carousel sequence logic | Indicates platform fit and audience attention assumption |
| Run duration | First seen vs. last seen dates | Long-running ads are statistically performing; recently paused may have failed |
| Audience signals | Terminology, visuals, offers that index to a segment | Reveals who they are prioritizing and which segments are underserved |

## Multi-Competitor Comparison Matrix

When analyzing 3+ competitors, structure findings as a matrix before writing narrative conclusions:

- **Rows**: Each competitor
- **Columns**: Pain point, primary value prop, dominant format, CTA type, estimated volume (few/moderate/many), notable gap or differentiator
- **Summary row**: What is consistent across all (table stakes messaging) vs. what only one or two say (differentiation opportunity)

Flag the "white space" -- pain points or audiences that no competitor is addressing in ads, which represent positioning opportunities for the user.

## Output Structure

Deliver analysis in this order:

1. **Snapshot** -- competitor name, platform, total ads reviewed, date range, formats observed
2. **Top 3 messaging themes** -- each with representative copy excerpt and frequency count
3. **Creative patterns** -- dominant formats, visual approaches, CTA language
4. **Audience segmentation signals** -- which segments each competitor appears to be targeting based on ad variations
5. **Comparison matrix** -- if multi-competitor scope
6. **White space / gaps** -- what is not being said that could be owned
7. **Recommendations** -- 3-5 specific, testable hypotheses for the user's own ads, grounded in what was observed

Do NOT fabricate metrics, impression counts, or engagement rates unless the platform surfaced them explicitly.

## Rationalization Table

| Decision | Rationale |
|---|---|
| Delete 170-line mock Notion output | Fake data simulating tool output wastes context, teaches nothing generalizable, and misleads about what ad libraries actually expose |
| Platform table with Limitations column | Each platform has distinct constraints (EU-only spend data, active-only history) that determine what analysis is possible -- omitting this causes user to expect data that does not exist |
| Legal note in Platform section | Automated scraping risk is commonly misunderstood; flagging it proactively prevents the user from requesting something that could violate ToS before the work begins |
| Run duration as analysis dimension | Ad longevity is the most accessible performance proxy in ad libraries that do not expose engagement metrics -- it is the key insight most users miss |
| White space as mandatory output section | Competitor analysis value is highest when it surfaces gaps, not just what competitors do; many users only get a description without the opportunity identification |
| Removed "What You Can Learn" and all tip sections | Claude already knows messaging analysis, copy formulas, and campaign strategy -- restating them as bullet lists adds lines without adding capability |

## Red Flags

- User asks to "copy" or "replicate" a competitor ad -- reframe immediately as extracting the strategic pattern, not duplicating creative or copy
- User expects engagement rate, CTR, or ROAS data -- ad libraries do not expose these; only Facebook EU and TikTok Creative Center surface any performance proxies
- User names a company with a very common name (e.g., "Apple" or "Visa") -- search results will include many unrelated pages; confirm the exact page URL or page ID before extracting
- User wants historical ads beyond 7 years on Facebook or any inactive ads on LinkedIn -- confirm platform retention limits before scoping the project
- User is analyzing a company in a restricted category (finance, housing, employment, politics) -- Facebook applies additional filtering and reduced data for these categories; output will be sparser than expected
- User wants to automate extraction via a script -- flag ToS risk and data protection law implications before writing any scraping code

## NEVER

- Fabricate ad copy, creative descriptions, impression counts, or engagement metrics that were not actually present in the ad library
- Present the mock Notion example (or any fabricated example) as representative output -- illustrative examples must be clearly labeled as hypothetical
- Use this skill to write new ad copy or design new creatives -- that is copywriting or social-content work
- Recommend specific scraping tools or bots without first flagging the platform ToS and legal exposure risk
- Draw conclusions about ad performance from run duration alone without noting that ads can run long due to budget scheduling, not just performance
