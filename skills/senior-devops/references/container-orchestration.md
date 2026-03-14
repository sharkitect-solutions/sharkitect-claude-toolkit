# Container Orchestration Production Patterns

## Pod Disruption Budgets (PDB)

A PDB declares the minimum number of pods that must remain available during
voluntary disruptions (node drains, cluster upgrades, spot instance reclaims).

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2          # At least 2 pods must stay running
  selector:
    matchLabels:
      app: api-server
```

**Why you need PDBs before node drains:** Without a PDB, `kubectl drain` evicts all pods
on a node simultaneously. If your deployment has 3 replicas on 2 nodes and both drain,
you get zero available pods. With `minAvailable: 2`, the drain waits until replacement
pods are running before evicting the next batch.

**minAvailable vs maxUnavailable:**
- `minAvailable: 2` -- always keep at least 2 running (use for critical services)
- `maxUnavailable: 1` -- allow at most 1 pod down at a time (use for large deployments)
- Never set `minAvailable` equal to replica count -- drains will block indefinitely

## Horizontal Pod Autoscaler (HPA) Tuning

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70    # Scale up when avg CPU > 70%
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300   # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 25                        # Remove max 25% of pods per step
        periodSeconds: 60
```

### Target CPU% Pitfalls
- Setting target too low (30-40%): constant scaling up/down (flapping)
- Setting target too high (90%): no headroom for traffic spikes, latency degrades before scale-up
- Sweet spot for most services: 60-75%
- CPU-based autoscaling misses memory-bound workloads entirely

### Custom Metrics HPA
For queue-based workers, scale on queue depth instead of CPU:
```yaml
metrics:
- type: External
  external:
    metric:
      name: sqs_approximate_number_of_messages
      selector:
        matchLabels:
          queue: order-processing
    target:
      type: AverageValue
      averageValue: 10    # Target 10 messages per pod
```

## Network Policies (Zero-Trust Within Cluster)

Default K8s allows all pod-to-pod traffic. This means a compromised pod can reach
every other service. Network policies restrict traffic to explicit allow rules.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-netpol
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api-server
  policyTypes: ["Ingress", "Egress"]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress       # Only ingress controller can reach API
    ports:
    - port: 3000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres            # API can only reach the database
    ports:
    - port: 5432
  - to:                            # Allow DNS resolution
    - namespaceSelector: {}
    ports:
    - port: 53
      protocol: UDP
```

**Critical:** Always allow DNS egress (port 53 UDP) or pods cannot resolve service names.
This is the number one mistake when first implementing network policies.

## Persistent Volume Strategies

### StatefulSet Gotchas
- PVCs created by StatefulSets are NOT deleted when the StatefulSet is deleted
- Leftover PVCs consume storage and cost money -- clean up manually
- Volume binding mode `WaitForFirstConsumer` prevents cross-AZ scheduling issues
- EBS volumes are AZ-locked: if your pod moves to a different AZ, it cannot attach

### Storage class selection
| Type | IOPS | Use Case |
|------|------|----------|
| gp3 (AWS) | 3000 baseline, burstable | General databases, app storage |
| io2 (AWS) | Provisioned, consistent | High-performance databases |
| pd-ssd (GCP) | Consistent | Production databases |
| pd-balanced (GCP) | Cost-optimized | Non-critical storage |

## Helm Chart Patterns

### Values.yaml layering
```bash
helm upgrade --install api ./charts/api \
  -f values.yaml \              # Base defaults
  -f values-production.yaml \   # Env-specific overrides
  --set image.tag=$GIT_SHA      # CI-injected values
```

### Chart structure for internal services
```
charts/api/
  Chart.yaml            # name, version, appVersion
  values.yaml           # Defaults (dev-safe)
  templates/
    deployment.yaml     # Deployment with resource limits, probes, PDB
    service.yaml        # ClusterIP service
    hpa.yaml            # HPA (only if .Values.autoscaling.enabled)
    networkpolicy.yaml  # Zero-trust network rules
    _helpers.tpl        # Shared template functions
