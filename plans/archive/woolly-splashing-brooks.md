# n8n Error Auto-Fix System — Implementation Plan

## Context

**Problem:** When n8n workflows fail, the only response today is logging + Slack notification. Chris has to manually investigate, diagnose, and fix every system error. With 17+ active workflows and growing client base, this doesn't scale.

**Solution:** An autonomous error detection and resolution system. When a system error occurs, Claude Code is automatically spawned to analyze, fix, test, and document the resolution — or escalate with specific human action steps if it can't fix it.

**Video Reference:** Nate Herk (AI Automation Society) demonstrated this pattern: n8n Error Trigger → bridge server → Claude Code CLI with n8n MCP → autonomous fix. We're building on that approach with our own enhancements (dual logging, learning loop, briefing integration, safety controls).

---

## Architecture

```
n8n Workflow Fails
       │
       ▼
Per-Client Error Handler (existing, e.g., oQDSXQdTyQgEFIyVMIwFx)
       │
       ├── User Error → Client notification (Monday, email, etc.) — NO CHANGE
       │
       └── System Error → Generate System Notes
                │
                ├── System ERROR Logger (Airtable, per-client) — EXISTING, NO CHANGE
                ├── Slack notification — EXISTING, NO CHANGE
                ├── Gmail notification — EXISTING (disabled), NO CHANGE
                │
                └── NEW: HTTP Request → Bridge Server (localhost:8765)
                         │
                         ▼
                   Bridge Server (Python FastAPI)
                   ├── Safety checks (dedup, rate limit, circuit breaker)
                   ├── Log to Airtable Operations Control Center (status: "received")
                   └── Spawn Claude Code CLI
                         │
                         ▼
                   Claude Code (autonomous, --dangerously-skip-permissions)
                   ├── Query Supabase: seen this error before?
                   ├── Read failed workflow via n8n MCP
                   ├── Analyze root cause
                   ├── Attempt fix via n8n MCP
                   ├── Validate fix
                   ├── Test fix (end-to-end)
                   ├── Log everything to Supabase (error_fixes table)
                   ├── Update Airtable record: status + notes/summary
                   │   ├── If solved: summary of what was done + solution details
                   │   └── If blocked: why blocked + step-by-step human instructions
                   ├── If blocked → Slack DM to Chris with action steps
                   └── Generate report in Supabase for briefing workflow
```

---

## Build Sequence (5 Phases)

### Phase 1: Foundation (no dependencies)

**1.1 — Supabase `error_fixes` table**
- Migration SQL creating the table with: error identity fields, analysis fields, fix attempt tracking, validation results, report JSONB, escalation tracking, Airtable cross-reference
- Key columns: `error_hash` (SHA256 for dedup), `fix_status` (pending/analyzing/fixing/testing/solved/blocked/escalated), `similar_fix_id` (FK for pattern matching), `report` (JSONB for briefing), `fix_diff` (JSONB before/after)
- Indexes: error_hash+created_at (dedup), error_category+fix_status (pattern match), workflow_id+fix_status+created_at (circuit breaker)
- RLS: service role full access

**1.2 — Airtable: "Operations Control Center" base (app628U7Qt8WXia2G)**
- Use EXISTING base — rename default blank table to "System Error Tracking"
- This base will grow to hold other operational data beyond errors
- Table fields: Error ID (primary), Timestamp, Workflow Name, Workflow ID, Failed Node, Error Message, Client, Error Category (single select), Fix Status (single select: Received/Analyzing/Fixing/Testing/Solved/Blocked/Escalated), Fix Description, Root Cause, Duration (seconds), Retry Count, Execution URL, Supabase ID
- **Resolution Notes** (long text) — when solved: summary of what Claude did and the solution; when blocked: why it's blocked + step-by-step instructions for what Chris needs to do
- **Resolution Summary** (single line text) — one-line summary for quick scanning (e.g., "Increased QBO API timeout to 30s" or "BLOCKED: QBO API key expired — regenerate in QBO Developer Portal")
- **Human Action Required** (checkbox) — true only when blocked, makes it easy to filter for items needing attention

