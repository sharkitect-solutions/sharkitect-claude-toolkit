---
name: pdf-processing-pro
description: "Use when extracting text/tables/forms from PDFs, filling PDF forms, OCR on scanned documents, batch PDF processing, diagnosing PDF extraction failures, choosing between PDF libraries. NEVER for Word documents (use docx), spreadsheets (use xlsx), presentations (use pptx), generating PDFs from scratch (use reportlab/weasyprint directly), image-only processing without PDF context (use standard PIL/OpenCV)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# PDF Processing Pro

## File Index

| File | Contents | When to Load |
|------|----------|--------------|
| `FORMS.md` | AcroForm field types, filling workflows, validation, flattening | Form analysis, filling, or validation tasks |
| `TABLES.md` | pdfplumber table settings, multi-page merge, export formats | Table extraction from any PDF |
| `OCR.md` | Tesseract integration, preprocessing pipeline, language setup | Scanned PDFs or image-based documents |
| `scripts/analyze_form.py` | CLI tool: extract form field metadata to JSON | Run directly for form field discovery |

## Scope Boundary

| Task | This Skill | Defer To |
|------|-----------|----------|
| Extract text/tables from native PDFs | Yes | -- |
| Fill and flatten PDF forms | Yes | -- |
| OCR scanned PDFs | Yes | -- |
| Batch process PDF directories | Yes | -- |
| Diagnose extraction failures | Yes | -- |
| Create Word documents | No | docx |
| Read/write Excel files | No | xlsx |
| Create presentations | No | pptx |
| Generate PDF from HTML/templates | No | reportlab, weasyprint |
| Edit PDF layout/design | No | Manual tools (Acrobat, LibreOffice) |

## Library Selection Decision Matrix

Pick the FIRST library that matches the PDF characteristics:

| PDF Characteristic | Primary Library | Why | Fallback |
|-------------------|----------------|-----|----------|
| Native text, simple layout | `pdfplumber` | Best text positioning, word-level coords | `pypdf` for metadata-only |
| Tables with visible gridlines | `pdfplumber` | Line-based table detection built in | `camelot` (Lattice mode) |
| Tables WITHOUT gridlines | `camelot` (Stream mode) | Text-position clustering superior | `pdfplumber` with `text` strategy |
| Form fields (AcroForm) | `pypdf` | Native AcroForm read/write support | -- |
| Form fields (XFA) | REJECT or `pdfrw` | pypdf/pdfplumber cannot read XFA; warn user XFA support is limited | External: Adobe API |
| Scanned/image-based | `pdf2image` + `pytesseract` | Convert to image then OCR | `ocrmypdf` for batch |
| Mixed (some pages scanned, some native) | Detect per-page, route accordingly | See Hybrid Detection below | -- |
| Encrypted (user password) | `pypdf` with `decrypt()` | Built-in decryption support | `pikepdf` for owner-password |
| Encrypted (owner password, no user pw) | `pikepdf` | Can remove restrictions when no user password set | -- |
| Very large (500+ pages) | `pdfplumber` page-by-page | Stream processing, never load full doc | `pypdf` with lazy loading |
| PDF/A archival format | `pypdf` | Preserves PDF/A compliance on write | -- |

### Hybrid Detection Procedure

Before processing any PDF, determine its nature:

```python
def classify_pdf_page(page):
    """Returns 'native', 'scanned', or 'mixed'."""
    text = page.extract_text() or ""
    images = page.images
    word_count = len(text.split())
    if word_count > 20 and not images:
        return "native"
    if word_count < 5 and images:
        return "scanned"
    return "mixed"  # has both -- extract text first, OCR image regions
```

## PDF Forensics Checklist

When extraction produces garbage, empty strings, or wrong characters, diagnose in this order:

