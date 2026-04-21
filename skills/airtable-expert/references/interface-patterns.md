# Airtable Interface Patterns

Choosing the right interface layout for the job. The wrong layout buries the information the user actually needs.

## Load when

- Designing or modifying any Airtable interface page
- Choosing between Dashboard / Record Review / Grid / List / Form / Timeline / Calendar / Gallery
- Building a client-facing view
- Laying out a print-ready / PDF-export page
- Adding button actions or record-linked navigation

## The Layout Decision

Answer these in order. First yes wins.

```
1. Does the user need to act on ONE record at a time
   (review, approve, enter data, add notes)?
     YES --> RECORD REVIEW

2. Is the primary job to scan MANY records with filters/sort?
     YES --> GRID (if editing inline) or LIST (if read-only + click-through)

3. Is the primary job to summarize? KPIs, totals, charts?
     YES --> DASHBOARD

4. Is the primary job to SCHEDULE or SEE across time?
     YES --> TIMELINE (Gantt-style ranges) or CALENDAR (date points)

5. Is the data visual by nature (photos, products, portfolios)?
     YES --> GALLERY

6. Is this data ENTRY from an external user (not a collaborator)?
     YES --> FORM
```

Do not default to Grid because it feels "safest." Grid is a spreadsheet; if you already wanted a spreadsheet, you would not be building an interface.

## Layout Reference

### Record Review

**Best for:** one-at-a-time review, approval workflows, data entry with many fields

**Structure:** top-right record picker, center body shows ONE record's fields in a form-like layout, optional side panel for related records

**Configure:**
- Source: a single table
- Field layout: drag fields into groups; use "Section" blocks for visual grouping
- Navigation: set a sort/filter so the left sidebar shows the expected record order

**When it fails:** user has 50+ records and needs to compare across them — Record Review hides everything except the current record. Switch to Grid for comparison, keep Record Review for the act-on-one-record flow.

**Client-facing use:** great for approval loops ("here's a proposal, approve or request changes"). Keep the field layout tight — 5-10 fields maximum visible; hide the rest in collapsible sections.

### Grid

**Best for:** power users scanning and editing many records, filtered exploration

**Structure:** spreadsheet-style rows and columns, inline editing, column show/hide, filter and sort at the top

**Configure:**
- Source: a single table
- Columns: pick only what the user needs — Grid bloat is a usability killer
- Row actions: configure buttons in the toolbar for common actions (Create, Link, Archive)

**When it fails:** client-facing use — Grid exposes too much structure. Clients see "this is a database" rather than "this is my workspace." Swap for Record Review + linked Grid for the "list" tab.

### Dashboard

**Best for:** KPI summaries, charts, metrics that answer "how are we doing?"

**Structure:** tile-based grid with number boxes, charts (bar, line, pie), and linked Grid/List elements

**Configure:**
- Source: multiple tables via separate elements
- Elements:
  - **Number** element for single KPIs (e.g., "Revenue This Month")
  - **Chart** element for trends (date on X, value on Y, grouped by category)
  - **Grid** element for drill-down (filtered list of records the KPI references)
  - **Filter** element at the top for cross-element filtering (e.g., date range)
- Global filters: propagate to all linked elements — decide what filters to pin globally vs per-element

**When it fails:** user wants to EDIT data — Dashboard is read-only. Put the edit flow on a sibling Record Review page and link to it from a button on the Number element.

**Print-ready variant:** set page width fixed, remove interactive filters (hard-code them), ensure all charts have enough contrast for black-and-white printing. Export via browser print-to-PDF (no native Airtable print export in 2026).

### List

**Best for:** mobile-friendly record browsing, simple read-heavy use cases

**Structure:** vertical list with card-style rows, click a row to open record detail

**Configure:**
- Source: a single table
- Display fields: primary field + 2-3 secondary fields per row
- Sort/filter: at the top, minimal

**When it fails:** desktop power users want density. Use Grid. List is for mobile consumers / read-only browsing.

### Timeline

**Best for:** projects, campaigns, schedules with a START and END date