**1.3 — Bridge server skeleton**
- Location: `tools/error-autofix/`
- Files: `server.py`, `config.py`, `safety.py`, `claude_runner.py`, `prompt_template.py`, `requirements.txt`, `start.bat`, `start.sh`
- Initial: FastAPI app with `/health` endpoint, Pydantic Settings loading from `.env`

### Phase 2: Plumbing (depends on Phase 1)

**2.1 — Bridge server webhook endpoint**
- `POST /webhook/n8n-error` — receives error payload, validates, queues for processing
- `GET /status` — queue depth, active fixes, circuit breaker state
- `GET /history` — last 20 processed errors (in-memory ring buffer)
- ErrorPayload model: execution_id, workflow_id, workflow_name, failed_node, error_message, error_type, client, timestamp, execution_url, raw_error, trigger_source

**2.2 — Safety controls**
- **Dedup:** In-memory dict + Supabase check. Same error_hash within 300s → reject (429)
- **Rate limit:** Sliding window, max 5 accepts/minute
- **Circuit breaker:** Per-workflow, 3 consecutive failures → trip. `POST /reset-circuit/{workflow_id}` to re-enable
- **Concurrency:** asyncio.Semaphore, max 2 Claude Code processes at once

**2.3 — Claude Code prompt template**
- Structured prompt with: error details, prior fix history, step-by-step instructions (check priors → read workflow → analyze → fix → validate → test → report)
- Required JSON output block for structured parsing
- Safety guardrails in prompt: never modify other workflows, never delete, never touch credentials, never fix the error handler itself
- Template uses Python string formatting with error context variables

### Phase 3: n8n Integration (depends on Phase 2)

**3.1 — Modify Global Error Handler workflow**
- Add HTTP Request node ("Bridge Server Webhook") after "Generate System Notes", parallel with existing System ERROR Logger / Slack / Gmail
- POST to `http://localhost:8765/webhook/n8n-error` with error payload
- **Continue On Fail = true** — if bridge is down, existing logging still works
- Connection: Generate System Notes → [existing nodes] + [new Bridge Server Webhook node]

**3.2 — End-to-end plumbing test**
- Create "AutoFix Test — Intentional Fail" workflow that deliberately errors
- Trigger it, confirm error arrives at bridge server
- Verify Airtable record created, Supabase record created

### Phase 4: Claude Code Autonomy (depends on Phase 3)

**4.1 — Claude Code CLI spawner**
- `claude_runner.py`: uses `asyncio.create_subprocess_exec` to spawn `claude --dangerously-skip-permissions -p "<prompt>" --project-dir "<HQ_PATH>"`
- Captures stdout/stderr, enforces 5-minute timeout
- Parses JSON output block from Claude's response
- On timeout: kills process, marks as blocked

**4.2 — Fix → log → report pipeline**
- Claude Code runs the full fix cycle (via prompt instructions)
- Bridge server receives Claude's JSON output
- Updates Supabase: root_cause, fix_description, fix_diff, fix_status, report
- Updates Airtable: Fix Status, Fix Description, Root Cause, Duration, Resolution Notes (detailed), Resolution Summary (one-liner), Human Action Required (checkbox)
  - **Solved:** Resolution Notes = what was done + solution details; Resolution Summary = one-line fix description; Human Action Required = false
  - **Blocked:** Resolution Notes = why blocked + step-by-step instructions for Chris; Resolution Summary = "BLOCKED: [reason]"; Human Action Required = true
- If blocked/escalated: sends Slack DM

**4.3 — Slack notification for blocked items**
- Uses Slack API `chat.postMessage` to Chris's DM
- Block Kit format: header, error details fields, why blocked, root cause, "View Execution" button, Supabase ID
- Circuit breaker trips get an urgent format with reset instructions

### Phase 5: Polish & Hardening

**5.1 — Windows auto-start**
- Task Scheduler task: "Sharkitect\ErrorAutoFixBridge", runs on logon, highest privileges
- Command: `pythonw -m uvicorn tools.error-autofix.server:app --host 127.0.0.1 --port 8765`
- Future cloud: systemd unit file or Docker (server code unchanged)

