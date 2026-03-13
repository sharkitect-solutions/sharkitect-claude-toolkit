---
name: docker-expert
description: "Use when writing or optimizing Dockerfiles, troubleshooting container builds, configuring Docker Compose, hardening container security, or reducing image sizes. Also use when the user mentions multi-stage builds, .dockerignore, container orchestration, image optimization, or Docker networking. NEVER use for Kubernetes orchestration (use kubernetes tooling), CI/CD pipeline configuration (use devops tooling), or cloud-specific container services like ECS or Cloud Run."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Docker Expert

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Dockerfile optimization, compose architecture, security checklist, troubleshooting, anti-patterns | Always (auto-loaded) |
| container-kernel-internals.md | Linux namespace isolation (8 types with gotchas), PID 1 signal problem, cgroups v2 memory/CPU control, /proc/meminfo lie, overlay2 filesystem mechanics, copy-on-write performance, seccomp profiles, capabilities vs privileged | When debugging container behavior that doesn't match expectations (signals, memory limits, filesystem performance, permission errors), when hardening beyond basic security checklist, or when explaining WHY a container behaves a certain way |
| buildkit-advanced-strategies.md | Cache mount patterns (9 package managers), build secrets, SSH agent forwarding, multi-platform builds with QEMU gotchas, Dockerfile frontend syntax (heredocs, --exclude), cache invalidation rules, inline cache export for CI | When optimizing build speed or CI pipeline builds, handling private dependencies during build, building multi-architecture images, or diagnosing cache invalidation problems |
| supply-chain-security.md | Image signing (cosign/keyless), SBOM generation (syft/trivy/docker scout), SLSA provenance levels, digest pinning strategy, vulnerability scanning triage (EPSS-based), registry security, admission control | When hardening container supply chain, implementing image signing, generating SBOMs for compliance, setting up vulnerability scanning policies, or securing registry access |

Do NOT load companion files for basic Dockerfile writing, simple compose setup, or standard multi-stage build questions -- SKILL.md covers these fully.

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| Dockerfiles, multi-stage builds, image optimization | YES | -- |
| Docker Compose configuration and architecture | YES | -- |
| Container security hardening (non-root, secrets, capabilities) | YES | -- |
| Container troubleshooting (build failures, runtime errors, networking) | YES | -- |
| .dockerignore and build context optimization | YES | -- |
| Linux kernel container primitives (namespaces, cgroups, seccomp) | YES (via companion) | -- |
| BuildKit advanced features (cache mounts, secrets, multi-platform) | YES (via companion) | -- |
| Container image supply chain security (signing, SBOM, SLSA) | YES (via companion) | -- |
| Kubernetes orchestration, Helm charts, K8s networking | NO | kubernetes tooling |
| CI/CD pipeline configuration (GitHub Actions, GitLab CI) | NO | devops tooling |
| Cloud container services (ECS, Cloud Run, App Runner) | NO | cloud-specific tooling |
| Application security (OWASP, code-level vulnerabilities) | NO | security-best-practices, vulnerability-scanner |

## Docker Analysis Procedure

1. **Detect environment**: Run `docker --version` and `docker info` to confirm Docker is available and identify the runtime (Docker Desktop, Docker Engine, Podman compatibility).
2. **Inventory existing config**: Find all `Dockerfile*`, `*compose*.yml`, and `.dockerignore` files in the project. Read each one before suggesting changes.
3. **Identify the problem category**: Map the user's request to a specific area (build optimization, security, compose architecture, image size, networking, development workflow).
4. **Apply the relevant patterns** from the sections below.
5. **Validate changes**: Build with `--no-cache` to confirm the build succeeds. Run the container and verify the healthcheck passes. For compose, run `docker-compose config` to validate syntax.

## Base Image Decision Matrix

Choosing the wrong base image is the most common source of bloated, insecure containers.

| Requirement | Recommended Base | Size | Trade-off |
|---|---|---|---|
| Node.js production (general) | `node:22-alpine` | ~50MB | Alpine uses musl libc; some native modules need `--build-from-source` |
| Node.js production (minimal) | `gcr.io/distroless/nodejs22-debian12` | ~40MB | No shell, no package manager -- debugging requires ephemeral containers |
| Python production | `python:3.12-slim` | ~45MB | Slim removes build tools; install build deps in a separate stage |
| Go production | `scratch` or `gcr.io/distroless/static` | ~2-10MB | Static binaries only; no shell, no libc -- set `CGO_ENABLED=0` |
| Java production | `eclipse-temurin:21-jre-alpine` | ~80MB | JRE-only; avoid JDK in production images |
| Multi-arch requirement | Any `-alpine` variant + `docker buildx` | Varies | Build with `--platform linux/amd64,linux/arm64` |
| Need to debug in production | `*-slim` variant (not distroless) | Slightly larger | Shell access available for troubleshooting |

## Multi-Stage Build Pattern

The canonical optimization pattern. Separate build-time dependencies from runtime.

