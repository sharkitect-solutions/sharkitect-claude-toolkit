# Reverse Engineering Analysis Framework

## 5-Phase Analysis Process

### Phase 1: Input Assessment
- What type of input do we have? (video, demo, tutorial, article, code, reviews)
- What is the baseline confidence level for this input type?
- What specific questions are we trying to answer?
- What would success look like for this analysis?

### Phase 2: Surface-Level Extraction
Extract everything directly stated or visible:
- Technologies mentioned by name
- Features demonstrated or described
- Integrations shown or referenced
- Architecture terms used
- Numbers cited (users, revenue, team size, timeline)
- Tools and platforms visible in UI or mentioned

Tag each item with source and initial confidence level.

### Phase 3: Deep Inference
For each surface-level finding, apply inference layers:

**Architecture Inference:**
- UI patterns suggest what framework? (React patterns differ from Vue differ from server-rendered)
- Response times suggest what backend architecture? (instant = cached/CDN, <100ms = read replica, >500ms = real-time computation)
- Feature set suggests what database model? (search = vector/elastic, real-time = websockets/events, multi-tenant = RLS/schema separation)

**Business Model Inference:**
- Pricing structure suggests what cost model? (per-seat = low marginal cost, usage-based = variable infrastructure)
- Feature gates suggest what conversion strategy? (freemium = volume play, demo-only = high-touch sales)
- Integration list suggests what ecosystem play? (many integrations = platform, few integrations = focused tool)

**Scale Inference:**
- Team size suggests what architecture complexity? (<10 = monolith, 10-50 = modular monolith, 50+ = microservices likely)
- Funding suggests what growth stage? (bootstrapped = lean stack, Series B+ = may be over-engineered)

### Phase 4: Cross-Reference Validation
For each inference, seek corroborating evidence:
- Search for technical blog posts from the company's engineering team
- Check job postings for technology mentions (hiring for Kubernetes = using Kubernetes)
- Scrape their website for technology signatures (via Firecrawl or Wappalyzer signals)
- Check GitHub for open-source contributions or public repos
- Look for conference talks or podcast appearances by founders/engineers

Each corroborating source increases confidence by 10-15%.

### Phase 5: Report Generation
Produce a structured intelligence report using the template in `intelligence-template.md`.
Route according to `downstream-routing.md`.

## Analysis Depth Tiers

| Tier | Time Budget | When to Use | Output |
|------|-------------|------------|--------|
| **Quick Scan** | 30 min | General curiosity, initial assessment | Bullet list with confidence tags |
| **Standard Analysis** | 1-2 hours | Informing a build decision, competitive positioning | Full intelligence report |
| **Deep Dive** | 3-5 hours | Replicating or competing directly, architecture decisions | Full report + architecture diagram + gap analysis |

## What Reverse Engineering Can and Cannot Reveal

**Can reveal (with varying confidence):**
- General architecture patterns
- Technology stack components (frameworks, databases, hosting)
- Feature scope and capabilities
- Business model structure
- Scale indicators
- Integration ecosystem

**Cannot reliably reveal:**
- Exact implementation details (unless code is available)
- Internal team structure or processes
- Exact costs or margins
- Custom algorithms or proprietary logic
- Security implementation details
- Data models or schema design

## Cross-Domain Intelligence Methodologies

### Analysis of Competing Hypotheses (ACH) — Richards Heuer, CIA

When multiple architecture interpretations are plausible, gut instinct picks the "most likely" and ignores alternatives. ACH forces structured elimination instead:

1. **List hypotheses** — Write down every plausible architecture interpretation (e.g., "they use serverless," "they run Kubernetes," "they use a PaaS like Railway").
2. **List evidence** — Catalog every piece of evidence collected across all phases (job postings, response times, UI behavior, tech blog posts, error messages).
3. **Build a consistency matrix** — For each hypothesis, mark each piece of evidence as Consistent (C), Inconsistent (I), or Neutral (N).
4. **Eliminate by inconsistency** — Discard hypotheses contradicted by the most reliable evidence. The surviving hypothesis with the fewest inconsistencies wins — not the one with the most confirming evidence.

**Why this matters for RE:** Confirmation bias causes analysts to favor the first architecture they infer. ACH counteracts this by making you evaluate all hypotheses against ALL evidence equally. Use ACH whenever Phase 3 (Deep Inference) produces 3+ competing interpretations.

### Admiralty Code (NATO Source/Information Grading)

The current confidence system (CONFIRMED through SPECULATIVE) grades findings but not sources. The Admiralty Code adds a 2-axis matrix that grades BOTH independently:

**Source Reliability:**
| Grade | Meaning | RE Example |
|-------|---------|------------|
| A | Completely reliable | Official documentation, public API specs |
| B | Usually reliable | Engineering blog posts, job postings from the company |
| C | Fairly reliable | YouTube tutorials by known practitioners, conference talks |
| D | Not usually reliable | Competitor marketing materials, sales demos |
| E | Unreliable | Anonymous forum posts, unverified rumors |
| F | Cannot be judged | New source with no track record |

**Information Credibility:**
| Grade | Meaning | RE Example |
|-------|---------|------------|
| 1 | Confirmed by other sources | Multiple independent sources agree |
| 2 | Probably true | Consistent with known patterns, one strong source |
| 3 | Possibly true | Reasonable but unverified |
| 4 | Doubtful | Conflicts with other evidence |
| 5 | Improbable | Contradicts multiple reliable sources |
| 6 | Cannot be judged | Insufficient basis for evaluation |

Tag high-stakes findings with Admiralty grades (e.g., "B2" for a job posting corroborated by a tech blog) alongside the existing confidence percentage. This is especially useful when the same finding appears in sources of varying quality.

### OSINT Intelligence Cycle

Professional intelligence work follows a 5-phase cycle. Map it to the RE workflow:

| OSINT Phase | RE Equivalent | Key Activity |
|-------------|---------------|-------------|
| **Direction** | Phase 1: Input Assessment | Define the question: what exactly are we trying to learn? Scope the collection plan. |
| **Collection** | Phase 2: Surface-Level Extraction | Gather raw data: scrape sites, watch videos, read docs, pull job postings. No analysis yet. |
| **Processing** | Phase 3: Deep Inference | Transform raw data into usable intelligence: tag confidence, categorize by architecture layer, normalize terminology. |
| **Analysis** | Phase 4: Cross-Reference Validation | Apply ACH, Admiralty grading, pattern matching. Synthesize processed data into assessed findings. |
| **Dissemination** | Phase 5: Report Generation | Produce the intelligence report, route via downstream-routing.md, brief the stakeholder. |

**Cycle, not line:** If Analysis reveals gaps, loop back to Collection. If new Direction emerges from findings, restart. Expect 1.5-2 passes through the cycle for Standard Analysis depth, 2-3 for Deep Dive.
