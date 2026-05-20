# Briefing System — Full System Audit Before AIOS

## Context

Phase 5 of the Founder-Grade Briefing System Rebuild is COMPLETE. Before moving to AIOS Vision Definition (project #3), Chris wants a comprehensive audit of everything built across Phases 1-5 + 3.5. Test every component, document issues, fix them, document fixes, and update all memory/history/Supabase so AIOS starts fresh.

**System under test:** 6 pipeline modes (morning, midday, evening, weekly, sync, midnight), ~45 check functions, AI synthesis via Haiku, Telegram delivery, Supabase data layer, Google Calendar/Gmail via gws CLI, n8n health monitoring, bot CRUD tools, Windows Task Scheduler automation.

## User Preferences (confirmed)

- **Telegram:** SEND live test messages during Batch E (Chris will see them)
- **Test data cleanup:** Clean up ALL test rows (tasks, escalations) at the END, not as we go
- **Known issue #0:** `register_tasks.py` has morning at `06:00` — should be `05:00`. MEMORY.md is correct. Fix during Batch G.

---

## Pre-Identified Issues

### ISSUE-0: register_tasks.py schedule out of sync
- **SEVERITY:** HIGH
- **SYMPTOM:** `register_tasks.py` line 11 has `/st 06:00` but morning audit runs at 5:00 AM per Task Scheduler + MEMORY.md
- **ROOT CAUSE:** Schedule was changed in Task Scheduler but `register_tasks.py` was not updated simultaneously. Classic cross-reference gap.
- **FIX PLANNED:** Update register_tasks.py during Batch G + verify Task Scheduler matches + check if MiddayAudit task is missing from register_tasks.py
- **FILES TO CHECK:** `tools/register_tasks.py`, all `.bat` files, MEMORY.md

---

## Execution Plan: 9 Batches

| Batch | Scope | Safety | Est. |
|-------|-------|--------|------|
| **A** | Environment & Credentials (12 checks) | READ-ONLY | 5m |
| **B** | Individual Check Functions (~30 functions) | MOSTLY READ-ONLY (B4 writes test rows) | 10m |
| **C** | Pipeline Integration (7 full runs, --no-telegram) | WRITES to Supabase logs/audit_log | 15m |
| **D** | AI Synthesis (3 brief types + fallbacks) | API COST ~$0.05 | 5m |
| **E** | Delivery (message split + Telegram + alert) | E2/E3 SEND real Telegram messages | 3m |
| **F** | Bot Tools (task CRUD, project status, escalation) | F2/F4 WRITE test rows | 5m |
| **G** | Task Scheduler (batch files + registration + FIX ISSUE-0) | WRITES to register_tasks.py + re-registers | 5m |
| **H** | Cross-Pipeline Data Flow (full day simulation) | WRITES all pipeline side effects | 15m |
| **I** | Cross-Reference Consistency Hardening | WRITES new check function + updates weekly audit | 10m |

**Dependency chain:** A → B → C → H. D requires A4. E requires A7. F requires A3. G is independent. I runs after all issues found in A-H.

---

## BATCH A: Environment & Credentials

### A1. Python packages
```bash
python -c "import httpx, anthropic, dotenv; print('OK')"
```
Pass: No ImportError.

### A2. All 12 env vars set
Test: TELEGRAM_HQ_BOT_TOKEN, TELEGRAM_CHAT_ID, SUPABASE_URL, SUPABASE_SERVICE_KEY, ANTHROPIC_API_KEY, N8N_API_KEY, N8N_INST_URL, OPENAI_API_KEY + GWS_PATH exists + AGENTS_DIR exists + KB_DIR exists + PROJECT_MEMORY_FILE exists.

### A3. Supabase REST reachable
Query each table (tasks, projects, logs, audit_log, escalations, memories, kb_docs) with `limit=1`. Pass: all return non-null.

### A4. Anthropic API reachable
Minimal Haiku call: `Say OK`. Pass: responds.

### A5. Google Workspace CLI reachable
`_run_gws(['calendar', 'events', 'list', ...])`. Pass: returns data. Known risk: auth token may be expired.

### A6. n8n API reachable
GET `/api/v1/workflows?limit=1`. Pass: HTTP 200.

### A7. Telegram Bot API reachable
GET `/getMe`. Pass: returns bot username. No message sent.

---

## BATCH B: Individual Check Functions

### B1. Filesystem checks (10 functions, pure read)
`check_department_capacity`, `check_initiative_registry`, `check_governance_log`, `check_rhythm_calendar`, `check_incoming_files`, `check_tmp_files`, `check_agent_memory_staleness`, `check_document_map_integrity`, `check_skills_currency`, `check_cross_references`, `get_project_study_context`.

### B2. Supabase query functions (18 functions, read-only)
`check_pending_tasks`, `check_active_projects`, `check_escalations`, `check_today_activity`, `check_overnight_activity`, `check_recent_interactions`, `extract_daily_tasks`, `get_carry_forward_items`, `get_captured_tasks`, `check_target_completion`, `get_morning_targets_today`, `check_midday_progress`, `find_quick_decisions`, `check_supabase_sync`, `check_n8n_workflow_health`, `check_completion_trends`, `check_pending_audit_approvals`, `check_overnight_audit`.

### B3. Calendar & Email (gws CLI)
`check_calendar`, `check_email`. Depends on A5.

### B4. Write functions (WRITES test rows)
`log_morning_targets` (test payload), `log_error_event` (test event), `check_skills_inventory` (writes snapshot). Cleanup needed after.

### B5. Priority synthesis (pure logic)
`synthesize_priorities` with mock data. Verify priority ordering: CARRY-FORWARD > BLOCKED > DECISION > PREP > BUILD.

### B6. Coaching generation (pure logic)
`_generate_coaching` with all 5 pace scenarios + edge case (no targets). Verify tone mapping.

---

## BATCH C: Pipeline Integration

Run each pipeline end-to-end with `--no-telegram`:

| Test | Command | Key Pass Criteria |
|------|---------|-------------------|
| C1 | `python tools/run_audit.py morning --no-telegram` | Contains MORNING BRIEF, all sections present, no tracebacks |
| C2 | `python tools/run_audit.py midday --no-telegram` | Contains MIDDAY PULSE, progress/coaching sections |
| C3 | `python tools/run_audit.py evening --no-telegram` | Contains EVENING BRIEF, scorecard, system health |
| C4 | `python tools/run_audit.py midnight --no-telegram` | 6 checks, auto-fixes count, AI analysis, findings logged |
| C5 | `python tools/run_audit.py weekly --no-telegram` | SAGE/ATLAS/STERLING/MARCUS sections, attention items |
| C6 | `python tools/run_audit.py sync` | Shows hash comparison, syncs if needed |
| C7 | `python tools/run_audit.py daily --no-telegram` | Same as C3 (backwards compat alias) |

**CAUTION:** C4 writes to disk (auto-fixes) and audit_log. C6 pushes content to Supabase.

---

## BATCH D: AI Synthesis

### D1-D3. Morning/Midday/Evening synthesis
Call `synthesize_morning()`, `synthesize_midday()`, `synthesize_evening()` with mock data. Verify: contains correct header, has HTML tags, no code fences, length > 300 chars.

### D4. Fallback formatters
Call `format_morning()`, `format_midday()`, `format_evening()`, `format_weekly()` with minimal mock data. Verify: produces valid Telegram HTML, no exceptions.

---

## BATCH E: Delivery

### E1. Message splitting (pure logic, read-only)
Test `_split_message` with short, long, and empty messages. Verify all chunks ≤ 4000 chars.

### E2. Live Telegram delivery (SENDS MESSAGE)
`send_brief('<b>AUDIT TEST</b>...')`. Chris will see this message.

### E3. Alert delivery (SENDS MESSAGE)
`send_alert(title='Audit Test', detail='...')`. Chris will see this alert.

---

## BATCH F: Bot Tools

### F1. list_tasks (read-only)
### F2. add_task + complete_task round trip (WRITES test task, then completes it)
### F3. get_project_status (read-only)
### F4. log_escalation (WRITES test escalation)

Cleanup: delete test rows from tasks and escalations tables.

---

## BATCH G: Task Scheduler + ISSUE-0 Fix

### G1. Batch file existence
Verify all 6 .bat files exist: `audit_morning.bat`, `audit_midday.bat`, `audit_evening.bat`, `audit_weekly.bat`, `audit_sync.bat`, `audit_midnight.bat`.

### G2. Task Scheduler registration vs register_tasks.py
Query `schtasks` for SharkitectDigital tasks. **Expected live schedules:** morning **5:00 AM**, midday 12:15 PM, evening 9:00 PM, midnight 12:00 AM, weekly Sun 9:30 PM, sync hourly.

**Cross-check:** Compare live `schtasks` output against `register_tasks.py` definitions. Flag ANY discrepancy.

### G3. FIX ISSUE-0: Update register_tasks.py
- Fix MorningAudit: `/st 06:00` → `/st 05:00`
- Check if MiddayAudit is missing from `register_tasks.py` (audit_midday.bat exists). If missing, add it with `/sc daily /st 12:15`.
- Verify all times in register_tasks.py match live Task Scheduler. This file must be the canonical "re-registration script" — if someone runs it, the correct schedules get applied.

### G4. Recent log files
Check `tools/logs/` for recent run logs.

### G5. pythonw.exe path
Verify the Python path in batch files exists.

---

## BATCH H: Cross-Pipeline Data Flow

### H1. Morning → Midday
Run morning (logs targets) → run midday (reads targets, shows pace ≠ NO_TARGETS).

### H2. Evening → Morning carry-forward
Run evening (logs scorecard) → run morning (shows carry-forward items).
**KNOWN RISK:** `carried_days` may not auto-increment. Investigate whether any process handles this.

### H3. Midnight → Morning audit surfacing
Run midnight (writes audit_log) → run morning (shows OVERNIGHT DOCUMENT HEALTH section).

### H4. Tier 3 approval flow
Check audit_log for `fix_status='proposed'` → morning surfaces "PENDING AUDIT FIXES".

### H5. Full day simulation
Run all 4 pipelines in sequence: morning → midday → evening → midnight. All complete without errors.

---

## BATCH I: Cross-Reference Consistency Hardening

Chris's feedback on ISSUE-0: *"This is a perfect example as to why we need to ensure there is some sort of audit and process in place that when something is changed, updated, modified, created, etc that any and all documents, databases, memory, history, sessions, supabase, everything everywhere that references it, uses it, knows about it, needs to know about it, etc is updated with the correct and recent information."*

### What Already Exists (no duplication)

The system already has strong checks in **midnight audit** (6 integrity checks) and **weekly audit** (Sage scan: memory staleness, doc_map integrity, cross-references, skills currency, drift signals). These cover:
- Document Map ↔ filesystem sync
- INDEX.md ↔ Document Map alignment
- Agent MEMORY.md staleness (>7 days)
- SKILLS.md currency (>14 days)
- Cross-references (broken internal links between KB docs)
- Doc map stats consistency

### What's Missing — The Gap ISSUE-0 Exposed

The existing checks verify **documents reference each other correctly** but do NOT check **code-to-documentation alignment**. ISSUE-0 is a code file (`register_tasks.py`) being out of sync with documentation/configuration. This class of drift isn't caught by any current check.

### I1. New check: `check_code_doc_alignment()`

Add to `audit_checks.py`. Checks known code↔documentation pairings:

1. **Task Scheduler alignment:** Parse `register_tasks.py` scheduled times → compare against live `schtasks /query` output. Flag mismatches.
2. **Env var documentation:** Compare `.env` variable names against `config.py` expected vars. Flag any var in config that's missing from .env or vice versa.
3. **Workflow ID alignment:** Compare `.tmp/workforce-workflow-ids.json` against n8n API `/workflows` list. Flag stale IDs.

**File:** `tools/audit/audit_checks.py` — new function at the end.

### I2. Wire into weekly audit

Add `check_code_doc_alignment` to `weekly_audit.py` under a new "CODE-DOC ALIGNMENT" section (after Sage scan). Report-by-exception: only surfaces if mismatches found.

**File:** `tools/audit/weekly_audit.py`

### I3. Codify CHANGE-PROPAGATION-CHECKLIST rule

Add to CLAUDE.md under Non-Negotiables or Active Rules:

> **CHANGE PROPAGATION RULE:** When ANY configuration, schedule, ID, path, or reference changes in code, the following must ALL be updated in the same session:
> 1. The code/config file itself
> 2. MEMORY.md (if it documents the value)
> 3. Any register/setup scripts that recreate the configuration
> 4. Supabase rows (if applicable)
> 5. Related documentation (plan.md, DOCUMENT-MAP.md, etc.)
>
> The weekly `check_code_doc_alignment()` audit catches drift that slips through, but the rule is: propagate at the time of change, not after.

This combines with existing DOCUMENT SYNC PROTOCOL and MEMORY-AFTER-EVERY-STEP but explicitly covers **code configuration → documentation** sync, which was the gap.

### I4. Verify the new check catches ISSUE-0 (regression test)

After implementing I1-I2, intentionally leave a test mismatch → run the check → confirm it's flagged → fix → confirm clean.

---

## Issue Documentation Template

```
ISSUE: [Brief description]
BATCH/TEST: [e.g., B2/check_pending_tasks]
SEVERITY: CRITICAL / HIGH / MEDIUM / LOW
SYMPTOM: [What happened]
ROOT CAUSE: [Why it happened]
FIX: [What was changed]
FILES MODIFIED: [List of files]
VERIFIED: [YES/NO + how]
LESSON LEARNED: [What to remember]
```

---

## Post-Audit Sync (after all issues fixed)

1. **Clean up test data** — Delete ALL AUDIT_TEST rows from Supabase (tasks, escalations). Deferred to end per Chris's preference.
2. **MEMORY.md** — Update with: audit results summary, all issues found/fixed, lessons learned, new rules (CHANGE PROPAGATION RULE), system status
3. **session-history.md** — Full audit session summary with all 9 batches, issue log, fixes
4. **Supabase projects** — Briefing System confirmed `complete` + audit notes
5. **plan.md** — `knowledge-base/projects/briefing-system-rebuild/plan.md` updated with audit results
6. **Agent MEMORY.md files** — Update any affected agents (Sage for new check, Orion for code alignment)
7. **DOCUMENT-MAP.md / INDEX.md** — Update if any files were added/modified
8. **CLAUDE.md** — Add CHANGE PROPAGATION RULE if approved (Batch I3)
9. **Signal:** "BRIEFING SYSTEM AUDIT COMPLETE — ready for AIOS in fresh chat"
