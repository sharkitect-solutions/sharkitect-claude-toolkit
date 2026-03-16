# Agent Scoring Calibration Guide

## Calibration Data from Agent Evaluations

This reference provides real-world scoring patterns specific to agents. Use when scoring to verify your scores align with established patterns.

---

## D1: Knowledge Delta Calibration for Agents

D1 varies by how well Claude's training data covers the agent's domain.

### Domain Saturation for Common Agent Types

| D1 Range | Agent Domain | Why | Example Agents |
|---|---|---|---|
| 15-18 | Proprietary tool-specific, n8n internals, MCP protocol | Near-zero coverage in training data | n8n-workflow-architect, mcp-server-architect |
| 12-14 | Specialized cross-domain (DevOps internals, security audit) | Partial coverage, expert nuance is novel | database-architect (with kernel-level content), test-engineer (with mutation testing) |
| 9-11 | Professional domains (project management, business analysis) | Well-documented but practitioner heuristics exist | project-manager, business-analyst |
| 6-8 | Heavily blogged (general code review, frontend dev) | Extensively covered in blog posts, tutorials | code-reviewer, frontend-developer |
| 3-5 | Standard practices thoroughly in training | Textbook content, common patterns | customer-support (generic), search-specialist |

### D1 Boosters for Saturated Domains

When an agent is in a D1<=8 domain, these techniques can push D1 higher:

| Technique | D1 Boost | Example |
|---|---|---|
| Cross-domain theory (behavioral economics, cognitive science) | +3-5 | CRO agent using loss aversion frameworks |
| Kernel/system-level internals | +4-6 | DevOps agent with cgroups, CFS bandwidth controller |
| Counterintuitive truths section | +2-4 | "Contrary to popular belief, X actually causes Y because..." |
| Named failure modes from production | +2-3 | "The Cascade Failure" with specific conditions and prevention |
| Quantified thresholds | +1-2 | "Above 200ms p99, switch from polling to SSE" |

### D1 Ceiling Warning

Agents in domains with D1<=6 typically max out at 85-90 total. To break through:
- Inject cross-domain content (behavioral science, systems theory, information theory)
- Add practitioner-only heuristics (things NOT in documentation)
- Include production failure analysis (real incident patterns)

---

## D5: Description & Triggering Calibration

D5 is the highest-leverage dimension for agents because description determines WHETHER the agent fires.

### D5 by Example Block Configuration

| Configuration | Typical D5 | Notes |
|---|---|---|
| No `<example>` blocks, 1-sentence description | 0-3 | Floor score. Agent triggering unreliable |
| No `<example>` blocks but detailed trigger conditions | 4-5 | Better but no phrasing variety |
| 1 example, no `<commentary>` | 4-6 | Shows one phrasing but doesn't explain reasoning |
| 2 examples, with `<commentary>`, reactive only | 7-9 | Good but missing proactive/edge scenarios |
| 3 examples, reactive + proactive, `<commentary>`, no exclusions | 10-12 | Strong but no negative boundary |
| 3-4 examples, reactive + proactive + edge case, exclusions, all with `<commentary>` | 13-15 | Target configuration |

### D5 Scoring Traps

| Trap | What Happens | Correction |
|---|---|---|
| Long description = high D5 | 500 words without examples still scores D5=3-5 | Examples + variety matter, not length |
| Same phrasing repeated | 3 examples all say "review my code" | Different words for same intent: "check changes", "look over PR", "audit this module" |
| Commentary restates obvious | "This triggers the agent" | Commentary should explain WHY this agent and NOT another |
| Missing exclusions | No "Do NOT use for..." | With 38 agents, overlap is inevitable. Exclusions prevent mis-routing |
| Proactive examples missing | Only reactive ("user asks...") | Proactive: "After code is written, before commit" context |

---

## D7: Tool & Model Scoping Calibration

