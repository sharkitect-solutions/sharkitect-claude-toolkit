# K1-K5 Knowledge Classification System

## Classification Criteria Matrix

### K1 — Critical Enterprise Knowledge
**Definition**: Loss or corruption of this knowledge would cause immediate operational failure or significant business harm.
**Characteristics**:
- Directly governs revenue, compliance, or client relationships
- No alternative source exists (single point of truth)
- Used in daily operations by multiple stakeholders
- Regulatory or contractual obligation to maintain

**Examples**:
- Client contracts and active agreements
- Pricing model and rate cards
- Compliance documentation (GDPR, CCPA policies)
- Business continuity plans
- Financial reporting templates
- Master service agreements

**Review**: Monthly | **Backup**: Real-time sync to Supabase | **Access**: Restricted to authorized roles

### K2 — Core Operational Knowledge
**Definition**: Loss would cause significant disruption to operations but not immediate failure. Recoverable with effort.
**Characteristics**:
- Governs how work gets done (processes, standards, patterns)
- Multiple people reference regularly
- Changes require review and approval
- Supports decision-making across the organization

**Examples**:
- Standard Operating Procedures (SOPs)
- Architecture decision records
- Workflow documentation
- Brand guidelines and voice standards
- Technology stack documentation
- Onboarding materials

**Review**: Quarterly | **Backup**: Weekly sync | **Access**: All team members

### K3 — Standard Reference Knowledge
**Definition**: Loss would be inconvenient but not disruptive. Can be reconstructed from other sources with moderate effort.
**Characteristics**:
- Supports ongoing work but isn't essential to operations
- Referenced periodically, not daily
- Created as output of specific activities
- Value degrades over time without updates

**Examples**:
- Project plans and implementation documents
- Meeting notes and decision summaries
- Research reports and market analyses
- Competitive intelligence snapshots
- Historical performance data
- Training materials

**Review**: Semi-annually | **Backup**: Monthly sync | **Access**: Open

### K4 — Supporting Context Knowledge
**Definition**: Loss would create a minor gap. Provides background context that aids understanding but isn't operationally necessary.
**Characteristics**:
- Historical value primarily
- Rarely referenced after initial creation
- Value comes from pattern recognition across multiple K4 documents
- Low maintenance cost justifies retention

**Examples**:
- Past project retrospectives
- Historical client communications
- Superseded architecture documents
- Old research that informed current decisions
- Reference implementations and examples

**Review**: Annually | **Backup**: Quarterly | **Access**: Open

### K5 — Experimental Knowledge
**Definition**: Temporary, disposable content. Created for exploration, testing, or short-term use.
**Characteristics**:
- Expected lifespan: 30 days maximum
- No one depends on it for operations
- Value is in the creation process, not the artifact
- Should be promoted (to K3+) or deleted at 30 days

**Examples**:
- Draft ideas and brainstorms
- Test documents and scratch notes
- Prototype specifications
- Temporary analysis for a specific question
- Experimental templates or formats

**Review**: On creation (30-day expiry) | **Backup**: None | **Access**: Creator only

## Classification Decision Flow

```
1. Would losing this document cause IMMEDIATE operational failure?
   YES --> K1
   NO  --> Continue

2. Would losing this cause SIGNIFICANT disruption to daily work?
   YES --> K2
   NO  --> Continue

3. Is this referenced REGULARLY (at least monthly) by the team?
   YES --> K3
   NO  --> Continue

4. Does this provide HISTORICAL CONTEXT that aids future decisions?
   YES --> K4
   NO  --> K5 (with 30-day expiry)
```

## Reclassification Triggers

- K5 document referenced 3+ times → promote to K3
- K3 document not referenced in 6 months → consider K4
- K4 document contradicted by newer K2 → archive or update
- K2 document becomes subject to compliance requirement → promote to K1
- K1 document's governing contract expires → demote to K4 (historical)
