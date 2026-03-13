# SMS & WhatsApp Messaging Patterns Guide

Load when implementing SMS messaging features, WhatsApp Business API, or designing message delivery architecture with Twilio.

## SMS Segment Optimization

### Segment Encoding Rules

| Character Set | Chars Per Segment | Max Concatenated | Detection |
|---|---|---|---|
| GSM-7 (basic Latin, digits, common symbols) | 160 (single) / 153 (concatenated) | 1,530 chars (10 segments) | All characters in GSM 03.38 basic character set |
| GSM-7 extended (€, {, }, [, ], ~, \, ^) | 160 but extended chars count as 2 | Same | Contains any extended character -- each uses 2 code points |
| UCS-2 (Unicode -- emoji, Chinese, Arabic, accented chars) | 70 (single) / 67 (concatenated) | 670 chars (10 segments) | Any character outside GSM-7 triggers UCS-2 for entire message |

**Critical gotcha**: A single emoji or non-GSM character switches the ENTIRE message to UCS-2, cutting capacity from 160 to 70 characters. One emoji in a 140-character message turns 1 segment into 3 segments (3x cost).

| Common UCS-2 Triggers | Alternative |
|---|---|
| Smart quotes (" " ' ') | Use straight quotes (" ') |
| Em dash (—) | Use hyphen-minus (-) or double hyphen (--) |
| Ellipsis character (…) | Use three periods (...) |
| Emoji (any) | Remove or replace with text |
| Accented characters (é, ñ, ü) | Keep if audience requires; accept UCS-2 cost |

### Message Template Patterns

| Message Type | Template | Segment Count | Notes |
|---|---|---|---|
| OTP / Verification | `Your code is 847291. It expires in 10 minutes. Don't share this code.` | 1 (GSM-7) | Always include expiry. Never include links (phishing red flag). |
| Order confirmation | `Order #4521 confirmed. $47.99 charged. Arrives Mar 15-17. Track: [short-domain]/t/4521` | 1 (GSM-7) | Use your own short domain, never generic shorteners (spam signal). |
| Appointment reminder | `Reminder: Dr. Smith on Mar 12 at 2:30 PM. Reply YES to confirm or call 555-0123 to reschedule.` | 1 (GSM-7) | Include actionable response option. |
| Delivery update | `Your package from StoreName is out for delivery. Expected by 5 PM today.` | 1 (GSM-7) | Don't include tracking links in every update -- link in final "delivered" message only. |

### Messaging Service Configuration

| Setting | Recommended Value | Why |
|---|---|---|
| Sticky Sender | Enabled | Same sender number for each recipient -- builds recognition and trust |
| Smart Encoding | Enabled | Auto-replaces smart quotes and special chars with GSM-7 equivalents to avoid UCS-2 |
| Country Code Geomatch | Enabled for marketing, disabled for transactional | Marketing: local numbers get higher response rates. Transactional: speed matters more. |
| Validity Period | 4 hours (OTP), 24 hours (alerts), 72 hours (marketing) | Expired messages aren't delivered -- prevents stale OTPs and irrelevant notifications |
| MMS fallback | Disabled unless needed | MMS costs 3-5x more than SMS. Only enable if sending images. |
| Alpha Sender ID | Use where supported (not US/Canada) | Alphanumeric sender IDs (e.g., "ACMECO") improve brand recognition in supported countries |

## WhatsApp Business API Patterns

### Template Message Rules

| Rule | Detail | What Happens If Violated |
|---|---|---|
| Business-initiated messages must use approved templates | Free-form messages only within 24-hour session window after user messages you | Message rejected (error 63016) |
| Templates must be pre-approved by Meta | Submit via Twilio Console or API; approval takes 1-48 hours | Template rejected or pending indefinitely |
| Template variables can't comprise >60% of message | Meta rejects templates that are mostly dynamic content | Template approval denied |
| Template language must match declared locale | If template is declared as `en_US`, content must be English | Approval denied or template suspended |
| Templates can't contain URL shorteners | bit.ly, tinyurl, etc. are prohibited in WhatsApp templates | Template approval denied |

### WhatsApp Session Window

```
User messages your business
  └─> 24-hour session window opens
       ├─> Free-form messages (any content) for 24 hours
       ├─> Each user message resets the 24-hour window
       └─> After 24 hours with no user message:
            └─> Must use approved template to re-initiate
                 └─> Template message opens new 24-hour window IF user replies
```

**Session window strategy**: End conversations with a question or prompt that encourages the user to reply, keeping the session window open. "Is there anything else I can help with?" extends the window by 24 hours when they reply "No."

### WhatsApp Message Types

| Type | Use Case | Requires Template | Cost Tier |
|---|---|---|---|
| Utility | Order confirmations, shipping updates, appointment reminders | Yes (if business-initiated) | Low ($0.005-0.03) |
| Authentication | OTP, login verification | Yes (if business-initiated) | Low ($0.005-0.03) |
| Marketing | Promotions, offers, re-engagement | Yes (always, even in session) | High ($0.02-0.08) |
| Service | Customer support responses | No (within session only) | Free (within session window) |

**Cost trap**: Marketing messages cost 3-10x more than utility messages on WhatsApp. If an order confirmation includes a promotional upsell, Meta classifies the ENTIRE message as marketing tier.

## Delivery Status Handling

### Status Callback Webhook

| Status | Meaning | Action |
|---|---|---|
| `queued` | Message accepted by Twilio, waiting to send | No action; normal flow |
| `sent` | Twilio sent to carrier (SMS) or provider (WhatsApp) | No action; doesn't confirm delivery |
| `delivered` | Carrier/provider confirmed delivery to device | Update UI to show delivered |
| `undelivered` | Carrier rejected or couldn't deliver | Check ErrorCode; retry if transient (30003), suppress if permanent (30005) |
| `failed` | Twilio couldn't process the message | Check ErrorCode; fix root cause (auth, format, permissions) |
| `read` | Recipient opened/read (WhatsApp only) | Update engagement metrics; WhatsApp read receipts can be disabled by user |

**Status webhook reliability**: SMS `delivered` status depends on carrier delivery receipts (DLR). Not all carriers return DLRs. US carriers return ~85% DLR rate. Absence of `delivered` doesn't mean undelivered.

### Retry Architecture for Messaging

| Error Category | Retry? | Strategy | Max Retries |
|---|---|---|---|
| Rate limit (429) | Yes | Exponential backoff starting at 1s | 5 |
| Carrier temporary failure (30003) | Yes | Wait 5 minutes, then retry once | 1 |
| Invalid number (21211, 30005) | No | Suppress number permanently | 0 |
| Opt-out (21610) | No | Update opt-out database; never retry | 0 |
| Carrier block (30004) | Investigate | Check A2P registration, message content | 0 until root cause fixed |
| WhatsApp session expired (63016) | No | Must send template message instead | 0 (change to template) |

## Number Management

### Number Type Selection

| Number Type | Use Case | Throughput | Cost | Registration |
|---|---|---|---|---|
| Local 10DLC | US/CA transactional + marketing SMS | 15-75 MPS (by trust score) | $1/mo + $0.0079/msg | A2P 10DLC required (2-4 weeks) |
| Toll-free | US/CA transactional SMS, customer support | 25 MPS | $2/mo + $0.0079/msg | Toll-free verification (1-2 weeks) |
| Short code | High-volume marketing, 2FA | 100+ MPS | $1,000+/mo | 6-12 week approval |
| Alphanumeric Sender ID | Brand recognition (UK, EU, AU -- not US/CA) | Varies by country | $0/mo (but per-message fees) | Varies; some countries require pre-registration |

**Number strategy**: Start with toll-free for fastest time-to-market. Migrate to 10DLC when volume justifies registration effort. Short codes only for >100k messages/month.

### A2P 10DLC Trust Score Impact

| Trust Score | MPS Limit | What Determines Score |
|---|---|---|
| 1 (Low) | 1 MPS | New brand, no website, low message volume history |
| 25-35 (Medium) | 15 MPS | Established brand, verified website, clean message history |
| 50-75 (High) | 40-75 MPS | Large brand, high volume history, zero compliance violations |

**Trust score gotcha**: Trust score is per-brand, not per-campaign. A compliance violation on one campaign affects ALL campaigns under that brand. One mistake can throttle your entire SMS operation.
