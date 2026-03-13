# Git Internals for Commit Design

How git actually stores and processes commits -- and why certain commit patterns make operations like bisect, revert, cherry-pick, and merge dramatically easier or harder.

## Git Object Model (Commit-Relevant Parts)

Every commit in git is a DAG node pointing to a tree object (snapshot of all files), parent commit(s), and metadata (author, message, timestamp).

| Object Type | What It Stores | Size Impact of Commits |
|---|---|---|
| Blob | File contents (deduplicated by SHA-1) | Identical files across commits share the same blob. Changing one byte creates a new blob for the ENTIRE file |
| Tree | Directory listing (filename -> blob SHA mappings) | Each commit stores a full tree snapshot, not a delta. Trees share unchanged subtrees via hash reuse |
| Commit | Pointer to tree, parent(s), author, message | ~200-500 bytes per commit regardless of change size. Commits are cheap -- the data is in blobs |
| Tag | Pointer to a commit + annotation | Annotated tags reference commits; lightweight tags are just refs |

**Key insight**: Commits are nearly free in storage terms. The blobs exist regardless of how many commits reference them. Making 5 atomic commits instead of 1 large commit adds ~2KB of overhead. The "save commits" instinct is a false economy.

## Why Atomic Commits Make Bisect O(log n) Effective

`git bisect` performs binary search over commit history to find the commit that introduced a bug. Its effectiveness depends entirely on commit atomicity.

| Commit Pattern | Bisect Behavior | Bisect Effectiveness |
|---|---|---|
| Each commit = one logical change | Bisect finds the exact commit. Done. | O(log n) -- optimal |
| Commits mix 2-3 concerns | Bisect finds the commit, but you still need to manually identify which change within it caused the bug | O(log n) to find commit, then O(m) manual analysis where m = number of mixed concerns |
| Large "squash everything" commits | Bisect narrows to a huge commit. You're now manually debugging the entire change | Effectively O(n) -- bisect can't help within a mega-commit |
| WIP commits with broken intermediate states | Bisect lands on a broken commit, can't determine if the bug is from the WIP or the real change | Bisect fails entirely -- `git bisect skip` repeatedly, losing the binary search advantage |

**The bisectability rule**: Every commit in the history should: (1) compile/build successfully, (2) pass existing tests, (3) represent exactly one logical change. If any commit violates these, `git bisect` becomes unreliable for the entire range.

**Practical threshold**: For a repository with 1000 commits, bisect needs ~10 steps to find a bug. But if 20% of commits mix concerns, the average post-bisect manual analysis adds 3-5 steps, reducing effectiveness by 30-50%.

## Rename Detection Heuristics

Git doesn't track renames explicitly. It infers them by comparing deleted and added files using content similarity.

| Detection Parameter | Default | What It Means |
|---|---|---|
| `-M` threshold | 50% | Files must share >50% of content to be detected as renamed. Below this, git sees delete + add |
| `-C` threshold | 50% | Same as -M but also detects copies across files |
| Break threshold (`-B`) | 50%/50% | If file changes >50%, git may break the rename pairing and show as delete + add |
| Rename limit | 1000 files | Git stops checking rename pairs after 1000 candidates. Large commits with many file changes may miss renames entirely |

**Commit implications**:
- Rename-only commits (no content change): Git detects these perfectly. `git log --follow` works. Diff shows `renamed: old -> new` with 0 lines changed
- Rename + small edit (<50% change): Git detects the rename. Diff shows the rename plus only the changed lines
- Rename + major rewrite (>50% change): Git CANNOT detect the rename. Shows as file deleted + new file added. `git log --follow` breaks. All blame history is lost
- **Best practice**: Always commit renames separately from content changes. The cost is one extra commit (trivial). The benefit is preserved blame history and clean diffs

## Merge vs Squash vs Rebase: Commit Structure Impact

How you integrate branches back to main affects which commits exist in final history and how operations work on them.

| Strategy | Commit History | Bisect Impact | Revert Impact | Blame Impact |
|---|---|---|---|---|
| Merge commit | All branch commits preserved + merge commit | Bisect can trace into branches; full granularity | Can revert individual commits or entire merge | Full blame history with branch context |
| Squash merge | All branch commits collapsed into ONE commit | Bisect sees one large commit; loses granularity within the feature | All-or-nothing revert of entire feature | Blame shows one author for all changes |
| Rebase + fast-forward | All branch commits replayed onto main linearly | Bisect has full granularity; linear history makes it fastest | Can revert individual commits | Full blame history but loses branch context |

