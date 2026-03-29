# Knowledge Base Audit Methodology

## Audit Types

### Full Audit (Quarterly)
Scope: All documents across all K-levels.
Duration: 1-2 sessions depending on KB size.
Deliverable: Audit report with findings, severity ratings, remediation tasks.

### Targeted Audit (On-demand)
Scope: Specific department, classification level, or document set.
Duration: 30-60 minutes.
Deliverable: Targeted findings with immediate remediation.

### Freshness Check (Monthly)
Scope: K1 and K2 documents only.
Duration: 15-30 minutes.
Deliverable: List of stale documents with recommended actions.

## 8-Step Audit Process

### Step 1: Inventory
- Count all documents by classification level
- Compare against last audit's inventory
- Flag: New documents added, documents deleted, documents moved

### Step 2: Freshness Scoring
For each document, calculate freshness score:
```
freshness_score = days_since_last_review / max_review_interval_for_k_level
```
- Score < 0.5: FRESH (green)
- Score 0.5-1.0: APPROACHING (yellow)
- Score > 1.0: STALE (red)
- Score > 2.0: CRITICAL (black) — double the review interval has passed

### Step 3: Orphan Detection
Identify documents with zero inbound cross-references.
- K1-K2 orphans: S2 severity (must be connected)
- K3 orphans: S3 severity (should be connected)
- K4-K5 orphans: S4 severity (expected for some)

### Step 4: Duplicate Detection
Scan for documents covering the same topic at the same classification level.
- Same topic + same K-level: Merge into single authoritative version
- Same topic + different K-levels: Verify higher-K version is the authority
- Near-duplicates: Flag for human review

### Step 5: Conflict Identification
Check for contradictory information across documents.
- Direct contradiction (Document A says X, Document B says NOT-X): S1 severity
- Soft conflict (different numbers, different processes for same thing): S2 severity
- Version conflict (old and new version both active): S3 severity

### Step 6: Ownership Verification
For K1-K2 documents:
- Is the owner still active/relevant?
- Has the owner reviewed within the required cadence?
- Are there documents with no owner assigned?

### Step 7: Cross-Reference Integrity
Verify all cross-references point to:
- Documents that still exist
- Documents at correct classification levels
- Documents with correct content (reference isn't to a renamed/moved doc)

### Step 8: Report Generation

Audit report structure:
```markdown
## KB Audit Report — [Date]

### Summary
- Documents scanned: [N]
- Findings: [N] (S1: [n], S2: [n], S3: [n], S4: [n])
- Overall health: [HEALTHY / NEEDS ATTENTION / AT RISK]

### Critical Findings (S1-S2)
[Table of findings with document, issue, severity, remediation]

### Remediation Queue
[Prioritized list of actions needed]

### Metrics Comparison (vs Last Audit)
[Freshness trend, orphan count trend, conflict count trend]
```

## Audit Anti-Patterns

1. **Audit Fatigue**: Running audits too frequently without acting on findings. Better to audit less and remediate fully.
2. **Metrics Without Context**: "15 stale documents" means nothing without knowing if that's 15 out of 20 (bad) or 15 out of 500 (acceptable).
3. **Ignoring K4-K5**: While lower priority, K4-K5 debris accumulates and makes audits slower over time. Clean regularly.
4. **Manual-Only Audits**: Use the `knowledge-governance` agent for scanning/counting. Reserve human judgment for classification decisions and conflict resolution.
