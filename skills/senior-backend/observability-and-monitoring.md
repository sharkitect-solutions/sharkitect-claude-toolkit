# Observability and Monitoring

Load when designing logging strategy, implementing distributed tracing, defining SLOs/SLIs, setting up alerting, or building monitoring dashboards for backend services.

## The Three Pillars (What Each Actually Solves)

| Pillar | What It Answers | When It Fails |
|--------|----------------|---------------|
| **Logs** | "What happened?" -- discrete events with context | Unstructured logs (free-text) are unsearchable at scale. grep breaks at 10GB/day. |
| **Metrics** | "How is the system behaving?" -- aggregated numerical measurements over time | Averages hide outliers. p50 latency of 100ms means nothing when p99 is 5s. Always track percentiles. |
| **Traces** | "Why is this specific request slow?" -- end-to-end path of a single request across services | Without trace context propagation, traces are per-service fragments. The cross-service story is lost. |

**The missing pillar**: Profiling. Logs/metrics/traces tell you WHAT is slow. Profiling tells you WHERE in the code. Continuous profiling (Pyroscope, Parca) catches CPU/memory hotspots that metrics can't pinpoint.

## Structured Logging That Works

| Rule | Implementation | Why |
|------|---------------|-----|
| JSON format, always | `{"level":"error","service":"payment","trace_id":"abc123","msg":"charge failed","amount":5000,"currency":"USD","error":"card_declined"}` | Structured logs are queryable. "Show me all payment errors > $100 in the last hour" is a query, not a grep. |
| Consistent field names across services | Agree on: `trace_id`, `span_id`, `service`, `level`, `msg`, `error`, `user_id`, `duration_ms` | Cross-service log correlation requires field name consistency. `request_id` in one service and `correlation_id` in another breaks joins. |
| Log levels mean something | ERROR = needs human attention. WARN = unexpected but handled. INFO = business events. DEBUG = development only, OFF in production. | If ERROR fires 500 times/day, it is not an error -- it is noise. Reclassify or fix. |
| Never log PII | Mask: email -> `j***@example.com`, card -> `****4242`, SSN -> never log at all | GDPR Article 17 (right to erasure) applies to log data too. You cannot "delete user data" if it is scattered across 90 days of log files. |
| Request context in every log line | Middleware injects `trace_id`, `user_id`, `request_path` into logger context | Without request context, log lines are orphans. "Connection timeout" means nothing without knowing which request, which user, which endpoint. |

**Log volume economics**: At scale, logging costs more than most engineers realize. 1 TB/day of logs in Datadog = ~$2,700/month (ingestion + 15-day retention). Strategy: log business events at INFO, log system details at DEBUG (sampled), never log request/response bodies in production (PII risk + cost).

## Distributed Tracing with OpenTelemetry

| Component | Purpose | Implementation Note |
|-----------|---------|-------------------|
| Trace | End-to-end journey of a request | Starts at the edge (API gateway or first service). One trace per user request. |
| Span | One operation within a trace (DB query, HTTP call, cache lookup) | Each span has: name, duration, status, attributes. Child spans nest under parent spans. |
| Context propagation | Passing trace/span IDs across service boundaries | W3C Trace Context standard: `traceparent` header. Use OpenTelemetry SDK auto-instrumentation for HTTP/gRPC/messaging. |
| Sampling | Reducing trace volume to control cost | Head sampling (decide at entry): simple but misses interesting traces. Tail sampling (decide after completion): captures slow/error traces but requires a collector pipeline. |

**Sampling strategy by environment**:
| Environment | Strategy | Rate |
|-------------|----------|------|
| Development | Always sample (100%) | All traces, full detail |
| Staging | Always sample (100%) | All traces for integration testing verification |
| Production (low traffic < 1K RPM) | Always sample (100%) | Volume is manageable |
| Production (medium 1K-100K RPM) | Tail sampling: always capture errors + slow (> 2s) + random 10% | Balance cost vs visibility |
| Production (high > 100K RPM) | Tail sampling: always capture errors + slow + random 1% | Cost control. 1% of 100K RPM = 1K traces/min = plenty for analysis |

