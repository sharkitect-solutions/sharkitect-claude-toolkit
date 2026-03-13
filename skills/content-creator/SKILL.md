---
name: content-creator
description: "Use when creating written content: blog posts, articles, case studies, whitepapers, social media posts, email copy, landing pages, or newsletters. Use when user asks to write, draft, create content, needs copywriting, or mentions content strategy. NEVER for code documentation, technical specs, or API docs -- those are developer-writing tasks, not content creation."
license: MIT
metadata:
  version: 2.0.0
  author: Alireza Rezvani (optimized)
  category: marketing
  domain: content-marketing
  updated: 2026-03-10
  python-tools: brand_voice_analyzer.py, seo_optimizer.py
  tech-stack: SEO, social-media-platforms
---

# Content Creator

Expert decision layer for producing content that engages, converts, and ranks. This skill exists because Claude's default content output is structurally correct but engagement-dead -- it follows templates without understanding WHY certain structures work for certain goals. The knowledge here closes that gap.

## The Content Type Decision Tree

Before writing a single word, match the request to the right content vehicle. Getting this wrong wastes the entire piece.

```
What is the PRIMARY goal?
|
+-- Educate/Inform
|   +-- Technical audience --> How-To Guide or Tutorial
|   +-- Business audience --> Whitepaper or Industry Report
|   +-- General audience --> Blog Post (explainer format)
|   +-- Quick consumption --> Listicle or Infographic script
|
+-- Persuade/Convert
|   +-- Top of funnel --> Blog Post (problem-aware)
|   +-- Middle of funnel --> Case Study or Comparison
|   +-- Bottom of funnel --> Landing Page or Sales Email
|   +-- Re-engagement --> Newsletter or Retargeting Email
|
+-- Build Authority
|   +-- Industry positioning --> Thought Leadership Article
|   +-- Social proof --> Case Study or Customer Story
|   +-- Community presence --> LinkedIn/Social Posts
|   +-- Media coverage --> Press Release
|
+-- Engage/Retain
|   +-- Community building --> Social Media Series
|   +-- Subscriber retention --> Email Newsletter
|   +-- Audience growth --> Platform-native content (Reels, Threads, Carousels)
```

**Why this matters:** A case study written when a how-to guide was needed fails regardless of writing quality. Content that underperforms most often does so because of format mismatch, not execution quality.

## Pre-Writing Workflow

Before drafting, chain these decisions in order. Skipping steps is the #1 cause of rewrites.

1. **Goal classification** -- Use the decision tree above. Lock the content type before anything else.
2. **Audience identification** -- Use the Audience-Tone Calibration table below. Identify formality, jargon level, proof type.
3. **Voice calibration** -- Consult `references/brand_guidelines.md` to set formality x energy x authority dimensions. If no brand guidance exists, use the inference heuristics.
4. **Research + angle finding** -- Follow the Research-to-Content Pipeline below. No angle = no piece. Stop here until the angle is clear.
5. **Structure selection** -- Consult `references/content_frameworks.md` for architecture decisions by content type. Select structure based on goal + audience, not habit.
6. **Hook selection** -- Use the Hook Patterns table below. Match the hook type to the content type and angle.
7. **Draft > Edit > Publish** -- Write to the outline. After editing, run the pre-publishing quality gate from `references/content_frameworks.md`.
8. **Distribution plan** -- Consult `references/social_media_optimization.md` for channel selection, cross-channel coordination, and repurposing schedule.

Each step narrows options for the next. By step 6, the hook practically writes itself because goal, audience, voice, angle, and structure are already locked.

## Hook Engineering

The first 50 words determine whether anyone reads the rest. Claude defaults to "In today's fast-paced world..." or "Have you ever wondered..." -- both are engagement killers. Use these patterns instead.

### Hook Patterns by Effectiveness

| Pattern | When to Use | Example |
|---------|------------|---------|
| **Contrarian Open** | Challenging industry assumptions | "Most SEO advice is backwards. Here's why keyword density stopped mattering in 2024." |
| **Specificity Hook** | Data-driven content | "We analyzed 2,847 blog posts. The ones that ranked had one thing in common -- and it's not what you think." |
| **Story Open** | Case studies, thought leadership | "Three months ago, our client was spending $40K/month on content that generated zero leads." |
| **Direct Problem** | How-to guides, tutorials | "Your landing page converts at 2%. Here's the structural flaw causing it." |
| **Before/After Gap** | Transformation content | "Companies using this framework went from 3% to 18% email open rates in 6 weeks." |

### Hook Anti-Patterns (NEVER use)

