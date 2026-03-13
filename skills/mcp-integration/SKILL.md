---
name: mcp-integration
description: "Use when: add MCP server, configure MCP, .mcp.json, Model Context Protocol, connect external service via MCP, mcp__ tool prefix, MCP debugging, MCP server not connecting. NEVER for: Claude Code hooks or event triggers (use hook-development), general REST API development without MCP, webhook endpoint creation, plugin.json structure beyond mcpServers field (use plugin-dev:skill-development)."
version: 2
optimized: true
optimized_date: 2026-03-11
---

# MCP Integration for Claude Code

## File Index

| File | Purpose | When to Load |
|------|---------|--------------|
| `examples/stdio-server.json` | stdio config with 3 server patterns | Need a stdio config template |
| `examples/sse-server.json` | SSE config with OAuth and custom headers | Setting up hosted/cloud MCP server |
| `examples/http-server.json` | HTTP config with Bearer and API key auth | Connecting REST-based MCP endpoint |
| `references/server-types.md` | Deep dive on stdio, SSE, HTTP, WebSocket | Need lifecycle details, migration paths, advanced config |
| `references/authentication.md` | OAuth flows, token patterns, headersHelper, mTLS | Auth setup, token troubleshooting, dynamic headers |
| `references/tool-usage.md` | Tool naming, allowed-tools in commands/agents, call patterns | Writing commands/agents that use MCP tools |

## Scope Boundary

| This Skill Handles | Defer To |
|---|---|
| MCP server configuration (.mcp.json, plugin.json mcpServers) | -- |
| Server type selection (stdio/SSE/HTTP/WS) | -- |
| MCP tool naming and discovery | -- |
| MCP debugging in Claude Code | -- |
| Claude Code hooks and event triggers | hook-development |
| Plugin structure, commands, agents (non-MCP parts) | plugin-dev:skill-development |
| General API client code (fetch, axios, requests) | clean-code or senior-architect |
| Building an MCP server from scratch (SDK, protocol impl) | External: modelcontextprotocol.io docs |

## Server Type Decision Matrix

Answer these questions in order. First match wins.

| Question | If Yes | If No |
|----------|--------|-------|
| Is it an npm package or local script you want to bundle? | **stdio** | Next |
| Does the service offer an official `mcp.*.com/sse` endpoint? | **SSE** | Next |
| Does the service require OAuth (user consent in browser)? | **SSE** | Next |
| Is it a REST API you control with token auth? | **HTTP** | Next |
| Do you need real-time push from server to client? | **WebSocket (ws)** | Next |
| Is it a third-party hosted MCP endpoint with token auth? | **HTTP** | Default to **stdio** (wrap it) |

**Key insight**: stdio is the only type where Claude Code manages the process lifecycle. All others connect to an already-running server. If you want to ship the server inside your plugin, use stdio.

## Configuration Location Decision

MCP server config can live in three places. Precedence matters.

| Location | Scope | When to Use | Precedence |
|----------|-------|-------------|------------|
| Project `.mcp.json` (repo root) | This project only | Project-specific servers (local DB, project API) | Highest -- overrides user settings |
| User settings (`~/.claude/settings.json` mcpServers) | All projects for this user | Personal API keys, global tools | Middle |
| Plugin `.mcp.json` (plugin root) | All users of this plugin | Plugin-bundled servers | Lowest -- plugin defaults |

**Merge behavior**: Same-named server in higher-precedence location completely replaces lower. No partial merge of env vars or args -- it is full replacement.

**Common mistake**: Defining a server in both plugin `.mcp.json` and project `.mcp.json` with different env vars, expecting them to merge. They do not. The project-level config wins entirely.

### .mcp.json vs plugin.json mcpServers

| Use `.mcp.json` (separate file) | Use `plugin.json` mcpServers field |
|---|---|
| Multiple MCP servers in one plugin | Single simple server |
| Servers need different env vars | Minimal configuration |
| Want clear separation from plugin metadata | Want single-file plugin |
| Recommended for most cases | Only for trivial plugins |

Both formats use identical server config objects. The only difference is the container.

## MCP Tool Naming Anatomy

Understanding the naming format is critical for `allowed-tools` in commands and `matcher` patterns in hooks.

```
mcp__plugin_<plugin-name>_<server-name>__<tool-name>
|    |       |             |              |
|    |       |             |              +-- Tool name from the MCP server
|    |       |             +-- Server key from .mcp.json
|    |       +-- Plugin directory name
|    +-- Fixed: indicates plugin-provided MCP
+-- Fixed: MCP namespace prefix
```

**Double underscore (`__`) = namespace separator. Single underscore (`_`) = part of a name.**

Example breakdown:
- Full name: `mcp__plugin_asana_asana__asana_create_task`
- Plugin name: `asana`
- Server name: `asana`
- Tool name: `asana_create_task` (server chose this name, includes its own prefix)

**For user/project MCP servers** (not from plugins), the format differs:
```
mcp__<server-name>__<tool-name>
```
No `plugin_` segment. Example: `mcp__github__get_file_contents`

**Hook matcher implications**: To match all tools from one MCP server in a hook config, use the tool prefix pattern. See `references/tool-usage.md` for `allowed-tools` wildcard syntax.

## Configuration Pitfalls Catalog

