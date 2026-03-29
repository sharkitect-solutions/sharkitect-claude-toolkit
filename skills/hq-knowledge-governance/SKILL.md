---
name: hq-knowledge-governance
description: >
  Use when auditing knowledge base health, classifying documents by criticality (K1-K5),
  checking cross-reference integrity, identifying documentation gaps, enforcing governance compliance,
  or when the user asks about knowledge organization, document freshness, or KB audits.
  NEVER use for generic documentation writing (use documentation-templates skill),
  generic knowledge base design for non-Sharkitect projects (use knowledge-management skill),
  or research synthesis from web sources (use research-synthesizer agent).
version: 0.1.0
---

# HQ Knowledge Governance — K1-K5 Classification & Audit System

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/k-classification.md` | Classifying new documents or reclassifying existing ones | Simple document reads with no classification need |
| `references/governance-protocol.md` | Running compliance checks, reviewing governance adherence | Quick document lookups or edits |
| `references/audit-methodology.md` | Running KB audits, freshness checks, gap analysis | Single document operations |

## Paired Agent

Launch `knowledge-governance` agent (Task tool) for execution-heavy work:
- Full KB audits (scanning all documents, checking freshness, finding orphans)
- Cross-reference integrity checks (verifying links between documents)
- Batch classification operations

Use this skill directly (without agent) for:
- Classifying a single document
- Quick governance compliance checks on one item
- Answering questions about the K1-K5 system

## K1-K5 Classification Quick Reference

| Level | Name | Description | Review Cadence | Examples |
|-------|------|-------------|----------------|----------|
| **K1** | Critical Enterprise | Loss = operational failure | Monthly | Client contracts, pricing model, compliance docs |
| **K2** | Core Operational | Loss = significant disruption | Quarterly | SOPs, workflow docs, architecture decisions |
| **K3** | Standard Reference | Loss = inconvenience | Semi-annually | Meeting notes, project plans, research summaries |
| **K4** | Supporting Context | Loss = minor gap | Annually | Historical decisions, past analyses, reference material |
| **K5** | Experimental | Temporary, disposable | On creation (30-day expiry) | Draft ideas, test documents, scratch notes |

**Default-to-Higher Rule**: When uncertain between two levels, classify at the HIGHER (more critical) level. Downgrading is safe; missing a critical classification is not.

## Governance Decision Tree

```
NEW DOCUMENT ARRIVES
  |
  +-- Classify using K1-K5 (see references/k-classification.md)
  |
  +-- Check: Does it REPLACE an existing document?
  |     YES --> Version the old one, update cross-references
  |     NO  --> Check: Does it RELATE to existing documents?
  |               YES --> Add cross-references in both directions
  |               NO  --> Standalone document, proceed
  |
  +-- Apply metadata:
  |     - Classification level (K1-K5)
  |     - Owner (who maintains it)
  |     - Review date (based on cadence)
  |     - Related documents (cross-references)
  |
  +-- Store in appropriate location based on classification
```

## Audit Triggers

Run a KB audit when ANY of these conditions are true:
1. **Scheduled**: Monthly for K1, quarterly for K2, semi-annually for K3
2. **Event-driven**: After a major project completion, restructure, or process change
3. **Signal-based**: User reports stale information, or a document conflict is discovered
4. **Capacity**: When new documents exceed 10% growth since last audit

## Anti-Patterns

1. **Classifying Everything as K1**: If everything is critical, nothing is. Use the classification criteria strictly. Most documents are K2-K3.
2. **Skipping Cross-References**: Orphaned documents become invisible. Every document must link to at least one related document.
3. **Audit Without Action**: Finding issues without creating remediation tasks is worse than not auditing — it creates a false sense of governance.
4. **Stale Review Dates**: A review date that passes without review is a governance failure. Either review or reschedule with justification.
5. **Over-Classifying K5**: Experimental documents that become operational should be reclassified immediately. K5 that survives 30 days without reclassification should be deleted or promoted.
