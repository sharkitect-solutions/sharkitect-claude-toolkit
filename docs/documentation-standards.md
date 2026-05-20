# Documentation Standards SOP — Sharkitect Digital

**Created:** 2026-04-15
**Updated:** 2026-04-15
**Owner:** Sentinel (defines and audits) | All workspaces (follow) | Skill Hub (contributed cascade rules, tool ownership)
**Authority:** This is the single source of truth for how entities are documented, tracked, and queried across the Sharkitect Digital workspace ecosystem.

---

## Purpose

Every workspace must document the same way, using the same statuses, the same fields, and the same locations. This SOP defines:
1. **What** entities exist and their allowed statuses
2. **Where** each entity is stored (Supabase table + local file)
3. **How** to create, update, and transition entities
4. **How** to query entities for accurate, consistent data

If it's not in this document, it's not a standard.

---

## 1. Entity Types

### 1.1 Projects

A project is a named initiative with defined scope, phases, and deliverables.

**Source of truth:** Supabase `projects` table
**Local reference:** MEMORY.md resume instructions (pointer only — Supabase is authoritative)

**Allowed statuses:**

| Status | Meaning | When to use | Visible in CEO briefs? |
|--------|---------|-------------|----------------------|
| `active` | Work is happening or ready to happen | Project has started and is being worked on | YES |
| `pending` | Defined but not started | Project is planned but no work has begun | YES |
| `paused` | Temporarily stopped, will resume | Intentional hold — resource constraint, waiting on decision | YES (flagged) |
| `blocked` | Cannot proceed, external dependency | Waiting on client, third party, or another project | YES (flagged) |
| `tabled` | Consciously shelved, review later | Not a priority now; has a `review_date` for re-evaluation | NO |
| `complete` | All work finished and verified | All tasks completed, deliverables accepted | NO (moves to completed section) |

**Required fields on creation:**

| Field | Required? | Notes |
|-------|-----------|-------|
| `name` | YES | Short, descriptive name |
| `status` | YES | Must be one of the 6 values above |
| `phase` | YES | Current phase description |
| `priority` | YES | `critical`, `high`, `medium`, or `low` |
| `workspace` | YES | Owning workspace (`workforce-hq`, `skill-management-hub`, `sentinel`) |
| `notes` | Recommended | Context for current state |

**Transition rules:**
- `active` → `paused`: Auto-cascades all non-completed tasks to `low` priority. Project remains visible in CEO briefs (collapsed).
- `active` → `tabled`: Auto-cascades all non-completed tasks to `tabled` status + `priority=low` + sets `review_date` (default 30 days). Project and tasks become INVISIBLE in CEO briefs until `review_date` arrives.
- `active` → `complete`: Only when ALL tasks are `completed` (auto-triggered by last task completion)
- `blocked` → `active`: When blocker clears (check via `check-blockers`)
- `tabled` → `active`: When `review_date` arrives and decision is made to resume. Reactivated tasks return to their original priority (or `medium` if unknown).
- `paused` → `active`: When ready to resume. Tasks remain at `low` priority until explicitly re-prioritized.

**Paused vs Tabled (critical distinction):**
| | Paused | Tabled |
|---|--------|--------|
| **Intent** | Coming back soon | Consciously shelved |
| **CEO brief visibility** | YES (flagged, collapsed) | NO (invisible until review date) |
| **Task cascade** | Priority drops to `low` | Status set to `tabled` + priority `low` + `review_date` |
| **Resurface trigger** | Manual reactivation | Morning brief surfaces ONE TIME when `review_date` arrives |

**How to update:**
```bash
python ~/.claude/scripts/update-project-status.py project "<name>" <status> --phase "<phase>" --notes "<notes>"
```

**How to query:**
```bash
# All active projects
python ~/.claude/scripts/update-project-status.py list-projects --status active

# Full project table with task rollups
python ~/.claude/scripts/update-project-status.py table "<project-name>"

# Supabase direct query (for scripts/reports)
GET /rest/v1/projects?status=eq.active&order=priority.desc
```

