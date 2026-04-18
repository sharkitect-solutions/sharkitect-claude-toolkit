# Supabase Edge Functions Patterns

Expert-only Edge Functions knowledge. Generic Deno tutorials are skipped. This file covers the runtime constraints, secret handling, deployment edges, and the specific gotchas that distinguish Edge Functions from Node.js Lambdas.

---

## Runtime Reality: It's Deno, Not Node

Edge Functions run on a **Deno runtime** (currently Deno 1.x, migrating toward Deno 2.x). The most common build/deploy failures stem from assuming Node.js semantics.

### The Six Things That Break in Deno That Work in Node

| Node | Deno equivalent | Why |
|------|-----------------|-----|
| `require('x')` | `import x from 'npm:x'` or `import x from 'jsr:@scope/x'` | Deno has no CommonJS in functions |
| `process.env.X` | `Deno.env.get('X')` | No `process` global |
| `__dirname` / `__filename` | `import.meta.url` + URL parsing | ESM has no Node module shims |
| `Buffer.from(x).toString('base64')` | `btoa(x)` / `atob(x)` or `encode/decode` from `jsr:@std/encoding/base64` | Buffer doesn't exist (some shims work, prefer std lib) |
| `fs.readFile` | `Deno.readTextFile` (with `--allow-read` permission, granted by default in Edge Functions) | Different API surface |
| `setTimeout(fn, ms).unref()` | No equivalent | Background timers keep the function alive past response → cold start cost |

### NPM packages: prefer `npm:` specifier over bundling

```ts
// Deno can import npm packages directly — no install, no package.json
import { Resend } from 'npm:resend@4.0.0'
import { z } from 'npm:zod@3.22.0'
```

**Pin versions explicitly.** Without a pinned version (`npm:resend` instead of `npm:resend@4.0.0`), each cold start may resolve a different version, causing intermittent failures.

### Avoid these npm packages (broken or expensive in Deno):

- `node-fetch` — Deno has native `fetch`, the npm version conflicts with the global
- `crypto` from npm — use `globalThis.crypto` or `jsr:@std/crypto`
- Heavy bundles (`firebase-admin`, full `aws-sdk`) — pull MBs of code per cold start
- Anything using native bindings (`bcrypt`, `sharp`, `canvas`) — fails to load

For password hashing use `npm:bcryptjs` (pure JS) or Deno's WebCrypto with PBKDF2/Argon2 via `jsr:@stdext/crypto`.

---

## The Cold Start Cost Model

Edge Functions are NOT always-warm. Each region has a cold start cost. Understanding this changes architecture decisions.

| Stage | Typical duration | What happens |
|-------|-----------------|--------------|
| First invocation | 100-1000ms | Container boot + JS module fetch + import resolution |
| Warm invocation (within ~10 min idle) | 5-50ms | Function code already loaded |
| Re-cold after idle | Same as first | Container reaped, restart from scratch |

**Implications:**
- Heavy `import` chains = expensive cold starts. Lazy-import expensive modules inside the handler if they're conditional.
- Module-level fetches (`const config = await fetch(...)`) run on EVERY cold start. Cache via Deno KV or compute once and inline.
- Synchronous DB-pool initialization at module load adds 200-500ms to first request. Use lazy init.

```ts
// Anti-pattern: heavy module-level work
import { Resend } from 'npm:resend@4.0.0'
const resend = new Resend(Deno.env.get('RESEND_KEY'))  // initialized on cold start

// Better: lazy init, only paid on first use
let _resend: Resend | undefined
const getResend = () => _resend ??= new Resend(Deno.env.get('RESEND_KEY')!)

Deno.serve(async (req) => {
  // ... use getResend() only when sending email
})
```

---

## Secrets and Environment Variables

### The four sources of secrets, in order of precedence:

