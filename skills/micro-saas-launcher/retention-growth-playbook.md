# Retention & Growth Playbook

Load when a micro-SaaS has launched and needs to improve retention, reduce churn, or find growth levers for the first 100-1000 customers.

## Churn Diagnosis Framework

Before fixing churn, classify it. Different churn types need different interventions.

| Churn Type | Signal | Root Cause | Fix Category |
|---|---|---|---|
| Day 1 churn (never activated) | Signs up but never completes setup | Onboarding friction or value not clear | Onboarding |
| Week 1 churn (tried and left) | Used product 1-3 times then stopped | Product didn't deliver promised value quickly enough | Activation |
| Month 1 churn (used then left) | Active for 2-4 weeks then stopped | Found alternative, solved problem manually, or pain wasn't recurring | Value delivery |
| Involuntary churn (card declined) | Payment fails, no user action | Expired cards, insufficient funds | Dunning |
| Downgrade churn (paid to free) | Switches to free tier or lower plan | Not using paid features enough to justify cost | Packaging |

### Churn Investigation Procedure

1. **Pull the data**: Last 30 days of churned users. Export: signup date, last login, feature usage count, plan, cancellation reason (if collected).
2. **Segment by churn type**: Use the table above. If >50% is Day 1 churn, fix onboarding before anything else.
3. **Interview 5 churned users**: Email with "We noticed you cancelled -- would you share why in a 5-minute call?" Expect 10-15% response rate. The patterns from 5 conversations are worth more than 500 survey responses.
4. **Identify the activation metric**: The ONE action that correlates with 30-day retention. For every micro-SaaS, there is a specific action that separates retained users from churned ones. Find it.

## Activation Metrics by Product Type

| Product Type | Likely Activation Metric | Target Timeframe | Retention Correlation |
|---|---|---|---|
| Monitoring/alerting tool | Set up first monitor + receive first alert | Within 24 hours | Users who get an alert in day 1 retain 3x better |
| Content/SEO tool | Run first analysis or generate first output | Within 1 hour | Immediate value demonstration is critical |
| Automation/workflow tool | Create and run first automation successfully | Within 48 hours | Complexity is the enemy; wizard-style setup wins |
| Chrome extension | Use the extension on a real page (not tutorial) | Within 10 minutes | Extensions that require configuration before first use lose 70% of installs |
| API/developer tool | Make first successful API call | Within 30 minutes | Quickstart guide quality directly predicts retention |
| Collaboration tool | Invite first team member | Within 1 week | Single-player mode has no retention moat |

## Dunning (Failed Payment Recovery)

Card failures cause 20-40% of all micro-SaaS churn. Most of it is recoverable.

| Retry Attempt | Timing | Email Content | Recovery Rate |
|---|---|---|---|
| 1st retry | 1 day after failure | No email yet (silent retry) | 15-25% auto-recover |
| 2nd retry | 3 days after failure | Friendly notice: "Your payment didn't go through. Update your card to keep your account active." | 10-15% |
| 3rd retry | 5 days after failure | Urgency: "Your account will be paused in 48 hours. Update payment to avoid interruption." | 5-10% |
| Final retry | 7 days after failure | Last chance: "We've paused your account. Click here to reactivate." | 3-5% |
| Grace period ends | 14 days after failure | Account paused. Data retained for 90 days. | -- |

**Implementation**: Use Stripe's Smart Retries (automatic) + custom email sequence. Lemon Squeezy and Paddle handle dunning natively. Total recovery potential: 30-50% of failed payments.

**Never do**: Don't immediately cancel on first failure. Don't send aggressive/threatening emails. Don't delete user data immediately -- keep it 90 days for reactivation.

## Growth Levers (Ordered by Effort)

For solo founders, pursue these in order. Each builds on the previous.

