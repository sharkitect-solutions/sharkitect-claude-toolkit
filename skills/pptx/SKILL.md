---
name: pptx
description: "Use when creating new PowerPoint presentations from scratch, editing existing .pptx files, working with slide templates, extracting or replacing slide text, analyzing slide layouts, or generating thumbnail grids. Use when the user mentions .pptx, PowerPoint, slides, or presentations. NEVER for PDF-only workflows, slide conversion to images as the primary goal, or reading presentation text when markitdown alone suffices."
license: Proprietary. LICENSE.txt has complete terms
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# PPTX Creation, Editing, and Analysis

## File Index

| File | Purpose |
|---|---|
| `html2pptx.md` | MANDATORY read before creating presentations from scratch |
| `ooxml.md` | MANDATORY read before editing existing presentations |
| `scripts/html2pptx.js` | Converts HTML slides to PowerPoint |
| `ooxml/scripts/unpack.py` | Unpacks .pptx to editable XML directory |
| `ooxml/scripts/validate.py` | Validates XML after edits |
| `ooxml/scripts/pack.py` | Repacks edited XML directory to .pptx |
| `scripts/thumbnail.py` | Generates thumbnail grid images from presentations |
| `scripts/rearrange.py` | Duplicates, reorders, and deletes slides from a template |
| `scripts/inventory.py` | Extracts all text shapes and properties to JSON |
| `scripts/replace.py` | Applies text replacements from JSON to a working presentation |

---

## Rationalization Table

| Rule | Why It Exists |
|---|---|
| Read html2pptx.md in full before creating | The library has non-obvious constraints on dimensions, element ordering, and gradient handling that cause silent layout errors if skipped |
| Read ooxml.md in full before editing | OOXML relationship files must stay consistent; editing slide XML without understanding relationships corrupts the file |
| Validate immediately after each XML edit | OOXML errors are cumulative -- a single bad relationship reference makes the entire file unreadable in PowerPoint |
| Rasterize gradients and icons to PNG before HTML | html2pptx renders via headless browser; CSS gradients and SVG icons frequently produce corrupt or invisible output when converted |
| State design approach before writing code | Forces intentional palette and layout choices before code structure locks them in; eliminates rework caused by unsatisfying visual results |
| Use thumbnail.py for visual validation | Text cutoff, overlap, and contrast failures are invisible in code and only caught visually |
| Two-column layout preferred for charts/tables | Vertically stacked charts below text produce compressed, unreadable layouts at standard slide dimensions |
| Shapes not in replacement JSON are auto-cleared | replace.py clears ALL inventory shapes before applying replacements; omitting a shape removes its text entirely, which is intentional behavior |

---

## Red Flags

- Skipping the mandatory full reads of `html2pptx.md` or `ooxml.md`
- Setting line or offset limits when reading mandatory reference files
- Referencing shapes in `replacement-text.json` without first confirming they exist in `text-inventory.json`
- Using slide indices without confirming 0-based counting against the actual template count
- Placing a chart or table below text in a single column layout
- Adding bullet symbols (-, *, -) manually when `"bullet": true` handles them automatically
- Editing XML files without running validate.py immediately after
- Using CSS gradients or inline SVG icons in HTML slides without rasterizing them first via Sharp

---

## NEVER

- NEVER place charts or tables below text in a single-column vertical stack -- use two-column or full-slide layouts
- NEVER set range limits when reading `html2pptx.md`, `ooxml.md`, `template-content.md`, or `text-inventory.json`
- NEVER add bullet symbols (-, *, -) to text strings when `"bullet": true` is set -- they are added automatically
- NEVER reference a shape in replacement JSON before verifying it exists in the inventory output
- NEVER use a three-column layout when you only have two content items
- NEVER skip validate.py after editing OOXML XML files
- NEVER use CSS gradients or SVG icons directly in HTML slides -- rasterize to PNG first with Sharp
- NEVER assume slide indices are 1-based -- all scripts use 0-based indexing

---

## Reading and Analyzing Presentations

### Text extraction

For reading text content only:

```bash
python -m markitdown path-to-file.pptx
```

### Raw XML access

Required for: comments, speaker notes, slide layouts, animations, design elements, and complex formatting.

```bash
python ooxml/scripts/unpack.py <office_file> <output_dir>
```

If the script is not at the expected path: `find . -name "unpack.py"`

**Key file locations inside unpacked directory:**

| Path | Content |
|---|---|
| `ppt/presentation.xml` | Main metadata and slide references |
| `ppt/slides/slide{N}.xml` | Individual slide content |
| `ppt/notesSlides/notesSlide{N}.xml` | Speaker notes |
| `ppt/comments/modernComment_*.xml` | Slide comments |
| `ppt/slideLayouts/` | Layout templates |
| `ppt/slideMasters/` | Master templates |
| `ppt/theme/theme1.xml` | Colors and fonts |
| `ppt/media/` | Images and media |

### Typography and color extraction

When emulating an existing design, analyze first:

