---
name: accessibility-auditor
description: |
  WCAG compliance audits, ARIA implementation, screen reader testing, and accessibility remediation.
  TRIGGER: "accessibility", "a11y", "WCAG", "ARIA", "screen reader", "keyboard navigation",
  "ADA compliance", "Section 508", "color contrast", "alt text", "focus management",
  "assistive technology", "inclusive design", "accessibility audit"
  EXCLUDE: General UI/UX design (use ui-ux-pro-max), CSS styling without accessibility context, SEO optimization
---

# Accessibility Auditor

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/audit-methodology.md` | Running a full site audit, creating VPATs, sampling large sites, legal compliance prep | Quick single-component fix, ARIA pattern lookup |
| `references/aria-patterns.md` | Building custom widgets, implementing complex ARIA, fixing screen reader issues, focus management | Running automated scans, writing audit reports |
| `references/remediation-recipes.md` | Fixing specific WCAG violations, SPA accessibility, framework-specific patterns | Planning audits, ARIA role selection |

## Audit Routing

**What are you doing?**

- IF starting a new project --> Use the Design-Phase Checklist (below) to bake in accessibility from day one. Load `audit-methodology.md` for testing strategy.
- IF auditing an existing site --> Load `audit-methodology.md` for the 4-phase methodology, sampling strategy, and VPAT documentation.
- IF fixing specific violations --> Load `remediation-recipes.md` for issue-specific fix patterns organized by WCAG criterion.
- IF building custom components --> Load `aria-patterns.md` for correct widget patterns, focus management, and screen reader testing.
- IF preparing for legal compliance --> Load `audit-methodology.md` (legal section) for ADA/508/EAA requirements and "substantial compliance" thresholds.
- IF setting up CI testing --> Load `audit-methodology.md` (regression section) for axe-core integration and threshold configuration.

## WCAG 2.2 Conformance Levels

| Level | Meaning | Criteria Count | Legal Standard? | Key Additions in 2.2 |
|-------|---------|---------------|-----------------|----------------------|
| A | Minimum baseline | 32 | Rarely sufficient | Focus Not Obscured (Minimum) |
| AA | Industry/legal standard | 24 | ADA, 508, EN 301 549, EAA | Focus Appearance, Dragging Movements, Target Size (Minimum) |
| AAA | Enhanced accessibility | 28 | Never legally required as blanket target | -- |

Key insight: Courts and regulators reference WCAG 2.1 AA as the standard. WCAG 2.2 adds 9 new criteria (6 at AA). Sites claiming 2.1 compliance still need 2.2 updates for legal defensibility going forward.

## The 4-Phase Audit Methodology

| Phase | Method | Coverage | What It Catches |
|-------|--------|----------|-----------------|
| 1. Automated Scan | axe-core, Lighthouse, WAVE | ~30% of WCAG issues | Missing alt text, contrast failures, missing labels, broken ARIA |
| 2. Keyboard Navigation | Tab, Shift+Tab, Enter, Space, Esc, Arrows | ~20% additional | Focus traps, unreachable controls, missing skip links, tab order issues |
| 3. Screen Reader Testing | NVDA/JAWS (Win), VoiceOver (Mac/iOS), TalkBack (Android) | ~25% additional | Announcement gaps, reading order, live region failures, unlabeled regions |
| 4. Expert Manual Review | Cognitive walkthrough, motor simulation | ~25% remaining | Cognitive load, timing issues, animation triggers, touch target sizing |

Critical: No single phase catches everything. Organizations that stop at Phase 1 miss 70% of real-world barriers. The most impactful issues (screen reader incompatibility, keyboard traps, cognitive barriers) require Phases 2-4.

## Critical Issues Priority Matrix

| Issue | Impact | Legal Risk | Fix Difficulty | WCAG |
|-------|--------|------------|----------------|------|
| No keyboard access to interactive elements | Blocks motor-impaired users entirely | Critical | Medium | 2.1.1 A |
| Missing form labels | Screen readers cannot identify fields | Critical | Easy | 1.3.1 A |
| No alt text on informative images | Content invisible to blind users | High | Easy | 1.1.1 A |
| Color as only differentiator | Colorblind users lose information | High | Medium | 1.4.1 A |
| Missing page language declaration | Screen readers use wrong pronunciation | High | Trivial | 3.1.1 A |
| Insufficient color contrast | Low-vision users cannot read | High | Easy | 1.4.3 AA |
| No focus indicators | Keyboard users lose position | High | Easy | 2.4.7 AA |
| Missing heading hierarchy | Navigation impossible for screen readers | Medium | Easy | 1.3.1 A |
| Auto-playing media without controls | Cognitive/hearing disruption | Medium | Easy | 1.4.2 A |
| No skip navigation link | Keyboard users must tab through headers repeatedly | Medium | Easy | 2.4.1 A |

## Named Anti-Patterns

### "The ARIA Overloader"
Adding ARIA roles to elements that already have native semantics. `<button role="button">` is redundant. `<nav role="navigation">` is redundant. Worse: ARIA can override native semantics, creating conflicts. Rule: if a native HTML element does what you need, never add ARIA. First rule of ARIA: no ARIA is better than bad ARIA.

### "The Contrast Gambler"
Eyeballing color contrast instead of measuring with tools. The human eye cannot distinguish 4.2:1 from 4.8:1 -- but one fails AA and the other passes. Required ratios: 4.5:1 for normal text, 3:1 for large text (18px+ or 14px+ bold), 3:1 for UI components and graphical objects. Use WebAIM Contrast Checker or browser DevTools (Chrome: inspect element > color picker shows ratio).

### "The Div Button"
Using `<div onclick>` instead of `<button>`. A div has no keyboard support, no role, no focus, no form submission behavior. Adding `role="button" tabindex="0" onkeydown` recreates what `<button>` gives for free. The same pattern applies to `<span>` links vs `<a href>`, and `<div>` headings vs `<h1>-<h6>`.

### "The Placeholder Label"
Using placeholder text as the only form label. Problems: placeholder disappears on input (users forget what field is for), placeholder has insufficient contrast by spec (about 3.5:1), placeholder is not consistently announced by screen readers, placeholder does not trigger the label-click-to-focus behavior. Always use a visible `<label>` element.

### "The Focus Thief"
Removing focus indicators globally with `*:focus { outline: none }` or `* { outline: 0 }`. This makes keyboard navigation impossible -- users cannot see where they are on the page. Fix: use `:focus-visible` to show outlines only for keyboard users while hiding them for mouse clicks. Never remove outlines without providing a visible custom alternative.

### "The Accessibility Overlay"
Installing JavaScript overlay widgets (AccessiBe, UserWay, AudioEye, EqualWeb) that claim to auto-fix all accessibility issues. Reality: overlays cannot fix structural HTML problems, often break screen reader navigation, create new ARIA conflicts, and have been specifically cited in ADA lawsuits as insufficient remediation. The National Federation of the Blind has formally opposed overlays. Real accessibility requires fixing the source code.

### "The Tab Index Abuser"
Using positive tabindex values (`tabindex="5"`, `tabindex="100"`) to force tab order. This creates an unpredictable navigation sequence that differs from visual layout. Only three tabindex values are valid in practice: `0` (add to natural tab order), `-1` (programmatically focusable but not in tab order), and omitted (use element's default). Positive values are technically valid but universally harmful.

### "The Hidden-but-Not"
Using `display: none` or `visibility: hidden` on content intended for screen readers. Both properties hide content from ALL users including assistive technology. For screen-reader-only content, use the `.sr-only` CSS pattern (position: absolute, clip, overflow: hidden, 1px dimensions). Conversely, using `aria-hidden="true"` hides from screen readers but keeps content visible -- use for decorative icons, duplicate content.

## Screen Reader Testing Quick Reference

| Screen Reader | Platform | Browser Pairing | Launch | Key Commands |
|--------------|----------|-----------------|--------|--------------|
| NVDA | Windows | Firefox (primary), Chrome | Ctrl+Alt+N | Browse: arrows; Focus: Tab; Elements list: NVDA+F7; Read all: NVDA+Down |
| JAWS | Windows | Chrome (primary), Edge | Auto-starts | Browse: arrows; Focus: Tab; Headings: H; Landmarks: R; Forms: F |
| VoiceOver | macOS | Safari (primary) | Cmd+F5 | Navigate: VO+arrows; Rotor: VO+U; Read all: VO+A; Web rotor: VO+U |
| VoiceOver | iOS | Safari | Triple-click Home/Side | Swipe right: next; Swipe left: previous; Double-tap: activate |
| TalkBack | Android | Chrome | Volume keys (hold both 3s) | Swipe right: next; Swipe left: previous; Double-tap: activate |

**Minimum testing matrix:** Test with NVDA+Firefox AND VoiceOver+Safari. This covers the two largest screen reader+browser combinations and catches the widest range of rendering differences. Add JAWS+Chrome for enterprise or government projects.

**What to verify during screen reader testing:**
1. Page title is announced on load
2. Landmarks are discoverable (banner, navigation, main, contentinfo)
3. Headings create a navigable outline of the page
4. Form fields announce their labels, required state, and error messages
5. Dynamic content updates are announced via live regions
6. Custom widgets announce their role, state, and value changes
7. Images announce meaningful alt text; decorative images are silent
8. Tables announce row/column headers when navigating cells

## Semantic HTML Landmark Architecture

Every page must have these landmarks for screen reader navigation:

| Element | ARIA Equivalent | Rule | Count |
|---------|----------------|------|-------|
| `<header>` (top-level) | `role="banner"` | Site-wide header | Exactly 1 |
| `<nav>` | `role="navigation"` | Major navigation blocks | 1+ (label each with `aria-label`) |
| `<main>` | `role="main"` | Primary page content | Exactly 1 |
| `<aside>` | `role="complementary"` | Related but independent content | 0+ |
| `<footer>` (top-level) | `role="contentinfo"` | Site-wide footer | Exactly 1 |
| `<form>` with label | `role="form"` | Significant forms (not search) | 0+ |
| `<search>` (HTML5.2) | `role="search"` | Search functionality | 0+ |

**Multiple landmarks of same type:** When a page has multiple `<nav>` elements, each must have a unique `aria-label` (e.g., "Main navigation", "Footer navigation", "Breadcrumb"). Without labels, screen reader users hear "navigation" multiple times with no way to distinguish them.

**Nesting rule:** Landmarks should not be nested inside each other except: `<nav>` inside `<header>`, `<nav>` inside `<footer>`, any landmark inside `<main>`. Do not nest `<main>` inside `<main>` or `<header>` inside `<header>`.

## Cognitive Accessibility

WCAG covers cognitive accessibility partially, but expert auditors go further. These issues affect users with ADHD, autism, learning disabilities, anxiety disorders, and age-related cognitive decline -- collectively the largest disability group (15-20% of population).

**Cognitive load reduction:**
- Maximum 3-5 steps per task flow. If more steps are needed, show progress and allow saving.
- Consistent navigation placement across all pages (never move the menu).
- Predictable behavior: buttons that look the same should do the same thing. No surprise redirects, popups, or new tabs without warning.
- Error recovery: always allow undo. Never make destructive actions irreversible without confirmation.

**Reading and comprehension:**
- Use plain language. Target 8th-grade reading level for public-facing content.
- Break long text into short paragraphs (3-4 sentences maximum).
- Use bullet points and numbered lists instead of dense paragraphs.
- Provide definitions for jargon, abbreviations (first use: spell out with abbreviation in parentheses).

**Timing and animation:**
- `prefers-reduced-motion` media query: respect it. Disable parallax, auto-scrolling carousels, animated transitions.
- Session timeouts: warn 20 seconds before expiration, allow extension (WCAG 2.2.1 AA).
- Auto-updating content (tickers, feeds): provide pause/stop mechanism (WCAG 2.2.2 A).
- Flashing content: nothing flashes more than 3 times per second (WCAG 2.3.1 A) -- seizure risk.

**Memory and attention:**
- Do not rely on user remembering information from a previous page. Carry context forward.
- Form validation: show errors inline next to the field, not just in a summary at the top.
- Multi-step forms: show what was entered in previous steps and allow editing.

## Color Contrast Quick Reference

| Context | AA Ratio | AAA Ratio | Applies To |
|---------|----------|-----------|------------|
| Normal text (<18px, not bold) | 4.5:1 | 7:1 | Body copy, labels, error messages |
| Large text (18px+ or 14px+ bold) | 3:1 | 4.5:1 | Headings, large UI text |
| UI components | 3:1 | -- | Buttons borders, form field borders, icons |
| Non-text graphics | 3:1 | -- | Charts, infographics, meaningful icons |
| Disabled elements | Exempt | Exempt | Grayed-out buttons, inactive inputs |
| Logos/brand text | Exempt | Exempt | Company logos, purely decorative text |

Checking tools: Chrome DevTools color picker (shows ratio inline), WebAIM Contrast Checker, Colour Contrast Analyser (desktop app for non-web contexts), Stark (Figma plugin for design phase).

## Common ARIA Widget Patterns (Summary)

**Accordion**: `<button aria-expanded="true/false" aria-controls="panel-id">` controlling a `<div role="region" aria-labelledby="button-id">`. Toggle `aria-expanded` and `hidden` attribute on panel.

**Tabs**: `<div role="tablist">` containing `<button role="tab" aria-selected="true/false" aria-controls="panel-id">`. Panels use `role="tabpanel" aria-labelledby="tab-id"`. Arrow keys move between tabs; Tab moves into the panel. Use roving tabindex (-1 on inactive tabs, 0 on active).

**Modal Dialog**: `<div role="dialog" aria-modal="true" aria-labelledby="title-id">`. Trap focus inside. Restore focus to trigger on close. Close on Escape. Prevent background scroll. Add `aria-hidden="true"` to content behind dialog.

**Tooltip**: `<button aria-describedby="tooltip-id">` with `<div role="tooltip" id="tooltip-id">`. Show on focus AND hover. Dismiss on Escape. Never put interactive content in tooltips. Tooltip content must be perceivable for screen readers even before display.

**Combobox**: `<input role="combobox" aria-expanded="true/false" aria-autocomplete="list" aria-controls="listbox-id" aria-activedescendant="option-id">` with `<ul role="listbox">` containing `<li role="option">`. Arrow keys move highlight; Enter selects; Escape closes.

See `references/aria-patterns.md` for complete implementation details, focus management, and screen reader testing.

## Legal Landscape

| Regulation | Jurisdiction | Scope | Standard | Deadline |
|------------|-------------|-------|----------|----------|
| ADA Title III | USA | Public accommodations (websites included per DOJ) | WCAG 2.1 AA | Ongoing; DOJ rule April 2024 |
| Section 508 | USA | Federal agencies and contractors | WCAG 2.0 AA (EN 301 549 mapped) | In effect |
| EN 301 549 | EU | Public sector + procurement | WCAG 2.1 AA + extras | In effect |
| EAA (European Accessibility Act) | EU | Private sector digital services | WCAG 2.1 AA (expected) | June 28, 2025 |
| AODA | Ontario, Canada | Organizations with 50+ employees | WCAG 2.0 AA | In effect |
| DDA | UK | Service providers | WCAG 2.1 AA (common reference) | In effect |

Key trend: ADA demand letters targeting e-commerce and SaaS have tripled since 2020. The DOJ's April 2024 rule explicitly requires WCAG 2.1 AA for state/local government sites. EAA extends compliance to private companies serving EU customers starting June 2025.

## Design-Phase Checklist

Before writing any code, verify:
- [ ] Color palette meets 4.5:1 contrast for all text/background combinations
- [ ] Interactive targets are minimum 24x24 CSS pixels (WCAG 2.2 2.5.8 AA)
- [ ] Form designs include visible labels (not placeholder-only)
- [ ] Error states use text + icon, not color alone
- [ ] Focus states are designed (not just default browser outlines)
- [ ] Animation can be disabled (prefers-reduced-motion support planned)
- [ ] Content hierarchy uses real heading levels (not just visual size)
- [ ] Mobile touch targets are minimum 44x44 CSS pixels (iOS/Android guidelines)

## Automated Tool False Positives

| Tool Says | Reality | How to Verify |
|-----------|---------|---------------|
| "Image missing alt text" | Image may be decorative (correctly using `alt=""`) | Check if image conveys information. Decorative = empty alt is correct. |
| "Link text is not descriptive" | Link may be descriptive in context (e.g., table row) | Read surrounding text. `aria-label` or `aria-describedby` may provide context. |
| "Color contrast insufficient" | Text may be on a gradient or image background | Check actual rendered contrast at the specific overlap point. |
| "ARIA role not valid" | Tool may not recognize newer ARIA 1.2 roles | Verify against current WAI-ARIA spec, not tool's built-in list. |
| "Tab order is incorrect" | Visual order may intentionally differ from DOM order (rare but valid) | Test with keyboard. If flow makes sense contextually, it may be intentional. |

Rule of thumb: automated tools have a 20-30% false positive rate. Every finding must be manually verified before filing as a defect.
