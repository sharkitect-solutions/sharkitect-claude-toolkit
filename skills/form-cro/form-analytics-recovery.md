# Form Analytics & Abandonment Recovery

Load when setting up form tracking, diagnosing form performance with analytics, building abandonment recovery flows, or interpreting form conversion data.

## Field-Level Analytics Implementation

Page-level analytics ("form page had 500 views") are useless for form optimization. You need field-level granularity.

### Event Taxonomy for Forms

| Event | Fire When | Data to Capture | Insight |
|---|---|---|---|
| `form_view` | Form becomes visible (IntersectionObserver) | Form ID, page URL, device type, referral source | Form visibility rate -- if form is below fold, many visitors never see it |
| `form_start` | First field receives focus | Form ID, first field name, time since page load | Form engagement rate = form_start / form_view |
| `field_focus` | Any field receives focus | Field name, field position, timestamp | Field engagement sequence (do users fill fields in order?) |
| `field_complete` | Field has value AND loses focus | Field name, time in field, input method (typed/autofilled/pasted) | Per-field completion time. Autofilled fields taking >5s = UX problem |
| `field_error` | Validation error appears | Field name, error type, current value length | Error rate per field. >15% error rate = confusing requirement |
| `field_abandon` | Field focused then form abandoned without completing that field | Field name, time in field, fields completed before this one | THE key metric -- which field is the quit point |
| `form_submit` | Submit button clicked/form submitted | All field completion flags, total time, error count during session | Completion rate denominator |
| `form_error` | Server rejects submission | Error type (validation, duplicate, server), HTTP status | Server-side failure rate |
| `form_success` | Submission confirmed successful | Submission ID, total duration, field count completed | Conversion event |

### Form Visibility Tracking

Many forms sit below the fold and never get seen. Track this before assuming "low conversion."

```
Form view rate = Users who scrolled to form / Page visitors
```

If form view rate is below 60%, the problem isn't the form -- it's the page layout. Fix the page (move form higher, add anchor CTA) before optimizing form fields.

**Implementation**: Use IntersectionObserver with `threshold: 0.5` (form is 50% visible). Fire `form_view` once per session per form.

### Input Method Detection

Distinguish typed, autofilled, and pasted inputs -- they have different optimization implications.

| Input Method | How to Detect | What It Means |
|---|---|---|
| Typed | `inputType === "insertText"` on `input` event | Normal interaction -- measure typing speed for UX insights |
| Autofilled | Chrome fires `animationstart` on autofilled fields (`:autofill` pseudo-class triggers) | High autofill rate = good autocomplete attributes. Low rate = fix attributes. |
| Pasted | `inputType === "insertFromPaste"` on `input` event | Pasted emails = user switching tabs. Pasted phone = copying from another source. |
| Voice input | `inputType === "insertFromDrop"` or speech-to-text (varies) | Mobile users using voice -- ensure fields accept natural language input |

### Abandonment Attribution

When a user leaves without submitting, attribute the abandonment to a specific field.

