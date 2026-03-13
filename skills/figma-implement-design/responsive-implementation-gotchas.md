# Responsive Implementation Gotchas

Load when converting fixed-width Figma frames to responsive layouts, debugging layout breakage at specific viewport widths, handling Figma auto-layout to CSS flexbox/grid translation, or implementing designs that must work across mobile, tablet, and desktop.

## Figma Auto-Layout to CSS: Non-Obvious Gaps

Figma auto-layout LOOKS like flexbox but diverges in critical ways.

| Figma Auto-Layout Property | Expected CSS | Actual Behavior Difference |
|---|---|---|
| Gap (spacing between items) | `gap: Npx` | Figma gap is ALWAYS uniform. CSS `gap` works the same for uniform spacing. But if the Figma design shows variable spacing between items, the designer used padding/margins on individual items, NOT auto-layout gap. Inspect each item separately. |
| "Hug contents" | `width: fit-content` or `width: auto` | Figma "hug" on the main axis = `flex: 0 0 auto` (don't grow, don't shrink). On the cross axis = `align-self: flex-start` (not stretch). The CSS default for flex children is `flex: 0 1 auto` (CAN shrink), which is different. |
| "Fill container" | `flex: 1 1 0` | Figma "fill" = take remaining space equally. CSS equivalent is `flex: 1 1 0` (not `flex: 1` which is shorthand for `flex: 1 1 0` in most browsers but behaves differently in IE11). Multiple "fill" children share space equally. |
| "Fixed size" | `width: Npx; flex-shrink: 0` | A fixed-size child in Figma NEVER shrinks. In CSS, the default `flex-shrink: 1` means it CAN shrink. Always add `flex-shrink: 0` for fixed-width elements inside a flex container. |
| Auto-layout wrap | No direct equivalent | Figma's auto-layout does NOT wrap. If the design appears to wrap, it's nested auto-layout frames. Implement with `flex-wrap: wrap` in CSS, but the wrap behavior needs manual testing -- Figma can't preview it. |
| Padding (auto-layout) | `padding` | Figma supports independent padding per side. Maps directly to CSS `padding-top/right/bottom/left`. No gotcha here -- rare direct mapping. |
| Alignment (primary axis) | `justify-content` | Direct mapping: "Packed start" = `flex-start`, "Packed center" = `center`, "Packed end" = `flex-end`, "Space between" = `space-between`. |
| Alignment (counter axis) | `align-items` | Direct mapping: "Top" = `flex-start`, "Center" = `center`, "Bottom" = `flex-end`. But "Baseline" alignment in Figma maps to `align-items: baseline` which requires text content to work correctly. |

## Breakpoint Mapping

Figma designs are typically delivered at fixed widths. Map them to the project's breakpoint system.

| Common Figma Frame Widths | Likely Target Breakpoint | CSS Implementation |
|---|---|---|
| 375px | Mobile (iPhone SE/13 Mini) | Default styles (mobile-first) or `max-width: 639px` |
| 390px | Mobile (iPhone 14/15) | Same as 375px in practice -- 15px difference is absorbed by fluid layout |
| 768px | Tablet | `min-width: 768px` (Tailwind `md`) |
| 1024px | Small desktop / Landscape tablet | `min-width: 1024px` (Tailwind `lg`) |
| 1280px | Desktop | `min-width: 1280px` (Tailwind `xl`) |
| 1440px | Large desktop | `min-width: 1440px` (Tailwind `2xl`) or max-width container |
| 1920px | Full HD | Usually same as 1440px with centered content area |

**Frame width is not breakpoint**: A 1440px Figma frame doesn't mean "only show this at exactly 1440px." It means "this is how the desktop layout should look." The layout must be fluid BETWEEN breakpoints.

### Missing Breakpoint Strategy

| Figma Provides | What's Missing | Implementation Strategy |
|---|---|---|
| Desktop (1440px) only | Mobile + Tablet | Ask the designer. If unavailable: stack horizontal elements vertically on mobile, reduce grid columns (4->2->1), scale typography down 15-20%, hide decorative elements. |
| Mobile (375px) + Desktop (1440px) | Tablet (768px) | Interpolate: use the desktop layout with reduced padding/margins. If desktop has 3-column grid, use 2-column at tablet. Test at 768px and 1024px. |
| Mobile + Tablet + Desktop | In-between states | Fluid layout handles this. Set max-width on content containers. Test at common intermediate widths: 480px, 640px, 900px, 1100px. |

