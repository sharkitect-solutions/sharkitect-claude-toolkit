---
name: stripe-best-practices
description: Guides Stripe integration decisions — API selection (Checkout Sessions vs PaymentIntents), Connect platform setup (Accounts v2, controller properties), billing/subscriptions, Treasury financial accounts, integration surfaces (Checkout, Payment Element), webhook handling, and migrating from deprecated Stripe APIs. Use when building, modifying, or reviewing any Stripe integration — including accepting payments, building marketplaces, integrating Stripe, processing payments, setting up subscriptions, handling webhooks, or creating connected accounts. Do NOT use for general payment processing concepts unrelated to Stripe, non-Stripe payment providers (PayPal, Square, Braintree), Stripe CLI setup and configuration, or Stripe Dashboard navigation.
---

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| SKILL.md | Always (routing hub) | -- |
| references/payments.md | Accepting payments, checkout, payment elements, PCI | Billing subscriptions, Connect marketplaces |
| references/billing.md | Subscriptions, recurring payments, usage billing | One-time payments, Connect |
| references/connect.md | Marketplaces, platforms, multi-party payments, connected accounts | Simple payments, billing |
| references/treasury.md | Banking-as-a-service, financial accounts, money movement | Payments, billing, Connect |
| references/webhooks.md | Event handling, webhook verification, idempotency | Initial integration setup |

## Scope Boundary

| Domain | In/Out | Use Instead |
|--------|--------|-------------|
| Stripe API integration | IN | -- |
| Stripe webhook handling | IN | -- |
| Stripe billing and subscriptions | IN | -- |
| Stripe Connect platforms | IN | -- |
| Stripe Treasury financial accounts | IN | -- |
| General payment concepts | OUT | smb-cfo |
| Non-Stripe providers (PayPal, Square, Braintree) | OUT | -- |
| Frontend UI components | OUT | frontend-design |
| Database schema for payments | OUT | database |
| Stripe CLI setup and configuration | OUT | -- |
| Stripe Dashboard navigation | OUT | -- |

Latest Stripe API version: **2026-02-25.clover**. Always use the latest API version and SDK unless the user specifies otherwise.

## Integration routing

| Building... | Recommended API | Details |
|---|---|---|
| One-time payments | Checkout Sessions | [references/payments.md](references/payments.md) |
| Custom payment form with embedded UI | Checkout Sessions + Payment Element | [references/payments.md](references/payments.md) |
| Saving a payment method for later | Setup Intents | [references/payments.md](references/payments.md) |
| Connect platform or marketplace | Accounts v2 (`/v2/core/accounts`) | [references/connect.md](references/connect.md) |
| Subscriptions or recurring billing | Billing APIs + Checkout Sessions | [references/billing.md](references/billing.md) |
| Embedded financial accounts / banking | v2 Financial Accounts | [references/treasury.md](references/treasury.md) |

Read the relevant reference file before answering any integration question or writing code.

## Key documentation

When the user's request does not clearly fit a single domain above, consult:

- [Integration Options](https://docs.stripe.com/payments/payment-methods/integration-options.md) — Start here when designing any integration.
- [API Tour](https://docs.stripe.com/payments-api/tour.md) — Overview of Stripe's API surface.
- [Go Live Checklist](https://docs.stripe.com/get-started/checklist/go-live.md) — Review before launching.
