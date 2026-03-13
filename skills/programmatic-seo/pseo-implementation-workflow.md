# pSEO Implementation Workflow

## Phase 0: Viability Assessment (Before Building Anything)

Answer these 5 questions. If any answer is "no" or "I don't know," stop and resolve before building.

| Question | Why It Matters | Red Flag Answer |
|---|---|---|
| 1. Does the keyword pattern have aggregate search volume >10K/month? | Below 10K aggregate, the total traffic opportunity may not justify the build effort. Calculate: (aggregate volume) x (expected CTR at position 3-5, ~5-8%) = estimated traffic | "I think people search for this" without data. Use Ahrefs, SEMrush, or Google Keyword Planner to validate actual volume |
| 2. Can you provide >30% unique content per page without manual writing? | Below 30%, you're in "thin content" territory and risk Helpful Content penalties. The unique content must come from data, UGC, or algorithmic enrichment -- not just variable substitution | "We'll swap the city name and add some AI-generated paragraphs." This is exactly what Google penalizes |
| 3. Is your data source Tier 3 or higher (UGC, product-derived, or proprietary)? | Tier 4-5 data (licensed or public) means any competitor can build the same pages. Your ranking advantage is temporary | "We'll scrape the same data everyone else uses." Zero defensibility. Competitors with higher DA will outrank you |
| 4. Can you sustain data freshness for the page count you're planning? | Stale pages lose rankings and user trust. More pages = more maintenance | "We'll update it later." No automation plan = guaranteed staleness. Calculate: (pages) x (update frequency) x (time per update) |
| 5. Do you have (or can you build) internal linking from high-authority pages? | Orphaned programmatic pages don't get crawled or indexed | "We'll put them in the sitemap." Sitemap alone results in <20% indexation for new pSEO pages |

## Phase 1: Research and Validation (Week 1-2)

| Step | Tool | Output | Decision Gate |
|---|---|---|---|
| 1. Keyword pattern research | Ahrefs/SEMrush keyword explorer. Search for the HEAD term, then analyze patterns in suggestions | List of keyword patterns with aggregate volume, volume distribution (head vs tail), and trend direction | STOP if aggregate volume <10K/month or trend is declining |
| 2. Competition analysis | Search each pattern variant. Analyze top 3 results | Competitor page audit: content depth, data sources, update frequency, DA, page count | STOP if top 3 competitors are DA 70+ with deep content AND you're DA <30 |
| 3. Data source identification | Inventory available data for each template variable | Data source map: what populates each section, where it comes from, how it's updated | STOP if all data sources are Tier 5 (public) with no enrichment path |
| 4. Template prototype | Build 5 representative pages manually (covering head, mid-tail, and long-tail keywords) | 5 draft pages with actual data | STOP if the pages don't provide genuine value when you read them honestly. If you wouldn't click, neither would users |
| 5. Unique content calculation | For each prototype page, calculate unique content percentage vs template boilerplate | Unique content % per page | STOP if average unique content <30% |

## Phase 2: Template and Data Architecture (Week 2-3)

| Component | Specification | Quality Check |
|---|---|---|
| URL structure | Define pattern: `/[category]/[slug]/`. All lowercase, hyphenated, max 3 levels deep | No IDs in URLs. No query parameters. Trailing slash consistent site-wide |
| Title tag template | Pattern: `[Primary Keyword] - [Secondary Info] | [Brand]`. Under 60 chars to avoid truncation | Check 10 variations for readability. No keyword stuffing. Each title must be unique |
| Meta description template | Pattern with variables. 150-160 chars. Include primary keyword and CTA | Check that variable substitution doesn't create awkward phrasing. "Best [service] in [city]" should read naturally for every city |
| H1 template | One H1 per page. Should match or closely align with title tag | No exact-match keyword stuffing. Natural language that a human would write |
| Content sections | Define which sections are template (shared) vs data-driven (unique) vs conditional (shown only if data exists) | Conditional sections prevent empty/thin content. If `local_regulations` data is empty, hide the section entirely -- don't show "No data available" |
| Schema markup | Define JSON-LD templates per page type. Common: LocalBusiness, Product, FAQPage, BreadcrumbList | Validate with Google's Rich Results Test for 5 representative pages. Schema must match visible page content |
| Internal linking logic | Define cross-linking rules: related pages by geography, category, or attribute | Max 5-10 internal links per page in content area (excluding nav/footer). Links must be contextually relevant |
| Data pipeline | Define how data flows: source -> storage -> template rendering | Include freshness schedule (how often each data source is refreshed) and fallback behavior (what happens when an API fails) |

