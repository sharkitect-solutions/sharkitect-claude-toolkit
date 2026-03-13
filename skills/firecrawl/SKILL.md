---
name: firecrawl
description: "Use when scraping web pages, searching the web via Firecrawl CLI, crawling sites for bulk content extraction, or automating browser interactions for content behind pagination or logins. Also use when the user mentions firecrawl, web scraping to markdown, or site mapping. NEVER use for API-based data fetching (use direct HTTP), non-web content extraction, or when the user has not installed Firecrawl."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Firecrawl CLI

Web scraping, search, and browser automation CLI. Returns clean markdown optimized for LLM context windows.

## File Index

| File | Purpose | Load When |
| ---- | ------- | --------- |
| rules/install.md | Installation and authentication setup | Firecrawl not installed or auth fails |
| rules/security.md | Output handling and data guidelines | Storing or sharing scraped content |

## Prerequisites

Check status before use:

```bash
firecrawl --status
# Shows: version, auth status, concurrency limit, remaining credits
```

If not ready, see rules/install.md. Run `firecrawl --help` or `firecrawl <command> --help` for full option details.

## Command Escalation Workflow

Follow this escalation pattern -- start at the lowest step that fits:

1. **Search** -- No specific URL yet. Find pages, answer questions, discover sources.
2. **Scrape** -- Have a URL. Extract its content directly.
3. **Map + Scrape** -- Large site or need a specific subpage. Use `map --search` to find the right URL, then scrape it.
4. **Crawl** -- Need bulk content from an entire site section (e.g., all /docs/).
5. **Browser** -- Scrape failed because content is behind interaction (pagination, modals, form submissions, multi-step navigation).

| Need | Command | When |
| ---- | ------- | ---- |
| Find pages on a topic | `search` | No specific URL yet |
| Get a page's content | `scrape` | Have a URL, page is static or JS-rendered |
| Find URLs within a site | `map` | Need to locate a specific subpage |
| Bulk extract a site section | `crawl` | Need many pages (e.g., all /docs/) |
| AI-powered data extraction | `agent` | Need structured data from complex sites |
| Interact with a page | `browser` | Content requires clicks, form fills, pagination, or login |
| Save entire site to files | `download` | Combines map + scrape for bulk local saves |

**Example: fetching API docs from a large site**

```
search "site:docs.example.com authentication API"  ->  found the docs domain
map https://docs.example.com --search "auth"        ->  found /docs/api/authentication
scrape https://docs.example.com/docs/api/auth...    ->  got the content
```

**Example: data behind pagination**

```
scrape https://example.com/products                 ->  only shows first 10 items, no next-page links
browser "open https://example.com/products"         ->  open in browser
browser "snapshot"                                  ->  find the pagination button
browser "click @e12"                                ->  click "Next Page"
browser "scrape" -o .firecrawl/products-p2.md       ->  extract page 2 content
```

## Command Quick Reference

### search

```bash
firecrawl search "your query" -o .firecrawl/result.json --json
firecrawl search "your query" --scrape -o .firecrawl/scraped.json --json
firecrawl search "your query" --sources news --tbs qdr:d -o .firecrawl/news.json --json
```

Options: `--limit <n>`, `--sources <web,images,news>`, `--categories <github,research,pdf>`, `--tbs <qdr:h|d|w|m|y>`, `--location`, `--country <code>`, `--scrape`, `--scrape-formats`, `-o`

### scrape

Multiple URLs are scraped concurrently; each result is saved to `.firecrawl/`.

```bash
firecrawl scrape "<url>" -o .firecrawl/page.md
firecrawl scrape "<url>" --only-main-content -o .firecrawl/page.md
firecrawl scrape "<url>" --wait-for 3000 -o .firecrawl/page.md
firecrawl scrape "<url>" --format markdown,links -o .firecrawl/page.json
firecrawl scrape https://site.com/a https://site.com/b https://site.com/c
```

Options: `-f <markdown,html,rawHtml,links,screenshot,json>`, `-H`, `--only-main-content`, `--wait-for <ms>`, `--include-tags`, `--exclude-tags`, `-o`

### map

```bash
firecrawl map "<url>" --search "authentication" -o .firecrawl/filtered.txt
firecrawl map "<url>" --limit 500 --json -o .firecrawl/urls.json
```

Options: `--limit <n>`, `--search <query>`, `--sitemap <include|skip|only>`, `--include-subdomains`, `--json`, `-o`

### crawl

```bash
firecrawl crawl "<url>" --include-paths /docs --limit 50 --wait -o .firecrawl/crawl.json
firecrawl crawl "<url>" --max-depth 3 --wait --progress -o .firecrawl/crawl.json
firecrawl crawl <job-id>    # check status of a running crawl
```

Options: `--wait`, `--progress`, `--limit <n>`, `--max-depth <n>`, `--include-paths`, `--exclude-paths`, `--delay <ms>`, `--max-concurrency <n>`, `--pretty`, `-o`

### agent

AI-powered autonomous extraction (2-5 minutes).

```bash
firecrawl agent "extract all pricing tiers" --wait -o .firecrawl/pricing.json
firecrawl agent "extract products" --schema '{"type":"object","properties":{"name":{"type":"string"}}}' --wait -o .firecrawl/products.json
firecrawl agent "get feature list" --urls "<url>" --wait -o .firecrawl/features.json
```

