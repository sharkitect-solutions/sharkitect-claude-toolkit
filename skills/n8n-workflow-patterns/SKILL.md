---
name: n8n-workflow-patterns
description: "Use when designing n8n workflow architecture, choosing between webhook/API/database/AI/scheduled
  patterns, configuring AI agent sub-nodes, or troubleshooting responseMode and execution
  order issues. NEVER for individual node configuration (use n8n-node-configuration)
  or MCP tool usage (use n8n-mcp-tools-expert)."
---

# n8n Workflow Patterns

## Pattern Selection Decision Tree

**Start here: What triggers the workflow?**

```
External system sends data to you?     --> Webhook Processing (35% of workflows)
You need to fetch from an external API? --> HTTP API Integration
Reading/writing/syncing databases?      --> Database Operations
AI needs to reason, use tools, or chat? --> AI Agent Workflow
Runs on a timer or recurring schedule?  --> Scheduled Tasks
```

**Hybrid patterns:** Most real workflows combine 2-3 patterns. A scheduled task that fetches an API and writes to a database uses patterns 2, 3, and 5. Start with the trigger pattern, layer in others.

**Complexity guide from telemetry:**
- Simple (3-5 nodes): 42% of workflows
- Medium (6-10 nodes): 38%
- Complex (11+ nodes): 20%

## Before/After: Webhook with Custom Response

**BROKEN (common first attempt):**
```
Webhook (default responseMode: onReceived)
  --> Set node (transform data)
  --> Postgres (insert record)
  --> Webhook Response (return {id: record_id, status: "created"})
```
Result: Caller gets immediate 200 OK with empty body. Webhook Response node is ignored. Data IS processed, but caller never gets confirmation.

**WORKING (correct configuration):**
```
Webhook (responseMode: lastNode)
  --> Set node (transform data)
  --> Postgres (insert record)
  --> Webhook Response (statusCode: 201, body: {id: record_id, status: "created"})
```
Result: Caller waits until workflow finishes, gets 201 with the record ID. The only change: `responseMode: "lastNode"`.

**Why this matters:** This is the #1 webhook debugging issue. The Webhook Response node doesn't error or warn when responseMode is wrong -- it silently does nothing. You'll spend hours debugging why your caller gets no data.

## Pattern 1: Webhook Processing

### responseMode -- The Critical Choice

| Mode | Behavior | Use When |
|------|----------|----------|
| `onReceived` (default) | Immediate 200 OK, workflow runs in background | Long-running workflows, fire-and-forget |
| `lastNode` | Waits for workflow to finish, sends custom response | Caller needs data back, form confirmations |

**The trap:** Webhook Response node is IGNORED when responseMode is `onReceived`. You must set `lastNode` for custom responses to work.

### Webhook Data Nesting

Data is NOT at `$json` -- it's nested one level deeper:

```
$json.headers    --> request headers (e.g., $json.headers['x-api-key'])
$json.params     --> URL path parameters (e.g., /webhook/form/:id)
$json.query      --> query string parameters (e.g., ?token=abc)
$json.body       --> YOUR ACTUAL PAYLOAD DATA
```

Common mistake: `{{$json.email}}` returns undefined. Correct: `{{$json.body.email}}`

### Webhook Response Node

Required ONLY when responseMode = `lastNode`. Configuration:

```javascript
{
  statusCode: 200,
  headers: { "Content-Type": "application/json" },
  body: { "id": "={{$json.record_id}}", "status": "success" }
}
```

For error branches, return 400/500 with error details on the false path of validation.

### Webhook Auth and Limits

- **Query token:** `{{$json.query.token}} equals "secret"` -- simple, least secure
- **Header auth:** `{{$json.headers['x-api-key']}}` -- better
- **Signature verification:** Code node with `crypto.createHmac('sha256', secret)` for Stripe/GitHub
- **Environment paths:** `{{$env.WEBHOOK_PATH_PREFIX}}/form-submit` -- never hardcode

Webhook timeout: 120 seconds. For long processing, queue to DB and respond immediately, then process via a separate scheduled workflow.

## Pattern 2: HTTP API Integration

### Pagination Patterns

