---
name: git-commit-helper
description: "Use when generating commit messages from git diffs, reviewing staged changes for commit readiness, or helping structure multi-file commits into atomic units. Also use when the user asks for help writing commit messages, splitting changes into separate commits, or determining commit scope and type. NEVER use for git workflow strategy (branching, merging, rebasing), git troubleshooting or error resolution, or pull request descriptions and reviews."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Git Commit Helper

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Diff analysis procedure, type selection, scope determination, commit sizing, summary/body rules, breaking change detection, anti-patterns | Always (auto-loaded) |
| code-review-science.md | How reviewers process diffs (eye-tracking research), 400 LOC review threshold (SmartBear study), cognitive load theory applied to commits, commit message as git blame retrieval interface, diff readability patterns (rename detection, indentation noise), review feedback latency by commit quality | When advising on commit splitting strategy, explaining WHY atomic commits matter with research backing, or diagnosing why PRs get slow/rubber-stamped reviews |
| git-internals-for-commits.md | Git object model (blob deduplication, tree sharing), bisect effectiveness by commit pattern (O(log n) vs degraded), rename detection heuristics (50% similarity threshold), merge vs squash vs rebase impact on history, cherry-pick/revert self-containment mechanics, reflog recovery, pack file efficiency | When explaining git internals affecting commit decisions, advising on merge strategy, or when user asks about bisect, cherry-pick, or revert implications |
| commit-automation-tooling.md | semantic-release commit parsing (which types trigger releases and which don't), commitlint rules and preset differences, monorepo conventions (Nx affected detection ignores commit scope), changelog generation quality, git hooks enforcement (husky gotchas, Windows line endings), commit signing (GPG vs SSH, vigilant mode), fixup/autosquash workflow | When setting up commit automation, working in monorepos, configuring commit signing, or debugging why automated releases aren't triggering |

Do NOT load companion files for basic commit message writing, simple type/scope selection, or standard diff analysis -- SKILL.md covers these fully.

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| Generating commit messages from staged diffs | YES | -- |
| Commit type and scope selection (conventional commits) | YES | -- |
| Splitting changes into atomic commits | YES | -- |
| Breaking change detection and formatting | YES | -- |
| Commit message body and footer conventions | YES | -- |
| Code review science for commit design | YES (via companion) | -- |
| Git internals affecting commit decisions | YES (via companion) | -- |
| Commit automation tooling (semantic-release, commitlint, hooks) | YES (via companion) | -- |
| Git workflow strategy (branching, merging, rebasing) | NO | git workflow tooling |
| Git troubleshooting and error resolution | NO | error-resolver |
| Pull request descriptions and reviews | NO | code review tooling |
| CI/CD pipeline configuration | NO | devops tooling |
| Code review process and methodology | NO | code review tooling |

## Diff Analysis Procedure

1. **Read the full diff**: Run `git diff --staged` and `git diff --staged --stat`. Understand every changed file before writing a message.
2. **Classify the change type**: Use the Type Selection table below. If multiple types apply, the changes should be split into separate commits.
3. **Determine scope**: Identify the most specific module, component, or system boundary affected. Use the Scope Determination method below.
4. **Draft the summary line**: Imperative mood, under 50 characters, no period. Describe the "why" in the body if the change isn't self-evident.
5. **Check for splitting needs**: Apply the Commit Sizing Rules. If the diff touches unrelated concerns, advise splitting before committing.

## Type Selection Decision Table

| Type | Use When | NOT When |
|---|---|---|
| `feat` | New user-facing capability that didn't exist before | Extending existing feature behavior (use `fix` or `refactor`) |
| `fix` | Correcting behavior that was wrong or broken | Changing behavior that worked but needs improvement (use `refactor`) |
| `refactor` | Restructuring code without changing external behavior | Adding new behavior (use `feat`) or fixing bugs (use `fix`) |
| `docs` | Only documentation files changed (README, JSDoc, comments) | Code changes alongside documentation updates (use the code's type) |
| `style` | Formatting, whitespace, semicolons, linting -- zero logic changes | Any change that affects runtime behavior |
| `test` | Only test files added or modified | Test changes alongside the code they test (use the code's type) |
| `chore` | Build scripts, CI config, dependency updates, tooling | Any change that affects application source code |
| `perf` | Measurable performance improvement with no behavior change | Speculative optimization or refactoring disguised as perf |

**Ambiguity rule**: When a change spans multiple types (e.g., feat + test + docs), use the type of the primary change. If truly independent, split into separate commits.

## Scope Determination Method

Scope identifies the area of the codebase affected. It goes inside parentheses: `type(scope): description`.

| Scope Source | Example | When to Use |
|---|---|---|
| Feature/module name | `feat(auth)`, `fix(payments)` | Changes contained within one feature boundary |
| Layer name | `refactor(api)`, `fix(db)` | Changes span features but stay in one architectural layer |
| Component name | `feat(navbar)`, `fix(user-form)` | Frontend component-scoped changes |
| File/package name | `chore(eslint)`, `docs(readme)` | Single-file changes or config updates |
| No scope | `fix: handle null in response` | Change is too cross-cutting for a meaningful scope |

**Scope selection priority**: Feature > Component > Layer > File. Pick the most specific scope that accurately describes the blast radius.

## Commit Sizing Rules

Each commit should represent one atomic, logical change. Apply these rules to determine if a diff should be split.

| Signal | Action |
|---|---|
| Diff touches 2+ unrelated features | Split into separate commits per feature |
| Bug fix mixed with refactoring | Commit the fix first, then the refactor separately |
| New feature includes test file changes | Keep together -- feat + its tests are one logical unit |
| Formatting changes mixed with logic changes | Commit formatting as `style` first, then the logic change |
| Dependency update mixed with code changes that use it | Commit `chore` dependency update first, then `feat`/`fix` using it |
| Migration file + model change | Keep together -- they're one logical unit |
| File renamed AND content modified | Split: rename-only commit first, then content changes. Git's rename detection needs >50% content similarity; combined changes break `git log --follow` and blame history |
| Diff exceeds ~400 lines changed | Consider splitting even within one feature. Code review research (SmartBear/Cisco, 2500+ reviews) shows defect detection drops from 70-90% under 200 LOC to <20% above 800 LOC |

**Splitting command**: Use `git add -p` to stage specific hunks, or `git add <file>` for file-level splitting.

## Summary Line Rules

| Rule | Good | Bad |
|---|---|---|
| Imperative mood | `add user validation` | `added user validation`, `adding user validation` |
| Under 50 characters | `fix null check in profile` | `fix the issue where profile crashes when user data is null` |
| Capitalize first letter | `Add login endpoint` | `add login endpoint` |
| No trailing period | `Update auth middleware` | `Update auth middleware.` |
| Describe the "what" concisely | `add JWT authentication` | `update code` |
| Be specific | `fix race condition in queue` | `fix bug` |

## Body Writing Guide

The body explains "why" -- the summary already covers "what". Include a body when any of these apply:

| Include Body When | Body Should Contain |
|---|---|
| The change isn't obvious from the diff | Motivation and context for the approach |
| There were alternative approaches considered | Brief mention of what was tried and why this path was chosen |
| The change has side effects | What other behavior is affected |
| There's a breaking change | `BREAKING CHANGE:` footer with migration instructions |
| The commit closes an issue | `Closes #123` or `Fixes #456` footer |

**Body formatting**: Wrap at 72 characters. Separate from summary with a blank line. Use bullet points for multiple items. Put `BREAKING CHANGE:` in a footer section, not in the summary.

## Breaking Change Detection

| Signal in Diff | Likely Breaking Change |
|---|---|
| Function/method signature changed (params added/removed/reordered) | Yes -- callers must update |
| API response structure changed | Yes -- clients must update |
| Environment variable renamed or removed | Yes -- deployment configs must update |
| Database column dropped or renamed | Yes -- queries and ORM mappings must update |
| Default behavior changed | Maybe -- depends on whether consumers rely on the default |
| Internal refactor with unchanged public API | No -- not breaking |

**Breaking change format**: Add `!` after type/scope in summary (`feat(api)!: restructure response`), plus `BREAKING CHANGE:` footer with migration details.

## Commit Anti-Patterns

| Name | Anti-Pattern | Why It Fails | Fix |
|---|---|---|---|
| The Kitchen Sink | One commit with 500+ lines across 10+ files covering a feature, a bug fix, and "some cleanup" | Impossible to bisect, revert, or cherry-pick any single concern. Code review drops to <20% defect detection above 800 LOC (SmartBear). Reviewer rubber-stamps it | Split into atomic commits per concern BEFORE committing. Use `git add -p` for hunk-level staging |
| The Cryptic One-Liner | `fix: update` or `chore: changes` with no body | `git blame` 6 months later returns zero useful context. `git log --oneline` becomes a wall of meaningless noise. Bisect identifies the commit but not the reasoning | Write a specific summary (what changed) and body (why it changed, what alternatives were considered) |
| The Stealth Refactor | Bug fix commit that also "cleans up" surrounding code while fixing the bug | Reviewer must run two parallel analyses (is the refactor correct? does the fix work?) with 20-40% cognitive penalty per context switch. If the fix needs revert, refactoring is also lost | Commit the bug fix alone. Commit the refactoring separately. Each is independently reviewable and revertable |
| The Time Capsule | 3 days of uncommitted work, squashed into one massive commit | No intermediate reasoning visible. Bisect useless within the mega-commit. If using semantic-release, one huge `feat` triggers one minor bump when 3 separate features deserve 3 separate changelog entries | Commit atomically as you work. Use `--fixup` for corrections, then `rebase --autosquash` before merge |
| The Breadcrumb Trail | 50+ tiny WIP commits: "wip", "fix typo", "try again", "actually fix", "oops" | Signal-to-noise ratio too low for `git log`. Bisect lands on broken intermediate states. Changelog generation produces garbage entries | Use fixup/autosquash workflow: commit WIP as `--fixup=SHA`, then clean up with `rebase -i --autosquash` before merging |
| The Silent Rename | File renamed AND content modified in the same commit | Git's rename detection requires >50% content similarity. Combined changes break detection -- diff shows full file delete + add. `git log --follow` and `git blame` history permanently broken | Commit renames separately from content changes. Zero extra effort, permanent history benefit |
| The Versioning Ghost | Commit uses `chore:` or `docs:` for a user-facing change | semantic-release ignores non-feat/fix types. No release triggered, no changelog entry, no version bump. User-facing change is invisible to consumers | Use `feat:` or `fix:` for anything that changes user-visible behavior, even if the code change feels like maintenance |
| The Unsigned Impersonator | Commits in a signed-commit repository without signing configured | GitHub Vigilant Mode shows "Unverified" badge. In security-sensitive projects, unsigned commits may be rejected by branch protection rules. CI-generated commits (bot merges) are often silently unsigned | Configure GPG or SSH signing (git 2.34+). Add signing key to GitHub as BOTH auth AND signing key |

## Recommendation Confidence

| Area | Confidence | Override When |
|---|---|---|
| Atomic commits (one logical change per commit) | HIGH | Only bundle when changes are truly inseparable (migration + model, feature + its tests). Even then, verify the bundle passes the cherry-pick self-containment test |
| Conventional commit format (type(scope): subject) | HIGH | When the team uses a different convention (Gitmoji, Angular, custom). Match the team's standard, not the general convention. Consistency within a project matters more than following any specific standard |
| Summary under 50 characters | MEDIUM | GitHub truncates at 72, not 50. The 50-char rule comes from `git log --oneline` readability. If the team uses 72 as the limit, that's fine -- pick one and enforce it |
| Imperative mood in summary | HIGH | Some teams prefer past tense ("added", "fixed"). The imperative convention exists because it reads as a command ("apply this commit and it will: add user validation"). But consistency trumps convention |
| Commit body for non-obvious changes | HIGH | Trivial changes (typo fixes, single-line bug fixes) where the diff IS the explanation. If you'd need to read the body to understand the diff, the body is mandatory |
| Splitting formatting from logic changes | HIGH | Only combine when the formatting change is specifically required by the logic change (e.g., extracting a function also changes indentation of the surrounding code). Even then, consider if they can be separated |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "I'll just write 'update' or 'fix stuff'" | Vague messages make `git log`, `git bisect`, and `git blame` useless; future developers (including you) need to understand why each change was made |
| "This is a small project, commit messages don't matter" | Small projects grow; commit discipline established early prevents archaeology problems later when onboarding contributors or debugging regressions |
| "I'll split it later with interactive rebase" | Interactive rebase of mixed commits is error-prone and time-consuming; staging atomically upfront takes seconds |
| "The diff is self-explanatory, no body needed" | Diffs show what changed, not why; six months later the motivation is lost if not recorded |
| "Everything in this branch is related, one big commit is fine" | Large commits make `git bisect` useless, code review harder, and selective reverts impossible |
| "Breaking changes are obvious from context" | Downstream consumers may not read every commit; the `BREAKING CHANGE` footer is a machine-parseable signal that tooling depends on |

## Red Flags

- Commit message is "update", "fix", "changes", "WIP", or any single generic word -- makes `git log`, `git bisect`, and `git blame` return zero useful context
- Diff touches 5+ unrelated files with no logical connection -- code review defect detection drops below 20% for 800+ LOC changes (SmartBear study)
- Bug fix and feature addition in the same commit -- revert of the bug fix also reverts the feature; cherry-pick of the feature also brings the bug fix
- Summary line exceeds 72 characters -- GitHub truncates at 72 in the commit list view, hiding the most important part of the message
- No scope on a commit that clearly affects one module -- automated changelog groups entries by scope; missing scope creates an "ungrouped" section
- Past tense in summary ("fixed", "added", "updated" instead of imperative) -- breaks consistency with git's own generated messages (`Merge branch`, `Revert "..."`)
- Commit includes unrelated formatting changes mixed with logic changes -- the formatting diff noise obscures the actual logic change, causing reviewers to miss bugs
- File renamed AND modified in the same commit -- git's rename detection fails above 50% content change, permanently breaking `git log --follow` and blame history

## NEVER

- Generate a commit message without first reading the actual diff -- the message must accurately reflect the changes, not guess from file names
- Use `git add .` or `git add -A` without reviewing what's staged -- this catches unintended files (`.env`, `node_modules`, build artifacts, OS files)
- Write a commit message that describes the intent but not the actual change -- if the code doesn't match the message, the message is a lie in the log
- Combine unrelated changes into one commit to "save time" -- atomic commits are the foundation of effective `git bisect`, `git revert`, and code review
- Skip the breaking change footer when public API contracts change -- automated changelog generators and downstream dependency tools rely on this signal
