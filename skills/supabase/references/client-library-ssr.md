# Supabase Client Library + SSR Patterns

Expert-only patterns for `@supabase/ssr` and `supabase-js` across Next.js, SvelteKit, Astro, Remix, and React. Generic "how to call supabase" is skipped. This file covers framework-specific cookie handling, the Server Component vs Server Action distinction, and the patterns that prevent session leaks across users.

---

## The Two Packages and When to Use Each

| Package | Use in | Storage | Why |
|---------|--------|---------|-----|
| `@supabase/supabase-js` | Browser-only apps, mobile (React Native), backend scripts where users don't have sessions | localStorage by default | Simpler API, but localStorage is unavailable server-side |
| `@supabase/ssr` | Any framework with server-side rendering (Next.js App Router/Pages Router, SvelteKit, Astro, Remix, Nuxt) | Cookies (you implement the storage adapter) | Cookies are the only universal session mechanism that works in both server and browser |

**Rule:** if your app renders pages on a server AND has authenticated users, you need `@supabase/ssr`. Trying to use base `supabase-js` for SSR-rendered apps causes either no auth on server, or `localStorage is not defined` errors during build.

---

## The Two Critical Architectural Rules

### Rule 1: NEVER share a server client across requests

The Supabase client carries session state. A module-level singleton on the server **leaks user A's session into user B's request**.

```ts
// WRONG — module-level instantiation
const supabase = createServerClient(url, key, {...})
export { supabase }
```

```ts
// RIGHT — factory pattern, called per-request
export function createClient(request, response) {
  return createServerClient(url, key, {
    cookies: {
      getAll: () => request.cookies.getAll(),
      setAll: (cookies) => cookies.forEach(c => response.cookies.set(c.name, c.value, c.options))
    }
  })
}
```

Browser-side singletons are fine — one tab = one user.

### Rule 2: The cookies adapter MUST forward setAll changes to the response

When Supabase auto-refreshes an expired access token (every ~1 hour), the new tokens come back via the `setAll` callback. If you don't write them to the response, the browser keeps using expired tokens until they fail entirely.

```ts
// WRONG — read-only, breaks token refresh
{ getAll: () => request.cookies.getAll(), setAll: () => {} }

// RIGHT — forwards all set operations
{
  getAll: () => request.cookies.getAll(),
  setAll: (cookiesToSet) =>
    cookiesToSet.forEach(({ name, value, options }) =>
      response.cookies.set(name, value, options)
    )
}
```

---

## Next.js App Router (the most-misused setup)

Next.js App Router has THREE distinct server contexts with DIFFERENT cookie capabilities:

| Context | Can READ cookies? | Can WRITE cookies? | Use Supabase here? |
|---------|-------------------|-------------------|-------------------|
| Server Component (page.tsx, layout.tsx) | YES | NO (throws) | Read-only auth checks via `getUser()` |
| Server Action ('use server') | YES | YES | Sign in/out, mutations |
| Route Handler (route.ts) | YES | YES | API endpoints, OAuth callback |
| Middleware (middleware.ts) | YES | YES | Auth gating, session refresh |

### Pattern 1: lib/supabase/server.ts (Server Component reader)

```ts
import { cookies } from 'next/headers'
import { createServerClient } from '@supabase/ssr'

export async function createClient() {
  const cookieStore = await cookies()  // Next.js 15+: must await
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options))
          } catch {
            // Server Components can't set cookies — middleware handles refresh
          }
        }
      }
    }
  )
}
```

**The try/catch is required.** In Server Components, `cookieStore.set()` throws if there's a token refresh attempt. The middleware handles refresh; the Server Component just reads. Wrapping in try/catch lets reads succeed even when refresh would fail.

### Pattern 2: middleware.ts (where session refresh actually happens)

```ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request })

  const supabase = createServerClient(url, key, {
    cookies: {
      getAll: () => request.cookies.getAll(),
      setAll: (cookies) => {
        cookies.forEach(({ name, value }) => request.cookies.set(name, value))
        response = NextResponse.next({ request })  // <-- regenerate response
        cookies.forEach(({ name, value, options }) =>
          response.cookies.set(name, value, options))
      }
    }
  })

  // CRITICAL: Call getUser() to trigger session refresh if needed
  const { data: { user } } = await supabase.auth.getUser()

  if (!user && !request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)']
}
```

**Why `getUser()` matters in middleware:** even if you don't gate routes here, calling `getUser()` triggers token refresh, and the cookies adapter forwards the new tokens to the response. Without this call, sessions silently expire over time.

### Pattern 3: Browser client (lib/supabase/client.ts)

```ts
'use client'
import { createBrowserClient } from '@supabase/ssr'

export const createClient = () =>
  createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
```

Browser singleton is OK here — instantiate once per tab.

