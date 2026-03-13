---
name: contract-legal
description: "Use when drafting, reviewing, or structuring business contracts, service agreements, NDAs, SLAs, terms of service, IP assignments, freelancer agreements, or legal clause selection. Use when building contract templates, negotiating terms, or reviewing counterparty redlines. Do NOT use for regulatory compliance audits, litigation strategy, tax law, employment law disputes, or any matter requiring licensed attorney review."
---

# Contract & Legal Drafting for SMBs

> **DISCLAIMER**: This skill provides contract templates, structural guidance, and negotiation frameworks. It does NOT constitute legal advice. AI-generated contract language must be reviewed by a licensed attorney before execution. Contracts create binding obligations -- never sign without qualified legal review. Laws vary by jurisdiction; templates require localization.

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/clause-library.md` | Selecting specific clauses, reviewing counterparty language, comparing clause variations, assessing clause risk levels | High-level contract structure questions, negotiation strategy |
| `references/agreement-structures.md` | Building a new contract from scratch, structuring MSA/SOW/NDA/SLA, creating amendment templates | Clause-level language review, negotiation tactics |
| `references/negotiation-playbook.md` | Preparing for contract negotiations, prioritizing terms, responding to counterparty redlines, deciding walkaway criteria | Initial contract drafting, clause selection |

## Scope Boundary

| In Scope | Out of Scope |
|----------|-------------|
| MSA, SOW, NDA, SLA drafting and structure | Litigation strategy or court filings |
| Freelancer and contractor agreements | Employment law disputes (refer to employment attorney) |
| Terms of Service and Privacy Policy structure | Regulatory compliance audits (HIPAA, SOC2, GDPR) |
| IP assignment and work-for-hire clauses | Tax law and tax treaty implications |
| Contract negotiation frameworks | Real estate contracts and lease agreements |
| Clause selection and risk assessment | Securities law, fundraising agreements |
| Change orders and amendments | Insurance policy drafting |
| Kill fee and termination provisions | International trade law and export controls |
| Payment terms and remedy structures | Bankruptcy and insolvency proceedings |

---

## Contract Architecture

### The Contract Hierarchy

Every business relationship should follow this hierarchy. Higher documents govern when conflicts arise.

```
Master Service Agreement (MSA)    -- Governs the relationship
  |-- Statement of Work (SOW)     -- Defines specific engagements
       |-- Change Order (CO)      -- Modifies SOW scope/timeline/cost
  |-- Purchase Order (PO)         -- Authorizes payment for SOW deliverables
