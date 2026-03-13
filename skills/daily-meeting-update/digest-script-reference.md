# Claude Code Digest Script Technical Reference

## Script Location and Usage

```bash
# Default: yesterday's sessions, text format
python3 ~/.claude/skills/daily-meeting-update/scripts/claude_digest.py

# JSON output (preferred for skill integration -- structured and parseable)
python3 ~/.claude/skills/daily-meeting-update/scripts/claude_digest.py --format json

# Today's sessions
python3 ~/.claude/skills/daily-meeting-update/scripts/claude_digest.py --date today --format json

# Specific date
python3 ~/.claude/skills/daily-meeting-update/scripts/claude_digest.py --date 2026-01-20 --format json

# Filter to specific project
python3 ~/.claude/skills/daily-meeting-update/scripts/claude_digest.py --project ~/my-app --format json
```

**Windows note**: Use `python` instead of `python3`. The script is stdlib-only (no pip installs needed).

---

## JSONL Session File Schema

Claude Code stores sessions as JSONL (one JSON object per line) in `~/.claude/projects/<encoded-path>/<session-id>.jsonl`.

### Entry Types

| `type` field | Content | Used By Script |
|---|---|---|
| `user` | User messages. May contain text or tool results | YES -- extracts first user message as title fallback |
| `assistant` | Claude responses. Contains `content` array with text and tool_use blocks | YES -- extracts file operations and bash commands |
| `summary` | Session summary (if conversation was compressed) | YES -- preferred title source when available |
| `system` | System messages (context, instructions) | NO -- skipped |
| Other | Various metadata entries | NO -- skipped |

### Message Content Structure

Content can be a string or an array of blocks:

| Block Type | Fields | What Script Extracts |
|---|---|---|
| `text` | `{"type": "text", "text": "..."}` | Plain text for title extraction |
| `tool_use` | `{"type": "tool_use", "name": "Read", "input": {"file_path": "..."}}` | Tool name (for file/command counting), file paths (for "Files" field) |
| `tool_result` | `{"type": "tool_result", "content": "..."}` | Not extracted (too verbose for standup) |

### Tracked Tool Operations

| Tool Name | What's Counted | Why |
|---|---|---|
| `Read` | File paths extracted, counted in "Files" | Shows which files were examined |
| `Write` | File paths extracted, counted in "Files" | Shows which files were created |
| `Edit` | File paths extracted, counted in "Files" | Shows which files were modified |
| `Bash` | Command count incremented | Shows volume of shell activity |
| Others | Ignored | Not relevant to standup summary |

---

## Project Path Encoding/Decoding

Claude Code encodes project paths as directory names by replacing `/` with `-` and prepending `-` for absolute paths.

| Actual Path | Encoded Directory Name | Platform |
|---|---|---|
| `/home/user/my-app` | `-home-user-my-app` | Linux/Mac |
| `/Users/john/projects/api` | `-Users-john-projects-api` | Mac |
| `C:\Users\john\projects\api` | Varies -- Windows paths use different encoding | Windows |

### Windows Path Encoding Gotchas