- "In today's [adjective] world..." -- Vacuous. Says nothing. Skip to the point.
- "Have you ever wondered..." -- Condescending. Assumes ignorance.
- "Content is king." -- Dead cliche. Signals lazy writing.
- "[Dictionary definition] According to Merriam-Webster..." -- Amateur hour.
- "In this article, we will..." -- Table of contents disguised as an intro. Delete it.

**Why these fail:** Each one signals to the reader that what follows is generic. Readers give you 8 seconds. Spend them on value, not throat-clearing.

## Content Architecture by Type

Different content types have different structural requirements. See `references/content_frameworks.md` for architecture selection decisions by content type. The execution-level decisions are here.

### Blog Posts (1,200-2,500 words)

**Structure:** Hook > Context (why now) > Core Value (3-5 sections) > Action Step > CTA

Critical decisions:
- **Length:** 1,500-2,000 words for ranking; under 1,200 only for news/announcements
- **Subheadings every 250-350 words** -- readers scan before committing to read
- **One idea per section.** If a section covers two concepts, split it. Sections trying to cover two things cover neither well.
- **Front-load value.** Put the best insight in the first third, not the conclusion. Readers who bounce at 40% should still get the main value.
- **CTA placement:** Primary CTA after value delivery (not at the very end). Secondary CTA at close.

### Case Studies

**Structure:** Result First > Challenge > Solution > Evidence > Takeaway

Critical decisions:
- **Lead with the number.** "43% reduction in churn" is the hook, not the company background.
- **Challenge section must include what they tried first and why it failed.** Without this, the case study reads like an ad.
- **Quantify everything.** "Improved efficiency" means nothing. "Cut processing time from 4 hours to 22 minutes" means everything.
- **Include timeline.** Results without timeline are unbelievable. "In 90 days" makes it real.

### Email Copy

**Structure:** Subject Line > Preview Text > Opening Line > Single Value Block > CTA

Critical decisions:
- **Subject line:** 30-50 characters. Test: would you open this from a stranger? If no, rewrite.
- **One CTA per email.** Multiple CTAs significantly reduce click-through rates (based on email marketing A/B test meta-analyses). Pick the one that matters.
- **Preview text must complement, not repeat, the subject line.** Together they form a two-part hook.
- **Mobile-first:** 67% of emails open on mobile. If the first 3 lines don't deliver value on a phone screen, the email fails.

### Social Media Posts

Platform-specific social media tactics live in the social-content skill. Distribution strategy in `references/social_media_optimization.md`. Expert decisions here:

- **LinkedIn:** First 2 lines are everything (preview cutoff). Never start with a hashtag. Optimal: personal story + business lesson + question.
- **Twitter/X:** One idea per tweet. Threads: promise the payoff in tweet 1, deliver it across 5-12 tweets, recap in final tweet.
- **Instagram:** First sentence = caption preview = your hook. Visual must stop the scroll; caption must hold the reader.

## The Research-to-Content Pipeline

Raw research does not become good content by summarizing it. The pipeline:

1. **Gather** -- Collect sources, data, quotes, examples
2. **Extract** -- Pull out the 3-5 insights that are genuinely surprising or non-obvious
3. **Angle** -- Find the ONE perspective that makes this piece different from everything else on the topic
4. **Outline** -- Structure around the angle, not around the research chronology
5. **Draft** -- Write to the outline; reference research to support claims, not to fill space
6. **Cut** -- Remove every sentence that doesn't serve the angle. If it's interesting but off-angle, save it for another piece.

**Why "angle" matters:** There are 7.5 million blog posts published every day. Content without a clear angle is invisible. The angle is the answer to: "Why should someone read THIS piece instead of the other 50 on this topic?"

## Audience-Tone Calibration

| Audience | Formality | Jargon Level | Proof Type | Sentence Length |
|----------|-----------|-------------|------------|-----------------|
| C-Suite | Professional | Industry-standard terms only | ROI, revenue, competitive advantage | 15-20 words avg |
| Practitioners | Conversational-professional | Technical terms OK with context | How-to, step-by-step, time savings | 12-18 words avg |
| General/Consumer | Conversational | Zero jargon | Stories, social proof, before/after | 10-15 words avg |
| Technical | Professional | Domain-specific expected | Benchmarks, specifications, code examples | 15-25 words avg |
| Social Media | Casual-conversational | Platform-native language | Screenshots, results, personal stories | 8-12 words avg |

**Calibration error to watch for:** Claude tends to write everything at "conversational-professional" regardless of audience. Force the adjustment. If writing for C-Suite, cut the friendliness. If writing for social, cut the formality.

## Rationalization Table

