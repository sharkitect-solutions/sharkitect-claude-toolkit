---
name: page-cro
description: "Use when the user wants to optimize, audit, or diagnose conversion problems on any marketing page -- homepage, landing page, pricing page, feature page, or blog post. Also use for 'CRO,' 'this page isn't converting,' 'improve conversions,' or 'why isn't this page working.' NEVER for signup/registration flows (signup-flow-cro), post-signup activation (onboarding-cro), form-specific optimization (form-cro), popup/modal optimization (popup-cro), general copy rewrites (copywriting), A/B test execution (ab-test-setup), or paywall/upgrade flows (paywall-upgrade-cro)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# Page Conversion Rate Optimization

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Diagnosis framework, message-market fit, above-fold hierarchy, CTA psychology, social proof, common mistakes | Always (auto-loaded) |
| core-web-vitals-conversion-impact.md | LCP/INP/CLS quantified conversion impact, CRO recommendations that hurt performance, image optimization for LCP, mobile performance constraints, performance audit checklist | Load when the page has known performance issues, when recommending changes that add JavaScript/images/third-party scripts, or when diagnosing unexplained conversion drops after site changes. Do NOT load for pure copy/messaging optimization on fast-loading pages. |
| statistical-rigor-for-cro.md | Sample size calculation, when to call a test, peeking problem quantified, Bayesian vs frequentist decision, multiple comparison corrections, test duration calendar effects | Load when the user wants to run an A/B test, asks if a result is significant, discusses sample size, or reports test results. Do NOT load for qualitative diagnosis or copy recommendations without testing. |
| behavioral-analytics-interpretation.md | Heatmap pattern recognition (6 click patterns), scroll depth benchmarks by page type, rage click diagnosis and volume benchmarks, session recording analysis framework, analytics tool selection | Load when the user has heatmap data, scroll depth reports, session recordings, rage click alerts, or wants to set up behavioral analytics for CRO. Do NOT load for pure copy optimization without behavioral data. |

## Scope Boundary

| Conversion Problem | This Skill | Not This Skill |
|---|---|---|
| Page has traffic but visitors don't convert | YES -- diagnose and fix | |
| Signup form has too many fields or high abandonment | | form-cro |
| User signed up but never activated | | onboarding-cro |
| Signup/registration flow multi-step issues | | signup-flow-cro |
| Popup timing, copy, or targeting | | popup-cro |
| Page needs complete copy rewrite from scratch | | copywriting |
| Setting up and analyzing A/B tests | | ab-test-setup |
| Paywall or upgrade flow optimization | | paywall-upgrade-cro |

---

## Diagnostic Procedure

Before responding to ANY page CRO request, execute these steps in order:

1. **Classify the page type** -- landing page, homepage, pricing, feature, or blog. Each has different benchmarks and levers.
2. **Identify the conversion metric** -- what counts as a conversion on this page? Form submit, CTA click, demo request, purchase? If the user hasn't defined this, ask.
3. **Match signal pattern** -- use the Page Type Diagnosis table below. Map the user's observed metrics (traffic, bounce, scroll, CTA clicks, form completion) to a diagnosis. If the user has no metrics, default to the 5-second test.
4. **Check traffic source** -- what sends visitors to this page? Paid search, social ads, organic, email? The traffic source determines visitor intent and sets the message-match requirement.
5. **Recommend in priority order** -- fix the diagnosed layer first. Never optimize downstream (CTA, social proof) while the upstream problem (headline, value prop) is broken.

## Page Type Diagnosis

| Signal Pattern | Diagnosis | Root Cause | Go To |
|---|---|---|---|
| High traffic, low conversion rate | Message-market mismatch | Value prop or targeting is wrong | Message-Market Fit Test |
| Low traffic, high conversion rate | Acquisition problem, not CRO | Page converts fine; not enough visitors | Defer to SEO/ads -- this skill can't help |
| High traffic, high bounce, low scroll depth | Above-fold failure | Headline or visual hierarchy repels visitors | Above-the-Fold Hierarchy Rules |
| Good scroll depth, low CTA click rate | CTA failure | Copy, placement, or commitment level wrong | CTA Psychology |
| High CTA clicks, low form completion | Form friction | Too many fields, unclear steps, trust gap | Defer to form-cro |
| High form starts, high abandonment mid-form | Trust or commitment failure | Asking too much too soon, missing reassurance | Social Proof Hierarchy + CTA commitment escalation |
| Returning visitors convert, new visitors don't | First-impression failure | Page assumes context visitors don't have | Message-Market Fit Test (5-second test) |

