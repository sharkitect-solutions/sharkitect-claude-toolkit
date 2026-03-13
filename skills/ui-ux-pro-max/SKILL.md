---
name: ui-ux-pro-max
description: "Use when reviewing UI/UX quality, auditing accessibility, choosing color palettes, selecting font pairings, evaluating design systems, recommending chart types, applying style-specific patterns (glassmorphism, brutalism, etc.), or generating stack-specific implementation guidelines. Triggered by: UI review, UX audit, design system, accessibility check, component review, color palette, font pairing, style selection, chart recommendation, landing page design, responsive audit, dark/light mode. NEVER for building new UIs from scratch (use frontend-design), Figma-to-code translation (use figma-implement-design), applying preset themes (use theme-factory), cleaning AI-generated code (use deslop), CRO optimization (use page-cro)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# UI/UX Pro Max - Design Intelligence

## Scope Boundary

| Task | This Skill | Defer To |
|------|-----------|----------|
| Review/audit existing UI for quality issues | YES | -- |
| Generate design system recommendations (colors, fonts, style) | YES | -- |
| Accessibility audit (WCAG 2.1 AA) | YES | -- |
| Stack-specific implementation guidelines | YES | -- |
| Build a new UI from scratch | NO | frontend-design |
| Convert Figma designs to code | NO | figma-implement-design |
| Apply or switch preset themes | NO | theme-factory |
| Clean up AI-generated code slop | NO | deslop |
| Optimize page conversion rates | NO | page-cro |

## File Index

| Group | File | When to Load |
|-------|------|-------------|
| **Scripts** | `scripts/search.py` | Entry point -- run for all design system and domain searches |
| | `scripts/core.py` | Internal -- loaded by search.py automatically |
| | `scripts/design_system.py` | Internal -- loaded by search.py --design-system |
| **Style & Visual** | `data/styles.csv` | 50+ UI style definitions (glassmorphism, brutalism, etc.) |
| | `data/colors.csv` | Color palette database by product type and mood |
| | `data/icons.csv` | Icon library reference and selection guidance |
| | `data/prompts.csv` | AI prompt templates mapped to CSS keywords |
| **Typography** | `data/typography.csv` | 57 font pairings with personality matching |
| **Layout & Structure** | `data/landing.csv` | Landing page patterns (hero, pricing, social proof) |
| | `data/products.csv` | Product type to design style mapping |
| **Quality & Guidelines** | `data/ux-guidelines.csv` | 99 UX best practices and anti-patterns |
| | `data/ui-reasoning.csv` | Design reasoning rules engine |
| | `data/web-interface.csv` | Web interface accessibility guidelines |
| | `data/charts.csv` | Chart type recommendations by data shape |
| | `data/react-performance.csv` | React-specific performance guidelines |
| **Stack Guidelines** | `data/stacks/html-tailwind.csv` | Tailwind utilities, responsive, a11y (DEFAULT) |
| | `data/stacks/react.csv` | State, hooks, performance, patterns |
| | `data/stacks/nextjs.csv` | SSR, routing, images, API routes |
| | `data/stacks/vue.csv` | Composition API, Pinia, Vue Router |
| | `data/stacks/svelte.csv` | Runes, stores, SvelteKit |
| | `data/stacks/swiftui.csv` | Views, State, Navigation, Animation |
| | `data/stacks/react-native.csv` | Components, Navigation, Lists |
| | `data/stacks/flutter.csv` | Widgets, State, Layout, Theming |
| | `data/stacks/shadcn.csv` | shadcn/ui components, theming, forms |
| | `data/stacks/nuxtjs.csv` | Nuxt 3 SSR, auto-imports, composables |
| | `data/stacks/nuxt-ui.csv` | Nuxt UI component library patterns |

## Script Usage Decision

| Scenario | Command | Why |
|----------|---------|-----|
| NEW project needing full design direction | `search.py "<keywords>" --design-system -p "Name"` | Searches 5 domains in parallel, applies reasoning rules, returns complete system |
| Specific domain question (e.g., "luxury typography") | `search.py "<keywords>" --domain typography` | Targeted search within one data file |
| Stack implementation patterns | `search.py "<keywords>" --stack react` | Returns framework-specific best practices |
| Quick one-off UI review | Skip scripts -- apply Review Methodology directly | Faster than running searches for known patterns |

Available domains: `style`, `color`, `typography`, `landing`, `product`, `chart`, `ux`, `react`, `web`, `prompt`
Available stacks: `html-tailwind` (default), `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`

## UI Review Methodology

When asked to review or audit a UI, follow this sequence. Each pass catches different failure modes.

### Pass 1: Accessibility (WCAG 2.1 AA)

**Critical (blocks usage):**
- Contrast below 3:1 on any text or interactive element
- No keyboard navigation path through interactive elements
- Screen reader cannot parse page structure (missing landmarks, headings)
- Form inputs without programmatic labels

**Major (degrades experience):**
- Missing alt text on informational images
- No visible focus indicators on interactive elements
- Unlabeled icon-only buttons (missing aria-label)
- Error messages not associated with their fields

**Minor (improvement opportunity):**
- Color as the only status indicator (no icon or text backup)
- Animation without prefers-reduced-motion check
- Touch targets below 44x44px on mobile

### Pass 2: Visual Hierarchy

