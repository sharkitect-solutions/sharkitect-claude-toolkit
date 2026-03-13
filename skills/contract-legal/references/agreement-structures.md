# Agreement Structures Reference

Section-by-section breakdowns for the six most common SMB contract types. Use these as structural blueprints -- every section listed is required unless marked optional.

## Master Service Agreement (MSA) Structure

The MSA governs the overall business relationship. Project-specific details go in SOWs.

| Section | Contents | Common Mistakes |
|---------|----------|-----------------|
| 1. Recitals | Parties identified, background context, purpose of agreement | Incorrect legal entity names (use exact registered names) |
| 2. Definitions | All capitalized terms defined (Deliverables, Services, Work Product, Confidential Information) | Under-defining terms -- every ambiguous word becomes a dispute vector |
| 3. Engagement and SOW Process | How SOWs are created, approved, and incorporated by reference | No explicit process for SOW approval (verbal SOWs are unenforceable) |
| 4. Fees and Payment | Rate structures, invoicing cadence, Net-30 terms, late fees, expense reimbursement policy | Missing late payment interest rate, no right to suspend for non-payment |
| 5. Intellectual Property | Work product ownership, pre-existing IP carve-out, license-back provisions | Failing to carve out pre-existing IP and general knowledge |
| 6. Confidentiality | Mutual obligations, definition, exclusions, term, return/destroy | One-sided obligations, missing standard exclusions |
| 7. Representations and Warranties | Authority to enter agreement, compliance with laws, non-infringement of third-party rights | Unlimited warranty scope without time limitation |
| 8. Indemnification | Mutual scope, defense obligations, settlement process, relationship to liability cap | Asymmetric obligations, no cap relationship defined |
| 9. Limitation of Liability | Aggregate cap (12 months fees), consequential damages exclusion, carve-outs | Missing entirely, or carve-outs that swallow the cap |
| 10. Term and Termination | Initial term, renewal mechanism, termination for cause (30-day cure), termination for convenience, wind-down | No convenience termination, no cure period |
| 11. Dispute Resolution | Governing law, escalation path (negotiation > mediation > arbitration/litigation) | Direct-to-litigation, unfavorable jurisdiction |
| 12. General Provisions | Force majeure, assignment, severability, entire agreement, amendments, notices, waiver, survival | Missing survival clause (obligations vanish at termination) |

**Signature block:** Full legal name of each entity, authorized signatory name and title, signature, date. Electronic signatures (DocuSign, Adobe Sign) are legally valid under ESIGN Act and UETA.

## Statement of Work (SOW) Structure

Every SOW references its parent MSA and adds project-specific terms.

**Header:** SOW number, effective date, MSA reference ("This SOW is governed by the MSA dated [DATE] between [PARTY A] and [PARTY B]").

| Section | Contents | Why It Matters |
|---------|----------|---------------|
| 1. Project Description | High-level summary of the engagement, business objectives | Sets context for interpreting scope disputes |
| 2. Scope of Services | Detailed deliverables list with descriptions, explicit in-scope items | Vague scope enables "The Scope Creep Enabler" anti-pattern |
| 3. Out of Scope | Explicit exclusions -- items NOT included in this SOW | Prevents assumptions about what is included by omission |
| 4. Deliverables and Acceptance | Each deliverable with format, acceptance criteria, review period (5-10 business days), revision rounds (2 standard) | Without acceptance criteria, deliverables are never "done" |
| 5. Timeline and Milestones | Start date, milestone dates, dependencies, final delivery date, delay provisions | Missing dependency documentation causes blame disputes |
| 6. Fees and Payment Schedule | Fixed fee or T&M rates, milestone payments, invoicing schedule, what triggers each payment | Payment tied to single acceptance event creates cash flow risk |
| 7. Assumptions | Conditions that must remain true for the SOW to succeed (client provides access within 5 days, feedback within 3 business days) | Unwritten assumptions become disputes when violated |
| 8. Client Responsibilities | Specific obligations of the client (content delivery, system access, stakeholder availability, approvals) | Client delays without documented responsibility clauses are unrecoverable |
| 9. Change Order Process | How scope changes are requested, evaluated, priced, and approved in writing before work begins | Verbal change approvals lead to disputed invoices |

**Signature block:** Same format as MSA. Both parties sign each SOW.

## NDA Structure

### Mutual NDA

