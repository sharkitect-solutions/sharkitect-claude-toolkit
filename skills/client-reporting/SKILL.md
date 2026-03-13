---
name: client-reporting
description: "Use when creating client-facing reports, progress updates, milestone documentation, retainer reports, ROI summaries, or project status dashboards. Use when building QBR decks, writing executive summaries, or designing client-facing KPI dashboards for service businesses. Do NOT use for internal team reports, analytics dashboards for internal use, marketing performance reports (use marketing-demand-acquisition), or financial statements (use smb-cfo)."
---

# Client Reporting & Deliverables

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/report-templates.md` | Building weekly/monthly status reports, project completion reports, retainer activity reports, needing structural templates | ROI calculations, dashboard design, visualization decisions |
| `references/roi-calculation-guide.md` | Quantifying value delivered, building ROI summaries, preparing renewal justification, calculating cost avoidance | Status report structure, dashboard layout, template formatting |
| `references/visualization-standards.md` | Designing client dashboards, choosing chart types, formatting data for non-technical audiences, building KPI displays | Report narrative writing, ROI calculations, template structure |

## Scope Boundary

| Domain | This Skill Covers | Use Instead |
|--------|-------------------|-------------|
| Financial statements | Client-facing revenue impact summaries only | smb-cfo |
| Internal team metrics | -- | Internal ops tooling |
| Marketing analytics | Campaign ROI as reported to client only | marketing-demand-acquisition |
| Sales proposals / renewals | Delivered-value evidence only | sales-enablement |
| Customer health scores | Report presentation only | customer-success |

---

## Report Type Framework

Every client engagement generates reporting obligations. Match report type to engagement structure -- mismatched reports erode trust faster than missing reports.

### Report Types by Engagement Model

| Engagement Type | Primary Report | Cadence | Secondary Reports |
|----------------|---------------|---------|-------------------|
| Project (fixed scope) | Milestone report | At each milestone | Weekly status, completion report |
| Retainer (ongoing hours) | Retainer activity report | Monthly | Weekly status, QBR deck quarterly |
| Managed service | KPI dashboard | Real-time/weekly | Monthly summary, QBR deck quarterly |
| Consulting engagement | Progress report | Bi-weekly | Deliverable acceptance docs, ROI summary |
| Hybrid (project + retainer) | Combined status report | Weekly | Milestone reports, monthly retainer summary |

### The Report Hierarchy

Every report follows this information density hierarchy. Violating the order creates confusion:

1. **Verdict first** -- One sentence: are we on track, ahead, or behind? Traffic light status.
2. **Evidence** -- The 3-5 metrics or milestones that support the verdict.
3. **Context** -- Why those numbers look the way they do.
4. **Actions** -- What happens next, who owns it, by when.
5. **Appendix** -- Raw data, detailed breakdowns, for clients who want to dig deeper.

Clients read top-down and stop when satisfied. Executives stop at verdict. Managers read through actions. Analysts reach the appendix. Structure every report so each audience gets what they need at their stopping point.

---

## Status Report Architecture

### Traffic Light System

Use a three-color system consistently across all reports. Define thresholds once at engagement kickoff and never change them mid-project without written client agreement.

| Status | Definition | Trigger |
|--------|-----------|---------|
| Green | On track. No intervention needed. | All KPIs within target range, timeline on schedule, budget within 90-100% |
| Yellow | At risk. Monitoring closely. Remediation underway. | Any KPI 10-20% off target, timeline slipping 1-2 weeks, budget 100-115% |
| Red | Off track. Client action or decision required. | Any KPI >20% off target, timeline slipping >2 weeks, budget >115%, blocker unresolved >5 days |

Never use yellow as a permanent state. Yellow means "this will become green or red within two reporting cycles." If something stays yellow for three consecutive reports, it is red -- you are avoiding a hard conversation.

### Metric Selection by Engagement Type

**Project engagements:** Milestones completed vs planned, budget consumed vs remaining, open blockers count, scope change count, velocity trend.

**Retainer engagements:** Hours utilized vs allocated, deliverables completed, response time metrics, strategic initiatives progress, value highlights.

**Managed services:** Uptime/availability, incident count and severity, SLA compliance rate, performance trends, optimization recommendations implemented.

Select 5-7 metrics maximum per report. More than 7 triggers "The Data Dump" anti-pattern -- the client stops reading and starts scanning, missing the metrics that actually matter.

---

## Milestone Documentation

### Deliverable Acceptance Framework

Every milestone needs acceptance criteria defined before work begins. Retroactive acceptance criteria invite scope disputes.

**Acceptance document structure:**
1. Milestone name and identifier
2. Deliverable description (what was built/delivered)
3. Acceptance criteria (specific, measurable, agreed upon at kickoff)
4. Testing/review evidence (screenshots, test results, user sign-off)
5. Deviation log (anything that differs from original scope, with approval reference)
6. Sign-off block (client name, date, conditional or unconditional)

### Change Log Discipline

Maintain a running change log visible to the client. Every scope modification gets an entry:

| Date | Change Description | Requested By | Impact (Timeline/Budget) | Approved By | Reference |
|------|-------------------|-------------|------------------------|-------------|-----------|
| 2026-01-15 | Added user authentication module | Client PM | +2 weeks, +$8K | Client Director, email 1/14 | CR-003 |

Never absorb scope changes silently. Silent absorption creates expectation drift -- the client believes the original scope included the additions. When the next change request arrives, they will resist any impact assessment because "last time it was included."

---

## ROI Summary Construction

### Before/After Framework

Structure every ROI report as a before/after comparison. Humans process contrast far more effectively than absolute numbers.

| Metric | Before (Baseline) | After (Current) | Change | Annualized Impact |
|--------|-------------------|-----------------|--------|-------------------|
| Average response time | 4.2 hours | 1.1 hours | -74% | 1,560 hours saved/year |
| Error rate | 8.3% | 1.7% | -80% | $127K cost avoidance |
| Monthly revenue from channel | $45K | $78K | +73% | $396K incremental |

### Attribution Methodology

Be explicit about what you can and cannot attribute. Over-claiming kills credibility when the client's finance team audits the numbers.

**Direct attribution:** Changes measured in systems you control, before/after with no other variables changing. Strongest claim.
**Contributory attribution:** Your work was one of multiple factors. State the methodology: "We contributed to a 40% increase alongside the client's internal team expansion."
**Estimated attribution:** Model-based. State assumptions explicitly. "Assuming 60% of the efficiency gain is attributable to the new system, based on workflow analysis."

Never claim 100% attribution for outcomes influenced by multiple factors. "The Data Dump" anti-pattern's cousin is "The Credit Grab" -- claiming full credit for shared outcomes. It works once. The second time, the client's team pushes back and your credibility is permanently damaged.

### Value Quantification for Intangibles

When outcomes are not directly monetary, convert to business terms:

- **Time saved** -- Hours saved x blended hourly rate of affected employees
- **Error reduction** -- Error rate reduction x average cost per error (rework hours + customer impact)
- **Speed improvement** -- Cycle time reduction x revenue per cycle or opportunity cost of delay
- **Risk reduction** -- Probability reduction x estimated impact. Frame as insurance value, not guaranteed savings.
- **Employee satisfaction** -- Attrition reduction x replacement cost (50-200% of annual salary per role)

---

## Retainer Reporting

### Hours vs Value Framing

The single most damaging pattern in retainer reporting is leading with hours consumed. Hours are inputs. Clients pay for outcomes. Lead with outcomes delivered, then show hours as context.

**Wrong structure:** "This month we used 87 of 120 hours. Here is what we did."
**Right structure:** "This month we delivered three campaign launches generating 2,400 leads. We achieved this efficiently using 87 of your 120 allocated hours."

### Utilization Presentation

| Utilization Range | Client Perception | How to Frame |
|-------------------|------------------|--------------|
| 90-100% | "Am I getting enough?" | Highlight value density. Propose scope expansion if demand exceeds allocation. |
| 70-89% | Ideal zone | Show outcomes per hour. Bank remaining hours for strategic initiatives. |
| 50-69% | "Am I wasting money?" | Proactively propose strategic projects. Show roadmap for utilizing remaining capacity. |
| Below 50% | "I should downgrade" | Trigger immediate conversation. Either increase scope or right-size the retainer. |

Never wait for the client to notice underutilization. If utilization drops below 60% for two consecutive months, proactively propose a scope adjustment or strategic initiative. Waiting for the client to ask "why am I paying for hours you're not using?" puts you in a defensive position you cannot recover from gracefully.

### Scope vs Effort Visualization

Show a 2x2 matrix quarterly:

```
                    Low Effort    |    High Effort
                 ─────────────────┼──────────────────
  High Value  │  Quick Wins       │  Strategic Work
              │  (celebrate)      │  (justify)
              ├───────────────────┼──────────────────
  Low Value   │  Maintenance      │  Scope Creep Risk
              │  (necessary)      │  (flag + discuss)
