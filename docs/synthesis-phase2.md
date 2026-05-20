# Phase 2 Synthesis Report -- Foundation Reset

**Date:** 2026-04-09
**Author:** Sentinel
**Inputs:** audit-sentinel.md, audit-supabase.md, audit-infrastructure.md, audit-skill-hub.md, audit-hq.md, audit-global-local.md, autonomous-systems-inventory.md
**Plan reference:** `~/.claude/plans/wise-sprouting-canyon.md`

---

## 1. Conflict Map

Where workspaces disagree about ownership, naming, or system state.

### 1.1 Workspace Naming -- Three Layers of Inconsistency

| Layer | Problem | Examples |
|-------|---------|---------|
| **Script-to-script** | Sentinel's own scripts use two different names for the same workspace | `gap-inbox-monitor.py` uses `skill-hub`; `dispatch-lifecycle-reviews.py` uses `skill-management-hub` |
| **Gap reports** | `gap-reporter.py` accepts freeform workspace names | Files contain "SKILL MANAGEMENT HUB", "Skill Management Hub", "SHARKITECT DIGITAL WORKFORCE HQ" -- none match the canonical kebab-case |
| **Supabase records** | 10 records use non-canonical workspace names | `hq` (2), `HQ` (1), `autonomous-operations` (4), `ops-center` (2), `remote-trigger` (1) |

**Canonical names (to enforce everywhere):** `workforce-hq`, `skill-management-hub`, `sentinel`, `global`

### 1.2 Workspace Count Disagreement

| Source | Workspaces Listed | Problem |
|--------|-------------------|---------|
| `universal-protocols.md` | 3 (HQ, Skill Hub, Sentinel) | Authoritative |
| `dispatch-lifecycle-reviews.py` | 4 (adds master-aios-builder) | Dead workspace included |
| `gap-inbox-monitor.py` | 3 (uses `skill-hub` not `skill-management-hub`) | Name mismatch |
| HQ cross-workspace awareness | HQ, Skill Hub, Sentinel | Doesn't know workspace 3's number |
| Skill Hub cross-workspace awareness | HQ, Skill Hub, Sentinel | Doesn't reference workspace 2 |

**Root cause:** Workspace 2 ("Master AIOS Builder") was dissolved but references persist in `dispatch-lifecycle-reviews.py`, two SessionStart hooks, and one orphaned project memory directory.

### 1.3 System State Conflicts

| Claim | Source | Reality | Severity |
|-------|--------|---------|----------|
| HQ has 6 active + 9 disabled Task Scheduler tasks | HQ MEMORY.md | Only 3 active tasks exist. Trigger tasks deleted. SupabaseSync never existed. | CRITICAL |
| `ralph-scheduler.py` is part of active briefing system | HQ MEMORY.md | File was deleted | CRITICAL |
| Hooks `aios-core` and `phase-gate` are registered | Skill Hub MEMORY.md | These are plugin-provided hooks, not custom hooks in hooks/ | MEDIUM |
| CEO briefs "needs fixes" | Skill Hub MEMORY.md | HQ says "COMPLETE" | MEDIUM |
| CronCreate is "PRIMARY" for scheduling | All CLAUDE.md files | CronCreate is session-only. For 6 AM and 9 PM tasks, the "fallback" (Task Scheduler or n8n) is the only path that fires. | HIGH |
| FallbackBrief tasks are "no longer present" | autonomous-systems-inventory.md | Infrastructure audit found 3 active FallbackBrief tasks | MEDIUM |
| CLAUDE.md says "17 workflows (all active)" | HQ CLAUDE.md | Only 7 active in n8n; 4 relevant to current operations | HIGH |
| Watcher's Watcher deployment unknown | audit-sentinel.md | Infrastructure audit confirmed it IS deployed and running (ID: N84M4ormvCzjlzTT, last exec 4/9 2:00 PM) | RESOLVED |

### 1.4 Agent Identity Ghost References

The dissolved 16-agent model (Alex, Marcus, Sage, Atlas, Sterling, Vera, Cleo, Orion, Felix, Axiom, Lex, Node, Vantage, Echo, Quill, Scout) persists across the system:

