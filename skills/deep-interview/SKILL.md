---
name: deep-interview
description: >
  Use when the user's request is vague, underspecified, or ambitious. Use when the user says
  "I want to build...", "I need...", "Can you create...", "Let's make..." without specifying
  scope, constraints, success criteria, or edge cases. Use when brainstorming would start
  but requirements feel thin. Use when the user describes a WHAT without a WHY or WHEN or
  HOW MUCH. Use when you detect 2+ undefined dimensions in a request. Use when the user
  explicitly says "/deep-interview", "interview me", "help me think through this",
  "clarify requirements", "what am I missing", "poke holes in this idea".
  Use BEFORE brainstorming or writing-plans when the idea has gaps.
  Do NOT use when requirements are already specific and complete. Do NOT use for simple
  tasks (rename a variable, fix a typo, add a comment). Do NOT use when the user says
  "just do it" or provides a detailed spec. Do NOT use for debugging, code review, or
  operational tasks. Use superpowers:brainstorming instead when requirements are clear
  but design needs exploration. Use writing-plans when both requirements and design are clear.
---

# Deep Interview: Socratic Requirements Clarification

Expose what the user hasn't thought about BEFORE any code gets written. This skill uses
structured Socratic questioning to transform vague ideas into buildable requirements briefs.

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/dimension-rubric.md` | Scoring clarity, assessing thresholds, weighting dimensions | Questioning phase (focus on asking, not scoring) |
| `references/question-bank.md` | Need specific probing questions for a dimension | Already past the questioning phase |
| `references/assumption-patterns.md` | Identifying hidden assumptions by domain | Simple, well-scoped requests |
| `references/ontology-tracking.md` | Entities shifting across rounds, need convergence method | Entities already stable for 2+ rounds |

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "I want to build X" (vague) | YES | - |
| "Help me think through this idea" | YES | - |
| "/deep-interview" | YES | - |
| "What am I missing?" | YES | - |
| "Build X with these exact specs [detailed]" | NO | superpowers:brainstorming or writing-plans |
| "Fix this bug" | NO | superpowers:systematic-debugging |
| "Review this code" | NO | code-reviewer |
| "Plan the implementation of [clear spec]" | NO | superpowers:writing-plans |
| "Explore approaches for [clear requirement]" | NO | superpowers:brainstorming |

<HARD-GATE>
Do NOT start implementation, write code, create files, scaffold projects, or invoke
any build skill until the interview produces a requirements brief with ALL dimensions
scoring 7+ out of 10. If the user says "just build it" mid-interview, present the
current clarity scores and explain which gaps will cause rework. Let them decide, but
make the cost visible.
</HARD-GATE>

## When to Auto-Suggest

Detect these signals and suggest a deep interview before proceeding:

- Request uses abstract nouns without specifics ("a system", "a platform", "a tool")
- No success criteria mentioned (how will we know it works?)
- No constraints mentioned (timeline, budget, tech stack, users)
- Scope is unbounded ("and also...", "with everything", "full-featured")
- User references something they saw without specifying what they want from it
- Multiple independent subsystems in a single sentence

**Auto-suggest phrasing:** "This sounds like it has some undefined dimensions. Want me
to run a quick deep interview to surface what we might be missing? It takes 3-5 questions."

## The Six Clarity Dimensions

Every requirement has six dimensions. Score each 1-10 during the interview.

| Dimension | Weight | What It Measures | Score 1 (Vague) | Score 10 (Crystal) |
|---|---|---|---|---|
| **Scope** | 25% | What's in, what's out | "Build me an app" | "CRUD API for tasks with 3 endpoints, no auth" |
| **Success Criteria** | 20% | How we know it's done | "It should work well" | "Returns 200 on valid input, 422 on bad input, <100ms p95" |
| **Constraints** | 20% | What limits the solution | None mentioned | "Python stdlib only, must run on Windows, no external APIs" |
| **Edge Cases** | 15% | What happens when things go wrong | Not considered | "Empty input returns [], malformed JSON returns 400, rate-limited after 100 req/min" |
| **Dependencies** | 10% | What this connects to | Unknown | "Reads from Supabase tasks table, called by n8n webhook node" |
| **User Context** | 10% | Who uses this and why | "Users" | "Internal team of 3, accessed via CLI, used daily for task triage" |

**Clarity threshold:** Weighted average >= 7.0. Below 7.0, keep asking. Above 7.0,
present the brief and transition to brainstorming.

## The Interview Process

### Phase 1: Quick Assessment (1 message)

**Brownfield detection:** Before scoring, check if the request involves modifying an
existing system. Look for signals: the CWD has source code, the user references existing
files/features, or says "add to", "change", "extend", "fix". If brownfield:
- Use Glob/Grep/Read to explore the relevant codebase area FIRST
- Cite what you found when asking questions: "I see JWT auth in `src/auth/`. Should this
  feature extend that, or use a different approach?" Never ask the user what the code
  already reveals.
- Brownfield projects score Dependencies higher (existing integrations matter more)

Read the user's request. Internally score all six dimensions. Identify the 2-3 lowest-scoring
dimensions. Do NOT dump all six scores on the user -- pick the biggest gaps.

### Phase 2: Socratic Probing (3-7 questions)

Ask ONE question at a time. Each question targets the lowest-scoring dimension.

**Question targeting rule:** Always probe the dimension where `(weight * gap_to_10)` is
largest. A scope dimension at 4 (weight 25%, gap 6) contributes 1.5 to the deficit. A
user context dimension at 4 (weight 10%, gap 6) contributes 0.6. Probe scope first --
it moves the needle 2.5x more per question.

**Rules for questions:**

1. **One question per message.** Never batch questions. Wait for the answer.
2. **Offer choices when possible.** "Would this be (a) internal tool, (b) customer-facing, or (c) both?" is better than "Who uses this?"
3. **Reflect back before asking.** "So it sounds like [X]. Given that, [question]?" shows you're listening.
4. **Name the assumption you're testing.** "I'm assuming [X] -- is that right, or...?" surfaces hidden assumptions the user didn't know they had.
5. **Stop when clarity threshold is met.** Don't over-interview. 7.0 weighted average means GO.
6. **Escalate, don't repeat.** If a dimension stays vague after 2 questions, flag it explicitly: "We still don't have clear [dimension]. This will cause rework later. Should we define it now or accept the risk?"
7. **Cap at 7 questions.** If clarity is 6.5+ after 5 questions, present the brief with noted risks rather than drilling further. See "The Over-Interviewer" anti-pattern below.
8. **Track entity stability.** After each answer, note the key entities (nouns) the user
   has named: systems, objects, users, data types. If the same concept gets different names
   across answers ("workflow" then "pipeline" then "queue"), the user's mental model is
   unstable. When entities shift across 2+ rounds, stop asking about features and ask:
   "You've described this as [X], [Y], and [Z]. Which one IS it, and which are views of
   the same thing?" Stable entities = ready to move forward. Shifting entities = keep probing
   scope. See `references/ontology-tracking.md` for the full convergence method.

### Phase 3: Assumption Exposure

After scoring hits 6.0+, present the assumptions you've detected:

```
## Detected Assumptions

