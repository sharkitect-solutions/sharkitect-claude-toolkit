# Browser Form API Internals

Load when diagnosing why form validation behaves unexpectedly, when custom validation UX doesn't match native behavior, when autofill isn't working on non-signup forms, or when form submission handling breaks in specific browsers.

## Constraint Validation API

Browsers have a built-in validation system. Most form tools bypass it entirely and reimplement validation in JavaScript -- which creates inconsistencies and misses free UX.

### ValidityState Properties

Every form input has a `.validity` object with these boolean properties:

| Property | Triggers When | Default Browser Behavior | CRO Implication |
|---|---|---|---|
| `valueMissing` | `required` field is empty | Blocks submit, shows "Please fill out this field" | Native tooltip is ugly but FREE. Custom validation that replaces this must be equally fast. |
| `typeMismatch` | `type="email"` gets non-email input | "Please include an '@' in the email address" | Very loose check -- `a@b` passes. You still need server-side email validation. |
| `patternMismatch` | Input doesn't match `pattern` regex | "Please match the requested format" | Useless message -- always override with `title` attribute which browsers append to the tooltip. |
| `tooShort` / `tooLong` | Below `minlength` / above `maxlength` | Varies by browser | `maxlength` silently truncates in most browsers (users don't see an error, data gets cut). `minlength` only validates on submit. |
| `rangeUnderflow` / `rangeOverflow` | Below `min` / above `max` on number/date | Shows min/max in message | Good for budget or quantity fields on quote forms. |
| `stepMismatch` | Value doesn't match `step` increment | "Please enter a valid value" | Surprising on number fields with `step="1"` when user enters decimal. |
| `customError` | Set via `setCustomValidity()` | Shows whatever string you passed | YOUR escape hatch for async validation (email already exists, invalid postal code, etc.) |

### submit() vs requestSubmit()

| Method | Runs Validation | Fires submit Event | Use When |
|---|---|---|---|
| `form.submit()` | NO | NO | Almost never -- bypasses all validation AND prevents `submit` event listeners from firing |
| `form.requestSubmit()` | YES | YES | Always prefer this when triggering submit via JavaScript |
| `submitButton.click()` | YES | YES | Alternative to requestSubmit(), works in older browsers |

**Common bug**: AJAX form libraries using `form.submit()` silently bypass all HTML validation AND prevent analytics from capturing the submit event. If your form analytics show 0 submit events but users are successfully submitting, check for `.submit()` calls.

### formnovalidate Gotcha

The `formnovalidate` attribute on a button skips ALL validation for that submit. Common pattern: "Save as Draft" button with `formnovalidate` next to the real "Submit" button. Problem: if buttons are close together on mobile, users accidentally tap "Save as Draft" and get an incomplete submission with no validation.

### checkValidity() vs reportValidity()

| Method | Shows Error UI | Returns Boolean | Use Case |
|---|---|---|---|
| `checkValidity()` | No | Yes | Silent validation check (e.g., enable/disable submit button) |
| `reportValidity()` | Yes | Yes | Trigger visible error messages without submitting |

**Progressive validation pattern**: Call `checkValidity()` on blur to silently validate. Only call `reportValidity()` on submit attempt. This prevents showing errors while the user is still typing.

## Autofill for Non-Signup Forms

Signup forms get autofill attention; other forms are usually misconfigured.

### autocomplete Values for Common Form Types

| Form Type | Field | Correct autocomplete | Common Mistake |
|---|---|---|---|
| Contact form | Full name | `name` | Missing entirely -- browser guesses wrong |
| Contact form | Email | `email` | `autocomplete="off"` (browser ignores it anyway) |
| Contact form | Phone | `tel` | `phone` (invalid value, no autofill) |
| Quote request | Company | `organization` | Missing -- browser can't autofill company names |
| Quote request | Street address | `street-address` | `address` (invalid) or `address-line1` (only works for first line) |
| Quote request | City | `address-level2` | `city` (invalid -- browsers use the WHATWG spec names) |
| Quote request | State/Province | `address-level1` | `state` (invalid) |
| Quote request | Postal code | `postal-code` | `zip` or `zipcode` (invalid) |
| Quote request | Country | `country-name` (display) or `country` (code) | `country` when you want the display name |
| Checkout | Card number | `cc-number` | Missing -- payment autofill disabled |
| Checkout | Expiry | `cc-exp` | Split into `cc-exp-month` + `cc-exp-year` which breaks some autofill |
| Checkout | CVV | `cc-csc` | `cvv` or `cvc` (invalid) |
| Checkout | Cardholder | `cc-name` | `name` (fills personal name, not card name) |

### Address Autofill Specifics

Address autofill saves 30-60 seconds on quote/checkout forms. When it works, completion rates jump 15-25%. When it's broken, users don't know why fields aren't filling.

**Browser behavior differences:**
- **Chrome**: Fills address fields as a group. If ANY address field has wrong `autocomplete`, ALL address fields may be skipped.
- **Safari**: More aggressive -- fills individual fields even if siblings are misconfigured.
- **Firefox**: Requires `autocomplete` on each field independently. Won't group-fill.

**Testing**: Open Chrome DevTools > Application > Autofill to see what Chrome detects for each field. If a field shows "No autofill prediction," fix the `autocomplete` attribute.

## FormData API for Multi-Step Forms

Multi-step forms often lose data between steps. FormData provides a reliable extraction mechanism.

### Common Data Loss Patterns

| Pattern | Cause | Fix |
|---|---|---|
| Step 2 data overwrites step 1 | Each step creates a new FormData from the visible form | Merge: `new FormData(form)` into a persistent object on each step advance |
| File upload lost on back-navigation | File inputs clear when removed from DOM | Store File objects in JavaScript, re-attach on back navigation |
| Select/radio state lost | Dynamic step rendering recreates elements without setting values | Save to sessionStorage on each step, restore on render |
| Hidden fields not included | `disabled` fields are excluded from FormData | Use `readonly` instead of `disabled` if you need the value submitted |

### sessionStorage vs localStorage for Form State

| Storage | Use When | Why |
|---|---|---|
| `sessionStorage` | Almost always | Dies when tab closes -- prevents stale data in future sessions |
| `localStorage` | Long application forms (insurance, mortgage) where users may close and return | Persists across sessions but needs explicit expiry logic |
| In-memory (JS variable) | Simple 2-3 step forms | Fastest but lost on page refresh |

## Input Event Timing

Form analytics and validation depend on knowing when events fire. The sequence matters.

| Event | Fires When | Use For |
|---|---|---|
| `focus` | User clicks/tabs into field | Track form start, highlight field |
| `input` | Every keystroke, paste, autofill | Real-time character count, live preview |
| `change` | Field value changed AND field loses focus | Preferred for validation (fires once, not per keystroke) |
| `blur` | Field loses focus (regardless of value change) | Field abandonment tracking |
| `invalid` | Built-in validation fails on submit attempt | Counting validation failures per field |

**Autofill timing**: Browser autofill fires `input` events but NOT `change` events in Chrome. If your validation listens for `change` only, autofilled values won't trigger validation until the user manually interacts with the field.

**Paste detection**: `input` event has `inputType` property. `inputType === "insertFromPaste"` detects paste. Useful for analytics (pasted emails = power users, pasted phone = switching from another tab with the number).
