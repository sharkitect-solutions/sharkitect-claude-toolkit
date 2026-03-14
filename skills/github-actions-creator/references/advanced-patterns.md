# Advanced GitHub Actions Patterns

Deep patterns for reusable workflows, composite actions, OIDC, and advanced matrix strategies.

## Reusable Workflows (workflow_call)

Shared workflows invoked by other workflows. The DRY principle for CI/CD.

### Caller Workflow

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml  # local
    with:
      node-version: 20
    secrets: inherit  # pass all secrets

  deploy:
    uses: org/shared-workflows/.github/workflows/deploy.yml@v2  # remote
    with:
      environment: production
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN }}
```

### Called Workflow (reusable-test.yml)

```yaml
name: Reusable Test
on:
  workflow_call:
    inputs:
      node-version:
        type: number
        default: 20
      working-directory:
        type: string
        default: '.'
    outputs:
      coverage:
        description: "Coverage percentage"
        value: ${{ jobs.test.outputs.coverage }}
    secrets:
      CODECOV_TOKEN:
        required: false

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    outputs:
      coverage: ${{ steps.cov.outputs.pct }}
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage
      - id: cov
        run: echo "pct=$(jq '.total.lines.pct' coverage/coverage-summary.json)" >> $GITHUB_OUTPUT
```

### When to Use Reusable vs Composite

| Factor | Reusable Workflow | Composite Action |
|--------|------------------|------------------|
| Scope | Full job(s) with runners | Steps within a job |
| Secrets | Can receive secrets | Cannot access secrets directly |
| Nesting | Max 4 levels deep | Can nest composites |
| Outputs | Job-level outputs | Step-level outputs |
| Best for | Standardized CI/CD pipelines | Shared step sequences |

## Composite Actions

Bundle multiple steps into a reusable action. Lives in `.github/actions/` or a separate repo.

### Structure

```
.github/actions/setup-and-test/
  action.yml
```

### action.yml

```yaml
name: 'Setup and Test'
description: 'Install deps, lint, and test with caching'
inputs:
  node-version:
    description: 'Node.js version'
    default: '20'
  skip-lint:
    description: 'Skip linting step'
    default: 'false'
outputs:
  test-result:
    description: 'Test exit code'
    value: ${{ steps.test.outputs.result }}
runs:
  using: 'composite'
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'npm'
      shell: bash

    - run: npm ci
      shell: bash

    - if: inputs.skip-lint != 'true'
      run: npm run lint
      shell: bash

    - id: test
      run: |
        npm test && echo "result=pass" >> $GITHUB_OUTPUT || echo "result=fail" >> $GITHUB_OUTPUT
      shell: bash
```

### Usage

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: ./.github/actions/setup-and-test
    with:
      node-version: 22
```

## OIDC Authentication (Keyless)

Eliminate long-lived cloud credentials. GitHub issues short-lived JWT tokens.

### AWS OIDC

```yaml
permissions:
  id-token: write   # Required for OIDC
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/github-actions
      aws-region: us-east-1
      # No access keys needed — OIDC handles auth
```

AWS Trust Policy (one-time setup):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123456789:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:org/repo:*"
      }
    }
  }]
}
```

### GCP OIDC

```yaml
steps:
  - uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: projects/123/locations/global/workloadIdentityPools/github/providers/repo
      service_account: github-actions@project.iam.gserviceaccount.com
```

## Advanced Matrix Strategies

### Dynamic Matrix (generated at runtime)

```yaml
jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - id: set
        run: |
          # Generate matrix from changed packages
          CHANGED=$(git diff --name-only HEAD~1 | grep -o 'packages/[^/]*' | sort -u | jq -R -s -c 'split("\n")[:-1]')
          echo "matrix={\"package\":$CHANGED}" >> $GITHUB_OUTPUT

  test:
    needs: prepare
    strategy:
      matrix: ${{ fromJson(needs.prepare.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing ${{ matrix.package }}"
```

### Matrix with Include/Exclude

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [18, 20, 22]
    include:
      - os: ubuntu-latest
        node: 22
        coverage: true          # Only run coverage on one combo
    exclude:
      - os: windows-latest
        node: 18                # Skip old Node on Windows
  fail-fast: false              # Don't cancel siblings on failure
```

## Self-Hosted Runners

### Runner Labels and Selection

```yaml
jobs:
  build:
    runs-on: [self-hosted, linux, x64, gpu]  # Multiple labels = AND logic
    timeout-minutes: 60  # Critical for self-hosted (no auto-timeout)
    steps:
      - uses: actions/checkout@v4
      # Cleanup is YOUR responsibility on self-hosted
      - name: Clean workspace
        run: rm -rf $GITHUB_WORKSPACE/*
        if: always()
```

### Self-Hosted Runner Security Rules

1. **Never use self-hosted on public repos** — any fork PR can run code on your machine
2. **Always set timeout-minutes** — no default timeout on self-hosted
3. **Clean up after each job** — state persists between runs
4. **Use ephemeral runners** for sensitive workloads (--ephemeral flag)
5. **Restrict with runner groups** in GitHub Enterprise

## Workflow Artifacts and Caching

### Artifact Passing Between Jobs

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 1      # Minimize storage cost

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
```

### Cache Key Strategies

```yaml
# Good: specific lock file hash
key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}

# Better: include Node version
key: ${{ runner.os }}-node-${{ matrix.node }}-npm-${{ hashFiles('**/package-lock.json') }}

# Fallback chain
restore-keys: |
  ${{ runner.os }}-node-${{ matrix.node }}-npm-
  ${{ runner.os }}-node-${{ matrix.node }}-
  ${{ runner.os }}-
```

## Environment Protection Rules

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://app.example.com
    runs-on: ubuntu-latest
    steps:
      - run: deploy.sh
```

Configure in GitHub Settings > Environments:
- **Required reviewers** — approval before deploy
- **Wait timer** — delay (0-43200 min)
- **Deployment branches** — restrict which branches can deploy
- **Environment secrets** — scoped secrets only available in this environment
