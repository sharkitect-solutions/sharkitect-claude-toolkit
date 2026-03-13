# Mobile Onboarding Patterns

Load when optimizing mobile app onboarding, designing cross-platform onboarding experiences, or handling mobile-specific constraints like push permissions, deep links, and small-screen progressive disclosure.

## iOS vs Android Onboarding Differences

The same onboarding logic produces different outcomes on iOS and Android because of platform-level differences.

| Factor | iOS | Android | Impact on Onboarding |
|---|---|---|---|
| Push notification permission | One-shot prompt. Deny = must go to Settings manually. | Granted by default until Android 13. Android 13+ requires runtime permission. | iOS: delay push prompt until after first value moment. Android <13: no prompt needed. Android 13+: same strategy as iOS. |
| App review guidelines | Apple rejects onboarding that requires signup before showing value (Guideline 5.1.1). | Google Play less strict but discourages mandatory account creation for browsing. | Both: allow browsing/value preview before requiring account. iOS enforces this via review rejection. |
| Background processing | Limited by App Naps, background refresh budget | More permissive, but Doze mode limits | Don't rely on background sync completing during onboarding. Show explicit "syncing" state. |
| Biometric auth | Face ID / Touch ID. Requires explicit user opt-in. | Fingerprint / face unlock. BiometricPrompt API. | Offer biometric setup as a checklist item after account creation, not during. "Skip" must be prominent. |
| Deep link handling | Universal Links (requires apple-app-site-association file) | App Links (requires assetlinks.json) | Both: email onboarding links must deep link into the app if installed, web if not. Test both paths. |
| Screen sizes | Narrower range (iPhone SE to Pro Max). Safe area insets. | Massive range (320dp to tablets). Cutouts, nav bar differences. | Design onboarding for 360dp width minimum. Test on SE-sized device. Never rely on horizontal space. |

## Push Notification Permission Strategy

Push permissions are the most consequential single permission in mobile onboarding. Mis-timed prompts permanently lose the ability to re-engage users.

| Strategy | Implementation | When to Use |
|---|---|---|
| Pre-prompt (soft ask) | Show a custom in-app dialog explaining the benefit BEFORE triggering the OS prompt | Always on iOS. Converts 3-5x better than cold OS prompt because users who tap "No" on soft ask never see the OS prompt. |
| Post-value prompt | Trigger push permission after the user receives their first value moment | When the value moment is early (within first session). "Want to know when your report is ready? Enable notifications." |
| Contextual prompt | Show permission request inline when a specific feature needs it | When push is not central to the product. "Get notified when someone replies to your comment." |
| Deferred prompt | Don't ask during onboarding at all. Ask on 2nd or 3rd session. | When push is nice-to-have, not core. Users who return without push prompting are already engaged. |

**iOS-specific trap**: If you trigger the native permission dialog and the user denies it, you CANNOT ask again. The only recovery is directing them to Settings. This is why the soft pre-prompt pattern exists -- it filters out users who would deny, preserving the one-shot native prompt for users who have already mentally committed.

**Android 13+ change**: Runtime notification permission mirrors iOS behavior. Apps targeting Android 13+ must request POST_NOTIFICATIONS permission. The same soft pre-prompt strategy now applies to Android.

## Deep Link Onboarding Resumption

Users abandon onboarding and return via email links, push notifications, or shared links. The return path determines whether they resume or restart.

| Scenario | Expected Behavior | Common Failure |
|---|---|---|
| User left mid-onboarding, returns via email CTA | Resume at exact step they left, with prior data preserved | Full restart of onboarding. User sees the same first 3 steps again and gives up. |
| User completed onboarding, returns via email "get started" link | Go to main app, not onboarding | Trapped in onboarding flow despite completion. Feels broken. |
| User has app installed, clicks web link | Open app to relevant screen (not just home) | Opens app to home screen. User must navigate manually to the linked content. |
| User doesn't have app installed, clicks app link | Web fallback OR app store with deferred deep link | Broken link, or app store page with no memory of the intended destination after install. |

**Deferred deep linking**: When a user clicks a link, downloads the app, and opens it for the first time, the app should remember the original link destination. Implement via Branch, Firebase Dynamic Links (deprecated -- migrate to shorter alternatives), or custom clipboard-based solutions.

**Onboarding state persistence**: Store onboarding progress server-side (not just local storage). Users switch devices, reinstall apps, and clear data. If onboarding state is client-only, every reinstall restarts the experience.

## Small-Screen Progressive Disclosure

Mobile screens cannot show the same density of information as web onboarding. Every element competes for 360x640dp of attention.

| Web Onboarding Pattern | Mobile Adaptation | Why |
|---|---|---|
| Sidebar checklist (always visible) | Bottom sheet or collapsible header | Sidebar takes 30%+ of mobile width -- unusable. |
| Multi-column setup wizard | Single-column, one question per screen | Horizontal scrolling on mobile is disorienting. Vertical flow only. |
| Tooltip-based product tour | Coach marks (one at a time, tap to advance) | Tooltips obscure content on small screens. Coach marks dim everything except the target. |
| Inline empty state with CTA + illustration | Stacked: illustration -> 1-line copy -> CTA button | Horizontal layout won't fit. Vertical stacking with large touch target CTA. |
| Progress bar at top of page | Progress dots or step counter (e.g., "2 of 4") | Full progress bars waste vertical space. Dots are compact. |

**Touch targets**: Every interactive element in onboarding must be at least 44x44pt (iOS) or 48x48dp (Android). Undersized buttons cause accidental taps and rage quits.

**Keyboard management**: When onboarding requires text input, the keyboard covers 40-50% of the screen. Ensure the active input field scrolls above the keyboard. Auto-advance to next field on completion. Show "Next" button above keyboard, not below it.

## App Store Onboarding (Pre-Install)

Onboarding starts before the user opens the app. App store screenshots and preview videos set expectations that the in-app experience must match.

| Element | Impact on Onboarding | Recommendation |
|---|---|---|
| Screenshot #1 | Sets primary value proposition expectation | Show the core value screen (dashboard with data, completed workflow). NOT the login page. |
| Screenshot sequence | Creates mental model of the product flow | Show: value -> key feature -> secondary feature -> social proof. NOT: feature list. |
| Preview video (iOS) | 30-second demo of the app experience | Show activation flow compressed: signup -> first value moment. Auto-plays in search results. |
| App description first line | Visible without expanding | State the activation benefit: "Track expenses in 30 seconds" not "The world's best expense tracker." |
| Ratings/reviews | Trust signal affecting willingness to start onboarding | Respond to negative reviews mentioning onboarding friction. These are public product feedback. |

## Cross-Platform Onboarding Consistency

When users sign up on web and continue on mobile (or vice versa):

| Rule | Implementation |
|---|---|
| Onboarding state syncs across platforms | Server-side state. When user opens mobile after starting onboarding on web, pick up where they left off. |
| Don't repeat steps already completed | Check completed steps before rendering onboarding UI. Platform-specific steps (push permission) shown only on relevant platform. |
| Account linking must be seamless | If user signed up with Google on web, Google SSO on mobile must link to same account without "email already exists" error. |
| Feature parity =/= onboarding parity | Mobile onboarding may skip steps that only apply to desktop features (e.g., keyboard shortcuts, browser extension install). |
| Handoff should be explicit | Email: "Continue setup on your phone" with deep link. Don't assume users will find the mobile app on their own. |