D7 is agent-unique (skills don't have tool scoping).

### Common Tool Scoping Patterns

| Agent Type | Correct Tools | Over-Permissioned Example | Score Impact |
|---|---|---|---|
| Code reviewer | Read, Glob, Grep | + Write, Edit, Bash | -3 points (read-only agent with write access) |
| Debugger | Read, Write, Edit, Bash, Glob, Grep | + WebSearch, Task | -1 point (unnecessary breadth) |
| Research agent | Read, Glob, Grep, WebSearch, WebFetch | + Bash, Write | -2 points (research shouldn't execute) |
| Coordinator | Read, Glob, Grep, Task | + Write, Edit, Bash | -2 points (coordinators delegate, not execute) |
| Full-stack dev | Read, Write, Edit, Bash, Glob, Grep | Correct as-is | 0 (needs full access) |

### Model Selection Calibration

| Agent Complexity | Correct Model | Wrong Model | Score Impact |
|---|---|---|---|
| Simple classification/formatting | haiku | opus | -2 points (cost waste) |
| Most analysis/generation tasks | sonnet or inherit | haiku | -1 point (underpowered) |
| Complex multi-step reasoning | opus | haiku | -3 points (model can't handle task) |
| Default (no strong reason) | inherit (omit field) | - | 0 (acceptable default) |

### Body-Tool Alignment Check

Read the body. For each action the body instructs the agent to do, verify the tool exists:

| Body Instruction | Required Tool | If Missing |
|---|---|---|
| "Search the codebase for..." | Glob, Grep | -2 from D7 |
| "Read the file at..." | Read | -2 from D7 |
| "Write/create a file..." | Write | -3 from D7 |
| "Run the test suite..." | Bash | -3 from D7 |
| "Delegate to specialist agent..." | Task | -3 from D7 |
| "Search the web for..." | WebSearch | -2 from D7 |
| "Read MEMORY.md for context..." | Read | -1 from D7 |

---

## Common Scoring Errors

### Arithmetic Errors (Most Common)

After scoring all 8 dimensions, ALWAYS verify:
```
D1 + D2 + D3 + D4 + D5 + D6 + D7 + D8 = Total
```

Common mistakes:
- D7 max is **10**, not 15. Adding 15 instead of 10 inflates by 5 points.
- Transposing D5 and D7 scores (confusing description quality with tool scoping)
- Forgetting to include D7 (smallest dimension, easy to skip)

**Verification method**: Add in pairs -- (D1+D2) + (D3+D4) + (D5+D6) + (D7+D8) = Total

### Agent-Specific Inflation Patterns

| Pattern | What Happens | Correction |
|---|---|---|
| **n8n agent bias** | n8n agents get inflated because they're domain-specific | Domain-specificity helps D1, but bullet lists still tank D2. Score each dimension independently |
| **Description length bias** | Long descriptions get high D4/D5 | Length ≠ quality. Check for examples, variety, exclusions |
| **Tool list credit** | Agents with long tool lists get D7 credit | More tools = more risk. Score for MINIMUM necessary tools |
| **Body size credit** | 300-line body assumed to be expert content | Could be 300 lines of bullets. Check content type, not line count |

### Agent-Specific Deflation Patterns

| Pattern | What Happens | Correction |
|---|---|---|
| **Thin agent auto-fail** | All thin agents scored F across all dimensions | Even thin agents can have good descriptions (D4/D5 may be 8-12) |
| **Generic domain penalty** | "Code reviewer" sounds generic = low D1 | Check if the body adds genuine review frameworks beyond "check for bugs" |
| **Missing model penalty** | No model specified → D7 penalty | Omitting model to inherit parent's is an acceptable choice (0-1 point penalty max) |

---

## Dimension Interaction Patterns for Agents

| Pattern | Why | Implication |
|---|---|---|
| High D1 + low D3 | Expert knowledge without anti-patterns is incomplete | If D1>=12 but D3<=5, anti-patterns were likely overlooked |
| High D5 + low D4 | Good examples but weak spec compliance | Check frontmatter: tools missing? Model missing? |
| High D2 + high bullet ratio | Contradiction: good procedures shouldn't be bullets | Re-evaluate D2: are the "procedures" really just lists? |
| Low D5 + high everything else | Good agent nobody uses | Description is the bottleneck. All other optimization is wasted. |
| D7=10 is rare | Most agents have at least 1 unnecessary tool | D7=9 is strong. D7=10 requires demonstrable minimum toolset |

---

## Score Distribution Expectations (38 agents, pre-optimization)

Based on structural pre-analysis:

| Score Range | Expected Count | Typical Profile |
|---|---|---|
| 85-100 (C to B) | 2-3 | Pattern D agents (well-built, need polish) |
| 60-84 (D+ to C) | 5-8 | Pattern A agents (decent description, bullet body) |
| 40-59 (F) | 10-15 | Pattern A/B mix (weak body, some with descriptions) |
| 0-39 (F) | 12-18 | Pattern B/C agents (thin or code-heavy) |

Post-optimization target: ALL 38 agents at 96+ (B gate).
