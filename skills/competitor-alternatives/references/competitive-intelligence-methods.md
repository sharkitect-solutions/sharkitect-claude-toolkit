# Competitive Intelligence Methods

## Win/Loss Analysis Deep Dive

### Interview Question Framework

Structure interviews in four phases. Each phase builds on the previous to avoid leading the respondent.

**Phase 1: Context (5 min)**
- "Walk me through what triggered your search for a new tool."
- "Who was involved in the evaluation? What were their roles?"
- "What was your timeline from first search to final decision?"

**Phase 2: Criteria Elicitation (10 min)**
- "Before we discuss any specific tools, what were your top 3 criteria for this decision?"
- "If you had to rank those criteria, what order would they fall in?"
- "Were there any must-haves that would immediately disqualify a tool?"
- "What would have been a deal-breaker?"

**Phase 3: Vendor Walkthrough (15 min)**
- "Which tools did you evaluate? Let's walk through each one."
- For each vendor: "What stood out positively? What concerned you?"
- "How did you compare pricing? What was the pricing model for each?"
- "Did you do a trial or demo? What was that experience like?"

**Phase 4: Decision Point (10 min)**
- "What was the single biggest factor in your final decision?"
- "Was there a specific moment where the decision crystallized?"
- "Looking back, is there anything you wish you had evaluated differently?"
- "What would the runner-up have needed to change to win?"

### Sample Size and Statistical Validity

| Sample Size | Confidence Level | Useful For |
|-------------|-----------------|------------|
| 5-10 | Anecdotal | Hypothesis generation, not decision-making |
| 10-20 | Directional | Identifying top 2-3 themes, trend spotting |
| 20-50 | Statistically useful | Reliable pattern identification, content creation |
| 50-100 | High confidence | Strategic positioning decisions, messaging pivots |
| 100+ | Diminishing returns | Academic research, enterprise-scale CI programs |

For comparison page content, target 20-30 interviews per major competitor. Below 20, your "patterns" may be noise. Above 50, each additional interview adds marginal insight relative to cost.

### Bias Mitigation

| Bias | How It Manifests | Countermeasure |
|------|-----------------|----------------|
| Confirmation bias | Interviewer probes deeper on answers that support existing beliefs | Use a standardized question set. Record interviews. Have a second analyst review notes. |
| Recency bias | Recent wins/losses weighted disproportionately | Maintain rolling 12-month dataset. Weight by recency but include older data. |
| Survivor bias | Only interviewing closed-won or closed-lost, missing abandoned evaluations | Include "no decision" outcomes in the sample. These reveal why buyers disengage. |
| Social desirability | Respondents give polished answers instead of honest ones | Anonymous surveys for sensitive questions (pricing sensitivity, budget). Verbal interviews for nuance. |
| Selection bias | Sales team nominates "good story" interviews | Random or systematic selection from CRM closed opportunities. Never let the account owner choose. |

---

## CI Tool Comparison

| Capability | Crayon | Klue | Manual Process |
|-----------|--------|------|----------------|
| Pricing page monitoring | Automated, daily | Automated, daily | Manual weekly checks |
| Battle card creation | Template-driven, auto-populated | AI-assisted, collaborative | Manual in Google Docs/Notion |
| Review mining | Aggregated from G2/Capterra | Aggregated with sentiment analysis | Manual reading, spreadsheet tracking |
| Win/loss integration | CRM connected (Salesforce, HubSpot) | CRM connected with auto-tagging | Manual CRM reports, export to spreadsheet |
| Cost | $20K-60K/year (depends on competitors tracked) | $25K-75K/year | 10-20 hours/week of analyst time |
| Best for | Marketing teams needing content fuel | Sales teams needing real-time battle cards | Early-stage companies with <5 competitors |

**When to invest in a CI platform:** When you track 10+ competitors, have a sales team of 20+, or publish comparison content monthly. Below these thresholds, manual processes with structured spreadsheets are more cost-effective.

---

## Review Mining Methodology

### G2, Capterra, TrustRadius Extraction

Mine reviews systematically, not anecdotally. The goal is quantified sentiment, not cherry-picked quotes.

**Process:**
1. Export all reviews for the competitor from the past 12 months (G2 and Capterra allow CSV export for buyers; TrustRadius requires manual collection).
2. Tag each review with sentiment per dimension: pricing, ease of use, support, features, reliability, integrations.
3. Calculate dimension-level satisfaction scores: (positive mentions / total mentions) per dimension.
4. Identify complaint clusters: group negative reviews by theme, rank by frequency.

**What to extract for comparison pages:**
- Top 3 praise themes (use these to acknowledge competitor strengths)
- Top 3 complaint themes (use these as "why people look for alternatives" content)
- Trend direction: is satisfaction improving or declining quarter-over-quarter?
- Notable quotes (attributed to role/company size, not name) for social proof sections

### Sentiment Scoring Table

| Dimension | Signal Phrases (Positive) | Signal Phrases (Negative) |
|-----------|--------------------------|---------------------------|
| Ease of use | "intuitive," "easy to learn," "simple setup" | "steep learning curve," "confusing UI," "hard to navigate" |
| Support | "responsive team," "helpful support," "quick resolution" | "slow response," "unhelpful," "canned responses," "no phone support" |
| Pricing | "fair pricing," "good value," "worth it" | "expensive," "price increases," "hidden fees," "nickel and dime" |
| Reliability | "always works," "reliable," "no downtime" | "buggy," "crashes," "slow performance," "downtime" |
| Features | "powerful," "feature-rich," "flexible" | "missing features," "limited," "basic," "half-baked" |

---

## Battle Card Design Principles

Battle cards are internal documents used by sales teams during competitive deals. They differ from public comparison pages in structure and tone.

### Battle Card Structure

| Section | Purpose | Length |
|---------|---------|--------|
| Quick kill summary | One-line positioning against this competitor | 1 sentence |
| Landmines | Questions to plant that expose competitor weakness | 3-5 questions |
| Trap handling | Responses when prospect raises competitor strengths | 3-5 scenarios |
| Pricing counter | How to reframe when competitor is cheaper/different pricing model | 2-3 talking points |
| Migration pitch | How to reduce perceived switching cost | 3-4 proof points |
| Customer evidence | Quotes from customers who switched from this competitor | 2-3 quotes |

### Landmine Questions (Expert Technique)

Landmine questions are designed to make the prospect ask the competitor a question that exposes a weakness -- without you ever saying anything negative directly.

**Formula:** "When you evaluate [Competitor], you might want to ask them about [specific capability that is their weakness]."

The prospect asks the question. The competitor stumbles. You never made a negative claim. This technique is both more effective and more legally safe than direct negative statements.

### Battle Card Freshness Protocol

| Trigger | Action | Owner |
|---------|--------|-------|
| Competitor pricing change | Update pricing counter section within 48 hours | Product marketing |
| Competitor product launch | Update quick kill + landmines within 1 week | Product marketing |
| Lost deal to this competitor | Add loss reason to trap handling section | Sales enablement |
| Quarterly review | Full battle card audit against current competitor state | CI analyst |