- Does the eye follow the intended path? (headline -> subhead -> CTA -> supporting)
- Is there ONE clear primary action per viewport?
- Are section boundaries clear without relying on color alone?
- Does whitespace group related elements and separate unrelated ones?

### Pass 3: Consistency Audit

- Spacing: Are gaps between elements using a consistent scale (4/8/12/16/24/32/48)?
- Color: Count unique color values -- more than 8 suggests palette drift
- Typography: Count unique font-size/weight combos -- more than 6 suggests scale drift
- Border radius: Are corners consistent? Mixing 4px and 8px randomly is a red flag
- Shadows: Is elevation consistent? (e.g., cards same level, modals higher)

### Pass 4: Interaction States

Every interactive element needs ALL of these:
- Default, Hover, Active, Focus, Disabled
- Loading state (for async actions)
- Error state (for form elements)
- Empty state (for lists, tables, search results)

### Pass 5: Responsive Audit

Test at 4 breakpoints: 375px (mobile), 768px (tablet), 1024px (laptop), 1440px (desktop)
- No horizontal scroll at any breakpoint
- Touch targets adequate on mobile
- Typography readable without zoom on mobile (min 16px body)
- Navigation pattern appropriate per breakpoint (hamburger on mobile, expanded on desktop)

## Design System Quick-Audit Checklist

When reviewing an existing design system or component library:

**Token Coverage** -- are these all defined as tokens (not raw values)?
- Colors (primary, secondary, neutral, semantic: success/warning/error/info)
- Spacing scale (4px base or 8px base, consistently applied)
- Typography scale (size + weight + line-height as named tokens)
- Shadows (elevation levels: sm, md, lg, xl)
- Border radii (none, sm, md, lg, full)

**Component Completeness** -- for each component, does it handle:
- All interaction states (default, hover, active, focus, disabled)
- Loading variant (skeleton or spinner)
- Error variant (with message slot)
- Size variants (sm, md, lg at minimum)
- Responsive behavior documented

**Documentation Quality:**
- Props listed with types, defaults, and constraints
- Usage guidelines (when to use vs. when NOT to use)
- Accessibility notes per component

## Common UI Review Findings

These are the most frequent issues found during reviews. Check for these first -- they cover 80% of problems.

| Finding | What to Look For | Fix |
|---------|-----------------|-----|
| Inconsistent spacing | Mixed px values (13px, 17px, 22px) instead of a scale | Adopt 4px or 8px base scale |
| Palette drift | More than 8 unique colors outside the design tokens | Audit with browser devtools, map to nearest token |
| Typography sprawl | More than 3 font sizes in a single section | Establish type scale, apply consistently |
| Missing states | No loading, error, or empty states | Add skeleton loaders, inline errors, empty illustrations |
| Div soup | Non-semantic HTML (nested divs with no roles) | Replace with nav, main, section, article, aside, header, footer |
| Invisible focus | No focus rings or outline:none without replacement | Add visible focus-visible styles |
| Layout shift | Elements jumping on hover (scale transforms, content reflow) | Use transform on non-layout properties, reserve space |
| Contrast failures | Light gray text on white, or dark gray on dark backgrounds | Test with contrast checker, minimum 4.5:1 for text |

## Rationalization Table

| Dimension | Reasoning |
|-----------|-----------|
| Why systematic passes? | Random "looks wrong" reviews miss 40-60% of issues. Sequential passes (a11y -> hierarchy -> consistency -> interaction -> responsive) ensure comprehensive coverage with no category skipped. |
| Why accessibility first? | Legal liability (ADA/WCAG lawsuits), largest user impact, and a11y issues often reveal deeper structural problems. Finding them first prevents rework. |
| Why token audit? | Raw values (colors, spacing, font sizes) scattered through code are the #1 cause of visual inconsistency. Tokenization is the fix. If tokens exist but aren't used, the design system is decoration. |
| Why count unique values? | Objective measurement beats subjective "it looks inconsistent." Counting color values (>8 = drift) and font combos (>6 = sprawl) gives actionable thresholds. |
| Why 4 breakpoints? | 375px (iPhone SE/min mobile), 768px (iPad), 1024px (laptop), 1440px (desktop) covers 95%+ of real traffic. Testing fewer misses tablet; testing more adds diminishing returns. |
| Why check all states? | Missing hover, focus, disabled, loading, error, or empty states are the most common component gap. Users encounter every state -- shipping without them creates dead-end UX. |

## Red Flags

1. "It works on my screen" -- no responsive testing performed, only desktop checked.
2. Skipping accessibility because "our users don't need it" -- 15-20% of users have some disability, plus SEO and legal implications.
3. Using outline:none globally without providing alternative focus indicators.
4. More than 3 z-index values defined ad-hoc without a documented scale.
5. Animations on layout properties (width, height, top, left) instead of transform/opacity.
6. Color-only error indication (red border but no icon, no text, no aria-invalid).
7. Placeholder text as the only label for form inputs (disappears on focus, invisible to screen readers).
8. Mixing icon libraries (Heroicons + Font Awesome + Material Icons in one project).

## NEVER

1. NEVER approve a UI review without testing keyboard navigation end-to-end.
2. NEVER recommend a color palette without verifying WCAG AA contrast ratios for text on background.
3. NEVER skip the empty state -- every list, table, and search result needs one.
4. NEVER use emojis as functional UI icons (decorative only, and sparingly).
5. NEVER deliver a design system recommendation without specifying the spacing scale base unit.
