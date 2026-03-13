---
name: daily-meeting-update
description: "Use when user says 'daily', 'standup', 'scrum update', 'status update', 'what did I do yesterday', 'prepare for meeting', 'morning update', or 'team sync'. Generates formatted standup updates through interactive interview + optional tool integrations (GitHub, Jira, Claude Code history). Do NOT use for: meeting transcription or analysis (meeting-insights-analyzer), writing internal announcements (internal-comms), crafting professional messages (professional-communication), giving or receiving performance feedback (feedback-mastery)."
user-invocable: true
---

# Daily Meeting Update

Generate daily standup updates through interview + optional integrations. Never assume tools are configured.

---

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `integration-troubleshooting.md` | Any integration detection fails, gh/jira/git commands return errors, digest script fails, user reports data mismatch | Simple manual-only standup with no integrations |
| `standup-effectiveness.md` | User asks about standup format, async standups, update length, audience calibration, or team standup design | Standard standup generation with no format questions |
| `digest-script-reference.md` | Claude Code history integration is used, digest script errors, need to understand JSONL schema or path encoding | No Claude Code history integration requested |
| `scripts/claude_digest.py` | User approves Claude Code history pull. Run with `python3 ~/.claude/skills/daily-meeting-update/scripts/claude_digest.py --format json` | User declines Claude Code history or `~/.claude/projects` doesn't exist |

---

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Prepare my daily standup" | YES | - |
| "Generate a scrum update" | YES | - |
| "What did I do yesterday?" (in standup context) | YES | - |
| "Summarize this meeting recording" | NO | meeting-insights-analyzer |
| "Write an announcement to the team" | NO | internal-comms |
| "Draft a message to my manager" | NO | professional-communication, email-composer |
| "Help me give feedback to a teammate" | NO | feedback-mastery |
| "Write my weekly status report" | PARTIAL -- can generate daily, but weekly aggregation is manual | - |
| "Run my standup for the whole team" | NO -- this generates YOUR update, not the team's | - |

---

## Integration Detection Order

Check integrations in this order. Each check must be SILENT (suppress all errors). Ask user BEFORE pulling any data.

| Priority | Integration | Detection Command | Failure Mode | Recovery |
|---|---|---|---|---|
| 1 | **Git** (local) | Check if current directory is a git repo: `git rev-parse --is-inside-work-tree` | Not in a git repo | Skip silently. Many standups don't need git |
| 2 | **GitHub CLI** | `gh auth status 2>&1` -- must show "Logged in" | Auth expired, wrong account, rate limited | Offer: "gh CLI detected but not authenticated. Skip GitHub data?" Never attempt `gh auth login` |
| 3 | **Jira CLI** | `jira version 2>&1` or check for `mcp__atlassian__*` tools | CLI not installed, wrong instance, token expired | Offer manual ticket input: "Want to list your Jira tickets manually?" |
| 4 | **Claude Code History** | Check `~/.claude/projects` exists with `.jsonl` files | No projects dir, no sessions for target date, script fails | Skip silently. Claude Code history is supplemental, never blocking |

### Integration Consent Decision

| Scenario | Action |
|---|---|
| User says "pull everything" | Ask which repos/projects specifically. Never interpret "everything" as all accessible repos |
| User says "just manual" | Skip ALL integrations. Go directly to interview Phase 2 |
| Integration detected but user declines | Skip that integration permanently for this session. Don't re-ask |
| Multiple repos detected | Ask user to select. Don't assume current directory is the only project |
| Integration fails mid-pull | Report briefly, continue without that data. "GitHub pull failed -- I'll ask you manually instead" |

---

## Interview Framework

### Context-Primed vs Cold Questions

Research on memory recall (Tulving 1973, encoding specificity): showing contextual cues before asking improves recall 40-60% vs open-ended questions.

| Data Available | Question Style | Example |
|---|---|---|
| **GitHub data pulled** | Context-primed | "I found: merged PR #123 (fix login timeout), 3 commits in backend-api. Anything else you worked on?" |
| **Jira tickets found** | Suggest-and-confirm | "I see PROJ-456 is In Progress. Will you continue this today?" |
| **Claude Code sessions** | Multi-select filter | Present sessions, let user check relevant ones. Personal projects get unchecked |
| **No data at all** | Open recall | "What did you work on yesterday/since last standup?" |

### Vague Answer Handling

| Signal | What's Happening | Follow-Up |
|---|---|---|
| "Not much" / "The usual" | Low recall or avoidance | Probe with specificity: "Any PRs, meetings, or research?" One concrete anchor often triggers recall cascade |
| "I worked on the project" | Lacks specificity for standup | "Which part specifically? What changed between yesterday and today?" |
| "Just bug fixes" | Minimizing | "Any specific bugs worth mentioning? Even small fixes tell the team where effort went" |
| User gives 1 bullet, stops | May think that's sufficient | "Anything else? Meetings, code reviews, planning, research all count" |

### The Four Questions (non-negotiable order)

| # | Question | Why This Order | Skip Conditions |
|---|---|---|---|
| 1 | **Yesterday** (what did you accomplish) | Sets context. Integration data shown here as memory cues | Never skip |
| 2 | **Today** (what will you work on) | Naturally follows from yesterday. Jira tickets suggested here | Never skip |
| 3 | **Blockers** | After stating plans, blockers surface naturally ("I want to do X but Y is blocking") | Never skip (even "no blockers" is valuable signal) |
| 4 | **Discussion topics** | Last because it requires synthesis: "given everything above, anything the team should know?" | Never skip. Often the most valuable part -- captures cross-team dependencies, architecture questions, alignment needs that tools can't detect |

---

## Update Format Decision

