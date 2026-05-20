# SystemLink Airtable Schema & n8n Workflow Analysis Plan

## Objective
Provide READ-ONLY exploration of SystemLink Airtable schema and n8n workflow to answer five specific analysis questions about link topology, rollup references, Projects↔Checks linking, and required changes.

## User's Five Questions to Answer
1. Map the current link topology showing all relationships between tables
2. Identify which rollup fields reference CLI vs Checks
3. Confirm presence/absence of direct Projects↔Checks links
4. Explain the Unassigned→Projects backlink mechanism
5. Describe required changes to add a Projects↔Checks link

## Phase 1: Complete File Reading (PENDING)
- [ ] Read lines 900-1100 of tools/create_check_dist_workflow_v2.py (Stage 7 and final config)
- [ ] Extract complete workflow structure and any additional linking logic
- [ ] Confirm all 34+ nodes and their relationships

## Phase 2: Synthesize Analysis Answers (PENDING)
- [ ] **Question 1 - Link Topology**: Map all Airtable relationships
  - Central hub: Check Line Items (CLI) connecting Projects, Checks, Vendors
  - Vendor→CLI→Check relationships
  - Project→CLI→Check relationships  
  - Direct links: Vendor↔Check, Project↔Unassigned, Project↔Retainers, Vendor↔Checks
  - Check↔Unassigned, Vendor↔Retainers relationships
  
- [ ] **Question 2 - Rollup References**: Analyze field_id mapping for rollup fields
  - Identify which rollups aggregate from CLI table
  - Identify which rollups aggregate from Checks table
  - Note null/unimplemented fields
  
- [ ] **Question 3 - Projects↔Checks Direct Link**: Confirm absence
  - Verify no "checks_project_link" in field mapping
  - Verify no "projects_checks_backlink" in field mapping
  - Confirm all Projects↔Checks relationships flow through CLI
  
- [ ] **Question 4 - Unassigned→Projects Mechanism**: Explain backlink
  - Analyze unassigned_project_link field purpose
  - Explain why items reach Unassigned table (couldn't match project)
  - Clarify that Projects NOT automatically created for unassigned items
  
- [ ] **Question 5 - Add Projects↔Checks Link**: Schema and workflow changes
  - Schema changes needed in Airtable
  - Workflow modifications required in n8n
  - Integration points with existing find-or-create patterns

## Notes
- All file reading complete for airtable-check-dist-ids-v2.json
- Partial reading complete for create_check_dist_workflow_v2.py (lines 300-899)
- No schema design file yet read (if it exists)
- Working in READ-ONLY mode - no file modifications permitted
