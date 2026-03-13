---
name: theme-factory
description: "Use when applying visual themes (colors, fonts) to slides, documents, reports, or HTML pages, or when creating custom color/font palettes for any artifact. NEVER use for content creation, layout design, or choosing between artifact types."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Theme Factory

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| SKILL.md | Application workflow, theme catalog, selection guide, accessibility, custom theme procedure | Always (auto-loaded) |
| color-theory-applied.md | Color harmony systems, cultural color meanings (6 regions), color blindness adaptation, contrast optimization beyond WCAG, color psychology in business, dark mode derivation | When creating custom themes, adapting themes for specific cultures/industries, or troubleshooting color issues |
| typography-pairing-guide.md | Font classification (10 types), pairing strategies (concordance/complement/contrast), x-height matching, web font performance budget, readability research, fallback stacks | When selecting fonts for custom themes, evaluating pairings, or troubleshooting readability |
| theme-application-patterns.md | Cross-artifact application rules (slides/docs/HTML/reports/emails), consistency checklist, context adaptation, chart theming, common failures, brand guideline integration, testing protocol | When applying themes to specific artifact types or troubleshooting inconsistent application |
| theme-showcase.pdf | Visual preview of all 10 themes | Always -- show to user before asking for choice |
| themes/*.md | Individual theme color/font specs (10 themes) | When user selects a specific theme |

## Scope Boundary

| This Skill Handles | Defer To |
|---|---|
| Color palette selection and application | canvas-design (programmatic visual art and composition) |
| Typography pairing and font selection | frontend-design (full frontend visual design systems) |
| Theme consistency across artifacts | figma-implement-design (Figma-to-code translation) |
| WCAG contrast verification | ui-ux-pro-max (comprehensive UI/UX review methodology) |
| Custom theme creation from mood/reference words | copywriting (brand voice and messaging, not visual identity) |
| Dark mode derivation from light themes | scroll-experience (scroll-based interaction patterns) |

## Application Workflow

1. **Show showcase**: Display `theme-showcase.pdf` — do not modify it, show only for viewing.
2. **Ask for choice**: Ask the user which theme to apply.
3. **Wait for selection**: Get explicit confirmation of the chosen theme.
4. **Read theme file**: Load the corresponding file from `themes/` for the full color/font spec.
5. **Apply consistently**: Apply the theme's colors and fonts throughout the entire artifact, maintaining visual identity across all sections.

## Available Themes

| # | Theme | Visual Identity | Best For |
|---|-------|----------------|---------|
| 1 | **Ocean Depths** | Professional, calming maritime blues | Corporate reports, finance, consulting |
| 2 | **Sunset Boulevard** | Warm, vibrant sunset oranges/pinks | Marketing, consumer brands, events |
| 3 | **Forest Canopy** | Natural, grounded earth tones | Sustainability, wellness, environmental |
| 4 | **Modern Minimalist** | Clean, contemporary grayscale | Tech startups, design agencies, SaaS |
| 5 | **Golden Hour** | Rich, warm autumnal amber/gold | Luxury brands, hospitality, premium |
| 6 | **Arctic Frost** | Cool, crisp winter whites/blues | Healthcare, science, data analytics |
| 7 | **Desert Rose** | Soft, sophisticated dusty pinks/taupes | Fashion, beauty, lifestyle, editorial |
| 8 | **Tech Innovation** | Bold, modern electric accents | Developer tools, AI, engineering |
| 9 | **Botanical Garden** | Fresh, organic greens/florals | Education, nonprofits, food/beverage |
| 10 | **Midnight Galaxy** | Dramatic, cosmic deep purples/blacks | Entertainment, gaming, creative agencies |

## Theme Selection Guide

Match the theme to the audience and artifact type:

- **Formal / executive audience**: Ocean Depths, Modern Minimalist, Arctic Frost
- **Creative / consumer audience**: Sunset Boulevard, Desert Rose, Botanical Garden
- **Technical / data-heavy content**: Tech Innovation, Modern Minimalist, Arctic Frost
- **Emotionally resonant / storytelling**: Midnight Galaxy, Golden Hour, Sunset Boulevard
- **Neutral / all-purpose fallback**: Modern Minimalist (safe across all contexts)

## Accessibility and Contrast

When applying any theme, verify readability:
- **Body text on background**: minimum 4.5:1 contrast ratio (WCAG AA)
- **Large headers on background**: minimum 3:1 contrast ratio (WCAG AA)
- **Never place light-on-light or dark-on-dark** — if the theme spec produces a contrast failure, substitute the nearest accent color that passes.
- Decorative elements (dividers, icons, background shapes) are exempt from contrast requirements.

## Create a Custom Theme

When none of the 10 preset themes fit:

1. **Gather inputs**: Ask for 1-3 reference words or a mood (e.g., "bold and futuristic", "calm and trustworthy").
2. **Choose a color strategy**:
   - *Complementary* (opposite on color wheel) — high contrast, energetic
   - *Analogous* (adjacent on color wheel) — harmonious, cohesive
   - *Triadic* (three equidistant hues) — vibrant, balanced
3. **Define the palette**: Primary, secondary, accent, background, and text hex codes.
4. **Pair fonts**: One display/header font + one readable body font.
5. **Name the theme**: A descriptive name that evokes the mood (same style as the 10 presets).
6. **Show for review**: Present the custom theme for user approval before applying.
7. **Apply**: Follow the standard Application Workflow above.

## Theme Diagnosis

When a themed artifact looks wrong but you cannot pinpoint why, check these signals in order (first match wins):

| Signal | Root Cause | Fix |
|---|---|---|
| "Something feels off" but colors are correct | 60-30-10 ratio violated -- accent overused or dominant underused | Measure surface area. Reallocate to 60% dominant, 30% secondary, 10% accent. |
| Text is technically readable but uncomfortable | Contrast is at WCAG minimum (4.5:1) but not comfortable, or pure black on pure white causing halation | Boost contrast to 5.5:1+ for body text. Replace #000/#fff with #1a1a1a/#fafafa. |
| Headers and body text feel "same-ish" | Font pairing lacks contrast -- same classification or insufficient size ratio | Switch to contrast pairing (serif + sans). Ensure 1.3-1.5x size ratio between heading levels. |
| Theme looks professional on screen, amateurish in print | Screen colors don't translate to print -- bright accents become muddy, dark backgrounds waste ink | For printable artifacts: white backgrounds, dark text, accents only in headers and borders. |
| Theme works for first half, falls apart in second half | Partial application -- copy-paste from unthemed source introduced default styling | Re-apply theme to entire artifact. Check for source formatting overrides in pasted sections. |
| Dark mode looks washed out or garish | Theme colors not adapted for dark context -- saturated colors on dark backgrounds cause eye strain | Desaturate brand colors 10-15%, lighten body text to #e0e0e0, use #121212 not #000000. |
| Charts and data visualizations clash with theme | Chart colors are default (Excel/Sheets blue, orange, gray) not theme-derived | Replace chart series colors with theme primary, secondary, accent, then tinted variants. |

## Effort Calibration

Scale the theming effort to match the artifact's stakes and complexity:

| Artifact Scale | Theming Approach | What to Skip |
|---|---|---|
| Quick artifact (1-3 pages, internal) | Apply preset theme as-is. Verify contrast on text. Done. | Skip: custom fonts, dark mode derivation, print testing, brand alignment |
| Standard artifact (4-15 pages, shared externally) | Apply preset or simple custom. Full contrast check. Consistency audit across all sections. | Skip: cultural color audit, font performance budget, chart color derivation (if no charts) |
| High-stakes artifact (16+ pages, executive/client-facing) | Full theme treatment: contrast verification, consistency audit, print test, brand alignment check. Load all 3 companion files for guidance. | Skip nothing. Test with grayscale, squint, 5-second, and dark mode protocol. |
| Multi-artifact campaign (slides + doc + email + web) | Define theme once with full spec. Apply consistently across all formats. Cross-format consistency check (see theme-application-patterns.md). | Skip: nothing. Use the cross-format consistency table for alignment audit. |

## Rationalization Table

| Decision | Rationale |
|----------|-----------|
| Show PDF before asking | User cannot make an informed choice without seeing the visual output |
| Read only the selected theme file | Loading all 10 theme files at once wastes context; load on-demand |
| Wait for explicit confirmation | Applying the wrong theme wastes user time and creates rework |
| Apply theme consistently across all sections | Partial theming looks unfinished and undermines professional quality |
| Check contrast after applying | Theme spec colors may render differently in different artifact renderers |
| Custom theme follows same workflow | Consistency reduces errors; same review-then-apply loop for all themes |

## Red Flags

- [ ] Applying a theme without first showing `theme-showcase.pdf`
- [ ] Asking the user to describe colors verbally instead of showing visual options
- [ ] Applying theme colors inconsistently (e.g., only headers, missing backgrounds)
- [ ] Loading all 10 theme files when only one was selected
- [ ] Skipping the user confirmation step before applying
- [ ] Using light text on a light background (contrast failure)
- [ ] Confusing "apply theme" with "redesign layout" — themes are colors and fonts only
- [ ] Creating a custom theme without presenting it for review first

## NEVER

- NEVER modify or annotate `theme-showcase.pdf` — display it read-only
- NEVER apply a theme before the user confirms their selection
- NEVER use theme application to alter content, layout, or artifact structure
- NEVER skip contrast verification on custom themes
- NEVER guess a theme preference — always ask explicitly
