# Global Lessons Learned

Cross-project patterns, API limitations, tool quirks, user preferences, and process decisions. Checked by AI at session and phase start to avoid repeating known failures and to apply known preferences.

**Scope:** This file captures GLOBAL knowledge that applies across ALL workspaces. Anything learned in one workspace that would benefit work in another belongs here.

**Categories:**
- **API Limitations** -- Tool/API operations that don't work, with documented workarounds
- **Tool Usage** -- Quirks, timeouts, and non-obvious tool behaviors
- **Platform** -- OS-level issues (encoding, paths, shell differences)
- **Approach** -- "We tried X, Y works better" process discoveries
- **Preferences** -- User communication, workflow, and output preferences
- **Process Decisions** -- Validated workflow choices that should be reused
- **Architecture Direction** -- Standing principles that inform every build decision

**Usage:** At the start of every phase, grep this file for keywords related to the tools/APIs you are about to use. If there is a match, follow the documented solution instead of repeating the failed approach.

---

## API Limitations

### [2026-03-28] api-limitation: Airtable cannot delete tables via API

**Tool:** airtable
**Operation:** delete-table
**Attempted:** DELETE request to /v0/{baseId}/tables/{tableId}
**Error:** 403 Forbidden - "Table deletion is not supported via the API"
**Solution:** Rename tables with "DEPRECATED_" prefix. Add to HUMAN-ACTION-REQUIRED.md for manual deletion via Airtable UI.
**Tags:** airtable, api-limitation, delete, table, manual-action

### [2026-04-05] api-limitation: Airtable cannot create rollup fields via API/MCP

**Tool:** airtable
**Operation:** create-rollup-field
**Attempted:** POST to /v0/{baseId}/tables/{tableId}/fields with type "rollup"; also tried MCP create_field tool
**Error:** UNSUPPORTED_FIELD_TYPE_FOR_CREATE - "Creating rollup fields is not supported at this time"
**Solution:** Provide manual Airtable UI instructions: Open table > Click "+" to add field > Select "Rollup" type > Configure source table, field, and aggregation function. Add to HUMAN-ACTION-REQUIRED.md with specific field name, source table, linked field, rollup field, and aggregation type.
**Manual-Steps:** 1. Open Airtable base in browser. 2. Navigate to the target table. 3. Click "+" at the end of the field headers. 4. Select "Rollup" as field type. 5. Choose the linked record field. 6. Choose the field to rollup from the linked table. 7. Select the aggregation function (SUM, COUNT, etc.). 8. Click "Create field."
**Tags:** airtable, api-limitation, rollup, create_field, field_type, mcp, unsupported

### [2026-04-05] api-limitation: Airtable cannot create formula fields via API/MCP

**Tool:** airtable
**Operation:** create-formula-field
**Attempted:** POST to /v0/{baseId}/tables/{tableId}/fields with type "formula"; also tried MCP create_field tool
**Error:** UNSUPPORTED_FIELD_TYPE_FOR_CREATE - "Creating formula fields is not supported at this time"
**Solution:** Provide manual Airtable UI instructions: Open table > Click "+" to add field > Select "Formula" type > Enter formula expression. Add to HUMAN-ACTION-REQUIRED.md with field name, table, and formula expression.
**Manual-Steps:** 1. Open Airtable base in browser. 2. Navigate to the target table. 3. Click "+" at the end of the field headers. 4. Select "Formula" as field type. 5. Enter the formula expression. 6. Click "Create field."
**Tags:** airtable, api-limitation, formula, create_field, field_type, mcp, unsupported

### [2026-04-05] api-limitation: Airtable cannot create lookup fields via API/MCP

**Tool:** airtable
**Operation:** create-lookup-field
**Attempted:** POST to /v0/{baseId}/tables/{tableId}/fields with type "lookup"; also tried MCP create_field tool
**Error:** UNSUPPORTED_FIELD_TYPE_FOR_CREATE - "Creating lookup fields is not supported at this time"
**Solution:** Provide manual Airtable UI instructions: Open table > Click "+" to add field > Select "Lookup" type > Choose linked record field and lookup field. Add to HUMAN-ACTION-REQUIRED.md with field name, linked record field, and lookup target field.
**Manual-Steps:** 1. Open Airtable base in browser. 2. Navigate to the target table. 3. Click "+" at the end of the field headers. 4. Select "Lookup" as field type. 5. Choose the linked record field. 6. Choose which field to look up. 7. Click "Create field."
**Tags:** airtable, api-limitation, lookup, create_field, field_type, mcp, unsupported

