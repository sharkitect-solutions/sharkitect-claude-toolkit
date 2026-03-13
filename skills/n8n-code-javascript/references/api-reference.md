# n8n Code Node API Reference

> Load this reference when you need exact syntax for an API. The main SKILL.md tells you WHEN to use each API.

## $input -- Accessing Data from Previous Nodes

```javascript
// All Items mode:
$input.all()    // Array of all items: [{json: {...}}, {json: {...}}, ...]
$input.first()  // First item only: {json: {...}}

// Each Item mode:
$input.item     // Current item being processed: {json: {...}}

// IMPORTANT: items have a .json property containing the actual data
const items = $input.all();
const name = items[0].json.name;    // CORRECT
const name = items[0].name;         // WRONG - undefined
```

## $node -- Cross-Node Data Access

Access output from any named node in the workflow. Name must be exact, case-sensitive, quoted.

```javascript
const webhookData = $node["Webhook"].json;
const apiResult = $node["HTTP Request"].json;
const dbRows = $node["Postgres"].json;

// Combine data from multiple nodes
return [{
  json: {
    userId: $node["Webhook"].json.body.userId,
    profile: $node["Get Profile"].json,
    orders: $node["Get Orders"].json
  }
}];
```

## $helpers.httpRequest() -- HTTP Calls from Code

```javascript
const response = await $helpers.httpRequest({
  method: 'POST',           // GET, POST, PUT, DELETE, PATCH
  url: 'https://api.example.com/data',
  headers: {
    'Authorization': `Bearer ${$env.API_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: {                   // Request payload (POST/PUT/PATCH)
    name: $json.body.name
  },
  qs: {                     // Query string parameters
    page: 1,
    limit: 50
  },
  timeout: 10000,           // Milliseconds
  json: true,               // Auto-parse JSON response (default: true)
  simple: false,            // false = don't throw on 4xx/5xx
  resolveWithFullResponse: true  // true = get statusCode + headers + body
});

return [{json: {data: response}}];
```

Key differences from HTTP Request node:
- No built-in auth credential selector -- pass tokens manually via headers
- No built-in pagination -- implement loops yourself
- No built-in retry -- wrap in try/catch and retry manually
- Advantage: can make conditional/dynamic requests based on code logic

## DateTime (Luxon) -- Date/Time Operations

Available as global `DateTime` object. This is Luxon, NOT standard JS Date.

```javascript
const now = DateTime.now();

// Formatting
now.toISO()                          // "2025-01-20T15:30:00.000Z"
now.toFormat('yyyy-MM-dd')           // "2025-01-20"
now.toFormat('yyyy-MM-dd HH:mm:ss') // "2025-01-20 15:30:00"

// Arithmetic
now.plus({days: 7})                  // 7 days from now
now.minus({hours: 2})                // 2 hours ago

// Parsing
DateTime.fromISO('2025-01-20T15:30:00')
DateTime.fromFormat('01/20/2025', 'MM/dd/yyyy')
DateTime.fromSeconds(1737384600)

// Comparison
const target = DateTime.fromISO('2025-12-31');
target.diff(now, 'days').days        // days between dates

// Timezone
now.setZone('America/New_York').toISO()
now.toUTC().toISO()

// Period boundaries
now.startOf('day')                   // midnight today
now.endOf('month')                   // last moment of current month
```

## $jmespath() -- JSON Querying

```javascript
const data = $input.first().json;

// Extract array of names
$jmespath(data, 'users[*].name')

// Filter by condition
$jmespath(data, 'users[?age >= `18`]')

// Sort and take top 5
$jmespath(data, 'users | sort_by(@, &score) | reverse(@) | [0:5]')

// Project specific fields
$jmespath(data, 'users[*].{name: name, email: contact.email}')

// Aggregation
$jmespath(data, 'length(users)')
$jmespath(data, 'sum(products[*].price)')
```

## $getWorkflowStaticData() -- Persistent Storage

Data persists ACROSS workflow executions. Useful for deduplication, counters, rate limiting.

```javascript
const staticData = $getWorkflowStaticData();

// Track last processed ID to avoid reprocessing
const lastId = staticData.lastProcessedId || 0;
const newItems = $input.all().filter(item => item.json.id > lastId);

if (newItems.length > 0) {
  staticData.lastProcessedId = Math.max(...newItems.map(i => i.json.id));
}

return newItems;
```

## $env -- Environment Variables

```javascript
const apiKey = $env.API_KEY;
const baseUrl = $env.BASE_URL;
```

## Available Node.js Modules

```javascript
// crypto - hashing, random bytes
const crypto = require('crypto');
const hash = crypto.createHash('sha256').update('text').digest('hex');

// Buffer - base64 encoding/decoding
const encoded = Buffer.from('Hello').toString('base64');
const decoded = Buffer.from(encoded, 'base64').toString();

// URL / URLSearchParams
const url = new URL('https://example.com/path?key=value');
const params = new URLSearchParams({search: 'query', page: 1});
```

NOT available: axios, lodash, moment, request, or any other npm package. Use `$helpers.httpRequest()` for HTTP and `DateTime` for dates.
