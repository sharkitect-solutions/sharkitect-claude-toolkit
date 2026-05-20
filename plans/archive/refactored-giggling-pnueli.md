# Fantastic Floors — Board-Agnostic Audit & Test Plan

## Context

Fantastic Floors workflows (CALCULATE and ESTIMATE) were running perfectly with hardcoded Monday.com board IDs pointing to "Residential Customers 2026." The client wants to duplicate the board for other departments (remodeling/construction, commercial, etc.) and reuse the same workflows.

You changed **only** the Monday.com native nodes — from fixed board ID/name selection to the expression `={{ $json.boardId }}`. **These workflows have NOT been tested since that change.**

This plan covers: (1) audit findings from the previous session, (2) testing the workflows now, (3) fixing any issues found.

---

## Your Available Tools for This Work

### Skills (invoke via Skill tool)
| Skill | Use For |
|-------|---------|
| `n8n-expression-syntax` | Validating/fixing `{{ }}` expressions in Monday nodes |
| `n8n-code-javascript` | Reviewing/modifying Code node logic |
| `n8n-validation-expert` | Interpreting validation results |
| `n8n-mcp-tools-expert` | Choosing the right MCP tool for each operation |
| `n8n-node-configuration` | Monday.com node property configuration |
| `n8n-workflow-patterns` | Workflow architecture patterns |

### MCP Servers (invoke via ToolSearch)
| Server | Tools | Use For |
|--------|-------|---------|
| `claude_ai_n8n` | `search_workflows`, `get_workflow_details`, `execute_workflow` | Reading/testing workflows on your instance |
| `n8n-mcp` | Full suite (20 tools) — `n8n_get_workflow`, `n8n_executions`, `n8n_test_workflow`, `n8n_update_partial_workflow`, etc. | Workflow management, execution history, testing, surgical updates |

### Built-in Agents (invoke via Task tool)
| Agent | Use For |
|-------|---------|
| `debugger` | Analyzing execution failures, root cause analysis |
| `n8n-workflow-debugger` | n8n-specific execution analysis |

### SaaS Packs (available but not needed for this task)
- `retellai-pack`, `deepgram-pack`, `customerio-pack`

---

## Audit Summary (Completed in Previous Session)

### What Was Done Right
- All 7 Monday.com native nodes across both workflows now use `={{ $json.boardId }}`
- All HTTP Request nodes query Monday's GraphQL API using `pulseId` from the webhook (dynamic) and fetch `board { id }` in the response
- All Code nodes extract boardId dynamically from GraphQL responses (`parentItem.board?.id`)
- Zero hardcoded board IDs or board names found anywhere
- Column IDs are preserved during Monday board duplication — all column references are safe
- QBO company ID is hardcoded but expected (same company for all departments)

### Items Flagged for Verification

| # | Node | Workflow | Concern | Risk Level |
|---|------|----------|---------|------------|
| 1 | **POST Estimate Link** | ESTIMATE | `$json.boardId` may be undefined — upstream "GET Estimate Info" doesn't output boardId | HIGH |
| 2 | **Change Quote Status to Ready to Send** | ESTIMATE | Same issue, cascades from #1 | HIGH |
| 3 | **Change Status to NEEDS REVIEW** | ESTIMATE | boardId nested at `$json.data.items[0].board.id`, not flat `$json.boardId` | HIGH (untested path — duplicate-estimate guardrail) |
| 4 | **Change Status For Subitems To Updated** | CALCULATE | Receives Monday node output — may not include flat boardId | MEDIUM |
| 5 | **Change Subitem Status to Updated** | ESTIMATE | Same as #4 | MEDIUM |

### The Key Question

Monday.com item IDs are globally unique. The n8n Monday.com node might:
- (a) Pass through input data fields to its output (so boardId survives), OR
- (b) Accept undefined boardId and resolve the board from the itemId internally

If either (a) or (b) is true, the workflows work even where boardId appears undefined. **Testing will confirm this.**

---

## ESTIMATE Workflow — Complete Branch Map

5 decision nodes create distinct execution paths:

```
Webhook
  → If (challenge present?)
      ├─ TRUE  → Respond to Webhook (Monday verification handshake — not a real run)
      └─ FALSE → Run & Capture Execution Data → Get Trigger Record
                  → Does Estimate Already Exist? (link column not empty?)
                      ├─ TRUE  → [BRANCH A: GUARDRAIL]
                      │           Change Status to NEEDS REVIEW → Log
                      └─ FALSE → [BRANCHES B-F: MAIN PATH] (3 parallel tracks)
                                  ├─ Track 1: Search For Customer → Does Customer Exist in QBO?
                                  │     ├─ TRUE  (DisplayName exists) → Merge [input 1]
                                  │     └─ FALSE (no DisplayName)    → Get Customer Info → Normalize → Create Customer → Merge [input 0]
                                  ├─ Track 2: Pull Subitems → Evaluate Calculation State → Need To Calculate?
                                  │     ├─ SKIP_ALL → Normalize → Combine → Merge [input 2]
                                  │     └─ NOT SKIP → ALL or SOME?
                                  │           ├─ RECALC_PARTIAL → (PARTIAL) CALCULATE → Update QTY → Change Subitem Status → Refresh → Normalize → Combine → Merge [input 2]
                                  │           └─ RECALC_ALL     → (ALL) CALCULATE     → Update QTY → Change Subitem Status → Refresh → Normalize → Combine → Merge [input 2]
                                  └─ Track 3: Direct → Merge [input 3]

                                  Merge All For Estimate
                                    → Estimate Builder (FINAL)
                                    → Post Estimate to QBO
                                    → GET Estimate Info
                                    → POST Estimate Link ← (boardId concern #1)
                                    → Change Quote Status to Ready to Send ← (boardId concern #2)
                                    → Log (Complete)
```

