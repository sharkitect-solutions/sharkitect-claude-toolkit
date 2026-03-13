---
name: n8n-mcp-tools-expert
description: "Use when working with n8n MCP tools (search_nodes, get_node, validate_node,
  create/update workflows), choosing nodeType formats, selecting validation profiles,
  or deploying templates. NEVER for expression syntax (use n8n-expression-syntax) or
  Code node content (use n8n-code-javascript/python)."
---

# n8n MCP Tools Expert

## THE #1 RULE: nodeType Format

Two prefixes exist. Using the wrong one = "Node not found" error.

**SHORT prefix** -- for search, get, validate tools:
```
nodes-base.slack
nodes-base.httpRequest
nodes-langchain.agent
```

**FULL prefix** -- for workflow tools (create, update, deploy):
```
n8n-nodes-base.slack
n8n-nodes-base.httpRequest
@n8n/n8n-nodes-langchain.agent
```

**The bridge**: `search_nodes` returns BOTH formats in every result:
- `nodeType` = short (use with get_node, validate_node, validate_workflow)
- `workflowNodeType` = full (use with n8n_create_workflow, n8n_update_partial_workflow)

Always capture both values from search results. Never construct prefixes manually
when search results are available.

---

## Tool Selection Decision Tree

```
WHAT DO YOU NEED?
|
|-- Find a node by keyword/service?
|   --> search_nodes (returns both nodeType formats)
|
|-- Understand a node's config?
|   --> get_node (detail: "standard" -- the default, 1-2K tokens)
|   |   Need more? See "get_node Escalation Strategy" below
|
|-- Validate a node config?
|   --> validate_node (profile: "runtime" recommended)
|
|-- Validate a whole workflow?
|   --> validate_workflow (local JSON) or n8n_validate_workflow (by ID)
|
|-- Create a new workflow?
|   --> n8n_create_workflow (requires API)
|
|-- Edit an existing workflow?
|   --> n8n_update_partial_workflow (requires API, 17 operation types)
|
|-- Fix validation errors automatically?
|   --> n8n_autofix_workflow (preview first, then apply)
|
|-- Start from a proven pattern?
|   --> search_templates --> get_template --> n8n_deploy_template
|
|-- Check what tools exist or how they work?
|   --> tools_documentation (self-documenting, always available)
```

---

## get_node Escalation Strategy

Start small. Escalate only when the previous level was insufficient.

**Level 1 (95% of cases)**: `get_node({nodeType: "nodes-base.X"})`
- Default detail="standard", 1-2K tokens
- Returns operations, essential properties, metadata

**Level 2 - readable docs**: `get_node({nodeType: "...", mode: "docs"})`
- Markdown documentation with usage examples
- Better than raw schema for understanding behavior

**Level 3 - find specific field**: `get_node({nodeType: "...", mode: "search_properties", propertyQuery: "auth"})`
- Targeted search when you know what property you need
- Common queries: auth, header, body, json, url, method, credential

**Level 4 (last resort)**: `get_node({nodeType: "...", detail: "full"})`
- 3-8K tokens, complete schema with all nested options
- Only for debugging complex configuration issues

**Version tools** (when upgrading nodes):
- `mode: "versions"` -- list all versions with breaking change flags
- `mode: "breaking"` + `fromVersion` -- show only breaking changes
- `mode: "compare"` + `fromVersion` + `toVersion` -- property-level diff
- `mode: "migrations"` + `fromVersion` -- auto-migratable changes

---

## Validation Strategy

### Profile Selection

| Profile | When to use | Strictness |
|---------|-------------|------------|
| `minimal` | During editing, quick checks | Most permissive |
| `runtime` | Pre-deployment (RECOMMENDED DEFAULT) | Balanced |
| `ai-friendly` | AI-generated configurations | Reduces false positives |
| `strict` | Production deployment | Most thorough |

Always specify the profile explicitly. Omitting it uses defaults that may not
match your intent.

### The Validation Loop

Telemetry shows this pattern repeats thousands of times:
1. Configure/edit node or workflow
2. Validate (23s avg thinking about errors)
3. Fix errors (58s avg fixing)
4. Validate again
5. Repeat until clean

This is normal and expected. Do not try to get validation right on the first pass.

### validate_node modes
- `mode: "minimal"` -- quick check: what fields are required?
- `mode: "full"` (default) -- comprehensive with errors/warnings/suggestions

### validate_workflow scope
Validates: node configs + connection validity + expression syntax + workflow
structure + AI connections. Use `profile: "runtime"` in options for node-level
validation within workflow context.

### n8n_autofix_workflow
- `applyFixes: false` (default) = preview mode, shows what would change
- `applyFixes: true` = apply fixes
- `confidenceThreshold`: "high", "medium", "low"
- Fix types: expression-format, typeversion-correction, error-output-config,
  webhook-missing-path, typeversion-upgrade, version-migration

---

## Workflow Management

### Smart Parameters (use instead of numeric indices)

**IF node connections** -- use `branch` instead of `sourceIndex`:
```
branch: "true"   --> true output (sourceIndex 0)
branch: "false"  --> false output (sourceIndex 1)
```

**Switch node connections** -- use `case` instead of `sourceIndex`:
```
case: 0  --> first case output
case: 1  --> second case output
case: 2  --> third case output
```

Smart parameters are clearer, less error-prone, and self-documenting.

### Intent Parameter

Always include `intent` in update operations. It describes what you are trying
to accomplish and produces better AI-generated responses:
```
intent: "Add error handling for API failures"
intent: "Connect webhook to Slack notification"
intent: "Activate workflow for production"
```

### Iterative Building Pattern

Telemetry data (31,464 occurrences): workflows are built iteratively,
averaging 56s between edits. This is the expected pattern:

