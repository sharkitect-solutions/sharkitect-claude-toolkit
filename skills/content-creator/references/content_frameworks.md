# Content Architecture Decisions

Expert decision layer for selecting and structuring content formats. Templates are scaffolding -- the decisions below determine whether the scaffolding produces a building or a pile of sticks.

## Blog Post Architecture Selection

```
Which blog structure fits this piece?
|
+-- Reader needs to DO something --> How-To Guide
|   Best when: clear process, sequential steps, measurable outcome
|   Fails when: topic is conceptual or opinion-based
|
+-- Reader needs a quick scan of options --> Listicle
|   Best when: comparing tools, tips, or tactics (5-15 items)
|   Fails when: items need deep explanation (>300 words each = use guide instead)
|
+-- Reader needs to understand a concept --> Explainer/Narrative
|   Best when: abstract topic, needs context and "why" framing
|   Fails when: reader already understands and wants actionable steps
|
+-- Reader is evaluating options --> Comparison/Versus
|   Best when: 2-4 options, clear evaluation criteria exist
|   Fails when: one option is objectively better (write a recommendation instead)
|
+-- Reader needs proof something works --> Case Study (see next section)
```

**Length by intent:**
- News/announcement: 400-800 words (deliver and get out)
- Standard value post: 1,200-1,800 words (ranking sweet spot)
- Comprehensive guide: 2,500-4,000 words (only when depth earns it)
- Pillar/cornerstone: 4,000+ words (only for topics you want to own in search)

**Structure rule:** If a blog post covers more than 3 major ideas, it is probably 2-3 posts forced into one. Split it. Each post can link to the others and you get more surface area.

## Case Study Architecture Selection

```
What is the primary reader motivation?
|
+-- "Prove it works" (skeptical buyer) --> Result-First Structure
|   Lead: headline metric. Then: challenge > solution > evidence.
|   Works because skeptics need the payoff before they invest attention.
|
+-- "Show me how" (curious practitioner) --> Narrative Journey
|   Lead: the problem situation. Then: attempts > turning point > solution > result.
|   Works because practitioners want to follow the problem-solving process.
|
+-- "Is this my problem?" (problem-aware, solution-unaware) --> Problem-Focused
|   Lead: the pain in vivid detail. Then: what made it hard > solution > outcome.
|   Works because the reader must see themselves in the problem first.
```

**Non-negotiable case study elements:**
- At least one quantified result with timeline (e.g., "43% reduction in 90 days")
- What the client tried before and why it failed (without this, it reads like an ad)
- A specific detail that makes the story feel real (a quote, a moment, a decision point)

## Whitepaper and Report Architecture

**Gated vs. ungated decision:**
- Gate it when: content is 3,000+ words, contains original research/data, audience is mid-funnel
- Leave it ungated when: content is thought leadership for brand awareness, audience is top-funnel, SEO value outweighs lead capture
- Hybrid approach: ungate the executive summary + key findings, gate the full report

**Length by audience:**
- C-Suite: 6-10 pages max. Executive summary on page 1. They will not read 30 pages.
- Practitioners: 15-25 pages. They want depth and methodology.
- Technical: Length is less important than completeness. Include appendices for deep data.

**Structure rule:** Every whitepaper needs a "So what?" section within the first 2 pages. If the reader cannot articulate what they will gain by page 2, they will close it.

## Content Repurposing Architecture

One pillar piece becomes 8-15 derivative pieces. The expert decisions are WHICH derivatives and in WHAT order.

**From a 2,000-word blog post:**
1. LinkedIn post: extract the single most contrarian insight + personal framing (publish same day)
2. Twitter/X thread: the core argument in 5-8 tweets with the best data points (day 2)
3. Email newsletter feature: summary + the one takeaway subscribers should act on (next send)
4. Instagram carousel: 5-7 slides covering the key framework or steps (day 3-4)
5. Short-form video: 60-second explanation of the main concept (week 1)
6. Quote graphics: 2-3 pull quotes for social scheduling (drip over 2 weeks)
7. Follow-up post: deeper dive on the point that got the most engagement (week 2-3)

**Repurposing decision rules:**
- Repurpose the ANGLE, not the text. Each platform needs native formatting.
- Prioritize platforms where your audience already engages. Not all 7 derivatives are worth creating for every brand.
- The pillar piece must be strong before repurposing. Spreading weak content across platforms multiplies the weakness.
- Time the derivatives: same-day for the first social push, then stagger over 2-3 weeks to extend the content lifecycle.

## Email Content Architecture

Brief because the email-sequence skill handles multi-email campaigns. This covers single-piece email decisions.

**Newsletter vs. promotional vs. nurture:**
- Newsletter: regular cadence, value-first, builds relationship. Reader expectation = "teach me something."
- Promotional: event-driven, offer-focused, clear deadline. Reader expectation = "sell me something."
- Nurture: behavior-triggered, personalized, progressive. Reader expectation = "help me decide."

**Key structural decision:** Newsletters with ONE focused topic outperform multi-topic roundups. If you must do a roundup, put the strongest item first and limit to 3 items. Four or more items = decision paralysis = nothing gets clicked.

## Pre-Publishing Quality Gate

Before any content ships, verify these five items in order:

1. **Angle test:** Can you state the piece's unique angle in one sentence? If not, the piece lacks focus.
2. **Hook test:** Read only the first 50 words. Would you keep reading if you found this in your feed? If not, rewrite the hook.
3. **Scan test:** Read only the headings. Do they tell a coherent story on their own? If not, restructure.
4. **Value test:** What specific thing can the reader DO after reading this that they could not do before? If the answer is vague, add actionable content.
5. **CTA test:** Is there exactly one primary call-to-action placed after the main value delivery? If it is only at the bottom, move it up.
