# Commit Automation & Tooling

How automated tools parse, validate, and act on commit messages -- and the specific gotchas that cause failures when your commit format doesn't match what the tools expect.

## Semantic Release: Commit-Driven Versioning

semantic-release automates version bumps and changelog generation by parsing commit messages. It's the most common consumer of conventional commits in CI/CD.

| Commit Type | Version Bump | Changelog Section | Notes |
|---|---|---|---|
| `fix:` | PATCH (0.0.x) | Bug Fixes | Only `fix` triggers a patch release. `chore`, `docs`, `style`, `test` trigger NO release |
| `feat:` | MINOR (0.x.0) | Features | New capabilities. Must be user-facing to justify a minor bump |
| `BREAKING CHANGE:` in footer | MAJOR (x.0.0) | Breaking Changes | Footer or `!` after type both work. Either triggers major regardless of type |
| `perf:` | No release (default) | Not included | Requires custom configuration to trigger a release. Most setups ignore it |
| `refactor:` | No release (default) | Not included | Internal change; no user-facing impact = no version bump |

**Critical gotcha -- no release triggered**: If your commit uses `chore:`, `docs:`, `test:`, `style:`, or `refactor:`, semantic-release will NOT create a release. Developers often wonder why their deploy didn't trigger -- it's because the commit type didn't match the release rules.

**Multi-branch configuration**:

| Branch | Default Behavior | Gotcha |
|---|---|---|
| `main` / `master` | Releases to `latest` dist-tag | Merging a `feat` commit triggers immediate release. No manual gate |
| `next` / `beta` / `alpha` | Pre-release versions (1.0.0-beta.1) | Pre-release commits must also follow conventional format; informal messages break the chain |
| Feature branches | No releases | Commits here still matter -- they'll be parsed when merged to a release branch |

**The squash merge problem**: If you squash-merge a branch with 5 well-typed commits into one commit with message "Merge feature X", semantic-release sees ONE commit with type... nothing (no conventional prefix). No release happens. Either: (1) use merge commits (preserves individual commit types), (2) rewrite the squash commit message with proper conventional format, or (3) configure semantic-release to parse PR titles instead.

## Commitlint: Message Validation

commitlint validates commit messages against configurable rules, typically run as a git hook.

| Rule | Default (Conventional) | Common Custom Override | Gotcha |
|---|---|---|---|
| `type-enum` | feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert | Add custom types: `wip`, `release`, `deps` | Adding `wip` to allowed types lets WIP commits into history -- semantic-release ignores them, so they're invisible to versioning but pollute the log |
| `subject-max-length` | 100 characters | 72 characters (GitHub truncation point) | Default is 100, but GitHub truncates at 72. Most teams should lower this |
| `subject-case` | `lower-case` | Some teams prefer `sentence-case` | Mixing cases breaks automated changelog grouping. Pick one and enforce |
| `body-max-line-length` | 100 characters | `Infinity` (disable) | Some teams disable this because long URLs in commit bodies trigger violations |
| `scope-enum` | Not enforced | Restrict to known module names | Unenforced scope allows typos (`auth` vs `authn` vs `authentication`) that fragment changelog sections |
| `header-max-length` | 100 characters | 72 characters | The "header" is type + scope + subject combined. A 50-char subject + `feat(authentication):` already uses 70 chars |

**Preset differences**:

| Preset | Type Format | Scope Format | Breaking Change |
|---|---|---|---|
| `@commitlint/config-conventional` | `type: subject` | `type(scope): subject` | `BREAKING CHANGE:` footer or `!` |
| `@commitlint/config-angular` | Same as conventional | Same | Same (Angular created the convention) |
| `@commitlint/config-lerna-scopes` | Same | Scopes auto-generated from package names in monorepo | Same |

**The hook bypass problem**: `git commit --no-verify` skips the commitlint hook entirely. Developers under pressure use this to skip validation. Defense: also run commitlint in CI on push (not just as a local hook). The CI check catches bypassed hooks.

## Monorepo Commit Conventions

Monorepos (Nx, Turborepo, Lerna) add complexity because one commit may affect multiple packages.

| Pattern | Convention | Tool Support |
|---|---|---|
| Single package change | `feat(package-name): add feature` | All tools handle this correctly |
| Multiple packages, one concern | `feat(core,utils): shared validation` | commitlint allows multiple scopes with config. semantic-release needs plugins to handle multi-package releases |
| Root-level change (CI, config) | `chore(root): update eslint config` or `chore: update eslint config` | No scope means all packages may be affected. Nx/Turborepo use `affected` detection based on file paths, not commit scopes |
| Cross-package breaking change | `feat(api)!: restructure response` -- only marks `api` as breaking | Other packages depending on `api` also need major bumps. Manual coordination required |

**Nx affected gotcha**: Nx determines which packages are affected by examining which files changed (file-based), NOT by parsing commit scopes. A commit scoped `feat(auth)` that also touches `packages/billing/src/index.ts` will trigger Nx rebuild for both `auth` AND `billing`, regardless of scope. The commit scope is for humans and changelog; Nx ignores it.

**Lerna versioning modes**:
- `fixed` mode: All packages share one version. ANY conventional commit bumps ALL packages. Simple but wasteful (unchanged packages get version bumps)
- `independent` mode: Each package versioned separately. Commits must be scoped to the correct package. A missing or wrong scope means the wrong package gets bumped

