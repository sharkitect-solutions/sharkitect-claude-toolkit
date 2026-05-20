# Plan: Restructure Proposal Scope of Work — 3-Week Timeline

## Context
The proposal's Scope of Work section (Phases 1-4, 4-5 weeks) doesn't reflect reality. Most of the work is already done:
- Discovery & Design: ~95% complete (months of back-and-forth, complex 66-tab analysis)
- Database: 6 tables built, 121 fields, all linked records working
- Workflow: v3 live with 19 nodes, void detection, memo parsing
- Dashboard: 6 Interface pages built in Airtable

The client is an existing partner with all system access already granted. The proposal timeline needs to be restructured to 3 weeks max, reflecting what's actually left to do — not a generic template.

## What's Actually Left to Build
1. **Post-meeting tweaks** — minor adjustments based on Friday presentation feedback
2. **Budget threshold settings** — confirm % with Juan, configure alerts
3. **Project breakdown approach** — help client set up manual tracking or find extraction method
4. **Historical data migration** — build automation to extract from 66 Google Sheets tabs + Monday boards
5. **Dedup guardrails** — add check-before-insert logic to prevent duplicates on re-runs
6. **Budget threshold email notification** — may need Airtable Team tier ($20/mo) or n8n webhook approach
7. **Discovery questionnaire/spreadsheet** — for client to fill in project details (active/inactive, budgets, etc.)
8. **Dashboard polish** — tweaks based on demo feedback
9. **End-to-end testing** with full production data
10. **SOP documentation + training walkthrough**

## File to Edit
`knowledge-base/projects/fantastic-floors-paylink/proposal-paylink.md`
- Lines ~264-298: Scope of Work section (Phases 1-4)
- Lines ~298: "Your team's part" paragraph

## Proposed New Scope of Work

### Phase 1: Finalize & Configure (Week 1)
- Incorporate feedback from Friday presentation
- Confirm budget thresholds and alert recipients with Juan
- Send project details questionnaire (active/inactive, budgets, addresses)
- Plan historical data migration strategy
- Determine project breakdown tracking approach
- Add dedup guardrails to workflow (check-before-insert)

### Phase 2: Migrate & Test (Weeks 1–2)
- Build historical data migration automation (Google Sheets → Airtable)
- Migrate existing data, verify accuracy (row counts, totals match source)
- Configure budget threshold email notifications
- Final workflow adjustments and polish
- End-to-end testing with full production data

### Phase 3: Delivery & Handoff (Weeks 2–3)
- Final dashboard polish based on team feedback
- Client walkthrough and training session
- SOP document delivered
- Go-live: activate automated schedule
- Week 1 monitoring by Sharkitect Digital
- Confirm system running independently

### "Your team's part" update
Remove: provide system access (already have it), respond to discovery questionnaire (already done), designate point of contact (already established)
Keep: fill out project details sheet (budgets, active/inactive), confirm budget threshold preference, participate in training walkthrough

## Budget Alert Email — Research Note
Airtable free plan limits automation emails to workspace members only. Options:
1. Upgrade to Airtable Team ($20/mo) — allows sending to external emails + more records
2. Use n8n webhook: Airtable automation triggers webhook → n8n sends email via SMTP
3. Airtable automation → Slack/other notification (if they use it)
Recommend: factor the $20/mo Airtable cost into the platform costs Chris absorbs per PLATFORM COST ABSORPTION rule. Research exact Team tier email capabilities before deciding.

## Also Update
- Internal comment at top: update back sheet notes about timeline
- "Implementation Time" in Bottom Line table: change "4-5 weeks" → "3 weeks"
- First-year net savings recalculation if timeline changes affect anything (it doesn't — pricing unchanged)

## Verification
- Read final proposal end-to-end after edits
- Regenerate DOCX via pandoc (no TOC)
- Confirm no references to "4-5 weeks" remain
- Confirm "Your team's part" doesn't ask for things already provided