### Anti-pattern: using `getSession()` in Next.js middleware

```ts
// WRONG — getSession() doesn't validate with auth server, attacker forges cookie
const { data: { session } } = await supabase.auth.getSession()
if (!session) redirect('/login')
```

```ts
// RIGHT — getUser() round-trips to auth server, validates token
const { data: { user } } = await supabase.auth.getUser()
if (!user) redirect('/login')
```

This single mistake is the most common Supabase Next.js security bug. Audit all middleware files and any server-side auth checks for `getSession()` and replace with `getUser()` (or `getClaims()` if you can use JWT-only validation).

---

## SvelteKit

SvelteKit's `event.cookies` works in `+page.server.ts`, `+layout.server.ts`, `+server.ts`, and `hooks.server.ts`. Pattern lives in `hooks.server.ts`:

```ts
import { createServerClient } from '@supabase/ssr'
import type { Handle } from '@sveltejs/kit'

export const handle: Handle = async ({ event, resolve }) => {
  event.locals.supabase = createServerClient(url, key, {
    cookies: {
      getAll: () => event.cookies.getAll(),
      setAll: (cookies) => cookies.forEach(({ name, value, options }) =>
        event.cookies.set(name, value, { ...options, path: '/' })  // path: '/' is REQUIRED
      )
    }
  })

  const { data: { user } } = await event.locals.supabase.auth.getUser()
  event.locals.user = user

  return resolve(event, {
    filterSerializedResponseHeaders: (name) => name === 'content-range' || name === 'x-supabase-api-version'
  })
}
```

**SvelteKit gotcha #1:** Without `path: '/'`, cookies are scoped to the current request path. Subsequent requests to other paths don't see the session.

**SvelteKit gotcha #2:** `filterSerializedResponseHeaders` for `x-supabase-api-version` is required to prevent SvelteKit from stripping headers needed for `supabase-js` to work correctly client-side.

---

## Astro

Astro middleware in `src/middleware.ts`:

```ts
import { defineMiddleware } from 'astro:middleware'
import { createServerClient, parseCookieHeader } from '@supabase/ssr'

export const onRequest = defineMiddleware(async (context, next) => {
  context.locals.supabase = createServerClient(url, key, {
    cookies: {
      getAll: () => parseCookieHeader(context.request.headers.get('Cookie') ?? ''),
      setAll: (cookies) => cookies.forEach(({ name, value, options }) =>
        context.cookies.set(name, value, options)
      )
    }
  })

  const { data: { user } } = await context.locals.supabase.auth.getUser()
  context.locals.user = user

  return next()
})
```

**Astro gotcha:** `parseCookieHeader` from `@supabase/ssr` (not from `astro:cookies`) — Astro's cookie parser doesn't return the format `getAll()` expects.

---

## Remix

Loader/action pattern in `app/utils/supabase.server.ts`:

```ts
import { createServerClient, parseCookieHeader, serializeCookieHeader } from '@supabase/ssr'

export function createClient(request: Request) {
  const headers = new Headers()

  const supabase = createServerClient(url, key, {
    cookies: {
      getAll: () => parseCookieHeader(request.headers.get('Cookie') ?? ''),
      setAll: (cookies) => cookies.forEach(({ name, value, options }) =>
        headers.append('Set-Cookie', serializeCookieHeader(name, value, options))
      )
    }
  })

  return { supabase, headers }
}
```

Use in loaders:
```ts
export async function loader({ request }: LoaderFunctionArgs) {
  const { supabase, headers } = createClient(request)
  const { data: { user } } = await supabase.auth.getUser()
  return json({ user }, { headers })  // headers MUST be returned for refresh to persist
}
```

**Remix gotcha:** if you forget `{ headers }` in `json()`/`redirect()`, the refresh cookies are lost. Wrap responses to always include the headers — easy to miss in helper functions.

---

## React Native

Use `@supabase/supabase-js` directly with `AsyncStorage`:

```ts
import { createClient } from '@supabase/supabase-js'
import AsyncStorage from '@react-native-async-storage/async-storage'

const supabase = createClient(url, key, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false  // mobile doesn't have URL-based callback
  }
})

// Required: re-init refresh on app foreground
import { AppState } from 'react-native'
AppState.addEventListener('change', (state) => {
  if (state === 'active') supabase.auth.startAutoRefresh()
  else supabase.auth.stopAutoRefresh()
})
```

**Mobile gotchas:**
- `detectSessionInUrl: false` — only web has URL fragments for OAuth
- `AppState` handler is required — Supabase doesn't auto-pause refresh in background, draining battery and risking refresh failures
- For OAuth in React Native, use deep links (`expo-auth-session` or `react-native-app-auth`) — Supabase's web OAuth flow doesn't work natively

---

