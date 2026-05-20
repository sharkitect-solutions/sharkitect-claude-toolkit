# Phase 5: VERIFY & FIX -- Detailed Execution Plan

> **Master Plan:** `~/.claude/plans/wise-sprouting-canyon.md` (Foundation Reset)
> **Phase:** 5 of 9
> **Created:** 2026-04-10
> **Status:** COMPLETE (Phase 5A COMPLETE 2026-04-13, Phase 5B COMPLETE 2026-04-12, Phase 5C COMPLETE 2026-04-14, Phase 5D COMPLETE 2026-04-15)
> **Owner:** All workspaces (each fixes its own systems; Sentinel verifies at the end)

---

## 1. Objective

Make every autonomous system FUNCTION correctly -- not just run, but produce the right output, at the right time, through the right channel, with the right data. Close the loop on the entire Foundation Reset by verifying reality matches specs.

**This phase is collaborative.** Chris reviews real outputs on screen, provides feedback, and approves changes before they go live. This is NOT an autonomous batch fix. Each system gets a working session.

---

## 2. Guiding Principles

1. **Show, don't assume.** Present current state (screenshots, actual messages, execution data) before proposing fixes.
2. **Chris decides the format.** The AI proposes, Chris approves. No changes go live without confirmation.
3. **Test before declaring done.** Trigger each system, verify the output, confirm with Chris. No system is "complete" until Chris sees a correct output.
4. **Fix one system at a time.** Don't context-switch between systems mid-fix.
5. **Update everything downstream.** When a system is fixed, update: the spec, Supabase records, the inventory doc, and any reports that reference it.
6. **Running != Functioning.** A system that executes but produces wrong/incomplete/confusing output is BROKEN, not done.

---

## 3. Prerequisites (Verified 2026-04-10)

### 3A. Supabase Tables

All required tables exist. Phase 4B tables were created by Sentinel but are **empty** -- they need population during or after Phase 5.

| Table | Rows | Status | Phase 5 Action |
|-------|------|--------|---------------|
| projects | 10 | Has data | Verify data is current |
| tasks | 76 | Has data | Verify data is current |
| briefs | 1 | Nearly empty | Will populate as CEO briefs are fixed |
| system_health | 11 | Has data | Verify heartbeats are being written |
| error_fixes | 4 | Has data | Verify error-autofix is logging correctly |
| activity_stream | 85 | Has data | Verify events are flowing |
| memories | 638 | Has data | Dream consolidation maintains this |
| dream_log | 1 | Has data | Verify dream is writing entries |
| doc_lifecycle | 94 | Has data | Verify dispatch is working |
| documents | 0 | **EMPTY** | Populate after systems are verified (Phase 6/7) |
| lessons_learned | 0 | **EMPTY** | Populate after systems are verified (Phase 6/7) |
| user_preferences | 0 | **EMPTY** | Populate after systems are verified (Phase 6/7) |
| system_specs | 0 | **EMPTY** | Populate after systems are verified (Phase 6/7) |
| automation_registry | 0 | **EMPTY** | Populate after systems are verified (Phase 6/7) |
| sync_conflicts | 0 | **EMPTY** | Used by sync processes when they run |
| document_relationships | 0 | **EMPTY** | Populate after systems are verified (Phase 6/7) |

**Decision:** Phase 5 focuses on making systems FUNCTION. Populating the new Phase 4B tables (documents, lessons_learned, user_preferences, etc.) is deferred to Phase 6/7 -- those tables support guardrails and operational intelligence, not system functionality.

### 3B. Specs (All Complete)

Every autonomous system has an authoritative spec written in Phase 4:

| System | Spec Location | Owner |
|--------|--------------|-------|
| CEO Daily Briefs | HQ `docs/specs/spec-ceo-briefs.md` | HQ |
| Error Auto-Fix Bridge | HQ `docs/specs/spec-error-autofix.md` | HQ |
| Internal Error Handler | HQ `docs/specs/spec-error-handler.md` | HQ |
| Gap Pipeline | Skill Hub `docs/specs/spec-gap-pipeline.md` | Skill Hub |
| Gap Inbox Alert | Skill Hub `docs/specs/spec-gap-inbox-alert.md` | Skill Hub |
| Sync Skills | Skill Hub `docs/specs/spec-sync-skills.md` | Skill Hub |
| Manifest Refresh | Skill Hub `docs/specs/spec-manifest-refresh.md` | Skill Hub |
| Session Startup Guard | Skill Hub `docs/specs/spec-session-startup-guard.md` | Skill Hub |
| Gap Reporter | Skill Hub `docs/specs/spec-gap-reporter.md` | Skill Hub |
| Morning System Report | Sentinel `docs/specs/spec-morning-report.md` | Sentinel |
| Dream Consolidation | Sentinel `docs/specs/spec-dream-consolidation.md` | Sentinel |
| Repo Monitor | Sentinel `docs/specs/spec-repo-monitor.md` | Sentinel |
| Doc Lifecycle Dispatch | Sentinel `docs/specs/spec-doc-lifecycle.md` | Sentinel |
| Watcher's Watcher | Sentinel `docs/specs/spec-watchers-watcher.md` | Sentinel |

---

## 4. Message Architecture Target

Phase 5 implements this notification architecture:

### 4A. Alex Bot (Personal Assistant -- CEO Briefs Only)

| Message | Time | Content |
|---------|------|---------|
| Morning CEO Brief | 6:00 AM CT | Priorities, calendar, inbox, tasks, suggested focus |
| Midday CEO Brief | 12:00 PM CT | Course-correct, wins, blockers, afternoon plan |
| Evening CEO Brief | 9:00 PM CT | Day assessment, tomorrow prep |

**Change from current:** Switch from HQ Bot to Alex Bot. Fix the 4x duplicate send bug. Add real AI synthesis agent node to n8n workflow.

