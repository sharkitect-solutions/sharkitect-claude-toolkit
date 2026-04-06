# Sharkitect Claude Toolkit

Complete Claude Code environment backup: 139 custom skills, 52 agents, 4 custom plugins, hooks, rules, and full setup automation. Clone this repo to restore or replicate the environment on any machine.

**Last updated:** 2026-03-31

---

## Quick Start (New Machine)

```bash
# 1. Clone the repo
git clone https://github.com/sharkitect-solutions/sharkitect-claude-toolkit.git
cd sharkitect-claude-toolkit

# 2. Copy skills
# Mac/Linux
cp -r skills/* ~/.claude/skills/
cp -r core/* ~/.claude/skills/
# Windows (PowerShell)
Copy-Item -Path "skills\*" -Destination "$env:USERPROFILE\.claude\skills" -Recurse -Force
Copy-Item -Path "core\*" -Destination "$env:USERPROFILE\.claude\skills" -Recurse -Force

# 3. Copy agents
# Mac/Linux
cp -r agents/* ~/.claude/agents/
# Windows (PowerShell)
Copy-Item -Path "agents\*" -Destination "$env:USERPROFILE\.claude\agents" -Recurse -Force

# 4. Copy hooks
# Mac/Linux
mkdir -p ~/.claude/hooks && cp hooks/* ~/.claude/hooks/
# Windows (PowerShell)
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\hooks" -Force
Copy-Item -Path "hooks\*" -Destination "$env:USERPROFILE\.claude\hooks" -Recurse -Force

# 5. Copy rules
# Mac/Linux
mkdir -p ~/.claude/rules && cp rules/* ~/.claude/rules/
# Windows (PowerShell)
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\rules" -Force
Copy-Item -Path "rules\*" -Destination "$env:USERPROFILE\.claude\rules" -Recurse -Force

# 6. Install custom plugins
# Mac/Linux
mkdir -p ~/.claude/plugins/cache/local
cp -r custom-plugins/aios-core ~/.claude/plugins/cache/local/aios-core
cp -r custom-plugins/quality-gate ~/.claude/plugins/cache/local/quality-gate
cp -r custom-plugins/auto-sync ~/.claude/plugins/cache/local/auto-sync
cp -r custom-plugins/phase-gate ~/.claude/plugins/cache/local/phase-gate
# Windows (PowerShell)
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\plugins\cache\local" -Force
Copy-Item -Path "custom-plugins\aios-core" -Destination "$env:USERPROFILE\.claude\plugins\cache\local\aios-core" -Recurse -Force
Copy-Item -Path "custom-plugins\quality-gate" -Destination "$env:USERPROFILE\.claude\plugins\cache\local\quality-gate" -Recurse -Force
Copy-Item -Path "custom-plugins\auto-sync" -Destination "$env:USERPROFILE\.claude\plugins\cache\local\auto-sync" -Recurse -Force
Copy-Item -Path "custom-plugins\phase-gate" -Destination "$env:USERPROFILE\.claude\plugins\cache\local\phase-gate" -Recurse -Force

# 7. Configure hooks in settings.json (merge with existing or copy template)
# See settings-template.json for the hook configuration structure

# 8. Configure MCP servers
# Copy mcp-template.json to ~/.claude/mcp.json and fill in your API keys

# 9. Install marketplace plugins -- see INSTALL-GUIDE.md for full list

# 10. Restart Claude Code session to activate everything
```

For detailed step-by-step instructions including plugin marketplace registration and MCP server setup, see [INSTALL-GUIDE.md](INSTALL-GUIDE.md).

---

## What's in This Repo

