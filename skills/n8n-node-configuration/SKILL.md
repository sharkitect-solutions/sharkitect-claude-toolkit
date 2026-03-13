---
name: n8n-node-configuration
description: "Use when configuring n8n nodes, understanding property dependencies,
  determining required fields per operation, resolving invisible/missing fields, or
  choosing get_node detail levels. NEVER for expression syntax (use n8n-expression-syntax),
  MCP tool selection (use n8n-mcp-tools-expert), or Code node JS/Python (use n8n-code-javascript
  or n8n-code-python)."
---

# n8n Node Configuration

## The Core Principle: Operation-Aware Configuration

The same node with different operations requires completely different fields. This is the #1 source of configuration errors.

```
Slack message/post   -> channel (required), text (required), messageId (hidden)
Slack message/update -> messageId (required), text (required), channel (optional)
Slack message/delete -> messageId (required), channel (required), text (hidden)
Slack channel/create -> name (required), text (hidden), channel (hidden)
```

**Rule**: resource + operation = a unique set of required, optional, and hidden fields. When you change operation, assume ALL field requirements change. Query get_node again -- do not reuse the previous config blindly.

## displayOptions: Why Fields Appear and Disappear

n8n controls field visibility through `displayOptions` rules in the node schema. This is the mechanism behind "invisible required fields" errors.

### The Mechanism

```javascript
// This field only appears when BOTH conditions are true
{
  "name": "body",
  "displayOptions": {
    "show": {
      "sendBody": [true],                    // condition 1
      "method": ["POST", "PUT", "PATCH"]     // condition 2
    }
  }
}
```

**Logic rules**:
- Multiple keys within `show` = AND (all must match)
- Multiple values within one key = OR (any can match)
- `hide` works inversely: field disappears when conditions match
- `show` is far more common than `hide` in practice

### Dependency Chains

Fields can form cascading dependency chains where each level unlocks the next:

```
method=POST          -> sendBody becomes visible
  sendBody=true      -> body becomes visible AND required
    body.contentType=json -> body.content expects JSON object
    body.contentType=form-data -> body.content expects form fields array
```

**Critical**: Configure parent properties first (method, resource, operation), then dependent fields. A field that depends on an unset parent will be invisible AND its value will be stripped on save even if you set it directly.

### Common Dependency Patterns

**Boolean toggle** -- a checkbox controls a section:
```
sendBody=true   -> body field appears (HTTP Request)
sendQuery=true  -> queryParameters field appears (HTTP Request)
sendHeaders=true -> headerParameters field appears (HTTP Request)
```

**Operation switch** -- different operations show different field sets:
```
resource=message, operation=post   -> shows channel, text, attachments
resource=message, operation=update -> shows messageId, text
resource=channel, operation=create -> shows name, isPrivate
```

**Type selection** -- a type dropdown changes available sub-fields:
```
conditions.string.operation=equals    -> shows value1, value2 (binary)
conditions.string.operation=isEmpty   -> shows value1 only (unary)
conditions.boolean.operation=true     -> shows value1 only (unary)
```

## get_node Escalation Strategy

Three detail levels exist. Always start at standard and escalate only when needed.

**Standard** (default, 1-2K tokens) -- covers 95% of cases:
```
get_node({ nodeType: "nodes-base.slack" })
```
Returns: required fields, common options, operation list, metadata. Use this first for any node configuration task.

**search_properties** -- targeted field lookup:
```
get_node({ nodeType: "nodes-base.httpRequest", mode: "search_properties", propertyQuery: "body" })
```
Returns: matching property paths with their displayOptions rules. Use when a specific field seems missing, invisible, or has unclear dependencies.

**full** (3-8K tokens) -- complete schema, last resort:
```
get_node({ nodeType: "nodes-base.slack", detail: "full" })
```
Returns: every property, every nested option, all displayOptions rules. Use only when standard + search_properties both failed to answer your question.

### Decision Tree

```
Need to configure a node?
  -> get_node (standard). Got what you need? DONE.
     |
     Missing a specific field or field seems invisible?
       -> get_node (search_properties, query=fieldName). Found it? DONE.
          |
          Still confused about the full dependency tree?
            -> get_node (detail="full"). Read the displayOptions.
```

## Node Category Patterns

### Resource/Operation Nodes (Slack, Google Sheets, Airtable, Gmail)

Structure: `{ resource: "<entity>", operation: "<action>", ...operation-specific fields }`

What makes these tricky: the same node exposes completely different interfaces per operation. A Slack node configured for "post" is almost a different node than one configured for "update." Always query get_node when switching operations.

