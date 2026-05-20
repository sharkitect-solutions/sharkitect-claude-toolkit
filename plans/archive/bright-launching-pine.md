# Plan: Complete Project Sanitization + Gear-Shift Cleanup Protocol

## Context

The Telegram bot was UPGRADED from Airtable-based memory to Supabase-backed semantic search (Sessions 35-39), but old artifacts were never cleaned up at the time of the pivot. Chris's directive: "Make it so the old Telegram bot never existed" — remove ALL stale files, dead code, old references, and cached artifacts across the ENTIRE project. Document what didn't work as a lesson learned. Then create a standard protocol so this cleanup happens automatically on every future gear-shift.

**Root cause of this issue:** When we pivoted from the old approach to the new one, we didn't immediately sanitize. We built forward without cleaning backward. This plan fixes that AND prevents it from recurring.

---

## Part A: Complete Artifact Cleanup (21 actions)

### Step 1: Delete Old Files (3 files)

| # | File | Why it's old |
|---|------|-------------|
| 1 | `tools/alex-telegram-bot/tools/airtable_tool.py` | Old Airtable query tool. Only consumer was `config["airtable_api_key"]`. Replaced by Supabase. |
| 2 | `tools/alex-telegram-bot/tests/test_airtable.py` | Tests for the deleted Airtable tool. No other references. |
| 3 | `tools/alex-telegram-bot/data/memory_backup.json` | Stale pre-Supabase backup from 2026-03-12. Supabase is now the backup. |

### Step 2: Delete ALL __pycache__ Directories (6 directories, 42 .pyc files)

Every `__pycache__` in the project — they auto-regenerate on next import. Several contain stale bytecode for deleted modules (`memory_sync.cpython-312.pyc`, `airtable_tool.cpython-312.pyc`).

| # | Directory | Notable stale content |
|---|-----------|----------------------|
| 4 | `tools/__pycache__/` | — |
| 5 | `tools/audit/__pycache__/` | — |
| 6 | `tools/alex-telegram-bot/__pycache__/` | `memory_sync.cpython-312.pyc` (deleted module) |
| 7 | `tools/alex-telegram-bot/prompts/__pycache__/` | — |
| 8 | `tools/alex-telegram-bot/tests/__pycache__/` | `test_airtable.cpython-312-pytest-9.0.2.pyc` |
| 9 | `tools/alex-telegram-bot/tools/__pycache__/` | `airtable_tool.cpython-312.pyc` (being deleted) |

### Step 3: Clear Stale Data (2 files — structures stay, content reset)

| # | File | Action | Reason |
|---|------|--------|--------|
| 10 | `tools/alex-telegram-bot/data/queue.json` | Replace with `[]` | 13 error entries from March 14-16 (old bot httpx errors). Queue system is ACTIVE (`bridge.py` uses it) — file stays, stale entries go. |
| 11 | `tools/alex-telegram-bot/logs/alex-bot.log` | Clear to empty | 3.2MB / 18,154 lines of mixed old+new entries. Contains 12K+ lines from old `memory_sync` process. New bot writes fresh entries on startup. |

### Step 4: Remove Dead Code References (5 code edits)

| # | File | Line(s) | What to change |
|---|------|---------|----------------|
| 12 | `tools/alex-telegram-bot/bot.py` | 215 | **Remove** `import tools.airtable_tool` (dead import; triggers auto-registration of deleted tool) |
| 13 | `tools/alex-telegram-bot/tools/__init__.py` | 62-87 | **Remove** entire `query_airtable` tool definition from `TOOL_DEFINITIONS` list (25 lines including trailing comma) |
| 14 | `tools/alex-telegram-bot/config.py` | 71-75 | **Remove** `airtable_api_key` config block (4 lines + comment). Only consumer was `airtable_tool.py` which is being deleted. |
| 15 | `tools/alex-telegram-bot/memory.py` | 8 | **Update** `"Airtable sync: memory_sync.py handles bidirectional Airtable persistence"` → `"Supabase sync: supabase_sync.py handles bidirectional Supabase persistence"` |
| 16 | `tools/alex-telegram-bot/prompts/alex_system.py` | 81-82, 102, 115, 174, 181 | **Update** 5 Airtable references in system prompt (details below) |

