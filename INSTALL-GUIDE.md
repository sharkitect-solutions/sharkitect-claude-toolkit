# Claude Code Setup Guide

Complete setup guide to restore or replicate this Claude Code environment from scratch.

**Last updated:** 2026-03-09

---

## Prerequisites

1. **Claude Code** installed and authenticated
2. **Python 3.8+** installed and on PATH
3. **Node.js (LTS)** installed (required for marketplace search and npx commands)

---

## Step 1: Register Plugin Marketplaces

Run these inside a Claude Code session:

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace add anthropics/claude-code
/plugin marketplace add wshobson/agents
/plugin marketplace add jeremylongshore/claude-code-plugins
/plugin marketplace add e-stpierre/agentic-forge
```

---

## Step 2: Install Plugins

> A machine-readable manifest of all plugins with install commands
> is available at `plugins-manifest.json` in this repo.

### Tier 1 — Core (install these first, always)

These are non-negotiable. They make Claude Code fundamentally better.

```
/plugin install superpowers@claude-plugins-official
```

> **IMPORTANT:** Restart your session after installing Superpowers.
> It uses a SessionStart hook that only activates on new sessions.
> This is the [Obra Superpowers](https://github.com/obra/superpowers) plugin — auto-triggered
> brainstorming, TDD, systematic debugging, and code review.

Then install the rest of Tier 1:

```
/plugin install github@claude-plugins-official
/plugin install pr-review-toolkit@claude-plugins-official
/plugin install code-simplifier@claude-plugins-official
/plugin install feature-dev@claude-plugins-official
/plugin install security-guidance@claude-plugins-official
/plugin install hookify@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install context7@claude-plugins-official
```

### Tier 2 — Highly Recommended

```
/plugin install plugin-dev@claude-plugins-official
/plugin install skill-creator@claude-plugins-official
/plugin install claude-code-setup@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin install firecrawl@claude-plugins-official
/plugin install ralph-loop@claude-plugins-official
/plugin install playwright@claude-plugins-official
/plugin install conductor@claude-code-workflows
```

### Tier 3 — Stack & Domain Specific

**Language servers (install based on your stack):**
```
/plugin install pyright-lsp@claude-plugins-official
/plugin install typescript-lsp@claude-plugins-official
```

**Integrations:**
```
/plugin install Notion@claude-plugins-official
/plugin install slack@claude-plugins-official
/plugin install sentry@claude-plugins-official
```

**Python development:**
```
/plugin install python-development@claude-code-workflows
```

**Workflow agents (wshobson/agents):**
```
/plugin install data-engineering@claude-code-workflows
/plugin install business-analytics@claude-code-workflows
/plugin install content-marketing@claude-code-workflows
/plugin install llm-application-dev@claude-code-workflows
/plugin install security-scanning@claude-code-workflows
/plugin install seo-content-creation@claude-code-workflows
/plugin install customer-sales-automation@claude-code-workflows
/plugin install data-validation-suite@claude-code-workflows
```

**Business tools (jeremylongshore/claude-code-plugins):**
```
/plugin install sow-generator@claude-code-plugins-plus
/plugin install discovery-questionnaire@claude-code-plugins-plus
/plugin install roi-calculator@claude-code-plugins-plus
/plugin install make-scenario-builder@claude-code-plugins-plus
/plugin install zapier-zap-builder@claude-code-plugins-plus
/plugin install prettier-markdown-hook@claude-code-plugins-plus
/plugin install brand-strategy-framework@claude-code-plugins-plus
/plugin install excel-analyst-pro@claude-code-plugins-plus
```

**API integration packs (jeremylongshore/claude-code-plugins):**
```
/plugin install retellai-pack@claude-code-plugins-plus
/plugin install customerio-pack@claude-code-plugins-plus
/plugin install deepgram-pack@claude-code-plugins-plus
/plugin install documenso-pack@claude-code-plugins-plus
/plugin install gamma-pack@claude-code-plugins-plus
```

---

## Step 3: MCP Servers

### GitHub MCP (recommended for repo management)

```bash
claude mcp add -s user --transport http github-mcp "https://api.githubcopilot.com/mcp/" -H "Authorization: Bearer YOUR_GITHUB_PAT"
```

> Requires a GitHub Personal Access Token with `repo` scope.
> Create at: github.com → Settings → Developer settings → Personal access tokens

### Essential MCPs

```bash
# Persistent knowledge graph memory
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory

# Live documentation lookup for any library
claude mcp add --transport http context7 https://mcp.context7.com/mcp
```

### Cloud Service MCPs

```bash
# Supabase (database/auth management)
claude mcp add --transport http supabase https://mcp.supabase.com/mcp

# Vercel (deployment management)
claude mcp add --transport http vercel https://mcp.vercel.com

# Cloudinary (asset/media management)
claude mcp add --transport http cloudinary https://asset-management.mcp.cloudinary.com/sse

# Make.com (automation platform)
claude mcp add --transport http make https://mcp.make.com
```

### Credential-Based MCPs (require API keys)

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "notionApi": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_TOKEN": "YOUR_NOTION_TOKEN"
      }
    },
    "airtable": {
      "command": "airtable-mcp-server",
      "args": [],
      "env": {
        "AIRTABLE_API_KEY": "YOUR_AIRTABLE_API_KEY"
      }
    },
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "YOUR_N8N_URL",
        "N8N_API_KEY": "YOUR_N8N_API_KEY"
      }
    }
  }
}
```

### Claude.ai Remote MCPs (configured via web UI)

These are configured at https://claude.ai settings, not locally:
- Canva, Clay, Figma, Gmail, Google Calendar, HubSpot, Jotform, Notion, Slack, Zapier, n8n

---

## Step 4: Install Custom Skills

Copy the `skills/` folder from this repo into your Claude home:

```bash
# Mac/Linux
cp -r skills/* ~/.claude/skills/

# Windows (Command Prompt)
xcopy /E /I skills "%USERPROFILE%\.claude\skills"

# Windows (PowerShell)
Copy-Item -Path "skills\*" -Destination "$env:USERPROFILE\.claude\skills" -Recurse -Force
```

Skills are immediately available in the next Claude Code session.

---

## Step 5: Install Custom Agents

Copy the `agents/` folder from this repo into your Claude home:

```bash
# Mac/Linux
cp -r agents/* ~/.claude/agents/

# Windows (Command Prompt)
xcopy /E /I agents "%USERPROFILE%\.claude\agents"

# Windows (PowerShell)
Copy-Item -Path "agents\*" -Destination "$env:USERPROFILE\.claude\agents" -Recurse -Force
```

Agents are available immediately for the Task tool in your next session.

---

## Step 6: Install Marketplace Skills (optional)

Browse available community skills at https://www.aitmpl.com/skills

Install with:
```bash
npx claude-code-templates@latest --skills <name> --yes
npx claude-code-templates@latest --agents <name> --yes
```

---

## Verification

After setup, start a new Claude Code session and verify:

1. Superpowers auto-triggers brainstorming when you describe a task
2. Run `/help` to see available skills listed
3. Check MCP tools are discoverable (Claude will show them as deferred tools)
4. Test GitHub MCP: ask Claude to read a file from your repo

---

## What's in This Repo

| Directory/File | Contents | Count |
|----------------|----------|-------|
| `skills/` | Custom Claude Code skills (SKILL.md files) | 110 |
| `agents/` | Global subagent definitions (.md files) | 38 |
| `core/` | Core framework files | — |
| `plugins-manifest.json` | Machine-readable plugin inventory with install commands | 44 plugins |
| `INSTALL-GUIDE.md` | This file | — |

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