---

### 1.1.1 Project Hierarchy (LIVE 2026-05-12)

Projects may be linked into a tree via `parent_project_id` (FK to `projects.id`). The `project_type` enum identifies the role each row plays in the tree.

**`project_type` enum values:**

| Value | Role | Example |
|-------|------|---------|
| `initiative` | Top-level multi-project effort spanning workspaces or quarters | "Foundation Reset" |
| `project` | Standalone work stream (default when no hierarchy needed) | "Sync skills .bat mirroring" |
| `phase_subproject` | Phase or sub-project belonging to a parent initiative | "Foundation Reset Phase 8 & 9 Amendment" |

**Schema fields (Supabase `projects` table):**

| Field | Purpose |
|-------|---------|
| `parent_project_id` | FK to parent's `projects.id`. NULL for top-level rows. |
| `project_type` | `initiative \| project \| phase_subproject` (enum) |
| `phase_number` | Integer position within parent (1, 2, 3, ...) when `project_type = phase_subproject` |
| `rollup_descendants` | Boolean; when true, recompute trigger walks descendant tree when rolling up counts |

**Triggers (LIVE):**
- Cycle prevention: insert/update of `parent_project_id` is rejected if it would create a cycle
- Recompute extended: `total_tasks` / `completed_tasks` rollup walks `rollup_descendants=true` subtrees when applicable

**Naming convention (positional-prefix STAYS):**

Sub-project names KEEP their positional prefix even after the hierarchy link is in place. The prefix is human shorthand for tree position; the FK is the authoritative link. Examples:

- `Sub-project A: <descriptive name>`
- `Sub-project B: <descriptive name>`
- `Sub-project B.1: <descriptive name>` (nested under B)
- `Sub-project B.2: <descriptive name>`

Rule of thumb: when filing a new sub-project, decide the position in the tree first, encode it in the name prefix, then set `parent_project_id` + `project_type=phase_subproject` + `phase_number`.

**"Working on this now" indicator (computed, no new status enum):**

The dashboard renders a "working now" visual on any project that has at least one task in `status = in_progress`, rolling up through `rollup_descendants=true` parents. This is a UI computation, not a stored status — `status` stays in its existing enum.

**Source:** Sentinel proposal `docs/audits/initiative-hierarchy-proposal-2026-05-12.md` + Sentinel commits `8c7840e + 7186072 + fc14044`. Deployed 2026-05-12 under one-time Chris exception (per `wr-sentinel-2026-05-12-003`). Default ownership protocol still applies: Skill Hub owns Skill-Hub-tagged project rows going forward.

---

### 1.2 Tasks

A task is a discrete unit of work within a project.

**Source of truth:** Supabase `tasks` table
**Local reference:** Plan documents (for detailed sub-task breakdowns)

**Allowed statuses:**

| Status | Meaning | When to use | Visible in CEO briefs? |
|--------|---------|-------------|----------------------|
| `pending` | Not started | Task is defined but no work has begun | YES |
| `in_progress` | Actively being worked on | Someone is currently working on this | YES |
| `completed` | Done and verified | Work finished, outputs verified | NO (moves to completed count) |
| `blocked` | Cannot proceed | Waiting on dependency, another task, or external input | YES (flagged) |
| `deferred` | Pushed to later, not abandoned | Intentionally delayed — lower priority or dependency not ready | YES (low priority) |
| `tabled` | Shelved with review date | Part of a tabled project, or individually shelved | NO |

**Required fields on creation:**

| Field | Required? | Notes |
|-------|-----------|-------|
| `task` | YES | Clear, actionable description |
| `project` | YES | Parent project name (must match `projects.name`) |
| `status` | YES | Must be one of the 6 values above |
| `priority` | YES | `critical`, `high`, `medium`, or `low` |
| `assigned_workspace` | YES | Which workspace is responsible for completing this |