**5.2 — API fallback for n8n MCP**
- If Claude Code's MCP tools fail, the prompt instructs it to fall back to direct n8n REST API calls via the API key in `.env`
- Bridge server also has direct httpx fallback for Airtable/Supabase updates if MCP is unavailable

**5.3 — Documentation**
- Update CLAUDE.md Architecture Overview to include the auto-fix system
- Add `tools/error-autofix/README.md` with setup/config instructions
- Update MEMORY.md with project entry

---

## Key Files

| File | Action | Purpose |
|------|--------|---------|
| `tools/error-autofix/server.py` | CREATE | FastAPI bridge server |
| `tools/error-autofix/config.py` | CREATE | Pydantic Settings, env loading |
| `tools/error-autofix/safety.py` | CREATE | Dedup, rate limit, circuit breaker |
| `tools/error-autofix/claude_runner.py` | CREATE | Claude Code CLI subprocess manager |
| `tools/error-autofix/prompt_template.py` | CREATE | Prompt builder |
| `tools/error-autofix/requirements.txt` | CREATE | Dependencies |
| `tools/error-autofix/start.bat` | CREATE | Windows launcher |
| `tools/error-autofix/start.sh` | CREATE | Linux launcher |
| `.env` | MODIFY | Add AUTOFIX_WEBHOOK_SECRET, AIRTABLE_OPS_BASE_ID (app628U7Qt8WXia2G), AUTOFIX_HOST, AUTOFIX_PORT |
| `tools/supabase_memory.py` | REFERENCE | Follow existing Supabase interaction pattern |
| `.mcp.json` | REFERENCE | Confirms MCP config for spawned Claude Code sessions |
| `CLAUDE.md` | MODIFY | Update Architecture Overview section |
| n8n workflow `oQDSXQdTyQgEFIyVMIwFx` | MODIFY | Add HTTP Request node on system error branch |
| Supabase | MODIFY | CREATE TABLE error_fixes (migration) |
| Airtable | MODIFY | Create new base + table |

---

## Environment Variables (new additions to .env)

```
AUTOFIX_WEBHOOK_SECRET=<random-string>
AIRTABLE_OPS_BASE_ID=app628U7Qt8WXia2G
AUTOFIX_HOST=127.0.0.1
AUTOFIX_PORT=8765
```

All other required keys (Supabase, n8n, Slack, Airtable API) already exist.

---

## Safety & Guardrails

| Control | Implementation |
|---------|---------------|
| Dedup | Same error_hash within 5 min → reject |
| Rate limit | Max 5 fix requests/minute |
| Circuit breaker | 3 consecutive failures on same workflow → trip, Slack alert, manual reset required |
| Concurrency | Max 2 Claude Code processes simultaneously |
| Timeout | 5 min hard timeout per fix attempt |
| Self-protection | If error is from the error handler itself → escalate, never auto-fix |
| Scope restriction | Prompt forbids: deleting workflows, modifying credentials, touching unrelated workflows |
| Graceful degradation | Bridge server node has Continue On Fail — existing logging always works |

---

## Verification Plan

1. **Unit tests:** safety.py (dedup, rate limit, circuit breaker), prompt_template.py, config.py
2. **Integration test:** POST to webhook → verify 202 response, Airtable record, Supabase record
3. **End-to-end test:** Create intentional-fail workflow → trigger → verify Claude Code spawns → fixes → logs → reports
4. **Blocked scenario test:** Trigger credential error → verify Slack DM arrives with action steps
5. **Safety tests:** Rapid duplicate errors (dedup works), 3 failures on same workflow (circuit breaker trips), bridge server down (existing logging unaffected)
6. **Restart test:** Reboot machine → verify bridge auto-starts → verify queued errors get processed

---

## Cost Considerations

- **Anthropic API:** Each Claude Code spawn uses API tokens. Estimate ~$0.10-0.50 per fix depending on complexity. At current error volume (low), cost is negligible.
- **Airtable:** Free tier handles the volume. New base doesn't affect limits.
- **Supabase:** Existing project, minimal additional storage.
- **Cloud hosting (future):** ~$6-12/mo VPS if/when migrated.
