---
name: github-actions-creator
description: |
  Use when the user wants to create, debug, or optimize a GitHub Actions workflow.
  TRIGGER: "github actions", "CI/CD pipeline", "workflow", "deploy workflow", "CI workflow",
  "github action", "reusable workflow", "composite action", "workflow_dispatch",
  "matrix strategy", "self-hosted runner", "OIDC deployment"
  EXCLUDE: General git operations, GitHub API usage, non-Actions CI systems (Jenkins, CircleCI)
---

# GitHub Actions Creator

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/workflow-templates.md` | User needs a complete workflow for a specific language/platform | Simple questions about syntax or triggers |
| `references/advanced-patterns.md` | Reusable workflows, composite actions, OIDC, dynamic matrices, self-hosted runners | Basic CI/CD setup |
| `references/debugging-guide.md` | Workflow is failing, debugging errors, cost optimization | Creating new workflows from scratch |
| `evals.json` | Evaluating skill output quality | Normal usage |

---

## Workflow Creation Process

### Step 1: Detect the Stack

Scan the project before writing YAML:

| Indicator File | Stack | Setup Action |
|---------------|-------|-------------|
| `package.json` | Node.js | `actions/setup-node@v4` (check for React, Next.js, etc.) |
| `pyproject.toml` / `requirements.txt` | Python | `actions/setup-python@v5` |
| `go.mod` | Go | `actions/setup-go@v5` |
| `Cargo.toml` | Rust | `dtolnay/rust-toolchain@stable` |
| `pom.xml` / `build.gradle` | Java/Kotlin | `actions/setup-java@v4` |
| `*.csproj` / `*.sln` | .NET | `actions/setup-dotnet@v4` |
| `Dockerfile` | Container builds | `docker/build-push-action@v6` |

Also check: `.github/workflows/` (existing workflows), `vercel.json`/`netlify.toml` (deploy targets), `Makefile`, test configs.

### Step 2: Route by Use Case

**IF user wants basic CI (test + lint):**
- Trigger: `pull_request` + `push` to main
- Parallel jobs: lint, test. Sequential: build after both pass
- Load `references/workflow-templates.md` for language-specific template

**IF user wants deployment:**
- Trigger: `push` to main (or release tags)
- Sequential: test -> build -> deploy (with `needs`)
- Use environment protection rules for production
- Load `references/advanced-patterns.md` for OIDC auth

**IF user wants reusable/shared workflows:**
- Load `references/advanced-patterns.md` for `workflow_call` patterns
- Decide: reusable workflow (full jobs) vs composite action (shared steps)

**IF user is debugging a failing workflow:**
- Load `references/debugging-guide.md`
- Check exit codes, permissions, cache keys first

**IF user wants scheduled automation:**
- Trigger: `schedule` with cron + `workflow_dispatch` for manual trigger
- Always add failure notifications

### Step 3: Generate the Workflow

Every workflow MUST include these structural elements:

```yaml
name: Descriptive Name

on:
  # Most specific triggers possible
  push:
    branches: [main]
    paths-ignore: ['**.md', 'docs/**']
  pull_request:
    branches: [main]

permissions:          # NEVER omit — always explicit minimal
  contents: read

concurrency:          # Prevent duplicate runs
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # false for deploys

jobs:
  job-name:
    runs-on: ubuntu-latest
    timeout-minutes: 15   # ALWAYS set
    steps:
      - uses: actions/checkout@v4
```

---

## Anti-Patterns (Named)

### The Naked Workflow
Omitting `permissions` block entirely. GitHub defaults may be `write-all` in older repos, creating a massive attack surface. **Always declare explicit minimal permissions.**

### The Infinite Runner
No `timeout-minutes` on jobs. Default is 6 hours. A hung test suite burns 6 hours of billable minutes before failing. **Always set timeout-minutes (5-15 for CI, 20-30 for builds, 60 max for deploys).**

### The Secret Leaker
Using `${{ github.event.issue.title }}` or `${{ github.event.pull_request.body }}` directly in `run:` blocks. This is a script injection vulnerability — attacker-controlled input becomes shell code.

```yaml
# VULNERABLE — attacker controls issue title
- run: echo "Processing ${{ github.event.issue.title }}"

# SAFE — passed through environment variable (shell-escaped)
- run: echo "Processing $ISSUE_TITLE"
  env:
    ISSUE_TITLE: ${{ github.event.issue.title }}