### 4B. HQ Bot (Operational/System Notifications)

| Message | Time | Content |
|---------|------|---------|
| Morning System Report | 5:00 AM CT | System health, pending gaps, brain stats, overnight activity |
| Evening System Report | 10:00 PM CT | **NEW** -- Day summary: errors, gaps processed/pending, system status, confirms all 3 CEO briefs delivered, anything needing attention before tomorrow |
| Error handler fallback | On-demand | Only when bridge is DOWN and n8n can't reach it |
| Watcher alerts | On-demand | Only when something needs CHRIS'S action (not auto-resolvable) |

**Changes from current:**
- Morning report moves from 5:45 AM to 5:00 AM
- Gap alerts (every 30 min) ELIMINATED as separate notifications -- folded into evening report
- Evening system report is NEW (must be built)
- Watcher alerts filtered to only escalate what needs human intervention

### 4C. What Gets Batched (Not Real-Time)

These items are NO LONGER separate notifications. They get included in the evening system report:

- Gaps detected and still pending at end of day
- Gaps that were auto-resolved during the day (summary count + what was built)
- Non-critical watcher events (system recovered on its own)
- Error fixes that were auto-resolved (count + summary)

### 4D. What Still Gets Real-Time Alerts

- Error handler fallback (bridge is unreachable -- means local machine may be off)
- Watcher alert for something that needs Chris's action (e.g., a system has been down for 24h+)
- Nothing else. Everything else is batched.

---

## 5. Execution Order

```
Phase 5A: HQ (Workforce HQ workspace)
  |-- 5A.1: CEO Daily Briefs (n8n workflow) -- COMPLETE (2026-04-12)
  |       Primary: rebuilt with native nodes (supabaseTool, telegramTool, gmailTool, googleCalendarTool, Claude AI Agent)
  |       Secondary: rebuilt with native nodes (supabase, telegram, gmail, googleCalendar, Claude API HTTP)
  |       Tertiary: Task Scheduler fallback updated (logging + HTML formatting)
  |       Three-tier cascade: Primary 6:00→Secondary 6:15→Tertiary 6:30, coordinated via activity_stream dedup
  |       Output: emojis, bold headers, exec summary, blockers section, workspace tags, readable dates
  |       Test webhooks on both workflows for future testing
  |-- 5A.2: Error Auto-Fix Bridge (FastAPI + cloudflared) -- VERIFIED (2026-04-13)
  |       Bridge: running (5+ days uptime), cloudflared tunnel active, startup shortcuts in place
  |       Safety controls: dedup, rate limit, circuit breaker all operational
  |       Stale Supabase records cleaned (2 orphaned 'fixing' rows from E2E test)
  |-- 5A.3: Internal Error Handler (n8n workflow) -- FIXED (2026-04-13)
  |       BUG FOUND: JSON escape bug in Bridge Webhook — same pattern as Watcher's Watcher
  |       Template interpolation of errorDetails broke JSON with special chars
  |       FIX: Changed jsonBody to use JSON.stringify() for proper escaping
  |       ADDED: Slack Error Alert fallback (DM to Chris) when bridge is unreachable
  |       Channel routing: Slack=errors/urgent, Telegram=reports/briefs (documented)
  |       All 4 internal workflows connected: Primary Brief, Secondary Brief, Watcher, Speed-to-Lead
  |       FF workflows correctly use their own FF Global Error Handler
  |       Primary brief 529 error (2026-04-13 6AM) = transient Anthropic overload, cascade worked
  v
Phase 5B: Skill Hub (this workspace)
  |-- 5B.1: Gap Reporter (global script)
  |-- 5B.2: Gap Pipeline (watcher + processing)
  |-- 5B.3: Gap Inbox Alert (redesign: eliminate, fold into evening report)
  |-- 5B.4: Session Startup Guard (hook)
  |-- 5B.5: Sync Skills (script)
  |-- 5B.6: Manifest Refresh (script)
  v
Phase 5C: Sentinel (Sentinel workspace)
  |-- 5C.1: Morning System Report -- COMPLETE (2026-04-12)
  |       Rebuilt from scratch: 6-section format, exec summary, Telegram Markdown with emojis
  |       Spec v2.0 updated, schedule changed to 5:00 AM CT, Chris approved live output
  |-- 5C.2: Evening System Report -- COMPLETE (2026-04-14)
  |       Built from scratch: format_evening_brief() rewritten, get_evening_summary() added to ops-brain.py
  |       6 sections: exec summary, system health, automation status, errors today, gap pipeline, activity summary + attention needed (conditional)
  |       Matches morning report style: Telegram Markdown, emojis, bold headers, bullet points
  |       Task Scheduler: Sentinel\EveningReport at 10:00 PM CT
  |       scheduled-runner.py: evening-report config added (20h cadence, sentinel-evening heartbeat)
  |       Spec: docs/specs/spec-evening-report.md v1.0
  |       Live Telegram test: sent successfully
  |-- 5C.3: Dream Consolidation -- COMPLETE (2026-04-12)
  |       Stage 1 verified: all 7 phases run, Supabase records updated, dream_log written
  |       Stage 2: CLI auth dependent, not blocking — Stage 1 is the critical path
  |       Dream report redesigned with Chris approval
  |-- 5C.4: Doc Lifecycle Dispatch -- COMPLETE (2026-04-12)
  |       Routing verified: per-workspace dispatch (not centralized), dirs created with parents=True
  |       Lifecycle review folders created in all 3 workspaces
  |       Processing workflow distributed to Sentinel and HQ
  |       First lifecycle trigger: May 6 (industry-skill-roadmap.md)
  |-- 5C.5: Repo Monitor -- COMPLETE (2026-04-14)
  |       Overhauled: expanded from 2 forks to all 31 forks + 4 own repos
  |       Fork-behind detection fixed (compare URL was broken since inception)
  |       Auto-sync with master-branch fallback, Supabase write errors fixed
  |       Live scan: 17 forks synced, 1 conflict detected, 4 findings routed to Skill Hub
  |       Autonomous findings pipeline built (Sentinel detects → Skill Hub evaluates)
  |-- 5C.6: Watcher's Watcher -- COMPLETE (2026-04-12)
  |       n8n workflow verified active, spec reviewed
  |       Review noted as pending for alert filtering refinement (deferred to Phase 6/7)
  v
Phase 5D: Cross-Workspace Verification
  |-- 5D.1: End-to-end gap pipeline test (file gap in HQ -> arrives in Skill Hub -> processed -> reflected in evening report)
  |-- 5D.2: Error flow test (break an n8n workflow -> error handler -> auto-fix bridge -> logged)
  |-- 5D.3: Message channel verification (Alex Bot for briefs, HQ Bot for everything else)
  |-- 5D.4: Supabase data flow verification (all heartbeats writing, all queries returning data)
```

