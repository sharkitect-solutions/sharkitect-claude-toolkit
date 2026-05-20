# SystemLink: Check Distribution Sync — Proposal Finalization

## Context

Proposal for Fantastic Floors' 2nd project (SystemLink: Check Distribution Sync). Steps 0-3 DONE in prior sessions (document processing, placeholder population except pricing, branded DOCX generated, workforce review PASS).

**Workflow change (Chris-directed):** Build a working MVP proof-of-concept BEFORE finalizing proposal pricing. The MVP validates actual build complexity and enables accurate pricing — current numbers are estimates. Pricing is TENTATIVE until MVP validates. The working MVP is also presented alongside the proposal to demonstrate the solution in action ("show, don't tell" — higher conversion for trades SMB clients).

This changes the plan from single-step proposal finalization to: **MVP Build → Complexity Validation → Pricing Finalization → Proposal Finalization → Deliver Both.**

---

## Completed Steps (Prior Sessions)

- [x] **Step 0** — Chris's modified documents processed, incoming files deleted
- [x] **Step 1** — Proposal populated (all placeholders except `[MONTHLY_RATE]` and dependents)
- [x] **Step 2** — Branded DOCX generated (`SystemLink-Check-Distribution-Sync-Proposal.docx`)
- [x] **Step 3** — Workforce review (Vera brand PASS, Sterling margin PASS)
- [x] **Naming convention** — "PayLink" retired, all docs updated to "SystemLink: Check Distribution Sync"

---

## Team Analysis Summary (Already Complete)

**Orion (CTO) — Build Assessment:**
- Build effort: 35-40 hours over 3-4 weeks
- Complexity: 5/10 (SLW-Standard)
- Reuses QBO + Monday.com integrations from Project 1
- Weekly batch processing = simpler than Project 1's on-demand triggers

**Atlas (COO) — Operational Cost:**
- Monthly maintenance: 1.5-2 hours labor (~$75-100) + ~$10-15 platform costs
- Total operational cost: ~$135-165/month
- LOWER than Project 1 (batch vs on-demand, read-only from QBO)

**Felix (Revenue) — Client Sensitivity:**
- FF currently pays $750/mo (pre-standard, above Core tier rate)
- Small increment ($150-250/mo) is easy to justify and unlikely to cause friction
- Large increment ($500+/mo) risks stalling the deal
- Felix recommends: $150-250/mo increment → $900-1,000/mo total

**Sterling (CFO) — Margin Analysis:**
- Operational cost floor: ~$135-165/mo
- Any increment above that is margin-positive
- Setup fee ($3,375) already validated against margin guardrails

---

## Decisions Locked (Regardless of MVP Outcome)

These decisions are FINAL and apply regardless of what the MVP reveals about complexity:

| Decision | Value | Status |
|---|---|---|
| Setup discount | 25% Partnership Progression (from pricing-structure.md) | LOCKED |
| Monthly deduction | **$125 flat** per additional project | LOCKED (Chris-directed) |
| Deduction type | Flat dollar amount, NOT percentage | LOCKED (Chris-directed) |
| Rate framing | No universal "standard" rate — each project priced on scope/complexity. Display as project-specific base rate. | LOCKED (Chris-corrected) |
| Forward-looking compounding | Include in proposal (team unanimous, Chris asked for team input) | LOCKED |
| Compounding display | Each project adds $125 savings (2 projects = $125/mo, 3 = $250/mo, 4 = $375/mo...) | LOCKED |
| Floor | **$250/mo minimum** for any project addition | LOCKED (Chris-directed) |
| Scope | FF-only monthly deduction for now. Standard-client monthly deductions get separate round table when next client enters pipeline. | LOCKED |
| FF exception | Exception to Pricing Rule #3. FF is pre-standard pricing. Does NOT modify locked pricing structure. | LOCKED |

---

## Phase 1 — MVP Build

**Purpose:** Build a working proof-of-concept of SystemLink: Check Distribution Sync to (a) validate complexity assessment, (b) discover actual build effort for accurate pricing, (c) demonstrate the solution to FF in action before they sign.

**Assigned to:** Orion (CTO) / Node (builder)

**Blueprint:** `knowledge-base/projects/fantastic-floors-paylink/blueprint-qbo-check-distribution.md` (v2.1)