These are the shortcuts Claude will be tempted to take. Recognize them and refuse.

| Rationalization | When It Appears | Why It's Wrong |
|----------------|-----------------|----------------|
| "I'll add a compelling introduction later" | Drafting body first | The hook determines if anyone reads the body. Write it first, refine it last. |
| "This template structure is sufficient" | Following a generic format | Templates are starting points. Every piece needs structural decisions based on goal + audience + platform. |
| "More information is always better" | Padding word count | Length without density is punishment. Every paragraph must earn its space. |
| "The reader will understand the context" | Skipping the 'why now' framing | Content without urgency gets bookmarked and never read. |
| "I'll use a professional tone since I'm unsure" | Default tone selection | Wrong tone alienates the actual audience. Ask or infer from context clues. |
| "The CTA at the end is fine" | Putting CTA only at bottom | 60% of readers never reach the bottom. Place primary CTA after value delivery. |

## NEVER List

- **NEVER open with "In today's..." or "In the world of..."** -- These are content filler. Start with the value or the hook.
- **NEVER use more than one CTA in email copy.** Multiple CTAs = decision paralysis = no clicks.
- **NEVER write a case study that leads with company background.** Lead with the result. The background is supporting context.
- **NEVER pad content to hit a word count.** 800 focused words outperform 2,000 padded words on every metric.
- **NEVER skip the angle decision.** "Write about [topic]" without an angle produces commodity content indistinguishable from 50 other articles.
- **NEVER copy the brand voice from the last piece without checking.** Different content types within the same brand require tone adjustments. A social post is not a whitepaper.
- **NEVER publish without reading the piece aloud (or simulating it).** Awkward phrasing, run-on sentences, and rhythm problems are invisible in silent reading.
- **NEVER treat SEO and readability as separate concerns.** Google's helpful content update means reader engagement IS the ranking signal. Write for humans; structure for crawlers.

## Quality Signals: B+ Content vs. AI Slop

| Signal | AI Slop | B+ Content |
|--------|---------|------------|
| Opening | Generic ("In today's...") | Specific (data point, story, contrarian claim) |
| Structure | Template-following | Goal-driven architecture |
| Examples | Hypothetical ("Imagine a company...") | Specific ("When Stripe launched...") |
| Claims | Unsupported ("Studies show...") | Cited ("McKinsey's 2024 report found...") |
| Voice | Uniform corporate-pleasant | Calibrated to audience + platform |
| Transitions | "Furthermore," "Additionally," | Logical flow that doesn't need connective tissue |
| CTA | "Contact us today!" | Specific next action tied to content value |
| Length | Padded to target | Exactly as long as the value requires |

## SEO Integration (Not Separate From Writing)

SEO is not a post-writing optimization step. It is a pre-writing structural decision.

**Before writing:**
- Identify primary keyword (search intent must match content type)
- Identify 3-5 secondary keywords (natural variations, not forced synonyms)
- Check search intent: informational, navigational, commercial, or transactional
- Match content format to intent (informational = guide/explainer, commercial = comparison/review)

**During writing:**
- Primary keyword in title, H1, first 100 words, and 2-3 H2 subheadings
- Keyword density 1-3% -- if you have to force it, the keyword doesn't match the content
- Internal links to related content (2-3 minimum)
- External links to authoritative sources (1-2, builds trust with both readers and search engines)

**After writing:** Run `scripts/seo_optimizer.py` to verify structural compliance. Fix gaps before publishing.

For structural pre-publishing checks after SEO optimization, see the Pre-Publishing Quality Gate in `references/content_frameworks.md`.

## Tool Usage

- **`scripts/brand_voice_analyzer.py <file> [json|text]`** -- Analyze content for voice consistency. Use on first draft to check tone calibration against target audience.
- **`scripts/seo_optimizer.py <file> [keyword] [secondary,keywords]`** -- Analyze SEO structural compliance. Use after final draft, before publishing.
- **`references/brand_guidelines.md`** -- Voice calibration framework (formality x energy x authority), consistency tests, miscalibration fixes, platform adaptation rules, voice inference heuristics. Consult before any draft to lock voice dimensions.
- **`references/content_frameworks.md`** -- Content architecture decisions by type (blog, case study, whitepaper, email), repurposing strategy, pre-publishing quality gate. Consult to select structure, not for fill-in-the-blank templates.
- **`references/social_media_optimization.md`** -- Distribution channel selection, paid vs organic decisions, content lifecycle management, cross-channel coordination, performance benchmarks. Consult after drafting to plan distribution.
- **`assets/content_calendar_template.md`** -- Monthly planning template. Copy and customize per engagement.