**alex_system.py edits (Step 16 detail):**
- **Lines 81-82**: Replace `### Data (Airtable)` section → `### Data (Supabase)` with updated description: "Shared brain — memories, KB documents, session logs via semantic search."
- **Line 102**: Update "Information Retrieval" authority → replace "Airtable" with "Supabase"
- **Line 115**: Remove "or Airtable" from confirmation rules (no Airtable to modify)
- **Line 174**: Remove entire Airtable row from tool routing table
- **Line 181**: Remove "Airtable is NOT a Google service" from CRITICAL note

### Step 5: Update Documentation (1 doc edit)

| # | File | Line | What to change |
|---|------|------|----------------|
| 17 | `knowledge-base/projects/operational-foundation/plan.md` | 369 | **Update** `Delete or rename existing SharkitectDailyAudit` → `SharkitectDailyAudit deleted — replaced by SharkitectMorningBrief + SharkitectEveningBrief + SharkitectWeeklyAudit + SharkitectSupabaseSync (completed 2026-03-15)` |

### Step 6: Document Lessons Learned (MEMORY.md)

Add to Process Improvement Table:

| Date | Issue | Root Cause | Fix | Status |
|------|-------|------------|-----|--------|
| 2026-03-17 | Old Telegram bot artifacts (files, imports, config, system prompt, cache) remained in project 2+ weeks after pivoting to Supabase approach | No cleanup protocol existed. Built forward without cleaning backward. Stale `airtable_tool.py`, `memory_backup.json`, 6 `__pycache__` dirs, dead imports, old system prompt references, 3.2MB stale log entries all persisted. | GEAR-SHIFT CLEANUP PROTOCOL codified (see Part B). 21 cleanup actions executed. Standard now: when an approach is abandoned, immediate cleanup before new build begins. | CODIFIED |

Also add to Key Decisions:

| Date | Decision | Reasoning |
|------|----------|-----------|
| 2026-03-17 | Airtable-based memory was a good prototype but doesn't scale | Keyword-only retrieval, ~41 entries, single-agent (Alex-only), no cross-platform visibility. Replaced by Supabase pgvector: 246+ records, 16-agent shared brain, semantic search, interaction logging. File-based + Airtable = prototype pattern. Shared database + vector embeddings = production pattern. |

---

## Part B: Gear-Shift Cleanup Protocol (NEW — Permanent Rule)

Chris's directive: This must be standard practice across the board. When something doesn't work and we shift gears, the cleanup happens IMMEDIATELY — not weeks later.

### New Rule: GEAR-SHIFT CLEANUP PROTOCOL

**Trigger:** Any time an approach, tool, integration, or system is being replaced or abandoned.

**Before starting the new build, execute these steps IN ORDER:**

1. **DOCUMENT** — What didn't work and why. Add to Process Improvement Table in MEMORY.md. This is the ONLY thing that survives from the old approach.

2. **INVENTORY** — List every file, config entry, import, tool definition, system prompt reference, test, cache directory, and documentation reference related to the old approach. Be exhaustive. Check:
   - Source files (`.py`, `.js`, `.bat`)
   - Config entries (`.env` refs, `config.py`)
   - Imports in other files that reference the old modules
   - Tool definitions / API schemas
   - System prompts that mention the old tool/approach
   - Tests that test the old functionality
   - Cache directories (`__pycache__/`, `.pyc` files)
   - Data files (`.json`, `.log`, backups)
   - Documentation (`MEMORY.md`, plan files, KB docs, agent KBs)
   - Scheduled tasks / automation that references old code