**Transition rules:**
- `pending` → `in_progress`: When work actually begins
- `in_progress` → `completed`: When work is done AND verified. Sets `completed_at` timestamp.
- `completed` (last task) → Auto-completes parent project
- `blocked` → `pending` or `in_progress`: When blocker clears
- Any → `tabled`: Sets `review_date`, inherits from project tabling or individual decision

**Parent-child cascades (triggered by PROJECT status changes):**

Tasks do not exist in isolation -- they inherit state from their parent project. These cascades are automatic (handled by `update-project-status.py`):

| Project changes to | Effect on non-completed tasks | Reversible? |
|--------------------|-----------------------------|-------------|
| `paused` | Priority drops to `low`. Status unchanged. | YES -- when project reactivates, tasks keep `low` until manually re-prioritized |
| `tabled` | Status set to `tabled` + priority set to `low` + `review_date` applied. Tasks become invisible in CEO briefs. | YES -- when project reactivates, tasks return to `pending` |
| `complete` | N/A -- project only completes when ALL tasks are already `completed` | N/A |

**Why this matters:** Without cascades, paused/tabled projects leave behind `critical` tasks that clutter CEO briefs with false urgency. The cascade ensures the task list reflects the project's actual state.

**How to update:**
```bash
# Update task status
python ~/.claude/scripts/update-project-status.py task "<task-text>" <status> --project "<project>"

# Create new task
python ~/.claude/scripts/update-project-status.py add-task "<task-text>" --project "<project>" --workspace "<ws>" --priority <p>

# Add dependency
python ~/.claude/scripts/update-project-status.py add-dependency "<task-text>" --depends-on "<blocker-task-text>"

# Check if your blockers cleared
python ~/.claude/scripts/update-project-status.py check-blockers --workspace "<workspace>"

# See your workspace's tasks
python ~/.claude/scripts/update-project-status.py my-tasks --workspace "<workspace>"
```

**How to query:**
```bash
# All pending tasks for a project
GET /rest/v1/tasks?project=eq.Foundation Reset&status=eq.pending&order=priority.desc

# All tasks assigned to a workspace
GET /rest/v1/tasks?assigned_workspace=eq.sentinel&status=not.in.(completed,tabled)

# Carried days (how long a task has been open)
GET /rest/v1/tasks?status=eq.pending&order=carried_days.desc
```

---

### 1.3 Plans

A plan is a phased implementation document for a multi-step initiative.

**Source of truth:** `~/.claude/docs/plans-registry.md` (global registry) + individual plan files
**Future source of truth:** Supabase `documents` table (Phase 6/7)

**Allowed statuses:**

| Status | Meaning |
|--------|---------|
| `IN PROGRESS` | Actively being executed |
| `COMPLETE` | All phases done, outcomes documented |
| `ABANDONED` | Stopped, not coming back — document why |
| `SUPERSEDED` | Replaced by a newer plan — link to replacement |
| `TABLED` | Shelved for later — document reason and re-examine trigger |

**Required metadata in plan file header:**

| Field | Required? | Example |
|-------|-----------|---------|
| `Created` | YES | `2026-04-15` |
| `Updated` | YES | `2026-04-15` |
| `Owner` | YES | `Sentinel` |
| `Status` | YES | One of the 5 values above |

**Required metadata in plans-registry.md row:**

| Column | Required? |
|--------|-----------|
| Plan name | YES |
| Path | YES |
| Status | YES |
| Phase | YES (current phase or "All N phases") |
| Workspaces | YES |
| Started | YES |
| Notes | YES |

**Protocol:**
1. On creation → Add row to `~/.claude/docs/plans-registry.md` Active Plans immediately
2. On phase completion → Update Status and Phase columns in registry
3. On completion → Move row to Completed Plans, fill Outcome and Lessons columns
4. On abandonment → Move to Completed Plans with ABANDONED, document why in Lessons
5. On tabling → Update status to TABLED with reason in Notes

