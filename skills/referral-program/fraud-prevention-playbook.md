# Referral Fraud Prevention Playbook

## Fraud Pattern Taxonomy

Understanding fraud patterns before building prevention. These are the actual patterns seen in production referral programs, not theoretical risks.

| Pattern | Sophistication | Detection Difficulty | Financial Impact |
|---|---|---|---|
| **Self-Referral** | Low. User creates second account with different email to claim both rewards | Easy. Same device fingerprint, same IP, same billing info | Low per instance, high in aggregate. 15-30% of unprotected program volume |
| **Household Referral Ring** | Low-medium. Family/roommates refer each other. Technically different people, but no genuine "spread" | Medium. Different people but same IP, same Wi-Fi, same household | Medium. Each referral is technically valid but doesn't expand your market |
| **Coupon Site Hijacking** | Medium. Coupon aggregators (RetailMeNot, Honey) scrape referral codes and post them publicly | Hard. Traffic looks organic. Conversions are real purchases. But attribution is stolen from organic intent | HIGH. These users would have converted anyway. You're paying referral rewards for customers you'd have gotten for free |
| **Referral Ring (Organized)** | High. Groups of 10-50 people systematically refer each other, churning through free trial rewards | Medium-hard. Different IPs, different devices, but similar signup patterns and rapid reward redemption | High. Organized rings can drain thousands/month before detection |
| **Bot Farm Referral** | High. Automated account creation at scale. Fake emails, virtual phone numbers, rotating proxies | Easy to catch basic bots (rate limiting). Hard to catch sophisticated bots with realistic behavior patterns | Very high. Can generate hundreds of fake referrals per day |
| **Affiliate Fraud (last-click hijacking)** | Very high. Affiliate uses browser extensions, toolbar, or cookie stuffing to overwrite existing attribution cookies | Very hard. The conversion is real, the customer is real, but the affiliate didn't actually drive the sale | Very high. Major affiliate programs lose 5-15% of commission spend to attribution fraud |

## Verification Tier Selection

Match verification strictness to reward value. Over-verifying creates friction; under-verifying creates fraud.

| Reward Value per Referral | Verification Tier | Required Checks | Friction Level |
|---|---|---|---|
| <$10 | Light | Email verification + referral limit (max 10/month) + delayed payout (7 days) | Minimal. Most fraud isn't worth the effort at this reward level |
| $10-50 | Standard | Light + device fingerprinting + IP monitoring + activity threshold (referred user must complete onboarding) | Low-medium. False positive rate ~2-3% |
| $50-200 | Enhanced | Standard + phone verification + manual review for >5 referrals/month + payment method uniqueness | Medium. Some legitimate referrers will contact support about delays |
| $200+ | Strict | Enhanced + identity verification + minimum referred customer tenure (30-60 days) + progressive payout (50% at signup, 50% after 30 days) | High. Accept the friction -- at this reward level, fraud economics justify sophisticated attackers |

## Device Fingerprinting Approaches

| Signal | What It Detects | Reliability | Privacy Consideration |
|---|---|---|---|
| Browser fingerprint (canvas, WebGL, fonts) | Same browser across "different" accounts | Medium. 80-90% accuracy. Fingerprints change with browser updates | Low concern. No PII collected. Check local privacy laws |
| IP address clustering | Multiple signups from same network | Low alone (shared IPs are common: offices, universities, VPNs). Useful in combination | Low concern. IP is infrastructure data |
| Payment method matching | Same credit card across accounts | Very high. Hard to get unique payment methods at scale | Medium concern. Requires payment data access |
| Phone number matching | Same phone across accounts | High. Virtual numbers detectable (Twilio Lookup API: $0.005/lookup detects carrier type) | Medium concern. Phone numbers are PII |
| Behavioral pattern matching | Similar navigation patterns, timing, typing speed across accounts | Medium-high for organized rings. Machine learning required | Higher concern. Behavioral data requires privacy notice |

**Critical gotcha**: Don't block VPN users outright. 15-25% of legitimate users use VPNs (NordVPN/ExpressVPN market data). Instead, flag VPN + other signals as risk factors. VPN alone is not fraud evidence.

## Payout Delay Strategies

Delaying reward payout is the single most effective anti-fraud measure. Fraudsters optimize for quick cash-out.

| Strategy | Delay Period | Fraud Reduction | Legitimate User Impact |
|---|---|---|---|
| No delay (immediate payout) | 0 days | 0% (baseline) | Best UX but maximum fraud exposure |
| Short delay | 7 days | 40-50% reduction | Minimal impact. Most users understand "rewards processed weekly" |
| Medium delay (recommended) | 14-30 days | 60-75% reduction | Some support tickets. Explain in program terms. Most fraud rings won't wait 30 days |
| Activity-gated | Payout when referred user completes specific action (first purchase, 7 days active, etc.) | 75-85% reduction | Reduces UX only if gating action is unclear. Be specific: "Your reward unlocks when [Name] makes their first purchase" |
| Progressive payout | 50% at signup, 50% after 30-day retention | 70-80% reduction | Best balance. Referrer gets immediate gratification + long-term reward. Fraudsters get only half reward for accounts that won't retain |

## Fraud Cost Modeling

Before building prevention, model the cost of fraud vs the cost of prevention.

| Factor | How to Calculate | Decision Rule |
|---|---|---|
| Estimated fraud rate without prevention | Industry average: 15-30% of referral volume for programs with <$50 rewards. 30-50% for programs with >$100 rewards | If (fraud rate x reward value x expected volume) < $500/month, basic prevention may suffice |
| Cost of fraud prevention tool | Platform-specific: ReferralCandy includes basic fraud detection. Dedicated tools (SEON, Sardine): $500-5000/month | If fraud cost < tool cost, build basic in-house checks instead |
| Cost of manual review | ~2 minutes per flagged referral x analyst hourly rate. At 100 referrals/day with 10% flag rate = ~20 minutes/day | Manual review scales poorly above 500 referrals/month. Automate detection, human review for edge cases only |
| False positive cost | Each false positive = 1 support ticket ($5-15) + customer goodwill damage | Target <3% false positive rate. A 10% false positive rate means you're punishing more legitimate users than fraudsters |

## Fraud Response Playbook

| Fraud Type Detected | Immediate Action | Investigation | Resolution |
|---|---|---|---|
| Self-referral (clear evidence) | Freeze pending rewards for both accounts | Verify device/IP/payment overlap | Void both rewards. Warn primary account. Do NOT ban immediately (may be innocent mistake: spouse sharing a device) |
| Organized ring (>5 accounts with pattern match) | Freeze all pending rewards in the cluster | Map the full ring (shared signals, timing patterns, reward redemption patterns) | Void all rewards. Ban accounts with >3 fraud signals. Report to platform if using affiliate network |
| Coupon site posting | Remove public code. Generate new referral links for affected users | Check if coupon site is an authorized affiliate | If unauthorized: send cease-and-desist. Switch from static codes to dynamic links. If authorized affiliate: negotiate terms |
| Bot farm (automated signups) | Rate limit IP range. Enable CAPTCHA for referral signups | Analyze signup velocity, email domain patterns, behavioral signals | Block identified bot infrastructure. Require phone verification for flagged cohorts. Report to email provider if using disposable email services |
