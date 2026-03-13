# Email Monitoring & Troubleshooting Guide

Load when debugging deliverability issues, investigating email failures, or setting up production monitoring for email infrastructure.

## Deliverability Investigation Procedure

When emails aren't reaching inboxes, follow this procedure in order. Stop at the first identified root cause.

### Step 1: DNS Authentication Check

| Check | Tool | Expected Result | If Failing |
|---|---|---|---|
| SPF record | `dig TXT yourdomain.com` or mxtoolbox.com/spf | `v=spf1 include:<esp> ~all` with <10 lookups | Fix SPF record. Count lookups (nested includes count). Flatten if >10. |
| DKIM record | `dig TXT selector._domainkey.yourdomain.com` | Valid DKIM public key | Verify selector name matches ESP config. Check for DNS propagation (48h). |
| DMARC record | `dig TXT _dmarc.yourdomain.com` | `v=DMARC1; p=none/quarantine/reject; rua=...` | Add DMARC record. Start at p=none. |
| SPF alignment | Check DMARC aggregate reports | Return-Path domain matches From domain | Update envelope sender (Return-Path) to match From domain |
| DKIM alignment | Check DMARC aggregate reports | DKIM d= domain matches From domain | Configure DKIM signing domain to match From domain |
| Reverse DNS | `dig -x <sending-ip>` | PTR record resolves to hostname that forward-resolves back | Contact ESP or hosting provider to set PTR record |

### Step 2: Reputation Check

| Check | Tool | What to Look For |
|---|---|---|
| IP reputation | Google Postmaster Tools | Bad/Low reputation = throttled at Gmail. Check daily. |
| Domain reputation | Google Postmaster Tools | Domain reputation matters more than IP for shared IPs |
| Blacklist status | mxtoolbox.com/blacklists | Check all major lists: Spamhaus (SBL, XBL, PBL), Barracuda, SpamCop |
| Microsoft reputation | SNDS (Smart Network Data Services) | Red status = Microsoft is filtering. Apply to JMRP for feedback. |
| Yahoo reputation | Yahoo Postmaster | Check for throttling or filtering signals |

### Step 3: Content Analysis

| Check | Tool | Passing Score |
|---|---|---|
| Spam score | mail-tester.com (send a test email) | 9/10 or higher |
| HTML validation | litmus.com or emailonacid.com | No rendering errors in top 10 clients |
| Link analysis | Check all links manually | No broken links, no URL shorteners, no HTTP-only links |
| Unsubscribe header | Check raw email headers | `List-Unsubscribe-Post: List-Unsubscribe=One-Click` present |
| Image-to-text ratio | Manual check | <60% images. Plain text version exists. |

### Step 4: Sending Pattern Analysis

| Check | Source | What to Look For |
|---|---|---|
| Volume spikes | ESP analytics | Sudden 5x+ volume increase triggers ISP throttling |
| Complaint rate trend | FBL reports, ESP dashboard | Rising complaint rate over 3+ days = content or list quality issue |
| Bounce rate trend | ESP dashboard | Rising bounce rate = list hygiene issue or ESP reputation issue |
| Engagement metrics | ESP analytics or Postmaster Tools | Declining open rates over weeks = reputation degradation |
| Sending time distribution | ESP logs | All volume in one burst vs spread over hours |

## ISP-Specific Troubleshooting

### Gmail

| Issue | Diagnosis | Fix |
|---|---|---|
| All email going to Promotions tab | Content triggers Gmail's categorization | Add personal elements: recipient's name in subject, conversational tone, fewer images. Or accept Promotions tab for marketing. |
| Emails going to spam for some recipients but not others | Per-user spam model. Some users' filters learned to distrust you. | Improve engagement. Ask users to move email to inbox and reply. Engagement signals retrain user-level filters. |
| 421 Too many connections | Sending too many simultaneous SMTP connections to Gmail | Limit to 10 concurrent connections per IP. Spread sending over time. |
| Temporary 4xx errors during warm-up | Gmail throttling new IP/domain | Reduce daily volume. Strictly follow warm-up schedule. Do not retry aggressively (it looks like spam). |
| Open tracking shows 0% opens | Gmail image proxy caching | Gmail pre-fetches images. Open tracking is unreliable for Gmail. Use click tracking instead. |

### Microsoft (Outlook, Hotmail, Live)

| Issue | Diagnosis | Fix |
|---|---|---|
| Email going to Junk for all Outlook recipients | Domain or IP on Microsoft's internal filter | Apply to JMRP (Junk Mail Reporting Program). Submit form at sender.office.com. Response takes 2-5 business days. |
| HTML rendering broken | Outlook uses Word rendering engine, not browser | Table-based layout. Inline CSS. No flexbox, grid, or advanced CSS. Test with Litmus. |
| Images blocked by default | Outlook blocks external images until user clicks "Download Images" | Always include alt text. Don't rely on images for key content. Use ALT text that communicates the message. |
| EOP (Exchange Online Protection) blocking | Enterprise Outlook uses additional filtering | Contact recipient's IT admin. Provide your SPF/DKIM/DMARC records for whitelisting. |

### Yahoo / AOL (now combined)