| Location | Scope | Impact |
|----------|-------|--------|
| HQ: 4 workflow files | operating-rhythm, governance-enforcement, learning-synthesis, performance-governance | Any session reading these will try to coordinate non-existent agents |
| HQ: 6+ KB docs with agent frontmatter | `owner: marcus`, `owner: sage`, `owner: atlas, lex`, `owner: felix, atlas` | Meaningless metadata in single-agent model |
| HQ: `.tmp/workforce-workflow-ids.json` | Maps 16 agent names to n8n workflow IDs | Stale IDs, workflows may not exist |
| Sentinel: `n8n-brain-integration-guide.md` | 30+ "Alex" references, "Alex's Rules" section | Would mislead any future n8n workflow development |
| Sentinel: `watcher-workflow-spec.md:7` | "If Alex goes down" | Should say "If any n8n workflow goes down" |
| Supabase: `logs` table | 160 of 163 rows reference `marcus` (95) or `alex` (65) | Historical data, no active writes |
| Supabase: `sessions` table | Default `agent_id` = `alex` | Active schema issue |
| Supabase: `kb_docs` | References to "Sage (CKO)" | Stale agent persona in document content |
| Global: NODE project memory | References Orion, Vantage, Echo, Atlas, Sage | Would mislead any session opening that workspace |

---

## 2. Stale Document Registry

Every document flagged STALE or SUPERSEDED across all audits.

### DELETE (no ongoing value, information preserved in git history)

| Document | Workspace | Reason |
|----------|-----------|--------|
| `workflows/governance-enforcement.md` | HQ | Describes dead 16-agent enforcement model (owner: marcus) |
| `workflows/learning-synthesis.md` | HQ | Describes dead 16-agent learning model (owner: sage) |
| `workflows/performance-governance.md` | HQ | Describes dead 16-agent KPI hierarchy (owner: marcus) |
| `knowledge-base/projects/era-client-offering/` | HQ | Duplicate of `email-response-automation/` |
| `knowledge-base/projects/fix-era/` | HQ | Duplicate of `email-response-automation/` |
| `.tmp/workforce-workflow-ids.json` | HQ | 16 stale agent n8n workflow IDs |
| `tools/sync-agents.py` | Skill Hub | Superseded by `sync-skills.py` |
| `docs/plans/2026-03-09-system-health-audit-design.md` | Skill Hub | Pre-Sentinel, obsolete |
| `docs/plans/2026-03-09-system-health-audit.md` | Skill Hub | Pre-Sentinel, obsolete |
| `docs/reports/2026-03-09-system-health-report.md` | Skill Hub | One-time historical artifact |
| `plans/snuggly-baking-meerkat.md` | Global | Superseded by wise-sprouting-canyon.md |
| ~25 completed plan files in `plans/` | Global | Never referenced again. Git history preserves them. |
| ~12 agent sub-plan files (`*-agent-a*.md`) in `plans/` | Global | Ephemeral worktree artifacts, should have been cleaned up |
| NODE project memory (both dirs) | Global | Dissolved agent personas, completely stale |
| AIOS Builder project dir | Global | No memory files, just session UUIDs |
| `settings.json.bak.20260328` | Global | 12-day-old backup |
| `installed_plugins.json.bak` | Global | Orphaned backup |

### MARK SUPERSEDED (add banner, keep for reference)

| Document | Workspace | Superseded By | Action |
|----------|-----------|---------------|--------|
| `docs/superpowers/specs/2026-04-07-autonomous-operations-architecture-design.md` | Skill Hub | `autonomous-systems-inventory.md` + CLAUDE.md scheduling rules | Add "SUPERSEDED 2026-04-08" banner |
| `docs/superpowers/plans/2026-04-07-hq-audit-system-cleanup.md` | Skill Hub | Actual cleanup (executed), ralph-loop refs now wrong | Add "EXECUTED -- ralph-loop refs outdated" banner |
| `workflows/skill-sync.md` | Skill Hub | `tools/sync-skills.py` | Add "SUPERSEDED by tools/sync-skills.py" banner |

### REWRITE (still needed, content is wrong)

