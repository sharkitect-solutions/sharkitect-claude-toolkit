# Container Supply Chain Security

Securing container images beyond "run as non-root" -- provenance, signing, SBOMs, and supply chain integrity that most Docker tutorials skip entirely.

## The Supply Chain Threat Model

Every `FROM` instruction is an implicit trust decision. You're executing arbitrary code from a registry, authored by someone you may not know, containing dependencies you haven't audited.

| Attack Vector | Real Example | Impact |
|---|---|---|
| Compromised base image | 2024 xz-utils backdoor (CVE-2024-3094) embedded in Ubuntu/Debian base images | Arbitrary code execution in every container built on affected images |
| Typosquatting | `docker pull nod:alpine` vs `node:alpine` | Malicious image executes in your pipeline |
| Tag mutability | `node:22-alpine` today is a different image than `node:22-alpine` last month | Builds are non-reproducible; a compromised tag update silently affects all rebuilds |
| Dependency confusion | Private npm/PyPI package name matches public package | Build installs malicious public package instead of internal one |
| CI secret exposure | Build logs leak `--build-arg API_KEY=...` | Credentials in plain text in CI logs and Docker history |
| Stale base image CVEs | Base image has known CVEs that upstream hasn't patched | Vulnerability inherited by every image built on it |

## Image Signing with Cosign

Cosign (from Sigstore project) signs container images so consumers can verify they came from a trusted source.

### Signing Workflow

```bash
# Generate a key pair (one-time)
cosign generate-key-pair

# Sign an image after building and pushing
cosign sign --key cosign.key ghcr.io/org/app:v1.2.3

# Verify before deploying
cosign verify --key cosign.pub ghcr.io/org/app:v1.2.3
```

### Keyless Signing (OIDC)

For CI pipelines, keyless signing uses OIDC identity from the CI provider -- no long-lived keys to manage:

```bash
# In GitHub Actions (automatic OIDC token)
cosign sign ghcr.io/org/app:v1.2.3
# Signs with GitHub Actions OIDC identity, logged in Rekor transparency log
```

| CI Provider | OIDC Support | Identity Format |
|---|---|---|
| GitHub Actions | Native (automatic) | `https://github.com/org/repo/.github/workflows/build.yml@refs/heads/main` |
| GitLab CI | Native (15.0+) | `https://gitlab.com/org/repo//.gitlab-ci.yml@refs/heads/main` |
| CircleCI | Via OIDC context | Project-scoped OIDC token |

**Verification gotcha**: Keyless verification requires specifying the expected identity AND issuer:
```bash
cosign verify \
  --certificate-identity "https://github.com/org/repo/.github/workflows/build.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/org/app:v1.2.3
```

Without both, verification succeeds for ANY valid Sigstore signature -- including from attackers.

## SBOM (Software Bill of Materials)

An SBOM lists every component inside a container image -- OS packages, language dependencies, and their versions. Required for compliance (US Executive Order 14028, EU Cyber Resilience Act).

### Generating SBOMs

| Tool | Format | Strength |
|---|---|---|
| `syft` (Anchore) | SPDX, CycloneDX | Best language ecosystem coverage (npm, pip, Go, Rust, Java, .NET) |
| `docker sbom` (Docker Scout) | SPDX | Integrated with Docker Desktop, lower adoption in CI |
| `trivy` (Aqua) | CycloneDX, SPDX | Combined SBOM + vulnerability scan in one pass |

```bash
# Generate CycloneDX SBOM with syft
syft ghcr.io/org/app:v1.2.3 -o cyclonedx-json > sbom.json

# Attach SBOM to image (stored alongside in registry)
cosign attach sbom --sbom sbom.json ghcr.io/org/app:v1.2.3
```

### SBOM Gotchas

1. **Distroless images have no package manager**: `syft` can't detect OS packages in distroless because there's no dpkg/rpm database. It still detects language-level deps (node_modules, pip packages) but the OS layer is opaque. Build your SBOM from the builder stage before copying to distroless.

2. **Multi-stage build SBOM gap**: The SBOM of the final image misses build-time-only dependencies. If a compromised build tool (babel, webpack, esbuild) injected malicious code during build, the final SBOM won't show that tool was ever involved. Generate SBOMs for builder stages separately for audit trails.

3. **SBOM drift**: The SBOM is a snapshot at build time. If the image is deployed 6 months later, the SBOM doesn't reflect newly discovered CVEs. Pair SBOM with continuous scanning (e.g., `trivy` running on a schedule against deployed images).

## SLSA (Supply-chain Levels for Software Artifacts)

SLSA is a framework that quantifies supply chain security maturity. It defines 4 levels (0-3).

| Level | Requirement | What It Proves |
|---|---|---|
| SLSA 0 | Nothing | No supply chain security guarantees |
| SLSA 1 | Build process documented; provenance exists but unsigned | You know HOW the image was built |
| SLSA 2 | Build service is authenticated; provenance is signed | The build came from a known CI system, not a developer laptop |
| SLSA 3 | Build service is hardened; provenance is non-forgeable; source is version-controlled | The build cannot be tampered with, even by insiders |

