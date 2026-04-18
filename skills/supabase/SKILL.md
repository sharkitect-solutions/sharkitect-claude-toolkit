---
name: supabase
description: "Use when doing ANY task involving Supabase products: Database (Postgres + RLS), Auth (sessions, JWT, getUser/getSession/getClaims, MFA, OAuth, magic links), Edge Functions (Deno runtime, secrets, cron, webhooks), Realtime (postgres_changes, broadcast, presence), Storage (buckets, signed URLs, transformations), Vectors (pgvector, HNSW, IVFFlat), Cron (pg_cron), Queues (pgmq); client libraries supabase-js and @supabase/ssr in Next.js / React / SvelteKit / Astro / Remix / React Native; Supabase CLI (supabase migration, db query, db advisors), Supabase MCP server, Postgres extensions (pg_graphql, pg_net, pg_vector, vault). Do NOT use for: deep Postgres query/index/schema optimization (use supabase-postgres-best-practices skill), Realtime WebSocket-level scaling and connection-drop debugging (use supabase-realtime-optimizer agent), generic database schema design without Supabase context (use database skill), generic backend architecture without Supabase (use senior-backend skill)."
metadata:
  author: supabase (optimized by Sharkitect Digital)
  version: "1.0.0"
---

# Supabase

Production-ready expertise across the full Supabase product surface. The companion files contain expert-only knowledge — version-specific gotchas, security traps, scaling failure modes, and named anti-patterns. This entry point is the orchestration layer: when to load which file, how to make architectural choices, and the named patterns to avoid.

**Skill design pattern:** Process — a ~280-line SKILL.md orchestrating 6 substantive reference companions (~290-440 lines each). The orchestration layer is intentionally dense with decision tools (decision trees, named anti-patterns, scope routing); deep technical patterns live in the companions and load only when the request triggers them.

---

## File Index

Load companion files only when the request matches the trigger. Loading everything wastes context.

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `SKILL.md` | Always | — |
| `references/auth-patterns.md` | Auth flows (signup/signin/signout), session management, JWT, MFA, OAuth callbacks, password reset, getUser vs getSession debate, RLS-from-auth integration, anonymous users | Pure DB queries unrelated to auth, frontend rendering without auth context |
| `references/realtime-patterns.md` | Subscribing to Postgres changes, broadcast messaging, presence tracking, channel cleanup, REPLICA IDENTITY config, channel RLS | DB schema, Auth flows, file uploads |
| `references/edge-functions-patterns.md` | Writing or deploying Edge Functions, Deno runtime issues, secrets, scheduled functions, webhooks, function-to-function auth, postgres connections from functions | Frontend code, DB-only tasks, browser-side patterns |
| `references/storage-patterns.md` | Bucket configuration, file uploads, RLS for storage.objects, signed URLs, image transformations, CORS for uploads, large file uploads | DB tables unrelated to files, Auth, Edge Functions |
| `references/client-library-ssr.md` | Setting up @supabase/ssr in Next.js / SvelteKit / Astro / Remix, cookie handling, server-side auth checks, generated TypeScript types, PostgREST query patterns | Pure Edge Function code, mobile-only React Native |
| `references/vectors-cron-queues.md` | pgvector embedding storage and search (HNSW, IVFFlat), pg_cron scheduled SQL, pgmq message queues, other Postgres extensions (pg_net, vault) | Auth, Storage, Realtime, frontend code |
| `references/skill-feedback.md` | The user reports this skill gave incorrect guidance and wants to file feedback to maintainers | Any other use |

**Routing examples:**
- "Why is my middleware sometimes returning the wrong user?" → `auth-patterns.md` (getSession vs getUser) + `client-library-ssr.md` (Next.js middleware pattern)
- "My image upload returns 200 but the file isn't replaced" → `storage-patterns.md` (upsert permission trap)
- "How do I run a daily report?" → `edge-functions-patterns.md` (cron section) + `vectors-cron-queues.md` (pg_cron details)
- "How do I do similarity search on documents?" → `vectors-cron-queues.md` (HNSW vs IVFFlat decision)

---

## Scope Boundary

| Request Type | Use This Skill | Use Instead |
|--------------|---------------|-------------|
| Anything Supabase-product-specific | YES | — |
| Deep Postgres query plans, EXPLAIN ANALYZE, advanced indexing strategies, schema design beyond basics | Cross-reference | `supabase-postgres-best-practices` |
| Realtime WebSocket-level connection drops, regional latency, channel scaling | Cross-reference | `supabase-realtime-optimizer` agent |
| Generic SQL not tied to Supabase | NO | `database` skill |
| Backend API design without Supabase | NO | `senior-backend` skill |
| Generic auth concepts (OAuth theory, OWASP) | NO | `security-best-practices` |
| Frontend component design unrelated to Supabase | NO | `frontend-design` |

