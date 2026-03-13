---
name: n8n-expression-syntax
description: "Use when writing n8n expressions in node fields, using {{}} syntax with
  $json/$node/$now variables, or troubleshooting expressions showing as literal text.
  NEVER for Code node JavaScript (use n8n-code-javascript) or Python (use n8n-code-python)."
---

# n8n Expression Syntax

## The Expression Model

n8n has TWO field modes. Expressions behave differently in each.

### Text Mode Fields (message bodies, descriptions, rich text)
Expressions go inline. No prefix needed.
```
Hello {{$json.body.name}}, your order is confirmed.
```
Adjacent text and expressions auto-concatenate. No JS template literals, no + operator.

### JSON Mode Fields (parameter inputs, property values)
The `=` prefix is REQUIRED before the opening braces:
```json
{
  "email": "={{$json.body.email}}",
  "name": "={{$json.body.name}}",
  "timestamp": "={{$now.toISO()}}"
}
```
Without `=`, the value `{{$json.body.email}}` is treated as a literal string.
With `=` in a text mode field, a literal `=` appears in the output.

### The Universal Rule
ALL expressions require double curly braces: `{{expression}}`.
Without them, text is literal. `$json.email` in a field renders as the string "$json.email".

---

## Core Variables

### $json -- Current Node Output
Access output data of the immediately preceding node:
```
{{$json.fieldName}}
{{$json.nested.property}}
{{$json['field with spaces']}}
{{$json.items[0].name}}
```
After a Webhook node, $json contains headers, params, query, AND body (see Webhook Gotcha below).
After an HTTP Request node, $json contains the response body directly.

### $node["Name"] -- Cross-Node Reference
Access any previous node's output by exact name:
```
{{$node["HTTP Request"].json.data}}
{{$node["Webhook"].json.body.email}}
```
CRITICAL rules:
- Name MUST be in quotes inside brackets
- Name is CASE-SENSITIVE: `$node["HTTP Request"]` works, `$node["http request"]` fails silently
- The `.json` segment is MANDATORY: `$node["Set"].json.value` not `$node["Set"].value`
- Name must match the node label in the workflow editor exactly

### $now -- Luxon DateTime (NOT JS Date)
Returns a Luxon DateTime object. Use Luxon methods only:
```
{{$now.toFormat('yyyy-MM-dd')}}
{{$now.toFormat('HH:mm:ss')}}
{{$now.plus({days: 7}).toFormat('yyyy-MM-dd')}}
{{$now.minus({hours: 24}).toISO()}}
```
Standard JS `new Date()` methods do NOT work on $now.
`DateTime.fromISO()` is available for parsing date strings.

### $env -- Environment Variables
Access server-configured environment variables:
```
{{$env.API_KEY}}
{{$env.DATABASE_URL}}
```

---

## The 3 Critical Gotchas

### Gotcha 1: Webhook .body Nesting

Webhook node output wraps POST data under `.body`:
```
Webhook $json structure:
{
  "headers": {...},
  "params": {...},
  "query": {...},
  "body": {              <-- POST data lives HERE
    "name": "John",
    "email": "john@example.com"
  }
}
```

WRONG: `{{$json.name}}` -- returns undefined
RIGHT: `{{$json.body.name}}` -- returns "John"

This applies everywhere webhook data flows downstream:
- Direct access: `{{$json.body.email}}`
- Cross-node: `{{$node["Webhook"].json.body.email}}`
- In URLs: `https://api.example.com/users/{{$json.body.user_id}}`

Query parameters are at `{{$json.query.paramName}}`, not under body.

### Gotcha 2: No {{}} in Code Nodes

Code nodes execute JavaScript/Python directly. Expression braces are WRONG here.

WRONG (in Code node):
```javascript
const email = '{{$json.email}}';
const name = '={{$json.body.name}}';
```
These produce literal strings "{{$json.email}}" and "={{$json.body.name}}".

