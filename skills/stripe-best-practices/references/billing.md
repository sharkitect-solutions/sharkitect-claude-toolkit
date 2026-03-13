# Billing / Subscriptions

## Table of contents
- When to use Billing APIs
- Recommended frontend pairing
- Subscription lifecycle management
- Usage-based and metered billing
- Proration strategies
- Trial management
- Dunning and failed payment handling
- Customer portal setup
- Code example: subscription with trial and proration
- Traps to avoid

## When to use Billing APIs

If the user has a recurring revenue model (subscriptions, usage-based billing, seat-based pricing), use the Billing APIs to [plan their integration](https://docs.stripe.com/billing/subscriptions/designing-integration.md) instead of a direct PaymentIntent integration.

Review the [Subscription Use Cases](https://docs.stripe.com/billing/subscriptions/use-cases.md) and [SaaS guide](https://docs.stripe.com/saas.md) to find the right pattern for the user's pricing model.

## Recommended frontend pairing

Combine Billing APIs with Stripe Checkout for the payment frontend. Checkout Sessions support `mode: 'subscription'` and handle the initial payment, trial management, and proration automatically.

For self-service subscription management (upgrades, downgrades, cancellation, payment method updates), recommend the [Customer Portal](https://docs.stripe.com/customer-management/integrate-customer-portal.md).

## Subscription lifecycle management

Subscriptions move through a predictable lifecycle. Guide users through each transition:

- **Create**: Use `stripe.subscriptions.create()` with a customer, price, and optional trial. Always attach a default payment method to the customer first via SetupIntent.
- **Upgrade / Downgrade**: Update the subscription's `items` array with the new price ID. Stripe calculates proration automatically unless overridden. Use `subscription_update` in the Customer Portal for self-service plan changes.
- **Pause**: Set `pause_collection` with `behavior: 'mark_uncollectible'` or `'void'`. Paused subscriptions retain their billing anchor but skip invoice generation. Resume by setting `pause_collection` to empty.
- **Cancel**: Use `cancel_at_period_end: true` for end-of-period cancellation (preferred -- customer keeps access until period ends). Use `stripe.subscriptions.cancel()` for immediate cancellation. Immediate cancellation can optionally issue a prorated credit via `prorate: true`.
- **Resume**: Reactivate a subscription set to cancel at period end by updating `cancel_at_period_end: false` before the period ends. For already-canceled subscriptions, create a new subscription.

**Anti-pattern -- The Frankenstein Lifecycle**: Building custom cron jobs to check subscription states and manually transition them. Stripe handles lifecycle transitions automatically via webhooks. Listen to events, do not poll.

## Usage-based and metered billing

For consumption-based pricing (API calls, storage, compute minutes):

- **Create a metered price**: Set `recurring.usage_type: 'metered'` on the Price object. Do not set a fixed `unit_amount` unless combining with a base fee.
- **Report usage**: Call `stripe.subscriptionItems.createUsageRecord()` with `quantity` and `timestamp`. Use `action: 'increment'` (default) to add to existing usage or `action: 'set'` to replace the running total.
- **Invoice timing**: Metered usage is tallied at the end of each billing period. The invoice is finalized ~1 hour after period end. Report all usage before the period closes.
- **Threshold billing**: For high-usage customers, set `billing_thresholds.amount_gte` on the subscription to trigger mid-cycle invoices when accumulated charges exceed a dollar threshold. This prevents surprise large invoices.
- **Combining models**: A subscription can mix metered prices (usage-based) and licensed prices (flat or per-seat) in the same `items` array. Each item is billed according to its own pricing model.

## Proration strategies

When a subscription changes mid-cycle (plan upgrade, quantity change), Stripe calculates proration by default. Control this with the `proration_behavior` parameter:

- `create_prorations` (default): Generate prorated line items on the next invoice. Customer pays the difference for upgrades, receives credit for downgrades.
- `always_invoice`: Create prorations AND immediately generate and pay a new invoice for the prorated amount. Best for upgrades where you want immediate charge.
- `none`: No proration. The new price takes effect at the next billing cycle. Use for downgrades where you want the customer to keep the current plan until renewal.

**Anti-pattern -- Manual Proration Math**: Never calculate proration amounts manually. Stripe's proration engine accounts for billing anchors, tax, discounts, and partial periods automatically. Manual math will drift.

## Trial management

- **trial_end**: Set an absolute Unix timestamp for when the trial expires. The first invoice is generated at trial end.
- **trial_period_days**: Simpler alternative -- set the number of trial days relative to subscription creation.
- **trial_settings.end_behavior**: Controls what happens when a trial ends without a payment method. Set to `cancel` to auto-cancel, or `pause` to pause collection. Default creates a past-due invoice.
- **Converting trials**: Listen to `customer.subscription.trial_will_end` (fires 3 days before trial end) to prompt the customer to add a payment method. If no method is attached, the first invoice will fail.

**Anti-pattern -- The Eternal Trial**: Not handling `trial_will_end` and letting trials convert to past-due subscriptions silently. Always wire up this webhook to trigger a payment method collection flow.

## Dunning and failed payment handling

When a subscription invoice payment fails, Stripe's dunning system manages retries:

- **Smart Retries**: Enable in Dashboard > Settings > Billing > Subscriptions. Stripe uses ML to pick optimal retry timing based on card type, issuer, and historical success patterns. This is the recommended default.
- **Custom retry schedule**: Configure up to 4 retry attempts with specific intervals (e.g., 3 days, 5 days, 7 days) in Dashboard > Billing > Subscriptions > Manage failed payments.
- **Webhook handling**: Listen to `invoice.payment_failed` to trigger customer notifications (email, in-app banner). Check `event.data.object.attempt_count` to escalate messaging on repeated failures.
- **Final action**: After all retries exhaust, configure the subscription to cancel, mark as unpaid, or pause. Set this in Dashboard or via `subscription_settings.default_payment_method` on the subscription schedule.
- **Revenue recovery emails**: Enable Stripe's built-in failed payment emails in Dashboard > Billing > Subscriptions > Manage failed payments > Email customers. These are optimized and outperform most custom implementations.

## Customer portal setup

The [Billing Portal](https://docs.stripe.com/customer-management/integrate-customer-portal.md) provides a Stripe-hosted UI for customers to manage subscriptions without custom code:

- **Create a portal session**: Call `stripe.billingPortal.sessions.create({ customer: 'cus_xxx', return_url: 'https://example.com/account' })`. Redirect the customer to the returned `url`.
- **Configure allowed actions**: In Dashboard > Settings > Billing > Customer portal, control which actions customers can take: update payment method, switch plans, cancel, view invoices, update billing address.
- **Restrict plan changes**: Use `subscription_update.products` to limit which prices/products a customer can switch between. Prevents unintended downgrades to legacy plans.
- **Deep links**: Use `flow_data` parameter to open the portal directly to a specific action (e.g., `flow_data: { type: 'subscription_cancel', subscription_cancel: { subscription: 'sub_xxx' } }`).

## Code example: subscription with trial and proration

```js
// Create a subscription with a 14-day trial and proration on upgrade
const subscription = await stripe.subscriptions.create({
  customer: 'cus_xxx',
  items: [{ price: 'price_standard_monthly' }],
  trial_period_days: 14,
  trial_settings: {
    end_behavior: { missing_payment_method: 'cancel' },
  },
  payment_settings: {
    save_default_payment_method: 'on_subscription',
  },
  proration_behavior: 'create_prorations',
});

// Later: upgrade to a higher plan mid-cycle
await stripe.subscriptions.update(subscription.id, {
  items: [{
    id: subscription.items.data[0].id,
    price: 'price_premium_monthly',
  }],
  proration_behavior: 'always_invoice', // charge difference immediately
});
```

## Traps to avoid

- Do not build manual subscription renewal loops using raw PaymentIntents. Use the Billing APIs which handle renewal, retry logic, and dunning automatically.
- Do not use the deprecated `plan` object. Use [Prices](https://docs.stripe.com/api/prices.md) instead.
- Do not create subscriptions without a payment method attached (unless using trials with `end_behavior: 'cancel'`). The first invoice will immediately fail.
- Do not skip `trial_will_end` webhook handling. Silent trial-to-paid conversions without payment methods cause churn spikes.
