# Browser API Mechanics for Popup Triggers

Load when implementing popup triggers in code, debugging why a popup doesn't fire on certain browsers/devices, optimizing popup display performance, or choosing between trigger implementation approaches. Also load when the user reports "exit intent doesn't work on mobile" or "popup causes layout shift." Do NOT load for popup copy, design, or A/B testing strategy.

## Exit Intent Implementation: Cross-Browser Reality

### Desktop: mouseout Event

```
// The standard approach
document.addEventListener('mouseout', (e) => {
  if (e.clientY < 0) showPopup();
});
```

| Browser | Behavior | Gotcha |
|---|---|---|
| Chrome | `mouseout` fires when cursor leaves the document area toward browser chrome | Fires on DevTools panel edge, bookmark bar, extensions. `clientY < 0` filters most but not all false positives |
| Firefox | Same as Chrome but `mouseout` ALSO fires when cursor moves over `<select>` dropdowns and `<iframe>` elements | Add check: `if (e.relatedTarget === null && e.clientY < 0)` to filter iframe/select false positives |
| Safari | `mouseout` is unreliable -- Safari does not consistently fire it when cursor leaves the window on macOS | Safari users represent 15-20% of desktop traffic. The "exit intent" feature functionally doesn't exist for them. Use time-based fallback |
| Edge | Same engine as Chrome (Chromium). Consistent behavior | No special handling needed |

**The Safari problem is worse than most CRO tools admit.** OptinMonster, Sumo, and similar tools silently fall back to scroll-triggered or time-based triggers on Safari. If the user expects true exit intent on all browsers, they need to know this doesn't exist.

### Mobile: Exit Intent Alternatives (Ranked by Reliability)

No mobile browser exposes cursor position. Every "mobile exit intent" is a proxy signal.

| Signal | API | Reliability | Implementation |
|---|---|---|---|
| **Page Visibility change** | `document.addEventListener('visibilitychange', ...)` | HIGH | Fires when user switches tabs, opens app switcher, or minimizes browser. Show popup when `document.visibilityState === 'visible'` (user returns). Cross-browser: works in all modern browsers including iOS Safari |
| **Scroll-up velocity** | `window.addEventListener('scroll', ...)` with velocity calculation | MEDIUM | Track scroll position at 100ms intervals. If `scrollY` decreases by >300px in <500ms, user is heading back to top (likely to leave). False positive rate: ~15% (users scrolling up to re-read) |
| **beforeunload event** | `window.addEventListener('beforeunload', ...)` | LOW | Fires when page is about to unload. BUT: you cannot show a custom popup in `beforeunload`. Browser shows its own generic dialog. Only useful for form-abandonment warnings, not marketing popups |
| **Back button (popstate)** | `window.addEventListener('popstate', ...)` | LOW | Fires when user hits back button. You can push a history state and intercept. BUT: this is hostile UX, violates user expectations, and some mobile browsers (Samsung Internet) block it. Use only for cart abandonment with high-value carts |

### The `beforeunload` Limitation

```
// This does NOT let you show a custom popup:
window.addEventListener('beforeunload', (e) => {
  e.preventDefault();        // Required in some browsers
  e.returnValue = '';        // Required in Chrome
  // Browser shows ITS OWN dialog, not yours
  // You cannot customize the message (Chrome removed that in 2016)
  // You cannot run async operations
  // You cannot redirect
});
```

**What `beforeunload` IS good for**: Form abandonment protection where the user has unsaved data. The browser's native dialog ("Leave site? Changes may not be saved") is appropriate here because the user has a genuine loss.

**What `beforeunload` is NOT good for**: Marketing popups, email capture, discount offers. The browser's generic dialog has no branding, no custom message (since Chrome 51), and users associate it with broken/malicious sites.

## IntersectionObserver for Scroll-Triggered Popups

`IntersectionObserver` is the performant way to trigger popups at scroll positions. It replaces scroll event listeners.

### Why IntersectionObserver Beats Scroll Events

| Approach | Performance | Battery Impact | Implementation Complexity |
|---|---|---|---|
| `scroll` event + throttle | Poor: fires every frame (60 times/sec), requires `getBoundingClientRect()` which triggers layout recalculation | High: continuous JS execution during scroll | Low (but deceptively so -- throttling is easy to get wrong) |
| `IntersectionObserver` | Excellent: browser-native, runs off main thread, no layout recalculation | Minimal: only fires callback when threshold is crossed | Moderate (API is slightly verbose but correct by design) |

### Scroll-Trigger Implementation Pattern

