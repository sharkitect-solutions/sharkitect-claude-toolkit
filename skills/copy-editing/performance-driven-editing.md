# Performance-Driven Editing Guide

Load when editing copy that has performance data available (A/B test results, conversion metrics, heatmap data) or when the user wants edits specifically to improve measurable outcomes.

## Editing from Data, Not Instinct

### Metric-to-Sweep Mapping

When performance data exists, prioritize sweeps based on what the data reveals.

| Data Signal | Primary Metric | Which Sweep First | Why |
|---|---|---|---|
| High bounce rate (>70%) on landing page | Time on page <10 seconds | Sweep 1 (Clarity) | Visitors don't understand what the page offers within 5 seconds |
| Visitors scroll but don't convert | Scroll depth >60% but conversion <1% | Sweep 7 (Zero Risk) | They're interested but hesitating -- objections aren't addressed |
| Low click-through on email | Open rate fine (>20%), CTR <1% | Sweep 3 (So What) | Subject line works but body copy doesn't bridge to action |
| High cart abandonment (>75%) | Abandonment at checkout page | Sweep 5 (Specificity) then 7 (Zero Risk) | Pricing or commitment feels vague; trust signals missing |
| High unsubscribe rate (>1%) | Unsubscribes after specific email | Sweep 2 (Voice) | Tone mismatch between what they signed up for and what they received |
| Ad click-through high, landing page conversion low | CTR >2% but landing conversion <2% | Sweep 2 (Voice) then 1 (Clarity) | Ad promised something the landing page doesn't deliver in matching tone |
| Returning visitors don't convert | 3+ sessions, no conversion | Sweep 4 (Prove It) then 6 (Emotion) | They need more evidence or emotional motivation to commit |

### Common "Improvements" That Decrease Conversion

| Edit That Feels Right | Why It Hurts | What Data Shows |
|---|---|---|
| Making copy shorter | Cutting proof, specifics, or objection handling to "keep it clean" removes conversion drivers | Long-form landing pages outperform short-form by 30-50% for products >$100 (Unbounce 2023 benchmark) |
| Replacing specific numbers with round numbers | "About 2,800 customers" feels less credible than "2,847 customers" | Specific numbers are 23% more believable than rounded numbers (Schindler & Yalch, 2006) |
| Adding more exclamation marks for "energy" | Exclamation marks signal amateur writing and reduce trust | Removing exclamation marks from CTAs increased click-through 8% in one A/B test (VWO case study) |
| Replacing benefit-focused headline with clever headline | Clever headlines satisfy the writer, not the reader | Direct benefit headlines outperform clever/witty ones by 41% in B2B (Conductor study) |
| Removing "negative" framing | Fear of loss is 2x more motivating than promise of gain | Loss-framed CTAs ("Don't miss out on $4,200/year in savings") outperform gain-framed ("Save $4,200/year") by 15-25% (Prospect Theory, Kahneman & Tversky) |
| Softening urgency language | If urgency is real, softening it removes a conversion driver | Real deadline copy converts 3-4x better than "available anytime" copy (ConversionXL) |

## Heatmap-Informed Editing

### Reading Pattern Edits

| Heatmap Pattern | What It Means | Editing Action |
|---|---|---|
| F-pattern with drop-off after first paragraph | Visitors scan, never find the key message | Move the primary value proposition and CTA to the first 2 sentences. Don't bury it after an introduction. |
| Attention clusters on images, not text | Copy near images is being skipped | Add captions to images (captions are read 300% more than body copy, Ogilvy). Move key copy into or adjacent to image captions. |
| Heavy engagement with FAQ section | Visitors are looking for answers the main copy didn't provide | Integrate FAQ answers into the main body copy where the questions naturally arise. The FAQ is a signal of copy failure above it. |
| Click concentration on non-clickable elements | Visitors expect something to happen (e.g., clicking a price, feature name) | Make those elements interactive or add CTAs immediately adjacent to the clicked area. |
| Zero engagement below fold | Below-fold content is invisible | Either move critical content above fold OR add a visual cue (arrow, "scroll for..." text) to encourage scrolling. |
| Rage clicks on CTA button | Button is present but something is wrong | Check: is the CTA text clear? Is the button visually distinct? Is the form too long? Rage clicks = intent + friction. |

