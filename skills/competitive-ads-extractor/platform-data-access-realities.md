# Platform Data Access Realities

Load when the user asks about specific ad library capabilities, wants to know exactly what data is available from a platform, encounters missing or unexpected data in ad library results, or needs to choose which platforms to prioritize for a competitive analysis. Do NOT load for general extraction workflow (use SKILL.md).

## Facebook Ad Library Deep Dive

### What the API Actually Exposes

| Data Point | Available? | Precision | Access Method |
|---|---|---|---|
| Ad creative (text + image/video) | Yes | Full copy text, thumbnail or playable media | Search by page name or page ID |
| Run dates (started, ended) | Yes | Day-level precision | Always shown per ad |
| Active/inactive status | Yes | Binary (active/inactive) | Filterable |
| Spend range | EU only | Bucketed ranges (e.g., "$500-$999") | DSA regulation requirement; US shows nothing |
| Impression range | EU only | Bucketed ranges (e.g., "10K-50K") | Same DSA regulation; US shows nothing |
| Demographic breakdown | EU only | Age, gender, location percentages | Only for ads about social issues, elections, politics in EU |
| Targeting criteria used | No | -- | Never exposed; this is the most commonly misunderstood limitation |
| Engagement (likes, shares, comments) | No | -- | Not in Ad Library; only visible on the live post if boosted |
| CTR, conversion rate, ROAS | No | -- | Never exposed on any platform's transparency tool |
| A/B test variants | Partial | Multiple ad creatives under one campaign visible, but not labeled as test variants | Inferred from similar copy with minor variations running simultaneously |
| Landing page URL | Sometimes | Visible in CTA link but may be a redirect/tracker URL | Click the CTA to resolve the final destination |

### Facebook Ad Library API (Programmatic Access)

| Aspect | Reality |
|---|---|
| API endpoint | `graph.facebook.com/ads_archive` -- requires approved Facebook app with `ads_archive` permission |
| Approval process | Must submit app review explaining use case. Approval takes 2-4 weeks. Denial common for vague purposes. |
| Rate limits | 200 requests per hour per app. Pagination required for brands with 1000+ ads. |
| Search limitations | Search by page ID is reliable. Search by keyword matches ad copy text only (not targeting, not landing page). |
| Historical depth | Ads from 2018+ for political/social; all ads retained since 2019 for all advertisers (but inactive ads older than 7 years may be pruned). |
| Bulk export | Not available. Must paginate through results. Third-party tools (AdLibrary.io, PowerAdSpy) aggregate but add cost and may violate Meta ToS. |
| Format for analysis | JSON responses. Each ad object includes: page_id, page_name, ad_creative_body, ad_creative_link_caption, ad_creative_link_title, ad_delivery_start_time, ad_delivery_stop_time, currency, spend (EU), impressions (EU). |

### Facebook-Specific Gotchas

| Gotcha | Impact | Workaround |
|---|---|---|
| Dynamic Creative Optimization (DCO) | A single ad ID may represent multiple headline/image/CTA combinations that Meta rotates. Ad Library shows ONE version, not all variants. | Look for multiple ads from the same page with identical start dates and similar but not identical copy -- these are likely DCO variants. |
| Page name changes | Companies rebrand. Searching "Acme Inc" won't find ads run when the page was called "Acme Corp." | Search by page ID (numeric, never changes) instead of page name. Find page ID via the page's About section or URL. |
| Multi-page brands | Large companies run ads from multiple pages (brand page, product pages, regional pages). | Search for the parent company name, then identify all related page IDs. Meta doesn't provide a "parent company" linkage. |
| Restricted categories | Housing, employment, credit, social issues, elections -- these have limited demographic data even in EU. | Reduced data is by design (anti-discrimination). Inform the user that analysis will be less detailed for these categories. |
| Spending spikes vs steady spend | EU spend ranges are lifetime per ad, not daily. An ad showing "$5K-$10K" could be $50/day for 100 days or $5K in one day. | Cross-reference with run dates to estimate daily spend: spend_range_midpoint / days_active = estimated daily spend. |

## Google Ads Transparency Center Deep Dive

### What's Actually Available

| Data Point | Available? | Precision |
|---|---|---|
| Ad creative (text ads) | Yes | Full headline, description, display URL |
| Ad creative (display/video) | Partial | Thumbnail visible, not always full-resolution. Video ads show a preview frame. |
| Advertiser identity | Yes | Verified advertiser name and country |
| Run dates | Yes | "First shown" and "Last shown" at day level |
| Geographic targeting | Yes | Countries where the ad was shown (not cities/regions) |
| Ad format | Yes | Text, image, video categorization |
| Spend | No | Not exposed at all |
| Keywords bid on | No | This is the biggest gap -- you cannot see what search terms triggered the ad |
| Audience targeting | No | Demographics, interests, remarketing lists are never shown |
| Quality Score | No | Internal Google metric, never externalized |
| Landing page | Sometimes | Display URL is shown; actual landing page may differ due to redirects |

