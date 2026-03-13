# Attribution Model Implementation

Load when setting up multi-touch attribution, designing UTM architecture, debugging attribution gaps, measuring dark funnel influence, or reconciling platform-reported conversions against CRM data.

## UTM Architecture

UTM parameters are your attribution foundation. Inconsistent UTMs make attribution impossible retroactively.

### Required UTM Structure

```
?utm_source={platform}
&utm_medium={channel_type}
&utm_campaign={campaign_id}
&utm_content={creative_variant}
&utm_term={keyword_or_audience}
```

### UTM Naming Convention (Enforce Exactly)

| Parameter | Format | Examples | Common Mistakes |
|---|---|---|---|
| utm_source | Lowercase platform name, no spaces | `linkedin`, `google`, `meta`, `partner-acme` | `LinkedIn`, `Google Ads`, `facebook` (Facebook rebranded to Meta in ads context) |
| utm_medium | Channel type, not platform | `paid-social`, `paid-search`, `cpc`, `display`, `email`, `organic-social` | `linkedin` (that's a source, not a medium), `ad`, `ppc` |
| utm_campaign | Kebab-case, include funnel stage | `tofu-thought-leadership-q1`, `bofu-demo-competitor-x`, `mofu-webinar-security` | `Campaign 1`, `test`, untitled campaigns without funnel stage |
| utm_content | Creative or offer variant | `carousel-testimonial`, `single-image-pain-point`, `video-demo-30s` | Missing entirely, or same value for all creatives (makes A/B testing invisible) |
| utm_term | Keyword (search) or audience segment (social) | `crm-software-enterprise`, `director-marketing-saas-500plus` | Missing for social campaigns (critical for audience-level attribution) |

### UTM Hygiene Rules

1. **Case sensitivity kills attribution**: `LinkedIn` and `linkedin` are separate sources in every analytics tool. Enforce lowercase everywhere.
2. **No spaces, ever**: Use hyphens. Spaces become `%20` in URLs and break reporting filters.
3. **Document in a shared sheet**: Maintain a live UTM registry (Google Sheet or Notion) that all marketers reference. Free-form UTM creation guarantees inconsistency within 2 weeks.
4. **URL builder enforcement**: Use a team UTM builder tool (Google's Campaign URL Builder, or a custom sheet) that validates naming conventions before generating the URL.
5. **Auto-tagging conflict**: Google Ads auto-tagging (`gclid`) and manual UTM can conflict. In GA4, auto-tagging overrides UTM. Decision: use auto-tagging for Google Ads and manual UTM for all other platforms.

## Multi-Touch Attribution Math

### W-Shaped Model (Recommended for B2B SaaS)

Credits three key touchpoints more heavily:

| Touchpoint | Credit | Why |
|---|---|---|
| First touch (discovery) | 30% | The channel that introduced the prospect to you |
| Lead creation (MQL moment) | 30% | The touchpoint that converted anonymous visitor to known lead |
| Opportunity creation (SQL moment) | 30% | The touchpoint that triggered sales engagement |
| All other touches | 10% (split equally) | Nurture touches that maintained awareness between key moments |

**Implementation**: Requires CRM timestamps for: first website visit (with UTM), lead creation event, opportunity creation event, and all touchpoints in between.

### Attribution Data Pipeline

| Step | Data Source | What You Capture |
|---|---|---|
| 1. First touch | Website analytics (GA4, Segment) | UTM parameters from first visit, landing page, referrer |
| 2. All touches | Marketing automation (HubSpot, Marketo) | Every email open, page visit, content download, webinar attendance with timestamps |
| 3. Lead creation | CRM (Salesforce, HubSpot CRM) | The specific action that created the lead record (form fill, demo request, signup) |
| 4. Opportunity creation | CRM | When sales accepted the lead as an opportunity, with the triggering touchpoint |
| 5. Closed-won | CRM | Final deal amount, close date, all associated touchpoints |

**Critical gap**: Most teams capture steps 3-5 in CRM but lose steps 1-2 because website analytics and CRM aren't connected. Without first-touch data, you cannot evaluate top-of-funnel channel effectiveness.

### Connecting the Pipeline

| Integration | Purpose | Implementation |
|---|---|---|
| UTM -> CRM | Carry UTM params into lead record | Hidden form fields auto-populated from URL params, or JavaScript that reads UTMs and writes to cookie -> form -> CRM |
| GA4 -> CRM | Match anonymous sessions to known leads | User ID or Client ID matching. GA4 Measurement Protocol for server-side events. |
| CRM -> Analytics | Feed offline conversions back | Offline conversion import: upload SQL and closed-won events to Google Ads, Meta CAPI, LinkedIn Offline Conversions |

**Offline conversion import is non-negotiable for B2B**: Without it, Google/Meta/LinkedIn optimize for form fills (cheap, low-quality) instead of SQLs (expensive, high-quality). Import SQL events with a 90-day lookback to train platform algorithms on your actual valuable conversions.

## Dark Funnel Measurement

30-60% of B2B buyer journey happens in channels you cannot track: Slack communities, WhatsApp groups, podcast mentions, word-of-mouth, LinkedIn DMs, private communities.

### Dark Funnel Evidence Collection

| Method | Implementation | What It Reveals |
|---|---|---|
| "How did you hear about us?" (open text field) | Add to demo request form, signup form, or first sales call script. MUST be open text, not dropdown. | Untrackable channels: "My colleague mentioned you", "Saw a post in a Slack community", "Heard your CEO on a podcast" |
| Self-reported attribution vs UTM comparison | Compare CRM "how did you hear" field against first-touch UTM data | When self-report says "podcast" but UTM says "google-search", the podcast drove the AWARENESS and Google drove the CLICK. Both channels deserve credit. |
| Content engagement before form fill | Track which pages a lead visited before converting (marketing automation page tracking) | A lead who read 5 blog posts before requesting a demo was nurtured by content, even if the UTM says "paid-search". The search ad was the last mile, not the whole journey. |
| Brand search volume trends | Monitor branded keyword search volume in Google Search Console and Google Trends | Rising brand search after podcast appearances, conference talks, or community engagement = dark funnel working. You can't track it per-lead, but you can see the trend. |

### Dark Funnel Attribution Rules

1. **Self-reported attribution is a leading indicator, not a tracking replacement**: Use it to identify which dark channels matter, then increase investment in those channels even though you can't measure them per-lead.
2. **Brand search is a proxy metric for dark funnel**: If brand search volume rises 20% after a podcast tour, the podcast tour is working -- even with zero trackable UTMs.
3. **Do not attribute dark funnel to "Direct/None"**: In analytics, "Direct" traffic includes dark funnel referrals (someone typed your URL after hearing about you in a Slack group). A rising Direct traffic percentage alongside rising self-reported word-of-mouth is a positive signal, not a tracking failure.

## Attribution Debugging

| Symptom | Likely Cause | Diagnostic Step |
|---|---|---|
| Platform reports 2x more conversions than CRM | Attribution window mismatch or deduplication failure | Compare platform attribution windows (7-day view, 28-day click) against CRM conversion timestamps. Check Meta CAPI deduplication. |
| First-touch data missing for 40%+ of leads | UTM parameters not passing to CRM | Test the form submission flow end-to-end. Check if hidden UTM fields are populated. Check if cookie-to-form bridge is working. |
| "Direct/None" is the top channel at >30% | Dark funnel or tracking gap | Add "How did you hear about us?" field. Check if UTMs are stripped by redirects, link shorteners, or SSO flows. |
| Google Ads shows 50 conversions, CRM shows 20 SQLs | Google counts all conversion actions; CRM counts SQLs | Verify only SQL-equivalent actions are set as Primary conversion in Google Ads. Import offline SQL conversions. |
| LinkedIn reports lower conversions than CRM attributes to LinkedIn | LinkedIn's 30-day attribution window is shorter than B2B sales cycles | Use UTM-based CRM attribution for LinkedIn (longer lookback) alongside LinkedIn's native reporting. |
| Month-over-month attribution shifts dramatically | Model instability or seasonality | Check if the attribution model changed, new UTM parameters were introduced, or a major campaign launched that shifted touchpoint distribution. |
