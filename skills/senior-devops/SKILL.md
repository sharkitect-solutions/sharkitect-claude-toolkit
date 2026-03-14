---
name: senior-devops
description: |
  Production infrastructure, CI/CD pipelines, container orchestration, and cloud operations.
  TRIGGER: "deploy", "infrastructure", "terraform", "kubernetes", "docker compose", "CI/CD",
  "monitoring", "alerting", "SLO", "load balancer", "autoscaling", "helm", "IaC",
  "container orchestration", "incident response", "rollback", "blue-green", "canary"
  EXCLUDE: GitHub Actions YAML (use github-actions-creator), Docker basics for development (use docker-expert), cloud pricing/billing questions
---

# Senior DevOps

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/infrastructure-as-code.md` | Terraform state issues, module design, IaC migration, drift detection | Simple docker-compose or basic CLI questions |
| `references/container-orchestration.md` | K8s deployments, pod issues, Helm charts, service mesh, autoscaling | Single-container dev environments |
| `references/observability-stack.md` | Monitoring setup, alert fatigue, SLO design, incident response, dashboards | Application-level logging only |

## Routing: What Are You Deploying?

**IF single service or simple app:**
- Containerize with multi-stage Dockerfile (see Image Size section below)
- Use docker-compose for local dev, single-node deploy
- CI/CD: build -> test -> push image -> deploy (webhook or SSH)
- Skip K8s unless you need auto-healing or horizontal scaling

**IF microservices (3+ services communicating):**
- K8s is justified -- load `references/container-orchestration.md`
- Service mesh (Istio/Linkerd) only when you need mTLS, traffic splitting, or circuit breaking
- Each service gets its own CI pipeline with independent deploy (see The Monolith Pipeline)
- Start with ClusterIP + Ingress. Add service mesh when you hit observability walls.

**IF serverless (event-driven, bursty, low-traffic):**
- IaC with Terraform or SST/Pulumi for Lambda/Cloud Functions
- Load `references/infrastructure-as-code.md` for module patterns
- Cold start budget: API Gateway timeout (29s) minus cold start must leave room for execution
- Watch for The Serverless Spaghetti -- 50+ functions with no naming convention or shared layers

**IF legacy migration (bare metal or manually configured VMs):**
- Never lift-and-shift without first documenting what is actually running
- Run `ss -tlnp` and `systemctl list-units --type=service` to discover services
- Terraform import for existing cloud resources (see companion for import strategies)
- Blue-green cutover: new infra runs parallel, DNS switch, old infra stays warm for 48h

## Counterintuitive Truths (Senior-Level)

These are things experienced DevOps engineers know that contradict common advice:

**CPU limits are almost always wrong.** K8s CPU limits trigger CFS throttling -- the kernel pauses your container mid-request even when the node has idle cores. Set CPU requests (for scheduling) but omit CPU limits unless you have a specific noisy-neighbor problem. Google's internal clusters run without CPU limits. Memory limits remain mandatory (OOM is unrecoverable; CPU throttling is just slow).

**Autoscaling is not the default -- right-sizing is.** Teams enable HPA before profiling their service. Most services have stable, predictable load 95% of the time. HPA adds complexity (flapping, cold pods, connection pool exhaustion on scale-down). Right-size with static replicas first. Add HPA only when you have measured traffic variability that justifies it.

**Terraform modules should be boring.** The instinct to build clever, reusable, parameterized modules creates "Terraform frameworks" that nobody can debug. A module should do one thing with minimal variables. Copy-paste between environments is acceptable when the alternative is a 40-variable module with conditionals. The DRY principle applies less aggressively to infrastructure than to application code.

**Canary deployments are useless without observability.** Teams implement canary deploys and declare victory. But if you cannot detect a 1% error rate increase within 5 minutes, the canary gives you zero signal. You need error budget burn rate alerting (see observability companion) before canary adds value. Without it, you are just doing a slow rolling deploy with extra steps.

**The cgroups memory trap.** Your container uses 180MB but gets OOMKilled at a 256MB limit. Why? The kernel page cache counts toward the cgroup's memory usage. File-heavy operations (reading config files, log writes, temp file processing) consume page cache that is attributed to your container. Set memory limits at 2x observed RSS, not 1.5x, to account for kernel-managed memory.

**GitOps does not mean "put everything in git."** GitOps (ArgoCD/Flux) reconciles cluster state to a git repo. But secrets, ephemeral jobs, and debug resources should NOT go through GitOps. Reconciliation loops will delete your `kubectl run` debug pods. Use GitOps for steady-state resources (deployments, services, config maps). Use imperative commands for operational tasks.

---

## Infrastructure as Code Quick Reference

### Terraform Lifecycle

```
terraform init      # Download providers, initialize backend
terraform plan      # Preview changes (ALWAYS review before apply)
terraform apply     # Execute changes (requires plan approval)
terraform destroy   # Tear down (use -target for surgical removal)
```

### State Management Decision Tree

**IF solo developer, single environment:** Local state with `.gitignore` (temporary only)
**IF team of 2+:** Remote state with locking. S3 + DynamoDB (AWS) or GCS + Cloud Storage (GCP).
**IF enterprise or multi-team:** Terraform Cloud or Spacelift. State is managed, RBAC on workspaces.
**NEVER:** Commit state to git. State contains secrets in plaintext.

### Module Structure

```
modules/
  networking/        # VPC, subnets, security groups, NAT gateways
    main.tf
    variables.tf
    outputs.tf
  compute/           # EC2/GCE instances, ASGs, launch templates
  data/              # RDS, ElastiCache, S3 buckets
  dns/               # Route53/Cloud DNS records