Three approaches, all using loop-back connections:
- **Offset-based:** Set page=1 --> HTTP Request --> IF has_more --> increment page --> loop
- **Cursor-based** (better for large sets): Extract `next_cursor` from response, loop until null
- **Link header** (GitHub-style): Parse `Link` header for `rel="next"`, loop until absent

### Rate Limit Handling

- **Fixed delay:** Split In Batches (1 item) --> HTTP Request --> Wait (1s) --> Loop
- **Exponential backoff:** `Math.pow(2, retryCount) * 1000` (1s, 2s, 4s)
- **Header-based:** Parse `x-ratelimit-remaining` and `x-ratelimit-reset`, wait when remaining < 10

### HTTP Error Handling

Two settings work together: `continueOnFail: true` (don't stop) + `ignoreResponseCode: true` (get body on 4xx/5xx). Then branch with `IF ({{$json.statusCode}} < 400)`.

**Fallback API pattern:** Primary (continueOnFail) --> IF (failed) --> Secondary API

### Binary Downloads and Auth

Binary: `{ responseFormat: "file", outputPropertyName: "data" }`

Authentication -- always use credentials system, never parameters:
- `nodeCredentialType: "httpHeaderAuth"` for Bearer/API key
- `nodeCredentialType: "httpBasicAuth"` for Basic
- `nodeCredentialType: "oAuth2Api"` for OAuth2

## Pattern 3: Database Operations

### Batch Processing with Split In Batches

For large datasets, NEVER select unbounded:

```
Query (LIMIT 10000) --> Split In Batches (100) --> Transform --> Write --> Loop
```

**Cursor-based pagination** (better than OFFSET for millions of rows):
```sql
SELECT * FROM table WHERE id > $1 ORDER BY id ASC LIMIT 1000
```
Track `last_id` from each batch, loop until no records returned.

### Transaction Pattern

n8n has no native transaction support. Use executeQuery:

```javascript
// Node 1: BEGIN
{ operation: "executeQuery", query: "BEGIN" }

// Nodes 2-N: Operations (with continueOnFail: true)
{ operation: "executeQuery", query: "INSERT INTO ..." }

// Final node: Commit or Rollback based on error
{ operation: "executeQuery", query: "={{$node['Operation'].json.error ? 'ROLLBACK' : 'COMMIT'}}" }
```

### Upsert Pattern (Postgres)

```sql
INSERT INTO users (id, name, email)
VALUES ($1, $2, $3)
ON CONFLICT (id)
DO UPDATE SET name = $2, email = $3, updated_at = NOW()
```

### Connection Pooling

Configured in credentials, not in nodes:
```javascript
{ host: "db.example.com", database: "mydb", min: 2, max: 10, idleTimeoutMillis: 30000 }
```

### Parameterized Queries

Always use `$1, $2` placeholders with parameters array. NEVER string-concatenate:
```javascript
// CORRECT
{ query: "SELECT * FROM users WHERE id = $1", parameters: ["={{$json.id}}"] }
// WRONG (SQL injection risk)
{ query: "SELECT * FROM users WHERE id = '={{$json.id}}'" }
```

MySQL uses `?` instead of `$1`.

## Pattern 4: AI Agent Workflow

### The 8 AI Connection Types

| Type | Purpose | Required? |
|------|---------|-----------|
| `ai_languageModel` | The LLM (OpenAI, Anthropic, etc.) | YES |
| `ai_tool` | Functions the agent can call | Recommended |
| `ai_memory` | Conversation context persistence | Recommended |
| `ai_outputParser` | Parse structured output from LLM | Optional |
| `ai_embedding` | Vector embeddings for RAG | For RAG only |
| `ai_vectorStore` | Vector database connection | For RAG only |
| `ai_document` | Document loaders | For RAG only |
| `ai_textSplitter` | Text chunking for documents | For RAG only |

### Sub-Node Connection Model

Tools, memory, and models connect TO the agent as sub-nodes -- they do NOT go after the agent in the flow:

```
OpenAI Chat Model  --[ai_languageModel]--> AI Agent --> Output
HTTP Request Tool  --[ai_tool]----------->
Database Tool      --[ai_tool]----------->
Window Buffer Mem  --[ai_memory]--------->
```

**Critical:** Connect tools via `ai_tool` port, NOT the main output port. A node connected to the main port feeds data into the agent as input, not as a callable tool.

### Agent Type Selection

| Agent | Best For | Key Trait |
|-------|----------|-----------|
| `conversationalAgent` | General chat, support | Natural flow, most common |
| `openAIFunctionsAgent` | Tool-heavy, structured output | Better tool selection, reliable calling |
| `ReAct` | Complex multi-step reasoning | Think-Act-Observe loop, visible reasoning |

### Memory Types

| Type | Behavior | Config Key |
|------|----------|------------|
| Buffer Memory | Stores ALL messages until cleared | `sessionKey` per user |
| Window Buffer Memory | Last N messages (recommended) | `contextWindowLength: 10` |
| Summary Memory | Summarizes old messages via LLM | `maxTokenLimit: 2000` |

All memory types use `sessionKey` for per-user/per-session isolation: `={{$json.body.session_id}}`

### Tool Configuration

ANY n8n node becomes a tool by connecting via `ai_tool` port. The agent sees:
1. Tool `name` and `description` (used to decide WHEN to call it)
2. Input schema (optional, helps the agent know what parameters to pass)
3. The agent generates parameters, n8n executes the node, results return to agent

**Tool descriptions must be specific.** Vague = agent won't know when to call it:
- BAD: `"Get data"`
- GOOD: `"Query customer orders by email address. Returns order ID, status, and shipping info."`

### Safety for Database Tools

Create read-only DB user: `GRANT SELECT ON customers, orders TO ai_readonly;` -- NO write access. AI can generate arbitrary SQL.

## Pattern 5: Scheduled Tasks

### Schedule Modes

**Interval:** `{ mode: "interval", interval: 15, unit: "minutes" }`

**Days & Hours:** `{ mode: "daysAndHours", days: ["monday","wednesday","friday"], hour: 9, minute: 0 }`

**Cron** (format: `minute hour day month weekday`):
```
0 9 * * 1-5          Weekdays at 9 AM
0 0 1 * *            First of month at midnight
*/15 9-17 * * 1-5    Every 15 min during business hours on weekdays
0 */6 * * *          Every 6 hours
0 9,17 * * *         At 9 AM and 5 PM daily
```

### Timezone Handling

Set in workflow settings: `{ timezone: "America/New_York" }`

**DST trap:** A UTC-based schedule for "9 AM local" shifts by 1 hour during DST transitions. Always set the workflow timezone explicitly -- n8n handles DST automatically when timezone is set.

### Overlap Prevention

Long-running tasks can overlap the next scheduled execution. Use a Redis lock:

```
Schedule --> Redis (GET lock) --> IF (lock exists) --> End (skip)
                              --> ELSE --> Redis (SET lock, TTL 30min)
                                      --> Execute workflow
                                      --> Redis (DELETE lock)
```

### Activation Caveat

Workflows must be activated manually in the n8n UI. The API/MCP `activateWorkflow` operation is not available -- schedule won't fire until manually activated.

## Data Flow Patterns

| Pattern | Structure | Use When |
|---------|-----------|----------|
| Linear | Trigger --> Transform --> Action | Single processing path |
| Branching | IF --> True path / False path | Conditional logic |
| Parallel | Trigger --> Branch 1 + Branch 2 --> Merge | Independent operations |
| Loop | Split In Batches --> Process --> Loop back | Large dataset processing |
| Error Handler | Main flow + Error Trigger --> separate error flow | Need dedicated error handling |

**Parallel branch caveat:** Execution order matters. Check workflow settings.

## Execution Order

| Version | Behavior | Use |
|---------|----------|-----|
| v0 | Top-to-bottom (legacy) | Existing old workflows |
| v1 | Connection-based (recommended) | All new workflows |

v0 executes nodes based on vertical position in the canvas. v1 follows connection wires. This ONLY matters when you have parallel branches -- v0 may execute them in unexpected order. Always use v1 for new workflows.

## Pattern Statistics (Telemetry Data)

**Trigger distribution:** Webhook 35%, Schedule 28%, Manual 22%, Service 15%

**Transformation nodes:** Set 68%, Code 42%, IF 38%, Switch 18%

**Output destinations:** HTTP Request 45%, Slack 32%, DB writes 28%, Email 24%

## Rationalizations That Break Workflows

| Rationalization | When It Appears | Why It's Wrong |
|---|---|---|
| "I'll just use onReceived and add a Webhook Response anyway" | Building webhook that needs to return data | Webhook Response is silently ignored with onReceived -- you'll debug for hours wondering why the caller gets 200 OK with no body |
| "The data is at $json.email, I checked" | Accessing webhook payload directly | Webhook nests your payload under body -- $json.email returns undefined, $json.body.email is correct |
| "I'll connect this tool to the agent's output" | Wiring AI agent workflows | Output port = data flow. ai_tool port = callable function. Wrong port means the agent can't call the tool |
| "I don't need LIMIT, the table is small" | Writing a SELECT query | Tables grow. "Small" table today is 10M rows next quarter. Always LIMIT, always use Split In Batches for large results |
| "I'll hardcode the API key for now and fix later" | Quick prototyping | Hardcoded secrets survive in workflow exports and version history. Use credentials system from the start |
| "Execution order doesn't matter for my workflow" | Building parallel branches | v0 executes by canvas position -- moving a node changes execution order. Always use v1 for predictable parallel behavior |
| "The schedule will just work in the right timezone" | Not setting timezone explicitly | Default timezone varies by install. DST transitions silently shift times by 1 hour. Always set timezone. |

## NEVER

1. **NEVER access webhook data at `$json.email`** -- it's always `$json.body.email`. The top-level `$json` contains headers, params, query, and body.
2. **NEVER use Webhook Response node with `responseMode: "onReceived"`** -- it's silently ignored. Switch to `lastNode` first.
3. **NEVER connect tool nodes to AI Agent's main output port** -- use the `ai_tool` connection type. Main port = data input, ai_tool port = callable function.
4. **NEVER run unbounded SELECT queries** -- always use LIMIT. `SELECT * FROM large_table` can return millions of rows and crash the workflow.
5. **NEVER string-concatenate values into SQL** -- use parameterized queries (`$1` for Postgres, `?` for MySQL) to prevent injection.
6. **NEVER hardcode credentials in HTTP Request parameters** -- use the credentials system. Hardcoded secrets are visible in workflow exports.
7. **NEVER skip timezone setting on scheduled workflows** -- the default may not match your intent, and DST transitions will cause silent timing shifts.
8. **NEVER run long tasks on tight schedules without overlap prevention** -- a 10-minute task on a 5-minute schedule causes parallel execution and resource contention.
9. **NEVER give AI agent tools write access to databases** -- create a read-only user. The agent generates arbitrary SQL and can DELETE or DROP tables.
10. **NEVER use execution order v0 for new workflows** -- v0's top-to-bottom order causes unpredictable behavior with parallel branches. Always use v1.
11. **NEVER assume API/MCP can activate scheduled workflows** -- activation must be done manually in the n8n UI.
12. **NEVER process all items at once for large datasets** -- use Split In Batches to avoid out-of-memory errors.

## Thinking Framework

When designing a new n8n workflow:

```
1. TRIGGER: What starts this workflow?
   - External event = Webhook
   - Timer = Schedule (set timezone!)
   - Manual = for testing only

2. PATTERN: Which core pattern(s) apply?
   - Match to the 5 patterns above
   - Most workflows combine 2-3 patterns

3. DATA FLOW: Linear, branching, parallel, or loop?
   - Large datasets --> Split In Batches + Loop
   - Conditional logic --> IF/Switch branching
   - Independent operations --> Parallel branches (use v1 execution order)

4. AI INVOLVED? If yes:
   - Choose agent type (conversational vs openAIFunctions vs ReAct)
   - Connect model via ai_languageModel
   - Connect tools via ai_tool (NOT main port)
   - Add memory via ai_memory with sessionKey
   - Write specific tool descriptions

5. ERROR HANDLING:
   - HTTP calls: continueOnFail + IF check
   - Scheduled: Error Trigger workflow + alerting
   - Database: Transaction pattern (BEGIN/COMMIT/ROLLBACK)
   - Rate limits: Wait node or exponential backoff

6. PRODUCTION READINESS:
   - Webhook: set responseMode, add auth
   - Schedule: set timezone, add overlap prevention
   - Database: parameterized queries, LIMIT on all SELECTs
   - AI: read-only DB user, limit tool output size
```