| Document | Workspace | Problem | Action |
|----------|-----------|---------|--------|
| `workflows/operating-rhythm.md` | HQ | Entire doc describes 16-agent orchestration | Rewrite for single-agent model with n8n + Task Scheduler |
| `knowledge-base/governance/workforce-governance-framework.md` | HQ | References "all 16 agents" (updated post-restructure but content wasn't changed) | Rewrite governance for single-agent model |
| `docs/n8n-brain-integration-guide.md` | Sentinel | 30+ Alex references, "Alex's Rules" | Strip Alex, replace with generic/current patterns |
| HQ MEMORY.md (Task Scheduler section) | HQ | Claims 6 active + 9 disabled tasks | Rewrite to match reality: 3 active fallback tasks |
| Skill Hub MEMORY.md (hooks section) | Skill Hub | Conflates plugin hooks with custom hooks | Clarify distinction |

### FIX (minor edits needed)

| Document | Workspace | Fix |
|----------|-----------|-----|
| `docs/watcher-workflow-spec.md:7` | Sentinel | Change "If Alex goes down" to "If any n8n workflow goes down" |
| `tools/dispatch-lifecycle-reviews.py:36` | Sentinel | Remove `master-aios-builder` entry |
| `lessons-learned.md:306-308` | Global | Note that trigger file pattern is obsolete |
| `lessons-learned.md:363` | Global | Fix title to remove dissolved workspace reference |
| 6 KB docs with agent `owner:` frontmatter | HQ | Remove or update frontmatter |
| `fallback-brief-sender.py:52` | HQ | Remove RemoteTrigger comment |
| `session-startup-guard.py` | Global | Remove master-aios-builder reference |
| `session-start-lifecycle.py` | Global | Remove master-aios-builder reference |

---

## 3. System Spec Gap List

Every autonomous system that lacks an authoritative specification document.

| System | Owner | Current Documentation | Spec Status |
|--------|-------|----------------------|-------------|
| Gap Pipeline Monitor | Sentinel | Code only + cron-schedule.md mention | **NO SPEC** |
| Health Check | Sentinel | Code only + cron-schedule.md mention | **NO SPEC** |
| Freshness Audit | Sentinel | Code only | **NO SPEC** |
| Lifecycle Dispatch | Sentinel | Code + Task Scheduler config | **NO SPEC** |
| Morning System Report | Sentinel | Code + Task Scheduler config | **NO SPEC** |
| Repo Monitor | Sentinel | Code + Task Scheduler config | **NO SPEC** |
| Feedback Rollup | Sentinel | Code only | **NO SPEC** |
| Lifecycle Inbox Polling | Sentinel | cron-schedule.md mention only | **NO SPEC** |
| Dream Consolidation | Sentinel | `dream-consolidation-prompt.md` (prompt only) | **PARTIAL** |
| Error Auto-Fix Bridge | HQ | MEMORY.md entry only | **NO SPEC** |
| Cloudflared Tunnel | HQ | MEMORY.md entry only | **NO SPEC** |
| Supabase Sync | All | Code is self-documenting but no spec | **NO SPEC** |
| Drift Detection Hook | All | CLAUDE.md universal protocols mention | **NO SPEC** |
| Gap Inbox Alert | Skill Hub | CLAUDE.md mention + code | **NO SPEC** |
| Session Startup Guard | Global | CLAUDE.md description + code | **NO SPEC** |
| Watcher's Watcher | Sentinel | `watcher-workflow-spec.md` | **HAS SPEC** (deployment now confirmed) |
| CEO Daily Briefs | HQ (n8n) | `ceo-brief-templates.md` + autonomous-systems-inventory | **HAS SPEC** |
| Internal Error Handler | HQ (n8n) | autonomous-systems-inventory description | **PARTIAL** |
| Gap Reporter Script | Global | Code + universal-protocols description | **NO SPEC** |

**Summary:** 15 of 19 autonomous systems have NO standalone spec. 2 have partial specs. Only 2 (Watcher's Watcher, CEO Daily Briefs) have proper spec docs.

**Impact:** Without specs, there is no definition of "correct behavior." Systems can silently drift, and verification is impossible.

**Recommendation:** Create a standardized system spec template. Priority order:
1. Systems with Task Scheduler fallbacks (Dream, Morning Report, Repo Monitor, Lifecycle Dispatch) -- these run unattended
2. Error Auto-Fix Bridge + Cloudflared Tunnel -- critical infrastructure, MEMORY.md can be pruned
3. Session-only systems (gap monitor, health check, freshness audit, etc.) -- lower priority since they only run during interactive sessions

---

## 4. Supabase Cleanup List

### Tables to Drop

| Table | Rows | Reason |
|-------|------|--------|
| `escalations` | 0 | Never populated. `work_requests` serves similar purpose. |
| `retained_files` | 0 | Workspace dissolution is complete. No ongoing purpose. |
| `feedback_metrics` | 0 | `feedback_tracker.py` exists but never wrote to this table. |

### Tables to Evaluate After First Run

| Table | Rows | Condition |
|-------|------|-----------|
| `repo_findings` | 0 | Evaluate after RepoMonitor first run (2026-04-12). Drop if unused after 2 runs. |

### Records to Fix (10 total)

| Table | Current Value | Correct Value | Count | Action |
|-------|---------------|---------------|-------|--------|
| `memories` | `hq` | `workforce-hq` | 2 | UPDATE |
| `activity_stream` | `HQ` | `workforce-hq` | 1 | UPDATE |
| `activity_stream` | `autonomous-operations` | Reassign to owning workspace | 4 | UPDATE (investigate which workspace performed the action) |
| `activity_stream` | `ops-center` | Investigate origin | 2 | UPDATE (unknown source -- may be stale) |
| `activity_stream` | `remote-trigger` | Remove or recategorize | 1 | UPDATE (not a workspace) |

### Schema Fixes

| Issue | Table | Fix | Priority |
|-------|-------|-----|----------|
| Default `agent_id` = `alex` | `sessions` | Change default to `claude-code` | HIGH |
| RLS `USING (true)` bypass | `error_fixes`, `escalations`, `projects`, `tasks` | Tighten if public access ever added (acceptable for now) | LOW |
| RLS initplan pattern | `doc_lifecycle` | Change to `(select auth.function())` pattern | MEDIUM |
| Vector extension in public schema | Global | Move to dedicated schema | LOW |
| 16 unused indexes | Multiple (mostly zero-row tables) | Drop with the tables or after table evaluation | LOW |
| Unindexed FK | `error_fixes.similar_fix_id` | Add index | LOW |

### Naming Standardization

Enforce canonical workspace names everywhere that writes to Supabase:
- `gap-reporter.py` -- normalize `--workspace` input to kebab-case
- `supabase-sync.py` -- already normalizes (good)
- `gap-inbox-alert.py` -- reads only (no write concern)
- All future scripts -- must use `workforce-hq`, `skill-management-hub`, `sentinel`, `global`

### Stale Agent Data

| Table | Agent | Records | Action |
|-------|-------|---------|--------|
| `logs` | `marcus` | 95 | Archive or leave (historical, no active writes) |
| `logs` | `alex` | 65 | Archive or leave (historical, no active writes) |
| `sessions` | `alex` | Default value | Fix default |
| `kb_docs` | `Sage (CKO)` | ~2 | Update document content |

### Missing Tables (Future -- Phase 4B)

Per the Supabase brain design spec, 5-6 new tables are needed for the queryable brain:
1. `document_relationships` -- cross-reference tracking
2. `lessons_learned` -- structured queryable lessons
3. `user_preferences` -- structured preferences and voice data
4. `system_specs` -- queryable system specification registry
5. `automation_registry` -- automation tracking
6. `sync_conflicts` -- conflict reconciliation

These are Phase 4B scope, not Phase 3 cleanup.

---

## 5. Infrastructure Cleanup List

### Task Scheduler -- DELETE

| Task Name | Reason |
|-----------|--------|
| `\Lead Gen - Daily Pipeline` | Points to dissolved workspace. Disabled, no files on disk. |
| `\SCOUTDailyPipeline` | Points to dissolved SCOUT workspace. Disabled, no files on disk. |
| `\SCOUTPipeline` | Duplicate of above. Disabled, no files on disk. |
| `\SCOUTWeekendSendOnly` | Points to dissolved SCOUT workspace. Disabled, no files on disk. |

### Task Scheduler -- FIX

| Task Name | Issue | Fix |
|-----------|-------|-----|
| `\SharkitectHQ\FallbackMorningBrief` | Exit code 0x80070002 (file not found at runtime) | Investigate: likely unquoted path or missing dependency. FallbackMidday succeeds. |
| `\SharkitectHQ\FallbackEveningBrief` | Same 0x80070002 error | Same fix as morning. |
| `\SharkitectHQ\FallbackMiddayBrief` | Action path uses `.tmp\..\tools\` detour | Rewrite to direct absolute path matching other two tasks. |

### Task Scheduler -- VERIFY

| Task Name | Condition |
|-----------|-----------|
| `\Sentinel\RepoMonitor` | Verify after first scheduled run (2026-04-12) |

### n8n -- CRITICAL (Security)

| Issue | Scope | Priority |
|-------|-------|----------|
| **63+ hardcoded credentials** across n8n workflows | Supabase service_role JWT (~50+), Telegram token (4), Slack token (6+), Anthropic key (1), webhook secret (1) | **CRITICAL -- SECURITY EMERGENCY** |
| **Action:** Migrate ALL credentials to n8n credential store, then rotate Supabase service_role key | Affects 20+ workflows | Immediate |

### n8n -- FIX

| Issue | Fix |
|-------|-----|
| Internal Error Handler bridge URL uses dead Cloudflare tunnel URL | Update to current tunnel URL |
| Speed-to-Lead Demo (active) has no error handler | Add error workflow reference |
| AIOS Error Handler (inactive) still referenced by 2 workflows | Delete or activate |
| 2 email workflows reference inactive AIOS Error Handler | Point to active Internal Error Handler |

### n8n -- ARCHIVE

| Category | Count | Action |
|----------|-------|--------|
| WORKFORCE Agent Fleet workflows | 16 | Archive (all inactive, from dissolved 16-agent model) |
| [ALEX] Sub-Agent Suite workflows | 9 | Archive |
| FF Testing/Archive copies | ~15 | Archive |
| Other inactive demos/tests | ~38 | Review individually, archive most |

**Total inactive workflows to archive:** ~78 of 85 total workflows

### Global Artifacts -- FIX

| Item | Location | Fix |
|------|----------|-----|
| `daily-freshness-check.bat` uses bare `python` | `~/.claude/hooks/` | Use full Python path per lessons-learned |
| `.bat` and `.vbs` files misplaced in hooks/ | `~/.claude/hooks/` | Move to Sentinel `tools/` |
| 2 hooks reference dissolved master-aios-builder | `session-startup-guard.py`, `session-start-lifecycle.py` | Remove stale workspace from detection logic |

### Global Artifacts -- CLEAN UP

| Item | Action |
|------|--------|
| ~37 completed + agent sub-plan files in `plans/` | Archive to `plans/archive/` or delete |
| NODE project memory (2 directories) | Delete both |
| AIOS Builder project directory | Delete |
| SCOUT project memory | Governance decision: active or dormant? If dormant, archive. |
| `builder/` directory at `~/.claude/builder/` | Investigate purpose; delete if orphaned |
| `installed_plugins.json.bak` | Delete |
| `settings.json.bak.20260328` | Delete |

### Sentinel-Specific Fixes

| Item | Fix |
|------|-----|
| `scheduled-runner.py` writes "healthy" heartbeat even when wrapped command fails | Add exit code check before writing heartbeat |
| `dispatch-lifecycle-reviews.py` references master-aios-builder | Remove entry |
| 4 CronCreate-only systems have no overnight coverage (freshness audit, lifecycle dispatch, feedback rollup, lifecycle polling) | Create Task Scheduler fallbacks or accept gap |
| Workspace naming: `skill-hub` vs `skill-management-hub` in scripts | Standardize to `skill-management-hub` everywhere |

---

## Priority Matrix for Phase 3

### Immediate (security / data integrity)

1. **Migrate 63+ hardcoded n8n credentials to credential store, then rotate Supabase service_role key**
2. Fix HQ MEMORY.md false claims (Task Scheduler, ralph-scheduler)
3. Fix Skill Hub MEMORY.md stale claims (hooks, brief status)

### High (system reliability)

4. Delete 4 orphaned Task Scheduler tasks
5. Fix 2 broken FallbackBrief Task Scheduler tasks
6. Fix `scheduled-runner.py` heartbeat-on-failure bug
7. Remove master-aios-builder references from scripts and hooks
8. Fix 10 non-canonical Supabase workspace name records
9. Update `sessions` table default agent_id

### Medium (documentation accuracy)

10. Rewrite HQ operating-rhythm.md for single-agent model
11. Strip Alex from Sentinel's n8n-brain-integration-guide.md
12. Mark 3 Skill Hub docs as SUPERSEDED
13. Delete 4+ stale HQ workflow/KB files
14. Fix Sentinel watcher-workflow-spec.md Alex reference
15. Normalize workspace naming in gap-reporter.py

### Low (cleanup / hygiene)

16. Archive ~37 completed plan files
17. Delete orphaned project memory directories (NODE x2, AIOS Builder)
18. Archive ~78 inactive n8n workflows
19. Drop 3 zero-row Supabase tables
20. Delete stale backup files
21. Move .bat/.vbs from hooks/ to Sentinel tools/
22. Fix lessons-learned.md stale entries

---

*Report generated: 2026-04-09 by Sentinel Phase 2 Synthesis*
*Input: 6 audit reports totaling ~1,800 lines of findings across all workspaces*
