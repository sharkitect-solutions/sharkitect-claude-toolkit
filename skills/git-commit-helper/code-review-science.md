# Code Review Science for Commit Design

How developers actually read diffs -- research findings that should inform how you structure commits and write messages. Most commit advice focuses on the writer; this focuses on the reader.

## How Reviewers Process Diffs

Developers don't read diffs linearly. Eye-tracking studies (Uwano et al. 2006, Sharif et al. 2012) show a scan-then-focus pattern: reviewers scan the file list first, mentally categorize changes, then deep-read only sections they flagged as risky.

| Review Phase | What Happens | Commit Implication |
|---|---|---|
| File list scan (5-15 seconds) | Reviewer reads filenames to build a mental model of change scope | Commits touching unrelated files force the reviewer to build TWO mental models simultaneously, splitting attention |
| Hunk triage (10-30 seconds per file) | Reviewer skims each hunk to classify: trivial/important/dangerous | Mixed trivial+dangerous changes in one commit waste triage time -- the reviewer can't skip trivial hunks without risking missing the dangerous one |
| Deep read (1-3 minutes per significant hunk) | Reviewer traces logic, checks edge cases, verifies correctness | Large hunks (>50 lines changed in one block) exceed working memory (~7 items); comprehension drops sharply |
| Context reconstruction (variable) | Reviewer tries to understand WHY, not just WHAT | If the commit message doesn't explain motivation, the reviewer must reverse-engineer intent from code -- error-prone and slow |

## Optimal Commit Size for Review Effectiveness

**The 400 LOC threshold** (SmartBear/Cisco Code Review study, 2,500+ reviews analyzed): Defect detection rate drops dramatically above 400 lines of code changed.

| Lines Changed | Defect Detection Rate | Review Time | Reviewer Experience |
|---|---|---|---|
| 1-100 | 70-90% of defects found | 10-20 minutes | Focused, thorough |
| 100-200 | 60-75% of defects found | 20-40 minutes | Engaged but tiring |
| 200-400 | 40-60% of defects found | 40-75 minutes | Fatigue begins, skimming increases |
| 400-800 | 20-40% of defects found | 60-90 minutes | Significant skimming, "LGTM" temptation |
| 800+ | <20% of defects found | Variable (often abandoned mid-review) | Rubber-stamping; reviewer gives up on thoroughness |

**Key finding**: Review effectiveness per line of code is INVERSELY proportional to total change size. A 50-line commit gets 10x more scrutiny per line than a 500-line commit. Splitting a 500-line change into 5 atomic commits doesn't just help git history -- it multiplies the review quality of every line.

**Review speed ceiling**: Reviewers shouldn't exceed 500 LOC per hour (SmartBear). Beyond this, comprehension drops and defects are missed. A 1000-line PR reviewed in 30 minutes was rubber-stamped, not reviewed.

## Cognitive Load Theory Applied to Commits

**Working memory limit** (Miller 1956, refined by Cowan 2001): Humans hold 4 +/- 1 chunks in working memory at once, not the often-cited 7. Each "chunk" in code review context is roughly one logical concern.

| Commit Pattern | Cognitive Load | Why |
|---|---|---|
| Single concern, single module | LOW (1 chunk) | Reviewer tracks one idea in one place |
| Single concern, multiple files | MODERATE (1-2 chunks) | One idea, but reviewer must hold the thread across files |
| Multiple concerns, single file | HIGH (2-4 chunks) | Reviewer must mentally separate interleaved changes |
| Multiple concerns, multiple files | OVERLOAD (4+ chunks) | Reviewer can't distinguish which changes serve which purpose |

**The interleaving problem**: When a commit mixes refactoring with a bug fix, the reviewer must run two parallel analyses: "Is this refactoring correct?" and "Does this fix the bug?" Errors in one analysis contaminate the other. Research on task switching (Monsell 2003) shows a 20-40% performance penalty per context switch.

**Implication for commit splitting**: The cost of creating two separate commits (30 seconds of `git add -p`) is trivially small. The benefit to the reviewer (avoiding interleaved analysis) saves minutes and catches more bugs.

## Commit Message as Knowledge Retrieval Interface

