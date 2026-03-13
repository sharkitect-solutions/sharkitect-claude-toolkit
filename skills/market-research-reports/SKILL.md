---
name: market-research-reports
description: "Use when producing market research analysis, market sizing, competitive landscape reports, or investment-grade market assessments. NEVER for product-level competitive feature comparisons, financial modeling/DCF, or general business writing that does not require market data analysis."
---

# Market Research Reports

## Research Scoping Decision Tree

Before any research begins, classify the request. Each type demands a completely different methodology, data strategy, and output structure.

```
What is the research question?
|
|-- "How big is this market?"
|   --> MARKET SIZING
|   Data needs: industry reports, company revenues, unit economics
|   Methodology: triangulated top-down + bottom-up
|   Output: TAM/SAM/SOM with assumption tables, not single numbers
|
|-- "Who competes here and how?"
|   --> COMPETITIVE LANDSCAPE
|   Data needs: financials, patent filings, job postings, M&A history
|   Methodology: strategic intent analysis, not feature matrices
|   Output: positioning map with cost structure and strategic trajectory
|
|-- "Should we enter this market?"
|   --> MARKET ENTRY ASSESSMENT
|   Data needs: barrier analysis, incumbent response patterns, unit economics
|   Methodology: entry barrier quantification + beachhead identification
|   Output: go/no-go framework with specific entry wedge recommendation
|
|-- "Is this worth investing in?"
|   --> INVESTMENT THESIS
|   Data needs: growth drivers, risk factors, comparable transactions
|   Methodology: scenario-weighted returns with sensitivity analysis
|   Output: thesis with bull/base/bear cases and key assumption tests
|
|-- "What trends matter for our strategy?"
|   --> TREND ANALYSIS
|   Data needs: patent velocity, funding flows, adoption curves, policy signals
|   Methodology: signal separation (noise vs trend vs structural shift)
|   Output: trend impact matrix with timing estimates and confidence levels
```

## The 5 Market Sizing Mistakes That Produce Garbage Numbers

| Mistake | What happens | How to catch it | What to do instead |
|---------|-------------|-----------------|-------------------|
| Top-down fantasy | Start with global GDP, multiply by "% that is addressable" to get a huge number that means nothing | Ask: "Can you name 10 companies whose combined revenue equals this TAM?" If no, the number is fiction | Build bottom-up from actual unit economics: customers x price x frequency. Then sanity-check against top-down |
| Bottom-up without unit economics | Count potential users without modeling what they would actually pay | The resulting number sounds impressive but has no purchasing evidence behind it | Validate willingness-to-pay with comparable products, published pricing, or analyst estimates of average deal sizes |
| TAM/SAM/SOM confusion | Present TAM as if it were capturable revenue. A $50B TAM means nothing if your SOM is $50M | SOM should be <5% of SAM for a new entrant. If SOM > 10% of TAM, the analysis is self-deceptive | Calculate SOM from realistic market share capture rates for companies at comparable stage and positioning |
| Ignoring market maturity | Apply growth-stage CAGR to a market that is actually consolidating or commoditizing | Check: is the number of competitors increasing or decreasing? Are margins expanding or compressing? | Map the market lifecycle stage (emerging/growth/mature/decline) and use stage-appropriate growth assumptions |
| Confusing addressable with obtainable | Treat geographic or segment restrictions as the only filter between TAM and SAM | SAM should also account for: product fit constraints, channel access limits, regulatory barriers, and competitive lockout | Apply at least 4 constraint filters: geography, product fit, channel access, and competitive displacement difficulty |

### Before/After: Market Sizing

**Bad (typical):**
"The global AI market is projected to reach $1.8 trillion by 2030 (Grand View Research). With our unique approach to enterprise AI, we can capture 2% of this market, representing a $36 billion opportunity."

Problems: uses broadest possible market definition, applies arbitrary share capture to TAM (not SAM), cites a single source with no methodology transparency, provides no unit economics, and the "unique approach" claim is unsupported.

**Expert approach:**
"We size the market from both directions and triangulate. Bottom-up: 14,000 enterprises in our target segments (manufacturing, logistics, retail with >$500M revenue) spend an average of $2.1M/year on predictive analytics tools (based on Gartner's 2024 enterprise software survey). That yields a SAM of $29.4B. Top-down cross-check: IDC sizes the broader enterprise AI market at $180B, of which predictive analytics is roughly 18% ($32.4B) -- consistent within 10% of our bottom-up figure. Our SOM assumes 1.5% penetration over 5 years based on the typical capture rate of Series B-stage vertical SaaS companies entering established markets (Bessemer data), yielding ~$440M in year-5 revenue. Key assumption to stress-test: the $2.1M average spend figure. If actual spend is 30% lower, SOM drops to $310M."

Why this is better: triangulated methodology, named data sources with dates, realistic SOM derived from comparable companies, explicit assumption sensitivity, and the final number is useful for decision-making.

## Data Source Quality Assessment

Not all data is created equal. Evaluate every source before using it.

