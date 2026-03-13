# Core Web Vitals Impact on Conversion

Load when the user reports slow page load, poor mobile performance, unexplained conversion drops after site changes, or when diagnosing page CRO on pages with known performance issues. Also load when recommending CRO changes that add JavaScript, images, or third-party scripts. Do NOT load for pure copy/messaging optimization on pages with no performance complaints.

## The Performance-Conversion Link

Performance is a CRO lever. A slow page doesn't just frustrate users -- it measurably reduces conversion at predictable thresholds.

| Metric | What It Measures | Conversion Impact (Quantified) |
|---|---|---|
| **LCP** (Largest Contentful Paint) | Time until the largest visible element renders | Every 100ms of LCP above 2.5s costs ~0.3% conversion rate (Deloitte/Google 2020, confirmed by Vodafone 2021: 31% improvement in LCP = 8% more sales). Below 2.5s: no measurable penalty. Above 4.0s: bounce rate increases 32%. |
| **INP** (Interaction to Next Paint) | Delay between user input and visual response | INP >200ms: users perceive "lag" and hesitate on subsequent interactions. INP >500ms: 15-20% of users do NOT click the CTA a second time after experiencing one slow interaction. redBus found 72% increase in sales after fixing INP from 600ms to 180ms. |
| **CLS** (Cumulative Layout Shift) | Visual stability -- how much the page "jumps" | CLS >0.1: users misclick 12% more often (Google UX research 2023). CLS >0.25: "rage quit" behavior -- user clicks CTA, layout shifts, user clicks wrong element, user leaves. Yahoo Japan: reducing CLS by 0.2 = 15% reduction in page abandonment. |
| **FCP** (First Contentful Paint) | Time until first visible content appears | FCP >1.8s: users begin to doubt the page is loading. FCP >3.0s: 53% of mobile users abandon (Google 2018, still validated). FCP is the "did anything happen?" threshold. |
| **TTFB** (Time to First Byte) | Server response time | TTFB >800ms: everything downstream is late. TTFB is the invisible ceiling -- no amount of frontend optimization fixes a slow server. CDN, edge caching, or server upgrade required. |

## CRO Recommendations That HURT Performance

Every CRO recommendation has a performance cost. Calculate before implementing.

| Common CRO Recommendation | Performance Cost | Mitigation |
|---|---|---|
| Add hero video (autoplay) | +2-8MB page weight, LCP delayed 1-3s | `loading="lazy"`, poster image for LCP, `preload` video only after first interaction. Or use an animated GIF preview with click-to-play |
| Add live chat widget (Intercom, Drift) | +200-500KB JS, INP degraded by 50-150ms | Load chat widget ONLY after 30s or scroll past fold. `requestIdleCallback` for non-blocking init. Never load on page load |
| Add social proof carousel (rotating testimonials) | CLS risk if height changes between slides, +50-100KB JS | Fixed-height container. CSS-only carousel if possible. Reserve explicit `height` in HTML |
| Add exit-intent popup | +30-100KB JS for popup library | Inline the popup HTML in page source, trigger with vanilla JS `mouseout`. Avoid loading OptinMonster/Sumo full library just for one popup |
| Add heatmap/analytics (Hotjar, FullStory) | +80-200KB JS, INP degraded 30-80ms | Load async, defer until after `onload`. Session recording is the expensive part -- disable on high-traffic pages unless actively analyzing |
| Add A/B testing script (Optimizely, VWO) | +50-150KB JS, CLS risk from DOM manipulation | Use server-side A/B testing when possible. Client-side A/B scripts that modify DOM after render cause CLS. Anti-flicker snippets add 100-300ms to FCP |
| Replace static image with interactive demo | +500KB-2MB JS depending on framework | Placeholder image for LCP, load interactive component on click or intersection. Never hydrate on page load |

## Performance Audit Before CRO Recommendations

Run this checklist BEFORE recommending CRO changes on any page:

| Check | Tool | Threshold | If Failing |
|---|---|---|---|
| LCP | PageSpeed Insights or Lighthouse | <2.5s (mobile) | Fix LCP before adding ANY new above-fold elements. New hero images, videos, or widgets will make it worse |
| INP | Chrome DevTools Performance panel or web-vitals JS | <200ms | Do not add JavaScript-heavy interactions (carousels, accordions, tabs) until INP is under control |
| CLS | PageSpeed Insights | <0.1 | Do not add dynamic content (testimonial rotators, A/B test DOM changes) until CLS is fixed |
| Total page weight | DevTools Network tab | <2MB on mobile (3G target) | Compress images, defer scripts, remove unused CSS before adding new assets |
| Third-party script count | DevTools Network tab, filter "3rd party" | <5 third-party domains | Each third-party script is a single point of failure AND a performance cost. Audit before adding another |

## Image Optimization (The Biggest LCP Lever)

Hero images are the #1 LCP element on marketing pages. Optimizing them has more conversion impact than most copy changes.

| Image Scenario | Optimal Format | Sizing Strategy | Expected LCP Improvement |
|---|---|---|---|
| Hero photo (above fold) | WebP with JPEG fallback, `<picture>` element | `srcset` with 3 breakpoints (480w, 1024w, 1920w). Width matches container, not viewport | 0.5-2.0s improvement vs unoptimized PNG |
| Product screenshots | WebP or AVIF | Exact pixel dimensions of display container. No CSS scaling from larger source | 0.3-1.0s improvement |
| Background gradients/patterns | CSS gradient or inline SVG | Zero image requests | Eliminates image LCP entirely |
| Logo bar (social proof) | Single SVG sprite or CSS-only | Combine all logos into one request or use inline SVG | Reduces requests from 6-12 to 1 |

**The preload trick for LCP**: `<link rel="preload" as="image" href="hero.webp" fetchpriority="high">` in `<head>` tells the browser to fetch the hero image BEFORE parsing CSS. This alone typically improves LCP by 200-500ms on image-heavy pages.

## Mobile Performance Reality

Mobile CRO is constrained by device performance in ways desktop is not:

| Factor | Desktop | Mobile | CRO Implication |
|---|---|---|---|
| CPU speed | 4-8x faster | Baseline | JavaScript-heavy interactions (carousels, parallax, animations) that feel smooth on desktop may stutter on mid-range Android devices. Test on throttled Chrome (4x CPU slowdown) |
| Network | Typically 50-200Mbps | 4G: 10-30Mbps, 3G: 1-5Mbps | Every added asset (image, script, font) costs 3-10x more in load time on mobile. Budget strictly |
| Memory | 8-32GB | 2-6GB | Long pages with many images cause memory pressure on low-end devices. Lazy-load everything below fold |
| Viewport | 1200-1920px | 375-430px | Images served at desktop resolution on mobile waste 60-80% of bandwidth. Responsive images are mandatory, not optional |

**The 3G rule**: If your CRO recommendation doesn't work on a throttled 3G connection with 4x CPU slowdown, it doesn't work for 15-25% of your mobile audience (the segment most likely to bounce).
