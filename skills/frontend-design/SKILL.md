---
name: frontend-design
description: "Use when building web components, pages, landing pages, dashboards, HTML/CSS layouts, React/Vue/Svelte components, or any frontend interface from scratch without a Figma source. Also use when the user asks to style, beautify, or redesign an existing web UI, or requests a visually distinctive artifact (poster, card, banner). NEVER use for Figma-to-code translation (use figma-implement-design), UX critique or design system audits (use ui-ux-pro-max), applying preset color/font themes (use theme-factory), or cleaning up AI-generated code (use deslop)."
---

# Frontend Design

Builds production-grade frontend interfaces from scratch with distinctive visual identity. This skill covers the creative design decisions and implementation -- not Figma translation, not UX auditing, not theme application.

## Scope Boundary

| This Skill (frontend-design) | Other Skills |
|---|---|
| From-scratch UI creation with original design direction | figma-implement-design: translating existing Figma designs to code |
| Aesthetic decision-making (color, type, layout, motion) | ui-ux-pro-max: UX best practices, accessibility audits, design system lookup |
| Visual implementation and polish | theme-factory: applying preset color/font themes to artifacts |
| Anti-slop enforcement for visual design | deslop: removing AI code artifacts from written code |

## Design Direction Decision Matrix

Select aesthetic direction based on context signals, not personal preference. The matrix prevents defaulting to the same style every time.

| Context Signal | Strong Match Aesthetics | Poor Match Aesthetics |
|---|---|---|
| B2B SaaS / enterprise | Editorial, industrial-utilitarian, refined minimal | Playful, retro-futuristic, maximalist |
| Consumer mobile / social | Playful, soft-pastel, organic-natural | Brutalist, industrial, editorial |
| Creative portfolio / agency | Brutalist-raw, maximalist-chaos, art-deco | Corporate-minimal, industrial-utilitarian |
| E-commerce / luxury brand | Luxury-refined, art-deco-geometric, editorial | Brutalist, playful-toy, industrial |
| Developer tools / docs | Industrial-utilitarian, refined-minimal, retro-terminal | Soft-pastel, organic-natural, luxury |
| Health / wellness | Organic-natural, soft-pastel, luxury-refined | Brutalist, industrial, retro-futuristic |
| Fintech / crypto | Retro-futuristic, refined-minimal, dark-editorial | Playful, organic-natural, soft-pastel |
| Gaming / entertainment | Maximalist-chaos, retro-futuristic, neon-brutalist | Corporate-minimal, editorial, luxury |
| Restaurant / food | Organic-natural, editorial-magazine, art-deco | Industrial, brutalist, retro-terminal |
| Education / non-profit | Playful, organic-natural, soft-editorial | Brutalist, maximalist, dark themes |

**Rule**: If the user specifies an aesthetic, use it regardless of this matrix. The matrix applies only when no direction is given.

## Typography Pairing Rules

Specific pairings that work. Do not pick fonts by browsing Google Fonts at random.

| Display Font | Body Font | Aesthetic | Use When |
|---|---|---|---|
| Playfair Display | Source Sans 3 | Editorial-luxury | Long-form content, magazines, luxury |
| Clash Display | General Sans | Bold-modern | Portfolios, agencies, startups |
| Fraunces | Outfit | Organic-warm | Wellness, food, lifestyle |
| Syne | Switzer (Fontshare) | Retro-futuristic | Tech, crypto, experimental |
| Cabinet Grotesk | Satoshi | Clean-confident | SaaS, dashboards, B2B |
| Bodoni Moda | Work Sans | Art-deco-elegant | Fashion, luxury, events |
| DM Serif Display | DM Sans | Classic-modern | Restaurants, editorial, branding |
| Instrument Serif | Instrument Sans | Refined-editorial | Portfolios, publications, galleries |
| Space Mono | Geist Sans | Developer-terminal | Dev tools, code products, CLI UIs |
| Bricolage Grotesque | Geist Sans | Quirky-technical | Creative tech, indie products |

**Rule**: Never reuse the same pairing across consecutive generations. Track what was last used and rotate. If a project has an established type system, use its fonts instead of this table.

## Color Strategy by Context

