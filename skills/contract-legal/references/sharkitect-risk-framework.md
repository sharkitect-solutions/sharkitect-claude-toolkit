# Sharkitect Digital Risk Assessment Framework

## 12-Category Risk Scoring

Every contract, engagement, and significant business decision is scored across 12 risk categories. Each category is scored 1-5 (1=minimal risk, 5=critical risk). Total score determines the risk level and required approval process.

### Risk Categories

| # | Category | What It Measures | 1 (Low) | 5 (High) |
|---|----------|-----------------|---------|----------|
| 1 | **Financial exposure** | Maximum possible financial loss | <$1K | >$25K |
| 2 | **Revenue dependency** | % of revenue from this client/deal | <5% | >25% |
| 3 | **Scope clarity** | How well-defined is the work | Crystal clear SOW | Vague/evolving |
| 4 | **Client sophistication** | Client's tech/business maturity | Experienced buyer | First-time buyer, unclear expectations |
| 5 | **Payment risk** | Likelihood of payment issues | Strong credit, upfront pay | No history, net terms |
| 6 | **IP/data sensitivity** | Sensitivity of information handled | Public data only | PII, financial, health data |
| 7 | **Third-party dependency** | Reliance on external platforms/APIs | None | Critical path depends on 3rd party |
| 8 | **Timeline pressure** | Deadline rigidity and consequences | Flexible | Hard deadline, penalties for miss |
| 9 | **Reputational impact** | Potential brand damage if it goes wrong | Internal only | Public-facing, high-profile client |
| 10 | **Legal complexity** | Regulatory or contractual complexity | Standard terms | Custom terms, regulated industry |
| 11 | **Resource commitment** | % of capacity this consumes | <10% | >50% |
| 12 | **Exit difficulty** | How hard is it to walk away if needed | Easy termination | Multi-year lock-in, migration complexity |

### Risk Level Determination

| Total Score | Level | Label | Required Actions |
|:-----------:|:-----:|-------|-----------------|
| 12-20 | 1 | **Green — Standard** | Standard contract, no special review |
| 21-30 | 2 | **Yellow — Elevated** | Review contract terms, add protective clauses |
| 31-40 | 3 | **Orange — High** | CEO review required, enhanced contract terms |
| 41-50 | 4 | **Red — Critical** | CEO + legal review, consider declining |
| 51-60 | 5 | **Black — Extreme** | Decline unless extraordinary justification |

## DRAFT Label Protocol

All documents, proposals, and contracts in progress must carry a DRAFT label until finalized:

### Label Rules
- **DRAFT** — Working document, subject to change. Not binding.
- **FINAL DRAFT** — Content-complete, under final review. Not yet binding.
- **EXECUTED** — Signed by all parties. Binding.
- **SUPERSEDED** — Replaced by a newer version. Not binding. Archive reference only.

### Where Labels Appear
- Document header (first page, top-right)
- Document footer (every page)
- Email subject line when sharing ("DRAFT: [Document Name]")
- File name suffix ("proposal-acme-DRAFT.pdf")

### Why This Matters
One "draft" proposal sent without the label was treated as a binding offer by a client. The DRAFT label protocol prevents unintentional commitments. Every document that isn't EXECUTED is a DRAFT. No exceptions.

## Standard Contract Clauses (Required)

Every client contract must include these protective clauses:

### Scope Limitation
"This agreement covers only the deliverables explicitly listed in the Scope of Work. Any additional work, changes, or expansions to scope require a written change order signed by both parties and may incur additional fees."

### Limitation of Liability
"Total liability under this agreement shall not exceed the fees paid by Client in the twelve (12) months preceding the claim. Neither party shall be liable for indirect, consequential, or incidental damages."

### Termination
"Either party may terminate this agreement with thirty (30) days written notice. Client shall pay for all work completed through the termination date. Setup fees are non-refundable."

### IP Assignment
"All deliverables become Client's property upon full payment. Sharkitect Digital retains the right to use anonymized versions of the work for portfolio and marketing purposes unless Client opts out in writing."

### Confidentiality
"Both parties agree to keep confidential all non-public information shared during the engagement. This obligation survives termination for two (2) years."

### Force Majeure
"Neither party shall be liable for delays caused by circumstances beyond reasonable control, including but not limited to: acts of God, government actions, pandemic, war, or disruption of third-party services upon which deliverables depend."

## Risk Mitigation Checklist

Before signing any engagement:

- [ ] Risk score calculated (all 12 categories)
- [ ] Risk level appropriate for our capacity (no Level 4+ without CEO approval)
- [ ] Standard contract clauses included
- [ ] Payment terms specified (upfront %, schedule, late fees)
- [ ] Scope of Work is specific and measurable
- [ ] All documents properly labeled (DRAFT until executed)
- [ ] Client has acknowledged AI usage in service delivery (where applicable)
- [ ] Exit strategy exists (can we walk away cleanly if needed?)
- [ ] Insurance coverage confirmed adequate for this engagement
- [ ] No single-client revenue dependency >25%

## Escalation Triggers

| Trigger | Action | Timeline |
|---------|--------|----------|
| Risk score 31+ | CEO review before proceeding | Before proposal |
| Client wants custom terms | Legal review of changes | Before signing |
| Regulated industry (health, finance, legal) | Category 10 auto-scores 4+ | Flag immediately |
| Client requests IP exclusivity | Assess impact on portfolio rights | Before signing |
| Payment 30+ days overdue | Pause work, escalate to CEO | Day 31 |
| Scope dispute | Reference SOW, document disagreement | Immediately |
| Client threatens legal action | CEO + legal advisor immediately | Same day |
