---
name: signup-flow-cro
description: "Use when optimizing signup, registration, account creation, or trial activation flows. Also use when the user mentions signup conversions, registration friction, signup form optimization, free trial signup, reduce signup dropoff, or account creation flow. NEVER use for post-signup onboarding (use onboarding-cro), lead capture forms without account creation (use form-cro), or landing page optimization leading to signup (use page-cro)."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Signup Flow CRO

Reduces registration friction and increases completion rates by eliminating unnecessary fields, optimizing form architecture, and removing trust barriers.

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Field reduction, form architecture, social auth, trust signals, error handling, measurement | Always (auto-loaded) |
| browser-autofill-mechanics.md | How Chrome/Safari/Firefox autofill works, autocomplete attribute mapping, password manager integration, mobile keyboard/autofill behavior, autofill audit checklist | When diagnosing silent form abandonment, autofill not pre-populating, password managers failing to save credentials, or mobile keyboard issues |
| identity-provider-gotchas.md | OAuth redirect failures, Google One Tap vs traditional OAuth, Apple Sign-In requirements, Microsoft/Azure AD tenant restrictions, GitHub email gotchas, email collision handling, provider downtime | When implementing social auth, diagnosing OAuth redirect failures, or troubleshooting why social signup isn't converting |
| signup-analytics-experimentation.md | Field-level tracking events, abandonment detection, funnel decomposition, A/B test sample sizes, sequential testing, cohort analysis, signals that mislead, privacy compliance | When setting up signup measurement, planning A/B tests on registration forms, or interpreting signup conversion data |

## Scope Boundary

| This Skill Handles | Defer To |
|---|---|
| Signup form fields, layout, auth methods | form-cro (non-signup lead capture forms) |
| Registration completion rate optimization | page-cro (landing page leading to signup) |
| Trust signals and error handling on signup | onboarding-cro (post-signup activation) |
| Social auth selection and placement | security-best-practices (OAuth implementation security) |
| Signup A/B testing and analytics | ab-test-setup (general experimentation framework) |

## Assessment Procedure

1. **Classify the flow type**: Free trial, freemium, paid account, waitlist, B2B vs B2C. Each has different optimal field counts and trust requirements.
2. **Audit current fields**: For each field, answer: "Can the user access the product without this data?" If yes, defer it to post-signup progressive profiling.
3. **Map the drop-off**: Identify where users abandon -- form start rate, field-level drop-off, submit error rate. If no analytics exist, instrument before optimizing.
4. **Evaluate trust signals**: Check for missing "no credit card required" messaging, social proof, privacy assurances, and clear post-signup expectations.
5. **Test mobile experience**: Verify touch targets (44px+), keyboard types, autofill support, and single-column layout on actual devices.

## Field Reduction Decision Table

Every field reduces conversion. Apply this filter to each field in the current signup form.

| Field | Keep If | Defer If | Cut If |
|---|---|---|---|
| Email | Always keep -- required for account identity | -- | -- |
| Password | Keep for email-based auth | Consider passwordless (magic link) for low-friction flows | SSO-only products |
| Full name | Used for immediate personalization (greeting, profile) | Only used in billing or settings -- collect later | Never displayed to user before onboarding |
| First/Last split | Legal/compliance requires separate fields | -- | No compliance need -- use single "Name" field (fewer keystrokes) |
| Company name | Required for workspace/tenant creation | Can be inferred from email domain or asked during onboarding | B2C products |
| Phone number | Required for SMS verification or calling leads | Only used for marketing -- collect during onboarding | No clear product or compliance need |
| Role/title | Determines product experience at signup (different dashboards) | Used only for segmentation -- collect via in-app survey | Never influences the product experience |
| Use case question | Determines initial template/setup | Used only for analytics | Adds friction without personalizing anything |

**Benchmark**: Every field beyond email + password reduces completion by 5-10%. Three fields is the sweet spot for most B2C; five fields maximum for B2B.

## Single-Step vs Multi-Step Decision

| Signal | Use Single-Step | Use Multi-Step |
|---|---|---|
| Total fields needed | 3 or fewer | 4 or more |
| Field types | All similar (text inputs) | Mixed (text + dropdowns + selections) |
| User intent level | High (from ads, waitlist, pricing page) | Variable (from blog, organic, social) |
| Business model | B2C, freemium, simple signup | B2B, enterprise, needs segmentation |
| Data urgency | All data needed before product access | Some data can wait |

**Multi-step rules**: Lead with the easiest fields (email, name). Put harder questions after psychological commitment (they already started). Show progress indicator. Save progress on every step (no data loss on refresh). Allow back navigation.

**Progressive commitment pattern**: Step 1 = email only (lowest barrier). Step 2 = password + name. Step 3 = optional customization questions.

## Social Auth Strategy

| Audience | Primary Auth Options | Rationale |
|---|---|---|
| B2C general | Google, Apple | Highest adoption; Apple required for iOS apps with social auth |
| B2B SaaS | Google, Microsoft, SSO/SAML | Enterprise users expect SSO; Google covers SMB |
| Developer tools | GitHub, Google | Developers prefer GitHub identity |
| Consumer apps | Google, Apple, Facebook | Facebook still dominant for social/gaming |

**Placement rule**: Social auth buttons above the email form when social signup rate > 30%. Below the form when email is primary. Never hide social auth behind a "More options" toggle -- it kills adoption.

## Trust Signal Placement