1. **Runtime-injected by Supabase platform** (always available, can't be overridden):
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_DB_URL`
2. **Custom secrets set via CLI/Dashboard** (`supabase secrets set NAME=value`)
3. **Local `.env` file** for `supabase functions serve` only (NEVER deployed)
4. **`.env.local` / `.env`** in your repo — DO NOT put secrets here for committed projects

### The naming trap

```bash
# WRONG — Supabase REJECTS any secret starting with SUPABASE_
supabase secrets set SUPABASE_API_KEY=xxx
# Error: "Reserved prefix"

# Use a different prefix
supabase secrets set MY_API_KEY=xxx
```

The `SUPABASE_` prefix is reserved for platform-managed secrets. Custom secrets must use a different prefix.

### Multi-environment secrets

Supabase has no built-in `dev/staging/prod` secret namespacing. Use separate Supabase projects per environment, OR prefix your secret names: `DEV_STRIPE_KEY`, `PROD_STRIPE_KEY`, and read by env in code:

```ts
const env = Deno.env.get('APP_ENV') ?? 'production'
const stripeKey = Deno.env.get(`${env.toUpperCase()}_STRIPE_KEY`)
```

### Inspecting deployed secrets

```bash
supabase secrets list  # names only, NEVER values
```

There is no "view secret value" — once set, the value is write-only via the API. To rotate, set a new value.

---

## Function-to-Function Authorization

A common pattern: Function A calls Function B. The auth handling is non-obvious.

### Option 1: Forward the user's JWT (most common)

```ts
// Function A receives a user JWT, forwards it to Function B
const userJwt = req.headers.get('Authorization')  // "Bearer xxx"
const res = await fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/function-b`, {
  headers: {
    'Authorization': userJwt!,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({...})
})
```

Function B then sees the user's session via `req.headers.get('Authorization')` and can apply user-scoped RLS via `createClient(url, anon, { global: { headers: { Authorization: userJwt } } })`.

### Option 2: Service-to-service (no user context)

```ts
const res = await fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/function-b`, {
  headers: {
    'Authorization': `Bearer ${Deno.env.get('SUPABASE_ANON_KEY')}`,
    'Content-Type': 'application/json'
  }
})
```

Function B receives the anon JWT — no `auth.uid()` available. Use service_role inside Function B for privileged DB operations, OR explicitly pass user_id in the request body and validate.

### The `verify_jwt` config trap

```toml
# supabase/config.toml
[functions.public-webhook]
verify_jwt = false  # webhook from Stripe — no user JWT
```

If `verify_jwt = true` (default) and a request arrives without a valid JWT, Supabase rejects it BEFORE your function runs — you can't even log the failed attempt. For public endpoints (webhooks, public APIs), set `verify_jwt = false` AND implement your own auth (signature verification, API key check) inside the function.

---

## Webhook Endpoints: The Three Hardening Steps

Edge Functions are commonly used for Stripe / GitHub / generic webhook receivers. Always:

### 1. Verify the signature BEFORE doing any work

```ts
// Stripe example
import Stripe from 'npm:stripe@14.0.0'
const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!)
const signature = req.headers.get('stripe-signature')!
const body = await req.text()  // MUST read as raw text, not JSON

let event
try {
  event = stripe.webhooks.constructEvent(
    body, signature, Deno.env.get('STRIPE_WEBHOOK_SECRET')!
  )
} catch (err) {
  return new Response('Invalid signature', { status: 400 })
}
```

**Critical:** read body as `req.text()`, not `req.json()`. Stripe signature verification needs the EXACT raw bytes. Re-serializing JSON changes whitespace and breaks the signature.

### 2. Idempotency via deduplication

Webhooks retry. If your function takes 30s to process and returns a timeout, the provider retries — and you process the event twice. Insert event IDs into a dedup table:

```sql
CREATE TABLE webhook_events_processed (
  event_id text PRIMARY KEY,
  processed_at timestamptz DEFAULT now()
);
```

```ts
const { error } = await supabase
  .from('webhook_events_processed')
  .insert({ event_id: event.id })

