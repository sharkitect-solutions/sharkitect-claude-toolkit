# Channel Playbooks

Per-channel execution checklists. Use after the campaign framework has
determined which channels to deploy.

---

## Email Marketing

**Setup Requirements:**
- ESP configured with authentication (SPF, DKIM, DMARC)
- Suppression lists loaded (unsubscribes, bounces, do-not-contact)
- Segments built and validated (check segment size before launch)
- UTM parameters templated for all links
- Unsubscribe link and physical address in footer (CAN-SPAM / GDPR)

**Measurement Setup:**
- Open rate tracking (note: Apple MPP inflates opens -- use click rate as
  primary engagement metric for Apple Mail users)
- Click tracking with UTM parameters on every link
- Conversion tracking via landing page or CRM integration
- Deliverability monitoring (bounce rate, spam complaints)

**Optimization Cadence:**
- A/B test subject lines on every send (minimum 1,000 per variant)
- Review performance weekly: click rate, conversion rate, unsubscribe rate
- Re-segment quarterly based on engagement data
- Sunset disengaged contacts after 90 days of no clicks

**Expected Ramp Time:** 2-4 weeks for new lists. Warm IP/domain gradually --
start with most engaged segment, expand weekly.

**Benchmarks (B2B SaaS -- adjust for your industry):**
- Open rate: 20-30% (less meaningful post-Apple MPP)
- Click rate: 2-5%
- Unsubscribe rate: < 0.5% per send
- Bounce rate: < 2%

---

## Paid Search (Google/Bing Ads)

**Setup Requirements:**
- Conversion tracking pixel installed and tested
- Keyword research complete: branded, non-branded, competitor terms
- Negative keyword list built (prevents waste on irrelevant queries)
- Ad copy variants written (minimum 3 per ad group)
- Landing pages built with message match to ad copy

**Measurement Setup:**
- Conversion tracking at the CRM level (not just form submit)
- GCLID/MSCLKID passthrough to CRM for offline conversion import
- Call tracking if phone leads matter

**Optimization Cadence:**
- Daily: check spend pacing, pause runaway campaigns
- Weekly: search term report review, add negative keywords, adjust bids
- Bi-weekly: ad copy performance review, pause underperformers
- Monthly: full account audit, quality score review, landing page tests

**Expected Ramp Time:** 2-4 weeks to gather enough conversion data for
smart bidding. Start with manual CPC, switch to target CPA after 30+
conversions per campaign.

**Benchmarks:**
- CTR: 3-6% (search), < 1% (display)
- Conversion rate: 3-8% (search landing page)
- Quality score target: 7+ for core keywords

---

## Paid Social (LinkedIn, Meta, Twitter/X)

**Setup Requirements:**
- Tracking pixel installed on all conversion pages
- Custom audiences built (email lists, website visitors, lookalikes)
- Creative assets in platform-required formats and sizes
- Exclusion audiences set (existing customers, employees, competitors)

**Platform Selection Guide:**
- LinkedIn: B2B, targeting by job title/company/industry. Expensive CPCs ($5-15)
  but high intent. Best for demand gen and account-based marketing.
- Meta (Facebook/Instagram): Broad reach, strong for B2C and top-of-funnel B2B.
  Lower CPCs ($1-5) but requires strong creative to stand out.
- Twitter/X: Niche for tech, developer, and media audiences. Lower competition
  but smaller scale. Best for awareness and community building.

**Measurement Setup:**
- Platform conversion tracking (pixel + API if available)
- UTM parameters on all ad URLs
- View-through conversion window: 1 day (default 7 or 28 days inflates results)

**Optimization Cadence:**
- Daily: check frequency (pause if > 3x/user/week), monitor spend
- Weekly: creative performance review, audience performance review
- Bi-weekly: refresh creative (ad fatigue sets in at 2-3 weeks)
- Monthly: full audience and placement audit

**Expected Ramp Time:** 1-2 weeks for learning phase. Do not judge performance
during platform learning phase -- let algorithms optimize before making changes.

---

## Content / SEO

**Setup Requirements:**
- Keyword research mapped to buyer journey stages (awareness, consideration,
  decision)
- Content calendar built with publishing cadence (minimum 2x/week for SEO impact)
- Analytics tracking: Google Analytics 4, Search Console
- Internal linking strategy documented

**Measurement Setup:**
- Organic traffic by page
- Keyword rankings for target terms
- Engagement: time on page, scroll depth, bounce rate
- Conversions from organic traffic (UTM not needed -- use source/medium filter)

**Optimization Cadence:**
- Monthly: search console review, update underperforming pages
- Quarterly: content audit (prune, consolidate, or refresh)
- Ongoing: internal linking updates as new content publishes

**Expected Ramp Time:** 3-6 months for meaningful organic traffic growth. This
is the slowest channel but compounds the most over time. Do not judge SEO
by first-month results.

**Content-Campaign Integration:**
- Use campaign landing pages as conversion destinations from organic content
- Repurpose campaign messaging into blog posts, guides, and social content
- Build email capture into high-traffic content pages

---

## Events / Webinars

**Setup Requirements:**
- Platform selected (webinar: Zoom, On24, Livestorm; events: Eventbrite, Luma)
- Registration page built with UTM tracking
- Email sequence: confirmation, reminder (24h + 1h), follow-up, replay
- Slide deck or demo environment prepared and tested
- Backup plan for technical failures

**Measurement Setup:**
- Registration count and source attribution
- Attendance rate (target: 40-50% of registrations)
- Engagement: poll responses, Q&A participation, chat activity
- Post-event: follow-up email open/click rate, meeting requests, pipeline created

**Optimization Cadence:**
- Per-event: post-event debrief within 48 hours
- Quarterly: review event ROI, adjust frequency and format

**Expected Ramp Time:** First event attendance is typically low. It takes 3-4
events to build audience expectation and attendance habits. Commit to a series,
not a one-off.

---

## Partnerships / Co-Marketing

**Setup Requirements:**
- Partner alignment on goals, audience, and success metrics
- Co-branded asset creation (who produces what, approval process)
- UTM tracking for both sides (each partner tracks their contribution)
- Legal review of any co-branded materials

**Measurement Setup:**
- Leads/traffic attributed to partnership (UTM + dedicated landing pages)
- Revenue influenced by partner-sourced leads
- Partner engagement (did they actually promote, or just agree to?)

**Optimization Cadence:**
- Monthly: performance review with partner
- Quarterly: evaluate partnership ROI, renew or sunset

**Partnership Selection Criteria:**
- Complementary audience (not competitive)
- Similar company stage and brand quality
- Willing to commit resources (not just logo placement)
- Track record of follow-through (check references)

**Warning:** Partnerships are the most overestimated channel in marketing.
Most co-marketing partnerships produce minimal results because one side does
not follow through. Only invest if both sides have skin in the game.
