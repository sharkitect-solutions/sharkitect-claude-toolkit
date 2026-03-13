# Production Hardening

Deep-dive reference for running NestJS in production. Load when dealing with deployment, performance, memory leaks, graceful shutdown, or scaling decisions.

---

## Graceful Shutdown Sequence

Container orchestrators send SIGTERM, wait a grace period (default 30s in K8s), then SIGKILL. Your app must complete cleanup within that window.

Enable with `app.enableShutdownHooks()`. Without this, NestJS ignores SIGTERM entirely.

**Lifecycle hook execution order during shutdown:**
1. `OnModuleDestroy` -- close internal resources (providers still active, requests still in-flight)
2. `BeforeApplicationShutdown(signal)` -- HTTP server still running, finish in-flight requests
3. `OnApplicationShutdown(signal)` -- HTTP server closed, close DB connections and external resources

**Common mistake:** Closing database connections in `OnModuleDestroy`. In-flight requests are still processing. Close DB in `OnApplicationShutdown` instead.

**Kubernetes-specific:** Add a `preStop` hook with a 5-second sleep to let the Service de-register the pod before connections drain. Without this, the load balancer sends traffic to a terminating pod.

---

## Connection Pool Sizing

PostgreSQL wiki formula: `pool_size = (num_cores * 2) + effective_spindle_count`

| Server Spec | SSDs | Pool Size |
|-------------|------|-----------|
| 2-core (small VM) | Yes (spindle=1) | 5 |
| 4-core (standard) | Yes | 9 |
| 8-core (production) | Yes | 17 |
| 16-core (high-perf) | Yes | 33 |

**Why smaller pools perform better:** Each connection consumes ~10MB of PostgreSQL memory. At 100 connections, 1GB just for buffers. Connections contend for disk I/O, CPU, and locks. Benchmarks consistently show pool of 10 outperforms pool of 100 on identical hardware.

**Leak detection:** Set `idleTimeoutMillis` to 10-30s. If "too many connections" errors occur despite small pool, an unreleased `queryRunner` is the likely culprit -- always release in a `finally` block.

---

## Memory Leak Patterns Unique to NestJS

**1. Event Listener Accumulation:** Every `EventEmitter.on()` without `off()` leaks a closure. Common in WebSocket gateways that register handlers per connection without cleanup, and microservice handlers that add listeners per request. Fix: use `once()` or remove in `onModuleDestroy()`.

**2. Unclosed Streams:** Interceptors that transform response streams but fail on error paths leave streams open. Always add `catchError` in interceptor pipes to ensure proper RxJS error propagation.

**3. Request-Scoped Provider Caching:** REQUEST-scoped provider stores data in a module-level Map. Provider instance is GC'd, but cache entries persist forever. Keep caches inside the instance, not at module scope.

**4. Circular References in Providers:** Provider A references Provider B which references A at runtime (not module-level). V8 GC cannot reclaim either. Detect with heap snapshots: if provider instance count grows linearly with requests, you have a leak.

---

## Fastify vs Express Performance

Benchmarked on 8-core server, Node.js 20, NestJS v10:

| Metric | Express | Fastify | Difference |
|--------|---------|---------|------------|
| Requests/sec (JSON) | ~15,000 | ~42,000 | 2.8x |
| P99 latency (1k concurrent) | ~45ms | ~12ms | 3.75x better |
| Memory (idle) | ~65MB | ~55MB | 15% less |

**When Fastify matters:** >5000 req/s, latency-sensitive, serverless (cold start). When it does not: CRUD apps <500 req/s, CPU-bound workloads.

**Migration breaking changes:** No `res.send()` after `return` (Fastify uses return values), Express middleware incompatible (use `fastify-express` bridge), multipart uses `@fastify/multipart` instead of `multer`, cookies use `@fastify/cookie`.

---

## Health Check Patterns

**Liveness probe:** "Is the process alive?" Check only event loop responsiveness and heap size. NEVER include database checks -- if DB is temporarily down, liveness fails, orchestrator restart-loops all pods, turning a degraded service into a complete outage.

**Readiness probe:** "Can this instance serve traffic?" Check database connectivity, cache availability, critical dependencies. If readiness fails, orchestrator removes from load balancer but does not restart.

```typescript
@Get('live')
liveness() {
  return this.health.check([
    () => this.memory.checkHeap('heap', 300 * 1024 * 1024),
  ]);
}

@Get('ready')
readiness() {
  return this.health.check([
    () => this.db.pingCheck('database', { timeout: 3000 }),
    () => this.memory.checkHeap('heap', 300 * 1024 * 1024),
  ]);
}
```

---

## Scaling Strategy

**Container replicas (preferred):** One NestJS process per container. Let K8s/ECS manage scaling. Better isolation, one log stream per process, works with horizontal pod autoscaling.

**Node.js cluster module:** For bare-metal or VMs without orchestration. Workers share the TCP port, each with separate memory. No shared state between workers.

---

## Security Hardening Checklist

- `helmet` middleware for security headers (CSP, HSTS, X-Frame-Options)
- `enableCors({ origin: ['https://your-domain.com'] })` -- never wildcard in production
- `@nestjs/throttler` rate limiting (10 req/60s on auth endpoints)
- `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })` -- rejects unknown properties
- Disable `x-powered-by` header
- Set `json({ limit: '1mb' })` to prevent payload DoS
