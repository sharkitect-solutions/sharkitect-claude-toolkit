# Invoice Data Extraction Patterns

## PDF Extraction Tool Selection

Choose the extraction tool based on document type and accuracy requirements:

| Tool | Best For | Accuracy | Speed | Install |
|------|----------|----------|-------|---------|
| pdfplumber | Native-text PDFs with tables | 99%+ on native text | Fast (~0.2s/page) | `pip install pdfplumber` |
| pymupdf (fitz) | Native-text PDFs, high volume | 99%+ on native text | Fastest (~0.05s/page) | `pip install pymupdf` |
| Tesseract OCR | Image-based PDFs, scanned docs | 85-98% depending on quality | Slow (~2-5s/page) | System install + `pip install pytesseract` |
| EasyOCR | Multi-language invoices | 90-96% on printed text | Medium (~1-3s/page) | `pip install easyocr` (GPU optional) |
| Amazon Textract | Production high-volume pipeline | 95-99%, best on forms | API latency ~3-8s | AWS SDK, pay-per-page |
| Google Document AI | Structured form extraction | 95-99%, strong on tables | API latency ~2-5s | GCP SDK, pay-per-page |

**Decision tree:**
1. Can you select/copy text in the PDF? -> Use pdfplumber or pymupdf (no OCR needed)
2. Is it a scanned document with clean print? -> Tesseract with preprocessing
3. Multi-language or handwritten? -> EasyOCR or cloud API
4. Production pipeline processing 1000+ invoices/month? -> Cloud API (Textract or Document AI)

## Regex Patterns for Invoice Fields

### Invoice Numbers

Common formats by vendor type:

```python
INVOICE_NUMBER_PATTERNS = [
    # Standard formats
    r'(?:Invoice|Inv|INV)[\s#:.-]*([A-Z0-9][\w-]{3,20})',
    # Numeric only (5+ digits)
    r'(?:Invoice|Inv|INV)\s*(?:No|Number|#|Num)?\s*[:.#]?\s*(\d{5,})',
    # Amazon order IDs
    r'(\d{3}-\d{7}-\d{7})',
    # Stripe invoice IDs
    r'(in_[a-zA-Z0-9]{8,32})',
    # UUID-style
    r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
    # Alphanumeric with prefix (e.g., INV-2024-0847, PO-12345)
    r'([A-Z]{2,4}[-/]\d{4}[-/]\d{3,6})',
]
```

### Date Formats

Parse in order of specificity to avoid ambiguity:

```python
DATE_PATTERNS = [
    # ISO 8601 (unambiguous)
    (r'(\d{4}[-/]\d{2}[-/]\d{2})', '%Y-%m-%d'),
    # US format (ambiguous with EU if day <= 12)
    (r'(\d{1,2}/\d{1,2}/\d{4})', '%m/%d/%Y'),
    # EU format
    (r'(\d{1,2}[./]\d{1,2}[./]\d{4})', '%d/%m/%Y'),
    # Written month (unambiguous)
    (r'(\w+ \d{1,2},? \d{4})', '%B %d, %Y'),  # March 15, 2024
    (r'(\d{1,2} \w+ \d{4})', '%d %B %Y'),      # 15 March 2024
    # Abbreviated month
    (r'(\d{1,2}[-/]\w{3}[-/]\d{4})', '%d-%b-%Y'),  # 15-Mar-2024
]
```

**Disambiguation rule:** When a date like `03/04/2024` is ambiguous, check:
1. Vendor country (US -> MM/DD, EU/UK -> DD/MM)
2. Other dates in the same document (if any date has day >12, it reveals the format)
3. If still ambiguous, default to vendor locale and flag `[DATE-AMBIGUOUS]`

### Currency Amounts

```python
AMOUNT_PATTERNS = [
    # US/UK format: $1,234.56 or 1,234.56
    r'[\$\x{00A3}]?\s*([\d,]+\.\d{2})\b',
    # EU format: 1.234,56 or EUR 1.234,56
    r'(?:EUR|CHF)?\s*([\d.]+,\d{2})\b',
    # No-decimal whole amounts: $1,234
    r'[\$\x{00A3}]\s*([\d,]+)\b',
    # Negative/credit amounts: -$50.00 or ($50.00)
    r'-?\$?\s*\(?([\d,]+\.\d{2})\)?',
]
```