RIGHT (in Code node):
```javascript
const email = $json.email;
const name = $json.body.name;
// Or via Code node API:
const email = $input.item.json.email;
const allItems = $input.all();
```

### Gotcha 3: The = Prefix Rule

JSON mode fields: `=` REQUIRED --> `"={{$json.body.email}}"`
Text mode fields: `=` FORBIDDEN --> `{{$json.body.email}}`

Wrong prefix direction:
- Missing `=` in JSON mode: expression treated as literal string
- Extra `=` in text mode: literal "=" prepended to output ("=john@example.com")

---

## Where Expressions Work and Don't

| Field Type                  | Expressions? | Syntax                        |
|-----------------------------|-------------|-------------------------------|
| Text/message fields         | YES         | {{$json.field}}               |
| JSON/parameter fields       | YES         | ={{$json.field}}              |
| URL fields                  | YES         | https://api.com/{{$json.id}}  |
| Header values               | YES         | Bearer {{$env.API_KEY}}       |
| Code node body              | NO          | Use direct JS: $json.field    |
| Webhook path field          | NO          | Static string only            |
| Credential fields           | NO          | Use n8n credential system     |
| Workflow/node name fields   | NO          | Static string only            |

---

## Common Failure Patterns

### "Expression shows as literal text"
CAUSE: Missing `{{}}` braces, or missing `=` prefix in JSON mode.
FIX: Wrap in `{{}}`. In JSON mode, add `=` prefix: `"={{$json.field}}"`.

### "Cannot read property 'X' of undefined"
CAUSE: Wrong data path. Parent object does not exist.
COMMON: Accessing `$json.name` instead of `$json.body.name` after webhook.
FIX: Verify actual data structure in the expression editor preview. Add missing path segments.

### "Undefined" for $node reference
THREE possible causes:
1. Node name case mismatch: `$node["http request"]` vs `$node["HTTP Request"]`
2. Missing `.json` segment: `$node["Set"].value` vs `$node["Set"].json.value`
3. Node name doesn't match: check workflow editor for exact label

### Literal "={{...}}" in output
CAUSE: Using `=` prefix in a text mode field.
FIX: Remove the `=`. Text mode auto-evaluates `{{}}` without it.

### Literal curly braces in output
CAUSE: Triple braces `{{{$json.field}}}` or empty braces `{{}}`.
FIX: Use exactly two braces: `{{$json.field}}`.

---

## $node Reference Checklist

Every $node reference must have ALL of these:
```
{{$node["Exact Name"].json.fieldPath}}
       ^             ^     ^
       |             |     +-- data path
       |             +-- MANDATORY (always .json for data, .binary for files)
       +-- quotes required, case-sensitive, exact match
```

Missing any one of these causes silent failure (undefined, not an error).

---

## Bracket Notation Rules

Dot notation works for simple names: `{{$json.email}}`
Bracket notation REQUIRED when names contain:
- Spaces: `{{$json['first name']}}`
- Special characters: `{{$json['user-id']}}`
- Numbers at start: `{{$json['123field']}}`

Node names always use brackets: `{{$node["Any Name"].json.field}}`

For arrays, use numeric brackets: `{{$json.items[0].name}}`
WRONG: `{{$json.items.0.name}}` -- dot notation with numbers fails.

---

## Text Mode Concatenation

In text mode fields, expressions auto-concatenate with surrounding text:
```
Hello {{$json.body.name}}, your order #{{$json.body.order_id}} is ready.
```

WRONG approaches (do not use):
- JS template literals: `` `Hello ${$json.name}` ``
- String concatenation: `"Hello " + $json.name`
- These produce literal text, not evaluated expressions.

---

## Defensive Expressions (Handling Missing Data)

Production workflows receive incomplete data. Fields may be undefined, null, or empty. Unguarded expressions crash the workflow or produce silent "undefined" strings in output.

### Optional Chaining -- Prevent "Cannot read property" Errors
When the parent object might not exist:
```
UNSAFE:  {{$json.body.user.address.city}}
         -- crashes if body, user, or address is undefined

SAFE:    {{$json.body?.user?.address?.city}}
         -- returns undefined (not an error) if any segment is missing
```