NEVER skip diagnosis. If the user says "optimize this page" without data, run the 5-second test first. Optimizing the wrong layer wastes effort.

---

## Message-Market Fit Test

This is the #1 CRO lever. No amount of button color testing fixes a broken value proposition.

**5-Second Test Protocol:**
Show page for 5 seconds, hide it, ask: "What does this do?" and "Who is it for?" If visitors can't answer BOTH correctly, the page fails at the most fundamental level. Fix this BEFORE touching anything else.

**Headline Audit:**

| Test | Question | Fail Signal | Fix |
|---|---|---|---|
| "So what?" | Can a visitor respond "so what?" and be justified? | Headline is vague or generic ("We help businesses grow") | Add specificity: who you help, what outcome, how fast |
| "Prove it" | Does the headline make a claim the page substantiates? | Unsubstantiated superlative ("The best platform for X") | Back with data, case study, or remove the claim |
| "Who cares?" | Does it name or imply the specific audience? | No audience signal -- could apply to anyone | Add segment language: "for SaaS teams", "for e-commerce brands" |

**Traffic Source Alignment:**
Ad copy, landing page headline, and CTA must tell ONE consistent story. Every mismatch costs conversions:
- Paid search: headline must echo the search query and ad copy
- Social ads: page must match the visual and emotional tone of the ad creative
- Email: landing page must deliver exactly what the subject line promised

**Intent Matching:**
- Informational intent ("what is X") needs educational content with soft CTA -- not a pricing page
- Transactional intent ("buy X") needs short-path conversion -- not a 2000-word explainer
- Navigational intent ("X login") needs the login page -- not a marketing page
- Mismatched intent is unfixable with CRO; fix the traffic source or create the right page

---

## Above-the-Fold Hierarchy Rules

**Visual Weight Allocation:**
- Headline: 40% of visual attention -- must be the dominant element
- Supporting visual (screenshot, illustration, or hero image): 30%
- Primary CTA: 20% -- prominent but subordinate to the headline
- Navigation: 10% -- functional, not competing

**Layout Pattern Decision:**
- F-pattern: text-heavy pages (feature pages, blogs)
- Z-pattern: conversion-focused pages (landing pages, pricing) -- default choice when unsure

**Hero Visual Decision:**
| Context | Best Visual | Why |
|---|---|---|
| SaaS product | Product screenshot or demo | Shows what they'll get |
| Service business | Customer outcome or results | Shows transformation |
| B2B complex product | Explainer video (< 90s) | Reduces cognitive load |
| AVOID always | Stock photos of people at laptops | Signals inauthenticity |

**Mobile Above-Fold Rule:**
One message. One CTA. Nothing else. Subheadline, trust badges, and secondary CTA go below the fold on mobile.

---

## CTA Psychology

**Commitment Escalation Ladder:**
Match CTA commitment level to visitor awareness stage:

| Visitor Stage | Appropriate CTA | Inappropriate CTA |
|---|---|---|
| Problem-unaware (cold traffic, blog) | "Learn how X works" / "Read the guide" | "Start free trial" (too much too soon) |
| Problem-aware (comparison, feature page) | "See how it works" / "Watch demo" | "Buy now" (not ready) |
| Solution-aware (pricing, case study) | "Start free trial" / "Get started free" | "Learn more" (too timid, loses momentum) |
| Decision-ready (pricing page, returning) | "Start free trial" / "Buy now" | "Schedule a call" (adds friction when ready to buy) |

**Value-First CTA Framing:**
"Get my free report" > "Download" > "Submit". "Start my free trial" > "Sign up" > "Register". ALWAYS state what they GET, not what they DO.

**Anxiety Reducers That Work:**
- "No credit card required" -- avg +28% lift on trial CTAs
- "Cancel anytime" -- avg +17% lift on subscription CTAs
- Specific time ("2-minute setup") beats vague "quick and easy" every time
- Place directly below/beside the CTA button, not in a footnote

**CTA Placement Rule:**
Place a CTA after every complete argument (benefit + proof). NOT just top and bottom.

**Secondary CTA Strategy:**
- Two CTAs ONLY when they serve distinct buyer types (self-serve vs. sales-assisted)
- If both target the same buyer, the secondary splits attention -- one CTA converts better than two

---

## Social Proof Hierarchy

Not all social proof is equal. Use the highest tier available.

