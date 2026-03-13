# Production Incident Patterns

Load when debugging production issues, designing incident response procedures, building runbooks, or analyzing why systems fail under real-world conditions.

## Cascade Failure Anatomy

Cascade failures follow a predictable sequence. Recognizing the stage determines the correct response.

| Stage | What Happens | Observable Signal | Correct Response |
|-------|-------------|-------------------|------------------|
| 1. Trigger | Single component degrades (slow DB query, network partition, deploy) | Latency p99 spikes, error rate ticks up | Investigate. Don't panic. Most triggers self-resolve. |
| 2. Saturation | Upstream callers retry, consuming more of the degraded resource | Thread pool/connection pool utilization > 80% | Shed load NOW. Enable rate limiting, reject non-critical requests. |
| 3. Propagation | Caller timeouts cascade to THEIR callers. Failure spreads upstream. | Multiple services alerting simultaneously, fan-out pattern in dependency graph | Circuit breakers should be opening. If they're not configured, manually block traffic to degraded service. |
| 4. Collapse | System-wide degradation. User-facing errors. | Error rate > 50%, all dashboards red | Rollback the trigger if known. If unknown, isolate the blast radius (kill traffic to affected path, not the whole system). |

**The retry amplification trap**: Service A retries 3x to Service B, which retries 3x to Service C. One failure at C generates 9 requests. With 4 layers: 81 requests from 1 failure. Every retry layer MULTIPLIES, not adds. Solution: retry budget per request chain (total retries across all hops <= 3), not per-service.

**Timeout hierarchy rule**: Caller timeout must be SHORTER than callee timeout. If Service A has a 30s timeout calling Service B with a 60s timeout, Service A will timeout and retry while B is still processing the first request -- doubling load on an already-slow service.

## Thundering Herd Scenarios

| Trigger | Mechanism | Prevention |
|---------|-----------|------------|
| Cache expiration (hot key) | 10,000 concurrent requests hit empty cache, all go to DB simultaneously | Cache stampede lock: first request populates cache, others wait. Or: stale-while-revalidate (serve stale, refresh async). |
| Service restart (fleet-wide) | All instances restart simultaneously, cold caches + connection pool establishment spike | Rolling restart with health check gates. Never restart > 25% of fleet simultaneously. |
| Scheduled job convergence | Cron jobs across services all fire at :00 (midnight batch processing) | Add random jitter to cron schedules. Spread across the hour, not synchronized to the minute. |
| Feature flag flip | Flag enables new code path for 100% of users instantly | Progressive rollout: 1% -> 10% -> 50% -> 100% with monitoring gates between each stage. |
| DNS TTL expiry | All clients refresh DNS simultaneously when TTL expires | Use TTL of 30-60s (not 300s). Shorter TTL = smaller herds per refresh cycle. |

## Split-Brain and Data Consistency

| Scenario | What Goes Wrong | Detection | Recovery |
|----------|----------------|-----------|----------|
| Network partition between primary and replica | Replica promotes itself to primary. Two primaries accept writes. Data diverges. | Monitor `pg_stat_replication` lag. Alert if replica reports no primary contact for > 30s. | Quorum-based promotion: require majority of nodes to agree before promotion. Fencing: STONITH (shoot the other node in the head) to prevent dual-primary. |
| Redis Sentinel split-brain | Sentinel group partitions. Each partition promotes a different replica. | Monitor `redis-cli INFO replication` on all nodes. Alert if > 1 node reports role:master. | Use odd number of Sentinels (3 or 5) across availability zones. Quorum = majority. |
| Distributed lock expiry | Process A holds lock, GC pause causes lock to expire. Process B acquires lock. Both think they have exclusive access. | Fencing tokens: lock service returns a monotonically increasing token. Resource rejects requests with stale tokens. | Use fencing tokens on all lock-protected resources. The lock itself is not sufficient -- the resource must validate the token. |

## Incident Severity Classification

| Severity | Definition | Response Time | Who's Involved | Example |
|----------|-----------|---------------|----------------|---------|
| SEV1 | Complete service outage or data loss | Immediate (< 5 min) | On-call + engineering lead + exec stakeholder | Payment processing down, user data corrupted |
| SEV2 | Partial outage or severe degradation | < 15 min | On-call + team lead | API latency 10x normal, 30% of requests failing |
| SEV3 | Degraded but functional, workaround exists | < 1 hour | On-call during business hours | Search results stale by 2 hours, export feature broken |
| SEV4 | Minor issue, no user impact | Next business day | Ticket assigned to team | Monitoring gap, non-critical log errors |

**Severity inflation trap**: When everything is SEV1, nothing is SEV1. Teams that over-classify burn out on-call engineers and dilute urgency. The test: "Would you wake someone at 3 AM for this?" If no, it's not SEV1.

## Postmortem Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|----------------|
| Blame assignment ("John pushed the bad code") | Individuals become defensive. Real systemic issues hidden. | Blameless: "The deployment pipeline allowed a breaking change to reach production without integration tests." |
| Action items: "Be more careful" | Not measurable, not systemic, doesn't prevent recurrence | Concrete: "Add integration test for payment flow. ETA: March 15. Owner: Payment team." |
| 50-page postmortem nobody reads | Length signals thoroughness but prevents learning | One-page format: Timeline (5 bullets), Root cause (1 paragraph), Action items (3-5 max, each with owner + deadline) |
| Postmortem written 2 weeks later | Details forgotten, urgency dissipated | Draft within 48 hours. Finalize within 5 business days. |
| Action items never tracked | Postmortem becomes theater | Track in the same system as regular work (Jira, Linear). Review completion in weekly team meeting. |

## On-Call Best Practices

| Practice | Implementation | Why |
|----------|---------------|-----|
| Runbook per alert | Every PagerDuty/OpsGenie alert links to a runbook with diagnosis steps + remediation | 3 AM on-call should not require deep system knowledge to triage |
| Escalation timeout | Auto-escalate if no acknowledgment in 10 min (SEV1) or 30 min (SEV2) | Prevents single-point-of-failure when on-call is unreachable |
| On-call handoff | 30-min overlap between outgoing and incoming on-call. Active issues briefed. | Context loss at handoff is the #1 source of prolonged incidents |
| Alert fatigue audit | Monthly: if > 30% of alerts require no action, tune or remove them | Noisy alerts train on-call to ignore alerts. Signal-to-noise ratio must stay high. |
| Game day exercises | Quarterly: inject controlled failures during business hours | Teams that only practice during real incidents practice under maximum stress with minimum learning |