**Structure:** Gantt-style horizontal bars across a time axis

**Configure:**
- Source: a single table with two date fields (start, end)
- Group by: project / owner / category
- Color by: status or priority

**When it fails:** single-date events (deadlines, birthdays). Use Calendar instead.

### Calendar

**Best for:** scheduling, event visibility, date-point-based records

**Structure:** month/week/day calendar grid, records appear on their date

**Configure:**
- Source: a single table with a date field
- Color by: category
- Click record: opens detail drawer

**When it fails:** data is range-based (start-to-end projects). Use Timeline.

### Gallery

**Best for:** visually-rich records — products, case studies, designs, people directories

**Structure:** card grid with image/cover field prominent

**Configure:**
- Source: table with an attachment field
- Card: cover attachment + title + 2-3 secondary fields
- Size: small / medium / large cards — match to density needs

### Form

**Best for:** data collection from external users (non-collaborators), structured intake

**Structure:** vertical form, one field per row, submit button at bottom

**Configure:**
- Source: a single table
- Public form: shareable URL, no login required
- Fields: mark required/optional, add help text
- After submit: customize thank-you message, optional redirect URL

**When it fails:** complex multi-step intake with branching logic. Use a dedicated form tool (Tally, Typeform) and webhook results into Airtable. Forms is purpose-built for simple intake.

## Button Actions (the power-user feature)

Any interface element can have a button-to-action. Actions available:

| Action | What It Does |
|--------|--------------|
| Open record | Navigate to a Record Review detail of the linked record |
| Update record | Set one or more fields to pre-defined values (e.g., Status = "Approved") |
| Create record | Pre-fill and open a new record form |
| Open URL | Jump to external URL (with field interpolation in the URL) |
| Trigger automation | Send webhook to Airtable Automation (which can cascade to any action) |

**Pattern:** Grid rows often need 3 buttons: [Edit] (Update record or navigate to Record Review), [Archive] (Update record → set status), [Copy] (Create record → duplicate fields). Add them as toolbar actions, not per-row — per-row buttons bloat the Grid visually.

## Print / PDF Export

No native Airtable PDF export in 2026. The workflows that work:

| Need | Approach |
|------|----------|
| Print current interface page | Browser print-to-PDF (Ctrl+P). Set page width fixed first. |
| Scheduled PDF report | Airtable Automation → send HTTP request to a PDF service (Make / n8n / DocGen) |
| Record-level printable invoice | Button action → Open URL to a DocGen template (Plumsail, Docmosis, or custom Cloudflare Worker that renders HTML) |

Design for print up-front when needed — retrofitting a Dashboard for print requires significant rework.

## Client-Facing Interface Checklist

Before sharing with a client:

- [ ] Base role for the collaborator is "none" (not "read only" or "editor") — prevents them seeing the base tables
- [ ] Interface shared explicitly via Share button, permission = "Can edit" or "Can comment" per need
- [ ] Grid elements hide internal-only fields
- [ ] No internal URLs / staff names in visible fields (sanitize)
- [ ] Dashboard filters default to current user's data if multi-tenant (use `CURRENT_USER()` in filter formulas)
- [ ] Test login: open the interface in an incognito window with the client's account — confirm they see what they should, nothing more

See `references/permission-patterns.md` for the permission-scoping details.

## Layout Anti-Patterns

| Pattern | Why It Fails | Fix |
|---------|--------------|-----|
| **Grid everywhere** | Clients see a database, not a product | Record Review for single-record work, Dashboard for metrics, Grid only for power-user "find a specific record" tabs |
| **Dashboard with 20 Number tiles** | Cognitive overload, no hierarchy | Max 6 headline numbers. Everything else goes in drill-down Grids below the fold |
| **Forms with 30 fields** | Abandonment | Split into multi-step flow (create record with minimal fields, then prompt user to complete on Record Review) |
| **Timeline with no color grouping** | Can't distinguish projects | Color by owner, category, or status — the visual signal is the point of Timeline |
| **Calendar as data entry** | Calendar click-to-create is clunky | Use Form or Record Review for entry, Calendar for viewing |
