---
name: n8n-validation-expert
description: "Use when interpreting n8n validation errors, choosing validation profiles,
  fixing operator structure issues, recognizing false positives, or recovering from
  broken workflow states. NEVER for expression syntax errors (use n8n-expression-syntax)
  or node configuration (use n8n-node-configuration)."
---

# n8n Validation Expert

## Validation Profiles

ALWAYS specify a profile explicitly -- omitting it uses defaults that may not match intent.

| Profile | When to Use | What It Checks | Trade-off |
|---------|-------------|----------------|-----------|
| `minimal` | Quick checks during editing | Required fields, basic structure | Fast but misses real issues |
| `runtime` | **RECOMMENDED** pre-deployment | Required fields, types, allowed values, dependencies | Balanced -- catches real errors without noise |
| `ai-friendly` | AI-generated configurations | Same as runtime but reduces false positives by 60% | Less noisy, may allow questionable configs |
| `strict` | Production deployment, critical workflows | Everything including best practices, performance, security | Maximum safety but many warnings |

**Progressive strictness pattern:** Use `ai-friendly` during development, `runtime` for pre-production, `strict` for production deployment.

## The Validation Loop

Telemetry from 7,841 occurrences shows this is an iterative process:
- Average 23 seconds analyzing errors, 58 seconds fixing
- 2-3 validate-fix cycles is NORMAL -- do not expect first-pass success
- This matters because without this knowledge, the instinct is to try fixing everything in one shot, which produces worse results than incremental fixing

**The correct approach:** Configure -> validate -> read ONE error -> fix it -> validate again -> repeat. Fix errors one at a time, not all at once.

## Error Type Taxonomy

Frequency distribution from production telemetry:

| Type | Frequency | Meaning | Fix Pattern |
|------|-----------|---------|-------------|
| `missing_required` | 45% | Required field not provided | Use `get_node` to discover required fields, then add them |
| `invalid_value` | 28% | Value not in allowed set | Check error message for allowed values; enums are CASE-SENSITIVE |
| `type_mismatch` | 12% | Wrong data type (string "100" vs number 100) | Match expected type exactly; "true" != true |
| `invalid_expression` | 8% | Expression syntax error | Defer to n8n-expression-syntax skill |
| `invalid_reference` | 5% | Referenced node does not exist | Check spelling, verify node exists, use cleanStaleConnections |
| `operator_structure` | <2% | IF/Switch operator issues | Auto-fixed on save -- do nothing |

**Conditional required fields trap:** Some fields are only required when another field is set. Example: `body` is required only when `sendBody: true`. The error message tells you which condition triggered the requirement -- read it.

## Auto-Sanitization

Runs automatically on every workflow create/update. Fixes operator structure issues without intervention.

### What It Fixes (trust it, do not do manually)

| Trigger | Operators | Action |
|---------|-----------|--------|
| Binary operators | equals, notEquals, contains, notContains, greaterThan, lessThan, startsWith, endsWith | REMOVES `singleValue` property (binary = two values) |
| Unary operators | isEmpty, isNotEmpty, true, false | ADDS `singleValue: true` (unary = one value) |
| IF v2.2+ / Switch v3.2+ | All conditional nodes at these versions | ADDS `conditions.options` metadata block |

### What It CANNOT Fix (requires manual intervention)

| Problem | Symptom | Solution |
|---------|---------|----------|
| Broken connections | References to deleted/renamed nodes | Use `cleanStaleConnections` operation |
| Branch count mismatch | 3 Switch rules but 2 output connections | Add missing connections or remove extra rules |
| Paradoxical corrupt state | API returns corrupt data but rejects updates | May require starting fresh or database intervention |

**Rule of thumb:** If validation complains about singleValue or conditions.options, ignore it -- auto-sanitization handles it on save. If it complains about connections or references, you must fix manually.

## False Positive Recognition

Not all warnings need fixing. Context determines whether a warning is actionable.

### When Warnings Are Acceptable

| Warning | Acceptable When | Must Fix When |
|---------|-----------------|---------------|
| "Missing error handling" | Test/dev workflows, non-critical notifications, manual triggers | Production automation, critical data processing, payment flows |
| "No retry logic" | Idempotent operations (GET), APIs with built-in retry (Stripe SDK), local/internal services | Flaky external APIs, non-idempotent POST to unreliable services |
| "Missing rate limiting" | Internal APIs, low-volume workflows (daily cron), APIs with server-side 429 handling | High-volume loops hitting rate-limited public APIs (GitHub, Twitter) |
| "Unbounded query" | Small known datasets (<100 rows), aggregation queries (COUNT/SUM), test databases | Production queries on tables that grow (users, orders, logs) |
| "Missing input validation" | Internal webhooks (your backend already validates), cryptographically signed sources (Stripe webhooks) | Public-facing webhooks accepting untrusted input |

