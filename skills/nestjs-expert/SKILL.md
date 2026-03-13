---
name: nestjs-expert
description: "Use when building NestJS applications, designing module architecture, configuring dependency injection, implementing guards/interceptors/pipes, or troubleshooting NestJS-specific errors. Do NOT use for general Node.js/Express questions, frontend frameworks, or database queries unrelated to NestJS ORM integration."
---

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| SKILL.md | Always -- core NestJS architecture, lifecycle, anti-patterns | Never skip |
| references/advanced-di-patterns.md | DI errors, custom providers, dynamic modules, injection scopes | Simple controller/service CRUD |
| references/production-hardening.md | Deployment, performance tuning, memory leaks, graceful shutdown | Early prototyping or local dev only |
| references/testing-deep-dive.md | Writing or fixing NestJS tests, mocking strategies, e2e setup | No testing work in scope |

## Scope Boundary

IN SCOPE: NestJS module architecture, dependency injection patterns, guards/interceptors/pipes, testing NestJS apps, microservices with NestJS transports, production hardening, Fastify adapter, custom decorators, dynamic modules.

OUT OF SCOPE: General Node.js without NestJS context, raw Express middleware, frontend frameworks, database queries unrelated to NestJS ORM integration, Deno/Bun runtimes.

---

## Module Architecture Patterns

Feature modules are the organizational backbone. Every bounded context gets its own module. The critical design choice is what crosses module boundaries.

**Module Taxonomy:**
- **Feature modules**: One per bounded context. Own controllers, services, repositories. Export only the service interface, never the repository.
- **Shared modules**: Stateless utilities (logging, validation helpers, common interceptors). Mark `@Global()` only when 80%+ of modules need it -- otherwise explicit imports preserve dependency clarity.
- **Dynamic modules**: Use `forRoot()` for singleton configuration (database, cache), `forRootAsync()` when config depends on other providers, `forFeature()` for per-module registration (TypeORM entities, Mongoose schemas).
- **Aggregator modules**: Import and re-export related modules. Useful for microservice boundaries where a transport layer needs access to multiple feature modules.

**Circular Dependency Resolution Without forwardRef:**
forwardRef is a crutch that masks architectural problems. When Module A and Module B depend on each other, extract the shared concern into Module C that both import. Common extraction targets: shared interfaces/DTOs, event bus modules, or mediator services. If you find yourself writing `forwardRef(() => SomeModule)`, stop and draw your dependency graph -- the cycle reveals a missing abstraction.

**Lazy-Loaded Modules (v8+):**
Use `LazyModuleLoader` for modules that are expensive to initialize but rarely used (report generation, admin-only features). The module is not instantiated until first access. This reduces cold-start time in serverless environments by 30-60% for apps with 20+ modules.

```typescript
// Lazy loading a heavy reporting module
const { ReportModule } = await import('./report/report.module');
const moduleRef = await this.lazyModuleLoader.load(() => ReportModule);
const reportService = moduleRef.get(ReportService);
```

---

## Advanced Dependency Injection

NestJS DI is built on top of the reflect-metadata system. Understanding the resolution algorithm matters when debugging.

**Provider Resolution Order:**
1. NestJS reads `@Injectable()` decorator metadata to discover constructor parameter types
2. It searches the current module's provider registry using the type as the token
3. If not found locally, it searches imported modules' exports
4. If still not found, it throws the "can't resolve dependencies" error with a `?` at the unresolved position

**Injection Scopes -- Performance Implications:**
- `DEFAULT` (singleton): One instance per module. Use for stateless services. Zero allocation overhead after bootstrap.
- `REQUEST`: New instance per HTTP request. Creates a new provider subtree on every request. Measured overhead: 15-40 microseconds per provider in the scope chain. Use only when the provider genuinely needs per-request state (multi-tenant context, request-scoped caching).
- `TRANSIENT`: New instance every time it is injected. Highest overhead. Use for stateful utility objects that must not share state (builders, accumulators).

**Critical trap:** A singleton that depends on a REQUEST-scoped provider silently becomes request-scoped itself. This "scope bubbling" can cascade through your entire dependency tree, destroying performance. Audit scope chains with `nest info` or by adding a constructor log.

**Custom Provider Patterns:**
See `references/advanced-di-patterns.md` for factory providers, async providers, multi-providers, and the ConfigModule.forRootAsync pattern with full examples.

---

## Request Lifecycle Mastery

The full NestJS request pipeline, in exact execution order:

```
Incoming Request
  -> Middleware (global, then module-scoped, in registration order)
    -> Guards (global, then controller, then route -- ALL must return true)
      -> Interceptors PRE-handler (global, controller, route -- wraps with RxJS)
        -> Pipes (global, controller, route, then param-level)
          -> Route Handler
        -> Interceptors POST-handler (route, controller, global -- reverse order)
      -> Exception Filters (route, controller, global -- first match wins)
  -> Response
```

**Decision Tree -- Which Layer to Use:**