**How to query:**
```bash
# Read the registry directly
cat ~/.claude/docs/plans-registry.md

# Find a plan by keyword
grep -i "foundation" ~/.claude/docs/plans-registry.md
```

---

### 1.4 System Health (Heartbeats)

A heartbeat is a timestamped signal that an automated system is running.

**Source of truth:** Supabase `system_health` table

**Allowed statuses:**

| Status | Meaning | Threshold |
|--------|---------|-----------|
| `healthy` | System ran successfully within expected cadence | Last heartbeat within expected interval |
| `degraded` | System ran but with issues | Partial success or non-critical errors |
| `stale` | System hasn't reported in longer than expected | Heartbeat older than 2x expected cadence |
| `failed` | System explicitly reported failure | Exit code non-zero or error state written |

**Required fields:**

| Field | Required? |
|-------|-----------|
| `component` | YES — unique system identifier (e.g., `nightly-dream`, `sentinel-evening`) |
| `status` | YES — one of the 4 values above |
| `last_heartbeat` | YES — ISO timestamp of last successful run |
| `workspace` | YES — owning workspace |

**How to update:**
```bash
# Sentinel only (health-monitor.py lives in Sentinel's tools/)
python tools/health-monitor.py heartbeat <component-name>

# Other workspaces: use supabase-sync.py (available in all workspaces)
python tools/supabase-sync.py write-activity "system_run" "<component> healthy"
```

**How to query:**
```bash
# Sentinel only (health-monitor.py)
python tools/health-monitor.py list
python tools/health-monitor.py check --alert

# Any workspace: Supabase direct query
GET /rest/v1/system_health?status=neq.healthy
```

---

### 1.5 Activity Stream

An activity event is a timestamped log of something that happened.

**Source of truth:** Supabase `activity_stream` table

**Required fields:**

| Field | Required? | Notes |
|-------|-----------|-------|
| `event_type` | YES | What happened: `session_start`, `session_end`, `task_completed`, `system_run`, `error`, `correction`, `voice_sample` |
| `content` | YES | Human-readable description |
| `workspace` | YES | Where it happened |
| `platform` | YES | `claude-code`, `n8n`, `task-scheduler`, `croncreate` |
| `actor` | Recommended | Who/what did it: `claude-code`, `n8n-workflow`, `scheduled-runner` |

**How to write:**
```bash
# Available in ALL workspaces (each has its own tools/supabase-sync.py)
python tools/supabase-sync.py write-activity "<event_type>" "<content>"
```

**How to query:**
```bash
# Last 24h activity
GET /rest/v1/activity_stream?order=timestamp.desc&limit=50

# Activity for a specific workspace
GET /rest/v1/activity_stream?workspace=eq.sentinel&order=timestamp.desc

# Activity by event type
GET /rest/v1/activity_stream?event_type=eq.error&order=timestamp.desc
```

---

### 1.6 Lessons Learned

A lesson is an actionable insight derived from experience.

**Source of truth:** `~/.claude/lessons-learned.md` (current) → Supabase `lessons_learned` table (after Phase 6/7)
**Note:** Supabase table exists but is empty (0 rows). Population planned for post-Foundation Reset.

**Allowed statuses (once in Supabase):**

| Status | Meaning |
|--------|---------|
| `active` | Current and applicable |
| `obsolete` | No longer valid — superseded or system changed |

**Required fields in markdown:**

| Field | Required? | Format |
|-------|-----------|--------|
| Title | YES | `### [YYYY-MM-DD] category: descriptive title` |
| Context | YES | `**Context:**` block |
| Apply when / Rule / Decision | YES | When/how to use this lesson |
| Tags | YES | `**Tags:**` comma-separated |

**Allowed categories (entry prefix):**

