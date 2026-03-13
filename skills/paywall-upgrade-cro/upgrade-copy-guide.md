# Upgrade Copy Guide

Load when writing paywall copy, CTA text, or value propositions for upgrade screens.

## CTA Copy by Trigger Type

Different trigger contexts require fundamentally different copy approaches. Using the wrong frame kills conversion.

| Trigger Type | CTA Frame | Example CTA | Why This Frame |
|-------------|-----------|-------------|----------------|
| Feature gate (clicked locked feature) | Unlock frame -- they want THIS thing | "Unlock [feature name]" | User has specific intent. Generic "Upgrade" loses the connection to what they wanted |
| Usage limit reached | Continue frame -- they were mid-workflow | "Continue with Pro" or "Keep going -- upgrade" | User was doing something. Frame as removing the interruption, not buying something new |
| Trial expiration (data created) | Keep frame -- loss aversion active | "Keep your [N] projects" or "Don't lose your work" | User has created value. The CTA should protect what they built, not sell features |
| Power user on free tier | Peer frame -- social proof | "See what Pro users at your level do" | These users have rationalized free. Feature lists fail. Peer comparison creates FOMO |
| Team expansion | Team capability frame | "Empower your team with Pro" | Reframes from personal expense to team investment. Triggers organizational budget thinking |
| Soft prompt (time-based) | Value frame -- gentle | "See Pro features" or "Explore Pro" | Low intent. Hard sell backfires. Give them information, not pressure |

## Value Proposition Structure

### The 3-Part Formula

Every paywall value proposition should contain exactly three elements:

1. **What they get** (specific feature or capability, not a vague benefit)
2. **Why it matters for THEM** (personalized to their usage pattern)
3. **Proof it works** (social proof, data point, or comparison)

**Good**: "Unlimited exports (you've hit the limit 4 times this month). Used by 12,000+ teams."
**Bad**: "Upgrade to Pro for the best experience and unlock premium features!"

### Feature Prioritization for Paywall Display

Show the 3-5 features that matter most to THIS user segment. Determining which features to show:

| Method | How | When to Use |
|--------|-----|-------------|
| Usage-based | Show features related to what user does most | Best for power users -- data-driven relevance |
| Blocked-action-based | Show the specific feature they just tried to use + 2 related features | Best for feature gate triggers -- immediate relevance |
| Segment-based | Predefined feature lists per user segment (solo/team/enterprise) | When personalization data is unavailable |
| Top-converting | Show the features that historically drive the most upgrades | Default fallback when no personalization is possible |

**Rule**: If you show more than 5 features, you're displaying a comparison table, not a value proposition. Comparison tables serve a different purpose (rational evaluation) and belong on a dedicated plan page, not in a modal paywall.

## Social Proof Patterns

### Hierarchy of Effectiveness

Listed from most to least effective for paywall contexts:

| Tier | Type | Example | Lift Range |
|------|------|---------|------------|
| 1 | Peer-specific | "Teams with [N] members in [industry] use Pro" | 15-25% |
| 2 | Usage-specific | "Users who create [N]+ [items] per month choose Pro" | 10-20% |
| 3 | Named customer | "[Recognizable company] uses Pro" | 8-15% |
| 4 | Aggregate count | "Join 50,000+ Pro teams" | 3-8% |
| 5 | Generic testimony | "Pro is amazing!" -- Jane D. | 0-3% (often negative) |

### Social Proof Placement Rules
- Place social proof BETWEEN the value proposition and the CTA button -- this is the decision moment
- Never place social proof above the fold if it pushes the CTA below the fold on mobile
- Peer-specific proof requires data accuracy >90% -- wrong industry or wrong company size performs WORSE than no proof
- Rotate social proof monthly -- the same testimonial goes stale after 4-6 weeks (banner blindness)

## Urgency Calibration

### When Urgency Works