```dockerfile
# Stage 1: Install production dependencies only
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

# Stage 2: Build application
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production runtime
FROM node:22-alpine AS runtime
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001 -G appgroup
WORKDIR /app
COPY --from=deps --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY --from=build --chown=appuser:appgroup /app/package.json ./
USER 1001
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

**Key rules**: Copy `package*.json` before source code (layer caching). Clean package manager cache in the same RUN layer. Use `npm ci` not `npm install`. Set USER by UID (not name) for compatibility.

## Container Security Checklist

| Security Measure | Implementation | Why It Matters |
|---|---|---|
| Non-root user | `RUN addgroup/adduser` + `USER 1001` | Root in container = root on host if container escapes |
| Minimal packages | No `curl`, `wget`, `vim` in production unless required for healthcheck | Every installed binary is an attack vector |
| Read-only filesystem | `--read-only` flag + tmpfs for writable paths | Prevents runtime file modification by attackers |
| No secrets in layers | Use `--mount=type=secret` for build-time secrets; Docker secrets or env vars for runtime | `docker history` exposes every layer; ENV and ARG values persist |
| Capability dropping | `--cap-drop=ALL --cap-add=<only-needed>` | Default capabilities include dangerous permissions (NET_RAW, SYS_CHROOT) |
| Resource limits | `--memory`, `--cpus` in compose deploy block | Prevents single container from consuming all host resources |
| Image scanning | `docker scout quickview` or `trivy image` | Catches known CVEs in base images and dependencies |

## Docker Compose Production Pattern

```yaml
services:
  app:
    build:
      context: .
      target: runtime
    depends_on:
      db:
        condition: service_healthy
    networks: [frontend, backend]
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits: { cpus: '1.0', memory: 1G }
        reservations: { cpus: '0.25', memory: 256M }
      restart_policy:
        condition: on-failure
        max_attempts: 3

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets: [db_password]
    volumes: [postgres_data:/var/lib/postgresql/data]
    networks: [backend]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access

volumes:
  postgres_data:

secrets:
  db_password:
    external: true
