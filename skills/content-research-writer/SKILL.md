---
name: content-research-writer
description: "Use when writing research-backed articles, blog posts, newsletters, or long-form content requiring source discovery, citation management, and iterative section-by-section refinement. Also use when the user mentions content research, article writing with citations, writing partner, or collaborative drafting. NEVER use for quick social media posts (use social-content), email copy (use email-composer), copy editing of existing text (use copy-editing), or copywriting from scratch without research needs (use copywriting)."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Content Research Writer

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Research-to-draft procedure, source credibility, research depth calibration, section feedback, citation management, hook improvement, pre-publish checklist | Always (auto-loaded) |
| source-verification-methods.md | Study methodology assessment, pre-registration checks, retraction/correction verification, statistical literacy for writers, press release vs research paper distortions, fact-checking procedure, disappeared source recovery | When evaluating source quality beyond the basic tier, fact-checking specific claims, assessing study methodology, or verifying statistics |
| long-form-structure-patterns.md | Argument architecture selection (6 patterns), information density calibration by audience, counterargument integration patterns, section transition engineering, multi-article series architecture, reader fatigue management | When structuring content longer than 2,000 words, building multi-section arguments, managing competing evidence, or diagnosing structural problems in drafts |
| editorial-quality-control.md | Research rabbit hole timeboxing, fact-checking tiers (4 levels), accuracy under deadline tradeoffs, hedge language calibration, voice consistency audit (5 markers), named editorial failures (7), correction/update protocol | When establishing review processes, managing research scope, handling accuracy-under-deadline tradeoffs, auditing voice consistency, or dealing with corrections |

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| Research-backed articles, blog posts, newsletters, long-form content | YES | -- |
| Collaborative writing with source discovery and citation management | YES | -- |
| Section-by-section feedback and iterative refinement | YES | -- |
| Quick social media posts (no research depth needed) | NO | social-content |
| Email copy (different structure and objectives) | NO | email-composer |
| Copy editing existing text (editing, not writing) | NO | copy-editing |
| Copywriting from scratch without research needs | NO | copywriting |
| SEO keyword strategy and technical SEO | NO | seo-optimizer |

## Assessment Procedure

Before starting any research-writing project, work through this sequence. Skipping steps leads to research rabbit holes or structural rewrites.

1. **Classify the content type** using the Research Depth Calibration table below. A blog post and a thought leadership piece require fundamentally different research investment -- misclassifying wastes hours or produces under-researched content.
2. **Confirm the thesis or argument.** If the author can't state their main point in one sentence, the piece isn't ready to research. Help them articulate it before searching for sources.
3. **Assess source availability.** Quick search: are there credible sources for this topic? If the topic has minimal published research, adjust expectations -- the piece may need to rely on expert interviews or primary data collection rather than citation-heavy evidence.
4. **Determine the author's voice.** Read 2-3 existing pieces by the author (or ask for samples). The goal is to enhance their voice, not replace it. Note: sentence length patterns, formality level, use of contractions, how they handle technical terms.
5. **Build the outline before researching.** The outline determines what research is needed. Researching before outlining leads to the rabbit hole -- you'll find interesting sources that don't serve the piece.
6. **Set the research timebox.** Based on content type classification. When the timebox expires, start writing with what you have. Load `editorial-quality-control.md` for timeboxing guidance.

## Research-to-Draft Procedure

1. **Scope the project**: Confirm topic, thesis/argument, target audience, desired length, content type (blog, newsletter, tutorial, thought leadership, case study), and available sources.
2. **Build the outline**: Structure with hook, introduction (context + problem + scope), 3-5 main sections with key points and evidence needs, conclusion with CTA. Mark sections needing research with `[RESEARCH: specific question]`.
3. **Conduct research**: Search for credible sources matching each `[RESEARCH]` tag. Extract key facts, data points, and quotable insights. Record full citations immediately -- never defer citation tracking.
4. **Draft iteratively**: Write one section at a time. After each section, review for clarity, flow, evidence, and voice consistency before moving to the next. This catches structural issues early instead of requiring full-draft rewrites.
5. **Polish and validate**: Full-draft review for flow across sections, citation completeness, and voice consistency. Run the Pre-Publish Checklist.