| Check | How | What It Means |
|-------|-----|---------------|
| 1. Text embedded? | `page.extract_text()` returns content | If empty: scanned PDF, route to OCR |
| 2. Encoding correct? | Look for `\x00` between chars, or `(cid:XX)` in output | CIDFont mapping missing -- try `pikepdf` to extract or re-encode |
| 3. Text vs image layer? | `len(page.images) > 0` AND `len(page.extract_text()) > 0` | Both present: text may be hidden behind image overlay (common in redacted PDFs) |
| 4. Custom font encoding? | Characters display correctly in viewer but extract as symbols | Font uses custom ToUnicode CMap -- extract with `pdfplumber` using `x_tolerance=1` |
| 5. Right-to-left text? | Arabic/Hebrew content appears reversed | Use `pdfplumber` -- it handles bidi better than pypdf |
| 6. Multi-column layout? | Text from adjacent columns interleaved | Crop to column bounding boxes, extract each separately |
| 7. Rotated pages? | Content appears rotated 90/180/270 degrees | Check `page.rotation` -- apply inverse before extraction |
| 8. Form type? | `reader.get_fields()` returns None but form visible | XFA form -- pypdf cannot read; check `/AcroForm/XFA` in trailer |

## Table Extraction Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| No gridlines | `extract_tables()` returns `[]` | Switch to `"vertical_strategy": "text", "horizontal_strategy": "text"` |
| Merged cells | `None` values in middle of rows | Post-process: forward-fill None values from left/above |
| Multi-page table | Headers repeat, data split across pages | Detect repeated header row, concatenate data rows, skip duplicate headers |
| Rotated text in cells | Cell values empty but table structure detected | Extract chars with rotation attribute, reconstruct text |
| Nested tables | Outer table detected, inner tables become single cells | Crop to inner cell bbox, run `extract_tables()` on cropped region |
| Spanning columns | Column count inconsistent across rows | `max_cols = max(len(r) for r in table)`, pad short rows |
| Invisible borders (white lines) | Looks bordered in viewer but `lines` strategy fails | Use `"edge_min_length": 1` and lower `"snap_tolerance"` to 1 |
| Table is actually an image | No text or lines detected in table region | Crop region to image, OCR that region only |

## OCR Quality Decision

| DPI of Source | Expected Accuracy | Recommendation |
|--------------|-------------------|----------------|
| <150 | <70% -- unreliable | Reject or request re-scan at 300 DPI |
| 150-200 | 70-85% -- usable with review | Process with aggressive preprocessing |
| 200-300 | 85-95% -- production quality | Standard preprocessing sufficient |
| >300 | 95%+ -- diminishing returns | Use as-is; higher DPI wastes processing time |

### OCR Preprocessing Pipeline (in order)

1. **Deskew** -- correct rotation (>0.5 degree skew kills accuracy)
2. **Binarize** -- convert to black/white (Otsu threshold, not fixed)
3. **Denoise** -- median filter (kernel=3 for 300 DPI, kernel=5 for 150 DPI)
4. **Remove borders** -- crop scan artifacts and black edges
5. **Scale** -- upscale to 300 DPI if source is lower (bicubic interpolation)

Skip steps that don't apply. Order matters -- deskew before binarize prevents artifacts.

### Tesseract PSM Selection

| Page Layout | PSM Value | When to Use |
|-------------|-----------|-------------|
| Full page, single column | `--psm 3` (default) | Standard documents |
| Single column, variable text sizes | `--psm 4` | Invoices, receipts |
| Single line of text | `--psm 7` | Extracting one field |
| Single word | `--psm 8` | Captchas, labels |
| Sparse text on page | `--psm 11` | Forms with scattered fields |
| Table/structured data | `--psm 6` | Tables, spreadsheets |

## Form Processing Edge Cases