### Known n8n False Positives (always ignore)

| Issue | Warning Message | Why It Fires | Action |
|-------|----------------|--------------|--------|
| #304 | "IF node missing conditions.options metadata" | Validation runs before auto-sanitization adds metadata | Ignore -- fixed on save |
| #306 | "Switch has N rules but N+1 output connections" | Fallback mode creates an extra output | Ignore if using fallback intentionally |
| #338 | "Cannot validate credentials without execution context" | Credentials validated at runtime, not during static validation | Ignore -- checked when workflow executes |

**Profile shortcut:** Switch to `ai-friendly` profile to suppress ~60% of false positives. Use this when building workflows to reduce noise, then validate with `runtime` or `strict` before deployment.

## Recovery Strategies

### Strategy 1: Start Fresh
**When:** Configuration is severely broken with cascading errors.
1. Use `get_node` to discover required fields for the node type
2. Build minimal valid configuration (required fields only)
3. Validate -> confirm clean
4. Add features one at a time, validating after each addition

### Strategy 2: Binary Search
**When:** Workflow validates but executes incorrectly (the hardest bugs).
1. Remove half the nodes from the workflow
2. Validate and test execution
3. If it works: problem is in the removed half
4. If it fails: problem is in the remaining half
5. Repeat until the broken node is isolated

### Strategy 3: Clean Stale Connections
**When:** "Node not found" errors from deleted/renamed nodes.
Use `n8n_update_partial_workflow` with `cleanStaleConnections` operation. This removes all connection references to non-existent nodes in one pass.

### Strategy 4: Autofix with Preview
**When:** Operator structure errors persist despite auto-sanitization.
1. Run `n8n_autofix_workflow` with `applyFixes: false` FIRST to preview what would change
2. Review the proposed fixes
3. If acceptable, run again with `applyFixes: true`
Never apply autofix blindly -- preview mode exists for a reason.

## NEVER

1. **NEVER manually set `singleValue`** on operator conditions -- auto-sanitization manages this. Manual setting creates conflicts that produce worse errors than the original.
2. **NEVER omit the `profile` parameter** from validation calls -- the default may not match your intent, leading to false confidence or unnecessary noise.
3. **NEVER try to fix all validation errors at once** -- fix one, re-validate, fix next. Fixing multiple simultaneously often introduces new errors because fixes interact.
4. **NEVER ignore error messages** and guess the fix -- the `message` and `fix` fields in validation results contain specific guidance. Read them.
5. **NEVER use `strict` profile during development** -- the volume of warnings obscures real errors. Use `ai-friendly` or `runtime` until pre-deployment.
6. **NEVER use `minimal` profile for pre-deployment validation** -- it only checks structure and misses value/type/reference errors that will fail at runtime.
7. **NEVER assume validation passed without checking the `valid` field** -- a response with warnings but no errors is still valid:true, while even one error makes it valid:false.
8. **NEVER manually add `conditions.options` metadata** to IF v2.2+ or Switch v3.2+ nodes -- auto-sanitization handles this. Manual additions may conflict with the auto-generated version.
9. **NEVER apply `n8n_autofix_workflow` with `applyFixes: true` without previewing first** -- preview mode (applyFixes: false) shows what will change. Blind autofix can break working parts of the workflow.
10. **NEVER ignore security warnings regardless of context** -- hardcoded credentials, SQL injection risks, and authentication bypasses must always be fixed, even in development.
11. **NEVER treat warnings and errors the same** -- errors block execution (must fix), warnings are advisory (context-dependent). Treating all as blocking wastes effort; treating all as ignorable risks production failures.

## Thinking Framework

When encountering validation results:

```
1. Is valid:true? -> Yes: review warnings by context, deploy if acceptable
                  -> No: continue to step 2

2. How many errors? -> 1-2: fix directly using error message guidance
                    -> 3+: consider Strategy 1 (start fresh with minimal config)

3. What error type?
   - missing_required -> use get_node to find required fields
   - invalid_value -> check allowed values in error message (case-sensitive!)
   - type_mismatch -> match exact type (string vs number vs boolean)
   - invalid_expression -> hand off to n8n-expression-syntax skill
   - invalid_reference -> run cleanStaleConnections, then re-validate
   - operator_structure -> ignore (auto-sanitization handles it)

4. After fixing, re-validate. Still failing?
   - Same error -> re-read the error message more carefully
   - New errors -> normal (fixing one can reveal others), continue iterating
   - Paradoxical state -> try Strategy 4 (autofix preview) or Strategy 1 (start fresh)

5. Warnings remaining after errors cleared?
   - Security warnings -> always fix
   - Known issues (#304, #306, #338) -> ignore
   - Best practice warnings -> check false positive table for context
   - Consider switching to ai-friendly profile if noise is overwhelming
```