```

This matrix makes resource allocation discussions objective. When a client sees 40% of hours going to "high effort, low value," they understand why a process change or scope adjustment benefits both parties.

---

## Client Dashboard Design

### KPI Selection Principles

Select dashboard KPIs using the CLEAR test:

- **C**lient-meaningful: The client can explain this metric to their boss without your help.
- **L**eading: The metric predicts future outcomes, not just records past activity.
- **E**videnced: You can source the number from a system of record, not an estimate.
- **A**ctionable: A change in this metric triggers a specific decision or action.
- **R**elevant: The metric connects to the client's stated business objectives from kickoff.

If a metric fails any criterion, it belongs in the appendix, not the dashboard.

### Refresh Cadence

| Data Type | Refresh Frequency | Why |
|-----------|-------------------|-----|
| Operational metrics (uptime, response time) | Real-time or daily | Enables immediate incident response |
| Performance metrics (conversions, leads, revenue) | Weekly | Smooths daily noise while catching trends |
| Strategic metrics (ROI, LTV, market share) | Monthly or quarterly | Requires sufficient sample size for meaningful comparison |

Never refresh strategic metrics weekly. Weekly fluctuations in ROI or market share create noise that clients misinterpret as signal. "The Vanity Report" anti-pattern often stems from cherry-picking the best weekly snapshot for a metric that should only be evaluated monthly.

---

## Communication Cadence & Escalation

### Cadence by Report Type

| Report | Timing | Audience | Length |
|--------|--------|----------|--------|
| Weekly status | Same day/time every week (Tuesday/Wednesday) | Project team + client PM | 1 page max |
| Monthly summary | Within 5 business days of month-end | Client PM + director | 2-3 pages |
| Milestone report | Within 2 business days of milestone completion | All stakeholders | 1-2 pages + appendix |
| QBR deck | Quarterly, scheduled 2 weeks in advance | Executive sponsor + team | 10-15 slides max |
| ROI summary | Semi-annually or at project completion | Executive sponsor + finance | 2-3 pages |

### Bad News Delivery Framework

Bad news gets worse with age. Deliver early, directly, with a recovery plan: (1) State the issue clearly -- no euphemisms, (2) Own what is yours, (3) Quantify the impact in days/dollars, (4) Present the recovery plan with owners and revised timeline, (5) State what you need from the client. Never bury bad news between two positive updates.

### Escalation Triggers

Escalate from routine reporting to direct communication when: any metric moves green to red in one period, budget projected to exceed 110%, blocker unresolved >5 business days, scope change impacts timeline >1 week, client stakeholder departure/reorg, or third consecutive yellow on any metric.

---

## Named Anti-Patterns

### The Data Dump
Sending clients raw data exports, unfiltered analytics, or 20-page reports with no narrative. Clients have 5 minutes for your report, not 50. **Detect:** Report exceeds 3 pages without an executive summary. More than 10 metrics on a single page. Client asks "what does this mean?" after reading the report. **Fix:** Apply the report hierarchy (verdict-evidence-context-actions-appendix). Executive summary on page one. Raw data in appendix only.

### The Vanity Report
Only presenting metrics that look good while omitting or burying unfavorable results. **Detect:** Every metric in the report is green or improving. No risks, no blockers, no "areas for improvement." Report does not mention any metric that declined. **Fix:** Include at least one challenge or risk in every report. Clients who only hear good news stop trusting the messenger. Present unfavorable metrics with context and a remediation plan.

### The Status Quo Syndrome
Copy-pasting last week's report with updated numbers. No new insights, no trend analysis, no recommendations. **Detect:** Report narrative is identical to prior period except for numbers. "Highlights" section is the same three items for four consecutive weeks. No forward-looking content. **Fix:** Every report must include at least one new insight, one trend observation, and one recommendation. If nothing changed, explain why stability is notable.

### The Missing Context
Presenting numbers without explaining what they mean, why they changed, or what action they imply. **Detect:** Report contains metrics without comparison (no vs target, vs prior period, vs benchmark). Client has to ask follow-up questions to understand every metric. **Fix:** Every metric gets three comparisons: vs target, vs prior period, vs trend. Every deviation gets a one-sentence explanation.

### The Delayed Bad News
Knowing a problem exists but waiting to report it, hoping it will resolve itself. **Detect:** Problems appear in reports weeks after internal teams knew about them. Recovery plans are presented alongside the problem announcement with suspiciously detailed timelines. **Fix:** Report problems within one business day of identification. A problem reported early with "we are investigating" is vastly better than a problem reported late with "here is what we did."

### The Scope Creep Enabler
Absorbing unrequested additions into deliverables without documenting the scope expansion. **Detect:** Deliverables consistently exceed original scope. Hours consistently exceed estimates but no change requests are filed. Team describes "small additions" that were "easier to just do." **Fix:** Log every out-of-scope request in the change log, even if delivered at no additional cost. Visibility protects both parties at renewal.

---

## Rationalization Table

| Shortcut | Why It Seems OK | Why It Fails | Do This Instead |
|----------|----------------|--------------|-----------------|
| "The client never reads the reports anyway" | Low engagement with past reports suggests they are not valued | When something goes wrong, the client will cite lack of reporting as evidence of poor communication. Reports are insurance, not entertainment. | Send concise reports consistently. Redesign the format if engagement is low. Ask the client what they actually need. |
| "We'll catch up on reporting next month" | Skipping one cycle saves time when the team is slammed | Skipped reports create information gaps that compound. The catch-up report is twice the work and half the quality. | Reduce scope of the report before skipping it entirely. A three-sentence email update beats silence. |
| "The numbers will look better next week" | Short-term dip might self-correct | Delayed reporting trains the client to distrust your timeline. When numbers do improve, the client wonders what you hid during the dip. | Report current numbers with context. "Metric X declined 12% this week due to [reason]. We expect recovery by [date] based on [evidence]." |
| "We can just add that to the retainer" | Small requests are easier to absorb than to document | Accumulated un-documented additions set false expectations for what the retainer includes. At renewal, the client expects expanded scope at the same price. | Log every addition in the change log. Deliver it, but make the scope expansion visible. |
| "The executive summary covers it" | Writing detailed sections takes time nobody has | When the executive summary says "on track" but a stakeholder asks about a specific metric, you have no supporting detail. Credibility depends on depth being available when requested. | Write the executive summary last. Build the detail first, then distill. The summary is the roof, not the foundation. |

---

## Red Flags Checklist

Stop and check when any of these conditions arise. Each flag indicates a reporting process failure that erodes client trust.

- [ ] **No report sent for 2+ consecutive scheduled cycles** -- The client will interpret silence as either incompetence or something being hidden. Catch up immediately with a consolidated update.
- [ ] **Client learns about a problem from someone other than you** -- Trust is fundamentally damaged. The recovery requires direct acknowledgment and a commitment to proactive communication going forward.
- [ ] **Report contains metrics you cannot source from a system of record** -- Estimated metrics without disclosure invite audit failure. Label every estimate explicitly with methodology.
- [ ] **Same blocker appears in 3+ consecutive reports without resolution** -- The blocker is not being managed, it is being reported. Escalate ownership or remove the blocker from the report and replace with the escalation action.
- [ ] **Client has not acknowledged or responded to reports for 30+ days** -- Disengagement is a churn signal. Proactively ask: "Are these reports meeting your needs? What would make them more useful?"
- [ ] **Dashboard shows all green while team internally tracks yellow/red items** -- Internal and external views are diverging. This is "The Vanity Report" in action. Reconcile immediately.
- [ ] **Retainer utilization below 50% for two consecutive months without proactive discussion** -- The client is questioning the value. Propose scope adjustments before they do.
- [ ] **No ROI or value summary has been presented in 6+ months of engagement** -- The relationship is running on inertia. At renewal, there will be no evidence to justify continued investment.