1. **[Assumption]** -- You haven't explicitly stated [X]. I'm assuming [Y].
   Is that correct, or should we define this differently?

2. **[Assumption]** -- The request implies [X], but [alternative Z] is also
   possible. Which do you intend?

3. **[Assumption]** -- No mention of [X]. Common pitfall: teams skip this
   and discover it during integration. Want to address it now?
```

Each assumption the user confirms or corrects improves the clarity score.

### Phase 4: Requirements Brief

When clarity threshold (7.0) is reached, produce this deliverable:

```markdown
## Requirements Brief: [Title]

**Clarity Score:** [weighted average] / 10

### Scope
- **In scope:** [bullet list]
- **Out of scope:** [bullet list]
- **Deferred:** [bullet list with reasoning]

### Success Criteria
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]

### Constraints
- [Constraint 1]
- [Constraint 2]

### Edge Cases
- [Edge case 1] -> [Expected behavior]
- [Edge case 2] -> [Expected behavior]

### Dependencies
- [Dependency 1] -- [status: exists/needs-building/unknown]
- [Dependency 2] -- [status]

### User Context
- **Who:** [description]
- **How:** [access method]
- **When:** [frequency/triggers]
- **Why:** [motivation]

### Assumptions (Confirmed)
- [Assumption 1] -- confirmed by user
- [Assumption 2] -- confirmed by user

