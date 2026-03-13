# Form Accessibility & Compliance

Load when auditing form accessibility, fixing screen reader issues with forms, ensuring WCAG compliance for form elements, or when form conversion is low for assistive technology users.

## WCAG Form Requirements (Quick Reference)

These are the specific WCAG 2.2 success criteria that apply to forms. Not all of WCAG -- only the form-relevant subset.

| Criterion | Level | Requirement | Common Violation |
|---|---|---|---|
| 1.3.1 Info & Relationships | A | Form controls must have programmatic labels | Using `placeholder` as the only label (disappears on focus) |
| 1.3.5 Identify Input Purpose | AA | Input purpose identifiable via `autocomplete` | Missing autocomplete attributes on name, email, phone, address |
| 2.1.1 Keyboard | A | All form controls operable via keyboard alone | Custom dropdowns that trap focus or don't respond to arrow keys |
| 2.4.3 Focus Order | A | Tab order matches visual order | CSS grid/flexbox reordering creates visual order != DOM order |
| 2.4.7 Focus Visible | AA | Focused elements must have visible indicator | `outline: none` in CSS with no replacement focus style |
| 3.3.1 Error Identification | A | Errors must be identified and described in text | Red border only (no text), or error shown only via color change |
| 3.3.2 Labels or Instructions | A | Labels or instructions provided for user input | Icon-only labels, or label visually present but not programmatically associated |
| 3.3.3 Error Suggestion | AA | When error is detected, provide correction suggestion | "Invalid input" instead of "Email must include @ and a domain" |
| 3.3.4 Error Prevention (Legal, Financial) | AA | Allow review, correction, reversal for legal/financial commitments | Checkout form with no confirmation step before charging |
| 3.3.8 Accessible Authentication | AA (NEW in 2.2) | No cognitive function test for authentication | CAPTCHA without accessible alternative |
| 4.1.2 Name, Role, Value | A | Custom controls expose name, role, state to assistive tech | Custom toggle that looks like a checkbox but has no ARIA role |

## Label Association Patterns

The #1 form accessibility failure is unlabeled fields. Screen readers announce "edit text" with no context.

### Correct Patterns

| Pattern | When to Use | Example |
|---|---|---|
| Explicit `<label for="">` | Default -- always use this | `<label for="email">Email</label><input id="email">` |
| Wrapping `<label>` | When you can't add `id` to input | `<label>Email <input type="email"></label>` |
| `aria-label` | Visually hidden label (e.g., search box with placeholder) | `<input aria-label="Search" placeholder="Search...">` |
| `aria-labelledby` | Label text exists elsewhere in the DOM | `<h3 id="contact">Contact Info</h3>...<input aria-labelledby="contact email-label">` |

### Anti-Patterns

| Pattern | Problem | Screen Reader Announces |
|---|---|---|
| `placeholder` as only label | Disappears on focus, not reliably read by all screen readers | Nothing or placeholder text (inconsistent) |
| `title` attribute as label | Not visible, inconsistently read | Sometimes reads title, sometimes ignores |
| Adjacent text without association | Visual proximity doesn't create programmatic relationship | "edit text" with no label |
| `aria-label` + visible `<label>` | Conflicting labels -- `aria-label` overrides visible label | aria-label text (visible label ignored) |

## Error Announcement

When validation errors appear, screen reader users may not know they exist unless you announce them.

### Error Announcement Patterns

| Technique | How It Works | When to Use |
|---|---|---|
| `aria-live="assertive"` on error container | Screen reader interrupts current task to read error | Form submission errors (summary) |
| `aria-live="polite"` on error container | Screen reader waits for pause, then reads error | Inline field validation (on blur) |
| `aria-describedby` linking field to error | Error read when field is focused | Always -- connects error to specific field |
| `aria-invalid="true"` on errored field | Announces "invalid" when field is focused | Always -- immediate state indicator |
| `role="alert"` on error element | Equivalent to `aria-live="assertive"` | One-time error injection into DOM |

