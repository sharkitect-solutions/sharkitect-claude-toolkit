# Plugin Protection + Marketplace Evolution Monitor

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Prevent silent loss of custom local plugins from Claude Code cache rebuilds, and establish a periodic capability evolution system that discovers, evaluates, and integrates new marketplace offerings.

**Architecture:** Two independent systems: (1) A deterministic protection layer (SessionStart hook + sync-skills.py extension) that detects missing local plugins and auto-restores from the GitHub toolkit repo backup. (2) A periodic marketplace monitor (monthly CronCreate job + evaluation workflow) that scans known marketplaces, scores new/updated items against current capabilities, and produces an actionable upgrade report.

**Tech Stack:** Python stdlib only (matching all existing tools). Existing infrastructure: sync-skills.py, refresh-inventory.py, audit-plugins.py, manage-plugins.py, skills-evaluation.md.

---

## Context

On 2026-04-09, Claude Code's plugin auto-update rebuilt the `~/.claude/plugins/cache/` directory, re-fetching marketplace plugins from git but destroying the `cache/local/` subdirectory containing 4 custom plugins (aios-core, quality-gate, auto-sync, phase-gate). The `installed_plugins.json` registry still referenced them, but the files were gone. This caused silent failure of Supabase brain sync (SessionStart/End), PreCompact context preservation, and phase-gate enforcement -- with zero errors or warnings.

The root cause: local plugins have no remote git source to re-fetch during cache rebuilds. The only backup was the `sharkitect-claude-toolkit/custom-plugins/` directory, and no automated mechanism checked for or restored missing plugins.

Additionally, the current system has no process for monitoring marketplace evolution -- new skills, agents, and plugins appear in the 5 configured marketplaces (claude-plugins-official, claude-code-workflows, claude-code-plugins-plus, claude-code-workflows, agentic-forge) but are only discovered when manually searched. This means the toolkit falls behind as the ecosystem evolves.

---

## Part A: Plugin Protection (Prevent + Auto-Recover) -- COMPLETE (2026-04-10)

### Task 1: Extend sync-skills.py to sync custom plugins -- DONE

**Files:**
- Modify: `tools/sync-skills.py`

**What:** Add a `sync_plugins()` function that mirrors `cache/local/*` to `sharkitect-claude-toolkit/custom-plugins/` (same pattern as skills/agents/rules sync). This ensures every `--sync --push` also backs up custom plugins to the toolkit repo.

**Key details:**
- Source: `~/.claude/plugins/cache/local/`
- Destination: `sharkitect-claude-toolkit/custom-plugins/`
- Compare by file hash (same as existing skill sync)
- Report new/modified/deleted plugins in sync output
- Include in `--push` git commit

### Task 2: Build plugin-integrity-check.py -- DONE

**Files:**
- Create: `tools/plugin-integrity-check.py`

**What:** A standalone script that:
1. Reads `~/.claude/plugins/installed_plugins.json`
2. For each `@local` plugin, verifies `cache/local/<name>/` exists
3. If missing: auto-restores from `sharkitect-claude-toolkit/custom-plugins/<name>/`
4. If restore source also missing: prints CRITICAL warning
5. Verifies each restored plugin appears in `settings.json` `enabledPlugins`
6. Returns exit code 0 if all good, 1 if any were missing (even if restored)

**Output on stdout (for hooks to display):**
- If all present: silent (exit 0)
- If restored: `RESTORED: <plugin-name> from toolkit backup. Cache was cleared by platform update.`
- If unrecoverable: `CRITICAL: <plugin-name> missing from cache AND backup. Manual rebuild required.`

### Task 3: Integrate into session-startup-guard.py -- DONE

**Files:**
- Modify: `~/.claude/hooks/session-startup-guard.py`

**What:** Add a Step 0 (before heartbeat check) that runs `plugin-integrity-check.py`. If it returns exit code 1, include a warning in the startup status output. This catches missing plugins at the very start of every session, before any hooks that depend on them fire.

### Task 4: Add settings.json backup to sync-skills.py -- DONE

**Files:**
- Modify: `tools/sync-skills.py`

