# Consent Mode v2 Implementation Reference

## Consent Signal Types

| Signal | Controls | Default (no consent) | When Granted |
|---|---|---|---|
| analytics_storage | GA4 cookies (_ga, _ga_XXXXX) | No cookies set. GA4 operates in cookieless mode with modeled data | Full GA4 tracking with cookies. User-level persistence across sessions |
| ad_storage | Advertising cookies (Google Ads, Floodlight) | No ad cookies. Conversion tracking uses modeled conversions | Full conversion tracking, remarketing audience building |
| ad_user_data | Sending user data to Google for advertising | No user data sent to Google Ads | User data (email for Customer Match, click IDs) sent to Google for ad targeting |
| ad_personalization | Personalized advertising | No personalized ads served | Remarketing, similar audiences, personalized ad delivery |
| functionality_storage | Functional cookies (language preference, login state) | No functional cookies | Non-analytics cookies that improve UX |
| personalization_storage | Personalization cookies (content recommendations) | No personalization cookies | Content and recommendation personalization |
| security_storage | Security cookies (authentication, fraud detection) | Allowed by default (legitimate interest) | Always allowed -- security cookies are typically exempt from consent |

**March 2024 requirement**: Google requires `ad_user_data` and `ad_personalization` signals for EU traffic. Without these, Google Ads conversion data and remarketing audiences are incomplete. This is in addition to the existing `analytics_storage` and `ad_storage` signals.

## CMP Integration Patterns

