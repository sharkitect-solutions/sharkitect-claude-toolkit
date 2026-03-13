---
name: n8n-code-javascript
description: "Use when writing JavaScript in n8n Code nodes, choosing between Code node
  and built-in nodes, debugging Code node errors (return format, undefined data, silent
  failures), or implementing pagination/retry/dedup in code. NEVER for expression
  fields (use n8n-expression-syntax) or Python Code nodes (use n8n-code-python)."
---

# n8n JavaScript Code Node

## Core Principle

The Code node is the escape hatch, not the default. 80% of workflows need zero Code nodes. When you do need one, failures cluster around three things: wrong return format, wrong data path, and missing error handling. This skill prevents all three.

---

## Decision: Code Node vs Built-in Node

**Use a built-in node when any single node can handle it:**

| Task | Use This Instead | Why Not Code |
|------|-----------------|--------------|
| Rename/add fields | Set node | Faster, no maintenance, no return format risk |
| True/false filter | Filter node | Built-in operators handle 95% of cases |
| Single condition branch | IF node | Cleaner workflow graph |
| Multi-value branch | Switch node | Easier to read and modify |
| HTTP call (standalone) | HTTP Request node | Built-in auth, pagination, retry |
| Date formatting only | Expression: `{{$now.toFormat(...)}}` | No Code node needed for simple format |

**Code node is correct when:**
- Logic requires loops, variables, or multi-step computation
- You need to combine/compare data from multiple items
- API call is conditional on computed logic (not just field values)
- Transformation requires intermediate variables or complex restructuring
- Deduplication, aggregation, or custom sorting across items

**The test:** If you can describe the operation in one clause ("filter where X > Y", "rename A to B"), use a built-in node. If you need two clauses connected by "and then" or "based on", consider Code.

---

## Mode Selection

**"Run Once for All Items" (default -- use 95% of the time)**
- Code executes ONCE. Access data via `$input.all()` or `$input.first()`.
- Use for: aggregation, filtering, sorting, batch transforms, deduplication.

**"Run Once for Each Item" (rare)**
- Code executes separately PER item. Access current item via `$input.item`.
- Use ONLY when: each item needs an independent API call, or per-item error isolation is required.

**Decision rule:** If you need to compare/combine across items, use All Items mode. If each item is 100% independent, consider Each Item mode. When unsure, use All Items -- you can always loop inside.

---

## The 3 Critical Rules

### Rule 1: Return format MUST be `[{json: {...}}]`

Every Code node must return an array of objects, each with a `json` property.

```javascript
// CORRECT - single result
return [{json: {total: 42, status: "done"}}];

// CORRECT - multiple results
return [
  {json: {id: 1, name: "Alice"}},
  {json: {id: 2, name: "Bob"}}
];

// CORRECT - empty (no output items)
return [];

// CORRECT - transforming input
return $input.all().map(item => ({
  json: {...item.json, processed: true}
}));
```

Wrong formats that SILENTLY FAIL or error:
```javascript
return {json: {result: "ok"}};       // missing array wrapper
return [{result: "ok"}];             // missing json property
return [{data: {result: "ok"}}];     // "data" is not "json"
return "done";                       // not an array of objects
```

### Rule 2: Webhook data lives at `$json.body`, not `$json`

The Webhook node wraps incoming payloads under `.body`. Accessing `$json.name` returns undefined.

```javascript
// WRONG - returns undefined
const name = $json.name;

// CORRECT - webhook payload is nested
const name = $json.body.name;

// Full webhook structure:
// $json.headers  - HTTP headers
// $json.body     - POST/PUT payload (YOUR DATA)
// $json.query    - URL query parameters (?key=value)
// $json.params   - URL path parameters
```

### Rule 3: No `{{}}` expression syntax in Code nodes

`{{$json.field}}` is expression syntax for Set/IF/HTTP Request nodes. In Code nodes, use plain JavaScript.

```javascript
// WRONG - treated as literal string, not evaluated
const name = "{{ $json.name }}";

// CORRECT - direct JavaScript access
const name = $json.name;
const name = $input.first().json.name;
```

---

## API Selection: What to Use When

Don't memorize API syntax -- know WHEN to reach for each tool. Full syntax in `references/api-reference.md`.

| You Need To... | Use This | Key Gotcha |
|----------------|----------|------------|
| Read data from previous node | `$input.all()` / `$input.first()` | Items have `.json` property: `items[0].json.name` not `items[0].name` |
| Read data from a specific node | `$node["Exact Name"].json` | Case-sensitive. Quotes required. `.json` mandatory. |
| Make an HTTP request | `$helpers.httpRequest({...})` | Must `await`. No built-in auth/retry/pagination. |
| Format/compare dates | `DateTime` (Luxon) | NOT JS Date. Use `.toFormat()`, `.plus()`, `.minus()` |
| Query complex JSON | `$jmespath(data, 'path')` | First arg is the object, not `$input` |
| Persist data across runs | `$getWorkflowStaticData()` | Mutate the object directly; changes auto-save |
| Read env variables | `$env.VAR_NAME` | Read-only. Set in n8n server config, not workflow |
| Hash/encode data | `require('crypto')`, `Buffer` | Only crypto, Buffer, URL, URLSearchParams available |

---

## Error Diagnosis & Recovery