**The squash trap**: Squash merging feels clean (one commit per feature!) but destroys the atomic commits you carefully crafted on the branch. If you wrote 8 well-structured commits during development, squashing erases all that work. Use squash ONLY when branch commits are messy WIP that you don't want in history.

**Rebase advantage for bisect**: Linear history (rebase + fast-forward) is the fastest for bisect because there are no merge commits to navigate around. Every step in bisect is a real change, not a merge.

## Cherry-Pick and Revert Mechanics

Both operations replay a commit's diff. Their success depends entirely on the commit being self-contained.

| Commit Quality | Cherry-Pick Success | Revert Success |
|---|---|---|
| Atomic (one logical change, all related files) | High -- the diff applies cleanly to other branches | High -- reversing the change doesn't affect unrelated code |
| Mixed (two concerns in one commit) | Low -- cherry-pick brings the unwanted change along. You must manually undo the extra part | Low -- reverting also undoes the part you want to keep. Partial revert requires manual editing |
| Dependent (assumes previous commit's changes) | Fails unless previous commit is also cherry-picked. Creates a dependency chain | Revert may break functionality that depends on this commit's changes |
| Reformatting mixed with logic | Cherry-pick succeeds but pollutes the target branch with formatting changes not matching its standards | Revert undoes both formatting and logic -- formatting must be reapplied manually |

**Self-containment test**: Before committing, ask: "Could this commit be cherry-picked to a release branch without bringing unrelated changes?" If no, it's not atomic enough.

## Commit Timestamps and Ordering

Git has TWO timestamps per commit: AuthorDate (when the change was originally written) and CommitDate (when the commit object was created, e.g., after rebase). This matters for commit ordering.

| Scenario | AuthorDate | CommitDate | Which to Trust |
|---|---|---|---|
| Normal commit | Same as CommitDate | Current time | Either (they match) |
| After `git rebase` | Original time | Rebase time | AuthorDate for "when was this written?" |
| After `git commit --amend` | Original time (preserved) | Amend time | CommitDate for "when was this finalized?" |
| After `git cherry-pick` | Original author's time | Cherry-pick time | AuthorDate for attribution, CommitDate for "when did this land?" |

**Gotcha**: `git log` shows AuthorDate by default. `git log --format="%cD"` shows CommitDate. In rebased histories, commits may appear out of chronological order by AuthorDate -- this is normal and expected.

## Reflog: The Undo Safety Net

Commits are never truly deleted (for ~90 days). The reflog records every HEAD movement.

| Situation | Recovery Command | Limitation |
|---|---|---|
| Accidentally amended the wrong commit | `git reflog` -> find pre-amend SHA -> `git reset --hard SHA` | Only works locally; if you pushed the amended commit, remote history is already changed |
| Lost commits after bad rebase | `git reflog` -> find pre-rebase SHA -> `git reset --hard SHA` | Works as long as the rebase was local. Force-pushed rebase = remote history lost |
| Deleted branch with unmerged commits | `git reflog` -> find branch tip SHA -> `git branch recovered SHA` | Commits expire from reflog after `gc.reflogExpire` (default 90 days) |
| Reset --hard dropped working changes | `git reflog` shows the reset, but UNSTAGED changes are gone | Reflog tracks commits, not working directory. Unstaged changes are unrecoverable |

**Commit-level implication**: Committing frequently (even with `--fixup` for later squashing) is cheap insurance. Uncommitted work is unrecoverable after `reset --hard`. Committed work is recoverable from reflog for 90 days.

## Pack Files and Commit Patterns

Git periodically packs loose objects into `.pack` files using delta compression. The packing algorithm works best when similar blobs are near each other.

| Commit Pattern | Pack Efficiency | Why |
|---|---|---|
| Small, incremental changes to the same files | Excellent -- deltas between versions are small | Pack algorithm finds high-similarity blobs easily; delta chains are short |
| Large reformatting commits | Poor -- every reformatted file gets a new blob with low similarity to the pre-format version | Delta compression has more work; pack files grow |
| Binary files committed frequently | Very poor -- binary diffs are rarely compressible | Each version stored nearly in full; repository size grows linearly |
| Vendored dependencies checked in | Poor -- thousands of files that change together on updates | Better to use lockfile + .gitignore; let package managers handle vendored copies |

**Repository size rule**: Commit size doesn't directly affect clone/fetch speed (git packs efficiently). But committing TYPES of content that compress poorly (binaries, generated files, vendored deps) permanently inflates repository size. Keep `.gitignore` strict and commit only source files.