```
// Trigger popup when user scrolls 50% down the page
const sentinel = document.createElement('div');
sentinel.style.cssText = 'position:absolute;top:50%;width:1px;height:1px;pointer-events:none';
document.body.appendChild(sentinel);

const observer = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) {
    showPopup();
    observer.disconnect();  // Fire once only
  }
}, { threshold: 0 });

observer.observe(sentinel);
```

| Configuration | Use Case | `threshold` Value |
|---|---|---|
| Trigger when element enters viewport | Scroll-to-section popup | `0` (any pixel visible) |
| Trigger when element is fully visible | Ensure user has SEEN the section | `1.0` (100% visible) |
| Trigger at 50% visibility | Balance between "entered" and "seen" | `0.5` |
| Trigger with margin (before visible) | Pre-load popup HTML before user reaches trigger point | `rootMargin: '200px 0px'` (fires 200px before element enters viewport) |

### Browser Support

| Browser | IntersectionObserver Support |
|---|---|
| Chrome 51+ (2016) | Full support |
| Firefox 55+ (2017) | Full support |
| Safari 12.1+ (2019) | Full support |
| Edge 15+ (2017) | Full support |
| iOS Safari 12.2+ (2019) | Full support |
| Samsung Internet 5.0+ | Full support |

**Polyfill not needed** for any browser released after 2019. If the project must support IE11 or Safari <12.1, use the W3C polyfill (7KB).

## requestIdleCallback for Non-Blocking Popup Display

Popups that initialize during page load degrade INP and LCP. Use `requestIdleCallback` to defer popup initialization to idle time.

### The Problem

```
// BAD: Popup library loads and initializes on DOMContentLoaded
// This blocks main thread for 50-200ms during page load
document.addEventListener('DOMContentLoaded', () => {
  initPopupLibrary();      // Parses DOM, binds events, fetches popup HTML
  registerAllTriggers();    // Sets up scroll, time, exit listeners
});
```

### The Solution

```
// GOOD: Defer to idle time
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    initPopupLibrary();
    registerAllTriggers();
  }, { timeout: 5000 });  // Guarantee execution within 5s even under load
} else {
  // Safari fallback (Safari doesn't support requestIdleCallback)
  setTimeout(() => {
    initPopupLibrary();
    registerAllTriggers();
  }, 2000);
}
```

| API | Browser Support | Behavior |
|---|---|---|
| `requestIdleCallback` | Chrome, Firefox, Edge (NOT Safari) | Runs callback when main thread is idle. Guarantees no scroll jank or INP degradation |
| `setTimeout` fallback | All browsers | Runs after specified delay. May execute during busy periods. Use 2000ms+ to avoid load-time conflicts |
| `requestAnimationFrame` | All browsers | Runs before next paint. NOT idle -- this runs every frame. Wrong tool for deferred initialization |

**Safari's missing `requestIdleCallback`**: Safari (both macOS and iOS) does not implement `requestIdleCallback` as of Safari 18 (2025). The `setTimeout` fallback with 2000ms+ delay is the standard workaround. This affects 20-30% of users on most sites.

## Popup Display: Avoiding CLS

Popups that shift page content cause CLS (Cumulative Layout Shift), which hurts both UX and Google ranking.

| Popup Type | CLS Risk | Prevention |
|---|---|---|
| Center modal with backdrop | LOW (overlay, doesn't shift content) | Use `position: fixed` + `z-index`. Content stays in place behind the backdrop. Correct default for most popups |
| Top sticky bar | HIGH (pushes all content down) | Reserve space in the DOM from page load: `<div style="min-height: 48px">`. Or use `position: fixed` so it overlays instead of pushing |
| Bottom slide-in | LOW-MEDIUM | `position: fixed; bottom: 0`. No content shift unless it overlays the page's own fixed footer |
| Full-page takeover | ZERO CLS (but worst UX) | Entire viewport is replaced. No shift because nothing else is visible. But Google penalizes this on mobile pre-interaction |
| Inline form that expands | HIGH | When a user clicks "Subscribe" and a form expands inline, content below shifts. Set explicit `min-height` on the container BEFORE expansion |

### Animation Performance

| Animation | Performance | Recommendation |
|---|---|---|
| `opacity` transition (fade in) | EXCELLENT: composited, no layout/paint | Default choice for popup appearance |
| `transform: translateY()` (slide up) | EXCELLENT: composited, no layout/paint | Good for bottom slide-ins |
| `height` animation (expand) | POOR: triggers layout on every frame | Avoid. Use `transform: scaleY()` or `max-height` with overflow hidden |
| `top`/`left` animation | POOR: triggers layout on every frame | Use `transform: translate()` instead. Same visual result, 60fps performance |
| `backdrop-filter: blur()` | MEDIUM: expensive on low-end devices | Test on mid-range Android. Fall back to solid `rgba()` background if needed |
