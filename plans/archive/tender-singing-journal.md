# Google Workspace CLI (`gws`) Integration — Alex Telegram Bot

## Context

Chris discovered the `gws` CLI tool (Google Workspace CLI) and forked it to `sharkitect-solutions/Google-CLI`. This tool provides **unified access to the entire Google Workspace API surface** — Drive, Gmail, Calendar, Sheets, Docs, Admin, Chat, and every other Workspace API — through a single CLI that reads Google's Discovery Service at runtime. When Google adds an API endpoint, `gws` picks it up automatically.

**Why this matters:** Alex's Telegram bot currently has 3 separate Google tools with limited capabilities:
- **Gmail**: IMAP/SMTP with App Passwords — can read/search/send, but no labels, no modify, no thread management
- **Calendar**: OAuth2 Python client — read-write but single calendar, hardcoded timezone
- **Drive**: OAuth2 Python client — **read-only**, no create/modify/delete, no folder navigation

`gws` would give Alex (and the entire workforce) full read-write access to ALL Google Workspace services through a single tool, outputting structured JSON perfect for programmatic consumption.

## What `gws` Is

- **Rust-based CLI** installed via `npm install -g @googleworkspace/cli` (ships pre-built binaries, no Rust toolchain needed)
- **Dynamic command surface** — reads Google's Discovery Service, so it covers every Workspace API automatically
- **Structured JSON output** — every response is JSON, ideal for `subprocess` capture and parsing
- **100+ agent skills** included — ready-made skill files for Claude/Gemini agents
- **Multiple auth methods**: OAuth2 (interactive + headless), service accounts, pre-obtained tokens
- **Helper commands** for common workflows: `+send`, `+triage`, `+agenda`, `+upload`, `+append`, etc.
- **Not officially supported by Google** — community/open-source project

## Current vs. `gws` Capability Comparison

| Capability | Current Bot Tools | With `gws` |
|-----------|------------------|------------|
| Gmail read/search | IMAP (basic) | Full Gmail API (labels, threads, filters) |
| Gmail send | SMTP (App Passwords) | Gmail API `+send`, `+reply`, `+forward` |
| Gmail triage | None | `+triage` (unread inbox summary) |
| Calendar view | OAuth2 (single calendar) | `+agenda` (all calendars) |
| Calendar create/modify | OAuth2 (basic) | Full Calendar API |
| Drive read | OAuth2 (read-only) | Full Drive API (read + write) |
| Drive create/upload | **None** | `+upload`, `files create` |
| Drive organize | **None** | Move, rename, share, permissions |
| Google Sheets | **None** | Full Sheets API (`+read`, `+append`, create) |
| Google Docs | **None** | Full Docs API (`+write`, create, edit) |
| Google Chat | **None** | Full Chat API (`+send`) |
| Google Admin | **None** | Full Admin SDK |
| Cross-service workflows | **None** | `+standup-report`, `+meeting-prep`, `+email-to-task`, `+weekly-digest` |

## Integration Architecture

### Approach: `gws` as a New Bot Tool (subprocess pattern)

Create a single `tools/gws_tool.py` that wraps the `gws` CLI via `subprocess.run()` — the same pattern already used by the Claude Code bridge (`bridge.py`). Alex's brain calls it via Claude tool-use for any Google Workspace operation.

```
Chris (Telegram) → Alex Brain → gws_tool.py → subprocess.run("gws ...") → JSON → Alex responds
```

### Phase Strategy

**Phase A: Install + Auth (one-time setup)**
1. Install `gws` globally: `npm install -g @googleworkspace/cli`
2. Run `gws auth setup` (or manual OAuth if no `gcloud`)
3. Authenticate with Chris's Google account: `gws auth login -s drive,gmail,calendar,sheets,docs`
4. Verify: `gws drive files list --params '{"pageSize": 1}'`

**Phase B: Create `gws_tool.py` wrapper**
- Single tool function that accepts a `gws` command string
- Runs via `subprocess.run()`, captures JSON stdout
- Returns parsed JSON to Claude for natural-language response
- Error handling: structured exit codes (0=success, 1=API error, 2=auth error, etc.)

**Phase C: Register as bot tool + update brain**
- Add `gws_workspace` tool definition to `tools/__init__.py`
- Update system prompt with `gws` capabilities
- Claude decides when to use `gws` vs. existing tools

**Phase D: Deprecate old tools (optional, future)**
- Once `gws` is proven reliable, gradually retire gmail_tool.py, calendar_tool.py, drive_tool.py
- Keep SMTP sending (Chris's SMTP-FIRST directive) as fallback for email sending

## Decisions (Chris-directed, 2026-03-12)

1. **gws handles ALL Gmail** — including sending. SMTP-FIRST directive overridden for Alex bot. gws Gmail API replaces both IMAP reading and SMTP sending.
2. **Single tool** — One `gws_workspace` tool. Claude constructs the command. Maximum flexibility, minimal tool bloat.
3. **Confirmation rules** — Read operations (list, get, search): no confirmation. Write operations (create, update, delete, send): confirmation required. Claude determines from the gws method name.
4. **Build today** — Install, auth, and build integration in this session.

## Implementation Steps

### Step 1: Chris installs + authenticates gws (manual)
```bash
npm install -g @googleworkspace/cli
gws auth setup          # or manual OAuth if no gcloud
gws auth login -s drive,gmail,calendar,sheets,docs
```

### Step 2: Verify gws works (I run these after Chris confirms)
```bash
gws --version
gws drive files list --params '{"pageSize": 1}'
gws gmail +triage
gws calendar +agenda
```

### Step 3: Create `tools/alex-telegram-bot/tools/gws_tool.py`
- `run_gws(config, command, params=None, json_body=None, flags=None)` — runs `gws` via `subprocess.run()`, captures JSON stdout, parses result
- Handles structured exit codes (0=success, 1=API error, 2=auth, 3=validation)
- Timeout: 30 seconds per call
- Register as `gws_workspace` tool

### Step 4: Update `tools/alex-telegram-bot/tools/__init__.py`
- Add `gws_workspace` tool definition with input schema: `command` (string), `dry_run` (bool)
- Add to `CONFIRMATION_REQUIRED` for write operations — Claude includes `is_write: true` flag
- Total tools: 20 (was 19)

### Step 5: Update `tools/alex-telegram-bot/prompts/alex_system.py`
- Add `gws_workspace` to available tools list
- Add usage instructions: common gws commands, when to use `--dry-run`, `--fields` for efficiency
- Note: replaces gmail, calendar, drive tools for most operations (old tools kept as fallback)

### Step 6: Update `tools/alex-telegram-bot/config.py`
- Add `gws_path` config (default: `gws`, allows override via GWS_CLI_PATH env var)

## Files to Create/Modify

| File | Action | What |
|------|--------|------|
| `tools/gws_tool.py` | CREATE | gws CLI subprocess wrapper (~80 lines) |
| `tools/__init__.py` | MODIFY | Add gws_workspace tool definition + confirmation logic |
| `prompts/alex_system.py` | MODIFY | Add gws capabilities section |
| `config.py` | MODIFY | Add gws_path config key |

## Verification

After build: send "what's on my calendar today" in Telegram → verify Alex uses `gws calendar +agenda` and returns results.