**Tier 1 - Primary / High confidence:**
- Company SEC filings (10-K, 10-Q) for revenue data
- Government statistical agencies (BLS, Census, Eurostat)
- Patent office databases for technology trajectory
- Job posting analysis for strategic intent signals
- Published pricing pages for competitive intelligence

**Tier 2 - Analyst reports / Medium confidence:**
- Gartner, Forrester, IDC market sizing -- useful as one input but treat with skepticism. These reports are often funded by vendors with an interest in inflating market size
- McKinsey, BCG, Bain published research -- high quality but typically 12-18 months stale by publication
- Industry association data -- generally reliable for member counts and aggregate revenue, but biased toward larger members

**Tier 3 - Use carefully / Verify independently:**
- Vendor-commissioned research (always inflates the market the vendor serves)
- Press releases announcing market size (check who funded the study)
- LinkedIn/social posts citing "trillion dollar markets" (usually citing Tier 3 sources)
- Older reports (>2 years) applied to fast-moving markets

**Red flags that a market size number is inflated:**
- The source is a company that sells into that market
- Round numbers with no methodology disclosure
- "Projected" market sizes >5 years out with >20% CAGR (compounding optimism)
- The same number appears in dozens of articles but traces back to one unverifiable source
- TAM includes adjacent segments that would require fundamentally different products

## Competitive Analysis Beyond Feature Matrices

Feature comparison tables are the lowest form of competitive analysis. They tell you what exists today but nothing about where competitors are going or why they will win or lose. Go deeper.

**Strategic intent analysis:**
- What do their job postings reveal? Hiring 50 ML engineers means a different future than hiring 50 sales reps
- What do their patent filings indicate about R&D direction?
- What do their acquisition patterns show? Three acqui-hires in data infrastructure signals platform ambitions
- What are their executives saying in earnings calls vs what their product roadmap shows?

**Cost structure analysis:**
- Gross margins reveal whether competitors can sustain pricing pressure
- A competitor with 80% gross margin can afford a price war that would bankrupt a 40% margin competitor
- Headcount per revenue dollar indicates operational efficiency and scaling model
- Infrastructure choices (cloud vs owned) predict cost trajectory

**Talent flow analysis:**
- Where are people leaving from and going to? Net talent flow between competitors reveals who is gaining momentum
- What seniority level is moving? Senior engineers leaving signals internal problems before they appear in financials

**Acquisition pattern analysis:**
- What types of companies are they buying? Technology tuck-ins vs market share consolidation vs geographic expansion tell different strategic stories
- How much are they paying (multiples)? Overpaying signals desperation or deep conviction
- Post-acquisition integration success rate (check if acquired products still exist 2 years later)

## Framework Selection Guide

Frameworks are tools, not rituals. Using the wrong one wastes pages and credibility.

| Framework | When it actually helps | When it is theater | Use instead |
|-----------|----------------------|-------------------|-------------|
| Porter's Five Forces | Mature, stable industries with clear boundaries (manufacturing, mining, utilities) | Digital markets where barriers to entry are low and value chains are collapsing | Direct analysis of switching costs, network effects, and regulatory moats -- the three things that actually create durable advantage in digital markets |
| PESTLE | Entering a new geography or evaluating regulatory risk across jurisdictions | Domestic market analysis where political/legal factors are stable and well-understood | Focus only on the 1-2 PESTLE dimensions that actually affect the specific decision being made |
| SWOT | Quick internal alignment exercise to surface disagreements among stakeholders | Formal deliverables. SWOT in a report is almost always superficial because it requires insider knowledge the analyst rarely has | If you must use SWOT, make every entry evidence-backed with a specific data point. "Strong brand" is useless. "Brand awareness at 73% in target segment (Nielsen 2024)" is useful |
| BCG Matrix | Portfolio decisions for multi-business companies with shared resources | Single-product companies or startups. You need an actual portfolio for this to mean anything | Customer segment attractiveness matrix using quantified criteria (segment size, growth, margin, competitive intensity) |
| TAM/SAM/SOM | When you need to quantify opportunity size for investment or resource allocation decisions | When used as a headline slide to impress rather than inform. The most common abuse in pitch decks | Always present with methodology, assumption table, and sensitivity analysis. A single TAM number without these is useless |
| Value Chain | Understanding where margin pools exist and where value is being captured/created | When applied generically without industry-specific cost data. A value chain without numbers is just a flowchart | Quantify each step: cost structure, margin %, who captures value. The insight is in the numbers, not the boxes |

## The Insight vs Information Problem

The most common failure in market research: reports full of data but empty of implications. Every section must answer "so what?" before moving to the next topic.

**Information (low value):** "The market grew 12% last year."

**Insight (high value):** "The market grew 12% last year, but growth was concentrated in the enterprise segment (23%) while SMB contracted (-4%). This divergence means a strategy targeting SMB must compete on displacement, not market expansion -- a fundamentally harder sale requiring different positioning and longer cycles."

**Test every finding:** Can someone make a different decision based on this statement? If the answer is no, it is information, not insight. Cut it or add the "so what."

