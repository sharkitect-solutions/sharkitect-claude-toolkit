# Debugging & Troubleshooting GitHub Actions

Systematic debugging techniques, common failure patterns, and cost optimization.

## Debugging Workflow Failures

### Enable Debug Logging

Two levels of debug output:

```yaml
# Option 1: Set as repo secret (persistent)
# Settings > Secrets > ACTIONS_STEP_DEBUG = true
# Settings > Secrets > ACTIONS_RUNNER_DEBUG = true

# Option 2: Re-run with debug (one-time)
# Click "Re-run jobs" > check "Enable debug logging"
```

### Read Logs Systematically

1. **Check the failing step name** — the red X tells you WHERE, not WHY
2. **Expand the failing step** — read the LAST 20 lines first (stack trace / exit code)
3. **Check "Set up job"** — runner version, OS, pre-installed tools
4. **Check "Post" steps** — cache save failures, artifact upload errors

### Common Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 1 | Generic failure | Read stderr output |
| 2 | Misuse of command | Check shell syntax |
| 126 | Permission denied | `chmod +x` the script |
| 127 | Command not found | Missing install step or PATH issue |
| 128 | Invalid exit signal | Killed by runner (timeout/OOM) |
| 137 | SIGKILL (OOM) | Reduce memory usage or use larger runner |
| 139 | SIGSEGV | Native code crash, check dependencies |

## Common Failure Patterns

### The Phantom Green (Silent Failure)

**Symptom:** Workflow passes but nothing actually deployed/published.
**Cause:** A step with `continue-on-error: true` or a conditional that silently skips.

```yaml
# BAD — deploy failure is swallowed
- run: deploy.sh
  continue-on-error: true

# GOOD — fail explicitly, handle specific errors
- run: deploy.sh
- if: failure()
  run: echo "::error::Deployment failed" && exit 1
```

### The Permission Maze

**Symptom:** `Resource not accessible by integration` or `403 Forbidden`.
**Cause:** Missing `permissions` block or wrong scope.

```yaml
# BAD — relies on default (may be restricted by org settings)
# No permissions block

# GOOD — explicit minimal permissions
permissions:
  contents: read
  pull-requests: write    # Needed for PR comments
  issues: write           # Needed for issue labels
  packages: write         # Needed for GHCR push
  id-token: write         # Needed for OIDC auth
  security-events: write  # Needed for SARIF upload
```

### The Cache Stampede

**Symptom:** Cache miss on every run despite correct key.
**Cause:** Cache key includes volatile data, or cache exceeds 10GB repo limit.

```yaml
# BAD — timestamp makes every key unique
key: ${{ runner.os }}-npm-${{ github.run_id }}

# BAD — OS update changes runner hash
key: ${{ runner.os }}-${{ hashFiles('**/*.lock') }}
# ubuntu-latest resolved to ubuntu-22.04 last week, ubuntu-24.04 this week

# GOOD — stable, deterministic key
key: ubuntu-24.04-node-20-npm-${{ hashFiles('package-lock.json') }}
```

### The Fork PR Trap

**Symptom:** Secrets are empty, OIDC fails, or builds break on fork PRs.
**Cause:** GitHub strips secrets from fork PRs for security.

```yaml
# Handle fork PRs gracefully
- name: Deploy preview
  if: github.event.pull_request.head.repo.full_name == github.repository
  run: deploy-preview.sh
  env:
    TOKEN: ${{ secrets.DEPLOY_TOKEN }}

- name: Fork PR notice
  if: github.event.pull_request.head.repo.full_name != github.repository
  run: echo "Skipping deploy for fork PR (no secrets available)"
```

### The Concurrency Race

**Symptom:** Two deploys run simultaneously, corrupting state.
**Cause:** Missing or wrong concurrency group.

```yaml
# BAD — different workflows can still race
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}

# GOOD — single deploy pipeline regardless of trigger
concurrency:
  group: deploy-production
  cancel-in-progress: false  # Don't cancel in-progress deploys!
```

### The Stale Reference

**Symptom:** Workflow uses wrong action version or deprecated features.
**Cause:** Actions pinned to `@master` or `@main` instead of version tags.

```yaml
# BAD — changes under you without warning
- uses: some-action@main

# RISKY — major version can still break
- uses: some-action@v3

# BEST — SHA pin for critical actions (supply chain security)
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
```

## Workflow Optimization

### Reduce Billable Minutes

```yaml
# 1. Skip unnecessary runs
on:
  push:
    paths-ignore: ['**.md', 'docs/**', '.gitignore', 'LICENSE']

# 2. Cancel superseded runs
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# 3. Short-circuit on lint failure
jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 5       # Lint should be fast
  test:
    needs: lint               # Don't waste minutes if lint fails
    timeout-minutes: 15
```

### Runner Cost Comparison (GitHub-hosted)

| Runner | vCPU | RAM | Cost/min | Best for |
|--------|------|-----|----------|----------|
| ubuntu-latest | 4 | 16GB | $0.008 | Default choice |
| ubuntu-latest-4-cores | 4 | 16GB | $0.008 | Same as default |
| ubuntu-latest-8-cores | 8 | 32GB | $0.016 | Large builds, Rust, C++ |
| ubuntu-latest-16-cores | 16 | 64GB | $0.032 | Monorepo, parallel tests |
| macos-latest | 3 | 14GB | $0.08 | iOS builds (10x Linux cost!) |
| windows-latest | 2 | 7GB | $0.016 | .NET, Windows-specific |

### Parallelization Patterns

```yaml
jobs:
  # Split test suite across runners
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: npm test -- --shard=${{ matrix.shard }}/4

  # Independent jobs run in parallel by default
  lint:
    runs-on: ubuntu-latest
    # No 'needs' = runs immediately in parallel with test
  test:
    runs-on: ubuntu-latest
  typecheck:
    runs-on: ubuntu-latest
```

## Workflow Status and Notifications

### Status Badges

```markdown
![CI](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg)
![CI](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg?branch=develop)
```

### Slack Notification on Failure

```yaml
- uses: slackapi/slack-github-action@v2
  if: failure()
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK }}
    webhook-type: incoming-webhook
    payload: |
      {
        "text": "CI Failed: ${{ github.repository }}@${{ github.ref_name }}",
        "blocks": [{
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|CI Failed>*\nRepo: `${{ github.repository }}`\nBranch: `${{ github.ref_name }}`\nCommit: `${{ github.sha }}`"
          }
        }]
      }
```

## GitHub Actions Limits

| Resource | Limit |
|----------|-------|
| Workflow run time | 6 hours (35 days for self-hosted) |
| Job execution time | 6 hours |
| API requests per hour | 1,000 per repo |
| Concurrent jobs (free) | 20 |
| Concurrent jobs (pro) | 40 |
| Concurrent macOS jobs | 5 |
| Matrix combinations | 256 per workflow |
| Workflow file size | 512 KB |
| Artifact retention | 90 days (configurable) |
| Cache size per repo | 10 GB |
| Log retention | 400 days (90 default) |
