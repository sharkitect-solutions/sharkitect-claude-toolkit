# SystemLink: Check Distribution Sync — Delivery Completion Plan

## Context

The Check Distribution Sync project for Fantastic Floors is demo-ready (presented April 4) and needs to move to delivery. The key remaining work: **schedule of values (SOV) tracking**, SOW creation, SOP, and historical data migration.

**SOV = flat table, not a hierarchy.** After reviewing the actual client data (120 Oaks, Evrens, etc.), each SOV entry is simply a named section within a project — "Building 1 - Floor 4", "Clubhouse", "Exterior", "Building 5" — with its own budget. No parent-child nesting. The existing Project Breakdown table already has the right structure; it just needs renaming and field cleanup.

**SOV automation included as goodwill** — no pricing change. Chris committed to full payment at completion (not 50/50). Each project gets its own SOW.

---

## What I Learned From the Actual Sheets

**120 Oaks (Painting tab)** — 1 building, 92 units, 4 floors. SOV sections:
- Bldg#1 / 4-floors 23 unit → $59,800
- Bldg#1 / 3-floors 23 unit → $59,800
- Bldg#1 / 2-floors 23 unit → $59,800
- Bldg#1 / 1-floors 23 unit → $59,800
- Clubhouse 2 unit → $5,700
- Exterior → $23,000

