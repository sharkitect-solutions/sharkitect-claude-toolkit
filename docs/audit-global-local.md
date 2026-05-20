# Global Local Filesystem Audit — `~/.claude/`

> **Audit Date:** 2026-04-09
> **Auditor:** Skill Management Hub (on behalf of all workspaces)
> **Purpose:** Phase 1 audit of globally shared filesystem for Foundation Reset. Complements workspace-specific audit-*.md reports.
> **Governance model:** This filesystem is SHARED INFRASTRUCTURE — no single workspace owns it. Access patterns noted per item.

---

## 1. IDENTITY

- **Name:** Global Claude Code Configuration (`~/.claude/`)
- **Purpose:** Shared infrastructure layer for all Sharkitect Digital workspaces. Contains rules, hooks, scripts, skills, agents, plans, docs, project memory, plugins, lessons learned, and session config.
- **Governance:** Not owned by any workspace. All workspaces read from it; specific workspaces write to specific subdirectories. No formal governance model exists — this is a gap.
- **Drift assessment:** MODERATE DRIFT. Core infrastructure (rules, hooks, scripts) is clean and current. Project memory directories contain orphaned entries from dissolved workspaces. Plans directory has significant accumulated clutter. Lessons-learned.md is well-maintained but large (500 lines).

---

## 2. FILE INVENTORY

### 2.1 Rules (`rules/`) — 3 files

| File | Status | Reads | Writes | Notes |
|------|--------|-------|--------|-------|
| `api-limitations.md` | ACTIVE | All workspaces | Skill Hub (when new limitations found) | Clean. 3 Airtable limitations documented. |
| `context7.md` | ACTIVE | All workspaces | Skill Hub | Clean. 4-step Context7 MCP protocol. |
| `universal-protocols.md` | ACTIVE | All workspaces | Skill Hub | Clean. 236 lines. Single source of truth. Recently updated (2026-04-09). |

**Verdict:** Rules directory is CLEAN. No stale references, no contradictions. Governance is clear.

### 2.2 Scripts (`scripts/`) — 2 files

| File | Status | Used By | Notes |
|------|--------|---------|-------|
| `gap-reporter.py` | ACTIVE | All workspaces | 203 lines. Reports gaps to Skill Hub inbox. Stdlib only. Clean. |
| `doc-cache-builder.py` | ACTIVE | All workspaces | 238 lines. Builds drift-detection cache. Stdlib only. Clean. |

**Verdict:** Scripts directory is CLEAN. Both scripts are well-documented, stdlib-only, actively used.

### 2.3 Hooks (`hooks/`) — 14 files (12 Python + 1 .bat + 1 .vbs)

**Python hooks (12) — registered in settings.json:**

| Hook | Event | Matcher | Status | Lines |
|------|-------|---------|--------|-------|
| `check-line-count.py` | PreToolUse | Edit\|Write | ACTIVE | 146 |
| `content-enforcer-hook.py` | PreToolUse | Edit\|Write | ACTIVE | 172 |
| `drift-detection-hook.py` | PreToolUse | Edit\|Write | ACTIVE | 273 |
| `pre-modify-checkpoint.py` | PreToolUse | Edit\|Write | ACTIVE | 120 |
| `mcp-limitation-guard.py` | PreToolUse | mcp__\|Bash | ACTIVE | 233 |
| `checkpoint-reminder.py` | PostToolUse | Edit\|Write | ACTIVE | 79 |
| `quality-gate-hook.py` | PostToolUse | Edit\|Write | ACTIVE | 111 |
| `resource-audit-hook.py` | PostToolUse | Edit\|Write | ACTIVE | 113 |
| `error-tracker-hook.py` | PostToolUse | Bash\|mcp__ | ACTIVE | 365 |
| `session-startup-guard.py` | SessionStart | startup\|resume | ACTIVE | 299 |
| `session-start-lifecycle.py` | SessionStart | startup\|resume | ACTIVE | 302 |

**Total hook registrations in settings.json:** 5 matchers across 3 events, 11 hook commands.

**Non-hook files in hooks directory:**

| File | Status | Purpose | Notes |
|------|--------|---------|-------|
| `daily-freshness-check.bat` | ACTIVE | Task Scheduler support | Calls Sentinel tools. Correct paths. |
| `daily-freshness-check.vbs` | ACTIVE | Silent runner for .bat | Wraps .bat without console window. |
| `__pycache__/` | IGNORABLE | Python cache | Auto-generated, harmless. |