| Context | Primary Strategy | Accent Strategy | Background Strategy |
|---|---|---|---|
| Dark theme (default for tech) | Desaturated primary (HSL S: 30-50%) | High-saturation accent at 1-2 touch points | Near-black with subtle hue tint (not pure #000) |
| Light theme (default for consumer) | Mid-saturation primary (HSL S: 50-70%) | Complementary or split-complementary accent | Warm off-white or cool off-white (not pure #fff) |
| High-energy (gaming, events) | Full-saturation primary | Neon accent, gradient transitions | Dark with noise/grain texture |
| Luxury / premium | Low-saturation or metallic tones | Gold (#C9A96E range), copper, champagne | Deep navy, charcoal, or cream |
| Playful / consumer | High-saturation, 3-4 color palette | Contrasting complementary | Light with subtle pattern or illustration |

**Anti-pattern**: Purple-to-blue gradient on white background. This is the single most common AI-generated color scheme. Avoid it entirely unless the user explicitly requests purple.

**CSS variable structure** (always implement):
```
--color-primary, --color-primary-hover, --color-accent, --color-surface, --color-surface-elevated, --color-text, --color-text-muted, --color-border
```

## Layout Pattern Selection

| Content Type | Layout Pattern | Key CSS |
|---|---|---|
| Hero / above-fold | Asymmetric split (60/40 or 70/30) with offset elements | Grid with named areas, negative margins for overlap |
| Feature grid | Bento grid with mixed cell sizes (not uniform cards) | `grid-template-columns: repeat(auto-fit, minmax())` with span variations |
| Long-form content | Single column, max-width 65ch, generous vertical rhythm | `margin-block` spacing scale, not margin-top/bottom pairs |
| Dashboard | CSS Grid with sidebar, fixed header, scrollable content area | `grid-template-rows: auto 1fr; overflow-y: auto` on content |
| Portfolio / gallery | Masonry or staggered grid with hover reveals | CSS columns or JS masonry; `aspect-ratio` for consistent cards |
| Pricing / comparison | Centered cards with elevation hierarchy (featured = elevated) | `transform: scale(1.05)` on featured, shadow depth differentiation |

**Rule**: Never use a 3-column uniform card grid as the default layout. It is the most overused AI pattern. Use bento, asymmetric splits, or staggered layouts instead.

## Animation Budget

Motion must be intentional. Allocate a budget per page, not per element.

| Animation Type | Max Per Page | Duration | Easing | Priority |
|---|---|---|---|---|
| Page-load entrance (staggered reveals) | 1 orchestrated sequence | 400-800ms total | cubic-bezier(0.16, 1, 0.3, 1) | HIGH -- do this first |
| Scroll-triggered reveals | 3-5 sections max | 300-500ms each | ease-out | MEDIUM |
| Hover micro-interactions | Unlimited but subtle | 150-200ms | ease-in-out | LOW -- add last |
| Background ambient (particles, gradients) | 0-1 per page | Continuous, slow | linear | OPTIONAL -- only for maximalist |
| Loading/skeleton states | Every async element | 1-2s pulse cycle | ease-in-out | REQUIRED for any async content |

**Rule**: One well-orchestrated page-load sequence with staggered `animation-delay` (50-100ms per element) creates more impact than 20 scattered hover effects. Invest time in the entrance, not the hover.

**CSS-first**: Use CSS animations and transitions for HTML projects. Only reach for JS animation libraries (Motion, GSAP) when CSS cannot achieve the effect (scroll-linked progress, physics-based spring, complex sequencing).

## Visual Slop Detection Checklist

These patterns mark a frontend as AI-generated. Check every output against this list before delivery.

| Slop Pattern | What It Looks Like | Fix |
|---|---|---|
| Purple gradient fallback | `linear-gradient(135deg, #667eea, #764ba2)` or similar purple-blue | Choose a context-appropriate palette from Color Strategy table |
| Inter/Roboto/Arial everywhere | System fonts or the 3 most common Google Fonts | Select from Typography Pairing Rules table |
| Uniform 3-card grid | Three identical cards in a row, same size, same spacing | Bento grid, asymmetric layout, or staggered sizes |
| Rounded-2xl on everything | Every element has `border-radius: 16px` | Vary radii: sharp for buttons (4-8px), medium for cards (8-12px), large only for hero images or avatars |
| Generic hero with centered text | Centered h1 + p + button on plain gradient | Asymmetric split, offset text, overlapping image, or editorial layout |
| Shadow-lg on all cards | Same box-shadow on every elevated element | Differentiate shadow depth by importance; use subtle shadows (2-4px blur) for most elements |
| Emoji as icons | Using unicode emoji in place of SVG icons | Use Lucide, Heroicons, Phosphor, or Tabler Icons (SVG) |
| White/light-gray background | `#ffffff` or `#f5f5f5` with no texture or personality | Off-white with hue tint, subtle noise texture, or gradient mesh |
| Evenly distributed color palette | Equal amounts of 4-5 colors across the page | 60-30-10 rule: dominant, secondary, accent |

## Responsive Implementation Gotchas

Non-obvious issues that cause production bugs on specific devices or browsers:

| Gotcha | What Goes Wrong | Fix |
|---|---|---|
| `100vh` on mobile Safari/Chrome | Address bar is included in viewport height -- bottom content gets cut off, buttons become unreachable | Use `100dvh` (dynamic viewport height) with `100vh` fallback: `height: 100vh; height: 100dvh;` |
| Fixed background on iOS | `background-attachment: fixed` does not work on iOS Safari -- image scrolls with content or causes repaint jank | Use `position: fixed` wrapper with `z-index: -1` behind scrollable content instead |
| Font-size below 16px in inputs on iOS | Safari auto-zooms the page when a user taps an input with font-size below 16px, breaking the layout until they pinch back | Set `font-size: 16px` minimum on all form inputs, or use `maximum-scale=1` on viewport meta (blocks pinch-zoom -- accessibility concern) |
| `gap` in flexbox on Safari 14 | `gap` property in flexbox was unsupported in Safari before 14.1 (2021) -- still matters for users on older iPads | Use `margin` on children as fallback, or check caniuse for your target browser range |
| Container queries without fallback | `@container` queries have no support in older browsers and fail silently -- layout breaks without error | Always provide a `@media` query fallback before the `@container` rule for progressive enhancement |
| Fluid typography clamping | `font-size: clamp(1rem, 2.5vw, 2rem)` creates text too small on narrow viewports and too large on ultrawide | Test at 320px (smallest phone) and 2560px (ultrawide). Adjust the vw coefficient -- `calc(1rem + 0.5vw)` is often more stable than clamp for body text |

## Implementation Procedure

1. **Parse requirements**: Identify content type, audience, technical constraints, and any stated aesthetic preferences.
2. **Select aesthetic direction**: Use the Decision Matrix if no direction is given. If a direction is given, commit to it fully.
3. **Choose typography**: Select a pairing from the Typography table that matches the aesthetic. Import via Google Fonts or Fontshare CDN link.
4. **Define color variables**: Apply Color Strategy for the context. Always implement CSS custom properties. Test contrast ratios (4.5:1 minimum for text).
5. **Choose layout pattern**: Match content type to Layout Pattern Selection. Never default to uniform grids.
6. **Implement core structure**: Build HTML/JSX structure with semantic elements. Apply layout with CSS Grid or Flexbox.
7. **Add visual personality**: Backgrounds (gradients, textures, noise), borders, shadows, and decorative elements that match the aesthetic direction.
8. **Apply animation budget**: Page-load entrance first, scroll triggers second, hover states last. Stay within budget.
9. **Run slop checklist**: Check output against every row in Visual Slop Detection. Fix any matches before delivery.
10. **Responsive pass**: Test at 375px, 768px, 1024px, 1440px. Ensure no horizontal scroll, readable text, functional navigation.

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "Inter is clean and professional, it works for everything" | Inter is Claude's default font choice -- using it guarantees the output looks AI-generated. Every context has a more distinctive option. |
| "A purple gradient looks modern and tech-forward" | It is the most common AI-generated color scheme. Users recognize it instantly as generic output. |
| "Three cards in a row is a clean layout" | It is the path of least resistance, not a design decision. Bento grids and asymmetric layouts require the same code effort but produce distinctive results. |
| "I'll add animations to everything for polish" | Scattered micro-interactions without a coherent entrance sequence feel chaotic. One orchestrated page-load creates more perceived quality. |
| "Minimalist means fewer CSS lines" | Minimalist execution requires more precision in spacing, typography scale, and color restraint -- not less code. Cutting corners produces empty, not minimal. |
| "The user didn't specify dark or light, so I'll use light with white background" | Light themes need more design effort to avoid looking generic. Default to dark for tech contexts, and always add texture/tint to light backgrounds. |

## Red Flags

- Outputting Inter, Roboto, or Arial as the font choice in any context
- Using purple-to-blue gradients without explicit user request for purple
- Generating three identical cards in a row as the primary layout pattern
- Applying the same border-radius, shadow, and spacing values to every element
- Centering all text in a hero section with no asymmetry or visual tension
- Adding `border-radius: 9999px` (full-round) to rectangular content cards
- Using emoji characters as UI icons instead of SVG icon libraries
- Producing a white (#fff) or light-gray (#f5f5f5) background with no texture, tint, or depth

## NEVER

- Use the same typography pairing in consecutive generations -- rotate from the pairing table
- Default to a centered hero + 3-card grid layout without considering alternatives from the Layout Pattern table
- Skip the Visual Slop Detection Checklist before delivering any frontend output
- Apply maximalist animation budgets to minimalist aesthetic directions or vice versa
- Generate a frontend that could be mistaken for a generic template -- every output must have a specific, defensible design rationale
