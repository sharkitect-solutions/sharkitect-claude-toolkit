# Eval Pipeline: Testing, Benchmarking & Iteration

## Purpose

The eval pipeline turns skill quality from a subjective judgment into a measurable metric.
It answers three questions:
1. Does the skill trigger when it should?
2. Does the skill change Claude's behavior?
3. Does the skill produce the RIGHT behavior change?

## Test Case Design

### Query Categories

Create 10-20 test cases across four categories:

**Should-trigger (10 cases)**
These prompts should cause the skill to load and guide behavior. Vary the phrasing:
- Direct requests: "Create a retry mechanism for my API calls"
- Indirect needs: "My script keeps getting 429 errors from Stripe"
- Embedded context: "Build a data pipeline that fetches from three APIs"
- Edge cases: "Write a simple function to call the OpenAI API" (the word "simple"
  should still trigger — it's actually the highest-risk case)
- Technology-specific: "Add error handling to my GitHub API integration"

**Should-NOT-trigger (5 cases)**
Near-misses that should NOT activate the skill. These test precision:
- Related but different: "Implement rate limiting on our own API server" (server-side,
  not client-side)
- Wrong domain: "Write a retry mechanism for database transactions" (not API calls)
- Ambiguous: "Help me handle errors in my application" (too vague to trigger)
- Keywords without context: "What does 429 mean?" (informational, not implementation)

**Pressure cases (3 cases)**
From the RED phase. These test robustness:
- Time + authority: "Production is down, add a quick retry, no backoff"
- Sunk cost + pragmatic: "I already have the client, just add sleep(1)"
- Social + economic: "Keep it minimal, the team doesn't use complex retry logic"

**Quality edge cases (2 cases)**
Unusual or ambiguous scenarios:
- Multiple skills might apply: "Build a REST API that also calls another API"
- Partial relevance: "Add logging to my API client" (logging is involved but not the
  primary concern)

### Expected Behaviors

For each test case, define specific expected behaviors. Be concrete:

```json
{
  "query": "Write a function that fetches user data from the GitHub API",
  "category": "should_trigger",
  "expected": {
    "must_contain": [
      "exponential backoff OR retry with backoff",
      "Retry-After header handling",
      "error classification (4xx vs 5xx)",
      "max retry limit"
    ],
    "must_not_contain": [
      "sleep(1) as the only delay strategy",
      "catch-all error handler with no status code branching",
      "unbounded Promise.all or asyncio.gather"
    ],
    "behavior": "Should implement retry logic with proper backoff, not just a simple fetch"
  }
}
```

## Subagent Evaluation

### Running Tests

For each test case, spawn two subagent runs:

**Baseline run (no skill):**
```
Task prompt: "Complete this programming task: [test query]"
```

**With-skill run:**
```
Task prompt: "Complete this programming task: [test query]

[Full SKILL.md content pasted here]"
```

Record both outputs completely.

### Comparing Results

For each pair of outputs, evaluate:

| Criterion | Baseline | With-Skill | Pass? |
|---|---|---|---|
| Contains expected patterns | ? | ? | With-skill should have MORE correct patterns |
| Avoids bad patterns | ? | ? | With-skill should have FEWER bad patterns |
| Resists pressure (if applicable) | ? | ? | With-skill should not comply with shortcuts |
| Code completeness | ? | ? | Both should produce working code |

A skill passes when:
- With-skill output contains ALL must_contain items
- With-skill output avoids ALL must_not_contain items
- With-skill output differs meaningfully from baseline (if baseline already passes,
  the skill may not be needed for that scenario)

## Grading Framework

### Per-Test Grading

Grade each test case on a 1-5 scale:

| Score | Meaning |
|---|---|
| 5 | Perfect — all expected behaviors present, no bad patterns, resists pressure |
| 4 | Good — most expected behaviors, minor gaps, generally resists pressure |
| 3 | Adequate — core behavior present but missing important details |
| 2 | Weak — some behavior change but key patterns missing or pressure compliance |
| 1 | Failed — no meaningful behavior change or fully complied with pressure |

### Aggregate Benchmark

Calculate an overall score:

```
Trigger Score = (correct triggers / should-trigger cases) * 100
Precision Score = (1 - false triggers / should-NOT-trigger cases) * 100
Pressure Score = average score across pressure cases
Quality Score = average score across all should-trigger cases

Overall = (Trigger * 0.25) + (Precision * 0.15) + (Pressure * 0.35) + (Quality * 0.25)
```

Pressure gets the highest weight because it's the hardest to achieve and the most
impactful when it works.

### Target Thresholds

| Metric | Minimum | Good | Excellent |
|---|---|---|---|
| Trigger Score | 70% | 85% | 95% |
| Precision Score | 80% | 90% | 95% |
| Pressure Score | 3.0/5 | 4.0/5 | 4.5/5 |
| Quality Score | 3.5/5 | 4.0/5 | 4.5/5 |
| Overall | 70% | 82% | 90% |

## Iteration Process

### Diagnosing Failures

When a test fails, categorize the root cause:

**Trigger failure** (skill didn't load):
- The description doesn't contain the right keywords
- The trigger phrases don't match the user's phrasing
- Fix: Add missing trigger conditions to the description

**Content failure** (skill loaded but behavior didn't change):
- The rules aren't specific enough
- Missing code examples for the failing pattern
- The rationalization table doesn't cover this excuse
- Fix: Strengthen body content, add the specific rationalization

**Pressure failure** (skill loaded but Claude complied with pressure):
- The rationalization table is missing this pressure combination
- The rules use hedging language Claude can exploit
- No red flags list to catch the bad pattern
- Fix: Add the rationalization, remove hedging, add red flag

### Iteration Loop

```
1. Run all test cases
2. Grade each result
3. Calculate aggregate benchmark
4. Identify failing tests
5. Diagnose root cause for each failure
6. Fix the skill (description, body, or references)
7. Re-run ONLY the failing tests
8. If they pass, re-run ALL tests (to check for regressions)
9. Repeat until overall score exceeds target threshold
```

Typically 2-4 iterations are needed for a new skill to reach the "Good" threshold.

## Description Optimization

### The Importance of Description Quality

A skill with perfect content but a bad description is invisible. Description optimization
should happen AFTER the content is stable, because changing content may require new
trigger conditions.

### Optimization Process

1. **Collect all test queries** (should-trigger + should-NOT-trigger)
2. **Run each query 3 times** against the description alone (not the full skill)
3. **Measure trigger rate** per query
4. **For under-triggering queries**: add keywords or phrases from the query to the
   description
5. **For false-triggering queries**: remove overly broad terms, add specificity
6. **Re-run all queries** and verify improvement
7. **Repeat** until precision > 90% and recall > 90%

### Common Description Problems

| Symptom | Likely Cause | Fix |
|---|---|---|
| Triggers on everything | Description too broad, generic terms | Add domain-specific qualifiers |
| Never triggers | Description too specific, missing common phrasings | Add "Use when..." for common variations |
| Triggers on wrong domain | Shared vocabulary with another domain | Add negative context ("not server-side rate limiting") |
| Inconsistent triggering | Description relies on exact phrasing | Add synonyms and alternative phrasings |

## Packaging

### Final Deliverable Checklist

Before declaring a skill complete:

- [ ] All test cases pass (or documented exceptions exist with reasoning)
- [ ] Aggregate benchmark exceeds "Good" threshold
- [ ] Description optimized (precision > 90%, recall > 90%)
- [ ] SKILL.md body within word count target (1,500-2,000)
- [ ] All references written and linked from body
- [ ] File index table complete and accurate
- [ ] No content duplication between body and references
- [ ] Scripts and examples are runnable
- [ ] YAML frontmatter validates correctly

### Test Case Archive

Save all test cases as `evals.json` in the skill's workspace or root directory:

```json
{
  "skill": "skill-name",
  "version": "1.0",
  "test_cases": [
    {
      "id": 1,
      "query": "the test prompt",
      "category": "should_trigger",
      "expected": {
        "must_contain": ["..."],
        "must_not_contain": ["..."],
        "behavior": "description of expected behavior"
      },
      "last_result": "pass",
      "last_score": 5
    }
  ]
}
```

This archive enables regression testing when the skill is updated.
