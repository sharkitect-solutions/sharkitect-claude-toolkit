# Global Lessons Learned

Cross-project patterns, API limitations, and tool quirks. Checked by AI at phase start to avoid repeating known failures.

**Usage:** At the start of every phase, grep this file for keywords related to the tools/APIs you are about to use. If there is a match, follow the documented solution instead of repeating the failed approach.

---

## API Limitations

### [2026-03-28] api-limitation: Airtable cannot delete tables via API

**Attempted:** DELETE request to /v0/{baseId}/tables/{tableId}
**Error:** 403 Forbidden - "Table deletion is not supported via the API"
**Solution:** Rename tables with "DEPRECATED_" prefix. Add to HUMAN-ACTION-REQUIRED.md for manual deletion via Airtable UI.
**Tags:** airtable, api-limitation, delete, manual-action

---

## Tool Usage

### [2026-03-25] tool-usage: YouTube transcript extraction unreliable via scraping

**Attempted:** Fetching YouTube transcript via web scrape / Firecrawl
**Error:** Rate limited / blocked after 2-3 requests
**Solution:** Use Context7 MCP for library docs. For video transcripts, ask user to paste transcript or use a dedicated transcript API.
**Tags:** youtube, scraping, rate-limit, workaround

### [2026-03-30] tool-usage: Firecrawl times out on pages over 50KB

**Attempted:** Scraping 50KB+ pages with default timeout
**Error:** Timeout after 30 seconds, no content returned
**Solution:** Use --timeout 120 flag for large pages. Alternative: use WebFetch for simpler pages that don't need JS rendering.
**Tags:** firecrawl, timeout, large-pages, web-scraping

---

## Platform

### [2026-03-15] platform: Windows cp1252 encoding breaks Python print output

**Attempted:** Printing Unicode characters (em dash, smart quotes) in Python scripts
**Error:** UnicodeEncodeError on Windows when stdout uses cp1252 encoding
**Solution:** Use ASCII-only characters in all Python print output. Replace em dash with --, smart quotes with straight quotes.
**Tags:** windows, encoding, python, cp1252, ascii

---

## Approach

### [2026-03-20] approach: davila7 marketplace installs to project, not global

**Attempted:** Installing skills via `npx claude-code-templates@latest --skills <name> --yes`
**Error:** Skills installed to project `.claude/skills/` instead of global `~/.claude/skills/`
**Solution:** After installing, manually copy from project `.claude/skills/` to `~/.claude/skills/`. Alternative: use `sickn33/antigravity-awesome-skills` which supports `--global` flag.
**Tags:** marketplace, davila7, install-location, global, skills