| Category prefix | Section | What it covers |
|----------------|---------|---------------|
| `api-limitation:` | API Limitations | Tool/API operations that don't work + workarounds |
| `tool-usage:` | Tool Usage | Quirks, timeouts, non-obvious behaviors |
| `platform:` | Platform | OS-level issues (encoding, paths, shell) |
| `approach:` | Approach | "We tried X, Y works better" |
| `preference:` | Preferences | User communication/workflow/output preferences |
| `process:` | Process Decisions | Validated workflow choices |
| `direction:` | Architecture Direction | Standing principles for all builds |

**How to write:** Append to `~/.claude/lessons-learned.md` under the correct `##` section.

**How to query (current):**
```bash
# Search by keyword
grep -i "airtable" ~/.claude/lessons-learned.md

# Search by tag
grep "airtable" ~/.claude/lessons-learned.md
```

**How to query (after Phase 6/7 Supabase population):**
```sql
SELECT * FROM lessons_learned WHERE tags @> ARRAY['airtable'] AND status = 'active';
SELECT * FROM lessons_learned WHERE category = 'preference' AND status = 'active';
```

---

### 1.7 Documents (Doc Lifecycle)

A tracked document with freshness monitoring and review scheduling.

**Source of truth:** Supabase `doc_lifecycle` table (94 rows, active tracking)
**Future expansion:** Supabase `documents` table (Phase 6/7 — richer metadata, cross-references)

**Allowed escalation states:**

| State | Meaning |
|-------|---------|
| `current` | Document is within its review cycle, no action needed |
| `due` | Review date has arrived, needs review |
| `overdue` | Past review date, not yet reviewed |
| `deferred` | Review intentionally postponed |

**Required fields:**

| Field | Required? |
|-------|-----------|
| `workspace` | YES |
| `doc_path` | YES |
| `doc_type` | YES |
| `category` | YES |
| `review_cycle_days` | YES |
| `is_active` | YES |

**How to query:**
```bash
# Sentinel only (freshness-auditor.py lives in Sentinel's tools/)
python tools/freshness-auditor.py check

# Any workspace: Supabase direct query
GET /rest/v1/doc_lifecycle?next_review=lt.2026-04-15&is_active=eq.true&escalation_state=neq.deferred
```

---

### 1.8 Work Requests

A cross-workspace request for work to be done.

**Source of truth:** File-based inbox system (`.work-requests/inbox/`, `processed/`, `outbox/`)
**Supabase reference:** `work_requests` table (1 row — under review for Phase 6/7)

**Allowed types:**

| Type | Meaning |
|------|---------|
| `MISSING` | Nothing exists for this need |
| `UNUSED` | Exists but wasn't invoked |
| `FALLBACK` | Used generic instead of specialized |
| `BUG` | Existing artifact needs fixing |
| `ENHANCE` | Existing system needs improvement |
| `TASK` | Operational work for another workspace |

**Allowed severities:** `info`, `warning`, `error`, `critical`

**How to create:**
```bash
python ~/.claude/scripts/work-request.py \
  --type MISSING --severity warning \
  --workspace "source workspace" --workspace-path "$(pwd)" \
  --task "what you were doing" --category operations \
  --needed "what capability was needed" \
  --gap "what's missing or broken" \
  --impact "how this affected the work" \
  --fix-type hook --fix-desc "recommended fix" \
  --fix-components "component1, component2"
```

---

### 1.9 Routed Tasks

A task routed from one workspace to another.

**Source of truth:** File-based (`.routed-tasks/inbox/`, `processed/`, `outbox/`)

**Required JSON fields:** See `universal-protocols.md` Cross-Workspace Routed Tasks Protocol.

**Allowed priorities:** `low`, `medium`, `high`, `critical`

**Protocol:** Source writes JSON to target's `inbox/`. Target processes and moves to `processed/` with `resolution` object appended.

---

### 1.10 Memories (Supabase Brain)

A contextual fact stored in the Supabase brain.

