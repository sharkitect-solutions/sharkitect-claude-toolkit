---
name: canvas-design
description: "Use when creating visual art, poster design, programmatic canvas art, PDF/PNG visual compositions, design philosophy-driven artwork, or abstract visual design. NEVER for static page layouts or component design (use frontend-design). NEVER for applying preset theme styles or design tokens (use theme-factory). NEVER for presentation slides (use pptx). NEVER for implementing Figma designs in code (use figma-implement-design)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

## File Index

| Path | Contents |
|------|----------|
| `canvas-fonts/` | 30 Google Font families (.ttf + OFL licenses): display, serif, sans, mono, handwritten, pixel categories. Use for all typography in canvas work. |

## Scope Boundary

| Request | This skill? | Instead use |
|---------|-------------|-------------|
| Create a poster, visual art piece, or abstract composition | YES | -- |
| Design philosophy for visual expression | YES | -- |
| PDF/PNG with artistic layout and minimal text | YES | -- |
| Multi-page visual storytelling (coffee-table book style) | YES | -- |
| Static webpage layout or UI component design | NO | frontend-design |
| Apply theme tokens, color schemes, or design systems | NO | theme-factory |
| Build a slide deck or presentation | NO | pptx |
| Translate a Figma mockup into working code | NO | figma-implement-design |
| Icon design or SVG illustration | NO | frontend-design |

## Two-Phase Process

Every canvas piece follows two phases. Do not skip or merge them.

**Phase 1 -- Design Philosophy (.md file):** Write a 4-6 paragraph manifesto for an art movement. This is NOT a brief -- it is an aesthetic worldview that guides visual expression. The philosophy must be generic enough to stand alone (no mention of the specific subject), yet specific enough in its visual language to produce a coherent piece.

**Phase 2 -- Canvas Expression (.pdf or .png file):** Interpret the philosophy visually. The result is 90% design, 10% essential text. Before starting Phase 2, identify the subtle reference (see below).

## Design Philosophy Architecture

A philosophy has three components:

| Component | Format | Purpose |
|-----------|--------|---------|
| Movement name | 1-2 words | Anchors the aesthetic identity |
| Core philosophy | 1 sentence | The conceptual thesis |
| Visual expression | 3-5 sentences | How the thesis manifests in form, space, color, typography, composition |

### Philosophy Archetypes

**"Concrete Poetry"** -- Communication through monumental form and bold geometry.
Visual: Massive color blocks, sculptural typography (huge single words, tiny labels), Brutalist spatial divisions, Polish poster energy meets Le Corbusier. Visual weight and spatial tension carry meaning.

**"Chromatic Language"** -- Color as the primary information system.
Visual: Geometric precision where color zones create meaning. Minimal sans-serif labels let chromatic fields communicate. Josef Albers' interaction meets data visualization. Information encoded spatially and chromatically.

**"Analog Meditation"** -- Quiet visual contemplation through texture and breathing room.
Visual: Paper grain, ink bleeds, vast negative space. Photography and illustration dominate. Japanese photobook aesthetic. Typography whispered -- small, restrained, serving the visual.

**"Organic Systems"** -- Natural clustering and modular growth patterns.
Visual: Rounded forms, organic arrangements, color from nature through architecture. Information through visual diagrams, spatial relationships, iconography. Text only as floating key labels.

**"Geometric Silence"** -- Pure order and restraint.
Visual: Grid-based precision, bold photography or stark graphics, dramatic negative space. Swiss formalism meets Brutalist material honesty. Small essential text, large quiet zones.

**"Metabolist Grid"** -- Modular repetition generating emergent complexity.
Visual: Repeating units that shift incrementally across the canvas -- rotation, scale, hue. The system IS the art. Inspired by Metabolist architecture (Kurokawa, Tange) and Sol LeWitt's wall drawings. Clinical labeling of the system's parameters.

**"Tectonic Collage"** -- Layered fragments creating geological depth.
Visual: Overlapping planes with visible edges, torn-paper textures, mixed media illusion (photo + vector + type). Depth through opacity and overlap, not perspective. David Carson meets Robert Rauschenberg.

**"Signal Noise"** -- Tension between data clarity and visual interference.
Visual: Clean data visualization forms (grids, axes, plot points) disrupted by glitch, grain, or hand-drawn marks. The collision between precision and entropy. Edward Tufte meets Ryoji Ikeda.

## Canvas Composition Decision Matrix

