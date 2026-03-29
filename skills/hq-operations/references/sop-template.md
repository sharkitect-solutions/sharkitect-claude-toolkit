# Sharkitect Digital SOP Template

## The 10-Field Standard

Every Standard Operating Procedure at Sharkitect Digital follows this template. No exceptions. Missing fields mean the SOP is incomplete and should not be considered authoritative.

---

```markdown
# SOP: [Procedure Name]

## 1. Purpose
[One sentence: Why does this SOP exist? What problem does it solve?]

## 2. Owner
**Primary:** [Name/Role]
**Backup:** [Name/Role]
**Review authority:** [Who can approve changes]

## 3. Trigger
[What event initiates this procedure?]
- Scheduled: [frequency, e.g., "Every Monday at 9 AM"]
- Event-driven: [condition, e.g., "New client signs contract"]
- On-demand: [request pattern, e.g., "CEO requests quarterly report"]

## 4. Inputs
[What is needed before this procedure can begin?]
- [ ] [Input 1 — where to get it, format expected]
- [ ] [Input 2 — where to get it, format expected]
- [ ] [Input 3 — where to get it, format expected]

## 5. Steps
[Numbered procedure. Each step should be specific enough that someone
unfamiliar with the process could follow it.]

1. [Action verb] [specific action] [using what tool/system]
2. [Action verb] [specific action] [using what tool/system]
3. [Action verb] [specific action] [using what tool/system]
   - If [condition]: [alternate action]
   - If [error]: [recovery action]
4. [Action verb] [specific action] [using what tool/system]
5. [Action verb] [specific action] [using what tool/system]

## 6. Tools & Systems
| Tool | Purpose in This SOP | Access Required |
|------|-------------------|-----------------|
| [Tool 1] | [What it does here] | [Who has access] |
| [Tool 2] | [What it does here] | [Who has access] |

## 7. Outputs
[What is produced when this procedure completes?]
- [Output 1] — delivered to [where/who], format: [format]
- [Output 2] — delivered to [where/who], format: [format]

## 8. Edge Cases
[What can go wrong and how to handle it]

| Scenario | Response | Escalation |
|----------|---------|------------|
| [What could happen] | [What to do] | [Who to notify if response fails] |
| [What could happen] | [What to do] | [Who to notify if response fails] |

## 9. Review Cadence
**Frequency:** [Monthly / Quarterly / Semi-annually / Annually]
**Next review due:** [YYYY-MM-DD]
**Review process:** [How the review is conducted — read through, test run, etc.]

## 10. Last Reviewed
**Date:** [YYYY-MM-DD]
**Reviewed by:** [Name/Role]
**Changes made:** [Brief description or "No changes — procedure confirmed current"]

---

**Version:** [1.0]
**Created:** [YYYY-MM-DD]
**Classification:** [K2 — Core Operational / K3 — Standard Reference]
```

---

## SOP Quality Scoring

Rate each of the 10 fields on a 1-3 scale:

| Score | Meaning |
|-------|---------|
| 3 | Field is complete, specific, and current |
| 2 | Field exists but is vague, incomplete, or potentially outdated |
| 1 | Field is missing or placeholder only |

**Total: /30**
- 25-30: Production-ready SOP
- 18-24: Needs minor updates before relying on it
- 10-17: Significant gaps — should not be used as-is
- Below 10: SOP is a skeleton — treat as draft

## SOP Audit Procedure

When auditing existing SOPs:

1. **Inventory**: List all documents labeled as SOPs
2. **Template compliance**: Score each against the 10-field template
3. **Freshness check**: Is the "Last Reviewed" date within the review cadence?
4. **Reality test**: Does the documented procedure match what actually happens?
5. **Dependency check**: Do referenced tools/systems still exist?
6. **Report**: Produce findings with scores and remediation priority

### Reality Test Method

The most common SOP failure is drift — the documented procedure no longer matches reality. To test:

1. Walk through the SOP step by step
2. At each step, ask: "Is this what actually happens?"
3. Note deviations: are steps skipped, reordered, or replaced?
4. If >20% of steps have drifted, the SOP needs rewrite (not just updates)

## Common SOP Categories at Sharkitect

| Category | Review Cadence | Typical K-Level | Examples |
|----------|---------------|-----------------|---------|
| **Client onboarding** | Quarterly | K2 | New client setup, access provisioning |
| **Service delivery** | Quarterly | K2 | Workflow build process, QA checklist |
| **Financial operations** | Monthly | K2 | Invoicing, expense reporting |
| **Marketing operations** | Quarterly | K3 | Content publishing, social scheduling |
| **System administration** | Monthly | K2 | Backup procedures, access reviews |
| **Emergency response** | Monthly | K1 | Incident response, data breach protocol |

## Capacity State Assessment Template

```markdown
## Operational Capacity Assessment

**Date:** [YYYY-MM-DD]
**Assessed by:** [Name/Role]

### Current State: [GREEN / YELLOW / RED]

### Utilization
- Team utilization: [X]%
- Active client projects: [n] / capacity: [n]
- Open tasks overdue: [n]

### SOP Health
- Total SOPs: [n]
- Current (within review cadence): [n]
- Stale (past review cadence): [n]
- Non-compliant (missing fields): [n]

### Blockers
- [Blocker 1 — impact — owner — estimated resolution]
- [Blocker 2 — impact — owner — estimated resolution]

### Recommended Actions
1. [Priority action]
2. [Priority action]
3. [Priority action]
```
