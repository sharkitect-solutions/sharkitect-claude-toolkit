# Treasury / Financial Accounts

## Table of contents
- v2 Financial Accounts API
- Financial account features
- Outbound payments and transfers
- Inbound flows
- Transaction handling and reconciliation
- Code example: creating a financial account
- Legacy v1 Treasury

## v2 Financial Accounts API

For embedded financial accounts (bank accounts, account and routing numbers, money movement), use the [v2 Financial Accounts API](https://docs.stripe.com/api/v2/core/vault/financial-accounts.md) (`POST /v2/core/vault/financial_accounts`). This is required for new integrations.

For Treasury concepts and guides, see the [Treasury overview](https://docs.stripe.com/treasury.md).

A Financial Account is a ledger-based account that holds funds on behalf of a connected account. It provides account and routing numbers (ACH/wire) so the connected account can receive and send funds programmatically. Financial accounts are created per connected account -- each connected account can have one or more financial accounts.

## Financial account features

Financial accounts are configured with feature flags that control what operations are available. Request features at creation time or enable them later:

- **financial_addresses.aba**: Assigns ACH routing and account numbers so the financial account can receive external transfers.
- **outbound_payments.ach**: Enables sending funds via ACH to external bank accounts.
- **outbound_payments.us_domestic_wire**: Enables sending funds via US domestic wire transfer.
- **outbound_transfers.ach**: Enables moving funds from the financial account to the connected account's external bank account (payout-like).
- **inbound_transfers.ach**: Enables pulling funds from an external bank account into the financial account.
- **deposit_insurance**: Provides FDIC pass-through insurance on deposited funds (up to $250K per end-customer).

Features may require additional verification or onboarding. Check the `status_details` on each feature after creation to confirm activation.

## Outbound payments and transfers

Stripe distinguishes between two types of outbound money movement:

- **OutboundPayment**: Send funds FROM a financial account TO an external third-party bank account (e.g., paying a vendor, contractor, or customer refund). Requires `outbound_payments.ach` or `outbound_payments.us_domestic_wire` feature. Specify the destination bank account, amount, and currency.
- **OutboundTransfer**: Move funds FROM a financial account TO the connected account's own external bank account. This is analogous to a payout -- moving money from the platform-managed account to the user's personal/business bank. Requires `outbound_transfers.ach` feature.

**Anti-pattern -- Confusing Payments and Transfers**: OutboundPayment is for paying third parties. OutboundTransfer is for moving money to the account holder's own bank. Using the wrong one causes compliance and reconciliation issues.

## Inbound flows

Money enters a financial account through two event types:

- **ReceivedCredit**: Funds received into the financial account from an external source (ACH credit, wire, or internal Stripe transfer). Listen to `treasury.received_credit` webhooks to reconcile incoming funds.
- **ReceivedDebit**: An authorized debit against the financial account (e.g., ACH debit initiated by a third party). Listen to `treasury.received_debit` webhooks. These can represent returns, chargebacks, or authorized pulls.

For inbound transfers initiated by your platform, use **InboundTransfer** to pull funds from the connected account's external bank into their financial account. This requires the `inbound_transfers.ach` feature.

## Transaction handling and reconciliation

Every money movement on a financial account creates a **Transaction** with associated **TransactionEntry** records:

- Transactions represent the net effect of a financial event (credit or debit).
- TransactionEntries are the double-entry line items within a transaction.
- Use `stripe.treasury.transactions.list({ financial_account: 'fa_xxx' })` to fetch the ledger.
- Filter by `status` (open, posted, void) and `created` date range for reconciliation.
- Match transactions to your internal records using the `description` and `flow` fields. The `flow` field links back to the originating object (OutboundPayment, ReceivedCredit, etc.).

**Anti-pattern -- Ignoring Pending Transactions**: Transactions start in `open` status before settling to `posted`. Do not treat `open` transactions as finalized. Wait for `posted` status or listen to `treasury.transaction.posted` webhooks before updating balances in your system.

## Code example: creating a financial account

```js
// Create a financial account with ACH features for a connected account
const financialAccount = await stripe.treasury.financialAccounts.create(
  {
    supported_currencies: ['usd'],
    features: {
      financial_addresses: { aba: { requested: true } },
      outbound_payments: { ach: { requested: true } },
      outbound_transfers: { ach: { requested: true } },
      inbound_transfers: { ach: { requested: true } },
      deposit_insurance: { requested: true },
    },
  },
  { stripeAccount: 'acct_connected_xxx' }
);

// Send funds to an external bank account
const payment = await stripe.treasury.outboundPayments.create(
  {
    financial_account: financialAccount.id,
    amount: 50000, // $500.00
    currency: 'usd',
    destination_payment_method: 'pm_bank_xxx',
    description: 'Vendor payment - Invoice #1234',
  },
  { stripeAccount: 'acct_connected_xxx' }
);
```

## Legacy v1 Treasury

Do not use the [v1 Treasury Financial Accounts API](https://docs.stripe.com/api/treasury/financial_accounts.md) (`POST /v1/treasury/financial_accounts`) for new integrations. Existing v1 integrations continue to work but should plan migration to v2. The v2 API provides improved feature management, better webhook coverage, and alignment with Stripe's evolving platform architecture.
