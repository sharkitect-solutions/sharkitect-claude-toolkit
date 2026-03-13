---
name: twilio-communications
description: "Use when building SMS messaging, voice calls, WhatsApp Business API, or phone verification features with Twilio. Also use when the user mentions Twilio, send SMS, text message, voice call IVR, phone verification, 2FA/OTP via phone, or TwiML. NEVER use for email sending (use email-systems), push notifications, non-Twilio communication APIs, or general authentication without phone verification."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Twilio Communications

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Channel selection, compliance requirements, rate limits, error handling, webhook security, cost control, TwiML reference | Always (auto-loaded) |
| messaging-patterns-guide.md | SMS segment optimization (GSM-7 vs UCS-2), WhatsApp Business API templates/sessions, delivery status handling, number management, A2P 10DLC trust scores | When implementing SMS/MMS/WhatsApp messaging features or optimizing message delivery |
| voice-ivr-patterns.md | IVR architecture (auto-attendant, speech recognition, queue-based), TwiML deep patterns, conference calls, call recording compliance, voice quality troubleshooting, STIR/SHAKEN | When building voice features, IVR flows, or troubleshooting call quality issues |
| verification-security-guide.md | Verify API channels and gotchas, fraud prevention (SMS pumping, toll fraud, SIM swap), credential security, webhook signature validation, MFA architecture | When implementing phone verification, 2FA, or securing Twilio integrations |

## Scope Boundary

| This Skill Handles | Defer To |
|---|---|
| SMS, voice, WhatsApp messaging with Twilio | email-systems (email infrastructure and deliverability) |
| Phone verification and 2FA via Twilio Verify | security-best-practices (general authentication patterns) |
| TwiML IVR design and voice call routing | voice-agents (AI-powered voice conversation agents) |
| A2P 10DLC registration and carrier compliance | data-privacy-compliance (general GDPR/privacy compliance) |
| Twilio webhook security and credential management | senior-backend (general API security patterns) |
| Twilio-specific cost optimization | app-builder (full application architecture decisions) |

Builds SMS, voice, WhatsApp, and phone verification features with Twilio, with critical focus on compliance requirements, rate limits, error handling, and cost control.

## Channel Selection Guide

Choose the right Twilio product for the communication need.

| Need | Twilio Product | Key Constraint | Cost Model |
|---|---|---|---|
| Transactional SMS (OTP, alerts, confirmations) | Messaging API + Messaging Service | A2P 10DLC registration required for US; 160-char segments | Per segment sent |
| Marketing SMS (promotions, campaigns) | Messaging API + Messaging Service | Requires explicit opt-in; TCPA compliance mandatory | Per segment + carrier fees |
| Phone verification / 2FA | Verify API | Use Verify, never DIY OTP -- built-in fraud prevention saved $82M+ blocking 747M attempts | Per verification attempt |
| Voice IVR / phone menus | Programmable Voice + TwiML | Stateless -- each webhook is independent; use URL params or session store for state | Per minute |
| Voice calls (connect users) | Programmable Voice | Use `<Dial>` verb; handle busy/no-answer with fallback | Per minute both legs |
| WhatsApp notifications | WhatsApp Business API | Must use pre-approved templates for business-initiated messages; 24-hour session window for free-form replies | Per message + Meta fees |
| Multi-channel (SMS + Voice + Email fallback) | Verify API with channel routing | Verify handles fallback automatically; configure channel priority | Per verification |

## Compliance Requirements

Non-compliance leads to number suspension, fines, or account termination. These are not optional.

| Requirement | Applies To | What You Must Do |
|---|---|---|
| A2P 10DLC registration | All US SMS (application-to-person) | Register brand and campaign with The Campaign Registry (TCR) via Twilio Console before sending any messages |
| TCPA compliance | US SMS and voice | Obtain prior express written consent before sending; honor STOP/opt-out immediately; maintain opt-out records |
| GDPR | EU recipients | Lawful basis for processing phone numbers; honor deletion requests; data processing agreement with Twilio |
| Opt-out handling | All SMS | Respond to STOP, UNSUBSCRIBE, CANCEL automatically; remove from send lists within 10 days; track opt-out status in your database |
| Sender ID registration | Some countries (UK, Australia, India) | Register alphanumeric sender IDs before sending; unregistered messages are blocked |

