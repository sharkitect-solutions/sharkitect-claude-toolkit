# Telegram Bot Conversation Patterns

Load when designing conversation flows beyond simple command-response.

## Scene/Wizard Lifecycle

Every multi-step flow follows: enter -> collect steps -> validate -> exit (complete or cancel).

| Lifecycle Event | What Happens | Common Mistake |
|----------------|--------------|----------------|
| Scene enter | Initialize state, send first prompt, register step handlers | Forgetting to clear stale state from previous abandoned attempts |
| Step handler | Validate input, store in scene state, advance or re-prompt | Not handling unexpected input types (user sends photo when text expected) |
| Scene leave | Persist collected data, clean up scene state, confirm to user | Leaving scene state in memory after completion (memory leak on long-running bots) |
| Cancel/timeout | User sends /cancel or no input for N minutes | Not implementing timeout -- scene stays active forever, confusing the user days later |

### Timeout Strategy
- Set scene timeout to 10-15 minutes for form-style flows
- Send a reminder at 80% of timeout ("Still working on this? Reply to continue or /cancel")
- On timeout: exit scene, send "Your [action] was cancelled due to inactivity. Use /start to begin again"
- Store partially completed data if resumption is valuable

## FSM Transition Table Pattern

For flows with 3+ branching paths, define transitions explicitly:

| Current State | Input/Event | Next State | Action |
|--------------|-------------|------------|--------|
| idle | /order | selecting_product | Show product catalog |
| selecting_product | product_callback | confirming_quantity | Show quantity picker |
| selecting_product | /cancel | idle | Clear selection |
| confirming_quantity | valid_number | reviewing_order | Show order summary |
| confirming_quantity | invalid_input | confirming_quantity | Re-prompt with validation error |
| reviewing_order | confirm_callback | processing_payment | Initiate payment |
| reviewing_order | edit_callback | selecting_product | Return to catalog with previous selection highlighted |
| processing_payment | payment_success | idle | Send receipt, clear state |
| processing_payment | payment_failure | reviewing_order | Show error, offer retry |

### FSM Implementation Rules
- Every state must handle unexpected input (default handler that re-prompts)
- Every state must handle /cancel (escape hatch)
- Store current state in persistent storage (Redis/DB), never in-memory variables
- Log state transitions for debugging ("user 123: selecting_product -> confirming_quantity")

## Deep Linking Patterns

Telegram deep links (`t.me/botname?start=PAYLOAD`) enable re-engagement and feature routing.

| Use Case | Payload Format | Handler Logic |
|----------|---------------|---------------|
| Referral tracking | `ref_USER123` | Credit referring user, track conversion |
| Feature shortcut | `feature_settings` | Skip menu, jump to settings flow |
| Notification action | `action_approve_456` | Process the specific action (approve item 456) |
| Group onboarding | `group_CHATID` | Pre-configure bot for specific group context |
| Reactivation | `return_CAMPAIGN` | Show personalized welcome-back message based on campaign |

### Deep Link Gotchas
- Payload max 64 characters (base64 encode if needed)
- Payload is passed to /start handler -- route based on prefix
- Deep links ONLY work in private chats, not groups
- Users who already started the bot still trigger /start with the payload
- URL-encode special characters in payload -- Telegram strips some

## Group Chat Admin Patterns

| Pattern | Implementation | Why Non-Obvious |
|---------|---------------|-----------------|
| Admin-only commands | Check `getChatMember` status before executing | `message.from` is the user, `message.chat` is the group -- don't confuse them |
| Settings per group | Key settings by `chat.id`, not `user.id` | Multiple admins in same group need shared settings, not per-user |
| Welcome new members | Handle `new_chat_members` update type | Array can contain multiple users (bulk add). Bot itself appears here when added to group |
| Anti-spam moderation | Delete message + restrict user, not ban | Banning is irreversible in the moment. Restrict (mute) is reversible. Escalate on repeat |
| Channel post forwarding | Use `channel_post` update type, not `message` | Bots in channels receive `channel_post`, not `message`. Different update field entirely |

### Group Permission Matrix

| Bot Permission | Required For | How to Check |
|---------------|-------------|--------------|
| Read messages | Responding to group commands | Privacy mode OFF (BotFather /setprivacy) or bot is admin |
| Delete messages | Moderation | Bot must be admin with "Delete Messages" permission |
| Restrict users | Anti-spam/timeout | Bot must be admin with "Restrict Members" permission |
| Pin messages | Announcements | Bot must be admin with "Pin Messages" permission |
| Invite link | Referral/invite features | Bot must be admin with "Invite Users via Link" permission |

## Inline Mode Result Patterns

| Result Type | When to Use | Cache Time |
|-------------|------------|------------|
| Article | Text-based search results (FAQ, documentation) | 300s in production |
| Photo | Image search, meme generation | 300s (unless personalized) |
| GIF | Animation search | 300s |
| Document | File search, generated exports | 0s (if content changes per query) |
| Voice | Audio search results | 300s |

### Inline Query Optimization
- Debounce: Telegram sends a query on every keystroke. Set `cache_time` and use `offset` for pagination
- Empty query: handle the case where user triggers inline mode with no text (show recent/popular results)
- Personal results: set `is_personal: true` if results differ per user (disables shared cache, increases API load)
- Feedback: `chosen_inline_result` update only fires if enabled via BotFather /setinlinefeedback -- useful for analytics but adds load

## Command Routing Architecture

For bots with 10+ features, flat command handling creates unmaintainable code. Use module routing:

| Pattern | Structure | When to Use |
|---------|-----------|-------------|
| Feature modules | Each feature registers its own handlers (commands, callbacks, messages) | 5-15 features, single developer |
| Plugin system | Features loaded dynamically, shared middleware | 15+ features, multiple developers |
| Command groups | Prefix-based routing (/admin_*, /settings_*, /order_*) | Quick organization, no architectural change needed |

### Callback Data Routing
- Callback data is limited to 64 bytes
- Use a prefix convention: `action:entity:id` (e.g., `approve:order:456`)
- Parse the prefix to route to the correct handler module
- For complex data, store the full payload in Redis with a short UUID as the callback data
- Never put sensitive data in callback data -- it's visible in Telegram's servers
