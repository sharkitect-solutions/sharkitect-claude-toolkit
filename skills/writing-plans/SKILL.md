---
name: writing-plans
description: "Use when you have a spec or requirements for a multi-step task and need a written implementation plan before touching any code. NEVER use for single-file changes or trivial edits -- inline steps are sufficient. NEVER use after implementation has already started."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Writing Plans

## Codebase Investigation Protocol

Read the codebase before writing a single task. Skipping this step produces plans that reference files that do not exist, recreate utilities that already exist, and use naming conventions inconsistent with the project.

**Required before writing:**
1. Read existing tests -- understand the test framework, assertion style, and fixture patterns in use
2. Read existing source files in the affected area -- understand naming conventions and module structure
3. Search for shared utilities related to the feature (validators, helpers, clients) -- do not plan to recreate them
4. Map the import chain -- identify which files will be affected by each change
5. Note the commit style from `git log --oneline -10` -- match it in the plan

## Plan Scope Calibration

Choose plan depth based on change size:

| Change Size | Plan Format | Separate Doc? |
|-------------|-------------|---------------|
| 1 file, self-contained | Inline steps in chat | No |
| 2-5 files, clear scope | Lightweight: file list + test expectations + steps | Optional |
| 6+ files or architectural change | Full plan doc with Architecture, Dependency Order, Rollback | Yes -- save to `docs/plans/` |

**Save full plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Dependency Ordering

Sequence tasks so the system compiles and passes tests after every commit:

1. Database / schema changes first (migrations, models)
2. Core business logic second (domain objects, services)
3. API / integration layer third (endpoints, clients, adapters)
4. UI / presentation last (templates, components, views)

Each task must leave the system in a working state. Never plan a task that breaks the build and expects a future task to fix it.

## Plan Document Header

Every full plan MUST start with this header:

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about the approach and key design decisions]

**Tech Stack:** [Key technologies and libraries used]

**Dependency Order:** [Brief note on sequencing rationale if non-obvious]

---
```

## Bite-Sized Task Granularity

Each step is one atomic action (2-5 minutes). Never combine "write test + implement + commit" into one step. They are always separate steps.

**Correct granularity:**
- "Write the failing test" -- one step
- "Run it to verify it fails" -- one step
- "Write the minimal implementation" -- one step
- "Run the tests to verify they pass" -- one step
- "Commit" -- one step

**Wrong granularity:**
- "Write and test the validation function" -- too many things at once
- "Implement the feature" -- no test step, no commit step

## Task Structure

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test_file.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function_name(input_value)
    assert result == expected_value
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test_file.py::test_specific_behavior -v`
Expected: FAIL with "NameError: name 'function_name' is not defined"

**Step 3: Write minimal implementation**

```python
def function_name(input_value):
    return expected_value
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test_file.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test_file.py src/path/file.py
git commit -m "feat: add specific behavior description"
```
```

## Plan Quality Standards

Every task in the plan must meet these standards:

- Exact file paths -- if the file does not exist yet, there is a Create step for it
- Complete code in the plan, not placeholders like "add validation here"
- Exact test commands with expected output (PASS or FAIL with the error message)
- Complete commit commands with meaningful messages matching the project style
- No task depends on uncommitted work from a previous task

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan saved to `docs/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (this session)** -- dispatch a fresh subagent per task, review output between tasks, fast iteration loop. REQUIRED SUB-SKILL: superpowers:subagent-driven-development

**2. Parallel Session (separate)** -- open a new session in the worktree, batch execution with checkpoints. REQUIRED SUB-SKILL: superpowers:executing-plans

Which approach?"

## Rationalization Table

| Rationalization | Why It Is Wrong |
|-----------------|-----------------|
| "The task is simple enough to implement directly without a plan." | Simple tasks still benefit from a file list and test expectations. Scope always expands once you start. |
| "The user wants to start coding now, so I'll skip the codebase investigation." | Plans written without reading the codebase reference nonexistent files and miss existing utilities. Fix it before writing, not during execution. |
| "I'll use approximate paths and the developer can figure out the exact locations." | Approximate paths produce lookup failures during execution. Exact paths are non-negotiable. |
| "The implementation is obvious so I'll skip the test steps." | Skipping test steps makes failures ambiguous. The test step verifies your implementation matches your intent. |
| "I'll write the plan as I understand it and note the unknowns with placeholders." | Placeholders ("add validation here") are useless in execution. Resolve every unknown before writing the plan. |
| "This is a Tier 1 priority so I should start immediately." | Urgency is not a reason to skip planning. A bad plan causes more delay than writing a good one. |
| "The spec is clear enough that investigation would be redundant." | The spec describes intent, not the existing code structure. Investigation reveals what you cannot know from the spec alone. |
| "I'll combine steps to make the plan more concise." | Combined steps hide failures. When step 3 fails, you do not know if the test was wrong, the implementation was wrong, or both. |

## Red Flags Checklist

Signs the skill is being violated or applied incorrectly:

- [ ] A task says "modify" a file but there is no preceding Create step and the file does not exist in the codebase
- [ ] A task step says "add validation" or "handle errors" without showing the actual code
- [ ] A test step shows only the assertion, not the full test function with imports and setup
- [ ] A run step is missing the expected output (PASS or specific FAIL message)
- [ ] Two or more concerns are combined in a single step ("write test and implement")
- [ ] A task commits work that depends on changes from a task that has not been committed yet
- [ ] The plan was written before reading any existing tests or source files
- [ ] The plan uses a utility or helper that was not verified to exist in the codebase
- [ ] Tasks are not ordered by dependency layer (UI task before the API it calls)
- [ ] The plan header is missing the executing-plans sub-skill instruction

## NEVER List

| Prohibition | Why |
|-------------|-----|
| NEVER write a plan without first reading existing tests and source in the affected area | Plans written blind recreate existing utilities, break naming conventions, and reference wrong paths |
| NEVER use placeholder content in task steps ("add error handling", "implement validation") | Placeholders cannot be executed. Every step must contain the exact code or command |
| NEVER combine test-write, implement, and commit into a single step | Combined steps make failures ambiguous and skip the verification that TDD requires |
| NEVER sequence tasks so that a later task fixes a broken state left by an earlier task | Every commit must leave the system in a working state. Breaking-then-fixing creates unrecoverable states mid-execution |
| NEVER skip the plan for a multi-file change because the scope "seems obvious" | Obvious scope always expands. The plan is how you verify scope before execution begins |
| NEVER omit the executing-plans sub-skill instruction from the plan header | Executors who open the plan in a new session need the sub-skill reference to proceed correctly |
