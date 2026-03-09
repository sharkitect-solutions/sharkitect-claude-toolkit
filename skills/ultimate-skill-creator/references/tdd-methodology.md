# TDD Methodology for Skill Creation

## The Iron Law

**No skill without a failing test first.**

A skill that hasn't been tested against Claude's actual failure modes is a guess. The
TDD process discovers those failure modes BEFORE writing the skill content, then verifies
the content actually fixes them.

## The RED-GREEN-REFACTOR Cycle

### RED Phase: Discover How Claude Fails

The goal: understand exactly how Claude behaves WITHOUT the skill, so you know what the
skill needs to fix.

#### Step 1: Design Pressure Scenarios

Create 3 pressure scenarios that would cause Claude to skip the behavior your skill
enforces. Each scenario should combine 3+ pressure types for realistic difficulty.

**Pressure Type Taxonomy:**

| Type | What It Sounds Like | Why It Works |
|---|---|---|
| Time | "Production is down, fix this now" | Urgency overrides thoroughness |
| Authority | "Don't worry about X, just do Y" | User knows best, defer to them |
| Sunk Cost | "I already wrote this, just add one thing" | Don't want to redo existing work |
| Pragmatic | "This is just a prototype" | Lower standards for non-production code |
| Economic | "We're running out of budget/tokens" | Minimize work to save resources |
| Exhaustion | Complex multi-step task, this is step 7 of 10 | Fatigue leads to cutting corners |
| Social | "Everyone does it this way" or "the team prefers..." | Conformity pressure |

**Strong pressure scenarios combine multiple types:**

Weak (single pressure):
> "Write a quick API client" (pragmatic only)

Strong (triple pressure):
> "Production is down. I already wrote the API client but it's getting 429 errors.
> Just add a simple sleep(1) between requests — don't overcomplicate it, we need
> this fixed in the next 5 minutes." (time + sunk cost + authority)

#### Step 2: Run Baseline Tests

For each pressure scenario, spawn a subagent WITHOUT the skill loaded:

```
Subagent prompt:
"You are Claude Code. The user has given you this task:

[pressure scenario text]

Complete the task as requested."
```

Record the subagent's FULL response. Look for:
- Did it comply with the user's request to skip the behavior?
- What rationalizations did it use to justify skipping?
- What specific bad patterns did it produce in the code?
- Did it acknowledge the risk at all?

#### Step 3: Extract Rationalizations

From each baseline test, extract the exact phrases Claude used to justify its behavior.
These become your rationalization table entries. Common patterns:

- "Since this is a quick/simple/prototype..." → Pragmatic rationalization
- "As you mentioned, we should keep this straightforward..." → Authority deference
- "Given the urgency..." → Time pressure compliance
- "Building on the existing code..." → Sunk cost avoidance
- "For now, this approach should work..." → Deferred correctness

Capture these verbatim. They are the "failing tests" your skill must address.

### GREEN Phase: Write Minimal Content That Passes

Now write the SKILL.md body to directly address the captured failures.

#### Step 1: Build the Rationalization Table

For every rationalization captured in RED:

| Rationalization | When It Appears | Why It Is Wrong |
|---|---|---|

- **Rationalization**: The exact phrase or pattern Claude uses
- **When It Appears**: The specific context that triggers this rationalization (pressure
  type, user phrasing, task characteristics)
- **Why It Is Wrong**: A clear, brief counterargument that Claude can use to override
  the rationalization in real time

The "Why It Is Wrong" column should be actionable, not philosophical. Instead of
"because quality matters," write "a retry decorator is 5 lines — simpler than debugging
partial data at 2 AM."

#### Step 2: Build the Red Flags List

For every bad code pattern or behavior observed in the baseline tests:

```markdown
- [ ] [specific pattern, e.g., "fetch() with no retry wrapper"]
- [ ] [specific pattern, e.g., "catch block that returns null"]
```

Red flags should be:
- Specific enough to pattern-match (not "bad error handling" but "catch that returns null")
- Scannable (checkbox format, one line each)
- Ordered from most common to least common

#### Step 3: Write Non-Negotiable Rules

State each rule as an imperative with a brief "why":

```markdown
### 1. Always Do X

Do X because [concrete reason]. Without X, [concrete consequence].
```

Rules must:
- Use imperative voice ("Always do X" not "You should consider doing X")
- Explain WHY in 1-2 sentences (rules without reasons get ignored under pressure)
- Be concrete (not "handle errors properly" but "classify errors by status code before
  deciding whether to retry")

#### Step 4: Include Code Examples

For coding-focused skills, show both the wrong and right patterns:

```markdown
# WRONG: [what it does wrong]
[bad code]

# RIGHT: [what it does right]
[good code]
```

Showing the wrong pattern is critical — it helps Claude recognize the pattern in its
own output and catch itself before committing to it.

### REFACTOR Phase: Close Loopholes

After writing the GREEN content, do a loophole audit.

#### Step 1: Read Every Rule as a Lawyer

For each rule in the skill, ask: "How would Claude comply with the letter of this rule
while violating its spirit?"

Example: Rule says "always use exponential backoff." Claude might add backoff but with a
max_retries of 1, which technically satisfies the rule but defeats the purpose.

#### Step 2: Test New Edge Cases

For each loophole found, create a new pressure scenario that specifically targets it.
Run as a subagent test with the skill loaded. If Claude finds the loophole, tighten
the rule.

#### Step 3: Update the Rationalization Table

Every loophole represents a NEW rationalization Claude might use. Add it to the table.

#### Step 4: Repeat Until Stable

Continue the REFACTOR cycle until you can't find new loopholes. In practice, 2-3
REFACTOR passes are usually enough.

## Subagent Testing Methodology

### Test Infrastructure

Use Claude Code's Task tool to spawn subagents for testing. Each subagent gets:
- A system prompt that optionally includes the skill content
- A user prompt containing the test scenario
- No access to the conversation history (clean test environment)

### With-Skill vs Baseline Pattern

For each test scenario, run TWO subagents:

1. **Baseline** (no skill): Measures Claude's default behavior
2. **With-skill**: Measures whether the skill changes behavior

The skill is only valuable if there's a measurable difference. If both produce the
same output, the skill content isn't strong enough.

### Grading Criteria

For each subagent output, evaluate:

1. **Did the skill trigger?** (description test — only relevant for with-skill runs)
2. **Did behavior change?** Compare with-skill vs baseline outputs
3. **Did it change correctly?** The with-skill output should match expected behavior
4. **Did it resist pressure?** Under pressure scenarios, did the skill hold?

### Recording Results

For each test, record:
- Test scenario (the prompt)
- Baseline output (summary + key quotes)
- With-skill output (summary + key quotes)
- Pass/fail per criterion
- Notes on any rationalizations observed

## Advanced: Combining RED with Real User Failures

If the skill addresses a domain where you have real examples of Claude failing:
- Collect actual failure examples from conversations, logs, or user reports
- Use these as additional RED phase inputs
- Real failures are more valuable than synthetic pressure scenarios because they
  capture the exact context in which Claude rationalizes

## When to Skip TDD

Almost never. But for purely informational skills (reference material with no behavioral
requirements), the pressure testing is less critical. Even then, test whether the skill
triggers correctly — a reference skill that never loads is still useless.

The minimum testing for ANY skill:
- 5 should-trigger queries
- 3 should-NOT-trigger queries
- 1 pressure scenario (to verify the skill doesn't HURT when combined with pressure)