| Issue | Details | Impact |
|---|---|---|
| Drive letter in path | `C:\Users\...` gets encoded differently than Unix paths | `decode_project_path()` assumes Unix-style leading `/`. Windows paths may decode incorrectly |
| Backslash vs forward slash | Windows uses `\`, encoding replaces `-` | The encoding is ambiguous: `-Users-` could be `/Users/` or part of a Windows path |
| Path with spaces | `My Documents` becomes `My-Documents` in encoding | Decoding can't distinguish space-dash from directory-separator-dash |

**Practical impact**: Project display names in standup output may show garbled paths on Windows. The session DATA is still correct -- only the display label is affected. Users can mentally map "Sharkitect-Digital-Documents-project" to their actual path.

---

## Title Extraction Priority

The script tries multiple sources for a session title, in this order:

| Priority | Source | Quality | Failure Mode |
|---|---|---|---|
| 1 | `summary` field (from conversation compression) | Best -- AI-generated summary of the entire session | Only present if conversation was long enough to trigger compression. Short sessions have no summary |
| 2 | First user message (non-tool-result) | Good -- usually contains the user's initial request | May be a slash command (`/commit`), a single word (`fix`), or a very long request that gets truncated to 80 chars |
| 3 | Fallback: "Untitled session" | Poor -- no useful information | Happens when session has no user messages (rare) or all user messages are tool results |

### Title Quality Issues

| Problem | Example | Workaround |
|---|---|---|
| Slash commands as titles | "/commit" or "/review-pr" | These are technically accurate but not descriptive for standup. User will need to annotate during selection |
| Continuation sessions | "Continue where we left off" | No context about what work is being continued. User must provide context in interview |
| Very long first messages | "I need to implement a comprehensive authentication system with OAuth2, SAML, and..." | Truncated to 80 chars. Usually still informative enough |
| Multi-task sessions | User worked on 3 different things in one session | Title only captures the first task. Other work is invisible in title. User catches this during multi-select review |

---

## Date Handling

### Timezone Behavior

| Component | Timezone Used | Risk |
|---|---|---|
| `--date yesterday` argument | Local system time (via `datetime.now()`) | If system clock is wrong, wrong date is targeted |
| Session timestamps in JSONL | UTC (ISO 8601 with timezone offset) | Timestamps are normalized by stripping timezone info before comparison |
| Date range filtering | Local midnight to local midnight (start of day to start of next day) | Sessions near midnight may appear on wrong day if UTC offset is large |

### The Midnight Edge Case

A session started at 11:30 PM local time:
- Session timestamp: `2026-01-21T23:30:00` local = `2026-01-22T07:30:00Z` (UTC+8)
- `--date 2026-01-21` looks for sessions between local midnight Jan 21 and local midnight Jan 22
- The session SHOULD appear for Jan 21 (when the work happened locally)
- The script correctly uses local time comparison, so this works

A session started at 11:30 PM with work continuing past midnight:
- Multiple JSONL entries span midnight
- Script uses the FIRST timestamp (session start), not the last
- Session appears on the start date, which is correct for standup ("yesterday's work")

---

## Error Recovery

| Error | Script Behavior | Caller (Skill) Should |
|---|---|---|
| `~/.claude/projects` doesn't exist | Returns empty session list (0 sessions) | Report "No Claude Code history found" and continue to interview |
| Individual JSONL file is corrupt | Skips that file, processes others | Not visible to caller. Handled internally |
| Individual JSONL line is corrupt | Skips that line, continues parsing file | Not visible to caller. Handled internally |
| Permission denied on file | Prints error to stderr, skips file | Check stderr if session count seems low. Usually not an issue |
| Very large JSONL file (100MB+) | May be slow (10-30 seconds) to parse | Set a timeout when calling the script. If it takes >15 seconds, kill and skip |
| No sessions for requested date | Returns valid JSON with `session_count: 0` | Report "No sessions found for [date]" and continue |
| Python not available | Script doesn't run at all | Catch the execution error. Fall back to manual interview |

---

## Output Schema (JSON Format)

```json
{
  "date": "2026-01-21",
  "session_count": 3,
  "sessions": [
    {
      "id": "abc12345",
      "title": "Fix authentication timeout bug",
      "project": "/home/user/backend-api",
      "branch": "fix/auth-timeout",
      "files": ["auth.ts", "session.ts", "middleware.ts"],
      "commands_count": 5
    }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Target date, not session date (they should match) |
| `session_count` | integer | Total sessions found. 0 is valid |
| `sessions[].id` | string (8 chars) | First 8 characters of session UUID. Enough for display |
| `sessions[].title` | string (max 80 chars) | Best-effort title (see extraction priority above) |
| `sessions[].project` | string | Decoded project path. May be garbled on Windows |
| `sessions[].branch` | string or null | Git branch at session start. null if not in a git repo or branch unknown |
| `sessions[].files` | array of strings (max 10) | File names (not full paths) touched via Read/Write/Edit tools. Capped at 10 |
| `sessions[].commands_count` | integer | Number of Bash tool invocations. Indicator of session complexity |

Sessions are sorted by timestamp (earliest first).