```

**Key rules**: Always define healthchecks. Use `internal: true` for backend networks. Use Docker secrets, not environment variables, for passwords. Set resource limits to prevent runaway containers.

## Dockerfile Anti-Patterns

| Name | Anti-Pattern | Problem | Fix |
|---|---|---|---|
| The Cache Buster | `COPY . .` before dependency install | Every source change invalidates dependency cache, rebuilding all deps on every build (~2-10 min wasted per build) | Copy lockfile first, install deps, then `COPY . .` |
| The Bloated Layer | `RUN apt-get update` without cleanup in same layer | Layer retains full package cache (~100-300MB permanently baked into image) | Single `RUN`: update + install + `rm -rf /var/lib/apt/lists/*` |
| The Leaked Secret | `ENV API_KEY=secret` or `ARG` with sensitive values | Secret persists in image metadata forever; `docker history` exposes it; anyone with image access has your credentials | Use `--mount=type=secret` (build-time) or runtime env injection |
| The Heavyweight | `FROM node:22` (full image) in production | ~350MB base when ~50MB Alpine works; 7x more CVE surface area; slower pulls, deploys, and scale-ups | Use `-alpine` or `-slim` variants; switch to distroless for minimal attack surface |
| The Open Door | No `.dockerignore` in a project with `node_modules` or `.git` | Build context includes everything -- `.git` (~50-500MB), `node_modules` (~200MB+), `.env` files with secrets | Create `.dockerignore`: `.git`, `node_modules`, `.env`, `*.log`, `dist/`, `.dockerignore` |
| The Non-Deterministic Build | `RUN npm install` in production | Installs devDependencies; resolves floating versions differently each build; cache busting when lockfile unchanged | `RUN npm ci --omit=dev` for reproducible, production-only installs |
| The Layer Cake | Multiple separate `RUN apt-get` commands | Each creates a layer; `apt-get update` cache in layer 1 goes stale relative to `apt-get install` in layer 2 | Consolidate into single `RUN` with `&&` |
| The Silent Failure | `HEALTHCHECK` missing from production containers | Orchestrators route traffic to dead containers; `depends_on: condition: service_healthy` doesn't work; container restarts are delayed | Always add HEALTHCHECK with appropriate `start_period` for your app |
| The Zombie Factory | No init process (app runs as PID 1 without signal handling) | `docker stop` sends SIGTERM but PID 1 ignores unhandled signals; container force-killed after 10s timeout; orphan child processes become zombies | Use `--init` flag, `tini` as entrypoint, or handle SIGTERM in application code |
| The Layer Delete Illusion | `RUN rm -rf /large-file` in a later layer to "reduce" image size | File still exists in the previous layer; deletion only creates a whiteout entry; image size unchanged | Multi-stage build: build tools stay in builder stage, never reach production |

## Development vs Production Configuration

| Concern | Development | Production |
|---|---|---|
| Build target | `target: development` | `target: runtime` |
| Volumes | Bind mount source: `.:/app` with exclusions (`/app/node_modules`) | No bind mounts; all code baked into image |
| Ports | Debug port exposed (`9229:9229`) | Only application port |
| Restart policy | `no` (fail fast during dev) | `on-failure` with max attempts |
| Resource limits | None (avoid dev friction) | Defined in deploy block |
| Environment | `NODE_ENV=development`, `DEBUG=app:*` | `NODE_ENV=production` |

## Troubleshooting Decision Tree

| Symptom | Most Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|
| Build takes 10+ minutes | Poor layer caching; large build context | `docker build` output shows which step rebuilds; `du -sh .` for context size | Reorder COPY statements; add `.dockerignore` |
| Image > 1GB | Build tools in production; wrong base image | `docker history <image>` shows layer sizes | Multi-stage build; switch to Alpine/distroless |
| Container exits immediately | Process crashes or wrong CMD | `docker logs <container>` | Check CMD/ENTRYPOINT; verify process starts correctly |
| Cannot connect to service | Network misconfiguration; port not exposed | `docker network inspect <net>`; `docker port <container>` | Verify EXPOSE, port mapping, and network membership |
| Health check failing | Endpoint not ready; wrong check command | `docker inspect --format='{{.State.Health}}' <container>` | Increase `start_period`; verify healthcheck command works inside container |
| Permission denied errors | Root-owned files, non-root user | `docker exec <container> ls -la /app` | `COPY --chown` and ensure writable dirs for the app user |

## Recommendation Confidence

Not all guidance above carries equal certainty. Override when your specific context demands it.

| Area | Confidence | Override When |
|---|---|---|
| Multi-stage builds for production | HIGH | Truly single-binary languages (Go, Rust with static linking) where there's nothing to separate. Even then, using scratch/distroless as the final stage is still a multi-stage pattern. |
| Non-root user requirement | HIGH | Only override for containers that genuinely need root: Docker-in-Docker, network configuration (VPN, service mesh sidecars), system-level tools. Add a comment explaining why. |
| Alpine vs Slim base image selection | MEDIUM | When native modules fail on Alpine (musl libc), switch to `-slim`. Test by building -- if `node-gyp` or similar fails, Alpine is wrong for that project. Don't guess; build and see. |
| Healthcheck implementation | HIGH | Sidecar containers and init containers in Kubernetes don't need healthchecks -- they have different lifecycle models. Every long-running service needs them. |
| Docker Compose for production | LOW | Compose is fine for single-node production (small SaaS, personal projects, internal tools). The "never use Compose in production" advice assumes multi-node requirements that many apps don't have. |
| Distroless vs Alpine for security | MEDIUM | Distroless eliminates more attack surface but makes debugging harder. For internet-facing services with strong security requirements: distroless. For internal services where incident response speed matters: Alpine with non-root. |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "Alpine is always the best base image" | Alpine uses musl libc which breaks some native modules (bcrypt, sharp, canvas); `-slim` is safer when native deps exist |
| "I'll optimize the image later" | Large images slow every deploy, CI run, and scale-up event; the cost compounds from the first build |
| "Running as root is fine in containers" | Container escape vulnerabilities exist; root in container = root on host without user namespace remapping |
| "Health checks are optional" | Without healthchecks, orchestrators route traffic to dead containers; `depends_on: condition: service_healthy` requires them |
| "I'll just use docker-compose for production" | Compose lacks rolling updates, service mesh, and node failure recovery; use Swarm or Kubernetes for multi-node production |
| "Distroless is always better than Alpine" | Distroless has no shell -- debugging production issues requires ephemeral sidecar containers; Alpine with non-root user is often the better trade-off |

## Red Flags

- No `.dockerignore` in a project with `node_modules` or `.git` -- build context will be enormous and may leak secrets
- `docker-compose.yml` with no healthchecks on any service -- orchestrators can't detect failures
- Secrets passed via `ENV` or `ARG` instructions in the Dockerfile -- visible in `docker history` forever
- Production containers running as root (no `USER` directive) -- container escape = host compromise
- Single-stage Dockerfile that includes build tools (gcc, make, python build deps) in the production image -- 300MB+ of unnecessary attack surface
- `latest` tag used for base images in production -- non-reproducible builds, silent breaking changes
- No resource limits in production compose -- one runaway container can OOM-kill the host
- `--privileged` flag used because "it was the only way to make it work" -- almost always a single missing capability, not a privileged requirement

## NEVER

- Put secrets in Dockerfile ENV/ARG instructions or commit them to image layers -- use Docker secrets or runtime env injection
- Use `docker-compose` as the sole production orchestrator for multi-node deployments -- it lacks failure recovery
- Skip healthchecks in production containers -- orchestrators need them to route traffic correctly
- Use `--privileged` flag unless there is an explicit, documented requirement -- it disables all container isolation
- Ignore `docker scout` or `trivy` CVE warnings on base images in production builds -- patch or upgrade the base image
