# Airtable Rollup & Formula Library

Idiomatic expressions for the patterns that take people 30 minutes to figure out on their own. Grouped by what you're actually trying to do.

## Load when

- Writing any rollup or formula field and the expression is not obvious
- Getting `#ERROR!` in a formula or rollup and need to diagnose
- Migrating logic from another system (Excel, Airtable competitor, SQL)
- Trying to do a filtered aggregation and the built-in rollup filter isn't enough

## The Two Filter Layers (understand this first)

Rollup fields have TWO independent filter points. Getting either one wrong is the #1 cause of wrong totals.

```
LINKED RECORD SET
       |
       v
  [Filter 1: Conditions on linked records]  <-- uses Airtable's "condition" UI
       |  Keeps only records where e.g. {Status} = "Paid"
       v
  [Filter 2: Aggregation formula]  <-- uses formula syntax
       |  Applies SUM, COUNT, IF, etc. to the surviving records
       v
  FINAL VALUE
```

**Default mistake:** you set Filter 1 correctly, then write `SUM({Amount})` in Filter 2. That works. BUT if you skip Filter 1 and just write `SUM({Amount})`, you sum ALL linked records — the "condition" interface was your only filter.

The safe pattern: **filter in BOTH layers when correctness matters.** Redundant filtering does no harm; missing a filter silently returns the wrong number.

## Rollup: Filtered Sum by Single-Select

**Goal:** Sum `{Amount}` of linked records where `{Status}` = "Paid"

Option A — use the condition UI for the filter (cleanest):
- Linked field: Invoices
- Condition: `Status` is `Paid`
- Aggregation formula: `SUM(values)`

Option B — conditional in the aggregation formula (works even if condition UI is awkward):
- Linked field: Invoices (no condition)
- Aggregation formula: `SUM(IF({Status}="Paid",{Amount},0))`

**Wait — that's wrong.** In a rollup formula, you can't reference the linked record's fields by name. `values` is the implicit variable representing the array of rolled-up values. You must set the "Field to roll up" = `Amount`, then use `values`:

- Field to roll up: `Amount`
- Aggregation formula: `SUM(values)`

If you need conditional logic, it lives in the CONDITION UI, not the aggregation formula — the aggregation formula operates on the post-filter array only.

**Correct Option B:** Condition UI sets `Status = Paid`, aggregation is `SUM(values)`.

Memorize: **the aggregation formula has access to `values` (the array), not individual fields.** If your filter needs to check a field on the linked record, it MUST go in the condition UI.

## Rollup: Multi-Condition Filter

**Goal:** Sum `{Amount}` where `{Status} = "Paid"` AND `{Invoice Date} >= start-of-month`

Condition UI (supports AND by stacking conditions):
- `Status` is `Paid`
- `Invoice Date` is after `first day of this month`

Aggregation formula: `SUM(values)`

If the UI lacks an appropriate operator (e.g., "same fiscal quarter"), you have to widen the condition UI filter and narrow in the aggregation formula — but this requires the ROLLED-UP FIELD to carry the needed data. Example: roll up a pre-computed boolean field `Is_In_FQ` from the linked table (a formula field on the linked table that evaluates the fiscal logic).

## Formula: Date Math

| Goal | Expression |
|------|-----------|
| Days between two dates | `DATETIME_DIFF({End}, {Start}, "days")` |
| Days overdue (0 if paid) | `IF({Status}="Paid", 0, DATETIME_DIFF(TODAY(), {Due Date}, "days"))` |
| Month number | `MONTH({Date})` |
| Year-Month text (for grouping) | `DATETIME_FORMAT({Date}, "YYYY-MM")` |
| First day of month | `DATETIME_FORMAT({Date}, "YYYY-MM-01")` |
| Is this month? | `IS_SAME({Date}, TODAY(), "month")` |
| Is within last 30 days? | `IS_AFTER({Date}, DATEADD(TODAY(), -30, "days"))` |
| Age in years (from birthdate) | `DATETIME_DIFF(TODAY(), {DOB}, "years")` |
| Business days between dates | `WORKDAY_DIFF({Start}, {End})` |

Edge case: `DATETIME_DIFF` returns a number; `DATEADD` returns a date. Mixing them accidentally returns weird values. Always wrap in the expected output type.

## Formula: String / Text

