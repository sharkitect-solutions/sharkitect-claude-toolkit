# Phase 5: Gap Analysis

## Context

All 110 skills optimized to B+ or above. Meta-skills at A grade. The AIOS targets "NextGen/NextLevel gold standard for SMBs." Before building new skills or moving to Phase 7 (Sub-Agents), we need to identify what's **missing** from the capability map.

**Goal**: Produce a prioritized gap report — what capabilities an SMB-focused AIOS lacks — with build/buy/skip recommendations for each.

**This phase is analysis only.** Building new skills is a separate follow-on phase.

---

## Current Coverage Map (110 skills across 15 categories)

| Category | Count | Skills |
|---|---|---|
| AI/Agent Development | 10 | agent-development, agent-evaluation, agent-memory-systems, agents-autogpt, agents-crewai, agents-llamaindex, ai-agents-architect, dispatching-parallel-agents, prompt-engineering-guidance, subagent-driven-development |
| n8n Automation | 7 | n8n-code-javascript, n8n-code-python, n8n-expression-syntax, n8n-mcp-tools-expert, n8n-node-configuration, n8n-validation-expert, n8n-workflow-patterns |
| Marketing & Outreach | 10 | cold-email, content-creator, email-sequence, executing-marketing-campaigns, lead-research-assistant, marketing-demand-acquisition, marketing-ideas, marketing-strategy-pmm, outreach-specialist, social-content |
| Business Strategy | 8 | ceo-advisor, cto-advisor, pricing-strategy, product-strategist, professional-communication, data-privacy-compliance, meeting-insights-analyzer, market-research-reports |
| Content & Copy | 5 | copywriting, copy-editing, content-research-writer, email-draft-polish, writing-clearly-and-concisely |
| CRO | 6 | form-cro, page-cro, popup-cro, signup-flow-cro, onboarding-cro, paywall-upgrade-cro |
| Developer Tools | 8 | clean-code, error-resolver, find-bugs, git-commit-helper, senior-architect, senior-backend, systematic-debugging, docker-expert |
| Frontend/Design | 6 | frontend-design, figma, figma-implement-design, theme-factory, canvas-design, ui-ux-pro-max |
| Document Processing | 6 | documentation-templates, docx, pptx, xlsx, pdf-processing-pro, transcribe |
| Email Systems | 3 | email-composer, email-systems, internal-comms |
| SEO & Growth | 5 | seo-optimizer, programmatic-seo, analytics-tracking, competitive-ads-extractor, scroll-experience |
| Product/Project | 5 | product-manager-toolkit, executing-plans, writing-plans, daily-meeting-update, feedback-mastery |
| SaaS & Launch | 5 | micro-saas-launcher, launch-strategy, free-tool-strategy, game-changing-features, interactive-portfolio |
| Comms/Voice/Security | 8 | telegram-bot-builder, twilio-communications, voice-agents, voice-ai-development, security-best-practices, vulnerability-scanner, deslop, marketing-psychology |
| Growth & Misc | 8 | viral-generator-builder, referral-program, ab-test-setup, statistical-analysis, mcp-integration, firecrawl, hook-development, notion-template-business |
| Meta | 2 | ultimate-skill-creator, skill-judge |
| Deferred (installed, not optimized) | 7 | nestjs-expert, nextjs-best-practices, invoice-organizer, supabase-postgres-best-practices, competitor-alternatives, database, file-organizer |

**Also available via plugins** (not custom skills, varying quality):
- python-development (16 skills), llm-application-dev (16), security-scanning (10), data-engineering (8), business-analytics (4), conductor (9), excel-analyst-pro (4), customerio-pack (24), deepgram-pack (24), documenso-pack (24), gamma-pack (24), retellai-pack (28)
- sow-generator, discovery-questionnaire, roi-calculator, make-scenario-builder, zapier-zap-builder

**Connected cloud tools**: Notion, Slack, Gmail, Google Calendar, HubSpot, n8n, Figma, Canva, Jotform, Clay, GitHub

---

## Identified Gaps (by priority)

### CRITICAL — Every SMB needs this

**1. Financial Management / SMB CFO**
- **Gap**: No skill for P&L analysis, cash flow forecasting, budget planning, runway calculation, expense categorization, monthly close process, tax planning basics
- **Partial coverage**: invoice-organizer (document processing only), excel-analyst-pro (investment banking models, not SMB ops)
- **Impact**: Financial decisions are the #1 reason SMBs fail. Every SMB operator needs this daily.
- **Recommendation**: BUILD custom skill

**2. Customer Success / Account Management**
- **Gap**: No skill for post-sale customer lifecycle — health scoring, churn prediction, renewal management, upsell identification, QBR prep, customer segmentation
- **Partial coverage**: lead-research-assistant (pre-sale only), customer-success-manager agent (exists but no skill backing it)
- **Impact**: Retaining customers is 5-7x cheaper than acquiring new ones. Critical for recurring revenue SMBs.
- **Recommendation**: BUILD custom skill

**3. Proposal / SOW / Sales Documents**
- **Gap**: No skill for creating winning proposals, scoping projects, pricing presentation, contract structure, client-facing documents
- **Partial coverage**: sow-generator plugin (basic template), copywriting (general copy, not proposals)
- **Impact**: Proposals are the revenue conversion point. Quality directly impacts close rates.
- **Recommendation**: BUILD custom skill

