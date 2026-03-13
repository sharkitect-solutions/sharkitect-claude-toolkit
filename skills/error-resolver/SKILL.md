---
name: error-resolver
description: Use when encountering any error message, stack trace, exception, or unexpected behavior during development. Use when debugging build failures, runtime crashes, test failures, dependency conflicts, configuration errors, or permission errors. NEVER for performance optimization without an error present, feature requests, code review tasks with no error, or general refactoring work.
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Error Resolver

A first-principle approach to diagnosing and resolving errors across all languages and frameworks.

## 5-Step Resolution Process

1. CLASSIFY -- 2. PARSE -- 3. MATCH -- 4. ANALYZE -- 5. RESOLVE

Execute all five steps in sequence. Do not skip steps based on apparent familiarity with the error.

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| patterns/nodejs.md | Node.js and npm error patterns | Error involves Node.js, npm, or JavaScript runtime |
| patterns/python.md | Python error patterns | Error involves Python, pip, or virtualenv |
| patterns/react.md | React and Next.js error patterns | Error involves React, JSX, or Next.js |
| patterns/database.md | Database error patterns | Error involves SQL, ORM, or DB connections |
| patterns/docker.md | Docker and container error patterns | Error involves Docker, containers, or images |
| patterns/git.md | Git error patterns | Error involves git commands or repository state |
| patterns/network.md | Network and API error patterns | Error involves HTTP, ECONNREFUSED, or API calls |
| patterns/go.md | Go error patterns | Error involves Go compilation or runtime |
| patterns/rust.md | Rust error patterns | Error involves Rust compilation or cargo |
| analysis/stack-trace.md | Stack trace parsing methodology | Stack trace is present and needs systematic parsing |
| analysis/root-cause.md | Root cause analysis techniques | 5 Whys analysis is needed for complex failures |
| replay/solution-template.yaml | Template for recording solutions | A new solution has been confirmed and should be recorded |
| replay/README.md | Replay system overview | Looking up or recording solution patterns |

## Error Classification Framework

### Primary Categories

| Category | Indicators | Common Causes |
|----------|------------|---------------|
| Syntax | Parse error, Unexpected token | Typos, missing brackets, invalid syntax |
| Type | TypeError, type mismatch | Wrong data type, null/undefined access |
| Reference | ReferenceError, NameError | Undefined variable, scope issues |
| Runtime | RuntimeError, Exception | Logic errors, invalid operations |
| Network | ECONNREFUSED, timeout, 4xx/5xx | Connection issues, wrong URL, server down |
| Permission | EACCES, PermissionError | File/directory access, elevated privileges needed |
| Dependency | ModuleNotFound, Cannot find module | Missing package, version mismatch |
| Configuration | Config error, env missing | Wrong settings, missing environment variables |
| Database | Connection refused, query error | DB down, wrong credentials, malformed query |
| Memory | OOM, heap out of memory | Memory leak, oversized data processing |

### Secondary Attributes

- **Severity**: Fatal / Error / Warning / Info
- **Scope**: Build-time / Runtime / Test-time
- **Origin**: User code / Framework / Third-party / System

## Analysis Workflow

### Step 1: Classify

Identify the error category by examining:
- Error name or code (e.g., ENOENT, TypeError, ModuleNotFound)
- Error message keywords
- Where it occurred (compile, runtime, test)

### Step 2: Parse

Extract all key information before proceeding:
- Error code: [specific code if present]
- File path: [where the error originated]
- Line number: [exact line if available]
- Function/method: [context of the error]
- Variable/value: [what was involved]
- Stack trace depth: [how deep is the call stack]

Load analysis/stack-trace.md if a stack trace is present.

### Step 3: Match Patterns

Check the relevant patterns/ file for the detected language or error category. Check replay/ for previously recorded solutions matching this error signature. If a match is found, apply the recorded solution and verify before closing.

### Step 4: Root Cause Analysis

Apply the 5 Whys technique (load analysis/root-cause.md for complex cases):

- Error: Cannot read property 'name' of undefined
- Why 1 -- user object is undefined
- Why 2 -- API call returned null
- Why 3 -- User ID does not exist in the database
- Why 4 -- ID was from a stale cache
- Why 5 -- Cache invalidation not implemented
- Root Cause: Missing cache invalidation logic

