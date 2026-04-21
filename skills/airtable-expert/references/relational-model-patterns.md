# Airtable Relational Model Patterns

How to model relationships in Airtable when the relational capability matters. Airtable is a hybrid — it looks like a spreadsheet but has link fields that behave like foreign keys. Using them well requires understanding what it can and can't do.

## Load when

- Modeling parent-child, one-to-many, or many-to-many relationships
- Designing a junction table for a many-to-many with relationship metadata
- Stuck on a rollup that requires a filter AIRTABLE can't express in the condition UI
- Trying to auto-link records via formulas (lookup-by-value, not manual link)
- Migrating from SQL and wondering how Airtable foreign keys behave

## The Link Field (Airtable's Foreign Key)

The `multipleRecordLinks` field type is Airtable's relationship primitive. It is:

- **Bidirectional.** Linking Table A record to Table B record automatically creates the reciprocal link (field on Table B appears with Table A's records).
- **Many-to-many by default.** A `multipleRecordLinks` field holds an ARRAY of linked record IDs. "One-to-many" and "one-to-one" are enforced by convention, not schema.
- **Cross-base capable.** You can link to records in a different base (but that base must be SYNCED into this one first — see api-limitations.md).

**There is no "required" flag on a link.** You can create orphan records (parent without child, child without parent). Enforce relational integrity with automations or formula validators.

**There is no cascade delete.** Deleting a record does not delete its linked records. It removes the link, leaving the other side with an empty array. This is usually what you want; if not, build a custom automation.

## One-to-Many

**Pattern:** one Client has many Invoices.

**Schema:**

| Table | Field | Type | Notes |
|-------|-------|------|-------|
| Clients | Name | singleLineText | Primary |
| Clients | Invoices | multipleRecordLinks → Invoices | Shows all linked invoices |
| Invoices | Invoice # | singleLineText | Primary |
| Invoices | Client | multipleRecordLinks → Clients | Reciprocal; by convention holds 1 record |
| Invoices | Amount | currency | |

**The convention:** "one" side holds a `multipleRecordLinks` field that by convention never holds more than one value. Airtable won't enforce this — it's a discipline.

**To enforce one-side uniqueness:** add a formula field on Invoices:
```
IF(
  LEN(ARRAYJOIN({Client}, ",")) - LEN(SUBSTITUTE(ARRAYJOIN({Client}, ","), ",", "")) >= 1,
  "⚠ Multiple clients linked",
  ""
)
```
Filter a view on `{⚠ Multiple clients linked} != ""` to catch violations.

## Many-to-Many

**Pattern:** Products can be in many Orders; Orders can contain many Products.

**Option A (simplest):** direct `multipleRecordLinks` on both sides.

| Products | Orders |
|---------|--------|
| Name, Price | Order #, Date |
| multipleRecordLinks → Orders | multipleRecordLinks → Products |

**Limitation:** you can't store per-link data (quantity, line-item discount, line-item tax). The link field stores WHICH records, not ABOUT each link.

**Option B (when per-link data matters): junction table**

| Line Items (junction) | Products | Orders |
|----------------------|---------|--------|
| Line Item ID (primary) | Name, Price | Order #, Date |
| Product (link) | multipleRecordLinks ← LineItems | multipleRecordLinks ← LineItems |
| Order (link) | (no direct Orders link) | (no direct Products link) |
| Quantity (number) | | |
| Line Total (formula) | | |

**Why:** now you can roll up `Line Total` from LineItems to Orders (order subtotal) and from LineItems to Products (product YTD revenue). You lose the direct Products ↔ Orders link, but rollups via LineItems reconstruct everything you need.

**When to use which:**
- **Direct m2m:** tags, categories, contributors — anything where the link itself IS the data
- **Junction table:** line items, enrollments, assignments, anything where the relationship has attributes

## Auto-Link via Formula (No — but sort of)

**Question:** can I write a formula that automatically links records based on a value match?

**Answer:** no, not directly. `multipleRecordLinks` requires actual record IDs, and formulas can't output record IDs. BUT there are three workarounds:

### Workaround 1: Automation with "Find records"

Airtable Automation → Trigger (e.g., record created) → Action: Find records (search by value) → Action: Update record (set link field to the found record ID).

This runs in the UI layer, not as a formula. Delay: 5-30 seconds. Reliable for bulk and real-time.

### Workaround 2: Sync key + manual link + formula lookup

Add a `{Sync Key}` text field on both sides. Use a formula (CONCAT or similar) that generates a matching value. Then use Automation ("Find records by sync key") to do the link. This trades formula for automation + an explicit sync key.

### Workaround 3: External tool (Make / n8n / Zapier)

If you need complex linking logic, do the matching outside Airtable and PATCH the link via the records API. This is the pattern for "link this new lead to the company matching the email domain" — the matching logic lives in n8n, Airtable stores the result.

**Do not try to make `multipleRecordLinks` work with a formula-computed value. It doesn't.**

## Rollup with Filter (the hard case)

**Problem:** a rollup's condition UI can't express the filter you need. E.g., "Sum of Line Total for orders where the order's Client is in a specific industry AND the line item's Product is a specific SKU."

**Pattern:** push the condition to the source table as a formula, then roll up the formula.

### Step 1: Add conditional formula on the source (Line Items):
```
Qualified_Amount = IF(
  AND(
    {Order → Client → Industry} = "Hospitality",
    {Product → SKU} = "SKU-042"
  ),
  {Line Total},
  0
)
```
(Note: `{Order → Client → Industry}` and `{Product → SKU}` are LOOKUP fields on Line Items — add them explicitly.)

### Step 2: Roll up Qualified_Amount on the target (e.g., Clients):
- Linked field: LineItems
- Field to roll up: `Qualified_Amount`
- Aggregation formula: `SUM(values)`

**Why it works:** the condition evaluates per-line-item, zeroing out non-matching rows. The rollup then sums the already-filtered values.

**Cost:** one extra formula field per condition pattern. Worth it for the flexibility.

## Lookup Fields

`lookup` fields pull a value from a linked record. They're free (no storage cost, re-evaluated on read).

| Linked Table | Lookup Target | Result |
|--------------|---------------|--------|
| Order | Client.Industry | Order shows its client's industry |
| Line Item | Product.Price | Line item sees product's price (but use a snapshot formula for invoicing — see below) |

**Snapshot anti-pattern:** if you need the price AS OF invoice creation, don't use a Lookup (which updates if Product.Price changes). Instead, use an Automation at record-creation time to COPY the current Product.Price into a Line Item text/number field.

## Rollup vs Lookup vs Formula (quick disambiguation)

| Need | Field Type | Notes |
|------|-----------|-------|
| Pull a single value from linked record | Lookup | Re-evaluated live; updates when source changes |
| Aggregate across multiple linked records | Rollup | `SUM`, `COUNT`, `MAX`, etc. over the array |
| Compute within the current record | Formula | Uses this record's own fields and lookups of linked records |
| Count linked records | Count | Shortcut — just `COUNT` of the link field |

## Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Using direct many-to-many when per-link data is needed | Can't store quantity/attributes | Refactor to junction table |
| Assuming Airtable enforces one-to-one | Silent corruption (multiple linked records) | Add formula validator or pre-check automation |
| Cascade-delete expectations | Orphan links; stale data | Build automation for cascade semantics |
| Rollup with filter via aggregation formula | Returns wrong numbers | Filter in condition UI OR in a pre-computed formula field on source, then roll up the filtered value |
| Using lookup for prices/rates that should be frozen | Historical invoices show current prices, not issue-time prices | Use automation to snapshot value into a plain field |
| Linking across bases without sync | Can't create the link; no cross-base join exists | Set up a sync (Airtable → Base A → Sync → Base B's table), THEN link via the sync target |
| Naming link fields by the linked table ("Clients" field in Invoices table) | Confusing pluralization when the link holds 1 record by convention | Name link fields by their RELATIONSHIP, not the target table ("Client" on Invoices, singular) |

## Schema Design Checklist

Before building:

- [ ] For every relationship, decide: one-to-many? many-to-many? one-to-one?
- [ ] For m2m: is the link itself data (tags/categories) or does it HAVE data (quantity/role)? If the latter, design a junction table.
- [ ] For any relationship with required integrity: design the validator (formula or automation)
- [ ] For any rollup: confirm the filter can be expressed in the condition UI. If not, plan the pre-computed formula field.
- [ ] For any Lookup: confirm you WANT live updates, not a frozen snapshot
- [ ] For any cross-base link: confirm the sync is set up first
- [ ] Name link fields for the relationship, not the target table
