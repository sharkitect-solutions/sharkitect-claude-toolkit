---
name: customer-success
description: "Use when managing post-sale customer relationships, building health scores, predicting churn, preparing QBRs, designing renewal playbooks, identifying expansion revenue, creating customer segmentation models, building NPS/CSAT programs, or designing escalation frameworks. Use when analyzing customer lifecycle stages from onboarding through advocacy. Do NOT use for lead generation, prospecting, or pre-sale activities (use lead-research-assistant). Do NOT use for deal closing, proposal writing, or sales pipeline management (use sales-enablement). Do NOT use for product feature development or roadmap planning."
---

# Customer Success Management

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/health-scoring-framework.md` | Building or refining health scores, defining thresholds, setting up automation rules, benchmarking account health | General renewal conversations, QBR prep without scoring focus |
| `references/qbr-playbook.md` | Preparing quarterly business reviews, structuring executive presentations, defining QBR cadence, measuring QBR effectiveness | Health scoring without review context, churn analysis |
| `references/churn-signals-library.md` | Analyzing churn risk, building early warning systems, designing intervention playbooks, conducting churn post-mortems | Healthy account expansion planning, new customer onboarding |

## Scope Boundary

| Domain | This Skill Covers | Use Instead |
|---|---|---|
| Pre-sale leads | -- | lead-research-assistant |
| Deal closing / proposals | -- | sales-enablement |
| Product roadmap decisions | Customer feedback synthesis only | Product management |
| Support ticket resolution | Escalation framework + trends | Support engineering |
| Billing disputes | Churn signal detection only | Finance / billing ops |
| Marketing campaigns | Advocacy program referrals only | marketing-demand-acquisition |

## Customer Lifecycle Stages

Define every account's current stage. Stage determines which playbooks apply and which metrics matter.

### Stage Definitions

1. **Onboarding** (Day 0-90): First-value delivery. Measure time-to-first-value, milestone completion rate, stakeholder training completion. Exit criteria: customer achieves predefined "aha moment" metric.
2. **Adoption** (Day 90-180): Deepening usage. Measure feature adoption breadth, active user growth, support ticket ratio (declining = healthy). Exit criteria: usage patterns stabilize above engagement baseline.
3. **Expansion** (Day 180-365): Value multiplication. Measure upsell pipeline, cross-sell signals, usage approaching plan limits. Exit criteria: expansion opportunity identified or account stabilizes at current tier.
4. **Renewal** (90 days before contract end): Retention execution. Measure renewal likelihood score, stakeholder sentiment, competitive threat level. Exit criteria: contract renewed or churn post-mortem completed.
5. **Advocacy** (Post-renewal, health score 80+): Revenue multiplier. Measure referral generation, case study participation, community engagement, NPS promoter status. Exit criteria: ongoing -- advocates cycle back through expansion.

Never skip stages. An account in Onboarding that requests expansion still completes onboarding milestones first. Skipping stages creates fragile relationships that collapse at renewal. Why: incomplete onboarding is the #1 predictor of first-year churn across all SaaS cohort studies.

## Customer Health Score Framework

Health scores are multi-dimensional. A single composite number hides critical risk signals. Track five dimensions independently, then combine.

### Five Dimensions

1. **Product Usage** (Weight: 30%): DAU/MAU ratio, feature adoption depth, login frequency trend (7/30/90 day windows), time-in-app trajectory
2. **Support Health** (Weight: 15%): Ticket volume trend (rising = concern), CSAT on resolved tickets, escalation rate, mean time to resolution satisfaction
3. **Financial Health** (Weight: 20%): Payment timeliness (days past due), contract value trend, expansion purchase history, discount dependency ratio
4. **Relationship Health** (Weight: 25%): Executive sponsor engagement frequency, champion identification status, multi-threading depth (contacts engaged across departments), NPS response and score
5. **Onboarding Health** (Weight: 10%, decays after Day 180): Time-to-first-value vs benchmark, milestone completion percentage, training adoption rate, implementation satisfaction score

### Scoring Methodology

Use the **weighted composite with floor override** method:

1. Score each dimension 0-100 based on metric thresholds
2. Apply dimension weights to compute composite score
3. Apply the floor override rule: if ANY single dimension scores below 40, cap the composite at 59 regardless of other dimensions. Why: a single critical failure dimension predicts churn more reliably than a blended average suggests.

### Threshold Definitions

- **Green (80-100)**: Healthy. Expansion-ready. Assign advocacy playbook.
- **Yellow (60-79)**: Monitor. Assign proactive outreach cadence. Investigate declining dimensions.
- **Red (0-59)**: At-risk. Trigger intervention playbook within 48 hours. Escalate to CS leadership.

### Score Decay Rule

When data points go missing for 30+ days, decay that dimension by 5 points per missing month. Why: absence of data is itself a signal -- disengaged customers stop generating telemetry before they stop paying.

## Churn Signal Detection

### Leading Indicators (90+ days before churn)

Detect these early and intervene before the customer mentally commits to leaving:

- **Usage decline**: >20% drop in core feature usage over 30-day window
- **Champion departure**: Primary contact leaves company or changes roles
- **Stakeholder ghosting**: Meeting no-shows increase, email response time doubles
- **Competitor signals**: Mentions of competitor names in support tickets or calls, RFP activity
- **Budget events**: Reorg announcements, hiring freezes, M&A activity at customer org
- **Login pattern shift**: Power users reducing frequency while casual users stay flat (indicates loss of internal advocacy)

### Lagging Indicators (30 days or less)

These indicate the decision is likely made. Shift from prevention to win-back:

- Non-renewal notice or downgrade request
- Data export or API migration activity
- Cancellation page visits or inquiry
- Payment disputes or chargebacks
- Legal team engagement on contract terms

Prioritize leading indicators in all dashboards and alerts. Lagging indicators are useful for post-mortem accuracy, not prevention. Why: by the time lagging indicators fire, the customer has already evaluated alternatives.

## Renewal Playbook

### 90-Day Renewal Cadence

**T-90 days (Assessment)**:
- Pull full health score report with dimension breakdown
- Identify all open support issues and resolution timeline
- Confirm executive sponsor and decision-maker contacts are current
- Document value delivered since last renewal in quantified terms

**T-60 days (Alignment)**:
- Conduct renewal-focused QBR (use QBR playbook reference)
- Present ROI summary: investment vs. measured outcomes
- Discuss upcoming roadmap items aligned to customer goals
- Surface expansion opportunities if health score is Green
- Address any Yellow/Red dimensions directly with remediation plan

**T-30 days (Execution)**:
- Send renewal proposal with pricing and terms
- Confirm decision-maker approval timeline
- Remove all open blockers (support tickets, feature gaps, billing issues)
- Prepare escalation path if renewal is at risk

**T-7 days (Close)**:
- Final follow-up. Escalate to CS Director if unsigned.
- Document outcome regardless: renewed, churned, or downgraded.

### Risk Mitigation by Dimension

| Failing Dimension | Intervention |
|---|---|
| Usage declining | Conduct re-onboarding sprint, assign adoption specialist |
| Support health red | Executive apology + dedicated support engineer for 30 days |
| Financial stress | Offer bridge pricing, defer expansion, reduce scope |
| Relationship gaps | Multi-thread aggressively, secure new executive sponsor |
| Onboarding stalled | Reset onboarding plan, assign implementation PM |

## Expansion Revenue Framework

Expansion revenue compounds retention value. A 110% net revenue retention means the business grows even with some churn.

### Upsell Triggers

- Usage consistently >80% of plan limits for 30+ days
- Feature requests for capabilities in higher tiers
- New departments or teams requesting access
- Customer achieves ROI milestone ahead of schedule
- Health score sustained Green for 90+ days

### Cross-Sell Signals

- Customer mentions adjacent pain points in QBRs or support conversations
- Usage patterns suggest workflow gaps your other products fill
- Industry peers adopt complementary products (social proof readiness)
- Customer's tech stack has integration opportunities with your other offerings

### Expansion Timing Rule

Never pitch expansion to a Yellow or Red account. Fix health first. Why: expansion attempts on unhealthy accounts accelerate churn by signaling you prioritize revenue over their success. The sole exception: when expansion directly solves the health problem (e.g., upgrading support tier for a support-health-red account).

## Customer Segmentation Model

### By Annual Contract Value (ACV)

| Segment | ACV Range | CS Model | Touch Frequency |
|---|---|---|---|
| Enterprise | >$100K | Named CSM, dedicated | Weekly |
| Mid-Market | $25K-$100K | Named CSM, pooled (1:25) | Bi-weekly |
| SMB | $5K-$25K | Pooled CSM (1:75) | Monthly |
| Self-Serve | <$5K | Tech-touch only | Automated |

### By Health Score

| Health | Action Model |
|---|---|
| Green 80+ | Expansion-focused, advocacy programs, case study candidates |
| Yellow 60-79 | Proactive monitoring, bi-weekly check-ins, risk remediation |
| Red 0-59 | Intervention mode, executive escalation, save playbook activated |

### By Lifecycle Stage

Apply stage-appropriate playbooks. An Enterprise account in Onboarding gets different treatment than an Enterprise account in Renewal. Segment by value first (determines resource allocation), then by health (determines urgency), then by stage (determines playbook).

## Escalation Framework

### Severity Levels

| Level | Criteria | Response SLA | Owner |
|---|---|---|---|
| SEV-1 | Revenue at risk >$100K, exec sponsor escalation, legal threat | 4 hours | VP of CS |
| SEV-2 | Health score Red for 30+ days, renewal at risk, multi-issue compound | 24 hours | CS Director |
| SEV-3 | Single dimension Red, feature blocker, support dissatisfaction | 48 hours | Senior CSM |
| SEV-4 | Yellow trending down, minor dissatisfaction, process complaint | 1 week | Assigned CSM |

### Escalation Path

1. CSM identifies trigger condition from severity matrix
2. CSM documents: account name, health score, failing dimensions, business impact estimate, recommended action
3. CSM notifies escalation owner via designated channel (not email -- use incident management tooling)
4. Escalation owner acknowledges within SLA window
5. Joint action plan created within 24 hours of acknowledgment
6. Customer contacted within 48 hours with remediation plan
7. Escalation remains open until health score exits Red or account renews

Never escalate without a recommended action. Escalations without recommendations waste leadership cycles and delay intervention. Why: the CSM closest to the account has the best context for initial remediation strategy.

## NPS/CSAT Program Design

### Survey Cadence

- **Relationship NPS**: Quarterly for Enterprise, semi-annually for Mid-Market, annually for SMB
- **Transactional CSAT**: After every support ticket resolution, after onboarding milestones, after QBRs
- **Post-churn survey**: Within 7 days of cancellation (critical for post-mortem data)

### Response Action Framework

| Score Range | Classification | Required Action |
|---|---|---|
| NPS 9-10 | Promoter | Invite to advocacy program, request referral, case study candidate |
| NPS 7-8 | Passive | Investigate barriers to delight, assign improvement plan |
| NPS 0-6 | Detractor | Trigger escalation framework SEV-3 minimum, personal outreach within 48h |

Close the loop on every detractor response within 5 business days. Why: detractors who receive follow-up are 3x more likely to remain customers than detractors who are ignored (Bain & Company research).

## Rationalization Table

| Situation | Wrong Approach | Right Approach | Why |
|---|---|---|---|
| Champion leaves customer org | Continue emailing departed contact | Immediately multi-thread: identify 3+ new contacts across departments within 2 weeks | Single-threaded relationships are the #1 controllable churn factor |
| NPS detractor response received | Log it in dashboard, review next quarter | Personal outreach within 48 hours, escalate to SEV-3 | Speed of response to negative feedback directly correlates with save rate |
| Usage drops 25% month-over-month | Wait to see if it recovers next month | Trigger proactive outreach within 72 hours, investigate root cause | Usage recovery without intervention occurs <15% of the time |
| Customer requests discount at renewal | Grant discount to save the deal | Quantify delivered ROI first, negotiate on scope not price | Discount dependency creates downward revenue spiral and trains customers to threaten churn |
| Account health is Green across all dimensions | Reduce touch frequency to focus on Red accounts | Maintain cadence and pivot to expansion/advocacy motions | Neglecting healthy accounts turns Green into Yellow within 2 quarters |

## Red Flags Checklist

- [ ] Health score calculated using a single dimension only (usage OR NPS, never both) -- composite scoring with floor override is mandatory
- [ ] No executive sponsor identified for accounts >$25K ACV -- single-threaded Enterprise accounts have 3x churn rate
- [ ] QBRs consist of feature demos without customer goal review -- this is "The QBR Theater" anti-pattern
- [ ] Churn analysis uses only lagging indicators -- by the time cancellation requests arrive, intervention window has closed
- [ ] Renewal process starts at T-30 instead of T-90 -- insufficient time for risk remediation if issues surface
- [ ] Expansion pitched to Red/Yellow accounts -- signals revenue-first mentality and accelerates churn
- [ ] NPS detractors not contacted within 5 business days -- unacknowledged negative feedback compounds into advocacy against your product
- [ ] Health scores not decayed for missing data -- stale Green scores create false confidence

## Named Anti-Patterns

### The Happy Ear Syndrome
Assuming silence equals satisfaction. Disengaged customers stop complaining before they stop paying. Silence is the most dangerous churn signal because it generates no alerts in reactive systems. Require proactive health checks regardless of inbound signal volume.

### The Logo Retention Illusion
Celebrating customer count retention while ignoring net revenue retention. Keeping 95% of logos means nothing if the retained accounts all downgraded. Track gross revenue retention (without expansion) and net revenue retention (with expansion) separately. The logo number goes on the slide deck; the revenue number drives strategy.

### The QBR Theater
Presenting a 45-minute product demo, calling it a Quarterly Business Review, and wondering why executives stop attending. QBRs exist to align on customer goals and demonstrate value delivered against those goals. If the customer talks less than 40% of the meeting, it is a sales pitch, not a QBR.

### The Reactive Firefighter
Only engaging with accounts after they turn Red. By the time a health score hits Red, the customer has been dissatisfied for weeks or months. Proactive CS means running expansion plays on Green accounts and remediation plays on Yellow accounts -- not waiting for fires.

### The Feature Request Trap
Treating every feature request as a churn risk and escalating to product. Most feature requests are aspirational, not existential. Distinguish between "nice to have" requests and "I will leave without this" blockers by asking: "If we never build this, what happens to your workflow?" The answer separates noise from signal.
