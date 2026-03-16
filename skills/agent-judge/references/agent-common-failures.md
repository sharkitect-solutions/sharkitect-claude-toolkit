# Agent Common Failure Patterns & Quick Reference

## The Four Agent Failure Patterns

### Pattern A: Bullet-List Body (~15 of 38 agents)
```
Symptom:  Body is 150-400 lines of bullet-point lists. Reads like meeting notes.
          Typical: "Key responsibilities:", "Best practices:", "Important considerations:"
Example:  debugger, business-analyst, scrum-master (~286 lines of bullets)
Score:    45-65 (D-F). D1:5-8, D2:3-7, D3:2-5
Root:     Author listed everything they know instead of teaching expert thinking
Fix:      Keep description (usually decent). Full body rewrite:
          - Replace bullet lists with decision trees and branching logic
          - Add 5-8 named anti-patterns with WHY + consequences
          - Add structured output format template
          - Add rationalization tables where appropriate
          - Target: <40% bullet ratio, >60% decision trees/tables/procedures
```

### Pattern B: Thin Agent (~12 of 38 agents)
```
Symptom:  Body is 15-80 lines. Often just a role statement + generic instructions.
          Typical: "You are an expert in X. Help the user with Y."
Example:  backend-architect (31 lines), customer-support (~40 lines)
Score:    25-55 (F). D1:2-5, D2:1-4, D3:0-2, D8:1-4
Root:     Created as placeholder, never fleshed out with expert content
Fix:      Full rebuild needed. Description AND body:
          - Write 3 <example> blocks with varied phrasings
          - Write 150-300 line body with expert decision trees
          - Add 5-8 named anti-patterns
          - Add structured output format
          - Add tool-body alignment
```

### Pattern C: Code-Heavy Agent (~4 of 38 agents)
```
Symptom:  Body is 400-935 lines, mostly code blocks and configuration examples.
          Code Claude could generate from training data alone.
Example:  test-engineer (935 lines), mcp-server-architect (~500 lines)
Score:    35-55 (F). D1:3-7 (code is redundant), D2:4-6, D7:3-5 (over-permissioned)
Root:     Author pasted reference code instead of teaching expert patterns
Fix:      Strip redundant code blocks (anything Claude can generate itself).
          Replace with:
          - Expert decision trees (WHEN to use which approach)
          - Named anti-patterns from production experience
          - Critical configuration gotchas (not the config itself)
          - Output format template
          - Target: 200-350 lines, <20% code blocks
```

### Pattern D: Strong Agent (2-3 of 38 agents)
```
Symptom:  150-350 lines, has examples, has some expert content, reasonable structure.
Example:  n8n-workflow-architect (337 lines), possibly agent-development
Score:    85-100 (C-B). Within striking distance of B gate.
Root:     Well-built but may lack polish: missing exclusions, incomplete anti-patterns,
          no output format, or description could have more example variety.
Fix:      Targeted polish only:
          - Add missing exclusions to description
          - Strengthen anti-patterns (name them, add WHY)
          - Add structured output format if missing
          - Verify tool-body alignment
          - Add 1-2 more example blocks if under 3
```

---

## Failure Pattern Detection Decision Tree

```
Read the agent → Check body line count
│
├─ < 80 lines → Pattern B (Thin)
│  Score prediction: 25-55 (F)
│  Strategy: Full rebuild
│
├─ 80-500 lines → Check bullet ratio
│  │
│  ├─ > 40% bullets → Pattern A (Bullet-list)
│  │  Score prediction: 45-65 (D-F)
│  │  Strategy: Keep description, rewrite body
│  │
│  └─ <= 40% bullets → Check content quality
│     │
│     ├─ Has decision trees + anti-patterns + output format → Pattern D (Strong)
│     │  Score prediction: 85-100 (C-B)
│     │  Strategy: Targeted polish
│     │
│     └─ Missing 2+ of above → Mixed (treat as A or B depending on gap)
│
└─ > 500 lines → Check code block ratio
   │
   ├─ > 30% code blocks → Pattern C (Code-heavy)
   │  Score prediction: 35-55 (F)
   │  Strategy: Strip code, add expert content
   │
   └─ <= 30% code → Likely Pattern A variant (verbose bullets)
      Strategy: Compress + rewrite
```

---

## Agent-Specific Scoring Traps

### Trap 1: Description Length ≠ Description Quality
A 500-word description can score D5=3 if it has no `<example>` blocks, no varied phrasings, and no exclusions. A 200-word description with 3 examples and commentary scores D5=13-15.

### Trap 2: Tool List Presence ≠ Tool Appropriateness
Having `tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Task` listed for a code-review agent is WORSE than having no tools specified, because it demonstrates lack of scoping discipline.

### Trap 3: Bullet Lists Can Look Expert
"Use dependency injection for loose coupling" looks expert but Claude knows this from training. The bullet-list format hides the redundancy. Convert to decision tree: "IF module has 3+ external dependencies AND is tested independently → DI. IF module is internal utility with 0-1 deps → direct instantiation."

### Trap 4: Code Examples Can Look Novel
A 50-line code block for setting up a webhook handler looks like expert content. But if Claude can generate the same code from a 1-sentence prompt, it's redundant (D1 = 0 for that section).

### Trap 5: n8n Cluster Agents Need Cross-Reference Check
The 7 n8n agents form a delegation chain. When scoring one, check whether it properly references its collaborators. An n8n-workflow-architect that never mentions delegating to n8n-workflow-builder is missing a core collaboration pattern.

---

## Quick Reference Checklist

```
AGENT EVALUATION QUICK CHECK

KNOWLEDGE DELTA (most important):
  [ ] No "What is X" explanations for basic concepts
  [ ] No step-by-step tutorials for standard operations
  [ ] Has decision trees for non-obvious choices
  [ ] Has trade-offs only practitioners would know
  [ ] Has edge cases from real-world experience
  [ ] E:A:R ratio is >60% Expert

DESCRIPTION & TRIGGERING (highest leverage):
  [ ] Has 3+ <example> blocks
  [ ] Examples use varied phrasings (not same words)
  [ ] Examples have <commentary> explaining WHY
  [ ] Has exclusions ("Do NOT use for...")
  [ ] Covers reactive + proactive scenarios (if appropriate)
  [ ] Description does NOT summarize workflow or content

BODY QUALITY:
  [ ] 150-350 lines (not too thin, not too bloated)
  [ ] < 40% bullet lists
  [ ] Has decision trees or branching logic
  [ ] Has structured output format template
  [ ] Has edge case handling

ANTI-PATTERNS:
  [ ] Has 5-8+ named anti-patterns
  [ ] Each has WHY (non-obvious consequences)
  [ ] Anti-patterns are specific, not vague warnings

TOOL & MODEL SCOPING:
  [ ] Tools are minimum necessary (least privilege)
  [ ] Model specified and appropriate
  [ ] Body references match available tools
  [ ] No over-permission (Bash for read-only agents)

SPEC COMPLIANCE:
  [ ] Valid YAML frontmatter (name, description, tools)
  [ ] name field matches filename stem
  [ ] description has trigger conditions + exclusions
```
