---
name: email-systems
description: "Use when building transactional or marketing email infrastructure, configuring SPF/DKIM/DMARC, debugging deliverability issues, setting up email queues with retry logic, or designing email automation workflows. NEVER use for writing email copy (use email-composer or email-draft-polish), designing email templates visually, or non-email notification systems."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Email Systems

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | DNS authentication, architecture decisions, IP warm-up, bounce/complaint handling, common failures | Always (auto-loaded) |
| esp-provider-guide.md | Provider selection (SendGrid/SES/Postmark/Resend/Mailgun), provider-specific gotchas, migration checklist, cost comparison | When choosing an ESP, migrating between providers, or debugging provider-specific issues |
| queue-architecture-patterns.md | Email queue patterns (direct/priority/fan-out), retry strategy, idempotency keys, dead letter queues, rate limiting | When building email sending infrastructure or implementing retry logic |
| monitoring-troubleshooting-guide.md | Deliverability investigation procedure, ISP-specific troubleshooting (Gmail/Outlook/Yahoo), monitoring dashboard, alert response playbook | When debugging deliverability issues or setting up production monitoring |

## Scope Boundary

| This Skill Handles | Defer To |
|---|---|
| DNS authentication (SPF, DKIM, DMARC) setup and debugging | security-best-practices (general security review) |
| Email queue architecture and retry logic | senior-backend (general queue/messaging patterns) |
| ESP selection, configuration, and migration | app-builder (full application architecture) |
| Bounce handling, complaint processing, suppression lists | email-composer (writing email copy and tone) |
| IP warm-up and sender reputation management | marketing-demand-acquisition (campaign strategy) |
| Deliverability troubleshooting and ISP-specific fixes | email-sequence (email automation sequences) |

## Deliverability Checklist

DNS authentication -- all three required before sending any volume:

- [ ] **SPF**: `v=spf1 include:sendgrid.net ~all` -- list every authorized sending source; use `~all` (softfail) not `-all` until verified clean
- [ ] **DKIM**: 2048-bit key minimum; rotate keys every 6-12 months; verify selector is published and resolving
- [ ] **DMARC**: Start with `p=none; rua=mailto:dmarc@yourdomain.com` to collect reports; graduate to `p=quarantine` then `p=reject` after 30 days of clean reports
- [ ] **Reverse DNS (PTR)**: Sending IP must resolve to a hostname that forward-resolves back to the same IP
- [ ] **BIMI**: Optional but boosts inbox placement -- requires DMARC at `p=quarantine` or `p=reject` plus a Verified Mark Certificate (VMC)
- [ ] **MX records**: Ensure your sending domain has valid MX records even if it only sends and never receives
- [ ] **HTTPS on unsubscribe links**: Plain HTTP unsubscribe links are a spam signal in 2024+

## Email Architecture Decision Table

| Decision | Signals to Separate | Signals to Combine | Recommendation |
|----------|--------------------|--------------------|----------------|
| Transactional vs Marketing | Volume > 50k/mo, complaint rate delta > 0.05%, different sender domains | Small list (< 5k), single ESP, no deliverability issues yet | Separate at scale; start combined and split when complaints diverge |
| Shared IP vs Dedicated IP | Volume > 100k/mo, brand reputation critical, history of high complaints | Volume < 50k/mo, cold start, irregular sending cadence | Dedicated IP requires warm-up; shared IP inherits ESP pool reputation |
| Single ESP vs Multi-ESP | Single ESP acceptable for < 500k/mo; multi-ESP for failover above that | -- | Use one primary + one failover with DNS MX failover or webhook replay |
| Queue architecture | Any production workload | Simple scripts / one-off sends | Always queue: async processing, retry logic, deduplication by idempotency key |
| Subdomain for marketing | Marketing email to cold or opted-in lists | Transactional-only sending | Use `mail.yourdomain.com` for transactional, `news.yourdomain.com` for marketing to isolate reputation |

## IP Warm-up Schedule

New dedicated IPs start with zero reputation. ISPs throttle or block unknown IPs sending high volume. Follow this schedule without skipping days:

| Day | Max Emails | Notes |
|-----|-----------|-------|
| 1-2 | 200/day | Highest-engagement segment only (opened in last 30 days) |
| 3-4 | 500/day | Expand to 60-day openers |
| 5-7 | 1,000/day | Expand to 90-day openers |
| 8-10 | 2,500/day | Monitor bounce and complaint rates daily |
| 11-14 | 5,000/day | Pause if complaint rate exceeds 0.08% |
| 15-21 | 10,000/day | Full list segments with suppression applied |
| 22-28 | 25,000/day | Normal cadence if metrics are clean |
| 29+ | Full volume | Graduated by 2x/week max if volume > 100k |

Abort criteria: Stop warm-up and investigate if hard bounce rate > 2%, soft bounce rate > 5%, or complaint rate > 0.1% on any single day.

## Bounce and Complaint Handling

### Hard Bounces (permanent failure -- 5xx SMTP)
- Suppress immediately on first hard bounce -- never retry
- Remove from all lists within 24 hours
- Threshold: hard bounce rate above 2% triggers ISP blocks; target < 0.5%
- Common causes: invalid address, domain doesn't exist, mailbox doesn't exist