**Algorithm:**
1. Track the last field that received focus before the exit event
2. If that field has a validation error visible, attribute to "error frustration"
3. If that field is empty and was focused for <2s, attribute to "intimidation" (field scared them off)
4. If that field is empty and was focused for >10s, attribute to "confusion" (they didn't know what to enter)
5. If that field is filled and the next field was never focused, attribute to "next field intimidation"

**Exit detection**: Use `visibilitychange` event (most reliable cross-browser). `beforeunload` is unreliable on mobile. Fire the abandonment event with the full field state.

## Funnel Analysis for Forms

### Decomposed Conversion Rates

Don't track a single "form conversion rate." Break it into stages:

| Stage | Calculation | Healthy Benchmark | Low Signal |
|---|---|---|---|
| Page-to-view | Form views / Page visitors | 60-80% | Form below fold or page bouncing before scroll |
| View-to-start | Form starts / Form views | 40-60% | Form looks intimidating or value prop is weak |
| Start-to-complete | Submissions / Form starts | 50-70% (lead capture), 30-50% (long forms) | Field friction, errors, or trust deficit |
| Complete-to-success | Successful / Submissions | 95%+ | Server errors, duplicates, or rate limiting |

### Cohort Tracking

Track form performance by weekly cohort to detect trend changes:

| Week | Traffic Source | Form Views | Starts | Completions | Rate | Change |
|---|---|---|---|---|---|---|
| W1 (baseline) | Organic | 1,000 | 450 | 270 | 60% | -- |
| W2 (new CTA) | Organic | 1,050 | 480 | 310 | 64.6% | +4.6% |
| W3 (added field) | Organic | 980 | 420 | 210 | 50% | -14.6% |
| W3 (added field) | Paid | 500 | 300 | 195 | 65% | N/A |

W3 shows: the new field killed organic conversion (-14.6%) but paid traffic converts better (higher intent tolerates more fields). Decision depends on traffic mix and lead quality.

## Abandonment Recovery

### Partial Submission Capture

Capture form data progressively -- don't wait for submit.

| Strategy | How It Works | When to Use | Privacy Note |
|---|---|---|---|
| Save on field blur | Each field blur sends data to server | Always for multi-step forms | Only capture after consent. Email captured = you now have PII. |
| Save on step advance | Capture all fields on each step completion | Multi-step forms | Cleaner than per-field, but loses last-step data |
| Capture email first | Email field is step 1 or first field | Lead capture forms | Once you have email, you can follow up even if they abandon |
| Local storage backup | Save to localStorage, sync on next visit | Long application forms | No server dependency, but user must return on same browser |

### Email Recovery Sequences

When you have the email but the form was abandoned:

| Email | Timing | Subject Line Pattern | Content |
|---|---|---|---|
| Recovery 1 | 1 hour after abandonment | "Still interested in [thing they were requesting]?" | Direct link back to form with fields pre-filled from saved data |
| Recovery 2 | 24 hours | "Quick question about your [form type] request" | Ask if they had trouble, offer alternative contact method (chat, phone) |
| Recovery 3 | 72 hours | "[Social proof] -- join [X] others who [completed action]" | Social proof + simplified version (fewer fields or phone option) |

**Critical rules:**
- ONLY send recovery emails if user consented to email contact (GDPR)
- Pre-fill the form when they click back (this alone recovers 20-30% of abandonments)
- Maximum 3 recovery emails -- more is spam
- Include unsubscribe in every recovery email

### Form Re-engagement Without Email

When you don't have the email yet:

| Tactic | How | Expected Recovery Rate |
|---|---|---|
| Exit-intent popup | Trigger when cursor moves toward browser chrome | 5-10% of abandoners |
| Reduced-friction alternative | "Just want the basics? Enter email only" | 10-15% who were intimidated by full form |
| Chat widget trigger | Auto-open chat: "Need help with the form?" after 30s inactivity | 3-8% engage with chat |
| Retargeting ads | Pixel-based retargeting showing the value prop | 2-5% return rate, lower cost than new acquisition |

## Statistical Validity for Form Tests

### Sample Size Requirements

Form changes affect small percentage differences. You need more data than you think.

| Baseline Rate | Minimum Detectable Effect | Required Sample Per Variant |
|---|---|---|
| 60% completion | 5% relative (60% → 63%) | 5,500 |
| 60% completion | 10% relative (60% → 66%) | 1,400 |
| 30% completion | 10% relative (30% → 33%) | 5,600 |
| 30% completion | 20% relative (30% → 36%) | 1,500 |

**Reality check**: At 500 form submissions/month, you need 11+ months to detect a 5% improvement on a 60% baseline. For most forms, use before/after cohort comparison instead of formal A/B tests.

### Misleading Form Metrics

| Metric | Why It Misleads | Better Alternative |
|---|---|---|
| Overall completion rate | Hides device, source, and form-type differences | Segment by device + traffic source |
| "Average" time to complete | Skewed by outliers (tab left open for hours) | Use median time, or P75 |
| Total submissions | Doesn't account for traffic changes | Submission rate (submissions / unique form views) |
| Form "bounce rate" | Counts users who never intended to fill the form | Form start rate (focuses first field / form views) |
