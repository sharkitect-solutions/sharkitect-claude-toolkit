---
name: xlsx
description: "Use when the task involves creating, editing, analyzing, or recalculating .xlsx, .xlsm, .csv, or .tsv files -- especially financial models, structured data exports, or formula-driven spreadsheets. NEVER for purely in-memory data analysis where no file output is needed."
license: Proprietary. LICENSE.txt has complete terms
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# xlsx Skill

## File Index

| File | Purpose |
|------|---------|
| `SKILL.md` | Rules, standards, and workflow for all Excel operations |
| `recalc.py` | LibreOffice-based formula recalculation and error detection |
| `LICENSE.txt` | Complete license terms |

---

## Rationalization Table

| Rule | Why It Exists | What Goes Wrong Without It |
|------|--------------|---------------------------|
| Use Excel formulas, never Python-calculated hardcodes | Spreadsheets must recalculate when inputs change | Model breaks on first scenario change; outputs become stale immediately |
| Run recalc.py after every openpyxl write | openpyxl stores formulas as strings; values are not evaluated | File opens with stale cached values or #VALUE! errors; recipient sees wrong numbers |
| Blue/black/green/red text color coding | IB standard lets any analyst instantly identify input vs. formula vs. link | Auditing is slow; formula cells get accidentally overwritten by users |
| Zeros display as "-" not "0" | Financial convention; zero clutter harms readability of sparse models | Models look amateur; key non-zero cells are hard to find visually |
| Assumptions in dedicated cells, never inline | Enables scenario analysis and sensitivity tables | Changing one assumption requires hunting through 50 formula strings |
| Years formatted as text strings | Prevents Excel from treating column headers as numbers and summing them | Year headers appear as "2,024" or get auto-converted in unexpected ways |
| Document all hardcoded values with source comments | Audit trail and reproducibility requirement | Nobody can validate the model or update it when data refreshes |

---

## NEVER List

- NEVER deliver a file with formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?). Zero tolerance.
- NEVER hardcode a calculated value that Excel can derive via formula. Write the formula string instead.
- NEVER open an openpyxl workbook with `data_only=True` and then save it -- this permanently destroys all formulas and replaces them with static values.
- NEVER skip recalc.py when the output file contains formulas. Always run it and fix any errors before delivering.
- NEVER impose your own formatting conventions on an existing file that has established patterns. Study and match what is already there.
- NEVER format years as numbers (1,024 style). Always write year headers as text strings.
- NEVER display negative numbers with a minus sign in financial models. Use parentheses: (123) not -123.
- NEVER leave hardcoded inputs without a source comment. Every hardcode needs: System, Date, Specific Reference, URL if available.

---

## Red Flags

Stop and verify if any of these are true before saving:

- [ ] A formula cell contains a literal number that should be derived from other cells
- [ ] Python code calculates a value and assigns it directly to a cell (e.g., `sheet['B10'] = total`)
- [ ] recalc.py has not been run after openpyxl wrote formulas to the file
- [ ] A year header is formatted as a number (shows thousands separator or is right-aligned)
- [ ] Any cell shows a zero as "0" instead of "-" in a financial model context
- [ ] A cross-sheet reference uses the wrong format (must be `Sheet1!A1`, not `A1` alone)
- [ ] A file was loaded with `data_only=True` for reading and then saved -- formulas are now gone
- [ ] An assumption (growth rate, margin, multiple) is embedded directly inside a formula string instead of referencing a dedicated cell
- [ ] Color coding was not applied and this is a financial model
- [ ] A hardcoded number has no source comment

---

## Tool Selection

| Situation | Tool | Reason |
|-----------|------|--------|
| Data analysis, aggregation, statistics | pandas | Vectorized operations, fast, easy filtering |
| Formula writing, cell formatting, complex layouts | openpyxl | Full access to Excel object model |
| Recalculating formulas after openpyxl writes | recalc.py | openpyxl does not evaluate formulas |
| Reading calculated values from an existing file | openpyxl `data_only=True` | Returns cached values without re-evaluating |

Use pandas for reading and analyzing. Use openpyxl for writing anything that requires formulas or formatting. Never mix responsibilities: do not use pandas to write a financial model.

---

## Output Requirements: All Excel Files

### Zero Formula Errors (Non-Negotiable)
Every file must be delivered with zero formula errors. Run recalc.py and fix every error before delivery. The acceptable error count is 0.

### Preserve Existing Templates
When modifying an existing file: study its format, style, and conventions first. Match them exactly. Existing template conventions override all guidelines below. Never impose standardization on a file that already has patterns.

---

## Financial Model Standards

### Color Coding (IB Convention)

Apply these colors unless the existing file uses different conventions or the user specifies otherwise.

| Color | RGB | Meaning |
|-------|-----|---------|
| Blue text | 0, 0, 255 | Hardcoded inputs -- numbers users change for scenarios |
| Black text | 0, 0, 0 | All formulas and calculations |
| Green text | 0, 128, 0 | Cross-sheet links (same workbook, different sheet) |
| Red text | 255, 0, 0 | External links to other files |
| Yellow background | 255, 255, 0 | Key assumptions requiring attention or cells pending update |

