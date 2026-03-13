---
name: scroll-experience
description: "Use when: user requests scroll-driven animations, parallax storytelling, scroll-triggered reveals, pinned/sticky scroll sections, horizontal scroll layouts, scroll progress indicators, cinematic web experiences, or scroll-based interactive narratives. NEVER for: static page layouts without scroll interaction (use frontend-design), general UI review or component audits (use ui-ux-pro-max), applying preset theme styles (use theme-factory), 3D scene construction (use 3d-web-experience)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# Scroll Experience

## Scope Boundary

| Request | This Skill | Defer To |
|---------|-----------|----------|
| Scroll-triggered animation, parallax, pin sections | YES | -- |
| Scroll progress indicators and scroll snapping | YES | -- |
| Horizontal scroll sections within vertical page | YES | -- |
| Static hero layout, grid, flexbox without scroll interaction | NO | frontend-design |
| General accessibility audit or UI component review | NO | ui-ux-pro-max |
| Applying an existing theme preset to a site | NO | theme-factory |
| WebGL/Three.js 3D scenes that happen to scroll | NO | 3d-web-experience |
| Page load animations unrelated to scroll position | NO | frontend-design |

## Library Selection Decision Matrix

Pick the FIRST row where all signals match the project.

| Signal | GSAP ScrollTrigger | Framer Motion | Lenis | CSS scroll-timeline |
|--------|-------------------|---------------|-------|-------------------|
| Framework | Any (vanilla, React, Vue, Svelte) | React/Next.js only | Any (scroll normalizer) | Any (no JS needed) |
| Complexity | Pin sections, horizontal scroll, sequenced timelines | Component-scoped scroll transforms | Smooth scroll feel only (pair with another for animations) | Single-element reveal, progress bar |
| Performance budget | ~45KB gzipped (core + ScrollTrigger) | Already in bundle if using Framer Motion | ~3KB gzipped | 0KB -- native CSS |
| Browser support | All modern + IE11 with polyfill | All modern | All modern | Chrome 115+, Firefox 110+, Safari 18+ (no IE) |
| Pin/scrub needed | YES -- best-in-class pin and scrub | Limited -- no native pin, requires workarounds | NO -- scroll feel only | NO -- animation-timeline only |
| React integration | Needs useLayoutEffect + cleanup patterns | Native -- useScroll, useTransform hooks | Wrap in useEffect | Native CSS, no React integration needed |
| License concern | Free for personal, paid for commercial SaaS with 100K+ monthly sessions | MIT | MIT | N/A |

Decision shortcut: If pinning or horizontal scroll is required, use GSAP. If React-only with simple transforms, use Framer Motion. If you just need smooth scroll feel, use Lenis. If reveals only and modern browsers guaranteed, use CSS scroll-timeline.

## Scroll Pattern Taxonomy

| Pattern | Description | When to Use | Complexity |
|---------|------------|-------------|-----------|
| Reveal | Elements fade/slide in as they enter viewport | Default for content-heavy pages | Low |
| Parallax | Layers move at different speeds creating depth | Hero sections, storytelling, editorial | Medium |
| Pin (sticky) | Element stays fixed while scroll content passes | Feature walkthroughs, before/after, step-by-step | Medium |
| Horizontal | Vertical scroll drives horizontal movement | Portfolios, timelines, product showcases | High |
| Progress | Visual indicator of scroll position or section completion | Long-form articles, multi-step guides | Low |
| Scrub | Animation position directly linked to scroll position (not triggered) | Interactive data viz, cinematic reveals | High |

Combination rule: Use at most 2 patterns per viewport. Mixing 3+ in one section causes cognitive overload and performance issues.

## Performance Budget Framework

| Metric | Desktop Target | Mobile Target | Measurement |
|--------|---------------|---------------|-------------|
| Scroll FPS | 60fps sustained | 60fps sustained (30fps acceptable for complex) | Chrome DevTools Performance panel |
| Total animation JS | < 80KB gzipped | < 50KB gzipped | Bundle analyzer |
| Animated elements per viewport | < 15 simultaneous | < 8 simultaneous | Manual count |
| Paint area per frame | < 40% of viewport | < 25% of viewport | DevTools Paint Flashing |
| Layout shifts during scroll | 0 | 0 | CLS in Lighthouse |
| will-change declarations | Only on actively animating elements | Same -- remove after animation completes | Audit in DevTools Layers |

Complexity tiers for animation budget:
- Tier 1 (Low): Opacity + transform only. No layout/paint triggers. Safe for any device.
- Tier 2 (Medium): Tier 1 + SVG path animation, clip-path. Test on mid-range mobile.
- Tier 3 (High): Tier 2 + filter effects, backdrop-filter, large parallax layers. Desktop-primary, degrade on mobile.

## Scroll Experience Anti-Pattern Catalog

