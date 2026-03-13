# Description Exclusion Patterns

## Why Exclusions Matter

The original CSO rule states descriptions contain only trigger conditions. Through 100+ skill optimizations, a critical addition emerged: **explicit exclusions** that prevent skill collision.

When Claude sees overlapping trigger conditions across multiple skills, it may load the wrong one -- or worse, load multiple competing skills that waste context. Exclusions solve this by naming specific skills that handle related-but-different tasks.

---

## The Exclusion Format

```yaml
description: >
  Use when [trigger condition]. Use when [trigger condition].
  Do NOT use for: [skill-name] ([what it handles]),
  [skill-name] ([what it handles]).
```

### Why This Format Works

| Without Exclusions | With Exclusions |
|---|---|
| "Write an email" could trigger email-composer, email-draft-polish, cold-email, or email-sequence | Exclusions route to the correct skill based on context |
| Multiple competing skills may load, wasting context | Only the most relevant skill loads |
| Claude guesses which skill applies based on vague overlap | Claude has explicit routing guidance |

### Real Example

```yaml
# email-composer description (with exclusions)
description: >
  Use when user needs to compose a professional email from scratch or reply to an
  email thread. Use when user says "write an email", "compose a reply", "draft a
  message to". Do NOT use for: cold-email (outbound prospecting sequences),
  email-draft-polish (refining an existing draft), email-sequence (multi-touch
  automated campaigns), professional-communication (Slack/Teams messages, not email).
```

---

## Exclusion Design Rules

| Rule | Why | Example |
|---|---|---|
| Name the competing skill explicitly | Claude cross-references against loaded skill metadata | "Do NOT use for: meeting-insights-analyzer (transcription analysis)" |
| Include parenthetical of what excluded skill does | Helps Claude understand boundary without loading the other skill | "Do NOT use for: professional-communication (drafting messages to specific recipients)" |
| Limit to 3-7 exclusions | Too many exclusions bloat description. Pick most commonly confused skills | 3 for focused skills, up to 7 for broad-trigger skills |
| Only exclude genuinely overlapping skills | Don't list unrelated skills for completeness | email-composer excludes cold-email, not pdf-processing |
| Order by confusion likelihood | Most commonly confused skill first | Put the #1 collision partner at the start of the exclusion list |

---

## Scope Boundary Tables

A complementary pattern inside SKILL.md body: maps user requests to the correct skill.

```markdown
## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Write a cold outreach email" | NO | cold-email |
| "Polish my draft email" | NO | email-draft-polish |
| "Write a reply to this email" | YES | - |
| "Compose a professional email" | YES | - |
| "Write a weekly status report" | PARTIAL -- daily update only | - |
```

### Scope Boundary Design

| Guideline | Reasoning |
|---|---|
| Include 8-12 entries | Covers common confusion points without bloating |
| Include NO entries first | Claude needs to learn what NOT to do before what to do |
| Use PARTIAL for gray areas | "PARTIAL -- can do X but Y requires [other skill]" |
| Match real user phrasings | Use natural trigger phrases, not formal descriptions |
| Include edge cases | "Run the standup for the whole team" (NO -- generates YOUR update, not team's) |

---

## Validated Impact

From 100+ skill optimizations across Tiers 1-3:

| Metric | Without Exclusions | With Exclusions | With Exclusions + Scope Boundary |
|---|---|---|---|
| D4 (Spec Compliance) avg | 10.1/15 | 12.8/15 | 14.0/15 |
| Skill collision rate | ~15% (wrong skill loads) | ~3% | <1% |
| Judge feedback on D4 | "Description lacks routing" | "Clear boundaries" | "Comprehensive skill delineation" |

The combination of description exclusions + body Scope Boundary table is the strongest D4 pattern discovered during optimization.

---

## Common Exclusion Mistakes

| Mistake | Why It Fails | Fix |
|---|---|---|
| Excluding by category ("Do NOT use for marketing skills") | Too vague -- Claude doesn't know which specific skills to check | Name each skill explicitly |
| Excluding skills that don't overlap | Wastes description space on irrelevant routing | Only exclude skills with genuine trigger overlap |
| Putting exclusions in body instead of description | Claude makes the load/skip decision from description alone. Body exclusions load too late | Exclusions MUST be in the description field |
| Using "NEVER" instead of "Do NOT use for" | "NEVER" is ambiguous (never do what?) | "Do NOT use for: [skill] ([purpose])" is explicit |
| Describing excluded skill's full functionality | Bloats description. Parenthetical should be 3-6 words | "(cold outreach sequences)" not "(creating personalized cold outreach email sequences with A/B testing and follow-up cadences)" |
