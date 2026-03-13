---
name: invoice-organizer
description: "Use when organizing, categorizing, or processing invoices and financial documents, extracting data from PDFs or images of invoices, building invoice filing systems, or preparing financial documents for accounting review. Do NOT use for accounting journal entries, tax filing, financial forecasting, or payment processing."
---

# Invoice Organizer -- Document Processing Pipeline for Financial Records

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `SKILL.md` | Any invoice organization, filing, or document processing task | Never skip -- always load |
| `references/extraction-patterns.md` | Extracting data from PDFs, OCR setup, parsing invoice fields, handling multi-page documents | Filing taxonomy design, tax categories, automation |
| `references/tax-category-rules.md` | Categorizing expenses for tax prep, IRS Schedule C mapping, deduction rules, receipt retention | PDF extraction, automation workflows, filing structure |
| `references/automation-recipes.md` | Building watched folder workflows, batch processing, vendor profiles, reconciliation, monthly close prep | One-time manual organization, tax rules, extraction patterns |

## Scope Boundary

| In Scope | Out of Scope |
|----------|-------------|
| Invoice data extraction (PDF, image, email) | Accounting journal entries (use smb-cfo) |
| Document classification (invoice vs receipt vs statement) | Tax return filing (refer to CPA) |
| Filing taxonomy design and naming conventions | Payment processing (use stripe-best-practices) |
| Duplicate detection and resolution | Financial forecasting and budgeting (use smb-cfo) |
| Accounting-ready CSV/Excel export | Payroll processing |
| Receipt and expense management | Bank account reconciliation (use smb-cfo) |
| Multi-currency document handling | Investment portfolio management |
| Vendor profile management | Audit procedures (refer to external auditor) |

---

## Document Classification Framework

Every financial document entering the pipeline must be classified before filing. Misclassification corrupts downstream categorization, duplicates line items in accounting imports, and breaks tax reporting.

**Document Type Identification:**

| Type | Key Visual Cues | Distinguishing Feature |
|------|----------------|----------------------|
| Invoice | "Invoice" header, invoice number, payment terms, line items with quantities | Requests payment -- has "Amount Due" or "Balance Due" |
| Receipt | "Receipt" or "Paid" stamp, transaction ID, payment method shown | Confirms payment already made -- no balance due |
| Credit Note | "Credit Note" or "Credit Memo", negative amounts, reference to original invoice | Reduces a previous invoice amount -- always references another document |
| Statement | "Statement of Account", date range, aging buckets (Current/30/60/90) | Summarizes multiple invoices over a period -- not a payment request |
| Purchase Order | "PO" number, "Purchase Order" header, delivery terms | Authorizes a purchase -- precedes the invoice |
| Proforma Invoice | "Proforma" label, no payment terms, estimate language | Quote or estimate -- not legally binding, do not file as payable |

**Classification Confidence Scoring:**

Assign confidence based on how many identifying markers are present:
- **3+ markers match a single type** (>95%): Auto-classify. File directly.
- **2 markers match** (80-95%): Classify with a `[REVIEW]` prefix in the filename. Include in the summary report's review queue.
- **0-1 markers** (<80%): Do not auto-classify. Place in `_needs-review/` folder with the original filename preserved.

Never trust filename alone for classification. A file named `invoice.pdf` could be a receipt, statement, or credit note. Always inspect content.

---

## Data Extraction Architecture

### Extraction Decision Tree

Before extracting, determine the document's text layer:

1. **Native text PDF** -- Text is selectable. Use direct text extraction (pdfplumber or pymupdf). Fast, 99%+ accuracy.
2. **Image-based PDF** -- Text not selectable, pages are embedded images. Requires OCR preprocessing. Accuracy varies 85-98% depending on scan quality.
3. **Image file** (JPG, PNG) -- Always requires OCR. Apply preprocessing: deskew, threshold adjustment, denoising.
4. **HTML/email** -- Parse HTML structure. Most reliable extraction source since text is already structured.

### Key Field Extraction

Extract these fields in priority order. A document missing fields 1-4 should be flagged for manual review:

