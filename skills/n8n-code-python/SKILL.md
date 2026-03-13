---
name: n8n-code-python
description: "Use when writing Python in n8n Code nodes, using _input/_json/_node
  syntax, or choosing between Beta and Native Python modes. NEVER for JavaScript Code
  nodes (use n8n-code-javascript) or expression fields (use n8n-expression-syntax)."
---

# Python Code Node

## Decision: Python vs JavaScript

Choose JavaScript for 95% of n8n Code node work. Python only when you need:
- `statistics` module (mean, median, stdev -- no JS equivalent in n8n)
- Complex regex with `re` (lookaheads, named groups, multi-pattern extraction)
- Specific stdlib functions (hashlib, urllib.parse, base64 in one operation)

JavaScript advantages in n8n: `$helpers.httpRequest()`, Luxon datetime, broader community support.
If the task is pure data transformation, use JavaScript.

## Before/After: Webhook Data Processing

**BROKEN (3 common mistakes in one):**
```python
import requests  # CRASH: ModuleNotFoundError

data = _json["name"]  # CRASH: KeyError (webhook nests under body)

return {"json": {"greeting": f"Hello {data}"}}  # FAIL: not a list
```

**WORKING:**
```python
name = _json.get("body", {}).get("name", "World")

return [{"json": {"greeting": f"Hello {name}"}}]
```

**Why:** No external imports (stdlib only), webhook data accessed via body key with safe .get() fallback, return is a list of dicts with "json" key.

## Beta vs Native Mode

n8n offers two Python execution modes. Pick one -- never mix their syntax.

**Python (Beta) -- RECOMMENDED:**
- Full helper API: `_input`, `_json`, `_node`, `_now`, `_today`, `_jmespath()`
- Use for all new Python Code nodes

**Python (Native) (Beta):**
- Raw variables only: `_items` (all-items mode), `_item` (each-item mode)
- No `_input`, `_node`, `_now`, `_today`, `_jmespath` helpers
- Use only when you need pure Python without n8n abstraction layer

| Operation | Beta mode | Native mode |
|-----------|-----------|-------------|
| Get all items | `_input.all()` | `_items` |
| Get first item | `_input.first()` | `_items[0]` |
| Current item (each-item) | `_input.item` | `_item` |
| Current item JSON | `_json` | `_item["json"]` |
| Cross-node reference | `_node["Name"]` | Not available |
| Current datetime | `_now` | `datetime.now()` |
| Current date | `_today` | `datetime.today()` |
| JMESPath query | `_jmespath(data, expr)` | Not available |

## The 3 Critical Rules

### Rule 1: Return format is [{"json": {...}}]

Every Code node must return a list of dicts, each with a "json" key.

```python
# CORRECT - single result
return [{"json": {"total": 42, "status": "done"}}]

# CORRECT - multiple results
return [{"json": {"id": 1}}, {"json": {"id": 2}}]

# CORRECT - empty (no output items)
return []

# WRONG - dict without list wrapper (silent failure or crash)
return {"json": {"total": 42}}

# WRONG - missing "json" key (next node gets no data)
return [{"total": 42}]
```

### Rule 2: Webhook data is nested under ["body"]

Webhook node wraps POST/JSON payload under `body`. Headers, query params, method are siblings.

```python
webhook = _input.first()["json"]

# Webhook output structure:
# {"headers": {...}, "params": {}, "query": {...}, "body": {YOUR DATA}, "method": "POST"}

# WRONG - KeyError, your fields are not at root
name = _json["name"]

# CORRECT
name = _json["body"]["name"]

# SAFE
name = _json.get("body", {}).get("name", "fallback")
```

### Rule 3: No {{}} expression syntax in Code nodes

Code nodes use direct Python variable access -- never template expressions.

```python
# WRONG - expression syntax does not work in Code nodes
value = "{{ $json.field }}"

# CORRECT - direct Python access
value = _json["field"]
```

## n8n Python API Reference

### Beta mode helpers (recommended)