```

Rule: `values.yaml` defaults must be safe for development. Production values come
from a separate `values-production.yaml` that overrides replica counts, resource
limits, and enables features like HPA and PDB.

## K8s RBAC: Least Privilege for Service Accounts

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]     # Read-only, no create/delete
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ci-pod-reader
  namespace: production
subjects:
- kind: ServiceAccount
  name: ci-deployer
roleRef:
  kind: Role
  name: pod-reader
```

**Common mistake:** Giving CI/CD service accounts `cluster-admin`. Instead, create a
deploy-specific role that can only update deployments and read pod status in the
target namespace. If the CI token leaks, blast radius is limited.

## Init Containers vs Sidecars: Decision Framework

**Use init containers when:**
- Task must complete BEFORE the main container starts
- Database migration, config file generation, secret fetching
- One-time setup that does not need to run alongside the app

**Use sidecars when:**
- Process must run continuously alongside the main container
- Log shipping (Fluentd/Filebeat), proxy (Envoy), metrics export
- The sidecar lifecycle must match the main container lifecycle

## Graceful Shutdown

```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 10"]   # Wait for LB to drain
terminationGracePeriodSeconds: 60               # Total time before SIGKILL
```

### Shutdown sequence
1. K8s sends SIGTERM to the container
2. K8s removes pod from Service endpoints (load balancer stops sending traffic)
3. Steps 1 and 2 happen in PARALLEL -- there is a race condition
4. The `preStop` sleep gives the LB time to stop routing BEFORE the app shuts down
5. App receives SIGTERM and begins draining in-flight requests
6. After `terminationGracePeriodSeconds`, K8s sends SIGKILL if still running

**The race condition is critical:** Without `preStop: sleep`, the app may start shutting
down while the load balancer is still sending requests, causing 502 errors during deploys.
A 5-15 second sleep in preStop is standard practice for HTTP services.

## Advanced: Container Runtime Internals

Understanding what happens below the orchestration layer helps debug subtle failures.

### cgroups v2 Memory Accounting

K8s `resources.limits.memory` maps to a cgroup memory limit. But cgroups v2 counts more
than just your application's heap:
- RSS (Resident Set Size) -- your application's actual memory
- Page cache -- kernel-managed file I/O buffers attributed to your container
- Kernel memory -- TCP buffers, socket structures, inode caches

A Java app using 200MB heap can be OOMKilled at 256MB because the JVM's
`/tmp` file operations, log writes, and socket buffers push total cgroup usage over the
limit. The page cache is reclaimable but cgroups may OOMKill before reclaiming it under
memory pressure.

**Diagnostic:** `cat /sys/fs/cgroup/memory.current` inside the container shows real usage.
Compare with `kubectl top pod` which only shows RSS.

### Why CPU Limits Cause Latency Spikes

K8s CPU limits use the CFS (Completely Fair Scheduler) bandwidth controller. The kernel
allocates a CPU quota per CFS period (default 100ms). If your container exhausts its
quota in 60ms, it is throttled for the remaining 40ms -- even if the node has idle cores.

This causes tail latency spikes: p50 is normal, p99 suddenly jumps because some requests
land in throttled periods. Check `cat /sys/fs/cgroup/cpu.stat` for `nr_throttled` and
`throttled_usec`. If these are non-zero and climbing, your CPU limit is causing latency.

**Best practice:** Set CPU requests for scheduling guarantees. Remove CPU limits unless
you have a specific reason (multi-tenant isolation, cost attribution). This is Google's
recommendation from their Borg/K8s operating experience.

### Container Image Layer Mechanics

Each Dockerfile instruction creates a layer stored as a tar archive. The overlay filesystem
stacks layers at runtime. Understanding this explains image size and build performance:

- Deleting a file in a later layer does not reduce image size -- it adds a "whiteout" entry
- `RUN apt-get install && apt-get clean` in a single layer works; split across two layers,
  the install layer still contains the full package cache
- `COPY --link` (BuildKit) creates layers independent of parent layers, enabling parallel
  builds and better cache reuse across different base images
- Multi-platform builds (`docker buildx --platform linux/amd64,linux/arm64`) create
  separate layer trees per architecture; manifest lists combine them
