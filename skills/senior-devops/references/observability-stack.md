# Observability Stack: Monitoring, Alerting, and Incident Response

## Three Pillars Architecture

### Metrics (Prometheus/Datadog/CloudWatch)
Numerical measurements sampled over time. Best for dashboards, alerting, and capacity planning.
- Counter: monotonically increasing (total_requests, total_errors)
- Gauge: current value that goes up and down (cpu_usage, memory_used, queue_depth)
- Histogram: distribution of values (request_duration_seconds)

### Logs (Loki/ELK/CloudWatch Logs)
Discrete events with context. Best for debugging specific incidents.
- Structured JSON logs outperform unstructured text 10:1 for searchability
- Always include: timestamp, level, service name, request ID, user ID
- Never log: passwords, tokens, PII, credit card numbers, full request bodies

### Traces (Jaeger/Tempo/X-Ray)
Request flow across services. Best for debugging latency in distributed systems.
- Instrument at service boundaries (HTTP calls, database queries, queue operations)
- Sampling: trace 100% in staging, 1-10% in production (cost control)
- Head-based sampling misses slow requests. Use tail-based sampling if budget allows.

## SLI Calculation Patterns

### Latency SLI
```promql
# p99 latency over 5 minutes
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket{service="api"}[5m])
)
```
**Warning:** Histograms with default bucket boundaries miss important latency ranges.
Configure buckets to match your SLO thresholds:
```go
// If SLO is "p99 < 500ms", bucket at 0.5 is critical
prometheus.LinearBuckets(0.01, 0.05, 20)  // 10ms to 1s in 50ms steps
```

### Error Budget Calculation
```
Error budget = 1 - SLO = 1 - 0.999 = 0.1% = 43.2 minutes/month

Current burn rate = actual_error_rate / allowed_error_rate
If burn rate > 1.0, you are consuming budget faster than allowed.
If burn rate > 14.4 (1-hour window), you will exhaust the monthly budget in 1 hour.
```

### Multi-Window Burn Rate Alerts
Instead of alerting on raw error rates (too noisy), alert on burn rate over multiple windows:
- **Page (SEV1):** burn rate > 14.4 over 1h AND > 14.4 over 5m (fast burn, confirmed)
- **Ticket (SEV3):** burn rate > 3.0 over 6h AND > 3.0 over 30m (slow burn, confirmed)
- The short window confirms the long window is not stale data

## Alert Fatigue Prevention

### Severity Level Design

| Level | Route To | Response | Example Condition |
|-------|----------|----------|-------------------|
| Critical | PagerDuty, phone call | Immediate, wake up | Error budget burn > 14x, total outage |
| Warning | Slack channel | Investigate within 1h | Error budget burn > 3x, degraded performance |
| Info | Dashboard only | Review in standup | Disk usage > 60%, certificate expiry < 30d |

### Alert Grouping and Inhibition
```yaml
# Alertmanager config
inhibit_rules:
- source_matchers: [severity="critical"]
  target_matchers: [severity="warning"]
  equal: [service]
  # If a critical alert fires for "api", suppress all warning alerts for "api"
  # The on-call already knows something is wrong

group_by: [service, alertname]
group_wait: 30s           # Wait 30s to batch related alerts
group_interval: 5m        # Re-notify every 5 min for ongoing issues
repeat_interval: 4h       # Re-page every 4h if unacknowledged
```

### Rules of Thumb
- Every alert must have a runbook link (even if the runbook says "investigate")
- If an alert fires and the response is always "ignore it," delete the alert
- Target: fewer than 5 pages per on-call shift. More than that degrades response quality.
- Never alert on cause metrics (CPU, memory) -- alert on symptom metrics (error rate, latency)
- Exception: disk usage > 90% is worth alerting on because it causes hard failures

## Dashboard Design

### USE Method (for infrastructure resources)
For each resource (CPU, memory, disk, network):
- **U**tilization: percentage of resource used (gauge)
- **S**aturation: work queued because resource is full (gauge)
- **E**rrors: error events related to this resource (counter)

### RED Method (for service endpoints)
For each service or endpoint:
- **R**ate: requests per second (counter)
- **E**rrors: failed requests per second (counter)
- **D**uration: latency distribution (histogram)

### Dashboard Layout
```
Row 1: Golden Signals (request rate, error rate, p50/p95/p99 latency)
Row 2: Error Budget (remaining %, burn rate, projected exhaustion)
Row 3: Infrastructure (CPU, memory, disk, network per node)
Row 4: Dependencies (database latency, cache hit rate, external API latency)
```
Rule: the top row answers "is the service healthy?" in under 5 seconds.
Every subsequent row answers "why not?"

## On-Call Rotation Design

### Follow-the-Sun Model
For teams across time zones: each region covers their business hours.
- US team: 06:00-18:00 PST
- EU team: 06:00-18:00 CET
- APAC team: 06:00-18:00 JST
Nobody gets paged at 3 AM. Handoff happens via written incident notes, not verbal.