## Typography Responsiveness

Figma uses fixed font sizes. CSS needs fluid typography or breakpoint-based scaling.

| Figma Typography | Responsive Implementation |
|---|---|
| Heading: 48px | Desktop 48px, Tablet 36px, Mobile 28px. Or use `clamp(1.75rem, 4vw, 3rem)` for fluid scaling. |
| Body: 16px | Keep 16px across all breakpoints. Below 16px on mobile triggers iOS Safari zoom on input focus. |
| Caption: 12px | Keep 12px minimum. Below 12px fails WCAG readability. Some projects set 14px as mobile minimum. |
| Line height: 1.5 (24px on 16px body) | Line height ratios transfer directly. Figma's absolute line height (e.g., "24") = `line-height: 1.5` relative. |

**The `clamp()` approach**: `font-size: clamp(min, preferred, max)` scales fluidly between breakpoints. Example: `clamp(1.25rem, 2.5vw + 0.5rem, 2rem)`. But test readability at ALL viewport widths -- `vw`-based sizing can produce awkward in-between sizes.

## Image and Asset Responsiveness

| Figma Asset | Responsive Implementation | Gotcha |
|---|---|---|
| Full-width hero image | `width: 100%; height: auto; object-fit: cover` | Figma shows a cropped rectangle. CSS `object-fit: cover` replicates this, but the CROP POINT changes at different viewports. Use `object-position` to control focal point. |
| Fixed-size icon (24px) | Keep at 24px or use `1.5rem` | Icons should NOT scale with viewport. 24px is a touch target minimum (WCAG). |
| Background pattern | `background-size: cover` or `contain` based on intent | Figma shows pattern at one size. Decide: should pattern scale (cover), tile (repeat), or maintain aspect ratio (contain)? |
| SVG illustration | `width: 100%; max-width: {figma-width}px; height: auto` | SVG scales infinitely but the Figma frame implies an intended maximum size. Preserve aspect ratio with `viewBox`. |
| Raster image (PNG/JPG) | `srcset` with 1x, 2x, 3x variants | Figma exports at 1x by default. For retina displays, export at 2x and 3x or request higher-resolution assets from the designer. |

## Grid System Translation

| Figma Grid | CSS Grid Implementation | Gotcha |
|---|---|---|
| 12-column grid, 1440px, 24px gutter | `grid-template-columns: repeat(12, 1fr); gap: 24px; max-width: 1440px` | Figma grids are visual guides, not code structures. The designer may or may not have aligned elements to the grid. Verify before assuming column spans. |
| Column span 4 (1/3 width) | `grid-column: span 4` on 12-col or `span 1` on 3-col | Use the simplest grid that matches the design. A 3-column layout doesn't need a 12-column grid -- `repeat(3, 1fr)` is cleaner. |
| Asymmetric columns (sidebar + main) | `grid-template-columns: 280px 1fr` | Fixed sidebar width + fluid main content. At mobile breakpoint: stack vertically with `grid-template-columns: 1fr`. |
| Figma "Layout Grid" with margins | `max-width` container + `padding` or `margin: 0 auto` | Figma grid margins = content padding from viewport edge. Map to `padding-inline` on the container. |

## Common Responsive Failures

| Failure | Why It Happens | Prevention |
|---|---|---|
| Content overflows on mobile | Fixed-width elements from Figma don't shrink | Use `max-width: 100%` on all elements that have a fixed width in Figma. Add `overflow-wrap: break-word` for text. |
| Horizontal scroll on mobile | An element exceeds viewport width | Set `overflow-x: hidden` on `body` as a safety net, but fix the root cause: find the element with `width > 100vw`. Common culprits: tables, code blocks, images without max-width. |
| Touch targets too small | Figma desktop design has 32px buttons | Minimum touch target: 44x44px (WCAG 2.5.8). Increase `padding` on mobile, not the visual button size. Use `min-height: 44px; min-width: 44px`. |
| Text unreadable on mobile | Font size below 16px | Set `font-size: max(16px, {figma-size})` for body text. Never go below 14px for any text on mobile. |
| Layout shifts during load | Images without explicit dimensions | Always set `width` and `height` attributes on `<img>` (even if CSS overrides them). This reserves space and prevents CLS. Use `aspect-ratio` for responsive images. |
| Inconsistent spacing at breakpoints | Hardcoded px values from Figma | Use relative spacing that scales: `clamp(1rem, 2vw, 2rem)` for margins, or breakpoint-specific spacing tokens. |
