# Behavioral Analytics Interpretation

Load when the user has heatmap data, scroll depth reports, session recordings, rage click alerts, or click maps and wants to diagnose conversion problems from behavioral data. Also load when recommending analytics tool setup for CRO diagnosis. Do NOT load for pure copy/messaging optimization without behavioral data, or for A/B test statistical analysis (use statistical-rigor-for-cro.md).

## Heatmap Pattern Recognition

Heatmaps show WHERE attention goes, but interpreting them requires knowing what patterns mean.

### Click Heatmap Patterns

| Pattern | What You See | Diagnosis | Action |
|---|---|---|---|
| **Ghost clicks** | Dense click clusters on non-clickable elements (images, headings, bold text) | Users expect these elements to be interactive. Design communicates "click me" without delivering | Make the element clickable (link the image, make the heading a jump link) OR remove the visual affordance (un-bold, remove underline styling) |
| **CTA blindness** | Primary CTA has cold/no color on heatmap despite prominent visual placement | Banner blindness -- CTA looks like an ad or blends with decorative elements | Change CTA visual weight. Test contrasting color, increased size, or surrounding whitespace. Move CTA OUT of the "ad zone" (right sidebar, top banner area) |
| **False floor** | All clicks concentrated above a horizontal line; nothing below | Users think the page ends. A visual element (full-width image, color block, whitespace gap) creates a perceived "bottom" | Break the false floor: add a content teaser that bleeds below the line, add a scroll indicator, reduce the visual break |
| **Scatter pattern** | Clicks distributed randomly across the page with no concentration | No visual hierarchy. Users have no idea where to focus | Redesign visual hierarchy. One primary CTA, clear heading, reduce competing elements |
| **Navigation obsession** | Heavy clicks on nav bar, minimal engagement with page content | Page content failed to capture interest; users are looking for something else | Message-market mismatch. The page isn't what users expected from the traffic source. Fix the headline or fix the traffic source |
| **Footer concentration** | Unexpectedly dense clicks in footer area | Users scroll past all content looking for something specific (often contact info, pricing, legal) | Whatever they're seeking in the footer should be on the main page. Check footer links for clues about unmet information needs |

### Scroll Heatmap Interpretation

| Metric | Benchmark by Page Type | What Deviation Means |
|---|---|---|
| **50% scroll depth reached by** | Landing page: 60-70% of visitors | Below 50%: above-fold content fails to create enough interest to continue. Fix headline, hero, or opening proposition |
| | Blog post: 45-55% of visitors | Below 35%: content doesn't match the headline promise. Or the answer is in the first paragraph and users leave satisfied |
| | Product page: 55-65% of visitors | Below 45%: product information architecture fails. Key details may be buried too far down |
| | Pricing page: 70-80% of visitors | Below 60%: pricing is immediately disqualifying. Users see the first number and leave without exploring options |
| **Scroll to CTA placement** | CTA should be at or above the depth where 50%+ of visitors still remain | If CTA is placed at 80% scroll depth but only 30% of visitors reach 80%: 70% of visitors never see your CTA |
| **Scroll velocity changes** | Even velocity = consistent reading. Acceleration = skimming. Deceleration = engaged reading | Acceleration through a section: that content bores users. Cut it or move it. Deceleration: that content matters; amplify it |

### Scroll Depth Benchmarks (by page type)

| Page Type | Median Scroll Depth | "Good" Engagement | "Problem" Signal |
|---|---|---|---|
| Homepage | 55-65% | >70% see CTA section | <40% (hero and value prop fail) |
| Long-form landing page (2000+ words) | 40-50% | >50% reach testimonials | <30% (copy loses them early) |
| Blog post (800-1200 words) | 50-60% | >60% reach conclusion | <35% (title mismatch or slow intro) |
| Product page | 60-70% | >70% see pricing | <50% (product description fails) |
| Pricing page | 75-85% | >80% see FAQ/comparison | <65% (price shock, leave immediately) |
| Case study | 35-45% | >50% reach results section | <25% (company context bores them) |

## Rage Click Diagnosis

Rage clicks = 3+ rapid clicks on the same element within 1-2 seconds. They indicate frustration, not enthusiasm.