### Risks
- [Risk 1] -- [mitigation or accepted]
```

### Phase 5: Handoff

After the user approves the brief:

1. Save the brief to `docs/superpowers/specs/YYYY-MM-DD-<topic>-requirements.md`
2. Invoke `superpowers:brainstorming` with the brief as input context
3. The brainstorming skill handles design exploration from there

## State Persistence

**Save after every round.** Write interview state to `.tmp/deep-interview-state.json`:

```json
{
  "topic": "brief title",
  "started": "2026-04-12T14:30:00Z",
  "round": 3,
  "scores": {"scope": 8, "success": 5, "constraints": 7, "edge_cases": 3, "dependencies": 6, "user_context": 9},
  "weighted_avg": 6.2,
  "entities": ["Task", "User", "Workflow"],
  "entity_stable_rounds": 1,
  "brownfield": false,
  "qa_pairs": [{"q": "...", "a": "..."}, ...]
}
```

**Resume on re-invocation.** If `.tmp/deep-interview-state.json` exists when the skill
loads, offer: "Found an in-progress interview about [topic] (round [N], clarity [X]/10).
Resume or start fresh?" If resume, load the state and continue from the next question.

**Clean up on completion.** Delete the state file after the requirements brief is saved
and approved. Don't leave stale state for the next interview.

## Anti-Pattern: "The Premature Builder"

The #1 failure mode: skipping requirements clarification because the task SEEMS clear.

**Detection signals:**
- You feel confident you understand after reading one sentence
- The request uses familiar words (API, dashboard, workflow) so you assume standard patterns
- The user is excited and you don't want to slow them down
- You've built something similar before

**Why it's wrong:** Familiar words mask different intentions. "Build me a dashboard"
means wildly different things depending on who's looking at it, what decisions it informs,
how often it updates, and what actions it enables. The 5 minutes spent interviewing saves
the 2 hours spent rebuilding when assumptions are wrong.

## Anti-Pattern: "The Over-Interviewer"

The #2 failure mode: asking so many questions the user disengages.

**Detection signals:**
- You've asked 5+ questions and clarity is already above 6.5
- The user's answers are getting shorter or more impatient
- You're probing low-weight dimensions (dependencies, user context) when high-weight ones are clear
- You're asking for precision beyond what the task requires (exact millisecond SLAs for an internal script)

**Why it's wrong:** The interview exists to prevent rework, not to produce a perfect spec.
A brief with two noted risks ships faster than a brief that never gets written because the
user said "forget it, just build something." Know when 80% clarity is enough to start.

**The rule:** 7 questions maximum for a moderately scoped request. If you hit question 5
with a weighted average of 6.5+, present the brief with explicit risk notes on the weak
dimensions. Let the user decide whether to clarify further or accept the risks.

## Rationalization Table

| Rationalization | When It Appears | Why It Is Wrong |
|---|---|---|
| "The user seems to know what they want" | User speaks confidently about a vague idea | Confidence about WHAT doesn't mean clarity about HOW, WHEN, WHO, or edge cases. Interview the gaps. |
| "This is straightforward, no interview needed" | Familiar problem domain | Familiar domains have the MOST hidden assumptions because you fill gaps with your own defaults instead of asking. |
| "I don't want to slow the user down with questions" | User seems eager to start | 5 minutes of questions saves 2 hours of rework. The user will thank you for surfacing the blind spot they missed. |
| "I'll figure out the details as I build" | Ambiguous scope but clear starting point | Discovering requirements during implementation means rework. Every assumption you don't validate is a potential rebuild. |
| "The brainstorming skill will handle requirements" | Requirements overlap with design | Brainstorming explores HOW given clear requirements. This skill defines WHAT. Skipping WHAT makes HOW meaningless. |
| "One quick question is enough" | Time pressure | One question covers one dimension. Six dimensions need targeted probing. Under-interviewing leaves 5 blind spots. |

## Red Flags Checklist

Before transitioning to brainstorming, verify NONE of these are true:

- [ ] Any dimension scores below 5 (critical gap -- must address)
- [ ] Weighted average below 7.0 (keep interviewing)
- [ ] User said something contradictory that wasn't resolved
- [ ] Scope includes multiple independent systems without decomposition plan
- [ ] Success criteria are subjective ("should work well", "looks good")
- [ ] No edge cases identified (every system has them -- dig harder)
- [ ] Dependencies listed as "unknown" without a plan to resolve
- [ ] Assumptions presented but user didn't confirm or deny
- [ ] Brief was produced but user didn't review and approve it

## Integration with Workflow

```
User Request (vague)
       |
  [deep-interview]  <-- YOU ARE HERE
       |
  Requirements Brief (approved)
       |
  [superpowers:brainstorming]
       |
  Design Spec (approved)
       |
  [superpowers:writing-plans]
       |
  Implementation Plan
       |
  [execution skills]
```

The deep interview is the FIRST gate. It feeds brainstorming, which feeds planning,
which feeds execution. Skipping this gate means every downstream stage inherits
unvalidated assumptions.

## Example: Before and After

**User request:** "I want to build a notification system"

**Without deep interview:** Claude starts building an email notification system with
SMTP, HTML templates, and a queue. User wanted Telegram alerts for their 3-person team.
2 hours wasted.

**With deep interview (3 questions):**

> Q1: "Would this be (a) email notifications, (b) push notifications, (c) chat alerts
> (Slack/Telegram/Discord), or (d) in-app notifications?"
> A: "Telegram alerts for our team"
>
> Q2: "What triggers an alert? Is it (a) a scheduled check, (b) an event from another
> system, or (c) manual? And how urgent -- real-time or batched?"
> A: "When a gap report lands in the inbox. Real-time."
>
> Q3: "I'm assuming the Telegram bot already exists and we just need to send to it.
> Is that right, or do we need to set up the bot too?"
> A: "Bot exists, just need the send function"

**Clarity scores after 3 questions:** Scope: 9, Success: 7, Constraints: 8, Edge Cases: 5,
Dependencies: 8, User Context: 9. Weighted average: 7.8. Threshold met.

**Result:** Requirements brief produced in 2 minutes. Correct system built on first attempt.