| Context | Urgency Level | Mechanism | Copy Pattern |
|---------|--------------|-----------|--------------|
| Trial with <3 days remaining | High | Genuine deadline | "Your trial ends in [N] days. Keep your [data]" |
| Usage at 95%+ of limit | Medium-High | Real scarcity | "[N] of [limit] used. Upgrade for unlimited" |
| Limited-time offer (genuine) | Medium | Time-bound value | "Annual plan: $X/year (save $Y) -- offer ends [date]" |
| Feature gate, no deadline | None | Do NOT manufacture urgency | "Unlock [feature] with Pro" -- let the desire do the work |

### When Urgency Backfires

| False Urgency Pattern | Why It Fails | Measured Impact |
|----------------------|-------------|-----------------|
| "This offer expires in 10:00 minutes" (resets on page refresh) | Users discover the lie. Trust destroyed permanently | 15-30% DECREASE in future paywall conversion for these users |
| "Only 3 spots left on Pro plan" (for a digital product) | Artificial scarcity doesn't make sense for software | Users share screenshots on social media, brand damage |
| "Upgrade now or lose access" (when they won't actually lose anything) | Empty threat detected immediately | Higher dismiss rate, lower future engagement |
| Countdown timer on every paywall view | Timer fatigue -- users learn to ignore it | Conversion drops 20% after 3rd exposure to timer |

**Rule**: If the urgency is not REAL (genuine deadline, genuine limit, genuine limited offer), do not use urgency. Users calibrate their trust level based on whether previous urgency claims were honest.

## Dismiss Button Copy

### What Works

| Copy | Context | Why |
|------|---------|-----|
| "Not now" | Default for all paywalls | Implies "maybe later" -- keeps door open |
| "Maybe later" | Soft prompts, low urgency | Explicitly non-committal, zero pressure |
| "No thanks" | After clear value proposition | Polite decline, respects the user's decision |
| "Remind me later" | Trial expiration, usage limits | Gives user control over next touchpoint |
| [X button with no text] | Modal overlays | Clean, no copy needed for close buttons |

### What Fails (and Why)

| Copy | Problem | Risk |
|------|---------|------|
| "No, I don't want to grow my business" | Manipulative -- guilts user into clicking Yes | EU DSA violation, NPS damage, social media backlash |
| "I'll stay limited" | Negative framing of their current state | Makes free users feel punished |
| "Maybe when I'm serious about [goal]" | Implies user isn't serious | Condescending, creates resentment |
| [No dismiss button] | Trapped -- forces engagement | App store rejection (Apple), user rage |
| "Continue with basic" (when it's the free tier) | Euphemism that insults intelligence | Users know "basic" means "free." Just say "Stay on Free" |

## Copy Anti-Patterns

| Anti-Pattern | Example | Fix |
|-------------|---------|-----|
| Feature list without context | "Unlimited storage, API access, Priority support" | "Unlimited storage (you're using 4.2 of 5 GB)" |
| Benefit without specificity | "Boost your productivity" | "Export reports 3x faster with batch processing" |
| Jargon in consumer context | "SSO, RBAC, SOC 2 compliance" | Only show these to enterprise segments |
| Price without anchor | "$29/month" | "$29/month ($0.96/day -- less than your coffee)" |
| Multiple CTAs competing | "Start Trial" + "See Plans" + "Talk to Sales" on same screen | One primary CTA. Others as text links below |
| ALL CAPS urgency | "UPGRADE NOW BEFORE IT'S TOO LATE" | Normal case. Urgency from content, not typography |

## Localization Gotchas

| Issue | Example | Rule |
|-------|---------|------|
| Direct translation of idioms | "It's a no-brainer" doesn't translate to most languages | Use simple, direct language. Avoid idioms in source copy |
| Currency symbol position | "$29" (US) vs "29 EUR" (Germany) vs "EUR 29" (Ireland) | Use locale-aware formatting, not string concatenation |
| Number formatting | "10,000" (US) vs "10.000" (Germany) vs "10 000" (France) | Use Intl.NumberFormat or equivalent locale-aware formatter |
| Color associations | Red = danger in West, luck in China, mourning in South Africa | Test paywall colors with target market users |
| CTA length | German and French CTAs are 30-50% longer than English | Design button width for longest localized string, not English |
| Formal vs informal | "Du" vs "Sie" in German, "tu" vs "vous" in French | Match the formality level of the rest of the product |
