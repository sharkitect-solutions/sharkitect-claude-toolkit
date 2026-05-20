# Plan: FF Bottleneck Solution — Check-to-Project Distribution Blueprint

## Context

Fantastic Floors (FF) has a bottleneck in their check payment reconciliation process. They write checks in QuickBooks Online (QBO) to installers who work across multiple projects. Each check has multiple line items, each tagged to a different project via QBO's native "Customer" column on expense lines.

**Current process (manual, high error risk):**
- 2 employees spend most of Friday on check reconciliation:
  - Employee 1: Goes through each check line item, verifying it matches the corresponding invoice (accuracy check)
  - Employee 2: Copies verified data into Google Sheets (the bulk of the time)
  - Then data gets manually entered into Monday.com
- High risk probability of errors — wrong numbers assigned to wrong projects. Some errors are caught, some are not. Uncaught errors compound: they affect project budgets AND future estimates (FF uses past project actuals to calibrate new bids)
- Google Sheets is one massive unstructured sheet — projects scattered everywhere, no organization

**What Chris wants:**
1. **Tiered solution options** — present FF with multiple levels, from basic automation to a complete end-to-end system
2. Google Sheets restructure: individual sheet per project + master summary sheet
3. Scalable, plug-and-play solution
4. Blueprint document to present to FF for approval → then formal proposal if approved