**DISCREPANCY FOUND:** MEMORY.md in Skill Hub claims these additional hooks: `aios-core` (SessionStart, SessionEnd, PreCompact), `phase-gate` (PreCompact), `superpowers` (SessionStart). These are **plugin-provided hooks**, not files in the hooks/ directory. The MEMORY.md listing conflates plugin hooks with custom hooks. Not technically wrong, but misleading — Phase 2 should clarify the distinction.

**Stale reference scan:** ZERO stale references to RemoteTrigger, ralph-loop-as-scheduler, Autonomous Operations, or old agent names in any hook file.

**Verdict:** Hooks directory is CLEAN. All registered, all active, no stale references.

### 2.4 Plans (`plans/`) — 48 files

**This is the most cluttered directory in the global filesystem.**

| Category | Count | Files |
|----------|-------|-------|
| COMPLETED plans | ~25 | bright-launching-pine, cozy-munching-hopper, elegant-giggling-church, federated-bubbling-hedgehog, floating-wondering-sutton, fluttering-wondering-globe, gentle-imagining-dusk, hazy-wishing-marble, iridescent-orbiting-goblet, keen-sprouting-pascal, lexical-leaping-hare, linear-yawning-papert, optimized-toasting-pancake, quizzical-jumping-bubble, refactored-giggling-pnueli, resilient-toasting-honey, shimmying-popping-petal, shiny-kindling-rossum, ticklish-tumbling-hare, virtual-strolling-sky, woolly-splashing-brooks, zazzy-swinging-dusk, zippy-herding-micali, federated-tinkering-hickey |
| ACTIVE plans | 2 | **wise-sprouting-canyon** (Foundation Reset), **wise-cuddling-plum** (Unified Brain) |
| Agent sub-plans | 12 | `*-agent-a*.md` files — worktree artifacts from parallel agent dispatches |
| Research/reference | 4 | adaptive-greeting-gray (video analysis), telegram-bot-architecture-research-synthesis, piped-meandering-swan (vision doc), snuggly-baking-meerkat (master plan - superseded) |
| Client project plans | 5 | iterative-spinning-forest (FF), lively-scribbling-flurry (FF), serene-coalescing-kitten (FF), tingly-booping-gadget (FF RLR), temporal-wibbling-moth (briefing) |

**ISSUES:**
1. **25+ completed plans never archived.** The Pivot Cleanup Protocol says to delete superseded artifacts, but plans accumulate indefinitely.
2. **12 agent sub-plan files** (`*-agent-a*.md`) are worktree artifacts that should have been cleaned up after agent tasks completed.
3. **No plan lifecycle management.** No "completed" folder, no archival process, no cleanup trigger.
4. **snuggly-baking-meerkat.md** (2026-03-19) is the old "Master Plan (Clean Slate)" that was superseded by wise-sprouting-canyon.md. Still present.

**Recommended action for Phase 3:**
- Archive completed plans to `plans/archive/` or delete with git history as backup
- Delete all `*-agent-a*.md` sub-plan files (these are ephemeral worktree artifacts)
- Establish plan lifecycle: Active -> Completed -> Archived (or deleted)

### 2.5 Docs (`docs/`) — 6 files

| File | Status | Purpose | Access Pattern |
|------|--------|---------|---------------|
| `audit-hq.md` | ACTIVE | Phase 1A HQ report | Sentinel reads for Phase 2 |
| `audit-infrastructure.md` | ACTIVE | Phase 1C-1E report | Sentinel reads for Phase 2 |
| `audit-sentinel.md` | ACTIVE | Phase 1A Sentinel report | Sentinel reads for Phase 2 |
| `audit-skill-hub.md` | ACTIVE | Phase 1A Skill Hub report | Sentinel reads for Phase 2 |
| `audit-supabase.md` | ACTIVE | Phase 1B report | Sentinel reads for Phase 2 |
| `autonomous-systems-inventory.md` | ACTIVE | Ownership map | All workspaces read. Updated 2026-04-09. |

**Verdict:** Docs directory is CLEAN. All files current and purposeful.

### 2.6 Agents (`agents/`) — 52 files

52 agent `.md` files. All custom-built agents for the superpowers ecosystem. Count matches MEMORY.md claim (52).

