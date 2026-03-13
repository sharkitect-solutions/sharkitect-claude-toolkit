---
name: programmatic-seo
description: "Use when building SEO-optimized pages at scale using templates and data, designing programmatic page strategies, selecting pSEO playbooks, evaluating data defensibility for page generation, or diagnosing thin content and indexation issues with template-generated pages. Also use when the user mentions programmatic SEO, template pages, directory pages, location pages, comparison pages at scale, or integration landing pages. NEVER use for auditing existing SEO technical issues (seo-optimizer), writing individual content pieces (content-research-writer), competitor product comparison strategy (competitor-alternatives), or general copywriting for landing pages (copywriting)."
version: "2.0"
optimized: true
optimized_date: "2026-03-12"
---

# Programmatic SEO

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Playbook selection, Google quality gates, data defensibility, template quality calibration, URL architecture, internal linking, indexation strategy, anti-patterns | Always (auto-loaded) |
| indexation-troubleshooting.md | Indexation rate diagnosis, Search Console Coverage report interpretation (specific GSC status codes), crawl budget optimization, Helpful Content System recovery phases and timeline, monitoring dashboard metrics | When programmatic pages aren't getting indexed, diagnosing GSC coverage issues, recovering from Helpful Content penalties, or setting up pSEO monitoring |
| data-enrichment-strategies.md | Data tier upgrade paths (Tier 5 to 3+), API sources for location data enrichment (Census, Numbeo, Google Places, BLS), UGC collection frameworks, data freshness automation, content enrichment without APIs | When planning data sources for new pSEO pages, upgrading from public data to more defensible sources, implementing UGC collection, or solving the cold start problem for new pages |
| pseo-implementation-workflow.md | Phase 0 viability assessment (5 go/no-go questions), Phase 1 research and validation, Phase 2 template and data architecture, Phase 3 staged rollout (4 expansion stages with decision gates), Phase 4 ongoing monitoring, common rollout failures | When building a new pSEO program from scratch, planning a staged rollout, or diagnosing why a rollout is failing |

Do NOT load companion files for basic playbook selection, URL structure decisions, or anti-pattern reference -- SKILL.md covers these decisions fully.

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| Programmatic page strategy and playbook selection | YES | -- |
| Template design for scaled page generation | YES | -- |
| Data defensibility assessment for pSEO | YES | -- |
| Internal linking architecture for programmatic pages | YES | -- |
| Thin content detection and quality calibration | YES | -- |
| Indexation strategy for large page sets | YES | -- |
| Keyword pattern research for scaled pages | YES | -- |
| URL structure for programmatic pages | YES | -- |
| Technical SEO auditing (crawl errors, site speed) | NO | seo-optimizer |
| Individual content writing | NO | content-research-writer |
| Competitor product comparison strategy | NO | competitor-alternatives |
| Landing page copywriting | NO | copywriting |
| Analytics tracking for page performance | NO | analytics-tracking |
| Schema markup implementation | NO | seo-optimizer |

## Playbook Selection Decision Matrix

12 proven pSEO patterns. Select based on what you have (data, product, audience), not what you want.

| Playbook | Pattern | Best When You Have | Search Volume Signal | Data Defensibility |
|---|---|---|---|---|
| Templates | "[type] template" | Downloadable/interactive assets users need | High intent, high volume | Medium -- competitors can create templates too, but quality and variety are defensible |
| Comparisons | "[X] vs [Y]", "[X] alternative" | Product in competitive space | High purchase intent | Low -- anyone can compare. Win with depth, freshness, and actual testing data |
| Locations | "[service] in [city]" | Local data, multi-geo business | Massive aggregate volume, low per-page | Low unless you have proprietary local data (pricing, reviews, regulations). City-name-swapping is the #1 pSEO penalty trigger |
| Integrations | "[your product] + [tool]" | Product with integration ecosystem | Medium, high conversion intent | High -- only you know your integration details. Competitors can't replicate |
| Personas | "[product] for [role/industry]" | Product serving multiple segments | Medium, high conversion | Medium -- requires genuine segment-specific content, not just headline swaps |
| Curation | "best [category]", "top [N] [tools]" | Genuine evaluation expertise | High commercial intent | Low -- extremely competitive. Win with proprietary testing methodology or data |
| Conversions | "[X] to [Y]", "[amount] [unit] in [unit]" | Utility tool capability | Very high volume, low intent | Low for simple conversions, high if using proprietary conversion logic |
| Examples | "[type] examples", "[category] inspiration" | Gallery of real-world work | Research phase traffic | Medium -- curation quality and freshness are defensible |
| Glossary | "what is [term]", "[term] definition" | Domain expertise | Top-of-funnel, high volume | Low -- Wikipedia and competitors cover most terms. Win with unique examples and depth |
| Directory | "[category] tools/software" | Comprehensive category data | Research phase, high volume | Medium -- comprehensiveness and freshness are defensible if actively maintained |
| Profiles | "[entity name]", "[company] + [attribute]" | Unique data about entities | Informational, varies widely | High if using proprietary data. Low if scraping public info (Wikipedia already exists) |
| Translations | Same content, multiple languages | Content worth translating | Opens entire markets | Medium -- quality localization (not just translation) is defensible |