Do not stop at the first plausible cause. Continue until the systemic origin is identified.

### Step 5: Resolve

Produce all three resolution layers:
1. Immediate fix -- get it working now
2. Proper fix -- the correct long-term solution
3. Prevention -- how to avoid recurrence

## Output Format

Produce this structure for every error resolution:

---
## Error Diagnosis

**Classification**: [Category] / [Severity] / [Scope]

**Error Signature**:
- Code: [error code]
- Type: [error type]
- Location: [file:line]

## Root Cause

[Explanation of why this error occurred]

**Contributing Factors**:
1. [Factor 1]
2. [Factor 2]

## Solution

### Immediate Fix
[Quick steps to resolve]

### Code Change
[Specific code to add/modify]

### Verification
[How to verify the fix works]

## Prevention

[How to prevent this error in the future]

## Replay Tag

[Unique identifier for this solution]
---

Record confirmed solutions using replay/solution-template.yaml in .claude/error-solutions/.

## Debugging Patterns

| Pattern | When to Use | Method |
|---------|-------------|--------|
| Binary Search | Error location is unclear | Comment out half the code; if error persists it is in the remaining half; repeat |
| Minimal Reproduction | Cannot isolate the cause | Build from an empty file, add code until the error appears |
| Rubber Duck | Assumptions may be wrong | State what should happen, what actually happens, what changed, and what assumptions exist |
| Git Bisect | Regression with unknown origin | Use git bisect to binary-search commits between last-known-good and current |

## Rationalization Table

| Rationalization | Why It Is Wrong |
|-----------------|-----------------|
| I already know what this error means -- I can skip to the fix | Pattern recognition is unreliable without parsing; similar error messages have different root causes across contexts |
| This is a simple error, the full workflow is overkill | Simple-looking errors frequently mask systemic issues; skipping analysis produces fixes that recur |
| The stack trace tells me everything I need | Stack traces show where an error surfaced, not why it originated; root cause analysis is always required |
| The user has already described the cause, I just need to fix it | User diagnosis is a hypothesis, not a root cause; verify before prescribing a solution |
| I have seen this exact error before, I know the solution | Prior solutions apply to prior contexts; environment, versions, and code state change the answer |
| The fix is obvious from the error message | Error messages are written for humans and are frequently misleading; classification and parsing validate the obvious interpretation |
| Checking patterns/ is unnecessary for common errors | The patterns directory contains language-specific edge cases and version-dependent behaviors not held in general knowledge |
| I can skip Step 3 because I did not write replay files | Replay files may exist from prior sessions or teammates; always check before treating an error as new |

## Red Flags Checklist

Check for these signs that the skill is being violated:

- [ ] Providing a fix without stating the error classification
- [ ] Suggesting code changes before completing the Parse step
- [ ] Stopping at "Why 1" in the 5 Whys analysis
- [ ] Skipping patterns/ lookup because the language seems familiar
- [ ] Omitting the Prevention section from the output
- [ ] Treating the user's stated cause as confirmed without verification
- [ ] Providing only an immediate fix without a proper long-term fix
- [ ] Skipping replay/ lookup before treating the error as novel
- [ ] Producing a solution without a Verification step
- [ ] Closing the resolution before the fix has been confirmed to work

## NEVER List

| Prohibition | Why |
|-------------|-----|
| NEVER skip directly to a code fix without completing Classify and Parse | Fixes applied to misclassified errors introduce new bugs and waste time |
| NEVER present a single-layer solution (immediate fix only) | Without the proper fix and prevention layers the error will recur |
| NEVER accept the first plausible root cause without applying 5 Whys | Surface causes mask systemic issues; stopping early produces recurring failures |
| NEVER omit Verification from the output | An unverified fix is a guess; the resolution is not complete until the fix is confirmed |
| NEVER apply a replay solution without verifying it matches the current context | Environments and versions differ; a past solution can be wrong or harmful in a new context |
| NEVER diagnose based on the error message alone without reading the stack trace | Error messages are human-readable summaries; stack traces reveal the actual execution path |
| NEVER treat missing context as sufficient reason to skip steps | If context is missing, ask for it before proceeding -- do not assume and continue |
