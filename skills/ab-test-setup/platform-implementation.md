# A/B Testing Platform Implementation Guide

## Tool Selection Decision

| Signal | Recommended Tool | Why |
|---|---|---|
| Marketing team runs tests, no engineering support | **Optimizely, VWO** | Visual editor, no-code variant creation, built-in analytics. Marketing can run tests independently |
| Product team, feature flags already in use | **PostHog, LaunchDarkly, Statsig** | Feature flag infrastructure doubles as experiment framework. Single system for flags + experiments |
| Data team wants full control over analysis | **Eppo, Statsig** | Warehouse-native: experiments defined in tool, analysis runs on YOUR data warehouse. No data duplication |
| Startup, <10K monthly visitors, tight budget | **PostHog (free tier), Google Optimize replacement (manual)** | PostHog free tier includes experiments for up to 1M events/month. Most startups don't need enterprise tools |
| Enterprise, strict data governance | **Eppo, LaunchDarkly** | Data stays in your warehouse (Eppo) or SOC2/HIPAA compliant infrastructure (LaunchDarkly) |
| Just need quick client-side tests | **VWO, Convert** | Fastest time to first test. Visual editor handles most marketing page changes |

## Platform Comparison

| Feature | PostHog | Optimizely | VWO | LaunchDarkly | Statsig | Eppo |
|---|---|---|---|---|---|---|
| **Client-side testing** | YES | YES | YES | YES (limited) | YES | NO (warehouse-native) |
| **Server-side testing** | YES | YES | YES | YES | YES | YES |
| **Visual editor** | YES (basic) | YES (advanced) | YES (advanced) | NO | NO | NO |
| **Bayesian stats** | YES | NO (frequentist) | NO (frequentist) | N/A | YES | YES (both) |
| **Sequential testing** | YES | NO | NO | N/A | YES | YES |
| **SRM detection** | YES (auto) | NO (manual) | NO (manual) | N/A | YES (auto) | YES (auto) |
| **Warehouse-native** | NO (own database) | NO | NO | NO | Partial | YES |
| **Free tier** | YES (generous) | NO | NO | YES (limited) | YES (limited) | NO |
| **Pricing** | Free-$450/mo | $36K+/year | $200+/mo | $10K+/year | Free-custom | Custom (enterprise) |

---

## Client-Side vs Server-Side Testing

### Client-Side Implementation

| Aspect | Details |
|---|---|
| **How it works** | JavaScript snippet loads, determines variant, modifies DOM before/after render |
| **Assignment** | Client-side cookie or localStorage |
| **Variant delivery** | DOM manipulation (hide/show/modify elements) |
| **Flicker risk** | HIGH. Page loads with original, then shifts to variant. Users see a "flash" |

### Flicker Prevention

| Technique | How It Works | Impact |
|---|---|---|
| **Anti-flicker snippet** | Hides page until variant JavaScript executes. Shows page only after modifications complete | Prevents flicker but adds 50-200ms to perceived load time. Google penalizes if >300ms |
| **CSS hiding** | Add `visibility: hidden` to test elements via CSS. JavaScript removes it after applying variant | Less aggressive than full-page hide. Only test elements are delayed |
| **Async loading with placeholder** | Show skeleton/placeholder in test area. Replace with variant when ready | Better UX than hiding. User sees loading state, not flicker |
| **Server-side only** | Don't use client-side for flicker-sensitive elements | Eliminates the problem entirely. More engineering work |

**Flicker reality check**: Google's anti-flicker snippet (from old Optimize) delays page render by up to 4 seconds. This DESTROYS Core Web Vitals. If you use anti-flicker, set a strict timeout (300ms max) and accept that some users will see the control if JavaScript is slow.

### Server-Side Implementation

| Aspect | Details |
|---|---|
| **How it works** | Server determines variant at request time. Response already contains correct variant HTML |
| **Assignment** | Server-side (user ID hash, cookie read on server, or feature flag SDK) |
| **Variant delivery** | Different HTML/data in the response. No DOM manipulation needed |
| **Flicker risk** | ZERO. Page arrives with the correct variant already rendered |

### Server-Side Gotchas