## A/B Test Results Integration

### Pre-Test Editing

Before running A/B tests on copy, ensure these editing principles:

| Pre-Test Check | Why | How |
|---|---|---|
| Test one variable at a time | Multi-variable tests can't attribute causation | Change EITHER the headline OR the CTA OR the proof section -- never all three |
| Control must be fully edited first | Testing unedited copy against edited copy tests "editing" not "which edit" | Run all 7 sweeps on control. Then create variant by changing one specific element. |
| Sample size before significance | Small samples produce false positives | Minimum 100 conversions per variant for statistical significance at 95% confidence |

### Post-Test Editing Interpretation

| Test Result | What It Means for Editing | Next Action |
|---|---|---|
| Variant headline wins by >10% | Original headline was the bottleneck | Apply Sweep 1 (Clarity) principles to other sections -- the same confusion pattern may exist throughout |
| Longer copy variant wins | Visitors need more information before converting | Add specificity (Sweep 5) and proof (Sweep 4) throughout. Don't cut for brevity. |
| Shorter copy variant wins | Original had filler or repetition | Ruthlessly apply Quick-Pass Editing Reference. Remove anything that doesn't serve clarity, proof, or action. |
| Social proof variant wins by >15% | Trust was the primary barrier | Add proof throughout the page, not just where tested. Move strongest testimonial near CTA. |
| Loss-framed CTA wins | Audience is risk-averse | Reframe throughout using Sweep 7 (Zero Risk) with loss language: "Don't lose..." not "Get..." |
| No significant difference | The tested element isn't the conversion bottleneck | Look at analytics for the real bottleneck: is it traffic quality? Page load speed? Mobile experience? Copy may not be the problem. |

## Copy Scoring Before and After Editing

### Quick Conversion Copy Scorecard

Score each element 1-5 before and after editing to quantify improvement.

| Element | 1 (Weak) | 3 (Adequate) | 5 (Strong) |
|---|---|---|---|
| Headline clarity | Reader doesn't know what's offered | Reader understands offering but not benefit | Reader knows what, why, and for whom in <5 seconds |
| Value proposition | Features listed without benefits | Benefits stated but vague | Specific, quantified benefit with proof |
| Social proof | None or "trusted by thousands" | Named companies or count | Specific result + name + role + company |
| CTA strength | "Submit" or "Learn More" | Action verb + outcome hint | Specific action + specific outcome + zero risk |
| Objection handling | No objections addressed | 1-2 objections addressed | All major objections addressed near point of decision |
| Specificity | "Improve your results" | "Get better results faster" | "Increase qualified leads by 47% in 90 days" |

**Scoring rule**: If any element scores 1-2 after editing, the edit session is incomplete. Focus remaining effort on the lowest-scoring element.

## Format-Specific Performance Benchmarks

| Format | Key Metric | Industry Average | Good | Excellent |
|---|---|---|---|---|
| Landing page | Conversion rate | 2.35% | 5.31% (top 25%) | 11.45% (top 10%) |
| Email subject line | Open rate | 21% | 30% | 40%+ |
| Email body | Click-through rate | 2.6% | 4% | 6%+ |
| Ad headline | Click-through rate | 1.91% (search) | 3% | 5%+ |
| Product description | Add-to-cart rate | 3-5% | 8% | 12%+ |
| CTA button | Click rate | 3-5% | 7% | 10%+ |

Use these benchmarks to set realistic expectations. If a landing page converts at 2% and the user expects 20% from copy edits alone, reset expectations -- copy improvements typically yield 20-50% relative lift, not 10x.
