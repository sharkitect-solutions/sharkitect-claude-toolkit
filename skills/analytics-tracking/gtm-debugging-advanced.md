# GTM Debugging and Server-Side Reference

## Debugging Decision Tree

Start here when tracking isn't working as expected.

| Symptom | First Check | Second Check | Likely Cause |
|---|---|---|---|
| No events in GA4 at all | Is GTM container loaded? (View Source, search for `gtm.js`) | Is GA4 config tag firing? (GTM Preview > Tags Fired) | GTM snippet not on page, or GA4 Measurement ID wrong. Most common: staging vs production container ID mismatch |
| Events fire in Preview but not in GA4 | Check GA4 DebugView (requires `?debug_mode=true` or Chrome extension) | Check GA4 property's data stream -- is the Measurement ID correct? | Preview mode uses debug endpoint. Production may have different Measurement ID, or tag is paused in production workspace |
| Events fire but parameters are missing | Check Variables in GTM Preview -- are they resolving? | Check Data Layer in Preview -- is the data layer push happening before the trigger? | Timing issue: trigger fires before data layer push. Fix: change trigger from "Page View" to "DOM Ready" or "Window Loaded" |
| Events fire twice | Check tag firing count in GTM Preview | Check for multiple GTM containers on the same page | Duplicate GTM snippets (one hardcoded, one injected by CMS plugin). Or: trigger fires on both "Click" and "Form Submit" for form buttons |
| Events fire on wrong pages | Check trigger conditions in GTM Preview > Triggers | Verify Page Path variable matches expectation (trailing slashes, query parameters) | Page Path matching: `/checkout` doesn't match `/checkout/` (with trailing slash). Use "contains" or regex matcher instead of "equals" |
| Conversion count doesn't match GA4 | Compare GTM tag firing count vs GA4 event count | Check GA4 conversion counting method (once per session vs every event) | "Once per session" counts one conversion even if the tag fires 5 times. Or: ad blocker prevents tag from reaching GA4 servers |
| User ID not appearing in GA4 | Check if user_id is set in GTM variable | Verify GA4 config tag has "Fields to Set" with user_id | user_id must be set in the GA4 Configuration tag (not just event tags). Or: user_id is set after the first page_view, so the first event in each session has no user_id |

## Data Layer Debugging

