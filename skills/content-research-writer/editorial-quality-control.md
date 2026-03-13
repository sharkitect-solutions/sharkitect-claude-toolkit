# Editorial Quality Control

Load when establishing review processes, managing research scope, handling accuracy-under-deadline tradeoffs, auditing voice consistency, dealing with corrections, or diagnosing why a draft isn't working despite good research.

## The Research Rabbit Hole Problem

Research has diminishing returns. The first hour finds 80% of useful sources. The next 3 hours find 15%. The last 6 hours find 5% and introduce confusion from contradictory findings.

### Timeboxing by Content Type

| Content Type | Research Timebox | Stop Researching When |
|---|---|---|
| Blog post (1,000-2,000 words) | 1-2 hours | You have 3+ credible sources for each major claim and zero unsupported assertions |
| Thought leadership (2,000-4,000 words) | 3-5 hours | You can articulate the 2-3 strongest counterarguments to your thesis |
| Comprehensive guide (4,000+ words) | 5-8 hours | You have coverage for every section in your outline and can't find new perspectives |
| Case study | 2-3 hours + subject interview | The subject has verified all metrics and you have before/after data |
| Newsletter issue | 30-60 minutes | You've identified 3-5 sources worth sharing and have a connective theme |

### Diminishing Returns Signals

| Signal | What It Means | What to Do |
|---|---|---|
| New sources repeat what you already have | You've reached saturation for this topic | Stop researching. Start writing. |
| Sources start contradicting each other | You've hit genuine ambiguity in the field | Acknowledge the disagreement in the piece rather than searching for a tiebreaker. |
| You're reading tangentially related papers | Scope creep -- you're no longer researching your topic | Return to your outline. Does the tangent serve a specific section? If not, bookmark and move on. |
| You keep refining search queries without finding new results | You've exhausted available sources | Document what you couldn't find ("no published data exists on X") -- that's a valid finding. |
| Research is more interesting than writing | Procrastination disguised as productivity | Set a hard deadline and start the draft with what you have. Gaps will be obvious during writing. |

## Fact-Checking Tiers

Not every claim needs the same verification rigor. Allocate effort based on risk.

| Tier | Verification Level | Applies To | Procedure |
|---|---|---|---|
| Critical | 3+ independent sources, primary source verified, quote checked verbatim | Core thesis claims, statistics that drive the argument, direct quotes, legal/medical/financial claims | Read the primary source yourself. Don't rely on another article's summary. Cross-reference with 2 additional sources. |
| Standard | 2 sources, one primary or authoritative | Supporting evidence, named facts, dates, attributions | Verify the claim appears in at least 2 independent sources. Check for currency (not outdated). |
| Contextual | 1 authoritative source, flagged if not found | Background context, widely accepted facts, illustrative examples | One credible source is sufficient. If you can't find one, drop the claim -- it's probably wrong. |
| Attribution-only | Source is named, reader can verify independently | Opinions, predictions, subjective assessments | "According to [source]..." -- you're reporting their view, not endorsing it. Accuracy means they actually said it. |

## Accuracy Under Deadline

When time is short, prioritize verification by damage potential.

| If Wrong, Impact Is... | Verification Priority | Acceptable Shortcut |
|---|---|---|
| Legal liability (defamation, securities, medical) | VERIFY OR REMOVE. No exceptions. | Remove the claim entirely if you can't verify quickly. |
| Reputation damage (misattribution, fabricated data) | VERIFY. This is the floor. | Contact the source directly for confirmation. |
| Misleading (wrong statistic, outdated data) | VERIFY if central to argument. Hedge if peripheral. | Use hedge language: "approximately," "as of [date]," "according to [single source]" |
| Minor inaccuracy (wrong year, approximate number) | Reasonable effort. Note uncertainty if unsure. | "[Year] or [Year]" or "[approximately X]" -- transparency preserves trust even with imprecision |
| Stylistic (tone, flow, structure) | Defer to next revision | Ship with a note to revisit in the next editing pass |

### Hedge Language Calibration

| Hedging Level | Language | Use When |
|---|---|---|
| No hedge needed | "X is..." or "Research shows..." | 3+ high-quality sources agree, claim is well-established |
| Light hedge | "X tends to..." or "Evidence suggests..." | 1-2 good sources, consistent with broader knowledge |
| Moderate hedge | "Some research indicates..." or "In many cases..." | Limited evidence, or evidence from adjacent domains |
| Strong hedge | "It's possible that..." or "Early findings hint at..." | Single study, small sample, preprint, or contested |
| Attribution hedge | "According to [source]..." | You're reporting a claim you can't independently verify |

## Voice Consistency Audit

Voice drift is the most common problem in collaborative writing and the hardest to detect.

