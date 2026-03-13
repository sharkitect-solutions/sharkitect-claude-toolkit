# Cold Email Infrastructure Setup Reference

## Domain Setup Checklist

### 1. Acquire Outreach Domain

- Register a domain similar to your primary business domain (e.g., `acme-team.com` for `acme.com`)
- Acceptable patterns: `brand-team.com`, `brand-hq.com`, `getbrand.com`, `trybrand.com`
- Avoid patterns that look disposable: random strings, numbers, hyphens stacked
- Register for 2+ years -- 1-year registrations correlate with throwaway spam domains
- Enable WHOIS privacy but ensure the domain resolves to a real landing page

### 2. Set Up Email Hosting

| Provider | Best For | Daily Safe Limit | Notes |
|---|---|---|---|
| Google Workspace | Most use cases | 50/account | Best deliverability baseline, strictest on abuse |
| Microsoft 365 | Enterprise-targeting campaigns | 80/account | Good deliverability, flags repetitive patterns faster |
| Zoho Mail | Budget option, secondary rotation | 40/account | Acceptable deliverability, less forgiving on warm-up |
| Amazon WorkMail | High-volume operations | 100/account | Requires more manual reputation management |

**Decision rule:** Google Workspace is the default. Only use alternatives for domain rotation at scale (3+ domains) or when targeting enterprises that may filter Google-origin cold email.

### 3. Configure Authentication (All Three Required)

#### SPF (Sender Policy Framework)
```
Type: TXT
Host: @
Value: v=spf1 include:_spf.google.com ~all
```
- For Google Workspace. Replace `_spf.google.com` with provider-specific value.
- Only ONE SPF record per domain. Multiple records = automatic fail.
- Use `~all` (softfail) not `-all` (hardfail) during warm-up. Switch to `-all` after 30 days.

#### DKIM (DomainKeys Identified Mail)
- Generated in email provider admin panel (Google Admin > Apps > Gmail > Authenticate Email)
- Creates a TXT record with a long cryptographic key
- Use 2048-bit key length (not 1024)
- Propagation takes 24-48 hours -- verify before sending

#### DMARC (Domain-based Message Authentication)
```
Type: TXT
Host: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomain.com
```
- Start with `p=none` (monitor only) during warm-up
- After 30 days with clean reports: move to `p=quarantine`
- After 60 days: move to `p=reject` for maximum protection
- The `rua` address receives aggregate reports -- review weekly

#### Verification Order
1. SPF first (immediate propagation, usually)
2. DKIM second (24-48 hour propagation)
3. DMARC third (depends on SPF + DKIM being active)
4. Verify all three pass using: `mail-tester.com` (send a test email, get a score)

### 4. Additional DNS Records

- **MX records:** Set by email provider automatically. Verify they exist.
- **Reverse DNS (PTR):** Usually handled by provider. Verify with `mxtoolbox.com/ReverseLookup.aspx`
- **Custom tracking domain:** If using a sending tool (Instantly, Smartlead, etc.), set up a custom tracking domain instead of shared tracking. Shared tracking domains carry reputation risk from other users.

## Warm-Up Ramp Schedule

### Phase 1: Passive Warm-Up (Days 1-7)

Send real, conversational emails to known contacts and warm-up services. No cold emails.

| Day | Emails/Account | Total (2 accounts) | Activity |
|---|---|---|---|
| 1-2 | 5 | 10 | Send to personal contacts, reply to their responses |
| 3-4 | 10 | 20 | Add warm-up service (Instantly, Warmbox, Mailreach) |
| 5-7 | 15 | 30 | Continue warm-up + sign up for newsletters to generate inbound |

### Phase 2: Mixed Warm-Up + Micro-Campaigns (Days 8-21)

Begin small cold campaigns alongside continued warm-up activity.

| Day | Warm-Up/Account | Cold/Account | Total/Account | Notes |
|---|---|---|---|---|
| 8-10 | 10 | 5 | 15 | First cold sends: best leads only, highest personalization |
| 11-14 | 10 | 10 | 20 | Monitor bounce rate obsessively -- pause if >3% |
| 15-17 | 8 | 17 | 25 | Shift ratio toward cold, maintain warm-up baseline |
| 18-21 | 5 | 25 | 30 | Warm-up becomes maintenance, cold is primary |

### Phase 3: Full Operations (Days 22-30+)

