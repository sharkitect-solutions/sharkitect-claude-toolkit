# Platform Compliance for Paywalls

Load when implementing mobile paywalls or reviewing paywall compliance before submission.

## Apple App Store Review Criteria

### Paywall-Specific Rejection Triggers

| Rule | What Apple Checks | Common Violation | Consequence |
|------|------------------|------------------|-------------|
| 3.1.1 In-App Purchase | All digital goods/services must use IAP | Linking to web checkout, mentioning web prices | Rejection + potential account review |
| 3.1.2(a) Subscriptions | Auto-renewable subs must use StoreKit | Using Stripe for recurring digital content | Rejection |
| Anti-steering (post-2024) | Cannot link to external purchase options, suggest lower prices exist elsewhere, or use language encouraging out-of-app purchase | "Subscribe on our website for a better deal" | Rejection + escalation risk |
| 3.1.3(b) Multiplatform | "Reader" apps (Netflix, Spotify) can link out but CANNOT include pricing info or purchase buttons in-app | Showing web pricing in a reader app | Rejection |
| Close button visibility | Paywall must have visible, accessible dismiss mechanism | Delayed close button, tiny close icon, hidden gesture | Rejection |
| Subscription terms display | Price, duration, and renewal terms must be visible before purchase | Terms only shown in App Store sheet | Rejection |
| Restore Purchases | Must provide accessible "Restore Purchases" for existing subscribers | No restore button, buried in settings | Rejection -- Apple specifically checks this |
| Free trial disclosure | If offering a trial, must clearly state trial duration and post-trial price | "Free trial" without showing $X/month after | Rejection |

### StoreKit 2 vs StoreKit 1

| Feature | StoreKit 1 | StoreKit 2 |
|---------|-----------|-----------|
| Minimum iOS | iOS 3+ | iOS 15+ |
| Receipt validation | Client-side receipt parsing OR server-to-server with `verifyReceipt` endpoint (deprecated) | Server-side with App Store Server API v2 + JWS signed transactions |
| Subscription status | Poll `verifyReceipt` or use server notifications | `Product.SubscriptionInfo.status` API + real-time App Store Server Notifications V2 |
| Offer codes | Not available | Supported natively -- generate in App Store Connect |
| Family sharing | Complex implementation | Built-in `isFamilyShareable` property |
| Refund handling | Server notification (unreliable timing) | `Transaction.revocationDate` + `beginRefundRequest()` to prompt user |
| Transaction history | `restoreCompletedTransactions()` floods delegate with all history | `Transaction.currentEntitlements` -- clean async sequence |

**Migration decision**: If targeting iOS 15+ (>95% of active devices as of 2025), use StoreKit 2 exclusively. If supporting iOS 14, implement SK2 with SK1 fallback. Do NOT maintain parallel implementations long-term -- the complexity is not worth the <5% user segment.

### Apple Review Timeline Expectations
- Standard review: 24-48 hours (can be weeks during holiday season)
- Expedited review: 24 hours (limited to genuine emergencies)
- Paywall changes specifically: Apple sometimes flags paywall-heavy apps for extended review
- Rejected for paywall issues: fix and resubmit adds another 24-48 hours
- Tip: submit paywall changes as a separate build from feature releases -- isolates rejection risk

## Google Play Billing

### Play Billing Library Versions

| Library Version | Status | Key Feature |
|----------------|--------|-------------|
| PBL 5.x | Current (required for new apps) | Supports billing config for regional pricing |
| PBL 6.x | Latest (recommended) | External offers program support, simplified API |
| PBL 4.x | Deprecated | Missing billing config, regional pricing limitations |

### Subscription Lifecycle Events

| Event | What Happens | Your Action |
|-------|-------------|-------------|
| SUBSCRIPTION_PURCHASED | New subscription or resubscription | Grant access, record start date |
| SUBSCRIPTION_RENEWED | Auto-renewal processed successfully | Extend access period |
| SUBSCRIPTION_IN_GRACE_PERIOD | Payment failed, grace period active (3-7 days) | Keep access, show "update payment" banner |
| SUBSCRIPTION_ON_HOLD | Grace period expired, hold started (up to 30 days) | Revoke access, show "resubscribe" prompt |
| SUBSCRIPTION_CANCELED | User canceled but still has time remaining | Show "you have access until [date]" -- do NOT revoke immediately |
| SUBSCRIPTION_EXPIRED | Access period ended after cancellation | Revoke access, show winback offer |
| SUBSCRIPTION_REVOKED | Refund granted or account issue | Revoke access immediately |
| SUBSCRIPTION_PAUSED | User paused subscription (if enabled) | Revoke access, show resume date |

### Proration Mode Selection Guide

| Scenario | Recommended Mode | User Experience |
|----------|-----------------|-----------------|
| User upgrades mid-cycle (Basic -> Pro) | IMMEDIATE_WITH_TIME_PRORATION | Prorated credit applied, no surprise charges. Best UX |
| User upgrades to much higher tier | IMMEDIATE_AND_CHARGE_PRORATED_PRICE | Immediate charge of difference. Clear but may surprise |
| User downgrades (Pro -> Basic) | DEFERRED | Change at next renewal. No refund confusion |
| User switches between similar tiers | IMMEDIATE_WITH_TIME_PRORATION | Smooth transition, fair billing |
| Enterprise customer with custom billing | Avoid Play Billing proration entirely | Handle through your own billing system with Play as IAP only |

## EU Digital Services Act (DSA) Compliance

| Requirement | Impact on Paywalls | Implementation |
|-------------|-------------------|----------------|
| Dark pattern prohibition | Manipulative dismiss text banned ("No, I don't want to succeed") | Neutral dismiss: "Not now", "Maybe later", "No thanks" |
| Transparent pricing | All costs must be clear before commitment | Show total price, billing frequency, renewal terms upfront |
| Easy cancellation | Cancellation must be as easy as signup | Provide in-app cancellation or direct link to platform subscription management |
| No forced consent | Cannot gate access to require personal data beyond what's needed | Do not require email/phone just to view pricing |
| Subscription auto-renewal disclosure | Must inform before each renewal if price changes | Push notification or email before renewal with any price changes |

### GDPR Intersection with Paywalls
- "Pay or consent" models (subscribe or accept tracking): CJEU ruled these require genuine free alternative
- Collecting analytics on paywall interactions: legitimate interest MAY apply but consent is safer
- Subscription data retention: must delete user subscription data on account deletion request (right to erasure)
- Cross-border pricing: price discrimination based on IP geolocation must be disclosed under EU geo-blocking regulation

## Regional Compliance Quick Reference

| Region | Key Requirement | Common Mistake |
|--------|----------------|----------------|
| EU/EEA | Tax-inclusive pricing display required | Showing USD-style exclusive pricing |
| Japan | Specified commercial transaction act -- must show seller info | No company name/address on payment screen |
| South Korea | Must offer refund within 7 days for digital goods | No refund mechanism implemented |
| Brazil | Consumer protection code -- 7-day cooling off period for remote purchases | No cancellation option within 7 days |
| India | RBI recurring payment rules -- must notify before each auto-debit >5000 INR | Silent auto-renewals above threshold |
| Australia | ACL requires clear cancellation and renewal terms | Subscription terms buried in fine print |
| California (US) | SB-313 automatic renewal law -- clear consent + cancellation mechanism required | Auto-renewal without explicit opt-in |

## Pre-Submission Compliance Checklist

| Platform | Check | Status Required |
|----------|-------|-----------------|
| iOS | Restore Purchases button accessible | Must pass |
| iOS | Subscription terms visible before purchase | Must pass |
| iOS | No external purchase links or pricing mentions | Must pass |
| iOS | StoreKit 2 for iOS 15+ target | Recommended |
| Android | Grace period handling implemented | Must pass |
| Android | Proration mode explicitly set for upgrades/downgrades | Must pass |
| Android | Real-time developer notifications configured | Recommended |
| Both | Close/dismiss button visible and functional | Must pass |
| Both | Neutral dismiss text (no dark patterns) | Must pass (EU mandate) |
| Both | Price shown in local currency | Must pass |
| Both | Auto-renewal terms clearly stated | Must pass |
