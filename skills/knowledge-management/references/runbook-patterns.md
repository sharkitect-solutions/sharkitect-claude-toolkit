# Runbook Patterns

## Incident Response Runbook Template

### Trigger Condition
"When [monitoring system] fires alert [alert name] OR when [on-call engineer] observes [symptom description]."

Write triggers as observable symptoms. "When the API returns 500 errors on the /checkout endpoint" -- not "When the payment service crashes." Users see symptoms before they know root causes.

### Severity Assessment Matrix

| Symptom | Customer Impact | Revenue Impact | Severity |
|---------|----------------|----------------|----------|
| Elevated error rate (<5%) | Degraded experience, retries succeed | Minimal | SEV-3 |
| Error rate 5-25% | Significant failures, some users blocked | Moderate | SEV-2 |
| Error rate >25% or total outage | Service unusable | High | SEV-1 |
| Data corruption suspected | Unknown scope | Potentially catastrophic | SEV-1 + Data Incident |

### Diagnostic Steps

Structure every diagnostic step as: Action -> Expected Output -> Branch.

```
Step 1: Check service health dashboard at [URL].
  Expected: All metrics green.
  If degraded: Note which metrics are red. Proceed to Step 2.
  If dashboard itself is unreachable: Skip to Step 5 (infrastructure check).

Step 2: Check application logs for the past 15 minutes.
  Command: [specific log query command or URL]
  Expected: Normal log patterns.
  If error spike visible: Record error class and count. Proceed to Step 3.
  If no errors but latency spike: Proceed to Step 4 (resource check).

Step 3: Identify error pattern.
  If authentication errors: Load auth-failure runbook.
  If database connection errors: Load database-connectivity runbook.
  If dependency timeout: Load dependency-failure runbook.
  If unknown error class: Escalate to SEV-2 with error samples.
```

### Resolution Steps

Structure as numbered actions with verification:

1. [Action]: Execute [specific command or UI action].
   - Verify: [Expected outcome]. Wait [time] before proceeding.
   - If verification fails: STOP. Do not proceed. Go to Rollback.

2. [Action]: Apply fix [specific change].
   - Verify: Error rate decreasing within 5 minutes.
   - If error rate unchanged after 10 minutes: Rollback and escalate.

### Rollback Steps

**Mandatory for every runbook.** Structure as the reverse of resolution steps:

1. Revert [specific change from Resolution Step 2].
   - Verify: System returns to pre-change state.
2. Revert [specific change from Resolution Step 1].
   - Verify: Original symptoms may return. This is expected.
3. Escalate to [next tier] with: incident timeline, steps attempted, rollback confirmation.

**Rollback rules:**
- If in doubt, roll back. A known-bad state is better than an unknown state.
- Rollback steps must be tested during game days (see Testing section below).
- If rollback is impossible (data migration, destructive operation), the resolution step must require explicit approval before execution.

### Escalation Path

| Severity | First Response | Escalation After | Escalation To | Communication |
|----------|---------------|-------------------|---------------|---------------|
| SEV-3 | On-call engineer | 30 minutes | Team lead | Internal Slack channel |
| SEV-2 | On-call engineer | 15 minutes | Engineering manager | Incident channel + status page |
| SEV-1 | On-call engineer + team lead | Immediate | VP Engineering + CTO | All-hands incident bridge |

### Post-Incident Checklist

- [ ] Timeline documented: when detected, when acknowledged, when mitigated, when resolved
- [ ] Root cause identified (or marked as unknown with investigation plan)
- [ ] Customer impact quantified: users affected, duration, revenue impact
- [ ] Blameless post-mortem scheduled within 48 hours
- [ ] Action items created with owners and due dates
- [ ] KB article created or updated with the failure pattern and resolution
- [ ] Runbook updated if any step was incorrect, missing, or unclear
- [ ] Monitoring updated if detection was delayed

---

## Deployment Runbook Template

### Pre-Deployment Checklist

- [ ] All tests passing on the deploy branch
- [ ] Change description reviewed and approved by at least one peer
- [ ] Rollback plan documented (specific steps, not "revert the deploy")
- [ ] Deployment window confirmed (low-traffic period or approved maintenance window)
- [ ] On-call engineer identified and notified
- [ ] Monitoring dashboards open: [list specific dashboard URLs]
- [ ] Communication sent to affected teams: [channel]

### Deployment Steps

1. Announce deployment start in [channel].
2. Execute deployment command: [specific command].
3. Monitor deployment progress: [how to check].
4. Verify health checks pass within [timeframe].
5. Run smoke tests: [specific test suite or manual checks].
6. Monitor error rates for 15 minutes post-deploy.
7. Announce deployment complete OR trigger rollback.

### Rollback Procedure

1. Announce rollback initiated in [channel].
2. Execute rollback: [specific command or procedure].
3. Verify previous version is serving: [verification command].
4. Confirm error rates return to pre-deployment baseline.
5. Announce rollback complete.
6. Create post-deploy incident report documenting why rollback was needed.

### Canary/Progressive Deployment Pattern