1. **Invoice Number** -- Patterns: `INV-\d{4,}`, `#\d{5,}`, `Invoice\s*(?:No|Number|#)?\s*:?\s*(\S+)`. Check header area first (top 20% of document). Vendors use inconsistent formats -- Amazon uses order IDs (`\d{3}-\d{7}-\d{7}`), Stripe uses `in_[a-zA-Z0-9]{24}`.
2. **Invoice Date** -- Search for labels: "Invoice Date", "Date Issued", "Date". Parse formats: `MM/DD/YYYY` (US), `DD/MM/YYYY` (EU/UK), `YYYY-MM-DD` (ISO). Ambiguous dates like `03/04/2024` require locale context -- default to the vendor's country format.
3. **Vendor Name** -- Usually the largest text in the header or the entity name beside a logo. Cross-reference against existing vendor profiles. Normalize: "ADOBE SYSTEMS INC" and "Adobe Inc." should map to "Adobe".
4. **Total Amount** -- Search bottom 40% of document. Look for "Total", "Amount Due", "Balance Due", "Grand Total". Extract the last/largest amount near these labels. Distinguish subtotal, tax, and grand total.
5. **Currency** -- Detect from symbol ($, EUR, GBP, CAD), ISO code, or vendor country. Default to USD for US-based vendors if no symbol present.
6. **Line Items** -- Table rows between header row and total row. Each line: description, quantity, unit price, line total. Not all invoices have itemized lines -- single-line invoices are common for subscriptions.
7. **Tax Amount** -- Search for "Tax", "VAT", "GST", "HST". Separate from total for accounting import. Tax rates help validate: US sales tax 4-10%, UK VAT 20%, EU VAT 17-27%.
8. **Payment Terms** -- "Net 30", "Due on Receipt", "Net 60", specific due date. Critical for AP aging reports.

### Extraction Confidence Thresholds

| Confidence | Action | Example |
|-----------|--------|---------|
| >95% | Auto-accept. Use extracted value directly. | Clear "Invoice #: INV-2024-0847" in native text PDF |
| 80-95% | Accept with flag. Mark field with `[VERIFY]` in export. | OCR reads amount as "$1,234.56" but slight blur on the "2" |
| <80% | Reject. Leave field blank in export, add to review queue. | Handwritten receipt, faded thermal paper, heavy watermark |

---

## Filing Taxonomy Design

### Choosing a Hierarchy

The right hierarchy depends on volume and primary access pattern:

| Volume | Primary Need | Recommended Hierarchy | Why |
|--------|-------------|----------------------|-----|
| <50/year | Simple retrieval | `Year/Vendor/` | Low volume -- vendor name is fastest lookup |
| 50-500/year | Tax preparation | `Year/Quarter/Category/` | Accountants need time-period + expense-type grouping |
| 500-2000/year | AP management | `Year/Month/Status/` (Paid/Unpaid/Disputed) | High volume demands payment-status filtering |
| 2000+/year | Full automation | `Year/Month/Vendor/` + database index | Folder browsing breaks down -- rely on search + metadata DB |

### Naming Convention

Standard format with collision prevention:

```
YYYY-MM-DD_VendorName_INV-XXXX_$Amount.ext
```

Rules:
- **Date**: Invoice date (NOT file system date, NOT download date). ISO 8601 format for chronological sorting.
- **Vendor**: PascalCase, no spaces, abbreviated to 20 chars max. Map variants: `AmazonWebServices` not `AWS` or `AMZN` or `Amazon.com Inc`.
- **Invoice ID**: Vendor's invoice number. If missing, use `NOID-MMDD` as placeholder.
- **Amount**: Dollar sign, no commas, two decimal places. Enables quick visual scanning.
- **Collision suffix**: If filename exists, append `-02`, `-03`. Never overwrite silently.

Examples:
```
2024-03-15_Adobe_INV-88234_$52.99.pdf
2024-03-10_Amazon_112-3456789-0123456_$127.45.pdf
2024-03-01_Stripe_in_1N2x3Y4z_$249.00.pdf
2024-02-28_Staples_NOID-0228_$43.17.jpg
```

### Duplicate Detection

Duplicates enter the system through email re-downloads, multiple payment reminders, and shared folder syncs. Undetected duplicates inflate expense reports and corrupt tax filings.

**Fuzzy matching criteria** -- flag as potential duplicate when ALL three match:
- Same vendor (after normalization)
- Same date (within +/- 1 calendar day to handle timezone differences)
- Same amount (within 1% tolerance to handle rounding and currency conversion)

