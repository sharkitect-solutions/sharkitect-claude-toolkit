# Default Resource Mappings

Fallback mappings when a workspace CLAUDE.md lacks ACTIVE_SKILLS or when the task category isn't covered by installed skills. The resource-auditor reads these defaults to identify potential UNUSED or MISSING gaps.

## How to Use This File

1. Classify the completed task into a work category (see SKILL.md Step 2)
2. Find the category below
3. Check: does the workspace have ANY of the listed resource types installed?
4. If yes but unused: potential UNUSED gap
5. If none installed: potential MISSING gap
6. If generic substitute used: potential FALLBACK gap

## Category-to-Resource Mappings

### content
**Tasks:** Writing, editing, creating client-facing text (landing pages, emails, proposals, social, blog)

| Resource Type | Examples | Why Needed |
|---|---|---|
| Brand voice skill | hq-brand-review, brand-voice-* | Client-facing text must match brand identity |
| Copywriting skill | copywriting, writing-clearly-and-concisely | Persuasion, clarity, structure |
| CRO skill | page-cro, form-cro, signup-flow-cro, popup-cro | Conversion optimization for web content |
| SEO skill | seo-optimizer, seo-content-* | Search visibility for public content |
| Content enforcer | hq-content-enforcer | Orchestration ensuring all content skills fire |
| Brand docs | brand-identity-guide.md, style-guide.md | Voice, tone, terminology reference |

**Common fallback:** Using `copywriting` alone without brand voice or CRO.

### technical-content
**Tasks:** API docs, technical guides, developer documentation, README files

| Resource Type | Examples | Why Needed |
|---|---|---|
| Technical writing skill | technical-documentation, api-docs | Endpoint tables, code examples, auth flows |
| Code reference | Language-specific SDK docs | Accurate code samples |
| Documentation templates | doc-templates, readme-template | Consistent structure |

**Common fallback:** Using `copywriting` or `writing-clearly-and-concisely` for technical content.

### code
**Tasks:** Building features, fixing bugs, refactoring, code reviews

| Resource Type | Examples | Why Needed |
|---|---|---|
| Language/framework skills | react-*, python-*, django-*, fastapi-* | Framework-specific patterns |
| Testing skills | test-driven-development, testing-* | Test coverage and quality |
| Code review agents | code-reviewer, architect-reviewer | Quality verification |
| Security skills | security-*, data-validation-* | Vulnerability prevention |

**Common fallback:** General coding without framework-specific skill guidance.

### automation
**Tasks:** Workflows, integrations, n8n scenarios, Make scenarios, Zapier zaps

| Resource Type | Examples | Why Needed |
|---|---|---|
| Workflow builder | n8n-workflow-*, make-scenario-builder | Platform-specific patterns |
| API integration | api-integration-researcher | External API setup guides |
| MCP tools | n8n-mcp, make-mcp | Direct platform interaction |

**Common fallback:** Building automations from scratch without platform-specific templates.

### analysis
**Tasks:** Research, competitive intel, market analysis, business intelligence

| Resource Type | Examples | Why Needed |
|---|---|---|
| Research skills | search-specialist, competitive-intelligence-analyst | Structured research methodology |
| Analysis agents | business-analyst, market-research-analyst | Framework-driven analysis |
| Data skills | data-engineer, business-analytics | Data processing and visualization |

**Common fallback:** Ad-hoc research without structured framework.

### design
**Tasks:** UI/UX, wireframes, design systems, visual design decisions

| Resource Type | Examples | Why Needed |
|---|---|---|
| Design review | ui-ux-designer agent | Research-backed design feedback |
| Frontend skills | frontend-developer, frontend-design | Implementation patterns |
| CRO skills | page-cro, form-cro | Conversion-aware design |

**Common fallback:** Design decisions based on general knowledge without usability research.

### strategy
**Tasks:** Planning, roadmaps, architecture decisions, business strategy

| Resource Type | Examples | Why Needed |
|---|---|---|
| Architecture agents | backend-architect, ai-systems-architect | Structured design decisions |
| Strategy skills | marketing-strategist, content-strategist | Domain-specific strategy frameworks |
| Planning skills | project-lifecycle, project-manager | Phase gates and milestone tracking |

**Common fallback:** Strategy without structured decision frameworks.

### operations
**Tasks:** Deployment, monitoring, infrastructure, CI/CD

| Resource Type | Examples | Why Needed |
|---|---|---|
| DevOps skills | devops-engineer, docker-expert | Infrastructure patterns |
| Security skills | security-auditor, security-scanning | Secure deployment |
| Monitoring tools | Sentinel tools, health-check scripts | Observability |

**Common fallback:** Manual deployment without infrastructure-as-code patterns.

### data
**Tasks:** Database design, migrations, data pipelines, ETL

| Resource Type | Examples | Why Needed |
|---|---|---|
| Database skills | database-architect, supabase-* | Schema design, optimization |
| Data pipeline | data-engineer, data-engineering | ETL patterns |
| Vector DB | vector-database-engineer | Embedding and search optimization |

**Common fallback:** Schema design without database-specific optimization patterns.

## Interpreting Missing Mappings

If a workspace's task doesn't fit any category above:
1. This itself is worth noting as an info-level observation in the audit
2. Check if the task is niche enough to warrant a new category
3. If the task required domain expertise not covered by any installed resource, that's a MISSING gap