## Automated Changelog Generation

| Tool | Input | Output Format | Grouping |
|---|---|---|---|
| `conventional-changelog` | Git commits | CHANGELOG.md | By type (Features, Bug Fixes, etc.) |
| `auto-changelog` | Git commits + PR titles | CHANGELOG.md | By merge date or tag |
| `release-please` (Google) | Git commits | CHANGELOG.md + GitHub Release | By type, with PR links |
| `changesets` | Manual changeset files, not commits | CHANGELOG.md | By changeset content |

**Changelog quality depends entirely on commit quality**:

| Commit Message | Changelog Entry | Reader Experience |
|---|---|---|
| `feat(auth): add SSO support for SAML providers` | **Features**: auth: add SSO support for SAML providers | Clear, useful, scannable |
| `feat: update` | **Features**: update | Useless -- reader has no idea what changed |
| `fix(api): handle null response from payment gateway (#234)` | **Bug Fixes**: api: handle null response from payment gateway (#234) | Clear with issue link for context |
| `fix stuff` | Not included (doesn't match conventional format) | Invisible -- the fix isn't documented |

**The changelog test**: Before committing, read your summary line as a changelog bullet point. Would a user or developer scanning the changelog understand what changed? If not, rewrite it.

## Git Hooks for Commit Enforcement

| Hook | Trigger | Purpose | Tool |
|---|---|---|---|
| `commit-msg` | After message is written, before commit is created | Validate message format | commitlint, gitlint |
| `pre-commit` | Before commit, after staging | Lint, format, test staged files | husky + lint-staged, pre-commit (Python) |
| `prepare-commit-msg` | Before editor opens | Pre-populate message template | Custom script (e.g., inject branch name as scope) |
| `post-commit` | After commit is created | Notifications, logging | Custom script |

**husky + lint-staged configuration gotchas**:

| Gotcha | What Happens | Fix |
|---|---|---|
| husky not installed after clone | New contributors don't get hooks. Commits bypass validation | Add `"prepare": "husky"` to package.json scripts. Runs on `npm install` |
| lint-staged runs on ALL files, not just staged | Formatter changes unstaged files, creating surprise diffs | Verify lint-staged config uses the staged files list (default behavior). Don't add `git add` to lint-staged tasks (v12+ handles this) |
| Hook fails on `npx --no-install` in CI | CI image doesn't have husky installed | Use `HUSKY=0` env var in CI to skip hooks (CI should run linting separately) |
| Windows line endings trigger formatting hook | Git converts CRLF->LF on commit, triggering the formatter to "fix" already-formatted files | Configure `.gitattributes`: `* text=auto eol=lf` and `.editorconfig`: `end_of_line = lf` |

## Commit Signing

Commit signing cryptographically verifies authorship. Two methods are in common use.

| Method | Setup | Verification | Gotcha |
|---|---|---|---|
| GPG signing | Generate GPG key, add to git config, upload public key to GitHub | Green "Verified" badge on GitHub | Key expires by default (2 years). Expired key = commits show "Expired" not "Verified". Set `--expire-date 0` for no expiry, or have a rotation plan |
| SSH signing (git 2.34+) | Use existing SSH key from `~/.ssh/`. Configure `git config gpg.format ssh` | Green "Verified" badge on GitHub (since 2022) | Must add SSH key to GitHub as BOTH authentication key AND signing key (separate settings). Missing the signing key upload means locally-signed commits show "Unverified" on GitHub |

**GitHub Vigilant Mode**: When enabled, GitHub marks ALL unsigned commits as "Unverified" (instead of showing no badge). This creates pressure to sign every commit, including automated ones. Gotcha: GitHub Actions bot commits aren't signed by default -- configure the `actions/checkout` action with GPG key to sign CI-generated commits.

**The `--no-gpg-sign` escape hatch**: During interactive rebase or autosquash, git may fail on signing for each replayed commit. Quick fix: `git -c commit.gpgsign=false rebase ...`. But this creates unsigned commits in signed-commit-required repositories. Better: ensure signing works reliably first.

## Fixup and Autosquash Workflow

For iterative development where you want atomic final commits but messy intermediate work.

| Command | Creates | Autosquash Behavior |
|---|---|---|
| `git commit --fixup=SHA` | Commit with `fixup! original message` prefix | `git rebase -i --autosquash` melts it into the original commit, using original's message |
| `git commit --squash=SHA` | Commit with `squash! original message` prefix | Autosquash combines it with original and opens editor to merge messages |
| `git commit --fixup=amend:SHA` | Commit with `amend! original message` prefix | Replaces the original commit's message entirely (git 2.32+) |

**The workflow**:
1. Make your clean atomic commits on the branch
2. During review, get feedback requiring changes to commit 3 of 5
3. Make the fix, then `git commit --fixup=<commit-3-SHA>`
4. After all review fixes: `git rebase -i --autosquash main`
5. Result: clean, atomic history with review feedback incorporated -- no "address review feedback" commits in final history

**Gotcha**: `--autosquash` only works with `git rebase -i` (interactive). Adding `rebase.autoSquash = true` to git config makes it the default for all interactive rebases.
