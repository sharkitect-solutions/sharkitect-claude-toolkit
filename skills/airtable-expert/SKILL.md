---
name: airtable-expert
description: "Use when building, modifying, or planning Airtable bases programmatically -- specifically: creating schemas via REST API, hitting a 422/INVALID_REQUEST error from the Airtable API, writing rollup or formula field expressions, designing interfaces (Dashboard / Record Review / Grid), scoping permissions for client-facing bases (interface-only vs full-editor), or modeling parent-child/many-to-many relationships. Triggers on phrases like 'Airtable base', 'create Airtable table', 'Airtable API', 'rollup formula', 'Airtable interface', 'base schema'. Do NOT use for: general REST API design (use backend-architect), SQL database schema (use database-architect), Notion or other non-Airtable no-code platforms (use the relevant platform skill), or generic spreadsheet design without Airtable-specific features (use xlsx skill)."
---

# Airtable Expert

Decisions, limitations, and idioms for building Airtable bases via the REST API and UI. Captures the API-vs-UI capability matrix (what's blocked at the API layer), rollup/formula syntax patterns, interface selection, permission scoping, and relational modeling.

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/api-limitations.md` | About to create/update a field or table via API; got a 422 error; designing a build order (API-first vs UI-finishing); need to know if automations/interfaces/views can be created via API | Working entirely in the Airtable UI with no API/MCP involvement |
| `references/rollup-formula-library.md` | Writing any rollup or formula expression; filtered-sum by single-select; multi-condition AND; date-range filters; string-matching; debugging an expression that returns `#ERROR!` | Reading existing formulas without editing |
| `references/interface-patterns.md` | Designing or modifying an interface page; choosing between Dashboard / Record Review / Grid / List layouts; print-ready layouts; button-action patterns; staff vs client views | Pure data-model work with no interface layer |
| `references/permission-patterns.md` | Setting up client-facing access; deciding interface-only vs full base collaborator; workspace vs base permissions; auditing who can see what | Solo / internal base with no external collaborators |
| `references/relational-model-patterns.md` | Modeling parent-child, one-to-many, or many-to-many; building junction tables; rollup-with-filter workarounds; auto-linking records via formulas | Single-table data with no relationships |

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Create Airtable base with N tables via API" | YES | -- |
| "Getting 422 error creating a formula field" | YES (load api-limitations) | -- |
| "Rollup that sums Amount where Status = Paid" | YES (load rollup-formula-library) | -- |
| "Which interface layout for client-facing KPI dashboard?" | YES (load interface-patterns) | -- |
| "Design REST API for my backend service" | NO | backend-architect |
| "Pick between Airtable, Notion, or Supabase for this use case" | NO | senior-architect (platform-selection scope) |
| "Write SQL schema for Postgres" | NO | database-architect |
| "Analyze CSV and create pivot tables" | NO | xlsx |
| "Automate Airtable -> Slack notifications" | PARTIAL -- use this skill for Airtable side, then n8n-workflow-patterns for the automation | n8n-workflow-patterns for the workflow layer |

## The Core Decision: API or UI?

Before writing any code that touches Airtable, answer this question. Guessing wrong costs 10-30 minutes per field.

```
FIELD TYPE YOU WANT TO CREATE
  |
  +--> Is it one of: singleLineText, multilineText, number,
  |    currency, percent, date, dateTime, checkbox,
  |    singleSelect, multipleSelects, singleCollaborator,
  |    multipleCollaborators, phoneNumber, email, url,
  |    rating, duration, multipleRecordLinks, attachment,
  |    barcode, count, createdTime, lastModifiedTime,
  |    createdBy, lastModifiedBy, autoNumber?
  |      |
  |      YES --> CREATE VIA API (PATCH fields collection)
  |
  +--> Is it: formula, rollup, lookup, count (computed),
       button, ai, syncedFromAnotherBase?
         |
         YES --> CANNOT CREATE VIA API. Document for UI.
                 See references/api-limitations.md for the
                 HUMAN-ACTION-REQUIRED.md template.
```

Rule of thumb: **if the field needs a formula/expression, it is UI-only.** Airtable does not expose formula, rollup, or lookup field creation through the REST API. This is not a bug — it is a product decision that has held since the API was introduced. Do not waste tokens testing it.

## What the API Can Do (quick view)

| Capability | API? | Notes |
|-----------|------|-------|
| Create base | NO | UI only (or duplicate via template) |
| Create table | YES | POST `/meta/bases/{baseId}/tables` |
| Create data-entry field | YES | PATCH `/meta/bases/{baseId}/tables/{tableId}/fields` |
| Create formula/rollup/lookup | **NO** | UI only -- see api-limitations.md |
| Update field name / description | YES | PATCH field |
| Delete table | **NO** | UI only -- rename with `DEPRECATED_` prefix if you can't access UI |
| Delete field | **NO** | UI only |
| Create record | YES | POST records |
| Update record | YES | PATCH records |
| Delete record | YES | DELETE records |
| Create view | **NO** | UI only |
| Create interface page | **NO** | UI only |
| Create automation | **NO** | UI only |
| Link records (multipleRecordLinks) | YES | Pass array of record IDs |

When the API cannot do something the build requires, add an entry to a `HUMAN-ACTION-REQUIRED.md` file in the project so the UI steps are explicit. See `references/api-limitations.md` for the template.

## Anti-Patterns (learned the hard way)

| Name | What Happens | Why It Fails | Fix |
|------|--------------|--------------|-----|
| **The Formula-API Trap** | You write 200 lines of Python to create 12 formula/rollup/lookup fields via API. All 422. | Airtable API rejects formula-bearing fields at field-creation time, not with a helpful error. | Skip the script. Document all formula/rollup/lookup fields in HUMAN-ACTION-REQUIRED.md for UI creation. |
| **The Rollup-Without-Filter Bug** | Rollup shows total of ALL linked records, not just the ones matching your condition. | Airtable rollup has TWO filter layers: the linked-records filter AND the aggregation formula filter. Missing the second = no filter. | Use `SUM(IF(AND({Status}="Paid",{Amount}),{Amount},0))` as the aggregation formula, not just `SUM({Amount})`. See rollup-formula-library.md. |
| **The Interface-Permission Gotcha** | You share a base with a client via interface, then they see ALL base tables in the left nav. | "Interface-only" requires explicit base permission level = "none" on the collaborator, not just interface sharing. | Add collaborator with base role "none", THEN share specific interface(s). See permission-patterns.md. |
| **The Junction-Table Omission** | You use multipleRecordLinks for many-to-many, then can't filter rollups by a relationship attribute. | A bare link field has no place to store relationship metadata (date-linked, role, quantity). | Create an explicit junction table with its own fields. See relational-model-patterns.md. |
| **The Delete-Table Dead-End** | You want to remove a deprecated table and realize the API won't delete it, and the UI requires base-owner permission. | Airtable has no table-delete endpoint. If you aren't a base owner, only rename is available. | Rename to `DEPRECATED_<tablename>` and log in HUMAN-ACTION-REQUIRED.md for the owner to delete manually. |
| **The Automation-Blind-Build** | You design a build assuming you can create automations via API, then realize on delivery day that you can't. | All Airtable automations (triggers, actions, scripts) are UI-only. API has no automation endpoints. | Design the automation specs in HUMAN-ACTION-REQUIRED.md alongside the schema spec, so UI setup takes <30 min. |
| **The Synced-Base Assumption** | You try to programmatically create or modify a synced-from-another-base connection. | Cross-base sync is configured in the UI only; the synced fields appear read-only in the target base. | Create the sync in the UI first; your API can only read and write non-synced fields in the target. |
| **The Interface-Layout-Wrong-Choice** | You build a KPI dashboard using Grid layout and the client sees a scrollable spreadsheet instead of headline numbers. | Grid shows rows; Dashboard shows summarized metrics with filters and charts. Different layout, different purpose. | Pick layout by primary task: "view individual records one-at-a-time" = Record Review; "scan many at once with filters" = Grid; "summarized metrics / KPIs" = Dashboard. See interface-patterns.md. |

## Build Workflow (API + UI)

For any non-trivial Airtable build:

```
1. Design schema on paper -- tables, fields, relationships, rollups, interfaces
2. Classify each field: API-creatable or UI-only
3. Write schema doc (docs/airtable-schema-v<N>.md) -- full spec, all fields
4. Write HUMAN-ACTION-REQUIRED.md -- every UI-only field/view/automation/interface
5. Build API-creatable fields programmatically (one POST per table, one PATCH per field batch)
6. Deliver HUMAN-ACTION-REQUIRED.md to base owner for UI setup
7. Create interfaces last -- after all fields (including formulas) exist
8. Test with a seed record flowing through the full pipeline
```

**Do not try to do everything via API and then "finish" in UI.** The API-vs-UI split is architectural — design for it from step 1. Trying to make API do UI work is the single largest source of wasted time on Airtable builds.

## API Reference Quick Card

```bash
# Auth: Personal Access Token (PAT) via Bearer header
AIRTABLE_PAT="pat_..."
BASE_ID="app..."

# Get base schema
curl -H "Authorization: Bearer $AIRTABLE_PAT" \
  "https://api.airtable.com/v0/meta/bases/$BASE_ID/tables"

# Create table
curl -X POST \
  -H "Authorization: Bearer $AIRTABLE_PAT" \
  -H "Content-Type: application/json" \
  -d '{"name":"Invoices","fields":[{"name":"Invoice #","type":"singleLineText"}]}' \
  "https://api.airtable.com/v0/meta/bases/$BASE_ID/tables"

# Add fields to existing table (one at a time via POST to fields endpoint)
curl -X POST \
  -H "Authorization: Bearer $AIRTABLE_PAT" \
  -H "Content-Type: application/json" \
  -d '{"name":"Amount","type":"currency","options":{"precision":2,"symbol":"$"}}' \
  "https://api.airtable.com/v0/meta/bases/$BASE_ID/tables/$TABLE_ID/fields"

# Insert records (batched, up to 10 per call)
curl -X POST \
  -H "Authorization: Bearer $AIRTABLE_PAT" \
  -H "Content-Type: application/json" \
  -d '{"records":[{"fields":{"Invoice #":"INV-001","Amount":1500}}]}' \
  "https://api.airtable.com/v0/$BASE_ID/$TABLE_ID"
```

Rate limit: 5 requests/second per base. Exceeding returns 429 with a 30-second lockout. For bulk inserts, batch 10 records per call and `sleep 0.25` between calls.

## Source

HQ Emmanuel FF Admin Database build (2026-04-21) -- 6 tables, ~40 API-creatable fields + 24 formula/rollup/lookup fields. Filed wr-2026-04-21-003 after losing ~10 minutes on a formula-field creation script that was doomed from the start. This skill consolidates that learning plus prior Airtable work so the next build starts at minute 0 knowing exactly what the API can and cannot do.
