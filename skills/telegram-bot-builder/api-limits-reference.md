# Telegram Bot API Limits & Formatting Reference

Load when troubleshooting rate limits, file operations, or message formatting issues.

## Rate Limits

Telegram does not publish official rate limit numbers. These are empirically determined by the community and may change.

| Context | Limit | What Happens on Exceed | Mitigation |
|---------|-------|----------------------|------------|
| Messages to same chat | ~30/second | 429 Too Many Requests, retry_after header | Queue per-chat with 35ms minimum delay |
| Messages across all chats | ~30/second (varies by bot age/reputation) | 429 with increasing retry_after | Global send queue, respect retry_after exactly |
| Bulk broadcast to many users | ~25-30 users/second | 429, escalating to temporary ban if ignored | Spread across 1-second windows, honor retry_after, implement exponential backoff |
| Group messages (bot is member of many groups) | Lower effective limit than private chats | 429 with longer retry_after (60s+) | Prioritize groups, batch updates |
| Inline query answers | 1 answer per query (last one wins) | Earlier answers silently dropped | Debounce, answer only the latest query |
| Webhook response | Must return 200 within 60 seconds | Telegram retries with exponential backoff (up to 1 hour) | Process async, return 200 immediately |
| setWebhook | No explicit limit but Telegram throttles rapid changes | Silently ignored or delayed | Set once on deploy, verify with getWebhookInfo |
| getUpdates (long polling) | timeout parameter max 50 seconds | Connection dropped | Set timeout: 30, reconnect immediately |

### Retry Strategy
1. On 429: read `retry_after` from response, wait EXACTLY that many seconds (not less)
2. Do NOT retry before retry_after expires -- Telegram increases the penalty for impatient retries
3. After 3 consecutive 429s, pause all sends for 60 seconds
4. Log every 429 with timestamp and chat_id to identify hot loops

## File Size Limits

| Operation | Limit | Notes |
|-----------|-------|-------|
| Upload via multipart (sendDocument, sendPhoto, etc.) | 50 MB | Bot API limit, not Telegram's internal limit |
| Download via getFile | 20 MB | Returns file_path for CDN download |
| Photo upload | 10 MB (JPG/PNG) | Telegram compresses to max 1280px on longest side |
| Photo as document | 50 MB | Preserves original quality but loses gallery preview |
| Video upload | 50 MB via API | 2 GB via Telegram client (but bots can't send >50MB without self-hosted Bot API) |
| Voice/audio | 50 MB | Telegram converts voice to .ogg Opus |
| Sticker (static) | 512 KB PNG | Must be 512x512px |
| Sticker (animated) | 64 KB TGS | Lottie-based, strict format requirements |
| Sticker (video) | 256 KB WEBM | VP9 codec, max 3 seconds, 512x512px |

### Self-Hosted Bot API Server
- Removes the 50 MB upload limit (sends up to 2 GB)
- Removes the 20 MB download limit
- Files served locally instead of via Telegram CDN
- Requires running `telegram-bot-api` server alongside your bot
- Trade-off: you manage the infrastructure, but gain full file size access

## Message Formatting

### MarkdownV2 Characters That MUST Be Escaped
These characters must be escaped with backslash outside of code blocks: `_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`

This is the most common source of "Bad Request: can't parse entities" errors. When in doubt, escape everything that isn't markup.

| Format | MarkdownV2 Syntax | HTML Equivalent | Notes |
|--------|-------------------|-----------------|-------|
| Bold | `*bold*` | `<b>bold</b>` | Nesting: `*bold _and italic_*` |
| Italic | `_italic_` | `<i>italic</i>` | |
| Underline | `__underline__` | `<u>underline</u>` | MarkdownV2 only |
| Strikethrough | `~strike~` | `<s>strike</s>` | |
| Spoiler | `\|\|spoiler\|\|` | `<tg-spoiler>text</tg-spoiler>` | Tap to reveal |
| Monospace | `` `code` `` | `<code>code</code>` | |
| Code block | ` ```lang\ncode``` ` | `<pre><code class="language-lang">code</code></pre>` | Language hint optional |
| Link | `[text](url)` | `<a href="url">text</a>` | URL must be valid |
| Mention | `[name](tg://user?id=123)` | `<a href="tg://user?id=123">name</a>` | Works even if user has no username |
| Custom emoji | Uses emoji entity type | Not available in basic text | Requires Telegram Premium or bot sticker sets |

### Parse Mode Decision
- Use `HTML` for programmatically generated messages (easier to construct, no escaping headaches)
- Use `MarkdownV2` for user-facing templates where readability of the template matters
- Use no parse mode (plain text) when content includes user-generated text that might contain special characters
- Mixing parse modes in one bot is fine -- set per-message

## Callback Data Constraints

| Constraint | Limit | Workaround |
|-----------|-------|------------|
| Max length | 64 bytes (not characters -- UTF-8 multibyte counts) | Store payload in Redis, use UUID as callback data |
| Unique per keyboard | Yes -- duplicate callback_data in same keyboard causes unpredictable behavior | Append unique suffix (e.g., `approve:123:a`, `approve:123:b`) |
| Persistence | Callback data lives as long as the message with the inline keyboard | Old messages (>48h) may fail to edit but callbacks still fire |
| answerCallbackQuery | MUST be called within 30 seconds | Always call it, even in error handlers. User sees perpetual spinner otherwise |

### Callback Answer Options
| Parameter | Effect | When to Use |
|-----------|--------|-------------|
| text (no show_alert) | Small toast notification at top of chat | Confirmations ("Item added to cart") |
| text + show_alert: true | Modal popup that requires dismissal | Important warnings ("This action cannot be undone") |
| url | Opens URL in Telegram browser | Payment links, external resources |
| (no parameters) | Dismisses loading spinner silently | When the UI update via editMessageText is sufficient feedback |

## Media Group Rules

| Rule | Detail |
|------|--------|
| Max items | 10 photos/videos per media group |
| Mixed types | Photos and videos can be mixed. Documents cannot be mixed with photos/videos |
| Captions | Only the FIRST item's caption is displayed prominently. Other captions are hidden |
| Edit | Cannot add/remove items from a sent media group. Can only edit captions |
| Send delay | All items must be sent in a single `sendMediaGroup` call -- you cannot append |
| Parse mode | Caption parse mode applies per-item but only the first caption is visible |

## Edit Message Constraints

| Constraint | Detail |
|-----------|--------|
| Time limit | Messages older than 48 hours cannot be edited |
| Content change | New content must differ from current -- identical edit returns error |
| Inline keyboard | Can update keyboard without changing text (editMessageReplyMarkup) |
| Media swap | Can change photo-to-photo or video-to-video but not photo-to-text |
| Bot messages only | Bot can only edit its own messages, not user messages |
| Channel posts | Bot can edit channel posts if it has admin rights |