**4. API Design & Integration Architecture**
- **Gap**: No dedicated skill for REST API conventions, authentication patterns (OAuth, API keys, JWT), rate limiting, versioning, webhook design, error response standards, API documentation
- **Partial coverage**: senior-backend (broad backend, not API-specific), mcp-integration (MCP protocol only)
- **Impact**: An AIOS that connects many services needs expert API knowledge. Every integration depends on this.
- **Recommendation**: BUILD custom skill

**5. Testing Strategy & QA Architecture**
- **Gap**: No proactive testing skill — test pyramid design, what/when/how to test, E2E strategy, test data management, CI test optimization
- **Partial coverage**: find-bugs (reactive), systematic-debugging (reactive), python-development:python-testing-patterns (Python-only plugin)
- **Impact**: Quality assurance is foundational. Without testing expertise, all other skills produce fragile outputs.
- **Recommendation**: BUILD custom skill

### IMPORTANT — Most SMBs need this

**6. HR / People Operations**
- **Gap**: Job descriptions, hiring workflows, interview question design, offer letters, employee onboarding, performance review frameworks, team structure design
- **Partial coverage**: None
- **Impact**: Every growing SMB hires. Bad hires are the most expensive SMB mistake after financial mismanagement.
- **Recommendation**: BUILD custom skill

**7. Client Reporting & Deliverables**
- **Gap**: Progress reports, client dashboards, milestone documentation, retainer reports, ROI summaries for clients
- **Partial coverage**: documentation-templates (internal format), pptx/docx (file creation, not reporting strategy)
- **Impact**: Service-based SMBs live or die by client communication quality.
- **Recommendation**: BUILD custom skill

**8. CI/CD & DevOps Pipelines**
- **Gap**: GitHub Actions workflows, deployment strategies (blue-green, canary), monitoring/alerting setup, infrastructure-as-code, environment management
- **Partial coverage**: docker-expert (containers only), git-commit-helper (commits only)
- **Impact**: Every software-producing SMB needs deployment automation. Manual deploys are the #1 source of outages.
- **Recommendation**: BUILD custom skill

**9. Contract & Legal Drafting**
- **Gap**: Contract templates (MSA, NDA, SLA), terms of service, legal clause library, IP assignment, freelancer agreements
- **Partial coverage**: data-privacy-compliance (privacy only), documenso-pack (e-signatures, not drafting)
- **Impact**: SMBs often skip legal protection until it costs them. Having templates prevents expensive mistakes.
- **Recommendation**: BUILD custom skill

**10. Knowledge Management / Internal Wiki**
- **Gap**: Knowledge base architecture, SOP creation frameworks, runbook design, documentation systems, information retrieval patterns
- **Partial coverage**: documentation-templates (format only), notion-template-business (Notion-specific)
- **Impact**: Knowledge loss from employee turnover is a silent SMB killer. Structured knowledge prevents it.
- **Recommendation**: BUILD custom skill

### NICE-TO-HAVE — Valuable but not urgent

**11. E-commerce Operations** — Product catalog, inventory, fulfillment, marketplace listings
**12. Payment/Billing Integration** — Stripe patterns, subscription management, dunning flows
**13. Accessibility (WCAG)** — Compliance patterns, testing, remediation
**14. Internationalization** — i18n/l10n patterns, locale management
**15. Database Migration** — Schema versioning, zero-downtime migrations (partially covered by supabase skill)

---

## Execution Plan

### Step 1: Validate Gap List (this session)
- Present gap analysis to user
- Get feedback: add/remove/reprioritize gaps
- Confirm scope (how many new skills to target)

### Step 2: Marketplace Search
- Search aitmpl.com for existing skills that fill CRITICAL/IMPORTANT gaps
- Check if any installed plugins adequately cover a gap (reducing need for custom build)
- For each gap: confirm build vs buy vs skip

### Step 3: Produce Gap Report
- Write `.tmp/audit-data/gap-analysis.json` with full categorization
- Write `.tmp/skills-manifest.json` (as required by workflows/skills-evaluation.md)
- Update MEMORY.md with Phase 5 results

### Step 4: Hand Off to Skill Creation Phase
- For each approved BUILD: queue for creation using ultimate-skill-creator
- New skills get the full pipeline: create -> optimize -> score -> B gate

---

## Also Pending: 7 Deferred Skills

These are **installed but not optimized**. Separate from gap analysis (they exist, they just need the standard optimization pass):

| Skill | Domain | Decision Needed |
|---|---|---|
| nestjs-expert | Backend framework | Optimize or skip? |
| nextjs-best-practices | Frontend framework | Optimize or skip? |
| invoice-organizer | Financial ops | Optimize (complements new CFO skill) |
| supabase-postgres-best-practices | Database | Optimize or skip? |
| competitor-alternatives | Sales content | Optimize (feeds SCOUT workspace) |
| database | General DB | Optimize or skip? |
| file-organizer | File management | Optimize or skip? |

**Recommendation**: Optimize all 7 during or after skill creation phase. They're already installed — optimization is cheaper than building from scratch.

---

## Deliverables

1. **Gap analysis JSON** — `.tmp/audit-data/gap-analysis.json`
2. **Skills manifest** — `.tmp/skills-manifest.json`
3. **User-approved build list** — Which gaps to fill with new custom skills
4. **Updated MEMORY.md** — Phase 5 results recorded

## Files to Create/Modify

- `.tmp/audit-data/gap-analysis.json` (NEW)
- `.tmp/skills-manifest.json` (NEW)
- `memory/MEMORY.md` (UPDATE with Phase 5 results)