### Practical SLSA Implementation

**SLSA 1** (most teams should start here):
- Generate provenance attestation during build
- Record: source repo, commit SHA, build command, builder identity, timestamp
- Store provenance alongside the image

**SLSA 2** (recommended for production):
- Use hosted CI (GitHub Actions, GitLab CI) -- not self-hosted runners
- Sign provenance with keyless signing (OIDC)
- Verify provenance before deployment

```bash
# GitHub Actions: slsa-github-generator creates SLSA 3 provenance
# In deployment pipeline:
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@refs/tags/v2.0.0" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/org/app:v1.2.3
```

## Image Pinning and Digest Verification

Tags are mutable pointers. `node:22-alpine` can point to a different image tomorrow. Digests are immutable content hashes.

### Pinning Strategy

| Context | Approach | Example |
|---|---|---|
| Dockerfiles (production) | Pin to digest | `FROM node:22-alpine@sha256:a1b2c3...` |
| Dockerfiles (development) | Pin to minor version tag | `FROM node:22-alpine` (accept patch updates) |
| Compose (production) | Pin to digest | `image: postgres:16-alpine@sha256:d4e5f6...` |
| CI dependency images | Pin to digest | `image: ghcr.io/org/ci-tools@sha256:...` |

### Finding and Updating Digests

```bash
# Get current digest for a tag
docker inspect --format='{{index .RepoDigests 0}}' node:22-alpine
# Or: crane digest node:22-alpine

# Automated digest updates: Renovate Bot or Dependabot can auto-PR digest bumps
```

**Gotcha**: Digest pinning breaks multi-platform images. A digest points to a specific platform manifest, not the multi-platform index. Use the INDEX digest (from `docker buildx imagetools inspect`), not the platform-specific manifest digest.

## Vulnerability Scanning Strategy

### Scanner Comparison

| Scanner | Type | CVE Database | Unique Strength |
|---|---|---|---|
| Trivy | OSS | NVD, vendor advisories, GitHub Security | Fastest scan time; scans code repos, IaC, and containers; EPSS scores for prioritization |
| Docker Scout | Commercial (free tier) | Docker's curated DB | Integrated with Docker Desktop and `docker` CLI; real-time monitoring |
| Grype (Anchore) | OSS | NVD, vendor advisories | Fastest raw matching; pairs with `syft` SBOM |
| Snyk Container | Commercial | Snyk's curated DB | Fix advice with base image upgrade suggestions; developer-friendly UX |

### Scanning Workflow

```bash
# Scan during build (CI gate)
trivy image --severity HIGH,CRITICAL --exit-code 1 ghcr.io/org/app:v1.2.3

# Scan deployed images (continuous monitoring)
trivy image --format json --output scan-results.json ghcr.io/org/app:v1.2.3
```

### Vulnerability Triage Decision

Not every CVE requires action. Triage by actual exploitability:

| Factor | Low Priority | High Priority |
|---|---|---|
| EPSS score | < 0.1% (less than 0.1% chance of exploitation in 30 days) | > 10% (actively being exploited) |
| Reachability | Vulnerable function not called by your code | Vulnerable function in your execution path |
| Network exposure | Internal-only service, no external ports | Internet-facing service |
| Fix available | No fix from upstream yet | Patch available, just needs rebuild |

**The "scan and ignore" anti-pattern**: Running scanners that produce 200+ findings and ignoring them all is worse than not scanning -- it creates a false sense of security. Set a triage policy: CRITICAL with EPSS > 1% = fix within 48 hours. HIGH with EPSS > 1% = fix within 2 weeks. Everything else: review monthly.

## Registry Security

### Registry Access Control

| Registry | Free Private Repos | Key Security Feature |
|---|---|---|
| GitHub Container Registry (ghcr.io) | Unlimited | Automatic GitHub Actions OIDC, fine-grained token scoping |
| Docker Hub | 1 | Docker Scout integrated scanning |
| AWS ECR | Unlimited within AWS | IAM policy-based access, image immutability tags |
| Google Artifact Registry | Unlimited within GCP | Binary Authorization enforcement |

### Content Trust and Admission Control

For production Kubernetes clusters, verify images before admission:

| Tool | What It Does |
|---|---|
| Kyverno | Policy engine that can require cosign signatures, specific base images, SBOM presence |
| OPA/Gatekeeper | General-purpose policy engine, can enforce image provenance |
| Sigstore Policy Controller | Native Sigstore verification as a Kubernetes admission webhook |
| AWS ECR Image Scanning | Blocks deployment of images with critical CVEs via EventBridge rules |

### Minimal Registry Hygiene

1. **Enable image immutability** for production tags -- prevents tag overwriting (ECR: `imageTagMutability: IMMUTABLE`)
2. **Set retention policies** -- delete untagged images after 30 days, keep only last N tagged versions
3. **Use separate registries** for dev vs prod -- dev registry allows mutable tags, prod requires signed + scanned
4. **Audit pull logs** -- know who/what is pulling production images and when
5. **Rotate credentials** on a schedule -- registry tokens should have expiration dates, not be permanent
