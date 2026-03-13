# Design Token Extraction and Mapping

Load when extracting design tokens from Figma variables, mapping Figma tokens to a project's existing token system, implementing theme switching (light/dark mode) from Figma, or setting up a design token pipeline between Figma and code.

## Figma Variables to Code Tokens

### Token Extraction via MCP

The `get_variable_defs` MCP tool returns Figma variable collections. These are the design's source-of-truth tokens.

| Figma Variable Concept | Code Equivalent | Extraction Note |
|---|---|---|
| Variable collection | Token category (colors, spacing, typography) | Figma organizes variables into collections. Each collection maps to a token group in code. |
| Variable mode | Theme variant (light, dark, high-contrast) | Figma modes on a collection = theme variants. A `colors` collection with `light` and `dark` modes = two theme token sets. |
| Alias variable | Token reference | A Figma variable can reference another variable (`primary-500` -> `blue-500`). In code: `--color-primary: var(--color-blue-500)`. Preserve the reference chain. |
| Number variable | Spacing / sizing token | Figma stores spacing as unitless numbers. Add the unit in code: `8` -> `0.5rem` (if base is 16px) or `8px`. Match the project's unit convention. |
| Color variable | Color token | Figma stores colors as hex or RGBA. Map to project's color format (hex, rgb, hsl, oklch). |

### Token Naming Translation

Figma variable names rarely match project token names. Always build a mapping table.

| Figma Variable Name | Common Project Token Name | Mapping Rule |
|---|---|---|
| `colors/primary/500` | `--color-primary` or `$color-primary` | Figma uses `/` hierarchy. CSS uses `-` or nested objects in JS. |
| `colors/neutral/100` | `--color-gray-100` or `--bg-surface` | Figma may use "neutral" where the project uses "gray" or semantic names. |
| `spacing/md` | `--space-4` or `--spacing-md` | Figma may use t-shirt sizes (xs, sm, md) while the project uses numeric scale (1-12). Map by value, not by name. |
| `typography/heading-lg/font-size` | `--font-size-2xl` or `--heading-lg-size` | Typography tokens in Figma are nested (font-size, line-height, weight as separate variables). Some project systems compose these into a single type scale token. |
| `border-radius/lg` | `--radius-lg` or `--rounded-lg` | Direct mapping is common here. Verify the actual pixel values match. |

**Mapping process**:
1. Export Figma variables via `get_variable_defs`
2. List project's existing tokens (search for CSS custom properties or design token files)
3. Match by VALUE first (Figma `#3b82f6` = project `--color-primary` if values match)
4. Match by SEMANTIC INTENT second (Figma `colors/primary/500` likely maps to `--color-primary` even if hex values differ slightly)
5. Flag unmatched tokens for designer review

## Theme Implementation (Light/Dark Mode)

### Figma Modes to CSS Themes

Figma variable modes define how tokens change per theme. Implementation varies by project approach.

| Project Approach | Implementation | When to Use |
|---|---|---|
| CSS custom properties (recommended) | `:root { --bg: white; }` `.dark { --bg: #1a1a2e; }` | Any project. Most flexible. Supports runtime switching. |
| Tailwind dark mode | `dark:bg-gray-900` utility classes | Tailwind projects. Uses `class` strategy (toggle `.dark` on `<html>`) or `media` strategy (prefers-color-scheme). |
| CSS Modules with theme prop | `styles[theme].container` | React + CSS Modules projects. Less flexible, requires component re-render on theme change. |
| Styled-components ThemeProvider | `${({ theme }) => theme.colors.bg}` | Styled-components projects. Theme via React context. |
| Sass variables with mixin | `@include theme(dark) { background: $bg-dark; }` | Sass projects. Compile-time themes (not runtime switchable without build step). |

### Token Resolution for Themes

| Figma Structure | CSS Custom Properties |
|---|---|
| Collection: `colors`, Mode: `light` -> `surface: #ffffff` | `:root { --color-surface: #ffffff; }` |
| Collection: `colors`, Mode: `dark` -> `surface: #1a1a2e` | `.dark { --color-surface: #1a1a2e; }` |
| Collection: `colors`, Mode: `light` -> `text-primary: #111827` | `:root { --color-text-primary: #111827; }` |
| Collection: `colors`, Mode: `dark` -> `text-primary: #f9fafb` | `.dark { --color-text-primary: #f9fafb; }` |
| Alias: `button-bg` -> `primary/500` (both modes) | `--color-button-bg: var(--color-primary-500);` (alias resolves per theme) |

