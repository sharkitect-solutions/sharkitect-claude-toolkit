---
name: form-cro
description: "Use when optimizing non-signup forms for conversion: lead capture forms, contact forms, demo request forms, application forms, survey forms, quote request forms, or checkout forms. Also for form field reduction decisions, multi-step form design, form error handling optimization, or form abandonment diagnosis. NEVER for signup/registration forms (use signup-flow-cro), popups containing forms (use popup-cro), page-level conversion optimization beyond the form (use page-cro), A/B test statistical setup (use ab-test-setup)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# Form CRO

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Form type diagnosis, field reduction, multi-step decisions, error handling, CTA psychology, abandonment diagnosis, mobile optimization | Always (auto-loaded) |
| browser-form-api-internals.md | Constraint Validation API, ValidityState properties, submit() vs requestSubmit(), autocomplete values for non-signup forms, address autofill specifics, FormData for multi-step state, input event timing | When form validation behaves unexpectedly, autofill isn't working on contact/quote/checkout forms, multi-step forms lose data between steps, or form submission handling breaks |
| form-accessibility-compliance.md | WCAG 2.2 form criteria, label association patterns, error announcement (aria-live, aria-invalid, aria-describedby), custom control accessibility (dropdown, checkbox, file upload), GDPR/CCPA/TCPA consent requirements | When auditing form accessibility, fixing screen reader issues, ensuring WCAG compliance, or implementing consent checkboxes for legal compliance |
| form-analytics-recovery.md | Field-level event taxonomy, form visibility tracking, input method detection, abandonment attribution algorithm, funnel decomposition, partial submission capture, email recovery sequences, re-engagement tactics, sample size requirements | When setting up form tracking, diagnosing form performance, building abandonment recovery flows, or determining statistical validity for form tests |

## Scope Boundary

| Area | This Skill | Other Skill |
|------|-----------|-------------|
| Lead capture, contact, demo, quote, application, survey, checkout forms | YES | -- |
| Signup / registration / account creation forms | NO | signup-flow-cro |
| Forms inside popups or modals | NO | popup-cro |
| Page-level conversion (hero, layout, trust sections) | NO | page-cro |
| A/B test sample size, duration, statistical significance | NO | ab-test-setup |
| Form field UX within a checkout flow | YES (field-level) | page-cro (flow-level) |

## Assessment Procedure

Before optimizing any form, work through this sequence. Skipping steps leads to prescribing solutions for the wrong problem.

1. **Classify the form type** using the Form Type Diagnosis table below. The form type determines which optimization lever matters most -- a lead capture form and a quote request form have fundamentally different constraints.
2. **Check if field-level analytics exist.** If no field-level data: instrument first, optimize second. Optimizing without knowing where users quit is guessing. Load `form-analytics-recovery.md` for implementation.
3. **Identify the highest-abandonment field.** This is your #1 fix target, not the first field in the form. A phone field with 30% drop-off matters more than a headline change.
4. **Run the enrichment-vs-ask analysis** for every field beyond email. Most qualifying data (company size, industry, revenue) can be obtained post-submit through enrichment APIs.
5. **Audit mobile separately.** Mobile form problems are different from desktop problems. Check input types, touch targets, autocomplete attributes, and keyboard behavior on actual devices.
6. **Check downstream dependencies** before removing any field. The form serves a business process (CRM routing, lead scoring, compliance). Confirm no automation breaks.

## Form Type Diagnosis

Match form type to primary optimization lever before doing anything else.

| Form Type | Primary Lever | Field Target | Key Tactic |
|-----------|--------------|-------------|------------|
| Lead capture (gated content) | Minimize fields | 1-2 (email default) | Value > effort -- the asset must justify every field |
| Contact form | Set expectations | 3-4 (name, email, message) | Show response time + offer alternatives (chat, phone) |
| Demo request | Qualify without killing conversion | 3-5 | Company size/role fields trade conversion for lead quality -- test the tradeoff |
| Quote/estimate | Reduce perceived complexity | 5-10 via multi-step | Start with easy fields, technical details in later steps |
| Application | Enable completion | 8-20+ via multi-step | Save progress mandatory, allow partial submit |
| Survey/feedback | Maintain engagement | Varies | One question per screen, decide incentive upfront |
| Checkout | Remove doubt | Minimal + payment | Trust signals critical, autofill everything, guest checkout default |

## Field Reduction Decision Framework

For each field on the form, classify it into one of four tiers:

| Tier | Definition | Action | Example |
|------|-----------|--------|---------|
| Must-have | Cannot fulfill form purpose without it | Keep | Email on a lead form |
| Nice-to-have | Improves follow-up quality | Make optional or move to step 2 | Company name on a content download |
| Enrichable | Obtainable from email domain, IP, Clearbit, ZoomInfo | Remove and enrich post-submit | Company size, industry, location |
| Vanity | Collected but never used in follow-up | Delete immediately | "How did you hear about us?" on a demo form |

**Quantified field cost:**
- Each field beyond 3 reduces completion by ~5-10%
- Phone number specifically costs 10-25% completion depending on form type (highest cost on lead capture, lowest on quote request)
- "Required" phone is 2-3x more damaging than "optional" phone

**Enrichment vs. ask decision:** If the field is available through enrichment APIs (Clearbit, ZoomInfo, IP geolocation) AND the form is top-of-funnel (lead capture, content download), enrich instead of asking. Exception: if enrichment data quality for your segment is below 70% accuracy, ask the field but make it optional.

## Single-Step vs Multi-Step Decision

| Field Count | Recommendation | Notes |
|-------------|---------------|-------|
| 1-4 fields | Single step always | Multi-step adds friction on short forms |
| 5-8 fields | Test both -- multi-step wins ~60% of the time | Split by topic (identity, then qualifying, then preferences) |
| 9+ fields | Multi-step mandatory | Single step with 9+ visible fields triggers immediate abandonment |

**Multi-step rules when splitting:**
- One topic per step (never mix contact info with qualifying questions)
- Progress indicator showing current step and total (step 2 of 3)
- Save state on each step advance (never lose data on back-navigation or refresh)
- Allow back navigation without data loss
- Easy fields first, sensitive/complex fields last

**Progressive commitment pattern:**
1. Low-friction entry: email only (or email + first name)
2. Qualifying: company, role, use case
3. Contact preferences: phone, preferred time, notes

This works because micro-commitments at step 1 create psychological investment. Completion rates for step 2+ are typically 60-80% once step 1 is submitted.

## Error Handling That Converts

| Pattern | Rule | Why |
|---------|------|-----|
| Validation timing | On blur (when user leaves field) | On-keystroke is aggressive and distracting. On-submit-only delays feedback too long |
| Error positioning | Inline, directly below the errored field | Summary banners at top are missed -- users scroll past them |
| Field preservation | NEVER clear valid fields when one field errors | Clearing the form is the #1 rage-quit trigger |
| Email typo detection | Suggest corrections for common misspellings: gmial.com, gmali.com, outlok.com, yaho.com | Catches 2-5% of submissions that would otherwise bounce |
| Phone formatting | Auto-format as user types, accept any reasonable input (spaces, dashes, dots, parens) | Rigid format requirements ("must be XXX-XXX-XXXX") cause 5-15% abandonment on phone fields |
| Required field indicator | Mark required fields with asterisk, OR mark optional fields with "(optional)" -- never both | Dual marking creates confusion about which convention applies |

## CTA Psychology for Forms

The submit button is the conversion moment. Generic "Submit" is the weakest possible CTA.

**Pattern: [Action verb] + [What they get]**

| Form Type | Weak CTA | Strong CTA |
|-----------|----------|------------|
| Lead capture | Submit | Get My Free Guide |
| Contact | Send | Send Message -- We Reply in 4 Hours |
| Demo request | Submit | Book My Demo |
| Quote | Submit Form | Get My Custom Quote |
| Application | Submit Application | Start My Application |

**Friction reducers near the button** -- place 1-2 of these directly below or beside the CTA:
- "No spam -- unsubscribe anytime" (lead capture)
- "Takes 30 seconds" (short forms)
- "No credit card required" (trial/demo)
- "We respond within [X] hours" (contact)
- Privacy link (not full policy text -- just the link)

**Loading state:** Disable button + show spinner on click. Prevents double-submit (which causes duplicate leads and confuses users).

## Form Abandonment Diagnosis

When a form underperforms, diagnose WHERE users quit before guessing WHY.

