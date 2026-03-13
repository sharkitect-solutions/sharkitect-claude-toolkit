# Email Queue Architecture Patterns

Load when building email sending infrastructure, implementing retry logic, or designing queue architecture for transactional or marketing email.

## Queue Architecture Decision

| Signal | Architecture | Why |
|---|---|---|
| Simple app, <1k emails/day, single server | In-process queue (BullMQ, Celery) | No external infrastructure. Queue lives in your process. Acceptable failure mode: emails lost on crash. |
| Production app, 1k-100k/day, reliability required | Dedicated queue service (Redis + BullMQ, RabbitMQ, or SQS) | Queue survives app restarts. Retry logic. Dead letter handling. |
| High volume, >100k/day, multiple services send email | Centralized email service with message broker | Kafka/SQS -> Email microservice. All email goes through one service that owns ESP config, templates, and deliverability. |
| Multi-region, compliance requirements | Regional queue + regional ESP configuration | Email data stays in-region. Queue per region with region-specific ESP endpoints. |

## Queue Implementation Patterns

### Pattern 1: Direct Queue (Simple)

```
App -> Queue -> Worker -> ESP
```

| Component | Role | Implementation |
|---|---|---|
| App | Enqueues email job with recipient, template, and data | `queue.add('send-email', { to, template, data })` |
| Queue | Stores jobs, handles retry on failure | Redis (BullMQ), RabbitMQ, or SQS |
| Worker | Dequeues job, renders template, calls ESP API | Separate process or serverless function |
| ESP | Sends the actual email | SendGrid, Postmark, SES, etc. |

**When to use**: Single application, straightforward email needs, team of 1-3 developers.

### Pattern 2: Priority Lanes

```
App -> Router -> High Priority Queue -> Worker Pool -> ESP
                 Normal Priority Queue -> Worker Pool -> ESP
                 Bulk Queue -> Rate-Limited Worker -> ESP
```

| Lane | Use Case | SLA | Rate Limit |
|---|---|---|---|
| High priority | Password resets, 2FA codes, payment confirmations | <30 seconds | No limit (process immediately) |
| Normal priority | Welcome emails, receipts, notifications | <5 minutes | ESP rate limit / 2 |
| Bulk | Marketing campaigns, newsletters, digest emails | <2 hours | ESP rate limit / 4 (spread over time) |

**When to use**: Mix of transactional and marketing email. Password resets must never wait behind a 50k newsletter blast.

**Lane assignment rule**: The application declares priority. The queue enforces it. Workers poll high-priority first, then normal, then bulk. Bulk workers pause when high-priority queue depth > 0.

### Pattern 3: Fan-Out with Deduplication

```
App -> Message Broker (Kafka/SNS) -> Email Service -> Queue -> ESP
                                  -> Analytics Service
                                  -> Audit Log
```

| Component | Role | Why Separate |
|---|---|---|
| Message Broker | Publishes "send email" events. Multiple consumers. | Email service, analytics, and audit all need the same event. |
| Email Service | Owns ESP configuration, templates, deliverability | Single service responsible for all email. No other service calls ESP directly. |
| Analytics | Tracks email events (sent, delivered, opened, clicked) | Decoupled from sending. Analytics failures don't block email. |
| Audit Log | Records all email events for compliance | Required for GDPR, HIPAA, SOC 2 audit trails. |

**When to use**: Multiple services need to trigger email (auth service, billing, notifications). Centralizing email prevents ESP config sprawl.

## Retry Strategy

### Exponential Backoff with Jitter

| Attempt | Base Delay | With Jitter | Max Delay |
|---|---|---|---|
| 1 | Immediate | Immediate | -- |
| 2 | 30 seconds | 15-45 seconds | -- |
| 3 | 2 minutes | 1-3 minutes | -- |
| 4 | 10 minutes | 5-15 minutes | -- |
| 5 | 1 hour | 30-90 minutes | -- |
| 6 | 4 hours | 2-6 hours | 6 hours max |

**Jitter is mandatory**: Without jitter, all failed emails retry at the same time, creating a thundering herd that trips ESP rate limits again.

### Retry Decision by Error Type