**Combination multiplier**: Layering playbooks (Locations + Personas: "marketing agencies for startups in Austin") multiplies page count but also multiplies thin content risk. Each combination must pass the Unique Value Test independently.

## Google Quality Gate

Google's algorithms specifically target low-quality programmatic pages. Every page must pass ALL of these.

| Gate | Test | Fail Signal | Consequence |
|---|---|---|---|
| Doorway page detection | Does this page exist primarily to funnel users to another page? | Page has thin content + aggressive CTAs + no standalone value | Manual action or algorithmic demotion. Entire subdirectory can be deindexed |
| Thin content | Remove the template -- what unique content remains on this specific page? | <30% of page content is unique to this URL. Or: only the H1 variable changes between pages | Helpful Content System demotes entire site (not just thin pages). Recovery takes 3-6 months after fixing |
| Keyword stuffing | Does the page repeat the target keyword unnaturally? | Keyword density >3% in body text, or keyword appears in every heading | Algorithmic demotion. Less severe than manual action but still significant ranking loss |
| Duplicate content | Is this page substantially similar to another page on your site? | >70% content overlap with another page (after removing boilerplate) | Google picks one canonical version and ignores the rest. Your "10,000 pages" become 500 in Google's index |
| E-E-A-T | Does this page demonstrate experience, expertise, authority, trust? | Template-generated content with no author, no sources, no evidence of experience | Particularly punishing for YMYL topics (health, finance, legal). Non-YMYL has more latitude |
| Site-wide quality | What percentage of your pages are low quality? | >30% of indexed pages have thin or duplicate content | Helpful Content System applies site-wide demotion. Even your good pages rank worse |

**The 30% rule**: If more than 30% of your programmatic pages would fail the thin content test, noindex them until you can add unique value. A smaller number of quality pages outperforms a large set that triggers site-wide quality signals.

## Data Defensibility Assessment

Rate your data source before building. This determines long-term ranking sustainability.

| Tier | Data Type | Defensibility | Examples | Risk |
|---|---|---|---|---|
| 1 (Strongest) | Proprietary -- you created it | Very high | Your product's usage analytics, proprietary research, original testing | If competitors can't access your data, they can't replicate your pages |
| 2 | Product-derived -- from your users | High | User reviews, community submissions, behavioral data | Defensible as long as your user base is active. Network effects compound |
| 3 | User-generated -- your community | Medium-high | Forum posts, submitted examples, ratings | Quality control challenge. Need moderation. But: authentic content is hard to fake |
| 4 | Licensed -- exclusive access | Medium | API partnerships, exclusive data feeds | Depends on exclusivity terms. If competitor can license the same data, advantage erodes |
| 5 (Weakest) | Public -- anyone can access | Low | Government databases, Wikipedia, public APIs | Zero defensibility. Competitors will scrape the same sources. Must differentiate on analysis or UX |

**Critical rule**: Tier 5 data alone will NOT sustain pSEO rankings long-term. Google increasingly favors "information gain" -- content that adds something beyond what's already available. If your page is just a prettier wrapper around public data, a competitor with better domain authority will outrank you.

## Template Quality Calibration

| Quality Level | Unique Content % | Page Count Guidance | Indexation Strategy | Example |
|---|---|---|---|---|
| Gold (recommended) | >60% unique per page | 100-1,000 pages | Index all. Each page earns its ranking | Location pages with local pricing data, provider reviews, regulation summaries. 15-20 min to create each page's unique content |
| Silver (acceptable) | 30-60% unique per page | 1,000-10,000 pages | Index pages above volume threshold. Noindex the rest | Integration pages with setup guides and use cases. Template provides structure, but each integration has genuine unique content |
| Bronze (risky) | 10-30% unique per page | 10,000-100,000+ pages | Index top 20% by search volume. Noindex or paginate the rest | City pages where only the city name and a few data points change. Requires supplementing with UGC, local data, or dynamic enrichment |
| Thin (avoid) | <10% unique per page | Any count = problem | Do not index. These pages will trigger Helpful Content penalties | "Best [service] in [city]" where only the city name is swapped. Google detects this pattern specifically |

