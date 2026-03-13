---
name: telegram-bot-builder
description: "Use when building Telegram bots, designing bot conversation flows, choosing bot libraries, configuring webhooks or polling, implementing Telegram Payments or Stars, handling Telegram API rate limits or file size constraints, or scaling a bot beyond hobby usage. NEVER for voice-based bot experiences (use voice-agents), no-code bot automation via n8n (use n8n-workflow-patterns), full web applications that happen to include a Telegram bot (use app-builder), Discord/Slack/WhatsApp bots (platform-specific skills)."
---

# Telegram Bot Builder

## Scope Boundary

| Request | This Skill | Defer To |
|---------|-----------|----------|
| Build a Telegram bot from scratch | YES | -- |
| Voice bot with speech recognition | NO | voice-agents |
| Connect Telegram to n8n workflows | NO | n8n-workflow-patterns |
| Full SaaS product with Telegram integration | NO | app-builder |
| Bot payment integration (Stars, Stripe) | YES | -- |
| Deploy bot to cloud infrastructure | Webhook/polling config only | docker-expert for containers |
| Bot database schema design | NO | senior-architect |
| Telegram Mini App (TWA) | NO | app-builder |

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Bot architecture decisions, library selection, API gotchas, scaling | Always (auto-loaded) |
| conversation-patterns.md | Scene/wizard lifecycle, FSM transition tables, deep linking, group chat patterns, inline mode, command routing | When designing multi-step conversation flows or complex bot interactions |
| api-limits-reference.md | Rate limit tables, file size limits by type, MarkdownV2 escaping, callback data constraints, media group rules | When troubleshooting API errors, formatting issues, or rate limit problems |
| deployment-guide.md | Webhook SSL setup, reverse proxy configs, health monitoring, graceful shutdown, self-hosted Bot API, backup/recovery | When deploying to production or troubleshooting production issues |

## Bot Development Procedure

Follow this sequence for every Telegram bot request. Do not jump to code.

1. **Clarify the bot's core loop**: What is the single most common user interaction? A bot that does one thing well beats a bot with 10 half-built features. If the user describes multiple features, identify which one drives retention. If the user already has a running bot and wants to extend it, skip to step 4.
2. **Choose library using Decision Matrix**: Match the first signal below. If the user already has a codebase with a specific library, use it -- do not suggest switching unless they report a blocking limitation.
3. **Decide polling vs webhook**: Use the Architecture Decision Matrix. If already in production with polling, only migrate to webhook when hitting rate limits or needing serverless deployment.
4. **Design conversation flow**: Match complexity to the State Machine Selection table. If the user describes a flow that sounds like FSM but only has 2-3 steps, push back -- use a scene/wizard instead. If they describe free-form input, verify whether they actually need NLP or just a text handler.
5. **Plan scaling from day one**: Choose session storage based on expected user count from the Scaling Patterns table. If the bot is already live and losing state on restart, skip planning and immediately migrate sessions to Redis -- this is the emergency fix.

**Key mindset**: Most bot projects fail not from bad code but from wrong scope. A bot that handles one use case end-to-end (including error states, edge cases, and graceful failures) ships faster and retains users better than a bot that half-handles five use cases.

## Library Selection Decision

Choose based on the FIRST matching signal:

| Signal | Choose | Reason |
|--------|--------|--------|
| Team knows TypeScript, wants type safety | grammy | Best TS support, transformer middleware |
| Rapid prototype, Python team | python-telegram-bot | Lowest time-to-hello-world |
| High-concurrency Python (>500 req/s) | aiogram | Async-native, no sync bottlenecks |
| Node.js team, large plugin ecosystem needed | Telegraf | Most middleware/plugins available |
| Need raw API control, any language | Direct HTTP | Libraries add overhead you may not want |
| Long-running background tasks in Python | aiogram | Telegraf and grammY lack native job queues |

**Override rule**: If the user has already chosen a library, use it. Do not suggest switching unless they report a specific problem the library cannot solve.

Warning: Do NOT mix libraries. Pick one per bot. Migration between them is painful due to middleware/context API differences.

## Bot Architecture Decision Matrix

### Polling vs Webhook

| Factor | Long Polling | Webhook |
|--------|-------------|---------|
| Development/local testing | USE THIS | Requires tunnel (ngrok) |
| Production deployment | Only if no public URL | USE THIS |
| Serverless (Lambda, CF Workers) | Impossible | USE THIS |
| VPS/dedicated server | Works but wasteful | USE THIS |
| Multiple bot instances | Race conditions | Load-balanced safely |
| Latency | 1-2s delay typical | Near-instant |
| Firewall-restricted environments | USE THIS (outbound only) | Needs inbound HTTPS on 443/80/88/8443 |