**EU vs US decimal handling:** In `1.234,56` the comma is decimal, periods are thousands. In `1,234.56` the period is decimal, commas are thousands. Detect by checking which separator appears last -- the last separator is always the decimal.

### Tax ID / VAT Number Formats

```python
TAX_ID_PATTERNS = {
    'US_EIN': r'\b(\d{2}-\d{7})\b',           # 12-3456789
    'UK_VAT': r'\b(GB\d{9})\b',               # GB123456789
    'DE_VAT': r'\b(DE\d{9})\b',               # DE123456789
    'FR_VAT': r'\b(FR[A-Z0-9]{2}\d{9})\b',    # FRXX123456789
    'CA_BN':  r'\b(\d{9}RT\d{4})\b',          # 123456789RT0001
    'AU_ABN': r'\b(\d{2}\s?\d{3}\s?\d{3}\s?\d{3})\b',  # 12 345 678 901
}
```

## Multi-Page Invoice Detection

Invoices spanning multiple pages require assembly before extraction:

**Page continuation indicators:**
- "Page X of Y" or "X/Y" in header/footer
- "Continued on next page" or "Continued from previous page"
- Same invoice number repeated across pages
- Running subtotal at bottom of non-final pages (no "Grand Total" or "Amount Due")
- Consistent header elements (logo, invoice number, vendor name) repeating

**Assembly strategy:**
1. Group pages by invoice number (extract from header of each page)
2. If no invoice number on subsequent pages, check for page numbering
3. Concatenate text in page order
4. Extract fields from the assembled text (totals typically on last page only)
5. Verify: sum of line items across pages should equal the total on the final page

## Table Extraction Strategies

Line items are the most complex extraction target. Strategies by document quality:

**Native text PDFs (pdfplumber):**
```python
import pdfplumber

with pdfplumber.open("invoice.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            # First row is typically headers
            headers = table[0]
            for row in table[1:]:
                # Map columns to fields
                pass
```

**When table extraction fails** (merged cells, irregular spacing):
- Fall back to line-by-line text extraction
- Use vertical position clustering to identify columns
- Look for repeating patterns: description followed by quantity followed by amount
- Use the total as a checksum: sum of line item amounts should equal subtotal

**Image-based documents:**
- Preprocess before OCR: convert to grayscale, apply adaptive threshold, deskew (correct rotation), denoise
- For table detection in images, use horizontal/vertical line detection (OpenCV) to find cell boundaries
- Process each cell individually for higher accuracy than full-page OCR

## Image Preprocessing Pipeline for OCR

Quality of OCR output depends heavily on image preprocessing. Apply these steps in order:

1. **Grayscale conversion** -- Remove color information. Reduces noise without losing text.
2. **Deskew** -- Detect rotation angle using Hough line transform. Correct if angle > 0.5 degrees. Even 2-degree skew drops OCR accuracy by 5-10%.
3. **Binarization** -- Convert to black and white using adaptive thresholding (Otsu's method for uniform lighting, adaptive Gaussian for uneven lighting like phone photos).
4. **Noise removal** -- Median filter (kernel size 3) removes salt-and-pepper noise from scans. Do not over-filter -- aggressive denoising erodes thin strokes on small text.
5. **Border removal** -- Crop black borders from scans. Borders confuse layout analysis.
6. **Resolution check** -- OCR accuracy drops below 90% at <150 DPI. Optimal is 300 DPI. Upscale low-resolution images using bicubic interpolation before OCR (upscaling to 300 DPI equivalent).

**Thermal receipt handling:** Thermal paper fades. If contrast is low, increase gamma (1.5-2.0) before binarization. If text is partially faded, use a lower threshold value. Always OCR thermal receipts at time of receipt -- they degrade within months.