**Unique content formula**: (Total words unique to this page) / (Total words on page - boilerplate nav/footer) x 100. Headers with swapped variables don't count as unique.

## URL Architecture

| Decision | Recommendation | Why | Gotcha |
|---|---|---|---|
| Subfolder vs subdomain | Always subfolder (`/templates/resume/`) | Subfolders inherit main domain authority. Subdomains are treated as separate sites by Google -- your pSEO pages start with zero authority | Moving from subdomain to subfolder requires 301 redirects and typically causes 2-4 months of ranking turbulence |
| Slug format | Lowercase, hyphenated, keyword-rich | `/best-crm-for-startups/` is human-readable and keyword-containing | Never include IDs or parameters in slugs (`/p/12345/` tells Google nothing). If you need IDs for backend routing, use them as query params, not path segments |
| Hierarchy depth | Max 3 levels (`/category/subcategory/page/`) | Deeper URLs get crawled less frequently. Google treats URL depth as a quality signal | `/tools/crm/enterprise/manufacturing/midwest/` is too deep. Flatten: `/crm/manufacturing/` |
| Trailing slashes | Pick one, enforce globally | Mixing `/page` and `/page/` creates duplicate content (two URLs, same content) | Configure server-level redirect (301) to enforce your choice. Most CMS default to trailing slash |
| Pagination | `/page/2/`, `/page/3/` with rel=next/prev | Google removed official support for rel=next/prev in 2019 but still uses the signal heuristically | For pSEO directories: prefer "load more" or infinite scroll with proper rendering over paginated URLs. If paginating: canonical all pages to page 1 for list pages, or self-canonical for distinct content pages |

## Internal Linking Architecture

| Pattern | When | Structure | Scaling Gotcha |
|---|---|---|---|
| Hub and spoke | Single playbook, one hierarchy level | Hub: `/templates/` -> Spokes: `/templates/resume/`, `/templates/invoice/` | Hub page must have genuine content, not just a list of links. Google treats link-only pages as thin |
| Nested hub and spoke | Multiple hierarchy levels | `/locations/` -> `/locations/california/` -> `/locations/california/san-diego/` | State-level hubs often end up thin. Either add unique state-level content or make state pages a simple directory without expecting them to rank |
| Cross-linking mesh | Related pages should reference each other | "See also: [X] vs [Y]" at bottom of comparison pages. "Similar: [service] in [nearby city]" on location pages | Don't cross-link everything to everything. Google treats excessive internal linking (50+ links per page) as a quality signal. 5-10 relevant cross-links per page |
| Breadcrumbs | Always, for all pSEO pages | Structured data (BreadcrumbList schema) + visible navigation | Breadcrumbs must reflect actual site hierarchy, not keyword-stuffed paths. `Home > CRM > Best CRM for Startups` not `Home > Best CRM Software > CRM for Startups > Top CRM Startups` |

## Indexation Strategy

| Page Set Size | Volume Threshold | Strategy | Implementation |
|---|---|---|---|
| <500 pages | Index all if quality passes | Submit all in sitemap. Monitor indexation rate in Search Console | If <70% indexed after 60 days, quality is the problem, not crawl budget |
| 500-5,000 pages | Index pages with >10 monthly searches | Separate sitemaps by page type. Noindex pages below volume threshold | Use Search Console's "Pages" report to identify which patterns Google refuses to index |
| 5,000-50,000 pages | Index top 30% by volume | Tiered sitemaps with priority hints. Aggressive noindex for tail pages | Crawl budget becomes real. Google allocates ~10K-100K URLs/day depending on site authority. New pages may take weeks to get crawled |
| 50,000+ pages | Index only proven patterns | Roll out in batches (1,000 at a time). Monitor indexation and quality signals before expanding | At this scale, Helpful Content System evaluates your site as a whole. 50K thin pages will tank rankings for your entire domain |

**Sitemap hygiene**: Remove noindexed and 404'd URLs from sitemaps within 7 days. Sitemaps with >30% non-indexable URLs waste crawl budget and signal quality problems to Google.

## Anti-Patterns

