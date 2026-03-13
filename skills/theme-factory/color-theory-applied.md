# Applied Color Theory for Theme Design

Load when creating custom themes, adapting existing themes for specific industries/cultures, or troubleshooting color issues in applied themes.

## Color Harmony Systems in Practice

| System | How It Works | When to Use | Risk |
|---|---|---|---|
| Complementary (opposite hues) | High contrast, maximum vibrancy | CTAs, attention-grabbing headers, marketing materials | Overuse creates visual fatigue -- limit complementary pairs to accents (10-15% of surface area) |
| Analogous (adjacent 30-60 degrees) | Natural harmony, low tension | Backgrounds, body sections, editorial content | Can feel monotonous without a contrast accent -- add one hue from opposite side for anchoring |
| Split-complementary | One base + two flanking its complement | Balanced variety without the harshness of direct complement | More complex to manage -- lock the base, adjust flanks by 15-30 degrees for fine-tuning |
| Triadic (three equidistant) | Vibrant, balanced, playful | Creative brands, children's products, entertainment | Must desaturate 2 of 3 hues or the palette fights itself -- 60/30/10 saturation rule |
| Monochromatic (single hue, varied lightness) | Sophisticated, cohesive, safe | Corporate, legal, medical, any context where color shouldn't distract | Needs strong value contrast (lightness difference) to maintain hierarchy |

**60-30-10 Rule**: 60% dominant color (background/base), 30% secondary (containers/cards), 10% accent (CTAs/highlights). Violating this ratio is the #1 cause of "it looks off but I can't explain why."

## Cultural Color Meanings

| Color | Western | East Asian | Middle Eastern | Latin American | South Asian |
|---|---|---|---|---|---|
| Red | Danger, passion, urgency | Luck, prosperity, celebration (China) | Danger, caution | Passion, religion (Christianity) | Purity, fertility (India -- bridal red) |
| White | Purity, cleanliness, minimal | Death, mourning (China, Korea, Japan) | Purity, peace | Peace | Death, mourning (funeral color) |
| Green | Nature, money, growth | Youth, fertility, new life | Islam, paradise, fertility | Death in some regions | Islam, fertility, happiness |
| Yellow | Happiness, caution | Royalty, sacred (China -- imperial yellow) | Happiness, prosperity | Death, mourning (some regions) | Sacred, auspicious (turmeric) |
| Purple | Luxury, royalty | Nobility (Japan), mourning (Thailand) | Wealth, spirituality | Mourning (Brazil) | Wealth, royalty |
| Black | Sophistication, death | Evil, bad luck (can be formal) | Death, mourning, evil | Mourning, masculinity | Evil, negativity, rebellion |

**Practical rule**: If the artifact targets a specific cultural region, cross-check ALL theme colors against that column. A "sophisticated black" theme for a South Asian audience may send the wrong signal. When in doubt, ask the user about their target audience geography.

## Color Blindness Considerations

| Type | Prevalence | What's Affected | Theme Adaptation |
|---|---|---|---|
| Deuteranomaly (weak green) | 5% of males | Green-red distinction reduced | Don't rely on green vs red alone for meaning. Add shape or text labels. |
| Protanomaly (weak red) | 1% of males | Red appears darker/muted | Red CTAs may not "pop" -- ensure luminance contrast, not just hue contrast |
| Tritanomaly (weak blue) | 0.01% of population | Blue-yellow confusion | Rare enough to not drive design, but avoid blue-on-yellow text |
| Achromatopsia (total) | 0.003% of population | All color perception | Design must work in grayscale -- test every theme in grayscale mode |

**Testing procedure**: After applying any theme, mentally convert to grayscale. If two elements that should be distinguishable become the same gray, they need a luminance adjustment, not just a hue change. Tools: Chrome DevTools > Rendering > Emulate vision deficiencies.

## Contrast Optimization Beyond WCAG Minimums

