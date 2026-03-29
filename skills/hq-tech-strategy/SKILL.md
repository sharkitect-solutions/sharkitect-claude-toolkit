---
name: hq-tech-strategy
description: >
  Use when making technology architecture decisions for Sharkitect operations, evaluating build-vs-buy for platforms/tools,
  assessing security tiering for new integrations, applying the MVA (Minimal Viable Architecture) principle,
  or when the user asks about tech stack decisions, platform selection, or technology risk assessment.
  NEVER use for generic software architecture without Sharkitect business context (use senior-architect skill),
  generic CTO advisory without specific tech decisions (use cto-advisor skill),
  or AI/LLM system design (use ai-systems-architect agent).
version: 0.1.0
---

# HQ Tech Strategy — MVA, Security Tiering & Platform Governance

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/mva-methodology.md` | Evaluating whether to build, buy, or wait on a technology | Already decided on approach, just need implementation |
| `references/security-tiers.md` | Assessing new integrations, APIs, or data flows for security classification | Internal-only changes with no external data exposure |
| `references/tech-stack.md` | Making platform decisions, evaluating alternatives, or auditing current stack | Generic technology questions unrelated to Sharkitect |

## Paired Agents

Launch these agents via Task tool for execution:
- `ai-systems-architect` — AI/LLM architecture decisions, model selection, agent pipeline design
- `backend-architect` — API design, service architecture, scalability decisions
- `devops-engineer` — Infrastructure, CI/CD, deployment architecture
- `mcp-server-architect` — MCP server design and implementation

Use this skill directly for:
- MVA assessments (build vs buy vs wait)
- Security tier classification
- Tech stack governance decisions
- Quick technology risk assessments

## MVA Principle — Minimal Viable Architecture

**Core rule**: Build the smallest defensible system. Document the expansion path. Never build for scale you haven't proven you need.

### MVA Decision Flow
```
TECHNOLOGY DECISION
  |
  +-- Define the OBJECTIVE (what problem are we solving?)
  |
  +-- Map CURRENT STATE (what do we already have?)
  |     |
  |     +-- Can existing tools solve this? --> YES: Use them. STOP.
  |     |
  |     +-- NO: Continue to MVA assessment
  |
  +-- MVA Assessment:
  |     1. What is the SMALLEST system that solves the objective?
  |     2. What is the EXPANSION PATH if demand grows?
  |     3. What is the COST of building now vs. waiting?
  |     4. What is the RISK of not building now?
  |
  +-- Decision:
        BUILD: Cost of waiting > Cost of building, AND risk is material
        BUY:   Existing solution covers 80%+, customization is minor
        WAIT:  Demand is unproven, cost of waiting is low
```

## Security Tiering

| Tier | Classification | Access Pattern | Examples |
|------|---------------|----------------|----------|
| **Tier 0** | Public | Read-only, no auth | Marketing site, public docs |
| **Tier 1** | Internal | Authenticated, team access | Internal tools, dashboards, KPIs |
| **Tier 2** | Confidential | Role-based, audit-logged | Client data, financial records, proposals |
| **Tier 3** | Critical | Encrypted, MFA, immediate escalation | API keys, credentials, payment data, PII |

**Classification Rule**: When uncertain, classify ONE TIER HIGHER. Downgrading is easy; a breach from under-classification is not.

**Tier 3 Escalation**: Any Tier 3 data handling requires explicit user approval before implementation. No exceptions.

## Anti-Patterns

1. **Resume-Driven Architecture**: Choosing a technology because it's interesting or trendy rather than because it solves the problem. Kubernetes for 3 containers. Microservices for a solo-developer company.
2. **Premature Scaling**: Building for 10,000 users when you have 50. The cost of scaling later is almost always less than the cost of building for scale now.
3. **Vendor Lock-In Blindness**: Choosing a platform without evaluating exit cost. Always ask: "What does it cost to leave this platform in 12 months?"
4. **Integration Without Audit**: Adding a new API, MCP server, or third-party service without security tier classification. Every external connection is an attack surface.
5. **Build When Buy Works**: Building custom infrastructure when an off-the-shelf solution covers 80%+ of needs. The remaining 20% rarely justifies the maintenance cost.
