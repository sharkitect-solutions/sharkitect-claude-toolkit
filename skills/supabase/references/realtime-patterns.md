# Supabase Realtime Patterns

Expert-only Realtime knowledge. Generic WebSocket basics are skipped. This file covers the three channel types, RLS interaction, scaling failure modes, and the cleanup patterns that prevent silent memory leaks.

> For deep WebSocket-level scaling and connection-drop debugging, use the **supabase-realtime-optimizer** agent. This file covers application-level patterns and decision-making.

---

## The Three Channel Types: Pick the Right One

Supabase Realtime exposes three orthogonal mechanisms. Choosing wrong = unnecessary cost, missed events, or both.

| Type | Use when | Cost model | Latency | RLS-aware |
|------|----------|-----------|---------|-----------|
| **Postgres Changes** | UI must reflect DB row mutations (collaborative docs, dashboards) | Per-message + DB replication overhead | 50-500ms (DB → WAL → broadcast) | YES (postgres_changes RLS) |
| **Broadcast** | Ephemeral peer-to-peer messages (typing indicators, cursor positions, ephemeral chat) | Per-message, NOT persisted | <50ms | YES (since 2024 — channel-level RLS) |
| **Presence** | Tracking who is online in a "room" (active users, typing, online status) | Heartbeat-based, low | Heartbeat interval | YES (channel-level) |

**Decision tree:**
```
Does the UI need to react to a DATABASE row change?
  YES → Postgres Changes
  NO  → Is the data ephemeral (no persistence needed)?
        YES → Is it about "who is here" specifically?
              YES → Presence
              NO  → Broadcast
        NO  → Write to DB + use Postgres Changes (or skip realtime entirely)
```

**Anti-pattern:** Using Postgres Changes for high-frequency cursor positions or typing indicators. Each message takes a DB round-trip and consumes WAL bandwidth. Cost balloons. Use Broadcast.

**Anti-pattern:** Using Broadcast for state that needs to survive a refresh. Broadcast is fire-and-forget; nothing is stored. Late joiners get nothing. Write to DB + Postgres Changes.

---

## Postgres Changes: The Replication Identity Trap

### REPLICA IDENTITY: The most common silent failure

Postgres Changes uses logical replication. By default, Postgres tables have `REPLICA IDENTITY DEFAULT` which only includes **the primary key** in DELETE and UPDATE event payloads. If you subscribe and expect to see the row's other columns in an UPDATE/DELETE payload, you get NULL or missing fields.

```sql
-- Default behavior: only primary key in old_record on UPDATE/DELETE
ALTER TABLE messages REPLICA IDENTITY DEFAULT;  -- (this is the default)

-- To get ALL columns in old_record:
ALTER TABLE messages REPLICA IDENTITY FULL;
```

**Trade-off:** `REPLICA IDENTITY FULL` adds WAL bandwidth and slows writes. Use only when you genuinely need the old values (audit logs, diff-based UI updates). For most cases, the new record + primary key is sufficient.

### Enabling realtime for a table

You must add the table to the `supabase_realtime` publication. Forgetting this = subscription fires successfully, but no events are ever delivered.

```sql
-- Enable for all events
ALTER PUBLICATION supabase_realtime ADD TABLE messages;

-- Or only specific operations (smaller WAL)
ALTER PUBLICATION supabase_realtime ADD TABLE messages
  WITH (publish = 'insert,update');  -- skip delete events
```

**Verify enabled tables:**
```sql
SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';
```

### Filters are PER-ROW, evaluated server-side

Subscriptions accept SQL-like filter expressions:

```ts
supabase.channel('orders')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'orders',
    filter: `user_id=eq.${userId}`
  }, handler)
```