| Lever | Effort | Expected Impact | When to Deploy |
|---|---|---|---|
| Cancellation survey (1 question) | 1 hour | Identifies top churn reason | Day 1 post-launch |
| Failed payment recovery (dunning) | 2-4 hours | Recover 30-50% of involuntary churn | Week 1 |
| Activation email sequence (3 emails) | 4-8 hours | 20-40% activation improvement | Week 2 |
| Annual pricing option | 1-2 hours | 10-20% of customers switch; reduces churn by 40% for those users | Month 1 |
| In-app upgrade prompts (feature gates) | 4-8 hours | 5-15% free-to-paid conversion | Month 2 |
| Referral program (simple credit) | 1-2 days | 5-15% of new customers from referrals | Month 3 |
| Content/SEO for long-tail keywords | Ongoing | Compounds over 6+ months | Month 2+ |
| Integrations with adjacent tools | 1-2 weeks each | Distribution through partner ecosystems | Month 4+ |

## Retention Email Sequences

### Post-Signup Activation Sequence

| Email | Timing | Subject Line Pattern | Content Focus |
|---|---|---|---|
| Welcome | Immediate | "Welcome -- here's how to get started in 5 minutes" | ONE action to take. Link directly to the activation step. Not a feature tour. |
| Activation nudge | Day 1 (if not activated) | "You're one step away from [specific benefit]" | Show what they'll get after completing setup. Include a GIF or screenshot. |
| Social proof | Day 3 (if not activated) | "How [similar company] uses [product] to [outcome]" | Real customer story or use case. Not testimonials -- show the workflow. |
| Last chance | Day 7 (if not activated) | "Need help getting started?" | Offer personal setup help (founder's email). This converts 5-10% of stuck users. |

### Engagement Maintenance Sequence

| Email | Trigger | Purpose |
|---|---|---|
| Weekly digest | Every Monday | Show what the product did for them that week (stats, saves, alerts). If the product did nothing, that's a churn signal. |
| Feature discovery | 30 days after signup | Introduce ONE advanced feature they haven't used. Not a feature dump. |
| Renewal reminder | 7 days before renewal | Summary of value delivered this billing cycle. Reduces "I forgot what this was" churn. |
| Win-back | 14 days after churn | "We've made improvements since you left" -- only send if you actually improved something relevant to their churn reason. |

## Pricing Iteration Triggers

| Signal | Current Price Issue | Action |
|---|---|---|
| >80% of prospects say "that's reasonable" | Too cheap | Raise price 30-50%. Some should wince. |
| <10% trial-to-paid conversion | May be too expensive OR value not demonstrated | Test lower entry price. If conversion doesn't change, problem is value not price. |
| Customers ask for more features at current price | Underpriced relative to value delivered | Add higher tier, not more features to current tier |
| Enterprise inquiries | Missing upmarket capture | Add "Contact us" tier. Don't publish enterprise pricing. |
| Lifetime deal buyers never return | LTD attracted wrong audience | Stop LTDs. They are customer acquisition for the wrong ICP. |
| Monthly churn >8% but annual churn <2% | Monthly pricing enables casual commitment | Push annual harder: bigger discount (20-30%), make it the default toggle position |

## Unit Economics Health Check

| Metric | Healthy for Micro-SaaS | Warning | Action if Warning |
|---|---|---|---|
| CAC (Customer Acquisition Cost) | <1 month of revenue | 1-3 months | Reduce paid spend, increase organic/referral |
| LTV (Lifetime Value) | >10x CAC | 3-10x CAC | Fix churn first. LTV is a churn problem. |
| LTV:CAC payback period | <3 months | 3-6 months | Cut acquisition costs or raise prices |
| Gross margin | >80% | 60-80% | Check hosting costs, API costs, support time |
| Revenue per employee (solo) | >$10K MRR | $3-10K MRR | Automate support, reduce manual ops |
| MRR growth rate | >10% MoM (first year) | 3-10% MoM | Growth problem. Audit acquisition channels. |

**Solo founder sustainability**: $5K MRR covers a modest salary in most markets. $10K MRR is comfortable. $20K+ MRR is where you can hire help. Don't hire before $15K MRR unless the hire directly generates revenue (e.g., sales).
