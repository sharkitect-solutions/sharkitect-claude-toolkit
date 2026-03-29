# SOP Drift Detection Playbook

## The Five Named Drift Patterns

### 1. Silent Shortcut

**What it is:** Team members skip steps they perceive as unnecessary. The SOP says 8 steps; reality is 5. The skipped steps often include verification, logging, or notification — things that feel like overhead until something breaks.

**Detection method:** Shadow a process execution. Have someone observe (not participate) while a team member follows the SOP. Compare observed steps to documented steps. The gap is the Silent Shortcut.

**Typical impact:** 30-40% of "minor" incidents trace back to skipped verification steps. The shortcut saves 5 minutes per execution and costs 2-4 hours when the skipped check would have caught an error.

**Remediation:** If the skipped steps are genuinely unnecessary, remove them from the SOP (the team is right). If they serve a purpose, explain WHY each step exists directly in the SOP. People skip steps they don't understand.

### 2. Tribal Knowledge Creep

**What it is:** Undocumented steps accumulate around a documented SOP. "Oh, you also need to ping Maria in Slack after Step 3" — but that's not written anywhere. The SOP works fine for veterans but fails for anyone new.

**Detection method:** Have a person who has NEVER executed the SOP follow it literally, with no help. Every point where they get stuck or need to ask someone reveals tribal knowledge that should be in the SOP.

**Typical impact:** New hire ramp time doubles when tribal knowledge exceeds 20% of actual process steps. Knowledge loss when a key person leaves can halt operations for days.

**Remediation:** Run the "new hire test" annually even if no new hires are expected. Document every piece of tribal knowledge surfaced. If the SOP grows past 20 steps after adding tribal knowledge, split into sub-procedures.

### 3. Tool Migration Orphan

**What it is:** The SOP references a tool or system that has been deprecated, replaced, or significantly updated. The team has adapted but the SOP still says "Open Trello" when the company moved to Monday.com 6 months ago.

**Detection method:** Automated check — extract all tool/system names and URLs from SOPs. Cross-reference against current tool inventory. Flag any SOP referencing a tool not on the active list. Also check URLs: do embedded links still resolve?

**Typical impact:** Creates confusion for new team members and audit failures. In regulated environments, referencing deprecated tools in SOPs can trigger compliance findings. At minimum, it erodes trust in SOP accuracy.

**Remediation:** When any tool migration occurs, immediately search all SOPs for references to the old tool. Update before the migration completes, not after. Add this to the tool migration checklist.

### 4. Scope Drift

**What it is:** The SOP's documented scope no longer matches its actual boundaries. Either the SOP has been informally extended to cover adjacent processes (scope expansion) or parts of it have been absorbed by other SOPs or tools (scope contraction).

**Detection method:** Compare the SOP's stated Purpose (Field 1) and Trigger (Field 3) against the actual situations where team members invoke it. If the SOP is being used for scenarios not described in its trigger, it has expanded. If entire sections are never executed, it has contracted.

**Typical impact:** Expanded SOPs become unwieldy and internally contradictory. Contracted SOPs waste the reader's time with irrelevant sections. Both reduce compliance.

**Remediation:** For expansion — either update the scope formally or split into multiple SOPs. For contraction — remove dead sections and update the Purpose field.

### 5. Calendar Decay

**What it is:** The SOP has not been reviewed within its stated review cadence. A quarterly-review SOP last reviewed 9 months ago is in Calendar Decay. The SOP may still be accurate, but confidence in its accuracy has expired.

**Detection method:** Freshness check. Compare "Last Reviewed" date (Field 10) against the Review Cadence (Field 9). If current date exceeds the next expected review date, the SOP is decayed.

**Typical impact:** SOPs in Calendar Decay have a 40%+ probability of containing at least one outdated element (based on typical SMB process change velocity). The longer the decay, the higher the probability.

**Remediation:** Flag decayed SOPs on a dashboard. Prioritize review by risk: SOPs supporting revenue-generating or client-facing processes first, internal administrative processes second.

---

## Worked Example: Client Onboarding SOP Audit

### Context
Sharkitect Digital has a "Client Onboarding" SOP. It was written 8 months ago, reviewed once 5 months ago, and has a quarterly review cadence. A new team member recently struggled to follow it.

### Step 1: 10-Field Scoring

