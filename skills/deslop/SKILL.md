---
name: deslop
description: "Use when cleaning up AI-generated code, removing unnecessary comments, defensive checks, redundant type assertions, or style inconsistencies introduced by AI coding assistants. Also use when the user says deslop, clean up AI code, or remove slop. NEVER use for refactoring human-written code, changing application logic, or code review (use clean-code)."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Deslop

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Deslop procedure, AI slop pattern catalog (18 patterns), language-specific slop, slop vs intentional decision guide | Always (auto-loaded) |
| framework-specific-patterns.md | React/Next.js, Express, Django, Rails slop patterns, framework-specific style conflicts, App Router gotchas | When deslopping code in a specific framework |
| codebase-style-calibration.md | Style detection procedure, config file authority, ambiguity resolution, multi-file calibration, confidence levels | When deslopping an unfamiliar codebase or when style conventions are unclear |
| batch-deslop-workflow.md | Large diff triage (20+ files), file categorization, slop density scoring, reporting formats, multi-commit handling | When deslopping large branches or producing structured deslop reports |

## Scope Boundary

| This Skill Handles | Defer To |
|---|---|
| Removing AI-generated code artifacts (comments, defensive checks, type noise) | clean-code (refactoring human-written code) |
| Detecting and removing debug artifacts (console.log, print statements) | systematic-debugging (investigating bugs) |
| Calibrating to local codebase style before removing | frontend-design (establishing new design conventions) |
| Framework-specific AI slop patterns | error-resolver (fixing actual runtime errors) |
| Batch deslop of large diffs with structured reporting | git-commit-helper (commit message writing) |
| Slop vs intentional decision guide | senior-backend (architecture decisions) |

## Deslop Procedure

1. **Identify the base branch**: Check `git remote show origin` to confirm the default branch (main, master, develop). If ambiguous, ask the user before proceeding.
2. **Get the diff**: `git diff <base>...HEAD` -- the three-dot form shows all commits on this branch relative to where it diverged from base.
3. **Multi-commit branches**: Diff still works the same way. Do NOT deslop individual commits -- work on the final diff only.
4. **Review each changed file**: For each file in the diff, compare AI additions against the surrounding human-written code to calibrate the local style.
5. **Apply the Pattern Catalog**: Check each addition against the catalog below. When unsure, apply the Slop vs Intentional Decision Guide.
6. **Preserve legitimate changes**: Only remove artifacts. Never alter application logic, error handling that exists for a documented reason, or code flagged with an explanatory comment.
7. **Report**: Deliver a 1-3 sentence summary of what was removed and why.

## AI Slop Pattern Catalog

| Pattern | Example | Why It's Slop | Fix |
|---|---|---|---|
| Obvious comments | `// Increment the counter` above `count++` | States what the code already says | Delete |
| Section-divider comments | `// ===== Helper Functions =====` | AI file organization noise | Delete |
| Unnecessary defensive try/catch | `try { return arr[0] } catch(e) {}` on a guaranteed non-empty array | Adds noise on trusted/validated paths | Delete |
| `any` cast to bypass types | `(value as any).foo` | Masks a real type issue | Fix the type or use a proper assertion |
| Inline Python imports | `import json` inside a function body | Violates project convention | Move to top-of-file import block |
| Redundant null check on non-nullable | `if (name !== null && name !== undefined)` on a required string param | TypeScript already knows it's non-null | Remove guard or tighten the type |
| Unused catch parameter | `catch (error) { throw new Error('failed') }` | `error` is ignored entirely | `catch { throw ... }` or log `error` |
| console.log left behind | `console.log('processing item', item)` | Debug artifact | Delete |
| Unnecessary async/await | `async function getId() { return await Promise.resolve(42) }` | Wraps a sync value for no reason | Remove async/await |
| Over-verbose variable names | `const userInputValidationResult = validate(input)` | Name length exceeds utility | `const validationResult` or just `valid` |
| Unnecessary intermediate variable | `const result = compute(); return result;` | One line would do | `return compute();` |
| Over-destructuring | `const { a, b, c, d, e } = obj` then only `a` is used | Imports more than needed | `const { a } = obj` |
| Gratuitous ternary | `const x = flag ? true : false` | Just assign the boolean | `const x = flag` |
| Unnecessary string interpolation | `` const msg = `Hello world` `` with no variables | Template literal with no substitution | `const msg = 'Hello world'` |
| Explicit `return undefined` | `return undefined;` at end of void function | JS/TS returns undefined implicitly | Delete |
| Unnecessary block around single statement | `if (cond) { doThing(); }` when codebase uses braceless style | Inconsistent with file style | Match local convention |
| Excessive inferred type annotations | `const count: number = 0` | TypeScript infers `number` from `0` | `const count = 0` |
| Wrapping existing util in a new function | `function isValid(x) { return validate(x); }` | Thin wrapper with no added logic | Call `validate()` directly |

