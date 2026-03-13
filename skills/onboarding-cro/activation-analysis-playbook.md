# Activation Analysis Playbook

Load when defining or redefining the activation event, troubleshooting low activation rates, validating activation metrics, or analyzing retention cohorts.

## Cohort Analysis Methodology

Finding the activation event is not guesswork. It is a data exercise with a specific procedure.

### Step-by-Step Process

1. **Define retained**: Users who are still active at day 30 (or your retention horizon). "Active" = performed a core action, not just logged in.
2. **Pull day-1 action data**: For every user who signed up in the last 90 days, list every action they took in their first 24 hours (or first session for B2B).
3. **Compare retained vs churned**: For each action, calculate: `(% of retained users who did it) - (% of churned users who did it)`. The action with the largest positive delta is your activation candidate.
4. **Validate correlation**: The candidate must have Pearson r > 0.5 with 7-day retention. Below 0.5, the signal is too weak to build onboarding around.
5. **Test directionality**: Does doing the action CAUSE retention, or do already-motivated users both do the action and retain? Run a holdback experiment: guide 50% of users toward the action, leave 50% unguided. If guided users retain better, it is causal.

### SQL Pattern (Pseudocode)

```
SELECT action_name,
  COUNT(CASE WHEN retained_30d THEN 1 END) * 1.0 / COUNT(*) as retention_rate,
  COUNT(*) as total_users
FROM user_first_day_actions
GROUP BY action_name
ORDER BY retention_rate DESC
```

Filter to actions performed by at least 10% of users (rare actions produce misleading high rates).

## False Activation Traps

These are events that LOOK like activation but are not. Each wastes optimization effort.

| Trap | Why It Looks Right | Why It Is Wrong |
|---|---|---|
| Account creation / signup | 100% of retained users did it | 100% of churned users also did it. Zero discriminating power. |
| Profile completion | Correlates with engagement | Motivated users complete profiles AND retain. It is a proxy for motivation, not a cause of retention. |
| Viewing the pricing page | Retained users viewed pricing more | Pricing page indicates purchase intent. It is a buying signal, not an activation signal. |
| Feature exploration (visited 5+ pages) | Retained users explored more | Navigation breadth measures curiosity, not value received. Explorers who find nothing still churn. |
| Time spent in app (>10 min first session) | Retained users spend more time | Time in app can mean confusion as easily as engagement. A user stuck on setup for 15 minutes is not activated. |
| Social sharing the product | Correlates with retention | Only 2-5% of users share. The 95% who retain without sharing have a different activation path. |
| Watching the tutorial video | Completers retain better | Selection bias: users willing to watch a 5-min video are already more committed. The video itself may add little. |
| Connecting a second integration | Multi-connected users retain better | The first integration is activation. The second is expansion. Don't require expansion for activation. |

## Activation Event Evolution

The activation event is not permanent. It changes when the product changes.

| Product Change | Activation Impact | What to Do |
|---|---|---|
| New core feature launched | Old activation event may be less relevant | Re-run cohort analysis with last 60 days of data. If a new action correlates more strongly, update. |
| New user segment acquired (e.g., moved upmarket) | Different segments may have different activation events | Run segment-level cohort analysis. Enterprise activation often differs from SMB. |
| Activation rate plateaus despite optimization | The event itself may be the ceiling | Look for a "deeper" activation event (not just "created a project" but "created a project AND invited a collaborator"). |
| Churn increases despite stable activation rate | Activation event no longer predicts retention | The correlation has decayed. Re-validate with recent data. |
| Feature deprecation | Activation event tied to deprecated feature | Identify replacement feature and validate new activation event before deprecating. |

**Re-validation cadence**: Quarterly for high-growth products (user base composition changes fast). Bi-annually for stable products.

## Multi-Product Activation

When the product is a suite or platform with multiple distinct features:

| Pattern | Example | Approach |
|---|---|---|
| Single core product | Slack (messaging) | One activation event for the product |
| Hub-and-spoke | HubSpot (CRM + Marketing + Sales) | One activation per hub, AND a cross-hub activation ("uses 2+ hubs") |
| Marketplace (two-sided) | Airbnb (hosts + guests) | Separate activation events per side. Host: first listing published. Guest: first booking completed. |
| Platform (developer tools) | Stripe (payments + billing + connect) | Primary activation = first successful payment. Secondary activations per product. |

**Multi-product trap**: Do not define activation as "used product A AND product B AND product C." Users who find value in one product are retained. Cross-product activation is an expansion metric, not a base activation metric.

## Business Model Activation Patterns

| Model | Typical Activation | Critical Nuance |
|---|---|---|
| Freemium | First use of a paid-tier feature (via trial or upgrade) | Free-only users who never touch paid features have ~3x churn rate. Activation must include at least exposure to premium value. |
| Free trial (time-limited) | Core value moment within first 25% of trial period | If trial is 14 days, activation must happen by day 3-4. Day 12 activations rarely convert. |
| Usage-based | First meaningful usage event (not just a test API call) | Define "meaningful" by $ value or data volume. A test call with 1 record is not activation. |
| Enterprise (annual contract) | Successful deployment + first team adoption | Signed contract is NOT activation. Deployment without adoption = shelfware = churn at renewal. |
| Marketplace | First completed transaction (both sides) | Listing creation (supply) or browsing (demand) are NOT activation. Only completed transactions demonstrate value exchange. |

## Activation Debugging Checklist

When activation rate is below target, diagnose systematically:

| Check | What to Look For | If Found |
|---|---|---|
| Step-level drop-off | Which step before activation has the biggest % drop? | That step is your optimization target. Fix the biggest leak first. |
| Segment variance | Is one channel/segment dragging down the aggregate? | Segment-specific onboarding may be needed. |
| Time-to-activation distribution | Is it bimodal (some activate fast, most never)? | The "never" group may have a fundamentally different need. Interview them. |
| Error rates at activation step | Are technical failures preventing activation? | Fix bugs before optimizing UX. A 5% error rate on the activation step costs 5% activation rate. |
| Value clarity | Do users understand what activation looks like? | Test: ask 5 new users what the product does. If they can't articulate it, the landing page and onboarding messaging are misaligned. |
| Competitive comparison | Are users signing up to compare, not to adopt? | High signup + low activation from comparison shopping channels (G2, Capterra) is normal. Segment these users. |
