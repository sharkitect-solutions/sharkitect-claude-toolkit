---
name: seo-optimizer
description: Use when optimizing website content for search rankings, conducting keyword research, auditing technical SEO issues, implementing schema markup, or planning organic content strategy. NEVER use for paid search (PPC/Google Ads), social media strategy, or general copywriting that is not search-intent-driven.
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# SEO Optimizer

## SEO Conflict Resolution

These are the real decisions that require judgment. Claude's default behavior without this skill is to treat each SEO factor in isolation. Apply these resolutions instead.

| Conflict | Default Mistake | Correct Resolution |
|---|---|---|
| Page speed vs. content richness | Remove images/JS to hit Core Web Vitals targets | Optimize delivery (lazy load, WebP, CDN) before removing content. Speed wins only when content removal has zero user-experience cost. |
| Keyword density vs. natural readability | Force keyword to 1-2% density even when it sounds robotic | Semantic variants and related terms count. One natural mention in H1 + one in intro is sufficient. Readability beats density every time. |
| Content length vs. search intent | Default to 2,000+ words because "longer ranks better" | Match intent: transactional queries want concise pages with clear CTAs, not exhaustive guides. Long-form is correct for informational head terms only. |
| Internal linking vs. user flow | Add 5+ internal links per page because "links pass authority" | Cap at 3-5 per 1,000 words. Each link is a distraction. Prioritize links that help the user complete their task, not links that sculpt PageRank. |
| Canonical vs. content variation | Canonical every near-duplicate to the main URL by default | Let pages compete when they serve different intent variants (e.g., "best running shoes" vs. "cheap running shoes"). Canonical kills ranking opportunity for legitimately distinct pages. |
| Schema completeness vs. maintenance burden | Mark up every schema type on every page | Focus schema on pages with direct SERP feature opportunity: FAQ on support pages, Product on e-commerce, HowTo on tutorials. Skip schema on pages with no realistic rich result chance. |
| Freshness signals vs. content stability | Update dates and rewrite sections to appear fresh | Only update when content accuracy has degraded. Gratuitous refreshes without substance changes can trigger re-evaluation and temporary ranking dips. |

## Intent-to-Content Format Decision Framework

Search intent determines format before any other consideration. Getting this wrong makes optimization effort irrelevant.

| Intent Type | Signal Words | Correct Format | Wrong Format |
|---|---|---|---|
| Informational | "how to", "what is", "guide", "tutorial", "learn" | Long-form guide, step-by-step, comparison tables | Product pages with CTAs |
| Navigational | Brand name, "[brand] login", "[product] pricing" | Landing page, direct answer, quick links | Blog posts, guides |
| Transactional | "buy", "price", "discount", "order", "cheap" | Product page with clear CTA, minimal friction | Long editorial content |
| Commercial investigation | "best", "vs", "review", "alternative", "top 10" | Comparison page, review with verdict, case study | Pure informational guides with no recommendation |

When intent is ambiguous: check the top 5 SERP results. The format Google is already ranking reveals the inferred intent. Match that format.

## SEO Audit Priority Matrix

Fix in this order. Impact is not alphabetical or intuitive -- this sequence is derived from what creates the fastest measurable ranking lift.

**Tier 1 -- Fix immediately (blocks indexing or signals penalties):**
- Pages accidentally blocked in robots.txt or noindex that should rank
- Missing or duplicate title tags on pages that receive organic traffic
- Broken canonical tags pointing to non-existent or wrong URLs
- 4xx errors on pages with external backlinks
- Redirect chains longer than 3 hops (link equity bleeds at each hop)

**Tier 2 -- Fix this week (direct ranking signal improvement):**
- Missing schema markup on pages with clear rich result opportunity
- Thin content (under 300 words) on pages Google has already indexed and ranked
- Mobile usability failures reported in Google Search Console
- Core Web Vitals failing pages that are in the top 20% of organic traffic
- Title tags over 60 characters getting truncated in SERPs

**Tier 3 -- Fix this month (incremental gains, compounding over time):**
- Image alt text missing on content images (decorative images do not need alt text)
- Internal linking gaps -- high-authority pages not linking to related content
- Content freshness on pages ranking positions 4-10 that cover time-sensitive topics
- URL structure cleanup on new site sections (avoid touching existing URLs that rank)

## Edge Cases That Change All Advice

| Scenario | How Standard SEO Advice Breaks | What to Do Instead |
|---|---|---|
| Single-page app (SPA) with client-side rendering | Standard crawling advice fails -- Googlebot may not execute JS fully | Implement server-side rendering (SSR) or static site generation (SSG). Test with Google's URL Inspection tool. Treat hydration time as a Core Web Vitals factor. |
| International/multilingual site | Separate-URL strategy creates duplicate content risk; subdomain vs. subdirectory debate is context-dependent | Use hreflang annotations for every language/region pair. Prefer subdirectory (/en/, /es/) over subdomains for sites without CDN infrastructure to support subdomain authority building. |
| E-commerce with 10,000+ product pages | Crawl budget becomes a real constraint; faceted navigation creates URL explosion | Use robots.txt or canonical tags to consolidate faceted navigation. Prioritize crawl budget for pages with sales potential. Paginate category pages with rel=next/prev patterns. |
| Content behind login or paywall | Google cannot index gated content by default | Use first-click-free or structured data paywallContent schema. For lead gen, ensure metadata (title, description) is descriptive enough to generate clicks even when content is gated. |
| Site migration (domain change or URL restructure) | Redirect mapping errors can erase years of ranking history | Map every URL with inbound links or organic traffic. Implement 301s before DNS cutover. Monitor Search Console for coverage errors for 90 days post-migration. Expect 10-20% temporary traffic dip. |