**The baggage trap**: OpenTelemetry Baggage propagates key-value pairs across ALL downstream services. Adding user metadata to baggage seems convenient but creates a hidden coupling: every service now receives (and potentially logs) data it doesn't need. Use baggage sparingly -- trace attributes are per-span and don't propagate.

## SLO/SLI/SLA Framework

| Term | Definition | Example | Who Owns It |
|------|-----------|---------|-------------|
| **SLI** (Service Level Indicator) | The metric you measure | Request latency p99, error rate, availability | Engineering |
| **SLO** (Service Level Objective) | The target for the SLI | p99 latency < 500ms, error rate < 0.1%, availability 99.9% | Engineering + Product |
| **SLA** (Service Level Agreement) | The contractual commitment (SLO + consequences) | 99.9% uptime or service credits | Business + Legal |
| **Error budget** | How much failure is allowed before action | 0.1% error budget = 43.2 min downtime/month (99.9% SLO) | Engineering (spend) + Product (prioritize) |

**Error budget policy** (what happens when budget is exhausted):
1. Freeze feature deployments -- only reliability work ships
2. Mandatory postmortem for each incident that consumed > 10% of budget
3. Budget resets monthly. Unused budget does NOT roll over (it's not a savings account)

**SLO gotchas**:
- 99.99% availability (4 nines) = 4.3 minutes downtime/month. Every deploy that takes > 30s with zero-downtime failure counts against this. Most startups should target 99.9% (3 nines = 43 min/month).
- Latency SLOs on averages are meaningless. The average of [100ms, 100ms, 100ms, 100ms, 10000ms] is 2080ms. Use p99 or p95.
- Client-side SLIs > server-side SLIs. Your server reports 200 OK in 50ms, but the client experienced 3s because of DNS resolution, TLS handshake, and response parsing. Measure from the client perspective when possible.

## Alerting Strategy

| Alert Type | Trigger | Action | Channel |
|-----------|---------|--------|---------|
| Page (wake someone up) | SLO burn rate > 14.4x (will exhaust budget in 1 hour) | On-call investigates immediately | PagerDuty/OpsGenie |
| Ticket (fix during work hours) | SLO burn rate > 1x (will exhaust budget this month) | Team creates work item, fixes within the week | Slack channel + ticket auto-creation |
| Informational | Anomaly detected, no SLO impact | Review in daily standup | Dashboard + daily summary email |

**Multi-window burn rate alerting** (Google SRE approach):
- Fast burn: 14.4x rate over 1 hour AND 6x rate over 6 hours -> Page
- Slow burn: 3x rate over 1 day AND 1x rate over 3 days -> Ticket
- This prevents paging for brief spikes that self-resolve while catching sustained degradation.

**Alert anti-patterns**:
| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Alert on every 500 error | One bad request pages the team. Error RATE matters, not individual errors. | Alert on error rate exceeding threshold (e.g., > 1% of requests). |
| Static thresholds for seasonal traffic | "CPU > 80%" fires every Monday morning during peak traffic. | Use dynamic thresholds (anomaly detection) or baseline-relative alerts. |
| Cascading alerts | One root cause triggers 15 alerts from 15 services | Alert on the SLO, not individual symptoms. Group related alerts. |
| "Just in case" alerts nobody acts on | Alert fatigue. Team ignores ALL alerts including real ones. | If an alert hasn't required action in 30 days, delete it. |

## The Four Golden Signals

| Signal | What to Measure | Warning | Critical |
|--------|----------------|---------|----------|
| **Latency** | p50, p95, p99 of successful requests (exclude errors -- failed requests are fast) | p99 > 2x baseline | p99 > 5x baseline |
| **Traffic** | Requests per second by endpoint | Sudden drop > 30% (may indicate upstream failure) | Drop > 70% or spike > 5x normal |
| **Errors** | Error rate (5xx / total), NOT error count | > 0.5% of requests | > 2% of requests |
| **Saturation** | Resource utilization: CPU, memory, disk I/O, connection pool, thread pool | Any resource > 70% | Any resource > 90% |

**Saturation is the leading indicator**. Latency, traffic, and errors are lagging -- by the time they degrade, the system is already struggling. Monitor saturation to PREDICT failures before users notice.