environments/
  production/        # Calls modules with prod values
    main.tf          # module "networking" { source = "../../modules/networking" }
    terraform.tfvars
  staging/
    main.tf
    terraform.tfvars
```

Rule: modules contain zero hardcoded values. All configuration flows through variables.

## Container Orchestration Essentials

### Multi-Stage Build Pattern

```dockerfile
# Stage 1: Build (1.2 GB with all dev dependencies)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build && npm prune --production

# Stage 2: Production (89 MB)
FROM node:20-alpine
RUN addgroup -g 1001 app && adduser -u 1001 -G app -s /bin/sh -D app
WORKDIR /app
COPY --from=builder --chown=app:app /app/dist ./dist
COPY --from=builder --chown=app:app /app/node_modules ./node_modules
USER app
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

Key wins: non-root user, no dev dependencies, no source code in production image.

### K8s Resource Limits

```yaml
resources:
  requests:          # Scheduler uses this for placement
    cpu: 100m        # 0.1 CPU core -- what the pod normally uses
    memory: 128Mi    # What the pod normally uses
  limits:
    cpu: 500m        # Burst ceiling -- throttled beyond this, NOT killed
    memory: 256Mi    # Hard ceiling -- OOMKilled beyond this
```

**OOMKilled debugging:** `kubectl describe pod <name>` shows `Last State: Terminated, Reason: OOMKilled`. Fix: increase memory limit OR find the leak. Check `kubectl top pod` during load test to find actual usage. Set limit at 1.5x observed peak.

### Readiness vs Liveness Probes

```yaml
readinessProbe:          # "Can this pod serve traffic?"
  httpGet:
    path: /healthz
    port: 3000
  initialDelaySeconds: 5   # Wait for app startup
  periodSeconds: 10
  failureThreshold: 3      # 3 failures = stop sending traffic

livenessProbe:           # "Is this pod alive at all?"
  httpGet:
    path: /livez
    port: 3000
  initialDelaySeconds: 15  # MUST be longer than readiness initial delay
  periodSeconds: 20
  failureThreshold: 5      # 5 failures = restart pod
```

**Timing gotcha:** If livenessProbe fires before the app finishes starting, K8s kills and restarts the pod in a crash loop. Set `initialDelaySeconds` for liveness to at least startup time + buffer. For JVM apps, this can be 60-90s. Use `startupProbe` for slow-starting apps instead.

## Deployment Strategies Decision Matrix

| Strategy | Rollback Speed | Extra Cost | Risk Level | Use When |
|----------|---------------|------------|------------|----------|
| **Blue-Green** | Instant (DNS/LB switch) | 2x infra during deploy | Low | Database-compatible releases, need instant rollback |
| **Canary** | Fast (route 0% to canary) | +1 instance minimum | Low | Validating with real traffic, gradual confidence building |
| **Rolling** | Slow (redeploy old version) | None | Medium | Stateless services, backward-compatible changes |
| **Recreate** | Slow (full redeploy) | None | High | Stateful apps that cannot run two versions, dev/staging only |

**Blue-green database trap:** Both blue and green must work with the same database schema. Deploy schema changes BEFORE the app change. Never deploy a breaking schema change and app change simultaneously.

## Named Anti-Patterns

### The YOLO Deploy
Deploying directly to production without staging. "It works on my machine" becomes "it crashed in production." Every change goes through: dev -> staging -> production. No exceptions. Staging must mirror production config (same env vars, same resource limits, same network topology).

### The State Squatter
Storing Terraform state on a local filesystem. One developer runs `terraform apply`, another runs it from their machine with stale state, and infrastructure gets destroyed or duplicated. Remote state with locking is non-negotiable for any team larger than one person.

### The Unlimited Pod
Running K8s pods without resource requests or limits. The scheduler cannot make informed placement decisions. One pod consumes all node memory and triggers OOMKilled cascading across unrelated services. Every pod gets requests AND limits.

### The Snowflake Server
Manually SSH-ing into servers to install packages, edit configs, or fix issues. No two servers are identical. When the server dies, nobody knows how to rebuild it. If you SSH into a production server to fix something, your next task is codifying that fix in IaC.

### The Alert Tsunami
Alerting on every metric crossing any threshold. The on-call engineer receives 50 alerts per shift, learns to ignore all of them, and misses the one that matters. Alert on symptoms (error rate, latency), not causes (CPU usage, disk I/O). See `references/observability-stack.md` for severity design.