| Rage Click Location | Likely Cause | Fix Priority |
|---|---|---|
| **On a button/CTA** | Button doesn't respond. JavaScript error, slow server response, or button is visually disabled but appears active | CRITICAL. Check browser console for JS errors. Test button functionality on mobile + slow connections. This is lost revenue |
| **On an image** | User expects the image to expand, link, or provide more information | MEDIUM. Make image clickable (lightbox, link to detail page) or add hover state indicating "not clickable" |
| **On text that looks like a link** | Colored text, underlined text, or text near icons that appears interactive but isn't | HIGH. Either make it a link or remove the visual styling that implies interactivity |
| **In empty space near a form** | Form submission failed silently. User clicks around trying to submit | CRITICAL. Check form validation -- errors may be displaying below the fold or in a color that's invisible against the background |
| **On page load (before content renders)** | Page is slow. User clicks impatiently while waiting | HIGH. Performance issue. Check LCP and TTFB. See core-web-vitals-conversion-impact.md |
| **On a dropdown/select** | Dropdown doesn't open on first click (common on mobile) or opens but closes immediately | HIGH. Test form elements on actual mobile devices. CSS `select` styling often breaks native mobile behavior |

### Rage Click Volume Benchmarks

| Rage Click Rate | Assessment |
|---|---|
| <0.5% of sessions | Normal. Some rage clicks are accidental double-clicks |
| 0.5-2% of sessions | Worth investigating. Check the top 3 rage-clicked elements |
| 2-5% of sessions | Page has a functional problem. At least one critical element is broken or misleading |
| >5% of sessions | Emergency. The page is significantly broken for a user segment. Check by browser/device/OS immediately |

## Session Recording Analysis Framework

Watching recordings is time-consuming. Use this framework to extract insights efficiently.

### Which Sessions to Watch

| Priority | Session Type | What to Learn | Sample Size |
|---|---|---|---|
| 1 (highest) | Converted visitors | What path did successful visitors take? What did they read? What convinced them? | 10-15 recordings |
| 2 | Visitors who reached CTA but didn't click | What hesitation signals appear? Do they scroll up (reconsidering)? Do they hover without clicking? | 10-15 recordings |
| 3 | High-engagement non-converters (3+ min, 80%+ scroll, no conversion) | They were interested but something stopped them. Find the barrier | 10-15 recordings |
| 4 | Quick bouncers (<15s, <25% scroll) | Did the page even load? Did they land and immediately leave? First-impression failure | 5-10 recordings |

### Session Recording Red Flags

| Behavior | Meaning | CRO Implication |
|---|---|---|
| **Scroll-up after reaching CTA** | User wasn't convinced. Looking for more proof or information | Add social proof or objection handling BEFORE the CTA, not after |
| **Cursor hovering over CTA without clicking** (3+ seconds) | Decision anxiety. Wants to click but something holds them back | Add anxiety reducer near CTA: "No credit card required", money-back guarantee, "Cancel anytime" |
| **Rapid scrolling past a section** | Content irrelevant or too long | Cut or condense that section. If it's testimonials, they may be unconvincing -- replace with stronger proof |
| **Pinch-to-zoom on mobile** | Text too small or layout broken on their device | Check responsive design at that viewport width. Minimum body text: 16px |
| **Repeated form field correction** | Form labels unclear or validation too strict | Review error messages, placeholder text, and input masks. Overly strict validation (phone format, zip code) causes abandonment |
| **Tab switching then returning** | User comparing alternatives | They're in research mode. Add comparison content, competitor differentiation, or "why us" section to reduce the need to compare externally |

## Analytics Tool Selection for CRO

| Need | Best Tool | Free Alternative | Key Limitation |
|---|---|---|---|
| Click + scroll heatmaps | Hotjar ($) or Microsoft Clarity (free) | Microsoft Clarity | Clarity has no scroll depth % export. Hotjar throttles on free tier |
| Session recordings | Hotjar, FullStory ($$$), or Microsoft Clarity | Microsoft Clarity | Clarity masks inputs by default (good for privacy, bad for form analysis). FullStory has best search/filter |
| Rage click detection | FullStory (auto-detects) or Clarity (auto-labels) | Microsoft Clarity | Clarity's rage click detection has ~10% false positive rate (fast scrollers on mobile trigger it) |
| Form analytics (field-level drop-off) | Hotjar Forms or Zuko ($) | None reliable for free | Hotjar Forms requires paid plan. Zuko is the specialist tool (field-by-field timing, correction rate) |
| Funnel visualization | Mixpanel, Amplitude, or GA4 | GA4 Exploration funnels | GA4 funnel visualization is limited to 10 steps and retroactive funnel creation can miss events if not configured in advance |

**The minimum viable CRO analytics stack**: Microsoft Clarity (free: heatmaps + recordings + rage clicks) + GA4 (free: funnels + goals + traffic source data). This covers 80% of CRO diagnosis needs at zero cost.
