# ESP Provider Selection & Gotchas Guide

Load when choosing an ESP, migrating between providers, or debugging provider-specific issues.

## Provider Selection Decision Matrix

Evaluate in order. First match wins.

| Signal | Provider | Why |
|---|---|---|
| Need transactional email only, developer-first, simple API | Postmark or Resend | Purpose-built for transactional. Postmark refuses marketing email entirely. Resend is newer, React-email native. |
| Need transactional + marketing with one platform | SendGrid or Mailgun | Both handle transactional and marketing. SendGrid has better marketing UI. Mailgun has better API/logs. |
| Volume > 100k/day and cost is primary concern | Amazon SES | $0.10/1000 emails. Lowest cost at scale. No UI -- you build everything. |
| Enterprise compliance (HIPAA, SOC 2, dedicated infra) | SparkPost (now MessageBird) or Postmark | Both offer HIPAA-compliant configurations with BAA. |
| Need email as part of a broader messaging platform (SMS, push, in-app) | Customer.io or Braze | Multi-channel platforms. Email is one channel among many. Higher cost but unified analytics. |
| Startup, <10k emails/mo, need free tier | Resend (3k/mo free) or SendGrid (100/day free) | Start free, upgrade when volume grows. |

## Provider-Specific Gotchas

### SendGrid

| Gotcha | Impact | Fix |
|---|---|---|
| Free tier limits to 100 emails/day, not /month | Developers assume 100/day x 30 = 3000/month budget. It's per calendar day. | Plan for strict daily limit or upgrade to Essentials ($19.95/mo for 50k/mo) |
| Sender authentication requires CNAME, not TXT for DKIM | Unlike most providers that use TXT records for DKIM, SendGrid requires CNAME records pointing to their DNS | Follow SendGrid's specific DNS setup, don't copy generic DKIM instructions |
| Event webhook drops events silently if endpoint returns non-2xx 3 times | After 3 failures, SendGrid stops sending events for that URL. No notification. | Monitor webhook health independently. Set up a health check that alerts if no events received in N minutes. |
| Suppression list is global across all subusers | If an address bounces on one subuser, it's suppressed for ALL subusers on the account | Check global suppressions before blaming deliverability. Use API to manage suppressions per subuser manually. |
| IP warm-up feature warms automatically but too aggressively for some ISPs | Auto warm-up can trigger Gmail throttling by ramping too fast | Use manual warm-up schedule from SKILL.md. Disable auto warm-up in settings. |
| Categories vs Unique Args for tracking | Categories are limited to 10 per email, shown in UI. Unique Args are unlimited but only in webhooks/API. | Use Categories for high-level segmentation (transactional, marketing, onboarding). Use Unique Args for per-email tracking (user_id, campaign_id). |

### Amazon SES

| Gotcha | Impact | Fix |
|---|---|---|
| Sandbox mode limits to verified addresses only | New accounts can only send TO verified email addresses. Not just FROM. | Request production access immediately. Takes 24-48 hours. Don't start development assuming you can send freely. |
| Sending quota is per-second, not per-minute | SES rate limit is measured in emails/second. At 14/sec (default production), that's only 50,400/hour. | Request quota increase before any bulk send. Monitor `Throttling` exceptions. |
| Bounce notifications require SNS topic configuration | SES doesn't process bounces internally -- you must set up SNS topics for bounce, complaint, and delivery notifications | Configure SNS topics BEFORE sending. Without them, you're blind to bounces and will damage reputation. |
| Configuration Sets are required for event tracking | Without a Configuration Set, you get no delivery/bounce/open/click events | Always send with a Configuration Set specified in headers or API call |
| Suppression list is opt-in per Configuration Set | Unlike other ESPs, SES doesn't auto-suppress bounced addresses unless you enable account-level or config-set-level suppression | Enable account-level suppression list in SES console. This is NOT enabled by default. |
| `ses:SendEmail` vs `ses:SendRawEmail` IAM permissions | `SendEmail` API can't set custom headers. `SendRawEmail` can but needs different IAM permission. | Use `SendRawEmail` for all production email. Grant `ses:SendRawEmail` in IAM. |
| Cross-region sending has different IP pools | SES in us-east-1 and eu-west-1 use different IP addresses with different reputations | Warm up each region independently. Don't assume us-east-1 reputation transfers to eu-west-1. |

### Postmark