**Evrens Apt** — 8 buildings, 358 units. SOV sections per building (e.g., Bldg#1 / 4-floors 31Unit → $104,501). Line items tracked per building with dates, invoice #s, descriptions, amounts, retention.

**Pattern:** Every project breaks down into named sections. Some are floors within one building, some are whole buildings, some are areas (clubhouse, exterior). Flat list, linked to parent project. No hierarchy needed.

---

## Priority Order & Dependencies

```
Google Sheet (SOV collection)  ──→  Data Migration (needs filled sheet)
         │                                    │
         ▼                                    ▼
Schema Cleanup (can start now)  ──→  Dashboard Enhancement
         │
         ▼
n8n Workflow Updates (needs schema)

SOW (write in parallel — no dependencies)
SOP (write in parallel — inform by schema decisions)
```

**Critical path:** Google Sheet → send to Jesus → wait for responses → migrate data. Start schema cleanup and SOW/SOP immediately in parallel.

---

## Workstream 1: Google Sheet — SOV Data Collection (DO FIRST)

**Goal:** Enhance the existing project list Google Sheet so Jesus can provide project details + SOV information.

**Existing sheet:** Already has project list. Needs additions.

### Sheet 1 Additions (Project Master List)
Add columns to existing project list:
- **Status**: Active / On Hold / Completed
- **Budget**: Total project budget ($)
- **Has Schedule of Values?**: Yes / No
- **SOV Notes**: Free text (e.g., "8 buildings, 4 floors each")
- **Pull Into System?**: Yes / No (some projects may be too old to migrate)

### New Sheet 2: Schedule of Values Detail
For every project marked "Has Schedule of Values = Yes":

| Column | Description | Example |
|--------|-------------|---------|
| Parent Project | Project name (from Sheet 1) | 120 Oaks Apartments |
| SOV Name | Section identifier | Building 1 - Floor 4 |
| Units | Unit count for this section | 23 |
| Section Budget | Budget for this section ($) | $59,800 |
| QBO Description Format | How they'll write it on checks | "Building 1, Floor 4" |

**Examples of SOV Names:**
- `Building 1 - Floor 4` (building + floor)
- `Building 5` (just building, no floor breakdown)
- `Clubhouse` (area)
- `Exterior` (area)

### New Sheet 3: Description Standardization Guide
Quick reference for QBO check descriptions:

**Format:** `SOV Name - Additional Description`

**Examples:**
- `Building 1, Floor 1 - Paint and materials`
- `Building 1 - Drywall`
- `Clubhouse - Paint`
- `Exterior - Primera Limpieza`

The SOV Name portion (before the dash) is what the system matches. The additional description (after the dash) is free-text for their reference. Since the check is already linked to the project (via QBO customer field), the SOV Name alone is enough to identify the section.

### Execution
- Use gws CLI to add columns/sheets to existing spreadsheet
- Pre-populate Sheet 1 with project names from existing data
- Pre-populate Sheet 2 with known SOV data (e.g., 120 Oaks sections from the painting tab)
- Add data validation dropdowns where possible
- Send to Jesus with brief instructions

### Source data for pre-population
- Spreadsheet `1zp-cVodkjRXWan7y97hy7kZCL1cZr0wDjL78B7rp4OQ` — 26 tabs showing project breakdowns
- Tab names give us project list: McGee, Evrens, 120 Oak, Alto, Mission 77, Guadalupe, Treadway, etc.
- Tab data gives us SOV structures (buildings, floors, budgets)

---

## Workstream 2: Airtable Schema — Simplify & Rename

**Goal:** Rename "Project Breakdown" to "Schedule of Values", remove unused columns, keep it flat.

### Current State (Table 2: `tblKCwcferE8wHrjn`)
14 fields including Breakdown Name, Project, Building, Floor, Units, Trade, Section Budget, Total Spent, Budget Used %, Budget Status, Retention, Last Payment Date, Checks link, Check Line Items link.

### Changes

**Rename table:** "Project Breakdown" → "Schedule of Values"

**Remove fields:**
- Building (embedded in Breakdown Name)
- Floor (embedded in Breakdown Name)
- Trade (comes from check descriptions, not the SOV record)

**Keep fields (final list):**
1. Breakdown Name (primary) — e.g., "Building 1 - Floor 4"
2. Project (link to Projects)
3. Units (number)
4. Section Budget (currency)
5. Total Spent (rollup from Check Line Items → Effective Amount)
6. Budget Used % (formula)
7. Budget Status (formula — traffic light)
8. Retention (rollup from linked CLI or Retainers)
9. Last Payment Date (rollup from Checks)
10. Checks (link to Checks)
11. Check Line Items (link to Check Line Items)

**No new fields needed on SOV table.** No Type column, no parent-child links. Flat table.

### Budget Mismatch Guardrail (add to Projects table)

**Problem:** When a project has SOV sections, the sum of all SOV section budgets should equal the project's total budget. Data entry errors (wrong amount on one section) should be caught immediately.

**New fields on Projects table:**

| Field | Type | Formula/Config |
|-------|------|----------------|
| SOV Budget Total | Rollup | SUM of `Section Budget` from linked Schedule of Values records |
| Budget Mismatch | Formula | `IF(AND({SOV Budget Total} > 0, {Budget} > 0, {SOV Budget Total} != {Budget}), "MISMATCH: " & IF({SOV Budget Total} > {Budget}, "$" & ({SOV Budget Total} - {Budget}) & " OVER", "$" & ({Budget} - {SOV Budget Total}) & " UNDER"), IF(AND({SOV Budget Total} > 0, {Budget} > 0), "✓ Matched", ""))` |

**Example:** Project=$100K. Four SOV sections at $25K + $25K + $25K + $30K = $105K. Budget Mismatch shows **"MISMATCH: $5,000 OVER"**. They fix it before any checks come in.

**Dashboard:** Add a filtered view showing only projects with budget mismatches — instant visibility into data entry errors. Can hide the SOV Budget Total rollup field if desired (it powers the formula but doesn't need to be visible).

### Execution
- Rename table via Airtable API or MCP
- Delete Building, Floor, Trade fields via API
- Update schema design doc
- Test: create sample SOV record, link a CLI record, verify rollups

### Impact on other tables
- **Check Line Items** field 18 ("Project Breakdown") → rename to "Schedule of Values" (link name changes when table renames)
- **Checks** field 11 ("Project Breakdown") → same rename
- **Projects** field 12 ("Project Breakdown") → same rename
- n8n workflow references to "Project Breakdown" table ID stay the same (IDs don't change on rename)

### File to update
- `knowledge-base/clients/fantastic-floors/systemlink-check-distribution/airtable-schema-design.md` — rewrite Table 2 section

---

## Workstream 3: n8n Workflow — Description Parsing for SOV (with Fuzzy Matching)

**Goal:** Parse the SOV Name from QBO check descriptions and auto-link line items to the correct Schedule of Values record. Use fuzzy matching to handle typos and abbreviations.

### Why Description (not Tags)
**Investigated:** QBO Tags are check-level only (confirmed in `create_check_dist_workflow_v3.py` line 139: `check.Tag?.Name`). Tags apply to the whole check, not individual line items. A check with line items for different SOV sections can't be distinguished by tags. QBO also doesn't support custom dropdown fields on check line items. Description is the only free-text field available per line item — it's the only viable option for SOV identification at the line level.

### Naming Convention (from SOP)
Description format: `SOV Name - Additional Description`
- `Building 1, Floor 1 - Paint and materials`
- `Building 1 - Drywall`
- `Clubhouse - Paint`
- `Exterior - Primera Limpieza`

**Parsing logic:** Take everything before the first ` - ` (space-dash-space) as the SOV Name.

### New Logic in n8n Code Node
1. **Parse SOV Name** from description: `description.split(' - ')[0].trim()`
2. **Fuzzy match** against Schedule of Values records for that project:
   - Normalize both strings (lowercase, trim whitespace, remove extra spaces)
   - Try exact match first
   - If no exact match: try contains-match (SOV Name contains the record name or vice versa)
   - If no contains-match: try similarity scoring (Levenshtein distance or similar) — match if >80% similar
   - Common abbreviation handling: `Bldg` = `Building`, `Fl` = `Floor`, `Ext` = `Exterior`, `CH` = `Clubhouse`
3. **If matched** → link CLI record + Check record to that SOV
4. **If not matched** → leave SOV field empty, item can still be assigned manually in Airtable dashboard

### Typo Mitigation Strategy (3 layers)
1. **Prevention:** Printed/posted reference sheet of valid SOV Names for each project. Include in SOP and training.
2. **Tolerance:** Fuzzy matching in n8n catches minor typos, abbreviations, and capitalization differences.
3. **Recovery:** Unmatched items are visible in the dashboard for manual SOV assignment (same pattern as Unassigned → CLI).

### Find-or-Match Pattern (NOT find-or-create)
Unlike Projects/Vendors, SOV records should NOT be auto-created. They're manually seeded from the discovery sheet. The workflow only matches existing records.

### Files to modify
- n8n workflow `bt54zeRz9SIOmSqf` — update Code node + add Search SOV node + fuzzy match logic
- `knowledge-base/clients/fantastic-floors/systemlink-check-distribution/airtable-schema-design.md` — update workflow spec section + add SOV parsing docs

---

## Workstream 4: Dashboard Enhancement

**Goal:** Add SOV drill-down to existing Airtable Interface pages.

### Changes
- **Page 2 (Project Budget Health):** When viewing a project, show linked Schedule of Values records with their individual budget bars and status
- **SOV grouped view:** Filter/sort by project, see all SOV sections with budget tracking per section
- Consider a new Interface page: "Schedule of Values" showing all SOV records grouped by project

---

## Workstream 5: Historical Data Migration

**Goal:** Migrate existing data from Google Sheets + seed projects/SOV from Jesus's completed sheet.

### Migration sources
1. **Project list** (from Jesus's sheet) → Projects table (with budgets)
2. **SOV data** (from Jesus's sheet) → Schedule of Values table
3. **Historical check data** (from Google Sheets tabs) → Check Line Items table
4. **Vendor list** (from 1099 data) → Vendors table (~30+ vendors)

### Approach
- Python script for each migration source
- Match format to existing n8n output (same Unique ID format, field mapping)
- Validate: row counts match, dollar totals match source
- Dedup check against Processed IDs table

### Blocked by
- Jesus completing the Google Sheet (Workstream 1)
- Confirming which historical data tabs to include

---

## Workstream 6: SOW for Check Distribution

**Goal:** Create project-specific SOW using the existing template.

### Key details
- **Template:** `knowledge-base/sops/sow-template-slw.md`
- **No existing SOW** for Check Distribution (confirmed)
- **Payment terms:** Full setup fee ($4,875) due at go-live/completion. NO 50% upfront. Monthly $350 starts 1st of month following go-live.
- **Scope includes:** Everything in proposal PLUS SOV automation (goodwill) — description parsing, auto-linking, SOV budget tracking dashboard
- **Scope excludes:** Deposit/expense/unit/investment tracking, changes to QBO check-printing process

### SOW template adaptations needed
The template is designed for Platform 1 → Platform 2 syncs (Monday → QBO style). Check Distribution is QBO → Airtable, so several sections need rewriting:
- Section 2 (System of Record): QBO is source, Airtable is destination/dashboard
- Section 3.1 (Discovery): The Google Sheet data collection IS the discovery
- Section 3.2 (Core Build): Rewrite for check distribution + SOV scope
- Section 6 (Payment): **Full at completion, not 50/50**
- Section 3.4 (Exclusions): Deposit tracking, expense tracking, changes to QBO workflow

### Output
- DOCX via `tools/sop_docx_builder.py` (pandoc pipeline)
- Store in `knowledge-base/clients/fantastic-floors/systemlink-check-distribution/deliverables/`

---

## Workstream 7: SOP Document

**Goal:** Client-facing operations manual.

### Sections
1. **System Overview** — What the platform does, tables, data flow
2. **Weekly Workflow** — What's automatic vs. what the team does
3. **QBO Description Standardization (CRITICAL)**
   - Format: `SOV Name - Additional Description`
   - Examples in English and Spanish
   - What happens if format isn't followed (lands in Unassigned, must be manually assigned)
   - List of valid SOV Names for each project (from the seeded Schedule of Values records)
4. **Check Status Management** — Pending → Picked Up → Cashed
5. **Unassigned Check Review** — How to assign checks to projects + SOV sections
6. **Schedule of Values Management** — How to create/view/track SOV records, understanding budget status colors
7. **Dashboard Guide** — Each page explained, traffic light meanings
8. **Budget Alerts** — Threshold triggers, what to do when notified
9. **Troubleshooting** — Common issues

### Output
- DOCX via pandoc pipeline
- Store in `knowledge-base/clients/fantastic-floors/systemlink-check-distribution/deliverables/`

---

## Execution Sequence

### Phase A: Immediate (can start now, no blockers)
1. **Build/enhance Google Sheet** with SOV collection tabs (Workstream 1) — send to Jesus ASAP
2. **Rename + simplify Airtable table** (Workstream 2) — rename Project Breakdown → Schedule of Values, drop unused fields
3. **Start SOW** from template (Workstream 6) — adapt for Check Distribution, update payment terms

### Phase B: While waiting for Jesus's responses
4. **Update n8n Code node** with description parsing logic (Workstream 3)
5. **Write SOP document** (Workstream 7)
6. **Build SOV dashboard views** (Workstream 4)

### Phase C: After Jesus completes the sheet
7. **Seed Projects** with budgets from completed sheet (Workstream 5)
8. **Seed Schedule of Values** with SOV records (Workstream 5)
9. **Run historical data migration** (Workstream 5)
10. **Final SOW review** and send for signature
11. **Training session** + SOP delivery

---

## Verification

- [ ] Google Sheet enhanced with SOV tabs, pre-populated with known project/SOV data
- [ ] Google Sheet sent to Jesus with clear instructions
- [ ] Airtable table renamed to "Schedule of Values"; Building, Floor, Trade fields removed
- [ ] SOW filled from template with updated payment terms (full at completion)
- [ ] Budget Mismatch guardrail works on Projects table (SOV totals vs project budget)
- [ ] n8n Code node parses SOV Name from descriptions (before ` - `)
- [ ] CLI records auto-link to correct SOV when description matches
- [ ] Dashboard shows SOV budget tracking within project view
- [ ] Historical data migrated with matching row counts and totals
- [ ] SOP document covers QBO description standardization prominently
- [ ] All deliverables in `knowledge-base/clients/fantastic-floors/systemlink-check-distribution/deliverables/`

---

## Critical Files

| File | Purpose |
|------|---------|
| `knowledge-base/clients/fantastic-floors/systemlink-check-distribution/airtable-schema-design.md` | Schema spec — update Table 2 |
| `knowledge-base/clients/fantastic-floors/systemlink-check-distribution/proposal-paylink.md` | Proposal v3.0 (reference for SOW) |
| `knowledge-base/clients/fantastic-floors/systemlink-check-distribution/plan.md` | Project plan — update with SOV scope |
| `knowledge-base/sops/sow-template-slw.md` | SOW template to fill |
| `knowledge-base/sops/discovery-signoff-template-slw.md` | Discovery template (reference) |
| `tools/sop_docx_builder.py` | DOCX generation pipeline |
| n8n workflow `bt54zeRz9SIOmSqf` | Live workflow — update Code node |
| Airtable base `appIZnZqi8HWa6MTF`, table `tblKCwcferE8wHrjn` | Schedule of Values table |
| Google Sheet `1zp-cVodkjRXWan7y97hy7kZCL1cZr0wDjL78B7rp4OQ` | FF Construction data (SOV source) |
