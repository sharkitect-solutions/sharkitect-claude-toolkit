# Supabase Audit Report — Phase 1B

**Date:** 2026-04-09
**Auditor:** Sentinel
**Project:** sharkitect-workforce (dgnjfamhwfyogmgcpedb)
**Database:** Postgres 17.6.1, us-east-2
**Part of:** Foundation Reset master plan (wise-sprouting-canyon.md)

---

## Part A: Current State

### Table Inventory Summary

| # | Table | Rows | RLS | Workspace Col | Status | Recommendation |
|---|-------|------|-----|---------------|--------|----------------|
| 1 | `memories` | 607 | Yes | Yes | Active — primary brain storage | **CLEAN** (fix naming) |
| 2 | `sessions` | 5 | Yes | No | Low use — agent session tracking | **KEEP** (add workspace col) |
| 3 | `kb_docs` | 69 | Yes | No | Active — knowledge base documents | **MODIFY** (add workspace, remove stale agent refs) |
| 4 | `logs` | 163 | Yes | No | Active — agent interaction logs | **CLEAN** (stale agent names) |
| 5 | `tasks` | 76 | Yes | Yes | Active — task tracking | **KEEP** |
| 6 | `projects` | 10 | Yes | Yes | Active — project tracking | **KEEP** |
| 7 | `escalations` | 0 | Yes | No | Zero-row, never used | **DROP** candidate |
| 8 | `audit_log` | 99 | Yes | Yes | Active — doc health audit results | **KEEP** |
| 9 | `activity_stream` | 57 | Yes | Yes | Active — cross-workspace event log | **CLEAN** (fix naming) |
| 10 | `voice_samples` | 1 | Yes | No | Minimal — Chris voice/tone samples | **MODIFY** (expand to user_preferences) |
| 11 | `work_requests` | 1 | Yes | from/to | Minimal — cross-workspace requests | **KEEP** (designed well, barely used) |
| 12 | `retained_files` | 0 | Yes | Yes | Zero-row, never used | **DROP** candidate |
| 13 | `system_health` | 11 | Yes | No | Active — component heartbeats | **KEEP** |
| 14 | `repo_findings` | 0 | Yes | No | Zero-row, never used | **DROP** candidate (repo_monitor hasn't run) |
| 15 | `dream_log` | 1 | Yes | No | Active but sparse — nightly consolidation | **KEEP** |
| 16 | `feedback_metrics` | 0 | Yes | Yes | Zero-row, never used | **DROP** candidate |
| 17 | `doc_lifecycle` | 94 | Yes | Yes | Active — document freshness tracking | **MODIFY** (add fields for queryable brain) |
| 18 | `clients` | 1 | Yes | No | Active — client master data | **KEEP** |
| 19 | `error_fixes` | 4 | Yes | No | Active — auto-fix bridge results | **KEEP** |
| 20 | `briefs` | 1 | Yes | No | Barely used — CEO brief storage | **MODIFY** (should store all briefs) |

---

### Per-Table Analysis

#### 1. `memories` (607 rows) — PRIMARY BRAIN STORE
- **Purpose:** Stores learned facts, lessons, preferences, and context across all workspaces.
- **Readers:** supabase-sync.py (all workspaces), ops-brain.py (Sentinel), dream-consolidation.py (Sentinel), n8n CEO Brief workflow
- **Writers:** supabase-sync.py (all workspaces), dream-consolidation.py (Sentinel)
- **Workspace values:** `workforce-hq` (532), `skill-management-hub` (56), `sentinel` (10), `shared` (7), `hq` (2 - NON-CANONICAL)
- **Issues:**
  - 2 records use `hq` instead of `workforce-hq`
  - `shared` (7 records) — intentional for cross-workspace memories, but undocumented convention
  - Has `embedding` column (vector type) but unclear if vector search is actually used
  - Key format `lesson:hash` makes it hard to query by topic without content scanning

#### 2. `sessions` (5 rows)
- **Purpose:** Tracks agent conversation sessions with summaries and pending tasks.
- **Agent IDs found:** `hq-agent`, `claude-code-hq`, `alex` — inconsistent naming
- **Issues:** No workspace column. `alex` agent name is from dissolved agent hierarchy.

#### 3. `kb_docs` (69 rows) — KNOWLEDGE BASE
- **Purpose:** Stores full-text knowledge base documents with embeddings.
- **Categories:** memory_topic (17), project (16), revenue (12), sop (11), strategy (5), governance (4), reference (2), operations (2)
- **Issues:**
  - No workspace column — can't filter by workspace
  - Contains references to dissolved agent `Sage (CKO)` in document headers
  - Overlaps with `memories` table in function — both store knowledge, no clear delineation
  - No `tags` or `doc_type` column for filtered queries

#### 4. `logs` (163 rows)
- **Purpose:** Agent interaction logs — tool calls, token usage, response tracking.
- **Agent IDs:** `marcus` (95 logs), `alex` (65 logs), `shared` (2), `hq-agent` (1)
- **Issues:**
  - 160 of 163 rows reference dissolved agent names (`marcus`, `alex`)
  - No new logs since April 4 — current system doesn't write to this table
  - Platform values inconsistent: `task_scheduler`, `telegram`, `claude_code`, `audit_test`, `claude-code`

#### 5. `tasks` (76 rows) — TASK TRACKING
- **Purpose:** Cross-workspace task management with priorities, status, and strategic goals.
- **All workspace values:** `workforce-hq` (76) — only HQ uses this table
- **Issues:** No tasks from Sentinel or Skill Hub despite being a shared resource.

#### 6. `projects` (10 rows)
- **Purpose:** Project portfolio tracking with phases, health, and client associations.
- **All workspace values:** `workforce-hq` (10)
- **Well-designed:** Has proper status checks, category, health tracking, target dates.

#### 7. `escalations` (0 rows) — ZERO-ROW
- **Purpose:** Designed for Telegram escalation requests. Never populated.
- **Recommendation:** DROP — the work_requests table serves a similar cross-workspace purpose.

#### 8. `audit_log` (99 rows)
- **Purpose:** Document health audit findings from nightly checks.
- **All workspace values:** `workforce-hq` (99) — only HQ docs audited
- **Comment:** "Midnight document health audit results. Each row = one check finding."
- **Issues:** Only tracks HQ documents. Sentinel and Skill Hub documents not audited here.

#### 9. `activity_stream` (57 rows) — CROSS-WORKSPACE EVENT LOG
- **Purpose:** Records significant events across all workspaces and platforms.
- **Workspace values:**
  - `skill-management-hub` (24) ✅
  - `workforce-hq` (16) ✅
  - `sentinel` (9) ✅
  - `autonomous-operations` (4) ❌ DISSOLVED WORKSPACE
  - `ops-center` (2) ❌ UNKNOWN WORKSPACE
  - `HQ` (1) ❌ CASE INCONSISTENCY (should be `workforce-hq`)
  - `remote-trigger` (1) ❌ NOT A WORKSPACE
- **Issues:** 8 records (14%) use non-canonical or invalid workspace names.

#### 10. `voice_samples` (1 row)
- **Purpose:** Chris's approved writing samples for voice matching.
- **Issues:** Only 1 sample. No domain categorization. Cannot serve as a structured preference store.

#### 11. `work_requests` (1 row)
- **Purpose:** Cross-workspace work requests with status tracking.
- **Design:** Well-structured (from_workspace, to_workspace, rationale, response).
- **Issues:** Barely used (1 request ever).

#### 12. `retained_files` (0 rows) — ZERO-ROW
- **Purpose:** Tracks files retained during workspace dissolution.
- **Recommendation:** DROP — dissolution is complete, this serves no ongoing purpose.

#### 13. `system_health` (11 rows)
- **Purpose:** Component heartbeat tracking for autonomous systems.
- **Components:** gap-pipeline, nightly-dream, freshness-auditor, n8n-watcher, sentinel-session, etc.
- **Issues:**
  - `sentinel-repo-monitor` status is `degraded` (last heartbeat April 3, never actually ran)
  - `workforce-hq-sync` and `sentinel-sync` heartbeats are from April 8 — slightly stale

#### 14. `repo_findings` (0 rows) — ZERO-ROW
- **Purpose:** Stores findings from repo monitoring (upstream changes, relevance scores).
- **Recommendation:** KEEP (conditionally) — repo_monitor hasn't run yet (first scheduled for April 12). Evaluate after first run.

#### 15. `dream_log` (1 row)
- **Purpose:** Tracks nightly dream consolidation run results.
- **Issues:** Only 1 entry despite dream running nightly — either not logging every run or clearing old entries.

#### 16. `feedback_metrics` (0 rows) — ZERO-ROW
- **Purpose:** Designed for workspace feedback trend tracking.
- **Recommendation:** DROP — the feedback_tracker.py tool exists but never wrote to this table.

#### 17. `doc_lifecycle` (94 rows) — DOCUMENT FRESHNESS
- **Purpose:** Tracks document review cycles, escalation states, and drift.
- **Workspace values:** `workforce-hq` (77), `skill-management-hub` (14), `sentinel` (3)
- **Closest existing table to the target `documents` table from the design spec.**
- **Issues:**
  - Missing: purpose_summary, tags, status/superseded_by, content_hash, sync_status, related_docs
  - Only 3 Sentinel documents tracked — should be more
  - No global (~/.claude/) documents tracked

#### 18. `clients` (1 row)
- **Purpose:** Client master data with payment preferences and contacts.
- **Well-designed:** Has detailed payment terms, contacts, industry data.

#### 19. `error_fixes` (4 rows)
- **Purpose:** Tracks n8n error auto-fix attempts from the Error Auto-Fix Bridge.
- **Issues:** Self-referencing FK `similar_fix_id` has no index (performance advisory).

#### 20. `briefs` (1 row)
- **Purpose:** Stores CEO daily briefs.
- **Issues:** Only 1 brief stored (April 8 morning). Should have 3x/day entries. Either n8n workflow isn't writing here, or entries are being overwritten.

---

### Workspace Naming Audit

**Distinct values found across ALL tables with workspace columns:**

| Value | Tables | Count | Canonical? | Action |
|-------|--------|-------|------------|--------|
| `workforce-hq` | memories, tasks, projects, audit_log, activity_stream, doc_lifecycle | 810 | YES | — |
| `skill-management-hub` | memories, activity_stream, doc_lifecycle, work_requests | 95 | YES | — |
| `sentinel` | memories, activity_stream, doc_lifecycle | 22 | YES | — |
| `shared` | memories | 7 | CONDITIONAL | Document convention or migrate to specific workspace |
| `autonomous-operations` | activity_stream | 4 | NO — dissolved | Clean: update to owning workspace or archive |
| `hq` | memories | 2 | NO — abbreviation | Clean: update to `workforce-hq` |
| `ops-center` | activity_stream | 2 | NO — unknown | Clean: investigate and fix |
| `HQ` | activity_stream | 1 | NO — case mismatch | Clean: update to `workforce-hq` |
| `remote-trigger` | activity_stream | 1 | NO — not a workspace | Clean: remove or recategorize |

**Canonical names (to be enforced):**
- `workforce-hq`
- `skill-management-hub`
- `sentinel`
- `global` (for ~/.claude/ artifacts — currently unrepresented)

**Total records needing cleanup:** 10 records across 2 tables.

---

### Schema Gaps — Tables That Should Exist But Don't

Based on the target schema in the design spec (`2026-04-09-supabase-brain-context-guardian-design.md`):

| Target Table | Status | Notes |
|-------------|--------|-------|
| `documents` | MISSING — `doc_lifecycle` is partial | Needs: purpose_summary, tags, content_hash, sync_status, superseded_by |
| `document_relationships` | MISSING | No cross-reference data exists anywhere |
| `lessons_learned` | MISSING — `memories` is partial | Lessons exist but lack category/tags for domain queries |
| `user_preferences` | MISSING — `voice_samples` is minimal | Only 1 sample, no structured preference data |
| `system_specs` | MISSING | No queryable system spec registry |
| `automation_registry` | MISSING | No automation tracking table (system_health is closest but different purpose) |
| `sync_conflicts` | MISSING | No conflict reconciliation tracking |

---

### RLS Check

**All 20 tables have RLS enabled.** However:

**Security advisories (4 WARN):**

| Table | Issue | Severity |
|-------|-------|----------|
| `error_fixes` | RLS policy "Service role full access" uses `USING (true)` — bypasses RLS | WARN |
| `escalations` | Same — `USING (true)` bypass | WARN |
| `projects` | Same — `USING (true)` bypass | WARN |
| `tasks` | Same — `USING (true)` bypass | WARN |

These are acceptable for a single-tenant system where only service_role accesses the data, but should be tightened if public-facing APIs or multi-tenant access are ever added.

**Performance advisory:**
- `doc_lifecycle` RLS policy re-evaluates `current_setting()` per row (use `(select auth.function())` pattern)
- `vector` extension in public schema — should move to dedicated schema
- 16 unused indexes across multiple tables (mostly on zero-row or barely-used tables)
- Unindexed foreign key on `error_fixes.similar_fix_id`

---

### Zero-Row Tables

| Table | Created For | Ever Used? | Recommendation |
|-------|-----------|-----------|----------------|
| `escalations` | Telegram escalation routing | No | DROP |
| `retained_files` | Workspace dissolution file tracking | No | DROP |
| `repo_findings` | Repo monitor upstream changes | Not yet (first run April 12) | KEEP (evaluate after first run) |
| `feedback_metrics` | Workspace feedback trends | No | DROP |

---

### Duplicate/Overlapping Tables

| Tables | Overlap | Recommendation |
|--------|---------|----------------|
| `memories` + `kb_docs` | Both store knowledge/lessons with embeddings | Merge: `kb_docs` content → structured `lessons_learned` table; keep `memories` as the brain store |
| `doc_lifecycle` + target `documents` | `doc_lifecycle` is a subset of what `documents` needs | Evolve: extend `doc_lifecycle` into `documents` table |
| `audit_log` vs `activity_stream` | Both log events; audit_log is HQ-only health checks, activity_stream is cross-workspace | Keep separate — different purposes |

---

### Stale Agent References

| Table | Agent Name | Records | Status |
|-------|-----------|---------|--------|
| `logs` | `marcus` | 95 | Dissolved agent — historical data |
| `logs` | `alex` | 65 | Dissolved agent — historical data |
| `sessions` | `alex` | default value | Dissolved agent in column default |
| `kb_docs` | `Sage (CKO)` | ~2 | Dissolved agent in document content |
| `memories` | `shared` agent_id | 7+ | Not dissolved, but undocumented |

---

## Part B: Queryable Brain Gap Analysis

Evaluating 6 use cases against current Supabase state, measured against the target schema in the design spec.

### 1. Document Registry

**Status: PARTIAL**

**What exists:** `doc_lifecycle` table with 94 rows tracks documents across 3 workspaces with file paths, doc types, review cycles, and escalation states. This is the closest thing to a document registry.

**What's missing vs target `documents` table:**
- No `purpose_summary` — agents can't query "what does this file do?"
- No `tags[]` — can't query "what do we have about Airtable?"
- No `status` enum (active/stale/superseded) — can't filter out dead docs
- No `superseded_by` — no supersession chain
- No `content_hash` — can't detect real changes vs phantom modifications
- No `sync_status` — no Supabase-to-local sync tracking
- No `filename` column — only full `doc_path`, making quick searches harder
- Only 94 of estimated 200+ significant files tracked
- No global (`~/.claude/`) documents tracked at all
- No `owner_workspace` (for global files maintained by specific workspaces)

**Can an agent query "what documents exist in workspace X of type Y?":** Partially. `SELECT * FROM doc_lifecycle WHERE workspace = 'skill-management-hub' AND doc_type = 'workflow'` works for the 94 tracked docs, but misses most files and has no purpose/tag metadata.

### 2. Lessons Learned

**Status: PARTIAL**

**What exists:** `memories` table stores 607 records including lessons (category='lesson' with key format `lesson:hash`). `kb_docs` table stores 69 knowledge base documents including SOPs, strategies, and project docs.

**What's missing vs target `lessons_learned` table:**
- No structured `category` taxonomy (preference/process/architecture/error/api-limitation)
- No `tags[]` column for domain-specific queries
- No `applies_to[]` — can't filter by which workspaces a lesson applies to
- No `confidence` enum (confirmed/provisional) — the `confidence` column in `memories` uses 'inferred' for everything
- Lessons in `memories` have opaque keys (`lesson:2ae1d8f92235`) — not human-readable
- `kb_docs` has full documents, not structured queryable lessons
- The flat file `~/.claude/lessons-learned.md` remains the primary source — Supabase is not authoritative

**Can an agent query "what have we learned about Airtable?":** No efficient way. Would need full-text scan of `memories.content` WHERE category='lesson' AND content ILIKE '%airtable%'. No tag-based or category-based filtering.

### 3. User Preferences & Voice

**Status: MISSING**

**What exists:** `voice_samples` table with 1 row (an approved email sample). `memories` table has some preference data mixed in with other content.

**What's missing vs target `user_preferences` table:**
- No structured `domain` taxonomy (communication/design/code/decisions)
- No `strength` indicator (strong/moderate/emerging)
- No `examples[]` for concrete reference
- Only 1 voice sample — insufficient for consistent voice matching
- Preferences scattered across `memories` content and `lessons-learned.md` without queryable structure

**Can an agent writing an email query "how does Chris communicate?":** No. Would need to read the full `lessons-learned.md` file and hope to find relevant entries. No structured, queryable preference data.

### 4. Cross-Workspace Awareness

**Status: MISSING**

**What exists:** `system_health` tracks 11 components by name, but not mapped to workspaces. `activity_stream` shows events per workspace but doesn't describe what systems exist.

**What's missing vs target `system_specs` + `automation_registry` tables:**
- No table listing what autonomous systems exist per workspace
- No queryable specification data (schedule, dependencies, data sources)
- No way to query "what systems in workspace Y would break if I change X?"
- The `autonomous-systems-inventory.md` file exists but isn't in Supabase

**Can an agent query "what systems exist in workspace Y that might be affected by this change?":** No. This data only exists in the local markdown file `~/.claude/docs/autonomous-systems-inventory.md`.

### 5. Audit Scheduling

**Status: PARTIAL**

**What exists:** `doc_lifecycle` has `review_cycle_days`, `next_review`, and `escalation_state` columns for 94 documents. The `freshness-auditor.py` tool queries this table.

**What works:**
- `SELECT * FROM doc_lifecycle WHERE next_review < NOW()` returns overdue documents
- Escalation states track whether a doc is current, due, or overdue
- Review counts and last review summaries are tracked

**What's missing:**
- Only 94 of 200+ documents tracked
- No purpose/tags — can't prioritize which overdue reviews matter most
- No global document tracking
- Review cadences may be wrong (all seem default 90 days)

**Can Sentinel query "which documents are overdue for review?":** Yes, for the 94 tracked docs. But coverage is incomplete (~47% of significant files).

### 6. Impact Detection

**Status: MISSING**

**What exists:** Nothing. No cross-reference data anywhere in Supabase.

**What's missing vs target `document_relationships` table:**
- No table tracking which documents reference which other documents
- No `relationship_type` data (references, supersedes, depends_on, duplicates)
- The current drift-detection hook reads a local file cache, not Supabase
- When a document changes, there's no way to query what else is affected

**Can an agent query "what other documents reference document X?":** No. This capability does not exist.

---

## Schema Recommendations for Phase 4B

### Priority 1: Extend `doc_lifecycle` → `documents`
Add columns: `purpose_summary`, `filename`, `tags text[]`, `status` (active/stale/superseded/archived), `superseded_by uuid`, `content_hash text`, `sync_status text`, `owner_workspace text`. Populate from filesystem scan across all workspaces + global.

### Priority 2: Create `document_relationships`
Junction table per design spec. Initial population by scanning document content for cross-references (file paths, document names).

### Priority 3: Create `lessons_learned`
Structured table per design spec. Initial population by parsing `~/.claude/lessons-learned.md` into rows with category/tags.

### Priority 4: Create `user_preferences`
Per design spec. Initial population from lessons-learned.md Preferences section and voice_samples content.

### Priority 5: Create `system_specs`
Per design spec. Initial population from `autonomous-systems-inventory.md`.

### Priority 6: Create `automation_registry`
Per design spec. Auto-population from Task Scheduler + n8n + hook registrations.

### Priority 7: Create `sync_conflicts`
Per design spec. Needed once reconciliation protocol is operational.

### Cleanup Actions (Phase 3)
1. Fix 10 records with non-canonical workspace names across `memories` and `activity_stream`
2. Update `sessions.agent_id` default from `'alex'` to `'claude-code'`
3. Drop 3 zero-row tables: `escalations`, `retained_files`, `feedback_metrics`
4. Evaluate `repo_findings` after first repo monitor run (April 12)
5. Fix `doc_lifecycle` RLS policy to use `(select auth.function())` pattern
6. Move `vector` extension out of public schema
7. Remove or archive 16 unused indexes (mostly on unused tables)
8. Add unindexed FK index on `error_fixes.similar_fix_id`

---

## Summary Statistics

- **Total tables:** 20
- **Active tables:** 14 (with data and active read/write patterns)
- **Zero-row candidates for drop:** 3-4
- **Tables needing schema modification:** 4 (doc_lifecycle, kb_docs, sessions, briefs)
- **Records with non-canonical workspace names:** 10
- **Records referencing dissolved agents:** 162
- **Security warnings:** 5 (4 RLS always-true, 1 extension in public)
- **Performance warnings:** 18 (16 unused indexes, 1 RLS initplan, 1 unindexed FK)
- **Gap analysis:** 1 EXISTS (partial audit scheduling), 2 PARTIAL (document registry, lessons), 3 MISSING (preferences, cross-workspace, impact detection)
- **New tables needed for queryable brain:** 5 (document_relationships, lessons_learned, user_preferences, system_specs, automation_registry) + 1 (sync_conflicts)