| Gotcha | Impact | Fix |
|---|---|---|
| Strictly transactional -- marketing email gets your account suspended | Postmark reviews sending patterns. Newsletter-like content triggers review. | Use Postmark for transactional only. Use a separate ESP for marketing. |
| Server concept separates streams | Each "Server" has its own API token, reputation, and statistics. Message Streams within a server separate transactional vs broadcast. | Create at minimum: one Server per environment (prod/staging). Use Message Streams for transactional vs broadcast within each. |
| Bounce webhooks fire for BOTH hard and soft bounces | Webhook doesn't distinguish by default in the event type | Check the `Type` field: `HardBounce` vs `SoftBounce` vs `SpamComplaint`. Handle each differently. |
| Templates require Handlebars-style syntax | Not Mustache, not Liquid, not Jinja. `{{variable}}` with `{{#if}}` and `{{#each}}`. | Don't assume your template engine works. Test with Postmark's template preview API before deploying. |
| Dedicated IP requires $50/mo add-on per IP | Dedicated IPs are not included in any plan. Shared IPs are very well-managed. | For most users (<500k/mo), Postmark's shared IPs outperform self-managed dedicated IPs. Only add dedicated for compliance or brand requirements. |

### Resend

| Gotcha | Impact | Fix |
|---|---|---|
| Built on SES infrastructure | Resend uses Amazon SES under the hood. Some SES limitations apply indirectly. | SES regional availability and rate limits may affect Resend. Monitor for SES-level throttling. |
| React Email integration is the selling point but not required | You can use any HTML template, not just React Email components | Don't rewrite existing templates to React Email. Use the plain HTML API if you already have templates. |
| API key scoping is per-domain, not per-project | One API key works for all verified domains on the account | Create separate API keys for different applications. Rotate keys if one application is compromised. |
| Webhook retry policy is limited | Fewer retries than established ESPs. Events can be lost if your endpoint is briefly down. | Use a queue (SQS, Redis) as webhook receiver. Process events asynchronously. |
| No built-in suppression list management | Resend doesn't auto-suppress bounced addresses | Build your own suppression list. Check against it before every send. |

### Mailgun

| Gotcha | Impact | Fix |
|---|---|---|
| Default sending domain includes `.mailgun.org` suffix | If you don't add a custom domain, emails send from `sandboxXXX.mailgun.org` -- guaranteed spam folder | Add and verify a custom domain immediately. Never use sandbox domain for anything user-facing. |
| EU vs US region affects data residency AND API endpoints | EU accounts use `api.eu.mailgun.net`, US accounts use `api.mailgun.net` | Specify region in SDK initialization. Wrong region = authentication failure with confusing error message. |
| Stored message retention is 3 days on free plan | After 3 days, you can't retrieve message content or debug delivery issues | Set up event webhooks from day one. Don't rely on stored messages for debugging. |
| Route matching uses priority numbers (lower = higher priority) | Priority 0 matches before priority 1. Counter-intuitive if you think higher = more important. | Document your routes with explicit priority ordering. Test route matching with the API before deploying. |
| Log retention varies by plan | Free: 1 day. Basic: 5 days. Pro: 30 days. | Export logs to your own storage for long-term debugging. |

## Migration Checklist

When switching ESPs, follow this order:

| Step | Action | Why | Timing |
|---|---|---|---|
| 1 | Set up new ESP account, verify domain, configure DNS | DNS propagation takes up to 48 hours | Week 1 |
| 2 | Update SPF record to include BOTH old and new ESP | Both ESPs must be authorized during migration | Week 1 |
| 3 | Set up DKIM for new ESP alongside existing DKIM | Use different DKIM selectors (old: `s1`, new: `s2`) | Week 1 |
| 4 | Warm up new ESP IP (if dedicated) using engaged segment | Follow warm-up schedule from SKILL.md | Week 1-4 |
| 5 | Route 10% of transactional email to new ESP | Monitor deliverability, bounce rates, latency | Week 4 |
| 6 | Gradually increase new ESP percentage (25%, 50%, 75%, 100%) | Each step: monitor for 3-5 days before increasing | Week 5-8 |
| 7 | Remove old ESP from SPF record | Only after 100% traffic on new ESP for 7+ days | Week 9 |
| 8 | Decommission old ESP DKIM selector | Remove DNS record for old selector | Week 9 |
| 9 | Cancel old ESP account | Verify no remaining traffic first | Week 10 |

**Migration risk**: Never do a hard cutover (0% -> 100% in one day). ISPs see new sending infrastructure as suspicious. Gradual migration preserves your domain reputation.

## Cost Comparison (as of 2025)

| Provider | Free Tier | Starting Paid | 100k emails/mo | 1M emails/mo |
|---|---|---|---|---|
| SendGrid | 100/day | $19.95/mo (50k) | $19.95/mo | ~$400/mo |
| Amazon SES | 62k/mo (from EC2) | $0.10/1k | $10/mo | $100/mo |
| Postmark | 100/mo trial | $15/mo (10k) | $85/mo | $475/mo |
| Resend | 3k/mo | $20/mo (50k) | $20/mo | ~$180/mo |
| Mailgun | 5k/mo (3 months) | $35/mo (50k) | $35/mo | ~$320/mo |

**Cost trap**: Cheap per-email pricing can be offset by add-on costs. SES requires separate infrastructure for bounce handling, analytics, and template management. Postmark charges $50/mo per dedicated IP. SendGrid's "Pro" tier ($89.95/mo) is where you get useful features like subuser management and IP pools.