For services with canary deployment capability:

| Phase | Traffic % | Duration | Go/No-Go Criteria |
|-------|----------|----------|-------------------|
| Canary | 1-5% | 15 minutes | Error rate < baseline + 0.1% |
| Partial | 25% | 30 minutes | Error rate < baseline + 0.5%, latency p99 < 2x baseline |
| Majority | 75% | 30 minutes | Same as partial |
| Full | 100% | -- | Monitor for 1 hour |

At any phase: if Go criteria are not met, roll back to previous phase and investigate.

---

## On-Call Runbook Template

### Shift Start Checklist

- [ ] Confirm pager is charged and receiving alerts
- [ ] Review open incidents from previous shift (handoff notes)
- [ ] Check monitoring dashboards for any pre-existing issues
- [ ] Verify access to all critical systems (VPN, SSH, admin consoles)
- [ ] Confirm escalation contacts are current and reachable
- [ ] Review any scheduled changes or deployments during this shift

### Alert Triage Decision Tree

```
Alert received:
  |
  Q: Is this a known false positive? (Check known-alerts list)
  |-- YES --> Acknowledge, document, file ticket to fix alert
  |-- NO --> Q: Is customer traffic affected?
              |-- YES --> Assess severity, begin incident response runbook
              |-- NO --> Q: Is it trending toward customer impact?
                          |-- YES --> Investigate proactively, 15-min check-in
                          |-- NO --> Acknowledge, investigate during business hours
```

### Shift Handoff Template

| Field | Content |
|-------|---------|
| Shift period | [Start time] to [End time] |
| Open incidents | [List with severity and status] |
| Resolved incidents | [List with brief resolution summary] |
| Ongoing investigations | [What you were looking into] |
| Scheduled events | [Deploys, maintenance, external events] |
| Notes for next shift | [Anything unusual or requiring follow-up] |

---

## Runbook Testing Methodology

### Game Day Exercises

Game days are controlled simulations where the team practices executing runbooks against real (or realistic) failure scenarios. They are the only reliable way to validate that runbooks work.

**Frequency:** Quarterly for critical runbooks. Semi-annually for others. After every major system change.

**Structure:**
1. **Pre-game:** Select a runbook to test. Inform participants but do not reveal the specific failure scenario. Prepare the simulated failure (fault injection, test environment recreation, or tabletop walkthrough).
2. **Execution:** Inject the failure. The on-call engineer follows the runbook exactly as written. Observers note any step that is unclear, wrong, or missing.
3. **Debrief:** Within 1 hour, review: Did the runbook work? What steps were unclear? What steps were wrong? What steps were missing? What took longer than expected?
4. **Update:** Revise the runbook immediately based on findings. Schedule re-test if changes were significant.

### Tabletop Exercises

When fault injection is too risky or expensive, run tabletop exercises:

1. Facilitator reads the trigger condition aloud
2. Responder narrates what they would do at each step
3. Facilitator provides simulated output for each diagnostic step
4. Team identifies gaps verbally
5. Runbook is updated based on discussion

Tabletop exercises catch 60-70% of the issues game days catch, at a fraction of the cost and risk. Use them for runbooks that cannot be safely simulated.

---

## Automation Progression Framework

### Assessment Criteria

Score each runbook on three axes to determine automation priority:

| Axis | Low (1) | Medium (3) | High (5) |
|------|---------|------------|----------|
| Frequency | Quarterly or less | Monthly | Weekly or more |
| Complexity | 3-5 simple steps | 6-15 steps with branches | 15+ steps, multiple decision points |
| Risk of human error | Low (steps are reversible) | Medium (some irreversible steps) | High (data loss or outage possible) |

**Priority = Frequency x Risk**. Automate high-frequency, high-risk runbooks first.

### Progression Path

**L0 to L1 (Manual to Assisted):**
- Create scripts for data-gathering steps (log queries, metric pulls, status checks)
- Keep all decision-making and execution with humans
- Typical investment: 2-4 hours per runbook

**L1 to L2 (Assisted to Semi-Automated):**
- Create scripts for execution steps with human approval gates
- Automated: "Here's what I plan to do: [action]. Approve? (y/n)"
- Typical investment: 1-2 days per runbook

**L2 to L3 (Semi-Automated to Fully Automated):**
- Remove human approval gates for well-understood, well-tested paths
- Keep human notification and override capability
- Requires: 10+ successful L2 executions, comprehensive test coverage
- Typical investment: 1-2 weeks per runbook

### Ownership and Rotation

| Role | Responsibility |
|------|---------------|
| Runbook owner | Single person. Keeps runbook current. Reviews after every use. |
| Rotation | Transfer ownership when team changes. Never leave runbooks unowned. |
| Review trigger | After every execution (successful or not). After related system changes. Quarterly if unused. |
| Retirement | When the system or process no longer exists. Archive with retirement date. |

**Rule:** If a runbook has no owner, it is unreliable. Assign an owner or retire it. Unowned runbooks create false safety -- the team believes a procedure exists, but no one ensures it works.
