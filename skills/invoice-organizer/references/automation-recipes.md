# Invoice Automation Recipes

## Watched Folder Automation

### Python Watchdog Pattern

Monitor a folder for new invoice files and process them automatically:

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pathlib import Path

WATCH_DIR = Path("~/Downloads/invoices").expanduser()
PROCESSING_DIR = Path("~/Documents/Invoices/_inbox").expanduser()
SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".tiff"}

class InvoiceHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        if filepath.suffix.lower() in SUPPORTED_EXTENSIONS:
            # Wait for file write to complete (critical for large PDFs)
            self._wait_for_stable(filepath)
            self._process_invoice(filepath)

    def _wait_for_stable(self, filepath, checks=3, interval=1):
        """Wait until file size stops changing."""
        sizes = []
        for _ in range(checks):
            time.sleep(interval)
            sizes.append(filepath.stat().st_size)
        if len(set(sizes[-2:])) > 1:
            self._wait_for_stable(filepath)  # Still changing

    def _process_invoice(self, filepath):
        # Move to processing directory (not copy -- prevents re-processing)
        dest = PROCESSING_DIR / filepath.name
        filepath.rename(dest)
        # Trigger extraction pipeline on dest
```

**Critical detail:** Files being downloaded or saved are not immediately complete. Without `_wait_for_stable`, the pipeline processes a partially-written file, extracts garbage data, and files it permanently. This is "The OCR Blindspot" at the system level.

### Folder Structure for Automation

```
~/Documents/Invoices/
  _inbox/              # New files land here (from watched folder or manual drop)
  _processing/         # Currently being extracted and classified
  _needs-review/       # Low-confidence extractions awaiting human check
  _paid/               # Payment confirmed -- ready for end-of-month archive
  2024/                # Archived by year
    Q1/
      01-January/
      02-February/
      03-March/
    Q2/
    ...
  _duplicate-log.csv   # All detected duplicates and resolution actions
  _extraction-log.csv  # Every extraction result with confidence scores
```

**Why separate _inbox and _processing:** If the extraction script crashes mid-processing, the file is still in `_processing`. Restart picks up where it left off. If you process directly from `_inbox`, a crash loses the file's processing state.

## Batch Processing Workflow

### Six-Stage Pipeline

Every invoice passes through six stages. Each stage is idempotent -- re-running a stage on the same file produces the same result without side effects.

**Stage 1: SCAN**
Discover all files in `_inbox/`. Record filename, extension, file size, file hash (SHA-256). Write manifest to `_processing/batch-YYYYMMDD-HHMMSS.json`.

**Stage 2: CLASSIFY**
For each file: determine document type (invoice, receipt, credit note, statement, purchase order). Apply confidence scoring. Route low-confidence files to `_needs-review/`.

**Stage 3: EXTRACT**
For each classified file: run the appropriate extraction pipeline (native text vs OCR). Extract all key fields. Record confidence per field. Write results to the batch manifest.

**Stage 4: VALIDATE**
Cross-check extracted data:
- Does the total equal subtotal + tax? (arithmetic validation)
- Is the invoice number unique? (duplicate check against vendor profile DB)
- Is the date within expected range? (not in the future, not >2 years old)
- Is the amount within expected range for this vendor? (anomaly detection)
Flag validation failures for review.

**Stage 5: FILE**
Apply naming convention. Create directory structure if needed. Move file to permanent location. Update the extraction log.

**Stage 6: EXPORT**
Generate accounting-ready CSV. Append to the running export file for the current period. Include all fields needed for the target accounting software.

### Batch Processing Script Skeleton

```python
import json
import hashlib
from datetime import datetime
from pathlib import Path

def run_batch(inbox_dir, output_dir):
    batch_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    manifest = {"batch_id": batch_id, "files": [], "stats": {}}

    # Stage 1: SCAN
    files = list(inbox_dir.glob("*"))
    files = [f for f in files if f.is_file() and f.suffix.lower()
             in {".pdf", ".jpg", ".jpeg", ".png"}]
    manifest["stats"]["total_files"] = len(files)

    for f in files:
        file_hash = hashlib.sha256(f.read_bytes()).hexdigest()
        manifest["files"].append({
            "original_name": f.name,
            "hash": file_hash,
            "size_bytes": f.stat().st_size,
            "stages_completed": [],
        })

    # Stages 2-6: process each file through the pipeline
    for entry in manifest["files"]:
        filepath = inbox_dir / entry["original_name"]
        # classify(filepath, entry)
        # extract(filepath, entry)
        # validate(entry)
        # file_document(filepath, entry, output_dir)
        # export_record(entry)

    # Write manifest
    manifest_path = output_dir / f"batch-{batch_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest
