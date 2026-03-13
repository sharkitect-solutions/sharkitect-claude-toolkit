# Codebase Style Calibration Guide

Load when deslopping a codebase you haven't seen before, when the diff spans multiple style conventions, or when AI additions conflict with existing code style.

## Style Detection Procedure

Before removing anything, read the existing codebase to establish baselines. This takes 5-10 minutes and prevents false positives.

### Step 1: Identify Style Signals

For each file in the diff, examine the UNCHANGED code (not the AI additions) for these signals:

| Signal | What to Look For | Example Values |
|---|---|---|
| Brace style | Same-line or next-line? | `function foo() {` vs `function foo()\n{` |
| Quote style | Single, double, or backticks? | `'string'` vs `"string"` |
| Semicolons | Present or absent? (JS/TS) | `const x = 1;` vs `const x = 1` |
| Naming convention | camelCase, snake_case, PascalCase, kebab-case? | `getUserName` vs `get_user_name` |
| Import organization | Grouped? Sorted? Blank lines between groups? | stdlib / external / internal with blank lines |
| Comment style | Block comments, inline, JSDoc, none? | `/** ... */` vs `// ...` vs no comments |
| Error handling | Explicit try/catch, error middleware, Result types? | Per-function vs centralized |
| Type annotation density | Explicit types or inference-heavy? | `const x: number = 1` vs `const x = 1` |
| Line length | ~80, ~100, ~120, unlimited? | Check longest lines in the file |
| Trailing commas | Present on last item or not? | `[a, b, c,]` vs `[a, b, c]` |
| Function style | Arrow functions, function declarations, or mixed? | `const fn = () => {}` vs `function fn() {}` |
| Blank lines | Between functions, inside functions, between logical blocks? | Count blank lines between existing functions |

### Step 2: Check for Config Files

These files are authoritative -- they override all visual inspection:

| File | What It Tells You |
|---|---|
| `.eslintrc` / `eslint.config.js` | JS/TS style rules, enforced automatically |
| `.prettierrc` / `prettier.config.js` | Formatting rules (quotes, semicolons, line length, trailing commas) |
| `pyproject.toml` `[tool.ruff]` or `[tool.black]` | Python formatting rules |
| `.editorconfig` | Cross-language indentation, line ending, final newline |
| `rubocop.yml` | Ruby style rules |
| `.clang-format` | C/C++ formatting |
| `rustfmt.toml` | Rust formatting |

**If a config file exists and AI code violates it**: This is slop. The AI ignored the project's formatter.
**If a config file exists and AI code follows it**: The AI code is correctly styled. Only check for semantic slop (unnecessary logic), not formatting.

### Step 3: Resolve Ambiguity

When the existing codebase is inconsistent (common in large projects with multiple contributors):

| Situation | Resolution |
|---|---|
| File A uses single quotes, File B uses double quotes | Follow each file's local convention. Don't unify across files -- that's refactoring, not deslopping. |
| Older files use `var`, newer files use `const/let` | Follow the file's era. Don't update `var` to `const` unless it's in the AI-added lines. |
| Some functions use explicit return types, some don't | Follow the density of the file. If 80%+ of functions have explicit types, the AI should too. |
| Mixed tabs and spaces in the same file | If `.editorconfig` or formatter config exists, follow it. Otherwise, follow the majority pattern. |
| No consistent style at all (early-stage codebase) | Don't flag style as slop. Only flag semantic slop (unnecessary code, debug artifacts, etc.). |

## Multi-File Diff Calibration

When the diff spans 10+ files across different areas of the codebase:

### Priority Order

1. **High-traffic files first** (routes, controllers, main components) -- these are most visible and most likely to have established patterns
2. **Test files second** -- tests often have intentionally different style (more verbose, descriptive names); calibrate separately
3. **Config/setup files last** -- these are rarely read and AI slop here is low-impact

### Cross-File Consistency Check

| Check | Why | Action |
|---|---|---|
| Same function added in multiple files | AI copies patterns including slop across files | Fix in all files, not just one |
| Import organization differs between AI additions | AI doesn't maintain consistent import grouping across files | Standardize AI imports to match each file's existing pattern |
| Error handling strategy differs between AI additions | AI uses try/catch in one file and if/else error checks in another | Each file should match its own established pattern |
| Comment density varies wildly between AI additions | AI adds heavy comments in some files, none in others | Calibrate to each file's existing comment density |

## Deslop Confidence Levels

Assign a confidence level to each removal. Report items below HIGH to the user for confirmation.

| Confidence | Criteria | Action |
|---|---|---|
| CERTAIN | Matches a catalog pattern exactly, clearly contradicts local style, and has no explanatory comment | Remove silently. Include in summary count. |
| HIGH | Matches a catalog pattern, probably contradicts local style, but surrounding code is ambiguous | Remove. Note in report. |
| MEDIUM | Looks like slop but has an edge case argument for keeping it (e.g., defensive check on a boundary that's "probably" safe) | Leave in place. Note in report as "possible slop, verify with owner." |
| LOW | Unusual code that doesn't match any catalog pattern but "feels" AI-generated | Leave in place. Don't mention. This is subjective and not actionable. |

## Edge Cases

### Greenfield Projects (No Existing Code)

If the entire codebase is AI-generated (new project, no human code to calibrate against):
- Only remove CERTAIN slop (debug artifacts, console.log, obvious comments)
- Do NOT flag style issues -- there is no human baseline to compare against
- Focus on semantic slop: unnecessary code paths, redundant checks, dead code

### Mixed Human + AI Files

If a file has both human-written and AI-written sections:
- The human-written section IS the style guide
- AI additions that deviate from the human section are candidates for slop
- AI additions that match the human section are fine, even if they'd be "slop" in isolation

### Monorepo with Multiple Languages

| Situation | Action |
|---|---|
| `packages/frontend/` is TypeScript, `packages/api/` is Python | Calibrate per package. Language-level slop patterns apply per directory. |
| Shared linting config at root | Root config is authoritative for all packages it covers |
| Different teams own different packages | Different conventions are expected. Calibrate per package, not per repo. |

### AI-Generated Tests

Tests have intentionally different style from production code:
- Verbose variable names are acceptable (readability > brevity in tests)
- Explicit assertions even when inference would work (clarity > conciseness)
- Duplicate setup across test cases is acceptable (test isolation > DRY)
- Only flag: `console.log` debug artifacts, commented-out tests, obvious copy-paste with wrong assertions