| Section | Contents |
|---------|----------|
| 1. Purpose | Reason for sharing confidential information (evaluating partnership, vendor selection, M&A) |
| 2. Definition of Confidential Information | Broad definition covering business, technical, financial, customer information. Include catch-all plus specific categories. |
| 3. Exclusions | Five standard exclusions: publicly available, prior knowledge, independent development, third-party receipt, legal compulsion with notice |
| 4. Obligations | Protect with same care as own confidential information (not less than reasonable care), limit access to need-to-know personnel, no reverse engineering |
| 5. Term | Agreement duration (typically 2-3 years), confidentiality survival period (2-5 years post-termination, indefinite for trade secrets) |
| 6. Return/Destroy | Within 30 days of termination or request, return or certify destruction. Carve-out for automated backups and legal archives with continued obligations. |
| 7. Remedies | Acknowledge that breach may cause irreparable harm and that injunctive relief is available without proving actual damages |
| 8. General Provisions | Governing law, jurisdiction, no assignment, entire agreement, severability |

### Unilateral NDA Differences

Same structure, but obligations apply only to the receiving party. The disclosing party section is replaced with a "Discloser's Retention of Rights" section confirming no license or ownership transfers with the disclosure.

## Freelancer/Contractor Agreement Structure

| Section | Contents | Critical Points |
|---------|----------|----------------|
| 1. Engagement | Contractor name, project description, MSA/SOW reference if applicable | Explicitly state independent contractor relationship |
| 2. Services and Deliverables | Scope, deliverables, acceptance criteria, revision rounds | Measurable acceptance criteria prevent infinite loops |
| 3. Compensation | Fixed fee or hourly rate, payment schedule, invoicing process, expense policy | Never 100% back-loaded -- use milestone payments |
| 4. Timeline | Start date, milestones, final delivery, extension provisions | Include buffer for review cycles |
| 5. Independent Contractor Status | Explicit declaration that contractor is not an employee, controls own methods/schedule/tools, responsible for own taxes | Include all IRS safe harbor indicators |
| 6. IP Assignment | Work-for-hire declaration AND backup assignment clause, pre-existing IP carve-out, moral rights waiver where permitted | Both clauses required -- work-for-hire alone has gaps |
| 7. Confidentiality | Incorporate by reference or repeat NDA terms | Standalone if no separate NDA exists |
| 8. Non-Solicitation | Contractor will not solicit client's employees or customers during engagement plus 12 months | Must be reasonable in scope and duration for enforceability |
| 9. Termination | Either party with 14-30 days notice, kill fee for client convenience termination (15-25% of remaining value), payment for work completed | No kill fee = contractor absorbs 100% of cancellation risk |
| 10. Representations | Contractor has authority, work will be original, no conflict with other obligations | Protects against IP contamination from prior engagements |
| 11. Insurance (Optional) | Contractor maintains professional liability insurance at $[amount] minimum | Required for high-value or high-risk engagements |

## SLA Structure

| Section | Contents |
|---------|----------|
| 1. Service Description | What is covered by the SLA, service boundaries, dependencies |
| 2. Performance Metrics | Uptime target, measurement methodology, measurement intervals, monitoring tools |
| 3. Response Time Tiers | P1-P4 severity definitions, response SLA per severity, resolution target per severity |
| 4. Exclusions | Scheduled maintenance (72h advance notice), force majeure, client-caused issues, third-party dependencies |
| 5. Measurement and Reporting | How metrics are tracked, reporting frequency (monthly), dashboard access, dispute process for measurements |
| 6. Service Credits | Credit percentage per SLA miss, calculation method, credit cap (typically 30% monthly fees), automatic vs claim-based |
| 7. Escalation Procedures | Who to contact per severity level, escalation timeline, management notification thresholds |
| 8. Review and Amendment | Quarterly SLA review meetings, annual target reassessment, amendment process |

### SLA Tier Examples

**Managed Services Provider:**
- Standard: 99.5% uptime, P1 response 30 min, P2 response 2 hours, 5% credit per 0.1% miss
- Premium: 99.9% uptime, P1 response 15 min, P2 response 1 hour, 10% credit per 0.1% miss

**SaaS Product:**
- Free tier: Best-effort, no SLA, community support only
- Professional: 99.9% uptime, business-hours support, 24h P1 response
- Enterprise: 99.95% uptime, 24/7 support, 1h P1 response, dedicated account manager

## Change Order / Amendment Format

| Field | Contents |
|-------|----------|
| Reference | Parent MSA number, SOW number being amended |
| Change Description | What is being added, removed, or modified (specific and measurable) |
| Impact on Scope | New deliverables or modified deliverables with updated acceptance criteria |
| Impact on Timeline | Revised milestone dates, new final delivery date |
| Impact on Fees | Additional fees, modified payment schedule, new total contract value |
| Assumptions | New assumptions created by this change |
| Authorization | Both parties sign. States: "All other terms of the MSA and SOW remain unchanged except as modified herein." |

**Change order rule:** No work begins on changed scope until the change order is signed by both parties. Verbal approvals followed by disputed invoices is the #1 source of freelancer payment disputes.
