---
name: shopify-development
description: |
  Build Shopify apps, extensions, themes using GraphQL Admin API, Shopify CLI, and Liquid.
  TRIGGER: "shopify", "shopify app", "checkout extension", "admin extension", "POS extension",
  "shopify theme", "liquid template", "polaris", "shopify graphql", "shopify webhook",
  "shopify billing", "app subscription", "metafields", "shopify functions"
  EXCLUDE: General e-commerce advice without Shopify context, payment processing (use stripe-best-practices), generic React/Node.js questions
---

# Shopify Development

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/app-development.md` | Building apps: OAuth, GraphQL API, webhooks, billing | Theme-only or extension-only work |
| `references/extensions.md` | Checkout/admin/POS UI extensions, Shopify Functions | Theme development, app backend |
| `references/themes.md` | Theme development: Liquid, sections, snippets, layout | App development, extensions |
| `evals.json` | Evaluating skill output quality | Normal usage |

---

## Routing: What Are You Building?

**IF integrating external services OR building merchant tools OR charging for features:**
- Build an **App** -- load `references/app-development.md`
- Apps live on your server, connect via OAuth, use GraphQL Admin API

**IF customizing checkout UI OR adding admin dashboard widgets OR creating POS actions OR implementing discount/validation rules:**
- Build an **Extension** -- load `references/extensions.md`
- Extensions run inside Shopify's sandboxed environment using React components

**IF customizing storefront design OR modifying product/collection pages OR editing the online store look:**
- Build a **Theme** -- load `references/themes.md`
- Themes use Liquid templating with JSON templates and section architecture

**IF you need backend logic AND storefront UI together:**
- Build **App + Theme App Extension** combo
- App handles API logic; theme extension renders storefront blocks

---

## Shopify CLI Quick Reference

```bash
# App development
shopify app init                                    # Scaffold new app
shopify app dev                                     # Dev server with ngrok tunnel
shopify app deploy                                  # Build + upload to Shopify
shopify app generate extension --type <TYPE>         # Add extension to app

# Extension types: checkout_ui_extension, admin_action,
#   admin_block, pos_ui_extension, function

# Theme development
shopify theme init                                  # Scaffold new theme
shopify theme dev                                   # Local preview at localhost:9292
shopify theme pull --live                           # Download live theme
shopify theme push --development                    # Upload to dev theme
shopify theme check                                 # Lint theme code
```

---

## GraphQL Admin API (2026-01)

API endpoint: `https://{shop}/admin/api/2026-01/graphql.json`
Auth header: `X-Shopify-Access-Token: {token}`

### Query Products (with pagination)

```graphql
query GetProducts($first: Int!, $after: String, $query: String) {
  products(first: $first, after: $after, query: $query) {
    edges {
      node {
        id
        title
        handle
        status
        variants(first: 10) {
          edges {
            node { id price sku inventoryQuantity }
          }
        }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
```

### Create Product

```graphql
mutation CreateProduct($input: ProductInput!) {
  productCreate(input: $input) {
    product { id title handle }
    userErrors { field message }
  }
}
```

### Set Metafields

```graphql
mutation SetMetafields($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { id namespace key value }
    userErrors { field message }
  }
}
```

Variables: `{ "metafields": [{ "ownerId": "gid://shopify/Product/123", "namespace": "custom", "key": "care_instructions", "value": "Hand wash only", "type": "single_line_text_field" }] }`

### Bulk Operations (for 250+ items)

```graphql
mutation BulkExportProducts {
  bulkOperationRunQuery(
    query: """
    { products { edges { node { id title variants { edges { node { id price } } } } } } }
    """
  ) {
    bulkOperation { id status }
    userErrors { field message }
  }
}
```

Poll status via `currentBulkOperation { status url }`, download JSONL from the URL.

---

## Webhook Configuration

In `shopify.app.toml`:

```toml
[webhooks]
api_version = "2026-01"

[[webhooks.subscriptions]]
topics = ["orders/create", "orders/updated"]
uri = "/webhooks/orders"

[[webhooks.subscriptions]]
topics = ["products/update"]
uri = "/webhooks/products"

# MANDATORY for app store approval
[webhooks.privacy_compliance]
customer_data_request_url = "/webhooks/gdpr/data-request"
customer_deletion_url = "/webhooks/gdpr/customer-deletion"
shop_deletion_url = "/webhooks/gdpr/shop-deletion"
```

### HMAC Verification (Non-Negotiable)

```javascript
import crypto from 'crypto';

function verifyWebhook(req) {
  const hmac = req.headers['x-shopify-hmac-sha256'];
  const hash = crypto
    .createHmac('sha256', process.env.SHOPIFY_API_SECRET)
    .update(req.rawBody, 'utf8')
    .digest('base64');
  return crypto.timingSafeEqual(Buffer.from(hmac), Buffer.from(hash));
}
```

Use `crypto.timingSafeEqual` -- string comparison (`===`) is vulnerable to timing attacks.

---

## Access Scopes

Configure in `shopify.app.toml`:

```toml
[access_scopes]
scopes = "read_products,write_products,read_orders"
```

