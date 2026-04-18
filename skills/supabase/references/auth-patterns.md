# Supabase Auth Patterns

Expert-only Auth knowledge. Generic auth basics (signup/signin/signout) are skipped — Supabase docs cover those. This file captures the gotchas that cause silent security holes, broken sessions, and unauthorized access in production.

---

## The getUser vs getSession Decision

This is the single most-misused pair of methods in `@supabase/ssr`. Wrong choice = either insecure (trusts client-tampered tokens) or wasteful (extra network call per request).

| Method | What it does | Network call? | Safe to trust? | Use when |
|--------|-------------|---------------|----------------|----------|
| `getSession()` | Returns the session from local storage / cookies WITHOUT validating with Auth server | NO | **Only the `access_token` payload — JWT signature verified locally if you have JWT secret. The user object is NOT re-validated.** | UI rendering decisions, optimistic checks |
| `getUser()` | Re-fetches user from `auth.users` via `/auth/v1/user` endpoint, validates token server-side | YES | **YES — authoritative** | Server-side authorization, RLS context, anything that gates access |
| `getClaims()` | Returns JWT claims locally; validates signature using JWKS fetched from Supabase. **No round-trip to Auth server.** | First call only (JWKS cache) | YES (claims, not user record) | Performance-sensitive server checks where claims are sufficient |

**Anti-pattern: `getSession()` in middleware for auth gating**
```ts
// WRONG — middleware trusts client cookie without server validation
const { data: { session } } = await supabase.auth.getSession()
if (!session) return redirectToLogin()  // attacker forges cookie, bypasses
```

**Correct: `getUser()` in middleware**
```ts
// RIGHT — re-validates with Auth server
const { data: { user }, error } = await supabase.auth.getUser()
if (error || !user) return redirectToLogin()
```

**Correct alternative: `getClaims()` (faster, still secure)**
```ts
// RIGHT — JWKS-validated claims, no round-trip after first JWKS fetch
const { data: { claims } } = await supabase.auth.getClaims()
if (!claims) return redirectToLogin()
```

**Why this matters:** `getSession()` reads from cookie/storage. A malicious client can craft a cookie with a JWT that LOOKS valid (right structure, expired token re-encoded, etc). Without `getUser()` server validation, your middleware will hand the attacker a session object.

**Cost trade-off:** `getUser()` adds ~50-150ms per request (one round-trip to Auth). For high-RPS endpoints, prefer `getClaims()` (asymmetric JWT signing, JWKS cached).

---

## Server-Side Cookie Handling: The 4 Mistakes

`@supabase/ssr` requires you to implement `cookies.getAll()` and `cookies.setAll()`. Get this wrong and sessions silently expire, refresh tokens get lost, or you leak across users.

### Mistake 1: Forgetting to call `setAll` after Supabase refreshes a token

When the access token expires (default 1 hour), Supabase auto-refreshes using the refresh token. The new tokens are returned via the `setAll` callback. If you don't write them back to the response cookies, the client keeps using the expired token until it fails.

```ts
// WRONG — only reads, never writes back
createServerClient(url, key, {
  cookies: {
    getAll: () => request.cookies.getAll(),
    setAll: () => {} // <-- silently breaks token refresh
  }
})
```

```ts
// RIGHT — forwards new cookies to response
createServerClient(url, key, {
  cookies: {
    getAll: () => request.cookies.getAll(),
    setAll: (cookiesToSet) => {
      cookiesToSet.forEach(({ name, value, options }) =>
        response.cookies.set(name, value, options)
      )
    }
  }
})
```

### Mistake 2: Sharing a single Supabase client across requests on the server

The Supabase client holds session state. If you instantiate it once at module load (singleton) and reuse it across requests, **user A's session leaks into user B's request**.

```ts
// WRONG — module-level singleton on server
const supabase = createServerClient(...)
export { supabase }  // <-- every request shares this
```

```ts
// RIGHT — new client per request
export const createClient = (request, response) =>
  createServerClient(url, key, { cookies: {...} })
```

This is per-request on the SERVER. On the browser, a singleton is fine because each browser tab IS one user.

### Mistake 3: Using `localStorage` storage in SSR contexts

Default Supabase client uses `localStorage`. On the server, `localStorage` is undefined → silent failures, sessions don't persist. Use `@supabase/ssr` (cookie-based) for server contexts. Never use `@supabase/supabase-js` directly for SSR.

### Mistake 4: Setting cookies in a Server Component (Next.js App Router)