1. Read `ppt/theme/theme1.xml` for `<a:clrScheme>` (colors) and `<a:fontScheme>` (fonts)
2. Examine `ppt/slides/slide1.xml` for actual `<a:rPr>` font usage
3. Grep `<a:solidFill>` and `<a:srgbClr>` across all XML files for color references

---

## Creating a New Presentation (No Template)

Use the html2pptx workflow to convert HTML slides to PowerPoint with accurate positioning.

### Step 1: Design approach

Before writing any code, state your design choices:

- What does the subject matter suggest for tone, industry, mood?
- If a company is mentioned, consider their brand identity
- Select a palette that reflects the content -- avoid autopilot defaults
- Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact

**Color palettes** (choose one, adapt it, or build your own):

| Name | Colors |
|---|---|
| Classic Blue | `#1C2833` `#2E4053` `#AAB7B8` `#F4F6F6` |
| Teal & Coral | `#5EA8A7` `#277884` `#FE4447` `#FFFFFF` |
| Bold Red | `#C0392B` `#E74C3C` `#F39C12` `#F1C40F` `#2ECC71` |
| Warm Blush | `#A49393` `#EED6D3` `#E8B4B8` `#FAF7F2` |
| Burgundy Luxury | `#5D1D2E` `#951233` `#C15937` `#997929` |
| Deep Purple & Emerald | `#B165FB` `#181B24` `#40695B` `#FFFFFF` |
| Cream & Forest Green | `#FFE1C7` `#40695B` `#FCFCFC` |
| Pink & Purple | `#F8275B` `#FF574A` `#FF737D` `#3D2F68` |
| Lime & Plum | `#C5DE82` `#7C3A5F` `#FD8C6E` `#98ACB5` |
| Black & Gold | `#BF9A4A` `#000000` `#F4F6F6` |
| Sage & Terracotta | `#87A96B` `#E07A5F` `#F4F1DE` `#2C2C2C` |
| Charcoal & Red | `#292929` `#E33737` `#CCCBCB` |
| Vibrant Orange | `#F96D00` `#F2F2F2` `#222831` |
| Forest Green | `#191A19` `#4E9F3D` `#1E5128` `#FFFFFF` |
| Retro Rainbow | `#722880` `#D72D51` `#EB5C18` `#F08800` `#DEB600` |
| Vintage Earthy | `#E3B448` `#CBD18F` `#3A6B35` `#F4F1DE` |
| Coastal Rose | `#AD7670` `#B49886` `#F3ECDC` `#BFD5BE` |
| Orange & Turquoise | `#FC993E` `#667C6F` `#FCFCFC` |

### Visual design options

**Geometric patterns:** diagonal dividers, asymmetric columns (30/70, 40/60), rotated headers at 90/270 degrees, overlapping shapes for depth

**Border treatments:** single-side thick borders (10-20pt), L-shaped borders (top+left or bottom+right), underline accents under headers (3-5pt)

**Typography:** extreme size contrast (72pt headline vs 11pt body), all-caps wide-tracked headers, Courier New for data/stats, oversized display numbers for key metrics

**Chart and data styling:** monochrome charts with single accent, horizontal bar charts, dot plots, data labels on elements (no legends), minimal or no gridlines

**Layout options:** full-bleed images with text overlays, 20-30% sidebar column for navigation, modular grid (3x3, 4x4), magazine-style multi-column

**Backgrounds:** solid blocks covering 40-60% of slide, split backgrounds (diagonal or vertical), edge-to-edge color bands

### Layout rule for charts and tables

- **Two-column (preferred):** Full-width header, then two columns below -- text/bullets in one column, chart/table in the other. Use flexbox with unequal widths (40/60 split).
- **Full-slide:** Let the chart/table fill the entire slide for maximum readability.
- NEVER stack charts or tables below text in a single column.

### Step 2: Workflow

1. **Read `html2pptx.md` in full.** NEVER set range limits. Read every line before touching code.
2. Create an HTML file per slide at proper dimensions (e.g., 720pt x 405pt for 16:9):
   - Use semantic tags: `<p>`, `<h1>`-`<h6>`, `<ul>`, `<ol>`
   - Use `class="placeholder"` for chart/table areas (gray background for visibility)
   - Rasterize gradients and icons to PNG using Sharp BEFORE referencing them in HTML
   - Apply two-column or full-slide layout for any chart, table, or image slide
3. Create and run a JavaScript file using `scripts/html2pptx.js`:
   - Call `html2pptx()` for each HTML file
   - Add charts and tables to placeholder areas via PptxGenJS API
   - Save with `pptx.writeFile()`
4. **Visual validation with thumbnail grid:**
   ```bash
   python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4
   ```
   Inspect for: text cutoff by header bars or slide edges, overlapping text/shapes, positioning too close to boundaries, contrast failures. Fix HTML and regenerate until all slides pass.

---

## Editing an Existing Presentation

Work directly with the OOXML format: unpack, edit XML, validate, repack.

1. **Read `ooxml.md` in full.** NEVER set range limits. Read every line before touching XML.
2. Unpack: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. Edit XML files (primarily `ppt/slides/slide{N}.xml` and related files)
4. Validate immediately after EACH edit: `python ooxml/scripts/validate.py <dir> --original <file>`
5. Fix all validation errors before making further edits
6. Repack: `python ooxml/scripts/pack.py <input_directory> <office_file>`