**The filter runs on Supabase Realtime servers, NOT in the database.** This means:
- Filtered-out events still consume WAL bandwidth (the DB sends everything; Realtime drops what doesn't match).
- The `filter` syntax is a subset of PostgREST filters: `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `in`. **No** `like`, `ilike`, `is.not.null`, complex AND/OR. Complex filtering must happen client-side.
- RLS still applies — even if your filter would let it through, RLS denies it server-side first.

### postgres_changes RLS Authorization

For Postgres Changes, the user's RLS policies on the SOURCE table determine which events they receive. **No additional channel RLS needed.** This means:
- A user subscribed to `orders` only receives events for rows their `SELECT` policy allows.
- If you have an RLS policy `USING (user_id = auth.uid())`, the user gets only their own orders' events automatically.

**Performance note:** RLS policy evaluation runs PER EVENT. A complex policy with subqueries on a high-write table can collapse Realtime throughput. Keep policies simple; for complex authorization, denormalize `user_id` / `org_id` into the table itself.

---

## Broadcast: The 2024 RLS Migration

Pre-2024, Broadcast was unauthenticated by default — anyone with the channel name could send/receive. Since 2024, channel-level RLS via `realtime.messages` controls authorization. Many tutorials online are out of date.

### Enabling channel authorization

```sql
-- Enable RLS on the realtime.messages table
ALTER TABLE realtime.messages ENABLE ROW LEVEL SECURITY;

-- Example: only authenticated users can broadcast in 'room:<id>' channels
CREATE POLICY "auth users broadcast" ON realtime.messages
FOR INSERT TO authenticated
WITH CHECK (
  realtime.topic() LIKE 'room:%'
  AND auth.uid() IS NOT NULL
);

-- Example: only members of an org can subscribe to org channels
CREATE POLICY "org members read" ON realtime.messages
FOR SELECT TO authenticated
USING (
  realtime.topic() LIKE 'org:' || (
    SELECT org_id::text FROM org_members WHERE user_id = auth.uid()
  )
);
```

### Client-side: setAuth is REQUIRED for authorized channels

```ts
// WRONG — uses anon key, RLS denies
const channel = supabase.channel('room:abc')
channel.subscribe()  // silently denied if RLS requires auth

// RIGHT — explicitly set auth before subscribing
const { data: { session } } = await supabase.auth.getSession()
supabase.realtime.setAuth(session.access_token)
const channel = supabase.channel('room:abc', {
  config: { private: true }  // <-- enables RLS check
})
channel.subscribe()
```

**Token refresh on long-lived channels:** the access token in the realtime connection does NOT auto-refresh. After ~1 hour the connection works but new RLS-checked sends fail silently. Listen for `auth.onAuthStateChange` and call `realtime.setAuth(newToken)` on `TOKEN_REFRESHED`.

### Send modes: client-side vs server-side broadcast

```ts
// Client-side: WebSocket → Realtime server → all subscribers
channel.send({ type: 'broadcast', event: 'cursor', payload: {...} })

// Server-side: HTTP POST → Realtime server (faster, no WS overhead, no client lib needed)
fetch(`${SUPABASE_URL}/realtime/v1/api/broadcast`, {
  method: 'POST',
  headers: { 'apikey': SERVICE_ROLE_KEY, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ topic: 'room:abc', event: 'system', payload: {...} }]
  })
})
```

Use server-side broadcast from Edge Functions / cron / webhooks where you don't want to maintain a WebSocket connection.

---

## Presence: Heartbeats, Not Events

Presence tracks "who is in this channel right now" via periodic heartbeats. It is NOT for arbitrary state sync.

```ts
const channel = supabase.channel('room:abc', {
  config: { presence: { key: userId } }  // unique per user
})

channel
  .on('presence', { event: 'sync' }, () => {
    const state = channel.presenceState()
    // state = { userId1: [{ online_at: ..., user_meta: ... }], ... }
  })
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') {
      await channel.track({ online_at: new Date().toISOString() })
    }
  })
