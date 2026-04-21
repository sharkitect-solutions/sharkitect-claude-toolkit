# Airtable REST API -- Complete Capability Matrix

What the Airtable REST API (v0, 2026) can and cannot do. This is the reference that prevents the Formula-API Trap.

## Load when

- About to write code that creates fields, tables, views, automations, or interfaces
- Got a 422 `INVALID_REQUEST` from Airtable and need to check if the operation is even supported
- Designing a build order — need to know what's API vs UI
- Scoping a proposal — need accurate estimates for API vs manual work

## The API Surface (Official Endpoints)

### Metadata API (schema operations)

Base path: `https://api.airtable.com/v0/meta/bases/{baseId}`

| Endpoint | Method | What It Does | Gotchas |
|----------|--------|--------------|---------|
| `/tables` | GET | List tables + fields + views (read-only schema) | Returns everything in one payload; for large bases this can be >1MB |
| `/tables` | POST | Create a new table with initial fields | First field must be a primary-field-eligible type (singleLineText typically) |
| `/tables/{tableId}` | PATCH | Update table name or description | Cannot rename primary field via this call — use fields PATCH |
| `/tables/{tableId}/fields` | POST | Add a single field to a table | **Cannot create formula, rollup, lookup, count, button, ai, syncedFromAnotherBase** |
| `/tables/{tableId}/fields/{fieldId}` | PATCH | Rename or redescribe a field | Cannot change field TYPE after creation (delete + recreate required) |

### Records API (data operations)

Base path: `https://api.airtable.com/v0/{baseId}/{tableIdOrName}`

| Endpoint | Method | What It Does | Gotchas |
|----------|--------|--------------|---------|
| (list) | GET | List records with filter/sort/fields/view params | `filterByFormula` max URL length ~16KB — encode carefully |
| (create) | POST | Insert up to 10 records per call | Rate limit 5 req/s per base; batch or sleep |
| (update) | PATCH | Update up to 10 records per call (merge) | Use `PATCH` for merge, `PUT` for full replace |
| (upsert) | PATCH | Upsert via `performUpsert.fieldsToMergeOn` | Only available on records endpoint; can't upsert on relationships alone |
| (delete) | DELETE | Delete up to 10 records per call | No bulk-delete-all-matching; must list first, then delete |

### What's NOT in the API

| Capability | API Status | UI Path |
|-----------|------------|---------|
| Create base | **NOT SUPPORTED** | `+ Add a base` in workspace |
| Duplicate base | **NOT SUPPORTED** | Base header menu → Duplicate |
| Delete base | **NOT SUPPORTED** | Base settings → Delete |
| Delete table | **NOT SUPPORTED** | Table header → Delete |
| Delete field | **NOT SUPPORTED** | Field header → Delete |
| Change field type | **NOT SUPPORTED** | Field edit → Change type |
| Create formula field | **NOT SUPPORTED** | Add field → Formula |
| Create rollup field | **NOT SUPPORTED** | Add field → Rollup |
| Create lookup field | **NOT SUPPORTED** | Add field → Lookup |
| Create count field | **NOT SUPPORTED** | Add field → Count |
| Create button field | **NOT SUPPORTED** | Add field → Button |
| Create view (grid/calendar/kanban/etc.) | **NOT SUPPORTED** | Views sidebar → + |
| Create interface page | **NOT SUPPORTED** | Interfaces tab |
| Modify interface layout | **NOT SUPPORTED** | Interfaces editor |
| Create automation | **NOT SUPPORTED** | Automations tab |
| Attach record comments (structured) | **LIMITED** | `comments` endpoint exists but only text + user mention |
| Create synced base connection | **NOT SUPPORTED** | Sync configuration in base settings |

**Rule:** if it involves computation (formula/rollup/lookup), a view-type, an automation, or interface layout — it is UI-only.