**Access pattern:** All workspaces read (agents are loaded by Claude Code globally). Skill Hub writes (creates/optimizes agents).

**Spot-check:** No stale references to old agent persona names found in hook scan. Full agent-by-agent audit was done during Phase 8 optimization cycle (38/38 success documented in MEMORY.md).

**Verdict:** CLEAN. Previously audited and optimized.

### 2.7 Skills (`skills/`) — 143 directories

143 skill directories. Count matches MEMORY.md claim (143).

**Access pattern:** All workspaces read. Skill Hub writes.

**Verdict:** CLEAN. Previously audited and optimized through Phase 8 cycles. Full re-audit not needed for Foundation Reset — the skills themselves are the product, not infrastructure.

### 2.8 Plugins (`plugins/`)

| Item | Status | Notes |
|------|--------|-------|
| `installed_plugins.json` | ACTIVE | 2 custom plugins tracked |
| `installed_plugins.json.bak` | ORPHANED | Backup file, can be deleted |
| `marketplaces/` (5 dirs) | ACTIVE | 5 marketplace sources configured |
| `blocklist.json` | ACTIVE | Plugin blocklist |
| `known_marketplaces.json` | ACTIVE | Marketplace registry |
| `cache/` | IGNORABLE | Auto-managed cache |
| `install-counts-cache.json` | IGNORABLE | Auto-managed |

**Verdict:** Mostly clean. `installed_plugins.json.bak` is orphaned.

---

## 3. PROJECT MEMORY FILES (`projects/*/memory/`)

### 3.1 Active Workspace Memories

| Workspace | Dir Name | MEMORY.md Lines | Topic Files | Status |
|-----------|----------|-----------------|-------------|--------|
| **HQ** | `c--...1---SHARKITECT-DIGITAL-WORKFORCE-HQ` | 127 | 40 | ACTIVE, within 200-line limit |
| **Skill Hub** | `c--...3---Skill-Management-Hub` | 109 | 20 | ACTIVE, within 200-line limit |
| **Sentinel** | `c--...4---Sentinel` | 6 | 6 | ACTIVE, very lean (index-only MEMORY.md) |

**Cross-workspace contradictions found:**
- None between the 3 active workspaces. Scheduling architecture is consistently described across all three.

### 3.2 Orphaned/Inactive Workspace Memories

| Project Dir | MEMORY.md Lines | Topic Files | Status | Action |
|-------------|-----------------|-------------|--------|--------|
| `c--...2---Master-AIOS-Builder` | NO MEMORY DIR | 3 session UUIDs only | ORPHANED | **Delete** — workspace 2 is inactive, no memory files, just session artifacts |
| `c--...0---Other-Workspaces-NODE---n8n-Workflow-Architect-Agent` | NO MEMORY DIR | 2 session UUIDs + JSONLs | ORPHANED | **Delete** — old path variant, no memory |
| `c--...NODE---n8n-Workflow-Architect-Agent` | 56 lines | 0 topic files | STALE | **Contains dissolved agent persona references** (Orion, Vantage, Echo, Atlas, Sage). 16-agent model was eliminated. Delete or archive. |
| `c--...SCOUT---Lead-Gen-Agent` | 94 lines | 7 topic files | STALE/DORMANT | Contains complete project state for SCOUT lead gen agent. Project appears dormant — last activity unknown. **Governance decision needed:** Is SCOUT still a project? If no, archive. If yes, it needs a workspace assignment. |

**CRITICAL FINDING — NODE memory:**
NODE's MEMORY.md (line 6-7) says: *"Reports to Orion (CTO). Receives blueprints from Vantage (Solutions Architect) and Echo (Reverse Engineer). Coordinates with Atlas (COO) for delivery, Sage (CKO) for knowledge governance."*

This is the old 16-agent persona model that was dissolved months ago. Any session opening the NODE workspace would inherit completely stale identity and reporting structure. **Must be cleaned up or deleted.**

**CRITICAL FINDING — Two NODE directories:**
Two separate project dirs exist for what appears to be the same workspace:
1. `c--...0---Other-Workspaces-NODE---...` (old path, session artifacts only)
2. `c--...NODE---n8n-Workflow-Architect-Agent` (has actual memory)

The first is an orphan from a path change. Delete.

---

## 4. LESSONS LEARNED (`lessons-learned.md`)