Next.js App Router forbids cookie writes inside Server Components (only Server Actions, Route Handlers, and middleware can write cookies). If your server-side `getUser()` triggers a token refresh inside a Server Component, the `setAll` will throw. Solution: do auth checks in middleware (which CAN write cookies), then read user in Server Components from there.

---

## RLS + Auth Integration

### The auth.uid() trap

`auth.uid()` returns the user ID from the JWT. **It returns NULL for unauthenticated requests using the anon key.** RLS policies that compare `user_id = auth.uid()` will silently match `user_id = NULL` rows if any exist.

```sql
-- WRONG — vulnerable if user_id can be NULL
CREATE POLICY "users see own" ON profiles FOR SELECT
USING (user_id = auth.uid())

-- RIGHT — explicit non-null guard
CREATE POLICY "users see own" ON profiles FOR SELECT
USING (auth.uid() IS NOT NULL AND user_id = auth.uid())
```

Or enforce `user_id NOT NULL` at the schema level (preferred).

### Enabling RLS does NOT enable any policy

```sql
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
-- ↑ This LOCKS the table. With no policies, NO ONE can SELECT/INSERT/UPDATE/DELETE
-- (except postgres role and roles with BYPASSRLS).
```

If you enable RLS and forget to add policies, your app appears broken with no obvious error — queries just return 0 rows or fail silently. After enabling RLS, **always add at least one policy per operation you need to allow**.

### `auth.jwt()->>'role'` and the postgres roles trap

```sql
-- This is the Postgres role embedded in the JWT, NOT a custom app role
auth.jwt()->>'role'  -- returns 'authenticated' or 'anon'
```

For app-level roles (admin, member, owner), put them in `app_metadata` (NOT `user_metadata` — see security checklist), and read them via `auth.jwt()->'app_metadata'->>'role'`.

### Custom claims via JWT hooks (Auth Hooks)

Stop adding `user_id` JOINs to every RLS policy. Instead: emit a custom claim once at JWT issuance via an Auth Hook (`custom_access_token_hook`). Store org_id, role, tenant_id in the JWT and read with `auth.jwt()`. Reduces query overhead from N RLS-evaluated joins to zero.

**Setup gotcha:** the hook function must be `SECURITY DEFINER`, owned by the `supabase_auth_admin` role, and granted EXECUTE to `supabase_auth_admin`. Standard `postgres`-owned functions cannot run as Auth Hooks.

---

## MFA: The Two-Tier Session Model

Supabase MFA introduces **AAL** (Authenticator Assurance Level):
- `aal1`: password-only session
- `aal2`: password + verified TOTP/WebAuthn factor

Common mistake: assume `getUser()` returning a user means they completed MFA. It doesn't. They have an aal1 session.

```sql
-- RLS policy that requires MFA for sensitive tables
CREATE POLICY "mfa required" ON billing_records FOR ALL
USING ((auth.jwt()->>'aal')::text = 'aal2')
```

**Step-up flow:** when user wants to access an MFA-gated resource, call `mfa.challenge()` then `mfa.verify()`. The verified session swaps the JWT for an aal2 token. Don't lazy-rely on aal in JWT — explicitly check `aal2` in your RLS or middleware before exposing protected data.

**Listing MFA factors:** `mfa.listFactors()` returns BOTH verified and unverified enrollments. Filter to `verified` ones for the "is MFA enabled?" check, or you'll show enrollment-in-progress users as "MFA enabled."

---

## OAuth: PKCE, State, and the Redirect Trap

### Default flow type: PKCE for SPAs, implicit for legacy

`@supabase/ssr` uses **PKCE** by default (correct for SPAs/server apps). PKCE requires a `code` exchange after the OAuth callback redirects back. You MUST handle the `?code=` query param in your callback route:

```ts
// app/auth/callback/route.ts (Next.js)
export async function GET(request) {
  const code = request.nextUrl.searchParams.get('code')
  if (code) {
    const supabase = createClient()
    await supabase.auth.exchangeCodeForSession(code)  // <-- required
  }
  return NextResponse.redirect('/')
}
```

Without `exchangeCodeForSession`, the user sees a successful redirect but no session is established.

### redirectTo must be in your allowlist

The `redirectTo` URL passed to `signInWithOAuth` must EXACTLY match (or match a wildcard pattern in) your Supabase project's "Redirect URLs" config. Mismatch → OAuth provider rejects with no useful error in the client. Check:
- Trailing slash (`/auth/callback` ≠ `/auth/callback/`)
- Protocol (http vs https)
- Port (development localhost:3000 vs production)

