# Clarity Dimension Scoring Rubric

Detailed scoring guide for each of the six clarity dimensions. Use this when you need
precise scores during the interview process.

## Scope (Weight: 25%)

| Score | Indicator | Example |
|---|---|---|
| 1-2 | Abstract noun only | "Build me a platform" |
| 3-4 | Category identified but boundaries unclear | "A task management tool" |
| 5-6 | Core features listed but edges fuzzy | "CRUD for tasks, maybe some reporting" |
| 7-8 | In-scope and out-of-scope explicitly stated | "Task CRUD + status tracking. No reporting, no auth, no mobile." |
| 9-10 | Scope locked with decomposition for large systems | "Phase 1: API with 3 endpoints. Phase 2: CLI client. Phase 3: Notifications." |

**Probing triggers (score < 7):**
- "What's the ONE thing this must do on day one?"
- "What are you explicitly NOT building?"
- "If you had to ship in 2 hours, which part ships?"

## Success Criteria (Weight: 20%)

| Score | Indicator | Example |
|---|---|---|
| 1-2 | No criteria or purely subjective | "It should work well" |
| 3-4 | General direction without measurement | "It should be fast" |
| 5-6 | Some measurable criteria mixed with vague ones | "Returns JSON, should be reliable" |
| 7-8 | All criteria measurable and testable | "200 on valid input, 422 on invalid, <100ms p95, 95% uptime" |
| 9-10 | Criteria include acceptance tests with specific inputs/outputs | "Given input X, returns Y. Given malformed Z, returns 400 with error body W." |

**Probing triggers (score < 7):**
- "How will you know this is done? What would you test?"
- "What does 'works correctly' mean -- can you give me one concrete example?"
- "If I showed you the finished product, what would you check first?"

## Constraints (Weight: 20%)

| Score | Indicator | Example |
|---|---|---|
| 1-2 | No constraints mentioned | - |
| 3-4 | Implicit constraints from context | "It's a Python project" (inferred from repo) |
| 5-6 | Some constraints explicit, others assumed | "Python, but no specific version or dependency rules" |
| 7-8 | Technical and process constraints stated | "Python 3.10+, stdlib only, must run on Windows, no external APIs, <500 lines" |
| 9-10 | Constraints include rationale and flexibility flags | "Stdlib only (deployment restriction, non-negotiable). Windows required (user's OS, non-negotiable). <500 lines (preference, negotiable)." |

**Probing triggers (score < 7):**
- "What technology constraints exist? (language, dependencies, platforms)"
- "Are there any 'must not' rules? (no external APIs, no new dependencies, no database)"
- "What's the deployment target? (local script, server, cloud function, CLI tool)"

## Edge Cases (Weight: 15%)

| Score | Indicator | Example |
|---|---|---|
| 1-2 | Not considered at all | - |
| 3-4 | Acknowledged but not specified | "Handle errors gracefully" |
| 5-6 | Happy path + one failure mode defined | "Empty input returns []. Errors logged." |
| 7-8 | 3+ edge cases with defined behavior | "Empty: []. Malformed: 400. Timeout: retry 3x. Rate limit: backoff." |
| 9-10 | Edge cases prioritized by likelihood with degradation strategy | "Most likely: timeout (retry). Second: malformed input (validate+reject). Unlikely: DB down (queue+retry). Catastrophic: data corruption (halt+alert)." |

**Probing triggers (score < 7):**
- "What happens when the input is empty? Malformed? Missing a field?"
- "What if the upstream service is down or slow?"
- "What's the worst thing that could happen? How should the system respond?"

## Dependencies (Weight: 10%)

| Score | Indicator | Example |
|---|---|---|
| 1-2 | Unknown or not considered | - |
| 3-4 | Vague references to other systems | "It connects to the database somehow" |
| 5-6 | Dependencies named but interface unclear | "Reads from Supabase" |
| 7-8 | Dependencies named with interface + status | "Reads from Supabase `tasks` table (exists, schema known). Called by n8n webhook (exists, endpoint defined)." |
| 9-10 | Dependencies mapped with fallback strategy | "Primary: Supabase tasks table. Fallback: local JSON cache. n8n webhook calls POST /api/tasks. If n8n unavailable: manual CLI trigger." |

**Probing triggers (score < 7):**
- "What existing systems does this interact with?"
- "Does this depend on anything that doesn't exist yet?"
- "What happens if a dependency is unavailable?"

## User Context (Weight: 10%)

| Score | Indicator | Example |
|---|---|---|
| 1-2 | No user information | "Users will use it" |
| 3-4 | General audience | "Internal team" |
| 5-6 | Audience + access method | "Dev team via CLI" |
| 7-8 | Audience + access + frequency + motivation | "3-person dev team, CLI, daily during standup, to triage overnight alerts" |
| 9-10 | Full user journey mapped | "User gets Telegram alert -> opens CLI -> runs triage command -> sees prioritized list -> marks items resolved -> summary pushed to Slack" |

**Probing triggers (score < 7):**
- "Who specifically will use this? How many people?"
- "How will they access it? (CLI, web, API, Slack bot, etc.)"
- "When and why do they use it? What triggers the need?"

## Calculating the Weighted Score

```
weighted_score = (scope * 0.25) + (success * 0.20) + (constraints * 0.20) +
                 (edge_cases * 0.15) + (dependencies * 0.10) + (user_context * 0.10)
```

**Threshold:** >= 7.0 to proceed. Below 7.0, identify the lowest-weighted dimension
that would move the needle most and target it with the next question.

**Efficiency rule:** A dimension at 4 with weight 25% (scope) contributes -0.75 to the
gap vs threshold. A dimension at 4 with weight 10% (user context) contributes -0.30.
Always probe the dimension where (weight * gap) is largest.
