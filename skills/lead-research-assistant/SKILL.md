---
name: lead-research-assistant
description: >
  Use when the user asks to find leads, prospects, target accounts, or potential customers
  for any product or service. Use when building outreach lists, qualifying prospects, or
  researching companies for sales or BD. Use when the user mentions ICP, lead scoring,
  prospect research, or account-based targeting. NEVER for recruiting/hiring research.
  NEVER for competitor analysis without a lead-gen angle. NEVER for market sizing alone.
---

# Lead Research Assistant

## The Research-Quality Problem

Most AI-generated lead lists fail in production. Sales teams report 60-70% of AI-suggested leads are unqualified -- either wrong company size, no budget authority, no active pain point, or already locked into a competitor. The root cause: research that stops at firmographics (industry + size + location) and never reaches intent signals or qualification depth.

This skill exists to produce leads that survive first contact with a sales team.

## Qualification Framework Selection

Different deal contexts demand different qualification lenses. Using the wrong framework wastes research time on irrelevant data points.

**Decision tree -- pick ONE primary framework:**

```
Is the deal > $50K ACV?
  YES --> Is the buying process committee-driven (3+ stakeholders)?
    YES --> Use MEDDIC (metrics, economic buyer, decision criteria, decision process, identify pain, champion)
    NO  --> Use BANT (budget, authority, need, timeline)
  NO  --> Is the product solving a known, urgent pain?
    YES --> Use CHAMP (challenges, authority, money, prioritization)
    NO  --> Use GPCTBA&CI (goals, plans, challenges, timeline, budget, authority, consequences, implications)
```

**Why this matters:** BANT on a $200K enterprise deal misses decision-process complexity. MEDDIC on a $5K SMB deal wastes time mapping stakeholders who don't exist. CHAMP works when pain is obvious and the buyer just needs to see you solve it. GPCTBA&CI works for consultative sales where the buyer hasn't fully articulated the problem yet.

See `references/qualification-frameworks.md` for full framework specifications and field-by-field research guidance.

## Research Data Points That Actually Matter

Not all data points are equal. Prioritize by predictive power for conversion.

### Tier 1 -- Deal Breakers (research these FIRST, stop if disqualifying)

| Data Point | Why It's Tier 1 | Where to Find It |
|---|---|---|
| Budget authority exists | No budget = no deal, regardless of fit | Job titles in org chart, recent spending signals |
| Active pain signal | Passive fit without active pain = 6-18 month cycle | Job postings, tech stack changes, leadership changes |
| No incumbent lock-in | Switching costs > your value = dead lead | Tech stack analysis, contract timing, integration depth |
| Company is operational | Layoffs, freezes, or restructuring = bad timing | News, LinkedIn headcount trends, Glassdoor |

### Tier 2 -- Qualification Depth (research after Tier 1 passes)

| Data Point | Signal Value |
|---|---|
| Tech stack overlap/gap | Shows integration feasibility and replacement opportunity |
| Hiring patterns in relevant roles | Indicates investment in the problem area you solve |
| Funding recency (< 18 months) | Budget availability and growth mandate |
| Leadership tenure (< 12 months in role) | New leaders buy tools to prove impact; established ones resist change |
| Competitor mentions in reviews/forums | Active evaluation or dissatisfaction with current solution |

### Tier 3 -- Enrichment (only after qualification confirmed)

Firmographics, org charts, social connections, content engagement, event attendance. These personalize outreach but do NOT predict conversion.

**NEVER research Tier 3 before confirming Tier 1.** This is the single most common time-wasting pattern in lead research.

## Intent Signal Detection

Intent signals separate "fits on paper" from "ready to buy." Weight these in scoring.

**Strong intent (add +3 to lead score):**
- Posted a job listing for the role your product replaces/augments (within last 90 days)
- Published content about the exact problem you solve (blog, podcast, conference talk)
- Evaluated a direct competitor within last 6 months (G2, Capterra reviews, community posts)
- Had a leadership change in the buying department (last 6 months)

**Moderate intent (add +1 to lead score):**
- Tech stack change in adjacent area (suggesting modernization wave)
- Increased hiring in the department your product serves
- Expansion into new market/geography (creates new operational needs)
- Recent funding round (creates spending mandate)

**Noise -- NOT intent (add +0):**
- Company matches your ICP on paper but shows zero behavioral signals
- Executive liked a LinkedIn post about your problem space
- Company is in a "hot" industry (this is firmographic, not intent)
- They use technology X that is tangentially related to your product

## Lead Scoring Method

Score every lead on a 1-10 scale using this formula:

