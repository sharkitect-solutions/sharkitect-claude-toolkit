# Agent Dimension Examples

Concrete high/low scoring examples for each dimension. Use for calibration when unsure about a score.

---

## D1: Knowledge Delta Examples

### HIGH D1 (16-20): n8n-workflow-architect

```markdown
## MANDATORY Design Process - The Discovery-Design Pattern

### Phase 1: Intelligent Discovery (15-20 minutes of exploration)
// Think in capability clusters, not individual nodes
1. search_nodes("webhook") + search_nodes("http") + search_nodes("database") // Parallel
2. get_templates_for_task(primary_task) // Find proven patterns
3. search_templates(business_domain) // Domain-specific solutions

// API Integration Check - CRITICAL STEP
FOR each external API/service needed:
  result = search_nodes(api_name)
  IF result.length == 0:  // No dedicated node exists
    → STOP and delegate to api-integration-researcher
```

**Why high D1**: Claude doesn't know n8n's internal template system, MCP tool names, or the discovery-design pattern. This is genuinely novel procedural knowledge that changes how the subagent approaches workflow design.

### LOW D1 (3-5): Generic code-reviewer body

```markdown
## Best Practices for Code Review
- Check for code readability
- Look for potential bugs
- Verify error handling
- Check naming conventions
- Review test coverage
```

**Why low D1**: Claude already knows all of this from training. These are the first 5 things anyone would list for code review. Zero knowledge delta.

---

## D2: Mindset & Procedures Examples

### HIGH D2 (12-15): Expert decision tree

```markdown
## Scope Assessment (Before Starting ANY Review)

What is the review scope?
├─ Single file change
│  ├─ Under 50 lines → Inline review (focus: correctness + style)
│  └─ Over 50 lines → Check: should this be split into smaller changes?
│
├─ Multi-file feature
│  ├─ Touches tests? → Review tests FIRST (they document intent)
│  └─ No tests? → Flag immediately: "Missing test coverage for [specific behavior]"
│
└─ Architectural change
   ├─ Has design doc reference? → Review against design doc
   └─ No design doc? → STOP. Request design review before code review.
```

**Why high D2**: This is a decision tree that shapes thinking. An expert reviewer DOES assess scope before diving in. This changes the subagent's approach from "scan everything linearly" to "assess, then focus."

### LOW D2 (2-4): Bullet-list procedures

```markdown
## Review Process
- Read through the code carefully
- Note any issues you find
- Provide constructive feedback
- Suggest improvements where appropriate
- Summarize your findings
```

**Why low D2**: These are generic steps anyone would follow. No branching logic, no decisions, no expert thinking framework.

---

## D3: Anti-Pattern Quality Examples

### HIGH D3 (12-15): Named anti-patterns with WHY

```markdown
## NEVER Do These (Named Anti-Patterns)

### The Rubber Stamp
**What**: Approving changes without thorough review because the author is senior.
**Why it fails**: Senior developers make architectural mistakes just like juniors — but theirs are harder to catch because they look intentional. 40% of production incidents trace to "obvious" changes that nobody reviewed carefully.
**Fix**: Review every change against the same criteria regardless of author.

### The Status Novel
**What**: Writing multi-paragraph review comments that explain your thought process.
**Why it fails**: Authors read the first sentence and skim the rest. Long comments signal uncertainty. If you need a paragraph to explain why something is wrong, the issue is architectural (escalate) not reviewable.
**Fix**: One sentence per issue. Link to documentation for context. Escalate complex concerns.

### The Shotgun Review
**What**: Listing 20+ minor issues across every file without prioritization.
**Why it fails**: Authors get overwhelmed and fix nothing, or fix the easy ones and ignore the critical ones. Volume ≠ value.
**Fix**: Maximum 5 issues per review. Rank by severity. Prefix each with [CRITICAL], [IMPORTANT], or [SUGGESTION].
```

**Why high D3**: Named patterns ("The Rubber Stamp"), non-obvious reasoning (senior devs make harder-to-catch mistakes), and actionable fixes. These are things experience teaches.

### LOW D3 (0-3): Generic warnings

```markdown
- Avoid writing bad code
- Be careful with edge cases
- Don't skip testing
```

**Why low D3**: No names, no WHY, no specifics. "Avoid writing bad code" teaches nothing.

---

## D4: Spec Compliance Examples

### HIGH D4 (14-15): Complete spec compliance

```yaml
---
name: code-reviewer
description: >
  Use this agent when you need to conduct comprehensive code reviews focusing on
  code quality, security vulnerabilities, and best practices. Specifically:

  <example>
  Context: Developer submitted a PR with authentication changes.
  user: "Review this PR that refactors our auth system."
  assistant: "I'll use code-reviewer to examine the auth logic for security issues."
  <commentary>Code review with security focus triggers this agent.</commentary>
  </example>

  Do NOT use for: architect-reviewer (architectural consistency), security-auditor
  (dedicated security scanning), debugger (fixing bugs, not reviewing code).
tools: Read, Glob, Grep
model: sonnet
---
```