| Directory/File | Contents | Count |
|----------------|----------|-------|
| `skills/` | Custom Claude Code skills (SKILL.md + companions) | 139 |
| `agents/` | Global subagent definitions (.md files) | 52 |
| `core/` | Core framework skills | 4 |
| `custom-plugins/` | Custom local plugins (aios-core, quality-gate, auto-sync, phase-gate) | 4 |
| `hooks/` | Hook scripts (line-count guard, checkpoint reminder) | 2 |
| `rules/` | Global rules (context7 MCP enforcement) | 1 |
| `plugins-manifest.json` | Machine-readable plugin inventory with install commands | 47 plugins |
| `settings-template.json` | Hook configuration template for ~/.claude/settings.json | -- |
| `mcp-template.json` | MCP server configuration template (fill in API keys) | -- |
| `INSTALL-GUIDE.md` | Complete setup guide with all install commands | -- |

---

## Core Components

The `core/` directory contains foundational skills that power the toolkit:

| Component | Description |
|-----------|-------------|
| `ultimate-skill-creator` | Unified skill creation: structure + TDD + evaluation |
| `systematic-debugging` | Structured debugging with root cause tracing |
| `writing-plans` | Plan writing discipline for implementation tasks |
| `executing-plans` | Structured plan execution with checkpoints |

---

## Custom Plugins

| Plugin | Hooks | Purpose |
|--------|-------|---------|
| `aios-core` | SessionStart, SessionEnd, PreCompact | Session lifecycle: workspace detection (reads CLAUDE.md PROJECT_PURPOSE), sync reminders, context preservation before compaction |
| `quality-gate` | PostToolUse (Write/Edit) | Structural validation for skill SKILL.md and agent .md files -- lints frontmatter, descriptions, required sections |
| `auto-sync` | PostToolUse (Write/Edit), Stop | Tracks skill/agent changes during session, blocks stop with sync reminder if unsynced changes exist |

---

## Skills (139)

### Development & Architecture
ab-test-setup, accessibility-auditor, agent-development, agent-evaluation, agents-autogpt, agents-crewai, agents-llamaindex, ai-agents-architect, api-patterns, app-builder, canvas-design, clean-code, database, deslop, docker-expert, error-resolver, figma, figma-implement-design, find-bugs, frontend-design, gemini-api-dev, git-commit-helper, github-actions-creator, hook-development, i18n-localization, interactive-portfolio, mcp-integration, nestjs-expert, nextjs-best-practices, programmatic-seo, prompt-engineering-guidance, scroll-experience, security-best-practices, senior-architect, senior-backend, senior-devops, shopify-development, stripe-best-practices, supabase-postgres-best-practices, telegram-bot-builder, testing-strategy, twilio-communications, vulnerability-scanner

### AI & Voice
agent-memory-systems, voice-agents, voice-ai-development

### n8n Automation
n8n-code-javascript, n8n-code-python, n8n-expression-syntax, n8n-mcp-tools-expert, n8n-node-configuration, n8n-validation-expert, n8n-workflow-patterns

### Marketing & Sales
cold-email, competitive-ads-extractor, competitor-alternatives, content-creator, content-research-writer, email-composer, email-draft-polish, email-sequence, email-systems, executing-marketing-campaigns, free-tool-strategy, game-changing-features, launch-strategy, lead-research-assistant, market-research-reports, marketing-demand-acquisition, marketing-ideas, marketing-psychology, marketing-strategy-pmm, micro-saas-launcher, notion-template-business, outreach-specialist, referral-program, sales-enablement, seo-optimizer, social-content, viral-generator-builder

### CRO & Conversion
form-cro, onboarding-cro, page-cro, paywall-upgrade-cro, popup-cro, signup-flow-cro

### Business & Strategy
ceo-advisor, cto-advisor, pricing-strategy, product-manager-toolkit, product-strategist, smb-cfo

### Communication & Content
copy-editing, copywriting, daily-meeting-update, documentation-templates, feedback-mastery, internal-comms, professional-communication, writing-clearly-and-concisely

### Documents & Data
docx, file-organizer, invoice-organizer, pdf-processing-pro, pptx, statistical-analysis, theme-factory, transcribe, xlsx