When a duplicate is detected:
1. Compare file hashes. If identical: keep the one with better filename metadata, delete the other.
2. If hashes differ but fields match: keep both, rename the newer one with `-DUP` suffix, add to review queue.
3. Never auto-delete without logging. Write every deletion to a `_duplicate-log.csv` with original path, kept path, match reason, and timestamp.

---

## Accounting-Ready Export

### Import Format Requirements

| Software | Format | Required Fields | Notes |
|----------|--------|----------------|-------|
| QuickBooks Online | CSV | Date, Description, Amount, Category | Date format: MM/DD/YYYY. Negative amounts for credits. |
| Xero | CSV | Date, Amount, Payee, Description, Account Code | Date: DD/MM/YYYY (UK default). Account codes must match Xero chart of accounts. |
| FreshBooks | CSV | Date, Vendor, Amount, Category, Tax | Supports multi-currency with separate currency column. |
| Wave | CSV | Date, Description, Amount, Account | Free tier -- popular with sole proprietors. Simple format. |
| Generic GL | CSV | Date, GL Account, Debit, Credit, Memo, Vendor | Double-entry format. Debits in one column, credits in another. |

### Chart of Accounts Mapping

Map each invoice to a GL expense account. Common SMB chart of accounts:

```
5000 - Cost of Goods Sold
6100 - Advertising & Marketing
6200 - Auto & Travel
6300 - Bank & Financial Fees
6400 - Contractor & Professional Services
6500 - Insurance
6600 - Office Supplies & Equipment
6700 - Rent & Utilities
6800 - Software & Subscriptions
6900 - Meals & Entertainment
7000 - Telephone & Internet
7100 - Training & Education
7200 - Miscellaneous
```

When a vendor's GL account is ambiguous, flag it rather than guessing. A misclassified expense is worse than an uncategorized one -- the uncategorized one gets reviewed, the misclassified one gets buried.

---

## Multi-Currency and International Documents

### Currency Detection Priority

1. Explicit ISO code in document text (EUR, GBP, CAD, AUD)
2. Currency symbol with context ($ alone is ambiguous -- could be USD, CAD, AUD, or others)
3. Vendor country of origin (use registered address, not payment address)
4. Bank account details (IBAN prefix indicates country)

### Exchange Rate Date Selection

Three valid dates exist for any foreign-currency invoice. Using the wrong one creates reconciliation mismatches:

| Date | When to Use | Why |
|------|------------|-----|
| Invoice date | Default for accrual accounting, IRS reporting | Matches revenue/expense recognition period |
| Payment date | Cash-basis accounting, bank reconciliation | Matches actual cash flow |
| Month-end rate | Simplified reporting (IRS allows average rates) | Reduces transaction-by-transaction conversion burden |

Record the original currency amount AND the converted amount in every export. Never discard the original -- auditors and accountants need both.

### VAT/GST Extraction

| Jurisdiction | Tax Name | Standard Rate | Search Terms |
|-------------|----------|--------------|-------------|
| US | Sales Tax | 4-10% (varies by state) | "Sales Tax", "Tax" |
| UK | VAT | 20% (reduced: 5%, zero: 0%) | "VAT", "Value Added Tax", VAT reg number: `GB\d{9}` |
| EU | VAT | 17-27% (varies by country) | "MwSt" (DE), "TVA" (FR), "IVA" (ES/IT) |
| Canada | GST/HST | 5% GST, 13-15% HST by province | "GST", "HST", BN format: `\d{9}RT\d{4}` |
| Australia | GST | 10% | "GST", ABN format: `\d{11}` |

**Reverse charge identification:** If an EU invoice shows 0% VAT with text like "Reverse Charge" or "Article 196", the buyer (not seller) is responsible for declaring VAT. Flag these invoices separately -- they require different accounting treatment.

---

## Named Anti-Patterns

### The Silent Overwrite
**Detect:** Script moves or copies a file to a path where a file already exists, without checking. **Impact:** Permanent document loss. The original file at the destination is gone. **Fix:** Always check destination path before write. If collision detected, append sequence suffix (`-02`, `-03`). Log every file operation to an audit trail.

### The Date Trust Trap
**Detect:** Using file system creation/modification date as the invoice date. **Impact:** File dates reflect when the file was downloaded, emailed, or copied -- not when the invoice was issued. A March invoice downloaded in June gets filed under June, corrupting time-based reports. **Fix:** Extract date from document content. Only fall back to file system date if content extraction fails, and mark the record `[DATE-UNVERIFIED]`.