## Language-Specific Slop

| Language | Common AI Slop Patterns |
|---|---|
| Python | Inline imports; `if x is not None:` on values already guarded upstream; `pass` in non-empty blocks; redundant `__all__` on private modules; f-strings with no interpolation; `return None` at end of function |
| TypeScript / JavaScript | `as any`; explicit `: void` return annotations; `Promise.resolve()` wrapping sync values; `console.log` artifacts; `undefined` checks on non-optional params; unnecessary `else` after `return` |
| React | Wrapping a single JSX element in a Fragment with no sibling need; `key={index}` on static lists; prop drilling a value one level (should be passed directly); empty `useEffect` dependency arrays on effects with deps |
| Go | Error shadowing with blank identifier `_ =`; `fmt.Println` debug artifacts; unnecessary pointer indirection; wrapping stdlib errors without adding context |

## Slop vs Intentional Decision Guide

Do NOT remove something that looks like slop if any of these apply:

- **Has an explanatory comment**: A comment explaining WHY the unusual pattern exists (upstream bug, external API quirk, compliance requirement) means it is intentional. Leave it.
- **Matches a pattern elsewhere in the file**: If three other functions in the same file use the same verbose style, it is the local convention. Leave it.
- **The defensive check is on an external input**: Try/catch and null guards on data from external APIs, user input, or file I/O are legitimate. Only remove them on fully internal/validated paths.
- **The type cast has context**: `as unknown as T` at a serialization boundary is often correct. Only remove `any` casts that exist solely to suppress a type error with no explanation.
- **You are unsure**: Note it in the report as "possible slop, left in place -- verify with owner" rather than silently removing it.

## Rationalization

| Dimension | Why This Skill Handles It |
|---|---|
| Scope precision | Operates on the branch diff only -- never touches pre-existing human code outside the changed lines |
| Style calibration | Reads surrounding file context before flagging anything, so local conventions override generic rules |
| Pattern completeness | Catalog covers 18 patterns across obvious and subtle AI artifacts, reducing false negatives |
| Language awareness | Per-language table captures idioms that generic rules miss (Python inline imports, React fragment noise) |
| False-positive protection | Decision Guide prevents removing intentional defensive code or local convention misidentified as slop |
| Reporting discipline | 1-3 sentence summary keeps the author informed without generating a wall of explanation |

## Red Flags

- Removing code you cannot fully explain -- if you do not understand why it was added, do not remove it
- Deleting defensive checks on external inputs (network, user, file) -- these are not slop
- Changing variable names or logic "while you're in there" -- that is refactoring, not deslopping
- Removing type annotations in dynamically typed sections where they serve as documentation
- Treating an entire file as slop because it was AI-generated -- evaluate line by line
- Altering test files -- test structure is often intentionally verbose for clarity; deslop rules apply loosely here
- Modifying files not in the diff -- scope is the branch only

## NEVER

- Refactor, restructure, or rename things unrelated to AI artifact removal
- Change application logic, business rules, or algorithm behavior
- Remove comments that explain non-obvious decisions, even if AI-written
- Run on the default branch directly -- always operate on a feature/fix branch diff
- Replace human-written code that happens to look like a known slop pattern