### Monday.com Nodes by Branch

| Branch | Monday Nodes Hit | boardId Source |
|--------|-----------------|---------------|
| **A: Guardrail** | Change Status to NEEDS REVIEW | `$json.boardId` — data from "Get Trigger Record" (nested at `$json.data.items[0].board.id`) |
| **B-F: Calculation** | Update QTY and Total SQFT, Change Subitem Status to Updated | `$json.boardId` — from CALCULATE code output (flat) |
| **B-F: Estimate Posting** | POST Estimate Link, Change Quote Status to Ready to Send | `$json.boardId` — from "GET Estimate Info" output (NOT included) |

---

## Execution Plan

### Testing Workflow

**You (Chris) trigger → I (Node) analyze.** For every test:

1. You set up / tweak the test item on the Monday board to match the branch conditions
2. You manually trigger the workflow from Monday (the natural trigger)
3. You tell me: "I triggered it" (and which test / branch)
4. I pull the latest execution via `n8n_executions`, analyze the result
5. **If it worked:** We confirm that branch is good and move to the next
6. **If it errored:** I diagnose the failure, we fix it together, you re-trigger

This keeps you in control of the test data and gives us real production-path executions — no synthetic webhook payloads.

---

### Step 1: Check Recent Execution History
- Use `n8n_executions` to pull recent executions for both workflows
- Determine: have any executions run SINCE the board ID change (after ~March 13)?
- If yes: check success/failure status and which branches were exercised
- This tells us what's already been proven vs. what still needs testing

### Step 2: Test CALCULATE Workflow (`p95MUMY5YIneTlQa`)
**One path — straightforward:**
- You trigger CALCULATE from a Monday item with subitems that need calculation
- I check the execution: did Update QTY and Change Status nodes resolve `$json.boardId`?

### Step 3: Test ESTIMATE Workflow — All Branches (`CwLsCqghAVA8Mst3`)

**6 tests covering every decision branch. You control the test item state for each:**

| Test | Branch | What You Set Up | Monday Nodes Tested | What It Proves |
|------|--------|----------------|---------------------|----------------|
| **E-1** | Guardrail | Item that ALREADY HAS an estimate link in the `link` column | Change Status to NEEDS REVIEW | boardId resolves from nested GraphQL data |
| **E-2** | RECALC_ALL + Customer exists | Item with NO estimate link, ALL subitems "Need Updated", customer exists in QBO | Update QTY, Change Subitem Status, POST Estimate Link, Change Quote Status | Full calculation + estimate creation path |
| **E-3** | RECALC_PARTIAL + Customer exists | Same item, tweak: MIX of subitems (some "Updated", some "Need Updated") | Same as E-2 via PARTIAL CALCULATE | Partial calculation path |
| **E-4** | SKIP_ALL + Customer exists | Same item, tweak: ALL subitems already "Updated" | POST Estimate Link, Change Quote Status (skips calc) | No-calc path still builds estimate correctly |
| **E-5** | Customer NOT in QBO | Item with a customer name that does NOT exist in QuickBooks | Create customer (QBO) + all downstream Monday nodes | Customer creation + estimate flow |
| **E-6** | Guardrail re-run | Re-trigger E-2's item (now has estimate link from E-2 run) | Change Status to NEEDS REVIEW | Confirms guardrail catches re-runs |

**Sequencing tip:** Run E-2 first (RECALC_ALL). After it succeeds, that item now has an estimate link — re-trigger it for E-6 (guardrail). Then tweak the same or different items for E-1, E-3, E-4, E-5 in any order.

### Step 4: Analyze Results & Fix Issues

For each execution I check:
- Did it complete successfully?
- Did every Monday.com node resolve `$json.boardId` to an actual board ID (not undefined/null)?
- Did the correct branch fire?

**If issues are found, pre-planned fixes:**

| Issue | Fix | Node to Modify |
|-------|-----|----------------|
| POST Estimate Link / Change Quote Status get undefined boardId | Add `boardId` to "GET Estimate Info" Code node output: `boardId: $('Run & Capture Execution Data').first().json.trigger_board_id` | GET Estimate Info |
| Change Status to NEEDS REVIEW gets undefined boardId | Change expression to `={{ $json.data.items[0].board.id }}` | Change Status to NEEDS REVIEW |
| Change Subitem Status / Change Status For Subitems gets undefined boardId | Change expression to `={{ $('Run & Capture Execution Data').first().json.trigger_board_id }}` | Change Subitem Status to Updated (ESTIMATE), Change Status For Subitems To Updated (CALCULATE) |

### Step 5: Re-test After Fixes (if needed)
- You re-trigger any failed test scenarios
- I confirm all 6 ESTIMATE branches + CALCULATE pass

### Step 6: Confirm Board-Agnostic Readiness
- If all tests pass: workflows are confirmed ready for duplicated boards
- Document the board duplication requirements for the customer (see below)

---

## Board Duplication Requirements (For the Customer)

Once workflows are confirmed working:
1. **Same column structure** — preserved automatically when duplicating
2. **Same subitem structure** — subitems and their columns must match
3. **Webhook setup** — each duplicated board needs a Monday automation sending webhooks to:
   - CALCULATE: `/webhook/PROD-CALC`
   - ESTIMATE: `/webhook/PROD-systemlink-estimate-sync`
4. **No per-board workflow changes** — one workflow handles all boards
