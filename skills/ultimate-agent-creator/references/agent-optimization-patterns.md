# Agent Optimization Patterns

Proven patterns from optimizing 38 agents across 4 failure types. Use when rewriting existing agent bodies or strengthening weak content.

---

## Pattern A Fix: Bullet-List Body Rewrite

**Diagnosis**: Body is 150-400 lines of bullet lists. Looks thorough but produces generic output because Claude already knows bullet-list content from training.

### Before (Pattern A)

```markdown
## Code Review Best Practices
- Check for code readability
- Look for potential bugs
- Verify error handling
- Check naming conventions
- Review test coverage
- Ensure proper documentation
- Look for security vulnerabilities
- Check performance implications
```

### After (Expert Decision Tree)

```markdown
## Review Scope Assessment

What changed?
├─ Single file, <50 lines
│  └─ Inline review: correctness + style only
├─ Single file, >50 lines
│  └─ Check: should this be split? If yes, flag before reviewing.
├─ Multi-file feature
│  ├─ Has tests? → Review tests FIRST (they document intent)
│  └─ No tests? → Flag: "Missing test coverage for [behavior]"
└─ Architectural change
   ├─ Has design doc? → Review against doc
   └─ No design doc? → STOP. Request design review first.

## Severity Classification

How bad is this issue?
├─ CRITICAL: Will cause data loss, security breach, or production outage
│  → Must fix before merge. Block the PR.
├─ IMPORTANT: Will cause bugs, performance issues, or maintenance burden
│  → Should fix before merge. Negotiate if time-pressured.
├─ SUGGESTION: Could be better but works correctly
│  → Note it. Don't block merge.
└─ NIT: Style preference, not a real issue
   → Skip it. Nits waste review capital.
```

### Conversion Rules

| Bullet Pattern | Convert To |
|---|---|
| List of things to check | Decision tree with conditions |
| List of best practices | Table with WHEN to apply each |
| List of steps | Conditional procedure with branching |
| List of tools/technologies | Decision matrix (WHEN to use which) |

---

## Pattern B Fix: Thin Agent Full Rebuild

**Diagnosis**: Body is 15-80 lines. Usually just a persona statement + generic instructions.

### Rebuild Sequence

1. **Research the domain**: What does an expert in this field know that Claude doesn't?
2. **Write the decision framework first**: What's the first decision the agent makes?
3. **Add 5-8 named anti-patterns**: What mistakes does inexperience cause?
4. **Add output format**: What should the single-message response look like?
5. **Add edge cases**: What unusual inputs break the happy path?
6. **Verify line count**: Target 200-300 lines.

### Thin-to-Expert Content Sources

| Content Type | How to Generate | Example |
|---|---|---|
| Decision trees | "What's the first question an expert asks?" | Scope assessment tree |
| Named anti-patterns | "What mistakes do juniors make that experts never do?" | "The Rubber Stamp", "The Shotgun Review" |
| Quantified thresholds | "At what point does the expert change approach?" | "Above 200ms p99, switch from polling to SSE" |
| Cross-domain insights | "What adjacent field knowledge applies here?" | Behavioral economics in CRO, systems theory in architecture |
| Production heuristics | "What does the expert check that documentation doesn't mention?" | "If the error message says X, it's always actually Y" |

---

## Pattern C Fix: Code-Heavy Compression

**Diagnosis**: Body is 400-935 lines, mostly code blocks. Code that Claude can generate from training data alone.

### Compression Decision Tree

```
For each code block in the body:
├─ Could Claude generate this from a 1-sentence prompt?
│  ├─ YES → DELETE the code block
│  │  └─ Replace with: "Generate [X] using [Y framework]. Critical: [gotcha]."
│  └─ NO → KEEP but verify it's genuinely novel
│
├─ Is it a configuration example?
│  ├─ Standard config → DELETE
│  └─ Config with non-obvious gotchas → KEEP only the gotcha parts
│
└─ Is it an integration pattern?
   ├─ Standard pattern → DELETE
   └─ Pattern with provider-specific quirks → KEEP the quirk, delete the boilerplate
```

### Target After Compression

| Before | After | What Changed |
|---|---|---|
| 935 lines, 60% code | 250 lines, 15% code | Stripped redundant code, added decision trees |
| 500 lines, 40% config examples | 200 lines, 10% config | Kept gotchas only, added anti-patterns |
| 400 lines, 50% tutorials | 180 lines, 5% code | Replaced tutorials with expert heuristics |

---

## Pattern D Fix: Targeted Polish

**Diagnosis**: 150-350 lines with good structure. Near B gate but missing specific elements.

### Common D-Pattern Gaps

