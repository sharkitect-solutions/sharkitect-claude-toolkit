---
name: figma
description: "Use when implementing UI from Figma designs, translating Figma nodes to production code, fetching design context or screenshots via Figma MCP, or troubleshooting Figma MCP integration. NEVER use for designing in Figma, non-Figma design tools, or creating designs from scratch without a Figma source."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Figma MCP Skill

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| `references/figma-mcp-config.md` | Server config snippet, env var setup, OAuth troubleshooting | MCP not connecting, token errors, first-time setup |
| `references/figma-tools-and-prompts.md` | Full tool catalog with signatures, prompt patterns, framework overrides | Choosing which MCP tool to call, generating non-React output |

## Implementation Workflow

Execute these steps in order. Do not skip or reorder.

1. **Fetch design context** -- call `get_design_context` with the exact Figma node link.
2. **Handle truncation** -- if response is truncated or oversized, call `get_metadata` first to map the layer tree, then re-call `get_design_context` on only the required sub-nodes.
3. **Get variable definitions** -- call `get_variable_defs` to surface the color, spacing, and typography tokens used in the selection. Map these to the project's token system before writing code.
4. **Get screenshot** -- call `get_screenshot` for a visual reference. Keep it open throughout implementation.
5. **Check code connect map** -- call `get_code_connect_map` to find existing component mappings before writing new components. Reuse mapped components unconditionally.
6. **Implement and validate** -- translate to the project's stack (see Framework Adaptation Rules), then compare final UI against the screenshot for 1:1 parity.

### Edge Cases

| Situation | Action |
|-----------|--------|
| `get_design_context` returns partial or empty data | Verify the link points to the exact frame or layer, not the file root. Re-extract node ID from the URL. |
| Design tokens in Figma conflict with project tokens | Project tokens win. Adjust spacing or sizes minimally to preserve visual parity. Document the override. |
| Asset missing from localhost MCP payload | Do not substitute with external CDN or icon package. Re-fetch the node; if still missing, flag to the user before continuing. |
| Node is a FigJam diagram | Use `get_figjam` instead of `get_design_context`. |
| Output is generic and ignores project stack | Re-state the project framework in the prompt: "generate using components from `src/components/ui` styled with [system]". See `references/figma-tools-and-prompts.md` for prompt patterns. |
| MCP server not reachable | Load `references/figma-mcp-config.md` for env var verification and OAuth troubleshooting steps. |

## Framework Adaptation Rules

The MCP outputs React + Tailwind by default. Treat it as a design specification, not final code.

| Figma MCP Output | Project Adaptation Rule |
|-----------------|------------------------|
| Tailwind utility classes | Replace with the project's preferred utilities or design-system tokens |
| Inline color values (hex or rgb) | Replace with the project's color tokens confirmed via `get_variable_defs` |
| Generated primitive elements (button, input, icon wrapper) | Replace with existing project components; never duplicate functionality |
| Hardcoded spacing or size values | Replace with spacing or typography scale tokens where a match exists |
| Data-fetch or state logic | Conform to existing repo patterns; do not introduce new patterns |
| Framework (React default) | Override via prompt: "generate in Vue / plain HTML / iOS" -- see `references/figma-tools-and-prompts.md` |

## Asset Handling

- The MCP server provides assets (images, SVGs) at a localhost endpoint.
- If the MCP returns a localhost source for an image or SVG: use it directly as-is.
- Do not import new icon packages. All assets must come from the Figma MCP payload.
- Do not create placeholders when a localhost source is provided.
- The server is link-based: the client extracts the node ID from the URL; it does not browse the Figma page.

## Common Pitfalls

Issues that arise specifically during Figma-to-code translation that are not obvious:

- **Token naming mismatch**: Figma variable names rarely match project token names. Always run `get_variable_defs` and manually map variable names to project tokens before writing styles -- do not assume names will match.
- **Variant selection error**: Figma links that point to a component set (parent) rather than a specific variant return all variants in the design context. Always link to the exact variant node to get targeted output.
- **Absolute-positioned layers**: Figma auto-layout nodes translate well; manually positioned layers in Figma produce absolute CSS. These must be manually converted to the project's layout system (flex or grid) to remain responsive.
- **Hidden layers included in output**: `get_design_context` includes all layers, including hidden ones. Review generated code for invisible elements that should not be rendered.
- **Component nesting depth**: Deeply nested Figma components can produce deeply nested generated markup. Flatten using existing project components wherever `get_code_connect_map` confirms a match.
- **Figma breakpoints vs. project breakpoints**: Figma frames are fixed-width snapshots. The project's responsive breakpoints must be applied manually; do not assume the generated code handles responsiveness.

## Rationalization Table

| Decision | Rationale |
|----------|-----------|
| Run `get_design_context` before any implementation | Skipping causes implementation drift; the node ID alone is insufficient to infer layout, tokens, or constraints |
| Use `get_metadata` only when context is truncated | Calling it on every node adds unnecessary latency; it exists to work around size limits, not as a default step |
| Run `get_variable_defs` before mapping tokens | Variable names in Figma and in the project rarely match; manual mapping from this output prevents silent token mismatches |
| Project tokens override Figma tokens | Design-system consistency outweighs pixel-perfect Figma fidelity; minor visual deviations are acceptable when tokens are correctly applied |
| Use localhost asset sources directly | MCP serves assets at a stable local endpoint during the session; fetching from CDN introduces unnecessary external dependencies |
| Check `get_code_connect_map` before creating new components | Reusing mapped components prevents sprawl; duplicate implementations diverge over time and create maintenance debt |

## Red Flags

- Implementing from a Figma link without first calling `get_design_context`
- Replacing or supplementing MCP-provided localhost assets with external CDN URLs or icon packages
- Creating new UI components when `get_code_connect_map` returns a match for the node
- Applying Figma token values directly as hardcoded CSS values instead of mapping to project tokens
- Skipping the `get_screenshot` validation step before marking implementation complete
- Linking to the file root or a component set instead of the specific frame or variant node
- Introducing new state management or data-fetch patterns that do not match existing repo conventions

## NEVER

- Design or modify anything inside Figma using this skill
- Use this skill for non-Figma design tools (Sketch, Framer, Figma Slides, etc.)
- Create UI from scratch without a Figma source node to reference
- Import external icon packages when the MCP payload already provides the asset
- Mark a Figma-to-code task complete without validating against the `get_screenshot` output