| Visual intent | Composition | Typography role | Color approach | Best archetypes |
|---------------|-------------|-----------------|----------------|-----------------|
| Monumental / Brutalist | Massive asymmetric blocks, extreme scale contrast | Sculptural -- type IS architecture | 2-3 color max, high saturation | Concrete Poetry, Tectonic Collage |
| Contemplative / Minimal | Vast negative space, single focal point | Whispered -- small, peripheral | Muted, desaturated, near-monochrome | Analog Meditation, Geometric Silence |
| Systematic / Diagrammatic | Strict grid, modular repetition | Clinical labels, small mono | Controlled palette, functional color | Metabolist Grid, Signal Noise |
| Organic / Fluid | Flowing forms, asymmetric balance | Integrated into forms, hand-placed | Nature-derived, gradients allowed | Organic Systems, Tectonic Collage |
| Kinetic / Dynamic | Diagonal tension, implied motion | Bold, angled, overlapping | High contrast, complementary pairs | Signal Noise, Concrete Poetry |
| Atmospheric / Textural | Layered surfaces, depth through grain | Embossed or debossed effect | Tonal range within one hue family | Analog Meditation, Tectonic Collage |

## Font Selection Guide

Fonts are in `./canvas-fonts/`. Load specific weights as needed.

### Display (headline impact, never body text)
| Font | Character | Best for |
|------|-----------|----------|
| Boldonse | Heavy, expressive slab | Brutalist posters, single-word statements |
| EricaOne | Ultra-bold condensed | Monumental type, vertical stacking |
| BigShoulders | Industrial condensed, 2 weights | Event posters, mechanical aesthetic |

### Serif (editorial elegance, body or accent)
| Font | Character | Best for | Pairs with |
|------|-----------|----------|------------|
| CrimsonPro | Classical proportions, 3 weights | Long-form elegance, literary feel | InstrumentSans, DMMono |
| Lora | Warm calligraphic curves, 4 weights | Organic warmth, approachable formality | WorkSans, Outfit |
| LibreBaskerville | Sturdy transitional | Authoritative body text | InstrumentSans |
| YoungSerif | Chunky contemporary | Display-sized headings, friendly weight | Outfit, BricolageGrotesque |
| Gloock | High-contrast Didone | Fashion, luxury, editorial covers | Jura, SmoochSans |
| IBMPlexSerif | Technical precision, 4 weights | Data-adjacent design, systematic work | IBMPlexMono, InstrumentSans |
| Italiana | Thin elegant Didone | Minimal luxury, whispered headings | PoiretOne, Jura |
| InstrumentSerif | Sharp contemporary, 2 weights | Modern editorial, refined accent | InstrumentSans |

### Sans-serif (modern, versatile)
| Font | Character | Best for | Pairs with |
|------|-----------|----------|------------|
| InstrumentSans | Clean geometric, 4 weights | Primary workhorse, labels, body | InstrumentSerif, CrimsonPro |
| Outfit | Rounded geometric, 2 weights | Friendly modern, tech-adjacent | Lora, YoungSerif |
| WorkSans | Humanist, 4 weights | Body text, readable at any size | Lora, IBMPlexSerif |
| BricolageGrotesque | Quirky grotesque, 2 weights | Personality-driven, editorial play | YoungSerif, CrimsonPro |
| ArsenalSC | Small-caps proportions | Labeling, systematic reference markers | CrimsonPro, DMMono |
| Jura | Light geometric, 2 weights | Futuristic, scientific, airy | Gloock, Italiana |
| SmoochSans | Soft rounded | Playful, approachable branding | Gloock, Lora |
| NationalPark | NPS-inspired, 2 weights | Nature themes, outdoor aesthetics | LibreBaskerville |
| PoiretOne | Art Deco thin | Decorative headlines, 1920s-1930s revival | Italiana, CrimsonPro |

### Monospace (technical, systematic)
| Font | Character | Best for |
|------|-----------|----------|
| DMMono | Compact, friendly | Code aesthetics, clean labels |
| GeistMono | Modern, crisp, 2 weights | Developer culture, tech minimalism |
| IBMPlexMono | Corporate technical, 2 weights | Data visualization labels, clinical |
| JetBrainsMono | Developer standard, 2 weights | Terminal aesthetics, code art |
| RedHatMono | Open-source character, 2 weights | Linux/open-source culture pieces |
| Silkscreen | Bitmap/pixel | Retro computing, 8-bit nostalgia |
| Tektur | Geometric tech, 2 weights | Futuristic displays, HUD aesthetic |