| Metric | Value |
|--------|-------|
| Line count | 500 |
| Categories | 7 (API Limitations, Tool Usage, Platform, Approach, Preferences, Process Decisions, Architecture Direction) |
| Entries | ~30+ |
| Stale entries | 2 (see below) |

**Stale/outdated entries:**
1. **Line 306-308** — Process decision references "trigger file pattern" for ralph-loop brief generation. This pattern was superseded by n8n cloud. The lesson itself is still valid (pattern concept) but the specific use case is obsolete.
2. **Line 363** — Architecture direction title says "3-tier architecture with Autonomous Operations workspace" even though the entry body correctly notes the workspace was dissolved. Title is misleading.

**Contradictory entries:** NONE found. Entries correctly use `[CORRECTED]` and `[CORRECTED AGAIN]` markers when updating prior entries.

**Access pattern:** All workspaces read at session start (per universal-protocols.md). All workspaces append at session end (via session-checkpoint skill).

**Governance concern:** At 500 lines and growing, this file is getting large. No pruning mechanism exists. Old entries never get removed. The file will eventually become unwieldy for session-start reads.

**Verdict:** MOSTLY CLEAN. Two minor stale entries. Growing size is a future concern. The planned Supabase `lessons_learned` table (Phase 4B) would solve the size problem by making entries queryable instead of requiring full-file reads.

---

## 5. SETTINGS AND CONFIG