### The Monolith Pipeline
One CI/CD pipeline builds, tests, and deploys all services in a monorepo. A typo in Service A's README triggers a 45-minute rebuild of Services B through E. Each service gets its own pipeline with path-based triggers. Only build what changed.

### The Immortal Container
Running base images that were pulled months ago without updates. Known CVEs accumulate silently. Schedule weekly base image rebuilds. Pin to minor versions (`node:20-alpine`), not SHA digests, so patch updates flow in. Scan images with Trivy or Grype in CI -- fail the build on CRITICAL/HIGH CVEs.

### The Secret Sprinkler
Hardcoding secrets in docker-compose files, Kubernetes manifests, or environment variable definitions committed to git. Use a secrets manager (Vault, AWS SSM Parameter Store, GCP Secret Manager) and reference secrets by path, never by value.

## SLI/SLO/SLA Framework

**SLI (Service Level Indicator):** A measured metric. Examples:
- Request latency: p50=45ms, p95=120ms, p99=800ms
- Error rate: 0.1% of requests return 5xx
- Availability: 99.95% of health checks succeed over 30 days

**SLO (Service Level Objective):** Internal target. "p99 latency < 500ms over 30-day window."
- Set SLOs tighter than SLAs (if SLA is 99.9%, SLO should be 99.95%)
- Error budget = 100% - SLO. At 99.95% SLO, you get 21.6 minutes of downtime per month.
- When error budget is exhausted: freeze feature releases, focus on reliability.

**SLA (Service Level Agreement):** Contractual promise with financial penalties.
- Only set SLAs you can afford to violate (credits, refunds)
- Never set an SLA tighter than your SLO

## Incident Response Runbook Template

### Severity Levels

| Level | Definition | Response Time | Example |
|-------|-----------|---------------|---------|
| SEV1 | Total service outage, data loss risk | 15 min | Database corruption, full site down |
| SEV2 | Major feature broken, significant user impact | 30 min | Payment processing failed, auth broken |
| SEV3 | Minor feature degraded, workaround exists | 4 hours | Search slow, non-critical API errors |
| SEV4 | Cosmetic or minor, no user impact | Next business day | Dashboard graph rendering issue |

### Incident Timeline Template

```
DETECTED:  [timestamp] - How was it detected? (alert/user report/monitoring)
ASSESSED:  [timestamp] - Severity level assigned, responders identified
MITIGATED: [timestamp] - Bleeding stopped (rollback/feature flag/scaling)
RESOLVED:  [timestamp] - Root cause fixed and deployed
REVIEWED:  [date]      - Postmortem completed and action items assigned
```

### Postmortem Structure (Blameless)
1. **Summary:** One paragraph. What happened, how long, who was affected.
2. **Timeline:** Minute-by-minute from detection to resolution.
3. **Root cause:** The systemic issue, not "human error."
4. **What went well:** Things that helped resolve faster.
5. **What went poorly:** Things that slowed resolution.
6. **Action items:** Each has an owner and a deadline. Track in issue tracker.

## Troubleshooting Decision Tree

**IF pods are crashing:**
- CrashLoopBackOff with OOMKilled -> increase memory limit OR find the leak. `kubectl top pod` under load reveals actual usage. Check for cgroups page cache contribution (see Counterintuitive Truths).
- CrashLoopBackOff without OOMKilled -> `kubectl logs <pod> --previous` for app-level crash. Common: liveness probe fires before startup completes. Use `startupProbe` for JVM/Python apps with 30s+ startup.
- ImagePullBackOff -> wrong image tag, expired registry credentials, or private registry missing `imagePullSecrets`.
- Pending (never starts) -> `kubectl describe pod` events. Usually: insufficient CPU/memory (node full), no nodes match nodeSelector/affinity, or PVC cannot bind (wrong storage class or AZ mismatch).

**IF deploys cause 502 errors:**
- The SIGTERM/endpoint-removal race condition. Add `preStop: sleep 10` so the load balancer drains before the app shuts down. See container-orchestration companion for the full shutdown sequence.
- Rolling update maxSurge too low -- not enough new pods ready before old pods terminate. Set `maxSurge: 25%` and `maxUnavailable: 0` for zero-downtime.

**IF Terraform plan shows unexpected destroys:**
- `~` (update in-place) is safe. `-/+` (destroy and recreate) is dangerous. Check why: provider version change altering resource schema, or `create_before_destroy` missing on resources that need it.
- State drift from console changes: `terraform refresh` then `terraform plan` to see what changed.
- Never `terraform apply` a plan with unexpected destroys without understanding each one. Use `-target` for surgical application.

**IF CI/CD pipeline takes too long:**
- Profile: 80% of pipeline time is usually in 20% of steps (dependency install, integration tests, Docker build).
- Layer caching: order Dockerfile commands from least-changing (OS, system deps) to most-changing (app code). `COPY package*.json` before `COPY . .`.
- Parallelism: lint, unit tests, and type checks are independent -- run them concurrently.
- Monorepo: path-based triggers so Service A changes do not rebuild Service B.