3. **CLASSIFY** — For each item: DELETE (stale), KEEP (still needed by new approach), or UPDATE (reference needs changing).

4. **EXECUTE** — Delete stale files, clear stale data, remove dead imports, update references. All in one pass.

5. **VERIFY** — Restart affected systems. Confirm clean operation. No import errors, no stale references, no orphaned config.

6. **UPDATE MEMORY** — Record what was cleaned, what was kept, and why. Update all affected MEMORY.md files.

**This protocol is NON-NEGOTIABLE.** It runs every time we pivot. The new build does not start until the old approach is fully sanitized.

Add to Active Rules in MEMORY.md:
`GEAR-SHIFT CLEANUP PROTOCOL (Chris-directed, 2026-03-17): When ANY approach/tool/system is being replaced or abandoned, IMMEDIATELY (before starting the new build): (1) Document what didn't work and why in Process Improvement Table. (2) Inventory EVERY file, import, config, prompt, test, cache, and doc reference to the old approach — check the ENTIRE project, not just the obvious folder. (3) Classify each as DELETE/KEEP/UPDATE. (4) Execute all cleanup in one pass. (5) Verify clean operation. (6) Update MEMORY.md. The new build does NOT start until the old approach is fully sanitized. No exceptions.`

---

## Part C: Systems Verification

After all cleanup is done:

1. **Kill running bot process** → restart with `python main.py` → confirm clean startup (no import errors)
2. **Verify no stale processes** — `tasklist /FI "IMAGENAME eq python.exe" /V`
3. **Verify scheduled tasks** — confirm only 4 current tasks exist (Morning, Evening, Sync, Weekly)
4. **Confirm Supabase sync** — bot should log "Synced X memories from Supabase" on startup
5. **Verify tool list** — bot should register all current tools WITHOUT `query_airtable`

---

## Complete Action Summary (21 items)

| # | Action | File/Target |
|---|--------|-------------|
| 1 | DELETE | `tools/alex-telegram-bot/tools/airtable_tool.py` |
| 2 | DELETE | `tools/alex-telegram-bot/tests/test_airtable.py` |
| 3 | DELETE | `tools/alex-telegram-bot/data/memory_backup.json` |
| 4 | DELETE | `tools/__pycache__/` (entire dir) |
| 5 | DELETE | `tools/audit/__pycache__/` (entire dir) |
| 6 | DELETE | `tools/alex-telegram-bot/__pycache__/` (entire dir) |
| 7 | DELETE | `tools/alex-telegram-bot/prompts/__pycache__/` (entire dir) |
| 8 | DELETE | `tools/alex-telegram-bot/tests/__pycache__/` (entire dir) |
| 9 | DELETE | `tools/alex-telegram-bot/tools/__pycache__/` (entire dir) |
| 10 | CLEAR | `tools/alex-telegram-bot/data/queue.json` → `[]` |
| 11 | CLEAR | `tools/alex-telegram-bot/logs/alex-bot.log` → empty |
| 12 | EDIT | `bot.py` line 215 — remove airtable import |
| 13 | EDIT | `tools/__init__.py` lines 62-87 — remove query_airtable definition |
| 14 | EDIT | `config.py` lines 71-75 — remove airtable_api_key block |
| 15 | EDIT | `memory.py` line 8 — update comment (Airtable → Supabase) |
| 16 | EDIT | `alex_system.py` — 5 Airtable references → Supabase (lines 81-82, 102, 115, 174, 181) |
| 17 | EDIT | `operational-foundation/plan.md` line 369 — update SharkitectDailyAudit reference |
| 18 | ADD | MEMORY.md Process Improvement Table — cleanup lesson |
| 19 | ADD | MEMORY.md Key Decisions — Airtable→Supabase reasoning |
| 20 | ADD | MEMORY.md Active Rules — GEAR-SHIFT CLEANUP PROTOCOL |
| 21 | VERIFY | Restart bot, check processes, confirm clean operation |
