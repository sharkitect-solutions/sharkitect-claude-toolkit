# Dependency and Supply Chain Security Guide

Load when auditing project dependencies, setting up supply chain security in CI/CD, evaluating third-party library risk, or responding to a dependency vulnerability disclosure.

## Dependency Audit Procedure

| Step | Action | Tool Options |
|---|---|---|
| 1. Inventory | Generate full dependency tree including transitive dependencies | `npm ls --all`, `pip show --verbose`, `go mod graph`, `cargo tree` |
| 2. Vulnerability scan | Check all dependencies against known vulnerability databases | `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`, Snyk, Dependabot |
| 3. License check | Verify no dependency introduces incompatible licenses | `license-checker` (npm), `pip-licenses`, FOSSA, or manual review |
| 4. Maintenance check | Identify abandoned or unmaintained dependencies | Last commit >12 months, no response to critical issues, single maintainer with no succession plan |
| 5. Size impact | Identify bloated dependencies adding unnecessary attack surface | `bundlephobia` (npm), `pipdeptree`, manual review of what percentage you actually use |
| 6. Remediate | Update, replace, or vendor based on findings | Prioritize by exploitability (EPSS score), not just severity (CVSS) |

## Vulnerability Triage Decision Matrix

| CVSS Severity | EPSS Score (Exploit Probability) | Action | Timeline |
|---|---|---|---|
| Critical (9.0+) | >10% (actively exploited) | Emergency patch. Stop other work. | Same day |
| Critical (9.0+) | <10% (not actively exploited) | Priority patch. Schedule immediately. | Within 48 hours |
| High (7.0-8.9) | >10% | Priority patch. | Within 1 week |
| High (7.0-8.9) | <10% | Scheduled patch. | Within 2 weeks |
| Medium (4.0-6.9) | Any | Next maintenance cycle. | Within 30 days |
| Low (0.1-3.9) | Any | Track and batch with other updates. | Within 90 days |

**Triage trap**: CVSS alone overprioritizes theoretical vulnerabilities. A CVSS 9.8 with EPSS 0.01% (no known exploits, complex attack prerequisites) is less urgent than a CVSS 7.2 with EPSS 40% (actively exploited in the wild). Always check EPSS at epss.cyentia.com.

## Lock File Security

| Package Manager | Lock File | CI Install Command | Key Rule |
|---|---|---|---|
| npm | `package-lock.json` | `npm ci` (not `npm install`) | `npm ci` fails if lock file doesn't match `package.json` -- prevents drift |
| Yarn | `yarn.lock` | `yarn install --frozen-lockfile` | `--frozen-lockfile` prevents automatic lock file updates in CI |
| pnpm | `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` | Same behavior as Yarn frozen |
| pip/Poetry | `poetry.lock` | `poetry install --no-update` | `--no-update` uses exact lock file versions |
| pip (requirements) | `requirements.txt` with pinned versions | `pip install -r requirements.txt --require-hashes` | `--require-hashes` validates integrity of every downloaded package |
| Go | `go.sum` | `go build` (automatically uses go.sum) | `GONOSUMCHECK` and `GONOSUMDB` should NEVER be set in CI |
| Cargo (Rust) | `Cargo.lock` | `cargo build --locked` | `--locked` fails if lock file is out of date |

**Lock file gotcha**: The lock file must be committed to version control. If someone adds it to `.gitignore`, different environments install different versions -- a supply chain attack waiting to happen.

## Dependency Update Strategy

| Strategy | How It Works | When to Use |
|---|---|---|
| Automated minor/patch updates | Dependabot/Renovate auto-creates PRs for minor and patch versions | Stable projects with good test coverage (tests catch regressions) |
| Manual major updates | Review changelog and migration guide before updating | Always for major versions (breaking changes). Schedule monthly. |
| Pinned + quarterly audit | Pin all versions, audit and update all at once quarterly | Low-change projects, regulated environments requiring change control |
| Continuous update (greenkeep) | Update everything as soon as new versions appear | Only for projects with >90% test coverage AND fast CI (<10min) |