### [2026-04-05] api-limitation: Airtable cannot delete fields/columns via API/MCP

**Tool:** airtable
**Operation:** delete-field
**Attempted:** DELETE request to /v0/{baseId}/tables/{tableId}/fields/{fieldId}
**Error:** Field deletion is not supported via the API
**Solution:** Document field for manual deletion in Airtable UI. Add to HUMAN-ACTION-REQUIRED.md with table name and field name. Note: hiding a field via API IS supported as an alternative.
**Manual-Steps:** 1. Open Airtable base in browser. 2. Navigate to the target table. 3. Click the field header dropdown. 4. Select "Delete field." 5. Confirm deletion.
**Tags:** airtable, api-limitation, delete, field, column, manual-action

---

## Tool Usage

### [2026-03-25] tool-usage: YouTube transcript extraction unreliable via scraping

**Attempted:** Fetching YouTube transcript via web scrape / Firecrawl
**Error:** Rate limited / blocked after 2-3 requests
**Solution:** Use Context7 MCP for library docs. For video transcripts, ask user to paste transcript or use a dedicated transcript API.
**Tags:** youtube, scraping, rate-limit, workaround

### [2026-03-30] tool-usage: Firecrawl times out on pages over 50KB

**Attempted:** Scraping 50KB+ pages with default timeout
**Error:** Timeout after 30 seconds, no content returned
**Solution:** Use --timeout 120 flag for large pages. Alternative: use WebFetch for simpler pages that don't need JS rendering.
**Tags:** firecrawl, timeout, large-pages, web-scraping

### [2026-04-08] tool-usage: Claude Code CLI has no --cwd or --project-dir flag

**Attempted:** Spawning Claude Code CLI from a Python subprocess with `--project-dir` to set working directory
**Error:** Unrecognized flag. Claude CLI does not support --cwd or --project-dir.
**Solution:** Set `cwd=` parameter on `subprocess.Popen()` or `asyncio.create_subprocess_exec()`. Also strip the `CLAUDECODE` environment variable before spawning — otherwise Claude detects a "nested session" and refuses to start.
**Code pattern:** `env={k:v for k,v in os.environ.items() if k != "CLAUDECODE"}` + `cwd="/path/to/project"`
**Tags:** claude-code, cli, subprocess, cwd, nested-session, CLAUDECODE, python

### [2026-04-08] tool-usage: n8n cloud cannot reach localhost — use tunnel

**Attempted:** n8n HTTP Request node pointing to localhost:8765 from cloud instance
**Error:** Silently fails (1ms execution, error branch) because n8n cloud runs remotely and has no access to the user's local machine
**Solution:** Use cloudflared tunnel to expose local services. Store tunnel URL and auto-update n8n webhook URL on each tunnel restart.
**Tags:** n8n, cloud, localhost, tunnel, cloudflared, webhook, http-request

### [2026-04-08] tool-usage: n8n API returns 200 even when PATCH changes nothing

**Attempted:** PATCH/PUT to n8n API to rename field values inside workflow nodes
**Error:** API returned 200 OK, but the string replacement didn't match anything — the field kept its old value. Workflow broke at runtime.
**Root cause:** Python script used escaped Unicode (`\\u0026`) which didn't match live workflow's actual Unicode (`\u0026`). 200 response is NOT confirmation content changed.
**Solution:** After ANY n8n API PATCH/PUT: (1) GET the workflow back, (2) search for the specific field/value you changed, (3) print confirmation with True/False, (4) only then declare success.
**Tags:** n8n, api, patch, put, verification, silent-failure, unicode

---

## Platform

### [2026-03-15] platform: Windows cp1252 encoding breaks Python print output

**Attempted:** Printing Unicode characters (em dash, smart quotes) in Python scripts
**Error:** UnicodeEncodeError on Windows when stdout uses cp1252 encoding
**Solution:** Use ASCII-only characters in all Python print output. Replace em dash with --, smart quotes with straight quotes.
**Tags:** windows, encoding, python, cp1252, ascii

