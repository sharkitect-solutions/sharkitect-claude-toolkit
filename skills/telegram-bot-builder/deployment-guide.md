# Telegram Bot Deployment Guide

Load when deploying a bot to production or troubleshooting production issues.

## Webhook SSL Configuration

| Setup | Pros | Cons | When to Use |
|-------|------|------|-------------|
| Let's Encrypt (certbot) | Free, auto-renewing, trusted by Telegram | Requires port 80 open for ACME challenge | VPS with public IP and domain name |
| Cloudflare proxy | Free SSL, DDoS protection, hides origin IP | Adds latency (10-50ms), requires domain | When you want Cloudflare's other features |
| Self-signed certificate | No domain needed, works with raw IP | Must upload public cert via setWebhook API call | Quick testing, no domain available |
| Reverse proxy (Nginx/Caddy) | Handles SSL termination, static files, load balancing | Extra infrastructure to maintain | Production deployments with multiple services |

### Self-Signed Certificate Setup
1. Generate: `openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out public.pem -subj "/CN=YOUR_IP"`
2. Set webhook with certificate: include `certificate` parameter in `setWebhook` API call pointing to `public.pem`
3. Gotcha: the CN in the certificate MUST match the IP or domain in the webhook URL exactly
4. Gotcha: Telegram rejects certificates with SHA-1 signature -- must use SHA-256

### Reverse Proxy Patterns