**Update strategy anti-pattern**: "Update only when something breaks" means you're always behind on security patches. By the time something breaks, the vulnerability may have been exploited. Automate at minimum security-only updates.

## Package Manager Specific Risks

### npm (JavaScript/TypeScript)

| Risk | Detail | Mitigation |
|---|---|---|
| Typosquatting | `lodas` instead of `lodash`, `crossenv` instead of `cross-env` | Verify package name letter-by-letter. Check download count on npmjs.com. Use `npm audit signatures`. |
| postinstall scripts | Arbitrary code execution during `npm install` | Review scripts: `npm pack <pkg>` then inspect `package.json` scripts. Use `--ignore-scripts` for untrusted. |
| Dependency confusion | Internal package name matches public registry package -- npm installs public version | Use scoped packages (`@company/package`). Configure `.npmrc` with registry per scope. |
| Transitive dependency depth | Your 5 dependencies have 200 transitive dependencies you didn't audit | Use `npm ls --all` to see full tree. Consider alternatives with fewer dependencies. |

### pip (Python)

| Risk | Detail | Mitigation |
|---|---|---|
| No built-in integrity verification | `pip install` doesn't verify package hashes by default | Use `--require-hashes` in production. Generate with `pip-compile --generate-hashes`. |
| `setup.py` arbitrary code | Installing from source runs `setup.py` which can execute anything | Prefer wheels (`.whl`) over source distributions. Use `--only-binary :all:` when possible. |
| Global install pollution | `pip install` without virtualenv modifies system Python | Always use virtual environments. Never `sudo pip install`. |
| PyPI namespace squatting | No package namespacing -- anyone can claim any name | Verify package author, repository URL, and download count before installing. |

### Go Modules

| Risk | Detail | Mitigation |
|---|---|---|
| Vanity import paths | `go get company.com/package` resolves via HTTP redirect -- redirect can be hijacked | Pin exact versions in `go.mod`. Use `GONOSUMCHECK` never in production. |
| Checksum database bypass | `GONOSUMDB` disables integrity checking against sum.golang.org | Never set `GONOSUMDB` or `GONOSUMCHECK` in CI/production environments. |

## CI/CD Pipeline Security

| Threat | How It's Exploited | Mitigation |
|---|---|---|
| Secrets in build logs | `echo $SECRET` or verbose build output leaks credentials | Use masked variables in CI. Review build output for accidental exposure. `--quiet` flags on install commands. |
| Compromised build dependencies | Attacker pushes malicious update to a build tool (webpack plugin, babel transform) | Pin build tool versions. Use lock files. Run builds in isolated containers. |
| Unsigned build artifacts | Attacker replaces deployment artifact between build and deploy | Sign artifacts with cosign/sigstore. Verify signatures before deployment. Content-addressable storage (by hash, not filename). |
| Pull request from fork | Fork PR runs CI with secrets, exfiltrates them | Never expose secrets to PRs from forks. Use `pull_request_target` carefully. Require approval before CI runs on external PRs. |
| Dependency cache poisoning | Attacker poisons the CI cache with a modified dependency | Use content-addressed caches (keyed by lock file hash). Don't share caches across branches. |

## SBOM (Software Bill of Materials)

| Aspect | Detail |
|---|---|
| What is it | A machine-readable inventory of every component in your software (direct + transitive dependencies, versions, licenses) |
| Why you need it | Required by Executive Order 14028 (US gov contracts). Enables rapid response to new CVEs -- search your SBOM instead of scanning every project. |
| Format | SPDX (ISO standard) or CycloneDX (OWASP standard). Both are JSON/XML. |
| Generation | `npm sbom` (npm 9+), `cyclonedx-bom` (Python), `syft` (container images), `trivy sbom` |
| Storage | Store alongside release artifacts. Version with each release. Make available to security team. |
| Maintenance | Regenerate on every release. Cross-reference against new CVEs within 24 hours of disclosure. |

**SBOM gotcha**: An SBOM is only useful if it's accurate and current. A stale SBOM gives false confidence. Automate generation in CI/CD -- never rely on manual creation.