**Implementation order**:
1. Define primitive tokens (raw color values per theme)
2. Define semantic tokens as aliases (`--color-text-primary: var(--color-gray-900)`)
3. Theme switch only changes primitives; semantic tokens update automatically via reference chain

### Dark Mode Gotchas

| Gotcha | What Happens | Fix |
|---|---|---|
| Pure black (#000000) background | Causes eye strain and "halation" (white text blooming) on OLED screens | Use dark gray (#1a1a2e, #121212, #0f172a) instead of pure black. Figma designs sometimes use #000 -- verify with designer. |
| Inverting all colors | Simply flipping light/dark creates wrong contrast. A `gray-100` background in light mode should NOT become `gray-900` in dark mode -- it should become `gray-800` or `gray-850`. | Map each semantic token independently. Light `surface` (#fff) maps to dark `surface` (#1e1e2e), not to the "opposite" of the light value. |
| Shadows invisible in dark mode | Box shadows with black/transparent-black are invisible on dark backgrounds. | Replace shadow with subtle border (`1px solid rgba(255,255,255,0.1)`) or use lighter shadow color in dark mode. Some designs use glow effects instead. |
| Images too bright in dark mode | Light-background images look like glowing rectangles on dark backgrounds. | Apply `filter: brightness(0.85)` to images in dark mode, or use separate dark-mode image assets if available in Figma. |
| SVG icons hardcoded to black | SVG with `fill="#000"` or `fill="black"` disappears on dark backgrounds. | Use `fill="currentColor"` so icons inherit text color. Check every SVG asset from Figma MCP output. |
| User preference ignored | Hardcoded theme without respecting `prefers-color-scheme` | Default to user's OS preference: `@media (prefers-color-scheme: dark)`. Allow manual override that saves to localStorage. |

## Token File Format by Project Type

| Project Stack | Token File Location | Format | Example |
|---|---|---|---|
| CSS (any framework) | `tokens.css` or `variables.css` | CSS custom properties | `--color-primary: #3b82f6;` |
| Tailwind | `tailwind.config.js` -> `theme.extend` | JS object | `colors: { primary: { 500: '#3b82f6' } }` |
| Sass | `_variables.scss` or `_tokens.scss` | Sass variables | `$color-primary: #3b82f6;` |
| Styled-components | `theme.ts` or `theme.js` | JS/TS object | `{ colors: { primary: '#3b82f6' } }` |
| Design token standard (W3C) | `tokens.json` | DTCG format | `{ "color": { "primary": { "$value": "#3b82f6", "$type": "color" } } }` |

### Cross-Project Token Sync Patterns

| Pattern | Implementation | When to Use |
|---|---|---|
| Figma Tokens plugin export | Export Figma variables as JSON -> transform -> write to project token files | Teams using Tokens Studio (Figma plugin) with automated pipeline |
| Style Dictionary | Token JSON as source of truth -> build step generates CSS/JS/iOS/Android tokens | Multi-platform projects (web + mobile) needing consistent tokens |
| Manual extraction via MCP | `get_variable_defs` -> manually map to project tokens | One-time implementation or projects without a token pipeline |

**Priority**: If the project already has a token system, ALWAYS map Figma values to existing tokens. Never create a parallel token system. If 80% of Figma tokens map to existing project tokens, map those 80% and flag the remaining 20% as new tokens to discuss with the team.

## Contrast and Accessibility Verification

After token mapping, verify contrast ratios meet WCAG 2.1 AA:

| Element Combination | Minimum Contrast Ratio | How to Check |
|---|---|---|
| Body text on background | 4.5:1 | `text-primary` on `surface` in BOTH light and dark themes |
| Large text (18px+ or 14px+ bold) on background | 3:1 | Heading tokens on surface tokens |
| Interactive elements (buttons, links) | 3:1 against adjacent colors | Button background against page background, link text against surrounding text |
| Disabled state text | No minimum (intentionally low contrast) | But should still be readable enough to identify the element. Target 2:1 minimum. |
| Focus indicator | 3:1 against adjacent colors | Focus ring color against both the element and the surrounding background |

**Theme-specific contrast trap**: A color pairing that passes in light mode may fail in dark mode (or vice versa). Verify ALL token pairings in EVERY theme. Common failure: `primary-500` text passes on `white` background (light mode) but fails on `gray-800` background (dark mode).