### The Flat Dump
**Detect:** All files in one directory with good naming but no folder hierarchy. **Impact:** Works fine under 200 files. At 500+ files, folder browsing becomes unusable, OS file listings slow down, and accidental bulk operations become dangerous. **Fix:** Implement hierarchy from the start. Even `Year/Month/` adds sufficient structure. Retroactive restructuring is always more expensive than upfront design.

### The Premature Archive
**Detect:** Moving invoices to an archive folder before confirming payment status. **Impact:** Unpaid invoices disappear from active view. Missed payments lead to late fees, service disruptions, and damaged vendor relationships. **Fix:** Use a status-based workflow: `_inbox/` (new) -> `_processing/` (extracted/filed) -> `_paid/` (confirmed) -> `_archive/` (fiscal year closed). Only archive after payment confirmation AND fiscal year close.

### The OCR Blindspot
**Detect:** Accepting OCR output without confidence validation, especially on thermal receipts, faded documents, or photographed invoices. **Impact:** Incorrect amounts, wrong dates, garbled vendor names silently enter the system. A $1,234.56 invoice OCR'd as $1,284.56 creates a $50 discrepancy that surfaces months later during reconciliation. **Fix:** Implement confidence thresholds. Flag any field below 95% confidence. Require human verification for amounts on low-quality scans.

### The Personal Mix
**Detect:** Business and personal expenses in the same filing system without separation. **Impact:** IRS audit risk. Commingled expenses force item-by-item review during audits instead of category-level verification. Personal expenses incorrectly deducted trigger penalties. **Fix:** Separate filing systems from day one. If using a single tool, enforce a top-level split: `Business/` and `Personal/`. Never allow cross-filing.

---

## Rationalization Table

| Shortcut | Why It Seems OK | Why It Fails | Do This Instead |
|----------|----------------|-------------|-----------------|
| "I'll organize later when I have more time" | Current volume is manageable by memory | Backlog grows exponentially. A 6-month backlog takes 10x longer than 6 monthly sessions. | Process invoices weekly. 15 minutes per week vs 8 hours every 6 months. |
| "The filename is descriptive enough, no need for folders" | Quick to implement, files are findable by search | Search fails when you need date-range queries, vendor totals, or category reports. Flat structures prevent bulk operations. | Implement at minimum `Year/Category/` hierarchy. Takes 2 minutes during setup. |
| "OCR is good enough now, I don't need to verify" | Modern OCR is 95%+ on clean documents | 95% accuracy across 10 fields means ~60% chance of at least one error per invoice. Errors in amounts or dates cascade through reports. | Verify amounts and dates on every document. Auto-accept only vendor names and descriptions. |
| "I'll just keep everything -- storage is cheap" | Avoids the effort of classifying duplicates | Duplicates inflate expense totals, confuse tax prep, and create reconciliation nightmares. 500 real invoices + 80 duplicates = every report is wrong. | Deduplicate at ingestion. Log deletions. Review quarterly. |

---

## Red Flags -- Stop and Check

1. **Amount mismatch >$1 between OCR extraction and expected range for the vendor.** Re-extract or verify manually. Even small discrepancies compound across hundreds of documents.
2. **Invoice date is in the future.** Likely a date parsing error (DD/MM vs MM/DD swap) or a proforma invoice misclassified as final. Verify the original document.
3. **Duplicate invoice number from the same vendor.** Either a re-send, a different revision, or a genuine duplicate. Compare amounts and dates before filing both.
4. **No invoice number on the document.** Legitimate for small vendors and sole proprietors, but verify it is not a quote, estimate, or proforma being treated as a payable invoice.
5. **Currency symbol without country context on amounts >$1,000.** A "$" could be USD, CAD, AUD, or others. The difference between $5,000 USD and $5,000 AUD is ~33%. Verify with vendor country.
6. **Tax amount exceeds 30% of subtotal.** No standard jurisdiction has a combined tax rate above 27%. Likely an extraction error or the "tax" field captured shipping, fees, or surcharges.
7. **Vendor name does not match any existing vendor profile and the amount exceeds $500.** New high-value vendors warrant verification before filing -- could be a phishing invoice or misdirected document.
