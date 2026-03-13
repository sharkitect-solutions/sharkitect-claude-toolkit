# Verification & Security Implementation Guide

Load when implementing phone verification, 2FA/MFA with Twilio Verify, or securing Twilio-powered communication features.

## Verify API Implementation

### Channel Selection

| Channel | Delivery Method | Cost | Success Rate | Best For |
|---|---|---|---|---|
| SMS | Text message with code | $0.05/verification | 85-95% (varies by country) | Default channel; highest reach |
| Voice | Automated phone call reads code | $0.10/verification | 70-85% | Fallback when SMS fails; landlines |
| Email | Email with code | $0.01/verification | 90%+ (if email valid) | Cost-sensitive flows; pre-existing email |
| WhatsApp | WhatsApp message with code | $0.01-0.05/verification | 80-90% (where WhatsApp popular) | LATAM, India, SE Asia users |
| Silent Network Auth (SNA) | Carrier-level verification (no code) | $0.03/verification | 60-80% (carrier dependent) | Frictionless; no user action required |
| TOTP | Authenticator app (Google Auth, Authy) | $0/verification after setup | 99%+ | Ongoing 2FA; no per-verification cost |

**Channel fallback strategy**: SNA -> SMS -> Voice. Start with lowest-friction channel. If SNA isn't supported by carrier, fall to SMS. If SMS fails (landline, international issue), fall to voice. Configure this in Verify Service settings.

### Verify API Gotchas

| Gotcha | Impact | Fix |
|---|---|---|
| Rate limit: 5 attempts per phone number per 10 minutes | User locked out if they request too many codes | Implement UI countdown timer. Show "Try again in X:XX" after each attempt. Don't let users hammer the "resend" button. |
| Verification check is one-shot | Once you call `verification_check`, the code is consumed regardless of result | If check returns `status: "pending"` (wrong code), create a new verification. Don't re-check the same SID. |
| Code expiration: 10 minutes default | User gets distracted, code expires, frustration | Show expiry countdown in UI. Offer "Resend code" button that appears after 60 seconds. |
| SNA requires mobile data | SNA fails on WiFi-only devices | Detect network type client-side. If WiFi-only, skip SNA and go directly to SMS. |
| International SMS delivery varies wildly | Some countries have 60%+ SMS failure rates | Monitor per-country success rates. Add WhatsApp as fallback for countries with <80% SMS delivery. |
| Verification SID vs phone number | Each verification creates a new SID; you verify against the SID, not the phone number | Store the verification SID when you create it. Pass it back when checking. Don't create a new verification and check an old SID. |

### Fraud Prevention

| Threat | How It Works | Mitigation |
|---|---|---|
| SMS Pumping (Toll Fraud) | Attacker triggers thousands of SMS verifications to premium-rate numbers they control, earning revenue per SMS | Enable Twilio Fraud Guard: set country permissions, rate limits per IP, and spend alerts. Block high-risk country codes (e.g., some Pacific Island nations). |
| Verification bombing | Attacker enters victim's phone number repeatedly, flooding them with SMS/calls | Rate limit per phone number (Verify does this at 5/10min). Also rate limit per IP address in YOUR application. Add CAPTCHA before verification request. |
| Toll fraud on voice | Attacker calls premium-rate international numbers through your voice integration | Geo-restrict outbound calls in Twilio Console. Only enable countries you need. Set per-call spend limits. |
| Account takeover via SIM swap | Attacker convinces carrier to transfer victim's number to attacker's SIM | Don't use SMS as sole authentication factor. Pair with TOTP or security key. Monitor for delivery failures on previously-working numbers. |
| OTP interception | Attacker intercepts SMS via SS7 vulnerabilities or malware | Use SNA where available (carrier-level, not interceptable). For high-security flows, use TOTP instead of SMS. |

**Fraud Guard configuration**: Enable in Twilio Console -> Verify -> Fraud Guard. Set:
- Allowed country codes (whitelist only countries where you have users)
- Per-phone-number rate limit (default 5/10min is good)
- Per-IP rate limit (add in your application: 10 verification requests per IP per hour)
- Spend alert at $100/day (adjust to your expected volume)

### Implementation Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|---|---|---|
| Building custom OTP generation | You handle code generation, expiration, rate limiting, retry logic, and fraud prevention yourself | Use Twilio Verify API which handles all of this and has blocked 747M+ fraudulent attempts |
| Storing OTP codes in your database | Creates a security liability (codes in your DB can be stolen) and you must handle expiration | Verify manages code lifecycle. You only call `create` and `check`. Never see the code. |
| Sending OTP via regular Messaging API | No built-in rate limiting, no fraud prevention, no channel fallback, no analytics | Verify API includes all of these. The $0.05/verification cost is cheaper than building and maintaining it yourself. |
| Same OTP code for multiple attempts | Code reuse enables brute force attacks | Verify generates a new code each time. Previous codes are invalidated. |
| No lockout after failed attempts | Attacker can brute force a 6-digit code (1M combinations) | Verify locks after 5 failed checks. Add your own lockout in the application after 3 failed attempts. |
| Verification without phone number validation | Invalid numbers waste Verify API calls | Validate E.164 format before calling Verify. Use Lookup API for carrier validation on critical flows. |

## Credential Security

### API Key Hierarchy