| Scenario | Detection | Handling |
|----------|-----------|----------|
| AcroForm vs XFA | Check `reader.trailer['/Root'].get('/AcroForm')` for `/XFA` key | AcroForm: use pypdf. XFA: warn user, suggest Adobe API or pdfrw |
| Read-only fields | `field_flags & 1 == 1` | Skip during fill, preserve existing value |
| Calculated fields | Field has `/AA` (additional actions) with `/C` (calculate) | DO NOT overwrite -- value auto-computes from other fields |
| Digital signature fields | Field type `/Sig` | NEVER fill -- invalidates existing signatures |
| Checkbox on-value varies | On-value can be `/Yes`, `/On`, `/1`, or custom | Read `/AP/N` keys to discover actual on-value per field |
| Radio button groups | Multiple fields share same `/T` name | Set value on parent group, not individual buttons |
| Rich text fields | `/Ff` bit 26 set (RichText) | Value may contain XML; pass plain text, let renderer format |
| Barcode fields | Custom field type, renders barcode from value | Validate barcode format (Code128, QR, etc.) before filling |

## Batch Processing Architecture

| PDF Count | File Size (avg) | Strategy | Why |
|-----------|----------------|----------|-----|
| <50 | Any | Sequential `for` loop | Overhead of parallelism not worth it |
| 50-500 | <5MB | `ProcessPoolExecutor(max_workers=cpu_count)` | CPU-bound extraction benefits from multiprocessing |
| 50-500 | >5MB | `ProcessPoolExecutor(max_workers=4)` | Cap workers to avoid memory exhaustion |
| 500+ | <5MB | Chunked multiprocessing (chunks of 100) | Prevents file descriptor exhaustion |
| 500+ | >5MB | Sequential with explicit `gc.collect()` per file | Memory safety over speed |
| Any | OCR needed | `ProcessPoolExecutor` (OCR is CPU-heavy) | Tesseract releases GIL; true parallelism |

**Memory rule of thumb**: pdfplumber uses ~10x file size in RAM. A 50MB PDF needs ~500MB. Plan worker count accordingly.

## Rationalization Table

| Decision | Rationale |
|----------|-----------|
| pdfplumber as default over pypdf | Superior text positioning and table detection; pypdf better only for form fields and metadata |
| Diagnose before fix | 80% of extraction failures are misdiagnosed (e.g., treating encoding issues as OCR problems) |
| Classify pages individually | Mixed PDFs (scanned + native) are common; blanket OCR wastes time and reduces accuracy on native pages |
| Reject low-DPI scans | Sub-150 DPI OCR produces errors that compound downstream; better to fail fast than propagate garbage |
| Sequential for large files | Memory exhaustion from parallel large-PDF processing causes silent corruption; safety over speed |
| XFA as explicit rejection | Silently failing on XFA forms wastes hours of debugging; explicit detection and warning saves time |

## Red Flags

1. **Applying OCR to a native PDF** -- text extraction failed for another reason (encoding, font mapping); OCR will produce inferior results
2. **Using pypdf for table extraction** -- pypdf has no table detection; always use pdfplumber or camelot for tables
3. **Loading entire PDF into memory for batch processing** -- process page-by-page or file-by-file
4. **Ignoring checkbox on-values** -- assuming `/Yes` when the PDF uses `/On` or `/1` causes silent fill failures
5. **Filling calculated or signature fields** -- overwrites auto-computed values or invalidates signatures
6. **Using fixed binarization threshold for OCR** -- Otsu adaptive thresholding handles varying scan quality; fixed thresholds fail on light or dark scans
7. **Skipping deskew before OCR** -- even 1-2 degree rotation drops accuracy 10-20%
8. **Parallel processing 500+ large PDFs without memory limits** -- will exhaust RAM and crash or corrupt output

## NEVER

1. **NEVER fill a `/Sig` (signature) field** -- invalidates the document's digital signatures
2. **NEVER assume XFA forms work with pypdf** -- they silently return empty fields; detect and warn explicitly
3. **NEVER OCR a native-text PDF without first checking why text extraction failed** -- the problem is encoding/fonts, not image-based content
4. **NEVER use `threading` for CPU-bound PDF extraction** -- GIL prevents parallelism; use `multiprocessing`
5. **NEVER skip the forensics checklist when extraction returns empty or garbage** -- random fixes waste more time than systematic diagnosis