| Check | How | What Good Looks Like | Common Problem |
|---|---|---|---|
| Data layer exists | Browser console: `typeof dataLayer` | Returns "object" | `dataLayer` is undefined -- GTM snippet loads after your data layer push. Fix: define `window.dataLayer = window.dataLayer || [];` BEFORE the GTM snippet |
| Data layer contents | Console: `JSON.stringify(dataLayer, null, 2)` | Array of objects, each with `event` key for custom events | Objects without `event` key are property-setters (valid but won't trigger GTM Custom Event triggers) |
| Push timing | Console: override `dataLayer.push` to add timestamps | Pushes happen before relevant triggers fire | Data layer push in `DOMContentLoaded` but trigger set to "Page View" (fires earlier). DOM Ready trigger matches DOMContentLoaded |
| Nested values | Console: `dataLayer.filter(d => d.event === 'purchase')` | Object with expected nested structure (ecommerce.items array) | Flat structure instead of nested (ecommerce data must use Google's expected nesting for Enhanced Ecommerce) |
| GTM processes the push | GTM Preview > Data Layer tab | Event appears with correct key-value pairs | GTM Preview shows the push but variable doesn't resolve -- Variable name doesn't match (case-sensitive, dot notation for nesting) |

## GTM Server-Side Tagging

### Architecture Overview

| Component | What | Where | Cost |
|---|---|---|---|
| Web container (client-side) | Standard GTM container on the website | Loaded in browser | Free (Google Tag Manager) |
| Server container | Processes events server-side before routing to destinations | Google Cloud Run or App Engine | $50-500/month depending on traffic volume. Auto-scaling Cloud Run recommended |
| Transport | How events get from web to server container | First-party domain (sgtm.yourdomain.com) via GA4 transport | Requires DNS configuration (CNAME or A record pointing to Cloud Run) |
| Clients | Server-side equivalent of triggers -- parse incoming requests | Inside server container | GA4 client parses GA4 requests. Measurement Protocol client parses custom requests |
| Tags | Server-side equivalent of tags -- send data to destinations | Inside server container | GA4 tag, Google Ads tag, Facebook CAPI tag, custom HTTP request tags |

### When Server-Side Is Worth It

| Signal | Why Server-Side Helps | ROI |
|---|---|---|
| Ad blocker rate >20% | First-party domain (sgtm.yourdomain.com) bypasses most ad blockers. Recovery of 15-25% of lost events | High -- directly recovers lost conversion data |
| Cookie duration <7 days (Safari ITP) | Server-set first-party cookies bypass ITP's 7-day JavaScript cookie cap. Extends cookie duration to your server's max-age | High for Safari-heavy audiences (iOS users). Recovers 10-20% user identity |
| Need to enrich events before sending | Server container can append server-side data (CRM ID, subscription status) before sending to GA4/Ads | Medium -- enables richer analytics without exposing server data to client |
| Reduce client-side JS load | Move heavy tags (Facebook, LinkedIn, TikTok pixels) server-side. Client sends one request, server fans out | Medium -- reduces 200-500ms of client-side tag loading time |
| Data compliance requirements | Server container acts as a data proxy. You control exactly what data leaves your infrastructure | High for regulated industries -- PII scrubbing, data residency enforcement |

### Server-Side Gotchas

| Gotcha | Impact | Fix |
|---|---|---|
| Cloud Run cold starts | First request after idle period takes 2-5 seconds. Events delayed or lost if timeout is too short | Set minimum instances to 1 (costs ~$15-25/month for always-warm). Or: configure Cloud Run with `min-instances=1` |
| IP address is server, not client | Server-side requests come from your server's IP, not the user's. Geo-targeting in GA4 shows your server's location | Forward client IP via `X-Forwarded-For` header. GA4 client in server container handles this automatically if configured |
| Preview mode is separate | Server container preview is independent of web container preview. Must debug both simultaneously | Open web container preview AND server container preview in separate tabs. Use the "Debug" request header to link them |
| Facebook CAPI deduplication | If running both client-side pixel AND server-side CAPI, events are counted twice | Set `event_id` in both client and server events. Facebook deduplicates by event_id within a 48-hour window. The event_id MUST match exactly |
| Custom domain SSL | First-party domain (sgtm.yourdomain.com) requires SSL certificate | Google auto-provisions certificate for custom domains in Cloud Run, but propagation takes 15-60 minutes. During this window, HTTPS requests fail |
| Logging costs | Server container logging to Cloud Logging can cost more than the compute itself at high volume | Set log level to WARNING or ERROR in production. Debug logging should only be enabled for debugging sessions |

## Browser-Specific Tracking Issues

| Browser | Issue | Impact | Workaround |
|---|---|---|---|
| Safari (ITP) | JavaScript-set cookies capped at 7 days. Third-party cookies blocked entirely | Users returning after 7 days appear as "new." GA4 user count inflated by 15-30% for Safari-heavy sites | Server-side tagging with first-party cookies (server-set cookies bypass ITP). Or: accept the limitation and adjust user metrics |
| Firefox (ETP) | Third-party cookies blocked by default. Some tracker domains blocked | Similar to Safari but less aggressive. Ad pixels (Facebook, LinkedIn) may not fire | Server-side CAPI for affected ad platforms. First-party analytics tracking is unaffected |
| Brave | Aggressive ad/tracker blocking. Blocks GTM by default on strict settings | 100% data loss for Brave users on strict mode (~2-5% of traffic) | No reliable workaround. Server-side with first-party domain recovers some, but Brave's strict mode blocks known analytics domains |
| Chrome (post-2025) | Third-party cookie deprecation timeline uncertain. Privacy Sandbox APIs (Topics, Attribution Reporting) replace cookies | GA4 first-party cookies unaffected. Google Ads conversion tracking moves to Privacy Sandbox APIs | Ensure Consent Mode v2 is implemented. Google handles the Privacy Sandbox transition automatically for GA4/Ads |
| iOS in-app browsers | WKWebView (used by social media apps) has separate cookie jar from Safari | Users clicking links from Instagram, Facebook, LinkedIn etc. appear as new users every time. Inflates user count significantly | Limited options. Deep links to Safari (using universal links) or server-side user matching via login state |