| Need | Use | Why Not the Others |
|------|-----|--------------------|
| Modify request/response headers, CORS, body parsing | Middleware | Runs before NestJS context exists; no access to handler metadata |
| Authorize access (roles, permissions, ownership) | Guards | Return boolean or throw; execution stops if any guard returns false |
| Transform response shape, add timing headers, cache | Interceptors | Wrap handler with RxJS Observable; can modify both request and response |
| Validate/transform incoming data | Pipes | Operate on individual parameters; throw BadRequestException on failure |
| Map exceptions to HTTP responses | Exception Filters | Catch specific exception types; last line of defense |

**Middleware vs Guards -- The Common Confusion:**
Middleware has no knowledge of which route handler will execute. It cannot read `@SetMetadata()` decorators. If your logic needs handler metadata (roles, permissions, feature flags), it must be a Guard. If it is pure request transformation (logging, compression, CORS), use Middleware.

---

## Testing Strategy

NestJS testing has unique challenges because of the DI container. Every test must bootstrap a `TestingModule`.

**Unit Tests -- Provider Isolation:**
Mock direct dependencies only. Use `jest.fn()` for methods, not whole class replacements, to catch interface drift.

```typescript
const module = await Test.createTestingModule({
  providers: [
    OrderService,
    { provide: PaymentGateway, useValue: { charge: jest.fn().mockResolvedValue({ id: 'ch_1' }) } },
    { provide: InventoryService, useValue: { reserve: jest.fn().mockResolvedValue(true) } },
  ],
}).compile();
```

**Integration Tests -- Module Boundaries:**
Test that module exports work correctly. Import the real module, mock only external boundaries (database, HTTP, message queues).

**E2E Tests -- Full Request Pipeline:**
Use `supertest` against the compiled app. This tests middleware, guards, interceptors, pipes, and filters together. Always test the auth flow end-to-end; mocking auth in e2e tests hides real integration bugs.

See `references/testing-deep-dive.md` for TestingModule.overrideProvider patterns, database strategies, and microservice transport testing.

---

## Microservices Patterns

NestJS microservices use a transport-agnostic abstraction. The two communication styles are fundamentally different:

**Message Patterns (request-response):**
Client sends a message, waits for a response. Use `@MessagePattern('pattern')`. The transport serializes/deserializes automatically. Suitable for queries and commands that need confirmation.

**Event Patterns (fire-and-forget):**
Client emits an event, does not wait. Use `@EventPattern('pattern')`. Suitable for notifications, audit logs, analytics. The emitter does not know or care if anyone handles the event.

**Transport Selection:**
| Transport | Latency | Throughput | Use When |
|-----------|---------|------------|----------|
| TCP | Lowest (~0.1ms local) | High | Same-host or low-latency LAN services |
| Redis | Low (~1-2ms) | High | Need pub/sub + request-response, existing Redis infra |
| NATS | Low (~1ms) | Very High | High-throughput event streaming, cluster-native |
| gRPC | Low (~1ms) | Very High | Strong typing with Protobuf, polyglot services |
| RabbitMQ | Medium (~5ms) | Medium | Complex routing, dead-letter queues, guaranteed delivery |
| Kafka | Higher (~10-50ms) | Extreme | Event sourcing, ordered log processing, massive scale |

**Hybrid Applications:**
A single NestJS app can serve HTTP and multiple microservice transports simultaneously. Use `app.connectMicroservice()` for each transport, then `app.startAllMicroservices()` before `app.listen()`. This is ideal for gradual migration from monolith to microservices.

**TCP Keep-Alive for Microservices:**
NestJS TCP transport uses persistent connections. Default Node.js TCP keep-alive is 2 hours, far too long for detecting dead peers behind load balancers. Set `keepAlive: true` and `keepAliveInitialDelay: 30000` (30 seconds) on the socket options to detect failures within one minute.

---

## Production Hardening

See `references/production-hardening.md` for the full deep-dive. Key highlights:

**Graceful Shutdown Sequence:**
1. Receive SIGTERM (container orchestrator sends this first)
2. Stop accepting new HTTP connections (`server.close()`)
3. Wait for in-flight requests to complete (set a timeout: 30 seconds max)
4. Close microservice transports (drain message queues)
5. Close database connection pools
6. Exit process with code 0

Enable with `app.enableShutdownHooks()`. Without this, NestJS ignores SIGTERM entirely and your containers get SIGKILL after the grace period.

**Connection Pool Sizing:**
For PostgreSQL: `pool_size = (num_cores * 2) + effective_spindle_count`. For SSDs, spindle count is 1. A 4-core server with SSD = 9 connections. Over-provisioning pools causes worse performance due to connection thrashing and lock contention.

**Fastify Adapter:**
Fastify handles 2-3x more requests/second than Express for JSON serialization workloads. Migration path: replace `NestExpressApplication` with `NestFastifyApplication`, replace Express-specific middleware with Fastify plugins, update any `req`/`res` type annotations. Breaking changes: no `res.send()` after `return` (Fastify uses return values), different multipart handling.

---

## Named Anti-Patterns

### 1. The God Module
**Detect:** One module imports 10+ other modules and provides 15+ services.
**Impact:** Defeats the purpose of modular architecture. Every change risks cascading failures. Circular dependency likelihood approaches 100%.
**Fix:** Apply the Single Responsibility Principle at the module level. Each module should represent one bounded context. If AppModule has more than 5-7 imports, extract aggregator modules for related feature groups.