---

## Core Principles (5)

### 1. Supabase changes frequently — verify against current docs before implementing

Function signatures, config.toml settings, and API conventions change between versions. Do not rely on training data. Use the documentation access methods below before implementing any feature you haven't recently confirmed.

### 2. Verify your work after every change

Run a test query / hit the endpoint / check the dashboard after implementing a fix. A fix without verification is incomplete. Supabase has many silent failure modes (RLS denies returning empty arrays, cookies not forwarded, replica identity wrong) where the symptom only appears at runtime in a specific scenario.

### 3. Recover from errors, don't loop

If an approach fails after 2-3 attempts, stop and reconsider. Try a different method, check Supabase Dashboard logs (Database → Logs, Edge Functions → Logs, Auth → Logs), inspect the error more carefully. Supabase issues are not always solved by retrying — and the answer is not always in the logs you'd guess first.

### 4. RLS by default in exposed schemas

Enable RLS on every table in any exposed schema (especially `public`). Tables in exposed schemas are reachable through the Data API. After enabling RLS, **add at least one policy per operation you need to allow** — enabled RLS with no policies LOCKS the table. For private schemas, prefer RLS as defense in depth.

### 5. Authorization data goes in app_metadata, NEVER user_metadata

`raw_user_meta_data` is user-editable and appears in `auth.jwt()`. It is unsafe for RLS policies or any other authorization logic. Store roles, tenant IDs, permissions in `raw_app_meta_data` / `app_metadata` instead. This is the single most-violated security rule in Supabase apps.

---

## Named Anti-Patterns (memorize these — they cause silent vulnerabilities)

Each pattern links to the companion file with the deeper diagnostic walkthrough.

| Pattern | What It Is | Consequence | Fix | Deep dive |
|---------|-----------|-------------|-----|-----------|
| **The Silent UPDATE** | UPDATE policy without matching SELECT policy | UPDATE silently returns 0 rows — no error, no change | Always pair UPDATE with SELECT policy on same table | `auth-patterns.md` (RLS+Auth integration) |
| **The Phantom Migration** | Using `apply_migration` to iterate locally instead of `execute_sql` | Migration history bloats with experimental SQL; `db diff` produces empty/conflicting output; can't iterate | Use `execute_sql` for iteration; only call `apply_migration` to commit final SQL | `SKILL.md` (Schema Change Workflow) |
| **The Editable JWT** | Using `user_metadata` for authorization data (roles, tenant_id) in RLS or middleware | Any user can edit their own role to "admin" via the auth API | Move to `app_metadata` (only service_role can write) | `auth-patterns.md` (RLS+Auth, custom claims) |
| **The Browser-Leaked Service Key** | Putting `service_role` key in `NEXT_PUBLIC_*` env var or any browser-exposed code | Full RLS bypass for any visitor; total data compromise | Use anon/publishable key in browser; service_role only on server, never prefixed with `NEXT_PUBLIC_` | `client-library-ssr.md` (Browser client) |
| **The Bypass View** | Creating a view in Postgres 15+ without `WITH (security_invoker = true)` | View runs as creator role, bypassing RLS for the calling user | Always create views with `WITH (security_invoker = true)`; for older Postgres, revoke from anon/authenticated and put in unexposed schema | `SKILL.md` Security Checklist (RLS section) |
| **The Forged Session** | Using `getSession()` for auth gating in middleware or server-side checks | Attacker forges a cookie that looks valid; `getSession()` returns it without validating with auth server | Use `getUser()` (network round-trip) or `getClaims()` (JWKS-validated) | `auth-patterns.md` (getUser vs getSession decision) |
| **The Singleton Server Client** | Module-level `createServerClient(...)` shared across requests | User A's session leaks into user B's request | Per-request client factory; instantiate inside the handler | `client-library-ssr.md` (Two architectural rules) |
| **The Lost Refresh** | `setAll` callback in cookies adapter is empty or doesn't forward to response | Sessions silently expire after access token expiry (~1h); user appears logged out with no event | Implement full `setAll` that writes every cookie back to the response | `auth-patterns.md` (Server-side cookie handling) + `client-library-ssr.md` (per-framework patterns) |
| **The Upsert Trap** | Storage RLS with INSERT-only policy, then using `upsert: true` | Replace operation silently no-ops; first upload works, replacement appears successful but file unchanged | Grant SELECT + INSERT + UPDATE for full upsert support | `storage-patterns.md` (Upsert Permission Trap) |
| **The Channel Leak** | React effect creating a Realtime channel without `removeChannel` cleanup | One channel per render → memory leak + duplicate handlers + rate limit hit | Always pair `channel.subscribe()` with `removeChannel(channel)` in cleanup | `realtime-patterns.md` (Connection Lifecycle) |
| **The Replica Identity Surprise** | Subscribing to `postgres_changes` UPDATE/DELETE expecting full row data | Old record only contains primary key; rest is NULL | `ALTER TABLE x REPLICA IDENTITY FULL;` (cost: more WAL bandwidth) | `realtime-patterns.md` (Postgres Changes section) |

