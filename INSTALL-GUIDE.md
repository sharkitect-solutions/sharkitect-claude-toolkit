# Claude Code Setup Guide

Complete setup guide to restore or replicate this Claude Code environment from scratch.

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
/plugin marketplace add anthropics/claude-code-plugins
/plugin marketplace add wshobson/agents
/plugin marketplace add e-stpierre/agentic-forge
```

---

## Step 2: Install Plugins

### Tier 1 — Non-Negotiable (install these first, always)

These make Claude Code fundamentally better at writing disciplined, quality code.

```
/plugin install superpowers@claude-plugins-official
```

> **Note:** This is the [Obra Superpowers](https://github.com/obra/superpowers) plugin by Jesse Vincent,
> distributed through Anthropic's official marketplace. It provides auto-triggered workflows for
> brainstorming, TDD, systematic debugging, and code review.
>
> **IMPORTANT:** Restart your session after installing superpowers.
> It uses a SessionStart hook that only activates on new sessions.

Then install the rest:

```
/plugin install github@claude-plugins-official
/plugin install commit-commands@claude-code-plugins
/plugin install code-simplifier@claude-plugins-official
/plugin install pr-review-toolkit@claude-plugins-official
/plugin install feature-dev@claude-plugins-official
/plugin install security-guidance@claude-plugins-official
/plugin install hookify@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
```

### Tier 2 — Highly Recommended

```
/plugin install plugin-dev@claude-plugins-official
/plugin install firecrawl@claude-plugins-official
/plugin install conductor@claude-code-workflows
/plugin install frontend-design@claude-plugins-official
/plugin install skill-creator@claude-plugins-official
/plugin install claude-code-setup@claude-plugins-official
```

### Tier 3 — Stack-Dependent (install based on your needs)

**Python development:**
```
/plugin install pyright-lsp@claude-plugins-official
/plugin install python-development@claude-code-workflows
```

**Integrations:**
```
/plugin install Notion@claude-plugins-official
/plugin install slack@claude-plugins-official
/plugin install sentry@claude-plugins-official
```

**Workflow agents (from wshobson/agents):**
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

**Business tools (from claude-code-plugins-plus):**
```
/plugin marketplace add <org/repo-for-claude-code-plugins-plus>
/plugin install sow-generator@claude-code-plugins-plus
/plugin install discovery-questionnaire@claude-code-plugins-plus
/plugin install roi-calculator@claude-code-plugins-plus
/plugin install make-scenario-builder@claude-code-plugins-plus
/plugin install zapier-zap-builder@claude-code-plugins-plus
/plugin install brand-strategy-framework@claude-code-plugins-plus
/plugin install retellai-pack@claude-code-plugins-plus
```

---

## Step 3: MCP Servers

### Essential MCP (add these always)

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

# Clarify (AI media understanding)
claude mcp add --transport http clarify https://api.clarify.ai/mcp

# Make.com (automation platform)
claude mcp add --transport http make https://mcp.make.com
```

### Credential-Based MCPs (require API keys)

These need API keys set in environment variables. Add to `~/.mcp.json` or `~/.claude/mcp.json`:

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

### Claude.ai Remote MCP (configured via web UI)

These are configured at https://claude.ai settings, not locally:
- Canva, Clay, Figma, Gmail, Google Calendar, HubSpot, Jotform, Notion, Slack, Zapier, n8n

---

## Step 4: Install Custom Skills

Copy the `skills/` folder from this repo into your Claude home:

```bash
# Copy all skills
cp -r skills/* ~/.claude/skills/

# Or on Windows:
# xcopy /E /I skills "%USERPROFILE%\.claude\skills"
```

Skills are immediately available in the next Claude Code session. No restart required.

---

## Step 5: Install Skills from AI Templates Marketplace

Browse available skills at https://www.aitmpl.com/skills

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

---

## Source Repositories

| Resource | URL |
|----------|-----|
| claude-plugins-official | https://github.com/anthropics/claude-plugins-official |
| claude-code-plugins | https://github.com/anthropics/claude-code-plugins |
| wshobson/agents | https://github.com/wshobson/agents |
| MCP Servers (official) | https://github.com/modelcontextprotocol/servers |
| AI Templates Marketplace | https://www.aitmpl.com |
| Context7 | https://context7.com |
