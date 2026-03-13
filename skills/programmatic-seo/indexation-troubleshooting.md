# pSEO Indexation Troubleshooting

## Indexation Rate Diagnosis

After launching programmatic pages, monitor indexation rate in Google Search Console. Expected rates and diagnostic actions:

| Indexation Rate (after 60 days) | Diagnosis | Action |
|---|---|---|
| >80% | Healthy. Google considers your pages indexable and valuable | Continue monitoring. Focus on ranking optimization |
| 50-80% | Mixed signals. Some pages passing quality threshold, others not | Identify patterns: which page types are indexed vs not? Sort by template, data completeness, word count |
| 20-50% | Quality problem. Google is crawling but choosing not to index most pages | Audit the non-indexed pages. Check "Discovered - currently not indexed" and "Crawled - currently not indexed" in Coverage report |
| <20% | Severe quality or crawl issue | Check: (1) Are pages in sitemap? (2) Are pages linked from site? (3) Is robots.txt blocking? (4) Are pages being crawled at all? |

## Search Console Coverage Report Interpretation

| GSC Status | What It Means | pSEO-Specific Cause | Fix |
|---|---|---|---|
| "Discovered - currently not indexed" | Google knows the URL exists but hasn't crawled it yet | Crawl budget exhaustion. Google allocates limited crawls per day. 50K new URLs overwhelm the crawl budget | Reduce sitemap to highest-priority pages. Improve internal linking from high-authority pages. Submit URLs via URL Inspection API (quota: 10K/day) |
| "Crawled - currently not indexed" | Google crawled the page but decided it's not worth indexing | **This is the most common pSEO failure.** Google crawled, evaluated, and rejected the page. Usually thin content or duplicate content | Audit these pages: compare content to indexed pages. Add unique value. If pattern-wide, the template needs more unique content per page |
| "Duplicate without user-selected canonical" | Google found multiple pages with substantially similar content | Template pages with insufficient variation. Google picked one as canonical and discarded the rest | Increase unique content per page. Check that canonical tags point to self (not all pointing to a hub page). Differentiate title tags |
| "Duplicate, submitted URL not selected as canonical" | You specified a canonical that Google disagrees with | Your canonical tag points to page A, but Google thinks page B is better | Google overrides canonicals when it detects the designated canonical is NOT the best version. Fix the underlying content duplication |
| "Excluded by 'noindex' tag" | Page has a noindex directive | Intentional (you noindexed low-value pages) or accidental (CMS adds noindex to dynamically generated pages) | If intentional: expected. If accidental: check CMS settings, dynamic rendering configuration, and meta tag injection logic |
| "Blocked by robots.txt" | robots.txt prevents crawling | Overly broad robots.txt rule blocking entire programmatic subdirectory | Review robots.txt. Common mistake: `Disallow: /search/` blocking all `/search/*` programmatic pages |
| "Soft 404" | Google detects the page returns 200 but looks like an error page | Pages with empty data sections, "No results found" content, or minimal text above fold | Set minimum data thresholds. If a page can't populate its template adequately, return actual 404 or noindex it |

## Crawl Budget Optimization

Google allocates a crawl budget based on site authority and server responsiveness. For large pSEO deployments, crawl budget is often the bottleneck.

| Factor | Impact on Crawl Budget | Optimization |
|---|---|---|
| Server response time | Pages responding >500ms get crawled less frequently | Target <200ms response time. Pre-render and cache programmatic pages. CDN for static pages |
| Sitemap quality | Sitemaps with >30% non-indexable URLs waste crawl budget | Only include indexable, canonical URLs. Remove 404s, redirects, and noindexed pages within 7 days |
| Internal link depth | Pages >4 clicks from homepage get crawled less frequently | Ensure all programmatic pages are within 3 clicks. Use hub pages to flatten the link structure |
| URL parameter handling | URLs with query parameters may be crawled as separate pages | Declare parameter handling in GSC (deprecated but still somewhat effective). Use clean URLs without parameters |
| Page freshness signals | Frequently updated pages get crawled more often | Add lastmod dates to sitemap entries. Actually update the content (Google ignores lastmod if content hasn't changed) |
| Redirect chains | Multiple redirects (A->B->C) waste crawl budget and lose PageRank | Maximum 1 redirect hop. Audit for chains quarterly. Fix at the source, not by adding more redirects |

## Helpful Content Recovery

If your programmatic pages triggered the Helpful Content System (HCS), recovery is possible but slow.

| Phase | Timeline | Action | Expected Result |
|---|---|---|---|
| 1. Diagnosis | Week 1 | Identify which pages triggered HCS. Check for site-wide ranking drops coinciding with HCS updates (use Google's "Search ranking updates" timeline) | Understanding of scope: is it specific page types or site-wide? |
| 2. Audit | Weeks 1-2 | Audit ALL programmatic pages. Calculate unique content percentage per page. Identify pages below 10% unique content. Count total thin pages vs quality pages | Quantified problem: "4,500 of 6,000 pages have <10% unique content" |
| 3. Remediation | Weeks 2-6 | Three options: (1) Add genuine unique content to thin pages, (2) Noindex thin pages, (3) 410 (permanently remove) the worst pages | Option 2 is fastest. Option 1 is best long-term. Option 3 is for pages you'll never fix |
| 4. Signal to Google | After remediation | Request re-crawl of updated pages via URL Inspection. Update sitemap. Wait | Google needs to re-crawl AND re-evaluate. This is NOT instant |
| 5. Recovery | 3-6 months after remediation | HCS re-evaluation happens during Google's periodic classifier updates (roughly monthly, but not guaranteed) | Gradual ranking restoration. Full recovery typically takes 2-3 HCS update cycles |

**Critical**: HCS is a site-wide signal. Even if only your programmatic pages are thin, the penalty affects your ENTIRE site's rankings. This is why the 30% rule exists -- keeping thin pages below 30% of your total indexed pages minimizes site-wide impact.

## Monitoring Dashboard Metrics

| Metric | Source | Healthy | Warning | Critical |
|---|---|---|---|---|
| Indexation rate | GSC Coverage report | >80% indexed | 50-80% | <50% |
| Crawl frequency | GSC Crawl Stats | Daily crawls for priority pages | Weekly crawls | Monthly or less |
| Avg. position (by template type) | GSC Performance report | Improving or stable | Declining 5+ positions over 30 days | Dropped off page 1 across template type |
| Click-through rate | GSC Performance report | >2% for pSEO pages | 1-2% | <1% (title/description not compelling) |
| Soft 404 count | GSC Coverage report | 0 | <5% of pages | >5% of pages |
| Pages per crawl session | GSC Crawl Stats | >100 pages/session | 50-100 | <50 (server too slow or content too thin to warrant deeper crawl) |