### Google-Specific Gotchas

| Gotcha | Impact | Workaround |
|---|---|---|
| Responsive Search Ads (RSA) rotation | Google rotates up to 15 headlines and 4 descriptions. Transparency Center shows ONE combination, not all permutations. | Look for multiple text ads from same advertiser with overlapping dates but different headline/description combos. |
| Performance Max opacity | PMax campaigns serve across Search, Display, YouTube, Gmail, Maps. Transparency Center may show the same creative in multiple format categories. | Deduplicate by creative text/image before counting unique ads. |
| YouTube ads fragmented | Pre-roll, mid-roll, bumper, and discovery ads all appear separately. A single video campaign may generate 4+ Transparency Center entries. | Group by video content, not by entry. |
| No historical archive depth guarantee | Google states ads are retained "for a period" but doesn't commit to a specific retention period. Older ads may disappear. | Export data promptly. Don't assume ads will still be visible next month. |

## LinkedIn Ad Library Deep Dive

### What's Actually Available

| Data Point | Available? | Precision |
|---|---|---|
| Ad creative (text + image/video) | Yes | Full copy, media, CTA |
| Active status | Yes | Only ACTIVE ads are shown (inactive ads are removed) |
| Targeting category | Partial | Shows "Job function: Marketing" or "Industry: Technology" but not the complete targeting spec |
| Company page | Yes | Linked to company page |
| Run dates | No | No start or end dates shown |
| Spend | No | Not exposed |
| Impressions | No | Not exposed |
| Ad format | Yes | Single image, video, carousel, message ad, conversation ad |

### LinkedIn-Specific Gotchas

| Gotcha | Impact | Workaround |
|---|---|---|
| Active-only visibility | The moment a competitor pauses or ends a campaign, ALL its ads vanish from the library. | Monitor weekly or use a third-party tracking tool (Pathmatics, Adbeat) for historical snapshots. Manual monitoring is the only free option. |
| No date context | You cannot tell if an ad has been running for 2 days or 2 years. | Check monthly: if the same ad appears across multiple checks, it's a long-runner (likely performing). |
| Sponsored Content vs Text Ads | Only Sponsored Content appears in the Ad Library. Text Ads (right rail) are NOT included. | Acknowledge this blind spot. Text Ads are a smaller format but may carry different messaging. |
| InMail / Message Ads | Sponsored InMail does NOT appear in the Ad Library. These are 1:1 messages visible only to recipients. | You cannot analyze competitor InMail strategy from the Ad Library. If the user asks about this, clarify the limitation immediately. |

## TikTok Creative Center Deep Dive

### What's Actually Available

| Data Point | Available? | Precision |
|---|---|---|
| Top-performing ads by industry | Yes | Curated selection, NOT a complete library |
| CTR/CVR benchmarks | Yes (aggregated) | Industry-level averages, not per-ad metrics |
| Video ad creative | Yes | Playable video with audio |
| Trending audio/music | Yes | Current trending sounds used in ads |
| Hashtag performance | Yes | Aggregated volume and trend direction |
| Specific brand ad library | No | Cannot search for "all ads by Company X" like Facebook |
| Spend | No | Not exposed |
| Run dates | No | Only "trending now" vs "trending this week/month" |

### TikTok-Specific Gotchas

| Gotcha | Impact | Workaround |
|---|---|---|
| Curated, not comprehensive | TikTok decides which ads appear as "top performing." Selection criteria are opaque. | Use TikTok Creative Center for format/trend inspiration, NOT for competitive intelligence. It's not a competitive tool despite appearing in the same category. |
| Spark Ads invisible | Spark Ads (boosted organic posts) may not appear in the Creative Center. They look like organic content with a small "Sponsored" label. | Monitor competitor TikTok profiles directly for posts with "Sponsored" label that don't appear in Creative Center. |
| Regional variation | Top ads vary significantly by country. US top ads are different from UK or SEA top ads. | Always set the country filter. Default results may not match the user's target market. |

## Platform Selection Decision

| Analysis Goal | Best Platform | Why |
|---|---|---|
| Complete historical analysis of competitor ad strategy | Facebook Ad Library | Longest retention (2019+), shows inactive ads, broadest data per ad |
| Understanding current competitor messaging and offers | LinkedIn Ad Library (B2B) or Facebook (B2C) | Active ads reflect current strategy; LinkedIn shows targeting categories |
| Estimating competitor ad spend | Facebook Ad Library (EU advertisers only) | Only platform that surfaces spend ranges |
| Identifying trending ad formats and creative approaches | TikTok Creative Center | Curated for creative quality, includes format/trend data |
| Search advertising competitive analysis | Google Ads Transparency Center | Only platform showing text ad creative; but no keyword data |
| Multi-platform competitive picture | Facebook + Google + LinkedIn (all three) | No single platform covers everything; combine for full view |
