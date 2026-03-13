# Platform-Specific Bidding and Targeting Gotchas

Load when configuring campaigns on LinkedIn, Google, or Meta -- specifically when setting bid strategies, audience targeting, or budget allocation within a platform. Also load when diagnosing unexplained spend increases, audience mismatch, or declining ROAS on an existing campaign.

## LinkedIn Ads Gotchas

| Gotcha | What Happens | Fix |
|---|---|---|
| Audience Network default ON | LinkedIn serves ads on partner apps/sites with 70-80% lower engagement and near-zero SQL conversion. Inflates impressions, wastes 15-25% of budget on junk placements. | Uncheck "LinkedIn Audience Network" in every campaign. Check existing campaigns -- it re-enables on campaign duplication. |
| Company size "1-10" includes freelancers | Targeting "1-10 employees" includes solo freelancers and dormant LLCs. Lead quality plummets for B2B enterprise motions. | Set minimum company size to 11+ for B2B. If SMB is the ICP, combine with industry + seniority filters to exclude non-businesses. |
| Job title matching is semantic, not exact | "Marketing Manager" matches "Email Marketing Manager", "Product Marketing Manager", and "Marketing Operations Manager" -- different ICPs with different buying authority. | Use Job Function + Seniority (e.g., Marketing + Director) instead of Job Title for cleaner targeting. Title-based targeting requires constant negative exclusions. |
| Lead Gen Form auto-fill inflates conversion | LinkedIn pre-fills form fields from profile data. Users submit with one tap. Result: high volume, low intent. 40-60% of Lead Gen Form leads never respond to follow-up. | Add a custom text field (not auto-fillable) asking a qualifying question. Example: "What's your biggest challenge with X?" Reduces volume 30-40% but intent quality doubles. |
| "Matched Audiences" CRM list match rate | LinkedIn matches on email, and B2B email domains often yield 30-50% match rates (personal vs work emails). Half your CRM list won't match. | Upload both work and personal emails if available. Supplement with company name + job title matching via Account Targeting. |
| Frequency cap absence | LinkedIn has no manual frequency cap. Users in small audiences (ABM) see the same ad 15-20 times. Ad fatigue destroys engagement after 7-8 impressions. | Rotate 3-4 creatives per campaign. Monitor frequency in campaign analytics. If frequency exceeds 8, add new creatives or expand audience by 20-30%. |
| Campaign budget optimizer (CBO) cannibalization | CBO across campaigns shifts budget to the campaign with cheapest clicks, not highest conversion quality. TOFU awareness campaigns eat BOFU conversion budget. | Never group TOFU and BOFU campaigns under the same CBO. Use separate campaign groups for each funnel stage with independent budgets. |

## Google Ads Gotchas

| Gotcha | What Happens | Fix |
|---|---|---|
| Broad match with Smart Bidding drift | Broad match + Target CPA learns to find cheap conversions, not quality conversions. It will match "free CRM" and "CRM tutorial" for a paid CRM product because those clicks convert to email signups (cheap conversions), not SQLs. | Use broad match only with offline conversion import (SQL data from CRM). Without SQL-level conversion data, use phrase match. |
| Search Partners default ON | "Google Search Partners" includes Ask.com, AOL, and other low-quality search sites. Traffic quality is 50-70% lower than Google.com proper. | Uncheck Search Partners on all campaigns. If enabled historically, segment performance data by "Network (with search partners)" to see the damage. |
| Performance Max black box | PMax campaigns automatically serve across Search, Display, YouTube, Gmail, Maps, and Discover. No control over placement mix. Google optimizes for its own ad inventory balance, not your conversion quality. | Use PMax only for e-commerce with product feeds. For B2B lead gen, use dedicated Search campaigns with manual placement control. |
| Responsive Search Ad (RSA) headline pinning trap | Google rotates 15 headlines. Without pinning, your brand name might not show. But over-pinning (pinning all positions) prevents Google's optimization. | Pin brand name to Position 1 only. Pin primary CTA to Position 3. Leave Positions 2 and all descriptions unpinned for rotation. |
| Location targeting "Presence OR Interest" | Default "Presence or interest" targets users who SHOW INTEREST in a location, not who ARE there. A user in India researching "New York office space" sees your NYC-only ad. | Switch to "Presence: People in or regularly in your targeted locations" for all B2B campaigns. The "interest" setting wastes 10-20% of geo-targeted budget. |
| Conversion action default: all conversions | Google counts ALL conversion actions (page views, button clicks, form fills) equally. If "Add to Cart" and "Purchase" are both conversion actions, Smart Bidding optimizes for the cheaper one. | Set only your primary conversion (SQL, demo booked, purchase) as "Primary" conversion action. All others set to "Secondary" (tracked but not optimized for). |
| Display campaign audience expansion | "Optimized targeting" on Display campaigns automatically expands beyond your selected audiences to "similar" users. Google's similarity model is opaque and often poor for B2B. | Uncheck "Optimized targeting" for all B2B Display campaigns. Use explicit remarketing lists and customer match only. |