## Phase 3: Staged Rollout (Week 3-6)

| Stage | Page Count | Duration | Success Criteria | Failure Action |
|---|---|---|---|---|
| 1. Seed batch | 50-100 pages (highest-volume keywords) | 2 weeks | >70% indexed in GSC after 14 days. No "Crawled - currently not indexed" pattern | Audit non-indexed pages. If pattern-wide: template quality issue. If specific pages: data quality issue. Fix before expanding |
| 2. Expansion A | 500-1,000 pages (head + mid-tail) | 3 weeks | >60% indexed after 21 days. Average position improving or stable for seed batch | If indexation rate drops below 50%: Google is signaling quality concerns. STOP expansion. Improve template quality |
| 3. Expansion B | Up to 5,000 pages (including long-tail) | 4 weeks | >50% indexed after 28 days. Seed batch showing impressions/clicks growth in GSC | If seed batch rankings drop after expansion: the new pages are diluting quality. Noindex lowest-quality pages |
| 4. Full deployment | Remaining pages | Ongoing | Stable indexation rate. No ranking regression for seed batch | Monitor weekly. Any site-wide ranking drop may indicate Helpful Content System flagging |

**Between each stage**: Wait the full duration. Do NOT accelerate because "the first batch looks good." Google's quality evaluation has delayed effects -- penalties can appear 2-4 weeks after indexation.

## Phase 4: Monitoring and Optimization (Ongoing)

| Frequency | Check | Tool | Action Threshold |
|---|---|---|---|
| Daily (first month) | New indexation in GSC | Google Search Console > Pages | If indexation rate drops 10+ percentage points day-over-day: investigate immediately |
| Weekly | Ranking changes for seed keywords | Ahrefs/SEMrush rank tracker | If average position drops 5+ positions for >20% of tracked keywords: audit recent changes |
| Bi-weekly | Content freshness | Internal dashboard (last_verified dates) | Pages with last_verified >90 days: queue for data refresh |
| Monthly | Competitor analysis | Manual search for top 10 keywords | If new competitor appears in top 3: analyze their pages. Identify what they're doing differently |
| Monthly | UGC volume (if applicable) | Internal metrics | If UGC per page dropping: review collection prompts, incentives, and moderation speed |
| Quarterly | Full template audit | Manual review of 20 random pages | Read the pages as a user. If they don't provide value, fix the template. Don't rely only on metrics |

## Common Rollout Failures

| Failure | Root Cause | Prevention |
|---|---|---|
| "Indexation cliff" -- first batch indexes fine, second batch doesn't | First batch got indexed because of novelty. Second batch reveals the pattern to Google, triggering quality evaluation | Don't change template quality between batches. If anything, later batches should be HIGHER quality (more data, more UGC) |
| "Ranking cannibalization" -- new pages steal rankings from existing pages | Programmatic pages target keywords that existing content already ranks for | Keyword-to-URL mapping before launch. If existing content ranks well for a keyword, don't create a programmatic page for it |
| "Crawl budget exhaustion" -- Google stops crawling after first 1,000 pages | Server response time too slow, or too many low-quality pages in sitemap | Pre-render and cache all pages. Remove non-indexable URLs from sitemap. Improve server performance |
| "Site-wide penalty" -- even non-programmatic pages lose rankings | Programmatic pages triggered Helpful Content System | This is the worst-case scenario. See Helpful Content Recovery guide. Noindex ALL thin programmatic pages immediately |
| "Stale data decay" -- pages rank initially but slowly lose positions | Data becomes outdated. Competitors update their pages. Users bounce because information is wrong | Build data freshness automation BEFORE launch, not after. If you can't automate freshness for the page count, reduce page count |