**Why high D4**: Has name, description with trigger conditions + examples + exclusions, tools list (appropriately scoped), model specified. Frontmatter is complete and well-structured.

### LOW D4 (3-6): Incomplete spec

```yaml
---
name: code-reviewer
description: "Expert code review agent"
---
```

**Why low D4**: Description is a 3-word summary (violates CSO rule). No trigger conditions, no examples, no exclusions. No tools declared. No model.

---

## D5: Description & Triggering Examples

### HIGH D5 (13-15): Full example coverage

```yaml
description: >
  Use this agent when... [trigger conditions]. Specifically:

  <example>
  Context: Developer has submitted a pull request with significant structural changes.
  user: "Please review the architecture of this new feature."
  assistant: "I will use the architect-reviewer agent to ensure the changes align."
  <commentary>Architectural reviews are critical for maintaining codebase health.</commentary>
  </example>

  <example>
  Context: Team is adding a new microservice to the system.
  user: "Can you check if this new service is designed correctly?"
  assistant: "I'll use the architect-reviewer to analyze service boundaries."
  <commentary>New services need boundary and dependency validation.</commentary>
  </example>

  <example>
  Context: After a production incident, team wants to prevent similar failures.
  user: "Review our error handling patterns across the payment module."
  assistant: "I'll use architect-reviewer to evaluate error handling architecture."
  <commentary>Post-incident architectural review is proactive use of this agent.</commentary>
  </example>

  Do NOT use for: code-reviewer (line-by-line code quality), security-auditor
  (security-specific scanning), debugger (finding and fixing specific bugs).
```

**Why high D5**: 3 examples with different contexts (PR review, new service, post-incident). Varied phrasings ("review architecture" / "check design" / "review patterns"). All have `<commentary>` explaining reasoning. Has exclusions listing 3 specific alternative agents.

### LOW D5 (0-3): No examples

```yaml
description: "Reviews code for architectural consistency and patterns."
```

**Why low D5**: Single sentence. No examples, no trigger conditions, no exclusions. Claude has no guidance on when to use this agent vs any other review-related agent.

---

## D7: Tool & Model Scoping Examples

### HIGH D7 (9-10): Minimum necessary tools

```yaml
# Read-only analysis agent
tools: Read, Glob, Grep
model: sonnet

# Body references:
# "Search the codebase for patterns" → needs Glob, Grep ✓
# "Read each file and analyze" → needs Read ✓
# No write operations mentioned → no Write, Edit, Bash ✓
```

**Why high D7**: Exactly the tools needed. Body-tool alignment is perfect. Model is appropriate (analysis needs sonnet, not haiku).

### LOW D7 (2-4): Over-permissioned

```yaml
# "Review agent" — but look at the tools:
tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Task, TodoWrite

# Body says:
# "Review the code and provide feedback"
# Never mentions writing files, running commands, searching web, or delegating
```

**Why low D7**: Agent has Write, Edit, Bash, WebSearch, WebFetch, Task — but its body only describes reading and reviewing. 6 unnecessary tools. This is a security and scope-creep risk.

---

## D8: Practical Usability Examples

### HIGH D8 (14-15): Structured output with edge cases

```markdown
## Output Format
Always structure your response as:

### Summary (2-3 sentences)
What was reviewed, overall assessment, and most critical finding.

### Findings (numbered list with severity)
1. **[CRITICAL]** [Finding] — [Impact] — [Fix]
2. **[IMPORTANT]** [Finding] — [Impact] — [Fix]
3. **[SUGGESTION]** [Finding] — [Impact] — [Fix]

### Recommendations (prioritized next steps)
1. [Highest priority action]
2. [Second priority action]

### Confidence Level
HIGH/MEDIUM/LOW with one-sentence reasoning.

## Edge Cases
- If the code is too large to review completely: state which portions were reviewed and flag the rest.
- If the code has no issues: still provide 1-2 suggestions for improvement. Never return "LGTM" alone.
- If the request is outside your scope: explicitly state what you cannot review and suggest the appropriate agent.
```

**Why high D8**: Structured output with clear headings, severity tiers, and actionable format. Edge cases handle realistic scenarios. Confidence level enables orchestrator routing.

### LOW D8 (2-5): No output structure

```markdown
Review the code and provide your analysis. Be thorough and helpful.
```

**Why low D8**: No output format. No edge cases. The subagent will return unstructured text that the orchestrator can't parse or route. Each invocation will produce different response structures.
