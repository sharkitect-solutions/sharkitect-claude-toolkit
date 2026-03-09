# Writing Rules: Style, CSO & Content Patterns

## CSO (Claude Search Optimization)

### What CSO Is

CSO is the practice of writing skill descriptions so that Claude's internal matching
system loads the skill at the right time. It's the most critical factor in skill
effectiveness — a skill that never triggers is a skill that doesn't exist.

### The Cardinal Rule

**The description must contain ONLY triggering conditions. Nothing else.**

When Claude reads a description that summarizes what the skill does ("Implements retry
logic with exponential backoff, circuit breakers, and token bucket rate limiting"), it
treats that summary as sufficient context. It doesn't load the full body because the
description already told it what the skill contains.

This is a tested and proven failure mode. It was discovered by running the same skill
with two different descriptions:

- **Summary description**: Claude loaded the skill ~60% of the time but only read the
  body ~30% of the time. It used the summary as a proxy.
- **Trigger-only description**: Claude loaded AND read the body ~85% of the time.

### Description Format

Every sentence starts with "Use when...":

```yaml
description: >
  Use when [condition]. Use when a user says "[specific phrase]" or
  "[another phrase]". Use when [edge case that should still trigger].
  Keywords: term1, term2, term3.
```

### Good vs Bad Descriptions

**Bad (summarizes workflow):**
```
Implements production-grade API rate limiting, retry logic, and backoff strategies.
This covers exponential backoff with jitter, circuit breakers, token bucket rate
limiting, Retry-After header parsing, and per-provider patterns.
```

Why it fails: Claude reads this and thinks "I know what this covers — exponential
backoff, circuit breakers, etc." and doesn't load the body.

**Bad (lists features):**
```
Provides patterns for robust API consumption including retry mechanisms, backoff
strategies, client-side throttling, and provider-specific rate limit handling.
```

Why it fails: Same problem — it's a feature list, not a trigger list.

**Good (trigger conditions only):**
```
Use when writing code that calls any external API — REST, GraphQL, or SDK.
Use when adding error handling to existing API integration code.
Use when a user says "simple" or "quick" but the task involves HTTP requests.
Use when implementing batch processing, data migration, or any loop over API calls.
Keywords: 429, rate limit, Too Many Requests, retry, backoff, Retry-After.
```

Why it works: It tells Claude WHEN to load the skill, not WHAT the skill contains.
Claude must load the body to find out what to do.

**Best (trigger conditions + pushy + edge cases):**
```
Use when Claude writes code that calls external APIs — REST endpoints, third-party
SDKs, webhook triggers, or any outbound HTTP request. Use when a user mentions 429
errors, rate limiting, retry logic, backoff, throttling, or API failures under load.
Use when a user asks for a "quick script" or "simple function" that fetches from an
API — these are the highest-risk cases because Claude will rationalize skipping rate
limit handling. Use when integrating with OpenAI, Stripe, GitHub, AWS, or Twilio.
```

Why it's best: Covers trigger conditions, includes edge cases ("quick script"), names
specific providers, and is assertive about when it applies without summarizing content.

### Description Red Flags

If your description contains any of these words/phrases, it's probably summarizing
instead of triggering:

- "Implements..." / "Provides..." / "Covers..."
- "This skill..." / "This covers..."
- "Including..." / "Such as..."
- "Three-stage..." / "Multi-step..."
- "With patterns for..." / "With support for..."
- Any mention of the skill's internal sections or methodology

### The Pushiness Rule

From skill-creator research: descriptions should be "a little bit pushy" about when
they apply. If there's a reasonable chance the skill is relevant, the description should
claim it.

**Not pushy enough:**
```
Use when the user explicitly asks for retry logic.
```

**Appropriately pushy:**
```
Use when writing ANY code that calls an external API. Use when a user asks for a
"quick script" that fetches from an API — these are the highest-risk cases.
```

The key: pushy about TRIGGERING CONDITIONS, never about content.

## Body Writing Style

### Voice

Use imperative voice throughout. The skill is giving instructions, not suggestions.

| Don't | Do |
|---|---|
| You should consider using backoff | Use exponential backoff |
| It might be helpful to classify errors | Classify errors before retrying |
| You may want to check the Retry-After header | Always check the Retry-After header |
| Consider adding concurrency limits | Bound concurrency. Never use unbounded Promise.all |

### The "Why" Requirement

Every rule must include a brief explanation of WHY. Rules without reasons get ignored
under pressure because Claude can rationalize that "this rule doesn't apply here."

**Rule without why (weak):**
```
Always use exponential backoff with jitter.
```

**Rule with why (strong):**
```
Always use exponential backoff with jitter. Fixed delays either waste time (too long)
or cause retry storms (too short). Jitter prevents thundering herd — without it, all
clients retry at the exact same instant after a rate limit window resets.
```

The "why" makes the rule self-justifying. Under pressure, Claude can recall the reason
and resist the urge to skip it.

### Paragraph Length

Keep paragraphs to 3-4 sentences maximum. Long paragraphs lose attention. If a concept
needs more space, break it into sub-sections or move details to a reference.

### Tables Over Prose

When comparing options, listing conditions, or mapping decisions, use tables instead
of prose. Tables are:
- Scannable (Claude can find the relevant row quickly)
- Unambiguous (each cell has one meaning)
- Space-efficient (convey more information per word)

### Code Examples

For coding-focused skills:
- Show both WRONG and RIGHT patterns
- Label them clearly (`# WRONG: ...` and `# RIGHT: ...`)
- Keep examples minimal — just enough to show the pattern
- Use the most common language for your domain (Python + JavaScript covers most cases)
- Don't put full implementations in the body — those go in scripts/ or examples/

## Rationalization Table Design

### Why Tables Work

A rationalization table works because it names the excuse BEFORE Claude thinks of it.
When Claude encounters a situation where it would rationalize, the table pre-empts the
rationalization by saying "you're about to think X — here's why X is wrong."

### Three-Column Format

| Rationalization | When It Appears | Why It Is Wrong |
|---|---|---|

- **Column 1**: The exact phrase or thought Claude would use. Use quotes for verisimilitude:
  "The user said keep it simple"
- **Column 2**: The specific context that triggers this rationalization. This column is
  critical — it helps Claude recognize the situation in real time.
- **Column 3**: A concrete counterargument. Make it actionable and brief. Numbers help:
  "It's 5 lines of code" is better than "it's not much work."

### How Many Entries

- Minimum: 4 entries for any disciplinary skill
- Ideal: 6-8 entries covering the major pressure types
- Maximum: 10-12 (beyond that, the table itself becomes TL;DR)

### Common Rationalization Patterns

These appear across many skills. Adapt for your domain:

1. "The user said keep it simple" → Compliance with authority
2. "This probably won't need it" → Optimism bias
3. "One [safety measure] is enough" → Minimal compliance
4. "[Best practice] is overkill for this" → Pragmatic shortcutting
5. "It would clutter the code" → Aesthetic preference over correctness
6. "If it fails twice, something is really wrong" → Wrong heuristic

## Red Flags List Design

### Format

Use checkboxes for scannability:

```markdown
- [ ] [specific bad pattern]
- [ ] [specific bad pattern]
```

### Content

Each red flag should be:
- A specific, observable pattern (not a vague quality concern)
- Something Claude could check in its own output before submitting
- Ordered from most common to least common

**Bad red flag:** "Poor error handling"
**Good red flag:** "`try/catch` that treats all errors the same (no status code branching)"

### Quantity

- Minimum: 5 items
- Ideal: 7-10 items
- Maximum: 15 (beyond that, it becomes a checklist no one reads)

## Content Quality Markers

### Signs of Strong Skill Content

- Opens with WHY the skill exists (not what it does)
- Names Claude's default failure pattern explicitly
- Rules are imperative with "why" explanations
- Rationalization table addresses real (not hypothetical) failure modes
- Red flags are specific enough to pattern-match against code
- Code examples show both wrong and right patterns
- Body stays under 2,000 words with detail in references
- No hedging language anywhere

### Signs of Weak Skill Content

- Opens with a feature list or capability summary
- Reads like a reference manual (informative but not behavioral)
- Uses passive voice or hedging ("might", "consider", "you could")
- No rationalization table or red flags
- Rules without explanations
- Body over 2,500 words (trying to cover everything inline)
- Content duplicated between body and references
