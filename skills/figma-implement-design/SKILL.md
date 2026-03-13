---
name: figma-implement-design
description: "Use when translating Figma designs into production code with pixel-perfect visual parity, implementing specific Figma frames or components from a URL, or validating implemented UI against Figma screenshots. Also use when the user provides a Figma URL with a node ID and asks to build or implement it. NEVER use for designing in Figma, modifying Figma files, general UI development without a Figma source, or Figma MCP setup troubleshooting (use figma skill)."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Implement Design

Translates Figma nodes into production code with 1:1 visual fidelity. Focuses on the code translation and validation -- for MCP tool usage, token mapping, and asset handling patterns, see the `figma` skill.

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Implementation procedure, framework translation basics, responsive adaptation, visual parity validation | Always (auto-loaded) |
| framework-translation-patterns.md | Detailed React-to-Vue/Svelte/Angular/vanilla conversion tables, CSS system translation (Tailwind to CSS Modules/Sass/styled-components), component library mapping (shadcn, MUI, Vuetify, Angular Material) | Load when the target project uses ANY framework other than React + Tailwind. Also load when the project uses a component library that needs mapping from MCP primitives. Do NOT load for React + Tailwind projects unless a component library mapping is needed. |
| responsive-implementation-gotchas.md | Figma auto-layout to CSS flexbox gaps, breakpoint mapping from Figma frame widths, typography responsiveness, image asset responsiveness, grid system translation, common responsive failures | Load when converting fixed-width Figma frames to responsive layouts. Also load when debugging layout breakage at specific viewport widths or handling mobile/tablet adaptation. Do NOT load for desktop-only implementations or simple single-component translations. |
| design-token-extraction.md | Figma variables to code tokens via get_variable_defs, token naming translation, light/dark theme implementation, dark mode gotchas, token file formats by stack, contrast verification | Load when extracting design tokens from Figma, implementing theme switching, or mapping Figma variables to a project's existing token system. Do NOT load for one-off color or spacing lookups (use SKILL.md Framework Translation Table). |

## Scope Boundary

| This Skill (figma-implement-design) | The figma Skill |
|---|---|
| Code translation: Figma output to project-stack code | MCP tool workflow: which tools to call, in what order |
| Visual parity validation against screenshots | Token mapping: `get_variable_defs` and project token alignment |
| Framework adaptation (React/Vue/Angular/plain HTML) | Asset handling: localhost sources, icon packages, Code Connect |
| Responsive behavior and accessibility compliance | MCP troubleshooting: connection issues, OAuth, truncation |

**When both apply**: Start with `figma` skill to fetch design context and assets via MCP, then switch to this skill for the code translation and validation steps.

## Implementation Procedure

1. **Parse the Figma URL**: Extract `fileKey` (segment after `/design/`) and `nodeId` (value of `node-id` param, convert `-` to `:`). For branch URLs, use `branchKey` as `fileKey`.
2. **Fetch design context**: Call `get_design_context(fileKey, nodeId)`. If response is truncated, call `get_metadata` first to map the layer tree, then re-fetch specific child nodes.
3. **Capture screenshot**: Call `get_screenshot(fileKey, nodeId)`. Keep this visible throughout implementation as the visual source of truth.
4. **Download assets**: Use localhost sources from MCP directly. Do not substitute with CDN URLs or icon packages.
5. **Translate to project stack**: Apply the Framework Translation table below. Treat MCP output as a design specification, not final code.
6. **Validate visually**: Compare implemented UI against the screenshot using the Validation Checklist. Fix discrepancies before marking complete.

## Framework Translation Table

The MCP returns React + Tailwind by default. Adapt every output to the project's actual stack.

| MCP Output | Translation Rule |
|---|---|
| Tailwind utility classes | Replace with project's CSS system (CSS modules, styled-components, design tokens, Sass, plain CSS) |
| Inline hex/rgb color values | Map to project color tokens; verify via `get_variable_defs` output |
| Generated `<button>`, `<input>`, `<div>` primitives | Replace with project's component library equivalents (shadcn/ui, MUI, Vuetify, custom) |
| Hardcoded `px` spacing values | Map to project spacing scale tokens where a match exists within 2px |
| React JSX | Convert to project framework: Vue SFC, Angular template, Svelte, plain HTML |
| Inline event handlers | Conform to project's state management and event handling patterns |
| Absolute positioning from Figma | Convert to flex/grid layout; Figma absolute positioning does not produce responsive code |