```python
# All items from previous node (use in "Run Once for All Items" mode)
items = _input.all()    # Returns list: [{"json": {...}}, ...]

# First item only
first = _input.first()  # Returns dict: {"json": {...}}

# Current item (use in "Run Once for Each Item" mode ONLY)
current = _input.item   # Returns dict: {"json": {...}}
# WARNING: _input.item is None in "All Items" mode -- will cause AttributeError

# Current item's JSON shorthand
data = _json             # Same as _input.item["json"] or _input.first()["json"]

# Cross-node reference by node name
webhook_data = _node["Webhook"]["json"]
api_result = _node["HTTP Request"]["json"]

# Built-in datetime helpers
now = _now               # datetime object for current time
today = _today           # date object for current date

# JMESPath queries on data
result = _jmespath(_json, "body.users[?active==`true`].name")
```

### Native mode variables

```python
# "Run Once for All Items" mode
for item in _items:                    # _items is the full list
    value = item["json"]["field"]

# "Run Once for Each Item" mode
data = _item["json"]                   # _item is the current item
```

### Python-to-JavaScript syntax mapping

| JavaScript ($ prefix) | Python Beta (_ prefix) | Python Native |
|------------------------|------------------------|---------------|
| `$input.all()` | `_input.all()` | `_items` |
| `$input.first()` | `_input.first()` | `_items[0]` |
| `$input.item` | `_input.item` | `_item` |
| `$json` | `_json` | `_item["json"]` |
| `$node["Name"]` | `_node["Name"]` | Not available |
| `$now` | `_now` | N/A |
| `$today` | `_today` | N/A |
| `$jmespath()` | `_jmespath()` | N/A |

Key difference: Python uses underscore `_` prefix. JavaScript uses dollar `$` prefix.
Using `$input` in Python is a syntax error. Using `_input` in JavaScript is undefined.

## The No-External-Libraries Constraint

n8n Python Code nodes have ONLY Python stdlib. No pip install. No venv.

**Available stdlib modules:**
json, datetime, re, base64, hashlib, urllib.parse, urllib.request, math, random,
statistics, collections, itertools, functools, copy, decimal, string, textwrap

**NOT available (ModuleNotFoundError):**
requests, pandas, numpy, scipy, beautifulsoup4/bs4, lxml, selenium, psycopg2,
pymongo, sqlalchemy, flask, fastapi, pillow, openpyxl

**Workarounds for common needs:**

| Need | Blocked library | n8n workaround |
|------|----------------|----------------|
| HTTP requests | requests | HTTP Request node before Code node, or use JavaScript `$helpers.httpRequest()` |
| Data analysis | pandas | List comprehensions + `statistics` module |
| Database queries | psycopg2, pymongo | Postgres/MySQL/MongoDB nodes before Code node |
| HTML parsing | beautifulsoup4 | HTML Extract node, or regex in Code node |
| Excel files | openpyxl | Spreadsheet File node |

`urllib.request.urlopen()` exists in stdlib but is limited (no easy headers, auth, POST body).
Prefer the HTTP Request node for any real API call.

## Rationalizations That Cause Runtime Crashes

| Rationalization | When It Appears | Why It's Wrong |
|---|---|---|
| "I'll use Python because I know it better" | Choosing language for Code node | n8n's JavaScript has httpRequest(), Luxon datetime, and better integration. Python should only be chosen for stdlib-specific needs (statistics, complex regex, hashlib) |
| "I'll just import requests for the API call" | Need to fetch external data | requests is NOT available -- only stdlib. Use HTTP Request node before the Code node, or switch to JavaScript for $helpers.httpRequest() |
| "The data is at _json['email']" | Processing webhook input | Webhook data is nested under body -- _json["body"]["email"] is correct. _json["email"] throws KeyError |
| "I'll return the dict directly" | Writing return statement | Must return [{"json": {...}}] -- a list of dicts with "json" key. Returning {"json": {...}} (no list) silently fails or crashes |
| "I'll use _input.item in All Items mode" | Processing multiple items | _input.item is None in "Run Once for All Items" mode -- it only works in "Run Once for Each Item" mode. Use _input.all() instead |
| "I can mix Beta and Native syntax" | Confused about which mode | Beta uses _input/_json/_node. Native uses _items/_item. They are exclusive -- mixing causes NameError at runtime |
| "I'll use expression syntax in the Code node" | Writing {{$json.field}} in Python | Template expressions only work in node parameter fields. In Code nodes, use direct Python: _json["field"] |