### 5.1 `settings.json` — ACTIVE
- 47 enabled plugins
- 11 hook commands across 5 matchers
- `autoUpdatesChannel: "latest"`, `effortLevel: "medium"`
- **No stale entries found**
- **ralph-loop plugin still enabled** — this is fine (it's a valid task iteration tool), but worth noting given past confusion about its purpose

### 5.2 `config/` — 1 file
- `skill-hub-path.txt` — Used by gap-reporter.py to find Skill Hub inbox. ACTIVE.

### 5.3 `mcp.json` — ACTIVE
- MCP server configuration. Not audited in detail (would need separate MCP audit).

### 5.4 Backup files
- `settings.json.bak` — Recent backup. Keep.
- `settings.json.bak.20260328` — Old dated backup. Can delete.

### 5.5 Other root files
- `.credentials.json` — Claude auth. ACTIVE.
- `history.jsonl` — Session history. ACTIVE, auto-managed.
- `mcp-needs-auth-cache.json` — MCP auth state. ACTIVE.
- `policy-limits.json` — Policy config. ACTIVE.
- `stats-cache.json` — Stats. Auto-managed.

---

## 6. OTHER DIRECTORIES

| Directory | Purpose | Status | Notes |
|-----------|---------|--------|-------|
| `.tmp/` | Temporary files | ACTIVE | Auto-managed |
| `backups/` | Unknown | UNKNOWN | Not inspected in detail |
| `builder/` | Contains `.claude/` and `.git/` subdirs | UNKNOWN | Appears to be a nested project. Needs investigation. |
| `cache/` | Claude cache | ACTIVE | Auto-managed |
| `debug/` | Debug artifacts | ACTIVE | Auto-managed |
| `downloads/` | Downloaded files | UNKNOWN | Not inspected |
| `file-history/` | File change history | ACTIVE | ~40+ UUID dirs. Auto-managed by Claude Code. |
| `ide/` | IDE integration | ACTIVE | Auto-managed |
| `session-env/` | Session environment | ACTIVE | Auto-managed |
| `sessions/` | Session data | ACTIVE | Auto-managed |
| `shell-snapshots/` | Shell state snapshots | ACTIVE | Auto-managed |
| `statsig/` | Feature flags | ACTIVE | Auto-managed |
| `telemetry/` | Telemetry data | ACTIVE | Auto-managed |
| `todos/` | Todo persistence | ACTIVE | Auto-managed |

**Flag:** `builder/` directory contains a `.claude/` and `.git/` subdirectory, suggesting it's an embedded project. This needs investigation — it may be an orphaned project or a tool installation artifact.

---

## 7. CROSS-WORKSPACE AWARENESS

### How global files mediate between workspaces

| Global File | Mediation Role |
|-------------|---------------|
| `rules/universal-protocols.md` | Enforces consistent behavior across all workspaces |
| `scripts/gap-reporter.py` | Routes gap reports from any workspace to Skill Hub |
| `scripts/doc-cache-builder.py` | Enables drift detection in any workspace |
| `hooks/session-startup-guard.py` | Ensures consistent session start across all workspaces |
| `hooks/session-start-lifecycle.py` | Checks doc review schedules across all workspaces |
| `docs/autonomous-systems-inventory.md` | Single source of truth for who owns what |
| `lessons-learned.md` | Cross-pollination of learnings between workspaces |

### Governance gap
No formal ownership/stewardship model exists for global files. Currently:
- **Skill Hub** is the de facto writer (creates/updates rules, skills, agents, hooks)
- **Sentinel** is the de facto auditor (monitors health, detects drift)
- **All workspaces** are readers

**Recommendation for Phase 4:** Formalize this as a co-stewardship model:
- **Skill Hub** = Write steward (builds and deploys global artifacts)
- **Sentinel** = Audit steward (monitors freshness, detects contradictions, reports issues)
- **All workspaces** = Read access + append to lessons-learned.md
- **No workspace "owns" it** — it's shared infrastructure with defined roles

---

## 8. GAPS AND CONTRADICTIONS

### Critical Issues

1. **NODE memory contains dissolved agent personas (Orion, Atlas, Sage, Vantage, Echo)** — Any session opening NODE workspace inherits completely wrong identity and organizational structure. Risk: if someone opens that workspace, they'll behave as the old 16-agent model.

2. **Two NODE project directories exist** — Path duplication creates confusion about which is authoritative.

3. **SCOUT project memory is rich but has no workspace assignment** — 94-line MEMORY.md + 7 topic files describe a complete lead-gen project. Not clear if this project is active, dormant, or abandoned. No workspace in the current 3-workspace model owns it.

### High Issues

4. **48 plans with no lifecycle management** — Plans accumulate indefinitely. ~25 are completed, ~12 are agent sub-plans (ephemeral artifacts). No archive, no cleanup trigger, no supersession tracking within the plans directory itself.

5. **MEMORY.md hook listing conflates plugin hooks with custom hooks** — Skill Hub MEMORY.md lists `aios-core`, `phase-gate`, `superpowers` as if they're files in hooks/. They're plugin-provided. Not wrong but misleading for auditors.

6. **No formal governance model for global filesystem** — De facto patterns exist (Skill Hub writes, Sentinel audits) but nothing is documented as a policy. Any workspace could write to any global file without coordination.

### Medium Issues

7. **lessons-learned.md at 500 lines and growing** — No pruning mechanism. Will become unwieldy. Supabase migration (Phase 4B) is the planned solution.

8. **AIOS Builder project dir has no memory, just session UUIDs** — Dead directory from inactive workspace. Should be cleaned up.

9. **settings.json.bak.20260328** — Stale backup from 12 days ago. Trivial cleanup.

10. **`builder/` directory at ~/.claude/builder/** — Contains .claude/ and .git/ subdirs. Unclear purpose. Needs investigation.

### Low Issues

11. **installed_plugins.json.bak** — Orphaned backup file in plugins/.

12. **Two stale entries in lessons-learned.md** — Title mismatch on line 363 (references dissolved workspace in title). Trigger file pattern on line 306-308 references obsolete use case.

---

## 9. SUMMARY FOR PHASE 2 (SYNTHESIS)

### What's Clean
- Rules (3 files) — all current, no conflicts
- Scripts (2 files) — all working, well-documented
- Hooks (12 Python files) — all registered, no stale refs
- Docs (6 files) — all current and purposeful
- Agents (52 files) — previously audited and optimized
- Skills (143 dirs) — previously audited and optimized
- Active workspace memories (HQ, Skill Hub, Sentinel) — no cross-contradictions
- Config files — minimal and correct

### What Needs Cleaning (Phase 3 targets)
- Plans directory: archive/delete ~37 completed + agent sub-plan files
- NODE project memory: delete or archive (stale agent personas)
- Duplicate NODE project dir: delete
- AIOS Builder project dir: delete
- Stale backup files: delete

### What Needs Governance Decisions (Phase 4 targets)
- SCOUT project: active or dormant? Workspace assignment?
- Global filesystem stewardship model: formalize Skill Hub = writer, Sentinel = auditor
- Plan lifecycle process: how do plans move from active -> completed -> archived?
- lessons-learned.md growth: pruning policy or wait for Supabase migration?
- `builder/` directory: what is it and should it stay?