---

## 6. Phase 5A: HQ Systems (Workforce HQ Workspace)

**Open the HQ workspace for this entire phase. Chris is on screen reviewing outputs.**

### 5A.1: CEO Daily Briefs (n8n Workflow)

**Spec:** `docs/specs/spec-ceo-briefs.md`
**Current state:** RUNNING BUT BROKEN -- sends 4 messages per trigger instead of 1.

**Step 1: Diagnose the 4x send bug**
- Open n8n workflow `xwgKEG6vfJsx43UR` in the browser
- Check execution history: what does each of the 4 messages contain?
- Identify which nodes are producing separate outputs (likely: multiple branch paths converging on separate Telegram send nodes, or a split/merge issue)
- Show Chris the workflow structure and the 4 messages

**Step 2: Review actual outputs with Chris**
- Chris pulls up Telegram history showing the 4 messages from the last CEO brief
- Chris identifies: "Message 1 has this good part, Message 4 has this good part"
- Document exactly which sections from which messages Chris wants to keep
- Agree on the target format (should match gold standard in spec, but Chris has final say)

**Step 3: Fix the n8n workflow**
- Restructure the workflow to produce ONE output message
- Merge the data gathering nodes into a single pipeline that feeds one output
- Add an AI Agent node (Claude) that takes all gathered data and synthesizes it into the gold standard format
- The AI agent node replaces the current static formatting -- it should produce the "Suggested Focus" section with real strategic advice
- Configure the AI agent with a system prompt based on the gold standard example in the spec

**Step 4: Switch to Alex Bot**
- Create or verify Alex Bot credentials in n8n
- Update the Telegram send node to use Alex Bot token instead of HQ Bot token
- Verify the chat ID is correct (same Chris user ID, different bot)

**Step 5: Test with Chris watching**
- Manually trigger the workflow in n8n
- Chris checks Telegram: did exactly ONE message arrive, from Alex Bot?
- Chris reviews the content: does it match what was agreed?
- If not right: iterate. Chris gives feedback, AI adjusts, re-trigger, re-check.
- Repeat until Chris says "that's what I want"

**Step 6: Verify all three brief types**
- Test morning, midday, and evening variants
- Each has different sections per the spec -- verify all three produce correct output
- Verify brief-to-brief continuity (midday references morning data)

**Step 7: Verify the `briefs` table logging**
- After a test brief sends, check Supabase `briefs` table for the new record
- Verify fields: type, content, timestamp, data sources used

**Step 8: Verify fallback behavior**
- Task Scheduler fallback briefs (`FallbackMorningBrief`, etc.) -- do they still exist? Are they needed?
- If n8n cloud is the primary and it's 24/7, discuss with Chris whether fallbacks add value or just add complexity
- Decision: keep or remove fallback Task Scheduler jobs

**Step 9: Update spec with any changes**
- If the gold standard format changed based on Chris's feedback, update `spec-ceo-briefs.md`
- If Alex Bot was added, update delivery channel section
- If fallbacks were removed, update failure behavior section

**Acceptance test:** Chris receives exactly 1 CEO brief from Alex Bot at the next scheduled time. Content matches agreed format. No duplicates. AI synthesis provides real strategic value.

---

### 5A.2: Error Auto-Fix Bridge

**Spec:** `docs/specs/spec-error-autofix.md`
**Current state:** RUNNING (when machine is on). Needs verification.

**Step 1: Check if it's actually running right now**
- `curl http://127.0.0.1:8765/health` -- does it respond?
- `curl http://127.0.0.1:8765/status` -- what's the current state?
- Check if cloudflared tunnel is running: `tasklist | grep cloudflared`
- Check if uvicorn is running: `tasklist | grep python` (look for the server process)

**Step 2: Check recent fix history**
- Query Supabase `error_fixes` table: what's in the 4 records?
- Are they recent? Are they accurate? Did the fixes actually work?
- Check Airtable Operations Control Center for matching records

**Step 3: Test the safety controls**
- Verify dedup: POST the same error twice within 5 min -- second should be rejected
- Verify rate limit: check the configured threshold
- Verify circuit breaker: check current breaker states via `/status`

**Step 4: Test an actual error fix (if safe to do)**
- If there's a non-critical n8n workflow to deliberately break and fix, do it
- Otherwise, review the last few error_fixes records and confirm the fixes were real

**Step 5: Verify startup behavior**
- Are `start.bat` and `start_tunnel.pyw` in the Startup folder?
- If machine reboots, does the bridge come back automatically?
- If not: this is a known risk, document it but don't block Phase 5 on it

**Step 6: Verify fallback path**
- When bridge is unreachable, does the n8n error handler fall back to Telegram via HQ Bot?
- This requires the error handler (5A.3) to be working