### Soft Bounces (temporary failure -- 4xx SMTP)
- Retry with exponential backoff: 5 min, 30 min, 2 hr, 6 hr, 24 hr
- After 5 consecutive soft bounces over 7 days: suppress address
- Distinguish by subtype: mailbox full (retry longer), graylisting (short retry), rate limit (back off sending rate)

### Spam Complaints (FBL reports)
- Google Postmaster, Yahoo CFL, Microsoft SNDS -- register for all three
- Suppress complainers immediately on FBL notification
- Complaint rate thresholds by ISP:
  - Google: > 0.10% triggers throttling; > 0.30% triggers blocking
  - Yahoo: > 0.10% triggers filtering
  - Microsoft: monitor via SNDS -- red status = immediate action needed
- Target complaint rate: < 0.05% for clean reputation

### Unsubscribes
- Process within 10 business days (CAN-SPAM); within 5 days recommended
- Honor List-Unsubscribe-Post header (RFC 8058) -- Gmail enforces this for bulk senders as of 2024
- One-click unsubscribe is now mandatory for Gmail/Yahoo bulk senders (> 5k/day)

## Common Failures Table

| Failure | Severity | Root Cause | Fix |
|---------|----------|-----------|-----|
| Emails landing in spam despite clean DNS | High | Reputation on shared IP pool | Switch to dedicated IP or move to reputable ESP; check content spam score with Mail-Tester |
| DKIM signature verification fails | Critical | Key mismatch, selector not propagated, or signing config error | Verify selector TXT record with `dig TXT selector._domainkey.yourdomain.com`; allow 48h DNS propagation |
| SPF permerror (too many lookups) | High | SPF record exceeds 10 DNS lookup limit | Flatten SPF using SPF flattening tools; consolidate include statements |
| DMARC failures despite valid SPF and DKIM | High | Alignment mismatch: From domain doesn't match SPF/DKIM domain | Ensure envelope-from (Return-Path) and DKIM d= tag align with the From header domain |
| Outlook renders HTML broken | Medium | Outlook uses Word rendering engine, not a browser engine | Use table-based layout, inline CSS only, avoid flexbox/grid, test with Litmus or Email on Acid |
| Bounce webhook not firing | High | Webhook endpoint returning non-2xx or timing out | ESPs retry webhooks 3-5 times then drop; ensure endpoint responds < 5s and returns 200; use a queue to accept and process async |
| Unsubscribe link broken after template update | Critical | URL parameter stripping or link rewriting by ESP | Use absolute URLs with tracking disabled on unsubscribe links; test post-deploy |
| New IP blocked by Spamhaus | Critical | IP on PBL (Policy Block List) -- common for cloud provider IPs | Check `mxtoolbox.com/blacklists`; request Spamhaus PBL removal for your IP; use ESP relay instead of direct SMTP from cloud VMs |

## Rationalization Table

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| Always use a queue for transactional email | Synchronous SMTP in request path adds 200-2000ms latency and fails the request if ESP is down | Queue adds infrastructure complexity; accept eventual delivery (usually < 5s) |
| Separate transactional and marketing IPs/subdomains | Marketing email generates more complaints; complaint rate from marketing bleeds into transactional deliverability | Costs more (two ESPs or two IP pools) but protects password resets and receipts |
| Start DMARC at p=none | Blind enforcement breaks legitimate email flows (forwarding, mailing lists, third-party senders) you didn't know existed | Delays enforcement; DMARC reports reveal all sending sources within 2-4 weeks |
| Suppress hard bounces permanently | Re-sending to invalid addresses is the fastest way to get blacklisted; ISPs treat persistent invalid address sends as spam behavior | Occasionally removes real addresses that had temporary issues; acceptable loss |
| Use 2048-bit DKIM keys minimum | 1024-bit keys are considered weak by modern standards and rejected by some ISPs | Slightly larger DNS record; no practical downside |
| Warm up dedicated IPs with engaged subscribers first | High engagement signals (opens, clicks) in the first days establish positive reputation with ISPs before volume increases | Means your best subscribers get slightly delayed sends during warm-up period |

## Red Flags

- No DMARC record at all -- authentication is incomplete and domain is spoofable
- Sending from a shared cloud VM IP (AWS EC2, GCP Compute, Azure VM) -- these IPs are pre-listed on Spamhaus PBL
- Complaint rate above 0.1% with no suppression automation in place
- No idempotency keys on transactional email sends -- duplicate sends on retry are a user trust issue
- Purchased or scraped email lists -- consent is not just ethical, it's the primary spam signal ISPs evaluate
- HTML-only emails with no plain text alternative -- both a spam signal and an accessibility failure
- Sending bulk volume from the same IP/subdomain as transactional email -- one campaign complaint spike blocks password resets
- Image-to-text ratio above 60% -- images are blocked by default in most clients; content-free emails trigger spam filters

## NEVER

- Never send to an address that hard-bounced without first verifying it through an email validation API
- Never skip the IP warm-up schedule regardless of urgency -- a blocked IP takes weeks to recover
- Never put the unsubscribe endpoint behind authentication -- CAN-SPAM requires one-click unsubscribe without login
- Never use URL shorteners in email links -- they are a top spam signal and obscure your domain reputation
- Never store ESP API keys in code or environment-committed files -- rotate on any potential exposure and use secrets management