**Critical**: Failing to register for A2P 10DLC results in message filtering rates of 80%+ for US numbers. Registration takes 2-4 weeks -- start before development.

## Rate Limits and Throttling

| Product | Default Limit | How to Handle |
|---|---|---|
| SMS (10DLC registered) | Varies by trust score: 15-75 MPS per campaign | Queue messages; implement exponential backoff on 429 errors |
| SMS (toll-free) | 25 MPS | Use Messaging Service with multiple numbers for higher throughput |
| SMS (short code) | 100+ MPS | Apply for short code (6-12 week approval); highest throughput |
| Voice (outbound) | 1 CPS (calls per second) per number | Use multiple numbers via Connection Policies for higher concurrency |
| Verify | 5 verification attempts per phone number per 10 minutes | Implement cooldown in your UI; show "try again in X minutes" |
| WhatsApp | 80 MPS per sender | Queue messages; monitor 429 responses |

**Application-level throttling**: For production volume (>1k messages/day), implement your own rate limiting in addition to Twilio's. For low-volume applications (<100 messages/day), handling 429 errors with exponential backoff is sufficient without a dedicated rate limiter. At medium volume (100-1k/day), a simple sliding window counter in Redis or memory is adequate -- no need for a token bucket.

## Error Handling Strategy

| Error Code | Meaning | Action |
|---|---|---|
| 20003 | Authentication failure | Check ACCOUNT_SID and AUTH_TOKEN; rotate if compromised |
| 20429 | Too many requests | Implement exponential backoff: wait 1s, 2s, 4s, 8s, max 60s |
| 21211 | Invalid phone number | Validate E.164 format before API call; use Lookup API for verification |
| 21408 | Permission not enabled | Enable the required permission in Console (e.g., international SMS) |
| 21610 | Recipient unsubscribed | Respect opt-out; do NOT retry; update your opt-out database |
| 21614 | Invalid mobile number | Not a mobile number; cannot receive SMS -- fall back to voice |
| 30003 | Unreachable destination | Retry once after 5 minutes; if still fails, try alternate channel |
| 30004 | Message blocked by carrier | Check A2P 10DLC registration; review message content for spam triggers |
| 30005 | Unknown destination | Number doesn't exist; remove from contact list |
| 30006 | Landline or unreachable | Cannot receive SMS; fall back to voice channel |
| 63016 | WhatsApp session expired | 24-hour window closed; must use approved template to re-initiate |

**Error handling rule**: Validate phone numbers with E.164 regex (`^\+[1-9]\d{1,14}$`) before any API call. For high-value flows (OTP, payment confirmations), also use the Lookup API for real-time carrier validation. For bulk messaging, regex-only validation is sufficient -- Lookup API costs $0.01/call.

## Cost Quick Reference

| Product | Unit | Cost Range | Watch Out For |
|---|---|---|---|
| SMS (US) | Per segment | $0.0079 outbound, $0.0075 inbound | UCS-2 encoding triples segment count |
| SMS (international) | Per segment | $0.01-$0.14 depending on country | Check country-specific pricing before bulk sends |
| MMS (US) | Per message | $0.02 outbound | 3-5x more than SMS; disable MMS fallback unless needed |
| Voice (US) | Per minute | $0.014 outbound, $0.0085 inbound | Both legs billed on `<Dial>` calls |
| WhatsApp (utility) | Per message | $0.005-$0.03 by country | Cheapest for transactional outside US |
| WhatsApp (marketing) | Per message | $0.02-$0.08 by country | 3-10x more than utility; avoid promo in transactional |
| Verify | Per attempt | $0.05 (SMS), $0.10 (voice), $0.01 (email) | Rapid retries waste money; implement UI cooldown |
| Phone number (US local) | Per month | $1.15 | Audit and release unused numbers monthly |
| Lookup API | Per lookup | $0.01 | Only use on high-value flows; skip for bulk |

## Webhook Security

Every Twilio webhook endpoint MUST validate the `X-Twilio-Signature` header to prevent request forgery.

| Security Measure | Implementation |
|---|---|
| Signature validation | Use `RequestValidator` from the Twilio SDK; compare against `X-Twilio-Signature` header |
| HTTPS required | Twilio sends webhooks over HTTPS only; your endpoint must have a valid TLS certificate |
| URL consistency | The URL you configure in Console must exactly match the URL seen by your server (including protocol, host, port, path) |
| Behind a proxy | If behind a reverse proxy, ensure `X-Forwarded-Proto` and `X-Forwarded-Host` are forwarded correctly for signature validation |