## Meta (Facebook/Instagram) Ads Gotchas

| Gotcha | What Happens | Fix |
|---|---|---|
| Advantage+ audience override | Advantage+ Audience (Meta's AI targeting) treats your selected audience as a "suggestion" and expands broadly. Your carefully selected "SaaS founders" audience becomes "anyone who clicked a tech ad." | For B2B: use Original Audience Options (toggle off Advantage+ Audience). For B2C or broad awareness, Advantage+ can work but requires conversion optimization with CRM data, not just pixel events. |
| Conversion API (CAPI) vs Pixel deduplication | Running both Pixel and CAPI without deduplication double-counts conversions. Your reported CPA looks 30-50% better than reality. | Implement CAPI with event_id deduplication. Match event_id between browser Pixel and server CAPI events. Without this, your entire measurement is wrong. |
| iOS 14.5+ attribution window | Post-ATT, Meta's default attribution is 7-day click / 1-day view. B2B sales cycles are 30-90 days. Meta reports zero conversions for leads that convert 3 weeks after clicking. | Supplement Meta reporting with UTM-based CRM attribution. Meta's reported numbers undercount by 20-40% for long B2B sales cycles. Budget decisions based solely on Meta's dashboard will under-invest in Meta. |
| Lookalike audience quality decay | Lookalikes based on page visitors or email openers are low-quality for B2B. Best lookalike seed: closed-won customers (min 100, ideal 500+). | Build lookalikes from CRM closed-won list, not pixel audiences. If closed-won list is <100, use SQLs as seed. Never use "All website visitors" for B2B lookalikes. |
| Automatic placements includes Audience Network | Meta's Audience Network (partner apps) is low quality for B2B lead gen. CPL looks cheap but SQL conversion is near-zero. Same pattern as LinkedIn Audience Network. | For B2B: manually select Facebook Feed, Instagram Feed, and Instagram Stories only. Deselect Audience Network, Messenger, and right column. |
| Creative exhaustion signal | Meta doesn't surface "creative fatigue" as a metric. It manifests as rising CPM + declining CTR. By the time you notice, you've overspent for 1-2 weeks. | Set up automated rule: if CTR drops >25% from 7-day average AND CPM rises >15%, pause the ad set and alert the team. Refresh creatives every 2-3 weeks proactively. |

## Cross-Platform Budget Waste Checklist

Run this monthly across all active campaigns:

- [ ] LinkedIn: Audience Network disabled on ALL campaigns (check after any duplication)
- [ ] Google: Search Partners disabled on all Search campaigns
- [ ] Google: Location targeting set to "Presence" not "Presence or interest"
- [ ] Google: Only primary conversion actions set to "Primary"
- [ ] Meta: Advantage+ Audience disabled for B2B campaigns
- [ ] Meta: CAPI + Pixel deduplication confirmed (check event_id matching)
- [ ] Meta: Audience Network excluded from B2B placements
- [ ] All platforms: No campaign has frequency >8 without creative rotation
- [ ] All platforms: Conversion data matches CRM SQL numbers within 15% variance
