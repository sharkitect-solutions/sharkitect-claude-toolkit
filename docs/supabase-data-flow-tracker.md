# Supabase Data Flow Tracker

> **Purpose:** Capture every Supabase read/write encountered during Phase 5 work. Each workspace session adds rows as it touches Supabase. This becomes the ground-truth input for Phase 6 (Supabase restructure).
>
> **How to use:** When fixing a system in Phase 5 and it queries or writes to Supabase, add a row below. Don't overthink it -- just log what you see.

---

## Data Flows Observed

| Date | Workspace | System | Table | R/W | Fields Used | What Worked | What's Missing or Broken |
|------|-----------|--------|-------|-----|-------------|-------------|--------------------------|
| 2026-04-12 | Skill Hub | Gap Pipeline (gap-watcher.py, gap-processing.md, notify-workspaces.py) | activity_stream | NONE | N/A | N/A | Gap pipeline has ZERO Supabase writes. No record of gap filing or resolution reaches Supabase. Evening system report needs "X gaps identified, Y resolved" but has no data source. Entire pipeline is file-based only. |
| 2026-04-12 | HQ | CEO Briefs Primary (n8n AI Agent) | projects | R | name,priority,queue_position,client_id,current_phase,phase_number,total_phases,blocker,target_date,health,status | Native supabaseTool getAll works. Filter string: status=in.(active,pending,blocked)&order=queue_position.asc | None |
| 2026-04-12 | HQ | CEO Briefs Primary (n8n AI Agent) | tasks | R | task,project,priority,status,carried_days,due_date | Native supabaseTool getAll works. Filter: status=neq.completed&order=created_at.asc | None |
| 2026-04-12 | HQ | CEO Briefs Primary (n8n AI Agent) | system_health | R | component,status,last_heartbeat | Native supabaseTool getAll works. Filter: status=neq.healthy | None |
| 2026-04-12 | HQ | CEO Briefs Primary/Secondary/Tertiary | activity_stream | R/W | workspace,platform,event_type,content,actor,tenant_id,timestamp | All 3 tiers write brief_sent events. Secondary+Tertiary read for dedup check (2h window). | Currently only logs brief_type in content string, not as a separate field. Makes dedup matching string-based instead of field-based. |
| 2026-04-12 | Skill Hub | Phase 5B session (manual insert) | projects | W | name,status,current_phase,phase_number,total_phases,priority,phase_description,workspace,health | Direct SQL INSERT via Supabase MCP worked. No `notes` column exists (used phase_description instead). | No `notes` or `description` column on projects table. update-project-status.py can only UPDATE existing rows, not INSERT new projects. |

---

## Schema Issues Found

Log any structural problems with the Supabase tables themselves (wrong data types, missing indexes, naming inconsistencies, tables that should be merged or split, etc.)

| Date | Table | Issue | Suggested Fix |
|------|-------|-------|---------------|
| | | | |

---

## Data Quality Issues Found

Log any problems with the actual data (stale records, duplicates, missing entries, wrong formats, etc.)

| Date | Table | Issue | Rows Affected | Fixed? |
|------|-------|-------|---------------|--------|
| | | | | |

---

## Notes

- **2026-04-12 (Phase 5B):** Gap pipeline Supabase writes DEFERRED to Phase 6. Interim solution: Sentinel reads gap status directly from Skill Hub filesystem (.gap-reports/inbox/ and processed/), filtering by date. All workspaces share the same machine -- cross-workspace filesystem reads are valid. Phase 6 should add proper activity_stream writes for gap lifecycle events.
