# Operation: Founder-Grade Briefing System Rebuild

## Context

Chris has identified that the current automated briefing system and Telegram bot are not delivering founder-grade value. The morning brief this morning showed inaccurate information. The bot can't access Gmail anymore. The escalation bridge pretends to talk to Marcus but can't. The briefs report data but don't synthesize intelligence. If given to a client today, this would look amateur. This needs to be rebuilt into a real strategic tool that Chris can trust daily and eventually offer as part of the AIOS client partnership package.

---

## Part 1: What's Actually Broken (Root Cause Analysis)

### Problem A: Task Completion Tracking is 30-40% Accurate
**Root cause:** `check_target_completion()` in `audit_checks.py` uses primitive keyword/substring matching to determine if tasks are done. "Fix database bug" matches "Database backup completed" — false positive. "Send proposal" doesn't match "proposal emailed" — false negative. This poisons EVERYTHING downstream:
- Morning carry-forwards include tasks that were actually completed
- Midday pace scoring shows wrong completion percentage
- Evening scorecard is wrong
- Tomorrow's morning brief inherits yesterday's errors

**Impact:** The single largest source of inaccuracy. ~50% of all wrong data in briefs traces back to this.

### Problem B: Google Workspace Access is Broken
**Root cause:** The `gws` CLI tool's authentication token has expired. Every Gmail, Calendar, Sheets, and Docs call returns exit code 2 ("Authentication error"). This affects BOTH the automated briefs (calendar/email sections show SKIPPED) AND the Telegram bot (can't access Gmail when Chris asks).

**Fix:** Run `gws auth login` on the Windows machine. But also: evaluate whether gws CLI is the right long-term approach vs direct Google API.

### Problem C: Briefs Report Data, Don't Synthesize Intelligence
**Root cause:** Architecture design. The brief system was built as a "check runner" — run 10 checks, format results, send. There's no intelligence layer that asks "so what does this mean?" or "what should Chris do about this?"

**What's missing:**
- No "ONE THING" — the single most important task for the day
- No strategic frame connecting today's work to quarterly goals
- No financial intelligence (revenue, pipeline, cash)
- No client health signals (FF status, next milestone)
- No energy-aware scheduling (decision load, deep work windows)
- No multi-day pattern detection (carry-forward streaks, completion trends)
- No scope creep detection in midday pulse
- No learning synthesis in evening brief
- System health takes up space even when everything is fine (should report by exception)

### Problem D: Escalation Bridge is Fundamentally Broken
**Root cause:** `bridge.py` calls `claude --print` which is a raw, context-free Claude API call. No project files, no agent knowledge bases, no tools. "Marcus routing" is impossible — it's just a generic Claude response pretending to be the workforce. Already confirmed: zero real escalations have ever been logged.

**Decision:** Disable and delete. Replace with Supabase queue that surfaces in next automated brief.

### Problem E: Bot's Supabase Integration May Be Incomplete
**Root cause:** The bot has a 412-line `supabase_sync.py` that provides semantic search, shared memory, and interaction logging — but it's disabled if SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, or OPENAI_API_KEY are missing from the bot's environment. If disabled, bot memory is local-only JSON — completely disconnected from the workforce's shared brain.

### Problem F: Stale Data Sources
**Root cause:** Multiple sources of staleness:
- MEMORY.md regex parsing is fragile (single formatting change breaks extraction)
- Plan files may not reflect current state
- Supabase sync hashes ALL content together — one stale file flags everything as stale
- No staleness timestamps on individual data points in briefs

---

## Part 1B: Screenshot Diagnosis — March 24 Morning Brief

**What Chris received:**
```
MORNING BRIEF — 2026-03-24

━━━ YESTERDAY'S RESULTS ━━━
  All targets hit. Clean slate.

━━━ TODAY'S PRIORITIES ━━━
  1. [DECISION] TMC DATA ANALYST MVP
     → Run data and create accurate reports. Consider HIPAA compliance.

━━━ TODAY'S SCHEDULE ━━━
  No events today
  Focus: 6:00 AM-10:00 PM (16h available)

━━━ PROJECT TRACKER ━━━
  Unified AI Workforce — Phase 0: Supabase Foundation

━━━ PENDING DECISIONS ━━━
  • TMC DATA ANALYST MVP — Run data ...

━━━ SYSTEM STATUS ━━━
  13 overnight interaction(s)
    Telegram (3)
    Task Scheduler (10)
```

**What's wrong — line by line:**

| Section | What It Said | Reality | Root Cause |
|---------|-------------|---------|------------|
| Yesterday's Results | "All targets hit. Clean slate." | Briefing system plan was in-progress. AIOS Vision pending 6+ days. Skills audit pending. | No evening scorecard logged yesterday (Claude Code session was active). Keyword matcher defaults to "all clear" when no scorecard exists. |
| Today's Priorities | Only TMC Data Analyst | Missing: AIOS Vision (URGENT), Briefing System Rebuild (active), Skills Audit, Check Dist Sync (paused). | `synthesize_priorities()` pulls from MEMORY.md pending list via fragile regex. Only matched TMC because its formatting happens to survive the parser. |
| Today's Schedule | "No events today" + "16h available" | gws CLI auth expired → Calendar returns SKIPPED → formatted as "no events." Even if calendar was empty, "16h available" is useless with no structure. | Problem B (gws auth expired). No fallback. No time-blocking intelligence. |
| Project Tracker | "Phase 0: Supabase Foundation" | Phase 0 completed 2026-03-15. All 4 phases complete. Project PAUSED pending AIOS Vision. | Regex grabs phase name but doesn't read the COMPLETE status next to it. Stale parse. |
| Pending Decisions | Only TMC | Missing: AIOS Vision, FF access (waiting on Monday.com + Sheets), ERA fix, multiple other items. | Same regex issue as priorities — only TMC's formatting survives. |
| System Status | "13 overnight interactions: Telegram (3), Task Scheduler (10)" | Chris: "That really is not useful." Counts mean nothing without context. | Architecture: no summary/synthesis layer. Just counts. |

**Accuracy score: ~15%.** Only the date was correct.

---

## Part 2: The Vision — What Founder-Grade Looks Like

### Date Format
All briefs use **DD-MM-YYYY** format (Chris preference). Example: `24-03-2026`.

### Chris's Daily Rhythm (Input for Time-Blocking AI)
The AI needs to know Chris's personal schedule to build intelligent time blocks:

- **5:00 AM** — Wake up
- **5:00-6:00 AM** — Morning prep routine: meditation (10 min) → workout (30 min) → study (20 min). Study is LAST because it transitions the mind into the day's work topics. NOT work tasks — this block is about getting mentally ready. The AI curates 2-3 study links (articles, YouTube videos) relevant to the day's primary project, so Chris doesn't waste 10-15 minutes searching.
- **6:00 AM onwards** — Work begins. This is when the brief "kicks off" the structured work day.
- **Meals/breaks** — Factor in lunch, transitions, travel time for meetings
- **Meetings** — Pulled from Google Calendar. Block travel/prep time before and after.
- **End of productive day** — flexible, but briefs should structure up to ~9-10 PM with diminishing intensity

### Core Requirement: Intelligent Time-Blocking

This is the #1 missing feature. The AI must:

1. **Know the current projects and their phases** — what phase we're at, what was completed yesterday, what's next
2. **Break projects into concrete tasks/steps** — not "work on AIOS Vision" but "Draft Section 3: Agent Orchestration Architecture (est. 90 min)"
3. **Fill the day with time blocks** — specific "from X to Y, work on Z" assignments
4. **Respect calendar events** — meetings, travel, prep time automatically accounted for
5. **Adjust based on progress** — if behind, prioritize catch-up; if ahead, advance to next phase
6. **Adapt to task complexity** — deep work gets morning blocks (freshest thinking), admin/lighter tasks afternoon

