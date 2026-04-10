---
name: resource-auditor
description: "Use after completing ANY significant deliverable, task, or output in ANY workspace. Detects four gap types: (1) UNUSED -- available skills, docs, or tools that were relevant but not invoked, (2) PROCESS -- methodology skills not followed for the task type (brainstorming skipped for creative work, systematic-debugging skipped for bugs, writing-plans skipped for multi-step work), (3) MISSING -- no purpose-built resource exists and Claude had to improvise with general knowledge, (4) FALLBACK -- generic/adjacent resource used when a specialized tool would produce meaningfully better results. Reads tool usage journal to verify methodology compliance. Writes structured gap reports to the Skill Management Hub for permanent resolution. Do NOT use for: mid-task skill discovery (check ACTIVE_SKILLS in CLAUDE.md), content enforcement in HQ (use hq-content-enforcer), code review or testing (use code-reviewer or test-engineer agents)."
---

# Resource Auditor

Post-task self-audit detecting gaps between what resources SHOULD have been used and what WAS used. Universal across all workspaces.

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/gap-report-schema.md` | Writing a gap report, need field definitions and valid values | Just checking if gaps exist without writing reports |
| `references/resource-mapping-defaults.md` | Workspace CLAUDE.md lacks ACTIVE_SKILLS or task category not covered by installed skills | Workspace has comprehensive ACTIVE_SKILLS covering the task |
| `references/fallback-detection-guide.md` | Suspect a generic resource was used where specialized would be better, need signal patterns | Clear UNUSED or MISSING gap already identified |

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Audit what resources I used for this task" | YES | -- |
| "Check if I missed any skills" | YES | -- |
| "Write a gap report" | YES | -- |
| "What skills should I use for this task?" | NO | Check ACTIVE_SKILLS in CLAUDE.md |
| "Am I using brand voice correctly?" | NO | hq-content-enforcer + hq-brand-review |
| "Review this code for quality" | NO | code-reviewer agent |
| "Score this skill" | NO | skill-judge |

## The Four Gap Types

```
TASK COMPLETE
  |
  v
[1] UNUSED CHECK -- Did I have resources and NOT use them?
  |                  Skill existed, doc existed, tool existed -- skipped.
  |                  FIX TYPE: Enforcement (hook, CLAUDE.md rule)
  |
  v
[2] PROCESS CHECK -- Did I follow the right methodology?
  |                   Planning without brainstorming. Debugging without
  |                   systematic-debugging. Building without a plan.
  |                   FIX TYPE: Enforcement (protocol, hook)
  |
  v
[3] MISSING CHECK -- Did I improvise because nothing exists?
  |                   No skill, no doc, no tool for this need.
  |                   FIX TYPE: Creation (new skill, tool, companion)
  |
  v
[4] FALLBACK CHECK -- Did I use a generic substitute?
                      Used copywriting for API docs. Used general SEO
                      for local SEO. "It worked but wasn't ideal."
                      FIX TYPE: Specialization (new skill or companion)