```

**Why this hierarchy matters:** The MSA contains terms negotiated once (liability caps, IP ownership, dispute resolution). SOWs reference the MSA and add project-specific scope, timeline, and fees. Without this separation, you re-negotiate legal terms on every new project -- wasting 2-6 weeks per engagement.

### MSA Core Sections

An MSA must contain these sections. Omitting any creates exploitable gaps:

1. **Definitions** -- Define every ambiguous term (Deliverables, Confidential Information, Intellectual Property, Services, Work Product). Undefined terms invite disputes.
2. **Scope of Services** -- High-level description referencing SOWs for specifics.
3. **Payment Terms** -- Rate structure, invoicing cadence, payment window (Net-30 standard), late payment penalties (1.5%/month is industry norm).
4. **Intellectual Property** -- Who owns what, when ownership transfers, pre-existing IP carve-outs.
5. **Confidentiality** -- Mutual obligations, definition of confidential information, exclusions, survival period.
6. **Representations and Warranties** -- Each party's promises about authority, compliance, non-infringement.
7. **Indemnification** -- Who covers whom for what categories of harm.
8. **Limitation of Liability** -- Cap on damages (typically 12 months of fees paid), consequential damages exclusion.
9. **Term and Termination** -- Duration, renewal mechanism, termination for cause, termination for convenience, wind-down obligations.
10. **Dispute Resolution** -- Governing law, jurisdiction, escalation path (negotiation, mediation, arbitration, litigation).
11. **General Provisions** -- Force majeure, assignment, severability, entire agreement, amendments, notices.

### SOW as MSA Addendum

Every SOW must reference its parent MSA and contain: project description, deliverables with acceptance criteria, timeline with milestones, fees and payment schedule, assumptions, out-of-scope items. The SOW inherits all MSA terms unless explicitly overridden (and the MSA must permit SOW-level overrides in its amendment clause).

---

## Essential Clause Principles

### Indemnification

Indemnification shifts financial risk for specific categories of harm. SMBs should insist on mutual indemnification -- one-sided indemnity is "The One-Sided Indemnity" anti-pattern.

**Standard mutual structure:** Each party indemnifies the other for: (a) bodily injury or property damage, (b) IP infringement claims, (c) breaches of confidentiality, (d) gross negligence or willful misconduct. The indemnifying party controls defense and settlement.

**SMB protection rule:** Never accept indemnification obligations broader than your insurance covers. If your E&O policy caps at $1M, uncapped indemnification is an existential risk.

### Limitation of Liability

Two components: (1) a damages cap, and (2) a consequential damages waiver.

**Damages cap:** Standard is 12 months of fees paid or payable under the applicable SOW. Accepting "total fees paid" instead of "12 months" means your liability shrinks as the contract ages -- counterparty disadvantage.

**Consequential damages waiver:** Both parties waive indirect, incidental, consequential, special, and punitive damages. Carve-outs for indemnification obligations, confidentiality breaches, and IP infringement are common and reasonable. Without a consequential damages waiver, a $50K project could generate a $5M lost-profits claim.

### Termination Provisions

**For cause:** Either party may terminate upon material breach if the breaching party fails to cure within 30 days of written notice. Define "material breach" explicitly -- vague language invites litigation.

**For convenience:** Either party may terminate without cause upon 30-60 days written notice. Include wind-down obligations: payment for work completed, return of materials, transition assistance period.

**Kill fee:** If client terminates for convenience mid-project, contractor is entitled to payment for work completed plus 15-25% of remaining contract value. Without a kill fee, clients can cancel after receiving 80% of value while paying for only 60%.

### Payment Terms

**Net-30** is standard. Net-15 is aggressive but reasonable for small engagements. Net-60 or Net-90 favors the payer and creates cash flow risk for the payee. Late payment should trigger interest at 1.5% per month (18% annually) -- this incentivizes timely payment without being punitive.

**Milestone-based payments** for project work: 25% upon SOW execution, 25% at midpoint milestone, 25% at final delivery, 25% upon acceptance. Never allow more than 50% to depend on a single acceptance event.

---

## NDA Framework

### Mutual vs Unilateral

**Mutual NDA:** Both parties share confidential information. Standard for partnership discussions, vendor evaluations, and M&A due diligence. Use mutual as default -- it signals good faith.

**Unilateral NDA:** One party discloses, the other receives. Appropriate when only one side shares proprietary information (e.g., product demos to prospects). Prospects may resist signing unilateral NDAs before evaluation.

### Critical NDA Elements

1. **Definition of Confidential Information:** Broad enough to cover business information, technical data, customer lists, pricing, and strategies. Include a catch-all: "any information that a reasonable person would consider confidential."
2. **Exclusions:** Information that is: (a) publicly available, (b) already known to the recipient, (c) independently developed, (d) rightfully received from a third party, (e) required by law to be disclosed (with prompt notice to the discloser).
3. **Term:** 2-3 years for the NDA itself. Confidentiality obligations survive 2-5 years after termination. Trade secrets survive indefinitely.
4. **Return/Destroy:** Upon termination or request, recipient must return or certify destruction of all confidential materials within 30 days. Carve-out for archival copies required by law or automated backup systems (with continued confidentiality obligations).

---

## SLA Design

### Uptime Commitments

| Tier | Monthly Uptime | Max Downtime/Month | Typical Use Case |
|------|---------------|-------------------|-----------------|
| Standard | 99.5% | 3.6 hours | Internal tools, non-critical apps |
| Professional | 99.9% | 43.8 minutes | Business-critical SaaS, client-facing |
| Enterprise | 99.95% | 21.9 minutes | Financial services, healthcare, e-commerce |
| Mission-Critical | 99.99% | 4.4 minutes | Payment processing, emergency services |

**Measurement methodology matters:** Define whether uptime is measured from the provider's infrastructure boundary or the end-user experience. Exclude scheduled maintenance windows (with 72-hour advance notice). Measure in 1-minute intervals, not 5-minute -- a 4-minute outage in a 5-minute measurement window registers as zero downtime.

### Response and Resolution Time Tiers

| Severity | Response SLA | Resolution SLA | Example |
|----------|-------------|----------------|---------|
| Critical (P1) | 15 minutes | 4 hours | Complete service outage |
| High (P2) | 1 hour | 8 hours | Major feature unavailable, no workaround |
| Medium (P3) | 4 hours | 2 business days | Feature degraded, workaround exists |
| Low (P4) | 1 business day | 5 business days | Cosmetic issues, enhancement requests |

### Credit Structures

Service credits should be meaningful enough to incentivize compliance. Standard: 5% credit per 0.1% below target, capped at 30% of monthly fees. Credits must be automatic or request-based within 30 days -- requiring complex claims processes is "The Paper Shield" anti-pattern.

---

## Freelancer and Contractor Agreements

### Work-for-Hire Doctrine

Under U.S. copyright law, work created by an employee within the scope of employment is automatically owned by the employer. For independent contractors, work-for-hire applies only to nine enumerated categories (including contributions to collective works and supplementary works). For everything else, an explicit IP assignment clause is required.

**Critical rule:** Every contractor agreement must include BOTH a work-for-hire provision AND a backup IP assignment. The work-for-hire clause covers the enumerated categories. The assignment clause covers everything else. Without the backup assignment, code, designs, and content created by contractors may remain their intellectual property.

### Independent Contractor Classification

Misclassification carries severe penalties: back taxes, penalties, benefits liability. The IRS evaluates three categories:

1. **Behavioral control:** Does the company dictate how, when, and where work is performed? Contractors choose their own methods.
2. **Financial control:** Does the worker have unreimbursed expenses, opportunity for profit/loss, and serve multiple clients? Contractors operate as businesses.
3. **Relationship type:** Are there written contracts, employee-type benefits, or permanency of relationship? Contractor relationships are project-based.

**Safe harbor indicators:** Written contract specifying independent contractor status, contractor provides own equipment, contractor sets own schedule, contractor serves multiple clients, contractor invoices for services, no employee benefits provided.

### Deliverable Acceptance

Define acceptance criteria in the SOW. Provide a review period (5-10 business days). Specify revision rounds (2 rounds standard). After acceptance period expires without written rejection, deliverables are deemed accepted. This prevents "The Infinite Revision Loop" where clients withhold acceptance indefinitely.

---

## Terms of Service Structure

### SaaS/Web Service ToS Core Sections

1. **Acceptance of Terms** -- How users agree (clickwrap, browsewrap), age restrictions, authority to bind organization
2. **Account Terms** -- Registration requirements, account security obligations, account termination
3. **Acceptable Use Policy** -- Prohibited activities, resource limits, enforcement actions
4. **User Content** -- License grant from users, content ownership, content moderation rights, DMCA procedures
5. **Intellectual Property** -- Provider's IP rights, trademark usage, feedback license
6. **Payment and Billing** -- Subscription terms, auto-renewal disclosure, refund policy, price change notice
7. **Service Availability** -- SLA reference, maintenance windows, force majeure
8. **Limitation of Liability** -- Mirror the MSA structure, adapted for consumer/user context
9. **Dispute Resolution** -- Mandatory arbitration (if applicable), class action waiver, governing law
10. **Modification of Terms** -- Notice period for changes (30 days minimum), continued use as acceptance

### DMCA Safe Harbor

To qualify for DMCA safe harbor protection: (1) designate a DMCA agent with the Copyright Office, (2) publish a DMCA policy with takedown/counter-notice procedures, (3) implement a repeat infringer policy, (4) accommodate standard technical measures. Failure to designate an agent eliminates safe harbor protection entirely.

---

## Contract Negotiation Framework

### Red-Line Priority Matrix

Categorize every clause before entering negotiation:

| Priority | Definition | Examples |
|----------|-----------|---------|
| Must-Have | Non-negotiable. Walk away if rejected. | Liability cap, IP ownership, payment terms |
| Should-Have | Important but flexible on specifics. | Termination convenience period, warranty duration |
| Nice-to-Have | Preferred but concedable for Must-Have gains. | Audit rights, reporting frequency |
| Concedable | Willing to accept counterparty's version. | Governing law (if reasonable jurisdiction), notice methods |

**Pre-negotiation rule:** Identify your Must-Haves, then identify the counterparty's likely Must-Haves. Trades happen when your Concedable aligns with their Must-Have and vice versa. Enter every negotiation knowing what you will trade and what you will not.

### Common Negotiation Patterns

- **The Anchor:** Counterparty starts with extreme position to shift the midpoint. Counter by ignoring the anchor and presenting your own starting position.
- **The Nibble:** After reaching agreement, counterparty adds small last-minute requests. Respond by treating each nibble as a reopening of the full negotiation.
- **The Good Cop/Bad Cop:** Counterparty's legal team rejects everything while their business team sympathizes. Negotiate directly with the decision-maker.
- **The Deadline Squeeze:** Counterparty imposes artificial urgency. Never accept unfavorable terms because of time pressure -- urgency is almost always manufactured.

---

## Named Anti-Patterns

### The Handshake Deal
Operating on verbal agreements without written contracts. Seems efficient until a dispute arises and there is no documentation of scope, payment, IP ownership, or termination rights. **Detect:** Any engagement exceeding $1,000 or 2 weeks without a signed agreement. **Fix:** Implement a minimum-viable contract for every engagement, even small ones. A 2-page letter agreement beats a handshake.

### The Template Blindness
Using downloaded contract templates without customizing them for the specific engagement, jurisdiction, or risk profile. Templates contain placeholder language, inapplicable clauses, and jurisdiction-specific provisions that may not apply. **Detect:** Contract contains "[COMPANY NAME]" placeholders, references laws from a different state, or includes irrelevant industry clauses. **Fix:** Treat templates as starting frameworks, not finished products. Review every clause for applicability.

### The Scope Creep Enabler
Vague deliverable definitions that allow unlimited interpretation of what is "included." Statements like "and other related services" or "including but not limited to" without boundaries. **Detect:** SOW deliverables section uses open-ended language, lacks acceptance criteria, or has no explicit exclusions section. **Fix:** Define deliverables with measurable acceptance criteria. Add an "Out of Scope" section equal in detail to the "In Scope" section.

### The One-Sided Indemnity
Accepting unlimited indemnification obligations while the counterparty limits theirs. Common in enterprise vendor agreements where the larger party imposes asymmetric risk. **Detect:** Indemnification section is not mutual, or your indemnification obligations are broader than theirs. **Fix:** Insist on mutual indemnification with identical scope. If counterparty insists on asymmetry, cap your additional obligations at the liability limit.

### The Perpetual Lock-In
Auto-renewal clauses with long notice periods (90+ days), early termination penalties, and no termination-for-convenience rights. Designed to make exit prohibitively expensive. **Detect:** Contract auto-renews for periods longer than the initial term, cancellation window is shorter than 30 days, or early termination requires paying remaining contract value. **Fix:** Negotiate 30-day cancellation notice, annual renewal caps, and termination-for-convenience with reasonable wind-down.

### The Paper Shield
Including SLA commitments with no meaningful remedies. Uptime guarantees that promise credits only if the customer completes a multi-step claims process within 7 days. **Detect:** SLA credits require manual claims, have short filing windows, or are capped at insignificant amounts (<5% of monthly fees). **Fix:** Require automatic credit application, reasonable filing windows (30 days), and credits meaningful enough to incentivize compliance (15-30% of monthly fees).

---

## Rationalization Table

| Temptation | Why It Fails | Do This Instead |
|------------|-------------|-----------------|
| "We trust them, we don't need a formal contract" | Trust is not a legal defense. When relationships sour -- and they do -- undocumented terms become he-said-she-said disputes with no resolution mechanism. | Draft a minimum-viable agreement for every engagement over $1K. Trust and contracts are complementary, not alternatives. |
| "Legal review costs more than the deal is worth" | A $500 legal review prevents a $50,000 dispute. The cost of a bad contract is never the contract value -- it is the liability exposure, lost IP, and dispute resolution costs. | Use attorney-reviewed templates for small deals. Reserve full legal review for contracts above $10K or those with unusual risk profiles. |
| "We'll add that clause later when it matters" | Amending signed contracts requires mutual consent. The counterparty has no incentive to add protections for you post-signature. | Include all necessary protections in the initial agreement. It is always easier to negotiate terms before signing than after. |
| "Their template is standard, no need to review" | Every "standard" template favors the drafter. Enterprise procurement templates routinely include unlimited indemnification, IP assignment of pre-existing work, and unilateral termination rights. | Red-line every counterparty template. Assume every clause was drafted to benefit them. Negotiate from your own template when possible. |
| "Auto-renewal saves us the hassle of renegotiating" | Auto-renewal without a review trigger locks you into potentially outdated terms, above-market pricing, and service levels that no longer match your needs. | Set calendar reminders 90 days before renewal dates. Review terms, benchmark pricing, and renegotiate before the auto-renewal window closes. |

---

## Red Flags Checklist

Monitor these indicators in any contract you review. Any single flag warrants legal review. Two or more flags simultaneously demand attorney involvement before signing.

- [ ] **No limitation of liability clause** -- Unlimited liability exposure can exceed the contract value by orders of magnitude. Insist on a cap.
- [ ] **One-sided indemnification** -- You indemnify them broadly, they indemnify you narrowly or not at all. Restructure to mutual.
- [ ] **Vague deliverable definitions** -- "Services as needed" or "related work" without boundaries. Demand measurable acceptance criteria.
- [ ] **No termination for convenience** -- You can only exit for cause, which requires proving material breach. Negotiate convenience termination with reasonable notice.
- [ ] **IP assignment of pre-existing work** -- Assignment clause that captures your background IP, not just project work product. Carve out pre-existing IP explicitly.
- [ ] **Auto-renewal with short cancellation window** -- 30-day cancellation window on an annual auto-renewal means 335 days per year you cannot exit. Extend the cancellation window.
- [ ] **Governing law in unfavorable jurisdiction** -- Contract governed by laws of a jurisdiction with no connection to either party. Negotiate your home jurisdiction or a neutral one.
- [ ] **No dispute resolution escalation** -- Contract jumps directly to litigation with no mediation or arbitration step. Add escalation: direct negotiation (30 days), mediation (60 days), then arbitration or litigation.
- [ ] **Payment terms exceeding Net-60** -- Extended payment terms signal cash flow issues or power imbalance. Negotiate Net-30 or request upfront deposits.
- [ ] **No force majeure clause** -- Without it, performance obligations continue regardless of extraordinary events. Include force majeure with specific trigger events and notification requirements.