Options: `--urls`, `--model <spark-1-mini|spark-1-pro>`, `--schema <json>`, `--schema-file`, `--max-credits <n>`, `--wait`, `--pretty`, `-o`

### browser

Cloud Chromium sessions in Firecrawl's remote sandboxed environment. Shorthand auto-launches a session.

```bash
firecrawl browser "open <url>"
firecrawl browser "snapshot"                    # accessibility tree with @ref IDs
firecrawl browser "click @e5"
firecrawl browser "fill @e3 'search query'"
firecrawl browser "scrape" -o .firecrawl/page.md
firecrawl browser close
```

| Command | Description |
| ------- | ----------- |
| `open <url>` | Navigate to a URL |
| `snapshot` | Get accessibility tree with @ref IDs |
| `screenshot` | Capture a PNG screenshot |
| `click <@ref>` | Click an element by ref |
| `type <@ref> <text>` | Type into an element |
| `fill <@ref> <text>` | Fill a form field (clears first) |
| `scrape` | Extract page content as markdown |
| `scroll <direction>` | Scroll up/down/left/right |
| `wait <seconds>` | Wait for a duration |
| `eval <js>` | Evaluate JavaScript on the page |

Session management: `launch-session --ttl 600`, `list`, `close`
Options: `--ttl <seconds>`, `--ttl-inactivity <seconds>`, `--session <id>`, `-o`

### download

Combines map + scrape to save a site as local files. Always pass `-y` to skip confirmation.

```bash
firecrawl download https://docs.example.com -y
firecrawl download https://docs.example.com --include-paths "/features,/sdks" --only-main-content --screenshot -y
firecrawl download https://docs.example.com --exclude-paths "/zh,/ja,/fr" --limit 50 -y
```

Options: `--limit <n>`, `--search <query>`, `--include-paths`, `--exclude-paths`, `--allow-subdomains`, `-y`, plus all scrape options.

### credit-usage

```bash
firecrawl credit-usage
firecrawl credit-usage --json --pretty -o .firecrawl/credits.json
```

## Output Conventions

Write results to `.firecrawl/` with `-o`. Add `.firecrawl/` to `.gitignore`. Always quote URLs -- shell interprets `?` and `&` as special characters.

Naming conventions:
```
.firecrawl/search-{query}.json
.firecrawl/search-{query}-scraped.json
.firecrawl/{site}-{path}.md
```

Single format outputs raw content. Multiple formats (e.g., `--format markdown,links`) output JSON.

Never read entire output files at once:
```bash
wc -l .firecrawl/file.md && head -50 .firecrawl/file.md
grep -n "keyword" .firecrawl/file.md
jq -r '.data.web[].url' .firecrawl/search.json
```

Check `.firecrawl/` for existing data before fetching again. `search --scrape` already includes full page content -- do not re-scrape those URLs.

**Parallelization:** Check concurrency limit via `firecrawl --status`. Run independent scrapes in parallel:
```bash
firecrawl scrape "<url-1>" -o .firecrawl/1.md &
firecrawl scrape "<url-2>" -o .firecrawl/2.md &
wait
```

For browser, launch separate sessions per independent task via `--session <id>`.

## Scrape vs Browser Decision

- Use `scrape` first. It handles static pages and JS-rendered SPAs.
- Use `browser` only when scrape fails because content is behind interaction: pagination buttons, modals, dropdowns, multi-step navigation, or infinite scroll.
- Never use `browser` for web searches -- use `search` instead.
- Use `agent` for structured data extraction from complex multi-page sites where format matters.

## Rationalization Table

| Scenario | Decision | Reason |
| -------- | -------- | ------ |
| Need content from a known URL | scrape | Fastest, cheapest, handles static + JS-rendered pages |
| URL unknown, topic known | search | Finds and ranks relevant pages before committing credits |
| Need one specific subpage from large site | map --search then scrape | Map filters to relevant URLs; avoids crawling entire site |
| Need all pages in /docs section | crawl with --include-paths | Bulk extraction in a single job; more efficient than repeated scrapes |
| Page has "Load More" or paginated JS | browser | Only escalate here when scrape returns incomplete content |
| Need structured data across multiple pages | agent | AI handles navigation and schema extraction autonomously |

## Red Flags

- Attempting `browser` without first trying `scrape` -- try scrape first, it handles most JS pages.
- Re-scraping URLs already fetched by `search --scrape` -- check the output file first.
- Reading entire large output files into context -- always use `head`, `grep`, or `jq` to extract what you need.
- Crawling an entire domain when only one section is needed -- use `--include-paths` or `map --search` first.
- Missing quotes around URLs containing `?` or `&` -- shell will misinterpret query parameters.
- Using `agent` for simple single-page extraction -- overkill; use `scrape` instead.
- Running unlimited parallel browser sessions -- check concurrency limit first with `firecrawl --status`.
- Storing output files outside `.firecrawl/` -- breaks naming conventions and gitignore coverage.

## NEVER

- Never use `browser` as a substitute for `search` -- browser has no search capability.
- Never skip `firecrawl --status` when credits or concurrency limits may be a concern.
- Never read large output files in full -- always pipe through `head`, `grep`, or `jq`.
- Never omit `-y` on `download` commands in automated/scripted contexts -- will hang waiting for input.
- Never store API keys or scraped PII outside `.env` and `.firecrawl/` -- see rules/security.md.