### Escalation Chain
```
T+0:   Primary on-call (PagerDuty auto-page)
T+10:  If unacknowledged -> secondary on-call
T+20:  If unacknowledged -> engineering manager
T+30:  If unacknowledged -> VP Engineering
```
Acknowledgment means "I am looking at this," not "I fixed it."

### On-Call Health Metrics
Track per rotation: pages received, MTTA (mean time to acknowledge), MTTR (mean time to resolve).
If a specific service causes >50% of pages, that team owes a reliability investment.

## Postmortem Best Practices

### What "blameless" actually means
Blameless does not mean "nobody is responsible." It means the system failed, not the person.
Ask "what about the system allowed this to happen?" instead of "who made the mistake?"
- Bad: "John deployed without testing"
- Good: "The deployment pipeline lacked a staging gate, allowing untested code to reach production"

### Action Item Quality
Every action item must be:
- **Specific:** "Add integration test for payment timeout handling" not "improve testing"
- **Owned:** Assigned to one person, not a team
- **Tracked:** Filed in the issue tracker with a deadline
- **Preventive:** Addresses root cause, not just the symptom

### Postmortem Review Cadence
- Weekly: review all open action items from recent postmortems
- Monthly: review recurring incident patterns across postmortems
- Quarterly: assess whether incident frequency and severity are trending down

## Cost of Observability

### Sampling Strategies
| Strategy | Cost | Coverage | Use When |
|----------|------|----------|----------|
| 100% sampling | Highest | Complete | Staging, low-traffic services |
| Head-based 10% | Low | Random subset | High-traffic, healthy services |
| Tail-based | Medium | All interesting traces | Need to catch slow/error requests |
| Adaptive | Medium | Proportional to anomalies | Production, cost-sensitive |

### Retention Policies
- Metrics: 15 days at full resolution, 1 year downsampled (5m intervals)
- Logs: 30 days hot (searchable), 90 days cold (archived), delete after 1 year
- Traces: 7 days hot, 30 days cold
- Adjust based on compliance requirements (HIPAA/SOC2 may require longer retention)

### Cost Reduction Levers
1. Drop debug-level logs in production (use log level filtering at the collector)
2. Pre-aggregate high-cardinality metrics before shipping to storage
3. Sample traces at the service level, not the collector level (reduce network cost)
4. Use recording rules in Prometheus for frequently-queried expressions

## Advanced: Observability Theory

### Goodhart's Law Applied to SLOs

"When a measure becomes a target, it ceases to be a good measure." Teams optimizing for
SLO numbers create perverse behaviors:
- Retrying failed requests internally to suppress error rate SLIs (errors still happened,
  user still waited, but the metric looks clean)
- Excluding slow endpoints from latency SLIs ("that endpoint is expected to be slow")
- Setting SLOs so loose they never fire (99% availability = 7.3 hours of downtime/month)

**Defense:** SLOs must be set from the user's perspective, not the system's perspective.
Measure at the edge (load balancer), not at the service. Include retries in latency.
Review SLO targets quarterly against actual user-reported incidents.

### The Observability vs Monitoring Distinction

Monitoring answers "is the system working?" (known-unknowns). Observability answers
"why is the system broken?" (unknown-unknowns). The difference matters for tooling:
- Monitoring: dashboards with pre-defined metrics. Useful for steady-state operations.
- Observability: high-cardinality, high-dimensionality data that can be sliced ad-hoc.
  Useful for debugging novel failures.

Pre-aggregated metrics (Prometheus counters) are monitoring. Raw request traces with
arbitrary attributes (OpenTelemetry spans) are observability. You need both.

### Correlation: The Hard Problem

Having metrics, logs, and traces is insufficient if you cannot correlate them. A trace ID
must flow through every layer:
```
HTTP request -> Load balancer (access log with trace-id)
             -> Service A (structured log with trace-id, span metrics)
             -> Service B (structured log with trace-id, span metrics)
             -> Database (slow query log correlated by trace-id)
```
Without correlation, debugging a slow request means searching logs by timestamp and hoping.
With correlation, you follow one trace-id from edge to database and see exactly where
latency accumulated. OpenTelemetry auto-instrumentation handles this for HTTP and gRPC.
Database correlation requires manual instrumentation or proxy-level injection.

### Capacity Planning with Little's Law

`L = lambda * W` (concurrent requests = arrival rate * average duration)

If your service handles 1000 req/s (lambda) with 50ms average latency (W), you have
50 concurrent requests in-flight (L). Each request needs ~10MB of memory, so steady-state
is 500MB. This is why a latency increase from 50ms to 200ms quadruples memory pressure
even though throughput has not changed -- you now have 200 concurrent requests consuming
2GB. Autoscaling on CPU misses this entirely; scale on concurrent connections or memory.
