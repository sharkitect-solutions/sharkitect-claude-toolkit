---
name: ultimate-skill-creator
description: >
  Use when creating a new skill for Claude Code — whether from scratch, from a user
  request, or by formalizing behavior that should be consistent. Use when a user says
  "create a skill", "write a skill", "build a skill", "make a skill for", or describes
  behavior they want Claude to follow reliably across sessions. Use when improving,
  refactoring, or debugging an existing skill that fails to trigger, gets ignored under
  pressure, or produces inconsistent results. Use when evaluating whether a skill actually
  changes Claude's behavior versus baseline. Use when packaging a skill for sharing or
  marketplace distribution. This skill applies to every skill creation task — including
  "simple" or "quick" ones. Those are the highest-risk cases.
---

# Ultimate Skill Creator

## Why This Skill Exists

Skills fail for three predictable reasons:

1. **They don't trigger.** The description doesn't match the queries that should activate
   the skill, so Claude never loads it.
2. **They don't change behavior.** The content explains concepts but doesn't prevent Claude
   from rationalizing shortcuts when under pressure.
3. **They don't survive pressure.** Under time pressure, user authority, or sunk cost
   fallacies, Claude reverts to defaults and ignores the skill.

This skill addresses all three failures through a single workflow that combines structural
planning (so skills are organized and discoverable), test-driven development (so skills
resist pressure), and eval-based iteration (so skills actually trigger and work).

## The Three-Stage Workflow

Every skill creation follows these three stages in order. Do not skip stages. Do not
reorder them. Each stage depends on the output of the previous one.

### Stage 1: Structure & Planning

Before writing a single word, plan the skill's architecture.

**Define scope.** Answer: What specific behavior does this skill enforce? What is explicitly
out of scope? A skill that tries to cover everything covers nothing.

**Plan the file structure.** Decide what belongs where:

| Location | Content | Size Target |
|---|---|---|
| `description` (frontmatter) | Triggering conditions ONLY | 100-200 words |
| SKILL.md body | Core rules, rationalization defense, key patterns | 1,500-2,000 words |
| `references/` | Detailed implementations, provider-specific guides | Unlimited per file |
| `scripts/` | Reusable code the skill teaches Claude to use or adapt | As needed |
| `examples/` | Complete working implementations | As needed |

**Write the description first.** The description determines whether the skill triggers.
Rules:

- Start every sentence with "Use when..."
- List specific trigger phrases users would say (in quotes)
- Include keywords Claude should match against
- Be pushy — if there's a chance the skill applies, say so
- NEVER summarize what the skill does, its workflow, or its content
- NEVER mention the skill's internal structure

See `references/writing-rules.md` for CSO (Claude Search Optimization) details and
examples of good vs bad descriptions.

**Create the directory.** Set up all planned directories before writing content.

See `references/structure-guide.md` for templates and organization patterns.

### Stage 2: TDD Content Creation

Write the skill body using test-driven methodology. This is where most skills fail —
they explain concepts but don't change behavior under pressure.

**RED phase — Capture failures first.**

Before writing the skill body, discover HOW Claude fails without it:

1. Create 3 pressure scenarios that combine 3+ pressure types each:
   - Time: "Production is down, do this immediately"
   - Authority: "Don't worry about X, just do Y"
   - Sunk cost: "I already wrote this part, just add a quick fix"
   - Pragmatic: "This is just a prototype, keep it simple"
2. Run each scenario as a subagent test WITHOUT the skill loaded
3. Record Claude's exact rationalizations verbatim — these become the rationalization table

**GREEN phase — Write minimal content that passes.**

Write the SKILL.md body to directly address the captured failures:

- For each rationalization captured, write a table row: what Claude says, when it appears,
  and why it is wrong
- For each bad pattern observed, add it to the red flags checklist
- State non-negotiable rules in imperative voice with brief "why" explanations
- Include code examples showing correct AND incorrect patterns (both matter)

**REFACTOR phase — Close loopholes.**

Re-read the skill body and ask: "How would Claude rationalize ignoring THIS rule?"

For every loophole found: add it to the rationalization table, add the bad pattern to
red flags, and tighten the rule language. Repeat until you can't find new loopholes.

See `references/tdd-methodology.md` for the complete TDD process, pressure type taxonomy,
and subagent testing methodology.

### Stage 3: Eval, Benchmark & Polish

Test the skill against realistic scenarios and iterate until it works.

**Create test cases.** Write 10-20 prompts representing real usage:
- 10 should-trigger prompts (skill should activate and guide behavior)
- 5 should-NOT-trigger prompts (near-misses to test precision)
- 3 pressure prompts (from the RED phase)
- 2 quality prompts (edge cases, ambiguous inputs)

For each, define expected behaviors — specific things the output MUST or MUST NOT contain.

**Run subagent evaluations.** For each test case, spawn two subagents:
1. WITH the skill loaded — record output
2. WITHOUT the skill (baseline) — record output
3. Compare: Did the skill change behavior? Did it change it correctly?