## Responsive Adaptation

Figma frames are fixed-width snapshots. The project's responsive system must be applied manually.

| Figma Signal | Responsive Implementation |
|---|---|
| Auto Layout (horizontal) | `display: flex; flex-direction: row` with `flex-wrap` at breakpoints |
| Auto Layout (vertical) | `display: flex; flex-direction: column`; stack order may change at breakpoints |
| Fixed-width frame (e.g., 1440px) | Max-width container with fluid behavior below the frame width |
| Absolute-positioned layer | Convert to relative positioning within a flex/grid parent |
| Multiple Figma frames at different widths | Map each to the project's closest breakpoint; implement responsive transitions between them |

**Rule**: If the Figma file only shows one frame width, implement it as the desktop view and apply the project's existing responsive patterns for tablet and mobile. If no responsive patterns exist, ask the user.

## Common Translation Errors

| Error | Cause | Prevention |
|---|---|---|
| Colors don't match despite using token names | Figma variable names rarely match project token names | Always run `get_variable_defs` and manually map variable names before writing styles |
| Generated code includes hidden layers | `get_design_context` returns all layers including hidden ones | Review the MCP output for invisible/hidden layers and exclude them from code |
| Component is too deeply nested | Figma component nesting creates deeply nested markup | Flatten by replacing nested primitives with existing project components from `get_code_connect_map` |
| Implementing the wrong variant | URL points to a component set (parent) not a specific variant | Verify the node ID points to the exact variant, not the component set |
| Spacing is inconsistent at different viewports | Figma uses fixed spacing; CSS needs responsive spacing | Use relative units (rem, %) or spacing tokens that scale, not hardcoded px values |
| Icons render as broken images | Used CDN or icon package instead of MCP-provided assets | Always use localhost asset URLs from MCP payload; never substitute external sources |

## Visual Parity Validation Checklist

Compare the implemented UI against the Figma screenshot before marking complete:

- [ ] **Layout**: Element positions, alignment, and spacing match within 2px tolerance
- [ ] **Typography**: Font family, size, weight, line height, and letter spacing match
- [ ] **Colors**: Background, text, border, and shadow colors match exactly (use color picker to verify)
- [ ] **Interactive states**: Hover, active, focus, and disabled states work as designed
- [ ] **Responsive behavior**: Scales correctly at standard breakpoints (if responsive frames exist in Figma)
- [ ] **Assets**: All icons and images render correctly using MCP-provided sources
- [ ] **Accessibility**: Proper semantic HTML, ARIA labels, keyboard navigation, contrast ratios meet WCAG 2.1 AA

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "The MCP output looks like working code, I'll use it directly" | MCP output is React + Tailwind regardless of project stack; using it directly creates framework inconsistency and ignores existing components |
| "Close enough is fine for spacing" | 4px spacing discrepancies compound across a layout; users perceive misalignment subconsciously even if they can't articulate it |
| "I'll skip the screenshot comparison" | Code that compiles correctly can still look visually wrong; the screenshot is the source of truth, not the design context JSON |
| "Absolute positioning from Figma is fine" | Figma auto-layout translates to flex/grid, but manually positioned Figma layers produce fixed-position CSS that breaks on any viewport other than the original frame width |
| "I'll handle responsive later" | Without responsive consideration during initial translation, the layout structure often needs rearchitecting; build responsiveness into the first implementation |
| "The project doesn't have a component for this, so I'll create one from scratch" | Check `get_code_connect_map` first; creating duplicates of existing components causes divergence and maintenance debt |

## Red Flags

- Implementing from a Figma URL without first calling `get_design_context` and `get_screenshot`
- Using Tailwind classes in a project that uses a different CSS system
- Creating new UI components when `get_code_connect_map` returns a matching existing component
- Hardcoding pixel values instead of using project spacing/typography tokens
- Skipping the Visual Parity Validation Checklist
- Implementing only the desktop view without considering responsive behavior
- Replacing MCP-provided localhost asset URLs with external CDN links or icon package imports

## NEVER

- Use MCP output verbatim as production code without adapting to the project's framework and component library
- Import external icon packages when the MCP payload provides the asset at a localhost URL
- Mark implementation as complete without comparing against the `get_screenshot` output
- Ignore hidden layers in the MCP design context -- they should not appear in the implementation
- Hardcode Figma hex color values when the project has a token system -- map colors to tokens