**Recommended combination**: Set `aria-invalid="true"` on the field + add `aria-describedby` pointing to the error text + use `aria-live="polite"` on the error container. This covers focus-based discovery AND live announcement.

### Focus Management After Error

| Scenario | Correct Behavior | Common Mistake |
|---|---|---|
| Single field error (inline) | Move focus to errored field | Focus stays on submit button -- user doesn't know what failed |
| Multiple field errors (submit) | Move focus to first errored field OR error summary | Focus stays on submit button, errors visible but unannounced |
| Error summary at top of form | Summary links to each errored field, focus moves to summary | Summary exists but items aren't links -- users can't jump to errors |
| Dynamic form (AJAX submit) | Announce result: "Form submitted successfully" or move to errors | Nothing happens -- screen reader user doesn't know submission occurred |

## Custom Form Controls

When replacing native form elements with custom UI, the accessibility contract must be maintained.

### Custom Dropdown/Select

Native `<select>` is fully accessible out of the box. Custom dropdowns break unless ALL of these are implemented:

| Requirement | Implementation |
|---|---|
| Keyboard navigation | Arrow keys move through options, Enter/Space selects, Escape closes |
| Role announcement | `role="listbox"` on container, `role="option"` on each item |
| State communication | `aria-expanded` on trigger, `aria-selected` on active option |
| Focus management | Focus trapped within dropdown when open, returns to trigger on close |
| Type-ahead | Typing letters jumps to matching option (native select does this automatically) |

### Custom Checkbox/Radio

| Requirement | Implementation |
|---|---|
| Role | `role="checkbox"` or `role="radio"` |
| State | `aria-checked="true/false"` (checkbox) or `aria-checked="true"` on selected radio |
| Group | `role="radiogroup"` with `aria-labelledby` pointing to group label |
| Keyboard | Space toggles checkbox, Arrow keys move between radio options |

### Custom File Upload

| Requirement | Implementation |
|---|---|
| Trigger button | `role="button"` with descriptive label ("Upload resume PDF") |
| File list | `aria-live="polite"` region that announces "resume.pdf added" when file selected |
| Remove action | Each file has a remove button with label "Remove resume.pdf" |
| Drag and drop | Drop zone has `role="button"` with instructions. Keyboard users need the button trigger since drag-and-drop is mouse-only. |

## Legal Form Compliance

Beyond accessibility -- specific regulatory requirements that affect form design.

| Regulation | Applies To | Form Requirement |
|---|---|---|
| GDPR Article 7 | EU users | Consent checkboxes must be unchecked by default. Pre-checked consent boxes are illegal. |
| GDPR Article 13 | EU users | Privacy notice must be accessible before form submission (link is sufficient). |
| CCPA | California users | "Do Not Sell My Personal Information" link must be accessible from any page collecting data. |
| CAN-SPAM | Email collection (US) | Must disclose how email will be used. "We'll send you marketing emails" is required if true. |
| TCPA | Phone collection (US) | Express written consent required before calling/texting collected phone numbers. Checkbox with disclosure text. |
| ADA Title III | US websites (case law evolving) | Forms must be accessible. No specific standard mandated, but WCAG 2.1 AA is the de facto benchmark. |
| EU Accessibility Act | EU (from June 2025) | All commercial websites must meet EN 301 549 (aligned with WCAG 2.1 AA). Applies to forms. |

### Consent Checkbox Implementation

| Element | Correct | Incorrect |
|---|---|---|
| Default state | Unchecked | Pre-checked (GDPR violation) |
| Label text | Specific: "I agree to receive marketing emails from [Company]" | Vague: "I agree to the terms" (bundled consent, GDPR violation) |
| Granularity | Separate checkboxes per purpose (marketing, analytics, third-party sharing) | Single checkbox for all purposes |
| Mandatory consent | NEVER tie service access to marketing consent | "You must agree to receive emails to download this guide" (GDPR violation: consent must be freely given) |
