# SOP Creation Framework

## SOP Template

Use this template as the starting point for every SOP. Adapt section depth to the complexity tier (checklist, quick reference, standard, complex) but never remove sections entirely.

---

### Section 1: Purpose

Write exactly one sentence: "This procedure ensures [outcome] by [method]."

Bad: "This document describes the customer refund process." (Describes, does not state purpose.)
Good: "This procedure ensures refund requests are resolved within 3 business days by standardizing approval routing and payment execution."

The purpose statement is the filter for scope creep. If a step does not serve the stated purpose, it belongs in a different SOP.

### Section 2: Scope

Define three boundaries:
- **Who executes**: Job title or role, never a person's name. People leave; roles persist.
- **When triggered**: The observable event that starts this procedure. "When a customer submits a refund request via the support portal."
- **Exclusions**: What this SOP explicitly does NOT cover. "Does not cover chargebacks, subscription cancellations, or refunds exceeding $5,000 (see SOP-FIN-042)."

### Section 3: Roles & Responsibilities

Use RACI for any SOP involving more than one role:

| Step | Responsible | Accountable | Consulted | Informed |
|------|------------|-------------|-----------|----------|
| Validate request | Support Agent | Support Lead | -- | Customer |
| Approve refund | Finance | Finance Director | Legal (if >$1K) | Support Agent |
| Process payment | Finance | Finance Director | -- | Customer, Support Agent |

**Rules:**
- Every step has exactly one Responsible and one Accountable
- Accountable may equal Responsible for simple steps
- "Consulted" means their input is required before proceeding
- "Informed" means they receive notification after completion, no action required

### Section 4: Prerequisites

Numbered list of conditions that must all be true before Step 1. Include:
- System access requirements (specific tool, permission level)
- Prior approvals or completed upstream procedures
- Required information or materials
- Environmental conditions ("During business hours only" or "Production traffic below 50%")

**Why prerequisites matter:** Discovering a missing prerequisite mid-procedure forces restarts, wastes time, and introduces error risk. Front-load all requirements.

### Section 5: Procedure

**Writing Standards:**

1. **Imperative voice**: "Click Submit" not "The user should click Submit" or "You may want to click Submit"
2. **One action per step**: "Open the admin panel" is one step. "Open the admin panel and navigate to Settings > Billing" is two steps written as one -- split them
3. **Observable verification after major steps**: "Expected: Green confirmation banner appears. If red error banner appears, go to Exceptions (Section 6)."
4. **No embedded explanations**: If a step needs context, add a "Note:" line below it. Never bury explanations inside action steps.
5. **Decision points as explicit branches**:

```
Step 7: Check the approval status.
  - If APPROVED: proceed to Step 8.
  - If REJECTED: proceed to Step 12 (Rejection Handling).
  - If PENDING for more than 24 hours: escalate per Section 7.
```

6. **Step granularity rule**: Each step should take between 30 seconds and 5 minutes to execute. Steps shorter than 30 seconds can be combined. Steps longer than 5 minutes should be broken into sub-steps.

**Numbering Convention:**
- Main steps: 1, 2, 3...
- Sub-steps: 1a, 1b, 1c...
- Decision branches: labeled with the outcome ("If APPROVED")
- Never use bullet points for sequential steps -- bullets imply unordered

### Section 6: Exceptions & Edge Cases

Structure as a table:

| Exception | Condition | Override Authority | Procedure |
|-----------|-----------|-------------------|-----------|
| High-value refund | Amount exceeds $5,000 | VP Finance | Follow SOP-FIN-042 |
| Recurring customer | 3+ refund requests in 90 days | Support Lead | Trigger account review before processing |
| System outage | Payment system unavailable | Finance Director | Log request, process within 4 hours of restoration |

**Every SOP must have at least one exception documented.** If the author claims "there are no exceptions," they have not consulted the people who execute the procedure. Procedures always have edge cases.

### Section 7: Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 1.0 | YYYY-MM-DD | Name | Initial publication |
| 1.1 | YYYY-MM-DD | Name | Added exception for high-value refunds |

**Version numbering:**
- Major version (2.0): Fundamental process change, new steps, changed roles
- Minor version (1.1): Clarifications, added exceptions, updated thresholds
- Never edit without updating the version and revision history

---

## Decision Tree Documentation

For SOPs with more than 3 decision points, supplement the procedure with a decision tree diagram.

**Text-based decision tree format** (platform-agnostic):

```
START: Customer requests refund
  |
  Q: Was the product delivered?
  |-- NO --> Issue full refund (Step 4)
  |-- YES --> Q: Is the request within 30 days?
                |-- NO --> Deny, cite policy (Step 12)
                |-- YES --> Q: Is the item in original condition?
                              |-- YES --> Issue full refund (Step 4)
                              |-- NO --> Q: Is damage customer-caused?
                                          |-- YES --> Issue 50% credit (Step 8)
                                          |-- NO --> Issue full refund (Step 4)
```

**Rules for decision trees:**
- Every branch ends at a defined action or another decision
- No dead ends -- every path resolves
- Maximum 5 levels deep. Beyond 5 levels, split into sub-procedures.
- Label each decision as a yes/no question. Avoid multi-option questions at a single node.

---

## Review and Approval Workflow

### Who Reviews

| Review Type | Reviewer | Purpose |
|-------------|----------|---------|
| Technical accuracy | Person who executes the procedure daily | Verify steps match reality |
| Completeness | Person who has executed the procedure fewer than 3 times | Identify missing context or assumed knowledge |
| Authority approval | Process owner or department head | Confirm the procedure reflects official policy |
| Compliance review | Compliance officer (if applicable) | Verify regulatory requirements are met |

**Minimum review team:** One daily executor + one process owner. Smaller teams can combine roles.

### Review Cadence Rules

| SOP Category | Review Frequency | Trigger for Off-Cycle Review |
|-------------|-----------------|------------------------------|
| Incident response | Quarterly + after every use | Runbook was used and any step failed |
| Customer-facing operations | Semi-annually | Customer complaint citing process failure |
| Internal administrative | Annually | Staff member reports step is outdated |
| Compliance-regulated | Per regulatory requirement | Regulation change or audit finding |

---

## Common SOP Failures

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| Steps are too vague ("Process the request") | Author assumed reader knowledge | Expand to specific UI actions, commands, or decisions |
| SOP is never followed | Procedure is more burdensome than ad-hoc | Simplify to minimum viable steps. If it takes 3x longer than improvising, the SOP is wrong. |
| SOP contradicts actual practice | Written by someone who does not execute it | Always have the executor review. Compare written steps to screen recordings of actual execution. |
| Steps work only for the happy path | Author did not consult edge cases | Interview 3 different executors. Ask: "When does this procedure break?" |
| SOP is 15+ pages long | Scope is too broad | Split into multiple SOPs by trigger condition. No single SOP should exceed 3 pages of procedure. |
| No one knows the SOP exists | Published in the wrong location or not announced | Publish in the canonical KB. Link from the relevant process tool. Announce to affected teams. |