**Source of truth:** Supabase `memories` table (705 rows)
**Local working copy:** Workspace MEMORY.md files

**Required fields:**

| Field | Required? |
|-------|-----------|
| `key` | YES — unique identifier within workspace |
| `category` | YES — `fact`, `preference`, `decision`, `pattern`, `correction` |
| `content` | YES — the memory content |
| `workspace` | YES |
| `confidence` | YES — `confirmed`, `inferred`, `provisional` |
| `active` | YES — boolean |

**How to write:**
```bash
# Available in ALL workspaces (each has its own tools/supabase-sync.py)
python tools/supabase-sync.py write-memory "<key>" "<category>" "<content>"
```

**How to query:**
```bash
# Sentinel only (ops-brain.py lives in Sentinel's tools/)
python tools/ops-brain.py summary

# Any workspace: Supabase direct query
GET /rest/v1/memories?workspace=eq.sentinel&active=eq.true&category=eq.decision
```

---

### 1.11 Skill Reference Companions (Alt 5 Pointer-Only Class, 2026-05-15)

A skill reference companion is a POINTER document that lives alongside a skill and cites authoritative K1 SoT content rather than duplicating it.

**Source of truth:** Filesystem only — NOT mirrored to Supabase
**Path pattern:** `~/.claude/skills/**/references/*.md`

**Allowed statuses:**

| Status | Meaning |
|--------|---------|
| `active` | Current and valid pointer document — citations resolve to live K1 SoT paths |
| `superseded` | A newer companion has replaced this one — follow `superseded_by` pointer |
| `archived` | No longer in use; K1 SoT itself has been deprecated or removed |

**Required frontmatter fields (per `skill-ref-companion` class in `~/.claude/config/frontmatter-schemas.json`):**

| Field | Required? | Notes |
|-------|-----------|-------|
| `status` | YES | One of the 3 values above |
| `last_rebuilt` | YES | ISO date when the companion was last regenerated from K1 SoT |
| `reason` | YES | Why this companion was (re)built — e.g., "Alt 5 Phase 1 initial build" |
| `superseded_by` | Conditional | Required when `status: superseded` — path to the replacing companion |
| `superseded_date` | Conditional | Required when `status: superseded` — ISO date |
| `superseded_reason` | Conditional | Required when `status: superseded` — one-line rationale |

**Pointer-only constraint (NON-NEGOTIABLE):**
Skill reference companions MUST be POINTER documents — headers, bullets, and citations to K1 SoT paths with version pins. They MUST NOT encode canonical prose that duplicates K1 SoT content. `skill-judge` refuses certification of PROSE-class companions. Validator: `~/.claude/scripts/skill_judge_pointer_validator.py` (H4 hybrid: line-class ratio + citation density + AI-judge escalation).

**How to create:**
1. Use `skill-judge` to generate the companion from the skill's existing reference material
2. Companion must cite K1 SoT paths with explicit version pins (e.g., `pricing-structure.md v3.2`)
3. Set frontmatter `status: active`, `last_rebuilt: YYYY-MM-DD`, `reason: "<context>"`
4. Companion is NOT registered in Supabase — filesystem only

**How to rebuild (when K1 SoT version bumps):**
1. Re-run `skill_judge_pointer_validator.py` against the existing companion
2. If citations are stale (referenced doc version has bumped): rebuild pointer citations
3. Update `last_rebuilt` and `reason` in frontmatter
4. Previous companion is automatically superseded — update `status: superseded` on old file if preserved

**Cross-references:** See `~/.claude/rules/universal-protocols.md` sections **Supersession-Pointer Pattern** and **SoT-Reference Discipline**.

---

## 2. Universal Documentation Rules

These rules apply to ALL entities, ALL workspaces, ALL the time.

### 2.1 Metadata is NON-NEGOTIABLE

Every document, plan, spec, and SOP must have:
- **Created date** — when it was first written
- **Updated date** — when it was last modified (update this on every edit)
- **Owner** — which workspace or person owns it

