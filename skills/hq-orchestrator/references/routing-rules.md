# Routing Rules — Complete Domain-to-Agent Map

## Department Classification

Every incoming task is classified into one or more of these domains. Classification drives routing.

| Domain | Keywords / Signals | Primary Agent(s) | Skill Pairing |
|--------|-------------------|-------------------|---------------|
| **Revenue** | client, proposal, deal, pricing, pipeline, renewal, upsell, churn | `sales-researcher`, `customer-success-manager` | `hq-revenue-ops`, `pricing-strategy` |
| **Finance** | budget, P&L, margin, cash flow, forecast, cost, ROI, unit economics | `financial-analyst` | `smb-cfo` |
| **Technology** | architecture, platform, API, integration, security, infrastructure, stack | `ai-systems-architect`, `backend-architect` | `hq-tech-strategy`, `senior-architect` |
| **Marketing** | campaign, ICP, funnel, content, SEO, social, demand gen, positioning | `marketing-strategist`, `content-strategist` | `marketing-strategy-pmm` |
| **Brand** | voice, tone, messaging, brand guide, visual consistency, communications | `brand-reviewer`, `communication-excellence-coach` | `hq-brand-review` |
| **Operations** | SOP, process, workflow, capacity, delivery, handoff, stage gate | `business-analyst`, `project-manager` | `hq-operations` |
| **Legal** | contract, compliance, liability, IP, GDPR, risk, terms of service | `legal-advisor` | `contract-legal`, `data-privacy-compliance` |
| **Knowledge** | documentation, KB, audit, classification, governance, cross-reference | `knowledge-governance`, `research-synthesizer` | `hq-knowledge-governance` |
| **Strategy** | enterprise architecture, organizational design, structural debt, pivot | `competitive-intelligence-analyst`, `market-research-analyst` | `hq-strategic-ops` |
| **Intelligence** | reverse engineer, competitor analysis, system deconstruction, research | `reverse-engineer`, `search-specialist` | `hq-reverse-engineering` |

## Multi-Domain Detection Rules

A task is multi-domain when ANY of these conditions are true:

1. **Explicit multiple domains**: "Review this proposal for pricing AND brand alignment"
2. **Implicit dependencies**: "Should we accept this deal?" (requires revenue + finance + legal)
3. **Cross-department impact**: "Change our pricing model" (revenue + finance + marketing + operations)
4. **Advisory triggers**: Company direction, irreversible, legal exposure, 2+ department impact

## Sequential vs Parallel Decision

```
Can Agent B start without Agent A's output?
  |
  YES --> Launch in PARALLEL (saves time)
  NO  --> Launch SEQUENTIALLY (Agent A first, feed output to Agent B)
```

Common parallel pairs:
- Brand review + Financial analysis (independent)
- Legal review + Technical assessment (independent)
- Marketing strategy + Operations assessment (independent)

Common sequential chains:
- Sales proposal --> Financial validation --> Legal review
- Technical architecture --> Cost analysis --> Decision
- Brand review --> Content revision --> Final approval

## Escalation Rules

| Condition | Action |
|-----------|--------|
| Any agent returns "INSUFFICIENT DATA" | Ask user for missing context before proceeding |
| Two agents disagree on recommendation | Present both positions, do NOT average or pick one |
| Legal exposure detected | Always include `legal-advisor`, flag for user review |
| Estimated cost > $5,000 | Always include `financial-analyst` |
| Irreversible decision | Require explicit user confirmation before executing |
| Task affects client relationship | Always include `customer-success-manager` for health check |
