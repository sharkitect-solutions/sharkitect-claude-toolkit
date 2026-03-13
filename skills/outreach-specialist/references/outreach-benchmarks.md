# Outreach Benchmarks Reference

## Reply Rate Benchmarks by Segment

### By Industry

| Industry | Expected Reply Rate | Notes |
|---|---|---|
| SaaS / Technology | 3-6% | Highly saturated inbox, requires Level 3+ personalization |
| Professional Services | 5-8% | Decision makers read email closely, quality over volume |
| Home Services (HVAC, plumbing, etc.) | 4-7% | Owners are busy; short, direct emails perform best |
| Real Estate | 6-10% | Highly email-responsive, fast reply cycles |
| Healthcare | 2-4% | Compliance concerns slow decision-making, longer cycles |
| Construction / Trades | 3-5% | Less email-responsive, phone follow-up often needed |
| E-commerce / Retail | 4-7% | High email volume tolerance, seasonal sensitivity |
| Financial Services | 3-5% | Compliance-heavy, formal tone expected |
| Education | 4-6% | Budget cycles dominate timing, seasonal windows |
| Manufacturing | 2-4% | Longer sales cycles, relationship-driven decisions |

### By Company Size

| Company Size | Expected Reply Rate | Personalization Minimum |
|---|---|---|
| 1-10 employees | 5-9% | Level 2 (owner reads everything) |
| 11-50 employees | 4-7% | Level 2-3 (delegated but attentive) |
| 51-200 employees | 3-5% | Level 3 (gatekeepers filter) |
| 201-1000 employees | 2-4% | Level 3-4 (buried in email) |
| 1000+ employees | 1-3% | Level 4 (noise is extreme) |

### By Decision-Maker Role Level

| Role Level | Expected Reply Rate | Best Approach |
|---|---|---|
| C-Suite (CEO, CTO, CFO) | 2-4% | Ultra-short, outcome-focused, sent early morning |
| VP / Director | 3-6% | Business outcome framing, peer social proof |
| Manager | 4-8% | Operational efficiency framing, tactical proof |
| Individual Contributor | 5-10% | Tool/process framing, ease-of-use messaging |

## Open Rate Expectations by Warm-Up Stage

| Stage | Expected Open Rate | If Below This | Action |
|---|---|---|---|
| Week 1-2 (early warm-up) | 30-40% | <20% | Check authentication, verify subject lines aren't triggering filters |
| Week 3-4 (late warm-up) | 40-55% | <30% | Check inbox placement with seed tests, review sending patterns |
| Month 2+ (established) | 45-65% | <35% | Test subject lines, check if domain reputation has dropped |
| Mature (3+ months clean) | 50-70% | <40% | Likely a targeting problem -- are you reaching the right people? |

**Important:** Open rate tracking requires a tracking pixel, which itself reduces deliverability by ~5%. Consider whether tracking opens is worth the tradeoff, especially during warm-up.

## Conversion Metrics: Reply to Close

### Reply to Meeting Conversion

| Reply Type | % of Replies | Meeting Conversion |
|---|---|---|
| Positive / interested | 30-50% | 60-80% (should book most of these) |
| Neutral / curious | 20-30% | 20-40% (need nurturing) |
| Objection (timing, budget) | 15-25% | 5-15% (long-term nurture) |
| Negative / unsubscribe | 10-20% | 0% (honor immediately) |

### Meeting to Close by Deal Size

| Deal Size (ACV) | Meetings to Close | Avg Cycle | Notes |
|---|---|---|---|
| <$1K | 1-2 | 1-2 weeks | Often closes on first call |
| $1K-5K | 2-3 | 2-4 weeks | Needs proof + proposal |
| $5K-25K | 3-5 | 1-3 months | Multiple stakeholders, formal evaluation |
| $25K-100K | 5-8 | 3-6 months | Committee decisions, procurement involved |
| $100K+ | 8-15 | 6-12 months | Enterprise sales cycle, champion required |

