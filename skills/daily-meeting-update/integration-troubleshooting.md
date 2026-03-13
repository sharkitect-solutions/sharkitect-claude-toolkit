# Integration Troubleshooting Reference

## GitHub CLI (gh) Failure Modes

| Error | Root Cause | Fix | Don't Do |
|---|---|---|---|
| `gh auth status` shows "not logged in" | Token expired or never configured | Skip GitHub integration. Offer manual input. Never attempt `gh auth login` in standup flow | Don't try to authenticate mid-standup. It requires browser interaction and derails the flow |
| `gh: command not found` | gh CLI not installed | Skip silently. Don't suggest installation during standup | Don't warn about missing tools unless user asked about integrations |
| Rate limited (403 / "API rate limit exceeded") | Too many requests (5000/hour for authenticated, 60/hour unauthenticated) | Skip GitHub for this session. Mention: "GitHub rate limited, using manual input" | Don't retry. Rate limit recovery is 1 hour minimum |
| Wrong account authenticated | `gh auth status` shows personal account but user wants work repos | Ask: "gh is authenticated as @personal. Is that the right account for your standup?" | Don't assume the authenticated account is correct |
| `gh api` returns partial data | Pagination -- repos with 100+ PRs may truncate | For standup purposes, last 24 hours is enough. Use `--limit 20` flag | Don't paginate through all results. Standup needs recent activity only |

### gh Commands for Standup Data

| Data Needed | Command | Gotcha |
|---|---|---|
| My recent commits | `git log --author="$(git config user.email)" --since="yesterday" --oneline` | Uses git directly, not gh. Faster and works offline. Author email must match (some devs have different emails for work/personal) |
| My PRs (opened) | `gh pr list --author=@me --state=all --limit 10` | `--state=all` catches both open and recently merged. `@me` resolves to authenticated user |
| My PRs (merged yesterday) | `gh pr list --author=@me --state=merged --limit 10` then filter by merge date | gh doesn't have a `--since` flag for PRs. Must filter results client-side by `mergedAt` |
| My reviews | `gh api "search/issues?q=reviewed-by:@me+type:pr+updated:>=$(date -d yesterday +%Y-%m-%d)"` | Search API, not PR API. `reviewed-by` is a search qualifier, not a filter flag |
| Specific repo PRs | `gh pr list --repo org/repo --author=@me` | Must specify `--repo` for non-current-directory repos |

### Multi-Repo Orchestration

When user specifies multiple repos:

| Scenario | Approach | Pitfall |
|---|---|---|
| 2-3 repos | Run gh commands sequentially per repo | Don't run in parallel -- gh CLI has concurrency issues with auth token |
| Current directory + others | Use `git log` for current (faster), `gh` for remote repos | Don't assume current directory's remote matches a user-specified repo name |
| Repos in different orgs | Each `gh pr list --repo org/repo` works across orgs | If user isn't a member of an org, the command fails silently with empty results, not an error |

---

## Jira CLI Failure Modes

| Error | Root Cause | Fix |
|---|---|---|
| `jira: command not found` | CLI not installed (go-jira or jira-cli-go) | Skip. Offer manual ticket listing |
| "No credentials found" | `.jira.d/config.yml` missing or token expired | Skip. Don't attempt configuration during standup |
| Wrong instance | User has multiple Jira instances (work + client + personal) | Ask: "Which Jira instance? I see [instance URL] configured" |
| "You don't have permission" | User's token doesn't have the right project access | Skip that project. Continue with accessible ones |

### Atlassian MCP Alternative

If `mcp__atlassian__*` tools are available, prefer MCP over CLI:

| Advantage | MCP | CLI |
|---|---|---|
| Authentication | Managed by MCP server config | User must configure separately |
| Token refresh | Handled automatically | Manual or may expire mid-session |
| Data format | Structured JSON | Requires parsing text output |
| Rate limiting | MCP handles retries | Manual retry logic needed |

Use MCP tools: `mcp__atlassian__jira_search` with JQL `assignee = currentUser() AND updated >= -1d ORDER BY updated DESC`.

---

## Claude Code Digest Script Failures

| Error | Cause | Recovery |
|---|---|---|
| `python3: command not found` | Python not installed or not in PATH | Try `python` (Windows often uses `python` not `python3`). If both fail, skip Claude Code integration |
| `No sessions found for [date]` | No Claude Code sessions on target date | Expected outcome. Report: "No Claude Code sessions found for yesterday" and continue |
| `FileNotFoundError: ~/.claude/projects` | Claude Code never used in this environment | Skip silently. User may be on a machine without Claude Code |
| `UnicodeDecodeError` on JSONL parsing | Session file contains non-UTF8 characters (rare, usually from pasted binary) | Script handles this per-line. Affected sessions skipped, others processed normally |
| `PermissionError` | JSONL files owned by different user (multi-user machine) | Skip affected files. Don't attempt permission changes |
| Script runs but returns 0 sessions for a date with known activity | Timezone mismatch: script uses local time, sessions stored in UTC | Sessions near midnight may appear on adjacent day. Not worth fixing during standup -- just ask user manually |
| `json.JSONDecodeError` on a line | Corrupted or truncated JSONL entry (power loss, crash) | Script skips bad lines. If entire file is corrupt, that session is lost. Continue with others |

### Windows-Specific Gotchas

| Issue | Cause | Workaround |
|---|---|---|
| Path encoding uses backslashes | Windows paths like `C:\Users\...` don't match Unix-style `~/.claude/projects` | Script uses `Path.home()` which works cross-platform. But project directory encoding uses forward-slash replacement that may break on Windows paths with drive letters |
| `python3` not found but `python` works | Windows Python installer adds `python` to PATH, not `python3` | Try `python` first on Windows, `python3` on Mac/Linux |
| JSONL files locked by running Claude Code session | Windows file locking prevents reading active session files | Read-only access works even with lock. But if Claude Code is actively writing, last few lines may be incomplete |
| Line endings (CRLF vs LF) | Git autocrlf may change JSONL line endings | `json.loads()` handles both. Not an issue in practice |

---

## Git Failure Modes

| Error | Cause | Recovery |
|---|---|---|
| "not a git repository" | User triggered standup from non-repo directory | Skip git integration. Ask: "Want to navigate to a specific project, or provide info manually?" |
| `git log` returns nothing for yesterday | All work was on a different branch, or commits were rebased/squashed | Ask: "I don't see recent commits on this branch. Were you working on a different branch?" |
| Author email mismatch | User committed with different email than `git config user.email` | Try `--author` with username instead of email. Or broaden: `--all --author="partial-name"` |
| Detached HEAD | User is not on a named branch | Report commits but note: "You're in detached HEAD state. Which branch was this work for?" |

---

## Integration Priority When Multiple Fail

| Scenario | Action |
|---|---|
| All integrations fail | Proceed with manual interview. Don't apologize excessively. "I'll ask you directly -- let's get your update ready" |
| Only git works (no gh, no jira) | Use `git log` for commit history. This covers 60-70% of code activity without GitHub API |
| gh works but rate limited on specific repo | Use available data, note the gap: "Couldn't pull from repo-x (rate limited). Anything notable there?" |
| Digest script fails but git/gh work | Skip Claude Code history. Note: "Claude Code history unavailable, but I have your git/GitHub activity" |
| One integration returns stale data | If data is >48 hours old, flag it: "This Jira data may be stale (last updated 3 days ago). Is it current?" |