### "ERROR: Code doesn't return items properly"
**Cause:** Return value isn't `[{json: {...}}]`.
**Fix:** Check every return path. Common traps:
```javascript
// TRAP 1: .map() without json wrapper
return items.map(i => i.json);           // WRONG
return items.map(i => ({json: i.json})); // CORRECT

// TRAP 2: conditional return misses a branch
if (condition) {
  return [{json: {result: "yes"}}];
}
// MISSING: no return for else branch -- returns undefined
// FIX: always return [] for empty case
return [];

// TRAP 3: async function forgot return
const data = await $helpers.httpRequest({...});
// forgot to return! Node outputs nothing
return [{json: data}]; // FIX
```

### "Cannot read property 'X' of undefined"
**Cause:** Data path is wrong. The object you're accessing doesn't exist.
**Diagnosis pattern:**
```javascript
// Step 1: Log what you actually have
const items = $input.all();
return [{json: {debug_first_item: items[0]?.json, debug_count: items.length}}];
// Run once, check output, then write real logic
```
**Common causes:**
- After webhook: data is at `$json.body.field`, not `$json.field`
- Cross-node: missing `.json` segment: `$node["Name"].json.field`
- Empty input: previous node returned 0 items

### Silent empty output (no error, no data)
**Cause:** Code ran but returned `[]` or all items were filtered out.
**Diagnosis:**
```javascript
const items = $input.all();
if (items.length === 0) {
  return [{json: {error: "NO INPUT ITEMS", hint: "Check previous node output"}}];
}
// ... rest of logic
```

### "$helpers.httpRequest is not a function"
**Cause:** Missing `await` or typo in method name.
**Fix:** Always `await $helpers.httpRequest({...})`. The `$helpers` object is always available -- if it's "not a function", you likely have a typo.

### "DateTime is not defined"
**Cause:** Using `DateTime` in an environment where Luxon isn't loaded (rare), or typo.
**Fix:** `DateTime` is a global in n8n Code nodes -- no import needed. Check capitalization: `DateTime`, not `datetime` or `Datetime`.

---

## Production Patterns

### Pagination Loop
```javascript
const allResults = [];
let page = 1;
const pageSize = 100;

while (true) {
  const response = await $helpers.httpRequest({
    method: 'GET',
    url: `https://api.example.com/items`,
    qs: { page, limit: pageSize },
    json: true,
    simple: false
  });

  if (!response || !response.data || response.data.length === 0) break;
  allResults.push(...response.data);
  if (response.data.length < pageSize) break; // last page
  page++;
  if (page > 50) break; // safety cap
}

return allResults.map(item => ({json: item}));
```

### Retry with Backoff
```javascript
async function withRetry(fn, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === maxRetries) throw err;
      // exponential backoff: 1s, 2s, 4s
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt - 1)));
    }
  }
}

const data = await withRetry(() =>
  $helpers.httpRequest({ method: 'GET', url: 'https://api.example.com/data', json: true })
);
return [{json: data}];
```

### Deduplication Using Static Data
```javascript
const staticData = $getWorkflowStaticData();
const seen = new Set(staticData.processedIds || []);
const items = $input.all();

const newItems = items.filter(item => {
  if (seen.has(item.json.id)) return false;
  seen.add(item.json.id);
  return true;
});

staticData.processedIds = [...seen].slice(-10000); // cap memory
return newItems.length > 0 ? newItems : [{json: {status: "no_new_items"}}];
```

### Safe Data Access (Defensive)
```javascript
// When upstream data shape is uncertain, guard access:
const items = $input.all();
return items.map(item => {
  const d = item.json || {};
  return {
    json: {
      name: d.body?.name || d.name || 'unknown',
      email: d.body?.email || d.email || '',
      id: d.body?.id ?? d.id ?? null,
    }
  };
});
```

---

## Thinking Framework

Before writing a Code node, answer these questions:
1. **Can a built-in node do this?** Set/Filter/IF/Switch handles it? Use that instead.
2. **All Items or Each Item?** Default: All Items unless per-item API calls needed.
3. **Where is my data?** `$input.all()` for batch, `$input.first()` for single, `$node["Name"].json` for specific node.
4. **Is this downstream of a Webhook?** If yes, actual data is at `.body`.
5. **Does every return path produce `[{json: {...}}]`?** Check if/else branches, empty cases, error paths.
6. **What fails at runtime?** Add guards for empty input, missing fields, API timeouts. Return diagnostic data instead of crashing silently.

---

## NEVER

- NEVER return a plain object -- `return {json: {...}}` silently breaks. MUST be `[{json: {...}}]`
- NEVER use `{{}}` expression syntax inside Code nodes -- use direct JS: `$json.field` not `"{{$json.field}}"`
- NEVER access webhook payload at root -- data is at `$json.body.field`, not `$json.field`
- NEVER use Code node for simple field rename/filter -- use Set/Filter node (faster, no maintenance)
- NEVER forget the `json` wrapper in return items -- `[{field: value}]` silently fails, must be `[{json: {field: value}}]`
- NEVER use `$input.item` in "All Items" mode -- it is undefined. Use `$input.all()`
- NEVER use `$input.all()` in "Each Item" mode -- use `$input.item` instead
- NEVER access `items[0].name` -- item data is at `items[0].json.name` (the `.json` property is required)
- NEVER use `moment` or `new Date()` for formatting -- use the built-in `DateTime` (Luxon) object
- NEVER import npm packages -- they are not available. Use n8n built-ins ($helpers, DateTime, crypto, Buffer)
- NEVER return without checking all code paths -- missing return in an else/catch branch produces silent empty output
- NEVER make `$helpers.httpRequest()` calls without `await` -- you'll get a Promise object instead of data