| Credential Type | Scope | When to Use |
|---|---|---|
| Account SID + Auth Token | Full account access (everything) | Server-side only. Never in client code. Equivalent to root password. |
| API Key (Standard) | Limited to API operations you specify | Production applications. Create per-service. Rotate regularly. |
| API Key (Restricted) | Scoped to specific products (e.g., Messaging only) | Microservices that only need one Twilio product. Least privilege. |

**Key rotation procedure**:
1. Create new API key in Console
2. Deploy new key to application (environment variable or secrets manager)
3. Verify new key works in production
4. Revoke old key
5. Total time with two active keys: <24 hours

| Credential Rule | Why |
|---|---|
| Never commit credentials to version control | Git history is permanent. Even if removed later, the credential exists in history. Use `.env` + `.gitignore` or secrets manager. |
| Use API keys, not Account SID + Auth Token | Auth Token has unlimited access. API keys can be scoped and individually revoked. |
| Rotate API keys every 90 days | Limits exposure window if a key is compromised. Automated rotation via CI/CD. |
| Monitor for credential exposure | Use GitHub secret scanning, TruffleHog, or similar. Twilio also notifies you if your credentials appear in public repos. |
| Use separate credentials per environment | Dev, staging, production each get their own API keys. Never reuse across environments. |

## Webhook Security Deep Dive

### Signature Validation Implementation

| Step | Detail |
|---|---|
| 1. Get `X-Twilio-Signature` header | This is a Base64-encoded HMAC-SHA1 of the request URL + POST body parameters |
| 2. Construct the validation URL | Must exactly match what Twilio sees: protocol + host + port + path. If behind a proxy, use the public URL, not the internal one. |
| 3. Sort POST parameters alphabetically | Append key + value pairs to the URL string |
| 4. HMAC-SHA1 with your Auth Token | Use the Auth Token associated with the account that configured the webhook |
| 5. Compare Base64 output to header value | Must be exact match. Use constant-time comparison to prevent timing attacks. |

### Common Signature Validation Failures

| Failure | Cause | Fix |
|---|---|---|
| Signature never matches | URL mismatch: Twilio sees `https://example.com/webhook` but your server sees `http://localhost:3000/webhook` | Reconstruct URL from the public-facing perspective. Set `X-Forwarded-Proto` and `X-Forwarded-Host` in your reverse proxy. |
| Works locally, fails in production | Trailing slash mismatch or port number included/excluded | Ensure Console webhook URL exactly matches what your validation code constructs. No trailing slash difference. |
| Intermittent failures | Load balancer changing request body encoding | Validate against raw body, not parsed body. Some frameworks modify POST parameter encoding. |
| Signature valid but request is spoofed | Auth Token leaked | Rotate Auth Token immediately. Use API key-based signature validation instead. |

### IP Allowlisting (Defense in Depth)

Twilio publishes its IP ranges for webhook origins. Adding IP allowlisting alongside signature validation provides defense in depth.

| Region | IP Ranges | Documentation |
|---|---|---|
| North America | Published at twilio.com/docs/sip-trunking/ip-addresses | Changes periodically -- use Twilio's notification service for updates |
| Europe | Different ranges from NA | Same documentation page |
| Asia Pacific | Different ranges from NA/EU | Same documentation page |

**IP allowlisting gotcha**: Twilio IP ranges change. Don't hardcode them. Fetch and cache them, or use Twilio's published list with automated updates. IP allowlisting is a SUPPLEMENT to signature validation, never a replacement.

## Multi-Factor Authentication Architecture

### MFA Decision Matrix

| Signal | Recommended MFA | Why |
|---|---|---|
| Standard user login | SMS OTP (Verify) | Widely supported, familiar UX. Adequate for most applications. |
| High-value transaction (>$500) | SMS OTP + in-app confirmation | Step-up authentication: additional factor for high-risk actions |
| Admin/privileged access | TOTP (authenticator app) | Not vulnerable to SIM swap. No per-verification cost. More secure. |
| Passwordless login | SNA (if mobile) -> SMS fallback | Zero-friction primary auth. SNA verifies device possession at carrier level. |
| Regulatory requirement (PSD2, HIPAA) | TOTP or hardware key. SMS insufficient. | PSD2 (banking) explicitly requires a "possession" factor that SMS may not satisfy. NIST 800-63 deprecates SMS for high-assurance scenarios. |

### Step-Up Authentication Flow

```
Normal login: username + password
  -> Session established at Level 1

User attempts high-value action (e.g., transfer $1,000):
  -> Application requires Level 2 authentication
  -> Trigger Verify SMS/Voice/TOTP
  -> User enters code
  -> Session elevated to Level 2 for 15 minutes
  -> After 15 minutes, session drops back to Level 1

User attempts admin action:
  -> Application requires Level 3
  -> Trigger TOTP + explicit confirmation
  -> Session elevated to Level 3 for 5 minutes
```

| Level | Elevation Method | Duration | Actions Allowed |
|---|---|---|---|
| 1 (Base) | Username + password | Session lifetime | View data, update profile, low-value actions |
| 2 (Elevated) | SMS/Voice OTP | 15 minutes | Transfers, purchases, settings changes |
| 3 (Privileged) | TOTP + confirmation | 5 minutes | Admin actions, API key management, account deletion |

**Step-up gotcha**: Don't cache the elevated level in a JWT without expiration. Use a server-side session with timestamp, and re-check on every privileged request. JWTs with long-lived elevated claims survive logout.