| Issue | Diagnosis | Fix |
|---|---|---|
| Temporary deferrals (421) | Yahoo uses aggressive rate limiting for unknown senders | Slow down. Spread sends over hours. Do not retry immediately -- wait 60+ minutes. |
| Bulk email rejected | Yahoo requires DMARC + List-Unsubscribe for bulk senders (>5k/day) | Implement DMARC at p=quarantine or stricter. Add List-Unsubscribe-Post header. |
| Poor deliverability despite clean metrics | Yahoo evaluates sender reputation at the domain level heavily | Focus on engagement. Remove unengaged subscribers (no open in 90 days). Yahoo rewards engagement more than other ISPs. |

## Production Monitoring Dashboard

### Tier 1 Metrics (Check Daily)

| Metric | Source | Healthy | Warning | Critical |
|---|---|---|---|---|
| Delivery rate | ESP dashboard | >98% | 95-98% | <95% |
| Bounce rate (hard) | ESP dashboard / webhooks | <0.5% | 0.5-2% | >2% |
| Complaint rate | FBL / Postmaster Tools | <0.05% | 0.05-0.1% | >0.1% |
| Open rate (relative to baseline) | ESP analytics | Within 10% of 30-day average | 10-25% below average | >25% below average |
| Click-through rate | ESP analytics | Within 15% of baseline | 15-30% below | >30% below |

### Tier 2 Metrics (Check Weekly)

| Metric | Source | What to Look For |
|---|---|---|
| Blacklist status | mxtoolbox.com / automated check | Any new listings |
| DMARC alignment rate | DMARC aggregate reports | Should be >95%. Below 90% means misconfigured sender. |
| SPF pass rate | DMARC reports | Should be >99%. Failures indicate unauthorized senders using your domain. |
| DKIM pass rate | DMARC reports | Should be >99%. Failures indicate key rotation issues or signature corruption. |
| Unsubscribe rate | ESP analytics | Stable or declining. Rising = content relevance issue. |

### Tier 3 Metrics (Check Monthly)

| Metric | Source | What to Look For |
|---|---|---|
| List growth rate | CRM / email platform | Net growth (new subscribers minus unsubscribes minus bounces) |
| Domain reputation trend | Google Postmaster Tools | Month-over-month trend. Gradual decline = slow reputation erosion. |
| ESP cost per email | ESP billing | Unexpected increases may indicate plan changes, overage charges, or duplicate sends |
| Template rendering errors | Email testing tool | New templates or updated templates may break in specific clients |

## Common Deliverability Myths

| Myth | Reality | What to Do Instead |
|---|---|---|
| "Avoiding spam trigger words improves deliverability" | Modern ISP filtering is ML-based, not keyword-based. "Free" in subject line doesn't trigger spam filters in 2024+. | Focus on authentication (SPF/DKIM/DMARC), reputation, and engagement. Content analysis is secondary. |
| "Sending from Gmail or Outlook accounts is fine for business" | Free email providers have strict rate limits and no authentication control. ISPs filter bulk from free domains. | Use a custom domain with proper DNS authentication. Even for small volume. |
| "High open rate means good deliverability" | Open tracking is unreliable: Apple Mail Privacy Protection pre-fetches all images (inflating opens), Gmail caches tracking pixels (deflating opens). | Use click-through rate and reply rate as engagement proxies. Open rate is directional only. |
| "Buying a 'clean' list is okay if it's verified" | Verified means "address exists." It does NOT mean "person consented." ISPs detect unsolicited email by engagement patterns, not just complaints. | Build your own list through opt-in forms. No shortcuts. |
| "Dedicated IP is always better than shared" | Dedicated IPs require volume to build reputation. <50k/mo on a dedicated IP often has WORSE deliverability than a well-managed shared pool. | Dedicated IP only if >100k/mo AND you can manage warm-up and reputation yourself. Otherwise, shared. |
| "Adding images makes emails more engaging" | Most email clients block images by default. Image-heavy emails are blank until user clicks "load images." | Lead with text content. Use images as supplements, not primary content. Always include alt text. |

## Alert Response Playbook

| Alert | Severity | First Response (within 15 min) | Investigation (within 1 hour) | Resolution |
|---|---|---|---|---|
| Bounce rate > 2% on single send | High | Pause current campaign. Check bounced addresses. | Identify pattern: all from one domain? Bad segment? Old list? | Suppress bounced addresses. Clean segment. Resume with clean list. |
| Complaint rate > 0.1% | Critical | Pause all marketing sends. Keep transactional running. | Check content of complained emails. Was it unsolicited? Off-topic? Too frequent? | Remove complainers. Review sending frequency. Resume at lower volume. |
| Blacklisted on Spamhaus | Critical | Identify which list (SBL, XBL, PBL). Stop all email from that IP. | SBL: your IP sent spam. XBL: your IP is compromised. PBL: cloud IP not meant for direct SMTP. | SBL: investigate and remediate, then request removal. XBL: scan for malware, fix, request removal. PBL: use ESP relay instead of direct SMTP. |
| ESP API returning 5xx | High | Check ESP status page. Switch to failover ESP if configured. | Wait for ESP resolution. Do not retry aggressively (will queue up backlog). | Once ESP recovers, replay queued messages. Monitor for duplicates. |
| Delivery rate drops below 95% | High | Check DNS authentication (SPF, DKIM, DMARC). Run Postmaster Tools. | Check reputation, blacklists, bounce rates, complaint rates. | Fix root cause (usually authentication or list hygiene). Recovery takes 1-2 weeks after fix. |
| DLQ depth growing | Medium | Check error reasons in DLQ messages. | Systemic (ESP down, auth expired) or per-email (bad addresses)? | Systemic: fix and replay. Per-email: suppress and discard. |