```

## Vendor Profile Database

After processing 3+ invoices from the same vendor, build a profile to accelerate future extractions:

### Profile Schema

```json
{
  "vendor_id": "vendor_adobe",
  "canonical_name": "Adobe",
  "name_variants": ["Adobe Inc.", "Adobe Systems", "ADOBE SYSTEMS INCORPORATED", "Adobe Creative Cloud"],
  "tax_id": "77-0493581",
  "default_gl_account": "6800",
  "default_category": "Software & Subscriptions",
  "currency": "USD",
  "typical_amount_range": {"min": 20.00, "max": 600.00},
  "invoice_number_pattern": "INV-\\d{8}",
  "payment_terms": "Net 30",
  "invoices_processed": 12,
  "last_invoice_date": "2024-03-15",
  "country": "US",
  "notes": "Monthly Creative Cloud subscription. Annual Acrobat Pro renewal in November."
}
```

### Profile Learning Rules

- **After 3 invoices:** Create profile with canonical name, default GL account, typical amount range
- **After 5 invoices:** Add invoice number pattern, lock payment terms
- **After 10 invoices:** Flag any invoice deviating >50% from typical amount range as anomalous
- **On vendor name mismatch:** If OCR extraction differs from profile but fuzzy match >80%, use the profile's canonical name. If <80%, flag for review.

### Amount Range Anomaly Detection

Calculate mean and standard deviation from historical invoices. Flag new invoices where amount falls outside 2 standard deviations from the mean.

Exception: Vendors with known seasonal variation (annual renewals, quarterly true-ups). Add `"variable_billing": true` to the profile and extend the range to 3 standard deviations.

## Reconciliation Workflow

### Invoice-to-Bank Transaction Matching

Match filed invoices against bank statement transactions to confirm payment:

**Matching criteria (in priority order):**
1. Exact amount match + vendor name match + date within 5 business days = auto-reconcile
2. Exact amount match + date within 10 days + no vendor match = suggest match, flag for review
3. Amount within 2% + vendor match + date within 15 days = suggest match (covers exchange rate or fee differences)
4. No match found after 45 days = flag as potentially unpaid

**Common reconciliation failures:**
- Payment aggregation: vendor charges 3 invoices on a single bank transaction. Match requires sum-of-invoices logic.
- Credit card delays: 2-5 business day lag between charge and statement posting.
- Currency conversion: Bank converts at a different rate than the invoice amount. Allow 2-5% variance on international invoices.
- Vendor name on bank statement differs from invoice (e.g., bank shows "STRIPE.COM" but invoice says "Stripe, Inc."). Maintain a bank-name-to-vendor mapping table.

## Monthly Close Preparation Checklist

Run this workflow on the 5th business day of each month for the prior month:

```
[ ] 1. Process all remaining invoices in _inbox/ (batch pipeline)
[ ] 2. Review and resolve all files in _needs-review/
[ ] 3. Run duplicate detection across the full month
[ ] 4. Export month's invoices to accounting CSV
[ ] 5. Run reconciliation against bank statement
[ ] 6. Flag unmatched invoices as potentially unpaid (notify AP)
[ ] 7. Flag unmatched bank transactions as missing invoices (request from vendor)
[ ] 8. Generate month-end summary report:
       - Total invoices processed
       - Total amount by category
       - Unresolved items count
       - Year-to-date totals by GL account
[ ] 9. Move confirmed-paid invoices from _paid/ to Year/Month/ archive
[ ] 10. Verify archive folder totals match export CSV totals (checksum)
```

**Why the 5th business day:** Allows time for bank statements to finalize, credit card charges to post, and late-arriving invoices to come in. Processing on the 1st catches only 85-90% of the month's invoices.

## Integration Patterns

### Google Drive Structure

```
My Drive/
  Business Finances/
    Invoices/
      _inbox/          # Shared with bookkeeper (edit access)
      _needs-review/   # Shared with business owner (edit access)
      2024/            # Shared with accountant (view access)
        Q1/
        Q2/
    Exports/
      monthly-export-2024-03.csv
    Reports/
      monthly-summary-2024-03.pdf
```

### Dropbox Business Pattern

Use Dropbox Paper or a shared folder with selective sync. Keep `_inbox/` synced locally for the watchdog script. Archive folders can be online-only to save disk space.

### Local-First with Cloud Backup

For businesses that prefer local control:
1. Process everything locally (fastest, no API costs)
2. After monthly close, sync the archive and exports to cloud storage
3. Keep 12 months locally, archive older years to cloud-only
4. Maintain the vendor profile database locally (contains no sensitive financial data, safe to sync)