```

### Critical: Track AFTER subscribe, not before

`channel.track()` only works after the subscription is confirmed (`status === 'SUBSCRIBED'`). Calling it earlier silently fails — your user appears as not present even though the channel is open.

### Presence key uniqueness

The `presence.key` config defaults to a random UUID. If you want one entry per logged-in user (not per browser tab), set `key: userId`. Multiple tabs from the same user with the same key will appear as ONE presence — last-tab-tracked wins.

### Presence is event-storm prone

Every join/leave triggers a `sync` event broadcast to ALL subscribers. In a 1000-user channel, one user joining = 1000 sync events. Keep presence channels small (per-room, per-document), not global ("all online users").

---

## Connection Lifecycle and Cleanup

### Anti-Pattern: The Channel Leak

```tsx
// WRONG — new channel on every render, never unsubscribed
function ChatRoom({ roomId }) {
  useEffect(() => {
    const channel = supabase.channel(`room:${roomId}`)
    channel.subscribe()
    // <-- no cleanup
  })
}
```

Each render creates a new WebSocket subscription. After 10 renders, you have 10 channels for the same room. Memory leak + duplicate event handlers + Supabase rate limit hit.

```tsx
// RIGHT — subscribe in effect, unsubscribe in cleanup
function ChatRoom({ roomId }) {
  useEffect(() => {
    const channel = supabase.channel(`room:${roomId}`)
      .on('postgres_changes', {...}, handler)
      .subscribe()

    return () => {
      supabase.removeChannel(channel)  // CRITICAL
    }
  }, [roomId])
}
```

### Anti-Pattern: The Reconnection Hammer

By default the JS client reconnects automatically with exponential backoff. If your app has unstable connectivity logic that destroys and recreates the Supabase client on every focus event, you generate thousands of reconnects. Use ONE Supabase client instance per browser tab.

### Reconnection state recovery

When a Realtime connection drops and reconnects, **events that fired during the disconnect are LOST**. There is no "replay missed events" mechanism. For state that must survive reconnects:
1. Source the canonical state from the database
2. Use Realtime as a delta hint, not as the source of truth
3. After reconnect (`SUBSCRIBED` status), re-fetch the current state via REST/RPC, then resume listening

---

## Scaling Failure Modes

### Per-project channel limits

Supabase enforces concurrent channel and message limits per plan tier. For Pro tier (as of 2024): 500 concurrent connections, 2 million messages/month included. Hitting limits = new subscriptions silently fail to join. Monitor in Dashboard → Reports → Realtime.

### The "subscribe to all rows" trap

```ts
// WRONG — every row change broadcast to every subscriber
supabase.channel('all-orders')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'orders' }, handler)
```

For a high-write table, this fans out every change to every connected client. Always filter by user/tenant scope.

### Database load from realtime triggers

Realtime is a CONSUMER of WAL. If your DB write throughput is high (10K+ writes/sec on a small instance), the WAL replication slot used by Realtime can fall behind. Symptoms: lag in event delivery, eventual disconnects. Fix: upsize the DB compute, reduce REPLICA IDENTITY FULL usage, or use partitioned tables and only publish the partitions that need realtime.

### Broadcast/Presence vs Postgres Changes scaling

Broadcast and Presence scale horizontally on Realtime servers (no DB involvement). Postgres Changes scales with WAL throughput (DB-bound). For high-fanout ephemeral workloads (typing indicators in a 10K-user channel), always use Broadcast.

---

## Debugging Checklist

When events aren't arriving:

1. **Is the table in the publication?** `SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';`
2. **Is REPLICA IDENTITY set correctly?** `SELECT relreplident FROM pg_class WHERE relname = '<table>';` (`d`=default, `f`=full, `n`=nothing, `i`=index)
3. **Does RLS allow this user to SELECT the row?** Test the query directly with the user's JWT — if SELECT returns 0 rows, Realtime won't send events for them.
4. **Is the channel actually subscribed?** Check `channel.state` — should be `'joined'`.
5. **Is `setAuth` called for private channels?** Without it, RLS uses the anon role and denies authenticated-only policies.
6. **For Broadcast: is `private: true` set?** Without it, RLS isn't enforced, but also some auth-restricted setups silently deny.
7. **Are you subscribing twice to the same channel name?** Supabase deduplicates by name — second subscribe attaches to the first channel's listeners, can cause confusion.

---

## When This Skill Has Failed in the Past

- Subscribing to Postgres Changes without enabling REPLICA IDENTITY FULL → UPDATE events have NULL old values
- Forgetting `ALTER PUBLICATION supabase_realtime ADD TABLE` → subscription works but no events
- Calling `channel.track()` before SUBSCRIBED → presence silently fails
- Using anon key for private broadcast → silent RLS denial
- Per-render channel creation in React → exponential WebSocket leak
- Long-lived channels stop accepting authorized sends after 1h → missing setAuth on token refresh
