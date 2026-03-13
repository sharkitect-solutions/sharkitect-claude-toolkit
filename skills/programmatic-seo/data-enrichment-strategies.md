# Data Enrichment for Programmatic SEO

## Data Tier Upgrade Paths

Moving from Tier 5 (public) data to higher defensibility tiers without building an entire product.

| Current Tier | Target Tier | Strategy | Effort | Example |
|---|---|---|---|---|
| 5 (Public) -> 4 (Licensed) | Negotiate exclusive or early-access data deals | Medium | Partner with a data provider for exclusive access to a subset. Even a 30-day exclusivity window gives you a ranking head start. Example: real estate data from MLS feeds that competitors can't easily access |
| 5 (Public) -> 3 (UGC) | Add user-generated content layer on top of public data | High initial, low ongoing | Add reviews, ratings, comments, or submissions to your pages. Each UGC contribution adds unique content that public data alone can't provide. Example: "Best coworking spaces in Austin" + user reviews of each space |
| 5 (Public) -> 2 (Product-derived) | Use your product's data to enrich pages | Medium | If your product tracks usage data, surface anonymized insights. Example: "Average time to complete [task] is 4.2 hours" based on your project management tool's data. Competitors can't replicate this |
| 5 (Public) -> 1 (Proprietary) | Create original research, analysis, or testing | High | Run original experiments, surveys, or analyses. Example: "We tested 47 CRM tools for response time" -- your testing methodology and results are proprietary even if the tools are public |

## API Sources for Location Data Enrichment

For location-based pSEO, enriching city-swapped pages with real local data.

| Data Type | API Source | Free Tier | Gotcha |
|---|---|---|---|
| Demographics | US Census Bureau API | Unlimited (public data) | Data is 1-2 years old. American Community Survey (ACS) is more current than Decennial Census. International: WorldBank API for country-level |
| Cost of living | Numbeo API | Limited free queries | Numbeo data is user-submitted (UGC), not official. Accuracy varies by city size. Cross-validate with BLS data for US cities |
| Business listings | Google Places API | $200/month free credit | $0.032 per Place Details request. 100K pages x 10 businesses each = $32K/month. Use caching aggressively (cache results for 30 days, per Google ToS) |
| Weather/climate | OpenWeatherMap API | 1,000 calls/day free | Historical data requires paid plan. For pSEO, cache climate averages (they don't change month-to-month). One API call per city, cache indefinitely |
| Real estate | Zillow API (ZTRAX) | Research access free | Commercial use requires Zillow partnership. Alternative: Redfin has no public API but publishes monthly market data as downloadable CSV |
| Employment/wages | BLS API | Unlimited (public data) | Data is by metro area (MSA), not city. Many pSEO cities don't map 1:1 to MSAs. Use FIPS codes for accurate mapping |
| Regulations | No single API | N/A | State and local regulations must be manually researched or sourced from legal databases. This is HIGH defensibility precisely because it's hard to automate |

**Caching strategy**: API data for pSEO pages should be cached aggressively. Most location data (demographics, cost of living, climate) changes quarterly at most. Set up a monthly refresh job rather than calling APIs per page view.

## UGC Collection Frameworks

User-generated content is the highest-leverage enrichment for pSEO because it's unique per page and scales with user engagement.

| UGC Type | Collection Method | Moderation Need | Content Value |
|---|---|---|---|
| Reviews/ratings | Structured form (star rating + text review). Require minimum 50 characters | Medium -- filter spam, verify purchases/visits if possible | High. Each review adds 50-200 words of unique, keyword-rich content. 5 reviews = 250-1000 unique words per page |
| Comments/discussions | Comment section with threading. Require login to reduce spam | High -- active moderation needed. Bot spam is aggressive on pSEO pages | Medium-high. Quality varies but creates "living" pages that Google crawls more frequently |
| User submissions | "Add a listing" or "Suggest an edit" forms | Low-medium -- verify data accuracy before publishing | Very high. Each submission adds structured data AND signals active community |
| Q&A | Structured Q&A section (like Stack Overflow format). Allow community answers | Medium -- mark "accepted" answers to signal quality | High. Q&A content naturally matches search queries ("How much does [service] cost in [city]?") |
| Photos | User-uploaded images with captions | Medium -- filter inappropriate content, verify relevance | Medium for SEO (alt text is the searchable part), high for engagement and time-on-page |

**Cold start problem**: New pSEO pages have zero UGC. Bootstrap strategies:
1. **Seed with editorial content** -- write 2-3 "reviews" or data points per page yourself (clearly labeled as editorial, not fake UGC)
2. **Incentivize early contributions** -- gamification (badges, leaderboards) or direct incentives (featured contributor status)
3. **Cross-pollinate** -- if users submit UGC on one page, prompt them to contribute to related pages ("You reviewed Austin -- how about San Antonio?")

## Data Freshness Automation

Stale data is the slow death of pSEO. Automate data freshness or accept that pages will decay.

| Data Type | Freshness Requirement | Automation Approach | Stale Signal |
|---|---|---|---|
| Pricing data | Monthly (minimum) | Scheduled API calls or web scraping pipeline. Store in database with last_updated timestamp | "Starting at $X/month" when the actual price changed 6 months ago. Users notice. Google notices bounce rates |
| Business listings | Quarterly | Re-validate via Google Places API or manual spot-checks. Flag businesses that no longer appear in search results | Listing a closed business. Destroys trust for the entire page. Worse if user calls a dead phone number |
| Statistics/demographics | Annually | Annual data refresh from Census/BLS when new data releases (typically March-September) | "Population: 1.2M (2023)" when 2025 data is available. Minor issue but signals neglect |
| Regulations/compliance | Immediately when laws change | Monitor regulatory feeds or legal news. This cannot be fully automated | Showing outdated legal information is a liability risk, especially for YMYL topics. Manual review required |
| Product/tool information | Monthly | Scheduled checks against product websites or APIs. Flag removed features, changed pricing, discontinued products | "Tool X has feature Y" when feature was removed. Users who rely on your comparison to make purchase decisions will not return |

**Freshness in templates**: Add `last_verified: YYYY-MM-DD` to each data section. Display it on the page. This serves two purposes:
1. Users trust dated information more than undated
2. Internal tracking -- pages where `last_verified` is >90 days old need priority refresh

## Content Enrichment Without APIs

Not all enrichment requires API access. These manual-but-scalable techniques add unique value.

| Technique | Effort per Page | Scalability | Unique Value |
|---|---|---|---|
| Editorial summaries | 15-30 min | Low (manual) | Very high. "Our analysis: [city] is best for [audience] because..." is impossible to automate well |
| Comparison callouts | 5-10 min | Medium (templatizable) | High. "Unlike [nearby city], [city] has [unique characteristic]" -- requires knowing both cities |
| Expert quotes | 30-60 min (sourcing) | Low | Very high. "Local [profession] [Name] says: '...'" -- E-E-A-T signal + unique content |
| Infographics | 1-2 hours | Low-medium (template + data) | High for engagement, medium for SEO (unless alt text is detailed). Earns backlinks |
| FAQ sections | 10-15 min | High (research common questions per page type) | High. "People also ask" matching. Use Google's PAA box for the target keyword to find real questions |
| Historical context | 15-30 min | Low | Medium-high. "In 2019, [city] had only 3 coworking spaces. Today there are 47." -- shows expertise and temporal depth |
