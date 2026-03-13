# Launch Analytics & Dark Funnel

Measuring what's actually working during a launch -- including the 60-70% of attribution you can't track with UTMs.

## The Attribution Problem in Launches

During a launch, traffic comes from everywhere simultaneously: social media, word of mouth, press coverage, direct visits, Slack/Discord mentions, podcast listeners, email forwards. Standard UTM attribution captures maybe 30-40% of this. The rest is "dark funnel" -- real influence that doesn't leave a trackable click trail.

| Traffic Source | UTM Trackable? | Dark Funnel? | Real Attribution Method |
|---|---|---|---|
| Email campaign | Yes (UTM links) | -- | Standard click tracking |
| Social media post | Partially (link clicks yes, copy-paste no) | Yes (screenshots, DMs) | Click tracking + "how did you hear?" survey |
| Press coverage | Partially (some articles link, some don't) | Yes (people Google you after reading) | Referral tracking + branded search volume spike |
| Podcast mention | Rarely (listeners don't click mid-episode) | Yes (they Google later) | Branded search spike within 48h of episode air date |
| Word of mouth | Never | Yes (entirely dark) | "How did you hear about us?" is the ONLY signal |
| Slack/Discord share | Never (private channels) | Yes | Survey only |
| Conference talk | Never | Yes | Branded search spike + survey |

## The "How Did You Hear About Us?" Survey

This is the single most important attribution tool for launches. It captures dark funnel signal that no analytics tool can.

| Implementation Rule | Why |
|---|---|
| Ask during signup, not after | Post-signup surveys get 5-10% completion. In-flow questions get 80-90% |
| Open text field, NOT dropdown | Dropdowns bias toward your expected channels. Users will type "my friend told me" or "saw it on Twitter" -- you need the raw signal |
| Optional but prominent | Don't gate signup on it, but make it visible. A single text field below the signup button works |
| Categorize responses manually weekly | "Saw it on Twitter" and "Someone tweeted about it" and "Twitter thread" are the same channel. Build a taxonomy |
| Track BEFORE and DURING launch | Pre-launch baseline reveals what channels were already working. Launch period reveals what NEW channels activated |

**Gotcha**: People often cite the LAST touchpoint, not the first. Someone who saw your Product Hunt post, then Googled you, then came back via email will say "email." Cross-reference survey data with other signals to build a multi-touch picture.

## Viral Coefficient (K-Factor)

K-factor measures organic growth: how many new users each existing user brings in.

**Formula**: K = i x c
- i = average number of invites/shares per user
- c = conversion rate of those invites

| K-Factor | Interpretation | Action |
|---|---|---|
| K < 0.5 | No meaningful organic growth | Focus on paid/owned acquisition. Don't invest in referral features yet |
| K = 0.5-0.9 | Organic growth supplements paid acquisition | Optimize the sharing mechanism. Small improvements in share rate or conversion compound significantly |
| K = 1.0 | Each user brings exactly one new user. Growth is self-sustaining without paid acquisition | Rare and unstable. Most products that hit K=1 fluctuate above and below |
| K > 1.0 | True viral growth. User base grows exponentially | Extremely rare. Focus shifts to infrastructure scaling and retention, NOT more acquisition |

**Launch context**: K-factor is artificially high during launch week (enthusiasm, novelty, press coverage amplify sharing). Measure K-factor at week 4-6 post-launch for the real baseline. If K at week 6 is below 0.3, the product doesn't have organic virality -- plan accordingly.

**Improving K-factor**:
- Increase i (shares): Make the product's output inherently shareable (Loom videos, Canva designs, Calendly links). The best sharing is when the product IS the share
- Increase c (conversion of shares): Optimize the landing experience for shared links. Recipients clicking a shared Canva design should see the design first, signup prompt second

## Launch Spike Decay Analysis

Every launch creates a traffic/signup spike that decays. The decay pattern reveals product-market fit.

| Decay Pattern | What It Means | Half-Life |
|---|---|---|
| Cliff (90%+ drop in 48h) | Launch generated awareness but not retention. Product-market fit problem | < 2 days |
| Steep decay (70% drop in 1 week) | Some users stick but most came for novelty. Onboarding may be failing | 3-5 days |
| Gradual decay (50% drop in 2 weeks) | Reasonable retention. Optimize onboarding and activation to flatten curve | 10-14 days |
| Plateau (30% of spike sustained at 4 weeks) | Strong product-market fit. Launch users are converting to regular users | 30+ days |
| Growth (post-spike baseline HIGHER than pre-launch sustained growth rate) | Excellent. Launch activated word-of-mouth that continues independently | N/A -- growing |

**Measurement**: Track daily active users (or daily signups) for 30 days post-launch. Plot the curve. Calculate: (Day 30 DAU) / (Peak launch day DAU) = retention ratio. Above 20% is good. Above 40% is exceptional.

## Cohort Analysis for Launch Effectiveness

Users acquired during different launch phases have different quality. Measure each cohort separately.

| Cohort | Typical Behavior | Key Metric |
|---|---|---|
| Alpha testers | Highest engagement, most forgiving, best feedback | Feature request quality and bug report thoroughness |
| Beta users | High engagement, moderate expectations, willingness to work around issues | Day-7 retention rate and NPS |
| Launch day signups | Mixed quality -- includes genuine users and curiosity browsers | Day-1 activation rate (did they complete the core use case?) |
| Post-launch organic | Self-selected, found you through search or referral | Highest long-term LTV but slowest initial adoption |
| Press/PH traffic | Lowest intent -- many are just browsing | Signup-to-activation ratio (expect 10-20%, vs 40-60% for organic) |

**Launch quality score**: (Day-30 retained users from launch cohort) / (Total launch signups) x 100. Below 5% = launch attracted wrong audience. 5-15% = normal. Above 15% = exceptional targeting.

## Real-Time Launch Dashboard

What to watch during launch day vs what to ignore.

| Watch (Actionable) | Why | Response |
|---|---|---|
| Signup velocity (signups per hour) | Trend tells you if momentum is building or dying | If declining: amplify social + email. If climbing: do nothing, ride the wave |
| Activation rate (% completing core use case) | Launch-day users who don't activate in first session rarely return | If below 30%: there's an onboarding bug or UX friction. Fix immediately |
| Error rates / 5xx | Infrastructure failures during peak traffic destroy first impressions | If spiking: scale infrastructure or enable queue/waitlist mode |
| Support ticket volume and themes | Real-time signal of what's confusing or broken | Cluster themes. If one issue accounts for >30% of tickets, fix it or add a banner |
| Social mention sentiment | Are people talking about you positively or complaining? | If negative: respond publicly, fix issues fast. If positive: amplify by retweeting/sharing |

| Ignore During Launch (Check Later) | Why |
|---|---|
| Revenue / conversion rate | Too early -- people are trialing, not buying. Check at day 7-14 |
| Bounce rate | Launch traffic always has high bounce from curiosity visitors. Not actionable on day 1 |
| SEO rankings | Takes weeks to months to reflect launch activity |
| Competitor response | They'll respond eventually. Focus on your users, not your competitors, during launch |

## Conversion Window Analysis

How long after first visit do users convert? This determines how long your launch momentum matters.

| Product Type | Typical Conversion Window | Implication |
|---|---|---|
| Consumer SaaS (simple) | 1-3 days | Launch day IS your conversion window. Optimize for immediate signup |
| B2B SaaS (SMB) | 3-14 days | Launch drives awareness; conversion happens over 2 weeks. Retargeting and email nurture critical |
| B2B SaaS (Enterprise) | 30-90 days | Launch creates pipeline, not revenue. Track demo requests and qualified leads, not signups |
| Developer tools | 7-30 days | Developers bookmark, try when they have a relevant project, then adopt. Long-tail conversion |
| Marketplace / platform | 14-60 days | Both sides need to find value. Launch must seed supply before demand arrives |

**The retargeting window**: Set retargeting pixels before launch. Everyone who visits during launch but doesn't convert can be retargeted for the full conversion window. For B2B SaaS, a 30-day retargeting window starting from launch day captures the majority of delayed conversions.

## Attribution Pitfalls During Launches

| Pitfall | What Happens | Fix |
|---|---|---|
| Last-touch attribution overvalues email | User saw social post -> Googled you -> clicked email -> signed up. Email gets 100% credit | Use first-touch attribution for launch analysis. The first touchpoint reveals which channel CREATED awareness |
| Direct traffic is misattributed | 40-60% of "direct" traffic during launches is actually dark funnel (podcast, word of mouth, Slack) | Cross-reference direct traffic spikes with offline activities. If direct spikes 2 hours after a podcast airs, that's podcast traffic |
| UTM parameters stripped by platforms | LinkedIn, some email clients, and iOS privacy strip UTMs | Use unique landing pages per channel as backup: /from-ph, /from-twitter, /from-podcast |
| Multi-device journey breaks attribution | User sees ad on phone, converts on laptop | "How did you hear about us?" survey captures this. Analytics can't |
| Organic search gets credit for brand awareness | Press coverage drives branded searches, which analytics attributes to "organic search" | Track branded search volume separately. A spike in branded searches after a press hit = PR-driven traffic, not SEO |
