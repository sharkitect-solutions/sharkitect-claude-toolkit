# Supabase-Specific Patterns

Reference for patterns unique to the Supabase platform -- Edge Functions interacting with the database, auth.uid() optimization, Realtime triggers via Postgres, CLI migration workflow, and multi-environment management. Load this file when working with Supabase-specific features rather than generic Postgres.

---

## Edge Functions + Database Patterns

Supabase Edge Functions (Deno-based) connect to Postgres through Supavisor. The connection lifecycle differs from traditional server applications.

**Connection Pattern for Edge Functions:**
```typescript
// CORRECT: Use the built-in Supabase client (handles pooling automatically)
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!  // server-side only
);

// Uses the REST API (PostgREST) -- no direct DB connection needed
const { data, error } = await supabase.from("orders").select("*").eq("status", "pending");
```

```typescript
// CORRECT: Direct Postgres connection when you need raw SQL
import postgres from "https://deno.land/x/postgresjs/mod.js";

// MUST use port 6543 (Supavisor transaction mode)
const sql = postgres(Deno.env.get("SUPABASE_DB_URL")!, {
  max: 1,                    // one connection per function instance
  idle_timeout: 10,          // release after 10 seconds idle
  connect_timeout: 5,
  prepare: false,            // disable named prepared statements in transaction mode
});

const orders = await sql`SELECT * FROM orders WHERE status = 'pending'`;
sql.end();  // always close when done
```

**PostgREST vs Direct SQL Decision:**
| Use PostgREST (supabase.from()) | Use Direct SQL |
|--------------------------------|----------------|
| Standard CRUD operations | Complex joins across 3+ tables |
| Filtering, sorting, pagination | CTEs, window functions, recursive queries |
| RLS-aware queries (uses user JWT) | Batch operations (bulk insert/update) |
| Simple aggregations | Custom functions, stored procedures |
| Real-time subscriptions | Advisory locks, SKIP LOCKED patterns |

---

## auth.uid() Optimization Patterns

`auth.uid()` extracts the user ID from the JWT token in the current request. Its performance in RLS policies depends on how it is called.

**Performance Hierarchy (fastest to slowest):**

1. **Subquery-wrapped with index** -- O(1) function call + O(log n) index lookup:
```sql
CREATE POLICY fast ON orders
  USING ((SELECT auth.uid()) = user_id);
-- Requires: CREATE INDEX orders_user_id_idx ON orders (user_id);
```

2. **Security definer helper** -- O(1) function call + O(log n) lookup + function overhead:
```sql
CREATE OR REPLACE FUNCTION get_my_team_ids()
RETURNS SETOF bigint
LANGUAGE sql SECURITY DEFINER SET search_path = ''
AS $$
  SELECT team_id FROM public.team_members WHERE user_id = (SELECT auth.uid());
$$;

CREATE POLICY team_access ON projects
  USING (team_id IN (SELECT get_my_team_ids()));
```

3. **Bare function call** -- O(n) where n = table rows (evaluated per row):
```sql
-- AVOID: auth.uid() called once per row
CREATE POLICY slow ON orders USING (auth.uid() = user_id);
```

**auth.uid() in Computed Columns and Triggers:**
```sql
-- Auto-populate user_id on insert
CREATE OR REPLACE FUNCTION set_user_id()
RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
  NEW.user_id := (SELECT auth.uid());
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_user_id_trigger
  BEFORE INSERT ON orders
  FOR EACH ROW EXECUTE FUNCTION set_user_id();
```

---

## Realtime Triggers via Postgres

Supabase Realtime listens to Postgres logical replication (WAL). Understanding the trigger chain prevents surprises.

**How Realtime Receives Changes:**
1. Table has `REPLICA IDENTITY` set (default = PRIMARY KEY)
2. Client subscribes to table via Supabase Realtime channel
3. Postgres writes change to WAL
4. Supabase Realtime reads WAL and pushes to subscribed clients
5. RLS policies filter which rows each client sees

**Common Pitfalls:**

```sql
-- PROBLEM: Realtime doesn't see UPDATE old values without REPLICA IDENTITY FULL
ALTER TABLE orders REPLICA IDENTITY FULL;
-- WARNING: increases WAL size significantly. Only use when old values are needed.

-- PROBLEM: RLS prevents Realtime from sending changes
-- Realtime respects RLS. If the subscribing user's JWT doesn't pass the policy,
-- they won't receive the change event even though it happened.
-- TEST: verify RLS policies work for the subscribing user's role.
```

**Database Webhooks (pg_net + Supabase):**
```sql
-- Trigger an external webhook on INSERT
CREATE OR REPLACE FUNCTION notify_webhook()
RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
  PERFORM net.http_post(
    url := 'https://your-api.com/webhook',
    headers := '{"Content-Type": "application/json", "Authorization": "Bearer secret"}'::jsonb,
    body := jsonb_build_object('event', TG_OP, 'record', row_to_json(NEW))
  );
  RETURN NEW;
END;
$$;

CREATE TRIGGER orders_webhook
  AFTER INSERT ON orders
  FOR EACH ROW EXECUTE FUNCTION notify_webhook();
```

---

## Supabase CLI Migration Workflow

**Local Development Cycle:**
```bash
# Start local Supabase (Docker required)
supabase start

# Create a new migration
supabase migration new add_orders_status_index
# -> creates supabase/migrations/<timestamp>_add_orders_status_index.sql

# Edit the migration file with your SQL
# IMPORTANT: use CREATE INDEX CONCURRENTLY for production safety

# Apply to local database
supabase db reset    # drops and recreates from all migrations

# Test locally, then push to remote
supabase db push     # applies pending migrations to remote project

# Pull remote schema changes (made via Dashboard SQL editor)
supabase db pull     # generates migration files for remote-only changes
```

**Migration File Best Practices:**
```sql
-- supabase/migrations/20240315120000_add_orders_index.sql

-- Always wrap in a transaction (Supabase does this automatically)
-- Exception: CREATE INDEX CONCURRENTLY cannot run inside a transaction

-- Safe: add column with default (Postgres 11+ metadata-only)
ALTER TABLE orders ADD COLUMN priority smallint DEFAULT 0;

-- Safe: create index concurrently (does not lock table)
-- NOTE: must be the ONLY statement in migration when using CONCURRENTLY
CREATE INDEX CONCURRENTLY IF NOT EXISTS orders_priority_idx ON orders (priority);
```

**Seeding Data:**
```bash
# supabase/seed.sql runs after migrations on `supabase db reset`
# Use for development/test data only -- never for production data
```

---

## Multi-Environment Management

Three environments: Local (`supabase start`, seed data, feature branches), Staging (linked project, anonymized data, staging branch), Production (linked project, real data, main branch).

**Key Commands:**
```bash
supabase link --project-ref <ref>    # switch target environment
supabase db push                      # apply pending migrations to linked project
supabase db diff --linked             # detect schema drift from Dashboard edits
supabase db pull                      # capture remote-only changes as migrations
supabase gen types typescript --linked > src/types/database.types.ts  # keep types in sync
```

Each environment needs its own `.env` file with `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `DATABASE_URL` (always port 6543 for remote). Git-ignore `.env.local`. Add type generation to CI pipeline to fail builds on stale types.