`git blame` is used 3-8x more often than `git log` for understanding code (based on developer workflow studies). This means commit messages serve primarily as inline documentation, not as a changelog.

| Retrieval Context | What the Reader Needs | Message Requirement |
|---|---|---|
| `git blame` on a confusing line | Why this line exists; what problem it solves | Body must explain motivation, not just what changed |
| `git bisect` for a regression | Which commit introduced the bug | Summary must be specific enough to recognize relevance without reading the diff |
| `git log --oneline` for recent history | Quick scan of what changed this week | Summary under 50 chars, meaningful type and scope |
| `git log -p` for deep archaeology | Full context of a past decision | Body should mention alternatives considered and why they were rejected |
| `git shortlog` for release notes | User-facing change description | `feat` and `fix` messages must make sense to non-developers |

**The 6-month test**: Write every commit message as if you'll read it via `git blame` 6 months from now, having completely forgotten the context. If the message doesn't reconstruct your reasoning, it's insufficient.

## Diff Readability Patterns

Not all diffs are equally readable. Some code changes produce clean, reviewable diffs; others produce noise that obscures the real change.

| Diff Problem | Cause | Commit-Level Fix |
|---|---|---|
| Massive rename diff (hundreds of lines) | Renamed a file or moved code | Commit the rename SEPARATELY from content changes. Git detects renames only when the file content is 50%+ similar (configurable with `-M` threshold). If you rename AND modify, git shows delete+add instead of rename |
| Indentation noise (every line shows as changed) | Reformatted or changed nesting level | Commit formatting separately as `style`. Reviewers can then skip the `style` commit entirely |
| Import reordering at top of file | Auto-formatter or new dependency | If meaningful code also changed, the import changes bury the real diff. Consider `.gitattributes` with `diff=` drivers for import sections |
| Whitespace-only changes (trailing spaces, line endings) | Editor settings mismatch | Configure `.editorconfig` and `.gitattributes` once (as a `chore` commit), then never deal with this again |
| Generated file changes (lockfiles, compiled assets) | Dependency update or build | Commit lockfile changes with the `chore` dependency update. Never mix lockfile changes with feature code |

**The 50% similarity threshold**: Git's rename detection (`-M` flag, default 50%) compares file content between delete and add. If you rename `utils.js` to `helpers.js` AND change 60% of the content in the same commit, git won't detect it as a rename -- it shows as one file deleted and one new file added. Splitting into rename-then-modify produces a clean diff that shows the actual changes.

## Review Feedback Latency Research

Rigby & Bird (2013, "Convergent Contemporary Software Peer Review Practices") found that review turnaround time correlates with commit quality:

| Commit Quality | Median Review Turnaround | Revision Requests |
|---|---|---|
| Small, atomic, well-described | 2-4 hours | 0-1 rounds |
| Medium, mostly atomic, adequate message | 4-12 hours | 1-2 rounds |
| Large, mixed concerns, vague message | 1-3 days | 2-4 rounds |
| Very large, unclear scope, no message body | 3-7 days (often abandoned) | N/A -- reviewer requests split first |

**The review tax**: Every round of revision feedback adds 12-24 hours of calendar time (developer must context-switch back to the change). A 3-round review cycle on a sloppy commit costs 2-4 days. Writing a clean, atomic commit with a good message costs 2-5 minutes upfront.

## Named Anti-Patterns (Reviewer's Perspective)

| Name | Pattern | Why Reviewers Hate It |
|---|---|---|
| The Shotgun Commit | 15+ files changed across unrelated modules | Reviewer can't hold the change scope in working memory; defaults to rubber-stamping |
| The Stealth Refactor | Bug fix that also "cleans up" surrounding code | Reviewer can't verify the fix without understanding the refactoring; two analyses interleaved |
| The Time Capsule | Commit from 3 days of uncommitted work, squashed into one | No intermediate reasoning visible; reviewer sees the end state but not the journey of decisions |
| The Breadcrumb Trail | 50+ tiny commits of WIP ("wip", "fix typo", "try again") | Reviewer can't find the meaningful changes; signal-to-noise ratio too low for `git log` or `git bisect` |
| The Silent Rename | File renamed AND content modified in one commit | Git can't detect the rename; diff shows full file delete + add instead of the actual 5-line change |