| Day | Warm-Up/Account | Cold/Account | Total/Account | Notes |
|---|---|---|---|---|
| 22-25 | 5 | 30 | 35 | Continue scaling cold if metrics are clean |
| 26-28 | 5 | 35 | 40 | Approaching ceiling -- watch bounce/complaint rates |
| 29-30 | 5 | 40-45 | 45-50 | Full capacity. Never exceed 50 total/account on Google |

### Warm-Up Rules

- **Never skip warm-up to "save time."** Skipping creates problems that take 3-5x longer to fix than the warm-up itself.
- **If any day shows bounce rate >3%:** Pause cold sends for 48 hours, audit list quality, resume at 50% volume.
- **If spam complaints appear:** Pause all cold sends for 72 hours. Review copy and targeting. Resume at 25% volume.
- **Keep warm-up running indefinitely** at 5-10/account/day even during full operations. Warm-up emails generate positive engagement signals that support cold email deliverability.
- **Weekend sends:** Reduce volume by 50% on weekends. Low weekend engagement rates can drag down sender reputation.

## Sending Account Architecture

### Single Account (Simplest)
- **Use when:** <25 cold emails/day, single niche, testing phase
- **Setup:** One domain, one email account, one sending tool
- **Risk:** All reputation on one account. If it gets flagged, everything stops.

### Dual Account (Recommended Default)
- **Use when:** 25-100 cold emails/day, multiple niches
- **Setup:** One domain, two email accounts (e.g., firstname@, team@), round-robin assignment
- **Benefit:** Spreads reputation risk, doubles effective capacity, enables A/B testing by account

### Multi-Domain Rotation (Scale Operations)
- **Use when:** 100+ cold emails/day, high-volume campaigns
- **Setup:** 2-4 domains, 2 accounts per domain, automated rotation
- **Each domain** needs independent authentication (SPF/DKIM/DMARC) and warm-up
- **Rotation logic:** Assign leads to domains at send time, not at import. Distribute evenly.
- **Recovery benefit:** If one domain gets flagged, others continue operating

### Account Naming Conventions
- Use real-sounding names: `sarah@`, `michael@`, not `sales@` or `outreach@`
- Functional addresses (`team@`, `solutions@`) are acceptable as secondary accounts
- Never use `noreply@` for cold email -- it signals one-way broadcast

## Deliverability Monitoring

### Daily Checks (During Warm-Up)
- Bounce rate: must be <3%
- Spam complaint count: must be 0
- Warm-up tool engagement score (if using one)
- Google Postmaster Tools: domain reputation, spam rate

### Weekly Checks (During Operations)
- Google Postmaster Tools dashboard: domain reputation trend
- Inbox placement test: send to seed accounts across Gmail, Outlook, Yahoo
- Bounce rate trend: should stay <2%, investigate any upward movement
- Blacklist check: `mxtoolbox.com/blacklists.aspx`

### Email Verification Pipeline (Pre-Send)

| Stage | Tool Type | What It Checks | Action on Fail |
|---|---|---|---|
| 1. MX Check | Free (DNS lookup) | Domain has mail server | Remove from list |
| 2. API Verification | Hunter, NeverBounce, MillionVerifier | Mailbox exists | Remove if invalid, flag if risky |
| 3. Catch-All Detection | Verification API | Domain accepts all addresses | Flag as risky, send only if high-value lead |

- **Valid:** Send normally
- **Risky:** Send only in micro-campaigns (<25), monitor bounce individually
- **Invalid:** Never send. Remove immediately.
- **Catch-all:** Treat as risky. Many catch-all addresses are valid but some are traps.

### Recovery Protocol (When Reputation Drops)

1. **Stop all cold sends immediately.** Do not reduce volume -- stop completely.
2. **Diagnose the cause:** Check bounce rate, spam complaints, blacklists, authentication status.
3. **Fix the root cause:** Bad list = reverify. Authentication issue = fix DNS. Content trigger = rewrite copy.
4. **Pause for 7-14 days** while warm-up continues at reduced volume (5-10/day).
5. **Restart at 25% of previous volume** and ramp back up over 2 weeks.
6. **If domain is permanently flagged** (reputation stays "Bad" in Postmaster Tools after 30 days): retire domain, start fresh with a new one. Do not try to rehabilitate a dead domain.