### HR & Legal
contract-legal, customer-success, data-privacy-compliance, hr-people-ops, knowledge-management, client-reporting

### Skill & Plugin Meta-Tools
agent-judge, context7-mcp, dispatching-parallel-agents, executing-plans, firecrawl, plugin-judge, skill-judge, subagent-driven-development, systematic-debugging, ultimate-agent-creator, ultimate-skill-creator, writing-plans, analytics-tracking, meeting-insights-analyzer

### HQ Operations (Sharkitect-specific)
hq-brand-review, hq-knowledge-governance, hq-operations, hq-orchestrator, hq-revenue-ops, hq-reverse-engineering, hq-strategic-ops, hq-tech-strategy

---

## Agents (52)

ai-systems-architect, analytics-engineer, api-integration-researcher, architect-review, backend-architect, brand-reviewer, business-analyst, code-reviewer, communication-excellence-coach, competitive-intelligence-analyst, content-strategist, context-manager, cro-analyst, customer-success-manager, customer-support, database-architect, debugger, devops-engineer, email-campaign-architect, financial-analyst, frontend-developer, fullstack-developer, knowledge-governance, legal-advisor, market-research-analyst, marketing-attribution-analyst, marketing-strategist, mcp-expert, mcp-server-architect, mobile-developer, multi-agent-coordinator, n8n-mcp-tester, n8n-webhook-tester, n8n-workflow-architect, n8n-workflow-builder, n8n-workflow-debugger, n8n-workflow-explorer, product-manager, project-manager, prompt-engineer, research-synthesizer, reverse-engineer, sales-researcher, scrum-master, search-specialist, seo-analyzer, social-media-clip-creator, social-media-copywriter, supabase-realtime-optimizer, test-engineer, ui-ux-designer

---

## Hooks

| Script | Event | Purpose |
|--------|-------|---------|
| `check-line-count.py` | PreToolUse (Edit/Write) | Blocks edits to MEMORY.md (>=150 lines) and CLAUDE.md (>=250 lines) to prevent file bloat |
| `checkpoint-reminder.py` | PostToolUse (Edit/Write) | After 3+ edits without touching MEMORY.md, reminds agent to checkpoint progress |

---

## Rules

| File | Purpose |
|------|---------|
| `context7.md` | Enforces Context7 MCP usage for library/framework documentation lookups instead of training data |

---

## Updating the Repo

When skills or agents are modified locally:

```bash
# Using sync tools (from Skill Management Hub workspace)
python tools/sync-skills.py --sync --push
python tools/sync-agents.py --sync --push

# Manual single-file update
cp -r ~/.claude/skills/<skill-name> skills/<skill-name>
git add . && git commit -m "Update <skill-name>" && git push
```

---

## Marketplace Plugins (47 total)

A machine-readable manifest with all plugins and install commands is at `plugins-manifest.json`.

**Registered Marketplaces:**

| Name | Repository |
|------|-----------|
| claude-plugins-official | anthropics/claude-plugins-official |
| claude-code | anthropics/claude-code |
| claude-code-workflows | wshobson/agents |
| claude-code-plugins-plus | jeremylongshore/claude-code-plugins |
| agentic-forge | e-stpierre/agentic-forge |

See [INSTALL-GUIDE.md](INSTALL-GUIDE.md) for the complete tiered plugin installation guide.

---

## Source Repositories

| Resource | URL |
|----------|-----|
| claude-plugins-official | https://github.com/anthropics/claude-plugins-official |
| claude-code | https://github.com/anthropics/claude-code |
| claude-code-workflows | https://github.com/wshobson/agents |
| claude-code-plugins-plus | https://github.com/jeremylongshore/claude-code-plugins |
| agentic-forge | https://github.com/e-stpierre/agentic-forge |
| MCP Servers (official) | https://github.com/modelcontextprotocol/servers |
| AI Templates Marketplace | https://www.aitmpl.com |
| Context7 | https://context7.com |