### HTTP-Based Nodes (HTTP Request, Webhook)

Structure: `{ method: "<verb>", url: "<endpoint>", authentication: "<type>", ...method-specific fields }`

Key dependencies:
- POST/PUT/PATCH/DELETE -> sendBody available (GET does NOT show sendBody)
- sendBody=true -> body required
- authentication != "none" -> credentials config required
- sendQuery=true -> queryParameters available

**Webhook gotcha**: Incoming webhook data lives at `$json.body`, not `$json` directly. This trips up every new n8n developer.

### Database Nodes (Postgres, MySQL, MongoDB)

Structure: `{ operation: "<action>", ...action-specific fields }`

Key dependencies by operation:
- executeQuery -> query field required
- insert -> table + columns required
- update -> table + columns + updateKey required
- delete -> table + conditions required

### Conditional Logic Nodes (IF, Switch)

Structure: `{ conditions: { <type>: [{ operation, value1, value2? }] } }`

**Binary operators** (equals, notEquals, contains, larger, smaller): require value1 AND value2.
**Unary operators** (isEmpty, isNotEmpty, true, false): require value1 ONLY. The `singleValue: true` flag is auto-added.

Switch nodes add: `{ mode: "rules", rules: { rules: [...] }, fallbackOutput: "extra" }`. Number of rules must match number of outputs.

## Auto-Sanitization (IF/Switch Nodes)

n8n auto-fixes operator structure on save. Know what IS and ISN'T handled:

**Auto-fixed (do not manually set)**:
- Binary operator used -> singleValue is removed if present
- Unary operator used -> singleValue: true is added
- IF v2.2+ / Switch v3.2+ -> version metadata auto-added to conditions

**NOT auto-fixed (you must handle)**:
- Missing required fields (channel, text, messageId, etc.)
- Wrong value types (string where number expected)
- Invalid operation names
- Missing resource/operation combination
- Fields hidden by unmet displayOptions (parent not set)

**Practical rule**: Set the operator and values correctly. Let auto-sanitization handle the structural metadata. Focus on business logic, not plumbing.

## NEVER

1. **NEVER jump to detail="full" first** -- standard covers 95% of cases and costs 2-5x fewer tokens. Escalate only after standard fails.
2. **NEVER reuse config across operations without re-querying** -- changing operation from "post" to "update" changes which fields are required, optional, and hidden. Query get_node again.
3. **NEVER set fields hidden by unmet displayOptions** -- they will be silently stripped on save. Set the parent property first (e.g., sendBody=true before body).
4. **NEVER manually set singleValue on IF/Switch conditions** -- auto-sanitization handles this. Manual setting creates conflicts.
5. **NEVER assume channel is always required for Slack** -- it depends on operation (required for post, optional for update, required for delete).
6. **NEVER skip the sendBody toggle for POST/PUT/PATCH** -- even though it seems obvious, n8n requires sendBody=true explicitly before accepting a body.
7. **NEVER configure body for GET requests** -- even if you force it in, n8n strips it because GET's displayOptions hide body-related fields.
8. **NEVER hardcode all possible fields upfront** -- fields hidden by displayOptions waste tokens and may cause validation confusion. Set only what the current operation requires.
9. **NEVER ignore validation errors about "missing" fields that seem present** -- this means a parent displayOptions condition is unmet. The field exists in your config but is invisible to n8n.
10. **NEVER assume webhook data is at $json directly** -- webhook payloads arrive at $json.body. This is n8n-specific and differs from most other nodes.
11. **NEVER mix up node type strings** -- it is `nodes-base.httpRequest` not `n8n-nodes-base.httpRequest`. The prefix matters for get_node lookups.
12. **NEVER configure expressions inside Code nodes** -- Code nodes use `$input.item.json` not `={{$json.field}}`. That is the domain of n8n-code-javascript.

## Thinking Framework

Before configuring any node, answer these five questions in order:

```
1. WHAT node type and operation?
   -> Determines the entire field set. Query get_node(standard) with the specific resource+operation.

2. WHAT fields does THIS operation require?
   -> Read the get_node response. Do not assume from other operations on the same node.

3. ARE there dependency chains I need to satisfy?
   -> Check if required fields depend on toggle/parent fields (sendBody, sendQuery, etc.).
   -> Set parents FIRST, then children.

4. IS there anything auto-sanitized?
   -> IF/Switch conditions: operator metadata is auto-fixed. Do not manually set singleValue.
   -> Everything else: you must set it yourself.

5. VALIDATE before deploying.
   -> Run validate_node. If it reports a "missing" field you already set, check displayOptions
      dependencies -- a parent condition is likely unmet.
```