### Specialty
| Font | Character | Best for |
|------|-----------|----------|
| NothingYouCouldDo | Handwritten casual | Personal touch, organic contrast with geometric layouts |
| PixelifySans | Pixel grid | Retro gaming, digital nostalgia, glitch art |

## Subtle Reference Integration

Before canvas creation, identify the conceptual DNA from the user's request. This reference is embedded INTO the art -- never announced.

| Reference depth | Technique | Example |
|-----------------|-----------|---------|
| Literal shape | Silhouette or outline abstracted into composition geometry | Mountain request -> triangular forms dominating the grid |
| Color association | Palette derived from subject's visual identity | Ocean request -> deep blue-green tonal range |
| Structural metaphor | Composition mimics subject's inherent structure | Music request -> visual rhythm through repeating elements |
| Cultural symbol | Iconographic shorthand woven into pattern | Japanese request -> circular motifs (enso), asymmetric balance |
| Emotional temperature | Overall mood calibrated to subject's feeling | Loss request -> descending forms, desaturated, heavy lower third |

The test: someone familiar with the subject feels it intuitively. Everyone else simply experiences a strong abstract composition. Like a jazz musician quoting another song -- only those who know catch it.

## Canvas Execution Rules

1. **Boundary discipline**: Nothing touches or overlaps canvas edges. Every element has breathing room. Check margins before finalizing.
2. **Text economy**: Text is a visual element, not content delivery. If a word doesn't serve the composition spatially, cut it.
3. **Font variety**: Use 2-3 fonts minimum from `./canvas-fonts/`. Typography is part of the art -- never default system fonts.
4. **Scientific-artifact quality**: Treat the piece as though documenting an imaginary discipline. Dense accumulation of marks, repeated elements, or layered patterns that build meaning through patient repetition and reward sustained viewing. Sparse clinical labels and reference markers suggest this could be a diagram from an unknown field.
5. **Sophistication floor**: Even for playful or irreverent subjects, maintain museum-quality execution. Punk energy expressed through professional craft, not amateur shortcuts.
6. **Single pass, then refine**: Create the full composition, then do one refinement pass. The refinement pass improves what exists -- it never adds new elements. Ask: "How do I make what is here more cohesive?" not "What should I add?"

## Multi-Page Extension

When requested, treat page 1 as the opening of a visual narrative. Subsequent pages are variations on the philosophy -- same DNA, distinct expression. Each page should feel like turning through a monograph: recognizably part of the same body of work, but never repetitive. Bundle as single PDF or multiple PNGs.

## Rationalization

Before presenting final output, verify:

| Check | Question |
|-------|----------|
| Philosophy-canvas alignment | Does the canvas faithfully express the written philosophy's visual language? |
| Reference subtlety | Would someone unfamiliar with the subject still find the piece compelling on purely visual terms? |
| Text minimalism | Is every word earning its place spatially? Could any text be removed without losing composition strength? |
| Font intentionality | Are font choices driven by the philosophy, not convenience? Do pairings create visual tension or harmony deliberately? |
| Boundary compliance | Are all elements contained within canvas margins with breathing room? Zero overlaps, zero edge-touching? |
| Craft standard | Does this look like it came from a senior designer's portfolio, not a template or AI generator? |

## Red Flags -- Stop and Reassess

1. More than 30% of canvas area occupied by text blocks -- this is a document, not art
2. Using system default fonts instead of canvas-fonts/ library
3. Philosophy reads like a creative brief ("The poster should have...") instead of an aesthetic manifesto
4. Literal depiction of the subject rather than abstract visual interpretation
5. Symmetric centered layout with no spatial tension -- defaults to "corporate brochure" feel
6. Adding decorative elements during refinement pass instead of tightening existing composition
7. Color palette exceeding 5 distinct hues without deliberate philosophical justification
8. Typography all set at similar sizes -- no scale contrast creating visual hierarchy

## NEVER

1. Never copy or directly reference a specific living artist's recognizable style -- create original philosophies
2. Never output text-heavy layouts disguised as "design" -- if it reads like a document, it failed
3. Never use Lorem Ipsum or placeholder text -- every word on canvas must be intentional
4. Never skip the design philosophy phase and jump straight to canvas creation
5. Never add "fun filters" or novelty effects (lens flare, drop shadows, gradients-for-decoration) -- every visual choice must serve the philosophy