| CMP | Integration Method | Key Gotcha |
|---|---|---|
| OneTrust | GTM template (OneTrust Cookie Consent) or direct JS integration | OneTrust categories (C0001-C0005) must be mapped to Google consent types. Default mapping is NOT automatic -- you must configure the mapping in OneTrust's Geolocation Rules |
| Cookiebot | GTM template (Cookiebot CMP) with automatic consent mode integration | Cookiebot's "Statistics" category maps to analytics_storage, "Marketing" to ad_storage. But: ad_user_data and ad_personalization require separate configuration in Cookiebot's settings -- they're NOT included in the default GTM template |
| Didomi | GTM template or Didomi SDK with consent mode adapter | Didomi uses purpose-based consent (not category-based). You must map Didomi purposes to Google consent types in the adapter configuration. The mapping is not 1:1 |
| Custom CMP | Direct gtag consent API calls | Must call `gtag('consent', 'default', {...})` BEFORE the GA4 config tag fires. Race condition is the #1 failure: if GA4 loads before consent default is set, first page events fire without consent signals |
| No CMP (consent wall) | Block all tracking until explicit opt-in | Simplest implementation but loses 40-70% of data (most EU users don't actively opt in). Google's behavioral modeling helps but accuracy degrades significantly below 70% consent rate |

## Implementation Sequence

The order of operations is critical. Getting this wrong means tags fire before consent is configured.

| Step | When | What | If Wrong |
|---|---|---|---|
| 1. Set consent defaults | First thing on page load (before ANY tags) | `gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' })` | Tags fire with implicit "granted" state. You've just violated GDPR for every EU visitor |
| 2. Load CMP | After consent defaults, before user interaction | CMP banner appears. User can interact | If CMP loads slowly (>2s), users navigate away without consenting. Pre-load CMP script in `<head>` |
| 3. GA4 config tag fires | After consent defaults are set | GA4 initializes in cookieless/modeled mode | GA4 still fires even with consent denied -- but in cookieless mode. This is intentional and GDPR-compliant |
| 4. User grants consent | When user clicks "Accept" in CMP | CMP calls `gtag('consent', 'update', { analytics_storage: 'granted', ... })` | If the update call doesn't reach gtag (JavaScript error, CMP misconfiguration), consent is never recorded and all subsequent visits remain cookieless |
| 5. Tags re-fire with consent | Immediately after consent update | GA4 sets cookies and sends a consent_state event. Ads tags fire if ad_storage granted | If tags don't re-fire, the current pageview is lost. GTM's "Consent Initialization" trigger type handles this automatically |

## Behavioral Modeling

When consent is denied, GA4 uses machine learning to model the missing data. Understanding the modeling limitations is critical for data quality assessment.

| Metric | Modeling Accuracy (>70% consent rate) | Modeling Accuracy (<50% consent rate) | Implication |
|---|---|---|---|
| User count | ~95% of actual | ~70-80% of actual | Low consent rates mean modeled user counts are unreliable. Don't trust user-level analysis |
| Session count | ~95% | ~75-85% | Sessions are easier to model than users (shorter attribution window) |
| Conversion count | ~90% | ~60-70% | Conversion modeling is the weakest. Below 50% consent, conversion numbers are estimates, not measurements |
| Traffic source attribution | ~85% | ~50-60% | Source/medium modeling degrades fastest. With <50% consent, channel attribution is essentially guessing |

**Critical threshold**: Below 70% consent rate, Google's behavioral modeling accuracy drops significantly. Below 50%, most modeled metrics are unreliable for decision-making. If your consent rate is below 50%, consider:
1. Improving consent UX (clearer value proposition, fewer categories to choose)
2. Server-side tracking with first-party data (bypasses cookie consent requirement for basic analytics in many EU DPA rulings)
3. Switching to cookieless analytics (Plausible, Fathom) that don't require consent

## Testing Consent States

| Test Scenario | How to Test | Expected Behavior | Common Failure |
|---|---|---|---|
| Default (no interaction) | Load page without interacting with CMP | GA4 fires in cookieless mode. No _ga cookies. DebugView shows events with consent_state: denied | GA4 doesn't fire at all (consent mode blocking tag instead of allowing cookieless mode) |
| Accept all | Click "Accept All" in CMP | Cookies set. Consent_state changes to granted. Events re-fire with cookies | Cookies set but consent_state doesn't update (CMP doesn't call gtag consent update) |
| Reject all | Click "Reject All" | No cookies. Cookieless mode persists. No ad tags fire | Some ad tags fire despite rejection (tag not configured for consent checks in GTM) |
| Partial consent (analytics only) | Accept statistics, reject marketing | GA4 cookies set (analytics_storage: granted). No ad cookies (ad_storage: denied) | All-or-nothing implementation: CMP sends all signals as granted or all as denied, no granular control |
| Consent withdrawal | Accept, then revoke via CMP settings page | Cookies deleted. Future events in cookieless mode | Cookies persist after revocation (CMP doesn't trigger cookie cleanup). GDPR requires effective revocation |
| Cross-session persistence | Accept on visit 1, return on visit 2 | Consent state persisted (CMP cookie). No banner shown. GA4 fires with granted state | CMP cookie expires or is blocked by browser (ITP in Safari: 7-day cookie cap for JavaScript-set cookies) |

## Regional Consent Requirements

| Region | Requirement | Consent Model | Implementation Note |
|---|---|---|---|
| EU/EEA (GDPR) | Explicit opt-in before any non-essential tracking | Prior consent | Must default to "denied" for all storage types. No pre-checked boxes. Reject must be as easy as accept |
| UK (UK GDPR + PECR) | Same as EU in practice | Prior consent | Post-Brexit, UK GDPR mirrors EU GDPR. ICO enforces PECR for cookies |
| California (CCPA/CPRA) | Opt-out model (can track by default, must honor "Do Not Sell") | Opt-out | Can fire tags by default. Must provide "Do Not Sell My Personal Information" link. GPC (Global Privacy Control) browser signal must be honored |
| Brazil (LGPD) | Consent or legitimate interest | Hybrid | Can use legitimate interest for basic analytics (similar to some EU DPA rulings). Marketing cookies require consent |
| Canada (PIPEDA + provincial) | Implied consent for non-sensitive, explicit for sensitive | Hybrid | Analytics tracking under implied consent is generally accepted. Targeting and profiling require explicit consent |
| Rest of world | Varies widely | Notice-only (minimum) | Default: provide cookie notice. Check specific country laws as they evolve. Many countries are adopting GDPR-like frameworks |
