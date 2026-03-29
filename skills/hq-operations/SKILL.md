---
name: hq-operations
description: >
  Use when creating or auditing Sharkitect Digital SOPs, detecting operational drift from documented
  procedures, managing capacity state assessments, or enforcing the 10-field SOP template standard.
  Covers process documentation, operational health monitoring, and capacity planning.
  NEVER use for project planning or timeline management (use project-manager agent),
  sprint facilitation or agile ceremonies (use scrum-master agent),
  or general business analysis without operational focus (use business-analyst agent).
version: 0.1.0
---

# HQ Operations — SOP Management & Operational Health

## Scope Boundary

| Request | This Skill | Use Instead |
|---------|-----------|-------------|
| "Create/audit an SOP" | YES | - |
| "Check operational health" | YES | - |
| "Assess team capacity" | YES | - |
| "Detect SOP drift or compliance issues" | YES | - |
| "Diagnose structural/architectural issues" | NO | hq-strategic-ops |
| "Build a technology solution" | NO | hq-tech-strategy |
| "Financial analysis of operations" | NO | smb-cfo |
| "Project planning/timeline" | NO | project-manager agent |
| "Sprint facilitation or agile ceremonies" | NO | scrum-master agent |
| "General business analysis without ops focus" | NO | business-analyst agent |

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/sop-template.md` | Creating or auditing any SOP, capacity assessment | General project management without SOP focus |
| `references/operational-excellence.md` | Diagnosing SOP failures, designing improvement processes, applying cross-domain frameworks (TPS, ITIL, SRE, PDCA, Poka-Yoke) | Quick compliance checks that don't need root cause analysis |
| `references/drift-detection.md` | Running drift audits, investigating SOP non-compliance, onboarding new SOPs into review cycles | Creating new SOPs from scratch (use sop-template.md instead) |

## Paired Agents

Launch these agents (Task tool) for execution:
- `business-analyst` — Process analysis, requirements gathering, bottleneck identification
- `project-manager` — Timeline planning, resource allocation, milestone tracking
- `scrum-master` — Sprint facilitation, velocity tracking, impediment removal

Use this skill directly (without agent) for:
- Quick SOP compliance checks (does existing SOP follow 10-field template?)
- Capacity state classification (Green/Yellow/Red)
- Operational drift detection (is the team following documented SOPs?)
- Routing operational requests to the correct agent

## SOP Decision Tree

```
OPERATIONAL REQUEST RECEIVED
  |
  +-- Is this about CREATING or UPDATING a documented procedure?
  |     YES --> Use 10-field SOP template from companion file
  |     |       Launch business-analyst if process analysis needed first
  |     NO  --> Continue
  |
  +-- Is this about TRACKING or MANAGING a project timeline?
  |     YES --> Route to project-manager agent (not this skill)
  |     NO  --> Continue
  |
  +-- Is this about TEAM PROCESS or SPRINT MANAGEMENT?
  |     YES --> Route to scrum-master agent (not this skill)
  |     NO  --> Continue
  |
  +-- Is this about OPERATIONAL HEALTH or CAPACITY?
  |     YES --> Run capacity state assessment (below)
  |     NO  --> Continue
  |
  +-- Is this about auditing COMPLIANCE with existing SOPs?
  |     YES --> SOP drift detection audit (load drift-detection.md)
  |     |       Classify issue: Incident (one-off) vs Problem (3+ occurrences)
  |     |       If Problem: load operational-excellence.md for root cause analysis
  |     NO  --> Continue
  |
  +-- Is this about IMPROVING an existing SOP after failure?
  |     YES --> Load operational-excellence.md
  |     |       Apply: 5 Whys (diagnosis) --> Error Budget (tolerance) --> PDCA (improvement) --> Poka-Yoke (prevention)
  |     NO  --> May not be an operations task -- check hq-orchestrator for routing