No exceptions. If a document lacks metadata, add it before making any other changes.

### 2.2 Supabase is the Source of Truth

For any entity that has a Supabase table:
1. **Update Supabase FIRST** — before updating local files
2. **Local files are working copies** — they can lag, Supabase cannot
3. **If Supabase and local disagree** — Supabase wins
4. **Queries for reports/briefs** — always query Supabase, never parse local files

### 2.3 Status Updates are Immediate

When a status changes (task completed, project paused, plan tabled):
1. Update Supabase within the same action — not at session end
2. Update all other tracking surfaces (plan doc, registry, MEMORY.md)
3. Verify the update landed (`my-tasks`, `list-projects`, or direct query)

### 2.4 Canonical Workspace Names

Always use these exact strings. No abbreviations, no variations.

| Canonical Name | Never Use |
|---------------|-----------|
| `workforce-hq` | `hq`, `HQ`, `workforce`, `Workforce HQ` |
| `skill-management-hub` | `skill-hub`, `Skill Hub`, `SMH`, `skills` |
| `sentinel` | `Sentinel`, `monitor`, `watchdog` |

**Exception:** Human-readable text (reports, MEMORY.md prose) can use display names. But Supabase fields, JSON files, and script arguments must use canonical names.

### 2.5 Priority Levels

Four levels. Use consistently across all entities.

| Priority | When to use |
|----------|-------------|
| `critical` | Blocks revenue, affects clients, or causes data loss |
| `high` | Important for operations, should be done this week |
| `medium` | Valuable but not urgent, can wait for next sprint |
| `low` | Nice to have, do when time permits |

---

## 3. Where Things Live (Quick Reference)

| What | Supabase Table | Local File/Dir | Script | Available In |
|------|---------------|----------------|--------|-------------|
| Projects | `projects` | MEMORY.md (pointer) | `~/.claude/scripts/update-project-status.py project` | ALL (global script) |
| Tasks | `tasks` | Plan documents | `~/.claude/scripts/update-project-status.py task` | ALL (global script) |
| Plans | -- (future: `documents`) | `~/.claude/plans/` + `plans-registry.md` | Manual | ALL |
| System health | `system_health` | `.tmp/health-state.json` | `tools/health-monitor.py` | Sentinel only |
| Activity log | `activity_stream` | -- | `tools/supabase-sync.py write-activity` | ALL (workspace-local copies) |
| Lessons learned | `lessons_learned` (empty) | `~/.claude/lessons-learned.md` | Manual (future: `lessons-learned-sync.py`) | ALL |
| Doc lifecycle | `doc_lifecycle` | -- | `tools/freshness-auditor.py`, `tools/dispatch-lifecycle-reviews.py` | Sentinel only |
| Memories | `memories` | Workspace MEMORY.md | `tools/supabase-sync.py write-memory` | ALL (workspace-local copies) |
| Work requests | -- (file-based) | `.work-requests/inbox/` | `~/.claude/scripts/work-request.py` | ALL (global script) |
| Routed tasks | -- (file-based) | `.routed-tasks/inbox/` | Manual JSON | ALL |
| Dream logs | `dream_log` | `.tmp/dream-report.json` | `tools/dream-consolidation.py` | Sentinel only |
| Skill reference companions | -- (filesystem only) | `~/.claude/skills/**/references/*.md` | `~/.claude/scripts/skill_judge_pointer_validator.py` | Skill Hub (build/validate) |

### Tool Availability Key

| Scope | Meaning | Path Pattern |
|-------|---------|-------------|
| **Global script** | Available from any workspace, single copy | `~/.claude/scripts/<name>.py` |
| **Workspace-local** | Each workspace has its own copy | `tools/<name>.py` (relative to workspace root) |
| **Sentinel only** | Only exists in Sentinel's `tools/` | Run from Sentinel workspace, or query Supabase directly from other workspaces |

