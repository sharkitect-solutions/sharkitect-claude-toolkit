# Webhooks

## Table of contents
- Webhook verification
- Event types by integration
- Idempotency and duplicate handling
- Retry behavior and event ordering
- Local testing
- Production best practices

## Webhook verification

Always verify webhook signatures using `stripe.webhooks.constructEvent`. Never trust raw payloads without verification.

```javascript
const event = stripe.webhooks.constructEvent(
  request.body,        // raw body (Buffer or string, NOT parsed JSON)
  request.headers['stripe-signature'],
  process.env.STRIPE_WEBHOOK_SECRET  // whsec_... from Dashboard
);
```

**Traps to avoid:**
- Do not parse the body as JSON before passing it to `constructEvent` -- it needs the raw body to verify the signature.
- Do not hardcode signing secrets -- use environment variables.
- Use separate webhook signing secrets per endpoint. Each endpoint in the Dashboard gets its own `whsec_` secret.

## Event types by integration

Subscribe only to the events your integration needs. Common mappings:

| Integration | Subscribe to | Why |
|---|---|---|
| One-time payments | `checkout.session.completed`, `payment_intent.succeeded`, `payment_intent.payment_failed` | Confirm fulfillment, handle failures |
| Subscriptions | `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted` | Track billing lifecycle, handle dunning |
| Connect platforms | `account.updated`, `payment_intent.succeeded` (on connected account), `payout.failed` | Monitor onboarding status, track connected payments |
| Setup Intents | `setup_intent.succeeded`, `setup_intent.setup_failed` | Confirm saved payment methods |
| Disputes | `charge.dispute.created`, `charge.dispute.closed` | Respond to chargebacks within deadline |

**Traps to avoid:** Do not subscribe to `*` (all events) in production. It creates unnecessary load and complicates event routing.

## Idempotency and duplicate handling

Stripe may deliver the same event more than once. Your webhook handler MUST be idempotent.

**Pattern: Event deduplication table**
1. Store processed `event.id` values in a database table with a unique constraint.
2. Before processing, check if `event.id` already exists.
3. If it exists, return 200 immediately without reprocessing.
4. If it does not exist, insert the ID and process the event.

```sql
CREATE TABLE stripe_processed_events (
  event_id VARCHAR(255) PRIMARY KEY,
  event_type VARCHAR(255) NOT NULL,
  processed_at TIMESTAMP DEFAULT NOW()
);
```

**Traps to avoid:**
- Do not rely on in-memory caches for deduplication -- they reset on deploy.
- Do not assume events arrive exactly once. Design every handler to be safe on replay.

## Retry behavior and event ordering

Stripe retries failed webhook deliveries (non-2xx responses) for up to 3 days using exponential backoff. Retry intervals increase from minutes to hours.

**Event ordering is NOT guaranteed.** Events may arrive out of chronological order. Design handlers to be order-independent:
- Fetch the current state from the Stripe API (`stripe.paymentIntents.retrieve(event.data.object.id)`) rather than trusting the event payload alone for critical state transitions.
- Use `event.data.object` for read-only notifications (logging, analytics).
- Use API fetches for state-changing operations (fulfillment, access grants).

**Traps to avoid:**
- Do not build state machines that depend on receiving events in order (e.g., `payment_intent.created` before `payment_intent.succeeded`).
- Do not ignore failed webhooks -- monitor your endpoint's success rate in the Dashboard under Developers > Webhooks.

## Local testing

Use the Stripe CLI to forward events to your local development server:

```bash
stripe listen --forward-to localhost:3000/api/webhooks
```

The CLI outputs a temporary signing secret (`whsec_...`) for local verification. Use it in your `.env` for development only.

For testing specific events:
```bash
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created
```

**Traps to avoid:** Do not use your production signing secret for local development. The CLI provides a separate secret.

## Production best practices

1. **Respond 200 immediately.** Acknowledge receipt before doing any processing. Queue the event for async handling.
2. **Process asynchronously.** Use a job queue (Bull, Celery, SQS) to handle event processing outside the request lifecycle. This prevents timeouts.
3. **Dead letter queue.** Route events that fail processing after N retries to a dead letter queue for manual inspection.
4. **Monitor endpoint health.** Stripe disables endpoints that consistently fail. Set up alerts on webhook failure rates.
5. **Use thin handlers.** The webhook endpoint should validate, deduplicate, enqueue, and return 200. Business logic belongs in the async worker.

| Anti-pattern | Why it fails | Do instead |
|---|---|---|
| Synchronous fulfillment in webhook handler | Timeouts on slow operations (email, DB writes) | Enqueue and process async |
| No deduplication | Double-charges, duplicate emails on retry | Event ID table with unique constraint |
| Trusting event payload for state changes | Stale data from out-of-order delivery | Fetch current state from Stripe API |
| Single webhook endpoint for all event types | Hard to maintain, debug, and scale | Route events to dedicated handlers by type |
