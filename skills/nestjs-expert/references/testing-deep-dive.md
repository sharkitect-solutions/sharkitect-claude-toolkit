# Testing Deep-Dive

Expert reference for testing NestJS applications. Load when writing or debugging NestJS tests, setting up test infrastructure, or designing mocking strategies.

---

## TestingModule.overrideProvider Patterns

The `overrideProvider` API replaces specific providers without rebuilding the entire module graph:

```typescript
const moduleRef = await Test.createTestingModule({
  imports: [OrderModule], // Import the REAL module
})
  .overrideProvider(PaymentGateway)
  .useValue({ charge: jest.fn().mockResolvedValue({ id: 'ch_test' }) })
  .overrideProvider(EmailService)
  .useValue({ send: jest.fn().mockResolvedValue(true) })
  .compile();
```

**Override order matters:** If Provider A depends on Provider B, overriding B makes A receive your mock. But overriding A as well makes the B override irrelevant. Override only the leaf dependencies you need to isolate.

---

## Testing Guards in Isolation

Test guards directly instead of only through slow e2e tests:

```typescript
describe('RolesGuard', () => {
  let guard: RolesGuard;
  let reflector: Reflector;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [RolesGuard, Reflector],
    }).compile();
    guard = module.get(RolesGuard);
    reflector = module.get(Reflector);
  });

  it('allows access when user has required role', () => {
    const context = createMock<ExecutionContext>();
    context.switchToHttp().getRequest.mockReturnValue({ user: { roles: ['admin'] } });
    jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['admin']);
    expect(guard.canActivate(context)).toBe(true);
  });

  it('denies when user lacks role', () => {
    const context = createMock<ExecutionContext>();
    context.switchToHttp().getRequest.mockReturnValue({ user: { roles: ['viewer'] } });
    jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['admin']);
    expect(guard.canActivate(context)).toBe(false);
  });
});
```

Use `createMock<ExecutionContext>()` from `@golevelup/ts-jest` -- it auto-generates mocks from the interface and updates when NestJS changes it.

---

## Testing Interceptors

Interceptors wrap the handler with RxJS. Test the observable transformation, including error paths:

```typescript
it('wraps response in envelope', (done) => {
  const context = createMock<ExecutionContext>();
  const handler: CallHandler = { handle: () => of({ id: 1 }) };
  interceptor.intercept(context, handler).subscribe({
    next: (value) => { expect(value).toEqual({ data: { id: 1 }, statusCode: 200 }); },
    complete: done,
  });
});
```

**Critical gap:** Most teams test only the happy path. Test with `throwError(() => new Error('fail'))` to verify error handling does not leak uncaught observables.

---

## Integration Test Database Strategies

**Testcontainers (Recommended):** Spin up a real PostgreSQL container per test suite. 3-5 second startup, but catches real query bugs that SQLite misses (JSONB, CTEs, array types).

```typescript
beforeAll(async () => {
  container = await new PostgreSqlContainer().start();
  const module = await Test.createTestingModule({
    imports: [TypeOrmModule.forRoot({
      type: 'postgres', host: container.getHost(),
      port: container.getMappedPort(5432),
      username: container.getUsername(), password: container.getPassword(),
      database: container.getDatabase(), entities: [User, Order], synchronize: true,
    }), UserModule],
  }).compile();
  app = module.createNestApplication();
  await app.init();
}, 30000);
```

**SQLite In-Memory:** Fastest but incompatible with Postgres-specific features. Good for simple CRUD-only tests.

**Transaction Rollback:** One persistent DB, each test wrapped in a transaction that rolls back. Fast, real SQL, but no parallel execution.

---

## E2E Test Patterns with Authentication

Bootstrap the full auth pipeline. **Do not mock auth in e2e tests** -- the entire point is to test the real request pipeline.

```typescript
beforeAll(async () => {
  app = (await Test.createTestingModule({ imports: [AppModule] }).compile())
    .createNestApplication();
  app.useGlobalPipes(new ValidationPipe({ whitelist: true }));
  await app.init();
  const res = await request(app.getHttpServer())
    .post('/auth/login').send({ email: 'test@example.com', password: 'pass' });
  authToken = res.body.access_token;
});

it('creates order with auth', () =>
  request(app.getHttpServer()).post('/orders')
    .set('Authorization', `Bearer ${authToken}`)
    .send({ productId: 1, quantity: 2 }).expect(201));

it('rejects without auth', () =>
  request(app.getHttpServer()).post('/orders')
    .send({ productId: 1, quantity: 2 }).expect(401));
```

---

## Testing Microservice Transports

Create a real microservice + client pair: compile the AppModule as a microservice (`createNestMicroservice` with TCP transport), then compile a separate `ClientsModule` test module to connect to it. Use `client.send()` for request-response patterns and `client.emit()` for events. Always `await client.connect()` before assertions and close both microservice and client in `afterAll`.

---

## Meaningful Coverage Metrics

| Metric | Target | Why |
|--------|--------|-----|
| Branch coverage on guards | 100% | Every authorization path must be tested |
| Module boundary integration tests | >80% | Module exports are internal API contracts |
| Auth endpoint e2e coverage | 100% | Auth bugs are security vulnerabilities |
| Business logic unit coverage | >90% | Core domain logic requires thorough verification |

**Skip coverage for:** Auto-generated module decorators, simple DTOs (test via pipe integration), and controllers that just delegate to services.
