# Theme Application Patterns

Load when applying themes to specific artifact types (slides, documents, HTML pages, reports), troubleshooting inconsistent theme application, or adapting a theme for a context it wasn't designed for.

## Cross-Artifact Application Rules

| Artifact Type | Background | Headers | Body Text | Accents | Gotcha |
|---|---|---|---|---|---|
| Slides (PPTX) | Full-bleed background color or gradient | Large, high-contrast, 28-44pt | 18-24pt minimum (projection readability) | Sparingly -- one accent color for emphasis | Projectors wash out colors by 20-30%. Increase saturation and contrast beyond what looks good on screen. |
| Documents (DOCX) | White or very light tint only | Brand primary color, 18-24pt | Black or near-black, 11-12pt | Links, callout boxes, table headers | Do NOT color document backgrounds dark -- printing wastes ink and photocopies badly. |
| HTML pages | Background-color on body or sections | Colored or weighted, follows H1-H6 hierarchy | 16px minimum, high contrast on background | CTAs, links, hover states, borders | Test on both light and dark system preferences if the page doesn't control its own color scheme. |
| Reports (PDF) | White for printability | Colored headers with sufficient contrast | 10-12pt, serif often preferred for long-form | Tables, charts, dividers | PDFs are often printed B&W. Ensure color-coded information also uses shape/pattern/label. |
| Emails (HTML) | White or brand-neutral | Inline styles only (no external CSS) | 14-16px, system fonts preferred | CTAs, section dividers | Email clients strip most CSS. Test in Gmail, Outlook, Apple Mail. Dark mode inverts colors unpredictably. |

## Theme Consistency Checklist

Apply after every theme application. Each item must pass.

| Check | What to Verify | Common Failure |
|---|---|---|
| Header hierarchy | H1, H2, H3 each visually distinct by size AND weight/color | All headers same size, only weight differs (too subtle) |
| Body text uniformity | Same font, size, color, and line height throughout | Copy-pasted sections retain source formatting |
| Accent usage | Accent color appears in same contexts everywhere (all CTAs, all links, all highlights) | Accent used for CTA in section 1 but not section 5 |
| Background consistency | Same background treatment for equivalent elements | Some cards have theme background, others are plain white |
| Border/divider style | Same color, weight, and style for all dividers | Top dividers are theme-colored, bottom dividers are default gray |
| Image integration | Images don't clash with theme palette | Stock photos with competing color palettes undermine theme cohesion |
| White space | Consistent padding/margins throughout | Tight spacing in some sections, loose in others |

## Theme Adaptation for Specific Contexts

### When the Theme Doesn't Fit the Content

| Situation | Adaptation Strategy | What NOT to Do |
|---|---|---|
| Dark theme applied to a data-heavy table | Lighten table background to a mid-tone (e.g., #2a2a2a -> #3d3d3d). Alternate row colors with 3-5% lightness difference. | Don't use the darkest background color for tables -- insufficient row distinction |
| Warm theme applied to a financial report | Desaturate warm accents by 20% for data sections. Keep warm accents for headers/titles only. | Don't use bright oranges/reds for financial data -- accidental "danger" signal |
| Vibrant theme applied to a legal document | Use vibrant colors only for headers and dividers. Body sections use neutral tones from the theme's extended palette. | Don't apply full vibrant treatment to legal text -- undermines perceived seriousness |
| Minimal theme applied to a marketing slide | Add ONE pop color from the minimal palette's accent. Scale it to 15-20% of visual area. | Don't add colors outside the theme -- "just one extra blue" breaks minimalism |
| Any theme applied to a chart/graph | Use theme colors for data series IN ORDER (primary, secondary, accent, then derived tints). | Don't use random theme colors for chart series -- the color order signals data hierarchy |

### Chart and Data Visualization Theming

| Element | Theme Application Rule |
|---|---|
| Data series (bars, lines, areas) | Primary color for most important series, secondary for second, accent for third. Beyond 3: derive tints at 60% and 40% opacity. |
| Axis labels and ticks | Body text color at smaller size. Never accent-colored. |
| Grid lines | 10-15% opacity of body text color. Must be visible but not compete with data. |
| Legend | Body font, body color. Position outside plot area. |
| Title | Header font and color from theme. Left-aligned preferred (research shows faster comprehension than centered). |

**Chart color gotcha**: If the theme only has 2-3 colors, deriving tints for a 6-series chart produces colors too similar to distinguish. For 4+ data series, use a sequential or diverging color scale derived from the primary hue, not the full theme palette.

## Common Theme Application Failures

| Failure | What Happens | Prevention |
|---|---|---|
| Partial application | Headers themed, body text default. Or first half themed, second half reverted. | Apply theme to the template/master, not individual elements. Check EVERY section. |
| Contrast failure introduced | Theme accent used for text on theme background -- contrast below 4.5:1 | Test EVERY text-on-background combination. Light accents on light backgrounds are the #1 failure. |
| Font not available | Custom theme font not installed on viewer's machine -- falls back to system default | For shared documents: embed fonts. For HTML: include font files or CDN link. For slides: use widely available fonts. |
| Theme overrides semantic colors | Theme replaces red error/green success with theme accent colors | NEVER theme semantic colors (error, warning, success, info). These are universal and must remain recognizable. |
| Logo color clash | Company logo colors conflict with applied theme | Place logo on white/neutral background inset, or use monochrome logo variant if available |
| Inconsistent icon styling | Some icons themed, others remain default blue/black | Inventory ALL icons and apply theme accent consistently. If SVG: change fill. If raster: use CSS filter or replace. |
| Dark mode not derived | Light theme applied, dark mode shows default/broken | If the artifact supports dark mode, derive the dark variant (see color-theory-applied.md) before delivery. |

## Brand Guideline Integration

When the user provides brand guidelines alongside a theme request:

| Priority | Rule |
|---|---|
| 1 | Brand colors override theme colors where they conflict |
| 2 | Brand fonts override theme fonts |
| 3 | Theme fills gaps (accent colors, secondary fonts) that brand guidelines don't specify |
| 4 | If brand and theme clash aesthetically, use brand as primary and theme as structural inspiration only |
| 5 | NEVER mix brand logo colors into the theme palette unless the brand guidelines explicitly allow it |

**Brand guideline gotcha**: Many brand guidelines specify CMYK colors for print but not HEX/RGB for screen. Don't convert CMYK to RGB naively -- CMYK has a smaller gamut, and direct conversion produces dull screen colors. Ask for screen-specific brand colors, or brighten converted values by 5-10%.

## Theme Testing Protocol

Before declaring a themed artifact complete:

| Test | Method | Pass Criteria |
|---|---|---|
| Grayscale test | View entire artifact in grayscale | All elements distinguishable by lightness alone |
| Squint test | Squint at the artifact from arm's length | Visual hierarchy (headers > body > captions) still readable |
| 5-second scan | Show artifact to someone for 5 seconds | They can identify: the topic, the key message, and where to look next |
| Print test (if printable) | Print one representative page in B&W | All content readable, no information lost |
| Resize test (if responsive) | View at 320px and 1920px widths | Theme doesn't break at extreme sizes |
| Dark mode test (if applicable) | Toggle to dark mode | All text readable, no invisible elements, semantic colors preserved |
