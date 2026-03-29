# Security Tier Classification System

## Tier Definitions

### Tier 0 — Public
**Data sensitivity**: None. Information is intended for public consumption.
**Access control**: None required.
**Audit requirements**: None.
**Examples**: Marketing website content, public documentation, blog posts, social media content.
**Integration requirements**: Standard HTTPS. No special handling.

### Tier 1 — Internal
**Data sensitivity**: Low. Business information not intended for external audiences.
**Access control**: Authentication required. Team-wide access acceptable.
**Audit requirements**: Basic access logging.
**Examples**: Internal dashboards, KPI reports, project plans, team communications, internal SOPs.
**Integration requirements**: Authenticated API calls. API keys stored in environment variables, not code.

### Tier 2 — Confidential
**Data sensitivity**: Medium-High. Client data, financial information, competitive intelligence.
**Access control**: Role-based access. Only authorized roles can read/write.
**Audit requirements**: Full access logging with timestamps and user IDs.
**Examples**: Client contracts, pricing proposals, financial records, client project data, competitive analyses, Supabase client data.
**Integration requirements**: Encrypted connections (TLS 1.2+). API keys in secret manager or .env. No client data in logs. Row-Level Security (RLS) for database access.

### Tier 3 — Critical
**Data sensitivity**: High. Compromise = immediate business harm, legal liability, or security breach.
**Access control**: MFA required. Individual-level access only. Principle of least privilege.
**Audit requirements**: Immutable audit trail. Alert on anomalous access patterns.
**Examples**: API keys and credentials, payment processing data, PII (names, emails, phone numbers combined), authentication tokens, encryption keys, Supabase service role keys.
**Integration requirements**: Encrypted at rest AND in transit. Secret rotation schedule. No hardcoding anywhere. Immediate escalation on suspected compromise.

## Classification Decision Flow

```
1. Does this data include credentials, payment info, or combined PII?
   YES --> Tier 3 (Critical)
   NO  --> Continue

2. Does this data belong to or describe a specific client?
   YES --> Tier 2 (Confidential)
   NO  --> Continue

3. Is this data intended only for internal team use?
   YES --> Tier 1 (Internal)
   NO  --> Tier 0 (Public)
```

## New Integration Security Checklist

Before connecting any new API, MCP server, or third-party service:

- [ ] **Classify the tier** of data it will access
- [ ] **Review authentication method** (OAuth preferred over API key for Tier 2+)
- [ ] **Check data residency** (where is data stored? GDPR implications?)
- [ ] **Assess vendor security** (SOC 2? GDPR compliant? Security page?)
- [ ] **Define access scope** (minimum permissions needed)
- [ ] **Document in tech-stack.md** (what, why, tier, access scope)
- [ ] **Set review date** (re-evaluate quarterly for Tier 2+)

## Incident Response by Tier

| Tier | Response | Timeline |
|------|----------|----------|
| Tier 0 | Log and monitor | Next business day |
| Tier 1 | Investigate, patch if needed | Same day |
| Tier 2 | Investigate immediately, notify affected clients if data exposed | Within 4 hours |
| Tier 3 | IMMEDIATE: Rotate credentials, lock access, investigate. Notify user. | Within 1 hour |