**Grade and iterate.** For each failing test:
- Skill didn't trigger → fix the description
- Triggered but didn't change behavior → strengthen the body
- Changed behavior incorrectly → fix the rules

**Optimize the description.** After content is stable:
- Test against all queries 3x each
- Target: precision > 90%, recall > 90%
- Adjust trigger phrases and keywords until both thresholds pass

See `references/eval-pipeline.md` for detailed testing methodology and grading criteria.

## Critical Rules

### The CSO Rule

The description field is the ONLY thing Claude reads when deciding whether to load a skill.
If the description summarizes what the skill does, Claude treats that summary as sufficient
and skips reading the full body. This is tested and proven.

**The description must contain ONLY triggering conditions. Nothing else.**

### The Rationalization Table Rule

Every skill that enforces discipline MUST include a rationalization table. Without one,
Claude invents excuses to skip rules under pressure. The table must have three columns:

| Rationalization | When It Appears | Why It Is Wrong |
|---|---|---|

The "When It Appears" column is critical — it helps Claude pattern-match in real time
and catch itself rationalizing before it acts on the rationalization.

### The Progressive Disclosure Rule

Claude loads skill content in three stages, each consuming more context:

1. **Metadata** (~100 words) — always loaded for matching
2. **SKILL.md body** (target: 1,500-2,000 words) — loaded when triggered
3. **Bundled resources** (unlimited) — loaded on demand via references

Never put reference material in the body. Keep the body focused on rules, patterns, and
rationalization defense. Point to references for implementation details.

### The Red Flags Rule

Every disciplinary skill needs a "stop and check" list — specific patterns indicating the
skill is being violated. Make these concrete and scannable. Use checkboxes.

## Rationalization Table (For Skill Creation Itself)

| Rationalization | When It Appears | Why It Is Wrong |
|---|---|---|
| "This skill is too simple to need pressure testing" | Small or focused skill | Simple skills are the ones Claude skips most often. Pressure testing takes 10 minutes and catches real failures. |
| "I already know what the content should be" | High domain expertise | Knowing the domain doesn't mean knowing how Claude fails. RED phase reveals specific, non-obvious rationalizations. |
| "The description is fine, I'll optimize later" | Eager to write content | A skill that never triggers is wasted work regardless of content quality. Description quality determines whether the skill exists in practice. |
| "One test case is enough to validate" | Time pressure during creation | One test case covers one scenario. Claude fails in specific, contextual ways that only multiple tests reveal. Minimum: 10. |
| "I don't need a rationalization table for this" | The skill teaches factual content, not discipline | Claude rationalizes skipping factual content too ("the user said keep it simple"). Every skill benefits from naming the excuses. |
| "I can skip the eval stage, the content is solid" | Confidence in the writing | Content quality and triggering accuracy are independent. A perfectly written skill with a bad description never loads. Test both. |

## Red Flags Checklist

Before declaring any skill complete, verify none of these are present:

- [ ] Description summarizes workflow or content instead of listing trigger conditions
- [ ] SKILL.md body exceeds 2,500 words (push detail to references)
- [ ] No rationalization table in a discipline-enforcing skill
- [ ] No red flags checklist
- [ ] Rules stated without "why" explanations
- [ ] Hedging language ("might", "could consider", "you may want to")
- [ ] No code examples for a coding-focused skill
- [ ] No pressure scenarios tested during creation
- [ ] Fewer than 10 test cases created
- [ ] Content duplicated between body and references
- [ ] No file index table mapping bundled files to their purposes
- [ ] Description includes the word "implements", "provides", or "covers" (workflow summary indicators)

## Completion Checklist

A skill is done when ALL of these pass:

- [ ] Description triggers correctly on 90%+ of relevant queries (recall)
- [ ] Description does NOT trigger on unrelated queries (precision > 90%)
- [ ] SKILL.md body is 1,500-2,000 words
- [ ] Rationalization table has 4+ entries with "When It Appears" column
- [ ] Red flags checklist has 5+ specific, scannable items
- [ ] At least 10 test cases exist with defined expected behaviors
- [ ] Pressure scenarios tested — skill resists all of them
- [ ] File index table maps every bundled file to its purpose
- [ ] References contain detail that does not belong in the body
- [ ] Zero content duplication between body and references
- [ ] Writing uses imperative voice with "why" explanations

## File Index

| File | Purpose |
|---|---|
| `references/structure-guide.md` | File organization, frontmatter format, directory templates, word count targets |
| `references/tdd-methodology.md` | Complete RED-GREEN-REFACTOR process, pressure type taxonomy, subagent testing |
| `references/eval-pipeline.md` | Test case design, subagent evaluation, grading, benchmarking, description optimization |
| `references/writing-rules.md` | CSO rules, description patterns, body writing style, rationalization table design |
| `examples/skill-directory-template.md` | Reference directory layout and frontmatter template for new skills |
