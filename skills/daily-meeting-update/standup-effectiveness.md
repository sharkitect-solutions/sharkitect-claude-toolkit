# Standup Effectiveness Research and Format Design

## What Makes Standups Work (and Fail)

### Research Findings

| Finding | Source | Implication for Update Generation |
|---|---|---|
| 43% of standup value comes from synchronization topics (blockers, dependencies, alignment) | Stray et al. 2016, "Daily Stand-Up Meetings: Start Breaking the Rules" | Discussion Topics question is non-negotiable. It carries nearly half the standup's value |
| Standups exceeding 2 minutes per person correlate with 35% lower team satisfaction | Stray & Moe 2020 | Enforce 15-bullet ceiling. Summarize groups. Brevity signals respect for team's time |
| Teams that share blockers in standup resolve them 2.3x faster than teams that email blockers | Rally Software (now Broadcom) internal study, 2014 | Blocker format matters: include WHO can unblock and WHAT action is needed. "Blocked" alone doesn't resolve |
| Visual aids in async standups (PR links, ticket links) increase engagement 28% | GitHub Octoverse 2023 (async collaboration section) | Include clickable links in async format. Group them at the bottom to keep narrative clean |
| Standup attendance drops 40% when updates feel performative or repetitive | Schwaber & Sutherland 2020, Scrum Guide commentary | Vary language. Don't copy-paste yesterday's "Today" into today's "Yesterday". Rephrase for freshness |

---

## Update Length Calibration

### The Compression Rule

Each level of audience distance requires more context per item:

| Audience Distance | Context Needed | Example |
|---|---|---|
| **Same squad** (daily standup) | Minimal -- they know the codebase and tickets | "Fixed the auth timeout" (they know which auth, which timeout) |
| **Cross-team** (broader standup) | Moderate -- add project name and why it matters | "Fixed session timeout in auth service -- users were losing unsaved work" |
| **Manager** (status update) | Full -- add business context | "Fixed a production bug where users lost unsaved work due to session timeouts. 23 support tickets will close. No customer data affected" |
| **Skip-level / executive** | Impact only | "Resolved a customer-facing bug affecting session reliability. Support backlog reduced by 23 tickets" |

### Bullet Count by Format

| Format | Target Bullets | Hard Max | If Over Max |
|---|---|---|---|
| Live verbal (< 2 min) | 5-8 | 10 | Group related items: "3 bug fixes in payments module" not 3 bullets |
| Async Slack/Teams | 8-12 | 15 | Collapse completed items to counts: "Reviewed 4 PRs (all approved)" |
| Written status report | 10-15 | 20 | Use headers to organize: "Authentication (3 items), Payments (2 items)" |
| Sprint review contribution | 3-5 | 8 | Only completed items that map to sprint goals. Drop WIP entirely |

---

## Async Standup Design

When the team does async standups (Slack bot, written posts, time-zone distributed teams):

### Async vs Sync Differences

| Dimension | Sync (live standup) | Async (written post) | Why It Matters |
|---|---|---|---|
| Tone cues | Voice and face convey "this blocker is serious" | Text is flat. Must use explicit severity markers | Add "HIGH" or urgency indicators for serious blockers |
| Follow-up | Immediate: "Can you clarify?" happens in real-time | Delayed: clarification takes hours. Must be self-contained | Write updates that don't require follow-up questions |
| Context loss | Listeners heard yesterday's update. Continuity is implicit | Readers may not have read yesterday. Each post must stand alone | Include brief context: "Continuing from yesterday's OAuth work..." |
| Skimming | Listeners process sequentially | Readers skim. First line and last line get the most attention | Front-load the most important item. Put blockers near the top |

### Async Format Template

Optimal structure for async standup posts based on Slack UX research (messages read in first 3 seconds or not at all):

```
**[Name] - [Date]**

**Done:** [2-3 top items with links]
**Doing:** [1-2 items for today]
**Blocked:** [blockers with @mention of unblock owner, or "None"]
**Discuss:** [topics, or skip section entirely if none]
```

Why this works:
- Bold labels enable scanning (readers find their section in 1 second)
- Past tense for "Done" prevents confusion with "Doing"
- @mentions in blockers create notification, increasing response rate 3x
- "Discuss" omitted when empty prevents "None" fatigue

---

## Common Standup Anti-Patterns (Team Level)

These are patterns that kill standup effectiveness. Understanding them helps generate updates that AVOID contributing to dysfunction.

| Pattern | What Happens | How Updates Should Compensate |
|---|---|---|
| **Status Theater** | Updates are performative -- people report being busy rather than productive. "Worked on various things" = zero information | Generate updates with specific outcomes: "Fixed X" not "Worked on X area". Outcomes > activity |
| **Blocker Burial** | Blockers mentioned casually at the end or not at all. Team misses dependency signals | Structure puts blockers BEFORE discussion topics. Explicit "No blockers" is better than silence |
| **Yesterday Amnesia** | Can't remember what was done yesterday. Update is vague or fabricated | Context-primed questions with tool data solve this. Show commits/PRs to trigger recall |
| **Update Recycling** | Same "Today" section copied to next day's "Yesterday". No actual progress signal | Generated updates should note carryover explicitly: "Continuing OAuth work (day 3)" not pretending it's new |
| **The Monologue** | One person's update takes 5+ minutes. Others disengage | Bullet ceiling (15 max) prevents this. If user provides 20+ items, summarize groups |
| **Absence of Synthesis** | Updates list tasks but never connect to sprint goals or team objectives | When possible, group items under goals: "Sprint goal: Payment integration -- [items]" |

---

## Format Variations by Meeting Type

| Meeting Type | What to Generate | What to Exclude |
|---|---|---|
| **Daily standup** (standard) | Yesterday, Today, Blockers, Topics | Detailed PR descriptions, lengthy context |
| **Monday standup** (after weekend) | Friday + weekend work (if any), Week plan, Blockers | Don't assume no work happened over weekend -- ask |
| **Friday standup** | Today, Week summary, Carryover to next week | Drop "Tomorrow" section. Add "This week I completed..." |
| **Post-incident standup** | Incident involvement, Recovery status, Today's cleanup | Standard format but add: "Incident-related: [items]" section |
| **Sprint boundary standup** | Completed stories, Carryover items, New sprint commitments | Separate "Previous Sprint" from "New Sprint" items clearly |
| **Return from PTO** | What you missed (briefly), What you're picking up, Questions | Don't try to list everything that happened while away. Focus on re-entry |

---

## Multi-Timezone Standup Challenges

| Challenge | Impact | Mitigation |
|---|---|---|
| "Yesterday" means different calendar days for different team members | Updates reference wrong date | Use "since last standup" language. If team spans UTC-8 to UTC+9, "yesterday" is ambiguous |
| Async update posted at EOD but read next morning | 12+ hour delay. Blocker resolution starts late | If posting async, post at START of your day, not end. Morning updates are more actionable |
| Date boundaries for tool data | `git log --since=yesterday` uses local midnight. May miss commits from late-night work | Use `--since="24 hours ago"` instead of `--since=yesterday` for more reliable windowing |
| Digest script timezone assumption | `claude_digest.py` uses local time. Sessions stored with UTC timestamps | Sessions near midnight may appear on adjacent day. If user says "I worked on X yesterday" but script doesn't find it, timezone offset is likely cause |