## Source Credibility Hierarchy

Evaluate every source before citing. Higher-tier sources require less corroboration.

| Tier | Source Type | Examples | Corroboration Needed |
|---|---|---|---|
| 1 (Gold) | Peer-reviewed research, official statistics, primary data | Academic journals, government census data, SEC filings, peer-reviewed meta-analyses | None -- cite directly |
| 2 (Silver) | Reputable industry research, established publications | McKinsey/Gartner reports, Harvard Business Review, established trade publications | One corroborating source preferred |
| 3 (Bronze) | Expert opinion, company-published data | Blog posts by recognized experts, company case studies, conference talks | Two corroborating sources or explicit attribution ("according to...") |
| 4 (Use cautiously) | Aggregated/secondary data, social proof | Wikipedia (follow to primary source), social media posts, forum discussions | Must trace to primary source before citing |
| 5 (Avoid) | Unattributed claims, outdated data, content mills | "Studies show..." with no citation, data older than 3 years for fast-moving topics, SEO content farms | Do not cite -- find the primary source or drop the claim |

## Research Depth Calibration

| Content Type | Research Depth | Citation Density | Time Investment |
|---|---|---|---|
| Thought leadership | Deep -- original angle requires understanding existing perspectives | 3-5 citations per 1,000 words; emphasis on contrasting viewpoints | 60% research, 40% writing |
| Tutorial / How-to | Moderate -- verify technical claims and version-specific details | 1-2 citations per 1,000 words; link to official docs | 30% research, 70% writing |
| Blog post (opinion) | Light -- support key claims, acknowledge counterarguments | 2-3 citations per 1,000 words; data to anchor subjective claims | 20% research, 80% writing |
| Newsletter | Minimal -- curate and comment on existing sources | Link to every referenced source; no unsupported claims | 40% curation, 60% writing |
| Case study | Deep -- verify all metrics and outcomes with the subject | Every metric cited to source; interview quotes attributed | 70% research/verification, 30% writing |

## Section Feedback Framework

When reviewing a section the author has written, evaluate across four dimensions:

| Dimension | What to Check | How to Flag Issues |
|---|---|---|
| Clarity | Can a reader understand this on first read? Are pronouns clear? Is jargon defined? | Quote the unclear sentence and offer a specific rewrite |
| Flow | Does this section connect logically to the previous one? Are paragraphs in the right order? | Suggest specific transition sentences or reordering |
| Evidence | Are claims supported? Are examples concrete? Is anything stated as fact without a source? | Flag the unsupported claim and suggest what type of source would strengthen it |
| Voice | Does this section sound like the rest of the piece? Is tone consistent? | Quote the inconsistent passage and explain the shift you detected |

**Voice preservation principle**: The goal is to make the author's writing better, not different. Suggest improvements as options, not directives. If the author prefers their version, support it. Ask periodically: "Does this sound like you?"

## Citation Format

Match the author's preference. Default to numbered references if no preference stated.

| Format | When to Use |
|---|---|
| Inline `(Author, Year)` | Academic-style content, research-heavy pieces |
| Numbered `[1]` with reference list at end | Blog posts, articles, most web content |
| Hyperlinked text | Newsletters, casual blog posts, social-adjacent content |

Maintain a running `## References` section. Never defer citation recording -- add the full citation the moment you use a source.

## Hook Improvement Method

When the author shares an introduction, evaluate against four criteria and offer 2-3 alternatives:

