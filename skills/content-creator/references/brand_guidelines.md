# Voice Calibration Reference

Expert decision layer for calibrating and maintaining brand voice. Generic advice says "be consistent." This reference tells you HOW to calibrate, verify, and adapt voice across content types and platforms.

## Voice Dimension Framework

Every brand voice sits at a point on three independent axes. Calibrate all three before writing.

```
Formality:  Casual ---|---|---|---|--- Formal
Energy:     Reserved ---|---|---|---|--- Energetic
Authority:  Peer ---|---|---|---|--- Expert
```

**Calibration rules by audience:**
- C-Suite: Formal 4-5, Energy 2-3, Authority 4-5. They want confidence without hype.
- Practitioners: Formal 2-3, Energy 3-4, Authority 3-4. They want useful, not stiff.
- General consumer: Formal 1-2, Energy 3-4, Authority 2-3. They want relatable, not lecturing.
- Technical: Formal 3-4, Energy 1-2, Authority 4-5. Precision matters more than warmth.
- Social media: Formal 1-2, Energy 4-5, Authority 2-3. Platform-native energy, conversational trust.

**The calibration error Claude makes:** Without explicit voice direction, Claude writes at Formal 3, Energy 2, Authority 3 for everything. This produces "corporate pleasant" -- readable but forgettable. Force the adjustment by specifying the three dimensions in your prompt or outline.

## Voice Consistency Test

Use this when writing a multi-piece campaign or content series to verify voice stays calibrated:

1. **Sentence length test:** Pull 5 random sentences from piece 1 and 5 from piece 2. If average sentence length differs by more than 5 words, the voice has drifted.
2. **Pronoun test:** Count "you/your" vs "we/our" ratio. If piece 1 is 3:1 and piece 2 is 1:2, the perspective shifted. Pick one ratio and hold it.
3. **Opening pattern test:** Line up the first sentence of each piece. If they share the same structure (e.g., all start with a question, or all start with "We"), the voice is consistent but the content feels repetitive. Same voice, different hooks.
4. **Read-aloud test:** Read a paragraph from each piece aloud, back to back. If they sound like different people wrote them, recalibrate the outlier.

## Common Voice Miscalibration Patterns

| Pattern | What It Looks Like | Fix |
|---------|-------------------|-----|
| **Corporate creep** | Casual brief, but output reads like a press release | Reset: write the first draft as if explaining to a friend, then adjust formality UP one notch only |
| **Enthusiasm inflation** | Every feature is "incredible," every update is "exciting" | Ban superlatives. Use specific impact instead: "cuts setup time by 60%" not "incredibly fast setup" |
| **Authority collapse** | Expert positioning, but hedging everywhere ("might," "could," "perhaps") | Remove hedge words. If the claim needs hedging, the claim is too strong -- rewrite the claim, not the hedge |
| **Tone whiplash** | Professional whitepaper suddenly drops a joke or casual aside | One register per piece. Humor is fine in casual content but must be sustained, not sporadic |
| **Jargon drift** | Consumer content that gradually introduces industry terms without explanation | Every jargon term gets a plain-language parenthetical on first use, or gets cut |

## Platform Voice Adaptation

Same brand, different platforms require voice ADJUSTMENTS (not voice changes):

**LinkedIn:** Shift Authority up +1, Energy down -1 from baseline. Professional context demands slightly more gravitas. Personal stories are fine but frame them as lessons, not anecdotes.

**Twitter/X:** Shift Formality down -1, Energy up +1. Compression forces directness. Remove qualifiers. One idea per tweet. The voice should feel like the brand speaking off the cuff, not reading a script.

**Instagram:** Shift Energy up +1, Authority down -1. Visual platform rewards enthusiasm and relatability. Captions should feel like a caption, not a blog paragraph reformatted.

**Email:** Keep all three dimensions at baseline. Email is the closest to your "natural" brand voice. The reader opted in; they expect the voice they signed up for.

**Blog/Website:** This IS the baseline. All other platforms adjust relative to this.

## Voice Inference Heuristics

When the user provides no voice guidance, infer it rather than defaulting to corporate-pleasant:

1. **Check their existing content first.** If the user has a website or previous content, analyze it for the three voice dimensions. Match what they already have unless they ask for a change.
2. **Industry norms as fallback.** Finance/legal = Formal 4, Energy 2. SaaS/tech = Formal 2-3, Energy 3. Consumer brands = Formal 1-2, Energy 4. Use as starting point, not final answer.
3. **Audience signals.** If the user mentions their audience is "developers," shift to Technical voice. If they mention "small business owners," shift to Practitioner voice. The audience determines the calibration more than the brand does.
4. **Content type signals.** A case study request implies Authority 4+. A social media post request implies Formality 1-2. Let the content type nudge the calibration.
5. **When truly ambiguous:** Ask one question: "Who is reading this, and what should they feel after reading it?" The answer sets all three dimensions.
