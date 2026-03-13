---
name: clean-code
description: "Use when writing, reviewing, or refactoring code in any language. Applies to new features, bug fixes, refactoring tasks, and code review. NEVER for documentation-only tasks, data processing one-offs with no maintainability requirement, or throwaway scripts where readability does not matter."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Clean Code -- Pragmatic AI Coding Standards

## Activation Reminders

These principles are deeply known. This table exists only as a pre-flight check -- scan it before writing, not as learning material.

| Principle | One-line reminder |
|-----------|-------------------|
| SRP | One function = one thing |
| DRY | Extract duplicates |
| KISS | Simplest solution that works |
| YAGNI | Don't build what wasn't asked for |
| Boy Scout | Leave code cleaner than you found it |
| Guard clauses | Early returns instead of nesting |
| Naming | Intent-revealing names; if a comment explains the name, rename it |
| Small functions | Under 20 lines, 0-2 args preferred |

---

## Before Editing ANY File

Before changing a file, answer these questions:

| Question | Why |
|----------|-----|
| **What imports this file?** | Callers may break |
| **What does this file import?** | Interface changes cascade |
| **What tests cover this?** | Tests may fail silently |
| **Is this a shared component?** | Multiple places are affected |

Rule: Edit the file AND all dependent files in the SAME task. Never leave broken imports or missing updates behind.

---

## Conflict Resolution

When two principles collide, use this decision table. These are the conflicts Claude encounters most often.

| Conflict | Resolution |
|----------|------------|
| **DRY vs KISS**: Extracting a shared function adds indirection and complexity. | If the shared function is called fewer than 3 times, inline it. Duplication is cheaper than the wrong abstraction. |
| **Boy Scout vs Scope**: The surrounding code is messy but the user asked for a specific fix. | Fix what was asked. Refactor only the code you touch. Do not expand scope without asking the user. |
| **Speed vs Quality**: The user wants something fast. | Speed does not override correctness. A fast fix that breaks callers is slower than a correct fix delivered promptly. |
| **YAGNI vs Reuse**: You can see a pattern forming but the user only asked for one instance. | Build only what was requested. If a second instance appears later, extract then. Premature abstraction is worse than duplication. |
| **SRP vs Readability**: Splitting a 25-line function into three 8-line functions makes the flow harder to follow. | Split only if each extracted function has a clear, independent purpose. If the split hides the sequence of operations, keep it together. |
| **Naming vs Convention**: The project uses short names (`usr`, `cfg`) throughout. | Match the project convention for existing code. Apply clean naming to new code you write. Do not rename the project's entire codebase. |

---

## Anti-Patterns

| Pattern | Fix |
|---------|-----|
| Comment every line | Delete obvious comments |
| Helper for one-liner | Inline the code |
| Factory for 2 objects | Direct instantiation |
| utils file with 1 function | Put code where it is used |
| Narrating actions in prose | Just write the code |
| Deep nesting (3+ levels) | Guard clauses |
| Magic numbers | Named constants |
| God functions (50+ lines) | Split by responsibility |

---

## Edge Cases

Real-world situations where the standard rules bend.

**Legacy codebase (no tests, inconsistent style):**
Do not attempt a full rewrite. Apply clean code only to lines you change. Add a test for the behavior you modify. Leave everything else untouched unless the user asks for broader cleanup.

**Large refactoring request:**
Ask the user to confirm scope before starting. Break the work into independently testable steps. Each step should leave the codebase in a working state. Never batch all changes into a single commit.

**Time-sensitive hotfix:**
Write the immediate fix cleanly. Do not skip naming, guard clauses, or dependency checks because of urgency. The hotfix path is not an excuse path. If the fix is genuinely one line, one line is fine -- no need to add abstraction around it.

**Unfamiliar language or framework:**
Follow the project's existing patterns over generic clean code rules. Read 2-3 existing files to learn the local conventions before writing new code. When in doubt, match what already exists.

---

## Rationalization Table

These are excuses Claude makes to skip following this skill. Each one is wrong.

| Rationalization | Why It Is Wrong |
|----------------|-----------------|
| "This is a quick fix so clean code doesn't apply here." | Quick fixes become permanent. Messy patches compound. Every change is subject to the same standards. |
| "The existing code is already messy, so matching the style is fine." | Boy Scout rule: leave it cleaner. Matching bad style makes the problem worse, not neutral. |
| "Adding a comment is faster than renaming." | Comments drift from code. A good name is always accurate. Comments lie; names enforce correctness. |
| "This function is already 30 lines -- splitting it is extra work the user didn't ask for." | The user asked for working, maintainable code. If the function does more than one thing, splitting IS the task. |
| "I'll create a helper function to keep things organized." | YAGNI. If a helper is only called once, it adds indirection with no benefit. Inline it. |
| "Nesting here is fine because it's only 3 levels deep." | Three levels of nesting is already past the limit. Guard clauses eliminate nesting at every level. |
| "The user wants speed, not refactoring, so I'll skip the dependency check." | Skipping the dependency check causes broken imports and missing updates -- that is slower, not faster. |
| "Explaining what I'm doing before writing code helps the user follow along." | The user wants working code. Narration adds tokens and delays delivery. Just write the code. |

---

## Red Flags Checklist

Observable signs this skill is being violated:

- [ ] A function is longer than 20 lines and handles more than one concern
- [ ] A variable is named `data`, `info`, `temp`, `x`, `n`, or another meaningless label
- [ ] A comment explains what the code does rather than why a non-obvious decision was made
- [ ] Nesting is 3 or more levels deep anywhere in the code
- [ ] A helper function exists that is called in exactly one place and contains fewer than 5 lines
- [ ] A magic number appears inline without a named constant
- [ ] Code was changed in one file but dependent files (callers, tests, interfaces) were not reviewed
- [ ] A util or shared module was created for a single function that is used once
- [ ] Response begins with narration ("First, let's...", "I'll start by...") before writing code
- [ ] A bug fix was explained in prose before the code was applied
- [ ] A principle conflict was resolved by ignoring one principle entirely instead of consulting the Conflict Resolution table
- [ ] Scope was expanded beyond the user's request without asking permission

---

## NEVER List

| Prohibition | Why |
|-------------|-----|
| NEVER add comments that restate what the code already says. | Obvious comments add noise and go stale without warning. If the code is unclear, rewrite it. |
| NEVER leave a task with broken imports or missing dependent updates. | Partial edits silently break callers. Every change must include all affected files in the same pass. |
| NEVER create a helper, wrapper, or abstraction for code that is only used once. | Single-use abstractions add indirection with no reuse benefit. Inline the logic. |
| NEVER nest code more than 2 levels deep when guard clauses can flatten it. | Deep nesting forces readers to track multiple conditions at once. Guard clauses eliminate the problem at the source. |
| NEVER use a vague name and compensate with a comment. | The name should be the documentation. If a comment is required to explain the name, the name is wrong. |
| NEVER build features or abstractions the user did not ask for. | YAGNI. Unrequested code becomes maintenance burden. Build exactly what was requested. |
| NEVER expand refactoring scope beyond what the user requested without asking. | Scope creep in refactoring introduces risk the user did not authorize. Confirm before widening. |