| Name | Pattern | Why It Fails | Fix |
|---|---|---|---|
| The City Swapper | Location pages where only the city name changes. Same paragraph with "[City]" replaced 50,000 times | Google's duplicate content detection specifically targets variable-substitution patterns. Sites have been deindexed for this. Helpful Content penalty applies site-wide | Each location page needs unique local data: pricing, regulations, provider reviews, market stats. If you can't source local data, don't create the page |
| The Template Mill | Generating 100K+ pages from a single template with minimal variable content, hoping volume = traffic | Site-wide Helpful Content demotion. Google crawls a sample, detects the pattern, and applies the penalty to ALL pages including your non-programmatic content | Start with 100 pages. Prove they rank and convert. Scale only after confirming Google indexes and ranks them. 10x at a time, monitoring quality signals |
| The Orphan Factory | Programmatic pages with no internal links from the main site. Only accessible via sitemap | Google treats orphan pages as low-priority. Crawl frequency drops. Indexation rate below 20% for orphaned pages | Every programmatic page must be reachable within 3 clicks from homepage via category/hub pages. Sitemap is a backup, not the primary discovery mechanism |
| The Keyword Cannibal | Multiple programmatic pages targeting the same keyword ("best CRM" appears in 15 different page titles) | Google picks one URL to rank and suppresses the rest. You're competing with yourself. Worst case: Google picks the weakest page | One URL per target keyword. Use a keyword-to-URL mapping document. If two pages could rank for the same term, consolidate them or differentiate their targeting |
| The Stale Index | Programmatic pages generated once and never updated. "2024 Guide" still live in 2026 | Google's freshness signals penalize outdated content. Users bounce when they see stale dates or discontinued products | Build update automation into the generation pipeline. Minimum: update dates and data quarterly. Remove pages for discontinued products/locations within 30 days |
| The Data Desert | Pages where the data source dried up or never existed. Empty sections, "No data available", zero results | Users bounce immediately. Google measures engagement signals (pogo-sticking). Pages with no useful content get deindexed naturally | Set minimum data thresholds per page. If a location page has <3 providers or a comparison page has <2 data points per product, noindex it until data is available |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "More pages = more traffic, it's simple math" | Google ranks pages, not page counts. 100K thin pages get deindexed while 500 quality pages rank. Worse: the thin pages trigger site-wide Helpful Content penalties that drag down your quality pages too |
| "We'll add unique content later, let's just launch the templates" | Google's first impression matters. If pages are indexed as thin content, the Helpful Content signal is applied immediately. Recovering from it takes 3-6 months AFTER fixing the content. Launching thin and fixing later is more expensive than launching quality from the start |
| "Our competitor has 50K pages, we need 50K too" | Your competitor may have been building those pages for years with established domain authority. Their thin pages survive because their overall site quality is high. A new pSEO effort with 50K thin pages on a lower-authority domain will be penalized |
| "We just need to get indexed, then we'll optimize" | Indexation without ranking is worthless. Google will index thin pages initially, then remove them in the next Helpful Content update. You've wasted crawl budget and potentially triggered quality signals |
| "Location pages are easy -- just swap the city name" | This is the most common pSEO failure mode. Google has been detecting city-name-swapping since Panda (2011). 15 years of algorithm updates specifically targeting this pattern. The "easy" approach is the one most likely to get penalized |
| "We can use AI to generate unique content for each page" | AI-generated content at scale often has consistent patterns (sentence structure, vocabulary, paragraph length) that Google's classifiers detect. Plus: AI without unique data just paraphrases the same information differently -- which is the definition of thin content |

## Red Flags

- Programmatic pages where only the H1 and title tag change between URLs -- this is the exact pattern Google's Helpful Content System targets
- No keyword-to-URL mapping document -- guarantees keyword cannibalization as page count grows
- Pages generated from public data only (Tier 5) with no proprietary enrichment -- zero defensibility, first competitor with better DA wins
- Sitemap containing 50K+ URLs with no indexation monitoring -- crawl budget waste and potential quality signal
- Template pages with empty sections or "No data available" placeholders -- immediate bounce signal that compounds across the page set
- Launching 10K+ pages simultaneously without a staged rollout -- no opportunity to detect quality problems before site-wide impact
- Cross-linking every programmatic page to every other page in the same set -- excessive internal links (50+ per page) are a quality signal
- No update automation for data-dependent pages -- stale data causes increasing bounce rates and eventual deindexation

## NEVER

- Launch programmatic pages with <10% unique content per page -- this triggers Helpful Content penalties that affect your entire domain, not just the programmatic pages
- Use subdomains for programmatic pages -- subdomains don't inherit main domain authority, so your pSEO pages start from zero regardless of your main site's strength
- Generate pages for keyword patterns with zero search volume -- pages that get no traffic provide no SEO value and dilute your site's overall quality signal
- Skip the staged rollout -- always launch 100-500 pages first, monitor indexation and ranking for 30-60 days, then scale. Detecting a quality penalty on 50K pages is recovery-prohibitive
- Create location pages without local data beyond the city name -- Google has specifically targeted city-name-swapping since 2011 and detection has only improved since then