The brief should read like a co-founder handed Chris a structured schedule, not a list of things to do.

### Morning Brief (6 AM CT) — "Here's your day, structured and ready."

```
MORNING BRIEF — 24-03-2026

━━━ STRATEGIC INSIGHT ━━━
Week 4 of Q1. AIOS Vision is the critical path to your next revenue
unlock. FF is stable. Today's work compounds toward launch readiness.
Protect the morning deep work block — it's where the breakthrough happens.

THE ONE THING
AIOS Vision Definition — Day 6 pending. This is your highest-leverage
strategic initiative. Break through today or decompose it.

━━━ YOUR DAY ━━━

  5:00-6:00  MORNING PREP
    • 10 min meditation
    • 30 min workout
    • 20 min study: AI orchestration patterns — relevant to AIOS
      📎 https://youtube.com/watch?v=... [Agent orchestration deep dive]
      📎 https://... [Multi-agent architecture patterns]
      (AI researches and curates 2-3 relevant links daily)

  6:00-8:00  DEEP WORK — AIOS Vision Definition [STRATEGIC]
    Phase: Architecture Design (Phase 2 of 4)
    Yesterday: Completed stakeholder requirements (Phase 1)
    Today's target: Draft core architecture framework
    Why first: Freshest thinking. This is your ONE THING.

  8:00-8:15  BREAK

  8:15-9:45  Briefing System Rebuild [INFRASTRUCTURE]
    Phase: Foundation fixes (Phase 1 of 4)
    Target: Fix data sources + create Supabase tasks table
    Why now: Unblocks everything else. Quick wins available.

  9:45-10:00  TRANSITION — prep for client meeting

  10:00-11:30  FF Check-in Meeting [CLIENT]
    Prep: Monday.com access status, Airtable demo ready
    Key question: When will Jesus provide Sheets access?

  11:30-12:00  LUNCH

  12:00-12:15  [Midday pulse arrives]

  12:15-2:00  Skills Audit [MAINTENANCE]
    Target: Complete 8 of 16 SKILLS.md files
    Why afternoon: Lower-complexity, systematic work

  2:00-2:15  BREAK

  2:15-4:00  AIOS Vision — Session 2 [STRATEGIC]
    Continue architecture framework from morning block
    Target: 60% draft complete by end of block

  4:00-5:00  ADMIN + COMMUNICATIONS
    Review pending decisions, respond to messages, prep tomorrow

━━━ PROJECTS OVERVIEW ━━━
  AIOS Vision Definition — Phase 2/4 (Architecture Design) — CRITICAL
  Briefing System Rebuild — Phase 1/4 (Foundation) — IN PROGRESS
  Skills Audit — 0/16 complete — PENDING
  SystemLink: Check Dist Sync — PAUSED (waiting on FF access)
  Unified AI Workforce — ALL PHASES COMPLETE, PAUSED for AIOS

━━━ MONEY ━━━ [when data exists]
  MRR: $750 (FF) | Pipeline: $0 active | Next invoice: 01-04-2026

━━━ CLIENTS ━━━
  Fantastic Floors: PAUSED (waiting Monday.com + Sheets access)
  Last contact: 23-03-2026 | Next: Interface setup when access arrives

━━━ CARRY-FORWARD ALERT ━━━
  "AIOS Vision Definition" carried 6 consecutive days.
  Today's plan dedicates 3.75 hours across 2 deep-work blocks.
  If not started by midday: escalation coaching will trigger.

━━━ PENDING DECISIONS ━━━
  • TMC Data Analyst MVP — needs planning session before build
  • ERA — fix needed before client offering
  [2 items — address in admin block or defer]

SYSTEM: All clear.
```

### Midday Pulse (12:15 PM CT) — "Are you on track?"

```
MIDDAY PULSE — 24-03-2026

THE ONE THING: AIOS Vision Definition
  Morning block (6:00-8:00): ✅ Completed / ☐ Not started / 🔄 Partial
  [If not started] "This has been pending 6 days. Your afternoon
  block (2:15-4:00) is your last shot today. Lock in."

━━━ MORNING SCORECARD ━━━
  6:00-8:00  AIOS Vision          ✅ / ☐
  8:15-9:45  Briefing Rebuild     ✅ / ☐
  10:00-11:30  FF Meeting         ✅ / ☐
  Progress: 2/3 blocks completed | PACE: ON TRACK

━━━ AFTERNOON PLAN ━━━
  12:15-2:00  Skills Audit (8/16 SKILLS.md files)
  2:15-4:00   AIOS Vision Session 2
  4:00-5:00   Admin + Communications

━━━ SCOPE CREEP CHECK ━━━
  1 new item captured since morning (not in today's plan)
  → Recommendation: Defer to tomorrow. Stay locked on AIOS.

━━━ STRATEGIC INSIGHT ━━━
  Solid morning — briefing rebuild foundation is done and you
  made progress on AIOS. Your afternoon has 2 more focus blocks.
  The Skills Audit is systematic — use it as a palate cleanser
  between the two AIOS sessions. Stay locked.
```

### Evening Brief (9 PM CT) — "Close the day, set up tomorrow"

```
EVENING BRIEF — 24-03-2026

━━━ DAY SCORE ━━━
  5/6 blocks completed | ONE THING: AIOS Vision 60% done
  Hit rate: 83% — strong day.

━━━ WIN OF THE DAY ━━━
  Broke the 6-day AIOS Vision logjam. Architecture framework
  is 60% drafted. This moves Q1's #1 strategic priority forward.

━━━ WHAT HAPPENED TODAY ━━━
  ✅ AIOS Vision — 2 deep-work blocks, architecture 60% complete
  ✅ Briefing Rebuild — Foundation fixes shipped
  ✅ FF Meeting — Monday.com access confirmed for Thursday
  ✅ Skills Audit — 8/16 files updated
  ☐ Admin block — deferred (ran long on AIOS, worth it)

━━━ PATTERN WATCH ━━━
  Briefing system rebuild growing in scope. Time-box to 2 more
  sessions, then ship MVP and iterate. Don't let infrastructure
  crowd out revenue-generating work.

━━━ TOMORROW PREVIEW ━━━
  ONE THING: AIOS Vision — finish architecture to 100%
  Key focus: AIOS final push (morning), Skills Audit (midday), Admin catch-up
  Calendar: No meetings — open for deep work
  Energy forecast: MEDIUM (2nd consecutive deep day, no meetings)

━━━ STRATEGIC INSIGHT ━━━
  Today proved deep focus > scattered breadth. 8 outcomes from one
  project beats 12 half-done across 5. Carry this into tomorrow.

SYSTEM: All clear.
```

### Key Differences from Current System
| Current | Founder-Grade |
|---------|--------------|
| Lists priorities with no structure | Structures entire day into time blocks |
| "16h available" with no guidance | Specific "6:00-8:00 work on X, 8:15-9:45 work on Y" |
| Lists task names only | Breaks projects into phases, knows current phase + yesterday's progress |
| Reports task completion via keyword matching | Uses explicit tracking (Supabase + user confirmation) |
| Generic coaching ("focus on next task") | Strategic Insight section in all 3 briefs — framing (AM), calibration (midday), reflection (PM) |
| System health takes 6+ lines even when healthy | One line: "All clear" or only surfaces exceptions |
| No financial data | Revenue, pipeline, next invoice |
| No client health | Active client status with next milestone |
| No pattern detection | Multi-day carry-forward alerts + scope creep |
| Calendar = raw event list | Calendar integrated INTO time blocks with travel/prep |
| Date format YYYY-MM-DD | DD-MM-YYYY per Chris preference |
| Evening = just scorecard | Tomorrow Preview (quick summary) + Strategic Insight (reflection) — morning brief handles full schedule |
| "13 interactions" count | "What happened today" with actual outcomes |