| Missing Element | D Impact | Fix Time |
|---|---|---|
| Exclusions in description | D4: -3, D5: -2 | 10 min -- add "Do NOT use for..." |
| Output format template | D8: -5 to -8 | 15 min -- add structured format section |
| Named anti-patterns (has some but <5) | D3: -3 to -5 | 20 min -- add 2-3 more with WHY |
| `<example>` block variety | D5: -3 to -5 | 15 min -- add 1-2 more examples with different phrasings |
| Model not specified | D7: -1 to -2 | 2 min -- add model: sonnet (or appropriate) |
| Memory injection missing | D8: -1 | 5 min -- add 2-line MEMORY.md instruction |

---

## Cross-Domain D1 Injection

When the agent's domain is saturated (Claude already knows it well), inject cross-domain expert content to boost knowledge delta.

### Proven Cross-Domain Pairs

| Agent Domain | Cross-Domain Injection | D1 Boost |
|---|---|---|
| Code review | Code review science (cognitive load theory, attention fatigue curves) | +3-4 |
| Project management | Theory of Constraints, Little's Law, Goodhart's Law | +3-5 |
| DevOps/deployment | Kernel internals (cgroups, CFS bandwidth controller, namespace mechanics) | +4-6 |
| CRO/conversion | Behavioral economics (loss aversion, anchoring, IKEA effect) | +3-4 |
| Security audit | Attack graphs from academic security research, MITRE ATT&CK beyond basics | +3-5 |
| Database design | Storage engine internals (B-tree vs LSM, WAL mechanics, vacuum strategies) | +3-5 |

### How to Apply

1. Identify the domain saturation level (use D1 calibration from agent-judge)
2. Select 1-2 cross-domain areas that genuinely improve the agent's decision-making
3. Write a "Counterintuitive Truths" or "Expert Heuristics" section (10-20 lines)
4. Ensure the cross-domain content is ACTIONABLE, not just interesting trivia

---

## Named Anti-Pattern Design

### Anatomy of a Good Anti-Pattern

```markdown
### The [Memorable Name]
**What**: [1-sentence description of the bad behavior]
**Why it fails**: [Non-obvious consequence -- not "it's bad"]
**Frequency**: [Common/Occasional/Rare]
**Fix**: [Specific, actionable correction]
```

### Anti-Pattern Quality Tiers

| Tier | Example | D3 Impact |
|---|---|---|
| Vague warning | "Avoid writing bad code" | 0 points |
| Specific but unnamed | "Don't approve PRs without reading all files" | +1 point |
| Named without WHY | "The Rubber Stamp: Approving without reading" | +1.5 points |
| Named with WHY | "The Rubber Stamp: Approving senior devs' code without review. Fails because senior devs make harder-to-catch architectural mistakes." | +2 points |
| Named + WHY + quantified | "The Rubber Stamp: ... 40% of production incidents trace to 'obvious' changes nobody reviewed." | +2.5 points |

### Universal Agent Anti-Patterns (add to any agent)

| Anti-Pattern | Applies To | WHY |
|---|---|---|
| The Scope Creep | Agents that fix/modify things | Agent does more than asked, breaking unrelated code |
| The Confidence Facade | Analysis/review agents | Reports HIGH confidence without acknowledging limitations |
| The Generic Response | All agents | Returns boilerplate instead of context-specific analysis |
| The Missing Context | Agents that don't read MEMORY.md | Repeats mistakes or contradicts prior decisions |
| The Tool Stampede | Agents with many tools | Uses powerful tools (Bash, Write) when simpler tools suffice |

---

## Output Format Templates

### Analysis Agent Template

```markdown
## Output Format
### Summary (2-3 sentences)
What was analyzed, overall assessment, critical finding.

### Findings
1. **[CRITICAL]** [Finding] -- [Impact] -- [Recommended action]
2. **[IMPORTANT]** [Finding] -- [Impact] -- [Recommended action]
3. **[SUGGESTION]** [Finding] -- [Impact] -- [Optional improvement]

### Recommendations (prioritized)
1. [Highest priority -- do this first]
2. [Second priority]
3. [Third priority]

### Confidence: HIGH/MEDIUM/LOW
[1 sentence explaining confidence level and any caveats]
```

### Creation Agent Template

```markdown
## Output Format
### What Was Created
[File paths and brief descriptions]

### Key Decisions Made
| Decision | Choice | Reasoning |
|---|---|---|

### Testing Recommendations
1. [How to verify the creation works]
2. [Edge cases to test]

### Known Limitations
[What this creation doesn't handle]
```

### Coordination Agent Template

```markdown
## Output Format
### Plan Overview (2-3 sentences)
### Delegation Map
| Agent | Task | Expected Output |
|---|---|---|

### Execution Order
1. [First -- because X depends on nothing]
2. [Second -- depends on step 1 output]
3. [Third -- can run parallel with step 2]

### Risk Points
- [What could fail and contingency]
```
