# Identity Provider Gotchas

Load when implementing social auth (Google, Apple, GitHub, Microsoft), diagnosing OAuth redirect failures, or troubleshooting why social signup isn't converting.

## OAuth Redirect Flow Failure Modes

Social signup seems simple but the redirect flow has failure points that silently kill conversions.

### The Redirect Chain

```
User clicks "Sign up with Google"
  -> Your app redirects to Google consent screen
  -> User authorizes
  -> Google redirects back to your callback URL
  -> Your app creates account + session
  -> User lands in product
```

Each arrow is a failure point. Any break = user sees error page or gets stuck in a loop.

### Common Redirect Failures

| Failure | Cause | User Experience | Fix |
|---|---|---|---|
| Redirect URI mismatch | Callback URL in code doesn't exactly match what's registered in provider console (trailing slash, http vs https, www vs non-www) | Google shows "Error 400: redirect_uri_mismatch" | Register ALL variants in provider console. Use environment-specific configs. |
| State parameter lost | User opens signup in new tab, or browser extension strips query params | CSRF error on callback, signup fails silently | Store state in sessionStorage as backup. Log state mismatches for debugging. |
| Popup blocked | `window.open()` for OAuth popup blocked by browser | Nothing happens when user clicks social button. No error visible. | Use redirect flow as fallback. Never rely solely on popup flow. |
| Session cookie not set | SameSite=Strict on session cookie prevents setting during cross-origin redirect | User appears logged out after successful OAuth | Use SameSite=Lax for session cookies (allows top-level redirects). |
| Mobile deep link failure | OAuth redirect goes to browser instead of app on mobile | User authorized in browser but app doesn't know | Use Universal Links (iOS) / App Links (Android). Test with link validators. |
| Double account creation | Race condition: user clicks social auth twice, two callbacks arrive | Duplicate account, or second callback errors with "email already exists" | Use idempotency key (provider's unique user ID) as database constraint. |

## Google Sign-In Specifics

### Google One Tap vs Traditional OAuth

| Feature | Google One Tap | Traditional OAuth Redirect |
|---|---|---|
| UX | Floating prompt on page, no redirect | Full-page redirect to Google consent screen |
| Friction | Very low -- one click, no page change | Medium -- redirect, consent, redirect back |
| Conversion lift | 20-50% more signups vs traditional | Baseline |
| Implementation | `google.accounts.id.initialize()` + callback | Standard OAuth 2.0 flow |
| Gotcha: Dismissed behavior | If user dismisses 3x, One Tap stops showing for 2 hours (exponential backoff) | No backoff |
| Gotcha: iframe restrictions | Won't display if Content-Security-Policy blocks Google's iframe | Not iframe-based |
| Gotcha: incognito | One Tap requires existing Google session. In incognito, no session = no prompt | Works in incognito (redirects to Google login) |

### Google-Specific Failure Modes

| Issue | Symptom | Root Cause | Fix |
|---|---|---|---|
| "Accounts mismatch" | User sees wrong Google account pre-selected | Multiple Google accounts signed in, browser picks the wrong one | Add `login_hint` parameter with user's email if known. Use `prompt=select_account` for fresh selection. |
| Scopes changed after launch | Users who previously authorized are asked to consent again | Adding new OAuth scopes triggers re-consent for all users | Add scopes incrementally. Only request what you need at signup. Request additional scopes in-app when the user needs that feature. |
| Token expiry in signup flow | "Invalid token" error on callback | User took too long on consent screen (>10 min) or browser cached stale auth | Check token timestamp on callback. Re-initiate flow if expired. |
| Unverified email | Account created with unverified email | Google returns `email_verified: false` for some accounts (workspace accounts with unverified domains) | Always check `email_verified` claim. If false, require email verification before granting access. |

## Apple Sign In Specifics

### Apple Requirements (Mandatory for App Store)

If your iOS app offers ANY social sign-in (Google, Facebook, etc.), Apple **requires** you also offer "Sign in with Apple." Rejection is automatic if missing.

| Requirement | Detail | Common Violation |
|---|---|---|
| Must offer if other social auth exists | App Store Review Guideline 4.8 | Offering Google but not Apple |
| Must match visual prominence | Apple button must be same size/position as other social buttons | Apple button smaller or below fold |
| Must handle "Hide My Email" | Users can generate relay email (abc123@privaterelay.appleid.com) | App rejects relay email format, breaking signup |
| Must handle name only on first auth | Apple sends user's name ONLY on first authorization. If you miss it, you never get it again. | Not saving name on first callback, then user has no display name |

### Apple-Specific Failure Modes

| Issue | Cause | Impact | Fix |
|---|---|---|---|
| Name missing forever | Didn't capture `fullName` on first authorization event | User profile shows blank name. Cannot re-request. | Save name from first `ASAuthorizationAppleIDCredential` immediately. If missed: ask user to enter name manually in settings. |
| Relay email bounces | Using email provider that blocks relay domains | All transactional emails to Apple users fail silently | Whitelist `*.privaterelay.appleid.com` in your email provider. Test with real relay address. |
| Token revocation callback missed | User revoked app access in Apple ID settings | App still thinks user is authenticated | Implement Apple's server-to-server revocation notification endpoint. Check token validity on each session. |
| Web flow differences | Apple's web OAuth uses form_post response mode (not query) | Callback handler expects query params, gets POST body | Handle both GET (query) and POST (form_post) on callback endpoint. |

## Microsoft / Azure AD Specifics

### B2B Signup Gotchas

| Issue | Detail | Fix |
|---|---|---|
| Tenant restrictions | Enterprise Azure AD admin can block OAuth to unauthorized apps | Your app must be registered in customer's Azure AD tenant, OR use multi-tenant app registration. Provide admin consent URL in your docs. |
| Conditional Access policies | Enterprise may require MFA, compliant device, or specific network | These policies apply during your OAuth flow. If they fail, your signup fails with an opaque "access denied" error. Surface a clear message: "Your organization's security policy blocked this sign-in." |
| Guest accounts | Azure AD guest users have different claims structure | `oid` claim differs from native users. `email` may be in `preferred_username` instead of `mail` claim. Handle both. |

## GitHub Sign-In Specifics

| Gotcha | Detail | Fix |
|---|---|---|
| Private email | GitHub user can hide email. `user:email` scope returns primary email, but it may be a no-reply address | Check for `@users.noreply.github.com` pattern. If found, use the first verified, non-noreply email from the `GET /user/emails` endpoint. |
| Organization restrictions | GitHub org admins can restrict OAuth app access | If your app needs org data, user must explicitly grant org access during OAuth. Show which orgs are accessible in your onboarding. |
| Scope changes | Changing OAuth scopes requires user to re-authorize | Avoid scope creep. Request minimum scopes at signup (just `user:email`). Request additional scopes when the feature needs them. |

## Cross-Provider Edge Cases

### Email Collision Problem

User signs up with Google (john@gmail.com). Later tries to sign up with email/password using the same email.

| Strategy | Tradeoff |
|---|---|
| Block: "Email already registered via Google" | Clear but frustrating. User may not remember which provider they used. |
| Link: Auto-link social + email to same account | Convenient but security risk if email isn't verified from both sources. |
| Merge prompt: "Link this login method to your existing account?" | Best UX but requires the user to prove ownership (re-authenticate via original method). |

**Recommended**: On email collision, show the existing auth method and offer to link after re-authentication. Never silently merge accounts without verification -- this is an account takeover vector.

### Provider Downtime Handling

Google, Apple, and Microsoft auth services go down 2-5 times per year. When they do, your signup breaks entirely if social auth is the only option.

| Mitigation | Implementation |
|---|---|
| Always offer email/password as fallback | Even if social is primary, keep the email form accessible |
| Show provider status on error | "Google Sign-In is temporarily unavailable. Sign up with email instead." |
| Monitor provider status pages | Google: status.cloud.google.com, Apple: developer.apple.com/system-status |
| Cache tokens aggressively | Don't re-validate social tokens on every page load during an outage |
