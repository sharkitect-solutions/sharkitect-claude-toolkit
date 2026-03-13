# Batch Deslop Workflow

Load when deslopping large diffs (20+ files), multi-commit branches, or when the user wants a structured deslop report.

## Large Diff Triage

### Step 1: Categorize Files by Impact

Run `git diff --stat <base>...HEAD` to get file-level change counts. Categorize:

| Category | Criteria | Priority |
|---|---|---|
| High-impact | Core business logic, API routes, main components, database models | Deslop first. Slop here affects readability of the most-read code. |
| Medium-impact | Utilities, helpers, middleware, service layers | Deslop second. |
| Low-impact | Config files, migrations, generated code, lockfiles | Skip or deslop last. Generated code is expected to be verbose. |
| Test files | Any file in `__tests__/`, `test/`, `spec/`, or `*_test.*` | Separate pass with relaxed rules (see Codebase Style Calibration Guide). |
| Vendor/generated | `node_modules/`, `.lock`, `dist/`, auto-generated types | Skip entirely. Never deslop generated files. |

### Step 2: Estimate Scope

| Diff Size | Estimated Deslop Time | Strategy |
|---|---|---|
| 1-5 files | 5-10 minutes | Deslop inline, single pass |
| 6-20 files | 15-30 minutes | Categorize first, then deslop by category |
| 21-50 files | 30-60 minutes | Full triage, batch by category, report per batch |
| 50+ files | 1-2 hours | Split into sub-PRs if possible. If not, focus on high-impact only. |

### Step 3: File-Level Quick Scan

For each file, do a 10-second scan before deep review:

| Quick Signal | What It Means | Action |
|---|---|---|
| File is 90%+ new code | Entire file is AI-generated | Apply full pattern catalog |
| File has small AI additions to large existing file | Surgical changes | Calibrate to existing file style, check only the diff |
| File is a rename/move with modifications | Path change + content change | Only review the content modifications, ignore the move |
| File has only import changes | AI reorganized imports | Check against project import conventions only |
| File has only comment additions | AI added documentation comments | Check each against "obvious comment" pattern. Keep non-obvious ones. |

## Slop Density Scoring

After scanning all files, score the overall slop density to calibrate expectations:

| Density | Slop Removals / 100 Lines Changed | What It Means |
|---|---|---|
| Clean | 0-2 | AI output was high quality or well-supervised. Light touch. |
| Normal | 3-8 | Typical AI code. Standard deslop pass works. |
| Heavy | 9-15 | AI was given minimal guidance. Expect framework-specific issues too. |
| Severe | 16+ | AI was used for bulk generation. Consider whether the code needs rewrite rather than deslop. |

**Severe density signal**: If slop density exceeds 16/100 lines, flag to the user. Deslopping at this level may produce a diff as large as the original AI output, making review harder. Rewriting specific files may be more effective.

## Reporting Format

### Per-File Report (for diffs of 1-10 files)

For each file, list:
```
**file.ts** (3 removals, 1 flagged)
- Removed: obvious comment L42, console.log L67, redundant null check L89
- Flagged: try/catch on L23-28 wraps fetch() which could fail -- verify if error handling is needed
```

### Batch Summary Report (for diffs of 10+ files)

```
**Deslop Summary: feature/user-auth (34 files, 1247 lines changed)**

Removals by pattern:
- Obvious comments: 12 instances across 8 files
- Console.log artifacts: 6 instances across 4 files
- Redundant type annotations: 5 instances across 3 files
- Unnecessary try/catch: 3 instances across 2 files
- React Fragment wrapping single child: 2 instances
- Unused imports: 4 instances across 3 files

Total: 32 removals, 47 lines removed

Flagged for review (3):
1. src/auth/login.ts:45 -- try/catch around token validation. May be intentional if tokens can be malformed.
2. src/components/UserCard.tsx:12 -- useCallback wrapping onClick. Child is not memoized but performance impact unknown.
3. src/utils/format.ts:8 -- Wrapper function around dayjs.format(). May be intentional abstraction for future customization.

Files skipped: 2 (migrations), 1 (generated types)
Slop density: 2.6/100 lines (Clean)
```

### Structured Report (for CI integration or automated tracking)

```json
{
  "branch": "feature/user-auth",
  "base": "main",
  "files_reviewed": 34,
  "files_skipped": 3,
  "total_lines_changed": 1247,
  "removals": 32,
  "lines_removed": 47,
  "flagged_for_review": 3,
  "slop_density": 2.6,
  "density_rating": "clean",
  "by_pattern": {
    "obvious_comment": 12,
    "console_log": 6,
    "redundant_type_annotation": 5,
    "unnecessary_try_catch": 3,
    "react_fragment_single_child": 2,
    "unused_import": 4
  }
}
```

## Multi-Commit Branch Handling

| Scenario | Approach |
|---|---|
| 5 commits, each adding a feature | Diff against base branch (three-dot diff). Deslop the final state, not individual commits. |
| Commits include "cleanup" commits | Still diff against base. AI "cleanup" commits often introduce new slop while fixing other issues. |
| Merge commits from main into feature branch | Use `git diff main...HEAD` to see only the feature branch changes. Merge commits are noise. |
| Interactive rebase was done before deslop | Good -- cleaner history. Diff against base as normal. |
| Deslop was already partially done in earlier commits | Check if the deslop commit introduced new issues. Compare pre-deslop and post-deslop diffs against base. |

## Common Batch Deslop Mistakes

| Mistake | Why It Happens | Prevention |
|---|---|---|
| Removing code in File A that File B depends on | Didn't check cross-file references before removal | For function/export removals, always `grep` for usages across the diff |
| Deslopping a generated file | File was in the diff because it was regenerated | Check for `@generated`, `AUTO-GENERATED`, or common generator markers before reviewing |
| Changing test assertions during deslop | Test had a verbose assertion style that looked like slop | Tests get relaxed rules. Only remove debug artifacts from tests, not assertion style. |
| Reporting every removal individually on a 50-file diff | User gets a wall of text | Use batch summary format for 10+ files. Individual line items only for flagged/uncertain removals. |
| Missing slop in files you scanned quickly | Time pressure on large diffs | Better to deslop high-impact files thoroughly than all files superficially |
| Applying strict rules to code outside the diff | "While I was in there" syndrome | The diff is the scope. Period. Surrounding code in the same file is context, not target. |

## Integration with Code Review

### When Deslop Runs Before Review

Ideal flow: AI writes code -> Deslop pass -> Human reviews clean code

Benefits:
- Reviewer focuses on logic, not style
- Fewer "nit" comments in review
- Review cycle is shorter

### When Deslop Runs During Review

Reviewer flags items -> Deslop addresses mechanical issues -> Reviewer re-checks logic only

Rules:
- Deslop only addresses items that match the pattern catalog
- If a reviewer flags something as "slop" that isn't in the catalog, discuss with reviewer -- it may be a new pattern to add
- Never change logic that a reviewer commented on -- that's the reviewer's domain

### When NOT to Deslop

| Situation | Why |
|---|---|
| Emergency hotfix branch | Speed > style. Deslop after the fire is out. |
| Code about to be deleted/replaced | Don't polish code that won't exist next sprint. |
| Proof-of-concept / throwaway branch | POC code has different quality standards. Save deslop for production paths. |
| Generated code that's checked in (Prisma client, GraphQL types, protobuf) | This code is regenerated. Your changes will be overwritten. |