## Making Recommendations Actionable

Most research recommendations fail three tests. Apply all three before including any recommendation.

**The specificity test:** Can someone start executing this recommendation on Monday morning without asking follow-up questions? "Expand into Asia-Pacific" fails. "Establish a sales office in Singapore targeting financial services companies with >$1B AUM, partnering with a local systems integrator for the first 6 deals" passes.

**The resource test:** Does the recommendation acknowledge what it costs (money, people, time, opportunity cost)? If not, it is a wish, not a recommendation. Every recommendation needs: estimated investment, timeline to first results, and what you must stop doing to free resources.

**The timeline test:** Does the recommendation have a clear "by when" and "measure of success"? "Increase market share" is a direction, not a recommendation. "Achieve 3% market share in the mid-market segment within 18 months, measured by quarterly revenue tracking against the $4.2B SAM" is actionable.

## Presenting Uncertainty Honestly

Pretending to know the future with precision destroys credibility. Expert research acknowledges uncertainty while still being useful.

**Use scenario analysis, not point estimates:**
- Bull case: what happens if key growth drivers accelerate (and why they might)
- Base case: trend continuation with realistic friction
- Bear case: what breaks the thesis (specific risks, not vague "macro headwinds")

**State assumption sensitivity:** "Our base case revenue projection of $340M in Year 5 is most sensitive to two assumptions: (1) average deal size -- a 20% reduction drops the projection to $270M, and (2) sales cycle length -- if cycles extend from 6 to 9 months, projection drops to $285M."

**Use confidence tiers:**
- High confidence (multiple corroborating sources, historical precedent): present as findings
- Medium confidence (limited sources, reasonable extrapolation): present as estimates with ranges
- Low confidence (single source, speculative): present as scenarios with explicit caveats

## NEVER List

1. NEVER present a single TAM number without methodology, sources, and assumption sensitivity
2. NEVER use a framework just to fill pages -- every framework must produce a specific insight that changes a recommendation
3. NEVER cite market size figures from vendor-funded research without flagging the conflict of interest
4. NEVER present competitive analysis as a feature matrix -- analyze strategic intent, cost structure, and trajectory
5. NEVER make a recommendation that fails the specificity, resource, or timeline test
6. NEVER extrapolate growth rates beyond 5 years without scenario analysis -- compounding errors make longer projections meaningless
7. NEVER present information without the "so what" -- every data point must connect to a decision or insight
8. NEVER treat all data sources as equally reliable -- tier your sources and flag confidence levels
9. NEVER write a 50-page report when a 10-page report with sharper insights would serve the reader better -- length is not a proxy for quality
10. NEVER use "the market is expected to grow" as a reason to enter -- every market is growing; the question is whether you can capture share profitably

## Rationalization Table

When you are tempted to take a shortcut, check this table first.

| What you want to do | Why it feels right | Why it produces bad research | Do this instead |
|---------------------|-------------------|------------------------------|-----------------|
| Use one big TAM number from a headline report | It is fast and the source is reputable | Single-source market sizing is unreliable. Analyst reports disagree by 30-50% on the same market | Triangulate: one top-down, one bottom-up, check they converge within 20% |
| Copy a Porter's Five Forces from a textbook example | The framework is well-known and looks professional | Generic application without industry-specific data produces generic conclusions | Only use Porter's if barriers to entry are the key strategic question. Otherwise, analyze the actual competitive dynamics directly |
| Project growth by extending the historical CAGR | It is simple and defensible ("the data says...") | Past growth rate includes conditions (funding booms, regulatory tailwinds, COVID effects) that may not repeat | Model growth from demand drivers. What specifically causes purchases? Are those drivers accelerating or decelerating? |
| List all competitors equally in a comparison table | It is thorough and nobody can say you missed someone | Treating a $50B incumbent and a $5M startup as equivalent competitors misleads the reader | Tier competitors by strategic relevance. Focus analysis on the 3-4 that actually affect your decision |
| Make the report longer to seem more comprehensive | More pages feel more valuable | Readers skim long reports and miss the key insights. Padding dilutes signal-to-noise | Front-load insights in a 2-page executive summary. Make every subsequent page earn its place |
| Present only the base case projection | Multiple scenarios feel wishy-washy or uncommitted | Single-scenario projections are almost always wrong. The question is which direction | Always present bull/base/bear with explicit assumptions for each. This is more useful, not less decisive |
| Skip the "limitations" section | It feels like undermining your own work | Hiding limitations does not make them go away. Sophisticated readers notice omissions and lose trust | State limitations clearly. It builds credibility and helps the reader weight your findings appropriately |

## LaTeX Assets

This skill includes professional LaTeX assets in `assets/`:
- `market_research.sty` -- consulting-firm style package with box environments, color palette, and custom commands
- `market_report_template.tex` -- complete report template structured for comprehensive market analysis

Use these when the deliverable format is LaTeX/PDF. The style package provides `keyinsightbox`, `marketdatabox`, `riskbox`, `recommendationbox`, and other environments for professional formatting.
