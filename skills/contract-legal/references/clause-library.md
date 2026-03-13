# Contract Clause Library

Quick-reference for the 18 most critical contract clauses. Each entry covers what the clause does, its risk level, common variations, and red flags to watch for in counterparty versions.

## Critical Clauses (Must Include -- Omission Creates Existential Risk)

### 1. Limitation of Liability
**What it does:** Caps the maximum financial exposure either party faces under the contract.
**Standard language:** Total aggregate liability capped at 12 months of fees paid or payable under the applicable SOW. Mutual exclusion of indirect, consequential, incidental, special, and punitive damages.
**Variations:** (a) Cap at total fees paid (favors provider in long contracts -- liability shrinks over time), (b) Cap at fees payable in current term (balanced), (c) Per-incident cap vs aggregate cap (per-incident allows multiple claims to exceed aggregate).
**Red flags:** No cap stated (unlimited liability), cap applies to only one party, consequential damages exclusion is one-sided, carve-outs so broad they swallow the cap (e.g., "except for any breach of this agreement").
**SMB-friendly alternative:** "Neither party's total aggregate liability shall exceed the greater of (a) fees paid in the 12 months preceding the claim or (b) $[floor amount]."

### 2. Indemnification
**What it does:** Shifts financial responsibility for third-party claims arising from specific categories of harm.
**Standard scope:** Mutual indemnification for (a) IP infringement, (b) confidentiality breaches, (c) gross negligence or willful misconduct, (d) bodily injury or property damage.
**Variations:** (a) Duty to defend vs duty to indemnify (defense duty is broader -- includes legal costs even if claim fails), (b) Control of defense (indemnifying party controls, but indemnified party participates), (c) Settlement approval (neither party settles without the other's consent).
**Red flags:** One-sided indemnification, indemnification scope broader than insurance coverage, no cap on indemnification obligations, obligation to indemnify for the other party's own negligence.
**SMB-friendly alternative:** Mirror indemnification -- identical obligations for both parties, capped at the liability limit.

### 3. Intellectual Property Ownership
**What it does:** Defines who owns work product created during the engagement.
**Standard structure:** Client owns deliverables upon full payment. Provider retains pre-existing IP and tools, granting client a perpetual license. Provider retains right to use general knowledge and techniques.
**Variations:** (a) Joint ownership (problematic -- either party can exploit without consent), (b) Assignment with license-back (client owns everything, licenses provider's tools back), (c) License-only (provider retains ownership, grants client usage license).
**Red flags:** Assignment of pre-existing IP (your background tools and frameworks), no license-back for provider's reusable components, ownership transfers before payment, "work product" defined to include internal communications and draft materials.

### 4. Termination
**What it does:** Defines how and when either party can end the agreement.
**Standard structure:** Termination for cause (30-day cure period after written notice of material breach) and termination for convenience (30-60 day written notice).
**Variations:** (a) Immediate termination for insolvency or bankruptcy, (b) Termination upon change of control, (c) Termination for persistent minor breaches (3+ breaches in 12 months even if individually cured).
**Red flags:** No termination for convenience (you can only exit by proving breach), asymmetric convenience rights (they can exit freely, you cannot), no cure period, termination triggers immediate payment of remaining contract value.

### 5. Confidentiality
**What it does:** Protects proprietary information shared between parties.
**Standard structure:** Mutual obligations. Confidential information defined broadly with five standard exclusions (public, prior knowledge, independent development, third-party receipt, legal compulsion).
**Variations:** (a) Survival period 2 years vs 5 years vs indefinite for trade secrets, (b) Residuals clause (permits use of general knowledge retained in unaided memory), (c) Return vs destroy (return is verifiable, destruction requires certification).
**Red flags:** One-sided confidentiality, no exclusions for independently developed information, no carve-out for legal compulsion with notice, survival period shorter than 2 years, no return/destroy obligation.

### 6. Governing Law and Jurisdiction
**What it does:** Determines which state/country's laws apply and where disputes are litigated.
**Standard approach:** Governing law of one party's home state, with exclusive jurisdiction in that state's courts.
**Variations:** (a) Governing law of one state, jurisdiction in another (creates complexity), (b) Delaware law (common in US tech contracts for its well-developed business law), (c) Arbitration instead of court jurisdiction.
**Red flags:** Governing law of a jurisdiction with no connection to either party, mandatory jurisdiction in a distant location (increases dispute costs), foreign governing law for a domestic deal.

## Important Clauses (Should Include -- Omission Creates Significant Risk)

### 7. Payment Terms
**Standard:** Net-30 from invoice date, 1.5%/month late interest, right to suspend services for payments 15+ days overdue.
**Red flags:** Net-60+ without justification, no late payment penalties, payment contingent on client's receipt of funds from a third party ("pay-when-paid"), no right to suspend for non-payment.

### 8. Force Majeure
**Standard:** Excuses performance for events beyond reasonable control (natural disasters, pandemics, war, government action). Affected party notifies within 72 hours, mitigates where possible, either party may terminate if force majeure exceeds 90 days.
**Red flags:** No force majeure clause (performance required regardless of circumstances), one-sided (only excuses one party), includes economic hardship or market changes (these are business risks, not force majeure), no termination right for extended force majeure.

### 9. Dispute Resolution
**Standard escalation:** Direct negotiation between designated representatives (30 days), then mediation (60 days), then binding arbitration or litigation. Each step must be exhausted before escalating.
**Red flags:** Direct to litigation (expensive and slow), mandatory arbitration with a provider the counterparty selects, no escalation path, loser-pays provisions in jurisdictions where this is not standard.

### 10. Non-Solicitation
**Standard:** Neither party solicits the other's employees or contractors for 12-24 months during the agreement and for 12 months after termination. Does not restrict responding to general job postings.
**Red flags:** Extends beyond employees to clients or vendors (non-compete disguised as non-solicitation), survival period exceeding 24 months (enforceability varies by state), no carve-out for general advertisements.

### 11. Warranty
**Standard:** Provider warrants services performed in a professional and workmanlike manner consistent with industry standards. Deliverables conform to specifications for 30-90 days post-acceptance.
**Red flags:** No warranty at all ("as-is"), warranty period shorter than 30 days, warranty voided by any modification, no remedy specified (warranty without remedy is decorative).

### 12. Assignment
**Standard:** Neither party may assign without prior written consent, not to be unreasonably withheld. Exception: assignment to an affiliate or successor in a merger/acquisition.
**Red flags:** One party can assign freely while the other cannot, no exception for M&A (locks you into the contract even if the counterparty is acquired by a competitor), assignment includes delegation of obligations to unvetted third parties.

## Standard Clauses (Include for Completeness)

### 13. Entire Agreement
Supersedes all prior written and oral agreements. Prevents parties from claiming verbal side agreements modify the contract. Always include.

### 14. Severability
If any provision is found unenforceable, the remainder survives. Without this, a single invalid clause could void the entire contract.

### 15. Amendment
Modifications require written agreement signed by both parties. Prevents informal email exchanges from inadvertently modifying contract terms.

### 16. Notices
Defines how formal communications must be delivered (certified mail, email to designated addresses). Specifies when notice is deemed received. Prevents disputes about whether a party was properly notified.

### 17. Waiver
Failure to enforce a provision does not waive the right to enforce it later. Without this, not enforcing a late payment once could be argued as waiving all future late payment claims.

### 18. Survival
Specifies which clauses survive termination (confidentiality, indemnification, limitation of liability, IP ownership, payment obligations). Without a survival clause, obligations may end at termination even when they should persist.

## Clause Review Checklist

When reviewing any counterparty contract, check each clause against this sequence:

1. **Is it mutual?** If obligations apply to only one party, flag for negotiation.
2. **Is it capped?** Financial obligations without limits create open-ended risk.
3. **Is it clear?** Ambiguous language is interpreted against the drafter -- but litigation to get that interpretation is expensive.
4. **Is it enforceable in your jurisdiction?** Non-competes, penalty clauses, and certain arbitration provisions vary by state.
5. **Is it insured?** Any obligation exceeding your insurance coverage is a personal liability risk for the business owner.