**What:** Copy `~/.claude/settings.json` to `sharkitect-claude-toolkit/settings-backup.json` during every `--sync`. This preserves the enabledPlugins list and hook registrations so they can be restored if settings.json gets corrupted or reset.

---

## Part B: Marketplace Evolution Monitor

### Task 5: Build marketplace-scanner.py

**Files:**
- Create: `tools/marketplace-scanner.py`

**What:** A script that:
1. Reads known marketplace repos from `~/.claude/plugins/known_marketplaces.json`
2. For each marketplace, lists all available plugins/skills (by reading the cache directory structure or querying the marketplace index)
3. Compares against current inventory (`.tmp/skills-manifest.json`)
4. Produces a delta report: NEW items (not installed), UPDATED items (version changed), REMOVED items (we have it but marketplace dropped it)
5. Output: `.tmp/marketplace-delta.json`

**Key details:**
- Stdlib only (use `subprocess` to run `git ls-remote` or read local cache dirs)
- Does NOT install anything -- read-only scan
- Includes item name, description (from plugin.json/SKILL.md frontmatter), and marketplace source

### Task 6: Build marketplace-evaluator workflow

**Files:**
- Create: `workflows/marketplace-evaluation.md`

**What:** An SOP that:
1. Reads `.tmp/marketplace-delta.json`
2. For each NEW or UPDATED item:
   - Score relevance to Sharkitect's capabilities (0-10) using project purpose + existing gaps
   - Check if it overlaps with or supersedes an existing custom skill/agent/plugin
   - Score quality (structural audit using audit-plugins.py or audit-skills.py patterns)
   - Classify: INSTALL (high value, no conflict), EVALUATE (potential value, needs deeper look), SKIP (low relevance), SUPERSEDES (replaces something we built)
3. For SUPERSEDES items: compare marketplace version vs our custom version -- which is better?
4. Output: `.tmp/marketplace-evaluation.json` with actionable recommendations
5. Notify user via session startup or Supabase activity_stream

### Task 7: Create monthly CronCreate job spec

**Files:**
- Modify: `workflows/cron-schedule.md`

**What:** Add a monthly marketplace scan to the cron schedule:
- Frequency: First session of each month (or CronCreate `0 0 1 * *`)
- Action: Run `python tools/marketplace-scanner.py` then display delta summary
- If delta has NEW items with relevance > 7: flag for evaluation in session startup
- This runs during active sessions only (CronCreate limitation) -- first session of the month triggers it

### Task 8: Extend refresh-inventory.py to track marketplace state

**Files:**
- Modify: `tools/refresh-inventory.py`

**What:** Add a `plugins` section to the skills-manifest.json output that includes:
- All installed plugins (marketplace + local) with version, source, enabled status
- Last marketplace scan date
- Count of pending evaluations
- This gives every workspace visibility into plugin health

---

## Dependency Order

```
Task 1 (sync plugins) -- no dependencies, extends existing tool
Task 2 (integrity check) -- no dependencies, new standalone tool
Task 3 (startup guard integration) -- depends on Task 2
Task 4 (settings backup) -- no dependencies, extends existing tool
Task 5 (marketplace scanner) -- no dependencies, new tool
Task 6 (evaluation workflow) -- depends on Task 5 output format
Task 7 (cron schedule) -- depends on Task 5
Task 8 (inventory extension) -- no dependencies, extends existing tool
```

Tasks 1, 2, 4, 5, 8 can run in parallel. Task 3 follows Task 2. Task 6 follows Task 5. Task 7 follows Task 5.

---

## Verification

1. **Plugin protection test:** Delete `~/.claude/plugins/cache/local/aios-core/`, run `python tools/plugin-integrity-check.py`. Should auto-restore and report.
2. **Sync test:** Run `python tools/sync-skills.py --sync`. Should show custom plugins in sync output.
3. **Startup guard test:** Start a new session. Startup guard should show plugin integrity check as Step 0.
4. **Marketplace scan test:** Run `python tools/marketplace-scanner.py`. Should produce `.tmp/marketplace-delta.json` with NEW items.
5. **Inventory test:** Run `python tools/refresh-inventory.py`. Manifest should include plugins section.