Decision: Use polling for development. Use webhooks for production. The only production exception is firewall-restricted environments where inbound HTTPS is blocked. If the user has a working polling setup they want to keep, do not force webhook migration unless they hit scaling limits.

### Webhook Configuration Gotchas
- Telegram only connects to ports 443, 80, 88, or 8443 -- no other ports work
- Self-signed certificates: must upload your public cert via setWebhook
- Secret token header (`X-Telegram-Bot-Api-Secret-Token`) -- always set this, validate on every request
- `setWebhook` silently succeeds even if your URL is unreachable -- test with `getWebhookInfo`
- Webhook response must return 200 within 60 seconds or Telegram retries with exponential backoff

## Conversation Flow Design

### State Machine Selection

| Flow Complexity | Pattern | Example |
|----------------|---------|---------|
| Single question-answer | Stateless handler | /weather command |
| 2-3 step linear form | Scene/wizard | Collect name + email |
| Branching dialog (>3 paths) | Finite state machine with named states | Support ticket triage |
| Free-form + structured mix | Hybrid: FSM for structure, NLP for free-form steps | AI chatbot with settings menu |

### Input Type Selection

| Need | Use | Avoid |
|------|-----|-------|
| Choose from <4 options | Inline keyboard | Reply keyboard (takes screen space) |
| Choose from 4-8 options | Inline keyboard with columns | Single-column (too tall) |
| Choose from >8 options | Paginated inline keyboard or text search | Massive button grid |
| Free text input (names, descriptions) | ForceReply or plain text handler | Inline keyboard |
| Persistent quick actions | Reply keyboard with resize | Inline keyboard (disappears) |
| Binary yes/no | Inline keyboard on same message | Separate message |

### Menu Depth Limit
Never exceed 3 levels of nested menus. At depth 4+, users lose context of where they are. If you need more depth, redesign as search or category filters.

## Telegram API Gotchas Catalog

| Gotcha | Detail | Mitigation |
|--------|--------|------------|
| Message edit timeout | Cannot edit messages older than 48 hours | Store message timestamps, fall back to new message |
| Callback query answer | MUST call `answerCallbackQuery` within 30 seconds or user sees loading spinner forever | Always answer, even on error |
| File size upload limit | 50 MB via bot API, 20 MB for photos | For larger files, upload to external storage, send URL |
| File size download limit | 20 MB via `getFile` | Use Telegram CDN URL directly for larger files |
| Rate limit (per chat) | ~30 messages/second to same chat | Queue messages, batch with delays |
| Rate limit (global) | ~30 messages/second across all chats (may vary) | Implement global send queue with backoff |
| Flood control (bulk send) | Sending to many users triggers 429 errors | Max ~25-30 messages/second, spread across 1-second windows |
| Group vs private behavior | Bot cannot see messages in groups unless BotFather `/setprivacy` is disabled or bot is admin | Document this for users; check `chat.type` |
| Inline mode rate limit | Results cached by Telegram for `cache_time` seconds | Set `cache_time` to 0 during development, 300+ in production |
| HTML parse mode quirks | Only supports a subset of HTML -- no `<div>`, no `<br>`, use `\n` for newlines | Stick to `<b>`, `<i>`, `<code>`, `<pre>`, `<a>` |
| Message length limit | 4096 characters for text, 1024 for captions | Split long messages, paginate |
| Silent message failures | `sendMessage` to a user who blocked the bot returns 403 -- no event, no notification | Catch 403, mark user inactive |

## Bot Monetization Architecture

### Payment Method Decision

| Scenario | Method | Why |
|----------|--------|-----|
| Digital goods (stickers, premium features) | Telegram Stars | No payment provider needed, native UX, Apple/Google compliant |
| Physical goods or services | Telegram Payments (Stripe/etc.) | Stars not allowed for physical goods |
| Subscription model | External payment + webhook | Telegram Payments lacks recurring billing natively |
| One-time digital purchase | Stars (preferred) or Telegram Payments | Stars has lowest friction |
| Users in restricted countries | External payment link | Telegram Payments provider coverage varies |

### Stars Currency Notes
- 1 Star ~= $0.02 USD (varies, Telegram sets exchange rate)
- Bot receives 100% of Stars (no platform commission currently)
- Refund window: user can request refund for unreceived goods
- Stars work in Mini Apps too -- unified across bot and web app

### Usage-Based Gating Pattern
- Track usage in your database, not in Telegram (no built-in quota system)
- Check limits BEFORE executing the action, not after
- Show remaining quota in bot responses ("3/10 free uses remaining today")
- Offer upgrade inline at the limit message -- do not just block

## Scaling Patterns