## Generated Types: `supabase gen types`

Stop typing query results as `any`. Generate TypeScript types from your schema:

```bash
supabase gen types typescript --linked > types/database.ts
# or for a specific project:
supabase gen types typescript --project-id <id> > types/database.ts
```

```ts
import type { Database } from './types/database'
const supabase = createBrowserClient<Database>(url, key)

// Now this is fully typed:
const { data } = await supabase.from('orders').select('id, total, customer:customers(name)')
//      ^? { id: number; total: number; customer: { name: string } }[]
```

**Regenerate after every migration.** Stale types cause silent runtime errors when the schema drifts.

**CI integration:** add `supabase gen types --project-id ${{ secrets.SUPABASE_PROJECT_ID }}` to your pre-commit or CI, fail if `git diff` shows changes (means someone migrated without regenerating types).

---

## PostgREST Query Patterns That Aren't Obvious

### Embedded resources (joins via foreign keys)

```ts
// Single nested resource
.select('*, profile:profiles(name, avatar_url)')

// Multiple nested
.select('*, comments(*, author:profiles(*))')

// Inner join (filter rows where the embedded resource is null)
.select('*, profile:profiles!inner(name)')

// Left join (default — returns rows even if related resource is null)
.select('*, profile:profiles(name)')
```

The `!inner` modifier changes the relational semantics — without it, you get `null` for missing relations; with it, those rows are excluded. Major source of "missing rows" bugs.

### Counting

```ts
// returns count + data
const { data, count } = await supabase.from('orders').select('*', { count: 'exact' })

// returns ONLY count (no data transferred)
const { count } = await supabase.from('orders').select('*', { count: 'exact', head: true })
```

`{ count: 'exact' }` runs a separate `COUNT(*)` query — slow on huge tables. For approximate counts on huge tables, use `'estimated'` (uses Postgres planner stats).

### Filtering on JSONB

```ts
.select('*').eq('metadata->>status', 'active')   // text comparison via ->>
.select('*').filter('metadata->priority', 'gt', 5)  // raw filter for typed comparison
```

Use `->>` for text, `->` for JSON value. Filter operator names: `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `like`, `ilike`, `in`, `is`, `cs` (contains), `cd` (contained-in).

### `.single()` vs `.maybeSingle()`

```ts
.single()       // throws if 0 OR >1 rows match
.maybeSingle()  // returns null if 0, throws if >1
```

Use `.maybeSingle()` for "find by unique key, may not exist" — `.single()` will pollute your error logs with "no rows" errors that aren't actual errors.

---

## Realtime + SSR Considerations

### Don't subscribe to Realtime on the server

Realtime needs WebSockets, which don't make sense in the lifetime of a server response. Subscribe only in client components with proper cleanup.

### Initial state from server, updates from client

Pattern: server-render the page with initial data, then client subscribes to deltas:

```tsx
// Server Component
const initial = await supabase.from('messages').select('*')
return <MessagesClient initial={initial.data} />

// Client Component
'use client'
function MessagesClient({ initial }) {
  const [messages, setMessages] = useState(initial)
  useEffect(() => {
    const channel = supabaseClient.channel(...)
      .on('postgres_changes', {...}, (payload) => setMessages(prev => [...prev, payload.new]))
      .subscribe()
    return () => supabaseClient.removeChannel(channel)
  }, [])
  return <ul>{messages.map(...)}</ul>
}
```

This avoids the loading spinner on first render while keeping reactive updates.

---

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Sessions silently expire after ~1h | `setAll` not implemented or ignored | Implement full forwarding to response |
| User A's data shown to User B | Server client singleton | Per-request factory pattern |
| OAuth redirect lands logged-out | Missing `exchangeCodeForSession` in callback route | Implement `app/auth/callback/route.ts` |
| `cookies()` should be awaited error (Next 15) | Pre-Next 15 sync API still in code | Add `await` |
| `localStorage is not defined` on build | Using `supabase-js` instead of `@supabase/ssr` | Switch packages |
| Middleware auth bypass with forged cookie | Used `getSession()` instead of `getUser()` | Replace all middleware/server gates with `getUser()` or `getClaims()` |
| Cookie not visible across paths in SvelteKit | Missing `path: '/'` in setAll | Add path option |
| Refresh tokens lost in Remix | `headers` not included in `json()` response | Always return headers |

---

## When This Skill Has Failed in the Past

- Module-level server client → cross-user session leak in production
- Empty `setAll` callback → sessions expire after 1h with no user-visible cause
- `getSession()` in middleware → forged-cookie bypass
- React Native without `AppState` handler → battery drain + refresh failures
- Missing `path: '/'` in SvelteKit → user appears logged out on `/dashboard` but logged in on `/`
- Stale generated types after migration → runtime field-not-found errors