In openpyxl, set font color via `Font(color="0000FF")` using hex. Blue = `"0000FF"`, Black = `"000000"`, Green = `"008000"`, Red = `"FF0000"`.

### Number Formatting Standards

| Data Type | Format String | Notes |
|-----------|--------------|-------|
| Currency | `$#,##0;($#,##0);-` | Units in header: "Revenue ($mm)" |
| Percentage | `0.0%` | One decimal default |
| Multiples | `0.0x` | EV/EBITDA, P/E, etc. |
| Years | Text string | Write as `"2024"` not `2024` |
| Zeros | `-` via format | Include in all numeric formats |
| Negatives | Parentheses `(123)` | Never use minus sign in financial output |

The format string `$#,##0;($#,##0);-` handles all three cases: positive (currency), negative (parentheses), zero (dash).

### Assumptions Placement

Place every assumption -- growth rates, margins, discount rates, multiples, tax rates -- in a dedicated cell on an assumptions sheet or assumptions section. Reference it by cell address in every formula that uses it.

**Wrong:**
```python
sheet['C5'] = '=B5*1.05'   # Growth rate hardcoded in formula
```

**Correct:**
```python
sheet['B2'] = 0.05              # Growth rate assumption cell (blue font)
sheet['C5'] = '=B5*(1+$B$2)'   # Formula references assumption
```

This is the single biggest structural difference between a professional model and a static table.

### Hardcoded Value Documentation

Any cell containing a hardcoded value sourced from external data requires a comment:

Format: `Source: [System/Document], [Date], [Specific Reference], [URL if applicable]`

Examples:
- `Source: Company 10-K, FY2024, Page 45, Revenue Note, https://sec.gov/...`
- `Source: Bloomberg Terminal, 2025-08-15, AAPL US Equity`
- `Source: FactSet, 2025-08-20, Consensus Estimates Screen`

---

## Formulas vs. Python Calculations

This is the most commonly violated rule. openpyxl writes whatever value you assign to a cell. If you compute a total in Python and assign the number, that number is frozen forever. Write formula strings instead.

**Wrong pattern:**
```python
total = df['Sales'].sum()
sheet['B10'] = total          # Frozen. Will not update if Sales changes.
```

**Correct pattern:**
```python
sheet['B10'] = '=SUM(B2:B9)'  # Recalculates automatically.
```

This applies to every calculation: sums, averages, growth rates, ratios, differences, percentages. If Excel has a function for it, use it.

---

## Recalc Workflow (Mandatory When Formulas Are Present)

openpyxl writes formula strings but does not evaluate them. The file contains correct formula text but stale or empty calculated values. recalc.py uses LibreOffice to open the file, recalculate all sheets, scan for errors, and return a JSON report.

**Run after every openpyxl save that introduced formulas:**

```bash
python recalc.py output.xlsx
python recalc.py output.xlsx 60   # Optional timeout in seconds
```

**Interpreting the output:**

```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {}
}
```

If `status` is `"errors_found"`, `error_summary` lists error types with counts and cell addresses. Fix every error, save again, re-run recalc.py. Repeat until `total_errors` is 0.

**Common errors and causes:**

| Error | Typical Cause |
|-------|--------------|
| `#REF!` | Cell reference points to a deleted row/column or out-of-bounds range |
| `#DIV/0!` | Formula divides by a cell that contains zero or is empty |
| `#VALUE!` | Wrong data type in formula (e.g., text where number expected) |
| `#NAME?` | Misspelled function name or undefined named range |

recalc.py automatically configures the LibreOffice macro on first run. LibreOffice must be installed.

---

## Formula Verification Checklist

Run this before calling recalc.py to catch the most common mistakes early:

- [ ] Test 2-3 sample cell references manually -- confirm they pull the correct values
- [ ] Verify column mapping: Excel column 64 = BL, not BK. Count carefully for wide models.
- [ ] Verify row offset: DataFrame row index 5 = Excel row 6 (1-indexed)
- [ ] Check for NaN in source data before referencing those cells in formulas
- [ ] Verify cross-sheet references use correct format: `Sheet1!A1`
- [ ] Check all denominators: any formula using division needs a guard against zero
- [ ] FY projection columns often start at column 50+; verify the offset is correct
- [ ] Search all occurrences of a header/label when mapping, not just the first match

---

## openpyxl Critical Notes

- Cell indices are 1-based: row=1, column=1 is cell A1
- `data_only=True` reads cached calculated values (last saved by Excel or recalc.py)
- **Saving after `data_only=True` permanently destroys formulas.** Read-only means read-only.
- For large files: use `read_only=True` for reading, `write_only=True` for fresh writes
- Formulas must be written as strings starting with `=`

## pandas Critical Notes

- Prefer pandas for reading, aggregating, and analyzing data -- not for writing formula-driven models
- Specify dtypes to prevent inference surprises: `dtype={'id': str}`
- For large files, read only needed columns: `usecols=['A', 'C']`
- `parse_dates=['date_column']` handles date conversion automatically

---

## Code Style

Write minimal Python code for Excel operations. No unnecessary comments, no verbose variable names, no redundant print statements. The code runs; it does not narrate itself.

For Excel file content: add comments to cells with complex formulas or important assumptions. Document all hardcoded values with source references. Include section headers for model navigation.
