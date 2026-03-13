---
name: systematic-debugging
description: "Use when encountering any bug, test failure, unexpected behavior, build failure, or integration issue -- before proposing fixes. Also use when previous fix attempts have failed, or when under time pressure where guessing is tempting. NEVER use for performance optimization without an error present, feature implementation, code review, or refactoring tasks."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Systematic Debugging

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes. Violating the letter of this process is violating the spirit of debugging.

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| `root-cause-tracing.md` | Backward stack trace technique | Error is deep in call stack |
| `defense-in-depth.md` | Multi-layer validation after root cause found | Adding post-fix hardening |
| `condition-based-waiting.md` | Replace arbitrary timeouts with condition polling | Timing-dependent issues |

**Related skills:**
- `superpowers:test-driven-development` -- Creating the failing test case (Phase 4, Step 1)
- `superpowers:verification-before-completion` -- Verify fix worked before claiming success

## Debugging Edge Cases

These scenarios change how the standard 4-phase process applies. Recognize them before starting Phase 1.

| Scenario | How Standard Debugging Breaks | What to Do Instead |
|---|---|---|
| Heisenbug (disappears under observation) | Adding logging or breakpoints changes timing and hides the bug | Use post-mortem analysis: core dumps, production logs, structured event tracing. Do not add live instrumentation. |
| Flaky test (passes sometimes, fails sometimes) | Reproducing consistently (Phase 1.2) is impossible | Identify the shared mutable state: global variables, database rows, file system, clock-dependent logic, or test execution order. Run the test in isolation AND in the full suite -- the difference reveals the dependency. |
| Works locally, fails in CI | Environment differences are invisible to git diff (Phase 1.3) | Compare: OS version, dependency lock file, env variables, file system case sensitivity, available memory, network access. Reproduce CI locally with `docker run` using the CI image. |
| Error only under load | Root cause is a concurrency issue that single-threaded debugging cannot surface | Reproduce with a load test targeting the specific endpoint. Add thread-safe logging at lock acquisition points. Look for missing locks, race conditions on shared state, and connection pool exhaustion. |
| Regression with unknown origin | "Check recent changes" (Phase 1.3) yields too many candidates | Use `git bisect` to binary-search the offending commit. Start from last known good build. This narrows thousands of commits to one in O(log n) runs. |

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully** -- Don't skip past errors or warnings. Read stack traces completely. Note line numbers, file paths, error codes. They often contain the exact solution.

2. **Reproduce Consistently** -- Can you trigger it reliably? What are the exact steps? If not reproducible, check the "Debugging Edge Cases" table above -- the bug may be a heisenbug, flaky test, or load-dependent issue requiring a different reproduction strategy.

3. **Check Recent Changes** -- What changed that could cause this? Review git diff, recent commits, new dependencies, config changes, and environmental differences. If the diff is too large, use `git bisect` (see Edge Cases table).

4. **Gather Evidence in Multi-Component Systems**

   When the system has multiple components (CI -> build -> deploy, API -> service -> database), add diagnostic instrumentation BEFORE proposing fixes:

   ```
   For EACH component boundary:
     - Log what data enters the component
     - Log what data exits the component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks.
   THEN analyze to identify the failing component.
   THEN investigate that specific component.
   ```

   Pattern: add a one-line probe at each layer boundary (e.g., `echo "VAR: ${VAR:-UNSET}"`), run once, and the output immediately narrows which layer is failing -- eliminating all layers above and below.

5. **Trace Data Flow** -- When the error is deep in the call stack, use `root-cause-tracing.md` for the complete backward tracing technique. Quick version: where does the bad value originate? What called this with the bad value? Keep tracing up until you find the source. Fix at source, not at symptom.

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples** -- Locate similar working code in the same codebase. What works that is similar to what is broken?

2. **Compare Against References** -- If implementing a pattern, read the reference implementation COMPLETELY. Do not skim -- read every line. Partial understanding guarantees bugs.