| Goal | Expression |
|------|-----------|
| Concat first + last name | `{First} & " " & {Last}` or `CONCATENATE({First}, " ", {Last})` |
| Uppercase | `UPPER({Field})` |
| Lowercase | `LOWER({Field})` |
| Trim whitespace | `TRIM({Field})` |
| Substring (first 10 chars) | `LEFT({Field}, 10)` |
| Substring (last 4 chars) | `RIGHT({Field}, 4)` |
| Find position of substring | `FIND("@", {Email})` returns 1-based index, 0 if not found |
| Replace | `SUBSTITUTE({Field}, "old", "new")` |
| Contains (case-sensitive) | `FIND("needle", {Field}) > 0` |
| Contains (case-insensitive) | `FIND("needle", LOWER({Field})) > 0` |
| Starts with | `LEFT({Field}, 4) = "ACME"` |
| Length | `LEN({Field})` |
| Extract domain from email | `RIGHT({Email}, LEN({Email}) - FIND("@", {Email}))` |

## Formula: Conditional / Logic

| Goal | Expression |
|------|-----------|
| Simple if-else | `IF({Amount} > 1000, "High", "Low")` |
| Nested if (chained) | `IF({Status}="Paid","green", IF({Status}="Overdue","red","gray"))` |
| SWITCH on a single-select | `SWITCH({Priority}, "High", 3, "Med", 2, "Low", 1, 0)` |
| AND | `AND({A} > 10, {B} < 20)` |
| OR | `OR({Status}="Paid", {Amount}=0)` |
| NOT | `NOT({Active})` |
| Is empty | `{Field} = BLANK()` or `NOT({Field})` for booleans |
| Is not empty | `{Field} != BLANK()` |

## Formula: Arrays (from linked records or multi-select)

These apply when the field being referenced is a `multipleSelects`, `multipleCollaborators`, or `lookup` result.

| Goal | Expression |
|------|-----------|
| Join array into comma-separated string | `ARRAYJOIN({Tags}, ", ")` |
| Count array elements | `LEN({Tags}) > 0 ? LEN(ARRAYJOIN({Tags}, ",")) - LEN(SUBSTITUTE(ARRAYJOIN({Tags}, ","), ",", "")) + 1 : 0` (ugly but works) |
| Check if array contains value | `FIND(",target,", "," & ARRAYJOIN({Tags}, ",") & ",") > 0` |
| Flatten nested lookup arrays | `ARRAYFLATTEN({LookupField})` |
| Unique values | `ARRAYUNIQUE({LookupField})` |
| Compact (remove nulls) | `ARRAYCOMPACT({LookupField})` |

## Rollup: Aggregation Reference

The aggregation formula operates on `values` — the post-filter array of rolled-up values.

| Goal | Expression |
|------|-----------|
| Sum | `SUM(values)` |
| Count (non-empty) | `COUNTALL(values)` or `COUNT(values)` for numbers |
| Average | `AVERAGE(values)` |
| Min / Max | `MIN(values)` / `MAX(values)` |
| First / Last | `values[0]` — NOT SUPPORTED; use `ARRAYJOIN(values, ",")` and parse, or use a formula field on source |
| Concatenated string | `ARRAYJOIN(values, ", ")` |
| Unique count | `COUNTALL(ARRAYUNIQUE(values))` |
| Sum where sub-condition | Do NOT attempt in aggregation formula. Push condition to either (a) condition UI, or (b) a formula field on the source table that pre-computes the value (e.g. `Amount_If_Paid = IF({Status}="Paid",{Amount},0)`), then roll up THAT field with `SUM(values)`. |

## Common #ERROR! Causes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `#ERROR!` in formula | Field name typo, unclosed brace, wrong argument count | Copy the expression to a code editor with bracket matching; re-check field names are spelled exactly |
| Formula evaluates to empty | A referenced field is empty and the formula doesn't handle null | Wrap in `IF({Field}, {Field}, "fallback")` or use `BLANK()`-safe operators |
| Rollup shows wrong total | Filter in aggregation formula that doesn't work (condition must be in UI) | Move filter to the condition UI, keep aggregation as `SUM(values)` |
| Date formula returns number | `DATETIME_DIFF` returns number — you expected a date | Use `DATEADD` instead for a date output |
| Currency format lost | Formula field output type defaults to string/number — format separately | In field options, set format to currency with your symbol/precision |
| Circular reference | A formula references another formula that references it back | Break the cycle; one of them must become stored data (e.g., auto-populated via automation) |

## Performance

- Formulas with `DATETIME_DIFF(TODAY(), ...)` recalculate on every view load. Fine for a few records; noticeable at 10K+.
- Rollups re-aggregate when any source record changes. Keep aggregation formulas simple.
- Lookup fields are cheap (pointer-based); formula fields that reference lookups can be expensive at scale.
- Avoid stacking: formula depends on rollup depends on lookup depends on link. At >3 hops, investigate whether one of the intermediate values should be persisted.