## HTTP Response Codes You Will See

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 200 | OK | Success |
| 201 | Created | Table/field/record successfully created |
| 400 | BAD_REQUEST | Malformed JSON, invalid field name |
| 401 | AUTHENTICATION_REQUIRED | Missing/invalid Bearer token |
| 403 | NOT_AUTHORIZED | PAT scope insufficient (needs `schema.bases:write` for table/field creation) |
| 404 | NOT_FOUND | baseId/tableId typo, or resource deleted |
| 422 | INVALID_REQUEST_UNKNOWN | Trying to create a formula/rollup/lookup field; check field type |
| 422 | UNPROCESSABLE_ENTITY | Field type incompatible with provided options |
| 429 | RATE_LIMITED | Exceeded 5 req/s per base; 30-second cool-down |

**Critical:** a 422 on field creation almost always means "you're trying to create a computed-field type via API." Check your field type against the NOT-supported list above BEFORE retrying.

## PAT (Personal Access Token) Scopes

| Scope | Needed For |
|-------|------------|
| `data.records:read` | GET records |
| `data.records:write` | POST/PATCH/DELETE records |
| `data.recordComments:read` | Read comments |
| `data.recordComments:write` | Create/delete comments |
| `schema.bases:read` | GET tables (list schema) |
| `schema.bases:write` | POST/PATCH tables + fields |
| `webhook:manage` | Create/manage webhooks |

A PAT that only has `data.records:*` will fail with 403 on any schema operation. Audit scopes at https://airtable.com/create/tokens.

## HUMAN-ACTION-REQUIRED.md Template

When the API can't do something the build needs, write this file in the project root:

```markdown
# HUMAN-ACTION-REQUIRED — <Project Name>

Items the API cannot create. Complete these in the Airtable UI before the base is ready for production use.

**Base:** `<baseId>` — link: https://airtable.com/<baseId>
**Last updated:** <YYYY-MM-DD>

## UI-only fields to create

For each, go to the table → `+ Add field` → select the type → configure per the spec below.

### Table: Invoices

| Field Name | Type | Formula / Config | Notes |
|-----------|------|------------------|-------|
| Balance Due | Formula | `{Total} - {Amount Paid}` | Format: currency ($) 2 decimals |
| Days Outstanding | Formula | `IF({Status}="Paid",0,DATETIME_DIFF(TODAY(),{Invoice Date},"days"))` | Format: integer |
| Client Total YTD | Rollup | Link: `Client`, Aggregation: `SUM(IF(YEAR({Invoice Date})=YEAR(TODAY()),{Total},0))` | Format: currency |

## Views to create

| Table | View Name | Type | Filter | Sort |
|-------|-----------|------|--------|------|
| Invoices | Overdue | Grid | `{Status}!="Paid" AND {Days Outstanding}>30` | Days Outstanding desc |
| Invoices | This Month | Grid | `IS_SAME({Invoice Date},TODAY(),"month")` | Invoice Date desc |

## Automations to create

| Name | Trigger | Actions | Notes |
|------|---------|---------|-------|
| Overdue Alert | Record matches conditions (Status!=Paid AND Days Outstanding>14) | Send email to {Assigned Staff} | Configure daily schedule check |

## Interfaces to create

| Interface Name | Pages | Audience |
|----------------|-------|----------|
| Admin Console | Data Entry (Record Review on Invoices), Monthly Close (Dashboard) | Internal staff |
| Client Portal | Invoice History (Grid filtered to {Client}=currentUser) | Interface-only collaborators |
```

## Why the API Won't Grow These Features

These are not on Airtable's roadmap at the time of writing:

- **Formula/rollup/lookup via API:** Would require exposing the formula parser and syntax validator as a public API surface. Airtable treats formulas as a UI-first product feature.
- **Interface creation via API:** Interfaces are a pixel-level layout tool; building one via JSON is a product redesign, not an API endpoint.
- **Automation via API:** Automations execute server-side in Airtable's infrastructure; exposing creation via API would compete with Zapier/Make and complicate the runtime model.
- **Table/field delete via API:** Intentional — destructive schema ops require UI confirmation to prevent cascading data loss.

Design builds around these constraints. Do not hope for them to change.