**Future consideration (not in this blueprint's build scope, but referenced as higher tiers):**
- Invoice capture workflow — when invoices are created/approved in QBO, capture and store that data so it feeds cleanly into checks (precursor workflow)
- End-of-month automated reporting with AI analysis — budget variance, project health, executive insights

**This is a new FF project (second engagement).** FF is Sharkitect's first client ($8,500 setup, $750/mo partnership). The existing SystemLink project handles Monday→QBO estimate sync. This new project handles the reverse direction: QBO check data → Google Sheets + Monday.

---

## QBO API Research Findings

### Purchase Entity (Checks)
- QBO stores checks as `Purchase` entities with `PaymentType = "Check"`
- **PrintStatus field**: Values include `NotSet`, `NeedToPrint`, `PrintComplete` — THIS is the trigger indicator
- **Line items**: Use `AccountBasedExpenseLineDetail` which contains a `CustomerRef` field
- **CustomerRef on line items**: Each line item CAN reference a different customer — this is exactly the native column FF just enabled
- **Query**: `SELECT * FROM Purchase WHERE PaymentType = 'Check' AND PrintStatus = 'PrintComplete'`

### Trigger Options
| Option | Mechanism | Reliability | Latency |
|--------|-----------|-------------|---------|
| **QBO Webhooks** | Purchase Create/Update event → n8n webhook | Medium — notifications batch every ~5 min, require CDC verification | ~5 min |
| **Scheduled Polling** | n8n cron queries QBO for new printed checks since last timestamp | High — deterministic, no missed events | Configurable (e.g., every 15 min) |
| **Hybrid** | Webhook triggers immediate poll; scheduled poll as safety net | Highest — best of both | ~5 min + safety net |
| **Single Batch Run** | One scheduled run after FF's check-printing cutoff (e.g., Thursday 8 PM or Friday 6 AM) | Highest — processes all checks in one pass, zero unnecessary API calls | Once per cycle (next business morning) |

**Recommendation: Single Batch Run** — FF prints all checks by a known cutoff day (currently Thursday). A single scheduled run after that cutoff is the simplest, most reliable, and most efficient approach. One API call pulls all printed checks for the week, processes them in one pass, and distributes to Google Sheets + Monday.com. Zero wasted API calls during the week. If FF's process changes (e.g., checks printed multiple days), the trigger can be upgraded to Scheduled Polling with no workflow changes — only the trigger node changes.

**Blueprint presentation:** Present Single Batch Run as the recommended default (matched to their current Thursday cutoff). Note that Scheduled Polling is available if their process evolves to print checks on multiple days. This positions the system as adaptable without over-engineering for Day 1.

### n8n Capabilities
- n8n has a native QuickBooks Online node (supports OAuth2, queries, CRUD)
- n8n has native Google Sheets node (append rows, create sheets, read/write)
- n8n has native Monday.com node (create items, update columns, subitems)
- All three integrations are proven in our existing FF SystemLink workflows

---

## Solution Architecture

### Workflow: "PayLink: QBO Check Distribution"

**Project name** (per RT#10 naming convention): **PayLink: QuickBooks Check Distribution**

```
[Scheduled Trigger: Single batch run — Thursday 8 PM or Friday 6 AM (after check-printing cutoff)]
    │
    ▼
[Query QBO: All printed checks since last run]
    │ SELECT * FROM Purchase WHERE PaymentType='Check'
    │   AND PrintStatus='PrintComplete' AND MetaData.LastUpdatedTime > {{last_run}}
    │
    ▼
[For Each Check]
    │
    ▼
[Extract Line Items + CustomerRef per line]
    │
    ├──▶ [Google Sheets: Append to project-specific sheet]
    │     - Find or create sheet tab for this project/customer
    │     - Append row: Date, Check#, Vendor, Description, Amount, etc.
    │     - Summary sheet auto-updates via Google Sheets formulas
    │
    ├──▶ [Monday.com: Add to project board/group]
    │     - Find the matching project board/group
    │     - Create item with check details
    │     - Link to original QBO transaction
    │
    └──▶ [Update tracking: Mark check as processed]
          - Store check ID + timestamp to avoid reprocessing
          - Airtable or JSON file for state tracking
```

### Google Sheets Structure (New)
```
Fantastic Floors Master Workbook
├── Dashboard (summary sheet)
│   ├── Project-by-project totals (auto-calculated)
│   ├── Monthly breakdown
│   └── Running totals
├── [Project A] (individual tab)
│   ├── Date | Check # | Vendor | Description | Amount | Category
│   └── ... (one row per check line item)
├── [Project B] (individual tab)
│   └── ...
└── [Project N] (individual tab)
    └── ...
```

**Migration plan for existing messy sheet:**
1. Archive current sheet as-is (rename to "Archive - [date]")
2. Create new structured workbook with above layout
3. Manual data migration: FF staff or SD maps existing data into per-project tabs
4. New automation writes ONLY to the new structured workbook

### Error Handling
| Scenario | Response |
|----------|----------|
| Line item has no CustomerRef | Route to "Unassigned" tab in Sheets + flag in Monday for manual review |
| Project/customer doesn't match any existing sheet tab | Auto-create new tab from template, notify FF team |
| QBO API rate limit | Exponential backoff; retry on next poll cycle |
| Duplicate detection | Check ID + line item index stored; skip already-processed |
| Google Sheets quota | Queue and retry; alert if persistent |

### Safeguards (matching SystemLink SOP pattern)
1. **Duplicate prevention** — each check line item tracked by Check ID + line index; never processed twice
2. **Unassigned routing** — line items without a CustomerRef don't silently drop; they go to a review queue
3. **Reconciliation check** — weekly summary email comparing QBO check totals vs Sheets totals (optional Phase 2)
4. **Audit trail** — every automated entry includes source check number, QBO transaction link, processing timestamp

---

## Tiered Solution Design

The blueprint presents FF with escalating solution tiers. Each tier builds on the previous one. This lets FF choose their comfort level and budget — and creates a natural upsell path.

### Tier 1 — PayLink Core (Check Distribution)
**What it solves:** The Friday bottleneck. Automates check-to-project distribution.
- Printed checks → extract line items → distribute to Google Sheets (per-project tabs) + Monday.com
- Google Sheets restructure (per-project tabs + Dashboard)
- Duplicate prevention, error handling, audit trail
- **This is the workflow detailed in the Solution Architecture section above**
- **Complexity:** SLW-Standard

### Tier 2 — PayLink Plus (Check Distribution + Invoice Capture)
**What it solves:** Everything in Tier 1, plus captures invoice data upstream so check creation is faster and verification is partially automated.
- Invoice capture workflow: when invoices are created/approved in QBO, data is stored and organized
- Invoice data feeds into check preparation — pre-populates or validates check line items
- System can flag when check line items don't match invoices (automated verification assist)
- Reduces the manual verification step (Employee 1's current job)
- **Complexity:** SLW-Medium (two connected workflows)

### Tier 3 — PayLink Complete (Full Financial Visibility)
**What it solves:** Everything in Tier 2, plus end-of-month automated reporting and AI-powered analysis.
- End-of-month automated reporting: budget vs. actuals per project
- AI-powered analysis: variance detection, budget health scoring, cost trend identification
- Executive summary generated automatically — insights on which projects are over/under budget, recommendations
- Project-level financial snapshots for estimating future bids more accurately
- **Complexity:** SLW-Medium to SLW-Complex (depends on report depth)

**Blueprint presentation strategy:** Lead with Tier 1 (what they asked for), show Tier 2 and 3 as "what becomes possible." Let FF see the full vision but make it clear Tier 1 is the starting point and delivers immediate value on its own.

---

## Deliverables

### Part 1: Blueprint Document (IMMEDIATE)

A branded DOCX using `tools/sop_docx_builder.py` that Chris presents to FF. Client-facing, plain language.

**Structure:**
1. Cover page (branded)
2. Executive Summary — the problem, the cost of the problem, the solution options
3. Current State — how it works today + **[VISUAL: Current vs. Future State diagram]**
4. Solution Options — Three tiers + **[VISUAL: Tiered Solution Overview]**
   - **Tier 1: PayLink Core** — Check distribution automation (the immediate fix)
   - **Tier 2: PayLink Plus** — Add invoice capture + automated verification
   - **Tier 3: PayLink Complete** — Add end-of-month reporting + AI analysis
5. How Tier 1 Works — Detailed walkthrough + **[VISUAL: PayLink Workflow Diagram]**
6. Google Sheets Restructure — new structure, migration plan + **[VISUAL: Sheets Structure mockup]**
7. Implementation Timeline — phases, responsibilities + **[VISUAL: Implementation Timeline]**
8. What This Means for Your Team — time saved, error risk eliminated, real-time visibility, better estimates
9. Next Steps — approval → proposal → build
10. Closing page (branded)

**Tone:** Same as SystemLink SOP — 3rd-5th grade reading level, plain language, Good Doctor metaphor where appropriate. FF team is the audience.

**Frontmatter:**
```yaml
document: PayLink QBO Check Distribution Blueprint
document_number: SD-BP-FF-002
version: 1.0
last_updated: 2026-03-10
client: Fantastic Floors
cover_title: PayLink
cover_subtitle: QuickBooks Check Distribution | Automated Project Tracking
cover_type: Solution Blueprint
```

### Part 1B: Visual Diagrams (Figma — alongside Blueprint)

Professional, client-facing visuals that Chris presents alongside the written blueprint. Created in FigJam/Figma for high-quality output. These make the solution tangible — FF can see the system, not just read about it.

**Diagrams to create:**

1. **Current vs. Future State** — Side-by-side comparison
   - LEFT: "Today" — manual Friday process (2 employees, verification step, manual copying, manual Monday entry, error risk arrows, time sink indicator)
   - RIGHT: "With PayLink" — automated flow (one scheduled run, automatic distribution, per-project sheets, real-time Monday updates)
   - Visual impact: messy/manual on left, clean/automated on right

2. **PayLink Workflow Diagram** — The core Tier 1 automation flow
   - Scheduled trigger → QBO query → line item extraction → split to Google Sheets + Monday.com
   - Clean, labeled nodes with arrows
   - Safeguards called out (duplicate prevention, unassigned routing, audit trail)
   - Color-coded: QBO = green, Google Sheets = blue, Monday.com = orange/red

3. **Google Sheets Structure** — Visual mockup of the new workbook
   - Tab bar showing Dashboard + project tabs
   - Dashboard with summary table (project names, totals, monthly breakdown)
   - Single project tab with column headers and sample data rows
   - Clean, looks like an actual spreadsheet

4. **Tiered Solution Overview** — Visual showing all 3 tiers
   - Stacked or side-by-side comparison
   - Tier 1 (Core) highlighted as "Start Here"
   - Tier 2 and 3 shown as expansion path with arrows
   - What each tier adds, visually distinct

5. **Implementation Timeline** — Phased visual
   - Week-by-week or phase-by-phase Gantt-style
   - What SD does vs. what FF does (color-coded)
   - Key milestones marked (setup, testing, go-live)

**Design standards:**
- Sharkitect Digital brand colors (Navy #0A2540, Accent #1B6B93)
- Clean, minimal — trades owners need to understand this at a glance
- No technical jargon in labels
- Professional enough to present in a meeting
- Export as PNG/PDF for embedding in DOCX or standalone presentation

**Tool:** Figma MCP (`generate_diagram` for FigJam or `get_design_context` for design files)

### Part 2: Proposal (AFTER FF APPROVAL)

If FF approves the blueprint, write a formal proposal using the proposal template pattern from the existing FF engagement. This includes:
- Scope of work (for whichever tier FF selects — likely Tier 1 to start)
- Pricing (per pricing-structure.md — this is a second SLW-type project)
- Timeline
- Deliverables
- Terms

**Pricing context:** This is FF's second project. Per pricing-structure.md: 25% setup fee discount on 2nd system ($4,500 × 0.75 = $3,375). Monthly partnership already active at $750/mo. Tier complexity mapping:
- Tier 1 (Core): SLW-Standard → $3,375 setup (discounted)
- Tier 2 (Plus): SLW-Medium → pricing TBD per complexity assessment
- Tier 3 (Complete): SLW-Medium to Complex → pricing TBD per complexity assessment

---

## Execution Steps

### Step 1: Write the Blueprint Markdown
- Create `knowledge-base/projects/fantastic-floors-paylink/blueprint-qbo-check-distribution.md`
- Write full blueprint content following structure above
- Client-facing language, brand-compliant

### Step 2: Create Visual Diagrams (Figma)
- Use Figma MCP `generate_diagram` to create each of the 5 diagrams
- Brand colors: Navy #0A2540, Accent #1B6B93, clean minimal style
- Priority order: (1) Current vs. Future State, (2) PayLink Workflow, (3) Tiered Overview, (4) Google Sheets Structure, (5) Implementation Timeline
- Export as high-res PNG for DOCX embedding and standalone use
- Save to `knowledge-base/projects/fantastic-floors-paylink/deliverables/visuals/`

### Step 3: Generate Branded DOCX
- Run `python tools/sop_docx_builder.py` on the markdown
- Output to `knowledge-base/projects/fantastic-floors-paylink/deliverables/`
- Embed key visuals inline where they add clarity (Current vs Future in Section 3, Workflow in Section 5, Sheets Structure in Section 6, Timeline in Section 7)
- Verify cover page, TOC, closing page render correctly

### Step 4: Assemble Presentation Package
- Blueprint DOCX (with embedded visuals)
- Standalone visual diagrams (PNG exports for screen-sharing or printing)
- Both formats ready for Chris to present to FF

### Step 5: Update Project Memory
- Create `knowledge-base/projects/fantastic-floors-paylink/` directory
- Update agent MEMORY.md files (Marcus, Atlas, Orion, Felix)
- Log in session history

### Step 6: Present to Chris for Review
- Show blueprint content + visuals for approval before sending to FF
- Chris may want adjustments to tone, scope, visual style, or technical detail level

### Step 7: (Conditional) Write Proposal
- Only after FF approves the blueprint
- Use proposal template pattern
- Route through Felix (Revenue) for pricing validation, Vera for brand pass

---

## Agent Routing (Marcus Coordination)

| Agent | Role | Deliverable |
|-------|------|-------------|
| **Atlas** (COO) | Process design — current vs future state, implementation timeline | Blueprint sections 3, 4, 6 |
| **Orion** (CTO) | Technical architecture — n8n workflow design, API integration, error handling | Blueprint sections 4, 5 (technical details) |
| **Felix** (Revenue) | Pricing, proposal structure, client relationship context | Proposal (Part 2), pricing validation |
| **Vera** (Brand) | Voice/readability pass on final blueprint | Final polish |
| **Sterling** (CFO) | Financial accuracy — check reconciliation logic, audit trail design | Blueprint section 4 (safeguards) |
| **Sage** (Knowledge) | KB structure, document classification, cross-references | Post-completion documentation |

---

## Verification

1. Blueprint markdown passes readability check (3rd-5th grade level)
2. DOCX generates cleanly with branded cover/closing pages
3. Technical architecture is feasible with confirmed QBO API capabilities
4. Pricing aligns with pricing-structure.md for second-project discounts
5. Blueprint content is client-appropriate (no internal jargon, no SD-specific references)
6. Google Sheets structure is practical and scalable
7. Error handling covers all edge cases identified
8. Three tiers are clearly differentiated — each builds on the previous, value is obvious
9. Current state accurately describes the verification + copying process (not just "copying")
10. Error risk language is accurate — "high risk probability," not "frequent errors nobody catches"
11. Tier 2/3 are presented as future options, not commitments — Tier 1 stands alone
12. All 5 visual diagrams created, brand-compliant, and client-appropriate
13. Visuals embedded in DOCX at correct sections + available as standalone PNGs
14. Chris reviews and approves blueprint + visuals before presenting to FF