| Trust Signal | Where to Place | When to Use |
|---|---|---|
| "No credit card required" | Directly above or below the CTA button | Free trial or freemium -- always include if true |
| "Free for X days" / "Free forever" | In the CTA button text or subheading | When commitment anxiety is the primary barrier |
| Privacy note ("We'll never share your email") | Below the email field | Cold traffic from ads or content |
| Security badges (SOC 2, GDPR) | Near form, not dominating visual hierarchy | Enterprise or regulated industry audiences |
| Social proof (customer count, logos, testimonial) | Adjacent to form, visible without scrolling | When brand recognition is low |
| "Takes 30 seconds" | Above or inside the form header | Multi-step forms or when time perception is a barrier |

## Error Handling Rules

| Error Type | Bad Pattern | Good Pattern |
|---|---|---|
| Invalid email format | Show error only after form submit | Inline validation on field blur with specific message |
| Email already registered | "Error occurred" | "This email is already registered. Log in or reset password?" with direct links |
| Weak password | Show all rules after first failure | Show requirements upfront with real-time checkmarks as they type |
| Server error on submit | Clear entire form | Preserve all field values, show retry option, offer alternative (social auth) |
| General validation | Red text with no context | Focus cursor on problem field, explain what's wrong and how to fix it |

**Critical rule**: Never clear form data on error. Users who have to re-type abandon.

## Measurement Framework

| Metric | What It Tells You | Healthy Benchmark |
|---|---|---|
| Form start rate (landed -> started) | Is the page motivating enough to begin? | 40-60% |
| Field-level drop-off | Which specific fields cause abandonment? | <5% per field |
| Form completion rate (started -> submitted) | Overall form friction level | 60-80% (single-step), 40-60% (multi-step) |
| Time to complete | Is the form taking too long? | <30 seconds (single-step), <90 seconds (multi-step) |
| Error rate by field | Which fields cause confusion? | <10% per field |
| Social auth vs email ratio | Is social auth working? | Varies by audience -- track trend |
| Mobile vs desktop completion | Mobile-specific friction? | Mobile should be within 10% of desktop |

## Common Signup Patterns

| Business Type | Optimal Pattern | Post-Submit Experience |
|---|---|---|
| B2B SaaS trial | Email + Password (or Google SSO) -> Name + Company (optional role) | Straight into onboarding flow |
| B2C app | Google/Apple SSO OR email -> immediate product access | Profile completion deferred |
| Waitlist / early access | Email only (one field) -> optional use-case question | Confirmation + position number |
| E-commerce | Guest checkout default -> optional account creation post-purchase | Order confirmation |
| Developer tool | GitHub SSO -> immediate product access | First project setup wizard |

## Recommendation Confidence

Not all guidance above carries equal certainty. Override when your specific context demands it.

| Area | Confidence | Override When |
|---|---|---|
| Field reduction (fewer fields = higher completion) | HIGH | Compliance requires specific fields at registration (HIPAA patient intake, KYC identity verification). Even then, collect minimum at signup and complete during onboarding. |
| Social auth placement | MEDIUM | Your analytics show <5% social auth adoption after 60 days. Some B2B audiences actively distrust social login for business tools. Test removal if adoption is negligible. |
| Single-step vs multi-step threshold | MEDIUM | Multi-step can outperform single-step even at 3 fields if the fields are psychologically different (email vs role selection vs use-case). Test both if traffic allows. |
| Trust signal recommendations | LOW | Trust signal effectiveness varies dramatically by audience sophistication. Enterprise buyers ignore "no credit card" (they expect it). Consumer audiences ignore SOC 2 badges (they don't know what it means). Match signals to audience. |
| Benchmark numbers (5-10% drop per field, 60-80% completion) | MEDIUM | Benchmarks assume general SaaS. Niche verticals with high intent (medical, legal, financial) tolerate more fields because the alternative is worse. Your actual data always beats benchmarks. |
| Error handling patterns | HIGH | Inline validation, preserved form data on error, and clear error messages are universally better. No known context where these hurt conversion. |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "We need all these fields for our CRM" | CRM data needs and signup conversion are opposing forces; collect minimum at signup, enrich via progressive profiling after the user is invested |
| "Our legal team requires these fields" | Challenge which fields are legally required vs organizationally preferred; most compliance needs can be met post-signup before first transaction |
| "Social auth is a nice-to-have, not priority" | Social auth reduces friction by 50-70% for supported audiences; it's often the single highest-impact signup optimization |
| "We'll optimize the form later, let's ship" | Signup is the narrowest point in the funnel; every day with a suboptimal form compounds lost users who never return |
| "Our completion rate is fine at 30%" | Industry benchmarks for simple signups are 60-80%; a 30% rate means the form is actively repelling two-thirds of interested users |
| "Mobile users will figure it out" | Mobile users have less patience, smaller screens, and higher abandonment rates; mobile optimization is not optional |

## Red Flags

- Signup form with more than 5 visible fields on a single step
- No social auth options on a consumer-facing product
- Password field that disables paste (breaks password managers)
- Email confirmation field (second email input) -- adds friction, catches almost no typos
- Form that clears all data on submission error
- No inline validation -- all errors shown only after submit
- "Create Account" as CTA text when "Start Free Trial" or value-oriented copy would reduce commitment anxiety
- No measurement instrumentation on any form field (flying blind)

## NEVER

- Add a CAPTCHA to the signup form without measuring its impact on completion rate -- CAPTCHAs reduce conversion 10-40% and should only be used when bot abuse is proven
- Require email verification before allowing any product access -- let users explore while verification is pending
- Use placeholder text as field labels -- labels disappear when typing, causing confusion and accessibility failures
- Collect credit card information for a free trial unless there is a proven business case for it -- "no credit card required" is one of the strongest trust signals
- Skip mobile testing -- forms that work on desktop often fail on mobile due to keyboard types, touch targets, and viewport issues