| User Count | Session Storage | Update Delivery | Key Concern |
|------------|----------------|-----------------|-------------|
| <1K | In-memory (Map/dict) | Polling OK | Simplicity |
| 1K-10K | Redis | Webhook required | Session persistence across restarts |
| 10K-100K | Redis cluster + DB for permanent data | Webhook + queue (Bull/Celery) | Message send rate limits |
| >100K | Sharded Redis + DB + dedicated send workers | Webhook + message queue + worker pool | Flood control, graceful degradation |

### Critical Scaling Rules
- Never store sessions in memory in production -- single restart loses all user state
- Separate "receive updates" from "send messages" -- send queue prevents rate limit cascades
- Bot API server can be self-hosted (telegram-bot-api) for removing file size limits and faster file access
- Use `getUpdates` offset tracking carefully -- missed offsets mean duplicate processing

## Bot UX Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| Menu Hell | 5+ levels of nested inline keyboards, users get lost. 40%+ drop-off per menu level beyond 3. | Flatten to max 3 levels, add "Back to Main" at every level |
| Spam Bot | Unsolicited messages, daily "tips", broadcast abuse. Telegram bans bots with >0.1% spam report rate. | Only message on user action or explicit opt-in notification |
| Silent Failure | Bot receives message, does nothing (no reply, no error). Users retry 2-3 times then abandon permanently. | Always reply -- even "I didn't understand" is better than silence |
| Keyboard Overload | 20+ buttons in one message | Paginate at 8, use categories, or switch to text search |
| No Onboarding | /start sends "Welcome!" and nothing else | Guide first action: show main menu, explain what bot does in 1-2 lines |
| State Amnesia | Bot forgets mid-conversation context after restart | Persist conversation state to Redis/DB, not memory |
| Wall of Text | Bot sends 2000-character messages | Break into multiple short messages with 200ms delay between |
| Confirmation Trap | Every single action requires "Are you sure?" | Only confirm destructive/irreversible actions |

## Pre-Launch Checklist

Verify before deploying any bot to production:

| Check | Why | Fail = |
|-------|-----|--------|
| Bot token in env var, not in code | Token in repo = compromised bot | Security breach |
| `/start` handler implemented | First thing every user triggers | Broken first impression |
| `answerCallbackQuery` on every inline button | Missing = permanent loading spinner | Users think bot is broken |
| Error handler registered | Unhandled error = crash = offline bot | Silent downtime |
| Webhook secret token set and validated | Without it, anyone can POST fake updates | Spoofed messages |
| Session storage is persistent (Redis/DB) | In-memory = data loss on restart | State amnesia |
| Rate limit queue for sends | Tight loops trigger 429 bans | Extended API ban |
| 403 handling for blocked users | Blocked users return 403 silently | Wasted send attempts, potential ban |

## Rationalization Table

| The agent might think... | But actually... |
|--------------------------|-----------------|
| "I should include the full Telegraf/grammY setup code" | Claude knows these libraries. Link to docs or describe the pattern. |
| "The bot needs a database, let me design the schema" | Database design is senior-architect territory. This skill covers bot-specific session storage only. |
| "I'll add webhook + polling + both options in the code" | Pick one based on the deployment context. Shipping both creates dead code. |
| "Let me build a web dashboard for bot admin" | That is a full web app (app-builder). Bot admin should be a separate admin bot or BotFather settings. |
| "I should handle voice messages with speech-to-text" | Voice processing is voice-agents scope. This skill can receive voice files but not process audio. |
| "The user wants a chatbot, so I need an AI/LLM integration" | Not all Telegram bots need AI. Clarify if they want command-driven, menu-driven, or conversational AI. |

## Red Flags

1. Bot token hardcoded in source code -- must be in environment variable
2. No `answerCallbackQuery` after inline button press -- causes permanent loading spinner
3. Webhook URL using HTTP instead of HTTPS -- Telegram rejects it silently
4. Storing user sessions in memory for a production bot -- data lost on restart
5. Sending messages in a tight loop without rate limiting -- triggers 429 flood control
6. No error handler registered -- unhandled errors crash the bot process
7. Using `setPrivacy` disabled in groups without informing users -- privacy concern
8. No `/start` command handler -- required by Telegram, first thing users trigger

## NEVER

1. Never store bot tokens in code, config files, or logs -- environment variables only
2. Never send unsolicited bulk messages without explicit user opt-in -- Telegram will ban the bot
3. Never ignore `429 Too Many Requests` responses -- implement exponential backoff or face extended bans
4. Never assume group and private chat behavior are identical -- permissions, privacy mode, and admin rights differ
5. Never skip webhook secret token validation -- any server on the internet can POST to your webhook URL