```

### The Main Pinner
Pinning actions to `@main` or `@master` instead of version tags. A compromised upstream action runs arbitrary code in your workflow. Use `@v4` minimum; SHA pins for high-security repos.

### The Eager Deployer
Using `cancel-in-progress: true` on deployment workflows. Canceling a mid-flight deploy can leave infrastructure in a broken state. **Use `cancel-in-progress: false` for any job that mutates remote state.**

### The Fork Blinder
Assuming secrets exist in fork PRs. GitHub strips secrets from fork PRs for security. Workflows that require secrets silently fail or error on community contributions. **Always check `github.event.pull_request.head.repo.full_name == github.repository`.**

### The Cache Buster
Using volatile values in cache keys (run IDs, timestamps, `runner.os` when runner images update). Every run gets a cache miss, negating all caching benefit. **Use deterministic keys based on lock file hashes and pinned OS versions.**

---

## Security Checklist (Non-Negotiable)

1. **Explicit permissions** at workflow or job level — never rely on defaults
2. **Pin actions** to major version tags (`@v4`), SHA for critical paths
3. **Never interpolate untrusted input** in `run:` blocks — use `env:` passthrough
4. **Use OIDC** for cloud auth — eliminate stored access keys (see advanced-patterns.md)
5. **Use GitHub Environments** for production deploys — require approvals
6. **Set concurrency** — prevent parallel deploys, cancel duplicate CI runs
7. **Never use self-hosted runners on public repos** — any fork PR runs code on your machine
8. **Validate `workflow_dispatch` inputs** — don't trust manual trigger values blindly

---

## Essential Actions Reference

### Setup (pin to major version)

| Action | Purpose | Cache |
|--------|---------|-------|
| `actions/checkout@v4` | Clone repo | N/A |
| `actions/setup-node@v4` | Node.js | `cache: 'npm'` / `'pnpm'` / `'yarn'` |
| `actions/setup-python@v5` | Python | `cache: 'pip'` / `'poetry'` |
| `actions/setup-go@v5` | Go | `cache: true` |
| `actions/setup-java@v4` | Java/Kotlin | `cache: 'maven'` / `'gradle'` |
| `dtolnay/rust-toolchain@stable` | Rust | Manual `actions/cache@v4` |
| `actions/setup-dotnet@v4` | .NET | `cache: true` |

### Build & Deploy

| Action | Purpose |
|--------|---------|
| `docker/build-push-action@v6` | Multi-platform Docker builds |
| `docker/login-action@v3` | Registry auth (GHCR, DockerHub, ECR) |
| `aws-actions/configure-aws-credentials@v4` | AWS auth (supports OIDC) |
| `google-github-actions/auth@v2` | GCP auth (supports OIDC) |
| `cloudflare/wrangler-action@v3` | Cloudflare Workers |
| `hashicorp/setup-terraform@v3` | Terraform CLI |

### Quality & Utility

| Action | Purpose |
|--------|---------|
| `github/codeql-action/analyze@v3` | SAST scanning |
| `aquasecurity/trivy-action@master` | Container vulnerability scan |
| `codecov/codecov-action@v4` | Coverage upload |
| `actions/dependency-review-action@v4` | Dependency audit on PRs |
| `softprops/action-gh-release@v2` | Create GitHub Releases |
| `dorny/paths-filter@v3` | Detect changed files/paths |
| `googleapis/release-please-action@v4` | Automated versioning + changelogs |

---

## Caching Quick Reference

```yaml
# Node.js — built into setup-node
- uses: actions/setup-node@v4
  with: { node-version: 20, cache: 'npm' }

# Python — built into setup-python
- uses: actions/setup-python@v5
  with: { python-version: '3.12', cache: 'pip' }

# Go — built into setup-go
- uses: actions/setup-go@v5
  with: { go-version: '1.22', cache: true }

# Docker — GHA cache backend
- uses: docker/build-push-action@v6
  with: { cache-from: 'type=gha', cache-to: 'type=gha,mode=max' }

# Rust — manual cache required
- uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/bin/
      ~/.cargo/registry/
      target/
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
```

---

## Cron Syntax

| Schedule | Expression |
|----------|-----------|
| Hourly | `0 * * * *` |
| Daily midnight UTC | `0 0 * * *` |
| Weekdays 9am UTC | `0 9 * * 1-5` |
| Weekly Sunday | `0 0 * * 0` |
| Monthly 1st | `0 0 1 * *` |

Note: GitHub cron can be delayed up to 15 minutes under load. Not suitable for time-critical tasks.

---

## Output Checklist

After creating a workflow, always provide:

1. **Summary** — what the workflow does in one paragraph
2. **Required secrets** — list secrets to configure in Settings > Secrets
3. **Required permissions** — if the workflow needs non-default repo settings
4. **How to trigger** — how to test the workflow (push, PR, manual dispatch)
5. **Cost estimate** — approximate minutes per run (e.g., "~3 min on ubuntu-latest")