| Field | Score | Notes |
|-------|-------|-------|
| 1. Purpose | 3 | Clear: "Ensure every new client is fully set up within 5 business days of contract signing." |
| 2. Owner | 2 | Lists "Operations Lead" but no backup owner. Current ops lead started 2 months ago. |
| 3. Trigger | 3 | "New client signs contract in HubSpot" — specific and verifiable. |
| 4. Inputs | 2 | Lists contract and client info but doesn't specify where to find the signed contract. |
| 5. Steps | 2 | 12 steps listed. Steps 4-6 reference "the project template" without naming which template or where it lives. |
| 6. Tools | 1 | Lists "HubSpot, Notion, Slack" but no links, no access requirements, no version info. |
| 7. Outputs | 3 | Clear: "Client workspace created, welcome email sent, kickoff meeting scheduled." |
| 8. Edge Cases | 1 | Only one edge case: "Client doesn't respond to welcome email." Missing: partial contract, multi-stakeholder onboarding, rush onboarding. |
| 9. Review Cadence | 3 | "Quarterly" — clearly stated. |
| 10. Last Reviewed | 2 | Date is 5 months ago. Cadence is quarterly. Overdue by 2 months. |
| **Total** | **22/30** | Needs minor updates — but the drift findings below reveal more. |

### Step 2: Reality Test

Observed an actual onboarding execution and compared to SOP:

- **Step 3** says "Create client folder in Notion." Team actually creates it in Monday.com now (Tool Migration Orphan — Notion was replaced 3 months ago).
- **Step 5** says "Send welcome email template." Team skips this and uses an automated HubSpot sequence instead (Silent Shortcut — automation replaced the manual step, but nobody updated the SOP).
- **Step 8** says "Schedule kickoff call." Team also sends a pre-kickoff questionnaire via Jotform that isn't in the SOP (Tribal Knowledge Creep — questionnaire was added informally 4 months ago).
- **Steps 9-12** (internal handoff) are followed as documented. No drift.

**Drift rate: 3 of 12 steps = 25%.** Exceeds the 20% threshold. This SOP needs a rewrite, not a patch.

### Step 3: Drift Detection Summary

| Drift Pattern | Found? | Details |
|---------------|--------|---------|
| Silent Shortcut | YES | Step 5 (manual email replaced by automation) |
| Tribal Knowledge Creep | YES | Step 8 (undocumented Jotform questionnaire) |
| Tool Migration Orphan | YES | Step 3 (Notion replaced by Monday.com) |
| Scope Drift | NO | SOP scope matches actual onboarding scope |
| Calendar Decay | YES | 2 months overdue for quarterly review |

### Step 4: Remediation Recommendations

1. **REWRITE** (not patch) — drift rate exceeds 20%
2. **Update tools section** — Replace Notion references with Monday.com, add Jotform, update HubSpot to reflect automation
3. **Add backup owner** — Current owner is new; assign previous ops lead as backup during transition
4. **Expand edge cases** — Add multi-stakeholder, rush onboarding, and partial contract scenarios
5. **Embed tool links** — Apply Poka-Yoke: every tool mention should be a clickable link to the exact location
6. **Add Flag Log section** — Enable Andon cord principle for future issue surfacing
7. **Reset review date** — Mark as reviewed upon rewrite, next review in 3 months

---

## Edge Cases in SOP Auditing

### Partially Compliant SOPs
An SOP scores 18-24/30 — not broken enough to rewrite, not complete enough to trust. **Resolution:** Create a punch list of the specific fields scoring below 3. Assign the SOP owner a 2-week deadline to patch those fields only. Re-score after patches.

### Conflicting SOPs
Two SOPs cover overlapping scope with contradictory steps. **Resolution:** Identify which SOP is actually followed in practice (the "de facto" standard). Archive the other. If both are partially followed, merge into a single authoritative SOP with the SOP owners collaborating on the merge.

### SOPs Referencing Discontinued Tools
A special case of Tool Migration Orphan where the tool no longer exists at all (not just replaced). **Resolution:** If no replacement tool exists, the SOP step itself may be obsolete. Verify with the process owner whether the step is still needed. If yes, identify the current tool. If no, remove the step and re-test the SOP end-to-end.

### Capacity State Disagreements
Two assessors classify operational capacity differently (one says Yellow, other says Green). **Resolution:** Use the more conservative (worse) rating as the working state. Investigate the disagreement — it usually means the assessment criteria aren't specific enough. Add quantitative thresholds to the Capacity State Framework table (e.g., "Yellow if ANY of these: utilization >80%, stale SOPs >1, overdue tasks >3").
