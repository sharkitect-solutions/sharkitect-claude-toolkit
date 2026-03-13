---
name: executing-plans
description: Use when you have a written implementation plan file to execute in a session with human review checkpoints between batches. NEVER use when no written plan exists, when the task is exploratory or open-ended, or when no clear stop-and-report structure has been agreed upon.
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Executing Plans

## Core Principle

Batch execution with checkpoints for architect review. Follow the plan exactly. Report between batches. Stop when blocked.

## The Process

### Step 1: Load and Review Plan

1. Read the plan file in full before touching any code or files
2. Review critically -- identify questions, ambiguities, or gaps
3. If concerns exist: raise them with your human partner before starting
4. If no concerns: create TodoWrite with all tasks and proceed

### Step 2: Calibrate Batch Size

Default batch size is 3 tasks. Adjust based on task complexity:

| Task Type | Batch Size | Reason |
|-----------|-----------|--------|
| Simple file moves, renames, config edits | 5-8 | Low risk, easy to reverse |
| Standard feature work with tests | 3 | Default -- balanced risk |
| Complex logic, multiple interacting systems | 2 | Errors compound quickly |
| Infrastructure, database migrations, deploys | 1 | Each step must be verified before next |

### Step 3: Execute Batch

For each task in the batch:

1. Mark task as in_progress in TodoWrite
2. Follow each step in the plan exactly -- do not improvise or improve
3. Run verifications as specified in the plan
4. If no verification is specified: write one before executing the task
5. Compare verification output to expected result
6. If output differs from expected: STOP -- do not proceed to next task
7. Mark task as completed only after verification passes

### Step 4: Report

When the batch is complete:

- List what was implemented (one line per task)
- Show verification output for each task
- Note any deviations from the plan, even minor ones
- Ask for feedback before proceeding

### Step 5: Continue

Based on feedback:

- Apply any corrections needed
- Execute the next batch using the same calibrated batch size
- Repeat Steps 3-5 until all tasks are complete

### Step 6: Complete Development

After all tasks are complete and verified:

- **REQUIRED SUB-SKILL:** Invoke superpowers:finishing-a-development-branch
- Follow that skill to verify tests, present options, and execute the chosen completion path

## When to Stop and Ask for Help

Stop executing immediately when:

- A blocker is hit mid-batch (missing dependency, failing test, unclear instruction)
- The plan has critical gaps that prevent starting a task
- An instruction is ambiguous and interpretation could go wrong
- Verification fails and the cause is not obvious
- Drift is detected (see below)

Ask for clarification rather than guessing. A wrong interpretation compounds across every subsequent task.

## Drift Detection

Drift means execution is diverging from the written plan. Stop and report when:

- You are writing code not described in the plan
- You are modifying files not listed in the plan
- The approach feels different from what was planned
- Tests are failing in ways the plan did not anticipate
- You are making judgment calls the plan did not authorize

Drift is not always bad -- but it must be surfaced, not silently absorbed.

## When to Return to Review

Return to Step 1 (full plan re-read) when:

- The human partner updates the plan based on your feedback
- A blocker reveals that the fundamental approach needs rethinking
- More than 2 tasks in a batch fail verification

Do not force through blockers. Stop and ask.

## Anti-Patterns

Common failures during plan execution:

- Skipping verification steps to move faster -- verification exists to catch errors early, not slow you down
- Silently fixing plan errors instead of reporting them -- the plan is the source of truth; deviations need human approval
- Batching too many tasks when complexity is high -- a failing task mid-batch wastes all prior work in that batch
- Continuing past a failing verification -- the next task likely depends on the current one succeeding
- Adding improvements not in the plan -- scope creep breaks the checkpoint model and introduces unreviewed changes
- Interpreting ambiguous instructions rather than asking -- wrong interpretations compound silently across batches

---

## Rationalization Table

| Rationalization | Why It Is Wrong |
|----------------|----------------|
| "The plan step is obvious, I can infer what it means." | Ambiguity in plans is a signal to stop and ask, not to interpret. Wrong interpretations compound across all subsequent tasks. |
| "I'll skip verification this once since the change is small." | Small changes have broken large systems. The verification step exists precisely for changes that seem safe. |
| "I'll fix this minor plan error myself rather than interrupting the human." | Plan deviations -- even small ones -- must be surfaced. The human needs to know the plan was wrong. |
| "I'll do 6 tasks this batch since they're all simple." | Batch size calibration exists for a reason. Simple tasks can have complex interactions. Stick to the calibrated size. |
| "The test is failing for an unrelated reason, I'll continue anyway." | A failing test is a failing test. Do not rationalize past it. Stop, report, get guidance. |
| "I'll add this small improvement while I'm in the file." | Unauthorized changes break the checkpoint model. Every change must be in the plan or explicitly approved. |
| "The plan is outdated, so I'll use my judgment for this section." | An outdated plan is a reason to stop and get an updated plan, not a license to improvise. |
| "Reporting after every batch is slow. I'll do 2 batches and then report." | The checkpoint model exists to catch errors early. Skipping a checkpoint means errors propagate further before detection. |

---

## Red Flags Checklist

- [ ] Executing tasks without having read the entire plan first
- [ ] Writing code or modifying files not mentioned in the plan
- [ ] Proceeding to the next task after a verification failure
- [ ] Making interpretation calls on ambiguous instructions without asking
- [ ] Batch size is larger than calibrated for the task complexity
- [ ] Improvements or refactors are being added that are not in the plan
- [ ] A plan error was silently corrected without reporting it
- [ ] Two or more tasks in the current batch have failed verification
- [ ] The finishing-a-development-branch sub-skill was skipped at completion
- [ ] Deviations from the plan are not being mentioned in batch reports

---

## NEVER List

| Prohibition | Why |
|------------|-----|
| NEVER continue past a failing verification | Failures cascade. The next task likely depends on the current one being correct. |
| NEVER silently fix plan errors | The human must know the plan was wrong. Silent fixes hide information needed for future planning. |
| NEVER add code or changes not in the plan | Unauthorized changes undermine the checkpoint model and introduce unreviewed behavior. |
| NEVER interpret ambiguous instructions -- always ask | Wrong interpretations compound across every subsequent task in the batch and beyond. |
| NEVER skip the finishing-a-development-branch sub-skill at completion | That skill handles final verification, option presentation, and safe handoff. Skipping it leaves work in an unverified state. |
| NEVER execute more than one batch without reporting | The checkpoint model requires human review between batches. Skipping a checkpoint defeats the entire purpose of this skill. |