### Measurable Voice Markers

| Marker | How to Measure | Consistency Rule |
|---|---|---|
| Sentence length | Average words per sentence by section | Variance of +/-30% across sections is normal. >50% variance indicates voice drift. |
| Formality level | Count contractions, colloquialisms, technical terms per 500 words | A section that suddenly drops contractions or adds jargon signals a different voice. |
| Person/perspective | First person (I/we), second person (you), third person (one/they) | Mixing perspectives within a piece is almost always a mistake. Choose one and maintain it. |
| Paragraph structure | Average sentences per paragraph | Sudden shift from 3-sentence paragraphs to 8-sentence paragraphs is jarring. |
| Qualifier density | Count hedging words (might, could, possibly, somewhat) per 500 words | A confident section followed by a heavily hedged section reads as two different authors. |

### Common Voice Drift Patterns

| Pattern | Cause | Fix |
|---|---|---|
| Introduction is casual, body is academic | Author wrote the intro; AI wrote the body (or vice versa) | Re-read the intro aloud, then the body. Adjust the body's tone to match the intro's. |
| One section is noticeably more polished | That section was revised more than others | Bring other sections to the same polish level, or slightly reduce the revised section's polish. |
| Abrupt formality shift after a quote | The quoted source's voice infected the surrounding text | Add a transition sentence in the author's voice between the quote and the analysis. |
| Technical depth spikes in one section | Author is more expert in that subtopic | Calibrate to the least-expert section's depth. Move excess detail to a footnote or companion piece. |

## Common Editorial Failures

Named failures for pattern recognition.

| Failure | What Happens | Detection | Prevention |
|---|---|---|---|
| The Citation Sandwich | Every paragraph has the same structure: claim, citation, interpretation, claim, citation, interpretation | Read 3 paragraphs aloud. If they all sound the same, you have this. | Vary paragraph structures. Some paragraphs should synthesize multiple sources. Some should be pure analysis with no citations. |
| The Source Launder | A dubious source is cited by a reputable one, and the writer cites the reputable one as if it originated the claim | Check: does the "reputable" source cite a primary source for this specific claim? | Always trace claims to their origin. "HBR says..." might mean "HBR quoted a blog post that quoted a Reddit comment." |
| The Anecdote Bridge | A single story is used to support a general claim with no statistical evidence | Count: how many data points support this generalization? If the answer is one story, it's an anecdote bridge. | Anecdotes illustrate; they don't prove. Pair every anecdote with data, or explicitly label it as illustration. |
| The Wikipedia Trail | Writer follows hyperlinks from one Wikipedia article to another, accumulating "research" that's actually one unreliable source chain | Check: are all your sources ultimately traceable to independent primary research? | Use Wikipedia for orientation only. Every fact must be verified against the cited primary source. |
| The Recency Trap | Writer only cites sources from the last 12 months, missing foundational work | Check the date range of your citations. If nothing is older than 2 years, you may be ignoring established knowledge. | Include foundational sources. A 2024 blog post citing a 2010 study doesn't make the finding new. Cite the 2010 study. |
| The Quote Wall | 40%+ of the piece is direct quotes, with the writer adding only transitions | Highlight all quoted text. If the highlighting covers most of the piece, you have a quote wall. | Paraphrase most sources. Reserve direct quotes for uniquely well-stated points or when precise wording matters (legal, scientific). |
| Attribution Drift | A claim is attributed to Source A in paragraph 1 but treated as established fact by paragraph 5 | Track which claims are attributed. If the same claim reappears later without attribution, attribution has drifted. | Re-attribute or clearly mark the transition: "As [Source A] established, X..." before building on it. |

## Correction and Update Protocol

Errors happen. How you handle them determines credibility.

| Error Type | Response | Timing |
|---|---|---|
| Factual error (wrong number, wrong date, wrong name) | Correct in-text + add correction notice at top: "Correction [date]: This article originally stated X. The correct figure is Y." | Immediately upon discovery |
| Misattribution (wrong person credited) | Correct + correction notice + notify affected parties | Immediately |
| Outdated information (was correct when published) | Update in-text + add "Updated [date]" notice with what changed | When you become aware or during scheduled reviews |
| Missing context (fact was correct but incomplete) | Add context + "Updated [date]: Added context about Y" | When the omission is pointed out or discovered |
| Source retracted (cited study was retracted after publication) | Remove or replace the citation + correction notice explaining the change | Immediately upon learning of retraction |

### Never Do

- Silently edit published content without a correction notice -- readers who shared the original version look foolish
- Delete comments or responses that pointed out the error -- this destroys trust
- Publish a "correction" that minimizes the error -- be straightforward about what was wrong
