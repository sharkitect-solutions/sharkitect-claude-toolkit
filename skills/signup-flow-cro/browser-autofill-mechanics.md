# Browser Autofill & Password Manager Mechanics

Load when diagnosing why users abandon signup forms despite few fields, when autofill isn't pre-populating correctly, or when password managers fail to save/suggest credentials.

## How Browser Autofill Actually Works

Browsers use a combination of signals to decide what to autofill. Getting these wrong causes silent abandonment -- users expect autofill to work and leave when it doesn't.

### Autofill Signal Priority (Chrome/Safari/Firefox)

| Signal | Weight | What Browsers Check |
|---|---|---|
| `autocomplete` attribute | Highest | Explicit declaration: `autocomplete="email"`, `autocomplete="new-password"` |
| `name` attribute | High | Pattern matching: `name="email"`, `name="firstName"`, `name="phone"` |
| `id` attribute | Medium | Same pattern matching as `name` |
| `label` text | Medium | Visible label text associated with the field |
| `placeholder` text | Low | Last resort -- unreliable across browsers |
| Field position in form | Low | First text field often assumed to be name/email |

**Critical**: If `autocomplete` is missing or wrong, browsers guess. Guessing fails 15-30% of the time, causing wrong data in wrong fields. Users see their phone number in the email field and leave.

### Autocomplete Values That Matter for Signup

| Field | Correct Value | Common Mistakes |
|---|---|---|
| Email | `autocomplete="email"` | `autocomplete="off"` (browsers ignore this anyway since Chrome 34), `autocomplete="username"` (wrong for signup) |
| New password | `autocomplete="new-password"` | `autocomplete="password"` (triggers login autofill, not password generation), `autocomplete="off"` |
| First name | `autocomplete="given-name"` | `autocomplete="name"` (fills full name), `autocomplete="first-name"` (invalid) |
| Last name | `autocomplete="family-name"` | `autocomplete="last-name"` (invalid), `autocomplete="surname"` (invalid) |
| Phone | `autocomplete="tel"` | `autocomplete="phone"` (invalid), `autocomplete="telephone"` (invalid) |
| Company | `autocomplete="organization"` | No standard exists -- browsers won't autofill this reliably |

### The `autocomplete="off"` Myth

Developers add `autocomplete="off"` thinking it prevents autofill. Reality:
- Chrome has ignored `autocomplete="off"` on most fields since 2014 (Chromium issue #468153)
- Safari ignores it on login-related fields
- Firefox respects it only on non-credential fields
- Password managers ignore it entirely (1Password, Bitwarden, LastPass all override)

**What actually happens**: `autocomplete="off"` breaks the browser's ability to match the correct data to the correct field, causing WORSE autofill behavior (wrong data in wrong fields) rather than no autofill.

## Password Manager Integration

### How Password Managers Detect Signup vs Login

| Signal | Signup Detection | Login Detection |
|---|---|---|
| Number of password fields | 2 (password + confirm) = signup | 1 = login |
| `autocomplete="new-password"` | Triggers "Save new password" prompt | -- |
| `autocomplete="current-password"` | -- | Triggers credential fill |
| Form action URL | `/register`, `/signup`, `/create-account` | `/login`, `/signin`, `/auth` |
| Presence of name fields | Suggests signup | -- |
| Page title/heading | "Create account", "Sign up", "Register" | "Log in", "Sign in" |

### Password Manager Failure Modes

| Failure | Cause | Impact | Fix |
|---|---|---|---|
| Credential not saved after signup | Missing `autocomplete="new-password"` or form submitted via JS without standard form submission event | User can't log in next time, creates support ticket or abandons | Use `autocomplete="new-password"` AND ensure form fires `submit` event |
| Wrong credential suggested | Login and signup forms on same page or similar URL patterns | User fills login credentials into signup form | Separate login/signup to different URLs. Use distinct `autocomplete` values |
| Password generator not triggered | `autocomplete="off"` on password field, or `maxlength` too short | User creates weak password or abandons because they want manager to generate | Remove `autocomplete="off"`, set `maxlength` >= 64 |
| Autofill popover covers submit button | Autofill dropdown overlays form elements on mobile | User can't tap Submit, thinks form is broken | Add 48px+ margin below last field before CTA |

## Mobile-Specific Autofill Behavior

### Keyboard Type Mapping

| Field | `inputmode` | `type` | Effect on Mobile |
|---|---|---|---|
| Email | `inputmode="email"` | `type="email"` | Shows @ and .com keys; enables email autofill suggestions |
| Phone | `inputmode="tel"` | `type="tel"` | Shows numeric keypad; enables phone autofill |
| Password | -- | `type="password"` | Triggers password manager bar on iOS/Android |
| Verification code | `inputmode="numeric"` | `type="text"` | Shows number pad; iOS auto-reads SMS codes with `autocomplete="one-time-code"` |

### iOS-Specific Gotchas

- **Safari autofill bar**: Appears above keyboard. If form fields are positioned behind it, users can't see what they're typing. Test with actual iOS devices.
- **Keychain password generation**: Only triggers when `autocomplete="new-password"` is present AND the field is `type="password"`. Missing either = no generation prompt.
- **Contact autofill**: iOS suggests from Contacts app. If `autocomplete` attributes are wrong, it fills the wrong contact field (home phone into work phone, etc.).
- **SMS OTP autofill**: Requires `autocomplete="one-time-code"` on the input. Without it, users must manually switch to Messages, copy the code, switch back, and paste.

### Android-Specific Gotchas

- **Google Autofill service**: Pre-populates from Google account data. Works well with standard `autocomplete` values, breaks with custom attributes.
- **Samsung Internet**: Has its own autofill that sometimes conflicts with Google Autofill. Fields get double-filled or cleared.
- **WebView autofill**: Apps using WebView for signup often have broken autofill because WebView doesn't share the browser's credential store. Use Custom Tabs instead.

## Autofill Audit Checklist

Run this against any signup form before shipping:

| Check | How to Verify | Pass Criteria |
|---|---|---|
| Every field has explicit `autocomplete` | View source or DevTools | No field relies on browser guessing |
| `autocomplete="new-password"` on password | View source | Not `password`, not `off` |
| `type` matches field purpose | View source | Email = `email`, phone = `tel`, password = `password` |
| `inputmode` set for mobile | View source | Email = `email`, phone = `tel`, OTP = `numeric` |
| No `autocomplete="off"` anywhere | View source | Zero instances (use `autocomplete="new-password"` to differentiate signup) |
| Password `maxlength` >= 64 | View source | Allows password manager generated passwords |
| Form fires standard submit event | Test with 1Password/Bitwarden | Credential save prompt appears after successful submit |
| Autofill popover doesn't cover CTA | Test on iOS Safari + Android Chrome | Submit button visible with autofill dropdown open |
| SMS OTP field has `one-time-code` | Test with real SMS on iOS | Code auto-populates from SMS |