---

## Part 3: Architecture Decisions

### Decision 1: Two Bots — Confirmed by Chris

**CONFIRMED: Two separate bots with clear separation of concerns.**

**Bot 1: "Sharkitect HQ"** (NEW — Chris will create)
- Purpose: Automated briefs and reports ONLY
- No interaction, no conversation
- Delivers: morning brief, midday pulse, evening brief, weekly report
- Architecture: Task Scheduler Python scripts → Telegram Bot API `sendMessage`
- No running process needed — just HTTP POST calls with the bot token
- Chris glances at this for situational awareness

**Bot 2: n8n Interactive Bot** (EXISTING — connects to n8n workforce)
- Purpose: Interactive conversation with the n8n workforce
- Handles: email drafting, calendar checks, task management, queries
- Architecture: n8n webhook triggers → n8n workforce workflows → responses
- This is where Chris works when away from computer
- Source code at `tools/n8n-bot-reference/` = reference only in this workspace

**Why two works here (Chris's reasoning):**
- The Claude Code bridge proved that Claude Code sessions block the bot — interactive work can't go through Claude Code
- n8n workforce handles interactive tasks (n8n interactive bot)
- Briefs are purely automated output (Sharkitect HQ bot) — no blocking issue
- Chris only actively converses with one bot (n8n interactive) — HQ is read-only
- Clean separation: reports in one thread, work in another

### Decision 2: Where Does Intelligence Come From?

**The current scripts can't synthesize intelligence** — they run deterministic checks and format results. For founder-grade briefs, we need an AI synthesis layer.

**Recommended approach:**
1. **Deterministic scripts** gather raw data (calendar, Supabase queries, filesystem checks)
2. **Claude API call** synthesizes the raw data into the brief, applying the founder-grade format
3. **Formatted output** sent to Telegram

This means each brief becomes: `gather data → Claude synthesis → format → send`. The Claude API call is what turns raw data into "THE ONE THING today is X because Y" instead of "here are 5 tasks."

**Cost:** ~$0.02-0.05 per brief (3 briefs/day = ~$0.15/day = ~$4.50/month). Trivial.

### Decision 3: Task Completion Tracking — Three-Tier System (Confirmed by Chris)

**Kill keyword matching entirely.** Replace with a three-tier tracking system:

**Tier 1: Explicit Marking (highest confidence)**
- Chris says "done: [task]" via Telegram (n8n interactive bot) → updates Supabase `tasks` table
- Chris confirms completion during Claude Code session → updates Supabase
- No ambiguity — human said it's done

**Tier 2: Auto-Detect from Sessions (high confidence)**
- End-of-session protocol: Claude Code sessions auto-push task status updates to Supabase
- When a task is completed during a session, Supabase is updated before session closes
- Hourly Supabase sync also captures any changes from MEMORY.md updates
- n8n workflow executions update Supabase when tasks are performed (future — noted for AIOS build)

**Tier 3: AI-Assisted Suggestion (needs confirmation)**
- Claude analyzes session logs semantically (NOT keyword matching) to identify likely completions
- Presents suggestions: "It looks like you completed X and Y. Confirm?" via next brief or Telegram
- User confirms or rejects — only confirmed items change status
- This catches tasks that slipped through Tiers 1 and 2

**Supabase as single source of truth** — `tasks` table with status, priority, project, dates.

**FUTURE NOTE (for AIOS build):** n8n workflows must also update Supabase after every execution. Any work performed through Alex (n8n) or Claude Code must flow to the same source of truth. Pinecone or additional vector DB may be added alongside Supabase for enhanced semantic search. Document this requirement in the AIOS Vision Definition.

### Decision 4: Data Architecture

**Supabase is the single source of truth for ALL brief data:**

| Data | Current Source | New Source |
|------|---------------|-----------|
| Today's tasks/priorities | MEMORY.md regex | Supabase `tasks` table |
| Task completion | Keyword matching on logs | Explicit status updates in `tasks` table |
| Carry-forwards | Evening scorecard log parsing | Auto-query: incomplete tasks from yesterday |
| Calendar | gws CLI subprocess | gws CLI (fix auth) OR direct Google Calendar API |
| Email summary | gws CLI subprocess | gws CLI (fix auth) OR IMAP direct |
| Client status | Not tracked | Supabase `clients` table (new) |
| Financial data | Not tracked | Supabase `financial` table (new, when data exists) |
| Project status | Plan.md regex parsing | Supabase `projects` table (with phases) |
| Project phases | Not tracked | Supabase `project_phases` table (new) |
| Pattern detection | Not implemented | Query task history for multi-day patterns |
| Chris's preferences | Not tracked | Supabase `preferences` table (wake time, routine, etc.) |

### Decision 5: The Bridge

**Delete `bridge.py` entirely.** Replace with:
- Supabase `escalations` table: bot logs failed/out-of-scope requests
- Next automated brief surfaces them as "ESCALATION QUEUE" section
- Real resolution happens in Claude Code sessions (where Marcus actually has context)
- Bot tells Chris: "Logged for the team. You'll see this in your next brief, or raise it in your next Claude Code session."

### Decision 6: Time-Blocking Intelligence (NEW — Chris requirement)

**The #1 gap in the current briefs: no structured day plan.**

Current brief says "16h available" — useless. Founder-grade brief says "6:00-8:00 AIOS Vision, 8:15-9:45 Briefing Rebuild, ..."

**How the AI builds time blocks:**

1. **Inputs gathered by deterministic scripts:**
   - Active tasks from Supabase `tasks` table (with priority, project, estimated duration)
   - Project phases from Supabase `projects` / `project_phases` tables (current phase, what's next)
   - Calendar events from Google Calendar API (meetings, appointments)
   - Yesterday's progress from Supabase (what was completed, what carried forward)
   - Chris's preferences (5 AM wake, 5-6 AM routine block, deep work morning preference)

2. **Claude API synthesizes the time-blocked schedule:**
   - Morning prep block (5-6 AM): meditation, study, workout — NOT work tasks
   - Deep work blocks (6 AM - first meeting): highest-priority strategic work
   - Meeting blocks: from calendar, with travel/prep time before
   - Afternoon blocks: lighter complexity work, systematic tasks
   - Admin block: communications, decisions, prep for tomorrow
   - Breaks factored in every 90-120 minutes

3. **Project phase awareness:**
   - AI knows each project's phases and current position
   - "We're at Phase 2 of 4 on AIOS Vision. Phase 1 completed yesterday."
   - Tasks are broken from phase-level down to session-level subtasks
   - Estimated durations assigned to each subtask
   - If behind schedule: catch-up blocks prioritized
   - If ahead: advance to next phase

4. **Supabase `projects` table schema:**
   - `id` (uuid)
   - `name` (text) — project name
   - `status` (text) — active/paused/complete/blocked
   - `current_phase` (text) — current phase name
   - `total_phases` (int)
   - `phase_number` (int) — current phase number
   - `phase_description` (text) — what this phase involves
   - `blocker` (text, nullable) — what's blocking progress
   - `priority` (text) — critical/high/medium/low
   - `updated_at` (timestamptz)

### Decision 7: Date Format

**All briefs use DD-MM-YYYY** (e.g., `24-03-2026`). Applies to all dates in all brief types.

### Decision 8: Plan-Driven Scheduling (Chris directive, 2026-03-24)

**The brief must NOT try to schedule all projects in one day.** Current problem: `extract_daily_tasks()` returns ALL pending/in_progress tasks (up to 10) from ALL projects. Claude tries to fit everything into one day — unrealistic.

**Fix: Plan-driven, phase-aware scheduling.**

Each project has a structured plan stored in Supabase with phases, tasks, subtasks, and **pre-estimated durations**. The brief synthesizer:

1. **Queries only ACTIVE projects** (status = active, not paused/complete/blocked)
2. **For each active project, reads current phase** (from `projects` table)
3. **Pulls only tasks matching current phase** (join tasks.phase = projects.current_phase)
4. **Uses pre-estimated times** from task records — the LLM just slots tasks into time blocks, not estimates
5. **Schedules a realistic day** — maybe 2-3 projects get blocks, not all 11

**Why this works:** When we plan a project in Claude Code, we use `seed_plan_to_supabase.py` to push the plan (phases, tasks, subtasks, time estimates) into Supabase. The brief system reads from that same data. The powerful brain (Opus/Sonnet in Claude Code) does the planning and estimating. The cheap brain (Haiku in briefs) just arranges pre-estimated tasks into time blocks.

**Implementation in Phase 4 (Project Plans Buildout).**

### Decision 9: Live Plan Update Protocol (Chris directive, 2026-03-24)

**When working on any project and something comes up for a DIFFERENT phase or project:**

1. **Do NOT diverge** from current work
2. **Immediately update** the affected phase/project's plan (Supabase tasks/projects, plan document)
3. **Continue current work** — zero context switch
4. **When we reach that phase later**, the update is already there — no reconfiguring

**Example:** Working on Phase 3 (Bot Enhancement). Chris mentions "the brief should also show client health." That's Phase 5 (Intelligence Upgrades). Don't start building it. Update Phase 5's plan to include it. Continue Phase 3.

This ensures:
- Plans stay current at all times
- No forgotten requirements
- No full replanning needed when reaching a new phase
- Every insight captured at the moment it's recognized

### Decision 10: Project Plan Documentation Standard (Chris directive, 2026-03-24)

**Every pending project must have a structured plan document** stored in a persistent location and seeded to Supabase. Standard:

1. **Plan document** at `knowledge-base/projects/<project-name>/plan.md` (persistent across sessions)
2. **Supabase `projects` row** with current phase, total phases, status
3. **Supabase `tasks` rows** for each task/subtask in the current phase (and optionally upcoming phases)
4. **Each task has `estimated_minutes`** — set by Claude Code during planning sessions, used by brief Haiku for scheduling
5. **Phase transitions** tracked: when all tasks in a phase complete, advance project to next phase

---

## Part 4: Implementation Plan (Phased)

**PHASE CHECKPOINT RULE:** Stop and compact between each phase. Each phase = one session. Do NOT roll Phase 2 into Phase 1's session. Compact → fresh context → continue.

**COMPACTION CHECKPOINT RULE (Chris directive, 2026-03-24):** During plan execution, stop between tasks/phases (depending on complexity/context heaviness) so Chris can compact before moving on. Don't wait until a phase is fully complete if context is getting heavy — pause at natural task boundaries, update all memory files, and let Chris compact. This prevents context degradation mid-phase.

### Phase 1: Foundation + Data Layer — COMPLETE (2026-03-24)
**Status:** All 10 items done. Supabase tables created (tasks 18 rows, projects 11 rows, escalations). Keyword matching killed. MM-DD-YYYY format. HQ bot token. Bridge.py deleted + escalation_tool.py created.

### Phase 2: AI Synthesis + Time-Blocking — COMPLETE (2026-03-24)
**Status:** `brief_synthesizer.py` created (Claude Haiku 4.5). All 3 briefs produce time-blocked, intelligent CEO-grade output. `seed_plan_to_supabase.py` built for plan-to-Supabase flow. Code fence stripping. Fallback formatters. Cost ~$0.01-0.05/brief.

### Phase 3: Bot Enhancement + Brief Upgrades — CURRENT
**Total estimated time: ~7 hours across stages**
**Goal:** Clean up bot naming (HQ Bot vs n8n interactive bot), add task management tools to the n8n interactive bot, change morning brief to 5 AM, add study topic suggestions, seed plan data so briefs can schedule properly.

**NAMING RULE (Chris directive, 2026-03-24):**
- **HQ Bot** = ALL automated output from this platform (briefs, scheduled tasks, notifications via Task Scheduler)
- **n8n interactive bot** = Chris's interactive communication with the workforce via n8n (code lives at `tools/n8n-bot-reference/` as reference)
- The `tools/n8n-bot-reference/` directory and its code STAY as-is — it's reference code for the n8n bot
- But NOTHING outside that directory should reference "Alex bot" for HQ brief/notification functions

**Architecture context:**
- n8n interactive bot: Claude Sonnet 4.6 brain (`brain.py`), tool-use loop, 12 tools registered
- Tool pattern: `def tool_name(config: dict, **kwargs) -> dict` → `register_tool("name", func)`
- TOOL_DEFINITIONS list in `__init__.py` = source of truth for Claude
- CONFIRMATION_REQUIRED = `{"create_notion_page"}` — add `complete_task` here
- Supabase REST API pattern: httpx + `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`
- Task Scheduler: `SharkitectDigital\MorningAudit` at `/st 06:00` via `register_tasks.py`

---

#### Stage 3.0A: HQ Bot Naming Cleanup (~30 min)

**Problem:** The automated brief system (telegram_sender.py, config.py, workforce_monitor.py) falls back to `TELEGRAM_ALEX_BOT_TOKEN` when `TELEGRAM_HQ_BOT_TOKEN` isn't set. Plan documents reference "Alex bot" for HQ brief functions. Chris directive: HQ Bot is HQ Bot — no Alex bot fallback, no naming confusion.

| # | Task | Priority | Est. | Files |
|---|------|----------|------|-------|
| 3.0A.1 | Remove Alex bot fallback from `telegram_sender.py` — HQ token only, fail with clear error if missing | critical | 10 min | `tools/audit/telegram_sender.py` (lines 11, 21-22, 27-28, 156) |
| 3.0A.2 | Remove Alex bot fallback from `workforce_monitor.py` — HQ token only | high | 5 min | `tools/workforce_monitor.py` (line 25) |
| 3.0A.3 | Update `config.py` comment — remove "Alex bot = fallback" language, keep `TELEGRAM_ALEX_BOT_TOKEN` export (still used by n8n bot reference code) | high | 5 min | `tools/audit/config.py` (lines 15-17) |
| 3.0A.4 | Update `.env` comments — lines 49, 108 say "Alex Bot" for HQ-used services, clarify which bot actually uses each credential | medium | 5 min | `.env` |
| 3.0A.5 | Update MEMORY.md — change "Alex bot" refs in HQ contexts to "n8n interactive bot" or remove | high | 5 min | `memory/MEMORY.md` |

#### Stage 3.0B: Session Setup + Quick Wins (~45 min)

| # | Task | Priority | Est. | Files |
|---|------|----------|------|-------|
| 3.0B.1 | Update `session-history.md` with sessions 14-18 | high | 10 min | `memory/session-history.md` |
| 3.0B.2 | Copy plan to persistent location | high | 5 min | `knowledge-base/projects/briefing-system-rebuild/plan.md` |
| 3.0B.3 | Create `memory/video-research-queue.md` from Part 8 | medium | 10 min | `memory/video-research-queue.md` |
| 3.0B.4 | Change morning brief Task Scheduler from 6:00 AM to 5:00 AM | critical | 10 min | `schtasks /Change /TN "SharkitectDigital\MorningAudit" /ST 05:00` |
| 3.0B.5 | Seed Phase 3 tasks to Supabase with time estimates via `quick_seed()` | critical | 10 min | `tools/seed_plan_to_supabase.py` |

#### Stage 3.1: Brief Content Upgrades (~60 min)

**Chris directives (2026-03-24):**
- Add **STRATEGIC INSIGHT** section to ALL three briefs (morning=framing, midday=calibration, evening=reflection)
- Rename midday "COACHING" → "STRATEGIC INSIGHT"
- Simplify evening "TOMORROW'S DAY" (full block schedule) → "TOMORROW PREVIEW" (4-5 lines: ONE THING + key focuses + calendar + energy forecast)
- Add study topic suggestions to morning 5-6 AM block

**Strategic Insight purpose per brief:**
- **Morning:** WHY today is structured this way. What to protect. Big-picture framing.
- **Midday:** Calibration based on morning performance. Specific, honest direction for afternoon.
- **Evening:** Day's lesson connected to bigger picture. Reflection, not just data.

| # | Task | Priority | Est. | Files |
|---|------|----------|------|-------|
| 3.1.1 | Update `_MORNING_SYSTEM` prompt — add STRATEGIC INSIGHT section (framing: why today matters, what to protect) + study topic suggestions for 5-6 AM block | critical | 15 min | `tools/audit/brief_synthesizer.py` |
| 3.1.2 | Update `_build_morning_prompt()` — include primary project context (name + phase + description) so Claude can suggest study topics and frame strategic insight | high | 10 min | `tools/audit/brief_synthesizer.py` |
| 3.1.3 | Update `_MIDDAY_SYSTEM` prompt — rename COACHING → STRATEGIC INSIGHT, update description to "calibration" framing | critical | 10 min | `tools/audit/brief_synthesizer.py` |
| 3.1.4 | Update `_EVENING_SYSTEM` prompt — add STRATEGIC INSIGHT section (reflection: day's lesson, bigger picture) + change TOMORROW'S DAY to TOMORROW PREVIEW (4-5 lines: ONE THING, key focuses, calendar heads-up, energy forecast — NOT full block schedule) | critical | 15 min | `tools/audit/brief_synthesizer.py` |
| 3.1.5 | Update fallback formatters (`_fallback_morning`, `_fallback_midday`, `_fallback_evening`) — add Strategic Insight placeholder in deterministic fallbacks | medium | 10 min | `tools/audit/brief_synthesizer.py` |

*Note: V1 study topics = AI-suggested based on project context. V2 (Phase 5) = actual curated URLs via web search.*

#### Stage 3.2: Task Management Tool — `task_tool.py` (~90 min)
*Added to n8n interactive bot reference code at `tools/n8n-bot-reference/tools/`*

| # | Task | Priority | Est. | Details |
|---|------|----------|------|---------|
| 3.2.1 | Create file with Supabase REST API boilerplate | critical | 15 min | `tools/n8n-bot-reference/tools/task_tool.py` — httpx, headers, query/post/patch helpers (reuse pattern from `escalation_tool.py`) |
| 3.2.2 | Implement `list_tasks(config, **kwargs)` | critical | 20 min | Query `tasks` table. Params: `project` (optional), `status` (optional). Return formatted list with priority, project, phase, estimated_minutes |
| 3.2.3 | Implement `complete_task(config, **kwargs)` | critical | 15 min | Update status→"completed", set `completed_at`. Match by task name + optional project. This is Tier 1 explicit marking. |
| 3.2.4 | Implement `add_task(config, **kwargs)` | high | 20 min | Insert new row: task, project, priority, estimated_minutes, phase, status="pending", source="manual" |
| 3.2.5 | Implement `update_task(config, **kwargs)` | high | 15 min | PATCH by task name + project. Update: priority, status, notes, estimated_minutes |
| 3.2.6 | Register all 4 functions with `register_tool()` | high | 5 min | Bottom of file: `register_tool("list_tasks", list_tasks)` etc. |

#### Stage 3.3: Project Status Tool — `project_tool.py` (~45 min)
*Added to n8n interactive bot reference code at `tools/n8n-bot-reference/tools/`*

| # | Task | Priority | Est. | Details |
|---|------|----------|------|---------|
| 3.3.1 | Create file with Supabase REST API boilerplate | high | 10 min | `tools/n8n-bot-reference/tools/project_tool.py` |
| 3.3.2 | Implement `get_project_status(config, **kwargs)` — single project | high | 20 min | Query `projects` table by name. Return: name, phase X/Y, description, status, priority, blocker |
| 3.3.3 | Implement summary mode — all active projects | high | 15 min | When no project specified: query all where status IN (active, in_progress, blocked). One-line per project. |

#### Stage 3.4: Tool Registration + Integration (~30 min)

| # | Task | Priority | Est. | Details |
|---|------|----------|------|---------|
| 3.4.1 | Add `list_tasks` to TOOL_DEFINITIONS with input_schema | high | 5 min | `tools/n8n-bot-reference/tools/__init__.py` |
| 3.4.2 | Add `complete_task` to TOOL_DEFINITIONS + CONFIRMATION_REQUIRED | high | 5 min | Prevents accidental task completion |
| 3.4.3 | Add `add_task` to TOOL_DEFINITIONS | high | 5 min | |
| 3.4.4 | Add `update_task` to TOOL_DEFINITIONS | high | 5 min | |
| 3.4.5 | Add `get_project_status` to TOOL_DEFINITIONS | high | 5 min | |
| 3.4.6 | Import both tool files, verify no registration conflicts | high | 5 min | Test: `python -c "from tools import *"` |

#### Stage 3.5: Escalation Surfacing in HQ Briefs (~30 min)

| # | Task | Priority | Est. | Files |
|---|------|----------|------|-------|
| 3.5.1 | Add `check_escalations()` to `audit_checks.py` — query `escalations` table for status != "resolved" | high | 15 min | `tools/audit/audit_checks.py` |
| 3.5.2 | Add escalation data to `_extract_morning_data()` in `run_audit.py` | high | 10 min | `tools/run_audit.py` |
| 3.5.3 | Test: verify escalation appears in morning brief output | medium | 5 min | `python tools/run_audit.py morning --no-telegram` |

#### Stage 3.6: Cross-Platform Verification (~30 min)

| # | Task | Priority | Est. | Details |
|---|------|----------|------|---------|
| 3.6.1 | Verify bot's `.env` has `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` | high | 5 min | Check `tools/n8n-bot-reference/.env` |
| 3.6.2 | Test: `complete_task()` via Claude Code → check Supabase row updated | high | 10 min | Use `seed_plan_to_supabase.complete_task()` |
| 3.6.3 | Run morning brief dry run → verify accuracy with seeded data | high | 10 min | `python tools/run_audit.py morning --no-telegram` |
| 3.6.4 | Verify Task Scheduler morning brief now shows 5:00 AM | medium | 5 min | `schtasks /Query /TN "SharkitectDigital\MorningAudit"` |

#### Stage 3.7: Memory Updates + Phase Checkpoint (~15 min)

| # | Task | Priority | Est. | Details |
|---|------|----------|------|---------|
| 3.7.1 | Update MEMORY.md — Phase 3 complete, 5 AM change, study topics added | high | 5 min | |
| 3.7.2 | Update session-history.md with session results | high | 5 min | |
| 3.7.3 | Update Supabase `projects` row — advance to next phase | high | 5 min | `seed_plan_to_supabase.advance_project_phase()` |

**COMPACTION CHECKPOINT: Stop here. Chris compacts before Phase 3.5.**

---

### Phase 3.5: Supabase Brain Health Audit (~3 hours)
**Goal:** Ensure Supabase — the single source of truth — is healthy before building plan-driven scheduling on top of it.

**Known issues (from cross-project audit, 2026-03-24):**
- Memory distribution skewed: shared(185) + alex(115) = 75% of all 399 memories
- 500+ KB docs, 18 have null categories
- Sessions table barely used (1 record)
- Logs table doesn't exist

| # | Task | Priority | Est. | Details |
|---|------|----------|------|---------|
| 3.5.1 | Query and document memory distribution per agent | high | 30 min | SQL via Supabase MCP |
| 3.5.2 | Fix 18 KB docs with null categories | high | 30 min | Assign correct categories based on content |
| 3.5.3 | Evaluate sessions table — keep, populate, or remove | medium | 15 min | Decision + document rationale |
| 3.5.4 | Evaluate logs table — create or document why not needed | medium | 15 min | Decision + document rationale |
| 3.5.5 | Verify all write paths work: Claude Code → Supabase, n8n bot → Supabase, briefs read ← Supabase | high | 30 min | End-to-end trace |
| 3.5.6 | MEMORY SHOOTOUT: Extract video insights (B5, B9, B3, A2, A5), research Pinecone docs/pricing | high | 45 min | Video research queue |
| 3.5.7 | Create comparison matrix: 8 candidates × 7 criteria | high | 30 min | See MEMORY SHOOTOUT section below |
| 3.5.8 | Present recommendation to Chris for decision | critical | 15 min | Decision determines AIOS memory architecture |

#### MEMORY SHOOTOUT — Vector DB & Agent Memory Evaluation
**Chris directive (2026-03-24):** Compare ALL memory/vector solutions. Determine the best option — optimal, efficient, scalable, long-term.

**Candidates:**

| Solution | Type | Source | Key Evaluation Points |
|----------|------|--------|----------------------|
| Supabase pgvector | Vector DB (current) | B9 | Performance at scale, query latency, embedding limits, metadata filtering |
| Pinecone | Managed vector DB | Chris-requested | Cost, migration effort, hybrid search quality, serverless scaling |
| Zep | Agent memory platform | B5 | Human-like memory, temporal awareness, n8n integration, vs raw pgvector |
| Gemini File Search | Managed retrieval | B3 | 10x cheaper embeddings, accuracy, vendor lock-in, n8n compatibility |
| Claude Memory 2.0 | Built-in (Claude Code) | A2 | Auto dream/consolidation/pruning, supplement vs replace Supabase |
| Claude /dream | Built-in (Claude Code) | A5 | Memory consolidation quality vs manual curation |
| Weaviate | Open-source vector DB | AIOS plan | Self-hosted, hybrid search, operational overhead |
| Qdrant | Open-source vector DB | AIOS plan | Rust-based performance, filtering, deployment complexity |

**Criteria:** (1) Performance, (2) Cost at current + AIOS scale, (3) Integration (n8n + Claude Code + bot), (4) Memory intelligence, (5) Operational overhead, (6) Scalability, (7) Vendor lock-in

**Possible outcomes:** A: Stay pgvector | B: Hybrid (Supabase + Pinecone) | C: Purpose-built migration | D: Layered approach

**COMPACTION CHECKPOINT: Stop here. Chris compacts before Phase 4.**

---

### Phase 4: Project Plans Buildout + Brief Scheduling Fix (~4-5 hours)
**Goal:** Create structured plans for every pending project. Fix brief to schedule only current-phase tasks with pre-estimated times.

| # | Task | Priority | Est. | Details |
|---|------|----------|------|---------|
| 4.1 | Audit all pending projects — current state, which need plans | high | 30 min | Review MEMORY.md pending list vs Supabase `projects` |
| 4.2 | Create plan.md for AIOS Vision Definition | critical | 30 min | Phases, tasks, subtasks, estimated_minutes |
| 4.3 | Create plan.md for TMC Data Analyst MVP | high | 20 min | Needs planning session first |
| 4.4 | Create plan.md for Fix ERA | high | 20 min | Diagnosis + fix plan |
| 4.5 | Create plan.md for remaining active projects | medium | 30 min | Voice AI, Educational Meetings, GBP, etc. |
| 4.6 | Seed ALL project plans to Supabase via `quick_seed()` | critical | 30 min | Every task gets `estimated_minutes` |
| 4.7 | Add phase-aware filtering to `extract_daily_tasks()` | critical | 45 min | Join tasks.phase = projects.current_phase WHERE projects.status = 'active' |
| 4.8 | Update `_extract_morning_data()` to pass phase-filtered tasks | high | 30 min | Include project context per task |
| 4.9 | Update synthesizer prompts: use pre-estimated times, realistic 6-8h days, paused projects in tracker only | high | 20 min | `brief_synthesizer.py` |
| 4.10 | Test: seed 2-3 projects → run morning brief → verify realistic schedule with correct phase filtering | high | 15 min | Compare scheduled hours vs available |

**COMPACTION CHECKPOINT: Stop here. Chris compacts before Phase 5.**

---

### Phase 5: Intelligence Upgrades (~6-8 hours, multiple sessions)
**Goal:** Add the strategic partner layer that makes this client-packageable.

| # | Task | Priority | Est. | Details |
|---|------|----------|------|---------|
| 5.1 | Client health tracking | high | 90 min | Supabase `clients` table, surface in morning brief (FF status, next milestone, last contact) |
| 5.2 | Financial intelligence | medium | 60 min | MRR, pipeline, next invoice — when data exists |
| 5.3 | Cross-day pattern analysis | high | 60 min | Weekly trends, completion rate, carry-forward streaks, energy patterns |
| 5.4 | Study link curation (V2) | medium | 90 min | Web search for actual URLs — upgrade from V1 topic suggestions to curated links |
| 5.5 | Voice message support | medium | 60 min | Transcribe voice → process as text |
| 5.6 | n8n workflow status integration | medium | 45 min | n8n interactive bot queries workforce workflow health |
| 5.7 | AIOS preparation | high | 90 min | Client-packageable architecture documentation |

### FUTURE — Documented for AIOS Build
- n8n workflows must update Supabase after every execution
- Pinecone/vector DB decision from Phase 3.5 MEMORY SHOOTOUT informs AIOS memory architecture
- All platforms (Claude Code, Telegram Alex, n8n workflows) write to same source of truth
- Client-facing version of this briefing system as part of partnership package
- **POST-N8N-ALEX CLEANUP:** Once n8n Alex is fully built and functional, review `tools/n8n-bot-reference/` folder — remove files no longer needed as reference. Standalone bot was killed 2026-03-24 (PID 181992). Folder renamed from `alex-telegram-bot`. Only keep what's useful for n8n tool patterns.

---

## Part 5: Critical Files

### Phase 1-2 (COMPLETE)
- `tools/audit/audit_checks.py` — keyword matching killed, Supabase queries active
- `tools/audit/daily_audit.py` — data gathering restructured
- `tools/audit/report_formatter.py` — preserved as deterministic fallback
- `tools/run_audit.py` — Claude API synthesis, HQ bot delivery, data extraction helpers
- `tools/audit/brief_synthesizer.py` — CREATED. Claude Haiku synthesis for all 3 briefs
- `tools/seed_plan_to_supabase.py` — CREATED. Plan-to-Supabase seeding tool
- `tools/audit/telegram_sender.py` — HQ bot token support added
- `tools/audit/config.py` — ANTHROPIC_API_KEY added
- `tools/n8n-bot-reference/tools/escalation_tool.py` — CREATED. Replaces bridge.py

### Phase 3: Files to Create
- `tools/n8n-bot-reference/tools/task_tool.py` — Task CRUD via Supabase REST API (n8n bot reference)
- `tools/n8n-bot-reference/tools/project_tool.py` — Project status queries (n8n bot reference)
- `memory/video-research-queue.md` — Video research catalog (from Part 8)

### Phase 3: Files to Modify (Stage 3.0A — Naming Cleanup)
- `tools/audit/telegram_sender.py` — Remove Alex bot fallback, HQ token ONLY
- `tools/audit/config.py` — Update comment (no "Alex bot = fallback" language)
- `tools/workforce_monitor.py` — Remove Alex bot fallback, HQ token ONLY
- `.env` — Update comments for credential usage clarity
- `memory/MEMORY.md` — Clean Alex bot references in HQ contexts

### Phase 3: Files to Modify (Stages 3.1-3.7)
- `tools/n8n-bot-reference/tools/__init__.py` — Register task_tool and project_tool, update TOOL_DEFINITIONS
- `tools/audit/audit_checks.py` — Add `check_escalations()` for unresolved escalation surfacing
- `tools/run_audit.py` — Add escalation data to morning brief extraction
- `tools/audit/brief_synthesizer.py` — Update morning prompt for study topic suggestions in 5-6 AM block
- Task Scheduler `SharkitectDigital\MorningAudit` — Change trigger from 06:00 to 05:00

### Phase 4: Files to Create
- `knowledge-base/projects/<each-project>/plan.md` — Structured plan docs for each pending project

### Phase 4: Files to Modify
- `tools/audit/audit_checks.py` — Add phase-aware filtering to `extract_daily_tasks()` (current: returns all pending tasks; new: filter by current phase of active projects)
- `tools/run_audit.py` — Update `_extract_morning_data()` to pass phase-filtered tasks with project context
- `tools/audit/brief_synthesizer.py` — Update system prompts to use pre-estimated times and schedule only current-phase tasks

### Existing Code to Reuse
- `tools/n8n-bot-reference/tools/escalation_tool.py` — Supabase REST API pattern for new tools (httpx, same headers)
- `tools/seed_plan_to_supabase.py` — `quick_seed()` for project plan seeding during Phase 4
- `tools/n8n-bot-reference/supabase_sync.py` — Bidirectional Supabase sync (412 lines, already working)
- `tools/n8n-bot-reference/brain.py` — Tool-use loop architecture for new tool registration

---

## Part 6: Verification Plan

### Phase 1 Verification
- [ ] `gws auth login` succeeds, calendar/email checks return data
- [ ] Supabase `tasks` + `projects` + `escalations` tables created
- [ ] Tasks seeded from MEMORY.md pending list — all 11 pending items present with correct status
- [ ] Projects seeded — AIOS Vision (active, Phase 2/4), Briefing Rebuild (active, Phase 1/4), etc.
- [ ] `python tools/run_audit.py morning --no-telegram` shows accurate data from Supabase
- [ ] Morning brief delivered via Sharkitect HQ bot token ONLY (no Alex bot fallback)
- [ ] Bridge.py deleted, escalation_tool.py in n8n bot reference code
- [ ] Date format = DD-MM-YYYY in all briefs
- [ ] **Screenshot re-test**: run morning brief, compare every line to reality. Target: 90%+ accuracy

### Phase 2 Verification
- [ ] Morning brief includes full time-blocked schedule (specific "6:00-8:00 work on X")
- [ ] 5:00-6:00 AM block shows morning prep routine (not work tasks)
- [ ] Deep work blocks assigned to morning, lighter work to afternoon
- [ ] Calendar events integrated into time blocks with travel/prep time
- [ ] Project phases shown correctly ("Phase 2 of 4, yesterday completed Phase 1")
- [ ] Tasks decomposed into concrete subtasks with estimated durations
- [ ] Claude synthesis produces intelligent, specific insights (not generic)
- [ ] Midday scorecard shows block-by-block progress, scope creep detection
- [ ] Evening brief includes tomorrow's day pre-structured
- [ ] System health = one line when healthy
- [ ] Synthesis cost confirmed (~$0.01-0.05/brief)
- [ ] Multi-day carry-forward alerts working (3+ days)
- [ ] Projects overview shows ALL active projects with current phase

### Phase 3 Verification
**Stage 3.0A (Naming Cleanup):**
- [ ] `telegram_sender.py` uses HQ bot token ONLY — no Alex bot fallback
- [ ] `workforce_monitor.py` uses HQ bot token ONLY — no Alex bot fallback
- [ ] `config.py` comment updated — no "Alex bot = fallback" language
- [ ] `.env` comments clarified — each credential shows which system uses it
- [ ] MEMORY.md cleaned — no "Alex bot" references in HQ brief contexts
- [ ] No code outside `tools/n8n-bot-reference/` references Alex bot for HQ functions

**Stage 3.0B (Setup) + Stages 3.1-3.7:**
- [ ] Morning brief Task Scheduler changed from 6:00 AM to 5:00 AM (confirmed via `schtasks /Query`)
- [ ] Morning brief includes study topic suggestions in 5-6 AM block based on day's primary project
- [ ] All three briefs include STRATEGIC INSIGHT section (morning=framing, midday=calibration, evening=reflection)
- [ ] Midday brief "COACHING" renamed to "STRATEGIC INSIGHT"
- [ ] Evening brief "TOMORROW'S DAY" simplified to "TOMORROW PREVIEW" (4-5 lines, not full block schedule)
- [ ] Phase 3 tasks seeded to Supabase with `estimated_minutes` populated
- [ ] `task_tool.py` created with list_tasks, complete_task, add_task, update_task (in n8n bot reference code)
- [ ] `project_tool.py` created with get_project_status (in n8n bot reference code)
- [ ] Both tools registered in `__init__.py` with TOOL_DEFINITIONS
- [ ] complete_task added to CONFIRMATION_REQUIRED list
- [ ] n8n bot Supabase connectivity verified (SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY in bot env)
- [ ] Cross-platform sync: complete task in Claude Code → reflected in Supabase → visible in next HQ brief
- [ ] Unresolved escalations surface in morning brief "ESCALATION QUEUE" section
- [ ] n8n bot restarts cleanly after tool additions (no import errors, no registration conflicts)
- [ ] Morning brief dry run (`python tools/run_audit.py morning --no-telegram`) shows accurate, time-blocked output
- [ ] Plan copied to `knowledge-base/projects/briefing-system-rebuild/plan.md` (persistent)
- [ ] `memory/video-research-queue.md` created from Part 8

### Phase 4 Verification
- [ ] All active pending projects have plan documents at `knowledge-base/projects/<name>/plan.md`
- [ ] All project plans seeded to Supabase via `seed_plan_to_supabase.py`
- [ ] Each task in Supabase has `estimated_minutes` populated (not null)
- [ ] `extract_daily_tasks()` only returns tasks matching current phase of active projects
- [ ] Paused/blocked/complete projects do NOT have tasks in daily schedule
- [ ] Morning brief schedules realistic day (6-8h active work, not all 11 projects)
- [ ] Time blocks use pre-estimated durations from Supabase, not AI-generated guesses
- [ ] Morning brief shows "Project X — Phase 2/4" context alongside scheduled tasks
- [ ] Paused projects appear in Project Tracker section only, NOT in time-blocked schedule

### Phase 3.5 Verification (Supabase Brain Health)
- [ ] Memory distribution per agent queried and documented
- [ ] C-suite agents with <10 memories evaluated — seed more if needed
- [ ] 18 KB docs with null categories fixed
- [ ] Sessions table decision made (use or remove)
- [ ] Logs table decision made (create or document why not needed)
- [ ] All write paths verified: Claude Code → Supabase, n8n bot → Supabase, briefs read from Supabase

### Client-Ready Test (Phase 5+)
- [ ] Brief looks professional — would not embarrass in a client demo
- [ ] Every data point traceable to source
- [ ] No stale data without freshness indicator
- [ ] Brief is actionable AND structured — founder can follow it like a schedule
- [ ] Architecture is documented for future client packaging

---

## Part 7: Session Handoff (ABSORBED INTO PHASE 3 STAGE 0)

All handoff tasks are now tracked as Stage 3.0 in Phase 3 above. Memory updates (MEMORY.md rules, session-history.md sessions 14-18) were completed in the prior session. Remaining items:
- 3.0.2: Copy plan to persistent `knowledge-base/projects/briefing-system-rebuild/plan.md`
- 3.0.3: Create `memory/video-research-queue.md`
- 3.0.5: Seed Phase 3 tasks to Supabase

---

## Part 8: Video Research Queue (2026-03-24)

**Chris directive:** Document videos now, extract insights at the appropriate stopping point when we reach the phase they relate to. Per LIVE PLAN UPDATE PROTOCOL — capture now, integrate later.

**Post-plan-mode action:** Copy this section to `memory/video-research-queue.md` as persistent reference.

### Category A: Claude Code Capabilities
*Discuss during: Phase 5 (Intelligence Upgrades) + AIOS Vision Definition*

| # | Video | Creator | Key Topic | Where It Fits |
|---|-------|---------|-----------|---------------|
| A1 | [Agent Teams](https://youtu.be/vDVSGVpB2vc) | Nate Herk | Lead + teammates, shared task list, inter-agent messaging. Enable via experimental flag. Best for 3-5 teammates. | AIOS Vision — parallel workforce ops. Phase 5 evaluation. |
| A2 | [Memory 2.0 / AutoMemory](https://youtu.be/LrgfmZkl3nc) | Nate Herk | "Auto dream" background sub-agent reviews/consolidates/prunes memory. Learns developer habits. v2.1.7+. | Phase 3.5 (compare with Supabase brain). AIOS Vision. |
| A3 | [Auto Mode](https://youtu.be/pkSxISewcw8) | Nate Herk | Safer alternative to bypass permissions. Background classifier auto-approves safe ops, blocks risky. Research preview. | Immediate evaluation for daily workflow. |
| A4 | [Claude Desktop / Cowork](https://youtu.be/X6EGzi9qm3E) | Nate Herk | Non-technical delegation via Claude Desktop. VM environment. Scheduled automation, Projects, mobile. **TABLED** by Chris for learning phases. | Chris's personal learning queue. AIOS client onboarding. |
| A5 | [/dream Feature](https://youtu.be/E-1Lmyv6Cjo) | Chase AI | Hidden /dream command for memory consolidation. Massively upgrades persistent memory quality. | Phase 3.5 (Supabase Brain Health). Compare /dream vs manual memory curation. |
| A6 | [Hosting Claude Code Agents](https://youtu.be/UGIZnh6HNLc) | Nate Herk | Deploying Claude Code agents to run persistently (cloud/server hosting). | AIOS Vision — production deployment architecture. |
| A7 | [Co-Founder System](https://youtu.be/PG6w8_HEn-o) | Nick Puru | Complete system for using Claude as co-founder. Full workflow architecture. | AIOS Vision — reference architecture. Chris learning. |

### Category B: RAG + n8n Agent Architecture
*Discuss during: Phase 3.5 (Supabase Brain Health) + AIOS Vision + n8n Workforce Enhancement*

| # | Video | Creator | Key Topic | Where It Fits |
|---|-------|---------|-----------|---------------|
| B1 | [RAG Agents in n8n](https://youtu.be/kOKavHnlPik) | Nate Herk | Building RAG agents easily in n8n. Core pattern. | n8n workforce enhancement (Topic E from Chris). |
| B2 | [RAG Masterclass 2026](https://youtu.be/dxeCH2duhMo) | Jack Roberts | Most profitable AI skill — full RAG deep dive. | AIOS Vision — RAG as client offering component. |
| B3 | [Gemini File Search for RAG](https://youtu.be/irg-2IfAjpo) | Nate Herk | Gemini's file search 10x cheaper for RAG agents. Alternative to OpenAI embeddings. | Phase 3.5 — evaluate embedding cost reduction. AIOS scaling. |
| B4 | [No-Code RAG Agents](https://youtu.be/QojPKL96Dx4) | Nate Herk | Easiest way to build RAG agents without code. | AIOS client onboarding — simplified RAG for clients. |
| B5 | [n8n + Zep Agent Memory](https://youtu.be/kNsX2qu8jHY) | Nate Herk | Human-like memory for agents using Zep + n8n. Next evolution of agent memory. | Phase 3.5 — evaluate Zep vs Supabase pgvector vs Pinecone. AIOS Vision. |
| B10 | Pinecone (no video — Chris-requested) | — | Leading managed vector DB. Serverless, metadata filtering, namespaces, hybrid search. Widely used in production RAG. | Phase 3.5 — MEMORY SHOOTOUT (see below). AIOS Vision. |
| B6 | [RAG Agents Step by Step](https://youtu.be/wEXrbtqNIqI) | Nate Herk | Incremental improvements to RAG agent quality. | n8n workforce enhancement reference. |
| B7 | [Metadata for RAG](https://youtu.be/lnm0PMi-4mE) | Nate Herk | Beginner's guide to metadata — makes RAG agents smarter. | Phase 3.5 — improve Supabase KB doc categorization (18 null categories). |
| B8 | [Reranking & Metadata in n8n](https://youtu.be/xWhX61651H8) | Nate Herk | n8n RAG reranking + metadata features. Advanced retrieval quality. | n8n workforce enhancement — improve agent response quality. |
| B9 | [Supabase + Postgres RAG in n8n](https://youtu.be/JjBofKJnYIU) | Nate Herk | Setting up Supabase + Postgres for RAG with memory in n8n. | **DIRECTLY RELEVANT** — our exact stack. Phase 3.5 + n8n workforce. |

### Category C: Full Architecture / Course
*Discuss during: AIOS Vision Definition*

| # | Video | Creator | Key Topic | Where It Fits |
|---|-------|---------|-----------|---------------|
| C1 | [Building AI Agents Full Course](https://youtu.be/eA9Zf2-qYYM) | Greg Isenberg | Complete course on building AI agents that work. | AIOS Vision — comprehensive reference. |
| C2 | [Liam Otley AIOS](https://youtu.be/P3mFkCLea_E) | Liam Otley | AIOS architecture and vision. | AIOS Vision — direct reference. |

### Research Status Summary
- **Already researched (from official docs):** Agent Teams, Cowork/Desktop, Dispatch, Scheduled Tasks, Connectors, Auto Mode
- **Partially researched (from search results):** Memory 2.0, /dream
- **Not yet extracted (title only):** All Category B videos, Nick Puru system, Greg Isenberg course, hosting, Liam Otley
- **Windows 10 constraints noted:** Computer Use + Dispatch = macOS only. Agent Teams split panes need tmux (in-process mode works).

### Chris's Remaining Topics (from prior session)
- **Topic C:** Multi-device seamless workforce → Relates to A4 (Cowork), A6 (Hosting)
- **Topic D:** Cross-project folder knowledge sync → Relates to A2 (Memory 2.0), A5 (/dream)
- **Topic E:** n8n workforce enhancement with skills → Relates to ALL Category B videos
