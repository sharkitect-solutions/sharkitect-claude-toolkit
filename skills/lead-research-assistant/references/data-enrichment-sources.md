# Data Enrichment Sources -- Detailed Reference

## Source Layering Strategy

Research quality scales with source diversity, not source quantity. The goal is to confirm data points across independent sources and fill gaps that no single source covers.

**Rule of Two:** Any data point used to score a lead (Tier 1 or Tier 2) must be confirmed by at least two independent sources. Single-source data points get flagged with "[unverified]" in the output.

---

## Layer 1 -- Public Web Sources (Free, Always Start Here)

### Company Website
- **What it gives you:** Official positioning, product/service description, team page, pricing (sometimes), blog content showing thought leadership priorities
- **Lead research value:** Reveals self-identified pain points (what they sell = what they think the market needs), company size signals (team page), and technology sophistication (site quality, tech choices)
- **Watch out for:** Websites lag reality by 6-18 months. A company in crisis still has an optimistic website. Cross-reference with other sources.

### Job Boards (LinkedIn Jobs, Indeed, company careers page)
- **What it gives you:** Active hiring = active investment. Job descriptions reveal tech stack, pain points, budget ranges, and organizational priorities
- **Lead research value:** THE single most underused lead research source. A job posting for "Revenue Operations Manager" tells you: they're scaling sales, they have budget for ops, they probably need tools, and the hiring manager is your buyer
- **Specific signals:**
  - Posting for a role your product replaces = strong intent
  - Posting mentioning your competitor's product in requirements = evaluation window
  - Multiple postings in one department = growth investment
  - Posting mentions "building from scratch" or "greenfield" = no incumbent

### LinkedIn Company Page
- **What it gives you:** Employee count, growth trend, department breakdown, recent posts, employee engagement
- **Lead research value:** Employee count trend over 6 months tells you growth trajectory. Department sizes reveal organizational priorities. Company posts reveal strategic messaging.
- **Technique:** Compare "About" employee count to actual LinkedIn member count. Large discrepancy suggests rapid change (growth or contraction).

### GitHub (for tech companies)
- **What it gives you:** Tech stack (languages, frameworks), engineering culture, open-source involvement, team size and activity
- **Lead research value:** If selling developer tools, GitHub activity is the best signal. Look at: languages used, CI/CD tools in configs, dependency files (package.json, requirements.txt), and issue discussions mentioning pain points.

### Press Releases and News
- **What it gives you:** Funding announcements, leadership changes, product launches, partnerships, expansion plans
- **Lead research value:** Trigger events. New funding = budget. New CTO = tool evaluation window. Expansion = new operational needs. Acquisition = integration challenges.

---

## Layer 2 -- Aggregator Platforms (Free Tier or Paid)

### Crunchbase
- **What it gives you:** Funding history, investors, founding date, employee count range, acquisitions, key people
- **Lead research value:** Funding recency and amount directly correlate with buying capacity. Series A = still scrappy, budget-conscious. Series C+ = willing to buy best-in-class. Last funding > 3 years ago with no revenue data = possible cash constraints.

### G2 / Capterra / TrustRadius
- **What it gives you:** Software the company uses (if they've left reviews), competitor evaluations, satisfaction levels
- **Lead research value:** If they reviewed a competitor product, they're actively using and evaluating that category. Low ratings on competitor = dissatisfaction = opportunity. Review authored by a specific person = that person is a potential champion or decision maker.
- **Power technique:** Search for reviews written BY employees of your target company. The reviewer is someone who cares about this category enough to write about it.

### BuiltWith / Wappalyzer
- **What it gives you:** Technology stack of any website -- analytics tools, CMS, frameworks, payment processors, marketing tools
- **Lead research value:** Reveals current tool investments. If they use competitor X, you know the switching conversation. If they DON'T use any tool in your category, it's a greenfield opportunity (but may also mean they don't prioritize it).

### Glassdoor
- **What it gives you:** Employee satisfaction, management quality, salary ranges, interview process, company culture
- **Lead research value:** Employee complaints about processes = operational pain points. "Outdated tools" or "manual processes" in reviews = buying signals for automation/tooling. High turnover in a department = leadership seeking solutions.

### SimilarWeb
- **What it gives you:** Website traffic, traffic sources, competitor comparison, audience demographics
- **Lead research value:** Traffic trends reveal growth trajectory. Traffic sources show marketing sophistication. Competitor overlap shows market awareness.

---

## Layer 3 -- Deep Research (Paid / Specialized)

### ZoomInfo / Apollo / Clearbit
- **What it gives you:** Direct contact information, org charts, technographics, intent data, company hierarchies
- **Lead research value:** When available, these are the fastest path to decision-maker identification. But they're Tier 3 data -- only invest in lookups after Tier 1 qualification passes.
- **Without paid access:** Approximate using LinkedIn (org chart), company website (team page), and email pattern guessing (first.last@company.com covers 70% of B2B).

### SEC Filings (Public Companies)
- **What it gives you:** Revenue, expenses, strategic priorities, risk factors, executive compensation, material contracts
- **Lead research value:** 10-K "Risk Factors" section is a goldmine -- companies literally list what keeps them up at night. If your product addresses a listed risk factor, that's a boardroom-level pain signal.

### Patent Databases
- **What it gives you:** Innovation direction, R&D focus areas, competitive moat analysis
- **Lead research value:** Niche use -- primarily for selling into R&D or IP-heavy organizations. Recent patents in your product's domain = they care deeply about this space.

---

## Verification Matrix

| Data Point | Minimum Sources Required | Recommended Sources |
|---|---|---|
| Company size / employee count | 2 | LinkedIn + Crunchbase + company website |
| Tech stack | 2 | BuiltWith + job postings + GitHub |
| Funding status | 1 (Crunchbase is authoritative) | Crunchbase + press releases |
| Decision maker identity | 2 | LinkedIn + company website + job postings |
| Active pain signal | 2 | Job postings + reviews/forums + news |
| Budget availability | 2 (indirect) | Funding + hiring patterns + company size |
| Competitor usage | 1 (if review-sourced) | G2/Capterra + BuiltWith + job postings |

---

## Research Time Budget

Allocate research time based on lead potential:

| Lead Score (estimated) | Max Research Time | Source Depth |
|---|---|---|
| Likely 8-10 | 30-45 minutes | All three layers |
| Likely 5-7 | 15-20 minutes | Layer 1 + selective Layer 2 |
| Likely 1-4 (or unknown) | 5-10 minutes | Layer 1 only (Tier 1 check) |
| Disqualified at Tier 1 | Stop immediately | No further research |