---

## Creating a Presentation from a Template

Duplicate and rearrange template slides, then replace placeholder text.

### Step 1: Extract and analyze the template

```bash
python -m markitdown template.pptx > template-content.md
python scripts/thumbnail.py template.pptx
```

Read `template-content.md` in full (NEVER set range limits). Review the thumbnail grid to understand layout patterns, image placeholder counts, and visual structure.

### Step 2: Build a template inventory file

Save `template-inventory.md`:

```markdown
# Template Inventory Analysis
**Total Slides: [count]**
**IMPORTANT: Slides are 0-indexed (first slide = 0, last slide = count-1)**

## [Category Name]
- Slide 0: [Layout code] - Description/purpose
- Slide 1: [Layout code] - Description/purpose
[... list every slide individually with its index ...]
```

### Step 3: Create a presentation outline with template mapping

Rules for selecting layouts:
- Single-column: unified narrative or single topic
- Two-column: ONLY when you have exactly 2 distinct items
- Three-column: ONLY when you have exactly 3 distinct items
- Image + text: ONLY when you have actual images to insert
- Quote: ONLY for actual quotes with attribution -- never for emphasis
- Count actual content pieces BEFORE selecting a layout
- NEVER use a layout with more placeholders than you have content

Save `outline.md` including the template mapping:

```python
# Template slides to use (0-based indexing)
# WARNING: Verify indices are within range (e.g., 73-slide template = indices 0-72)
template_mapping = [
    0,   # Title/Cover
    34,  # B1: Title and body
    34,  # B1: second copy
    50,  # E1: Quote
    54,  # F2: Closing + Text
]
```

### Step 4: Rearrange slides

```bash
python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52
```

- Indices are 0-based
- Repeated indices duplicate that slide
- Script handles duplication, deletion, and reordering automatically

### Step 5: Extract full text inventory

```bash
python scripts/inventory.py working.pptx text-inventory.json
```

Read `text-inventory.json` in full (NEVER set range limits).

**Inventory JSON structure:**

```json
{
  "slide-0": {
    "shape-0": {
      "placeholder_type": "TITLE",
      "left": 1.5, "top": 2.0, "width": 7.5, "height": 1.2,
      "paragraphs": [
        {
          "text": "Paragraph text",
          "alignment": "CENTER",
          "bold": true,
          "bullet": true,
          "level": 0,
          "font_name": "Arial",
          "font_size": 14.0,
          "color": "FF0000",
          "theme_color": "DARK_1"
        }
      ]
    }
  }
}
```

Key behaviors:
- Shapes ordered by visual position (top-to-bottom, left-to-right)
- Slide number shapes are filtered out automatically
- Only non-default property values are included
- `level` is always present when `bullet: true`
- Colors: `"color"` for RGB, `"theme_color"` for theme references

### Step 6: Generate replacement JSON

Before writing replacement content:
- Verify which shapes exist in the inventory -- only reference shapes that are present
- Shapes NOT listed in your replacement JSON will have their text cleared automatically

```json
{
  "slide-0": {
    "shape-0": {
      "paragraphs": [
        { "text": "Presentation Title", "alignment": "CENTER", "bold": true },
        { "text": "First bullet item", "bullet": true, "level": 0 },
        { "text": "Red colored text", "color": "FF0000" },
        { "text": "Theme colored text", "theme_color": "DARK_1" }
      ]
    }
  }
}
```

Formatting rules:
- Titles: `"bold": true`, often `"alignment": "CENTER"`
- Bullet items: `"bullet": true, "level": 0` -- NEVER add bullet symbols to the text string
- Preserve alignment, font, and color properties from the original inventory
- For overlapping shapes: prefer the shape with larger `default_font_size` or more appropriate `placeholder_type`
- Save as `replacement-text.json`

### Step 7: Apply replacements

```bash
python scripts/replace.py working.pptx replacement-text.json output.pptx
```

The script validates all referenced shapes against inventory, clears all inventory shapes, then applies replacements. Validation errors are shown all at once:

```
ERROR: Invalid shapes in replacement JSON:
  - Shape 'shape-99' not found on 'slide-0'. Available shapes: shape-0, shape-1, shape-4
  - Slide 'slide-999' not found in inventory

ERROR: Replacement text made overflow worse in these shapes:
  - slide-0/shape-2: overflow worsened by 1.25" (was 0.00", now 1.25")
```

---

## Thumbnail Grids

```bash
python scripts/thumbnail.py template.pptx [output_prefix]
python scripts/thumbnail.py template.pptx analysis --cols 4
```

- Output: `thumbnails.jpg` (or `thumbnails-1.jpg`, `thumbnails-2.jpg` for large decks)
- Default: 5 columns, max 30 slides per grid
- Column limits: 3 cols = 12 slides/grid, 4 = 20, 5 = 30, 6 = 42
- Slides are 0-indexed in output labels
- Include path in prefix for specific output directory: `workspace/my-grid`

---

## Code Style

- Write concise code
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements
