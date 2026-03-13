# Referral Platform Selection Guide

## Build vs Buy Decision

| Signal | Buy (SaaS Platform) | Build Custom |
|---|---|---|
| Time to launch | Need program live in <2 weeks | 6-12 week development timeline acceptable |
| Program complexity | Standard double-sided referral or affiliate program | Multi-sided marketplace referrals, custom attribution logic, or non-standard reward triggers |
| Scale | <50K referrals/month | >50K referrals/month AND platform pricing becomes cost-prohibitive |
| Engineering resources | No dedicated engineering time for referral infrastructure | Dedicated team member for ongoing maintenance |
| Payment integration | Standard Stripe/PayPal/Braintree | Custom payment system or cryptocurrency rewards |
| Fraud sophistication | Standard fraud patterns (self-referral, rings) | Industry-specific fraud requiring custom detection (e.g., fintech KYC-integrated referrals) |

**Default recommendation**: Buy. Custom referral systems have 3-5x the maintenance cost of SaaS platforms. Only build custom if you have a genuine technical requirement that no platform supports.

## Platform Comparison

### Customer Referral Platforms

| Platform | Best For | Pricing | Stripe Integration | Key Gotcha |
|---|---|---|---|---|
| **GrowSurf** | SaaS and tech companies. Lightweight, developer-friendly | $200-600/month (by participant count) | Native Stripe integration. Auto-detects conversions from Stripe events | Free tier limited to 1,000 participants. Pricing jumps at scale. No built-in email -- requires integration with your email provider |
| **ReferralCandy** | E-commerce (Shopify, WooCommerce, BigCommerce) | $59/month + % of referral sales (up to 3.5%) | Not direct. Works through e-commerce platform integration | The commission-based pricing means your cost scales with success. At high volume, this gets expensive. No SaaS subscription tracking |
| **Viral Loops** | Template-based campaigns (pre-launch, milestone rewards, leaderboards) | $49-299/month by campaign type | Limited. Works better with e-commerce than SaaS | Templates are quick to launch but hard to customize deeply. If you outgrow the template, migration is painful |
| **Friendbuy** | Mid-market e-commerce and subscription brands | Custom pricing ($1000+/month) | Yes, but primarily e-commerce focused | Enterprise-level features (A/B testing, segmentation) but enterprise-level pricing. Overkill for early-stage companies |
| **Prefinery** | Pre-launch waitlists and beta programs | $49-299/month | No direct Stripe integration | Great for pre-launch viral waitlists. Limited for post-launch ongoing referral programs |

### Affiliate Platforms

| Platform | Best For | Pricing | Commission Tracking | Key Gotcha |
|---|---|---|---|---|
| **PartnerStack** | B2B SaaS affiliate/partner programs | Custom pricing ($800+/month) | Full lifecycle: click -> trial -> purchase -> renewal | Minimum 12-month contract. Expensive for startups. But: includes partner marketplace for affiliate recruitment |
| **Rewardful** | Stripe-native SaaS affiliate tracking | $49-299/month | Direct Stripe integration. Tracks MRR, upgrades, downgrades, churn | ONLY works with Stripe. If you use another payment provider, Rewardful won't work. No built-in affiliate marketplace |
| **FirstPromoter** | SaaS companies (similar to Rewardful) | $49-299/month | Stripe + Paddle + Chargebee integration | Slightly more payment provider flexibility than Rewardful. UI is less polished. Better fraud detection than Rewardful |
| **Tapfiliate** | SaaS + e-commerce hybrid | $89-249/month | Stripe + various e-commerce platforms | Broad but shallow integrations. Jack-of-all-trades positioning means no integration is as deep as specialized alternatives |
| **Impact** | Enterprise partnership programs | Custom pricing ($2000+/month) | Multi-touch attribution, cross-device tracking | The "Salesforce of affiliate management" -- powerful but complex. 3-6 month implementation typical. Not for startups |

### Affiliate Networks (marketplaces)

| Network | When to Use | Commission to Network | Key Difference from Platform |
|---|---|---|---|
| **ShareASale** | Want access to 240K+ existing affiliates without recruitment | 20% of commissions paid (network fee) | You don't recruit affiliates -- they find you in the marketplace. Lower quality average but higher volume |
| **CJ Affiliate** | Enterprise e-commerce with established affiliate program | Custom network fees | Largest enterprise network. Premium publishers. Minimum spend requirements |
| **Awin** | International reach (strong in EU/UK) | Custom network fees (typically 2.5% + transaction fee) | Best for companies with significant European customer base. ShareASale is a subsidiary |

**Platform vs Network decision**: Platform = you recruit and manage affiliates (better quality, more work). Network = affiliates find you (less work, lower average quality, network takes commission cut). Most companies start with a platform, add a network later for volume.

## Stripe Integration Patterns

Since most SaaS companies use Stripe, here are the integration patterns that matter:

| Pattern | How It Works | Supported Platforms | Gotcha |
|---|---|---|---|
| Webhook-based tracking | Stripe sends `invoice.paid` or `checkout.session.completed` webhook. Referral platform matches webhook to referral cookie/link | Rewardful, FirstPromoter, GrowSurf | Webhook delivery isn't guaranteed. Implement webhook failure handling. Check for missed events with periodic Stripe API reconciliation |
| Stripe Checkout metadata | Pass referral code as metadata in Stripe Checkout session. Platform reads metadata to attribute | Rewardful, custom builds | Only works if referral code flows through your checkout. If user clears cookies between referral click and purchase, attribution lost |
| Stripe customer metadata | Store referral attribution on the Stripe Customer object. Platform reads customer metadata | Most platforms via API | Requires your app to write referral data to Stripe before checkout. Extra integration step that's easy to skip |
| Coupon-based tracking | Create unique Stripe coupon per referrer. Redemption = referral attribution | Custom builds only | Coupons aren't designed for attribution. Works for simple programs but creates coupon management overhead at scale |

**Critical Stripe gotcha**: Stripe test mode and live mode are completely separate environments. Test your referral integration in Stripe test mode FIRST. Common failure: referral platform configured for test mode API key, works perfectly in testing, fails silently in production because live mode key wasn't updated.

## Attribution Window Gotchas

| Platform | Default Attribution Window | Can You Change It? | What Happens at Window Expiry |
|---|---|---|---|
| GrowSurf | 90 days | Yes (custom per campaign) | Referral link click expires. Next click from any source gets attribution |
| ReferralCandy | 30 days | No (hardcoded) | Conversion after 30 days = organic, not referral. No reward |
| Rewardful | 60 days | Yes (30, 60, 90 days, or lifetime) | Lifetime option available but increases fraud risk. Recommended: match your sales cycle length |
| PartnerStack | 90 days | Yes (custom per partner tier) | Premium partners can get longer windows as an incentive |

**Multi-device attribution problem**: User clicks referral link on mobile, purchases on desktop 3 days later. Most platforms use cookie-based attribution -- different device = lost attribution. Solutions: (1) login-based attribution (if user creates account on mobile, conversion on desktop still attributes), (2) UTM-based attribution (pass referral code in URL, store in user profile at signup).

## Migration Considerations

| From | To | Difficulty | Data at Risk |
|---|---|---|---|
| Custom build -> SaaS platform | Medium | Historical referral data (import via CSV). Active referral links (need redirect rules) |
| SaaS platform A -> SaaS platform B | Medium-hard | Active affiliate relationships. Pending commissions. Historical attribution data (most platforms don't export full attribution chain) |
| Network (ShareASale) -> Platform (Rewardful) | Hard | Affiliate relationships (affiliates must re-register). Commission history. Brand recognition within network |

**Migration golden rule**: Run both systems in parallel for 30-60 days. Only cut over the old system after confirming the new system captures 95%+ of referrals. Attribution gaps during migration = lost revenue for affiliates = damaged relationships.
