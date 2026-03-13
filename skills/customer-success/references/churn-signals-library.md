# Churn Signals Library - Deep Reference

## Leading Indicators (Detectable 90+ Days Before Churn)

These signals appear while the customer still has time and willingness to be saved. Intervention at this stage has a 40-60% save rate when executed within 2 weeks of signal detection.

### Usage Decline Signals

| Signal | Detection Method | Severity | Intervention Window |
|---|---|---|---|
| Core feature usage drops >20% over 30 days | Product analytics trend | High | 2 weeks |
| DAU/MAU ratio drops below 10% | Daily active tracking | High | 2 weeks |
| Login frequency drops >30% over 14 days | Auth log analysis | Medium | 3 weeks |
| API call volume declines >25% | API gateway metrics | High | 2 weeks |
| Session duration drops >40% | Session analytics | Medium | 3 weeks |
| New feature adoption stops (0 new features tried in 60 days) | Feature tracking | Low | 1 month |

Usage decline is the most reliable leading indicator because it reflects behavioral change, not stated intent. Customers who say "everything is fine" while reducing usage are in the most dangerous category -- they have mentally disengaged but have not yet started evaluating alternatives.

### Relationship Decline Signals

| Signal | Detection Method | Severity | Intervention Window |
|---|---|---|---|
| Champion departs or changes roles | LinkedIn monitoring, contact updates | Critical | Immediate (48h) |
| Executive sponsor unresponsive for 60+ days | CRM touchpoint tracking | High | 1 week |
| Meeting no-show rate increases >50% | Calendar tracking | High | 1 week |
| Email response time doubles vs baseline | Email analytics | Medium | 2 weeks |
| QBR attendee seniority decreases | QBR attendance records | Medium | 2 weeks |
| New stakeholders not introduced to CSM | Org chart monitoring | Medium | 3 weeks |

Champion departure is the single highest-severity leading indicator. When a champion leaves, you have 30 days to identify and develop a replacement before institutional memory of your product's value fades. The replacement champion must be someone who personally benefits from your product, not just someone assigned to manage the vendor relationship.

### Competitive Threat Signals

| Signal | Detection Method | Severity | Intervention Window |
|---|---|---|---|
| Competitor names mentioned in support tickets | Ticket keyword scanning | High | 1 week |
| Customer posts RFP or vendor evaluation notice | News monitoring, industry alerts | Critical | Immediate |
| Customer attends competitor events or webinars | Social media monitoring, event lists | Medium | 2 weeks |
| Customer asks for data export or API documentation | Support ticket analysis | High | 1 week |
| Customer requests feature parity comparisons | CSM conversation notes | Medium | 2 weeks |
| Competitor sales rep connects with customer contacts on LinkedIn | LinkedIn monitoring | Low | 3 weeks |

When competitive signals appear, do not respond with FUD (fear, uncertainty, doubt) about the competitor. Instead, accelerate your value demonstration. Schedule an executive alignment meeting focused exclusively on ROI delivered and roadmap fit. Customers evaluating alternatives want to know they matter -- prove it through action, not through disparaging alternatives.

### Organizational Change Signals

| Signal | Detection Method | Severity | Intervention Window |
|---|---|---|---|
| Customer announces reorg or leadership change | News monitoring, customer communications | High | 2 weeks |
| Budget freeze or hiring freeze announced | Earnings calls, news monitoring | High | 2 weeks |
| M&A activity (acquiring or being acquired) | News monitoring | Critical | 1 week |
| Department consolidation affecting your users | Customer communications | High | 2 weeks |
| Customer's industry faces regulatory change | Industry news | Medium | 1 month |

M&A is uniquely dangerous because even satisfied customers churn when acquired by a company that uses a different vendor. The acquirer's vendor almost always wins. When M&A signals appear, immediately identify the acquiring company's tech stack and prepare a migration prevention strategy.

## Lagging Indicators (30 Days or Less Before Churn)

Save rate at this stage drops to 10-20%. Shift strategy from prevention to graceful exit with win-back positioning.

### Terminal Signals

| Signal | Action | Save Probability |
|---|---|---|
| Non-renewal notice received | Executive-to-executive outreach within 24h, emergency remediation offer | 15-20% |
| Downgrade request submitted | Investigate root cause, offer bridge pricing, present ROI data | 20-30% |
| Data export initiated | Do not block. Offer migration assistance. Position for win-back | 5-10% |
| Cancellation page visited (tracked) | Trigger immediate CSM outreach before formal notice | 25-35% |
| Legal team engages on contract termination | Involve your legal + CS Director, focus on terms not retention | 5-10% |
| Payment dispute or chargeback filed | Finance + CS joint response, resolve billing issue first | 10-15% |