### Full Funnel Math Example

For a $5K ACV service targeting SMB professional services:
- **1,000 emails sent** (across all campaign touches)
- **550 opened** (55% open rate, established domain)
- **50 replies** (5% reply rate)
- **20 positive replies** (40% positive)
- **12 meetings booked** (60% of positive replies)
- **3 closed deals** (25% close rate at this ACV)
- **$15K revenue** from 1,000 email sends
- **Cost per acquisition:** ~$5-15/deal (email tooling + time)

## Deliverability Health Indicators

### Green (Healthy)
| Metric | Healthy Range |
|---|---|
| Bounce rate | <2% |
| Spam complaint rate | <0.05% |
| Open rate | >45% |
| Reply rate | >3% |
| Google Postmaster reputation | "High" |
| Blacklist status | Not listed on any major list |

### Yellow (Watch Closely)
| Metric | Warning Range | Action |
|---|---|---|
| Bounce rate | 2-4% | Tighten verification, check list source |
| Spam complaint rate | 0.05-0.1% | Review copy for aggressive language |
| Open rate | 25-45% | Test subject lines, check inbox placement |
| Reply rate | 1-3% | Review targeting and personalization depth |
| Google Postmaster reputation | "Medium" | Reduce volume 25%, increase warm-up ratio |

### Red (Emergency)
| Metric | Critical Range | Action |
|---|---|---|
| Bounce rate | >4% | **STOP all sends.** Audit entire list. Do not resume until verified. |
| Spam complaint rate | >0.1% | **STOP all sends.** Review all copy. Pause 72 hours minimum. |
| Open rate | <25% | Check if emails are landing in spam. Run seed test. |
| Reply rate | <1% for 2+ weeks | Overhaul targeting, copy, AND timing simultaneously. |
| Google Postmaster reputation | "Low" or "Bad" | **STOP sends. Begin recovery protocol** (see infrastructure-setup.md). |
| Listed on blacklist | Any major list (Spamhaus, Barracuda, etc.) | Submit delisting request, pause sends until resolved. |

## Campaign Diagnostic Decision Tree

When metrics are off, diagnose in this order:

### Emails not getting opened (open rate <25%)
1. **Check inbox placement first.** Send test emails to seed accounts (Gmail, Outlook, Yahoo). If landing in spam, this is a deliverability problem, not a subject line problem.
2. **If inbox placement is fine:** Test subject lines. Run A/B with 2-4 word internal-memo style vs. current.
3. **If subject lines tested:** Check send timing. Test morning (8-10 AM) vs. early afternoon (1-2 PM) in recipient's timezone.
4. **If all above tested:** The list may not be reachable via email. Consider if this audience is phone-first.

### Emails opened but no replies (open rate >40%, reply rate <2%)
1. **Check email length.** If >120 words, cut. Measure again.
2. **Check CTA clarity.** Is there exactly one ask? Is it low-commitment?
3. **Check personalization depth.** Level 1 (name/company only) rarely works beyond SMB. Increase depth.
4. **Check offer-market fit.** The offer may not resonate with this audience. Test a different angle.
5. **Check reading level.** Paste into Hemingway App. If above 6th grade, simplify.

### Getting replies but not meetings (reply rate >5%, meeting rate <30% of positive replies)
1. **Response speed.** Reply within 2 hours during business hours. After 24 hours, meeting conversion drops 50%.
2. **Reply content.** First reply should include ONE scheduling link and ONE sentence of context. Not a pitch.
3. **Qualification mismatch.** Replies may be from non-decision-makers. Check if targeting is reaching the right titles.

### Getting meetings but not closing (meeting rate fine, close rate <15%)
1. This is no longer an outreach problem -- it's a sales process problem.
2. Common causes: weak discovery call, no clear next steps, pricing mismatch, wrong decision-maker in meeting.
3. Outreach optimization cannot fix post-meeting conversion. Escalate to sales process review.