```

## Capacity State Framework

Assess operational capacity across three states:

| State | Definition | Indicators | Action |
|-------|-----------|------------|--------|
| **Green** | Operating within capacity, SOPs followed, no blockers | <80% utilization, all SOPs current, no overdue tasks | Continue normal operations |
| **Yellow** | Approaching limits, some drift detected | 80-95% utilization, 1-2 stale SOPs, minor delays | Triage non-essential work, update stale SOPs |
| **Red** | Over capacity, significant drift, blockers present | >95% utilization, multiple stale SOPs, overdue deliverables | Stop new intake, remediate blockers, CEO escalation |

**Seasonal adjustment:** Review capacity states against known demand cycles (e.g., Q4 client ramp, January slow-down). A state that looks Yellow in isolation may be normal-for-season or abnormal-for-season. Always contextualize.

## SOP Audit Quick Check

For any existing SOP, verify these 10 fields are present and current:

1. **Purpose** — Why does this SOP exist?
2. **Owner** — Who maintains it?
3. **Trigger** — What initiates this procedure?
4. **Inputs** — What's needed to start?
5. **Steps** — The procedure itself (numbered, specific)
6. **Tools** — What tools/systems are used?
7. **Outputs** — What's produced?
8. **Edge Cases** — What can go wrong and how to handle it?
9. **Review Cadence** — How often is this reviewed?
10. **Last Reviewed** — When was it last verified?

Missing fields = non-compliant SOP. Route to business-analyst for remediation.

## Anti-Patterns (The 8 Named Operational Failures)

### 1. "Process Without SOP" (Operational Debt)
Running a process 3+ times without documenting it. Undocumented repeating processes are operational debt that compounds: each execution accumulates tribal knowledge that lives only in one person's head. **Consequence:** When that person is unavailable, the process fails or runs at 50-60% quality. Organizations with >30% undocumented processes experience 2-3x longer recovery times from staff transitions.

### 2. "SOP Without Owner" (The Orphan Document)
An SOP exists but nobody is responsible for reviewing or updating it. Unowned SOPs decay at roughly the same rate as the processes they describe change — in most SMBs, that means meaningful drift within 3-6 months. **Consequence:** Orphan SOPs create false confidence. Teams believe they have documentation when they actually have historical artifacts. In audits, orphan SOPs are worse than no SOP — they evidence awareness of the need without follow-through.

### 3. "Audit Theater" (Compliance Without Action)
Conducting SOP audits, producing findings, filing reports — and never implementing the recommendations. This is the most insidious anti-pattern because it feels productive. **Consequence:** 70% of audit recommendations in SMBs go unimplemented. Each ignored audit erodes trust in the audit process itself. After 2-3 cycles of theater, team members stop flagging issues because "nothing happens anyway." The Andon cord goes unpulled.

### 4. "Template Worship" (Rigid Compliance)
Following the SOP template rigidly when the underlying process has evolved. The template says 10 steps but the real process is now 7. Team members either fabricate 3 steps to satisfy the template or ignore the template entirely. **Consequence:** SOPs that are 6+ months old without review have 40%+ drift from reality. Forcing compliance with a drifted SOP introduces errors that wouldn't exist if the team just followed their actual (undocumented) process.

### 5. "Capacity Denial" (Operating Red, Reporting Yellow)
Acknowledging pressure privately while reporting a more optimistic capacity state. Usually stems from fear of being seen as unable to handle the workload, or from leadership that treats Red as a personal failing rather than a systemic signal. **Consequence:** Burnout hits 3-6 months after sustained Red-reported-as-Yellow. By the time the true state surfaces, recovery requires 2-4x the intervention that early escalation would have needed. Quality drops 15-25% in denied-Red states.

### 6. "Over-Documentation" (The 40-Step SOP)
Documenting every micro-step, decision, and variation in a single SOP. Comes from good intentions (thoroughness) but creates the opposite of its goal. **Consequence:** SOPs over 20 steps have 50% lower compliance rates than SOPs with 8-15 steps. The person executing gives up reading and goes from memory — which is exactly what the SOP was supposed to prevent. If a process genuinely has 40 steps, split it into 3-4 sub-procedures of 10-12 steps each.

### 7. "Parallel Process" (The Shadow SOP)
Two or more people follow different versions of the same procedure. Often happens after an SOP update when one person adopts the new version and another continues with the old. Also occurs when a "better way" spreads informally without updating the official SOP. **Consequence:** 15-20% error rate increase when parallel processes exist. Debugging becomes nearly impossible because the same procedure produces inconsistent outputs depending on who executed it. Handoffs between parallel-process followers are especially failure-prone.

### 8. "Seasonal Blindness" (Static Capacity Planning)
Not adjusting capacity states, review cadences, or SOP scope for predictable demand cycles. Every business has seasons — client ramps, holiday slowdowns, quarterly reporting surges. Operating as if demand is constant guarantees being surprised by events that were entirely predictable. **Consequence:** Teams that don't adjust for seasons spend Q4 in crisis mode and Q1 over-staffed. SOP review cadences set during a calm period create impossible backlogs during peak periods. Build seasonal adjustment triggers into capacity planning.

## Structured Output: SOP Audit Report

When producing an SOP audit, use this template:

```markdown
# SOP Audit Report

