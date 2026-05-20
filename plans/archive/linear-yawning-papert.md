# Git + GitHub Repository Setup & Session Protocol

## Context

The HQ workspace has git initialized but zero commits, no `.gitignore`, no remote, and `.env` with all API keys is staged. 756 files staged. All work exists only on local machine with zero backup. This plan sets up GitHub, establishes the session protocol, and deactivates the briefing scheduled tasks.

## Step 1: Create `.gitignore`

Exclude ONLY sensitive credentials and Python/Node cache. Everything else travels with the repo so Chris can work from any computer without gaps.

```gitignore
# Credentials — never push secrets
.env

# OAuth tokens — machine-specific, re-auth needed per computer
tools/n8n-bot-reference/.calendar_token.json
.config/gws/token_cache.json

# Python cache — auto-regenerated
__pycache__/
*.pyc

# Node modules — auto-regenerated from package.json
node_modules/

# OS files
Thumbs.db
.DS_Store
```

**Included (travels with repo):** `.claude/` (both settings files), `.tmp/` (analysis files, configs), `knowledge-base/`, `tools/`, `workflows/`, `docs/`, `resources/`, `_archive/`, `.mcp.json`, deliverables — everything needed to pick up and work.

## Step 2: Reset staging and re-add with `.gitignore` active

```bash
git reset HEAD                    # unstage everything
git add .gitignore                # add gitignore first
git add -A                        # re-stage everything (gitignore now filters)
```

Verify `.env` is NOT staged: `git status | grep .env` should show nothing or show it as untracked.

## Step 3: Initial commit

```bash
git commit -m "Initial commit: Sharkitect Digital Workforce HQ"
```

## Step 4: Create private GitHub repo and push

```bash
gh repo create sharkitect-workforce-hq --private --source=. --push
```

## Step 5: Verify

- `gh repo view sharkitect-solutions/sharkitect-workforce-hq` shows private repo
- `.env` is NOT in the repo
- `.calendar_token.json` is NOT in the repo
- All knowledge-base, tools, docs, .tmp, .claude files ARE in the repo

## Step 6: Deactivate scheduled tasks

**Keep running:** `SharkitectSupabaseSync` (calls `tools/audit_sync.bat`, started 3/15)
**Disable:** The other 9 tasks (including the duplicate `SharkitectDigital\SupabaseSync` which calls the same file)

```bash
schtasks /change /tn "SharkitectMorningBrief" /disable
schtasks /change /tn "SharkitectEveningBrief" /disable
schtasks /change /tn "SharkitectWeeklyAudit" /disable
schtasks /change /tn "SharkitectDepsUpdate" /disable
schtasks /change /tn "SharkitectDigital\MorningAudit" /disable
schtasks /change /tn "SharkitectDigital\MiddayAudit" /disable
schtasks /change /tn "SharkitectDigital\EveningAudit" /disable
schtasks /change /tn "SharkitectDigital\MidnightAudit" /disable
schtasks /change /tn "SharkitectDigital\SupabaseSync" /disable
```

**Note:** Both Supabase sync tasks call `tools/audit_sync.bat`. They're exact duplicates (different setup rounds: 3/15 vs 3/23). Keeping the original (#3), disabling the duplicate (#10).

**Future task (not this session):** Reanalyze all scheduled tasks. Consolidate duplicates, verify briefing scripts pull correct data, potentially recreate from scratch. Added to project queue.

Verify: `schtasks /query /fo LIST | grep -A1 "Sharkitect"` — 9 should show Disabled, 1 (SharkitectSupabaseSync) should show Ready

## Step 7: Create Session Protocol

Save as feedback memory AND add to CLAUDE.md under "How to Operate":

**Session Start:**
1. Read MEMORY.md — check pending items, patterns, preferences
2. `git pull` — sync with latest from GitHub
3. Resume from where last session left off

**During Session (at stage completions / checkpoints):**
1. Update MEMORY.md with decisions and progress
2. Push state to Supabase
3. `git add` + `git commit` with descriptive message
4. `git push`

**Session End / Project Transition:**
1. Clean up stale files from the project just completed (project-scoped only, not global)
2. Purge `.tmp/` of anything no longer useful before pushing
3. Update MEMORY.md with session learnings
4. Push to Supabase (memories, session log)
5. `git add` + `git commit` + `git push` — final backup
6. Confirm clean state

**Full Workspace Audit (only when Chris explicitly requests):**
- Review entire workspace for stale/orphaned files across ALL projects
- Verify every file/folder still has a purpose
- Remove anything no longer needed

## Step 8: Update MEMORY.md

Add note that GitHub repo is set up and session protocol is active.

## Verification

- [ ] `.gitignore` created, excludes only credentials + cache
- [ ] `.env` NOT in GitHub repo
- [ ] Initial commit pushed to private repo
- [ ] All 10 scheduled tasks disabled (not deleted)
- [ ] Session protocol saved to CLAUDE.md and feedback memory
- [ ] MEMORY.md updated
- [ ] Can `git clone` on another machine and have everything needed to work (minus `.env`)