### 2. The forwardRef Bandaid
**Detect:** Any use of `forwardRef(() => SomeModule)` in imports or `forwardRef(() => SomeService)` in constructors.
**Impact:** Hides a genuine circular dependency that will cause increasingly bizarre DI errors as the app grows. Makes the dependency graph unpredictable.
**Fix:** Draw the dependency cycle. Extract the shared concept into a new module that both sides import. Common extraction targets: shared DTOs, event emitters, mediator services.

### 3. The Leaky Repository
**Detect:** A service method returns a TypeORM/Mongoose entity directly to a controller, which serializes it to the response.
**Impact:** Database schema changes break API contracts. Lazy-loaded relations trigger unexpected queries during serialization. Sensitive fields leak to clients.
**Fix:** Map entities to DTOs at the service boundary. Use `class-transformer` with `@Exclude()` as a safety net, not as the primary strategy.

### 4. The Any-Cast Guard
**Detect:** A guard that checks `if (process.env.NODE_ENV === 'development') return true;` or similar bypass.
**Impact:** This inevitably reaches production through a missed environment variable or misconfigured deployment. One missed config = zero authentication.
**Fix:** Guards must always enforce policy. Use separate test fixtures or test-specific modules to bypass auth in tests, never conditional logic in the guard itself.

### 5. The Synchronous Trap
**Detect:** An interceptor or middleware that performs CPU-intensive computation (crypto, image processing, JSON parsing of large payloads) synchronously.
**Impact:** Blocks the V8 event loop. A single 100ms synchronous operation in an interceptor serving 1000 req/s means 100 requests queue behind it. Tail latency explodes.
**Fix:** Offload heavy computation to worker threads (`worker_threads` module) or a background job queue (Bull/BullMQ). For interceptors, ensure all operations are async and yield to the event loop.

### 6. The Mock Drift
**Detect:** Test doubles that were written when the service had 3 methods but now the real service has 8. Tests pass but exercise a fiction.
**Impact:** False confidence. Tests pass, production breaks. Particularly dangerous with TypeORM repository mocks that miss new query methods.
**Fix:** Use `jest.mocked()` with full type checking. Or use `@golevelup/ts-jest` `createMock<T>()` which auto-generates mocks from the interface and fails when the interface changes.

---

## Rationalization Table

| Shortcut | Why It Seems OK | Why It Fails | Do This Instead |
|----------|-----------------|--------------|-----------------|
| Put everything in AppModule | "It works and I'll refactor later" | Refactoring cost grows quadratically with provider count. At 20+ providers, extracting modules requires rewriting half the tests. | Create feature modules from day one. Cost is 2 minutes per module. |
| Use `any` for DI tokens | "TypeScript is just for compile time anyway" | Loses refactoring safety. Renaming a service silently breaks injection. Runtime error in production, not a compile error. | Use class references or `Symbol()` tokens with explicit typing. |
| Skip e2e tests | "Unit tests cover the logic" | Unit tests cannot catch middleware ordering bugs, guard composition failures, or pipe transformation issues. These are the #1 source of production NestJS bugs. | Write 3-5 e2e tests covering the critical auth + CRUD path. Takes 30 minutes, saves days. |
| Copy-paste test module setup | "DRY doesn't matter in tests" | When the real module changes, 15 test files have stale setups. Mock drift accumulates silently. | Create a shared `createTestModule()` factory that mirrors the real module structure. |
| Use `@Global()` on feature modules | "Saves import boilerplate" | Invisible coupling. Any module can now depend on yours without declaring it. Refactoring becomes impossible because you cannot trace consumers. | Explicit imports in every module that needs the dependency. |

---

## Red Flags -- Stop and Check

1. **`?` in a DI error message** -- Count your constructor parameters. The `?` position (0-indexed) tells you exactly which dependency is unresolved. Check that module's providers and imports before anything else.

2. **REQUEST-scoped provider in a performance-critical path** -- Scope bubbling can silently make your entire request pipeline allocate new instances. Run a load test before and after adding REQUEST scope.

3. **More than 2 levels of module nesting** -- If Module A imports Module B which imports Module C which imports Module D, your architecture is likely over-engineered. Flatten to 2 levels: feature modules import shared modules.

4. **Test file longer than the source file** -- Usually indicates over-mocking. If you need 200 lines of mock setup to test 50 lines of service code, the service has too many dependencies. Refactor the service first.

5. **`app.enableCors({ origin: '*' })` in production** -- Universal CORS is a security hole. Always whitelist specific origins. If you need dynamic origins, validate against a database or environment whitelist.

6. **No `enableShutdownHooks()` in main.ts** -- Your application will ignore SIGTERM, causing hard kills in container environments. Data corruption risk for any in-flight write operations.

7. **Interceptor that calls `next.handle()` conditionally** -- If an interceptor sometimes skips calling `next.handle()`, the handler never executes but the client gets an empty response or hangs. Always call `next.handle()` and transform the result.