---

## Decision Trees

### Which Supabase API key do I use?

```
Is the code running in a BROWSER (visible to users)?
  YES → Use ANON key (or PUBLISHABLE key if available — preferred new format)
        - RLS applies, user gets only what their session allows
  NO  → Is this a backend that needs to BYPASS RLS for admin operations?
        YES → Use SERVICE_ROLE key (NEVER expose to browser, NEVER NEXT_PUBLIC_)
        NO  → Use ANON key + forward user JWT (RLS-respecting privileged operations)
```

### Where do I store authorization data (role, tenant_id)?

```
Does the user need to read it for UI hints?
  YES → app_metadata (writable only via service_role; readable in JWT)
  NO  → Custom JWT claim via Auth Hook (cleanest; doesn't touch metadata at all)

NEVER use user_metadata — user can edit their own role.
```

### How should I do schema changes?

```
Are you ITERATING on the design (will change SQL multiple times)?
  YES → execute_sql / supabase db query
        - When done, generate migration: supabase db pull --local --yes
  NO  → (Final, ready-to-commit SQL)
        → supabase migration new <name> (creates file)
        → Edit file, run supabase db reset to verify
        → supabase migration up to apply locally
        → supabase db push to deploy

NEVER use apply_migration during iteration — it writes history on every call.
```

### Which Realtime channel type?

```
Does the UI need to react to a DATABASE row change?
  YES → postgres_changes
        - ALTER TABLE x REPLICA IDENTITY FULL (if you need old values)
        - ALTER PUBLICATION supabase_realtime ADD TABLE x
        - RLS on the source table is the authorization layer
  NO  → Is the data ephemeral (cursor positions, typing indicators)?
        YES → "Who is here right now?" specifically?
              YES → Presence
              NO  → Broadcast (with channel-level RLS via realtime.messages)
        NO  → Write to DB + use postgres_changes (or skip realtime)
```

### Which vector index?

```
How many rows in the table?
  < 10K  → No index — sequential scan is fast enough
  10K-1M → HNSW (default ops + parameters)
  > 1M   → HNSW with tuned m=16-32, ef_construction=64-128
            OR IVFFlat with lists=sqrt(N) IF you have specific reasons (faster build, more updates)

Distance metric?
  OpenAI embeddings → cosine (<=>) with vector_cosine_ops
  Pre-normalized embeddings → inner product (<#>) with vector_ip_ops (faster)
  Other / unknown → cosine (<=>) — most forgiving
```

---

## Security Checklist (run for any Auth, RLS, View, Storage, or user-data task)

These are Supabase-specific traps that silently create vulnerabilities. Apply EVERY time you touch this surface.

### Auth & Sessions
- [ ] Authorization data in `app_metadata`, not `user_metadata`
- [ ] Middleware/server-side auth uses `getUser()` or `getClaims()`, NOT `getSession()`
- [ ] Server client created per-request, not module-level singleton
- [ ] Cookies adapter `setAll` forwards every cookie to the response
- [ ] User deletion path calls `auth.admin.signOut(userId, 'global')` BEFORE delete
- [ ] JWT-based authorization aware that claims are stale until token refresh

### Keys & Exposure
- [ ] No `service_role` in any `NEXT_PUBLIC_*` env var
- [ ] No `service_role` in client-side code, browser bundles, or git history
- [ ] Any direct postgres connection uses transaction pooler (port 6543) with `prepare: false`

### RLS, Views, Privileged DB Code
- [ ] RLS enabled on every table in `public` (and other exposed schemas)
- [ ] At least one policy per allowed operation (enabled RLS without policies = locked table)
- [ ] Views in Postgres 15+ use `WITH (security_invoker = true)`
- [ ] UPDATE policies have matching SELECT policies on same table
- [ ] `SECURITY DEFINER` functions live in unexposed schema