## Anti-Patterns

| Anti-Pattern | What It Looks Like | Why It Fails | Fix |
|---|---|---|---|
| Dollar-sign variables | `$input.all()`, `$json["field"]` | Python syntax error -- $ is not valid in Python identifiers | Use underscore prefix: `_input.all()`, `_json["field"]` |
| Bare dict return | `return {"json": {"total": 42}}` | n8n expects a list, not a dict -- next node receives nothing or crashes | Wrap in list: `return [{"json": {"total": 42}}]` |
| Direct webhook access | `name = _json["name"]` | KeyError -- webhook wraps payload under "body" | Use `_json["body"]["name"]` or `.get("body", {}).get("name")` |
| Expression in code | `value = "{{ $json.field }}"` | Literal string, not evaluated -- template syntax only works in node parameter fields | Use `value = _json["field"]` |
| External imports | `import pandas as pd` | ModuleNotFoundError at runtime -- only stdlib available | Use list comprehensions + statistics module, or pre-process with dedicated nodes |
| All-Items mode with .item | `data = _input.item["json"]` | AttributeError: NoneType -- _input.item is None in All Items mode | Use `_input.all()` to get list, then iterate |

## NEVER

```
NEVER import external libraries (requests, pandas, numpy, bs4) - only stdlib available
NEVER use $input/$json/$node (dollar sign) - Python uses _input/_json/_node (underscore)
NEVER return a plain dict - must return list: [{"json": {...}}] not {"json": {...}}
NEVER access webhook data at root - it is _json["body"]["field"], not _json["field"]
NEVER use {{}} expression syntax in Code nodes - use direct Python: _json["field"]
NEVER choose Python by default - JavaScript has better n8n integration (httpRequest, Luxon)
NEVER use _input/_node/_now/_today/_jmespath in Native mode - only _items/_item available
NEVER mix Beta and Native syntax - _input.all() (Beta) vs _items (Native) are exclusive
NEVER use _input.item in "All Items" mode - it is None and will cause AttributeError
```

## Common Recipes

### Aggregate data from multiple items (All Items mode)
```python
items = _input.all()
total = sum(item["json"]["amount"] for item in items)
count = len(items)
avg = total / count if count > 0 else 0

return [{"json": {"total": total, "count": count, "average": avg}}]
```

### Group items by a field
```python
from collections import defaultdict

items = _input.all()
groups = defaultdict(list)
for item in items:
    key = item["json"]["category"]
    groups[key].append(item["json"])

return [{"json": {"category": k, "items": v, "count": len(v)}} for k, v in groups.items()]
```

### Safe field extraction with defaults
```python
data = _json.get("body", _json)  # Works for both webhook and non-webhook input
name = data.get("name", "Unknown")
email = data.get("email", "")
score = int(data.get("score", 0))  # Cast with default

return [{"json": {"name": name, "email": email, "score": score}}]
```

### Hash and deduplicate
```python
import hashlib

items = _input.all()
seen = set()
unique = []
for item in items:
    key = item["json"]["email"].lower().strip()
    h = hashlib.md5(key.encode()).hexdigest()
    if h not in seen:
        seen.add(h)
        unique.append(item)

return unique  # Already in [{"json": {...}}] format
```

## Thinking Framework

Before writing Python in an n8n Code node, answer these:

1. **Can a built-in node do this?** Set node for field mapping, Filter node for filtering,
   IF/Switch for conditionals, HTTP Request for API calls. Code node is last resort.
2. **Should this be JavaScript instead?** If you need HTTP calls, date math (Luxon),
   or nothing Python-specific -- use JavaScript.
3. **Am I in Beta or Native mode?** Check the Code node dropdown. Use the matching API only.
4. **Is my data from a Webhook?** If yes, access payload via `["body"]`.
5. **Does every code path return [{"json": {...}}]?** Including error/empty cases.
6. **Am I importing only stdlib?** Any `import X` where X is not stdlib will crash at runtime.