| # | Pitfall | Symptom | Fix |
|---|---------|---------|-----|
| 1 | **Windows path expansion** -- `${CLAUDE_PLUGIN_ROOT}` expands with forward slashes but spawned process may use backslashes internally | Args corrupted on Windows | Use forward slashes everywhere; ensure executable handles them |
| 2 | **Spaces in paths** -- `${CLAUDE_PLUGIN_ROOT}` with spaces (e.g., `C:\Users\John Doe\...`) | Command fails to spawn | Claude Code handles quoting for `command`; keep `args` elements as single entries, never split |
| 3 | **Env vars not set at runtime** -- `"API_KEY": "${MY_API_KEY}"` silently expands to empty string | Server starts then fails cryptically | Document required vars; in stdio servers, validate at startup and exit with clear error |
| 4 | **Server name conflicts** -- two plugins both name their server `"api"` | Confusing `/mcp` output (tools won't collide due to plugin namespace) | Use descriptive, unique server names |
| 5 | **stdout pollution (stdio)** -- `print()`, `console.log()`, or library debug output on stdout | Silent MCP protocol failures | All logging to stderr only; Python: set `PYTHONUNBUFFERED=1` + use `sys.stderr` |
| 6 | **No hot-reload** -- editing `.mcp.json` mid-session | Old config still active | Restart Claude Code session; verify with `/mcp` |
| 7 | **npx cache staleness** -- `npx -y @some/mcp-server` runs cached old version | Wrong server version | Use `@latest` suffix or clear npx cache |

## Debugging Procedure: "MCP Server Not Working"

Follow in order. Stop when you find the issue.

| Step | Action | What to Look For |
|------|--------|-----------------|
| 1 | Run `/mcp` | Not listed = config not loaded (check location + JSON syntax). Disconnected/error = connection failed (go to step 2). Connected with 0 tools = server returned nothing (check implementation). Connected with tools = server fine, problem is in tool usage. |
| 2 | Run `claude --debug`, attempt tool use | `MCP server <name> failed to start` = command not found. `MCP connection error` = network/protocol. `MCP auth required` = complete OAuth in browser. `MCP tool call failed` = check parameters. |
| 3 | Test server independently | stdio: run command manually, check for JSON-RPC on stdout. SSE/HTTP: `curl` the URL, verify HTTPS. |
| 4 | Check env vars | For each `${VAR}` in config, verify it is set in the shell where Claude Code launched. Different terminal windows do not share vars. |
| 5 | Check stdout (stdio only) | If server starts but tools fail silently, non-JSON-RPC output on stdout is likely. Run manually and inspect. |

## Authentication Flow Decision

| Scenario | Auth Method | Config Pattern |
|----------|-------------|----------------|
| Official hosted MCP (Asana, GitHub, etc.) | OAuth (automatic) | Just set `type` + `url`. Claude Code handles the rest. |
| Your own hosted server with user accounts | OAuth (if you implement it) or Bearer token | SSE/HTTP with `headers` or headersHelper |
| Internal/private API with static key | Bearer token or API key in headers | HTTP with `"Authorization": "Bearer ${TOKEN}"` |
| Local server bundled in plugin | Env vars passed to process | stdio with `env` block |
| Service with rotating/expiring tokens | headersHelper script | SSE/HTTP with `headersHelper` path |

**OAuth token lifecycle** (non-obvious): First use opens browser for consent. Subsequent uses reuse stored token. On expiry, Claude Code attempts silent refresh; if refresh fails, browser opens again. Users cannot inspect or extract OAuth tokens. To force re-auth: sign out of Claude Code.

**headersHelper**: Escape hatch for auth that does not fit OAuth or static tokens. Runs a script that outputs a JSON headers object. See `references/authentication.md` for details.

## Implementation Checklist

1. Choose server type (use Decision Matrix above)
2. Choose config location (use Configuration Location Decision above)
3. Write config (load the matching example file as template)
4. Set required env vars in your shell
5. Start/restart Claude Code session
6. Run `/mcp` -- verify server appears and shows tools
7. Test a tool call manually
8. Add `allowed-tools` to commands that need MCP tools (see `references/tool-usage.md`)
9. Document required env vars in plugin README

## Rationalization Table

| What Was Removed | Why |
|---|---|
| Server type detailed configs and lifecycle (80+ lines) | Fully covered in `references/server-types.md` + example JSON files |
| Authentication patterns and token management (70+ lines) | Fully covered in `references/authentication.md` |
| Integration patterns with command/agent examples (50+ lines) | Fully covered in `references/tool-usage.md` |
| Security best practices (HTTPS, token storage, scoping) | Generic knowledge Claude already has; specific rules in auth reference |
| Error handling and performance sections (40+ lines) | Generic advice (validate inputs, handle errors, batch requests) |
| Quick reference tables and best practices summary (50+ lines) | Duplicated content from sections above; replaced by decision matrices |

## Red Flags -- Stop and Verify

1. Config has `"command"` AND `"url"` on the same server -- these are mutually exclusive (stdio vs network)
2. Config uses `"type": "stdio"` -- stdio is the default, specifying it is unnecessary but harmless; verify the user did not mean SSE
3. HTTP/WSS URL without `https://` or `wss://` -- always require secure transport
4. `allowed-tools` uses `*` wildcard -- ask if they really need all tools or just specific ones
5. MCP tool name in code does not match the `mcp__plugin_...` or `mcp__...` format -- likely wrong
6. User wants to create an MCP server (protocol implementation) -- this skill covers configuration, not server development
7. `.mcp.json` placed inside a subdirectory instead of plugin root or project root -- it will not be found
8. User sets env vars in `.env` file expecting automatic loading -- Claude Code does not auto-load `.env`; vars must be in shell environment

## NEVER

1. NEVER hardcode secrets in `.mcp.json` -- always use `${ENV_VAR}` expansion
2. NEVER assume env vars are set -- always verify and document required variables
3. NEVER put non-MCP plugin config in `.mcp.json` -- it is exclusively for MCP server definitions
4. NEVER skip the `/mcp` verification step after config changes -- config errors are silent until you check
5. NEVER mix stdout logging with MCP protocol in stdio servers -- all logging to stderr only
