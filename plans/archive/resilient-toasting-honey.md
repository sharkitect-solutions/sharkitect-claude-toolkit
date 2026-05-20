# Complete System Retrospective + Restructure Plan

## FRESH CHAT EXECUTION GUIDE

**Status:** APPROVED — Ready for execution.
**Plan location:** This file + permanent copy at `knowledge-base/projects/aios-vision-definition/restructure-retrospective.md`
**To begin:** Start a new chat and say: "Let's execute the restructure plan. Begin with Session 1."

### Session Breakdown (compaction-safe chunks)

Each session is sized to complete within ~60-70% context, leaving room for memory saves before compacting.

**SESSION 1 — Foundation (Phases 2-3, ~60 min)**
- Phase 2: Memory architecture research → write decision document
- Phase 3: Slim CLAUDE.md from 347 → 200-250 lines
- **End of session:** Save progress to MEMORY.md + Supabase. Compact.
- **Pickup marker:** "Session 1 complete. CLAUDE.md slimmed. Memory architecture decided."

**SESSION 2 — Core Files + Migration Start (Phases 4-5A, ~50 min)**
- Phase 4: Slim MEMORY.md from 250+ → under 150 lines (move data to Supabase)
- Phase 5A: Migrate all 16 agents' content to Supabase `memories` table
- **End of session:** Save progress to MEMORY.md + Supabase. Compact.
- **Pickup marker:** "Session 2 complete. MEMORY.md slimmed. 16 agents migrated to Supabase."

**SESSION 3 — Skill Specs + Archive (Phases 5B-5C, ~40 min)**
- Phase 5B: Write all 16 custom skill specification documents
- Phase 5C: Archive agent folders + update audit code
- **End of session:** Save progress to MEMORY.md + Supabase. Compact.
- **Pickup marker:** "Session 3 complete. 16 skill specs written. Agent folders archived."

**SESSION 4 — Deliverables + Hooks (Phases 6-7, ~45 min)**
- Phase 6: Gap analysis → builder deliverable document
- Phase 7: Configure basic enforcement hooks (line count limits)
- **End of session:** Save progress to MEMORY.md + Supabase. Compact.
- **Pickup marker:** "Session 4 complete. Builder deliverable ready. Basic hooks configured."

**SESSION 5 — Verify + Finalize (Phases 8-9, ~45 min)**
- Phase 8: Run verification checks on everything
- Phase 9: Project plan reorganization + platform assessment + final state sync
- **End of session:** Full state sync to MEMORY.md + Supabase. Project complete.
- **Pickup marker:** "Restructure COMPLETE. All 27 verification criteria passed."

### How to Resume After Compaction

1. Read this plan file (it has the session breakdown above)
2. Read MEMORY.md (has current progress markers)
3. Check the pickup marker — it tells you exactly where to start
4. Continue with the next session's phases

### Key Files Modified During Execution

| File | Phase | Change |
|------|-------|--------|
| `CLAUDE.md` | 3 | Slimmed from 347 → 200-250 lines |
| `MEMORY.md` | 4 | Slimmed from 250+ → under 150 lines |
| `knowledge-base/projects/aios-vision-definition/memory-architecture.md` | 2 | NEW — architecture decision doc |
| `knowledge-base/projects/aios-vision-definition/skill-specs.md` | 5B | NEW — 16 skill specifications |
| `knowledge-base/projects/aios-vision-definition/builder-deliverable.md` | 6 | NEW — hooks/skills/plugins spec |
| `knowledge-base/projects/aios-vision-definition/platform-capabilities.md` | 9B | NEW — Claude Code feature assessment |
| `knowledge-base/projects/aios-vision-definition/restructure-retrospective.md` | 9C | Permanent copy of this plan |
| `tools/audit/config.py` | 5C | Updated for archived agents |
| `tools/audit/audit_checks.py` | 5C | Graceful handling of archived agents |
| `agents/*` → `_archive/agents/*` | 5C | All 16 agent folders archived |
| All 10 project `plan.md` files | 9A | Reviewed + structured |
| Supabase `memories` table | 4, 5A | Agent content + moved decisions |
| Supabase `projects` table | 9A | Priorities re-evaluated |
| `.claude/settings.json` or hook config | 7 | Basic enforcement hooks |

---

## Part 1: What We've Learned (3+ Weeks, ~50 Sessions)

### Platform Truth: Claude Code Is a Single Agent

The fundamental mistake: we built a 16-agent organizational hierarchy on a platform that runs ONE agent per session. Every "agent activation" was just me reading a different markdown file and pretending to be someone else. The context window never changed. The capabilities never changed. It was theater.

**What Claude Code actually is:**
- One AI model (Opus/Sonnet) with one context window per session
- Tools: file read/write, bash, grep, glob, web search/fetch
- Task tool: launches REAL separate subprocess agents (35+ types: fullstack-developer, business-analyst, code-reviewer, debugger, etc.)
- MCP servers: external service connections (Supabase, GitHub, Slack, Gmail, Calendar, etc.)
- Skills/plugins: prompt templates that activate specialized behavior within THIS agent
- Hooks: pre/post tool execution scripts — automated enforcement (INSTALLED but ZERO configured)
- MEMORY.md: auto-loaded every session, truncated at 200 lines
- CLAUDE.md: project instructions, effectiveness degrades above ~300 lines