| Gotcha | What Happens | Fix |
|---|---|---|
| **CDN caching** | CDN caches the first variant it sees and serves it to everyone. Test appears to work in dev, breaks in production | Vary header by cookie. Or bypass CDN for test pages. Or use edge-side assignment (Cloudflare Workers, Vercel Edge Middleware) |
| **Sticky session failure** | Load balancer sends user to different server on return. New server doesn't have their assignment | Store assignment in shared state (Redis, database) or derive deterministically from user ID hash |
| **SSR + client hydration mismatch** | Server renders variant B, but client-side React hydrates with variant A (or vice versa) | Pass variant assignment from server to client via serialized state (window.__EXPERIMENT_DATA__). Never re-randomize on client |
| **Feature flag SDK latency** | SDK makes network call to get flag value. Adds 50-200ms to server response | Use local evaluation mode (download all flags on server start, evaluate locally). Most SDKs support this |

---

## CDN and Caching Interference

The #1 reason server-side A/B tests silently break in production.

| Scenario | What Breaks | Detection | Fix |
|---|---|---|---|
| **Full-page CDN cache** | CDN caches variant A's HTML. All subsequent users get variant A regardless of assignment | SRM: one variant has 95%+ of traffic | Add `Vary: Cookie` header. Or set `Cache-Control: private` on test pages. Or use edge-side assignment |
| **API response cache** | CDN caches API response for first variant. Subsequent users get wrong data | Test results show no difference between variants (both getting same data) | Set `Cache-Control: no-store` on experiment API endpoints. Or include variant in cache key |
| **Static asset cache** | CSS/JS for variant B is cached with aggressive TTL. After test ends, some users still see variant B | Users report "old" version weeks after test concluded | Use versioned asset URLs (hash in filename). Purge CDN on test completion |
| **Browser cache** | User assigned to variant A. Clears cookies. Re-assigned to variant B. Browser cache still has variant A assets | Intermittent visual glitches. Hard to reproduce | Use unique class names per variant. Don't rely on cached stylesheets for variant-specific styles |

---

## Feature Flag to A/B Test Migration

Many teams start with feature flags (binary on/off) and want to graduate to A/B tests (measured comparison).

### Migration Steps

| Step | What Changes | Common Mistake |
|---|---|---|
| 1. Add measurement | Attach conversion metric to the flag. Track metric for both flag-on and flag-off users | Measuring only flag-on users. You need the control group (flag-off) measured identically |
| 2. Randomize assignment | Change from targeted rollout (specific users/%) to random assignment | Not ensuring assignment is sticky. User who was flag-on for 3 weeks gets re-randomized to flag-off. Contaminated data |
| 3. Define hypothesis | What do you expect the flag to change? By how much? What metric? | "We just want to see what happens" -- this is the Level 1 hypothesis trap from SKILL.md |
| 4. Calculate sample size | Based on current baseline and minimum detectable effect | Running the "experiment" for 2 days because "we have a lot of traffic." Check the calculator |
| 5. Run and analyze | Follow standard A/B test protocol (no peeking, check SRM, etc.) | Treating it like a flag rollout: "looks good after a day, ship it" |

### Flag Percentage != A/B Split

| | Feature Flag 50% | A/B Test 50/50 |
|---|---|---|
| **Purpose** | Gradual rollout, risk mitigation | Measured comparison |
| **Measurement** | Optional, often pre/post | Required, concurrent comparison |
| **Duration** | Until confident, then ramp to 100% | Until sample size reached |
| **Assignment stability** | Users may be re-assigned as % changes | Users MUST stay in assigned variant |
| **Analysis** | "Did anything break?" | "Did it improve metric X by Y%?" |

---

## Tracking Implementation Checklist

| Check | Why | How to Verify |
|---|---|---|
| Variant assignment fires BEFORE any user interaction | If assignment fires on click, users who bounce are never assigned. Surviving population is biased | Check timestamp of assignment event vs page view event. Assignment should be <= page view |
| Same user always gets same variant | Without sticky assignment, A/B test becomes random noise | Log in as test user. Reload page 20 times. Check that variant never changes |
| Assignment logged even for users who don't convert | Denominator must include ALL assigned users, not just converters | Compare assignment count to conversion count. Ratio should match expected conversion rate |
| No double-counting of conversions | User converts, comes back, converts again. Counted once or twice? | Check conversion events per user. If metric is "signed up," each user should have exactly 0 or 1 conversion |
| Cross-device attribution handled (or acknowledged) | User sees variant B on mobile, converts on desktop. Which variant gets credit? | If using cookie-based assignment, accept ~5-10% cross-device leakage. Document this limitation |
| Revenue tracking matches source of truth | A/B tool says $50K revenue, backend says $48K | Compare A/B tool revenue total to payment processor total for same period. Discrepancy >2% = tracking bug |