**Acceptance test:** Bridge is running, health endpoint responds, recent fixes are logged in Supabase and Airtable, safety controls work, fallback notification reaches HQ Bot.

---

### 5A.3: Internal Error Handler (n8n)

**Spec:** `docs/specs/spec-error-handler.md`
**Current state:** ACTIVE on n8n cloud.

**Step 1: Verify workflow is active**
- Check n8n workflow `3AVNR5ZAfuelDz5d` status
- Check recent execution history

**Step 2: Verify error routing**
- Does it POST to the cloudflared tunnel URL?
- Is the tunnel URL current? (Tunnel URL changes when cloudflared restarts)
- Check the webhook URL in the n8n workflow matches the active tunnel

**Step 3: Verify Telegram fallback**
- If bridge is unreachable, does it send via HQ Bot?
- The fallback should use HQ Bot (not Alex Bot) -- confirm

**Step 4: Verify which workflows use this as their error handler**
- List all n8n workflows that have error handling configured
- Are there workflows that SHOULD have error handling but don't?

**Acceptance test:** Error handler is active, webhook URL matches current tunnel, fallback sends via HQ Bot, critical workflows are connected.

---

## 7. Phase 5B: Skill Hub Systems (This Workspace)

**Work happens in the Skill Hub workspace. Chris reviews outputs.**

### 5B.1: Gap Reporter (Global Script)

**Spec:** `docs/specs/spec-gap-reporter.md`
**Current state:** WORKING (stdlib Python).

**Step 1: Functional test**
- Run `gap-reporter.py` with test parameters and verify a `.json` file lands in `.gap-reports/inbox/`
- Verify the JSON structure matches the spec
- Delete the test file after verification

**Step 2: Verify all workspaces can call it**
- Check the script path is accessible from HQ and Sentinel working directories
- Verify each workspace's CLAUDE.md references the correct path

**Step 3: Verify auto-filing behavior**
- The goal: when ANY workspace agent detects a gap, it should auto-file it (not just suggest filing)
- Check universal-protocols.md gap detection section -- does it say "file automatically" or "suggest filing"?
- If it says suggest, update to mandate auto-filing: "When in doubt, file a gap report. Do not ask for permission."
- This is a protocol change, not a code change

**Acceptance test:** A test gap report writes to inbox correctly. Protocol mandates auto-filing.

---

### 5B.2: Gap Pipeline (Watcher + Processing)

**Spec:** `docs/specs/spec-gap-pipeline.md`
**Current state:** WORKING but needs end-to-end verification.

**Step 1: Verify `gap-watcher.py`**
- Run `python tools/gap-watcher.py --context` -- does it correctly report inbox state?
- With an empty inbox: does it say "clear"?
- With a test file in inbox: does it produce processing context?

**Step 2: Verify processing workflow**
- Review `workflows/gap-processing.md` -- is it current and accurate?
- The ideal flow: detect gap -> auto-file report -> watcher picks it up -> AI processes (triages, builds fix, judges, deploys) -> moves to processed/ -> updates Supabase
- Verify the processed/ directory has past processed reports

**Step 3: Verify Supabase update on resolution**
- When a gap is processed: does anything write to Supabase?
- Currently: gap-watcher.py detects and reports, but does the processing workflow update any Supabase table?
- If not: add a step to gap-processing.md that writes to `activity_stream` when a gap is resolved
- This is critical for the evening system report to say "3 gaps identified, 3 resolved"

**Step 4: Verify notification flow**
- After processing: does `notify-workspaces.py` run and tell all workspaces about new capabilities?
- Verify the notification mechanism works

**Acceptance test:** End-to-end: file a test gap -> watcher detects -> processing workflow runs -> gap resolved -> moved to processed/ -> Supabase updated -> workspaces notified.

---

### 5B.3: Gap Inbox Alert (Redesign)

**Spec:** `docs/specs/spec-gap-inbox-alert.md`
**Current state:** DISABLED. Was spamming every 30 minutes even when inbox was empty (bug was fixed, but alert is still disabled in Task Scheduler).

**Decision from Chris:** Eliminate as a separate real-time notification. Gap status gets folded into the morning and evening system reports instead.

**Step 1: Verify the Task Scheduler job is disabled**
- Check `schtasks /query /tn "AutonomousOps\GapInboxAlert"` -- should be Disabled
- If still running, disable it

**Step 2: Update the spec**
- Update `spec-gap-inbox-alert.md` to reflect new status: DECOMMISSIONED
- Reason: gap status now reported via morning + evening system reports (batched, not real-time)
- Keep the script (`tools/gap-inbox-alert.py`) as reference but note it's not actively used

**Step 3: Verify gap data is queryable for reports**
- The evening system report needs to pull: "gaps identified today" and "gaps still pending"
- Verify `.gap-reports/inbox/` files have timestamps that allow date filtering
- Verify `.gap-reports/processed/` files are kept for historical reference

**Acceptance test:** Task Scheduler job confirmed disabled. Spec updated. Gap data is accessible for Sentinel's evening report to query.

---

### 5B.4: Session Startup Guard

**Spec:** `docs/specs/spec-session-startup-guard.md`
**Current state:** WORKING. Fires on every session start.

**Step 1: Verify hook registration**
- Check `~/.claude/settings.json` for the SessionStart hook entry
- Verify the script path is correct

**Step 2: Verify 3-state heartbeat logic**
- Check `.tmp/session-heartbeat.json` -- does it have today's date?
- The status table output at the top of this conversation was from the guard -- verify it matched reality

**Step 3: Fix CronCreate issue**
- Known issue: startup guard tells AI to create CronCreate jobs, but they often don't get created
- Decision needed: Is CronCreate even necessary here?
  - The startup guard already checks inboxes on every session start
  - CronCreate only helps if you have a LONG session and a gap arrives mid-session
  - If sessions are typically <2 hours, CronCreate adds complexity for minimal value