---

## Approach

### [2026-04-08] platform: Hidden background processes on Windows require .pyw + CREATE_NO_WINDOW

**Attempted:** Running persistent Python server (FastAPI/uvicorn) in the background on Windows without visible window
**Failed approaches:** (1) `pythonw -m uvicorn` — uvicorn needs stdout, crashes silently. (2) `cmd /c start /min` from Git Bash — doesn't survive session end. (3) Windows Task Scheduler — requires admin elevation. (4) PowerShell `WindowStyle Minimized` — still shows minimized window in taskbar.
**Solution:** Create a `.pyw` launcher that uses `subprocess.Popen()` with `creationflags=0x08000000` (`CREATE_NO_WINDOW`), resolves full path to `python.exe`, redirects stdout/stderr to a log file. The `.pyw` extension means `pythonw.exe` runs it without a console. For auto-start on login, create a Windows Startup folder shortcut (no admin needed).
**Tags:** windows, background-process, pythonw, pyw, CREATE_NO_WINDOW, taskbar, hidden, startup

### [2026-04-05] platform: Plugin hooks using python3 fail on Windows

**Attempted:** hookify and ralph-loop plugins using `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/pretooluse.py` in hooks.json
**Error:** python3 resolves to Windows Store stub (AppInstallerPythonRedirector.exe) which exits code 49. Every tool call fails because hookify fires on every PreToolUse/PostToolUse/Stop/UserPromptSubmit.
**Solution:** Patch the plugin's `hooks.json` to use `python` instead of `python3` with quoted paths: `python "${CLAUDE_PLUGIN_ROOT}/hooks/pretooluse.py"`. Real Python at Python312/python comes first in PATH. Also disable Windows App Execution Aliases for python.exe and python3.exe in Settings > Apps > Advanced app settings.
**Tags:** windows, python3, hookify, ralph-loop, plugin-hooks, app-execution-alias

---

### [2026-03-20] approach: davila7 marketplace installs to project, not global

**Attempted:** Installing skills via `npx claude-code-templates@latest --skills <name> --yes`
**Error:** Skills installed to project `.claude/skills/` instead of global `~/.claude/skills/`
**Solution:** After installing, manually copy from project `.claude/skills/` to `~/.claude/skills/`. Alternative: use `sickn33/antigravity-awesome-skills` which supports `--global` flag.
**Tags:** marketplace, davila7, install-location, global, skills

---

## Preferences

### [2026-04-07] preference: Communication channel routing

**Context:** User has specific channel assignments for different communication types. This is non-negotiable routing.
**Telegram:** ALL internal business communications -- briefs, health checks, status updates, business summaries, internal reports, daily digests. Telegram is the primary internal channel.
**Slack:** Workflow error alerts and system notifications only -- n8n failures, hook errors, automation breakdowns, monitoring alerts.
**Apply when:** Building ANY notification, alert, report, or communication workflow. Route to the correct channel based on content type, not convenience.
**Rule of thumb:** Is it a business/operational message? -> Telegram. Is it a system/workflow error? -> Slack.
**Tags:** communication, notifications, telegram, slack, routing, alerts, briefs, internal-comms

### [2026-04-07] preference: Compact between phases to preserve context

**Context:** User prefers to pause after each major phase completion to compact conversation context before proceeding. Standing request: "after each phase, let's stop so I can compact before proceeding."
**Apply when:** Multi-phase work sessions. Announce phase completion and wait for user signal before continuing.
**Tags:** context-management, phases, workflow, compaction

### [2026-04-08] preference: Plan mode — exit once, never re-display after compaction

**Context:** Two rules for plan mode behavior:
1. **Exit once:** Call ExitPlanMode exactly ONCE when plan is ready. If user cancels/escapes the dialog, STOP — do not re-ask or re-trigger. The user's typical post-plan flow: read plan → compact → switch permissions → tell you to proceed.
2. **No re-display after compaction:** After user compacts, do NOT re-write the full plan in chat. It's already in the plan file. Re-displaying burns the context that compaction just freed. Give a brief status line ("Resuming Phase 3. Starting with [next task].") and jump into execution.
**Why:** ExitPlanMode re-triggering creates an annoying loop that prevents the user from reading the plan or doing anything else. Re-displaying plans defeats the purpose of compaction.
**Tags:** plan-mode, exit, compaction, context-management, workflow