**Date:** [YYYY-MM-DD]
**Auditor:** [Name/Role]
**Scope:** [Which SOPs were audited, or "Full inventory"]

## Executive Summary
[2-3 sentences: how many SOPs audited, overall health, top finding]

## Inventory

| SOP Name | Owner | Last Reviewed | Cadence | Status |
|----------|-------|---------------|---------|--------|
| [name] | [owner] | [date] | [freq] | Current / Stale / Non-compliant |

## Scoring Detail

| SOP Name | Purpose | Owner | Trigger | Inputs | Steps | Tools | Outputs | Edge Cases | Cadence | Last Rev | Total /30 | Grade |
|----------|---------|-------|---------|--------|-------|-------|---------|------------|---------|----------|-----------|-------|
| [name] | [1-3] | [1-3] | [1-3] | [1-3] | [1-3] | [1-3] | [1-3] | [1-3] | [1-3] | [1-3] | [X/30] | [grade] |

**Grading scale:** 25-30 Production-ready | 18-24 Needs updates | 10-17 Significant gaps | <10 Draft/skeleton

## Drift Detection

| SOP Name | Drift Pattern Found | Severity | Evidence | Remediation |
|----------|-------------------|----------|----------|-------------|
| [name] | [Silent Shortcut / Tribal Knowledge / Tool Migration / Scope Drift / Calendar Decay / None] | [High/Med/Low] | [What was observed] | [What to do] |

## Capacity State Assessment

**Current state:** [GREEN / YELLOW / RED]
**Utilization:** [X]%
**Active SOPs:** [n] current, [n] stale, [n] non-compliant
**Blockers:** [list or "None"]

## Anti-Pattern Check

| Anti-Pattern | Detected? | Evidence | Impact |
|-------------|-----------|----------|--------|
| Process Without SOP | [Y/N] | [details] | [consequence if Y] |
| SOP Without Owner | [Y/N] | [details] | [consequence if Y] |
| Audit Theater | [Y/N] | [details] | [consequence if Y] |
| Template Worship | [Y/N] | [details] | [consequence if Y] |
| Capacity Denial | [Y/N] | [details] | [consequence if Y] |
| Over-Documentation | [Y/N] | [details] | [consequence if Y] |
| Parallel Process | [Y/N] | [details] | [consequence if Y] |
| Seasonal Blindness | [Y/N] | [details] | [consequence if Y] |

## Recommendations (Priority-Ordered)

1. **[CRITICAL/HIGH/MEDIUM/LOW]** — [Specific action] — Owner: [who] — Deadline: [when]
2. ...

## Fallback: When the Audit Can't Complete

- **SOP owner unavailable:** Score what you can from the document. Mark reality test as "DEFERRED — owner unavailable." Schedule follow-up within 2 weeks.
- **Tool access denied:** Note which tools couldn't be verified. Score Tools field as 1 (unverifiable). Flag for access review.
- **Conflicting information:** Document both versions. Escalate to the SOP owner's manager for resolution. Do not pick a winner without authority.
- **No SOPs exist yet:** Shift from audit to creation mode. Identify the top 3 processes by frequency and risk. Create SOPs for those first using the 10-field template.
```