1. Create workflow (or deploy template)
2. Add/configure nodes one at a time
3. Validate after significant changes
4. Fix issues
5. Repeat steps 2-4
6. Activate when ready

Do NOT attempt to build complete workflows in a single operation. The iterative
approach has a 99.0% success rate per operation.

### 17 Operation Types for n8n_update_partial_workflow

Node ops: addNode, removeNode, updateNode, moveNode, enableNode, disableNode
Connection ops: addConnection, removeConnection, rewireConnection, cleanStaleConnections, replaceConnections
Metadata ops: updateSettings, updateName, addTag, removeTag
Activation ops: activateWorkflow, deactivateWorkflow

**updateNode** uses dot notation for nested properties.
**removeNode** accepts node ID or name.
**cleanStaleConnections** removes references to deleted/renamed nodes.
**rewireConnection** atomically changes a connection target (source + from + to).

### Property Removal

Set a property to `undefined` to remove it:
```
updates: { continueOnFail: undefined, onError: "continueErrorOutput" }
```
Useful for migrating from deprecated properties to their replacements.

### AI Connection Types

8 sourceOutput types for AI workflow connections:
- ai_languageModel, ai_tool, ai_memory, ai_outputParser
- ai_embedding, ai_vectorStore, ai_document, ai_textSplitter

Always specify `sourceOutput` when connecting AI nodes. Without it, the
connection type defaults to "main" which is wrong for AI sub-nodes.

### Best-Effort and Preview Modes

- `continueOnError: true` -- apply what works, skip what fails
- `validateOnly: true` -- preview changes without applying

---

## Auto-Sanitization

Runs automatically on ALL nodes during ANY workflow update (create or
update_partial). You do not invoke it -- it happens silently.

### What it fixes
- Binary operators (equals, contains, greaterThan, etc.) --> removes `singleValue`
- Unary operators (isEmpty, isNotEmpty, true, false) --> adds `singleValue: true`
- IF v2.2+ nodes --> adds complete `conditions.options` metadata
- Switch v3.2+ nodes --> adds complete `conditions.options` for all rules
- Invalid operator structures --> corrects to proper format

### What it CANNOT fix
- Broken connections (references to deleted/renamed nodes)
- Branch count mismatches (e.g., 3 Switch rules but only 2 outputs)
- Corrupt workflow states from API inconsistencies

### Rule of thumb
Never manually set `singleValue` on operators. Let auto-sanitization handle it.
If you see operator structure validation errors, just do another update and
auto-sanitization will correct them. For broken connections, use
`cleanStaleConnections`. For deeper issues, use `n8n_autofix_workflow`.

---

## Template System

2,700+ templates available. Four search modes:

| Mode | Use when | Key parameter |
|------|----------|---------------|
| keyword (default) | Know what you want | `query: "webhook slack"` |
| by_nodes | Have specific nodes | `nodeTypes: ["n8n-nodes-base.httpRequest"]` |
| by_task | Know the task type | `task: "webhook_processing"` |
| by_metadata | Filter by attributes | `complexity: "simple"`, `maxSetupMinutes: 15` |

**get_template modes**:
- `structure` -- nodes + connections only (for understanding the pattern)
- `full` -- complete workflow JSON (for deployment or deep inspection)

**n8n_deploy_template** (requires API):
- `autoFix: true` (default) -- auto-fix common issues during deployment
- `autoUpgradeVersions: true` (default) -- upgrade nodes to latest versions
- `stripCredentials: true` (default) -- remove credential references
- Returns: workflow ID, required credentials list, fixes applied

Templates are the fastest way to start. Deploy first, then customize iteratively.

---

## Tool Availability Split

**Always available (no API needed)**:
search_nodes, get_node, validate_node, validate_workflow,
search_templates, get_template, tools_documentation

These tools work offline against the bundled node database and template catalog.

**Requires n8n API (N8N_API_URL + N8N_API_KEY)**:
n8n_create_workflow, n8n_update_partial_workflow, n8n_validate_workflow (by ID),
n8n_list_workflows, n8n_get_workflow, n8n_test_workflow, n8n_executions,
n8n_deploy_template, n8n_autofix_workflow, n8n_workflow_versions

**When API is unavailable**: Use search/get/validate tools to design and validate
node configurations locally. Use templates as reference patterns. Build the
workflow JSON structure, validate it with validate_workflow, and deploy manually.

---

## NEVER

- NEVER use full prefix (n8n-nodes-base.*) with search/validate tools -- use nodes-base.*
- NEVER use short prefix (nodes-base.*) with workflow tools -- use n8n-nodes-base.*
- NEVER default to detail="full" for get_node -- start with standard (1-2K tokens)
- NEVER skip validation profile -- always specify explicitly (runtime recommended)
- NEVER try to build workflows in one shot -- iterate (avg 56s between edits)
- NEVER manually fix singleValue on operators -- auto-sanitization handles it
- NEVER ignore n8n_autofix_workflow for operator structure issues
- NEVER assume all tools need API -- search, get, validate work without it
- NEVER construct nodeType prefixes manually when search_nodes results are available
- NEVER omit sourceOutput when connecting AI nodes -- defaults to "main" which is wrong

---

## Thinking Framework

When working with n8n MCP tools, reason through:

1. **Which prefix?** Am I calling a search/validate tool (short) or workflow tool (full)?
2. **Minimum information?** Start with standard detail. Escalate only if insufficient.
3. **Which profile?** Match validation strictness to the development stage.
4. **Iterative or one-shot?** Always iterative. Plan multiple small operations.
5. **API available?** If not, stick to search/get/validate/template tools.
6. **Auto-sanitization relevant?** If operator errors appear, another update fixes them.
7. **Template shortcut?** Before building from scratch, check if a template exists.