```
Base Score (firmographic fit):     0-3 points
Qualification Depth (Tier 1+2):   0-4 points
Intent Signals:                    0-3 points
                                   ----------
Total:                             0-10 points
```

**Scoring thresholds for action:**
- 8-10: Immediate outreach -- research full Tier 3, draft personalized messaging
- 5-7: Nurture list -- worth monitoring, outreach if capacity allows
- 1-4: Discard or defer -- do not waste outreach resources

**NEVER inflate scores.** A lead that matches ICP perfectly but has zero intent signals is a 3, not an 8. Explain the score breakdown for every lead.

## Source Layering for Data Enrichment

Single-source research produces incomplete pictures. Layer sources for verification and depth.

**Layer 1 -- Public Web (free, start here):**
Company website, blog, press releases, job boards, LinkedIn company page, GitHub (if tech company), regulatory filings

**Layer 2 -- Aggregator Platforms (free tier or paid):**
Crunchbase, G2/Capterra reviews, Glassdoor, BuiltWith/Wappalyzer, SimilarWeb

**Layer 3 -- Deep Research (paid/specialized):**
ZoomInfo, Apollo, Clearbit, industry-specific databases, SEC filings, patent databases

**Verification rule:** Any data point used for scoring must be confirmed by 2+ sources OR flagged as "single-source -- verify before outreach."

See `references/data-enrichment-sources.md` for detailed source-by-source guidance and verification strategies.

## Context-Specific Research Approach

Different contexts demand different research methods. Use the right playbook.

| Context | Primary Research Focus | Key Differentiator |
|---|---|---|
| SaaS B2B (< $20K ACV) | Tech stack fit + pain signals from reviews | Speed matters more than depth -- qualify fast, outreach fast |
| Enterprise B2B (> $50K ACV) | Org mapping + decision process + budget cycle timing | Multi-threaded research across 3-5 stakeholders minimum |
| Professional Services | Trigger events + relationship proximity | Personal connections outweigh all other signals |
| SMB / Local | Online presence + growth indicators + owner accessibility | Owner IS the decision maker -- skip org mapping entirely |

See `references/industry-research-playbooks.md` for detailed playbooks per context.

## Anti-Patterns and Failure Modes

### Rationalization Table

| Rationalization | When It Appears | Why It's Wrong |
|---|---|---|
| "They're in the right industry so they're a lead" | Firmographic-only research | Industry match without pain signal or budget = 5% conversion |
| "I'll research everyone to the same depth" | Large list requests (20+ leads) | Tier 1 disqualifiers eliminate 40-60% -- check those first |
| "More leads is better" | User asks for "as many as possible" | 10 qualified leads > 50 unqualified. Push back on volume requests. |
| "Recent funding means they'll buy" | VC-backed companies | Funding creates budget but NOT need. Still need pain signal. |
| "The CTO is always the decision maker for tech" | Tech product lead research | CTO decides architecture. VP Eng decides tools. CFO approves budget. Map the actual process. |
| "Job title = buying authority" | Identifying decision makers | Titles vary wildly by company size. A "Director" at a 50-person company has CEO-level authority. A "Director" at Google has none. |

### NEVER List

- **NEVER** present leads without score breakdowns. A number without reasoning is useless.
- **NEVER** research Tier 3 data before confirming Tier 1 qualification. This wastes 70% of research time on leads that will be discarded.
- **NEVER** assume company size from employee count alone. 500 employees at a manufacturing company vs 500 at a SaaS company have wildly different budgets and buying processes.
- **NEVER** use "they could benefit from this" as a qualification signal. Every company "could" benefit. The question is whether they KNOW they have the pain and are DOING something about it.
- **NEVER** skip the incumbent check. If they already have a well-integrated competitor product, switching cost analysis must be part of the score.
- **NEVER** list a lead without specifying the actual decision maker role (not just "leadership team").
- **NEVER** present all leads as equally actionable. Scoring exists to force prioritization.

## Output Format

For each lead, present:

1. **Company + Score** (X/10 with breakdown: base/qualification/intent)
2. **Why Qualified** -- specific Tier 1 evidence (not firmographic generalities)
3. **Decision Maker** -- specific role title AND why that role (based on deal size + org structure)
4. **Active Pain Signal** -- the specific evidence of current need
5. **Recommended Approach** -- personalized angle based on their specific situation
6. **Risk Factors** -- what could disqualify this lead on deeper research

Group output by score tier (8-10 first, then 5-7). Do not present leads scoring 1-4 unless the user specifically requests a complete list.