| Error Type | Retry? | Max Attempts | Notes |
|---|---|---|---|
| ESP rate limit (429) | Yes | 6 | Back off. Check rate limit headers for `Retry-After`. |
| ESP server error (5xx) | Yes | 4 | ESP is down temporarily. |
| Network timeout | Yes | 3 | Check if email was actually sent before retrying (idempotency). |
| Invalid recipient (400, hard bounce) | No | 0 | Suppress the address. Do not retry. |
| Authentication failure (401/403) | No | 0 | API key is wrong or expired. Alert ops team. Do not retry. |
| Template rendering error | No | 0 | Fix the template. Retrying will produce the same error. |
| Payload too large (413) | No | 0 | Reduce attachment size or inline content. |

### Idempotency Keys

**Critical for retry safety**: Without idempotency, retrying a failed send can deliver the email twice.

| Approach | How | Tradeoff |
|---|---|---|
| ESP-provided idempotency | Postmark: `X-PM-Message-Id`. SES: `MessageId` in response. | Only works if you capture the ID before the failure. |
| Application-generated key | Generate UUID per email job. Store in queue metadata. Check before re-sending. | Requires a store (Redis, database) to track sent IDs. |
| Content hash | Hash of (recipient + template + timestamp rounded to minute) | Simple but can false-positive on legitimate duplicate sends (e.g., two orders in the same minute). |

**Recommended**: Application-generated UUID stored in Redis with 24-hour TTL. Before each send attempt, check if UUID exists in Redis. If yes, skip (already sent or in-flight).

## Dead Letter Queue (DLQ) Handling

Emails that exhaust all retry attempts go to the DLQ. This is NOT a trash bin -- it's an alert.

| DLQ Action | When | How |
|---|---|---|
| Alert ops team | Every time DLQ depth > 0 | Slack/PagerDuty alert on DLQ metric |
| Manual review | Within 4 hours of alert | Check error reason. Is it a systemic issue (ESP down, auth expired) or per-email issue (bad address)? |
| Replay | After fixing the systemic issue | Move DLQ messages back to main queue. Process normally. |
| Discard | Per-email issue that can't be fixed | Log the failure. Update suppression list if it's a bad address. |
| Escalate | Pattern of failures (>5% DLQ rate) | Something is fundamentally wrong. ESP account issue, DNS misconfiguration, or code bug. |

**DLQ retention**: Keep DLQ messages for 7 days. After 7 days, the email is stale and sending it would confuse the recipient (e.g., "Your password reset" from a week ago).

## Rate Limiting

### ESP Rate Limits by Provider

| Provider | Default Rate Limit | How to Increase |
|---|---|---|
| SendGrid | 600/min (Essentials), 3000/min (Pro) | Upgrade plan or contact support |
| Amazon SES | 14/sec (default production), configurable up to 500/sec | Request via AWS support ticket |
| Postmark | 500/sec (shared), configurable on dedicated | Contact support for custom limits |
| Resend | 2/sec (free), 10/sec (paid) | Upgrade plan |
| Mailgun | 300/min (free), configurable on paid | Contact support |

### Client-Side Rate Limiting

Never rely solely on ESP rate limits. Implement your own:

| Strategy | How | Why |
|---|---|---|
| Token bucket | Refill N tokens per second. Each send consumes 1 token. | Smooth sending rate. Handles bursts up to bucket size. |
| Sliding window | Count sends in last N seconds. Block if over limit. | Simple to implement. Less smooth than token bucket. |
| Adaptive | Monitor ESP 429 responses. Reduce rate by 50% on 429. Increase by 10% every minute with no 429. | Self-tuning. Best for variable load. |

**Why client-side**: ESP rate limiting returns 429 errors that count as failures and trigger retry logic. Your own rate limiter prevents sending the request at all, avoiding failed attempts and reputation damage from excessive 429s.

## Monitoring Essentials

| Metric | Alert Threshold | What It Means |
|---|---|---|
| Queue depth (per lane) | High priority > 100, Normal > 10k | Sending is falling behind. Scale workers or check ESP. |
| DLQ depth | > 0 for > 15 minutes | Failed emails are accumulating. Investigate immediately. |
| Send latency (queue to ESP accept) | P95 > 10 seconds | Worker bottleneck or ESP slowdown. |
| ESP error rate (non-retry) | > 1% | Systemic issue: auth, DNS, or ESP-side problem. |
| Retry rate | > 5% of all sends | Transient issues are too frequent. Check ESP health. |
| Duplicate send rate | > 0.1% | Idempotency is failing. Check key generation and storage. |