Never make data export difficult as a retention tactic. Customers who feel trapped become vocal detractors. Facilitate clean exits and they become future win-back opportunities. Why: 15-20% of churned customers return within 18 months when the exit experience was professional and respectful.

## Multi-Signal Risk Scoring

Individual signals are informative. Combined signals are predictive. Use this weighting system.

### Signal Combination Weights

| Signals Present | Risk Level | Required Response |
|---|---|---|
| 1 leading indicator | Watch | Add to monitoring dashboard, increase touch frequency |
| 2 leading indicators | Elevated | Proactive CSM outreach within 1 week, investigate root cause |
| 3+ leading indicators | High | Trigger SEV-3 escalation, executive involvement, save plan |
| Any leading + any lagging | Critical | Trigger SEV-2 escalation, all-hands save effort |
| 2+ lagging indicators | Terminal | Shift to graceful exit + win-back positioning |

### Compound Signal Patterns (Highest Churn Correlation)

These specific combinations predict churn with >80% accuracy:

1. **The Silent Retreat**: Usage decline + meeting no-shows + email response delays (customer is mentally gone but contractually present)
2. **The Champion Collapse**: Champion departure + no replacement identified within 30 days + usage unchanged (muscle memory keeps usage up temporarily, but no advocate remains)
3. **The Budget Squeeze**: Payment delays + discount requests + reduced user licenses (financial pressure forces vendor consolidation)
4. **The Competitive Shop**: Data export request + competitor mentions + new stakeholder requesting demos (active replacement in progress)
5. **The Reorg Casualty**: Leadership change + exec sponsor replacement + strategy review requests (new leadership evaluates all vendor relationships)

## Intervention Playbooks by Signal Type

### Usage Decline Intervention
1. Pull detailed usage analytics: which features declined, which users reduced activity
2. Identify if decline is seasonal, event-driven, or systemic
3. Reach out to power users directly (not just the contact) to understand behavioral change
4. Offer targeted re-training or onboarding refresh for underutilized features
5. Set 14-day checkpoint to measure recovery

### Champion Departure Intervention
1. Immediately identify 3+ alternative contacts across different departments
2. Schedule introduction meetings within 2 weeks
3. Prepare "value delivered" one-pager for new contacts who lack historical context
4. Identify the departed champion's replacement and prioritize relationship building
5. If no replacement exists, escalate to CS Director for executive-level re-engagement

### Competitive Threat Intervention
1. Do not mention the competitor by name in communications
2. Schedule executive alignment meeting within 1 week
3. Prepare custom ROI analysis specific to this account's usage
4. Identify and address any legitimate gaps the competitor fills
5. Accelerate any pending feature requests or product improvements relevant to this account
6. Offer product roadmap preview under NDA for strategic accounts

## Win-Back Strategy Framework

### Win-Back Timing

| Churn Reason | Optimal Win-Back Timing | Win-Back Approach |
|---|---|---|
| Price/budget | 6-9 months (budget cycle resets) | New pricing tier or bundled offer |
| Feature gap | When the gap feature ships | Personalized "we built this" outreach |
| Champion departure | When new leadership settles (3-6 months) | Fresh executive-to-executive introduction |
| Competitor switch | 9-12 months (honeymoon period ends) | Check-in: "How is the transition going?" |
| M&A consolidation | 12-18 months (integration chaos peaks) | Offer as relief from integration pain |

### Win-Back Contact Rules
- First contact at 90 days post-churn: brief, no-pressure check-in
- Share relevant industry content at 6 months (not product marketing)
- Offer a "welcome back" incentive only when the customer initiates conversation
- Never disparage their current vendor -- it validates their choice to leave

## Churn Post-Mortem Template

Complete within 14 days of confirmed churn. Required fields: account name, ACV, lifetime (months), customer-stated churn reason, internal root cause assessment, leading indicators detected vs missed, intervention timeline and effectiveness, preventable Y/N with reasoning, specific process improvement, win-back potential (H/M/L) with assigned owner.

Conduct post-mortems for every churned account above $10K ACV. Share findings monthly with CS leadership. Pattern recognition across post-mortems is the highest-leverage improvement mechanism for a CS organization.