| Scope | Access |
|-------|--------|
| `read_products` / `write_products` | Product catalog |
| `read_orders` / `write_orders` | Order management |
| `read_customers` / `write_customers` | Customer data (GDPR implications) |
| `read_inventory` / `write_inventory` | Stock levels |
| `read_fulfillments` / `write_fulfillments` | Fulfillment tracking |
| `read_checkouts` / `write_checkouts` | Checkout data |

**Principle of least privilege:** Request only scopes you actively use. Excessive scopes slow app review and reduce merchant trust.

---

## Anti-Patterns (Named)

### The REST Holdout
Using REST API for new development when GraphQL is available. REST is maintenance-mode; GraphQL gets new features first, supports field selection (lower bandwidth), and has cost-based rate limiting instead of call-count limits. **Always use GraphQL for new work.**

### The Scope Hoarder
Requesting every access scope "just in case." Merchants see your scope list during install. Requesting `write_customers` + `write_orders` when you only read products kills install conversion. **Request minimum scopes; add more via OAuth re-authorization when needed.**

### The Webhook Truther
Processing webhooks without verifying the HMAC signature. Any HTTP client can POST fake webhook payloads to your endpoint. **Always verify before processing.** Use `crypto.timingSafeEqual`, not `===`.

### The Pagination Skipper
Fetching products with `first: 250` and assuming that's all of them. Stores can have 100,000+ products. **Always check `pageInfo.hasNextPage` and paginate with `after: endCursor`.** For 250+ items, use bulk operations.

### The Sync Looper
Polling the API every 30 seconds for changes instead of using webhooks. Burns rate limit budget, adds latency, and misses events during downtime. **Use webhooks for real-time events; poll only as a reconciliation fallback.**

### The Version Pinner
Hardcoding API version and never updating. Shopify versions have 12-month deprecation windows. After deprecation, your app breaks. **Track quarterly releases, test against new versions, update within 6 months.**

### The Monolith Extension
Putting all checkout customization into a single extension with every hook and feature. Extensions have performance budgets -- a bloated single extension loads slowly and degrades checkout conversion. **One extension per concern.**

---

## Rate Limiting

GraphQL uses cost-based throttling:
- **Bucket:** 2000 points
- **Restore rate:** 100 points/second (full bucket in 20s)
- **Max single query cost:** 2000 points

Check cost in response:
```javascript
const cost = response.extensions?.cost;
console.log(`Used ${cost.actualQueryCost} of ${cost.throttleStatus.maximumAvailable}`);
```

**When throttled:** Implement exponential backoff starting at 1 second. Read `Retry-After` header when present.

---

## Checkout Extension Quick Example

```tsx
import {
  reactExtension, BlockStack, TextField, Checkbox,
  useApplyAttributeChange
} from '@shopify/ui-extensions-react/checkout';

export default reactExtension('purchase.checkout.block.render', () => <GiftMessage />);

function GiftMessage() {
  const [isGift, setIsGift] = useState(false);
  const [message, setMessage] = useState('');
  const applyChange = useApplyAttributeChange();

  useEffect(() => {
    if (isGift && message) {
      applyChange({ type: 'updateAttribute', key: 'gift_message', value: message });
    }
  }, [isGift, message]);

  return (
    <BlockStack spacing="loose">
      <Checkbox checked={isGift} onChange={setIsGift}>This is a gift</Checkbox>
      {isGift && <TextField label="Gift Message" value={message} onChange={setMessage} multiline={3} />}
    </BlockStack>
  );
}
```

---

## Troubleshooting

**IF rate limit errors (`429` or `THROTTLED`):**
- Switch to bulk operations for large datasets
- Implement exponential backoff with jitter
- Monitor `X-Shopify-Shop-Api-Call-Limit` header
- Reduce query complexity (fewer nested connections)

**IF authentication fails (`401` or `UNAUTHORIZED`):**
- Verify access token is not expired (offline tokens don't expire, online tokens do)
- Confirm required scopes were granted during OAuth
- Check that shop domain matches the token's shop

**IF extension not appearing in checkout:**
- Verify `shopify.extension.toml` target is correct
- Run `shopify app deploy` (not just `dev`)
- Confirm app is installed on the development store
- Check browser console for JavaScript errors

**IF webhook events not arriving:**
- Verify endpoint is publicly accessible (not localhost)
- Check HMAC verification isn't rejecting valid payloads
- Review webhook delivery logs in Partner Dashboard > Webhooks
- Webhooks retry 19 times over 48 hours on failure

**IF GraphQL query returns errors:**
- Validate query in GraphiQL explorer (Partners Dashboard)
- Check for deprecated fields (error message includes alternatives)
- Verify access scopes cover the requested resource
- Watch for `userErrors` array (mutations succeed at HTTP level but fail logically)

---

## Key Links

- API Reference: https://shopify.dev/docs/api/admin-graphql
- CLI Reference: https://shopify.dev/docs/api/shopify-cli
- Extensions Components: https://shopify.dev/docs/api/checkout-ui-extensions/components
- Polaris Design System: https://polaris.shopify.com
- API Version: **2026-01** (quarterly releases, 12-month deprecation)