| Audience | Format | Length | Include |
|---|---|---|---|
| **Live verbal standup** (< 2 min) | Bullet points, no links | 5-8 bullets max | Yesterday (2-3), Today (2-3), Blockers, Topics |
| **Async Slack/Teams** | Formatted markdown with links | 8-12 bullets | All sections + PR links + ticket links |
| **Manager status email** | Narrative sentences | 10-15 bullets, grouped | All sections + context for non-technical readers |
| **Sprint review** | Outcome-focused | 3-5 items | Completed items only, linked to sprint goals |

### Output Principles

| Principle | Rule | Why |
|---|---|---|
| **15-bullet ceiling** | Never generate more than 15 bullets total | Updates > 2 minutes lose the audience. Research: attention drops 50% after 90 seconds in standups (Stray et al. 2016) |
| **No raw commit messages** | Translate "fix: resolve timeout" to "Fixed session timeout causing users to lose work" | Commit messages are developer shorthand. Standup audience needs human-readable outcomes |
| **No orphan references** | Never write "PROJ-123" without title/summary next to it | Context-free ticket numbers force listeners to look things up. That's a standup killer |
| **Links at bottom** | Group all PR/ticket links in a "Links" footer section | Keeps the narrative clean. Links are reference material, not the story |
| **Blocker escalation** | If blocker exists, include WHO can unblock and WHAT's needed | "Blocked" without action path is venting. "Blocked on API credentials -- need from @backend-team" is actionable |

---

## Anti-Patterns

| Anti-Pattern | What Happens | Why It Fails | Fix |
|---|---|---|---|
| **The Autopilot** | Run gh/jira without asking, dump raw data as the update | Users may have personal repos visible. Raw tool data misses context, meetings, planning work. Standup becomes a git log | Always ask consent. Always interview. Tools supplement, never replace |
| **The Single-Repo Assumption** | Only check current working directory | Developers work on 2-5 repos simultaneously. Missing frontend work while in backend repo | Ask "Which projects are you working on?" before pulling |
| **The Interview Skip** | Tool data looks complete, so skip the interview entirely | Tools capture WHAT happened but never WHY. Miss context: "I spent 4 hours debugging that 1-line fix" and miss non-code work entirely | Interview is mandatory. Tools prime the conversation, they don't finish it |
| **The Premature Generate** | Start generating after 2 questions because "I have enough" | Blockers and discussion topics come last by design. Skipping them misses the most valuable standup content | Complete all 4 questions before generating. No shortcuts |
| **The Status Novel** | Generate 25+ bullets trying to be comprehensive | Long updates are ignored. Teams tune out after 90 seconds. Nobody reads a 3-screen standup | Enforce 15-bullet ceiling. Summarize groups: "3 bug fixes in auth module" not 3 separate bullets |
| **The Ticker Tape** | Include PR numbers and ticket IDs without context | "Reviewed PR #456" means nothing without "Reviewed PR #456 (payment refund logic)" | Every reference gets a human-readable description |

---

## Rationalization Table

| You might think... | But actually... |
|---|---|
| "The git log IS the standup" | Git captures code changes. Standups capture intent, context, blockers, and cross-team signals. A 4-hour debugging session might produce 1 commit. Meetings, research, and planning produce zero commits |
| "I don't need to ask consent for public repos" | Public repos may expose work the user hasn't announced yet. Work-in-progress branches, experimental features, or contributions to other projects are the user's to share or withhold |
| "Discussion topics are optional" | They're the highest-value standup item. They surface cross-team dependencies, alignment needs, and architectural decisions that no tool can detect. Stray et al. (2016): 43% of standup value comes from synchronization topics |
| "Async standups don't need format changes" | Async readers lack tone, facial expressions, and real-time Q&A. Written standups need 30% more context than verbal ones to convey the same information (Gutwin et al. 2004) |
| "One blocker per standup is enough" | Multiple blockers need separate entries because they may have different unblock owners. Combining blockers masks the dependency map |

---

## Red Flags (user's request needs pushback)

| Signal | Risk | Response |
|---|---|---|
| "Just generate something from my git log" | Update will miss non-code work, blockers, and discussion topics | "Git data is a starting point, but standup value comes from context only you can provide. Let me show you what I found and ask a few questions" |
| "Pull from all my repos" | May expose personal/unrelated projects | "Which specific repos are relevant to this standup? I want to keep it focused" |
| "Skip the questions, just use the data" | Loses 60%+ of standup value (blockers, topics, context) | "The questions take 2 minutes and catch things tools can't see -- blockers, discussions, and context. Worth it?" |
| "Make it longer / more detailed" | Exceeding 15 bullets loses the audience | "Longer updates get skimmed. Can we prioritize the top items instead?" |
| "Include my personal project too" | Mixing personal/work in a team standup | "Want to keep personal projects separate? I can note the work without the repo name" |
| "Generate a weekly report from 5 dailies" | This skill generates ONE day's update | "I can help with today's update. For weekly aggregation, you'd compile dailies manually or use a different workflow" |
| "Run the standup for the whole team" | This generates YOUR update, not others' | "I generate individual updates. Each team member would run this separately" |

---

## NEVER

- **NEVER pull from any integration without explicit user consent** -- even if gh/jira are configured and authenticated. Detection is silent; data access requires permission
- **NEVER skip the Discussion Topics question** -- it captures cross-team signals, architecture decisions, and alignment needs that no tool can detect. 43% of standup value (Stray et al. 2016)
- **NEVER generate more than 15 bullets** -- updates exceeding 2 minutes lose the audience. Summarize groups rather than listing everything
- **NEVER include ticket/PR numbers without human-readable context** -- "PROJ-123" is meaningless. Always include title or summary
- **NEVER block the standup flow on a failed integration** -- if gh/jira/digest fails, report briefly and continue. The interview is the primary path; integrations are supplemental