- **Recommendation:** Remove CronCreate requirement from startup guard. The guard itself checks inboxes at session start, and gaps can wait until next session start (they'll also show up in evening report now).
- If Chris agrees: update the startup guard script to remove Step 5 (cron polling) and update the spec

**Step 4: Fix Sentinel CronCreate issue**
- Known issue: Sentinel's startup guard creates a CronCreate job that polls `.gap-reports/inbox/` and `.lifecycle-reviews/inbox/` -- but these directories only exist in Skill Hub
- Fix: make startup guard workspace-aware. If workspace is NOT Skill Hub, don't create gap/lifecycle cron jobs.
- Or: if CronCreate is eliminated per Step 3 recommendation, this issue goes away

**Step 5: Verify startup guard doesn't block session start**
- The guard is non-blocking (always exits 0) -- verify this is still true
- Check timeout setting (15 seconds) -- verify it doesn't slow down session start

**Acceptance test:** Guard fires correctly, heartbeat updates, no false CronCreate instructions for non-Skill-Hub workspaces.

---

### 5B.5: Sync Skills

**Spec:** `docs/specs/spec-sync-skills.md`
**Current state:** WORKING.

**Step 1: Run and verify**
- `python tools/sync-skills.py` -- does it complete without errors?
- Check `.tmp/last-sync.json` -- is the report accurate?

**Step 2: Verify GitHub push**
- `python tools/sync-skills.py --sync --push` -- does it push to `sharkitect-claude-toolkit`?
- Verify the repo has current skills/agents/rules

**Step 3: Verify plugin backup**
- sync-skills.py was extended to backup plugins to the toolkit repo
- Verify `~/.claude/plugins/` contents are synced

**Acceptance test:** Sync runs clean, GitHub repo is current, plugins are backed up.

---

### 5B.6: Manifest Refresh

**Spec:** `docs/specs/spec-manifest-refresh.md`
**Current state:** WORKING.

**Step 1: Run and verify**
- `python tools/refresh-inventory.py` -- does it complete?
- Check `.tmp/skills-manifest.json` -- is it fresh and accurate?

**Step 2: Verify --all flag**
- `python tools/refresh-inventory.py --all` -- does it write manifests to all workspaces?

**Acceptance test:** Manifest is current, accessible from all workspaces.

---

## 8. Phase 5C: Sentinel Systems (Sentinel Workspace)

**Open the Sentinel workspace for this entire phase. Chris is on screen reviewing outputs.**

### 5C.1: Morning System Report -- COMPLETE (2026-04-12)

**Spec:** `docs/specs/spec-morning-report.md` (v2.0)
**Current state:** COMPLETE. Runs at 5:00 AM via Task Scheduler + CronCreate. Telegram Markdown format with emojis, bold headers, bullet points, executive summary. Chris approved live output.

**Step 1: Review recent output**
- Chris pulls up the most recent morning report from Telegram
- Review: Is the data correct? Are sections populated? Is it useful?
- Identify any sections that are empty, wrong, or confusing

**Step 2: Change schedule to 5:00 AM**
- Update Task Scheduler job `Sentinel\MorningReport` to fire at 5:00 AM instead of 5:45 AM
- Update the spec with new time
- If CronCreate is eliminated (5B.4 decision), remove the CronCreate reference from the spec

**Step 3: Verify Supabase data sources**
- Run `python tools/brief-generator.py morning` manually
- Check each data section: system_health, tasks, projects, activity_stream, brain memories, gap pipeline status
- For any section that's empty or wrong: trace the query back to Supabase and fix the data or query
- Show Chris the output and get feedback

**Step 4: Add gap pipeline summary**
- Morning report should include: "Gaps: X pending, Y processed total"
- Verify `brief-generator.py` queries `.gap-reports/inbox/` and `processed/` for these counts
- If not: add the query

**Step 5: Verify delivery via HQ Bot**
- Confirm the Telegram bot token used is the HQ Bot (not Alex Bot)
- Verify the message arrives in the right chat

**Step 6: Verify dedup**
- If both CronCreate and Task Scheduler could fire, verify `scheduled-runner.py` dedup works
- If CronCreate is eliminated, this is no longer a concern

**Step 7: Iterate with Chris**
- Chris reviews the test output and gives feedback on format, content, usefulness
- Make changes, re-run, re-review until Chris approves

**Acceptance test:** Report arrives at 5:00 AM via HQ Bot with correct, complete data. Chris has approved the format.

---

### 5C.2: Evening System Report (NEW -- Must Be Built)

**No existing spec.** This system doesn't exist yet and must be created.

**Step 1: Design the report format with Chris**
- Purpose: End-of-day summary of system operations and anything needing attention
- Proposed sections (Chris confirms/modifies):
  - **SYSTEM HEALTH** -- current status of all monitored components
  - **GAPS TODAY** -- gaps identified today (count, severity, which workspace). Gaps resolved today (count, what was built). Gaps still pending (count, how long they've been waiting)
  - **ERRORS TODAY** -- errors caught by auto-fix bridge (count, resolved vs blocked). Any unresolved errors needing Chris's attention.
  - **AUTOMATION STATUS** -- did all scheduled systems fire today? (CEO briefs 3x, morning report, dream consolidation). Any missed heartbeats?
  - **ACTIVITY SUMMARY** -- high-level summary of session activity across workspaces
  - **ATTENTION NEEDED** -- anything that requires Chris's action before tomorrow (blocked errors, long-pending gaps, systems that have been down)
- Chris reviews and adjusts this structure

**Step 2: Build the report generator**
- Create `tools/brief-generator.py evening` mode (extend existing script)
- Data sources: Supabase `system_health`, `error_fixes`, `activity_stream`, plus local `.gap-reports/` directories
- Format: plain text, similar style to morning report
- Delivery: Telegram via HQ Bot

**Step 3: Set up Task Scheduler job**
- Create `Sentinel\EveningReport` Task Scheduler job at 10:00 PM CT (must run AFTER the 9:00 PM evening CEO brief so it can confirm all 3 briefs were delivered)
- Create `sched-evening-report.bat` entry point
- Use `scheduled-runner.py evening-report` with dedup cadence

**Step 4: Write the spec**
- Create `docs/specs/spec-evening-report.md` following the spec template
- Include gold standard example based on what Chris approved

**Step 5: Test with Chris**
- Run the report manually, show Chris the output
- Iterate until Chris approves
- Let it run at 6:00 PM for a day or two and confirm it arrives correctly

**Acceptance test:** Evening report arrives at 6:00 PM via HQ Bot with accurate day summary. Chris has approved the format. Spec is written.

---

### 5C.3: Dream Consolidation -- COMPLETE (2026-04-12)

**Spec:** `docs/specs/spec-dream-consolidation.md`
**Current state:** VERIFIED. Stage 1 runs all 7 phases. Stage 2 depends on CLI auth (not blocking).

**Step 1: Verify it's actually running**
- Check `scheduled-runner-state.json` for last `dream-consolidation` run
- Check Supabase `dream_log` table for recent entries
- Check `.tmp/sched-dream.log` for output

**Step 2: Verify Stage 1 (deterministic)**
- Run `python tools/dream-consolidation.py` manually
- Check each of the 7 phases: ORIENT, DUPLICATES, CONFLICTS, FRESHNESS, VOICE, PATTERNS, REPORT
- Verify Supabase RPC functions exist: `find_duplicate_memories`, `find_contradicting_memories`
- If RPCs don't exist: those phases will return empty (degraded but functional)

**Step 3: Verify Stage 2 (AI synthesis)**
- Check if Claude CLI is available: `claude --version`
- Check if auth is current
- If Stage 2 has been failing (CLI auth expired), note it but don't block Phase 5 on it -- Stage 1 is the critical maintenance work

**Step 4: Review with Chris**
- Show Chris a recent dream consolidation output
- Is it providing value? Are duplicates actually being cleaned?
- Any adjustments needed?

**Acceptance test:** Stage 1 runs all 7 phases, Supabase records are updated, dream_log entry written. Stage 2 runs if CLI auth is valid.

---

### 5C.4: Doc Lifecycle Dispatch -- COMPLETE (2026-04-12)

**Spec:** `docs/specs/spec-doc-lifecycle.md`
**Current state:** VERIFIED. Per-workspace routing, lifecycle folders created in all 3 workspaces.

**Step 1: Verify Task Scheduler job**
- Check `Claude-DocLifecycle-DailyCheck` status and last run
- Verify the .bat and .vbs wrapper chain works

**Step 2: Fix routing architecture**
- Known issue: `dispatch-lifecycle-reviews.py` routes reviews to EACH workspace's `.lifecycle-reviews/inbox/` (line 227). But only Skill Hub has the inbox dir and processing infra.
- Fix: change routing to send ALL reviews to Skill Hub's `.lifecycle-reviews/inbox/` only
- Update the script's target directory

**Step 3: Verify freshness auditor**
- Run `python tools/freshness-auditor.py check --alert` manually
- Check which documents it flags and whether the staleness assessments are correct

**Step 4: Verify the first lifecycle trigger**
- MEMORY.md says first doc review triggers May 6 (industry-skill-roadmap.md)
- Verify this is correctly scheduled in `doc_lifecycle` table

**Acceptance test:** Dispatch runs daily, routes reviews to Skill Hub inbox only, freshness auditor flags correct documents.

---

### 5C.5: Repo Monitor -- COMPLETE (2026-04-14)

**Spec:** `docs/specs/spec-repo-monitor.md`
**Current state:** VERIFIED + OVERHAULED. Expanded to 31 forks + 4 own repos, fork detection fixed, autonomous routing built.

**Step 1: Verify Task Scheduler job**
- Check `Sentinel\RepoMonitor` is registered and enabled
- Verify schedule: weekly Sunday at 8:00 PM

**Step 2: Test manually**
- Run `python tools/repo-monitor.py scan` manually
- Does it find forked repos? Does it check for upstream changes?
- Verify output format

**Step 3: Verify Supabase logging**
- Does it write to `repo_findings` table (currently 0 rows)?
- After manual run: check if findings appear

**Acceptance test:** Manual run completes without errors, checks forked repos, logs to Supabase. Ready for first automated run on Apr 12.

---

### 5C.6: Watcher's Watcher (n8n) -- COMPLETE (2026-04-12)

**Spec:** `docs/specs/spec-watchers-watcher.md`
**Current state:** VERIFIED. Active on n8n cloud. Alert filtering refinement deferred to Phase 6/7.

**Step 1: Verify workflow is active**
- Check n8n workflow `N84M4ormvCzjlzTT` status and recent executions
- Check if it's actually running on schedule

**Step 2: Verify heartbeat checking logic**
- Does it query Supabase `system_health` for heartbeat timestamps?
- Are the monitored components correct? (CEO brief, morning report, dream, gap alert)
- Since gap alert is being decommissioned: remove it from monitored components or update the spec

**Step 3: Verify alert filtering**
- Chris only wants alerts when something needs HIS action
- Current behavior: alerts on any missed heartbeat
- Needed behavior: alert only if a system has been down for >24h OR if the system can't self-recover
- Systems that self-recover (dream consolidation Stage 2 failing) should be logged but not alert Chris
- Discuss with Chris which systems warrant real-time alerts vs batched evening report inclusion

**Step 4: Verify alert channel**
- Alerts should go via HQ Bot (not Alex Bot)
- Confirm Telegram credentials in n8n

**Acceptance test:** Watcher is running, monitors the right systems, only alerts for things needing Chris's action, uses HQ Bot.

---

## 9. Phase 5D: Cross-Workspace Verification

**Run after all individual systems are verified. Can be done from any workspace.**

### 5D.1: End-to-End Gap Pipeline Test

1. From HQ, trigger a gap report: `python ~/.claude/scripts/gap-reporter.py --type MISSING --severity warning --workspace "workforce-hq" --workspace-path "$(pwd)" --task "Phase 5 E2E test" --category operations --needed "Test gap" --gap "This is a test gap for E2E verification" --impact "None - test only" --fix-type skill --fix-desc "No fix needed" --fix-components "test"`
2. Verify: file appears in Skill Hub's `.gap-reports/inbox/`
3. Open Skill Hub: startup guard detects the gap
4. Process the test gap (or manually clean it up)
5. Verify: evening system report would include this gap in its summary
6. Clean up: delete test gap file

### 5D.2: Error Flow Test

1. Verify error auto-fix bridge is running (health endpoint)
2. Check: if a non-critical n8n workflow errors, does the error handler route it to the bridge?
3. Verify: bridge receives it, Claude attempts diagnosis
4. Verify: result logged to Supabase `error_fixes` and Airtable
5. Verify: if bridge were down, error handler falls back to Telegram via HQ Bot

### 5D.3: Message Channel Verification

After all systems are configured:
1. CEO briefs arrive via **Alex Bot** (not HQ Bot)
2. Morning + evening system reports arrive via **HQ Bot**
3. Error fallback alerts arrive via **HQ Bot**
4. Watcher alerts (when they fire) arrive via **HQ Bot**
5. No system sends via the wrong bot
6. No system sends duplicate messages

### 5D.4: Supabase Data Flow Verification

1. `system_health` table has recent heartbeats from: CEO brief workflow, morning report, dream consolidation
2. `briefs` table is receiving new records from CEO brief workflow
3. `error_fixes` table gets new records when errors are auto-fixed
4. `activity_stream` has recent events from all three workspaces
5. `dream_log` has entries from dream consolidation runs

---

## 10. Completion Criteria

Phase 5 is COMPLETE when:

- [ ] Every autonomous system has been individually verified as FUNCTIONING (not just running)
- [ ] Chris has reviewed and approved the output format of every user-facing message
- [ ] CEO briefs send exactly 1 message via Alex Bot at each scheduled time
- [ ] Morning system report arrives at 5:00 AM via HQ Bot with correct data
- [ ] Evening system report (NEW) arrives at ~6:00 PM via HQ Bot with day summary
- [ ] Gap pipeline works end-to-end: detect -> file -> process -> update Supabase -> reflect in evening report
- [ ] Gap inbox alert is decommissioned (folded into evening report)
- [ ] No duplicate messages from any system
- [ ] No real-time notifications except: error handler fallback (bridge down) and critical watcher alerts
- [ ] All specs updated to match actual behavior after fixes
- [ ] `autonomous-systems-inventory.md` updated with current state
- [ ] Cross-workspace data flows verified (5D tests pass)
- [ ] Supabase tables receiving data from all systems that should write to them

---

## 11. Spec Updates Needed During Phase 5

As systems are fixed, their specs must be updated to reflect reality:

| Spec | What Changes |
|------|-------------|
| `spec-ceo-briefs.md` | Delivery channel: Alex Bot. Workflow structure after 4x bug fix. AI agent node details. Fallback decision. |
| `spec-gap-inbox-alert.md` | Status: DECOMMISSIONED. Replaced by evening system report. |
| `spec-morning-report.md` | Schedule: 5:00 AM. CronCreate reference removed (if eliminated). Gap summary section added. |
| `spec-session-startup-guard.md` | CronCreate step removed (if eliminated). Workspace-aware logic documented. |
| `spec-watchers-watcher.md` | Monitored components updated (gap alert removed). Alert filtering logic documented. |
| `spec-doc-lifecycle.md` | Routing: all reviews to Skill Hub inbox only. |
| `spec-evening-report.md` | **NEW** -- must be written during 5C.2. |

---

## 12. After Phase 5

With all systems FUNCTIONING:
- **Phase 6 (GUARDRAILS)** can begin -- building drift prevention, doc freshness enforcement, session-start verification
- **Phase 4B tables** can be populated -- now that systems are stable, we can populate documents, lessons_learned, user_preferences, etc.
- **Phase 7 (OPERATIONAL)** -- everything running, verified, trusted, Supabase brain fully live

---

## Appendix A: HQ Execution Prompt

Paste this into the HQ workspace to begin Phase 5A:

```
PHASE 5A: VERIFY & FIX -- HQ SYSTEMS

You are executing Phase 5A of the Foundation Reset plan. This phase is COLLABORATIVE -- Chris is on screen reviewing outputs. Do NOT make changes without his approval.

CONTEXT:
- Master plan: ~/.claude/plans/wise-sprouting-canyon.md
- Phase 5 detail: ~/.claude/plans/phase5-verify-and-fix.md (read Section 6)
- Your specs: docs/specs/spec-ceo-briefs.md, spec-error-autofix.md, spec-error-handler.md

SYSTEMS TO VERIFY (in order):

1. CEO DAILY BRIEFS (n8n workflow xwgKEG6vfJsx43UR)
   - KNOWN BUG: Sends 4 messages per trigger instead of 1
   - TARGET: Switch delivery from HQ Bot to Alex Bot
   - TARGET: Add AI Agent node for synthesis (produces "Suggested Focus" section)
   - TARGET: Exactly 1 message per trigger matching gold standard in spec
   - PROCESS: Show Chris current outputs -> he identifies what's good -> combine -> rebuild workflow -> test -> Chris approves

2. ERROR AUTO-FIX BRIDGE (tools/error-autofix/)
   - Verify: health endpoint, recent fixes in Supabase error_fixes table, safety controls
   - Verify: startup behavior (auto-starts on login?)
   - Verify: fallback path (when bridge is down, error handler sends via HQ Bot Telegram)

3. INTERNAL ERROR HANDLER (n8n workflow 3AVNR5ZAfuelDz5d)
   - Verify: active, webhook URL matches current tunnel
   - Verify: Telegram fallback uses HQ Bot
   - Verify: critical workflows are connected to this handler

RULES:
- Show Chris what each system is doing BEFORE proposing changes
- For CEO briefs: Chris will provide screenshots of the 4 messages. Analyze them together.
- Ask Chris which elements from which messages he wants to keep
- Test every change with Chris watching before declaring it done
- After each system is verified/fixed: update its spec to match reality
- When all 3 systems are done: update MEMORY.md and report status

DO NOT:
- Make autonomous changes to n8n workflows without Chris confirming
- Assume the 4x message bug is a simple fix -- investigate first
- Skip the Alex Bot migration for CEO briefs
- Declare anything "done" without Chris seeing a correct test output
```

---

## Appendix B: Sentinel Execution Prompt

Paste this into the Sentinel workspace to begin Phase 5C:

```
PHASE 5C: VERIFY & FIX -- SENTINEL SYSTEMS

You are executing Phase 5C of the Foundation Reset plan. This phase is COLLABORATIVE -- Chris is on screen reviewing outputs. Do NOT make changes without his approval.

IMPORTANT: Run this AFTER Phase 5A (HQ) and 5B (Skill Hub) are complete. Sentinel reports on systems that should already be working.

CONTEXT:
- Master plan: ~/.claude/plans/wise-sprouting-canyon.md
- Phase 5 detail: ~/.claude/plans/phase5-verify-and-fix.md (read Section 8)
- Your specs: docs/specs/spec-morning-report.md, spec-dream-consolidation.md, spec-doc-lifecycle.md, spec-repo-monitor.md, spec-watchers-watcher.md

SYSTEMS TO VERIFY (in order):

1. MORNING SYSTEM REPORT
   - Change schedule: 5:45 AM -> 5:00 AM (update Task Scheduler job Sentinel\MorningReport)
   - Verify all data sections pull correct Supabase data
   - Add gap pipeline summary section (pending + resolved counts)
   - Delivery via HQ Bot (NOT Alex Bot)
   - Run manually, show Chris output, iterate until he approves format

2. EVENING SYSTEM REPORT (NEW -- MUST BE BUILT)
   - This does not exist yet. You are building it from scratch.
   - Purpose: end-of-day summary of system operations
   - Sections: system health, gaps today (identified/resolved/pending), errors today (auto-fixed/blocked), automation status (did all systems fire?), activity summary, attention needed
   - Design format WITH Chris -- show him a mock, get approval, then build
   - Create: brief-generator.py evening mode, Task Scheduler job at 6:00 PM, new spec
   - Delivery via HQ Bot
   - Test with Chris watching

3. DREAM CONSOLIDATION
   - Verify scheduled-runner-state.json shows recent runs
   - Verify Supabase dream_log has entries
   - Run Stage 1 manually, verify all 7 phases execute
   - Check Stage 2 (Claude CLI) availability
   - Show Chris a recent dream output, confirm it's useful

4. DOC LIFECYCLE DISPATCH
   - Fix routing: change dispatch-lifecycle-reviews.py to send ALL reviews to Skill Hub inbox only
   - Currently sends to each workspace's .lifecycle-reviews/inbox/ but only Skill Hub processes them
   - Verify freshness-auditor.py flags correct documents
   - Verify first trigger: May 6 for industry-skill-roadmap.md

5. REPO MONITOR
   - Verify Task Scheduler job Sentinel\RepoMonitor is enabled (weekly Sunday 8 PM)
   - Run manually: python tools/repo-monitor.py scan
   - Verify it checks forked repos and logs to Supabase repo_findings
   - First automated run: Apr 12

6. WATCHER'S WATCHER (n8n N84M4ormvCzjlzTT)
   - Verify active and running on schedule
   - Update monitored components: remove gap alert (decommissioned)
   - Alert filtering: only alert Chris for things needing his action
   - Systems that self-recover should be logged, not alerted
   - Alerts via HQ Bot
   - Discuss with Chris: which systems warrant real-time watcher alerts vs evening report batching?

RULES:
- Show Chris current output BEFORE proposing changes
- For the evening report: design the format WITH Chris, don't just build and show
- Test every change with Chris watching
- After each system: update its spec to match reality
- Write spec-evening-report.md when the evening report is built
- When all systems done: update MEMORY.md, update autonomous-systems-inventory.md
- Run Phase 5D cross-workspace tests after all systems are verified

DO NOT:
- Build the evening report without Chris approving the format first
- Change the morning report format without Chris reviewing
- Skip the doc lifecycle routing fix
- Declare systems done without test verification
```

---

## Appendix C: Phase 5D Cross-Workspace Prompt

Run this from any workspace after 5A, 5B, and 5C are complete:

```
PHASE 5D: CROSS-WORKSPACE VERIFICATION

All individual systems have been verified. Now test the connections between them.

Read ~/.claude/plans/phase5-verify-and-fix.md Section 9 for the full test plan.

TESTS:
1. Gap pipeline E2E: File test gap from this workspace -> verify it arrives in Skill Hub inbox -> verify evening report would include it -> clean up test file
2. Error flow: Verify error-autofix bridge health -> check recent error_fixes records -> verify fallback path
3. Message channels: Confirm CEO briefs come from Alex Bot, everything else from HQ Bot
4. Supabase data: Verify system_health heartbeats are current, briefs table has records, activity_stream has recent events, dream_log has entries

Report results as a checklist: PASS/FAIL per test with details on failures.
```