Use `?.` at every uncertain nesting level. After a Webhook, `$json.body` usually exists but inner fields may not.

### Default Values -- Ternary Guard
When a field might be missing and you need a fallback:
```
{{$json.body?.name ? $json.body.name : 'Unknown'}}
{{$json.body?.email ? $json.body.email : 'no-reply@example.com'}}
{{$json.status ? $json.status : 'pending'}}
```

### Default Values -- OR Operator (Short Form)
The `||` operator returns the right side if the left is falsy (undefined, null, empty string, 0):
```
{{$json.body?.name || 'Unknown'}}
{{$json.body?.phone || 'Not provided'}}
```
WARNING: `||` treats `0`, `""`, and `false` as falsy. If those are valid values, use `??` instead.

### Nullish Coalescing -- Preserve 0 and Empty String
The `??` operator returns the right side ONLY if the left is null or undefined (not 0 or ""):
```
{{$json.count ?? 0}}             -- preserves count=0 from API
{{$json.body?.discount ?? 0}}    -- preserves 0% discount
{{$json.body?.notes ?? ''}}      -- preserves empty string
```
Use `??` for numeric fields and boolean-adjacent values. Use `||` for string fields where empty = missing.

### Debugging Undefined Expressions
When an expression returns "undefined" or blank in the output:

**Step 1:** Check the expression editor preview. Click the field and look at the resolved value.
**Step 2:** Simplify to find the break point:
```
Try:     {{$json}}                    -- does the whole object exist?
Then:    {{$json.body}}               -- does body exist?
Then:    {{$json.body.user}}          -- does user exist?
Then:    {{$json.body.user.email}}    -- found the missing level
```
**Step 3:** Fix with optional chaining + default: `{{$json.body?.user?.email || 'missing'}}`

### Combining Guards in JSON Mode
Remember the `=` prefix applies to the whole value:
```json
{
  "email": "={{$json.body?.email || 'fallback@example.com'}}",
  "name": "={{$json.body?.first_name || 'Customer'}}",
  "amount": "={{$json.body?.total ?? 0}}"
}
```

---

## NEVER

- NEVER use `{{}}` in Code nodes -- Code nodes use direct JS/Python. `"{{$json.field}}"` becomes literal text
- NEVER omit `{{}}` in expression fields -- `$json.field` without braces is treated as literal text
- NEVER forget `=` prefix in JSON mode -- `={{$json.field}}` not `{{$json.field}}` in parameter fields
- NEVER access webhook data at root -- it is `{{$json.body.field}}`, not `{{$json.field}}`
- NEVER use wrong case for node names -- `$node["HTTP Request"]` works, `$node["http request"]` fails silently
- NEVER nest curly braces -- `{{{$json.field}}}` is invalid, use `{{$json.field}}`
- NEVER use expressions in credential fields -- use n8n credential system instead
- NEVER use expressions in webhook path -- must be static string
- NEVER omit `.json` in $node references -- `$node["Name"].json.field` not `$node["Name"].field`
- NEVER use JS Date methods on $now -- it is Luxon DateTime, use .toFormat(), .plus(), .minus()

---

## Thinking Framework

Before writing any n8n expression:

1. **What field type?** Text mode = no prefix. JSON mode = needs `=` prefix.
2. **Am I in a Code node?** If yes, use direct JS: `$json.field`. No braces.
3. **Is this webhook data?** If yes, data is under `.body`: `$json.body.field`.
4. **Am I referencing another node?** Use `$node["Exact Name"].json.field` -- case-sensitive, with `.json`.
5. **Do any names have spaces?** Use bracket notation: `$json['field name']`, `$node["Node Name"]`.
6. **Could any field be missing?** Add `?.` for uncertain paths, `|| 'default'` for required output, `?? 0` for numeric fields.
7. **Is this a restricted field?** Webhook paths, credentials, node names = no expressions allowed.