| WCAG Level | Contrast Ratio | What It Actually Means |
|---|---|---|
| AA (minimum) | 4.5:1 for body, 3:1 for large text | Legal compliance minimum. Text is technically readable but can still be uncomfortable. |
| AAA (enhanced) | 7:1 for body, 4.5:1 for large text | Comfortable reading for most users including older adults and low-vision users |
| Practical target | 5.5:1 for body, 4:1 for large text | Sweet spot: clearly readable without looking harsh or "high contrast mode" |

**Contrast anti-pattern**: Maxing contrast (pure black on pure white, 21:1) causes halation -- letters appear to vibrate on screen for users with astigmatism (~33% of population). Use #1a1a1a on #ffffff (18.1:1) or #000000 on #f5f5f5 (19.3:1) instead. Perceptually equivalent readability without the vibration.

| Common Contrast Failures | Why It Happens | Fix |
|---|---|---|
| Light gray body text on white | Designer values "clean" aesthetic over readability | Minimum #595959 on white (7.0:1 AAA) or #757575 on white (4.6:1 AA) |
| Colored text on colored background | Theme accent used for both text and containers | One must be near-neutral. Use the accent for ONE, neutral for the other. |
| Placeholder text too faint | Matches "disabled" convention but is actually instructional | Placeholders need 3:1 minimum if they contain real guidance (not just "Type here...") |
| Dark mode: pure white on pure black | Same halation as reverse but even worse on OLED screens | Use #e0e0e0 on #121212 (15.4:1) for comfortable dark mode reading |

## Color Psychology in Business Contexts

| Business Context | Color Strategy | Research Basis |
|---|---|---|
| Financial services | Blue dominance (trust, stability), green accents (growth, money) | Blue is the #1 preferred color across genders and cultures (Hallock 2003). 33% of top 100 brands use blue. |
| Healthcare | Soft blues and greens (calm, clinical cleanliness) + white space | Patients associate blue/green with sterile environments. Warm colors in healthcare increase anxiety (Dijkstra 2008) |
| E-commerce CTAs | Orange/red for "Buy Now" buttons | Orange CTA on blue/neutral page increased clicks 32.5% vs green (HubSpot A/B test). But this is context-dependent. |
| Legal / consulting | Navy, charcoal, minimal accent | Conservative palettes signal authority and reliability. Bright colors signal casual/creative -- wrong for "trust us with your case" |
| SaaS / tech | Brand-primary accent on neutral base | Too many colors signal complexity. SaaS that looks "fun" gets fewer enterprise signups (Stripe's restraint is strategic) |

**Psychology caveat**: Color psychology research is mostly based on Western, college-aged samples. Effect sizes are small (2-8% conversion differences). Never override brand guidelines or cultural norms based on "red means urgency" blanket rules.

## Deriving Dark Mode from a Light Theme

| Element | Light Theme | Dark Mode Derivation Rule |
|---|---|---|
| Background | White or near-white (#ffffff, #fafafa) | Not pure black. Use #121212 (Material Design) or #1a1a1a. Pure black on OLED causes smearing on scroll. |
| Surface/cards | Light gray (#f5f5f5, #eeeeee) | Elevation = lighter. Cards: #1e1e1e. Modals: #2c2c2c. Each layer 4-8% lighter. |
| Primary text | Near-black (#1a1a1a, #333333) | Not pure white. Use #e0e0e0 (87% opacity white equivalent). |
| Secondary text | Medium gray (#666666, #757575) | #a0a0a0 or similar. Must still meet 4.5:1 on #121212 background. |
| Brand primary | As specified in theme | Desaturate 10-15% and lighten 10%. Saturated colors on dark backgrounds cause eye strain. |
| Brand accent | As specified in theme | May need NO change or slight lightening. Test on dark surface. |
| Borders/dividers | #e0e0e0 (light on white) | #333333 (subtle on dark). Dividers should be discoverable, not prominent. |

**Dark mode trap**: Don't just invert the light theme. Inversion breaks semantic color meaning (red errors become cyan, green success becomes magenta). Keep semantic colors (error, success, warning) identical in both modes -- they're already designed for attention.
