# Failure Documentation Template

Use this template when something fails during project execution. Document immediately -- do not defer.

---

## Entry Format

```markdown
## [YYYY-MM-DD] [Category]: [Short descriptive title]

**Attempted:** [What was tried -- specific command, API call, approach, tool usage]
**Error:** [What happened -- error message, unexpected behavior, symptom]
**Solution:** [What worked instead -- the fix, workaround, or alternative approach]
**Tags:** [comma-separated tags for grep matching]
```

---

## Categories

| Category | When to use | Example |
|----------|------------|---------|
| `api-limitation` | External API doesn't support an operation | Airtable API cannot delete tables |
| `tool-usage` | Claude Code tool or MCP tool used incorrectly | Firecrawl timeout on large pages |
| `approach` | The overall approach was wrong, not a tool issue | Tried to scrape when API was available |
| `configuration` | Settings, env vars, or config were wrong | MCP server URL had trailing slash |
| `dependency` | Missing or incompatible dependency | npm package requires Node 18+ |
| `permissions` | Access denied, auth failure | GitHub PAT missing repo scope |
| `rate-limit` | Throttled by external service | YouTube blocks after 3 transcript requests |
| `timeout` | Operation took too long | Webhook test timed out at 30s default |
| `data-format` | Input/output format mismatch | API returns XML but code expects JSON |
| `platform` | OS-specific issue | Windows path separator in Python script |

---

## Scope Decision

After documenting, decide where the entry goes:

| Question | If YES | If NO |
|----------|--------|-------|
| Would this failure happen in ANY project using this tool/API? | Add to BOTH project AND global `~/.claude/lessons-learned.md` | Project file only |
| Is this a permanent limitation (not a bug that will be fixed)? | Global | Project only |
| Did you find this in the global file from a different project? | Already global -- just reference it | -- |

---

## Examples

### Cross-project entry (goes in BOTH files)

```markdown
## [2026-03-28] api-limitation: Airtable cannot delete tables via API

**Attempted:** DELETE request to /v0/{baseId}/tables/{tableId}
**Error:** 403 Forbidden - "Table deletion is not supported via the API"
**Solution:** Rename tables with "DEPRECATED_" prefix. Add to HUMAN-ACTION-REQUIRED.md for manual deletion via Airtable UI.
**Tags:** airtable, api-limitation, delete, manual-action
```

### Project-specific entry (project file only)

```markdown
## [2026-03-30] configuration: n8n webhook URL requires /webhook/ prefix

**Attempted:** POST to https://instance.app.n8n.cloud/my-workflow
**Error:** 404 Not Found
**Solution:** URL must be https://instance.app.n8n.cloud/webhook/my-workflow (note /webhook/ path segment)
**Tags:** n8n, webhook, url, configuration
```

### Tool usage entry

```markdown
## [2026-03-25] tool-usage: Firecrawl times out on pages over 50KB

**Attempted:** firecrawl scrape https://example.com/large-docs-page
**Error:** Timeout after 30 seconds, no content returned
**Solution:** Use --timeout 120 flag for large pages. Alternative: use WebFetch for simpler pages that don't need JS rendering.
**Tags:** firecrawl, timeout, large-pages, web-scraping
```

---

## How to Check Before Starting Work

At the start of every phase or significant task:

```
1. Identify the tools/APIs you're about to use
2. grep lessons-learned.md for those tool names
3. grep ~/.claude/lessons-learned.md for those tool names
4. If matches found: read the entries and follow the documented solutions
5. If no matches: proceed normally, document any new failures
```