```

## Audit Mindset

**Default assumption: you MISSED something.** Your job is to prove yourself innocent, not confirm you were right.

Three thinking traps that cause audits to fail:
- **Confirmation bias:** "I did good work, so I must have used the right tools." Challenge this. Trace each resource explicitly.
- **Availability bias:** "I can't think of what I missed, so nothing was missed." You can't see your own blind spots. That's why the audit checks ACTIVE_SKILLS mechanically, not from memory.
- **Satisficing:** "The output was good enough." Good enough for whom? Would a domain expert say the same? Would the user, if they knew a specialized skill existed, accept "I used general knowledge"?

**The acid test:** For every aspect of the output, can you name the SPECIFIC resource (skill, doc, tool) that informed it? If you can't -- that's a gap.

## Audit Procedure

### Step 1: Read Workspace Context

Read CLAUDE.md from the current workspace. Extract:
- **PROJECT_PURPOSE** -- what this workspace does
- **ACTIVE_SKILLS** -- what skills are designated for this workspace
- **Post-task checklist** -- any workspace-specific audit requirements

If CLAUDE.md lacks ACTIVE_SKILLS: load `references/resource-mapping-defaults.md` for default category-to-resource mappings.

### Step 2: Classify the Completed Task

Determine the work category: content, technical-content, code, automation, analysis, design, strategy, operations, data.

**Category traps -- when the obvious category is WRONG:**

| Task | Obvious Category | Actual Scope | What Gets Missed |
|---|---|---|---|
| Rewrite landing page | content | content + design + CRO + SEO | CRO skills, SEO optimization, design review |
| Build API endpoint | code | code + security + technical-content | Security review, API documentation skills |
| Create email sequence | content | content + automation + analysis | Email systems skill, analytics tracking |
| Set up monitoring | operations | operations + strategy | Architecture decisions about what to monitor |
| Redesign signup flow | design | design + CRO + code + data | signup-flow-cro, analytics tracking, form-cro |

**Rule:** If a task touches user-facing output AND technical implementation, it's ALWAYS multi-category. Audit each category separately.

### Step 3: UNUSED Check

For each ACTIVE_SKILL in the workspace CLAUDE.md:
1. Was this skill relevant to the task category?
2. If relevant -- was it actually invoked during this task?
3. If not invoked -- why? Legitimate skip or oversight?

**Legitimate skip reasons (NOT a gap):**
- Task was too small to warrant the skill (< 5 minutes of work)
- Skill covers a sub-aspect not present in this task
- User explicitly said to skip it

**Actual gap signals:**
- Skill directly maps to the task but wasn't invoked
- Output lacks qualities the skill would have provided
- User had to ask "did you use X?" after the fact

Also check for relevant KB docs, MCP tools, and companion files that should have been loaded.

### Step 3.5: PROCESS Check

Process gaps detect when methodology-appropriate skills were NOT invoked for the type of work performed. Unlike UNUSED (which checks workspace ACTIVE_SKILLS), PROCESS checks whether the right *approach* was followed.

**Read the tool usage journal:**
```python
import os, json, tempfile
journal_file = os.path.join(tempfile.gettempdir(), "claude_tool_usage_journal.jsonl")
invocations = []
try:
    with open(journal_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                invocations.append(json.loads(line))
except FileNotFoundError:
    invocations = []
skills_used = [e["skill"] for e in invocations if e.get("tool") == "Skill"]
agents_used = [e.get("subagent_type", "") for e in invocations if e.get("tool") == "Agent"]
```

**Process methodology matrix -- match task nature to expected skills:**

| Task Nature | Expected Skill | Gap If Missing |
|---|---|---|
| Creating a new feature, designing something, creative work | `brainstorming` (or `superpowers:brainstorming`) | Jumped to implementation without divergent thinking |
| Multi-step implementation requiring a plan | `writing-plans` (or `superpowers:writing-plans`) | Started coding without a structured plan |
| Bug, test failure, unexpected behavior | `systematic-debugging` (or `superpowers:systematic-debugging`) | Guessed at fixes instead of following diagnostic methodology |
| Executing a written plan | `executing-plans` (or `superpowers:executing-plans`) | Plan exists but execution wasn't structured |
| 2+ independent parallel tasks | `dispatching-parallel-agents` (or `superpowers:dispatching-parallel-agents`) | Sequential execution when parallel was possible |
| Completing a task (about to say "done") | `verification-before-completion` (or `superpowers:verification-before-completion`) | Claimed completion without verification |

**How to check:**
1. Determine the task nature from context (what did this session actually DO?)
2. Look up expected skills in the matrix above
3. Check if those skills appear in `skills_used`
4. If missing AND the task clearly matches the nature: **PROCESS gap**

**Legitimate skip reasons (NOT a PROCESS gap):**
- Task was trivially small (single file edit, quick lookup)
- User explicitly directed a different approach
- The methodology was followed manually without the skill (rare, but valid if traceable)

**PROCESS gap signals:**
- Built a feature without brainstorming -- no alternatives were considered
- Fixed a bug by trial-and-error without systematic-debugging
- Executed a 5-step plan without executing-plans structure
- Session involved 4 independent tasks done sequentially without parallel dispatch

**Report as:** gap_type `PROCESS`, fix_type `enforcement` (add protocol/hook to ensure invocation).

### Step 4: MISSING Check

For each aspect of the completed task, ask:
- Did I rely on general training knowledge for any domain-specific decision?
- Did I produce output that an expert would say "this is generic, not tailored"?
- Did I have to reason from first principles where a reference would have helped?

**MISSING signals:**
- "I applied general best practices" for a task with domain-specific requirements
- No installed skill covers this task category at all
- Output lacks industry-specific patterns, terminology, or standards
- Had to search the web for information a skill could have provided

### Step 5: FALLBACK Check

Load `references/fallback-detection-guide.md` if uncertain.

For each resource that WAS used:
- Was it the best-fit resource, or was it adjacent/generic?
- Would a more specialized resource produce meaningfully better output?
- Did the resource lack patterns specific to this task's domain?

**FALLBACK signals:**
- Used `copywriting` for technical documentation
- Used `seo-optimizer` for local SEO (lacks geo-targeting, NAP, service-area patterns)
- Used a general template where an industry-specific template would differ significantly
- The resource "worked" but required significant manual adaptation

### Step 6: Severity Classification

| Severity | Criteria | Action Timeline |
|---|---|---|
| **critical** | Output quality significantly impacted. Client/user would notice. | Address before next similar task |
| **warning** | Output functional but suboptimal. Expert would see the gap. | Address within current build cycle |
| **info** | Minor improvement opportunity. Output acceptable as-is. | Queue for future enhancement |

### Step 7: Write Gap Reports

For each gap found, write a structured JSON report.

**Report destination:** Read `~/.claude/config/skill-hub-path.txt` for the Skill Management Hub path. Write reports to `{skill-hub-path}/.gap-reports/inbox/`.

**Filename format:** `{date}_{workspace}_{brief-description}.json`

Load `references/gap-report-schema.md` for the complete field specification.

**CRITICAL:** Every gap report must include `recommended_fix` with enough detail that the Skill Hub can build the solution without re-investigating the problem. Include:
- Fix type (skill, hook, plugin, CLAUDE.md rule, or package)
- Specific description of what to build
- Component list (files to create/modify)

### Step 7.5: Read and Reset Edit Counter

The resource-audit-hook tracks Write/Edit operations on deliverable files and nudges every 5 edits. The counter only resets when this audit actually runs -- not on nudge. This means the counter value tells you how many edits happened and how many nudges were delivered but not acted on.

**Read the counter:**
```python
import os, tempfile
counter_file = os.path.join(tempfile.gettempdir(), "claude_resource_audit_counter.txt")
try:
    with open(counter_file, "r") as f:
        edit_count = int(f.read().strip())
except (FileNotFoundError, ValueError):
    edit_count = 0
nudges_delivered = edit_count // 5
```

**Include in gap reports:** Add these fields to every gap report JSON:
- `"edit_count_at_audit"`: the counter value when the audit ran
- `"nudges_delivered"`: how many nudge reminders were injected (edit_count // 5)
- `"nudges_acted_on"`: 0 (if this is the post-task audit and counter was never reset mid-task)

**Include in summary** (even when no gaps found): Report the counter value so the session has a record.

**Reset the counter AND journal after the audit completes:**
```python
try:
    os.remove(counter_file)
except FileNotFoundError:
    pass
try:
    os.remove(os.path.join(tempfile.gettempdir(), "claude_tool_usage_journal.jsonl"))
except FileNotFoundError:
    pass
```

**CRITICAL:** Always reset both files. If you skip this, the next task inherits stale counts and journal data becomes meaningless.

### Step 8: Report Summary

After writing all gap reports (or finding no gaps), produce a summary:

```
RESOURCE AUDIT COMPLETE
  Workspace: {workspace name}
  Task: {brief description}
  Edit counter: {edit_count} edits, {nudges_delivered} nudges delivered
  Tool journal: {N} skills invoked, {M} agents dispatched
  
  UNUSED gaps: {count} ({critical}/{warning}/{info})
  PROCESS gaps: {count} ({critical}/{warning}/{info})
  MISSING gaps: {count} ({critical}/{warning}/{info})  
  FALLBACK gaps: {count} ({critical}/{warning}/{info})
  
  Reports written to: {skill-hub-path}/.gap-reports/inbox/
  {list filenames}
```

If zero gaps found: "No resource gaps detected. All relevant resources were used appropriately. Edit counter: {edit_count} edits, {nudges_delivered} nudges delivered. Tool journal: {N} skills, {M} agents."

## Worked Example: Landing Page Rewrite in HQ

**Task completed:** Rewrote hero section and contact form for Sharkitect Digital website.

**Step 1 -- Context:** HQ CLAUDE.md shows ACTIVE_SKILLS includes hq-content-enforcer, hq-brand-review, page-cro, seo-optimizer, copywriting.

**Step 2 -- Category trap:** "Landing page rewrite" looks like `content` but is actually content + CRO + SEO + design. Must audit all four.

**Step 3 -- UNUSED check:**
- `hq-content-enforcer`: NOT invoked. **GAP.** This is the orchestrator -- skipping it means no brand guide loaded, no skill routing.
- `hq-brand-review`: NOT invoked. **GAP.** Client-facing content shipped without brand voice verification.
- `page-cro`: NOT invoked. **GAP.** Hero section has no conversion optimization.
- `seo-optimizer`: NOT invoked. **GAP (warning).** SEO matters but page isn't new -- existing URLs retain ranking.
- `copywriting`: Invoked. OK.

**Step 4 -- MISSING check:** No design review skill was available to check visual hierarchy. Used general knowledge. **FALLBACK candidate.**

**Step 5 -- FALLBACK check:** Used `copywriting` for form labels/microcopy. Copywriting is marketing-focused; form microcopy benefits from `form-cro` which has field-specific conversion patterns. **FALLBACK confirmed.**

**Step 6 -- Severity:** Brand review = critical (client would notice). CRO = critical. SEO = warning. Design = info.

**Result:** 3 UNUSED gaps (2 critical, 1 warning), 1 FALLBACK gap (warning). Reports written to `.gap-reports/inbox/`.

## Worked Example: Feature Build Without Methodology

**Task completed:** Built a new marketplace-scanner tool and evaluation workflow in Skill Hub.

**Step 3.5 -- PROCESS check:** Read tool usage journal. Skills invoked: none. Agents dispatched: none.

**Task nature:** Creating a new tool (creative work + multi-step implementation).

**Expected skills:**
- `brainstorming` -- new tool design has multiple valid approaches. Was it invoked? NO. **PROCESS gap.** Jumped straight to implementation without considering alternatives (web scraping vs API, scan frequency, report format options).
- `writing-plans` -- multi-file deliverable (tool + workflow + cron config). Was it invoked? NO. **PROCESS gap (info).** Task was small enough that a plan wasn't strictly needed, but structured execution would have caught the evaluation workflow being thin.

**Result:** 1 PROCESS gap (warning), 1 PROCESS gap (info). The tool works, but no evidence alternatives were considered. Future similar tasks should brainstorm before building.

## Anti-Patterns

| Name | What It Is | Why It Fails | Fix |
|---|---|---|---|
| **The Rubber Stamp** | Running audit but marking everything "no gaps" without checking | Defeats the purpose. Gaps go undetected, system doesn't improve | Actually trace each skill against the task. If you can't explain WHY a skill wasn't needed, it's a gap |
| **The Kitchen Sink** | Flagging every unused skill as a gap regardless of relevance | Floods inbox with noise. Real gaps get buried | Only flag skills that would have MEANINGFULLY changed the output |
| **The Vague Report** | Writing "could use a better skill" without specifics | Skill Hub can't build a fix from vague descriptions | Every report needs: what was needed, why existing resources fell short, what to build |
| **The Self-Forgiver** | "I used general knowledge and it was fine" without checking | The whole point is catching when "fine" could have been "excellent" | Compare output against what a specialized skill would have provided |
| **The Scope Creep** | Auditing tasks that haven't finished yet | Premature auditing produces false MISSING gaps | Only audit completed deliverables |
| **The Island** | Finding a gap and trying to fix it locally instead of reporting | Bypasses the Skill Hub's quality gate. Fix won't be available to other workspaces | Always write gap reports. Local workspaces don't build global artifacts |
| **The Methodology Dodger** | Got the right result without invoking the methodology skill (brainstorming, debugging, etc.) | No audit trail, pattern isn't reproducible, and "it worked this time" masks that alternatives weren't considered | If the task matched a methodology, invoke the skill even if you think you know the answer |

## Edge Cases

- **No CLAUDE.md in workspace:** Use `references/resource-mapping-defaults.md` for category mappings. Flag this as an info-level gap (workspace not properly bootstrapped).
- **skill-hub-path.txt missing:** Write gap reports to `.tmp/pending-gap-reports/` locally. Note that reports need manual delivery to Skill Hub.
- **Task spans multiple categories:** Audit each category separately. A landing page task touches content + design + SEO -- check resources for all three.
- **User explicitly chose not to use a skill:** Not a gap. Document in audit summary as "intentional skip per user direction."
- **Workspace has no ACTIVE_SKILLS:** Every skill is potentially relevant. Use default mappings. This itself is a warning-level gap (workspace needs skills evaluation).