**Rule:** If you need data from a Sentinel-only tool but you're in a different workspace, use the Supabase direct query (`GET /rest/v1/...`) instead. Never reference another workspace's `tools/` path.

---

## 4. Common Query Patterns

### "What's active right now?"
```bash
python ~/.claude/scripts/update-project-status.py list-projects --status active
python ~/.claude/scripts/update-project-status.py my-tasks --workspace sentinel
```

### "What's blocked and why?"
```bash
python ~/.claude/scripts/update-project-status.py check-blockers --workspace sentinel
```
```sql
SELECT task, project, notes FROM tasks WHERE status = 'blocked';
```

### "Is everything running?"
```bash
python tools/health-monitor.py check --alert
```
```sql
SELECT component, status, last_heartbeat FROM system_health WHERE status != 'healthy';
```

### "What happened today?"
```sql
SELECT event_type, content, workspace FROM activity_stream
WHERE timestamp > now() - interval '24 hours'
ORDER BY timestamp DESC;
```

### "What do we know about [topic]?"
```bash
grep -i "airtable" ~/.claude/lessons-learned.md
```
```sql
-- After Phase 6/7 population:
SELECT title, lesson FROM lessons_learned WHERE tags @> ARRAY['airtable'] AND status = 'active';
```

### "What documents need review?"
```bash
python tools/freshness-auditor.py check
```
```sql
SELECT workspace, doc_path, next_review FROM doc_lifecycle
WHERE next_review < now() AND is_active = true AND escalation_state != 'deferred'
ORDER BY next_review;
```

### "What tasks are carrying too long?"
```sql
SELECT task, project, carried_days, priority FROM tasks
WHERE status IN ('pending', 'in_progress') AND carried_days > 7
ORDER BY carried_days DESC;
```

---

## 5. Workspace Responsibilities

| Workspace | Documents | Queries | Audits |
|-----------|-----------|---------|--------|
| **Workforce HQ** | Projects, tasks, client deliverables, proposals | Active projects, blocked tasks, CEO brief data | Own workspace docs only |
| **Skill Hub** | Skills, agents, plugins, work requests, gap reports | Gap pipeline, skill inventory, sync status | Own workspace docs only |
| **Sentinel** | System specs, audit reports, health data | System health, activity stream, cross-workspace status | ALL workspaces + Supabase + infrastructure |

---

## 6. Enforcement

Sentinel audits compliance with these standards as part of its permanent watchdog role:
- **Session start:** Startup guard validates heartbeats and workspace naming
- **Dream cycle:** Duplicate/contradiction detection on memories
- **Morning/evening reports:** Surface stale heartbeats, blocked tasks, overdue reviews
- **Phase 8 (Foundation Reset):** Full cross-workspace state reconciliation

Violations found during audits are reported via work requests to the owning workspace.

---

## 7. Recent Protocol Additions

### Pointer-Only Constraint (Alt 5, 2026-05-15)

Skill reference companions under `~/.claude/skills/**/references/*.md` must be POINTER documents — headers, bullets, citations to K1 SoT paths with version pins. They MUST NOT encode canonical prose that duplicates K1 SoT content. See `~/.claude/rules/universal-protocols.md` sections **Supersession-Pointer Pattern** and **SoT-Reference Discipline** for the full protocol. Validator: `~/.claude/scripts/skill_judge_pointer_validator.py` (H4 hybrid: line-class ratio + citation density + AI-judge escalation). `skill-judge` refuses certification of PROSE-class companions.

The `skill-ref-companion` file class is catalogued in Section 1.11 above and in `~/.claude/config/frontmatter-schemas.json`. Required fields: `status` (active | superseded | archived), `last_rebuilt` (ISO date), `reason` (rebuild context). Companion files are filesystem-only — no Supabase row. The universal-protocols.md sections are the authoritative protocol surface and ARE synced to the toolkit repo; this documentation-standards.md file is a supporting catalog reference.