### [2026-04-08] preference: Bundle full scope — no phased upsells

**Context:** When scoping client projects, bundle the full value into one package at one price. Do NOT propose Phase 1 / Phase 2 / Phase 3 upsells.
**Why:** User said phased upselling "looks a little bit weird" and like "nickel-and-diming." Wants to provide clients with a solid foundation of what's truly useful and charge once upfront.
**Apply when:** Any client proposal or project scoping. If scope is bigger than planned, expand the single proposal — don't pitch minimum + additions.
**Tags:** pricing, proposals, client-facing, upselling, scope

### [2026-04-08] preference: Back every price with hours × rate formula

**Context:** Never propose a price without a back sheet showing derivation: hours × hourly rate + complexity adjustment +/- discounts. Line items: discovery, schema, build, migration, workflow, training, QA.
**Why:** User said "we need to come up with a formula to come up with what the price will be instead of just kind of throwing random numbers out there." Wants to break it down if a client asks.
**Apply when:** Any SLW/project proposal pricing. Client-facing number is the total — back sheet stays internal unless asked.
**Tags:** pricing, formula, proposals, transparency, client-facing

### [2026-04-08] preference: Proposal presentation rules — in-person close, 3-doc model

**Context:** Proposals are delivered in person. Rules:
- No "Contact us" CTAs — Chris presents and closes on the spot
- No Table of Contents — proposals are not manuals
- Always include "Prepared For" with full name and title
- Three-document delivery: (1) one-page visual comparison (Chris's talking points), (2) executive summary (1-2 pages for client to read), (3) full proposal (detailed reference)
**Why:** Chris closes in-person. No document should assume the client will "get back to us."
**Tags:** proposals, presentation, in-person, client-facing, documents, deliverables

### [2026-04-08] preference: DOCX generation — pandoc drafts, sop_docx_builder finals

**Context:** Two-tier document workflow:
- **Drafts:** Plain pandoc for quick DOCX during review cycles. Save to `.tmp/`.
- **Finals:** Once approved, `python tools/sop_docx_builder.py` generates branded version with logos, cover page, closing page. Save to project's `deliverables/` folder.
**Why:** Branded builder is slower; draft cycle doesn't need logos. `deliverables/` is the source of truth for client-facing documents.
**Tags:** docx, pandoc, documents, workflow, deliverables, branding

### [2026-04-08] preference: Cleanup scope = current project only

**Context:** When user says "clean up everything" during session closeout, this means: clean up files related to the CURRENT PROJECT only. Never touch files from other projects.
**Why:** User has many pending projects with their own plans and docs. Deleting those destroys work. Only exception: user explicitly says "do a complete sweep of the entire folder."
**Tags:** cleanup, scope, session, files, projects

### [2026-04-08] preference: Payment terms are client-specific, never hardcode

**Context:** Payment terms (Net 7, Net 14, etc.) are determined per client during onboarding. Never hardcode "Net 15" or any fixed term.
**Apply when:** Templates say "determined per client" or "[PAYMENT_TERMS]". Client SOWs specify exact terms. Invoicing sends [Net days] before client's payment date.
**Tags:** payment, invoicing, client-specific, net-terms, onboarding

### [2026-04-08] preference: Verify service descriptions against source docs before writing

**Context:** Never describe VDR, RLR, or SLW capabilities without checking the actual service-definitions.md first. Landing pages describe base/entry-tier capabilities unless explicitly noted. Additional content rules:
- Never say "babysitting" about systems — use "minimal oversight"
- "Not the flashiest system" = negative self-framing, never use
- Always let live demos prove speed rather than over-promising in copy
- Self-edit before presenting — don't present with known issues flagged as "optional fix"
**Why:** User caught multiple inaccuracies where higher-tier features were described as standard. Trust requires accuracy.
**Tags:** content, accuracy, services, verification, landing-page, copy

### [2026-04-08] preference: Chris's content and writing style

**Context:** User's content preferences for all client-facing materials:
- Tell a story with natural flow — not jumpy between sections
- Paint a picture through relatable examples over abstract statements
- Accuracy over marketing polish — if it doesn't match the service, fix it
- "Your AI Transformation Partner" not "an" (psychological ownership)
- Specificity over generic claims — real scenarios
- Educate the reader — teach, not just sell
- Always acknowledge human oversight — never claim "zero human needed"
- Base-tier features on landing pages, not high-tier
- Proactive monitoring emphasis — "error-fixing-before-you-know-it"
**Tags:** writing-style, content, copy, brand-voice, client-facing, preferences

---

## Process Decisions

### [2026-04-07] process: Annealing loop is mandatory -- optimize to maximum, not just gate

**Context:** Every skill, agent, hook, and plugin must go through the build-judge-optimize loop. Quality gate minimum is B (96+/120), but the system must keep optimizing beyond the gate as long as improvements are achievable without excessive risk. Don't stop at "good enough" -- push to the ceiling, then note the ceiling score for future revisits.
**Apply when:** Building or modifying any skill, agent, hook, or plugin.
**Why:** Single-pass builds consistently score 80-90. The judge-optimize cycle catches gaps that the builder misses. Stopping at the B gate leaves 10-20 points of achievable improvement on the table.
**Tags:** quality-gate, annealing, build-judge-optimize, skills, agents, optimize-to-max

### [2026-04-08] process: Push back on proposals — trust requires honesty, not compliance

**Context:** Never be a yes-agent. Analyze every proposal critically and push back when something won't work in reality, even if it sounds good in theory. When agreeing, show WHY — not just "yes."
**Why:** User said: "I need to be able to trust that if I give you instructions, you're going to push back when you need to push back." Agreement without challenge erodes trust.
**Apply when:** Pricing, strategy, architecture, process design — everything. Run proposals against real-world constraints. Show the math or scenario that breaks it. Offer alternatives when pushing back.
**Tags:** pushback, trust, critical-thinking, proposals, validation

### [2026-04-07] process: Gap reports go to Skill Hub, not local fixes

**Context:** When any workspace detects a missing capability (skill, hook, agent), it reports to the Skill Management Hub via gap-reporter.py. Workspaces do NOT build global artifacts locally.
**Apply when:** You discover a missing skill, broken hook, or capability gap in any workspace.
**Why:** Local fixes bypass quality gating and won't be available to other workspaces. Central processing ensures consistent quality and global deployment.
**Tags:** gap-detection, skill-hub, centralized-build, quality-gate

---

## Architecture Direction

### [2026-04-07] direction: Everything must be autonomy-ready

**Context:** The user is building toward a completely autonomous AI operating system. Every workflow, tool, hook, and automation must be designed with full autonomy in mind -- even if current implementation requires manual steps.
**Apply when:** Making ANY design decision. Ask: "Can this run without human intervention? If not now, can it be upgraded to autonomous later without a rewrite?"
**Design principles:**
- Prefer event-driven over polling where possible
- Build hooks and triggers, not manual checklists
- Default to automated notification rather than requiring the user to check status
- Design for upgrade path: manual today, automated tomorrow, autonomous next quarter
**Tags:** autonomy, ai-os, architecture, design-principle, future-proofing

### [2026-04-07] direction: Claude Code integration hierarchy -- MCP > CLI > API (with exceptions)

**Context:** When integrating external services with Claude Code, the default preference order is MCP > CLI > API. However, each has specific strengths that can override this default.
**Default:** MCP -- gives Claude native tool access within sessions. Use for most integrations.
**CLI supersedes MCP when:** Claude Code needs to be invoked externally (outside an active session). Example: n8n error-catching workflow that triggers Claude Code CLI to auto-fix issues even when no session is open. MCP requires an active session; CLI does not.
**API as fallback:** When neither MCP nor CLI covers the use case, or when building non-Claude integrations.
**Apply when:** Adding any new integration or tool capability. Choose the right tier based on whether it runs inside a session (MCP) or needs to trigger Claude externally (CLI).
**Tags:** mcp, cli, api, integration, architecture, tool-selection, n8n