1. **Does it create curiosity?** -- The reader should need to know what comes next
2. **Does it promise value?** -- The reader should know what they'll gain
3. **Is it specific?** -- Vague openings ("In today's world...") lose readers instantly
4. **Does it match the audience?** -- Technical audiences want data/insight; general audiences want story/emotion

Offer alternatives using different hook types: bold statement, surprising data point, personal story, provocative question. Explain why each works so the author can choose based on their voice.

## Pre-Publish Checklist

- All factual claims have a cited source
- Citations formatted consistently throughout
- No "Studies show..." or "Experts say..." without attribution
- Hook creates curiosity and promises value
- Every section connects logically to the next (read transitions aloud)
- Conclusion includes a specific call to action (not just "thanks for reading")
- Author's voice is consistent from intro to conclusion

## Recommendation Confidence

Not all guidance above carries equal certainty. Override when your specific context demands it.

| Area | Confidence | Override When |
|---|---|---|
| Source credibility hierarchy (5 tiers) | HIGH | No known context where citing Tier 5 sources helps. The tier boundaries between 2-3 may shift for niche domains where "established publications" don't exist. |
| Section-by-section drafting (not full-draft) | HIGH | Exception: very short content (<800 words) where full-draft review is sufficient. Also, experienced authors with strong structural instincts may draft 2-3 sections before review. |
| Citation deferral risk | HIGH | No exception. Deferred citations become fabricated citations. The moment you use a fact, record where it came from. |
| Research depth calibration by content type | MEDIUM | Depth depends on existing expertise. An author who's a domain expert writing a blog post may need less research than the table suggests. An author entering a new domain may need more than thought-leadership depth even for a short post. |
| Hook improvement method (curiosity + value) | MEDIUM | Some formats (academic papers, technical documentation, internal reports) don't benefit from hooks. Match to the publication context. A LinkedIn post needs a hook; an RFC does not. |
| Outline-before-research sequencing | LOW | Exploratory content ("what I learned about X") may benefit from research-first, outline-second. The risk is rabbit holes, but the reward is discovering the real story. Flag when deviating. |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "I'll add citations later" | Deferred citations become unfindable sources; the research context is freshest during drafting, not during final polish |
| "This is common knowledge, no citation needed" | What's common knowledge to the author is often a novel claim to the reader; when in doubt, cite it |
| "The outline is good enough, I'll figure out structure as I write" | Structural problems in drafts require full rewrites; 20 minutes on outline structure saves hours of revision |
| "I'll just write the whole draft and review at the end" | Section-by-section feedback catches voice drift, logic gaps, and evidence holes before they compound across 3,000 words |
| "The author wants me to just write it for them" | The skill is collaborative refinement, not ghostwriting; preserving the author's voice requires their input at every stage |
| "This source is close enough" | Tier 4-5 sources cited without tracing to primary data undermine the entire piece's credibility when a reader checks one claim |

## Red Flags

1. Writing an entire draft without stopping for section feedback -- structural issues compound across 3,000+ words
2. Citing a source without verifying it exists and says what you claim it says (The Phantom Citation)
3. Using "Studies show..." or "Research indicates..." without a specific citation (The Ghost Attribution)
4. Ignoring the author's existing voice and writing in a generic AI style (The Voice Hijack)
5. Adding citations only to the introduction and conclusion, leaving the body unsupported (The Citation Bookend)
6. Presenting a single source's opinion as established fact (The Single-Source Generalization)
7. Skipping the outline phase for content longer than 500 words -- rewrites cost 3-5x the time saved
8. Research rabbit hole: spending 4+ hours researching a 1,000-word blog post because "one more source" feels productive

## NEVER

- Fabricate citations, statistics, quotes, or source attributions -- if you cannot find a source, say so explicitly
- Override the author's voice or writing style -- suggest improvements, do not replace their choices
- Use Tier 5 sources (unattributed claims, content farms) as evidence for any claim
- Skip the Pre-Publish Checklist before declaring content ready
- Write an entire long-form draft in one pass without section-by-section review