Set both dev and prod URLs in Supabase Dashboard → Auth → URL Configuration.

### Provider tokens are NOT in the session by default

`signInWithOAuth({ provider: 'google' })` → user logs in → session created. **The Google access_token is NOT in the session by default.** It's stored in `auth.identities.identity_data` server-side. To get the provider token client-side (e.g., to call Google APIs), set:

```ts
signInWithOAuth({
  provider: 'google',
  options: { scopes: 'https://www.googleapis.com/auth/calendar.readonly' }
})
// Then in the callback session, provider_token is exposed
```

**Token refresh for provider tokens is YOUR job.** Supabase doesn't refresh Google/GitHub tokens. Store the provider refresh token securely (server-side only) and refresh manually before the access token expires.

---

## Email Confirmation, Password Reset, Magic Links: Common Failures

### "Email not received"

Default Supabase email service is rate-limited (3-4 emails/hour per project). For production, **always configure an SMTP provider** (Resend, AWS SES, Postmark) in Auth → SMTP Settings. Without it, users hit the rate limit and complain "I never got the email" even though the API succeeded.

### Email link expired immediately

Default Supabase magic link / password reset email expires in **1 hour**. If your email provider has delivery delays (especially in compliance-heavy environments), users may not click in time. Adjust `OTP Expiry` in Auth → Email settings (max 86400 seconds = 24h).

### Confirmation redirect loop

Email confirmation links redirect to `/auth/confirm` (or your configured URL) with `token_hash` and `type` query params. If your callback doesn't `verifyOtp({ type, token_hash })`, the user lands logged out and the link is now consumed. Implement:

```ts
const { type, token_hash } = parseSearchParams(request.url)
await supabase.auth.verifyOtp({ type, token_hash })
```

### Password reset not "logging out other devices"

`updateUser({ password })` does NOT invalidate other sessions. To force logout-everywhere on password change, call `auth.signOut({ scope: 'global' })` after the password update (this revokes all refresh tokens for the user).

---

## Anonymous Sign-In and the Linking Flow

`signInAnonymously()` creates a real `auth.users` row with `is_anonymous = true`. Useful for guest carts, demo accounts, etc. Two gotchas:

1. **Anonymous users count toward your MAU billing** unless you delete them via cron. Set up a daily job to delete `is_anonymous = true` users idle > 7 days.

2. **Linking anonymous → permanent account** requires `linkIdentity({ provider: 'email' })` or `updateUser({ email })` while still signed in as the anonymous user. If the user signs out first, the anonymous data is orphaned.

3. **RLS policies should exclude anonymous users from sensitive operations:**
```sql
USING ((auth.jwt()->>'is_anonymous')::boolean = false)
```

---

## Session Lifecycle Cheat Sheet

| Event | Token state | What to do |
|-------|------------|-----------|
| User signs in | New access (1h) + refresh (no expiry by default) | Set cookies via `setAll` |
| Access token expires | Auto-refresh on next API call | `setAll` MUST forward new tokens |
| User signs out (`scope: 'local'`) | Local tokens cleared, server session intact | OK for "this device only" |
| User signs out (`scope: 'global'`) | All refresh tokens revoked across all devices | Use after password reset, account compromise |
| User deleted via Admin API | **Existing access tokens remain valid until expiry** | Call `auth.admin.signOut(userId, 'global')` BEFORE delete |
| Refresh token reuse detected | Session revoked, user must re-auth | Default protection — don't disable |

---

## Admin API: Server-Only, Never in Browser

`supabase.auth.admin.*` requires the `service_role` key. Calling these from the browser exposes service_role and grants full bypass of RLS to any visitor. Always wrap admin calls behind your own backend endpoints with your own auth check.

Common admin operations:
- `admin.createUser({ email, password, email_confirm: true })` — bypass email verification
- `admin.updateUserById(id, { app_metadata: { role: 'admin' } })` — set authorization claims
- `admin.deleteUser(id)` — remove user (does NOT cascade to your app tables; delete those first or use FK ON DELETE CASCADE)
- `admin.listUsers({ page, perPage })` — paginated; default 50, max 1000 per page

---

## When This Skill Has Failed in the Past

- Treating `getSession()` as authoritative for auth gating → fixed by `getUser()` or `getClaims()`
- Forgetting `exchangeCodeForSession` in OAuth callback → users redirected back logged-out
- Singleton server client leaking sessions across users → fixed by per-request client factory
- Default Supabase email service silently rate-limited in prod → fixed by SMTP provider config
- Anonymous user MAU billing surprise → fixed by cleanup cron