**Step 1 -- Get field-level data:**
- Which field has the highest exit rate? (This is your #1 fix target)
- What % start the form vs. submit? (Form start rate vs. completion rate)
- Desktop vs. mobile split? (Mobile forms fail differently)

**Common abandonment triggers by field position:**

| Quit Point | Likely Cause | Fix |
|-----------|-------------|-----|
| Before first field | Value proposition unclear or form looks too long | Reduce visible fields, strengthen headline above form |
| At phone number | Users don't want calls | Make optional, add "We won't call unless you ask" |
| At company/role fields | Feels like sales qualification | Move to step 2 or enrich post-submit |
| At free-text (message/comments) | Typing effort too high | Make optional, reduce character expectation |
| At submit button | Last-second trust doubt | Add trust signals, privacy note, expected response time |

**Fix priority:** Always fix the highest-abandonment field first, not the first field in the form. A phone field with 30% drop-off matters more than a name field with 2% drop-off.

## Mobile Form Optimization

These are not generic "responsive" rules -- they are specific decisions that affect conversion.

| Decision | Rule | Detail |
|----------|------|--------|
| Input types | Set correct HTML type for every field | type="email" triggers @ keyboard on iOS/Android. type="tel" triggers number pad. type="text" for names. Wrong type = extra taps |
| Touch targets | 48px minimum height (not 44px) | Google's updated recommendation is 48px. 44px is outdated Material Design v1 |
| Autocomplete attributes | Set on every applicable field | given-name, family-name, email, tel, organization, street-address. Browser autofill can complete forms in 2 taps |
| Layout | Single column only -- no exceptions | Two-column forms on mobile cause horizontal scroll or cramped fields. Both kill conversion |
| Sticky CTA | Pin submit button to bottom of viewport on long forms | Prevents users from not seeing the submit button after scrolling through fields |
| Keyboard management | Ensure form doesn't jump/resize when virtual keyboard appears | Test on iOS Safari specifically -- viewport behavior differs from Android Chrome |

## Recommendation Confidence

Not all guidance above carries equal certainty. Override when your specific context demands it.

| Area | Confidence | Override When |
|---|---|---|
| Field reduction (fewer fields = higher completion) | HIGH | Compliance requires fields at submission (HIPAA intake, financial KYC, government applications). Even then, separate required-by-law from required-by-policy -- policy fields can be deferred. |
| Error handling patterns (inline, preserve data, specific messages) | HIGH | No known context where these hurt conversion. The only variable is validation timing (blur vs submit) which can be tested. |
| Phone number cost (10-25% completion drop) | HIGH | Exception: outbound sales teams that call within 5 minutes of submission see 3-5x higher contact rates with phone. Run the math: does the higher contact rate offset the lost leads? |
| Single vs multi-step threshold | MEDIUM | Multi-step can outperform single-step even at 3-4 fields if the fields are psychologically different (email vs file upload vs scheduling). Test if traffic allows 1,400+ submissions per variant. |
| CTA copy recommendations | MEDIUM | CTA effectiveness varies by audience sophistication. Enterprise buyers may find "Get My Free Guide" too casual. Match tone to brand voice. The principle (verb + benefit) holds; the specific words don't. |
| Enrichment vs ask | LOW | Enrichment data quality varies dramatically by segment. B2B tech: 80-90% accuracy (Clearbit, ZoomInfo). B2B manufacturing: 40-60%. Local businesses: often <30%. Always validate enrichment accuracy for YOUR segment before removing fields. |

## Rationalization

| When the user says... | They actually need... |
|----------------------|----------------------|
| "Our form conversion rate is low" | Field-level abandonment data first, then targeted fixes -- not a form redesign |
| "We need to add more fields for lead quality" | Enrichment-vs-ask analysis -- most qualifying data can be obtained post-submit |
| "Let's make it multi-step" | Field count check first -- multi-step under 5 fields adds friction, not reduces it |
| "Phone number should be required" | Cost-benefit: required phone costs 10-25% completion. Is the phone call worth losing 1 in 5 leads? |
| "We want to A/B test the form" | One variable at a time. Field reduction first (highest impact), then CTA, then layout |
| "The form works fine on desktop" | Mobile audit -- mobile form completion rates are typically 30-50% lower than desktop |

## Red Flags

1. Form has 8+ visible fields on a single step with no multi-step split
2. Phone number is required on a top-of-funnel lead capture form
3. Submit button says "Submit" with no value-oriented CTA
4. No field-level analytics -- optimizing blind without knowing where users quit
5. Error messages clear the entire form or only appear in a top-of-page summary
6. Form asks for data that could be enriched (company size, industry, revenue) on a lead capture form
7. Mobile form has no autocomplete attributes set on any fields
8. "Required" and "optional" markers are both absent -- users guess which fields they can skip

## NEVER

1. NEVER remove a required field without confirming it is not used in downstream automation (CRM routing, lead scoring, compliance)
2. NEVER recommend CAPTCHA on a lead capture form without noting the 10-20% conversion cost -- use honeypot or invisible reCAPTCHA instead
3. NEVER suggest "just remove fields" without the enrichment-vs-ask analysis -- some removed fields destroy lead quality
4. NEVER prescribe a specific tool or platform (Typeform, HubSpot, Gravity Forms) -- recommend patterns, not products
5. NEVER optimize form fields without asking what happens to submissions downstream -- the form serves a business process, not itself