**What Claude Code is NOT:**
- A multi-agent orchestration platform (that's n8n, CrewAI, LangGraph)
- A persistent process (each session starts fresh from files)
- A database (state lives in files or Supabase, not in the model)
- Able to update its own memory files while running headless (Task Scheduler runs Python scripts, not Claude Code)

**NEW platform capabilities discovered (March 2026 — research preview / recent releases):**
- **Channels** — Push events INTO running sessions from Telegram, Discord, iMessage. Two-way communication + permission relay (approve/deny tool use from phone). Plugin-based: `telegram@claude-plugins-official`. Requires v2.1.80+, claude.ai login.
- **Cloud Scheduled Tasks** — Run on Anthropic's infrastructure. Work when computer is OFF. No local Task Scheduler needed.
- **Remote Control** — Continue any running session from phone or browser.
- **Dispatch** — Send a message from phone → creates a desktop Claude Code session automatically.
- **Desktop App** — Windows native app. Visual diff review, multiple simultaneous sessions.
- **Agent SDK** — Build custom agents powered by Claude Code's tools and capabilities.
- **Chrome Extension** — Debugging assistance in browser.

These capabilities fundamentally change the architecture. See Part 2 for impact analysis.

**What I should have told you on Day 1:** "Chris, Claude Code is one very capable agent. The way to get multi-agent behavior is through the Task tool (real subprocesses) and n8n (real workflows). Building 16 agent folders with role documents is creating maintenance overhead with zero capability gain. Let's use the platform's actual strengths instead."

### What Works (Verified, Preserved)

| Component | Status | Evidence |
|-----------|--------|----------|
| Task Scheduler (6 tasks) | WORKING | Logs show daily execution since install |
| Briefing pipeline (audit_checks.py → brief_synthesizer.py → telegram_sender.py) | WORKING | Morning briefs delivering, HTML sanitizer fixed Telegram errors |
| Supabase (8 tables, REST API) | WORKING | 428 memories, 1,348 kb_docs, tasks/projects/escalations/audit_log/logs/sessions |
| Midnight document health audit | WORKING | Runs nightly, logs to audit_log, surfaces in morning brief |
| n8n (17 workflows, 16 active) | SKELETON | ~35% complete — 14 of 17 are 7-node skeletons |
| Knowledge base (46 docs) | ACCURATE | Business knowledge, pricing, ICP, client details all current |
| Supabase sync (hourly) | WORKING | Hash-based change detection, auto-push |
| seed_supabase.py / seed_plan_to_supabase.py | WORKING | Memory + KB seeding, plan-to-tasks pipeline |
| GWS CLI integration | WORKING | Calendar + email checks in briefs |
| Python tooling (63 scripts) | WORKING | Bootstrap, report generators, DOCX builder, audit tools |

### What Doesn't Work (Root Causes)

| Problem | Root Cause | Real Fix |
|---------|-----------|----------|
| 80 agent files go stale | Nobody reads them — they're static docs pretending to be dynamic | Eliminate. Move to Supabase rows. |
| MEMORY.md exceeds 200 lines (truncated) | Rules accumulate, never pruned. 30+ active rules, many aspirational | Slim to <150 lines. Move history to Supabase. |
| CLAUDE.md at 347 lines | Every new rule gets added, nothing removed | Slim to 200-250 lines. Only enforceable rules. |
| 12 non-negotiables, 0 enforced | No hooks configured. Rules depend on model "remembering" | Reduce to 5. Automate via hooks. |
| Operating Rhythm Calendar shows "2026-03-17" | Task Scheduler runs Python headless — can't update MEMORY.md | Remove from MEMORY.md. Track in Supabase. |
| Session continuity breaks on compaction | State only persists if explicitly written to files before compaction | Checkpoint protocol with Supabase push |
| Agent "activation" is just reading files | Single context window. Reading Marcus ROLE.md doesn't create Marcus. | Use Task tool subagents for real delegation |
| session-history.md is 3,590 lines | Nobody reads a 3,590-line file. Information lost in volume. | Replace with Supabase session log entries |
| Context runs out mid-task | No built-in awareness of context consumption | Checkpoint protocol with natural stopping points |

### Key Decisions That Proved Right

1. **Supabase as backend** — Healthiest part of the system. REST API works. Schema is clean. Embeddings at 100%.
2. **Briefing pipeline architecture** — Deterministic data collection + AI synthesis is the right pattern. Haiku for synthesis, Opus for planning.
3. **Task Scheduler for automation** — Reliable, runs without intervention.
4. **Phase-aware task filtering** — Only scheduling tasks for active project phases prevents overload.
5. **Plan-to-Supabase pipeline** — Planning sessions auto-seed tasks with estimated_minutes.
6. **Report-by-exception** — System health only surfaces issues, not "all clear" noise.

### Key Decisions That Proved Wrong

1. **16-agent folder model** — Created 80 files of maintenance debt with zero capability gain.
2. **MEMORY.md as operational database** — Should be an index, not a data store.
3. **Rules without enforcement** — 30+ rules, 0 hooks. Aspirational, not operational.
4. **Session-history.md as continuity mechanism** — 3,590 lines nobody reads.
5. **Agent SKILLS.md files** — Manually maintained capability lists that go stale immediately.

---

## Part 2: Revised Architecture

### Design Principles

1. **Supabase is the source of truth** — All dynamic state lives there. Local files are caches/indexes.
2. **Enforce, don't document** — If a rule matters, automate it via hooks/skills. If it can't be automated, it's guidance, not a rule.
3. **One agent, many tools** — Claude Code is one well-structured agent. Specialized behavior = custom skills (invocable prompts). Real multi-agent = Task tool subagents + n8n workflows.
4. **Context is finite** — Build checkpoint/save protocols into every multi-step plan.
5. **Simplicity over completeness** — 5 enforced rules beat 30 aspirational ones.
6. **Build for AIOS portability** — Every architecture decision here becomes the AIOS template. Abstract data layers so backends can swap without code rewrites.
7. **Claude Code → n8n bridge** — Claude Code handles planning, building, and direct work. n8n handles automation, background workflows, and multi-agent orchestration. Shared Supabase database = the bridge. No information gaps between systems.
8. **Platform awareness is continuous** — Claude Code releases features fast. Morning brief includes a platform update check. New capabilities get evaluated before the workday starts. If a new feature makes planned work easier, adapt the plan.
9. **Plans are persistent and multi-day aware** — Every plan lives in `knowledge-base/projects/<name>/plan.md` (NOT just `.claude/plans/`). Multi-day plans include daily breakpoints. The briefing system knows which phase is active and schedules today's portion.

### CLAUDE.md (Target: 200-250 lines)

Keep ONLY:
- Project purpose (3 lines)
- How to operate (10 lines — tools first, follow workflows, verify, memory mandatory)
- Non-negotiables (5 rules, each enforceable)
- Task protocols (pre/post checklists, simplified)
- Checkpoint protocol (context management)
- File structure reference (table)
- Environment summary (credentials, integrations)

Remove:
- Entire workforce governance section (16-agent hierarchy, chain of command, delegation rules) — this model is being eliminated
- Instantiation/bootstrap sections — already done
- Agent identity protocol — no more agent folders
- C-Suite department structure — not how Claude Code works
- Detailed non-negotiables 1-12 — replace with 5 enforced ones

### MEMORY.md (Target: 100-130 lines)

Keep ONLY:
- Active rules (pruned to ~15 that are ACTUALLY enforced or directly useful)
- Project queue (10 projects, 1 line each — detail lives in Supabase)
- Environment config (credentials, paths, versions — reference only)
- Memory file index (links to topic files)

Move OUT:
- Process Improvement Table → Supabase `audit_log` or `memories`
- Key Decisions (all 30+) → Supabase `memories` table with tag "decision"
- Workforce hierarchy → eliminated (one agent model)
- Project structure tree → CLAUDE.md (static)
- Operating Rhythm Calendar → Supabase (Task Scheduler updates Supabase directly)

### 5 Enforced Non-Negotiables (replacing 12)

1. **SUPABASE IS TRUTH** — All project/task/decision state lives in Supabase. Local files are read-only caches. When in doubt, query Supabase.

2. **CHECKPOINT BEFORE CONTEXT LIMIT** — Every multi-step plan includes checkpoint markers. At each checkpoint: update MEMORY.md + push critical state to Supabase + signal "safe to compact." Plans estimate context usage and create stopping points at ~60% consumption.

3. **VERIFY BEFORE PRESENTING** — Never present data without stating the source and reading it directly. No secondary references. No assumptions.

4. **PUSH BACK ON PLATFORM LIMITS** — If what's being asked can't be done well on this platform, say so immediately. Offer alternatives. Never pretend something works when it doesn't.

5. **CHANGE = PROPAGATE** — When any config, reference, or state changes: update the code AND Supabase in the same action. The midnight audit catches drift, but the rule is: propagate at time of change.

### Agent Folder Strategy (THREE outputs, not just archive)

**Current:** 16 folders, 80 files (ROLE.md, KNOWLEDGE.md, OPERATIONS.md, MEMORY.md, SKILLS.md per agent)

**Action — Triple Output:**

**Output 1: Supabase Migration**
- Export each agent's content to Supabase `memories` table with structured tags (agent_name, content_type: role/knowledge/operations/skills)
- This content = starting blocks for n8n workforce build AND reference for custom skill creation

**Output 2: Custom Skill Specs (ALL 16 agents)**
- For each agent, produce a detailed skill specification document
- Spec includes: role definition, domain expertise, decision frameworks, tools/capabilities, escalation rules, example interactions
- These specs go to Chris's other project folder (skill builder) to create real invocable skills
- Priority tiers: Tier 1 (build immediately) = Marcus, Orion, Felix, Vera, Sage, Sterling | Tier 2 = Atlas, Cleo, Axiom, Lex | Tier 3 (n8n only) = Node, Vantage, Echo, Quill, Scout
- Skills replace the "pretend to be agent" pattern with real, invocable specialized behavior

**Output 3: Archive**
- Move folders to `_archive/agents/` (not deleted — reference available)
- Remove all agent-related governance from CLAUDE.md and MEMORY.md

**Result:** 80 files eliminated from active maintenance. Content preserved in Supabase. Skill specs ready for builder project. Agent definitions available for n8n workforce.

### Context Management Protocol (NEW)

**Problem:** Context runs out mid-task. Compaction loses unsaved state. No guardrails.

**Solution — Three-layer approach:**

**Layer 1: Checkpoint Protocol (during work)**
- Every plan with 3+ steps includes checkpoint markers
- At each checkpoint: (1) update MEMORY.md with current progress, (2) push task/project state to Supabase, (3) write progress note to plan file
- Estimated context usage per step noted in plan
- At ~60% context usage: mandatory checkpoint + "safe to compact" signal
- After compaction: read MEMORY.md + query Supabase to restore state

**Layer 2: Session State in Supabase (across sessions)**
- `sessions` table (currently 1 row, underutilized) becomes the session continuity mechanism
- On session start: create session record with goals, context
- During session: update with decisions, progress, blockers
- On session end (or checkpoint): save full state snapshot
- On new session: query latest session record to restore context

**Layer 3: Plan Files as Continuity Documents (across compactions)**
- Active plan files (`knowledge-base/projects/<name>/plan.md`) include a "Current State" section
- Updated at every checkpoint
- After compaction, the plan file tells the next context window exactly where we are
- Plan files are the handoff document between context windows

**Guardrails:**
- Hook (pre-compact): auto-save current task state to Supabase
- MEMORY.md progress markers: `## Current Work: [task] — Step X/Y — [timestamp]`
- Plan files include `## Checkpoint Log` section with timestamped entries

### Memory Architecture (Abstraction-Ready)

**Design principle:** Build with an abstraction layer. Today it uses Supabase pgvector. Tomorrow it can swap to Pinecone/Weaviate without changing calling code. This is the AIOS-portable pattern.

| Layer | What | Where (Today) | Future AIOS Option | Updated By |
|-------|------|---------------|-------------------|-----------|
| Hot | Session state, active rules, project queue | MEMORY.md (<150 lines) | Same (local project file) | Claude Code (every checkpoint) |
| Warm | Decisions, patterns, agent defs, session history | Supabase `memories` (428+ rows, pgvector) | Pinecone (serverless, per-client namespace) OR keep pgvector | Claude Code (push at checkpoints) |
| Cold | Business docs, SOPs, reference material | Supabase `kb_docs` (1,348 chunks, pgvector) | Pinecone (dedicated index) OR keep pgvector | seed_supabase.py (hourly sync) |
| Operational | Tasks, projects, escalations, audit findings | Supabase tables (structured, no vectors) | Supabase (always — this is relational data) | Claude Code + Task Scheduler + n8n |

**Why this works for AIOS:**
- Each client gets their own Supabase project (operational data + optional pgvector)
- If vector scale demands it, add Pinecone with per-client namespaces alongside Supabase
- Chris's master AIOS queries across all client Supabase instances for dashboards
- n8n workflows read from same Supabase → webhook triggers when data arrives
- Cloud-based = accessible from any computer with the project folder

**Memory architecture research** happens in Phase 2 of execution (below). Output = decision document stored in `knowledge-base/projects/aios-vision-definition/memory-architecture.md`.

### Gaps Requiring Custom Skills/Hooks/Plugins (NEW)

**Currently missing — to be built by Chris's skill-builder project folder:**

**Hooks (automated enforcement — run before/after tool calls):**
1. **MEMORY.md line limiter** — Pre-Edit hook: reject edits that push MEMORY.md over 150 lines
2. **CLAUDE.md line limiter** — Pre-Edit hook: reject edits that push CLAUDE.md over 300 lines
3. **Checkpoint reminder** — Periodic hook: at ~60% context usage, emit "checkpoint recommended" signal
4. **Session state auto-save** — Post-session hook: push session summary to Supabase `sessions` table
5. **Cross-reference validator** — Post-Edit hook on KB files: verify DOCUMENT-MAP.md and INDEX.md still match filesystem

**Custom Skills (invocable specialized behavior — replace "agent pretend" pattern):**
- All 16 agent skills specified in Phase 5 of execution plan
- Priority: Tier 1 = Marcus, Orion, Felix, Vera, Sage, Sterling (daily use)
- Tier 2 = Atlas, Cleo, Axiom, Lex (periodic use)
- Tier 3 = Node, Vantage, Echo, Quill, Scout (n8n workforce primarily)

**Plugins (if gaps exist after skills):**
- To be evaluated after skill specs are produced — may not need any custom plugins
- Existing 51 plugins + 138 skills cover most general needs

**Detailed specs for ALL of the above** are produced in Phase 6 of execution and packaged as a deliverable for the skill-builder project folder.

### Claude Code Channels — Impact Analysis (NEW)

**What it is:** Native two-way communication between Telegram (or Discord/iMessage) and a running Claude Code session. Not an n8n bot — this is Claude Code itself receiving messages and responding.

**How it works:**
1. Install plugin: `/plugin install telegram@claude-plugins-official`
2. Configure: `/telegram:configure <BOT_TOKEN>` (can use existing HQ bot or create dedicated channel bot)
3. Launch with channels: `claude --channels plugin:telegram@claude-plugins-official`
4. Pair account: `/telegram:pair` → links Telegram user to Claude Code session
5. Two-way: Chris sends message in Telegram → arrives as event in Claude Code session. Claude Code can reply back through the channel.
6. Permission relay: tool use approvals can be done from Telegram (approve/deny from phone).

**Impact on current architecture:**
- **n8n interactive bot**: Channels does PART of what the n8n bot does (conversational interaction). BUT n8n bot runs 24/7 independently. Channels requires an open Claude Code session. These are COMPLEMENTARY, not replacements.
  - Channels = direct Claude Code interaction when session is running (planning, building, direct work)
  - n8n bot = always-on workforce access (task queries, status checks, quick actions even when Claude Code is closed)
- **Remote Control + Dispatch**: Combined with Channels, Chris can: (a) start sessions from phone, (b) communicate via Telegram during sessions, (c) approve tool use from phone. This is the mobile-first workflow Chris described for AIOS.
- **Cloud Scheduled Tasks**: If stable, could REPLACE local Windows Task Scheduler for briefs. Runs on Anthropic infra = works when computer is off. Evaluate during AIOS build.
- **Agent SDK**: Could replace some n8n workforce workflows with native Claude Code agents. Evaluate during UAW rebuild.

**Decision for today:** Document and spec. Do NOT implement Channels yet (it's research preview). Add it to the builder deliverable as a high-priority evaluation item. The current Telegram setup (HQ bot via Python scripts + n8n bot reference) continues as the stable path. Channels becomes the upgrade path when it exits preview.

### Claude Code Documentation Monitoring (NEW)

**Problem:** Claude Code releases features rapidly. We missed Channels, Cloud Tasks, Remote Control, Desktop App, and Agent SDK — all directly relevant to our workflow. These could have saved significant development effort if caught early.

**Solution — Three-tier monitoring:**

**Tier 1: Morning Brief Integration (implement now)**
- Add `check_claude_code_updates()` to `audit_checks.py`
- Uses Firecrawl (already available, API key in .env) to scrape `https://code.claude.com/docs/en/overview` changelog section
- Compares against stored hash/version in Supabase
- If changes detected: surfaces in morning brief System Health section
- Report-by-exception: only shows up when something NEW exists

**Tier 2: n8n Automation (implement during UAW)**
- n8n workflow: daily Firecrawl scrape of Claude Code docs (overview, changelog, core concepts)
- Diff detection → Supabase insert with category tags
- Could extend to monitor other tool docs (n8n releases, Supabase updates, etc.)

**Tier 3: Feature Database (implement during AIOS)**
- Supabase table: `platform_features` — name, status (preview/stable/deprecated), documentation_url, impact_assessment, date_discovered
- Becomes the AIOS platform awareness layer — each client installation knows what features are available
- Cross-references with installed skills/plugins to identify gaps

**For today's restructure:** Tier 1 spec goes into the builder deliverable. Brief enhancement spec included. Implementation during Phase 7 if time permits, otherwise documented for next session.

### Plan Persistence & Multi-Day Scheduling (NEW)

**Problem:** Plans in `.claude/plans/` are ephemeral. Multi-day work has no mechanism to break into daily chunks. The briefing system doesn't know where in a multi-day plan we are.

**Solution:**

**Plan persistence (already partially solved):**
- Plans ALWAYS saved to `knowledge-base/projects/<name>/plan.md` (this rule exists but isn't always followed)
- `.claude/plans/` files are working copies only — the KB version is the source of truth
- Each plan includes a `## Checkpoint Log` section with timestamped entries
- Each plan includes a `## Daily Breakpoints` section that maps phases to calendar days

**Multi-day briefing integration:**
- `extract_daily_tasks()` in `audit_checks.py` already filters by active project + current phase
- Enhancement: when a plan has `Daily Breakpoints`, the brief pulls ONLY today's breakpoint tasks
- Haiku synthesis prompt updated to reference the breakpoint context: "You are on Day X of Y for this project. Today's focus: [breakpoint description]"
- Evening brief reports progress against today's breakpoint, previews tomorrow's

**For today's restructure:** Add `## Daily Breakpoints` section to THIS plan. Update all 10 project plans during the project plan reorganization phase.

### Project Plan Reorganization (NEW)

**Problem:** 10 projects in the queue, but plan quality varies. Some have detailed plans, some have stubs. Priorities may have shifted based on new Claude Code capabilities.

**Solution — Add to execution plan:**
- Review all 10 project plans in `knowledge-base/projects/<name>/plan.md`
- For each: verify plan structure (phases, tasks, estimated_minutes, dependencies, breakpoints)
- Re-evaluate priority order based on:
  - New Claude Code features (Channels, Cloud Tasks, Agent SDK impact)
  - Dependency chains (unchanged: if B depends on A, A ranks higher)
  - Client revenue priority (SystemLink still #1 when unblocked)
- Ensure Supabase `projects` table matches updated priorities
- Ensure every project has a properly structured plan ready for execution

**This happens in Phase 9 (expanded from just "final state" to include project plan review).**

### Claude Code vs n8n — Capability Analysis & Workforce Simplification (NEW)

**The question Chris is asking:** Do I need a 16-agent workforce in n8n? Or can Claude Code (with custom skills, multiple project folders, and Task tool subagents) handle most of the work — leaving n8n for only what genuinely needs to run 24/7?

**The answer: You do NOT need 16 agents in n8n.** The decision framework is simple:

**The one question that decides where work lives:**
> "Does this need to run when no Claude Code session is open?"
> - YES → n8n workflow (or Cloud Scheduled Tasks when stable)
> - NO → Claude Code (this project folder, or a purpose-built one)

**Claude Code strengths (verified in this project):**
- All planning, reasoning, analysis, research, writing, complex decision-making
- Building n8n workflows via API (Chris does this from another project folder right now)
- Building code, scripts, automations, documents
- Direct MCP access to Gmail, Calendar, Supabase, Slack, Notion, GitHub, etc.
- Task tool subagents for real parallel specialized work (35+ agent types)
- Custom skills for specialized behavior (what the 16 agents SHOULD become)

**Claude Code limitations (hard limits, not fixable with skills):**
- Session-bound — must have an open session to work
- Cannot respond to webhooks in real-time 24/7
- Cannot monitor email/calendar continuously in background
- Cannot run concurrent independent processes
- Context window degrades over very long sessions
- (Cloud Scheduled Tasks MAY address some of this — evaluate when stable)

**n8n strengths (things Claude Code genuinely cannot do):**
- Always-on 24/7 — works when computer is off, when no session is running
- Webhook-triggered instant responses (new email → immediate action)
- Reliable cron scheduling for repetitive tasks
- Multi-workflow concurrent execution
- Simple automations that don't need heavy reasoning

**Capability mapping — where each role actually belongs:**

| Role | n8n Agent? | Why / What Instead |
|------|-----------|-------------------|
| Alex (assistant) | **YES — the only full agent** | Always-on: email monitoring, calendar, scheduling, task management, quick lookups. This is the personal assistant that runs 24/7. |
| Marcus (routing) | NO | Routing = a Claude Code skill. Invoke `/marcus` to route tasks. No 24/7 need. |
| Atlas (operations) | NO | Operations planning = reasoning-heavy. Claude Code skill. |
| Sterling (finance) | NO | Financial analysis = reasoning-heavy. Claude Code skill. |
| Vera (brand) | NO | Brand review = reasoning-heavy. Claude Code skill. |
| Cleo (marketing) | PARTIAL | Strategy = Claude Code skill. Lead gen automation = n8n workflow (runs on schedule). |
| Orion (tech) | NO | All building happens in Claude Code project folders. |
| Felix (revenue) | PARTIAL | Client strategy = Claude Code skill. CRM automation = n8n workflow. |
| Sage (knowledge) | NO | Knowledge management = file-based. Claude Code's domain. |
| Axiom (strategy) | NO | Pure reasoning. Claude Code skill. |
| Lex (legal) | NO | Pure reasoning. Claude Code skill. |
| Node, Vantage, Echo, Quill | NO | Orion's workers. Claude Code + Task tool subagents replace all of them. |
| Scout | PARTIAL | Market research = Claude Code. Automated lead scraping = n8n. |

**DEEPER ANALYSIS (Chris's push: "Do I even need n8n at all?")**

**Answer: Almost not at all. n8n's ONLY irreplaceable function is persistent webhook endpoints.**

When QuickBooks sends a webhook saying "a check was created," something needs to receive that POST request 24/7. That receiver needs a persistent URL, to be running when the computer is off, and to process data immediately. That's n8n. Claude Code cannot listen for incoming webhooks. Task Scheduler cannot receive HTTP requests.

**Where n8n is genuinely irreplaceable:**
- Client delivery workflows (the PRODUCT Sharkitect sells): SystemLink, ERA, future client automations
- These process external webhook events from client systems (QBO, Monday.com, etc.)
- This is it. This is the ONLY thing n8n does that nothing else can.

**Where n8n is NOT needed (replacements already exist or can be built):**
- Morning briefs → Task Scheduler (ALREADY WORKING)
- Email checking → Task Scheduler + Python polling script (not webhook — POLL on schedule)
- Calendar management → MCP during Claude Code sessions
- Lead gen → Task Scheduler + Python scripts on schedule
- Alex personal assistant → Claude Code session + Channels (when stable) for always-on interaction
- System monitoring → Task Scheduler + Python health checks
- All planning, strategy, analysis, building → Claude Code

**The three-level architecture:**

```
LEVEL 1 — Claude Code (where ALL reasoning + direct work lives):
  HQ folder: operations, planning, audits, strategy, building
  Additional purpose-specific folders as needed (lead gen, client work, etc.)
  Custom skills: replace all 16 "agents" with invocable specialized behavior
  Task Scheduler: runs Python scripts on schedule (briefs, syncs, audits, monitoring)
  Channels (future): Telegram/iMessage for communicating with HQ folder sessions
  Cloud Scheduled Tasks (future): replace Task Scheduler — runs on Anthropic infra

LEVEL 2 — n8n (Alex + client delivery):
  Alex: always-on personal assistant — email, calendar, scheduling, task management
    → Future evolution: voice-activated AI assistant (Jarvis-style phone/voice interaction)
    → Needs to run 24/7 without a Claude Code session open
    → Channels can't replace this (requires running session)
  Client delivery workflows: SystemLink, ERA, future client automations
    → These are what Sharkitect SELLS. Webhook-triggered, always-on.

LEVEL 3 — Supabase (the shared brain):
  All folders + n8n + Task Scheduler read/write same database
  Source of truth for state, memory, tasks, projects, audit logs
  Cloud-accessible from any device, any location
```

**What this eliminates vs original plan:**

| What We Planned | Status | Replacement |
|----------------|--------|-------------|
| 16-agent n8n workforce | **ELIMINATED** | Claude Code custom skills |
| Alex n8n bot (always-on assistant) | **KEPT** | Alex STAYS in n8n — needs to be always-on without a running session. Future: voice-activated AI assistant (Jarvis-style phone call interaction). Channels is for HQ folder communication, NOT Alex replacement. |
| n8n for lead gen | **ELIMINATED** | Claude Code folder + Task Scheduler scripts |
| n8n for email monitoring | **ELIMINATED** | Task Scheduler + Python polling script |
| n8n for system monitoring | **ELIMINATED** | Task Scheduler (already does this) |
| n8n for reporting | **ELIMINATED** | Task Scheduler + Python report scripts |
| n8n for client delivery (SystemLink, ERA) | **KEPT** | Irreplaceable — webhook endpoints |

**Multi-device portability (traveling laptop):**
1. Memory/state → Supabase (cloud, accessible from anywhere)
2. Project files → Google Drive or similar cloud sync
3. Claude Code → Installed on both machines, same `.env` from Bitwarden
4. Skills → Installed globally per machine (same set on both)
5. Channels → Communicate with sessions from phone regardless of which laptop is running
6. Only machine-specific thing = `.env` credentials → Bitwarden solves this

**Multi-folder strategy:**

Multiple Claude Code project folders = different persistent contexts. All connected via shared Supabase.

| Folder | Purpose | Why Separate |
|--------|---------|-------------|
| **HQ** (this folder) | Operations center: planning, audits, briefings, strategy | Core operations context |
| **Builder** (exists) | n8n workflow construction, code builds | Build context separate from operations |
| **Lead Gen** (potential) | Prospect research, outreach strategy, campaign planning | Needs its own persistent ICP/prospect context |
| **Client Delivery** (potential) | Per-client project execution | Client-specific context (FF, future clients) |
| **Website/Brand** (potential) | Website updates, content creation, SEO | Creative context separate from technical |

Each folder has its own MEMORY.md (folder-specific context) but shares Supabase as common brain. The briefing system in HQ can query Supabase to see what ALL folders have been doing.

**What this means for multi-folder auditing:**
- HQ folder runs the morning brief → queries Supabase for ALL project/task status across folders
- Each folder pushes its work to Supabase (sessions, tasks, decisions)
- HQ is the "auditor" folder — it sees everything via Supabase
- No need for a separate "audit folder" — HQ already does this

**AIOS impact (dramatic simplification):**
- Client AIOS = ONE Claude Code project folder + Supabase + 2-3 n8n delivery workflows (the product)
- No "workforce" per client — just Claude Code skills + scheduled scripts
- Dramatically simpler, cheaper, and more maintainable
- Fewer moving parts = fewer things to troubleshoot = faster to deploy

**Impact on current plan:**

1. **Phase 5B (Skill Specs)** — ALL 16 become Claude Code skills. No "n8n-only" tier. Each spec includes platform recommendation (Claude Code skill vs n8n delivery workflow).
2. **UAW project (#4 in queue)** — Scope changes fundamentally: from "16-agent workforce" to "client delivery workflows only." Rename consideration: "Client Delivery Automations" instead of "Unified AI Workforce."
3. **AIOS vision** — Simplified deployment model. One Claude Code folder + Supabase + minimal n8n = complete client installation.
4. **Phase 9 (Project Plan Reorg)** — UAW plan must be completely rewritten. May merge with or become part of AIOS project.

**Decision for today:** This analysis goes into the platform capabilities document (Phase 9B). The UAW plan gets rewritten during Phase 9A. All skill specs in Phase 5B use the new platform framework. No structural change to today's execution phases — the analysis informs the outputs.

---

## Part 3: Execution Plan (TODAY)

### Phase 1: Retrospective Document — THIS PLAN
You're reading it. This IS the retrospective Chris asked for.

### Phase 2: Memory Architecture Research (30 min)
**Goal:** Produce an informed architecture decision document before restructuring.
- Research Supabase pgvector vs Pinecone vs Weaviate vs Qdrant for AIOS use case
- Evaluate: cost at scale, multi-tenant support, cross-device access, n8n integration, client isolation
- Decision criteria: What works NOW (this project) + what scales for AIOS (50+ clients)
- **Output:** `knowledge-base/projects/aios-vision-definition/memory-architecture.md`
- **Decision for TODAY's restructure:** Use Supabase pgvector with abstraction layer (swap-ready)
- **Checkpoint: decision document written, architecture choice confirmed**

### Phase 3: Slim CLAUDE.md (30 min)
- Read current CLAUDE.md (347 lines)
- Remove: workforce governance, agent identity protocol, C-Suite structure, delegation hierarchy, 12 non-negotiables (replace with 5)
- Keep: project purpose, how to operate, task protocols (simplified), file structure, environment
- Add: checkpoint protocol, simplified non-negotiables, AIOS portability note
- Remove: instantiation/bootstrap sections (already done)
- Target: 200-250 lines
- **Checkpoint: verify CLAUDE.md loads clean, line count under 250**

### Phase 4: Slim MEMORY.md (30 min)
- Move Key Decisions to Supabase `memories` (tag: decision)
- Move Process Improvement Table to Supabase `memories` (tag: process_fix)
- Remove workforce hierarchy section
- Remove Operating Rhythm Calendar (move to Supabase)
- Prune Active Rules to ~15 actually enforced ones
- Condense project queue to 1 line each
- Target: 100-130 lines
- **Checkpoint: verify MEMORY.md loads clean, under 150 lines, no truncation**

### Phase 5: Migrate Agents + Produce Skill Specs (60 min)
**This is the triple-output phase — Supabase migration, skill specs, archive.**

**5A: Supabase Migration (20 min)**
- For each of 16 agents: read ROLE.md + KNOWLEDGE.md + OPERATIONS.md + MEMORY.md + SKILLS.md
- Insert into Supabase `memories` table with structured tags: `agent:<name>`, `content_type:<role|knowledge|operations|memory|skills>`
- Verify content accessible via REST API

**5B: Custom Skill Specification Documents (30 min)**
- For ALL 16 agents, produce a skill spec document containing:
  - Skill name and invocation command (e.g., `/cto` for Orion)
  - Role definition (what this skill does when invoked)
  - Domain expertise and decision frameworks
  - Tools/capabilities the skill should leverage
  - Escalation rules (when to hand off to a different skill or back to the user)
  - Example interactions (2-3 per skill)
  - Priority tier: 1 (build as Claude Code skill immediately), 2 (build as Claude Code skill soon), 3 (evaluate: Claude Code skill vs n8n workflow vs hybrid — based on 24/7 requirement)
  - Platform recommendation: Claude Code skill, n8n workflow, or hybrid (per capability analysis)
- **Output:** `knowledge-base/projects/aios-vision-definition/skill-specs.md`
- This document is the DELIVERABLE for Chris's skill-builder project folder
- **NEW:** Each spec now includes a "Platform" field indicating whether the agent's capabilities belong in Claude Code, n8n, or both — based on the "Does this need to run 24/7?" framework

**5C: Archive + Code Updates (10 min)**
- Move agent folders to `_archive/agents/`
- Update `tools/audit/config.py` — modify agent-dependent checks to query Supabase or skip gracefully
- Update `tools/audit/audit_checks.py` — functions that read agent MEMORY.md files need graceful handling
- Remove all agent-related governance from CLAUDE.md and MEMORY.md
- **Checkpoint: all 16 agents in Supabase, skill specs document complete, folders archived, no broken code**

### Phase 6: Gap Analysis — Hooks/Skills/Plugins Spec (30 min)
**Goal:** Produce a complete specification document for Chris's skill-builder project folder.

**6A: Hook Specifications**
- For each hook identified in the architecture section: detailed spec (trigger, logic, error handling, installation instructions)
- Hooks: MEMORY.md limiter, CLAUDE.md limiter, checkpoint reminder, session auto-save, cross-reference validator

**6B: Skill Build Priorities**
- Summarize the 16 skill specs from Phase 5B into a prioritized build queue
- Include any additional skills identified during restructure
- Note which existing skills/plugins partially cover the gap (may just need configuration, not building)

**6C: Plugin/Integration Gaps**
- Review current 51 plugins against actual needs post-restructure
- Identify any gaps that require custom plugins
- Note: many "gaps" may actually be solved by skills alone

**Output:** `knowledge-base/projects/aios-vision-definition/builder-deliverable.md`
- Self-contained document that Chris's other project folder can use independently
- Includes: all hook specs, all skill specs (or link to skill-specs.md), plugin recommendations, priority order
- **Checkpoint: deliverable document complete, ready for handoff**

### Phase 7: Configure Basic Hooks (15 min)
- Hooks that CAN be configured now within Claude Code's native hook system:
  - MEMORY.md line count enforcement (pre-Edit)
  - CLAUDE.md line count enforcement (pre-Edit)
- Hooks that need the builder project folder: checkpoint reminder, session auto-save, cross-reference validator
- Configure what we can. Document what needs building.
- **Checkpoint: basic hooks tested, working**

### Phase 8: Verify Everything (15 min)
- Run morning brief dry run — verify it produces accurate output with new structure
- Query Supabase — verify agent content migrated correctly (spot-check 3-4 agents)
- Read CLAUDE.md — verify it loads clean under 250 lines
- Read MEMORY.md — verify it loads clean under 150 lines
- Verify hooks trigger on file edits
- Verify skill specs and builder deliverable are complete and actionable

### Phase 9: Project Plan Reorganization + Final State (30 min)
**Expanded from original "final state" — now includes full project plan review.**

**9A: Review All 10 Project Plans (20 min)**
- Read each `knowledge-base/projects/<name>/plan.md`
- For each project, verify/create:
  - Clear phase structure with tasks and estimated_minutes
  - `## Daily Breakpoints` section (for multi-day plans)
  - `## Checkpoint Log` section
  - Dependencies on other projects explicitly noted
  - Current status accurately reflected
- Re-evaluate priority order considering:
  - New Claude Code capabilities (Channels, Cloud Tasks, Remote Control, Agent SDK)
  - Claude Code vs n8n capability analysis (what belongs where?)
  - Does any feature make a project easier/faster/unnecessary?
  - Does any feature create a NEW project or modify an existing one?
- **CRITICAL:** Rewrite UAW plan to reflect simplified scope (5-8 purpose-built workflows, NOT 16 agent simulations)
- For each project: determine if it's a Claude Code project folder task, an n8n automation, or hybrid
- Update Supabase `projects` table with any priority/status changes
- Seed any new/modified tasks to Supabase via `seed_plan_to_supabase.py`

**9B: Claude Code Platform Assessment Document (5 min)**
- Create `knowledge-base/projects/aios-vision-definition/platform-capabilities.md`
- Document ALL discovered Claude Code features with status (preview/stable), impact assessment, and evaluation timeline
- This becomes the reference for AIOS architecture decisions

**9C: Final State Sync (5 min)**
- Update project statuses in Supabase to match reality
- Create session record documenting this restructure
- Update MEMORY.md with new project state
- Push all changes to Supabase via sync
- Save this retrospective plan to `knowledge-base/projects/aios-vision-definition/restructure-retrospective.md` (permanent copy)
- **Final checkpoint: everything consistent, ready for next session**

### Time Estimate: ~4.5 hours total
Phase 1: Done (this plan)
Phase 2: 30 min (memory research)
Phase 3: 30 min (CLAUDE.md)
Phase 4: 30 min (MEMORY.md)
Phase 5: 60 min (agents → Supabase + skill specs + archive)
Phase 6: 30 min (gap analysis deliverable — now includes Channels spec + doc monitoring spec)
Phase 7: 15 min (hooks)
Phase 8: 15 min (verification)
Phase 9: 30 min (project plan reorganization + platform assessment + final state)

**Context management:** Natural compaction points between Phase 4→5 (MEMORY.md done) and Phase 6→7 (specs done). I'll signal "safe to compact" at each.

### Daily Breakpoints (if work spans multiple sessions)

| Day | Phases | Focus | Briefing Context |
|-----|--------|-------|-----------------|
| Day 1 | 1-4 | Retrospective + restructure core files (CLAUDE.md, MEMORY.md) | "Restructure Day 1: core files slimmed, architecture established" |
| Day 2 | 5-6 | Agent migration + skill specs + gap analysis | "Restructure Day 2: 16 agents migrated, all specs produced" |
| Day 3 | 7-9 | Hooks + verification + project plan reorg | "Restructure Day 3: enforcement active, all plans organized, system verified" |

If completed in one session: great. If not, the briefing system picks up at the correct breakpoint.

---

## Part 4: How This Feeds AIOS

This restructured workspace IS the AIOS pilot. Every architecture decision here becomes the template.

### What This Restructure Produces for AIOS

| Component Built Today | AIOS Role |
|----------------------|-----------|
| Clean CLAUDE.md (200-250 lines) | AIOS bootstrap instructions — what every client installation starts with |
| Supabase schema (8 tables) | AIOS data layer — each client gets their own Supabase project with same schema |
| Briefing pipeline | AIOS reporting engine — daily audits, insights, recommendations per client |
| Task Scheduler config | AIOS automation layer — runs without client intervention |
| Agent definitions in Supabase | AIOS agent routing — n8n reads these to route tasks to correct workflow |
| Custom skill specs | AIOS skill library — auto-installed per client based on their industry/needs |
| Checkpoint protocol | AIOS session management — no lost context, ever, any device |
| Memory architecture document | AIOS data strategy — cloud-first, multi-device, multi-tenant |
| Hook specifications | AIOS enforcement layer — automated guardrails per installation |
| Builder deliverable package | AIOS build instructions — what the builder project folder needs to create |
| Platform capabilities document | AIOS feature matrix — which Claude Code features each client installation uses |
| Project plan templates (10 plans, all structured) | AIOS project management — every client project follows same plan structure |
| Claude Code vs n8n capability analysis | AIOS deployment model — what lives in Claude Code vs n8n per client. Simplifies from 16-agent workforce to 5-8 purpose-built workflows. |
| Multi-folder strategy | AIOS scaling pattern — separate Claude Code folders for different concerns, all sharing Supabase brain |

### AIOS Architecture (Chris's Vision — Clarified)

**Client AIOS (installed on client computer) — MAXIMUM SIMPLICITY MODEL:**
```
Client PC → Claude Code project folder (bootstrapped from AIOS template)
  → Bootstrap: analyze client's tool stack, create Supabase project, install skills
  → Onboarding: capture business info, preferences, goals, daily rhythm
  → Operation: daily audits, insights, task tracking, efficiency recommendations
  → Skills: custom Claude Code skills for ALL reasoning/analysis/planning work
  → Memory: Supabase (cloud, accessible from any device)
  → Task Scheduler: briefs, monitoring, scheduled checks (Python scripts)
  → n8n: ONLY client-specific delivery automations (the product Sharkitect sells them)
  → Channels (future): client communicates with their AIOS via Telegram/iMessage
```

**Chris's Master AIOS — MAXIMUM SIMPLICITY MODEL:**
```
Chris's PC → Claude Code project folders + Supabase + minimal n8n
  → HQ folder: operations, planning, audits, briefings, strategy (this workspace)
  → Builder folder: n8n workflow construction, code builds
  → Additional folders as needed: lead gen, client delivery, etc.
  → Task Scheduler: morning briefs, monitoring, syncs, scheduled checks
  → Channels (future): Telegram/iMessage communication with any running session
  → n8n: ONLY client delivery workflows (SystemLink, ERA — the product)
  → Supabase: shared brain across ALL folders + n8n + Task Scheduler
  → Cross-client: HQ queries all client Supabase instances for dashboards
  → Pipeline: Claude Code plans + builds → n8n delivers to clients
```

**The bridge (Claude Code ↔ n8n):**
- Shared data layer: both systems read/write same Supabase tables
- Claude Code = planning, building, direct interaction with Chris
- n8n = automation, background workflows, multi-agent execution, webhook triggers
- When Claude Code can't do something (persistent background processes, multi-agent orchestration): handoff to n8n with full context via Supabase
- When n8n needs something built or planned: it queues a task in Supabase for Claude Code session

**Multi-device portability:**
- Project folder synced via Google Drive (or similar)
- All memory in cloud (Supabase) — local MEMORY.md is just an index/cache
- Skills installed globally per machine — same skill set on any computer
- .env credentials = only machine-specific component (stored in Bitwarden for portability)

**NEW: Claude Code native capabilities that reshape AIOS (March 2026):**

| Feature | AIOS Impact | Status |
|---------|-------------|--------|
| **Channels (Telegram)** | Chris communicates with ANY running session from phone. Client AIOS sessions could push updates to client's preferred channel. | Research preview |
| **Cloud Scheduled Tasks** | Briefs, audits, monitoring run on Anthropic infra — no local computer needed. Client AIOS works even if client's PC is off. | Evaluate stability |
| **Remote Control** | Continue any session from phone/browser. Chris manages multiple client sessions remotely. | Available |
| **Dispatch** | Message from phone → creates desktop session. Chris initiates work without being at desk. | Available |
| **Agent SDK** | Build custom agents (e.g., "Sharkitect Onboarding Agent") as distributable packages. Client AIOS bootstrap could be an SDK agent. | Evaluate |
| **Desktop App** | Multiple simultaneous sessions. Chris manages HQ + client sessions side-by-side. | Available for Windows |

**Revised communication architecture:**
```
CURRENT (what works today):
  Task Scheduler → Python scripts → Telegram HQ bot (one-way: briefs out)
  n8n bot reference → Telegram Alex bot (two-way: conversational, always-on)

NEAR FUTURE (when Channels exits preview):
  Claude Code session + Channels → Telegram (two-way: direct session interaction)
  n8n bot → Telegram (two-way: always-on workforce access when no session running)
  Cloud Scheduled Tasks → briefs (no local Task Scheduler needed)

BOTH coexist — Channels for live sessions, n8n bot for always-on access.
```

---

## Part 5: What This Does NOT Do (Yet)

- Does NOT build the AIOS product (that's the next project, using deliverables from this restructure)
- Does NOT rebuild the n8n workforce (UAW scope FUNDAMENTALLY CHANGED: from 16-agent workforce to client delivery workflows only. n8n = the product Sharkitect sells, NOT internal operations. Plan rewritten in Phase 9A. May rename project.)
- Does NOT change the briefing system's code (it works — the issue was the data it reads, not the code)
- Does NOT set up Pinecone or alternative vector DBs (research and decision doc only — implementation during AIOS build)
- Does NOT build the custom skills themselves (produces SPECS that Chris's builder project folder implements)
- Does NOT build advanced hooks (produces SPECS — basic hooks configured, advanced ones built by builder project)
- Does NOT set up the Claude Code ↔ n8n bridge (architecture documented, implementation during AIOS/UAW)
- Does NOT set up multi-device sync (architecture noted, implementation when Chris needs second computer)
- Does NOT install Claude Code Channels (research preview — spec only, evaluate when stable)
- Does NOT migrate to Cloud Scheduled Tasks (evaluate stability first — local Task Scheduler continues)
- Does NOT build the documentation monitoring automation (spec included in deliverable, implementation in next session or n8n build)

**What it DOES produce (deliverables):**
1. Clean, slim CLAUDE.md and MEMORY.md
2. All agent content preserved in Supabase
3. Memory architecture decision document
4. 16 custom skill specifications
5. Hook/plugin gap analysis with detailed specs (now includes Channels evaluation + doc monitoring spec)
6. Builder deliverable package (ready for skill-builder project folder)
7. Working basic hooks (line count enforcement)
8. AIOS vision documentation updated with architecture clarity
9. **NEW:** Platform capabilities document (all Claude Code features assessed)
10. **NEW:** All 10 project plans reviewed, structured, and prioritized
11. **NEW:** Retrospective saved to permanent KB location (not just `.claude/plans/`)
12. **NEW:** Claude Code vs n8n capability analysis (what belongs where, simplified workforce model)
13. **NEW:** Multi-folder strategy document (how to organize Claude Code project folders)
14. **NEW:** UAW plan rewritten — n8n = client delivery only, everything else in Claude Code (eliminates months of unnecessary build work)

---

## Verification Criteria

After execution, ALL of these must be true:
- [ ] CLAUDE.md < 250 lines, loads clean
- [ ] MEMORY.md < 150 lines, loads clean, no truncation
- [ ] All 16 agents' content in Supabase `memories` table (spot-checked)
- [ ] Agent folders archived to `_archive/agents/`
- [ ] Basic hooks configured and enforcing line count limits
- [ ] Morning brief dry run produces accurate output with new structure
- [ ] Supabase project/task data matches reality
- [ ] Checkpoint protocol documented in CLAUDE.md
- [ ] No file references things that don't exist
- [ ] Memory architecture document written (`memory-architecture.md`)
- [ ] 16 skill specs document written (`skill-specs.md`)
- [ ] Builder deliverable package written (`builder-deliverable.md`)
- [ ] `audit_checks.py` handles archived agent folders gracefully (no crashes)
- [ ] AIOS vision project plan updated with architecture clarity from this restructure
- [ ] Platform capabilities document written (`platform-capabilities.md`)
- [ ] All 10 project plans reviewed and structured with Daily Breakpoints
- [ ] Supabase `projects` table priorities re-evaluated against new Claude Code features
- [ ] Retrospective saved permanently to `knowledge-base/projects/aios-vision-definition/restructure-retrospective.md`
- [ ] Claude Code documentation monitoring spec included in builder deliverable
- [ ] Claude Code vs n8n capability analysis included in platform capabilities document
- [ ] Each of 16 skill specs includes "Platform" field (Claude Code / n8n / hybrid)
- [ ] UAW plan rewritten — scope = client delivery workflows only (not workforce)
- [ ] Multi-folder strategy documented with shared Supabase architecture