## SEO Activation Reminders

These principles are deeply known. This table exists only as a pre-flight check -- not learning material. Review before starting any optimization task.

| Area | One-Line Check |
|---|---|
| Title tag | Under 60 chars, primary keyword near start, unique per page |
| Meta description | 150-160 chars, compelling, matches page content (does not affect ranking, affects CTR) |
| H1 | One per page, contains primary keyword, matches or closely mirrors title tag |
| URL structure | Lowercase, hyphens not underscores, keyword-relevant, stable once published |
| Images | WebP or compressed JPEG, descriptive alt text on content images, width/height set |
| E-E-A-T | Author credentials, cited sources, original insight -- applies to YMYL topics most |
| Core Web Vitals | LCP < 2.5s, FID/INP < 200ms, CLS < 0.1 -- measure on field data not lab only |
| Mobile-first | Test on real devices -- viewport, tap target size (48x48px min), font 16px min |
| Internal links | Descriptive anchor text, 3-5 per 1,000 words, update old content to link new |
| Schema | Validate with Google's Rich Results Test before deploying |

## Pre-Publish SEO Checklist

- [ ] Title tag: unique, keyword-forward, under 60 characters
- [ ] Meta description: 150-160 characters, written to earn clicks
- [ ] H1 present, one only, contains primary keyword
- [ ] URL is readable and keyword-relevant
- [ ] Images have alt text; file sizes compressed
- [ ] Internal links added to and from this page
- [ ] Schema markup implemented and validated
- [ ] Mobile rendering tested
- [ ] Canonical tag correct or absent (do not self-canonical every page by default)

## Rationalization Table

| Rationalization | Why It Is Wrong |
|---|---|
| "The user just wants the content written, not a full SEO audit" | Keyword placement, title tag, and intent alignment take 2 minutes and compound over years. Skipping them on request is negligence, not efficiency. |
| "This page doesn't need schema -- it's just a blog post" | Blog posts are eligible for Article schema, breadcrumb schema, and FAQ schema if they contain Q&A sections. Skipping schema is a missed rich result opportunity. |
| "I'll optimize for search volume -- just pick the highest volume keyword" | High volume without intent match = traffic that bounces. A lower-volume keyword with correct intent match will outperform on conversions and dwell time, which are ranking signals. |
| "The content is good so the technical SEO doesn't matter much" | A page blocked in robots.txt or missing a canonical tag will not rank regardless of content quality. Technical SEO is a prerequisite, not optional polish. |
| "Long-form content always ranks better" | Intent determines length. A transactional page with 3,000 words of explanation will underperform a concise 400-word page that converts. Length should match what the user came to find. |
| "We can always fix the URL structure later" | Changing URLs on ranking pages requires 301 redirects and costs link equity temporarily. URL structure decisions should be made before content is indexed. |
| "Duplicate content penalty is a myth so it doesn't matter" | While there is no manual penalty, Google chooses which duplicate to index and rank -- often not the one intended. Canonical tags are the mechanism for controlling this choice. |

## Red Flags Checklist

Signs this skill is being applied incorrectly or incompletely:

- [ ] Recommending keyword density targets without checking if the text reads naturally
- [ ] Suggesting canonical tags on every page regardless of whether duplicate content exists
- [ ] Optimizing title tags without checking current character count in a SERP preview
- [ ] Adding schema markup without validating with Google's Rich Results Test
- [ ] Recommending content length without first checking the format of top-ranking results
- [ ] Ignoring search intent and optimizing purely for keyword inclusion
- [ ] Treating Core Web Vitals lab scores as authoritative (field data is what Google uses)
- [ ] Recommending URL changes on pages that are already indexed and receiving traffic
- [ ] Adding internal links without checking that anchor text is descriptive and varied
- [ ] Skipping mobile testing and assuming desktop optimization is sufficient

## NEVER

| Prohibition | Why |
|---|---|
| NEVER recommend changing URLs on ranking pages without a redirect plan | Changing URLs without 301 redirects destroys ranking history. Even with redirects, there is a temporary ranking impact. |
| NEVER keyword stuff -- including in alt text, title tags, or meta descriptions | Modern Google identifies and discounts over-optimized text. Readability is itself a ranking signal via engagement metrics. |
| NEVER block CSS or JavaScript in robots.txt | Googlebot needs to render the page to evaluate it. Blocking render resources causes Google to see a broken page. |
| NEVER set noindex on pages without confirming they have no ranking value | Noindex is irreversible in the short term -- removed pages take weeks to de-index, and re-indexing after removing noindex is not immediate. |
| NEVER treat schema markup as a guaranteed rich result | Schema is eligibility, not entitlement. Google decides whether to display rich results based on quality signals beyond schema presence. |
| NEVER recommend a site migration without a full URL redirect map | Unmapped URLs from a migration lose all accumulated link equity and ranking history permanently. |