**Critical**: Skipping signature validation allows anyone to trigger your webhook endpoints by sending fake requests. This is an exploitable vulnerability for any endpoint that processes payments, sends messages, or modifies data.

## Cost Control Patterns

| Cost Driver | Mitigation |
|---|---|
| Long SMS (>160 chars) | Count segments before sending: `segments = ceil(len(body) / 160)`. Each segment is billed separately. Optimize message copy to fit in 1 segment |
| International SMS | Use country-specific pricing lookup before sending; some countries cost 10x US rates. Consider WhatsApp for international (cheaper) |
| Voice minutes | Set `timeout` on `<Dial>` to avoid billing for unanswered calls. Use `<Gather>` with short timeout instead of `<Pause>` |
| Verify API | Each attempt costs; implement UI cooldown to prevent rapid retries. Use silent network auth (SNA) where available for zero-cost verification |
| Unused numbers | Audit monthly; release numbers not actively used -- each costs $1-2/month |

## TwiML Quick Reference

| Verb | Purpose | Key Attributes |
|---|---|---|
| `<Say>` | Text-to-speech | `voice` (alice, man, woman), `language`, `loop` |
| `<Play>` | Play audio URL | `loop`, `digits` (DTMF tones) |
| `<Gather>` | Collect keypad/speech input | `numDigits`, `action` (webhook URL), `timeout`, `input` (dtmf/speech) |
| `<Dial>` | Connect to another number | `timeout`, `callerId`, `record`, `action` |
| `<Record>` | Record caller | `maxLength`, `action`, `transcribe` |
| `<Redirect>` | Move to another TwiML endpoint | URL of next TwiML document |
| `<Hangup>` | End the call | -- |

**Stateless rule**: Twilio makes a new HTTP request for each TwiML interaction. Your application must manage state externally (database, session store, URL parameters) -- there is no built-in session between TwiML requests.

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "I'll build my own OTP system instead of using Verify" | DIY OTP requires you to handle code generation, expiration, rate limiting, and fraud prevention; Twilio Verify handles all of this and blocked 747M fraudulent attempts -- your custom solution won't match that |
| "A2P 10DLC registration can wait until we scale" | Unregistered messages are filtered at 80%+ rates for US numbers; registration takes 2-4 weeks, so delaying means your first users get unreliable SMS |
| "We don't need to validate webhook signatures in development" | Development patterns become production patterns; skipping validation in dev means it's often forgotten in production, creating an exploitable endpoint |
| "SMS is always the right channel for notifications" | SMS costs per message and has regulatory overhead; for users with your app installed, push notifications are free and have higher engagement -- use SMS only when push isn't available |
| "Phone number format validation is unnecessary -- Twilio will reject invalid numbers" | Each invalid API call costs latency and counts against rate limits; validating E.164 format client-side prevents wasted calls and improves user experience |
| "Opt-out handling is a nice-to-have" | TCPA violations carry fines of $500-$1,500 per message; opt-out handling is a legal requirement, not a feature |

## Red Flags

- Sending SMS to US numbers without A2P 10DLC registration -- messages will be filtered by carriers
- No webhook signature validation on any Twilio endpoint
- Hardcoded ACCOUNT_SID or AUTH_TOKEN in source code instead of environment variables
- Building custom OTP instead of using Twilio Verify API
- No opt-out handling -- STOP messages not processed or not removing users from send lists
- Sending SMS without E.164 phone number validation
- No rate limiting in application code -- relying entirely on Twilio's 429 responses
- WhatsApp business-initiated messages sent without approved templates (will be rejected)

## NEVER

- Hardcode Twilio credentials in source code or commit them to version control -- use environment variables or a secrets manager; exposed credentials enable account takeover and toll fraud
- Skip A2P 10DLC registration for US SMS -- carrier filtering makes unregistered messages unreliable, and Twilio may suspend non-compliant accounts
- Store OTP codes in your own database when using Verify -- Twilio manages code lifecycle; storing codes creates a security liability with no benefit
- Ignore the 24-hour WhatsApp session window -- business-initiated messages outside the window must use pre-approved templates or they will be rejected
- Send SMS without checking opt-out status -- each message sent after opt-out is a potential TCPA violation with statutory damages