| Anti-Pattern | Detection Signal | Impact | Fix |
|-------------|-----------------|--------|-----|
| Scroll Hijacking | Custom scroll velocity, wheel event preventDefault, overriding native scroll distance | Users lose control, accessibility broken, back button fails | Use scrub-linked animations instead -- enhance scroll, never replace it |
| Jank Waterfall | Animating width/height/top/left, triggering layout in scroll handler, no will-change | Sub-60fps, visible stutter, battery drain | Animate only transform + opacity, use requestAnimationFrame, batch reads/writes |
| Animation Fatigue | Every element animates on scroll, 5+ different animation types per page, animations last > 800ms | User stops noticing, content becomes secondary, bounce rate increases | Limit to 1-2 animation types, animate only key moments, keep durations 200-500ms |
| Mobile Neglect | No touch device testing, same animation count on mobile, no matchMedia breakpoints | Unusable on phones (majority of traffic), performance collapse | Reduce animated elements by 50%+ on mobile, disable parallax on < 768px if janky |
| Accessibility Blind Spot | No prefers-reduced-motion query, content invisible until animated, no keyboard scroll support | WCAG 2.1 failure, seizure risk, screen reader users see nothing | Always implement reduced-motion fallback that shows all content statically |
| Progress Confusion | Scroll indicator doesn't match actual position, multiple competing progress indicators | User doesn't know where they are or how much is left | One progress indicator per page, tied to documentElement scrollTop / scrollHeight |

## Accessibility Compliance for Scroll

Mandatory requirements (non-negotiable):

1. **prefers-reduced-motion**: Wrap ALL scroll animations in a media query check. Reduced-motion users see static content with no animation. This is not optional.
2. **Content without JS**: All content must be visible and readable if JS fails to load. Scroll animations are progressive enhancement.
3. **Keyboard navigation**: Tab order must follow visual order. Pinned sections must not trap focus. Horizontal scroll sections need keyboard arrow support.
4. **Screen readers**: Use aria-hidden on purely decorative animated elements. Ensure animated text content is in the DOM (not generated by animation).
5. **Vestibular disorders**: Large parallax movement (> 100px) and zoom effects can trigger nausea. Cap parallax displacement on mobile. Avoid auto-playing scroll-linked zoom.
6. **Focus management**: When scroll pins a section, do not auto-move focus. Let the user control focus with Tab/Shift+Tab.

## Mobile Degradation Strategy

| Desktop Feature | Mobile Action | Threshold |
|----------------|---------------|-----------|
| Multi-layer parallax (3+ layers) | Reduce to 2 layers or remove parallax entirely | < 768px or deviceMemory < 4GB |
| Horizontal scroll section | Convert to vertical stack or swipeable carousel | < 768px (touch scroll horizontal is awkward) |
| Pinned section with long scroll distance | Reduce pin scroll distance by 40% (thumb fatigue) | Touch device detected |
| Complex SVG path animations | Replace with simple opacity fade | < 480px or connection == slow-2g/2g |
| Scroll-linked video playback | Replace with static poster image + play button | connection == slow-2g/2g/3g |
| Background fixed attachment | Remove -- background-attachment: fixed is broken on iOS | iOS detected (any viewport) |

Detection: Use matchMedia for viewport, navigator.connection for network, navigator.deviceMemory for RAM. Apply degradation at initialization, not reactively during scroll.

## Rationalization

| Principle | Reason |
|-----------|--------|
| Enhance scroll, never replace it | Users expect native scroll behavior; overriding it causes disorientation and accessibility failure |
| Transform + opacity only | These are the only CSS properties that skip layout and paint, enabling 60fps on all devices |
| Mobile-first degradation | Mobile is majority traffic; designing desktop-first creates experiences most users never see correctly |
| One progress pattern per page | Multiple progress indicators compete for attention and confuse spatial orientation |
| Content visible without animation | Scroll animation is enhancement; if content depends on animation to be seen, JS failure hides the page |
| prefers-reduced-motion is mandatory | Legal accessibility requirement (WCAG 2.1 AA) and prevents vestibular disorder triggers |

## Red Flags

1. Using wheel event listeners with preventDefault to control scroll speed
2. Animating layout properties (width, height, top, left, margin) during scroll
3. More than 15 simultaneously animated elements in a single viewport
4. No prefers-reduced-motion media query anywhere in the scroll animation code
5. Parallax or pin effects that have never been tested on a real mobile device
6. Scroll-triggered content that is invisible/inaccessible when JavaScript is disabled
7. Using background-attachment: fixed on a page that must work on iOS Safari
8. Horizontal scroll section with no keyboard navigation support (arrow keys)

## NEVER

1. NEVER override native scroll velocity or distance with custom scroll hijacking
2. NEVER ship scroll animations without a prefers-reduced-motion fallback
3. NEVER animate width, height, top, left, or margin in a scroll handler -- transform and opacity only
4. NEVER assume mobile devices can handle the same animation density as desktop
5. NEVER hide meaningful content behind animations that require JS to reveal
