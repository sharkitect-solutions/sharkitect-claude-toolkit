# Department Taxonomy — Sharkitect Digital Workforce

## Organizational Structure

Sharkitect Digital operates as an AI-powered digital services company. The "workforce" is a single Claude Code agent with specialized skills and sub-agents, NOT separate humans or separate AI instances. This taxonomy defines the logical departments for routing purposes.

## Departments

### Revenue Department
**Covers:** Sales pipeline, client relationships, pricing, renewals, expansion
**Primary skill:** `hq-revenue-ops` (Felix)
**Primary agents:** `sales-researcher`, `customer-success-manager`, `financial-analyst`
**Activation signals:** "client," "proposal," "pricing," "deal," "pipeline," "renewal," "churn," "revenue"

### Technology Department
**Covers:** Architecture, platforms, AI tools, integrations, security, infrastructure
**Primary skill:** `hq-tech-strategy` (Orion)
**Primary agents:** `ai-systems-architect`, `backend-architect`, `devops-engineer`, `mcp-server-architect`
**Activation signals:** "architecture," "platform," "API," "integration," "security," "tech stack," "infrastructure"

### Marketing Department
**Covers:** Campaigns, content, lead generation, positioning, brand awareness
**Primary skill:** `marketing-strategy-pmm` (Cleo)
**Primary agents:** `marketing-strategist`, `content-strategist`, `seo-analyzer`
**Activation signals:** "campaign," "content," "SEO," "funnel," "ICP," "positioning," "demand gen"

### Brand Department
**Covers:** Voice consistency, visual standards, communications, drift detection
**Primary skill:** `hq-brand-review` (Vera)
**Primary agents:** `brand-reviewer`, `communication-excellence-coach`
**Activation signals:** "brand," "voice," "tone," "messaging," "visual," "communications," "brand review"

### Operations Department
**Covers:** SOPs, processes, delivery workflows, capacity management
**Primary skill:** `hq-operations` (Atlas)
**Primary agents:** `business-analyst`, `project-manager`, `scrum-master`
**Activation signals:** "SOP," "process," "workflow," "capacity," "delivery," "handoff," "operations"

### Finance Department
**Covers:** Budgets, P&L, forecasting, unit economics, deal validation
**Primary skill:** `smb-cfo` (Sterling)
**Primary agents:** `financial-analyst`
**Activation signals:** "budget," "P&L," "margin," "cash flow," "forecast," "cost," "ROI"

### Legal Department
**Covers:** Contracts, compliance, risk assessment, IP protection
**Primary skill:** `contract-legal` (Lex)
**Primary agents:** `legal-advisor`
**Activation signals:** "contract," "compliance," "liability," "IP," "GDPR," "risk," "legal"

### Knowledge Department
**Covers:** Documentation, KB governance, audits, classification
**Primary skill:** `hq-knowledge-governance` (Sage)
**Primary agents:** `knowledge-governance`, `research-synthesizer`
**Activation signals:** "documentation," "KB," "audit," "classification," "governance," "knowledge"

### Strategy Department
**Covers:** Enterprise architecture, organizational design, structural diagnosis
**Primary skill:** `hq-strategic-ops` (Axiom)
**Primary agents:** `competitive-intelligence-analyst`, `market-research-analyst`
**Activation signals:** "enterprise," "structural," "strategic," "organizational," "debt," "architecture" (org context)

### Intelligence Department
**Covers:** Reverse engineering, competitive intelligence, system deconstruction
**Primary skill:** `hq-reverse-engineering` (Echo)
**Primary agents:** `reverse-engineer`, `search-specialist`
**Activation signals:** "reverse engineer," "how did they build," "competitor analysis," "deconstruct," "intelligence"

## Disambiguation Rules

When a task could belong to multiple departments:

1. **"Architecture"** — If about software/systems → Technology. If about organizational structure → Strategy.
2. **"Strategy"** — If about marketing positioning → Marketing. If about enterprise structure → Strategy. If about pricing → Revenue + Finance.
3. **"Review"** — If about code → Technology. If about brand/communications → Brand. If about legal documents → Legal.
4. **"Audit"** — If about knowledge/docs → Knowledge. If about financial → Finance. If about security → Technology. If about processes → Operations.
5. **"Client"** — If about relationship/health → Revenue. If about delivery → Operations. If about contract → Legal.
