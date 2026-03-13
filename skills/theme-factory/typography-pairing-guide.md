# Typography Pairing Guide

Load when selecting fonts for custom themes, evaluating font pairing quality in existing themes, or troubleshooting readability issues in themed artifacts.

## Font Classification System

| Classification | Characteristics | Signal | Examples |
|---|---|---|---|
| Serif (Old Style) | Organic axis, moderate contrast, bracketed serifs | Traditional authority, publishing, academia | Garamond, Caslon, Palatino |
| Serif (Transitional) | Vertical axis, higher contrast, refined serifs | Professional, corporate, established | Times New Roman, Georgia, Baskerville |
| Serif (Modern/Didone) | Extreme thick-thin contrast, hairline serifs | Luxury, fashion, editorial | Bodoni, Didot, Playfair Display |
| Sans-Serif (Grotesque) | Near-uniform stroke width, slightly quirky forms | Neutral, workhorse, industrial | Helvetica, Arial, Akzidenz-Grotesk |
| Sans-Serif (Neo-Grotesque) | Very uniform stroke, clean terminals | Modern corporate, tech, clean | Inter, SF Pro, Roboto |
| Sans-Serif (Geometric) | Built from circles/lines, uniform strokes | Modern, minimal, design-forward | Futura, Montserrat, Poppins |
| Sans-Serif (Humanist) | Calligraphic influence, varied stroke width | Warm, approachable, readable | Open Sans, Lato, Gill Sans |
| Slab Serif | Thick, block-like serifs | Bold, confident, startup/tech | Rockwell, Roboto Slab, Zilla Slab |
| Monospace | Fixed-width characters | Code, technical, retro/typewriter | Fira Code, JetBrains Mono, IBM Plex Mono |
| Display/Decorative | Highly stylized, not for body text | Headlines only, brand personality | Lobster, Abril Fatface, Playfair Display |

## Pairing Rules

### The Three Pairing Strategies

| Strategy | How It Works | Result | Example |
|---|---|---|---|
| Concordance | Same family, different weights | Harmonious, subtle, safe | Roboto Light (headers) + Roboto Regular (body) |
| Complement | Same classification, different families | Cohesive with personality | Georgia (headers) + Merriweather (body) |
| Contrast | Different classifications | Dynamic, hierarchical, interesting | Playfair Display (headers) + Source Sans Pro (body) |

**Default recommendation**: Use Contrast pairing (serif header + sans body, or vice versa). It creates the clearest visual hierarchy with minimal effort. Concordance is safe but boring. Complement requires expert font knowledge.

### Pairing Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Two decorative fonts | Both compete for attention. No hierarchy. | Maximum one display/decorative font, and only for headers. |
| Fonts from the same classification that look similar | Creates uncanny valley -- "these are almost the same but something's off" | If they look similar, either use the same family (concordance) or pick clearly different fonts |
| Geometric sans header + Geometric sans body | No contrast in structure. Hierarchy relies entirely on size. | Pair geometric with humanist, or switch header to serif/slab |
| Serif body text at small sizes on screen | Thin serifs break down below 14px on standard screens (non-retina) | Use sans-serif for screen body text below 16px. Serif is fine for print or large screen text. |
| More than 2 font families | Each additional font increases page weight and visual complexity | Limit to 2 families. Use weight/style variations within each for variety. |
| Using a font because it looks good in a preview specimen | Specimens show fonts at their best (large, ideal spacing). Real use is body text at 14-16px. | Test every font at actual body text size on the target medium before committing. |

## X-Height and Optical Size Matching

| Concept | What It Means | Why It Matters |
|---|---|---|
| X-height | Height of lowercase 'x' relative to cap height | Fonts with similar x-heights at the same point size look optically balanced side-by-side |
| Cap height | Height of capital letters | If two fonts have different cap heights at the same size, headers and body look misaligned |
| Optical size | Font variant designed for specific sizes (caption, text, display) | A font designed for display (large) will look thin and spindly at body size. Use the correct optical size. |

**Matching rule**: When pairing two fonts, set both to the same point size and compare x-heights. If one is notably taller/shorter, adjust the body font size by 1-2px to compensate. This is why some "correct" pairings look wrong at default sizes.

## Web Font Performance Budget

| Metric | Target | Why |
|---|---|---|
| Total font file weight | <100KB (all variants combined) | Fonts are render-blocking. Each KB delays first contentful paint. |
| Number of variants loaded | Maximum 4 (regular, bold, italic, bold italic) | Each variant is a separate file request and ~25KB |
| Font display strategy | `font-display: swap` | Shows fallback font immediately, swaps when custom font loads. Prevents invisible text. |
| Subsetting | Latin subset only (unless multilingual) | Full Unicode font files can be 200KB+. Subsetting removes unused glyphs. |
| Self-hosting vs CDN | Self-host for performance; CDN for convenience | Google Fonts CDN no longer has cross-site caching benefit (Chrome 86+, 2020). Self-hosting is faster. |

**Performance trap**: Loading 6+ font variants (light, regular, medium, semibold, bold, extrabold) adds 150KB+ and provides marginal visual benefit. Users can't distinguish between regular/medium or semibold/bold at body sizes.

| Weight | Common Name | Use In Theme |
|---|---|---|
| 300 | Light | Large display text (hero headlines) only. Not body text. |
| 400 | Regular | Body text, paragraphs |
| 600 | Semibold | Subheadings, labels, emphasis |
| 700 | Bold | Headers, CTAs, key data points |

**Weight rule**: Skip 100/200 (too thin on screen), 500 (indistinguishable from 400/600), 800/900 (too heavy for most contexts). Four weights cover 98% of use cases.

## Readability Research

| Factor | Finding | Source | Application |
|---|---|---|---|
| Line length | 50-75 characters per line optimal | Baymard Institute, 2020 | Set max-width on text containers. Common failure: full-width text on wide screens. |
| Line height | 1.4-1.6x font size for body text | Web Content Accessibility Guidelines | Tight leading (1.0-1.2) is only acceptable for headlines. |
| Font size | 16px minimum for screen body text | WCAG 2.1 recommendation | 14px is technically allowed but measurably harder to read for ages 40+ |
| Letter spacing | Default for body; +0.5-1px for all-caps | Research on tracking and readability | All-caps without extra tracking is a common readability failure |
| Paragraph spacing | 0.5-1em between paragraphs | UX research consensus | No paragraph spacing creates "wall of text" that suppresses reading |

**Font size hierarchy**: Each level should be 1.2-1.5x the previous. Body 16px -> H3 20px -> H2 24px -> H1 32px. Ratios below 1.2 create weak hierarchy. Ratios above 1.5 create visual gaps.

## Fallback Stack Management

| Font Type | Recommended Fallback Stack | Why This Order |
|---|---|---|
| Sans-serif (generic) | `'Inter', 'Segoe UI', 'Roboto', system-ui, sans-serif` | Inter is most common custom, then Windows native, then Android, then system default |
| Serif (generic) | `'Georgia', 'Cambria', 'Times New Roman', serif` | Georgia was designed for screens; Cambria for Windows; Times as last resort |
| Monospace | `'JetBrains Mono', 'Fira Code', 'Consolas', 'Courier New', monospace` | Developer favorites first, then Windows default, then universal fallback |

**Fallback testing**: Always test the fallback by temporarily disabling custom fonts. If the fallback looks terrible (wrong line breaks, truncated text, broken layout), the design is too dependent on exact font metrics. Adjust container sizing to be font-tolerant.