**Scope — Option A only (per Chris's direction):**
- QBO check query → line item extraction
- Project identification via Customer field
- Google Sheets distribution (project tabs + Dashboard + Unassigned queue)
- Monday.com board updates
- Duplicate prevention
- Unassigned item routing

**Requirements:**
- Access to FF's QuickBooks Online (read access for check data)
- Google Sheets workspace (test or production)
- Monday.com workspace (test or production)
- Sample/test check data mimicking FF's actual structure
- n8n as automation platform (standard for Sharkitect builds)

**Deliverable:** Working POC processing test check data through the full pipeline. Demonstrable to FF.

**Estimated build effort:** 8-15 hours (per Orion's initial assessment — to be validated by actual build)

**Complexity tracking:** Document actual build hours, unexpected complexity, integration challenges. This data feeds Phase 2 pricing validation.

### Phase 1 Status Update (2026-03-22)

**STATUS: BLOCKED** — Two external dependencies must be resolved before Phase 1 testing can complete.

**Blocking items (Chris action required):**
1. **QBO Admin Access to FF Construction account** — Chris needs FF Construction to grant admin privileges for QBO connection. Production credential cannot be created until this is resolved.
2. **Monday.com board access** — Chris needs access to FF's Monday.com boards to determine exact column mapping. Data schema (which fields to capture in Sheets/Airtable) cannot be finalized until Monday.com columns are known.

**Completed during testing (2026-03-22):**
- [x] QBO Sandbox connection working — 403 fix: production URL (`quickbooks.api.intuit.com`) changed to sandbox URL (`sandbox-quickbooks.api.intuit.com`). **Lesson: credential AND API URL must match the environment (sandbox vs production).**
- [x] Separate QBO Dev App created — Chris created a new QBO Developer app specifically for this project to prevent interference with Project 1's app. Sandbox realm: `9341456660342857` (Sandbox Company US c287).
- [x] Google Sheets workbook created — "FF Construction - Check Distribution" (ID: `1Jh6Y7MzB05szEUQfnftLwQyhhjN3Fk9T1iHPE4dPCko`). Tabs: Dashboard, Unassigned, Processed. Google Sheets credential: "Admin Google Sheets."
- [x] First test run executed — QBO check data pulled and parsed successfully.
- [ ] Dynamic project tab creation — "Append to Project Tab" node fails when tab doesn't exist. Blueprint promises auto-creation. **PAUSED** — Chris stopped fixing this to wait for Monday.com column mapping before finalizing data schema.

**Chris feedback — Google Sheets limitations:**
- Dashboard tab too simple — needs auto-populating/auto-updating (not just static headers)
- Need Monday.com column mapping to ensure Sheets match Monday columns
- Overall Google Sheets may not be professional enough for client presentation

### Phase 1.6 — Real Check Data Analysis (Chris screenshots 2026-03-22)

**Chris provided screenshots of 3 actual QBO checks from FF Construction's account.** This reveals the real data structure our workflow must handle.

**Check #7413** (1 line item):
- Category: Cost of goods sold:Subcontractor expenses:Labor
- Description: "Architect Services Ther Meadow Deck 7 Unit"
- Amount: $5,250.00 | Customer: Ther Meadows Deck | Class: **FF Costruccion and Rem...**

**Check #7405** (3 line items — Payee: Orellana Flooring LLC, Date: 03/19/2026, Tag: "Comercial"):
- Line 1: "Arrive Kc" — $2,442.00 — Customer: Arrive Kc Apt — Class: **Fantastic Floors**
- Line 2: "5%" — **-$122.00** (negative = retainer deduction) — Customer: **Reten** — Class: (empty)
- Line 3: "Akrofire Apt" — $3,598.30 — Customer: Akrofire — Class: **Fantastic Floors**

**Check #7325** (2 line items — Payee: Lusvin Chinchilla, Date: 03/05/2026, Tag: "Comercial"):
- Line 1: "Apt varios" — $1,658.04 — Customer: Country Meadows — Class: **Fantastic Floors**
- Line 2: "Pendiente Material por pagar" — $342.00 — Customer: Bicentennial Manor — Class: **Fantastic Floors**

#### Key Data Schema Discoveries

| Discovery | Impact | Action Required |
|---|---|---|
| **CLASS field distinguishes divisions** | "FF Costruccion and Rem..." = FF Construction division. "Fantastic Floors" = FF division. Both in SAME QBO account. | Add `class` column to ALL output tables. May need class-based filtering if only one division in scope. |
| **Negative amounts (retainers)** | Line 2 on #7405: "Reteiners 5%" = -$122.00. Customer = "Reten" (not a real project). | Define routing rule: exclude retainer lines from project routing? Or route to special "Retainers" category? Chris to confirm. |
| **Bilingual descriptions** | Spanish: "Apt varios" (various apartments), "Pendiente Material por pagar" (pending material to pay). English: "Architect Services Ther Meadow Deck 7 Unit". | AI agent node MUST handle English + Spanish parsing. |
| **Tags exist** | "Comercial" tag on checks #7405 and #7325. | Potential additional metadata column. TBD if useful for filtering/categorization. |
| **Permit no field** | Exists in QBO UI, appears empty on these examples. | Add column if some checks use it. Low priority. |
| **Customer = Project** | Confirmed: CustomerRef maps to project names (Ther Meadows Deck, Arrive Kc Apt, Country Meadows, etc.) | Current project routing logic is CORRECT. |
| **Multi-line checks confirmed** | Up to 3+ lines per check, each potentially different project AND different class. | Already handled by Parse & Flatten. |

#### MVP Code Gap: ClassRef NOT Captured

**Current Parse & Flatten code does NOT extract `ClassRef`.** QBO API returns ClassRef at the line detail level:
- `AccountBasedExpenseLineDetail.ClassRef.name` / `.value`
- `ItemBasedExpenseLineDetail.ClassRef.name` / `.value`

**Required code change** (when build resumes):
```javascript
// Add to both AccountBased and ItemBased extraction blocks:
className: detail.ClassRef?.name || '',
classId: detail.ClassRef?.value || '',
```

**Additional fields to consider adding:**
- `tags` — if available via QBO API (check Purchase object schema)
- `permitNo` — if available at check level
- `payeeAddress` — for reference (visible in screenshots)

#### Schema Decisions (Chris — 2026-03-22)

| Question | Decision | Notes |
|---|---|---|
| Class filtering | **Capture ALL classes** | Show both FF Construction and Fantastic Floors divisions. Add Class column. Client can filter/sort. |
| Retainer lines | **Separate Retainers category** (tentative) | Chris needs to check with client if they need to track retainers and how. For now: create dedicated Retainers tab/table with check # link + QBO deep link. Final routing TBD after client input. |
| Tags | **Capture** | Add Tags column to output. "Comercial" and other tags may be useful for categorization. |
| Permit no | **Skip for now** | Client doesn't appear to use it. Can add later if needed. |

#### Updated Output Schema (All Platforms)

Based on real check data + Chris's decisions, the complete column set:

| Column | Source | Notes |
|---|---|---|
| Date | `check.TxnDate` | Payment date |
| Check # | `check.DocNumber` | Check number |
| Vendor | `check.EntityRef.name` | Payee name |
| Description | `line.Description` | Line item description (bilingual EN/ES) |
| Amount | `line.Amount` | Can be negative (retainers) |
| Customer/Project | `detail.CustomerRef.name` | Project routing field |
| Category | `detail.AccountRef.name` | Account category |
| Class | `detail.ClassRef.name` | **NEW** — Division (FF Construction vs Fantastic Floors) |
| Tags | `check.Tag` (TBD) | **NEW** — Check-level tags (e.g., "Comercial") |
| Check URL | Constructed | **NEW** — `https://app.qbo.intuit.com/app/check?txnId=[checkId]` |
| Check ID | `check.Id` | Internal reference |
| Line # | Loop index | For dedup |
| Unique ID | `checkId-lineNumber` | Dedup key |
| Processed At | `$now.toISO()` | Timestamp (Processed table only) |

**AI Agent Parsed Fields** (added by AI node, TBD after Monday.com access):
- Apartment/Unit Number (extracted from description)
- Invoice Number (extracted from description)
- Additional fields TBD based on Monday.com column mapping

**Routing Rules:**
- `isAssigned && CustomerRef != "Reten"` → Project tab/table (grouped by Customer)
- `!isAssigned` → Unassigned queue
- `CustomerRef == "Reten" || isRetainer` → Retainers category (separate tab/table)
- Retainer detection: Customer = "Reten" OR negative amount with retention-related category

---

### Phase 1.5 — Data Layer Decision: Airtable vs Google Sheets (RT#12)

**Chris's proposal (2026-03-22):** Replace Google Sheets with Airtable as the data layer for Check Distribution Sync. Key arguments:
- More professional, cleaner, better UI/UX
- Airtable Interfaces can serve as a native dashboard (better than Sheets formulas)
- CEO said he's open to new tools/platforms
- Present BOTH options (Sheets + Airtable) to FF and let them choose
- If FF picks Airtable, Monday.com push could be bypassed (Airtable potentially replaces BOTH Sheets and Monday.com for this workflow)

**Chris's additional feature requests (2026-03-22):**
1. **QBO check deep links** — Add a link column so client can click directly to the check in QBO for easy review, especially for unassigned items
2. **AI agent node for description parsing** — Extract key information from check line descriptions (apartment numbers, invoice numbers, etc.) and populate corresponding columns. Schema TBD after Monday.com board reveals required fields.
3. **Airtable built-in automations** — Unassigned records sit in an Unassigned table. Employee assigns a project → Airtable automation auto-moves/links the record to the correct project. Much cleaner than copy-paste in Google Sheets.
4. **Dual workflow approach** — Build separate Airtable version alongside existing Google Sheets workflow. Present both to FF. Leave Google Sheets version untouched as fallback.

---

### RT#12 — Round Table: Airtable vs Google Sheets as Data Layer

**Convened by:** Marcus (Chief of Staff)
**Participants:** Orion (CTO), Atlas (COO), Sterling (CFO), Felix (Revenue), Vera (Brand)
**Date:** 2026-03-22

#### Orion (CTO) — Technical Assessment

**FOR Airtable:**
- n8n has native Airtable nodes — integration complexity is equivalent to Google Sheets
- Airtable's relational data model is inherently better than flat spreadsheet tabs for project-organized data
- Airtable Interfaces → native, auto-updating dashboard without maintaining spreadsheet formulas
- Airtable automations → unassigned record re-routing handled IN Airtable natively — no additional n8n nodes needed
- Linked records between projects and line items = structurally cleaner data model
- Sharkitect already uses Airtable (ERA state tracker, credential `4nvWheAnDcTUBg9Y`) — team has Airtable experience
- Airtable MCP server already configured in our environment
- QBO deep links: feasible with both platforms — QBO deep link format: `https://app.qbo.intuit.com/app/check?txnId=[checkId]`
- AI agent node for description parsing: platform-agnostic — works identically whether output goes to Sheets or Airtable

**NEUTRAL:**
- Build effort for Airtable version: ~3-5 additional hours (separate workflow variant, not a swap)
- If Monday.com push is dropped with Airtable → actually REDUCES total complexity (fewer integration points)
- Both platforms have n8n native nodes

**BUILD EFFORT IMPACT ON COMPLEXITY ASSESSMENT:**
- Adding Airtable version: small scope increase, still within SLW-Standard envelope
- Dual workflow (Sheets + Airtable): two variants of the same core logic — not double the work
- If FF chooses Airtable and drops Monday.com push: net complexity DECREASES

**Orion's position:** Airtable is technically superior for this use case. Relational data model + Interfaces + native automations = less n8n complexity, not more. **SUPPORT.**

#### Atlas (COO) — Operational Assessment

**FOR Airtable:**
- Lower maintenance overhead — Airtable automations handle in-app routing (unassigned → project assignment), reducing n8n workflow complexity
- Cleaner data model = fewer client support issues ("where is my data?" resolved by Interface dashboard)
- Airtable Interfaces = better CEO experience = fewer "how do I find X" support requests
- If Airtable replaces Monday.com for this workflow → one fewer integration to maintain monthly

**CONSIDERATIONS:**
- New platform for the client to learn (mitigated: CEO said he's open to it)
- Platform cost: $20-40/mo (1-2 editor seats at Team plan) — absorbed per PLATFORM COST ABSORPTION rule

**Operational cost impact:**
- Current estimate: $135-165/mo maintenance
- Adding Airtable: +$20-40/mo platform cost
- If Monday.com push removed: reduced maintenance time (~30 min/mo less)
- Net: roughly neutral operational overhead

**Atlas's position:** Operationally cleaner. Fewer support touchpoints, cleaner data model, native automations reduce n8n maintenance. **SUPPORT.**

#### Sterling (CFO) — Financial Assessment

**Airtable pricing (2026):**
| Plan | Annual Billing | Monthly Billing | Records/Base | Automations/Mo |
|------|---------------|----------------|-------------|----------------|
| Free | $0 | $0 | 1,000 | 100 |
| Team | $20/user/mo | $24/user/mo | 50,000 | 25,000 |
| Business | $45/user/mo | $54/user/mo | 125,000 | 100,000 |

**For FF Construction:**
- Need: Team plan, 1-2 editor seats = **$20-40/month**
- Falls well under PLATFORM COST ABSORPTION rule (<$100/mo per client)
- Sharkitect absorbs — FF never sees this line item

**Margin analysis with Airtable:**
- Monthly increment: $250/mo (LOCKED)
- Operational floor with Airtable: ~$155-205/mo (current $135-165 + $20-40 Airtable)
- Margin: $45-95/mo — still margin-positive
- No pricing change required regardless of platform choice

**Sterling's position:** Financially neutral to slightly positive (if Monday.com maintenance drops). Airtable cost absorbed within existing policy. No impact on locked pricing. **SUPPORT.**

#### Felix (Revenue) — Client Positioning

**FOR Airtable:**
- Chris's instinct is correct — a construction CEO responds better to a clean, modern interface than a spreadsheet with tabs
- Airtable Interfaces = "dashboard built for your business" vs "a spreadsheet you have to navigate"
- Trades SMBs are visual operators — they want to SEE the data at a glance, not hunt through tabs
- Presenting BOTH options = confidence signal: "We built it two ways — pick the one that works for you"
- CEO already said he's open to new tools → low adoption friction
- PERCEIVED value increases with Airtable — same $250/mo feels like a bigger win
- Strengthens the "AI Transformation Partner" positioning — this isn't just automation, it's a better way to see your business

**CLIENT SENSITIVITY:**
- Whether data lives in Sheets or Airtable doesn't change the pricing ($250/mo either way)
- But Airtable increases perceived value → supports Felix's strategy of making the increment feel like a bargain
- Dual presentation approach aligns with ASSUMPTIVE CLOSE TECHNIQUE: "Of these two options, which one would work better for your team?"

**Felix's position:** Stronger client positioning. Higher perceived value at the same price point. Dual presentation is smart sales strategy. **STRONG SUPPORT.**

#### Vera (Brand) — Presentation Quality

**FOR Airtable:**
- Significantly more professional than Google Sheets for client-facing data
- Airtable Interfaces: branded, clean, interactive — matches Sharkitect's "AI Transformation Partner" identity
- When FF CEO shows this to his team or peers → better impression → word-of-mouth potential
- Case study screenshots: Airtable Interface screenshots > spreadsheet screenshots in every context
- Demonstrates that Sharkitect builds polished solutions, not "just spreadsheets"

**Vera's position:** Objectively better brand representation. No downsides from a brand/presentation perspective. **STRONG SUPPORT.**

---

#### RT#12 — Team Recommendation: UNANIMOUS SUPPORT FOR AIRTABLE

**Decision:** Build an Airtable version alongside the existing Google Sheets workflow. Present both to FF. Let them choose.

**Execution plan:**
1. **Keep Google Sheets workflow** (`Q3dABipnUekcFlpO`) as-is — functional fallback
2. **Build Airtable variant** — separate workflow, same core logic (QBO query + parse), output to Airtable instead of Sheets
3. **Airtable structure:**
   - Base: "FF Construction - Check Distribution"
   - Table: "Check Line Items" (all line items — columns: Date, Check #, Vendor, Description, Amount, Customer/Project, Category, Class, Tags, Check URL, Check ID, Line #, Unique ID, + AI-parsed fields TBD)
   - Table: "Unassigned" (or filtered view of main table where Customer/Project = empty)
   - Table: "Retainers" (separate table for retention/retainer lines — linked to check via Check # + Check URL for easy review. Final routing TBD after client input.)
   - Table: "Processed IDs" (dedup tracking)
   - Interface: Dashboard view with project summaries, running totals, monthly breakdowns, filterable by Class (FF Construction vs Fantastic Floors)
   - Automation: When Unassigned record gets Project assigned → auto-move/link to project view
4. **QBO check deep links** — add `checkUrl` column: `https://app.qbo.intuit.com/app/check?txnId=[checkId]`
5. **AI agent node** — scope TBD after Monday.com board access reveals required extraction fields
6. **Monday.com push** — keep as optional in Airtable version; if FF finds Airtable sufficient, Monday.com push can be disabled
7. **Present both to FF** using assumptive close: "We built two versions — which one fits better for your team?"

**Pricing impact:** NONE. Same $250/mo increment. Airtable cost ($20-40/mo) absorbed. SLW-Standard complexity confirmed.

**APPROVED by Chris (2026-03-22)** — Plan approved with RT#12 included. Airtable variant will be built alongside Google Sheets when Phase 1 blockers clear.

---

### Phase 1.7 — Airtable Workflow Build (Chris-directed 2026-03-22)

**Context:** Chris directed: build the Airtable workflow now with all known columns. Monday.com-dependent columns (AI-parsed fields) are added later when board access is obtained. Adding columns to Airtable later is trivial — no reason to wait.

**Assigned to:** Orion (CTO) / Node (builder)

**Prerequisites (all available):**
- Airtable credential in n8n: "SHARKITECT - AIOS" (ID: `4nvWheAnDcTUBg9Y`)
- QBO Sandbox credential: working (realm `9341456660342857`)
- Existing MVP workflow: `Q3dABipnUekcFlpO` (core logic to replicate)
- Blueprint: `knowledge-base/projects/fantastic-floors-paylink/blueprint-qbo-check-distribution.md` v2.1

#### Build Now vs Add Later

| Build NOW (14 core columns) | Add LATER (after Monday.com access) |
|---|---|
| All known columns from real check data analysis | AI-parsed columns (apartment/unit #, invoice #) |
| 4 Airtable tables + Interface dashboard | AI agent node configuration |
| QBO query + parse + route logic | Monday.com push (if kept alongside Airtable) |
| ClassRef + Tags + Check URL extraction | Column name adjustments (if needed) |
| Dedup prevention via Processed IDs | |
| Assigned/Unassigned/Retainer routing | |
| Airtable automation (unassigned re-routing) | |

#### Step 1: Create Airtable Base Structure

Create base: **"FF Construction - Check Distribution"**

**Design principle:** Use Airtable's relational model — linked records, rollups, lookups — instead of flat text fields. This gives FF's team auto-updating project summaries, clickable cross-references, and grouped views equivalent to (but better than) per-project Sheets tabs.

**Table 1: Projects** (auto-populated — one record per unique project)

| Field | Type | Notes |
|---|---|---|
| Project Name | Single line text (Primary) | From `CustomerRef.name` — e.g., "Ther Meadows Deck", "Arrive Kc Apt" |
| Class / Division | Single Select | Options: "FF Construction", "Fantastic Floors" (from ClassRef) |
| Total Paid | **Rollup** | SUM of Amount from linked Check Line Items |
| Line Item Count | **Rollup** | COUNTA of linked Check Line Items |
| Last Payment Date | **Rollup** | MAX of Date from linked Check Line Items |
| Check Line Items | Linked Record → Check Line Items | Backlink (auto-created when Check Line Items links here) |

**How projects are created:** The n8n workflow searches the Projects table for each `CustomerRef.name`. If found → link. If not found → create new project record, then link. New projects appear automatically as checks reference them — no manual setup needed.

**Table 2: Check Line Items** (primary data — all assigned line items)

| Field | Type | Notes |
|---|---|---|
| Date | Date | `check.TxnDate` — Payment date |
| Check # | Single line text | `check.DocNumber` |
| Vendor | Single line text | `check.EntityRef.name` — Payee |
| Description | Long text | `line.Description` — bilingual EN/ES |
| Amount | Currency | `line.Amount` — can be negative (retainers) |
| Project | **Linked Record** → Projects | Replaces plain text — links to Projects table for rollups |
| Project Name | **Lookup** | Auto-pulls Project Name from linked Project record |
| Category | Single line text | `detail.AccountRef.name` |
| Class | Single line text | `detail.ClassRef.name` — Division (FF Construction vs Fantastic Floors) |
| Tags | Single line text | Check-level tags (e.g., "Comercial") |
| Check URL | URL | `https://app.qbo.intuit.com/app/check?txnId=[checkId]` |
| Check ID | Single line text | `check.Id` — internal QBO reference |
| Line # | Number (integer) | Loop index for dedup |
| Unique ID | Single line text | `checkId-lineNumber` — dedup key |

**Views on Check Line Items:**
- **All Items** — default view, all records
- **By Project** — grouped by Project field (equivalent to per-project Sheets tabs)
- **By Vendor** — grouped by Vendor
- **By Class** — grouped by Class (FF Construction vs Fantastic Floors)
- **By Month** — grouped by Date (month)
- **Recent** — filtered to last 30 days

**Table 3: Unassigned** (review queue)

Same columns as Check Line Items EXCEPT: Project field is empty (no linked record). When FF team assigns a project, Airtable automation moves the record to Check Line Items with the link.

| Field | Type | Notes |
|---|---|---|
| Date | Date | `check.TxnDate` |
| Check # | Single line text | `check.DocNumber` |
| Vendor | Single line text | `check.EntityRef.name` |
| Description | Long text | `line.Description` |
| Amount | Currency | `line.Amount` |
| Assign to Project | **Linked Record** → Projects | FF team selects project here → triggers automation |
| Category | Single line text | `detail.AccountRef.name` |
| Class | Single line text | `detail.ClassRef.name` |
| Tags | Single line text | Check-level tags |
| Check URL | URL | Deep link to QBO check — for easy review when assigning |
| Check ID | Single line text | `check.Id` |
| Line # | Number (integer) | Loop index |
| Unique ID | Single line text | `checkId-lineNumber` |

**Table 4: Retainers** — same core columns as Check Line Items. Items where Customer = "Reten" OR negative amount with retention-related category. Linked Record to Projects optional (retainers may reference the associated project if identifiable from the check).

| Field | Type | Notes |
|---|---|---|
| Date | Date | `check.TxnDate` |
| Check # | Single line text | `check.DocNumber` |
| Vendor | Single line text | `check.EntityRef.name` |
| Description | Long text | `line.Description` |
| Amount | Currency | Negative values (e.g., -$122.00) |
| Related Project | **Linked Record** → Projects | Optional — if retainer is identifiable to a project |
| Category | Single line text | `detail.AccountRef.name` |
| Class | Single line text | `detail.ClassRef.name` |
| Tags | Single line text | Check-level tags |
| Check URL | URL | Deep link to QBO — critical for retainer review |
| Check ID | Single line text | `check.Id` |
| Line # | Number (integer) | Loop index |
| Unique ID | Single line text | `checkId-lineNumber` |

**Table 5: Processed IDs** (dedup tracking)

| Field | Type | Notes |
|---|---|---|
| Unique ID | Single line text | `checkId-lineNumber` |
| Processed At | Date (include time) | `$now.toISO()` |

#### Step 2: Build n8n Workflow

Create new workflow: **"SystemLink: Check Distribution Sync — Airtable"**

Replicate core logic from MVP (`Q3dABipnUekcFlpO`), replace Google Sheets output with Airtable nodes.

**Node structure (~16 nodes):**

| # | Node | Type | Purpose |
|---|---|---|---|
| 1 | Manual Trigger | Trigger | Testing (swap to Schedule for production) |
| 2 | Set Configuration | Set | realmId, date range, Airtable base/table IDs |
| 3 | Query QBO Checks | HTTP Request | GET Purchase entity, PrintStatus='PrintComplete' filter |
| 4 | Parse & Flatten | Code | Extract line items — **UPDATED** with ClassRef + Tags + Check URL |
| 5 | Check Dedup | Airtable Search | Lookup Unique ID in Processed IDs table |
| 6 | Filter New | IF | Skip items already in Processed IDs |
| 7 | Route: Retainer | IF | Customer="Reten" OR (negative amount AND retention category) |
| 8 | Route: Assigned/Unassigned | IF | Customer/Project exists and non-empty |
| 9 | **Find Project** | Airtable Search | Search Projects table for CustomerRef name |
| 10 | **Project Exists?** | IF | Check if search returned a result |
| 11 | **Create Project** | Airtable Create | New project record (name + class) — only if not found |
| 12 | Insert Check Line Items | Airtable Create | Assigned items → Check Line Items table with **Linked Record** to Project |
| 13 | Insert Unassigned | Airtable Create | Unassigned items → Unassigned table (no project link) |
| 14 | Insert Retainers | Airtable Create | Retainer items → Retainers table (optional project link) |
| 15 | Log Processed IDs | Airtable Create | Record Unique ID + timestamp for dedup |
| 16 | Summary | Code | Count: inserted / skipped / retainers / unassigned / new projects created |

**Project find-or-create logic (nodes 9-11):**
- Node 9 searches Projects table: `filterByFormula = {Project Name} = "CustomerRef.name"`
- Node 10 checks if result exists (Airtable Search with `alwaysOutputData: true` returns empty array if not found)
- Node 11 creates new project record with: Project Name, Class/Division (from ClassRef)
- Node 12 uses the project record ID (from node 9 OR 11) as the Linked Record value when inserting the check line item
- Rollup fields (Total Paid, Line Item Count, Last Payment Date) auto-calculate in Airtable — no n8n logic needed

**Parse & Flatten code updates** (from Phase 1.6 gap analysis):
```javascript
// Add to both AccountBased and ItemBased extraction blocks:
className: detail.ClassRef?.name || '',
classId: detail.ClassRef?.value || '',
// Add check-level:
tags: check.Tag || check.MetaData?.Tag || '',
checkUrl: `https://app.qbo.intuit.com/app/check?txnId=${check.Id}`,
```

**n8n Airtable node rules** (from Node's pattern library):
- ALWAYS use native Airtable nodes (`n8n-nodes-base.airtable` v2.1) — never HTTP Request
- Resource locator: `{"__rl": true, "value": "tblXXX", "mode": "id"}`
- Output: fields at JSON root (`json.fieldName`), record ID at `json.id`
- Search nodes: `alwaysOutputData: true`
- Credential: "SHARKITECT - AIOS" (ID: `4nvWheAnDcTUBg9Y`)

#### Step 3: Create Airtable Interface (Dashboard)

Build after data flows into tables. The Interface leverages rollup fields from the Projects table — summaries are auto-calculated, not manually maintained.

**Interface pages:**
- **Project Dashboard** — Grid/Gallery of Projects table showing: Project Name, Class/Division, Total Paid (rollup), Line Item Count (rollup), Last Payment Date (rollup). Filterable by Class. Click any project → expands to show linked Check Line Items.
- **All Payments** — Full Check Line Items table with grouping options (by Project, by Vendor, by Month, by Class)
- **Unassigned Queue** — Unassigned table view. FF team assigns projects here → triggers automation.
- **Retainers** — Retainers table with Check URL links for easy QBO review
- **Monthly Summary** — Check Line Items grouped by month with summary bar (total amounts, item counts)

#### Step 4: Set Up Airtable Automation

**Automation 1: Unassigned → Assigned**
- **Trigger:** When "Assign to Project" field in Unassigned table is populated (linked record selected)
- **Action:** Create matching record in Check Line Items table with all fields copied + Project linked record set
- **Cleanup:** Optionally mark original Unassigned record as "Assigned" or delete it

This handles the workflow where FF team members review unassigned items and assign them to projects — natively in Airtable without additional n8n nodes. The assigned record automatically appears in the correct project's rollups.

#### Step 5: Test with QBO Sandbox

1. Run workflow against QBO Sandbox data
2. Verify Projects table auto-populated with unique project names from check data
3. Verify Check Line Items linked correctly to Projects via Linked Record
4. Verify rollups: Total Paid, Line Item Count, Last Payment Date calculate correctly on Projects
5. Verify Lookup: Project Name auto-displays on Check Line Items
6. Verify routing: assigned → Check Line Items (linked), unassigned → Unassigned, retainers → Retainers
7. Verify dedup: run workflow twice, confirm no duplicates on second run
8. Verify Check URL: clickable links opening correct check in QBO
9. Verify Class field: FF Construction vs Fantastic Floors correctly captured
10. Verify Views: By Project, By Vendor, By Month, By Class groupings work
11. Verify Interface dashboard: rollup summaries display, filters work, project drill-down works
12. Verify Automation: manually assign a project to an Unassigned record → confirm it moves to Check Line Items with correct link

#### Phase 1.7 Verification Checklist

- [ ] Airtable base created with **5 tables** (Projects, Check Line Items, Unassigned, Retainers, Processed IDs) and correct field types
- [ ] **Projects table**: rollup fields (Total Paid, Line Item Count, Last Payment Date) configured
- [ ] **Check Line Items table**: Linked Record → Projects configured, Lookup for Project Name working
- [ ] **Views created**: By Project, By Vendor, By Month, By Class on Check Line Items
- [ ] n8n workflow created (~16 nodes) and connected to Airtable credential
- [ ] Parse & Flatten updated: ClassRef extracted (`detail.ClassRef?.name`)
- [ ] Parse & Flatten updated: Tags extracted
- [ ] Parse & Flatten updated: Check URL constructed
- [ ] **Project find-or-create**: workflow searches Projects table, creates new project if not found, links record
- [ ] Routing: assigned items → Check Line Items table (with project link)
- [ ] Routing: unassigned items → Unassigned table (no project link)
- [ ] Routing: retainer items → Retainers table (optional project link)
- [ ] Dedup: Processed IDs table prevents reprocessing
- [ ] Test run: QBO Sandbox data flows correctly into all Airtable tables
- [ ] Rollups verified: project summaries auto-calculate correctly
- [ ] Interface: dashboard created with project summaries, drill-down, and filters
- [ ] Automation: unassigned re-routing configured and tested
- [ ] Memory files updated (Orion, Atlas, Node, project MEMORY)
- [ ] PENDING (add later): AI-parsed columns after Monday.com access
- [ ] PENDING (add later): AI agent node for description parsing
- [ ] PENDING (add later): Monday.com push integration (if kept)

---

## Phase 2 — Complexity Validation & Pricing Finalization

**Purpose:** Compare actual MVP build effort against estimated complexity. Resolve scope questions. Build enhanced ROI case. Confirm or adjust pricing before proposal goes out.

**Assigned to:** Orion (assessment) + Sterling (margin validation) + Felix (client pricing) + Chris (final approval)

### 2a — QBO Realm Correction (Chris input 2026-03-21)

**Critical correction:** Check Distribution Sync targets **FF Construction's QBO account** — NOT Fantastic Floors. FF has not requested this for the Fantastic Floors division ("at least for now" — Chris). Chris recently obtained access to FF Construction's QBO via his admin@ email account.

**Current state:**
- MVP (`Q3dABipnUekcFlpO`) is wired to Fantastic Floors QBO credential (`LGpzRblDucNLdRTZ`, realm `193514569899119`) — **WRONG realm for production**
- FF Construction QBO credential does NOT exist in n8n yet — needs creation

**QBO Dev App answer:** Same QBO Dev App (client ID + client secret) works for FF Construction. Chris authorizes against FF Construction's QBO account using admin@ email → creates a second credential in n8n with FF Construction's realm ID. No new app needed in QBO Dev.

**Actions required (Phase 1 completion items):**
1. Chris creates FF Construction QBO OAuth2 credential in n8n (Settings → Credentials → New → QuickBooks OAuth2, authorize with admin@ against FF Construction's account)
2. Record the new credential ID and realm ID
3. Update MVP workflow `Q3dABipnUekcFlpO`:
   - Swap QBO credential on "Query QBO Checks" node from `LGpzRblDucNLdRTZ` to new FF Construction credential
   - Update `realmId` in "Set Configuration" node from `193514569899119` to FF Construction's realm ID
4. Test with FF Construction's actual check data

**Scope note (UPDATED 2026-03-22):** Real check data confirms BOTH divisions (FF Construction + Fantastic Floors) exist in the same QBO account, distinguished by Class field. Chris decided: capture ALL classes. Fantastic Floors division data is captured and visible in output — client filters by Class as needed. This is NOT a scope expansion — it's capturing what's already in the checks. If FF later requests dedicated workflows or separate processing rules per division, THAT would be a scope expansion.

### 2b — Complexity Assessment + RT#13 Hybrid Pricing (LOCKED 2026-03-22)

**MVP build result:** 12 nodes, ~3-4 hours equivalent build effort.

**RT#13 — Complexity Reclassification Round Table (2026-03-22):**

Chris proposed hybrid pricing — system architecture is SLW-Standard, but the client environment (disorganized department, lack of structure) justifies elevated setup. Team unanimously supported after 3 iterations:

- **Iteration 1:** Full SLW-Medium? → Team AGAINST (build effort within Standard, AI agent is one node, API cost <$1/mo)
- **Iteration 2:** Medium setup ($6,500/$4,875) + $350/mo? → Team SUPPORTED (environmental complexity justifies premium)
- **Iteration 3 (FINAL):** Custom $5,500 setup + $350/mo? → Team UNANIMOUSLY SUPPORTED

**Key distinction (Orion):** Architecture = Standard. Environment = messy. The $1,000 above Standard covers extra discovery/organization work, not system complexity.

**LOCKED pricing (Chris-approved 2026-03-22):**

| Element | Base Rate | With PP | Math |
|---|---|---|---|
| Setup fee | $5,500 | **$4,125** | $5,500 × 0.75 (25% PP) |
| Monthly increment | $475 | **$350** | $475 - $125 (flat PP deduction) |

**The $125 flat deduction and 25% setup PP apply at ALL complexity levels.** Only base rates change.

### 2c — Enhanced ROI Framework (NEW — Chris input 2026-03-21)

**Chris's insight:** ROI should capture not just the hours saved from automation, but also the productive value of those hours being redirected to revenue-generating work. Additionally, error reduction has its own cost avoidance value.

**Three-Pillar ROI Model:**

| Pillar | What It Measures | Current Data | Status |
|---|---|---|---|
| **1. Direct Labor Savings** | Hours no longer spent on manual check distribution | 10-14 hrs/week, 2 team members. $10,400-$18,200/year (from proposal) | AVAILABLE |
| **2. Labor Reallocation Value** | Productive output from hours redirected to other work | Same 10-14 hrs/week, but valued at revenue-contribution rate instead of just wage cost | FRAMEWORK READY — needs framing approach decision |
| **3. Error Cost Avoidance** | Errors prevented × cost per error × frequency | Chris gathering data from FF team (2026-03-22) | PENDING — Chris action |

**Pillar 2 — Framing approach:**
The proposal should NOT mathematically double the hours (that looks inflated). Instead, present it as a SEPARATE value dimension:
- "Your team recovers 10-14 hours weekly — hours that shift from repetitive data entry to [revenue-generating activities / project management / client service]."
- Frame as: "Every hour your team ISN'T doing data entry is an hour they're doing something that moves the business forward."
- This is qualitative-with-quantitative-anchor, not a second line item in the ROI math.

**Pillar 3 — Error cost data (PENDING):**
Chris will speak with FF team members on 2026-03-22 to estimate:
- How often errors occur in the manual process
- Approximate cost per error (rework time, vendor disputes, accounting corrections)
- This data gets incorporated into the ROI section as a third value dimension

**Impact on pricing:** The enhanced ROI strengthens the VALUE JUSTIFICATION for the pricing, not the pricing itself. A stronger ROI case makes the $250/mo increment feel even more like a bargain, which supports Felix's positioning strategy.

### 2d — Final Pricing (LOCKED — Chris Approved 2026-03-22)

**Numbers (RT#13 hybrid pricing — custom $5,500 setup base):**

| Placeholder | Value | Math |
|---|---|---|
| Setup fee (base) | $5,500 | Custom — between Standard $4,500 and Medium $6,500 |
| Setup fee (with PP) | **$4,125** | $5,500 × 0.75 |
| Setup savings (PP) | $1,375 | $5,500 - $4,125 |
| Monthly base | $475 | Project-specific base |
| Monthly increment (with PP) | **$350** | $475 - $125 flat PP deduction |
| Monthly savings (PP) | $125/mo ($1,500/yr) | Flat PP deduction |
| Total monthly (FF) | **$1,100** | $750 existing + $350 |
| First-year investment | **$8,325** | $4,125 + (12 × $350) |
| First-year savings (low) | **$2,075** | $10,400 - $8,325 (Pillar 1 only) |
| First-year savings (high) | **$9,875** | $18,200 - $8,325 (Pillar 1 only) |
| Five-year investment | **$25,125** | $4,125 + (60 × $350) |
| Five-year net value | **$26,875** | $52,000 - $25,125 (Pillar 1 only) |
| First-year PP savings | **$2,875** | $1,375 setup + $1,500 monthly |
| Margin at $350/mo | $190-244/mo (54-70%) | Op cost floor $106-160/mo |
| Error cost avoidance | TBD | Pending Chris's data — will improve ROI further |

**Note:** Financial ROI math uses Pillar 1 (direct labor savings) as the conservative baseline. Pillars 2 and 3 are presented as ADDITIONAL value dimensions, not added to the core savings math — this keeps the numbers defensible and avoids looking inflated. Chris confirmed: once error cost data arrives from FF team, ROI will look even better.

**APPROVED by Chris 2026-03-22. Numbers LOCKED.**

---

## Phase 3 — Proposal Finalization

**Executes AFTER Phase 2 pricing is locked by Chris.**

### Step 3a — Populate placeholders + restructure Investment section

File: `knowledge-base/projects/fantastic-floors-paylink/proposal-paylink.md`

Replace all `[PLACEHOLDER]` values with Phase 2 validated numbers.

**Structural changes to proposal:**

1. **Executive Summary pricing table** (lines 58-63): Update with final setup + monthly + savings numbers.

2. **Investment & Return section** (lines 168-177): Replace simple 2-cell table with Partnership Progression Savings breakdown:

```markdown
**Your Investment — Partnership Progression Pricing**

Because we are already in your infrastructure from SystemLink: Monday-QuickBooks Sync, Partnership Progression Pricing reduces both your setup investment and your monthly partnership rate.

| | Base Project Rate | Your Partnership Rate | You Save |
|---|---|---|---|
| **Setup Fee** | [BASE_SETUP] | **[PP_SETUP]** | [SETUP_SAVINGS] |
| **Monthly Addition** | [BASE_MONTHLY]/mo | **[PP_MONTHLY]/mo** | $125/mo |

**Your Total Monthly Partnership: [TOTAL]/month**

Your monthly partnership now covers both SystemLink projects under one partnership — SystemLink: Monday-QuickBooks Sync and SystemLink: Check Distribution Sync.

**First-Year Partnership Progression Savings: [PP_TOTAL_SAVINGS]**

([SETUP_SAVINGS] setup savings + [ANNUAL_MONTHLY_SAVINGS] annual monthly savings)

Partnership Progression Pricing applies to every system addition. As your partnership grows, both your setup investment and monthly partnership rates continue to improve — the deeper the partnership, the greater the return.
```

**Note:** "Base Project Rate" (not "Standard Rate") per Chris's correction — each project priced on scope, not a universal standard.

3. **"What Is Included" list** (lines 178-189): Keep as-is.

4. **ROI section** (lines 191-210): Restructure into Three-Pillar ROI Model:

```markdown
**Return on Investment — Three Value Dimensions**

**1. Direct Labor Savings**

| | Conservative | High Estimate |
|---|---|---|
| Current Annual Labor Cost | $10,400/year | $18,200/year |
| Your First-Year Investment | [FIRST_YEAR_INVESTMENT] | [FIRST_YEAR_INVESTMENT] |
| **First-Year Net Savings** | **[FIRST_YEAR_SAVINGS_LOW]** | **[FIRST_YEAR_SAVINGS_HIGH]** |

| 5-Year Projection | |
|---|---|
| 5-Year Labor Savings (Conservative) | $52,000 |
| 5-Year Total Investment | [FIVE_YEAR_INVESTMENT] |
| **5-Year Net Value** | **[FIVE_YEAR_NET_VALUE]+** |

**2. Labor Reallocation**

Every hour your team isn't manually entering check data is an hour redirected to work that moves the business forward — project management, client service, revenue-generating activities. SystemLink gives your team back [HOURS_PER_WEEK] hours every week — not just as time saved, but as capacity gained.

**3. Error Prevention**

[IF ERROR DATA AVAILABLE FROM CHRIS:]
Manual data entry across three platforms introduces [ERROR_FREQUENCY] errors [per week/month]. Each error costs approximately [ERROR_COST] in rework, corrections, and delays. SystemLink eliminates manual entry entirely — your data flows once, correctly, every time.

[IF ERROR DATA NOT AVAILABLE:]
Manual data entry across three platforms introduces inevitable errors — transposed numbers, missed line items, data entered in the wrong project tab. SystemLink eliminates manual entry entirely — your data flows once, correctly, every time.
```

**Note:** Pillar 1 carries the hard numbers. Pillars 2 and 3 are value-framing — compelling but not inflated. If Chris's error data is quantifiable, Pillar 3 gets a dollar figure. If not, it remains qualitative.

### Step 3b — Update proposal metadata
- version: 1.1 → 1.2
- status: DRAFT → FINAL
- Remove internal comment block (lines 13-23)
- Update `last_updated` to current date

### Step 3c — Regenerate branded DOCX
- Delete existing DOCX
- Run `python tools/sop_docx_builder.py` on updated markdown
- Output: `knowledge-base/projects/fantastic-floors-paylink/deliverables/SystemLink-Check-Distribution-Sync-Proposal.docx`

### Step 3d — Update memory files
- Project MEMORY.md: Record validated pricing, complexity result, proposal FINAL status
- Felix MEMORY.md: Record final pricing + FF portfolio update + flat $125 deduction policy + FF-only exception
- Sterling MEMORY.md: Record margin validation + complexity assessment + Pricing Rule #3 exception

---

## Phase 4 — Deliver Proposal + MVP

**Deliverables to FF:**
1. Final branded proposal (DOCX) with validated pricing
2. Working MVP demonstration (live walkthrough)

**Presentation approach:** Show the working MVP first ("here's how it works in your environment"), then present the proposal ("here's the investment"). Demonstrate → Validate → Close.

---

## Deliverables

1. Working MVP — POC of Check Distribution Sync processing test data through full pipeline
2. `proposal-paylink.md` — FINAL proposal (validated pricing, Partnership Progression display)
3. `SystemLink-Check-Distribution-Sync-Proposal.docx` — FINAL branded DOCX

---

## Verification

**Phase 1 (MVP):**
- [x] MVP workflow built in n8n — 12 nodes, ID: Q3dABipnUekcFlpO (2026-03-20)
- [x] Duplicate prevention: Processed IDs tracking tab in Google Sheets
- [x] Unassigned routing: IF node routes items without CustomerRef to "Unassigned" tab
- [x] Build effort: ~3-4 hours equivalent (12 nodes, SLW-Standard complexity confirmed)
- [x] QBO Sandbox connection working — 403 fixed (production→sandbox URL) (2026-03-22)
- [x] Separate QBO Dev App created for this project (2026-03-22)
- [x] Google Sheets workbook created — "FF Construction - Check Distribution" (ID: `1Jh6Y7MzB05szEUQfnftLwQyhhjN3Fk9T1iHPE4dPCko`) (2026-03-22)
- [x] Google Sheets credential "Admin Google Sheets" configured (2026-03-22)
- [x] First test run — QBO check data pulled and parsed successfully (2026-03-22)
- [ ] BLOCKED: FF Construction QBO Admin Access — Chris needs company to grant admin privileges
- [ ] BLOCKED: Monday.com board access — needed for column mapping to finalize data schema
- [ ] PAUSED: Dynamic project tab creation (waiting for Monday.com column mapping)
- [x] RT#12 APPROVED — Airtable alongside Google Sheets, dual workflow, present both to FF (2026-03-22)
- [ ] PENDING: If Airtable approved → build Airtable workflow variant (~3-5 hrs additional)
- [ ] PENDING: QBO check deep links (add checkUrl column)
- [ ] PENDING: AI agent node for description parsing — bilingual EN/ES (scope TBD after Monday.com access)
- [ ] PENDING: Add ClassRef extraction to Parse & Flatten code (not currently captured)
- [ ] PENDING: Add Tags extraction to Parse & Flatten code
- [ ] PENDING: Retainers routing — separate Retainers table/tab with check # + deep link (final rules TBD after client input)
- [ ] PENDING: End-to-end test with FF Construction production data
- [ ] PENDING: Monday.com live integration (if kept alongside Airtable)

**Phase 2 (Pricing) — BLOCKED until Phase 1 completes + error data:**
- [x] Complexity assessment compared to Orion's estimate — SLW-Standard CONFIRMED (12 nodes, ~3-4 hrs)
- [x] QBO scope clarified — FF Construction QBO account. Single realm. Both divisions (FF Construction + Fantastic Floors) exist in same account, distinguished by Class field. Capture ALL classes per Chris (2026-03-22).
- [x] QBO Dev App: Chris created separate app for Project 2 (2026-03-22)
- [x] Enhanced ROI framework defined — Three-Pillar Model (2026-03-21)
- [ ] BLOCKED: Error cost data — Chris speaking with FF team (target: 2026-03-22)
- [ ] Pricing confirmed or adjusted based on complexity + error data ROI impact
- [ ] Chris approves final numbers

**Phase 3 (Proposal):**
- [ ] All `[PLACEHOLDER]` values replaced with validated numbers
- [ ] Partnership Progression table shows base rate → PP rate → savings
- [ ] $125 flat monthly deduction displayed correctly
- [ ] Forward-looking compounding language included
- [ ] ROI math verified with final numbers
- [ ] Internal comment block removed (client-facing doc)
- [ ] DOCX regenerated with final numbers
- [ ] Memory files updated

**Phase 4 (Deliver):**
- [ ] MVP demo ready for client presentation
- [ ] Proposal and MVP delivered together