**Nginx minimal config for bot webhook:**
- Listen on 443 (or 8443) with SSL
- Proxy pass to `localhost:BOT_PORT`
- Set `proxy_read_timeout 75` (Telegram's timeout is 60s, give buffer)
- Forward `X-Telegram-Bot-Api-Secret-Token` header for validation
- Rate limit: `limit_req_zone` per IP to prevent abuse even with secret token

**Caddy automatic SSL:**
- Caddy auto-provisions Let's Encrypt certificates
- Config: `yourdomain.com { reverse_proxy localhost:BOT_PORT }`
- Zero SSL configuration needed -- handles renewal automatically
- Best option when you have a domain and want minimal SSL management

## Health Monitoring

| What to Monitor | How | Alert Threshold |
|----------------|-----|-----------------|
| Webhook delivery | Check `getWebhookInfo` -- `pending_update_count` field | >100 pending = bot is behind. >1000 = likely crashed |
| Webhook errors | `getWebhookInfo` -- `last_error_date` and `last_error_message` | Any error newer than 5 minutes |
| Response time | Measure time from webhook receipt to sendMessage response | >2 seconds average = performance issue |
| Error rate | Count 4xx/5xx responses from Telegram API per minute | >5% error rate sustained for 5 minutes |
| Memory usage | Process RSS memory | >500MB for a standard bot = likely memory leak |
| Redis connection | Ping Redis on interval | Connection failure = sessions will be lost |
| Rate limit hits | Count 429 responses per minute | >10/minute = send queue needs throttling |

### getWebhookInfo Diagnostic Fields
- `pending_update_count`: updates waiting to be delivered. Should be 0 in normal operation
- `last_error_date`: Unix timestamp of last delivery failure
- `last_error_message`: human-readable error. Common: "SSL error", "Connection timed out", "Wrong response from the webhook"
- `max_connections`: 1-100 (default 40). Higher = more parallel webhook deliveries. Increase for high-traffic bots but ensure your server can handle concurrent requests

## Graceful Shutdown

Sequence matters. Getting this wrong causes lost messages or duplicate processing.

1. **Stop accepting new webhooks**: remove webhook with `deleteWebhook` OR stop returning 200 (Telegram will queue)
2. **Finish processing in-flight updates**: wait for all current handlers to complete (set a max timeout of 30 seconds)
3. **Flush send queue**: deliver all queued outgoing messages before shutdown
4. **Persist session state**: ensure Redis/DB writes are committed, not buffered
5. **Close connections**: disconnect Redis, database, close HTTP server
6. **Exit process**: clean exit code 0

### Rolling Restart (Zero Downtime)
- For webhook bots behind a load balancer: start new instance, wait for health check pass, drain old instance, stop old
- For polling bots: CANNOT do zero downtime with multiple instances -- only one can poll at a time. Use webhook instead
- During restart gap (seconds): Telegram queues updates and redelivers when webhook comes back. No messages lost, but check for duplicate processing using `update_id` deduplication

## Self-Hosted Bot API Server

When to use: you need files >50MB upload or >20MB download, or you want faster file access without CDN routing.

| Aspect | Default Bot API | Self-Hosted |
|--------|----------------|-------------|
| File upload limit | 50 MB | 2 GB |
| File download limit | 20 MB | No limit |
| File access speed | Via Telegram CDN (variable latency) | Local filesystem (fast) |
| Setup complexity | None | Must run `telegram-bot-api` binary |
| Maintenance | Zero | You handle updates, storage, monitoring |
| Cost | Free | Server compute + storage |

### Setup Notes
- Download `telegram-bot-api` from GitHub (tdlib/telegram-bot-api)
- Requires api_id and api_hash from my.telegram.org (different from bot token)
- Files are stored locally in a working directory -- plan for disk space
- Bot token is still validated against Telegram servers -- self-hosted only handles the HTTP API layer
- Can run alongside your bot on the same server or as a separate service

## Update Processing Guarantees

| Guarantee | Webhook | Long Polling |
|-----------|---------|-------------|
| At-least-once delivery | Yes -- Telegram retries on non-200 response | Yes -- unacknowledged updates are redelivered |
| Ordering | Updates delivered in order per chat (but not guaranteed across chats) | Strictly ordered by update_id |
| Deduplication | Your responsibility -- check `update_id` | Handled by offset parameter |
| Idempotency | Required -- same update may arrive twice on network issues | Required -- offset tracking failure causes reprocessing |

### Idempotency Pattern
- Store processed `update_id` values in Redis with 24-hour TTL
- Before processing any update, check if `update_id` exists in the set
- If exists, skip processing but still return 200 to Telegram
- This prevents double-processing of messages, double-sends, and duplicate database entries

## Production Logging

| Log Level | What to Log | Example |
|-----------|-------------|---------|
| INFO | User actions, state transitions | "user=123 action=start_order state=idle->selecting_product" |
| WARN | Rate limits, slow responses, retries | "429 from Telegram, retry_after=30, chat_id=456" |
| ERROR | Failed API calls, unhandled exceptions, data corruption | "sendMessage failed: chat not found, user=789 may have blocked bot" |
| DEBUG | Full update payloads, Redis operations | "update_id=12345 type=callback_query data=approve:order:456" |

### What NOT to Log
- Bot token (appears in URL paths -- redact or use environment-based logging)
- User personal data (phone numbers from contact sharing, location data)
- Full message text in production (privacy concern, storage cost)
- Passwords or payment details (obviously, but check that library debug mode doesn't dump these)

## Backup and Recovery

| What to Back Up | Frequency | Recovery Strategy |
|----------------|-----------|-------------------|
| Redis session data | Continuous (Redis persistence: RDB + AOF) | Restore from latest RDB snapshot, replay AOF |
| Bot configuration | On change (store in version control) | Redeploy from repo |
| User database | Daily snapshots + WAL/binlog | Point-in-time recovery |
| Environment variables | On change (encrypted backup) | Restore .env from secure vault |
| Webhook URL | Documented in deployment config | Re-run setWebhook after server recovery |

### Disaster Recovery Checklist
1. New server provisioned with correct runtime (Node.js/Python version)
2. Environment variables restored from secure backup
3. Redis data restored (or accept session loss -- users restart conversations)
4. Database restored from backup
5. Bot code deployed from version control
6. Webhook set to new server URL: `setWebhook(url=NEW_URL, secret_token=TOKEN)`
7. Verify with `getWebhookInfo` -- check `pending_update_count` for queued updates
8. Monitor for 15 minutes: check error rate, response time, session restoration
