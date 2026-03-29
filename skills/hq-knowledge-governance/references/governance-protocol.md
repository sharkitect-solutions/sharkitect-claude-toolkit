# Knowledge Governance Protocol

## Compliance Checks

Every document in the knowledge base must satisfy these governance requirements based on its classification level.

### K1 Compliance Checklist
- [ ] Owner assigned and active
- [ ] Last reviewed within 30 days
- [ ] Cross-references verified (all links valid)
- [ ] Backed up to Supabase (real-time sync confirmed)
- [ ] Version history maintained (at least last 3 versions)
- [ ] No conflicting documents at same or higher classification
- [ ] Access controls appropriate (restricted if contains client/financial data)

### K2 Compliance Checklist
- [ ] Owner assigned
- [ ] Last reviewed within 90 days
- [ ] Cross-references verified
- [ ] Backed up to Supabase (weekly sync)
- [ ] No conflicting documents at same level

### K3 Compliance Checklist
- [ ] Last reviewed within 180 days
- [ ] At least one cross-reference exists
- [ ] No duplicate covering same topic

### K4 Compliance Checklist
- [ ] Tagged as historical/supporting
- [ ] Not contradicted by newer documents

### K5 Compliance Checklist
- [ ] Creation date recorded
- [ ] 30-day expiry date set
- [ ] Promote-or-delete decision pending if past expiry

## Severity Tiers for Governance Violations

| Tier | Description | Response Time | Example |
|------|-------------|---------------|---------|
| **S1** | Enterprise risk — K1 document missing, corrupted, or conflicting | Immediate (same session) | Client contract missing from KB |
| **S2** | Operational risk — K2 document stale or unowned | Within 24 hours | SOP not updated after process change |
| **S3** | Quality risk — Cross-reference broken or duplicate detected | Within 1 week | Dead link between related docs |
| **S4** | Hygiene — K5 past expiry, minor metadata issues | Next scheduled audit | Draft document still in KB after 60 days |

## Review Cadence Calendar

| Month | K1 Review | K2 Review | K3 Review | K4 Review |
|-------|-----------|-----------|-----------|-----------|
| Jan | Yes | Yes | Yes | Yes (annual) |
| Feb | Yes | | | |
| Mar | Yes | | | |
| Apr | Yes | Yes | | |
| May | Yes | | | |
| Jun | Yes | | | |
| Jul | Yes | Yes | Yes | |
| Aug | Yes | | | |
| Sep | Yes | | | |
| Oct | Yes | Yes | | |
| Nov | Yes | | | |
| Dec | Yes | | | |

## Escalation Protocol

1. **S1 violations**: Halt current work. Resolve immediately. Notify user.
2. **S2 violations**: Log finding. Create remediation task. Include in next brief.
3. **S3 violations**: Log finding. Add to next audit's remediation queue.
4. **S4 violations**: Log finding. Batch-resolve during next scheduled audit.