### Storage
- [ ] Upsert paths have SELECT + INSERT + UPDATE policies
- [ ] Path convention puts `auth.uid()::text` as first segment for ownership-based RLS
- [ ] Bucket `allowed_mime_types` set if uploads should be type-restricted (knowing this is spoofable; magic-byte validation needed for true safety)
- [ ] CORS `allowedHeaders` includes `x-upsert` if browser uploads use upsert

### Realtime
- [ ] Tables added to `supabase_realtime` publication
- [ ] `REPLICA IDENTITY FULL` on tables where old-row data is needed in subscriptions
- [ ] Channel cleanup (`removeChannel`) in every component effect
- [ ] Private channels use `realtime.setAuth(token)` and `{ private: true }` config

For any security concern not covered above, fetch the Supabase product security index: `https://supabase.com/docs/guides/security/product-security.md`

---

## Supabase CLI

Always discover commands via `--help` — never guess. The CLI structure changes between versions.

```bash
supabase --help                    # All top-level commands
supabase <group> --help            # Subcommands
supabase <group> <command> --help  # Flags for a command
```

### Version-Specific Gotchas

| Command | Minimum CLI version | Fallback if older |
|---------|---------------------|-------------------|
| `supabase db query` | v2.79.0 | MCP `execute_sql` or `psql` |
| `supabase db advisors` | v2.81.3 | MCP `get_advisors` |
| `supabase migration new <name>` | All versions | Always use this — never invent migration filenames manually |

Check version: `supabase --version`. Changelog: [supabase/cli releases](https://github.com/supabase/cli/releases).

---

## Supabase MCP Server

For setup, server URL, and configuration, see the [MCP setup guide](https://supabase.com/docs/guides/getting-started/mcp).

### Connection Troubleshooting (in order)

1. **Server reachable?**
   `curl -so /dev/null -w "%{http_code}" https://mcp.supabase.com/mcp`
   `401` = up (no token expected). Timeout / "connection refused" = server may be down.

2. **`.mcp.json` configured?**
   Project root needs valid `.mcp.json` pointing to `https://mcp.supabase.com/mcp`. If missing, create it.

3. **Authenticated?**
   Server reachable + `.mcp.json` correct but tools invisible → user needs OAuth 2.1 auth. Trigger flow in agent, complete in browser, reload session.

---

## Documentation Access (priority order)

1. **MCP `search_docs` tool** (preferred — relevant snippets directly)
2. **Fetch docs as markdown** — append `.md` to any docs URL path
3. **Web search** for topics where you don't know the right page

---

## Schema Change Workflow (committed)

When ready to commit schema changes you iterated on with `execute_sql` / `db query`:

1. **Run advisors** → `supabase db advisors` (v2.81.3+) or MCP `get_advisors`. Fix all issues.
2. **Review the Security Checklist above** if changes touch views, functions, triggers, RLS, or storage.
3. **Generate migration** → `supabase db pull <descriptive-name> --local --yes`
4. **Verify** → `supabase migration list --local`
5. **Regenerate types** → `supabase gen types typescript --linked > types/database.ts`
6. **Commit BOTH** the migration file AND the regenerated types

---

## When This Skill Gives Bad Guidance

If guidance from this skill turns out to be incorrect or missing:
- For Supabase product behavior issues (the underlying API/CLI changed) → follow `references/skill-feedback.md` to file feedback to maintainers
- For our optimization or local additions → file a work request to Skill Hub via `python ~/.claude/scripts/work-request.py`

---

## Reference Companion Files

- [auth-patterns.md](references/auth-patterns.md) — getUser vs getSession, cookie handling, MFA, OAuth, anonymous users
- [realtime-patterns.md](references/realtime-patterns.md) — channel types, REPLICA IDENTITY, RLS, scaling
- [edge-functions-patterns.md](references/edge-functions-patterns.md) — Deno runtime, secrets, webhooks, cron, postgres from functions
- [storage-patterns.md](references/storage-patterns.md) — bucket RLS, upsert trap, signed URLs, transformations
- [client-library-ssr.md](references/client-library-ssr.md) — @supabase/ssr per framework, generated types, query patterns
- [vectors-cron-queues.md](references/vectors-cron-queues.md) — pgvector indexes, pg_cron, pgmq, extensions
- [skill-feedback.md](references/skill-feedback.md) — feedback workflow when guidance is incorrect