if (error?.code === '23505') {  // unique_violation
  return new Response('Already processed', { status: 200 })
}
```

### 3. Return 200 fast, do work async via Background Tasks

Webhook providers retry on slow responses (Stripe: 30s). For heavy work, queue it via pgmq or call another function with `EdgeRuntime.waitUntil`:

```ts
Deno.serve((req) => {
  const heavyWork = async () => { /* ... */ }
  // @ts-ignore - Supabase-specific
  EdgeRuntime.waitUntil(heavyWork())
  return new Response('ok', { status: 200 })
})
```

`waitUntil` lets the response return while the promise continues in the background until the function instance is reaped.

---

## Database Connections from Edge Functions

### Use `supabase-js` from inside Edge Functions, not raw `pg`

```ts
import { createClient } from 'jsr:@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!  // bypasses RLS
  // OR Deno.env.get('SUPABASE_ANON_KEY')! + user JWT for RLS-respecting access
)
```

Why not raw `pg`/`postgres-js`? Each Edge Function instance is short-lived and may be cold-started in any region. Direct postgres connections need to go through Supavisor (the connection pooler) to avoid exhausting DB connections. The `supabase-js` client uses the PostgREST API which is already pooled.

If you genuinely need direct SQL (raw queries that PostgREST can't express), use the **transaction pooler** URL (port 6543) NOT the direct connection (5432):

```ts
import postgres from 'npm:postgres@3.4.0'
const sql = postgres(Deno.env.get('SUPABASE_DB_URL')!.replace(':5432/', ':6543/'), {
  prepare: false  // CRITICAL — Supavisor transaction mode does not support prepared statements
})
```

**`prepare: false` is mandatory.** Without it, every query throws `prepared statement "X" already exists` after the first invocation.

---

## Scheduled / Cron Functions

Two ways to schedule Edge Functions:

### Option 1: pg_cron + http extension (older, more flexible)

```sql
-- One-time setup
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS http;

-- Schedule a daily job at 3am UTC
SELECT cron.schedule(
  'daily-report',
  '0 3 * * *',
  $$
    SELECT net.http_post(
      url := 'https://<project>.supabase.co/functions/v1/daily-report',
      headers := jsonb_build_object(
        'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key'),
        'Content-Type', 'application/json'
      ),
      body := '{}'::jsonb
    );
  $$
);
```

### Option 2: Cron Schedules in Dashboard (newer, simpler)

Supabase Dashboard → Edge Functions → [function] → Schedule → set cron expression. Manages auth automatically.

### Cron gotchas

- `pg_cron` runs in **UTC only** — adjust expressions for local time.
- `cron.schedule` is idempotent BUT changing the SQL of an existing job requires `cron.unschedule` first then `cron.schedule` again — re-running with the same name doesn't update the body.
- The schedule fires reliably, but Edge Function execution is best-effort. Long-running jobs may be cut off at the timeout limit.

---

## Function Limits

| Limit | Value | What happens at limit |
|-------|-------|----------------------|
| CPU time per invocation | ~150-400ms (varies by tier) | Function killed, 504 returned |
| Wall clock per invocation | 25 seconds (free), 150 seconds (paid) | Same |
| Memory | 256MB | OOM, function dies |
| Request body size | 6MB | 413 returned before function runs |
| Response body size | 6MB | 502 returned |
| Concurrent invocations per project | 1000s (no hard limit, soft scaling) | Cold starts amplify |

For >25s work: split into orchestrator function + background tasks via `EdgeRuntime.waitUntil` or pgmq queue + worker functions.

For >6MB responses: stream via `Response(new ReadableStream(...))` or write to Storage and return a signed URL.

---

## Deploy and Local Dev

### Local serve uses different env loading

```bash
supabase functions serve  # uses ./supabase/.env (NOT .env.local)
```

Local `.env` for `supabase functions serve` is in `supabase/.env` by convention. Putting secrets in repo `.env.local` won't work for function serving.

### Deploying

```bash
supabase functions deploy <function-name>            # deploy single function
supabase functions deploy <function-name> --no-verify-jwt  # public endpoint
supabase functions deploy                            # deploy ALL functions (dangerous)
```

The `--no-verify-jwt` flag at deploy is now superseded by `verify_jwt` in `config.toml` — prefer the config file approach so the setting is version-controlled.

### Import map (advanced)

For complex projects, use `supabase/functions/import_map.json` to centralize npm/jsr versions across all functions. This avoids version drift between functions.

---

## When This Skill Has Failed in the Past

- Using `process.env` instead of `Deno.env.get()` → reference error
- Module-level heavy work → 1-2s cold starts
- Forgetting `prepare: false` on direct postgres connection → broken after first invocation
- Reading webhook body as JSON before signature verify → signature mismatch
- `verify_jwt = true` on a public webhook endpoint → all webhooks rejected
- Trying to set a secret with `SUPABASE_` prefix → reserved name error
- Naming both an env var and a CLI secret → CLI secret takes precedence in deployed function but not local serve
