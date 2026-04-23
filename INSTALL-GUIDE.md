# Claude Code Setup Guide

Complete setup guide to restore or replicate this Claude Code environment from scratch.

**Last updated:** 2026-03-31

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

### Tier 1 -- Core (install these first, always)

These are non-negotiable. They make Claude Code fundamentally better.

```
/plugin install superpowers@claude-plugins-official
```

> **IMPORTANT:** Restart your session after installing Superpowers.
> It uses a SessionStart hook that only activates on new sessions.
> This is the [Obra Superpowers](https://github.com/obra/superpowers) plugin -- auto-triggered
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

### Tier 2 -- Highly Recommended

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

### Tier 3 -- Stack & Domain Specific

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

## Step 3: Install Custom Skills

Copy the `skills/` and `core/` folders from this repo into your Claude home:

```bash
# Mac/Linux
cp -r skills/* ~/.claude/skills/
cp -r core/* ~/.claude/skills/

# Windows (Command Prompt)
xcopy /E /I skills "%USERPROFILE%\.claude\skills"
xcopy /E /I core "%USERPROFILE%\.claude\skills"

# Windows (PowerShell)
Copy-Item -Path "skills\*" -Destination "$env:USERPROFILE\.claude\skills" -Recurse -Force
Copy-Item -Path "core\*" -Destination "$env:USERPROFILE\.claude\skills" -Recurse -Force
```

Skills are immediately available in the next Claude Code session.

---

## Step 4: Install Custom Agents

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

## Step 5: Install Custom Plugins

Four custom local plugins provide session lifecycle automation:

```bash
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
```

Then register them in `~/.claude/plugins/installed_plugins.json`. Add these entries to the `plugins` object:

```json
{
  "aios-core@local": [{"version": "1.0.0", "scope": "global", "installPath": "~/.claude/plugins/cache/local/aios-core"}],
  "quality-gate@local": [{"version": "1.0.0", "scope": "global", "installPath": "~/.claude/plugins/cache/local/quality-gate"}],
  "auto-sync@local": [{"version": "1.0.0", "scope": "global", "installPath": "~/.claude/plugins/cache/local/auto-sync"}],
  "phase-gate@local": [{"version": "1.0.0", "scope": "global", "installPath": "~/.claude/plugins/cache/local/phase-gate"}]
}
```

> **Note:** Replace `~` with your actual home directory path (e.g., `C:\Users\YourName` on Windows).

| Plugin | Purpose |
|--------|---------|
| `aios-core` | Session lifecycle: workspace detection, phase awareness, context preservation |
| `quality-gate` | Structural validation for skill/agent files on Write/Edit |
| `auto-sync` | Tracks skill/agent changes, prompts sync before session end |
| `phase-gate` | Phase lifecycle enforcer: plan change detection, artifact tracking, stop gating, pre-compact state preservation |

---

## Step 6: Install Hooks

Copy hook scripts and configure them in settings:

```bash
# Mac/Linux
mkdir -p ~/.claude/hooks
cp hooks/* ~/.claude/hooks/

# Windows (PowerShell)
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\hooks" -Force
Copy-Item -Path "hooks\*" -Destination "$env:USERPROFILE\.claude\hooks" -Recurse -Force
```

Then add the hook configuration to `~/.claude/settings.json`. See `settings-template.json` for the structure. The key entries are:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": "python \"~/.claude/hooks/check-line-count.py\""}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": "python \"~/.claude/hooks/checkpoint-reminder.py\""}]
      }
    ]
  }
}
```

> **Note:** On Windows, use the full path with forward slashes: `"python \"C:/Users/YourName/.claude/hooks/check-line-count.py\""`

---

## Step 7: Install Rules

```bash
# Mac/Linux
mkdir -p ~/.claude/rules
cp rules/* ~/.claude/rules/

# Windows (PowerShell)
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\rules" -Force
Copy-Item -Path "rules\*" -Destination "$env:USERPROFILE\.claude\rules" -Recurse -Force
```

### What the rules do

| Rule | Purpose |
|------|---------|
| `context7.md` | Instructs Claude to use Context7 MCP for library documentation lookups |
| `api-limitations.md` | Protocol for handling API/MCP limitations with manual workarounds |
| `universal-protocols.md` | **Core operating protocols** -- pre-task, post-task, memory, session lifecycle, git backup. Auto-loaded into every session. Workspace CLAUDE.md files extend these with workspace-specific additions only. |

---

## Step 7.5: Install Cross-Workspace Scripts

Cross-workspace tool scripts live under `~/.claude/scripts/` and are callable from any workspace (`python ~/.claude/scripts/close-inbox-item.py ...`, etc.). They are mirrored from the toolkit as of 2026-04-23.

```bash
# Mac/Linux
mkdir -p ~/.claude/scripts
cp scripts/*.py ~/.claude/scripts/

# Windows (PowerShell)
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\scripts" -Force
Copy-Item -Path "scripts\*.py" -Destination "$env:USERPROFILE\.claude\scripts" -Recurse -Force
```

### What the scripts do

| Script | Purpose |
|--------|---------|
| `close-inbox-item.py` | Atomic close for work-request / routed-task / lifecycle inbox items (updates JSON, moves to processed/, updates Supabase) |
| `update-project-status.py` | Update Supabase project + task status from any workspace |
| `work-request.py` | File a new work request to Skill Hub's inbox from any workspace |
| `register-asset.py` | Register hooks / scripts / automations / tables in the Supabase assets registry |
| `load-env.py` | Load credentials from `~/.claude/.env` with workspace prefixes |
| `notify-human-action.py` | Append entry to `HUMAN-ACTION-REQUIRED.md` + send Telegram notification |
| `doc-cache-builder.py` | Build the document lifecycle cache for drift-detection-hook.py |
| `check-orphan-claude-processes.py` / `kill-orphan-claude-processes.py` | Detect and kill stale VS Code / Claude Code processes |

> **Important:** Many scripts read credentials via `load-env.py` from `~/.claude/.env`. Make sure `.env` exists with the right prefixes (SKILLHUB_*, HQ_*, SENTINEL_*) before running scripts that touch Supabase, Telegram, or other external services.

---

## Step 8: MCP Servers

### GitHub MCP (recommended for repo management)

```bash
claude mcp add -s user --transport http github-mcp "https://api.githubcopilot.com/mcp/" -H "Authorization: Bearer YOUR_GITHUB_PAT"
```

> Requires a GitHub Personal Access Token with `repo` scope.
> Create at: github.com -> Settings -> Developer settings -> Personal access tokens

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

### Credential-Based MCPs

Copy `mcp-template.json` from this repo to `~/.claude/mcp.json` and fill in your API keys:

```bash
# Mac/Linux
cp mcp-template.json ~/.claude/mcp.json

# Windows (PowerShell)
Copy-Item -Path "mcp-template.json" -Destination "$env:USERPROFILE\.claude\mcp.json"
```

Then edit `~/.claude/mcp.json` and replace the placeholder values:
- `YOUR_AIRTABLE_API_KEY` -- from Airtable account settings
- `YOUR_N8N_CLOUD_URL` -- your n8n cloud instance URL
- `YOUR_N8N_API_KEY` -- from n8n Settings -> API

### Claude.ai Remote MCPs (configured via web UI)

These are configured at https://claude.ai settings, not locally:
- Canva, Clay, Figma, Gmail, Google Calendar, HubSpot, Jotform, Notion, Slack, Zapier, n8n

---

## Step 9: Install Marketplace Skills (optional)

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
5. Verify hooks: edit a file and confirm check-line-count and checkpoint-reminder fire
6. Verify aios-core: check session start output shows workspace detection

---

## Setting Up a New Workspace

1. Copy `BOOTSTRAP.md` from this repo to your new workspace root
2. Rename to `CLAUDE.md`
3. Open Claude Code in the workspace and say "instantiate"
4. The bootstrap process will:
   - Check prerequisites (Python, Node.js)
   - Create directories and tool files
   - Verify universal protocols rule is installed (flags if missing)
   - Run skills evaluation for the project
   - Populate workspace-specific checklist items based on PROJECT_PURPOSE

> **Note:** Universal protocols (`~/.claude/rules/universal-protocols.md`) must be
> installed first (Step 7 above). The bootstrap process validates this and warns
> if the rule is missing.

---

## What's in This Repo

| Directory/File | Contents | Count |
|----------------|----------|-------|
| `skills/` | Custom Claude Code skills (SKILL.md files) | 139 |
| `agents/` | Global subagent definitions (.md files) | 52 |
| `core/` | Core framework skills | 4 |
| `custom-plugins/` | Custom local plugins | 4 |
| `hooks/` | Hook scripts for settings.json | 2 |
| `rules/` | Global rule files (includes universal-protocols.md) | 3 |
| `scripts/` | Cross-workspace tool scripts (`~/.claude/scripts/` mirror) | -- |
| `BOOTSTRAP.md` | Workspace template -- copy to new workspace root, rename to CLAUDE.md | -- |
| `plugins-manifest.json` | Machine-readable plugin inventory with install commands | 48 plugins |
| `lessons-learned-template.md` | Global lessons-learned template for cross-project learnings | -- |
| `settings-template.json` | Hook configuration template | -- |
| `mcp-template.json` | MCP server configuration template | -- |
| `INSTALL-GUIDE.md` | This file | -- |

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