3. **Identify Differences** -- What is different between working and broken? List every difference, however small. Do not assume "that can't matter."

4. **Understand Dependencies** -- What other components does this need? What settings, config, or environment? What assumptions does it make?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis** -- State clearly: "I think X is the root cause because Y." Be specific. Write it down.

2. **Test Minimally** -- Make the SMALLEST possible change to test the hypothesis. One variable at a time. Do not fix multiple things at once.

3. **Verify Before Continuing** -- Did it work? Yes -> Phase 4. No -> form a NEW hypothesis. Do not stack more fixes on top.

4. **When You Don't Know** -- Say "I don't understand X." Do not pretend. Ask for help or research further before proceeding.

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create Failing Test Case** -- Simplest possible reproduction. Automated test if possible; one-off script if no framework. This MUST exist before implementing the fix. Use `superpowers:test-driven-development` for writing proper failing tests.

2. **Implement Single Fix** -- Address the root cause identified. ONE change at a time. No "while I'm here" improvements. No bundled refactoring.

3. **Verify Fix** -- Test passes? No other tests broken? Issue actually resolved?

4. **If Fix Doesn't Work** -- STOP. Count how many fixes you have tried. If fewer than 3: return to Phase 1 and re-analyze with new information. If 3 or more: do NOT attempt another fix -- proceed to step 5.

5. **If 3+ Fixes Failed: Question Architecture** -- Each fix revealing a new problem in a different place, fixes requiring massive refactoring, or each fix creating new symptoms elsewhere all indicate an architectural problem, not a hypothesis failure.

   STOP and question the fundamentals:
   - Is this pattern fundamentally sound?
   - Are we continuing through sheer inertia?
   - Should we refactor the architecture rather than fix more symptoms?

   Discuss with your human partner before attempting any further fixes. This is a wrong architecture, not a failed hypothesis.

   If the investigation exhausts all leads and the issue is genuinely environmental or timing-dependent: document what was investigated, implement appropriate handling (retry, timeout, error message), and add monitoring for future investigation. Note: 95% of "no root cause found" conclusions are the result of incomplete investigation.

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather layer-by-layer evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare against reference | Identify all differences |
| **3. Hypothesis** | Form single theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create failing test, single fix, verify | Bug resolved, tests pass |

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms does not equal understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Red Flags Checklist

Stop and return to Phase 1 if any of the following apply:

- [ ] Thinking "quick fix for now, investigate later"
- [ ] Thinking "just try changing X and see if it works"
- [ ] Adding multiple changes at once before testing
- [ ] Skipping the failing test case ("I'll manually verify")
- [ ] Proposing a fix before tracing the actual data flow
- [ ] Saying "I don't fully understand but this might work"
- [ ] Adapting a pattern without reading the reference completely
- [ ] Listing fixes without completing investigation ("here are the main problems: ...")
- [ ] Attempting a fix attempt when 2 or more have already failed
- [ ] Each fix revealing a new problem in a different place

Human partner signals that indicate the same issue: "Is that not happening?" (you assumed without verifying), "Will it show us...?" (you should have added evidence gathering), "Stop guessing" (proposing fixes without understanding), "Ultrathink this" (question fundamentals, not symptoms).

## NEVER List

| Prohibition | Why |
|-------------|-----|
| NEVER propose a fix before completing Phase 1 root cause investigation | Fixes without understanding entrench wrong assumptions and mask the real issue |
| NEVER apply multiple fixes simultaneously | Cannot isolate what worked; introduces new bugs and defeats hypothesis testing |
| NEVER skip creating a failing test case before implementing a fix | Without a test, there is no proof the fix solved the right problem |
| NEVER continue past 3 failed fix attempts without questioning the architecture | Repeated failures signal a structural problem, not a missing patch |
| NEVER assume a root cause without tracing the actual data flow | Assumptions about cause are symptoms masquerading as diagnoses |
| NEVER treat "no root cause found" as a valid conclusion without exhaustive investigation | 95% of such conclusions result from incomplete Phase 1 work |