| Tier | Type | Example | Conversion Impact |
|---|---|---|---|
| 1 (strongest) | Specific customer results with numbers | "Acme increased conversion 34% in 60 days" | Highest -- quantified proof eliminates skepticism |
| 2 | Named testimonials with photo and title | "Jane Smith, VP Marketing at Acme" + headshot | Strong -- human faces build trust |
| 3 | Logo bars of recognizable brands | Google, Stripe, Shopify logos | Moderate -- but ONLY if logos are recognizable |
| 4 (weakest) | Aggregate stats | "10,000+ customers" or "4.8/5 rating" | Weak alone -- use only as supplement to Tier 1-3 |

**Placement Rules:**
- Tier 1 near primary CTA (final reassurance before clicking)
- Tier 2 after benefit claims (validates them)
- Tier 3 early -- hero or just below (establishes credibility fast)
- Tier 4 in hero ONLY as last resort

**Logo Bar Warning:**
Unknown logos HURT more than they help. If visitors don't recognize any logo, the bar signals "our biggest customers are companies you've never heard of." Use only logos the TARGET AUDIENCE recognizes.

---

## Common CRO Mistakes

| Mistake | Quantified Impact | Why It Persists |
|---|---|---|
| **Testing button colors before fixing the value prop** | <1% lift from color changes vs 30-200% from value prop rewrites (WiderFunnel case studies) | Button tests are easy to run and feel productive |
| **Unknown logos in trust bar** | Unrecognized logos reduce trust scores 8-12% in eye-tracking studies (Baymard 2022) | Teams assume "more logos = more trust" without checking recognition |
| **Stock photos of people at laptops** | MarketingSherpa: authentic photos convert 35% higher than stock on landing pages | Stock is faster and cheaper than custom photography |
| **Long-form pages for low-consideration offers** | Free tool signups: short pages convert 2-3x higher than long-form (Unbounce 2023 benchmark) | "More info = more convincing" instinct is wrong for low-risk offers |
| **Removing nav on organic traffic pages** | Organic landing pages without nav: 15-25% higher bounce rate (HubSpot 2021) | Best practice confusion -- nav removal works for PPC, hurts organic |
| **Insufficient A/B test sample size** | Tests called with <500 conversions/variant have 40%+ false positive rate | Tools show "significant" too early; users trust the green checkmark |
| **Multiple equal-weight CTAs** | Each additional CTA above 1 reduces primary CTA clicks 13-17% (Wordstream) | Stakeholders each want their CTA represented |
| **Copying competitor pages** | Same messaging as competitors = commodity positioning, 0% differentiation | Competitors' pages are the most visible "inspiration" source |

---

## Rationalization Table

| Rationalization | Why It's Wrong |
|---|---|
| "We just need to A/B test more things" | Testing without a diagnosis is random; diagnose the conversion problem first |
| "Our bounce rate is high so the page is bad" | High bounce + high conversion = good page; bounce rate alone is meaningless without conversion context |
| "We need to add more information to the page" | More information often means more cognitive load; remove first, then add only what's missing |
| "The page works fine on desktop, mobile can wait" | 60%+ of traffic is mobile for most sites; "desktop-first" CRO ignores the majority |
| "We should follow what [big company] does" | Their page is optimized for THEIR traffic sources, audience, and brand awareness -- none of which you share |
| "Social proof isn't relevant for our product" | Every purchase involves trust; the question is which TYPE of proof fits, not whether proof matters |

## Red Flags

Reject or push back when:
1. User wants to "optimize" a page but has no conversion data -- insist on baseline metrics first
2. User asks to copy a competitor's page layout wholesale -- different context makes this counterproductive
3. User wants to A/B test with < 100 weekly conversions -- sample size is too small for meaningful results
4. Recommendations target visual polish (fonts, colors, spacing) while the value proposition is unclear
5. User conflates page CRO with funnel CRO -- this skill optimizes individual pages, not multi-step flows
6. User wants to remove ALL friction (forms, pricing, commitment language) -- some friction qualifies leads; zero friction attracts unqualified traffic
7. User asks for "best practices" without describing their specific page, audience, or goal -- generic advice is anti-CRO
8. Changes would require significant development work but user hasn't validated the hypothesis first -- test the concept before building it

## NEVER

1. Recommend changes without first diagnosing which conversion problem exists (use the Page Type Diagnosis table)
2. Suggest A/B tests without specifying the hypothesis, primary metric, and minimum sample size needed
3. Provide generic CRO checklists -- every recommendation must be specific to this page's diagnosed problem
4. Optimize a page in isolation from its traffic source -- ad-to-page message match is non-negotiable
5. Treat all pages the same regardless of visitor intent and awareness stage -- a pricing page visitor and a blog reader need completely different approaches
